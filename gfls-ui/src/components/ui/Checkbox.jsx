export function Checkbox({ checked, onChange, children }) {
  return (
    <div className="checkbox-row" onClick={() => onChange(!checked)}>
      <div className={`checkbox-box${checked ? " checked" : ""}`}>
        {checked && <span style={{ color: "#000", fontSize: 11, fontWeight: 700 }}>✓</span>}
      </div>
      <span style={{ fontSize: 13, color: "var(--text)" }}>{children}</span>
    </div>
  );
}
