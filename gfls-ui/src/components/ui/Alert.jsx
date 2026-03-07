export function Alert({ type = "info", children }) {
  const icons = { info: "ℹ", success: "✓", warn: "⚠", error: "✕" };
  return (
    <div className={`alert alert-${type}`}>
      <span>{icons[type]}</span>
      <span>{children}</span>
    </div>
  );
}
