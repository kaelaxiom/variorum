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

import argparse
import contextlib
import copy
import hashlib
import io
import json
import sys
import tempfile
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


class C2paBridgeTests(unittest.TestCase):
    """C2P-1..C2P-6: the bridge points at a manifest and binds only the records that claim it (ADR-0011)."""

    URN = "urn:c2pa:F9168C5E-CEB2-4FAA-B6BF-329BF39FA1E4"

    def claimed(self, **claim) -> dict:
        return record_with(extensions={"variorum:c2pa": {"manifest": self.URN, "location": "embedded", **claim}})

    def assert_rejected(self, record: dict, expected_rule: str) -> None:
        report = variorum.validate_record(record)
        rules = {issue.rule for issue in report.errors}
        self.assertFalse(report.ok, "the record should have been rejected")
        self.assertIn(expected_rule, rules, f"expected {expected_rule}, got {sorted(rules)}: {report.errors}")

    def assert_accepted(self, record: dict) -> None:
        report = variorum.validate_record(record)
        self.assertTrue(report.ok, f"the record should have been accepted: {report.errors}")

    def test_claim_must_be_an_object(self) -> None:
        for claim in ("urn:c2pa:F9168C5E-CEB2-4FAA-B6BF-329BF39FA1E4", None, []):
            with self.subTest(claim=claim):
                self.assert_rejected(record_with(extensions={"variorum:c2pa": claim}), "C2P-1")

    def test_manifest_must_be_a_c2pa_urn(self) -> None:
        for manifest in ("https://example.com/manifests/asset.c2pa", "urn:c2pa:manifest-1", "", "urn:c2pa:" + "z" * 36):
            with self.subTest(manifest=manifest):
                self.assert_rejected(self.claimed(manifest=manifest), "C2P-2")

    def test_optional_urn_components_are_opaque(self) -> None:
        for manifest in (self.URN + ":Acme", self.URN + ":Acme:2_1", self.URN + "::2_1", self.URN.lower()):
            with self.subTest(manifest=manifest):
                self.assert_accepted(self.claimed(manifest=manifest))

    def test_location_is_required_and_closed(self) -> None:
        self.assert_rejected(record_with(extensions={"variorum:c2pa": {"manifest": self.URN}}), "C2P-3")
        self.assert_rejected(self.claimed(location="sidecar"), "C2P-3")

    def test_external_manifest_requires_an_absolute_uri(self) -> None:
        self.assert_rejected(self.claimed(location="external"), "C2P-4")
        self.assert_rejected(self.claimed(location="external", uri="manifests/asset.c2pa"), "C2P-4")
        self.assert_accepted(self.claimed(location="external", uri="https://example.com/manifests/asset.c2pa"))

    def test_embedded_manifest_forbids_a_uri(self) -> None:
        self.assert_rejected(self.claimed(uri="https://example.com/manifests/asset.c2pa"), "C2P-4")

    def test_claim_defines_three_members(self) -> None:
        self.assert_rejected(self.claimed(signer="Acme"), "C2P-5")

    def test_id_stays_the_digest(self) -> None:
        record = self.claimed()
        record["id"] = self.URN
        rules = {issue.rule for issue in variorum.validate_record(record).errors}
        self.assertIn("C2P-6", rules, "the C2PA URN must never become the record's identity")
        self.assertIn("ID-7", rules)

    def test_without_the_claim_nothing_changes(self) -> None:
        self.assert_accepted(record_with())
        self.assert_accepted(record_with(extensions={"org.example:note": "x"}))


class SwhidBridgeTests(unittest.TestCase):
    """SWH-1..SWH-6: the bridge cites a sibling identifier and binds only the records that claim it (ADR-0012)."""

    FIXTURE = ROOT / "spec" / "vectors" / "fixtures" / "hello.txt"
    CONTENT = "swh:1:cnt:bad480af921edbabd43ecf18df4362aa3c3ae871"
    SNAPSHOT = "swh:1:snp:c7c108084bc0bf3d81436bf980b46e98bd338453"
    REVISION = "swh:1:rev:309cf2674ee7a0749978cf8265ab91a60aea0f7d"
    DIRECTORY = "swh:1:dir:d198bc9d7a6bcf6db04f476d29314f157507d505"

    def claimed(self, value: str = CONTENT, **claim) -> dict:
        return record_with(extensions={"variorum:swhid": {"swhid": value, **claim}})

    def assert_rejected(self, record: dict, expected_rule: str) -> None:
        report = variorum.validate_record(record)
        rules = {issue.rule for issue in report.errors}
        self.assertFalse(report.ok, "the record should have been rejected")
        self.assertIn(expected_rule, rules, f"expected {expected_rule}, got {sorted(rules)}: {report.errors}")

    def assert_accepted(self, record: dict) -> None:
        report = variorum.validate_record(record)
        self.assertTrue(report.ok, f"the record should have been accepted: {report.errors}")

    def test_the_fixture_swhid_is_recomputed_not_stored(self) -> None:
        """SWHID 1.2 §5.2: the content SWHID is SHA-1 over 'blob <size>' + NUL + the bytes.

        The base claim in spec/vectors/swhid.json is asserted against this
        computation, so the vectors cannot drift from the fixture they name.
        """
        data = self.FIXTURE.read_bytes()
        header = b"blob %d\0" % len(data)
        self.assertEqual(hashlib.sha1(header + data).hexdigest(), self.CONTENT.split(":")[-1])
        document = json.loads((ROOT / "spec" / "vectors" / "swhid.json").read_text(encoding="utf-8"))
        self.assertEqual(document["base"]["extensions"]["variorum:swhid"]["swhid"], self.CONTENT)

    def test_claim_must_be_an_object(self) -> None:
        for claim in (self.CONTENT, None, []):
            with self.subTest(claim=claim):
                self.assert_rejected(record_with(extensions={"variorum:swhid": claim}), "SWH-1")

    def test_claim_requires_the_identifier(self) -> None:
        self.assert_rejected(record_with(extensions={"variorum:swhid": {}}), "SWH-2")
        self.assert_rejected(self.claimed(""), "SWH-2")

    def test_core_identifier_shape(self) -> None:
        rejected = (
            "swh:1:cnt:bad480af",                                     # truncated hash
            "swh:2:cnt:bad480af921edbabd43ecf18df4362aa3c3ae871",      # unknown scheme version
            "swh:1:blob:bad480af921edbabd43ecf18df4362aa3c3ae871",     # git's word for the type
            "swh:1:cnt:BAD480AF921EDBABD43ECF18DF4362AA3C3AE871",      # uppercase hex
            "swh:1:cnt:bad480af921edbabd43ecf18df4362aa3c3ae871 ",     # trailing space
        )
        for value in rejected:
            with self.subTest(value=value):
                self.assert_rejected(self.claimed(value), "SWH-2")

    def test_qualifier_shape(self) -> None:
        for value in (
            self.CONTENT + ";collection=swh:1:cnt:" + "0" * 40,  # name outside §6.2/§6.3
            self.CONTENT + ";origin=",                             # empty value
            self.CONTENT + ";origin",                              # not a key/value pair
        ):
            with self.subTest(value=value):
                self.assert_rejected(self.claimed(value), "SWH-2")

    def test_visit_requires_origin_and_a_snapshot(self) -> None:
        self.assert_rejected(self.claimed(self.CONTENT + ";visit=" + self.SNAPSHOT), "SWH-4")
        self.assert_rejected(self.claimed(self.CONTENT + ";origin=https://example.com/r.git;visit=" + self.REVISION), "SWH-4")
        self.assert_accepted(self.claimed(self.CONTENT + ";origin=https://example.com/r.git;visit=" + self.SNAPSHOT))

    def test_path_is_only_for_contents_and_directories(self) -> None:
        self.assert_rejected(self.claimed(self.REVISION + ";path=/src"), "SWH-4")
        self.assert_rejected(self.claimed(self.CONTENT + ";path=src/main.c"), "SWH-4")
        self.assert_accepted(self.claimed(self.DIRECTORY + ";path=/src"))

    def test_anchor_requires_path_and_a_root_object(self) -> None:
        self.assert_rejected(self.claimed(self.CONTENT + ";anchor=" + self.REVISION), "SWH-4")
        self.assert_rejected(self.claimed(self.CONTENT + ";path=/main.c;anchor=" + self.CONTENT), "SWH-4")
        self.assert_accepted(self.claimed(self.CONTENT + ";path=/main.c;anchor=" + self.REVISION))

    def test_qualifiers_must_not_repeat(self) -> None:
        value = self.CONTENT + ";origin=https://example.com/a.git;origin=https://example.com/b.git"
        self.assert_rejected(self.claimed(value), "SWH-4")

    def test_origin_must_be_a_uri(self) -> None:
        self.assert_rejected(self.claimed(self.CONTENT + ";origin=github.com/darktable-org/darktable"), "SWH-4")
        self.assert_accepted(self.claimed(self.CONTENT + ";origin=https://example.com/x%3By.git"))

    def test_fragment_qualifiers_are_forbidden(self) -> None:
        for qualifier in ("lines=9-15", "bytes=154-315"):
            with self.subTest(qualifier=qualifier):
                self.assert_rejected(self.claimed(self.CONTENT + ";" + qualifier), "SWH-5")

    def test_the_claim_defines_one_member(self) -> None:
        record = self.claimed(self.CONTENT, resolver="https://archive.softwareheritage.org/" + self.CONTENT + "/")
        self.assert_rejected(record, "SWH-3")

    def test_identity_never_becomes_a_swhid(self) -> None:
        record = self.claimed()
        record["id"] = self.CONTENT
        rules = {issue.rule for issue in variorum.validate_record(record).errors}
        self.assertIn("SWH-6", rules, "a SWHID must never become the record's identity")
        self.assertIn("ID-7", rules)
        promoted = self.claimed()
        promoted["artifact"]["digest"] = self.CONTENT
        self.assert_rejected(promoted, "SWH-6")

    def test_a_local_check_is_not_the_record_validator_s_job(self) -> None:
        """SWH-7 binds the consumer with the bytes; a shape-valid claim is all the record can decide."""
        self.assert_accepted(self.claimed("swh:1:cnt:" + "4" * 40))

    def test_without_the_claim_nothing_changes(self) -> None:
        self.assert_accepted(record_with())
        self.assert_accepted(record_with(extensions={"org.example:note": "x"}))


class SpdxBridgeTests(unittest.TestCase):
    """SPDX-1..SPDX-6: the bridge points at a bill of materials and binds only the records that claim it (ADR-0013)."""

    FIXTURE = ROOT / "spec" / "vectors" / "fixtures" / "hello.txt"
    DOCUMENT = ROOT / "spec" / "vectors" / "fixtures" / "hello.spdx.json"
    NAMESPACE = "https://variorum.spec/spdxdocs/variorum-hello-fixture-3f2504e0-4f89-41d3-9a0c-0305e82c3301"

    def claimed(self, **claim) -> dict:
        base = {"version": "2.3", "document": self.NAMESPACE, "element": "SPDXRef-File-hello"}
        return record_with(extensions={"variorum:spdx": {**base, **claim}})

    def assert_rejected(self, record: dict, expected_rule: str) -> None:
        report = variorum.validate_record(record)
        rules = {issue.rule for issue in report.errors}
        self.assertFalse(report.ok, "the record should have been rejected")
        self.assertIn(expected_rule, rules, f"expected {expected_rule}, got {sorted(rules)}: {report.errors}")

    def assert_accepted(self, record: dict) -> None:
        report = variorum.validate_record(record)
        self.assertTrue(report.ok, f"the record should have been accepted: {report.errors}")

    def test_the_fixture_document_describes_the_fixture_file(self) -> None:
        """The equality this bridge is about, recomputed rather than stored.

        SPDX 2.3.1 §8.4: a file checksum hashes the file's bytes, so its SHA256
        can equal artifact.digest. §7.9: the package verification code is the
        SHA-1 of the sorted concatenation of the files' SHA-1 *hex strings* — a
        third value, over text, that no algorithm applied to the bytes can
        produce. Both are rebuilt here from the fixture, so neither the document
        nor the spec's table can drift silently.
        """
        document = json.loads(self.DOCUMENT.read_text(encoding="utf-8"))
        data = self.FIXTURE.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        sha1 = hashlib.sha1(data).hexdigest()

        vectors = json.loads((ROOT / "spec" / "vectors" / "spdx.json").read_text(encoding="utf-8"))
        claim = vectors["base"]["extensions"]["variorum:spdx"]
        self.assertEqual(claim["document"], document["documentNamespace"])
        self.assertEqual(claim["version"], document["spdxVersion"].removeprefix("SPDX-"))
        self.assertEqual(vectors["base"]["artifact"]["digest"], "sha256:" + digest)

        elements = {element["SPDXID"]: element for element in document["files"]}
        self.assertIn(claim["element"], elements, "the claim must name a file the document defines")
        checksums = {entry["algorithm"]: entry["checksumValue"] for entry in elements[claim["element"]]["checksums"]}
        self.assertEqual(checksums["SHA256"], digest, "the element's SHA256 is the digest, not merely like it")
        self.assertEqual(checksums["SHA1"], sha1)

        package = document["packages"][0]
        self.assertIs(package["filesAnalyzed"], True, "a verification code requires filesAnalyzed true (§7.9)")
        code = package["packageVerificationCode"]["packageVerificationCodeValue"]
        self.assertEqual(code, hashlib.sha1(sha1.encode("ascii")).hexdigest())
        self.assertNotEqual(code, digest)
        self.assertNotEqual(code, sha1)

    def test_claim_must_be_an_object(self) -> None:
        for claim in (self.NAMESPACE, None, []):
            with self.subTest(claim=claim):
                self.assert_rejected(record_with(extensions={"variorum:spdx": claim}), "SPDX-1")

    def test_version_is_required_and_closed(self) -> None:
        self.assert_rejected(self.claimed(version=None), "SPDX-2")
        for version in ("3.0.1", "2.2", "2.3.1", 2.3):
            with self.subTest(version=version):
                self.assert_rejected(self.claimed(version=version), "SPDX-2")
        self.assert_accepted(self.claimed(version="2.3"))

    def test_document_must_be_an_absolute_uri_without_a_fragment(self) -> None:
        for value in (None, "", "spdxdocs/variorum-hello", "https://variorum.spec/x#SPDXRef-File-hello", "https://variorum.spec/x y"):
            with self.subTest(document=value):
                self.assert_rejected(self.claimed(document=value), "SPDX-3")
        self.assert_accepted(self.claimed(document="urn:uuid:3f2504e0-4f89-41d3-9a0c-0305e82c3301"))

    def test_element_must_be_an_spdx_element_identifier(self) -> None:
        for value in (
            "DocumentRef-upstream:SPDXRef-File-hello",  # an element of another document (§6.6)
            "SPDXRef-",                                  # empty idstring
            "SPDXRef-File_hello",                        # underscore is not in the idstring charset (§7.2)
            "SPDXRef-File+hello",                        # '+' is allowed in DocumentRef, not here
            "spdxref-file-hello",                        # the prefix is case-sensitive
            42,
        ):
            with self.subTest(element=value):
                self.assert_rejected(self.claimed(element=value), "SPDX-4")
        self.assert_accepted(self.claimed(element="SPDXRef-3D.Printerator.v2"))

    def test_the_element_must_not_be_the_document_itself(self) -> None:
        self.assert_rejected(self.claimed(element="SPDXRef-DOCUMENT"), "SPDX-4")
        self.assert_accepted(self.claimed(element="SPDXRef-Package-hello"))

    def test_the_claim_defines_three_members(self) -> None:
        record = self.claimed(checksum="sha256:" + "a" * 64)
        self.assert_rejected(record, "SPDX-5")

    def test_identity_never_becomes_a_document_name(self) -> None:
        record = self.claimed()
        record["id"] = self.NAMESPACE
        rules = {issue.rule for issue in variorum.validate_record(record).errors}
        self.assertIn("SPDX-6", rules, "a namespace must never become the record's identity")
        self.assertIn("ID-7", rules)

        element_uri = self.claimed()
        element_uri["id"] = self.NAMESPACE + "#SPDXRef-File-hello"
        self.assert_rejected(element_uri, "SPDX-6")

        other_element = self.claimed()
        other_element["id"] = self.NAMESPACE + "#SPDXRef-Something-Else"
        self.assert_rejected(other_element, "SPDX-6")

    def test_the_claim_need_not_name_an_element(self) -> None:
        record = self.claimed()
        del record["extensions"]["variorum:spdx"]["element"]
        self.assert_accepted(record)

    def test_without_the_claim_nothing_changes(self) -> None:
        self.assert_accepted(record_with())
        self.assert_accepted(record_with(extensions={"org.example:sbom": self.NAMESPACE}))


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


class ShowTests(unittest.TestCase):
    """`show` must render every tool shape the schema allows (REC-5)."""

    def test_a_single_tool_object(self) -> None:
        self.assertEqual(
            variorum.render_tool_chain({"name": "openscad", "version": "2021.01"}),
            "openscad 2021.01",
        )

    def test_a_tool_chain(self) -> None:
        chain = [
            {"name": "openscad", "version": "2021.01"},
            {"name": "orca-slicer", "version": "2.2"},
        ]
        self.assertEqual(
            variorum.render_tool_chain(chain), "openscad 2021.01, orca-slicer 2.2"
        )

    def test_a_generative_tool_prints_its_model(self) -> None:
        self.assertEqual(
            variorum.render_tool_chain({"name": "higgsfield", "model": "grok_video"}),
            "higgsfield/grok_video",
        )

    def test_an_unknown_shape_is_not_a_crash(self) -> None:
        for value in (None, [], {}, [{}], "openscad"):
            with self.subTest(value=value):
                self.assertEqual(variorum.render_tool_chain(value), "?")

    def test_show_prints_a_chain_instead_of_a_question_mark(self) -> None:
        record = record_with(
            recipe={
                "kind": "build",
                "source": {"digest": "sha256:" + "d" * 64},
                "tool": [{"name": "openscad", "version": "2021.01"}],
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "variorum.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                variorum.command_show(argparse.Namespace(record=str(path)))
        self.assertIn("via openscad 2021.01", output.getvalue())


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
