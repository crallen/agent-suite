---
description: Review code for quality, security, and best practices — diffs when changes are pending, full codebase when the working tree is clean
agent: code-reviewer
subtask: true
---

Review the following code for quality, security, performance, and maintainability issues.

If specific files are named, focus there. Otherwise, use the diff below as the review target: prefer staged changes when present, fall back to unstaged changes when nothing is staged. If the diff says `(no pending changes)`, review the full codebase by exploring it directly. If the diff includes sensitive-looking files (`.env*`, keys, certs, credentials, or similar), stop and tell the user to redact or remove them before review.

Current review diff:
!`if git diff --staged --quiet && git diff --quiet; then printf '(no pending changes)'; else paths=$(if git diff --staged --quiet; then git diff --name-only; else git diff --staged --name-only; fi); if printf '%s\n' "$paths" | rg '(^|/)\.env(rc|\..*)?$|(^|/)\.npmrc$|(^|/)id_[^/]+$|credentials[^/]*\.json$|service-?account[^/]*\.json$|\.pem$|\.key$|\.p12$|\.pfx$|\.tfvars(\.json)?$|(^|/)secrets?[^/]*\.(ya?ml|json)$' >/dev/null; then printf 'REVIEW BLOCKED: sensitive-looking files are present in the diff. Remove or redact them before using /code-reviewer.\n\nChanged paths:\n%s\n' "$paths"; else if git diff --staged --quiet; then git diff; else git diff --staged; fi; fi; fi`

$ARGUMENTS
