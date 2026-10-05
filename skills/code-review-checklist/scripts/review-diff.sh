#!/bin/sh
# Print the diff a review command works from, refusing when a changed path looks
# secret-bearing. The single home for that path screen: the review commands of
# every harness call this instead of carrying their own copy.
#
#   review-diff.sh          pending changes: staged if any, else unstaged, plus
#                           untracked files; "(no pending changes)" when clean
#   review-diff.sh <ref>    commits and three-dot diff since <ref>;
#                           "(no changes since <ref>)" when empty
#
# Either mode prints "REVIEW BLOCKED: ..." and the offending paths instead of a
# diff when the screen matches. Exit status is 0 in every case the caller should
# relay, so an injected call always yields its message.

# Mirrors the deny list in platforms/claude/settings.json.example. Placeholder
# env files (.env.example and friends) hold no secrets and pass.
SENSITIVE='(^|/)\.env(rc|\..*)?$|(^|/)\.npmrc$|(^|/)id_(rsa|ed25519|ecdsa|dsa)[^/]*$|credentials[^/]*\.json$|service-?account[^/]*\.json$|\.pem$|\.key$|\.p12$|\.pfx$|\.tfvars(\.json)?$|(^|/)secrets?(\.[^/]*)?\.(ya?ml|json)$|(^|/)secrets/'
PLACEHOLDER='(^|/)\.env\.(example|sample|template|dist)$'

blocked() {
    hits=$(printf '%s\n' "$1" | grep -Ev "$PLACEHOLDER" | grep -E "$SENSITIVE")
    [ -n "$hits" ] || return 1
    printf 'REVIEW BLOCKED: sensitive-looking files are present in the changes. Remove or redact them before running the review.\n\nBlocked paths:\n%s\n' "$hits"
}

git rev-parse --git-dir >/dev/null 2>&1 || { printf '(not a git repository)\n'; exit 0; }

if [ $# -gt 0 ]; then
    ref=$1
    git rev-parse --verify --quiet "$ref^{commit}" >/dev/null || {
        printf '(%s does not resolve to a commit)\n' "$ref"; exit 0; }
    paths=$(git diff --name-only "$ref...HEAD")
    [ -n "$paths" ] || { printf '(no changes since %s)\n' "$ref"; exit 0; }
    blocked "$paths" && exit 0
    printf 'Commits since %s:\n' "$ref"
    git log --oneline "$ref..HEAD"
    printf '\n'
    git diff "$ref...HEAD"
    exit 0
fi

staged=$(git diff --staged --name-only)
unstaged=$(git diff --name-only)
untracked=$(git ls-files --others --exclude-standard)

if [ -z "$staged" ] && [ -z "$unstaged" ] && [ -z "$untracked" ]; then
    printf '(no pending changes)\n'
    exit 0
fi

tracked=${staged:-$unstaged}
paths=$(printf '%s\n%s\n' "$tracked" "$untracked" | sed '/^$/d')
blocked "$paths" && exit 0

if [ -n "$staged" ]; then git diff --staged; else git diff; fi
printf '%s\n' "$untracked" | sed '/^$/d' | while IFS= read -r f; do
    git diff --no-index /dev/null "$f" || true
done
exit 0
