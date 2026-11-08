package de.local.tvbridge;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.content.Intent;
import android.os.SystemClock;
import android.view.KeyEvent;
import android.view.accessibility.AccessibilityEvent;
import android.widget.Toast;
import java.io.FileDescriptor;
import java.io.PrintWriter;

public class RemoteService extends AccessibilityService {
    private volatile int lastKeyCode, lastScanCode, launches;
    private long lastErrorAt = -10000;
    @Override protected void onServiceConnected() {
        AccessibilityServiceInfo info = getServiceInfo();
        info.flags |= AccessibilityServiceInfo.FLAG_REQUEST_FILTER_KEY_EVENTS;
        setServiceInfo(info);
    }
    @Override public void onAccessibilityEvent(AccessibilityEvent event) { }
    @Override public void onInterrupt() { }
    @Override protected boolean onKeyEvent(KeyEvent event) {
        lastKeyCode = event.getKeyCode();
        lastScanCode = event.getScanCode();
        // HA reads these from raw input; consume their foreground-app action.
        // Red remains untouched.
        if (event.getKeyCode() == KeyEvent.KEYCODE_PROG_GREEN
                || event.getKeyCode() == KeyEvent.KEYCODE_PROG_YELLOW
                || event.getKeyCode() == KeyEvent.KEYCODE_PROG_BLUE
                || (event.getKeyCode() == 192 && event.getScanCode() == 150)) return true;
        boolean prime = event.getKeyCode() == 194 && event.getScanCode() == 207;
        boolean mapped = event.getScanCode() == 416 || prime;
        String target = prime ? "de.exaring.waipu" : "org.jellyfin.androidtv";
        if (!mapped) return false;
        if (event.getAction() == KeyEvent.ACTION_DOWN && event.getRepeatCount() == 0) {
            Intent intent = getPackageManager().getLeanbackLaunchIntentForPackage(target);
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
                launches++;
            } else if (SystemClock.elapsedRealtime() - lastErrorAt > 4000) {
                lastErrorAt = SystemClock.elapsedRealtime();
                Toast.makeText(this, "Ziel-App ist nicht installiert: " + target, Toast.LENGTH_SHORT).show();
            }
        }
        return true;
    }
    @Override protected void dump(FileDescriptor fd, PrintWriter writer, String[] args) {
        writer.println("TV_BRIDGE lastKeyCode=" + lastKeyCode + " lastScanCode=" + lastScanCode + " launches=" + launches);
    }
}
