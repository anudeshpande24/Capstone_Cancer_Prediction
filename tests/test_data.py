"""
test_data.py — Unit tests for raw dataset integrity.

Verifies that WBCD and METABRIC CSV files load correctly and satisfy
the structural properties assumed by the model training pipelines.

Run from repo root:
    pytest tests/test_data.py -v
"""
import pytest
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WBCD_PATH = DATA_DIR / "WBCD_dataset.csv"
METABRIC_PATH = DATA_DIR / "Breast Cancer METABRIC.csv"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def wbcd():
    """Load WBCD dataset and drop unnamed index columns."""
    df = pd.read_csv(WBCD_PATH)
    return df.loc[:, ~df.columns.str.startswith("Unnamed")]


@pytest.fixture(scope="module")
def metabric():
    """Load METABRIC dataset."""
    return pd.read_csv(METABRIC_PATH)


# ── WBCD Tests (UT-D01 through UT-D07) ───────────────────────────────────────

def test_wbcd_row_count(wbcd):
    """UT-D01: WBCD must contain exactly 569 patient records."""
    assert wbcd.shape[0] == 569, f"Expected 569 rows, got {wbcd.shape[0]}"


def test_wbcd_feature_count(wbcd):
    """UT-D02: WBCD must have at least 31 columns (id + diagnosis + 30 features)."""
    assert wbcd.shape[1] >= 31, f"Expected ≥31 columns, got {wbcd.shape[1]}"


def test_wbcd_no_missing_values(wbcd):
    """UT-D03: WBCD must contain zero null values across all columns."""
    null_count = wbcd.isnull().sum().sum()
    assert null_count == 0, f"Found {null_count} null values in WBCD"


def test_wbcd_no_duplicate_rows(wbcd):
    """UT-D04: WBCD must contain no duplicate rows."""
    dup_count = wbcd.duplicated().sum()
    assert dup_count == 0, f"Found {dup_count} duplicate rows in WBCD"


def test_wbcd_diagnosis_column_present(wbcd):
    """UT-D05: WBCD must contain the 'diagnosis' target column."""
    assert "diagnosis" in wbcd.columns, "Column 'diagnosis' missing from WBCD"


def test_wbcd_class_balance(wbcd):
    """UT-D06: Benign class should constitute approximately 62–63% of WBCD samples."""
    upper_diag = wbcd["diagnosis"].str.upper()
    # Original labels: N = Benign, R = Malignant (or B/M depending on version)
    value_counts = upper_diag.value_counts(normalize=True)
    benign_key = next((k for k in value_counts.index if k in ("N", "B")), None)
    if benign_key is not None:
        benign_frac = value_counts[benign_key]
    else:
        # Fallback: majority class should be ~63%
        benign_frac = value_counts.iloc[0]
    assert 0.60 <= benign_frac <= 0.66, (
        f"Expected benign fraction 60–66%, got {benign_frac:.1%}"
    )


def test_wbcd_features_are_numeric(wbcd):
    """UT-D07: All WBCD feature columns (excluding id and diagnosis) must be numeric."""
    feature_cols = [c for c in wbcd.columns if c not in ("id", "diagnosis")]
    numeric_count = wbcd[feature_cols].select_dtypes(include="number").shape[1]
    assert numeric_count == len(feature_cols), (
        f"Expected {len(feature_cols)} numeric feature columns, got {numeric_count}"
    )


# ── METABRIC Tests (UT-D08 through UT-D13) ───────────────────────────────────

def test_metabric_row_count(metabric):
    """UT-D08: METABRIC must contain exactly 2,509 patient records."""
    assert metabric.shape[0] == 2509, f"Expected 2509 rows, got {metabric.shape[0]}"


def test_metabric_no_duplicate_rows(metabric):
    """UT-D09: METABRIC must contain no duplicate rows."""
    dup_count = metabric.duplicated().sum()
    assert dup_count == 0, f"Found {dup_count} duplicate rows in METABRIC"


def test_metabric_survival_columns_present(metabric):
    """UT-D10: METABRIC must include all four survival outcome columns."""
    required = [
        "Overall Survival (Months)",
        "Overall Survival Status",
        "Relapse Free Status (Months)",
        "Relapse Free Status",
    ]
    missing = [c for c in required if c not in metabric.columns]
    assert not missing, f"Missing survival columns: {missing}"


def test_metabric_known_missing_columns_exist(metabric):
    """UT-D11: Columns with known high missingness must be present and contain nulls."""
    high_missing_cols = ["Tumor Stage", "3-Gene classifier subtype"]
    for col in high_missing_cols:
        assert col in metabric.columns, f"Expected column '{col}' not found"
        assert metabric[col].isnull().sum() > 0, (
            f"'{col}' was expected to have missing values but appears complete"
        )


def test_metabric_age_within_clinical_range(metabric):
    """UT-D12: Age at Diagnosis must fall within a plausible clinical range (18–110)."""
    col = "Age at Diagnosis"
    assert col in metabric.columns, f"Column '{col}' not found"
    ages = metabric[col].dropna()
    assert ages.min() >= 18, f"Minimum age {ages.min()} below 18"
    assert ages.max() <= 110, f"Maximum age {ages.max()} above 110"


def test_metabric_os_months_non_negative(metabric):
    """UT-D13: Overall Survival (Months) must be non-negative where present."""
    col = "Overall Survival (Months)"
    assert col in metabric.columns
    valid = metabric[col].dropna()
    assert (valid >= 0).all(), "Negative OS months found in METABRIC"
