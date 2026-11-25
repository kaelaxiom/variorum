# 90 — SPDX bridge

How a Variorum record cites the bill of materials that describes an artifact's contents — and why this is the one bridge where a foreign checksum *can* equal the digest, which makes pointing more important here than anywhere else.

**Status:** draft, format `0.1`. Purely additive: this bridge defines no rule that a record outside it must satisfy, and adds no MUST to `core` (see [ADR-0013](../../docs/adr/ADR-0013-spdx-bridge-points-at-the-sbom.md)).

The vocabulary here follows the SPDX specification, version 2.3.1 (`https://spdx.github.io/spdx-spec/v2.3/`). Terms such as *SPDX document*, *document namespace*, *package*, *file*, *SPDX identifier*, *checksum*, *package verification code* and *relationship* are used with the meaning that document gives them and are not redefined here. Its clauses are cited by number: §6 for the document itself, §7 for packages, §8 for files, §11 for relationships, and Annex K for how SPDX itself recommends verifying a package.

Three edition facts belong before the first rule. SPDX 2.3 and 2.3.1 share one document model, and both declare `SPDXVersion: SPDX-2.3` (§6.1). The ISO edition of that line, ISO/IEC 5962:2021, standardises v2.2.1 and does not touch the fields used here. SPDX 3.0 replaced the model — `spdxId` became an IRI, `namespaceMap` replaced the single document namespace, and checksums moved behind `verifiedUsing` — so 3.0 is a different bridge, not a lenient reading of this one (90.8).

## 90.1 The claim

**SPDX-1.** A record claims this bridge by carrying the member `extensions["variorum:spdx"]`. When present, its value MUST be an object.

**SPDX-2.** A record claiming this bridge MUST carry `version`, the value of the document's `SPDXVersion` field (§6.1) without its `SPDX-` prefix. This bridge defines one value, `"2.3"`, and a record MUST NOT claim a version it does not name. 2.3 and 2.3.1 are the same model; 3.0 is not.

**SPDX-3.** A record claiming this bridge MUST carry `document`, the document namespace (§6.5): a non-empty string with no whitespace, an absolute URI with a scheme, and no fragment. The `#` is excluded because SPDX reserves it to build element URIs — `<namespace>#<SPDXID>` (§7.2, §8.2) — so a namespace that already carries one cannot be read unambiguously.

**SPDX-4.** A record claiming this bridge MAY carry `element`, the SPDX identifier of the package or file element that describes this artifact: the literal `SPDXRef-` followed by one or more letters, digits, `.` or `-` (§7.2, §8.2). The value MUST NOT be `SPDXRef-DOCUMENT`, the identifier SPDX reserves for the document itself (§6.3): a document is not one of the things it describes, and a record that wants to point at the document without naming an element omits `element`.

**SPDX-5.** This bridge defines exactly three members: `version`, `document` and `element`. A record claiming it MUST NOT carry other members inside the claim object.

```json
"extensions": {
  "variorum:spdx": {
    "version": "2.3",
    "document": "https://variorum.spec/spdxdocs/variorum-hello-fixture-3f2504e0-4f89-41d3-9a0c-0305e82c3301",
    "element": "SPDXRef-File-hello"
  }
}
```

That claim points at [`spec/vectors/fixtures/hello.spdx.json`](../vectors/fixtures/hello.spdx.json), a real SPDX 2.3.1 document that ships with this repository and describes the 111-byte `hello.txt` fixture, whose digest appears in the vector base records: `sha256:a370e4f1…`. The document's file element carries both a `SHA1` and a `SHA256` checksum of that file; 90.3 takes them apart.

The member set is closed for the reason the C2PA bridge is closed ([ADR-0011](../../docs/adr/ADR-0011-c2pa-bridge-references-the-manifest.md)), and here the reason is sharper. SPDX carries checksums in the same algorithms Variorum uses, so the tempting extra member is a copy of the checksum — and a copy can be numerically right while the record is stale. There is also nothing else worth copying: the document owns the licences, the suppliers, the file list and the relationships, and every one of those is a statement about contents that a record is not qualified to restate.

Two refusals inside `element` deserve their reasons. `SPDXRef-DOCUMENT` is a well-formed identifier and a category error as a subject (SPDX-4). An identifier of the form `DocumentRef-…:SPDXRef-…` — a legal way for an SPDX document to name an element of *another* document (§6.6, §11) — is refused by the shape, because the claim already names one document and the bridge has no member for a second one. The idstring charsets also differ: `DocumentRef-` permits `+`, `SPDXRef-` does not (§6.6, §7.2); the bridge follows the element rule.

Here, unlike the C2PA bridge, there is no grammar-versus-ecosystem split to accommodate. The prose (§7.2, §8.2) and the published SPDX 2.3.1 JSON schema agree on `^SPDXRef-[a-zA-Z0-9.-]+$`, so an underscore or a `+` is not an SPDX element identifier in either rendering, and a record that carries one is not quoting a document faithfully.

## 90.2 What SPDX already guarantees

SPDX owns the document and this bridge does not restate it. For the purposes of this document the relevant guarantees are:

1. **One namespace per document version.** The namespace is a unique absolute URI; a new version of a document needs a new namespace, and a namespace names at most one document (§6.5).
2. **Element identifiers scoped to the document.** Every package, file and snippet carries an `SPDXID` of the form `SPDXRef-[idstring]`, unique within the document, and its URI is the namespace, `#`, and that identifier (§6.3, §7.2, §8.2).
3. **Checksums attached to elements.** A file carries at least one checksum, `SHA1` is obligatory and other algorithms are optional (§8.4); a package may carry any number of checksums (§7.10). Each is an `algorithm` and a lowercase hexadecimal `checksumValue`.
4. **A verification code over a package's contents.** One SHA-1 over the files a package holds, computed from their SHA-1 values (§7.9), forbidden when `filesAnalyzed` is `false` (§7.8, §7.9).
5. **Relationships.** The document describes packages, packages contain files, and every one of those statements is an element-to-element edge (§11). One document may describe many packages, so "the document exists" and "this artifact is that package" are different claims.
6. **External document references.** A document may cite another document by its namespace together with a checksum *of that document* (§6.6).
7. **No version, no lifecycle, no signature.** SPDX 2.3 has `versionInfo` as a free string chosen by the document's creator, no state machine, and no signature over the document. It is a bill of materials, not a versioning system (90.6).

## 90.3 Five checksums, three subjects

An SPDX document can carry five distinct kinds of checksum, and the word "checksum" does not tell them apart. What separates them is the subject — what bytes are hashed — and that is what decides whether any of them can equal `artifact.digest`.

Take the same 111 bytes, [`spec/vectors/fixtures/hello.txt`](../vectors/fixtures/hello.txt), and the fixture document that describes them:

| Where it sits | What it hashes | Value for `hello.txt` | Can it be the digest? |
|---|---|---|---|
| File checksum, `SHA256` (§8.4) | the file's bytes | `a370e4f11b0e59…bef14f7f` | **yes** — same bytes, same algorithm; the digest is that value written as `sha256:…` |
| File checksum, `SHA1` (§8.4) | the same bytes, another algorithm | `affa1e6dfd52ba…5215286c` | no: twenty bytes, and the digest names its algorithm in the value |
| Package checksum (`SHA256`, §7.10) | the package blob — the archive or file the package stands for | the same digits **iff** the package is this file (Annex K.2.2.3) | conditionally: only when the package is one blob and the artifact is that blob |
| Package verification code (§7.9) | the sorted concatenation of the files' SHA-1 **hex strings**, then SHA-1 | `41b0f52089ef07…f7d5ae78` for a package holding only `hello.txt` | never: it hashes text, not bytes, and it describes a set |
| External document reference checksum (§6.6) | the referenced SPDX **document**'s bytes | depends on the BOM, not on the artifact | never: it identifies the document |

The fourth row is the one that is routinely misread. §7.9 does not hash file contents twice; it hashes the *text* of the files' SHA-1 values: sort the forty-character lowercase hex strings, concatenate them without separators, and take the SHA-1 of that ASCII string. For a package holding one file whose SHA-1 is `affa1e6d…5215286c`, the code is `SHA1("affa1e6d…5215286c")` — a value that no algorithm applied to the bytes can produce, because the pre-image is a string of hexadecimal digits. A package holding a thousand files yields one code over a forty-thousand-character string; nothing in it is the hash of a file.

The fifth row carries a self-reference argument worth stating once. A document cannot contain a checksum of the container that contains the document: the archive's bytes include the checksum, and the checksum includes the archive's bytes. SPDX says so itself and gives the escape — a verification code over the package with the SPDX document listed in `packageVerificationCodeExcludedFiles` (Annex K.2.2.1). Variorum has the same shape of problem from the other side: a record cannot live inside the artifact whose digest it carries (`CORE-15`), which is why the record is a sidecar at all.

So the equality that this bridge must not lose is narrow and precise: **an SPDX `SHA256` checksum of a file element, or of a package that is a single blob, is computed over the same bytes with the same algorithm as `artifact.digest`, and the two values coincide.** Two documents can then be compared by anyone holding both, which is exactly the kind of check invariant 1 exists to make possible. Nothing else in the document can coincide with the digest, and the verification code is the clearest example of a hash that looks comparable and is not.

## 90.4 Identity remains the digest

**SPDX-6.** A record claiming this bridge MUST carry `id` in the `urn:variorum:` form derived from `artifact.digest` (`ID-7`, `ID-8`), and MUST NOT use the document namespace — or any element URI built from it, `<namespace>#<SPDXID>` — as `id`.

The temptation is specific here, not generic. An SPDX element URI looks like an identifier for the artifact: it is a URI, it names a thing, and for a file element it is as close to a content address as SPDX gets. But it identifies an element *inside one version of one document*: rewrite the document with a new namespace and the same file has a different URI, and a reader holding the artifact cannot derive the URI from the bytes at all. Identity in this format is the claim a reader verifies against the artifact in hand (`ID-1`), and a namespace is a name, not a hash.

This is also why the claim carries no checksum. A producer that copies the document's `SHA256` checksum into `artifact.digest` gets the right value from the right subject — by luck, and with the wrong habit. A producer that copies the package checksum of a *different* package, or the verification code, gets a value that no reader can reproduce, and the record is false. Computing the digest from the bytes (`ID-3`) is the only path that is right for the right reason.

**What equal values mean.** When the file element's `SHA256` checksum equals the digest, the two documents agree about the same bytes. That agreement is evidence and it is not identity: the BOM is a statement made at a moment, the record is a statement made at a moment, and either can be regenerated while the other stays as it was. A reader who finds them equal has learned that both statements are about the same bytes; a reader who finds them different has learned that at least one of them is about something else — a repackaged archive, a rebuilt tarball, a document for a neighbouring release.

## 90.5 What a reader can check

**SPDX-7.** A consumer that holds the artifact, the document and a claim whose `element` names a file element MUST recompute the artifact's SHA-256 and compare it with that element's `SHA256` checksum, and MUST report a disagreement between the record and the document rather than silently preferring either. When `element` names a package, no such comparison is defined: a package checksum is over the package's blob, which may be an archive that contains the artifact.

**SPDX-8.** A consumer MUST NOT treat a package verification code, or any checksum whose algorithm is not `SHA256`, as `artifact.digest`; MUST NOT conclude from two records carrying equal verification codes that they describe the same artifact; and MUST NOT conclude from a claim without `element` that any particular element describes the artifact — the absence says only that the artifact is in the document's scope.

Both rules bind a reader rather than a record, and both are exempted in [`spec/vectors/exemptions.json`](../vectors/exemptions.json) for that reason. `SPDX-7` needs the artifact, the document and a resolver for both; no record decides it. `SPDX-8` is about conclusions a reader might draw, which no file can contain.

The asymmetry in `SPDX-7` is deliberate and is the bridge's main practical content. An SPDX document has no obligation to hold one checksum per artifact, because its subject is a package and a package may be a directory. So the bridge promises a local check exactly where SPDX promises one: on a file element, and on a package that is a single blob. Everywhere else the honest answer is that verification belongs to the tools that hold the document.

## 90.6 Mapping in both directions

| From | To | Rule |
|---|---|---|
| `documentNamespace` (§6.5) | `extensions["variorum:spdx"].document` | shape-checked only (`SPDX-3`) |
| `SPDXVersion` (`SPDX-2.3`, §6.1) | claim `version` | `2.3` only (`SPDX-2`) |
| Element `SPDXID` (§7.2, §8.2) | claim `element` | shape-checked only (`SPDX-4`) |
| File checksum `SHA256` (§8.4) | `artifact.digest` | may be equal; the digest is computed from the bytes and the equality is a reader's check, never a copy (90.3, `SPDX-7`) |
| File checksum `SHA1` (§8.4) | `artifact.digest` | does not map: another algorithm, and the digest carries its algorithm in the value |
| Package checksum (§7.10) | `artifact.digest` | maps only when the package is one blob and the artifact is that blob (Annex K.2.2.3); not decidable from the record |
| Package verification code (§7.9) | `artifact.digest` | does not map: SHA-1 over a concatenation of hex strings, and a set is not a file (`SPDX-8`) |
| `packageVerificationCodeExcludedFiles` (§7.9) | — | does not map: an exclusion list changes the pre-image, and the record has no member for it |
| External document reference checksum (§6.6) | `artifact.digest` | does not map: it is a checksum of the referenced document |
| Relationship `DESCRIBES` / `CONTAINS` (§11) | `lineage` | does not map: containment between BOM elements is not a derivation between artifacts, and neither end of the edge has a digest |
| Relationship `GENERATED_FROM`, `ANCESTOR_OF`, … (§11) | `lineage.parent` | does not map: the edge joins two elements of one document; a lineage edge joins two records by digest ([03-lineage.md](../03-lineage.md)) |
| `versionInfo` (§7.3) | `scheme.version` | does not map: a free string chosen by the document's creator, not a version under a scheme (`SCH-7`, [02-scheme.md](../02-scheme.md)) |
| `supplier` / `originator` (§7.5, §7.6) | `producer` | does not map: a distribution source is not a producer, and neither field is verified |
| `licenseConcluded`, `copyrightText`, `primaryPackagePurpose` | — | no Variorum member; a BOM states licences and purposes, a record does not |
| Variorum `artifact.digest` | checksum with algorithm `SHA256` (§7.10, §8.4) | the same value; the document owns its own field and the record does not write it |
| Variorum `artifact.size` | — | does not map: SPDX 2.3 has no file-size field |
| Variorum `state`, `attestation` | — | no equivalent: SPDX 2.3 has no lifecycle and no signature ([05-state.md](../05-state.md), [06-attestation.md](../06-attestation.md)) |
| Variorum `recipe` | — | does not map: SPDX 2.3 describes contents, not production ([04-recipe.md](../04-recipe.md)) |

An SPDX document never tells a record what its digest is. A record never tells a document what a package contains. The direction SPDX → Variorum produces one checkable statement — this artifact is the subject of that element — and the direction Variorum → SPDX produces none at all, because the record has no way to say "what is inside".

## 90.7 Who answers which question

| Question | Authoritative document | Where |
|---|---|---|
| Which exact bytes is this? | Variorum | `artifact.digest`, `id` (`ID-1`, `ID-7`) |
| Which document describes it, and which element? | SPDX | `extensions["variorum:spdx"]` (`SPDX-3`, `SPDX-4`) |
| What is inside the package? | SPDX | file elements, relationships, licenses |
| Is the artifact the file this BOM lists? | both, by comparison | `SPDX-7`: file element `SHA256` against the digest |
| Is this package the same contents as that package? | SPDX | compare verification codes, knowing they cover sets (`SPDX-8`) |
| Which version is this? | the scheme named in `scheme` | `scheme` ([02-scheme.md](../02-scheme.md)) |
| What is its lineage, how was it produced, where in its lifecycle? | Variorum | `lineage`, `recipe`, `state` |
| Who asserts all of this? | Variorum | `attestation` ([06-attestation.md](../06-attestation.md)) |

## 90.8 Editions, and why 3.0 is not covered

SPDX 3.0 is a different document model, not a revision of the grammar. Its document element carries `spdxId` as an IRI and `namespaceMap` instead of one document namespace; elements are referenced by IRI rather than by `SPDXRef-` identifiers scoped to a document; checksums and verification codes sit behind `verifiedUsing` and `IntegrityMethod`. A record written against 2.3 semantics and validated by 3.0 shapes would be a claim nobody specified, which is why `version` exists and why it is a closed list (`SPDX-2`). Adding `"3.0"` is a bridge revision with its own claim shape and its own vectors, not an extension of this one.

The 2.3 line has no AI profile; SPDX 3.0 introduced one. That absence does not limit this bridge, because it never asks what an artifact *is*: a model weights file is a file element, or a package that is a single blob, and its `SHA256` checksum is over the same bytes as the digest. An ML-BOM in SPDX 3.0 would need the 3.0 bridge for its own fields, and would still need `SPDX-6` and `SPDX-8` to keep identity and contents apart.

## 90.9 Conformance

- Every rule here is exercised by [`spec/vectors/spdx.json`](../vectors/spdx.json). The vectors that exercise a bridge rule carry `"bridge": "variorum:spdx"` (`CON-28`), plus one accept vector without the claim, which proves an unclaimed record stays a core record. `SPDX-7` and `SPDX-8` are exempted with a reason: both bind a consumer.
- An implementation that claims the SPDX bridge MUST pass those vectors. An implementation that does not claim it skips them and remains conformant at its declared level (`CON-9`).
- No rule here changes what a record with no SPDX claim means. A record for an artifact that happens to be listed in an SBOM, without the claim, says nothing about the SBOM: silence is not a denial, exactly as in the C2PA and SWHID bridges.
- The fixture document is part of the suite's honesty. `tests/test_validate.py` parses [`spec/vectors/fixtures/hello.spdx.json`](../vectors/fixtures/hello.spdx.json), recomputes the file's `SHA1` and `SHA256` from the bytes, rebuilds the package verification code with the §7.9 algorithm, and asserts each against the document and against the digest. A stored checksum that drifts from the fixture fails a test, in the same spirit as `CON-19`.

## 90.10 What this bridge does not do

- It does not look anything up. It does not fetch a document by its namespace, resolve an `SPDXID`, or confirm that the element exists in the document it is attributed to.
- It does not parse an SPDX document, and it does not validate one. A record claims 2.3; whether the document is conformant SPDX is the document's problem and its tools'.
- It does not recompute the document's checksums. It states the consumer's comparison as `SPDX-7` and performs none itself, because the record carries neither the artifact nor the document.
- It does not convert an SPDX checksum into a digest, a version, a supplier or a licence, and it does not accept a snippet, a relationship or a namespace where the record identifies one whole artifact (`ID-9`).
- It does not cover SPDX 3.0, CycloneDX or any other bill-of-materials format. A format with a different document identity needs its own bridge, because the question "which document is this" is answered differently in each.
