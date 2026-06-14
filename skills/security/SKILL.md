---
description: Run a security assessment on code, configuration, and dependencies
argument-hint: [scope (optional)]
agent: security-analyst
context: fork
disable-model-invocation: true
---

Perform a security assessment.

If specific files or directories are mentioned, focus the analysis there. Otherwise, use the diff below as the primary target — assess the changed code for vulnerabilities, then broaden to project-wide concerns (secrets in config, dependency manifests, attack surface) as relevant. The diff prefers staged changes, falls back to unstaged changes, and always includes any new untracked files. If the diff says `(no pending changes)`, assess the full codebase instead.

Start by identifying the tech stack and mapping the attack surface, then analyze for vulnerabilities systematically. If dependency manifests are present, run available audit commands (npm audit, pip audit, etc.).

Current diff:
!`s=$(git diff --staged --name-only); u=$(git diff --name-only); o=$(git ls-files --others --exclude-standard); if [ -z "$s" ] && [ -z "$u" ] && [ -z "$o" ]; then printf '(no pending changes)'; else { [ -n "$s" ] && git diff --staged || git diff; printf '%s\n' "$o" | sed '/^$/d' | while IFS= read -r f; do git diff --no-index /dev/null "$f"; done; }; fi`

$ARGUMENTS
