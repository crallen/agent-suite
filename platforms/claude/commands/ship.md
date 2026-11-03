---
description: Commit and push in one step — stages logical changes, creates Conventional Commit(s), then pushes to the remote
argument-hint: [instructions (optional)]
disable-model-invocation: true
---
Load the `git-conventions` skill and follow it.

Create the commit(s), choosing what to commit as the skill describes for a task that also pushes. Then push to the remote tracking branch.

Repository state:
!`git status --short --branch`

Staged diff summary:
!`git diff --staged --stat`

Unstaged diff summary:
!`git diff --stat`

Recent commits:
!`git log --oneline -5`

$ARGUMENTS
