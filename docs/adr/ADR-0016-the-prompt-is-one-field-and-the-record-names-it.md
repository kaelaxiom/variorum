# ADR-0016 — `recipe.prompt` holds one field, and the record names which

**Status:** accepted
**Date:** 2026-11-28

## Context

`REC-9` was written for the generator that has one prompt: `recipe.prompt` MUST be "the prompt as sent, verbatim, including any system or negative prompt in `parameters`". The sentence assumes the provider offers a field that is *the* prompt and a few auxiliary prompts beside it.

Phase 3's third case study met a generator that has no such field. Suno's Custom mode takes six textual inputs — lyrics, styles, exclude styles, title, vocal gender and three numeric controls — and its interface has no box called "prompt" at all (its API reuses the name for the lyrics field, which is a coincidence, not a design). The `echo-language` adopter put the lyric field in `recipe.prompt` and the other five in `parameters` under `REC-11`. That reading is defensible — the lyrics are the text a voice sings — and it is not defined: nothing in the record says `prompt` holds the lyric field, so a consumer cannot reconstruct the call without knowing Suno's interface, and two records that both carry "the prompt" may be holding different fields.

Three readings were available and the text excluded none of them:

- `prompt` holds the lyrics, and the style text is a parameter (what the adopter did).
- `prompt` holds the style text, because that is the field that shapes the sound.
- `prompt` holds a concatenation of every field, which is a string nobody sent — a violation of "as sent" that no rule names.

The format already has the rule this case needed, in another section: `LIN-9` forbids a consumer from claiming a lineage complete when the parents are unresolved. `REC-9` had no equivalent for inputs, and the absence of a rule was read as a licence to infer.

## Options

1. **`prompt` becomes an object of named fields** — `{ "lyrics": …, "styles": … }`. Evidence-complete: the whole textual input in one member. But it gives a member every consumer reads as a string a second grammar, and it duplicates `parameters` for the half of the same call that is not text. ADR-0015 rejected exactly this shape for `determinism`, for the same reason.
2. **`prompt` holds the provider's field literally named `prompt`.** Rejected: it makes the standard's meaning depend on a vendor's vocabulary. Suno's API field named `prompt` happens to hold the lyrics; a provider that names a style field "prompt" would move the standard's answer with it.
3. **Define the semantic winner in the rule** — "the text the artifact renders". Rejected as a MUST: whether a style field is "rendered" into a song is a judgement about the provider's interface, not a property a record can be checked for. It is the class of rule MEMORY records as a preference wearing a normative keyword.
4. **Keep one string, let the record name which field it holds.** `REC-9` states that the member holds one field's value, never a synthesis; `recipe.promptField` names that field using the provider's own name; an absent member leaves the mapping unspecified, which is silence and not a claim of completeness. Chosen.

## Decision

- **`REC-9` is rewritten.** `recipe.prompt` MUST hold, verbatim, the value of one field the generator accepts — never a concatenation of fields, never a paraphrase. When `recipe.promptField` is absent, the mapping between `prompt` and the generator's fields is unspecified: the record does not claim that the generator has only one textual field.
- **`REC-23` is new and is a SHOULD.** When the generator accepts more than one textual field, the record SHOULD name the field `recipe.prompt` holds in `recipe.promptField`, using the provider's own name, and SHOULD record the remaining fields in `recipe.parameters` under their provider names (`REC-11`).
- **`REC-24` is new and is a MUST.** `recipe.promptField`, when present, MUST be a non-empty string, and MUST NOT be present unless `recipe.prompt` is. The shape is checkable; the truth of the name is not.
- **The schema types the member and nothing more:** `promptField` is a string with `minLength: 1`, and `dependentRequired` binds it to `prompt`. Both clauses are `REC-24`'s, not extra assertions.
- **Tool 0.9.0 rejects a `promptField` that is malformed or orphaned, and says nothing when it is absent.** It cannot see the provider's interface, so a warning on absence would be a guess (ADR-0005, `CON-8`).
- **The semantic guidance is prose, not a rule.** The field to promote is the one that carries what the artifact is about — the words a voice sings or speaks, the description a frame depicts — rather than one that shapes the output: style, exclusion, title, voice. A record for an instrumental that promotes the style field is not wrong; it made a different choice and named it.

## Rationale

**A member that holds "the prompt" while the generator has six of them is a member with no defined content.** `REC-9` did not fail by being wrong; it failed by being written for the only generator its author had used. The evidence a multi-field call leaves is a set of named strings. One of them travels in `prompt` because the member exists and consumers expect it; the rest travel in `parameters`, which is already the open map. What was missing is the label that connects the two halves — twenty-four bytes that turn an inference into a record.

**Absence is silence, not completeness.** Making an absent `promptField` mean "the generator has one field" would repeat the defect ADR-0015 closed: it would turn a decision no producer made into a claim the reader cannot distinguish from a considered one. The rule instead says what the absence means — the mapping is unspecified — which is the smallest true statement available.

**Why a SHOULD and not a MUST.** No validator can count the fields of a provider it has never seen. A MUST there would be unenforceable, and `conform --coverage` would count it as tested by a vector that only tests the shape of a name. The honest pair is a checkable MUST (`REC-24`) on the member's shape and a SHOULD (`REC-23`) on its presence: the accept vector exercises the member exactly as `REC-11` is exercised by a record carrying `parameters`, so the rule is cited without pretending its absence can be detected.

**Why not a bridge.** A provider that wants its field names fixed can define them in `spec/90-extensions/` — a Suno bridge could close `promptField` to `lyrics`, `styles`, `exclude_styles`, and so on. `REC-23` is the generic label that makes such a bridge possible; binding core to one vendor's vocabulary would do the opposite.

**What a consumer may conclude.** `prompt` is one field, so a consumer comparing two records' prompts compares one field whose identity is known only when both records name it. When either is silent, the comparison is about strings, not about inputs. This is `LIN-9`'s discipline applied to the recipe: the record states what it can show and remains silent about the rest.

## Consequences

- `spec/04-recipe.md`: `REC-9` rewritten, `REC-23` and `REC-24` added, and prose covering the choice of field, the instrumental case and the consumer's caution.
- `spec/vectors/recipe.json`: four vectors — an accept for a named multi-field prompt, and rejects for a non-string, an empty and an orphaned `promptField`. The suite moves to 208 vectors in thirteen groups.
- Coverage: 102/142 rules referenced, 40 exempt, 0 uncovered.
- Reference tool 0.9.0 checks `REC-24` for a recipe and for every hybrid stage, because `REC-19` makes a stage satisfy its kind's rules.
- `schema/variorum.schema.json` types `recipe.promptField` and requires `prompt` when it appears.
- `docs/case-studies/echo-language.md`: the question it recorded as open is closed, and its record — stamped before the member existed — can add `"promptField": "lyrics"` in one edit in the adopter's repository.
- No existing record becomes invalid: `prompt` stays a string, and the only new rejections concern a member that did not exist before.
- The lifecycle question the case studies produced — whether a generated take gets a state of its own — remains open for 0.2 and is an owner decision.
