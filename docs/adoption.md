# Adopting Variorum

Variorum asks a project for one thing: for each artifact it ships, a small JSON file that says *which exact bytes this is* and *what the project calls it*. The required members fit on a screen, the file sits beside the artifact, and no build system, registry, service or dependency is involved.

This guide walks the `core` path on a real release — `instruisto`'s [`github-copilot-agents/v1.1.0`](https://github.com/cazucito/instruisto/releases/tag/github-copilot-agents/v1.1.0) — and every command below was run to produce the records in [`examples/instruisto-release-copilot/`](../examples/instruisto-release-copilot/). Nothing here is a summary written afterwards: it is the path that was followed.

## 1. What `core` requires

| Member | Carries |
|---|---|
| `variorum` | the record format version, `"0.1"` |
| `id` | `urn:variorum:sha256:` followed by the digest — derived, never chosen (`ID-7`, `ID-8`) |
| `artifact` | `digest`, and the descriptive `size`, `mediaType`, `name` — only `digest` is required (`ID-2`) |
| `scheme` | the version scheme the project **already uses**, and its label |
| `created` | when the record was written, RFC 3339 with an explicit offset (`CORE-5`, `CORE-6`) |

`producer` and `extensions` are optional. So are `lineage`, `recipe`, `state` and `attestation` — those are separate classes, adopted later or never ([00-overview.md](../spec/00-overview.md) §5).

## 2. Stamp the artifact

```bash
gh release download github-copilot-agents/v1.1.0 -R cazucito/instruisto -p '*.pdf' -D .
python3 tools/variorum.py stamp syllabus.pdf \
  --scheme semver 1.1.0 \
  --media-type application/pdf \
  --producer cazucito \
  -o 60d62fe0bbe7.variorum.json
```

```
60d62fe0bbe7.variorum.json
```

```json
{
  "variorum": "0.1",
  "id": "urn:variorum:sha256:60d62fe0bbe732bcd1712902d3dcaba5bfa046d622c04d2dda9682ee96517a0f",
  "artifact": {
    "digest": "sha256:60d62fe0bbe732bcd1712902d3dcaba5bfa046d622c04d2dda9682ee96517a0f",
    "size": 148743,
    "mediaType": "application/pdf",
    "name": "syllabus.pdf"
  },
  "scheme": { "name": "semver", "version": "1.1.0" },
  "created": "2026-11-25T05:21:26-06:00",
  "producer": { "name": "cazucito", "kind": "human" }
}
```

`stamp` computes the digest from the bytes; the number in the file is never typed by a person. Omit `--scheme` entirely when the artifact has no version label and the tool writes `{"name": "none"}` — a legitimate answer, not a placeholder (`SCH-3`).

If you would rather not run the tool, the same record is four commands away — `sha256sum`, `stat -c %s`, `file --mime-type`, and an editor. What matters is that the digest comes from the file:

```bash
sha256sum syllabus.pdf
```

## 3. Declare what you satisfy

`stamp` writes the five required members, fills `artifact`'s descriptive members, and adds `producer` when it is given one — but it never writes a conformance declaration, and it never invents a `lineage`, `recipe` or `state`. Add the declaration yourself, because it is a claim about your implementation, not about this artifact (`CORE-7`):

```json
"extensions": { "variorum:conformance": ["core"] }
```

That is the only hand edit in the two records this guide produced, and it is the one thing an adopter should not let a tool guess.

## 4. Validate

```bash
python3 tools/variorum.py validate 60d62fe0bbe7.variorum.json
```

```
OK — record conforms to Variorum 0.1 (core)
```

```bash
python3 tools/variorum.py show 60d62fe0bbe7.variorum.json
```

```
id        urn:variorum:sha256:60d62fe0bbe732bcd1712902d3dcaba5bfa046d622c04d2dda9682ee96517a0f
artifact  syllabus.pdf  148743 bytes  application/pdf
scheme    semver 1.1.0
created   2026-11-25T05:21:26-06:00
```

Validation is offline and deterministic: the record is JSON, the rules are in `spec/`, and a warning is not a failure (a violated SHOULD is never a rejection — [ADR-0005](adr/ADR-0005-should-violations-are-warnings.md)).

## 5. One artifact, one record

The release has two assets, so it gets two records — not one record listing two files (`ID-9`):

| Record | Artifact | Size |
|---|---|---|
| [`2605defcf2a7.variorum.json`](../examples/instruisto-release-copilot/2605defcf2a7.variorum.json) | `proposal.pdf` | 73,506 B |
| [`60d62fe0bbe7.variorum.json`](../examples/instruisto-release-copilot/60d62fe0bbe7.variorum.json) | `syllabus.pdf` | 148,743 B |

Both carry `1.1.0`, because both shipped under that tag. A release is a publishing event; an artifact is a sequence of bytes. The record describes the second, and a release with ten assets has ten of them.

To say that two artifacts belong together, use `lineage` — that is what the graph is for, and it is a later class.

## 6. Where the file goes, and what it is called

- **Beside the artifact, never inside it** (`CORE-15`). A record embedded in the artifact changes its bytes, so the digest it carries would describe a file that no longer exists.
- **`variorum.json`** when the record sits next to the single artifact it describes — which is `stamp`'s default.
- **`<digest-prefix>.variorum.json`** when several records share one directory, where the prefix is the first 12 hex characters of the digest (`CORE-13`).
- **Ship it with the release.** Commit it, attach it, put it next to the download. A record is public metadata about public bytes; if it has to be kept secret, it is the wrong file.

## 7. The version is the project's label, not Variorum's

`scheme.name` says which scheme the label belongs to and `scheme.version` is that label, byte for byte (`SCH-7`). Adopting Variorum never renumbers anything (invariant 3): the release above is `1.1.0` because the project already called it that.

Two consequences:

- **Do not "fix" the label.** `1.1.0` is not `v1.1.0`, and `1.1.0-rc.1` is not `1.1.0`. A consumer treats the string as opaque, and a producer must not depend on it being parsed.
- **A tag is not a version.** This release's tag is `github-copilot-agents/v1.1.0` — a monorepo prefix, which no scheme defines. The version is `1.1.0`; recording the tag is the SemVer bridge's job, one opt-in key ([`90-extensions/semver.md`](../spec/90-extensions/semver.md), `SEM-5`), worked end to end in [`examples/instruisto-guide-owasp/`](../examples/instruisto-guide-owasp/). The records in this guide deliberately stop short of it, so the core path stays five members.

## 8. Seven ways to get it wrong

1. **Hashing what you built instead of what you shipped.** A source tree is not a release; `git archive` output is not reproducible byte-for-byte across git versions, and GitHub's auto-generated `Source code (tar.gz)` is regenerated rather than stored. Hash the file you uploaded.
2. **Hashing a failed download.** While writing this guide, the public asset URL returned a nine-byte `Not Found` body because the repository is private. Check the size against an independent record before you trust a digest — nine bytes are a valid hash of something.
3. **Putting the record inside the artifact.** See §6: the digest and the container contradict each other the moment the record is embedded (`CORE-15`).
4. **Expecting a re-encode to keep the digest.** Re-saving, re-muxing or recompressing produces different bytes for the same content (`ID-15`). That is a new artifact and a new record, joined to the old one by `transcode` (`ID-16`).
5. **Writing a digest by hand.** A digest copied into a template, a CI variable or a README goes stale silently and no validator can catch it, because the record still parses. Compute it from the file every time; if a build cannot, it should fail rather than reuse.
6. **Local time.** `created` without an offset is invalid, not merely ambiguous (`CORE-5`, `CORE-6`).
7. **Declaring a class you do not satisfy.** `"lineage"` in the declaration without a `lineage` member is a validation error (`CON-6`), which is the point: a declaration a consumer can trust has to be one that cannot be false.

## 9. What you can postpone

Conformance is graded (invariant 4), and partial adoption is legitimate and declarable:

- **`lineage`** — when an artifact derives from another and the relation is known. Not before: a guess is worse than silence.
- **`recipe`** — when a build or a generation can be described well enough to attempt reproduction.
- **`state`** — when the project has a lifecycle with real transitions and dates.
- **`attestation`** — when someone needs to verify *who* asserts the record.

A record that declares `["core"]` is not a lesser record. It is a record that answers one question exactly, and the specification would rather have it than a record full of reconstructed history.

## 10. Checking the claim

`variorum conform` runs the vector suite for the classes and bridges an implementation claims ([07-conformance.md](../spec/07-conformance.md)):

```bash
python3 tools/variorum.py conform --coverage
```

A consumer does not take `["core"]` on faith: it runs the same vectors against the implementation, then validates the records. What you write in `extensions["variorum:conformance"]` is a sentence someone can test.

## 11. What adoption does not require

- No renumbering of anything already released (invariant 3).
- No registry, domain or account: a record is a file, and `urn:variorum:` is derived, not registered.
- No signature, no timestamp authority, no service call at validation time.
- No dependency in your build: the reference tool is Python 3.11+ standard library only, and the format is JSON.
- No change to how you publish. The record is additive — wrap, do not replace (invariant 3).

If a step in this guide ever demands one of those, the guide is wrong, not your project.

## 12. When the artifact is not yours

An archive, a mirror or a museum publishes bytes it did not produce and cannot rebuild. The path is the same — `core`, one record per artifact, the digest computed from the file — with two differences worth knowing before you start:

- **A hash stored in your catalogue is a claim, not a source.** Copying it into a record produces a record that repeats your database and inherits its staleness, with no way to notice when the bytes and the value drift apart. Fetch the artifact back and hash it; if you cannot, leave the record unwritten.
- **`producer` is you, not the vendor.** It names the actor that created the record, never the author of the binary. Provenance belongs in whatever instrument your project already uses for it.

[`case-studies/software-tools.md`](case-studies/software-tools.md) walks the whole path on a real archive — 91 stored hashes, one record, and the reason the other ninety stayed unrecorded.

## Verify the example

```bash
for record in examples/instruisto-release-copilot/*.variorum.json; do
  python3 tools/variorum.py validate "$record" || exit 1
done
```
