# Routing and drift fixes

## Goal

Make every Claude command do what its frontmatter claims, bring OpenCode to parity
with the Claude side, and remove harness-specific wording and factual errors from
shared skills. After this, `/commit`-class commands run inline by design rather than
by accident, `/docs`, `/debugger`, `/frontend`, and `/frontend-polish` reach the
agents whose capabilities justify them, and Codex users never hit a dead `/command`
pointer inside a shared skill.

## Context

- **`agent:` is inert without `context: fork`.** The Claude Code docs define `agent`
  as "which subagent type to use when `context: fork` is set". Seven commands set it
  alone: `commit`, `ship`, `release`, `docs`, `debugger`, `frontend`,
  `frontend-polish`. Confirmed live on 2026-09-22 when `/ship` ran on the session
  model. The 2026-09-01 roster spec assumed `agent:` alone routed; it never did.
- **Forks run in the background with no history and cannot ask.** A forked
  git-manager would only see `git diff --stat`, which kills commit bodies.
- **`/full-review` is fine.** Subagents nest up to three levels by default, so a
  fork spawning two reviewers works. No change.
- **Memory works but is fragile.** A live test showed code-reviewer receives only
  Read and Bash in this harness, no Write or Edit, despite `memory: local` being
  documented as auto-enabling them. Writes succeed via shell redirection only. The
  test also left `platforms/opencode/.claude/agent-memory-local/` in the submodule
  because `local` scope resolves from the working directory.
- **ADR-0001** says an agent earns its slot by capability. git-manager's only
  capability on Claude is the sonnet pin, which this spec gives up.
- **Shared skills name harness machinery** in eight places: wayfinder (`Explore`,
  `general-purpose`, four `/commands`), grill (`AskUserQuestion`, T3 Code),
  spec-writing (`tech-lead`, `/architecture`), frontend-patterns (`/spec`),
  debugging-methodology (`/architecture` twice), why, blast-radius, unslop (`/name`
  invocation phrasing). AGENTS.md forbids this, and Codex has no commands.
- **Factual slips:** security-analysis grep with quoted brace expansion, `pip audit`;
  ci-pipeline and docker references pin versions the skill itself says to verify;
  coding-guardrails says "four" for six; agent-authoring's color table lists six
  agents deleted on 2026-09-01.
- **OpenCode drift:** no `|| true` in `code-review`, `security`, `full-review`
  injections; `/prototype` has `subtask: true` but must converse; git-manager lacks
  convention deferral and Filesystem Safety; no `/wayfinder`; agent-builder line 95
  contradicts architect being primary and line 54 contradicts the bash-allow rule.
- **Small Claude gaps:** `/zoom-out` has no `$ARGUMENTS`; `/agent-builder` and
  `/agent-review` inject `ls ~/.claude/skills/`, which now lists `synced`;
  `/architecture` never loads grill-methodology.

## Decisions

- **Route by what the agent carries.** `/commit`, `/ship`, `/release` run inline
  with `git-conventions` loaded; git-manager is deleted on Claude. `/docs` forks to
  documenter. `/debugger`, `/frontend`, `/frontend-polish` use prose routing so
  debugger's memory and frontend-engineer's Playwright engage.
- **Full OpenCode parity.** All drift items are ported, including `/wayfinder`.

## Approach

One branch in agent-suite, six themed commits in dependency order: routing, roster
removal, OpenCode parity, harness-neutral skills, factual fixes, hygiene. The
validator runs after each. Every routed command gets a live smoke test before the
branch merges, since the validator cannot see routing semantics. Then a pointer bump
in dotfiles.

Alternatives considered: a single squashed commit (harder to bisect if a routing
change misbehaves), or folding this into the density-cut spec (mixes behavior
changes with prose trims and makes review harder).

## Components

**1. Routing (`platforms/claude/commands/`)**

- `commit.md`, `ship.md`, `release.md`: remove `agent: git-manager`. Add a first
  line "Load the `git-conventions` skill and follow it." Filesystem Safety from
  git-manager moves into `git-conventions` as a short section, since it encodes a
  real incident.
- `docs.md`: add `context: fork` under `agent: documenter`.
- `debugger.md`, `frontend.md`, `frontend-polish.md`: remove `agent:`. Body opens
  with "Use the `@debugger` subagent to…" or "Use the `@frontend-engineer` subagent
  to…" so the delegation carries conversation context.
- `zoom-out.md`: add `argument-hint: [area or module]` and trailing `$ARGUMENTS`.
- `architecture.md`: add `grill-methodology` to the loaded skills.
- `agent-builder.md`, `agent-review.md`: injection becomes
  `ls -d ~/.claude/skills/*/SKILL.md` so `synced` never appears.

**2. Roster (`platforms/claude/`, `docs/`)**

- Delete `agents/git-manager.md`.
- `CLAUDE.md`: routing bullet line 23 drops git-manager; guideline line 42 becomes
  "Handle git and GitHub operations directly, `gh` for hosted tasks"; agents table
  row 59 removed; command table rows 106–108 Agent column becomes
  "— (inline, `git-conventions`)".
- `docs/adr/0001-…` line 10: drop git-manager, add one sentence noting it was
  retired when the pin stopped paying for itself.
- `skills/agent-authoring/SKILL.md` color table: the seven remaining agents.

**3. OpenCode parity (`platforms/opencode/`)**

- `commands/code-review.md`, `security.md`, `full-review.md`: append `|| true` to
  the `git diff --no-index` loop.
- `commands/prototype.md`: remove `subtask: true`.
- `agent/git-manager.md`: port step 2 and 4 wording (defer to project conventions),
  drop the 72-char paragraph, add the Filesystem Safety section.
- `commands/wayfinder.md`: new, `agent: architect`, no subtask, body mirrors
  Claude's. `AGENTS.md`: command row plus a "multi-session effort" workflow row.
- `agent/agent-builder.md`: line 95 becomes "tech-lead and architect are the only
  primaries"; line 54 drops "Analysis agents don't need full bash".

**4. Harness-neutral skills (`skills/`)**

- `wayfinder-methodology/SKILL.md`: line 92 becomes "dispatch a read-only subagent
  for in-repo facts, a web-capable one otherwise"; lines 14–19 reference
  `grill-methodology`, `spec-writing`, `ticket-writing` by skill name.
- `grill-methodology/SKILL.md` line 32 and `spec-writing/SKILL.md` line 41: one
  shared sentence, "do not use the harness's structured question tool", no product
  names.
- `spec-writing/SKILL.md`: delete the suggested-wording block at 143–146; line 165
  says `architecture-review` not `/architecture`.
- `frontend-patterns/SKILL.md` line 16, `debugging-methodology/SKILL.md` lines 123
  and 144: skill names in place of slash commands.
- `why`, `blast-radius`, `unslop`: description and body say "when invoked against…"
  instead of `/name`. Matching index rows change in step (validator parity).

**5. Factual fixes (`skills/`)**

- `security-analysis/SKILL.md`: line 102 grep rewritten with repeated `--include`
  flags; line 117 becomes `pip-audit`; add `yarn npm audit` for Berry.
- `ci-pipeline/reference/{go,node,rust,github-actions}.md` and
  `docker-best-practices/reference/{go,rust}.md`: verify and update every pin at
  implementation time. A one-line comment above each block records the check date.
- `coding-guardrails/SKILL.md` lines 8, 12, 119: "four" becomes "six".

**6. Hygiene**

- Delete `platforms/opencode/.claude/`. Add `.claude/` to the suite's `.gitignore`.
- `platforms/claude/agents/code-reviewer.md` and `debugger.md`: one sentence in the
  memory section, "if Write is unavailable, write memory files through Bash".

Deliberately left out: `/full-review` stays as is; the `disallowedTools` experiment
on code-reviewer waits for the density spec's agent frontmatter pass.

## Testing

Live smoke test per changed command, from a Claude Code session in a scratch git
repo with a small dirty tree.

- `/commit`, `/ship`, `/release`: session model with `git-conventions` loaded, no
  subagent. Commit message matches the project's convention.
- `/docs`: background fork on documenter, model sonnet.
- `/debugger`, `/frontend`, `/frontend-polish`: Agent call to the named subagent.
  Debugger memory lands in the repo root's `.claude/agent-memory-local/`.
  Frontend-engineer's tool list includes Playwright.
- `/zoom-out payments`: the argument reaches the prompt.
- `/architecture`: first grilling question uses lettered options with a
  recommendation.
- `/agent-builder`: the injected skill list has no `synced` entry.
- OpenCode: `/code-review` with one untracked file completes cleanly. `/prototype`
  can ask mid-run. `/wayfinder` appears in the command list.
- Validator passes after every commit, with PyYAML installed locally.
- Grep shared skills for `/spec`, `/grill`, `/architecture`, `/ticket`,
  `/wayfinder`, `AskUserQuestion`, `Explore`, `general-purpose`, `tech-lead`: zero
  hits outside `platforms/` and `agent-authoring`.

## Risks & Open Questions

- **Risk:** inline git loses the cost saving. Accepted; commit-body quality was
  judged worth more.
- **Risk:** prose routing is instruction, not enforcement. The 2026-09-01 spec moved
  away from it for that reason, but frontmatter routing without a fork was never
  enforcement either. The smoke test checks it once; revisit if it drifts.
- **Risk:** `/docs` as a background fork changes its feel. Fallback: inline like the
  git commands, and documenter goes the way of git-manager.
- **Risk:** CI pins rot again. Mitigated by the dated comment, not solved.
- **Open:** Glob and Grep were absent for subagents and the main session on
  2026-09-22. Harness build or T3 Code SDK configuration is unknown. `tools:`
  allowlists still name them, harmlessly. Check in the tooling spec.
- **Open:** which allowlist mechanism hid Write from code-reviewer. Covered by the
  Bash fallback sentence.

## Task Checklist

Branch `fix/routing-and-drift` in agent-suite. Run `scripts/validate-config.py`
after each numbered group.

**1. Routing**
- [ ] `platforms/claude/commands/commit.md`, `ship.md`, `release.md`: remove
      `agent: git-manager`; prepend "Load the `git-conventions` skill and follow it."
- [ ] `skills/git-conventions/SKILL.md`: add a "Filesystem Safety" section carrying
      the four bullets from git-manager verbatim.
- [ ] `platforms/claude/commands/docs.md`: add `context: fork`.
- [ ] `platforms/claude/commands/debugger.md`, `frontend.md`, `frontend-polish.md`:
      remove `agent:`; open with "Use the `@debugger` subagent to…" /
      "Use the `@frontend-engineer` subagent to…".
- [ ] `platforms/claude/commands/zoom-out.md`: add `argument-hint: [area or module]`
      and a trailing `$ARGUMENTS`.
- [ ] `platforms/claude/commands/architecture.md`: load `grill-methodology`.
- [ ] `platforms/claude/commands/agent-builder.md`, `agent-review.md`: injection
      becomes `ls -d ~/.claude/skills/*/SKILL.md`.

**2. Roster**
- [ ] Delete `platforms/claude/agents/git-manager.md`.
- [ ] `platforms/claude/CLAUDE.md`: edit lines 23, 42, 59, 106–108.
- [ ] `docs/adr/0001-agents-earn-their-slot-by-capability.md` line 10.
- [ ] `skills/agent-authoring/SKILL.md` lines 303–312: color table for the seven
      current agents with their actual colors.

**3. OpenCode parity**
- [ ] `platforms/opencode/commands/code-review.md`, `security.md`,
      `full-review.md`: append `|| true` inside the `--no-index` loop.
- [ ] `platforms/opencode/commands/prototype.md`: remove `subtask: true`.
- [ ] `platforms/opencode/agent/git-manager.md`: port steps 2 and 4, delete the
      72-char bullet, add Filesystem Safety.
- [ ] Create `platforms/opencode/commands/wayfinder.md` with `agent: architect`.
- [ ] `platforms/opencode/AGENTS.md`: `/wayfinder` command row and a
      "multi-session effort" workflow row.
- [ ] `platforms/opencode/agent/agent-builder.md`: fix lines 54 and 95.

**4. Harness-neutral skills**
- [ ] `skills/wayfinder-methodology/SKILL.md`: rewrite line 92 and lines 14–19.
- [ ] `skills/grill-methodology/SKILL.md` line 32 and `skills/spec-writing/SKILL.md`
      line 41: neutral wording.
- [ ] `skills/spec-writing/SKILL.md`: delete lines 143–146; line 165 references
      `architecture-review`.
- [ ] `skills/frontend-patterns/SKILL.md` line 16,
      `skills/debugging-methodology/SKILL.md` lines 123 and 144.
- [ ] `skills/why/SKILL.md`, `skills/blast-radius/SKILL.md`, `skills/unslop/SKILL.md`:
      drop `/name` phrasing; update the matching rows in all three index documents.

**5. Factual fixes**
- [ ] `skills/security-analysis/SKILL.md`: lines 102 and 116–119.
- [ ] `skills/ci-pipeline/reference/*.md`, `skills/docker-best-practices/reference/*.md`:
      verify and update every pin; dated check comment above each block.
- [ ] `skills/coding-guardrails/SKILL.md` lines 8, 12, 119.

**6. Hygiene**
- [ ] Delete `platforms/opencode/.claude/`; add `.claude/` to `.gitignore`.
- [ ] `platforms/claude/agents/code-reviewer.md`, `debugger.md`: Bash fallback
      sentence in the memory section.

**7. Verify and land**
- [ ] `pip install pyyaml` locally; validator passes with the frontmatter check active.
- [ ] Run the smoke tests in Testing; record results in the PR body.
- [ ] Grep the shared skills for harness terms; zero hits.
- [ ] Merge, then bump the submodule pointer in dotfiles.
