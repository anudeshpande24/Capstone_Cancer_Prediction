"""
generate_figures.py — Produce all report figures and save to figures/

Run from repo root:
    python generate_figures.py
"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as mpatch
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import seaborn as sns
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    roc_curve, auc, confusion_matrix, ConfusionMatrixDisplay
)
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier
from lifelines import KaplanMeierFitter

ROOT   = Path(__file__).parent
FIGS   = ROOT / "figures"
FIGS.mkdir(exist_ok=True)

# Consistent style
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
})
NU_DARK  = "#1f3864"
NU_RED   = "#c00000"
PINK     = "#f43f7a"
GRAY     = "#555555"


# ─── Helper ───────────────────────────────────────────────────────────────────
def save(fig, name):
    path = FIGS / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Saved figures/{name}")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — EDA Overview (WBCD class distribution + correlation heatmap)
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Figure 1: EDA Overview...")

df_wbcd = pd.read_csv(ROOT / "data" / "WBCD_dataset.csv")
df_wbcd = df_wbcd.loc[:, ~df_wbcd.columns.str.startswith("Unnamed")]
df_wbcd["diagnosis_label"] = df_wbcd["diagnosis"].str.upper().map({"N": "Benign", "R": "Malignant"})

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# --- Left: class distribution ---
ax = axes[0]
counts = df_wbcd["diagnosis_label"].value_counts()
bars = ax.bar(counts.index, counts.values,
              color=[NU_DARK, NU_RED], edgecolor="white", linewidth=1.2, width=0.5)
ax.set_title("WBCD Class Distribution", fontsize=13, fontweight="bold", color=NU_DARK, pad=10)
ax.set_ylabel("Number of Patients", fontsize=11)
ax.set_xlabel("Diagnosis", fontsize=11)
for bar, val in zip(bars, counts.values):
    pct = val / counts.sum() * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 4,
            f"{val}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=10, color=GRAY)
ax.set_ylim(0, counts.max() * 1.18)
ax.tick_params(labelsize=10)

# --- Right: correlation heatmap (top 10 most variable features) ---
ax = axes[1]
feature_cols = [c for c in df_wbcd.columns if c not in ("id", "diagnosis", "diagnosis_label")]
top_features = df_wbcd[feature_cols].std().nlargest(10).index.tolist()
corr = df_wbcd[top_features].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, ax=ax, cmap="coolwarm", center=0,
            vmin=-1, vmax=1, annot=True, fmt=".1f", annot_kws={"size": 7},
            linewidths=0.4, cbar_kws={"shrink": 0.8})
ax.set_title("Feature Correlation (Top 10 by Variance)", fontsize=13,
             fontweight="bold", color=NU_DARK, pad=10)
ax.tick_params(axis="x", rotation=45, labelsize=7)
ax.tick_params(axis="y", rotation=0, labelsize=7)

fig.suptitle("Exploratory Data Analysis — WBCD Dataset", fontsize=14,
             fontweight="bold", color=NU_DARK, y=1.02)
fig.tight_layout()
save(fig, "eda_overview.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Model A ROC Curve
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Figure 2: Model A ROC Curve...")

# Replicate exact split from export_models.py
df_a = pd.read_csv(ROOT / "data" / "WBCD_dataset.csv")
df_a["diagnosis"] = df_a["diagnosis"].astype(str).str.strip().str.upper()
df_a["target"] = df_a["diagnosis"].map({"R": 1, "N": 0})
df_a = df_a.drop(
    columns=["diagnosis", "id"] + [c for c in df_a.columns if c.startswith("Unnamed")],
    errors="ignore"
).drop_duplicates()

X_a = df_a.drop(columns=["target"])
y_a = df_a["target"]
_, X_temp, _, y_temp = train_test_split(X_a, y_a, test_size=0.3, stratify=y_a, random_state=42)
_, X_test_a, _, y_test_a = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)

bundle_a = joblib.load(ROOT / "models" / "model_a.pkl")
model_a  = bundle_a["model"]
y_proba_a = model_a.predict_proba(X_test_a)[:, 1]

fpr, tpr, _ = roc_curve(y_test_a, y_proba_a)
roc_auc = auc(fpr, tpr)

fig, ax = plt.subplots(figsize=(5.5, 5))
ax.plot(fpr, tpr, color=NU_RED, lw=2.5, label=f"Calibrated RF  (AUC = {roc_auc:.3f})")
ax.plot([0, 1], [0, 1], color="lightgray", lw=1.5, linestyle="--", label="Random classifier")
ax.fill_between(fpr, tpr, alpha=0.08, color=NU_RED)
ax.set_xlabel("False Positive Rate", fontsize=12)
ax.set_ylabel("True Positive Rate", fontsize=12)
ax.set_title("Model A — ROC Curve\n(WBCD Test Set, n = 86)", fontsize=13,
             fontweight="bold", color=NU_DARK)
ax.legend(fontsize=10, loc="lower right")
ax.set_xlim([-0.01, 1.01])
ax.set_ylim([-0.01, 1.05])
ax.tick_params(labelsize=10)
fig.tight_layout()
save(fig, "model_a_roc.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Model B Confusion Matrix
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Figure 3: Model B Confusion Matrix...")

# Replicate exact split from export_models.py
df_b = pd.read_csv(ROOT / "data" / "Breast Cancer METABRIC.csv").drop_duplicates()
df_b["Risk_Level"] = pd.qcut(
    df_b["Overall Survival (Months)"], q=3, labels=["High", "Medium", "Low"]
)
df_b = df_b.drop(columns=["Overall Survival (Months)", "Overall Survival Status"], errors="ignore")
df_b = df_b.dropna(subset=["Risk_Level"]).copy()
df_b["Risk_Level"] = df_b["Risk_Level"].map({"Low": 0, "Medium": 1, "High": 2}).astype(int)
if "Age at Diagnosis" in df_b.columns:
    df_b["Age_Squared"] = df_b["Age at Diagnosis"] ** 2
df_b = df_b.drop(columns=["Patient ID", "Patient's Vital Status"], errors="ignore")

X_b = df_b.drop(columns=["Risk_Level"])
y_b = df_b["Risk_Level"]
_, X_test_b, _, y_test_b = train_test_split(
    X_b, y_b, test_size=0.20, random_state=42, stratify=y_b
)

bundle_b = joblib.load(ROOT / "models" / "model_b.pkl")
model_b  = bundle_b["model"]
y_pred_b = model_b.predict(X_test_b)

cm = confusion_matrix(y_test_b, y_pred_b, labels=[0, 1, 2])
labels = ["Low", "Medium", "High"]

fig, ax = plt.subplots(figsize=(5.5, 4.5))
im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

tick_marks = np.arange(3)
ax.set_xticks(tick_marks)
ax.set_yticks(tick_marks)
ax.set_xticklabels(labels, fontsize=11)
ax.set_yticklabels(labels, fontsize=11)
ax.set_xlabel("Predicted Label", fontsize=12, labelpad=8)
ax.set_ylabel("True Label", fontsize=12, labelpad=8)
ax.set_title("Model B — Confusion Matrix\n(METABRIC Test Set, n = 397)",
             fontsize=13, fontweight="bold", color=NU_DARK)

thresh = cm.max() / 2
for i in range(3):
    for j in range(3):
        ax.text(j, i, f"{cm[i,j]}",
                ha="center", va="center", fontsize=13,
                color="white" if cm[i,j] > thresh else NU_DARK,
                fontweight="bold")

fig.tight_layout()
save(fig, "model_b_confusion.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Model C Survival Curves (KM Baseline + CoxPH Individual)
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Figure 4: Model C Survival Curves...")

bundle_c = joblib.load(ROOT / "models" / "model_c.pkl")
cph_os   = bundle_c["cph_os"]
cph_rfs  = bundle_c["cph_rfs"]
covariates = bundle_c["covariates"]
defaults   = bundle_c["defaults"]
encoders   = bundle_c["encoders"]

# Load METABRIC for KM baseline
df_m = pd.read_csv(ROOT / "data" / "Breast Cancer METABRIC.csv")
df_m_os  = df_m.dropna(subset=["Overall Survival (Months)", "Overall Survival Status"])
df_m_rfs = df_m.dropna(subset=["Relapse Free Status (Months)", "Relapse Free Status"])

# Map status strings to 0/1
os_event  = df_m_os["Overall Survival Status"].map({"Living": 0, "Deceased": 1}).fillna(0).astype(int)
rfs_event = df_m_rfs["Relapse Free Status"].map({"Not Recurred": 0, "Recurred": 1}).fillna(0).astype(int)

# CoxPH individual prediction using defaults
X_default = pd.DataFrame([defaults])[covariates]
times_curve = list(range(0, 121, 6))
sf_os  = cph_os.predict_survival_function(X_default, times=times_curve)
sf_rfs = cph_rfs.predict_survival_function(X_default, times=times_curve)
os_curve  = sf_os.values.flatten()
rfs_curve = sf_rfs.values.flatten()

fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

# --- Left: Overall Survival ---
ax = axes[0]
kmf_os = KaplanMeierFitter()
kmf_os.fit(df_m_os["Overall Survival (Months)"], event_observed=os_event)
t_km = kmf_os.survival_function_.index
s_km = kmf_os.survival_function_["KM_estimate"]
ax.step(t_km, s_km, where="post", color=GRAY, lw=1.8, linestyle="--",
        label="KM Baseline (population)", alpha=0.8)
ax.plot(times_curve, os_curve, color=NU_RED, lw=2.5,
        label="CoxPH (median patient)")
ax.fill_between(times_curve, os_curve, alpha=0.10, color=NU_RED)
ax.set_xlabel("Time (Months)", fontsize=11)
ax.set_ylabel("Survival Probability", fontsize=11)
ax.set_title("Overall Survival", fontsize=13, fontweight="bold", color=NU_DARK)
ax.legend(fontsize=9)
ax.set_ylim(0, 1.05)
ax.set_xlim(0, 120)
ax.tick_params(labelsize=10)

# --- Right: Relapse-Free Survival ---
ax = axes[1]
kmf_rfs = KaplanMeierFitter()
kmf_rfs.fit(df_m_rfs["Relapse Free Status (Months)"], event_observed=rfs_event)
t_km2 = kmf_rfs.survival_function_.index
s_km2 = kmf_rfs.survival_function_["KM_estimate"]
ax.step(t_km2, s_km2, where="post", color=GRAY, lw=1.8, linestyle="--",
        label="KM Baseline (population)", alpha=0.8)
ax.plot(times_curve, rfs_curve, color=NU_DARK, lw=2.5,
        label="CoxPH (median patient)")
ax.fill_between(times_curve, rfs_curve, alpha=0.10, color=NU_DARK)
ax.set_xlabel("Time (Months)", fontsize=11)
ax.set_ylabel("Relapse-Free Probability", fontsize=11)
ax.set_title("Relapse-Free Survival", fontsize=13, fontweight="bold", color=NU_DARK)
ax.legend(fontsize=9)
ax.set_ylim(0, 1.05)
ax.set_xlim(0, 120)
ax.tick_params(labelsize=10)

fig.suptitle("Model C — Survival Curves: KM Baseline vs. CoxPH Individual Prediction\n(METABRIC Dataset)",
             fontsize=13, fontweight="bold", color=NU_DARK, y=1.01)
fig.tight_layout()
save(fig, "model_c_survival.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — System Architecture Diagram
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Figure 5: Architecture Diagram...")

fig, ax = plt.subplots(figsize=(13, 7))
ax.set_xlim(0, 13)
ax.set_ylim(0, 7)
ax.axis("off")

def box(ax, x, y, w, h, label, sublabel="", facecolor=NU_DARK, textcolor="white", fontsize=10):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.08",
                          facecolor=facecolor, edgecolor="white",
                          linewidth=1.5, zorder=3)
    ax.add_patch(rect)
    cy = y + h / 2
    if sublabel:
        ax.text(x + w/2, cy + 0.13, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=textcolor, zorder=4)
        ax.text(x + w/2, cy - 0.22, sublabel, ha="center", va="center",
                fontsize=fontsize - 1.5, color=textcolor, alpha=0.85, zorder=4)
    else:
        ax.text(x + w/2, cy, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=textcolor, zorder=4)

def arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.8), zorder=2)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.08, my, label, fontsize=8, color=GRAY, va="center")

# ── Row 1: Data sources ───────────────────────────────────────────────────────
ax.text(6.5, 6.65, "BreastCare — System Architecture", ha="center", va="center",
        fontsize=14, fontweight="bold", color=NU_DARK)

box(ax, 1.0, 5.5, 2.6, 0.8, "WBCD Dataset", "569 patients · 30 features",
    facecolor="#2d5fa8")
box(ax, 4.5, 5.5, 2.6, 0.8, "METABRIC Dataset", "2,509 patients · 33 features",
    facecolor="#2d5fa8")
box(ax, 8.0, 5.5, 2.6, 0.8, "METABRIC Dataset", "2,509 patients · 33 features",
    facecolor="#2d5fa8")

# ── Row 2: Models ─────────────────────────────────────────────────────────────
box(ax, 1.0, 3.9, 2.6, 1.1, "Model A", "Calibrated Random Forest\nTumor Diagnosis",
    facecolor=NU_RED)
box(ax, 4.5, 3.9, 2.6, 1.1, "Model B", "XGBoost Classifier\nRisk Stratification",
    facecolor=NU_RED)
box(ax, 8.0, 3.9, 2.6, 1.1, "Model C", "Cox PH × 2\nSurvival Analysis",
    facecolor=NU_RED)

# ── Row 3: Serialized bundles ─────────────────────────────────────────────────
box(ax, 1.0, 2.6, 2.6, 0.75, "model_a.pkl", "joblib serialized",
    facecolor="#555555")
box(ax, 4.5, 2.6, 2.6, 0.75, "model_b.pkl", "joblib serialized",
    facecolor="#555555")
box(ax, 8.0, 2.6, 2.6, 0.75, "model_c.pkl", "joblib serialized",
    facecolor="#555555")

# ── Row 4: FastAPI ────────────────────────────────────────────────────────────
box(ax, 3.2, 1.35, 6.0, 0.85, "FastAPI Backend  (port 8000)",
    "POST /predict/diagnosis · /predict/risk · /predict/survival · GET /predict/shap",
    facecolor="#1a3a1a", fontsize=9)

# ── Row 5: Streamlit ──────────────────────────────────────────────────────────
box(ax, 3.2, 0.2, 6.0, 0.85, "Streamlit Frontend  (port 8501)",
    "Diagnosis · Risk · Survival · Metrics · Cohort Comparison · Data Overview",
    facecolor=PINK, fontsize=9)

# ── Arrows: Data → Models ─────────────────────────────────────────────────────
arrow(ax, 2.30, 5.50, 2.30, 5.00)
arrow(ax, 5.80, 5.50, 5.80, 5.00)
arrow(ax, 9.30, 5.50, 9.30, 5.00)

# ── Arrows: Models → PKL ─────────────────────────────────────────────────────
arrow(ax, 2.30, 3.90, 2.30, 3.35)
arrow(ax, 5.80, 3.90, 5.80, 3.35)
arrow(ax, 9.30, 3.90, 9.30, 3.35)

# ── Arrows: PKL → FastAPI (converge to center) ───────────────────────────────
arrow(ax, 2.30, 2.60, 4.50, 2.20)
arrow(ax, 5.80, 2.60, 6.20, 2.20)
arrow(ax, 9.30, 2.60, 8.00, 2.20)

# ── Arrow: FastAPI → Streamlit ────────────────────────────────────────────────
arrow(ax, 6.20, 1.35, 6.20, 1.05)

# ── Legend labels ─────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(facecolor="#2d5fa8", label="Data Sources"),
    mpatches.Patch(facecolor=NU_RED,    label="ML Models"),
    mpatches.Patch(facecolor="#555555", label="Serialized Bundles"),
    mpatches.Patch(facecolor="#1a3a1a", label="FastAPI Backend"),
    mpatches.Patch(facecolor=PINK,      label="Streamlit Frontend"),
]
ax.legend(handles=legend_items, loc="lower left", fontsize=8.5,
          framealpha=0.9, edgecolor=GRAY)

fig.tight_layout()
save(fig, "architecture.png")

print("\nAll figures saved to figures/")
