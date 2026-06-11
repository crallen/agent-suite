---
description: Review staged or unstaged code changes for quality, security, and best practices
argument-hint: [files to focus on (optional)]
agent: code-reviewer
context: fork
disable-model-invocation: true
---

Review the following code for quality, security, performance, and maintainability issues.

If specific files are named, focus there. Otherwise, review the current working diff below: prefer the staged diff when present; fall back to the unstaged diff when nothing is staged. If the diff includes sensitive-looking files (`.env*`, keys, certs, credentials, or similar), stop and tell the user to redact or remove them before review.

Current review diff:
!`paths=$(if git diff --staged --quiet; then git diff --name-only; else git diff --staged --name-only; fi); if printf '%s\n' "$paths" | rg '(^|/)\.env(rc|\..*)?$|(^|/)\.npmrc$|(^|/)id_[^/]+$|credentials[^/]*\.json$|service-?account[^/]*\.json$|\.pem$|\.key$|\.p12$|\.pfx$|\.tfvars(\.json)?$|(^|/)secrets?[^/]*\.(ya?ml|json)$' >/dev/null; then printf 'REVIEW BLOCKED: sensitive-looking files are present in the diff. Remove or redact them before using /review.\n\nChanged paths:\n%s\n' "$paths"; else if git diff --staged --quiet; then git diff; else git diff --staged; fi; fi`

$ARGUMENTS
