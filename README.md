# Variorum

[![CI](https://github.com/kaelaxiom/variorum/actions/workflows/ci.yml/badge.svg)](https://github.com/kaelaxiom/variorum/actions/workflows/ci.yml)

**An open record format for identifying, tracing and attesting any artifact — software or content, produced by humans or by machines.**

> 📛 See [NAME.md](NAME.md) for the origin and meaning of the name.

---

## The problem

Version numbers answer one question: *"can I upgrade without breaking something?"*

That question only exists for libraries. For everything else — a rendered video, a dataset, a document, a model, a poster — a version number is asked to carry meaning it was never designed for. It cannot say which exact bytes it refers to, what produced them, where they came from, or whether anyone approved them.

The result is what every studio and every repository eventually accumulates:

```
final.mp4
final_v2.mp4
FINAL_v3_USAR.mp4
final_v3_aprobado_bueno.mp4
```

No scheme fixes that, because the missing information is not a number. It is an **identity**, a **lineage**, a **recipe** and a **state**.

## What Variorum is

A sidecar record — one JSON file, `variorum.json` — that travels with an artifact and states:

| Question | Field | Answer type |
|----------|-------|-------------|
| Which exact bytes is this? | `artifact` (and the `id` derived from it) | `sha256:…` |
| Which version scheme does the project use? | `scheme` | `semver:1.4.2`, `calver:2026.11`, `date:2024-06-20`, … |
| Where did it come from? | `lineage` | a DAG of parents |
| How was it produced? | `recipe` | build, generative or hybrid |
| Is it approved? | `state` | a lifecycle with transitions and actors |
| Who vouches for it? | `attestation` | optional signature |

## What Variorum is not

- **Not a replacement for SemVer or CalVer.** Variorum *wraps* an existing scheme and never redefines its ordering. If your project already says `1.4.2`, it keeps saying `1.4.2`.
- **Not a registry, a service, or a network.** It is a file and a set of rules. It works offline, in a folder, in a git repo, or on a USB drive.
- **Not an AI standard.** AI-made artifacts are a case it covers well, not the reason it exists.

## The thesis, in one line

> **Identity is the digest. The version is a claim. The record is the evidence.**

## Quick example

One record, complete: [`examples/la-enpenso-shot-01/b0d1bfac8fc9.variorum.json`](examples/la-enpenso-shot-01/b0d1bfac8fc9.variorum.json), copied verbatim. The digests were computed from the bytes, nothing is elided, and `tests/test_docs.py` fails if this block stops matching the file it came from.

```json
{
  "variorum": "0.1",
  "id": "urn:variorum:sha256:b0d1bfac8fc9e59be3525f2e4b973ea7017f31e2b35e49e5d6864c3979e941dd",
  "artifact": {
    "digest": "sha256:b0d1bfac8fc9e59be3525f2e4b973ea7017f31e2b35e49e5d6864c3979e941dd",
    "size": 2683457,
    "mediaType": "video/mp4",
    "name": "discipline-gardan-001.es.video-shot-01.raw.mp4"
  },
  "scheme": {
    "name": "x-la-enpenso-shot",
    "version": "001",
    "sequence": 2
  },
  "created": "2026-11-22T21:58:00-06:00",
  "producer": {
    "name": "hermes-agent",
    "kind": "software",
    "software": { "name": "hermes" }
  },
  "lineage": {
    "parents": [
      {
        "id": "urn:variorum:sha256:b4b9ac719a3f127d887b1a4903c3c2c3f3248d4c3500b9b3621e3c2012dc28b8",
        "relation": "revision",
        "note": "Same intent, second attempt after the first take was rejected."
      }
    ]
  },
  "recipe": {
    "kind": "generative",
    "tool": {
      "name": "higgsfield",
      "model": "grok_video",
      "snapshot": "2026-11-20"
    },
    "prompt": "Static camera, locked. A hand presses a brick onto the top course. No cuts, no zoom, no camera movement.",
    "parameters": {
      "resolution": "1080x1920",
      "fps": 24,
      "duration_s": 15,
      "start_image": "R4-C1"
    },
    "determinism": "none",
    "generatedAt": "2026-11-20T08:41:00-06:00"
  },
  "state": {
    "current": "approved",
    "transitions": [
      {
        "from": "draft",
        "to": "candidate",
        "actor": { "name": "hermes-agent", "kind": "software", "software": { "name": "hermes" } },
        "at": "2026-11-20T08:43:00-06:00"
      },
      {
        "from": "candidate",
        "to": "approved",
        "actor": { "name": "cazucito", "kind": "human" },
        "at": "2026-11-20T16:51:54-06:00"
      }
    ]
  },
  "extensions": {
    "variorum:conformance": ["core", "lineage", "recipe"]
  }
}
```

`core` is the five members `variorum`, `id`, `artifact`, `scheme` and `created`; everything below `created` is a conformance class adopted because the project needed it. The scheme is one the project invented and Variorum does not interpret — and `determinism: "none"` is an honest answer, not a missing one.

To adopt it for one artifact: [`docs/adoption.md`](docs/adoption.md). What adoption looks like in a project that did it, with its commit and its own tooling: [`docs/case-studies/`](docs/case-studies/).

## Conformance

Conformance is not a compliment; it is a testable claim ([`spec/07-conformance.md`](spec/07-conformance.md)). The contract is a data suite any implementation can run, in any language:

```
python3 tools/variorum.py conform --coverage
```

- [`spec/vectors/`](spec/vectors/) — 211 accept/reject/graph/canonicalisation vectors in thirteen groups, each citing the rule it exercises.
- [`spec/vectors/exemptions.json`](spec/vectors/exemptions.json) — the rules no record can decide, each with a stated reason.
- **Implementation levels:** `core`, `lineage`, `recipe`, `attestation`. Levels are not a ladder — an implementation may claim `recipe` without claiming `lineage`.
- **Extension bridges:** [`spec/90-extensions/`](spec/90-extensions/) — adjacent standards Variorum coexists with. Written: SemVer ([`semver.md`](spec/90-extensions/semver.md)), C2PA Content Credentials ([`c2pa.md`](spec/90-extensions/c2pa.md)), SWHID ([`swhid.md`](spec/90-extensions/swhid.md)), SPDX ([`spdx.md`](spec/90-extensions/spdx.md)) and W3C PROV ([`prov.md`](spec/90-extensions/prov.md)). A bridge is an opt-in claim and adds no MUST to `core`, so its vectors are required only of implementations that declare the bridge (`CON-28`).
- **Reporting a run:** `conform --verbose` prints the suite's profile, so a report can account for every vector it skipped — by class or by bridge (`CON-29`).

A validator that rejects a record for violating a **SHOULD** is wrong: SHOULD violations are warnings, never errors ([ADR-0005](docs/adr/ADR-0005-should-violations-are-warnings.md)).

## Repository layout

```
spec/                  The normative specification (English)
spec/vectors/          Conformance vectors (data, not code)
schema/                JSON Schema (2020-12) — normative for implementers
tools/                 Reference CLI and conformance runner (Python, stdlib only)
examples/              Real records from real projects
docs/adoption.md       How to adopt it, on one real release
docs/case-studies/     Adoption in real projects, told from their repository
docs/adr/              Decisions taken while designing the standard
.agents/               Continuity protocol for agent sessions
```

## Status

**Draft v0.1** — the specification is complete through section 07 and its conformance suite; the SemVer, C2PA, SWHID, SPDX and PROV bridges are written. Nothing here is stable yet. See [CHANGELOG.md](CHANGELOG.md) and [.agents/STATE.md](.agents/STATE.md).

## Licence

- Specification text: **CC BY 4.0**
- Schemas, tools and examples: **Apache 2.0**

See [LICENSE.md](LICENSE.md). Implementation of the specification is unrestricted; the licence covers the text, not the idea.
