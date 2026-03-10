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
- **Size:** 2,509 patients x 32 columns (after cleaning)
- **Key features:**
  - *Demographics:* Age at Diagnosis, Inferred Menopausal State
  - *Tumor characteristics:* Tumor Size, Tumor Stage, Neoplasm Histologic Grade, Cellularity
  - *Molecular markers:* ER Status, HER2 Status, PR Status, Pam50 + Claudin-low subtype, 3-Gene Classifier Subtype
  - *Treatment:* Type of Breast Surgery, Chemotherapy, Hormone Therapy, Radio Therapy
  - *Outcomes:* Overall Survival (Months), Relapse Free Status, Patient's Vital Status
- **Challenges:** ~30% missingness in 3-Gene Classifier Subtype and Tumor Stage; class imbalance in vital status

### WBCD
- **Size:** 569 samples x 30 numeric features + binary target (benign/malignant)
- **Key features:** Cell nucleus measurements (radius, texture, perimeter, area, smoothness, etc.)
- **Challenges:** Moderate class imbalance (~63% benign, ~37% malignant)

---

## Methods & Models

### Model A -- Binary Classification (`models/binary_classification.ipynb`)
Classifies tumors as benign or malignant using the WBCD dataset.
- Logistic Regression (baseline)
- Calibrated Random Forest (primary model -- saved as `models/model_a.pkl`)
- Train/validation/test split: 70% / 15% / 15%, stratified
- **Metrics:** ROC-AUC, PR-AUC, Precision, Recall, F1-score, Confusion Matrix

### Model B -- Risk Stratification (`models/risk.ipynb`)
Assigns patients to Low / Medium / High risk tiers using the METABRIC dataset.
- XGBoost classifier
- Risk buckets derived from predicted probability: Low (<0.33), Medium (0.33-0.66), High (>0.66)
- **Metrics:** Accuracy, Classification Report, Confusion Matrix

### Model C -- Survival Analysis (`models/survival_analysis.ipynb`)
Estimates patient survival probability over time using the METABRIC dataset.
- Kaplan-Meier estimator
- Cox Proportional Hazards model
- **Metrics:** C-index (concordance), Calibration curves

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
- [x] Model A: Binary classification pipeline implemented
- [x] Model B: Risk stratification pipeline implemented

### In Progress / Next Steps
- [ ] Complete Model C: Survival analysis — Kaplan-Meier curves, Cox PH model evaluation, and result visualizations
- [ ] Finalize evaluation metrics and threshold tuning for Models B and C
- [ ] Build and connect the `webapp/` layer (Streamlit or FastAPI)

**Data Science Capstone Project** by Anagha Deshpande, Thanya Mysore Santhosh, and Melissa Rejuan.

This project is an end-to-end breast cancer prediction system that combines clinical and genomic data to support cancer diagnosis, risk stratification, and survival analysis. Using the METABRIC dataset and the Wisconsin Breast Cancer dataset, we build a full-stack pipeline — from data ingestion and preprocessing through machine learning modeling to an interactive web dashboard.

The system addresses three core prediction tasks:

1. **Binary Classification** — Benign vs. Malignant tumor prediction
2. **Risk Stratification** — Categorizing patients into Low / Medium / High risk groups
3. **Survival Analysis** — Time-to-event modeling of patient outcomes