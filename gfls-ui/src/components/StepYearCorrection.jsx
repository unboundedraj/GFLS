import { useState } from "react";
import { Alert, Checkbox, InputField, SelectField, Divider, Spinner, StatBox, DataTable } from "./ui";
import { INTERP_METHODS, API_BASE } from "../constants";
import { apiFetch } from "../utils/api";

export function StepYearCorrection({ sessionId, uploadResult, onDone }) {
  const [apply, setApply] = useState(false);
  const [refYear, setRefYear] = useState(2023);
  const [fixMethod, setFixMethod] = useState("Interpolate");
  const [interpMethod, setInterpMethod] = useState("linear");
  const [polyOrder, setPolyOrder] = useState(2);
  const [maWindow, setMaWindow] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    try {
      const d = await apiFetch("/year-correction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          ref_year: refYear,
          fix_method: fixMethod,
          interp_method: interpMethod,
          poly_order: polyOrder,
          ma_window: maWindow,
        }),
      });
      setResult(d);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (!uploadResult) return <Alert type="warn">Complete Step 1 before proceeding.</Alert>;

  return (
    <>
      <div className="section-title">Year Correction</div>
      <div className="section-sub">Optionally fill missing values via interpolation or extrapolation</div>

      <div className="card">
        <Checkbox checked={apply} onChange={(v) => { setApply(v); setResult(null); }}>
          Apply Year Correction (Optional)
        </Checkbox>

        {apply && (
          <>
            <InputField
              label="Reference Year"
              type="number"
              value={refYear}
              onChange={setRefYear}
              min={1900}
              max={2100}
              step={1}
            />
            <div className="card-title" style={{ marginTop: 8 }}>
              Fill Method
            </div>
            <div className="radio-group">
              {["Interpolate", "Extrapolate"].map((m) => (
                <button
                  key={m}
                  className={`radio-btn${fixMethod === m ? " selected" : ""}`}
                  onClick={() => setFixMethod(m)}
                >
                  {m}
                </button>
              ))}
            </div>
            <SelectField
              label={`${fixMethod} Method`}
              options={INTERP_METHODS}
              value={interpMethod}
              onChange={setInterpMethod}
            />
            {fixMethod === "Extrapolate" && (
              <div className="two-col">
                {interpMethod === "polynomial" && (
                  <InputField
                    label="Polynomial Order"
                    type="number"
                    value={polyOrder}
                    onChange={setPolyOrder}
                    min={1}
                    max={5}
                  />
                )}
                <InputField
                  label="Moving Average Window"
                  type="number"
                  value={maWindow}
                  onChange={setMaWindow}
                  min={1}
                  max={10}
                />
              </div>
            )}
            {error && <Alert type="error">{error}</Alert>}
            <div className="btn-row">
              <button className="btn btn-primary" onClick={handleRun} disabled={loading || !!result}>
                {loading ? (
                  <>
                    <Spinner /> Running…
                  </>
                ) : (
                  "Run Correction →"
                )}
              </button>
              <button className="btn btn-secondary" onClick={() => onDone(null)}>
                Skip
              </button>
            </div>
          </>
        )}

        {!apply && (
          <>
            <Alert type="info">No correction will be applied. Proceeding with raw formatted data.</Alert>
            <div className="btn-row">
              <button className="btn btn-primary" onClick={() => onDone(null)}>
                Continue →
              </button>
            </div>
          </>
        )}
      </div>

      {result && (
        <div className="card">
          <div className="card-title">Correction Summary</div>
          <div className="stat-grid">
            <StatBox label="Original Missing" value={result.original_missing} color="var(--danger)" />
            <StatBox label="Values Filled" value={result.values_filled} color="var(--success)" />
            <StatBox label="Remaining Missing" value={result.final_missing} color="var(--accent)" />
          </div>
          <DataTable rows={result.preview} />
          <div style={{ height: 1, background: "var(--border)", margin: "20px 0" }} />
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: 12,
            }}
          >
            <button
              className="btn btn-success"
              onClick={() =>
                window.open(
                  `${API_BASE}/download/${sessionId}?filename=corrected_data.xlsx`
                )
              }
            >
              📥 Download Corrected Data
            </button>
            <button className="btn btn-primary" onClick={() => onDone(result)}>
              Proceed to Regression →
            </button>
          </div>
        </div>
      )}
    </>
  );
}
