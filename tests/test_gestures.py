"""Gesture arbitration, migration, helper negotiation and real HA dispatch."""
import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from test_ha import hass, options_flow
from custom_components.tv_volume_bridge.gestures import GestureEngine, validate_owner
from custom_components.tv_volume_bridge.adb import app_config, sync_helper


class Clock:
    def __init__(self):
        self.now, self.jobs = 0, []
    def call_later(self, delay, callback, *args):
        handle = SimpleNamespace(at=self.now + delay, callback=callback, args=args, cancelled=False)
        handle.cancel = lambda: setattr(handle, "cancelled", True)
        self.jobs.append(handle)
        return handle
    def advance(self, delay):
        end = self.now + delay
        while pending := sorted([job for job in self.jobs if not job.cancelled and job.at <= end], key=lambda job: job.at):
            job = pending[0]
            self.now, job.cancelled = job.at, True
            job.callback(*job.args)
        self.now = end


@pytest.mark.parametrize("scenario,expected", [
    ("single", [(1, "single")]), ("double", [(1, "double")]),
    ("long", [(1, "long")]), ("second_long", [(1, "long")]),
    ("reset", []), ("independent", [(1, "single"), (2, "single")]),
])
def test_gesture_arbitration(scenario, expected):
    clock, calls = Clock(), []
    engine = GestureEngine(lambda code, press: calls.append((code, press)))
    with patch("custom_components.tv_volume_bridge.gestures.asyncio.get_running_loop", return_value=clock):
        engine.feed(1, "DOWN", {"single", "double", "long"})
        engine.feed(1, "REPEAT", {"single", "double", "long"})
        if scenario == "long":
            clock.advance(.76)
        engine.feed(1, "UP", {"single", "double", "long"})
        if scenario in ("double", "second_long"):
            clock.advance(.1)
            engine.feed(1, "DOWN", {"single", "double", "long"})
            if scenario == "second_long": clock.advance(.76)
            engine.feed(1, "UP", {"single", "double", "long"})
        if scenario == "independent":
            engine.feed(2, "DOWN", {"single", "double", "long"})
            engine.feed(2, "UP", {"single", "double", "long"})
        if scenario == "reset": engine.reset()
        clock.advance(6)
    assert calls == expected
    assert not engine.states


def test_legacy_immediate_and_long_only_release():
    clock, calls = Clock(), []
    engine = GestureEngine(lambda code, press: calls.append((code, press)))
    with patch("custom_components.tv_volume_bridge.gestures.asyncio.get_running_loop", return_value=clock):
        engine.feed(1, "DOWN", {"single"})
        assert calls == [(1, "single")]
        engine.feed(1, "DOWN", {"single"})
        engine.feed(1, "UP", {"single"})
        engine.feed(2, "DOWN", {"single", "long"})
        engine.feed(2, "UP", {"single", "long"})
        clock.advance(6)
    assert calls == [(1, "single"), (2, "single")]


def test_expired_double_window_becomes_two_singles():
    clock, calls = Clock(), []
    engine = GestureEngine(lambda code, press: calls.append(press))
    with patch("custom_components.tv_volume_bridge.gestures.asyncio.get_running_loop", return_value=clock):
        for _ in range(2):
            engine.feed(1, "DOWN", {"single", "double"})
            engine.feed(1, "UP", {"single", "double"})
            clock.advance(.351)
    assert calls == ["single", "single"]


def test_owner_and_app_payload_preserve_legacy():
    binding = {"name": "Netflix", "kind": "app", "package": "org.example.one",
               "gestures": {"double": {"name": "Second", "kind": "app", "package": "org.example.two"}}}
    assert app_config({"416": binding}) == {"416": {"single": "org.example.one", "double": "org.example.two"}}
    assert app_config({"416": {"name": "Old", "kind": "app", "package": "org.example.one"}}) == {"416": "org.example.one"}
    binding["gestures"]["double"] = {"kind": "event", "name": "HA"}
    with pytest.raises(ValueError, match="mixed_gesture_targets"): validate_owner(binding)


@pytest.mark.asyncio
async def test_old_helper_rejected_before_any_configuration_write():
    device = SimpleNamespace(shell=AsyncMock(return_value="Broadcast completed: result=0"))
    bindings = {"166": {"kind": "event", "name": "Red", "gestures": {"double": {"kind": "event", "name": "Double"}}}}
    with pytest.raises(RuntimeError, match="helper_gestures_unsupported"):
        await sync_helper(device, bindings)
    assert device.shell.await_count == 1
    assert ".PROTOCOL" in device.shell.call_args.args[0]
    device.shell = AsyncMock(return_value="Broadcast completed: result=2")
    await sync_helper(device, bindings)
    assert "--ei protocol 2" in device.shell.call_args.args[0]


@pytest.mark.asyncio
async def test_flow_preserves_single_and_rejects_mixed_owner(hass):
    flow, runtime = options_flow(hass)
    flow._code = "416"
    runtime.entry.data["bindings"]["416"] = {"name": "Old", "kind": "app", "package": "org.example.one"}
    @asynccontextmanager
    async def maintenance(): yield SimpleNamespace()
    runtime.maintenance = maintenance
    with patch("custom_components.tv_volume_bridge.config_flow.sync_helper", new=AsyncMock()) as sync:
        form = await flow.async_step_press({"press": "double"})
        assert form["step_id"] == "function"
        result = await flow.async_step_binding({"name": "Double", "kind": "app", "package": "org.example.two"})
        binding = result["data"]["bindings"]["416"]
        assert binding["package"] == "org.example.one"
        assert binding["gestures"]["double"]["package"] == "org.example.two"
        result = await flow.async_step_binding({"name": "HA", "kind": "event"})
        assert result["errors"]["base"] == "mixed_gesture_targets"
        assert sync.await_count == 1
    await runtime.stop()


@pytest.mark.asyncio
async def test_runtime_ha_gesture_dispatch_once_and_reset(hass):
    flow, runtime = options_flow(hass)
    runtime.config["bindings"]["166"] = {"kind": "event", "name": "Red",
        "gestures": {"double": {"kind": "event", "name": "Double"}}}
    tasks = []
    runtime.entry.async_create_background_task = lambda _hass, coro, _name: tasks.append(asyncio.create_task(coro))
    with patch.object(type(hass.bus), "async_fire") as fire:
        for action in ("DOWN", "UP", "DOWN", "UP"):
            assert runtime.observe(166, action)
        await asyncio.gather(*tasks)
        # Use the integration constant rather than assuming a public event spelling.
        from custom_components.tv_volume_bridge.const import EVENT_BUTTON
        events = [call for call in fire.call_args_list if call.args[0] == EVENT_BUTTON]
        assert len(events) == 1
        assert events[0].args[1]["press"] == "double"
        runtime.observe(166, "DOWN")
        runtime.observe(166, "UP")
        runtime.status("disconnected")
        assert not runtime.gestures.states
    await runtime.stop()


@pytest.mark.asyncio
async def test_remove_only_double_preserves_legacy_single(hass):
    flow, runtime = options_flow(hass)
    flow._code, flow._press = "166", "double"
    runtime.entry.data["bindings"]["166"] = {"name": "Red", "kind": "event",
        "gestures": {"double": {"name": "Second", "kind": "event"}}}
    @asynccontextmanager
    async def maintenance(): yield SimpleNamespace()
    runtime.maintenance = maintenance
    with patch("custom_components.tv_volume_bridge.config_flow.sync_helper", new=AsyncMock()):
        result = await flow.async_step_binding({"name": "Second", "kind": "none"})
    assert result["data"]["bindings"]["166"] == {"name": "Red", "kind": "event"}
    await runtime.stop()


@pytest.mark.asyncio
async def test_local_app_gestures_never_schedule_ha_actions(hass):
    flow, runtime = options_flow(hass)
    runtime.config["bindings"]["416"] = {"kind": "app", "name": "App", "package": "org.example.one",
        "gestures": {"long": {"kind": "app", "name": "Other", "package": "org.example.two"}}}
    for action in ("DOWN", "REPEAT", "UP"):
        assert runtime.observe(416, action)
    assert not runtime.gestures.states
    await runtime.stop()


@pytest.mark.asyncio
async def test_queued_ha_gesture_is_discarded_on_disconnect(hass):
    flow, runtime = options_flow(hass)
    runtime.config["bindings"]["166"] = {"kind": "event", "name": "Red"}
    tasks = []
    runtime.entry.async_create_background_task = lambda _hass, coro, _name: tasks.append(asyncio.create_task(coro))
    with patch.object(type(hass.bus), "async_fire") as fire:
        runtime._gesture(166, "single")
        runtime.status("disconnected")
        await asyncio.gather(*tasks)
        from custom_components.tv_volume_bridge.const import EVENT_BUTTON
        assert not [call for call in fire.call_args_list if call.args[0] == EVENT_BUTTON]
    await runtime.stop()
