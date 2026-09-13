export type StrategyFormState = {
  startDay: number;
  endDay: number;
  initialCash: number;
  maxPositionPerGood: number;
  minCashBuffer: number;
};

export function StrategyForm({
  value,
  onChange,
  onSubmit,
  disabled,
}: {
  value: StrategyFormState;
  onChange: (next: StrategyFormState) => void;
  onSubmit: () => void;
  disabled: boolean;
}) {
  return (
    <section className="panel">
      <h2>Backtest Konfiguration</h2>
      <div className="form-grid">
        <NumberField label="Start Tag" value={value.startDay} onChange={(v) => onChange({ ...value, startDay: v })} />
        <NumberField label="End Tag" value={value.endDay} onChange={(v) => onChange({ ...value, endDay: v })} />
        <NumberField label="Startkapital" value={value.initialCash} onChange={(v) => onChange({ ...value, initialCash: v })} />
        <NumberField
          label="Max Position / Ware"
          value={value.maxPositionPerGood}
          onChange={(v) => onChange({ ...value, maxPositionPerGood: v })}
        />
        <NumberField
          label="Min. Barreserve"
          value={value.minCashBuffer}
          onChange={(v) => onChange({ ...value, minCashBuffer: v })}
        />
      </div>
      <button disabled={disabled} onClick={onSubmit}>
        Backtest starten
      </button>
    </section>
  );
}

function NumberField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="field">
      {label}
      <input type="number" value={value} onChange={(e) => onChange(Number(e.target.value))} />
    </label>
  );
}
