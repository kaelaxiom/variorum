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

# SESSION — 2026-11-25 (Phase 3: the first case study)

## Objective

Turn Phase 3's first case study from a plan into an adoption performed in another repository, then write it up from the adopter's side.

## Done

- **Read the adopter before designing the record.** `software-tools` is an archive, not a release pipeline: 58 fichas, a PHP 8.1 + SQLite site, 91 download rows in its exported inventory, and an admin panel that already stores a `sha256` per hosted file. Its ADR-011 splits downloads into four axes (work, version, variant, era) plus a year — which decides what `scheme.version` means for every artifact the archive will ever record.
- **Fetched the artifact back from production instead of trusting the catalogue.** Unlocked the private collection with the general password from BWS, downloaded `Gel86a.zip` (2,520,484 B, `Content-Length` agreeing), ran `unzip -t` (no errors) and hashed it: `fc0cadf23dc1…`, identical to the value the panel stored for the `gel` row. The digest came from the bytes; the panel's value was confirmed by it, not copied into it.
- **Wrote `ops/tools/variorum_record.py` in the adopter's repository** (218 lines, stdlib only): `stamp` computes digest and size and writes `<digest-prefix>.variorum.json` (`CORE-13`); `check` recomputes both and exits 1 when they diverge. There is deliberately no option that accepts a digest, and `--conformance` refuses to declare a class whose member the record does not carry.
- **Emitted one record and explained the ninety that were not emitted.** `ops/records/fc0cadf23dc1.variorum.json` (core) plus `ops/records/README.md` and `docs/variorum.md` (Spanish, the adopter's language for docs). The reason the rest stay unrecorded is written where the next agent of that repository will read it.
- **Decisions taken in the adopter's terms:** `version: "8.6"` (ADR-011 calls 8.6a the *variant*; `SCH-7` makes the label the project's and opaque), `authority` = the ADR that defines the scheme (`SCH-4`; a site URL would have been decoration), `producer` = `software-tools` with the script named (00-overview §4: the record's creator), and no `state`/`recipe`/`lineage` — `STA-7` would have forced `"draft"` on a file served since 2002.
- **On this side:** `docs/case-studies/README.md` (the bar: real adopter, computed digest, declaration, friction), `docs/case-studies/software-tools.md`, `docs/adoption.md` §12, README pointer and layout row, `CaseStudyIndexTests`, PLAN split into three boxes, CHANGELOG, STATE.
- `software-tools` commit `e0a739f` pushed.

## Numbers

- 115 unit tests OK (was 114; `CaseStudyIndexTests` added).
- `conform --coverage`: 188/188 PASS; 96/133 rules referenced, 37 exempt, 0 uncovered.
- Seven example records validate.
- Adopter's record: reference `validate --artifact` → `OK — record conforms to Variorum 0.1 (core)`; adopter's `check` → `0` on the real file, `1` on a different one.

## Decisions

- **A case study's record lives in the adopter's repository, not in `examples/`.** The example set holds records this repository ships; the case study is evidence that someone else can ship one, and its commit is the proof.
- **One record, not ninety-one, is the honest adoption.** A record copied from a catalogue is a claim wearing evidence's clothes; the case study says so in the adopter's own words instead of quietly producing ninety plausible files.
- **The version axis belongs to the adopter's taxonomy.** The record says `8.6` while the artifact is called `Gel86a.zip`; refining it would have been the adoption overruling the project it was adopted by.
- **The index is tested.** A case study with no row in `docs/case-studies/README.md` now fails the suite — the `examples/README.md` table had already drifted once.

## Open

- Two more case studies: a project that produces what it records, exercising `recipe` or `state`.
- Owner review, transfer to `cazucito`, site domain, `u-onoma`/`_index` registration.
- `software-tools` cannot serve the record beside the download without a streamer change: owner decision.
- SemVer bridge still treats an explicit `null` claim as absent while C2PA, SWHID and SPDX reject it; PROV bridge planned; `conform --verbose` still has no skipped-bridge report; one `semver.tag` per record.

# SESSION — 2026-11-25 (Phase 3: the second case study, in `3d-printerator`)

## Objective

Close the case study the previous run left uncommitted, then adopt the format in a second real repository — one that builds what it records — and write it up from the adopter's side.

## Done

- **Committed the previous run's work after re-verifying it.** `conform --coverage` 188/188, seven examples, the adopter's record still matching its artifact; commit `8dbb6dd` carries `docs/case-studies/` (index + `software-tools.md`), `docs/adoption.md` §12, the README pointer and `CaseStudyIndexTests`.
- **Chose `3d-printerator` as the second adopter** because it is the opposite direction from the archive: a CAD repository where the STL is the output of a text source and a declared toolchain, and where the repository's own convention (`designs/<solution>/vN/`, OpenSCAD 2021.01, `--export-format binstl`) already names the recipe Variorum asks for.
- **Wrote `tools/variorum_record.py` in the adopter's repository** (290 lines, stdlib): `stamp` computes the artifact's digest and size and the `--source` digest, writing both into `recipe.source` and `lineage.parents`; `check` recomputes all three. No option accepts a digest, and a claims file that states a `digest` or an `id` is rejected with exit 2 — this record has two digests in it, so the guard had to cover both.
- **Stamped one record** for `aw9-d2strap-case-v2-holder.stl` (374,684 B, `cf3a7707…`): `core`, `lineage` (`render` of the 28,155 B `.scad`, `916c01f5…`), `recipe` (build, `openscad 2021.01`, `part=holder`, `export_format=binstl`) and `state` `candidate → rejected`.
- **Measured instead of assuming determinism.** OpenSCAD 2021.01 was installed on this machine at the exact version the repository declares, so the build was re-run twice: the committed STL and both rebuilds hold the same 7,492 triangles *exactly* — same vertices, normals, attribute words, header and bounding box — and three different digests, because the facet order differs. That is why the record has no `determinism` member: `"full"` is forbidden by `REC-13`, `"none"` would misstate the geometry, and `REC-12` has no value for the case in between.
- **Exercised the guards before saying they work:** a claims file with a digest → exit 2 with the offending path; `check` against a different STL → exit 1 with both digests; `check` against a different `.scad` → exit 1 with both source digests and the parent mismatch.
- **Adoption found two defects on this side, both fixed:** `show` printed `recipe build via ?` for a legal `recipe.tool` array (`REC-5`, schema `oneOf`) — fixed in 0.6.1 with `ShowTests`; `docs/adoption.md` §1 and §9 called `state` a separate class when `CON-3` puts it inside `core` — fixed in both places.
- **On this side:** `docs/case-studies/3d-printerator.md`, the index row, the PLAN box, CHANGELOG and STATE. The case study quotes the adopter's record verbatim, checked by parsing both files and comparing them member for member.

## Numbers

- 120 unit tests OK (was 115; `ShowTests` adds five).
- `conform --coverage`: 188/188 PASS; 96/133 rules referenced, 37 exempt, 0 uncovered.
- Seven example records validate.
- Adopter's record: reference `validate --artifact` → `OK — record conforms to Variorum 0.1 (core, lineage, recipe)` with no warnings; adopter's `check` → `0` on both files, `1` on a different STL and a different `.scad`.
- `3d-printerator` commit `faa987c` (511 insertions, none in the design files).

## Decisions

- **One record out of seven files, again.** The fit tests never had a lifecycle (`STA-7` would force `draft` on files that already served their purpose) and v1 has no documented approval, so `superseded` — reachable only from `approved` or `published` — would have been invented. Silence is a legitimate answer.
- **`at` is the commit timestamp.** The project has no decision log apart from git; citing the moment the decision entered the history is verifiable, and reconstructing an hour nobody wrote down is not.
- **The first transition names the coding agent, not the owner.** `CLAUDE.md` is the agent's contract and the commit bodies narrate its work; the commits carry the owner's git identity, which is exactly why `attestation` exists and why the case study says it was not adopted.
- **No `sequence`.** The project's label orders design folders, and three STLs of one iteration would tie at the same number; an order that cannot increase strictly (`SCH-9`) is better omitted.
- **The `determinism` gap is written down, not patched.** A fourth enum value would be a normative change needing an ADR, schema, vectors and CHANGELOG, and one measurement does not justify changing a shipped format.

## Open

- Third case study: a content project with a generative recipe, or one willing to sign.
- The `determinism` value question — owner's call before 0.2.
- `CLAUDE.md` in `3d-printerator` was not edited (approval-protected, no approver in this run); the tool is documented in `docs/variorum.md` and the README.
- Owner review, transfer to `cazucito`, site domain, `u-onoma`/`_index` registration.
- The older consistency items unchanged: SEM `null`, `conform --verbose`, one `semver.tag`, `SPDX-7`, CycloneDX, PROV.

# SESSION — 2026-11-26 (Phase 3: the third case study, in `echo-language`)

## Objective

Ship the case study the previous run wrote but did not commit, after checking it against the files it describes, and close Phase 3's case studies.

## Done

- **Re-derived every number in `docs/case-studies/echo-language.md`.** SHA-256 and size of the four takes recomputed (3,650,777 / 3,548,907 / 4,286,810 / 4,097,358 B); durations read with `ffprobe` (158.280 / 152.880 / 186.648 / 178.128 s); the JSON block in the document parsed and compared member for member with the committed take-04 record (equal); the adopter's `check` run on all four records (`0`) and against a mismatched take (`1`, both digests printed); the C2PA hard binding recomputed for every take — SHA-256 over the file minus the 13,659-byte exclusion starting at byte 18,915 — reproducing `709d7fe7…` for take 04 against a Variorum digest of `ba774da9…`.
- **Corrected two statements the previous run left imprecise.** The "three takes are `revision` siblings" sentence belongs to the paragraph under `LIN-6`, not to `LIN-6`; and the prompt/`USLT` equality holds at 667 characters for takes 02–04 only — take 01's frame is 709 because the provider repeats the final `[Outro]` section. The case study now says the tag is a transcription that can drift, and the adopter's own `docs/variorum.md` carries the same correction.
- **Fixed two defects in the adopter's stamper** (`tools/variorum-record/main.py` in `echo-language`): `frame_language_text` returned the frame's content descriptor instead of its text, so every UTF-8 `USLT` decoded as `""`; `reject_derived` exited 1 where three documents promised 2. Added `tests/test_variorum_record.py` (13 tests). Adopter's suite 78 → 91, all green. Commit `2232272`, pushed.
- **Fixed a documentation defect in all three case studies:** "What a consumer can check" ran `python3 tools/variorum.py` with the adopter's paths, as if the two repositories were one directory; the comment now says the reference command runs in a checkout of this repository.
- **On this side:** the case study file, its row in `docs/case-studies/README.md`, the PLAN box, a CHANGELOG `Added` entry and a `Changed` entry, STATE and HANDOFF.

## Numbers

- 120 unit tests OK.
- `conform --coverage`: 188/188 PASS; 96/133 rules referenced, 37 exempt, 0 uncovered.
- Seven example records validate.
- `echo-language` commit `2232272` (4 files, 209 insertions); `software-tools` `e0a739f` and `3d-printerator` `faa987c` unchanged and clean.

## Decisions

- **The case study quotes the record, it does not paraphrase it.** Comparing the parsed JSON block with the committed file member by member is what caught nothing this time — and is the only reason to trust that it will next time.
- **A provider's tag is evidence, not a checksum.** Take 01 proves the distinction: the lyrics Suno wrote back repeat the outro, so the tag can drift from the prompt while the prompt is what was sung.
- **A defect found while documenting an adopter is fixed in the adopter's repository, not worked around in the case study.** The exit-code mismatch and the empty lyrics were both real; recording them as quirks would have left a tool that lies to its own documentation.

## Open

- Phase 3's remaining work is the site, which needs a domain (owner).
- Three normative questions for 0.2, each needing an ADR: `REC-12`'s missing determinism value, `REC-9`'s single prompt field, and a `generated` state.
- Owner review, transfer to `cazucito`, `u-onoma`/`_index` registration.
- The older consistency items unchanged: SEM `null`, `conform --verbose`, one `semver.tag`, `SPDX-7`, CycloneDX, PROV.

# SESSION — 2026-11-27 (the PROV bridge, closed)

## Objective

Finish the bridge the previous run left written, uncommitted and red — and decide whether what it claims about PROV is true.

## Done

- **Fixed the one failing test, and confirmed the rule was not at fault.** `ProvBridgeTests.test_the_claim_requires_no_section_and_forbids_none` passed its sections to `claimed(**claim)`, which places members inside `extensions["variorum:prov"]`; `PROV-3` closes that object, so the rejection was correct. The test now uses `record_with(extensions=..., producer=..., lineage=..., recipe=..., state=...)`. The bridge's own vector `prov/claim-survives-a-full-projection` already asserted the valid shape, which is what identified the helper as the defect.
- **Audited every PROV citation against the published documents** before committing. PROV-DM: §5.1.1/§5.1.2/§5.3.1 definitions; §2.1.2 "PROV does not attempt to specify the conditions under which derivations exist"; §5.2.2 revision, §5.2.3 quotation, §5.2.4 primary source; §5.7.1 "two entities (resp. activities, agents) are equal if they have the same identifier"; §5.7.2 the five reserved attributes; §5.7.2.5 `prov:value` may occur at most once, and Example 53's two entities sharing a value; §5.7.3 "interpretation is outside the scope of PROV"; §5.7.5 qualified name → IRI; §5.4 "a bundle is a named set of provenance descriptions, and is itself an entity"; §5.5.1 "a specialization is not, as defined here, also an influence"; §6 reserved extensibility attributes and Example 56 (a translation typed as a sub-relation of derivation). PROV-CONSTRAINTS: §1.2 anonymous toplevel instance and "PROV instances need not be valid"; §2.4 a graph is violated only by a cycle that includes a strictly-precedes edge; §7.2 "the names of its bundles are distinct". PROV-O: `generatedAtTime` "the time at which an entity was completely created and is available for use"; `invalidatedAtTime` "no longer usable".
- **Corrected one quotation.** The draft claimed §5.5.2 says alternates "fix some aspects of some common thing"; the section says "Two alternate entities present aspects of the same thing". Fixed in `spec/90-extensions/prov.md` 90.6.
- **Finished the documentation the previous run had not started:** README (both PROV mentions and the 188→200 vector count), `spec/00-overview.md` §8, `spec/90-extensions/README.md` (prov.md Written, five bridges, ADR-0014), `spec/vectors/README.md` (group row), CHANGELOG (Added/Changed), CONTEXT, PLAN, STATE, this file and HANDOFF.
- **One unrelated defect, fixed while verifying:** `variorum validate <directory>` raised `IsADirectoryError` as a traceback although `load_record`'s docstring promises a readable error. It now exits 1 with `<path>: not a file` — the sentence `digest` and `stamp` already use — and `RecordLoadingTests` covers a directory and a missing path.

## Numbers

- 128 unit tests OK.
- `conform --coverage`: 200/200 PASS; 99/139 rules referenced, 40 exempt, 0 uncovered.
- Seven example records validate.

## Decisions

- **A vector and a unit test are two implementations of one rule; when they disagree, read both before editing either.** The failing test said `PROV-3` was wrong; the vector exercising the same rule said the test was. The vector won because it is the conformance contract (`ADR-0006`) and the test is a convenience around it.
- **A projection bridge is worth writing even though it has no document to point at.** The four earlier bridges answer "where does the record point"; this one answers "what does each member become", and the three mistakes it names — `created` on the entity, `producer` as attribution, `generation` as Generation — are mistakes a reader would otherwise make plausibly.

## Open

- Owner review, transfer to `cazucito`, site domain, `u-onoma`/`_index` registration.
- Three normative questions for 0.2: `REC-12`'s determinism value, `REC-9`'s single prompt field, a `generated` state.
- The older consistency items: SEM `null`, `conform --verbose`, one `semver.tag`, `SPDX-7`, CycloneDX.

# SESSION — 2026-11-27 (afternoon): the PROV commit, and a null that was not a claim

## Objective

Commit and push the PROV bridge the previous run left in the tree, then close one open consistency item without inventing normative changes.

## Done

- **Committed and pushed the PROV bridge as `25bac33`.** Re-ran the suite and read the full diff before committing: 128 tests, 200/200 vectors, seven examples, schema claim closed, tool 0.7.0, `PROV` in `RULE_FAMILIES`, all docs updated. Nothing needed repair; the previous run's stop was purely the iteration limit. Pushed to `main`, HEAD equals remote.
- **Fixed the SemVer bridge's handling of an explicit `null` claim.** `validate_semver_bridge` read `extensions.get(...)` and returned on `None`, so a record carrying `"variorum:semver": null` skipped `SEM-1`..`SEM-5` and validated; the four bridges written later all test key membership and reject `null`. Changed to `if SEMVER_BRIDGE not in extensions: return`, then read the value. This is the implementation matching existing text, not a rule change: `SEM-1` says "When present, its value MUST be an object" and the schema types all five claims as objects.
- **Added `semver/claim-must-not-be-null`** to `spec/vectors/semver.json` (reject, `SEM-1`) and widened `SemverBridgeTests.test_claim_must_be_an_object` to five non-object values in subTests. Suite 200 → 201 vectors; tests stay 128.
- **Documentation:** CHANGELOG `Fixed` entry, README vector count, STATE counts, HANDOFF and this file. The four older HANDOFF sections keep their "SEM null" open item because they record what those sessions left open; the new section closes it.

## Numbers

- 128 unit tests OK.
- `conform --coverage`: 201/201 PASS; 99/139 rules referenced, 40 exempt, 0 uncovered.
- Seven example records validate.
- `25bac33` pushed; tree clean at the end of the PROV work before this commit.

## Decisions

- **A consistency defect in one bridge is not grounds for a normative change in the other four.** The tempting "fix" was to make the other bridges tolerate `null` the way SEM did; the text and the schema both said the opposite, so the one implementation that disagreed was the defect.
- **Extend the existing test rather than add a near-duplicate.** `test_claim_must_be_an_object` is exactly the rule under repair; a second test method would assert the same predicate for one more value.

## Open

- Owner review, transfer to `cazucito`, site domain, `u-onoma`/`_index` registration.
- Three normative questions for 0.2: `REC-12`'s determinism value, `REC-9`'s single prompt field, a `generated` state.
- Remaining consistency items: `conform --verbose` has no skipped-bridge report, one `semver.tag` per record, `SPDX-7` stated but not performed, CycloneDX still planned.

# SESSION — 2026-11-27 (evening): determinism gets a content grade

## Objective

Close one of the three normative questions the Phase 3 case studies produced, end to end: the `REC-12` gap the `3d-printerator` measurement exposed. No owner decisions involved.

## Done

- **`REC-12` gained a fourth grade, `content`, and the four are now defined.** `none`, `seeded`, `content` and `full` had only ever been listed; the table states what each claims. `content` is the measured middle: the same values under a stated normalization, not necessarily the same bytes. `REC-13` was extended rather than duplicated — a `content` claim requires a verified re-execution exactly as `full` does.
- **`REC-22` (new, SHOULD):** a `content` claim SHOULD state its normalization in `parameters.normalization` (on the recipe, or on the hybrid stage that carries the claim); the tool warns when it is absent. A dedicated member was considered and rejected — `parameters` already holds producer facts no rule can verify, and a member would add surface without adding a check.
- **Fixed the schema defect the member exposed:** `recipe.determinism` was an `enum`, although `REC-12` is a SHOULD, so a standard JSON Schema validator rejected a record `CON-8` calls conformant. The property now carries a description and no assertion.
- **`tests/test_schema.py` (new).** The schema had never been read by a test. It now pins every closed vocabulary the schema and the tool share (recipe kinds, the seven states in three places, the eight relations, actor kinds, algorithms, conformance classes, the five bridge keys) and asserts that `determinism` carries no `type`, `enum` or other assertion.
- **Three vectors, all accepts:** `content` with normalization, `content` without (warning, not invalidation), and an unrecognised grade (the over-strictness guard). Suite 201 → 204.
- **Case study brought forward:** `3d-printerator.md` dates its record's absence to stamping and says the gap is closed by ADR-0015; the record itself may add the grade in one edit (its rebuilds already satisfy `REC-13`), in the adopter's repository.
- ADR-0015; CHANGELOG (`Added`, `Changed`, `Fixed`); README and vectors README counts; PLAN gained the 0.2 questions with this one checked; STATE and HANDOFF updated.

## Numbers

- 139 unit tests OK (was 128).
- `conform --coverage`: 204/204 PASS; 100/140 rules referenced, 40 exempt, 0 uncovered (was 201/201, 99/139).
- Seven example records validate.

## Decisions

- **A grade, not a domain word.** `geometry` would name the CAD case and misname every other medium; `content` names what is determined, whatever the serializer calls it. `canonical` would assert a property of the artifact the record cannot know.
- **A SHOULD, not a MUST.** The case for `content` is that a vocabulary cannot foresee every case; a MUST on the value space would make the next unforeseen case invalid and teach producers to omit the member.
- **The schema must not be stricter than `CON-8`.** This is the same rule the extension-name pattern already followed; the test makes it hard to undo.
- **Extend `REC-13` instead of adding a near-duplicate rule.** Both grades are unverified-claim prohibitions; one identifier, two clauses.

## Open

- Owner review, transfer to `cazucito`, site domain, `u-onoma`/`_index` registration.
- Two normative questions for 0.2: `REC-9`'s single prompt field, a `generated` state.
- Remaining consistency items: `conform --verbose` has no skipped-bridge report, one `semver.tag` per record, `SPDX-7` stated but not performed, CycloneDX still planned.

# SESSION — 2026-11-28 (early): the prompt is one field, and the record names it

## Objective

Close the second normative question the Phase 3 case studies produced: `REC-9` assumed a generator with one prompt field, and Suno's Custom mode has six textual inputs and no box called "prompt".

## Done

- **`REC-9` rewritten.** `recipe.prompt` MUST hold, verbatim, the value of one field the generator accepts — never a concatenation, never a paraphrase — and an absent `recipe.promptField` leaves the mapping unspecified rather than implying the generator has one field.
- **`REC-23` (new, SHOULD):** a generator with more than one textual field SHOULD name the field `prompt` holds in `recipe.promptField`, using the provider's own name, and SHOULD record the remaining fields in `parameters` under their provider names (`REC-11`).
- **`REC-24` (new, MUST):** `promptField`, when present, MUST be a non-empty string and MUST NOT appear without `prompt`.
- `docs/adr/ADR-0016-the-prompt-is-one-field-and-the-record-names-it.md` — four options (an object of named fields, the provider's literal `prompt`, a semantic winner defined in the rule, one string with a declared field name), why the object repeats the split ADR-0015 refused and why the vendor's literal name would move the standard's answer with the vendor.
- Schema types `recipe.promptField` (`minLength: 1`) and binds it to `prompt` with `dependentRequired`; tool 0.9.0 checks both clauses, for a recipe and for every hybrid stage (`REC-19`), and warns on nothing when the member is absent.
- Four vectors in `spec/vectors/recipe.json` (one accept, three rejects); four tests in `tests/test_validate.py`, one pinning that an unnamed prompt draws no warning.
- `docs/case-studies/echo-language.md` records that the question it left open is closed and that `"promptField": "lyrics"` is one edit in the adopter's repository.

## Numbers

- 208 vectors in thirteen groups; `conform --coverage` 102/142 referenced, 40 exempt, 0 uncovered.
- 143 unit tests — re-run green at the start of the lifecycle session on the same day, because this commit did not update STATE, HANDOFF or this file.

## Decisions

- **Absence is silence, not completeness.** Making an absent `promptField` mean "the generator has one field" would repeat the defect ADR-0015 closed for `determinism`: a decision no producer made, read as a claim.
- **One string plus a label, not an object.** An object of named fields gives a member every consumer reads as a string a second grammar and duplicates `parameters` for the non-text half of the same call.

## Open

- The lifecycle question — whether a generated take gets a state of its own — closed later the same day by ADR-0017.
- Owner review, transfer to `cazucito`, site domain, `u-onoma`/`_index` registration.
- The documented deferrals: `conform --verbose` has no skipped-bridge report, one `semver.tag` per record, `SPDX-7` stated but not performed, CycloneDX planned.

# SESSION — 2026-11-28 (lifecycle): two premises, no `generated` state

## Objective

Close the last normative question the Phase 3 case studies produced: what a generated take that was produced but never judged records as its state.

## Done

- **`STA-7` and `STA-9` extended.** With no transitions, `current` MUST be `draft` or `candidate`; the first transition MUST start at `draft` or `candidate`. §5.3 now states the principle: only a premise may be held without a transition, and every state that asserts a decision requires one. §5.2's glosses and the seven values are untouched.
- **`candidate → archived` added to §5.4.** Shelving a batch nobody judged is a decision about activity, not a judgement of the work; without it a record would have to record a rework it never did.
- **`state` is not provenance.** §5.6 says why there is no `generated` state: that a model made the bytes is `producer.kind` and `recipe.kind` (tool, model, prompt, determinism), and `state` records decisions.
- **ADR-0017** records four options — add `generated` (refused: provenance in a section about decisions, and a second premise no rule can distinguish from `draft`), redefine `draft` as "undecided" (refused: answers by emptying the word, leaves finished work labelled unfinished), silence as the only answer (refused: makes the most common machine workflow inexpressible), two premises with no new vocabulary (chosen).
- **Schema:** a `description` on the `state` object; no new assertion. `STA-7`/`STA-9` are relational and were never expressible there.
- **Tool 0.10.0:** `INITIAL_STATES = {"draft", "candidate"}` gates both rules; `LEGAL_TRANSITIONS["candidate"]` gains `archived`.
- **Vectors:** two replaced, three added. `state/empty-transitions-mean-draft` became `state/empty-transitions-cannot-claim-a-decision` (`approved`, no transitions), and `state/first-transition-starts-at-draft` became `state/first-transition-starts-at-a-premise` (`approved → published` with no earlier history). New accepts: born a `candidate`, rejected without a draft step, archived without a judgement. 208 → 211.
- **Tests:** replaced `test_first_transition_must_start_at_draft` — its fixture used `candidate → candidate`, which `STA-10` rejects on its own — with `test_first_transition_must_start_at_a_premise`, and added four for the premises, the still-invalid decision state and the two new edges. `StateVocabularyTests` in `tests/test_docs.py` now compares §5.2's table with `variorum.STATES`.
- **Case studies:** `echo-language`, `software-tools` and `3d-printerator` no longer reason from the old clause; `echo-language` states that the batch can now carry `candidate` with no transitions.

## Numbers

- 148 unit tests OK (was 143).
- `conform --coverage`: 211/211 PASS; 102/142 rules referenced, 40 exempt, 0 uncovered.
- Seven examples validate; the `software-tools-inventory` record keeps its known `REC-5` warning.

## Decisions

- **A transition is an attestation; never require one to reach a state that asserts no decision.** The old rule forced a fabricated `draft → candidate` on every artifact born complete — the one thing a record must not do.
- **The vocabulary does not multiply with the number of ways an artifact can be made.** `candidate` was already the right word; the fix was to let it be held without a transition, not to add `generated`.
- **Two premises, one rule.** `draft` and `candidate` are the only states that assert no decision, and the only two an empty transition list may hold; the five decision states keep their actor-and-timestamp requirement.
- **A third rendering deserves a test.** The spec table defines the vocabulary; nothing read it. `StateVocabularyTests` closes the triangle with `tests/test_schema.py`.

## Open

- Owner review, transfer to `cazucito`, site domain, `u-onoma`/`_index` registration.
- Phase 3's remaining work is the site (domain) and the announcement; no normative question from the case studies is open.
- The documented deferrals: `conform --verbose` has no skipped-bridge report, one `semver.tag` per record, `SPDX-7` stated but not performed, CycloneDX planned.

# SESSION — 2026-11-28 (conformance profile): a report that accounts for what it skipped

## Objective

Close the oldest documented deferral: `conform --verbose` had no "skipped bridge vector" report, so `CON-9`'s permission to skip a bridge an implementation does not claim left the report unaccountable.

## Done

- **`CON-29` (new, §7.5).** A conformance report MUST account for every vector in the suite — passed, failed or skipped — and a skipped vector MUST name whether its class or its bridge was not claimed (`CON-9`). An implementation MAY produce the accounting on request, but MUST NOT state a pass total without the vectors it did not run.
- **`conform --verbose` prints the suite's profile.** One line per class (total, vectors without a bridge claim, bridge-only ones), one line per bridge (total and classes spanned), and one line reconciling a `core`-and-no-bridge claim with the suite total — 67 of 211 run, 144 skipped (93 bridge-only, 51 in other classes). Every number is derived from the loaded vectors; nothing is stored in a document.
- **`CONFORMANCE_CLASS_ORDER`** added beside `CONFORMANCE_CLASSES`, which is now derived from it, so the four class names have one ordered source (the profile's row order, and the order every other listing can adopt).
- **`ProfileTests`** in `tests/test_vectors.py` (six tests): class lines sum to the suite total, each bridge has exactly one line with its count, the reconciling line adds up, `--verbose` prints the block, the default report does not.
- **ADR-0018** — four options (leave it; a JSON report with its own schema; one line per skipped vector; a derived profile plus a rule), why `CON-10`'s argument applies one level up, and why the counts must be computed rather than documented.
- **Docs:** §7.5 defines the profile; `spec/vectors/README.md` and `README.md` point at it; CHANGELOG records `CON-29` and tool 0.11.0.

## Numbers

- 154 unit tests OK (was 148).
- `conform --coverage --verbose`: 211/211 PASS; 102/142 rules referenced, 40 exempt, 0 uncovered. `CON` rules stay outside the coverage denominator, so `CON-29` needs no vector and no exemption.
- Seven examples validate, unchanged.

## Decisions

- **A skip rule without a denominator is not a conformance result.** `CON-9` said implementations MUST skip unclaimed bridges; nothing said a report must say how many. The same argument `CON-10` makes for rejections — cite the rule, or the verdict is untraceable — applies to a pass over an unstated subset.
- **The profile describes the suite and a claim, not the run.** It prints when everything passes, which is exactly when a green report needs to say what it did not measure.
- **No stored counts.** A document with "67 of 211" would be stale at the next vector; the numbers are computed from the suite and the tests recompute them.

## Open

- Owner review, transfer to `cazucito`, site domain, `u-onoma`/`_index` registration.
- The documented deferrals left: one `semver.tag` per record, `SPDX-7` stated but not performed, CycloneDX planned.
