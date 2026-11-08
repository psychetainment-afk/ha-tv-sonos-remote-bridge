# Hardware test plan / Hardwaretest

Current pair: HA integration 0.5.0 / TV app 1.7. Evidence and its version limits: [PRUEFUNG.md](PRUEFUNG.md). A passing automated test does not mark any hardware item below as passed.

Before updates, privately back up HA, the current integration, relevant YAML/automations, app version and assignments. Confirm recovery credentials and a fallback such as the Sonos app. Never publish keys or personal configuration. Update HA and APK separately; exactly one reader may run. See [migration](MIGRATION.md).

- [ ] Confirm volume short/hold/release after APK 1.7; release must stop repetition.
- [ ] Confirm existing assignments without duplicate original actions.
- [ ] Test distinct local app targets for single/double/long and a long second press; exactly one target must run.
- [ ] Test HA gestures first with harmless events, then intended actions.
- [ ] Check 350 ms double/750 ms long boundaries, missing release, learning timeout and cancellation.
- [ ] Remove one gesture and preserve the others; restore intended assignments.
- [ ] Confirm local app shortcuts without the HA reader when a temporary pause is acceptable.
- [ ] Reload integration, then separately restart TV and HA; confirm reconnection and actual keys after each.
- [ ] Test controlled TV network loss and reconnection without queued/replayed actions.
- [ ] Separately plan a host restart and rollback; do not interrupt unrelated services without authorization.

On duplicate actions, uncontrolled volume/movement or connection problems, disable the integration; also disable the TV accessibility service if local remaps need stopping. Do not automatically uninstall. An old APK is not a guaranteed downgrade path. Stop tests when recovery is uncertain.

Record version pair, generic device/firmware, test result and observation, without private IPs, keys or full diagnostics. German setup: [INSTALLATION.md](INSTALLATION.md).
