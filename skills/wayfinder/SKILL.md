---
description: Chart a large effort as a map of decision tickets in the repo, then resolve one decision per session until the way is clear
argument-hint: [loose idea, or a path to an existing map]
---

Wayfind the effort below, operating as the architect: decisions only, no implementation. Use the Skill tool to load `wayfinder-methodology` for the map format, ticket types, and both workflows. This runs inline in the main conversation — grilling and prototype tickets are worked *with* the user, and a forked subagent cannot pause for their answers.

Pick the mode from the argument: a path or effort name that matches an existing map means **work through the map**, anything else means **chart** a new one. If the argument is empty, list the maps below and ask which to work. Before charting, check the effort really outlives one session — if the way to the destination is already clear, say so and recommend `/spec` instead of charting a map.

Existing maps:
!`find docs/wayfinder -maxdepth 1 -name '*.md' 2>/dev/null | head -10 || echo "(none yet)"`

Current repository state:
!`git status --short 2>/dev/null || echo "(not a git repository)"`

$ARGUMENTS
