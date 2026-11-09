---
description: Critique frontend UX and visual direction, then suggest targeted improvements
argument-hint: [surface to critique]
agent: frontend-engineer
context: fork
disable-model-invocation: true
---
Report only; do not edit repository files.

Critique the requested frontend surface: task clarity, hierarchy, interaction tone, copy quality, and whether the UI feels product-specific rather than generic. Prefer `frontend-patterns/reference/anti-patterns.md`, plus any accessibility or architecture reference that materially affects the critique. If implementation is needed afterward, recommend `/frontend`.

Report in this format:

```markdown
## Summary

## What Works

## Must-Fix
| Area | Issue | Why it matters | Suggested improvement |
|---|---|---|---|

## Optional Polish
| Area | Opportunity | Suggested improvement |
|---|---|---|
```

$ARGUMENTS
