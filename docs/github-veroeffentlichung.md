# GitHub und Alpha-Veröffentlichung

Öffentliches Repository: [OnekoSL/die-hanse](https://github.com/OnekoSL/die-hanse). Anzeigename „Die Hanse“, Repository-Name `die-hanse`.

Die Planung wurde zuerst veröffentlicht. Es folgt die spielbare Windows-x64-Vorabversion `v0.1.0-alpha.1` mit Quellcode, MSI, `SHA256SUMS.txt`, `dependency-sources.zip`, Bauanleitung und bekannten Einschränkungen. Die MSI-interne Produktversion ist wegen der Windows-Installer-Vorgaben `0.1.0`; Tag, API, Cargo- und npm-Version kennzeichnen die Alpha.

## Prüfungen vor einem Release

1. Ruff, Backend-Tests mit eigener temporärer Datenbank, Frontend-Tests und TypeScript/Vite-Build ausführen.
2. Installer bauen, installieren, Handel und Ausbau prüfen, schließen und fortsetzen; belegten Backend-Port und Prozessende prüfen.
3. Browserprüfung, Tastaturbedienung, Dokumentation, Herkunft und Fremdlizenzen kontrollieren. Umgebungsgrenzen im [Abnahmeprotokoll](abnahme.md) nennen.
4. Quellcode auf GitHub veröffentlichen und CI-Ergebnis kontrollieren.
5. MSI und Quellenarchiv prüfen, SHA-256-Datei erstellen und gemeinsam als Vorabversion veröffentlichen.

Keine Datenbanken, lokalen Speicherstände, Zugangsdaten, Logs, virtuellen Umgebungen oder Buildverzeichnisse ins Repository aufnehmen. Alte Medien bleiben ausgeschlossen. Änderungen erfolgen auf `codex/`-Branches; veröffentlichte Tags werden nicht nachträglich verschoben.

Spätere Versionen müssen Format-, Welt- und Regelversion getrennt behandeln. Unbekannte Speicherstände werden erhalten und abgewiesen, bis eine ausdrücklich entwickelte Migration vorliegt.
