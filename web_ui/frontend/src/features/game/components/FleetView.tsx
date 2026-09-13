import { useState } from "react";
import { api } from "../../../api-client/client";
import type { GameController } from "../useGameController";
import { label, money, dateAt } from "../display";
import { inventoryTotal } from "../model";
export function FleetView({ c }: { c: GameController }) {
  const state = c.state!;
  const [shipClass, setShipClass] = useState("kogge_standard");
  const item = c.catalog?.ships.find((s) => s.id === shipClass);
  return (
    <div className="two-columns">
      <section className="panel">
        <p className="eyebrow">DEIN HANDELSHAUS</p>
        <h2>Flotte</h2>
        {state.ships.map((ship) => (
          <article className="asset-card" key={ship.id}>
            <h3>{ship.name}</h3>
            <p>
              {ship.at_sea
                ? `Unterwegs nach ${label(ship.destination!)} · Ankunft ${dateAt(state.current_day + ship.eta_days)}`
                : `Im Hafen von ${label(ship.current_city!)}`}
            </p>
            <p>
              {inventoryTotal(ship.cargo)} / {ship.capacity_total} Last ·{" "}
              {ship.max_per_good} je Ware
            </p>
            <p>
              {Object.entries(ship.cargo)
                .filter(([, q]) => q > 0)
                .map(([g, q]) => `${q} ${label(g)}`)
                .join(" · ") || "Keine Ladung"}
            </p>
            <div className="button-row">
              <button
                aria-pressed={ship.id === state.active_ship_id}
                disabled={c.busy || ship.id === state.active_ship_id}
                onClick={() => c.command(() => api.gameSelectShip(ship.id))}
              >
                Schiff auswählen
              </button>
              <button
                disabled={
                  c.busy ||
                  ship.at_sea ||
                  inventoryTotal(ship.cargo) > 0 ||
                  state.ships.length === 1
                }
                onClick={() =>
                  c.command(() =>
                    api.gameShipSell({
                      city: ship.current_city!,
                      ship_id: ship.id,
                    }),
                  )
                }
              >
                Verkaufen · {money(Math.floor((ship.buy_price ?? 0) / 2))}
              </button>
            </div>
            {(ship.at_sea ||
              inventoryTotal(ship.cargo) > 0 ||
              state.ships.length === 1) && (
              <p className="reason">
                Verkauf benötigt ein leeres Schiff im Hafen; ein Schiff muss
                verbleiben.
              </p>
            )}
          </article>
        ))}
      </section>
      <section className="panel">
        <p className="eyebrow">WERFT</p>
        <h2>Schiff bestellen</h2>
        <p>Bauort: {label(c.city)}</p>
        <label>
          Schiffsklasse
          <select
            disabled={c.busy}
            value={shipClass}
            onChange={(e) => setShipClass(e.target.value)}
          >
            {c.catalog?.ships.map((s) => (
              <option key={s.id} value={s.id}>
                {label(s.id)}
              </option>
            ))}
          </select>
        </label>
        {item && (
          <>
            <p>
              {item.capacity_total} Last · {item.max_per_good} je Ware
            </p>
            <p>
              {money(item.buy_price)} · {item.build_days} Tage Bauzeit
            </p>
            <p>Verfügbar am {dateAt(state.current_day + item.build_days)}</p>
            <button
              className="primary"
              disabled={c.busy || state.cash < item.buy_price}
              onClick={() =>
                c.command(() =>
                  api.gameShipBuy({ city: c.city, ship_class_id: shipClass }),
                )
              }
            >
              Kostenpflichtig bestellen
            </button>
            {state.cash < item.buy_price && (
              <p className="reason">Für dieses Schiff fehlt noch Geld.</p>
            )}
          </>
        )}
      </section>
    </div>
  );
}
