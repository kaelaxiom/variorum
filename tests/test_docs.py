"""Documentation integrity: every relative markdown link must resolve, and the
record the README shows must be a record this repository actually ships.

The specification is consumed by reading it. A dead relative link is a broken
citation in the one document a reader is asked to trust, and it is invisible to
every other check in this repository: `validate` reads JSON, `conform` reads
vectors, and neither looks at prose.

Links inside fenced code blocks and inline code spans are ignored: those are
examples of text, not citations. External URLs are not fetched — CI must not
depend on the network — but an empty or anchor-only target is skipped.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent

FENCE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\]\(([^)\s]+)")
CASE_LINK = re.compile(r"\]\(([a-z0-9-]+\.md)\)")
README_JSON = re.compile(r"^```json\n(.*?)^```", re.MULTILINE | re.DOTALL)
SKIP_DIRS = {".git", "__pycache__", ".mypy_cache", ".pytest_cache"}


def markdown_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.md") if not SKIP_DIRS & set(path.parts))


def broken_links() -> list[str]:
    failures: list[str] = []
    for path in markdown_files():
        text = FENCE.sub("", path.read_text(encoding="utf-8"))
        text = INLINE_CODE.sub("", text)
        for match in LINK.finditer(text):
            target = match.group(1).split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / unquote(target)).resolve()
            if not resolved.exists():
                line = text[: match.start()].count("\n") + 1
                failures.append(f"{path.relative_to(ROOT)}:{line} -> {target}")
    return failures


class LinkIntegrityTests(unittest.TestCase):
    def test_every_relative_link_resolves(self) -> None:
        failures = broken_links()
        self.assertEqual([], failures, "dead relative links:\n" + "\n".join(failures))

    def test_the_checker_finds_links_to_check(self) -> None:
        """Guard against a regex that silently matches nothing."""
        text = FENCE.sub("", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertGreater(len(LINK.findall(text)), 5)


class ReadmeExampleTests(unittest.TestCase):
    """The quick example is the one record most readers will copy.

    It used to be an invented skeleton, and it showed shapes the validator
    rejects — `lineage.parents` as an array of strings, `state.transitions[].actor`
    as a string — so the most visible page in the repository taught the wrong
    format. It is now a verbatim copy of a record under `examples/`, and this
    test refuses any future edit that quietly stops being one. Validity is not
    re-checked here: `ExamplesTests` validates the same bytes.
    """

    def test_quick_example_is_a_shipped_record(self) -> None:
        blocks = README_JSON.findall((ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(1, len(blocks), "README must carry exactly one ```json block")
        record = json.loads(blocks[0])
        matches = [
            path
            for path in sorted((ROOT / "examples").rglob("*.variorum.json"))
            if json.loads(path.read_text(encoding="utf-8")).get("id") == record.get("id")
        ]
        self.assertTrue(matches, "the README quick example is not a record shipped under examples/")
        shipped = json.loads(matches[0].read_text(encoding="utf-8"))
        self.assertEqual(
            shipped,
            record,
            f"README quick example drifted from {matches[0].relative_to(ROOT)}",
        )


class CaseStudyIndexTests(unittest.TestCase):
    """Every case study must be reachable from the index.

    A case study nobody links to is a document nobody reads, and the index is a
    hand-maintained table — `examples/README.md` already shipped one directory it
    did not list. Link integrity would catch a table row pointing at nothing; it
    cannot catch a file with no row.
    """

    def test_every_case_study_is_listed(self) -> None:
        index = ROOT / "docs" / "case-studies" / "README.md"
        listed = set(CASE_LINK.findall(index.read_text(encoding="utf-8")))
        files = {
            path.name
            for path in (ROOT / "docs" / "case-studies").glob("*.md")
            if path.name != "README.md"
        }
        self.assertEqual(set(), files - listed, "case studies missing from the index")
        self.assertTrue(files, "no case studies found; Phase 3 has at least one")


if __name__ == "__main__":
    unittest.main()
