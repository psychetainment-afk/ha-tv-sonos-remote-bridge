package de.local.tvbridge;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.provider.Settings;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(56, 48, 56, 48);
        TextView info = new TextView(this);
        info.setText("TV-Fernbedienungsbrücke\n\nNetflix → Jellyfin\nPrime Video → waipu.tv\nXiaomi TV+ → Kino über Home Assistant\nGrün / Gelb / Blau → konfigurierte Home-Assistant-Aktionen\nRot bleibt frei\n\nLautstärke und Farbtasten verarbeitet der lokale Home-Assistant-Tastenleser.\n\nKein Bildschirmzugriff, keine Werbung, keine Cloud.\n\nZum Abschalten der App-Tastenumleitung den Bedienungshilfedienst deaktivieren oder diese App deinstallieren.");
        info.setTextSize(22);
        layout.addView(info);
        Button settings = new Button(this);
        settings.setText("Bedienungshilfen öffnen");
        settings.setOnClickListener(v -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
        layout.addView(settings);
        setContentView(layout);
    }
}
