package de.local.tvbridge;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.content.Intent;
import android.os.SystemClock;
import android.os.Handler;
import android.os.Looper;
import android.content.SharedPreferences;
import android.view.KeyEvent;
import android.view.accessibility.AccessibilityEvent;
import android.widget.Toast;
import java.io.FileDescriptor;
import java.io.PrintWriter;
import org.json.JSONObject;

public class RemoteService extends AccessibilityService {
    private volatile int lastKeyCode, lastScanCode, launches;
    private long lastErrorAt = -10000;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private static final class HandlerScheduler implements GestureTracker.Scheduler {
        private final Handler handler;
        HandlerScheduler(Handler handler) { this.handler = handler; }
        public void post(Runnable job, long delay) { handler.postDelayed(job, delay); }
        public void cancel(Runnable job) { handler.removeCallbacks(job); }
    }
    private final GestureTracker tracker = new GestureTracker(new HandlerScheduler(handler),
        (code, press) -> fireGesture(code, press));
    private final SharedPreferences.OnSharedPreferenceChangeListener changed = (prefs, key) -> tracker.reset();
    @Override protected void onServiceConnected() {
        AccessibilityServiceInfo info = getServiceInfo();
        info.flags |= AccessibilityServiceInfo.FLAG_REQUEST_FILTER_KEY_EVENTS;
        setServiceInfo(info);
        getSharedPreferences("bridge", MODE_PRIVATE).registerOnSharedPreferenceChangeListener(changed);
    }
    @Override public void onAccessibilityEvent(AccessibilityEvent event) { }
    @Override public void onInterrupt() { tracker.reset(); }
    @Override public void onDestroy() {
        tracker.reset();
        getSharedPreferences("bridge", MODE_PRIVATE).unregisterOnSharedPreferenceChangeListener(changed);
        super.onDestroy();
    }
    private void fireGesture(int code, String press) {
        try {
            JSONObject config = new JSONObject(getSharedPreferences("bridge", MODE_PRIVATE).getString("bindings", "{}"));
            JSONObject targets = config.optJSONObject(Integer.toString(code));
            if (targets != null) launch(targets.optString(press, ""));
        } catch (Exception ignored) { }
    }
    private void launch(String target) {
        if (target.isEmpty()) return;
        Intent intent = getPackageManager().getLeanbackLaunchIntentForPackage(target);
        if (intent == null) intent = getPackageManager().getLaunchIntentForPackage(target);
        if (intent != null) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            try { startActivity(intent); launches++; }
            catch (RuntimeException ignored) { Toast.makeText(this, "App kann nicht geöffnet werden", Toast.LENGTH_SHORT).show(); }
        } else if (SystemClock.elapsedRealtime() - lastErrorAt > 4000) {
            lastErrorAt = SystemClock.elapsedRealtime();
            Toast.makeText(this, "Ziel-App ist nicht installiert: " + target, Toast.LENGTH_SHORT).show();
        }
    }
    @Override protected boolean onKeyEvent(KeyEvent event) {
        lastKeyCode = event.getKeyCode();
        lastScanCode = event.getScanCode();
        String target;
        try {
            String text = getSharedPreferences("bridge", MODE_PRIVATE).getString("bindings", "{}");
            JSONObject config = new JSONObject(text);
            String code = Integer.toString(event.getScanCode());
            if (!config.has(code)) return false;
            JSONObject targets = config.optJSONObject(code);
            if (targets != null) {
                if (event.isCanceled()) tracker.cancel(event.getScanCode());
                else if (event.getAction() == KeyEvent.ACTION_DOWN && event.getRepeatCount() == 0)
                    tracker.down(event.getScanCode(), targets.has("double"), targets.has("long"));
                else if (event.getAction() == KeyEvent.ACTION_UP)
                    tracker.up(event.getScanCode(), targets.has("double"));
                return true;
            }
            target = config.getString(code);
        } catch (Exception ignored) { return false; }
        if (target.isEmpty()) return true;
        if (event.getAction() == KeyEvent.ACTION_DOWN && event.getRepeatCount() == 0) {
            launch(target);
        }
        return true;
    }
    @Override protected void dump(FileDescriptor fd, PrintWriter writer, String[] args) {
        writer.println("TV_BRIDGE lastKeyCode=" + lastKeyCode + " lastScanCode=" + lastScanCode + " launches=" + launches);
    }
}
