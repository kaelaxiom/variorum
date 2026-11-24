# Conformance vectors

The machine-readable half of [section 07](../07-conformance.md). Any implementation, in any language, can run these files; `tools/variorum.py conform` is only the reference runner.

```
python3 tools/variorum.py conform --coverage
```

## Layout

| File | Group | Rules |
|---|---|---|
| `core.json` | record shape, version, timestamps, extensions | CORE-1…CORE-10 |
| `identity.json` | digest, identifier, producer | ID-1…ID-12 |
| `scheme.json` | scheme name, version, authority, sequence | SCH-1…SCH-10 |
| `lineage.json` | parents, relations, acyclicity | LIN-1…LIN-8 |
| `recipe.json` | manual, build, generative, hybrid | REC-1…REC-19 |
| `state.json` | lifecycle values and transitions | STA-1…STA-12 |
| `attestation.json` | signature shape, canonical bytes | ATT-1…ATT-7 |
| `conformance.json` | the declaration itself | CON-5, CON-6, CORE-7 |
| `semver.json` | the SemVer bridge, opt-in per record | SEM-1…SEM-5, SEM-7 |
| `c2pa.json` | the C2PA bridge, opt-in per record | C2P-1…C2P-6 |
| `exemptions.json` | rules no record can decide, with reasons | — |
| `fixtures/` | real bytes for the digest rules | — |

## Anatomy of a vector

```json
{
  "name": "identity/digest-mismatch",
  "class": "core",
  "description": "The record claims hello.txt but is checked against other.txt.",
  "rules": ["ID-3"],
  "artifact": "fixtures/other.txt",
  "patch": {},
  "expect": { "valid": false, "rules": ["ID-3"] }
}
```

- `class` — which conformance level the vector exercises (CON-9).
- `bridge` — when present, the extension key of the bridge the vector belongs to (CON-28). Implementations that do not claim that bridge skip these vectors.
- `rules` — the rules the vector demonstrates; `conform --coverage` counts these.
- `record` or `patch` — a complete record, or a shallow patch over the file's `base` (CON-16).
- `artifact` — validate against these bytes; add `"fixture": true` when the record's digest must equal the file's (CON-19).
- `expect.rules` — a rejection must cite at least one of these identifiers (CON-10).

`kind` selects the vector type: `record` (default), `graph` (several records, `expect.acyclic`) or `jcs` (exact canonical bytes, `expect.jcs`).

## Adding a vector

1. Pick the rule from `spec/00`–`spec/06` or from a bridge under `spec/90-extensions/`. If it is a MUST, add a reject vector; if it is a SHOULD, add an accept vector proving a violation does not invalidate the record. A bridge rule also needs `"bridge": "<extension key>"` on the vector (CON-28).
2. Name it `<group>/<what-it-proves>`, in the present tense.
3. Run `python3 tools/variorum.py conform --coverage`. A new rule with no vector and no exemption fails the run.
4. If the rule genuinely cannot be decided from a record, add it to `exemptions.json` with a reason that says why (CON-25).

Never write a digest by hand: create the fixture, run `python3 tools/variorum.py digest <file>`, and paste the output. The `fixture: true` check recomputes it on every run, so a stale digest fails as a suite error instead of quietly passing.
