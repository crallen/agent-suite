---
description: Stage logical changes when needed and create well-formed Conventional Commits
agent: tech-lead
subtask: true
---

Review the current working tree and create appropriate Conventional Commit(s). If the working tree is clean, report that there is nothing to commit and stop. If files are already staged, treat the staged set as the intended commit unless the user says otherwise. If nothing is staged, inspect unstaged and untracked changes, group them into logical commits, stage the current group, and commit. If the split is ambiguous, explain the proposed grouping and ask before committing.

Repository state:
!`git status --short --branch`

Staged diff summary:
!`git diff --staged --stat`

Unstaged diff summary:
!`git diff --stat`

Recent commits:
!`git log --oneline -5`

$ARGUMENTS
