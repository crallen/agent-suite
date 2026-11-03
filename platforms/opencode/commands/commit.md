---
description: Stage logical changes when needed and create well-formed Conventional Commits
agent: git-manager
subtask: true
---

Review the current working tree and create appropriate Conventional Commit(s), choosing what to commit as `git-conventions` describes.

Repository state:
!`git status --short --branch`

Staged diff summary:
!`git diff --staged --stat`

Unstaged diff summary:
!`git diff --stat`

Recent commits:
!`git log --oneline -5`

$ARGUMENTS
