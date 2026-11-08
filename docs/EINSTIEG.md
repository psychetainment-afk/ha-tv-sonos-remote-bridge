# Einstieg: vom Fernseher zum erkannten Tastendruck

Diese Vorbereitung kommt **vor** der Tastenbelegung. Sie ist ohne KI ausführbar. Gemeint ist **ADB – Android Debug Bridge**. Entwickleroptionen, ADB-Freigabe und Bedienungshilfedienst sind drei verschiedene Dinge.

**Normaler Einrichtungsweg:** [INSTALLATION.md](INSTALLATION.md) führt direkt durch den HA-Browser, ohne Computer-ADB. Die folgenden Terminalbefehle sind optionale Diagnose für Entwickler.

## 1. Den benötigten Weg wählen

| Ziel | Was im Betrieb aktiv sein muss |
|---|---|
| Netflix/Xiaomi TV+ mit der vorhandenen APK nach Jellyfin umleiten | TV-App und ihr Bedienungshilfedienst |
| Tasten am Computer untersuchen | Vorübergehend autorisiertes ADB |
| Sonos-Lautstärke und HA-Farbtasten dieses Projekts | TV-ADB, dauerhaft autorisierter HA-Leser, Netzwerk und Home Assistant |

ADB wird bei unserer Installationsmethode zunächst auch zum Installieren der APK verwendet. Für die reine App-Tastenumleitung kann es danach wieder ausgeschaltet werden. Für die HA-Funktionen bleibt es eingeschaltet. Die Bluetooth-Fernbedienung bleibt mit dem Fernseher gekoppelt.

## 2. Entwickleroptionen am TV öffnen

1. Einstellungen → System/Geräteeinstellungen → Info/Über öffnen.
2. Den Eintrag „Android-TV-Betriebssystem-Build“ beziehungsweise „Build“ suchen und siebenmal OK drücken.
3. Zurückgehen und die nun sichtbaren Entwickleroptionen öffnen. Bezeichnungen können je nach Hersteller abweichen.

Entwickleroptionen allein stellen noch keine Verbindung her. Für dieses Projekt werden weder OEM-Entsperrung, Werksmenü noch Änderungen an Grafik-/Protokollierungsoptionen benötigt.

## 3. Den richtigen ADB-Zugang aktivieren

### Geprüfter Xiaomi-Weg, auch über Ethernet

Beim getesteten MiTV-MOEU0 „Mi TV ADB Debugging“ einschalten und einen verlangten TV-Neustart abwarten. Der TV stellt damit einen klassischen ADB-TCP-Zugang auf Port 5555 bereit. Das hat im geprüften Aufbau über Netzwerkkabel funktioniert.

Der separate Schalter „Debugging über WLAN“ ließ sich an diesem Xiaomi ohne WLAN-Verbindung nicht aktivieren. Dafür musste die Ethernet-Verbindung nicht ersetzt werden. USB-Debugging nur zusätzlich einschalten, falls das Gerät es für seinen ADB-Zugang ausdrücklich verlangt.

### Andere Android-/Google-TVs

Manche Geräte bieten stattdessen „Kabelloses Debugging“ mit Kopplungscode und dynamischen Ports. Das ist ein anderer Verbindungsweg. Mit aktuellen Platform Tools kann ein Computer sich so koppeln:

```text
adb pair TV_IP:KOPPLUNGSPORT
adb connect TV_IP:VERBINDUNGSPORT
```

Den Code bei Aufforderung eingeben. Kopplungsport und Verbindungsport können verschieden sein; beide vom TV ablesen, nicht 5555 raten. Manche Geräte verlangen für diesen Modus tatsächlich WLAN.

**Grenze unseres Prototyps:** Der HA-Leser verwendet derzeit klassischen ADB-TCP mit RSA-Schlüssel. Ein eigener TLS-/Kopplungscode-Dialog ist nicht implementiert. Eine erfolgreiche moderne WLAN-Kopplung des Computers belegt daher noch keine Kompatibilität mit dem HA-Leser. Bietet ein anderer TV ausschließlich diesen Modus, ist eine Erweiterung erforderlich. Ein anderer Port in der YAML allein ersetzt diese Erweiterung nicht.

## 4. Computer verbinden und freigeben

1. Die offiziellen [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) herunterladen und entpacken.
2. TV-IP in den Netzwerkeinstellungen nachsehen. Computer und TV müssen sich lokal erreichen können; keine Internet-Portweiterleitung anlegen.
3. Für den getesteten klassischen TCP-Weg im Terminal ausführen:

```text
adb connect TV_IP:5555
adb devices -l
```

In Windows PowerShell im entpackten Platform-Tools-Ordner gegebenenfalls `adb` durch `./adb.exe` ersetzen. Alle folgenden Beispiele nehmen an, dass `adb` im Terminal gefunden wird.

Am TV erscheint beim ersten eigenen Schlüssel eine Freigabeabfrage mit RSA-Fingerabdruck. Sie kann auch bei Ethernet „USB-Debugging zulassen?“ heißen. Den eigenen Computer zulassen; für einen dauerhaft benötigten Leser die dauerhafte Freigabe auswählen.

Die Abfrage entsteht durch einen Verbindungsversuch. Auf der Einstellungsseite muss vorher nichts aufpoppen. „USB-Debugging-Autorisierungen aufheben“ löscht bestehende Freigaben und ist kein Einrichtungsschritt.

Erfolgskriterium: Der gewünschte Eintrag in `adb devices -l` steht auf **device**.

| Anzeige | Nächster Schritt |
|---|---|
| `unauthorized` | TV-Abfrage bestätigen |
| `offline` | TV/Neustart und Verbindung prüfen, erneut verbinden |
| Kein Eintrag / Verbindung abgelehnt | IP, Port und aktivierten Debugging-Modus prüfen |
| Mehrere Einträge | Den eigenen TV gezielt mit `adb -s TV_IP:PORT ...` auswählen |

## 5. Eingabegerät und Tastensignale lesen

Diese Schritte lesen nur. Sie belegen noch keine Taste neu.

```text
adb -s TV_IP:PORT shell getevent -lp
```

Den Namen der Fernbedienung und ihren aktuellen `/dev/input/eventN`-Pfad suchen. Im geprüften Aufbau hieß sie `Xiaomi RC Consumer Control`. Die Nummer kann sich nach Neustarts ändern; deshalb sucht die HA-Integration nach dem konfigurierten Namen.

Anschließend den gefundenen Pfad einsetzen:

```text
adb -s TV_IP:PORT shell getevent -lt /dev/input/eventN
```

Eine Taste kurz drücken und loslassen. Erwartet werden passende **DOWN**- und **UP**-Zeilen, beim Halten gegebenenfalls Wiederholungen. Für eine Zuordnung die Tasten einzeln mit kurzem Abstand drücken und die physische Taste daneben notieren. Die Aufnahme mit Strg+C beenden. Das Eingabegerät liefert auch andere Tasten; nur die benötigten Signale erfassen.

Beim geprüften Xiaomi war das ohne Root lesbar. Meldet ein anderes Gerät „Permission denied“, sind seine Rohereignisse auf diesem Weg nicht freigegeben. Dann keine allgemeine Kompatibilität zusagen und nicht als normalen Einrichtungsschritt rooten oder den Bootloader entsperren. Eine App-Tastenumleitung kann unabhängig davon trotzdem möglich sein.

Linux-Ereignisname, HID-`MSC_SCAN`, Android-Scan-Code und Android-Keycode sind nicht automatisch dieselbe Zahl. Unsere Messungen und die getesteten Farben stehen in [FARBTASTEN.md](FARBTASTEN.md).

## 6. Erst nach dem Erkennen zuordnen

- Für vorhandene HA-Farbtasten eigene Entity-IDs und Aktionen in `examples/buttons.yaml` einsetzen.
- Für HA-Lautstärke TV-Adresse, Eingabegerätename und Medienplayer in `examples/reader.yaml` konfigurieren.
- In Entwicklungsversion 0.4.0 werden Tasten im HA-Optionsdialog gelernt. Ereignis, HA-Aktionsfolge oder installierte Ziel-App anhand ihres Namens auswählen; Belegungen werden an die gebündelte App 1.6 übertragen. Die Hardwareprüfung dieses neuen Weges steht aus.
- Der bisherige reale Aufbau 0.2.0/1.4 besitzt feste App-Belegungen. Nicht ohne die Schritte aus [MIGRATION.md](MIGRATION.md) aktualisieren.

Danach [INSTALLATION.md](INSTALLATION.md) folgen und jede Funktion einzeln testen.

## 7. Home Assistant besitzt eine eigene Freigabe

Der HA-Leser erzeugt seinen eigenen ADB-Schlüssel. Die Computerfreigabe vom Installieren oder Messen reicht dafür nicht aus. Beim ersten HA-Verbindungsversuch die neue TV-Abfrage für den eigenen HA-Leser bestätigen. Bei bereits gespeicherter Freigabe muss sie nicht bei jedem Start erneut erscheinen.

Im bisherigen YAML-Betrieb lautet die Leser-Meldung `TV volume reader: listening`; UI-Einträge haben einen Statussensor mit Zustand `listening`. Danach echten Tastendruck und tatsächliche Zielreaktion prüfen – eine reine Netzwerkverbindung genügt nicht als Funktionstest.

Wenn nur die APK-Funktionen benötigt werden, ADB nach der Einrichtung ausschalten. Wenn HA die Tasten dauerhaft lesen soll, ADB und seine Autorisierung aktiv lassen. Beim vollständigen Abbau die Rücknahmeschritte der Installationsanleitung verwenden; keine privaten ADB-Schlüssel veröffentlichen.

## Quellen und Prüfgrenze

- [Android: ADB, Autorisierung und Verbindung](https://developer.android.com/tools/adb)
- [Android: Eingabeereignisse mit getevent](https://source.android.com/docs/core/interaction/input/getevent)

Die Xiaomi-/Ethernet-Schritte und Tastenmessungen sind am dokumentierten persönlichen Aufbau geprüft. Andere Hersteller und der moderne WLAN-Pairingweg wurden mit dieser HA-Integration nicht praktisch bestätigt. Stand: 7. November 2026.
