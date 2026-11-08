"""Per-key gestures. One owner per key: local TV apps or HA actions/events."""
from __future__ import annotations

import asyncio

PRESSES = ("single", "double", "long")
DOUBLE_SECONDS = 0.35
LONG_SECONDS = 0.75


def gestures(binding):
    """Keep the original flat binding as single press for lossless migration."""
    return {"single": binding, **binding.get("gestures", {})} if binding.get("kind") != "none" else dict(binding.get("gestures", {}))


def validate_owner(binding):
    owners = {"app" if value["kind"] == "app" else "ha"
              for value in gestures(binding).values() if value.get("kind") != "none"}
    if len(owners) > 1:
        raise ValueError("mixed_gesture_targets")
    return next(iter(owners), "ha")


class GestureEngine:
    """Timers use the event loop's monotonic clock; reset never dispatches."""
    def __init__(self, emit):
        self.emit = emit
        self.states = {}
        self.generation = 0

    def reset(self):
        self.generation += 1
        for code in list(self.states):
            self._drop(code)

    def _drop(self, code):
        state = self.states.pop(code, None)
        if state:
            for handle in state["timers"]:
                handle.cancel()

    def feed(self, code, action, enabled):
        loop = asyncio.get_running_loop()
        state = self.states.get(code)
        if action == "DOWN":
            if state and state["down"]:
                return
            second = bool(state and state["waiting"])
            if state:
                self._drop(code)
            state = {"down": True, "waiting": False, "second": second,
                     "fired": False, "timers": [], "enabled": set(enabled)}
            self.states[code] = state
            state["timers"].append(loop.call_later(5, self._expire, code, state))
            if "long" in enabled:
                state["timers"].append(loop.call_later(LONG_SECONDS, self._long, code, state))
            elif not second and "double" not in enabled:
                state["fired"] = True
                self.emit(code, "single")
        elif action == "UP" and state and state["down"]:
            state["down"] = False
            for handle in state["timers"]:
                handle.cancel()
            if state["fired"]:
                self._drop(code)
            elif state["second"]:
                self._drop(code)
                self.emit(code, "double")
            elif "double" in state["enabled"]:
                state["waiting"] = True
                state["timers"].append(loop.call_later(DOUBLE_SECONDS, self._single, code, state))
            else:
                self._drop(code)
                self.emit(code, "single")

    def _expire(self, code, state):
        if self.states.get(code) is state:
            self._drop(code)

    def _long(self, code, state):
        if self.states.get(code) is state and state["down"]:
            state["fired"] = True
            self.emit(code, "long")

    def _single(self, code, state):
        if self.states.get(code) is state:
            self._drop(code)
            self.emit(code, "single")
