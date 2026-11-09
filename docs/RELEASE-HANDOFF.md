# Release checklist

Target: https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge (public).

Local patch 0.5.1 / APK 1.7.1 (versionCode 9), GPL-3.0-only; installed on the personal test setup, no new tagged release. Previous public prerelease remains 0.5.0 / 1.7. See docs/REVIEW-2026-11-09.md for patch validation and outstanding hardware tests. Metadata must name this target and @psychetainment-afk. Public documentation contains no private recovery paths or personal HA configuration.

Before tagging: review intended files, dependency/licence notices, source-to-APK version and checksum, English/German installation, tests, and passing HACS/hassfest runs. Do not claim default-catalogue inclusion. Publish matching source archive with APK and integration package. Signing keys remain private.

Release workflow revalidates the tag before creating a GitHub prerelease. No force-push. Verify remote commit/tag, CI result and downloaded asset checksums. Hardware limitations in README and PRUEFUNG remain part of the release.
