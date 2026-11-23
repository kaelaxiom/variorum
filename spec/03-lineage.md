# 03 — Lineage

How artifacts relate to the artifacts they came from.

## 3.1 The lineage object

**LIN-1.** The `lineage` member, when present, MUST be an object.

**LIN-2.** `lineage.parents` MUST be present and MUST be a non-empty array.

**LIN-3.** Each element of `parents` MUST be an object with an `id` matching `^urn:variorum:sha256:[0-9a-f]{64}$`.

**LIN-4.** Each element MUST carry a `relation` from the table in §3.2.

**LIN-5.** The `id` of a parent MUST NOT equal the record's own `id`. Self-reference is invalid.

```json
"lineage": {
  "parents": [
    { "id": "urn:variorum:sha256:8a11…", "relation": "generation" }
  ]
}
```

## 3.2 Relations

The relation describes the edge **from the parent to this artifact** — that is, what was done to the parent to obtain this artifact.

| Relation | Meaning | Typical producer |
|---|---|---|
| `generation` | Produced by a generative process from the parent as input | image-to-video, image-to-image, text-to-speech |
| `revision` | A new attempt at the same intent; a sibling take | any iterative workflow |
| `edit` | A non-generative modification of the parent's content | colour grade, cut, crop |
| `render` | Produced from the parent as a source document | PDF from Typst, HTML to PNG |
| `transcode` | Same content, different encoding | re-mux, format conversion |
| `fork` | Diverges from the parent and will not be merged back | experimental branch, alternate cut |
| `restore` | Recovered from the parent as a backup or archive | restore from vault |
| `derivation` | Any other derivation not covered above | catch-all |

**LIN-6.** A `revision` SHOULD be used when the intent is unchanged and only the attempt differs. A `generation` SHOULD be used when a new artifact is produced from the previous one as a source.

The distinction matters: three takes of the same prompt are three `revision` siblings with a common ancestor, not a chain. Modelling them as a chain implies improvement that nobody claimed.

## 3.3 Graph validity

**LIN-7.** A record MUST NOT participate in a cycle. A consumer that resolves records into a graph MUST detect cycles and MUST reject the graph if one is found.

**LIN-8.** A record MAY reference a parent whose record is not available. Unresolvable parents are not an error.

Rationale: records travel with artifacts, and artifacts get separated. A format that requires the whole graph to be present cannot describe an archive that was split across media.

**LIN-9.** When a parent is unresolvable, a consumer MUST still be able to use the artifact and MUST NOT claim that the lineage is complete.

## 3.4 Work-level identity

**LIN-10.** Two artifacts belong to the same work if they share an ancestor and every edge on the path uses one of `revision`, `edit`, `render`, `transcode`, `restore`.

**LIN-11.** An edge of type `fork` starts a new work.

**LIN-12.** `generation` neither joins nor splits works: it extends the work of its parent unless the producer states otherwise through an extension.

## 3.5 Depth and pruning

**LIN-13.** A producer SHOULD record the immediate parent only. Transitive ancestry is derived, never stored, except where an archive must be self-contained.

Storing the full chain duplicates information that a graph already contains, and duplicated information drifts.
