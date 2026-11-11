#!/usr/bin/env python3
"""Client fragment, IPC daemon, and Antigravity manifest tests."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "configure_clients.py"
BINARY = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 and Path(sys.argv[1]).exists() else None


class AdapterTests(unittest.TestCase):
    def invoke(self, client, *extra):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--client", client, *extra],
            text=True, capture_output=True, check=False,
        )

    def test_public_catalogue_survives_all_client_formats(self):
        catalog = '/opt/Review Build/catalog/tools.json'
        for client in ('codex', 'claude', 'antigravity', 'antigravity-cli', 'gemini-cli', 'generic'):
            result = self.invoke(client, '--binary', '/opt/bridge', '--config', '/tmp/config.json', '--tool-catalog', catalog)
            self.assertEqual(result.returncode, 0, result.stderr)
            parsed = tomllib.loads(result.stdout) if client == 'codex' else json.loads(result.stdout)
            server = parsed['mcp_servers' if client == 'codex' else 'mcpServers']['symphony']
            self.assertEqual(server['args'], ['--config', '/tmp/config.json', '--tool-catalog', catalog])
        rejected = self.invoke('generic', '--binary', '/opt/bridge', '--connect-socket', '/tmp/socket', '--tool-catalog', catalog)
        self.assertNotEqual(rejected.returncode, 0)

    def test_json_profiles_preserve_arguments_as_data(self):
        binary = '/opt/Alpha Build/quo"te/$literal/symphony-mcp'
        config = '/tmp/input $(literal)/connection.json'
        for client in ("claude", "antigravity", "antigravity-cli", "gemini-cli", "generic"):
            with self.subTest(client=client):
                result = self.invoke(client, "--binary", binary, "--config", config)
                self.assertEqual(result.returncode, 0, result.stderr)
                server = json.loads(result.stdout)["mcpServers"]["symphony"]
                self.assertEqual(server["command"], binary)
                self.assertEqual(server["args"], ["--config", config])
                self.assertEqual(server.get("type"), "stdio" if client == "claude" else None)

    def test_toml_roundtrip_and_socket_selection(self):
        binary = '/opt/Native "Build"/symphony-mcp'
        socket = "/tmp/alpha IPC/bridge.sock"
        result = self.invoke("codex", "--binary", binary, "--connect-socket", socket)
        self.assertEqual(result.returncode, 0, result.stderr)
        server = tomllib.loads(result.stdout)["mcp_servers"]["symphony"]
        self.assertEqual(server["command"], binary)
        self.assertEqual(server["args"], ["--connect-socket", socket])
        self.assertEqual(server["default_tools_approval_mode"], "writes")
        for client in ("antigravity", "antigravity-cli"):
            res = self.invoke(client, "--binary", binary, "--connect-socket", socket)
            self.assertEqual(res.returncode, 0, res.stderr)
            srv = json.loads(res.stdout)["mcpServers"]["symphony"]
            self.assertEqual(srv["args"], ["--connect-socket", socket])

    def test_reject_ambiguous_or_unsafe_paths(self):
        for path in ("relative/binary", "/", "/a/../b", "/a\nb", "/a\x00b"):
            if "\x00" in path:
                continue
            with self.subTest(path=path):
                result = self.invoke("generic", "--binary", path, "--config", "/tmp/config.json")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
        result = self.invoke("generic", "--binary", "/opt/bridge", "--config", "/tmp/config", "--connect-socket", "/tmp/socket")
        self.assertNotEqual(result.returncode, 0)

    def test_exclusive_private_output_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "client.json"
            args = ("--binary", "/opt/bridge", "--config", "/tmp/config", "--output", str(output))
            result = self.invoke("generic", *args)
            self.assertEqual(result.returncode, 0, result.stderr)
            original = output.read_bytes()
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            repeated = self.invoke("generic", *args)
            self.assertNotEqual(repeated.returncode, 0)
            self.assertEqual(output.read_bytes(), original)
            link = Path(directory) / "link.json"
            os.symlink(output, link)
            rejected = self.invoke("generic", *args[:-1], str(link))
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(output.read_bytes(), original)

    def test_antigravity_manifests_and_ipc_helpers(self):
        plugin = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["name"], "symphony")
        self.assertEqual(plugin["displayName"], "Symphony")
        self.assertEqual(plugin["rules"], "./rules/")
        self.assertEqual(plugin["skills"], "./skills/")
        self.assertEqual(plugin["mcpServers"], "./mcp_config.json")
        self.assertTrue((ROOT / "GEMINI.md").is_file())
        self.assertTrue((ROOT / "rules" / "AGENTS.md").is_file())
        for skill_dir in ("symphony-admin", "symphony-setup", "symphony-ipc"):
            self.assertTrue((ROOT / "skills" / skill_dir / "SKILL.md").is_file(), skill_dir)

        if BINARY is not None:
            tmp_base = "/private/tmp" if Path("/private/tmp").is_dir() else "/tmp"
            with tempfile.TemporaryDirectory(prefix="s-adm-", dir=tmp_base) as tmp:
                out = Path(tmp) / "reviewer"
                summary = json.loads(
                    subprocess.run(
                        [
                            sys.executable,
                            str(ROOT / "scripts" / "prepare_reviewer_setup.py"),
                            "--output-dir",
                            str(out),
                            "--binary",
                            str(BINARY),
                            "--smoke-fixture",
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout
                )
                self.assertEqual(summary["mode"], "smoke_fixture_not_real_symphony")
                for client_key in ("antigravity", "antigravity-cli", "gemini-cli", "codex", "claude", "generic"):
                    self.assertTrue(Path(summary["client_configs"][client_key]).is_file(), client_key)

                sock_dir = Path(tmp) / "run"
                sock_dir.mkdir(mode=0o700)
                sock_path = sock_dir / "mcp.sock"
                try:
                    started = json.loads(
                        subprocess.run(
                            [
                                sys.executable,
                                str(ROOT / "scripts" / "manage_ipc_daemon.py"),
                                "start",
                                "--binary",
                                str(BINARY),
                                "--config",
                                summary["connection_profile"],
                                "--socket",
                                str(sock_path),
                            ],
                            check=True,
                            capture_output=True,
                            text=True,
                        ).stdout
                    )
                    self.assertEqual(started["status"], "listening")
                    probed = json.loads(
                        subprocess.run(
                            [
                                sys.executable,
                                str(ROOT / "scripts" / "manage_ipc_daemon.py"),
                                "status",
                                "--socket",
                                str(sock_path),
                                "--binary",
                                str(BINARY),
                                "--probe",
                            ],
                            check=True,
                            capture_output=True,
                            text=True,
                        ).stdout
                    )
                    self.assertTrue(probed["is_socket"])
                    self.assertEqual(probed["connection_probe"]["mcp_protocol"], "2025-11-25")
                    self.assertEqual(probed["connection_probe"]["qxctl_sha256"], summary["qxctl_sha256"])
                finally:
                    subprocess.run(
                        [
                            sys.executable,
                            str(ROOT / "scripts" / "manage_ipc_daemon.py"),
                            "stop",
                            "--socket",
                            str(sock_path),
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                    )

                archive_path = Path(tmp) / "release.tar.gz"
                release = json.loads(
                    subprocess.run(
                        [
                            sys.executable,
                            str(ROOT / "scripts" / "package_release.py"),
                            "--source",
                            str(ROOT),
                            "--output",
                            str(archive_path),
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout
                )
                self.assertTrue(archive_path.is_file())
                with tarfile.open(archive_path, "r:gz") as tf:
                    names = tf.getnames()
                    self.assertIn("symphony-agent-plugin/plugin.json", names)
                    self.assertIn("symphony-agent-plugin/mcp_config.json", names)
                    self.assertIn("symphony-agent-plugin/GEMINI.md", names)
                    self.assertIn("symphony-agent-plugin/rules/AGENTS.md", names)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])
