# Changelog

All notable changes to the Variorum specification. Format loosely based on Keep a Changelog; the specification follows SemVer (see [GOVERNANCE.md](GOVERNANCE.md)).

## [Unreleased]

### Added

- `docs/adoption.md` — the adoption guide, written by following its own steps rather than describing them afterwards: the `core` path performed on `instruisto`'s release `github-copilot-agents/v1.1.0`, from `gh release download` through `stamp`, the single hand edit (the conformance declaration, `CORE-7`), `validate` and `show`. It states what `core` requires member by member, where the record goes and what it is named (`CORE-12`, `CORE-13`), why a tag is not a version (`SCH-7`, `SEM-5`), seven ways to get the digest or the timestamp wrong, and which classes may be postponed without making the record a lesser one (invariant 4).
- `examples/instruisto-release-copilot/` — the two records that guide produced, one per release asset rather than one per release (`ID-9`): `proposal.pdf` (73,506 B, `2605defcf2a7…`) and `syllabus.pdf` (148,743 B, `60d62fe0bbe7…`), both carrying the label `1.1.0` the release already had. Both digests were recomputed from the downloaded assets before the records were written.
- `tests/test_docs.py` — `ReadmeExampleTests`: the README's quick example must be a verbatim copy of a record under `examples/`, so the most-visible page cannot teach a shape the validator rejects (it did: `lineage.parents` as strings, `state.transitions[].actor` as a string).
- `spec/90-extensions/spdx.md` — the fourth extension bridge (`SPDX-1`…`SPDX-8`): a record cites the SPDX 2.3 document that describes the artifact's contents, in `extensions["variorum:spdx"]` (`version`, `document`, optional `element`), and never copies a checksum out of it. This is the first bridge where a foreign checksum *can* equal `artifact.digest` — a file element's `SHA256` (§8.4), or a package checksum whose package is a single blob (Annex K.2.2.3) — so the document states exactly when, and why the package verification code cannot: §7.9 hashes the sorted concatenation of the files' SHA-1 *hex strings*, not the files' bytes. `SPDXRef-DOCUMENT` is refused as an element (a document is not one of the things it describes), the namespace may not carry a `#` (§6.5), and `version` is a closed list because SPDX 3.0 replaced the document model (`spdxId` as an IRI, `namespaceMap`, checksums behind `verifiedUsing`).
- `spec/vectors/spdx.json` — 18 vectors for the bridge, each marked `"bridge": "variorum:spdx"`, including accept vectors for a document-only claim, a package element and an idstring with dots and uppercase, and reject vectors for the `DocumentRef-…:SPDXRef-…` form, a `+` and an underscore in an idstring, and an `id` that is the namespace or an element URI.
- `spec/vectors/fixtures/hello.spdx.json` — a real SPDX 2.3.1 document for the existing `hello.txt` fixture; `tests/test_validate.py` recomputes its file `SHA1`, its file `SHA256` and its package verification code with the §7.9 algorithm, so neither the document nor the spec's arithmetic table can go stale.
- `docs/adr/ADR-0013-spdx-bridge-points-at-the-sbom.md` — why the bridge points at the document instead of copying a checksum that would often be numerically right.
- `SPDX-1`…`SPDX-6` in the reference validator; `TOOL_VERSION` 0.6.0.
- `spec/90-extensions/swhid.md` — the third extension bridge (`SWH-1`…`SWH-8`): a record cites a Software Heritage identifier in `extensions["variorum:swhid"].swhid` and never promotes it to `artifact.digest` or `id`. A `cnt` SWHID hashes `blob <size>` + NUL + the bytes (§5.2), so it is a different pre-image from the digest even for the friendliest object type; `dir`, `rev`, `rel` and `snp` are not about the artifact's bytes at all. Context qualifiers (`origin`, `visit`, `anchor`, `path`) are validated against SWHID's producer constraints (§6.1–§6.3), fragment qualifiers (`lines`, `bytes`) are refused because a fragment is not an artifact (`ID-9`), and one SWHID per record is the whole claim.
- `spec/vectors/swhid.json` — 32 vectors for the bridge, each marked `"bridge": "variorum:swhid"`, including an accept vector for a record without the claim (silence is not a denial) and an accept vector pinning the fact that the record validator cannot relate a shape-valid `cnt` SWHID to the digest (that is the consumer's `SWH-7` check, not the validator's).
- `docs/adr/ADR-0012-swhid-bridge-is-a-sibling-identifier.md` — why a content hash from another model stays a sibling identifier instead of becoming the identity.
- `SWH-1`…`SWH-6` in the reference validator; `TOOL_VERSION` 0.5.0.
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

- `README.md` — the "Quick example" is now a real record, copied verbatim from [`examples/la-enpenso-shot-01/`](examples/la-enpenso-shot-01/), instead of an invented skeleton whose `lineage.parents` were strings and whose `state.transitions[].actor` was a string — both shapes the validator rejects. The field table's first row now names `artifact` and its derived `id`, the members that exist; `identity` was a section title, not a member.
- `schema/variorum.schema.json` — `extensions["variorum:spdx"]` is typed: `version` fixed to `"2.3"`, `document` an absolute URI with no fragment, `element` an `SPDXRef-` identifier that is not `SPDXRef-DOCUMENT`, and no member beyond the three the bridge defines.
- `spec/vectors/exemptions.json` — `SPDX-7` and `SPDX-8` exempted with reasons: comparing a file element's checksum and refusing to read a verification code as an artifact identifier are both obligations on a consumer that holds the artifact and the document.
- `schema/variorum.schema.json` — `extensions["variorum:swhid"]` is typed: an object with `swhid` required and no other member, the identifier pattern kept byte-for-byte in step with the tool's regex, and a `not` guard against fragment qualifiers. The qualifier *combinations* of `SWH-4` depend on the object type and on the other qualifiers; JSON Schema cannot express them, so the reference tool enforces them and the schema says so.
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
