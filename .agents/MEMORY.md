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
