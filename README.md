# GFLS Automation

A data-processing and machine-learning toolkit for country-level indicators (GDP, population,
life expectancy, …). It takes messy spreadsheets in several layouts, normalises them into one
long format, fills gaps, forecasts values and groups countries by similarity.

The workflow has five steps:

| # | Step | What it does |
|---|------|--------------|
| 1 | **Data upload** | Reads Excel/CSV in 4 layouts and converts them to `country, year, metric, value, source, assumption` |
| 2 | **Year correction** | Fills missing values for a reference year by interpolation or extrapolation (CAGR, regression, moving-average growth, ARIMA) |
| 3 | **Regression** | Predicts a metric for a future year with linear, polynomial, ridge, lasso, logistic, decision tree, random forest, SVM or neural-network models |
| 4 | **Clustering** | Weighted K-Means on countries with complete data, with silhouette score and elbow curve |
| 5 | **KNN classification** | Assigns countries that are missing one metric to the nearest cluster |

## Architecture

```
┌──────────────────────┐   REST/JSON    ┌──────────────────────┐
│  gfls-ui (React +    │ ─────────────▶ │  api.py (FastAPI)    │
│  Vite, port 5173)    │ ◀───────────── │  port 8000           │
└──────────────────────┘                └──────────┬───────────┘
                                                   │ imports
                                        ┌──────────▼───────────┐
                                        │  app.py              │
                                        │  parsing, ML logic + │
                                        │  Streamlit UI        │
                                        └──────────────────────┘
```

- **`app.py`** – all processing functions (format parsers, interpolation/extrapolation,
  regression, clustering). Also runs on its own as a Streamlit app.
- **`api.py`** – FastAPI backend that wraps `app.py` and keeps per-session data in memory.
- **`gfls-ui/`** – React front end that walks through the five steps.

## Input formats

| Format | Layout | Example columns |
|--------|--------|-----------------|
| 1 | Already long, different labels (map them in the UI) | `Nation, Yr, Indicator, Amount, …` |
| 2 | One row per country + parameter, years as columns | `Country, Parameter, Y1 2015, Y2 2016, …` |
| 3 | One row per country + year, metrics as columns | `Country, Year, GDP per capita, Population, …` |
| 4 | One row per country, year inside metric labels | `Country, GDP per capita (2021), …` |

Ready-made examples of every layout (CSV and Excel) are in [`sample_data/`](sample_data/).
Regenerate them with `python scripts/generate_sample_data.py`.

## Getting started

Requirements: **Python 3.10+** and **Node.js 20+**.

### 1. Backend

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

uvicorn api:app --reload --port 8000
```

Interactive API docs: http://localhost:8000/docs

### 2. Front end

```bash
cd gfls-ui
npm install
npm run dev
```

Open http://localhost:5173 and upload a file from `sample_data/`.

If port 8000 is already in use, start the API on another port and point the UI at it:

```bash
uvicorn api:app --reload --port 8001
# gfls-ui/.env.local
VITE_API_BASE=http://127.0.0.1:8001
```

### Streamlit UI (optional)

The original single-page interface is still available:

```bash
streamlit run app.py
```

## API reference

| Method | Path | Description |
|--------|------|-------------|
| POST | `/preview-columns` | Column names and first rows of an uploaded file |
| POST | `/upload` | Apply format 1–4 and store the result in the session |
| GET  | `/download/{session_id}` | Current session data as Excel |
| POST | `/year-correction` | Interpolate / extrapolate missing values for a reference year |
| POST | `/regression/predict` | Predict a metric for a target year |
| POST | `/regression/add-prediction` | Append a prediction to the session data |
| POST | `/clustering/run` | Weighted K-Means clustering |
| POST | `/clustering/knn` | KNN classification of partial-data countries |
| GET  | `/clustering/download/{session_id}` | Clustering results as CSV |
| POST | `/clustering/diagnose/{session_id}` | Debug info about pivoting and available features |

Every request carries a `session_id`; the UI generates one per browser tab.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The suite uploads every sample format (CSV and Excel) and exercises each interpolation,
extrapolation and regression method, clustering, KNN and the download endpoints.

Front-end checks:

```bash
cd gfls-ui
npm run lint
npm run build
```

## Notes

- Sessions live in memory, so they are lost when the API restarts. Use Redis or a database
  for anything beyond local use.
- CORS is open (`allow_origins=["*"]`) for local development; restrict it before deploying.

## About

GFLS Automation was built as a team project for our Bachelor of Engineering final year.
