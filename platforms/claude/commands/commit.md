---
description: Stage logical changes when needed and create well-formed Conventional Commits
argument-hint: [instructions (optional)]
disable-model-invocation: true
---

Load the `git-conventions` skill and follow it.

Review the current working tree and create appropriate Conventional Commit(s), choosing what to commit as the skill describes.

Repository state:
!`git status --short --branch`

Staged diff summary:
!`git diff --staged --stat`

Unstaged diff summary:
!`git diff --stat`

Recent commits:
!`git log --oneline -5`

$ARGUMENTS
