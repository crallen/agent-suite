---
description: Create or modify an OpenCode agent, skill, or slash command
agent: agent-builder
subtask: true
---

Create or modify an OpenCode agent, skill, or slash command. Follow the established schemas and conventions.

Current agents:
!`if [ -d "./agent" ]; then ls "./agent"; elif [ -d "./opencode/.config/opencode/agent" ]; then ls "./opencode/.config/opencode/agent"; else ls ~/.config/opencode/agent; fi`

Current skills:
!`if [ -d "./skills" ]; then ls "./skills"; elif [ -d "./opencode/.config/opencode/skills" ]; then ls "./opencode/.config/opencode/skills"; else ls ~/.config/opencode/skills; fi`

Current commands:
!`if [ -d "./commands" ]; then ls "./commands"; elif [ -d "./opencode/.config/opencode/commands" ]; then ls "./opencode/.config/opencode/commands"; else ls ~/.config/opencode/commands; fi`

$ARGUMENTS
