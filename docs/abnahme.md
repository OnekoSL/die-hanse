# Abnahmeprotokoll – 0.1.0-alpha.1

Stand: 13. September 2026. Implementierte Basis; öffentliche MSI-Freigabe wartet noch auf den unten genannten Umgebungstest oder eine ausdrücklich akzeptierte Testlücke.

## Automatisierte Prüfungen

| Prüfung | Ergebnis |
| --- | --- |
| Ruff Backend | Bestanden |
| GitHub CI, Python 3.11 / Node 22 unter Linux | Backend und Frontend bestanden ([Lauf](https://github.com/OnekoSL/die-hanse/actions/runs/34757176610)) |
| Backend Python 3.11.16, eigene temporäre SQLite-Datei | 75 Tests bestanden |
| Frontend Node.js 22.23.2, Vitest | 15 Tests bestanden |
| TypeScript und Vite, Web- und Desktop-Modus | Bestanden |
| Windows x64 / Tauri / PyInstaller / MSI | Installer gebaut und lokal installiert |
| Unabhängiger Windows-Build auf GitHub (Windows Server 2022) | Tests, MSI-Build und Artefaktbereitstellung bestanden ([Lauf](https://github.com/OnekoSL/die-hanse/actions/runs/34757328416)); keine interaktive Installationsabnahme auf diesem Runner |

Die Backend-Tests prüfen unter anderem alle elf erreichbaren Häfen und neun Waren, Handelsvorschau/Buchung/Teilkäufe, Grenzen, ungültige Aktionen ohne Zustandsänderung, veraltete und gleichzeitig eingereichte Vorschauen, Marktinformationsalter, Bauzeiten, Monatswechsel und gleichzeitige Ereignisse, Speicherplätze, beschädigte/incompatible Stände und Neustarts. Ein simulierter Commit-Fehler ergibt keine Erfolgsmeldung und verändert den Zustand nicht.

Ausgangsmessung vor Regeländerungen in der isolierten A-Kopie: 62 Backend-Tests und Ruff bestanden, neun reine Frontend-Modelltests bestanden. Die alten UI-Tests benötigten ausgeschlossene Porträts; sie wurden für die neue eigenständige Oberfläche ersetzt. Die neuen UI-Integrationstests laufen mit jsdom und werden durch den tatsächlichen Browsertest ergänzt.

## Tatsächlicher Browser

Im Chromium-basierten Browser mit dem lokalen Backend ausgeführt:

1. Neues Spiel am 1. März 1400 mit 1.000,00 Mark.
2. Zehn Salz in Lübeck: Vorschau und Kauf 109,85 Mark; zehn Einheiten an Bord.
3. Fünf Tage nach London reisen, Schiff bleibt dort; Verkauf 202,63 Mark, Bargeld 1.092,78 Mark.
4. Benannten Spielstand „Erste Londonreise“ speichern; Seite neu laden und fortsetzen: Datum, Hafen und Bargeld erhalten.
5. Lübecker Kontor für 350,00 Mark ausbauen; vor Fertigstellung Stufe 1 und gesperrter zweiter Auftrag, am 13. März Stufe 2 mit 140 Last.
6. Bis 1. April vorspulen: Märzbericht mit 1.000,00 Anfangsgeld, 202,63 Warenverkäufen, 109,85 Einkäufen, 350,00 Ausbauausgaben und 742,78 Endgeld.
7. Tabulator und Eingabetaste öffnen den Spielbereich; sichtbarer goldener Fokusrahmen im Screenshot geprüft. Beschriftete Hafenliste entspricht den elf Kartenhäfen.

Darstellung von Markt, Vorschau, Karte und Kontoren visuell geprüft; keine Browser-Konsolenfehler beobachtet.

## Installiertes Windowsprogramm

Auf dem vorhandenen Windows 10 x64 (Build 19045) den MSI erfolgreich pro Benutzer installiert. Start aus einem fremden Arbeitsverzeichnis mit auf Windows-Systemverzeichnisse reduziertem PATH funktioniert: Python und Node.js werden nicht aus einer Entwicklerinstallation benötigt. WebView2 ist auf diesem Rechner bereits vorhanden.

Installierter Backend-Ablauf über seine HTTP-Schnittstelle geprüft: Kaufen → Londonreise → Verkaufen → Kontorausbau → Bauabschluss → benannten Stand während der Bauzeit laden. Nach regulärem Schließen per Alt+F4 sind Anwendung und eigener API-Port beendet. Nach erneutem Start stimmt die vollständige aktive Sitzung einschließlich Revision, Reise-/Baudaten, Märkten und Chronik exakt mit dem gespeicherten Zustand überein. Das native Startmenü wurde zusätzlich über den Windows-Zugänglichkeitsbaum kontrolliert.

Die native Bildschirmaufnahme des Automationswerkzeugs wird auf diesem Windows-Build nicht unterstützt; deshalb erfolgte die visuelle und vollständige Bedienprüfung im Browser. Der native Spielablauf wurde über das installierte Backend geprüft, nicht als vollständiger Maus-Test des WebView-Fensters ausgegeben.

Mit dem abschließenden Installer geprüft: Ein zweiter Start bei belegtem Port zeigt einen verständlichen Windows-Dialog. Nach dessen Bestätigung endet nur die zweite Instanz; die zuerst gestartete Sitzung und ihr Backend bleiben unverändert erreichbar. Der beim Test gefundene Tauri-Setup-Abbruch wurde vor dem abschließenden Build korrigiert.

Weitere Fehlerprüfungen bestanden: Ein vorzeitig endendes Backend und ein absichtlich nicht antwortender Testprozess führen zu verständlichen Meldungen. Nach dem 30-Sekunden-Timeout ist der eigene Testprozess beendet. Auch beim erzwungenen Ende der Hauptanwendung beendet das Windows-Jobobjekt deren Backend; der Port bleibt frei.

MSI-Prüfsumme (SHA-256): `81d21e5bd86b4d7fd105357bbf225592c57fceefb63cbc4266b97d9e93a583d6`. Der Installer, die Prüfsummendatei und das Quellenarchiv der MPL-Komponenten sind als GitHub-Release-Entwurf vorbereitet.

## Noch offene Umgebungsabnahme

Ein frisch aufgesetztes Windows ohne vorhandene WebView2 Runtime beziehungsweise eine frische Windows-VM ist hier nicht verfügbar. Erstinstallation dieser Runtime und ein vollständiger Bedienablauf auf einem solchen System sind deshalb **nicht als bestanden erklärt**. Eine öffentliche MSI-Freigabe setzt diesen Test oder die ausdrücklich akzeptierte Veröffentlichung als Alpha mit dieser Testlücke voraus.

## Bekannte Einschränkungen

- Erste Startbalance; kein Nachweis langfristiger Wirtschafts-Balance.
- Verwalter, automatische Routen, Produktion, Verderb, Gefahren und Altimporte fehlen bewusst.
- Backtest nutzt weiterhin seine eigenen Regeln und Geldwerte.
- Installer ohne Codesignatur; Windows kann einen unbekannten Herausgeber anzeigen.
- Vollständige Snapshots und Chronik wachsen mit Spielzeit und Speicherplätzen; keine Lösch-/Archivverwaltung in dieser Alpha.
- Warnungen ohne Prüfungsfehler: FastAPI/Starlette-Testclient-Abkündigungen, React-Router-Zukunftshinweise, Diagrammgröße in jsdom und Vite-Hinweis zum über 500-kB-Bundle.

## Wiederholen

`./scripts/test.ps1` führt die vorgesehenen Prüfungen mit isolierter Datenbank aus. [Bauanleitung](../lokal_exe/README.md), [API](../web_ui/docs/api.md) und [Spielregeln](spielkonzept.md) bilden die Referenz für weitere Abnahmen. Vorgängerordner und deren Spielstände werden nicht für Tests benutzt.
