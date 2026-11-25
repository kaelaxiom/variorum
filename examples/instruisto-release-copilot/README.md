# Example — instruisto, release `github-copilot-agents/v1.1.0`

The adoption path, performed rather than described: one real release, two assets, two records, core class only.

- Release: [`github-copilot-agents/v1.1.0`](https://github.com/cazucito/instruisto/releases/tag/github-copilot-agents/v1.1.0), published 2026-10-08
- Assets: `proposal.pdf` (73,506 B) and `syllabus.pdf` (148,743 B), both `application/pdf`
- Scheme: `semver` with version `1.1.0`, the label the release carries
- No lineage, no recipe, no state, no bridge claim

Both records were produced by `variorum stamp` and then hand-edited in exactly one place: the `extensions["variorum:conformance"]` declaration (`CORE-7`), which `stamp` does not write. Nothing else was touched, so the digests, sizes, names and timestamps are the tool's own output.

| Record | Artifact | Digest prefix | Size |
|---|---|---|---|
| [`2605defcf2a7.variorum.json`](2605defcf2a7.variorum.json) | `proposal.pdf` | `2605defcf2a7` | 73,506 B |
| [`60d62fe0bbe7.variorum.json`](60d62fe0bbe7.variorum.json) | `syllabus.pdf` | `60d62fe0bbe7` | 148,743 B |

## How the two artifacts were identified

The release assets were downloaded from GitHub and their sizes checked against the release API before hashing:

```bash
gh release download github-copilot-agents/v1.1.0 -R cazucito/instruisto -p '*.pdf' -D .
sha256sum proposal.pdf syllabus.pdf
```

`gh release download` was used rather than the public asset URL because the repository is private: the URL returns a nine-byte `Not Found` body, which is exactly the kind of thing that would have become a digest if the size had not been checked against the API first. That is pitfall 2 in [`docs/adoption.md`](../../docs/adoption.md), met while following the guide.

## What this example demonstrates

- **One artifact, one record** (`ID-9`). A release is not an artifact. Publishing two files under one tag means two records, both carrying `1.1.0`, differing in digest and name.
- **The core class as the whole adoption** — five required members and a declaration. Nothing here needs a build system, a registry, a signature or a service.
- **A version wrapped, not invented** — `1.1.0` is the release's own label. The tag is `github-copilot-agents/v1.1.0`, and a tag is not a version: recording it is the SemVer bridge's job (`SEM-5`), deliberately not done here, because this directory shows the minimum. The worked version of that step is [`../instruisto-guide-owasp/`](../instruisto-guide-owasp/).
- **`stamp` as the reference path.** The command computes the digest from the bytes; nobody types a hash.

## Verify

```bash
for record in examples/instruisto-release-copilot/*.variorum.json; do
  python3 tools/variorum.py validate "$record" || exit 1
done
```
