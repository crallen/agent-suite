# Agent Suite (Codex)

A custom suite of software engineering skills for building software across any tech stack.
The same skills back Claude Code and OpenCode; this document is Codex's view of them.

## How the suite works here

Codex has no roster of named specialist agents to hand work to — there is no
`@code-reviewer` to delegate a review to. You do the work yourself, and the suite
shows up as **skills**: packaged procedural knowledge you load when a task calls
for it.

- A skill loads **automatically** when its description matches the work at hand.
- Invoke one **explicitly** with `$skill-name` — `$why`, `$unslop`, `$blast-radius`.
- Read the whole `SKILL.md` before acting on it, and follow its routing into
  `reference/` files rather than reading them all.

Load the smallest useful set. For implementation work that is `coding-guardrails`
plus the one domain skill that fits; adding more crowds out the actual task.

## Available Skills

| Skill | Description | Reach for it when |
|---|---|---|
| `architecture-review` | Architecture deepening workflow: find shallow modules, propose depth-increasing refactors, present markdown report of candidates, then grill on the chosen one with CONTEXT.md / ADR integration | A module feels shallow or hard to test |
| `backend-patterns` | Backend application patterns for handlers, services, validation, auth/authz, integrations, and app-layer refactors | Writing handlers, services, auth, or integrations |
| `blast-radius` | Find what a change breaks beyond its obvious callers, then prove the safety-critical fact by running code, ranking each claim on a verification ladder | About to ship a change that could break distant callers |
| `ci-pipeline` | CI/CD stage order, architecture and coverage enforcement gates, auditing an inherited pipeline, per-stack reference workflows, and a discovery procedure for unfamiliar stacks | Building, auditing, or adding gates to a pipeline |
| `code-review-checklist` | Structured review rubric across core review categories, spec fidelity, and a Fowler design-smell baseline, with severity levels | Reviewing a diff and wanting a rubric |
| `coding-guardrails` | Cross-cutting execution guardrails for implementation work: assumptions, simplicity, surgical diffs, verification, structure/error/safety defaults, and naming over comments, plus on-demand principle references (type-system discipline, idempotency, build-the-lever, encode-lessons-in-structure) | Any implementation work — the default companion skill |
| `database-patterns` | Database design and performance patterns for schemas, migrations, indexes, constraints, transactions, and query behavior | Schema, migrations, indexes, or query behaviour |
| `debugging-methodology` | Phased debugging workflow — Phase 0 builds a feedback loop (10 strategies), phases 1–5 reproduce/gather/hypothesize/test/fix, Phase 6 is cleanup and post-mortem | Chasing a bug, test failure, or unexplained behaviour |
| `doc-templates` | Templates for READMEs, API docs, changelogs, code comments, plus Diátaxis document-type selection and global-audience prose rules, and register/naming rules — ADRs defer to `domain-modeling` | Writing a README, API doc, or changelog |
| `docker-best-practices` | The static-binary vs runtime base-image decision, multi-stage builds, layer caching, hardening, and per-stack reference Dockerfiles | Writing or shrinking a Dockerfile or Compose file |
| `domain-modeling` | Active domain-model maintenance: terminology sharpening, CONTEXT.md glossary upkeep, which terms earn a type, and minimal ADRs — both gated by a three-part test | Pinning down terminology, or recording a hard-to-reverse decision |
| `frontend-patterns` | Frontend router for product context gathering, work-mode selection, escalation, and targeted reference selection | Building or reshaping UI |
| `git-conventions` | Conventional Commits format, branching model, commit hygiene, short-summary commit and PR style | Writing commits, branches, or a PR description |
| `grill-methodology` | One-question-at-a-time Socratic interrogation of a plan: frontier questioning, recommendation-first questions, codebase cross-referencing, and a shared-understanding gate — pairs with `domain-modeling` | Stress-testing a plan before committing to it |
| `prototype-methodology` | Throwaway prototype workflow — routes between a terminal app for logic/state questions and multiple UI variants for visual questions | Answering a design question with throwaway code |
| `security-analysis` | Vulnerability taxonomy, data flow analysis, dependency auditing, remediation patterns | Auditing code, config, or dependencies for vulnerabilities |
| `spec-writing` | Scope decomposition, clarifying dialogue, approach exploration, staged design presentation, and spec self-review | Turning an ambiguous goal into a design spec |
| `test-strategy` | Test type selection, coverage targets, mocking guidelines, fixture-data hygiene | Choosing test types, coverage targets, or mocking approach |
| `ticket-writing` | Spec-to-ticket splitting, story/task and bug templates, testable acceptance-criteria rules, and JIRA/Linear platform notes | Splitting a spec into tracker tickets |
| `unslop` | Cut AI tells from any writing (puffery, AI vocabulary, punctuation/list overuse, hedging, voiceless prose), then restore a human voice | Finalising prose a human will read |
| `wayfinder-methodology` | Multi-session effort mapping: chart a destination plus decision tickets in-repo, work the frontier one decision per session, hold unsharpened work as fog of war | Planning an effort too big for one session |
| `why` | Reconstruct why code is shaped as it is — recover rationale from git history, PRs, issues, comments, and ADRs, each claim cited with stated confidence and gaps named | The intent behind existing code is unclear |

## Suggested Workflows

| Goal | Skills, in order |
|---|---|
| Ambiguous or cross-cutting change | `spec-writing` → `coding-guardrails` + the domain skill → `test-strategy` → `code-review-checklist` |
| Effort spanning many sessions | `wayfinder-methodology` → `spec-writing` → implementation |
| Stress-testing a plan | `grill-methodology` → `domain-modeling` for the terms it sharpens |
| Exploring a design first | `prototype-methodology` → `spec-writing` if it survives |
| Straightforward backend work | `backend-patterns` + `coding-guardrails` → `test-strategy` |
| Database-heavy change | `database-patterns` + `coding-guardrails` |
| Frontend work | `frontend-patterns` + `coding-guardrails` |
| Bug investigation | `debugging-methodology` → `why` when the intent is murky |
| Before shipping something risky | `blast-radius` |
| Security-sensitive change | `security-analysis` alongside the domain skill |
| Documentation | `doc-templates` → `unslop` |
| Committing | `git-conventions` |

## General Guidelines

- Read the project's config and nearby code before changing anything. If `CONTEXT.md`
  exists at the repo root (or `CONTEXT-MAP.md` for multi-context repos), read it — it
  defines that project's canonical domain language and outranks general terminology.
- Skills are the canonical long-form guidance. Load only what the task needs.
- Surface assumptions and alternative readings instead of silently picking one.
- Push back when a simpler approach satisfies the goal. When the goal is ambitious,
  scope down the mechanism, not the goal.
- Prefer the smallest change that satisfies the request over opportunistic cleanup,
  and match the conventions already in the file.
- Verify with concrete checks — run the tests, run the code — rather than asserting
  that a change works.
- Keep commit messages and PR descriptions short: a subject line and a few lines of
  why. The diff carries the detail. Never attach a TODO list or suggested follow-up
  work to either.
- Never append attribution footers to commits or PR descriptions.
- Never read `.env` files or other secret-bearing files. `.env.example` is the
  exception — it holds placeholders and may be read and edited.
