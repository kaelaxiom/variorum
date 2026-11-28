#!/usr/bin/env python3
"""Agreement tests between the JSON Schema and the reference tool.

`schema/variorum.schema.json` and `tools/variorum.py` are two renderings of one
contract (CONTEXT.md: "Schema and spec must not drift"). Until this file
existed, nothing compared them: the tool's vocabularies lived as set literals,
the schema's as `enum` arrays, and a change to one could pass every test while
the other kept rejecting what the specification allows.

The last test pins a deliberate asymmetry. `recipe.determinism` is a SHOULD
(`REC-12`), and `CON-8` says a record that violates only a SHOULD remains
conformant, so the schema must not reject an unrecognised grade. The value space
is documented in the property's description and enforced as a warning by the
tool (ADR-0005, ADR-0015).
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import variorum  # noqa: E402

SCHEMA_PATH = ROOT / "schema" / "variorum.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def enum_at(*path: str) -> list[str]:
    node = SCHEMA
    for key in path:
        node = node[key]
    return node["enum"]


class SchemaVocabularyTests(unittest.TestCase):
    """Every closed vocabulary a record validator enforces exists twice: here it must agree."""

    def assert_same(self, schema_values: list[str], tool_values: set[str], label: str) -> None:
        self.assertEqual(sorted(schema_values), sorted(tool_values), f"{label} drifted between schema and tool")

    def test_recipe_kinds(self) -> None:
        self.assert_same(enum_at("properties", "recipe", "properties", "kind"), variorum.RECIPE_KINDS, "recipe.kind")

    def test_states(self) -> None:
        current = enum_at("properties", "state", "properties", "current")
        transitions = SCHEMA["properties"]["state"]["properties"]["transitions"]["items"]["properties"]
        self.assert_same(current, variorum.STATES, "state.current")
        self.assert_same(transitions["from"]["enum"], variorum.STATES, "state.transitions[].from")
        self.assert_same(transitions["to"]["enum"], variorum.STATES, "state.transitions[].to")

    def test_lineage_relations(self) -> None:
        relation = SCHEMA["properties"]["lineage"]["properties"]["parents"]["items"]["properties"]["relation"]
        self.assert_same(relation["enum"], variorum.RELATIONS, "lineage.parents[].relation")

    def test_actor_kinds(self) -> None:
        self.assert_same(enum_at("$defs", "actor", "properties", "kind"), variorum.ACTOR_KINDS, "actor.kind")

    def test_attestation_algorithms(self) -> None:
        self.assert_same(
            enum_at("$defs", "attestation", "properties", "algorithm"),
            variorum.ALGORITHMS,
            "attestation.algorithm",
        )

    def test_conformance_classes(self) -> None:
        self.assert_same(
            enum_at("properties", "extensions", "properties", "variorum:conformance", "items"),
            variorum.CONFORMANCE_CLASSES,
            "variorum:conformance",
        )

    def test_every_typed_bridge_key_is_a_bridge_the_tool_defines(self) -> None:
        typed = {
            key
            for key in SCHEMA["properties"]["extensions"]["properties"]
            if key.startswith("variorum:") and key != "variorum:conformance"
        }
        defined = {
            variorum.SEMVER_BRIDGE,
            variorum.C2PA_BRIDGE,
            variorum.SWHID_BRIDGE,
            variorum.SPDX_BRIDGE,
            variorum.PROV_BRIDGE,
        }
        self.assertEqual(typed, defined, "the schema types a different set of bridge claims than the tool defines")

    def test_determinism_stays_a_warning(self) -> None:
        """REC-12 is a SHOULD: the schema must not carry an assertion for it."""
        determinism = SCHEMA["properties"]["recipe"]["properties"]["determinism"]
        forbidden = {"type", "enum", "const", "oneOf", "anyOf", "allOf", "not", "pattern"}
        self.assertEqual(set(), forbidden & set(determinism), "a SHOULD-graded member cannot be a schema rejection")
        self.assertIn("REC-12", determinism.get("description", ""))
        self.assertIn("content", determinism.get("description", ""))


if __name__ == "__main__":
    unittest.main()
