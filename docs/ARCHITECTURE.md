# Architektur und Betriebsgrenzen

## Warum TV-App und HA-Leser?

Auf dem geprüften Xiaomi erreichen App-Tasten die Android-Bedienungshilfe, Lautstärketasten dagegen nur die Rohereigniserfassung. Die optisch angeschlossene Sonos Playbar erhält Audio ohne Steuerkanal für die Bluetooth-Fernbedienung. HA liest deshalb die Rohereignisse und ruft die vorhandene Medienplayer-Integration auf. Die TV-App öffnet Ziel-Apps und konsumiert zugeordnete Tasten, soweit Android dies zulässt.

## Laufzeit 0.5.0

### Warum keine reine Tastenmapper- oder Pegelsynchronisations-App?

Die Architektur folgt dem Verhalten der geprüften Xiaomi-Firmware, nicht einer allgemeinen Einschränkung aller Android-TVs. Ein gewöhnlicher Tastenmapper empfängt Android-KeyEvents über eine Bedienungshilfe. Unser Dienst verwendet denselben Mechanismus für App-Tasten; für die hier nicht zugestellten Lautstärketasten liest HA stattdessen die Linux-Rohereignisse über ADB und steuert das Lautstärkeziel mit der vorhandenen HA-Integration. Die TV-App benötigt dadurch weder Netzwerkberechtigung noch HA-Token. Der Preis dafür ist die dauerhafte Abhängigkeit von ADB, HA und Netzwerk; ADB gewährt grundsätzlich Shell-Rechte.

Am 8. November 2026 lesend am bestehenden Aufbau nachgeprüft: Android meldete STREAM_MUSIC auf spdif mit 100/100. Nach vom Nutzer bestätigten gemischten Lauter-/Leiser-/Halteversuchen und anschließend separat dreimal ausschließlich Leiser blieb dieser Wert bei 100/100. Die Diagnose unseres laufenden Bedienungshilfediensts blieb beim Vergleich unverändert bei lastKeyCode=192, lastScanCode=150, launches=1. Die Lautstärketasten wurden damit nicht als letzter KeyEvent dieses Diensts sichtbar. Das stützt den bisherigen Befund; es ersetzt keinen vollständigen Ereignismitschnitt. Keine Einstellungen, APK oder HA-Konfiguration für diese Prüfung geändert.

Eine Synchronisation ausschließlich anhand dieses beobachteten Android-Pegels hätte in dieser Konfiguration keinen geänderten Zielwert erhalten. Daraus folgt weder allgemeine Unveränderlichkeit des TV-Pegels noch nachgewiesene Inkompatibilität einer anderen App: alternative Einrichtung, Firmware oder Audioausgänge wurden nicht geprüft. mUseFixedVolume=false wurde ebenfalls gemeldet; der einzelne Pegelwert ist deshalb kein Beweis für global fest eingestellte Lautstärke.

Vergleich: [QuickBars](https://github.com/Trooped/QuickBars) erfasst im [QuickBarService](https://github.com/Trooped/QuickBars/blob/main/app/src/main/java/dev/trooped/tvquickbars/services/QuickBarService.kt) KeyEvents über die Bedienungshilfe und sendet über seinen [HomeAssistantClient](https://github.com/Trooped/QuickBars/blob/main/app/src/main/java/dev/trooped/tvquickbars/ha/HomeAssistantClient.kt) authentifizierte WebSocket-Serviceaufrufe. Das ist für dort ankommende Tasten ein direkterer Weg; seine Eignung für diese Xiaomi-Lautstärketasten ist nicht bestätigt. [VolumeLink](https://play.google.com/store/apps/details?id=dev.hodges.volumelink) beschreibt TV-/Sonos-Pegelsynchronisation; interne Erfassung, Protokoll und mögliche zusätzliche Einrichtung wurden nicht geprüft. Kein Anspruch auf technische Überlegenheit oder Alleinstellung.

Prüfgrenzen und Fortsetzung: [Prüfung](PRUEFUNG.md#architecture-observation).

Config flow verbindet mit klassischem ADB-TCP/RSA und ermittelt Eingabegerätenamen. Jeder UI-Eintrag besitzt genau eine Runtime mit einem VolumeReader. Der Pfad /dev/input/eventN wird bei jeder Verbindung neu anhand des Namens bestimmt. Ein active YAML reader blockiert UI-Einträge, damit die bisherige Konfiguration nicht parallel bedient wird.

Der Leser verwendet getevent -lp sowie numerisches getevent -t. Er verarbeitet DOWN/UP/REPEAT, entprellt normale Belegungen und wiederholt Lautstärke ab 450 ms im Abstand von 220 ms, höchstens fünf Sekunden. Verbindungsausfälle führen zum Schließen und Neuverbinden; keine Wiedergabe alter Befehle.

Der Optionsdialog erfasst innerhalb von 60 Sekunden einen Code. Währenddessen unterdrückt die Runtime HA-Aktionen; lokale Android-Aktionen bleiben davon unabhängig. Volume/Power sind reserviert. Tasten können HA-Ereignisse auslösen, lokal gespeicherte HA-Aktionsfolgen ausführen oder eine Android-App öffnen. Skripte laufen getrennt vom Eingabestrom, jeweils im Modus single. Konfigurationsdaten bleiben JSON; HA-Templates werden erst beim Laufzeitaufbau kompiliert.

Für Installation und Konfiguration stoppt eine exklusive Wartungssperre den Leser, verwendet genau eine Verwaltungsverbindung und startet ihn anschließend neu. Entladen setzt vor dem Warten ein Stoppsignal; eine gleichzeitig laufende Wartung darf keinen verwaisten Leser neu starten. Änderungen werden nach Bestätigung des TV-Konfigurationsempfängers in HA gespeichert. Ein Verbindungsverlust genau nach dem Schreiben kann trotzdem eine erneute Übertragung erfordern; es gibt keine verteilte Transaktion zwischen Android und HA.

## TV-App 1.7

Paket de.local.tvbridge. Keine INTERNET-Berechtigung, kein Fensterinhaltszugriff. Zuordnungen von Linux-/Android-Scan-Code zu Paketkennung liegen in privaten SharedPreferences; ein leerer Zielwert konsumiert die Taste zugunsten der HA-Aktion. Nicht zugeordnete Tasten werden weitergereicht. Frische App- und HA-Installationen beginnen ohne Beispielbelegungen; gespeicherte SharedPreferences/Eintragsdaten bleiben bei Updates erhalten.

Der explizite Broadcast-Empfänger ConfigReceiver verlangt android.permission.DUMP, die der autorisierte ADB-Shell-Client besitzt. Normale Apps besitzen diese Berechtigung nicht. Er prüft Codes, Paketkennungen und Größenlimits und bestätigt erst nach dauerhaftem Speichern. Lautstärke/Power werden nicht über diesen Empfänger umbelegt. Ein Rohsignal garantiert nicht, dass der Bedienungshilfedienst die jeweilige Taste erhält.

HA kann die gebündelte signierte APK nach ausdrücklicher Auswahl installieren und ihre Startseite öffnen. Bei Signaturkonflikt keine automatische Deinstallation. Bedienungshilfe und ADB-Freigabe bleiben bewusste Bestätigungen am TV.

## Schlüssel, Status und Rückweg

HA verwendet einen eigenen RSA-Schlüssel unter .storage/tv_volume_bridge/. Verzeichnis 0700, Schlüssel 0600 auf dem geprüften Linux-HA. Moderne WLAN-TLS-Kopplung ist nicht implementiert. Die ADB-Autorisierung erlaubt grundsätzlich Shell-Zugang: Nur im Normalbetrieb ist der Leser rein lesend; ausdrückliche App-Verwaltung schreibt APK und Belegungen auf den TV.

Der Statussensor zeigt den Leserzustand und letzten Code; Diagnosen enthalten nur Version, Transport, Zustand, Anzahl der Belegungen und Fehlertyp. Keine Schlüssel, Adresse oder Aktionsdaten werden ausgegeben. Private Schlüssel und Signiermaterial gehören nicht ins Repository.

Für lokale App-Ziele reicht nach Einrichtung die TV-Bedienungshilfe. Lautstärke und HA-Aktionen benötigen ADB, Netzwerk, HA und Zielintegration. Kein zusätzlicher Container oder dauerhafter Installationscomputer.

Bedienungshilfe abschalten gibt App-Tasten frei; HA-Eintrag entfernen stoppt den Leser, deinstalliert aber keine App. Bestehender YAML-Weg bleibt als Kompatibilitätspfad erhalten. Konkrete Grenzen, Migrationsschutz und Rücknahme stehen in [MIGRATION.md](MIGRATION.md). Entwicklung und laufender Aufbau sind bewusst getrennt.


## Erkennung und App-Auswahl

Ein zeitlich begrenzter numerischer getevent-Stream ordnet Leiser (114/DOWN) einem zuvor inventarisierten event-Pfad zu. Mehrere Treffer führen zur manuellen Bestätigung; ein Treffer ist kein vollständiger Kompatibilitätsnachweis. Setup-Erkennungen werden je Host serialisiert und bei aktivem Eintrag blockiert. Options-Erkennung verwendet die exklusive Runtime-Wartung, stoppt vorher Lernmodus und normalen Leser und startet diesen auch bei Abbruch wieder. Keine HA-Aktionen im Erkennungsstream.

App 1.6 beantwortet LIST_APPS über denselben DUMP-geschützten expliziten Empfänger. PackageManager liefert aktivierte startbare Leanback-/Launcher-Apps und lesbare Namen, nach Paket dedupliziert. JSON wird als Base64 im Broadcast-Ergebnis zurückgegeben; HA validiert Paketkennungen und Größenlimits und bietet eine sortierte Auswahl. Kein Netzwerkzugriff der App und keine manuell zusammengesetzten Benutzer-Shellbefehle. Einträge mit App 1.5 können weiterhin konfiguriert werden, liefern aber noch keine App-Liste.


## Gestenerkennung ab 0.5.0 / TV-App 1.7

Das flache Belegungsobjekt bleibt Einzeldruck; optionale `gestures.double` und `gestures.long` enthalten eigene Ziele. `kind: none` entfernt nur die betreffende Druckart. Pro Taste sind ausschließlich App-Ziele oder HA-Aktionen/Ereignisse erlaubt; App/HA-Mischungen werden vor Übertragung abgewiesen. HA-Event und HA-Aktion dürfen auf derselben Taste kombiniert werden. Damit entscheidet genau eine Instanz pro Taste über die Geste: TV-App für App-Ziele, HA für Hausaktionen. Unterschiedliche Tasten dürfen unterschiedliche Besitzer haben. Diese bewusste Grenze vermeidet widersprüchliche Entscheidungen zwischen Android-KeyEvents und verzögert eintreffenden Linux-Rohereignissen. Lokale App-Ziele bleiben ohne HA nutzbar; die TV-App bleibt ohne Netzwerkberechtigung und HA-Token.

Beide Implementierungen verwenden monotone Timer, Zustände pro Taste und 350 ms Doppeldruckfenster nach dem ersten Loslassen sowie 750 ms Langdruck. Bei Doppelbelegung wartet Einzel bis zum Fensterende; bei Langbelegung bis zur Entscheidung (kurzer Druck beim Loslassen). Ein zweiter kurzer Druck löst Doppel erst beim Loslassen aus. Wird der zweite Druck lang gehalten, gewinnt Lang und verbraucht die gesamte Geste. Eine abgefeuerte Langaktion wird beim Loslassen nicht erneut ausgelöst. Wiederholte DOWN-/REPEAT-Signale lösen keine zusätzliche Aktion aus. Nach fünf Sekunden wird ein unvollständiger Zustand ohne weitere Aktion verworfen. Fenstergrenzen müssen noch am echten TV erprobt werden.

HA verwirft offene Gesten bei Lernmodus, Verbindungsausfall, Wartung, Reload und Unload. Android verwirft lokale Gesten bei Konfigurationsübertragung (auch bei gleichem Inhalt), unterbrochener Bedienungshilfe und Service-Ende sowie abgebrochenem KeyEvent. Ein HA-Ausfall stoppt absichtlich keine lokalen App-Ziele. Volume/Power bleiben von frei belegbaren Gesten ausgeschlossen; der bisherige Lautstärkeleser bleibt unverändert. HA-Ereignisse enthalten zusätzlich `press` mit `single`, `double` oder `long`; vorhandene Felder bleiben erhalten. App-Ziele erzeugen keine zusätzlichen HA-Tastenaktionen.

Bei Mehrfachbelegungen prüft HA zuerst die Protokollfähigkeit der TV-App per DUMP-geschütztem PROTOCOL-Broadcast. Erst nach Antwort 2 werden neue Belegungen mit Protokoll 2 übertragen und bestätigt. Alte APKs werden vor einer Konfigurationsänderung abgewiesen. Ohne Mehrfachbelegungen bleibt das alte String-Payloadformat erhalten. Bestehende gespeicherte Belegungen werden nicht automatisch verändert. Keine fremden Quelltexte übernommen.
