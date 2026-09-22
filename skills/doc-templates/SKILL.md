---
name: doc-templates
description: Templates and structure for READMEs, API documentation, changelogs, and inline code documentation, plus Diátaxis document-type selection (tutorial / how-to / reference / explanation), global-audience prose rules, and the register and naming rules for prose humans read (name the mechanism, not a metaphor for it) — ADRs defer to the domain-modeling skill
---

# Documentation Templates

Reusable templates for common documentation artifacts: READMEs, API docs, changelogs, and inline code comments. ADRs defer to the `domain-modeling` skill.

## Diátaxis: Pick the Document Type First

Four documentation types, each serving one distinct need. Mixing them in a single document is the most common structural failure — a tutorial that detours into reference, an explanation that slides into how-to. Decide which one you are writing before you draft it.

| Type | Serves | Shape |
|---|---|---|
| Tutorial | Learning by doing | A guided lesson that succeeds end to end. Concrete, no choices offered, no digression. |
| How-to guide | A goal the reader already has | Numbered steps to an outcome. Assumes competence; omits theory. |
| Reference | Looking something up | Dry, complete, consistent. Describes the machinery; argues nothing. |
| Explanation | Understanding why | Design, tradeoffs, background. The place for rationale. |

The templates below are mostly how-to and reference; ADRs and design docs are explanation. When a page tries to be two types at once, split it.

## README

Sections, in order: one-sentence description of what it does and who it is for;
Quick Start (prerequisites with versions, then clone, install, run); Usage (the
most common call, then a table or short list of options); Project Structure (only
when the layout is non-obvious); Development (test, lint, build commands);
Contributing; License. Every command shown must run as written.

## API Documentation

Per endpoint or public function, in order: signature as the heading; one-line
purpose; authentication; parameters as a table with name, type, required,
description; a request example; a response example with status code; errors as a
table with status, condition, body. Show real shapes, not placeholders.

## Architecture Decision Records (ADRs)

ADRs follow the `domain-modeling` skill — it owns the three-part gate for when a
decision deserves one, the `docs/adr/` layout, and the canonical minimal format.
Load it before writing an ADR.

## Changelog

[Keep a Changelog](https://keepachangelog.com/) format: an `[Unreleased]` section
at the top, then one section per version with its date, each split into Added,
Changed, Fixed, Removed as needed. Every entry ends with its issue or PR
reference in parentheses, `(#123)`.

## Code Comments

Comments explain why: workarounds, business rules, performance tricks, links to
specs and issues. The code already shows what. Public APIs document parameters,
return values, error conditions, and one usage example; everything else is
documented only when a caller cannot infer it from the signature, so a
"document everything" lint is satisfied by fewer, better comments, not more.

Prose in code is read on every pass, so keep it minimal. When an explanation
outgrows a couple of lines, move it to a README, an ADR, or a design doc and
link it from the code; the code carries the load-bearing why, the documents carry
the depth. A TODO carries its issue number. Commented-out code is deleted; git
has the history. When a group of fields matters enough to label, give it a type
instead of a banner comment.

## Writing for a Global Audience

Much technical prose is read by non-native English speakers and by translation
tools, so on top of the general prose hygiene the `unslop` skill owns: keep
sentences under about 25 words, write "start" and "roughly" rather than "kick
off" and "in the ballpark", and give every "it" and "this" a clear antecedent.

## Register

Applies to every prose surface a human reads: comments, README and API docs,
changelog entries, and commit bodies.

Name the mechanism, not a metaphor for it. Colloquial phrasing reads as
precision but carries less information: it gestures at what happened instead of
saying it.

| Instead of | Write |
|---|---|
| "blows up with a `SettingsError`" | "raises `SettingsError`" |
| "clobbers the value" | "overwrites the value" |
| "so keep it honest" | "so the entry stays current" |
| "fails loudly" | "fails", or "exits non-zero" |
| "under the hood" | name the layer actually doing the work |

Cut emphasis that adds nothing: "before this validator *ever* runs" says no more
than "before this validator runs".

Keep the words that are load-bearing, though. "A real value here **silently**
becomes the image tag" earns its adverb — the absence of any error is the whole
reason the surrounding check exists.

## Naming

The same standard applies to identifiers, and vague naming does more damage
there, because a reader cannot skip a name the way they can skip a comment.

- Name a test helper for the scenario it represents, not for the fact that it
  fails: `raise_access_denied`, not `_boom`.
- Do not alias a well-known framework fixture to a vaguer name. `monkeypatch`
  used directly reads as what it is; returning it as `clean_env` produces
  `clean_env.setattr(...)`, which describes neither the environment nor the
  patching.
- If an assertion refers to an identifier by name, the name should make the
  assertion self-explanatory without a comment.

## Accuracy

Docs describe what the code does now, not what it might do.

- Keep docs true to the code. When a change alters behavior, update the docs that
  describe it in the same change.
- Prefer under-claiming. Don't describe features, commands, or guarantees that
  aren't built — aspirational docs read as false the moment a reader tries them.
- When a documented claim turns out wrong, retract it with evidence — what you
  checked and where — rather than quietly leaving it in place.
