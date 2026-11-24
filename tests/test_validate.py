#!/usr/bin/env python3
"""Tests for the Variorum reference validator.

Run with:

    python3 -m unittest discover -s tests -v

No third-party dependencies: this suite must run on a bare Python install,
for the same reason the reference tool has none.

Two kinds of test live here: conformance (a MUST was violated and the record
must be rejected) and severity (a SHOULD was violated and the record must
remain valid, ADR-0005).
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
        rules = {issue.rule for issue in report.errors}
        self.assertIn(expected_rule, rules, f"expected an error {expected_rule}, got {sorted(rules)}: {report.errors}")

    def assert_accepted(self, record: dict) -> None:
        report = variorum.validate_record(record)
        self.assertTrue(report.ok, f"the record should have been accepted: {report.errors}")

    def assert_warning(self, record: dict, expected_rule: str) -> None:
        report = variorum.validate_record(record)
        self.assertTrue(report.ok, f"a warning must not invalidate the record: {report.errors}")
        rules = {issue.rule for issue in report.warnings}
        self.assertIn(expected_rule, rules, f"expected a warning {expected_rule}, got {sorted(rules)}")

    # Core -------------------------------------------------------------- #

    def test_minimal_record_is_valid(self) -> None:
        self.assert_accepted(record_with())

    def test_unknown_members_are_ignored(self) -> None:
        self.assert_accepted(record_with(**{"com.example:future": {"anything": True}}))

    def test_record_version_format(self) -> None:
        self.assert_rejected(record_with(variorum="one"), "CORE-2")

    def test_created_requires_offset(self) -> None:
        self.assert_rejected(record_with(created="2026-11-22T12:00:00"), "CORE-5")

    def test_generated_at_requires_offset(self) -> None:
        self.assert_rejected(
            record_with(recipe={
                "kind": "generative",
                "tool": {"name": "x", "model": "y", "snapshot": "s"},
                "prompt": "p",
                "generatedAt": "2026-11-22T12:00:00",
            }),
            "CORE-6",
        )

    def test_extensions_must_be_object(self) -> None:
        self.assert_rejected(record_with(extensions=["a"]), "CORE-9")

    def test_unnamespaced_extension_is_only_a_warning(self) -> None:
        self.assert_warning(record_with(extensions={"note": "un-namespaced"}), "CORE-10")

    # Identity ----------------------------------------------------------- #

    def test_id_must_match_digest(self) -> None:
        self.assert_rejected(record_with(id="urn:variorum:sha256:" + "b" * 64), "ID-8")

    def test_digest_must_be_sha256(self) -> None:
        self.assert_rejected(
            record_with(artifact={"digest": "md5:abc", "size": 1, "mediaType": "text/plain"}),
            "ID-2",
        )

    def test_media_type_syntax(self) -> None:
        self.assert_rejected(
            record_with(artifact={"digest": "sha256:" + "a" * 64, "mediaType": "video"}),
            "ID-5",
        )

    def test_software_producer_needs_name(self) -> None:
        self.assert_rejected(record_with(producer={"kind": "software"}), "ID-10")

    def test_software_producer_without_details_is_only_a_warning(self) -> None:
        self.assert_warning(record_with(producer={"name": "hermes-agent", "kind": "software"}), "ID-12")

    # Scheme ------------------------------------------------------------- #

    def test_scheme_none_is_valid(self) -> None:
        self.assert_accepted(record_with(scheme={"name": "none"}))

    def test_scheme_none_must_not_carry_version(self) -> None:
        self.assert_rejected(record_with(scheme={"name": "none", "version": "1.0"}), "SCH-3")

    def test_version_required_unless_none(self) -> None:
        self.assert_rejected(record_with(scheme={"name": "semver"}), "SCH-3")

    def test_scheme_name_must_be_lowercase(self) -> None:
        self.assert_rejected(record_with(scheme={"name": "DV", "version": "dv-001"}), "SCH-2")

    def test_project_scheme_name_is_valid_with_a_warning(self) -> None:
        """SCH-2 allows any lowercase name; SCH-10 merely recommends the x- prefix."""
        self.assert_warning(record_with(scheme={"name": "du-vortoj", "version": "dv-001"}), "SCH-10")

    def test_authority_must_be_an_absolute_uri(self) -> None:
        self.assert_rejected(record_with(scheme={"name": "semver", "version": "1.4.2", "authority": "semver.org"}), "SCH-4")

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

    def test_build_requires_toolchain(self) -> None:
        self.assert_rejected(record_with(recipe={"kind": "build", "source": {"ref": "https://example.org/x"}}), "REC-3")

    def test_build_tool_version_is_only_a_warning(self) -> None:
        self.assert_warning(
            record_with(recipe={
                "kind": "build",
                "source": {"ref": "https://example.org/x"},
                "tool": [{"name": "make"}],
            }),
            "REC-5",
        )

    def test_input_ref_must_be_identifiable(self) -> None:
        self.assert_rejected(
            record_with(recipe={"kind": "manual", "inputs": [{"ref": "R4-C1", "role": "start_image"}]}),
            "REC-15",
        )

    def test_hybrid_stage_must_satisfy_its_kind(self) -> None:
        self.assert_rejected(
            record_with(recipe={
                "kind": "hybrid",
                "stages": [{"kind": "generative", "tool": {"name": "x", "model": "y", "snapshot": "s"}}],
            }),
            "REC-6",
        )

    def test_unknown_determinism_is_only_a_warning(self) -> None:
        self.assert_warning(record_with(recipe={"kind": "manual", "determinism": "maybe"}), "REC-12")

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

    def test_transition_actor_must_be_an_object(self) -> None:
        self.assert_rejected(
            record_with(state={"current": "candidate", "transitions": [
                {"from": "draft", "to": "candidate", "actor": "cazucito", "at": "2026-11-22T12:00:00-06:00"}
            ]}),
            "STA-6",
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

    def test_successor_must_be_an_identifier(self) -> None:
        self.assert_rejected(
            record_with(state={"current": "superseded", "transitions": [
                {"from": "draft", "to": "candidate", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"},
                {"from": "candidate", "to": "approved", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"},
                {"from": "approved", "to": "superseded", "actor": {"name": "a"}, "at": "2026-11-22T12:00:00-06:00"},
            ], "supersededBy": "final_v2.mp4"}),
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

    def test_missing_signature_is_rejected(self) -> None:
        self.assert_rejected(record_with(attestation={"algorithm": "ed25519"}), "ATT-2")

    def test_keyid_must_be_a_string(self) -> None:
        self.assert_rejected(
            record_with(attestation={"algorithm": "ed25519", "signature": "abc", "keyid": 7}),
            "ATT-4",
        )

    # Conformance declaration -------------------------------------------- #

    def test_declaration_must_be_an_array_of_known_classes(self) -> None:
        self.assert_rejected(
            record_with(extensions={"variorum:conformance": ["core", "provenance"]}),
            "CON-5",
        )

    def test_declared_class_must_be_backed_by_its_member(self) -> None:
        self.assert_rejected(record_with(extensions={"variorum:conformance": ["core", "lineage"]}), "CON-6")

    def test_declared_class_with_member_is_accepted(self) -> None:
        self.assert_accepted(record_with(
            lineage={"parents": [{"id": "urn:variorum:sha256:" + "c" * 64, "relation": "revision"}]},
            extensions={"variorum:conformance": ["core", "lineage"]},
        ))

    def test_undeclared_class_is_only_a_warning(self) -> None:
        self.assert_warning(
            record_with(recipe={"kind": "manual", "steps": ["press"]}),
            "CORE-7",
        )


class SemverBridgeTests(unittest.TestCase):
    """SEM-1..SEM-5 and SEM-7: the bridge binds only the records that claim it (ADR-0009)."""

    def claimed(self, **scheme_overrides) -> dict:
        scheme = {"name": "semver", "version": "1.4.2", "authority": "https://semver.org/spec/v2.0.0.html"}
        scheme.update(scheme_overrides)
        return record_with(scheme=scheme, extensions={"variorum:semver": {}})

    def assert_rejected(self, record: dict, expected_rule: str) -> None:
        report = variorum.validate_record(record)
        rules = {issue.rule for issue in report.errors}
        self.assertFalse(report.ok, "the record should have been rejected")
        self.assertIn(expected_rule, rules, f"expected {expected_rule}, got {sorted(rules)}: {report.errors}")

    def assert_accepted(self, record: dict) -> None:
        report = variorum.validate_record(record)
        self.assertTrue(report.ok, f"the record should have been accepted: {report.errors}")

    def test_claim_must_be_an_object(self) -> None:
        self.assert_rejected(record_with(extensions={"variorum:semver": "1.4.2"}), "SEM-1")

    def test_claim_requires_the_semver_scheme(self) -> None:
        record = record_with(scheme={"name": "custom", "version": "1.4.2"}, extensions={"variorum:semver": {}})
        self.assert_rejected(record, "SEM-2")

    def test_version_must_match_the_semver_grammar(self) -> None:
        for version in ("v1.4.2", "1.4", "^1.4.2", "1.4.2 ", "1.4.2\n", "1.04.2", "latest"):
            with self.subTest(version=version):
                self.assert_rejected(self.claimed(version=version), "SEM-3")

    def test_prerelease_build_and_zero_are_versions(self) -> None:
        for version in ("1.4.2-rc.1", "1.4.2-rc.1+build.5", "0.0.0"):
            with self.subTest(version=version):
                self.assert_accepted(self.claimed(version=version))

    def test_sequence_is_forbidden(self) -> None:
        self.assert_rejected(self.claimed(sequence=3), "SEM-4")

    def test_tag_must_end_with_the_precedence_part(self) -> None:
        rejected = record_with(extensions={"variorum:semver": {"tag": "v1.4.1"}})
        self.assert_rejected(rejected, "SEM-5")
        empty = record_with(extensions={"variorum:semver": {"tag": ""}})
        self.assert_rejected(empty, "SEM-5")
        for tag in ("v1.4.2", "course/v1.4.2", "release-1.4.2"):
            with self.subTest(tag=tag):
                self.assert_accepted(record_with(extensions={"variorum:semver": {"tag": tag}}))

    def test_a_tag_may_omit_build_metadata(self) -> None:
        record = self.claimed(version="1.4.2+build.5")
        record["extensions"]["variorum:semver"]["tag"] = "v1.4.2"
        self.assert_accepted(record)

    def test_without_the_claim_the_label_stays_opaque(self) -> None:
        """SCH-7: 'semver' alone does not make the grammar a core rule."""
        self.assert_accepted(record_with(scheme={"name": "semver", "version": "1.4"}))
        self.assert_accepted(record_with(scheme={"name": "semver", "version": "1.4"}, extensions={"org.example:note": "x"}))

    def test_authority_is_only_a_warning(self) -> None:
        record = self.claimed()
        del record["scheme"]["authority"]
        report = variorum.validate_record(record)
        self.assertTrue(report.ok, f"a missing authority must not invalidate the record: {report.errors}")
        self.assertIn("SEM-7", {issue.rule for issue in report.warnings})


class SeverityTests(unittest.TestCase):
    def test_warnings_do_not_make_a_report_fail(self) -> None:
        report = variorum.validate_record(record_with(extensions={"note": "x"}))
        self.assertTrue(report.ok)
        self.assertEqual(report.errors, [])
        self.assertEqual(len(report.warnings), 1)
        self.assertEqual(report.warnings[0].severity, "warning")

    def test_errors_are_errors(self) -> None:
        report = variorum.validate_record(record_with(variorum="one"))
        self.assertFalse(report.ok)
        self.assertEqual([issue.severity for issue in report.errors], ["error"])


class SatisfiedClassTests(unittest.TestCase):
    def test_minimal_record_is_core(self) -> None:
        self.assertEqual(variorum.satisfied_classes(BASE_RECORD), ["core"])

    def test_members_extend_the_class_set(self) -> None:
        record = record_with(
            lineage={"parents": [{"id": "urn:variorum:sha256:" + "c" * 64, "relation": "revision"}]},
            recipe={"kind": "manual"},
        )
        self.assertEqual(variorum.satisfied_classes(record), ["core", "lineage", "recipe"])


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
                self.assertTrue(report.ok, f"{path}: {report.errors}")

    def test_every_shipped_example_declares_what_it_carries(self) -> None:
        """CON-6: the shipped examples must not over-claim."""
        for path in sorted((ROOT / "examples").glob("*/*.variorum.json")):
            with self.subTest(example=path.name):
                record = json.loads(path.read_text(encoding="utf-8"))
                declared = (record.get("extensions") or {}).get("variorum:conformance", [])
                for class_name in declared:
                    if class_name == "core":
                        continue
                    self.assertIn(class_name, record, f"{path} declares {class_name} but does not carry it")


if __name__ == "__main__":
    unittest.main()
