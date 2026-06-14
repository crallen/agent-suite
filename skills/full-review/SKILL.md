---
description: Run a code quality review and security audit in parallel — diffs when changes are pending, full codebase when the working tree is clean
argument-hint: [files or scope (optional)]
context: fork
disable-model-invocation: true
---

Run a combined review: spawn `@code-reviewer` and `@security-analyst` as **parallel subagents** and present their findings in two labeled sections.

If the diff below says `REVIEW BLOCKED`, relay the message to the user and stop immediately. If it says `(no pending changes)`, both agents should assess the full codebase directly. If specific files or scope are mentioned in `$ARGUMENTS`, pass that focus to both agents.

Current diff:
!`s=$(git diff --staged --name-only); u=$(git diff --name-only); o=$(git ls-files --others --exclude-standard); if [ -z "$s" ] && [ -z "$u" ] && [ -z "$o" ]; then printf '(no pending changes)'; else paths=$(printf '%s\n%s\n' "$( [ -n "$s" ] && printf '%s' "$s" || printf '%s' "$u" )" "$o" | sed '/^$/d'); if printf '%s\n' "$paths" | grep -E '(^|/)\.env(rc|\..*)?$|(^|/)\.npmrc$|(^|/)id_[^/]+$|credentials[^/]*\.json$|service-?account[^/]*\.json$|\.pem$|\.key$|\.p12$|\.pfx$|\.tfvars(\.json)?$|(^|/)secrets?[^/]*\.(ya?ml|json)$' >/dev/null 2>&1; then printf 'REVIEW BLOCKED: sensitive-looking files are present in the changes. Remove or redact them before using /full-review.\n\nChanged paths:\n%s\n' "$paths"; else { [ -n "$s" ] && git diff --staged || git diff; printf '%s\n' "$o" | sed '/^$/d' | while IFS= read -r f; do git diff --no-index /dev/null "$f"; done; }; fi; fi`

Spawn both subagents simultaneously — do not wait for one before starting the other. Give each the diff above and any scope from `$ARGUMENTS`.

Once both complete, present findings under two headings:

**Code Review** — quality, performance, maintainability issues from `@code-reviewer`

**Security Audit** — vulnerabilities and security concerns from `@security-analyst`

$ARGUMENTS
