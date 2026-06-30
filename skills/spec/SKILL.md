---
description: Research a goal and produce a design spec with task checklist before any work begins
argument-hint: [goal]
context: fork
agent: architect
disable-model-invocation: true
---

Collaborate with the user to produce a design spec for the goal below. Start with the scope gate: if the request spans multiple independent subsystems, propose a decomposition before diving in. Otherwise, read relevant code first, then ask clarifying questions one at a time, propose 2-3 approaches, and present the design in stages. End with a markdown task checklist ready to execute.

The `spec-writing` skill is preloaded into your context; follow its full dialogue-to-spec workflow.

Current repository state:
!`git status --short`

Recent commits:
!`git log --oneline -10`

$ARGUMENTS
