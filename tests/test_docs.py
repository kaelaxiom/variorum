"""Documentation integrity: every relative markdown link must resolve.

The specification is consumed by reading it. A dead relative link is a broken
citation in the one document a reader is asked to trust, and it is invisible to
every other check in this repository: `validate` reads JSON, `conform` reads
vectors, and neither looks at prose.

Links inside fenced code blocks and inline code spans are ignored: those are
examples of text, not citations. External URLs are not fetched — CI must not
depend on the network — but an empty or anchor-only target is skipped.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent

FENCE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\]\(([^)\s]+)")
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


if __name__ == "__main__":
    unittest.main()
