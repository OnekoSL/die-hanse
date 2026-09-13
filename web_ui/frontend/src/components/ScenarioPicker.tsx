import type { ScenarioSummary } from "../api-client/types";

export function ScenarioPicker({
  scenarios,
  value,
  onChange,
}: {
  scenarios: ScenarioSummary[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="field">
      Szenario
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {scenarios.map((s) => (
          <option key={s.id} value={s.id}>
            {s.name} ({s.version})
          </option>
        ))}
      </select>
    </label>
  );
}
