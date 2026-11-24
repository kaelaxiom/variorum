# ADR-0012 — The SWHID bridge records a sibling identifier, never a digest

**Status:** accepted
**Date:** 2026-11-24

## Context

Phase 2's third bridge. The handoff left an explicit question: **a SWHID is itself a hash of content, so can it stand in for `artifact.digest`?**

A SWHID (Software Heritage identifier, specification 1.2, published as ISO/IEC 18670:2025) names an object in the Software Heritage archive. It has five object types — content (`cnt`), directory (`dir`), revision (`rev`), release (`rel`), snapshot (`snp`) — and its intrinsic identifier is a SHA-1 over a *type-specific serialisation*: for a content, git's blob header (`blob <size>\0`) followed by the bytes (§5.2); for a directory, git's tree serialisation (§5.3); for a revision, git's commit object (§5.4); for a release, git's tag object (§5.5); for a snapshot, Software Heritage's own branch map (§5.6).

Four shapes were on the table:

1. **Promote.** When a SWHID is a `cnt` SWHID, use its hash as the record's identity (or as `artifact.digest` under a second algorithm label).
2. **Absorb.** Parse the qualifiers and spread them across Variorum members — `origin` into `producer`, `visit` into `created`, `rev` parents into `lineage`.
3. **Reference.** Define an opt-in claim that carries one SWHID as a sibling identifier, with an explicit statement of what it does and does not identify.
4. **No bridge.** Say nothing, and let each reader invent a mapping — including the tempting wrong one.

## Decision

- **Reference (3).** A record claims the bridge by carrying `extensions["variorum:swhid"]`, an object with exactly one member, `swhid` (`SWH-1`, `SWH-3`): one SWHID, stored as the archive's identifier, never summarised.
- **A SWHID is never the identity (`SWH-6`).** `artifact.digest` is `sha256:` over the exact bytes (`ID-2`, `ID-3`); a SWHID of scheme version 1 is a SHA-1 over a pre-image with a type header. For a content the two hash *the same bytes* under different algorithms and different pre-image rules — `sha256`, raw SHA-1 and the git blob SHA-1 of the same 111-byte fixture are three different values — so neither identifier is derivable from the other. `id` stays `urn:variorum:sha256:…` derived from the digest (`ID-7`, `ID-8`).
- **Not every SWHID is even about the artifact.** A `dir` SWHID hashes a tree serialisation, not a tarball; a `rev` SWHID hashes a commit with its metadata and message; a `rel` SWHID hashes a tag object; a `snp` SWHID hashes a set of branch targets. Only `cnt` has the artifact's byte sequence as its subject, and even there the pre-image is not the bare bytes.
- **Fragment qualifiers are forbidden (`SWH-5`).** `lines` and `bytes` narrow a SWHID to a subpart of a content (§6.2.1). A record describes one artifact (`ID-9`); a fragment is not an artifact, and a claim that pointed at one would make the record's identity ambiguous. Context qualifiers (`origin`, `visit`, `anchor`, `path`) are allowed and validated against SWHID's own producer constraints (`SWH-4`).
- **One SWHID per record.** The five object types form a chain inside the archive (`rel` → `rev` → `dir` → `cnt`); recording the highest one the archive holds lets the archive walk down. A project that needs a second anchor uses a self-namespaced extension key (`CORE-10`) until a bridge revision adds a multi-object form with its own ADR.
- **Pin `swh:1:` and the specification edition.** Scheme version 1 is the only version defined by SWHID 1.2, and it fixes 40 hexadecimal digits. A future scheme version is a new bridge revision, not something a lenient parser should accept silently.
- **No MUST is added to `core`.** The class model stays at four and the bridge binds only the records that claim it (ADR-0009 applies unchanged).

## Rationale

The load-bearing reason is the same one that governs the C2PA bridge, from the opposite direction: **an identifier a reader cannot recompute from the artifact is a locator, not an identity.** That is exactly what makes a SWHID valuable — it survives re-packaging, re-compression and repository moves because it hashes what the code *is*, not how it was shipped. It is also exactly why it cannot be the digest: the digest must be checkable against the bytes in hand, and a `dir` SWHID is not.

Option (1) fails on arithmetic and on schema. Even in the friendliest case (`cnt`), the pre-image includes `blob <size>\0`, so a record whose `artifact.digest` copied a SWHID would be stating a hash of a header-plus-content byte string as though it were the hash of the content. Option (2) fails on meaning: `origin` records where an object was *observed*, not who produced it; `visit` is a snapshot of refs, not a timestamp; ancestors of a commit are not derivations of the artifact. A mapping that looks plausible and verifies wrong is worse than an admitted gap — the same conclusion ADR-0011 reached for C2PA ingredients.

## Consequences

- `spec/90-extensions/swhid.md` defines `SWH-1`…`SWH-8`; `spec/vectors/swhid.json` holds the vectors, each marked `"bridge": "variorum:swhid"` (`CON-28`). `SWH-7` and `SWH-8` are exemptions with reasons: both bind a consumer that holds the artifact or the archive.
- Reference tool 0.5.0 validates `SWH-1`…`SWH-6`. `schema/variorum.schema.json` types the claim, so a standard JSON Schema validator and the reference CLI agree on the same vectors.
- A reader with the artifact can verify a `cnt` SWHID locally — `git hash-object <file>` prints the same hexadecimal digits — and cannot verify `dir`, `rev`, `rel` or `snp` without the archive. The bridge says so instead of implying a verification it cannot offer.
- A record without the claim is unaffected, even when its artifact is archived: silence is not a denial (`90.10`).
- The bridge does not make a Variorum implementation depend on Software Heritage's API, on git, or on any resolver; it validates a string and stops there.
