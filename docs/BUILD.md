# APK aus den Quellen lokal bauen

Der aktuelle Build verwendet keine KI, keinen Gradle-Download und keine persönlichen HA-Zugangsdaten. Das Skript ist für Windows/PowerShell ausgelegt und nutzt JDK sowie Android-SDK-Werkzeuge.

## Voraussetzungen

- Vollständiges JDK 21 oder ein kompatibles JDK.
- Android-Plattform 34 mit `android.jar`.
- Android Build Tools 34.0.0 mit aapt, d8, zipalign und apksigner.
- Eigener Signier-Keystore. Private Signierschlüssel bleiben außerhalb von Git.

Die vorhandene APK wurde mit JDK 21 und Android Build Tools 34 gebaut. SDK-Werkzeuge über die offiziellen Android-Entwicklerquellen beziehen: [SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools), [Android SDK](https://developer.android.com/studio).

## Bauen

Den Keystore mit `keytool` einmal selbst erstellen, falls noch keiner vorhanden ist. Passwort interaktiv oder über eine eigene sichere Umgebung übergeben; kein Passwort in Quellcode oder Git speichern.

Das Buildskript erwartet das Keystore-Passwort nur über die Prozess-Umgebungsvariable `TVBRIDGE_KEYSTORE_PASSWORD`. Pfade und Alias anpassen:

```powershell
./scripts/build-apk.ps1 `
  -JdkPath 'C:/Tools/jdk-21' `
  -AndroidJar 'C:/Android/platforms/android-34/android.jar' `
  -BuildToolsPath 'C:/Android/build-tools/34.0.0' `
  -KeyStorePath 'C:/PRIVATE/tvbridge.p12' `
  -KeyAlias 'tvbridge'
```

Das Skript erzeugt pro Lauf ein eigenes Verzeichnis unter `build/`, kompiliert Java, erstellt DEX, richtet die APK aus, signiert sie und prüft anschließend ihre Signatur. Ergebnis: `dist/tv-sonos-remote-bridge-1.7.apk`. Beide Verzeichnisse sind in Git ignoriert. Relative Werkzeugpfade werden vor dem Build absolut aufgelöst.

Für das Komplettpaket die geprüfte APK anschließend als `custom_components/tv_volume_bridge/assets/tvbridge.apk` übernehmen. Nur diese bewusst gebündelte APK ist vom allgemeinen APK-Git-Ausschluss ausgenommen; Quellcode, Lizenz und Buildanleitung werden mitgeliefert. SHA256-Prüfsumme im Paket vermerken. Der Build installiert die App nicht.

## Update und Installation

Eine bereits installierte APK akzeptiert ein Update nur bei passendem Signierschlüssel. Ein eigener fremd signierter Neubau ersetzt die vorhandene App daher nicht automatisch. Öffentliche APK-Updates behalten den bestehenden Projektsignierer; geänderte Neubauten erhöhen versionCode. Signierschlüssel bleiben privat. Unverändert veröffentlichte APK 1.7 enthält den bekannten kosmetischen Anleitungstitel 1.6.

Installation und TV-Freigaben stehen in [INSTALLATION.md](INSTALLATION.md). Private Schlüssel und ein eventuell gesetztes Passwort nach dem Build nicht in Logs oder das Repository übernehmen.


Gestenerkennung ohne Android-Gerät verifizieren: GestureTracker.java und tests/GestureTrackerTest.java mit demselben JDK in ein temporäres Klassenverzeichnis kompilieren (`javac -encoding UTF-8 --release 8 -d <classes> <GestureTracker.java> <GestureTrackerTest.java>`), dann `java -cp <classes> GestureTrackerTest`. Der Test verwendet einen deterministischen Timer statt realer Wartezeiten. Der Android-Handler-Adapter ist eine statische Klasse: die vorhandenen D8-Build-Tools scheiterten hier an einer mit JDK 21 erzeugten anonymen inneren Klasse; die statische Variante wurde erfolgreich gebaut.
