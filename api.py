


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
