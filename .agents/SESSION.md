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

---

# SESSION — 2026-11-23 (second session, Phase 2)

## Objective

Open Phase 2 with the SemVer bridge: the worked wrapping example every other bridge will cite.

## Done

- `spec/90-extensions/semver.md` — `SEM-1`…`SEM-7`. The bridge is claimed by `extensions["variorum:semver"]`; a claimed record must use `scheme.name = "semver"` and a version matching the official SemVer 2.0.0 grammar, must not carry `scheme.sequence`, may carry the release `tag` (which must end with the version's precedence part), and should name the SemVer authority. Ordering stays SemVer's; no tiebreaker, no identity from version equality.
- `spec/vectors/semver.json` — 18 vectors, each marked `"bridge": "variorum:semver"` except the one that proves an unclaimed label stays opaque. Includes the three grammar traps: `v` prefix, leading zero, and a trailing newline that a `$` anchor would let through.
- `spec/07-conformance.md` — `CON-28` defines the vector `bridge` member; `CON-9` makes bridge vectors opt-in for implementations; `CON-24` extends coverage to `spec/90-extensions/`.
- `docs/adr/ADR-0009-semver-bridge-is-opt-in.md`, `docs/adr/ADR-0010-bridge-rules-are-conformance-rules.md`.
- `schema/variorum.schema.json` — the `variorum:semver` claim is typed (object, optional `tag` string).
- `tools/variorum.py` 0.3.0 — `validate_semver_bridge` (official regex under `re.ASCII`, applied with `fullmatch`), `SEM` added to the rule families, coverage scans the extension bridges.
- `examples/instruisto-guide-owasp/` — real release asset `guide.pdf` (637,290 B, tag `owasp-api-security/v1.3.1`, commit `1360025`), digest `c40d573a…` computed from the downloaded asset; recipe tool `typst 0.15.1` and `generatedAt` read from the PDF metadata; no `state` because nobody recorded an approval chain.
- Updated README, CHANGELOG, extension README, vectors README, examples README, PLAN, STATE, HANDOFF, CONTEXT, MEMORY.

## Numbers

- 77 unit tests OK.
- `conform --coverage`: 121/121 PASS; 78/109 rules referenced, 31 exempt, 0 uncovered.
- Five example records validate.

## Decisions

- A bridge binds only the records that claim it; it is not a conformance class (ADR-0009).
- Bridge rules are conformance rules: covered by vectors, marked with `bridge`, opt-in for implementations (ADR-0010).

## Open

- C2PA, SWHID, SPDX, PROV bridges.
- A single `tag` per record; a project publishing two equivalent tags for one release needs a future extension of the bridge.
- `conform --verbose` has no "skipped bridge vector" report yet; the reference runner implements every bridge, so it does not need one.

# SESSION — 2026-11-23 (evening, close-out of the SemVer bridge)

## Objective

Close the SemVer bridge session: the tree had been left uncommitted with one known citation defect, so nothing of the previous work was durable.

## Done

- Corrected the SemVer citation in `spec/90-extensions/semver.md` and `tools/variorum.py`: the normative grammar is the *Backus–Naur Form Grammar for Valid SemVer Versions* appendix; the regular expression is the pattern published in the SemVer FAQ. The earlier "§9" was wrong — item 9 of SemVer is the pre-release rule, not the grammar.
- Re-downloaded `guide.pdf` from the `owasp-api-security/v1.3.1` release and re-hashed it: `c40d573a4bbdfa17cdb6d5619c129868f753a46a82e87a3fa24adeb1fbcc1f6a`, 637,290 B. The example record matches the released bytes; the digest was not taken on trust from the previous session.
- Found and fixed five dead relative links: three in `spec/90-extensions/` (`../docs/adr/` → `../../docs/adr/`) and two in `docs/adr/ADR-0010` (`../spec/` → `../../spec/`).
- Added `tests/test_docs.py`: every relative markdown link must resolve, with fenced and inline code stripped first, plus a guard test that the checker actually finds links. The specification is read as prose; a dead citation is invisible to `validate` and `conform`.
- Gave the out-of-order `CON-28` a lead paragraph in §7.4 explaining why bridge vectors are marked, so the number's placement reads as deliberate rather than accidental.

## Numbers

- 79 unit tests OK.
- `conform --coverage`: 121/121 PASS; 78/109 rules referenced, 31 exempt, 0 uncovered.
- Five example records validate.

## Open

- C2PA bridge (next), then SWHID, SPDX, PROV.
- Owner review and the transfer to `cazucito` remain owner decisions.
