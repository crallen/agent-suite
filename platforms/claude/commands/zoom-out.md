---
description: Go up a layer of abstraction when unfamiliar with an area — produces a map of relevant modules and callers using the project's domain vocabulary
argument-hint: [area or module]
disable-model-invocation: true
---

I don't know this area of code well. Go up a layer of abstraction. Read `CONTEXT.md` (or `CONTEXT-MAP.md`) at the repo root first if present, then give me a map of all the relevant modules and callers in its domain vocabulary.

Repository files:
!`{ git ls-files 2>/dev/null || ls; } | head -200`

$ARGUMENTS
