# agent-suite

The agents, skills, and commands shared across Claude Code, OpenCode, and Codex.
Read this before changing anything here.

This file is repo instructions — how to work *on* the suite. It is not any harness's
operating instructions; those live in `platforms/<harness>/`.

## How this repo is structured

```text
agents/                 canonical agent definitions
skills/                 canonical skills — the single source of truth
platforms/
  claude/CLAUDE.md      Claude Code's index
  codex/                Codex's index, plus its skill links
  opencode/             OpenCode's index, its own agents and commands, plus skill links
scripts/                validate-config.py
```

The top level is canonical. A platform directory holds that harness's **view**: an
index document, skill directories symlinked back to `skills/`, and anything the
harness needs in a shape the canonical tree does not provide.

Claude Code has no skill or agent directory of its own because it consumes the
canonical trees whole — only its index is platform-specific.

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
`platforms/<harness>/skills/<name>` as a symlink to `../../../skills/<name>`. The
Claude-only workflow skills (the `/`-commands) are shared with no platform.

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
