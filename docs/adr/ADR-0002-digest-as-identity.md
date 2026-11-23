# ADR-0002 — Identity is the digest

**Status:** accepted
**Date:** 2026-11-22

## Context

Artifacts need an identifier. Candidates: a UUID assigned at creation, a publisher-scoped path, a version label, or the cryptographic hash of the content.

## Decision

The identifier is derived from the content: `urn:variorum:sha256:<hex>`, where `<hex>` is the SHA-256 of the artifact's bytes. `id` and `artifact.digest` must agree, and a validator rejects the record if they do not.

## Rationale

The digest is the only identifier a reader can **verify** without trusting the author. Two parties holding the same file compute the same identifier and can compare. A UUID can be reassigned; a path can be reused; a version label can lie.

Deriving the identifier also means the graph is stable across producers: two independent records describing the same bytes necessarily carry the same `id`, so lineage edges do not break when two teams describe the same artifact.

## Consequences

- **Re-encoding changes identity.** Re-muxing an MP4 produces a different `id` for the same content. This is why `lineage` exists and why `transcode` is a relation: the work survives the byte change through the graph, not through the hash.
- **No identity for mutable things.** A file that changes in place has no stable identity. The format is for immutable artifacts; a changing thing is a sequence of artifacts.
- **SHA-256 only, for now.** One algorithm keeps v0.1 simple. A future MINOR may add an algorithm prefix registry; the `sha256:` prefix already leaves room.
