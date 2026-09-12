# Öffentliche GitHub-Veröffentlichung

Stand: 12. September 2026. Die Planung ist unter [OnekoSL/die-hanse](https://github.com/OnekoSL/die-hanse) öffentlich veröffentlicht. Repository-Sichtbarkeit, Hauptbranch und hochgeladener Erststand wurden nach dem Upload überprüft. Die folgenden Angaben beschreiben den Inhalt und die Vorbereitung weiterer Ausbaustufen.

## Öffentliches Projekt

| Feld | Stand |
| --- | --- |
| Projektname | Die Hanse |
| Repository-Name | `die-hanse` |
| Eigentümer / Organisation | `OnekoSL`, verbundenes GitHub-Konto |
| Sichtbarkeit | Öffentlich |
| Beschreibung | Historische Handelssimulation: Aufbau eines Handelshauses mit Flotte, Kontoren und Verwaltern |
| Sprache | Deutsch; englische Kurzbeschreibung später optional |
| Erster Inhalt | Planungsunterlagen; deutlich als noch nicht spielbar gekennzeichnet |
| Lizenz | CC BY-NC 4.0 für den Planungsstand; spätere Softwarelizenz gesondert |
| Hauptbranch | `main`; Änderungen später auf `codex/...` oder passend benannten Arbeitsbranches |

Die Veröffentlichung der Planung und die Veröffentlichung einer spielbaren Anwendung sind getrennte Schritte. Ein frühes Planungsrepository darf seine Roadmap zeigen, soll aber keine Downloads, Startbefehle oder erfolgreich laufende CI behaupten, die noch nicht vorhanden sind.

## Lizenz und Herkunft

**Öffentlich sichtbar bedeutet nicht automatisch Open Source.** GitHub unterscheidet öffentliche Sichtbarkeit von einer Lizenz, die Verwendung, Änderung und Weitergabe erlaubt. Die gewünschte Nutzung muss deshalb bewusst festgelegt werden. [GitHub: Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

Die Vorgabe lautet nichtkommerzielle Nutzung. Der aktuelle Planungsstand steht dafür unter **CC BY-NC 4.0**, einschließlich Bearbeitung und Weitergabe mit Namensnennung. Der vollständige Text liegt in [LICENSE](../LICENSE); der [Geltungsbereich](lizenz.md) grenzt die Planung vom späteren Spielcode ab. Die [Herkunftsliste](herkunft.md) hält die vor einer späteren Code-/Grafikübernahme zu prüfenden Bestandteile fest.

Die bisherige Seekarte basiert laut Projektdokumentation auf einer lokalen Bildvorlage. Ein bearbeitetes oder generiertes Bild ersetzt keinen Nachweis zur Nutzung seiner Vorlage. Für den ersten Planungsupload ist die Karte nicht erforderlich; zum technischen Start kann eine einfache eigene Darstellung verwendet werden. Porträts und Schriftdateien werden ebenfalls vor einer Übernahme zugeordnet.

## Umfang des ersten Uploads

Der erste Upload enthält die Projekt-README, die Planungsdokumente einschließlich Lizenzhinweisen, den vollständigen Lizenztext sowie `.gitignore` und `.gitattributes`. Vorgängerprogramme, ihre Git-Verzeichnisse, Dokumentbilder und persönliche Spielstände sind nicht enthalten.

Die `.gitignore` bereitet den Ausschluss von Umgebungsdateien, Datenbanken samt SQLite-Nebendateien, Savegames, Logs, Abhängigkeiten und Buildausgaben vor. Beispieldaten und Vorlagen können gezielt versioniert werden. Die Dateiliste des ersten Commits muss trotzdem geprüft werden: Ignore-Regeln ersetzen keine Inhaltsprüfung.

## Ablauf der Erstveröffentlichung

1. Eigentümer, Repository-Name, Lizenz und ersten Inhaltsumfang festlegen.
2. Nur die dafür vorgesehenen Dateien auf Vollständigkeit, Herkunft und veröffentlichungsgeeignete Inhalte prüfen. Lokale Pfade, echte Spielstände, Tokens und nicht benötigte Originalvorlagen nicht aufnehmen.
3. Den Ordner als eigenständiges lokales Git-Repository mit `main` initialisieren, die konkrete Dateiauswahl prüfen und den ersten Commit erstellen.
4. Das öffentliche GitHub-Repository unter dem festgelegten Eigentümer erstellen und den lokalen Stand verbinden. Bei Übernahme eines bereits lokal begonnenen Repositories keine konkurrierende README/Lizenz/Ignore-Datei auf GitHub erzeugen. [GitHub: Adding locally hosted code to GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).
5. Den geprüften Commit hochladen und die GitHub-Ansicht kontrollieren: README, Links, Lizenz, Sichtbarkeit und Dateiliste.
6. Die tatsächliche Repository-URL in der README ergänzen. Roadmap-Aufgaben erst anschließend als Issues anlegen und verlinken.

Die Veröffentlichung betrifft ausschließlich den neuen Projektordner. Die beiden Vorgängerprojekte und ihre bisherigen Repository-Einstellungen bleiben erhalten. Automatisch angelegte Issues oder weitere Veröffentlichungen gehören nicht zum ersten Upload.

## Mit der Codeübernahme ergänzen

- Startanleitung, tatsächliche Voraussetzungen und eine Konfiguration mit Beispielwerten.
- Bestehende Prüfungen als CI: Backend-Lint/-Tests mit isolierter Datenbank sowie Frontend-Tests/-Build. Erst dann einen passenden Status anzeigen.
- Hinweise für Beiträge und Fehlermeldungen, einschließlich benötigter Reproduktionsschritte.
- Nachweise für übernommene Grafiken, Schriften und erforderliche Abhängigkeitshinweise.
- Dokumentation der Datenspeicherung und Migration; keine echten Nutzerstände in Issues oder Testdaten.

Eine Desktop-Auslieferung erhält zusätzlich Versionsangabe, Änderungsübersicht, bekannte Einschränkungen und einen tatsächlich geprüften frischen Start. Generierte Installer gehören in die Auslieferung, nicht in den Quellbaum.
