# STATE

**Phase:** 1 — Testability (complete); Phase 2 next
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
- [x] `spec/07-conformance.md` — conformance targets, implementation levels, suite contract, coverage (`CON-1`…`CON-27`)
- [x] `spec/vectors/` — 103 vectors in eight groups, real fixtures, `exemptions.json` with reasons
- [x] `schema/variorum.schema.json` — JSON Schema 2020-12
- [x] `tools/variorum.py` — reference CLI and `conform` runner (stdlib only)
- [x] `examples/` — three real records
- [x] `tests/` — 67 unit tests (validator + vector-suite integrity)
- [x] `.github/workflows/ci.yml` — tests, conformance with coverage, examples on Python 3.11/3.13
- [x] ADRs 0001–0008

## Verified on the last session

- `python3 -m unittest discover -s tests` → 67 tests OK.
- `python3 tools/variorum.py conform --coverage` → 103/103 PASS; 72/102 rules referenced, 30 exempt, 0 uncovered.
- All four records under `examples/*/*.variorum.json` validate.

## What does not exist yet

- [ ] Extension bridges: C2PA, SWHID, SPDX, semver worked example (Phase 2)
- [ ] Worked adoption guide (`docs/adoption.md`)
- [ ] Published site (no domain assigned)
- [ ] Registration in `u-onoma` and `_index`
- [ ] Owner review of the draft and decision to transfer to `cazucito`

## Next

See [HANDOFF.md](HANDOFF.md). Phase 2 starts with `spec/90-extensions/`, one bridge at a time; no bridge may add a MUST to `core`.
