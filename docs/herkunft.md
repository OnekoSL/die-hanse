# Herkunft und Quellstände

Stand: 13. September 2026. Die Zusammenführung wurde vom Projektinhaber OnekoSL beauftragt; eigener Spielcode wird unter PolyForm Noncommercial 1.0.0 veröffentlicht.

| Quelle | Festgehaltener Stand | Verwendung |
| --- | --- | --- |
| A: Hanse – Handelssimulation | Git HEAD `b877c384d9b4221e75ec73ddf6e48842a36eb48f` | Python-Engine, API, SQLite-Zugriff, React-Aufteilung, Backtest und Tauri-Hülle als Ausgangscode |
| B: Hanse – Dein Handelshaus | Lokaler C#-Projektstand vom 12./13. September 2026; kein verifizierter Git-Commit | Fachliche Referenz für zusätzliche Städte, Grundwaren, Kalender und Monatsberichte |

[quellstaende.json](quellstaende.json) erfasst SHA-256-Prüfsummen der relevanten Ausgangsdateien. Die ursprüngliche Vergleichsanalyse liegt weiterhin im Vorgängerprojekt. [Spielkonzept](spielkonzept.md) und [Entscheidungen](entscheidungen.md) dokumentieren die ausgewählte Zusammenführung eigenständig.

## Übernahme und Änderungen

Aus A wurden die benötigten Quell-, Szenario-, Test- und Builddateien übernommen. Geldformat, Handel, Zeit, Bauaufträge, Spielstände, Oberfläche und Prozessverwaltung wurden gezielt überarbeitet. Der Backtest bleibt als separates Entwicklungswerkzeug erhalten. Die bisherigen sechs Städte und sechs Waren werden unmittelbar auf elf und neun erweitert.

Aus B wurde keine C#-Engine, ausführbare Datei oder Laufzeitabhängigkeit übernommen. Seine Monatsrunden und erzwungenen Rückfahrten werden durch den gemeinsamen Tageskalender und freie Reisen ersetzt. Personal, Produktionsfreischaltungen und Gefahren sind spätere Ausbaustufen.

Die alte Seekarte, Porträts, Rastergrafiken, Schriftdateien, Datenbanken, Spielstände, Logs und Buildausgaben wurden nicht übernommen. Karte und Symbole wurden für dieses Projekt neu als einfache Vektoren gestaltet; die Anwendung verwendet Systemschriften. Die neue Anwendung benötigt keinen Vorgängerordner.

## Bibliotheken

Versionen stehen in Python-Constraints, npm-Lockdateien und Cargo.lock. [THIRD-PARTY-NOTICES.txt](../THIRD-PARTY-NOTICES.txt) enthält komponentenbezogene Hinweise. Originale Lizenzergänzungen liegen unter `licenses/third-party/`; MPL-Quellen werden zusätzlich unverändert als `dependency-sources.zip` zum Release angeboten. Fremdbibliotheken behalten ihre jeweiligen Lizenzen.

Die alten Projekte und Spielstände wurden für Entwicklung und Tests nicht verändert. Die [Abnahme](abnahme.md) unterscheidet tatsächlich ausgeführte Prüfungen von noch offenen Umgebungsprüfungen.
