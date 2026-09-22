# Roadmap: suite cleanup, September 2026

Four specs from the 2026-09-22 review, in dependency order. Each is one to three
sessions. Tick a phase here when its branch merges and the dotfiles pointer is
bumped; the per-task checklists live in the specs.

| # | Spec | Sessions | Unblocks | Done when |
|---|---|---|---|---|
| 1 | [Routing and drift fixes](specs/2026-09-22-routing-and-drift-fixes.md) | 1 | 3, 4 | Every routed command reaches its agent or runs inline by design; OpenCode at parity; zero harness terms in `skills/` |
| 2 | [Validator hardening and settings checks](specs/2026-09-22-validator-and-settings-checks.md) | 1 | 3, 4 | Validator runs on `uv`, four new checks, pre-commit hooks in both repos, `make check` verifies settings.json |
| 3 | [Platform-layer density and caching](specs/2026-09-22-platform-density-and-caching.md) | 1 | 4 (meta branch) | CLAUDE.md at or under 9 KB; agent and command bodies say each thing once |
| 4 | [Skills density cut](specs/2026-09-22-skills-density.md) | 3, one per cluster | — | About 1,300 lines out; agent-authoring shared; glossary folded |

## Order and why

1 → 2 → 3 → 4 (meta → engineering → methodology).

- **1 before everything.** It changes behavior and is the smallest. Its
  harness-neutral wording and factual fixes mean later specs edit text that is
  already correct, and its `.claude/` gitignore stops memory directories landing
  in the tree during the sessions that follow.
- **2 before 3 and 4.** The stricter validator (key allowlists, token-based index
  matching, injection scan) runs against every later cut, and the pre-commit hook
  means those sessions cannot land a broken index by accident. Spec 3 then edits
  the validator again, so 2 must be merged first, not in flight.
- **3 before 4.** Spec 3 removes the Skills and Agents tables from CLAUDE.md and
  changes description parity to OpenCode-versus-Codex. Spec 4's description
  rewrites are two-sided only because of that. Spec 3 also assigns the
  `cacheTtl` note to spec 4's agent-authoring rewrite.
- **Within 4, meta first.** agent-authoring's restructure removes the validator's
  hand-maintained carve-out and shrinks agent-reviewer's preload, and skill-design
  is the rulebook the other two branches cut by.

## Session plan

| Session | Work | Landing |
|---|---|---|
| A | Spec 1, all six commits, smoke tests | Merge; pointer bump |
| B | Spec 2, suite branch then dotfiles branch; seed settings on this machine | Merge both; pointer bump |
| C | Spec 3, five commits; record before/after sizes | Merge; pointer bump |
| D | Spec 4 meta branch | Merge; pointer bump |
| E | Spec 4 engineering branch | Merge; pointer bump |
| F | Spec 4 methodology branch | Merge; pointer bump |

Each session starts by reading its spec's Context and ends with the spec's
Testing section run and results in the PR body. A session that runs long stops at
a commit boundary; the spec's checklist records where.

## Cross-cutting rules

- The validator passes after every commit. From session B on, the hook enforces it.
- One commit per file or skill inside a branch, so any cut reverts alone.
- Line and byte counts before and after go in every PR body. The numbers are
  the evidence that a density change did what it claimed.
- A rule that turns out to be load-bearing after removal comes back as a single
  revert commit with the reason in the message, and the spec's Risks section
  gets a line so the next cluster knows.
- Attribution footers stay off every commit and PR, per `AGENTS.md`.

## Deferred, deliberately

- `disallowedTools` versus `memory` on code-reviewer: covered by the Bash
  fallback line in spec 1; a proper experiment waits until spec 3's agent pass.
- `KNOWN_TOOLS` contents and the Glob/Grep question: settled from the docs
  during spec 2.
- Subagent cache TTLs: no change; documented in spec 3 and in agent-authoring
  after spec 4.
- `/full-review` fork shape: correct as is under current subagent nesting.

## Progress

- [x] 1. Routing and drift fixes (merged 2026-09-22, PR #3)
- [ ] 2. Validator hardening and settings checks
- [ ] 3. Platform-layer density and caching
- [ ] 4a. Skills density: meta
- [ ] 4b. Skills density: engineering
- [ ] 4c. Skills density: methodology
