import { useState, useEffect } from "react";
import { Alert, InputField, Label, Divider, Spinner, StatBox, DataTable } from "./ui";
import { API_BASE } from "../constants";
import { apiFetch } from "../utils/api";

export function StepClustering({ sessionId, uploadResult, onDone }) {
  const availableFeatures = uploadResult?.pivot_features?.length
    ? uploadResult.pivot_features
    : uploadResult?.metrics || [];

  const [clusterYear, setClusterYear] = useState(2023);
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [nClusters, setNClusters] = useState(3);
  const [maxClusters, setMaxClusters] = useState(6);
  const [weights, setWeights] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (availableFeatures.length > 0 && selectedFeatures.length === 0) {
      setSelectedFeatures(availableFeatures.slice(0, 2));
    }
  }, [availableFeatures.length]);

  const toggleFeature = (f) =>
    setSelectedFeatures((prev) =>
      prev.includes(f) ? prev.filter((x) => x !== f) : [...prev, f]
    );

  const handleCluster = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const d = await apiFetch("/clustering/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          ref_year: clusterYear,
          selected_features: selectedFeatures,
          n_clusters: nClusters,
          max_clusters: maxClusters,
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

  if (!uploadResult) return <Alert type="warn">Complete Step 1 before proceeding.</Alert>;

  return (
    <>
      <div className="section-title">Data Clustering</div>
      <div className="section-sub">K-Means clustering on countries with complete feature data</div>

      <div className="card">
        <div style={{ maxWidth: 280 }}>
          <InputField
            label="Year to Review"
            type="number"
            value={clusterYear}
            onChange={setClusterYear}
            min={1900}
            max={2100}
            step={1}
          />
        </div>
      </div>

      <div className="card">
        <div className="card-title">Feature Selection</div>
        <div className="tag-list">
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
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 20 }}>
              <div>
                <Label>Number of Clusters</Label>
                <div className="slider-row">
                  <input
                    type="range"
                    className="slider"
                    min={2}
                    max={8}
                    step={1}
                    value={nClusters}
                    onChange={(e) => setNClusters(Number(e.target.value))}
                  />
                  <span className="slider-val">{nClusters}</span>
                </div>
              </div>
              <div>
                <Label>Max Clusters (Elbow)</Label>
                <div className="slider-row">
                  <input
                    type="range"
                    className="slider"
                    min={nClusters}
                    max={12}
                    step={1}
                    value={maxClusters}
                    onChange={(e) => setMaxClusters(Number(e.target.value))}
                  />
                  <span className="slider-val">{maxClusters}</span>
                </div>
              </div>
            </div>
            <div className="card-title">Feature Weights</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 20 }}>
              {selectedFeatures.map((f) => (
                <div key={f} style={{ flex: "0 0 140px" }}>
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

        {error && <Alert type="error">{error}</Alert>}

        {selectedFeatures.length >= 2 ? (
          <div className="btn-row">
            <button className="btn btn-primary" onClick={handleCluster} disabled={loading}>
              {loading ? (
                <>
                  <Spinner /> Clustering…
                </>
              ) : (
                "🔄 Run Clustering"
              )}
            </button>
          </div>
        ) : (
          <Alert type="warn">Select at least 2 features to enable clustering.</Alert>
        )}
      </div>

      {result && (
        <div className="card">
          <div className="card-title">Clustering Results</div>
          <div className="stat-grid">
            <StatBox label="Silhouette Score" value={result.silhouette_score?.toFixed(3)} />
            <StatBox label="Countries Clustered" value={result.countries_clustered} color="var(--success)" />
            <StatBox label="Partial (for KNN)" value={result.partial_countries} color="var(--info)" />
            <StatBox label="Insufficient" value={result.insufficient_countries} color="var(--danger)" />
            <StatBox label="Features Used" value={result.features_used} color="var(--accent2)" />
            <StatBox label="Clusters" value={nClusters} />
          </div>
          {result.clusters?.length > 0 && (
            <>
              <div className="card-title" style={{ marginTop: 16 }}>
                Cluster Assignments
              </div>
              <DataTable rows={result.clusters.slice(0, 20)} />
            </>
          )}
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
                window.open(`${API_BASE}/clustering/download/${sessionId}`)
              }
            >
              📥 Download Clustering Results
            </button>
            {result.partial_countries > 0 ? (
              <button
                className="btn btn-primary"
                onClick={() =>
                  onDone({
                    ...result,
                    clusterYear,
                    selectedFeatures,
                    weights,
                  })
                }
              >
                Proceed to KNN Classification →
              </button>
            ) : (
              <span style={{ fontSize: 11, color: "var(--muted)" }}>
                No partial-data countries found — KNN Classification step not required.
              </span>
            )}
          </div>
        </div>
      )}
    </>
  );
}
