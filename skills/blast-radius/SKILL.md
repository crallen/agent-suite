---
description: Find what a change breaks beyond its obvious callers, then prove the one fact that makes it safe by running code rather than asserting it. A pre-commit impact pass — trace downstream effects, rank each safety claim by how it was verified. Load before shipping a risky change, or on /blast-radius against a diff or change.
argument-hint: [the change or diff to assess]
---

# Blast Radius

Map what a change could break elsewhere — past the callers grep hands you — and prove the claim that it is safe. This is a pass you run *before* committing a risky change, not a review rubric; `code-review-checklist` owns the rubric.

## The core discipline

**Words are where you start, not what you ship.** A convincing writeup that a change is safe is worth nothing until code confirms it. Distrust your own prose — the more persuasive it reads, the more you should want to run it.

## Verification ladder

Rank each safety claim by how it was checked, and push the *critical* one as high as the situation allows:

1. **Asserted** — "this is fine." No evidence. Never shippable for a load-bearing claim.
2. **Sourced** — points at the code that makes it true.
3. **Reasoned** — walks through why the failure cannot occur.
4. **Executed** — a script calls the real code and shows the result.
5. **Reproduced** — the behavior is confirmed in the running app.

Any load-bearing safety claim that does not reach step 4 ships marked **unproven**, not settled.

## What to trace

- Direct callers (grep, LSP), then *their* callers — the effect that propagates two hops out.
- Contracts you changed: signatures, return shapes, error types, nullability, ordering, timing.
- Implicit consumers: serialized data, persisted state, API responses, emitted events, config keys, env vars.
- Shared state and invariants a caller relied on but never declared.

## Output

- **Changed** — what the diff actually does.
- **Critical safety fact** — the one thing that must hold, verified to its highest feasible rung (name the rung).
- **Genuine risks** — each with likelihood and impact, not a list of everything conceivable.
- **Checked and cleared** — what you ruled out, so the reader knows the search was real.
- **Test** — the smallest test that catches a real regression from this change.
