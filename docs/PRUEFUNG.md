# Test evidence / Prüfstand

Stand: 2026-11-08. Integration 0.5.0 / APK 1.7 (versionCode 8).

## Automated checks / Automatisierte Prüfungen

Re-run on 2026-11-08: 37 tests with real Home Assistant Core 2026.10.4 and simulated ADB; ten isolated reader/cover-template tests. All passed. The HA dependency stack emits deprecation warnings. Tests use temporary HA data and never connect to real TVs or other devices.

Coverage includes config/options flows, discovery, learning, timeout/cancellation, app lists, installation failure without uninstall, runtime actions, load/unload, gesture ownership/timing, timer cleanup, legacy single bindings, and volume hold/release. The five cover tests execute the actual example templates and verify the 50% lower boundary, stop/reverse, and invalid-state handling.

Android GestureTracker has ten deterministic Java scenarios; all ten passed again on 2026-11-08 with JDK 21. APK v2/v3 signatures, manifest versionCode 8/version 1.7, absence of INTERNET permission and the unchanged bundled SHA256 were rechecked. Earlier build verification confirmed the same signer as its predecessor. The bundled SHA256 is recorded in assets/README.md and release checksums. Binary-reproducible builds have not been established.

HACS, hassfest and all software tests passed in [GitHub Actions validation](https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge/actions/runs/42472537852) on 2026-11-08. The initial validator findings (manifest key ordering, shared-package minimum version and missing repository topics) were corrected. Tag CI repeats these checks before publication. Package verification checked ZIP integrity, unique entry names, required source/build files, licence, bundled APK and SHA256SUMS.

## Hardware evidence / Hardwarebelege

Only Xiaomi MiTV-MOEU0 / ladybird / Android TV 14 with Xiaomi RC Consumer Control and Sonos Playbar has evidence. Historical tests confirmed volume hold/release, app shortcuts and example colour actions on earlier versions. With HA 0.5.0 and APK 1.6, the user confirmed existing app mappings, volume short/hold/release and connected status. The update to APK 1.7 retained its accessibility service and a single reader. The user then confirmed Netflix single press → Jellyfin and long press → Twitch on 0.5.0/1.7.

These are specific observations, not full certification. Volume was not explicitly rechecked after APK 1.7. Double press, long second press, HA gestures, exact timing limits, network/TV/HA/host recovery and rollback remain open for the current pair.

## Architecture observation

On the tested Xiaomi, our accessibility service did not receive volume keys. Android STREAM_MUSIC stayed at 100/100 on SPDIF before and after mixed presses and a separate user-confirmed three-volume-down test. These snapshots support the current raw-input ADB design; they are not a complete event trace and do not establish incompatibility of every alternative app. mUseFixedVolume was false; no global fixed-volume claim is made.

## Known limitations / Grenzen

Classic ADB TCP/RSA only; no TLS pairing. No automatic combination of multiple input devices. Each button has one gesture owner (TV app or HA), no app/HA mixing on that button. TV firmware may retain original button actions. APK 1.7 help title still says 1.6. Downgrade/restore and unattended long-term operation are not guaranteed or fully tested. No independent security audit has been completed.

Full remaining procedure: [HARDWARETEST.md](HARDWARETEST.md). Sources and commands: [BUILD.md](BUILD.md), [BUILD-EN.md](BUILD-EN.md), tests/ and GitHub Actions.
