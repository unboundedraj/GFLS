import { useState, useEffect } from "react";
import { Alert, InputField, Label, Divider, Spinner, StatBox } from "./ui";
import { apiFetch } from "../utils/api";

export function StepKNN({ sessionId, uploadResult, clusteringResult }) {
  const availableFeatures =
    clusteringResult?.selectedFeatures ||
    uploadResult?.pivot_features ||
    uploadResult?.metrics ||
    [];

  const [knnYear, setKnnYear] = useState(clusteringResult?.clusterYear || 2023);
  const [selectedFeatures, setSelectedFeatures] = useState(
    clusteringResult?.selectedFeatures || []
  );
  const [weights, setWeights] = useState(clusteringResult?.weights || {});
  const [nNeighbors, setNNeighbors] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (clusteringResult?.selectedFeatures?.length && selectedFeatures.length === 0) {
      setSelectedFeatures(clusteringResult.selectedFeatures);
    }
    if (clusteringResult?.weights) {
      setWeights(clusteringResult.weights);
    }
    if (clusteringResult?.clusterYear) {
      setKnnYear(clusteringResult.clusterYear);
    }
  }, [clusteringResult]);

  const toggleFeature = (f) =>
    setSelectedFeatures((prev) =>
      prev.includes(f) ? prev.filter((x) => x !== f) : [...prev, f]
    );

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const d = await apiFetch("/clustering/knn", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          ref_year: knnYear,
          selected_features: selectedFeatures,
          feature_weights: weights,
        }),
      });
      setResult(d);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (!result?.knn_results?.length) return;
    const headers = Object.keys(result.knn_results[0]);
    const rows = result.knn_results.map((r) => headers.map((h) => r[h] ?? "").join(","));
    const csv = [headers.join(","), ...rows].join("\n");
    const a = document.createElement("a");
    a.href = "data:text/csv;charset=utf-8," + encodeURIComponent(csv);
    a.download = "knn_classification_results.csv";
    a.click();
  };

  if (!uploadResult)
    return <Alert type="warn">Complete Step 1 (Data Upload) before proceeding.</Alert>;

  if (!clusteringResult)
    return (
      <div className="card">
        <Alert type="warn">
          KNN Classification requires clustering to be run first. Go back to Step 4 and complete
          clustering — then return here.
        </Alert>
      </div>
    );

  return (
    <>
      <div className="section-title">KNN Classification</div>
      <div className="section-sub">
        Classify partial-data countries using K-Nearest Neighbours trained on cluster assignments
      </div>

      <div className="card">
        <div className="card-title">Clustering Context</div>
        <div className="stat-grid">
          <StatBox label="Countries Clustered" value={clusteringResult.countries_clustered} color="var(--success)" />
          <StatBox label="Partial Countries" value={clusteringResult.partial_countries} color="var(--info)" />
          <StatBox label="Silhouette Score" value={clusteringResult.silhouette_score?.toFixed(3)} />
        </div>
        <Alert type="info">
          The KNN model is already trained on the {clusteringResult.countries_clustered} countries
          clustered in Step 4. It will now classify the {clusteringResult.partial_countries} partial-data
          countries that were held aside.
        </Alert>
      </div>

      <div className="card">
        <div className="card-title">Configuration</div>

        <div className="two-col">
          <div>
            <InputField
              label="Reference Year"
              type="number"
              value={knnYear}
              onChange={setKnnYear}
              min={1900}
              max={2100}
              step={1}
            />
          </div>
          <div>
            <Label>K (Neighbours)</Label>
            <div className="slider-row" style={{ marginTop: 6 }}>
              <input
                type="range"
                className="slider"
                min={1}
                max={10}
                step={1}
                value={nNeighbors}
                onChange={(e) => setNNeighbors(Number(e.target.value))}
              />
              <span className="slider-val">{nNeighbors}</span>
            </div>
            <div style={{ fontSize: 10, color: "var(--muted)", marginTop: 4 }}>
              Note: capped at number of clustered countries in the backend.
            </div>
          </div>
        </div>

        <Divider />

        <div className="card-title">Features</div>
        <Alert type="info">
          Pre-filled from your clustering configuration. Adjust only if needed — features must match
          those used during clustering.
        </Alert>
        <div className="tag-list" style={{ marginTop: 12 }}>
          {availableFeatures.map((f) => (
            <button
              key={f}
              className={`tag${selectedFeatures.includes(f) ? " active" : ""}`}
              onClick={() => toggleFeature(f)}
            >
              {f}
            </button>
          ))}
        </div>

        {selectedFeatures.length >= 2 && (
          <>
            <Divider />
            <div className="card-title">Feature Weights</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 8 }}>
              {selectedFeatures.map((f) => (
                <div key={f} style={{ flex: "0 0 160px" }}>
                  <InputField
                    label={f}
                    type="number"
                    value={weights[f] ?? 1}
                    onChange={(v) => setWeights((w) => ({ ...w, [f]: v }))}
                    min={0}
                    step={0.1}
                  />
                </div>
              ))}
            </div>
          </>
        )}

        {selectedFeatures.length < 2 && <Alert type="warn">Select at least 2 features to run KNN.</Alert>}

        {error && <Alert type="error">{error}</Alert>}

        <div className="btn-row" style={{ marginTop: 16 }}>
          <button
            className="btn btn-primary"
            onClick={handleRun}
            disabled={loading || selectedFeatures.length < 2 || clusteringResult.partial_countries === 0}
          >
            {loading ? (
              <>
                <Spinner /> Classifying…
              </>
            ) : (
              "🤖 Run KNN Classification"
            )}
          </button>
          {clusteringResult.partial_countries === 0 && (
            <span style={{ fontSize: 11, color: "var(--muted)" }}>
              No partial-data countries to classify.
            </span>
          )}
        </div>
      </div>

      {result && (
        <div className="card">
          <div className="card-header">
            <div className="card-title" style={{ marginBottom: 0 }}>
              Classification Results
            </div>
            <div style={{ fontSize: 11, color: "var(--muted)" }}>
              <strong style={{ color: "var(--success)" }}>{result.classified}</strong> countries classified
            </div>
          </div>

          {result.classified === 0 ? (
            <Alert type="warn">No partial-data countries were found to classify.</Alert>
          ) : (
            <>
              <div className="stat-grid" style={{ marginBottom: 20 }}>
                <StatBox label="Countries Classified" value={result.classified} color="var(--success)" />
                <StatBox
                  label="Avg Confidence"
                  value={
                    result.knn_results?.length
                      ? (
                          (result.knn_results.reduce((s, r) => s + r.confidence, 0) /
                            result.knn_results.length) *
                          100
                        ).toFixed(1) + "%"
                      : "—"
                  }
                  color="var(--info)"
                />
                <StatBox label="Features Used" value={selectedFeatures.length} color="var(--accent2)" />
              </div>

              <div style={{ display: "flex", gap: 16, marginBottom: 16, flexWrap: "wrap" }}>
                {[
                  { label: "High confidence (≥80%)", color: "var(--success)" },
                  { label: "Medium (60–79%)", color: "var(--accent)" },
                  { label: "Low (<60%)", color: "var(--danger)" },
                ].map(({ label, color }) => (
                  <div
                    key={label}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      fontSize: 11,
                      color: "var(--muted)",
                    }}
                  >
                    <span
                      style={{
                        width: 10,
                        height: 10,
                        borderRadius: "50%",
                        background: color,
                        display: "inline-block",
                      }}
                    />
                    {label}
                  </div>
                ))}
              </div>

              <div className="tbl-wrap">
                <table className="tbl">
                  <thead>
                    <tr>
                      <th>Country</th>
                      <th>Predicted Cluster</th>
                      <th>Confidence</th>
                      <th>Missing Feature</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.knn_results.map((r, i) => {
                      const pct = r.confidence * 100;
                      const col = pct >= 80 ? "var(--success)" : pct >= 60 ? "var(--accent)" : "var(--danger)";
                      return (
                        <tr key={i}>
                          <td>{r.country}</td>
                          <td>
                            <span
                              style={{
                                padding: "2px 10px",
                                borderRadius: 3,
                                fontSize: 11,
                                fontWeight: 600,
                                background: `color-mix(in srgb,${col} 15%,transparent)`,
                                border: `1px solid color-mix(in srgb,${col} 40%,transparent)`,
                                color: col,
                              }}
                            >
                              Cluster {r.predicted_cluster}
                            </span>
                          </td>
                          <td>
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                              <div style={{ width: 60, height: 5, borderRadius: 3, background: "var(--border2)", overflow: "hidden" }}>
                                <div
                                  style={{
                                    width: `${pct}%`,
                                    height: "100%",
                                    background: col,
                                    borderRadius: 3,
                                    transition: "width .3s",
                                  }}
                                />
                              </div>
                              <span style={{ color: col, fontWeight: 500 }}>{pct.toFixed(1)}%</span>
                            </div>
                          </td>
                          <td style={{ color: "var(--muted)" }}>{r.missing_feature}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              <div className="btn-row" style={{ marginTop: 20 }}>
                <button className="btn btn-success" onClick={downloadCSV}>
                  📥 Download Classification Results
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
}
