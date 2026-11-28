# ADR-0015 — A recipe can determine the content without determining the bytes

**Status:** accepted
**Date:** 2026-11-27

## Context

`REC-12` listed three determinism grades and had never defined any of them: `none`, `seeded`, `full`. Phase 3's second case study produced the first measurement that fits none of the three.

`3d-printerator` records a binary STL built from a parametric OpenSCAD source. The committed STL and two rebuilds with the declared toolchain contain **the same 7,492 triangles** — same vertices, same normals, same attribute words, same 84-byte header, same bounding box — and **three different SHA-256 digests**, because the facet order differs between runs. Under the format's own first principle those are three artifacts, not one.

The vocabulary could not describe it:

- `determinism: "full"` is forbidden: `REC-13` requires a verified identical digest, and there is none.
- `determinism: "none"` would be false in the other direction: the recipe determines the geometry completely.
- So the record omitted the member, and the absence is not a claim. A consumer cannot tell a producer who measured "content, not bytes" from one who never considered the question — and `STA-15`'s rule that silence is legal makes that ambiguity explicit without resolving it.

The case study recorded the gap as an open question for 0.2 rather than patch a shipped enum on the strength of one measurement. The measurement was repeatable — the same three-way result on every run — and the shape is not exotic: any serialization that embeds a timestamp, a generated document id or a non-canonical ordering has one content and many byte sequences.

A second, smaller defect surfaced while reading the member. `schema/variorum.schema.json` enumerated `determinism` as `["none", "seeded", "full"]` although `REC-12` is a SHOULD. A record carrying `"determinism": "maybe"` therefore validated with a warning from the reference tool and was **rejected** by a standard JSON Schema validator. `CON-8` says a record that violates only a SHOULD remains conformant, so the schema was stating a MUST the specification does not contain. The same file already avoids this for extension names, where its pattern is deliberately looser than `CORE-10`'s recommendation "so that a warning is not turned into a schema rejection".

## Options

1. **Leave `REC-12` alone and document the absence.** The case study's record stays honest, and the standard keeps a vocabulary that cannot express a measured middle. Every future adopter with the same measurement faces the same silence.
2. **Add `geometry`.** Names the CAD case exactly and every other case wrongly: a PDF's content is page content, a text file's is lines, an image's is pixels, an archive's is entries. The thing that is determined is not geometry; it is the content, whatever the medium calls it.
3. **Add `content`.** A grade that speaks about the output rather than the encoding: the same values under a stated normalization, not necessarily the same bytes. Applies to CAD, PDF, text, images and archives without a domain in its name.
4. **Split the member.** `determinism` becomes an object — `{ "grade": …, "basis": … }` — or two members, one for bytes and one for content. Every record written so far carries a string; this breaks the shape for one fact and adds a second grammar to a member that only needed a fourth word.

## Decision

- **Option 3.** `REC-12`'s vocabulary becomes `none`, `seeded`, `content`, `full`, and the four are defined in a table rather than listed. `content` claims that a re-execution produces the same geometry, text or values under the normalization the record states, but not necessarily the same bytes, so the digest may differ.
- **`REC-13` is extended, not duplicated.** A producer MUST NOT claim `content` unless a re-execution has been verified to produce the same content under the stated normalization — the same standard of evidence `full` already demands for the identical digest.
- **`REC-22` names the basis.** A record claiming `content` SHOULD state the normalization as a non-empty string in `parameters.normalization` on the object that carries the claim — the recipe, or the stage of a hybrid recipe (for example `"binary STL: the multiset of triangles, facet order ignored"`). The normalization is what makes the grade testable, and the digest cannot stand in for it: two files with the same geometry have different digests by construction.
- **`REC-12` stays a SHOULD.** A MUST would make an unrecognised grade invalid, and the case for `content` is precisely that the author of a vocabulary cannot foresee every case. The reference tool warns; a closed enum would teach the next adopter to omit the member instead.
- **The schema stops asserting.** `determinism` carries a description and no `type`, `enum` or other assertion. This is not a rule change: `CON-8` and ADR-0005 already decided that a SHOULD violation is a warning, and the schema was the implementation that disagreed.
- **No new member for the normalization.** A dedicated member (`determinismBasis`) was considered. `parameters` already holds producer-supplied facts no rule can verify — the `echo-language` records keep the provider's content id there — and a new member would add surface without adding a check.

## Rationale

**A vocabulary is a standard's memory of cases.** `REC-12` could only say what its author had imagined. The first adopter who measured a case outside it had two options that were both lies and one that was silence. Adding the word costs one enum entry; not adding it costs every adopter the same silence.

**`content` is the word the case used.** The case study's own summary is "this recipe determines the shape, not the bytes"; the record says `content` because the general case is content, and CAD is one medium of it. `canonical` would assert that the artifact is in canonical form — something the record cannot know — and `semantic` names a theory rather than a comparison.

**The claim needs its basis or it cannot be tested.** `full` is unambiguous: the digest either repeats or it does not. `content` is not: "the same content" is a statement relative to a normalization, and without one a consumer will do the natural thing — compare digests — and report a correct recipe as irreproducible. `REC-22` is a SHOULD rather than a MUST because a one-line string can never fully specify a comparison, but its absence is a warning for exactly the same reason.

**Honesty keeps its old price.** `REC-13` is exempt from the vectors for both grades: whether a producer actually ran the recipe twice is invisible in the record. Extending the rule to `content` does not make the claim verifiable; it makes the same demand of the producer that `full` already made.

## Consequences

- `spec/04-recipe.md` gains the four-grade table, `REC-22`, and a build example with `determinism: "content"`; `REC-13` covers both verified grades.
- `spec/vectors/recipe.json` gains three vectors: a `content` claim with its normalization, one without (a warning, not a rejection), and an unrecognised grade (likewise). The suite moves to 204 vectors in thirteen groups; coverage to 100/140 rules referenced, 40 exempt, 0 uncovered.
- Reference tool 0.8.0 defines `DETERMINISM_GRADES`, warns `REC-12` for an unknown grade and `REC-22` for a `content` claim with no normalization.
- `schema/variorum.schema.json` documents the vocabulary in a description instead of enforcing it; `tests/test_schema.py` compares every closed vocabulary the schema and the tool share, and fails if `determinism` grows an assertion again.
- `docs/case-studies/3d-printerator.md` now dates the record's absence to its stamping rather than presenting it as the standard's current answer. The record itself could add `determinism: "content"` and `parameters.normalization` in one edit — the measurement behind `REC-13` already exists — but that commit belongs to the adopter's repository, not this one.
- Existing records are unaffected: `none`, `seeded` and `full` keep their meanings, and a record with an unknown grade remains valid with a warning.
- The other two questions the case studies produced — `REC-9`'s single prompt field and a lifecycle state for a generated artifact — are untouched and stay open for 0.2.
