import { useState } from "react";
import { Alert, Label, Divider, Spinner, StatBox } from "./ui";
import { apiFetch } from "../utils/api";

export function StepKNN({ sessionId, uploadResult, clusteringResult }) {
  // The KNN model is trained on the clustering output, so features, weights
  // and year are fixed by Step 4 and only shown here for reference.
  const selectedFeatures = clusteringResult?.selectedFeatures || [];
  const weights = clusteringResult?.weights || {};
  const knnYear = clusteringResult?.clusterYear || 2023;
  const maxNeighbors = Math.max(1, Math.min(10, clusteringResult?.countries_clustered || 10));

  const [nNeighbors, setNNeighbors] = useState(Math.min(5, maxNeighbors));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

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
          n_neighbors: nNeighbors,
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
            <Label>Reference Year</Label>
            <div className="stat-val" style={{ color: "var(--accent)", marginTop: 6 }}>
              {knnYear}
            </div>
          </div>
          <div>
            <Label>K (Neighbours)</Label>
            <div className="slider-row" style={{ marginTop: 6 }}>
              <input
                type="range"
                className="slider"
                min={1}
                max={maxNeighbors}
                step={1}
                value={nNeighbors}
                onChange={(e) => setNNeighbors(Number(e.target.value))}
              />
              <span className="slider-val">{nNeighbors}</span>
            </div>
            <div style={{ fontSize: 10, color: "var(--muted)", marginTop: 4 }}>
              Capped at the number of clustered countries.
            </div>
          </div>
        </div>

        <Divider />

        <div className="card-title">Features &amp; Weights</div>
        <Alert type="info">
          Taken from your clustering run. To change them, go back to Step 4 and re-run clustering.
        </Alert>
        <div className="tag-list" style={{ marginTop: 12 }}>
          {selectedFeatures.map((f) => (
            <span key={f} className="tag active" style={{ cursor: "default" }}>
              {f} × {weights[f] ?? 1}
            </span>
          ))}
        </div>

        {error && <Alert type="error">{error}</Alert>}

        <div className="btn-row" style={{ marginTop: 16 }}>
          <button
            className="btn btn-primary"
            onClick={handleRun}
            disabled={loading || clusteringResult.partial_countries === 0}
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
