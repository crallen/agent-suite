# Routing and behavior evals

## Goal

Catch behavioral regressions the validator cannot see, before they merge. Two tiers:
**routing evals** (a prompt loads the expected skill or agent) and **four behavioral
regressions** (debugger Phase 0, code-reviewer catches a planted bug, `/commit`
conventions, `/spec` asks before drafting). `scripts/run-evals.py` runs both locally
against `main` and the working tree and prints a base-vs-head report for the PR
body. CI makes no model calls: it fails a PR touching `skills/` or `platforms/`
whose body carries neither the report marker nor `evals: n/a — <reason>`.

## Context

- `validate-config.py` is structural only (uv/PEP 723); CI runs it on push and PR,
  the pre-commit hook on suite paths. Nothing tests behavior.
- The density specs cut about 1,300 lines and rewrote descriptions; the roadmap
  already anticipates "a rule that turns out to be load-bearing after removal." Today
  that is found only in live use.
- The live config is this working tree (`~/.claude/skills` →
  `dotfiles/claude/.claude/skills` → `agent-suite/skills`), so comparing a branch
  against `main` needs a config built per ref.
- Routing targets: 26 tracked skills and 7 agents. The 28 commands all set
  `disable-model-invocation`, so they are reachable only by explicit `/name` and are
  tested only in the behavioral tier.
- `skills/synced/` (skill-creator) is gitignored, so it is absent in CI and on a
  fresh clone. Its `run_eval.py` tests one skill in isolation; we borrow its
  stream-json parsing approach, not its code.
- `settings.json.example` enables two plugins; loading them would put
  `frontend-design:frontend-design` into routing competition.
- This machine authenticates by OAuth (no `ANTHROPIC_API_KEY`), which rules out
  `--bare`: it accepts only an API key or `apiKeyHelper`.

## Approach

One uv script driving `claude -p --output-format stream-json
--include-partial-messages`, matching the validator's toolchain. Alternatives
considered: the Claude Agent SDK (typed messages, but a dependency that wraps the
same CLI and leaves isolation unchanged) and promptfoo (free reporting, but Node, a
framework DSL, and isolation hidden behind a provider layer).

Decisions:

- **Per-ref config.** A temporary `CLAUDE_CONFIG_DIR` (mode 0700, removed on exit)
  built from a suite root R: `agents`, `commands`, `CLAUDE.md` link into
  `R/platforms/claude/`; `skills/` is a real directory with one link per **tracked**
  `skills/<name>/`, so `synced/` is excluded on both sides; `settings.json` is the
  example with `enabledPlugins` replaced by the builtin plugins set to `false`
  (`cc-plugin-plugin-authoring`, `cc-plugin-agents-md`, `cc-plugin-telemetry`, each
  `@builtin`); runs pass `--strict-mcp-config` with no MCP config. A run whose init
  event still lists a plugin is reported as an isolation warning. Each run also gets
  a temporary `HOME` whose `.claude` links to that config dir, because command `!`
  lines hardcode `~/.claude/...` (`/code-review`, `/full-review`, `/agent-review`,
  `/agent-builder`) and would otherwise run the live suite's scripts on both sides.
  Base R is a `git worktree add --detach` of `--base` (default `main`); head R is the
  working tree itself, so it runs before commit, and a dirty tree marks `-dirty`.
- **Auth.** The runner needs `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`)
  or `ANTHROPIC_API_KEY`. A variable already in the environment wins; otherwise the
  runner loads `KEY=VALUE` lines from `<head root>/.env`, gitignored, with a committed
  `.env.example` as the template. The runner loading the file itself means humans,
  implementer agents, and red-proof runs all get the token without it entering an
  agent's context; the deny list's `Read(**/.env)` keeps agents out of the file.
  The token goes only into the subprocess environment, never into a log, report, or
  recording. Symlinking `~/.claude/.credentials.json` was rejected: an OAuth refresh
  can replace the link with a real token copy in `/tmp` or rotate the refresh token
  under the live login.
- **Routing observation.** A run's route is the set of `Skill` calls
  (`input.skill`), `Agent` calls (`input.subagent_type`), and `Read`s of a `SKILL.md`
  within the first 3 main-thread tool calls. The process is killed at the `assistant`
  event carrying an `Agent` call (the tool starts executing there, before
  `content_block_stop`), so no subagent runs; `Skill` and `SKILL.md` `Read` hits are
  recorded and reading continues until the window closes, since a skill load has no
  side effects and the expected skill may load after another one.
  A run passes when the route set contains the `expect` target or any `any_of`
  member, other loads alongside it notwithstanding (`coding-guardrails` loads with
  most implementation prompts); `expect: none` passes only on an empty set.
- **Scoring.** N runs per case (default 3); a case passes at ≥ 2/3. The report marks
  **REGRESSION** when base passes and head fails, **FIXED** for the reverse, and
  **INCONCLUSIVE** when either side has fewer than 2 runs that count. Any case first
  scored REGRESSION or FIXED is confirmed automatically: 5 more runs per side, then
  rescored on all of them under the same rule, and the report shows the combined
  rates and that the case was confirmed. At N=3 a case near 50% flips on noise (task
  11 scored `routing/git-conventions` FIXED with no suite change). The human
  reading the report judges it; CI checks only that it is present.
- **Gate trigger.** Any PR changing `skills/**` or `platforms/**`, excluding
  `skills/synced/**` and `platforms/claude/settings.json.example`. A PR that changes
  no behavior says `evals: n/a — <reason>`.

## Components

### `evals/routing.yaml`

About 40 entries: one prompt per tracked skill (26), one per agent (7), and about 6
negatives that should route nowhere (conceptual questions). Each entry is
`{prompt, expect: <name>}`, `{prompt, any_of: [..]}` for genuine overlap (such as
`code-reviewer` vs `code-review-checklist`), or `{prompt, expect: none}`. Prompts are
written the way a user would ask, never paraphrased from the description, and ask
for work rather than advice: the task 11 run showed advice questions get answered
inline with nothing loaded, on base and head alike.

An entry may carry `fixture: <path under evals/>` naming a directory with
`before/` and optional `after/`, set up exactly like a behavior fixture (unstaged
overlay), so a request to review or debug has a repo to act on. Agent entries use
`expect: <agent>`; `any_of` pairing an agent with its own skill passes on a skill
load alone, so it does not test agent routing. A case that fails on base in a full
run guards nothing and is reworded or dropped.

### `evals/behavior/<case>/`

`case.yaml` plus `fixture/before/` and an optional `fixture/after/`. An empty
fixture is a case with no `fixture/` directory at all. The runner copies the
fixture to scratch, `git init`s it with a fixed identity (`user.name evals`,
`user.email evals@localhost`, set in the scratch repo's config so `/commit` can
commit), commits `before/` as exactly one commit, then overlays `after/` as
uncommitted changes, or staged ones when `stage: true`. An empty fixture still gets
`git init` and the identity, with no commit.

`case.yaml` keys: `prompt`;
`allowed_tools` (narrow, e.g. `["Bash(python3 -m unittest*)", "Edit"]`);
`timeout`; `stage`; and `assert`, a list using five types:

| Type | Shape | Checks |
|---|---|---|
| `order` | `{first: <tool[:regex]>, before: <tool>}` | A call matching `first` occurs, and if `before` is ever called, the first match precedes its first call. Fails when `first` never occurs. For `Bash`, the regex runs against the `command` input. One `before` tool per assertion; "before Edit or Write" is two assertions |
| `tool_not_called` | `[<tool>, ..]` | None of these tools was called |
| `final_text` | `{match: [..], not_match: [..]}` | Regexes against the final assistant text |
| `shell` | `{run, match, not_match}` | Command run in scratch after the session; regexes against its stdout |
| `no_paths` | `[<glob>, ..]` | No file matching these exists in scratch afterwards |

Agent cases run through their real commands, not `--agent`: an agent's `skills:`
preload applies only when it runs as a subagent or fork. Tool calls from a subagent
or fork carry a `parent_tool_use_id` and count in `order` and `tool_not_called`
alongside main-thread calls, in stream order.

Every regex in an assertion is applied with `re.search` and no default flags;
a case that needs case folding or line anchors writes `(?i)` or `(?m)` inline.

The four cases:

| Case | Setup | Passes when |
|---|---|---|
| `debugger-phase-0` | prompt `/debugger <symptom>`, `Agent` allowed; Python fixture with a failing `unittest` | `order`: a Bash call matching `unittest` precedes the first `Edit`/`Write` |
| `reviewer-planted-bug` | prompt `/code-review`, `Bash(sh *)` allowed; unstaged `after/` adds string-built SQL to `db.py` at a known line | `final_text` matches `db.py` and that line number |
| `commit-conventions` | prompt `/commit`; `stage: true`; `allowed_tools: ["Bash(git *)"]` | `shell: git log -1 --format=%B` matches `^(feat\|fix\|docs\|style\|refactor\|perf\|test\|build\|ci\|chore)(\(.+\))?!?: .{1,71}$` on the first line and not `Co-Authored-By\|Generated with` |
| `spec-asks-first` | prompt `/spec <goal>`; empty fixture | `final_text` matches a lettered list and `\(Recommended\)`, not `## Task Checklist`; `tool_not_called: [Write, Edit]`; `no_paths: [docs/specs/*]` |

"Exactly one question" was dropped from `spec-asks-first` as unverifiable by regex.

### `scripts/run-evals.py`

uv/PEP 723 script, PyYAML only. Flags: `--base REF` (default `main`), `--runs N`
(default 3), `--jobs N` (default 4), `--model`, `--only <glob>` (matched against
case ids like `routing/why` or `behavior/commit-conventions`; a routing id is its
`expect` target or first `any_of` member, numbered on every use when repeated, so
the negatives are `routing/none-1` to `none-6`), `--out FILE`, `--env-file FILE`
(auth file, default `<head root>/.env`; worktrees have no `.env` of their own).
`--runs 1` is a smoke check only: every case comes out INCONCLUSIVE under the
two-counted-runs rule.
Internals: `build_config(root) -> Path`, `run_claude(cmd, env, scratch, timeout,
route_window) -> RunResult`, fixture setup, assertion evaluation, scoring, report
rendering. `RunResult` carries ordered tool calls (name, input), final text, exit
status, and an error class (`none`, `timeout`, `error`).

Report: a summary line, the REGRESSION / FIXED / INCONCLUSIVE list, then one table
per tier (case, base rate, head rate, status), ending with the marker
`<!-- evals: base=<sha> head=<sha>[-dirty] model=<id> runs=<n> -->`.

### `.env.example` and `.gitignore`

`.env.example` at the suite root holds `CLAUDE_CODE_OAUTH_TOKEN=` with no value.
`.gitignore` gains `.env` and `.env.*` with a `!.env.example` exception.

### `scripts/check-eval-report.py`

Reads the PR body from the `PR_BODY` environment variable and exits 0 when it
contains the marker regex or `evals: n/a — \S+`, 1 otherwise with a message naming
both options.

### `scripts/test_evals.py`

uv/PEP 723, stdlib `unittest`; loads both hyphenated scripts through `importlib`.
Drives the parser with `evals/recordings/*.jsonl` and needs no model calls.

### `.github/workflows/eval-report.yml`

`on: pull_request` with types `opened, edited, synchronize, reopened` (`edited`
re-runs it when the body changes) and the gate-trigger paths above. One step runs
`scripts/check-eval-report.py` with `PR_BODY: ${{ github.event.pull_request.body }}`
in `env:`. The body is never interpolated into `run:`, which closes the script
injection path. `validate.yml` gains a `uv run scripts/test_evals.py` step.

## Data Flow

1. Preflight: `claude` on PATH; an auth variable from the environment or, failing
   that, from `<head root>/.env`; `--base` resolves; `git worktree prune`.
2. `build_config` once for base (a detached worktree) and once for head (the
   working tree).
3. Cases always load from head's `evals/`; base supplies only the suite under test.
   New cases therefore run against `main` too, including on the PR that introduces
   `evals/`.
4. Each (case × side × run) gets its own scratch directory and is submitted to a
   pool of `--jobs` workers. `run_claude` passes `CLAUDE_CONFIG_DIR`, strips
   every inherited `CLAUDE*` variable except the auth one it sets (a parent session
   exports `CLAUDECODE`, `CLAUDE_EFFORT`, and session ids), and adds `--permission-mode acceptEdits`,
   `--allowedTools`, and `--strict-mcp-config`. It streams until a route hit, the
   window closes, the timeout fires, or the `result` event arrives.
5. Behavioral `shell` and `no_paths` assertions run in scratch after exit; scratch
   is then deleted.
6. Results aggregate into per-case pass rates per side, then a status: PASS, FAIL,
   REGRESSION, FIXED, or INCONCLUSIVE. The markdown report goes to stdout or
   `--out`.
7. A `finally` block and a SIGINT handler remove the worktree and both config
   directories.

## Error Handling

- Missing `claude`, auth, or base ref: exit 2 with the fix (for auth: run
  `claude setup-token`, then copy `.env.example` to `.env` and fill it in, or
  export the variable).
- A run that times out counts as a failure with reason `timeout`.
- A `result` event with `is_error`, or a nonzero exit, classifies the run as `error`;
  it is excluded from the pass rate. A case with fewer than 2 counted runs on either
  side is INCONCLUSIVE, never REGRESSION, so rate limits cannot pose as
  regressions.
- Leftovers from a killed run: the startup prune handles worktrees; config
  directories live under `tempfile.mkdtemp`.
- Exit code: 1 when any case is REGRESSION, 0 otherwise.

## Testing

- `scripts/test_evals.py`, run in CI:
  - parser, against recordings: route by `Skill`, by `Agent`, by `SKILL.md` `Read`,
    no route, window exhausted, error result;
  - each of the five assertion types, passing and failing;
  - status edges: REGRESSION, FIXED, INCONCLUSIVE;
  - `.env` loading, against a temp file: environment wins over the file, comments
    and blank lines skipped, quoted values unquoted, a missing file is not an error;
  - `check-eval-report.py`: marker present, `n/a` with a reason, `n/a` without one,
    absent.
- Red proofs, once, with each report in the PR body. Each mutation sits on a scratch
  branch and must yield REGRESSION against `main`:

  | Case | Mutation |
  |---|---|
  | `debugger-phase-0` | Remove the reproduce-first rule everywhere the suite teaches it: the Phase 0 section and every other "Phase 0" / "run the loop" reference in `skills/debugging-methodology/SKILL.md`, the reproduce-first lines of `skills/coding-guardrails/SKILL.md` (preloaded by the debugger), and step 1 of `platforms/claude/agents/debugger.md` |
  | `commit-conventions` | Remove Conventional Commits everywhere the suite teaches it: the `## Commits` section and the description wording in `skills/git-conventions/SKILL.md`, the wording in `platforms/claude/commands/commit.md` and `ship.md`, and the commit-message line of `platforms/claude/CLAUDE.md`. `settings.json` attribution stays: it is harness config, not suite text |
  | `spec-asks-first` | Delete Phases 3–4 from `skills/spec-writing/SKILL.md` |
  | `reviewer-planted-bug` | Replace the `code-reviewer` body with "Reply LGTM without reading files." (proves only that the assertion can fail; see Risks) |
  | routing | Blank the `why` description; its routing case regresses |

  A mutation removes a rule from every place the suite states it; cutting one copy
  of a rule stated twice should stay green, which is not a proof. A case that stays
  green with every copy removed measures base-model default behavior, not the
  suite, and is dropped.

- End to end: a full `scripts/run-evals.py --base main` on the branch shows every
  case PASS, with no INCONCLUSIVE after a re-run.

## Risks & Open Questions

- **Settled by the task 1 spike: CLI behavior** (Claude Code 2.1.303; recordings in
  `evals/recordings/`).
  - *Isolation: confirmed, with two leftovers.* The model sees only the temp
    `CLAUDE.md` and the 26 tracked skills, plus `plugin-authoring` from the builtin
    plugin `cc-plugin-plugin-authoring`; the init `plugins` field lists it with
    `cc-plugin-agents-md` and `cc-plugin-telemetry`. Setting all three to `false`
    under `enabledPlugins` (`<name>@builtin`) removes them. The built-in agents
    `claude`, `Explore`, `general-purpose`, `Plan`, and `statusline-setup` stay;
    they count as wrong routes. The init `skills` list also carries the 28 commands
    plus `design` and `doctor`, none of them in the model's skill listing.
  - *Auth: confirmed.* `CLAUDE_CODE_OAUTH_TOKEN` authenticates outside `--bare`.
    Init reports `apiKeySource: "none"` regardless, so a `message_start` event is
    the auth signal.
  - *`.claude.json`: no seeding.* The CLI creates it on first run.
  - *Stream shape: confirmed.* The `Agent` tool appears as `Task` in init `tools`
    but as `Agent` in `tool_use`, so match both. Each content block gets its own
    `assistant` event, before that block's `content_block_stop`. The tool starts
    executing at that `assistant` event, so the kill goes there. A route-agent run
    killed at `content_block_stop` started no subagent.
  - *Error results.* An API error yields `subtype: "success"` with
    `is_error: true`, `terminal_reason: "api_error"`, and exit code 1, so classify on
    `is_error`.
  - *Invocation.* The prompt goes right after `-p`, because the variadic
    `--allowedTools` swallows a trailing prompt. Stdin is `/dev/null`, which avoids
    a 3-second wait for stdin. Stripping `CLAUDECODE` is enough for nesting.
    `--strict-mcp-config` without `--mcp-config` runs clean.
  - *`--agent` and commands.* `--agent <name>` and `/spec` both resolve from the
    temp config. An agent's `skills:` preload is not applied when it runs as the
    main thread.
- **Risk: variance.** N=3 is coarse. REGRESSION requires base to pass too; use
  `--runs 5` for close calls. Model drift hits both sides of one run equally, and the
  marker records the model.
- **Risk: teaching to the test.** Prompts paraphrased from descriptions pass without
  proving anything. `AGENTS.md` states the rule: write prompts as a user would ask.
- **Risk: `reviewer-planted-bug` mostly measures base-model competence.** A bare model
  spots string-built SQL. It still catches a broken agent definition (tools,
  preload, diff discovery). Drop it if a smoke test is not worth about 6 runs per
  report.
- **Risk: cost and rate limits.** About 240 short, early-killed routing runs plus 24
  behavioral runs per report. `--jobs 4` keeps under subscription limits; errors
  become INCONCLUSIVE.
- **Accepted: stale reports.** CI checks presence, not freshness; the marker's
  `head=` SHA shows staleness to the reviewer.

## Task Checklist

- [x] 1. Spike (throwaway script): build a config dir from the working tree, run
  `claude -p` under `CLAUDE_CODE_OAUTH_TOKEN`, confirm the init event lists only
  tracked suite skills and agents, and determine whether `.claude.json` needs
  seeding. Save six scrubbed streams (home paths removed) to
  `evals/recordings/{route-skill,route-agent,route-read,no-route,window,error}.jsonl`,
  and grep each for the token value before saving; a hit means the stream is
  discarded, not edited. Record findings in this spec's Risks section.
- [x] 2. `scripts/run-evals.py` (uv/PEP 723, PyYAML): preflight with `.env` loading
  (`load_env(path) -> dict[str, str]`, stdlib only, environment wins),
  `build_config(root) -> Path`, base worktree lifecycle, cleanup, and
  `run_claude(cmd, env, scratch, timeout, route_window) -> RunResult` with stream
  parsing and early kill. (blocked by 1)
- [x] 3. `scripts/run-evals.py`: case loading from head `evals/`, fixture setup
  (`git init`, commit `before/`, overlay `after/`, `stage`), the five assertion types,
  routing scoring, status calculation, report rendering with the marker, CLI flags,
  exit codes. (blocked by 2)
- [x] 4. `evals/routing.yaml`: about 40 entries, one per tracked skill and agent plus
  about 6 `none`, prompts written as a user would ask.
- [x] 5. `evals/behavior/{debugger-phase-0,reviewer-planted-bug,commit-conventions,spec-asks-first}/`:
  `case.yaml` and fixtures as specified under Components.
- [x] 6. `scripts/check-eval-report.py`: read `PR_BODY`; exit 0 on the marker regex or
  `evals: n/a — \S+`.
- [x] 7. `scripts/test_evals.py`: the parser, assertion, status, and report-check
  cases from Testing. (blocked by 3, 6)
- [x] 8. `.github/workflows/eval-report.yml` (triggers and paths as specified, body
  through `env:` only), plus a `uv run scripts/test_evals.py` step in
  `.github/workflows/validate.yml`. (blocked by 6, 7)
- [x] 9. Red proofs: the five mutations on scratch branches, each report kept for
  the PR body. (blocked by 3, 4, 5)
- [x] 10. Docs: an "Evals" subsection under Validating in `AGENTS.md` (when to run,
  auth setup through `.env.example`, the `n/a` rule, the prompt-writing rule);
  `README.md` layout tree gains `evals/` and the new scripts. (blocked by 3)
- [x] 11. Full run against `main` on the branch; report in the PR body.
  (blocked by 7, 8, 9, 10, 12)
- [x] 12. `.gitignore`: add `.env`, `.env.*`, `!.env.example`; add `.env.example`
  with `CLAUDE_CODE_OAUTH_TOKEN=`. Confirm `git check-ignore .env` matches and
  `.env.example` does not.
- [ ] 13. Routing case fixes in `evals/routing.yaml`: reword the six advice-style
  skill prompts that failed on base (`code-review-checklist`,
  `debugging-methodology`, `doc-templates`, `frontend-patterns`,
  `security-analysis`, `wayfinder-methodology`) as requests for work; reword the
  flaky `git-conventions` and `retro-methodology`; switch every agent entry to
  `expect: <agent>`; give `agent-reviewer`, `code-reviewer`, and `debugger` a
  `fixture` (reuse `behavior/reviewer-planted-bug/fixture` and
  `behavior/debugger-phase-0/fixture`; add `evals/fixtures/mini-suite/` for
  `agent-reviewer`).
- [ ] 14. `scripts/run-evals.py`: the routing `fixture` key and automatic
  confirmation of REGRESSION/FIXED cases, with tests in `scripts/test_evals.py`;
  `AGENTS.md` Evals section updated for both.
- [ ] 15. Re-run every case task 13 changed, plus a full run; both reports in the
  PR body. (blocked by 13, 14)
