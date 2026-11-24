# ADR-0011 — The C2PA bridge references the manifest, never copies it

**Status:** accepted
**Date:** 2026-11-24

## Context

Phase 2's second bridge. A C2PA 2.2 manifest answers a question Variorum does not: *who signed what happened to this asset*, with a claim signature, ingredients, actions and a trust model. Variorum answers a different one: *which bytes is this, what is its declared lineage, how was it produced and where is it in its lifecycle*. The two documents routinely meet on the same media file, and a reader needs to know which one to believe about what.

Four shapes were on the table:

1. **Absorb.** Copy the manifest's assertions — actions, ingredients, signer, validation result — into the record, so that one document carries everything.
2. **Apply by presence.** Treat any record whose artifact carries a manifest as being in the bridge, with no claim in the record.
3. **Reference.** Define an opt-in claim whose only content is a pointer to the manifest plus the one fact Variorum needs to read the pointer correctly: where the manifest lives.
4. **No bridge.** Say nothing; let every reader invent the coexistence rules.

## Decision

- **Reference (3).** A record claims the bridge by carrying `extensions["variorum:c2pa"]`, an object with exactly three members (`C2P-1`, `C2P-5`): `manifest`, `location`, and `uri` when and only when the manifest is external (`C2P-3`, `C2P-4`).
- **`manifest` is C2PA's label, not ours.** The value is the `urn:c2pa:` URN of the *active* manifest (C2PA 2.2 §8.1, §15.5.1), and the bridge checks only its shape — namespace, UUID component, opaque optional tail (`C2P-2`). Variorum does not parse C2PA's ABNF, and it never re-cases or normalises the URN. Both hexadecimal cases are accepted because C2PA libraries emit lowercase UUID string representations (Java's `UUID.toString()`) while the specification's examples are uppercase.
- **`location` is mandatory** because the digest means different things in the two storage models (§11.4): embedding a manifest changes the bytes, so the record's digest is of the signed file; an external store can leave the artifact untouched. A single label would hide the distinction that decides what the digest covers.
- **Nothing is copied (`C2P-5`).** No assertions, no actions, no ingredients, no signer, no validation status. A producer that needs to record more about the manifest uses a separate, self-namespaced extension key (`CORE-10`).
- **Identity stays the digest (`C2P-6`).** `id` remains `urn:variorum:sha256:…` derived from `artifact.digest` (`ID-7`, `ID-8`); the C2PA URN is never promoted to identity. It is stable across re-encoding, which is exactly the property that makes it unusable as a Variorum identity: a reader cannot recompute a UUID from the bytes.
- **The C2PA hard binding is not `artifact.digest`.** A hard binding hashes the asset minus declared exclusions (§9.1, §9.2, §18.5); with the manifest excluded it is the digest of no file at all. Equality with `artifact.digest` holds only in the no-exclusion, whole-asset, same-algorithm case, and is a consequence, never a mapping rule. A producer records the digest of the bytes it has, never the hash it read in a manifest.
- **Ingredients are not lineage, and neither graph contains the other** (`C2P-7`). No derivation in either direction; a consumer that reads both and finds a contradiction reports it instead of silently preferring one document.
- **A signature is not an approval** (`C2P-8`). A valid C2PA signature is not a Variorum `attestation`, and C2PA validation does not set `state.current`. The two signatures cover different bytes and rest on different trust models.
- **No MUST is added to `core`.** The class model stays at four and the bridge binds only claimants (ADR-0009 applies unchanged).

## Rationale

The load-bearing reason is that **a signed statement cannot be copied into an unsigned document without losing the property that made it worth having**. A C2PA manifest is verifiable because every assertion in it is covered by the claim signature; a copy in a sidecar is at most a quotation, and a quotation that drifts from the original is worse than no copy, because it looks authoritative. Symmetrically, a Variorum record is verifiable because its identity is a digest the reader can recompute; that property is not transferable to a UUID.

Each document is therefore checkable in its own way, and neither can borrow the other's verification. The only interop that survives is a pointer plus a written-down division of labour — the table in 90.4 — including the cases that do **not** map. Those non-mappings are the important half: a mapping that looks plausible (hard binding → digest) and verifies wrong is more dangerous than an admitted gap.

Options (1) and (2) fail on top of that. Absorption re-specifies a signed format inside an unsigned one and forces Variorum to track C2PA's assertion schemas forever. Applying by presence would make the bridge untestable and unimplementable: the reference validator never opens the artifact's bytes, so it cannot know a manifest exists, and a rule that fires on what is not in the record cannot be a conformance rule ([ADR-0006](ADR-0006-vectors-are-the-conformance-contract.md)).

## Consequences

- `spec/90-extensions/c2pa.md` defines `C2P-1`…`C2P-8`; `spec/vectors/c2pa.json` holds 19 vectors, each marked `"bridge": "variorum:c2pa"` (`CON-28`). `C2P-7` and `C2P-8` are exemptions with reasons: both are obligations on consumers who hold both documents.
- Reference tool 0.4.0 validates `C2P-1`…`C2P-6`. `schema/variorum.schema.json` types the claim (`additionalProperties: false`, `location` enum, conditional `uri`), so a schema validator and the reference CLI agree on the same vectors.
- An explicit JSON `null` under the claim key is a rejected claim (`C2P-1`), not an absent one: the record wrote the key. The schema already types the claim as an object; the tool now agrees with it.
- A record without the claim is unaffected, even when its artifact carries a manifest: silence is not a denial (`90.9`).
- A consumer that wants the manifest's content uses C2PA tooling; Variorum never re-implements validation, trust lists or JUMBF parsing, and this bridge does not make a Variorum implementation depend on any of them.
