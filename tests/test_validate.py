#!/usr/bin/env python3
"""Tests for the Variorum reference validator.

Run with:

    python3 -m unittest discover -s tests -v

No third-party dependencies: this suite must run on a bare Python install,
for the same reason the reference tool has none.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import variorum  # noqa: E402

BASE_RECORD = {
    "variorum": "0.1",
    "id": "urn:variorum:sha256:" + "a" * 64,
    "artifact": {"digest": "sha256:" + "a" * 64, "size": 10, "mediaType": "video/mp4"},
    "scheme": {"name": "semver", "version": "1.4.2"},
    "created": "2026-11-22T12:00:00-06:00",
}


def record_with(**overrides) -> dict:
    """Return a deep copy of the base record with top-level members replaced."""
    record = copy.deepcopy(BASE_RECORD)
    record.update(overrides)
    return record


class ValidationTests(unittest.TestCase):
    def assert_rejected(self, record: dict, expected_rule: str) -> None:
        report = variorum.validate_record(record)
        self.assertFalse(report.ok, "the record should have been rejected")
        rules = {issue.rule for issue in report.issues}
        self.assertIn(expected_rule, rules, f"expected {expected_rule}, got {sorted(rules)}: {report.issues}")

    def assert_accepted(self, record: dict) -> None:
        report = variorum.validate_record(record)
        self.assertTrue(report.ok, f"the record should have been accepted: {report.issues}")

    # Core -------------------------------------------------------------- #

    def test_minimal_record_is_valid(self) -> None:
        self.assert_accepted(record_with())

    def test_unknown_members_are_ignored(self) -> None:
        self.assert_accepted(record_with(**{"com.example:future": {"anything": True}}))

    def test_record_version_format(self) -> None:
        self.assert_rejected(record_with(variorum="one"), "CORE-2")

    def test_created_requires_offset(self) -> None:
        self.assert_rejected(record_with(created="2026-11-22T12:00:00"), "CORE-5")

    # Identity ----------------------------------------------------------- #

    def test_id_must_match_digest(self) -> None:
        self.assert_rejected(record_with(id="urn:variorum:sha256:" + "b" * 64), "ID-8")

    def test_digest_must_be_sha256(self) -> None:
        self.assert_rejected(
            record_with(artifact={"digest": "md5:abc", "size": 1, "mediaType": "text/plain"}),
            "ID-2",
        )

    def test_software_producer_needs_name(self) -> None:
        self.assert_rejected(record_with(producer={"kind": "software"}), "ID-10")

    # Scheme ------------------------------------------------------------- #

    def test_scheme_none_is_valid(self) -> None:
        self.assert_accepted(record_with(scheme={"name": "none"}))

    def test_scheme_none_must_not_carry_version(self) -> None:
        self.assert_rejected(record_with(scheme={"name": "none", "version": "1.0"}), "SCH-3")

    def test_version_required_unless_none(self) -> None:
        self.assert_rejected(record_with(scheme={"name": "semver"}), "SCH-3")

    def test_custom_scheme_names_must_be_namespaced(self) -> None:
        self.assert_rejected(record_with(scheme={"name": "du-vortoj", "version": "dv-001"}), "SCH-2")

    # Lineage ------------------------------------------------------------ #

    def test_self_parent_is_rejected(self) -> None:
        self.assert_rejected(
            record_with(lineage={"parents": [{"id": BASE_RECORD["id"], "relation": "revision"}]}),
            "LIN-5",
        )

    def test_empty_parents_is_rejected(self) -> None:
        self.assert_rejected(record_with(lineage={"parents": []}), "LIN-2")

    def test_unknown_relation_is_rejected(self) -> None:
        self.assert_rejected(
            record_with(lineage={"parents": [{"id": "urn:variorum:sha256:" + "c" * 64, "relation": "upgrade"}]}),
            "LIN-4",
        )

    # Recipe ------------------------------------------------------------- #

    def test_generative_requires_prompt(self) -> None:
        self.assert_rejected(
            record_with(recipe={"kind": "generative", "tool": {"name": "x", "model": "y", "snapshot": "s"}}),
            "REC-6",
        )

    def test_generative_requires_snapshot_or_generated_at(self) -> None:
        self.assert_rejected(
            record_with(recipe={"kind": "generative", "tool": {"name": "x", "model": "y"}, "prompt": "p"}),
            "REC-8",
        )

    def test_build_requires_source(self) -> None:
        self.assert_rejected(record_with(recipe={"kind": "build", "tool": {"name": "make"}}), "REC-4")

    # State -------------------------------------------------------------- #

    def test_first_transition_must_start_at_draft(self) -> None:
        self.assert_rejected(
            record_with(state={"current": "candidate", "transitions": [
                {"from": "candidate", "to": "candidate", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"}
            ]}),
            "STA-9",
        )

    def test_illegal_contiguous_transition(self) -> None:
        self.assert_rejected(
            record_with(state={"current": "approved", "transitions": [
                {"from": "draft", "to": "approved", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"}
            ]}),
            "STA-10",
        )

    def test_current_must_equal_last_transition(self) -> None:
        self.assert_rejected(
            record_with(state={"current": "published", "transitions": [
                {"from": "draft", "to": "candidate", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"}
            ]}),
            "STA-7",
        )

    def test_superseded_requires_successor(self) -> None:
        self.assert_rejected(
            record_with(state={"current": "superseded", "transitions": [
                {"from": "draft", "to": "candidate", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"},
                {"from": "candidate", "to": "approved", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"},
                {"from": "approved", "to": "superseded", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"},
            ]}),
            "STA-12",
        )

    def test_rejected_is_terminal(self) -> None:
        self.assert_rejected(
            record_with(state={"current": "approved", "transitions": [
                {"from": "draft", "to": "candidate", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"},
                {"from": "candidate", "to": "rejected", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"},
                {"from": "rejected", "to": "approved", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"},
            ]}),
            "STA-10",
        )

    # Attestation -------------------------------------------------------- #

    def test_unknown_algorithm_is_rejected(self) -> None:
        self.assert_rejected(
            record_with(attestation={"algorithm": "md5-hmac", "signature": "abc"}),
            "ATT-5",
        )

    def test_padded_signature_is_rejected(self) -> None:
        self.assert_rejected(
            record_with(attestation={"algorithm": "ed25519", "signature": "abc=="}),
            "ATT-3",
        )


class GraphTests(unittest.TestCase):
    def test_edges_are_extracted(self) -> None:
        child = record_with(lineage={"parents": [{"id": "urn:variorum:sha256:" + "b" * 64, "relation": "revision"}]})
        edges, cycles = variorum.build_graph([child])
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0][2], "revision")
        self.assertEqual(cycles, [])

    def test_cycle_is_detected(self) -> None:
        first_id = "urn:variorum:sha256:" + "a" * 64
        second_id = "urn:variorum:sha256:" + "b" * 64
        first = record_with(id=first_id, artifact={"digest": "sha256:" + "a" * 64},
                            lineage={"parents": [{"id": second_id, "relation": "revision"}]})
        second = record_with(id=second_id, artifact={"digest": "sha256:" + "b" * 64},
                             lineage={"parents": [{"id": first_id, "relation": "revision"}]})
        _edges, cycles = variorum.build_graph([first, second])
        self.assertTrue(cycles, "a cycle should have been detected")


class ExamplesTests(unittest.TestCase):
    def test_every_shipped_example_conforms(self) -> None:
        examples = sorted((ROOT / "examples").glob("*/*.variorum.json"))
        self.assertGreaterEqual(len(examples), 3, "expected at least three shipped examples")
        for path in examples:
            with self.subTest(example=path.name):
                record = json.loads(path.read_text(encoding="utf-8"))
                report = variorum.validate_record(record)
                self.assertTrue(report.ok, f"{path}: {report.issues}")


if __name__ == "__main__":
    unittest.main()
