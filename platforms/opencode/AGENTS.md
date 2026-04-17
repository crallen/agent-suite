# OpenCode

A custom suite of software engineering agents, skills, and commands designed for building software across any tech stack.

## Agent Suite

### Primary Agent: Tech Lead (default)

The **tech-lead** is the default primary agent and acts as the executing orchestrator. It:

- Analyzes requests and breaks complex work into structured plans
- Delegates specialist work to subagents via the Task tool
- Delegates to `@architect` when work needs a design spec before implementation
- Integrates results from subagents into cohesive solutions
- Handles straightforward tasks directly without delegation

Switch to the built-in **plan** agent (Tab key) for read-only analysis and planning.

### Specialist Subagents

These are invoked automatically by the tech-lead or manually via `@mention`:

| Agent | Purpose | Permissions |
|---|---|---|
| `@architect` | Collaborative spec writing: clarify scope, explore approaches, produce a design and task checklist | Read-only. Cannot modify files. |
| `@code-reviewer` | Code quality and best practices review | Read-only. Cannot modify files. |
| `@security-analyst` | Security vulnerability assessment, dependency audits, threat modeling | Read-only. Cannot modify files. |
| `@tester` | Test generation, coverage analysis, test strategy | Full access. Writes test files, runs test suites. |
| `@debugger` | Root cause analysis and systematic debugging | Full access. Reads logs, traces code, applies fixes. |
| `@documenter` | Technical documentation and API docs | Write access. Bash limited to read-only commands. |
| `@devops` | Docker, CI/CD, infrastructure configuration | Full access. Writes configs, runs build commands. |
| `@git-manager` | Commits, branches, releases, changelogs | Write access. Bash limited to git and read commands. |
| `@frontend` | UI components, styling, accessibility, responsive design | Full access. Builds and tests frontend code. |
| `@agent-builder` | Creates, modifies, and reviews agents, skills, and slash commands | Write access. Bash limited to read-only commands. |

Plus the built-in subagents:

| Agent | Purpose |
|---|---|
| `@explore` | Fast read-only codebase search and file discovery |
| `@general` | General-purpose multi-step research and tasks |

### Available Skills

Skills are loaded on-demand by agents via the `skill` tool. They provide detailed procedural knowledge without consuming context until needed.

| Skill | Description | Primary users |
|---|---|---|
| `spec-writing` | Scope decomposition, clarifying dialogue, approach exploration, staged design presentation, and spec self-review | architect |
| `git-conventions` | Conventional Commits format, branching model, commit hygiene | git-manager, tech-lead |
| `test-strategy` | Test type selection, coverage targets, mocking guidelines | tester, tech-lead |
| `code-review-checklist` | Structured review rubric across 7 categories with severity levels | code-reviewer |
| `security-analysis` | Vulnerability taxonomy, data flow analysis, dependency auditing, remediation patterns | security-analyst |
| `debugging-methodology` | 5-phase debugging workflow: reproduce, gather, hypothesize, test, fix | debugger |
| `doc-templates` | Templates for READMEs, API docs, ADRs, changelogs, code comments | documenter |
| `docker-best-practices` | Multi-stage builds, security hardening, layer caching, Compose patterns | devops |
| `ci-pipeline` | CI/CD patterns for GitHub Actions and GitLab CI with caching strategies | devops |
| `frontend-patterns` | Component architecture, state management, accessibility, responsive design | frontend |
| `agent-authoring` | Schemas, templates, and conventions for creating agents, skills, and commands | agent-builder |

### Slash Commands

Quick-access commands for common workflows:

| Command | Action | Agent |
|---|---|---|
| `/review` | Review staged or unstaged changes for quality issues | code-reviewer |
| `/security` | Run a security assessment on code and dependencies | security-analyst |
| `/test` | Run tests and analyze results | tester |
| `/debug <description>` | Start a systematic debugging session | debugger |
| `/docs` | Generate or update documentation | documenter |
| `/commit` | Stage logical changes when needed and create Conventional Commits | git-manager |
| `/release` | Prepare release notes, changelog, and version bump | git-manager |
| `/frontend` | Build, update, or fix frontend UI components and pages | frontend |
| `/agent-builder` | Create or modify an agent, skill, or command | agent-builder |
| `/agent-review` | Review agents, skills, and commands for correctness and consistency | agent-builder |
| `/spec` | Research a goal and produce a design spec with task checklist | architect |

## General Guidelines

- **Language-agnostic**: Agents detect and adapt to whatever tech stack is in the workspace. Read project config files (package.json, go.mod, Cargo.toml, etc.) to understand conventions before making changes.
- **Conventional Commits**: All commits follow the Conventional Commits specification. Use `/commit` or `@git-manager` for well-formed commits.
- **Review before merge**: Use `/review` to check code quality and `/security` to assess security posture before committing significant changes.
- **Test with changes**: New functionality should include tests. Use `/test` to verify the test suite passes.
- **Keep docs current**: When making significant changes, update relevant documentation. Use `/docs` to assess and fill documentation gaps.
- **Use skills lazily**: Load skills via the `skill` tool only when you need the detailed procedural knowledge. Don't preload everything.
- **Existing conventions first**: Always read existing code before writing new code. Match the project's style, patterns, and file organization.
- **Never read `.env` files**: Agents must avoid reading `.env` files via any method (`cat`, `grep`, `source`, etc.). Treat `.env` files as off-limits regardless of access method.
