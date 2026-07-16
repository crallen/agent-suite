---
description: Review code for quality, security, and best practices — pending changes, changes since a base ref, or the full codebase when the tree is clean
argument-hint: [files to focus on, or a base ref like main (optional)]
agent: code-reviewer
context: fork
disable-model-invocation: true
---

Review code for quality, security, performance, and maintainability issues.

If the diff below says `REVIEW BLOCKED`, relay the message to the user and stop immediately.

Otherwise, pick the review target in this order:

1. **Base ref** — if the arguments name a git ref (branch, tag, or commit, e.g. `main`), review the changes since that fixed point. Confirm it resolves with `git rev-parse`; if it doesn't but matches an existing path, treat it as a named file (step 2). Screen `git diff <ref>...HEAD --name-only` for sensitive-looking paths (`.env*`, keys, certs, credentials) — if any appear, report that the review is blocked and stop. Then review `git diff <ref>...HEAD` (three-dot, so the comparison is against the merge-base) with `git log <ref>..HEAD --oneline` as commit context; if that diff is empty, report it and stop. Pending working-tree changes fall outside this range — if the diff below shows any, note that they were not reviewed.
2. **Named files** — if the arguments name specific files, focus there.
3. **Pending changes** — otherwise use the diff below: staged changes when present, unstaged when nothing is staged, always including any new untracked files.
4. **Full codebase** — if the diff below says `(no pending changes)`, review the full codebase by exploring it directly.

Current review diff:
!`s=$(git diff --staged --name-only); u=$(git diff --name-only); o=$(git ls-files --others --exclude-standard); if [ -z "$s" ] && [ -z "$u" ] && [ -z "$o" ]; then printf '(no pending changes)'; else paths=$(printf '%s\n%s\n' "$( [ -n "$s" ] && printf '%s' "$s" || printf '%s' "$u" )" "$o" | sed '/^$/d'); if printf '%s\n' "$paths" | grep -E '(^|/)\.env(rc|\..*)?$|(^|/)\.npmrc$|(^|/)id_[^/]+$|credentials[^/]*\.json$|service-?account[^/]*\.json$|\.pem$|\.key$|\.p12$|\.pfx$|\.tfvars(\.json)?$|(^|/)secrets?[^/]*\.(ya?ml|json)$' >/dev/null 2>&1; then printf 'REVIEW BLOCKED: sensitive-looking files are present in the changes. Remove or redact them before using /code-review.\n\nChanged paths:\n%s\n' "$paths"; else { [ -n "$s" ] && git diff --staged || git diff; printf '%s\n' "$o" | sed '/^$/d' | while IFS= read -r f; do git diff --no-index /dev/null "$f"; done; }; fi; fi`

$ARGUMENTS
