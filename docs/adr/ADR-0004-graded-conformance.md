# ADR-0004 — Graded conformance instead of one mandatory shape

**Status:** accepted
**Date:** 2026-11-22

## Context

A format that requires lineage, recipe, state and attestation on every record is unusable. A photographer with a PNG has no lineage and no recipe. A build system has no lifecycle states. Demanding everything produces either fabricated data or non-adoption.

## Decision

Four conformance classes: `core`, `lineage`, `recipe`, `attestation`. A record is described by the highest class it satisfies. `core` requires only `variorum`, `id`, `artifact`, `scheme` and `created`.

Producers SHOULD declare the classes they satisfy in `extensions["variorum:conformance"]`, but a consumer must not infer the absence of data from the absence of a declaration.

## Rationale

Adoption happens one class at a time. `core` alone already solves the problem that motivated the standard — knowing which exact bytes a file is — and it costs one CLI invocation.

Fabrication is the real risk. If the format requires a recipe, people write `"recipe": {"kind": "manual"}` on everything and the field becomes noise. If it requires a state, everything becomes `approved`. Making optional things optional is what keeps the required things trustworthy.

## Consequences

- Consumers must handle partial records. A consumer that requires lineage must check for it rather than assume it.
- Two records can both be conformant and answer different questions. Documentation must state which class a tool supports.
- The conformance suite (planned) must test each class independently, not only the full form.
