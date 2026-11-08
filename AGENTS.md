# Projektregeln

- Dieses Repository ist der Quellcode-Einstieg. Das Dokumentations-/Installationspaket ist ein daraus abzuleitender Snapshot.
- Ausgangsproblem: Bluetooth-TV-Fernbedienung kann eine optisch angeschlossene ältere Sonos-Playbar nicht über das Audiokabel in der Lautstärke steuern.
- TV-App und HA-Leser getrennt halten. Die APK braucht derzeit keine Netzwerkberechtigung.
- Keine privaten ADB-/Signierschlüssel, Tokens, persönliche HA-Konfiguration oder Gerätedaten in Git aufnehmen.
- Keine laufenden TVs, Lautsprecher, Rollläden oder HA-Konfiguration allein zum Bearbeiten dieses Repositories ändern.
- Tests: `python tests/run.py`; Build und manuelle Geräteprüfung siehe docs/BUILD.md und docs/PRUEFUNG.md.
- Den bestätigten Aufbau und die 50-%-Abwärtsgrenze der Beispiel-Rollladensteuerung erhalten. Hardware-/Firmwarekompatibilität nicht aus Handelsnamen ableiten.
- Dokumentation auf den gültigen Stand bringen; keine Chat-Chronik. Zustand und nächste Schritte in docs/STATUS.md.
- Remote-Ziel, Sichtbarkeit und Lizenz vor Veröffentlichung klären. Keine Veröffentlichung als HACS-Integration behaupten, solange sie nicht erfolgt ist.
