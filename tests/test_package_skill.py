"""The portable archive contains the skill without heavy demo assets."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_skill import package  # noqa: E402


class PackageSkillTests(unittest.TestCase):
    def test_archive_has_required_files_and_excludes_demo_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "trip-skill.zip"
            package(output)
            with ZipFile(output) as archive:
                names = set(archive.namelist())
                self.assertIn("SKILL.md", names)
                self.assertIn("assets/trip.example.json", names)
                self.assertIn("bridge/server.py", names)
                self.assertIn("scripts/validate_trip.py", names)
                self.assertNotIn("assets/workbench-overview-v2.jpg", names)
                self.assertTrue(archive.testzip() is None)


if __name__ == "__main__":
    unittest.main()
