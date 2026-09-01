# agent-suite

A custom suite of software engineering agents, skills, and commands, shared across
Claude Code, OpenCode, and Codex.

Extracted from the `dotfiles` repo — it was `claude/.claude/` and the agent-suite
half of `opencode/.config/opencode/`, with its history intact.

## Repo Layout

```text
agent-suite/
├── AGENTS.md               # How to work on this repo (not any harness's instructions)
├── agents/                 # Specialist subagent definitions
├── skills/                 # Skills — methodology skills plus the /-command workflows
├── platforms/
│   ├── claude/             # Claude Code's view: CLAUDE.md (it uses the canonical trees)
│   ├── codex/              # Codex's view: AGENTS.md + skills/ (symlinks into skills/)
│   └── opencode/           # OpenCode's view: agent/, commands/, AGENTS.md, skills/ (symlinks)
└── scripts/
    └── validate-config.py  # Reference integrity, index accuracy, shared-skill links
```

The top level is the canonical suite. `platforms/` holds each harness's view of it:
an index document written for that harness, skill directories symlinked back into
`skills/`, and whatever else it needs in its own shape — OpenCode keeps commands in
their own tree rather than as skills, and has its own agent definitions. Claude Code
consumes the canonical trees whole, so only its index is platform-specific.

## Working here

`skills/<name>/` is the single source of truth for every shared skill, and each
platform's copy is a **symlink** to it — so there is nothing to sync and drift is
impossible. Every skill carries a `name:` matching its directory, which is what lets
one file serve all three harnesses: OpenCode's loader requires the key, Claude Code
treats it as a display name, and Codex falls back to the directory name.

Editing `skills/<name>/SKILL.md` changes it everywhere at once.

`scripts/validate-config.py` is the broader check — reference integrity (agent → skill,
command → agent, skill → reference file), index accuracy across the three index documents, frontmatter validity, and shared-skill link integrity. It runs
in CI via `.github/workflows/validate.yml`. Run it after any change to an agent, skill,
command, or either index document:

```sh
scripts/validate-config.py        # list every check and what it covered; exit 1 on any problem
scripts/validate-config.py -q     # only failures and the summary, for a git hook
```

One skill is deliberately not shared and stays a real directory on both sides:
`agent-authoring`, which documents each platform's own schemas. Sharing is otherwise
opt-in by existence — a platform gets a skill only if someone creates the symlink —
which is why the `/`-command workflow skills, being Claude Code-specific, appear
under `skills/` but in no platform tree.

## Installation

Consumed as a git submodule by the `dotfiles` repo, which symlinks these directories
into the paths each harness expects and applies them with GNU Stow. Nothing here is
stowed directly.

## Conventions

- Commits use Conventional Commits, scoped by area (`feat(skills):`, `chore(scripts):`).
- Changes to a shared skill touch both the canonical and platform copies, and must be
  committed together under the `skills` scope.
- Never read or commit secret-bearing files (`.env`, keys, credentials).

## Acknowledgments

The suite draws inspiration from Matt Pocock's
[skills](https://github.com/mattpocock/skills) repo (MIT) — several skills (`skill-design`,
`code-review-checklist`, `domain-modeling`, the grill skills, and the wayfinder skills)
adapt material from it directly.

It also draws on Cursor's [pstack](https://github.com/cursor/plugins/tree/main/pstack)
skills. The `unslop`, `why`, and `blast-radius` skills, the `coding-guardrails` principle
references (type-system discipline, idempotency, build-the-lever, encode-lessons-in-structure),
and the `doc-templates` framework guidance (Diátaxis, Simplified Technical English) are
independent reimplementations of ideas from it — reworked in our own words, since that repo
carries no license.

## License

MIT — see [LICENSE](LICENSE). Third-party attribution is in [NOTICE](NOTICE):
portions of the suite are adapted from
[mattpocock/skills](https://github.com/mattpocock/skills), also MIT.
