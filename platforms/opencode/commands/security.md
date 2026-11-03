---
description: Run a security assessment on code, configuration, and dependencies
agent: security-analyst
subtask: true
---

Perform a security assessment.

Pick the target with `sh ~/.config/opencode/skills/code-review-checklist/scripts/review-diff.sh --select <arguments>`, passing the arguments below verbatim, or none when there are none. Act on what it prints:

- **A diff**: assess the changed code for vulnerabilities, then broaden to project-wide concerns (secrets in config, dependency manifests, attack surface) as relevant. When it opens with a note that pending changes were left out, repeat that in the report.
- **`(focus: …)`**: focus the analysis on the named files or directories.
- **`(no pending changes)` or `(not a git repository)`**: assess the full codebase.
- **`REVIEW BLOCKED`, or any other line in parentheses**: relay it and stop.

Start by identifying the tech stack and mapping the attack surface, then analyze for vulnerabilities systematically. If dependency manifests are present, run available audit commands (npm audit, pip audit, etc.).

$ARGUMENTS
