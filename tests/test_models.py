"""
test_models.py — Unit tests for the three serialized model bundles.

Tests load model_a/b/c.pkl directly and verify prediction outputs,
stored metrics, and mathematical properties (probability bounds,
monotone survival functions).

Prerequisites:
    python export_models.py   (generates the .pkl files)

Run from repo root:
    pytest tests/test_models.py -v
"""
import pytest
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


def _load_bundle(name: str) -> dict:
    """Load a model bundle, skipping the test if the file is missing."""
    path = MODELS_DIR / name
    if not path.exists():
        pytest.skip(f"{name} not found — run: python export_models.py")
    return joblib.load(path)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def model_a():
    return _load_bundle("model_a.pkl")


@pytest.fixture(scope="module")
def model_b():
    return _load_bundle("model_b.pkl")


@pytest.fixture(scope="module")
def model_c():
    return _load_bundle("model_c.pkl")


# ── Model A — Tumor Diagnosis (MT-A01 through MT-A06) ────────────────────────

def test_model_a_bundle_keys(model_a):
    """MT-A01: model_a.pkl must contain required keys."""
    required_keys = ("model", "features", "feature_stats", "metrics")
    for key in required_keys:
        assert key in model_a, f"Missing key in model_a bundle: '{key}'"


def test_model_a_feature_count(model_a):
    """MT-A02: Model A must expect exactly 30 input features."""
    assert len(model_a["features"]) == 30, (
        f"Expected 30 features, got {len(model_a['features'])}"
    )


def test_model_a_prediction_is_binary(model_a):
    """MT-A03: Model A prediction must be 0 (Benign) or 1 (Malignant)."""
    features = model_a["features"]
    stats = model_a["feature_stats"]
    X = np.array([[stats[f]["mean"] for f in features]])
    pred = model_a["model"].predict(X)
    assert pred[0] in (0, 1), f"Expected prediction in {{0, 1}}, got {pred[0]}"


def test_model_a_probabilities_sum_to_one(model_a):
    """MT-A04: Class probabilities must sum to 1.0 within floating-point tolerance."""
    features = model_a["features"]
    stats = model_a["feature_stats"]
    X = np.array([[stats[f]["mean"] for f in features]])
    proba = model_a["model"].predict_proba(X)[0]
    assert abs(proba.sum() - 1.0) < 1e-6, (
        f"Probabilities sum to {proba.sum():.8f}, expected 1.0"
    )


def test_model_a_probabilities_in_unit_interval(model_a):
    """MT-A05: All class probabilities must be in [0, 1]."""
    features = model_a["features"]
    stats = model_a["feature_stats"]
    X = np.array([[stats[f]["mean"] for f in features]])
    proba = model_a["model"].predict_proba(X)[0]
    assert np.all(proba >= 0) and np.all(proba <= 1), (
        f"Probability out of [0,1]: {proba}"
    )


def test_model_a_stored_roc_auc(model_a):
    """MT-A06: Stored test ROC-AUC must be ≥ 0.99 (reflects near-perfect discrimination)."""
    roc_auc = model_a["metrics"]["roc_auc"]
    assert roc_auc >= 0.99, f"ROC-AUC {roc_auc:.4f} below expected threshold of 0.99"


# ── Model B — Risk Stratification (MT-B01 through MT-B05) ────────────────────

def test_model_b_bundle_keys(model_b):
    """MT-B01: model_b.pkl must contain required keys."""
    required_keys = ("model", "features", "num_cols", "cat_cols",
                     "label_map", "cat_options", "num_stats", "metrics")
    for key in required_keys:
        assert key in model_b, f"Missing key in model_b bundle: '{key}'"


def test_model_b_label_map(model_b):
    """MT-B02: Model B label map must be {0: 'Low', 1: 'Medium', 2: 'High'}."""
    expected = {0: "Low", 1: "Medium", 2: "High"}
    assert model_b["label_map"] == expected, (
        f"Label map mismatch: {model_b['label_map']} != {expected}"
    )


def test_model_b_prediction_in_valid_classes(model_b):
    """MT-B03: Model B prediction using median/first-category defaults must be in {0, 1, 2}."""
    features = model_b["features"]
    num_stats = model_b["num_stats"]
    cat_options = model_b["cat_options"]

    row = {f: num_stats[f]["median"] for f in model_b["num_cols"]}
    row.update({f: cat_options[f][0] for f in model_b["cat_cols"]})

    X = pd.DataFrame([row])[features]
    pred = int(model_b["model"].predict(X)[0])
    assert pred in (0, 1, 2), f"Expected prediction in {{0, 1, 2}}, got {pred}"


def test_model_b_probabilities_have_three_classes(model_b):
    """MT-B04: Model B must output probabilities for exactly 3 classes."""
    features = model_b["features"]
    num_stats = model_b["num_stats"]
    cat_options = model_b["cat_options"]

    row = {f: num_stats[f]["median"] for f in model_b["num_cols"]}
    row.update({f: cat_options[f][0] for f in model_b["cat_cols"]})

    X = pd.DataFrame([row])[features]
    proba = model_b["model"].predict_proba(X)
    assert proba.shape == (1, 3), (
        f"Expected probability shape (1, 3), got {proba.shape}"
    )


def test_model_b_stored_accuracy(model_b):
    """MT-B05: Stored test accuracy must be ≥ 0.88."""
    accuracy = model_b["metrics"]["accuracy"]
    assert accuracy >= 0.88, (
        f"Stored accuracy {accuracy:.4f} below expected threshold of 0.88"
    )


# ── Model C — Survival Analysis (MT-C01 through MT-C05) ──────────────────────

def test_model_c_bundle_keys(model_c):
    """MT-C01: model_c.pkl must contain both Cox PH models and all metadata."""
    required_keys = ("cph_os", "cph_rfs", "covariates", "defaults",
                     "evaluation_times", "metrics")
    for key in required_keys:
        assert key in model_c, f"Missing key in model_c bundle: '{key}'"


def test_model_c_evaluation_times(model_c):
    """MT-C02: Evaluation times must be exactly [12, 24, 36] months."""
    assert model_c["evaluation_times"] == [12, 24, 36], (
        f"Unexpected evaluation times: {model_c['evaluation_times']}"
    )


def test_model_c_c_indices_above_chance(model_c):
    """MT-C03: Both concordance indices must exceed 0.5 (better than random ranking)."""
    metrics = model_c["metrics"]
    assert metrics["c_index_os"] > 0.5, (
        f"OS C-index {metrics['c_index_os']:.4f} ≤ 0.5"
    )
    assert metrics["c_index_rfs"] > 0.5, (
        f"RFS C-index {metrics['c_index_rfs']:.4f} ≤ 0.5"
    )


def test_model_c_survival_probabilities_in_unit_interval(model_c):
    """MT-C04: Survival probabilities at evaluation times must be in [0, 1]."""
    covariates = model_c["covariates"]
    defaults = model_c["defaults"]
    X = pd.DataFrame([defaults])[covariates]
    times = model_c["evaluation_times"]

    for label, cph in (("OS", model_c["cph_os"]), ("RFS", model_c["cph_rfs"])):
        sf = cph.predict_survival_function(X, times=times)
        vals = sf.values.flatten()
        assert np.all(vals >= 0) and np.all(vals <= 1), (
            f"{label} survival probability out of [0,1]: {vals}"
        )


def test_model_c_survival_function_non_increasing(model_c):
    """MT-C05: Survival function must be monotonically non-increasing over time."""
    covariates = model_c["covariates"]
    defaults = model_c["defaults"]
    X = pd.DataFrame([defaults])[covariates]
    curve_times = list(range(0, 121, 12))

    for label, cph in (("OS", model_c["cph_os"]), ("RFS", model_c["cph_rfs"])):
        sf = cph.predict_survival_function(X, times=curve_times)
        vals = sf.values.flatten()
        diffs = np.diff(vals)
        assert np.all(diffs <= 1e-9), (
            f"{label} survival function is not non-increasing; "
            f"found positive increment(s): {diffs[diffs > 1e-9]}"
        )
