"""One owned reader per config entry, including bounded exclusive maintenance."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.script import Script
from homeassistant.helpers import config_validation as cv

from .adb import connection, list_apps
from .const import DOMAIN, EVENT_BUTTON
from .reader import VolumeReader
from .gestures import GestureEngine, gestures, validate_owner


class Runtime:
    def __init__(self, hass, entry, signer):
        self.hass, self.entry, self.signer = hass, entry, signer
        self.config = {**entry.data, **entry.options}
        self.state = "connecting"
        self.last_key = None
        self.learned = None
        self.learning = False
        self._learn_timer = None
        self._discard_until = 0.0
        self.lock = asyncio.Lock()
        self._stopping = False
        self.gestures = GestureEngine(self._gesture)
        self.scripts = {}
        for code, binding in self.config.get("bindings", {}).items():
            validate_owner(binding)
            for press, target in gestures(binding).items():
                if target.get("kind") == "action":
                    self.scripts[(code, press)] = Script(
                        hass, cv.SCRIPT_SCHEMA(target["actions"]), target["name"], DOMAIN,
                        script_mode="single", max_runs=1)
        self.reader = VolumeReader(
            self.config["host"], self.config["port"], signer,
            self.config["device_name"], self.send, self.status,
            key=self.key, observe=self.observe,
        )

    @property
    def signal(self):
        return f"{DOMAIN}_{self.entry.entry_id}"

    def status(self, value):
        self.state = value
        if value != "listening":
            self.gestures.reset()
        async_dispatcher_send(self.hass, self.signal)

    def observe(self, code, action):
        if self.learning:
            if action == "DOWN" and self.learned is None:
                self.learned = code
                self.last_key = code
                self.status(self.state)
            return True
        if asyncio.get_running_loop().time() < self._discard_until:
            return True
        binding = self.config.get("bindings", {}).get(str(code))
        if binding and binding.get("gestures") and code not in (114, 115, 116):
            if validate_owner(binding) != "app":
                self.gestures.feed(code, action, gestures(binding))
            return True
        return False

    async def start_learning(self):
        self.stop_learning()
        await self.reader._cancel_repeat()
        self.reader._pressed_buttons.clear()
        self.learned = None
        self.learning = True
        self._learn_timer = asyncio.get_running_loop().call_later(60, self.stop_learning)

    def stop_learning(self):
        if self._learn_timer:
            self._learn_timer.cancel()
            self._learn_timer = None
        self.learning = False
        self.gestures.reset()
        # Discard the release/repeat of the key used during capture.
        self._discard_until = asyncio.get_running_loop().time() + 1

    async def send(self, direction):
        target = self.config["target"]
        state = self.hass.states.get(target)
        if state is None or state.state in ("unknown", "unavailable"):
            raise RuntimeError("target_unavailable")
        await self.hass.services.async_call(
            "media_player", f"volume_{direction}", {"entity_id": target}, blocking=True)

    def _gesture(self, code, press):
        self.entry.async_create_background_task(
            self.hass, self._run_gesture(code, press, self.gestures.generation),
            f"TV remote gesture {code} {press}")

    async def _run_gesture(self, code, press, generation):
        if not self._stopping and generation == self.gestures.generation:
            await self.key(code, press)

    async def key(self, code, press="single"):
        if self._stopping:
            return
        self.last_key = code
        binding = self.config.get("bindings", {}).get(str(code))
        if not binding:
            return
        binding = gestures(binding).get(press)
        if not binding or binding.get("kind") in ("app", "none"):
            return
        self.hass.bus.async_fire(EVENT_BUTTON, {
            "entry_id": self.entry.entry_id, "button": binding["name"], "scan_code": code, "press": press})
        if script := self.scripts.get((str(code), press)):
            # A long-running action must not block the input stream or key release.
            self.entry.async_create_background_task(
                self.hass, script.async_run(), f"TV remote key {code}")
        self.status(self.state)

    @asynccontextmanager
    async def maintenance(self):
        async with self.lock:
            if self._stopping:
                raise RuntimeError("entry_unloading")
            self.gestures.reset()
            await self.reader.stop()
            try:
                async with connection(self.config["host"], self.config["port"], self.signer) as device:
                    yield device
            finally:
                if not self._stopping:
                    self.reader.start()

    async def installed_apps(self):
        async with self.maintenance() as device:
            return await list_apps(device)

    async def stop(self):
        self._stopping = True
        self.stop_learning()
        async with self.lock:
            await self.reader.stop()
        for script in self.scripts.values():
            await script.async_stop()
