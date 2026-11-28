# ADR-0018 — A conformance report accounts for the vectors it did not run

**Status:** accepted
**Date:** 2026-11-28

## Context

`CON-9` makes bridge vectors opt-in: an implementation that does not claim a bridge "MUST skip it rather than fail it". The suite now holds 211 vectors, 93 of them bridge-only and all of those class `core`, so an implementation claiming `core` and no bridge runs 67 vectors while one claiming every level and every bridge runs 211. Both can print the same word, `PASS`, and nothing in either report says which suite the word was measured against.

The skip rule protects implementers from a suite that grows bridges they never asked for (ADR-0009, ADR-0010). What it left unaccountable is the report. A runner that skips the vectors it fails and passes the rest produces a report identical to one that skipped exactly the bridges it does not claim — the difference lives in a flag, not in the artifact anyone reads. The reference runner implements every bridge, so it had nothing to skip and never grew the accounting; `conform --verbose` appeared in §7.5's command block with no defined behaviour beyond the provenance of a failing vector.

This is the same argument `CON-10` settles for rejections: an implementation must cite at least one of the vector's rules, because a verdict nobody can trace is not a conformance result. A pass count over an unstated subset has the same defect, one level up.

## Options

1. **Leave it.** `CON-9` is satisfied by any runner that remembers which bridges it implements, and no vector can observe a report. Rejected: that argument would also make `CON-10` optional, and a report is the only surface on which an implementation's claim can be checked at all.
2. **A machine-readable `conform --json` report with its own schema.** Rejected: this repository's contract is the record format. A schema for tool output would be a second contract, versioned separately, with no consumer — and the accounting is arithmetic a reader can do from text.
3. **One line per skipped vector.** Rejected: 144 lines in the common case, and it restates what the reader already has, because the suite is public and every vector has a name. What the reader cannot derive from the suite alone is the denominator a given claim implies.
4. **A profile of the suite by class and by bridge, printed under `--verbose`, and a rule requiring a report to account for every vector.** Chosen.

## Decision

- **`CON-29` is new (§7.5).** A conformance report MUST account for every vector in the suite — passed, failed or skipped — and a skipped vector MUST name whether its class or its bridge was not claimed (`CON-9`). An implementation MAY produce the accounting on request rather than by default, but MUST NOT state a pass total without the vectors it did not run.
- **`conform --verbose` prints the profile.** One line per class: the total, the count without a bridge claim, and the bridge-only count. One line per bridge: the total and the classes it spans, marked "only with the bridge claimed (CON-9)". One closing line reconciling the smallest claim the suite admits — `core`, no bridge — against the suite total, splitting the skips into bridge-only and outside-the-level.
- **Every number is derived from the loaded suite.** No document stores a count; a vector added to any file moves the profile with it, which is also how the suite's own tests check it.
- **The profile prints whether the run passes or fails.** It describes the suite and a claim, not the run. A report that appears only on failure cannot tell a reader what a green pass skipped.

## Consequences

- **Spec:** §7.5 gains `CON-29` and the paragraph that defines the profile.
- **Tool 0.11.0:** `CONFORMANCE_CLASS_ORDER` (with `CONFORMANCE_CLASSES` derived from it, so the four names have one source), `conformance_profile(vectors)`, and the `--verbose` output. The `--verbose` help string now names the profile.
- **Tests:** `tests/test_vectors.py` gains `ProfileTests` — the class lines sum to the suite total, every bridge present in the suite has exactly one line whose count matches its vectors, the closing line adds up, and `--verbose` prints the block while the default output does not.
- **CHANGELOG:** `CON-29`, the tool version, and the profile under `Added`.
- No vector and no exemption changes: `CON` rules describe the suite and the act of conformance, and were never in the coverage denominator (`spec_rule_ids` scans the record families only).

## What this ADR does not do

- **It does not make the reference runner skip anything.** It implements every bridge, so its profile is a description of what other implementations must skip, not of what this one did.
- **It does not add a report type to the record format.** `CON-29` binds an implementation's report, not a record; nothing in `schema/` changes.
- **It does not decide which levels or bridges a project claims.** Graded conformance stays declarative (ADR-0004); the profile only makes the declared scope auditable.
