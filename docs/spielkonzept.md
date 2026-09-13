# Spielkonzept – Alpha 0.1.0

Verbindlicher Stand: 13. September 2026. Die Startbalance wird nach Spielerfahrungen weiterentwickelt.

## Einstieg und Welt

Am 1. März 1400 beginnt ein Handelshaus in Lübeck mit 1.000 Mark, einer Standardkogge (40 Last insgesamt, 20 je Ware) und einem Kontor der Stufe 1 (80 insgesamt, 30 je Ware). Der Ablauf ist Kaufen → Reisen → Verkaufen → Ausbauen → Speichern und Fortsetzen.

| Stadt | Hauptware |
| --- | --- |
| Lübeck | Salz |
| London | Tuch |
| Rostock | Holz |
| Danzig | Getreide |
| Riga | Wachs |
| Visby | Fisch |
| Hamburg | Malz |
| Stockholm | Eisen |
| Bergen | Fisch |
| Brügge | Tuch |
| Nowgorod | Felle |

Alle neun Waren sind in jedem Markt grundsätzlich handelbar. `Pelze` bleibt die technische Kennung für die Anzeige „Felle“. Weitere technische Stadtnamen verwenden beispielsweise `Luebeck` und `Bruegge`.

## Märkte und Geld

Basispreise in Mark: Salz 17, Getreide 10, Holz 12, Tuch 19, Felle 22, Fisch 11, Malz 8, Eisen 15, Wachs 20. Die sechs bisherigen Waren und Stadtfaktoren stammen aus A. Neue Kombinationen beginnen bei 1,00, neue Hauptwaren bei 0,80; Riga erhält Wachs als Hauptware und Felle-Faktor 1,00.

Startbestand je Ware: Hauptware 160, andere 80. Marktgrenze 200. Hauptware produziert täglich 5 und verbraucht 2; alle anderen produzieren 0 und verbrauchen 2. Produktion wird bei der Marktgrenze begrenzt, Verbrauch bei null.

Geld wird als ganze Hundertstel-Mark gespeichert. Jede gehandelte Einheit verändert den Bestand vor der Preisberechnung der nächsten Einheit. Vorschau und Buchung verwenden dieselbe Berechnung einschließlich Rundung: Teilkäufe kosten bei unverändertem Datum und ohne andere Marktänderung zusammen genauso viel wie ein Gesamtkauf. Geld, Warenbestand sowie Gesamt- und Pro-Ware-Kapazitäten müssen für die ganze Aktion ausreichen. Sonst bleibt der Spielstand unverändert.

Eine Vorschau enthält die Revision der Sitzung. Eine andere erfolgreiche Spielaktion macht sie ungültig. Dann muss der Spieler eine neue Vorschau anfordern. Handel und Bestellungen verbrauchen keine Tage.

Marktinformationen sind durch ein eigenes Schiff im Hafen oder ein Kontor aktuell. Andernfalls erscheinen der letzte bekannte Stand und sein Alter; bisher nicht besuchte Märkte bleiben unbekannt.

## Reisen und Kalender

Schiffe bleiben nach Ankunft im Zielhafen und können dort handeln oder weiterreisen. Mehrere Reisen laufen gleichzeitig. Die 15 bisherigen Verbindungen behalten ihre Dauern. Neue beidseitige Verbindungen: Hamburg–Lübeck 2, Hamburg–London 4, Brügge–London 2, Brügge–Hamburg 3, Bergen–Hamburg 4, Bergen–London 4, Stockholm–Visby 2, Stockholm–Riga 3, Nowgorod–Riga 3 Tage. Fehlende direkte Verbindungen erhalten die kürzeste Gesamtdauer durch dieses Netz ohne Zwischenstopps.

Der Kalender verwendet reale Monatslängen und technisch die gregorianische Schaltjahrregel. Ein Tageswechsel verarbeitet: alten Monat gegebenenfalls abschließen → Datum erhöhen → Märkte aktualisieren → Bauaufträge fertigstellen → Schiffe ankommen lassen → Marktinformationen aktualisieren. Vorspulen verarbeitet dieselben Tageswechsel bis zum nächsten Bauabschluss, einer Ankunft oder dem nächsten Monatsanfang.

Monatsberichte zeigen Anfangs- und Endgeld, Handelseinnahmen, Wareneinkäufe, Ausbauausgaben und gegebenenfalls Vermögensverkäufe. Der Geldüberschuss ist keine Berechnung des Unternehmensgewinns.

## Ausbau

| Schiff | Preis in Mark | Gesamt / je Ware | Bauzeit |
| --- | ---: | ---: | ---: |
| Standardkogge | 900 | 40 / 20 | 7 Tage |
| Große Kogge | 1.600 | 70 / 35 | 14 Tage |
| Fernhändler | 2.600 | 100 / 50 | 21 Tage |

| Kontorstufe | Gesamt / je Ware | Preis dieser Bestellung in Mark |
| --- | ---: | ---: |
| 1 | 80 / 30 | 200 |
| 2 | 140 / 50 | 350 |
| 3 | 220 / 80 | 600 |
| 4 | 320 / 120 | 950 |

Kontorbau und jeder Ausbau dauern sieben Tage. Zahlung bei Bestellung, neue Kapazität ab Fertigstellung. Während des Ausbaus bleibt die bisherige Kapazität nutzbar. Je Stadt ist nur ein Kontorauftrag gleichzeitig möglich. Stornieren folgt später. Bestehende A-Verkaufsregeln gelten: halber Anschaffungspreis, kein Verkauf des letzten, beladenen oder reisenden Schiffs; Kontorrückbau nur bei passenden Restbeständen und ohne laufenden Bauauftrag.

## Bedienung und Speicherung

Startmenü mit Neu, Fortsetzen und Laden. Im Spiel stehen eine eigene schematische Hafenkarte mit gleichwertiger Liste, Flotte, Markt, Ladung/Kontor, Bauaufträge, Handelsbuch und Monatsberichte zur Verfügung. Beschriftete Standard-Steuerelemente unterstützen Tastaturbedienung und sichtbaren Fokus.

Jeder erfolgreiche Befehl speichert automatisch. Zusätzliche benannte Speicherplätze enthalten die vollständige Sitzung samt Reisen, Bauten, Berichten und Informationsalter. Überschreiben erfordert die Auswahl eines vorhandenen Platzes. Laden validiert vor Austausch der aktiven Sitzung; der vorherige Stand wird zusätzlich archiviert. Beschädigte oder unbekannte Versionen werden erhalten und verständlich abgewiesen.

## Bewusst später

Verwalter, automatische Routen, Produktion, Verderb, Reisegefahren und Altspielstand-Importe gehören nicht zu dieser Alpha. Auch eine Regelangleichung des separaten Backtests, Mehrspieler und Politik sind nicht enthalten.
