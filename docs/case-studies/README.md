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

The three Phase 3 case studies are adopted one at a time; the archive is the first because it is the hardest case: it publishes artifacts it did not produce.
