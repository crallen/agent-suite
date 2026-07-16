---
name: architecture-review
description: Architecture deepening workflow — finds shallow modules, proposes refactors that increase depth (leverage + locality), presents candidates as a markdown report, then grills on the chosen one. Integrates with CONTEXT.md and ADRs.
---

# Architecture Review

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

Use the vocabulary in `architecture-review/reference/vocabulary.md` exactly in every suggestion. Read it first. Consistent language is the whole point.

## Process

### 1. Orient

Read `architecture-review/reference/vocabulary.md` for the shared architectural language.

If `CONTEXT.md` exists at the repo root (or `CONTEXT-MAP.md` for multi-context repos), read it — use domain vocabulary throughout the review. Check `docs/adr/` for any decisions that constrain what you can suggest.

### 2. Explore

Walk the codebase. Don't follow rigid heuristics — explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? "Yes, concentrates" is the signal.

### 3. Present Candidates

Write a markdown report. For each candidate:

- **Files** — which files / modules are involved
- **Problem** — why the current architecture causes friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and how tests would improve
- **Recommendation strength** — `Strong`, `Worth exploring`, or `Speculative`

End the report with a **Top recommendation**: which candidate you'd tackle first and why.

**Use CONTEXT.md vocabulary for the domain, and `vocabulary.md` terms for the architecture.** If CONTEXT.md defines "Order," talk about "the Order intake module" — not "the FooBarHandler."

**ADR conflicts:** if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting. Mark it clearly: *"contradicts ADR-0007 — but worth reopening because…"* Don't list every theoretical refactor an ADR forbids.

Do NOT propose interfaces yet. After presenting, ask: "Which of these would you like to explore?"

### 4. Grilling Loop

Once the user picks a candidate, drop into a grilling conversation. Walk the design tree with them — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Read `architecture-review/reference/deepening.md` to classify the candidate's dependencies and determine the right testing strategy across the seam.

Side effects happen inline as decisions crystallize — follow `domain-modeling` for the CONTEXT.md and ADR formats:

- **Naming a deepened module after a concept not in CONTEXT.md?** Add the term to CONTEXT.md.
- **Sharpening a fuzzy term?** Update CONTEXT.md right there.
- **User rejects a candidate with a load-bearing reason?** Offer an ADR: *"Want me to record this so future architecture reviews don't re-suggest it?"* Only when the reason would actually help a future explorer — skip ephemeral reasons ("not worth it right now") and self-evident ones.
- **Want to explore alternative interfaces for the deepened module?** Read `architecture-review/reference/interface-design.md` for the parallel sub-agent pattern.
