# Projektstand

Stand: 2026-11-08. Öffentliche Release-Vorbereitung für https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge.

## Zustand

Integration 0.5.0, TV-App 1.7/versionCode 8. GPL-3.0-only. Erster öffentlicher Stand als Vorabversion vorgesehen. Die aktuelle APK bleibt unverändert; ihr Anleitungstitel nennt irrtümlich 1.6.

Am Testaufbau sind 0.5.0/1.7 installiert. Nutzer bestätigt lokale App-Einzel-/Langbelegung Jellyfin/Twitch. Lautstärke kurz/halten/loslassen und Altbelegungen wurden mit HA 0.5.0/alter APK 1.6 bestätigt; nach APK-Update keine erneute ausdrückliche Lautstärkeprüfung. Keine allgemeine Gerätekompatibilität ableiten.

## Prüfung

Am 08.11. erneut 37 HA-/Gestentests mit Core 2026.10.4 und simuliertem ADB sowie zehn isolierte Leser-/Rollladentests bestanden. APK und passende Quellen vorhanden. HACS/hassfest werden im Veröffentlichungsworkflow gegen das tatsächliche Repository geprüft; ihr Ergebnis steht in GitHub Actions und wird vor dem Release kontrolliert.

## Offen und nächste Schritte

Vollständige Hardwareprüfung für Doppel-/HA-Gesten, Zeitgrenzen, Lautstärke nach APK 1.7, Ausfall, Neustart und Rücknahme. Mehrere TV-Eingänge und TLS-Pairing sind nicht implementiert. Anleitungstitel bei nächstem APK-Build korrigieren, versionCode erhöhen und Signierer erhalten. Vor Veröffentlichung CI abschließen; allgemeine HACS-Standardliste separat beantragen.

## Relevante Dateien und letzte Änderung

README.md; docs/INSTALLATION.md; docs/PRUEFUNG.md; docs/HARDWARETEST.md; docs/BUILD.md; docs/BUILD-EN.md; NOTICE.md; .github/workflows/validate.yml; .github/workflows/release.yml; custom_components/tv_volume_bridge/manifest.json.

Letzte Änderung: öffentliche Zielmetadaten, zweisprachiger Einstieg und bereinigte Release-Dokumentation. Private Rückwegdaten bleiben außerhalb des Repositories. Technische Release- und CI-Nachweise stehen am veröffentlichten Commit.
