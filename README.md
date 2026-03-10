# Breast Cancer Prediction

**Data Science Capstone Project**

**Team Members:** Anagha Deshpande, Thanya Mysore Santhosh, and Melissa Rejuan

---

## Problem Statement & Objectives

Breast cancer is one of the most prevalent cancers worldwide, and early, accurate assessment of tumor malignancy and patient risk significantly improves treatment outcomes. This project builds an end-to-end breast cancer prediction system that uses clinical and genomic data to support three core tasks:

1. **Binary Classification** — Predict whether a tumor is benign or malignant
2. **Risk Stratification** — Assign patients to Low / Medium / High risk categories
3. **Survival Analysis** — Model time-to-event patient outcomes

The goal is to deliver an interpretable, deployable prediction platform that could support clinical decision-making in breast cancer treatment planning.

---

## Datasets

| Dataset | Role | Source |
|---|---|---|
| **METABRIC** | Primary dataset — risk stratification & survival analysis | [Kaggle](https://www.kaggle.com/datasets/gunesevitan/breast-cancer-metabric) · [cBioPortal](https://www.cbioportal.org/) |
| **Wisconsin Breast Cancer (WBCD)** | Binary classification | [UCI ML Repository](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic) |

### METABRIC
- **Size:** 2,509 patients x 33 columns (after cleaning); risk model uses 1,981 rows after removing records with missing survival data
- **Key features:**
  - *Demographics:* Age at Diagnosis, Inferred Menopausal State
  - *Tumor characteristics:* Tumor Size, Tumor Stage, Neoplasm Histologic Grade, Cellularity
  - *Molecular markers:* ER Status, HER2 Status, PR Status, Pam50 + Claudin-low subtype, 3-Gene Classifier Subtype
  - *Treatment:* Type of Breast Surgery, Chemotherapy, Hormone Therapy, Radio Therapy
  - *Outcomes:* Overall Survival (Months), Relapse Free Status, Patient's Vital Status
- **Challenges:** ~30% missingness in 3-Gene Classifier Subtype (29.7%) and Tumor Stage (28.7%); class imbalance in vital status

### WBCD
- **Size:** 569 samples x 30 numeric features + binary target (benign/malignant)
- **Key features:** Cell nucleus measurements (radius, texture, perimeter, area, smoothness, etc.)
- **Challenges:** Moderate class imbalance (~63% benign, ~37% malignant)

---

## EDA Findings

### METABRIC (`eda/metabric_exploration.ipynb`)
- **Age at diagnosis** is approximately normally distributed, centered around 55–65 years
- **Tumor Stage 2** is the most common stage, followed by Stage 1; Stages 3–4 are less frequent
- **Invasive Ductal Carcinoma** is the dominant cancer subtype, followed by Invasive Lobular Carcinoma
- **Surgery type** is nearly split between Mastectomy (~1,000 cases) and Breast Conserving (~950 cases), with ~550 missing
- **Vital status** is imbalanced: most patients are living, followed by died of disease, then died of other causes
- **Correlations:** Nottingham prognostic index correlates positively with Tumor Size and Lymph nodes examined positive; Overall Survival Months and Relapse Free Status Months are strongly correlated with each other; most other feature pairs show low multicollinearity

### WBCD (`eda/wbcd_exploration.ipynb`)
- **No missing values** and no duplicates confirmed across all 569 samples
- **Class distribution:** 62.7% benign, 37.3% malignant — a mild imbalance addressed with `class_weight="balanced"`
- **Feature distributions:** Area and size features (radius, perimeter, area) are right-skewed; most features differ meaningfully between benign and malignant cases
- **Correlations:** Radius, perimeter, and area are highly correlated with each other; `_worst` variants (worst-case cell measurements) tend to be stronger discriminators than `_mean` variants

---

## Methods & Models

### Task A -- Binary Classification (`models/binary_classification.ipynb`)
Classifies tumors as benign or malignant using the WBCD dataset.
- Logistic Regression (baseline)
- Calibrated Random Forest
- Train/validation/test split: 70% / 15% / 15%, stratified
- **Metrics:** ROC-AUC, PR-AUC, Precision, Recall, F1-score, Confusion Matrix

### Task B -- Risk Stratification (`models/risk.ipynb`)
Assigns patients to Low / Medium / High risk tiers using the METABRIC dataset.
- XGBoost classifier
- Risk buckets derived from predicted probability: Low (<0.33), Medium (0.33-0.66), High (>0.66)
- **Metrics:** Accuracy, Classification Report, Confusion Matrix

### Task C -- Survival Analysis (`models/survival_analysis.ipynb`)
Estimates patient survival probability over time using the METABRIC dataset.
- **Right censoring** accounted for: patients still living or not recurred at study end are treated as censored (event = 0), meaning we know they hadn't experienced the event yet but don't know if/when they will
- Kaplan-Meier estimator
- Cox Proportional Hazards model with 5-fold cross-validation
- Evaluated on both Overall Survival and Relapse-Free Status outcomes
- **Metrics:** C-index (concordance), time-dependent ROC-AUC at 12, 24, and 36 months

---

## Key Results

### Task A — Binary Classification (WBCD, Test Set)
| Model | ROC-AUC | PR-AUC | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| Logistic Regression | 0.9988 (val) | 0.9981 (val) | 98.8% | 1.00 | 0.94 | 0.97 |
| Calibrated Random Forest | **1.00** | **1.00** | **98.8%** | **1.00** | **0.97** | **0.98** |

### Task B — Risk Stratification (METABRIC, Test Set)
| Class | Precision | Recall | F1 |
|---|---|---|---|
| Low Risk | 0.96 | 0.89 | 0.92 |
| Medium Risk | 0.86 | 0.91 | 0.89 |
| High Risk | 0.91 | 0.93 | 0.92 |
| **Weighted Avg** | **0.91** | **0.91** | **0.91** |

Overall accuracy: **91.0%**

### Task C — Survival Analysis (METABRIC, Test Set)
| Outcome | C-Index | ROC-AUC @12mo | ROC-AUC @24mo | ROC-AUC @36mo |
|---|---|---|---|---|
| Overall Survival | 0.658 | 0.294 | 0.286 | 0.236 |
| Relapse-Free Status | 0.636 | 0.371 | 0.324 | 0.319 |

C-index values in the 0.63–0.67 range indicate moderate discrimination; consistent with the complexity of long-term survival prediction from clinical data.

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

### 3. Run EDA Notebooks

```bash
jupyter notebook eda/metabric_exploration.ipynb
jupyter notebook eda/wbcd_exploration.ipynb
```

### 4. Run Modeling Notebooks

Run in the following order to ensure cleaned data and saved models are available:

```bash
jupyter notebook models/binary_classification.ipynb
jupyter notebook models/risk.ipynb
jupyter notebook models/survival_analysis.ipynb
```

> **Note:** All notebooks read data from the `data/` folder using relative paths (e.g. `../data/clean_WBCD.csv`). Open them directly in VS Code or run Jupyter from the `models/` directory.

---

## Assumptions & Limitations

- **Missing data** in METABRIC (up to ~30% in some columns) is handled via imputation within model pipelines; records are not dropped outright.
- **Class imbalance** in both datasets is addressed using `class_weight="balanced"` and calibrated classifiers.
- The WBCD dataset serves as a clean baseline for binary classification and does not reflect the full clinical complexity of the METABRIC dataset.
- Risk buckets for Model B use fixed probability thresholds (0.33 / 0.66), which are heuristic and would require clinical validation before any real-world deployment.
- `Overall Survival Months` is excluded from risk stratification features to prevent data leakage.

---

## Current Progress & Next Steps

### Completed
- [x] Data ingestion and folder structure setup (`data/`, `eda/`, `models/`)
- [x] Data cleaning for METABRIC and WBCD datasets
- [x] EDA for both datasets
- [x] Model A: Binary classification pipeline implemented and evaluated
- [x] Model B: Risk stratification pipeline implemented and evaluated

### In Progress / Next Steps
- [ ] Complete Model C: Survival analysis — Cox PH model evaluation, threshold tuning, and result visualizations
- [ ] Finalize evaluation metrics and threshold tuning for Models B and C
- [ ] Build and connect the `webapp/` layer (Streamlit or FastAPI)
