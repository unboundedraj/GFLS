import { useState } from "react";
import { Alert, SelectField, InputField, Label, Spinner, StatBox } from "./ui";
import { REGRESSION_METHODS, API_BASE } from "../constants";
import { apiFetch } from "../utils/api";

export function StepRegression({ sessionId, uploadResult, onDone }) {
  const countries = uploadResult?.countries || [];
  const metrics = uploadResult?.metrics || [];
  const [country, setCountry] = useState(countries[0] || "");
  const [metric, setMetric] = useState(metrics[0] || "");
  const [method, setMethod] = useState("linear");
  const [targetYear, setTargetYear] = useState(2025);
  const [polyOrder, setPolyOrder] = useState(2);
  const [alpha, setAlpha] = useState(1.0);
  const [C, setC] = useState(1.0);
  const [hiddenLayers, setHiddenLayers] = useState("10");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [predAdded, setPredAdded] = useState(false);
  const [addLoading, setAddLoading] = useState(false);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    setPrediction(null);
    try {
      const d = await apiFetch("/regression/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          country,
          metric,
          target_year: targetYear,
          method,
          poly_order: polyOrder,
          alpha,
          C,
          hidden_layers: hiddenLayers,
        }),
      });
      setPrediction(d);
      setPredAdded(false);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddPrediction = async () => {
    if (!prediction) return;
    setAddLoading(true);
    try {
      await apiFetch("/regression/add-prediction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          country: prediction.country,
          metric: prediction.metric,
          year: prediction.year,
          value: prediction.predicted_value,
        }),
      });
      setPredAdded(true);
      onDone?.();
    } catch (e) {
      setError(e.message);
    } finally {
      setAddLoading(false);
    }
  };

  if (!uploadResult) return <Alert type="warn">Complete Step 1 before proceeding.</Alert>;

  return (
    <>
      <div className="section-title">Regression Analysis</div>
      <div className="section-sub">Fit a model on historical data and predict future values</div>
      <div className="two-col">
        <div className="card">
          <div className="card-title">Filter</div>
          {countries.length > 0 ? (
            <SelectField label="Country" options={countries} value={country} onChange={setCountry} />
          ) : (
            <InputField label="Country" value={country} onChange={setCountry} placeholder="e.g. Germany" />
          )}
          {metrics.length > 0 ? (
            <SelectField label="Metric" options={metrics} value={metric} onChange={setMetric} />
          ) : (
            <InputField label="Metric" value={metric} onChange={setMetric} placeholder="e.g. GDP" />
          )}
        </div>
        <div className="card">
          <div className="card-title">Target Year</div>
          <InputField
            label="Predict for Year"
            type="number"
            value={targetYear}
            onChange={setTargetYear}
            min={1900}
            max={2200}
            step={1}
          />
        </div>
      </div>
      <div className="card">
        <div className="card-title">Regression Method</div>
        <div className="method-grid">
          {REGRESSION_METHODS.map((m) => (
            <button
              key={m}
              className={`method-chip${method === m ? " selected" : ""}`}
              onClick={() => setMethod(m)}
            >
              {m.replace(/_/g, " ")}
            </button>
          ))}
        </div>
        {method === "polynomial" && (
          <div style={{ maxWidth: 280 }}>
            <Label>Polynomial Order</Label>
            <div className="slider-row">
              <input
                type="range"
                className="slider"
                min={2}
                max={5}
                step={1}
                value={polyOrder}
                onChange={(e) => setPolyOrder(Number(e.target.value))}
              />
              <span className="slider-val">{polyOrder}</span>
            </div>
          </div>
        )}
        {["ridge", "lasso"].includes(method) && (
          <div style={{ maxWidth: 280 }}>
            <InputField label="Alpha" type="number" value={alpha} onChange={setAlpha} min={0} step={0.1} />
          </div>
        )}
        {["svm", "logistic"].includes(method) && (
          <div style={{ maxWidth: 280 }}>
            <InputField label="C" type="number" value={C} onChange={setC} min={0} step={0.1} />
          </div>
        )}
        {method === "neural_network" && (
          <div style={{ maxWidth: 280 }}>
            <InputField
              label="Hidden Layer Sizes (comma-sep)"
              value={hiddenLayers}
              onChange={setHiddenLayers}
              placeholder="10,20,10"
            />
          </div>
        )}
        {error && <Alert type="error">{error}</Alert>}
        <div className="btn-row" style={{ marginTop: 20 }}>
          <button className="btn btn-primary" onClick={handlePredict} disabled={loading}>
            {loading ? (
              <>
                <Spinner /> Running…
              </>
            ) : (
              "Run Prediction →"
            )}
          </button>
        </div>
      </div>

      {prediction && (
        <div className="prediction-box">
          <div style={{ fontSize: 11, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>
            Predicted Value
          </div>
          <div className="prediction-value">{Number(prediction.predicted_value).toFixed(4)}</div>
          <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 6 }}>
            {prediction.country} · {prediction.metric} · {prediction.year} · {prediction.method}
          </div>
          <div className="btn-row" style={{ marginTop: 16 }}>
            {!predAdded ? (
              <button className="btn btn-secondary" onClick={handleAddPrediction} disabled={addLoading}>
                {addLoading ? (
                  <>
                    <Spinner /> Adding…
                  </>
                ) : (
                  "+ Add to Data Table"
                )}
              </button>
            ) : (
              <Alert type="success">Prediction added to the data table.</Alert>
            )}
            <button
              className="btn btn-success"
              onClick={() =>
                window.open(`${API_BASE}/download/${sessionId}?filename=data_with_predictions.xlsx`)
              }
            >
              📥 Download Data Table
            </button>
          </div>
        </div>
      )}

      {/* <div
        className="btn-row"
        style={{ marginTop: 32, paddingTop: 20, borderTop: "1px solid var(--border)" }}
      >
        <button className="btn btn-primary" onClick={() => onDone?.()}>
          Proceed to Clustering →
        </button>
      </div> */}
    </>
  );
}
