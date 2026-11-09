# Draft: 0.5.1 / APK 1.7.1

Local patch only, installed on the personal test setup, no new tagged release. Previous public prerelease: 0.5.0 / APK 1.7.

- Separate function, action and target screens; first-render domain-filtered HA entities for common actions. Advanced sequences retained.
- Explain HA events versus direct actions; hide unrelated fields and preserve existing gestures.
- Configurable volume step (0 = native, 1–10 absolute percentage points), real target feedback, volume DOWN deduplication and diagnostic logging. Sonos supports whole 0–100 levels; no extra level below 1. Android TV volume bar remains separate.
- Read TV help title from package version, fixing the old 1.6 label. APK 1.7.1/versionCode 9, same signer, no INTERNET permission.

44 HA tests, ten isolated reader/cover tests and ten Android gesture tests passed locally. No new HACS/hassfest CI or physical test. Sporadic TV 100-%/mute observation remains to be captured simultaneously with Sonos state. Limits and verification: [review](REVIEW-2026-11-09.md). GPL-3.0-only; ship matching sources with binaries.

## Deutsch

Lokaler Patch 0.5.1 / APK 1.7.1, am eigenen Testaufbau installiert, ohne neuen getaggten Release. Getrennte Tastenfunktionen, direkt passende HA-Ziele, optionale Einerschritte statt Sonos-Zweierschritten, tatsächliche Pegelrückmeldung und korrigierter Versionstitel. Sonos-Stufe 1 bleibt die kleinste Stufe über 0; TV-Balken zeigt nicht den Sonos-Wert. 44 HA-, zehn Leser- und zehn Android-Gestentests bestanden. Sporadischer Mute-Fall und realer Editorablauf bleiben im Hardwaretest zu prüfen. Bestehender öffentlicher Vorabrelease bleibt 0.5.0 / 1.7.
