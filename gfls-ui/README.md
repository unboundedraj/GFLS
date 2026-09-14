# gfls-ui

React + Vite front end for GFLS Automation. It guides the user through upload, year correction,
regression, clustering and KNN classification, calling the FastAPI backend in the repository root.

## Scripts

```bash
npm install      # install dependencies
npm run dev      # dev server on http://localhost:5173
npm run build    # production build into dist/
npm run preview  # serve the production build
npm run lint     # ESLint
```

## Configuration

The backend URL defaults to `http://localhost:8000`. Override it with `VITE_API_BASE` in
`.env.local` (see `.env.example`).

## Structure

```
src/
  App.jsx               step navigation and shared state
  constants.js          API URL, steps, method lists
  styles/               global styles (injected by App)
  utils/api.js          fetch wrapper with error handling
  utils/excel.js        client-side Excel preview (SheetJS, lazy-loaded)
  components/
    StepUpload.jsx          1 · file upload, preview, format + column mapping
    StepYearCorrection.jsx  2 · interpolation / extrapolation
    StepRegression.jsx      3 · regression prediction
    StepClustering.jsx      4 · K-Means clustering
    StepKNN.jsx             5 · KNN classification
    ui/                     small presentational components
```
