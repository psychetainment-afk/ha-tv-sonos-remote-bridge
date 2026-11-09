# Projektstand

Stand: 2026-11-09. Repository: https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge.

## Zustand

**0.5.1 / TV-App 1.7.1 (versionCode 9) am persönlichen Testaufbau installiert**, nach Nutzerbestätigung zum Push freigegeben; kein neuer Release. Lautstärke-Voreinstellung jetzt **ein Prozentpunkt**, auch für bestehende Einträge ohne explizite Option. Funktionsabhängige HA-Belegungsdialoge und korrigierter Versionstitel enthalten. Öffentlicher Vorabrelease weiterhin 0.5.0 / 1.7. Gespeicherte Tastenbelegungen und Optionen unverändert.

## Prüfung

Private Sicherung von Komponentenordner, Bridge-Eintrag und TV-APK. 17 Komponentendateien SHA256-geprüft, ha core check erfolgreich, regulärer HA-Neustart abgeschlossen, HTTP 200. APK 1.7.1/9, aktivierte Bedienungshilfe und genau ein getevent-Leser nachgelesen. Verbindungssensor nach Neustart listening mit neuen Pegelattributen (Recorder). Keine Lautstärke-/Licht-/Rollladenaktion durch Codex. Auf Nutzerwunsch keine erneute große Testreihe; frühere Patchprüfung: 44 HA-, zehn Leser-/Rollladen- und zehn Java-Gestentests. [Review und Installationsnachtrag](REVIEW-2026-11-09.md).

## Offen und nächster Schritt

Nutzer bestätigt die direkte HA-Belegung als funktionierend; Beschriftung weiterhin etwas unklar. Damit ist die zuvor bedingte Push-Freigabe erfüllt. Lautstärke-Einerschritte installiert, keine zusätzliche ausdrückliche physische Lautstärkebestätigung ableiten. Sporadischer Android-100-%-/Mute-Fall weiterhin nicht abschließend reproduziert; Sonos unterstützt keine Zwischenstufe unter 1. Keine weitere Diagnose-/Testausweitung ohne Anlass. Kein neuer HACS-/hassfest-Lauf oder Release.

## Relevante Dateien und letzte Änderung

custom_components/tv_volume_bridge/{config_flow,runtime,reader,sensor,diagnostics}.py; Android MainActivity/Manifest; tests/test_review.py; docs/REVIEW-2026-11-09.md; docs/INSTALLATION.md.

Letzte Änderung: lokales HA-/TV-Update und Einerschritt-Voreinstellung aktiviert, Wiederanlauf und unveränderte Belegungen geprüft; direkte HA-Belegung vom Nutzer bestätigt; getesteten Stand zum Push freigegeben.
