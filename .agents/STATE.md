# STATE

**Phase:** 2 complete (SemVer, C2PA, SWHID and SPDX bridges); Phase 3 — Adoption — next
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
- [x] `spec/90-extensions/spdx.md` — the SPDX 2.3 bridge (`SPDX-1`…`SPDX-8`), a pointer to the bill of materials, opt-in per record
- [x] `spec/vectors/` — 188 vectors in twelve groups, real fixtures, `exemptions.json` with reasons
- [x] `schema/variorum.schema.json` — JSON Schema 2020-12, including the `variorum:semver`, `variorum:c2pa`, `variorum:swhid` and `variorum:spdx` claim shapes
- [x] `tools/variorum.py` — reference CLI 0.6.0 (validator, `conform` runner, four bridge checks, stdlib only)
- [x] `examples/` — five real records in four directories
- [x] `tests/` — 113 unit tests (validator + four bridges + vector-suite integrity + relative-link integrity)
- [x] `.github/workflows/ci.yml` — tests, conformance with coverage, examples on Python 3.11/3.13
- [x] ADRs 0001–0013

## Verified on the last session

- `python3 -m unittest discover -s tests` → 113 tests OK.
- `python3 tools/variorum.py conform --coverage` → 188/188 PASS; 96/133 rules referenced, 37 exempt, 0 uncovered.
- All five records under `examples/*/*.variorum.json` validate.
- The SPDX bridge's arithmetic was recomputed, and the document it cites ships with the suite: `spec/vectors/fixtures/hello.spdx.json` describes the 111-byte `hello.txt`. Its file element carries `SHA256 = a370e4f1…bef14f7f` (the digest, same bytes, same algorithm) and `SHA1 = affa1e6d…5215286c`; its package verification code is `41b0f52089ef07…f7d5ae78`, the SHA-1 of the forty-character SHA-1 *text*, which no algorithm applied to the bytes can produce. `SpdxBridgeTests` rebuilds all three.

## What does not exist yet

- [ ] `spec/90-extensions/prov.md` — W3C PROV (planned in the extensions README, outside the four Phase 2 boxes)
- [ ] Worked adoption guide (`docs/adoption.md`) — first task of Phase 3
- [ ] Published site (no domain assigned)
- [ ] Registration in `u-onoma` and `_index`
- [ ] Owner review of the draft and decision to transfer to `cazucito`

## Next

See [HANDOFF.md](HANDOFF.md). Phase 2 is closed. Phase 3 starts with `docs/adoption.md`: a one-page core-only path (`variorum`, `id`, `artifact`, `scheme`, `created`) written by recording a real release from one of the projects already cited in `examples/`, so the guide is the instructions someone followed rather than a summary of the format.
