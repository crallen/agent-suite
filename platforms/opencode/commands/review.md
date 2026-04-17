---
description: Review code for quality, security, and best practices
agent: code-reviewer
subtask: true
---

Review the following code for quality, security, performance, and maintainability issues.

If specific files are named, focus there. Otherwise, review the current working diff below: prefer the staged diff when present; fall back to the unstaged diff when nothing is staged.

Current review diff:
!`if git diff --staged --quiet; then git diff; else git diff --staged; fi`

$ARGUMENTS
