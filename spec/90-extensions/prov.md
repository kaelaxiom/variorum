# 90 — W3C PROV bridge

How a Variorum record is read as a PROV graph — and why this bridge, unlike the four before it, fixes a projection instead of pointing at a document.

**Status:** draft, format `0.1`. Purely additive: this bridge defines no rule that a record outside it must satisfy, and adds no MUST to `core` (see [ADR-0014](../../docs/adr/ADR-0014-prov-bridge-is-a-profile-not-a-pointer.md)).

The vocabulary here follows the PROV family of documents as published on 30 April 2013. *Entity*, *activity*, *agent*, *generation*, *usage*, *derivation*, *attribution*, *association*, *specialization*, *alternate* and *bundle* are used with the meaning PROV-DM gives them and are not redefined here. Sections are cited by number: §5.1 for entities and activities, §5.2 for derivations, §5.3 for agents, §5.4 for bundles, §5.5 for alternate entities, §5.7 for identifiers and attributes, §6 for the extensibility points and §7 for validity. PROV-CONSTRAINTS is cited for what validity means, and PROV-O for the property names a projection writes in RDF.

Three facts about the standard belong before the first rule.

1. **PROV is not versioned.** The family was published once, on 30 April 2013: PROV-DM, PROV-O, PROV-N and PROV-CONSTRAINTS as W3C Recommendations of that date, PROV-XML and PROV-AQ as Notes. No second edition exists. `version` therefore names a date, because a date is the only stable identifier the family offers.
2. **PROV defines no checksum and no document identity.** §5.7.2 lists the five attributes the namespace reserves — `prov:label`, `prov:location`, `prov:role`, `prov:type` and `prov:value` — and none of them hashes bytes. A PROV document is "an anonymous instance, called the toplevel instance, together with zero or more named instances, called bundles" (PROV-CONSTRAINTS §1.2), and nothing in it is required to name it.
3. **A PROV instance need not be valid.** PROV-CONSTRAINTS §1.2 says it in as many words. Validity is a property a graph may have, not one it has because it exists.

## 90.1 The claim

**PROV-1.** A record claims this bridge by carrying the member `extensions["variorum:prov"]`. When present, its value MUST be an object.

**PROV-2.** A record claiming this bridge MUST carry `version`, and MUST NOT claim a version this bridge does not name. This bridge defines one value, `"2013"`: the PROV family as recommended on 30 April 2013 (`PROV-1`…`PROV-6` are written against that edition, and no other exists).

**PROV-3.** This bridge defines exactly one member, `version`. A record claiming it MUST NOT carry other members inside the claim object — in particular no `document`, no `entity` and no `checksum`, for the reasons in 90.8.

```json
"extensions": {
  "variorum:prov": {
    "version": "2013"
  }
}
```

A claim this small is the point, not an oversight. The four earlier bridges point at a document that another standard gives an identity to — a `urn:c2pa:` URN, an SPDX document namespace, a SWHID — and their claim objects carry that identity because a reader can resolve it. PROV offers nothing of the kind, and 90.8 argues why inventing one would be worse than leaving it out. What the claim buys is a reading: the record's sections project onto PROV terms exactly as 90.3 says, no further, and a consumer holding a PROV graph may take back only what 90.7 allows.

## 90.2 What PROV already guarantees

PROV owns the model and this bridge does not restate it. For the purposes of this document the relevant guarantees are:

1. **Three types and one graph.** An entity is "a physical, digital, conceptual, or other kind of thing with some fixed aspects" (§5.1.1); an activity "occurs over a period of time and acts upon or with entities" (§5.1.2); an agent "bears some form of responsibility for an activity taking place, for the existence of an entity, or for another agent's activity" (§5.3.1). Entities and activities are joined by generation and usage events (§5.1).
2. **Derivation is deliberately undefined.** "PROV does not attempt to specify the conditions under which derivations exist; rather, derivation is considered to have been determined by unspecified means" (§2.1.2). A derivation between two entities is a claim that some influence occurred, and the standard refuses to say which.
3. **Three derivation subtypes.** A revision is "a derivation for which the resulting entity is a revised version of some original" (§5.2.2); a quotation repeats some or all of an entity (§5.2.3); a primary source is a thing a secondary entity was derived from, without hindsight (§5.2.4). Each declares a type — `prov:Revision`, `prov:Quotation`, `prov:PrimarySource` — carried in `prov:type`.
4. **Identity is nominal.** Entity, activity and agent have a mandatory identifier, and "two entities (resp. activities, agents) are equal if they have the same identifier" (§5.7.1). A qualified name maps to an IRI by concatenating the prefix's IRI and the local part (§5.7.5).
5. **Relations are shorthands that can be expanded.** A derivation may optionally name the activity, the generation and the usage behind it (§5.2.1); an association may name the plan the agent relied on (§5.3.3). Every one of those arguments is optional, so the binary form is complete enough to be valid.
6. **Application vocabulary goes in attributes.** `prov:type`, `prov:role` and `prov:location` are the reserved extensibility attributes, and a sub-relation is expressed as `prov:type` on the relation itself (§6; the standard's own example types a derivation as a translation).
7. **Validity is about events, not cycles.** PROV-CONSTRAINTS builds a graph of precedes relations and rejects it when a cycle includes a strictly-precedes edge (§2.4, §6.2). It states no acyclicity requirement on `wasDerivedFrom` itself: two entities may each be derived from the other as far as PROV-DM says, and the contradiction appears only when events are supplied that cannot be ordered.
8. **Nothing is signed, and nothing is ordered.** PROV has no signature term and no canonical serialisation of a statement. A bundle — "a named set of provenance descriptions, and is itself an entity" (§2.2.2, §5.4) — is how provenance of provenance is expressed, not how it is authenticated. And PROV describes what happened; it has no vocabulary for which entity supersedes which.

## 90.3 The projection

A record is read as one PROV instance. This table is the whole of the projection: a member that is absent contributes nothing, and a member that is present contributes exactly the row's terms.

| Variorum member | PROV projection | Note |
|---|---|---|
| `id` | the identifier of the artifact's `prov:Entity` (§5.1.1, §5.7.1) | A URN is already an IRI, so §5.7.5 needs a prefix declaration, not a translation. One entity, one identifier: `artifact.digest` is not a second identifier for it. |
| `artifact.digest` | an attribute on the entity, `variorum:digest` | Not `prov:value`: §5.7.2.5 gives that attribute a different job and lets two entities carry the same one (`PROV-4`). |
| `artifact.size`, `artifact.mediaType`, `artifact.name` | attributes; `name` MAY be `prov:label` (§5.7.2.1) | `prov:label` is a human-readable string and carries no identity. |
| `created` | `prov:generatedAtTime` on the **bundle**, never on the entity | 90.4. |
| `producer` | a `prov:Agent` and `prov:wasAttributedTo(bundle, agent)`, never `(entity, agent)` | 90.4. `kind` selects `prov:Person`, `prov:Organization` or `prov:SoftwareAgent` — the three types §5.3.1 names; `software` is a `prov:SoftwareAgent` associated with the activity of recording. |
| `scheme` | attributes: `variorum:scheme`, `variorum:version`, `variorum:authority` | No PROV equivalent. PROV has no ordering vocabulary, and the label's meaning stays with the scheme (`SCH-7`). |
| `lineage.parents[]` | `prov:wasDerivedFrom(entity, parent)` with `prov:type` naming the `relation` (§6) | The type is what carries the relation; without it the edge says only "derived" (§2.1.2, `PROV-5`). `relation: "revision"` projects to `prov:type: "prov:Revision"` (§5.2.2). |
| `recipe` | a `prov:Activity`; `tool` a `prov:SoftwareAgent` via `prov:wasAssociatedWith`; `source` and `inputs` entities `prov:used` | The expanded derivation of §5.2.1 is where this activity belongs when there is one parent and one recipe. |
| `recipe.prompt` | an attribute of the activity, or a `prov:Plan` associated with it (§2.2.1.2, §5.3.3) | Either is legal; the bridge requires neither, because a plan is an entity with its own provenance and a prompt is a string the provider may not keep. |
| `recipe.generatedAt` | `prov:generatedAtTime` on the entity | The only member in the record that is about the artifact's own creation (90.4). |
| `state.transitions[]` | one `prov:Activity` per transition: `prov:type` naming `from`→`to`, `prov:wasAssociatedWith` the `actor`, `at` as `prov:startedAtTime` and `prov:endedAtTime` | A decision is an activity that used the artifact. `state.current` with no transitions contributes nothing. `rejected` is not an invalidation (`PROV-6`). |
| `state.supersededBy` | nothing | PROV has no ordering: which artifact is current is Variorum's statement (`STA-12`, `STA-13`). |
| `attestation` | nothing | PROV has no signature and no canonical form to sign (90.8). |
| `extensions` other than this claim | attributes, or the projection of the bridge that owns the key | This bridge licenses no other bridge's claim; each is opt-in in its own document. |

Two rows are the load-bearing ones, and each has a section of its own: `created` and `producer` describe the record rather than the artifact (90.4), and `lineage.parents[].relation` is not PROV's `Generation` (90.5).

## 90.4 Two members describe the record, not the artifact

The tempting projection attaches every member of a record to the entity it is about. Two members are not about the artifact at all, and both mistakes produce a graph that is internally consistent and false.

`created` is the record's creation timestamp (`CORE-5`). The record is written by whoever holds the artifact, often long after the artifact existed — the archive in [the `software-tools` case study](../../docs/case-studies/software-tools.md) recorded a 2002 installer in 2026. `prov:generatedAtTime` is "the time at which an entity was completely created and is available for use" (PROV-O), so projecting `created` onto the entity would state that the installer was created in 2026. Nothing in the resulting graph reveals the error: the value is a well-formed `xsd:dateTime` and the statement is syntactically perfect.

`producer` is "the actor that created the record" ([00-overview](../00-overview.md) §4), not the actor that made the artifact. `prov:wasAttributedTo(e, ag)` says that `e` "was generated by some unspecified activity that in turn was associated to agent `ag`" (§5.3.2) — so attaching the producer to the artifact asserts that the archive built the installer. The record has a member for the artifact's own production, and it is `recipe`; the record has a member for decisions about the artifact, and it is `state.transitions[].actor`.

The honest projection therefore puts both members where they belong: the record is a bundle, `created` is the bundle's generation time, and `producer` is the agent the bundle is attributed to. A bundle is an entity like any other (§2.2.2, §5.4), so both statements are legal PROV, and both are about the right subject.

One consequence is worth stating. The entity in a projection then has no generation time at all unless the record carries `recipe.generatedAt` (`REC-8`), which exists for generative recipes whose provider publishes no snapshot. PROV permits that: `entity(id)` requires an identifier and nothing else (§5.1.1), and generation is a separate, optional relation.

**A bundle needs its own identifier.** PROV-CONSTRAINTS §7.2 requires the names of a document's bundles to be distinct, and §5.7.1 makes two entities with one identifier the same entity. A producer that names a bundle with the artifact's `id` has stated that the record and the artifact are one thing. This bridge does not choose a naming convention for bundles; it requires only that the name differ from the artifact's `id`.

## 90.5 The word *generation* names two different things

Variorum's `generation` is a lineage relation: an edge from a parent to this artifact, meaning "produced by a generative process from the parent as input" ([03-lineage](../03-lineage.md) §3.2). PROV's Generation is an event: "the completion of the production of a new entity by an activity" (§2.1.1, §5.1.3). They share a word and no meaning.

The error this invites is a category mistake that survives review because both sides look right. A record with `lineage.parents: [{relation: "generation"}]` does not say the artifact "was generated by" anything in PROV's sense; it says the artifact came from a model run that took the parent as input. The projection is `prov:wasDerivedFrom` with a type, not `prov:wasGeneratedBy`, and the activity that generated the artifact is the `recipe`'s activity, which the lineage edge knows nothing about. `prov:wasGeneratedBy` is therefore never written from `lineage`, and a `relation` value is never written as `prov:Generation`.

The same care applies to the three PROV subtypes that do look like relations. `prov:Revision` corresponds to Variorum's `revision` (§5.2.2). `prov:Quotation` and `prov:PrimarySource` have no Variorum relation of their own: both can land only on `derivation`, the catch-all of §3.2, and a record that needs the distinction keeps the PROV type in `extensions` rather than letting `derivation` erase it.

## 90.6 Identity: nominal in PROV, material in Variorum

PROV's identity is the name you give an entity: an identifier is mandatory, and two entities with the same identifier are the same entity (§5.7.1). Variorum's identity is the artifact's bytes: `id` is derived from `artifact.digest` (`ID-7`, `ID-8`), so two identifiers over one byte sequence describe one artifact, and one identifier over two byte sequences is a false record (`ID-1`).

This bridge makes the two coincide in one direction and refuses to in the other.

**Record → PROV.** The projection uses `id` as the entity's identifier, which makes PROV's nominal identity carry the digest. A reader who wants Variorum's guarantee must still recompute SHA-256 from the artifact: PROV will happily accept the same identifier for different bytes, because it never looks inside the thing it names. The graph inherits the identity; it does not inherit the verification.

**PROV → record.** No PROV identifier becomes an `id`. A qualified name maps to an IRI through a prefix declaration (§5.7.5), and a prefix declaration is not a hash; a blank node is worse, because its name means nothing outside the document that contains it, so the same bytes would get a different identity in every rendering. A record that wants the identity computes it from the bytes.

**Neither direction uses `alternateOf` or `specializationOf`.** They are the terms a reader reaches for when two entities look like two views of one thing, and PROV is explicit that neither is a derivation: "a specialization is not, as defined here, also an influence" (§5.5.1), and an alternate is the statement that two entities "present aspects of the same thing" (§5.5.2), carrying no identifier and no attributes of its own. Three takes of one prompt are three entities with three digests and a common ancestor — a lineage question (`LIN-6`, `LIN-10`), not an alternate one. Writing `alternateOf` between them would say they are aspects of one entity, which is exactly the claim the digest exists to refuse.

## 90.7 What a reader may bring back

**PROV-4.** A consumer MUST NOT treat `prov:value`, or any attribute of an entity, as `artifact.digest`. `prov:value` is "a direct representation of an entity as a PROV-DM Value" and may occur at most once (§5.7.2.5), two entities may carry the same value (§5.7.2.5, Example 53), and a value's "interpretation is outside the scope of PROV" (§5.7.3). A hash is a string PROV assigns no meaning to; the digest is a value the reader recomputes from the bytes (`ID-3`).

**PROV-5.** A consumer MUST NOT read `prov:wasDerivedFrom` as one of the relations of [03-lineage](../03-lineage.md) §3.2 unless the derivation's `prov:type` names it, and MUST NOT read `prov:specializationOf` or `prov:alternateOf` as lineage at all. PROV does not define when a derivation holds (§2.1.2), the binary form carries no type (§5.2.1), and the two alternate relations are not influences (§5.5.1, §5.5.2). A derivation with a `prov:type` the record's scheme does not name is a derivation whose relation is unknown, and it MUST NOT be written as one of the eight.

**PROV-6.** A consumer MUST NOT read `prov:wasInvalidatedBy` or `prov:invalidatedAtTime` as a `state` transition, and MUST NOT read `prov:wasAttributedTo` as `attestation`. Invalidation means the entity is "no longer usable" (PROV-O), while Variorum's `rejected` and `superseded` describe decisions about an artifact whose bytes stay retrievable (`STA-11`, `STA-13`); and attribution is an unsigned ascription to an agent (§5.3.2) while `attestation` is a signature over the record's canonical bytes (`ATT-6`).

All three rules bind a reader rather than a record, and all three are exempted in [`spec/vectors/exemptions.json`](../vectors/exemptions.json) for that reason. No record decides what a consumer concludes from a graph it does not contain.

## 90.8 Why the claim carries no document and no checksum

A pointer bridge is honest when the foreign standard gives the pointed-at thing an identity the reader can act on: a C2PA manifest has a `urn:c2pa:` URN, an SPDX document has a unique namespace, a SWHID is its own identifier. PROV gives nothing of the sort. A document is an anonymous toplevel instance plus bundles (PROV-CONSTRAINTS §1.2); no member is required to name it; and a PROV instance need not be valid, so a URI would assert the existence of a file whose consistency nothing checks. A `document` member would therefore be a string the producer typed, indistinguishable from a typo, and a validator could check its shape and nothing else — the definition of a preference wearing a rule's clothes.

A `checksum` member is worse. PROV reserves five attributes and none hashes bytes (§5.7.2), so a checksum in the claim could only be Variorum's own digest written twice, or a foreign value with no subject to attach it to. The first is the copy `SPDX-6` already refuses; the second is a value no reader can reproduce.

What remains is the mapping, and the mapping is checkable from the record alone: that is the test a bridge should pass. A reader can compare the record with a PROV graph and say, member by member, what must be there and what must not. That is more than a pointer to an unverifiable URI would buy.

## 90.9 Who answers which question

| Question | Authoritative document | Where |
|---|---|---|
| Which exact bytes is this? | Variorum | `artifact.digest`, `id` (`ID-1`, `ID-7`) |
| What is the artifact's place in a provenance graph? | PROV | entities, activities, agents and their relations |
| Which version is this, and which artifact supersedes which? | the scheme named in `scheme`, and Variorum | `scheme`, `state` (`STA-12`) |
| When was the artifact created? | the record, when it knows | `recipe.generatedAt` (`REC-8`); *not* `created` (90.4) |
| When was the claim written, and by whom? | Variorum | `created`, `producer` (`CORE-5`) |
| What was it derived from, and how? | Variorum | `lineage`, with typed relations (`LIN-4`) |
| How was it produced? | Variorum | `recipe` |
| Who asserts all of this? | Variorum | `attestation` (`ATT-6`), never `prov:wasAttributedTo` |

## 90.10 Conformance

- Every record rule here is exercised by [`spec/vectors/prov.json`](../vectors/prov.json). The vectors that exercise a bridge rule carry `"bridge": "variorum:prov"` (`CON-28`), plus one accept vector without the claim, which proves an unclaimed record stays a core record — including a record whose `scheme.name` happens to be a word PROV uses. `PROV-4`, `PROV-5` and `PROV-6` are exempted with reasons: all three bind a consumer.
- An implementation that claims the PROV bridge MUST pass those vectors. An implementation that does not claim it skips them and remains conformant at its declared level (`CON-9`).
- No rule here changes what a record with no PROV claim means. A record for an artifact that appears in a PROV graph, without the claim, says nothing about the graph: silence is not a denial, exactly as in the other bridges.
- This bridge defines no fixture. It has no foreign document to parse and no foreign hash to recompute: the projection is made of the record's own members, and every vector needs only a record.

## 90.11 What this bridge does not do

- It does not serialise anything. It names the terms a projection uses, not the syntax: PROV-N, PROV-O and PROV-XML are all legal renderings, and this document writes none of them.
- It does not validate a PROV graph, and does not claim that a graph produced from a record is valid. PROV-CONSTRAINTS decides validity, and its verdict depends on events a record does not carry.
- It does not convert PROV shortcomings into Variorum members. A graph with no `prov:type` on a derivation does not become a record with a guessed relation (`PROV-5`); an invalidation does not become a `rejected` state (`PROV-6`); an attribution does not become a signature.
- It does not cover PROV's extended structures — bundles as entities, collections and membership, delegation, plans, influence — beyond the two places where a projection needs them: the record is a bundle (90.4) and a prompt may be a plan (90.3). Everything else in components 4 to 6 has no Variorum counterpart, and none is invented.
- It does not replace the four pointer bridges. A record may carry a PROV claim and an SPDX claim; each binds its own members, and neither licenses the other's.
