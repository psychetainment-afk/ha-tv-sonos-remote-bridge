"""Regression checks for first-render HA targets and precise volume feedback."""
import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from test_ha import hass, options_flow
from custom_components.tv_volume_bridge.reader import VolumeReader
from custom_components.tv_volume_bridge.sensor import ReaderStatus
from custom_components.tv_volume_bridge.diagnostics import async_get_config_entry_diagnostics


def fields(form):
    return {str(key): value for key, value in form['data_schema'].schema.items()}


@pytest.mark.asyncio
async def test_function_fields_and_first_render_targets(hass):
    flow, runtime = options_flow(hass)
    flow._code = '166'
    hass.services.async_register('light', 'toggle', AsyncMock())
    hass.services.async_register('scene', 'turn_on', AsyncMock())
    hass.states.async_set('light.room', 'on')
    hass.states.async_set('scene.cinema', 'scening')
    form = await flow.async_step_press({'press': 'single'})
    assert set(fields(form)) == {'kind'}
    form = await flow.async_step_function({'kind': 'event'})
    assert form['step_id'] == 'binding_event'
    assert set(fields(form)) == {'name'}
    runtime.installed_apps.assert_not_awaited()
    form = await flow.async_step_function({'kind': 'action'})
    assert set(fields(form)) == {'action'}
    form = await flow.async_step_action({'action': 'scene.turn_on'})
    assert set(fields(form)) == {'name', 'entity_id'}
    assert fields(form)['entity_id'].config['domain'] == ['scene']
    form = await flow.async_step_action({'action': 'light.toggle'})
    assert fields(form)['entity_id'].config['domain'] == ['light']
    @asynccontextmanager
    async def maintenance(): yield SimpleNamespace()
    runtime.maintenance = maintenance
    with patch('custom_components.tv_volume_bridge.config_flow.sync_helper', new=AsyncMock()):
        result = await flow.async_step_binding_action({'name': 'Light', 'entity_id': ['light.room'], 'package': 'org.stale.app'})
    binding = result['data']['bindings']['166']
    assert binding == {'name': 'Light', 'kind': 'action', 'actions': [
        {'action': 'light.toggle', 'target': {'entity_id': ['light.room']}}]}
    form = await flow.async_step_action({'action': 'sequence'})
    assert set(fields(form)) == {'name', 'actions'}
    await runtime.stop()


@pytest.mark.asyncio
async def test_direct_empty_target_and_error_retains_selection(hass):
    flow, runtime = options_flow(hass)
    flow._code, flow._press, flow._kind = '166', 'single', 'action'
    flow._direct_action = 'scene.turn_on'
    result = await flow.async_step_binding_action({'name': 'Cinema', 'entity_id': []})
    assert result['errors'] == {'entity_id': 'empty_action'}
    @asynccontextmanager
    async def maintenance(): yield SimpleNamespace()
    runtime.maintenance = maintenance
    with patch('custom_components.tv_volume_bridge.config_flow.sync_helper', side_effect=RuntimeError):
        result = await flow.async_step_binding_action({'name': 'Cinema', 'entity_id': ['scene.cinema']})
    assert result['errors'] == {'base': 'helper_failed'}
    key = next(key for key in result['data_schema'].schema if str(key) == 'entity_id')
    assert key.description['suggested_value'] == ['scene.cinema']
    assert '166' not in flow.config['bindings']
    await runtime.stop()


@pytest.mark.asyncio
async def test_fine_volume_serialized_real_feedback_and_boundaries(hass):
    flow, runtime = options_flow(hass)
    runtime.config['volume_step'] = 1
    calls = []
    def state(level):
        hass.states.async_set('media_player.test', 'playing', {'volume_level': level, 'supported_features': 4})
    async def record(call):
        calls.append(call.data['volume_level'])
        await asyncio.sleep(.01)
        state(call.data['volume_level'])
    hass.services.async_register('media_player', 'volume_set', record)
    state(.01)
    await asyncio.gather(runtime.send('up'), runtime.send('up'))
    assert calls == [.02, .03]
    state(.01)
    await runtime.send('down')
    await runtime.send('down')
    assert calls[-1] == 0
    assert calls.count(0) == 1
    state(.99)
    await runtime.send('up')
    await runtime.send('up')
    assert calls[-1] == 1
    assert calls.count(1) == 1
    assert runtime.last_volume_command['requested'] == 1
    await runtime.stop()


@pytest.mark.asyncio
async def test_no_fallback_on_missing_level_or_unsupported_target(hass):
    flow, runtime = options_flow(hass)
    runtime.config['volume_step'] = 1
    for attrs, error in [({}, 'volume_set_unsupported'), ({'supported_features': 4}, 'volume_level_unavailable'),
                         ({'supported_features': 4, 'volume_level': float('nan')}, 'volume_level_unavailable')]:
        hass.states.async_set('media_player.test', 'playing', attrs)
        with pytest.raises(RuntimeError, match=error): await runtime.send('up')
    await runtime.stop()


@pytest.mark.asyncio
async def test_stale_feedback_stops_without_optimistic_sensor_level(hass):
    flow, runtime = options_flow(hass)
    runtime.config['volume_step'] = 1
    hass.states.async_set('media_player.test', 'playing', {'volume_level': .01, 'supported_features': 4, 'is_volume_muted': False})
    handler = AsyncMock()
    hass.services.async_register('media_player', 'volume_set', handler)
    with pytest.raises(TimeoutError): await runtime.send('up')
    handler.assert_awaited_once()
    sensor = ReaderStatus(runtime, runtime.entry); sensor.hass = hass
    assert sensor.extra_state_attributes['volume_level'] == .01
    diagnostic = await async_get_config_entry_diagnostics(hass, runtime.entry)
    assert diagnostic['integration_version'] == '0.5.1'
    assert diagnostic['volume_command']['requested'] == .02
    assert 'tv.invalid' not in str(diagnostic)
    await runtime.stop()


@pytest.mark.asyncio
async def test_duplicate_volume_down_and_opposite_release():
    send = AsyncMock()
    reader = VolumeReader('unused', 5555, None, 'unused', send, lambda _: None)
    for key, action in [('KEY_VOLUMEUP', 'DOWN'), ('KEY_VOLUMEUP', 'DOWN'),
                        ('KEY_VOLUMEUP', 'REPEAT'), ('KEY_VOLUMEDOWN', 'UP')]:
        await reader.handle_line(f'EV_KEY {key} {action}')
    assert reader._volume_direction == 'up'
    send.assert_awaited_once_with('up')
    await reader.handle_line('EV_KEY KEY_VOLUMEUP UP')
    assert reader._volume_direction is None
    await reader.stop()

@pytest.mark.asyncio
async def test_sensor_updates_on_external_volume_change_and_removes_listener(hass):
    from unittest.mock import Mock
    flow, runtime = options_flow(hass)
    sensor = ReaderStatus(runtime, runtime.entry)
    sensor.hass = hass
    sensor.async_write_ha_state = Mock()
    await sensor.async_added_to_hass()
    hass.states.async_set('media_player.test', 'playing', {'volume_level': .07, 'is_volume_muted': True})
    await hass.async_block_till_done()
    sensor.async_write_ha_state.assert_called_once()
    assert sensor.extra_state_attributes['volume_level'] == .07
    assert sensor.extra_state_attributes['is_volume_muted'] is True
    await sensor.async_internal_will_remove_from_hass()
    await runtime.stop()
