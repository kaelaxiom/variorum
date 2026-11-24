# Example — instruisto, OWASP API Security guide

A course guide PDF from a project that already used SemVer, wrapped without renumbering anything.

- Artifact: `guide.pdf`, 49-page PDF, 637,290 bytes
- Project: `instruisto` (`github.com/cazucito/instruisto`)
- Release tag: `owasp-api-security/v1.3.1`, at commit `1360025`
- Scheme: `semver:1.3.1`, with `extensions["variorum:semver"].tag` carrying the tag as published

## What this example demonstrates

- **Wrapping without renumbering.** The project released `1.3.1` before Variorum existed. The record references that label and leaves the tag, the changelog and the release alone (P3, invariant 3).
- **The tag is not the version.** The tag is `owasp-api-security/v1.3.1`: a monorepo prefix plus a `v`. The version is `1.3.1`. `SEM-5` keeps the tag verbatim next to the version instead of pretending either is the other.
- **A build recipe read from the artifact.** The toolchain version (`typst 0.15.1`) and the build timestamp come from the PDF's own metadata (`Creator: Typst 0.15.1`, `CreationDate: 2026-10-08 12:34:32 -06:00`), not from a guess about the CI runner. `determinism: "none"` is deliberate: the workflow installs Typst through `setup-typst@v4`, which does not pin a version, and Typst embeds a creation date — a byte-identical rebuild is not claimed because it was not verified (`REC-13`).
- **A retroactive record with no `state`.** The release exists and is public, but nobody recorded a `draft → candidate → approved` chain. `STA-15` says a record without `state` has no declared lifecycle, which is more honest than inventing approvals that never happened.

## Verify

```bash
variorum validate examples/instruisto-guide-owasp/c40d573a4bbd.variorum.json
variorum show     examples/instruisto-guide-owasp/c40d573a4bbd.variorum.json
```

To check the digest against the released bytes:

```bash
gh release download owasp-api-security/v1.3.1 -R cazucito/instruisto -p guide.pdf -D .
sha256sum guide.pdf   # c40d573a4bbdfa17cdb6d5619c129868f753a46a82e87a3fa24adeb1fbcc1f6a
```

The tag contains a slash, so a hand-built `…/releases/download/<tag>/guide.pdf` URL is ambiguous; `gh release download` resolves it. That is a property of the tag, not of the record — which is exactly why the record stores the tag as data.
