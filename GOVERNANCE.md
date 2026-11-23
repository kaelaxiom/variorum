# Governance

## Current model: benevolent dictator

`variorum` is authored and maintained by Kael Axiom. Until the specification reaches `1.0.0`, change control is deliberately fast: one maintainer, no committee, no voting.

This is stated openly because an open standard that hides its governance is not open — it is a personal project wearing a standard's clothes.

## How decisions are made

| Kind of change | Process |
|---|---|
| Editorial (typos, clarity, examples) | Direct commit to `main` |
| New normative rule, new field, new conformance class | ADR in `docs/adr/` before merge |
| Breaking change to the record format | ADR + `CHANGELOG` entry + version bump of the spec |
| Removal of a conformance class or field | Requires a deprecation cycle, never a silent removal |

Every normative rule carries a stable identifier in the spec (`CORE-1`, `LIN-4`, …) so that implementations and conformance suites can cite it precisely.

## Versioning of the specification itself

The spec follows SemVer, because a spec *does* have consumers whose implementations can break:

- **MAJOR** — an existing conformant record can become non-conformant.
- **MINOR** — new optional fields, new conformance classes, new relations.
- **PATCH** — editorial only, no semantic change.

Tags: `spec/vX.Y.Z`.

## Compatibility promise

Within a MAJOR version:

- A record valid under `1.x` MUST remain valid under `1.y` for all `y > x`.
- Unknown fields MUST be ignored by consumers, never rejected. This is what allows independent extensions.
- A conformant consumer MUST NOT refuse a record solely because it carries fields from a newer MINOR.

## Path to wider governance

If the specification acquires implementations outside this repository, governance moves to a lightweight model: maintainers listed in `MAINTAINERS.md`, lazy consensus on the issue tracker, and a public changelog of every normative decision. That step is not taken pre-1.0 — committees are a poor way to write a first draft.

## Licensing of contributions

By contributing you agree that code contributions are licensed Apache 2.0 and specification contributions CC BY 4.0, without additional terms.
