# AGENTS.md — variorum

Permanent context for any agent working in this repository. Read this before touching anything.

## What this project is

An **open specification** for a sidecar record that identifies, traces and attests artifacts (software or content, human- or machine-made). The repository *is* the source of truth: there is no product to build, only a normative document, a schema, a reference validator and real examples.

This is a **spec-nucleus** repository. Consumers are external projects that adopt the format and declare conformance; they never live here.

## Language boundary

- **English** for everything agent-facing and normative: `spec/`, `schema/`, `AGENTS.md`, `README.md`, `GOVERNANCE.md`, code, commit messages, `.agents/`.
- **Spanish** only for owner-facing conversation and the validation notes in `NAME.md`.

A standard is consumed internationally. Normative text in Spanish would halve its audience on day one.

## The four invariants

These are the design decisions everything else derives from. Do not violate them without a new ADR.

1. **Identity is the digest.** An artifact is identified by `sha256:` of its bytes. Never by a filename, never by a date, never by a version number.
2. **The version is a claim; the record is the evidence.** Variorum references the scheme a project already uses and never redefines ordering. `semver:1.4.2` keeps SemVer's precedence rules; Variorum does not touch them.
3. **Wrap, don't replace.** Adopting Variorum must never force a project to renumber its releases. A record is additive.
4. **Graded conformance.** A project can adopt `core` on day one and never implement lineage, recipes or attestations. Partial adoption must be legitimate and declarable.

## Normative language discipline

- Use RFC 2119 keywords (**MUST**, **MUST NOT**, **SHOULD**, **MAY**) only where you mean them, always in capitals.
- Every normative statement gets a stable identifier (`CORE-3`, `LIN-2`) so implementations can cite it and conformance suites can test it.
- Do not invent normative behaviour inside examples. Examples illustrate; only `spec/` defines.
- If a rule cannot be tested, it is not a rule — it is a preference. Rewrite it as a SHOULD or move it to rationale.

## Working rules

- **Do not add dependencies to `tools/`.** The reference validator runs on Python 3.11+ with the standard library only. A standard whose reference implementation needs a package manager is a standard nobody runs.
- **Schema and spec must not drift.** Every schema change is mirrored by a spec section and a CHANGELOG entry.
- **Examples must be real.** They come from actual projects (`du-vortoj`, `la-enpenso`, `software-tools`), with real digests recomputed from the actual files. Never fabricate an example digest.
- **Version the spec, not the repo.** Tags are `spec/vX.Y.Z`.
- **Decisions go to `docs/adr/`.** The reasoning behind a normative rule is as important as the rule.

## Session protocol

At the start of every session read, in order:

1. `.agents/STATE.md` — where the work stands
2. `.agents/HANDOFF.md` — what the previous session left open
3. `.agents/CONTEXT.md` — architecture and current design
4. `.agents/MEMORY.md` — lessons learned and mistakes to avoid
5. `.agents/PLAN.md` — roadmap and checklist

During the session, append notes to `.agents/SESSION.md`. At the end, update `STATE.md`, `HANDOFF.md` and `MEMORY.md`.

## Commits

Conventional Commits, always in English, detailed body — the history is context for future agents:

```
feat(spec): add lineage relation types and cycles prohibition

Defines the seven derivation relations and makes cycles invalid.
Cites LIN-1..LIN-5. Adds schema branch and two conformance vectors.
```

## Autonomy

The owner has authorised autonomous daily work with direct pushes to `main`. Green: writing spec text, schema, tools, examples, docs, tests. Yellow: renaming normative concepts, changing field names, dropping conformance classes — propose first. Red: relicensing, changing the standard's name, publishing to package registries.
