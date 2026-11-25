# ADR-0013 — The SPDX bridge points at the bill of materials and never copies a checksum

**Status:** accepted
**Date:** 2026-11-24

## Context

Phase 2's fourth bridge. The handoff left an explicit question: **SPDX carries checksums in the same algorithms Variorum uses, so unlike SWHID a checksum *can* equal `artifact.digest` — what does a package checksum mean when the record describes one artifact, and what should the bridge point at?**

The arithmetic decides more than the prose. An SPDX 2.3.1 document can carry five distinct kinds of checksum:

| Where | Subject | Can equal the digest |
|---|---|---|
| File checksum, `SHA256` (§8.4) | the file's bytes | yes |
| File checksum, `SHA1` (§8.4) | the same bytes, other algorithm | no |
| Package checksum (§7.10) | the package blob | yes, iff the package is one blob and the artifact is that blob (Annex K.2.2.3) |
| Package verification code (§7.9) | the sorted concatenation of the files' SHA-1 hex strings | never |
| External document reference checksum (§6.6) | the referenced document's bytes | never |

And the document has its own identity model: one namespace per document version, no `#` in it because `#` builds element URIs (§6.5, §7.2), and element identifiers meaningful only inside that document.

Four shapes were on the table:

1. **Copy.** Carry the document's `SHA256` checksum — or the verification code — inside the claim, so a reader has the comparison without fetching the BOM.
2. **Derive.** Treat a package checksum that happens to use SHA-256 as the digest, and build `id` from it.
3. **Reference.** An opt-in claim carrying the document namespace, the edition it is written against, and optionally the element that describes this artifact; the digest stays computed from the bytes, and the equality is a reader's check.
4. **No bridge.** Say nothing, and let a reader assume that an SBOM sitting next to an artifact describes that artifact — the assumption that attaches a BOM to the wrong release.

## Decision

- **Reference (3).** The claim is `extensions["variorum:spdx"]` with exactly three members: `version` (`"2.3"`), `document` (the `documentNamespace`) and an optional `element` (`SPDXRef-…`) (`SPDX-1`…`SPDX-5`).
- **The edition is pinned.** `version` is a closed list holding one value, because SPDX 3.0 replaced the document model (`spdxId` as an IRI, `namespaceMap`, checksums behind `verifiedUsing`). A 3.0 document cited under 2.3 rules would be a claim nobody specified (`SPDX-2`, 90.8).
- **`element` is optional, and `SPDXRef-DOCUMENT` is refused.** Without `element` the claim says only that the artifact is in the document's scope; with it the claim names the package or file that describes the artifact. Naming the document itself is a category error: a document is not one of the things it describes (`SPDX-4`).
- **Identity stays the digest, and never becomes an element URI.** `id` is `urn:variorum:sha256:…` derived from `artifact.digest` (`ID-7`, `ID-8`); the namespace and any `<namespace>#<SPDXID>` are refused as `id` (`SPDX-6`), because an element URI changes when the document is reissued under a new namespace and cannot be recomputed from the bytes at all.
- **The claim carries no checksum.** No copy of a file checksum, a package checksum or a verification code. What SPDX owns, SPDX states; a copy would be a third statement that can go stale on its own (`SPDX-5`, ADR-0011's rule applied to a case where the copy would often be numerically right).
- **The two comparable cases are named, and only they.** A file element's `SHA256` checksum, and a package checksum whose package is a single blob, are hashed over the same bytes with the same algorithm as the digest, so a reader holding both can compare them (`SPDX-7`). The verification code is never comparable: §7.9 hashes the *text* of the files' SHA-1 values, and a set is not a file (`SPDX-8`).
- **The consumer rules are exemptions, not vector bait.** `SPDX-7` and `SPDX-8` bind a reader that holds the artifact, the document and a resolver; no record decides them.
- **No MUST is added to `core`.** The class model stays at four and the bridge binds only the records that claim it (ADR-0009 applies unchanged).

## Rationale

**A copy would be right often enough to be dangerous.** This is the first bridge where copying produces the *correct value* in the common case — a release tarball whose BOM lists it as a package, a PDF listed as a file — so a copied checksum would pass every eyeball test while introducing a statement the record is not entitled to make. The SWHID and C2PA bridges avoided copying because the copy would have been obviously wrong; here it has to be avoided because it would be subtly right.

**"Checksum" is not one subject, and the verification code proves it.** A package verification code is a SHA-1 over the sorted concatenation of the files' SHA-1 hex strings (§7.9). For the 111-byte fixture, the digest is `a370e4f1…`, the file's SHA-1 is `affa1e6d…`, and the code over a package holding only that file is `41b0f520…` — a third value that no algorithm applied to the bytes can produce, because its pre-image is a string of hex digits. Two records carrying equal codes describe packages with the same file hashes; they do not describe the same artifact, and they need not describe the same number of artifacts.

**The BOM's identity is a name, not a hash.** The namespace is unique by construction (§6.5) and may not be resolvable; SPDX says so explicitly. That is the opposite of what `id` must be, which settles why the claim exists at all: the record says "this artifact is that element of that document", and the document says what is inside. Neither absorbs the other.

**A document cannot checksum its own container.** SPDX's own Annex K.2.2.1 says a document inside a package cannot carry the archive's checksum, and prescribes the verification code with the document excluded. Variorum has the mirror constraint in `CORE-15` (a record cannot live inside the artifact whose digest it carries). Two standards independently refusing the same self-reference is a good sign that identity belongs outside the thing identified.

## Consequences

- `spec/90-extensions/spdx.md` defines `SPDX-1`…`SPDX-8`; `spec/vectors/spdx.json` holds the vectors, each marked `"bridge": "variorum:spdx"` (`CON-28`), plus an accept vector without the claim and one with no `element`.
- `spec/vectors/fixtures/hello.spdx.json` is a real SPDX 2.3.1 document for the existing `hello.txt` fixture, with its namespace as the claim's `document`. `tests/test_validate.py` recomputes its file checksums and rebuilds its verification code with the §7.9 algorithm, so neither the document nor the spec's table can drift silently.
- Reference tool 0.6.0 validates `SPDX-1`…`SPDX-6`. `schema/variorum.schema.json` types the claim with the same patterns, so a standard JSON Schema validator and the reference CLI agree on the same vectors.
- A 3.0 bridge is a revision with its own ADR: it needs `namespaceMap`, `spdxId` as an IRI, and `IntegrityMethod`, and none of those fit the 2.3 claim shape.
- CycloneDX is not covered. Its document identity (`serialNumber`) and hash model (`alg` names, `content`) differ enough that folding it into this file would blur which document owns which rule; it gets its own bridge when a project needs it.
- A record without the claim is unaffected, even when its artifact is listed in an SBOM: silence is not a denial (90.9).
- The bridge does not make a Variorum implementation depend on an SPDX parser, a resolver, or the SPDX tools; it validates three strings and stops there.
