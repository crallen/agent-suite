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
| `@backend-engineer` | Backend application work: API handlers, services, auth/authz, validation, integrations, app-layer refactors | Full access. Writes code, runs app and test commands. |
| `@database-specialist` | Schema design, migrations, indexes, query tuning, constraints, transactions, ORM/query-builder work where database behavior matters | Full access. Writes migrations and query code, runs database verification commands. |
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
| `coding-guardrails` | Cross-cutting execution guardrails for implementation work: assumptions, simplicity, surgical diffs, and verification | tech-lead, code-reviewer, tester, debugger, devops, frontend, backend-engineer, database-specialist |
| `spec-writing` | Scope decomposition, clarifying dialogue, approach exploration, staged design presentation, and spec self-review | architect |
| `git-conventions` | Conventional Commits format, branching model, commit hygiene | git-manager, tech-lead |
| `test-strategy` | Test type selection, coverage targets, mocking guidelines | tester, tech-lead |
| `code-review-checklist` | Structured review rubric across core review categories with severity levels | code-reviewer |
| `security-analysis` | Vulnerability taxonomy, data flow analysis, dependency auditing, remediation patterns | security-analyst |
| `debugging-methodology` | 5-phase debugging workflow: reproduce, gather, hypothesize, test, fix | debugger |
| `doc-templates` | Templates for READMEs, API docs, ADRs, changelogs, code comments | documenter |
| `docker-best-practices` | Multi-stage builds, security hardening, layer caching, Compose patterns | devops |
| `ci-pipeline` | CI/CD patterns for GitHub Actions and GitLab CI with caching strategies | devops |
| `backend-patterns` | Backend application patterns for handlers, services, validation, auth/authz, integrations, and app-layer refactors | backend-engineer, tech-lead |
| `database-patterns` | Database design and performance patterns for schemas, migrations, indexes, constraints, transactions, and query behavior | database-specialist, tech-lead |
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
| `/backend-engineer` | Implement or modify backend application code | backend-engineer |
| `/database-specialist` | Design or modify database schemas, migrations, queries, and indexes | database-specialist |
| `/frontend` | Build, update, or fix frontend UI components and pages | frontend |
| `/agent-builder` | Create or modify an agent, skill, or command | agent-builder |
| `/agent-review` | Review agents, skills, and commands for correctness and consistency | agent-builder |
| `/spec` | Research a goal and produce a design spec with task checklist | architect |

## General Guidelines

- Read project config and nearby code before changing anything.
- For ambiguous or cross-cutting work, use `/spec` or `@architect` first.
- Skills are the canonical long-form guidance. Keep agent bodies and commands short; load only what you need. For implementation work, start with `coding-guardrails` plus the domain skill.
- Route backend application work to `@backend-engineer`; when schema, SQL, migrations, indexes, transaction behavior, or database-heavy ORM/query-builder behavior are the real concern, involve `@database-specialist`.
- For implementation work, surface assumptions, keep changes simple and scoped, and verify with explicit checks.
- Match existing conventions and prefer the smallest change that satisfies the request.
- Use `/review`, `/security`, `/test`, `/docs`, and `/commit` as appropriate to keep quality, docs, and history clean.
- Never read `.env` files via any method.
