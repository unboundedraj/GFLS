export function StatBox({ label, value, color }) {
  return (
    <div className="stat-box" style={{ borderLeft: `3px solid ${color || "var(--accent)"}` }}>
      <div style={{ fontSize: 10, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>
        {label}
      </div>
      <div className="stat-val" style={{ color: color || "var(--accent)" }}>
        {value}
      </div>
    </div>
  );
}
