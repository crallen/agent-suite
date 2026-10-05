---
description: Run a code quality review and security audit in parallel — pending changes, changes since a base ref, or the full codebase when the tree is clean
agent: tech-lead
subtask: true
---

Run a combined review: spawn `@code-reviewer` and `@security-analyst` as **parallel subagents** and present their findings in two labeled sections.

If the diff below says `REVIEW BLOCKED`, relay the message to the user and stop immediately.

Otherwise, pick the review target in this order:

1. **Base ref** — if the arguments name a git ref (branch, tag, or commit, e.g. `main`), review the changes since that fixed point. Confirm it resolves with `git rev-parse`; if it doesn't but matches an existing path, treat it as file scope (step 2). Run `sh ~/.config/opencode/skills/code-review-checklist/scripts/review-diff.sh <ref>` and hand both agents what it prints: the commits since the ref and the three-dot diff against the merge-base. If it prints `REVIEW BLOCKED` or `(no changes since <ref>)` instead, relay that and stop. Pending working-tree changes fall outside this range — if the diff below shows any, note that they were not reviewed.
2. **Named files or scope** — if the arguments name specific files or a scope, pass that focus to both agents.
3. **Pending changes** — otherwise give both agents the diff below.
4. **Full codebase** — if the diff below says `(no pending changes)`, both agents assess the full codebase directly.

Current diff:
!`sh ~/.config/opencode/skills/code-review-checklist/scripts/review-diff.sh`

Spawn both subagents simultaneously — do not wait for one before starting the other. Give each the review target selected above.

Once both complete, present findings under two headings:

**Code Review** — quality, performance, maintainability issues from `@code-reviewer`

**Security Audit** — vulnerabilities and security concerns from `@security-analyst`

$ARGUMENTS
