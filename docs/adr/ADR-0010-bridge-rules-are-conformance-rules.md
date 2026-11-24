# ADR-0010 — Bridge rules are conformance rules

**Status:** accepted
**Date:** 2026-11-23

## Context

[`spec/90-extensions/README.md`](../../spec/90-extensions/README.md) sets the rule for writing a bridge: add a vector for every rule it defines, because `conform --coverage` fails on a rule that is neither exercised nor exempted (`CON-24`, `CON-25`). When the first bridge was written, two mechanisms made that rule impossible to honour:

1. `CON-24` counted rule identifiers in `spec/00` through `spec/06` only. A rule defined in [`spec/90-extensions/semver.md`](../../spec/90-extensions/semver.md) was invisible to coverage, so a bridge could ship untested while the command reported success.
2. `CON-15` requires every vector's `class` to be one of the four conformance classes. If bridge vectors were ordinary `core` vectors, `CON-9` would oblige every core implementation to pass them — which would make the SemVer bridge mandatory for core conformance, contradicting [ADR-0009](ADR-0009-semver-bridge-is-opt-in.md) and the graded-conformance invariant.

A rule that cannot be covered drifts; a suite that cannot express an optional profile either mandates it or leaves it untested. Neither is acceptable for a standard whose only product is trust in its own checks.

## Decision

- **`CON-24` covers the bridges.** Every rule identifier defined under `spec/90-extensions/` counts, exactly like a rule of sections 00–06. `conform --coverage` and the CI job check it.
- **Vectors carry an optional `bridge` member** (`CON-28`): the extension key the bridge defines, for example `variorum:semver`.
- **Bridge vectors are opt-in for implementations** (`CON-9`): an implementation that claims the bridge must pass them; any other implementation skips them and remains conformant at its declared level.
- The vector suite stays a single suite with a single version. `bridge` is a selector, not a new suite.

## Rationale

The alternative — keeping bridges out of the vector suite and testing them only in `tests/` — was rejected because the suite is the public contract; the reference tool's unit tests are not. A third-party implementation must be able to read the bridge's contract from data, in any language, the same way it reads the core's.

The `bridge` marker is the smallest mechanism that keeps optional profiles testable without weakening `CON-9`. It also gives a runner an honest report: a skipped vector is knowledge about the implementation, not a silent pass.

## Consequences

- Coverage numbers rise by the bridge's rule count; `SEM-6` is the only bridge rule exempted, with a consumer-obligation reason.
- The reference runner loads `bridge`, rejects a value that is not a namespaced extension key as a suite error (`CON-28`), and treats it as metadata otherwise.
- An implementation's conformance report should state which bridges it claims; a suite run without that statement is incomplete, not failing.
- Adding a second bridge later needs no change to the conformance section: define the key, mark the vectors, extend the coverage set.
