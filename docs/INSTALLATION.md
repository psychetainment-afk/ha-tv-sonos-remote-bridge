# Installation

[English](#english) | [Deutsch](#deutsch)

## English

Local patch **0.5.1** / TV app **1.7.1 (versionCode 9)**, installed on the personal test setup, no new tagged release. Public prerelease remains 0.5.0 / 1.7. Read the [hardware evidence and open tests](PRUEFUNG.md) first. For an existing installation, follow [migration and rollback](MIGRATION.md); never run two readers against the same remote.

### 1. Prepare the TV

1. Open TV Settings → System/Device preferences → About. Select the Android TV OS build seven times to enable developer options; exact names vary.
2. Enable classic network ADB. On the tested Xiaomi this is “Mi TV ADB Debugging”; restart the TV if prompted. No OEM unlocking or factory reset is required.
3. Make the TV reachable from HA on the trusted local network. Typical classic ADB port: 5555. USB debugging alone does not establish network access. Pairing-code/TLS wireless debugging is not supported.
4. Note the TV IP from its network settings. Do not expose the ADB port to the Internet.

### 2. Install the HA integration

In HACS, add `https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge` as a **custom repository → Integration**. Download it and restart HA. For a prerelease, enable beta/prerelease versions where available. Inclusion in the default HACS catalogue is a separate process.

Manual alternative: copy the complete `custom_components/tv_volume_bridge` folder, including assets/tvbridge.apk, translations and brand, into `/config/custom_components/`, then restart HA. The release integration ZIP contains a top-level tv_volume_bridge folder suitable for extraction into that directory. Keep private backups outside the public project.

### 3. Connect and discover the remote

Open **Settings → Devices & services → Add integration → TV Sonos Remote Bridge**.

1. Enter TV IP, classic ADB port and the existing Sonos/media-player volume target.
2. At the TV authorization prompt, choose **Always allow from this computer** and **Allow**. It may say “USB debugging” even over Ethernet. HA uses its own key; an already authorized laptop does not replace HA authorization. Do not reset existing authorizations unnecessarily.
3. Start remote discovery, briefly press **volume down once**, and release it within the 20-second capture period. HA actions are suppressed during capture; the TV itself can react.
4. Confirm the detected input. On timeout/ambiguity, retry or select it manually. Other buttons can belong to a different input; automatic multi-input support is not implemented.
5. Complete the setup. New entries start with empty assignments; existing entries retain theirs. Volume is reserved and independent of learned mappings.

Options remain available at **Settings → Devices & services → TV Sonos Remote Bridge → Configure**, or the device's configuration link. Help is always available. “Connected – waiting for buttons” (raw state listening) means the reader is active; it does not blink for every key.

### 4. Install and enable the companion TV app

In the options dialog choose TV-app setup / transfer assignments. Explicitly select installation/update of the bundled APK. The local patch installs APK 1.7.1 and opens its help screen, whose version comes from the package metadata. On the TV enable **Accessibility → TV remote bridge**, approve the request, return to HA, and finish the confirmation step.

Without installation selected, the dialog only transfers mappings. Transfers replace TV-app mappings. A signer conflict aborts; the integration never automatically uninstalls. A downgrade is not guaranteed. Local app targets require the accessibility service; volume can work with the HA reader without the TV app.

### 5. Learn and assign buttons

Choose learn/change button, press and release the desired button within 60 seconds, confirm, then select single/double/long press. Assign a launchable installed TV app, an HA action sequence or an HA event. Repeat learning for another gesture on the same button. Only the selected gesture changes; removing that gesture preserves others, while removing the whole mapping clears all gestures.

Each button uses **either local app targets or HA actions/events**. To change ownership, remove the entire button mapping first. Different buttons can have different owners. Power and volume are reserved. Existing colour-event automations must not duplicate actions added in the editor.

Double press: second press within 350 ms after release. Long press: 750 ms, once. A long second press wins over double. Single actions may wait when double/long targets exist. Volume holding is separate. Test with harmless targets first; stop on duplicate original actions. Learning suppresses HA actions, but existing TV-app or original actions can still occur.

### Operation and recovery

Local app targets work on the TV after configuration without HA. Volume and HA actions need HA, the network and TV ADB. Disable the TV accessibility service to stop local remaps; disable the HA integration to stop its volume/actions. Use the Sonos app as a fallback. Do not spontaneously uninstall or assume APK downgrade works. See [migration](MIGRATION.md) and [remaining hardware tests](HARDWARETEST.md).

## Deutsch


# Einrichtung in Home Assistant

Lokaler Patch **0.5.1 / TV-App 1.7.1**, am eigenen Testaufbau installiert, ohne neuen getaggten Release; öffentlicher Vorabrelease weiterhin **0.5.0 / 1.7**. Teilweise hardwaregeprüft; genaue Belege und offene Prüfungen unter [Prüfstand](PRUEFUNG.md). Für einen bestehenden Aufbau zuerst [Migration](MIGRATION.md) beachten: gezielter Rückweg, alten Leser stoppen, niemals zwei Leser gleichzeitig.

## Wofür ist die Brücke da?

Im ursprünglichen Aufbau waren zwei Fernbedienungen nötig: Bluetooth für den Fernseher und eine zweite Infrarot-Fernbedienung nur für Lauter/Leiser der optisch angeschlossenen Sonos-Playbar. Die Integration nutzt dafür die Lautstärketasten der TV-Fernbedienung. Weitere Tasten können installierte TV-Apps oder Home-Assistant-Aktionen auslösen.

Praktisch getestet wurde Xiaomi MiTV-MOEU0 / Android TV 14 mit Xiaomi RC Consumer Control und Sonos-Playbar. Andere Android-/Google-TVs sind nicht bestätigt. LG/webOS und Samsung/Tizen werden nicht unterstützt. Neue Versionen sind nicht allein durch diese Geräteangabe hardwaregeprüft.

## 1. TV vorbereiten

1. TV einschalten. Einstellungen → System/Geräteeinstellungen → Info/Über öffnen.
2. „Build“ bzw. „Android-TV-Betriebssystem-Build“ auswählen und **siebenmal OK** drücken, bis die Entwicklerfreigabe bestätigt wird. Menünamen variieren.
3. Entwickleroptionen öffnen. Beim getesteten Xiaomi **Mi TV ADB Debugging** aktivieren und einen angeforderten TV-Neustart abwarten. Keine OEM-Entsperrung oder Rücksetzung nötig.
4. TV und HA müssen im Heimnetz erreichbar sein. Klassisches Netzwerk-ADB kann über LAN oder WLAN laufen; beim Xiaomi funktioniert LAN auf Port 5555. USB-Debugging allein bedeutet nicht, dass Netzwerk-ADB verfügbar ist.
5. TV-IP unter den Netzwerkeinstellungen nachsehen. Falls nur „Kabelloses Debugging“ mit **Kopplungscode/TLS** angeboten wird: Dieser Modus wird aktuell nicht unterstützt. Kein Kopplungsport in das klassische Formular übertragen.

Erklärung und optionale manuelle Diagnose: [Einstieg](EINSTIEG.md). Ein Installationscomputer ist für die Browser-Einrichtung nicht erforderlich.

## 2. Integration installieren

**Manuelle Installation:** Vollständigen Ordner `custom_components/tv_volume_bridge` einschließlich `assets/tvbridge.apk`, Übersetzungen und Branddateien nach `/config/custom_components/` kopieren und HA neu starten. Bei bestehender Installation ausschließlich nach dem gesicherten [Migrationsplan](MIGRATION.md) austauschen. Ein zusätzliches Test-HA darf nicht parallel den gleichen TV lesen.

**Über HACS:** `https://github.com/psychetainment-afk/ha-tv-sonos-remote-bridge` als benutzerdefiniertes Repository vom Typ Integration hinzufügen, herunterladen und HA neu starten. Ein lokaler Windows-Pfad lässt sich nicht als HACS-Repository verwenden. Aufnahme in den allgemeinen Katalog ist ein separater Schritt.

## 3. Verbinden und Fernbedienung erkennen

**Einstellungen → Geräte & Dienste → Integration hinzufügen → TV Sonos Remote Bridge.**

1. TV-IP, klassischen ADB-Port (gewöhnlich 5555) und vorhandenen Sonos-/Medienplayer als Lautstärkeziel wählen.
2. Beim Verbindungsversuch am TV **„Von diesem Computer immer zulassen“** und **„Zulassen“** bestätigen. Auch über Ethernet kann die Abfrage „USB-Debugging zulassen?“ heißen. Sie erscheint erst beim Verbindungsversuch. Bereits vorhandene Freigaben nicht zurücksetzen. HA verwendet einen eigenen Schlüssel; die Computerfreigabe ersetzt ihn nicht.
3. „Per Tastendruck erkennen“ aktiv lassen und weitergehen. Auf der nächsten Seite starten; dann innerhalb von 20 Sekunden **einmal kurz Leiser drücken und loslassen**. Der Test führt keine HA-Aktion aus; der TV selbst kann reagieren.
4. Den erkannten Eingang bestätigen. Bei Timeout oder mehreren Eingängen manuell wählen oder die Erkennung wiederholen. Die Liste enthält auch virtuelle/interne TV-Eingänge. Namen allein belegen keine Kompatibilität. Bei diesem Xiaomi ist der Lautstärkeeingang `Xiaomi RC Consumer Control`.
5. Den Abschluss mit den nächsten Schritten lesen und bestätigen. Neue Einträge beginnen mit **leeren Tastenbelegungen**; vorhandene Einträge behalten ihre Konfiguration. Lautstärke ist unabhängig davon fest reserviert.

Leiser erkennt den Lautstärkeeingang; andere Tasten können auf anderen Eingängen liegen. Diese Mehrgeräte-Unterstützung ist nicht automatisch gelöst. „Fernbedienung erneut erkennen“ steht später im Konfigurationsmenü zur Verfügung und pausiert den bisherigen Leser exklusiv für die Erfassung.

## 4. Wo ist die Einrichtung später?

**Einstellungen → Geräte & Dienste → TV Sonos Remote Bridge → Zahnrad/Konfigurieren.** Auf der Geräteseite gibt es zusätzlich **„Konfiguration besuchen“** als direkten Weg zum Integrationseintrag. „Hinzufügen zu …“ erstellt andere HA-Verknüpfungen und öffnet nicht die Fernbedienungseinrichtung.

Im Menü bleibt **„Anleitung und getestete Geräte“** jederzeit verfügbar. Der Status **„Verbunden – wartet auf Tasten“** (Rohwert `listening`) bedeutet, dass der Leser aktiv ist. Er blinkt nicht bei jedem Tastendruck. Lautstärke kann jetzt schon ohne TV-App funktionieren: kurz drücken, halten, loslassen und tatsächliche Sonos-Reaktion prüfen. Bei weiterlaufender Lautstärke Integration deaktivieren und Sonos-App verwenden.

## 5. TV-App einrichten

1. **TV-App einrichten / Belegungen übertragen** öffnen.
2. **Mitgelieferte TV-App installieren/aktualisieren** bewusst aktivieren. Dies schreibt beim lokalen Patch APK 1.7.1 auf den TV und öffnet die App. Ohne Häkchen werden nur Belegungen übertragen.
3. Am TV **Bedienungshilfen öffnen → TV-Fernbedienungsbrücke → Ein** wählen und die Freigabe bestätigen. Je nach TV liegen Bedienungshilfen unter System oder Geräteeinstellungen.
4. Mit Zurück die TV-App verlassen und in HA den Bestätigungsschritt abschließen. Die App arbeitet im Hintergrund. Ihre Anleitung bleibt beim erneuten Öffnen verfügbar, auch nach Aktivierung des Dienstes.

Installation und reine Übertragung ersetzen die bisherigen TV-App-Belegungen. Erst nach bestätigter Übertragung speichert HA eine neue Belegung. Bei Signaturkonflikten erfolgt keine automatische Deinstallation. Ein APK-Downgrade ist nicht garantiert. App 1.6 ist für die App-Auswahlliste erforderlich; die Integration meldet eine nicht verfügbare Liste verständlich. Ohne App-Liste bleiben HA-Aktionen und die optionale Experteneingabe einer Paketkennung möglich.

## 6. Eine Taste einrichten oder ändern

1. **Taste lernen / Belegung ändern** öffnen.
2. Innerhalb von 60 Sekunden die gewünschte Taste einmal drücken und loslassen, dann bestätigen. Die numerische Erkennung ist automatisch; kein Code muss nachgeschlagen werden. HA-Aktionen sind während des Lernens unterdrückt; bestehende TV-App-/Originalaktionen können trotzdem starten.
3. Druckart auswählen, dann Funktion und Weiter:
   - **HA-Aktion direkt ausführen:** Befehl auswählen (z. B. Licht umschalten oder Szene aktivieren), danach passende Ziel-Entitäten und Bezeichnung. Für Helligkeit, mehrere Befehle, Geräte oder Bereiche die erweiterte Aktionsfolge wählen.
   - **TV-App öffnen:** anschließend nur Ziel-App und Bezeichnung.
   - **HA-Ereignis für eigene Automation:** anschließend nur Bezeichnung; meldet `tv_volume_bridge_button`, schaltet selbst nichts. Eine eigene Ereignis-Automation übernimmt die Wirkung. Auch direkte Aktionen senden dieses Ereignis: keine doppelte Wirkung konfigurieren.
4. Speichern, dann reale Wirkung einmal prüfen. Bei App-Zielen muss die gewünschte App öffnen, ohne zusätzliche Originalaktion. Bei Doppelaktion Belegung entfernen.

**Belegung entfernen** gibt eine Taste wieder frei. Lautstärke und Power sind reserviert. Vorhandene Farbtasten-Automationen bleiben bei Migration erhalten; dieselbe Aktion nicht zusätzlich im neuen Editor anlegen. Bewegung von Rollläden nur unter Sichtkontrolle testen; bestehende 50-%-Grenze erhalten.

## Betrieb und Abschalten

Lokale App-Ziele benötigen nach Konfiguration nur TV-App und Bedienungshilfe. Lautstärke/HA-Aktionen benötigen TV-ADB, Netzwerk und HA. Es gibt keine nachgeholten Befehle nach Verbindungsverlust. Ein regulärer Neustart soll Bedienungshilfe und Leser wiederherstellen; das ist je Geräte-/Versionskombination praktisch zu prüfen.

**Nur TV-Tastenumleitungen aus:** Am TV Bedienungshilfen → TV-Fernbedienungsbrücke → Aus. **Auch HA-Lautstärke aus:** zusätzlich die HA-Integration deaktivieren. Keine Deinstallation als spontane Fehlerbehebung; Rückweg nach [Migration](MIGRATION.md), Prüfplan unter [Hardwaretest](HARDWARETEST.md).

Quellen für allgemeine Schritte: [Android-Entwickleroptionen](https://developer.android.com/studio/debug/dev-options), [HACS Custom Repositories](https://www.hacs.xyz/docs/faq/custom_repositories/). Gerätespezifischer Xiaomi-Weg: eigene frühere Messungen, siehe [Einstieg](EINSTIEG.md).


## Mehrfachdruck ab 0.5.0 / App 1.7

Vor Mehrfachbelegungen die gebündelte TV-App 1.7 über den vorhandenen Installationsweg aktualisieren und Bedienungshilfe prüfen. Alte Apps werden bei der Übertragung vor Änderungen erkannt. Im HA-Optionsmenü „Taste lernen / Belegung ändern“: Taste drücken und loslassen, bestätigen, Einzel-/Doppel-/Langdruck auswählen, Ziel speichern. Für weitere Druckarten dieselbe Taste erneut lernen. Nur die gewählte Druckart wird ersetzt; „Diese Druckart entfernen“ erhält andere Druckarten, „Belegung entfernen“ löscht die ganze Taste.

Pro Taste entweder TV-App-Ziele oder HA-Aktionen/Ereignisse verwenden. Zum Wechsel zwischen App und HA zunächst die ganze Taste entfernen. Für Doppel-/Langdruck unterschiedliche Ziele zuweisen und am TV testen. Zweiter kurzer Druck innerhalb von 350 ms nach Loslassen ergibt Doppel; 750 ms halten ergibt einmal Lang. Einzeldruck wartet bei aktivierter Doppel-/Langbelegung auf die Entscheidung. Ein lang gehaltener zweiter Druck ergibt Lang statt Doppel. Lautstärke-Halten bleibt unabhängig. Konkrete Firmwaregrenzen und offene Hardwareprüfung unter ARCHITECTURE.md und PRUEFUNG.md.

## Lautstärke im lokalen Patch 0.5.1 / Volume in local patch 0.5.1

Unter „Verbindung und Lautstärkeziel“ Schrittweite **1** für einen Prozentpunkt wählen; **0** erhält den bisherigen Gerätestandard (Sonos zwei Punkte), **2–10** erlauben größere Schritte. Voreinstellung ist jetzt **1**, auch bei bestehenden Einträgen ohne explizite Option; 0 bleibt optionaler Gerätestandard. Ein Geräteziel mit `volume_set` und aktuellem `volume_level` ist erforderlich; bei fehlender Rückmeldung wird nicht auf gröbere Schritte ausgewichen. Sonos kann nur ganze Stufen 0–100, somit keine Zwischenstufe unter 1.

The TV bar is independent of the selected HA volume target. Use its HA media-player volume or connection sensor attributes for reported volume and mute. Detailed causes, exact event payload, logging recipe and test limits: [Review](REVIEW-2026-11-09.md).
