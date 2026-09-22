# Claude Code Reference

Frontmatter, permissions, and routing for Claude Code artifacts. Paths are relative
to `~/.claude/`; in this repo that maps to `platforms/claude/` for agents and
commands and to `skills/` for skills.

## Agent Frontmatter

```yaml
---
name: kebab-case-name
description: When Claude should delegate to this subagent.
tools: Read, Glob, Grep, Bash
disallowedTools: Write, Edit, NotebookEdit
skills:
  - relevant-skill
memory: local
color: red
---
```

| Key | Description |
|---|---|
| `name` | Required; must match the filename here. |
| `description` | Required. Appears in the agent listing and drives auto-routing. |
| `tools` | Allowlist. Excludes everything unlisted, including `Skill`, so a read-only agent cannot load skills at runtime: preload them via `skills:`. |
| `disallowedTools` | Denylist applied before `tools` is resolved. |
| `skills` | Preloaded whole at startup. Cannot include a skill with `disable-model-invocation: true`. |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, a full ID, or `inherit` (default). Suite convention: omit, so the session model applies; pin only for deliberate cost routing. |
| `color` | One of `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`. Hex is rejected. Unique across the roster while it fits; the validator downgrades to a warning once it cannot. |
| `memory` | `user`, `project`, or `local`. `local` resolves from the working directory, so run agents from the repo root; `.claude/` is gitignored here for that reason. Read, Write, and Edit are documented as auto-enabled for the memory directory, but some harness builds withhold Write, so bodies say to fall back to Bash. |
| `mcpServers` | Names of configured servers, or inline definitions scoped to this agent. An inline definition keeps the server's tools out of the main conversation. |
| `permissionMode`, `maxTurns`, `hooks`, `effort`, `background`, `isolation`, `omitClaudeMd`, `initialPrompt` | Available; none used in this suite today. |
| `experimental.cacheTtl` | `5m` or `1h` for the subagent's prompt cache. Left at the default here: a one-hour write costs 2x base input versus 1.25x, and only pays off when the same agent is spawned again within the hour. |

Agents are loaded at session start; edits on disk need a new session.

### Permission patterns

Full access (implementation): omit `tools:` and `disallowedTools:`; preload the
always-needed skills. Read-only (analysis): `tools: Read, Glob, Grep, Bash` plus
`disallowedTools: Write, Edit, NotebookEdit`, and the body states that it does not
modify files, since Bash can still redirect and delete.

## Skill Frontmatter

```yaml
---
name: skill-directory-name
description: What the skill covers and when to load it.
argument-hint: [optional, when the skill takes an argument]
---
```

`description` drives the listing and auto-routing; put the trigger first, since the
listing truncates. `disable-model-invocation` is never set on a skill here: it
blocks the Skill tool and preloading, which are a skill's only routes. A user-only
workflow is a command instead.

## Command Frontmatter

```yaml
---
description: What the command does.
argument-hint: [free-form request]
disable-model-invocation: true
---
```

Every command sets `disable-model-invocation: true`; the validator fails without it.
That key is why commands are files here rather than skills: the harness enforces
explicit-only invocation instead of the index asking the model nicely. Avoid
shadowing a bundled skill's name; check the `/` menu. `/code-review` is claimed on
purpose and lists above the bundled one.

### Routing

| Shape | When | Effect |
|---|---|---|
| `context: fork` + `agent: name` | Self-contained analysis: review, audit, security, docs | Runs in the background on that agent, with no conversation history and no way to ask the user. Inject needed state with `` !`command` ``. |
| Prose: "Use the `@name` subagent to…" | Work that needs conversation context: debugging, implementation | The main conversation composes the delegation. |
| Neither | Dialogue-driven workflows and inline skill work | Runs in the main conversation with the skills the body loads. |

`agent:` without `context: fork` does nothing; the command runs inline.

### Body

```markdown
One to three sentences of instruction.

Injected state:
!`git status --short`

$ARGUMENTS
```

`` !`command` `` runs at invocation and is replaced by its output. `$ARGUMENTS`
takes the user's text after the command name; `$0`, `$1` address positions.

## Index

`platforms/claude/CLAUDE.md` lists commands only. The harness injects the skill
and agent listings from frontmatter, so those tables were removed; a new agent or
skill needs nothing there. A new command needs a row in the Commands table.
