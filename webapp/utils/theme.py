CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base ─────────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
}
.stApp {
    background-color: #0d1b3e !important;
}
.main .block-container {
    padding: 2rem 2.5rem 4rem 2.5rem !important;
    max-width: 1280px;
}
#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0a1530 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.6) !important; }

.sb-brand {
    padding: 28px 22px 22px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 10px;
}
.sb-brand-name {
    font-size: 1.3rem; font-weight: 800; letter-spacing: -0.02em;
    color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
}
.sb-brand-sub {
    font-size: 0.71rem; font-weight: 400; letter-spacing: 0.03em;
    color: rgba(255,255,255,0.3) !important; margin-top: 3px;
}

.sb-section {
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: rgba(255,255,255,0.25) !important;
    padding: 16px 22px 8px;
}

[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    color: rgba(255,255,255,0.45) !important;
    -webkit-text-fill-color: rgba(255,255,255,0.45) !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.84rem !important;
    font-weight: 400 !important;
    text-align: left !important;
    padding: 9px 14px !important;
    margin: 1px 10px !important;
    width: calc(100% - 20px) !important;
    box-shadow: none !important;
    transition: background 0.15s, color 0.15s !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.05) !important;
    color: rgba(255,255,255,0.85) !important;
    -webkit-text-fill-color: rgba(255,255,255,0.85) !important;
    box-shadow: none !important;
    transform: none !important;
}

.nav-item-active {
    display: flex;
    align-items: center;
    gap: 9px;
    background: rgba(244,63,122,0.13) !important;
    color: #f9a8c9 !important;
    -webkit-text-fill-color: #f9a8c9 !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    padding: 9px 14px 9px 11px !important;
    margin: 1px 10px !important;
    border-left: 3px solid #f43f7a !important;
    border-radius: 0 8px 8px 0 !important;
    letter-spacing: 0.01em !important;
    box-sizing: border-box !important;
}
.nav-item-active svg { flex-shrink: 0; opacity: 0.9; }
.nav-item-active span { color: #f9a8c9 !important; -webkit-text-fill-color: #f9a8c9 !important; }

.sb-footer {
    position: absolute; bottom: 24px; left: 0; right: 0;
    text-align: center; font-size: 0.67rem;
    color: rgba(255,255,255,0.15) !important; letter-spacing: 0.04em;
}

/* ── Page chrome ──────────────────────────────────────────────────────────── */
.page-eyebrow {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #f43f7a !important;
    -webkit-text-fill-color: #f43f7a !important; margin-bottom: 5px;
}
.page-title {
    font-size: 1.75rem; font-weight: 800; letter-spacing: -0.03em;
    color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
    margin: 0 0 5px; line-height: 1.15;
}
.page-sub {
    font-size: 0.875rem; color: rgba(255,255,255,0.45) !important;
    font-weight: 400; line-height: 1.6; margin: 0;
}

/* ── Status pill ──────────────────────────────────────────────────────────── */
.status-ok {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.75rem; font-weight: 600;
    color: #4ade80 !important; -webkit-text-fill-color: #4ade80 !important;
}

/* ── Divider ──────────────────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.07) !important;
    margin: 1.2rem 0 !important;
}

/* ── Stat cards (overview row) ────────────────────────────────────────────── */
.stat-card {
    background: #112052;
    border-radius: 16px;
    padding: 20px 22px;
    border: 1px solid rgba(255,255,255,0.07);
    display: flex; align-items: center; gap: 16px;
    animation: fadeUp 0.4s ease;
}
.stat-card-icon {
    width: 46px; height: 46px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; flex-shrink: 0;
}
.stat-card-value {
    font-size: 1.65rem; font-weight: 800; color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important; letter-spacing: -0.03em;
    line-height: 1;
}
.stat-card-label {
    font-size: 0.72rem; font-weight: 500; letter-spacing: 0.03em;
    color: rgba(255,255,255,0.45) !important; margin-top: 3px;
}

/* ── Section heading ──────────────────────────────────────────────────────── */
.section-heading {
    font-size: 1.05rem; font-weight: 700; color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    letter-spacing: -0.02em; margin: 0 0 16px;
}

/* ── Content card ─────────────────────────────────────────────────────────── */
.content-card {
    background: #112052;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.07);
    padding: 26px;
    animation: fadeUp 0.35s ease;
}

/* ── Page banner ──────────────────────────────────────────────────────────── */
.page-banner {
    background: #112052;
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 4px solid #f43f7a;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 28px;
    animation: fadeUp 0.4s ease;
}
.page-banner h3 {
    color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
    font-size: 1.05rem; font-weight: 700; margin: 0 0 4px; letter-spacing: -0.02em;
}
.page-banner p {
    color: rgba(255,255,255,0.5) !important;
    -webkit-text-fill-color: rgba(255,255,255,0.5) !important;
    font-size: 0.875rem; margin: 0; line-height: 1.6;
}
.page-banner strong { color: #f9a8c9 !important; -webkit-text-fill-color: #f9a8c9 !important; }
.page-banner code {
    background: rgba(244,63,122,0.15) !important;
    color: #f9a8c9 !important; padding: 1px 6px; border-radius: 4px; font-size: 0.82rem;
}

/* ── Metric cards ─────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #112052 !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    padding: 20px 22px !important;
    box-shadow: none !important;
    transition: transform 0.2s ease, border-color 0.2s ease !important;
    animation: fadeUp 0.4s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(244,63,122,0.3) !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 0.67rem !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.1em;
    color: rgba(255,255,255,0.6) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important; font-weight: 800 !important;
    color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
    letter-spacing: -0.03em;
}

/* ── Headings & body ──────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important; letter-spacing: -0.02em;
}
p, li, div, small, .stMarkdown, .stText {
    color: rgba(255,255,255,0.88) !important;
}
.stMarkdown strong { color: #f9a8c9 !important; font-weight: 600; }
[data-testid="stCaptionContainer"] p {
    color: rgba(255,255,255,0.55) !important; font-style: normal;
}

/* ── Expanders ────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #112052 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    box-shadow: none !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
    transition: border-color 0.2s !important;
}
[data-testid="stExpander"]:hover { border-color: rgba(244,63,122,0.25) !important; }
[data-testid="stExpander"] summary {
    background: rgba(255,255,255,0.03) !important;
    color: rgba(255,255,255,0.85) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 14px 18px !important;
}

/* ── Form widgets ─────────────────────────────────────────────────────────── */
[data-testid="stWidgetLabel"] p {
    color: rgba(255,255,255,0.9) !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
}
[data-baseweb="select"] > div:first-child {
    background: #0d1b3e !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    transition: border-color 0.15s !important;
}
[data-baseweb="select"] > div:first-child:focus-within {
    border-color: rgba(244,63,122,0.5) !important;
}
[data-baseweb="select"] span, [data-baseweb="select"] div {
    color: #ffffff !important;
}
[data-baseweb="popover"], [data-baseweb="menu"],
[role="listbox"], ul[data-baseweb="menu"] {
    background: #0f1e42 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    box-shadow: 0 16px 48px rgba(0,0,0,0.4) !important;
}
[data-baseweb="menu"] li, [role="option"] {
    background: transparent !important;
    color: rgba(255,255,255,0.7) !important;
}
[data-baseweb="menu"] li:hover, [role="option"]:hover, [aria-selected="true"] {
    background: rgba(244,63,122,0.15) !important;
    color: #f9a8c9 !important;
}
[data-baseweb="input"] input, [data-baseweb="base-input"] input,
.stNumberInput input, input[type="number"] {
    background: #0d1b3e !important;
    color: #ffffff !important;
    border: 1.5px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
}
[data-testid="stSlider"] p, [data-testid="stSlider"] span {
    color: rgba(255,255,255,0.85) !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.main .stFormSubmitButton button, .main .stButton button {
    background: #f43f7a !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.6rem 1.6rem !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 4px 16px rgba(244,63,122,0.35) !important;
    transition: background 0.2s, box-shadow 0.2s, transform 0.15s !important;
}
.main .stFormSubmitButton button:hover, .main .stButton button:hover {
    background: #e11d68 !important;
    box-shadow: 0 6px 22px rgba(244,63,122,0.5) !important;
    transform: translateY(-1px) !important;
    color: #ffffff !important;
}

/* ── Dataframe ────────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}

/* ── Table (st.table) ─────────────────────────────────────────────────────── */
[data-testid="stTable"] {
    max-height: 280px;
    overflow-y: auto;
    display: block;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}
[data-testid="stTable"] table {
    width: 100%;
    border-collapse: collapse;
    background: #112052;
    border-radius: 12px;
    overflow: hidden;
}
[data-testid="stTable"] thead th {
    background: #0a1530 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    padding: 10px 14px !important;
    border-bottom: 1px solid rgba(255,255,255,0.1) !important;
    text-align: center !important;
}
[data-testid="stTable"] tbody td {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    padding: 9px 14px !important;
    border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    font-size: 0.875rem !important;
    text-align: center !important;
    white-space: nowrap !important;
}
[data-testid="stTable"] tbody tr:hover td {
    background: rgba(244,63,122,0.06) !important;
}

/* ── Alert / Info ─────────────────────────────────────────────────────────── */
[data-testid="stInfo"] {
    background: rgba(244,63,122,0.08) !important;
    border: 1px solid rgba(244,63,122,0.25) !important;
    border-radius: 12px !important;
}
[data-testid="stInfo"] p { color: #f9a8c9 !important; -webkit-text-fill-color: #f9a8c9 !important; }

/* ── Result boxes ─────────────────────────────────────────────────────────── */
.result-box {
    background: #112052;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 22px;
    margin: 16px 0;
    font-size: 1rem; font-weight: 700;
    display: flex; align-items: center; gap: 12px;
    animation: fadeUp 0.35s ease;
}
.result-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.result-malignant { border-left: 4px solid #f43f7a; color: #fda4af !important; -webkit-text-fill-color: #fda4af !important; }
.result-malignant .result-dot { background: #f43f7a; box-shadow: 0 0 10px rgba(244,63,122,0.6); }
.result-benign    { border-left: 4px solid #4ade80; color: #86efac !important; -webkit-text-fill-color: #86efac !important; }
.result-benign    .result-dot { background: #4ade80; box-shadow: 0 0 10px rgba(74,222,128,0.5); }
.result-high      { border-left: 4px solid #f43f7a; color: #fda4af !important; -webkit-text-fill-color: #fda4af !important; }
.result-high      .result-dot { background: #f43f7a; box-shadow: 0 0 10px rgba(244,63,122,0.6); }
.result-medium    { border-left: 4px solid #fbbf24; color: #fde68a !important; -webkit-text-fill-color: #fde68a !important; }
.result-medium    .result-dot { background: #fbbf24; box-shadow: 0 0 10px rgba(251,191,36,0.5); }
.result-low       { border-left: 4px solid #4ade80; color: #86efac !important; -webkit-text-fill-color: #86efac !important; }
.result-low       .result-dot { background: #4ade80; box-shadow: 0 0 10px rgba(74,222,128,0.5); }

/* ── Model header ─────────────────────────────────────────────────────────── */
.model-header {
    background: #112052;
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 4px solid #f43f7a;
    border-radius: 0 12px 12px 0;
    padding: 14px 20px;
    margin: 28px 0 18px;
}
.model-header h4 { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; margin: 0 0 3px; font-size: 0.95rem; font-weight: 700; }
.model-header p  { color: rgba(255,255,255,0.4) !important; margin: 0; font-size: 0.8rem; }

/* ── Scrollbar ────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0a1530; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(244,63,122,0.4); }

/* ── Animation ────────────────────────────────────────────────────────────── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
"""


def inject_theme():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
