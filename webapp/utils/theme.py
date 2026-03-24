PINK_CSS = """
<style>
    .stApp { background-color: #fff0f4; }
    [data-testid="stSidebar"] { background-color: #fce4ec; }
    [data-testid="stSidebar"] * { color: #4a0020 !important; }
    h1, h2, h3 { color: #880e4f !important; }
    p, li, span, label { color: #2d0012; }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #f48fb1;
        border-radius: 10px;
        padding: 12px 16px;
    }
    [data-testid="stMetricLabel"] { color: #4a0020 !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #880e4f !important; font-weight: 700; }
    hr { border-color: #f48fb1; }
    .result-box {
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 16px;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .result-malignant { background: #fce4ec; border: 2px solid #e91e63; color: #880e4f; }
    .result-benign    { background: #e8f5e9; border: 2px solid #4caf50; color: #1b5e20; }
    .result-high      { background: #fce4ec; border: 2px solid #e91e63; color: #880e4f; }
    .result-medium    { background: #fff8e1; border: 2px solid #ffc107; color: #5d4037; }
    .result-low       { background: #e8f5e9; border: 2px solid #4caf50; color: #1b5e20; }
</style>
"""


def inject_theme():
    import streamlit as st
    st.markdown(PINK_CSS, unsafe_allow_html=True)
