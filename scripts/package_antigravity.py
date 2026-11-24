#!/usr/bin/env python3
"""Assemble a native Antigravity plugin ZIP for a released Symphony profile."""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build(profile, binary, catalog, destination):
    release = json.loads((ROOT / "packaging/release-targets.json").read_text())
    bindings = release["profiles"][profile]
    manifest = json.loads((ROOT / "plugin.json").read_text())
    if release["version"] != manifest["version"]:
        raise ValueError("Release and plugin versions differ")
    members = {name: ROOT / name for name in (
        "plugin.json", "mcp_config.json", "LICENSE", "README.md",
        "scripts/configure_connection.py", "scripts/configure_clients.py",
        "scripts/prepare_reviewer_setup.py", "scripts/manage_ipc_daemon.py",
        "packaging/antigravity/launcher.sh")}
    for name in ("rules", "skills", "assets", "docs"):
        for path in sorted((ROOT / name).rglob("*")):
            if path.is_file():
                members[path.relative_to(ROOT).as_posix()] = path
    members["catalog/tools.json"] = catalog
    members["bin/symphony-mcp"] = binary
    payload = {}
    for name, path in members.items():
        if path.is_symlink():
            raise ValueError(f"Not a release input: {path}")
        payload[name] = path.read_bytes()
    if hashlib.sha256(payload["catalog/tools.json"]).hexdigest() != bindings["catalog_sha256"]:
        raise ValueError("Catalog differs from the signed release profile")
    metadata = {"release": release["version"], "profile": profile, **bindings,
                "bridge_sha256": hashlib.sha256(payload["bin/symphony-mcp"]).hexdigest()}
    payload["release-profile.json"] = (json.dumps(metadata, sort_keys=True, indent=2) + "\n").encode()
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(payload.items()):
            item = zipfile.ZipInfo(name, (2026, 11, 24, 0, 0, 0))
            item.create_system = 3
            mode = 0o755 if name in {"bin/symphony-mcp", "packaging/antigravity/launcher.sh"} else 0o644
            item.external_attr = (stat.S_IFREG | mode) << 16
            archive.writestr(item, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build(args.profile, args.binary, args.catalog, args.output)
