---
description: Run a code quality review and security audit in parallel — pending changes, changes since a base ref, or the full codebase when the tree is clean
agent: tech-lead
subtask: true
---

Run a combined review: spawn `@code-reviewer` and `@security-analyst` as **parallel subagents** and present their findings in two labeled sections.

If the diff below says `REVIEW BLOCKED`, relay the message to the user and stop immediately.

Otherwise, pick the review target in this order:

1. **Base ref** — if the arguments name a git ref (branch, tag, or commit, e.g. `main`), review the changes since that fixed point. Confirm it resolves with `git rev-parse`; if it doesn't but matches an existing path, treat it as file scope (step 2). Screen `git diff <ref>...HEAD --name-only` for sensitive-looking paths (`.env*`, keys, certs, credentials) — if any appear, report that the review is blocked and stop. Then hand both agents `git diff <ref>...HEAD` (three-dot, so the comparison is against the merge-base) with `git log <ref>..HEAD --oneline` as commit context; if that diff is empty, report it and stop. Pending working-tree changes fall outside this range — if the diff below shows any, note that they were not reviewed.
2. **Named files or scope** — if the arguments name specific files or a scope, pass that focus to both agents.
3. **Pending changes** — otherwise give both agents the diff below.
4. **Full codebase** — if the diff below says `(no pending changes)`, both agents assess the full codebase directly.

Current diff:
!`s=$(git diff --staged --name-only); u=$(git diff --name-only); o=$(git ls-files --others --exclude-standard); if [ -z "$s" ] && [ -z "$u" ] && [ -z "$o" ]; then printf '(no pending changes)'; else paths=$(printf '%s\n%s\n' "$( [ -n "$s" ] && printf '%s' "$s" || printf '%s' "$u" )" "$o" | sed '/^$/d'); if printf '%s\n' "$paths" | grep -E '(^|/)\.env(rc|\..*)?$|(^|/)\.npmrc$|(^|/)id_[^/]+$|credentials[^/]*\.json$|service-?account[^/]*\.json$|\.pem$|\.key$|\.p12$|\.pfx$|\.tfvars(\.json)?$|(^|/)secrets?[^/]*\.(ya?ml|json)$' >/dev/null 2>&1; then printf 'REVIEW BLOCKED: sensitive-looking files are present in the changes. Remove or redact them before using /full-review.\n\nChanged paths:\n%s\n' "$paths"; else { [ -n "$s" ] && git diff --staged || git diff; printf '%s\n' "$o" | sed '/^$/d' | while IFS= read -r f; do git diff --no-index /dev/null "$f"; done; }; fi; fi`

Spawn both subagents simultaneously — do not wait for one before starting the other. Give each the review target selected above.

Once both complete, present findings under two headings:

**Code Review** — quality, performance, maintainability issues from `@code-reviewer`

**Security Audit** — vulnerabilities and security concerns from `@security-analyst`

$ARGUMENTS
