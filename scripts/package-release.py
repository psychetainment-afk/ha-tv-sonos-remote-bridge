"""Package the checked tag without private build files or signing keys."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
tag = sys.argv[1]
version = json.loads((root / "custom_components/tv_volume_bridge/manifest.json").read_text())["version"]
if tag != "v" + version:
    raise SystemExit("Tag must match integration version")
dist = root / "dist"
dist.mkdir(exist_ok=True)
component = root / "custom_components/tv_volume_bridge"
apk = dist / "tv-sonos-remote-bridge-1.7.apk"
shutil.copyfile(component / "assets/tvbridge.apk", apk)
with zipfile.ZipFile(dist / ("tv-sonos-remote-bridge-" + version + ".zip"), "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(component.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            archive.write(path, path.relative_to(component.parent))
    archive.write(root / "NOTICE.md", "tv_volume_bridge/NOTICE.md")
subprocess.run(["git", "archive", "--format=zip", "--prefix=ha-tv-sonos-remote-bridge-" + version + "/", "-o", str(dist / ("ha-tv-sonos-remote-bridge-" + version + "-source.zip")), "HEAD"], cwd=root, check=True)
files = sorted(dist.glob("*.zip")) + [apk]
(dist / "SHA256SUMS").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name + "\n" for p in files), encoding="utf-8")
print("Packaged integration, APK, matching source and SHA256SUMS")
