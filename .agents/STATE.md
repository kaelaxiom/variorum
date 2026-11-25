# STATE

**Phase:** 3 — Adoption (guide and its worked example are done; three case studies next)
**Spec version:** 0.1.0-draft (record format `0.1`, vector suite `variorum-vectors/1`)
**Updated:** 2026-11-25

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
- [x] `tools/variorum.py` — reference CLI 0.6.0 (validator, `conform` runner, four bridge checks, stdlib only)
- [x] `docs/adoption.md` — the core-only adoption path, performed on `instruisto`'s release `github-copilot-agents/v1.1.0` rather than summarised afterwards
- [x] `examples/` — seven real records in five directories
- [x] `tests/` — 114 unit tests (validator + four bridges + vector-suite integrity + relative-link integrity + the README record must be a shipped one)
- [x] `.github/workflows/ci.yml` — tests, conformance with coverage, examples on Python 3.11/3.13
- [x] ADRs 0001–0013

## Verified on the last session

- `python3 -m unittest discover -s tests` → 114 tests OK.
- `python3 tools/variorum.py conform --coverage` → 188/188 PASS; 96/133 rules referenced, 37 exempt, 0 uncovered.
- All seven records under `examples/*/*.variorum.json` validate.
- The two records of `examples/instruisto-release-copilot/` were re-derived from the release itself, not trusted: `gh release download github-copilot-agents/v1.1.0 -R cazucito/instruisto -p '*.pdf'` returns `proposal.pdf` (73,506 B) and `syllabus.pdf` (148,743 B), whose SHA-256 values are `2605defcf2a7…` and `60d62fe0bbe7…` — the digests both records carry. `stamp` reproduces each record member for member except `created`.
- The guide's warnings were re-checked: the public asset URL answers `404` with a nine-byte `Not Found` body (the repository is private), and `stamp` without `--scheme` writes `{"name": "none"}`.

## What does not exist yet

- [ ] `spec/90-extensions/prov.md` — W3C PROV (planned in the extensions README, outside the four Phase 2 boxes)
- [ ] Three real repositories adopted as case studies — Phase 3's remaining work before the site
- [ ] Published site (no domain assigned)
- [ ] Registration in `u-onoma` and `_index`
- [ ] Owner review of the draft and decision to transfer to `cazucito`

## Next

See [HANDOFF.md](HANDOFF.md). Phase 3's guide is closed. The next task is the first case study: adopt Variorum in a real repository that is *not* one of the four already cited in `examples/` — the guide says what to do, a case study is someone else's project doing it, with the record living in that project's repository and a conformance declaration to match. `software-tools` is the best candidate: its release pipeline already computes inventory hashes, so the record can be produced by the pipeline instead of by hand.
