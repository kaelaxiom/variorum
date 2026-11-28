# Case study — `software-tools`

The first project to adopt Variorum is one that does not build the artifacts it publishes: a private archive of software, curated by hand since 1991 and served by a small PHP site. It adopted `core` for one artifact, and the reason it recorded only one is the most instructive part of the story.

Everything below is in the adopter's repository: [cazucito/software-tools](https://github.com/cazucito/software-tools), commit [`e0a739f`](https://github.com/cazucito/software-tools/commit/e0a739f).

## The project

`software-tools` is a personal archive of the software its owner has actually used, from 1991 to today: 58 fichas (one Markdown page per tool, with the year, context and successors), a PHP 8.1 + SQLite site at <https://software-tools.pcabrera.com> whose home is a mind map, and a downloads catalogue of 91 rows in its last exported inventory — some pointing at the vendor's own site, some hosted by the archive itself behind a single general password.

Its downloads are the interesting case. An archive is not a release pipeline: it publishes other people's binaries, sometimes decades after those vendors disappeared. Which exact bytes is this? Which label does the archive give them? Those are the two questions `core` answers, and they are the only two the archive can answer without reconstructing history it does not have.

## What was adopted

- The class: `core`, declared in the record's `extensions["variorum:conformance"]`.
- The record: one, at [`ops/records/fc0cadf23dc1.variorum.json`](https://github.com/cazucito/software-tools/blob/main/ops/records/fc0cadf23dc1.variorum.json).
- The tooling: [`ops/tools/variorum_record.py`](https://github.com/cazucito/software-tools/blob/main/ops/tools/variorum_record.py), 218 lines of Python standard library, with two commands — `stamp` writes a record for a file, `check` recomputes the digest and size and fails when the record stops describing the bytes. No dependencies, no service, no change to the site's build or deploy.

The tool has no option that accepts a digest. That omission is the design: a digest can only enter a record from the file.

## Why one record and not ninety-one

The archive's admin panel already stores a `sha256` for every hosted file, written by whatever process uploaded it. Ninety-one values were therefore sitting in the database, each one a valid digest of a real artifact, and every one of them was unusable as evidence.

Copying them would have produced records that are *numerically right* in the ordinary case — the same bytes, the same algorithm — and evidentially empty: a record that repeats the database inherits the database's staleness and cannot detect it. It is the same refusal [ADR-0013](../adr/ADR-0013-spdx-bridge-points-at-the-sbom.md) makes for a foreign checksum, applied to the producer's own database, and the archive wrote the rule down in its own words: *el digest se calcula, nunca se copia*.

So the first record went to the one artifact that could be hashed from the bytes. The three steps, as the probe ran them (the probe used Python's `hashlib`; `sha256sum` prints the same line):

```bash
# 1. unlock the private collection (the general password read from Bitwarden Secrets Manager)
POST https://software-tools.pcabrera.com/download/gel      # → 200, sets the session cookie
# 2. fetch the file the site actually serves
GET  https://software-tools.pcabrera.com/download/gel/Gel86a.zip
#     200, Content-Length: 2520484
# 3. hash the bytes
sha256sum Gel86a.zip
#     fc0cadf23dc1473236ccedf27aa3f7f61e2415088ddddaa8262e8c0415c812ad
```

`unzip -t` reported no errors, so the download was not a truncated stream. The digest then matched, character for character, the value the panel held for that row: `fc0cadf23dc1…`. The record does not repeat the panel's claim — the panel's claim turned out to be true, and the record is the separate file that shows it.

The other ninety rows stay unrecorded until each one is fetched back and hashed the same way. That is the archive's adoption plan, stated in [`docs/variorum.md`](https://github.com/cazucito/software-tools/blob/main/docs/variorum.md), and it is a legitimate end state, not a pending chore: a project adopts a class per artifact, and a record that exists is worth more than ninety that assert.

## The record

```json
{
  "variorum": "0.1",
  "id": "urn:variorum:sha256:fc0cadf23dc1473236ccedf27aa3f7f61e2415088ddddaa8262e8c0415c812ad",
  "artifact": {
    "digest": "sha256:fc0cadf23dc1473236ccedf27aa3f7f61e2415088ddddaa8262e8c0415c812ad",
    "size": 2520484,
    "mediaType": "application/zip",
    "name": "Gel86a.zip"
  },
  "scheme": {
    "name": "custom",
    "version": "8.6",
    "authority": "https://github.com/cazucito/software-tools/blob/main/docs/adr/011-descargas-coleccion-privada.md"
  },
  "created": "2026-11-25T17:35:20-06:00",
  "producer": {
    "name": "software-tools",
    "kind": "software",
    "software": {
      "name": "ops/tools/variorum_record.py",
      "version": "1.0.0"
    }
  },
  "extensions": {
    "variorum:conformance": ["core"]
  }
}
```

## Three decisions the format left to the adopter

**The version is `8.6`, and the artifact is called `Gel86a.zip`.** The archive's own taxonomy ([ADR-011](https://github.com/cazucito/software-tools/blob/main/docs/adr/011-descargas-coleccion-privada.md)) separates four axes — work, version, variant, era — plus a year. It calls the version `8.6` and the variant *Gel 8.6a (instalador final)*. The record carries the version axis byte for byte (`SCH-7`); the finer label survives in the filename and the ficha. Adoption did not get to overrule the adopter's taxonomy, and a reader who wants the variant finds it where the archive always kept it.

**`authority` points at a document that exists.** `custom` is defined by project documentation, so the record names the document: the ADR that defines the archive's label axes and their global order. It would have been easy to write `https://software-tools.pcabrera.com` here; that URL is the site, not the definition of a scheme, and pointing at it would have made `SCH-4` a decoration.

**`producer` is the archive, not the vendor.** The binary was written by GExperts in 2002 and survives through the Internet Archive's Tucows collection; none of that is in `producer`, because `producer` is *the actor that created the record* (00-overview §4). The provenance lives in the ficha, which is the archive's own instrument for it. Getting this backwards is the first mistake a curator makes — and it is worth saying plainly: naming the vendor as `producer` would claim that whoever made the binary also wrote this JSON file, which nobody would believe about a 2002 installer and which is no truer for a modern one.

## What a consumer can check

```bash
# the format, with the reference implementation (run in a checkout of this repository)
python3 tools/variorum.py validate ops/records/fc0cadf23dc1.variorum.json --artifact Gel86a.zip
# OK — record conforms to Variorum 0.1 (core)

# the bytes, with the adopter's own tool
python3 ops/tools/variorum_record.py check ops/records/fc0cadf23dc1.variorum.json --artifact Gel86a.zip
# OK    ops/records/fc0cadf23dc1.variorum.json: digest y tamaño del archivo
```

Both commands were run before the commit. `check` was also run against a different file, and returned `1` with the two differing digests, which is the only way to know a comparison actually compares.

Nothing here needs the network, the site's password or the archive's database. The record is metadata about bytes, and it is as public as the repository it lives in.

## What adoption did not include

- **`state`.** The archive has no dated record of when each file was registered, approved or published. `STA-7` allows only the two premises — `draft` or `candidate` — on an empty transition list, and neither is true of a file that has been served for years; the honest answer was to omit the member (`STA-15`).
- **`recipe`.** The archive does not produce these binaries. A `kind: "manual"` recipe saying "downloaded from the Internet Archive" would describe the archivist's action, not the artifact's production — and the format's `recipe` is about the latter.
- **`lineage`.** The fichas have successors (GEL → NetBeans), but a successor in a personal timeline is not a derivation of bytes. `lineage` links artifacts, and these are distinct works.
- **Shipping the record next to the download.** The natural home for a record is beside the artifact (`CORE-12`); serving `downloads/gel/Gel86a.zip.variorum.json` would mean changing the streamer and the admin panel. That is a change to live code in a production site, so it is a decision for the owner, not for the agent that adopted the format. Until then the record is published with the repository.

## What it cost

Three new files, two index lines and one tool. The site's build (`import_catalog.py`), its deploy path and its PHP were not touched, and the archive's e2e suite counts fichas, sitemap entries and bundle contents — none of which changed, because none of them are in `ops/`. That is the whole point of a sidecar: the record is additive (invariant 3), and a project can adopt it on a Tuesday afternoon without a migration.

## What this case study says about the standard

- **"Do not copy a digest" is the rule adoption tests first.** The standard states identity as a computed digest (`ID-2`, `ID-5`) and warns about staleness; a real archive with ninety-one stored hashes is where that stops being advice. The `docs/adoption.md` guide now links here for the case where the artifact is not yours.
- **`producer` needs its one-line definition in front of adopters.** The glossary is unambiguous, but the field name reads like "who made this artifact" to anyone who is not implementing the spec. This case study is the argument for keeping that sentence where a curator will see it.
- **A curator's `scheme.version` may legitimately be coarser than the artifact's name.** The archive's taxonomy decides what the version is; the format must not try to refine it, and `SCH-7` already forbids a consumer from doing so.
