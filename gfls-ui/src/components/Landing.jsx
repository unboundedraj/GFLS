import { useEffect } from "react";
import { landingStyles } from "../styles/landing";
import { REGRESSION_METHODS } from "../constants";

const STEP_INFO = [
  { t: "Upload", d: "Drop an Excel or CSV file in any of four layouts. It is reshaped into one tidy schema." },
  { t: "Year correction", d: "Fill gaps for a reference year by interpolating or extrapolating from history." },
  { t: "Regression", d: "Forecast any metric for a future year and add the prediction to your dataset." },
  { t: "Clustering", d: "Group countries with complete data using weighted K-Means, scored and plotted." },
  { t: "KNN", d: "Place countries that are missing one metric into the nearest existing cluster." },
];

const FEATURES = [
  { i: "⇄", t: "Four layouts, one schema", d: "Years as columns, years as rows, years inside labels, or already long. Everything lands as country, year, metric, value, source, assumption." },
  { i: "◔", t: "Gap filling you can choose", d: "Six interpolation and five extrapolation methods, from linear and spline to CAGR and ARIMA.", chips: ["linear", "spline", "log-scale", "CAGR", "ARIMA"] },
  { i: "↗", t: "Nine forecasting models", d: "Compare simple trends against ensembles and neural networks on the same series.", chips: ["ridge", "lasso", "random forest", "SVM", "MLP"] },
  { i: "◉", t: "Weighted clustering", d: "Standardized K-Means with per-feature weights, silhouette score and an elbow curve to pick k." },
  { i: "✦", t: "KNN for partial data", d: "Countries missing a single indicator are classified into a cluster with a confidence score instead of being dropped." },
  { i: "⤓", t: "Export what you built", d: "Download the cleaned dataset as Excel and the clustering results as CSV at any point." },
];

function ForecastChart() {
  return (
    <svg className="lp-svg" viewBox="0 0 460 250" role="img" aria-label="Illustrative forecast line chart: a rising historical line continues as a dashed forecast with a widening confidence band">
      {[50, 100, 150, 200].map((y) => (
        <line key={y} x1="30" x2="440" y1={y} y2={y} stroke="#2a2d38" strokeDasharray="2 6" />
      ))}
      <polygon className="lp-fade" points="310,108 350,84 390,56 430,28 430,92 390,100 350,102 310,108" fill="rgba(232,197,71,0.13)" />
      <polyline
        className="lp-draw"
        pathLength="1"
        points="30,200 70,190 110,176 150,170 190,150 230,140 270,118 310,108"
        fill="none"
        stroke="#e8c547"
        strokeWidth="2.5"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <polyline
        className="lp-fade"
        points="310,108 350,94 390,78 430,60"
        fill="none"
        stroke="#f0d97a"
        strokeWidth="2.5"
        strokeDasharray="6 6"
        strokeLinecap="round"
      />
      <line className="lp-fade" x1="310" x2="310" y1="20" y2="216" stroke="#353848" strokeDasharray="3 5" />
      <circle cx="310" cy="108" r="4.5" fill="#e8c547" />
      <circle className="lp-ping" cx="430" cy="60" r="4.5" fill="#e8c547" />
      <circle cx="430" cy="60" r="4.5" fill="#0b0c0f" stroke="#f0d97a" strokeWidth="2" />
      <g fontFamily="DM Mono, monospace" fontSize="10" fill="#7a7f96">
        <text x="30" y="236">2015</text>
        <text x="296" y="236">2023</text>
        <text x="412" y="236">2026</text>
        <text x="318" y="34" fill="#e8c547">forecast →</text>
      </g>
    </svg>
  );
}

function ClusterChart() {
  const A = [[70, 150], [85, 172], [105, 155], [95, 186], [74, 176], [112, 176]];
  const B = [[230, 58], [255, 86], [272, 64], [246, 48], [276, 92], [236, 82]];
  const C = [[240, 168], [265, 196], [286, 174], [250, 202], [282, 158], [272, 184]];
  const dots = (pts, color) => pts.map(([x, y], i) => <circle key={color + i} cx={x} cy={y} r="6" fill={color} fillOpacity="0.9" />);
  return (
    <svg className="lp-svg" viewBox="0 0 360 240" role="img" aria-label="Illustrative scatter plot of three clusters of countries, with one partial-data country linked to its nearest neighbours in cluster 2">
      <ellipse cx="94" cy="168" rx="46" ry="38" fill="rgba(232,197,71,0.06)" stroke="rgba(232,197,71,0.25)" strokeDasharray="3 5" />
      <ellipse cx="252" cy="70" rx="46" ry="38" fill="rgba(78,203,141,0.06)" stroke="rgba(78,203,141,0.25)" strokeDasharray="3 5" />
      <ellipse cx="266" cy="180" rx="46" ry="40" fill="rgba(92,159,224,0.06)" stroke="rgba(92,159,224,0.25)" strokeDasharray="3 5" />
      {dots(A, "#e8c547")}
      {dots(B, "#4ecb8d")}
      {dots(C, "#5c9fe0")}
      {[[240, 168], [250, 202], [265, 196]].map(([x, y], i) => (
        <line key={i} x1="214" y1="170" x2={x} y2={y} stroke="#f0d97a" strokeOpacity="0.7" strokeDasharray="3 3" />
      ))}
      <circle cx="214" cy="170" r="8" fill="#0b0c0f" stroke="#f0d97a" strokeWidth="2" strokeDasharray="3 2" />
      <g fontFamily="DM Mono, monospace" fontSize="10" fill="#7a7f96">
        <text x="40" y="214" fill="#e8c547">Cluster 0</text>
        <text x="236" y="28" fill="#4ecb8d">Cluster 1</text>
        <text x="290" y="226" fill="#5c9fe0">Cluster 2</text>
        <text x="132" y="150" fill="#f0d97a">KNN → Cluster 2</text>
      </g>
    </svg>
  );
}

export function Landing({ onLaunch }) {
  useEffect(() => {
    const els = document.querySelectorAll(".lp-rv");
    if (!("IntersectionObserver" in window)) {
      els.forEach((el) => el.classList.add("in"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        }),
      { threshold: 0.12 }
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  return (
    <div className="lp">
      <style>{landingStyles}</style>

      <nav className="lp-nav">
        <div className="lp-wrap lp-nav-in">
          <div className="lp-brand"><span>⬡</span> GFLS</div>
          <div className="lp-links">
            <a href="#workflow">Workflow</a>
            <a href="#preview">Preview</a>
            <a href="#features">Features</a>
          </div>
          <button className="btn btn-primary" onClick={onLaunch}>Launch app →</button>
        </div>
      </nav>

      <header className="lp-hero">
        <div className="lp-wrap lp-hero-grid">
          <div>
            <div className="lp-eyebrow"><span className="lp-dot" /> Global Forecasting &amp; Learning System</div>
            <h1 className="lp-h1">From messy spreadsheets to <em>forecasts and clusters.</em></h1>
            <p className="lp-lead">
              GFLS cleans country-level indicator data from four common layouts, fills the gaps,
              forecasts with nine models and groups countries by similarity, in five guided steps.
            </p>
            <div className="lp-cta">
              <button className="btn btn-primary lp-btn" onClick={onLaunch}>Start with your data →</button>
              <a className="btn btn-secondary lp-btn" href="#workflow">See how it works</a>
            </div>
            <div className="lp-note"><b>Excel &amp; CSV</b> · GDP, population, life expectancy and more</div>
          </div>

          <div className="lp-panel">
            <div className="lp-panel-bar"><i /><i /><i /><span>GDP per capita · sample series</span></div>
            <div className="lp-panel-body"><ForecastChart /></div>
            <div className="lp-legend">
              <span><i /> Observed</span>
              <span><i className="dash" /> Forecast</span>
            </div>
          </div>
        </div>
      </header>

      <section className="lp-stats">
        <div className="lp-wrap lp-stats-grid">
          {[["4", "Input layouts"], ["11", "Gap-filling methods"], ["9", "Forecast models"], ["5", "Guided steps"]].map(([n, l]) => (
            <div className="lp-stat" key={l}><b>{n}</b><span>{l}</span></div>
          ))}
        </div>
      </section>

      <section className="lp-sec" id="workflow">
        <div className="lp-wrap">
          <div className="lp-rv">
            <div className="lp-kicker">Workflow</div>
            <h2 className="lp-h2">Five steps, one clean pipeline.</h2>
            <p className="lp-sub">Each step feeds the next. Move forward when you are happy, or jump back and adjust.</p>
          </div>
          <div className="lp-steps">
            {STEP_INFO.map((s, i) => (
              <div className="lp-step lp-rv" style={{ transitionDelay: `${i * 70}ms` }} key={s.t}>
                <div className="lp-step-n">0{i + 1}</div>
                <h3>{s.t}</h3>
                <p>{s.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="lp-sec" id="preview">
        <div className="lp-wrap">
          <div className="lp-rv">
            <div className="lp-kicker">Preview</div>
            <h2 className="lp-h2">See what changes to your data.</h2>
            <p className="lp-sub">Illustrative examples of the reshaping and clustering the app performs.</p>
          </div>
          <div className="lp-show">
            <div className="lp-panel lp-rv">
              <div className="lp-reshape">
                <div>
                  <div className="lp-tag-mini">Before · years as columns</div>
                  <div className="lp-mini">
                    <div className="c3 h"><span>Country</span><span>Y1 2015</span><span>Y2 2016</span></div>
                    <div className="c3"><span>India</span><span>1,606</span><span>1,714</span></div>
                    <div className="c3"><span>Kenya</span><span>1,293</span><span>1,331</span></div>
                  </div>
                </div>
                <div className="lp-arrow">→</div>
                <div>
                  <div className="lp-tag-mini">After · long format</div>
                  <div className="lp-mini">
                    <div className="c4 h"><span>country</span><span>year</span><span>metric</span><span>value</span></div>
                    <div className="c4"><span>India</span><span>2015</span><span className="mut">GDP per capita</span><span>1,606</span></div>
                    <div className="c4"><span>India</span><span>2016</span><span className="mut">GDP per capita</span><span>1,714</span></div>
                    <div className="c4"><span>Kenya</span><span>2015</span><span className="mut">GDP per capita</span><span>1,293</span></div>
                  </div>
                </div>
              </div>
              <div className="lp-cap">
                <h3>Messy in, tidy out</h3>
                <p>Columns for country, year and metric are detected automatically, and the layout only needs mapping by hand when it is ambiguous.</p>
              </div>
            </div>

            <div className="lp-panel lp-rv" style={{ transitionDelay: "90ms" }}>
              <div className="lp-panel-body"><ClusterChart /></div>
              <div className="lp-cap">
                <h3>Clusters that include everyone</h3>
                <p>Countries missing a single indicator are assigned to the nearest cluster instead of being thrown away.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="lp-sec" id="features">
        <div className="lp-wrap">
          <div className="lp-rv">
            <div className="lp-kicker">Features</div>
            <h2 className="lp-h2">Everything between raw file and insight.</h2>
            <p className="lp-sub">Built on pandas and scikit-learn, with a FastAPI backend and a React interface.</p>
          </div>
          <div className="lp-feats">
            {FEATURES.map((f, i) => (
              <div className="lp-feat lp-rv" style={{ transitionDelay: `${(i % 3) * 80}ms` }} key={f.t}>
                <div className="lp-ico">{f.i}</div>
                <h3>{f.t}</h3>
                <p>{f.d}</p>
                {f.chips && (
                  <div className="lp-chips">
                    {f.chips.map((c) => <span className="lp-chip" key={c}>{c}</span>)}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="lp-final">
        <div className="lp-wrap lp-rv">
          <h2 className="lp-h2">Ready to turn a spreadsheet into answers?</h2>
          <p className="lp-sub">Bring your own file, or start with the bundled sample datasets.</p>
          <button className="btn btn-primary lp-btn" onClick={onLaunch}>Launch GFLS →</button>
        </div>
      </section>

      <footer className="lp-wrap lp-foot">
        <span>GFLS Automation · {REGRESSION_METHODS.length} regression models · Python &amp; React</span>
        <span>Bachelor of Engineering final-year project</span>
      </footer>
    </div>
  );
}
