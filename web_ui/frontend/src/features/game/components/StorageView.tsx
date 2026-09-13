import { api } from "../../../api-client/client";
import type { GameController } from "../useGameController";
import { label, money, dateAt } from "../display";
import { inventoryTotal } from "../model";
export function StorageView({ c }: { c: GameController }) {
  const state = c.state!;
  return (
    <section className="panel">
      <p className="eyebrow">LAGER UND NIEDERLASSUNGEN</p>
      <h2>Kontore</h2>
      <div className="asset-grid">
        {state.private_storages.map((storage) => {
          const next = c.catalog?.storages.find(
            (s) => s.level === storage.level + 1,
          );
          const previous = c.catalog?.storages.find(
            (s) => s.level === storage.level - 1,
          );
          const building = state.orders.some(
            (o) => o.kind === "storage" && o.city === storage.city,
          );
          const canReduce =
            !building &&
            storage.level > 0 &&
            inventoryTotal(storage.stock_by_good) <=
              (previous?.capacity_total ?? 0) &&
            Object.values(storage.stock_by_good).every(
              (q) => q <= (previous?.max_per_good ?? 0),
            );
          return (
            <article className="asset-card" key={storage.city}>
              <h3>{label(storage.city)}</h3>
              <p>
                {storage.active
                  ? `Stufe ${storage.level} · ${inventoryTotal(storage.stock_by_good)} / ${storage.capacity_total} Last`
                  : "Noch kein Kontor"}
              </p>
              <p>
                {Object.entries(storage.stock_by_good)
                  .filter(([, q]) => q > 0)
                  .map(([g, q]) => `${q} ${label(g)}`)
                  .join(" · ") || "Keine Waren eingelagert"}
              </p>
              {next && (
                <>
                  <p>
                    {money(next.buy_price)} · fertig am{" "}
                    {dateAt(state.current_day + next.build_days)}
                  </p>
                  <button
                    disabled={c.busy || building || state.cash < next.buy_price}
                    onClick={() =>
                      c.command(() =>
                        api.gameStorageUpgrade({ city: storage.city }),
                      )
                    }
                  >
                    {storage.active ? "Ausbau bestellen" : "Kontor bestellen"}
                  </button>
                </>
              )}
              {storage.active && (
                <button
                  disabled={c.busy || !canReduce}
                  onClick={() =>
                    c.command(() => api.gameStorageSell({ city: storage.city }))
                  }
                >
                  Stufe verkaufen ·{" "}
                  {money(
                    c.catalog?.storages.find((s) => s.level === storage.level)
                      ?.sell_price ?? 0,
                  )}
                </button>
              )}
              <p className="reason">
                {building
                  ? "Bauauftrag läuft; bisheriges Lager bleibt nutzbar."
                  : next && state.cash < next.buy_price
                    ? "Für den Ausbau fehlt noch Geld."
                    : !next
                      ? "Höchste Kontorstufe erreicht."
                      : "Bauzeit: 7 Tage. Bezahlung bei Bestellung."}
              </p>
              {storage.active && !canReduce && !building && (
                <p className="reason">
                  Vor dem Rückbau Waren bis zur kleineren Lagergrenze entnehmen.
                </p>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
