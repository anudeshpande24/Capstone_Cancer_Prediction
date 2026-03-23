import streamlit as st
from utils.data_loader import load_wbcd, load_metabric, api_health

st.set_page_config(page_title="Cancer Prediction Platform", layout="wide")
st.title("Breast Cancer Clinical Decision Support")

# ── API health check ──────────────────────────────────────────────────────────
if api_health():
    st.success("API connected — http://localhost:8000")
else:
    st.error("Cannot reach API. Run: uvicorn backend.main:app --reload --port 8000")
    st.stop()

st.divider()

# ── WBCD ──────────────────────────────────────────────────────────────────────
st.header("Dataset A: Wisconsin Breast Cancer Diagnostic (WBCD)")
try:
    wbcd = load_wbcd()
    st.success(f"Loaded — {wbcd.shape[0]} rows × {wbcd.shape[1]} columns")
    st.write("**Columns:**", wbcd.columns.tolist())
    st.dataframe(wbcd.head())
except Exception as e:
    st.error(f"Failed to load WBCD: {e}")

st.divider()

# ── METABRIC ──────────────────────────────────────────────────────────────────
st.header("Dataset B: METABRIC")
try:
    metabric = load_metabric()
    st.success(f"Loaded — {metabric.shape[0]} rows × {metabric.shape[1]} columns")
    st.write("**Columns:**", metabric.columns.tolist())
    st.dataframe(metabric.head())
except Exception as e:
    st.error(f"Failed to load METABRIC: {e}")
