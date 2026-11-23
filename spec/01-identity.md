# 01 — Identity

Normative rules for identifying an artifact.

## 1.1 The artifact

**ID-1.** The `artifact` member MUST be present and MUST be an object.

**ID-2.** `artifact.digest` MUST be present and MUST match the regular expression `^sha256:[0-9a-f]{64}$`.

**ID-3.** The digest MUST be computed over the exact bytes of the artifact, with no normalisation, no transcoding and no line-ending conversion.

**ID-4.** `artifact.size`, when present, MUST be the exact length in bytes and MUST be consistent with the artifact.

**ID-5.** `artifact.mediaType`, when present, SHOULD be a media type registered with IANA and MUST follow the `type/subtype` syntax of RFC 2046.

**ID-6.** `artifact.name`, when present, is informational. It MUST NOT be used as an identifier, and consumers MUST NOT treat two artifacts with the same name as the same artifact.

```json
"artifact": {
  "digest": "sha256:3f9c1d0b6a4e8f27a5d3c9b1e0f4a7d2c5b8e1f3a6d9c0b2e5f7a1c4d8b0e3f6",
  "size": 2741182,
  "mediaType": "video/mp4",
  "name": "discipline-gardan-001.es.video-shot-01.mp4"
}
```

## 1.2 The record identifier

**ID-7.** The `id` member MUST be present and MUST match `^urn:variorum:sha256:[0-9a-f]{64}$`.

**ID-8.** The hexadecimal component of `id` MUST be identical to the hexadecimal component of `artifact.digest`.

Rationale: a derived identifier cannot disagree with the artifact. If two records describe the same bytes, they necessarily carry the same `id`, and a graph that references records by `id` is therefore stable across producers.

**ID-9.** A record MUST describe exactly one artifact. A record describing several artifacts is invalid; produce one record per artifact and link them with `lineage`.

## 1.3 The producer

**ID-10.** The `producer` member, when present, MUST be an object with at least a `name`.

**ID-11.** `producer.kind`, when present, MUST be one of `human`, `organization`, `software`.

**ID-12.** When `producer.kind` is `software`, the `producer.software` member SHOULD identify the software by `name` and `version`.

```json
"producer": {
  "name": "cazucito",
  "kind": "human"
}
```

```json
"producer": {
  "name": "hermes-agent",
  "kind": "software",
  "software": { "name": "hermes", "version": "0.21.7" }
}
```

## 1.4 Identity is per artifact, not per work

**ID-13.** Two artifacts with different bytes MUST have different `id` values, even when they represent the same work at the same logical moment.

**ID-14.** A consumer MUST NOT infer that two artifacts are the same work from anything in this section. Work-level identity is recovered through `lineage` (03-lineage) or an extension.

## 1.5 Non-stability of byte-representation

**ID-15.** A producer SHOULD be aware that re-muxing, re-saving or re-compressing an artifact produces a different digest for content that is perceptually identical.

**ID-16.** When an artifact is re-encoded without semantic change, the resulting record SHOULD declare the relation `transcode` to the previous artifact's `id`, so that the work-level identity survives the byte-level change.

This is the reason lineage exists. A digest identifies a file; only the graph identifies a work.
