# Claude Code

Software engineering agents, skills, and commands, for any language or stack.

## Routing

An agent earns its slot by carrying a capability that instructions cannot: tool
restrictions the harness enforces, an MCP server, persistent memory, or a model
pin. Everything else is a skill you load and work you do yourself.

- **Route to an agent** when you want what it enforces. `@code-reviewer`,
  `@security-analyst`, `@agent-reviewer`, and `@frontend-auditor` cannot write
  files. `@frontend-engineer` carries Playwright. `@debugger` and `@code-reviewer`
  keep project-local memory across sessions. `@documenter` runs on a cheaper model.
- **Load a skill and do the work** for everything else, backend, database,
  testing, infrastructure, and agent-authoring included. These have no agent by
  design; the knowledge is the whole point and it lives in `skills/`.
- **Fork for isolation** when a task will read far more than the answer is worth
  keeping. The commands that need this already set `context: fork`.
- **Keep the work yourself** when it is simple enough to handle directly, spans
  several domains, or the user asked you to do it.

When the goal is ambitious, scope down the mechanism, not the goal: simplify how a
thing gets built, never quietly shrink what is being built.

## Commands

Quick-access commands for common workflows. Each is a file at `commands/<name>.md`, invoked as `/name`.

Every command sets `disable-model-invocation: true`, so I reach them and you do not. Recommend one by name in prose; never invoke it.

| Command | Action | Agent |
|---|---|---|
| `/code-review` | Review pending changes, changes since a base ref, or the full codebase when the working tree is clean | code-reviewer |
| `/security` | Run a security assessment on code and dependencies | security-analyst |
| `/full-review` | Run a code quality review and security audit in parallel | code-reviewer + security-analyst |
| `/test` | Run tests and analyze results | — (fork, `test-strategy`) |
| `/debugger` | Start a systematic debugging session | debugger |
| `/docs` | Generate or update documentation | documenter |
| `/commit` | Stage logical changes when needed and create Conventional Commits | — (inline, `git-conventions`) |
| `/ship` | Commit and push in one step — same logic as `/commit`, then pushes to the remote | — (inline, `git-conventions`) |
| `/release` | Prepare release notes, changelog, and version bump | — (inline, `git-conventions`) |
| `/backend-engineer` | Implement or modify backend application code | — (fork, `backend-patterns`) |
| `/database-specialist` | Design or modify database schemas, migrations, queries, and indexes | — (fork, `database-patterns`) |
| `/frontend` | Build, update, or fix frontend UI components and pages | frontend-engineer |
| `/frontend-audit` | Audit frontend quality, states, responsiveness, and anti-patterns without editing files | frontend-auditor |
| `/frontend-critique` | Critique frontend UX and visual direction, then suggest targeted improvements | frontend-auditor |
| `/frontend-polish` | Apply focused frontend polish before handoff with verification and restraint | frontend-engineer |
| `/agent-builder` | Create or modify an agent, skill, or command | — (fork, `agent-authoring`) |
| `/agent-review` | Review agents, skills, and commands for correctness and consistency | agent-reviewer |
| `/spec` | Research a goal and produce a design spec with task checklist | — (inline) |
| `/grill` | Stress-test a plan with relentless one-question-at-a-time interrogation, sharpening domain language and writing CONTEXT.md / ADRs as decisions crystallize | — (inline) |
| `/ticket` | Turn a spec, requirements, or the conversation into paste-ready JIRA/Linear tickets | — (inline) |
| `/prototype` | Build a throwaway prototype to explore a design question — logic branch for state/data-model questions, UI branch for visual layout questions | frontend-engineer, or inline |
| `/architecture` | Find deepening opportunities in the codebase, present a markdown report of candidates, then grill on the chosen one | — (inline) |
| `/wayfinder` | Chart a large effort as a map of decision tickets, then resolve one decision per session until the way is clear | — (inline) |
| `/zoom-out` | Get a map of relevant modules and callers when unfamiliar with an area, using the project's domain vocabulary | — |

## Workflows

| Goal | Suggested flow |
|---|---|
| Ambiguous feature or cross-cutting change | `/spec` → the implementation command for the domain → `/code-review` or `/security` as needed → `/test` → `/commit` |
| Effort too big to hold in one session | `/wayfinder` to chart the map → `/wayfinder` once per session to work the frontier → `/spec` → the implementation command for the domain → `/commit` |
| Stress-testing a plan or sharpening domain language | `/grill` → the implementation command for the domain → `/commit` |
| Turning a spec into tracker tickets | `/spec` → `/ticket` |
| Exploring a design before committing to it | `/prototype` → `/spec` if needed → the implementation command for the domain → `/commit` |
| Improving codebase architecture or testability | `/zoom-out` (orient first) → `/architecture` → the implementation command for the domain → `/test` → `/commit` |
| Straightforward backend work | `/backend-engineer` → `/test` → `/code-review` → `/commit` |
| Database-heavy change | `/database-specialist` → `/test` if applicable → `/code-review` → `/commit` |
| Frontend implementation | `/frontend` → `/frontend-polish` if needed → `/test` → `/code-review` → `/commit` |
| Frontend critique before coding | `/frontend-audit` or `/frontend-critique` → `/frontend` or `/frontend-polish` → `/test` → `/code-review` |
| Bug investigation | `/debugger` → specialist follow-up if needed → `/test` → `/code-review` → `/commit` |
| Security-sensitive change | `/spec` or implementation command → `/full-review` → `/test` → `/commit` |
| Documentation update | `/docs` → `/code-review` if the doc change affects technical accuracy significantly → `/commit` |
| Agent/skill/command changes | `/agent-review` → `/agent-builder` → `/agent-review` → `/commit` |
| Release preparation | `/code-review` or `/test` as needed → `/release` |

## General Guidelines

- When reporting information to me, be extremely concise and sacrifice grammar for the sake of concision.
- T3 Code hides every assistant message of a turn except the last one behind a "Worked for …" row once the turn settles, so any text written before a tool call disappears when the turn ends. Do the work first, then answer: keep text before a tool call to a one-line heads-up, never end a turn with tool calls followed by a bare "Done", and make the final message of every turn the complete, self-contained answer — findings, decisions, and questions included, with no reference back to text written earlier in the turn. Concise still means complete. Ask questions only in the final message, then stop and wait for the reply.
- Read project config and nearby code before changing anything. If `CONTEXT.md` exists at the repo root (or `CONTEXT-MAP.md` for multi-context repos), read it too — it defines the canonical domain language for that project and takes precedence over general terminology.
- For ambiguous or cross-cutting work, recommend `/spec` first.
- For implementation work, load `coding-guardrails` plus the domain skill: `backend-patterns` for application code, `database-patterns` when schema, SQL, migrations, indexes, or transaction behavior are the real concern. Surface assumptions and alternative readings instead of silently choosing one, push back when a simpler approach satisfies the goal, and prefer the smallest change that matches existing conventions.
- Use the GitHub CLI (`gh`) for GitHub-hosted tasks.
- Keep commit messages and PR descriptions to short summaries: a subject line plus a few lines of why. Describe only what the change contains — no TODO lists, follow-up work, or attribution footers of any kind, including from subagents.
- Never read `.env` files or other secret-bearing files, by any method. `.env.example` is the exception — it holds placeholder values and may be read and edited (never put real secrets in it).
