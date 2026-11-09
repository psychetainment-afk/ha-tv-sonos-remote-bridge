"""Explicit allowlist: never export address, ADB keys or user action data."""
from importlib.resources import files
import json

from .const import DOMAIN


def _version():
    return json.loads(files(__package__).joinpath("manifest.json").read_text())["version"]


async def async_get_config_entry_diagnostics(hass, entry):
    runtime = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    return {
        "integration_version": await hass.async_add_executor_job(_version),
        "transport": "adb_tcp_rsa",
        "status": runtime.state if runtime else "not_running",
        "binding_count": len(({**entry.data, **entry.options}).get("bindings", {})),
        "last_error_type": runtime.reader.last_error if runtime else None,
        "volume_step": runtime.config.get("volume_step", 1) if runtime else None,
        "volume_command": runtime.last_volume_command if runtime else None,
    }
