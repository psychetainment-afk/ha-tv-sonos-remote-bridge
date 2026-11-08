# Veröffentlichung

Ziel: https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge, öffentlich, Maintainer @psychetainment-afk. Integration 0.5.0 / unveränderte TV-App 1.7 (versionCode 8). GPL-3.0-only bleibt bestehen.

Zunächst Vorabrelease und benutzerdefiniertes HACS-Repository. Die Aufnahme in den Standardkatalog ist ein separater Schritt. README und Installation erklären Zweck, Einrichtung, Gerätebelege und offene Hardwaretests auf Englisch und Deutsch. Technische Detailnotizen können Deutsch bleiben.

Vor Tag/Release vorgesehenen Inhalt, Secrets/Privatdaten, Quellen/Lizenzen und APK-Prüfsumme prüfen. Automatisierte Tests, HACS und hassfest müssen erfolgreich sein. Das öffentliche Repository muss für die HACS-Prüfung erreichbar sein; deshalb folgt der Release erst nach dem geprüften ersten Push und dessen CI-Ergebnis.

Der Tag-Workflow prüft erneut und veröffentlicht erst danach einen GitHub-Vorabrelease mit APK, Integrations-ZIP, passendem Quellarchiv und SHA256SUMS. Keine Signierschlüssel oder persönlichen HA-Dateien mitliefern. Signierter APK-Bestand und Quellen bleiben unverändert, einschließlich des dokumentierten kosmetischen Anleitungstitels 1.6 in APK 1.7.

Quellen: [HACS Integration](https://www.hacs.xyz/docs/publish/integration/), [HACS Action](https://www.hacs.xyz/docs/publish/action/), [hassfest](https://contributors.home-assistant.io/blog/2020/04/16/hassfest/), [Lizenz](../LICENSE). Anforderungen am 08.11.2026 erneut gelesen.
