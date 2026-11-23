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
