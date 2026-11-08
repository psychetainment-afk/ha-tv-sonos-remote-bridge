"""Minimal private Home Assistant integration for TV volume keys."""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from adb_shell.auth.keygen import keygen
from adb_shell.auth.sign_cryptography import CryptographySigner
import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID, EVENT_HOMEASSISTANT_STARTED, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import CoreState, HomeAssistant, callback
import homeassistant.helpers.config_validation as cv

from .reader import VolumeReader
from .runtime import Runtime

DOMAIN = "tv_volume_bridge"
_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = vol.Schema({
    vol.Optional(DOMAIN): vol.Schema({
        vol.Required("host"): cv.string,
        vol.Optional("port", default=5555): cv.port,
        vol.Required("target"): cv.entity_id,
        vol.Optional("device_name", default="Xiaomi RC Consumer Control"): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)


def _load_signer(key_path):
    path = Path(key_path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    if not path.exists():
        keygen(str(path))
    os.chmod(path, 0o600)
    os.chmod(str(path)+".pub", 0o600)
    return CryptographySigner(str(path))


async def async_get_signer(hass):
    """Serialize first-time key creation across setup flows and entries."""
    lock = hass.data.setdefault(DOMAIN + "_key_lock", asyncio.Lock())
    async with lock:
        return await hass.async_add_executor_job(
            _load_signer, hass.config.path(".storage", DOMAIN, "adbkey"))


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    if DOMAIN not in config:
        hass.data.setdefault(DOMAIN, {})
        return True
    hass.data[DOMAIN + "_legacy"] = True
    conf = config[DOMAIN]
    if not conf["target"].startswith("media_player."):
        _LOGGER.error("TV volume target must be a media_player entity")
        return False
    signer = await async_get_signer(hass)
    last_status = None

    @callback
    def status(value):
        nonlocal last_status
        if value != last_status:
            _LOGGER.info("TV volume reader: %s", value)
            last_status = value
        hass.data[DOMAIN+"_status"] = value

    async def send(direction):
        state = hass.states.get(conf["target"])
        if state is None or state.state in ("unavailable", "unknown"):
            raise RuntimeError("target_unavailable")
        await hass.services.async_call(
            "media_player", "volume_"+direction,
            {ATTR_ENTITY_ID: conf["target"]}, blocking=True,
        )

    async def button(color):
        hass.bus.async_fire("tv_volume_bridge_button", {"button": color})

    reader = VolumeReader(conf["host"], conf["port"], signer, conf["device_name"], send, status, button)
    hass.data[DOMAIN] = reader

    @callback
    def start(_event=None):
        reader.start()

    async def shutdown(_event):
        await reader.stop()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, shutdown)
    if hass.state == CoreState.running:
        start()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, start)
    return True


async def async_setup_entry(hass, entry):
    """UI entries never take over an existing YAML reader."""
    from homeassistant.exceptions import ConfigEntryError
    if hass.data.get(DOMAIN + "_legacy"):
        raise ConfigEntryError("Remove legacy tv_volume_bridge YAML before enabling a UI entry")
    signer = await async_get_signer(hass)
    runtime = Runtime(hass, entry, signer)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = runtime
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    runtime.reader.start()
    entry.async_on_unload(entry.add_update_listener(_async_update_options))

    async def shutdown(_event):
        await runtime.stop()

    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, shutdown))
    return True


async def _async_update_options(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass, entry):
    if not await hass.config_entries.async_unload_platforms(entry, ["sensor"]):
        return False
    runtime = hass.data[DOMAIN].pop(entry.entry_id)
    await runtime.stop()
    return True
