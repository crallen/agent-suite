# Rule list: implementation balance, Branch 2

Classifies every rule in scope for tasks 14–19 of
[the implementation balance spec](2026-11-09-implementation-balance.md). Verdicts
measured on `claude-opus-5-5`. Nothing is edited until the owner approves this list.

Classes: **house** (house style), **counter** (counter-correction), **textbook**,
**restate** (restatement). Evidence names the guarding case and result, or says
"judgment" when no eval covers the rule. Decisions: **keep**, **cut**, **rewrite**,
**move**.

Evidence shorthand, from the spec's Testing table:

- *guarded*: ablation went red (0/5); the rule stays.
- *ablation 5/5*: followed with every copy removed; a candidate cut.
- *freedom*: a freedom case went red only when this kind of rule was added, or
  when its counterweight was removed.

## coding-guardrails

| # | Rule | Class | Evidence | Decision |
|---|---|---|---|---|
| 1 | Opener: "bias toward caution over speed" | counter | judgment; pushes toward the ceremony the freedom cases guard against | cut |
| 2 | Opener: "apply proportionally — a one-line typo fix does not need a ceremony-heavy process" | counter | freedom: `impl-trivial-no-ceremony` went red only once this line was removed | keep |
| 3 | The Guardrails table | restate | restates §1–4 headings | cut |
| 4 | §1: state assumptions; ask when scope, data shape, UX, security, performance, or policy is unclear | counter | `impl-ambiguous-asks` stays green with it deleted (no run loads the skill); judgment | rewrite: "Ask when readings lead to materially different code and the repo cannot settle it; otherwise state the assumption and proceed." |
| 5 | §1: "If a simpler path satisfies the goal, say so" | counter | judgment | keep |
| 6 | §2 intro: understand the real constraint, smallest model | house | judgment | keep |
| 7 | §2: build exactly what was asked; abstraction only where something varies; dependencies and flags only for a present caller; handle failures with evidence | counter | judgment | keep |
| 8 | §2: "If 200 lines could be 50, simplify" | restate | the Simplicity Test says it | cut |
| 9 | Ceremony versus architecture paragraph, with the `architecture-review` one-adapter test | house | judgment | keep |
| 10 | Simplicity Test | house | judgment | keep |
| 11 | §3 bullets: leave adjacent code, match style, clean up only what you orphaned, mention unrelated issues | counter | judgment | keep |
| 12 | §3: reach versus shape paragraph | house | judgment | keep |
| 13 | §4 intro and "define success criteria", "for new features decide checks before coding" | restate | two bullets saying one thing | rewrite: one bullet, "Decide what will prove the change before making it." |
| 14 | §4: failing test or reproduction before a bug fix | house | guarded: `impl-test-first` (copy of test-strategy's rule) | keep |
| 15 | §4: behavior baseline before a refactor; loop until verified | counter | judgment | keep |
| 16 | Plan Template | counter | freedom: plan-with-`verify:` ceremony is what `impl-trivial-no-ceremony` asserts against; nothing else points at it | cut |
| 17 | Operating Loops table | restate | restates §4 per work type | cut |
| 18 | Thin composition root; modules as facades; errors with context and cause; no panics on recoverable paths | house | judgment | keep |
| 19 | Guard clauses, early return | textbook | judgment | cut |
| 20 | Naming and Comments paragraph | restate | `doc-templates` owns it | rewrite to one pointer line |
| 21 | Principle Deep-Dives router | house | judgment | keep |

## test-strategy

| # | Rule | Class | Evidence | Decision |
|---|---|---|---|---|
| 1 | Intro: "`coding-guardrails` owns the verification loop per work type" | restate | inaccurate once Operating Loops is cut | cut |
| 2 | Clarify before encoding; no suites for hypothetical behavior | restate | coding-guardrails §1 and §2 | cut |
| 3 | Test-first vertical slices; all-tests-first produces imagined behavior | house | guarded: `impl-test-first` 0/5 | keep |
| 4 | "Before the first test, confirm the interface changes" | counter | judgment: reads as an instruction to stop and ask, the over-constraint `impl-clear-feature-finishes` guards | rewrite: drop "confirm the interface changes"; keep "list the behaviors in domain vocabulary, critical paths first" |
| 5 | Tracer bullet; one test per behavior; refactor only at green | house | guarded with #3 | keep |
| 6 | Pointer to `code-review-checklist`'s smell baseline | restate | cascade load into a review skill | cut |
| 7 | Test through the public interface; survive a refactor | counter | judgment | keep |
| 8 | Expected values from an independent source; tautological assertions | counter | judgment | keep |
| 9 | Mock at boundaries; prefer fakes; more than three mocks means refactor | house | judgment | keep |
| 10 | "Verify mock interactions sparingly" | textbook | judgment | cut |
| 11 | Coverage targets table | house | judgment: the per-category numbers are house targets the model would not pick unprompted; the description advertises them | keep |
| 12 | Branch coverage, not line | house | judgment | keep |
| 13 | Skip tests of framework behavior, generated code, private helpers | textbook | judgment | cut |
| 14 | Spec-style test names | house | judgment | keep |
| 15 | Helpers follow `doc-templates`; tests run in any order | restate, textbook | judgment | cut |
| 16 | Fixture Data: reserved placeholders table | house | guarded: `impl-fixture-placeholders` 0/5 | keep |
| 17 | Don't invent "obviously fake" values; one placeholder per repo | counter | guarded with #16 | keep |

## backend-patterns

| # | Rule | Class | Evidence | Decision |
|---|---|---|---|---|
| 1 | Load line and routing table | restate | the description says it | cut |
| 2 | Request Path steps 1–5 | textbook | judgment | cut |
| 3 | Authentication and authorization handled separately | counter | judgment | keep, one line |
| 4 | Normalize input once at the boundary | house | judgment | keep, one line |
| 5 | Handlers coordinate, no deep business logic | restate | Dependency Direction | cut |
| 6 | Dependency Direction core: inward, service never sees HTTP | textbook | ablation 5/5 (`impl-integration-timeout`) | cut |
| 7 | Acyclic import graph; extract the shared concept | counter | judgment | keep |
| 8 | Inject at new seams; match hidden globals rather than half-convert | counter | judgment | keep |
| 9 | Validation table | house | judgment | keep |
| 10 | "Do not rely on application checks alone" | restate | the table's third row, and `database-patterns` | cut |
| 11 | Integrations: explicit timeouts | textbook | ablation 5/5 | cut |
| 12 | Integrations: retry matches idempotency; validate responses; map errors locally; keep trace context; provider mapping at the edge | counter | judgment | keep |
| 13 | Structured logs plus a metrics endpoint as defaults; no secrets in logs | house | judgment | keep |
| 14 | Security-sensitive defaults fail closed | house | judgment | keep |
| 15 | Match existing error handling and wiring | restate | coding-guardrails §3 | cut |
| 16 | Surface ambiguous contracts before encoding | restate | coding-guardrails §1 | cut |
| 17 | Refactor the app layer only when it serves the change | restate | coding-guardrails §3 | cut |

## database-patterns

| # | Rule | Class | Evidence | Decision |
|---|---|---|---|---|
| 1 | Load line and routing table | restate | the description and the closing pairing paragraph | cut |
| 2 | Constraints are the last line of defense; ORM validations do not replace them | house | judgment | keep |
| 3 | Constraint table rows: primary key, unique constraint | textbook | judgment | cut |
| 4 | Constraint table rows: foreign key with chosen deletion behavior, check constraints, cross-table invariants | counter | judgment | keep |
| 5 | Nullability and defaults are decisions; every delete rule explicit | house | judgment | keep |
| 6 | Timestamps, soft deletes, tenant scoping follow the project | restate | coding-guardrails §3 | cut |
| 7 | Expand, migrate, contract | house | ablation 5/5 with a rolling deploy; without one, base 0/3 even with the rule | rewrite, scoped: "When old and new code run against one schema (several instances, rolling deploys), stage a breaking change as expand, migrate, contract." |
| 8 | Backfills restartable, batched outside hot-path transactions; schema and backfill separate when risky; irreversibility stated | counter | judgment | keep |
| 9 | Each migration small enough to roll forward; blocking operations out of peak windows | textbook | judgment | cut |
| 10 | Indexes from a query pattern, not intuition; measure the plan | house | judgment | keep |
| 11 | Transaction spans exactly the invariant | house | judgment | keep |
| 12 | Transaction table rows: single-row write, multi-statement invariant | textbook | judgment | cut |
| 13 | Never a network call inside a transaction; outbox | house | judgment | keep, as a line |
| 14 | Transaction table row: long backfill | restate | #8 | cut |
| 15 | Isolation explicit; locks understood; deadlock retry designed; read the ORM's SQL | counter | judgment | keep |
| 16 | Closing pairing paragraph | house | judgment | keep |

## frontend-patterns

| # | Rule | Class | Evidence | Decision |
|---|---|---|---|---|
| 1 | Reuse the existing visual system before inventing one | textbook | ablation 5/5 (`impl-frontend-tokens`) | cut |
| 2 | Generic polished UI that ignores workflow and tone is the failure | house | judgment | keep |
| 3 | Cover the states that matter | house | judgment | keep |
| 4 | Verify explicitly | restate | coding-guardrails §4 | keep: one line, it is what Playwright is for |
| 5 | Escalate to `spec-writing` for workflow or IA changes | house | judgment | keep |
| 6 | Context First paragraph and situation table | house | judgment | keep |
| 7 | Route table rows for `design-direction.md` and `verification.md` | — | files deleted per spec | cut |
| 8 | Promoted from `design-direction.md`: one dominant move per screen; typography before decoration; color is semantic, spacing does structure; tighten inside groups, loosen between; `gap` over margin hacks; motion explains state, reduced motion respected; feedback at the interaction point; buttons name the action | house | judgment | move into `SKILL.md`, one line each |
| 9 | Promoted from `anti-patterns.md`: one primary action per region; no reflex gradients, glows, or cards in cards; stable layout between loading and loaded | house | judgment | move into `SKILL.md`; the catalog stays in the reference |
| 10 | Promoted from `verification.md`: report names the states checked, the commands run, and the missing proof | house | judgment | move into Report |
| 11 | Rest of `design-direction.md` and `verification.md` | restate, textbook | judgment | cut with the files |
| 12 | Description: "which reference to load for design direction, … or verification" | — | advertises deleted references | rewrite, with the OpenCode and Codex rows; `frontend-patterns` routing cases must not regress |
| 13 | OpenCode `frontend-critique.md` and `frontend-audit.md` pointers to the deleted files | — | dangling | rewrite to `anti-patterns.md` and `SKILL.md` |

## Agent bodies

| # | Rule | Class | Evidence | Decision |
|---|---|---|---|---|
| 1 | `frontend-engineer` steps 1–4 | restate | `frontend-patterns` Context First, router, situation table, non-negotiables | cut |
| 2 | `frontend-engineer` step 5: Playwright, load the screen, exercise states, narrow and wide | house | the agent's capability | keep |
| 3 | `frontend-engineer` report-only line; output format | house | judgment | keep |
| 4 | `security-analyst` step 1, scope | house | judgment | keep |
| 5 | `security-analyst` steps 2–5 | restate | `security-analysis`, preloaded | cut |
| 6 | `security-analyst` theoretical versus practical exposure; clean is valid | counter | judgment | keep |
| 7 | `code-reviewer` steps 1, 3, 4 | restate, textbook | `code-review-checklist` and `coding-guardrails`, preloaded | cut, keeping "a clean review is a valid outcome" |
| 8 | `code-reviewer` step 2: task-handed skill governs; Read other skills from `~/.claude/skills/<name>/SKILL.md` | house | no Skill tool | keep |
| 9 | `code-reviewer` memory and `git fetch` lines | house | the agent's capability | keep |
| 10 | `agent-reviewer` steps 1 and 2 except reading `agent-authoring/reference/claude.md` | restate, textbook | preloaded | cut |
| 11 | `agent-reviewer` step 3: run the validator, report its failures first | house | judgment | keep |
| 12 | `agent-reviewer` step 3: least privilege, identifiers, stale references | restate | `agent-authoring` checklist | cut |
| 13 | `agent-reviewer` step 4: name the `skill-design` failure mode and its lever | counter | judgment | keep |

## Index documents

| # | Rule | Class | Evidence | Decision |
|---|---|---|---|---|
| 1 | `platforms/claude/CLAUDE.md` implementation bullet: surface assumptions, push back, smallest change | restate | coding-guardrails §1–3; `impl-ambiguous-asks` stayed green 3/3 with "surface assumptions" removed | cut to the load instruction |
| 2 | `platforms/opencode/AGENTS.md:149` same bullet | restate | as #1 | cut; line 146 already holds the load instruction |
| 3 | `platforms/codex/AGENTS.md:13` | — | already only a load instruction | no change |
