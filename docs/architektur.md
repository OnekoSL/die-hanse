# Architektur

Beschlossen und umgesetzt: Python/FastAPI, React/TypeScript, SQLite und Tauri. Die Übernahme verwendet A-Engine, Preisbildung, Kapazitäts-/Reiseprüfungen, API-Struktur, SQLAlchemy, Backtest und React-Aufteilung. B liefert zusätzliche Weltdaten und fachliche Vorbilder; es läuft keine zweite Engine.

## Zuständigkeiten

React stellt dar und steuert Auswahl/Aktionen. Wirtschaftsregeln, Kalender und Buchungen liegen im Backend. API, Pydantic-Schemas, TypeScript-Verträge und Client werden gemeinsam gepflegt. `GameScreen`, `useGameController`, reine Hilfsfunktionen und Bereichskomponenten bleiben getrennt.

Der Backtest besitzt weiterhin eigene Preisformel, Strategie und Szenarien. Er bleibt unter `/backtest` ein Entwicklungswerkzeug. Der Haupteinstieg öffnet das Spielmenü.

## Speicherung

SQLite hält vollständige Snapshots in `game_snapshots`: ein automatischer Stand `active` sowie beliebig viele manuelle/archivierte Stände. Gespeichert werden Sitzung, Märkte, Kontore, Flotte, Reisen, Bauaufträge, Kalender, Monatsbuchungen/-berichte, Marktinformationen und Handelsbuch.

Formatversion 1, Weltversion `alpha-world-1`, Regelversion 1 und SHA-256-Prüfsumme sind voneinander getrennt. Struktur, Versionen, Preise, Waren, Kapazitäten und Reisen werden vor Verwendung geprüft. Unbekannte/beschädigte Stände werden unverändert erhalten. Ein gültiger Speicherplatz kann einen defekten automatischen Stand ablösen; dessen Originalbytes werden zuvor archiviert.

Jede Spieloperation verwendet `BEGIN IMMEDIATE` in einer SQLite-Transaktion. Lesen–Prüfen–Ändern–Speichern bleibt auch zwischen Prozessen serialisiert. Fehler rollen vollständig zurück. Erfolgreiche Befehle und Laden erzeugen eine neue Zustandsrevision; veraltete Handelsvorschauen liefern HTTP 409.

Altdatenbanken mit `game_sessions` werden vor der Initialisierung abgewiesen. Keine Tabellenlöschung, kein Weltreset. Altimporte und Migrationen sind spätere Arbeitspakete.

## Desktop

Kennung `com.onekosl.diehanse`, API `127.0.0.1:18522`, Daten `%AppData%/com.onekosl.diehanse/data/hanse.db`. Tauri startet ein PyInstaller-Verzeichnisbundle mit eigener Python-Laufzeit.

Ein Windows-Jobobjekt bindet die gestarteten Backendprozesse an die Anwendung. Healthcheckfehler und Beenden räumen eigene Prozesse auf. Keine PID-Dateien, kein Beenden fremder Prozesse oder Übernehmen eines laufenden Backends. Ein belegter Port führt zur Startfehlermeldung.

MSI-Produktversion: 0.1.0; Git-Tag, API und Quellpakete: `v0.1.0-alpha.1`. MSI erfordert hier eine numerische Version. Projekt- und Fremdlizenzhinweise werden mitinstalliert.
