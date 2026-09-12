# Festlegungen und offene Entscheidungen

Stand: 12. September 2026.

**Festgelegt** bezeichnet eine ausdrückliche Vorgabe des Projektinhabers; deren konkrete Umsetzung ist gegebenenfalls zusätzlich benannt. **Vorschlag** bezeichnet die aktuelle Empfehlung. **Offen** bedeutet, dass vor dem betroffenen Arbeitspaket eine Entscheidung benötigt wird. Keine dieser offenen Fragen verhindert das Weiterarbeiten an unabhängigen Planungsunterlagen.

## Register

| ID | Thema | Status | Inhalt / Vorschlag | Benötigt vor |
| --- | --- | --- | --- | --- |
| D-01 | Name und Projektort | Festgelegt | Zusammenführung im neuen Ordner „Die Hanse“; zuerst Planung | Erfüllt |
| D-02 | GitHub-Veröffentlichung | Festgelegt | Projekt „Die Hanse“ öffentlich veröffentlichen; als Repository `die-hanse` unter dem verbundenen Konto `OnekoSL` umgesetzt | Erster Upload |
| D-03 | Lizenz | Nutzungsziel festgelegt; Planungslizenz umgesetzt | Nichtkommerzielle Nutzung; für den jetzigen Planungsstand CC BY-NC 4.0. Konkrete Softwarelizenz für späteren Code noch offen; fremde Grafiken gesondert prüfen | Erfüllt für Planung; Code vor Übernahme klären |
| D-04 | Technische Basis | Vorschlag | Python/FastAPI + React/TypeScript + SQLite + Tauri weiterführen; B-Regeln fachlich portieren | M1 |
| D-05 | Regelmodell | Vorschlag | Eine Engine; freie lokale Märkte und Tagesreisen, ergänzt um Monatsabrechnung | M2/M3 |
| D-06 | Erster öffentlicher Umfang | Reihenfolge festgelegt | Zunächst Planungsrepository, anschließend spielbare Zusammenführung; erste gemeinsame Vorabfassung nach M4 weiterhin vorgeschlagen | Erfüllt für Planung |
| D-07 | Code und Vorgängerhistorie | Vorschlag | Gezielte Codeübernahme in eigenständiges Repository; Herkunft dokumentieren, alte Git-Historie nicht pauschal übertragen | M1 und Codeveröffentlichung |
| D-08 | Geldformat | Offen, Empfehlung vorhanden | Ganze kleinste Recheneinheiten; einheitliche Rundung; Altwerte explizit konvertieren | M2 |
| D-09 | Kalender und Ereignisreihenfolge | Offen | Start März 1400 vorgeschlagen; Tages-/Monatslängen, gleiche Zeitpunkte, Verkäufe vor Lohnzahlung und Dienstbeginn festlegen | M3 |
| D-10 | Kontore und Personal | Vorschlag | Vier A-Stufen behalten; zusätzliche Freischaltungen anfügen; nur Automatisierung benötigt bezahltes Personal | M3/M4 |
| D-11 | Lager und Verderb | Offen, Empfehlung vorhanden | Bestehende Gesamt-/Pro-Ware-Limits; kein Abschneiden importierter Bestände; Alter bei Transfers erhalten; Verderb auf See gesondert entscheiden | M6 |
| D-12 | Manufakturen | Vorschlag | Erst lokale Warenfreischaltung am Beispiel Fisch/Stockfisch; echte Verarbeitung später separat | M6 |
| D-13 | Alte Spielstände | Vorschlag | Datenerhaltende A-Migration, B-Import zunächst ohne laufende Fahrt; laufende Altaufträge später ausdrücklich unterstützen | M2 bzw. M7 |
| D-14 | Schulden und Bankrott | Offen | Zunächst vorhandene Liquiditätsgrenzen; später Besitzbewertung einschließlich Umgang mit Ladung auf See festlegen | M7 |
| D-15 | Stadt- und Warenumfang | Vorschlag | Zuerst sechs A-Städte/-Waren, danach Bergenpilot, später gesamte Vereinigung; Pelze/Felle-Zuordnung bestätigen | M6/M7 |

## Nächste Entscheidungen

Für den nächsten Umsetzungsschritt sind technische Basis, erster Spielumfang und die konkrete Lizenz für Spielcode wichtig. Name, erster Veröffentlichungsumfang und nichtkommerzielles Nutzungsziel sind festgelegt. Über konkrete Gehälter, Warenpreise oder die spätere Pleitegrenze muss dafür noch nicht abschließend entschieden werden.

Die Planungsunterlagen erlauben mit CC BY-NC 4.0 nichtkommerzielle Bearbeitung und Weitergabe mit Namensnennung. Vor dem späteren Spielcode wird eine dafür geeignete Lizenz mit demselben nichtkommerziellen Nutzungsziel gewählt. Die Dokumentationslizenz wird nicht automatisch auf Software oder fremde Grafiken übertragen; siehe [Lizenz](lizenz.md).

## Entscheidungsprotokoll

| Datum | Entscheidung | Grundlage |
| --- | --- | --- |
| 12.09.2026 | Neues gemeinsames Projekt heißt „Die Hanse“ und erhält einen eigenen Ordner | Vorgabe des Projektinhabers |
| 12.09.2026 | Zunächst Planung erstellen; Veröffentlichung als öffentliches GitHub-Projekt vorbereiten | Vorgabe des Projektinhabers; noch kein Veröffentlichungsauftrag |
| 12.09.2026 | Planung zuerst öffentlich machen, danach spielbare Zusammenführung entwickeln; Projektname „Die Hanse“, Nutzung nur nichtkommerziell | Anschließende ausdrückliche Vorgabe des Projektinhabers |
| 12.09.2026 | Repository-Schreibweise `die-hanse` und verbundenes Konto `OnekoSL`; CC BY-NC 4.0 für den aktuellen Planungsstand | Konkrete Umsetzung dieser Vorgabe; spätere Softwarelizenz bleibt gesondert |

Weitere Beschlüsse ergänzen Datum, gewählte Alternative, Grund und betroffene Dokumente. Nach einer Regelentscheidung werden Spielkonzept, Roadmap und später die technische Regel-/API-Referenz entsprechend angepasst.
