# Examples

Real records from real artifacts. Every digest here was computed from the actual file, not written by hand — a fabricated example digest would teach an implementer to do the same.

| Directory | Artifact | Teaches |
|---|---|---|
| [la-enpenso-shot-01](la-enpenso-shot-01/) | Two generative video takes, one rejected and one approved | Lineage, sibling semantics, generative recipe, terminal rejection |
| [instruisto-guide-owasp](instruisto-guide-owasp/) | A released course guide PDF | Wrapping an existing SemVer label unchanged, the `v` and monorepo tag problem, a build recipe read from the artifact |
| [software-tools-inventory](software-tools-inventory/) | A generated JSON report | Build recipe, a custom scheme wrapped unchanged, full lifecycle |
| [du-vortoj-mark](du-vortoj-mark/) | A brand PNG | Core conformance only, `scheme: none`, declared limitations |

## Running them all

```bash
for record in examples/*/*.variorum.json; do
  python3 tools/variorum.py validate "$record" || exit 1
done

python3 tools/variorum.py graph examples/la-enpenso-shot-01/*.variorum.json --mermaid
```

## Naming convention

Each record is named `<digest-prefix>.variorum.json` (CORE-13) because several records live in the same directory. When a record sits next to the single artifact it describes, the name is `variorum.json`.
