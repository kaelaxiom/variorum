# PLAN

## Phase 0 — Definition

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
- [x] `spec/90-extensions/spdx.md` — SBOM/ML-BOM cross-reference
- [x] `spec/90-extensions/prov.md` — W3C PROV projection bridge, written after Phase 2 closed as the last unwritten bridge (ADR-0014)

## Phase 3 — Adoption (current)

- [x] `docs/adoption.md` — one-page guide, core-only path first
- [ ] Adopt in three real repositories as case studies
  - [x] [`software-tools`](../docs/case-studies/software-tools.md) — an archive that publishes artifacts it did not produce; one artifact, `core`, emitted by the project's own tool
  - [x] [`3d-printerator`](../docs/case-studies/3d-printerator.md) — a CAD repository that builds what it records; one artifact with `recipe`, `lineage` and a `state` that ends in `rejected`
  - [x] [`echo-language`](../docs/case-studies/echo-language.md) — a content project whose artifacts come from a model; four takes with a generative `recipe` (`determinism: "none"`), a `lineage` edge to the lyric source and the `c2pa` bridge pointing at the provider's embedded manifest
- [x] Close the normative questions the case studies produced, each with an ADR before 0.2
  - [x] `REC-12` gains a `content` determinism grade, `REC-22` its normalization ([ADR-0015](../docs/adr/ADR-0015-a-recipe-can-determine-the-content-not-the-bytes.md))
  - [x] `REC-9` states how a multi-field generator maps onto `recipe.prompt` — the member holds one field, `recipe.promptField` names it ([ADR-0016](../docs/adr/ADR-0016-the-prompt-is-one-field-and-the-record-names-it.md))
  - [x] The lifecycle vocabulary answers whether a generated take gets a state of its own — no new state: `draft` and `candidate` are the two premises, and a complete artifact may be born a candidate ([ADR-0017](../docs/adr/ADR-0017-a-complete-artifact-is-born-a-candidate.md))
- [ ] Public site (domain not yet decided)
- [ ] Announce

## Phase 4 — Standard

- [ ] `1.0.0`
- [ ] `MAINTAINERS.md` and lazy-consensus governance if external implementations appear
