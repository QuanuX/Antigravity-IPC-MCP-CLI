import argparse
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


path = Path(__file__).resolve().parents[1] / "scripts/install-antigravity.py"
spec = importlib.util.spec_from_file_location("public_installer", path)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class PublicInstallerTests(unittest.TestCase):
    def setUp(self):
        factory = tempfile.TemporaryDirectory()
        self.addCleanup(factory.cleanup)
        self.home = Path(factory.name)
        self.workspace = self.home / "project"
        self.workspace.mkdir()
        self.qxctl = self.home / "qxctl"
        self.qxctl.write_text("fixture, never executed")
        self.archive = self.home / "different.zip"
        self.archive.write_bytes(b"incorrect download")
        self.args = argparse.Namespace(workspace=self.workspace, qxctl=self.qxctl, archive=self.archive)
        self.plugin = self.workspace / ".agents/plugins/symphony"
        for override in (patch.object(Path, "home", return_value=self.home),
                         patch.object(installer, "cohort", return_value="ubuntu26.04-amd64"),
                         patch.object(installer.os, "geteuid", return_value=1000)):
            override.start()
            self.addCleanup(override.stop)

    def test_foreign_installation_preserved(self):
        self.plugin.mkdir(parents=True)
        marker = self.plugin / "owned-config"
        marker.write_bytes(b"unchanged")
        with self.assertRaisesRegex(ValueError, "existing plugin"):
            installer.install(self.args)
        self.assertEqual(marker.read_bytes(), b"unchanged")

    def test_mismatched_digest_never_commits_installation(self):
        prior_mask = installer.os.umask(0o077)
        try:
            with patch.dict(installer.ARCHIVES, {"ubuntu26.04-amd64": "a" * 64}):
                with self.assertRaisesRegex(ValueError, "SHA-256"):
                    installer.install(self.args)
        finally:
            installer.os.umask(prior_mask)
        self.assertFalse(self.plugin.exists())
        self.assertEqual(list(self.plugin.parent.glob(".symphony-stage-*")), [])


if __name__ == "__main__":
    unittest.main()
