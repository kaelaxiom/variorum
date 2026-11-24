# CONTEXT

## The design in one paragraph

A Variorum record is a JSON sidecar that describes one immutable artifact. It carries six sections — identity, scheme, lineage, recipe, state, attestation — of which only `identity` and `scheme` are required. Everything else is a conformance class a project can adopt when it needs it. The format never defines ordering between versions; it defers to the scheme the project already uses, naming it explicitly.

## Why not extend SemVer?

SemVer's three numbers encode *compatibility deltas against a public API*. Generated content has no API, no consumers, and no monotonic improvement — a second take is a sibling, not an upgrade. Adding fields to SemVer would break every parser in existence while still failing to express lineage or state. A sidecar is additive: it disturbs nothing.

## Why the digest is the identity

Because it is the only claim that is verifiable by the reader without trusting the author. Two parties with the artifact can compute the same identifier and compare. A version number cannot be verified; a digest can. Field `id` is therefore derived: `urn:variorum:sha256:<hex>`.

## Why the record is separate from the artifact

Three reasons:

1. **Feasibility.** Most formats have nowhere to put metadata, and rewriting a 2 GB video to insert a manifest is not a versioning system, it is a re-encode.
2. **Portability.** A sidecar works for a binary, a document, a dataset, a directory tree.
3. **Extensibility.** The record can be superseded, re-signed or re-stated without touching the bytes it describes — which would otherwise change the digest and invalidate the identity.

That last point is the load-bearing one: **metadata cannot live inside the thing whose hash it defines.**

## Architecture of the repository

```
spec/        normative text, numbered sections, stable rule IDs
spec/vectors/ conformance vectors, data not code
spec/90-extensions/  bridges to adjacent standards, opt-in per record
schema/      JSON Schema 2020-12, the machine-readable contract
tools/       reference CLI, zero dependencies, stdlib only
examples/    real records with real digests
docs/adr/    why each normative decision was taken
```

The spec and the schema are two renderings of the same contract. Neither is allowed to drift from the other; a change in one is a change in both.

## Bridges are claims, not classes

A bridge to another standard (SemVer first; C2PA, SWHID, SPDX and PROV planned) never applies because of a scheme name. A record claims the bridge by carrying an extension key — `extensions["variorum:semver"]` — and the bridge's rules bind only that record. The claim is visible data, an unclaiming consumer ignores it as `CORE-3` requires, and the four conformance classes stay four (ADR-0009). Bridge rules are covered by vectors marked with the extension key (ADR-0010).

## Known tensions

- **Digest stability.** `.mp4` files are not byte-stable across re-muxing; the digest identifies *a file*, not *a work*. The lineage graph is what recovers the work-level identity. This is stated in `spec/01-identity.md` and is the reason lineage is not optional in practice, even though it is optional in the format.
- **After the fact.** Adding a record to an artifact that already exists means the record describes an artifact you did not produce under observation. Variorum does not pretend to solve that; `attestation` says who claims what, and the reader decides how much that is worth.
- **Zero dependencies vs. real JSON Schema validation.** The reference CLI validates structurally and semantically with hand-written rules; third-party implementers should use a standard JSON Schema validator against `schema/variorum.schema.json`. Both paths must accept and reject the same vectors — that is what the conformance suite exists for.
