# Webentwicklung

Voraussetzungen: Python 3.11 und Node.js 22. Windows/PowerShell, vom Projektstamm:

```powershell
py -3.11 -m venv web_ui/backend/.venv
& ./web_ui/backend/.venv/Scripts/python.exe -m pip install -r web_ui/backend/requirements.txt -r web_ui/backend/requirements-dev.txt
npm.cmd --prefix web_ui/frontend ci
```

API in einer Konsole starten:

```powershell
$env:HANSE_DB_PATH = Join-Path $PWD 'local/development.db'
& ./web_ui/backend/.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir web_ui/backend --host 127.0.0.1 --port 8000
```

Frontend in einer zweiten Konsole: `npm.cmd --prefix web_ui/frontend run dev`, anschließend `http://127.0.0.1:5173`. Der Client verwendet standardmäßig API-Port 8000; `VITE_API_URL` überschreibt die API-Adresse. Desktop-Builds verwenden `.env.desktop` mit Port 18522.

## Prüfen

Vom Stamm `./scripts/test.ps1` ausführen. Das Skript setzt eine eigene temporäre Testdatenbank und stellt die vorherige Umgebungsvariable wieder her. API-Tests ohne `HANSE_DB_PATH` werden absichtlich abgewiesen; niemals die Spieler-Datenbank für Tests verwenden.

Backend einzeln: aus `web_ui/backend` mit dem venv-Interpreter `-m ruff check .` und `-m pytest`; zuvor eigene `HANSE_DB_PATH` setzen. Frontend: `npm.cmd --prefix web_ui/frontend test` und `npm.cmd --prefix web_ui/frontend run build`.

## Struktur

- `backend/app/engine/`: deterministische Spielregeln und separater Backtest.
- `backend/app/api/`: HTTP-Verträge und serialisierte Spielbefehle.
- `backend/app/infra/`: SQLite und versionierte vollständige Spielstände.
- `frontend/src/features/game/`: Steuerung, Darstellung und reine UI-Hilfsfunktionen.
- `data/scenarios/`: Backtest-Szenarien; keine interaktive Spielwelt.

[Regeln](docs/rules.md), [API](docs/api.md), [Szenarioformat](docs/scenario-format.md), [Windows-Build](../lokal_exe/README.md).
