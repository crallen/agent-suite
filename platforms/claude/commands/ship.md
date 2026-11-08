---
description: Commit and push in one step — stages logical changes, creates Conventional Commit(s), then pushes to the remote
argument-hint: [instructions (optional)]
disable-model-invocation: true
---
Load the `git-conventions` skill and follow it.

Create the commit(s), choosing what to commit as the skill describes for a task that also pushes. Then push to the remote tracking branch.

Repository state:
!`git status --short --branch 2>/dev/null || echo "(not a git repository)"`

Staged diff summary:
!`git diff --staged --stat 2>/dev/null || echo "(no staged diff)"`

Unstaged diff summary:
!`git diff --stat 2>/dev/null || echo "(no unstaged diff)"`

Recent commits:
!`git log --oneline -5 2>/dev/null || echo "(no commits yet)"`

$ARGUMENTS
