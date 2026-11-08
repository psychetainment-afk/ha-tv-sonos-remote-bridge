"""Local reader status, without host address or key material."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([ReaderStatus(hass.data[DOMAIN][entry.entry_id], entry)])


class ReaderStatus(SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "connection"
    _attr_device_class = "enum"
    _attr_options = ["connecting", "listening", "stopped", "action_failed", "disconnected"]
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:remote-tv"

    def __init__(self, runtime, entry):
        self.runtime = runtime
        self._attr_unique_id = f"{entry.entry_id}_connection"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title, "manufacturer": "TV Remote Bridge",
            "model": "ADB remote input",
            "configuration_url": "homeassistant://config/integrations/integration/tv_volume_bridge",
        }

    @property
    def native_value(self):
        return self.runtime.state

    @property
    def extra_state_attributes(self):
        return {"last_scan_code": self.runtime.last_key}

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(
            self.hass, self.runtime.signal, self.async_write_ha_state))
