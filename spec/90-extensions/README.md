# Extensions

Bridges between Variorum and adjacent standards. Each file states what the other standard does, what Variorum does, and how the two coexist without either absorbing the other.

Nothing here modifies the core specification. An extension may add keys under `extensions`, and may define a mapping in both directions; it may not redefine a core member (`CORE-11`).

## Planned

| File | Standard | Question it answers |
|---|---|---|
| `c2pa.md` | Content Credentials | A media file carries a signed C2PA manifest. Where does the Variorum record point, and which one wins? |
| `swhid.md` | Software Hash Identifier | A source tree has a SWHID. Does a Variorum record replace it, wrap it, or ignore it? |
| `spdx.md` | SPDX / CycloneDX (SBOM, ML-BOM) | The BOM describes what is inside; Variorum describes the artifact. How are they cross-referenced? |
| `prov.md` | W3C PROV | Variorum is a serialisation of a PROV subset. Which subset, and what is deliberately omitted? |
| `semver.md` | Semantic Versioning | A worked wrapping example that preserves SemVer precedence end to end. |

## Rules for writing one

1. State what the other standard already guarantees. Do not re-specify it.
2. Give the mapping in both directions, including the cases that do not map.
3. Say which standard is authoritative for which question.
4. Add a vector in `spec/vectors/` once the conformance suite exists.
