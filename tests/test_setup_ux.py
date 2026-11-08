"""Setup UX regression tests; all ADB is simulated."""
import asyncio
import base64
import json
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from test_ha import hass, options_flow
from custom_components.tv_volume_bridge.adb import detect_remote, list_apps
from custom_components.tv_volume_bridge.config_flow import ConfigFlow

INVENTORY = 'add device 1: /dev/input/event2\n name: "Remote"\nadd device 2: /dev/input/event3\n name: "Keyboard"\n'

class Device:
    def __init__(self, chunks, wait=False):
        self.shell = AsyncMock(return_value=INVENTORY)
        self.chunks, self.closed, self.wait = chunks, False, wait
    async def streaming_shell(self, *args, **kwargs):
        try:
            for chunk in self.chunks:
                yield chunk
            if self.wait:
                await asyncio.Event().wait()
        finally:
            self.closed = True

@pytest.mark.asyncio
async def test_detection_fragmented_stream_ignores_other_keys():
    device = Device(['[ 1.0] /dev/input/event3: 0001 001c 00000001\n',
        '[ 2.0] /dev/input/event2: 0001 007', '2 00000001\n'])
    assert await detect_remote(device) == ['Remote']
    assert device.closed

@pytest.mark.asyncio
async def test_detection_ambiguous_and_timeout_close_stream():
    device = Device(['[ 1.0] /dev/input/event2: 0001 0072 00000001\n'
                     '[ 1.0] /dev/input/event3: 0001 0072 00000001\n'])
    assert await detect_remote(device) == ['Remote', 'Keyboard']
    idle = Device([], wait=True)
    assert await detect_remote(idle, seconds=0.01) == []
    assert idle.closed

@pytest.mark.asyncio
async def test_detection_cancellation_closes_stream():
    device = Device([], wait=True)
    task = asyncio.create_task(detect_remote(device))
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError): await task
    assert device.closed

@pytest.mark.asyncio
async def test_apps_decode_labels_and_reject_bad_payload():
    data = base64.b64encode(json.dumps({'org.jellyfin.androidtv': 'Jellyfin', 'de.exaring.waipu': 'waipu.tv'}).encode()).decode()
    device = SimpleNamespace(shell=AsyncMock(return_value=f'Broadcast completed: result=1, data="{data}"'))
    apps = await list_apps(device)
    assert apps[0] == {'value':'org.jellyfin.androidtv', 'label':'Jellyfin (org.jellyfin.androidtv)'}
    device.shell.return_value = 'Broadcast completed: result=0'
    with pytest.raises(RuntimeError): await list_apps(device)
    data=base64.b64encode(b'{"bad;reboot":"Bad"}').decode()
    device.shell.return_value=f'Broadcast completed: result=1, data="{data}"'
    with pytest.raises(ValueError): await list_apps(device)

@pytest.mark.asyncio
async def test_detection_progress_selects_only_after_confirmation(hass):
    flow = ConfigFlow(); flow.hass=hass
    flow._data={'host':'tv.invalid','port':5555,'target':'media_player.test'}
    flow._devices=['Remote','Keyboard']
    assert (await flow.async_step_device({'detect':True,'device_name':'Keyboard'}))['step_id']=='detect_start'
    release = asyncio.Event()
    async def detect():
        await release.wait()
        return ['Remote']
    with patch.object(flow, '_detect', new=detect):
        result=await flow.async_step_detect_start({})
        assert result['type']=='progress'
        task=flow._detect_task
        # Refresh reuses the same task.
        await flow.async_step_detect()
        assert flow._detect_task is task
        release.set()
        await task
        assert (await flow.async_step_detect())['type']=='progress_done'
    assert flow._detected_device=='Remote'
    result=await flow.async_step_device({'detect':False,'device_name':'Remote'})
    assert result['step_id']=='finish'
    assert (await flow.async_step_finish({}))['data']['device_name']=='Remote'

@pytest.mark.asyncio
async def test_detection_never_opens_stream_with_existing_reader(hass):
    flow=ConfigFlow(); flow.hass=hass; flow._data={'host':'tv.invalid','port':5555}
    hass.data['tv_volume_bridge']={'existing':SimpleNamespace(config={'host':'tv.invalid'})}
    with patch('custom_components.tv_volume_bridge.async_get_signer', new=AsyncMock()), patch(
            'custom_components.tv_volume_bridge.config_flow.connection') as connect:
        assert await flow._detect()==[]
        connect.assert_not_called()

@pytest.mark.asyncio
async def test_binding_shows_installed_app_selector_and_preserves_choice(hass):
    flow,runtime=options_flow(hass); flow._code='416'
    runtime.installed_apps=AsyncMock(return_value=[{'value':'org.jellyfin.androidtv','label':'Jellyfin'}])
    result=await flow.async_step_binding()
    assert not result['errors']
    fields=result['data_schema'].schema
    field=next(key for key in fields if str(key)=='package')
    assert fields[field].config['options'][0]['label']=='Jellyfin'
    @asynccontextmanager
    async def maintenance(): yield SimpleNamespace()
    runtime.maintenance=maintenance
    with patch('custom_components.tv_volume_bridge.config_flow.sync_helper',new=AsyncMock()):
        result=await flow.async_step_binding({'name':'Netflix','kind':'app','package':'org.jellyfin.androidtv'})
    assert result['data']['bindings']['416']['package']=='org.jellyfin.androidtv'
    await runtime.stop()

@pytest.mark.asyncio
async def test_help_is_repeatable_and_install_has_tv_instructions(hass):
    flow,runtime=options_flow(hass)
    assert 'guide' in (await flow.async_step_init())['menu_options']
    assert (await flow.async_step_guide())['step_id']=='guide'
    assert (await flow.async_step_guide({}))['type']=='menu'
    @asynccontextmanager
    async def maintenance(): yield SimpleNamespace()
    runtime.maintenance=maintenance
    with patch('custom_components.tv_volume_bridge.config_flow.install_helper',new=AsyncMock()) as install, patch(
            'custom_components.tv_volume_bridge.config_flow.sync_helper',new=AsyncMock()):
        result=await flow.async_step_helper({'install':True})
    install.assert_awaited_once()
    assert result['step_id']=='helper_ready'
    assert (await flow.async_step_helper_ready({}))['type']=='create_entry'
    await runtime.stop()


@pytest.mark.asyncio
async def test_options_detection_pauses_reader_and_resumes_on_cancel(hass):
    flow,runtime=options_flow(hass)
    runtime.reader.stop=AsyncMock()
    runtime.reader.start=Mock()
    started=asyncio.Event()
    @asynccontextmanager
    async def connection(*args): yield SimpleNamespace()
    async def capture(device):
        started.set()
        await asyncio.Event().wait()
    with patch('custom_components.tv_volume_bridge.runtime.connection',connection), patch(
            'custom_components.tv_volume_bridge.config_flow.detect_remote',new=capture):
        flow._detect_task=asyncio.create_task(flow._detect())
        await started.wait()
        runtime.reader.stop.assert_awaited_once()
        runtime.reader.start.assert_not_called()
        flow.async_remove()
        with pytest.raises(asyncio.CancelledError): await flow._detect_task
    runtime.reader.start.assert_called_once()
    await runtime.stop()

@pytest.mark.asyncio
async def test_new_xiaomi_entry_does_not_install_example_bindings(hass):
    flow=ConfigFlow(); flow.hass=hass
    flow._data={'host':'tv.invalid','port':5555,'target':'media_player.test'}
    flow._device_name='Xiaomi RC Consumer Control'
    result=await flow.async_step_finish({})
    assert result['data']['bindings']=={}
