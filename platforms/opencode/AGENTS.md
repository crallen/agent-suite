# OpenCode

Software engineering agents, skills, and commands, for any language or stack.

## Agents

### Primary Agents

Primary agents appear in the Tab agent switcher for direct conversation.

| Agent | Purpose |
|---|---|
| **tech-lead** (default) | Executing orchestrator: analyzes requests, delegates to specialists, integrates results, handles routine work directly. |
| **architect** | Collaborative design: researches goals, asks clarifying questions, produces specs with task checklists. Switch to this agent (Tab) when work needs a design step before implementation. |

The built-in **plan** agent is also available via Tab for read-only analysis.

### Specialist Subagents

These are invoked by the tech-lead via Task tool, or manually via `@mention`.

| Agent | Purpose | Permissions |
|---|---|---|
| `@code-reviewer` | Code quality and best practices review | Read-only. Cannot modify files. |
| `@security-analyst` | Security vulnerability assessment, dependency audits, threat modeling | Read-only. Cannot modify files. |
| `@tester` | Test generation, coverage analysis, test strategy | Write access. |
| `@debugger` | Root cause analysis and systematic debugging | Write access. |
| `@documenter` | Technical documentation and API docs | Write access. |
| `@devops-engineer` | Docker, CI/CD, infrastructure configuration | Write access. |
| `@backend-engineer` | Backend application work: API handlers, services, auth/authz, validation, integrations, app-layer refactors | Write access. |
| `@database-specialist` | Schema design, migrations, indexes, query tuning, constraints, transactions, ORM/query-builder work where database behavior matters | Write access. |
| `@git-manager` | Release preparation, changelog generation, and versioning-heavy git workflow | Write access. |
| `@frontend-engineer` | UI components, styling, accessibility, responsive design | Write access. |
| `@frontend-auditor` | Read-only frontend audit and critique for UI quality, accessibility, responsiveness, and product-specific design fit | Read-only. Cannot modify files. |
| `@agent-builder` | Creates and modifies agents, skills, and slash commands | Write access. |
| `@agent-reviewer` | Read-only review of agents, skills, and commands for correctness, permissions, and consistency | Read-only. Cannot modify files. |

`@agent-reviewer` and `@frontend-auditor` are `hidden: true` — they stay out of `@` autocomplete and are reached through their commands (`/agent-review`, `/frontend-audit`, `/frontend-critique`).

Plus the built-in subagents:

| Agent | Purpose |
|---|---|
| `@explore` | Fast read-only codebase search and file discovery |
| `@general` | General-purpose multi-step research and tasks |

## Skills

Skills are loaded on-demand by agents via the `skill` tool. They provide detailed procedural knowledge without consuming context until needed.

| Skill | Description |
|---|---|
| `coding-guardrails` | Execution guardrails for implementation work: when to ask before coding, the simplicity test, diff scope, verification targets, structure and error defaults, naming over comments. Load for any feature, fix, refactor, config change, or diff review; its references cover type design, idempotency, building reusable levers, and encoding lessons in structure. |
| `spec-writing` | Dialogue-to-spec workflow: scope gate, one-question-at-a-time clarification with lettered options, recommended approaches, staged design, self-review, and a dated spec file |
| `ticket-writing` | Spec-to-ticket splitting, story/task and bug templates, testable acceptance-criteria rules, and JIRA/Linear platform notes |
| `git-conventions` | Commit, branch, and pull-request rules — the project's own conventions first, then Conventional Commits with the type-to-bump mapping, short bodies, no attribution footers, and filesystem safety for git work. Load before committing, branching, opening a pull request, or preparing a release. |
| `test-strategy` | House rules for proving correctness — test-first vertical slices, the mock limit, coverage targets by category, test naming, and reserved fixture placeholders. Load when deciding how a change will be verified, writing or reviewing tests, or setting a coverage gate. |
| `code-review-checklist` | The review rubric and report format — spec fidelity as its own axis, the house rules for naming and error shape, the Fowler design-smell baseline, and severity calibration. Load when reviewing a diff, a pull request, or a file for quality. |
| `security-analysis` | The security report format and severity matrix, a source-to-sink method, and the vulnerability categories to cover with their CWE ids. Load when performing a security review, auditing dependencies, or investigating a suspected vulnerability. |
| `debugging-methodology` | The debugging discipline — build a pass/fail feedback loop before anything else, rank falsifiable hypotheses and show them, tag instrumentation for removal, fix at a correct test seam or record that none exists. Load when investigating a bug, a failing test, or unexplained behavior. |
| `doc-templates` | Templates for READMEs, API docs, changelogs, code comments, plus Diátaxis document-type selection and global-audience prose rules, and register/naming rules — ADRs defer to `domain-modeling` |
| `unslop` | Cut AI tells from any writing (puffery, AI vocabulary, punctuation/list overuse, hedging, voiceless prose), then restore a human voice |
| `why` | Reconstruct why code is shaped as it is — recover rationale from git history, PRs, issues, comments, and ADRs, each claim cited with stated confidence and gaps named |
| `blast-radius` | Find what a change breaks beyond its obvious callers, then prove the safety-critical fact by running code, ranking each claim on a verification ladder |
| `docker-best-practices` | The static-binary vs runtime base-image decision, multi-stage builds, layer caching, hardening, and per-stack reference Dockerfiles |
| `ci-pipeline` | CI/CD stage order, architecture and coverage enforcement gates, auditing an inherited pipeline, per-stack reference workflows, and a discovery procedure for unfamiliar stacks |
| `backend-patterns` | House rules for application-layer code — the request path, inward dependency direction, where each kind of validation lives, constraints before app checks, and structured logs plus a metrics endpoint as defaults. Load for handlers, services, validation, auth, integrations, and app-layer refactors; pair with database-patterns when SQL behavior is the real concern. |
| `database-patterns` | House rules for database work — expand/migrate/contract migrations, the constraint-per-need table, transaction boundaries chosen by invariant, and evidence-based indexing. Load for schema design, migrations, indexes, query tuning, transaction boundaries, and ORM code where database behavior is the real concern. |
| `frontend-patterns` | Frontend router — the non-negotiables for UI work, when to infer from precedent versus ask versus escalate, and which reference to load for design direction, anti-patterns, component architecture, accessibility and responsiveness, or verification. Load first for any UI component, page, form, layout, styling, or state-management task. |
| `agent-authoring` | Conventions and validation checklist for agents, skills, and commands, with per-harness schema references |
| `domain-modeling` | Active domain-model maintenance: terminology sharpening, CONTEXT.md glossary upkeep, which terms earn a type, and minimal ADRs — both gated by a three-part test |
| `grill-methodology` | One-question-at-a-time Socratic interrogation of a plan: frontier questioning, recommendation-first questions, codebase cross-referencing, and a shared-understanding gate — pairs with `domain-modeling` |
| `architecture-review` | Architecture deepening workflow: find shallow modules, propose depth-increasing refactors, present markdown report of candidates, then grill on the chosen one with CONTEXT.md / ADR integration |
| `prototype-methodology` | Throwaway prototype workflow — routes between a terminal app for logic/state questions and multiple UI variants for visual questions |
| `wayfinder-methodology` | Multi-session effort mapping: chart a destination plus decision tickets in-repo, work the frontier one decision per session, hold unsharpened work as fog of war |

## Commands

Quick-access commands for common workflows:

| Command | Action | Agent |
|---|---|---|
| `/code-review` | Review pending changes, changes since a base ref, or the full codebase when the working tree is clean | code-reviewer |
| `/security` | Run a security assessment on code and dependencies | security-analyst |
| `/full-review` | Run a code quality review and security audit in parallel | tech-lead |
| `/test` | Run tests and analyze results | tester |
| `/debugger` | Start a systematic debugging session | debugger |
| `/docs` | Generate or update documentation | documenter |
| `/commit` | Stage logical changes when needed and create Conventional Commits | git-manager |
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
| `/grill <plan or topic>` | Stress-test a plan through relentless questioning, sharpen domain language, and write CONTEXT.md and ADRs inline | architect |
| `/wayfinder [idea or map path]` | Chart a large effort as a map of decision tickets, then resolve one decision per session until the way is clear | architect |
| `/ticket <spec or requirements>` | Turn a spec, requirements, or the conversation into paste-ready JIRA/Linear tickets | architect |
| `/ship` | Commit and push in one step — same logic as `/commit`, then pushes to the remote | git-manager |
| `/architecture` | Find deepening opportunities in the codebase, present a markdown report of candidates, then grill on the chosen one | architect |
| `/prototype` | Build a throwaway prototype to explore a design question — logic branch for state/data-model questions, UI branch for visual layout questions | tech-lead |
| `/zoom-out` | Get a map of relevant modules and callers when unfamiliar with an area, using the project's domain vocabulary | — |
| `/loop [interval] <prompt>` | Re-run a prompt or command on a fixed interval, or self-paced when no interval is given — requires the `opencode-loop-plugin` reference in `opencode.json`, whose `file:` path is machine-specific — update it per machine | — |

## Workflows

These are common starting points, not rigid rules. Pick the smallest workflow that fits the request.

| Goal | Suggested flow |
|---|---|
| Ambiguous feature or cross-cutting change | `/spec` → specialist implementation command or `tech-lead` → `/code-review` or `/security` as needed → `/test` → `/commit` |
| Straightforward backend work | `/backend-engineer` → `/test` → `/code-review` → `/commit` |
| Database-heavy change | `/database-specialist` → `/test` if applicable → `/code-review` → `/commit` |
| Frontend implementation | `/frontend` → `/frontend-polish` if needed → `/test` → `/code-review` → `/commit` |
| Frontend critique before coding | `/frontend-audit` or `/frontend-critique` → `/frontend` or `/frontend-polish` → `/test` → `/code-review` |
| Bug investigation | `/debugger` → specialist follow-up if needed → `/test` → `/code-review` → `/commit` |
| Security-sensitive change | `/spec` or implementation command → `/full-review` → `/test` → `/commit` |
| Documentation update | `/docs` → `/code-review` if the doc change affects technical accuracy significantly → `/commit` |
| Agent/skill/command changes | `/agent-review` → `/agent-builder` → `/agent-review` → `/commit` |
| Release preparation | `/code-review` or `/test` as needed → `/release` |
| Stress-testing a plan or sharpening domain language | `/grill <plan>` → specialist implementation command → `/commit` |
| Effort too big to hold in one session | `/wayfinder` to chart the map → `/wayfinder` once per session to work the frontier → `/spec` → specialist implementation command → `/commit` |
| Turning a spec into tracker tickets | `/spec` → `/ticket` |
| Exploring a design before committing to it | `/prototype` → `/spec` if needed → specialist implementation command → `/commit` |
| Improving codebase architecture or testability | `/zoom-out` (orient first) → `/architecture` → specialist implementation command → `/test` → `/commit` |

## General Guidelines

- Read project config and nearby code before changing anything. If `CONTEXT.md` exists at the repo root (or `CONTEXT-MAP.md` for multi-context repos), read it too — it defines the canonical domain language for that project and takes precedence over general terminology.
- T3 Code hides every assistant message of a turn except the last one behind a "Worked for …" row once the turn settles, so any text written before a tool call disappears when the turn ends. Do the work first, then answer: keep text before a tool call to a one-line heads-up, never end a turn with tool calls followed by a bare "Done", and make the final message of every turn the complete, self-contained answer — findings, decisions, and questions included, with no reference back to text written earlier in the turn. Concise still means complete. Ask questions only in the final message, then stop and wait for the reply.
- For ambiguous or cross-cutting work, use `/spec` or `@architect` first. The architect is a collaborative dialogue agent — always invoke it directly, never via Task delegation.
- Skills are the canonical long-form guidance. Keep agent bodies and commands short; load only what you need. For implementation work, start with `coding-guardrails` plus the domain skill.
- Agent permissions enforce two things: `edit` (denied on the read-only agents) and `task` (`"*": deny` on every subagent, so subagents cannot spawn subagents; the primaries keep delegation — tech-lead unrestricted, architect only to explore, code-reviewer, and security-analyst; `/full-review` routes tech-lead as a subtask, which works only because tech-lead carries no task deny). Bash is `allow` across the suite — a read-only agent's shell restraint is carried by its prose, so state it in the body. Role-scoped bash allowlists exist in the schema (`agent-authoring` documents the pattern) for an agent that genuinely needs a narrower shell.
- Route backend application work to `@backend-engineer`; when schema, SQL, migrations, indexes, transaction behavior, or database-heavy ORM/query-builder behavior are the real concern, involve `@database-specialist`.
- For implementation work, surface assumptions, keep changes simple and scoped, and verify with explicit checks.
- Match existing conventions and prefer the smallest change that satisfies the request.
- Use the GitHub CLI (`gh`) for GitHub-hosted tasks when shell access is appropriate.
- Keep commit messages and PR descriptions to short summaries: a subject line plus a few lines of why. The diff carries the detail.
- Describe only what the change contains. Never attach a TODO list, "additional things to verify", or suggested follow-up work to a commit message or PR description.
- Never append attribution footers to commits or PR descriptions — no "Generated with Claude Code", no `Co-Authored-By: Claude`, no session links. This applies to every commit and PR body, including those written by subagents.
- Never read `.env` files or other secret-bearing files, by any method. `.env.example` is the exception — it holds placeholder values and may be read and edited (never put real secrets in it).
