---
description: Run a security assessment on code, configuration, and dependencies
agent: security-analyst
subtask: true
---

Perform a security assessment.

If the arguments name a git ref (branch, tag, or commit, e.g. `main`) that resolves with `git rev-parse`, assess the changes since it: run `sh ~/.config/opencode/skills/code-review-checklist/scripts/review-diff.sh <ref>` and work from what it prints, relaying `REVIEW BLOCKED` or `(no changes since <ref>)` and stopping if it prints either. If specific files or directories are mentioned, focus the analysis there. Otherwise, use the diff below as the primary target — assess the changed code for vulnerabilities, then broaden to project-wide concerns (secrets in config, dependency manifests, attack surface) as relevant. The diff prefers staged changes, falls back to unstaged changes, and always includes any new untracked files. If the diff says `(no pending changes)`, assess the full codebase instead. If the diff says `REVIEW BLOCKED`, relay the message to the user and stop immediately.

Start by identifying the tech stack and mapping the attack surface, then analyze for vulnerabilities systematically. If dependency manifests are present, run available audit commands (npm audit, pip audit, etc.).

Current diff:
!`sh ~/.config/opencode/skills/code-review-checklist/scripts/review-diff.sh`

$ARGUMENTS
