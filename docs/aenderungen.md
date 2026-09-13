# Änderungen

## 0.1.0-alpha.2 – Waren und Schiffsladung

- Vollständige Schiffsladung als eigene Übersicht über dem Markt, mit Mengen und freiem Laderaum. Waren in der Ladung lassen sich direkt auswählen.
- Die gewählte Ware erscheint rechts mit ihrem Namen, Beständen in Schiff und Kontor sowie Kauf- und Verkaufspreis je Last. Veraltete Preise behalten ihre Alterskennzeichnung.
- Die gesamte Marktzeile ist anklickbar; die zusätzliche Spalte „An Bord“ zeigt die eigene Menge je Ware. Tastaturbedienung erfolgt über die beschrifteten Warenknöpfe.
- Ein Verkauf ohne ausreichenden Warenbestand wird mit Mengenhinweis gesperrt. Die verbindliche Berechnung und Bestätigung bleiben unverändert.
- Umladen ist in einem aufklappbaren Bereich untergebracht. Auf breiten Fenstern bleibt die rechte Übersicht beim Scrollen erreichbar; schmale Fenster zeigen Ladung, Warendetails und Markt untereinander.

Spielregeln, Speicherformat und vorhandene Spielstände bleiben kompatibel zu Alpha 1. Die interne MSI-Produktversion bleibt technisch 0.1.0; das Paket und die API tragen 0.1.0-alpha.2.

Prüfung: gezielte UI-Regressionen für Auswahl, Ladung, fehlenden Verkaufsbestand und alte Marktinformationen; TypeScript/Vite und tatsächliche Browserprüfung. Die Windows-Ausgabe wird als eigener Installer geliefert.
