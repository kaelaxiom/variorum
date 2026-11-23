# 04 — Recipe

How the artifact was produced.

## 4.1 The recipe object

**REC-1.** The `recipe` member, when present, MUST be an object.

**REC-2.** `recipe.kind` MUST be present and MUST be one of `manual`, `build`, `generative`, `hybrid`.

| Kind | Meaning |
|---|---|
| `manual` | Produced by human action with no automated pipeline; the recipe is descriptive |
| `build` | Produced deterministically by executing a build from declared sources |
| `generative` | Produced by a model from a prompt and/or inputs; output is not byte-reproducible |
| `hybrid` | A pipeline with both deterministic and generative stages |

## 4.2 Build

**REC-3.** When `kind` is `build`, the recipe MUST identify the source and the toolchain.

**REC-4.** `recipe.source` MUST be an object carrying either `digest` (a Variorum id or a `sha256:` digest of the source archive) or `ref` (a repository URI plus commit).

**REC-5.** `recipe.tool` SHOULD identify each tool in the chain by `name` and `version`.

```json
"recipe": {
  "kind": "build",
  "source": { "ref": "https://github.com/cazucito/libri-alms", "commit": "d4d8aed" },
  "tool": [ { "name": "typst", "version": "0.13.1" } ],
  "environment": { "os": "debian-13", "arch": "amd64" }
}
```

## 4.3 Generative

**REC-6.** When `kind` is `generative`, the recipe MUST identify the tool and the prompt.

**REC-7.** `recipe.tool` MUST be an object with `name` and `model`.

**REC-8.** `recipe.tool.snapshot` SHOULD be present and SHOULD identify the exact model snapshot or revision. When the provider publishes no snapshot identifier, the producer MUST record `generatedAt` at the recipe level.

**REC-9.** `recipe.prompt` MUST be the prompt as sent, verbatim, including any system or negative prompt in `parameters`.

**REC-10.** `recipe.seed`, when the generator accepts one, SHOULD be recorded.

**REC-11.** `recipe.parameters` SHOULD record every parameter that affects the output: resolution, duration, frame rate, aspect ratio, guidance, steps, voice, style.

**REC-12.** `recipe.determinism` SHOULD be one of `none`, `seeded`, `full`, declaring how much of the output the recipe actually determines.

```json
"recipe": {
  "kind": "generative",
  "tool": { "name": "higgsfield", "model": "grok_video", "snapshot": "2026-11-20" },
  "prompt": "Static camera, hands pressing a brick onto a course. No cuts, no zoom.",
  "seed": 41827,
  "parameters": { "resolution": "1080x1920", "fps": 24, "duration_s": 15, "start_image": "R4-C1" },
  "determinism": "none"
}
```

**REC-13.** A producer MUST NOT claim `determinism: "full"` unless a re-execution has been verified to produce the identical digest.

This rule exists because the opposite is common. Recording `seed` does not make a diffusion pipeline reproducible; providers change weights, schedulers and hardware kernels between runs. A field that lies is worse than a field that is absent.

## 4.4 Inputs

**REC-14.** `recipe.inputs`, when present, MUST be an array of objects each with a `ref` and a `role`.

**REC-15.** A `ref` MUST be either a Variorum `id` or an absolute URI.

**REC-16.** `role` SHOULD be a short token naming the function of the input: `start_image`, `end_image`, `reference`, `mask`, `audio`, `transcript`, `dataset`, `style`.

**REC-17.** Inputs that are themselves artifacts with records SHOULD be referenced by Variorum `id` rather than by path, so that the input's own lineage remains reachable.

## 4.5 Manual and hybrid

**REC-18.** When `kind` is `manual`, the recipe MAY be limited to `steps` as an array of strings.

**REC-19.** When `kind` is `hybrid`, the recipe MUST carry a `stages` array; each stage MUST have a `kind` of `build` or `generative` and MUST satisfy the rules for that kind.

## 4.6 Recipes describe claims, not guarantees

**REC-20.** A recipe states what the producer says was done. It MUST NOT be read as a guarantee of reproducibility.

**REC-21.** A consumer MUST NOT report an artifact as "reproducible" on the strength of a recipe alone.
