#!/usr/bin/env bash
# Ask Claude Code itself to judge the suite, as the current model sees it.
#
#   1. `claude plugin validate --strict` on the Claude-facing trees: frontmatter
#      and structure as the harness parses them.
#   2. `/doctor prompt-audit`: the harness's own audit of CLAUDE.md, agents,
#      commands, and skills for outdated, conflicting, or model-redundant
#      instructions. It accepts no path; it audits the user config plus the
#      directory it starts in, so it starts in an empty one and sees only
#      ~/.claude, which is this suite once the dotfiles are stowed. It audits
#      the installed checkout, not a worktree.
#
# Makes model calls and takes several minutes. Read-only: plan mode, and the
# audit's proposed diff lands under ~/.claude/plans rather than in the repo.
# The suite's settings disable bundled skills, which the audit needs, so they
# are re-enabled for this run only.
set -uo pipefail

root="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
status=0

echo "## claude plugin validate --strict"
for dir in skills platforms/claude/agents platforms/claude/commands; do
  claude plugin validate "$root/$dir" --strict || status=1
done

echo
echo "## /doctor prompt-audit"
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
(cd "$scratch" && claude -p "/doctor prompt-audit" \
  --permission-mode plan \
  --settings '{"disableBundledSkills":false}') || status=1

exit "$status"
