


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


@app.get("/download/{session_id}")
def download_excel(session_id: str, filename: str = "data.xlsx"):
    """Stream the current session DataFrame as an Excel file."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    df = session["df"]
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Formatted_Data")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Year Correction (Interpolate / Extrapolate)
# ─────────────────────────────────────────────────────────────────────────────

class YearCorrectionRequest(BaseModel):
    session_id: str
    ref_year: int = 2023
    fix_method: str = "Interpolate"    # "Interpolate" | "Extrapolate"
    interp_method: str = "linear"
    poly_order: int = 2
    ma_window: int = 3


@app.post("/year-correction")
async def year_correction(req: YearCorrectionRequest):
    """
    Pivot the session DataFrame to detect missing values, then interpolate
    or extrapolate them.  Mirrors the Streamlit year_correction_section():

      1. pivot_with_assumptions(df, ref_year)  → pivot table (country as INDEX)
      2. interpolate_col / extrapolate_col     → filled pivot (country still as INDEX)
      3. reset_index() + melt                 → back to long format
      4. concat with original df              → corrected long df saved to session

    Returns a preview of the corrected long DataFrame.
    """
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please re-upload your file.",
        )

    df: pd.DataFrame = session["df"]

    try:
        # Ensure value/year are numeric before pivoting (guards against
        # object-dtype values that cause .mean() to fail during pivot).
        df = _coerce_numeric(df)

        # ── 1. Pivot ────────────────────────────────────────────────────────
        pdf = pivot_with_assumptions(df, req.ref_year)

        original_missing = int(pdf.isnull().sum().sum())

        # ── 2. Fill missing values ───────────────────────────────────────────
        # IMPORTANT: interpolate_col / extrapolate_col expect `columns='None'`
        # as their third positional arg.  Both functions return a pivot DataFrame
        # with country still in the INDEX (not as a column).
        if req.fix_method == "Interpolate":
            result = interpolate_col(
                pdf, df,
                peak_year=req.ref_year,
                columns="None",
                method=req.interp_method,
            )
        else:
            result = extrapolate_col(
                pdf, df,
                peak_year=req.ref_year,
                columns="None",
                method=req.interp_method,
                order=req.poly_order,
                ma_window=req.ma_window,
            )

        final_missing = int(result.isnull().sum().sum())

        # ── 3. Melt corrected pivot back to long format ──────────────────────
        # `result` has country in the INDEX.  Reset it first so it becomes a column.
        result_reset = result.reset_index()   # country is now a proper column

        # Identify id-variable columns that exist after reset_index
        id_candidates = ["country", "source", "assumption"]
        id_vars = [c for c in id_candidates if c in result_reset.columns]

        # Everything else is a metric column
        metric_cols = [c for c in result_reset.columns if c not in id_vars]

        long_df = result_reset.melt(
            id_vars=id_vars,
            value_vars=metric_cols,
            var_name="metric",
            value_name="value",
        )
        long_df["year"] = req.ref_year

        # Re-order to canonical column order, filling any missing cols with None
        for col in ["country", "year", "metric", "value", "source", "assumption"]:
            if col not in long_df.columns:
                long_df[col] = None
        long_df = long_df[["country", "year", "metric", "value", "source", "assumption"]]

        # ── 4. Concat + sort, save back to session ───────────────────────────
        corrected = (
            pd.concat([df, long_df], ignore_index=True)
            .sort_values(["country", "year", "metric"])
            .reset_index(drop=True)
        )
        sessions[req.session_id]["df"] = corrected

        return {
            "original_missing": original_missing,
            "final_missing":    final_missing,
            "values_filled":    original_missing - final_missing,
            "shape": {
                "rows": int(corrected.shape[0]),
                "cols": int(corrected.shape[1]),
            },
            "preview": corrected.head(10).replace({np.nan: None}).to_dict(orient="records"),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Regression
# ─────────────────────────────────────────────────────────────────────────────

class RegressionRequest(BaseModel):
    session_id: str
    country: str
    metric: str
    target_year: int
    method: str = "linear"
    poly_order: int = 2
    alpha: float = 1.0
    C: float = 1.0
    hidden_layers: str = "10"   # comma-separated


class AddPredictionRequest(BaseModel):
    session_id: str
    country: str
    metric: str
    year: int
    value: float


@app.post("/regression/predict")
async def predict(req: RegressionRequest):
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    df: pd.DataFrame = session["df"]
    filtered = (
        df[(df["country"] == req.country) & (df["metric"] == req.metric)]
        .sort_values("year")
    )

    if len(filtered) < 2:
        raise HTTPException(
            status_code=400,
            detail="Not enough data points for regression (need ≥ 2).",
        )

    years  = filtered["year"].values
    values = filtered["value"].values

    try:
        hidden_layer_sizes = tuple(int(x) for x in req.hidden_layers.split(","))
    except Exception:
        hidden_layer_sizes = (10,)

    try:
        y_pred = regression_analysis(
            years=years,
            values=values,
            target_year=req.target_year,
            method=req.method,
            poly_order=req.poly_order,
            alpha=req.alpha,
            C=req.C,
            hidden_layer_sizes=hidden_layer_sizes,
        )
        return {
            "predicted_value": float(y_pred),
            "country":  req.country,
            "metric":   req.metric,
            "year":     req.target_year,
            "method":   req.method,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/regression/add-prediction")
async def add_prediction(req: AddPredictionRequest):
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    df: pd.DataFrame = session["df"]
    new_row = pd.DataFrame([{
        "country":    req.country,
        "year":       req.year,
        "metric":     req.metric,
        "value":      req.value,
        "source":     "regression_prediction",
        "assumption": "",
    }])
    sessions[req.session_id]["df"] = pd.concat([df, new_row], ignore_index=True)
    return {"status": "added", "rows": int(sessions[req.session_id]["df"].shape[0])}


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Clustering & KNN
# ─────────────────────────────────────────────────────────────────────────────

class ClusterRequest(BaseModel):
    session_id: str
    ref_year: int = 2023
    selected_features: List[str]
    n_clusters: int = 3
    max_clusters: int = 6
    feature_weights: dict = {}


class KNNRequest(BaseModel):
    session_id: str
    ref_year: int = 2023
    selected_features: List[str]
    feature_weights: dict = {}


@app.post("/clustering/run")
async def run_clustering(req: ClusterRequest):
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    df: pd.DataFrame = session["df"]

    try:
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score

        # Validate required columns
        required_cols = ["country", "metric", "year", "value"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Data missing required columns: {missing_cols}",
            )

        # Use latest available year if requested year not present
        available_years = sorted(_safe_list(df["year"].dropna().unique()))
        ref_year = (
            req.ref_year
            if req.ref_year in available_years
            else (max(available_years) if available_years else 2023)
        )

        pdf = pivot_with_assumptions(df, ref_year)
        if pdf.empty:
            raise HTTPException(
                status_code=400,
                detail=f"No data found for year {ref_year}. Available: {available_years}",
            )

        pdf.reset_index(inplace=True)

        country_col = next(
            (c for c in ["country", "Country", "COUNTRY"] if c in pdf.columns), None
        )

        available_features = [
            c for c in pdf.columns
            if c not in ["country", "Country", "COUNTRY", "source", "assumption"]
        ]
        if not available_features:
            raise HTTPException(status_code=400, detail="No metric features found in pivoted data.")

        valid_features = [f for f in req.selected_features if f in available_features]
        if not valid_features:
            raise HTTPException(
                status_code=400,
                detail=f"Selected features not in data. Available: {available_features}",
            )

        # Coerce all selected feature columns to float (defensive guard —
        # in case any metric value slipped through as object dtype).
        for feat in valid_features:
            pdf[feat] = pd.to_numeric(pdf[feat], errors="coerce")

        # Split into complete / partial / insufficient
        missing_counts    = pdf[valid_features].isna().sum(axis=1)
        complete_data     = pdf[missing_counts == 0].copy()
        partial_data      = pdf[missing_counts == 1].copy()
        insufficient_data = pdf[missing_counts  > 1].copy()

        if len(complete_data) < 3:
            raise HTTPException(
                status_code=400,
                detail="Need at least 3 countries with complete data for clustering.",
            )

        # Standardise + weight
        scaler   = StandardScaler()
        std_data = scaler.fit_transform(complete_data[valid_features])
        std_df   = pd.DataFrame(std_data, columns=valid_features)
        for feat in valid_features:
            std_df[feat] *= req.feature_weights.get(feat, 1.0)

        weighted = std_df.values
        kmeans   = KMeans(n_clusters=req.n_clusters, random_state=42, n_init=10)
        labels   = kmeans.fit_predict(weighted)
        complete_data = complete_data.copy()
        complete_data["Cluster"] = labels

        sil     = float(silhouette_score(weighted, labels))
        k_range = range(1, min(req.max_clusters + 1, len(complete_data)) + 1)
        inertia = []
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(weighted)
            inertia.append(float(km.inertia_))

        # Persist clustering state for KNN
        sessions[req.session_id]["clustering"] = {
            "complete_data":     complete_data,
            "partial_data":      partial_data,
            "weighted_data":     weighted,
            "scaler":            scaler,
            "cluster_labels":    labels,
            "selected_features": valid_features,
            "feature_weights":   req.feature_weights,
            "country_col":       country_col,
        }

        cluster_cols = [country_col, "Cluster"] if country_col else ["Cluster"]
        return {
            "silhouette_score":       sil,
            "countries_clustered":    int(len(complete_data)),
            "partial_countries":      int(len(partial_data)),
            "insufficient_countries": int(len(insufficient_data)),
            "features_used":          int(len(valid_features)),
            "elbow": {"k": list(k_range), "inertia": inertia},
            "clusters": (
                complete_data[cluster_cols]
                .replace({np.nan: None})
                .to_dict(orient="records")
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clustering/knn")
async def run_knn(req: KNNRequest):
    session = sessions.get(req.session_id)
    if not session or "clustering" not in session:
        raise HTTPException(status_code=404, detail="Please run clustering first.")

    clust = session["clustering"]

    try:
        from sklearn.neighbors import KNeighborsClassifier

        complete    = clust["complete_data"]
        partial     = clust["partial_data"]
        features    = clust["selected_features"]
        labels      = clust["cluster_labels"]
        country_col = clust["country_col"]
        X_train     = clust["weighted_data"]

        knn = KNeighborsClassifier(n_neighbors=min(5, len(complete)))
        knn.fit(X_train, labels)

        results = []
        for _, row in partial.iterrows():
            missing_feat = [f for f in features if pd.isna(row[f])]
            if not missing_feat:
                continue
            missing_feat = missing_feat[0]

            imputed = [
                row[f] if not pd.isna(row[f]) else float(complete[f].mean())
                for f in features
            ]
            imputed_scaled = clust["scaler"].transform([imputed])[0]
            for i, feat in enumerate(features):
                imputed_scaled[i] *= req.feature_weights.get(feat, 1.0)

            probs      = knn.predict_proba([imputed_scaled])[0]
            pred_class = int(knn.predict([imputed_scaled])[0])
            confidence = float(max(probs))

            results.append({
                "country":           row[country_col] if country_col else "Unknown",
                "predicted_cluster": pred_class,
                "confidence":        round(confidence, 4),
                "missing_feature":   missing_feat,
            })

        return {"knn_results": results, "classified": len(results)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/clustering/download/{session_id}")
def download_clustering(session_id: str):
    session = sessions.get(session_id)
    if not session or "clustering" not in session:
        raise HTTPException(status_code=404, detail="No clustering results found.")
    df = session["clustering"]["complete_data"]
    buf = BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="clustering_results.csv"'},
    )


# ── Debug endpoint ────────────────────────────────────────────────────────────
@app.post("/clustering/diagnose/{session_id}")
async def diagnose_clustering(session_id: str, ref_year: int = 2023):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    df: pd.DataFrame = session["df"]
    diagnosis: dict = {
        "raw_data": {
            "shape":   list(df.shape),
            "columns": df.columns.tolist(),
        },
        "required_columns_present": all(
            c in df.columns for c in ["country", "metric", "year", "value"]
        ),
    }

    if "year" in df.columns:
        available_years = sorted(_safe_list(df["year"].dropna().unique()))
        diagnosis["available_years"] = available_years
        diagnosis["requested_year"]  = ref_year
        diagnosis["year_in_data"]    = ref_year in available_years

    try:
        pdf = pivot_with_assumptions(df, ref_year)
        diagnosis["pivot"] = {
            "shape":      list(pdf.shape),
            "columns":    pdf.columns.tolist(),
            "index_name": pdf.index.name,
            "empty":      bool(pdf.empty),
        }
        if not pdf.empty:
            skip = {"source", "assumption"}
            diagnosis["available_features"] = [c for c in pdf.columns if c not in skip]
            diagnosis["pivot_preview"] = (
                pdf.head(3).replace({np.nan: None}).to_dict(orient="records")
            )
    except Exception as e:
        diagnosis["pivot_error"] = str(e)

    return diagnosis
