"""Real HA forms/runtime, fake ADB only. Never connect to a real device."""
import asyncio
import json
import shutil
from contextlib import asynccontextmanager
from copy import deepcopy
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntries, ConfigEntryState
from homeassistant.setup import async_setup_component
from homeassistant import loader
from homeassistant.auth import auth_manager_from_config
from homeassistant.bootstrap import async_load_base_functionality

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from custom_components.tv_volume_bridge.adb import app_config, input_devices, install_helper, sync_helper
from custom_components.tv_volume_bridge.config_flow import ConfigFlow, OptionsFlow
from custom_components.tv_volume_bridge.const import DEFAULT_BINDINGS, DOMAIN
from custom_components.tv_volume_bridge.reader import VolumeReader, parse_key
from custom_components.tv_volume_bridge.runtime import Runtime


@pytest_asyncio.fixture
async def hass(tmp_path):
    instance = HomeAssistant(str(tmp_path))
    instance.config_entries = ConfigEntries(instance, {})
    with patch.object(Runtime, "installed_apps", new=AsyncMock(return_value=[])):
        yield instance
    await instance.async_stop(force=True)


def entry_data():
    return {"host": "tv.invalid", "port": 5555, "target": "media_player.test",
            "device_name": "Test remote", "bindings": deepcopy(DEFAULT_BINDINGS)}


def options_flow(hass):
    entry = SimpleNamespace(entry_id="test_entry", data=entry_data(), options={}, title="Test TV")
    hass.config_entries.async_get_known_entry = Mock(return_value=entry)
    flow = OptionsFlow()
    flow.hass = hass
    flow.handler = entry.entry_id
    runtime = Runtime(hass, entry, None)
    runtime.state = "listening"
    hass.data[DOMAIN] = {entry.entry_id: runtime}
    return flow, runtime


@pytest.mark.asyncio
async def test_connection_form_and_failed_probe(hass):
    flow = ConfigFlow()
    flow.hass = hass
    result = await flow.async_step_user()
    assert result["step_id"] == "user"
    flow._abort_if_unique_id_configured = Mock()
    flow.async_set_unique_id = AsyncMock()
    with patch("custom_components.tv_volume_bridge._load_signer", return_value=None), patch(
            "custom_components.tv_volume_bridge.config_flow.probe", side_effect=ConnectionError):
        result = await flow.async_step_user({"host": "tv.invalid", "port": 5555, "target": "media_player.test"})
    assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.asyncio
async def test_setup_selects_discovered_device(hass):
    flow = ConfigFlow()
    flow.hass = hass
    flow._abort_if_unique_id_configured = Mock()
    flow.async_set_unique_id = AsyncMock()
    with patch("custom_components.tv_volume_bridge._load_signer", return_value=None), patch(
            "custom_components.tv_volume_bridge.config_flow.probe", return_value=["Test remote"]):
        result = await flow.async_step_user({"host": "TV.INVALID", "port": 5555, "target": "media_player.test"})
    assert result["step_id"] == "device"
    result = await flow.async_step_device({"device_name": "Test remote"})
    assert result["step_id"] == "finish"
    result = await flow.async_step_finish({})
    assert result["data"]["host"] == "tv.invalid"
    assert result["data"]["bindings"] == {}  # Never guess Xiaomi codes on an unknown remote.


@pytest.mark.asyncio
async def test_yaml_reader_blocks_ui_setup(hass):
    hass.data[DOMAIN + "_legacy"] = True
    flow = ConfigFlow()
    flow.hass = hass
    result = await flow.async_step_user({"host": "tv.invalid", "port": 5555, "target": "media_player.test"})
    assert result["reason"] == "legacy_yaml_active"


@pytest.mark.asyncio
async def test_learn_suppresses_actions_and_protects_volume(hass):
    flow, runtime = options_flow(hass)
    runtime.send = AsyncMock()
    runtime.reader.send = runtime.send
    await flow.async_step_learn()
    await runtime.reader.handle_line("[ 1.0] 0001 0073 00000001")
    runtime.send.assert_not_called()
    result = await flow.async_step_learn({})
    assert result["errors"]["base"] == "protected_key"
    await runtime.reader.handle_line("[ 2.0] 0001 00a6 00000001")
    result = await flow.async_step_learn({})
    assert result["step_id"] == "press"
    assert flow._code == "166"
    await runtime.stop()


@pytest.mark.asyncio
async def test_cancelled_learning_expires_and_maintenance_restarts(hass):
    flow, runtime = options_flow(hass)
    await runtime.start_learning()
    assert runtime.learning
    runtime._learn_timer._run()
    assert not runtime.learning
    runtime.reader.stop = AsyncMock()
    runtime.reader.start = Mock()
    @asynccontextmanager
    async def fail_connection(*args):
        raise ConnectionError()
        yield
    with patch("custom_components.tv_volume_bridge.runtime.connection", fail_connection):
        with pytest.raises(ConnectionError):
            async with runtime.maintenance():
                pass
    runtime.reader.stop.assert_awaited_once()
    runtime.reader.start.assert_called_once()


@pytest.mark.asyncio
async def test_binding_saved_only_after_helper_ack(hass):
    flow, runtime = options_flow(hass)
    flow._code = "166"
    @asynccontextmanager
    async def maintenance():
        yield SimpleNamespace()
    runtime.maintenance = maintenance
    with patch("custom_components.tv_volume_bridge.config_flow.sync_helper", side_effect=RuntimeError):
        result = await flow.async_step_binding({"name": "Red", "kind": "event"})
    assert result["errors"]["base"] == "helper_failed"
    assert "166" not in flow.config["bindings"]
    with patch("custom_components.tv_volume_bridge.config_flow.sync_helper", new=AsyncMock()):
        result = await flow.async_step_binding({"name": "Red", "kind": "action", "actions": [
            {"action": "light.turn_on", "data": {"brightness": "{{ 42 }}"}}]})
    assert result["data"]["bindings"]["166"]["name"] == "Red"
    json.dumps(result["data"])  # Template validation must not store non-JSON Template objects.
    await runtime.stop()


@pytest.mark.asyncio
async def test_action_runs_in_ha_and_volume_service(hass):
    entry = SimpleNamespace(entry_id="test_entry", data=entry_data(), options={}, title="Test TV")
    entry.data["bindings"]["166"] = {"name": "Red", "kind": "action", "actions": [
        {"action": "test.record", "data": {"value": "{{ 'pressed' }}"}}]}
    tasks = []
    def background(_hass, coroutine, _name):
        task = asyncio.create_task(coroutine)
        tasks.append(task)
        return task
    entry.async_create_background_task = background
    calls = []
    async def record(call):
        calls.append(dict(call.data))
    hass.services.async_register("test", "record", record)
    hass.services.async_register("media_player", "volume_up", record)
    hass.states.async_set("media_player.test", "playing")
    runtime = Runtime(hass, entry, None)
    await runtime.key(166)
    await asyncio.gather(*tasks)
    runtime.config["volume_step"] = 0
    await runtime.send("up")
    assert calls == [{"value": "pressed"}, {"entity_id": "media_player.test"}]
    await runtime.stop()


@pytest.mark.asyncio
async def test_numeric_key_dedup_and_release():
    keys = []
    async def key(code): keys.append(code)
    reader = VolumeReader("test.invalid", 5555, None, "Test", AsyncMock(), Mock(), key=key)
    for value in ("00000001", "00000001", "00000002", "00000000", "00000001"):
        await reader.handle_line("[ 1.0] 0001 00a6 " + value)
    assert keys == [166, 166]
    await reader.stop()


def test_inventory_and_config_reject_shell_input():
    assert input_devices('add device 1: /dev/input/event3\n name: "Test"\n') == ["Test"]
    with pytest.raises(ValueError):
        app_config({"416": {"kind": "app", "package": "bad; reboot"}})
    with pytest.raises(ValueError):
        app_config({"116": {"kind": "event"}})
    assert parse_key("[ 1.0] 0001 01a0 00000001") == (416, "DOWN")


@pytest.mark.asyncio
async def test_helper_config_requires_ack_and_install_never_uninstalls():
    device = SimpleNamespace(shell=AsyncMock(return_value="Broadcast completed: result=0"), push=AsyncMock())
    with pytest.raises(RuntimeError):
        await sync_helper(device, DEFAULT_BINDINGS)
    device.shell = AsyncMock(return_value="Failure [INSTALL_FAILED_UPDATE_INCOMPATIBLE]")
    with pytest.raises(RuntimeError):
        await install_helper(device)
    assert not any("uninstall" in call.args[0] for call in device.shell.call_args_list)
    assert any("rm -f /data/local/tmp/tv-volume-bridge.apk" == call.args[0] for call in device.shell.call_args_list)


@pytest.mark.asyncio
async def test_unload_during_maintenance_cannot_restart_reader(hass):
    flow, runtime = options_flow(hass)
    runtime.reader.stop = AsyncMock()
    runtime.reader.start = Mock()
    entered, release = asyncio.Event(), asyncio.Event()
    @asynccontextmanager
    async def fake_connection(*args):
        yield SimpleNamespace()
    async def maintenance():
        async with runtime.maintenance():
            entered.set()
            await release.wait()
    with patch("custom_components.tv_volume_bridge.runtime.connection", fake_connection):
        task = asyncio.create_task(maintenance())
        await entered.wait()
        stop = asyncio.create_task(runtime.stop())
        await asyncio.sleep(0)
        release.set()
        await asyncio.gather(task, stop)
    runtime.reader.start.assert_not_called()


@pytest.mark.asyncio
async def test_real_ha_entry_and_status_sensor_load_and_unload(hass):
    source = Path(__file__).resolve().parents[1] / "custom_components"
    shutil.copytree(source, hass.config.path("custom_components"), ignore=shutil.ignore_patterns("__pycache__"))
    hass.config.skip_pip = True
    loader.async_setup(hass)
    assert await async_load_base_functionality(hass)
    hass.auth = await auth_manager_from_config(hass, [], [])
    with patch("custom_components.tv_volume_bridge._load_signer", return_value=None), patch.object(
            VolumeReader, "start"), patch.object(VolumeReader, "stop", new=AsyncMock()), patch(
            "custom_components.tv_volume_bridge.config_flow.probe", return_value=["Test remote"]):
        assert await async_setup_component(hass, DOMAIN, {})
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
        assert result["step_id"] == "user"
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {
            "host": "tv.invalid", "port": 5555, "target": "media_player.test"})
        assert result["step_id"] == "device"
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {"device_name": "Test remote", "detect": False})
        assert result["step_id"] == "finish"
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
        entry = result["result"]
        await hass.async_block_till_done()
        assert entry.state is ConfigEntryState.LOADED
        assert entry.entry_id in hass.data[DOMAIN]
        assert any(state.domain == "sensor" and state.state == "connecting" for state in hass.states.async_all())
        options = await hass.config_entries.options.async_init(entry.entry_id)
        assert options["type"] == "menu"
        options = await hass.config_entries.options.async_configure(options["flow_id"], {"next_step_id": "connection"})
        assert options["step_id"] == "connection"
        result = await hass.config_entries.options.async_configure(options["flow_id"], {
            "host": "tv.invalid", "port": 5555, "target": "media_player.changed", "device_name": "Test remote"})
        assert result["type"] == "create_entry"
        await hass.async_block_till_done()
        assert entry.options["target"] == "media_player.changed"
        assert hass.data[DOMAIN][entry.entry_id].config["target"] == "media_player.changed"
        assert await hass.config_entries.async_unload(entry.entry_id)
        assert entry.entry_id not in hass.data[DOMAIN]
