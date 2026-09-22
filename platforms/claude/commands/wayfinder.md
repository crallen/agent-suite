---
description: Chart a large effort as a map of decision tickets in the repo, then resolve one decision per session until the way is clear
argument-hint: [loose idea, or a path to an existing map]
disable-model-invocation: true
---
Load `wayfinder-methodology` and follow it for the effort below: decisions only, no implementation.

Pick the mode from the argument: a path or effort name that matches an existing map means **work through the map**, anything else means **chart** a new one. If the argument is empty, list the maps below and ask which to work. Before charting, check the effort really outlives one session; if the way is already clear, say so and recommend `/spec` instead.

Existing maps:
!`find docs/wayfinder -maxdepth 1 -name '*.md' 2>/dev/null | head -10 || echo "(none yet)"`

Current repository state:
!`git status --short 2>/dev/null || echo "(not a git repository)"`

$ARGUMENTS
