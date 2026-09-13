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
  const market = c.cityView?.markets?.find((item) => item.good === good);
  const cargo = Object.entries(ship.cargo).filter(([, amount]) => amount > 0);
  const cargoTotal = inventoryTotal(ship.cargo);
  const available =
    target === "ship" ? ship.cargo[good] : storage.stock_by_good[good];
  const tradeReason = !c.cityView?.has_live_visibility
    ? "Keine aktuelle Marktpräsenz in diesem Hafen."
    : target === "ship" && !inPort
      ? "Das ausgewählte Schiff liegt nicht in diesem Hafen."
      : target === "private_storage" && !storage.active
        ? "Hier besitzt du noch kein Kontor."
        : !Number.isInteger(qty) || qty < 1 || qty > 200
          ? "Menge zwischen 1 und 200 wählen."
          : side === "sell" && qty > available
            ? `Nur ${available} Last ${label(good)} ${target === "ship" ? "an Bord" : "im Kontor"} verfügbar.`
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
      <section className="panel cargo-panel" aria-label="Schiffsladung">
        <div className="section-heading">
          <div>
            <p className="eyebrow">AN BORD · {ship.name}</p>
            <h2>Deine Schiffsladung</h2>
          </div>
          <strong>
            {cargoTotal} / {ship.capacity_total} Last
          </strong>
        </div>
        <p className="cargo-space">
          {ship.capacity_total - cargoTotal} Last frei · höchstens{" "}
          {ship.max_per_good} je Ware
        </p>
        {cargo.length ? (
          <div className="cargo-list">
            {cargo.map(([cargoGood, amount]) => (
              <button
                key={cargoGood}
                aria-pressed={good === cargoGood}
                disabled={c.busy}
                onClick={() => setGood(cargoGood)}
              >
                <span>{label(cargoGood)}</span>
                <strong>{amount} Last</strong>
              </button>
            ))}
          </div>
        ) : (
          <p className="empty-cargo">
            Das Schiff ist leer. Kaufe Waren am Markt oder lade sie aus deinem
            Kontor ein.
          </p>
        )}
        {!inPort && (
          <p className="reason">
            {ship.at_sea
              ? `Unterwegs nach ${label(ship.destination!)}.`
              : `Dieses Schiff liegt in ${label(ship.current_city!)}.`}{" "}
            Handel ist erst im selben Hafen möglich.
          </p>
        )}
      </section>
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
                  <th>An Bord</th>
                </tr>
              </thead>
              <tbody>
                {c.cityView.markets.map((m) => (
                  <tr
                    key={m.good}
                    className={m.good === good ? "highlight" : ""}
                    onClick={() => {
                      if (!c.busy) setGood(m.good);
                    }}
                  >
                    <th>
                      <button
                        className="text-button"
                        disabled={c.busy}
                        aria-pressed={m.good === good}
                        onClick={() => setGood(m.good)}
                      >
                        {label(m.good)}
                      </button>
                    </th>
                    <td>{m.stock} / 200</td>
                    <td>{money(m.stadt_verkaufspreis)}</td>
                    <td>{money(m.stadt_ankaufspreis)}</td>
                    <td className={ship.cargo[m.good] ? "stock-present" : ""}>
                      {ship.cargo[m.good]} Last
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
      <section className="panel goods-panel" aria-label="Warendetails">
        <div className="goods-overview" aria-live="polite" aria-atomic="true">
          <p className="eyebrow">AUSGEWÄHLTE WARE · {label(c.city)}</p>
          <h2>{label(good)}</h2>
          <div className="goods-stock-grid">
            <div>
              <span>An Bord · {ship.name}</span>
              <strong>{ship.cargo[good]} Last</strong>
            </div>
            <div>
              <span>Im Kontor · {label(c.city)}</span>
              <strong>
                {storage.active
                  ? `${storage.stock_by_good[good]} Last`
                  : "Kein Kontor"}
              </strong>
            </div>
          </div>
          {market ? (
            <>
              <p className="market-age">
                {c.cityView?.has_live_visibility
                  ? "Aktuelle Marktpreise je Last"
                  : `Letzter Marktbericht · vor ${c.cityView?.days_stale} Tagen`}
              </p>
              <dl className="goods-prices">
                <div>
                  <dt>Du kaufst für</dt>
                  <dd>{money(market.stadt_verkaufspreis)}</dd>
                </div>
                <div>
                  <dt>Du verkaufst für</dt>
                  <dd>{money(market.stadt_ankaufspreis)}</dd>
                </div>
              </dl>
              <p className="fine-print">
                Marktbestand: {market.stock} / 200 Last · Tagesproduktion{" "}
                {market.production_rate} · Verbrauch {market.consumption_rate}
              </p>
            </>
          ) : (
            <p className="reason">
              Für diesen Hafen sind noch keine Marktpreise bekannt.
            </p>
          )}
        </div>
        <h3>Waren handeln</h3>
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
        <details className="transfer-details">
          <summary>Zwischen Schiff und Kontor umladen</summary>
          <p>
            Kontor: {inventoryTotal(storage.stock_by_good)} /{" "}
            {storage.capacity_total} Last · höchstens {storage.max_per_good} je
            Ware
          </p>
          <p>
            Menge: {qty} Last {label(good)}. Die Menge kannst du oben ändern.
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
        </details>
      </section>
    </div>
  );
}
