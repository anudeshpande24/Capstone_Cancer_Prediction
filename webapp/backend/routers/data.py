from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

ROOT = Path(__file__).resolve().parent.parent.parent.parent

router = APIRouter(prefix="/data", tags=["data"])


def _load(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    return pd.read_csv(path)


@router.get("/wbcd")
def get_wbcd():
    df = _load(ROOT / "WBCD_dataset.csv")
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "records": df.to_dict(orient="records"),
    }


@router.get("/metabric")
def get_metabric():
    df = _load(ROOT / "clean_metabric.csv")
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "records": df.to_dict(orient="records"),
    }
