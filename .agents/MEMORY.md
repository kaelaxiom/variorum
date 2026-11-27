# MEMORY

Lessons learned while working on this repository. Append only; never delete an entry because it became inconvenient.

## 2026-11-22 — Naming

The first naming batch died almost entirely on live collision checks: `stemma`, `spuro`, `editio`, `recensio`, `provenio`, `colophon`, `exemplar`. All were reasonable Latin/Greek roots and all were occupied — several by products in adjacent niches (`colophon.fyi` is literally "publishing infrastructure for AI agents").

**Lesson:** for a public standard, run the collision search *before* getting attached to a name. A root that is semantically perfect and commercially occupied is worth less than a plainer root that is free.

## 2026-11-22 — Scope

The tempting design was "a better version scheme". It would have been unadoptable: nobody renumbers their releases for a new standard.

**Lesson:** standards spread by adding a layer, not by demanding a migration. Wrap, then earn the right to influence.

## 2026-11-22 — Prior art is dense

An *AI Provenance Protocol* with its own versioning section already exists, and SWHID already covers content-addressed identifiers for software. The differentiation has to be explicit in `spec/00-overview.md`, not left implicit.

**Lesson:** in a crowded adjacent space, the overview document is a positioning document. Say what you are not, early.

## 2026-11-23 — Accept vectors find the real bugs

The reject vectors were easy: take a rule, break it, assert a rejection. The accept vectors are what exposed the drift — the validator was rejecting records the specification allowed (`scheme.name` outside a closed list, an extension key without a namespace), because every implemented check had been treated as fatal. No reject vector can ever catch a validator that is too strict.

**Lesson:** for every MUST, write both a reject vector and an accept vector that is one deliberate step away from the boundary. The accept side is where over-strictness hides.

## 2026-11-23 — A fixture digest is code, not prose

A vector that asserts a digest against a stored string can pass forever while the file it describes has changed. Marking digest vectors `fixture: true` and recomputing the hash on every run (CON-19) turns staleness into a suite error (exit 2) instead of a silent pass.

**Lesson:** never let a conformance suite trust a stored hash it can recompute. A stale fixture is a broken test, not a failing record.

## 2026-11-23 — Testability closes the spec, not the code

`conform --coverage` counts every rule identifier in `spec/00`–`spec/06` and fails when one is neither exercised nor exempted with a reason. The exemption list (30 rules) is the first honest map of what this format cannot verify from a file: producer honesty, consumer caution, storage retention, key material.

**Lesson:** the exemptions are part of the standard's honesty, not a to-do list. Whenever a rule is exempted, the reason must say who the obligation falls on; "hard to test" is an admission that the rule is a preference and belongs in a SHOULD.

## 2026-11-23 — A bridge that applies by name is a trap

Applying the SemVer grammar whenever `scheme.name` is `semver` would have made `core` conformance stricter than `SCH-7` allows and retroactively invalidated labels a project already published. The fix was to make the bridge a claim — an extension key the record carries — so the rules bind only the records that asked for them.

**Lesson:** when an extension sharpens a core member, the sharpening must be opt-in and visible in the record. A rule that fires on a name rather than on a claim silently changes what an existing record means.

## 2026-11-23 — Adopting a foreign grammar costs two traps, not one

Implementing SemVer's grammar from the published pattern exposed two host-language traps: Python's `\d` accepts any Unicode decimal digit (matching `١.٢.٣`), and `$` matches before a trailing newline, so `"1.4.2\n"` passed an anchored `match`. Both were caught by testing against the official valid/invalid example list, not by reading the pattern.

**Lesson:** when a specification imports an external grammar, copy that standard's own conformance examples into the tests and run them before trusting the pattern. `re.ASCII` and `fullmatch` (or `\Z`) are the minimum defences in Python.

## 2026-11-24 — A citation is a claim like any other

The C2PA draft carried two confident, well-formatted section references that were simply wrong: "the active manifest is the last one whose content bindings validate" (§15.5.1 says the last manifest in the store) and "the manifest store is one of the exclusions" (exclusions are a mechanism the claim generator may use, and a manifest may carry no hard binding at all). Neither error would have been caught by any test in this repository — both were prose about a document we do not own.

**Lesson:** when a normative sentence summarises a foreign specification, open that specification and check the section before merging. A citation that looks precise is indistinguishable from a correct one until someone follows it.

## 2026-11-24 — ABNF and ecosystem disagree; the bridge must accept both

C2PA's ABNF for its URN allows only uppercase hex digits, yet the UUID string representations its own libraries produce (Java's `UUID.toString()`) are lowercase. A strict copy of the ABNF would reject pointers that real manifests carry. The same ABNF also allows colons inside the claim-generator component, so a regex that excludes them is silently over-strict.

**Lesson:** for a foreign identifier, the accept side is defined by what the foreign ecosystem emits, not only by its grammar. Read the ABNF, then look at what an implementation actually writes — and put both cases in accept vectors.

## 2026-11-24 — "Verbatim" is an untestable MUST

`C2P-2` originally required the URN to be "recorded verbatim". No vector can check that: verification needs the manifest, which the record validator never sees. The requirement is real, but it is a producer obligation, so it belongs in prose, not in a rule the coverage report counts as tested.

**Lesson:** any MUST whose truth depends on a document outside the record is a preference wearing a normative keyword. Keep the checkable shape as the rule; state the fidelity expectation as prose.

## 2026-11-24 — Three hashes, one byte sequence

The 111-byte `hello.txt` fixture hashes to `a370e4f1…` under SHA-256 (the digest), `affa1e6d…` under raw SHA-1 (used by nothing here) and `bad480af…` under SHA-1 of `blob 111\0` + bytes (the `cnt` SWHID, and what `git hash-object` prints). An identifier that looks like a hash can still be a hash of something else.

**Lesson:** before deciding whether two identifiers can ever substitute for each other, hash the same fixture every way the candidates allow and compare pre-images, not just algorithms. "Both are hashes of the content" is the sentence that produces records that verify wrong.

## 2026-11-24 — CON-19 recomputes digests, not every hash a vector carries

A vector's `fixture: true` check guards `artifact.digest`; it cannot recompute a SWHID, because that needs a different pre-image that the suite does not model. The base claim in `spec/vectors/swhid.json` is therefore a stored string, and only a unit test can keep it honest.

**Lesson:** when a bridge vector carries a foreign hash, add a test that rebuilds that hash from the fixture in the foreign standard's own way and asserts the vector's value. Otherwise the same staleness CON-19 exists to prevent simply moves one file over.

## 2026-11-24 — The right value for the wrong reason

The SPDX bridge is the first place where copying a foreign checksum into `artifact.digest` would produce the *correct* value in the ordinary case: a file element's `SHA256` is the same bytes under the same algorithm. Every other bridge refused the copy because it was obviously wrong (a SWHID hashes a different pre-image, a C2PA manifest is a different subject). Refusing a copy that would be numerically right is the harder discipline, because no test of the resulting record can tell it apart from a computed digest.

**Lesson:** the question is never "does this value match?" but "is this document entitled to state it?". When a foreign field happens to coincide with a local one, keep the local one computed from the bytes and make the coincidence a consumer's comparison — otherwise the record inherits a staleness it cannot detect.

## 2026-11-24 — A hash over hex text is not a hash over bytes

SPDX's package verification code (§7.9) is SHA-1 over the sorted concatenation of the files' SHA-1 *hex strings*. For the 111-byte fixture that is `SHA1("affa1e6d…5215286c") = 41b0f520…`, a value no algorithm applied to the bytes can produce. It looks like a content hash and is a hash of a set rendered as text.

**Lesson:** before treating any "checksum" as comparable to a digest, read what its pre-image is built from. Equal-length hex is not equal subject, and a set hashed as text is the case where the two diverge most quietly.


## 2026-11-25 — The storefront is the most-copied document, and no test reads prose

The README's Quick example showed `lineage.parents` as an array of strings and `state.transitions[].actor` as a string — two shapes the validator rejects — so the first record many readers would write was invalid by construction. `validate` reads JSON, `conform` reads vectors, and link checking reads only links: nothing was ever going to notice.

**Lesson:** the example on the front page is not prose, it is a template. Make it a record the repository already validates, and pin the copy with a test that fails on drift. A hand-written skeleton needs a second implementation of the format to stay true, and it never gets one.

## 2026-11-25 — Verify a defect report before acting on it

The previous run listed three broken shapes in the README. Two were real; the third — `recipe.tool` as an object — is exactly what `$defs/tool` allows, and "fixing" it would have broken a correct example. Reported defects are claims from a run that may have stopped early, not measurements.

**Lesson:** check each claimed defect against the schema or the tool before editing. An audit finding that is wrong is more expensive than one that is missing, because acting on it damages working text.

## 2026-11-25 — An uncommitted example is a claim, not a fact

`docs/adoption.md` and `examples/instruisto-release-copilot/` sat in the tree from the previous run with plausible digests. Re-downloading both release assets and recomputing their SHA-256 cost two minutes and turned "the guide says so" into "the bytes say so"; the digests happened to match, which is exactly why the habit is cheap and the alternative is not.

**Lesson:** before committing an example produced by an earlier run, re-derive its identity from the source. The expensive failure is not a wrong digest that gets caught — it is a wrong digest that gets published.

## 2026-11-26 — A tag the provider writes back is evidence, not a copy

The lyric block in the project's prompt file and the `USLT` frame Suno writes into the MP3 agree character for character in three of four takes, and the fourth carries the final `[Outro]` section twice. "The prompt is checkable against the artifact" was true enough to write and wrong as stated for one file in four.

**Lesson:** when a document compares a generator's output tag with the input that produced it, measure every artifact before claiming equality for a batch. State the comparison as evidence that can drift, not as a checksum that must match.

## 2026-11-26 — A command block is read from the directory it names

All three case studies ran `python3 tools/variorum.py` over paths relative to the adopter's repository — a directory that does not contain that tool. The block is correct only for a reader who happens to be standing in a second checkout, which is the one thing the prose never said.

**Lesson:** every shell block in a document must state the directory it assumes. When two repositories meet in one command, say which side the tool comes from; the paths already say which side the data is on.

## 2026-11-27 — A failing test and a passing vector can both be right

`ProvBridgeTests` failed because its helper put a record's sections inside the bridge's claim object, and `PROV-3` rejects exactly that. The vector exercising the same rule (`prov/claim-survives-a-full-projection`) had the correct shape and passed. The test was the defect; the rule was doing its job.

**Lesson:** when a unit test and a vector disagree about one rule, read both before editing either. The vector is the conformance contract; the test is a convenience built around it. Editing the validator to satisfy a badly built fixture turns a correct rule into a wrong one, and the suite would still be green.
