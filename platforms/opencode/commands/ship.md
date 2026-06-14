---
description: Commit and push in one step — stages logical changes, creates Conventional Commits, then pushes to the remote
agent: git-manager
subtask: true
---

Review the current working tree, create appropriate Conventional Commit(s), and then push to the remote. If the working tree is clean with no unpushed commits, report that there is nothing to do and stop. If files are already staged, treat the staged set as the intended commit unless the user says otherwise. If nothing is staged, inspect unstaged and untracked changes, group them into logical commits, stage and commit each group. If the split is ambiguous, explain the proposed grouping and ask before committing. After all commits are created, push to the remote tracking branch (`git push`).

Repository state:
!`git status --short --branch`

Staged diff summary:
!`git diff --staged --stat`

Unstaged diff summary:
!`git diff --stat`

Recent commits:
!`git log --oneline -5`

$ARGUMENTS
