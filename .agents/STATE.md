# STATE

**Phase:** 2 — Interoperability (in progress); Phase 1 complete
**Spec version:** 0.1.0-draft (record format `0.1`, vector suite `variorum-vectors/1`)
**Updated:** 2026-11-24

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
- [x] `spec/vectors/` — 138 vectors in ten groups, real fixtures, `exemptions.json` with reasons
- [x] `schema/variorum.schema.json` — JSON Schema 2020-12, including the `variorum:semver` and `variorum:c2pa` claim shapes
- [x] `tools/variorum.py` — reference CLI 0.4.0 (validator, `conform` runner, SemVer and C2PA bridge checks, stdlib only)
- [x] `examples/` — five real records in four directories
- [x] `tests/` — 88 unit tests (validator + both bridges + vector-suite integrity + relative-link integrity)
- [x] `.github/workflows/ci.yml` — tests, conformance with coverage, examples on Python 3.11/3.13
- [x] ADRs 0001–0011

## Verified on the last session

- `python3 -m unittest discover -s tests` → 88 tests OK.
- `python3 tools/variorum.py conform --coverage` → 138/138 PASS; 84/117 rules referenced, 33 exempt, 0 uncovered.
- All five records under `examples/*/*.variorum.json` validate.
- The C2PA bridge was written against the C2PA 2.2 specification and the citations were checked there, not recalled: the active manifest is the last manifest in the store (§15.5.1), the manifest store is *normally* an excluded range rather than a mandated one (§9.1, §9.2), and external stores are served as `application/c2pa` (§11.4).

## What does not exist yet

- [ ] Extension bridges: SWHID, SPDX, PROV (Phase 2)
- [ ] Worked adoption guide (`docs/adoption.md`)
- [ ] Published site (no domain assigned)
- [ ] Registration in `u-onoma` and `_index`
- [ ] Owner review of the draft and decision to transfer to `cazucito`

## Next

See [HANDOFF.md](HANDOFF.md). The next bridge is SWHID: unlike C2PA, a SWHID *is* a content hash, so the interesting question is whether a SWHID can be a Variorum digest or only a sibling identifier — answer that before writing rules.
