"""Browser setup, learning and action assignment; classic ADB TCP/RSA only."""
from __future__ import annotations

import asyncio
from copy import deepcopy
import re

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, selector

from .adb import connection, detect_remote, install_helper, probe, sync_helper
from .const import DEFAULT_DEVICE, DOMAIN
from .gestures import PRESSES, gestures, validate_owner


def connection_schema(defaults):
    return vol.Schema({
        vol.Required("host", default=defaults.get("host", "")): str,
        vol.Required("port", default=defaults.get("port", 5555)): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
        vol.Required("target", default=defaults.get("target", "")): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="media_player")),
    })


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            # Avoid duplicate readers for YAML or another config entry.
            user_input["host"] = user_input["host"].strip().lower()
            if not user_input["host"] or re.search(r"[\s/\\]", user_input["host"]):
                errors["host"] = "invalid_host"
            elif self.hass.data.get(DOMAIN + "_legacy"):
                return self.async_abort(reason="legacy_yaml_active")
            else:
                await self.async_set_unique_id(f"{user_input['host']}:{user_input['port']}")
                self._abort_if_unique_id_configured()
                from . import async_get_signer
                try:
                    signer = await async_get_signer(self.hass)
                    self._devices = await probe(user_input["host"], user_input["port"], signer)
                except ValueError:
                    errors["base"] = "no_input_devices"
                except Exception:
                    errors["base"] = "cannot_connect"
                else:
                    self._data = user_input
                    return await self.async_step_device()
        return self.async_show_form(step_id="user", data_schema=connection_schema(user_input or {}), errors=errors)

    async def async_step_device(self, user_input=None):
        if user_input:
            if user_input.get("detect", False):
                return await self.async_step_detect_start()
            self._device_name = user_input["device_name"]
            return await self.async_step_finish()
        default = getattr(self, "_detected_device", None) or (
            DEFAULT_DEVICE if DEFAULT_DEVICE in self._devices else self._devices[0])
        return self.async_show_form(step_id="device", data_schema=vol.Schema({
            vol.Required("detect", default=not hasattr(self, "_detected_device")): bool,
            vol.Required("device_name", default=default): selector.SelectSelector(
                selector.SelectSelectorConfig(options=self._devices))}), errors=getattr(self, "_detect_errors", {}))

    async def async_step_detect_start(self, user_input=None):
        if user_input is not None:
            if not getattr(self, "_detect_task", None) or self._detect_task.done():
                self._detect_task = self.hass.async_create_task(self._detect(), "TV remote detection")
            return await self.async_step_detect()
        return self.async_show_form(step_id="detect_start", data_schema=vol.Schema({}), last_step=False)

    async def _detect(self):
        from . import async_get_signer
        signer = await async_get_signer(self.hass)
        # A single stream per host, even when more than one setup is opened.
        lock = self.hass.data.setdefault(DOMAIN + "_detect_lock_" + self._data["host"], asyncio.Lock())
        if lock.locked():
            return []
        async with lock:
            active = self.hass.data.get(DOMAIN, {})
            if self.hass.data.get(DOMAIN + "_legacy") or any(
                    runtime.config["host"] == self._data["host"] for runtime in active.values()):
                return []
            async with connection(self._data["host"], self._data["port"], signer) as device:
                return await detect_remote(device)

    async def async_step_detect(self, user_input=None):
        if not self._detect_task.done():
            return self.async_show_progress(step_id="detect", progress_action="detecting",
                                            progress_task=self._detect_task)
        self._detect_errors = {}
        try:
            names = self._detect_task.result()
        except Exception:
            names = []
        if len(names) == 1 and names[0] in self._devices:
            self._detected_device = names[0]
        else:
            self._detected_device = None
            self._detect_errors = {"base": "detection_ambiguous" if names else "detection_timeout"}
        return self.async_show_progress_done(next_step_id="device")

    async def async_step_finish(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=self._data["host"], data={
                **self._data, "device_name": self._device_name,
                "bindings": {}})
        return self.async_show_form(step_id="finish", data_schema=vol.Schema({}))

    def async_remove(self):
        task = getattr(self, "_detect_task", None)
        if task and not task.done():
            task.cancel()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlow()


class OptionsFlow(config_entries.OptionsFlow):
    @property
    def runtime(self):
        return self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)

    @property
    def config(self):
        return {**self.config_entry.data, **self.config_entry.options}

    async def async_step_init(self, user_input=None):
        if self.runtime is None:
            return self.async_abort(reason="not_running")
        self.runtime.stop_learning()
        return self.async_show_menu(step_id="init", menu_options=["guide", "helper", "learn", "remove", "detect_start", "connection"])

    async def async_step_guide(self, user_input=None):
        if user_input is not None:
            return await self.async_step_init()
        return self.async_show_form(step_id="guide", data_schema=vol.Schema({}))

    async def async_step_detect_start(self, user_input=None):
        if user_input is not None:
            if not getattr(self, "_detect_task", None) or self._detect_task.done():
                self._detect_task = self.hass.async_create_task(self._detect(), "TV remote detection")
            return await self.async_step_detect()
        return self.async_show_form(step_id="detect_start", data_schema=vol.Schema({}), last_step=False)

    async def _detect(self):
        if self.runtime is None or self.runtime.lock.locked():
            raise RuntimeError("reader_busy")
        self.runtime.stop_learning()
        async with self.runtime.maintenance() as device:
            return await detect_remote(device)

    async def async_step_detect(self, user_input=None):
        if not self._detect_task.done():
            return self.async_show_progress(step_id="detect", progress_action="detecting",
                                            progress_task=self._detect_task)
        self._detect_errors = {}
        try:
            names = self._detect_task.result()
        except Exception:
            names = []
        self._detected_device = names[0] if len(names) == 1 else self.config["device_name"]
        if len(names) != 1:
            self._detect_errors = {"base": "detection_ambiguous" if names else "detection_timeout"}
        return self.async_show_progress_done(next_step_id="detect_result")

    async def async_step_detect_result(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data={**self.config_entry.options, **user_input})
        return self.async_show_form(step_id="detect_result", data_schema=vol.Schema({
            vol.Required("device_name", default=self._detected_device): str}), errors=self._detect_errors)

    def async_remove(self):
        task = getattr(self, "_detect_task", None)
        if task and not task.done():
            task.cancel()
        if self.runtime:
            self.runtime.stop_learning()

    async def async_step_connection(self, user_input=None):
        errors = {}
        schema = connection_schema(self.config).extend({
            vol.Required("device_name", default=self.config["device_name"]): str})
        if user_input:
            # Address changes require a fresh integration so unique IDs stay accurate.
            if (user_input["host"], user_input["port"]) != (self.config["host"], self.config["port"]):
                errors["base"] = "address_changed"
            else:
                return self.async_create_entry(title="", data={**self.config_entry.options, **user_input})
        return self.async_show_form(step_id="connection", data_schema=schema, errors=errors)

    async def async_step_learn(self, user_input=None):
        runtime = self.runtime
        if not runtime or runtime.state != "listening":
            return self.async_abort(reason="not_running")
        errors = {}
        if user_input is not None:
            if runtime.learned is None:
                errors["base"] = "no_key"
            elif runtime.learned in (114, 115, 116):
                errors["base"] = "protected_key"
                runtime.learned = None
            else:
                self._code = str(runtime.learned)
                runtime.stop_learning()
                self._apps = None
                return await self.async_step_press()
        else:
            await runtime.start_learning()
        return self.async_show_form(step_id="learn", data_schema=vol.Schema({}), errors=errors)

    async def async_step_press(self, user_input=None):
        if user_input is not None:
            self._press = user_input["press"]
            return await self.async_step_binding()
        return self.async_show_form(step_id="press", data_schema=vol.Schema({
            vol.Required("press", default="single"): selector.SelectSelector(
                selector.SelectSelectorConfig(options=list(PRESSES), translation_key="press"))}))

    async def async_step_binding(self, user_input=None):
        errors = {}
        if user_input:
            user_input = dict(user_input)
            press = user_input.pop("press", getattr(self, "_press", "single"))
            self._press = press
            kind = user_input["kind"]
            if kind == "app" and not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+", user_input.get("package", "")):
                errors["package"] = "invalid_package"
            elif kind == "action" and not user_input.get("actions"):
                errors["actions"] = "empty_action"
            else:
                if kind == "action":
                    try:
                        cv.SCRIPT_SCHEMA(user_input["actions"])
                    except vol.Invalid:
                        errors["base"] = "invalid_action"
                bindings = deepcopy(self.config["bindings"])
                old_binding = bindings.get(self._code, {"name": user_input["name"], "kind": "none"})
                if press == "single":
                    binding = {**user_input}
                    if old_binding.get("gestures"):
                        binding["gestures"] = deepcopy(old_binding["gestures"])
                else:
                    binding = deepcopy(old_binding)
                    binding.setdefault("gestures", {})
                    if kind == "none":
                        binding["gestures"].pop(press, None)
                    else:
                        binding["gestures"][press] = user_input
                    if not binding["gestures"]:
                        binding.pop("gestures")
                try:
                    validate_owner(binding)
                except ValueError:
                    errors["base"] = "mixed_gesture_targets"
                if binding.get("kind") == "none" and not binding.get("gestures"):
                    bindings.pop(self._code, None)
                else:
                    bindings[self._code] = binding
                if not errors:
                    try:
                        async with self.runtime.maintenance() as device:
                            await sync_helper(device, bindings)
                    except Exception:
                        errors["base"] = "helper_failed"
                    else:
                        return self.async_create_entry(title="", data={**self.config_entry.options, "bindings": bindings})
        if getattr(self, "_apps", None) is None:
            self._apps = []
            try:
                self._apps = await self.runtime.installed_apps()
            except Exception:
                pass
        if not self._apps and not errors:
            errors["base"] = "app_list_unavailable"
        press = getattr(self, "_press", "single")
        old = user_input or gestures(self.config["bindings"].get(self._code, {})).get(press, {})
        apps = list(self._apps)
        if old.get("package") and not any(app["value"] == old["package"] for app in apps):
            apps.append({"value": old["package"], "label": old["package"]})
        return self.async_show_form(step_id="binding", description_placeholders={"code": self._code, "press": press},
            data_schema=vol.Schema({
                vol.Required("name", default=old.get("name", f"Key {self._code}")): str,
                vol.Required("kind", default=old.get("kind", "event")): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=["event", "action", "app", "none"], translation_key="binding_kind")),
                vol.Optional("package", description={"suggested_value": old.get("package", "")}): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=apps, custom_value=True, mode="dropdown")),
                vol.Optional("actions", default=old.get("actions", [])): selector.ActionSelector(),
            }), errors=errors)

    async def async_step_remove(self, user_input=None):
        bindings = deepcopy(self.config["bindings"])
        if not bindings:
            return self.async_abort(reason="no_bindings")
        if user_input:
            bindings.pop(user_input["code"], None)
            try:
                async with self.runtime.maintenance() as device:
                    await sync_helper(device, bindings)
            except Exception:
                return self.async_show_form(step_id="remove", data_schema=vol.Schema({
                    vol.Required("code", default=user_input["code"]): str}), errors={"base": "helper_failed"})
            return self.async_create_entry(title="", data={**self.config_entry.options, "bindings": bindings})
        return self.async_show_form(step_id="remove", data_schema=vol.Schema({
            vol.Required("code"): selector.SelectSelector(selector.SelectSelectorConfig(options=[
                {"value": code, "label": f"{value['name']} ({code})"} for code, value in bindings.items()]))}))

    async def async_step_helper(self, user_input=None):
        errors = {}
        if user_input:
            try:
                async with self.runtime.maintenance() as device:
                    if user_input["install"]:
                        await install_helper(device)
                    await sync_helper(device, self.config["bindings"])
            except Exception:
                errors["base"] = "helper_failed"
            else:
                return await self.async_step_helper_ready()
        return self.async_show_form(step_id="helper", data_schema=vol.Schema({
            vol.Required("install", default=False): bool}), errors=errors)

    async def async_step_helper_ready(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=dict(self.config_entry.options))
        return self.async_show_form(step_id="helper_ready", data_schema=vol.Schema({}))
