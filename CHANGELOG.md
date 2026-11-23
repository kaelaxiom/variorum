# Changelog

All notable changes to the Variorum specification. Format loosely based on Keep a Changelog; the specification follows SemVer (see [GOVERNANCE.md](GOVERNANCE.md)).

## [0.1.0-draft] — 2026-11-22

First draft. Nothing here is stable.

### Added

- `spec/00-overview.md` — scope, six design principles, conformance classes, terminology, relationship to eight existing standards.
- `spec/01-identity.md` — digest-based identity (`ID-1`…`ID-16`), derived record identifier `urn:variorum:sha256:<hex>`.
- `spec/02-scheme.md` — scheme reference table, eleven reserved scheme names, prohibition on redefining ordering (`SCH-1`…`SCH-9`).
- `spec/03-lineage.md` — eight derivation relations, acyclic graph rules, work-level identity (`LIN-1`…`LIN-13`).
- `spec/04-recipe.md` — `manual` / `build` / `generative` / `hybrid`, honest determinism (`REC-1`…`REC-21`).
- `spec/05-state.md` — seven-state lifecycle, legal transition table, terminal rejection (`STA-1`…`STA-15`).
- `spec/06-attestation.md` — JCS signing over the record minus attestation (`ATT-1`…`ATT-12`).
- `schema/variorum.schema.json` — JSON Schema 2020-12.
- `tools/variorum.py` — reference CLI, standard library only.
- `examples/` — three records built from real artifacts in real projects.

### Known gaps

- No conformance suite or test vectors yet; `validate` implements the rules but nothing proves two implementations agree.
- Attestation signing and verification are specified but not implemented in the CLI (needs a key distribution story first).
- Extension bridges (C2PA, SWHID, SPDX, PROV) are planned, not written.
