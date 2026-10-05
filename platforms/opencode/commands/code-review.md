---
description: Review code for quality, security, and best practices — pending changes, changes since a base ref, or the full codebase when the tree is clean
agent: code-reviewer
subtask: true
---

Review code for quality, security, performance, and maintainability issues.

If the diff below says `REVIEW BLOCKED`, relay the message to the user and stop immediately.

Otherwise, pick the review target in this order:

1. **Base ref** — if the arguments name a git ref (branch, tag, or commit, e.g. `main`), review the changes since that fixed point. Confirm it resolves with `git rev-parse`; if it doesn't but matches an existing path, treat it as a named file (step 2). Run `sh ~/.config/opencode/skills/code-review-checklist/scripts/review-diff.sh <ref>` and review what it prints: the commits since the ref and the three-dot diff against the merge-base. If it prints `REVIEW BLOCKED` or `(no changes since <ref>)` instead, relay that and stop. Pending working-tree changes fall outside this range — if the diff below shows any, note that they were not reviewed.
2. **Named files** — if the arguments name specific files, focus there.
3. **Pending changes** — otherwise use the diff below: staged changes when present, unstaged when nothing is staged, always including any new untracked files.
4. **Full codebase** — if the diff below says `(no pending changes)`, review the full codebase by exploring it directly.

Current review diff:
!`sh ~/.config/opencode/skills/code-review-checklist/scripts/review-diff.sh`

$ARGUMENTS
