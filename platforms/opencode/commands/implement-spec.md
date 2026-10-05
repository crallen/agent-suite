---
description: Implement an approved spec end to end — parallel implementer subagents across the task graph's frontier, landing on one integration branch, then a review against the spec
agent: tech-lead
---

Load the `spec-implementation` skill and follow it for the spec below; with no argument, use the most recent spec listed and confirm it with the user first.

Delegate each frontier task to the specialist that fits it (`@backend-engineer`, `@database-specialist`, `@frontend-engineer`), spawning the frontier in parallel. Create each task's worktree with `git worktree add` before delegating and name its path in the brief, along with the skills to load. Use `@code-reviewer` for the final review, passing the integration branch's base ref and the spec path.

Recent specs:
!`find docs/specs -maxdepth 1 -name '*.md' 2>/dev/null | sort -r | head -5 | grep . || echo "(none)"`

Current repository state:
!`git status --short --branch 2>/dev/null || echo "(not a git repository)"`

$ARGUMENTS
