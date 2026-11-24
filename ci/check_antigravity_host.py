#!/usr/bin/env python3
"""Use Google's checksum-pinned agy host to inspect the installed beta plugin."""
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import tempfile


def main():
    assets = json.loads(Path(__file__).with_name("antigravity-cli-release.json").read_text())
    host = assets[f"{platform.system()}-{platform.machine()}"]
    plugin = Path.home() / ".gemini/config/plugins/symphony"
    version = json.loads((plugin / "plugin.json").read_text())["version"]
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        archive, executable = directory / "agy.tar.gz", directory / "agy"
        subprocess.run(["curl", "--disable", "-fsSLo", str(archive), "--proto", "=https",
                        "--proto-redir", "=https", "--retry", "2", host["url"]], check=True)
        with archive.open("rb") as source:
            assert hashlib.file_digest(source, "sha512").hexdigest() == host["sha512"]
        with tarfile.open(archive) as package, executable.open("xb") as out:
            entry = package.getmember("antigravity")
            assert entry.isfile()
            shutil.copyfileobj(package.extractfile(entry), out)
        executable.chmod(0o700)
        findings = json.loads(subprocess.check_output([
            str(executable), "plugin", "validate", "--strict", "--json", str(plugin)]))
        assert not findings["findings"] and findings["components"]["mcpServers"] == 1
        plugins = json.loads(subprocess.check_output([str(executable), "plugin", "list", "--json"]))
        installed, = (item for item in plugins if item["name"] == "symphony")
        assert installed["enabled"] and installed["version"] == version
        assert installed["mcpServers"] == ["symphony"] and len(installed["rules"]) == 1
        assert set(installed["skills"]) == {"symphony-admin", "symphony-ipc", "symphony-setup"}
        print(f"Antigravity {host['version']} validated and registered Symphony {version}.")


if __name__ == "__main__":
    main()
