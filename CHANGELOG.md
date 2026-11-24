# Changelog

All notable changes to the Variorum specification. Format loosely based on Keep a Changelog; the specification follows SemVer (see [GOVERNANCE.md](GOVERNANCE.md)).

## [Unreleased]

### Added

- `spec/90-extensions/c2pa.md` — the second extension bridge (`C2P-1`…`C2P-8`): a record points at the active C2PA 2.2 manifest by its `urn:c2pa:` URN and never copies the manifest's content; `location` says whether the manifest store is embedded or external (the digest means different things in each case); identity stays the digest, and the C2PA hard binding, ingredients and claim signature are written down as non-mappings rather than plausible conversions.
- `spec/vectors/c2pa.json` — 19 vectors for the bridge, each marked `"bridge": "variorum:c2pa"`, including the over-strictness guards (lowercase UUID string representations, opaque optional URN components) and a rejected JSON `null` claim.
- `docs/adr/ADR-0011-c2pa-bridge-references-the-manifest.md` — why the bridge points instead of absorbing signed content into an unsigned sidecar.
- `C2P-1`…`C2P-6` in the reference validator; `TOOL_VERSION` 0.4.0.
- `spec/90-extensions/semver.md` — the first extension bridge (`SEM-1`…`SEM-7`): an opt-in claim via `extensions["variorum:semver"]`, the SemVer 2.0.0 grammar, the tag-to-version mapping (`v1.3.1`, monorepo prefixes), the prohibition on `scheme.sequence`, and precedence left entirely to SemVer.
- `spec/vectors/semver.json` — 18 vectors for the bridge (7 accept, 11 reject), including the over-strictness guard that an unclaimed `semver` label stays opaque.
- `examples/instruisto-guide-owasp/` — a real release artifact (49-page PDF, 637,290 B, tag `owasp-api-security/v1.3.1`) wrapped unchanged; the digest was computed from the released bytes.
- `CON-28` — vectors may carry `bridge`, the extension key of the bridge they exercise.
- `docs/adr/ADR-0009-semver-bridge-is-opt-in.md` — a bridge binds only the records that claim it.
- `docs/adr/ADR-0010-bridge-rules-are-conformance-rules.md` — bridge rules are covered like core rules, and bridge vectors are opt-in for implementations.
- `SEM-1`…`SEM-7` in the reference validator; `TOOL_VERSION` 0.3.0.
- `spec/07-conformance.md` — conformance targets for records and implementations, four implementation levels, the vector-suite contract and the coverage obligation (`CON-1`…`CON-27`).
- `spec/vectors/` — 103 machine-readable vectors (30 accept, 70 reject, 3 graph/canonicalisation) in eight groups, plus `exemptions.json` with a stated reason for each rule no record can decide, and real fixtures whose digests are recomputed on every run.
- `tools/variorum.py conform` — reference runner for the suite, `--vectors`, `--coverage` and `--verbose`; exit `0` pass, `1` failure, `2` malformed or stale suite.
- `tests/test_vectors.py` — suite integrity tests: structural validity, unique names, fixture digests, and full citation of every rule a reject vector lists.
- `.github/workflows/ci.yml` — unit tests, conformance with coverage, real examples and JSON well-formedness on Python 3.11 and 3.13, no third-party packages.
- `docs/adr/ADR-0005-should-violations-are-warnings.md` — severity split between MUST and SHOULD.
- `docs/adr/ADR-0006-vectors-are-the-conformance-contract.md` — why conformance is data, not prose.
- `docs/adr/ADR-0007-declared-classes-must-be-backed.md` — a declared class without its member is an error.
- `docs/adr/ADR-0008-scheme-names-are-opaque.md` — reserved scheme names are a vocabulary, not a whitelist.
- `SCH-10` — the `x-` prefix for unregistered scheme names is a SHOULD, and a warning when absent.

### Changed

- `CON-9` — a vector carrying `bridge` is obligatory only of implementations that claim that bridge; every other implementation skips it instead of failing it.
- `schema/variorum.schema.json` — `extensions["variorum:c2pa"]` is typed: an object with `manifest` and `location` required, `uri` required exactly when `location` is `external` and forbidden otherwise, and no members beyond the three the bridge defines.
- `CON-24` — coverage now counts every rule identifier defined under `spec/90-extensions/`, not only sections 00–06; `conform --coverage` and CI follow.
- `schema/variorum.schema.json` — `extensions["variorum:semver"]` is now typed (an object, with an optional string `tag`), mirroring `SEM-1` and `SEM-5`.
- `validate` now separates errors (violated MUST) from warnings (violated SHOULD); only errors make a record non-conformant. Checks affected: ID-12, CORE-10, REC-5, REC-12, SCH-10.
- `scheme.name` accepts any lowercase name (SCH-2) in the schema and the reference tool; the previous closed enumeration rejected names the specification already allowed.
- The two examples that declared `lineage` without carrying a `lineage` member now declare what they actually contain.
- `spec/00-overview.md` points class definitions at section 07; extensions may use an unprefixed name, with a warning rather than a rejection.

### Fixed

- Schema/tool drift against SCH-2 and CORE-10: a SHOULD was being enforced as a MUST, and a valid scheme name was rejected.

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
