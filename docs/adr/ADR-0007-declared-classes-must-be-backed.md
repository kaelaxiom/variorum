# ADR-0007 — A declared conformance class must be backed by its member

**Status:** accepted
**Date:** 2026-11-23

## Context

CORE-7 lets a producer declare conformance classes in `extensions["variorum:conformance"]`. Until now the declaration was purely decorative: a record could declare `lineage` while carrying no `lineage` member at all. The shipped examples did exactly that — two of the three declared `lineage` and had none.

A declaration that can be false is worse than no declaration, because a consumer that trusts it skips the check it would otherwise make. The invariant the whole standard rests on — *the version is a claim; the record is the evidence* — applies with equal force to the conformance claim itself.

## Decision

Two new normative rules, defined in `spec/07-conformance.md`:

- **CON-5.** `extensions["variorum:conformance"]`, when present, MUST be an array of known class names (`core`, `lineage`, `recipe`, `attestation`).
- **CON-6.** A record that declares a class other than `core` MUST carry the corresponding member. Declaring `lineage` without a `lineage` member is a validation error.

Under-declaration remains a SHOULD violation and therefore a warning (CORE-7): a record carrying `recipe` but not declaring it is conformant, and an implementation may point it out.

## Rationale

The asymmetry is deliberate. Declaring too much is a lie and is rejected; declaring too little is modesty and is at most noted. This keeps the strict rule on the side where trust is at stake, and keeps the gentle rule on the side where a forgotten field costs nothing.

`core` needs no member of its own: it is the baseline every record must satisfy anyway.

## Consequences

- The two examples that declared `lineage` without one are corrected. The records themselves are unchanged; only the claim was wrong.
- Generators that emit a conformance declaration must derive it from the members they actually wrote, not from a template.
- A consumer may treat the declaration as a promise about presence, but still MUST NOT infer absence from silence (CORE-8).
