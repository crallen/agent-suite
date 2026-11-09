---
description: Implement an approved spec end to end — parallel implementer subagents across the task graph's frontier, landing on one integration branch, then a review against the spec
argument-hint: [spec file (optional; defaults to the most recent)]
disable-model-invocation: true
---
Load `spec-implementation` and follow it for the spec below; with no argument, use the most recent spec listed and confirm it with me first.

Run implementers as background subagents with worktree isolation: `@frontend-engineer` for UI tasks, a general-purpose subagent for the rest, whose brief also names `doc-templates` when the task is docs-only. A subagent starts without skills, so its brief must carry every one the skill names. Use `@code-reviewer` for the final review, passing the integration branch's base ref and the spec path; when the skill calls for a security review, run `@security-analyst` in parallel with the same inputs.

Recent specs:
!`find docs/specs -maxdepth 1 -name '*.md' 2>/dev/null | sort -r | head -5 | grep . || echo "(none)"`

Current repository state:
!`git status --short --branch 2>/dev/null || echo "(not a git repository)"`

$ARGUMENTS
