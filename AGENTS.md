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
scripts/                validate-config.py
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

`agent-authoring` is the one deliberate exception — a real directory on both the
canonical and OpenCode sides, because it documents each harness's own schemas.

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
file), index accuracy in both directions, frontmatter validity, description parity
across indexes, and that every platform skill directory is a live symlink into
`skills/`. CI runs it on every push.

For the schemas and file layout of agents, skills, and commands, use the
`agent-authoring` skill — it is the source of truth for frontmatter keys and
conventions.

## Conventions

- Conventional Commits, scoped by area: `feat(skills):`, `fix(agents):`,
  `docs(codex):`, `build(scripts):`.
- Keep commit messages and PR descriptions short — a subject line and a few lines of
  why. Never attach a TODO list or suggested follow-up work.
- Never append attribution footers to commits or PR descriptions.
- Never read or commit secret-bearing files (`.env`, keys, credentials).
