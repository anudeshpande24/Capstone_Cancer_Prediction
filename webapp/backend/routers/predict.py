import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.model_loader import get_model_a, get_model_b, get_model_c

router = APIRouter(prefix="/predict", tags=["predict"])


class FeaturesRequest(BaseModel):
    features: dict


# ─── Schema endpoints ──────────────────────────────────────────────────────────

@router.get("/diagnosis/schema")
def diagnosis_schema():
    bundle = get_model_a()
    return {"features": bundle["features"], "stats": bundle["feature_stats"]}


@router.get("/risk/schema")
def risk_schema():
    bundle = get_model_b()
    return {
        "num_cols": bundle["num_cols"],
        "cat_cols": bundle["cat_cols"],
        "cat_options": bundle["cat_options"],
        "num_stats": bundle["num_stats"],
    }


@router.get("/survival/schema")
def survival_schema():
    bundle = get_model_c()
    return {
        "covariates": bundle["covariates"],
        "cat_options": bundle["cat_options"],
        "defaults": bundle["defaults"],
        "evaluation_times": bundle["evaluation_times"],
    }


# ─── Metrics endpoint ──────────────────────────────────────────────────────────

@router.get("/metrics")
def get_metrics():
    result = {}
    for key, loader in [("model_a", get_model_a), ("model_b", get_model_b), ("model_c", get_model_c)]:
        try:
            result[key] = loader().get("metrics")
        except Exception:
            result[key] = None
    return result


# ─── Prediction endpoints ──────────────────────────────────────────────────────

@router.post("/diagnosis")
def predict_diagnosis(req: FeaturesRequest):
    bundle = get_model_a()
    model = bundle["model"]
    features = bundle["features"]

    row = {f: req.features.get(f, 0.0) for f in features}
    X = pd.DataFrame([row])[features]

    prob = float(model.predict_proba(X)[0][1])
    pred = int(prob >= 0.5)
    return {
        "prediction": pred,
        "label": "Malignant" if pred == 1 else "Benign",
        "probability_malignant": round(prob, 4),
        "probability_benign": round(1 - prob, 4),
    }


@router.post("/risk")
def predict_risk(req: FeaturesRequest):
    bundle = get_model_b()
    model = bundle["model"]
    features = bundle["features"]
    label_map = bundle["label_map"]

    row = {f: req.features.get(f, None) for f in features}
    X = pd.DataFrame([row])[features]

    pred = int(model.predict(X)[0])
    proba = model.predict_proba(X)[0].tolist()
    return {
        "prediction": pred,
        "label": label_map[pred],
        "probabilities": {label_map[i]: round(float(p), 4) for i, p in enumerate(proba)},
    }


@router.post("/survival")
def predict_survival(req: FeaturesRequest):
    bundle = get_model_c()
    cph_os = bundle["cph_os"]
    cph_rfs = bundle["cph_rfs"]
    encoders = bundle["encoders"]
    covariates = bundle["covariates"]
    defaults = bundle["defaults"]
    times = bundle["evaluation_times"]

    row = {}
    for col in covariates:
        val = req.features.get(col)
        if val is None:
            row[col] = defaults[col]
        elif col in encoders:
            le = encoders[col]
            try:
                row[col] = int(le.transform([str(val)])[0])
            except Exception:
                row[col] = defaults[col]
        else:
            row[col] = val

    X = pd.DataFrame([row])[covariates]

    sf_os = cph_os.predict_survival_function(X, times=times)
    sf_rfs = cph_rfs.predict_survival_function(X, times=times)

    return {
        "overall_survival": {int(t): round(float(sf_os.loc[t].iloc[0]), 4) for t in times},
        "relapse_free_survival": {int(t): round(float(sf_rfs.loc[t].iloc[0]), 4) for t in times},
    }
