---
description: Structured interrogation workflow for stress-testing a plan — one question at a time, domain-language sharpening, codebase cross-referencing, and inline writes to CONTEXT.md and ADRs as decisions crystallize. Load when the user wants to grill a plan or design.
---

# Grill Methodology

This skill drives a structured grilling session: a sustained, Socratic interrogation of a plan or design that challenges every assumption, resolves terminology, and anchors decisions in the real codebase. Load it when the user wants to stress-test a plan before or after speccing it — or when domain language is muddled and needs to be nailed down.

## Interrogation Workflow

Work through the plan branch by branch, resolving dependencies between decisions one at a time. Do not move to the next question until the current one is settled.

**For each question:**
1. **Explore first** — if the codebase can answer it, read the relevant files before asking. Prefer evidence over opinion.
2. **State your recommendation** — do not ask a neutral question. Pose the question, then give your best answer and the reasoning behind it.
3. **Wait for feedback** — one question per message, always. No batching.
4. **Anchor the answer** — once agreed, note it as a resolved decision before moving on.

Keep going until the entire plan has been walked down. The goal is zero unresolved branches.

## Session Behaviors

Apply these lenses throughout the session:

**Challenge the glossary** — when a term is used that the domain might own (an entity name, a process name, an action verb), check whether it matches the project's established language. If it drifts, surface the conflict and propose the canonical term.

**Sharpen fuzzy language** — words like "manage", "handle", "process", and "sync" hide decisions. When you encounter them, ask: what specifically happens? Who initiates it? What is the result?

**Stress-test with concrete scenarios** — for each significant decision, run at least one edge case through it. "What happens when X is empty?", "What if two users do this simultaneously?", "What does the caller do if this fails?" Vague designs collapse under concrete scenarios.

**Cross-reference with code** — when a design refers to an existing module, pattern, or entity, read it. Confirm that the plan is consistent with what actually exists, not what someone remembers existing.

## Domain Awareness

Before the first question, orient yourself to the project's documented domain model.

Look for:
- `CONTEXT.md` at the repo root — the project's bounded context and glossary
- `CONTEXT-MAP.md` at the repo root — present in multi-context repos; lists all contexts and how they relate
- `docs/adr/` — architectural decision records for past hard calls

If `CONTEXT-MAP.md` exists, read it first to understand the context landscape, then read the relevant `CONTEXT.md` files. If only a root `CONTEXT.md` exists, read it. If neither exists, that's fine — create one lazily when the first term is resolved.

## Live Documentation

As decisions crystallize during the session, write them into the project's documentation immediately — do not defer to the end.

### Updating CONTEXT.md

Add or update glossary terms as soon as their definitions are agreed. Do not wait for the session to finish.

**When to update**: a term is used that belongs to this domain's language and either (a) doesn't exist in CONTEXT.md yet, or (b) has a definition that no longer matches how it's being used.

**When not to update**: general programming concepts (timeouts, error types, retry logic) don't belong in CONTEXT.md even if the project uses them heavily. Only terms specific to this problem domain.

**File structure:**

```markdown
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
A request from a customer to deliver specific items at a price.
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

**Rules for CONTEXT.md entries:**
- Be opinionated — when multiple words describe the same concept, pick the best one and list the rest under `_Avoid_`.
- Keep definitions tight — one or two sentences max. Define what it IS, not what it does.
- Group under subheadings only when natural clusters emerge; a flat list is fine otherwise.
- For multi-context repos: update only the context file relevant to the current session. If a new context is warranted, add it to `CONTEXT-MAP.md` and create its file.

**Creating CONTEXT.md lazily**: if no CONTEXT.md exists yet, create `CONTEXT.md` at the repo root when the first term is resolved. Start from the template above, naming the context after the primary domain (e.g., `# Orders` or `# Billing`).

### Writing ADRs

Offer to write an ADR when all three of these are true:

1. **Hard to reverse** — changing this decision later carries meaningful cost.
2. **Surprising without context** — a future reader will see the code and wonder why it was done this way.
3. **A real trade-off** — there were genuine alternatives and you picked one for specific reasons.

If only one or two of these apply, skip the ADR. Most decisions don't need one.

**File location**: `docs/adr/` using sequential numbering: `0001-slug.md`, `0002-slug.md`. Create the directory lazily — only when the first ADR is needed.

**ADR format:**

```markdown
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

That's it. An ADR can be a single paragraph. The value is in recording *that* a decision was made and *why* — not in filling out sections.

**Optional ADR sections** (only when they add genuine value — most ADRs won't need them):
- **Status** (`proposed | accepted | deprecated | superseded by ADR-NNNN`) — useful when decisions are revisited
- **Considered Options** — only when the rejected alternatives are worth remembering
- **Consequences** — only when non-obvious downstream effects need to be called out

Before writing an ADR, confirm with the user. Example:

> "This feels like a decision worth recording. Want me to write ADR-0001 for it?"

## Anti-Patterns

- **Batching questions.** One at a time, always. Batching lets the user skim past the hard ones.
- **Neutral questions with no recommendation.** Every question should include your best answer. You're stress-testing, not surveying.
- **Deferring doc writes.** Write CONTEXT.md and ADR updates inline. Deferred documentation doesn't happen.
- **Glossary inflation.** Don't add every noun to CONTEXT.md. Only project-specific domain terms belong there.
- **ADR for every decision.** The three-part test is a gate. Most decisions don't clear it.
- **Moving on with unresolved ambiguity.** If a question reveals a contradiction or gap, stay on it until it's resolved.
