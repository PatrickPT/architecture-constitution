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

    def test_description_too_long(self):
        self.assertFails("longer than 1024", SKILL + "SKILL.md", 'its CI checks."', "x" * 1024 + '"')

    def test_wrapped_count(self):
        self.assertFails("'16 articles', but there are 15", "README.md", "15\n  articles", "16\n  articles")

    def test_themes_count(self):
        self.assertFails("'13 themes', but there are 12", CATALOG, "in 12 themes", "in 13 themes")

    def test_duplicate_principle(self):
        self.assertFails("principle 1 is defined twice", CATALOG, "| 2 | **High Cohesion", "| 1 | **High Cohesion")

    def test_theme_missing_from_index(self):
        self.assertFails(
            "theme 'Socio-technical' is missing from the index",
            CATALOG,
            "| [Socio-technical](#socio-technical) | 50–54 |\n",
            "",
        )

    def test_empty_cell(self):
        self.assertFails("principle 1 needs", CATALOG, "| #27: don't pre-split a small script |", "|  |")

    def test_lean_after_full(self):
        self.assertFails("article X is out of order", BASE, "### X. Contexts own their data (full;", "### X. Contexts own their data (lean;")

    def test_profile_line(self):
        self.assertFails("lean profile line must name Articles I–VIII", BASE, "Articles I–VIII.", "Articles I–VII.")

    def test_lean_range_elsewhere(self):
        self.assertFails("'Articles I–IX' is neither", "README.md", "(Articles I–VIII)", "(Articles I–IX)")

    def test_article_without_check(self):
        self.assertFails("'### I. Precedence (lean)' has no Check", BASE, "- **Check:** Plan: the Constitution Check,", "Plan:")

    def test_link_with_title(self):
        self.assertFails("link to missing nowhere.md", "README.md", "## License", '[x](nowhere.md "t")\n\n## License')

    def test_links_in_code_fences_are_text(self):
        code, out = self.run_check("README.md", "## License", "```text\n[x](nowhere.md)\n```\n\n## License")
        self.assertEqual(code, 0, out)

    def test_repeated_heading_anchor(self):
        edit = ("README.md", "## License", "[x](#license-1)\n\n## License\n\n## License")
        code, out = self.run_check(*edit)
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
