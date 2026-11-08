# English

First public **preview** of TV Sonos Remote Bridge: integration **0.5.0**, companion TV app **1.7 / versionCode 8**.

Use an Android TV remote for Sonos volume, TV-app shortcuts and Home Assistant actions. HA-based setup, remote discovery, button learning, English/German interface, and single/double/long assignments. Local ADB, no cloud service; the companion app has no INTERNET permission.

Install through this custom HACS repository (Integration; enable prereleases where available) or use the integration ZIP. Extract its tv_volume_bridge folder under /config/custom_components and restart HA. See README and docs/INSTALLATION.md. Not included in the HACS default catalogue.

Hardware evidence is limited to Xiaomi MiTV-MOEU0 / Android TV 14 / Xiaomi RC Consumer Control with Sonos Playbar. App single/long was user-confirmed on 0.5.0/1.7. Volume short/hold/release was confirmed on HA 0.5.0 with APK 1.6, not explicitly rechecked after APK 1.7. Double/HA gestures, timing boundaries, outage/restart recovery and rollback remain open. Classic ADB TCP/RSA only, no TLS pairing. No app/HA target mixing on the same button. APK 1.7 help title still says 1.6. Downgrade not guaranteed.

GPL-3.0-only. Assets: signed APK, integration ZIP, matching source ZIP and SHA256SUMS. Build instructions and dependency notices are in the source. Signing keys remain private. Automated HACS, hassfest, HA/reader and Java gesture checks must pass before this release workflow publishes.

# Deutsch

Erste öffentliche **Vorabversion**: Integration **0.5.0**, TV-App **1.7 / versionCode 8**. Android-TV-Fernbedienung für Sonos-Lautstärke, TV-Apps und HA-Aktionen; Einrichtung und Tastenlernen im HA-Browser, Einzel-/Doppel-/Langdruck, deutsche und englische HA-Oberfläche. Lokal über ADB, keine Cloud; TV-App ohne INTERNET-Berechtigung.

Als benutzerdefiniertes HACS-Repository vom Typ Integration hinzufügen und gegebenenfalls Vorabversionen aktivieren. Alternativ tv_volume_bridge aus dem Integrations-ZIP nach /config/custom_components entpacken und HA neu starten. Anleitung in README und docs/INSTALLATION.md. Keine Aufnahme im HACS-Standardkatalog.

Gerätebelege nur für Xiaomi MiTV-MOEU0 / Android TV 14 / Xiaomi RC Consumer Control und Sonos Playbar. App-Einzel/Lang mit 0.5.0/1.7 bestätigt. Lautstärke kurz/halten/loslassen unter HA 0.5.0 mit APK 1.6 bestätigt, nach APK 1.7 noch nicht erneut ausdrücklich geprüft. Doppel-/HA-Gesten, genaue Zeitgrenzen, Ausfall-/Neustart-/Rücknahmetests offen. Kein TLS-Pairing oder App-/HA-Mischziel auf derselben Taste. Kosmetischer Fehler: APK-1.7-Anleitungstitel nennt 1.6. Downgrade nicht garantiert.

GPL-3.0-only. APK, Integration, passendes Quellarchiv und SHA256SUMS enthalten; Buildanleitung und Lizenzhinweise in den Quellen, Signierschlüssel privat. Veröffentlichung durch den Tag-Workflow erst nach erfolgreichen HACS-, hassfest-, HA-/Leser- und Java-Gestenprüfungen.
