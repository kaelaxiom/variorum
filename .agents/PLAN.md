# PLAN

## Phase 0 — Definition (current)

- [x] Name, validation and registration path
- [x] Scope decision: umbrella standard
- [x] Specification draft v0.1 (sections 00–06)
- [x] JSON Schema 2020-12
- [x] Reference CLI (stdlib only)
- [x] Three real examples
- [ ] Owner review of the draft

## Phase 1 — Testability

- [x] `spec/07-conformance.md` defining conformance classes and required behaviour
- [x] `spec/vectors/` — machine-readable accept/reject vectors
- [x] `variorum conform` command running the vectors
- [x] CI: run `conform` on every push (GitHub Actions, no dependencies)

## Phase 2 — Interoperability

- [x] `spec/90-extensions/semver.md` — a worked wrapping example with precedence preserved
- [x] `spec/90-extensions/c2pa.md` — how a Variorum record and a C2PA manifest coexist
- [x] `spec/90-extensions/swhid.md` — mapping to SWHID for source code
- [ ] `spec/90-extensions/spdx.md` — SBOM/ML-BOM cross-reference

## Phase 3 — Adoption

- [ ] `docs/adoption.md` — one-page guide, core-only path first
- [ ] Adopt in three real repositories as case studies
- [ ] Public site (domain not yet decided)
- [ ] Announce

## Phase 4 — Standard

- [ ] `1.0.0`
- [ ] `MAINTAINERS.md` and lazy-consensus governance if external implementations appear
