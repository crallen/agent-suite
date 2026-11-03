---
description: Commit and push in one step — stages logical changes, creates Conventional Commits, then pushes to the remote
agent: git-manager
subtask: true
---

Review the current working tree, create appropriate Conventional Commit(s), choosing what to commit as `git-conventions` describes, and then push to the remote tracking branch (`git push`).

Repository state:
!`git status --short --branch`

Staged diff summary:
!`git diff --staged --stat`

Unstaged diff summary:
!`git diff --stat`

Recent commits:
!`git log --oneline -5`

$ARGUMENTS
