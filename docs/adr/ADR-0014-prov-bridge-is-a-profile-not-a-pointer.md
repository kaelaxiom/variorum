# ADR-0014 — The PROV bridge fixes a projection instead of pointing at a document

**Status:** accepted
**Date:** 2026-11-27

## Context

`spec/90-extensions/README.md` planned a PROV bridge with a question already written into the table: *"Variorum is a serialisation of a PROV subset. Which subset, and what is deliberately omitted?"* The four written bridges all answered a different question — where to point — because each of them points at a document another standard gives an identity to: a `urn:c2pa:` manifest URN, a SWHID, an SPDX document namespace (`ADR-0011`, `ADR-0012`, `ADR-0013`).

PROV offers none of that. A PROV document is "an anonymous instance, called the toplevel instance, together with zero or more named instances, called bundles" (PROV-CONSTRAINTS §1.2); no member is required to name it; a PROV instance need not be valid; and the namespace reserves five attributes (`prov:label`, `prov:location`, `prov:role`, `prov:type`, `prov:value`) of which none hashes bytes (§5.7.2). Meanwhile the two models overlap heavily — entity, activity, agent, derivation, attribution — and the overlap is where the wrong mappings live: `created` looks like `prov:generatedAtTime`, `producer` looks like `prov:wasAttributedTo`, and Variorum's `generation` relation shares a word with PROV's Generation event.

Four shapes were on the table:

1. **Pointer.** `extensions["variorum:prov"] = {version, document, entity?}`, copying the SPDX claim shape.
2. **Embed.** A `prov` member holding entities, activities and relations inside the record — the record as a partial PROV serialisation.
3. **Profile.** A claim of one member, `version`, that licenses a member-by-member projection and nothing else; no foreign document, no foreign hash.
4. **No bridge.** Leave the relationship to the sentence already in [00-overview §8](../../spec/00-overview.md) and let readers make their own mappings.

## Decision

- **Profile (3).** The claim is `extensions["variorum:prov"]` with exactly one member, `version` (`"2013"`), the date the PROV family was recommended (`PROV-1`…`PROV-3`).
- **No `document` member.** A URI would assert the existence of a file that no rule can distinguish from a typo, that nothing requires to be valid, and that PROV does not require to have a name. A pointer bridge is honest only when the foreign standard gives the pointed-at thing an identity a reader can act on (90.8).
- **No `checksum` member, and none is invited.** PROV has no hash term; a checksum in the claim could only duplicate Variorum's digest or carry a value with no subject (`PROV-3`).
- **The projection is written down member by member**, including the members that do not map (`state.supersededBy`, `attestation`, `scheme` ordering) and the two that belong to the record rather than the artifact: `created` and `producer` attach to the bundle, never to the entity (90.4).
- **Identity stays material.** `id` is derived from `artifact.digest` (`ID-7`, `ID-8`); no PROV identifier, qualified name or blank node becomes an `id`, and `alternateOf`/`specializationOf` are refused as lineage because PROV says they are not influences (§5.5.1, §5.5.2) (90.6).
- **The word *generation* is disambiguated.** Variorum's `generation` relation is `prov:wasDerivedFrom` with a `prov:type`, never `prov:wasGeneratedBy`; the activity that generated the artifact belongs to `recipe`, not to a lineage edge (90.5).
- **Three consumer rules, exempted.** `PROV-4`, `PROV-5` and `PROV-6` bind a reader holding a graph: no attribute is the digest, a derivation without a named type is not one of the eight relations, an invalidation is not a `rejected` state, and an attribution is not a signature.
- **No MUST is added to `core`.** The class model stays at four and the bridge binds only the records that claim it (ADR-0009 applies unchanged).

## Rationale

**A pointer needs a name, and PROV refuses to supply one.** The other four bridges exist because their standard hands out an identifier: C2PA a manifest URN, SPDX a namespace that must be unique, SWHID an identifier that is itself a hash. Copying that shape for PROV would produce a claim whose `document` member is a producer-typed URI with no constraint beyond "looks like a URI" — a validator checking syntax and a reader learning nothing. A rule that cannot be tested is a preference, and a member that carries one is a preference with a schema.

**The useful content of this bridge is a list of mistakes not to make, and each one is specific.** `created` is the record's timestamp, so projecting it onto the entity dates a 2002 installer to 2026 and no test of the graph can tell. `producer` is the record's creator, so `prov:wasAttributedTo(entity, archive)` says the archive built the binary. `lineage.parents[].relation: "generation"` is a model run, not a `prov:wasGeneratedBy`. A pointer bridge would have said none of this, and a reader mapping record to graph would make all three errors and find them plausible.

**PROV's identity is nominal and Variorum's is material, so the projection runs one way only.** §5.7.1 makes two entities with one identifier the same entity, which is a sentence Variorum cannot accept unqualified: the same identifier over two byte sequences is a false record (`ID-1`), and the digest is the only thing that can tell. The projection uses `id` as the entity's identifier so that PROV's naming carries the digest, and the reverse direction refuses every PROV identifier, because a prefix declaration is not a hash (§5.7.5).

**Embedding would make the record a second-rate PROV serialiser.** Shape (2) fails on the same argument as `CORE-15`: metadata cannot live inside the thing whose hash it defines, and a record that grows an entity/activity/relation model of its own would have two grammars to keep in step — the projection table and the embedded graph — with no test that could compare them.

**The divergences are the document's value, not its problem.** PROV permits a derivation cycle that Variorum forbids (`LIN-7`), allows an invalid instance, has no signature, and has no ordering. Each is stated in 90.2 and 90.7 rather than smoothed over, because a bridge that pretends the two models agree produces exactly the records that verify wrong.

## Consequences

- `spec/90-extensions/prov.md` defines `PROV-1`…`PROV-6`; `spec/vectors/prov.json` holds the vectors, each marked `"bridge": "variorum:prov"` (`CON-28`), including an accept vector without the claim and one whose `scheme.name` is a word PROV uses.
- `PROV-4`…`PROV-6` are exempted in `spec/vectors/exemptions.json`: no record decides what a consumer concludes from a graph it does not contain.
- Reference tool 0.7.0 validates `PROV-1`…`PROV-3`; `schema/variorum.schema.json` types the claim as a closed object with `version` fixed to `"2013"`.
- The bridge has no fixture and no foreign document to parse: the projection is made of the record's own members, so every vector needs only a record, and no unit test has to recompute a foreign hash.
- `spec/00-overview.md` §8 stops calling the PROV alignment "planned" and points at the bridge. `spec/90-extensions/README.md` moves `prov.md` from Planned to Written; CycloneDX remains planned.
- A PROV-N, PROV-O or PROV-XML rendering is out of scope. The bridge names terms, not syntax, and a serialiser is a tool for a producer, not a rule for a standard.
- A record without the claim is unaffected, even when its artifact appears in a PROV graph: silence is not a denial (90.10).
