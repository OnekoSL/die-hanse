import { useState } from "react";
import type { GameController } from "../useGameController";
import { label, money, dateAt } from "../display";
function description(type: string, p: Record<string, unknown>): string {
  const city = label(String(p.city ?? ""));
  if (type === "session_started") return "Handelshaus in Lübeck gegründet.";
  if (type === "market_trade_executed")
    return `${p.type === "buy" ? "Kauf" : "Verkauf"}: ${p.qty} ${label(String(p.good))} in ${city} · Gesamt ${money(Number(p.total))}`;
  if (type === "transfer_executed")
    return `${p.qty} ${label(String(p.good))} in ${city} ${p.direction === "ship_to_private" ? "ins Kontor entladen" : "auf das Schiff geladen"}.`;
  if (type === "course_set")
    return `Kurs von ${label(String(p.from))} nach ${label(String(p.to))} · ${p.eta_days} Tage.`;
  if (type === "ship_arrival") return `Schiff in ${city} angekommen.`;
  if (type === "construction_ordered" || type === "construction_completed")
    return `${p.kind === "ship" ? "Schiff" : "Kontor"} in ${city} ${type === "construction_ordered" ? `bestellt · ${money(Number(p.price))}` : "fertiggestellt"}.`;
  if (type === "month_closed")
    return `Monatsabschluss ${p.month} · Geldüberschuss ${money(Number(p.cash_surplus))}.`;
  if (type === "ship_sold" || type === "storage_sold")
    return `${type === "ship_sold" ? "Schiff" : "Kontorstufe"} in ${city} verkauft · ${money(Number(p.price))}.`;
  return "Eintrag im Handelsbuch.";
}
export function LogbookView({ c }: { c: GameController }) {
  const [count, setCount] = useState(50);
  return (
    <div className="two-columns">
      <section className="panel">
        <p className="eyebrow">ALLE HÄFEN</p>
        <h2>Handelsbuch</h2>
        {c.events.slice(0, count).map((event) => (
          <article key={event.id} className="ledger-row">
            <small>{dateAt(event.day)}</small>
            <p>{description(event.event_type, event.payload)}</p>
          </article>
        ))}
        {count < c.events.length && (
          <button onClick={() => setCount(count + 50)}>
            Ältere Einträge anzeigen
          </button>
        )}
      </section>
      <section className="panel">
        <h2>Monatsberichte</h2>
        <p className="muted">
          Einnahmen und Ausgaben des Handelshauses. Geldüberschuss ist kein
          Unternehmensgewinn.
        </p>
        {!c.state!.reports.length && (
          <p>Der erste Bericht erscheint am 1. April 1400.</p>
        )}
        {[...c.state!.reports].reverse().map((r) => (
          <article className="asset-card" key={r.month}>
            <h3>{r.month}</h3>
            <dl>
              <dt>Anfangsgeld</dt>
              <dd>{money(r.opening_cash)}</dd>
              <dt>Warenverkäufe</dt>
              <dd>{money(r.trade_income)}</dd>
              <dt>Wareneinkäufe</dt>
              <dd>−{money(r.trade_expenses)}</dd>
              <dt>Ausbauausgaben</dt>
              <dd>−{money(r.construction_expenses)}</dd>
              <dt>Anlagenverkäufe</dt>
              <dd>{money(r.asset_income)}</dd>
              <dt>Endgeld</dt>
              <dd>{money(r.closing_cash)}</dd>
              <dt>Geldüberschuss</dt>
              <dd>{money(r.cash_surplus)}</dd>
            </dl>
          </article>
        ))}
      </section>
    </div>
  );
}
