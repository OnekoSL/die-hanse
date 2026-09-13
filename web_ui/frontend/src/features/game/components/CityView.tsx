import { useEffect, useState } from "react";
import { api } from "../../../api-client/client";
import type { MarketTradeAction, TradeQuote } from "../../../api-client/types";
import type { GameController } from "../useGameController";
import { label, money } from "../display";
import { inventoryTotal } from "../model";
export function CityView({ c }: { c: GameController }) {
  const state = c.state!;
  const ship = state.ship;
  const storage = state.private_storages.find((s) => s.city === c.city)!;
  const [good, setGood] = useState("Salz");
  const [qty, setQty] = useState(1);
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [target, setTarget] = useState<"ship" | "private_storage">("ship");
  const [quote, setQuote] = useState<TradeQuote>();
  useEffect(
    () => setQuote(undefined),
    [good, qty, side, target, c.city, state.revision],
  );
  const inPort = !ship.at_sea && ship.current_city === c.city;
  const tradeReason = !c.cityView?.has_live_visibility
    ? "Keine aktuelle Marktpräsenz in diesem Hafen."
    : target === "ship" && !inPort
      ? "Das ausgewählte Schiff liegt nicht in diesem Hafen."
      : target === "private_storage" && !storage.active
        ? "Hier besitzt du noch kein Kontor."
        : !Number.isInteger(qty) || qty < 1 || qty > 200
          ? "Menge zwischen 1 und 200 wählen."
          : "";
  const action: MarketTradeAction = {
    type: side,
    city: c.city,
    good,
    qty,
    counterparty: target,
    ship_id: ship.id,
  };
  return (
    <div className="trade-layout">
      <section className="panel market-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">STADTMARKT</p>
            <h2>{label(c.city)}</h2>
          </div>
          <span className="badge">
            Hauptware: {label(state.city_primary_goods[c.city])}
          </span>
        </div>
        <p className="muted">
          {c.cityView?.has_live_visibility
            ? "Aktuelle Preise durch eigene Präsenz"
            : c.cityView?.visibility_level === "stale"
              ? `Letzter Bericht vor ${c.cityView.days_stale} Tagen`
              : "Noch keine Marktinformationen. Reise zu diesem Hafen."}
        </p>
        {c.cityView?.markets ? (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Ware</th>
                  <th>Bestand</th>
                  <th>Du kaufst ab</th>
                  <th>Du verkaufst ab</th>
                  <th>Produktion / Verbrauch</th>
                </tr>
              </thead>
              <tbody>
                {c.cityView.markets.map((m) => (
                  <tr
                    key={m.good}
                    className={m.good === good ? "highlight" : ""}
                  >
                    <th>
                      <button
                        className="text-button"
                        disabled={c.busy}
                        onClick={() => setGood(m.good)}
                      >
                        {label(m.good)}
                      </button>
                    </th>
                    <td>{m.stock} / 200</td>
                    <td>{money(m.stadt_verkaufspreis)}</td>
                    <td>{money(m.stadt_ankaufspreis)}</td>
                    <td>
                      +{m.production_rate} / −{m.consumption_rate}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            Ein eigener Besuch oder ein Kontor erschließt diesen Markt.
          </div>
        )}
        <p className="fine-print">
          Preise gelten für die nächste Einheit. Größere Mengen verändern den
          Marktpreis; die Vorschau zeigt die verbindliche Gesamtsumme.
        </p>
      </section>
      <section className="panel">
        <p className="eyebrow">HANDELSAUFTRAG</p>
        <h2>Waren handeln</h2>
        <fieldset disabled={c.busy}>
          <label>
            Ware
            <select value={good} onChange={(e) => setGood(e.target.value)}>
              {Object.keys(ship.cargo).map((g) => (
                <option key={g} value={g}>
                  {label(g)}
                </option>
              ))}
            </select>
          </label>
          <div className="form-pair">
            <label>
              Aktion
              <select
                value={side}
                onChange={(e) => setSide(e.target.value as typeof side)}
              >
                <option value="buy">Kaufen</option>
                <option value="sell">Verkaufen</option>
              </select>
            </label>
            <label>
              Menge
              <input
                type="number"
                min="1"
                max="200"
                step="1"
                value={qty}
                onChange={(e) => setQty(Number(e.target.value))}
              />
            </label>
          </div>
          <label>
            Lagerort
            <select
              value={target}
              onChange={(e) => setTarget(e.target.value as typeof target)}
            >
              <option value="ship">{ship.name}</option>
              <option value="private_storage">Kontor {label(c.city)}</option>
            </select>
          </label>
          {tradeReason && <p className="reason">{tradeReason}</p>}
          <button
            disabled={!!tradeReason}
            onClick={() => {
              setQuote(undefined);
              void c.run(() => api.gameQuote(action), setQuote);
            }}
          >
            Handelsvorschau
          </button>
          {quote && quote.revision === state.revision && (
            <div className="quote" role="status">
              <p>
                {quote.action.qty} {label(quote.action.good)}{" "}
                {quote.action.type === "buy" ? "kaufen" : "verkaufen"}
              </p>
              <strong>{money(quote.total)}</strong>
              <button
                className="primary"
                onClick={() => {
                  const q = quote;
                  setQuote(undefined);
                  void c.command(() =>
                    api.gameMarketTrade({ ...q.action, revision: q.revision }),
                  );
                }}
              >
                Handel bestätigen
              </button>
            </div>
          )}
        </fieldset>
        <hr />
        <h3>Ladung & Kontor</h3>
        <p>
          {ship.name}: {inventoryTotal(ship.cargo)} / {ship.capacity_total} Last
          · höchstens {ship.max_per_good} je Ware
        </p>
        <p>
          Kontor: {inventoryTotal(storage.stock_by_good)} /{" "}
          {storage.capacity_total} Last · höchstens {storage.max_per_good} je
          Ware
        </p>
        <p>
          {label(good)}: {ship.cargo[good]} im Schiff ·{" "}
          {storage.stock_by_good[good]} im Kontor
        </p>
        <div className="button-row">
          <button
            disabled={
              c.busy ||
              !inPort ||
              !storage.active ||
              qty < 1 ||
              !Number.isInteger(qty)
            }
            onClick={() =>
              c.command(() =>
                api.gameTransfer({
                  city: c.city,
                  good,
                  qty,
                  ship_id: ship.id,
                  direction: "ship_to_private",
                }),
              )
            }
          >
            Ins Kontor entladen
          </button>
          <button
            disabled={
              c.busy ||
              !inPort ||
              !storage.active ||
              qty < 1 ||
              !Number.isInteger(qty)
            }
            onClick={() =>
              c.command(() =>
                api.gameTransfer({
                  city: c.city,
                  good,
                  qty,
                  ship_id: ship.id,
                  direction: "private_to_ship",
                }),
              )
            }
          >
            Schiff beladen
          </button>
        </div>
        {(!inPort || !storage.active) && (
          <p className="reason">
            Umladen benötigt Schiff und eigenes Kontor im selben Hafen.
          </p>
        )}
      </section>
    </div>
  );
}
