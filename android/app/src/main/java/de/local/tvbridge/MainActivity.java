package de.local.tvbridge;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.provider.Settings;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.ScrollView;

public class MainActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(56, 48, 56, 48);
        TextView info = new TextView(this);
        info.setText("TV-Fernbedienungsbrücke 1.6\n\n1. „Bedienungshilfen öffnen“ wählen.\n2. TV-Fernbedienungsbrücke auswählen, einschalten und Freigabe bestätigen.\n3. Danach mit Zurück wechseln. In Home Assistant: Einstellungen → Geräte & Dienste → TV Sonos Remote Bridge → Zahnrad/Konfigurieren → Taste lernen / Belegung ändern.\n4. Taste drücken, loslassen, bestätigen und Ziel-App oder HA-Aktion auswählen.\n\nDiese Anleitung bleibt hier auch nach dem Aktivieren erreichbar. Die App arbeitet im Hintergrund. Für Lautstärke bleiben TV-ADB und Home Assistant erforderlich.\n\nZum Abschalten: Bedienungshilfen → TV-Fernbedienungsbrücke → Aus. Dadurch enden lokale Tastenumleitungen; HA-Lautstärke separat in HA deaktivieren.\n\nKein Bildschirmzugriff, keine Werbung, keine Cloud.");
        info.setTextSize(22);

        Button settings = new Button(this);
        settings.setText("Bedienungshilfen öffnen");
        settings.setOnClickListener(v -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
        layout.addView(settings);
        layout.addView(info);
        ScrollView scroll = new ScrollView(this);
        scroll.addView(layout);
        setContentView(scroll);
        settings.requestFocus();
    }
}
