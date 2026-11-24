# 90 — SWHID bridge

How a Variorum record cites the Software Heritage identifier of a source object without promoting that identifier to the artifact's identity.

**Status:** draft, format `0.1`. Purely additive: this bridge defines no rule that a record outside it must satisfy, and adds no MUST to `core` (see [ADR-0012](../../docs/adr/ADR-0012-swhid-bridge-is-a-sibling-identifier.md)).

The vocabulary here follows the SWHID specification, version 1.2 (`https://www.swhid.org/swhid-specification/v1.2/`), published as ISO/IEC 18670:2025. Terms such as *core identifier*, *qualifier*, *content*, *directory*, *revision*, *release* and *snapshot* are used with the meaning that document gives them and are not redefined here. Its normative chapters are cited by number: §4 for the grammar and §5–§6 for the semantics and the qualifiers.

Two version numbers meet in this document and must not be confused. The *specification* has editions (1.2 at the time of writing); the *identifier* carries a scheme version, which is `1` and appears literally in every SWHID (`swh:1:…`). This bridge is written against scheme version 1 and specification edition 1.2.

## 90.1 The claim

**SWH-1.** A record claims this bridge by carrying the member `extensions["variorum:swhid"]`. When present, its value MUST be an object.

**SWH-2.** A record claiming this bridge MUST carry `swhid`, a string holding exactly one SWHID of scheme version 1: the literal `swh:1:`, an object type, a colon, 40 lowercase hexadecimal digits (§4, §5.1), and optionally a list of qualifiers. The value MUST contain no whitespace. Each qualifier MUST have the form `name=value`, with `name` one of `origin`, `visit`, `anchor`, `path`, `lines` or `bytes` and `value` non-empty; a qualifier whose name is not in that list is not part of any SWHID.

```json
"extensions": {
  "variorum:swhid": {
    "swhid": "swh:1:cnt:bad480af921edbabd43ecf18df4362aa3c3ae871"
  }
}
```

That value is the SWHID of [`spec/vectors/fixtures/hello.txt`](../vectors/fixtures/hello.txt), the 111-byte fixture whose digest appears in the vector base records: `sha256:a370e4f1…`. It was not written by hand — `git hash-object` on the same file prints the same hexadecimal digits, because for a content the SWHID is git's blob hash (§5.2, §5.8). Section 90.3 takes the three hashes of that one file apart.

The qualifier list is parsed by splitting on `;`. That is safe by construction: §4 requires `;` and `%` inside a qualifier value to be percent-encoded (`%3B`, `%25`), so a raw `;` always separates qualifiers and never occurs inside one. This bridge does not decode percent-escapes, does not normalise case, and does not reorder qualifiers: the SWHID is stored as the archive emitted it, and a comparison of two SWHIDs is done under SWHID's own rules (§6.4).

The object type is matched strictly, including lowercase hexadecimal digits. SWHID's grammar admits only `a`–`f` (§4), and the reference implementation (`swh.model`) emits lowercase, so here grammar and ecosystem agree — unlike the C2PA bridge, which has to accept both hexadecimal cases because C2PA's grammar and C2PA's libraries disagree. A lenient parser MAY accept an uppercase identifier it reads elsewhere and compare it after lowercasing (§6.4 compares core identifiers as values); a *record* that carries uppercase digits does not conform to this bridge.

**SWH-3.** This bridge defines exactly one member, `swhid`. A record claiming it MUST NOT carry other members inside the claim object. A producer that needs to record more about the archive — a resolver URL, a collection name, the date of a save request — uses a separate extension key, namespaced to itself (`CORE-10`).

The claim is a citation, not a copy. Everything derivable from the SWHID (the object type, the qualifiers, the resolver URL Software Heritage serves at `https://archive.softwareheritage.org/<swhid>/`) is left derivable; duplicating it in the record creates two statements that can disagree.

## 90.2 What SWHID already guarantees

SWHID owns the identifier and this bridge does not restate it. For the purposes of this document the relevant guarantees are:

1. **One object per identifier.** A SWHID names exactly one object in the archive, and its type is part of the identifier: `cnt`, `dir`, `rev`, `rel`, `snp` (§5.1).
2. **An intrinsic hash.** The fourth field is a SHA-1 over a type-specific serialisation of the object and its metadata (§5.1–§5.6). It is intrinsic: it does not depend on where the object is stored, which repository it came from, or when it was archived.
3. **A Merkle structure.** The objects refer to each other by these hashes — a revision to its root directory and parents, a directory to its entries' hashes, a snapshot to its branches' targets — so the archive is a Merkle DAG and a hash is stable across re-packaging.
4. **Comparison rules.** Two core identifiers are equal exactly when they name the same object; qualifiers are ignored for that comparison, and two qualified SWHIDs are equivalent in context only when their qualifier sets and values are identical (§6.4).
5. **Qualifiers with validity constraints.** Context qualifiers add where an object was seen (`origin`, `visit`) and where inside a tree it sits (`anchor`, `path`); fragment qualifiers narrow it to a range (`lines`, `bytes`). Validity depends on the object type and on other qualifiers, and a conformant implementation must not generate an invalid combination (§6.1–§6.3).
6. **Archival persistence.** A SWHID is an identifier, not a URL, but resolvers exist; the archive's promise is that the object it names remains retrievable as long as the archive holds it.

## 90.3 The digest boundary

A Variorum record identifies bytes (`ID-1`–`ID-3`). A SWHID identifies an object in another model. The two are routinely confused because both are hexadecimal hashes, and the confusion produces records that look right and verify wrong.

Take the same 111 bytes, `spec/vectors/fixtures/hello.txt`, and hash them three ways:

| Computation | Value | What it is |
|---|---|---|
| SHA-256 of the bytes | `a370e4f11b0e59…bef14f7f` | `artifact.digest` and, after `urn:variorum:sha256:`, `id` |
| SHA-1 of the bytes | `affa1e6dfd52ba…5215286c` | neither: no Variorum member and no SWHID uses it |
| SHA-1 of `blob 111` + NUL + the bytes | `bad480af921edb…3c3ae871` | `swh:1:cnt:bad480af…`; also `git hash-object` |

Three values, one byte sequence. The third differs from the second because §5.2 prepends git's blob header before hashing; it differs from the first because it is SHA-1 and not SHA-256. So the friendliest possible case — a `cnt` SWHID, the only type whose subject *is* the artifact's bytes — still does not yield a digest: **the two identifiers are hashes of different pre-images.** Neither can be computed from the other, and a record that copied one into the other's field would be stating a falsehood that a reader with the file can detect in one command.

The other four types are further away still:

| Type | What the SHA-1 covers | Changes when | Checkable from the artifact alone? |
|---|---|---|---|
| `cnt` | `blob <size>` + NUL + the bytes (§5.2) | the content changes | yes: recompute the blob hash |
| `dir` | `tree <size>` + NUL + a sorted serialisation of entry names, normalised modes and child hashes (§5.3) | an entry's name, mode or content changes | no: needs every child and the serialisation rules |
| `rev` | `commit <size>` + NUL + tree reference, parents, author and committer lines with timestamps, extra headers, message (§5.4) | the tree, a parent, the metadata or the message changes | no: needs the whole DAG |
| `rel` | `tag <size>` + NUL + target, target type, tag name, tagger line, message (§5.5) | the target, the name, the metadata or the message changes | no: needs the target object |
| `snp` | `snapshot <size>` + NUL + the sorted branch-to-target map (§5.6) | any recorded branch moves | no: needs the reference set |

Two consequences matter for a versioning standard.

**A `dir` SWHID is not a tarball.** It hashes names, modes and content hashes; it does not hash mtimes, ownership, compression, archive framing, `.gitignore`d files or empty directories — none of which git records. Two release archives built from the same tree at different times, on different hosts, with different compression levels, have two different `artifact.digest` values and one `dir` SWHID. That is not a defect in either standard: the digest says *which file you hold*, and the SWHID says *which source tree is inside it*. A host that regenerates its source archives (many forges do) changes the first without touching the second, and that is precisely the case where the two identifiers earn their keep side by side.

**A `rev` SWHID is not a tree either.** It covers commit metadata — author, committer, timestamps, message — so rewriting a commit message without touching a single file changes the `rev` SWHID and leaves the `dir` SWHID identical. Neither is "more correct": they answer different questions.

## 90.4 Qualifiers: context yes, fragments no

**SWH-4.** Qualifiers carried in the claim MUST satisfy SWHID's producer constraints, which this bridge holds a record to because a record is generated by a producer (§6.1: a conformant implementation *shall not generate* invalid qualifiers or combinations):

- each qualifier appears at most once (§6.2.1, §6.3.1);
- `visit` requires `origin`, and its value MUST be a core SWHID of object type `snp` (§6.3.3);
- `path` is valid only when the object type is `cnt` or `dir`, and its value MUST be an absolute path beginning with `/` (§4: `ipath-absolute`; §6.3.4);
- `anchor` requires `path`, and its value MUST be a core SWHID of object type `dir`, `rev`, `rel` or `snp` (§6.3.5);
- `origin` MUST be a URI with a scheme, as RFC 3986 defines one (§6.3.2);
- a core SWHID used as the value of `visit` or `anchor` carries no qualifiers of its own (§4: `<identifier_core>`).

The distinction between the two halves of §6.1 is what makes this rule legitimate rather than over-strict. An implementation that *reads* a SWHID with `path` on a `rev` ignores the qualifier; a producer must never generate it. A record is on the producing side, so the bridge rejects the combination instead of silently discarding part of a claim.

**SWH-5.** A record claiming this bridge MUST NOT carry a fragment qualifier: neither `lines` nor `bytes`. Both are valid SWHIDs — of a fragment (§6.2). A record describes exactly one artifact (`ID-9`), and a fragment is not an artifact: a record whose claim pointed at lines 9–15 of a file would leave a reader unable to say whether the record is about the file or about those lines. A producer that needs to cite a fragment uses a self-namespaced extension key (`CORE-10`).

Context qualifiers are worth keeping because they answer questions the artifact cannot: `origin` says where the object was observed, `visit` pins the snapshot of the repository at that observation, and `anchor` plus `path` place a content at a location inside a tree. None of them is a Variorum member, and none of them belongs in one (90.9).

## 90.5 Identity remains the digest

**SWH-6.** A record claiming this bridge MUST carry `id` in the `urn:variorum:` form derived from `artifact.digest` (`ID-7`, `ID-8`), MUST NOT record a SWHID — or any value derived from one — as `artifact.digest`, and MUST NOT use a SWHID as `id`.

The temptation is specific here, not generic. A SWHID is stable where a digest is not: rebuild the archive, recompress the tarball, move the repository, and `artifact.digest` changes while the SWHID does not. That stability is real, and it is exactly why the SWHID cannot be the identity: identity in this format is the claim a reader verifies against the bytes in hand (`ID-1`), and no SWHID of a `dir`, `rev`, `rel` or `snp` can be verified that way at all.

The SWHID lives in `extensions["variorum:swhid"].swhid`, one pointer away and never a substitute. A project that wants both stabilities records both: the digest of the bytes it publishes and the SWHID of the object it came from.

**SWH-7.** A consumer that holds both the artifact and a claim whose SWHID has object type `cnt` MUST recompute the SWHID from the bytes — the SHA-1 of `blob <size>`, a NUL byte and the bytes (§5.2) — and MUST report a mismatch between the record and the artifact rather than silently preferring one of them.

This is the only SWHID a reader can check locally, and it is worth stating as an obligation because the check is cheap and the failure is silent. For `dir`, `rev`, `rel` and `snp` no local check exists: verification requires the archive, which recomputes the object from what it stores. The bridge does not pretend otherwise.

## 90.6 Choosing the object type

One SWHID per record forces a choice, and the choice is meaningful because the five types form a chain inside the archive.

| The project wants to cite | Record | Why |
|---|---|---|
| The released tag of a source repository | `rel` | the release object names the target and carries the tag name and message |
| A commit, when releases are not tagged with annotated tags | `rev` | the commit is the archived object |
| A source tree with no usable history | `dir` | the tree is the object |
| A single file's exact bytes | `cnt` | the content is the object, and the only type a reader can verify locally |

Recording the highest object the archive holds is usually right: `rel` points at `rev` (or at a `dir` for an imported release), `rev` points at a `dir`, and the archive can walk down. Walking down requires the archive, so a project that wants a locally checkable claim records the `cnt` as well — in a second record, or in a namespaced extension key until this bridge defines a multi-object form.

## 90.7 Who answers which question

| Question | Authoritative document | Where |
|---|---|---|
| Which exact bytes is this? | Variorum | `artifact.digest`, `id` (`ID-1`, `ID-7`) |
| Which archived source object does this artifact come from? | SWHID | `extensions["variorum:swhid"].swhid` |
| Is this source tree identical to that archived tree? | SWHID | compare core `dir` identifiers (§6.4) |
| Where was this object observed, and at which snapshot of the repository? | SWHID | `origin`, `visit` qualifiers |
| Where inside a tree does this content sit? | SWHID | `anchor`, `path` qualifiers |
| Which version is this? | the scheme named in `scheme` | `scheme` ([02-scheme.md](../02-scheme.md)) |
| What is its lineage, how was it produced, where in its lifecycle? | Variorum | `lineage`, `recipe`, `state` |
| Who asserts all of this? | Variorum | `attestation` ([06-attestation.md](../06-attestation.md)) |

SWHID has no version, no lifecycle and no signature. A `rel` object carries a *tag name*, which may look like a version (`v2.3.0`) and is not one: it is a string chosen by the project when the tag was created, it can be changed by re-tagging a different commit as a new release object, and two projects can tag the same tree differently. A record that needs a version states it in `scheme`, under the scheme's own rules.

## 90.8 Object types are not interchangeable

**SWH-8.** A consumer MUST NOT treat a `dir`, `rev`, `rel` or `snp` SWHID as identifying the artifact's bytes, and MUST NOT infer from two such SWHIDs being equal that the two records describe the same artifact.

Several distinct artifacts share one `dir` SWHID: every tarball, zip and git archive of the same tree, in every compression and at every packaging date. One tree has many `rev` SWHIDs, one per commit whose root directory it is. One revision has many `rel` SWHIDs, one per tag object pointing at it. One `snp` SWHID is shared by every artifact that was present at a given state of a set of branches.

For `cnt` the implication runs the other way and is useful: equal `cnt` SWHIDs do mean identical bytes, and therefore the same `artifact.digest` and the same `id` (`ID-13`). It is still not a way to *fill* those members — the digest is computed from the bytes (`ID-3`), never transcribed from an identifier that happens to name them.

## 90.9 Mapping in both directions

| From | To | Rule |
|---|---|---|
| SWHID core `swh:1:cnt:…` | `extensions["variorum:swhid"].swhid` | as the archive emitted it, shape-checked only (`SWH-2`) |
| `cnt` SWHID | `artifact.digest` | does not map: same bytes, different algorithm and different pre-image (§5.2, 90.3) |
| `dir`/`rev`/`rel`/`snp` SWHID | `artifact.digest` | does not map: the subject is another object, not the artifact's bytes (90.3) |
| SWHID with `lines` or `bytes` | — | does not map: a fragment is not an artifact (`SWH-5`, `ID-9`) |
| `origin` qualifier | `producer` | does not map: where an object was observed, not who produced it (§6.3.2) |
| `visit` qualifier | `created` | does not map: a snapshot of branch targets, not a timestamp (§6.3.3) |
| `anchor` + `path` | `lineage` | does not map: a location inside a tree is not a derivation (§6.3.4) |
| `rev` parents | `lineage.parent` | does not map: commit ancestry is a version-control relation between revisions, not a derivation of one artifact from another ([03-lineage.md](../03-lineage.md)) |
| `rel` tag name | `scheme.version` | does not map: a tag is a name, and a version belongs to a scheme (`SCH-7`) |
| SWHID, any type | `attestation` | does not map: an SWHID is unsigned; the archive's integrity is Merkle integrity, not authorship ([06-attestation.md](../06-attestation.md)) |
| Variorum `state`, `recipe` | — | does not map: SWHID has no lifecycle and says nothing about production |
| Variorum `scheme.version` | — | does not map: the archive does not version the artifact (90.7) |

A record never synthesises a SWHID from its own members. `artifact.name` does not yield a `dir` SWHID, `created` is not a `visit`, and a `lineage` edge does not imply that the parent exists in the archive. The direction Variorum → SWHID is empty, and saying so is more useful than inventing a mapping.

## 90.10 Conformance

- Every rule here is exercised by `spec/vectors/swhid.json`. The vectors that exercise a bridge rule carry `"bridge": "variorum:swhid"` (`CON-28`), plus one accept vector without the claim, which proves an unclaimed record stays a core record. `SWH-7` and `SWH-8` are exempted with a reason: both bind a consumer that holds the artifact or the archive.
- An implementation that claims the SWHID bridge MUST pass those vectors. An implementation that does not claim it skips them and remains conformant at its declared level (`CON-9`).
- No rule here changes what a record with no SWHID claim means. A record for an artifact that happens to be archived, without the claim, says nothing about the archive: the absence of the claim licenses no conclusion about the artifact's presence there, just as silence is not a denial in the C2PA bridge.

## 90.11 What this bridge does not do

- It does not look anything up. It does not call the Software Heritage API, resolve a SWHID, or confirm that the archive holds the object.
- It does not recompute hashes for `dir`, `rev`, `rel` or `snp`; that requires the object's children and metadata, which the record does not carry. For `cnt` it states the recomputation as a consumer obligation (`SWH-7`) and performs none itself.
- It does not run git, parse a tree, or walk a commit DAG. The compatibility with git's object identifiers (§5.8) is "practical but incidental" in SWHID's own words, and this bridge relies on it only as prose, never as a definition.
- It does not decode or normalise qualifier values, reorder qualifiers, or rewrite the SWHID into a canonical form; it validates the shape and stores the archive's string.
- It does not convert a SWHID into a digest, a version, a timestamp or a signature, and it does not accept a fragment where the record identifies a whole artifact.
