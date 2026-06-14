---
description: Review code for quality, security, and best practices — diffs when changes are pending, full codebase when the working tree is clean
argument-hint: [files to focus on (optional)]
agent: code-reviewer
context: fork
disable-model-invocation: true
---

Review the following code for quality, security, performance, and maintainability issues.

If specific files are named, focus there. Otherwise, use the diff below as the review target: prefer staged changes when present, fall back to unstaged changes when nothing is staged, and always include any new untracked files. If the diff says `(no pending changes)`, review the full codebase by exploring it directly. If the diff includes sensitive-looking files (`.env*`, keys, certs, credentials, or similar), stop and tell the user to redact or remove them before review.

Current review diff:
!`s=$(git diff --staged --name-only); u=$(git diff --name-only); o=$(git ls-files --others --exclude-standard); if [ -z "$s" ] && [ -z "$u" ] && [ -z "$o" ]; then printf '(no pending changes)'; else paths=$(printf '%s\n%s\n' "$( [ -n "$s" ] && printf '%s' "$s" || printf '%s' "$u" )" "$o" | sed '/^$/d'); if printf '%s\n' "$paths" | grep -E '(^|/)\.env(rc|\..*)?$|(^|/)\.npmrc$|(^|/)id_[^/]+$|credentials[^/]*\.json$|service-?account[^/]*\.json$|\.pem$|\.key$|\.p12$|\.pfx$|\.tfvars(\.json)?$|(^|/)secrets?[^/]*\.(ya?ml|json)$' >/dev/null 2>&1; then printf 'REVIEW BLOCKED: sensitive-looking files are present in the changes. Remove or redact them before using /code-review.\n\nChanged paths:\n%s\n' "$paths"; else { [ -n "$s" ] && git diff --staged || git diff; printf '%s\n' "$o" | sed '/^$/d' | while IFS= read -r f; do git diff --no-index /dev/null "$f"; done; }; fi; fi`

$ARGUMENTS
