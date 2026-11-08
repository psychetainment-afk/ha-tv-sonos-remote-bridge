import de.local.tvbridge.GestureTracker;
import java.util.*;

/** Deterministic behavioral tests, no Android device or Android stubs. */
public class GestureTrackerTest {
    static class Clock implements GestureTracker.Scheduler {
        long now;
        Map<Runnable, Long> jobs = new LinkedHashMap<>();
        public void post(Runnable job, long delay) { jobs.put(job, now + delay); }
        public void cancel(Runnable job) { jobs.remove(job); }
        void advance(long delay) {
            long end = now + delay;
            while (true) {
                Runnable next = null;
                long at = Long.MAX_VALUE;
                for (Map.Entry<Runnable, Long> job : jobs.entrySet()) {
                    if (job.getValue() <= end && job.getValue() < at) {
                        next = job.getKey(); at = job.getValue();
                    }
                }
                if (next == null) break;
                now = at; jobs.remove(next); next.run();
            }
            now = end;
        }
    }
    static void check(boolean ok, String message) {
        if (!ok) throw new AssertionError(message);
    }
    public static void main(String[] args) {
        int count = 0;
        for (String scenario : new String[] {"single", "double", "long", "secondLong", "reset", "cancel", "independent", "immediate", "shortLong", "missingUp"}) {
            Clock clock = new Clock();
            List<String> calls = new ArrayList<>();
            GestureTracker tracker = new GestureTracker(clock, (code, press) -> calls.add(code + ":" + press));
            boolean doubled = !scenario.equals("immediate") && !scenario.equals("shortLong");
            tracker.down(1, doubled, !scenario.equals("immediate"));
            tracker.down(1, doubled, !scenario.equals("immediate"));
            if (scenario.equals("immediate")) check(calls.size() == 1, "single must be immediate");
            if (scenario.equals("long") || scenario.equals("missingUp")) clock.advance(750);
            if (!scenario.equals("missingUp")) tracker.up(1, doubled);
            if (scenario.equals("double") || scenario.equals("secondLong")) {
                clock.advance(349);
                check(calls.isEmpty(), "single must wait");
                tracker.down(1, true, true);
                if (scenario.equals("secondLong")) clock.advance(750);
                tracker.up(1, true);
            }
            if (scenario.equals("independent")) {
                tracker.down(2, true, true); tracker.up(2, true);
            }
            if (scenario.equals("reset")) tracker.reset();
            if (scenario.equals("cancel")) tracker.cancel(1);
            clock.advance(6000);
            String expected;
            if (scenario.equals("reset") || scenario.equals("cancel")) expected = "[]";
            else if (scenario.equals("double")) expected = "[1:double]";
            else if (scenario.equals("long") || scenario.equals("secondLong") || scenario.equals("missingUp")) expected = "[1:long]";
            else if (scenario.equals("independent")) expected = "[1:single, 2:single]";
            else expected = "[1:single]";
            check(calls.toString().equals(expected), scenario + " got " + calls);
            check(clock.jobs.isEmpty(), "timers leaked: " + scenario);
            count++;
        }
        System.out.println(count + " Android gesture behavior checks passed");
    }
}
