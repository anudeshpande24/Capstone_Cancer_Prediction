from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent


@st.cache_data
def load_wbcd() -> pd.DataFrame:
    return pd.read_csv(ROOT / "WBCD_dataset.csv")


@st.cache_data
def load_metabric() -> pd.DataFrame:
    return pd.read_csv(ROOT / "clean_metabric.csv")
