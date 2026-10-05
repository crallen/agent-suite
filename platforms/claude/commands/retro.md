---
description: Run a retrospective on a coding session and propose improvements to the agent's environment — pointers, checks, standards, steering files
argument-hint: [session to look back on (optional; defaults to this one)]
disable-model-invocation: true
---
Load `retro-methodology` and follow it for the session below, or for this conversation when none is named: proposals only, no edits until I pick.

Steering files in this repo:
!`for f in CLAUDE.md AGENTS.md CODING_STANDARDS.md CONTRIBUTING.md .claude/CLAUDE.md; do [ -f "$f" ] && echo "$f"; done | grep . || echo "(none found)"`

Commits from the session's likely range:
!`git log --oneline -10 2>/dev/null || echo "(no git history)"`

$ARGUMENTS
