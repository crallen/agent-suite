---
description: Create or modify a Claude Code agent, skill, or slash command
argument-hint: [what to create or change]
disable-model-invocation: true
---

Use the `@agent-builder` subagent to create or modify a Claude Code agent, skill, or slash command. Follow the established schemas and conventions.

Current agents:
!`ls ~/.claude/agents/ 2>/dev/null || echo "(none)"`

Current skills:
!`ls ~/.claude/skills/ 2>/dev/null || echo "(none)"`

Current commands:
!`ls ~/.claude/commands/ 2>/dev/null || echo "(none)"`

$ARGUMENTS
