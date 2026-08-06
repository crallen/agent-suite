---
name: domain-modeling
description: Active domain-model maintenance — sharpen terminology, keep CONTEXT.md as the project glossary, record ADRs for hard-to-reverse decisions, and decide which terms earn their own type. Load when pinning down domain language, deciding whether a concept needs a type, recording an architectural decision, or when a session is changing the domain model; merely reading CONTEXT.md for vocabulary needs no skill.
---

# Domain Modeling

Actively build and sharpen the project's domain model: challenge terms, probe concept boundaries with concrete scenarios, and write glossary entries and decisions down the moment they crystallize. This is the *changing* discipline — merely reading `CONTEXT.md` for vocabulary is a one-line habit any task can do without this skill.

## Domain Files

Orient before the first term is challenged:

- `CONTEXT.md` at the repo root — the project's bounded context and glossary
- `CONTEXT-MAP.md` at the repo root — present in multi-context repos; lists all contexts and how they relate. Each context has its own `CONTEXT.md` (e.g. `src/ordering/CONTEXT.md`) and may keep its own `docs/adr/` for context-specific decisions; the root `docs/adr/` holds system-wide ones.
- `docs/adr/` — architectural decision records for past hard calls

If `CONTEXT-MAP.md` exists, read it first, then the relevant `CONTEXT.md` files. If only a root `CONTEXT.md` exists, read it. If neither exists, that's fine — create files lazily, only when there's something to write.

## Model-Sharpening Lenses

**Challenge the glossary** — when a term is used that the domain might own (an entity name, a process name, an action verb), check whether it matches the project's established language. If it drifts, surface the conflict and propose the canonical term.

**Sharpen fuzzy language** — words like "manage", "handle", "process", and "sync" hide decisions. When you encounter them, ask: what specifically happens? Who initiates it? What is the result?

**Probe concept boundaries with scenarios** — when domain relationships are on the table, invent edge cases that force precision about where one concept ends and another begins. "Is a cancelled Order still an Order?" "What does a partial refund do to the Invoice?"

**Cross-reference domain claims with code** — when someone states how the domain works, check whether the code agrees. Surface contradictions: "The code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

## Updating CONTEXT.md

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
- CONTEXT.md is a glossary and nothing else — no implementation details, specs, or scratch notes. Decisions belong in ADRs.
- Be opinionated — when multiple words describe the same concept, pick the best one and list the rest under `_Avoid_`.
- Keep definitions tight — one or two sentences max. Define what it IS, not what it does.
- Group under subheadings only when natural clusters emerge; a flat list is fine otherwise.
- For multi-context repos: update only the context file relevant to the current session. If a new context is warranted, add it to `CONTEXT-MAP.md` and create its file.

**Creating CONTEXT.md lazily**: if no CONTEXT.md exists yet, create `CONTEXT.md` at the repo root when the first term is resolved. Start from the template above, naming the context after the primary domain (e.g., `# Orders` or `# Billing`).

## Terms That Earn a Type

A glossary entry names a concept; a type makes the code agree. When a term is resolved, ask once whether it should exist in the type system — but hold the line, because wrapping every noun is the **Speculative Generality** that `coding-guardrails` warns against.

A term earns its own type when all three hold:

1. **It carries a rule a primitive cannot** — a non-empty constraint, a format, a range, a currency that must not be assumed.
2. **Mixing it up would be a real bug** — two `string` parameters that must never be swapped, two `int` amounts in different units.
3. **It crosses a seam** — the concept is passed between modules, so the compiler has somewhere useful to object.

If only one or two hold, the primitive is fine. Suspecting a type is already overdue in existing code is the reactive case, and the **Primitive Obsession** entry in `code-review-checklist` owns it.

### How far the type system will take you

Say what the language actually enforces rather than promising more:

| Language | Enforcement available |
|---|---|
| Rust | Strong. Newtypes resist coercion, enums are real sum types with exhaustive `match`, and private fields plus a fallible constructor make validity structural. |
| TypeScript, Java, C# | Good for sum types (discriminated unions, sealed hierarchies). Branded primitives work but are a convention the boundary can erase. |
| Go | Naming, plus a validated constructor by convention. A named type is distinct but cheaply converted, there are no sum types or exhaustiveness checks, and **the zero value is always constructible** — so validity is enforced at the boundary, not by the type. |
| Python | Documentation. `NewType` is erased at runtime; `frozen=True` dataclasses carry intent, not a guarantee. |

"Make illegal states unrepresentable" is achievable in Rust and largely is not in Go. Where the type system won't carry the rule, put it in one validated constructor and say in CONTEXT.md what the term guarantees — the glossary is then the contract the compiler can't express.

## Writing ADRs

Offer to write an ADR when all three of these are true:

1. **Hard to reverse** — changing this decision later carries meaningful cost.
2. **Surprising without context** — a future reader will see the code and wonder why it was done this way.
3. **A real trade-off** — there were genuine alternatives and you picked one for specific reasons.

If only one or two of these apply, skip the ADR. Most decisions don't need one.

**File location**: `docs/adr/` using sequential numbering: `0001-slug.md`, `0002-slug.md`. Create the directory lazily — only when the first ADR is needed. In multi-context repos, context-specific decisions go in that context's `docs/adr/`; system-wide ones at the root.

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

- **Deferring doc writes.** Write CONTEXT.md and ADR updates the moment a term or decision is resolved. Deferred documentation doesn't happen.
- **Glossary inflation.** Don't add every noun to CONTEXT.md. Only project-specific domain terms belong there.
- **ADR for every decision.** The three-part test is a gate. Most decisions don't clear it.
- **A type per noun.** The three-part test above is a gate too. A wrapper that carries no rule and crosses no seam is indirection with a domain name on it.
- **Promising enforcement the language can't give.** Claiming a Go named type makes a state unrepresentable is worse than saying nothing — it retires a boundary check that was doing the real work.
