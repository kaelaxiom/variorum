# STATE

**Phase:** 3 — Adoption (one of three case studies done: `software-tools`)
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
- [x] `docs/adoption.md` — the core-only adoption path, performed on `instruisto`'s release `github-copilot-agents/v1.1.0` rather than summarised afterwards; §12 covers adopting an artifact you did not produce
- [x] `docs/case-studies/` — an index with the bar every case study must meet, and `software-tools.md`: the first real adopter, an archive that publishes artifacts it did not make, with one `core` record for a 2002 installer it fetched back from its own live site
- [x] `examples/` — seven real records in five directories (records *this* repository ships; a case study's record lives in the adopter's)
- [x] `tests/` — 115 unit tests (validator + four bridges + vector-suite integrity + relative-link integrity + the README record must be a shipped one + every case study must be listed in its index)
- [x] `.github/workflows/ci.yml` — tests, conformance with coverage, examples on Python 3.11/3.13
- [x] ADRs 0001–0013

## Verified on the last session

- `python3 -m unittest discover -s tests` → 115 tests OK.
- `python3 tools/variorum.py conform --coverage` → 188/188 PASS; 96/133 rules referenced, 37 exempt, 0 uncovered.
- All seven records under `examples/*/*.variorum.json` validate.
- The case study's record was checked against the adopter's own bytes, not against its database: `Gel86a.zip` was downloaded back from `software-tools.pcabrera.com` through the general downloads password (2,520,484 B, `Content-Length` agreeing), `unzip -t` reported no errors, and its SHA-256 — `fc0cadf23dc1…` — matched the value the archive's panel stored for that row. The reference CLI reports `OK — record conforms to Variorum 0.1 (core)` with `--artifact`; the adopter's `check` returns `0` on the real file and `1` on a different one.
- `software-tools` commit `e0a739f` is pushed; that repository's tree is clean and its HEAD equals its remote.

## What does not exist yet

- [ ] `spec/90-extensions/prov.md` — W3C PROV (planned in the extensions README, outside the four Phase 2 boxes)
- [ ] Two more real repositories adopted as case studies — Phase 3's remaining work before the site
- [ ] Published site (no domain assigned)
- [ ] Registration in `u-onoma` and `_index`
- [ ] Owner review of the draft and decision to transfer to `cazucito`

## Next

See [HANDOFF.md](HANDOFF.md). Phase 3's guide is closed and the first case study is shipped. The next case study should be a project that *builds* what it records — the archive covered the hard direction (publishing artifacts you did not produce), so the second should exercise `recipe` or `state` on artifacts the project produces. `la-enpenso` and `du-vortoj` are already in `examples/`; the case study has to be a project that has not adopted the format yet.
