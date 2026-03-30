PINK_CSS = """
<style>
    /* ─── Global ─────────────────────────────────────────────────────────────── */
    .stApp {
        background: linear-gradient(160deg, #fdf2f6 0%, #fce9f1 60%, #f9dcea 100%);
        min-height: 100vh;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1150px;
    }

    /* ─── Hide Streamlit chrome ──────────────────────────────────────────────── */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }

    /* ─── Sidebar shell ──────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d0012 0%, #4a0020 60%, #6b0f35 100%) !important;
        border-right: none !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 0 !important;
    }

    /* ─── Brand block ────────────────────────────────────────────────────────── */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 28px 20px 22px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 8px;
    }
    .sidebar-brand-icon {
        font-size: 1.9rem;
        line-height: 1;
    }
    .sidebar-brand-name {
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffffff !important;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .sidebar-brand-sub {
        font-size: 0.73rem;
        color: rgba(255,255,255,0.55) !important;
        font-weight: 400;
        letter-spacing: 0.04em;
        margin-top: 2px;
    }

    /* ─── Nav section label ──────────────────────────────────────────────────── */
    .sidebar-nav-label {
        font-size: 0.65rem;
        font-weight: 700;
        color: rgba(255,255,255,0.4) !important;
        letter-spacing: 0.12em;
        padding: 0 20px 6px 20px;
        margin-top: 4px;
    }

    /* ─── Nav buttons — override Streamlit button defaults ──────────────────── */
    [data-testid="stSidebar"] .stButton button {
        background: transparent !important;
        color: rgba(255,255,255,0.72) !important;
        border: none !important;
        border-radius: 10px !important;
        font-size: 0.93rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 11px 16px !important;
        margin: 1px 12px !important;
        width: calc(100% - 24px) !important;
        box-shadow: none !important;
        transition: background 0.15s ease, color 0.15s ease !important;
        letter-spacing: 0.01em !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* ─── Active nav button ──────────────────────────────────────────────────── */
    [data-testid="stSidebar"] .stButton button[kind="primary"],
    [data-testid="stSidebar"] .nav-active button {
        background: linear-gradient(135deg, #e91e63, #c2185b) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(233,30,99,0.4) !important;
        font-weight: 700 !important;
    }

    /* ─── Sidebar footer ─────────────────────────────────────────────────────── */
    .sidebar-footer {
        position: absolute;
        bottom: 24px;
        left: 0; right: 0;
        text-align: center;
        font-size: 0.72rem;
        color: rgba(255,255,255,0.3) !important;
        letter-spacing: 0.04em;
    }

    /* ─── Page title ─────────────────────────────────────────────────────────── */
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #880e4f 0%, #e91e63 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.15rem;
        line-height: 1.15;
        letter-spacing: -0.03em;
    }
    .main-subtitle {
        font-size: 1rem;
        color: #6b3352 !important;
        margin-top: 0.4rem;
        margin-bottom: 1.2rem;
        font-weight: 400;
        line-height: 1.6;
    }

    /* ─── Headings ───────────────────────────────────────────────────────────── */
    h1, h2, h3, h4, h5, h6 {
        color: #880e4f !important;
        letter-spacing: -0.02em;
    }

    /* ─── Body text ──────────────────────────────────────────────────────────── */
    p, li, div, small,
    .stMarkdown, .stText { color: #2d0012 !important; }

    /* ─── Captions ───────────────────────────────────────────────────────────── */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: #6b3352 !important;
        font-style: italic;
    }

    /* ─── Section header banner ──────────────────────────────────────────────── */
    .section-header {
        background: linear-gradient(135deg, #880e4f 0%, #c2185b 60%, #e91e63 100%);
        border-radius: 16px;
        padding: 22px 28px;
        margin-bottom: 22px;
        box-shadow: 0 6px 24px rgba(136, 14, 79, 0.22);
    }
    .section-header h3 {
        color: #ffffff !important;
        margin: 0 0 5px 0;
        font-size: 1.45rem;
        font-weight: 700;
        -webkit-text-fill-color: #ffffff !important;
    }
    .section-header p {
        color: rgba(255,255,255,0.82) !important;
        margin: 0;
        font-size: 0.93rem;
        -webkit-text-fill-color: rgba(255,255,255,0.82) !important;
    }

    /* ─── Model metric header strip ──────────────────────────────────────────── */
    .model-header {
        background: #ffffff;
        border: 1.5px solid #fce4ec;
        border-left: 4px solid #e91e63;
        border-radius: 0 12px 12px 0;
        padding: 14px 20px;
        margin: 24px 0 16px 0;
        box-shadow: 0 2px 10px rgba(136,14,79,0.07);
    }
    .model-header h4 {
        color: #880e4f !important;
        margin: 0 0 3px 0;
        font-size: 1.05rem;
        font-weight: 700;
    }
    .model-header p {
        color: #6b3352 !important;
        margin: 0;
        font-size: 0.84rem;
    }

    /* ─── Form labels ────────────────────────────────────────────────────────── */
    label,
    .stSlider label,
    .stSelectbox label,
    .stNumberInput label,
    .stTextInput label,
    .stRadio label,
    .stCheckbox label,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p {
        color: #2d0012 !important;
        font-weight: 500;
        font-size: 0.87rem !important;
    }

    /* ─── Selectbox ──────────────────────────────────────────────────────────── */
    [data-baseweb="select"] > div:first-child {
        background-color: #ffffff !important;
        border: 1.5px solid #f48fb1 !important;
        border-radius: 10px !important;
        box-shadow: 0 1px 4px rgba(136,14,79,0.07) !important;
    }
    [data-baseweb="select"] span,
    [data-baseweb="select"] div { color: #2d0012 !important; }
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"],
    ul[data-baseweb="menu"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 24px rgba(136,14,79,0.12) !important;
    }
    [data-baseweb="menu"] li,
    [role="option"] { background-color: #ffffff !important; color: #2d0012 !important; }
    [data-baseweb="menu"] li:hover,
    [role="option"]:hover,
    [aria-selected="true"] { background-color: #fce4ec !important; color: #880e4f !important; }

    /* ─── Number inputs ──────────────────────────────────────────────────────── */
    [data-baseweb="input"],
    [data-baseweb="base-input"],
    [data-baseweb="input"] input,
    [data-baseweb="base-input"] input,
    .stNumberInput input,
    .stTextInput input,
    input[type="number"] {
        background-color: #ffffff !important;
        color: #2d0012 !important;
        border: 1.5px solid #f48fb1 !important;
        border-radius: 10px !important;
    }

    /* ─── Slider ─────────────────────────────────────────────────────────────── */
    [data-testid="stSlider"] p,
    [data-testid="stSlider"] span { color: #2d0012 !important; }

    /* ─── Expander ───────────────────────────────────────────────────────────── */
    [data-testid="stExpander"] {
        border: 1.5px solid #fce4ec !important;
        border-radius: 14px !important;
        background: #ffffff !important;
        overflow: hidden !important;
        box-shadow: 0 2px 10px rgba(136,14,79,0.07) !important;
        margin-bottom: 10px !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    .streamlit-expanderHeader {
        color: #880e4f !important;
        font-weight: 600;
        background: #fff9fb !important;
        padding: 14px 18px !important;
    }

    /* ─── Strong text ────────────────────────────────────────────────────────── */
    .stMarkdown strong { color: #880e4f !important; font-weight: 700; }

    /* ─── Alert / Info ───────────────────────────────────────────────────────── */
    [data-testid="stInfo"] {
        background: #fff0f8 !important;
        border: 1.5px solid #f48fb1 !important;
        border-radius: 12px !important;
    }
    [data-testid="stInfo"] p { color: #880e4f !important; }
    [data-testid="stAlert"] p { color: #2d0012 !important; }

    /* ─── Metric cards ───────────────────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1.5px solid #fce4ec;
        border-radius: 16px;
        padding: 18px 22px;
        box-shadow: 0 3px 14px rgba(136,14,79,0.08);
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: 0 6px 22px rgba(136,14,79,0.15);
        transform: translateY(-1px);
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: #6b3352 !important;
        font-weight: 600;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    [data-testid="stMetricValue"] {
        color: #880e4f !important;
        font-weight: 800;
        font-size: 1.75rem !important;
        letter-spacing: -0.02em;
    }

    /* ─── Dataframe ──────────────────────────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border: 1.5px solid #fce4ec !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 10px rgba(136,14,79,0.06) !important;
    }

    /* ─── Main content buttons ───────────────────────────────────────────────── */
    .main .stFormSubmitButton button,
    .main .stButton button {
        background: linear-gradient(135deg, #c2185b 0%, #e91e63 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border-radius: 12px !important;
        letter-spacing: 0.02em !important;
        padding: 0.65rem 1.5rem !important;
        box-shadow: 0 4px 16px rgba(233,30,99,0.35) !important;
        transition: all 0.2s ease !important;
    }
    .main .stFormSubmitButton button:hover,
    .main .stButton button:hover {
        background: linear-gradient(135deg, #880e4f 0%, #c2185b 100%) !important;
        box-shadow: 0 6px 22px rgba(136,14,79,0.45) !important;
        transform: translateY(-1px) !important;
        color: #ffffff !important;
    }

    /* ─── Divider ────────────────────────────────────────────────────────────── */
    hr {
        border: none !important;
        border-top: 1.5px solid #f8bbd0 !important;
        margin: 1.5rem 0 !important;
    }

    /* ─── API status badge ───────────────────────────────────────────────────── */
    .status-ok {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, #fce4ec, #fff0f6);
        border: 1.5px solid #f48fb1;
        border-radius: 20px;
        padding: 5px 16px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: #880e4f !important;
        -webkit-text-fill-color: #880e4f !important;
    }

    /* ─── Result boxes ───────────────────────────────────────────────────────── */
    .result-box {
        border-radius: 16px;
        padding: 20px 26px;
        margin: 16px 0;
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: 0.01em;
    }
    .result-malignant {
        background: linear-gradient(135deg, #fce4ec, #ffd0e4);
        border: 2px solid #e91e63;
        color: #880e4f !important;
        box-shadow: 0 4px 18px rgba(233,30,99,0.18);
    }
    .result-benign {
        background: linear-gradient(135deg, #e8f5e9, #d5f0d5);
        border: 2px solid #43a047;
        color: #1b5e20 !important;
        box-shadow: 0 4px 18px rgba(67,160,71,0.18);
    }
    .result-high {
        background: linear-gradient(135deg, #fce4ec, #ffd0e4);
        border: 2px solid #e91e63;
        color: #880e4f !important;
        box-shadow: 0 4px 18px rgba(233,30,99,0.18);
    }
    .result-medium {
        background: linear-gradient(135deg, #fff8e1, #ffefc7);
        border: 2px solid #fb8c00;
        color: #4a3000 !important;
        box-shadow: 0 4px 18px rgba(251,140,0,0.18);
    }
    .result-low {
        background: linear-gradient(135deg, #e8f5e9, #d5f0d5);
        border: 2px solid #43a047;
        color: #1b5e20 !important;
        box-shadow: 0 4px 18px rgba(67,160,71,0.18);
    }
</style>
"""


def inject_theme():
    import streamlit as st
    st.markdown(PINK_CSS, unsafe_allow_html=True)
