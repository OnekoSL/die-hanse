import { useState } from "react";
import type { GameController } from "../useGameController";
export function SavesPanel({ c }: { c: GameController }) {
  const [name, setName] = useState("");
  return (
    <section className="panel">
      <p className="eyebrow">DEINE REISEN BEWAHREN</p>
      <h2>Spielstände</h2>
      <p>
        Jede erfolgreiche Spielaktion wird automatisch gespeichert. Benannte
        Spielstände bleiben zusätzlich erhalten.
      </p>
      {c.state && (
        <form
          className="save-form"
          onSubmit={(e) => {
            e.preventDefault();
            void c.saveGame(name);
          }}
        >
          <label>
            Name des Spielstands
            <input
              value={name}
              maxLength={80}
              onChange={(e) => setName(e.target.value)}
              disabled={c.busy}
              placeholder="Mein Handelshaus"
            />
          </label>
          <button disabled={c.busy || !name.trim()} className="primary">
            Neuen Speicherplatz anlegen
          </button>
        </form>
      )}
      {!c.saves.length && (
        <p className="muted">Noch keine benannten Spielstände.</p>
      )}
      {c.saves.map((slot) => (
        <article className="save-slot" key={slot.id}>
          <div>
            <h3>{slot.name}</h3>
            <p>Spielzeit: {slot.date}</p>
          </div>
          <div className="button-row">
            <button
              disabled={c.busy}
              onClick={() => {
                if (
                  !c.state ||
                  window.confirm(
                    `„${slot.name}“ laden? Der aktuelle Stand wird vorher gesichert.`,
                  )
                )
                  void c.loadGame(slot.id);
              }}
            >
              Laden
            </button>
            {c.state && (
              <button
                disabled={c.busy}
                onClick={() => {
                  if (
                    window.confirm(
                      `„${slot.name}“ mit dem aktuellen Spielstand überschreiben?`,
                    )
                  )
                    void c.saveGame(slot.name, slot.id);
                }}
              >
                Überschreiben
              </button>
            )}
          </div>
        </article>
      ))}
    </section>
  );
}
