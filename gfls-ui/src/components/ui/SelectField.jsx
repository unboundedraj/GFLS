import { Label } from "./Label";

export function SelectField({ label, options, value, onChange, disabled }) {
  return (
    <div className="input-group">
      {label && <Label>{label}</Label>}
      <select
        className="input-field"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        {options.map((o) => (
          <option key={o.value ?? o} value={o.value ?? o}>
            {o.label ?? o}
          </option>
        ))}
      </select>
    </div>
  );
}
