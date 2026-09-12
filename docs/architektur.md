# Architektur und Codeübernahme

Stand: 12. September 2026. **Architekturvorschlag; noch keine Codeübernahme.**

## Technische Basis

Empfohlen ist die Weiterverwendung von Python/FastAPI, React/TypeScript, SQLite und der vorhandenen Tauri-Desktop-Hülle. Der neue Ordner erhält dafür eine eigenständige, gezielte Übernahme des bestehenden Quellcodes. Er darf zur Laufzeit nicht von Dateien außerhalb dieses Projekts abhängen.

Aus der C#-Variante werden zunächst Datenmodelle, Regeln, Bedienideen und Testfälle fachlich übertragen. WinForms-Steuerelemente lassen sich nicht unmittelbar als React-Komponenten verwenden. Eine dauerhaft zweite Engine würde Geld, Zeit und Marktzustand doppelt verwalten und wird deshalb nicht empfohlen.

Der neue Projektort bedeutet keine vollständige Neuentwicklung. Bewährte Engine-Funktionen, API-Verträge, Repositories und Komponenten werden weitergeführt und in nachvollziehbaren Schritten angepasst.

## Vorgeschlagene Struktur nach der Codeübernahme

```text
Die Hanse/
  README.md
  docs/                       Planung, Regeln, API und Herkunft
  web_ui/
    backend/                  FastAPI, Engine, SQLite und Backend-Tests
    frontend/                 React, API-Client und UI-Tests
    data/scenarios/           Versionierte Backtest-Szenarien
  lokal_exe/                  Tauri und Desktop-Buildskripte
  .github/workflows/          Prüfungen nach der Codeübernahme
  .gitignore
  .gitattributes
```

Die Struktur erhält wichtige Pfade des ersten Prototyps und reduziert unnötige Anpassungen an Buildskripten. Der aktuelle Ordner enthält erst `README.md`, `docs/` und die beiden Git-Konfigurationsdateien. Geplante Verzeichnisse werden angelegt, wenn sie Inhalt erhalten.

## Zuständigkeiten

| Bereich | Aufgabe |
| --- | --- |
| React | Bedienung, Auswahlzustand und Anzeige; keine verbindliche Wirtschaftsberechnung |
| API | Eingaben und Antworten, Aufruf der Regeln, Transaktionsgrenzen |
| Engine | Handel, Kapazitäten, Reisen, Zeit, Aufträge, Personal und Ereignisse |
| Repositories/SQLite | Spielstände, Buchungen, Marktinformationen und sichere Migrationen |
| Daten | Versionierte Weltdefinition, Waren, Routen, Ausbau- und Saisonwerte |
| Tauri | Lokale Desktop-Verpackung derselben Anwendung |

Neue Bereiche wie Kalender, Personal und Aufträge erhalten überschaubare Module. Bestehende Dateien werden nur geteilt, wenn der jeweilige Umbau es erfordert. Änderungen an der API betreffen gemeinsam Schemas, Routen, TypeScript-Typen, Client, Tests und API-Dokumentation.

## Reihenfolge der Übernahme

1. Einen Quellstand beider Prototypen dokumentieren, einschließlich nicht eingecheckter Abweichungen und nötiger Herkunftsnachweise.
2. Benötigten A-Quellcode, Manifeste, Lockdateien, Tests und Start-/Buildskripte auswählen. Keine pauschale Ordnerkopie mit Datenbanken, Buildausgaben oder alter Git-Historie.
3. Relative Pfade und Umgebungsvariablen prüfen; einen frischen Start mit eigener Datenbank ermöglichen.
4. Bestehende Backend-/Frontend-Prüfungen als Ausgangsmessung ausführen; Abweichungen vor neuen Spielregeln dokumentieren.
5. Die einzelnen B-Mechaniken nach Roadmap ergänzen und die dazu passenden Tests übertragen.

Die bisherigen Projekte bleiben währenddessen als Referenz erhalten. Es werden keine Verknüpfungen, Submodule oder Importpfade angelegt, die eine zweite lokale Projektkopie zum Spielen voraussetzen.

## Daten und Spielstände

Speicherformat, Spielregeln und Welt-/Balancingdaten benötigen unterscheidbare Versionen. Die bisherige A-Initialisierung kann bei Altschemata Tabellen löschen; ein Weltversionswechsel kann außerdem Sitzungen archivieren sowie Märkte, Lager, Informationen und Ereignisse löschen. Diese Übergänge werden vor einer Erweiterung der Welt durch sichere Migrationen ersetzt.

| Quelle | Zu erhalten | Neu zu definieren |
| --- | --- | --- |
| A: SQLite | Geld, Bestände, Kapazitäten, Kontorstufen, Reisen, Ereignisse und Informationsalter | Kalenderzuordnung, neue Personal-/Altersfelder und Geldformat |
| B: JSON bis Version 5 | Besitz, Personal, Regeln, Altersposten, Berichte und gespeicherter Zufallszustand | Lokale Märkte, Tagesreisen und Zuordnung der abweichenden Kennungen |

Importe erzeugen eine neue Sitzung auf Basis einer Kopie. Fehler ersetzen keinen aktiven Stand. Zwei importierte Handelshäuser bleiben getrennte Spielstände. Bestehende Überbestände werden nicht abgeschnitten. Der erste B-Import kann auf Zustände ohne laufende Fahrt begrenzt sein; eine spätere Übernahme laufender Altaufträge muss Rückware, bereits gezahlte Kosten und Zufallsauswertung ausdrücklich behandeln.

Für die Zuordnung gilt insbesondere: A-`Fisch` entspricht B-`rohfisch`; B-`fisch` ist Stockfisch. A-`Luebeck` bleibt als bestehende technische Kennung erhalten. Anzeigenamen und Importkennungen werden getrennt behandelt. Die endgültige Tabelle aller Kennungen entsteht vor dem Import.

## Backtest

Der bestehende Backtest besitzt eigene Szenarien, eine eigene Preisformel und eine eigene Strategie. Er ist noch kein Nachweis für die Regeln des interaktiven Handelshauses. Die Auswertung bleibt nutzbar, während gemeinsame Preis-, Zeit- und Auftragsfunktionen schrittweise angeglichen werden. Alte Läufe bleiben mit ihrem Regelstand erkennbar.

## Prüfstrategie

Backend-Tests immer mit einer eigenen temporären Datenbank über `HANSE_DB_PATH` ausführen, bevor die Anwendung importiert wird. Keine produktiven Spielstände für Tests verwenden. Zunächst gezielte Regressionen, danach die betroffenen bestehenden Prüfungen ausführen.

Zum übernommenen Grundstand gehören Ruff, pytest, Frontend-Tests und TypeScript-/Vite-Build. UI-Integration zusätzlich im echten Browser prüfen; die vorhandenen Vitest-/jsdom-Tests ersetzen dies nicht. Desktop-Builds folgen bei Änderungen an der Paketierung bzw. vor einer Desktop-Auslieferung.

Für neue Regeln besonders prüfen: Vorschau entspricht Abrechnung, Sammelaktionen sind vollständig oder wirkungslos, Zeitüberspringen entspricht Einzeltagen, Löhne werden genau einmal fällig, Transfers erhalten Warenalter, Vorschauen verbrauchen keinen Zufall und fehlgeschlagene Importe erhalten das aktive Spiel.
