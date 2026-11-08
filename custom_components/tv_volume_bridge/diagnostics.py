"""Explicit allowlist: never export address, ADB keys or user action data."""
from .const import DOMAIN


async def async_get_config_entry_diagnostics(hass, entry):
    runtime = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    return {
        "integration_version": "0.3.0",
        "transport": "adb_tcp_rsa",
        "status": runtime.state if runtime else "not_running",
        "binding_count": len(({**entry.data, **entry.options}).get("bindings", {})),
        "last_error_type": runtime.reader.last_error if runtime else None,
    }
