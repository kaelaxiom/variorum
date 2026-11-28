# 05 — State

The lifecycle of an artifact, and who decided what.

## 5.1 The state object

**STA-1.** The `state` member, when present, MUST be an object.

**STA-2.** `state.current` MUST be present and MUST be one of the values in §5.2.

**STA-3.** `state.transitions` MUST be present and MUST be an array. It MAY be empty.

## 5.2 States

| State | Meaning |
|---|---|
| `draft` | In progress; not yet proposed for review |
| `candidate` | Complete and awaiting a decision |
| `approved` | Accepted for its intended use |
| `published` | Released to its audience |
| `superseded` | Replaced by a later artifact |
| `rejected` | Decided against |
| `archived` | Retained but no longer active |

## 5.3 Transitions

**STA-4.** Each transition MUST be an object with `from`, `to`, `actor` and `at`.

**STA-5.** `at` MUST be an RFC 3339 timestamp with an explicit UTC offset.

**STA-6.** `actor` MUST identify the decision-maker, using the same shape as `producer` (`name`, and optionally `kind` and `software`).

**STA-7.** `state.current` MUST equal the `to` of the last transition. When `transitions` is empty, `state.current` MUST be `draft` or `candidate`.

**STA-8.** Transitions MUST be contiguous: each transition's `from` MUST equal the previous transition's `to`. Gaps are invalid.

**STA-9.** The first transition MUST have `from` equal to `draft` or `candidate`.

```json
"state": {
  "current": "approved",
  "transitions": [
    { "from": "draft",     "to": "candidate", "actor": { "name": "hermes-agent", "kind": "software" }, "at": "2026-11-20T14:42:28-06:00" },
    { "from": "candidate", "to": "approved",  "actor": { "name": "cazucito", "kind": "human" },         "at": "2026-11-20T16:51:54-06:00" }
  ]
}
```

A record with no transitions declares a **premise**, not a history. There are two premises, and they are the only two states that assert no decision: `draft` says the artifact may still change, and `candidate` says it is complete and nothing has been decided about it. Neither needs an actor, because nobody decided anything. Every state from `approved` onward asserts that someone decided, and therefore requires a transition naming that actor and the time (`STA-4`).

The distinction matters most for an artifact a machine made. A take that a model produced is complete the moment the provider returns it; writing `draft → candidate` only to reach `candidate` would record a decision, with a name and a date, that nobody made. The record states the premise instead:

```json
"state": { "current": "candidate", "transitions": [] }
```

Its first transition is the first decision actually taken — usually a human's choice between takes — and it starts from `candidate` (`STA-9`). A lifecycle that begins with an attested `draft → candidate` is equally valid and says something different: the artifact was worked on before it was complete ([ADR-0017](../docs/adr/ADR-0017-a-complete-artifact-is-born-a-candidate.md)).

## 5.4 Legal transitions

| From | Allowed to |
|---|---|
| `draft` | `candidate`, `archived` |
| `candidate` | `approved`, `rejected`, `draft`, `archived` |
| `approved` | `published`, `superseded`, `archived` |
| `published` | `superseded`, `archived` |
| `superseded` | `archived` |
| `rejected` | — |
| `archived` | `draft` |

**STA-10.** A transition not listed in §5.4 MUST be treated as invalid.

`archived` is reachable from both premises: shelving undecided work — a draft nobody finished, a candidate nobody judged — is a decision about whether the artifact is active, not a judgement of the work, which `STA-14` permits.

**STA-11.** `rejected` is terminal for an artifact. Re-attempting the work produces a *new artifact* with a `revision` relation to the rejected one — never a resurrection of the same record.

This is the rule that makes the format honest about generative work. A rejected take is not "version 2 of the approved one"; it is a sibling that lost. Keeping it as a sibling preserves the evidence that it existed.

## 5.5 Supersession

**STA-12.** When `state.current` is `superseded`, `state.supersededBy` MUST be present and MUST be a Variorum `id`.

**STA-13.** A superseded artifact MUST remain retrievable. Supersession is a statement about which artifact is current, not a deletion.

## 5.6 What state is not

**STA-14.** State MUST NOT encode quality, score or preference. It records a decision, not a judgement of the work.

**STA-15.** A record without `state` MUST be interpreted as having no declared lifecycle, which is different from `draft`.

The distinction protects honest archives: an artifact ingested from an old backup has no lifecycle, and pretending it is a draft invents a history that never happened.

For the same reason, the vocabulary has no state named for a production method. That a model generated the bytes — with which tool, model and prompt — is `recipe`'s claim (`REC-1`, `REC-2`) and `producer`'s, stated where the record can describe production; a `generated` state would add a third copy of that fact in the one section whose subject is decisions, and it would be the copy no rule could check ([ADR-0017](../docs/adr/ADR-0017-a-complete-artifact-is-born-a-candidate.md)).
