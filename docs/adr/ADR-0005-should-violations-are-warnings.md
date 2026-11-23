# ADR-0005 — A violated SHOULD is a warning, never a rejection

**Status:** accepted
**Date:** 2026-11-23

## Context

The specification uses RFC 2119 keywords deliberately: **MUST** for rules a record cannot break and still conform, **SHOULD** for rules that have legitimate exceptions. The reference validator, however, treated every check it implemented as fatal. A record with an extension key that lacked a namespace (CORE-10, a SHOULD) was rejected exactly like a record whose digest did not match the file (ID-3, a MUST).

Two problems follow. First, the validator is stricter than the specification it implements, which is the worst kind of drift: an implementer who passes the reference tool would fail a correct record produced elsewhere. Second, a conformance suite cannot be written on top of a validator that has no notion of severity — every accept/reject vector would encode the tool's opinion rather than the specification's.

## Decision

Validation produces two severities:

- **error** — a violated MUST. The record is non-conformant.
- **warning** — a violated SHOULD. The record remains conformant; the warning is informative.

`Report.ok` is true when there are no errors. Warnings are reported by the reference tool but are not part of the conformance contract: an implementation is free to omit them entirely.

The executable form of the rule is in `spec/07-conformance.md` (CON-8) and in the vectors: a record that violates only a SHOULD has an accept vector, and no implementation may reject it on that ground.

## Rationale

A standard is only as strong as the agreement between its prose and its reference implementation. Making SHOULD violations fatal silently promotes every piece of advice to a requirement, which is precisely the failure mode RFC 2119 exists to prevent.

There is a cost: a validator that only warns is easier to ignore. That is accepted, because the alternative is a validator that lies about what the specification requires.

## Consequences

- `validate` exits 0 on a record with warnings, printing them to stderr; exit 1 means non-conformance.
- Checks that were fatal but cite a SHOULD become warnings: ID-12, CORE-10, REC-12, REC-5, SCH-10.
- The schema follows: `extensions` property names may omit the `<prefix>:` form (CORE-10 recommends it), and `scheme.name` is no longer a closed enumeration (ADR-0008). A schema that rejects a valid record is the same drift in another file.
- New validators must decide the severity from the keyword in the rule, not from how easy the check was to implement.
- The conformance vectors assert validity only. Warnings are exercised by `tests/test_validate.py`, which tests the reference tool rather than the standard.
