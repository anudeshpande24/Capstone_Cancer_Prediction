import streamlit as st
import requests
from utils.theme import inject_theme

st.set_page_config(page_title="Diagnosis", page_icon="🔬", layout="wide")
inject_theme()

API = "http://localhost:8000"

st.title("Tumor Diagnosis")
st.caption(
    "Predicts whether a breast mass is **Benign** or **Malignant** using cell nucleus "
    "measurements from a fine needle aspirate (FNA). Powered by a Calibrated Random Forest."
)
st.divider()


@st.cache_data
def get_schema():
    return requests.get(f"{API}/predict/diagnosis/schema", timeout=10).json()


try:
    schema = get_schema()
except Exception as e:
    st.error(f"Could not load schema from API: {e}")
    st.stop()

features = schema["features"]
stats = schema["stats"]

# Group features into mean / se / worst sections
mean_feats = [f for f in features if f.endswith("_mean")]
se_feats = [f for f in features if f.endswith("_se")]
worst_feats = [f for f in features if f.endswith("_worst")]

inputs = {}

with st.form("diagnosis_form"):
    st.markdown("### Cell Nucleus Measurements")

    with st.expander("Mean values", expanded=True):
        cols = st.columns(3)
        for i, f in enumerate(mean_feats):
            s = stats[f]
            inputs[f] = cols[i % 3].number_input(
                f, min_value=float(s["min"]), max_value=float(s["max"]),
                value=float(s["mean"]), format="%.5f", key=f,
            )

    with st.expander("Standard error values"):
        cols = st.columns(3)
        for i, f in enumerate(se_feats):
            s = stats[f]
            inputs[f] = cols[i % 3].number_input(
                f, min_value=float(s["min"]), max_value=float(s["max"]),
                value=float(s["mean"]), format="%.5f", key=f,
            )

    with st.expander("Worst values"):
        cols = st.columns(3)
        for i, f in enumerate(worst_feats):
            s = stats[f]
            inputs[f] = cols[i % 3].number_input(
                f, min_value=float(s["min"]), max_value=float(s["max"]),
                value=float(s["mean"]), format="%.5f", key=f,
            )

    submitted = st.form_submit_button("Run Diagnosis", use_container_width=True)

if submitted:
    with st.spinner("Running model..."):
        try:
            resp = requests.post(
                f"{API}/predict/diagnosis", json={"features": inputs}, timeout=15
            )
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            st.error(f"Prediction failed: {e}")
            st.stop()

    label = result["label"]
    p_mal = result["probability_malignant"]
    p_ben = result["probability_benign"]
    css_class = "result-malignant" if label == "Malignant" else "result-benign"

    st.divider()
    st.markdown("### Result")
    st.markdown(
        f'<div class="result-box {css_class}">Prediction: {label}</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    col1.metric("Malignant probability", f"{p_mal:.1%}")
    col2.metric("Benign probability", f"{p_ben:.1%}")
