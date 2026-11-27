# HANDOFF

## Last session — 2026-11-27 (the PROV bridge, closed)

**Did:** closed the PROV bridge the previous run left written, uncommitted and red — one failing unit test, no documentation or changelog, nothing pushed.

- **The red was a defect in the test, not in the rule.** `ProvBridgeTests.test_the_claim_requires_no_section_and_forbids_none` built its "full" record with `claimed(**sections)`, which put `producer`, `lineage`, `recipe` and `state` *inside* the claim object, so `PROV-3` rejected it exactly as written. The test now builds the same record with `record_with(extensions=..., producer=..., lineage=..., recipe=..., state=...)`, sections at the top level where the projection names them. Nothing in `tools/variorum.py` changed for this: `prov/claim-survives-a-full-projection` already proved the rule accepts the valid shape, which is why the failure pointed at the helper.
- **Every citation was opened before merging** — the lesson the C2PA bridge cost. Checked against PROV-DM (§5.1.1, §5.1.2, §5.3.1 definitions; §2.1.2 derivations determined "by unspecified means"; §5.2.2–§5.2.4 revision, quotation, primary source; §5.7.1 identifier equality; §5.7.2 the five reserved attributes; §5.7.2.5 `prov:value` at most once and Example 53's two entities with one value; §5.7.3 "interpretation is outside the scope of PROV"; §5.7.5 qualified name mapped to an IRI; §5.4 bundle; §5.5.1 specialization is not an influence; §6 sub-relations via `prov:type`, with Example 56's translation), PROV-CONSTRAINTS (§1.2 anonymous toplevel instance, "PROV instances need not be valid"; §2.4 a cycle is a violation only when it includes a strictly-precedes edge; §7.2 "the names of its bundles are distinct") and PROV-O (`generatedAtTime` "completely created and is available for use"; `invalidatedAtTime` "no longer usable").
- **One quotation was wrong and is fixed.** The draft attributed to §5.5.2 the words "fix some aspects of some common thing"; §5.5.2 actually says "Two alternate entities present aspects of the same thing". The sentence now quotes that. It was a quotation with a section number next to it — the exact shape that survives review until someone follows it.
- **Documentation:** `README.md` (bridge list, vector count 188→200, Status), `spec/00-overview.md` §8 (PROV now points at the bridge instead of calling it planned), `spec/90-extensions/README.md` (`prov.md` moved to Written; "all five bridges"; ADR-0014 sentence), `spec/vectors/README.md` (`prov` group row), CHANGELOG (`Added`: the bridge, 12 vectors, ADR-0014, `PROV-1`…`PROV-3` and tool 0.7.0; `Changed`: the schema claim, the three exemptions, the four docs), CONTEXT and PLAN.

**Verified:** 128 unit tests OK; `conform --coverage` 200/200 PASS (99/139 referenced, 40 exempt, 0 uncovered); all seven examples validate.

**Left open:**
- Owner review of the whole draft and the transfer to `cazucito`. Unchanged, still the only blocker on a public announcement.
- **Phase 3's case studies are complete; the site is what remains**, and it cannot start without a domain. Owner decision.
- **Three normative questions the case studies produced**, each needing an ADR before 0.2: `REC-12` has no value for a build that fixes every vertex and no byte (from `3d-printerator`); `REC-9` assumes one prompt field where Suno's Custom mode has six (from `echo-language`, which puts the lyric field in `recipe.prompt` and the rest in `parameters`); and the lifecycle vocabulary has no `generated` state — a take that was produced but never judged fits neither `draft` nor `candidate`, and `STA-15` makes silence legal but says nothing about a generator recording its own output.
- Consistency item (open since the C2PA bridge): `C2P-1`, `SWH-1`, `SPDX-1` and now `PROV-1` reject an explicit JSON `null` claim; `SEM-1` treats `null` as absent and returns early. Aligning SEM is a behaviour change to a shipped bridge — needs its own vector and a CHANGELOG line.
- `conform --verbose` still has no "skipped bridge vector" report; `extensions["variorum:semver"].tag` still holds one tag per record; `SPDX-7`'s comparison is stated, not performed; CycloneDX stays the one planned bridge.
- Domain for the public site, `u-onoma`/`_index` registration: owner decisions, nothing in the repository invents a URL.

## Previous session — 2026-11-26 (Phase 3: the third case study, in `echo-language`)

**Did:** closed Phase 3's case studies. The previous run had written `docs/case-studies/echo-language.md` and left it uncommitted; this session checked every claim in it against the files, corrected two, and shipped it.

- **The case study is real, and every number was re-derived.** Four Suno takes of *Liora* (`Liora-take-01..04.mp3`), SHA-256 and size recomputed from the bytes (3,650,777 / 3,548,907 / 4,286,810 / 4,097,358 B), `ffprobe` durations (158.280 / 152.880 / 186.648 / 178.128 s), the quoted JSON block parses to exactly the committed take-04 record, and the adopter's `check` returns `0` on all four records and `1` on a mismatched take. The C2PA hard binding recomputes for every take (`709d7fe7…` for take 04, over the file minus the 13,659-byte exclusion starting at byte 18,915) while the Variorum digest is `ba774da9…` — `C2P-6` measured, not argued.
- **Two statements corrected.** The sentence about *three takes of one prompt being siblings* is the paragraph under `LIN-6`, not `LIN-6` itself, and the case study now says so. The claim that the prompt block and the `USLT` frame are equal "667 characters both ways" holds for takes 02–04; take 01's frame is 709 characters because the provider repeats the final `[Outro]` section, so the text now says the tag is a transcription that can drift, not a copy of the prompt.
- **Two defects in the adopter's stamper, found by reading its output.** `frame_language_text` returned the USLT content descriptor instead of the text — every UTF-8 frame (Suno writes encoding 3 with an empty descriptor) decoded as `""` — and `reject_derived` exited 1 where the module docstring, the tool README and the adopter's `docs/variorum.md` all promised exit 2. Both fixed in `echo-language` commit `2232272`, with `tests/test_variorum_record.py` (13 tests: four encodings, empty and non-empty descriptors, no terminator, truncated payload, three refusal paths, two end-to-end `check` runs that skip when the audio is absent). That repository's suite went from 78 to 91 tests, all green.
- **One documentation defect across all three case studies.** Each "What a consumer can check" block showed `python3 tools/variorum.py …` with paths relative to the adopter's repository, as if both trees were one directory. The comment now says the reference command runs in a checkout of this repository.
- **On this side:** the case study, its row in `docs/case-studies/README.md`, the PLAN box, CHANGELOG, STATE and this file.

**Verified:** 120 unit tests OK; `conform --coverage` 188/188 PASS (96/133 referenced, 37 exempt, 0 uncovered); seven examples validate; `echo-language` `2232272` pushed and clean; `software-tools` (`e0a739f`) and `3d-printerator` (`faa987c`) unchanged, pushed and clean.

**Left open:**
- Owner review of the whole draft and the transfer to `cazucito`. Unchanged, still the only blocker on a public announcement.
- **Phase 3's case studies are complete; the site is what remains**, and it cannot start without a domain. Owner decision.
- **Three normative questions the case studies produced**, each needing an ADR before 0.2: `REC-12` has no value for a build that fixes every vertex and no byte (from `3d-printerator`); `REC-9` assumes one prompt field where Suno's Custom mode has six (from `echo-language`, which puts the lyric field in `recipe.prompt` and the rest in `parameters`); and the lifecycle vocabulary has no `generated` state — a take that was produced but never judged fits neither `draft` nor `candidate`, and `STA-15` makes silence legal but says nothing about a generator recording its own output.
- Consistency item (open since the C2PA bridge): `C2P-1`, `SWH-1` and `SPDX-1` reject an explicit JSON `null` claim; `SEM-1` treats `null` as absent and returns early. Aligning SEM is a behaviour change to a shipped bridge — needs its own vector and a CHANGELOG line.
- `conform --verbose` still has no "skipped bridge vector" report; `extensions["variorum:semver"].tag` still holds one tag per record; `SPDX-7`'s comparison is stated, not performed; CycloneDX stays a separate planned bridge; `spec/90-extensions/prov.md` is still unwritten.
- Domain for the public site, `u-onoma`/`_index` registration: owner decisions, nothing in the repository invents a URL.

## Previous session — 2026-11-25 (Phase 3: the second case study, in `3d-printerator`)

**Did:** shipped the case study the previous run had written but not committed, then adopted the format in a second real repository — one that builds what it records.

- **First, the previous run's work.** Re-verified (`conform --coverage` 188/188, seven examples, the adopter's record still matching its artifact) and committed as `8dbb6dd`: `docs/case-studies/` (index and `software-tools.md`), `docs/adoption.md` §12, the README pointer and `CaseStudyIndexTests`.
- **`3d-printerator`** (public repository, two designs, parametric OpenSCAD 2021.01, ANYCUBIC Photon Mono 4K) now has `tools/variorum_record.py` (290 lines, stdlib: `stamp` computes the artifact digest and size and the `--source` digest, writing both into `recipe.source` and `lineage.parents`; `check` recomputes all three; a claims file that states a `digest` or an `id` is refused with exit 2), `designs/aw9-d2strap-case/v2/cf3a7707ccdb.variorum.json`, its `.claims.json`, `docs/variorum.md` (Spanish) and a README pointer. Commit `faa987c`, pushed; tree clean, HEAD equals remote.
- **The record** describes the complete v2 two-watch separator (`aw9-d2strap-case-v2-holder.stl`, 374,684 B, `model/stl`) with `core`, `lineage` (`render` of the `.scad`, 28,155 B, `916c01f5…`), `recipe` (build, `openscad 2021.01`, `part=holder`, `export_format=binstl`) and `state` `candidate → rejected`: the design was committed as the version to print, and two days later the owner bought a TPU bumper instead. `at` uses commit timestamps because the project has no decision log; the first transition names `claude-code` and the case study says plainly that the commit carries the owner's git identity — that gap is what `attestation` is for.
- **The measurement that matters:** re-running the declared toolchain reproduces the geometry exactly (same 7,492 triangles, normals, attribute words, header and bounding box) but not the bytes — the facet order varies between consecutive runs, so three files with one geometry have three digests. `determinism: "full"` is therefore forbidden by `REC-13`, `"none"` would misstate the geometry, and the member is absent.
- **Two defects adoption found on this side:** `show` printed `recipe build via ?` for a legal `recipe.tool` array (fixed in 0.6.1 with `ShowTests`, five new tests); `docs/adoption.md` §1 and §9 called `state` a separate conformance class when `CON-3` puts it inside `core` (fixed in both places).
- **On this side:** `docs/case-studies/3d-printerator.md`, the index row, the PLAN box, CHANGELOG and STATE.

**Verified:** 120 unit tests OK; `conform --coverage` 188/188 PASS (96/133 referenced, 37 exempt, 0 uncovered); seven examples validate; the adopter's record validates with `--artifact` and no warnings; its `check` returns `0` on the STL and the `.scad`, and `1` on a different STL and a different `.scad`; both repositories pushed and clean.

**Left open:**
- Owner review of the whole draft and the transfer to `cazucito`. Unchanged, still the only blocker on a public announcement.
- **Third case study.** Open ground: a content project with a generative `recipe` (`determinism: "none"`), or one willing to sign (`attestation`). Not `la-enpenso`, `du-vortoj` or `instruisto` — all three are already in `examples/`.
- **The `determinism` gap is a spec question for the owner.** `REC-12` allows `none`, `seeded`, `full`; a CAD build can determine every vertex and none of the bytes. A fourth value (e.g. `geometry`) would be a normative change — ADR, schema enum, vectors, CHANGELOG — and one measurement is not enough to patch a shipped enum. Decide before 0.2 whether the gap gets a value or a rationale sentence in `REC-12`.
- **`CLAUDE.md` in `3d-printerator` was not updated:** it is an approval-protected agent-instruction file and this run had no approver. `tools/` and the record convention are documented in `docs/variorum.md` and the README; the owner can add one Structure line and one rule if the agent contract should list them.
- The `.scad` has no record of its own. Its digest is verifiable from the repository and `LIN-8` allows an unresolvable parent, but a consumer must not claim the lineage complete (`LIN-9`). Recording the source is that project's decision.
- Consistency item (open since the C2PA bridge): `C2P-1`, `SWH-1` and `SPDX-1` reject an explicit JSON `null` claim; `SEM-1` treats `null` as absent and returns early. Aligning SEM is a behaviour change to a shipped bridge — needs its own vector and a CHANGELOG line.
- `conform --verbose` still has no "skipped bridge vector" report; `extensions["variorum:semver"].tag` still holds one tag per record; `SPDX-7`'s comparison is stated, not performed; CycloneDX stays a separate planned bridge.
- Domain for the public site, `u-onoma`/`_index` registration: owner decisions, nothing in the repository invents a URL.

## Previous session — 2026-11-25 (Phase 3: the first case study, in `software-tools`)

**Did:** adopted Variorum in a second repository — a real one, not another record under `examples/` — and wrote the case study from that side.

- **`software-tools`** (public repo, PHP 8.1 + SQLite archive of 58 fichas, 91 download rows in its exported inventory) now has `ops/tools/variorum_record.py` (218 lines, stdlib; `stamp` writes a record, `check` recomputes digest and size; there is no option that accepts a digest), `ops/records/fc0cadf23dc1.variorum.json`, `docs/variorum.md`, and index lines in `ops/README.md`, `ops/tools/README.md`, `docs/README.md` and `.agents/`. Commit `e0a739f`, pushed; that tree is clean and its HEAD equals its remote.
- **The record describes `Gel86a.zip`** (2,520,484 B, the final GEL 8.6a installer, 2002). The digest was computed from the bytes the site serves: the file was downloaded back from production (general downloads password from BWS, session cookie `st_dl_all`), `unzip -t` reported no errors, and SHA-256 `fc0cadf23dc1…` matched — character for character — the value the admin panel had stored for that row. The record therefore confirms a claim the archive had only asserted.
- **The other ninety artifacts were deliberately left unrecorded.** Their hashes exist only in the panel; copying them would produce records that are numerically right and evidentially empty (ADR-0013's refusal, seen from the producer's side). The adoption plan, written in the adopter's own docs, is to stamp each one when it is re-hashed from the served copy — not before.
- **Four decisions the format left to the adopter**, documented in both repositories: `scheme.version` is `8.6` and not `8.6a` (the archive's ADR-011 splits version from variant, and `SCH-7` says the label is the project's, opaque); `scheme.authority` points at ADR-011 rather than at the site (`SCH-4` would otherwise have turned a marketing URL into a definition); `producer` is the archive, not GExperts (00-overview §4: the actor that created the record, not the vendor of the binary); and `state`, `recipe` and `lineage` are omitted for reasons stated in the case study — an empty-transition `state` would have forced `"draft"` on a file served for years.
- **On this side:** `docs/case-studies/README.md` (the bar every case study must meet), `docs/case-studies/software-tools.md`, `docs/adoption.md` §12 ("When the artifact is not yours"), a README pointer and layout row, `CaseStudyIndexTests` in `tests/test_docs.py` (a case study with no row in the index fails), PLAN split into three case-study boxes, CHANGELOG and STATE.

**Verified:** 115 unit tests OK; `conform --coverage` 188/188 PASS, 96/133 referenced, 37 exempt, 0 uncovered; all seven example records validate. The case study's record validates with `--artifact` against the downloaded file (reference CLI) and the adopter's `check` returns `0` on the real file and `1` on a different one.

**Left open:**
- Owner review of the whole draft and the transfer to `cazucito`. Unchanged, still the only blocker on a public announcement.
- **Case studies two and three.** The archive covered the hard direction — publishing what you did not produce. The next should exercise `recipe` or `state` on artifacts the project *does* produce, in a project that has not adopted the format yet (`la-enpenso` and `du-vortoj` are already in `examples/`, so neither qualifies).
- **Serving the record beside the download in `software-tools`** (`downloads/<slug>/<file>.variorum.json`) needs the streamer and the admin panel to accept a new extension on a production site — an owner decision, recorded in that repository's HANDOFF.
- `spec/90-extensions/prov.md` (W3C PROV) is still planned and unwritten — outside Phase 2's four boxes, still worth doing before 1.0.
- Consistency item (open since the C2PA bridge): `C2P-1`, `SWH-1` and `SPDX-1` reject an explicit JSON `null` claim; `SEM-1` treats `null` as absent and returns early. Aligning SEM is a behaviour change to a shipped bridge — needs its own vector and a CHANGELOG line.
- `conform --verbose` still has no "skipped bridge vector" report; `extensions["variorum:semver"].tag` still holds one tag per record; `SPDX-7`'s comparison is stated, not performed (`check-spdx` is the honest place when adoption asks); CycloneDX stays a separate planned bridge.
- Domain for the public site, `u-onoma`/`_index` registration: owner decisions, nothing in the repository invents a URL.

## Previous session — 2026-11-25 (Phase 3: the adoption guide, and the README's front door)

**Did:** closed Phase 3's first task. `docs/adoption.md` and `examples/instruisto-release-copilot/` had been written the previous run but left uncommitted and unaudited; this session verified them against reality, fixed a real defect in the README, and shipped all three.

- **The guide was re-walked, not re-read.** `gh release download github-copilot-agents/v1.1.0 -R cazucito/instruisto -p '*.pdf'` fetched both assets (73,506 B and 148,743 B; the release API reports the same sizes), and their SHA-256 values — `2605defcf2a7aafb…` and `60d62fe0bbe732bc…` — are exactly the digests the two records carry. `stamp syllabus.pdf --scheme semver 1.1.0 --media-type application/pdf --producer cazucito` reproduces `60d62fe0bbe7.variorum.json` member for member except `created`. The public asset URL still answers `404` with a nine-byte body, so pitfall 2 in the guide is a lived fact, not advice.
- **`docs/adoption.md` tightened in two places.** Only `artifact.digest` is required inside `artifact` (`ID-2`); the table previously implied `size`, `mediaType` and `name` were part of the requirement, and now says which is which. §3 no longer claims `stamp` writes "the five required members and nothing else" — it also fills `artifact`'s descriptive members and writes `producer` when given one; what it never writes is a conformance declaration or an invented section.
- **The README's Quick example was teaching a format the validator rejects.** It showed `lineage.parents` as an array of strings, `state.transitions[].actor` as a string, and truncated digests, so every reader who copied it got an invalid record in the most visible place in the repository. It is now the record shipped in `examples/la-enpenso-shot-01/`, copied verbatim: real digests, a real generative recipe with `determinism: "none"`, a real two-step lifecycle, and an unregistered scheme (`x-la-enpenso-shot`) wrapped untouched. Correction to the previous run's note: `recipe.tool` as an object was *not* a defect — `$defs/tool` allows `{name, model, snapshot}`; two of the three reported shapes were wrong and one was already legal.
- **`tests/test_docs.py` — `ReadmeExampleTests`.** The README must carry exactly one ```json block, and it must equal, member for member, a record under `examples/`. Validity is not re-checked there because `ExamplesTests` validates the same bytes; the new test guards the copy, which is what drifted.
- The field table's first row said `identity`, which is a section title and not a member; it now says `artifact` and the `id` derived from it.
- `examples/README.md` gained the missing `instruisto-release-copilot` row (the directory existed; the index did not list it). CHANGELOG `Unreleased` gained three `Added` entries and one `Changed`; PLAN's Phase 3 first box is checked; STATE marked Phase 3.

**Verified:** 114 unit tests OK; `conform --coverage` 188/188 PASS, 96/133 referenced, 37 exempt, 0 uncovered; all seven example records validate (the `software-tools-inventory` record still emits its pre-existing `REC-5` warning about tool version, which is a warning by `ADR-0005`).

**Left open:**
- Owner review of the whole draft and the transfer to `cazucito`. Unchanged, and still the only blocker on a public announcement.
- Phase 3's remaining work: **three case studies**, then the site, then the announcement. A case study is a project adopting the format in *its own* repository, not another record under `examples/`; `software-tools` is the natural first candidate because `ops/tools/downloads_inventory.py` already hashes release files, so the record can come out of the pipeline instead of from an editor.
- `spec/90-extensions/prov.md` (W3C PROV) is still planned and unwritten — outside Phase 2's four boxes, still worth doing before 1.0.
- Consistency item (open since the C2PA bridge, now three bridges disagree with SemVer): `C2P-1`, `SWH-1` and `SPDX-1` reject an explicit JSON `null` claim; `SEM-1` treats `null` as absent and returns early. The schema types all four claims as objects. Aligning SEM is a behaviour change to a shipped bridge — needs its own vector and a CHANGELOG line.
- `conform --verbose` still has no "skipped bridge vector" report (it never had; the reference runner implements every bridge).
- `extensions["variorum:semver"].tag` still holds one tag per record.
- `SPDX-7`'s comparison is stated, not performed: no tool command takes an SPDX document yet. If adoption asks for it, `variorum check-spdx <record> <document>` would be the honest place, and it must not become a second validator.
- CycloneDX stays a separate bridge (`spec/90-extensions/README.md`, Planned).
- Domain for the public site, `u-onoma`/`_index` registration: owner decisions, nothing in the repository invents a URL.

## Previous session — 2026-11-24 (Phase 2: SPDX bridge, and Phase 2 closed)

**Did:** wrote the fourth bridge and answered its handoff question with arithmetic: **an SPDX checksum can equal the digest, but only one kind of it can, and equality is never a licence to copy.**

- `spec/90-extensions/spdx.md` (`SPDX-1`…`SPDX-8`). The claim is `extensions["variorum:spdx"]` with exactly `version`, `document` and an optional `element`. `version` is a closed list holding `"2.3"` — the `SPDXVersion` without its prefix — because SPDX 3.0 replaced the document model (`spdxId` as an IRI, `namespaceMap`, checksums behind `verifiedUsing`) and a 3.0 document cited under 2.3 rules would be a claim nobody specified. `document` is the `documentNamespace` (§6.5: unique absolute URI, scheme required, no `#`, because SPDX reserves the fragment for element URIs). `element` is an `SPDXRef-[A-Za-z0-9.-]+` identifier (§7.2, §8.2) and is refused when it is `SPDXRef-DOCUMENT`, a well-formed identifier and a category error as a subject. `DocumentRef-x:SPDXRef-y` is refused by shape: the claim names one document and has no member for a second.
- 90.3 is the load-bearing section: five checksums, three subjects. File `SHA256` (the bytes) **can** equal the digest; file `SHA1` cannot; a package checksum can when the package is one blob and the artifact is that blob (Annex K.2.2.3); the package verification code **never** can, because §7.9 hashes the sorted concatenation of the files' SHA-1 *hex strings* — for `hello.txt`, `SHA1("affa1e6d…5215286c") = 41b0f52089ef07…f7d5ae78`, a third value over text; an `ExternalDocumentRef` checksum covers the *document's* bytes. 90.3 also states the self-reference argument SPDX itself makes in Annex K.2.2.1 and pairs it with `CORE-15`.
- `spec/vectors/fixtures/hello.spdx.json` — a real SPDX 2.3.1 document for the existing 111-byte fixture, with `SPDXRef-Package-hello` (`filesAnalyzed: true`, verification code) containing `SPDXRef-File-hello` (`SHA1` + `SHA256`), and the two relationships. Its namespace is the claim's `document` in `spec/vectors/spdx.json`'s base record.
- `spec/vectors/spdx.json` — 18 vectors marked `"bridge": "variorum:spdx"`: claim shape, `null`, version missing and `"3.0.1"`, document missing / schemeless / fragment-bearing, element `DocumentRef-…`, `SPDXRef-`, underscore, `+`, `SPDXRef-DOCUMENT`, a copied `checksum` member, `id` as the namespace and as an element URI, plus four accepts (document-only claim, package element, dots-and-uppercase idstring, unclaimed record). `SPDX-7`/`SPDX-8` exempted with consumer-obligation reasons.
- `docs/adr/ADR-0013-spdx-bridge-points-at-the-sbom.md` — why a copy that would often be *numerically right* is the most dangerous kind.
- Schema: `extensions["variorum:spdx"]` typed (`const` version, namespace pattern, element pattern with a `not` guard); tool 0.6.0 (`validate_spdx_bridge`, `SPDX` family); `SpdxBridgeTests` (10 tests), one of which parses the fixture document, recomputes both checksums and rebuilds the §7.9 code; `spdx` added to the expected groups. README, CHANGELOG, PLAN, extensions README and vectors README updated; STATE rewritten.

**Citations verified against SPDX 2.3.1 before merging,** not recalled: §6.1 (`SPDX-M.N`), §6.3 (`SPDXRef-DOCUMENT`), §6.5 (namespace, no `#`, scheme), §6.6 (`DocumentRef-`, `+` allowed there), §7.2/§8.2 (idstring charset), §7.8/§7.9/§7.10 (verification code, package checksum), §8.4 (file checksum, SHA1 obligatory), Annex K.2.1–K.2.2.3. Two corrections to what was assumed: ISO/IEC 5962:2021 standardises SPDX **2.2.1**, not 2.3, and in 2.3.1 the verification code is §7.9 while the package checksum is §7.10. The published schema pins the element pattern `^SPDXRef-[a-zA-Z0-9.-]+$`, so here — unlike C2PA's hex case — prose and schema agree and strictness is faithful.

**Verified:** 113 unit tests OK; `conform --coverage` 188/188 PASS, 96/133 referenced, 37 exempt, 0 uncovered; five examples validate.

**Left open:**
- Owner review of the whole draft and the transfer to `cazucito`. Unchanged, and still the only blocker on a public announcement.
- **Phase 2 is closed.** Phase 3 begins with `docs/adoption.md`: the core-only path, written by actually recording one real release from a project already in `examples/`. Then the three case studies, then the site (owner decision on the domain).
- SPDX 3.0 is deliberately not covered. A 3.0 bridge is a revision with its own claim shape (`namespaceMap`, `spdxId` as an IRI, `IntegrityMethod`) and its own ADR; `SPDX-2` refuses `"3.0"` until then.
- CycloneDX stays a separate bridge (`spec/90-extensions/README.md`, Planned): its document identity is `serialNumber` and its hash model differs, so folding it into `spdx.md` would blur which document owns which rule.
- Consistency item (still open, three bridges now disagree with SemVer): `C2P-1`, `SWH-1` and `SPDX-1` reject an explicit JSON `null` claim; `SEM-1` treats `null` as absent and returns early. The schema types all four claims as objects. Aligning SEM is a behaviour change to a shipped bridge — needs its own vector and a CHANGELOG line.
- `conform --verbose` still has no "skipped bridge vector" report (it never had; the reference runner implements every bridge).
- `extensions["variorum:semver"].tag` still holds one tag per record.
- `SPDX-7`'s comparison is stated, not performed: no tool command takes an SPDX document yet. If adoption asks for it, a `variorum check-spdx <record> <document>` would be the honest place, and it must not become a second validator.
- Domain for the public site, `u-onoma`/`_index` registration: owner decisions, nothing in the repository invents a URL.

## Previous session — 2026-11-24 (Phase 2: SWHID bridge)

**Did:** closed the SWHID bridge the previous run had left written but uncommitted and red.

- `spec/90-extensions/swhid.md` (`SWH-1`…`SWH-8`): a record claims the bridge with `extensions["variorum:swhid"]`, an object with exactly one member, `swhid`, holding one SWHID of scheme version 1. The identifier is shape-checked only — `swh:1:`, one of the five object types, 40 lowercase hex digits, optional `;name=value` qualifiers from the closed list of §6.2/§6.3. Context qualifiers are held to SWHID's *producer* constraints (§6.1–§6.3: `visit` requires `origin` and names a snapshot, `path` only on `cnt`/`dir` and absolute, `anchor` requires `path` and names a root object, each qualifier at most once, `origin` a URI); fragment qualifiers (`lines`, `bytes`) are refused because a fragment is not an artifact (`ID-9`); identity stays the digest (`SWH-6`).
- The load-bearing answer to the handoff's question — **can a SWHID be the digest?** No, and the document proves it with the same 111 bytes hashed three ways: `a370e4f1…` (SHA-256, the digest), `affa1e6d…` (raw SHA-1, used by nothing), `bad480af…` (SHA-1 over `blob 111\0` + bytes, the `cnt` SWHID; `git hash-object` prints the same digits). Even the friendliest object type hashes a different pre-image; `dir`, `rev`, `rel` and `snp` are not about the artifact's bytes at all, and the tarball/`dir` distinction is written down as the case where the two identifiers earn their keep side by side.
- `spec/vectors/swhid.json` — 32 vectors, each marked `"bridge": "variorum:swhid"`, including accept vectors for the four non-`cnt` object types, a full four-qualifier claim in canonical order, a `%3B` escape that must survive untouched, a path whose case must not be normalised, and the unmarked accept vector proving a record without the claim says nothing about the archive. `SWH-7`/`SWH-8` exempted with reasons (consumer obligations).
- `docs/adr/ADR-0012-swhid-bridge-is-a-sibling-identifier.md` — why a content hash from another model stays a sibling identifier, and why absorbing qualifiers into `producer`/`created`/`lineage` would state things that verify wrong.
- Schema: `extensions["variorum:swhid"]` typed (`additionalProperties: false`, pattern kept byte-for-byte in step with the tool's regex, a `not` guard against fragment qualifiers); the `SWH-4` combination checks are declared as tool-enforced, because JSON Schema cannot express a constraint that depends on another member's value.
- Tool 0.5.0 (`validate_swhid_bridge`, `SWH` rule family); `tests/test_validate.py` gains `SwhidBridgeTests` (15 tests), one of which recomputes the fixture's `cnt` SWHID from `blob 111\0` + bytes and asserts that `spec/vectors/swhid.json`'s base claim is that value — the vector suite cannot recompute a SWHID itself, so a unit test pins it. `tests/test_vectors.py` expects the `swhid` group; README, CHANGELOG, PLAN, extension and vector READMEs updated.

**Verified:** 103 unit tests OK; `conform --coverage` 170/170 PASS, 90/125 referenced, 35 exempt, 0 uncovered; five examples validate.

**Left open:**
- Owner review of the whole draft and the transfer to `cazucito`. Unchanged, and still the only blocker on a public announcement.
- SPDX next. Worth reading before designing: SPDX carries `checksum` values in the same algorithms Variorum uses, so unlike SWHID a checksum *can* equal `artifact.digest`. The decision is what a checksum of a *package* means when the record describes one artifact, and what the bridge should point at (the SBOM document, by `documentNamespace`) rather than copy.
- One SWHID per record. A project that wants both the `rel` and a locally checkable `cnt` of the same release needs two records or a namespaced extension key until a bridge revision adds a multi-object form (ADR-0012).
- Consistency item: `C2P-1` and `SWH-1` reject an explicit JSON `null` under the claim key, because the record wrote the key; the SemVer bridge still treats `null` as absent and returns early. The schema types all three claims as objects, so the tool is now stricter than the SemVer check. Aligning SEM is a behaviour change to a shipped bridge — needs its own vector and a CHANGELOG line, so it was not done here.
- `conform --verbose` still has no "skipped bridge vector" report (it never had; the reference runner implements every bridge).
- `extensions["variorum:semver"].tag` still holds one tag per record.
- Domain for the public site, `u-onoma`/`_index` registration: owner decisions, nothing in the repository invents a URL.

## Previous session — 2026-11-24 (Phase 2: C2PA bridge)

**Did:** closed the C2PA bridge the previous run had left uncommitted and red.

- `spec/90-extensions/c2pa.md` (`C2P-1`…`C2P-8`): a record claims the bridge with `extensions["variorum:c2pa"]`, an object with exactly `manifest` (the `urn:c2pa:` URN of the active manifest), `location` (`embedded`/`external`) and `uri` (required iff external, forbidden otherwise). Nothing is copied out of the manifest. Identity stays the digest (`C2P-6`); the hard binding, ingredients and claim signature are written down as non-mappings (90.3, 90.6, 90.7).
- Verified every C2PA citation against the 2.2 specification before merging. Two statements inherited from the draft were wrong and are fixed: the active manifest is the **last manifest in the store** (§15.5.1), not "the last one whose bindings validate"; and the manifest store is **normally** an excluded range, not a mandated one (§9.1 allows a manifest with no hard binding at all, and exclusions are the mechanism, not a requirement).
- Removed an untestable MUST: `C2P-2` no longer says the URN is "recorded verbatim" as a rule — that is prose in 90.1, because no vector can know what C2PA emitted. What remains normative is the shape: namespace, UUID, and an opaque optional tail.
- The URN shape check accepts both hexadecimal cases and a claim-generator containing colons. C2PA's ABNF allows colons in that component and its HEXDIG is uppercase-only, but real libraries emit lowercase UUIDs (Java's `UUID.toString()`), so the bridge is lenient on input and never re-cases the stored value. Two accept vectors pin this.
- `spec/vectors/c2pa.json` — 19 vectors, marked `"bridge": "variorum:c2pa"`, including the over-strictness guards above and a rejected JSON `null` claim. `C2P-7`/`C2P-8` exempted with reasons (consumer obligations).
- `docs/adr/ADR-0011-c2pa-bridge-references-the-manifest.md` — why the bridge points instead of absorbing signed content into an unsigned sidecar.
- Schema: `extensions["variorum:c2pa"]` typed (`additionalProperties: false`, `location` enum, conditional `uri`); the `manifest` pattern kept byte-for-byte in step with the tool's regex.
- Tool 0.4.0 (`validate_c2pa_bridge`, `C2P` rule family); `tests/test_validate.py` gains `C2paBridgeTests` (9 tests); `tests/test_vectors.py` expects the `c2pa` group; README, CHANGELOG, PLAN, extension and vector READMEs updated.

**Verified:** 88 unit tests OK; `conform --coverage` 138/138 PASS, 84/117 referenced, 33 exempt, 0 uncovered; five examples validate.

**Left open:**
- Owner review of the whole draft and the transfer to `cazucito`. Unchanged, and still the only blocker on a public announcement.
- SWHID next. It is the opposite case to C2PA: a SWHID is itself a content hash with its own object-type prefixes (`swh:1:cnt:…`), so the decision to make is whether it may ever stand in for `artifact.digest` (probably not: different algorithm family, different preimage rules) and what the bridge therefore records.
- Consistency item: `C2P-1` rejects an explicit JSON `null` under the claim key, because the record wrote the key; the SemVer bridge still treats `null` as absent and returns early. The schema types both claims as objects, so the tool is now stricter than the SemVer check. Aligning SEM is a behaviour change to a shipped bridge — needs its own vector and a CHANGELOG line, so it was not done here.
- `conform --verbose` still has no "skipped bridge vector" report (it never had; the reference runner implements every bridge).
- `extensions["variorum:semver"].tag` still holds one tag per record.
- Domain for the public site, `u-onoma`/`_index` registration: owner decisions, nothing in the repository invents a URL.

## Previous session — 2026-11-23 (evening, close-out)

**Did:** made the SemVer bridge durable. The tree had been left uncommitted by the previous run.

- Fixed the citation defect recorded in the previous handoff: the SemVer grammar is normative in the *Backus–Naur Form Grammar for Valid SemVer Versions* appendix, and the regular expression is the pattern published in the SemVer FAQ — not "§9" (item 9 is the pre-release rule). Corrected in `spec/90-extensions/semver.md` and in the comment above `SEMVER_PATTERN`.
- Re-hashed the example artifact from the release itself (`c40d573a…`, 637,290 B): the record is still a digest of the real bytes.
- Fixed five dead relative links (three in `spec/90-extensions/`, two in ADR-0010) and added `tests/test_docs.py`, which fails on any relative markdown link that does not resolve.
- Added a lead paragraph to `CON-28` so the out-of-order number explains itself.

**Verified:** 79 unit tests OK; `conform --coverage` 121/121 PASS, 78/109 referenced, 31 exempt, 0 uncovered; five examples validate.

**Left open (unchanged):** C2PA bridge next; owner review and transfer to `cazucito` are owner decisions.

## Previous session — 2026-11-23 (Phase 2: SemVer bridge)

**Did:** wrote `spec/90-extensions/semver.md` (`SEM-1`…`SEM-7`) and made the whole bridge testable end to end:

- The bridge is an opt-in claim: a record joins it by carrying `extensions["variorum:semver"]`. Rules: the claim is an object (SEM-1), requires `scheme.name = "semver"` (SEM-2) and a SemVer 2.0.0 version string (SEM-3), forbids `scheme.sequence` (SEM-4), constrains the optional `tag` to end with the version's precedence part (SEM-5), leaves ordering to SemVer with no tiebreaker and no identity from version equality (SEM-6), recommends the authority URI (SEM-7).
- `spec/vectors/semver.json` — 18 vectors (7 accept, 11 reject) marked `"bridge": "variorum:semver"`, plus one unmarked accept vector proving an unclaimed `semver` label stays opaque.
- Conformance section: new `CON-28` (`bridge` member on vectors), revised `CON-9` (bridge vectors are opt-in for implementations) and `CON-24` (coverage includes `spec/90-extensions/`).
- ADR-0009 (opt-in claim) and ADR-0010 (bridge rules are conformance rules).
- Reference tool 0.3.0: `validate_semver_bridge` with the official SemVer grammar compiled under `re.ASCII` and applied with `fullmatch`; coverage scans extension bridges.
- Schema types `extensions["variorum:semver"]` as an object with an optional string `tag`.
- `examples/instruisto-guide-owasp/` — a real released artifact (49-page `guide.pdf`, 637,290 B, tag `owasp-api-security/v1.3.1`, digest `c40d573a…` computed from the release asset, not written by hand), with a build recipe whose toolchain and timestamp come from the PDF's own metadata.

**Verified:** unit tests 77/77 OK; `conform --coverage` 121/121 PASS, 78/109 rules referenced, 31 exempt, 0 uncovered; all five example records validate; the grammar reproduces semver.org's own valid/invalid lists.

**Decisions taken (recorded in ADRs, no owner input needed):**
- A bridge is an extension claim, never a conformance class, and binds only records that carry the claim (ADR-0009). This keeps `SCH-7` opacity and invariant 3 intact: no project is forced to strict-label its past releases.
- Bridge rules are part of the coverage contract, and bridge vectors are opt-in for implementations (ADR-0010).

**Left open:**
- Owner review of the whole draft (Phase 0 checkbox) and, after it, the transfer to `cazucito`. Unchanged.
- Extension bridges still to write: C2PA, SWHID, SPDX, PROV. C2PA next; it must not absorb the SemVer bridge's shape blindly — a C2PA manifest is embedded and signed, so "who wins" needs an explicit answer.
- `extensions["variorum:semver"].tag` holds one tag. A project that publishes several equivalent tags for one release (`v1.3.1` and `course/v1.3.1`) can record only one. Deferred until a project needs both; adding an array later would be a compatible extension of the bridge, but it needs an ADR.
- `conform --verbose` does not yet report which vectors were skipped for lack of a bridge claim, because the reference runner implements every bridge. A third-party runner needs that report to satisfy `CON-9` honestly.
- The public site domain and the `u-onoma`/`_index` registration remain owner decisions; nothing in the repository invents a URL.

## Next session should

*(Fulfilled on 2026-11-24: `spec/90-extensions/spdx.md` was written as `SPDX-1`…`SPDX-8`, with 18 vectors, the fixture document and ADR-0013. Phase 2 is closed; the next task is `docs/adoption.md`, in the section at the top of this file.)*

## Previous session — 2026-11-23 (Phase 1: testability)

**Did:** closed Phase 1 (testability) end to end. Wrote `spec/07-conformance.md` (`CON-1`…`CON-27`), the 103-vector suite in `spec/vectors/` with real fixtures and an exemptions list, the `conform` command with `--coverage`, `tests/test_vectors.py`, four ADRs (0005–0008) and the CI workflow (Python 3.11 and 3.13, no packages). Fixed the drift the suite exposed: SHOULD violations are now warnings, not errors; `scheme.name` accepts any lowercase name (SCH-2, new SCH-10 recommendation); the two examples that declared `lineage` without carrying it were corrected.

**Verified:** unit tests 67/67 OK; `conform --coverage` 103/103 PASS, 72/102 rules referenced, 30 exempt with reasons, 0 uncovered; the four real examples validate; `conform` exits 2 on a malformed suite and works from any working directory.

**Left open (now closed):** the SemVer bridge and its place in the conformance contract.

## Previous session — 2026-11-22

**Did:** created the repository, chose the name (`variorum`, validated against u-onoma with live collision checks), fixed the scope (a wrapper standard, not a replacement), wrote the v0.1 draft of the specification, the JSON Schema, the reference CLI and three real examples.

**Left open (closed on 2026-11-23):** conformance suite and test vectors; the extension bridges and the adoption guide remain open.
