# HANDOFF

## Last session — 2026-11-23 (evening, close-out)

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

1. Write `spec/90-extensions/c2pa.md`: what C2PA guarantees (embedded, signed, ingredient-based), what Variorum guarantees (sidecar identity, lineage, state), which standard is authoritative for which question, and the non-mapping cases (C2PA hard binding vs. Variorum digest; C2PA ingredients vs. `lineage`; a C2PA manifest that is stripped or re-signed).
2. Make it opt-in the same way: extension key `variorum:c2pa` or a documented reference from `extensions["c2pa:manifest"]` to the manifest, rules marked `bridge`, vectors in `spec/vectors/c2pa.json`.
3. Add an ADR if the coexistence rule is normative; re-run `python3 -m unittest discover -s tests` and `python3 tools/variorum.py conform --coverage` before every commit.

## Previous session — 2026-11-23 (Phase 1: testability)

**Did:** closed Phase 1 (testability) end to end. Wrote `spec/07-conformance.md` (`CON-1`…`CON-27`), the 103-vector suite in `spec/vectors/` with real fixtures and an exemptions list, the `conform` command with `--coverage`, `tests/test_vectors.py`, four ADRs (0005–0008) and the CI workflow (Python 3.11 and 3.13, no packages). Fixed the drift the suite exposed: SHOULD violations are now warnings, not errors; `scheme.name` accepts any lowercase name (SCH-2, new SCH-10 recommendation); the two examples that declared `lineage` without carrying it were corrected.

**Verified:** unit tests 67/67 OK; `conform --coverage` 103/103 PASS, 72/102 rules referenced, 30 exempt with reasons, 0 uncovered; the four real examples validate; `conform` exits 2 on a malformed suite and works from any working directory.

**Left open (now closed):** the SemVer bridge and its place in the conformance contract.

## Previous session — 2026-11-22

**Did:** created the repository, chose the name (`variorum`, validated against u-onoma with live collision checks), fixed the scope (a wrapper standard, not a replacement), wrote the v0.1 draft of the specification, the JSON Schema, the reference CLI and three real examples.

**Left open (closed on 2026-11-23):** conformance suite and test vectors; the extension bridges and the adoption guide remain open.
