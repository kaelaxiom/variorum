# 90 — SemVer bridge

How a Variorum record carries a Semantic Versioning 2.0.0 label without touching SemVer's grammar or its precedence.

**Status:** draft, format `0.1`. Purely additive: this bridge defines no rule that a record outside it must satisfy, and adds no MUST to `core` (see [ADR-0009](../../docs/adr/ADR-0009-semver-bridge-is-opt-in.md)).

## 90.1 The claim

**SEM-1.** A record claims this bridge by carrying the member `extensions["variorum:semver"]`. When present, its value MUST be an object.

**SEM-2.** A record claiming this bridge MUST carry `scheme.name` equal to `semver`.

The claim is an extension key and not a conformance class, deliberately. A conformance class says what a record *is* — it carries lineage, or it does not. A bridge says that one member of the record has been checked against the standard it names. Making bridges classes would multiply the class lattice with every neighbour standard; declaring the bridge as an extension keeps the class model at four (ADR-0009).

The opt-in also preserves `SCH-7`. A core consumer treats `scheme.version` as an opaque label, and it must keep doing so: a record whose scheme is `semver` but which carries no claim is still a valid record, and its label is still unparsed. Only a record that carries the claim accepts the stricter reading, and only an implementation that implements this bridge may enforce it. An implementation that does not implement the bridge ignores the key, as `CORE-3` requires of any unknown member.

```json
"extensions": { "variorum:semver": {} }
```

An empty object is a valid claim. The object exists so that a bridge can carry mapping metadata without inventing top-level members; this bridge defines one member, `tag` (§90.6), and a bridge-aware implementation ignores members it does not recognise.

## 90.2 What SemVer 2.0.0 already guarantees

SemVer owns three questions and this bridge does not restate the answers:

1. **The grammar.** `MAJOR.MINOR.PATCH`, an optional `-PRERELEASE`, an optional `+BUILD`, ASCII only, with no leading zeroes in numeric identifiers. The normative statement is the specification's *Backus–Naur Form Grammar for Valid SemVer Versions* appendix, with item 2 stating the `X.Y.Z` form and items 9–10 the prerelease and build identifier rules; the authoritative URL is `https://semver.org/spec/v2.0.0.html`.
2. **Precedence.** §11 defines the total order between versions: numeric comparison of major, minor and patch, then prerelease rules, with build metadata ignored.
3. **The boundaries of the term.** SemVer defines a *version*, not a range, not a dist-tag, and not a tag with a prefix. Its own FAQ states that `v1.2.3` is a version *tag*, not a version; ranges such as `^1.2.3` belong to package managers, not to SemVer.

Variorum adds only what SemVer does not describe: which bytes carry the label, where they came from, how they were produced, and whether anyone approved them. Those questions live in [01-identity.md](../01-identity.md) through [06-attestation.md](../06-attestation.md) and are unchanged by this bridge.

## 90.3 The version string

**SEM-3.** A record claiming this bridge MUST carry `scheme.version`, and its value MUST be a single version matching the SemVer 2.0.0 grammar: `MAJOR.MINOR.PATCH`, optionally followed by `-PRERELEASE` and `+BUILD`. The string is ASCII, carries no `v` or `=` prefix, is not a range or a wildcard, is not a partial version, and has no surrounding whitespace.

The grammar as a regular expression — the pattern the SemVer FAQ publishes for implementers — is:

```
^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)
(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)
(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?
(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
```

`\d` in that grammar means an ASCII digit, not any Unicode decimal digit. An implementation that applies the pattern in a language whose `\d` is Unicode-aware — Python is one — must restrict the class; the reference tool compiles it with `re.ASCII`. This is not pedantry: a record accepted in one language and rejected in another is exactly the interoperability failure the suite exists to prevent.

The end anchor has a second trap. A regex `$` in Python also matches immediately before a trailing newline, so `1.4.2\n` would pass a naive anchored `match`. An implementation must require the pattern to consume the whole string — `fullmatch`, or `\Z` instead of `$`. The grammar is a statement about every character of the value, not about a prefix of it.

| Value | Verdict | Why |
|---|---|---|
| `1.4.2` | accepted | the base case |
| `0.0.0` | accepted | zero is a version |
| `1.4.2-rc.1` | accepted | prerelease identifiers |
| `1.4.2-rc.1+build.5` | accepted | prerelease and build metadata |
| `v1.4.2` | rejected | a tag with a prefix, not a version |
| `1.4` | rejected | a partial version |
| `^1.4.2` | rejected | a range, which SemVer does not define |
| `1.04.2` | rejected | leading zero in a numeric identifier |
| ` 1.4.2` | rejected | whitespace is not part of the grammar |
| `latest` | rejected | a dist-tag, not a version |

## 90.4 Ordering

**SEM-6.** Versions of records claiming this bridge MUST be ordered by SemVer 2.0.0 precedence and by nothing else. An implementation MUST NOT introduce a tiebreaker drawn from `created`, `artifact.digest`, `state` or the lineage graph, and MUST NOT treat two versions of equal precedence as the same artifact: identity remains the digest (`ID-1`).

Two consequences follow.

First, `1.0.0+build.1` and `1.0.0+build.2` have equal precedence. They may be two different artifacts — different bytes, different digests, both legitimately versioned `1.0.0` because build metadata does not affect precedence. A consumer that sorts them by digest and calls the result "the order" has invented an ordering Variorum never granted.

Second, `created` is when the record was written, not when the version was released. A retroactive record for an old release is newer than the record of a recent one; neither fact orders the versions.

`SEM-6` is an obligation on consumers, so no record can decide it. It is exempted in the vector suite rather than pretended to be testable.

## 90.5 Sequence is not applicable

**SEM-4.** A record claiming this bridge MUST NOT carry `scheme.sequence`.

`SCH-8` offers `sequence` to schemes that define no order. SemVer defines one. Carrying both creates two orderings that can disagree — a record with `scheme.sequence: 5` at `1.0.0` and `scheme.sequence: 4` at `1.1.0` is internally inconsistent in a way no validator can repair, because the specification would have to choose which field wins. It does not choose: the bridge forbids the second field.

## 90.6 Tags that are not versions

A release is published under a *tag*; a version is a value inside it. The two often differ:

| Tag as published | Version | Note |
|---|---|---|
| `v1.4.2` | `1.4.2` | the `v` is a tag convention, not part of SemVer |
| `owasp-api-security/v1.3.1` | `1.3.1` | a monorepo tag names the course or package before the version |
| `release-2026-11` | — | no version: cannot be recorded, and that is correct |

**SEM-5.** When `extensions["variorum:semver"].tag` is present, it MUST be a non-empty string with no whitespace, and it MUST end with the version's precedence part — `scheme.version` with any build metadata (`+…`) removed.

`tag` is optional, and it is the only place where a tag belongs. It is not `scheme.version`, because a tag is not a version; it is not a top-level member, because a tag is a property of the project's release process, not of the artifact's identity. A project that publishes no tags simply omits it.

The suffix rule accepts `v1.4.2`, `course/v1.4.2` and `release-1.4.2` for version `1.4.2`, and rejects `v1.4.1`, `1.4.2-rc.1` (when the version has no prerelease) and `latest`. It permits a prefix because prefixes are project policy; it refuses a different version because that would make the two members contradict each other.

Build metadata is removed before the comparison on purpose. A project may tag `v1.4.2` while the artifact declares `1.4.2+build.5`; the tag carries the precedence part, and the build metadata stays where it affects nothing.

## 90.7 Authority

**SEM-7.** A record claiming this bridge SHOULD carry `scheme.authority` equal to `https://semver.org/spec/v2.0.0.html`.

A violated SHOULD is a warning, never a rejection (ADR-0005). The recommendation exists because `scheme.authority` is what tells a reader which document defines the label; for a reserved scheme name the answer is known, and stating it costs one line.

## 90.8 Mapping in both directions

| From | To | Rule |
|---|---|---|
| SemVer version `1.4.2` | `scheme.version` | verbatim, never reformatted (`SCH-7`, `SEM-3`) |
| SemVer tag `v1.4.2` | `extensions["variorum:semver"].tag` | verbatim, when the project publishes one (`SEM-5`) |
| SemVer precedence | SemVer's own §11 | Variorum adds nothing (`SCH-6`, `SEM-6`) |
| SemVer range `^1.4.2` | — | does not map: a range is not a version (`SEM-3`) |
| SemVer dist-tag `latest` | — | does not map: a dist-tag names a moving pointer (`SEM-5`) |
| Variorum `artifact.digest` | — | does not map: SemVer has no identity for bytes |
| Variorum `created` | — | does not map: SemVer has no timestamp |
| Variorum `state` | — | does not map: SemVer has no lifecycle |
| Variorum `lineage` | — | does not map: SemVer has no derivation graph |

A record never synthesises a SemVer label from its own fields. `state.current: published` does not imply that a SemVer release exists, and `created` is not a version date. The direction Variorum → SemVer is therefore mostly empty, and saying so is more useful than inventing a mapping.

## 90.9 Precedence preserved, end to end

Given records whose versions are the SemVer §11 example chain, any consumer that orders them must produce exactly this sequence:

```
1.0.0-alpha
1.0.0-alpha.1
1.0.0-alpha.beta
1.0.0-beta
1.0.0-beta.2
1.0.0-beta.11
1.0.0-rc.1
1.0.0
```

and then, for a pair such as `1.0.0+build.1` and `1.0.0+build.2`, no order at all: they have equal precedence, and which one is "later" is not a question SemVer answers or Variorum asks.

The bridge verifies that the label is a version. It does not implement the comparison — the comparison is SemVer's, published once, and any implementation that reproduces it is correct by definition. This is the whole point of wrapping: the wrapped standard stays authoritative, and Variorum never grows a second, subtly different SemVer implementation.

## 90.10 A worked record

[`examples/instruisto-guide-owasp/`](../../examples/instruisto-guide-owasp/) describes the 49-page guide PDF of the `owasp-api-security` course, released by the `instruisto` project under the tag `owasp-api-security/v1.3.1`. The project already used SemVer, kept its tag, and added a record:

```json
"scheme": {
  "name": "semver",
  "version": "1.3.1",
  "authority": "https://semver.org/spec/v2.0.0.html"
},
"extensions": {
  "variorum:conformance": ["core", "recipe"],
  "variorum:semver": { "tag": "owasp-api-security/v1.3.1" }
}
```

Three things are worth noticing. The version is `1.3.1`, not `v1.3.1` and not the whole tag. The tag is kept verbatim, because stripping it would lose the course name a reader needs. And the digest in that record is of the released bytes — the PDF from the release, 637,290 of them — not of a rebuild.

## 90.11 Conformance

- Every rule here is exercised by `spec/vectors/semver.json`; each vector names `"bridge": "variorum:semver"` (`CON-28`).
- An implementation that claims the SemVer bridge MUST pass those vectors. An implementation that does not claim it skips them and remains conformant at its declared level (`CON-9`).
- No rule here changes what a record with `scheme.name: "semver"` and no claim means. Such a record is still core-conformant, and its version is still opaque.

## 90.12 What this bridge does not do

- It does not verify that a release exists, that a registry accepted it, or that the tag names the same commit.
- It does not define ranges, resolutions or dependency constraints; those belong to package managers.
- It does not order artifacts. Precedence orders *versions*; identity, lineage and state order artifacts.
- It does not replace `attestation`. A bridge sharpens a claim; a signature establishes who made it.
