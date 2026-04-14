"""
conftest.py — pytest configuration for BreastCare test suite.

Adds webapp/ to sys.path so that `from backend.xxx import yyy` works
in test_api.py without requiring an installed package.
"""
import sys
from pathlib import Path

# Project root (one level above this file)
ROOT = Path(__file__).resolve().parent.parent

# webapp/ must be on sys.path so `from backend.main import app` resolves
WEBAPP = ROOT / "webapp"
if str(WEBAPP) not in sys.path:
    sys.path.insert(0, str(WEBAPP))
