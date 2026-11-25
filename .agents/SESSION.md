# SESSION — 2026-11-22

## Objective

Found the repository and produce a v0.1 draft of the Variorum specification.

## Done

- Created `/mnt/thoth/projects/variorum`, git init, local identity configured.
- Name selected (`variorum`) after validating nine candidates against `u-onoma` POLICIES §7 with live collision searches (Firecrawl local + GitHub).
- Owner decisions recorded: umbrella scope, public repo under `kaelaxiom` with later transfer, full v0.1 deliverables, 6-hour autonomous cadence.
- Wrote `NAME.md`, `README.md`, `AGENTS.md`, `GOVERNANCE.md`, `.agents/` protocol.
- Wrote `spec/00`–`06`, `schema/variorum.schema.json`, `tools/variorum.py`, three real examples.

## Decisions

- Identity is the digest (`urn:variorum:sha256:<hex>`); the record is a sidecar, never embedded — metadata cannot live inside the bytes whose hash it defines.
- The standard wraps existing schemes and never redefines ordering.
- Conformance is graded: `core`, `lineage`, `recipe`, `attestation`.

## Open

- Conformance suite and vectors.
- Whether `recipe` should allow free-form `extensions` at the top level or only per section (deferred to ADR-0004).
- A public domain for the specification site has not been decided.

---

# SESSION — 2026-11-23

## Objective

Close Phase 1 (testability): a normative conformance section, a machine-readable vector suite, a runner, and CI.

## Done

- Wrote `spec/07-conformance.md` (`CON-1`…`CON-27`): two targets (record, implementation), four implementation levels, the vector contract, exit codes, and the coverage obligation.
- Built `spec/vectors/`: 103 vectors across `core`, `identity`, `scheme`, `lineage`, `recipe`, `state`, `attestation` and `conformance`, plus fixture-backed digest vectors, `graph` (LIN-7) and `jcs` (ATT-6/7) kinds, and `exemptions.json` with a reason per exempt rule. Fixture digests are recomputed on every run (CON-19).
- Extended `tools/variorum.py` to 0.2.0: `conform` with `--vectors`, `--coverage`, `--verbose`; exit 0/1/2; vector loading, patching, graph and JCS runners; severity split (`Issue.severity`, `Report.errors`/`Report.warnings`).
- Added `tests/test_vectors.py`: suite structure, unique names, fixture freshness, and the stricter rule that the reference tool must cite every rule a reject vector lists.
- Added `.github/workflows/ci.yml`: unit tests, `conform --coverage`, example validation and JSON well-formedness on Python 3.11 and 3.13, with no dependency installation.
- ADR-0005 (SHOULD violations are warnings), ADR-0006 (vectors are the conformance contract), ADR-0007 (declared classes must be backed), ADR-0008 (scheme names are opaque unless reserved).
- Drift fixes the vectors exposed: `scheme.name` accepts any lowercase name (SCH-2) in schema and tool, with `SCH-10` as a SHOULD for the `x-` prefix; extensions may be unprefixed (CORE-10 warning, not error); two examples that declared `lineage` without carrying it now declare only what they contain.

## Numbers

- 67 unit tests OK.
- `conform --coverage`: 103/103 PASS; 72/102 rules referenced, 30 exempt with reasons, 0 uncovered.

## Decisions

- Conformance is defined by data, not by the reference implementation (ADR-0006).
- MUST and SHOULD are different severities in code, not just in prose (ADR-0005).
- A declared conformance class is a promise about presence; declaring too little stays a warning (ADR-0007).
- The reserved scheme table is a vocabulary, never a whitelist (ADR-0008).

## Open

- Phase 2: extension bridges (semver first, then C2PA, SWHID, SPDX).
- Owner review of the draft; transfer to `cazucito` after approval.
- Domain for a public site — owner decision, not an agent decision.

---

# SESSION — 2026-11-23 (second session, Phase 2)

## Objective

Open Phase 2 with the SemVer bridge: the worked wrapping example every other bridge will cite.

## Done

- `spec/90-extensions/semver.md` — `SEM-1`…`SEM-7`. The bridge is claimed by `extensions["variorum:semver"]`; a claimed record must use `scheme.name = "semver"` and a version matching the official SemVer 2.0.0 grammar, must not carry `scheme.sequence`, may carry the release `tag` (which must end with the version's precedence part), and should name the SemVer authority. Ordering stays SemVer's; no tiebreaker, no identity from version equality.
- `spec/vectors/semver.json` — 18 vectors, each marked `"bridge": "variorum:semver"` except the one that proves an unclaimed label stays opaque. Includes the three grammar traps: `v` prefix, leading zero, and a trailing newline that a `$` anchor would let through.
- `spec/07-conformance.md` — `CON-28` defines the vector `bridge` member; `CON-9` makes bridge vectors opt-in for implementations; `CON-24` extends coverage to `spec/90-extensions/`.
- `docs/adr/ADR-0009-semver-bridge-is-opt-in.md`, `docs/adr/ADR-0010-bridge-rules-are-conformance-rules.md`.
- `schema/variorum.schema.json` — the `variorum:semver` claim is typed (object, optional `tag` string).
- `tools/variorum.py` 0.3.0 — `validate_semver_bridge` (official regex under `re.ASCII`, applied with `fullmatch`), `SEM` added to the rule families, coverage scans the extension bridges.
- `examples/instruisto-guide-owasp/` — real release asset `guide.pdf` (637,290 B, tag `owasp-api-security/v1.3.1`, commit `1360025`), digest `c40d573a…` computed from the downloaded asset; recipe tool `typst 0.15.1` and `generatedAt` read from the PDF metadata; no `state` because nobody recorded an approval chain.
- Updated README, CHANGELOG, extension README, vectors README, examples README, PLAN, STATE, HANDOFF, CONTEXT, MEMORY.

## Numbers

- 77 unit tests OK.
- `conform --coverage`: 121/121 PASS; 78/109 rules referenced, 31 exempt, 0 uncovered.
- Five example records validate.

## Decisions

- A bridge binds only the records that claim it; it is not a conformance class (ADR-0009).
- Bridge rules are conformance rules: covered by vectors, marked with `bridge`, opt-in for implementations (ADR-0010).

## Open

- C2PA, SWHID, SPDX, PROV bridges.
- A single `tag` per record; a project publishing two equivalent tags for one release needs a future extension of the bridge.
- `conform --verbose` has no "skipped bridge vector" report yet; the reference runner implements every bridge, so it does not need one.

# SESSION — 2026-11-23 (evening, close-out of the SemVer bridge)

## Objective

Close the SemVer bridge session: the tree had been left uncommitted with one known citation defect, so nothing of the previous work was durable.

## Done

- Corrected the SemVer citation in `spec/90-extensions/semver.md` and `tools/variorum.py`: the normative grammar is the *Backus–Naur Form Grammar for Valid SemVer Versions* appendix; the regular expression is the pattern published in the SemVer FAQ. The earlier "§9" was wrong — item 9 of SemVer is the pre-release rule, not the grammar.
- Re-downloaded `guide.pdf` from the `owasp-api-security/v1.3.1` release and re-hashed it: `c40d573a4bbdfa17cdb6d5619c129868f753a46a82e87a3fa24adeb1fbcc1f6a`, 637,290 B. The example record matches the released bytes; the digest was not taken on trust from the previous session.
- Found and fixed five dead relative links: three in `spec/90-extensions/` (`../docs/adr/` → `../../docs/adr/`) and two in `docs/adr/ADR-0010` (`../spec/` → `../../spec/`).
- Added `tests/test_docs.py`: every relative markdown link must resolve, with fenced and inline code stripped first, plus a guard test that the checker actually finds links. The specification is read as prose; a dead citation is invisible to `validate` and `conform`.
- Gave the out-of-order `CON-28` a lead paragraph in §7.4 explaining why bridge vectors are marked, so the number's placement reads as deliberate rather than accidental.

## Numbers

- 79 unit tests OK.
- `conform --coverage`: 121/121 PASS; 78/109 rules referenced, 31 exempt, 0 uncovered.
- Five example records validate.

## Open

- C2PA bridge (next), then SWHID, SPDX, PROV.
- Owner review and the transfer to `cazucito` remain owner decisions.

---

# SESSION — 2026-11-24 (Phase 2: C2PA bridge)

## Objective

Close the C2PA bridge the previous run had left in the tree and red: no ADR, no vector group in the test, no docs.

## Done

- Wrote `docs/adr/ADR-0011-c2pa-bridge-references-the-manifest.md`: reference (the chosen shape) against absorption, application by presence, and no bridge at all. Records that a signed statement cannot be copied into an unsigned sidecar without losing the property that made it worth having.
- Verified the bridge's C2PA 2.2 citations against the published specification instead of trusting the draft. Two statements were wrong and are corrected: the active manifest is the last manifest in the store (§15.5.1), and the manifest store is normally — not mandatorily — an excluded range (§9.1, §9.2).
- Rewrote `C2P-2`: the "recorded verbatim" MUST was untestable (no vector knows what C2PA emitted), so it moved to prose in 90.1 and the rule kept only the checkable shape. The shape check accepts both hex cases and a colon-bearing claim generator; two accept vectors pin the leniency, since C2PA's ABNF is uppercase-only while its libraries emit lowercase UUIDs.
- `spec/vectors/c2pa.json` — 19 vectors (accept/reject), all marked `"bridge": "variorum:c2pa"` except the unclaimed-record accept vector; a rejected JSON `null` claim; `C2P-7`/`C2P-8` exempted with consumer-obligation reasons.
- Schema typed for the claim; `validate_c2pa_bridge` in tool 0.4.0; `C2P` added to the rule families; `C2paBridgeTests` (9 tests) in `tests/test_validate.py`; `c2pa` group expected in `tests/test_vectors.py`.
- Docs brought in line: README counts (138 vectors, ten groups), CHANGELOG, extensions README (c2pa moved to Written), vectors README, PLAN, CON-28 example, STATE, HANDOFF.

## Numbers

- 88 unit tests OK.
- `conform --coverage`: 138/138 PASS; 84/117 rules referenced, 33 exempt, 0 uncovered.
- Five example records validate.

## Decisions

- The bridge is a pointer: three members, nothing copied from the manifest (ADR-0011).
- Identity is still the digest; the C2PA URN never becomes `id` (`C2P-6`).
- The hard binding, ingredients and claim signature are non-mappings, written down as such.

## Open

- SWHID, SPDX, PROV bridges.
- SemVer bridge still treats an explicit `null` claim as absent while the C2PA bridge rejects it; aligning needs a decision and a vector.
- Owner review, transfer to `cazucito`, site domain.

---

# SESSION — 2026-11-24 (Phase 2: SWHID bridge, closed)

## Objective

Close the SWHID bridge the previous run had left in the tree, uncommitted and with one red test.

## Done

- Finished `spec/90-extensions/swhid.md` (`SWH-1`…`SWH-8`) as written by the previous run: one-member claim, strict scheme version 1 shape, context qualifiers held to SWHID's producer constraints, fragment qualifiers refused, identity never a SWHID.
- Took the three hashes of the same 111-byte fixture apart in 90.3 — `a370e4f1…` (digest), `affa1e6d…` (raw SHA-1, unused) and `bad480af…` (git blob SHA-1, the `cnt` SWHID) — and used them to answer the handoff question directly: **no SWHID can be the digest, because the pre-images differ**; for `dir`/`rev`/`rel`/`snp` the subject is not even the artifact's bytes.
- `spec/vectors/swhid.json` — 32 vectors marked `"bridge": "variorum:swhid"`, plus one unmarked accept vector. `SWH-7`/`SWH-8` exempted with consumer-obligation reasons.
- `docs/adr/ADR-0012-swhid-bridge-is-a-sibling-identifier.md`.
- Schema typed for the claim; the `SWH-4` combination rules are declared tool-enforced because JSON Schema cannot condition on another member's value.
- Tool 0.5.0 (`validate_swhid_bridge`, `SWH` rule family); `SwhidBridgeTests` (15 tests) in `tests/test_validate.py`, including `test_the_fixture_swhid_is_recomputed_not_stored` — it rebuilds `blob 111\0` + bytes, hashes it, and asserts the vector base carries that value, so the stored SWHID cannot go stale silently; `swhid` added to the expected groups in `tests/test_vectors.py`.
- Docs brought in line: README counts (170 vectors, eleven groups) and bridge list, CHANGELOG (Added and Changed), extensions README (swhid moved to Written, ADR-0012 cited), vectors README row, PLAN checkbox, STATE, HANDOFF, and the stale "Next session should" block, which still described the C2PA work.

## Numbers

- 103 unit tests OK.
- `conform --coverage`: 170/170 PASS; 90/125 rules referenced, 35 exempt, 0 uncovered.
- Five example records validate.

## Decisions

- Reference, never promote or absorb (ADR-0012): a content hash from another object model is a sibling identifier.
- One SWHID per record; the object type is the producer's choice and each type answers a different question.
- Context qualifiers yes, fragment qualifiers no — a record describes one artifact, and a fragment is not one.
- The record validator checks shape only; relating a `cnt` SWHID to the bytes is `SWH-7`'s consumer obligation, and no vector pretends otherwise.

## Open

- SPDX next; its checksums can coincide with the digest, which is the interesting difference from SWHID.
- SemVer bridge still treats an explicit `null` claim as absent while C2PA and SWHID reject it.
- Owner review, transfer to `cazucito`, site domain, `u-onoma`/`_index` registration.

---

# SESSION — 2026-11-24 (Phase 2: SPDX bridge, and Phase 2 closed)

## Objective

Close Phase 2 with its fourth bridge, answering the handoff's question: SPDX carries checksums in the same algorithms Variorum uses, so can one of them be the digest, and what should the bridge point at?

## Done

- `spec/90-extensions/spdx.md` (`SPDX-1`…`SPDX-8`). The claim is `extensions["variorum:spdx"]` with exactly `version`, `document` and an optional `element`. `version` is a closed list holding `"2.3"` — the `SPDXVersion` without its prefix — because SPDX 3.0 replaced the document model (`spdxId` as an IRI, `namespaceMap`, checksums behind `verifiedUsing`). `document` is the `documentNamespace` (§6.5: absolute URI, scheme required, no `#`, because SPDX reserves the fragment for element URIs). `element` is an `SPDXRef-[A-Za-z0-9.-]+` identifier (§7.2, §8.2), and `SPDXRef-DOCUMENT` is refused: a well-formed identifier and a category error as a subject.
- 90.3 is the load-bearing section: five checksums, three subjects. A file element's `SHA256` **can** equal the digest; its `SHA1` cannot; a package checksum can when the package is one blob and the artifact is that blob (Annex K.2.2.3); the package verification code **never** can, because §7.9 hashes the sorted concatenation of the files' SHA-1 *hex strings* — for the fixture, `SHA1("affa1e6d…5215286c") = 41b0f52089ef07…f7d5ae78`, a third value over text; an `ExternalDocumentRef` checksum covers the document's bytes. 90.3 pairs SPDX's own self-reference argument (Annex K.2.2.1) with `CORE-15`.
- `spec/vectors/fixtures/hello.spdx.json` — a real SPDX 2.3.1 document for the existing 111-byte fixture, with `SPDXRef-Package-hello` (`filesAnalyzed: true`, verification code) containing `SPDXRef-File-hello` (`SHA1` + `SHA256`). Its namespace is the claim's `document` in the vector base record.
- `spec/vectors/spdx.json` — 18 vectors marked `"bridge": "variorum:spdx"`: claim shape, `null`, version missing and `"3.0.1"`, document missing / schemeless / fragment-bearing, `DocumentRef-…`, `SPDXRef-`, underscore, `+`, `SPDXRef-DOCUMENT`, a copied `checksum` member, `id` as namespace and as element URI, plus four accepts (document-only claim, package element, dots-and-uppercase idstring, unclaimed record). `SPDX-7`/`SPDX-8` exempted with consumer-obligation reasons.
- `docs/adr/ADR-0013-spdx-bridge-points-at-the-sbom.md` — why a copy that would often be numerically right is the most dangerous kind.
- Schema typed (`const` version, namespace pattern, element pattern with a `not` guard); tool 0.6.0 (`validate_spdx_bridge`, `SPDX` family); `SpdxBridgeTests` (10 tests), one of which parses the fixture, recomputes both checksums and rebuilds the §7.9 code; `spdx` added to the expected groups. README, CHANGELOG, PLAN, extensions README and vectors README updated; STATE and HANDOFF rewritten.

## Numbers

- 113 unit tests OK.
- `conform --coverage`: 188/188 PASS; 96/133 rules referenced, 37 exempt, 0 uncovered.
- Five example records validate.

## Decisions

- Reference, never copy (ADR-0013): the equality between a file element's `SHA256` and the digest is a reader's check, not a licence to write the digest from the document.
- `version` is a closed list, because a 3.0 document under 2.3 rules would be a claim nobody specified.
- `element` is optional; absent means "in this document's scope", and `SPDXRef-DOCUMENT` is refused rather than silently ignored.
- Identity stays the digest; a namespace or an element URI is a name that changes when the document is reissued and cannot be recomputed from the bytes.

## Open

- Phase 2 is closed. Phase 3 starts with `docs/adoption.md`: the core-only path, written by actually recording one real release from a project already in `examples/`.
- SemVer bridge still treats an explicit `null` claim as absent while C2PA, SWHID and SPDX reject it.
- SPDX 3.0 and CycloneDX stay separate bridges; each needs its own claim shape and ADR.
- Owner review, transfer to `cazucito`, site domain, `u-onoma`/`_index` registration.

---

# SESSION — 2026-11-25 (Phase 3: the adoption guide and the README's front door)

## Objective

Close Phase 3's first task. The previous run had written `docs/adoption.md` and `examples/instruisto-release-copilot/` and left them uncommitted, with one open question about the README: its Quick example was reported to teach three shapes the validator rejects.

## Done

- **The guide was re-walked.** Downloaded both assets of `github-copilot-agents/v1.1.0` from `cazucito/instruisto`, confirmed sizes against the release API (73,506 B / 148,743 B) and recomputed both digests: `2605defcf2a7aafb…` and `60d62fe0bbe732bc…`, which are what the two records carry. `stamp` with the guide's exact flags reproduces `60d62fe0bbe7.variorum.json` member for member except `created`. `stamp` without `--scheme` writes `{"name": "none"}` as the guide says; the public asset URL answers `404` with a nine-byte body as pitfall 2 says.
- **Two imprecisions in `docs/adoption.md` fixed.** The §1 table now distinguishes the required `artifact.digest` (`ID-2`) from the descriptive `size`, `mediaType` and `name`; §3 no longer says `stamp` writes "the five required members and nothing else", because it also fills those three and writes `producer` when given one — what it never writes is a conformance declaration or an invented section.
- **The README Quick example replaced with a real record.** It had `lineage.parents` as an array of strings, `state.transitions[].actor` as a string and elided digests: a validator-rejected shape in the most copied block in the repository. It is now `examples/la-enpenso-shot-01/b0d1bfac8fc9.variorum.json` verbatim. The third reported defect (`recipe.tool` as an object) was not one: `$defs/tool` allows `{name, model, snapshot}`.
- **`ReadmeExampleTests`** in `tests/test_docs.py`: exactly one ```json block in the README, and it must equal a shipped record; validity is covered by `ExamplesTests` on the same bytes, so the test guards the copy.
- README's field table first row: `identity` → `artifact` and the derived `id`. These are the members; `identity` is a section title.
- `examples/README.md` gained the missing `instruisto-release-copilot` row. CHANGELOG: three `Added` entries and one `Changed`. PLAN: Phase 3 first box checked. STATE rewritten, HANDOFF prepended.

## Numbers

- 114 unit tests OK.
- `conform --coverage`: 188/188 PASS; 96/133 rules referenced, 37 exempt, 0 uncovered.
- Seven example records validate (one pre-existing `REC-5` warning, a SHOULD).

## Decisions

- The README's example is a shipped record rather than an invented skeleton. A storefront that teaches a shape the validator rejects makes every reader's first record invalid, and no other check in the repository reads prose.
- The test asserts equality with a shipped record instead of re-validating: the validator already runs on those bytes through `ExamplesTests`, and the failure mode being guarded is drift, not invalidity.

## Open

- Phase 3 continues with three case studies — adoption in a project's own repository, not another record under `examples/`.
- Owner review of the draft, transfer to `cazucito`, site domain, `u-onoma`/`_index` registration.
- SemVer bridge still treats an explicit `null` claim as absent while C2PA, SWHID and SPDX reject it.
- PROV bridge planned; `conform --verbose` still has no skipped-bridge report; one `semver.tag` per record.
