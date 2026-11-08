---
description: Stage logical changes when needed and create well-formed Conventional Commits
argument-hint: [instructions (optional)]
disable-model-invocation: true
---

Load the `git-conventions` skill and follow it.

Review the current working tree and create appropriate Conventional Commit(s), choosing what to commit as the skill describes.

Repository state:
!`git status --short --branch 2>/dev/null || echo "(not a git repository)"`

Staged diff summary:
!`git diff --staged --stat 2>/dev/null || echo "(no staged diff)"`

Unstaged diff summary:
!`git diff --stat 2>/dev/null || echo "(no unstaged diff)"`

Recent commits:
!`git log --oneline -5 2>/dev/null || echo "(no commits yet)"`

$ARGUMENTS
