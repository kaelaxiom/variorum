# ADR-0001 — The record is a sidecar, never embedded

**Status:** accepted
**Date:** 2026-11-22

## Context

A record describes an artifact's identity, which is the digest of its bytes. C2PA and most photo formats embed metadata inside the file. Embedding is convenient: the record cannot be separated from the artifact.

## Decision

Variorum records live outside the artifact, in a sibling file (`variorum.json` or `<digest-prefix>.variorum.json`).

## Rationale

**Metadata cannot live inside the thing whose hash it defines.** Writing a manifest into a video changes the video's bytes, which changes the digest, which changes the identifier the manifest is supposed to contain. The only ways out of that loop are to compute the digest over a normalised form (which nobody can reproduce reliably) or to exclude the metadata region from the hash (which lets the metadata be swapped without detection).

Both are worse than a sidecar.

Secondary reasons:

1. **Format coverage.** Most formats have nowhere to put metadata. Variorum must work on `.mp4`, `.pdf`, `.parquet`, `.zip` and a directory tree.
2. **Cost.** Rewriting a 2 GB file to insert 2 KB of JSON is not a versioning system.
3. **Supersession.** A record can be re-issued — re-signed, extended, corrected — without touching the artifact.

## Consequences

- Records can be separated from artifacts. Mitigation: `attestation` and the convention of storing the record beside its artifact.
- A record can be lost while the artifact survives. The artifact remains identifiable by recomputing the digest; only the claims are lost.
- Implementations may carry a copy of the record inside an extension for transport, but the authoritative record is the external one.
