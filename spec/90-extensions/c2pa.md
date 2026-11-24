# 90 — C2PA bridge

How a Variorum record points at a Content Credentials manifest without copying it, and which of the two documents answers which question.

**Status:** draft, format `0.1`. Purely additive: this bridge defines no rule that a record outside it must satisfy, and adds no MUST to `core` (see [ADR-0011](../../docs/adr/ADR-0011-c2pa-bridge-references-the-manifest.md)).

The vocabulary here follows the C2PA 2.2 specification, *Content Credentials: C2PA Technical Specification* (`https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html`). Terms such as *asset*, *manifest*, *manifest store*, *claim*, *hard binding* and *ingredient* are used with the meaning that document gives them and are not redefined here.

## 90.1 The claim

**C2P-1.** A record claims this bridge by carrying the member `extensions["variorum:c2pa"]`. When present, its value MUST be an object.

**C2P-2.** A record claiming this bridge MUST carry `manifest`: a string identifying the manifest's *active* manifest in C2PA's own `urn:c2pa:` namespace (§8.1). The value MUST be the URN for the active manifest, not a URL, a filename or a manifest store location, and its UUID component MUST have the `8-4-4-4-12` hexadecimal shape. The optional claim-generator and version-reason components are opaque to this bridge: a record carries them as C2PA wrote them, and no rule here parses them.

**C2P-3.** A record claiming this bridge MUST carry `location`, whose value MUST be either `embedded` or `external`.

**C2P-4.** When `location` is `external`, the claim MUST carry `uri`, an absolute URI reference where the C2PA manifest store can be retrieved (served as `application/c2pa`). When `location` is `embedded`, the claim MUST NOT carry `uri`: the manifest travels inside the artifact, and a second location would be a claim that can contradict it.

**C2P-5.** This bridge defines exactly three members. A record claiming it MUST NOT carry other members inside the claim object. A producer that needs to record more about the manifest uses a separate extension key, namespaced to itself (`CORE-10`); copying the manifest's own content into the record is not an option (90.2).

```json
"extensions": {
  "variorum:c2pa": {
    "manifest": "urn:c2pa:F9168C5E-CEB2-4FAA-B6BF-329BF39FA1E4",
    "location": "embedded"
  }
}
```

The claim is a pointer, not a summary. Everything the pointer names is signed together by C2PA; anything copied here would be unsigned prose that drifts from the signed original. A reader who wants the assertions, the actions or the signer goes to the manifest, where C2PA's own validation applies.

The URN is C2PA's label, not Variorum's, so the record keeps it as C2PA emitted it: neither the case of its hexadecimal digits nor its optional components are normalised. In practice both cases occur — Java's `UUID.toString()`, used by C2PA libraries, is lowercase, while the C2PA examples are uppercase — so a reader accepts either and compares the URN as a string.

## 90.2 What C2PA already guarantees

C2PA owns the manifest and this bridge does not restate it. For the purposes of this document the relevant guarantees are:

1. **Storage.** A manifest store is a JUMBF structure, either embedded in the asset (for example an `APP11` segment in JPEG, a `caBX` chunk in PNG, a `uuid` box in ISO BMFF) or stored externally and located by reference or URI, served with the media type `application/c2pa` (§11.4).
2. **Structure.** A manifest store contains one or more manifests; the *active* manifest is the last manifest in the store (§15.5.1). Each manifest combines assertions, a claim and a claim signature (§2.3.4–2.3.7, §10, §11).
3. **Identity.** A manifest is identified by a `urn:c2pa:` URN; a C2PA asset is identified by the URN of its active manifest (§8.1). That identifier is *not* a hash of the asset.
4. **Binding.** A manifest carries at most one assertion defining a hard binding — a cryptographic hash over the asset's bytes minus declared exclusion ranges — and may carry none; it may carry several soft bindings. An embedded manifest cannot hash the bytes it is written into, so the manifest store is normally one of the excluded ranges (§9.1, §9.2, §18.5). Soft bindings (fingerprints, watermarks) match derived renditions and MUST NOT be used as hard bindings (§9.3).
5. **History inside the asset.** Ingredients (`c2pa.ingredient.v3`) record the inputs an asset was produced from, and actions (`c2pa.actions.v2`) record what was done to it, including generative provenance via `digitalSourceType`.
6. **Signing.** The claim is signed (a COSE signature), and validation involves the signer's X.509 chain, C2PA trust lists, timestamps and revocation information (§13–§15).

## 90.3 The digest boundary

A Variorum record identifies bytes (`ID-1`–`ID-3`); a C2PA manifest identifies an asset and binds it to bytes through a hard binding whose excluded ranges normally include the manifest store itself. The two hashes answer different questions, and conflating them produces records that look right and verify wrong.

**When the manifest is embedded**, signing modifies the file. The digest of the signed file, and therefore the record's `id`, differs from the digest of the same image before signing. Both records are correct; they describe different bytes. The C2PA hard binding, meanwhile, hashes the image content with the manifest excluded, so it is not the digest of the file and MUST NOT be recorded as `artifact.digest`.

**When the manifest is external**, the artifact's bytes may be untouched. If the manifest's hard binding covers the whole asset with no exclusions and uses SHA-256, then its value and `artifact.digest` are the same 32 bytes written two ways: C2PA carries them as a CBOR byte string, Variorum as 64 lowercase hexadecimal characters after `sha256:`. This equality is a consequence, not a rule: a producer records the digest of the bytes it has, not the hash it read in a manifest.

The asymmetry is the point. C2PA can say that two different encodings are the same *asset* (soft bindings, ingredient chains, the continuity of a manifest store); Variorum says they are different *artifacts*. Both statements are true, and neither standard should be read as contradicting the other.

## 90.4 Who answers which question

| Question | Authoritative document | Where |
|---|---|---|
| Which bytes is this? | Variorum | `artifact.digest`, `id` (`ID-1`, `ID-7`) |
| What was done to this content, and with what inputs? | C2PA | assertions: `c2pa.actions`, `c2pa.ingredient` |
| Who signed the provenance statement, and is the signature trusted? | C2PA | claim signature, X.509 chain, trust lists (§14–§15) |
| Which artifact does this record describe, and what is its lineage? | Variorum | `lineage` ([03-lineage.md](../03-lineage.md)) |
| How was this artifact produced, step by step, and can it be rebuilt? | Variorum | `recipe` ([04-recipe.md](../04-recipe.md)) |
| Where is it in its lifecycle? | Variorum | `state` ([05-state.md](../05-state.md)) |
| Who claims this record? | Variorum | `attestation` ([06-attestation.md](../06-attestation.md)) |
| Which version is this? | The scheme named in `scheme` | `scheme` ([02-scheme.md](../02-scheme.md)) |

C2PA has no artifact version. The `claim_generator` field names the software that wrote the manifest, not the release of the content; a reader looking for a version label finds it in `scheme` or nowhere.

## 90.5 Identity remains the digest

**C2P-6.** A record claiming this bridge MUST carry `id` in the `urn:variorum:` form derived from `artifact.digest` (`ID-7`, `ID-8`), and MUST NOT use the C2PA URN — or any value derived from it — as `id`.

The temptation is real: C2PA already has a stable identifier that survives re-encoding, and it is tempting to promote it to the record's identity. Doing so would break the property that makes a Variorum record checkable: a reader can recompute a digest from the bytes and compare, but cannot recompute a UUID. The C2PA URN lives in `extensions["variorum:c2pa"].manifest` where it belongs, one pointer away and never a substitute.

## 90.6 Ingredients are not lineage

C2PA ingredients describe what a tool recorded as the inputs of an asset, and they exist to make the provenance chain inside the manifest store verifiable. Variorum `lineage` describes the derivation graph a project declares, including artifacts that never passed through a C2PA-aware tool.

They overlap without being equal: a manifest can list an ingredient Variorum does not know, and a lineage edge can join two artifacts whose manifests never met. Neither graph is a superset, so neither can be derived from the other.

**C2P-7.** A consumer that reads both the record and the manifest MUST report a contradiction between them — for example, an ingredient the manifest presents as a parent of this asset that the record's `lineage` presents as unrelated, or a recorded derivation the manifest's ingredients deny — rather than silently preferring one document. Which document is *more complete* is a judgement about the producer's process; which document is *contradicted* is a fact the consumer can state.

This is an obligation on consumers, so no record can decide it. It is exempted in the vector suite rather than pretended to be testable.

## 90.7 A signature is not an approval

A C2PA signature establishes that a signer signed a claim about an asset, and C2PA validation establishes whether that signature chains to a trust anchor, whether the hard binding still matches, and whether the manifest is intact. None of that is a Variorum attestation, and none of it is a lifecycle state.

**C2P-8.** A consumer MUST NOT treat a valid C2PA signature as an `attestation` under [06-attestation.md](../06-attestation.md), and MUST NOT infer `state.current: approved` from a valid C2PA validation. Conversely, a Variorum signature does not validate a C2PA manifest: the two signatures cover different bytes and rest on different trust models.

The practical consequence: a record can carry both, and a reader should be told which one says what. `state` records a decision by an actor (`STA-6`); a signature records who signed. If nobody approved the artifact, a signed manifest does not fill the gap.

## 90.8 Mapping in both directions

| From | To | Rule |
|---|---|---|
| C2PA manifest URN | `extensions["variorum:c2pa"].manifest` | as C2PA emitted it, shape-checked only (`C2P-2`) |
| Embedded manifest store | `location: "embedded"` | the bytes carry it (`C2P-3`) |
| External manifest store | `location: "external"` + `uri` | the URI is where it is served (`C2P-4`) |
| C2PA hard binding over the whole asset, SHA-256 | `artifact.digest` | same bytes, if and only if no exclusions and the asset is the one hashed (90.3) |
| C2PA hard binding with exclusions | — | does not map: it is not the digest of the file (90.3, `ID-3`) |
| C2PA soft binding | — | does not map: a fingerprint is not an identity (`ID-1`) |
| C2PA ingredient | `lineage.parent` | may be cited, never derived: the graphs overlap, neither contains the other (`C2P-7`) |
| C2PA action | `recipe` | does not map: actions are a log, a recipe is a plan with sources and determinism ([04-recipe.md](../04-recipe.md)) |
| C2PA claim signature | `attestation` | does not map: different document, different covered bytes (`C2P-8`) |
| C2PA validation status | `state` | does not map: trust in a signature is not a lifecycle decision (`C2P-8`) |
| Variorum `scheme.version` | — | does not map: C2PA does not version the artifact (90.4) |

A record never synthesises C2PA fields from its own members. `state.current: published` does not imply that a manifest exists, and `created` is not the manifest's signing time. The direction Variorum → C2PA is empty, and saying so is more useful than inventing a mapping.

## 90.9 Conformance

- Every rule here is exercised by `spec/vectors/c2pa.json`. The vectors that exercise a bridge rule carry `"bridge": "variorum:c2pa"` (`CON-28`), plus one accept vector without the claim, which proves an unclaimed record stays a core record. `C2P-7` and `C2P-8` are exempted with a reason.
- An implementation that claims the C2PA bridge MUST pass those vectors. An implementation that does not claim it skips them and remains conformant at its declared level (`CON-9`).
- No rule here changes what a record with no C2PA claim means. A record for an artifact that happens to carry a manifest, without the claim, says nothing about it: the absence of the claim licenses no conclusion about the manifest's absence.

## 90.10 What this bridge does not do

- It does not validate a manifest, evaluate a trust list, check a certificate chain or verify a signature; that is C2PA's job, with C2PA tooling and C2PA trust anchors.
- It does not parse JUMBF, locate the manifest inside a file, or confirm that `location: "embedded"` is true of the bytes at hand. A reader checks that with the same tooling it uses to read the manifest.
- It does not match soft bindings or recover a manifest from a fingerprint.
- It does not re-sign, re-embed or strip a manifest. Removing a manifest changes the bytes and therefore the digest, which produces a new record at most — never a correction of the old one.
