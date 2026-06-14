---
description: Run a security assessment on code, configuration, and dependencies
argument-hint: [scope (optional)]
agent: security-analyst
context: fork
disable-model-invocation: true
---

Perform a security assessment.

If specific files or directories are mentioned, focus the analysis there. Otherwise, use the diff below as the primary target — assess the changed code for vulnerabilities, then broaden to project-wide concerns (secrets in config, dependency manifests, attack surface) as relevant. If the diff says `(no pending changes)`, assess the full codebase instead.

Start by identifying the tech stack and mapping the attack surface, then analyze for vulnerabilities systematically. If dependency manifests are present, run available audit commands (npm audit, pip audit, etc.).

Current diff:
!`if git diff --staged --quiet && git diff --quiet; then printf '(no pending changes)'; else if git diff --staged --quiet; then git diff; else git diff --staged; fi; fi`

$ARGUMENTS
