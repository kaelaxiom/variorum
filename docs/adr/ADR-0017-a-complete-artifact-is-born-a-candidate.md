# ADR-0017 — A complete artifact is born a `candidate`, not a draft

**Status:** accepted
**Date:** 2026-11-28

## Context

`STA-7` and `STA-9` made `draft` the only way into a lifecycle: with no transitions, `state.current` MUST be `draft`, and the first transition MUST start at `draft`. §5.2 defines `draft` as "In progress; not yet proposed for review".

Phase 3's third case study met an artifact for which that is false from its first instant. Four Suno takes of *Liora* arrive complete from the provider; nothing about them was ever in progress, and nobody has decided anything about them. The vocabulary's word for them already exists — `candidate`, "Complete and awaiting a decision" — and the machine made it unreachable without a transition. Reaching it would mean writing `draft → candidate` with an `actor` and an `at` (`STA-4`), recording a decision with a name and a date that never existed, in order to arrive at a state that is simply true. The case study omitted `state` rather than invent that entry, which is legal (`STA-15`) and gives up the one thing the section exists to record.

The defect is not that `candidate` is missing. It is that the machine required a transition to reach a state that asserts no decision. A transition is an attestation; a record must not need one to say where it starts.

## Options

1. **Add a `generated` state.** It names the means, not the status. The fact that a model produced the bytes already has a home — `producer.kind: "software"`, and `recipe.kind: "generative"` with its tool, model, prompt and determinism — called for by `REC-1` and `REC-2` in the section built to describe production. A `generated` state would be a third copy in the one section whose subject is decisions (`STA-14`), and the only copy no rule could check. It also creates a second premise that no rule can distinguish from `draft`: a machine output can be edited by hand afterwards, and a hand-made file can come out of a script. What matters at birth is whether the artifact is complete, not what made it.
2. **Redefine `draft` as "no decision recorded".** It answers by changing the word rather than the machine, and leaves the vocabulary with two names for "nothing decided" and none for "being worked on". Every consumer who has met the word before would still read a finished take labelled `draft` as unfinished — the misreading the case study refused. `draft` is worth keeping as the premise "this may still change".
3. **Leave `STA-15` silence as the only answer.** Silence means "no declared lifecycle": the right answer for an artifact ingested from an old archive (`software-tools`' 2002 installer, `3d-printerator`'s fit-test STLs) and the wrong one for a producer that has just made the thing. It would make the most common machine workflow — generate a batch, then judge — inexpressible, and push every generative project to omit the section.
4. **Two premises, no new vocabulary.** `draft` and `candidate` are the only two states that assert no decision: "may still change" and "complete, nothing decided". Let both be held with an empty transition list, and let the first transition start at either. Chosen.

## Decision

- **`STA-7` is extended.** When `transitions` is empty, `state.current` MUST be `draft` or `candidate`.
- **`STA-9` is extended.** The first transition MUST have `from` equal to `draft` or `candidate`.
- **The principle those two clauses now state:** only a premise may be held without a transition; every state that asserts a decision requires one. The five decision states — `approved`, `published`, `superseded`, `rejected`, `archived` — remain unreachable without an `actor` and an `at`. A record with `"current": "approved"` and no transitions is still invalid: a decision without a decision-maker is exactly what the transition list exists to prevent.
- **`candidate` may be archived** (§5.4). A batch that is shelved without ever being judged had no exit: `approved` and `rejected` are decisions about the work, `draft` is a return for rework, and `archived` is "retained but no longer active". Shelving is a decision about activity rather than quality, which is the kind `STA-14` permits. Without the edge, a record would have to record a rework it never did — the same fabricated transition this ADR removes.
- **`state` is not a record of provenance** (§5.6, prose). A `generated` state was refused above; the section now says why, once, so the next case does not reopen it.

**What does not change.** The seven values and their glosses; every other edge of §5.4; `STA-11`'s terminal `rejected`; `STA-15`'s distinction between no state and an undecided one; and every existing record. The shipped `la-enpenso-shot-01` records keep their `draft → candidate` transition, which remains legal and now says something more specific: the take was worked on before it was complete.

**The schema gains a description, not an assertion.** `STA-7` and `STA-9` compare `current` with the transition list, and the schema has never encoded that comparison: it carries the structural contract while the vectors are the conformance contract (ADR-0006). Encoding the empty-list half alone would make a JSON Schema validator reject some state-machine errors and accept others, with no test in this repository able to compare the two renderings. The `state` description names the two premises and the decision rule; no `enum`, `const` or conditional is added.

## Consequences

- **Spec:** `spec/05-state.md` — `STA-7` and `STA-9` extended, a new "premises" paragraph and example in §5.3, `candidate → archived` in §5.4, and the provenance refusal in §5.6.
- **Schema:** a `description` on the `state` object naming the two premises and the decision rule. No `enum`, `const` or conditional is added.
- **Tool 0.10.0:** `INITIAL_STATES = {"draft", "candidate"}` gates `STA-7` and `STA-9`, and `LEGAL_TRANSITIONS["candidate"]` gains `archived`.
- **Vectors:** two vectors that encoded the old assumption are replaced — `state/empty-transitions-mean-draft` ("the only honest current state is draft") and `state/first-transition-starts-at-draft` — by two rejects for the claims that are still false (`approved` with no transitions; a first transition from `approved`) and three accepts that pin the new shapes: a take born a `candidate`, a candidate rejected without a draft step, and a candidate archived without a judgement. Suite 208 → 211.
- **Tests:** `tests/test_validate.py` — the test named `test_first_transition_must_start_at_draft` asserted the old clause and used a transition `candidate → candidate` that `STA-10` rejects anyway; it is replaced by one that isolates `STA-9` (`approved → published` with no earlier history). New tests cover both premises with an empty list, the still-invalid decision state, and the two new edges.
- **Docs:** the three case studies that reasoned from the old clause — `echo-language` (which omitted `state`), `software-tools` (which cited `STA-7` as forcing `draft`), `3d-printerator` (same, for its fit-test STLs) — state the new rule and, in `echo-language`, that the batch's honest record can now carry `candidate` with no transitions.

## What this ADR does not do

- **It does not give a generated take a state of its own.** The vocabulary does not multiply with the number of ways an artifact can be made; `candidate` was already the right word, and the fix was to stop requiring a fabricated transition to reach it.
- **It does not let an archive claim a decision it cannot date.** A file served for years but never approved by a recorded act still has no `state`, and `STA-15` still says that is different from `draft`. `published` requires a transition with an actor and a date, and remains out of reach to a producer reconstructing history from a changelog.
- **It does not touch the ordering of versions, the digest, or any bridge.** The change is inside §5 and additive: every record valid under 0.1 remains valid.
