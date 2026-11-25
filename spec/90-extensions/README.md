# Extensions

Bridges between Variorum and adjacent standards. Each file states what the other standard does, what Variorum does, and how the two coexist without either absorbing the other.

Nothing here modifies the core specification. An extension may add keys under `extensions`, and may define a mapping in both directions; it may not redefine a core member (`CORE-11`) and may not add a MUST to a core section.

## Written

| File | Standard | Question it answers |
|---|---|---|
| [semver.md](semver.md) | Semantic Versioning 2.0.0 | A project already versions its releases with SemVer. What exactly does the record claim, and where does a tag go? |
| [c2pa.md](c2pa.md) | Content Credentials (C2PA 2.2) | A media file carries a signed C2PA manifest. Where does the Variorum record point, and which one is authoritative for what? |
| [swhid.md](swhid.md) | Software Heritage identifier (SWHID 1.2, ISO/IEC 18670:2025) | A source tree has a SWHID. Is it a digest, a version, or something else — and what does the record therefore carry? |
| [spdx.md](spdx.md) | SPDX 2.3.1 (bill of materials) | A bill of materials lists what is inside a package. Which document describes this artifact, which element, and can an SPDX checksum be the digest? |

All four bridges are opt-in: the rules bind only records that carry the bridge's extension key (`extensions["variorum:semver"]`, `extensions["variorum:c2pa"]`, `extensions["variorum:swhid"]`, `extensions["variorum:spdx"]`), and the class model stays at four ([ADR-0009](../../docs/adr/ADR-0009-semver-bridge-is-opt-in.md)). The C2PA bridge additionally refuses to copy anything out of the manifest it points at ([ADR-0011](../../docs/adr/ADR-0011-c2pa-bridge-references-the-manifest.md)); the SWHID bridge refuses to promote an identifier from another object model to the artifact's identity ([ADR-0012](../../docs/adr/ADR-0012-swhid-bridge-is-a-sibling-identifier.md)); the SPDX bridge refuses to copy a checksum that would often be numerically right ([ADR-0013](../../docs/adr/ADR-0013-spdx-bridge-points-at-the-sbom.md)).

## Planned

| File | Standard | Question it answers |
|---|---|---|
| `prov.md` | W3C PROV | Variorum is a serialisation of a PROV subset. Which subset, and what is deliberately omitted? |
| `cyclonedx.md` | CycloneDX (ECMA-424) | Another BOM format, with its own `serialNumber` and hash model. Kept apart from `spdx.md` so that each document owns its own rules. |

## Rules for writing one

1. State what the other standard already guarantees. Do not re-specify it.
2. Give the mapping in both directions, including the cases that do not map.
3. Say which standard is authoritative for which question.
4. Make the bridge opt-in: define the extension key that claims it, and bind only the records that carry it. A bridge that applies implicitly to a scheme name makes core conformance stricter than `SCH-7` allows.
5. Add a vector in `spec/vectors/` for every rule the bridge defines, carrying `"bridge": "<extension key>"` (CON-28). `conform --coverage` fails on a rule that is neither exercised nor exempted with a reason (CON-24, CON-25). See [ADR-0010](../../docs/adr/ADR-0010-bridge-rules-are-conformance-rules.md).
