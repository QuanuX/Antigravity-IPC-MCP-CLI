#!/usr/bin/env python3
"""The release gate must reject missing, failed or skipped suites."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('qualification', ROOT / 'ci/qualify_local.py')
QUALIFICATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(QUALIFICATION)


class QualificationTests(unittest.TestCase):
    def test_complete_report_and_growing_case_counts(self):
        self.check_report(None)

    def test_incomplete_or_failed_reports_are_rejected(self):
        for mode in ('missing', 'duplicate', 'failure', 'error', 'skipped', 'notrun', 'nestedskip'):
            with self.subTest(mode=mode):
                self.check_report(mode)

    def check_report(self, mode):
        names = ('transport', 'bounded-hashing', 'mcp-integration', 'public-operation-tools', 'client-adapters', 'qualification-report')
        root = ET.Element('testsuite')
        for name in names:
            case = ET.SubElement(root, 'testcase', name=name, status='run')
            ET.SubElement(case, 'system-out').text = 'Ran 50 tests\nOK'
        if mode == 'missing': root.remove(root[3])
        elif mode == 'duplicate': ET.SubElement(root, 'testcase', name='transport', status='run')
        elif mode == 'notrun': root[0].set('status', 'notrun')
        elif mode == 'nestedskip': root[0][0].text = 'OK (skipped=1)'
        elif mode: ET.SubElement(root[0], mode)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.xml'
            ET.ElementTree(root).write(path)
            if mode:
                with self.assertRaises(RuntimeError): QUALIFICATION.validate_test_report(path)
            else: self.assertEqual(QUALIFICATION.validate_test_report(path), sorted(names))

    def test_elf_architecture_and_source_inventory(self):
        self.assertEqual(QUALIFICATION.version_tuple("cmake version 4.4.3"), (4, 4, 3))
        with tempfile.TemporaryDirectory() as tmp:
            elf_x64 = Path(tmp) / "x64.bin"
            header = bytearray(20)
            header[:6] = b"\x7fELF\x02\x01"
            struct.pack_into("<H", header, 18, 62)
            elf_x64.write_bytes(bytes(header))
            self.assertEqual(QUALIFICATION.elf_architecture(elf_x64), "x86_64")
        inventory = QUALIFICATION.source_inventory(ROOT)
        for required in ("CMakeLists.txt", "plugin.json", "mcp_config.json", "gemini-extension.json", "GEMINI.md", "rules/AGENTS.md", "catalog/tools.json"):
            self.assertIn(required, inventory)


if __name__ == '__main__':
    unittest.main()
