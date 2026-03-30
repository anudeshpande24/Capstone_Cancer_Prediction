import io
import datetime

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go


from utils.data_loader import load_wbcd, load_metabric, api_health
from utils.theme import inject_theme

st.set_page_config(page_title="BreastCare Decision Support", page_icon="🩺", layout="wide")
inject_theme()

API = "http://localhost:8000"

NAV_ITEMS = [
    "Data Overview",
    "Diagnosis",
    "Risk Stratification",
    "Survival Analysis",
    "Model Metrics",

    "Cohort Comparison",
]

if "page" not in st.session_state:
    st.session_state.page = "Data Overview"

if "history" not in st.session_state:
    st.session_state["history"] = []

# ── Module-level HTML helpers (reused across pages) ───────────────────────────

def _metrics_html(items, color="#f43f7a"):
    """items: list of (label, value 0-1) tuples"""
    rows = ""
    for label, value in items:
        pct = round(value * 100, 1)
        rows += (
            f'<div style="margin-bottom:10px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px;">'
            f'<span style="font-size:0.78rem;font-weight:600;color:rgba(255,255,255,0.75);">{label}</span>'
            f'<span style="font-size:0.9rem;font-weight:700;color:#ffffff;">{pct}%</span>'
            f'</div>'
            f'<div style="background:rgba(255,255,255,0.07);border-radius:100px;height:8px;overflow:hidden;">'
            f'<div style="width:{pct}%;height:100%;border-radius:100px;'
            f'background:linear-gradient(90deg,{color},{color}cc);'
            f'box-shadow:0 0 8px {color}66;transition:width 0.4s ease;"></div>'
            f'</div>'
            f'</div>'
        )
    return f'<div style="padding:4px 0;">{rows}</div>'


def _cm_html(matrix, labels):
    max_val = max(v for row in matrix for v in row) or 1
    header_cells = "".join(
        f'<th style="padding:10px 16px;text-align:center;color:#ffffff;font-size:0.72rem;'
        f'font-weight:600;text-transform:uppercase;letter-spacing:0.07em;'
        f'background:#0a1530;border-bottom:1px solid rgba(255,255,255,0.1);">Pred<br>{l}</th>'
        for l in labels
    )
    rows_html = ""
    for i, row_label in enumerate(labels):
        cells = ""
        for j, val in enumerate(matrix[i]):
            intensity = val / max_val
            if i == j:
                bg = f"rgba(244,63,122,{0.12 + intensity * 0.65:.2f})"
                color = "#ffffff"
            else:
                bg = f"rgba(255,255,255,{0.02 + intensity * 0.12:.2f})"
                color = "rgba(255,255,255,0.55)"
            cells += (
                f'<td style="padding:18px 16px;text-align:center;background:{bg};'
                f'color:{color};font-size:1.35rem;font-weight:700;'
                f'border:1px solid rgba(255,255,255,0.05);">{val}</td>'
            )
        rows_html += (
            f'<tr>'
            f'<th style="padding:10px 16px;text-align:right;color:#ffffff;font-size:0.72rem;'
            f'font-weight:600;text-transform:uppercase;letter-spacing:0.07em;'
            f'background:#0a1530;border-right:1px solid rgba(255,255,255,0.1);">'
            f'Actual<br>{row_label}</th>{cells}</tr>'
        )
    return (
        f'<table style="width:100%;border-collapse:collapse;border-radius:12px;overflow:hidden;">'
        f'<tr><td style="background:#0a1530;border-bottom:1px solid rgba(255,255,255,0.1);'
        f'border-right:1px solid rgba(255,255,255,0.1);"></td>{header_cells}</tr>'
        f'{rows_html}</table>'
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sb-brand">'
        '<div class="sb-brand-name">BreastCare</div>'
        '<div class="sb-brand-sub">Decision Support System</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sb-section">Navigation</div>', unsafe_allow_html=True)
    _NAV_ICONS = {
        "Data Overview":       '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
        "Diagnosis":           '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
        "Risk Stratification": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        "Survival Analysis":   '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
        "Model Metrics":       '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="20" x2="21" y2="20"/><rect x="4" y="14" width="4" height="6" rx="0.5"/><rect x="10" y="8" width="4" height="12" rx="0.5"/><rect x="16" y="4" width="4" height="16" rx="0.5"/></svg>',

        "Cohort Comparison":   '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="12" r="7"/><circle cx="15" cy="12" r="7"/></svg>',
    }
    for label in NAV_ITEMS:
        active = st.session_state.page == label
        icon = _NAV_ICONS.get(label, "")
        if active:
            st.markdown(
                f'<div class="nav-item-active">{icon}<span>{label}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                st.session_state.page = label
                st.rerun()


page = st.session_state.page

# ── Page header ───────────────────────────────────────────────────────────────
connected = api_health()
status_html = (
    '<span class="status-ok">● API Connected</span>'
    if connected else
    '<span style="display:inline-flex;align-items:center;gap:7px;'
    'background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);'
    'border-radius:20px;padding:4px 14px;font-size:0.75rem;font-weight:600;'
    'color:#fca5a5;-webkit-text-fill-color:#fca5a5;">● API Offline</span>'
)
st.markdown(
    f'<div class="page-eyebrow">Clinical ML Platform</div>'
    f'<div style="display:flex;align-items:flex-start;justify-content:space-between;'
    f'flex-wrap:wrap;gap:12px;margin-bottom:8px;">'
    f'  <div>'
    f'    <p class="page-title">BreastCare Decision Support</p>'
    f'    <p class="page-sub">Interpretable prediction platform supporting clinical '
    f'decision-making in breast cancer care.</p>'
    f'  </div>'
    f'  <div style="padding-top:6px;">{status_html}</div>'
    f'</div>',
    unsafe_allow_html=True,
)
st.divider()

# ── Schema / metrics loaders ──────────────────────────────────────────────────
@st.cache_data
def get_diagnosis_schema():
    return requests.get(f"{API}/predict/diagnosis/schema", timeout=10).json()

@st.cache_data
def get_risk_schema():
    return requests.get(f"{API}/predict/risk/schema", timeout=10).json()

@st.cache_data
def get_survival_schema():
    return requests.get(f"{API}/predict/survival/schema", timeout=10).json()

@st.cache_data
def get_all_metrics():
    return requests.get(f"{API}/predict/metrics", timeout=10).json()

# ── Overview stat row (shown on every page) ───────────────────────────────────
_ICON_MICROSCOPE = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
    'stroke="#f43f7a" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M6 18h12"/><path d="M3 21h18"/>'
    '<path d="M14 18a6 6 0 0 0 0-10"/>'
    '<path d="M10 8V3h4v5"/>'
    '<path d="M10 8h4"/>'
    '<circle cx="10" cy="13" r="5"/>'
    '</svg>'
)
_ICON_DNA = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
    'stroke="#6366f1" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M2 15c6.667-6 13.333 0 20-6"/>'
    '<path d="M2 9c6.667 6 13.333 0 20 6"/>'
    '<path d="M7 11.5v1"/><path d="M12 9v1"/><path d="M17 11.5v1"/>'
    '<path d="M7 3C5.5 5.5 5.5 8 7 9.5"/>'
    '<path d="M17 3c1.5 2.5 1.5 5 0 6.5"/>'
    '<path d="M7 14.5C5.5 16 5.5 18.5 7 21"/>'
    '<path d="M17 14.5c1.5 1.5 1.5 4 0 6.5"/>'
    '</svg>'
)
_ICON_NETWORK = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
    'stroke="#14b8a6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="5" r="2"/>'
    '<circle cx="5" cy="19" r="2"/>'
    '<circle cx="19" cy="19" r="2"/>'
    '<circle cx="12" cy="14" r="2"/>'
    '<line x1="12" y1="7" x2="12" y2="12"/>'
    '<line x1="10.5" y1="15.5" x2="6.5" y2="17.5"/>'
    '<line x1="13.5" y1="15.5" x2="17.5" y2="17.5"/>'
    '<line x1="10.5" y1="6.5" x2="6.5" y2="17.5"/>'
    '<line x1="13.5" y1="6.5" x2="17.5" y2="17.5"/>'
    '</svg>'
)
_ICON_CHART = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
    'stroke="#fbbf24" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<line x1="3" y1="20" x2="21" y2="20"/>'
    '<rect x="4" y="14" width="4" height="6" rx="0.5" fill="rgba(251,191,36,0.3)" stroke="#fbbf24"/>'
    '<rect x="10" y="8" width="4" height="12" rx="0.5" fill="rgba(251,191,36,0.3)" stroke="#fbbf24"/>'
    '<rect x="16" y="4" width="4" height="16" rx="0.5" fill="rgba(251,191,36,0.3)" stroke="#fbbf24"/>'
    '</svg>'
)

c1, c2, c3, c4 = st.columns(4, gap="medium")
c1.markdown(
    f'<div class="stat-card">'
    f'<div class="stat-card-icon" style="background:rgba(244,63,122,0.15);">{_ICON_MICROSCOPE}</div>'
    '<div><div class="stat-card-value">569</div>'
    '<div class="stat-card-label">WBCD Patients</div></div></div>',
    unsafe_allow_html=True,
)
c2.markdown(
    f'<div class="stat-card">'
    f'<div class="stat-card-icon" style="background:rgba(99,102,241,0.15);">{_ICON_DNA}</div>'
    '<div><div class="stat-card-value">2,509</div>'
    '<div class="stat-card-label">METABRIC Patients</div></div></div>',
    unsafe_allow_html=True,
)
c3.markdown(
    f'<div class="stat-card">'
    f'<div class="stat-card-icon" style="background:rgba(20,184,166,0.15);">{_ICON_NETWORK}</div>'
    '<div><div class="stat-card-value">3</div>'
    '<div class="stat-card-label">ML Models</div></div></div>',
    unsafe_allow_html=True,
)
c4.markdown(
    f'<div class="stat-card">'
    f'<div class="stat-card-icon" style="background:rgba(251,191,36,0.15);">{_ICON_CHART}</div>'
    '<div><div class="stat-card-value">30+</div>'
    '<div class="stat-card-label">Clinical Features</div></div></div>',
    unsafe_allow_html=True,
)
st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)

# ── Data Overview ─────────────────────────────────────────────────────────────
if page == "Data Overview":
    st.markdown(
        '<div class="page-banner"><h3>Dataset Overview</h3>'
        '<p>Explore the two clinical datasets powering the prediction models.</p></div>',
        unsafe_allow_html=True,
    )

    # ── WBCD ──────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-heading">Wisconsin Breast Cancer Diagnostic</p>', unsafe_allow_html=True)
    st.caption("569 patient samples · 30 cell nucleus measurements · Binary classification")
    try:
        wbcd = load_wbcd()
        df_w = wbcd.copy()
        if "diagnosis" in df_w.columns:
            df_w["diagnosis"] = df_w["diagnosis"].astype(str).str.strip().str.upper()
            dc_w = df_w["diagnosis"].value_counts()
            n_benign    = int(dc_w.get("N", 0))
            n_malignant = int(dc_w.get("R", 0))
        else:
            n_benign = n_malignant = 0
        completeness_w = round((1 - df_w.isnull().mean().mean()) * 100, 1)
        n_miss_w = int((df_w.isnull().sum() > 0).sum())

        hw = st.columns(5)
        hw[0].metric("Total Patients",    f"{len(df_w):,}")
        hw[1].metric("Features",          df_w.shape[1])
        hw[2].metric("Benign",            f"{n_benign} ({n_benign/len(df_w):.0%})")
        hw[3].metric("Malignant",         f"{n_malignant} ({n_malignant/len(df_w):.0%})")
        hw[4].metric("Data Completeness", f"{completeness_w}%")

        tp_w, ts_w, td_w, tfi_w, tcorr_w = st.tabs(["Data Preview", "Summary Statistics", "Distributions", "Feature Correlation", "Correlation Explorer"])

        with tp_w:
            st.caption(f"First 5 of {len(df_w):,} rows · {n_miss_w} columns with missing values")
            st.table(df_w.head(5))

        with ts_w:
            st.caption("Descriptive statistics for all numeric features")
            st.table(df_w.select_dtypes(include="number").describe().round(4))

        with td_w:
            col_d1, col_d2 = st.columns(2, gap="large")
            with col_d1:
                st.markdown("**Diagnosis Distribution**")
                st.bar_chart(
                    pd.DataFrame({"Patients": {"Benign": n_benign, "Malignant": n_malignant}}),
                    color="#f43f7a",
                )
            with col_d2:
                st.markdown("**Mean Feature Values (key measurements)**")
                key_w = [c for c in ["radius_mean","texture_mean","perimeter_mean","area_mean","smoothness_mean","compactness_mean"] if c in df_w.columns]
                if key_w:
                    st.bar_chart(df_w[key_w].mean().rename("Mean Value"), color="#6366f1")

        with tfi_w:
            st.caption("Absolute Pearson correlation with malignancy — higher values indicate stronger predictive signal")
            if "diagnosis" in df_w.columns:
                df_w["_target"] = (df_w["diagnosis"] == "R").astype(int)
                num_cols_w = [c for c in df_w.select_dtypes(include="number").columns if c != "_target"]
                corr_w = df_w[num_cols_w].corrwith(df_w["_target"]).abs().sort_values(ascending=False).head(15)
                st.bar_chart(corr_w.rename("|Correlation|"), color="#f43f7a")

        with tcorr_w:
            st.caption("Select two numeric features to explore their relationship, colored by diagnosis")
            num_cols_exp = df_w.select_dtypes(include="number").columns.tolist()
            if len(num_cols_exp) >= 2:
                cx1, cx2 = st.columns(2, gap="medium")
                x_feat = cx1.selectbox("X axis", options=num_cols_exp, index=0, key="corr_x")
                y_feat = cx2.selectbox("Y axis", options=num_cols_exp, index=min(1, len(num_cols_exp) - 1), key="corr_y")
                if "diagnosis" in df_w.columns:
                    scatter_df = df_w[[x_feat, y_feat, "diagnosis"]].dropna().copy()
                    scatter_df["Diagnosis (0=Benign, 1=Malignant)"] = (scatter_df["diagnosis"] == "R").astype(int)
                    st.scatter_chart(scatter_df, x=x_feat, y=y_feat, color="Diagnosis (0=Benign, 1=Malignant)")
                else:
                    st.scatter_chart(df_w[[x_feat, y_feat]].dropna(), x=x_feat, y=y_feat)

    except Exception as e:
        st.error(f"Failed to load WBCD: {e}")

    st.markdown("<div style='margin-bottom:32px'></div>", unsafe_allow_html=True)

    # ── METABRIC ──────────────────────────────────────────────────────────────
    st.markdown('<p class="section-heading">METABRIC (Molecular Taxonomy of Breast Cancer International Consortium)</p>', unsafe_allow_html=True)
    st.caption("2,509 patients · Clinical, molecular & genomic features · Risk stratification & survival analysis")
    try:
        metabric = load_metabric()
        df_m = metabric.copy()

        n_deceased = n_living = 0
        median_surv = None
        if "Overall Survival Status" in df_m.columns:
            sc = df_m["Overall Survival Status"].value_counts()
            n_deceased = int(sc.get("Deceased", 0))
            n_living   = int(sc.get("Living", 0))
        if "Overall Survival (Months)" in df_m.columns:
            median_surv = round(float(df_m["Overall Survival (Months)"].median()), 1)
        completeness_m = round((1 - df_m.isnull().mean().mean()) * 100, 1)
        n_miss_m = int((df_m.isnull().sum() > 0).sum())

        hm = st.columns(5)
        hm[0].metric("Total Patients",    f"{len(df_m):,}")
        hm[1].metric("Features",          df_m.shape[1])
        hm[2].metric("Deceased",          f"{n_deceased} ({n_deceased/len(df_m):.0%})" if len(df_m) else "—")
        hm[3].metric("Median Survival",   f"{median_surv} mo" if median_surv else "—")
        hm[4].metric("Data Completeness", f"{completeness_m}%")

        tp_m, ts_m, td_m, tc_m, tsg_m = st.tabs(["Data Preview", "Summary Statistics", "Distributions", "Clinical Breakdown", "Subgroup Analysis"])

        with tp_m:
            st.caption(f"First 5 of {len(df_m):,} rows · {n_miss_m} columns with missing values")
            st.table(df_m.head(5))

        with ts_m:
            st.caption("Descriptive statistics for all numeric features")
            st.table(df_m.select_dtypes(include="number").describe().round(4))

        with td_m:
            col_m1, col_m2 = st.columns(2, gap="large")
            with col_m1:
                st.markdown("**Overall Survival Status**")
                if n_deceased or n_living:
                    st.bar_chart(
                        pd.DataFrame({"Patients": {"Living": n_living, "Deceased": n_deceased}}),
                        color="#14b8a6",
                    )
            with col_m2:
                st.markdown("**Age at Diagnosis Distribution**")
                if "Age at Diagnosis" in df_m.columns:
                    age_bins = pd.cut(df_m["Age at Diagnosis"].dropna(), bins=10)
                    age_dist = age_bins.value_counts().sort_index()
                    age_dist.index = [f"{int(i.left)}–{int(i.right)}" for i in age_dist.index]
                    st.bar_chart(age_dist.rename("Patients"), color="#6366f1")

        with tc_m:
            col_c1, col_c2 = st.columns(2, gap="large")
            with col_c1:
                st.markdown("**Top Cancer Subtypes**")
                if "Cancer Type Detailed" in df_m.columns:
                    st.bar_chart(df_m["Cancer Type Detailed"].value_counts().head(8).rename("Patients"), color="#f43f7a")

                st.markdown("**Tumor Stage Distribution**")
                if "Tumor Stage" in df_m.columns:
                    st.bar_chart(df_m["Tumor Stage"].value_counts().sort_index().rename("Patients"), color="#fbbf24")
            with col_c2:
                st.markdown("**Treatment Distribution**")
                tx_counts = {}
                for t in ["Chemotherapy", "Hormone Therapy", "Radio Therapy"]:
                    if t in df_m.columns:
                        yes = int(df_m[t].astype(str).str.strip().str.lower().isin(["yes","1"]).sum())
                        tx_counts[t] = yes
                if tx_counts:
                    st.bar_chart(pd.Series(tx_counts).rename("Patients"), color="#14b8a6")

                st.markdown("**PAM50 Molecular Subtype**")
                if "Pam50 + Claudin-low subtype" in df_m.columns:
                    st.bar_chart(df_m["Pam50 + Claudin-low subtype"].value_counts().head(7).rename("Patients"), color="#6366f1")

        with tsg_m:
            st.caption("Filter the METABRIC cohort by clinical attributes and inspect survival statistics")
            sg1, sg2, sg3 = st.columns(3, gap="medium")
            cancer_types = sorted(df_m["Cancer Type Detailed"].dropna().unique().tolist()) if "Cancer Type Detailed" in df_m.columns else []
            sel_cancer = sg1.multiselect("Cancer Type Detailed", options=cancer_types, default=cancer_types[:3] if len(cancer_types) >= 3 else cancer_types, key="sg_cancer")
            sel_chemo  = sg2.selectbox("Chemotherapy", options=["All", "Yes", "No"], index=0, key="sg_chemo")
            tumor_stages = sorted(df_m["Tumor Stage"].dropna().unique().tolist()) if "Tumor Stage" in df_m.columns else []
            sel_stage  = sg3.multiselect("Tumor Stage", options=tumor_stages, default=tumor_stages, key="sg_stage")

            mask = pd.Series([True] * len(df_m), index=df_m.index)
            if sel_cancer and "Cancer Type Detailed" in df_m.columns:
                mask &= df_m["Cancer Type Detailed"].isin(sel_cancer)
            if sel_chemo != "All" and "Chemotherapy" in df_m.columns:
                mask &= df_m["Chemotherapy"].astype(str).str.strip().str.lower() == sel_chemo.lower()
            if sel_stage and "Tumor Stage" in df_m.columns:
                mask &= df_m["Tumor Stage"].isin(sel_stage)
            df_sg = df_m[mask]

            st.caption(f"Filtered cohort: {len(df_sg):,} patients")
            ss1, ss2, ss3 = st.columns(3, gap="medium")
            if "Overall Survival Status" in df_sg.columns:
                ss1.markdown("**Survival Status**")
                ss1.bar_chart(df_sg["Overall Survival Status"].value_counts().rename("Patients"), color="#14b8a6")
            if "Overall Survival (Months)" in df_sg.columns:
                med = df_sg["Overall Survival (Months)"].median()
                ss2.metric("Median Overall Survival", f"{med:.1f} months" if not pd.isna(med) else "—")
            if "Age at Diagnosis" in df_sg.columns and len(df_sg) > 0:
                ss3.markdown("**Age at Diagnosis**")
                age_bins_sg = pd.cut(df_sg["Age at Diagnosis"].dropna(), bins=8)
                age_dist_sg = age_bins_sg.value_counts().sort_index()
                age_dist_sg.index = [f"{int(i.left)}–{int(i.right)}" for i in age_dist_sg.index]
                ss3.bar_chart(age_dist_sg.rename("Patients"), color="#6366f1")

    except Exception as e:
        st.error(f"Failed to load METABRIC: {e}")

# ── Diagnosis ─────────────────────────────────────────────────────────────────
elif page == "Diagnosis":
    st.markdown(
        '<div class="page-banner"><h3>Tumor Diagnosis</h3>'
        '<p>Predicts whether a breast mass is <strong>Benign</strong> or <strong>Malignant</strong> '
        'from 30 cell nucleus measurements. Powered by a Calibrated Random Forest.</p></div>',
        unsafe_allow_html=True,
    )
    try:
        schema_a    = get_diagnosis_schema()
        features_a  = schema_a["features"]
        stats_a     = schema_a["stats"]
        mean_feats  = [f for f in features_a if f.endswith("_mean")]
        se_feats    = [f for f in features_a if f.endswith("_se")]
        worst_feats = [f for f in features_a if f.endswith("_worst")]

        tab_predict, tab_history = st.tabs(["Predict", "History"])

        with tab_predict:
            inputs_a = {}
            with st.form("diagnosis_form"):
                with st.expander("Mean values", expanded=True):
                    cols = st.columns(3)
                    for i, f in enumerate(mean_feats):
                        s = stats_a[f]
                        inputs_a[f] = cols[i % 3].number_input(
                            f, min_value=float(s["min"]), max_value=float(s["max"]),
                            value=float(s["mean"]), format="%.5f", key=f"a_{f}")
                with st.expander("Standard error values"):
                    cols = st.columns(3)
                    for i, f in enumerate(se_feats):
                        s = stats_a[f]
                        inputs_a[f] = cols[i % 3].number_input(
                            f, min_value=float(s["min"]), max_value=float(s["max"]),
                            value=float(s["mean"]), format="%.5f", key=f"a_{f}")
                with st.expander("Worst values"):
                    cols = st.columns(3)
                    for i, f in enumerate(worst_feats):
                        s = stats_a[f]
                        inputs_a[f] = cols[i % 3].number_input(
                            f, min_value=float(s["min"]), max_value=float(s["max"]),
                            value=float(s["mean"]), format="%.5f", key=f"a_{f}")
                submitted_a = st.form_submit_button("Run Diagnosis", use_container_width=False)

            if submitted_a:
                st.session_state["last_diagnosis_inputs"] = dict(inputs_a)
                with st.spinner("Analysing..."):
                    resp = requests.post(f"{API}/predict/diagnosis", json={"features": inputs_a}, timeout=15)
                    resp.raise_for_status()
                    r = resp.json()
                st.session_state["last_diagnosis_result"] = r

                label_a = r["label"]
                css = "result-malignant" if label_a == "Malignant" else "result-benign"
                st.markdown(
                    f'<div class="result-box {css}"><div class="result-dot"></div>'
                    f'Prediction: {label_a}</div>',
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns(2)
                c1.metric("Malignant probability", f"{r['probability_malignant']:.1%}")
                c2.metric("Benign probability",    f"{r['probability_benign']:.1%}")

                # Record in history
                ts_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state["history"].append({
                    "timestamp": ts_str,
                    "model": "Diagnosis (Model A)",
                    "inputs_summary": f"radius_mean={inputs_a.get('radius_mean', ''):.4f}, texture_mean={inputs_a.get('texture_mean', ''):.4f}",
                    "result": f"{label_a} (P_mal={r['probability_malignant']:.1%})",
                })

                # Patient report download
                buf = io.StringIO()
                buf.write("BreastCare Decision Support — Patient Report\n")
                buf.write("=" * 50 + "\n")
                buf.write(f"Timestamp : {ts_str}\n")
                buf.write(f"Model     : Diagnosis (Calibrated Random Forest)\n\n")
                buf.write("Patient Inputs\n")
                buf.write("-" * 30 + "\n")
                for feat, val in inputs_a.items():
                    buf.write(f"  {feat}: {val}\n")
                buf.write("\nPrediction Result\n")
                buf.write("-" * 30 + "\n")
                buf.write(f"  Label              : {r['label']}\n")
                buf.write(f"  P(Malignant)       : {r['probability_malignant']:.4f}\n")
                buf.write(f"  P(Benign)          : {r['probability_benign']:.4f}\n")
                st.download_button(
                    "Download Patient Report (.txt)",
                    data=buf.getvalue(),
                    file_name=f"diagnosis_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                )

        with tab_history:
            hist = [h for h in st.session_state["history"] if "Diagnosis" in h["model"]]
            if hist:
                st.table(pd.DataFrame(hist))
            else:
                st.info("No predictions yet this session.")

    except Exception as e:
        st.error(f"Diagnosis model unavailable: {e}")

# ── Risk Stratification ───────────────────────────────────────────────────────
elif page == "Risk Stratification":
    st.markdown(
        '<div class="page-banner"><h3>Risk Stratification</h3>'
        '<p>Classifies patient into <strong>Low</strong>, <strong>Medium</strong>, or '
        '<strong>High</strong> risk using clinical and molecular features. Powered by XGBoost.</p></div>',
        unsafe_allow_html=True,
    )
    try:
        schema_b    = get_risk_schema()
        num_stats_b = schema_b["num_stats"]
        cat_opts_b  = schema_b["cat_options"]
        KEY_NUM_B = [
            "Age at Diagnosis", "Tumor Size", "Tumor Stage", "Neoplasm Histologic Grade",
            "Lymph nodes examined positive", "Nottingham prognostic index", "Mutation Count",
        ]
        KEY_CAT_B = [
            "Type of Breast Surgery", "Cancer Type Detailed", "ER Status", "HER2 Status",
            "PR Status", "Cellularity", "Chemotherapy", "Hormone Therapy", "Radio Therapy",
            "Pam50 + Claudin-low subtype",
        ]

        tab_predict_b, tab_history_b = st.tabs(["Predict", "History"])

        with tab_predict_b:
            inputs_b = {}
            with st.form("risk_form"):
                col1, col2 = st.columns(2, gap="large")
                with col1:
                    st.markdown("**Clinical measurements**")
                    for f in KEY_NUM_B:
                        if f in num_stats_b:
                            s = num_stats_b[f]
                            inputs_b[f] = st.slider(
                                f, min_value=float(s["min"]), max_value=float(s["max"]),
                                value=float(s["median"]), key=f"b_{f}")
                with col2:
                    st.markdown("**Molecular & treatment features**")
                    for f in KEY_CAT_B:
                        if f in cat_opts_b:
                            inputs_b[f] = st.selectbox(f, options=cat_opts_b[f], key=f"b_{f}")
                submitted_b = st.form_submit_button("Run Risk Stratification", use_container_width=False)

            if submitted_b:
                with st.spinner("Analysing..."):
                    resp = requests.post(f"{API}/predict/risk", json={"features": inputs_b}, timeout=15)
                    resp.raise_for_status()
                    r = resp.json()
                label_b = r["label"]
                css = f"result-{label_b.lower()}"
                st.markdown(
                    f'<div class="result-box {css}"><div class="result-dot"></div>'
                    f'Risk Level: {label_b}</div>',
                    unsafe_allow_html=True,
                )
                cols = st.columns(3)
                for i, (risk, prob) in enumerate(r["probabilities"].items()):
                    cols[i].metric(f"{risk} Risk", f"{prob:.1%}")

                # Record in history
                ts_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state["history"].append({
                    "timestamp": ts_str,
                    "model": "Risk Stratification (Model B)",
                    "inputs_summary": f"Age={inputs_b.get('Age at Diagnosis', '')}, Stage={inputs_b.get('Tumor Stage', '')}",
                    "result": label_b,
                })

                # Patient report download
                buf = io.StringIO()
                buf.write("BreastCare Decision Support — Patient Report\n")
                buf.write("=" * 50 + "\n")
                buf.write(f"Timestamp : {ts_str}\n")
                buf.write(f"Model     : Risk Stratification (XGBoost)\n\n")
                buf.write("Patient Inputs\n")
                buf.write("-" * 30 + "\n")
                for feat, val in inputs_b.items():
                    buf.write(f"  {feat}: {val}\n")
                buf.write("\nPrediction Result\n")
                buf.write("-" * 30 + "\n")
                buf.write(f"  Risk Level : {r['label']}\n")
                for risk, prob in r["probabilities"].items():
                    buf.write(f"  P({risk}) : {prob:.4f}\n")
                st.download_button(
                    "Download Patient Report (.txt)",
                    data=buf.getvalue(),
                    file_name=f"risk_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                )

        with tab_history_b:
            hist_b = [h for h in st.session_state["history"] if "Risk" in h["model"]]
            if hist_b:
                st.table(pd.DataFrame(hist_b))
            else:
                st.info("No predictions yet this session.")

    except Exception as e:
        st.error(f"Risk model unavailable: {e}")

# ── Survival Analysis ─────────────────────────────────────────────────────────
elif page == "Survival Analysis":
    st.markdown(
        '<div class="page-banner"><h3>Survival Analysis</h3>'
        '<p>Estimates <strong>Overall Survival</strong> and <strong>Relapse-Free Survival</strong> '
        'probabilities at 12, 24, and 36 months via Cox Proportional Hazards.</p></div>',
        unsafe_allow_html=True,
    )
    try:
        schema_c   = get_survival_schema()
        cat_opts_c = schema_c["cat_options"]
        defaults_c = schema_c["defaults"]
        KEY_CAT_C = [
            "Type of Breast Surgery", "Cancer Type Detailed", "ER Status", "HER2 Status",
            "PR Status", "Cellularity", "Chemotherapy", "Hormone Therapy", "Radio Therapy",
            "Pam50 + Claudin-low subtype", "Inferred Menopausal State",
        ]
        KEY_NUM_C = {
            "Age at Diagnosis": (20.0, 100.0), "Tumor Size": (1.0, 200.0),
            "Tumor Stage": (1.0, 4.0), "Neoplasm Histologic Grade": (1.0, 3.0),
            "Lymph nodes examined positive": (0.0, 30.0),
            "Nottingham prognostic index": (1.0, 7.0), "Mutation Count": (0.0, 300.0),
        }

        tab_predict_c, tab_history_c = st.tabs(["Predict", "History"])

        with tab_predict_c:
            inputs_c = {}
            with st.form("survival_form"):
                col1, col2 = st.columns(2, gap="large")
                with col1:
                    st.markdown("**Clinical measurements**")
                    for f, (lo, hi) in KEY_NUM_C.items():
                        inputs_c[f] = st.slider(
                            f, min_value=lo, max_value=hi,
                            value=float(defaults_c.get(f, (lo + hi) / 2)), key=f"c_{f}")
                with col2:
                    st.markdown("**Molecular & treatment features**")
                    for f in KEY_CAT_C:
                        if f in cat_opts_c:
                            opts = cat_opts_c[f]
                            default_idx = min(int(defaults_c.get(f, 0)), len(opts) - 1)
                            inputs_c[f] = st.selectbox(f, options=opts, index=default_idx, key=f"c_{f}")
                submitted_c = st.form_submit_button("Run Survival Analysis", use_container_width=True)

            if submitted_c:
                st.session_state["last_survival_inputs"] = dict(inputs_c)
                with st.spinner("Analysing..."):
                    resp = requests.post(f"{API}/predict/survival", json={"features": inputs_c}, timeout=15)
                    resp.raise_for_status()
                    r = resp.json()
                st.session_state["last_survival_result"] = r

                col_os, col_rfs = st.columns(2, gap="large")
                with col_os:
                    st.markdown(
                        '<p style="font-size:0.72rem;font-weight:600;color:rgba(255,255,255,0.4);'
                        'text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">'
                        'Overall Survival</p>', unsafe_allow_html=True)
                    for months, prob in r["overall_survival"].items():
                        st.metric(f"{months}-month", f"{prob:.1%}")
                with col_rfs:
                    st.markdown(
                        '<p style="font-size:0.72rem;font-weight:600;color:rgba(255,255,255,0.4);'
                        'text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">'
                        'Relapse-Free Survival</p>', unsafe_allow_html=True)
                    for months, prob in r["relapse_free_survival"].items():
                        st.metric(f"{months}-month", f"{prob:.1%}")
                st.info("C-index — Overall Survival: 0.658 · Relapse-Free Survival: 0.636")

                # Record in history
                ts_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                os_vals = list(r["overall_survival"].values())
                rfs_vals = list(r["relapse_free_survival"].values())
                result_summary = f"OS@12mo={os_vals[0]:.1%}, RFS@12mo={rfs_vals[0]:.1%}" if os_vals else "—"
                st.session_state["history"].append({
                    "timestamp": ts_str,
                    "model": "Survival Analysis (Model C)",
                    "inputs_summary": f"Age={inputs_c.get('Age at Diagnosis', '')}, Stage={inputs_c.get('Tumor Stage', '')}",
                    "result": result_summary,
                })

                # Patient report download
                buf = io.StringIO()
                buf.write("BreastCare Decision Support — Patient Report\n")
                buf.write("=" * 50 + "\n")
                buf.write(f"Timestamp : {ts_str}\n")
                buf.write(f"Model     : Survival Analysis (Cox Proportional Hazards)\n\n")
                buf.write("Patient Inputs\n")
                buf.write("-" * 30 + "\n")
                for feat, val in inputs_c.items():
                    buf.write(f"  {feat}: {val}\n")
                buf.write("\nPrediction Result — Overall Survival\n")
                buf.write("-" * 30 + "\n")
                for months, prob in r["overall_survival"].items():
                    buf.write(f"  {months}-month OS: {prob:.4f}\n")
                buf.write("\nPrediction Result — Relapse-Free Survival\n")
                buf.write("-" * 30 + "\n")
                for months, prob in r["relapse_free_survival"].items():
                    buf.write(f"  {months}-month RFS: {prob:.4f}\n")
                st.download_button(
                    "Download Patient Report (.txt)",
                    data=buf.getvalue(),
                    file_name=f"survival_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                )

            # Survival curve (shows if a result already exists this session)
            if "last_survival_inputs" in st.session_state:
                with st.expander("Survival Curve"):
                    try:
                        curve_resp = requests.post(
                            f"{API}/predict/survival/curve",
                            json={"features": st.session_state["last_survival_inputs"]},
                            timeout=20,
                        )
                        curve_resp.raise_for_status()
                        curve_data = curve_resp.json()
                        curve_df = pd.DataFrame({
                            "Overall Survival": curve_data["overall_survival"],
                            "Relapse-Free Survival": curve_data["relapse_free_survival"],
                        }, index=curve_data["months"])
                        curve_df.index.name = "Months"
                        st.line_chart(curve_df, x_label="Time (Months)", y_label="Survival Probability")
                    except Exception as ex:
                        st.warning(f"Survival curve unavailable: {ex}")

        with tab_history_c:
            hist_c = [h for h in st.session_state["history"] if "Survival" in h["model"]]
            if hist_c:
                st.table(pd.DataFrame(hist_c))
            else:
                st.info("No predictions yet this session.")

    except Exception as e:
        st.error(f"Survival model unavailable: {e}")

# ── Model Metrics ─────────────────────────────────────────────────────────────
elif page == "Model Metrics":
    st.markdown(
        '<div class="page-banner"><h3>Model Performance</h3>'
        '<p>Held-out test set evaluation for all three models. ',
        unsafe_allow_html=True,
    )

    try:
        all_m = get_all_metrics()

        # ── Model A ───────────────────────────────────────────────────────────
        st.markdown(
            '<div class="model-header"><h4>Model A — Tumor Diagnosis</h4>'
            '<p>Calibrated Random Forest · WBCD · Binary classification</p></div>',
            unsafe_allow_html=True,
        )
        ma = all_m.get("model_a")
        if ma:
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Accuracy",  f"{ma['accuracy']:.1%}")
            c2.metric("Precision", f"{ma['precision']:.1%}")
            c3.metric("Recall",    f"{ma['recall']:.1%}")
            c4.metric("F1 Score",  f"{ma['f1']:.1%}")
            c5.metric("ROC-AUC",   f"{ma['roc_auc']:.3f}")

            with st.expander("Metric definitions"):
                st.markdown(
                    '<div class="metric-glossary">'
                    '<span><strong>Accuracy</strong> — overall % of correct predictions</span>'
                    '<span><strong>Precision</strong> — of cases flagged malignant, % that truly are (low false-positive rate)</span>'
                    '<span><strong>Recall</strong> — of all true malignancies, % the model caught (low false-negative rate)</span>'
                    '<span><strong>F1 Score</strong> — harmonic mean of precision and recall; balances both concerns</span>'
                    '<span><strong>ROC-AUC</strong> — probability that the model ranks a malignant case higher than a benign one (1.0 = perfect)</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            col_va, col_cma = st.columns(2, gap="large")
            with col_va:
                st.markdown("**Classification Metrics**")
                st.markdown(_metrics_html([
                    ("Accuracy",  ma["accuracy"]),
                    ("Precision", ma["precision"]),
                    ("Recall",    ma["recall"]),
                    ("F1 Score",  ma["f1"]),
                    ("ROC-AUC",   ma["roc_auc"]),
                ], color="#f43f7a"), unsafe_allow_html=True)
            with col_cma:
                st.markdown("**Confusion Matrix**")
                st.markdown(_cm_html(ma["confusion_matrix"], ["Benign", "Malignant"]), unsafe_allow_html=True)
            st.caption(f"Test set: {ma['test_size']} samples · Diagonal cells = correct predictions (darker = more)")
        else:
            st.warning("Model A metrics not available — re-run export_models.py")

        # ── Model B ───────────────────────────────────────────────────────────
        st.markdown(
            '<div class="model-header"><h4>Model B — Risk Stratification</h4>'
            '<p>XGBoost · METABRIC · 3-class (Low / Medium / High)</p></div>',
            unsafe_allow_html=True,
        )
        mb = all_m.get("model_b")
        if mb:
            fpc = mb["f1_per_class"]
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Accuracy",    f"{mb['accuracy']:.1%}")
            c2.metric("F1 Weighted", f"{mb['f1_weighted']:.1%}")
            c3.metric("F1 — Low",    f"{fpc['Low']:.1%}")
            c4.metric("F1 — Medium", f"{fpc['Medium']:.1%}")
            c5.metric("F1 — High",   f"{fpc['High']:.1%}")

            with st.expander("Metric definitions"):
                st.markdown(
                    '<div class="metric-glossary">'
                    '<span><strong>Accuracy</strong> — overall % of patients assigned the correct risk tier</span>'
                    '<span><strong>F1 Weighted</strong> — F1 averaged across all three classes, weighted by class size; handles class imbalance</span>'
                    '<span><strong>F1 per class</strong> — per-tier F1; a low score for "High" risk means the model struggles to identify the most critical patients</span>'
                    '<span><strong>Confusion matrix</strong> — rows are true labels, columns are predictions; off-diagonal cells are misclassifications</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            col_vb, col_cmb = st.columns(2, gap="large")
            with col_vb:
                st.markdown("**Classification Metrics**")
                st.markdown(_metrics_html([
                    ("Accuracy",    mb["accuracy"]),
                    ("F1 Weighted", mb["f1_weighted"]),
                    ("F1 — Low",    fpc["Low"]),
                    ("F1 — Medium", fpc["Medium"]),
                    ("F1 — High",   fpc["High"]),
                ], color="#6366f1"), unsafe_allow_html=True)
            with col_cmb:
                st.markdown("**Confusion Matrix**")
                st.markdown(_cm_html(mb["confusion_matrix"], ["Low", "Medium", "High"]), unsafe_allow_html=True)
            st.caption(f"Test set: {mb['test_size']} samples · Diagonal cells = correct predictions (darker = more)")
        else:
            st.warning("Model B metrics not available — re-run export_models.py")

        # ── Model C ───────────────────────────────────────────────────────────
        st.markdown(
            '<div class="model-header"><h4>Model C — Survival Analysis</h4>'
            '<p>Cox Proportional Hazards · METABRIC · Time-to-event</p></div>',
            unsafe_allow_html=True,
        )
        mc = all_m.get("model_c")
        if mc:
            c1, c2, c3 = st.columns(3)
            c1.metric("C-index — Overall Survival",      f"{mc['c_index_os']:.3f}")
            c2.metric("C-index — Relapse-Free Survival", f"{mc['c_index_rfs']:.3f}")
            c3.metric("Training Patients", f"{mc['train_size']:,}")

            with st.expander("Metric definitions"):
                st.markdown(
                    '<div class="metric-glossary">'
                    '<span><strong>C-index (Concordance index)</strong> — measures how well the model ranks patients by survival time. '
                    '0.5 = no better than random chance; 1.0 = perfect ranking; values above 0.6 are considered clinically useful</span>'
                    '<span><strong>Overall Survival C-index</strong> — discriminative ability for time until death</span>'
                    '<span><strong>Relapse-Free Survival C-index</strong> — discriminative ability for time until cancer recurrence or death</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            col_vc, _ = st.columns([1, 1])
            with col_vc:
                st.markdown("**C-index Comparison**")
                st.markdown(_metrics_html([
                    ("Random baseline",       0.5),
                    ("Overall Survival",      mc["c_index_os"]),
                    ("Relapse-Free Survival", mc["c_index_rfs"]),
                    ("Perfect ceiling",       1.0),
                ], color="#14b8a6"), unsafe_allow_html=True)
            st.caption(f"C-index: 0.5 = random · 1.0 = perfect discrimination · Training set: {mc['train_size']:,} patients")
        else:
            st.warning("Model C metrics not available — re-run export_models.py")

    except Exception as e:
        st.error(f"Metrics unavailable: {e}")

# ── Cohort Comparison ─────────────────────────────────────────────────────────
elif page == "Cohort Comparison":
    st.markdown(
        '<div class="page-banner"><h3>Cohort Comparison</h3>'
        '<p>Compare two patient profiles side-by-side: risk stratification and survival curves.</p></div>',
        unsafe_allow_html=True,
    )
    try:
        schema_b    = get_risk_schema()
        num_stats_b = schema_b["num_stats"]
        cat_opts_b  = schema_b["cat_options"]
        KEY_NUM_B_C = [
            "Age at Diagnosis", "Tumor Size", "Tumor Stage", "Neoplasm Histologic Grade",
            "Lymph nodes examined positive", "Nottingham prognostic index", "Mutation Count",
        ]
        KEY_CAT_B_C = [
            "Type of Breast Surgery", "Cancer Type Detailed", "ER Status", "HER2 Status",
            "PR Status", "Cellularity", "Chemotherapy", "Hormone Therapy", "Radio Therapy",
            "Pam50 + Claudin-low subtype",
        ]

        col1, col2 = st.columns(2, gap="large")

        def _cohort_form(col, suffix):
            inputs = {}
            with col:
                st.markdown(f"**Patient {suffix}**")
                with st.form(f"cohort_form_{suffix}"):
                    st.markdown("*Clinical measurements*")
                    for f in KEY_NUM_B_C:
                        if f in num_stats_b:
                            s = num_stats_b[f]
                            inputs[f] = st.slider(
                                f, min_value=float(s["min"]), max_value=float(s["max"]),
                                value=float(s["median"]), key=f"cc{suffix}_{f}")
                    st.markdown("*Molecular & treatment features*")
                    for f in KEY_CAT_B_C:
                        if f in cat_opts_b:
                            inputs[f] = st.selectbox(f, options=cat_opts_b[f], key=f"cc{suffix}_{f}")
                    run = st.form_submit_button(f"Run Patient {suffix}", use_container_width=True)
            return inputs, run

        inputs_p1, run_p1 = _cohort_form(col1, "A")
        inputs_p2, run_p2 = _cohort_form(col2, "B")

        if run_p1:
            st.session_state["cohort_p1_inputs"] = dict(inputs_p1)
            with st.spinner("Running Patient A..."):
                r1 = requests.post(f"{API}/predict/risk", json={"features": inputs_p1}, timeout=15)
                r1.raise_for_status()
                st.session_state["cohort_p1_result"] = r1.json()

        if run_p2:
            st.session_state["cohort_p2_inputs"] = dict(inputs_p2)
            with st.spinner("Running Patient B..."):
                r2 = requests.post(f"{API}/predict/risk", json={"features": inputs_p2}, timeout=15)
                r2.raise_for_status()
                st.session_state["cohort_p2_result"] = r2.json()

        if "cohort_p1_result" in st.session_state or "cohort_p2_result" in st.session_state:
            st.markdown("---")
            st.markdown("### Risk Comparison")
            res_col1, res_col2 = st.columns(2, gap="large")

            if "cohort_p1_result" in st.session_state:
                r1 = st.session_state["cohort_p1_result"]
                with res_col1:
                    label1 = r1["label"]
                    css1 = f"result-{label1.lower()}"
                    st.markdown(
                        f'<div class="result-box {css1}"><div class="result-dot"></div>'
                        f'Patient A — {label1}</div>',
                        unsafe_allow_html=True,
                    )
                    for risk, prob in r1["probabilities"].items():
                        st.metric(f"{risk} Risk", f"{prob:.1%}")

            if "cohort_p2_result" in st.session_state:
                r2 = st.session_state["cohort_p2_result"]
                with res_col2:
                    label2 = r2["label"]
                    css2 = f"result-{label2.lower()}"
                    st.markdown(
                        f'<div class="result-box {css2}"><div class="result-dot"></div>'
                        f'Patient B — {label2}</div>',
                        unsafe_allow_html=True,
                    )
                    for risk, prob in r2["probabilities"].items():
                        st.metric(f"{risk} Risk", f"{prob:.1%}")

        if "cohort_p1_inputs" in st.session_state and "cohort_p2_inputs" in st.session_state:
            st.markdown("---")
            st.markdown("### Survival Curve Comparison")
            try:
                schema_c = get_survival_schema()
                defaults_c = schema_c["defaults"]

                def _merge_survival_inputs(risk_inputs):
                    merged = dict(defaults_c)
                    for k, v in risk_inputs.items():
                        merged[k] = v
                    return merged

                curve1_resp = requests.post(
                    f"{API}/predict/survival/curve",
                    json={"features": _merge_survival_inputs(st.session_state["cohort_p1_inputs"])},
                    timeout=20,
                )
                curve1_resp.raise_for_status()
                curve1 = curve1_resp.json()

                curve2_resp = requests.post(
                    f"{API}/predict/survival/curve",
                    json={"features": _merge_survival_inputs(st.session_state["cohort_p2_inputs"])},
                    timeout=20,
                )
                curve2_resp.raise_for_status()
                curve2 = curve2_resp.json()

                months = curve1["months"]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=months, y=curve1["overall_survival"],      name="Patient A — OS",  line=dict(color="#f43f7a", width=2)))
                fig.add_trace(go.Scatter(x=months, y=curve1["relapse_free_survival"], name="Patient A — RFS", line=dict(color="#f43f7a", width=2, dash="dash")))
                fig.add_trace(go.Scatter(x=months, y=curve2["overall_survival"],      name="Patient B — OS",  line=dict(color="#38bdf8", width=2)))
                fig.add_trace(go.Scatter(x=months, y=curve2["relapse_free_survival"], name="Patient B — RFS", line=dict(color="#38bdf8", width=2, dash="dash")))
                fig.update_layout(
                    xaxis_title="Time (Months)",
                    yaxis_title="Survival Probability",
                    yaxis=dict(range=[0, 1.05]),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ffffff"),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                    margin=dict(l=20, r=20, t=20, b=20),
                )
                fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.15)")
                fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.15)")
                st.plotly_chart(fig, use_container_width=True)
                st.caption(
                    "**OS (Overall Survival):** Probability the patient is still alive at a given time. "
                    "**RFS (Relapse-Free Survival):** Probability the patient is alive and has not had a cancer recurrence. "
                    "RFS is always ≤ OS since a relapse counts as an event even if the patient survives it."
                )
            except Exception as ex:
                st.warning(f"Survival curve comparison unavailable: {ex}")

    except Exception as e:
        st.error(f"Cohort comparison unavailable: {e}")
