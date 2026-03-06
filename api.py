


"""
GFLS Automation - FastAPI Backend
Wraps all processing functions from app.py and exposes them as REST endpoints.
Run with: uvicorn api:app --reload --port 8000
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import numpy as np
from io import BytesIO
import json
import warnings
warnings.filterwarnings('ignore')

# ── Import all processing functions from app.py ──────────────────────────────
from app import (
    df_format1, df_format2, df_format3, df_format4,
    regression_analysis,
    interpolate_col, extrapolate_col,
    pivot_with_assumptions,
    advanced_cluster_analysis,
)

app = FastAPI(title="GFLS Automation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory session store (replace with Redis/DB for production) ────────────
sessions: dict = {}


def _safe_list(arr):
    """Convert numpy array to plain Python list (handles numpy int64 etc.)."""
    return [v.item() if hasattr(v, "item") else v for v in arr]


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce the 'value' column to float64, turning anything unparseable into NaN.
    Also coerces 'year' to int where possible.
    Call this right after format processing, before storing in session,
    so that pivot_with_assumptions(..).mean() never hits an object-dtype column.
    """
    df = df.copy()
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Upload & Preview
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/preview-columns")
async def preview_columns(
    file: UploadFile = File(...),
    file_type: str = Form(...),       # "Excel" | "CSV"
    sheet_name: str = Form("Sheet1"),
):
    """
    Return raw column names and first 10 rows from an uploaded file.
    Called immediately on file drop — before any format is chosen.
    """
    contents = await file.read()
    buf = BytesIO(contents)
    try:
        if file_type == "Excel":
            df_full = pd.read_excel(buf, sheet_name=sheet_name)
        else:
            df_full = pd.read_csv(buf)

        df_preview = df_full.head(10)
        return {
            "columns":    df_full.columns.tolist(),
            "preview":    df_preview.replace({np.nan: None}).to_dict(orient="records"),
            "total_rows": int(len(df_full)),
            "total_cols": int(len(df_full.columns)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Apply Format
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form(...),          # "Excel" | "CSV"
    sheet_name: str = Form("Sheet1"),
    format_num: int = Form(...),         # 1 | 2 | 3 | 4
    column_mapping: Optional[str] = Form(None),  # JSON string for format 1
    session_id: str = Form(...),
):
    """
    Apply a format transformation to the uploaded file and store in session.
    Returns a JSON preview and shape info — mirroring the Streamlit
    "Formatted Data" preview shown after clicking a Format button.
    """
    contents = await file.read()
    buf = BytesIO(contents)

    try:
        mapping = json.loads(column_mapping) if column_mapping else None

        if format_num == 1:
            df = df_format1(buf, sheet_name=sheet_name,
                            column_mapping=mapping,
                            is_excel=(file_type == "Excel"))
        elif format_num == 2:
            df = df_format2(buf, sheet_name=sheet_name,
                            is_excel=(file_type == "Excel"))
        elif format_num == 3:
            df = df_format3(buf, sheet_name=sheet_name,
                            is_excel=(file_type == "Excel"))
        elif format_num == 4:
            df = df_format4(buf, sheet_name=sheet_name,
                            is_excel=(file_type == "Excel"))
        else:
            raise HTTPException(status_code=400, detail="Invalid format_num")

        # Coerce value/year to numeric BEFORE saving to session.
        # Prevents "agg function failed [how->mean, dtype->object]" when
        # pivot_with_assumptions() calls .mean() on the value column.
        df = _coerce_numeric(df)

        # Persist formatted df to session
        sessions[session_id] = {"df": df}

        # Pre-compute pivot feature names for the clustering step
        pivot_features = []
        if "metric" in df.columns and "country" in df.columns and "year" in df.columns:
            try:
                available_years = sorted(df["year"].dropna().unique().tolist())
                sample_year = (
                    2023 if 2023 in available_years
                    else (max(available_years) if available_years else 2023)
                )
                pdf_sample = pivot_with_assumptions(df, sample_year)
                if not pdf_sample.empty:
                    skip = {"source", "assumption", "country", "Country", "COUNTRY"}
                    pivot_features = [c for c in pdf_sample.columns if c not in skip]
                else:
                    pivot_features = _safe_list(df["metric"].unique())
            except Exception as e:
                print(f"Pivot feature pre-computation error: {e}")
                pivot_features = _safe_list(df["metric"].unique()) if "metric" in df.columns else []

        return {
            "rows":           int(df.shape[0]),
            "cols":           int(df.shape[1]),
            "columns":        df.columns.tolist(),
            "countries":      _safe_list(df["country"].unique()) if "country" in df.columns else [],
            "metrics":        _safe_list(df["metric"].unique())  if "metric"  in df.columns else [],
            "pivot_features": pivot_features,
            "available_years": (
                sorted(_safe_list(df["year"].dropna().unique()))
                if "year" in df.columns else []
            ),
            "preview": df.head(10).replace({np.nan: None}).to_dict(orient="records"),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
