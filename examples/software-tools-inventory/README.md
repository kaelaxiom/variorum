# Example — software-tools, downloads inventory

A generated JSON report from the `software-tools` repository, described with a `build` recipe.

- Artifact: `ops/reports/downloads-inventory.json` (36,207 B)
- Source: `github.com/cazucito/software-tools` at `91d8acf`
- Scheme: `custom: v3` — the project's own "v3" label, carried unchanged

## What this example demonstrates

- **Wrapping a label Variorum does not understand.** `custom` says: this project has a version convention, and it is not one of the shared ones. Variorum carries it without parsing it.
- **A build recipe that admits non-determinism.** The report is a scan of a filesystem; the same commit on the same day produces the same output only if the filesystem is identical. `determinism: "none"` says so.
- **A full lifecycle on a non-media artifact.** `draft → candidate → approved → published`, each step with an actor and a timestamp.

## Verify

```bash
variorum validate examples/software-tools-inventory/184e00a4737c.variorum.json
variorum show    examples/software-tools-inventory/184e00a4737c.variorum.json
```
