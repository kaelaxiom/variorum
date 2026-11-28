# Case study — `3d-printerator`

The first case study was a project that publishes artifacts it did not make. This one builds what it records: a repository of 3D-printing solutions where the STL is the output of a parametric text source and an OpenSCAD build, and where the design that mattered most was the one nobody printed.

Everything below is in the adopter's repository: [cazucito/3d-printerator](https://github.com/cazucito/3d-printerator), commit [`faa987c`](https://github.com/cazucito/3d-printerator/commit/faa987c).

## The project

`3d-printerator` is a personal repository of 3D-print solutions for problems that actually happened. Two designs live in it: a thermal spacer for a Mac Mini and a two-watch wrist case. The machine is an ANYCUBIC Photon Mono 4K (SLA resin), and the repository's own rules ask for parametric OpenSCAD 2021.01, every dimension named at the top of the `.scad`, and one folder per iteration — `designs/<solution>/vN/` holding the source, previews and binary STLs.

That layout is why the second case study is this one. A CAD repository knows exactly how its artifacts are made — a text source and a toolchain — and it also knows when one of them was abandoned. The archive could only answer *which bytes*; this project can answer *how they were produced* and *what was decided about them*.

## The artifact

`designs/aw9-d2strap-case/v2/aw9-d2strap-case-v2-holder.stl` — 374,684 B, `model/stl`, `sha256:cf3a7707…`.

The problem: the owner wears an Apple Watch S9 45 mm on the left wrist, rotated 180° so the crown faces the elbow, and a Huawei Watch D2 on the right of the same wrist, each on its own strap. The cases knock against each other. v1 was a holder with lugs for the D2 strap; v2 became a single rigid separator — two cradles and a bridge — with each watch keeping its own strap and the crowns exposed through the outer wall (`SPEC R6`).

The record describes the complete v2 holder. The folder holds three STLs (the holder and two fit tests) plus the `.scad`; v1 holds three more. One of those seven files has a record, and it is the one that reached a decision.

## What was adopted

- The classes: `core`, `lineage`, `recipe` — declared in `extensions["variorum:conformance"]`. `state` is not declared because it is not a class: when the member is present it belongs to `core` (`CON-3`).
- The record: [`designs/aw9-d2strap-case/v2/cf3a7707ccdb.variorum.json`](https://github.com/cazucito/3d-printerator/blob/main/designs/aw9-d2strap-case/v2/cf3a7707ccdb.variorum.json), beside the artifact it describes, named by the first twelve hex digits of its digest (`CORE-13`). A bare `variorum.json` would not say which of the three STLs in that folder it describes.
- The tooling: [`tools/variorum_record.py`](https://github.com/cazucito/3d-printerator/blob/main/tools/variorum_record.py), 290 lines of Python standard library. `stamp` computes the artifact's digest and size and the `--source` file's digest, writing the second into both `recipe.source` and `lineage.parents`; everything a tool cannot invent — scheme, recipe, state, declaration — comes from a claims file. `check` recomputes both digests and the size.

As in `software-tools`, there is no option that accepts a digest. Here the guard goes one step further, because this record has two digests in it: a claims file that tries to state a `digest` or an `id` is rejected with exit code 2. Both numbers in this record came from `hashlib`.

## The record

```json
{
  "variorum": "0.1",
  "id": "urn:variorum:sha256:cf3a7707ccdb99bcf87dc425cb818234cbf8ee6ca55713867928697a4f5c271c",
  "artifact": {
    "digest": "sha256:cf3a7707ccdb99bcf87dc425cb818234cbf8ee6ca55713867928697a4f5c271c",
    "size": 374684,
    "mediaType": "model/stl",
    "name": "aw9-d2strap-case-v2-holder.stl"
  },
  "scheme": {
    "name": "custom",
    "version": "v2",
    "authority": "https://github.com/cazucito/3d-printerator/blob/main/docs/workflow.md"
  },
  "created": "2026-11-25T23:47:00-06:00",
  "producer": {
    "name": "3d-printerator",
    "kind": "software",
    "software": { "name": "tools/variorum_record.py", "version": "1.0.0" }
  },
  "recipe": {
    "kind": "build",
    "tool": [ { "name": "openscad", "version": "2021.01" } ],
    "parameters": { "part": "holder", "export_format": "binstl" },
    "source": { "digest": "sha256:916c01f5c11c6e827f2e17ed9576fabfcf7fc5d41088c831a0717903f9048634" }
  },
  "lineage": {
    "parents": [
      {
        "id": "urn:variorum:sha256:916c01f5c11c6e827f2e17ed9576fabfcf7fc5d41088c831a0717903f9048634",
        "relation": "render"
      }
    ]
  },
  "state": {
    "current": "rejected",
    "transitions": [
      {
        "from": "draft",
        "to": "candidate",
        "actor": { "name": "claude-code", "kind": "software", "software": { "name": "claude-code" } },
        "at": "2026-09-29T05:28:00-06:00"
      },
      {
        "from": "candidate",
        "to": "rejected",
        "actor": { "name": "cazucito", "kind": "human" },
        "at": "2026-10-01T23:39:13-06:00",
        "reason": "No printed part: a bought TPU bumper (Hontao Slim, 45 mm) mirrors the D2's case, so the aluminium watch strikes bumper against bumper and the design was set aside."
      }
    ]
  },
  "extensions": {
    "variorum:conformance": ["core", "lineage", "recipe"]
  }
}
```

## Three decisions the format left to the project

**The label is `v2`, which is what the tree calls it.** The documentation commit `8a2a73e` called the final concept *v3*; the implementation landed as `v2/`, and `v2` is the label the artifact lives under. `SCH-7` makes the label opaque precisely so that adoption does not get to correct the adopter: the record carries `v2`, not `2`, and not `v3`.

**`authority` points at `docs/workflow.md`,** the document that defines `designs/<solution>/vN/` as iterations under version control. Pointing at the repository URL would have satisfied the shape of `SCH-4` while defining nothing.

**`producer` is the project, not the agent that modelled the part.** `producer` names the actor that created the record (`00-overview` §4); here that is `tools/variorum_record.py`. The modelling agent appears one member later, where it belongs: as the actor of a lifecycle transition.

## The measurement that removed `determinism`

A build recipe invites a question the format refuses to let a producer guess at: does re-running it produce the same artifact? The answer here is no, and it was measured rather than assumed.

`openscad --export-format binstl -D 'part="holder"' aw9-d2strap-case-v2.scad` was run twice on the machine that validated this case study, both times with OpenSCAD 2021.01. The committed STL and the two rebuilds contain **the same 7,492 triangles, exactly** — same vertices, same normals, same attribute words, same 84-byte binary STL header, same bounding box — and **three different SHA-256 digests**, because the facet order differs between them. The multiset of triangles is identical; the serialisation is not.

Consequences, in the format's own terms:

- Under `P1`, those are three artifacts, not one. The identity is the bytes.
- `determinism: "full"` is unavailable: `REC-13` forbids it unless a re-execution has been verified to produce the identical digest, and it does not.
- `determinism: "none"` would be wrong in the other direction: the recipe determines the geometry completely.
- So the member is absent, and the absence is the honest statement: *this recipe determines the shape, not the bytes.*

No value in the `REC-12` this record was stamped against covered that case. The gap it recorded as open was closed in the draft by [`ADR-0015`](../adr/ADR-0015-a-recipe-can-determine-the-content-not-the-bytes.md): `determinism: "content"` names exactly this — the same content under a stated normalization, not necessarily the same bytes — and `REC-13` now requires a verified re-execution for that claim as it already did for `full`. The record still omits the member because it was stamped before the grade existed; adding it, together with `parameters.normalization`, is one edit the adopter can make from the same measurement.

The same fact is why `lineage` matters more here than in a software release. The artifact is one serialisation of a design; the design is recovered by following the `render` edge back to the `.scad`, whose digest the record also carries. A consumer can hash the source and check the parent without any registry. The source has no record of its own — `LIN-8` allows that, and `LIN-9` is the rule that keeps the claim honest: this lineage is not complete, it ends at a source that has an identity but no record.

## State: an artifact that lost

The v2 model was committed as the version to print (`a46501b`, 2026-09-29), after the owner's review of the first v2 rejected blind control grooves and `SPEC R6` demanded operable crowns and buttons. Two days later the owner decided against printing it at all and bought a TPU bumper for the Apple Watch instead (`9312e40`, 2026-10-01). The design stays in the repository as a discarded iteration; the record says so in a machine-readable way.

- **`at` is the commit timestamp**, not a reconstructed hour. The project has no decision log apart from git, and a record that invents a time is worse than one that cites the moment the decision became part of the history.
- **The first transition names `claude-code`,** the coding agent this repository's `CLAUDE.md` addresses. The commits carry the owner's git identity, so a reader who wants proof of *who* did what needs `attestation` — which was not adopted, and the record does not pretend otherwise.
- **`rejected` is terminal** (`STA-11`): a later attempt is a new artifact joined to this one by `revision`. For a CAD project that is not a legal technicality — a re-export is a different file by construction, as the measurement above shows. The rule and the toolchain agree.

## What adoption found in the standard

Two defects, both found by using the format rather than reading it:

- **`show` printed `recipe build via ?`** for this record. `recipe.tool` may be a single object or an array (`REC-5`, and the schema types it as `oneOf`); the command only handled the object. Fixed in the reference CLI 0.6.1, with `ShowTests` pinning both shapes.
- **The adoption guide called `state` a separate conformance class** in §1. It is not: `CON-3` puts it inside `core` whenever the member is present, which is why this record declares three classes and carries four sections. The guide was corrected; a reader who trusted it would have declared a class that `CON-5` does not allow.

Adoption is a test of the guide, not only of the adopter.

## What a consumer can check

```bash
# the record against its own files: artifact digest, size, source digest, parent id
python3 tools/variorum_record.py check \
  designs/aw9-d2strap-case/v2/cf3a7707ccdb.variorum.json \
  --artifact designs/aw9-d2strap-case/v2/aw9-d2strap-case-v2-holder.stl \
  --source   designs/aw9-d2strap-case/v2/aw9-d2strap-case-v2.scad
# OK    …: digest and size of the artifact, digest of the source

# the format, with the reference implementation (run in a checkout of this repository)
python3 tools/variorum.py validate \
  designs/aw9-d2strap-case/v2/cf3a7707ccdb.variorum.json \
  --artifact designs/aw9-d2strap-case/v2/aw9-d2strap-case-v2-holder.stl
# OK — record conforms to Variorum 0.1 (core, lineage, recipe)
```

Both were run before the commit, and `check` was also run against a different STL and a different `.scad`: it returned `1` with both digests on screen, which is the only evidence that a comparison compares.

## What adoption did not include

- **`attestation`.** No keys, no signature. The record is public and verifiable, not signed — and the state section says who decided what, which is a claim a signature would strengthen.
- **Records for the other six files.** The two fit-test STLs exist to validate a fit that was never tested; their lifecycle has no transitions, and an empty `state` could only claim a premise — `draft` or `candidate` (`STA-7`) — neither of which is true of files that already served their purpose. v1 was replaced by v2, but `superseded` is reachable only from `approved` or `published` (§5.4) and nothing documents that v1 was ever approved. Silence was the honest answer in both cases.
- **Serving the record next to a download.** This repository publishes nothing over HTTP; the record travels in the same commit as the artifact, which is as close as a sidecar gets.

## What it cost

One tool, one record, one claims file, one document and one README line — 511 inserted lines, none of them in the design files. The STLs, the `.scad` and the printing workflow were not touched: a record is additive (invariant 3), and the only thing that changed about the design is that its rejection is now a fact a program can read.

## What this case study says about the standard

- **A recipe earns its keep when the vocabulary fits what was measured.** The most informative member of this record was the one that had to be absent: the measurement found a middle between `none` and `full`, and the format had no field for "the content, not the bytes" — a gap the `content` grade now fills ([ADR-0015](../adr/ADR-0015-a-recipe-can-determine-the-content-not-the-bytes.md)). An enum that cannot express a measured middle pushes honest producers into silence.
- **`state` on an artifact that never shipped is the class doing its job.** Most version schemes cannot say *this existed and lost*; `rejected` can, and `STA-11`'s refusal to resurrect it is what makes the statement worth recording.
- **A build recipe's `source.digest` is a lineage edge a consumer can verify without records.** `LIN-8`'s unresolvable parent is the normal case for sources, not a defect.
- **Adoption keeps finding the documentation.** The front-page example, the `state` class, the tool shape — each case study has found at least one place where the standard's own text or code disagreed with itself.
