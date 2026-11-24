# STATE

**Phase:** 2 — Interoperability (in progress); Phase 1 complete
**Spec version:** 0.1.0-draft (record format `0.1`, vector suite `variorum-vectors/1`)
**Updated:** 2026-11-23

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
- [x] `spec/vectors/` — 121 vectors in nine groups, real fixtures, `exemptions.json` with reasons
- [x] `schema/variorum.schema.json` — JSON Schema 2020-12, including the `variorum:semver` claim shape
- [x] `tools/variorum.py` — reference CLI 0.3.0 (validator, `conform` runner, SemVer bridge checks, stdlib only)
- [x] `examples/` — five real records in four directories
- [x] `tests/` — 79 unit tests (validator + bridge + vector-suite integrity + relative-link integrity)
- [x] `.github/workflows/ci.yml` — tests, conformance with coverage, examples on Python 3.11/3.13
- [x] ADRs 0001–0010

## Verified on the last session

- `python3 -m unittest discover -s tests` → 79 tests OK.
- `python3 tools/variorum.py conform --coverage` → 121/121 PASS; 78/109 rules referenced, 31 exempt, 0 uncovered.
- All five records under `examples/*/*.variorum.json` validate.
- The SemVer grammar pattern reproduces the official valid/invalid example lists from semver.org exactly, including the ASCII-digit and trailing-newline traps.
- The citation of the SemVer grammar in `semver.md` was corrected: the normative source is the BNF appendix, the regex is the FAQ pattern (not "§9").
- `guide.pdf` was downloaded again from the release and re-hashed: `c40d573a…`, 637,290 B — the example record still matches the real bytes.

## What does not exist yet

- [ ] Extension bridges: C2PA, SWHID, SPDX, PROV (Phase 2)
- [ ] Worked adoption guide (`docs/adoption.md`)
- [ ] Published site (no domain assigned)
- [ ] Registration in `u-onoma` and `_index`
- [ ] Owner review of the draft and decision to transfer to `cazucito`

## Next

See [HANDOFF.md](HANDOFF.md). The next bridge is C2PA, using the SemVer bridge as the template: an extension key that claims it, rules that bind only claimants, bridge-marked vectors.
