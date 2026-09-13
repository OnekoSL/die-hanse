# Interaktive Spielregeln

Die verbindlichen Alpha-Regeln, Preise, Kapazitäten, Reisedauern und Bauzeiten stehen im [Spielkonzept](../../docs/spielkonzept.md). Die [Architektur](../../docs/architektur.md) beschreibt Transaktionen und Speicherung, der [API-Vertrag](api.md) das Geldformat und die Befehle.

Regelquelle im Code: `backend/app/engine/game_world.py` und `game_engine.py`. Backend-Regeln sind maßgeblich; UI-Hilfsfunktionen berechnen Darstellung und Sperrgründe. Vorschau und Buchung benutzen dieselbe Handelsfunktion.

Der Backtest unter `simulation.py`, `pricing.py` und `strategy.py` ist ein getrenntes Entwicklungswerkzeug mit eigenen JSON-Szenarien. Seine Geldwerte und Zeitregeln werden durch die Alpha nicht angeglichen. Szenarioformat: [scenario-format.md](scenario-format.md).
