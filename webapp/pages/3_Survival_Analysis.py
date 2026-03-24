import streamlit as st
import requests
from utils.theme import inject_theme

st.set_page_config(page_title="Survival Analysis", page_icon="📈", layout="wide")
inject_theme()

API = "http://localhost:8000"

st.title("Survival Analysis")
st.caption(
    "Estimates **Overall Survival** and **Relapse-Free Survival** probabilities at "
    "12, 24, and 36 months using a Cox Proportional Hazards model trained on METABRIC."
)
st.divider()


@st.cache_data
def get_schema():
    return requests.get(f"{API}/predict/survival/schema", timeout=10).json()


try:
    schema = get_schema()
except Exception as e:
    st.error(f"Could not load schema from API: {e}")
    st.stop()

cat_options = schema["cat_options"]
defaults = schema["defaults"]

# Key clinical inputs to surface
KEY_CAT = ["Type of Breast Surgery", "Cancer Type Detailed", "ER Status", "HER2 Status",
           "PR Status", "Cellularity", "Chemotherapy", "Hormone Therapy", "Radio Therapy",
           "Pam50 + Claudin-low subtype", "Inferred Menopausal State"]
KEY_NUM = {
    "Age at Diagnosis": (20.0, 100.0),
    "Tumor Size": (1.0, 200.0),
    "Tumor Stage": (1.0, 4.0),
    "Neoplasm Histologic Grade": (1.0, 3.0),
    "Lymph nodes examined positive": (0.0, 30.0),
    "Nottingham prognostic index": (1.0, 7.0),
    "Mutation Count": (0.0, 300.0),
}

inputs = {}

with st.form("survival_form"):
    st.markdown("### Patient Clinical Profile")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Numeric**")
        for f, (lo, hi) in KEY_NUM.items():
            inputs[f] = st.slider(
                f,
                min_value=lo,
                max_value=hi,
                value=float(defaults.get(f, (lo + hi) / 2)),
                key=f"num_{f}",
            )

    with col2:
        st.markdown("**Categorical**")
        for f in KEY_CAT:
            if f in cat_options:
                opts = cat_options[f]
                default_encoded = defaults.get(f, 0)
                default_idx = min(int(default_encoded), len(opts) - 1)
                inputs[f] = st.selectbox(f, options=opts, index=default_idx, key=f"cat_{f}")

    submitted = st.form_submit_button("Run Survival Analysis", use_container_width=True)

if submitted:
    with st.spinner("Running model..."):
        try:
            resp = requests.post(
                f"{API}/predict/survival", json={"features": inputs}, timeout=15
            )
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            st.error(f"Prediction failed: {e}")
            st.stop()

    os_probs = result["overall_survival"]
    rfs_probs = result["relapse_free_survival"]

    st.divider()
    st.markdown("### Results")

    col_os, col_rfs = st.columns(2)

    with col_os:
        st.markdown("#### Overall Survival")
        for months, prob in os_probs.items():
            st.metric(f"At {months} months", f"{prob:.1%}")

    with col_rfs:
        st.markdown("#### Relapse-Free Survival")
        for months, prob in rfs_probs.items():
            st.metric(f"At {months} months", f"{prob:.1%}")

    st.info(
        "**C-index reference:** OS = 0.658 · RFS = 0.636 — "
        "these scores reflect moderate discrimination typical of clinical-only survival models."
    )
