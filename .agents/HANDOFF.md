# HANDOFF

## Last session — 2026-11-24 (Phase 2: SWHID bridge)

**Did:** closed the SWHID bridge the previous run had left written but uncommitted and red.

- `spec/90-extensions/swhid.md` (`SWH-1`…`SWH-8`): a record claims the bridge with `extensions["variorum:swhid"]`, an object with exactly one member, `swhid`, holding one SWHID of scheme version 1. The identifier is shape-checked only — `swh:1:`, one of the five object types, 40 lowercase hex digits, optional `;name=value` qualifiers from the closed list of §6.2/§6.3. Context qualifiers are held to SWHID's *producer* constraints (§6.1–§6.3: `visit` requires `origin` and names a snapshot, `path` only on `cnt`/`dir` and absolute, `anchor` requires `path` and names a root object, each qualifier at most once, `origin` a URI); fragment qualifiers (`lines`, `bytes`) are refused because a fragment is not an artifact (`ID-9`); identity stays the digest (`SWH-6`).
- The load-bearing answer to the handoff's question — **can a SWHID be the digest?** No, and the document proves it with the same 111 bytes hashed three ways: `a370e4f1…` (SHA-256, the digest), `affa1e6d…` (raw SHA-1, used by nothing), `bad480af…` (SHA-1 over `blob 111\0` + bytes, the `cnt` SWHID; `git hash-object` prints the same digits). Even the friendliest object type hashes a different pre-image; `dir`, `rev`, `rel` and `snp` are not about the artifact's bytes at all, and the tarball/`dir` distinction is written down as the case where the two identifiers earn their keep side by side.
- `spec/vectors/swhid.json` — 32 vectors, each marked `"bridge": "variorum:swhid"`, including accept vectors for the four non-`cnt` object types, a full four-qualifier claim in canonical order, a `%3B` escape that must survive untouched, a path whose case must not be normalised, and the unmarked accept vector proving a record without the claim says nothing about the archive. `SWH-7`/`SWH-8` exempted with reasons (consumer obligations).
- `docs/adr/ADR-0012-swhid-bridge-is-a-sibling-identifier.md` — why a content hash from another model stays a sibling identifier, and why absorbing qualifiers into `producer`/`created`/`lineage` would state things that verify wrong.
- Schema: `extensions["variorum:swhid"]` typed (`additionalProperties: false`, pattern kept byte-for-byte in step with the tool's regex, a `not` guard against fragment qualifiers); the `SWH-4` combination checks are declared as tool-enforced, because JSON Schema cannot express a constraint that depends on another member's value.
- Tool 0.5.0 (`validate_swhid_bridge`, `SWH` rule family); `tests/test_validate.py` gains `SwhidBridgeTests` (15 tests), one of which recomputes the fixture's `cnt` SWHID from `blob 111\0` + bytes and asserts that `spec/vectors/swhid.json`'s base claim is that value — the vector suite cannot recompute a SWHID itself, so a unit test pins it. `tests/test_vectors.py` expects the `swhid` group; README, CHANGELOG, PLAN, extension and vector READMEs updated.

**Verified:** 103 unit tests OK; `conform --coverage` 170/170 PASS, 90/125 referenced, 35 exempt, 0 uncovered; five examples validate.

**Left open:**
- Owner review of the whole draft and the transfer to `cazucito`. Unchanged, and still the only blocker on a public announcement.
- SPDX next. Worth reading before designing: SPDX carries `checksum` values in the same algorithms Variorum uses, so unlike SWHID a checksum *can* equal `artifact.digest`. The decision is what a checksum of a *package* means when the record describes one artifact, and what the bridge should point at (the SBOM document, by `documentNamespace`) rather than copy.
- One SWHID per record. A project that wants both the `rel` and a locally checkable `cnt` of the same release needs two records or a namespaced extension key until a bridge revision adds a multi-object form (ADR-0012).
- Consistency item: `C2P-1` and `SWH-1` reject an explicit JSON `null` under the claim key, because the record wrote the key; the SemVer bridge still treats `null` as absent and returns early. The schema types all three claims as objects, so the tool is now stricter than the SemVer check. Aligning SEM is a behaviour change to a shipped bridge — needs its own vector and a CHANGELOG line, so it was not done here.
- `conform --verbose` still has no "skipped bridge vector" report (it never had; the reference runner implements every bridge).
- `extensions["variorum:semver"].tag` still holds one tag per record.
- Domain for the public site, `u-onoma`/`_index` registration: owner decisions, nothing in the repository invents a URL.

## Previous session — 2026-11-24 (Phase 2: C2PA bridge)

**Did:** closed the C2PA bridge the previous run had left uncommitted and red.

- `spec/90-extensions/c2pa.md` (`C2P-1`…`C2P-8`): a record claims the bridge with `extensions["variorum:c2pa"]`, an object with exactly `manifest` (the `urn:c2pa:` URN of the active manifest), `location` (`embedded`/`external`) and `uri` (required iff external, forbidden otherwise). Nothing is copied out of the manifest. Identity stays the digest (`C2P-6`); the hard binding, ingredients and claim signature are written down as non-mappings (90.3, 90.6, 90.7).
- Verified every C2PA citation against the 2.2 specification before merging. Two statements inherited from the draft were wrong and are fixed: the active manifest is the **last manifest in the store** (§15.5.1), not "the last one whose bindings validate"; and the manifest store is **normally** an excluded range, not a mandated one (§9.1 allows a manifest with no hard binding at all, and exclusions are the mechanism, not a requirement).
- Removed an untestable MUST: `C2P-2` no longer says the URN is "recorded verbatim" as a rule — that is prose in 90.1, because no vector can know what C2PA emitted. What remains normative is the shape: namespace, UUID, and an opaque optional tail.
- The URN shape check accepts both hexadecimal cases and a claim-generator containing colons. C2PA's ABNF allows colons in that component and its HEXDIG is uppercase-only, but real libraries emit lowercase UUIDs (Java's `UUID.toString()`), so the bridge is lenient on input and never re-cases the stored value. Two accept vectors pin this.
- `spec/vectors/c2pa.json` — 19 vectors, marked `"bridge": "variorum:c2pa"`, including the over-strictness guards above and a rejected JSON `null` claim. `C2P-7`/`C2P-8` exempted with reasons (consumer obligations).
- `docs/adr/ADR-0011-c2pa-bridge-references-the-manifest.md` — why the bridge points instead of absorbing signed content into an unsigned sidecar.
- Schema: `extensions["variorum:c2pa"]` typed (`additionalProperties: false`, `location` enum, conditional `uri`); the `manifest` pattern kept byte-for-byte in step with the tool's regex.
- Tool 0.4.0 (`validate_c2pa_bridge`, `C2P` rule family); `tests/test_validate.py` gains `C2paBridgeTests` (9 tests); `tests/test_vectors.py` expects the `c2pa` group; README, CHANGELOG, PLAN, extension and vector READMEs updated.

**Verified:** 88 unit tests OK; `conform --coverage` 138/138 PASS, 84/117 referenced, 33 exempt, 0 uncovered; five examples validate.

**Left open:**
- Owner review of the whole draft and the transfer to `cazucito`. Unchanged, and still the only blocker on a public announcement.
- SWHID next. It is the opposite case to C2PA: a SWHID is itself a content hash with its own object-type prefixes (`swh:1:cnt:…`), so the decision to make is whether it may ever stand in for `artifact.digest` (probably not: different algorithm family, different preimage rules) and what the bridge therefore records.
- Consistency item: `C2P-1` rejects an explicit JSON `null` under the claim key, because the record wrote the key; the SemVer bridge still treats `null` as absent and returns early. The schema types both claims as objects, so the tool is now stricter than the SemVer check. Aligning SEM is a behaviour change to a shipped bridge — needs its own vector and a CHANGELOG line, so it was not done here.
- `conform --verbose` still has no "skipped bridge vector" report (it never had; the reference runner implements every bridge).
- `extensions["variorum:semver"].tag` still holds one tag per record.
- Domain for the public site, `u-onoma`/`_index` registration: owner decisions, nothing in the repository invents a URL.

## Previous session — 2026-11-23 (evening, close-out)

**Did:** made the SemVer bridge durable. The tree had been left uncommitted by the previous run.

- Fixed the citation defect recorded in the previous handoff: the SemVer grammar is normative in the *Backus–Naur Form Grammar for Valid SemVer Versions* appendix, and the regular expression is the pattern published in the SemVer FAQ — not "§9" (item 9 is the pre-release rule). Corrected in `spec/90-extensions/semver.md` and in the comment above `SEMVER_PATTERN`.
- Re-hashed the example artifact from the release itself (`c40d573a…`, 637,290 B): the record is still a digest of the real bytes.
- Fixed five dead relative links (three in `spec/90-extensions/`, two in ADR-0010) and added `tests/test_docs.py`, which fails on any relative markdown link that does not resolve.
- Added a lead paragraph to `CON-28` so the out-of-order number explains itself.

**Verified:** 79 unit tests OK; `conform --coverage` 121/121 PASS, 78/109 referenced, 31 exempt, 0 uncovered; five examples validate.

**Left open (unchanged):** C2PA bridge next; owner review and transfer to `cazucito` are owner decisions.

## Previous session — 2026-11-23 (Phase 2: SemVer bridge)

**Did:** wrote `spec/90-extensions/semver.md` (`SEM-1`…`SEM-7`) and made the whole bridge testable end to end:

- The bridge is an opt-in claim: a record joins it by carrying `extensions["variorum:semver"]`. Rules: the claim is an object (SEM-1), requires `scheme.name = "semver"` (SEM-2) and a SemVer 2.0.0 version string (SEM-3), forbids `scheme.sequence` (SEM-4), constrains the optional `tag` to end with the version's precedence part (SEM-5), leaves ordering to SemVer with no tiebreaker and no identity from version equality (SEM-6), recommends the authority URI (SEM-7).
- `spec/vectors/semver.json` — 18 vectors (7 accept, 11 reject) marked `"bridge": "variorum:semver"`, plus one unmarked accept vector proving an unclaimed `semver` label stays opaque.
- Conformance section: new `CON-28` (`bridge` member on vectors), revised `CON-9` (bridge vectors are opt-in for implementations) and `CON-24` (coverage includes `spec/90-extensions/`).
- ADR-0009 (opt-in claim) and ADR-0010 (bridge rules are conformance rules).
- Reference tool 0.3.0: `validate_semver_bridge` with the official SemVer grammar compiled under `re.ASCII` and applied with `fullmatch`; coverage scans extension bridges.
- Schema types `extensions["variorum:semver"]` as an object with an optional string `tag`.
- `examples/instruisto-guide-owasp/` — a real released artifact (49-page `guide.pdf`, 637,290 B, tag `owasp-api-security/v1.3.1`, digest `c40d573a…` computed from the release asset, not written by hand), with a build recipe whose toolchain and timestamp come from the PDF's own metadata.

**Verified:** unit tests 77/77 OK; `conform --coverage` 121/121 PASS, 78/109 rules referenced, 31 exempt, 0 uncovered; all five example records validate; the grammar reproduces semver.org's own valid/invalid lists.

**Decisions taken (recorded in ADRs, no owner input needed):**
- A bridge is an extension claim, never a conformance class, and binds only records that carry the claim (ADR-0009). This keeps `SCH-7` opacity and invariant 3 intact: no project is forced to strict-label its past releases.
- Bridge rules are part of the coverage contract, and bridge vectors are opt-in for implementations (ADR-0010).

**Left open:**
- Owner review of the whole draft (Phase 0 checkbox) and, after it, the transfer to `cazucito`. Unchanged.
- Extension bridges still to write: C2PA, SWHID, SPDX, PROV. C2PA next; it must not absorb the SemVer bridge's shape blindly — a C2PA manifest is embedded and signed, so "who wins" needs an explicit answer.
- `extensions["variorum:semver"].tag` holds one tag. A project that publishes several equivalent tags for one release (`v1.3.1` and `course/v1.3.1`) can record only one. Deferred until a project needs both; adding an array later would be a compatible extension of the bridge, but it needs an ADR.
- `conform --verbose` does not yet report which vectors were skipped for lack of a bridge claim, because the reference runner implements every bridge. A third-party runner needs that report to satisfy `CON-9` honestly.
- The public site domain and the `u-onoma`/`_index` registration remain owner decisions; nothing in the repository invents a URL.

## Next session should

1. Write `spec/90-extensions/spdx.md`: what an SBOM guarantees (elements, relationships, package checksums, `documentNamespace`), what Variorum guarantees, and the one place the two can agree (an SPDX `checksum` using SHA-256 of the artifact itself, which *can* equal `artifact.digest` — say when, and what a package checksum that covers more than one file means instead).
2. Make it opt-in the same way: extension key `variorum:spdx`, vectors in `spec/vectors/spdx.json` marked `bridge`, `CON-28`.
3. Add an ADR if the coexistence rule is normative; re-run `python3 -m unittest discover -s tests` and `python3 tools/variorum.py conform --coverage` before every commit.

## Previous session — 2026-11-23 (Phase 1: testability)

**Did:** closed Phase 1 (testability) end to end. Wrote `spec/07-conformance.md` (`CON-1`…`CON-27`), the 103-vector suite in `spec/vectors/` with real fixtures and an exemptions list, the `conform` command with `--coverage`, `tests/test_vectors.py`, four ADRs (0005–0008) and the CI workflow (Python 3.11 and 3.13, no packages). Fixed the drift the suite exposed: SHOULD violations are now warnings, not errors; `scheme.name` accepts any lowercase name (SCH-2, new SCH-10 recommendation); the two examples that declared `lineage` without carrying it were corrected.

**Verified:** unit tests 67/67 OK; `conform --coverage` 103/103 PASS, 72/102 rules referenced, 30 exempt with reasons, 0 uncovered; the four real examples validate; `conform` exits 2 on a malformed suite and works from any working directory.

**Left open (now closed):** the SemVer bridge and its place in the conformance contract.

## Previous session — 2026-11-22

**Did:** created the repository, chose the name (`variorum`, validated against u-onoma with live collision checks), fixed the scope (a wrapper standard, not a replacement), wrote the v0.1 draft of the specification, the JSON Schema, the reference CLI and three real examples.

**Left open (closed on 2026-11-23):** conformance suite and test vectors; the extension bridges and the adoption guide remain open.
