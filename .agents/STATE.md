# STATE

**Phase:** 3 — Adoption (three of three case studies done; the site waits on a domain)
**Spec version:** 0.1.0-draft (record format `0.1`, vector suite `variorum-vectors/1`)
**Updated:** 2026-11-28

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
- [x] `spec/90-extensions/prov.md` — the W3C PROV bridge (`PROV-1`…`PROV-6`), a member-by-member projection rather than a pointer, opt-in per record
- [x] `spec/vectors/` — 211 vectors in thirteen groups, real fixtures, `exemptions.json` with reasons
- [x] `schema/variorum.schema.json` — JSON Schema 2020-12, including the `variorum:semver`, `variorum:c2pa`, `variorum:swhid`, `variorum:spdx` and `variorum:prov` claim shapes
- [x] `tools/variorum.py` — reference CLI 0.10.0 (validator, `conform` runner, five bridge checks, `show` renders tool chains, `state` knows the two premises, stdlib only)
- [x] `docs/adoption.md` — the core-only adoption path, performed on `instruisto`'s release `github-copilot-agents/v1.1.0` rather than summarised afterwards; §12 covers adopting an artifact you did not produce
- [x] `docs/case-studies/` — an index with the bar every case study must meet, plus three adopters: `software-tools.md` (an archive that publishes artifacts it did not make, one `core` record for a 2002 installer fetched back from its own live site), `3d-printerator.md` (a CAD repository that builds what it records, one record with `recipe`, `lineage` and a `state` ending in `rejected`) and `echo-language.md` (a content project whose four Suno takes carry generative recipes, a lineage edge to the lyric source and the `c2pa` bridge pointing at the provider's embedded manifest)
- [x] `examples/` — seven real records in five directories (records *this* repository ships; a case study's record lives in the adopter's)
- [x] `tests/` — 148 unit tests (validator + five bridges + vector-suite integrity + relative-link integrity + the README record must be a shipped one + every case study must be listed in its index + `show` must render both `recipe.tool` shapes + a path that is not a file gets a sentence, not a traceback + the schema and the tool must agree on every shared vocabulary + the spec's state table must agree with both)
- [x] `.github/workflows/ci.yml` — tests, conformance with coverage, examples on Python 3.11/3.13
- [x] ADRs 0001–0017

## Verified on the last session

- `python3 -m unittest discover -s tests` → 148 tests OK.
- `python3 tools/variorum.py conform --coverage` → 211/211 PASS; 102/142 rules referenced, 40 exempt, 0 uncovered.
- All seven records under `examples/*/*.variorum.json` validate (the `software-tools-inventory` record still emits its known `REC-5` warning about a missing tool version, which is a SHOULD by ADR-0005).
- The lifecycle question is answered: `STA-7` and `STA-9` allow `draft` or `candidate` as the two premises, `candidate → archived` is legal, and `state` is stated not to be a record of provenance (ADR-0017). A `generated` state was refused, not postponed.
- `tests/test_docs.py` now reads §5.2 of the state specification and compares the table with the tool's vocabulary; `tests/test_schema.py` already compared the schema with the tool, so all three renderings cannot drift apart.
- The old clause was spelled into exactly two vectors and one unit test. All three were replaced — and one of them, `test_first_transition_must_start_at_draft`, was already wrong under the old rules: its fixture used a `candidate → candidate` transition that `STA-10` rejects on its own.

## What does not exist yet

- [ ] Published site (no domain assigned)
- [ ] Registration in `u-onoma` and `_index`
- [ ] Owner review of the draft and decision to transfer to `cazucito`

## Next

See [HANDOFF.md](HANDOFF.md). All five bridges are written, Phase 3's case studies are complete, and the three normative questions they produced are closed by ADR-0015, ADR-0016 and ADR-0017. What remains in Phase 3 is the public site, which cannot start without a domain from the owner, and the announcement after the owner's review. No normative question from adoption is open any more; what is left is the small set of documented deferrals — `conform --verbose` has no skipped-bridge report, `extensions["variorum:semver"].tag` holds one tag per record, `SPDX-7`'s comparison is stated rather than performed, and CycloneDX remains the one planned bridge.
