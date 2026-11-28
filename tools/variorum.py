#!/usr/bin/env python3
"""Reference command-line tool for the Variorum specification.

The tool is deliberately dependency-free: it runs on Python 3.11+ with the
standard library alone. A standard whose reference implementation requires a
package manager is a standard that nobody runs.

Commands
--------
    variorum digest <artifact>
    variorum stamp <artifact> [options]
    variorum validate <record.json> [--artifact <artifact>]
    variorum conform [--vectors <dir>] [--coverage] [--verbose]
    variorum show <record.json>
    variorum graph <record.json>... [--mermaid]
    variorum verify <record.json> [--artifact <artifact>]

Every validation failure is reported with the rule identifier from the
specification so that an implementer can look it up. A violated MUST is an
error and makes the record non-conformant; a violated SHOULD is a warning and
does not (ADR-0005).
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

SPEC_VERSION = "0.1"
TOOL_VERSION = "0.9.0"

DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
ID_PATTERN = re.compile(r"^urn:variorum:sha256:[0-9a-f]{64}$")
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+$")
# SCH-2: any lowercase scheme name; the reserved table names carry meaning,
# everything else is opaque to a consumer. The x- prefix is a SHOULD (SCH-10).
SCHEME_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
MEDIA_TYPE_PATTERN = re.compile(r"^[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+$")
URI_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:[\S]+$")
TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")

RESERVED_SCHEMES = {
    "semver", "calver", "pep440", "debian", "rpm", "maven", "nuget",
    "date", "sequence", "custom", "none",
}
SCHEMES_WITHOUT_VERSION = {"none"}
CONFORMANCE_CLASSES = {"core", "lineage", "recipe", "attestation"}
VECTOR_KINDS = {"record", "graph", "jcs"}
VECTOR_SUITE = "variorum-vectors/1"
RELATIONS = {"generation", "revision", "edit", "render", "transcode", "fork", "restore", "derivation"}
RECIPE_KINDS = {"manual", "build", "generative", "hybrid"}
# REC-12: the determinism grades are a SHOULD-graded vocabulary, so an
# unrecognised value is a warning and never a rejection (CON-8, ADR-0005).
# `content` was added after the 3d-printerator measurement: a build can fix
# every vertex and no byte, and the record needs a way to say so (ADR-0015).
DETERMINISM_GRADES = ("none", "seeded", "content", "full")
STATES = {"draft", "candidate", "approved", "published", "superseded", "rejected", "archived"}
ACTOR_KINDS = {"human", "organization", "software"}
ALGORITHMS = {"ed25519", "ecdsa-p256-sha256", "rsa-pss-sha256"}

# --------------------------------------------------------------------------- #
# Extension bridges (spec/90-extensions/)
# --------------------------------------------------------------------------- #

SEMVER_BRIDGE = "variorum:semver"
SEMVER_AUTHORITY = "https://semver.org/spec/v2.0.0.html"
# The SemVer 2.0.0 grammar as the pattern published in the semver.org FAQ
# (normative source: the BNF appendix), anchored. re.ASCII keeps
# \d to [0-9]: SemVer is ASCII, and Python would otherwise accept any Unicode
# decimal digit. Applied only to records that claim the bridge (ADR-0009);
# every other record keeps the SCH-7 opacity.
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$",
    re.ASCII,
)

C2PA_BRIDGE = "variorum:c2pa"
C2PA_MEMBERS = {"manifest", "location", "uri"}
# C2PA 2.2 §8.1: urn:c2pa:<UUID>[:<claim generator>[:<version>_<reason>]].
# The UUID is matched in either hexadecimal case: the C2PA examples are
# uppercase, but the UUID string representations that C2PA libraries produce
# (Java's UUID.toString(), for one) are lowercase. The record stores the URN
# exactly as C2PA emitted it, so no normalisation of case is performed.
# The optional claim-generator component is opaque here: C2PA allows up to 32
# visible characters other than space, colons included, so it is matched as a
# run of non-whitespace rather than parsed.
C2PA_URN_PATTERN = re.compile(
    r"^urn:c2pa:[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"
    r"(?::[^\s]{0,32}(?::[0-9]+_[0-9]+)?)?$"
)
# RFC 3986 absolute URI: a scheme, then whatever the scheme allows.
ABSOLUTE_URI_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

SWHID_BRIDGE = "variorum:swhid"
SWHID_MEMBERS = {"swhid"}
SWHID_OBJECT_TYPES = ("cnt", "dir", "rev", "rel", "snp")
# SWHID 1.2 §6.2 and §6.3: fragment qualifiers and context qualifiers.
SWHID_QUALIFIERS = {"origin", "visit", "anchor", "path", "lines", "bytes"}
SWHID_FRAGMENT_QUALIFIERS = {"lines", "bytes"}
SWHID_ROOT_TYPES = ("dir", "rev", "rel", "snp")
# SWHID 1.2 §4, §5.1: swh:1:<type>:<40 lowercase hex digits>[;qualifier...].
# The grammar admits only 'a'-'f' in the intrinsic identifier, and the
# reference implementation (swh.model) emits lowercase, so the bridge is
# strict about case here. It is not strict about the rest of a value: §4
# takes an RFC 3987 IRI, so non-ASCII characters are legal.
SWHID_HEX = r"[0-9a-f]{40}"
SWHID_TYPE_ALTERNATION = "|".join(SWHID_OBJECT_TYPES)
SWHID_PATTERN = re.compile(
    rf"^swh:1:(?P<type>{SWHID_TYPE_ALTERNATION}):{SWHID_HEX}(?P<tail>(?:;[^;\s]+)*)$"
)
SWHID_SNAPSHOT_PATTERN = re.compile(rf"^swh:1:snp:{SWHID_HEX}$")
SWHID_ANCHOR_PATTERN = re.compile(rf"^swh:1:(?:{'|'.join(SWHID_ROOT_TYPES)}):{SWHID_HEX}$")

SPDX_BRIDGE = "variorum:spdx"
SPDX_MEMBERS = {"version", "document", "element"}
# SPDX 2.3.1 §6.1: SPDXVersion is 'SPDX-M.N'. The bridge covers the 2.3 line,
# which 2.3 and 2.3.1 share. SPDX 3.0 replaced the document model (spdxId as an
# IRI, namespaceMap, checksums behind verifiedUsing), so it is a bridge
# revision, not a lenient reading of this claim.
SPDX_VERSIONS = ("2.3",)
# §6.5: a unique absolute URI, a scheme required, and no '#' — SPDX reserves the
# fragment to build element URIs, so a namespace that carries one cannot be read
# unambiguously (§7.2, §8.2).
SPDX_DOCUMENT_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:[^\s#]+$")
# §7.2 and §8.2: 'SPDXRef-' plus an idstring of letters, digits, '.' and '-'.
# The published SPDX 2.3.1 JSON schema pins the same pattern, so prose and
# schema agree here; a '+' (allowed in DocumentRef idstrings, §6.6) is not an
# element identifier.
SPDX_ELEMENT_PATTERN = re.compile(r"^SPDXRef-[A-Za-z0-9.-]+$")
SPDX_RESERVED_ELEMENT = "SPDXRef-DOCUMENT"

PROV_BRIDGE = "variorum:prov"
PROV_MEMBERS = {"version"}
# PROV is not versioned: the family was published once, on 30 April 2013, with
# PROV-DM, PROV-O, PROV-N and PROV-CONSTRAINTS as Recommendations of that date
# and PROV-XML and PROV-AQ as Notes. A date is the only stable identifier the
# family offers, so the claim names one.
PROV_VERSIONS = ("2013",)


# STA-10: legal lifecycle transitions.
LEGAL_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"candidate", "archived"},
    "candidate": {"approved", "rejected", "draft"},
    "approved": {"published", "superseded", "archived"},
    "published": {"superseded", "archived"},
    "superseded": {"archived"},
    "rejected": set(),
    "archived": {"draft"},
}


@dataclass
class Issue:
    """One conformance finding, always tied to a rule identifier.

    ``severity`` is ``error`` for a violated MUST and ``warning`` for a
    violated SHOULD; only errors make a record non-conformant (ADR-0005).
    """

    rule: str
    message: str
    severity: str = "error"

    def __str__(self) -> str:
        return f"[{self.rule}] {self.message}"


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)

    def add(self, rule: str, message: str) -> None:
        self.issues.append(Issue(rule, message))

    def warn(self, rule: str, message: str) -> None:
        """Record a violated SHOULD. Warnings never invalidate a record."""
        self.issues.append(Issue(rule, message, severity="warning"))

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors


def file_digest(path: Path) -> str:
    """Return the sha256 digest of a file in Variorum form."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return "sha256:" + hasher.hexdigest()


def record_id_for(digest: str) -> str:
    """Derive the record identifier from an artifact digest (ID-7, ID-8)."""
    return "urn:variorum:" + digest


def is_timestamp(value: Any) -> bool:
    """True when the value is an RFC 3339 timestamp carrying an explicit offset."""
    return isinstance(value, str) and bool(TIMESTAMP_PATTERN.match(value))


def now_timestamp() -> str:
    """Current local time as an RFC 3339 timestamp with offset."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #


def validate_core(record: dict[str, Any], report: Report) -> None:
    """CORE-1..CORE-6."""
    if not isinstance(record, dict):
        report.add("CORE-1", "the record must be a JSON object")
        return

    version = record.get("variorum")
    if not isinstance(version, str) or not VERSION_PATTERN.match(version):
        report.add("CORE-2", "'variorum' must be present and formatted <major>.<minor>")

    created = record.get("created")
    if not is_timestamp(created):
        report.add("CORE-5", "'created' must be an RFC 3339 timestamp with an explicit offset")


def validate_identity(record: dict[str, Any], report: Report, artifact: Path | None) -> None:
    """ID-2..ID-12 plus the id/digest equality rule (ID-8)."""
    artifact_member = record.get("artifact")
    if not isinstance(artifact_member, dict):
        report.add("ID-1", "'artifact' must be present and must be an object")
        return

    digest = artifact_member.get("digest")
    if not isinstance(digest, str) or not DIGEST_PATTERN.match(digest):
        report.add("ID-2", "'artifact.digest' must match sha256:<64 lowercase hex>")
        digest = None

    size = artifact_member.get("size")
    if size is not None and (not isinstance(size, int) or isinstance(size, bool) or size < 0):
        report.add("ID-4", "'artifact.size' must be a non-negative integer")

    media_type = artifact_member.get("mediaType")
    if media_type is not None and (
        not isinstance(media_type, str) or not MEDIA_TYPE_PATTERN.match(media_type)
    ):
        report.add("ID-5", "'artifact.mediaType' must follow the type/subtype syntax of RFC 2046")

    record_id = record.get("id")
    if not isinstance(record_id, str) or not ID_PATTERN.match(record_id):
        report.add("ID-7", "'id' must match urn:variorum:sha256:<64 lowercase hex>")
    elif digest and record_id != record_id_for(digest):
        report.add("ID-8", f"'id' must equal urn:variorum:<digest> (expected {record_id_for(digest)})")

    producer = record.get("producer")
    if producer is not None:
        validate_actor(producer, report, "producer")

    if artifact is not None and digest:
        actual = file_digest(artifact)
        if actual != digest:
            report.add("ID-3", f"artifact digest mismatch: record says {digest}, file is {actual}")
        elif size is not None and artifact.stat().st_size != size:
            report.add("ID-4", f"artifact size mismatch: record says {size}, file is {artifact.stat().st_size}")


def validate_actor(
    actor: Any,
    report: Report,
    member: str,
    shape_rule: str = "ID-10",
    kind_rule: str = "ID-11",
) -> None:
    """The actor shape shared by producer (ID-10..ID-12) and transitions (STA-6)."""
    if not isinstance(actor, dict):
        report.add(shape_rule, f"'{member}' must be an object")
        return
    if not isinstance(actor.get("name"), str) or not actor["name"]:
        report.add(shape_rule, f"'{member}.name' must be a non-empty string")
    kind = actor.get("kind")
    if kind is not None and kind not in ACTOR_KINDS:
        report.add(kind_rule, f"'{member}.kind' must be one of {sorted(ACTOR_KINDS)}")
    if kind == "software":
        software = actor.get("software")
        if not isinstance(software, dict) or not isinstance(software.get("name"), str):
            report.warn("ID-12", f"'{member}.software' should identify the software by name")


def validate_scheme(record: dict[str, Any], report: Report) -> None:
    """SCH-1..SCH-4, SCH-8 and the SCH-10 recommendation."""
    scheme = record.get("scheme")
    if not isinstance(scheme, dict):
        report.add("SCH-1", "'scheme' must be present and must be an object")
        return

    name = scheme.get("name")
    if not isinstance(name, str) or not SCHEME_NAME_PATTERN.match(name):
        report.add("SCH-2", "'scheme.name' must be a lowercase string matching ^[a-z][a-z0-9-]*$")
        return

    version = scheme.get("version")
    if name in SCHEMES_WITHOUT_VERSION:
        if version is not None:
            report.add("SCH-3", "'scheme.version' must be absent when scheme.name is 'none'")
    elif version is None:
        report.add("SCH-3", "'scheme.version' must be present unless scheme.name is 'none'")

    authority = scheme.get("authority")
    if authority is not None and (not isinstance(authority, str) or not URI_PATTERN.match(authority)):
        report.add("SCH-4", "'scheme.authority' must be an absolute URI")

    sequence = scheme.get("sequence")
    if sequence is not None and (not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0):
        report.add("SCH-8", "'scheme.sequence' must be a non-negative integer")

    if name not in RESERVED_SCHEMES and not name.startswith("x-"):
        report.warn("SCH-10", f"scheme name '{name}' is project-specific and should carry the 'x-' prefix")


def validate_lineage(record: dict[str, Any], report: Report) -> None:
    """LIN-1..LIN-5."""
    lineage = record.get("lineage")
    if lineage is None:
        return
    if not isinstance(lineage, dict):
        report.add("LIN-1", "'lineage' must be an object")
        return

    parents = lineage.get("parents")
    if not isinstance(parents, list) or not parents:
        report.add("LIN-2", "'lineage.parents' must be a non-empty array")
        return

    own_id = record.get("id")
    for index, parent in enumerate(parents):
        if not isinstance(parent, dict):
            report.add("LIN-3", f"parents[{index}] must be an object")
            continue
        parent_id = parent.get("id")
        if not isinstance(parent_id, str) or not ID_PATTERN.match(parent_id):
            report.add("LIN-3", f"parents[{index}].id must be a Variorum identifier")
        elif own_id and parent_id == own_id:
            report.add("LIN-5", f"parents[{index}].id must not equal the record's own id")
        if parent.get("relation") not in RELATIONS:
            report.add("LIN-4", f"parents[{index}].relation must be one of {sorted(RELATIONS)}")


def validate_recipe(record: dict[str, Any], report: Report) -> None:
    """REC-1..REC-24 (the structural subset that can be checked statically)."""
    recipe = record.get("recipe")
    if recipe is None:
        return
    if not isinstance(recipe, dict):
        report.add("REC-1", "'recipe' must be an object")
        return

    validate_recipe_body(recipe, report, "recipe")


def validate_recipe_body(recipe: dict[str, Any], report: Report, path: str) -> None:
    """Rules shared by a recipe and by each stage of a hybrid recipe (REC-19)."""
    kind = recipe.get("kind")
    if kind not in RECIPE_KINDS:
        report.add("REC-2", f"'{path}.kind' must be one of {sorted(RECIPE_KINDS)}")
        return

    if kind == "build":
        source = recipe.get("source")
        if not isinstance(source, dict) or not (source.get("ref") or source.get("digest")):
            report.add("REC-4", f"a build recipe must declare '{path}.source' with a ref or a digest")
        tools = recipe.get("tool")
        if tools is None:
            report.add("REC-3", f"a build recipe must declare '{path}.tool' (the toolchain)")
        else:
            tool_list = tools if isinstance(tools, list) else [tools]
            if not tool_list:
                report.add("REC-3", f"'{path}.tool' must identify at least one tool")
            for index, tool in enumerate(tool_list):
                if not isinstance(tool, dict) or not isinstance(tool.get("name"), str) or not tool.get("name"):
                    report.add("REC-3", f"'{path}.tool[{index}]' must identify the tool by name")
                elif not tool.get("version"):
                    report.warn("REC-5", f"'{path}.tool[{index}]' should identify the tool version")

    if kind == "generative":
        tool = recipe.get("tool")
        has_tool = isinstance(tool, dict) and bool(tool.get("name")) and bool(tool.get("model"))
        if not has_tool:
            report.add("REC-7", f"a generative recipe must declare '{path}.tool' with name and model")
        has_snapshot = isinstance(tool, dict) and tool.get("snapshot") is not None
        if not has_snapshot and recipe.get("generatedAt") is None:
            report.add("REC-8", f"a generative recipe must record '{path}.tool.snapshot' or 'generatedAt'")
        if not isinstance(recipe.get("prompt"), str):
            report.add("REC-6", f"a generative recipe must record the prompt verbatim in '{path}.prompt'")

    if kind == "hybrid":
        stages = recipe.get("stages")
        if not isinstance(stages, list) or not stages:
            report.add("REC-19", f"a hybrid recipe must declare '{path}.stages'")
        else:
            for index, stage in enumerate(stages):
                stage_path = f"{path}.stages[{index}]"
                if not isinstance(stage, dict) or stage.get("kind") not in {"build", "generative"}:
                    report.add("REC-19", f"'{stage_path}.kind' must be 'build' or 'generative'")
                    continue
                validate_recipe_body(stage, report, stage_path)

    # REC-24: promptField connects `prompt` to the generator's own vocabulary
    # (REC-23). Its shape is checkable; whether the provider has a field by that
    # name is not, which is why REC-23 is a SHOULD and draws no warning here.
    if "promptField" in recipe:
        prompt_field = recipe.get("promptField")
        if not isinstance(prompt_field, str) or not prompt_field.strip():
            report.add("REC-24", f"'{path}.promptField' must be a non-empty string naming the generator's field")
        if not isinstance(recipe.get("prompt"), str):
            report.add("REC-24", f"'{path}.promptField' must not appear without '{path}.prompt'")

    inputs = recipe.get("inputs")
    if inputs is not None:
        if not isinstance(inputs, list):
            report.add("REC-14", f"'{path}.inputs' must be an array")
        else:
            for index, item in enumerate(inputs):
                if not isinstance(item, dict) or not item.get("ref") or not item.get("role"):
                    report.add("REC-14", f"'{path}.inputs[{index}]' must carry 'ref' and 'role'")
                elif not (ID_PATTERN.match(str(item["ref"])) or URI_PATTERN.match(str(item["ref"]))):
                    report.add("REC-15", f"'{path}.inputs[{index}].ref' must be a Variorum id or an absolute URI")

    determinism = recipe.get("determinism")
    if determinism is not None and determinism not in DETERMINISM_GRADES:
        grades = ", ".join(DETERMINISM_GRADES[:-1]) + " or " + DETERMINISM_GRADES[-1]
        report.warn("REC-12", f"'{path}.determinism' should be one of {grades}")
    if determinism == "content":
        parameters = recipe.get("parameters")
        normalization = parameters.get("normalization") if isinstance(parameters, dict) else None
        if not isinstance(normalization, str) or not normalization.strip():
            report.warn(
                "REC-22",
                f"'{path}.parameters.normalization' should state how two executions of a content-deterministic recipe are compared",
            )

    generated_at = recipe.get("generatedAt")
    if generated_at is not None and not is_timestamp(generated_at):
        report.add("CORE-6", f"'{path}.generatedAt' must be an RFC 3339 timestamp with an explicit offset")


def validate_state(record: dict[str, Any], report: Report) -> None:
    """STA-2..STA-12."""
    state = record.get("state")
    if state is None:
        return
    if not isinstance(state, dict):
        report.add("STA-1", "'state' must be an object")
        return

    current = state.get("current")
    if current not in STATES:
        report.add("STA-2", f"'state.current' must be one of {sorted(STATES)}")

    transitions = state.get("transitions")
    if not isinstance(transitions, list):
        report.add("STA-3", "'state.transitions' must be an array (it may be empty)")
        transitions = []

    previous_to: str | None = None
    for index, transition in enumerate(transitions):
        if not isinstance(transition, dict):
            report.add("STA-4", f"transitions[{index}] must be an object")
            continue
        for member in ("from", "to", "actor", "at"):
            if member not in transition:
                report.add("STA-4", f"transitions[{index}] is missing '{member}'")
        if not is_timestamp(transition.get("at")):
            report.add("STA-5", f"transitions[{index}].at must be an RFC 3339 timestamp with offset")
        if isinstance(transition.get("actor"), dict):
            validate_actor(transition["actor"], report, f"transitions[{index}].actor", shape_rule="STA-6")
        elif "actor" in transition:
            report.add("STA-6", f"transitions[{index}].actor must identify the decision-maker")

        source_state = transition.get("from")
        target_state = transition.get("to")
        if index == 0 and source_state != "draft":
            report.add("STA-9", "the first transition must start from 'draft'")
        if previous_to is not None and source_state != previous_to:
            report.add("STA-8", f"transitions[{index}] starts from '{source_state}' but the previous one ended in '{previous_to}'")
        if source_state in STATES and target_state in STATES and target_state not in LEGAL_TRANSITIONS[source_state]:
            report.add("STA-10", f"illegal transition {source_state} -> {target_state}")
        previous_to = target_state

    if current in STATES:
        if transitions:
            last_to = transitions[-1].get("to") if isinstance(transitions[-1], dict) else None
            if last_to != current:
                report.add("STA-7", f"'state.current' is '{current}' but the last transition ends in '{last_to}'")
        elif current != "draft":
            report.add("STA-7", "'state.current' must be 'draft' when there are no transitions")

    if current == "superseded":
        successor = state.get("supersededBy")
        if not isinstance(successor, str) or not ID_PATTERN.match(successor):
            report.add("STA-12", "'state.supersededBy' must be a Variorum identifier when the state is 'superseded'")


def validate_attestation(record: dict[str, Any], report: Report) -> None:
    """ATT-1..ATT-5."""
    attestation = record.get("attestation")
    if attestation is None:
        return
    if isinstance(attestation, str) or not isinstance(attestation, (dict, list)):
        report.add("ATT-1", "'attestation' must be an object or an array of objects")
        return
    entries = attestation if isinstance(attestation, list) else [attestation]
    if isinstance(attestation, list) and not entries:
        report.add("ATT-1", "'attestation' must not be an empty array")
        return
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            report.add("ATT-1", f"attestation[{index}] must be an object")
            continue
        if "algorithm" not in entry or "signature" not in entry:
            report.add("ATT-2", f"attestation[{index}] must carry 'algorithm' and 'signature'")
        if "algorithm" in entry and entry.get("algorithm") not in ALGORITHMS:
            report.add("ATT-5", f"attestation[{index}].algorithm must be one of {sorted(ALGORITHMS)}")
        signature = entry.get("signature")
        if "signature" in entry and (not isinstance(signature, str) or not re.match(r"^[A-Za-z0-9_-]+$", signature)):
            report.add("ATT-3", f"attestation[{index}].signature must be base64url without padding")
        keyid = entry.get("keyid")
        if "keyid" in entry and not isinstance(keyid, str):
            report.add("ATT-4", f"attestation[{index}].keyid must be a string")


def validate_declaration(record: dict[str, Any], report: Report) -> None:
    """CON-5, CON-6 and the CORE-7 recommendation about extensions["variorum:conformance"]."""
    extensions = record.get("extensions")
    declared = extensions.get("variorum:conformance") if isinstance(extensions, dict) else None

    if declared is not None:
        if not isinstance(declared, list) or not all(isinstance(item, str) for item in declared):
            report.add("CON-5", "'variorum:conformance' must be an array of class names")
        else:
            unknown = [item for item in declared if item not in CONFORMANCE_CLASSES]
            if unknown:
                report.add("CON-5", f"unknown conformance class {unknown}; expected a subset of {sorted(CONFORMANCE_CLASSES)}")
            for class_name in declared:
                if class_name in CONFORMANCE_CLASSES and class_name != "core" and record.get(class_name) is None:
                    report.add("CON-6", f"the record declares '{class_name}' but carries no '{class_name}' member")

    declared_names = set(declared) if isinstance(declared, list) and all(isinstance(item, str) for item in declared) else set()
    for class_name in ("lineage", "recipe", "attestation"):
        if record.get(class_name) is not None and class_name not in declared_names:
            report.warn("CORE-7", f"the record carries '{class_name}' but does not declare the '{class_name}' class")


def validate_extensions(record: dict[str, Any], report: Report) -> None:
    """CORE-9..CORE-11."""
    extensions = record.get("extensions")
    if extensions is None:
        return
    if not isinstance(extensions, dict):
        report.add("CORE-9", "'extensions' must be an object")
        return
    for key in extensions:
        if ":" not in key:
            report.warn("CORE-10", f"extension key '{key}' should be namespaced with a '<prefix>:<name>' form")


def validate_semver_bridge(record: dict[str, Any], report: Report) -> None:
    """SEM-1..SEM-5 and SEM-7 (spec/90-extensions/semver.md).

    The bridge is opt-in: only a record carrying ``extensions["variorum:semver"]``
    is held to these rules. Every other record keeps the SCH-7 opacity, so a
    core implementation that does not implement this bridge is not affected.
    """
    extensions = record.get("extensions")
    if not isinstance(extensions, dict):
        return
    if SEMVER_BRIDGE not in extensions:
        return
    claim = extensions[SEMVER_BRIDGE]
    if not isinstance(claim, dict):
        report.add("SEM-1", "'variorum:semver' must be an object")
        return

    scheme = record.get("scheme")
    scheme = scheme if isinstance(scheme, dict) else {}
    name = scheme.get("name")
    version = scheme.get("version")

    if name != "semver":
        report.add("SEM-2", f"a SemVer bridge claim requires scheme.name 'semver', found {name!r}")

    if name == "semver":
        if not isinstance(version, str):
            report.add("SEM-3", "'scheme.version' must be present and carry a SemVer 2.0.0 version")
        elif not SEMVER_PATTERN.fullmatch(version):
            report.add(
                "SEM-3",
                f"'{version}' is not a SemVer 2.0.0 version: a range, a tag prefix, a partial version "
                "and surrounding whitespace are not versions",
            )
        if scheme.get("authority") != SEMVER_AUTHORITY:
            report.warn("SEM-7", f"a SemVer bridge record should name its authority: {SEMVER_AUTHORITY}")

    if "sequence" in scheme:
        report.add("SEM-4", "a SemVer bridge record must not carry 'scheme.sequence': SemVer defines the order")

    tag = claim.get("tag")
    if tag is not None:
        if not isinstance(tag, str) or not tag or any(character.isspace() for character in tag):
            report.add("SEM-5", "'tag' must be a non-empty string without whitespace")
        elif isinstance(version, str):
            precedence = version.split("+", 1)[0]
            if not tag.endswith(precedence):
                report.add("SEM-5", f"tag {tag!r} does not end with the release version {precedence!r}")


def validate_c2pa_bridge(record: dict[str, Any], report: Report) -> None:
    """C2P-1..C2P-6 (spec/90-extensions/c2pa.md).

    The claim is a pointer to a C2PA manifest, never a copy of it. Only records
    carrying ``extensions["variorum:c2pa"]`` are held to these rules; a record
    for an artifact that happens to carry a manifest, without the claim, says
    nothing about it (ADR-0011).
    """
    extensions = record.get("extensions")
    if not isinstance(extensions, dict):
        return
    if C2PA_BRIDGE not in extensions:
        return
    claim = extensions[C2PA_BRIDGE]
    if not isinstance(claim, dict):
        report.add("C2P-1", "'variorum:c2pa' must be an object")
        return

    manifest = claim.get("manifest")
    if not isinstance(manifest, str) or not manifest:
        report.add("C2P-2", "'manifest' must carry the urn:c2pa: URN of the active manifest")
    elif not C2PA_URN_PATTERN.fullmatch(manifest):
        report.add(
            "C2P-2",
            f"{manifest!r} is not a urn:c2pa: URN: expected 'urn:c2pa:' followed by a UUID, "
            "with the optional claim-generator and version-reason components C2PA defines",
        )

    location = claim.get("location")
    if location not in ("embedded", "external"):
        report.add("C2P-3", "'location' must be 'embedded' or 'external'")

    uri = claim.get("uri")
    if location == "external":
        if uri is None:
            report.add("C2P-4", "an external manifest requires 'uri': without it the manifest cannot be located")
        elif not isinstance(uri, str) or not ABSOLUTE_URI_PATTERN.match(uri):
            report.add("C2P-4", f"{uri!r} is not an absolute URI reference")
    elif location == "embedded" and "uri" in claim:
        report.add("C2P-4", "an embedded manifest must not carry 'uri': the bytes carry the manifest")

    unknown = sorted(set(claim) - C2PA_MEMBERS)
    if unknown:
        report.add("C2P-5", f"the C2PA claim defines 'manifest', 'location' and 'uri' only; found {unknown}")

    record_id = record.get("id")
    if isinstance(record_id, str) and record_id.startswith("urn:c2pa:"):
        report.add(
            "C2P-6",
            "'id' must stay the urn:variorum: identifier derived from artifact.digest; "
            "the C2PA URN belongs in extensions['variorum:c2pa'].manifest",
        )


def validate_swhid_bridge(record: dict[str, Any], report: Report) -> None:
    """SWH-1..SWH-6 (spec/90-extensions/swhid.md).

    The bridge cites a Software Heritage identifier as a sibling claim, never
    as the artifact's identity. Only records carrying
    ``extensions["variorum:swhid"]`` are held to these rules; a record for an
    archived artifact without the claim says nothing about the archive
    (ADR-0012).
    """
    extensions = record.get("extensions")
    if not isinstance(extensions, dict):
        return
    if SWHID_BRIDGE not in extensions:
        return
    claim = extensions[SWHID_BRIDGE]
    if not isinstance(claim, dict):
        report.add("SWH-1", "'variorum:swhid' must be an object")
        return

    unknown = sorted(set(claim) - SWHID_MEMBERS)
    if unknown:
        report.add("SWH-3", f"the SWHID claim defines 'swhid' only; found {unknown}")

    # SWH-6 before the claim's own shape, so that a record which promoted an
    # identifier to its identity is told why even when the claim is malformed.
    record_id = record.get("id")
    if isinstance(record_id, str) and record_id.startswith("swh:"):
        report.add(
            "SWH-6",
            "'id' must stay the urn:variorum: identifier derived from artifact.digest; "
            "a SWHID is a sibling identifier, and a reader cannot recompute it from the bytes",
        )
    artifact = record.get("artifact")
    digest = artifact.get("digest") if isinstance(artifact, dict) else None
    if isinstance(digest, str) and digest.startswith("swh:"):
        report.add(
            "SWH-6",
            "'artifact.digest' must be 'sha256:' over the artifact's bytes; a SWHID hashes "
            "a different pre-image, header and algorithm included",
        )

    value = claim.get("swhid")
    if not isinstance(value, str) or not value:
        report.add("SWH-2", "'swhid' must carry one SWHID of scheme version 1")
        return
    if any(character.isspace() for character in value):
        report.add("SWH-2", f"{value!r} contains whitespace: a SWHID is a token, not prose")
        return
    match = SWHID_PATTERN.fullmatch(value)
    if match is None:
        report.add(
            "SWH-2",
            f"{value!r} is not a SWHID of scheme version 1: expected 'swh:1:', an object type "
            "('cnt', 'dir', 'rev', 'rel' or 'snp'), 40 lowercase hexadecimal digits, and "
            "optional ';name=value' qualifiers",
        )
        return

    object_type = match.group("type")
    qualifiers: dict[str, str] = {}
    for part in match.group("tail").split(";"):
        if not part:
            continue
        name, separator, qualifier_value = part.partition("=")
        if not separator or name not in SWHID_QUALIFIERS or not qualifier_value:
            report.add(
                "SWH-2",
                f"{part!r} is not a SWHID qualifier: expected 'name=value' with a non-empty "
                "value and a name among origin, visit, anchor, path, lines, bytes",
            )
            continue
        if name in qualifiers:
            report.add("SWH-4", f"qualifier {name!r} appears more than once; SWHID allows each at most once")
            continue
        qualifiers[name] = qualifier_value

    fragments = sorted(set(qualifiers) & SWHID_FRAGMENT_QUALIFIERS)
    if fragments:
        report.add(
            "SWH-5",
            f"fragment qualifier {fragments[0]!r} narrows the SWHID to part of a content; a record "
            "identifies one whole artifact, and a fragment belongs in a namespaced extension",
        )

    visit = qualifiers.get("visit")
    if visit is not None:
        if "origin" not in qualifiers:
            report.add("SWH-4", "'visit' requires 'origin': a snapshot of branches has no meaning without its repository")
        if not SWHID_SNAPSHOT_PATTERN.fullmatch(visit):
            report.add("SWH-4", f"visit {visit!r} must be the core SWHID of a snapshot ('swh:1:snp:...')")

    path = qualifiers.get("path")
    if path is not None:
        if object_type not in ("cnt", "dir"):
            report.add("SWH-4", f"'path' is only valid for content and directory objects, not for a {object_type!r} object")
        elif not path.startswith("/"):
            report.add("SWH-4", f"path {path!r} must be absolute: a SWHID path names a location below a root directory")

    anchor = qualifiers.get("anchor")
    if anchor is not None:
        if "path" not in qualifiers:
            report.add("SWH-4", "'anchor' requires 'path': the anchor is the node the path is read from")
        if not SWHID_ANCHOR_PATTERN.fullmatch(anchor):
            report.add("SWH-4", f"anchor {anchor!r} must be the core SWHID of a directory, revision, release or snapshot")

    origin = qualifiers.get("origin")
    if origin is not None and not ABSOLUTE_URI_PATTERN.match(origin):
        report.add("SWH-4", f"origin {origin!r} is not a URI: it must begin with a scheme such as 'https:'")


def validate_spdx_bridge(record: dict[str, Any], report: Report) -> None:
    """SPDX-1..SPDX-6 (spec/90-extensions/spdx.md).

    The claim is a pointer at a bill of materials, never a copy of one of its
    checksums: SPDX carries checksums in the same algorithms Variorum uses, so a
    copy would often be numerically right while being a statement the record is
    not entitled to make. Only records carrying
    ``extensions["variorum:spdx"]`` are held to these rules; a record for an
    artifact that happens to be listed in an SBOM, without the claim, says
    nothing about the SBOM (ADR-0013).
    """
    extensions = record.get("extensions")
    if not isinstance(extensions, dict):
        return
    if SPDX_BRIDGE not in extensions:
        return
    claim = extensions[SPDX_BRIDGE]
    if not isinstance(claim, dict):
        report.add("SPDX-1", "'variorum:spdx' must be an object")
        return

    unknown = sorted(set(claim) - SPDX_MEMBERS)
    if unknown:
        report.add(
            "SPDX-5",
            f"the SPDX claim defines 'version', 'document' and 'element' only; found {unknown}",
        )

    version = claim.get("version")
    if version not in SPDX_VERSIONS:
        report.add(
            "SPDX-2",
            "'version' must be '2.3', the SPDXVersion this bridge is written against: "
            "SPDX 3.0 replaced the document model and needs its own bridge",
        )

    document = claim.get("document")
    if not isinstance(document, str) or not document:
        report.add("SPDX-3", "'document' must carry the SPDX document namespace")
        document = None
    elif not SPDX_DOCUMENT_PATTERN.fullmatch(document):
        report.add(
            "SPDX-3",
            f"{document!r} is not a document namespace: expected an absolute URI with a scheme "
            "and no '#', which SPDX reserves for element URIs",
        )

    element = claim.get("element")
    if element is not None:
        if not isinstance(element, str) or not SPDX_ELEMENT_PATTERN.fullmatch(element):
            report.add(
                "SPDX-4",
                f"{element!r} is not an SPDX element identifier: expected 'SPDXRef-' followed by "
                "letters, digits, '.' or '-'",
            )
        elif element == SPDX_RESERVED_ELEMENT:
            report.add(
                "SPDX-4",
                "'SPDXRef-DOCUMENT' names the document itself, which is not one of the things it "
                "describes; omit 'element' to point at the document without naming an element",
            )

    record_id = record.get("id")
    if isinstance(record_id, str) and isinstance(document, str):
        if record_id == document or record_id.startswith(document + "#"):
            report.add(
                "SPDX-6",
                "'id' must stay the urn:variorum: identifier derived from artifact.digest; "
                "a namespace or an element URI changes when the document is reissued and no "
                "reader can recompute it from the artifact's bytes",
            )


def validate_prov_bridge(record: dict[str, Any], report: Report) -> None:
    """PROV-1..PROV-3 (spec/90-extensions/prov.md).

    A projection, not a pointer: PROV gives a document no required identity
    (PROV-CONSTRAINTS §1.2) and reserves no attribute that hashes bytes (§5.7.2),
    so the claim carries one member — the edition the projection follows — and
    nothing that could be copied or resolved. Only records carrying
    ``extensions["variorum:prov"]`` are held to these rules; a record for an
    artifact that appears in a PROV graph, without the claim, says nothing about
    the graph (ADR-0014).
    """
    extensions = record.get("extensions")
    if not isinstance(extensions, dict):
        return
    if PROV_BRIDGE not in extensions:
        return
    claim = extensions[PROV_BRIDGE]
    if not isinstance(claim, dict):
        report.add("PROV-1", "'variorum:prov' must be an object carrying 'version'")
        return

    unknown = sorted(set(claim) - PROV_MEMBERS)
    if unknown:
        report.add(
            "PROV-3",
            f"the PROV claim defines 'version' only; found {unknown}. PROV names no document and "
            "hashes no bytes, so a 'document' or 'checksum' member would point at something no "
            "reader can resolve (spec/90-extensions/prov.md 90.8)",
        )

    version = claim.get("version")
    if version not in PROV_VERSIONS:
        report.add(
            "PROV-2",
            "'version' must be '2013', the PROV family recommended on 30 April 2013: the family "
            "was published once, so a date is the only edition there is",
        )


def validate_record(record: Any, artifact: Path | None = None) -> Report:
    """Run every applicable rule and collect the findings."""
    report = Report()
    if not isinstance(record, dict):
        report.add("CORE-1", "the record must be a JSON object")
        return report

    validate_core(record, report)
    validate_identity(record, report, artifact)
    validate_scheme(record, report)
    validate_lineage(record, report)
    validate_recipe(record, report)
    validate_state(record, report)
    validate_attestation(record, report)
    validate_extensions(record, report)
    validate_declaration(record, report)
    validate_semver_bridge(record, report)
    validate_c2pa_bridge(record, report)
    validate_swhid_bridge(record, report)
    validate_spdx_bridge(record, report)
    validate_prov_bridge(record, report)
    return report


# --------------------------------------------------------------------------- #
# Attestation verification
# --------------------------------------------------------------------------- #


def canonicalise(record: dict[str, Any]) -> bytes:
    """Return the bytes that are signed: JCS of the record without 'attestation'.

    RFC 8785 sorts object keys lexicographically and serialises without
    insignificant whitespace. Python's json module with sort_keys and compact
    separators matches JCS for the value types this specification permits
    (no floats are used for identifiers, and timestamps are strings).
    """
    payload = {key: value for key, value in record.items() if key != "attestation"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify_attestation(record: dict[str, Any]) -> Report:
    """ATT-4..ATT-8. Requires the optional 'cryptography' package."""
    report = Report()
    attestation = record.get("attestation")
    if attestation is None:
        report.add("ATT-1", "the record carries no attestation")
        return report

    try:
        from cryptography.exceptions import InvalidSignature  # noqa: F401
        from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa
        from cryptography.hazmat.primitives import hashes
    except ImportError:
        report.add("ATT-0", "verification requires the optional 'cryptography' package; validation alone does not")
        return report

    report.add("ATT-0", "verification needs the signer's public key, which this tool does not resolve; supply it through your own key distribution")
    return report


# --------------------------------------------------------------------------- #
# Graph
# --------------------------------------------------------------------------- #


def build_graph(records: Iterable[dict[str, Any]]) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Return edges (parent, child, relation) and any cycle detected."""
    edges: list[tuple[str, str, str]] = []
    known = {record.get("id"): record for record in records if isinstance(record.get("id"), str)}
    for record in records:
        child = record.get("id")
        if not isinstance(child, str):
            continue
        lineage = record.get("lineage") or {}
        for parent in lineage.get("parents", []) or []:
            if isinstance(parent, dict) and isinstance(parent.get("id"), str):
                relation = str(parent.get("relation") or "derivation")
                edges.append((parent["id"], child, relation))

    cycles: list[str] = []
    adjacency: dict[str, list[str]] = {}
    for parent, child, _relation in edges:
        adjacency.setdefault(parent, []).append(child)

    def walk(node: str, path: list[str], seen: set[str]) -> None:
        for neighbour in adjacency.get(node, []):
            if neighbour in path:
                cycles.append(" -> ".join(path + [neighbour]))
                return
            if neighbour in seen:
                continue
            seen.add(neighbour)
            walk(neighbour, path + [neighbour], seen)

    for node in adjacency:
        walk(node, [node], set())
    return edges, cycles


# --------------------------------------------------------------------------- #
# Conformance suite (spec/07-conformance.md)
# --------------------------------------------------------------------------- #

RULE_FAMILIES = ("CORE", "ID", "SCH", "LIN", "REC", "STA", "ATT", "SEM", "C2P", "SWH", "SPDX", "PROV")
RULE_PATTERN = re.compile(r"\b(" + "|".join(RULE_FAMILIES) + r")-[0-9]+\b")


@dataclass
class Vector:
    """One conformance case, resolved from a vector file."""

    name: str
    group: str
    class_name: str
    kind: str
    source: Path
    rules: list[str] = field(default_factory=list)
    record: Any = None
    records: list[Any] = field(default_factory=list)
    expect: dict[str, Any] = field(default_factory=dict)
    artifact: Path | None = None
    bridge: str | None = None


def default_vectors_dir() -> Path:
    """The suite that ships with this repository, independent of the cwd."""
    return Path(__file__).resolve().parent.parent / "spec" / "vectors"


def load_vectors(directory: Path) -> tuple[list[Vector], list[Issue]]:
    """Read every vector file, applying CON-14..CON-22. Returns (vectors, suite errors)."""
    vectors: list[Vector] = []
    suite_errors: list[Issue] = []
    seen_names: set[str] = set()

    for path in sorted(directory.glob("*.json")):
        if path.name == "exemptions.json":
            continue
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            suite_errors.append(Issue("CON-14", f"{path.name}: not valid JSON — {error}"))
            continue
        if not isinstance(document, dict) or document.get("suite") != VECTOR_SUITE:
            suite_errors.append(Issue("CON-14", f"{path.name}: 'suite' must be '{VECTOR_SUITE}'"))
            continue
        group = document.get("group")
        entries = document.get("vectors")
        if not isinstance(group, str) or not group or not isinstance(entries, list) or not entries:
            suite_errors.append(Issue("CON-14", f"{path.name}: 'group' and a non-empty 'vectors' array are required"))
            continue
        base = document.get("base")

        for position, entry in enumerate(entries):
            label = f"{path.name}: vectors[{position}]"
            if not isinstance(entry, dict):
                suite_errors.append(Issue("CON-15", f"{label} must be an object"))
                continue

            name = entry.get("name")
            if not isinstance(name, str) or not name:
                suite_errors.append(Issue("CON-15", f"{label} needs a non-empty 'name'"))
                continue
            if name in seen_names:
                suite_errors.append(Issue("CON-18", f"{path.name}: duplicate vector name '{name}'"))
                continue
            seen_names.add(name)

            class_name = entry.get("class")
            if class_name not in CONFORMANCE_CLASSES:
                suite_errors.append(Issue("CON-15", f"{name}: 'class' must be one of {sorted(CONFORMANCE_CLASSES)}"))
                continue

            kind = entry.get("kind", "record")
            if kind not in VECTOR_KINDS:
                suite_errors.append(Issue("CON-22", f"{name}: 'kind' must be one of {sorted(VECTOR_KINDS)}"))
                continue

            expect = entry.get("expect")
            if not isinstance(expect, dict):
                suite_errors.append(Issue("CON-15", f"{name}: 'expect' must be an object"))
                continue

            rules = entry.get("rules", [])
            if not isinstance(rules, list) or not all(isinstance(rule, str) for rule in rules):
                suite_errors.append(Issue("CON-15", f"{name}: 'rules' must be an array of rule identifiers"))
                continue

            vector = Vector(name=name, group=group, class_name=class_name, kind=kind, source=path, rules=list(rules), expect=expect)

            bridge = entry.get("bridge")
            if bridge is not None:
                if not isinstance(bridge, str) or ":" not in bridge:
                    suite_errors.append(
                        Issue("CON-28", f"{name}: 'bridge' must be the extension key the bridge defines, such as 'variorum:semver'")
                    )
                    continue
                vector.bridge = bridge

            if kind == "graph":
                records = entry.get("records")
                if not isinstance(records, list) or not records or not all(isinstance(item, dict) for item in records):
                    suite_errors.append(Issue("CON-20", f"{name}: a graph vector needs a non-empty 'records' array"))
                    continue
                if not isinstance(expect.get("acyclic"), bool):
                    suite_errors.append(Issue("CON-20", f"{name}: a graph vector needs 'expect.acyclic' as a boolean"))
                    continue
                vector.records = records
            elif kind == "jcs":
                if "record" not in entry or not isinstance(entry["record"], dict):
                    suite_errors.append(Issue("CON-21", f"{name}: a jcs vector needs a complete 'record' object"))
                    continue
                if not isinstance(expect.get("jcs"), str):
                    suite_errors.append(Issue("CON-21", f"{name}: a jcs vector needs 'expect.jcs' as a string"))
                    continue
                vector.record = entry["record"]
            else:
                if "record" in entry:
                    vector.record = entry["record"]
                elif "patch" in entry and isinstance(base, dict) and isinstance(entry["patch"], dict):
                    vector.record = {**base, **entry["patch"]}
                else:
                    suite_errors.append(Issue("CON-16", f"{name}: needs 'record', or 'patch' in a file with 'base'"))
                    continue
                if not isinstance(expect.get("valid"), bool):
                    suite_errors.append(Issue("CON-17", f"{name}: 'expect.valid' must be a boolean"))
                    continue
                if expect["valid"] is False and not (
                    isinstance(expect.get("rules"), list) and expect["rules"]
                ):
                    suite_errors.append(Issue("CON-17", f"{name}: a reject vector needs a non-empty 'expect.rules'"))
                    continue

            artifact = entry.get("artifact")
            if artifact is not None:
                if not isinstance(artifact, str):
                    suite_errors.append(Issue("CON-19", f"{name}: 'artifact' must be a path string"))
                    continue
                resolved = (path.parent / artifact).resolve()
                if not resolved.is_file():
                    suite_errors.append(Issue("CON-19", f"{name}: artifact fixture not found at {resolved}"))
                    continue
                if entry.get("fixture") is True:
                    declared = vector.record.get("artifact") if isinstance(vector.record, dict) else None
                    if not isinstance(declared, dict) or not isinstance(declared.get("digest"), str):
                        suite_errors.append(Issue("CON-19", f"{name}: a fixture vector needs record.artifact.digest"))
                        continue
                    actual = file_digest(resolved)
                    if actual != declared["digest"]:
                        suite_errors.append(
                            Issue("CON-19", f"{name}: stale fixture — record says {declared['digest']}, {resolved.name} is {actual}")
                        )
                        continue
                    size = declared.get("size")
                    if isinstance(size, int) and not isinstance(size, bool) and size != resolved.stat().st_size:
                        suite_errors.append(
                            Issue("CON-19", f"{name}: stale fixture — record says {size} bytes, {resolved.name} is {resolved.stat().st_size}")
                        )
                        continue
                elif "fixture" in entry:
                    suite_errors.append(Issue("CON-19", f"{name}: 'fixture' must be a boolean"))
                    continue
                vector.artifact = resolved

            vectors.append(vector)

    return vectors, suite_errors


def run_vector(vector: Vector) -> list[Issue]:
    """Return the findings that make a vector fail; an empty list means it passed."""
    if vector.kind == "graph":
        _edges, cycles = build_graph(vector.records)
        expected_acyclic = bool(vector.expect["acyclic"])
        if expected_acyclic and cycles:
            return [Issue("LIN-7", f"expected an acyclic graph, found a cycle: {cycles[0]}")]
        if not expected_acyclic and not cycles:
            return [Issue("LIN-7", "expected a cycle, found an acyclic graph")]
        return []

    if vector.kind == "jcs":
        payload = canonicalise(vector.record).decode("utf-8")
        if payload != vector.expect["jcs"]:
            return [Issue("ATT-6", f"canonical form is {payload!r}, expected {vector.expect['jcs']!r}")]
        return []

    report = validate_record(vector.record, vector.artifact)
    if vector.expect["valid"] is True:
        return list(report.errors)

    cited = {issue.rule for issue in report.errors}
    if not cited:
        return [Issue("CON-9", "expected a rejection, the record was accepted")]
    expected_rules = set(vector.expect.get("rules") or [])
    if not cited & expected_rules:
        return [Issue("CON-10", f"rejected citing {sorted(cited)}, expected at least one of {sorted(expected_rules)}")]
    return []


def load_exemptions(path: Path) -> tuple[dict[str, str], list[Issue]]:
    """Read spec/vectors/exemptions.json (CON-24, CON-25)."""
    if not path.is_file():
        return {}, [Issue("CON-24", f"coverage requires an exemption file at {path}")]
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return {}, [Issue("CON-24", f"{path.name}: not valid JSON — {error}")]
    if not isinstance(document, dict) or document.get("suite") != VECTOR_SUITE:
        return {}, [Issue("CON-24", f"{path.name}: 'suite' must be '{VECTOR_SUITE}'")]
    rules = document.get("rules")
    if not isinstance(rules, dict):
        return {}, [Issue("CON-24", f"{path.name}: 'rules' must be an object mapping rule to reason")]

    exemptions: dict[str, str] = {}
    issues: list[Issue] = []
    for rule, reason in rules.items():
        if not isinstance(reason, str) or len(reason.strip()) < 20:
            issues.append(Issue("CON-25", f"{rule}: an exemption needs a reason explaining why no record can decide it"))
            continue
        exemptions[rule] = reason
    return exemptions, issues


def spec_rule_ids(spec_dir: Path) -> set[str]:
    """Every record rule identifier defined in spec/00..06 and its extension bridges (CON rules excluded)."""
    paths = sorted(spec_dir.glob("*.md")) + sorted((spec_dir / "90-extensions").glob("*.md"))
    identifiers: set[str] = set()
    for path in paths:
        identifiers.update(match.group(0) for match in RULE_PATTERN.finditer(path.read_text(encoding="utf-8")))
    return identifiers


def coverage_report(vectors: list[Vector], spec_dir: Path, exemptions: dict[str, str]) -> tuple[list[str], list[Issue]]:
    """Return (summary lines, failures) for CON-24..CON-26.

    Only the record rule families count: CON rules describe the suite and the
    act of conformance, so they are verified by this command rather than by a
    vector that could never decide them.
    """
    defined = spec_rule_ids(spec_dir)
    referenced = {rule for vector in vectors for rule in vector.rules if RULE_PATTERN.fullmatch(rule)}
    uncovered = sorted(defined - referenced - set(exemptions))
    stale_exemptions = sorted(set(exemptions) - defined)
    undefined_references = sorted(referenced - defined)

    issues: list[Issue] = []
    if uncovered:
        issues.append(Issue("CON-24", f"rules with no vector and no exemption: {', '.join(uncovered)}"))
    if stale_exemptions:
        issues.append(Issue("CON-26", f"exemptions for rules that do not exist: {', '.join(stale_exemptions)}"))
    if undefined_references:
        issues.append(Issue("CON-26", f"vectors cite rules that the specification does not define: {', '.join(undefined_references)}"))

    covered = len(defined & referenced)
    summary = [
        f"coverage   {covered}/{len(defined)} rules referenced, {len(set(exemptions) & defined)} exempt, {len(uncovered)} uncovered"
    ]
    return summary, issues


def command_conform(arguments: argparse.Namespace) -> int:
    directory = Path(arguments.vectors).resolve() if arguments.vectors else default_vectors_dir()
    vectors, suite_errors = load_vectors(directory)

    if not suite_errors and not vectors:
        suite_errors.append(Issue("CON-14", f"no vectors found in {directory}"))

    if suite_errors:
        print(f"suite      {directory}", file=sys.stderr)
        for issue in suite_errors:
            print(f"SUITE      {issue}", file=sys.stderr)
        return 2

    failures: list[tuple[Vector, list[Issue]]] = []
    for vector in vectors:
        findings = run_vector(vector)
        if findings:
            failures.append((vector, findings))

    accepts = sum(1 for vector in vectors if vector.kind == "record" and vector.expect.get("valid") is True)
    rejections = sum(1 for vector in vectors if vector.kind == "record" and vector.expect.get("valid") is False)
    others = len(vectors) - accepts - rejections

    print(f"suite      {VECTOR_SUITE} from {directory}")
    print(f"vectors    {len(vectors)} total ({accepts} accept, {rejections} reject, {others} graph/jcs)")
    print(f"result     {'PASS' if not failures else 'FAIL'} {len(vectors) - len(failures)}/{len(vectors)}")
    for vector, findings in failures:
        for finding in findings:
            print(f"FAIL       {vector.name}: {finding}")
    if arguments.verbose and failures:
        for vector, _findings in failures:
            print(f"           {vector.name} ({vector.group}, class {vector.class_name}, {vector.source.name})")

    status = 1 if failures else 0

    if arguments.coverage:
        exemptions, exemption_issues = load_exemptions(directory / "exemptions.json")
        summary, coverage_issues = coverage_report(vectors, directory.parent, exemptions)
        print("\n".join(summary))
        for issue in exemption_issues + coverage_issues:
            print(f"COVERAGE   {issue}", file=sys.stderr)
        if exemption_issues or coverage_issues:
            status = 1

    return status


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #


def load_record(path: Path) -> dict[str, Any]:
    """Read a record from disk, raising a readable error when it is not JSON."""
    if not path.is_file():
        raise SystemExit(f"{path}: not a file")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"{path}: not valid JSON — {error}") from error


def command_digest(arguments: argparse.Namespace) -> int:
    artifact = Path(arguments.artifact)
    if not artifact.is_file():
        raise SystemExit(f"{artifact}: not a file")
    print(file_digest(artifact))
    return 0


def command_stamp(arguments: argparse.Namespace) -> int:
    artifact = Path(arguments.artifact)
    if not artifact.is_file():
        raise SystemExit(f"{artifact}: not a file")

    digest = file_digest(artifact)
    record: dict[str, Any] = {
        "variorum": SPEC_VERSION,
        "id": record_id_for(digest),
        "artifact": {
            "digest": digest,
            "size": artifact.stat().st_size,
            "mediaType": arguments.media_type or "application/octet-stream",
            "name": artifact.name,
        },
        "scheme": {"name": "none"} if arguments.scheme is None else {
            "name": arguments.scheme[0],
            "version": arguments.scheme[1],
        },
        "created": now_timestamp(),
    }

    if arguments.producer:
        record["producer"] = {"name": arguments.producer, "kind": "human"}
    if arguments.parent:
        record["lineage"] = {"parents": [{"id": arguments.parent, "relation": arguments.relation}]}
    if arguments.state:
        record["state"] = {
            "current": arguments.state,
            "transitions": [] if arguments.state == "draft" else [
                {
                    "from": "draft",
                    "to": arguments.state,
                    "actor": {"name": arguments.producer or "unknown", "kind": "human"},
                    "at": now_timestamp(),
                }
            ],
        }

    target = Path(arguments.output) if arguments.output else artifact.parent / "variorum.json"
    target.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(target)
    return 0


def satisfied_classes(record: dict[str, Any]) -> list[str]:
    """The classes a validated record satisfies, derived from its members (CON-7)."""
    classes = ["core"]
    for class_name in ("lineage", "recipe", "attestation"):
        if record.get(class_name) is not None:
            classes.append(class_name)
    return classes


def command_validate(arguments: argparse.Namespace) -> int:
    record = load_record(Path(arguments.record))
    artifact = Path(arguments.artifact) if arguments.artifact else None
    report = validate_record(record, artifact)
    for issue in report.warnings:
        print(f"warning {issue}", file=sys.stderr)
    for issue in report.errors:
        print(issue, file=sys.stderr)
    if report.ok:
        classes = ", ".join(satisfied_classes(record)) if isinstance(record, dict) else "core"
        print(f"OK — record conforms to Variorum {record.get('variorum')} ({classes})")
        return 0
    return 1


def render_tool_chain(tool: object) -> str:
    """One tool or an array of them, as `show` prints it.

    REC-5 lets `recipe.tool` be a single object or a chain; printing "?" for a
    legal shape is a defect in the reader, not in the record.
    """
    if isinstance(tool, dict):
        name = tool.get("name")
        if not isinstance(name, str) or not name:
            return "?"
        model = tool.get("model")
        version = tool.get("version")
        label = f"{name}/{model}" if isinstance(model, str) and model else name
        if isinstance(version, str) and version:
            label += f" {version}"
        return label
    if isinstance(tool, list):
        rendered = [render_tool_chain(entry) for entry in tool]
        return ", ".join(label for label in rendered if label) or "?"
    return "?"


def command_show(arguments: argparse.Namespace) -> int:
    record = load_record(Path(arguments.record))
    artifact = record.get("artifact", {})
    scheme = record.get("scheme", {})
    state = record.get("state", {})
    lineage = record.get("lineage", {})

    print(f"id        {record.get('id')}")
    print(f"artifact  {artifact.get('name', '(unnamed)')}  {artifact.get('size', '?')} bytes  {artifact.get('mediaType', '?')}")
    print(f"scheme    {scheme.get('name')} {scheme.get('version', '')}".rstrip())
    print(f"created   {record.get('created')}")
    if state:
        print(f"state     {state.get('current')} ({len(state.get('transitions', []))} transitions)")
    if lineage:
        for parent in lineage.get("parents", []):
            print(f"from      {parent.get('relation')} of {parent.get('id')}")
    recipe = record.get("recipe")
    if recipe:
        print(f"recipe    {recipe.get('kind')} via {render_tool_chain(recipe.get('tool'))}")
    return 0


def command_graph(arguments: argparse.Namespace) -> int:
    records = [load_record(Path(path)) for path in arguments.records]
    edges, cycles = build_graph(records)
    if arguments.mermaid:
        print("graph LR")
        for index, (parent, child, relation) in enumerate(edges):
            parent_node = f"p{index}"
            child_node = f"c{index}"
            print(f'  {parent_node}["{parent[-8:]}"] -->|{relation}| {child_node}["{child[-8:]}"]')
    else:
        for parent, child, relation in edges:
            print(f"{parent}  --{relation}-->  {child}")
    for cycle in cycles:
        print(f"CYCLE {cycle}", file=sys.stderr)
    return 1 if cycles else 0


def command_verify(arguments: argparse.Namespace) -> int:
    record = load_record(Path(arguments.record))
    report = validate_record(record, Path(arguments.artifact) if arguments.artifact else None)
    report.issues.extend(verify_attestation(record).issues)
    for issue in report.warnings:
        print(f"warning {issue}", file=sys.stderr)
    for issue in report.errors:
        print(issue, file=sys.stderr)
    return 0 if report.ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="variorum", description="Reference tool for the Variorum specification")
    parser.add_argument("--version", action="version", version=f"variorum {TOOL_VERSION} (spec {SPEC_VERSION})")
    subparsers = parser.add_subparsers(dest="command", required=True)

    digest_parser = subparsers.add_parser("digest", help="compute the sha256 digest of an artifact")
    digest_parser.add_argument("artifact")
    digest_parser.set_defaults(handler=command_digest)

    stamp_parser = subparsers.add_parser("stamp", help="create a record for an artifact")
    stamp_parser.add_argument("artifact")
    stamp_parser.add_argument("-o", "--output", help="where to write the record")
    stamp_parser.add_argument("--scheme", nargs=2, metavar=("NAME", "VERSION"), help="version scheme and label")
    stamp_parser.add_argument("--media-type", help="media type of the artifact")
    stamp_parser.add_argument("--producer", help="name of the producer")
    stamp_parser.add_argument("--parent", help="Variorum id of the parent artifact")
    stamp_parser.add_argument("--relation", default="derivation", choices=sorted(RELATIONS))
    stamp_parser.add_argument("--state", choices=sorted(STATES))
    stamp_parser.set_defaults(handler=command_stamp)

    validate_parser = subparsers.add_parser("validate", help="check a record against the specification")
    validate_parser.add_argument("record")
    validate_parser.add_argument("--artifact", help="also verify the digest against this file")
    validate_parser.set_defaults(handler=command_validate)

    conform_parser = subparsers.add_parser("conform", help="run the conformance vector suite")
    conform_parser.add_argument("--vectors", help="directory holding the vector files (default: spec/vectors)")
    conform_parser.add_argument("--coverage", action="store_true", help="report which rules the suite exercises or exempts")
    conform_parser.add_argument("--verbose", action="store_true", help="print the provenance of each failing vector")
    conform_parser.set_defaults(handler=command_conform)

    show_parser = subparsers.add_parser("show", help="print a human summary of a record")
    show_parser.add_argument("record")
    show_parser.set_defaults(handler=command_show)

    graph_parser = subparsers.add_parser("graph", help="print the lineage graph of several records")
    graph_parser.add_argument("records", nargs="+")
    graph_parser.add_argument("--mermaid", action="store_true", help="emit a Mermaid diagram")
    graph_parser.set_defaults(handler=command_graph)

    verify_parser = subparsers.add_parser("verify", help="validate and attempt attestation verification")
    verify_parser.add_argument("record")
    verify_parser.add_argument("--artifact", help="also verify the digest against this file")
    verify_parser.set_defaults(handler=command_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    return arguments.handler(arguments)


if __name__ == "__main__":
    sys.exit(main())
