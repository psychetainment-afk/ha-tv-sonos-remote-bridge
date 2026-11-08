# Gerätekompatibilität

## Bestätigter Aufbau

Praktisch geprüft am 7. November 2026:

| Merkmal | Geprüfter Wert |
|---|---|
| Hersteller / Modellkennung | Xiaomi MiTV-MOEU0 |
| Plattformname | ladybird |
| Betriebssystem | Android TV 14 |
| Firmware-Build | UKN1.240806.017.V816.0.25.12.1.ULBMIXM |
| Sicherheitspatch | 5. November 2025 |
| ADB-Eingabegerät | Xiaomi RC Consumer Control |
| Audioaufbau | Optisch angeschlossene Sonos Playbar; Steuerung über Home Assistant |

Handelsname und Bildschirmgröße sind durch diese Modellkennung nicht eindeutig bestätigt. Eine andere Firmware desselben Modells muss erneut geprüft werden.

## Andere Android TVs und Google TVs

Der Ansatz ist nicht auf Xiaomi-Technik angewiesen: Android stellt Bedienungshilfen zum Filtern von Tasten sowie das Diagnosewerkzeug getevent bereit. Daraus folgt jedoch keine allgemeine Geräteunterstützung. Herstellerrechte, ADB-Verbindungsart, Fernbedienung und weitergereichte Tastencodes entscheiden über die nutzbaren Funktionen.

Vor einer Kompatibilitätsmeldung müssen folgende Punkte geprüft werden:

1. Klassischer ADB-TCP/RSA-Zugang funktioniert dauerhaft mit Home Assistant. Moderne WLAN-TLS-Kopplung unterstützt der aktuelle Leser noch nicht.
2. getevent darf die tatsächlichen Tastendrücke ohne zusätzliche Root-Rechte lesen. Auf dem geprüften Xiaomi ist das möglich; auf anderen Geräten bleibt es offen.
3. Eingabegerätename und Codes werden gemessen. Version 0.4.0 bietet Erkennung per Leiser-Tastendruck, manuelle Geräteauswahl und numerisches Tastenlernen. Neue Einträge beginnen ohne Beispielbelegungen. Geräteerkennung und App-Auswahl von 0.4.0/1.6 brauchen den realen Hardwaretest; die 0.3.0-Teilprüfung steht in STATUS.md.
4. Der Bedienungshilfen-Dienst lässt sich aktivieren und erhält die gewünschten App-Tasten. Systemtasten können von der Firmware abgefangen werden.
5. Halten/Loslassen, konkurrierende Originalaktionen, Standby und Wiederverbindung werden am realen Gerät geprüft.

Samsung Tizen und LG webOS sind keine Android-TV-Plattformen und werden durch die vorhandene APK nicht unterstützt. Google TV als Bezeichnung allein genügt ebenfalls nicht für eine Kompatibilitätszusage.

Für Beiträge bitte Modell, Android-Version, Firmware-Build, Fernbedienung, gemessene Codes und bestandene Funktionen angeben. Keine Seriennummern, Schlüssel oder vollständigen privaten Diagnoselogs veröffentlichen.

## Quellen

- [Android AccessibilityService](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService)
- [Android getevent](https://source.android.com/docs/core/interaction/input/getevent)
- Eigene Messungen und Funktionsprüfungen: [Prüfung](PRUEFUNG.md), [Einstieg](EINSTIEG.md).

## Vorgeschlagener Git-Ablauf

Den geprüften Ausgangsstand zunächst auf main committen und als experimentellen Prototyp veröffentlichen. Neue Funktionen auf kurzen Themenbranches entwickeln, beispielsweise feature/ha-config-flow, und erst nach Prüfung übernehmen. Ein dauerhafter develop-Branch ist für den bisherigen kleinen Projektumfang nicht erforderlich. Ein öffentlicher Prototyp ist noch keine HACS-Veröffentlichung.
