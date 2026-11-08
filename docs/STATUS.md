# Projektstand

Stand: 2026-11-08. Öffentliches Repository: https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge.

## Zustand

Integration 0.5.0, TV-App 1.7/versionCode 8. GPL-3.0-only. [v0.5.0 als erster öffentlicher Vorabrelease veröffentlicht](https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge/releases/tag/v0.5.0), Tag-Commit 4b2ad7b4691c8dabf94f6725b3997e66d018e506. APK, Integration, passendes Quellarchiv und SHA256SUMS vorhanden. Die APK bleibt unverändert; ihr Anleitungstitel nennt irrtümlich 1.6.

Am Testaufbau sind 0.5.0/1.7 installiert. Nutzer bestätigt lokale App-Einzel-/Langbelegung Jellyfin/Twitch. Lautstärke kurz/halten/loslassen und Altbelegungen wurden mit HA 0.5.0/alter APK 1.6 bestätigt; nach APK-Update keine erneute ausdrückliche Lautstärkeprüfung. Keine allgemeine Gerätekompatibilität ableiten.

## Prüfung

Am 08.11. erneut 37 HA-/Gestentests mit Core 2026.10.4 und simuliertem ADB, zehn isolierte Leser-/Rollladentests und zehn Java-Gestentests bestanden. APK-Signatur v2/v3, Manifest, unveränderte Prüfsumme, JSON/YAML, DE/EN-Schlüssel und lokale Doku-Dateilinks geprüft. HACS, hassfest und Softwaretests am Tag-Commit im [CI-Lauf](https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge/actions/runs/42472827447) und erneut im [Release-Workflow](https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge/actions/runs/42472934722) erfolgreich; Veröffentlichungsschritt ebenfalls erfolgreich. Paketstruktur, Lizenz, passende Quellen und Prüfsummen geprüft. Keine produktive HA-/TV-Änderung während der Veröffentlichung.

## Offen und nächste Schritte

Vollständige Hardwareprüfung für Doppel-/HA-Gesten, Zeitgrenzen, Lautstärke nach APK 1.7, Ausfall, Neustart und Rücknahme. Mehrere TV-Eingänge und TLS-Pairing sind nicht implementiert. Anleitungstitel bei nächstem APK-Build korrigieren, versionCode erhöhen und Signierer erhalten. Installation über ein benutzerdefiniertes HACS-Repository an einem frischen Aufbau separat praktisch prüfen; allgemeine HACS-Standardliste separat beantragen.

## Relevante Dateien und letzte Änderung

README.md; docs/INSTALLATION.md; docs/PRUEFUNG.md; docs/HARDWARETEST.md; docs/BUILD.md; docs/BUILD-EN.md; NOTICE.md; .github/workflows/validate.yml; .github/workflows/release.yml; custom_components/tv_volume_bridge/manifest.json.

Letzte Änderung: erfolgreichen öffentlichen Vorabrelease und CI-Nachweise eingetragen. Private Rückwegdaten bleiben außerhalb des Repositories. Nächster Chatumfang: gezielte verbleibende Hardware-/HACS-Installationsprüfung oder nächster APK-Patch.
