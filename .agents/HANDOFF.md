# HANDOFF

## Last session — 2026-11-23

**Did:** closed Phase 1 (testability) end to end. Wrote `spec/07-conformance.md` (`CON-1`…`CON-27`), the 103-vector suite in `spec/vectors/` with real fixtures and an exemptions list, the `conform` command with `--coverage`, `tests/test_vectors.py`, four ADRs (0005–0008) and the CI workflow (Python 3.11 and 3.13, no packages). Fixed the drift the suite exposed: SHOULD violations are now warnings, not errors; `scheme.name` accepts any lowercase name (SCH-2, new SCH-10 recommendation); the two examples that declared `lineage` without carrying it were corrected.

**Verified:** unit tests 67/67 OK; `conform --coverage` 103/103 PASS, 72/102 rules referenced, 30 exempt with reasons, 0 uncovered; the four real examples validate; `conform` exits 2 on a malformed suite and works from any working directory.

**Decisions taken by the owner (still in force):**
- Name: `variorum`
- Scope: umbrella — wraps existing schemes, never redefines ordering
- Repo: public under `kaelaxiom`, transfer to `cazucito` after the owner approves the draft
- Deliverables for v0.1: spec + schema + CLI + real examples
- Autonomy: cron every 6 hours, direct push to `main`

**Left open:**
- Owner review of the whole draft (Phase 0 checkbox) and, after it, the transfer to `cazucito`.
- Extension bridges (Phase 2): C2PA, SWHID, SPDX, and a worked semver wrapping example.
- A public domain for the specification site — the owner has not chosen one; do not invent a URL in normative text.
- Whether the vector suite should be published as a standalone artifact (`variorum-vectors/1` as a versioned file) once external implementations appear. Not needed for a single implementation; revisit when a second one exists.
- `tests/` has no coverage requirement of its own; if the suite grows past ~150 vectors, split by group directory. Deferred.

## Next session should

1. Start Phase 2 with `spec/90-extensions/semver.md` — the worked wrapping example, since every other bridge cites it.
2. Then C2PA (the closest neighbour): `spec/90-extensions/c2pa.md`, stating coexistence and what each format owns.
3. Each bridge must be purely additive: no new MUST on `core`, no change to the vector suite unless a new rule is defined, and an ADR if any normative rule is added.
4. Re-run `python3 -m unittest discover -s tests` and `python3 tools/variorum.py conform --coverage` before every commit.

## Previous session — 2026-11-22

**Did:** created the repository, chose the name (`variorum`, validated against u-onoma with live collision checks), fixed the scope (a wrapper standard, not a replacement), wrote the v0.1 draft of the specification, the JSON Schema, the reference CLI and three real examples.

**Left open (now closed on 2026-11-23):** conformance suite and test vectors; the extension bridges and the adoption guide remain open.
