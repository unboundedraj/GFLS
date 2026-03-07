import { Label } from "./Label";

export function InputField({ label, type = "text", value, onChange, min, max, step, placeholder, disabled }) {
  return (
    <div className="input-group">
      {label && <Label>{label}</Label>}
      <input
        className="input-field"
        type={type}
        value={value}
        onChange={(e) => onChange(type === "number" ? Number(e.target.value) : e.target.value)}
        min={min}
        max={max}
        step={step}
        placeholder={placeholder}
        disabled={disabled}
      />
    </div>
  );
}
