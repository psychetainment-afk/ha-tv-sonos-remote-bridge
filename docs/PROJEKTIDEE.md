# Projektumfang

Zuerst ein Komplettpaket für Menschen mit Home Assistant und kompatiblem Android-/Google-TV: Verbindung, Lautstärke, Tastenlernen und Belegungen im HA-Browser; TV-App über dieselbe Integration verteilen und konfigurieren. HACS dient der Installation und Aktualisierung, HA erledigt die laufende Steuerung.

Ausgangspunkt ist die optisch angeschlossene ältere Sonos Playbar: Audio funktioniert, Bluetooth-TV-Lautstärketasten erreichen sie nicht. Die Brücke erspart die zweite Fernbedienung und nutzt vorhandene HA-Geräte weiter. Licht, Nachtton und Rollladen sind austauschbare HA-Aktionen, keine fest eingebauten Hausgeräte.

Die TV-App bleibt eine kleine Komponente ohne Netzwerkberechtigung. Lokale App-Belegungen funktionieren nach der Einrichtung auch ohne laufenden HA-Leser. Ein eigenständiges öffentliches Tastenmapper-Produkt ist zurückgestellt; keine parallele zweite Produktentwicklung.

Öffentlicher Kandidat 0.5.0/TV-App 1.7 unter GPL-3.0-only. Ziel ist das Repository psychetainment-afk/ha-tv-sonos-remote-bridge. Teilweise hardwaregeprüft, verbleibende Grenzen unter [Prüfung](PRUEFUNG.md). Releaseverfahren unter [Veröffentlichung](VEROEFFENTLICHUNG.md), Geräteänderungen nach [Migration](MIGRATION.md).

Weitere Hersteller benötigen eigene Profile und Nachweise. Entwickleroptionen, ADB und TV-Freigaben können nicht durch HACS ersetzt werden. Ein Firmwarewechsel, Root oder eine Werbebereinigung gehören nicht zum Projektumfang.
