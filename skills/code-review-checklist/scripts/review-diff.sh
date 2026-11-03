#!/bin/sh
# Print the diff a review command works from, refusing when a changed path looks
# secret-bearing. The single home for that path screen and for review-target
# selection: the review commands of every harness call this instead of carrying
# their own copy.
#
#   review-diff.sh          pending changes: staged if any, else unstaged, plus
#                           untracked files; "(no pending changes)" when clean
#   review-diff.sh <ref>    commits and three-dot diff since <ref>;
#                           "(no changes since <ref>)" when empty
#   review-diff.sh <ref> <head>
#                           the same, for <head> in place of HEAD: a branch or
#                           fetched pull request that is not checked out
#   review-diff.sh --select [arg...]
#                           pick the target from a command's arguments: a first
#                           argument that resolves to a commit is a base ref, and
#                           pending changes are ignored; after it, arguments that
#                           exist as paths narrow the diff and any other words
#                           print as a "Focus: ..." line above it. Without a ref,
#                           arguments print "(focus: ...)" for the caller to
#                           review directly; none is pending-changes mode.
#                           "(no pending changes)" or "(not a git repository)"
#                           there means review the full codebase.
#
# Every mode that would print a diff prints "REVIEW BLOCKED: ..." and the
# offending paths instead when the screen matches. Exit status is 0 in every case
# the caller should relay, so a caller always gets a message to act on.

# Mirrors the deny list in platforms/claude/settings.json.example. Placeholder
# env files (.env.example and friends) hold no secrets and pass.
SENSITIVE='(^|/)\.env(rc|\..*)?$|(^|/)\.npmrc$|(^|/)id_(rsa|ed25519|ecdsa|dsa)[^/]*$|credentials[^/]*\.json$|service-?account[^/]*\.json$|\.pem$|\.key$|\.p12$|\.pfx$|\.tfvars(\.json)?$|(^|/)(secrets[^/]*|secret)\.(ya?ml|json)$|(^|/)secrets/'
PLACEHOLDER='(^|/)\.env\.(example|sample|template|dist)$'

blocked() {
    hits=$(printf '%s\n' "$1" | grep -Ev "$PLACEHOLDER" | grep -E "$SENSITIVE")
    [ -n "$hits" ] || return 1
    printf 'REVIEW BLOCKED: sensitive-looking files are present in the changes. Remove or redact them before running the review.\n\nBlocked paths:\n%s\n' "$hits"
}

is_commit() { git rev-parse --verify --quiet "$1^{commit}" >/dev/null 2>&1; }

since() {  # since <ref> <head> [path...]; $focus, if set, prints above the diff
    ref=$1 head=$2; shift 2
    for r in "$ref" "$head"; do
        is_commit "$r" || { printf '(%s does not resolve to a commit)\n' "$r"; exit 0; }
    done
    paths=$(git diff --name-only "$ref...$head" -- "$@")
    [ -n "$paths" ] || { printf '(no changes since %s)\n' "$ref"; exit 0; }
    blocked "$paths" && exit 0
    lead=
    if [ -n "${focus-}" ]; then printf 'Focus: %s\n' "$focus"; lead=1; fi
    if [ "$head" = HEAD ] && [ -n "$(git status --porcelain)" ]; then
        printf 'Note: pending working-tree changes are outside this range and not shown.\n'
        lead=1
    fi
    [ -z "$lead" ] || printf '\n'
    printf 'Commits since %s:\n' "$ref"
    git log --oneline "$ref..$head" -- "$@"
    printf '\n'
    git diff "$ref...$head" -- "$@"
    exit 0
}

if [ "${1-}" = --select ]; then
    shift
    for a in "$@"; do  # drop empty arguments
        shift; [ -n "$a" ] && set -- "$@" "$a"
    done
    if [ $# -gt 0 ] && git rev-parse --git-dir >/dev/null 2>&1 && is_commit "$1"; then
        ref=$1; shift
        focus=
        for a in "$@"; do  # existing paths narrow the diff; other words are focus
            shift
            if [ -e "$a" ]; then set -- "$@" "$a"; else focus="${focus:+$focus }$a"; fi
        done
        since "$ref" HEAD "$@"
    fi
    if [ $# -gt 0 ]; then  # nothing is diffed here, so there is nothing to screen
        printf '(focus: %s)\n' "$*"
        exit 0
    fi
fi

git rev-parse --git-dir >/dev/null 2>&1 || { printf '(not a git repository)\n'; exit 0; }

[ $# -gt 0 ] && since "$1" "${2:-HEAD}"

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
