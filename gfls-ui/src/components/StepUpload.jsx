import { useState, useRef } from "react";
import { Alert, SelectField, InputField, Divider, Spinner, DataTable, StatBox } from "./ui";
import { FORMATS, COLUMN_FIELDS } from "../constants";
import { apiFetch } from "../utils/api";
import { readExcelClientSide } from "../utils/excel";

export function StepUpload({ sessionId, onDone }) {
  const fileRef = useRef();
  const [drag, setDrag] = useState(false);
  const [fileType, setFileType] = useState("Excel");
  const [sheetName, setSheetName] = useState("Sheet1");
  const [file, setFile] = useState(null);
  const [format, setFormat] = useState(null);
  const [rawPreview, setRawPreview] = useState(null);
  const [rawCols, setRawCols] = useState([]);
  const [mapping, setMapping] = useState({});
  const [reading, setReading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFile = async (f) => {
    if (!f) return;
    setFile(f);
    setRawPreview(null);
    setResult(null);
    setError(null);
    setFormat(null);
    setReading(true);
    try {
      if (fileType === "Excel") {
        const data = await readExcelClientSide(f, sheetName);
        setSheetName(data.usedSheet);
        setRawPreview(data);
        setRawCols(data.columns);
        const def = {};
        COLUMN_FIELDS.forEach((field, i) => {
          def[field] = data.columns[i] || data.columns[0];
        });
        setMapping(def);
      } else {
        const fd = new FormData();
        fd.append("file", f);
        fd.append("file_type", "CSV");
        fd.append("sheet_name", "");
        const d = await apiFetch("/preview-columns", { method: "POST", body: fd });
        setRawPreview({
          columns: d.columns,
          preview: d.preview,
          totalRows: d.total_rows,
          totalCols: d.total_cols,
        });
        setRawCols(d.columns);
        const def = {};
        COLUMN_FIELDS.forEach((field, i) => {
          def[field] = d.columns[i] || d.columns[0];
        });
        setMapping(def);
      }
    } catch (e) {
      setError("Could not read file: " + e.message);
    } finally {
      setReading(false);
    }
  };

  const handleSheetChange = async (val) => {
    setSheetName(val);
    if (file && fileType === "Excel") {
      setReading(true);
      try {
        const data = await readExcelClientSide(file, val);
        setRawPreview(data);
        setRawCols(data.columns);
        const def = {};
        COLUMN_FIELDS.forEach((field, i) => {
          def[field] = data.columns[i] || data.columns[0];
        });
        setMapping(def);
      } catch (e) {
        setError(e.message);
      } finally {
        setReading(false);
      }
    }
  };

  const handleFormatSelect = (id) => {
    setFormat(id);
    setResult(null);
    setError(null);
  };

  const handleApply = async () => {
    if (!file || !format) return;
    setLoading(true);
    setError(null);
    const fd = new FormData();
    fd.append("file", file);
    fd.append("file_type", fileType);
    fd.append("sheet_name", sheetName);
    fd.append("format_num", format);
    fd.append("session_id", sessionId);
    if (format === 1) {
      fd.append(
        "column_mapping",
        JSON.stringify(Object.fromEntries(COLUMN_FIELDS.map((f) => [mapping[f], f])))
      );
    }
    try {
      const d = await apiFetch("/upload", { method: "POST", body: fd });
      setResult(d);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="section-title">Data Collation</div>
      <div className="section-sub">Upload a file — raw preview shown instantly, then choose a format</div>

      <div className="card">
        <div className="card-title">File Type</div>
        <div className="radio-group">
          {["Excel", "CSV"].map((t) => (
            <button
              key={t}
              className={`radio-btn${fileType === t ? " selected" : ""}`}
              onClick={() => {
                setFileType(t);
                setFile(null);
                setRawPreview(null);
                setResult(null);
                setFormat(null);
              }}
            >
              {t}
            </button>
          ))}
        </div>

        <div
          className={`upload-zone${drag ? " drag" : ""}`}
          onClick={() => fileRef.current.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDrag(true);
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDrag(false);
            handleFile(e.dataTransfer.files[0]);
          }}
        >
          <div className="upload-icon">📂</div>
          <div className="upload-label">
            {fileType === "CSV" ? "Drop CSV file here" : "Drop Excel file here"}
          </div>
          <div className="upload-hint">
            {fileType === "CSV" ? ".csv" : ".xlsx, .xls"} · click or drag & drop
          </div>
          <input
            ref={fileRef}
            type="file"
            style={{ display: "none" }}
            accept={fileType === "CSV" ? ".csv" : ".xlsx,.xls"}
            onChange={(e) => handleFile(e.target.files[0])}
          />
        </div>

        {file && (
          <div className="upload-success">
            <span style={{ color: "var(--success)", fontSize: 18 }}>✓</span>
            <div>
              <div style={{ fontSize: 13, fontWeight: 500, color: "var(--success)" }}>
                {file.name}
              </div>
              <div style={{ fontSize: 11, color: "var(--muted)" }}>
                {(file.size / 1024).toFixed(1)} KB
                {rawPreview && ` · ${rawPreview.totalRows} rows · ${rawPreview.totalCols} columns`}
              </div>
            </div>
          </div>
        )}

        {fileType === "Excel" && file && (
          <div style={{ marginTop: 16, maxWidth: 320 }}>
            {rawPreview?.sheetNames?.length > 1 ? (
              <SelectField
                label="Sheet"
                options={rawPreview.sheetNames}
                value={sheetName}
                onChange={handleSheetChange}
              />
            ) : (
              <InputField
                label="Sheet Name"
                value={sheetName}
                onChange={handleSheetChange}
                placeholder="Sheet1"
              />
            )}
            {rawPreview?.usedSheet && (
              <div style={{ fontSize: 11, color: "var(--muted)", marginTop: -8 }}>
                Active: <span style={{ color: "var(--accent)" }}>{rawPreview.usedSheet}</span>
                {rawPreview.sheetNames?.length > 1 &&
                  ` · ${rawPreview.sheetNames.length} sheets available`}
              </div>
            )}
          </div>
        )}
      </div>

      {reading && (
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", gap: 10, color: "var(--muted)", fontSize: 13 }}>
            <Spinner /> Reading file…
          </div>
        </div>
      )}

      {rawPreview && !reading && (
        <div className="card">
          <div className="card-header">
            <div className="card-title" style={{ marginBottom: 0 }}>
              Original Data Preview
            </div>
            <div style={{ fontSize: 11, color: "var(--muted)" }}>
              Showing first <strong style={{ color: "var(--accent)" }}>{rawPreview.preview.length}</strong> of{" "}
              <strong style={{ color: "var(--accent)" }}>{rawPreview.totalRows}</strong> rows ·{" "}
              <strong style={{ color: "var(--accent)" }}>{rawPreview.totalCols}</strong> columns
            </div>
          </div>
          <DataTable rows={rawPreview.preview} columns={rawPreview.columns} />
          <div className="tbl-meta">Columns: {rawPreview.columns.join(" · ")}</div>
        </div>
      )}

      {file && rawPreview && (
        <div className="card">
          <div className="card-title">Choose a Formatting Option</div>
          <div className="format-grid">
            {FORMATS.map((f) => (
              <div
                key={f.id}
                className={`format-card${format === f.id ? " selected" : ""}`}
                onClick={() => handleFormatSelect(f.id)}
              >
                <div className="format-card-num">{f.id}</div>
                <div className="format-card-label">{f.label}</div>
                <div className="format-card-desc">{f.desc}</div>
              </div>
            ))}
          </div>

          {format === 1 && rawCols.length > 0 && (
            <>
              <Divider />
              <div className="card-title">Column Mapping</div>
              <Alert type="info">Map your file's columns to the required standard fields.</Alert>
              <div className="mapping-grid">
                {COLUMN_FIELDS.map((field) => (
                  <SelectField
                    key={field}
                    label={`${field.charAt(0).toUpperCase() + field.slice(1)} column`}
                    options={rawCols}
                    value={mapping[field] || rawCols[0]}
                    onChange={(v) => setMapping((m) => ({ ...m, [field]: v }))}
                  />
                ))}
              </div>
            </>
          )}

          {error && <Alert type="error">{error}</Alert>}

          <div className="btn-row">
            <button className="btn btn-primary" onClick={handleApply} disabled={loading || !format}>
              {loading ? (
                <>
                  <Spinner /> Processing…
                </>
              ) : (
                "Apply Format →"
              )}
            </button>
          </div>
        </div>
      )}

      {result && (
        <div className="card">
          <div className="card-header">
            <div className="card-title" style={{ marginBottom: 0 }}>
              Formatted Data Preview
            </div>
            <div style={{ fontSize: 11, color: "var(--muted)" }}>
              Showing first <strong style={{ color: "var(--success)" }}>{result.preview?.length}</strong> of{" "}
              <strong style={{ color: "var(--success)" }}>{result.rows}</strong> rows ·{" "}
              <strong style={{ color: "var(--success)" }}>{result.cols}</strong> columns
            </div>
          </div>
          <div className="stat-grid" style={{ marginBottom: 16 }}>
            <StatBox label="Total Rows" value={result.rows} />
            <StatBox label="Columns" value={result.cols} color="var(--info)" />
            <StatBox label="Countries" value={result.countries?.length || "—"} color="var(--success)" />
          </div>
          <DataTable rows={result.preview} columns={result.columns} />
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
            <div style={{ fontSize: 12, color: "var(--muted)" }}>
              ✓ Format applied successfully. Review the data above, then proceed.
            </div>
            <button className="btn btn-primary" onClick={() => onDone(result)}>
              Proceed to Year Correction →
            </button>
          </div>
        </div>
      )}

      {!file && <Alert type="warn">Upload a file above to get started.</Alert>}
    </>
  );
}
