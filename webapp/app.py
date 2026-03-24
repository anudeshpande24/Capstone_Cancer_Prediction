import streamlit as st
from utils.data_loader import load_wbcd, load_metabric, api_health

st.set_page_config(
    page_title="BreastCare AI",
    page_icon="🩺",
    layout="wide",
)

# ── Theme ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #fff0f4; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #fce4ec; }
    [data-testid="stSidebar"] * { color: #4a0020 !important; }
    [data-testid="stSidebar"] h2 { color: #880e4f !important; font-weight: 700; }
    [data-testid="stSidebar"] small { color: #6d1a3a !important; }

    /* Main title */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #880e4f;
        margin-bottom: 0;
        line-height: 1.2;
    }
    .main-subtitle {
        font-size: 1.05rem;
        color: #4a0020;
        margin-top: 0.4rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }

    /* Section headers */
    h2, h3 { color: #880e4f !important; }

    /* Body text */
    p, li, span, label { color: #2d0012; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #f48fb1;
        border-radius: 10px;
        padding: 12px 16px;
    }
    [data-testid="stMetricLabel"] { color: #4a0020 !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #880e4f !important; font-weight: 700; }

    /* Dataframe */
    [data-testid="stDataFrame"] { border: 1px solid #f48fb1; border-radius: 8px; }

    /* Divider */
    hr { border-color: #f48fb1; }

    /* Status badge */
    .status-ok {
        display: inline-block;
        background: #fce4ec;
        color: #4a0020;
        border: 1px solid #f48fb1;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.divider()
    st.markdown("**Navigation**")
    st.markdown("- Data Overview ← you are here")
    st.markdown("- [Diagnosis](Diagnosis)")
    st.markdown("- [Risk Stratification](Risk_Stratification)")
    st.markdown("- [Survival Analysis](Survival_Analysis)")
    st.divider()
    st.markdown("<small>Capstone Project · DS 2026</small>", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">Breast Cancer Risk Modeling and Clinical Decision Support</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="main-subtitle">Interpretable prediction platform supporting clinical decision-making in breast cancer treatment planning</p>',
    unsafe_allow_html=True,
)

# ── API health check ──────────────────────────────────────────────────────────
api_ok = api_health()
if api_ok:
    st.markdown('<span class="status-ok">● API Connected</span>', unsafe_allow_html=True)
else:
    st.error("Cannot reach API. Run: uvicorn backend.main:app --reload --port 8000")
    st.stop()

st.divider()

# ── Dataset cards ─────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2, gap="large")

with col_a:
    st.markdown("### Dataset A — WBCD")
    st.caption("Wisconsin Breast Cancer Diagnostic · Binary classification")
    try:
        wbcd = load_wbcd()
        m1, m2 = st.columns(2)
        m1.metric("Patients", f"{wbcd.shape[0]:,}")
        m2.metric("Features", wbcd.shape[1])
        st.dataframe(wbcd.head(5), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Failed to load WBCD: {e}")

with col_b:
    st.markdown("### Dataset B — METABRIC")
    st.caption("Molecular Taxonomy of Breast Cancer · Risk & survival")
    try:
        metabric = load_metabric()
        m1, m2 = st.columns(2)
        m1.metric("Patients", f"{metabric.shape[0]:,}")
        m2.metric("Features", metabric.shape[1])
        st.dataframe(metabric.head(5), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Failed to load METABRIC: {e}")
