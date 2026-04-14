"""
test_api.py — Integration tests for the BreastCare FastAPI backend.

Uses FastAPI's TestClient (in-process, no server required) to exercise
all prediction and data endpoints end-to-end.

Prerequisites:
    python export_models.py   (generates the .pkl files)

Run from repo root:
    pytest tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


# ── Health & Schema Endpoints (IT-01 through IT-05) ──────────────────────────

def test_health_endpoint():
    """IT-01: GET /health must return HTTP 200 with {status: ok}."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_diagnosis_schema_returns_30_features():
    """IT-02: GET /predict/diagnosis/schema must expose exactly 30 feature names."""
    resp = client.get("/predict/diagnosis/schema")
    assert resp.status_code == 200
    data = resp.json()
    assert "features" in data, "Response missing 'features' key"
    assert "stats" in data, "Response missing 'stats' key"
    assert len(data["features"]) == 30, (
        f"Expected 30 features, got {len(data['features'])}"
    )


def test_risk_schema_has_required_keys():
    """IT-03: GET /predict/risk/schema must include num_cols, cat_cols, and stats."""
    resp = client.get("/predict/risk/schema")
    assert resp.status_code == 200
    data = resp.json()
    for key in ("num_cols", "cat_cols", "num_stats", "cat_options"):
        assert key in data, f"Risk schema missing key: '{key}'"


def test_survival_schema_has_required_keys():
    """IT-04: GET /predict/survival/schema must include covariates, defaults, and times."""
    resp = client.get("/predict/survival/schema")
    assert resp.status_code == 200
    data = resp.json()
    for key in ("covariates", "defaults", "evaluation_times"):
        assert key in data, f"Survival schema missing key: '{key}'"
    assert data["evaluation_times"] == [12, 24, 36]


def test_metrics_endpoint_returns_all_models():
    """IT-05: GET /predict/metrics must return metric blocks for model_a, b, and c."""
    resp = client.get("/predict/metrics")
    assert resp.status_code == 200
    data = resp.json()
    for model_key in ("model_a", "model_b", "model_c"):
        assert model_key in data, f"Metrics response missing '{model_key}'"
        assert data[model_key] is not None, f"Metrics for '{model_key}' are None"


# ── Diagnosis Prediction (IT-06 through IT-08) ────────────────────────────────

def test_diagnosis_prediction_returns_valid_label():
    """IT-06: POST /predict/diagnosis with mean feature values must return a valid label."""
    schema = client.get("/predict/diagnosis/schema").json()
    features = {f: schema["stats"][f]["mean"] for f in schema["features"]}

    resp = client.post("/predict/diagnosis", json={"features": features})
    assert resp.status_code == 200
    data = resp.json()
    assert data["prediction"] in (0, 1), f"Unexpected prediction: {data['prediction']}"
    assert data["label"] in ("Benign", "Malignant"), (
        f"Unexpected label: {data['label']}"
    )
    assert "probability_malignant" in data
    assert "probability_benign" in data


def test_diagnosis_probabilities_sum_to_one():
    """IT-07: P(Benign) + P(Malignant) must equal 1.0 within floating-point tolerance."""
    schema = client.get("/predict/diagnosis/schema").json()
    features = {f: schema["stats"][f]["mean"] for f in schema["features"]}

    resp = client.post("/predict/diagnosis", json={"features": features})
    data = resp.json()
    total = data["probability_benign"] + data["probability_malignant"]
    assert abs(total - 1.0) < 1e-4, (
        f"Probabilities sum to {total:.6f}, expected 1.0"
    )


def test_diagnosis_empty_features_uses_zero_fallback():
    """IT-08: POST /predict/diagnosis with empty dict must not crash (fallback to 0.0)."""
    resp = client.post("/predict/diagnosis", json={"features": {}})
    assert resp.status_code == 200
    data = resp.json()
    assert "label" in data
    assert data["label"] in ("Benign", "Malignant")


# ── Risk Prediction (IT-09 through IT-11) ─────────────────────────────────────

def test_risk_prediction_returns_valid_label():
    """IT-09: POST /predict/risk with median/first-category features must return a valid label."""
    schema = client.get("/predict/risk/schema").json()
    features = {f: schema["num_stats"][f]["median"] for f in schema["num_cols"]}
    features.update({f: schema["cat_options"][f][0] for f in schema["cat_cols"]})

    resp = client.post("/predict/risk", json={"features": features})
    assert resp.status_code == 200
    data = resp.json()
    assert data["label"] in ("Low", "Medium", "High"), (
        f"Unexpected risk label: {data['label']}"
    )
    assert data["prediction"] in (0, 1, 2)


def test_risk_probabilities_sum_to_one():
    """IT-10: Sum of Low + Medium + High probabilities must be approximately 1.0."""
    schema = client.get("/predict/risk/schema").json()
    features = {f: schema["num_stats"][f]["median"] for f in schema["num_cols"]}
    features.update({f: schema["cat_options"][f][0] for f in schema["cat_cols"]})

    resp = client.post("/predict/risk", json={"features": features})
    data = resp.json()
    total = sum(data["probabilities"].values())
    assert abs(total - 1.0) < 1e-3, (
        f"Risk probabilities sum to {total:.6f}, expected 1.0"
    )


def test_risk_probabilities_in_unit_interval():
    """IT-11: Each risk class probability must be in [0, 1]."""
    schema = client.get("/predict/risk/schema").json()
    features = {f: schema["num_stats"][f]["median"] for f in schema["num_cols"]}
    features.update({f: schema["cat_options"][f][0] for f in schema["cat_cols"]})

    resp = client.post("/predict/risk", json={"features": features})
    data = resp.json()
    for label, prob in data["probabilities"].items():
        assert 0.0 <= prob <= 1.0, (
            f"Risk probability for '{label}' out of [0,1]: {prob}"
        )


# ── Survival Prediction (IT-12 through IT-14) ─────────────────────────────────

def test_survival_prediction_returns_valid_structure():
    """IT-12: POST /predict/survival with schema defaults must return OS and RFS dicts."""
    schema = client.get("/predict/survival/schema").json()
    features = schema["defaults"]

    resp = client.post("/predict/survival", json={"features": features})
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_survival" in data, "Response missing 'overall_survival'"
    assert "relapse_free_survival" in data, "Response missing 'relapse_free_survival'"


def test_survival_probabilities_in_unit_interval():
    """IT-13: All survival probabilities at evaluation times must be in [0, 1]."""
    schema = client.get("/predict/survival/schema").json()
    features = schema["defaults"]

    resp = client.post("/predict/survival", json={"features": features})
    data = resp.json()

    for outcome_key in ("overall_survival", "relapse_free_survival"):
        for t, prob in data[outcome_key].items():
            assert 0.0 <= prob <= 1.0, (
                f"{outcome_key} at t={t} is {prob}, outside [0, 1]"
            )


def test_survival_evaluation_times_match_schema():
    """IT-14: Survival prediction keys must match the schema's evaluation_times."""
    schema = client.get("/predict/survival/schema").json()
    features = schema["defaults"]
    expected_times = {str(t) for t in schema["evaluation_times"]}

    resp = client.post("/predict/survival", json={"features": features})
    data = resp.json()
    actual_times = set(data["overall_survival"].keys())
    assert actual_times == expected_times, (
        f"Survival time keys {actual_times} don't match schema {expected_times}"
    )


# ── SHAP Endpoint (IT-17 through IT-19) ──────────────────────────────────────

def test_shap_endpoint_returns_top_10_features():
    """IT-17: POST /predict/shap/diagnosis must return exactly 10 SHAP values."""
    schema = client.get("/predict/diagnosis/schema").json()
    features = {f: schema["stats"][f]["mean"] for f in schema["features"]}

    resp = client.post("/predict/shap/diagnosis", json={"features": features})
    assert resp.status_code == 200, f"SHAP endpoint returned {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "shap_values" in data
    assert len(data["shap_values"]) == 10


def test_shap_values_have_required_keys():
    """IT-18: Each SHAP entry must contain 'feature' and 'shap_value' keys."""
    schema = client.get("/predict/diagnosis/schema").json()
    features = {f: schema["stats"][f]["mean"] for f in schema["features"]}

    resp = client.post("/predict/shap/diagnosis", json={"features": features})
    data = resp.json()
    for entry in data["shap_values"]:
        assert "feature" in entry, f"Missing 'feature' key in SHAP entry: {entry}"
        assert "shap_value" in entry, f"Missing 'shap_value' key in SHAP entry: {entry}"


def test_shap_feature_names_are_valid():
    """IT-19: SHAP feature names must all be valid WBCD feature names."""
    schema = client.get("/predict/diagnosis/schema").json()
    valid_features = set(schema["features"])
    features = {f: schema["stats"][f]["mean"] for f in schema["features"]}

    resp = client.post("/predict/shap/diagnosis", json={"features": features})
    data = resp.json()
    for entry in data["shap_values"]:
        assert entry["feature"] in valid_features, (
            f"SHAP returned unknown feature: {entry['feature']}"
        )


# ── Survival Curve Endpoint (IT-20 through IT-22) ────────────────────────────

def test_survival_curve_returns_valid_structure():
    """IT-20: POST /predict/survival/curve must return months, OS, and RFS arrays."""
    schema = client.get("/predict/survival/schema").json()
    features = schema["defaults"]

    resp = client.post("/predict/survival/curve", json={"features": features})
    assert resp.status_code == 200, f"Curve endpoint returned {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "months" in data
    assert "overall_survival" in data
    assert "relapse_free_survival" in data


def test_survival_curve_has_21_time_points():
    """IT-21: Survival curve must cover 0–120 months in 6-month steps (21 points)."""
    schema = client.get("/predict/survival/schema").json()
    features = schema["defaults"]

    resp = client.post("/predict/survival/curve", json={"features": features})
    data = resp.json()
    assert len(data["months"]) == 21, (
        f"Expected 21 time points (0–120 in steps of 6), got {len(data['months'])}"
    )
    assert data["months"][0] == 0
    assert data["months"][-1] == 120
    assert len(data["overall_survival"]) == 21
    assert len(data["relapse_free_survival"]) == 21


def test_survival_curve_probabilities_in_unit_interval():
    """IT-22: All survival curve probabilities must be in [0, 1]."""
    schema = client.get("/predict/survival/schema").json()
    features = schema["defaults"]

    resp = client.post("/predict/survival/curve", json={"features": features})
    data = resp.json()
    for key in ("overall_survival", "relapse_free_survival"):
        for i, prob in enumerate(data[key]):
            assert 0.0 <= prob <= 1.0, (
                f"{key}[{i}] = {prob} is outside [0, 1]"
            )


# ── Data Endpoints (IT-15 through IT-16) ─────────────────────────────────────

def test_wbcd_data_endpoint_returns_569_rows():
    """IT-15: GET /data/wbcd must return exactly 569 patient records."""
    resp = client.get("/data/wbcd")
    assert resp.status_code == 200
    data = resp.json()
    assert data["rows"] == 569, f"Expected 569 rows, got {data['rows']}"


def test_metabric_data_endpoint_returns_rows():
    """IT-16: GET /data/metabric must return a non-empty dataset."""
    resp = client.get("/data/metabric")
    assert resp.status_code == 200
    data = resp.json()
    assert data["rows"] > 0, "METABRIC endpoint returned 0 rows"
    assert "column_names" in data
    assert len(data["column_names"]) > 0
