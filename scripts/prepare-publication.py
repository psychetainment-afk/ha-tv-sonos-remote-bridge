"""Set local publication metadata; never creates remotes or contacts GitHub."""
import argparse
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--repository", required=True)
parser.add_argument("--owner", required=True)
args = parser.parse_args()
url = args.repository.rstrip("/")
if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+", url):
    parser.error("Expected a GitHub repository URL without credentials or query parameters")
if not re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)?", args.owner):
    parser.error("Expected a GitHub maintainer or organization/team identifier")
path = Path(__file__).resolve().parents[1] / "custom_components/tv_volume_bridge/manifest.json"
manifest = json.loads(path.read_text(encoding="utf-8"))
manifest.update(documentation=url, issue_tracker=url + "/issues", codeowners=["@" + args.owner])
path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print("Local metadata updated. No publication or remote change performed.")
