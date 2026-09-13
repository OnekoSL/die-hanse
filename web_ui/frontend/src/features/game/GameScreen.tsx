import { useState } from "react";
import { api } from "../../api-client/client";
import { useGameController } from "./useGameController";
import { HarborMap } from "./components/HarborMap";
import { CityView } from "./components/CityView";
import { FleetView } from "./components/FleetView";
import { StorageView } from "./components/StorageView";
import { LogbookView } from "./components/LogbookView";
import { SavesPanel } from "./components/SavesPanel";
import { dateAt, label, money } from "./display";
export function GameScreen() {
  const c = useGameController();
  const [showSaves, setShowSaves] = useState(false);
  const [destination, setDestination] = useState("London");
  const state = c.state;
  const ship = state?.ship;
  const route = state?.routes.find(
    (r) => r.from === ship?.current_city && r.to === destination,
  );
  const alerts = (
    <>
      <div className="status-line" role="status">
        {c.busy ? "Wird verarbeitet …" : c.notice}
      </div>
      {c.error && (
        <div className="error" role="alert">
          {c.error}
          <button onClick={() => c.refresh()}>Erneut laden</button>
        </div>
      )}
    </>
  );
  if (c.mode === "menu" || !state)
    return (
      <div className="menu-page">
        <div className="menu-card">
          <p className="eyebrow">NORD- UND OSTSEE · ANNO 1400</p>
          <div className="brand-mark" aria-hidden="true">
            ⚓
          </div>
          <h1>Die Hanse</h1>
          <p className="menu-subtitle">
            Dein Schiff. Dein Kontor. Dein Handelshaus.
          </p>
          <p>
            Elf Häfen verbinden die Meere. Kaufe Waren, entdecke Märkte und baue
            deine eigene Handelsflotte auf.
          </p>
          <div className="menu-actions">
            <button
              className="primary"
              disabled={c.busy || c.loading}
              onClick={() => {
                if (
                  !state ||
                  window.confirm(
                    "Neues Handelshaus gründen? Das bisherige Spiel wird vorher gesichert.",
                  )
                )
                  void c.newGame();
              }}
            >
              Neues Spiel
            </button>
            <button
              disabled={!state || c.busy}
              onClick={() => {
                c.enter(state!);
              }}
            >
              Fortsetzen
            </button>
            <button disabled={c.busy} onClick={() => setShowSaves(!showSaves)}>
              Spielstand laden
            </button>
          </div>
          {alerts}
          <p className="fine-print">
            Alpha 0.1 · Freie Handelsfahrten · Lokal gespeichert
          </p>
        </div>
        {showSaves && (
          <div className="menu-saves">
            <SavesPanel c={c} />
          </div>
        )}
      </div>
    );
  return (
    <div className="game-shell">
      <header className="topbar">
        <div className="brand">
          <span aria-hidden="true">⚓</span>
          <div>
            <h1>Die Hanse</h1>
            <small>DEIN HANDELSHAUS</small>
          </div>
        </div>
        <div className="top-stat">
          <small>SPIELZEIT</small>
          <strong>{dateAt(state.current_day)}</strong>
        </div>
        <div className="top-stat">
          <small>BARVERMÖGEN</small>
          <strong>{money(state.cash)}</strong>
        </div>
        <button onClick={() => c.setMode("menu")} disabled={c.busy}>
          Hauptmenü
        </button>
      </header>
      <div className="workspace">
        <aside className="sidebar">
          <p className="eyebrow">HANDELSKOMPASS</p>
          <label>
            Ausgewähltes Schiff
            <select
              value={state.active_ship_id}
              disabled={c.busy}
              onChange={(e) =>
                c.command(() => api.gameSelectShip(e.target.value))
              }
            >
              {state.ships.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <div className="ship-status">
            <strong>{ship!.name}</strong>
            <p>
              {ship!.at_sea
                ? `Auf See nach ${label(ship!.destination!)}`
                : `Im Hafen von ${label(ship!.current_city!)}`}
            </p>
            {ship!.at_sea && (
              <p>Ankunft {dateAt(state.current_day + ship!.eta_days)}</p>
            )}
          </div>
          <label>
            Hafen ansehen
            <select
              value={c.city}
              disabled={c.busy}
              onChange={(e) => c.setCity(e.target.value)}
            >
              {state.cities.map((city) => (
                <option key={city} value={city}>
                  {label(city)}
                </option>
              ))}
            </select>
          </label>
          <hr />
          <label>
            Reiseziel
            <select
              value={destination}
              disabled={c.busy || ship!.at_sea}
              onChange={(e) => setDestination(e.target.value)}
            >
              {state.cities.map((city) => (
                <option key={city} value={city}>
                  {label(city)}
                </option>
              ))}
            </select>
          </label>
          <p className="reason">
            {ship!.at_sea
              ? "Dieses Schiff ist bereits unterwegs."
              : route
                ? `${route.days} Tage · Ankunft ${dateAt(state.current_day + route.days)}`
                : "Wähle einen anderen Zielhafen."}
          </p>
          <button
            className="primary"
            disabled={c.busy || !route || ship!.at_sea}
            onClick={() =>
              c.command(() =>
                api.gameSetCourse({
                  destination_city: destination,
                  ship_id: ship!.id,
                }),
              )
            }
          >
            Kurs setzen
          </button>
          <hr />
          <p className="eyebrow">ZEIT VERGEHEN LASSEN</p>
          <button
            disabled={c.busy}
            onClick={() => c.command(api.gameAdvanceDay)}
          >
            Einen Tag weiter
          </button>
          <button
            disabled={c.busy}
            onClick={() => c.command(api.gameAdvanceNextEvent)}
          >
            Bis zum nächsten Ereignis
          </button>
          <p className="fine-print">
            Stoppt bei Ankunft, Bauabschluss oder Monatswechsel.
          </p>
          <hr />
          <p className="eyebrow">BAUAUFTRÄGE</p>
          {state.orders.length ? (
            state.orders.map((o) => (
              <div className="order" key={o.id}>
                <strong>
                  {o.kind === "ship"
                    ? label(o.class_id!)
                    : `Kontor Stufe ${o.level}`}
                </strong>
                <p>
                  {label(o.city)} · {dateAt(o.due_day)}
                </p>
              </div>
            ))
          ) : (
            <p className="muted">Keine offenen Bauaufträge.</p>
          )}
        </aside>
        <main className="game-main">
          {alerts}
          <HarborMap
            cities={state.cities}
            selected={c.city}
            onSelect={c.setCity}
            disabled={c.busy}
          />
          <nav className="game-tabs" aria-label="Spielbereiche">
            {["Handel", "Flotte", "Kontore", "Handelsbuch", "Spielstände"].map(
              (tab) => (
                <button
                  key={tab}
                  aria-current={c.tab === tab ? "page" : undefined}
                  onClick={() => c.setTab(tab)}
                >
                  {tab}
                </button>
              ),
            )}
          </nav>
          {c.tab === "Handel" && <CityView c={c} />}
          {c.tab === "Flotte" && <FleetView c={c} />}
          {c.tab === "Kontore" && <StorageView c={c} />}
          {c.tab === "Handelsbuch" && <LogbookView c={c} />}
          {c.tab === "Spielstände" && <SavesPanel c={c} />}
          <footer>Die Hanse · Alpha 0.1 · Alle Geldbeträge in Mark</footer>
        </main>
      </div>
    </div>
  );
}
