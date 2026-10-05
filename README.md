# agent-suite

Software engineering agents, skills, and commands, shared across Claude Code,
OpenCode, and Codex.

Extracted from the `dotfiles` repo — it was `claude/.claude/` and the agent-suite
half of `opencode/.config/opencode/`, with its history intact.

## Repo Layout

```text
agent-suite/
├── AGENTS.md               # How to work on this repo (not any harness's instructions)
├── skills/                 # Canonical skills, the one shared tree
├── platforms/
│   ├── claude/             # Claude Code's view: CLAUDE.md, agents/, commands/, settings.json.example
│   ├── codex/              # Codex's view: AGENTS.md + skills/ (symlinks into skills/)
│   └── opencode/           # OpenCode's view: AGENTS.md, agent/, commands/, skills/ (symlinks)
└── scripts/
    └── validate-config.py  # Reference integrity, index accuracy, shared-skill links
```

`skills/` is the canonical tree. `platforms/` holds each harness's view of it: an
index document written for that harness, its own agents and commands where it has
them, and skill directories symlinked back into `skills/`. Claude Code consumes
`skills/` whole, so its view has no skill directory.

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
command, or any of the three index documents:

```sh
scripts/validate-config.py        # list every check and what it covered; exit 1 on any problem
scripts/validate-config.py -q     # only failures and the summary, for a git hook
```

Sharing is opt-in by existence — a platform gets a skill only if someone creates the symlink.

Commands are not shared at all. A command names its harness's agents and uses its
invocation syntax, so each platform keeps its own set: `platforms/claude/commands/`
and `platforms/opencode/commands/`.

## Installation

Consumed as a git submodule by the `dotfiles` repo, which symlinks these directories
into the paths each harness expects and applies them with GNU Stow. Nothing here is
stowed directly.

### Claude Code settings

`platforms/claude/settings.json.example` is the starting point for
`~/.claude/settings.json` — the deny list that keeps agents out of `.env` files and
private keys, the plugin set, and the runtime preferences.

The live file is **not** tracked. It is machine-local on purpose: which plugins and
marketplaces a machine enables is a property of that machine, and a work laptop
should be able to register a private marketplace without that path landing in a
public repo. `dotfiles` gitignores it.

`dotfiles` seeds it on `make install`, copying the example into the Stow package
when no settings file is there yet:

```sh
cp agent-suite/platforms/claude/settings.json.example claude/.claude/settings.json
```

That guard is there because Stow is silent about the gap — without it a fresh machine
stows cleanly and simply has no `~/.claude/settings.json`, secret-file deny list
included.

Nothing syncs the two afterwards. Update the example when a setting is worth carrying
to the next machine, and leave machine-local additions out of it.

## Conventions

- Commits use Conventional Commits, scoped by area (`feat(skills):`, `chore(scripts):`).
- A shared skill is edited only at `skills/<name>/`; sharing it with a new platform adds
  a symlink and an index row, committed together under the `skills` scope.
- Never read or commit secret-bearing files (`.env`, keys, credentials).

## Acknowledgments

The suite draws inspiration from Matt Pocock's
[skills](https://github.com/mattpocock/skills) repo (MIT) — several skills (`skill-design`,
`code-review-checklist`, `domain-modeling`, `retro-methodology`, `spec-implementation`,
the grill skills, and the wayfinder skills) adapt material from it directly. The PR
body guidance in `git-conventions` reworks ideas from Humanlayer's
[show-me](https://github.com/humanlayer/skills) skill (MIT), by way of that repo.

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
