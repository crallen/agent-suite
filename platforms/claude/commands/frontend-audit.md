---
description: Audit frontend quality, states, responsiveness, and anti-patterns without editing files
argument-hint: [surface to audit]
agent: frontend-auditor
context: fork
disable-model-invocation: true
---

Audit the requested frontend surface without editing files. Focus on screen intent, hierarchy, states, accessibility, responsiveness, and anti-patterns. If implementation is needed afterward, recommend `/frontend`.

Use `frontend-patterns` as a router. For this workflow, prefer `frontend-patterns/reference/anti-patterns.md`, `frontend-patterns/reference/design-direction.md`, and `frontend-patterns/reference/verification.md`. Report concrete findings, better directions, and what still needs browser/manual validation.

$ARGUMENTS
