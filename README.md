# BreastCare Decision Support Tool

**Data Science Capstone Project**

**Team Members:** Anagha Deshpande, Thanya Mysore Santhosh, and Melissa Rejuan

---

## Overview

Breast cancer is one of the most prevalent cancers worldwide. Early, accurate assessment of tumor malignancy and patient risk significantly improves treatment outcomes. This project delivers an end-to-end breast cancer clinical decision support platform — **BreastCare Decision Support Tool** — that uses machine learning on clinical and genomic data to support three core prediction tasks:

1. **Tumor Diagnosis** — Predict whether a breast mass is Benign or Malignant
2. **Risk Stratification** — Classify patients into Low, Medium, or High risk tiers
3. **Survival Analysis** — Estimate Overall Survival and Relapse-Free Survival probabilities over time

The platform is fully deployed as an interactive web application, accessible to clinicians and researchers with no technical background required.

---

## Datasets

| Dataset | Role | Source |
|---|---|---|
| **Wisconsin Breast Cancer Diagnostic (WBCD)** | Tumor diagnosis (Model A) | [UCI ML Repository](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic) |
| **METABRIC** | Risk stratification & survival analysis (Models B & C) | [Kaggle](https://www.kaggle.com/datasets/gunesevitan/breast-cancer-metabric) · [cBioPortal](https://www.cbioportal.org/) |

### WBCD
- **Size:** 569 patients × 30 numeric features + binary target
- **Features:** 30 real-valued measurements computed from digitized FNA biopsy images — each of 10 cell nucleus characteristics (radius, texture, perimeter, area, smoothness, compactness, concavity, concave points, symmetry, fractal dimension) captured as mean, standard error, and worst (largest) value
- **Target:** Benign / Malignant
- **Class balance:** ~63% Benign, ~37% Malignant
- **Missing values:** None

### METABRIC
- **Size:** 2,509 patients × 33 columns (post-cleaning)
- **Key features:**
  - *Demographics:* Age at Diagnosis, Inferred Menopausal State
  - *Tumor characteristics:* Tumor Size, Tumor Stage, Neoplasm Histologic Grade, Cellularity, Nottingham Prognostic Index
  - *Molecular markers:* ER Status, HER2 Status, PR Status, PAM50 + Claudin-low subtype
  - *Treatment:* Type of Breast Surgery, Chemotherapy, Hormone Therapy, Radio Therapy
  - *Outcomes:* Overall Survival (Months), Overall Survival Status, Relapse Free Status (Months), Relapse Free Status
- **Challenges:** ~30% missingness in Tumor Stage and 3-Gene Classifier Subtype; class imbalance in vital status

---

## EDA Findings

### WBCD (`eda/wbcd_exploration.ipynb`)
- No missing values or duplicates across all 569 samples
- Mild class imbalance (62.7% benign, 37.3% malignant) — addressed with `class_weight="balanced"`
- Area and size features are right-skewed; most features differ meaningfully between classes
- Radius, perimeter, and area are highly intercorrelated
- `_worst` features are consistently stronger discriminators than `_mean` features

### METABRIC (`eda/metabric_exploration.ipynb`)
- Age at diagnosis is approximately normally distributed, centered around 55–65 years
- Tumor Stage 2 is the most common stage; Stages 3–4 are less frequent
- Invasive Ductal Carcinoma is the dominant cancer subtype
- Nottingham Prognostic Index correlates positively with Tumor Size and lymph node positivity
- Overall Survival Months and Relapse-Free Survival Months are strongly correlated with each other

---

## Models

### Model A — Tumor Diagnosis (`models/binary_classification.ipynb`)

- **Algorithm:** `CalibratedClassifierCV` wrapping a `Pipeline` of `StandardScaler` → `RandomForestClassifier`
- **Dataset:** WBCD
- **Task:** Binary classification (Benign / Malignant)
- **Calibration:** Platt scaling applied post-hoc to produce reliable probability estimates
- **Split:** 70% train / 15% validation / 15% test, stratified

| Metric | Score |
|---|---|
| Accuracy | 98.8% |
| Precision | 100% |
| Recall | 97% |
| F1 Score | 98% |
| ROC-AUC | 1.00 |

---

### Model B — Risk Stratification (`models/risk.ipynb`)

- **Algorithm:** `XGBClassifier` (XGBoost)
- **Dataset:** METABRIC
- **Task:** 3-class classification (Low / Medium / High risk)
- **Risk label engineering:** Risk tiers derived from clinical thresholds (Nottingham Prognostic Index, tumor stage, lymph node status)
- **Overall Accuracy:** 91.0%

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Low Risk | 0.96 | 0.89 | 0.92 |
| Medium Risk | 0.86 | 0.91 | 0.89 |
| High Risk | 0.91 | 0.93 | 0.92 |
| **Weighted Avg** | **0.91** | **0.91** | **0.91** |

---

### Model C — Survival Analysis (`models/survival_analysis.ipynb`)

- **Algorithm:** Two independent `CoxPHFitter` models (lifelines library)
  - One fitted on Overall Survival (OS)
  - One fitted on Relapse-Free Survival (RFS)
- **Dataset:** METABRIC
- **Task:** Time-to-event prediction with right-censored data
- **Evaluation times:** 12, 24, 36 months (fixed); 0–120 months at 6-month intervals (survival curve)

| Outcome | C-Index |
|---|---|
| Overall Survival | 0.658 |
| Relapse-Free Survival | 0.636 |

C-index > 0.5 indicates the model ranks patient risk better than chance; values above 0.6 are considered clinically useful.

---

## Web Application

The BreastCare Decision Support Tool is a fully interactive web application built with **Streamlit** (frontend) and **FastAPI** (backend).

### Pages

| Page | Description |
|---|---|
| **Data Overview** | Explore WBCD and METABRIC datasets — previews, summary statistics, distributions, feature correlations, clinical breakdowns, and interactive subgroup filtering |
| **Diagnosis** | Enter 30 cell nucleus measurements, run Model A, receive Benign/Malignant prediction with probabilities. Download patient report. |
| **Risk Stratification** | Enter clinical and molecular features, run Model B, receive Low/Medium/High risk classification with per-class probabilities. Download patient report. |
| **Survival Analysis** | Enter clinical covariates, run Model C, receive OS and RFS survival probabilities at 12/24/36 months with expandable survival curve over 0–120 months. Download patient report. |
| **Model Metrics** | View model performance — animated metric bars, color-coded confusion matrices, and plain-English metric glossaries for all three models. |
| **Cohort Comparison** | Enter two patient profiles side by side, compare risk stratification results, and overlay their OS and RFS survival curves on a single interactive Plotly chart. |

---

## How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/Capstone_Cancer_Prediction.git
cd Capstone_Cancer_Prediction
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Export Models

Run this once to train and serialize all three model bundles into `models/`:

```bash
python export_models.py
```

### 4. Start the FastAPI Backend

```bash
cd webapp
uvicorn backend.main:app --reload --port 8000
```

### 5. Start the Streamlit Frontend

In a separate terminal:

```bash
cd webapp
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

---

## Assumptions & Limitations

- Missing data in METABRIC is handled via imputation within model pipelines; records with missing survival time are excluded from survival model training only
- Risk tier thresholds for Model B are heuristic and would require clinical validation before real-world deployment
- The Cox proportional hazards assumption (constant hazard ratio over time) is not formally tested; violations would silently bias survival estimates
- `Overall Survival Months` is excluded from risk stratification features to prevent data leakage
- C-index values of 0.636–0.658 represent moderate discriminative ability; the survival model is informative at the population level but not highly precise for individual patients