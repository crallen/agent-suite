---
description: Create or modify a Claude Code agent, skill, or slash command
argument-hint: [what to create or change]
context: fork
disable-model-invocation: true
---

Load the `agent-authoring` and `skill-design` skills, then create or modify a Claude Code agent, skill, or slash command following the established schemas and conventions.

Current agents:
!`ls ~/.claude/agents/ 2>/dev/null || echo "(none)"`

Current skills:
!`ls ~/.claude/skills/ 2>/dev/null || echo "(none)"`

Current commands:
!`ls ~/.claude/commands/ 2>/dev/null || echo "(none)"`

$ARGUMENTS
