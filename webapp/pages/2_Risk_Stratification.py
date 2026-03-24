import streamlit as st
import requests
from utils.theme import inject_theme

st.set_page_config(page_title="Risk Stratification", page_icon="📊", layout="wide")
inject_theme()

API = "http://localhost:8000"

st.title("Risk Stratification")
st.caption(
    "Stratifies a patient into **Low**, **Medium**, or **High** risk based on clinical and "
    "molecular features. Powered by XGBoost trained on METABRIC."
)
st.divider()


@st.cache_data
def get_schema():
    return requests.get(f"{API}/predict/risk/schema", timeout=10).json()


try:
    schema = get_schema()
except Exception as e:
    st.error(f"Could not load schema from API: {e}")
    st.stop()

num_stats = schema["num_stats"]
cat_options = schema["cat_options"]

# Key clinical fields to surface in the UI
KEY_NUM = ["Age at Diagnosis", "Tumor Size", "Tumor Stage", "Neoplasm Histologic Grade",
           "Lymph nodes examined positive", "Nottingham prognostic index", "Mutation Count"]
KEY_CAT = ["Type of Breast Surgery", "Cancer Type Detailed", "ER Status", "HER2 Status",
           "PR Status", "Cellularity", "Chemotherapy", "Hormone Therapy", "Radio Therapy",
           "Pam50 + Claudin-low subtype"]

inputs = {}

with st.form("risk_form"):
    st.markdown("### Clinical Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Numeric**")
        for f in KEY_NUM:
            if f in num_stats:
                s = num_stats[f]
                inputs[f] = st.slider(
                    f,
                    min_value=float(s["min"]),
                    max_value=float(s["max"]),
                    value=float(s["median"]),
                    key=f"num_{f}",
                )

    with col2:
        st.markdown("**Categorical**")
        for f in KEY_CAT:
            if f in cat_options:
                opts = cat_options[f]
                inputs[f] = st.selectbox(f, options=opts, key=f"cat_{f}")

    submitted = st.form_submit_button("Run Risk Stratification", use_container_width=True)

if submitted:
    with st.spinner("Running model..."):
        try:
            resp = requests.post(
                f"{API}/predict/risk", json={"features": inputs}, timeout=15
            )
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            st.error(f"Prediction failed: {e}")
            st.stop()

    label = result["label"]
    probs = result["probabilities"]
    css_class = f"result-{label.lower()}"

    st.divider()
    st.markdown("### Result")
    st.markdown(
        f'<div class="result-box {css_class}">Risk Level: {label}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Probability breakdown")
    cols = st.columns(3)
    for i, (risk, prob) in enumerate(probs.items()):
        cols[i].metric(f"{risk} Risk", f"{prob:.1%}")
