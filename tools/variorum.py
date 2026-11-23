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
    variorum show <record.json>
    variorum graph <record.json>... [--mermaid]
    variorum verify <record.json> [--artifact <artifact>]

Every validation failure is reported with the rule identifier from the
specification so that an implementer can look it up.
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
TOOL_VERSION = "0.1.0"

DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
ID_PATTERN = re.compile(r"^urn:variorum:sha256:[0-9a-f]{64}$")
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+$")
SCHEME_NAME_PATTERN = re.compile(r"^(semver|calver|pep440|debian|rpm|maven|nuget|date|sequence|custom|none|x-[a-z0-9-]+)$")
TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")

SCHEMES_WITHOUT_VERSION = {"none"}
RELATIONS = {"generation", "revision", "edit", "render", "transcode", "fork", "restore", "derivation"}
RECIPE_KINDS = {"manual", "build", "generative", "hybrid"}
STATES = {"draft", "candidate", "approved", "published", "superseded", "rejected", "archived"}
ACTOR_KINDS = {"human", "organization", "software"}
ALGORITHMS = {"ed25519", "ecdsa-p256-sha256", "rsa-pss-sha256"}

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
    """One conformance failure, always tied to a rule identifier."""

    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.rule}] {self.message}"


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)

    def add(self, rule: str, message: str) -> None:
        self.issues.append(Issue(rule, message))

    @property
    def ok(self) -> bool:
        return not self.issues


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
    """ID-2..ID-11 plus the id/digest equality rule (ID-8)."""
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


def validate_actor(actor: Any, report: Report, member: str) -> None:
    """ID-10, ID-11, ID-12 and the actor shape shared by producer and transitions."""
    if not isinstance(actor, dict):
        report.add("ID-10", f"'{member}' must be an object")
        return
    if not isinstance(actor.get("name"), str) or not actor["name"]:
        report.add("ID-10", f"'{member}.name' must be a non-empty string")
    kind = actor.get("kind")
    if kind is not None and kind not in ACTOR_KINDS:
        report.add("ID-11", f"'{member}.kind' must be one of {sorted(ACTOR_KINDS)}")
    if kind == "software":
        software = actor.get("software")
        if not isinstance(software, dict) or not isinstance(software.get("name"), str):
            report.add("ID-12", f"'{member}.software' should identify the software by name")


def validate_scheme(record: dict[str, Any], report: Report) -> None:
    """SCH-1..SCH-3."""
    scheme = record.get("scheme")
    if not isinstance(scheme, dict):
        report.add("SCH-1", "'scheme' must be present and must be an object")
        return

    name = scheme.get("name")
    if not isinstance(name, str) or not SCHEME_NAME_PATTERN.match(name):
        report.add("SCH-2", "'scheme.name' must be a reserved name or x-<vendor>-<name>")
        return

    version = scheme.get("version")
    if name in SCHEMES_WITHOUT_VERSION:
        if version is not None:
            report.add("SCH-3", "'scheme.version' must be absent when scheme.name is 'none'")
    elif version is None:
        report.add("SCH-3", "'scheme.version' must be present unless scheme.name is 'none'")

    authority = scheme.get("authority")
    if authority is not None and not isinstance(authority, str):
        report.add("SCH-4", "'scheme.authority' must be an absolute URI")

    sequence = scheme.get("sequence")
    if sequence is not None and (not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0):
        report.add("SCH-8", "'scheme.sequence' must be a non-negative integer")


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
    """REC-1..REC-19 (the structural subset that can be checked statically)."""
    recipe = record.get("recipe")
    if recipe is None:
        return
    if not isinstance(recipe, dict):
        report.add("REC-1", "'recipe' must be an object")
        return

    kind = recipe.get("kind")
    if kind not in RECIPE_KINDS:
        report.add("REC-2", f"'recipe.kind' must be one of {sorted(RECIPE_KINDS)}")
        return

    if kind == "build":
        source = recipe.get("source")
        if not isinstance(source, dict) or not (source.get("ref") or source.get("digest")):
            report.add("REC-4", "a build recipe must declare 'source' with a ref or a digest")

    if kind == "generative":
        tool = recipe.get("tool")
        has_tool = isinstance(tool, dict) and bool(tool.get("name")) and bool(tool.get("model"))
        if not has_tool:
            report.add("REC-7", "a generative recipe must declare 'tool' with name and model")
        has_snapshot = isinstance(tool, dict) and tool.get("snapshot") is not None
        if not has_snapshot and recipe.get("generatedAt") is None:
            report.add("REC-8", "a generative recipe must record 'tool.snapshot' or 'generatedAt'")
        if not isinstance(recipe.get("prompt"), str):
            report.add("REC-6", "a generative recipe must record the prompt verbatim")

    if kind == "hybrid":
        stages = recipe.get("stages")
        if not isinstance(stages, list) or not stages:
            report.add("REC-19", "a hybrid recipe must declare 'stages'")

    inputs = recipe.get("inputs")
    if inputs is not None:
        if not isinstance(inputs, list):
            report.add("REC-14", "'recipe.inputs' must be an array")
        else:
            for index, item in enumerate(inputs):
                if not isinstance(item, dict) or not item.get("ref") or not item.get("role"):
                    report.add("REC-14", f"inputs[{index}] must carry 'ref' and 'role'")

    determinism = recipe.get("determinism")
    if determinism is not None and determinism not in {"none", "seeded", "full"}:
        report.add("REC-12", "'recipe.determinism' must be none, seeded or full")


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
        validate_actor(transition.get("actor"), report, f"transitions[{index}].actor")

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

    if current == "superseded" and not state.get("supersededBy"):
        report.add("STA-12", "'state.supersededBy' is required when the state is 'superseded'")


def validate_attestation(record: dict[str, Any], report: Report) -> None:
    """ATT-1..ATT-5."""
    attestation = record.get("attestation")
    if attestation is None:
        return
    entries = attestation if isinstance(attestation, list) else [attestation]
    if isinstance(attestation, list) and not entries:
        report.add("ATT-1", "'attestation' must not be an empty array")
        return
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            report.add("ATT-1", f"attestation[{index}] must be an object")
            continue
        if entry.get("algorithm") not in ALGORITHMS:
            report.add("ATT-5", f"attestation[{index}].algorithm must be one of {sorted(ALGORITHMS)}")
        signature = entry.get("signature")
        if not isinstance(signature, str) or not re.match(r"^[A-Za-z0-9_-]+$", signature):
            report.add("ATT-3", f"attestation[{index}].signature must be base64url without padding")


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
            report.add("CORE-10", f"extension key '{key}' should be namespaced with a '<prefix>:<name>' form")


def validate_record(record: Any, artifact: Path | None = None) -> Report:
    """Run every applicable rule and collect the failures."""
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
# Commands
# --------------------------------------------------------------------------- #


def load_record(path: Path) -> dict[str, Any]:
    """Read a record from disk, raising a readable error when it is not JSON."""
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


def command_validate(arguments: argparse.Namespace) -> int:
    record = load_record(Path(arguments.record))
    artifact = Path(arguments.artifact) if arguments.artifact else None
    report = validate_record(record, artifact)
    for issue in report.issues:
        print(issue, file=sys.stderr)
    if report.ok:
        print(f"OK — record conforms to Variorum {record.get('variorum')} (core)")
        return 0
    return 1


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
        tool = recipe.get("tool")
        tool_name = tool.get("name") if isinstance(tool, dict) else "?"
        model = tool.get("model") if isinstance(tool, dict) else None
        print(f"recipe    {recipe.get('kind')} via {tool_name}{('/' + model) if model else ''}")
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
    for issue in report.issues:
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
