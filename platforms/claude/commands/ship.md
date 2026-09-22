---
description: Commit and push in one step — stages logical changes, creates Conventional Commit(s), then pushes to the remote
argument-hint: [instructions (optional)]
disable-model-invocation: true
---
Load the `git-conventions` skill and follow it.

Same as `/commit`: if the working tree is clean with no unpushed commits, report that there is nothing to do and stop; treat a staged set as the intended commit; otherwise group unstaged and untracked changes into logical commits, asking first if the split is ambiguous. Then push to the remote tracking branch.

Repository state:
!`git status --short --branch`

Staged diff summary:
!`git diff --staged --stat`

Unstaged diff summary:
!`git diff --stat`

Recent commits:
!`git log --oneline -5`

$ARGUMENTS
