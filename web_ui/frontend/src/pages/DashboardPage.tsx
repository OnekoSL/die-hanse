import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";

import { api } from "../api-client/client";
import type { BacktestResult } from "../api-client/types";
import { EquityChart } from "../components/EquityChart";
import { EventTable } from "../components/EventTable";
import { MetricsPanel } from "../components/MetricsPanel";
import { ScenarioPicker } from "../components/ScenarioPicker";
import { StrategyForm, type StrategyFormState } from "../components/StrategyForm";

export function DashboardPage() {
  const [form, setForm] = useState<StrategyFormState>({
    startDay: 1,
    endDay: 365,
    initialCash: 10000,
    maxPositionPerGood: 30,
    minCashBuffer: 100,
  });
  const [selectedScenario, setSelectedScenario] = useState<string>("");
  const [clientError, setClientError] = useState<string>("");

  const scenarios = useQuery({ queryKey: ["scenarios"], queryFn: api.listScenarios });
  const runs = useQuery({ queryKey: ["runs"], queryFn: () => api.listRuns(1, 10) });

  const mutation = useMutation({
    mutationFn: api.runBacktest,
  });

  const activeScenario = useMemo(() => {
    if (!scenarios.data || scenarios.data.length === 0) return "";
    return selectedScenario || scenarios.data[0].id;
  }, [scenarios.data, selectedScenario]);

  const result: BacktestResult | undefined = mutation.data;

  const onRun = () => {
    setClientError("");
    if (form.endDay <= form.startDay) {
      setClientError("End Tag muss groesser als Start Tag sein.");
      return;
    }
    mutation.mutate({
      scenario_id: activeScenario,
      start_day: form.startDay,
      end_day: form.endDay,
      initial_cash: form.initialCash,
      strategy: { type: "rule_based_v1", params: {} },
      risk_limits: {
        max_position_per_good: form.maxPositionPerGood,
        min_cash_buffer: form.minCashBuffer,
      },
    });
  };

  return (
    <div className="layout">
      <section className="panel">
        <h2>Szenario</h2>
        {scenarios.isLoading ? <p>Lade Szenarien...</p> : null}
        {scenarios.data && scenarios.data.length > 0 ? (
          <ScenarioPicker scenarios={scenarios.data} value={activeScenario} onChange={setSelectedScenario} />
        ) : null}
      </section>

      <StrategyForm value={form} onChange={setForm} onSubmit={onRun} disabled={mutation.isPending || !activeScenario} />

      {clientError ? <p className="error">{clientError}</p> : null}
      {mutation.error ? <p className="error">{String(mutation.error)}</p> : null}

      {result ? (
        <>
          <MetricsPanel summary={result.summary} />
          <EquityChart data={result.equity_curve} />
          <EventTable events={result.trade_log} />
          {result.violations.length > 0 ? (
            <section className="panel">
              <h2>Verletzungen</h2>
              <ul>
                {result.violations.map((v) => (
                  <li key={v}>{v}</li>
                ))}
              </ul>
            </section>
          ) : null}
        </>
      ) : null}

      <section className="panel">
        <h2>Laufhistorie</h2>
        {runs.isLoading ? <p>Lade Historie...</p> : null}
        {runs.data?.items.map((item) => (
          <article key={item.run_id} className="history-item">
            <div>
              <strong>{item.run_id.slice(0, 8)}</strong>
              <p>{item.scenario_id}</p>
            </div>
            <div>
              <p>PnL: {item.summary.pnl.toFixed(2)}</p>
              <p>Dauer: {item.duration_ms} ms</p>
            </div>
            <Link to={`/runs/${item.run_id}`}>Einzelansicht</Link>
          </article>
        ))}
      </section>
    </div>
  );
}
