# SESSION — 2026-11-22

## Objective

Found the repository and produce a v0.1 draft of the Variorum specification.

## Done

- Created `/mnt/thoth/projects/variorum`, git init, local identity configured.
- Name selected (`variorum`) after validating nine candidates against `u-onoma` POLICIES §7 with live collision searches (Firecrawl local + GitHub).
- Owner decisions recorded: umbrella scope, public repo under `kaelaxiom` with later transfer, full v0.1 deliverables, 6-hour autonomous cadence.
- Wrote `NAME.md`, `README.md`, `AGENTS.md`, `GOVERNANCE.md`, `.agents/` protocol.
- Wrote `spec/00`–`06`, `schema/variorum.schema.json`, `tools/variorum.py`, three real examples.

## Decisions

- Identity is the digest (`urn:variorum:sha256:<hex>`); the record is a sidecar, never embedded — metadata cannot live inside the bytes whose hash it defines.
- The standard wraps existing schemes and never redefines ordering.
- Conformance is graded: `core`, `lineage`, `recipe`, `attestation`.

## Open

- Conformance suite and vectors.
- Whether `recipe` should allow free-form `extensions` at the top level or only per section (deferred to ADR-0004).
- A public domain for the specification site has not been decided.
