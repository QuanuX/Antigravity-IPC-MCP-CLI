#!/usr/bin/env python3
"""Prepare an isolated local reviewer setup without touching user dotfiles."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIGURE_CONNECTION = REPO_ROOT / "scripts/configure_connection.py"
CONFIGURE_CLIENTS = REPO_ROOT / "scripts/configure_clients.py"
DEFAULT_CATALOG = REPO_ROOT / "catalog/tools.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def make_fixture_qxctl(destination: Path) -> Path:
    records = [
        {
            "command_id": "qxcmd:symphony:status",
            "status": "experimental",
            "introduced_in": "0.1.0-dev",
            "deprecated_in": None,
            "replacement_ids": [],
            "grammar": "qxctl status [--json]",
            "aliases": [],
            "visibility": "public",
            "feature_bindings": [],
            "infrastructure_purpose": "reviewer smoke fixture status",
            "backend_operation_ids": [],
            "mutability": "read_only",
            "authority_mode": "none",
            "target_scope": "local",
            "input_protocols": [],
            "output_protocols": [],
            "result_validation_protocols": [],
            "recovery_command_id": None,
            "noninteractive": True,
            "json_output": True,
        },
        {
            "command_id": "qxcmd:symphony:doctor",
            "status": "experimental",
            "introduced_in": "0.1.0-dev",
            "deprecated_in": None,
            "replacement_ids": [],
            "grammar": "qxctl doctor [--json]",
            "aliases": [],
            "visibility": "public",
            "feature_bindings": [],
            "infrastructure_purpose": "reviewer smoke fixture doctor",
            "backend_operation_ids": [],
            "mutability": "read_only",
            "authority_mode": "none",
            "target_scope": "local",
            "input_protocols": [],
            "output_protocols": [],
            "result_validation_protocols": [],
            "recovery_command_id": None,
            "noninteractive": True,
            "json_output": True,
        },
        {
            "command_id": "qxcmd:symphony:validate.scan",
            "status": "experimental",
            "introduced_in": "0.1.0-dev",
            "deprecated_in": None,
            "replacement_ids": [],
            "grammar": "qxctl validate scan [--json] [--prefix VALUE]",
            "aliases": [],
            "visibility": "public",
            "feature_bindings": [],
            "infrastructure_purpose": "reviewer smoke fixture non-read preview/apply",
            "backend_operation_ids": [],
            "mutability": "evidence_only",
            "authority_mode": "target_host_permission",
            "target_scope": "local",
            "input_protocols": [],
            "output_protocols": [],
            "result_validation_protocols": [],
            "recovery_command_id": "qxcmd:symphony:status",
            "noninteractive": True,
            "json_output": True,
        },
    ]
    script = f"""#!{sys.executable}
import hashlib, json, pathlib, sys
records = {records!r}
args = sys.argv[1:]
if args == ["commands", "manifest", "--json"]:
    doc = {{
        "protocol": "symphony.qxctl.command-registry.v1",
        "format_version": 1,
        "registry_kind": "observed",
        "client_id": "qxctl",
        "client_version": "reviewer-fixture-1",
        "client_trust": "unreceipted",
        "receipt_digest": None,
        "executable_digest": "sha256:" + hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "commands": records,
    }}
    doc["registry_digest"] = "sha256:" + hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(json.dumps(doc))
    raise SystemExit(0)
print(json.dumps({{"fixture": "reviewer_smoke_only_not_real_symphony", "argv": args}}))
"""
    destination.write_text(script, encoding="utf-8")
    destination.chmod(0o700)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path, help="New private directory to create")
    parser.add_argument("--binary", default=REPO_ROOT / "bin/symphony-mcp", type=Path, help="Compiled symphony-mcp path")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--qxctl", type=Path, help="Installed qxctl binary")
    source.add_argument("--smoke-fixture", action="store_true", help="Create an isolated self-contained qxctl smoke fixture")
    parser.add_argument("--working-directory", type=Path, help="Working directory for qxctl; defaults to the private output dir")
    parser.add_argument("--enable-nonread", action="append", default=[], help="Non-read command ID to enable in connection.json")
    args = parser.parse_args()

    out = args.output_dir.expanduser().resolve()
    if out.is_relative_to(REPO_ROOT):
        raise SystemExit("Keep --output-dir outside the repository tree")
    out.mkdir(parents=True, exist_ok=False)
    os.chmod(out, 0o700)

    binary = args.binary.expanduser().resolve(strict=True)
    mode = binary.stat().st_mode
    if not stat.S_ISREG(mode) or not os.access(binary, os.X_OK):
        raise SystemExit("--binary must be an existing executable regular file")

    if args.smoke_fixture:
        qxctl = make_fixture_qxctl(out / "qxctl-smoke-fixture")
        enabled = args.enable_nonread or ["qxcmd:symphony:validate.scan"]
        catalog = None
    else:
        qxctl = args.qxctl.expanduser().resolve(strict=True)
        enabled = args.enable_nonread
        catalog = DEFAULT_CATALOG.resolve(strict=True)

    workdir = (args.working_directory.expanduser().resolve(strict=True) if args.working_directory else out)
    connection = out / "connection.json"
    cmd = [
        sys.executable,
        str(CONFIGURE_CONNECTION),
        "--qxctl",
        str(qxctl),
        "--working-directory",
        str(workdir),
        "--output",
        str(connection),
    ]
    for item in enabled:
        cmd += ["--enable-nonread", item]
    subprocess.run(cmd, check=True)

    outputs = {
        "antigravity": out / "antigravity.mcp_config.json",
        "antigravity-cli": out / "antigravity-cli.settings.json",
        "gemini-cli": out / "gemini-cli.settings.json",
        "codex": out / "codex.config.toml",
        "claude": out / "claude.mcp.json",
        "generic": out / "generic.mcp.json",
    }
    for client, path in outputs.items():
        client_cmd = [
            sys.executable,
            str(CONFIGURE_CLIENTS),
            "--client",
            client,
            "--binary",
            str(binary),
            "--config",
            str(connection),
            "--output",
            str(path),
        ]
        if catalog is not None:
            client_cmd += ["--tool-catalog", str(catalog)]
        subprocess.run(client_cmd, check=True)

    profile = json.loads(connection.read_text(encoding="utf-8"))
    summary = {
        "mode": "smoke_fixture_not_real_symphony" if args.smoke_fixture else "installed_qxctl",
        "tool_interface": "legacy_discovery_smoke_fixture" if catalog is None else "public_operation_catalog",
        "output_directory": str(out),
        "binary": str(binary),
        "binary_sha256": sha256_file(binary),
        "connection_profile": str(connection),
        "tool_catalog": str(catalog) if catalog else None,
        "qxctl": profile["qxctl"],
        "qxctl_sha256": profile["qxctl_sha256"],
        "registry_digest": profile["registry_digest"],
        "enabled_nonread_commands": profile["enabled_nonread_commands"],
        "client_configs": {key: str(val) for key, val in outputs.items()},
    }
    (out / "SETUP-SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    os.chmod(out / "SETUP-SUMMARY.json", 0o600)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
