import { useState } from "react";
import { StepUpload, StepYearCorrection, StepRegression, StepClustering, StepKNN } from "./components";
import { STEPS } from "./constants";
import { styles } from "./styles";

const SESSION_ID = Math.random().toString(36).slice(2);

export default function App() {
  const [activeStep, setActiveStep] = useState(0);
  const [uploadResult, setUploadResult] = useState(null);
  const [yearDone, setYearDone] = useState(false);
  const [regressionDone, setRegressionDone] = useState(false);
  const [clusteringResult, setClusteringResult] = useState(null);

  const stepDone = [
    !!uploadResult,      // Step 1: Upload
    yearDone,            // Step 2: Year Correction
    regressionDone,      // Step 3: Regression
    !!clusteringResult,  // Step 4: Clustering
    false,               // Step 5: KNN Classification
  ];

  const goNext = () => setActiveStep((s) => Math.min(s + 1, STEPS.length - 1));

  return (
    <>
      <style>{styles}</style>
      <div className="app">
        <header className="header">
          <div>
            <div className="logo">
              <span>⬡</span> GFLS
            </div>
            <div className="logo-sub">Global Forecasting & Learning System · Automation UI</div>
          </div>
          <div style={{ fontSize: 11, color: "var(--muted)" }}>
            Session: <span style={{ color: "var(--accent)", fontFamily: "var(--font-mono)" }}>{SESSION_ID}</span>
          </div>
        </header>

        <nav className="step-nav">
          {STEPS.map((name, i) => (
            <button
              key={i}
              className={`step-btn${activeStep === i ? " active" : ""}${
                stepDone[i] && activeStep !== i ? " done" : ""
              }`}
              onClick={() => setActiveStep(i)}
            >
              <span className="step-num">{stepDone[i] && activeStep !== i ? "✓" : i + 1}</span>
              {name}
            </button>
          ))}
        </nav>

        <main className="main">
          {activeStep === 0 && (
            <StepUpload
              sessionId={SESSION_ID}
              onDone={(d) => {
                setUploadResult(d);
                goNext();
              }}
            />
          )}
          {activeStep === 1 && (
            <StepYearCorrection
              sessionId={SESSION_ID}
              uploadResult={uploadResult}
              onDone={() => {
                setYearDone(true);
                goNext();
              }}
            />
          )}
          {activeStep === 2 && (
            <StepRegression
              sessionId={SESSION_ID}
              uploadResult={uploadResult}
              onDone={() => setRegressionDone(true)}
            />
          )}
          {activeStep === 3 && (
            <StepClustering
              sessionId={SESSION_ID}
              uploadResult={uploadResult}
              onDone={(d) => {
                setClusteringResult(d);
                goNext();
              }}
            />
          )}
          {activeStep === 4 && (
            <StepKNN
              sessionId={SESSION_ID}
              uploadResult={uploadResult}
              clusteringResult={clusteringResult}
            />
          )}

          <div
            className="btn-row"
            style={{ marginTop: 32, paddingTop: 20, borderTop: "1px solid var(--border)" }}
          >
            {activeStep > 0 && (
              <button className="btn btn-secondary" onClick={() => setActiveStep((s) => s - 1)}>
                ← Back
              </button>
            )}
            {activeStep > 0 && activeStep < STEPS.length - 1 && (
              <button className="btn btn-primary" onClick={goNext}>
                Next: {STEPS[activeStep + 1]} →
              </button>
            )}
          </div>
        </main>
      </div>
    </>
  );
}
