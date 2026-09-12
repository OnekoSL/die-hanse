# Roadmap

Stand: 12. September 2026. Planungsentwurf ohne zugesagte Termine.

## Arbeitsweise

Ein Arbeitspaket beschreibt einen beobachtbaren Nutzen und seine Abnahme. Dokumentation, Implementierung und passende Prüfungen gehören zum selben Paket. Erst nach der Abnahme erhält es den Status „abgeschlossen“. Ein vorhandener Prototyp gilt noch nicht als in Die Hanse integriert.

Größen sind relativ: **S** = begrenzt, **M** = mehrere zusammenhängende Änderungen, **L** = neuer Spielbereich, **XL** = umfangreicher Übergang. Sie sind keine Aufwandsschätzung in Tagen.

## Meilensteine

| ID | Ergebnis | Abhängigkeit | Größe | Status |
| --- | --- | --- | --- | --- |
| M0 | Eigenständige Planung und geklärter erster Veröffentlichungsumfang | Keine | M | Planung öffentlich veröffentlicht; technische Entwurfsentscheidungen weiter offen |
| M1 | Technischer Grundstand läuft aus diesem Projekt | Architekturentscheidung und Herkunftsprüfung | M–L | Geplant |
| M2 | Verlässlicher Handel und sichere Spielstandentwicklung | M1 | L | Geplant |
| M3 | Verständlicher manueller Handelsablauf mit Karte und Monatsbericht | M2, Zeit-/Kalenderentscheidung | L | Geplant |
| M4 | Bezahlter Verwalter wiederholt denselben Handelsablauf | M3, Dienst-/Auftragsregeln | L | Geplant |
| M5 | Jahreszeiten, Reisegefahren und Schutzwirkung | M4, gespeicherter Zufall | L | Geplant |
| M6 | Warenalter und Bergen/Fisch/Stockfisch als Manufakturpilot | M5, sichere Weltmigration | L | Geplant |
| M7 | Breiter Zusammenschluss und Import der zweiten Variante | M6, Waren-/Stadtmapping und Importregeln | XL | Geplant |
| M8 | Abgestimmter Spielverlauf und Desktop-Auslieferung | M7, laufende Balanceprüfungen | L | Geplant |

Das **Planungsrepository** ist öffentlich veröffentlicht; danach folgt die spielbare Zusammenführung. Eine **spielbare öffentliche Vorabfassung** ist ein anderes Ergebnis und wird frühestens nach M4 vorgeschlagen. Ihr genauer Umfang wird noch entschieden. Offene technische Entwurfsentscheidungen in M0 sind in der öffentlichen Planung kenntlich gemacht.

## M0 – Planung und Veröffentlichung vorbereiten

- Projektname, neuen Ort und Zweck dokumentieren.
- Architekturvorschlag und Umfang von M1–M4 konkretisieren.
- Festgelegt: Repository `OnekoSL/die-hanse`, aktueller Planungsstand unter CC BY-NC 4.0.
- Erster Veröffentlichungsinhalt: Planungsunterlagen und redaktionelle Projektdateien, keine Vorgängerprogramme oder Spielgrafiken.
- Herkunft von Code, Grafiken und Schriftarten getrennt erfassen.

**Abnahme:** Einstieg und Roadmap sind auch ohne Zugriff auf die Vorgängerprojekte verständlich. Beschlüsse und Vorschläge sind unterscheidbar. Für den tatsächlich zu veröffentlichenden Umfang sind Lizenz und Herkunft geklärt. Ein Repository wurde erst dann veröffentlicht, wenn eine überprüfte URL vorliegt.

## M1 – Bestehenden Grundstand übernehmen

Die vorhandene A-Engine, API, Persistenz, React-Struktur und erforderlichen Projektdateien gezielt übernehmen. Quellstände festhalten, Pfadabhängigkeiten entfernen und eine isolierte Entwicklungsdatenbank benutzen. Vorhandene Prüfungen als Ausgangsbasis ausführen.

**Abnahme:** Backend und Frontend starten allein aus Die Hanse. Es werden keine Dateien aus einem anderen Projektordner benötigt. Testergebnisse und etwaige übernommene Fehler sind dokumentiert. Produktive Datenbanken und nicht geklärte Grafiken wurden nicht übernommen; bei Bedarf werden einfache Platzhalter verwendet.

## M2 – Handel und Speicherung verlässlich machen

Versionierte, datenerhaltende Migrationen vor Weltänderungen einführen. Vorschau und Ausführung auf dieselbe Mengen-/Preisberechnung setzen. Tatsächlich gebuchte Preise und Summen protokollieren. Produktion/Verbrauch und die angezeigten Bestandsänderungen aufeinander abstimmen.

**Abnahme:** Gleiche Gesamtmenge führt bei unverändertem Zeitstand zur gleichen Abrechnung, auch in Teilaktionen. Geld und Waren werden genau einmal gebucht. Ein alter A-Spielstand bleibt nach dem Übergang vollständig erhalten. Ungültige Eingaben verändern ihn nicht.

## M3 – Einen manuellen Handelsablauf verständlich zeigen

Karte mit Hafenliste, konsistente Schiffsauswahl und klare Handelsaktionen einführen. Kalender und monatliche Buchungsübersicht ergänzen. Zeitneutrale Bau-/Schiffsbestellungen mit Fertigstellungsterminen umsetzen, damit sie zur gemeinsamen Ereignisuhr passen.

**Abnahme:** Ein Spieler kann eine Route mit Vorschau kaufen → reisen → verkaufen bedienen. Karte und Hafenliste sind per Tastatur nutzbar. Vorspulen verarbeitet Ankünfte, Bauabschlüsse und Monatsgrenzen in definierter Reihenfolge. Das globale Handelsbuch bleibt unabhängig von der gewählten Stadt verfügbar.

## M4 – Den Ablauf delegieren

Personal anstellen/entlassen, Dienstperioden bezahlen und eine wiederkehrende Handelsroute konfigurieren. Geldreserve, Mengen-/Preisgrenzen und Prioritäten gemeinsam prüfen. Automatik führt dieselben Regeln wie manuelle Aktionen aus.

**Abnahme:** Ohne bezahlten Verwalter läuft kein Dauerauftrag. Eine manuell begonnene Fahrt wird nicht doppelt ausgelöst. Fehlende Mittel, voller Laderaum und zu hoher Mindestpreis pausieren sichtbar. Speichern/Laden erhält Auftrag und Dienststatus. Dieser Meilenstein bildet den ersten vorgeschlagenen gemeinsamen Spielumfang.

## M5 bis M8 – Die besonderen Systeme vervollständigen

| Meilenstein | Inhalt | Abnahme |
| --- | --- | --- |
| M5 | Saisonale Produktion/Nachfrage, Fahrtgefahren, Geschütze und robuste Schiffe | Gleicher gespeicherter Stand mit gleicher Befehlsfolge liefert gleiche Ereignisse; Vorschauen verändern den Zufall nicht; Risiken sind auf Reisedauer abgestimmt |
| M6 | Lageralter/FIFO, Transfers mit Alterserhalt, Bergen und Stockfischfreischaltung | Alte Ware wird durch Umladen nicht frisch; Verderb und Kapazitäten sind erklärt; die neue Weltversion erhält alte Bestände |
| M7 | Weitere Häfen/Waren, vollständiger Ausbau, Ränge und bewusst gewählte Finanz-/Pleiteregeln; B-Import | Stadt-/Warenkennungen sind eindeutig, Altbestände bleiben erhalten, Importgrenzen sind sichtbar; kein doppeltes Bezahlen oder Erzeugen von Ladung |
| M8 | Gemeinsame Backtest-Regeln, Balance, Einführung, Desktop-Verpackung | Manueller und automatisierter Spielverlauf geprüft; frischer Desktop-Start und Fortsetzen funktionieren; bekannte Einschränkungen sind dokumentiert |

Balance wird bereits ab M2 überprüft. Insbesondere Startkapital, Monatslöhne, mehrere kurze Reisen je Monat, Lagergrößen und Sättigung müssen gemeinsam betrachtet werden.

## Erste Aufgaben für spätere GitHub-Issues

Diese Einträge sind vorbereitete Aufgaben, noch keine auf GitHub erstellten Issues.

| ID | Titel | Erledigt, wenn |
| --- | --- | --- |
| PLAN-01 | Architektur und Umfang der ersten Vorabfassung festlegen | D-04 und der konkrete Umfang der spielbaren Vorabfassung festgelegt sind; die Planungsveröffentlichung gemäß D-06 ist bereits beauftragt |
| PUB-01 | Repository-Eigentümer, Name und Lizenz bestimmen | Für den Planungsstand geklärt: `OnekoSL/die-hanse`, CC BY-NC 4.0; Softwarelizenz bleibt als separate Folgeaufgabe |
| PUB-02 | Herkunft des ersten Veröffentlichungsumfangs erfassen | Jede enthaltene fremde Datei Quelle und Nutzungsgrundlage besitzt |
| BASE-01 | Eigenständigen A-Grundstand übernehmen | M1-Abnahme erfüllt ist |
| SAVE-01 | Datenlöschung bei Schema-/Weltwechsel ersetzen | Ein Upgrade-Test vorhandene Märkte, Lager, Ereignisse und Reisen erhält |
| TRADE-01 | Verbindliche Handelsvorschau und Abrechnung | Vorschau, Buchung und Logbuch dieselben Summen zeigen |
| TIME-01 | Gemeinsame Tagesuhr und Monatsgrenze definieren | Gleichzeitige Ereignisse und Lohnperioden eindeutig geregelt sind |

## Fertig-Kriterium je Änderung

Änderung und betroffene Verträge dokumentiert; passende Prüfungen tatsächlich ausgeführt; neue Dateien und Diff kontrolliert; keine Spielstände, Secrets oder Buildausgaben enthalten. Bei sichtbaren UI-Änderungen Browserprüfung ergänzen. Nicht ausgeführte Prüfungen ausdrücklich benennen.
