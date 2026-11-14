"""scripts/check.py passes on the repository and fails on each kind of drift it guards against."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = "skills/architecture-constitution/"
CATALOG = SKILL + "references/principles.md"
BASE = SKILL + "references/constitution-base.md"


class CheckTest(unittest.TestCase):
    def run_check(self, path=None, old=None, new=None):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(ROOT, tmp, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            if path:
                f = Path(tmp) / path
                text = f.read_text(encoding="utf-8")
                self.assertIn(old, text, "the edit must apply, or the test proves nothing")
                f.write_text(text.replace(old, new, 1), encoding="utf-8")
            r = subprocess.run(
                [sys.executable, "-I", str(ROOT / "scripts/check.py"), tmp],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return r.returncode, r.stdout + r.stderr

    def assertFails(self, expected, *edit):
        code, out = self.run_check(*edit)
        self.assertEqual(code, 1, out)
        self.assertIn(expected, out)

    def test_repository_passes(self):
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("ok:", out)

    def test_unknown_reference(self):
        self.assertFails("#700 is no principle", BASE, "#70", "#700")

    def test_broken_link(self):
        self.assertFails("link to missing principle.md", BASE, "(principles.md)", "(principle.md)")

    def test_broken_anchor(self):
        self.assertFails("no heading for anchor", CATALOG, "(#security--privacy)", "(#security)")

    def test_wrong_count(self):
        self.assertFails("'118 principles', but there are 119", CATALOG, "119 principles", "118 principles")

    def test_theme_index_out_of_step(self):
        self.assertFails("theme 'Structure & modularity' lists", CATALOG, "| 1–9 |", "| 1–8 |")

    def test_skill_table_misses_a_theme(self):
        self.assertFails("theme table misses", SKILL + "SKILL.md", "security 97–108", "security 97–107")

    def test_core_count(self):
        self.assertFails("'core 20', but there are 19", CATALOG, "Concerns** ★", "Concerns**")

    def test_article_order(self):
        self.assertFails("article III is out of order", BASE, "### II. ", "### III. ")

    def test_skill_name(self):
        self.assertFails("name must be", SKILL + "SKILL.md", "name: architecture-constitution", "name: arch")


if __name__ == "__main__":
    unittest.main()
