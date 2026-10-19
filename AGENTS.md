# agent-suite

The agents, skills, and commands shared across Claude Code, OpenCode, and Codex.
Read this before changing anything here.

This file is repo instructions — how to work *on* the suite. It is not any harness's
operating instructions; those live in `platforms/<harness>/`.

## How this repo is structured

```text
skills/                 canonical skills — the single source of truth
platforms/
  claude/               Claude Code's index, its agents, and its commands
  codex/                Codex's index, plus its skill links
  opencode/             OpenCode's index, its own agents and commands, plus skill links
evals/
  routing.yaml          routing cases: a prompt and the skill or agent it should load
  behavior/<case>/      behavior cases: case.yaml plus a fixture repo
  recordings/           captured CLI streams the eval tests parse
scripts/                validate-config.py, run-evals.py, check-eval-report.py, test_evals.py
```

The top level is canonical. A platform directory holds that harness's **view**: an
index document, skill directories symlinked back to `skills/`, and anything the
harness needs in a shape the canonical tree does not provide.

Skills are the only canonical tree. Claude Code has no skill directory of its own
because it consumes that tree whole; its index, agents, and commands are the
platform-specific part. Agent rosters are per-platform because nothing has ever
been shared between them — each harness has its own frontmatter schema, and the
two rosters have diverged in both size and membership.

An agent must earn its slot by a capability, not by a topic. If a definition only
carries a persona and preloads a skill, it is a skill and a command, not an agent
— an agent is worth its always-loaded description only when it expresses something
instructions cannot: tool restrictions the harness enforces, an MCP server,
persistent memory, or a model pin. Claude Code's roster holds to this. OpenCode's
does not, deliberately: it routes every command structurally with `agent:` plus
`subtask: true`, which makes a per-topic agent the unit that routing acts on.

Commands are not skills. A command is a single `.md` file under
`platforms/<harness>/commands/`, invoked only by the user as `/name`, and it is
platform-specific by nature — it names that harness's agents and uses its
invocation syntax. Claude Code's set carries `disable-model-invocation: true`, which
is the whole point of keeping them as commands: the harness enforces explicit-only
invocation rather than an index asking the model nicely.

## Editing skills

`skills/<name>/SKILL.md` is the only place a shared skill is edited. Every platform
copy is a symlink to it, so one edit lands everywhere and drift is impossible.

Every skill carries `name:` matching its directory. That single key is what lets one
file serve all three harnesses: OpenCode's loader requires it, Claude Code treats it
as a display name, Codex falls back to the directory name when it is absent.

Two rules follow:

- **Never edit a platform's copy.** It is a symlink; you are editing the canonical
  file without realising which one you changed.
- **Keep shared content harness-neutral.** No tool names, invocation syntax, or
  machinery specific to one harness. Anything that cannot be said neutrally belongs
  in a platform's index, not in a skill.

Harness-specific schemas live in `agent-authoring/reference/<harness>.md`, so
even that skill is shared; its core stays neutral.

Sharing a skill with a platform is opt-in by existence: create
`platforms/<harness>/skills/<name>` as a symlink to `../../../skills/<name>`.
`skill-design` is shared with no platform: it is guidance for writing the skills in
this repo, not for doing work with them.

## Index documents

Each platform has one, and each describes only what that harness actually has.
Do not port machinery across: an index that explains an agent roster to a harness
with no agent roster spends context on an absence and invites the model to reach
for something that is not there.

What they must agree on is the description of a shared skill — the validator
enforces that a skill's row reads identically in every index that lists it.

## Validating

Run after any change to an agent, skill, command, or index document:

```sh
scripts/validate-config.py        # every check and what it covered; exit 1 on a problem
scripts/validate-config.py -q     # only failures and the summary
```

It covers reference integrity (agent → skill, command → agent, skill → reference
file), index accuracy in both directions, frontmatter validity and known keys, tool
names, color uniqueness, bare injection lines, description parity across indexes,
and that every platform skill directory is a live symlink into `skills/`. It runs
under `uv`, the one prerequisite, which supplies PyYAML from the script's inline
metadata. CI runs it on every push, and `.githooks/pre-commit` runs it before any
commit touching `skills/`, `platforms/`, or `scripts/` once `core.hooksPath` points
at `.githooks` (the dotfiles `make install` sets that).

For the schemas and file layout of agents, skills, and commands, use the
`agent-authoring` skill — it is the source of truth for frontmatter keys and
conventions.

### Evals

The validator checks structure. It cannot tell whether a request still loads the
right skill, or whether `/debugger` still reproduces a bug before editing. The evals
check that behavior. Routing cases send a prompt and check which skill or agent
loads. Behavior cases run a command against a fixture repo and assert on its tool
calls, final text, and the files it leaves.

Run them on any PR that touches `skills/` or `platforms/`, and paste the report into
the PR body:

```sh
scripts/run-evals.py --base main            # every case, 3 runs per side
scripts/run-evals.py --only 'behavior/*'    # case ids matching a glob
```

The runner builds one Claude Code config from `--base` and one from the working
tree, uncommitted edits included, and runs every case against both. A PR that
changes no behavior carries `evals: n/a — <reason>` instead. CI's `eval-report`
workflow makes no model calls: it fails a PR whose body has neither the report's
closing marker nor that line. Changes only to `skills/synced/` or
`platforms/claude/settings.json.example` do not trigger it.

The runner needs `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY`. Create a token
with `claude setup-token`, then export it or copy `.env.example` to `.env` and fill
it in. A variable already in the environment wins over the file. The runner reads
`.env` itself and passes the token only to the `claude` processes it starts, so an
agent running the evals never sees it. A worktree has no `.env` of its own; pass
`--env-file` with the main checkout's.

Each case runs `--runs` times per side (default 3), and a side passes at two thirds
of its counted runs. Runs that end in an error, such as a rate limit, are not
counted; timeouts count as failures.

| Status | Meaning |
|---|---|
| PASS | Both sides pass |
| FAIL | Both sides fail, so the failure predates this change |
| REGRESSION | Base passes, head fails; the runner exits 1 |
| FIXED | Base fails, head passes |
| INCONCLUSIVE | A side has fewer than 2 counted runs; re-run the case |

Three runs are coarse. Before acting on a close call, re-run that case with
`--only <id> --runs 5`. `--runs 1` is a smoke check only: every case comes out
INCONCLUSIVE. An isolation warning means a plugin loaded alongside the suite and
may have competed for routes.

To add a routing case, add an entry to `evals/routing.yaml`: `expect: <name>`,
`any_of: [..]` when several targets are honestly correct, or `expect: none` for a
prompt that should load nothing. A behavior case is a directory
`evals/behavior/<case>/` holding `case.yaml` and an optional `fixture/` with
`before/` (committed) and `after/` (left uncommitted, or staged with `stage: true`).
`case.yaml` takes `prompt`, `allowed_tools`, `timeout` (seconds), `stage`, and
`assert`, and no other keys. The assertions are `order`, `tool_not_called`,
`final_text`, `shell`, and `no_paths`; the eval spec in `docs/specs/` defines their
shapes, and the existing cases show each in use.

Write prompts the way a user would ask: concrete, specific, often terse. Never
paraphrase the target's description. A prompt that echoes the description passes
without showing that real requests reach the target.

`scripts/test_evals.py` tests the runner's stream parser, assertions, and scoring,
plus the report check, against `evals/recordings/`. It makes no model calls and runs
in CI; run it after changing either eval script.

## Conventions

- Conventional Commits, scoped by area: `feat(skills):`, `fix(agents):`,
  `docs(codex):`, `build(scripts):`.
- Keep commit messages and PR descriptions short — a subject line and a few lines of
  why. Never attach a TODO list or suggested follow-up work.
- Never append attribution footers to commits or PR descriptions.
- Never read or commit secret-bearing files (`.env`, keys, credentials).
