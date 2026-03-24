import joblib
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


@lru_cache(maxsize=None)
def get_model_a():
    return joblib.load(ROOT / "models/model_a.pkl")


@lru_cache(maxsize=None)
def get_model_b():
    return joblib.load(ROOT / "models/model_b.pkl")


@lru_cache(maxsize=None)
def get_model_c():
    return joblib.load(ROOT / "models/model_c.pkl")
