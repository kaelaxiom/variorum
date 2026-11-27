# Case studies

An [adoption guide](../adoption.md) says what to do. A case study shows a project that did it — in its own repository, with its own conventions, under its own constraints. The records described here live in the adopter's repository, not in this one: `examples/` holds records this project ships, a case study holds records someone else ships.

Every case study in this directory meets the same bar:

- **A real adopter.** The record is committed to the project's repository, and the commit is linked, so a reader can read the change instead of a summary of it.
- **A computed digest.** The document names the command or script that hashed the artifact, and the artifact is one the project actually publishes or serves.
- **A declaration.** The project states which conformance classes it satisfies, and says what it deliberately did not adopt.
- **The friction.** What the format made the adopter decide, what the adopter's own conventions decided for them, and anything the standard could state more clearly as a result.

| Case study | Project | Artifact recorded | Classes |
|---|---|---|---|
| [software-tools](software-tools.md) | A private archive of software one person has used since 1991 — 58 fichas, a PHP + SQLite site, 91 download rows in its exported inventory | `Gel86a.zip`, the final GEL 8.6a installer (2002), fetched back from the live site | `core` |
| [3d-printerator](3d-printerator.md) | A repository of 3D-print solutions for real problems — two designs, parametric OpenSCAD 2021.01 sources, binary STLs, SLA resin | `aw9-d2strap-case-v2-holder.stl`, the complete v2 two-watch separator (374,684 B), decided against before printing | `core`, `lineage`, `recipe` |
| [echo-language](echo-language.md) | A transmedia musical project built around a constructed language for singing, generated with Suno Pro | The four discovery takes of *Liora* (3.6–4.3 MB each), each carrying a C2PA manifest embedded by the provider | `core`, `lineage`, `recipe` |

The three Phase 3 case studies are adopted one at a time. The archive came first because it is the hardest direction — it publishes artifacts it did not produce. The second was chosen for the opposite reason: it builds what it records, so `recipe` and `state` could be exercised on an artifact the project produced, including one that lost. The third covers the ground neither could: a content project whose artifacts come out of a model, where the recipe cannot be re-executed, and where the provider has already signed a manifest of its own.
