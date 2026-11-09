"""Local reader status, without host address or key material."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import callback
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
        state = self.hass.states.get(self.runtime.config["target"])
        return {"last_scan_code": self.runtime.last_key,
                "volume_target": self.runtime.config["target"],
                "volume_level": state.attributes.get("volume_level") if state else None,
                "is_volume_muted": state.attributes.get("is_volume_muted") if state else None}

    async def async_added_to_hass(self):
        from homeassistant.helpers.event import async_track_state_change_event
        @callback
        def target_changed(event):
            self.async_write_ha_state()

        self.async_on_remove(async_track_state_change_event(
            self.hass, [self.runtime.config["target"]], target_changed))
        self.async_on_remove(async_dispatcher_connect(
            self.hass, self.runtime.signal, self.async_write_ha_state))
