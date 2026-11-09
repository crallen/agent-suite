---
description: Audit frontend quality, states, responsiveness, and anti-patterns without editing files
argument-hint: [surface to audit]
agent: frontend-engineer
context: fork
disable-model-invocation: true
---
Report only; do not edit repository files.

Audit the requested frontend surface: screen intent, hierarchy, states, accessibility, responsiveness, and anti-patterns. Prefer `frontend-patterns/reference/anti-patterns.md`. If implementation is needed afterward, recommend `/frontend`.

Report in this format:

```markdown
## Summary

## Findings
| Area | Issue | Impact | Better direction |
|---|---|---|---|

## Validation Gaps

## Recommendations
```

$ARGUMENTS
