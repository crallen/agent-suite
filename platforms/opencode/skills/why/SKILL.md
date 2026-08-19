---
name: why
description: Reconstruct why code is shaped the way it is — recover the rationale behind a decision from git history, PRs, issues, comments, and ADRs, every claim cited and confidence stated. Load when asked why code exists in its current form, before changing code whose intent is unclear, or on /why against a file, symbol, or decision.
argument-hint: [file, symbol, or decision to explain]
---

# Why

Recover the *rationale* behind code — why it is shaped this way — not what it does. Reading the code tells you the what; the why lives in the history and discussion around it. Investigate the target named in the `/why` invocation, or the code under discussion when none is named.

## Principles

- **Evidence before narrative.** Build the account from sources you can cite, not from a plausible story the code suggests.
- **Cite every claim.** Each statement ties to a specific commit, PR, issue, comment, or doc. A claim with no source is a guess — label it one.
- **State confidence.** "The commit message says X" is high confidence. "This pattern suggests X" is low. Say which.
- **Null results are evidence.** "No PR discussion, no linked issue, commit message is just 'fix'" is a real finding: it tells the reader the rationale was never written down.
- **Code is not intent.** What the code does is not why someone chose it. Never present a reading of the code as the reason for it.

## Where the rationale hides

Gather from the sources the repo actually has, cheapest first. Not every source exists — a missing one is a null result, not a dead end.

| Source | Where to look | What it reveals |
|---|---|---|
| Introducing commit | `git blame`, `git log -L :<fn>:<file>`, `git log -S '<string>'` | The change and its stated reason |
| Surrounding history | `git log --follow <file>` | The sequence a decision sat in |
| Pull request | `gh pr list --search`, PR linked from the commit | Review discussion, tradeoffs raised |
| Issue / ticket | `gh issue view`, tracker ref in commit or PR | The problem being solved |
| Comments & docstrings | the file itself | Rationale the author left inline |
| ADRs / CONTEXT.md | repo root, `docs/adr/` | Decisions recorded deliberately |
| Changelog | CHANGELOG.md, release notes | When it shipped and why |

## Process

1. Pin the target: the file, symbol, or decision, and the exact lines.
2. Find the change that introduced the current shape — `git blame` to the commit, `git log -S`/`-L` for when a string or function first appeared.
3. Follow the trail outward: commit message → PR → issue → any linked discussion.
4. Check the deliberate records: ADRs, CONTEXT.md, comments, changelog.
5. Write the account — the rationale, each claim cited, confidence stated, gaps named.

Done when every claim carries a source or is marked a guess, and the gaps in the record are stated rather than filled with a plausible story.
