---
description: Review agents, skills, and commands for correctness, consistency, and best practices
agent: agent-reviewer
subtask: true
---

Review the existing agents, skills, and slash commands for correctness, consistency, and adherence to conventions. Check structural correctness, cross-references, permission models, and quality.

If specific artifacts are named, focus the review there. Otherwise, audit the full suite.

Current agents:
!`if [ -d "./agent" ]; then ls "./agent"; elif [ -d "./opencode/.config/opencode/agent" ]; then ls "./opencode/.config/opencode/agent"; else ls ~/.config/opencode/agent; fi`

Current skills:
!`if [ -d "./skills" ]; then ls "./skills"; elif [ -d "./opencode/.config/opencode/skills" ]; then ls "./opencode/.config/opencode/skills"; else ls ~/.config/opencode/skills; fi`

Current commands:
!`if [ -d "./commands" ]; then ls "./commands"; elif [ -d "./opencode/.config/opencode/commands" ]; then ls "./opencode/.config/opencode/commands"; else ls ~/.config/opencode/commands; fi`

$ARGUMENTS
