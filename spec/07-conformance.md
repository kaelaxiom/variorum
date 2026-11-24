# 07 — Conformance

What it means for a record, and for an implementation, to claim Variorum.

Conformance here is not a compliment. It is a testable statement with a name and a version.

## 7.1 Two targets

**CON-1.** A conformance claim MUST name its target: a **record** or an **implementation**. The rules for each are different and neither implies the other.

**CON-2.** A conformance claim MUST name the record format version it is made against (for example `0.1`).

A record can conform to the format while the program that wrote it is wrong; a program can be correct while emitting records that violate the rules elsewhere.

## 7.2 Record conformance

**CON-3.** A record conforms to `core` if and only if it satisfies every MUST rule in [00-overview.md](00-overview.md), [01-identity.md](01-identity.md), [02-scheme.md](02-scheme.md) and — when `state` is present — [05-state.md](05-state.md).

**CON-4.** A record conforms to `lineage`, `recipe` or `attestation` if and only if it conforms to `core` and carries the corresponding member satisfying every MUST rule of its section ([03-lineage.md](03-lineage.md), [04-recipe.md](04-recipe.md), [06-attestation.md](06-attestation.md)).

The member is what defines the class. A record without `recipe` is not a `recipe` record, whatever its producer intended.

**CON-5.** `extensions["variorum:conformance"]`, when present, MUST be an array of strings drawn from `core`, `lineage`, `recipe`, `attestation`.

**CON-6.** A record that declares a class other than `core` MUST carry the member that class requires. Declaring `lineage` without a `lineage` member is a validation error.

Rationale: a declaration a consumer can trust only saves work if it cannot be false. See [ADR-0007](../docs/adr/ADR-0007-declared-classes-must-be-backed.md).

**CON-7.** The classes a record satisfies are determined by its content, not by its declaration. A declaration MAY be incomplete; the highest satisfied class still describes the record.

**CON-8.** A record that violates only a SHOULD rule remains conformant. An implementation MUST NOT reject a record on the sole ground that a SHOULD was not followed.

See [ADR-0005](../docs/adr/ADR-0005-should-violations-are-warnings.md). Warnings are useful; they are not the contract.

## 7.3 Implementation conformance

Four levels, mirroring the record classes:

| Level | Requirement |
|---|---|
| `core` | Passes every vector of class `core` |
| `lineage` | Passes `core` plus every vector of class `lineage` |
| `recipe` | Passes `core` plus every vector of class `recipe` |
| `attestation` | Passes `core` plus every vector of class `attestation` |

Levels are not a ladder: an implementation may claim `recipe` without claiming `lineage`.

**CON-9.** An implementation claiming level `L` MUST accept every accept vector whose class is `L` or `core`, and MUST reject every reject vector of those classes. A vector carrying `bridge` is required only of implementations that claim that bridge; every other implementation MUST skip it rather than fail it.

**CON-10.** On a reject vector, the implementation MUST report at least one of the rule identifiers listed in the vector. Reporting additional rules is permitted.

**CON-11.** An implementation MUST NOT pass a reject vector by accident — that is, it MUST NOT reject a record for a reason absent from the specification, since its verdict would then disagree with every other implementation on some other record.

**CON-12.** An implementation MUST NOT alter the record it validates. Normalising a version string in flight (SCH-7) is a non-conformance even when the verdict is right.

**CON-13.** A conformance claim MUST name the suite version against which it was established, not only the record format version.

## 7.4 The vector suite

The suite lives in [`spec/vectors/`](vectors/README.md). It is data, not code: any implementation in any language can run it.

**CON-14.** A vector file MUST be a JSON object with `suite` (the suite version, currently `variorum-vectors/1`), `group` (a short name) and `vectors` (a non-empty array).

**CON-15.** Every vector MUST carry `name`, `class` and `expect`. `class` MUST be one of the four conformance classes.

**CON-16.** Every vector MUST carry either `record` — a complete JSON value — or `patch`, a JSON object merged shallowly onto the file's `base` member. A vector carrying neither, or a `patch` in a file without `base`, is a suite error.

Shallow means exactly that: a `patch` key replaces the whole value at that key. Nested objects are not merged.

**CON-17.** `expect.valid` MUST be a boolean. When it is `false`, `expect.rules` MUST be a non-empty array of rule identifiers.

**CON-18.** Vector names MUST be unique across the whole suite, so that a failure can be cited in a bug report without ambiguity.

**CON-19.** A vector MAY carry `artifact`, a path relative to the vector file. The runner MUST resolve it and validate the record against those bytes. When the vector also sets `fixture` to `true`, the record's `artifact.digest` and `artifact.size` MUST equal the file's; the runner MUST verify this and treat a mismatch as a **stale suite** error (exit code 2), never as a pass or a failure of the record. A vector whose fixture moved must be repaired, not interpreted.

**CON-20.** A vector of kind `graph` MUST carry `records` (an array of complete records) and `expect.acyclic` (a boolean) instead of `record`. It tests graph-level rules that no single record can decide, currently LIN-7.

**CON-21.** A vector of kind `jcs` MUST carry `record` and `expect.jcs`, the exact UTF-8 string produced by the JSON Canonicalization Scheme (RFC 8785) of the record with `attestation` removed. It fixes the bytes a signature covers (ATT-6, ATT-7).

**CON-22.** `kind`, when present, MUST be one of `record`, `graph`, `jcs`. When absent it is `record`.

An extension bridge contributes vectors of its own. They live in the same suite and are marked so that a runner which does not implement the bridge can skip them honestly instead of failing them ([ADR-0010](../docs/adr/ADR-0010-bridge-rules-are-conformance-rules.md)).

**CON-28.** A vector MAY carry `bridge`, naming the extension bridge it exercises. Its value MUST equal the extension key the bridge defines — for example `variorum:semver` or `variorum:c2pa`. A bridge vector carries a `class` like any other, and is obligatory only for implementations that claim that bridge (`CON-9`).

## 7.5 Running the suite

```
python3 tools/variorum.py conform [--vectors <dir>] [--coverage] [--verbose]
```

**CON-23.** The runner MUST exit `0` when every vector passes, `1` when any vector fails, and `2` when the suite itself is malformed or stale.

`--coverage` additionally reports which rule identifiers of sections 00–06 and of the extension bridges under `spec/90-extensions/` are exercised by the suite and fails (exit `1`) when a rule is neither referenced nor exempted.

## 7.6 Coverage

**CON-24.** Every rule identifier defined in `spec/00-overview.md` through `spec/06-attestation.md`, and every rule identifier defined by an extension bridge under `spec/90-extensions/`, MUST be referenced by at least one vector or listed in [`spec/vectors/exemptions.json`](vectors/exemptions.json).

**CON-25.** An exemption MUST state a reason, and that reason MUST describe why no record can decide the rule — an obligation on a producer, a consumer, storage or a signing key. "Hard to test" is not a reason.

**CON-26.** A rule identifier that appears in a vector but is not defined in the specification is a suite error; the same applies to an exemption for a rule that does not exist.

**CON-27.** Coverage MUST be checked on every push by CI.

The exemption list is the honest accounting of what this standard cannot verify from a file. It is expected to shrink as the tooling grows; it must never grow silently.

## 7.7 What conformance does not mean

A conformant record is not a true record. Conformance says the record is well-formed and internally consistent; it says nothing about whether the artifact was produced as claimed, whether the producer had the right to produce it, or whether a signature is valid — the last requires key material that this format deliberately does not distribute.

An implementation that claims conformance claims to agree with these vectors. Nothing more, and nothing less.
