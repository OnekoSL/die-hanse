# Windows-Anwendung bauen

Die Hanse verwendet Tauri 2 und ein mit PyInstaller gebündeltes Python-Backend. Zum Spielen sind weder Python noch Node.js erforderlich. Windows x64 und die WebView2 Runtime werden benötigt. Bei fehlender Runtime kann deren Installation während des MSI-Setups Internetzugriff benötigen.

## Voraussetzungen

Python 3.11, Node.js 22, Rust mit Ziel `x86_64-pc-windows-msvc`, Visual Studio 2022 Community oder Build Tools mit C++ und Windows SDK. Aus einer PowerShell im Projektstamm:

```powershell
py -3.11 -m venv web_ui/backend/.venv
& ./web_ui/backend/.venv/Scripts/python.exe -m pip install -r web_ui/backend/requirements-build.txt -r web_ui/backend/requirements-dev.txt
npm.cmd --prefix web_ui/frontend ci
npm.cmd --prefix lokal_exe ci
./scripts/test.ps1
npm.cmd --prefix lokal_exe run build:msi
```

Ergebnis: `lokal_exe/src-tauri/target/release/bundle/msi/Die Hanse_0.1.0_x64_en-US.msi`. Der Release benennt es als `Die-Hanse-0.1.0-alpha.1-windows-x64.msi`. MSI benötigt eine numerische Produktversion; die öffentliche Vorabversion heißt `v0.1.0-alpha.1`.

Der Build erstellt das Frontend, ein PyInstaller-Ordnerpaket inklusive Python/Abhängigkeiten/Szenarien sowie den Tauri-Installer mit Lizenzhinweisen. Bestehende Lockdateien und Python-Constraints verwenden. Keine Vorgängerinstallation oder Quelldatei wird zur Laufzeit benötigt.

## Laufzeit und Fehlerdiagnose

Anwendungskennung: `com.onekosl.diehanse`. Daten und Logs unter `%AppData%/com.onekosl.diehanse/`, Spielstände in `data/hanse.db`. API ausschließlich auf `127.0.0.1:18522`. Bei belegtem Port erscheint eine Meldung; der dort laufende Prozess bleibt erhalten.

Tauri hält ausschließlich seinen gestarteten Backendprozess und dessen Windows-Job. Ende und fehlgeschlagener Start beenden diesen eigenen Prozessbaum. Es gibt keine PID-Datei und kein Beenden fremder Prozesse. Logs stehen im eigenen Anwendungsdatenordner unter `logs/`.

`HANSE_BACKEND_BIN` und `HANSE_SCENARIO_DIR` sind optionale Entwicklerüberschreibungen. Normale Installationen benötigen sie nicht.

## Lizenzen und Freigabe

`THIRD-PARTY-NOTICES.txt` und die Projektlizenztexte werden mit installiert. Für aktualisierte Abhängigkeiten zuerst `cargo metadata --locked --filter-platform x86_64-pc-windows-msvc --format-version 1` als UTF-8 nach `local/cargo-metadata.json` schreiben; danach mit dem Backend-Interpreter `scripts/generate-notices.py` ausführen. Ergänzende Originaltexte liegen unter `licenses/third-party/`.

Zum Release gehören MSI, SHA-256-Prüfsumme und `dependency-sources.zip` für enthaltene MPL-Komponenten. [Abnahmeprotokoll und Einschränkungen](../docs/abnahme.md).
