# MEMORY

Lessons learned while working on this repository. Append only; never delete an entry because it became inconvenient.

## 2026-11-22 — Naming

The first naming batch died almost entirely on live collision checks: `stemma`, `spuro`, `editio`, `recensio`, `provenio`, `colophon`, `exemplar`. All were reasonable Latin/Greek roots and all were occupied — several by products in adjacent niches (`colophon.fyi` is literally "publishing infrastructure for AI agents").

**Lesson:** for a public standard, run the collision search *before* getting attached to a name. A root that is semantically perfect and commercially occupied is worth less than a plainer root that is free.

## 2026-11-22 — Scope

The tempting design was "a better version scheme". It would have been unadoptable: nobody renumbers their releases for a new standard.

**Lesson:** standards spread by adding a layer, not by demanding a migration. Wrap, then earn the right to influence.

## 2026-11-22 — Prior art is dense

An *AI Provenance Protocol* with its own versioning section already exists, and SWHID already covers content-addressed identifiers for software. The differentiation has to be explicit in `spec/00-overview.md`, not left implicit.

**Lesson:** in a crowded adjacent space, the overview document is a positioning document. Say what you are not, early.

## 2026-11-23 — Accept vectors find the real bugs

The reject vectors were easy: take a rule, break it, assert a rejection. The accept vectors are what exposed the drift — the validator was rejecting records the specification allowed (`scheme.name` outside a closed list, an extension key without a namespace), because every implemented check had been treated as fatal. No reject vector can ever catch a validator that is too strict.

**Lesson:** for every MUST, write both a reject vector and an accept vector that is one deliberate step away from the boundary. The accept side is where over-strictness hides.

## 2026-11-23 — A fixture digest is code, not prose

A vector that asserts a digest against a stored string can pass forever while the file it describes has changed. Marking digest vectors `fixture: true` and recomputing the hash on every run (CON-19) turns staleness into a suite error (exit 2) instead of a silent pass.

**Lesson:** never let a conformance suite trust a stored hash it can recompute. A stale fixture is a broken test, not a failing record.

## 2026-11-23 — Testability closes the spec, not the code

`conform --coverage` counts every rule identifier in `spec/00`–`spec/06` and fails when one is neither exercised nor exempted with a reason. The exemption list (30 rules) is the first honest map of what this format cannot verify from a file: producer honesty, consumer caution, storage retention, key material.

**Lesson:** the exemptions are part of the standard's honesty, not a to-do list. Whenever a rule is exempted, the reason must say who the obligation falls on; "hard to test" is an admission that the rule is a preference and belongs in a SHOULD.

## 2026-11-23 — A bridge that applies by name is a trap

Applying the SemVer grammar whenever `scheme.name` is `semver` would have made `core` conformance stricter than `SCH-7` allows and retroactively invalidated labels a project already published. The fix was to make the bridge a claim — an extension key the record carries — so the rules bind only the records that asked for them.

**Lesson:** when an extension sharpens a core member, the sharpening must be opt-in and visible in the record. A rule that fires on a name rather than on a claim silently changes what an existing record means.

## 2026-11-23 — Adopting a foreign grammar costs two traps, not one

Implementing SemVer's grammar from the published pattern exposed two host-language traps: Python's `\d` accepts any Unicode decimal digit (matching `١.٢.٣`), and `$` matches before a trailing newline, so `"1.4.2\n"` passed an anchored `match`. Both were caught by testing against the official valid/invalid example list, not by reading the pattern.

**Lesson:** when a specification imports an external grammar, copy that standard's own conformance examples into the tests and run them before trusting the pattern. `re.ASCII` and `fullmatch` (or `\Z`) are the minimum defences in Python.

## 2026-11-24 — A citation is a claim like any other

The C2PA draft carried two confident, well-formatted section references that were simply wrong: "the active manifest is the last one whose content bindings validate" (§15.5.1 says the last manifest in the store) and "the manifest store is one of the exclusions" (exclusions are a mechanism the claim generator may use, and a manifest may carry no hard binding at all). Neither error would have been caught by any test in this repository — both were prose about a document we do not own.

**Lesson:** when a normative sentence summarises a foreign specification, open that specification and check the section before merging. A citation that looks precise is indistinguishable from a correct one until someone follows it.

## 2026-11-24 — ABNF and ecosystem disagree; the bridge must accept both

C2PA's ABNF for its URN allows only uppercase hex digits, yet the UUID string representations its own libraries produce (Java's `UUID.toString()`) are lowercase. A strict copy of the ABNF would reject pointers that real manifests carry. The same ABNF also allows colons inside the claim-generator component, so a regex that excludes them is silently over-strict.

**Lesson:** for a foreign identifier, the accept side is defined by what the foreign ecosystem emits, not only by its grammar. Read the ABNF, then look at what an implementation actually writes — and put both cases in accept vectors.

## 2026-11-24 — "Verbatim" is an untestable MUST

`C2P-2` originally required the URN to be "recorded verbatim". No vector can check that: verification needs the manifest, which the record validator never sees. The requirement is real, but it is a producer obligation, so it belongs in prose, not in a rule the coverage report counts as tested.

**Lesson:** any MUST whose truth depends on a document outside the record is a preference wearing a normative keyword. Keep the checkable shape as the rule; state the fidelity expectation as prose.
