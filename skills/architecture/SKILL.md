---
description: Explore the codebase for architecture deepening opportunities, present candidates as a markdown report, then grill on the chosen one — writing CONTEXT.md and ADRs as decisions crystallize
argument-hint: [area or concern to focus on, optional]
context: fork
agent: architect
disable-model-invocation: true
---

Run an architecture review session. Use the Skill tool to load `architecture-review` for the full workflow. Explore the codebase for deepening opportunities, present candidates as a markdown report, then drop into a grilling loop on whichever the user picks. Write CONTEXT.md and ADR updates inline as decisions crystallize.

Current repository state:
!`git status --short 2>/dev/null || echo "(not a git repository)"`

Recent commits:
!`git log --oneline -10 2>/dev/null || echo "(no git history yet)"`

$ARGUMENTS
