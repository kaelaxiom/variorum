# ADR-0009 — The SemVer bridge is an opt-in claim

**Status:** accepted
**Date:** 2026-11-23

## Context

Phase 2 adds bridges between Variorum and neighbouring standards. The first is SemVer, whose value is that a consumer can verify a label's grammar and trust its precedence. The obvious implementation is to apply the SemVer grammar whenever `scheme.name` is `semver`.

That reading collides with two rules the format already made. `SCH-7` says the version string is opaque: a consumer must not parse, normalise or rewrite it. `CORE-11` says an extension must not redefine the semantics of a core member; and invariant 3 (*wrap, don't replace*) says adoption must never force a project to change what it already publishes.

A record written by a project that says `semver` but carries a non-strict label — `1.4` from an old tag, say — is a record the core specification deliberately accepts. If the bridge applied by name, adding the bridge would retroactively invalidate it, and `core` conformance would silently become stricter than section 02 says it is. That is exactly the drift Phase 1 was built to catch.

## Decision

- A record claims the SemVer bridge by carrying `extensions["variorum:semver"]` (`SEM-1`). The bridge's rules bind only records that carry the claim.
- A claim requires `scheme.name = "semver"` (`SEM-2`) and a version matching the SemVer 2.0.0 grammar (`SEM-3`); it forbids `scheme.sequence` (`SEM-4`), constrains the optional tag (`SEM-5`) and recommends the authority (`SEM-7`).
- A record with `scheme.name: "semver"` and no claim remains what it always was: a core-conformant record with an opaque label. A consumer that does not implement the bridge ignores the extension key, as `CORE-3` requires.
- Bridges are **not** conformance classes. The class model stays at four (`core`, `lineage`, `recipe`, `attestation`); a bridge sharpens a claim inside a record, it does not change what the record is.

## Rationale

Graded conformance is the reason this format can be adopted at all. A project must be able to say "identity and scheme, nothing else" and be conformant. If a bridge were implicit in a scheme name, a core project would have to understand SemVer's grammar to be conformant — the opposite of a graded model. If a bridge were a class, the class lattice would grow with every neighbour standard (C2PA, SWHID, SPDX, PROV…), and every consumer would need to know names of specifications it may never touch.

The claim also survives being *ignored*. An unknown extension key is not an error (`CORE-3`), so a bridge-aware producer can add the claim without breaking a consumer written before the bridge existed. That is what makes a bridge addable to a standard that already has implementations.

## Consequences

- `validate` enforces `SEM-1`…`SEM-5` and `SEM-7` only for records that carry the claim (tool 0.3.0).
- A record whose `semver` label is not strict remains valid without the claim; the bridge never fails a record that did not ask for it.
- Bridge vectors are marked with the extension key (`CON-28`) so an implementation that does not claim the bridge is not required to pass them.
- Future bridges follow the same shape: an extension key that names the bridge, rules that bind only claimants, and no new class.
