package de.local.tvbridge;

import java.util.HashMap;
import java.util.Map;

/** No Android dependency: one recognizer per locally owned key. */
public final class GestureTracker {
    public interface Scheduler {
        void post(Runnable job, long delay);
        void cancel(Runnable job);
    }
    public interface Listener { void fire(int code, String press); }
    public static final long DOUBLE_MS = 350, LONG_MS = 750;
    private final Scheduler scheduler;
    private final Listener listener;
    private final Map<Integer, State> states = new HashMap<>();
    private static final class State {
        boolean down = true, waiting, second, fired;
        Runnable single, hold, expiry;
    }
    public GestureTracker(Scheduler scheduler, Listener listener) {
        this.scheduler = scheduler;
        this.listener = listener;
    }
    public void reset() {
        for (Integer code : states.keySet().toArray(new Integer[0])) cancel(code);
    }
    public void cancel(int code) {
        State state = states.remove(code);
        if (state != null) {
            if (state.single != null) scheduler.cancel(state.single);
            if (state.hold != null) scheduler.cancel(state.hold);
            if (state.expiry != null) scheduler.cancel(state.expiry);
        }
    }
    public void down(int code, boolean hasDouble, boolean hasLong) {
        State old = states.get(code);
        if (old != null && old.down) return;
        boolean second = old != null && old.waiting;
        cancel(code);
        State state = new State();
        state.second = second;
        states.put(code, state);
        state.expiry = () -> { if (states.get(code) == state) cancel(code); };
        scheduler.post(state.expiry, 5000);
        if (hasLong) {
            state.hold = () -> {
                if (states.get(code) == state && state.down) {
                    state.fired = true;
                    listener.fire(code, "long");
                }
            };
            scheduler.post(state.hold, LONG_MS);
        } else if (!hasDouble && !second) {
            state.fired = true;
            listener.fire(code, "single");
        }
    }
    public void up(int code, boolean hasDouble) {
        State state = states.get(code);
        if (state == null || !state.down) return;
        state.down = false;
        if (state.hold != null) scheduler.cancel(state.hold);
        if (state.fired) {
            cancel(code);
        } else if (state.second) {
            cancel(code);
            listener.fire(code, "double");
        } else if (hasDouble) {
            state.waiting = true;
            state.single = () -> {
                if (states.get(code) == state) {
                    cancel(code);
                    listener.fire(code, "single");
                }
            };
            scheduler.post(state.single, DOUBLE_MS);
        } else {
            cancel(code);
            listener.fire(code, "single");
        }
    }
}
