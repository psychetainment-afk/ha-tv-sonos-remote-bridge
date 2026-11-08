"""Read volume keys through one authenticated, read-only ADB stream."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from contextlib import suppress
import re
import time

from adb_shell.adb_device_async import AdbDeviceTcpAsync

_DEVICE = re.compile(r"add device \d+: (/dev/input/event\d+)")
_KEY = re.compile(r"EV_KEY\s+(KEY_VOLUMEUP|KEY_VOLUMEDOWN)\s+(DOWN|UP|REPEAT|00000002)")
_BUTTON = re.compile(r"EV_KEY\s+(KEY_EJECTCD|KEY_SHUFFLE|KEY_SEARCH|KEY_WWW)\s+(DOWN|UP|REPEAT|00000002)")
_COLORS = {"KEY_EJECTCD": "green", "KEY_SHUFFLE": "yellow", "KEY_SEARCH": "blue", "KEY_WWW": "tv_plus"}


class VolumeReader:
    """No adb executable, subprocess, webhook or external server required."""

    def __init__(self, host, port, signer, device_name, send, status, button=None):
        self.host, self.port, self.signer = host, port, signer
        self.device_name = device_name
        self.send: Callable[[str], Awaitable[None]] = send
        self.status = status
        self.button = button
        self._pressed_buttons = set()
        self.device = None
        self._task = None
        self._repeat_task = None
        self._generation = 0
        self._closed = False
        self.sent = 0
        self.last_error = None

    def start(self):
        self._task = asyncio.create_task(self._run(), name="tv_volume_bridge_reader")

    async def stop(self):
        self._closed = True
        await self._cancel_repeat()
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        self.status("stopped")

    async def _cancel_repeat(self):
        self._generation += 1
        if self._repeat_task:
            self._repeat_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._repeat_task
            self._repeat_task = None

    async def _send_once(self, direction):
        try:
            async with asyncio.timeout(3):
                await self.send(direction)
            self.sent += 1
        except asyncio.CancelledError:
            raise
        except Exception as error:
            self.last_error = type(error).__name__
            self.status("action_failed")
            raise

    async def _repeat(self, direction, generation):
        started = time.monotonic()
        await asyncio.sleep(0.45)
        try:
            while not self._closed and generation == self._generation and time.monotonic()-started < 5:
                await self._send_once(direction)
                await asyncio.sleep(0.22)
        except asyncio.CancelledError:
            raise
        except Exception:
            # Never retry or replay failed volume changes after reconnecting.
            return

    async def handle_line(self, line):
        color_match = _BUTTON.search(line)
        if color_match:
            key, action = color_match.groups()
            if action == "UP":
                self._pressed_buttons.discard(key)
            elif action == "DOWN" and key not in self._pressed_buttons:
                self._pressed_buttons.add(key)
                if self.button is not None:
                    await self.button(_COLORS[key])
            return
        match = _KEY.search(line)
        if not match:
            return
        direction = "up" if match.group(1) == "KEY_VOLUMEUP" else "down"
        action = match.group(2)
        if action == "DOWN":
            await self._cancel_repeat()
            await self._send_once(direction)
            self._repeat_task = asyncio.create_task(self._repeat(direction, self._generation))
        elif action == "UP":
            await self._cancel_repeat()

    async def _run(self):
        while not self._closed:
            try:
                self.status("connecting")
                self.device = AdbDeviceTcpAsync(self.host, self.port, default_transport_timeout_s=10)
                await self.device.connect(rsa_keys=[self.signer], auth_timeout_s=45, read_timeout_s=50)
                inventory = await self.device.shell("getevent -lp", timeout_s=15)
                path = None
                current = None
                for line in inventory.splitlines():
                    if match := _DEVICE.search(line):
                        current = match.group(1)
                    if "name:" in line and f'"{self.device_name}"' in line:
                        path = current
                        break
                if not path or not re.fullmatch(r"/dev/input/event\d+", path):
                    raise RuntimeError("input_device_not_found")
                self.status("listening")
                buffer = ""
                async for chunk in self.device.streaming_shell(
                    f"getevent -lt {path}", transport_timeout_s=3600, read_timeout_s=3610
                ):
                    buffer += chunk
                    if len(buffer) > 16384:
                        raise RuntimeError("input_buffer_limit")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        await self.handle_line(line)
                raise ConnectionError("input_stream_closed")
            except asyncio.CancelledError:
                raise
            except Exception as error:
                self.last_error = type(error).__name__
                self.status("disconnected")
            finally:
                self._pressed_buttons.clear()
                await self._cancel_repeat()
                if self.device:
                    with suppress(Exception):
                        async with asyncio.timeout(5):
                            await self.device.close()
                    self.device = None
            await asyncio.sleep(5)
