package de.local.tvbridge;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import org.json.JSONObject;
import java.util.Iterator;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.util.Base64;
import java.nio.charset.StandardCharsets;

/** ADB shell can configure the helper; ordinary apps lack android.permission.DUMP. */
public class ConfigReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context, Intent intent) {
        setResultCode(0);
        if ("de.local.tvbridge.PROTOCOL".equals(intent.getAction())) {
            setResultCode(2);
            return;
        }
        if ("de.local.tvbridge.LIST_APPS".equals(intent.getAction())) {
            try {
                PackageManager pm = context.getPackageManager();
                JSONObject apps = new JSONObject();
                for (String category : new String[] {Intent.CATEGORY_LEANBACK_LAUNCHER, Intent.CATEGORY_LAUNCHER}) {
                    Intent query = new Intent(Intent.ACTION_MAIN).addCategory(category);
                    for (ResolveInfo app : pm.queryIntentActivities(query, 0)) {
                        if (app.activityInfo == null || !app.activityInfo.enabled || !app.activityInfo.exported
                                || !app.activityInfo.applicationInfo.enabled) continue;
                        String pkg = app.activityInfo.packageName;
                        if (context.getPackageName().equals(pkg)) continue;
                        String label = app.loadLabel(pm).toString();
                        if (label.length() > 200) label = label.substring(0, 200);
                        if (apps.length() < 1000) apps.put(pkg, label.isEmpty() ? pkg : label);
                    }
                }
                byte[] bytes = apps.toString().getBytes(StandardCharsets.UTF_8);
                if (bytes.length > 262144) return;
                setResultData(Base64.encodeToString(bytes, Base64.NO_WRAP));
                setResultCode(1);
            } catch (Exception ignored) { }
            return;
        }
        if (!"de.local.tvbridge.CONFIGURE".equals(intent.getAction())) return;
        String text = intent.getStringExtra("bindings");
        if (text == null || text.length() > 32768) return;
        try {
            JSONObject config = new JSONObject(text);
            if (config.length() > 128) return;
            Iterator<String> keys = config.keys();
            while (keys.hasNext()) {
                String key = keys.next();
                int code = Integer.parseInt(key);
                if (code < 1 || code > 767 || code == 114 || code == 115 || code == 116) return;
                Object value = config.get(key);
                if (value instanceof String) {
                    if (!validTarget((String)value)) return;
                } else if (value instanceof JSONObject && intent.getIntExtra("protocol", 1) == 2) {
                    JSONObject targets = (JSONObject)value;
                    if (targets.length() > 3) return;
                    Iterator<String> presses = targets.keys();
                    while (presses.hasNext()) {
                        String press = presses.next();
                        if (!press.equals("single") && !press.equals("double") && !press.equals("long")) return;
                        Object target = targets.get(press);
                        if (!(target instanceof String) || ((String)target).isEmpty() || !validTarget((String)target)) return;
                    }
                } else return;
            }
            if (context.getSharedPreferences("bridge", Context.MODE_PRIVATE).edit()
                    .putString("bindings", config.toString())
                    .putLong("configuration_revision", android.os.SystemClock.elapsedRealtimeNanos()).commit()) setResultCode(intent.getIntExtra("protocol", 1) == 2 ? 2 : 1);
        } catch (Exception ignored) { }
    }
    private boolean validTarget(String target) {
        return target.isEmpty() || target.matches("[A-Za-z][A-Za-z0-9_]*(\\.[A-Za-z][A-Za-z0-9_]*)+");
    }
}
