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

**STA-7.** `state.current` MUST equal the `to` of the last transition. When `transitions` is empty, `state.current` MUST be `draft`.

**STA-8.** Transitions MUST be contiguous: each transition's `from` MUST equal the previous transition's `to`. Gaps are invalid.

**STA-9.** The first transition MUST have `from` equal to `draft`.

```json
"state": {
  "current": "approved",
  "transitions": [
    { "from": "draft",     "to": "candidate", "actor": { "name": "hermes-agent", "kind": "software" }, "at": "2026-11-20T14:42:28-06:00" },
    { "from": "candidate", "to": "approved",  "actor": { "name": "cazucito", "kind": "human" },         "at": "2026-11-20T16:51:54-06:00" }
  ]
}
```

## 5.4 Legal transitions

| From | Allowed to |
|---|---|
| `draft` | `candidate`, `archived` |
| `candidate` | `approved`, `rejected`, `draft` |
| `approved` | `published`, `superseded`, `archived` |
| `published` | `superseded`, `archived` |
| `superseded` | `archived` |
| `rejected` | — |
| `archived` | `draft` |

**STA-10.** A transition not listed in §5.4 MUST be treated as invalid.

**STA-11.** `rejected` is terminal for an artifact. Re-attempting the work produces a *new artifact* with a `revision` relation to the rejected one — never a resurrection of the same record.

This is the rule that makes the format honest about generative work. A rejected take is not "version 2 of the approved one"; it is a sibling that lost. Keeping it as a sibling preserves the evidence that it existed.

## 5.5 Supersession

**STA-12.** When `state.current` is `superseded`, `state.supersededBy` MUST be present and MUST be a Variorum `id`.

**STA-13.** A superseded artifact MUST remain retrievable. Supersession is a statement about which artifact is current, not a deletion.

## 5.6 What state is not

**STA-14.** State MUST NOT encode quality, score or preference. It records a decision, not a judgement of the work.

**STA-15.** A record without `state` MUST be interpreted as having no declared lifecycle, which is different from `draft`.

The distinction protects honest archives: an artifact ingested from an old backup has no lifecycle, and pretending it is a draft invents a history that never happened.
