"""
Train and serialize all three models.
Run once from the repo root:
    python export_models.py
"""
import warnings
warnings.filterwarnings("ignore")

import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier
from lifelines import CoxPHFitter

ROOT = Path(__file__).parent
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)


# ─── MODEL A: Binary Classification (WBCD) ────────────────────────────────────
print("Training Model A: Binary Classification (WBCD)...")

df_a = pd.read_csv(ROOT / "WBCD_dataset.csv")
df_a["diagnosis"] = df_a["diagnosis"].astype(str).str.strip().str.upper()
df_a["target"] = df_a["diagnosis"].map({"R": 1, "N": 0})
df_a = df_a.drop(
    columns=["diagnosis", "id"] + [c for c in df_a.columns if c.startswith("Unnamed")],
    errors="ignore",
)
df_a = df_a.drop_duplicates()

X_a = df_a.drop(columns=["target"])
y_a = df_a["target"]

X_train_a, X_temp, y_train_a, y_temp = train_test_split(
    X_a, y_a, test_size=0.3, stratify=y_a, random_state=42
)
X_val_a, X_test_a, y_val_a, y_test_a = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
)

rf = Pipeline([
    ("scaler", StandardScaler()),
    ("rf", RandomForestClassifier(n_estimators=500, random_state=42, class_weight="balanced")),
])
rf_calibrated = CalibratedClassifierCV(rf, method="isotonic", cv=5)
rf_calibrated.fit(X_train_a, y_train_a)

feature_stats_a = {
    col: {
        "min": float(X_a[col].min()),
        "max": float(X_a[col].max()),
        "mean": float(X_a[col].mean()),
    }
    for col in X_a.columns
}

joblib.dump(
    {"model": rf_calibrated, "features": X_a.columns.tolist(), "feature_stats": feature_stats_a},
    MODELS_DIR / "model_a.pkl",
)
print(f"  Saved models/model_a.pkl  ({len(X_a.columns)} features)")


# ─── MODEL B: Risk Stratification (METABRIC) ──────────────────────────────────
print("Training Model B: Risk Stratification (METABRIC)...")

df_b = pd.read_csv(ROOT / "Breast Cancer METABRIC.csv")
df_b = df_b.drop_duplicates()

df_b["Risk_Level"] = pd.qcut(
    df_b["Overall Survival (Months)"], q=3, labels=["High", "Medium", "Low"]
)
df_b = df_b.drop(
    columns=["Overall Survival (Months)", "Overall Survival Status"], errors="ignore"
)
df_b = df_b.dropna(subset=["Risk_Level"]).copy()
df_b["Risk_Level"] = df_b["Risk_Level"].map({"Low": 0, "Medium": 1, "High": 2}).astype(int)

if "Age at Diagnosis" in df_b.columns:
    df_b["Age_Squared"] = df_b["Age at Diagnosis"] ** 2

df_b = df_b.drop(columns=["Patient ID", "Patient's Vital Status"], errors="ignore")

X_b = df_b.drop(columns=["Risk_Level"])
y_b = df_b["Risk_Level"]

X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(
    X_b, y_b, test_size=0.20, random_state=42, stratify=y_b
)

num_cols_b = X_train_b.select_dtypes(include=[np.number]).columns.tolist()
cat_cols_b = [c for c in X_train_b.columns if c not in num_cols_b]

preprocess_b = ColumnTransformer(
    transformers=[
        ("num", SimpleImputer(strategy="median"), num_cols_b),
        ("cat", Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), cat_cols_b),
    ],
    remainder="drop",
)

xgb = XGBClassifier(
    n_estimators=600,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1,
)

model_b = Pipeline(steps=[("preprocess", preprocess_b), ("model", xgb)])
model_b.fit(X_train_b, y_train_b)

cat_options_b = {c: sorted(str(v) for v in X_b[c].dropna().unique()) for c in cat_cols_b}
num_stats_b = {
    c: {"min": float(X_b[c].min()), "max": float(X_b[c].max()), "median": float(X_b[c].median())}
    for c in num_cols_b
}

joblib.dump(
    {
        "model": model_b,
        "features": X_b.columns.tolist(),
        "num_cols": num_cols_b,
        "cat_cols": cat_cols_b,
        "cat_options": cat_options_b,
        "num_stats": num_stats_b,
        "label_map": {0: "Low", 1: "Medium", 2: "High"},
    },
    MODELS_DIR / "model_b.pkl",
)
print(f"  Saved models/model_b.pkl")


# ─── MODEL C: Survival Analysis (METABRIC) ────────────────────────────────────
print("Training Model C: Survival Analysis (METABRIC)...")


def safe_mode(x, global_series=None):
    m = x.mode()
    if len(m) > 0:
        return x.fillna(m.iloc[0])
    elif global_series is not None:
        return x.fillna(global_series.mode().iloc[0])
    return x


def safe_mean(x, global_series=None):
    if x.notna().any():
        return x.fillna(x.mean())
    elif global_series is not None:
        return x.fillna(global_series.mean())
    return x


def safe_median(x, global_series=None):
    if x.notna().any():
        return x.fillna(x.median())
    elif global_series is not None:
        return x.fillna(global_series.median())
    return x


df_c = pd.read_csv(ROOT / "Breast Cancer METABRIC.csv")

# Imputation (mirrors survival_analysis.ipynb exactly)
df_c["Relapse Free Status"] = df_c.groupby("Cancer Type Detailed")["Relapse Free Status"].transform(
    lambda x: safe_mode(x, df_c["Relapse Free Status"])
)
df_c["Relapse Free Status (Months)"] = df_c.groupby(
    ["Cancer Type Detailed", "Relapse Free Status"]
)["Relapse Free Status (Months)"].transform(
    lambda x: safe_mean(x, df_c["Relapse Free Status (Months)"])
)
df_c["Overall Survival Status"] = df_c.groupby(
    ["Cancer Type Detailed", "Relapse Free Status"]
)["Overall Survival Status"].transform(
    lambda x: safe_mode(x, df_c["Overall Survival Status"])
)
df_c["Overall Survival (Months)"] = df_c.groupby(
    ["Cancer Type Detailed", "Overall Survival Status"]
)["Overall Survival (Months)"].transform(
    lambda x: safe_mean(x, df_c["Overall Survival (Months)"])
)
df_c["ER status measured by IHC"] = safe_mode(df_c["ER status measured by IHC"])
df_c["ER Status"] = df_c.groupby("ER status measured by IHC")["ER Status"].transform(
    lambda x: safe_mode(x, df_c["ER Status"])
)
df_c["HER2 status measured by SNP6"] = safe_mode(df_c["HER2 status measured by SNP6"])
df_c["HER2 Status"] = df_c.groupby("HER2 status measured by SNP6")["HER2 Status"].transform(
    lambda x: safe_mode(x, df_c["HER2 Status"])
)
df_c["PR Status"] = df_c.groupby("Cancer Type Detailed")["PR Status"].transform(
    lambda x: safe_mode(x, df_c["PR Status"])
)
for col in ["Chemotherapy", "Hormone Therapy", "Radio Therapy"]:
    df_c[col] = df_c.groupby("Cancer Type Detailed")[col].transform(
        lambda x: safe_mode(x, df_c[col])
    )
df_c["Age at Diagnosis"] = df_c.groupby("Cancer Type Detailed")["Age at Diagnosis"].transform(
    lambda x: safe_mean(x, df_c["Age at Diagnosis"])
)
df_c["Cohort"] = df_c.groupby("Cancer Type Detailed")["Cohort"].transform(
    lambda x: safe_median(x, df_c["Cohort"])
)
df_c["Cellularity"] = df_c.groupby("Cancer Type Detailed")["Cellularity"].transform(
    lambda x: safe_mode(x, df_c["Cellularity"])
)
df_c["Tumor Stage"] = df_c.groupby(["Cancer Type Detailed", "Cellularity"])[
    "Tumor Stage"
].transform(lambda x: safe_median(x, df_c["Tumor Stage"]))
df_c["Tumor Stage"] = df_c.groupby("Cancer Type Detailed")["Tumor Stage"].transform(
    lambda x: safe_median(x, df_c["Tumor Stage"])
)
df_c["Tumor Size"] = df_c.groupby(["Cancer Type Detailed", "Tumor Stage"])[
    "Tumor Size"
].transform(lambda x: safe_median(x, df_c["Tumor Size"]))
df_c["Tumor Size"] = df_c.groupby("Cancer Type Detailed")["Tumor Size"].transform(
    lambda x: safe_median(x, df_c["Tumor Size"])
)
df_c["Tumor Size"] = safe_mode(df_c["Tumor Size"])
for col in [
    "Neoplasm Histologic Grade", "Primary Tumor Laterality", "Tumor Other Histologic Subtype",
    "Mutation Count", "Pam50 + Claudin-low subtype", "Integrative Cluster",
    "Type of Breast Surgery", "3-Gene classifier subtype",
]:
    df_c[col] = df_c.groupby("Cancer Type Detailed")[col].transform(
        lambda x: safe_mode(x, df_c[col])
    )
df_c["Tumor Other Histologic Subtype"] = df_c["Tumor Other Histologic Subtype"].fillna("Ductal/NST")
df_c["Nottingham prognostic index"] = df_c.groupby("Tumor Size")[
    "Nottingham prognostic index"
].transform(lambda x: safe_median(x, df_c["Nottingham prognostic index"]))
df_c["Nottingham prognostic index"] = df_c["Nottingham prognostic index"].fillna(
    df_c["Nottingham prognostic index"].median()
)
df_c["Lymph nodes examined positive"] = df_c.groupby("Cancer Type Detailed")[
    "Lymph nodes examined positive"
].transform(lambda x: safe_mode(x, df_c["Lymph nodes examined positive"]))
df_c["Inferred Menopausal State"] = safe_mode(df_c["Inferred Menopausal State"])
df_c.drop(columns=["Patient's Vital Status", "Integrative Cluster"], inplace=True, errors="ignore")

# Label encode categoricals
object_cols_c = [
    "Type of Breast Surgery", "Cancer Type", "Cancer Type Detailed", "Cellularity",
    "Chemotherapy", "Pam50 + Claudin-low subtype", "ER status measured by IHC",
    "ER Status", "HER2 status measured by SNP6", "HER2 Status", "Tumor Other Histologic Subtype",
    "Hormone Therapy", "Inferred Menopausal State", "Primary Tumor Laterality",
    "Oncotree Code", "PR Status", "Radio Therapy", "Sex", "3-Gene classifier subtype",
]
encoders_c = {}
cat_options_c = {}
for col in object_cols_c:
    if col in df_c.columns:
        le = LabelEncoder()
        df_c[col] = np.uint8(le.fit_transform(df_c[col]))
        encoders_c[col] = le
        cat_options_c[col] = le.classes_.tolist()

df_c["Overall Survival Status"] = np.uint8(
    df_c["Overall Survival Status"].map({"Living": 0, "Deceased": 1})
)
df_c["Relapse Free Status"] = np.uint8(
    df_c["Relapse Free Status"].map({"Not Recurred": 0, "Recurred": 1})
)

covariates = [
    "Age at Diagnosis", "Type of Breast Surgery", "Cancer Type", "Cancer Type Detailed",
    "Cellularity", "Chemotherapy", "Pam50 + Claudin-low subtype", "Cohort",
    "ER status measured by IHC", "ER Status", "Neoplasm Histologic Grade",
    "HER2 status measured by SNP6", "HER2 Status", "Tumor Other Histologic Subtype",
    "Hormone Therapy", "Inferred Menopausal State", "Primary Tumor Laterality",
    "Lymph nodes examined positive", "Mutation Count", "Nottingham prognostic index",
    "Oncotree Code", "PR Status", "3-Gene classifier subtype", "Tumor Size", "Tumor Stage",
]

df_train_c, _ = train_test_split(
    df_c, test_size=0.2, stratify=df_c["Cancer Type Detailed"], shuffle=True, random_state=0
)
df_train_c = df_train_c.reset_index(drop=True)

cph_os = CoxPHFitter(baseline_estimation_method="breslow", n_baseline_knots=4, penalizer=1e-2)
cph_os.fit(
    df_train_c[covariates + ["Overall Survival (Months)", "Overall Survival Status"]],
    duration_col="Overall Survival (Months)",
    event_col="Overall Survival Status",
)

cph_rfs = CoxPHFitter(baseline_estimation_method="breslow", n_baseline_knots=4, penalizer=1e-2)
cph_rfs.fit(
    df_train_c[covariates + ["Relapse Free Status (Months)", "Relapse Free Status"]],
    duration_col="Relapse Free Status (Months)",
    event_col="Relapse Free Status",
)

defaults_c = {col: float(df_c[col].median()) for col in covariates}

joblib.dump(
    {
        "cph_os": cph_os,
        "cph_rfs": cph_rfs,
        "encoders": encoders_c,
        "covariates": covariates,
        "defaults": defaults_c,
        "cat_options": cat_options_c,
        "evaluation_times": [12, 24, 36],
    },
    MODELS_DIR / "model_c.pkl",
)
print(f"  Saved models/model_c.pkl")

print("\nAll models exported successfully.")
