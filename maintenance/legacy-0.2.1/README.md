# Wartungsstand des bisherigen YAML-Aufbaus

HA-Leser 0.2.1 / TV-App 1.4.1. Dies ist der kleine Patch für den bestehenden persönlichen Aufbau, keine Migration auf die HACS-Entwicklung 0.3.0. Er wird nicht von HACS als zweite Integration installiert.

- Prime Video: gemessen als Android-Keycode 194, Scan-Code 207 / Linux KEY_PLAY; öffnet de.exaring.waipu.
- Netflix Scan-Code 416 bleibt Jellyfin.
- Xiaomi TV+ Android 192 / Scan-Code 150 wird konsumiert; KEY_WWW sendet das HA-Ereignis button: tv_plus. Die Beispielautomation startet eine Kinoszene.
- Beispielszene: TV-Beleuchtung an; Spots und Deckenlicht an mit brightness 51 (20 %); kein Rollladenbefehl.
- Lautstärke und bestehende Farbtasten bleiben unverändert.

Die Quellen stammen gezielt aus dem bisher installierten 0.2.0/1.4-Aufbau. Persönliche HA-Adresse, Zielentitäten, Schlüssel und die tatsächlich eingesetzte Package-Datei sind nicht enthalten. Beispiele müssen angepasst werden. Der übergeordnete LICENSE-Text gilt auch hier.

Bauen mit scripts/build-apk.ps1 und denselben Parametern wie in der Haupt-Buildanleitung. Keine Installation durch den Build. VersionName 1.4.1 verwendet für diesen ausschließlich lokalen ADB-Patch bewusst weiterhin versionCode 5, damit die gesicherte Original-APK 1.4 mit gleichem Code und gleicher Signatur ohne Versionscode-Downgrade zurückinstallierbar bleibt. Vor einem öffentlichen Release eine eigene Versions-/Updatepolitik verwenden. Der HACS-Prüfstand 1.5 hat versionCode 6.

Vor Änderung wurden vorhandene APK und die betroffenen HA-Dateien privat lokal gesichert. Der zusätzliche Leserpfad wurde isoliert auf TV+-Entprellung und die bisherigen Leserfunktionen geprüft; bestehende Automationen im Package sind strukturell unverändert. Reale Testergebnisse und Rücknahme werden im privaten Vault-Betriebsstand gepflegt.

Isolierte Prüfung aus dem Haupt-Repository: `python maintenance/legacy-0.2.1/tests/run.py` mit den Entwicklungsabhängigkeiten.

Korrektur der Kino-Zuordnung: Die zunächst gewählte Deckenlampe gehört laut Nutzer zum Bad, obwohl HA sie unter Wohnzimmer meldet. Sie wurde aus der Live-Szene entfernt; Konfiguration geprüft und ausschließlich Szenen über den angemeldeten HA-Browser neu geladen. Die Badlampe war bereits wieder bei 100 %. Aktuelle Kinoszene: TV-Beleuchtung an, Hue-Spots 20 %; keine Deckenlampe zugeordnet. Die richtige Wohnzimmer-Deckenlampe erst bei einem späteren Termin eindeutig identifizieren. Der bisherige 20-%-Messwert war kein Nachweis für die richtige Kino-Deckenbeleuchtung.
