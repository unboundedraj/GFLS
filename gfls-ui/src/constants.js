export const API_BASE = "http://localhost:8000";

export const STEPS = ["Data Upload", "Year Correction", "Regression", "Clustering", "KNN Classification"];

export const FORMATS = [
  { id: 1, label: "Format 1", desc: "Same form, different labels" },
  { id: 2, label: "Format 2", desc: "Years in different columns" },
  { id: 3, label: "Format 3", desc: "Year in rows, metrics in columns" },
  { id: 4, label: "Format 4", desc: "Metric in columns with labelled years" },
];

export const REGRESSION_METHODS = [
  "linear", "polynomial", "ridge", "lasso",
  "logistic", "decision_tree", "random_forest", "svm", "neural_network",
];

export const COLUMN_FIELDS = ["country", "year", "metric", "value", "source", "assumption"];

export const INTERP_METHODS = [
  "linear", "polynomial", "spline", "nearest_neighbour", "piecewise_constant", "logarithmic"
];
