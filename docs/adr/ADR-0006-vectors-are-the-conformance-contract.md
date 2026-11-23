# ADR-0006 — Conformance is defined by data, not by prose

**Status:** accepted
**Date:** 2026-11-23

## Context

Until now a second implementation could only demonstrate conformance by reading 120 rules of prose and hoping it interpreted them the same way. AGENTS.md already states the principle — *if a rule cannot be tested, it is not a rule* — but nothing enforced it: the reference CLI was both the implementation and the only evidence.

A test suite written in Python would test the Python implementation. It would not tell a Rust or JavaScript implementer what to run.

## Decision

Conformance for implementations is defined by a **machine-readable vector suite** in `spec/vectors/`, described normatively in `spec/07-conformance.md`:

- Each vector carries a record (or a patch over a group base), an expectation (`valid: true|false`), and the rule identifiers it exercises.
- Three vector kinds exist: `record` (validate one record, optionally against a fixture artifact), `graph` (resolve several records and decide whether the graph is acyclic), and `jcs` (canonicalise a record and compare the exact bytes that would be signed).
- An implementation conforms when it accepts every accept vector, rejects every reject vector, and cites at least one of the listed rule identifiers for each rejection.
- `variorum conform` runs the suite. It is the reference runner, not the definition: any implementation can run the same JSON files.

The suite is versioned separately from the record format (`"suite": "variorum-vectors/1"`) because vectors are added for existing rules without changing the format.

Coverage is a property of the repository, enforced by `conform --coverage`: every rule identifier in `spec/00`–`spec/06` MUST be referenced by at least one vector or listed in `spec/vectors/exemptions.json` with a reason. The exemption list is the honest admission of which rules are obligations on producers, consumers or storage rather than properties of a record.

## Rationale

Data beats prose for the same reason digests beat version numbers: it is verifiable by a party who does not trust the author. A vector is a record plus an expected verdict; two implementations that agree on the vectors agree on the format, at least on everything the suite covers — and the coverage check makes "everything it covers" an explicit, auditable set rather than an accident.

Vectors are also the cheapest form of bug report. A disagreement between two implementations becomes one JSON file in a pull request.

## Consequences

- The reference CLI gains a `conform` subcommand and can no longer call itself conformant on its own authority.
- A normative change is incomplete until a vector exercises it; a new rule without a vector fails CI.
- Rules that cannot be decided from a record (producer honesty, consumer caution, storage retention) must be declared in `exemptions.json` with a reason, which makes the untestable residue visible instead of implied.
- CI runs the suite on every push (`.github/workflows/ci.yml`), with no third-party Python packages.
