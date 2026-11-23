# ADR-0008 — Scheme names are opaque unless reserved

**Status:** accepted
**Date:** 2026-11-23

## Context

`spec/02-scheme.md` contains two statements that disagreed. SCH-2 admits any lowercase name matching `^[a-z][a-z0-9-]*$`; an unnumbered sentence below the reserved table said that custom schemes *outside the list* **MUST** use the `x-` form. The schema and the reference validator implemented the stricter reading as a closed enumeration of the eleven reserved names plus `x-…`, so a record using a perfectly reasonable name such as `dv` — or even a reserved-looking name the table did not anticipate — was rejected.

This matters more than it looks. The reserved table is explicitly *informative*: it is a vocabulary, not a gate. A consumer that meets `dv` must treat it as opaque and move on; rejecting the record because the name is unfamiliar turns a naming convention into an interoperability failure, and it makes the registry a closed list that a standard cannot honestly maintain.

## Decision

- **SCH-2** remains the normative shape: any lowercase name matching `^[a-z][a-z0-9-]*$` is valid.
- The `x-` prefix is a **SHOULD**, promoted to its own identifier, **SCH-10**: a name outside the reserved table should carry `x-` so that it does not collide with a name the table reserves later. A violated SHOULD is a warning (ADR-0005), never a rejection.
- The schema pattern and the validator accept any lowercase name. `x-` is checked only to emit the SCH-10 warning.

## Rationale

A registry that grows over time cannot also be a validation whitelist: every addition to the table would retroactively invalidate records that were valid yesterday. The only stable contract is the shape of the name, not its membership in a list.

The `x-` prefix is still worth recommending — it is cheap, it prevents exactly the collision the table creates by expanding — but it cannot be a MUST without breaking invariant 3 (*wrap, don't replace*): a project that already calls its scheme `dv` must not be forced to rename it to adopt Variorum.

## Consequences

- Records using unregistered lowercase scheme names validate without warnings; records using an `x-` name validate too.
- A record using a non-`x-` custom name is valid with a SCH-10 warning. Implementations that print no warnings are still conformant (ADR-0005).
- Adding a name to the reserved table is a clarification of meaning, never a narrowing of what is legal.
- Two vectors cover the pair: any lowercase name is accepted, and the warning is exercised in `tests/test_validate.py` rather than asserted as invalidity.
