# Codex

Software engineering skills, for any language or stack. Each skill packages the procedural
knowledge for a particular kind of task.

## How I Work

- A skill loads **automatically** when its description matches the work at hand.
- Invoke one **explicitly** with `$skill-name` — `$why`, `$unslop`, `$blast-radius`.
- Read the whole `SKILL.md` before acting on it, and follow its routing into
  `reference/` files rather than reading them all.

Load the smallest useful set. For implementation work that is `coding-guardrails`
plus the one domain skill that fits; adding more crowds out the actual task.

## Skills

| Skill | Description | Reach for it when |
|---|---|---|
| `architecture-review` | Architecture deepening workflow: find shallow modules, propose depth-increasing refactors, present markdown report of candidates, then grill on the chosen one with CONTEXT.md / ADR integration | A module feels shallow or hard to test |
| `backend-patterns` | House rules for application-layer code — the request path, inward dependency direction, where each kind of validation lives, constraints before app checks, and structured logs plus a metrics endpoint as defaults. Load for handlers, services, validation, auth, integrations, and app-layer refactors; pair with database-patterns when SQL behavior is the real concern. | Writing handlers, services, auth, or integrations |
| `blast-radius` | Find what a change breaks beyond its obvious callers, then prove the safety-critical fact by running code, ranking each claim on a verification ladder | About to ship a change that could break distant callers |
| `ci-pipeline` | CI/CD stage order, architecture and coverage enforcement gates, auditing an inherited pipeline, per-stack reference workflows, and a discovery procedure for unfamiliar stacks | Building, auditing, or adding gates to a pipeline |
| `code-review-checklist` | The review rubric and report format — spec fidelity as its own axis, the house rules for naming and error shape, the Fowler design-smell baseline, and severity calibration. Load when reviewing a diff, a pull request, or a file for quality. | Reviewing a diff and wanting a rubric |
| `coding-guardrails` | Execution guardrails for implementation work: when to ask before coding, the simplicity test, diff scope, verification targets, structure and error defaults, naming over comments. Load for any feature, fix, refactor, config change, or diff review; its references cover type design, idempotency, building reusable levers, and encoding lessons in structure. | Any implementation work — the default companion skill |
| `database-patterns` | House rules for database work — expand/migrate/contract migrations, the constraint-per-need table, transaction boundaries chosen by invariant, and evidence-based indexing. Load for schema design, migrations, indexes, query tuning, transaction boundaries, and ORM code where database behavior is the real concern. | Schema, migrations, indexes, or query behaviour |
| `debugging-methodology` | The debugging discipline — build a pass/fail feedback loop before anything else, rank falsifiable hypotheses and show them, tag instrumentation for removal, fix at a correct test seam or record that none exists. Load when investigating a bug, a failing test, or unexplained behavior. | Chasing a bug, test failure, or unexplained behaviour |
| `doc-templates` | Templates for READMEs, API docs, changelogs, code comments, plus Diátaxis document-type selection and global-audience prose rules, and register/naming rules — ADRs defer to `domain-modeling` | Writing a README, API doc, or changelog |
| `docker-best-practices` | The static-binary vs runtime base-image decision, multi-stage builds, layer caching, hardening, and per-stack reference Dockerfiles | Writing or shrinking a Dockerfile or Compose file |
| `domain-modeling` | Active domain-model maintenance: terminology sharpening, CONTEXT.md glossary upkeep, which terms earn a type, and minimal ADRs — both gated by a three-part test | Pinning down terminology, or recording a hard-to-reverse decision |
| `frontend-patterns` | Frontend router — the non-negotiables for UI work, when to infer from precedent versus ask versus escalate, and which reference to load for design direction, anti-patterns, component architecture, accessibility and responsiveness, or verification. Load first for any UI component, page, form, layout, styling, or state-management task. | Building or reshaping UI |
| `git-conventions` | Commit, branch, and pull-request rules — the project's own conventions first, then Conventional Commits with the type-to-bump mapping, short bodies, no attribution footers, and filesystem safety for git work. Load before committing, branching, opening a pull request, or preparing a release. | Writing commits, branches, or a PR description |
| `grill-methodology` | One-question-at-a-time Socratic interrogation of a plan: frontier questioning, recommendation-first questions, codebase cross-referencing, and a shared-understanding gate — pairs with `domain-modeling` | Stress-testing a plan before committing to it |
| `prototype-methodology` | Throwaway prototype workflow — routes between a terminal app for logic/state questions and multiple UI variants for visual questions | Answering a design question with throwaway code |
| `security-analysis` | The security report format and severity matrix, a source-to-sink method, and the vulnerability categories to cover with their CWE ids. Load when performing a security review, auditing dependencies, or investigating a suspected vulnerability. | Auditing code, config, or dependencies for vulnerabilities |
| `spec-writing` | Dialogue-to-spec workflow: scope gate, one-question-at-a-time clarification with lettered options, recommended approaches, staged design, self-review, and a dated spec file | Turning an ambiguous goal into a design spec |
| `test-strategy` | House rules for proving correctness — test-first vertical slices, the mock limit, coverage targets by category, test naming, and reserved fixture placeholders. Load when deciding how a change will be verified, writing or reviewing tests, or setting a coverage gate. | Choosing test types, coverage targets, or mocking approach |
| `ticket-writing` | Spec-to-ticket splitting, story/task and bug templates, testable acceptance-criteria rules, and JIRA/Linear platform notes | Splitting a spec into tracker tickets |
| `unslop` | Cut AI tells from any writing (puffery, AI vocabulary, punctuation/list overuse, hedging, voiceless prose), then restore a human voice | Finalising prose a human will read |
| `wayfinder-methodology` | Multi-session effort mapping: chart a destination plus decision tickets in-repo, work the frontier one decision per session, hold unsharpened work as fog of war | Planning an effort too big for one session |
| `why` | Reconstruct why code is shaped as it is — recover rationale from git history, PRs, issues, comments, and ADRs, each claim cited with stated confidence and gaps named | The intent behind existing code is unclear |

## Workflows

| Goal | Suggested flow |
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
- T3 Code hides every assistant message of a turn except the last one behind a
  "Worked for …" row once the turn settles, so any text written before a tool call
  disappears when the turn ends. Do the work first, then answer: keep text before a
  tool call to a one-line heads-up, never end a turn with tool calls followed by a
  bare "Done", and make the final message of every turn the complete, self-contained
  answer — findings, decisions, and questions included, with no reference back to
  text written earlier in the turn. Ask questions only in the final message, then
  stop and wait for the reply.
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
- Never read `.env` files or other secret-bearing files, by any method. `.env.example` is the exception — it holds placeholder values and may be read and edited (never put real secrets in it).
