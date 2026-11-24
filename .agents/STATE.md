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
- [x] `spec/90-extensions/swhid.md` — the SWHID 1.2 bridge (`SWH-1`…`SWH-8`), a sibling identifier, opt-in per record
- [x] `spec/vectors/` — 170 vectors in eleven groups, real fixtures, `exemptions.json` with reasons
- [x] `schema/variorum.schema.json` — JSON Schema 2020-12, including the `variorum:semver`, `variorum:c2pa` and `variorum:swhid` claim shapes
- [x] `tools/variorum.py` — reference CLI 0.5.0 (validator, `conform` runner, SemVer, C2PA and SWHID bridge checks, stdlib only)
- [x] `examples/` — five real records in four directories
- [x] `tests/` — 103 unit tests (validator + three bridges + vector-suite integrity + relative-link integrity)
- [x] `.github/workflows/ci.yml` — tests, conformance with coverage, examples on Python 3.11/3.13
- [x] ADRs 0001–0012

## Verified on the last session

- `python3 -m unittest discover -s tests` → 103 tests OK.
- `python3 tools/variorum.py conform --coverage` → 170/170 PASS; 90/125 rules referenced, 35 exempt, 0 uncovered.
- All five records under `examples/*/*.variorum.json` validate.
- The SWHID bridge was written against SWHID 1.2 and its arithmetic was recomputed, not recalled: on the 111-byte `hello.txt` fixture the three hashes are `a370e4f1…` (SHA-256, the digest), `affa1e6d…` (raw SHA-1, used by nothing) and `bad480af…` (SHA-1 over `blob 111\0` + bytes, the `cnt` SWHID — `git hash-object` prints the same digits). No SWHID can be the digest: the pre-images differ.

## What does not exist yet

- [ ] Extension bridges: SPDX, PROV (Phase 2)
- [ ] Worked adoption guide (`docs/adoption.md`)
- [ ] Published site (no domain assigned)
- [ ] Registration in `u-onoma` and `_index`
- [ ] Owner review of the draft and decision to transfer to `cazucito`

## Next

See [HANDOFF.md](HANDOFF.md). The next bridge is SPDX: the question a record has to answer is not "what is inside" (the BOM owns that) but "which artifact does this BOM describe, and can the two disagree without either being wrong?" Answer that before writing rules.
