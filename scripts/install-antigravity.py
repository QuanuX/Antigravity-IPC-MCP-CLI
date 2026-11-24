#!/usr/bin/env python3
"""Install the released Symphony plugin for Antigravity and agy."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile


VERSION = "0.2.0-beta.2.1"
RELEASE_URL = f"https://github.com/QuanuX/Antigravity-IPC-MCP-CLI/releases/download/v{VERSION}"
# SHA-256 of each profile ZIP published alongside this installer.
ARCHIVES = {}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def cohort():
    os_name, arch = platform.system(), platform.machine().lower()
    if os_name == "Darwin":
        if platform.mac_ver()[0].split(".")[0] == "15" and arch == "arm64":
            return "macos15-arm64"
    elif os_name == "Linux":
        release = platform.freedesktop_os_release()
        cpu = {"x86_64": "amd64", "aarch64": "arm64"}.get(arch)
        profile = f"{release.get('ID')}{release.get('VERSION_ID')}-{cpu}"
        if profile in ARCHIVES:
            return profile
    raise ValueError("This host has no matching Symphony beta package. See https://quanux.org/downloads.")


def verify_server(binary, config, catalog, metadata):
    initialize = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-11-25", "capabilities": {},
        "clientInfo": {"name": "antigravity-install-check", "version": VERSION}}}
    notified = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    inspection = {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                  "params": {"name": "symphony_connection", "arguments": {}}}
    result = subprocess.run([str(binary), "--config", str(config), "--tool-catalog", str(catalog)],
        input="".join(json.dumps(row) + "\n" for row in (initialize, notified, inspection)),
        capture_output=True, text=True, timeout=45, check=True)
    initialized, connection = map(json.loads, result.stdout.splitlines())
    actual = connection["result"]["structuredContent"]
    if (initialized["result"]["serverInfo"]["version"] != VERSION
            or actual["bridge_version"] != VERSION
            or actual["qxctl_sha256"] != "sha256:" + metadata["qxctl_sha256"]
            or actual["registry_digest"] != "sha256:" + metadata["observed_registry_digest"]):
        raise ValueError("The MCP server did not confirm the selected beta installation")


def extract(archive, target):
    with zipfile.ZipFile(archive) as package:
        for member in package.infolist():
            path = Path(member.filename)
            if path.is_absolute() or ".." in path.parts or not stat.S_ISREG(member.external_attr >> 16):
                raise ValueError(f"Invalid archive entry: {member.filename}")
            out = target / path
            out.parent.mkdir(parents=True, exist_ok=True)
            with package.open(member) as src, out.open("xb") as dest:
                shutil.copyfileobj(src, dest)
            out.chmod(0o700 if member.external_attr >> 16 & 0o111 else 0o600)


def install(args):
    if os.geteuid() == 0:
        raise ValueError("Run this installer without sudo as the user who runs Antigravity.")
    profile = cohort()
    home = Path.home()
    qxctl = args.qxctl.expanduser().resolve()
    if not qxctl.is_file():
        raise ValueError(f"Install Symphony {VERSION} first at https://quanux.org/downloads or select --qxctl.")
    if args.workspace:
        workdir = args.workspace.expanduser().resolve(strict=True)
        parent = workdir / ".agents/plugins"
    else:
        workdir = home
        parent = home / ".gemini/config/plugins"
    if not workdir.is_dir():
        raise ValueError("Choose an existing workspace directory")
    target = parent / "symphony"
    data = home / ".local/share/quanux/antigravity"
    data.mkdir(mode=0o700, parents=True, exist_ok=True)
    binding = hashlib.sha256(os.fsencode(target)).hexdigest()[:24]
    os.umask(0o077)
    with (data / "install.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if os.path.lexists(target):
            receipt = target / "release-profile.json"
            if not target.is_symlink() and receipt.is_file():
                meta = json.loads(receipt.read_text())
                profile_file = data / f"{binding}-{VERSION}.json"
                if (meta.get("release") == VERSION and meta.get("profile") == profile and profile_file.is_file()
                        and json.loads(profile_file.read_text()).get("qxctl") == str(qxctl)
                        and sha(target / "bin/symphony-mcp") == meta["bridge_sha256"]
                        and sha(target / "catalog/tools.json") == meta["catalog_sha256"]):
                    verify_server(target / "bin/symphony-mcp", profile_file, target / "catalog/tools.json", meta)
                    print(f"Already installed and verified: {target}")
                    return
            raise ValueError(f"An existing plugin occupies {target}. Preserve it and choose another --workspace or move it before retrying.")
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent, prefix=".symphony-stage-") as temp:
            stage = Path(temp)
            archive = args.archive
            if archive is None:
                archive = stage / "plugin.zip"
                name = f"symphony-antigravity-{VERSION}-{profile}.zip"
                subprocess.run(["curl", "--disable", "--fail", "--silent", "--show-error", "--location",
                    "--proto", "=https", "--proto-redir", "=https", "--retry", "2", "--max-filesize", "20000000",
                    "--output", str(archive), f"{RELEASE_URL}/{name}"], check=True)
            if sha(archive) != ARCHIVES[profile]:
                raise ValueError("Plugin archive SHA-256 does not match this release and platform")
            plugin = stage / "plugin"
            plugin.mkdir(mode=0o700)
            extract(archive, plugin)
            meta = json.loads((plugin / "release-profile.json").read_text())
            if (meta["release"] != VERSION or meta["profile"] != profile or sha(qxctl) != meta["qxctl_sha256"]
                    or sha(plugin / "bin/symphony-mcp") != meta["bridge_sha256"]
                    or sha(plugin / "catalog/tools.json") != meta["catalog_sha256"]):
                raise ValueError("Plugin, catalog or qxctl does not match the selected signed Symphony cohort")
            config = data / f"{binding}-{VERSION}.json"
            with tempfile.TemporaryDirectory(dir=data) as configuration:
                pending = Path(configuration) / "connection.json"
                subprocess.run([sys.executable, "-I", str(plugin / "scripts/configure_connection.py"),
                    "--output", str(pending), "--qxctl", str(qxctl), "--working-directory", str(workdir)], check=True)
                verify_server(plugin / "bin/symphony-mcp", pending, plugin / "catalog/tools.json", meta)
                entry = {"command": str(target / "bin/symphony-mcp"),
                         "args": ["--config", str(config), "--tool-catalog", str(target / "catalog/tools.json")]}
                (plugin / "mcp_config.json").write_text(json.dumps({"mcpServers": {"symphony": entry}}, indent=2) + "\n")
                created = False
                if os.path.lexists(config):
                    if config.is_symlink() or config.read_bytes() != pending.read_bytes():
                        raise ValueError(f"Existing private connection profile differs: {config}")
                else:
                    os.link(pending, config)
                    created = True
                try:
                    plugin.rename(target)
                except OSError:
                    if created:
                        config.unlink()
                    raise
    print(f"Installed Symphony {VERSION} for Antigravity ({profile}) at {target}")
    print("MCP initialization and local qxctl binding verified. Restart the Antigravity session and open /mcp.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, help="Install for one workspace (default: user-global)")
    parser.add_argument("--qxctl", type=Path, default=Path.home() / f"symphony-{VERSION}/bin/qxctl")
    parser.add_argument("--archive", type=Path, help="Use an already downloaded matching release ZIP")
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        sys.exit("Python 3.11 or later is required.")
    try:
        install(args)
    except (ValueError, OSError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        sys.exit(f"Installation stopped: {error}")


if __name__ == "__main__":
    main()
