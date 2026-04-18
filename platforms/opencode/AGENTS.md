# OpenCode

A custom suite of software engineering agents, skills, and commands designed for building software across any tech stack.

## Agent Suite

### Primary Agent: Tech Lead (default)

The **tech-lead** is the default primary agent and acts as the executing orchestrator. It:

- Analyzes requests and breaks complex work into structured plans
- Delegates specialist work to subagents via the Task tool
- Delegates to `@architect` when work needs a design spec before implementation
- Integrates results from subagents into cohesive solutions
- Handles straightforward tasks directly, including basic shell work and routine git/GitHub operations

Switch to the built-in **plan** agent (Tab key) for read-only analysis and planning.

### Specialist Subagents

These are invoked automatically by the tech-lead or manually via `@mention`:

| Agent | Purpose | Permissions |
|---|---|---|
| `@architect` | Collaborative spec writing: clarify scope, explore approaches, produce a design and task checklist | Read-only. Cannot modify files. |
| `@code-reviewer` | Code quality and best practices review | Read-only. Cannot modify files. |
| `@security-analyst` | Security vulnerability assessment, dependency audits, threat modeling | Read-only. Cannot modify files. |
| `@tester` | Test generation, coverage analysis, test strategy | Write access. Bash allowlisted for test/build toolchains. |
| `@debugger` | Root cause analysis and systematic debugging | Write access. Bash allowlisted for repro, diagnostics, and runtime toolchains. |
| `@documenter` | Technical documentation and API docs | Write access. Bash limited to read-only commands. |
| `@devops-engineer` | Docker, CI/CD, infrastructure configuration | Write access. Bash allowlisted for infrastructure and delivery toolchains. |
| `@backend-engineer` | Backend application work: API handlers, services, auth/authz, validation, integrations, app-layer refactors | Write access. Bash allowlisted for app/runtime toolchains. |
| `@database-specialist` | Schema design, migrations, indexes, query tuning, constraints, transactions, ORM/query-builder work where database behavior matters | Write access. Bash allowlisted for database and migration toolchains. |
| `@git-manager` | Release preparation, changelog generation, and versioning-heavy git workflow | Write access. Bash limited to git, `gh`, and read commands. |
| `@frontend-engineer` | UI components, styling, accessibility, responsive design | Write access. Bash allowlisted for frontend build/test toolchains. |
| `@frontend-auditor` | Read-only frontend audit and critique for UI quality, accessibility, responsiveness, and product-specific design fit | Read-only. Cannot modify files. |
| `@agent-builder` | Creates, modifies, and reviews agents, skills, and slash commands | Write access. Bash limited to read-only commands. |
| `@agent-reviewer` | Read-only review of agents, skills, and commands for correctness, permissions, and consistency | Read-only. Cannot modify files. |

Plus the built-in subagents:

| Agent | Purpose |
|---|---|
| `@explore` | Fast read-only codebase search and file discovery |
| `@general` | General-purpose multi-step research and tasks |

### Available Skills

Skills are loaded on-demand by agents via the `skill` tool. They provide detailed procedural knowledge without consuming context until needed.

| Skill | Description | Primary users |
|---|---|---|
| `coding-guardrails` | Cross-cutting execution guardrails for implementation work: assumptions, simplicity, surgical diffs, and verification | tech-lead, code-reviewer, tester, debugger, devops-engineer, frontend-engineer, backend-engineer, database-specialist |
| `spec-writing` | Scope decomposition, clarifying dialogue, approach exploration, staged design presentation, and spec self-review | architect |
| `git-conventions` | Conventional Commits format, branching model, commit hygiene | git-manager, tech-lead |
| `test-strategy` | Test type selection, coverage targets, mocking guidelines | tester, tech-lead |
| `code-review-checklist` | Structured review rubric across core review categories with severity levels | code-reviewer |
| `security-analysis` | Vulnerability taxonomy, data flow analysis, dependency auditing, remediation patterns | security-analyst |
| `debugging-methodology` | 5-phase debugging workflow: reproduce, gather, hypothesize, test, fix | debugger |
| `doc-templates` | Templates for READMEs, API docs, ADRs, changelogs, code comments | documenter |
| `docker-best-practices` | Multi-stage builds, security hardening, layer caching, Compose patterns | devops-engineer |
| `ci-pipeline` | CI/CD patterns for GitHub Actions and GitLab CI with caching strategies | devops-engineer |
| `backend-patterns` | Backend application patterns for handlers, services, validation, auth/authz, integrations, and app-layer refactors | backend-engineer, tech-lead |
| `database-patterns` | Database design and performance patterns for schemas, migrations, indexes, constraints, transactions, and query behavior | database-specialist, tech-lead |
| `frontend-patterns` | Frontend router for product context gathering, work-mode selection, escalation, and targeted reference selection | frontend-engineer, frontend-auditor |
| `agent-authoring` | Schemas, templates, and conventions for creating agents, skills, and commands | agent-builder, agent-reviewer |

### Slash Commands

Quick-access commands for common workflows:

| Command | Action | Agent |
|---|---|---|
| `/review` | Review staged or unstaged changes for quality issues | code-reviewer |
| `/security` | Run a security assessment on code and dependencies | security-analyst |
| `/test` | Run tests and analyze results | tester |
| `/debug <description>` | Start a systematic debugging session | debugger |
| `/docs` | Generate or update documentation | documenter |
| `/commit` | Stage logical changes when needed and create Conventional Commits | tech-lead |
| `/release` | Prepare release notes, changelog, and version bump | git-manager |
| `/backend-engineer` | Implement or modify backend application code | backend-engineer |
| `/database-specialist` | Design or modify database schemas, migrations, queries, and indexes | database-specialist |
| `/frontend` | Build, update, or fix frontend UI components and pages | frontend-engineer |
| `/frontend-audit` | Audit frontend quality, states, responsiveness, and anti-patterns without editing files | frontend-auditor |
| `/frontend-critique` | Critique frontend UX and visual direction, then suggest targeted improvements | frontend-auditor |
| `/frontend-polish` | Apply focused frontend polish before handoff with verification and restraint | frontend-engineer |
| `/agent-builder` | Create or modify an agent, skill, or command | agent-builder |
| `/agent-review` | Review agents, skills, and commands for correctness and consistency | agent-reviewer |
| `/spec` | Research a goal and produce a design spec with task checklist | architect |

### Suggested Workflows

These are common starting points, not rigid rules. Pick the smallest workflow that fits the request.

| Goal | Suggested flow |
|---|---|
| Ambiguous feature or cross-cutting change | `/spec` → specialist implementation command or `tech-lead` → `/review` or `/security` as needed → `/test` → `/commit` |
| Straightforward backend work | `/backend-engineer` → `/test` → `/review` → `/commit` |
| Database-heavy change | `/database-specialist` → `/test` if applicable → `/review` → `/commit` |
| Frontend implementation | `/frontend` → `/frontend-polish` if needed → `/test` → `/review` → `/commit` |
| Frontend critique before coding | `/frontend-audit` or `/frontend-critique` → `/frontend` or `/frontend-polish` → `/test` → `/review` |
| Bug investigation | `/debug <issue>` → specialist follow-up if needed → `/test` → `/review` → `/commit` |
| Security-sensitive change | `/spec` or implementation command → `/security` → `/test` → `/review` → `/commit` |
| Documentation update | `/docs` → `/review` if the doc change affects technical accuracy significantly → `/commit` |
| Agent/skill/command changes | `/agent-review` → `/agent-builder` → `/agent-review` → `/commit` |
| Release preparation | `/review` or `/test` as needed → `/release` |

## General Guidelines

- Read project config and nearby code before changing anything.
- For ambiguous or cross-cutting work, use `/spec` or `@architect` first.
- Skills are the canonical long-form guidance. Keep agent bodies and commands short; load only what you need. For implementation work, start with `coding-guardrails` plus the domain skill.
- Prefer deny-by-default shell permissions with role-scoped allowlists; reserve unrestricted shell access for cases that truly require it.
- Route backend application work to `@backend-engineer`; when schema, SQL, migrations, indexes, transaction behavior, or database-heavy ORM/query-builder behavior are the real concern, involve `@database-specialist`.
- For implementation work, surface assumptions, keep changes simple and scoped, and verify with explicit checks.
- Match existing conventions and prefer the smallest change that satisfies the request.
- Use the GitHub CLI (`gh`) for GitHub-hosted tasks when shell access is appropriate.
- Use `/review`, `/security`, `/test`, `/docs`, and `/commit` as appropriate to keep quality, docs, and history clean.
- Never read `.env` files via any method.
