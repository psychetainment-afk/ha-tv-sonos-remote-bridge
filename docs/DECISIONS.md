# Verbindliche Entscheidungen

- Zuerst ein Home-Assistant-Komplettpaket für HACS entwickeln. Einrichtung und Tastenbelegungen gehören in den HA-Browser. Ein separates öffentliches Tastenmapper-Produkt ist zurückgestellt.
- HA führt den lokalen ADB-Leser selbst aus. Kein zusätzlicher Container oder dauerhaft benötigter Installationscomputer.
- Die TV-App bleibt eine Komponente ohne Netzwerkberechtigung. App-Ziele funktionieren nach Konfiguration lokal; Hausaktionen werden über HA ausgeführt.
- Eigener Projektcode unter GPL-3.0-only. Abhängigkeiten behalten ihre Lizenzen.
- Öffentliche Veröffentlichung im beauftragten GitHub-Repository als erste Vorabversion; Standard-HACS-Katalog separat. Produktiven Aufbau durch die HACS-Entwicklung nicht verändern; gesondert beauftragte Wartungspatches am bisherigen Aufbau gezielt sichern und prüfen.
- Gerätekompatibilität nur für gemessene Firmware/Fernbedienung behaupten. Kein Root, Bootloader-/Firmwarewechsel oder Werbebereinigung als Teil dieses Pakets.
- Persönliche Hausaktionen bleiben austauschbare Beispiele. Rollladenbeispiel erhält die 50-%-Offengrenze, Fahrt/Stopp/Gegenrichtung; Licht ohne feste Helligkeitsvorgabe.

- Learnings aus dem Hardwaretest vom 8. November 2026: installierte TV-Apps mit lesbaren Namen auswählen; Eingabegerät per Tastendruck ermitteln, mit manueller Rückfallauswahl. Anleitung zu Entwickleroptionen, ADB-Freigabe und Bedienungshilfe direkt in der Einrichtung und später erneut erreichbar anbieten. Neue Installationen ohne Beispielbelegungen, bestehende Konfiguration erhalten.

- Gewünschter Funktionsumfang vom 8. November 2026: Einzel-, Doppel- und Langdruck für frei belegbare Tasten vorsehen; Lokal umgesetzt in 0.5.0/1.7; App-Einzel/Lang teilweise hardwarebestätigt; weitere Prüfungen offen. Bestehende Belegungen als Einzeldruck erhalten, Lautstärke-Haltewiederholung und reservierte Power-Taste erhalten. TV-App bleibt ohne Netzwerkberechtigung; lokale App-Ziele sollen ohne laufendes HA funktionieren. Technischer Gestenablauf und Prüfkriterien unter [STATUS](STATUS.md); Zeitfenster und Zuständigkeit zwischen App und HA vor Umsetzung festlegen.
