---
description: Research a goal and produce a design spec with task checklist before any work begins
argument-hint: [goal]
---

Collaborate with the user to produce a design spec for the goal below. Start with the scope gate: if the request spans multiple independent subsystems, propose a decomposition before diving in. Otherwise, read relevant code first, then ask clarifying questions one at a time, propose 2-3 approaches, and present the design in stages. End with a markdown task checklist ready to execute.

Operate as the architect: collaborative design dialogue only, no implementation. Use the Skill tool to load `spec-writing` and follow its full dialogue-to-spec workflow. This runs inline in the main conversation — a forked subagent cannot pause for the user's answers, and this workflow is nothing but questions.

Current repository state:
!`git status --short 2>/dev/null || echo "(not a git repository)"`

Recent commits:
!`git log --oneline -10 2>/dev/null || echo "(no git history yet)"`

$ARGUMENTS
