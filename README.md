# TV Sonos Remote Bridge

[English](#english) | [Deutsch](#deutsch)

![TV Sonos Remote Bridge icon](custom_components/tv_volume_bridge/brand/icon.png)

## English

Use your Android TV remote to control Sonos volume, launch TV apps, and trigger Home Assistant actions.

### Why this exists

My TV uses a Bluetooth remote, while an older Sonos Playbar receives audio over an optical cable. The remote controls the TV, but the optical connection does not carry volume commands to Sonos. This project replaces the second remote I previously needed for volume control.

Home Assistant reads remote button events over a local ADB connection and controls the selected media player. A bundled companion TV app handles local app shortcuts and suppresses their original actions where the firmware allows it. On the tested Xiaomi, volume keys do not reach our accessibility service, so the TV app alone cannot provide the complete solution. See the [architecture](docs/ARCHITECTURE.md) for evidence and limitations.

### Features

- Set up the connection, discover the remote, learn buttons, and edit assignments in Home Assistant.
- Control Sonos volume, including holding a volume key and stopping on release.
- Assign single, double, and long presses to installed TV apps, HA actions, or HA events.
- Each button uses either local TV-app targets or HA actions/events; mixing both on one button is not supported.
- Install the bundled signed APK and transfer assignments from the HA options dialog.
- English and German HA interface, connection status, and redacted diagnostics.
- Local operation: no cloud service, extra container, or permanently running installation computer. The TV app has no INTERNET permission.

### Requirements and compatibility

- Home Assistant **2026.10.0 or newer**; automated tests use Core **2026.10.4**.
- Android/Google TV with **classic ADB TCP/RSA access**, reachable from HA. Wireless-debugging pairing codes/TLS are not supported.
- A Sonos or other suitable media player already configured in HA.
- The companion app requires Android 8/API 26 or newer and an enabled accessibility service.

Hardware evidence is limited to **Xiaomi MiTV-MOEU0, ladybird, Android TV 14**, Xiaomi RC Consumer Control, and a Sonos Playbar. Other models and firmware need their own tests. Samsung Tizen and LG webOS are not supported.

### Install

Add this repository to **HACS → Custom repositories → Integration**, download it, and restart Home Assistant:

```text
https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge
```

Then select **Settings → Devices & services → Add integration → TV Sonos Remote Bridge**. Follow the TV preparation and ADB authorization steps, choose the volume target, and configure the companion app in the integration options. Keep ADB within your trusted local network.

This is a **custom HACS repository**, not an entry in the HACS default catalogue. For prereleases, enable beta/prerelease versions in HACS where available; manual installation is also documented.

**[Step-by-step installation / Schritt-für-Schritt-Anleitung](docs/INSTALLATION.md)**

### Preview release and known limits

Local patch **0.5.1**, bundled TV app **1.7.1 / versionCode 9**, GPL-3.0-only. Installed on the personal test setup; no new tagged release. Public prerelease remains **0.5.0 / 1.7**.

The previous 0.5.0 / 1.7 pair has been installed on the test setup. App single/long press (Jellyfin/Twitch) was confirmed by the user on real hardware. Volume short/hold/release was confirmed with HA 0.5.0 and the previous APK 1.6; it has not been explicitly rechecked after installing APK 1.7. Double press, HA gestures, precise timing boundaries, outage/restart recovery, and rollback remain incompletely tested on hardware. Automated tests use simulated ADB and do not replace these checks.

Double press uses a 350 ms window after release; long press fires once after 750 ms. Single actions may wait when a double/long target is configured. Power and volume are reserved. Buttons on multiple input devices are not automatically combined. Local app targets work without HA after configuration; volume and HA actions require HA, networking, and TV ADB.

APK 1.7.1 derives the help title from the installed package version, fixing the old 1.6 title. See [button/volume review](docs/REVIEW-2026-11-09.md) for the new function-specific editor, one-point volume option and TV-bar limitations. APK downgrades are not guaranteed. Never run two readers against the same remote or uninstall automatically to resolve a signature conflict.

### Development and licence

The matching APK sources are under [android/app/src/main](android/app/src/main), with the [build script](scripts/build-apk.ps1) and [English build instructions](docs/BUILD-EN.md). Signing keys are private. Source archives are published alongside the binary release.

```sh
python -m pip install -r requirements-ha-test.txt
python tests/run.py
python -m pytest
```

HA tests require Python 3.14.2 or newer. See [test results](docs/PRUEFUNG.md), [migration](docs/MIGRATION.md), [hardware test plan](docs/HARDWARETEST.md), and [third-party notices](NOTICE.md).

Project code: [GNU GPL version 3 only](LICENSE), **SPDX: GPL-3.0-only**. Dependencies retain their own licences. This is an independent project, not affiliated with Sonos, Xiaomi, Google, or Home Assistant.

## Deutsch

Nutze deine Android-TV-Fernbedienung für Sonos-Lautstärke, TV-Apps und Home-Assistant-Aktionen.

### Warum es das Projekt gibt

Mein Fernseher hat eine Bluetooth-Fernbedienung; die ältere Sonos Playbar erhält den Ton über ein optisches Kabel. Darüber gelangen keine Lautstärkebefehle zur Sonos. Bisher brauchte ich deshalb eine zweite Fernbedienung nur für Lauter und Leiser.

Die Integration liest Tastensignale über eine lokale ADB-Verbindung und steuert den gewählten HA-Medienplayer. Die mitgelieferte TV-App übernimmt lokale App-Tasten und unterdrückt deren Originalaktionen, soweit die Firmware das zulässt. Beim getesteten Xiaomi erreichen Lautstärketasten unsere Bedienungshilfe nicht; deshalb ist zusätzlich der HA-Leser nötig. Belege und Grenzen stehen in der [Architektur](docs/ARCHITECTURE.md).

### Funktionen

- Verbindung, Fernbedienungserkennung, Tastenlernen und Belegungen direkt im HA-Browser.
- Sonos-Lautstärke einschließlich Halten und Stoppen beim Loslassen.
- Einzel-, Doppel- und Langdruck für TV-Apps, HA-Aktionen oder HA-Ereignisse.
- Je Taste entweder lokale App-Ziele oder HA-Aktionen/Ereignisse; keine Mischung auf derselben Taste.
- Signierte TV-App installieren und Belegungen aus dem HA-Dialog übertragen.
- Deutsche und englische HA-Oberfläche, Status und bereinigte Diagnose.
- Lokal ohne Cloud, zusätzlichen Container oder dauerhaft benötigten Installationscomputer. Die TV-App hat keine INTERNET-Berechtigung.

### Voraussetzungen und Installation

Home Assistant ab **2026.10.0**, ein in HA eingerichteter Sonos-/Medienplayer und Android-/Google-TV mit **klassischem ADB-TCP/RSA-Zugang** im vertrauenswürdigen Heimnetz. Kopplungscode/TLS wird nicht unterstützt. Die TV-App benötigt mindestens Android 8/API 26 und eine aktivierte Bedienungshilfe.

Praktisch erprobt: **Xiaomi MiTV-MOEU0 / ladybird / Android TV 14**, Xiaomi RC Consumer Control und Sonos Playbar. Andere Geräte/Firmwares brauchen eigene Tests. LG webOS und Samsung Tizen werden nicht unterstützt.

Dieses Repository in **HACS → Benutzerdefinierte Repositories → Integration** hinzufügen, herunterladen und HA neu starten. Danach **Einstellungen → Geräte & Dienste → Integration hinzufügen → TV Sonos Remote Bridge**. Im Dialog ADB-Freigabe und Lautstärkeziel einrichten; die TV-App über die Optionen konfigurieren. Es handelt sich um ein benutzerdefiniertes Repository, keinen Eintrag im HACS-Standardkatalog. Vorabversionen gegebenenfalls über die Beta-/Vorabversionsauswahl aktivieren.

**[Vollständige Installation](docs/INSTALLATION.md)** · [Migration](docs/MIGRATION.md) · [Kompatibilität](docs/KOMPATIBILITAET.md)

### Vorabversion und Grenzen

Lokaler Patch **0.5.1**, TV-App **1.7.1 / versionCode 9**, am eigenen Testaufbau installiert, ohne neuen getaggten Release. Öffentlicher Vorabrelease bleibt **0.5.0 / 1.7**; Testaufbau jetzt **0.5.1 / 1.7.1**; App-Einzel/Lang für Jellyfin/Twitch wurde vom Nutzer bestätigt. Lautstärke kurz/halten/loslassen ist unter HA 0.5.0 mit alter APK 1.6 bestätigt, nach APK 1.7 noch nicht erneut ausdrücklich geprüft. Doppel-, HA-Gesten-, Ausfall-, Neustart- und Rücknahmetests sowie genaue Zeitgrenzen bleiben offen.

Doppel: 350 ms nach Loslassen; lang: einmal nach 750 ms. Bei Mehrfachbelegung kann Einzel verzögert reagieren. Power und Lautstärke bleiben reserviert. Unterschiedliche Eingabegeräte werden nicht automatisch zusammengeführt. Lokale App-Ziele funktionieren nach Einrichtung ohne HA; Lautstärke und HA-Aktionen benötigen HA, Netzwerk und TV-ADB.

APK 1.7.1 liest den Anleitungstitel aus der Paketversion und korrigiert den alten Titel 1.6. [Tasten-/Lautstärkeprüfung](docs/REVIEW-2026-11-09.md): getrennte Funktionsdialoge, Einerschritte und Grenzen des TV-Balkens. Ein APK-Downgrade ist nicht garantiert. Niemals zwei Leser gleichzeitig betreiben oder bei Signaturkonflikten automatisch deinstallieren.

[Prüfstand](docs/PRUEFUNG.md) · [Hardwaretest](docs/HARDWARETEST.md) · [APK bauen](docs/BUILD.md) · [Projektstand](docs/STATUS.md)

### Lizenz und Quellen

Eigener Projektcode unter [GNU GPL Version 3](LICENSE), **GPL-3.0-only**. Passende APK-Quellen, Buildskript und Buildanleitung werden mitgeliefert; Signierschlüssel bleiben privat. Abhängigkeiten behalten ihre [eigenen Lizenzen](NOTICE.md). Unabhängiges Projekt ohne Verbindung zu Sonos, Xiaomi, Google oder Home Assistant. Persönliche HA-Konfiguration ist nicht enthalten; neue Einträge beginnen mit leeren Belegungen.
