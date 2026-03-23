import pandas as pd
import requests
import streamlit as st

API_BASE = "http://localhost:8000"


def _fetch(endpoint: str) -> dict:
    response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
    response.raise_for_status()
    return response.json()


@st.cache_data
def load_wbcd() -> pd.DataFrame:
    data = _fetch("/data/wbcd")
    return pd.DataFrame(data["records"])


@st.cache_data
def load_metabric() -> pd.DataFrame:
    data = _fetch("/data/metabric")
    return pd.DataFrame(data["records"])


def api_health() -> bool:
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
