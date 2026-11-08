# Migration and rollback / Bestehenden Aufbau umstellen

Automated tests use temporary HA data and simulated ADB. Installation and APK transfer are separate, deliberate operations on the real setup.

1. Privately back up HA and the installed integration, relevant packages/automations, assignments, APK version and available recovery data. Never include ADB/signing keys in Git.
2. Record the current app signer and accessibility setting. A backup APK does not guarantee a downgrade.
3. Stop the old reader before connecting the new UI entry. Never run two readers against one remote. The UI setup blocks while legacy tv_volume_bridge YAML is active; disable only that reader block and retain independent automations/helpers.
4. Install the complete new integration folder and restart HA. Confirm connection and existing volume behaviour before changing the APK.
5. Update the bundled APK separately and confirm the accessibility service. A signature conflict aborts installation; never automatically uninstall to work around it.
6. App 1.7 is required for multiple gesture targets. Confirm old single assignments first, then configure gestures. Legacy colour-event automations can remain; avoid duplicating the same action in the editor.
7. Transferring assignments replaces TV-app mappings. Confirm desired mappings and test under supervision. Keep the 50%-open boundary of the cover example.

## Rückweg / Rollback

Disable the new HA entry first; disable TV accessibility if local remaps must stop. Restore only the affected integration/YAML from private backups, validate HA configuration and restart as needed. Preserve unrelated later changes. Exactly one reader may be active.

Android can reject older APK version codes even with the same signer. No automatic uninstall and no guaranteed downgrade. Keep a working fallback (for example the Sonos app); restore a complete HA backup only as a deliberate separate operation. Current-version restart/outage/rollback hardware tests are still open. This project does not modify or back up TV firmware/bootloader.
