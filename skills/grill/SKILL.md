---
description: Stress-test a plan with relentless one-at-a-time interrogation — sharpens domain language and writes CONTEXT.md / ADRs as decisions crystallize
argument-hint: [plan or topic to grill]
context: fork
agent: architect
disable-model-invocation: true
---

Run a grilling session on the plan or topic below. Use the Skill tool to load `grill-methodology` for the interrogation workflow and `domain-modeling` for the CONTEXT.md / ADR discipline. Ask one question at a time with your recommendation, explore the codebase before asking whenever it can answer the question, and write CONTEXT.md and ADR updates inline as decisions are resolved.

Current repository state:
!`git status --short 2>/dev/null || echo "(not a git repository)"`

Recent commits:
!`git log --oneline -10 2>/dev/null || echo "(no git history yet)"`

$ARGUMENTS
