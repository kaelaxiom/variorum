# 02 — Scheme references

How a record points at the version scheme a project already uses, without altering it.

## 2.1 The scheme object

**SCH-1.** The `scheme` member MUST be present and MUST be an object.

**SCH-2.** `scheme.name` MUST be present and MUST be a lowercase string matching `^[a-z][a-z0-9-]*$` or a namespaced custom name of the form `x-<vendor>-<name>`.

**SCH-3.** `scheme.version` MUST be present unless `scheme.name` is `none`, in which case it MUST be absent.

**SCH-4.** `scheme.authority`, when present, MUST be an absolute URI identifying the definition of the scheme.

```json
"scheme": { "name": "semver", "version": "1.4.2", "authority": "https://semver.org/spec/v2.0.0.html" }
```

```json
"scheme": { "name": "none" }
```

## 2.2 Scheme registry

The following names are reserved and carry the stated meaning. The list is informative; a consumer that does not know a scheme name MUST treat it as opaque.

| Name | Meaning | Ordering defined by |
|---|---|---|
| `semver` | Semantic Versioning 2.0.0 | semver.org §11 |
| `calver` | Calendar Versioning | calver.org; the specific format is conveyed by the version string |
| `pep440` | Python version scheme, including epochs and local versions | PEP 440 |
| `debian` | `[epoch:]upstream-revision` | Debian Policy §5.6.12 |
| `rpm` | Epoch-Version-Release | RPM version comparison rules |
| `maven` | Maven version ordering | Maven `ComparableVersion` |
| `nuget` | Four-part NuGet version | NuGet versioning rules |
| `date` | A date used as a version label | The field itself; must be ISO 8601 calendar date |
| `sequence` | A monotonically increasing integer (build, take, revision) | The integer |
| `custom` | A project-specific label with no shared semantics | Project documentation |
| `none` | The project assigns no version label | — |

Custom schemes outside this list SHOULD use the `x-` form: `x-du-vortoj-dv`.

**SCH-10.** A scheme name that is not in the reserved table SHOULD carry the `x-` prefix, so that a name a project invents today does not collide with a name this table reserves tomorrow.

The prefix is a recommendation, not a requirement: a lowercase name outside the table is opaque to every consumer and valid (SCH-2). A consumer that does not recognise `dv` MUST NOT reject the record, and MUST NOT guess what it means.

## 2.3 Ordering is not Variorum's business

**SCH-5.** Variorum MUST NOT define, and a consumer MUST NOT assume, any ordering between version labels belonging to different schemes.

**SCH-6.** Within one scheme, ordering is defined exclusively by that scheme's authority. Variorum does not restate it, refine it or override it.

**SCH-7.** Variorum MUST treat the version string as opaque. A producer MUST NOT depend on a consumer parsing it, and a consumer MUST NOT normalise, trim, case-fold or rewrite it.

Rationale: the moment Variorum parses version strings it becomes a competing scheme with an incomplete implementation of every other scheme. The value of wrapping is that the wrapped thing stays authoritative.

## 2.4 When the scheme has no ordering

**SCH-8.** When the scheme does not define an ordering (`custom`, `none`), the record MAY carry `scheme.sequence` as a non-negative integer to give consumers a monotonic order without inventing semantics.

**SCH-9.** `scheme.sequence`, when present, MUST increase strictly across artifacts of the same work in the same lineage.

```json
"scheme": {
  "name": "x-du-vortoj-dv",
  "version": "dv-001",
  "sequence": 1,
  "authority": "https://du-vortoj.social-data.com"
}
```

## 2.5 Worked examples

A library that already uses SemVer and must not change:

```json
"scheme": { "name": "semver", "version": "2.7.0", "authority": "https://semver.org/spec/v2.0.0.html" }
```

An editorially numbered series:

```json
"scheme": { "name": "sequence", "version": "12", "sequence": 12 }
```

A file with no version at all — honest, and therefore valid:

```json
"scheme": { "name": "none" }
```

The third case matters. A standard that forces a version number onto something that never had one teaches people to invent numbers. `none` is a legitimate answer.
