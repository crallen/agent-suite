---
description: Review agents, skills, and commands for correctness, consistency, and best practices
argument-hint: [artifacts to focus on (optional)]
agent: agent-reviewer
context: fork
disable-model-invocation: true
---

Review the existing agents, skills, and slash commands for correctness, consistency, and adherence to conventions. Check structural correctness, cross-references, permission models, and quality.

If specific artifacts are named, focus the review there. Otherwise, audit the full suite.

Current agents:
!`ls ~/.claude/agents/ 2>/dev/null || echo "(none)"`

Current skills (reference skills and workflow skills / slash commands):
!`ls ~/.claude/skills/ 2>/dev/null || echo "(none)"`

$ARGUMENTS
