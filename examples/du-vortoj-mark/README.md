# Example — du-vortoj, brand mark

The minimal case: identity and nothing else.

- Artifact: `branding/logo/png/DV_mark-integracion-principal.png` (2,081,153 B)
- Scheme: `none` — the project assigns no version label to its logo
- No lineage, no recipe, no state

## What this example demonstrates

- **The core conformance class on its own.** A record that answers exactly one question — *which bytes is this?* — and refuses to invent answers to the others.
- **`scheme: "none"` as a legitimate answer.** Most assets never had a version. Forcing one onto them teaches people to type `v1` and then `v1-final`.
- **A declared limitation.** The mark was produced with model assistance, but no production record was kept at the time. The note says so instead of reconstructing a recipe after the fact.

This is the adoption path the specification expects most projects to take first: stamp the artifacts you already have, and only add recipe and lineage when a workflow can produce them honestly.

## Verify

```bash
variorum validate examples/du-vortoj-mark/df678b70810c.variorum.json
```
