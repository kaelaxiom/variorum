# SESSION — 2026-11-22

## Objective

Found the repository and produce a v0.1 draft of the Variorum specification.

## Done

- Created `/mnt/thoth/projects/variorum`, git init, local identity configured.
- Name selected (`variorum`) after validating nine candidates against `u-onoma` POLICIES §7 with live collision searches (Firecrawl local + GitHub).
- Owner decisions recorded: umbrella scope, public repo under `kaelaxiom` with later transfer, full v0.1 deliverables, 6-hour autonomous cadence.
- Wrote `NAME.md`, `README.md`, `AGENTS.md`, `GOVERNANCE.md`, `.agents/` protocol.
- Wrote `spec/00`–`06`, `schema/variorum.schema.json`, `tools/variorum.py`, three real examples.

## Decisions

- Identity is the digest (`urn:variorum:sha256:<hex>`); the record is a sidecar, never embedded — metadata cannot live inside the bytes whose hash it defines.
- The standard wraps existing schemes and never redefines ordering.
- Conformance is graded: `core`, `lineage`, `recipe`, `attestation`.

## Open

- Conformance suite and vectors.
- Whether `recipe` should allow free-form `extensions` at the top level or only per section (deferred to ADR-0004).
- A public domain for the specification site has not been decided.

---

# SESSION — 2026-11-23

## Objective

Close Phase 1 (testability): a normative conformance section, a machine-readable vector suite, a runner, and CI.

## Done

- Wrote `spec/07-conformance.md` (`CON-1`…`CON-27`): two targets (record, implementation), four implementation levels, the vector contract, exit codes, and the coverage obligation.
- Built `spec/vectors/`: 103 vectors across `core`, `identity`, `scheme`, `lineage`, `recipe`, `state`, `attestation` and `conformance`, plus fixture-backed digest vectors, `graph` (LIN-7) and `jcs` (ATT-6/7) kinds, and `exemptions.json` with a reason per exempt rule. Fixture digests are recomputed on every run (CON-19).
- Extended `tools/variorum.py` to 0.2.0: `conform` with `--vectors`, `--coverage`, `--verbose`; exit 0/1/2; vector loading, patching, graph and JCS runners; severity split (`Issue.severity`, `Report.errors`/`Report.warnings`).
- Added `tests/test_vectors.py`: suite structure, unique names, fixture freshness, and the stricter rule that the reference tool must cite every rule a reject vector lists.
- Added `.github/workflows/ci.yml`: unit tests, `conform --coverage`, example validation and JSON well-formedness on Python 3.11 and 3.13, with no dependency installation.
- ADR-0005 (SHOULD violations are warnings), ADR-0006 (vectors are the conformance contract), ADR-0007 (declared classes must be backed), ADR-0008 (scheme names are opaque unless reserved).
- Drift fixes the vectors exposed: `scheme.name` accepts any lowercase name (SCH-2) in schema and tool, with `SCH-10` as a SHOULD for the `x-` prefix; extensions may be unprefixed (CORE-10 warning, not error); two examples that declared `lineage` without carrying it now declare only what they contain.

## Numbers

- 67 unit tests OK.
- `conform --coverage`: 103/103 PASS; 72/102 rules referenced, 30 exempt with reasons, 0 uncovered.

## Decisions

- Conformance is defined by data, not by the reference implementation (ADR-0006).
- MUST and SHOULD are different severities in code, not just in prose (ADR-0005).
- A declared conformance class is a promise about presence; declaring too little stays a warning (ADR-0007).
- The reserved scheme table is a vocabulary, never a whitelist (ADR-0008).

## Open

- Phase 2: extension bridges (semver first, then C2PA, SWHID, SPDX).
- Owner review of the draft; transfer to `cazucito` after approval.
- Domain for a public site — owner decision, not an agent decision.
