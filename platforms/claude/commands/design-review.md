---
description: Judge whether a PR, branch, or the changes since a base ref fit the system's recorded design — ADRs, ownership, existing mechanisms, contract growth, spec scope
argument-hint: [PR number, branch, or base ref; add "comment" for a paste-ready review comment]
agent: code-reviewer
context: fork
disable-model-invocation: true
---

Run a design review. Read `~/.claude/skills/design-conformance/SKILL.md` first and follow it.

Find the default branch `D`: `git symbolic-ref --short refs/remotes/origin/HEAD`, else `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`, else whichever of `main` or `master` exists. Then pick the target and get its diff from `sh ~/.claude/skills/code-review-checklist/scripts/review-diff.sh <base> [<head>]`. If that prints `REVIEW BLOCKED` or a line in parentheses, such as `(no changes …)` or `(… does not resolve to a commit)`, relay it and stop.

1. **PR**: a number, `#n`, or PR URL. Read `gh pr view <n> --json title,body,baseRefName,headRefOid,commits,comments,reviews`, run `git fetch -q origin <baseRefName> pull/<n>/head`, then diff `origin/<baseRefName>` against `<headRefOid>`. If the remote is not GitHub or `gh` fails, say so and stop, asking for a branch or base ref instead.
2. **Branch**: a branch other than `D` and the current branch. Diff `D` against it, and look up its PR with `gh pr view <branch>` for the body.
3. **Base ref**: any other ref that resolves (`D`, a tag, a commit). The changes on HEAD since it, with no `<head>` argument.
4. **No target, or the current branch's name**: the current branch's PR below, if there is one; else HEAD since `D`; else, when HEAD is on `D`, the pending changes (`review-diff.sh` with no arguments).

Current branch's PR:
!`gh pr view --json number,title -q '"#\(.number) \(.title)"' 2>/dev/null || echo "(none)"`

Open the report with the target mode and the diff range you used. Run no `gh` command that writes. For cross-repo ownership, when the workspace instructions name a repo-map skill, Glob `~/.claude/plugins/cache/**/skills/<name>/SKILL.md` and Read it, since this agent has no skill tool; if nothing matches, say so in the report. You cannot ask the user anything, so blocking questions go in the report.

$ARGUMENTS
