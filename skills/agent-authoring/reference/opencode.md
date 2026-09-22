# OpenCode Reference

Frontmatter, permissions, and routing for OpenCode artifacts. Paths are relative to
`~/.config/opencode/`; in this repo that maps to `platforms/opencode/`.

## Agent Frontmatter

```yaml
---
description: One-sentence summary of the agent's purpose.
mode: subagent
permission:
  edit: allow
  bash: allow
  task:
    "*": deny
color: "#e06c75"
---
```

| Key | Description |
|---|---|
| `description` | Required. Displayed in listings and injected at runtime. |
| `mode` | `primary` (session-level, reachable via Tab; this suite has tech-lead and architect) or `subagent`. |
| `permission` | Required. See below. |
| `color` | Six-digit hex, required, unique across the roster. |
| `hidden` | Subagents only; hides from `@` autocomplete, still reachable via Task. |
| `temperature`, `top_p`, `steps`, `model` | Available; omit to inherit defaults. |

OpenCode has no preload field. An agent loads skills at runtime through the skill
tool, so its body names the skills to load.

### Permission patterns

Write agent, the suite default for implementation:

```yaml
permission:
  edit: allow
  bash: allow
  task:
    "*": deny
```

Read-only agent:

```yaml
permission:
  edit: deny
  bash: allow
  task:
    "*": deny
```

`edit: deny` is the enforced guarantee. Bash stays open, so the body states the
restraint in words. `task: "*": deny` keeps subagents from spawning subagents; the
primaries keep delegation (architect narrows its own block to explore,
code-reviewer, and security-analyst). Per-agent permissions narrow the global
baseline and cannot widen it.

Bash accepts a deny-by-default allowlist of command prefixes when an agent needs a
narrower shell:

```yaml
permission:
  bash:
    "*": deny
    "git diff*": allow
    "git log*": allow
```

Treat interpreter, package-manager, and container prefixes as high-trust even
inside an allowlist, and keep the index's permission column in step with what the
file enforces. Other keys: `webfetch` (`allow`, `ask`, `deny`), `skill` (name
patterns), `question`.

## Skill Frontmatter

```yaml
---
name: skill-directory-name
description: What the skill covers and when to load it.
---
```

`name` is required by the loader and must match the directory. `argument-hint` is
tolerated on the shared skills that carry it.

## Command Frontmatter

```yaml
---
description: What the command does.
agent: agent-identifier
subtask: true
---
```

| Key | Description |
|---|---|
| `description` | Required. |
| `agent` | Routes the command. Omit to run as the current agent (`/loop`, `/zoom-out`). Naming a `mode: primary` agent without `subtask` switches the live session to it, which is the shape for dialogue-driven commands (`/spec`, `/grill`, `/architecture`, `/wayfinder`, `/prototype`). |
| `subtask` | `true` runs the command as a delegated subtask that reports back. Self-contained work only; never for a command that must converse mid-run. |

`/full-review` routes tech-lead as a subtask, which works only because tech-lead
carries no task deny. Body conventions match Claude's: short instruction, injected
state via `` !`command` ``, `$ARGUMENTS` last.

## Colors

One Dark palette, all in use:

| Hex | Agent |
|---|---|
| `#e06c75` | code-reviewer |
| `#be5046` | security-analyst |
| `#98c379` | tester |
| `#e5c07b` | debugger |
| `#61afef` | documenter |
| `#c678dd` | devops-engineer |
| `#528bff` | backend-engineer |
| `#d19a66` | git-manager |
| `#56b6c2` | frontend-engineer |
| `#8fbcbb` | frontend-auditor |
| `#7f848e` | database-specialist |
| `#abb2bf` | agent-builder |
| `#b48ead` | agent-reviewer |
| `#83a598` | architect |
| `#c8ccd4` | tech-lead |

## Index

`platforms/opencode/AGENTS.md` lists agents, skills, and commands. A new artifact
of any kind needs a row; a shared skill's description must match the Codex index
row exactly, which the validator enforces.
