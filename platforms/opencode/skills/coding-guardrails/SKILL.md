---
name: coding-guardrails
description: "Cross-cutting execution guardrails for coding tasks: surface assumptions, prefer simple solutions, make surgical changes, define verifiable success criteria, shape code with sound structure/error/safety defaults, and prefer a clear name over a comment that explains it"
---

# Coding Guardrails

Load this skill for implementation work: writing features, fixing bugs, refactoring, reviewing diffs, or changing configuration. It captures four behavioral guardrails that keep work grounded, simple, scoped, and easy to verify.

These guardrails bias toward caution over speed. Apply them proportionally — a one-line typo fix does not need a ceremony-heavy process.

## The Four Guardrails

| Guardrail | Prevents | Core question |
|---|---|---|
| Think before coding | Silent assumptions, hidden confusion, wrong tradeoffs | What am I assuming, and do I need to ask first? |
| Simplicity first | Overengineering, speculative abstractions, bloated APIs | What is the smallest thing that solves today's problem? |
| Surgical changes | Drive-by refactors, style churn, unrelated cleanup | Does every changed line trace back to the request? |
| Goal-driven execution | Vague progress, weak validation, unproven fixes | How will I prove this worked? |

## 1. Think Before Coding

Do not silently pick an interpretation when the request is ambiguous.

- State assumptions explicitly.
- If multiple readings lead to meaningfully different implementations, surface them.
- If a simpler path would satisfy the goal, say so.
- If you are confused, stop and ask instead of guessing.

Ask instead of guessing when scope, data shape, UX, security, performance, or policy choices are unclear.

## 2. Simplicity First

Understand the real constraint, then fight for the smallest model that makes the correct behavior unsurprising.

- No features beyond what was asked.
- No abstraction layer unless something real varies across it — a second implementation, or a seam a test genuinely needs.
- No configurability or "future-proofing" nobody requested.
- No ceremony without payoff: a builder for a one- or two-field struct, generics with a single caller, or dependencies and feature flags pulled in ahead of need.
- No complex failure handling for scenarios with no evidence they matter.
- If 200 lines could be 50 without losing clarity, simplify.

Simplicity governs *ceremony*, not *architecture*. Build the system properly — reach for the seam, port, or layer when it earns its keep; abstraction with a payoff is not speculative. Strip only the indirection that buys nothing. When a seam's payoff is unclear, `architecture-review` holds the test: one adapter is a hypothetical seam, two is a real one.

### Simplicity Test

Ask: **Would a strong senior engineer call this overcomplicated for the stated goal?** If yes, simplify before continuing.

## 3. Surgical Changes

Touch only what the request requires. Keep the diff narrow and local.

- Do not refactor adjacent code just because you noticed it.
- Do not reformat files, rename symbols, or rewrite comments unless your change requires it.
- Match the existing style and conventions, even if you would prefer a different style.
- Clean up imports, variables, and functions only when **your** change made them unused.
- If you notice unrelated issues, mention them separately instead of fixing them in the same change.

These bound your **reach** — which code you may touch — not the **shape** of code the request already puts you inside. There, write what the change actually needs rather than mirroring the surrounding complexity; that something is already complicated is not a reason to add to it. This is about structure, not style: the conventions above still hold. Reaching outside the request to simplify something you merely noticed is still a drive-by refactor.

### Diff Discipline Checklist

- [ ] Every changed line traces directly to the user's request or an approved spec.
- [ ] Adjacent edits are required for correctness, tests, or build health.
- [ ] Comments or docs changed only because the implementation changed their truth.
- [ ] Existing dead code stays unless the user asked to remove it.
- [ ] Style drift stayed out of the diff.

## 4. Goal-Driven Execution

Translate work into explicit proof, not vague motion.

- Define success criteria before making non-trivial changes.
- Prefer failing tests or repeatable reproductions before bug fixes.
- For new features, decide what checks will prove success before coding.
- For refactors, establish behavior baselines and confirm they still hold afterward.
- Loop until verified; do not stop at "the code looks right."

### Plan Template

```markdown
1. [Change]
   verify: [test, command, manual check, or observable signal]

2. [Change]
   verify: [test, command, manual check, or observable signal]
```

## Operating Loops

| Work type | Loop |
|---|---|
| Bug fix | Reproduce → minimal fix → regression check |
| New feature | Clarify → smallest useful slice → verify |
| Refactor | Capture behavior → change in steps → confirm behavior holds |

## Structure, Errors, and Safety

Defaults for how code is shaped — starting points, not straitjackets. Match the repo, and reach for `architecture-review` (structure) or `backend-patterns` (layer boundaries) when a decision needs depth.

- **Thin composition root.** `main`/entry wires dependencies and delegates to a `run()`-style function. Business logic does not live in the entrypoint.
- **Modules as facades.** Expose a curated public surface; keep the parts a caller doesn't need private. The public API is the seam, not the internals.
- **Errors carry context and cause.** Wrap as they cross a boundary ("failed to X"), chained to the source; don't swallow. Model the distinctions callers act on — retriable vs fatal, the status you'll return — and no error types nothing inspects.
- **Guard clauses.** Handle the failing case and return early; keep the happy path flat and unindented.
- **No panics on recoverable paths.** Propagate errors instead. Reserve `panic`/`unwrap`/`expect`-style aborts for provable startup invariants (with a message) or tests.

## Naming and Comments

Both get read far more often than they get written, so a vague one charges every
later reader. Prefer a name that makes the code self-explanatory over a comment
that explains it. Where a comment earns its place, name the mechanism rather than
a metaphor for it — "raises `SettingsError`", not "blows up".

`doc-templates` holds the full register and naming rules. Load it when writing
comments, docstrings, or identifiers a human will read.

## Anti-Patterns

- Silent assumption
- Speculative architecture (a seam nothing varies across)
- Panic on a recoverable path
- Drive-by refactor
- Vague success criteria
- Comment standing in for a name that could have been clearer
