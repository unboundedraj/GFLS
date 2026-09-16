# About GFLS Automation

Reference for explaining this project: the problem it solves, what it is,
the tech stack, the concepts behind it, and how to run and deploy it.

## 1. What issue does it solve

Organizations working with country-level statistics (GDP, population, life expectancy,
CO2 emissions, etc.) pull data from multiple sources — World Bank exports, UN reports,
internal trackers — and every source formats its spreadsheet differently: some have years
as columns, some have years as rows, some bury the year inside the column header itself.
On top of that, real-world datasets almost always have gaps — a country might be missing
GDP data for 2023, or missing one indicator entirely. Analysts were manually reformatting
these files and eyeballing what to do about missing values before they could even start
analysis.

This project automates that entire pre-analysis pipeline: normalize any of 4 common
layouts into one consistent schema, fill in missing values using statistically
appropriate methods, forecast future values, and group similar countries together —
without a human manually reshaping spreadsheets each time.

## 2. What the project is

A full-stack web application with a 5-step guided workflow:

1. **Upload** — detect and normalize one of 4 spreadsheet layouts into a long-format
   table (`country, year, metric, value, source, assumption`)
2. **Year correction** — fill missing values for a reference year via interpolation or
   extrapolation
3. **Regression** — forecast a metric into a future year using one of 9 ML models
4. **Clustering** — group countries with complete data using weighted K-Means
5. **KNN classification** — assign countries with partial data to the nearest cluster

A React frontend walks through those steps, talking to a FastAPI backend over REST.
A legacy Streamlit single-page version is also available as a self-contained fallback UI.
There's also a standalone data-quality/sparsity-analysis module that flags how usable a
dataset is before any ML runs on it.

## 3. Tech stack

- **Backend**: Python, FastAPI (REST API), Uvicorn (ASGI server), Pydantic (request
  validation)
- **Data/ML**: pandas, numpy, scipy, scikit-learn, statsmodels
- **Frontend**: React 19, Vite (build tool/dev server)
- **Secondary UI**: Streamlit, matplotlib, seaborn
- **Testing**: pytest with FastAPI's TestClient

No containerization (no Dockerfile) and no CI pipeline exist yet — it's a local-dev tool,
not a deployed production service. Sessions live in an in-memory dict keyed by a UUID per
browser tab, not a database — a deliberate scope tradeoff for a local tool (see
Deployment below for what changes if this goes to production).

## 4. Is this backend-only?

No — it's full-stack, with backend and frontend decoupled over REST:

- **Backend** (FastAPI, Python): owns all data processing and ML. Runs on port 8000.
- **Frontend** (React + Vite): renders the 5-step wizard UI and calls the backend as
  JSON over HTTP. Runs on port 5173.
- **Streamlit alternative**: `app.py` can also run standalone (`streamlit run app.py`)
  as a single Python process that is both backend and frontend at once — no separate
  React app needed. Useful to know the toolkit doesn't strictly require the web stack.

## 5. Key concepts (likely interview questions)

### Interpolation vs. extrapolation

Both fill in missing values, but differ in *where* the gap is relative to known data:

- **Interpolation** fills a gap *between* two known points — e.g., you have GDP for 2018
  and 2020 but are missing 2019; interpolation estimates 2019 from the surrounding data.
  It's generally more reliable because the estimate is bounded by real observations on
  both sides.
  Methods implemented: linear, polynomial, spline, nearest-neighbor, piecewise-constant
  (forward-fill/back-fill), and a custom log-scale method (log-transform, interpolate
  linearly, exponentiate back — useful for metrics that grow exponentially, like GDP).

- **Extrapolation** projects *beyond* the known range — e.g., your latest data point is
  2023 and you want an estimate for 2024. It's riskier because it assumes the existing
  trend continues past the observed data.
  Methods implemented: CAGR (Compound Annual Growth Rate), linear regression, polynomial
  regression, moving-average growth rate, and ARIMA (AutoRegressive Integrated Moving
  Average — a classical time-series model from `statsmodels` that captures trend and
  autocorrelation).

### Regression models — what they are and where they come from

Regression predicts a **continuous value** (e.g., GDP in 2026) from input data. All 9
methods are implementations from **scikit-learn**, not hand-written from scratch — the
project's job is orchestrating which one runs and with what hyperparameters, not
reimplementing the algorithms:

| Method | scikit-learn class | Module |
|---|---|---|
| Linear regression | `LinearRegression` | `sklearn.linear_model` |
| Polynomial regression | `PolynomialFeatures` + `LinearRegression` | `sklearn.preprocessing` / `sklearn.linear_model` |
| Ridge regression | `Ridge` | `sklearn.linear_model` |
| Lasso regression | `Lasso` | `sklearn.linear_model` |
| Logistic regression | `LogisticRegression` | `sklearn.linear_model` |
| Decision tree | `DecisionTreeRegressor` | `sklearn.tree` |
| Random forest | `RandomForestRegressor` | `sklearn.ensemble` |
| SVM | `SVR` | `sklearn.svm` |
| Neural network | `MLPRegressor` | `sklearn.neural_network` |

**Package vs. library terminology**: scikit-learn is a *library* — a collection of
reusable, pre-built code you import and call. It's distributed and installed as a
*package* via pip (`pip install scikit-learn`). In everyday Python usage the two terms
are used almost interchangeably; "package" technically refers to the installable unit,
"library" to the body of code/functionality it provides.

Brief notes on each method, for follow-up questions:

- **Linear** — fits a straight line through the data.
- **Polynomial** — fits a curve of a chosen degree instead of a straight line.
- **Ridge** — linear regression plus an L2 penalty that shrinks coefficients, reducing
  overfitting when features are correlated.
- **Lasso** — linear regression plus an L1 penalty that can shrink coefficients to
  exactly zero, effectively doing feature selection.
- **Logistic** — actually a classifier, not a true regressor; included here on a
  binarized target as a demonstration option, not a core forecasting method.
- **Decision tree** — splits the data into branches based on threshold rules; captures
  non-linear patterns and is easy to interpret.
- **Random forest** — an ensemble of many decision trees averaged together, reducing the
  overfitting risk of a single tree.
- **SVM (Support Vector Machine)** — finds the best-fit curve within a margin of
  tolerance; robust to outliers.
- **Neural network (MLP)** — a multi-layer perceptron; layers of weighted connections
  that learn non-linear relationships. Most flexible, but needs more data to be reliable.

**Regularization** (the `alpha` parameter on Ridge/Lasso) is worth being ready to
explain on its own: it's a penalty term added to the loss function that discourages the
model from fitting noise too closely, trading a little training accuracy for better
generalization to unseen data.

### Clustering — what it is and where it comes from

**K-Means clustering** is an unsupervised algorithm that groups countries into `k`
clusters by minimizing the distance between each point and its cluster's center
(centroid), iterating until the assignment stabilizes. Also scikit-learn:

| Piece | scikit-learn class | Module |
|---|---|---|
| Clustering | `KMeans` | `sklearn.cluster` |
| Feature scaling | `StandardScaler` | `sklearn.preprocessing` |
| Dimensionality reduction | `PCA` | `sklearn.decomposition` |
| Cluster quality metric | `silhouette_score` | `sklearn.metrics` |
| Interpretability layer | `DecisionTreeClassifier` | `sklearn.tree` |

Supporting concepts:

- **Standardization** — features like GDP (in thousands) and life expectancy (in tens)
  are on very different scales, so features are standardized (mean 0, std 1) before
  clustering; otherwise a large-magnitude feature like GDP would dominate the distance
  calculation purely because of scale, not because it's actually more important.
- **Feature weighting** — weights are adjustable per feature rather than uniform, so a
  user can say "GDP should matter twice as much as population" for a given analysis.
- **Silhouette score** — ranges from -1 to 1, measuring how well-separated clusters are
  (how close a point is to its own cluster vs. the nearest other cluster). Higher is
  better.
- **Elbow method** — plots inertia (within-cluster sum of squared distances) against
  different values of `k`; the "elbow" is where adding more clusters stops meaningfully
  reducing inertia, used to pick a good `k`.
- **PCA** — when more than 2 features are selected, clusters can't be plotted directly,
  so PCA reduces the data to 2 dimensions (the directions of maximum variance) purely
  for visualization.
- **Interpretability** — after clustering, a `DecisionTreeClassifier` is trained on the
  same cluster labels just to extract human-readable rules (e.g., "if GDP per capita
  > $X, likely Cluster 2"). K-Means alone is a black box; this adds an explanation layer
  on top of it.

### KNN classification — what it is

**K-Nearest Neighbors (KNN)** is a supervised classification algorithm. Given a labeled
dataset — here, "which cluster does this country belong to" — classifying a new,
unlabeled point means looking at its `k` closest points by distance in feature space and
assigning the majority class among those neighbors. Implementation:
`KNeighborsClassifier` from `sklearn.neighbors`.

In this project, KNN is the mechanism behind Step 5: countries missing one indicator
can't be included in the original K-Means clustering (which requires complete feature
data), so instead they're classified against the already-formed clusters using the
features they do have, with a confidence score from `predict_proba`.

## 6. How to run the project

**Terminal 1 — Backend:**

```bash
python -m venv .venv
source .venv/Scripts/activate      # Git Bash on Windows
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd gfls-ui
npm install
npm run dev
```

Open `http://localhost:5173` and upload a file from `sample_data/` to walk through the
5-step flow. Interactive API docs are auto-generated by FastAPI at
`http://localhost:8000/docs`.

**Optional — Streamlit UI instead of React:**

```bash
source .venv/Scripts/activate
streamlit run app.py
```

## 7. How would this be deployed

Today the project is built for local development only: sessions are stored in-memory
and CORS is wide open (`allow_origins=["*"]`). To take it to production:

1. **Containerize the backend** with Docker; run Uvicorn (optionally behind Gunicorn
   with multiple workers) inside the container.
2. **Host the backend** on a platform like Render, Railway, Fly.io, or AWS
   ECS/Fargate — anywhere that can run a long-lived container and expose a port.
3. **Replace the in-memory session store with Redis or Postgres.** This is the main
   blocker to scaling past a single process: the current `dict` only exists inside one
   running instance, so sessions would break the moment there's more than one backend
   instance or a restart happens.
4. **Build and host the frontend separately** — `npm run build` produces static files
   deployable to Vercel, Netlify, or S3 + CloudFront, fully decoupled from the backend
   since they only communicate over REST.
5. **Lock down CORS** to the actual frontend's deployed domain instead of `*`.
6. **Point the frontend at the deployed API** via the `VITE_API_BASE` environment
   variable instead of `localhost`.
7. **Put both behind HTTPS** — most PaaS options handle TLS termination automatically.

The deployment story is straightforward specifically because backend and frontend are
already decoupled via a REST/JSON contract; the main engineering work would be swapping
the session store, not restructuring the app.
