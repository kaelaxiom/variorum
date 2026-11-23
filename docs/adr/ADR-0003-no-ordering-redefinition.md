# ADR-0003 — Variorum never redefines version ordering

**Status:** accepted
**Date:** 2026-11-22

## Context

The obvious design for a "better versioning standard" is a single unified scheme that replaces SemVer, CalVer, PEP 440, Debian's format and everything else. It would be simpler to specify and much more satisfying to write.

It would also be adopted by nobody. Every ecosystem already has a comparator: npm's semver, pip's packaging, dpkg, rpm, Maven. Replacing them means every tool in every language must change at once, for a benefit measured in tidiness.

## Decision

Variorum **references** a scheme (`scheme.name`, `scheme.version`, `scheme.authority`) and never defines, refines or overrides that scheme's ordering. The version string is opaque to Variorum.

## Rationale

A wrapper can be adopted in an afternoon. A replacement needs a migration of the entire ecosystem, and the first thing a replacement does is implement every other scheme badly — YAML's version-number problems, npm's range semantics, PEP 440's epochs, Debian's tilde. That is a decade of bug reports for a feature nobody asked for.

There is also a correctness argument: **ordering is only meaningful inside a scheme.** Comparing `1.10.0` to `2026.11` is not a hard problem — it is a category error. A standard that permits it invites exactly the confusion it was meant to end.

## Consequences

- Multi-scheme repositories are valid and honest: each artifact declares its own scheme.
- Consumers that need to sort must implement the schemes they care about, or fall back to `scheme.sequence` when the producer supplied one.
- Variorum cannot answer "is version X newer than version Y" across schemes, and does not pretend to. Packages that want total ordering must stay within one scheme.
