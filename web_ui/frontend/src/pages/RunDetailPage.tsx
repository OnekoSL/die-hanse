import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { api } from "../api-client/client";
import { EquityChart } from "../components/EquityChart";
import { EventTable } from "../components/EventTable";
import { MetricsPanel } from "../components/MetricsPanel";

export function RunDetailPage() {
  const { runId = "" } = useParams();
  const [good, setGood] = useState<string>("alle");
  const [dayFrom, setDayFrom] = useState<number>(1);

  const query = useQuery({ queryKey: ["run", runId], queryFn: () => api.getRun(runId), enabled: !!runId });

  const filteredEvents = useMemo(() => {
    if (!query.data) return [];
    return query.data.trade_log.filter((e) => {
      const goodMatch = good === "alle" || e.good === good;
      return goodMatch && e.day >= dayFrom;
    });
  }, [query.data, good, dayFrom]);

  const goods = useMemo(() => {
    if (!query.data) return [] as string[];
    return Array.from(new Set(query.data.trade_log.map((e) => e.good)));
  }, [query.data]);

  if (query.isLoading) return <p>Lade Lauf...</p>;
  if (query.error || !query.data) return <p>Lauf nicht gefunden.</p>;

  return (
    <div className="layout">
      <section className="panel">
        <Link to="/">Zurueck</Link>
        <h2>Lauf {query.data.run_id}</h2>
      </section>
      <MetricsPanel summary={query.data.summary} />
      <EquityChart data={query.data.equity_curve} />
      <section className="panel filter-row">
        <label className="field">
          Ware
          <select value={good} onChange={(e) => setGood(e.target.value)}>
            <option value="alle">alle</option>
            {goods.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          Tag ab
          <input type="number" value={dayFrom} onChange={(e) => setDayFrom(Number(e.target.value))} />
        </label>
      </section>
      <EventTable events={filteredEvents} />
    </div>
  );
}
