---
description: Create or modify a Claude Code agent, skill, or slash command
argument-hint: [what to create or change]
context: fork
disable-model-invocation: true
---

Load the `agent-authoring` and `skill-design` skills and read `agent-authoring/reference/claude.md`, then create or modify the requested agent, skill, or slash command.

Current agents:
!`ls ~/.claude/agents/ 2>/dev/null || echo "(none)"`

Current skills:
!`for d in ~/.claude/skills/*/; do [ -f "$d/SKILL.md" ] && basename "$d"; done 2>/dev/null || echo "(none)"`

Current commands:
!`ls ~/.claude/commands/ 2>/dev/null || echo "(none)"`

$ARGUMENTS
