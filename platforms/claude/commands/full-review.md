---
description: Run a code quality review and security audit in parallel — pending changes, changes since a base ref, or the full codebase when the tree is clean
argument-hint: [files or scope to focus on, or a base ref like main (optional)]
context: fork
disable-model-invocation: true
---

<!-- No `agent:` key by design: this fork orchestrates two subagents (@code-reviewer and @security-analyst) in parallel rather than routing to a single named agent. -->

Run a combined review: spawn `@code-reviewer` and `@security-analyst` as **parallel subagents** and present their findings in two labeled sections.

Pick the target with `sh ~/.claude/skills/code-review-checklist/scripts/review-diff.sh --select <arguments>`, passing the arguments below verbatim, or none when there are none. Act on what it prints:

- **A diff**: hand it to both agents. Apply a leading `Focus:` line, and repeat a leading `Note:` line in the report.
- **`(focus: …)`**: pass that focus to both agents.
- **`(no pending changes)` or `(not a git repository)`**: both agents assess the full codebase directly.
- **`REVIEW BLOCKED`, or any other line in parentheses**: relay it and stop.

Spawn both subagents simultaneously — do not wait for one before starting the other. Give each the target picked above.

Once both complete, present findings under two headings:

**Code Review** — quality, performance, maintainability issues from `@code-reviewer`

**Security Audit** — vulnerabilities and security concerns from `@security-analyst`

$ARGUMENTS
