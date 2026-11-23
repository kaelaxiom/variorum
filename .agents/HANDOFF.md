# HANDOFF

## Last session — 2026-11-22

**Did:** created the repository, chose the name (`variorum`, validated against u-onoma with live collision checks), fixed the scope (a wrapper standard, not a replacement), wrote the v0.1 draft of the specification, the JSON Schema, the reference CLI and three real examples.

**Decisions taken by the owner:**
- Name: `variorum`
- Scope: umbrella — wraps existing schemes, never redefines ordering
- Repo: public under `kaelaxiom`, transfer to `cazucito` after the owner approves the draft
- Deliverables for v0.1: spec + schema + CLI + real examples
- Autonomy: cron every 6 hours, direct push to `main`

**Left open:**
- Conformance suite and test vectors
- Bridges to C2PA, SWHID, SPDX
- Adoption guide
- Domain for a public site (not decided)

## Next session should

1. Read `.agents/CONTEXT.md` for the design rationale.
2. Write `spec/07-conformance.md` and a machine-readable vector set in `spec/vectors/`.
3. Extend `tools/variorum.py` with a `conform` command that runs the vectors.
4. Only then move to extension bridges — the core must be testable before it grows.
