# Breast Cancer Prediction

**Data Science Capstone Project** by Anagha Deshpande, Thanya Mysore Santhosh, and Melissa Rejuan.

This project is an end-to-end breast cancer prediction system that combines clinical and genomic data to support cancer diagnosis, risk stratification, and survival analysis. Using the METABRIC dataset and the Wisconsin Breast Cancer dataset, we build a full-stack pipeline — from data ingestion and preprocessing through machine learning modeling to an interactive web dashboard.

The system addresses three core prediction tasks:

1. **Binary Classification** — Benign vs. Malignant tumor prediction
2. **Risk Stratification** — Categorizing patients into Low / Medium / High risk groups
3. **Survival Analysis** — Time-to-event modeling of patient outcomes

The goal is to deliver an interpretable, deployable prediction platform that could support clinical decision-making in breast cancer treatment planning.

---

## Data Sources

| Dataset | Role | Link |
|---|---|---|
| **METABRIC** (CSV / API) | Primary dataset | [Kaggle](https://www.kaggle.com/datasets/gunesevitan/breast-cancer-metabric) · [cBioPortal](https://www.cbioportal.org/) |
| **Wisconsin Breast Cancer** | Feature reference for binary classification baseline | [UCI ML Repository](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic) |

### Dataset Description

| Source | Size | Variables | Challenges |
|---|---|---|---|
| Molecular Taxonomy of Breast Cancer International Consortium (METABRIC) database. Publicly available on the cBioPortal for Cancer Genomics. | 32 columns. Each row is a clinical profile of 2,509 breast cancer patients. | A mix of continuous variables (such as radius, texture, and area measurements), categorical variables (such as diagnosis-related descriptors), and boolean indicators. | Null values, class imbalance (e.g. Cancer Type Detection). |

**Key features include:**

- **Demographics:** Age at Diagnosis, Inferred Menopausal State
- **Tumor characteristics:** Tumor Size, Tumor Stage, Neoplasm Histologic Grade, Cellularity
- **Molecular markers:** ER Status, HER2 Status, PR Status, Pam50 + Claudin-low subtype, 3-Gene Classifier Subtype
- **Treatment:** Type of Breast Surgery, Chemotherapy, Hormone Therapy, Radio Therapy
- **Outcomes:** Overall Survival (Months), Relapse Free Status, Patient's Vital Status

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/Capstone_Cancer_Prediction.git
cd Capstone_Cancer_Prediction
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Notebook

Open `metabric_exploration.ipynb` in Jupyter Notebook or VS Code and run all cells:

```bash
jupyter notebook metabric_exploration.ipynb
```
---
## Analysis & Key Results

### Data Cleaning

- Removed the redundant `Sex` column (all patients are female) and the uniform `Cancer Type` column.
- Identified and assessed missing values across features; notable missingness in mutation count and certain molecular markers.
- Dropped duplicate records to ensure data integrity.

### Exploratory Data Analysis

- **Surgery type distribution:** Mastectomy is the most common procedure, followed by Breast Conserving surgery; a subset of records have missing surgery information.
- **Age at Diagnosis:** Roughly normally distributed with the majority of patients diagnosed between ages 40–75.
- **Vital Status:** The dataset is imbalanced — more patients are classified as "Living" than "Died of Disease" or "Died of Other Causes."
- **Tumor Stage vs. Vital Status:** Higher tumor stages (3–4) show a proportionally greater number of disease-related deaths compared to earlier stages.
- **Correlation analysis:** A heatmap of numerical features reveals relationships between tumor size, lymph nodes examined positive, Nottingham prognostic index, and survival outcomes.
- **Missing data profile:** Visualized missingness across all features to guide imputation strategy.

### Core Models (In Progress)

#### Model A: Binary Classification (Benign vs. Malignant)

Classifies tumors as benign or malignant using clinical features.

- Logistic Regression (baseline)
- Random Forest
- XGBoost
- Support Vector Machine (SVM)
- **Metrics:** Accuracy, Precision, Recall, F1-score, AUC-ROC

#### Model B: Risk Stratification (Low / Medium / High)

Assigns patients to risk tiers based on tumor characteristics and molecular markers.

- Multi-class Logistic Regression
- Gradient Boosting (XGBoost)
- Random Forest
- **Metrics:** Accuracy, Macro F1-score, Confusion Matrix

#### Model C: Survival Analysis (Time-to-Event)

Estimates patient survival probability over time.

- Kaplan-Meier estimator
- Cox Proportional Hazards model
- **Metrics:** C-index (concordance), Calibration curves

---

## Application Layer (Planned)

| Component | Technology | Purpose |
|---|---|---|
| Backend API | FastAPI / Flask | Serve model predictions via REST endpoints |
| Frontend Dashboard | Streamlit | Interactive UI for clinicians to input patient data and view predictions |
| Storage | PostgreSQL / SQLite | Persist patient records, predictions, and evaluation logs |
| Monitoring | Custom dashboards | Track accuracy, C-index, calibration, and error alerts over time |
