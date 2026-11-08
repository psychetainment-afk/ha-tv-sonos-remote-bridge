# Projektumfang

Zuerst ein Komplettpaket für Menschen mit Home Assistant und kompatiblem Android-/Google-TV: Verbindung, Lautstärke, Tastenlernen und Belegungen im HA-Browser; TV-App über dieselbe Integration verteilen und konfigurieren. HACS dient der Installation und Aktualisierung, HA erledigt die laufende Steuerung.

Ausgangspunkt ist die optisch angeschlossene ältere Sonos Playbar: Audio funktioniert, Bluetooth-TV-Lautstärketasten erreichen sie nicht. Die Brücke erspart die zweite Fernbedienung und nutzt vorhandene HA-Geräte weiter. Licht, Nachtton und Rollladen sind austauschbare HA-Aktionen, keine fest eingebauten Hausgeräte.

Die TV-App bleibt eine kleine Komponente ohne Netzwerkberechtigung. Lokale App-Belegungen funktionieren nach der Einrichtung auch ohne laufenden HA-Leser. Ein eigenständiges öffentliches Tastenmapper-Produkt ist zurückgestellt; keine parallele zweite Produktentwicklung.

Lokale Entwicklung 0.3.0/1.5 vorhanden und isoliert geprüft; Produktivstand bleibt 0.2.0/1.4. Noch keine neue Hardwareprüfung, kein Remote und keine Veröffentlichung. GPL-3.0-only gewählt. Vor Veröffentlichung [Veröffentlichung](VEROEFFENTLICHUNG.md), vor Geräteänderungen [Migration](MIGRATION.md) beachten.

Weitere Hersteller benötigen eigene Profile und Nachweise. Entwickleroptionen, ADB und TV-Freigaben können nicht durch HACS ersetzt werden. Ein Firmwarewechsel, Root oder eine Werbebereinigung gehören nicht zum Projektumfang.
