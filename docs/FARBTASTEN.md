# Tastenbelegung und Rohsignale

Diese Seite dokumentiert historische Gerätemessungen und optionale YAML-Beispiele aus 0.2.0/1.4. In 0.5.0/TV-App 1.7 sind Belegungen im HA-Browser frei änderbar; neue Installationen beginnen ohne diese Ziele. Aktueller Prüfstand: [PRUEFUNG.md](PRUEFUNG.md). Nicht zugleich eine Beispielautomation und eine identische direkte HA-Aktionsbelegung aktivieren.

Prüfdatum: 7. November 2026. Der Nutzer drückte Rot, Grün, Gelb, Blau in dieser Reihenfolge; vier unterscheidbare DOWN/UP-Paare wurden erfasst.

| Physische Taste | Linux-Ereignis | HID MSC_SCAN | Aktuelle Aktion |
|---|---|---|---|
| Rot | KEY_STOPCD | 000c00b7 | Frei/unverändert |
| Grün | KEY_EJECTCD | 000c00b8 | Rollladen Fahrt / Stopp / Gegenrichtung |
| Gelb | KEY_SHUFFLE | 000c00b9 | Hue-Spots ein/aus, letzte Helligkeit |
| Blau | KEY_SEARCH | 000c0221 | Sonos-Nacht-Sound ein/aus |

Das Gerät hieß bei der Messung `Xiaomi RC Consumer Control`, damals `/dev/input/event4`. Der Leser ermittelt die Nummer dynamisch. Die Linux-Bezeichnungen beschreiben Treibersignale; sie entsprechen nicht den aufgedruckten Farben. Für Blau wurden zusätzlich Android-Keycode 186 und Scan-Code 217 im App-Dienst gelesen. Andere Android-Codes wurden nicht einzeln als Messwerte protokolliert.

Netflix wurde als Linux KEY_VIDEOPHONE/Scan-Code 416 erkannt; Xiaomi TV+ als Android-Keycode 192/Scan-Code 150. Im damaligen Aufbau führten beide zu Jellyfin; die aktuelle APK enthält diese Ziele nicht als Standardbelegung.

## Grün: Bedienung wie ein Rollladentaster

1. Im Stillstand startet Grün die nächste Fahrt.
2. Während einer Fahrt hält Grün den Rollladen an.
3. Der folgende Druck startet die Gegenrichtung.

Beispiel: runter → Stopp → hoch → Stopp → runter. Abwärts endet diese Tastensteuerung spätestens bei **50 % offen**, aufwärts bei ganz offen. Home Assistant verwendet 0 = geschlossen und 100 = offen. Andere bestehende Rollladensteuerungen wurden nicht verändert.

Der Helfer `input_boolean.tv_remote_cover_next_open` merkt die nächste Richtung. Bei einem Stopp wird die tatsächliche Fahrtrichtung berücksichtigt. Die Aktion fährt nicht los, wenn Position, Verfügbarkeit oder Helferzustand fehlen. Nach erstmaligem Anlegen des Helfers müssen Helfer und Automationen geladen werden.

## Gelb und Blau

Gelb schaltet die Hue-Spots-Gruppe ein oder aus. Beim Einschalten wird kein Helligkeitswert vorgegeben; die zuletzt verwendete Einstellung soll erhalten bleiben. Eine feste TV-Dimmung ist ausdrücklich nicht gewünscht.

Blau schaltet Sonos-Nacht-Sound um. Der eingeschaltete Zustand wurde nach dem Tastentest über Sonos gelesen. Die bestehende Audio-Profilautomatik bleibt unabhängig davon aktiv.

## Prüfergebnis

Gelb ein/aus und Grün einschließlich Fahrt/Stopp/Gegenrichtung sind nach dem YAML-Reload vom Nutzer bestätigt. HA meldete die korrigierte Rollladenposition 50. Die APK verhindert zusätzliche Vordergrund-App-Aktionen für Grün/Gelb/Blau. Lautstärke und Jellyfin-Tasten bleiben erhalten.
