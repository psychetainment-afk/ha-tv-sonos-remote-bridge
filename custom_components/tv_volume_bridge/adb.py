"""Bounded setup operations; no shell command supplied by the user."""
from __future__ import annotations

import asyncio
import base64
from contextlib import asynccontextmanager, suppress
import json
from pathlib import Path
import re
import shlex

from adb_shell.adb_device_async import AdbDeviceTcpAsync

from .reader import parse_key
from .gestures import gestures, validate_owner

PACKAGE = "de.local.tvbridge"


@asynccontextmanager
async def connection(host, port, signer):
    device = AdbDeviceTcpAsync(host, port, default_transport_timeout_s=10)
    try:
        async with asyncio.timeout(60):
            connected = await device.connect(rsa_keys=[signer], auth_timeout_s=45, read_timeout_s=50)
            if not connected:
                raise ConnectionError("not_authorized")
        yield device
    finally:
        with suppress(Exception):
            async with asyncio.timeout(5):
                await device.close()


def input_devices(inventory):
    result = []
    for block in re.split(r"add device \d+: ", inventory)[1:]:
        if re.match(r"/dev/input/event\d+", block):
            match = re.search(r'name:\s*"([^"\n]+)"', block)
            if match and match[1] not in result:
                result.append(match[1])
    return result


async def probe(host, port, signer):
    async with connection(host, port, signer) as device:
        inventory = await device.shell("getevent -lp", timeout_s=15)
        names = input_devices(inventory)
        if not names:
            raise ValueError("no_input_devices")
        return names


def app_config(bindings):
    """Only package identifiers and scan codes cross the ADB boundary."""
    result = {}
    for raw_code, binding in bindings.items():
        code = int(raw_code)
        if not 1 <= code <= 767 or code in (114, 115, 116):
            raise ValueError("protected_key")
        owner = validate_owner(binding)
        targets = {}
        for press, target in gestures(binding).items():
            package = target.get("package", "") if target.get("kind") == "app" else ""
            if package and not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+", package):
                raise ValueError("invalid_package")
            if target.get("kind") != "none":
                targets[press] = package
        result[str(code)] = targets if binding.get("gestures") and owner == "app" else targets.get("single", "")
    return result


async def sync_helper(device, bindings):
    has_gestures = any(binding.get("gestures") for binding in bindings.values())
    if has_gestures:
        capability = await device.shell("am broadcast --receiver-include-background -n " + PACKAGE
            + "/.ConfigReceiver -a " + PACKAGE + ".PROTOCOL", timeout_s=15)
        if "result=2" not in capability:
            raise RuntimeError("helper_gestures_unsupported")
    payload = json.dumps(app_config(bindings), separators=(",", ":"))
    command = ("am broadcast --receiver-include-background -n " + PACKAGE
               + "/.ConfigReceiver -a " + PACKAGE + ".CONFIGURE --es bindings " + shlex.quote(payload))
    # Versioned payload: old helpers must reject gestures instead of silently dropping them.
    if any(binding.get("gestures") for binding in bindings.values()):
        command += " --ei protocol 2"
    result = await device.shell(command, timeout_s=15)
    expected = "result=2" if any(binding.get("gestures") for binding in bindings.values()) else "result=1"
    if expected not in result:
        raise RuntimeError("helper_configuration_failed")


async def install_helper(device):
    apk = Path(__file__).parent / "assets" / "tvbridge.apk"
    if not apk.is_file():
        raise FileNotFoundError("bundled_apk_missing")
    remote = "/data/local/tmp/tv-volume-bridge.apk"
    try:
        async with asyncio.timeout(90):
            await device.push(str(apk), remote)
            result = await device.shell("pm install -r " + remote, timeout_s=60)
        if "Success" not in result:
            # No automatic uninstall: keep an existing differently signed app.
            raise RuntimeError("helper_install_failed")
    finally:
        with suppress(Exception):
            await device.shell("rm -f " + remote, timeout_s=10)
    await device.shell("am start -n " + PACKAGE + "/.MainActivity", timeout_s=15)


def input_paths(inventory):
    """Only use kernel event paths actually returned by getevent."""
    result = {}
    for block in re.split(r"add device \d+: ", inventory)[1:]:
        path = re.match(r"/dev/input/event\d+", block)
        name = re.search(r'name:\s*"([^"\n]+)"', block)
        if path and name:
            result[path[0]] = name[1]
    return result


async def detect_remote(device, seconds=20):
    """One bounded stream, no HA actions; request a short Volume Down press."""
    paths = input_paths(await device.shell("getevent -lp", timeout_s=15))
    matches = set()
    deadline = asyncio.get_running_loop().time() + seconds
    stream = device.streaming_shell("getevent -t", read_timeout_s=seconds + 2)
    pending = ""
    try:
        while (remaining := deadline - asyncio.get_running_loop().time()) > 0:
            try:
                chunk = await asyncio.wait_for(anext(stream), remaining)
            except (TimeoutError, StopAsyncIteration):
                break
            pending += chunk
            if len(pending) > 65536:
                raise ValueError("invalid_input_stream")
            while "\n" in pending:
                line, pending = pending.split("\n", 1)
                path = re.search(r"(/dev/input/event\d+):", line)
                if path and path[1] in paths and parse_key(line) == (114, "DOWN"):
                    matches.add(path[1])
                    if len(matches) == 1:
                        deadline = min(deadline, asyncio.get_running_loop().time() + 0.7)
    finally:
        await stream.aclose()
    return [paths[path] for path in sorted(matches)]


async def list_apps(device):
    """Helper returns labels using Android PackageManager, over existing ADB."""
    reply = await device.shell(
        "am broadcast --receiver-include-background -n " + PACKAGE
        + "/.ConfigReceiver -a " + PACKAGE + ".LIST_APPS", timeout_s=15)
    match = re.search(r'result=1, data="([A-Za-z0-9+/=]+)"', reply)
    if not match:
        raise RuntimeError("app_list_unavailable")
    payload = base64.b64decode(match[1], validate=True)
    if len(payload) > 262144:
        raise ValueError("app_list_too_large")
    data = json.loads(payload)
    if not isinstance(data, dict) or len(data) > 1000:
        raise ValueError("invalid_app_list")
    result = []
    for package, label in data.items():
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+", package):
            raise ValueError("invalid_package")
        if not isinstance(label, str) or not label.strip() or len(label) > 200:
            raise ValueError("invalid_app_label")
        result.append({"value": package, "label": f"{label} ({package})"})
    return sorted(result, key=lambda item: item["label"].casefold())
