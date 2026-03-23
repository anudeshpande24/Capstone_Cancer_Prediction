from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"


@st.cache_data
def load_wbcd() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "clean_WBCD.csv")


@st.cache_data
def load_metabric() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "clean_metabric.csv")
