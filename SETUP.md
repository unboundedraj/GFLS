# GFLS Automation — Full Stack Setup

## Files
- `app.py`       — your original Streamlit logic (all ML functions live here)
- `api.py`       — FastAPI backend that wraps app.py and exposes REST endpoints
- `gfls_ui.jsx`  — React frontend that calls the API

---

## 1. Install Python dependencies

```bash
pip install fastapi uvicorn python-multipart openpyxl scikit-learn pandas numpy scipy
```

If you use ARIMA extrapolation:
```bash
pip install statsmodels
```

---

## 2. Put all 3 files in the same folder

```
project/
  app.py
  api.py
  gfls_ui.jsx   ← used separately (see Step 4)
```

---

## 3. Start the FastAPI backend

```bash
uvicorn api:app --reload --port 8000
```

Visit http://localhost:8000/docs to see all endpoints in the auto-generated Swagger UI.

---

## 4. Run the React frontend

**Option A — Paste into Claude.ai Artifacts**
Open claude.ai, create a new artifact, paste the contents of `gfls_ui.jsx`.
The app will run in the sandbox. Make sure your backend is running and accessible.

**Option B — Vite / Create React App**
```bash
npm create vite@latest gfls-ui -- --template react
cd gfls-ui
# Replace src/App.jsx with gfls_ui.jsx content
npm run dev
```

---

## 5. API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | `/preview-columns` | Get column names from uploaded file |
| POST | `/upload` | Upload + apply format (1–4), stores in session |
| POST | `/year-correction` | Interpolate or extrapolate missing values |
| GET  | `/download/{session_id}` | Download current session data as Excel |
| POST | `/regression/predict` | Run regression and predict a value |
| POST | `/regression/add-prediction` | Append prediction to session data |
| POST | `/clustering/run` | Run K-Means clustering |
| POST | `/clustering/knn` | Run KNN classification on partial-data countries |
| GET  | `/clustering/download/{session_id}` | Download clustering results as CSV |

---

## Notes

- **Sessions** are stored in memory (Python dict). For production, replace with Redis or a database.
- **CORS** is open (`allow_origins=["*"]`). Restrict this in production.
- The `session_id` is generated randomly per browser session in the React UI — it's passed with every request so the backend knows which data to use.
