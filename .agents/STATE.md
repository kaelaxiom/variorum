# STATE

**Phase:** 3 — Adoption (three of three case studies done; the site waits on a domain)
**Spec version:** 0.1.0-draft (record format `0.1`, vector suite `variorum-vectors/1`)
**Updated:** 2026-11-26

## What exists

- [x] Repository scaffold (AGENTS.md, GOVERNANCE.md, NAME.md, licences)
- [x] `spec/00-overview.md` — scope, principles, conformance classes, terminology
- [x] `spec/01-identity.md` — digest-based identity
- [x] `spec/02-scheme.md` — wrapping existing version schemes
- [x] `spec/03-lineage.md` — derivation graph
- [x] `spec/04-recipe.md` — production recipe, including generative
- [x] `spec/05-state.md` — lifecycle and transitions
- [x] `spec/06-attestation.md` — signatures and binding
- [x] `spec/07-conformance.md` — conformance targets, implementation levels, suite contract, coverage (`CON-1`…`CON-28`)
- [x] `spec/90-extensions/semver.md` — the SemVer 2.0.0 bridge (`SEM-1`…`SEM-7`), opt-in per record
- [x] `spec/90-extensions/c2pa.md` — the C2PA 2.2 bridge (`C2P-1`…`C2P-8`), a pointer to the manifest, opt-in per record
- [x] `spec/90-extensions/swhid.md` — the SWHID 1.2 bridge (`SWH-1`…`SWH-8`), a sibling identifier, opt-in per record
- [x] `spec/90-extensions/spdx.md` — the SPDX 2.3 bridge (`SPDX-1`…`SPDX-8`), a pointer to the bill of materials, opt-in per record
- [x] `spec/vectors/` — 188 vectors in twelve groups, real fixtures, `exemptions.json` with reasons
- [x] `schema/variorum.schema.json` — JSON Schema 2020-12, including the `variorum:semver`, `variorum:c2pa`, `variorum:swhid` and `variorum:spdx` claim shapes
- [x] `tools/variorum.py` — reference CLI 0.6.1 (validator, `conform` runner, four bridge checks, `show` renders tool chains, stdlib only)
- [x] `docs/adoption.md` — the core-only adoption path, performed on `instruisto`'s release `github-copilot-agents/v1.1.0` rather than summarised afterwards; §12 covers adopting an artifact you did not produce
- [x] `docs/case-studies/` — an index with the bar every case study must meet, plus three adopters: `software-tools.md` (an archive that publishes artifacts it did not make, one `core` record for a 2002 installer fetched back from its own live site), `3d-printerator.md` (a CAD repository that builds what it records, one record with `recipe`, `lineage` and a `state` ending in `rejected`) and `echo-language.md` (a content project whose four Suno takes carry generative recipes, a lineage edge to the lyric source and the `c2pa` bridge pointing at the provider's embedded manifest)
- [x] `examples/` — seven real records in five directories (records *this* repository ships; a case study's record lives in the adopter's)
- [x] `tests/` — 120 unit tests (validator + four bridges + vector-suite integrity + relative-link integrity + the README record must be a shipped one + every case study must be listed in its index + `show` must render both `recipe.tool` shapes)
- [x] `.github/workflows/ci.yml` — tests, conformance with coverage, examples on Python 3.11/3.13
- [x] ADRs 0001–0013

## Verified on the last session

- `python3 -m unittest discover -s tests` → 120 tests OK.
- `python3 tools/variorum.py conform --coverage` → 188/188 PASS; 96/133 rules referenced, 37 exempt, 0 uncovered.
- All seven records under `examples/*/*.variorum.json` validate.
- `echo-language`'s four records were re-derived from the audio: SHA-256 and size match for all four takes (3,650,777 / 3,548,907 / 4,286,810 / 4,097,358 B), the JSON block quoted in the case study parses to exactly the committed take-04 record, and the adopter's `check` returns `0` for each record and `1` for a mismatched take, printing both digests.
- The C2PA hard binding recomputes for every take (`709d7fe7…` for take 04, over the file minus the 13,659-byte exclusion that starts at byte 18,915) while the Variorum digest is `ba774da9…`: two SHA-256 values over one file, and neither stands for the other.
- Durations in the case study come from `ffprobe` (158.280 / 152.880 / 186.648 / 178.128 s), not from a tag.
- `echo-language` commit `2232272` (two stamper fixes, 13 tests) is pushed; its tree is clean and its HEAD equals its remote. `software-tools` (`e0a739f`) and `3d-printerator` (`faa987c`) are unchanged, pushed and clean.

## What does not exist yet

- [ ] `spec/90-extensions/prov.md` — W3C PROV (planned in the extensions README, outside the four Phase 2 boxes)
- [ ] Published site (no domain assigned)
- [ ] Registration in `u-onoma` and `_index`
- [ ] Owner review of the draft and decision to transfer to `cazucito`

## Next

See [HANDOFF.md](HANDOFF.md). Phase 3's case studies are complete: three adopters, each covering ground the others could not — an archive publishing what it did not make, a CAD repository that builds what it records, and a content project whose artifacts come out of a model. What remains in Phase 3 is the public site, and nothing in the repository can start it without a domain from the owner. Until then the work that needs no decision is the set of questions the case studies produced: `REC-12`'s missing value for a build that fixes every vertex and no byte, `REC-9`'s assumption of one prompt field where a generator has six, and the absence of a `generated` state or of a transition a generator can make about its own output. Each is a normative change and needs an ADR before 0.2.
