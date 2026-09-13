import type { BacktestSummary } from "../api-client/types";

export function MetricsPanel({ summary }: { summary: BacktestSummary }) {
  return (
    <section className="panel metrics-grid">
      <Metric label="ROI" value={`${(summary.roi * 100).toFixed(2)}%`} />
      <Metric label="PnL" value={summary.pnl.toFixed(2)} />
      <Metric label="Max Drawdown" value={`${(summary.max_drawdown * 100).toFixed(2)}%`} />
      <Metric label="Win Rate" value={`${(summary.win_rate_trades * 100).toFixed(2)}%`} />
      <Metric label="Turnover" value={summary.turnover.toFixed(2)} />
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-card">
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  );
}
