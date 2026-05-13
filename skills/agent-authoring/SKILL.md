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
| Skill | `skills/<name>/SKILL.md` | kebab-case directory name | Directory name (no `name:` in frontmatter) |
| Command | `commands/<name>.md` | kebab-case filename | Filename sans `.md` (becomes `/name`) |

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
disallowedTools: Write, Edit, MultiEdit, NotebookEdit
model: sonnet
color: red
---
```

| Key | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Unique identifier. Must match filename sans `.md`. Lowercase + hyphens. |
| `description` | string | Yes | When Claude should delegate to this subagent. Appears in the agent listing and informs auto-routing. |
| `tools` | comma-separated string | No | Allowlist of tools the agent can use. Omit to inherit the full tool set. Use the allowlist to scope read-only agents. |
| `disallowedTools` | comma-separated string | No | Denylist applied on top of the inherited or allowlisted tool set. Useful for blocking write tools while keeping Bash. |
| `model` | string | No | `sonnet`, `opus`, `haiku`, or full model ID. Defaults to inherit from parent. |
| `color` | string | No | Word: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`. **Not** a hex code. |
| `permissionMode` | string | No | `default`, `acceptEdits`, `auto`, `dontAsk`, or `bypassPermissions`. |
| `maxTurns` | integer | No | Maximum agentic turns before stopping. |

### Permission Patterns

Claude Code's `tools:` key is an **unrestricted allowlist** — there is no granular per-command Bash scoping like OpenCode supports. Listing `Bash` grants arbitrary shell. Use one of these patterns:

#### Full access (implementation agents)

Omit `tools:` and `disallowedTools:`. The agent inherits the full tool set.

```yaml
---
name: backend-engineer
description: Implements backend application code ...
model: sonnet
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
disallowedTools: Write, Edit, MultiEdit, NotebookEdit
model: opus
color: red
---
```

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
2. **Step two** - Load relevant skills: "Use the Skill tool to load `skill-name` for [what it provides]."
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
| `description` | string | Yes | One-sentence summary. Displayed in the Skill tool's available-skills listing and used for auto-routing. |
| `disable-model-invocation` | boolean | No | Set `true` to prevent auto-loading. Skill becomes user-invocable only. |
| `allowed-tools` | comma-separated string | No | Tools pre-approved while this skill is active. |

Claude Code skills do **not** use a `name:` field. The directory name (`skills/<name>/`) is the canonical identifier.

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
- Skills typically range from 90-250 lines. For larger reference material, split into `SKILL.md` (router) plus `reference/*.md` files loaded on demand.

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

## Command Definition Schema

### Frontmatter

```yaml
---
description: Short description of what the command does.
agent: agent-identifier
context: fork
disable-model-invocation: true
---
```

| Key | Type | Required | Description |
|---|---|---|---|
| `description` | string | Yes | Short description displayed in `/help` and the command palette. |
| `agent` | string | No | Agent identifier (filename without `.md`) to route the command to. When paired with `context: fork`, the command runs in that agent's isolated subagent context. |
| `context` | string | No | Set to `fork` to run the command in an isolated subagent context with no access to the conversation history. Pair with `agent:`. |
| `disable-model-invocation` | boolean | No | Set `true` to prevent the command from being auto-invoked by Claude — it becomes user-triggered only. |
| `allowed-tools` | comma-separated string | No | Tools pre-approved while this command is running. |

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
- **Dynamic content**: Use `` !`command` `` syntax to inject shell command output into the prompt at invocation time. The `!` backtick block evaluates the command and replaces itself with the output.
- **`$ARGUMENTS`**: When the command accepts free-form user input, place `$ARGUMENTS` at the end. The user's text after the slash command (e.g., `/debug the login page crashes`) replaces it.
- **Keep it short**. Commands are prompts, not documentation. 5-15 lines total.
- **Multiple commands can route to the same agent** (e.g., `/frontend`, `/frontend-polish`, and `/frontend-audit` route within the frontend workflow family).
- **Prefer frontmatter routing over prose-only routing**. `agent:` + `context: fork` is the canonical way to delegate; the prose body should still name the agent for clarity, but the frontmatter is what wires the routing.

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

- [ ] **Filename matches identifier**: Agent filename = `@mention` name = `name:` frontmatter. Skill directory matches references in prose. Command filename = `/command` name.
- [ ] **Cross-references are correct**: Commands reference valid agent identifiers via `agent:` frontmatter or prose. Agents reference valid skill names. `CLAUDE.md` lists the new artifact.
- [ ] **Color is a valid word**: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, or `cyan` — not a hex code.
- [ ] **Tool scope is appropriate**: Read-only agents allowlist only `Read, Glob, Grep, Bash` (Bash only if needed for git/lint/etc.) and add `disallowedTools: Write, Edit, MultiEdit, NotebookEdit`. Implementation agents typically omit `tools:` to inherit everything.
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
