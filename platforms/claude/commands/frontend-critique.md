---
description: Critique frontend UX and visual direction, then suggest targeted improvements
argument-hint: [surface to critique]
agent: frontend-auditor
context: fork
disable-model-invocation: true
---

Critique the requested frontend surface without editing files. Focus on task clarity, hierarchy, interaction tone, copy quality, and whether the UI feels product-specific rather than generic. If implementation is needed afterward, recommend `/frontend`.

Use `frontend-patterns` as a router. For this workflow, prefer `frontend-patterns/reference/design-direction.md`, `frontend-patterns/reference/anti-patterns.md`, and any accessibility or architecture reference that materially affects the critique. Separate must-fix issues from optional polish.

$ARGUMENTS
