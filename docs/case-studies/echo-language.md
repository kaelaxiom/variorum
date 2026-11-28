# Case study — `echo-language`

The first case study recorded an archive that publishes what it did not make; the second, a CAD repository that builds what it records with a declared toolchain. This one records something neither could: an artifact **produced by a model**, where re-running the recipe is impossible in principle, and where the provider has already signed a provenance manifest of its own.

Everything below is in the adopter's repository: [cazucito/echo-language](https://github.com/cazucito/echo-language), commit [`b8837a9`](https://github.com/cazucito/echo-language/commit/b8837a9).

## The project

Echo Language is a transmedia musical project built around **Avela**, a constructed language written to be sung. The repository is the project's canon: a lexicon of 124 validated words, grammar and phonology, a complete song specification, and a workflow that treats Suno Pro as the generation instrument. Its first release is *Liora*, catalogued as **Echo Archive 01** inside the project's fiction.

Two of its own rules make it the right third case:

- **Generated media does not enter git.** `assets/audio/**` and `*.mp3` are ignored; the project's `.gitignore` says so under "generated media (large binaries)". A format that requires the record to travel *with* the artifact has to answer for that.
- **The generation is not reproducible.** Suno offers no seed and no snapshot the project can request; the same prompt twice yields different audio. `determinism: "none"` is not a hedge here — it is the measured truth.

## The artifacts

Four discovery takes of one prompt, generated on 2026-08-05 in two batches:

| Take | Bytes | Duration | Digest (first 16) | Generated |
|---|---:|---:|---|---|
| `Liora-take-01.mp3` | 3,650,777 | 158.280 s | `94a5ba226ad217eb` | 2026-08-05T17:15:24Z |
| `Liora-take-02.mp3` | 3,548,907 | 152.880 s | `92abfb0746c9b29b` | 2026-08-05T17:15:24Z |
| `Liora-take-03.mp3` | 4,286,810 | 186.648 s | `c90c19771e34de91` | 2026-08-05T17:21:12Z |
| `Liora-take-04.mp3` | 4,097,358 | 178.128 s | `ba774da9a7e39159` | 2026-08-05T17:21:12Z |

They are siblings, not versions. The paragraph under `LIN-6` says it in one sentence — "three takes of the same prompt are three `revision` siblings with a common ancestor, not a chain" — and this batch is the first time the format's own example is a real directory.

## What was adopted

- **Four records**, one per take, committed beside the audio at `assets/audio/001-liora/takes/<digest-prefix>.variorum.json` (`CORE-13`: several artifacts in one directory). The audio stays out of git; a `.gitignore` exception admits `*.variorum.json`, because a sidecar is text and the bytes it describes are not.
- **A stamper**, [`tools/variorum-record/main.py`](https://github.com/cazucito/echo-language/blob/main/tools/variorum-record/main.py) — 531 lines of Python standard library (526 at the adoption commit; the two fixes came later, in [`2232272`](https://github.com/cazucito/echo-language/commit/2232272)). It parses the ID3v2.4 tag and the C2PA manifest store, and derives from the artifact what the artifact can answer. A claims file that states a `digest`, `id`, `size`, `manifest`, `model`, `generatedAt` or `content_id` is refused with exit 2.
- **The classes**: `core`, `lineage`, `recipe`, declared in `extensions["variorum:conformance"]`. `state` is not declared because it is not a class (`CON-3`), and it is also absent for a reason of its own — see below.

## The record

One of the four, verbatim — take 04, the longest of the second batch:

```json
{
  "variorum": "0.1",
  "id": "urn:variorum:sha256:ba774da9a7e39159be2a25bae86bf33517a34534c6b61e27fcfde3b05e170cdf",
  "artifact": {
    "digest": "sha256:ba774da9a7e39159be2a25bae86bf33517a34534c6b61e27fcfde3b05e170cdf",
    "size": 4097358,
    "mediaType": "audio/mpeg",
    "name": "Liora-take-04.mp3"
  },
  "scheme": {
    "name": "x-echo-archive",
    "version": "01",
    "authority": "https://github.com/cazucito/echo-language/blob/main/docs/lore/archive-system.md"
  },
  "created": "2026-11-26T05:57:47-06:00",
  "producer": {
    "name": "echo-language",
    "kind": "software",
    "software": {
      "name": "tools/variorum-record/main.py",
      "version": "1.0.0"
    }
  },
  "recipe": {
    "kind": "generative",
    "tool": {
      "name": "suno",
      "model": "chirp-fenix-t4"
    },
    "prompt": "[Intro]\nLiora… liora…\nAe, liora.\n\n[Verse 1]\nAvela eka en mi,\nnave sora, vere stela.\nSilei en mi,\nsilei en te.\n\n[Pre-chorus]\nAe, lumia —\nsava en tena,\nsava en mi.\n\n[Chorus]\nLiora, liora!\nNae lumia, nae liora.\nLiora, liora!\nTea eko sava en mi.\nKa te rema?\nLiora, liora.\n\n[Verse 2]\nSiga nae sora,\nperda en vea.\nKasa en dorma,\ndora en mi.\nRemei na vera,\nforei na te.\n\n[Pre-chorus]\nAe, lumia —\nsava en tena,\nsava en mi.\n\n[Bridge]\nLumina, lumina,\nlumina en mare.\nEke voka, eke voka,\nkanta nae reva.\nKuna e espera,\nkuna e espera.\nRenova, renova!\n\n[Final Chorus]\nLiora, liora!\nNae lumia, nae liora.\nKa te rema? Ka te rema?\nLiora sava en mi.\n\n[Outro]\nAvela… avela…\nSilei en mi.\nLiora…",
    "parameters": {
      "styles": "Intimate ambient cinematic pop with ethereal electronic and neoclassical textures, 72-84 BPM. Androgynous gender-ambiguous close-mic lead, controlled fragility, soft consonants, pure vowels, audible but sparse breath, restrained late vibrato, whisper-to-full transitions, clear diction. Felt piano, warm pads, deep low pulse, restrained electronic percussion, layered harmonies; distant choir only in the bridge. Begin with the Liora hook over voice and piano within 15 seconds; verses stay sparse, chorus adds pulse and harmony, bridge delivers the only crescendo, final chorus surrenders, outro ends quiet, unresolved and loopable. Warm archival production, dark wide space, subtle tape texture, natural dynamics. Sing Avelian exactly as written with five pure vowels and penultimate stress.",
      "exclude_styles": "English lyrics, invented extra syllables, clearly masculine lead, clearly feminine lead, soprano, bass-baritone, childlike vocal, vocal runs, melisma, belting, operatic vibrato, constant breathiness, ASMR whispering, growls, shouting, glossy autotune, robotic doubling, bright commercial pop, EDM drops, trap hi-hats, rock guitars, epic trailer drums, full orchestra, generic fantasy choir, constant choir, busy percussion, supersaw synths, sidechain pumping, harsh treble, loud brickwall mastering, multiple crescendos, abrupt ending, generic fade-out, musical glitch effects",
      "title": "Liora",
      "vocal_gender": "neutral/unspecified",
      "instrumental": false,
      "voice": "none",
      "weirdness": 50,
      "style_influence": 80,
      "provider_content_id": "5d7c60de-1c42-4af3-83de-95f52ef811c2",
      "provider_url": "https://suno.com/song/5d7c60de-1c42-4af3-83de-95f52ef811c2"
    },
    "generatedAt": "2026-08-05T17:21:12Z",
    "determinism": "none"
  },
  "lineage": {
    "parents": [
      {
        "id": "urn:variorum:sha256:9581524a274775086f6b579ffc542e4e2079a0c27b9621b98109f1bfb3907caf",
        "relation": "generation"
      }
    ]
  },
  "extensions": {
    "variorum:conformance": [
      "core",
      "lineage",
      "recipe"
    ],
    "variorum:c2pa": {
      "manifest": "urn:c2pa:c450e94c-813a-4ed1-9f8c-ac2d5a15b91a",
      "location": "embedded"
    }
  }
}
```

## The two hashes, and why neither is the other

Suno writes a C2PA manifest store into each MP3, inside a `GEOB` ID3 frame. The store holds one manifest whose assertions say, among other things, that the asset was created by `trainedAlgorithmicMedia` on Suno's side, what its content id is, and what SHA-256 the asset has.

That hash is **not** the Variorum digest, and the difference is arithmetic, not disagreement. C2PA's `c2pa.hash.data` assertion hashes the asset with the manifest store excluded — for take 04, a 13,659-byte range starting at byte 18,915. Variorum hashes every byte of the file.

| File | Variorum digest (all bytes) | C2PA hard binding (manifest excluded) |
|---|---|---|
| `Liora-take-01.mp3` | `94a5ba22…` | verified |
| `Liora-take-02.mp3` | `92abfb07…` | verified |
| `Liora-take-03.mp3` | `c90c1977…` | verified |
| `Liora-take-04.mp3` | `ba774da9…` | `709d7fe7…` |

The adopter's `check` recomputes the binding for every take: SHA-256 over the bytes outside the exclusion range reproduces the stored value exactly in all four. Both numbers are correct. A record that copied the C2PA hash into `artifact.digest` would be *numerically plausible and evidentially false* — the mistake [ADR-0013](../../docs/adr/ADR-0013-spdx-bridge-points-at-the-sbom.md) warns about, seen from the content side.

This is the first artifact in the project that exercises the [`c2pa` bridge](../../spec/90-extensions/c2pa.md) against a manifest produced by someone else. The bridge's rule holds without modification: the record names the active manifest (`C2P-2`) and where it lives (`location: "embedded"`), and copies nothing out of it. The signature's trust chain is C2PA's question; the record does not authenticate what it did not sign.

## The model was in the bytes

`REC-7` requires a generative recipe's `tool` to carry a `model`. The project's own brief asks for "v5.5 (or current compatible production model)" — a target, not a fact, and the generation session was never logged. Guessing from it would have produced a record that says something nobody knows.

The answer was in the file. Suno's `com.suno.provenance` assertion carries:

```json
{"contentId": "5d7c60de-…", "createdAt": "2026-08-05T17:21:12Z", "providerName": "Suno, Inc.", "systemName": "Suno", "systemVersion": "chirp-fenix-t4"}
```

So the record carries `"model": "chirp-fenix-t4"` and `"generatedAt": "2026-08-05T17:21:12Z"`, both read from the provider's signed assertion rather than inferred. All four takes report the same system version and one of two creation instants.

This is also the limit of the method: a Suno take whose file predates the C2PA embedding, or one downloaded without it, has no model to read. The stamper refuses with exit 2 rather than fill the gap with the brief's aspiration. `REC-7`'s MUST is satisfiable only when the provider publishes the fact; a project that records a guess satisfies the letter and breaks `REC-20`.

## Three decisions the format left to the project

**The scheme is `x-echo-archive`.** The catalogue numbering is the project's invention, and `SCH-10` recommends the `x-` prefix for names outside the reserved table. The first stamped records said `echo-archive` and the validator emitted `SCH-10`; the warning was right, and the prefix costs nothing. (The reference CLI printed a warning, not an error — `SCH-2` accepts any lowercase name — which is the correct severity for a SHOULD.)

**The version label is `01`, and its authority is [`docs/lore/archive-system.md`](https://github.com/cazucito/echo-language/blob/main/docs/lore/archive-system.md),** the document that defines *Echo Archive NN*. Four takes of one song share one label, because the label names the release while the digest names the artifact — `SCH-7`'s opacity doing exactly the job it was written for. `authority` points at the definition, not at the repository URL (`SCH-4` would otherwise be satisfied by a page that defines nothing).

**`state` is absent, and that was the honest record when it was stamped.** The takes are complete generations; none has been compared, scored or chosen, and the project's workflow puts that decision after the batch. At stamping, `STA-7` allowed only `draft` with an empty transition list, and `draft` would have called a finished take work in progress; `candidate` describes them, but reaching it required a `draft → candidate` transition with an actor and a timestamp, and nobody made that decision. The record therefore omitted the member, which `STA-15` allows. [`ADR-0017`](../adr/ADR-0017-a-complete-artifact-is-born-a-candidate.md) closes the gap: `candidate` may be held with no transitions, so the same record can now carry `{ "current": "candidate", "transitions": [] }`, and the first decision — which take is chosen — becomes the first transition, starting from `candidate`.

## What adoption found

- **`SCH-10` works as a warning.** Adoption produced the one condition the recommendation exists for, and the fix was a prefix, not an argument.
- **`REC-9` assumed one prompt field, and the gap it found is closed.** Suno's Custom mode has six: lyrics, styles, exclude styles, title, vocal gender and three numeric controls. The record puts the lyric field — the text that produces words — in `recipe.prompt`, and the rest in `parameters` (`REC-11`). At stamping that was a defensible reading and not a defined one; `REC-9` now says the member holds, verbatim, the value of one field and never a synthesis, `REC-23` recommends naming it in `recipe.promptField`, and `REC-24` fixes that member's shape ([ADR-0016](../adr/ADR-0016-the-prompt-is-one-field-and-the-record-names-it.md)). The record predates the member: `"promptField": "lyrics"` is one edit in this repository, and the fields are already where the rule wants them.
- **The prompt is checkable against the artifact, up to the provider's transcription.** The lyric block in `songs/001-liora/suno-prompt.md` and the `USLT` frame Suno wrote back into the MP3 are equal once the eight blank lines between sections are removed — 667 characters in takes 02, 03 and 04. Take 01's frame holds 709: the provider repeats the final `[Outro]` section, so the tag is a transcription that can drift, not a copy. Read as evidence rather than treated as a checksum, it is still a stronger guarantee than most software recipes can offer, and it came free with the provider's tag.
- **The lifecycle vocabulary had no way to say "produced, undecided", and the fix was not a `generated` state.** A take that was produced but never chosen sat between `draft` (in progress) and `candidate` (awaiting a decision) with no transition to justify either. `STA-7` and `STA-9` now let a record hold either premise with no transitions — `draft` or `candidate` — and let the first transition start at either, so a batch is born a `candidate` and the first real decision lands directly on it ([ADR-0017](../adr/ADR-0017-a-complete-artifact-is-born-a-candidate.md)). A `generated` state was refused: that a model made the bytes is `recipe`'s and `producer`'s claim, and `state` records decisions, not provenance.
- **`REC-7` cannot be satisfied from a provider that stays silent.** Recorded here rather than patched: the standard says the model MUST be named, and a provider that publishes no model makes that MUST unsatisfiable for an honest producer.

## What a consumer can check

```bash
# the format, with the reference implementation (run in a checkout of this repository)
python3 tools/variorum.py validate assets/audio/001-liora/takes/ba774da9a7e3.variorum.json \
  --artifact assets/audio/001-liora/takes/Liora-take-04.mp3
# OK — record conforms to Variorum 0.1 (core, lineage, recipe)

# every fact the record claims, including the C2PA hard binding
python3 tools/variorum-record/main.py check \
  assets/audio/001-liora/takes/ba774da9a7e3.variorum.json \
  --artifact assets/audio/001-liora/takes/Liora-take-04.mp3 \
  --source songs/001-liora/lyrics.avelian.md
# OK    digest, size, manifest, model, generatedAt
# OK    lineage parent matches songs/001-liora/lyrics.avelian.md
```

The first command validates a record that ships in the adopter's repository; the second re-derives every value in it. Both were run before the adopter's commit, and the second also runs against a different take, where it fails and prints both digests.

## What adoption did not include

- **`attestation`.** The project never signs; Suno signs, and the record points at that signature rather than competing with it.
- **Records for the clips, covers and social graphics.** They do not exist yet. When they do, the same stamper handles any MP3 with these tags; images and video would need their own extractors, and none was written.
- **A reconstructed generation log.** `songs/001-liora/suno-settings.md` still says `pending`; its columns record what the UI showed during a session nobody wrote down. The sidecars now carry what the files can prove — creation time, system version, content id — and the log was left alone rather than filled from a guess.

## What it cost

Twelve files and 1,098 inserted lines on the adopter's side: one tool, one claims file, four records, one document, a README line and a `.gitignore` exception. The audio, the lyrics and the generation workflow were not touched.

Checking this document against the files found two defects in that tool, both fixed in a second commit ([`2232272`](https://github.com/cazucito/echo-language/commit/2232272), four files, 209 lines): the `USLT` decoder returned the frame's content descriptor instead of its text, so the lyrics of every take read as an empty string, and the claims guard printed its message but exited 1 where three documents promised 2. Neither defect could reach a record — the lyrics are not recorded and the guard fires before a record is written — but both were found only by reading the tool's output rather than its exit status, which is the argument for the thirteen tests the fix added. The records and the audio were not touched by either change.

## What this case study says about the standard

- **A generative recipe is worth recording precisely because it cannot be re-executed.** The useful members are the ones that came from the provider's own assertion — model, timestamp, content id — not the parameters a human retyped.
- **A sidecar's portability is not a slogan.** Four 4 MB files cannot enter a repository that forbids generated media; four 4 KB records can, and they point at the artifacts by the only identifier those artifacts cannot change without becoming different artifacts.
- **Two correct hashes over one file is the normal case, not an edge case.** C2PA hashes around its manifest; Variorum hashes the bytes. The bridges are useful only if they refuse to blur that, and this is the first real artifact where the temptation existed.
- **A warning is a finding.** `SCH-10` fired on the first stamped record and the adopter changed its own name to obey it. A standard whose only feedback is pass/fail teaches nothing.

## The records in this repository's tests

`CaseStudyIndexTests` requires every file in this directory to have a row in [the index](README.md). The adopter's four records are validated there, not here: `examples/` holds records this project ships, and a case study holds records someone else ships.
