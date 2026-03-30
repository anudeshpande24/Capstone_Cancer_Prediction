import streamlit as st
import requests
from utils.data_loader import load_wbcd, load_metabric, api_health
from utils.theme import inject_theme

st.set_page_config(page_title="BreastCare Decision Support", page_icon="🩺", layout="wide")
inject_theme()

API = "http://localhost:8000"

NAV_ITEMS = [
    ("📊", "Data Overview"),
    ("🔬", "Diagnosis"),
    ("📈", "Risk Stratification"),
    ("📉", "Survival Analysis"),
    ("📐", "Model Metrics"),
]

if "page" not in st.session_state:
    st.session_state.page = "Data Overview"

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="sidebar-brand-icon">🩺</div>'
        '<div>'
        '<div class="sidebar-brand-name">BreastCare</div>'
        '<div class="sidebar-brand-sub">Decision Support</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-nav-label">MENU</div>', unsafe_allow_html=True)
    for icon, label in NAV_ITEMS:
        active = st.session_state.page == label
        # Highlight active item with a distinct background via injected CSS targeting the next button
        if active:
            st.markdown(
                '<style>'
                '[data-testid="stSidebar"] .stButton:last-of-type button {'
                '  background: linear-gradient(135deg,#e91e63,#c2185b) !important;'
                '  color:#fff !important; font-weight:700 !important;'
                '  box-shadow: 0 4px 14px rgba(233,30,99,0.45) !important;'
                '}</style>',
                unsafe_allow_html=True,
            )
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label
            st.rerun()
    st.markdown('<div class="sidebar-footer">Capstone Project · DS 2026</div>', unsafe_allow_html=True)

page = st.session_state.page

st.markdown('<p class="main-title">BreastCare Decision Support</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Interpretable prediction platform supporting clinical decision-making in breast cancer treatment planning</p>', unsafe_allow_html=True)

if api_health():
    st.markdown('<span class="status-ok">● API Connected</span>', unsafe_allow_html=True)
else:
    st.error("Cannot reach API. Run: uvicorn backend.main:app --reload --port 8000")

st.divider()

# ── Schema loaders (top-level so caching works correctly) ─────────────────────
@st.cache_data
def get_diagnosis_schema():
    return requests.get(f"{API}/predict/diagnosis/schema", timeout=10).json()

@st.cache_data
def get_risk_schema():
    return requests.get(f"{API}/predict/risk/schema", timeout=10).json()

@st.cache_data
def get_survival_schema():
    return requests.get(f"{API}/predict/survival/schema", timeout=10).json()

# ── Data Overview ─────────────────────────────────────────────────────────────
if page == "Data Overview":
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

# ── Diagnosis ─────────────────────────────────────────────────────────────────
elif page == "Diagnosis":
    st.markdown("### Tumor Diagnosis")
    st.caption("Predicts whether a breast mass is **Benign** or **Malignant** using cell nucleus measurements. Powered by a Calibrated Random Forest.")
    try:
        schema_a = get_diagnosis_schema()
        features_a = schema_a["features"]
        stats_a = schema_a["stats"]
        mean_feats = [f for f in features_a if f.endswith("_mean")]
        se_feats   = [f for f in features_a if f.endswith("_se")]
        worst_feats = [f for f in features_a if f.endswith("_worst")]
        inputs_a = {}
        with st.form("diagnosis_form"):
            with st.expander("Mean values", expanded=True):
                cols = st.columns(3)
                for i, f in enumerate(mean_feats):
                    s = stats_a[f]
                    inputs_a[f] = cols[i % 3].number_input(f, min_value=float(s["min"]), max_value=float(s["max"]), value=float(s["mean"]), format="%.5f", key=f"a_{f}")
            with st.expander("Standard error values"):
                cols = st.columns(3)
                for i, f in enumerate(se_feats):
                    s = stats_a[f]
                    inputs_a[f] = cols[i % 3].number_input(f, min_value=float(s["min"]), max_value=float(s["max"]), value=float(s["mean"]), format="%.5f", key=f"a_{f}")
            with st.expander("Worst values"):
                cols = st.columns(3)
                for i, f in enumerate(worst_feats):
                    s = stats_a[f]
                    inputs_a[f] = cols[i % 3].number_input(f, min_value=float(s["min"]), max_value=float(s["max"]), value=float(s["mean"]), format="%.5f", key=f"a_{f}")
            submitted_a = st.form_submit_button("Run Diagnosis", use_container_width=True)
        if submitted_a:
            with st.spinner("Running model..."):
                resp = requests.post(f"{API}/predict/diagnosis", json={"features": inputs_a}, timeout=15)
                resp.raise_for_status()
                r = resp.json()
            label_a = r["label"]
            css = "result-malignant" if label_a == "Malignant" else "result-benign"
            st.markdown(f'<div class="result-box {css}">Prediction: {label_a}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.metric("Malignant probability", f"{r['probability_malignant']:.1%}")
            c2.metric("Benign probability",    f"{r['probability_benign']:.1%}")
    except Exception as e:
        st.error(f"Diagnosis model unavailable: {e}")

# ── Risk Stratification ───────────────────────────────────────────────────────
elif page == "Risk Stratification":
    st.markdown("### Risk Stratification")
    st.caption("Stratifies a patient into **Low**, **Medium**, or **High** risk. Powered by XGBoost trained on METABRIC.")
    try:
        schema_b = get_risk_schema()
        num_stats_b  = schema_b["num_stats"]
        cat_opts_b   = schema_b["cat_options"]
        KEY_NUM_B = ["Age at Diagnosis", "Tumor Size", "Tumor Stage", "Neoplasm Histologic Grade",
                     "Lymph nodes examined positive", "Nottingham prognostic index", "Mutation Count"]
        KEY_CAT_B = ["Type of Breast Surgery", "Cancer Type Detailed", "ER Status", "HER2 Status",
                     "PR Status", "Cellularity", "Chemotherapy", "Hormone Therapy", "Radio Therapy",
                     "Pam50 + Claudin-low subtype"]
        inputs_b = {}
        with st.form("risk_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Numeric features**")
                for f in KEY_NUM_B:
                    if f in num_stats_b:
                        s = num_stats_b[f]
                        inputs_b[f] = st.slider(f, min_value=float(s["min"]), max_value=float(s["max"]), value=float(s["median"]), key=f"b_{f}")
            with col2:
                st.markdown("**Categorical features**")
                for f in KEY_CAT_B:
                    if f in cat_opts_b:
                        inputs_b[f] = st.selectbox(f, options=cat_opts_b[f], key=f"b_{f}")
            submitted_b = st.form_submit_button("Run Risk Stratification", use_container_width=True)
        if submitted_b:
            with st.spinner("Running model..."):
                resp = requests.post(f"{API}/predict/risk", json={"features": inputs_b}, timeout=15)
                resp.raise_for_status()
                r = resp.json()
            label_b = r["label"]
            css = f"result-{label_b.lower()}"
            st.markdown(f'<div class="result-box {css}">Risk Level: {label_b}</div>', unsafe_allow_html=True)
            cols = st.columns(3)
            for i, (risk, prob) in enumerate(r["probabilities"].items()):
                cols[i].metric(f"{risk} Risk", f"{prob:.1%}")
    except Exception as e:
        st.error(f"Risk model unavailable: {e}")

# ── Survival Analysis ─────────────────────────────────────────────────────────
elif page == "Survival Analysis":
    st.markdown("### Survival Analysis")
    st.caption("Estimates **Overall Survival** and **Relapse-Free Survival** at 12, 24, and 36 months. Powered by Cox Proportional Hazards.")
    try:
        schema_c    = get_survival_schema()
        cat_opts_c  = schema_c["cat_options"]
        defaults_c  = schema_c["defaults"]
        KEY_CAT_C = ["Type of Breast Surgery", "Cancer Type Detailed", "ER Status", "HER2 Status",
                     "PR Status", "Cellularity", "Chemotherapy", "Hormone Therapy", "Radio Therapy",
                     "Pam50 + Claudin-low subtype", "Inferred Menopausal State"]
        KEY_NUM_C = {
            "Age at Diagnosis": (20.0, 100.0), "Tumor Size": (1.0, 200.0),
            "Tumor Stage": (1.0, 4.0), "Neoplasm Histologic Grade": (1.0, 3.0),
            "Lymph nodes examined positive": (0.0, 30.0),
            "Nottingham prognostic index": (1.0, 7.0), "Mutation Count": (0.0, 300.0),
        }
        inputs_c = {}
        with st.form("survival_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Numeric features**")
                for f, (lo, hi) in KEY_NUM_C.items():
                    inputs_c[f] = st.slider(f, min_value=lo, max_value=hi, value=float(defaults_c.get(f, (lo + hi) / 2)), key=f"c_{f}")
            with col2:
                st.markdown("**Categorical features**")
                for f in KEY_CAT_C:
                    if f in cat_opts_c:
                        opts = cat_opts_c[f]
                        default_idx = min(int(defaults_c.get(f, 0)), len(opts) - 1)
                        inputs_c[f] = st.selectbox(f, options=opts, index=default_idx, key=f"c_{f}")
            submitted_c = st.form_submit_button("Run Survival Analysis", use_container_width=True)
        if submitted_c:
            with st.spinner("Running model..."):
                resp = requests.post(f"{API}/predict/survival", json={"features": inputs_c}, timeout=15)
                resp.raise_for_status()
                r = resp.json()
            col_os, col_rfs = st.columns(2)
            with col_os:
                st.markdown("#### Overall Survival")
                for months, prob in r["overall_survival"].items():
                    st.metric(f"At {months} months", f"{prob:.1%}")
            with col_rfs:
                st.markdown("#### Relapse-Free Survival")
                for months, prob in r["relapse_free_survival"].items():
                    st.metric(f"At {months} months", f"{prob:.1%}")
            st.info("C-index reference: OS = 0.658 · RFS = 0.636")
    except Exception as e:
        st.error(f"Survival model unavailable: {e}")
