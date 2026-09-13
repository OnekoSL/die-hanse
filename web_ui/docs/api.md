# API-Vertrag – Die Hanse Alpha

Basis `/api/v1`. Die interaktiven `/game/`-Endpunkte verwenden für Geld ausschließlich ganze Hundertstel-Mark (`100000` = 1.000,00 Mark). Die getrennten Backtest-Endpunkte behalten ihre bisherigen Mark-Werte und das [Szenarioformat](scenario-format.md).

## Sitzung und Ansichten

| Methode / Pfad | Bedeutung |
| --- | --- |
| GET `/health` | Zustand, Anwendungskennung `die-hanse`, Version |
| POST `/game/session/new` | Neue Sitzung; bisherigen automatischen Stand vorher archivieren |
| GET `/game/session/active` | Vollständige Spieleransicht, 404 wenn kein Spiel vorhanden |
| GET `/game/city-view/{city}` | Live, veraltete oder unbekannte Marktinformation mit Alter |
| GET `/game/events` | Globales Handelsbuch |
| GET `/game/assets/catalog` | Schiffsklassen, Kontorstufen, Kapazitäten, Preise, Bauzeiten |
| GET `/game/avatars` | Katalog des eigenen einfachen Händlersymbols |

`GameState` enthält `revision`, `format_version`, `world_version`, `rules_version`, `current_day` (0 am 1. März 1400), `date` (ISO), `cash`, `ships`, `active_ship_id`, `private_storages`, `orders`, `reports`, Städte, Waren und Reisedauern. `ship` ist der kompatible Alias für das ausgewählte Schiff. Fremde Märkte werden nicht durch die Sitzung als aktuelle Information offengelegt.

## Handel und Befehle

Alle folgenden Pfade beginnen mit `/game/action/`. Erfolgreiche Schreibbefehle liefern `GameState` und speichern automatisch.

| POST-Pfad | JSON-Felder |
| --- | --- |
| `market-quote` | `type` buy/sell, `city`, `good`, `qty` ganze Zahl 1–200, `counterparty` ship/private_storage, optional `ship_id` |
| `market-trade` | Dieselben Felder plus `revision` aus der Vorschau |
| `transfer` | `city`, `good`, `qty`, `direction` ship_to_private/private_to_ship, optional `ship_id` |
| `set-course` | `destination_city`, optional `ship_id` |
| `select-ship` | `ship_id` |
| `ship-buy` | `city`, `ship_class_id` |
| `ship-sell` | `city`, `ship_id` |
| `storage-upgrade` | `city` |
| `storage-sell` | `city` |
| `advance-day` | Kein Inhalt erforderlich |
| `advance-next-event` | Kein Inhalt erforderlich |

Die Vorschau ist lesend und liefert `revision`, `total`, `unit_prices` und `action`. Beispiel:

```json
{"type":"buy","city":"Luebeck","good":"Salz","qty":10,"counterparty":"ship"}
```

Für die Ausführung die zurückgelieferte Revision ergänzen. `total` ist die Summe der Einzelpreise; dieselbe Funktion berechnet die Buchung. Eine inzwischen veränderte Sitzung ergibt HTTP 409 und verlangt eine neue Vorschau. Lager-, Geld- und Marktgrenzen werden vollständig vor der Übernahme der Aktion geprüft.

Bauaufträge enthalten Art, Stadt, Bestelltag, Fälligkeitstag, Kosten sowie Schiffsklasse beziehungsweise Kontorstufe. Kalender und UI leiten Termine vom gemeinsamen Startdatum ab. Monatsberichte unterscheiden Handelsumsätze, Einkäufe, Bauausgaben und Vermögensverkäufe.

## Speicherplätze

| Methode / Pfad | Vertrag |
| --- | --- |
| GET `/game/saves` | Benannte Speicherplätze mit `id`, `name`, `date`, `updated_at` |
| POST `/game/saves` | `{ "name": "Londonfahrt" }` erzeugt einen neuen Platz |
| POST `/game/saves` | `overwrite_id` zusätzlich ausdrücklich angeben, um diesen vorhandenen Platz zu überschreiben |
| POST `/game/saves/{slot_id}/load` | Prüfen, vorherige aktive Sitzung archivieren, geprüften Stand aktivieren |

Namen sind 1–80 Zeichen lang und enthalten keine Steuerzeichen. Gleiche Namen sind erlaubt und überschreiben ohne `overwrite_id` nichts. `active` kann nicht als manueller Platz überschrieben werden. Laden einer beschädigten oder inkompatiblen Sitzung verändert die aktive Sitzung nicht. Auch ein beschädigter bisheriger Autosave bleibt beim Beginn eines neuen Spiels oder Laden als unverändertes Archiv erhalten.

## Atomarität und Fehler

Schreibzugriffe werden über SQLite `BEGIN IMMEDIATE` serialisiert. Zustand, Informationsstand, Revision und Buchungen werden in einer Transaktion gespeichert. Fehler führen zum Rollback: Geld, Waren, Aufträge und Zeit bleiben unverändert. HTTP 404 bezeichnet fehlende Sitzung/Plätze, 409 eine veraltete Handelsvorschau, 422 ungültige Aktionen oder beschädigte/unbekannte Speicherstände. Die Oberfläche zeigt verständliche Fehlermeldungen.

Ein Snapshot enthält die komplette Sitzung, alle Märkte und Kontore, SHA-256-Prüfsumme sowie getrennte Versionen: Format 1, Welt `alpha-world-1`, Regeln 1. Keine automatische Tabellenlöschung und kein Altimport. OpenAPI unter `/docs` beschreibt die konkreten Schemas.
