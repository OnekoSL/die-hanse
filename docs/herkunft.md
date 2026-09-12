# Ausgangsprojekte und Herkunft

Stand: 12. September 2026. Dokumentation der Planungsgrundlage; noch kein Nachweis abgeschlossener Code- oder Grafikübernahmen.

## Analysierte Prototypen

| Kürzel | Ausgangsprojekt | Technischer Stand | Rolle für Die Hanse |
| --- | --- | --- | --- |
| A | Hanse – Handelssimulation | Python/FastAPI, React/TypeScript, SQLite; Tauri-Desktop-Fassung | Empfohlene technische und wirtschaftliche Basis |
| B | Hanse – Dein Handelshaus | C#-Engine, WinForms und CLI, JSON-Spielstände Version 5 | Referenz für Personal, Kalender, Lageralter, Reisegefahren, Manufakturfreischaltungen und Berichte |

Der analysierte A-Repository-HEAD lautet `b877c384d9b4221e75ec73ddf6e48842a36eb48f` vom 11. August 2026. Der Arbeitsstand enthielt zusätzliche Analysedokumentation. B lag am 12. September 2026 als hinzugefügter, im A-Repository noch nicht versionierter Projektordner vor; für B wird deshalb kein überprüfter Commit angegeben.

Vor tatsächlicher Übernahme ist der dann gewählte Quellstand erneut festzuhalten. Ein A-Commit allein beschreibt weder die zusätzlichen Dokumente noch den vollständigen B-Quellstand. Die alten Projekte bleiben bis dahin lokal erhalten; eine öffentliche Quelladresse wird nicht erfunden.

## Nachprüfbare Einstiegspunkte der Analyse

Die folgenden Angaben bezeichnen Pfade **in den Ausgangsprojekten**, nicht bereits vorhandene Dateien dieses Repositories.

| Thema | Quellpfade |
| --- | --- |
| A-Welt und Handelsregeln | `web_ui/backend/app/engine/game_world.py`, `game_engine.py` |
| A-Speicherung | `web_ui/backend/app/infra/db.py`, `repositories.py`, `models.py` |
| A-Oberfläche | `web_ui/frontend/src/features/game/`, `src/App.tsx` |
| A-Backtest | `web_ui/backend/app/engine/simulation.py`, `pricing.py`, `strategy.py` |
| A-Vergleichsdokument | `web_ui/docs/vergleich-und-zusammenfuehrung.md`, Analyse vom 12.09.2026 |
| B-Regeln und Import | `Hanse.Engine/GameEngine.cs`, `Models.cs` |
| B-Zusatzsysteme | `Hanse.Engine/Kalender.cs`, `Lagerhaltung.cs`, `FirmenBewertung.cs`, `Handelsbuch.cs` |
| B-Welt und Ausbau | `data/staedte.json`, `waren.json`, `ausbau.json`, `kalender.json` |
| B-Karte | `Hanse.WinForms/HanseMap.cs`, `Hanse.WinForms/Assets/hanse-seekarte.png`, `docs/16-seekarte.md` |
| B-Prüfungen | `Hanse.Tests/Program.cs`, `Hanse.WinForms/MainForm.Check.cs` |

Die vollständige frühere Vergleichsanalyse verbleibt im Vorgängerprojekt. Die neuen Unterlagen fassen ihre entscheidungsrelevanten Ergebnisse eigenständig zusammen und haben keine Markdown-Links auf nicht mitgelieferte lokale Quellen.

## Herkunftsliste vor Veröffentlichung von Code und Medien

| Bestandteil | Vorliegender Hinweis | Noch zu dokumentieren | Übernahmestatus |
| --- | --- | --- | --- |
| A-Quellcode | Bestehendes lokales Projekt; README nennt noch keine gewählte Projektlizenz | Rechteinhaber/Beiträge, konkreter Quellstand, Lizenzentscheidung und ggf. fremde Hinweise | Nicht übernommen |
| B-Quellcode und Daten | Zweites lokales Projekt; keine Projekt-Lizenzdatei in der geprüften Quellstruktur gefunden | Rechteinhaber/Beiträge, stabiler Quellstand und Nutzungsgrundlage | Nicht übernommen |
| Seekarte B | Dokumentierter Einsatz von Bildgenerierung auf Basis einer lokalen Vorlage | Herkunft und Nutzung der Vorlage, Kennzeichnung der Bearbeitung, Geltungsbereich der Grafiklizenz | Nicht übernommen |
| Porträts A | Vorhandene Spieler-/Händlerbilder | Herkunft und erlaubte Veröffentlichung jeder übernommenen Datei | Nicht übernommen |
| Schriftgestaltung A | CSS bindet Space Grotesk über Google Fonts ein | Benötigte Dateien, Lizenzhinweise und ggf. lokale Einbindung für Desktop prüfen | Nicht übernommen |
| Bibliotheken | In den jeweiligen Manifesten deklarierte Abhängigkeiten | Tatsächlich übernommene Versionen, Lockdateien und nötige Hinweise | Noch kein Codegrundstand |
| Neue Planungsunterlagen und redaktionelle Projektdateien | In diesem Projekt für die Zusammenführung erstellt | CC BY-NC 4.0, Namensnennung OnekoSL; siehe [Lizenz](lizenz.md) | Öffentlich veröffentlicht |

Für jede später übernommene fremde Datei erfassen: Zielpfad, Quelle, Urheberangabe, Lizenz/Freigabe, erforderlichen Hinweis und eigene Änderungen. Fehlende Nachweise werden nicht durch eine pauschale Projektlizenz ersetzt. Benötigte rechtliche Hinweise bleiben beim Übertragen von Code erhalten.

## Aussagegrenzen

Die Grundlage ist eine Quellcode-, Daten- und Dokumentationsanalyse vom 12. September 2026, ergänzt um vorhandene Bilder aus B. Es wurden dafür keine neuen vollständigen Spieldurchläufe oder Anwendungstests ausgeführt. Frühere Tests im Ausgangsprojekt gelten nicht als bestandene Tests einer zukünftigen Integration.

Noch ungeprüft sind unter anderem Langzeitbalance, vollständige Importkompatibilität, Veröffentlichungstauglichkeit aller alten Medien und der gemeinsame Desktop-Build. Diese Punkte sind in Roadmap und Veröffentlichungsvorbereitung eingeplant.
