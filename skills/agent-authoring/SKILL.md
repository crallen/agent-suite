---
description: Schemas, templates, conventions, and validation rules for creating Claude Code agents, skills, and slash commands.
---

# Agent Authoring Reference

This skill contains the exact schemas, conventions, and templates for authoring Claude Code agents, skills, and slash commands. Use it whenever creating or modifying these artifacts.

Paths below are relative to the Claude Code config root at `~/.claude/`. In a dotfiles repo, that root may be mirrored elsewhere (for example via GNU Stow), but the artifact layout stays the same.

## File Locations and Naming

| Artifact | Location | Naming Rule | Identifier |
|---|---|---|---|
| Agent | `agents/<name>.md` | kebab-case filename | Filename sans `.md` (becomes `@name`) |
| Skill (reference) | `skills/<name>/SKILL.md` | kebab-case directory name | Directory name |
| Skill (workflow/command) | `skills/<name>/SKILL.md` | kebab-case directory name | Directory name (becomes `/name`) |

This suite has no `commands/` directory: slash commands are implemented as **workflow skills** — `skills/<name>/SKILL.md` with `disable-model-invocation: true`. Legacy `commands/<name>.md` files still work in Claude Code but should not be created here. When naming a workflow skill, avoid shadowing bundled skills (`/debug`, `/review`, `/security-review`, `/run`, `/verify`, `/init`, `/loop`, `/batch`, `/simplify`, `/schedule`, `/claude-api`); when a workflow delegates to one agent and the natural verb is taken, name it after the agent (e.g., `/debugger`). One deliberate exception: this suite **intentionally claims** `/code-review` with its own workflow skill (which forks to `@code-reviewer`). The bundled `/code-review` still appears in the menu, but the personal skill lists above it and is selected by default — so `/code-review` runs ours. Do not rename it to dodge the bundled name; the collision is intentional.

Identifiers must be consistent across all references:
- Commands route to agents via the `agent:` frontmatter key (filename without `.md`) and/or via prose ("Use the `@name` subagent ...").
- Agents reference skills by directory name in prose (e.g., "Use the Skill tool to load `agent-authoring`").
- `CLAUDE.md` uses `@name` syntax when referencing agents.

## Agent Definition Schema

### Frontmatter

```yaml
---
name: kebab-case-name
description: One-sentence summary of when Claude should delegate to this subagent.
tools: Read, Glob, Grep, Bash
disallowedTools: Write, Edit, NotebookEdit
skills:
  - relevant-skill
color: red
---
```

| Key | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Unique identifier. Lowercase + hyphens. The filename does not have to match, but in this suite it must (convention). |
| `description` | string | Yes | When Claude should delegate to this subagent. Appears in the agent listing and informs auto-routing. |
| `tools` | comma-separated string | No | Allowlist of tools the agent can use. Omit to inherit the full tool set. Use the allowlist to scope read-only agents. **An allowlist excludes everything unlisted — including the `Skill` tool** (see permission patterns below). |
| `disallowedTools` | comma-separated string | No | Denylist applied on top of the inherited or allowlisted tool set. Useful for blocking write tools while keeping Bash. If both are set, `disallowedTools` wins. |
| `skills` | YAML list | No | Skills whose **full content is preloaded** into the agent's context at startup. The canonical way to wire skill-backed knowledge into an agent — required for agents whose `tools:` allowlist excludes `Skill`. Cannot preload skills with `disable-model-invocation: true`. |
| `model` | string | No | `sonnet`, `opus`, `haiku`, `fable`, a full model ID, or `inherit`. Defaults to `inherit` (the main conversation's model). **Suite convention: omit this key** so the user's session model selection applies to every agent; pin only for deliberate cost routing. |
| `color` | string | No | Word: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`. **Not** a hex code. |
| `permissionMode` | string | No | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, or `plan`. If the parent session uses `auto`, `acceptEdits`, or `bypassPermissions`, the parent mode takes precedence. |
| `maxTurns` | integer | No | Maximum agentic turns before stopping. |
| `memory` | string | No | Persistent cross-session memory directory: `user` (`~/.claude/agent-memory/<name>/`), `project` (checked in), or `local` (project-level, not checked in). Auto-enables Read/Write/Edit for the memory directory. |
| `mcpServers` | YAML list | No | MCP servers available to this agent: names referencing already-configured servers, or inline server definitions scoped to this agent only. |
| `hooks` | YAML map | No | Lifecycle hooks scoped to this agent (e.g., a `PreToolUse` command hook that validates Bash commands). |
| `effort` | string | No | `low`, `medium`, `high`, `xhigh`, or `max`. Overrides the session effort level. |
| `background` | boolean | No | `true` to always run as a background task. Background agents auto-deny permission prompts. |
| `isolation` | string | No | `worktree` to run the agent in a temporary git worktree (isolated repo copy, auto-cleaned if unchanged). |

Subagents are loaded at session start; agents added or edited on disk need a session restart (agents created via `/agents` take effect immediately).

### Permission Patterns

Claude Code's `tools:` key is an **unrestricted allowlist** — there is no granular per-command Bash scoping like OpenCode supports. Listing `Bash` grants arbitrary shell. Use one of these patterns:

#### Full access (implementation agents)

Omit `tools:` and `disallowedTools:`. The agent inherits the full tool set, including the Skill tool for loading situational skills on demand. Preload the skills it always needs via `skills:`.

```yaml
---
name: backend-engineer
description: Implements backend application code ...
skills:
  - backend-patterns
  - coding-guardrails
color: blue
---
```

#### Read-only (analysis agents that must not modify files)

Allowlist only the read/search tools, plus Bash if the agent needs git/lint/dependency commands. Add `disallowedTools:` to belt-and-suspenders the write tools in case Bash inheritance changes:

```yaml
---
name: code-reviewer
description: Reviews code for quality, security, performance, and best practices ...
tools: Read, Glob, Grep, Bash
disallowedTools: Write, Edit, NotebookEdit
skills:
  - code-review-checklist
  - coding-guardrails
color: red
---
```

**The allowlist excludes the `Skill` tool**, so a read-only agent cannot load skills at runtime. Any skill the agent depends on must be preloaded via the `skills:` field; its body should say the skill is "preloaded into your context," never "use the Skill tool." (Skill reference files such as `reference/*.md` are still reachable through the Read tool.)

Bash remains powerful — shell `>` redirects, `rm`, `mv`, `sed -i`, etc. all stay available. The prose body of read-only agents must explicitly forbid file modification ("You do NOT modify files — you only read and analyze.").

#### Write but no Bash (rare)

```yaml
tools: Read, Glob, Grep, Edit, Write
```

Use when the agent should be able to author files but never run shell commands.

### Body Structure

Follow this template for the markdown body (after the closing `---` of frontmatter):

```markdown
You are a senior [role title]. Your job is to [primary responsibility in one sentence].

## How You Work

1. **Step one** - Description of the first phase of the agent's workflow.
2. **Step two** - Reference preloaded skills: "The `skill-name` skill ([what it provides]) is preloaded into your context." For situational skills on full-access agents: "Use the Skill tool to invoke `skill-name` when [condition]."
3. **Step three** - The core work phase.
4. **Step four** - Verification, output, or handoff.

## [Domain-Specific Section]

Content covering the agent's domain expertise: categories, principles, techniques, etc.

## Output Format (optional — for analysis agents)

Structure your [report/review/analysis] as:

[Template with severity levels, sections, etc.]

## Guidelines

- Behavioral rule one.
- Behavioral rule two.
- Always read existing [artifacts] before creating new ones.
```

Key conventions:
- **Opening line**: Always starts with "You are a senior [role]." followed by "Your job is to [verb]."
- **How You Work**: Numbered steps. Reference the Skill tool here for loading procedural knowledge.
- **Domain sections**: One or more sections with the agent's area-specific knowledge.
- **Output Format**: Only for analysis/reporting agents (code-reviewer, security-analyst). Includes severity levels and structured templates.
- **Guidelines**: Always the last section. Bullet list of behavioral rules and guardrails.

## Skill Definition Schema

### Frontmatter

```yaml
---
description: One-sentence description of the skill's content and when to load it.
---
```

| Key | Type | Required | Description |
|---|---|---|---|
| `description` | string | Recommended | What the skill does and when to use it. Drives auto-routing. Put the key use case first — combined `description` + `when_to_use` text is truncated at 1,536 characters in the skill listing. |
| `when_to_use` | string | No | Extra routing context: trigger phrases or example requests. Appended to `description` in the listing. |
| `name` | string | No | Display name in skill listings only. The directory name remains the `/command` identifier — this suite omits `name:` and relies on the directory name. |
| `disable-model-invocation` | boolean | No | Set `true` so only the user can invoke it (use for side-effectful workflows like commit/release). Also blocks preloading via an agent's `skills:` field — never set it on skills that agents preload. |
| `user-invocable` | boolean | No | Set `false` to hide from the `/` menu. Use for background knowledge that isn't a meaningful user action. |
| `argument-hint` | string | No | Autocomplete hint for expected arguments, e.g. `[issue-number]`. |
| `arguments` | list | No | Named positional arguments usable as `$name` substitutions in the body. |
| `allowed-tools` | string/list | No | Tools pre-approved while the skill is active. Supports rule specifiers, e.g. `Bash(git add *) Bash(git commit *)`. |
| `disallowed-tools` | string/list | No | Tools removed from the pool while the skill is active. |
| `model` / `effort` | string | No | Model or effort override for the rest of the turn while the skill is active. |
| `context` | string | No | `fork` to run the skill in an isolated subagent context (see command schema below). |
| `agent` | string | No | Which agent type executes the skill when `context: fork` is set. |
| `paths` | string/list | No | Glob patterns limiting auto-activation to work on matching files. |
| `hooks` | map | No | Hooks scoped to this skill's lifecycle. |

The directory name (`skills/<name>/`) is the canonical identifier you type after `/`.

### Body Structure

Skills are **reference documents**, not personas. They contain structured knowledge that agents load on demand.

```markdown
# Skill Title

Brief introduction (1-2 sentences) explaining what this skill covers and when to load it.

## Section One

Reference content: tables, rules, patterns, examples.

### Subsection

More detailed content. Use:
- **Tables** for quick-reference data (commit types, severity levels, coverage targets)
- **Code blocks** with language tags for examples
- **Checklists** (`- [ ]`) for audit/review workflows
- **Numbered steps** for ordered processes

## Section Two

Additional reference content.

## Anti-Patterns (optional)

What NOT to do. Common mistakes to avoid.
```

Key conventions:
- **No persona statements**. Skills never say "you are..." — they are pure reference material.
- **Dense and scannable**. Use headings, tables, code blocks, and bullet points liberally.
- **Actionable examples**. Include real code examples, command snippets, and templates.
- **Self-contained**. A skill should provide everything an agent needs without requiring additional context lookups.
- **Open with `# H1 Title`**. Every skill body starts with a single H1 matching the skill's purpose, followed by a 1-2 sentence intro. Avoid jumping straight into an H2.
- Skills typically range from 90-250 lines; keep `SKILL.md` under 500 lines (official guidance). For larger reference material, split into `SKILL.md` (router) plus `reference/*.md` files loaded on demand.
- **Preloadable**. Skills consumed via an agent's `skills:` field are injected whole at startup — keep them lean, and push rarely-needed depth into `reference/*.md` files the agent Reads on demand.

### Reference-File Pattern

When a skill's domain is too large for a single file, split it:

```
skills/<name>/
├── SKILL.md         # Router: index of references and when to load each
└── reference/
    ├── topic-a.md
    ├── topic-b.md
    └── topic-c.md
```

The router `SKILL.md` should map task shapes to the reference files an agent should load. See `frontend-patterns/SKILL.md` for the canonical example.

## Cross-Cutting Skill Expectations

Some skills are domain-specific (`docker-best-practices`, `frontend-patterns`). Others should be reused across multiple agents rather than re-explained in every file.

- **`coding-guardrails`** - Default cross-cutting skill for agents that write, refactor, fix, or review code/configuration. Covers assumption management, simplicity, surgical diffs, and verification-driven execution.
- **`spec-writing`** - Default cross-cutting skill for design-first planning agents.

Wire cross-cutting skills into agents via the `skills:` preload field rather than runtime Skill-tool instructions — preloading guarantees the guidance is present and works for read-only agents whose allowlist excludes the Skill tool.

## Workflow Skill (Command) Definition Schema

Custom commands have been **merged into skills**: a skill at `skills/<name>/SKILL.md` creates `/name`. This suite implements every slash command as a workflow skill with `disable-model-invocation: true` (user-triggered only). Unlike reference skills, workflow skills are short task prompts — they keep the command conventions below rather than the reference-skill body structure (no `# H1 Title` requirement).

### Frontmatter

```yaml
---
description: Short description of what the command does.
argument-hint: [free-form request]
agent: agent-identifier
context: fork
disable-model-invocation: true
---
```

| Key | Type | Required | Description |
|---|---|---|---|
| `description` | string | Yes | Short description displayed in `/help` and the command palette. |
| `argument-hint` | string | No | Autocomplete hint shown after the command name, e.g. `[issue description]`. Add it whenever the command accepts `$ARGUMENTS`. |
| `agent` | string | No | Agent identifier (filename without `.md`) to route the command to. When paired with `context: fork`, the command runs in that agent's isolated subagent context. |
| `context` | string | No | Set to `fork` to run the command in an isolated subagent context with no access to the conversation history. Pair with `agent:`. Only use when the body is a self-contained task (inject any needed state via `` !`command` ``). |
| `disable-model-invocation` | boolean | No | Set `true` to prevent the command from being auto-invoked by Claude — it becomes user-triggered only. |
| `allowed-tools` | comma-separated string | No | Tools pre-approved while this command is running. Supports rule specifiers like `Bash(git commit *)`. |

### Body Structure

```markdown
Instructional text telling the agent what to do (1-3 sentences).

Optional dynamic content:
!`shell command here`

Optional conditional/fallback logic in prose:
If [condition], do X. If [other condition], do Y.

$ARGUMENTS
```

Key conventions:
- **Dynamic content**: Use `` !`command` `` syntax to inject shell command output into the prompt at invocation time. The `!` backtick block evaluates the command and replaces itself with the output before Claude sees the content. The `!` must start a line or follow whitespace; use a ```` ```! ```` fenced block for multi-line commands.
- **`$ARGUMENTS`**: When the command accepts free-form user input, place `$ARGUMENTS` at the end. The user's text after the slash command (e.g., `/debug the login page crashes`) replaces it. Positional access is available via `$0`/`$1` (or `$ARGUMENTS[N]`), and `${CLAUDE_SKILL_DIR}` resolves to the skill's own directory for referencing bundled files.
- **Keep it short**. Workflow skills are prompts, not documentation. 5-15 lines total.
- **Multiple workflow skills can route to the same agent** (e.g., `/frontend`, `/frontend-polish`, and `/frontend-audit` route within the frontend workflow family).
- **Choose the routing style by context needs**. `agent:` + `context: fork` runs the skill body as the task in an isolated subagent — no conversation history, so inject any needed state via `` !`command` ``. Prose routing ("Use the `@name` subagent ...") runs in the main conversation, which composes a delegation message that can carry conversation context. Use fork for self-contained analyses (review, audit, security); use prose routing when the surrounding conversation matters (debugging, implementation).

## Color Palette

Claude Code colors are limited to a fixed set of names: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`. Hex codes are not supported.

Current assignments in this suite:

| Color | Currently used by | Semantic meaning |
|---|---|---|
| `red` | code-reviewer, security-analyst | Critical analysis, security |
| `green` | architect, tester, frontend-auditor | Planning, pass/fail, audit |
| `yellow` | debugger | Warnings, investigation |
| `blue` | backend-engineer, database-specialist | Application/data implementation |
| `purple` | devops-engineer | Infrastructure |
| `orange` | git-manager | Version control |
| `cyan` | documenter, frontend-engineer | Documentation, UI |
| `pink` | agent-builder, agent-reviewer | Meta/tooling |

With only 8 colors available, duplication across roles is unavoidable. When picking a color for a new agent, prefer one with semantic relevance even if it overlaps an existing assignment.

## Validation Checklist

After creating or modifying an agent, skill, or command, verify:

- [ ] **Filename matches identifier**: Agent filename = `@mention` name = `name:` frontmatter. Skill directory matches references in prose and equals the `/command` name for workflow skills.
- [ ] **No bundled-skill shadowing**: New workflow skill names do not collide with Claude Code's bundled skills.
- [ ] **Cross-references are correct**: Workflow skills reference valid agent identifiers via `agent:` frontmatter or prose. Agents reference valid skill names. `CLAUDE.md` lists the new artifact.
- [ ] **Color is a valid word**: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, or `cyan` — not a hex code.
- [ ] **Tool scope is appropriate**: Read-only agents allowlist only `Read, Glob, Grep, Bash` (Bash only if needed for git/lint/etc.) and add `disallowedTools: Write, Edit, NotebookEdit`. Implementation agents typically omit `tools:` to inherit everything. Tool names must exist in the current tools reference (no stale names like `MultiEdit`).
- [ ] **Skills are preloaded, not stranded**: Every skill an agent's body depends on appears in its `skills:` frontmatter. An agent with a `tools:` allowlist that omits `Skill` must never be told to "use the Skill tool." Preloaded skills must not set `disable-model-invocation: true`.
- [ ] **Frontmatter is complete**: All required keys are present with valid values.
- [ ] **Body follows conventions**: Opening persona line (agents), `# H1 Title` + intro (skills), `$ARGUMENTS` at end when accepting user args (commands).
- [ ] **Cross-cutting guidance is wired in**: Implementation-oriented agents reference `coding-guardrails` (or clearly include equivalent guardrails) alongside any domain skill.
- [ ] **`CLAUDE.md` is updated**: New agents appear in the subagent table, new skills in the skills table, new commands in the commands table.
- [ ] **User-facing docs are updated if present**: README or other suite docs are kept in sync when this repo actually includes them.

## Updating Suite Documentation

When adding a new artifact, update these docs as applicable:

### `CLAUDE.md` under the current Claude Code config root

- Add agents to the "Specialist Subagents" table.
- Add skills to the "Available Skills" table with description and primary agent users.
- Add commands to the "Slash Commands" table with description and agent.

### `README.md` or other user-facing docs (if present)

- Update any public-facing summary tables so they match the suite on disk.
- If the repo has no README or equivalent docs file, do not invent one just to satisfy a checklist item.
