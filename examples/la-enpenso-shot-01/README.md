# Example — la-enpenso, shot 01

Two records for one shot: the rejected first attempt and the approved second one.

| File | Artifact | State |
|---|---|---|
| `b4b9ac719a3f.variorum.json` | `…video-shot-01.raw-v1-rejected.mp4` (3,840,669 B) | `rejected` |
| `b0d1bfac8fc9.variorum.json` | `…video-shot-01.raw.mp4` (2,683,457 B) | `approved` |

Source files (not in this repository — they are production assets):

```
/mnt/thoth/projects/la-enpenso/output/discipline/gardan/
```

## What this example demonstrates

- **Sibling semantics.** The second take is a `revision` of the first, not an upgrade. Both remain retrievable with their full history.
- **A terminal rejection.** The rejected artifact stays in the graph. Deleting it would erase the evidence that it existed, which is precisely the information a studio later needs.
- **A generative recipe with honest determinism.** `determinism: "none"` — recording a seed does not make a diffusion pipeline reproducible.
- **A retroactive record.** Both records were authored after the artifacts existed. `created` is when the record was written; `recipe.generatedAt` is when the artifact was produced (taken from filesystem metadata). The distinction is deliberate: a record cannot claim to have observed a process it did not witness.

## Verify

```bash
variorum validate examples/la-enpenso-shot-01/b0d1bfac8fc9.variorum.json
variorum graph examples/la-enpenso-shot-01/*.variorum.json --mermaid
```
