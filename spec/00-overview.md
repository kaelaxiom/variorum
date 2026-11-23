# Variorum Specification

**Version:** 0.1.0-draft
**Status:** Draft — not stable, not yet implemented outside this repository
**Editor:** Kael Axiom
**Licence:** CC BY 4.0

---

## Abstract

This document specifies **Variorum**, a record format for identifying, tracing and attesting artifacts. An artifact is any immutable sequence of bytes: a software release, a document, an image, a video, a dataset, a model. A Variorum record is a JSON sidecar that states which exact bytes an artifact consists of, which version scheme its project uses, where it came from, how it was produced, what state it is in, and who vouches for it.

Variorum does not define a new version numbering scheme. It is an envelope that carries the scheme a project already uses.

## 1. Introduction

### 1.1 The problem

Existing version schemes answer a narrow question: *given a dependency, is this update safe?* SemVer encodes compatibility against a public API; CalVer encodes recency; PEP 440 and Debian's version format encode packaging relationships. All of them assume a consumer who parses the number and acts on it.

Most artifacts have no such consumer. A rendered video, a photograph, a dataset, a poster, a build of a document — nobody imports these. Their version label, if they have one, is read by a human who wants to know *which one this is*. A number designed to signal compatibility answers a question nobody asked, and fails to answer the ones that matter:

- Which exact bytes is this?
- What produced it, and with what inputs?
- Where does it sit in the history of the work?
- Is it approved, or is it a candidate?

In practice these questions are answered by filenames — `final_v3_USAR.mp4` — which are neither verifiable nor machine-readable.

### 1.2 The approach

Variorum separates four things that version numbers currently conflate:

| Concern | Carrier | Property |
|---|---|---|
| **Identity** | content digest | verifiable by any reader |
| **Version** | a scheme reference | deferred to the scheme's own rules |
| **History** | a lineage graph | ordered by derivation, not by comparison |
| **Status** | a lifecycle with actors | auditable |

A record may carry all four, or only the first two.

### 1.3 Design principles

**P1 — Identity is the digest.** An artifact is identified by the cryptographic hash of its bytes. Nothing else is an identity.

**P2 — The version is a claim; the record is the evidence.** A version label is metadata asserted by a producer. The record states who asserted it and against which scheme.

**P3 — Wrap, don't replace.** Adopting Variorum MUST NOT require a project to renumber its releases or change its existing scheme. A record is additive.

**P4 — The record is a sidecar.** Metadata MUST NOT be embedded inside the artifact, because embedding changes the bytes and therefore invalidates the identity it would define.

**P5 — Graded conformance.** A project may adopt identity and scheme only. Lineage, recipe and attestation are separate conformance classes.

**P6 — No ordering across schemes.** Variorum never compares a `semver` label to a `calver` label. Ordering is defined by the scheme, and only within it.

## 2. Scope

This specification defines:

- the structure and required fields of a Variorum record;
- how a record references an existing version scheme without altering its semantics;
- how records are linked into a derivation graph;
- how the production of an artifact is described, including generative production;
- a lifecycle for artifacts with recorded transitions;
- an optional attestation mechanism binding a record to its artifact;
- conformance classes and what each one requires.

## 3. Non-goals

- **It is not a versioning scheme.** It does not assign, increment or order version labels.
- **It is not a registry, service or protocol.** No network endpoints, no resolution, no central authority.
- **It is not a storage format.** It does not define where records live or how they are found. Those are implementation concerns.
- **It is not a replacement for C2PA, SWHID, SPDX or W3C PROV.** Section 10 states the relationship to each.
- **It is not a legal attestation framework.** `attestation` establishes cryptographic authorship of a claim, not the truth of the claim.

## 4. Terminology

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY** and **OPTIONAL** are to be interpreted as described in RFC 2119.

- **Artifact** — a finite, immutable sequence of bytes with a declared media type.
- **Work** — the abstract entity of which artifacts are instances. A work is not directly addressable; it is recovered through lineage.
- **Record** — a JSON document conforming to this specification.
- **Producer** — the actor that created the record.
- **Scheme** — a named set of rules that assigns version labels and defines their ordering.
- **Variant** — an artifact sharing a work with another artifact but differing in bytes.
- **Witness** — an artifact that attests to the existence or content of a work at a point in time. Borrowed from textual criticism; the term is informative, not normative.
- **Digest** — `sha256:` followed by 64 lowercase hexadecimal characters.

## 5. Record structure

A record is a JSON object with the following members. Unknown members MUST be ignored by consumers (see `CON-3`).

| Member | Required | Conformance class | Section |
|---|---|---|---|
| `variorum` | yes | core | §6 |
| `id` | yes | core | 01-identity |
| `artifact` | yes | core | 01-identity |
| `scheme` | yes | core | 02-scheme |
| `created` | yes | core | §6 |
| `producer` | no | core | 01-identity |
| `lineage` | no | lineage | 03-lineage |
| `recipe` | no | recipe | 04-recipe |
| `state` | no | core (if present) | 05-state |
| `attestation` | no | attestation | 06-attestation |
| `extensions` | no | core | §7 |

**CORE-1.** A record MUST be a JSON object encoded in UTF-8.

**CORE-2.** The member `variorum` MUST be present and MUST contain the record format version as `<major>.<minor>`.

**CORE-3.** A consumer MUST ignore members it does not recognise, and MUST NOT reject a record solely because it contains unknown members.

**CORE-4.** A producer MUST NOT rely on unknown members being preserved by a consumer.

**CORE-5.** The member `created` MUST be an RFC 3339 timestamp with an explicit UTC offset.

**CORE-6.** All timestamps in a record MUST carry an explicit UTC offset. Local times without offset are invalid.

## 6. Conformance classes

Implementations declare conformance per class. A record is described by the highest class it satisfies. [07-conformance.md](07-conformance.md) makes both statements testable: it defines what each class requires, how a declaration is checked, and the vector suite an implementation must pass.

### 6.1 `core`

Identity and scheme. A record MUST carry a valid digest, a derivable `id`, a scheme reference, and a creation timestamp. This is the minimum a project can adopt, and it is enough to answer *which bytes is this* and *which label does the project give it*.

### 6.2 `lineage`

Adds `lineage`. The record states its parents, the relation to each, and thereby becomes part of a graph. Enables work-level identity: several variants sharing an ancestor.

### 6.3 `recipe`

Adds `recipe`. The record states how the artifact was produced, with enough detail to attempt reproduction — build inputs, or model, prompt, seed and parameters.

### 6.4 `attestation`

Adds `attestation`. The record is signed. Establishes who asserted the record's contents.

### 6.5 Declaring conformance

**CORE-7.** A producer SHOULD declare the classes it satisfies in `extensions["variorum:conformance"]` as an array of class names.

**CORE-8.** A consumer MUST validate the members it understands and MUST NOT infer the absence of a member from the absence of a conformance declaration.

A declaration is a claim, and a claim that can be false is worse than silence. `CON-5` bounds its form to known class names, and `CON-6` requires every declared class other than `core` to be backed by its member — a record declaring `lineage` must carry `lineage`. Under-declaring remains a SHOULD violation.

## 7. Extensions

**CORE-9.** The `extensions` member, when present, MUST be an object whose keys are extension identifiers.

**CORE-10.** Extension identifiers SHOULD be namespaced with a prefix the definer controls, using `:` as separator (for example `c2pa:manifest`, `org.example:custom`).

**CORE-11.** Extensions MUST NOT redefine the semantics of a core member.

## 8. Relationship to existing standards

| Standard | What it does | Variorum's relationship |
|---|---|---|
| **SemVer 2.0.0** | Ordering of compatibility deltas for APIs | Referenced as a scheme (`scheme.name = "semver"`); precedence untouched |
| **CalVer** | Date-based labels | Referenced as a scheme |
| **PEP 440, Debian, RPM, NuGet, Maven** | Ecosystem-specific version ordering | Referenced as schemes; their comparison algorithms remain authoritative |
| **SWHID** | Persistent content identifiers for software source code | Complementary: a SWHID may appear as an identifier inside `extensions`, and `artifact.digest` covers non-source artifacts SWHID does not address |
| **C2PA / Content Credentials** | Signed provenance manifests embedded in media | Complementary: C2PA answers *what was done to these pixels*; Variorum answers *which artifact, in which state, derived from what*. An ADR records the mapping |
| **SPDX / CycloneDX (SBOM, ML-BOM)** | Inventory of components | Complementary: the BOM describes what is inside the artifact; Variorum identifies the artifact and its place in a graph |
| **W3C PROV** | Generic provenance model (entity, activity, agent) | Variorum is a concrete, minimal serialisation of a PROV subset for artifacts; alignment noted in `spec/90-extensions/prov.md` (planned) |
| **SLSA / in-toto** | Supply-chain attestations for builds | Complementary; a SLSA attestation may be carried in `extensions` and referenced by `attestation` |
| **AI Provenance Protocol (APP)** | Provenance for AI-generated content | Adjacent; APP describes generation, Variorum describes identity, lineage and lifecycle across all artifacts, AI or not |

## 9. File conventions

**CORE-12.** A record SHOULD be stored as `variorum.json` in the same directory as the artifact it describes.

**CORE-13.** When several artifacts in one directory carry records, each record SHOULD be named `<digest-prefix>.variorum.json`, where `<digest-prefix>` is the first 12 hexadecimal characters of the artifact digest.

**CORE-14.** The media type `application/variorum+json` is RECOMMENDED. It is not yet registered with IANA.

**CORE-15.** A record MUST NOT be embedded in the artifact it describes.

## 10. Security considerations

- **The digest proves integrity, not authorship.** Anyone can compute `sha256:` of any file. Authorship comes from `attestation`, and even then only establishes who signed.
- **A record can be rewritten while the artifact stays the same.** Records are not part of the artifact. Consumers SHOULD require attestation when the record's claims carry consequences.
- **Signature scope is the record, not the artifact.** Attestation binds a record to a digest. The binding is only as strong as the reader's decision to recompute the digest.
- **Ignoring unknown members is a security-relevant rule.** It permits extensions, and it also permits an attacker to add fields a naive consumer might honour. Consumers MUST NOT act on unrecognised members.

## 11. Acknowledgements

The vocabulary of textual criticism — *stemma*, *recensio*, *variorum*, *witness*, *exemplar* — supplied most of the concepts this specification needed and did not have. Archives solved this problem for manuscripts five centuries before software had the same problem.
