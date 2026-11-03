---
description: Review code for quality, security, and best practices — pending changes, changes since a base ref, or the full codebase when the tree is clean
agent: code-reviewer
subtask: true
---

Review code for quality, security, performance, and maintainability issues.

Pick the target with `sh ~/.config/opencode/skills/code-review-checklist/scripts/review-diff.sh --select <arguments>`, passing the arguments below verbatim, or none when there are none. Act on what it prints:

- **A diff**: review it. Apply a leading `Focus:` line, and repeat a leading `Note:` line in the report.
- **`(focus: …)`**: review the named files or scope directly.
- **`(no pending changes)` or `(not a git repository)`**: review the full codebase by exploring it directly.
- **`REVIEW BLOCKED`, or any other line in parentheses**: relay it and stop.

$ARGUMENTS
