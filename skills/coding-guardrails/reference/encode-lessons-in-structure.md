# Encode Lessons in Structure

When you catch yourself writing the same instruction a second time, or notice a recurring correction, encode the rule as a mechanism — a type, lint, metadata flag, runtime check, or script — instead of more text. Textual instructions are easy to miss: they require every future reader to notice, remember, and comply. A mechanism enforces itself.

## The move

1. Notice the repeat — the instruction given twice, the same review comment again, the correction that keeps recurring.
2. Ask what mechanism could make the rule structural instead of remembered.
3. Encode it, then delete the prose the mechanism replaces.

## Pick the strongest rung

When several mechanisms fit, choose the strongest the situation allows — each rung fails earlier and harder than the one below:

1. **Unrepresentable state** — the mistake cannot compile (see `coding-guardrails/reference/type-system-discipline.md`).
2. **Lint rule or banned API** — the mistake fails CI.
3. **Canonical helper** — the right way is the easy, obvious call, so the wrong way isn't reached for.
4. **Runtime check** — the mistake fails loudly at the boundary where it occurs.

Prose is the rung below all of these — the fallback when none fit, not the default.

## Anti-patterns

- **Acknowledging without recording** — "good catch, I'll remember" remembers nothing.
- **Recording without routing** — a note no mechanism enforces is prose by another name.
- **Fixing the instance, not the pattern** — patch the one occurrence and the class recurs. Generalize the underlying rule.
