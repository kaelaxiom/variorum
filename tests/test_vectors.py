#!/usr/bin/env python3
"""Tests for the conformance vector suite itself.

These are stricter than `variorum conform`: they require the reference tool to
cite *every* rule a reject vector lists, and they check that each fixture's
digest still matches the bytes on disk. A suite that drifts from the reference
implementation must fail here before it fails an implementer.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import variorum  # noqa: E402

VECTORS = ROOT / "spec" / "vectors"


def run_cli(*arguments: str) -> int:
    """Call the CLI in-process so the test does not depend on a shell."""
    return variorum.main(list(arguments))


class SuiteIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.vectors, cls.suite_errors = variorum.load_vectors(VECTORS)

    def test_suite_has_no_structural_errors(self) -> None:
        self.assertEqual(self.suite_errors, [], "the suite must load cleanly (CON-14..CON-22)")

    def test_suite_is_not_trivially_small(self) -> None:
        self.assertGreaterEqual(len(self.vectors), 90, "the suite should cover the specification, not a sample of it")

    def test_every_group_is_present(self) -> None:
        groups = {vector.group for vector in self.vectors}
        expected = {"core", "identity", "scheme", "lineage", "recipe", "state", "attestation", "conformance"}
        self.assertEqual(groups, expected)

    def test_every_vector_passes(self) -> None:
        for vector in self.vectors:
            with self.subTest(vector=vector.name):
                self.assertEqual(variorum.run_vector(vector), [])

    def test_reject_vectors_cite_every_listed_rule(self) -> None:
        """The reference tool must report all listed rules, not merely one of them."""
        for vector in self.vectors:
            if vector.kind != "record" or vector.expect.get("valid") is not False:
                continue
            with self.subTest(vector=vector.name):
                report = variorum.validate_record(vector.record, vector.artifact)
                cited = {issue.rule for issue in report.errors}
                missing = set(vector.expect["rules"]) - cited
                self.assertEqual(missing, set(), f"{vector.name} does not cite {sorted(missing)}")

    def test_accept_vectors_produce_no_errors(self) -> None:
        for vector in self.vectors:
            if vector.kind != "record" or vector.expect.get("valid") is not True:
                continue
            with self.subTest(vector=vector.name):
                report = variorum.validate_record(vector.record, vector.artifact)
                self.assertEqual(report.errors, [])


class FixtureTests(unittest.TestCase):
    def test_every_fixture_matches_its_record(self) -> None:
        """Recompute each declared digest from the real bytes (never trust a stored hash)."""
        checked = 0
        for path in sorted(VECTORS.glob("*.json")):
            if path.name == "exemptions.json":
                continue
            document = json.loads(path.read_text(encoding="utf-8"))
            base = document.get("base", {})
            for entry in document["vectors"]:
                if "artifact" not in entry or entry.get("fixture") is not True:
                    continue
                record = entry.get("record") or {**base, **entry.get("patch", {})}
                fixture = (path.parent / entry["artifact"]).resolve()
                with self.subTest(vector=entry["name"]):
                    self.assertTrue(fixture.is_file(), f"{fixture} is missing")
                    self.assertEqual(variorum.file_digest(fixture), record["artifact"]["digest"])
                    self.assertEqual(fixture.stat().st_size, record["artifact"]["size"])
                    checked += 1
        self.assertGreaterEqual(checked, 1, "at least one vector must check a real fixture")


class CoverageTests(unittest.TestCase):
    def test_every_rule_is_exercised_or_exempted(self) -> None:
        vectors, errors = variorum.load_vectors(VECTORS)
        self.assertEqual(errors, [])
        exemptions, exemption_errors = variorum.load_exemptions(VECTORS / "exemptions.json")
        self.assertEqual(exemption_errors, [])
        _summary, coverage_errors = variorum.coverage_report(vectors, ROOT / "spec", exemptions)
        self.assertEqual(coverage_errors, [])

    def test_exemptions_state_a_reason(self) -> None:
        document = json.loads((VECTORS / "exemptions.json").read_text(encoding="utf-8"))
        for rule, reason in document["rules"].items():
            with self.subTest(rule=rule):
                self.assertIsInstance(reason, str)
                self.assertGreaterEqual(len(reason.split()), 8, "an exemption reason must explain itself (CON-25)")

    def test_referenced_rules_exist_in_the_specification(self) -> None:
        vectors, _errors = variorum.load_vectors(VECTORS)
        defined = variorum.spec_rule_ids(ROOT / "spec")
        referenced = {
            rule for vector in vectors for rule in vector.rules if variorum.RULE_PATTERN.fullmatch(rule)
        }
        self.assertEqual(sorted(referenced - defined), [], "a vector cites a rule the spec does not define")


class CommandTests(unittest.TestCase):
    def test_conform_passes(self) -> None:
        self.assertEqual(run_cli("conform"), 0)

    def test_conform_with_coverage_passes(self) -> None:
        self.assertEqual(run_cli("conform", "--coverage"), 0)

    def test_stale_fixture_is_a_suite_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "vectors"
            shutil.copytree(VECTORS, copy)
            fixture = copy / "fixtures" / "hello.txt"
            fixture.write_bytes(fixture.read_bytes() + b"drift\n")
            self.assertEqual(run_cli("conform", "--vectors", str(copy)), 2)

    def test_a_failing_vector_returns_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "vectors"
            shutil.copytree(VECTORS, copy)
            document = json.loads((copy / "core.json").read_text(encoding="utf-8"))
            for entry in document["vectors"]:
                if entry["name"] == "core/version-is-major-minor":
                    entry["expect"] = {"valid": True}
                    break
            (copy / "core.json").write_text(json.dumps(document), encoding="utf-8")
            self.assertEqual(run_cli("conform", "--vectors", str(copy)), 1)

    def test_an_empty_suite_is_a_suite_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(run_cli("conform", "--vectors", directory), 2)


if __name__ == "__main__":
    unittest.main()
