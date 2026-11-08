"""Minimal private Home Assistant integration for TV volume keys."""
from __future__ import annotations

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


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    if DOMAIN not in config:
        return True
    conf = config[DOMAIN]
    if not conf["target"].startswith("media_player."):
        _LOGGER.error("TV volume target must be a media_player entity")
        return False
    signer = await hass.async_add_executor_job(
        _load_signer, hass.config.path(".storage", DOMAIN, "adbkey")
    )
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
