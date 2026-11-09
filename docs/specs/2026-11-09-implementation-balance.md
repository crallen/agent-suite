# Implementation balance: evals, roster, and skill cut

## Goal

Re-justify every rule in the implementation skills and every agent in the Claude
roster. An agent stays when it carries a harness-enforced capability that is
actually used. A rule stays when it is **house style** or a **counter-correction**;
**textbook** rules and **restatements** go, and so does anything that
over-constrains the model. Done means the roster is 4 agents under ADR 0002;
`coding-guardrails`, `test-strategy`, `backend-patterns`, `database-patterns`,
`frontend-patterns`, and the implementation lines of the index documents are each
cut against an approved **rule list**; and new implementation evals show no
regression against `main`. Terms in bold are defined in `CONTEXT.md`.

## Context

- **Prior cut.** The 2026-09-22 skills density spec removed about 1,300 lines,
  judged by line counts and smoke tests rather than behavior. Since then skills
  grew from 32.1k to 36.8k words, mostly from new skills; the implementation
  skills barely moved.
- **Usage across 118 local projects (session transcripts, 2026-11-09).**
  - Skill loads: `coding-guardrails` 400, `git-conventions` 357, `test-strategy`
    302, `backend-patterns` 171, `database-patterns` 66, `frontend-patterns` 1
    (it is a **preload** of `frontend-engineer` instead).
  - About 90 percent of implementation-skill loads happen inside subagents
    (`coding-guardrails` 355 of 400, `test-strategy` 273 of 302, `backend-patterns`
    151 of 171), mostly `/implement-spec` implementers, which load them because the
    **implementer brief** says to (`skills/spec-implementation/SKILL.md` line 33),
    not by routing.
  - Implementer traffic runs on `claude-opus-5-5` (16,760 events against 44 on
    `claude-sonnet-5-5`).
  - Reference reads: `coding-guardrails/reference/*` 0, `frontend-patterns/reference/*`
    0, across 48 `frontend-engineer` spawns.
  - Agent spawns: `code-reviewer` 106, `frontend-engineer` 48, `agent-reviewer` 38,
    `documenter` 7, `security-analyst` 4, `debugger` 0, `frontend-auditor` 0. No
    transcript shows `/frontend-audit` or `/frontend-critique` being run.
  - Agent memory: `code-reviewer` has written memory in 9 projects (29 files in
    one); `debugger` has written none anywhere.
- **Per-task load is modest.** An implementation task loads about 2.2k words
  (`coding-guardrails` 1,024, a domain skill about 500, `test-strategy` 637). The
  concern is signal, not size: textbook lines and restatements dilute house style,
  and some lines push toward caution and ceremony.
- **The forced-load line stays.** `CLAUDE.md`'s "a skill whose area the work
  touches still loads, even for a one-line question" came from eval triage
  (`ea00164`) and fixed real routing misses.
- **Descriptions stay.** Commit `7c49a3a` widened four skill triggers, including
  `frontend-patterns`, taking their known-gap cases from 0–1/10 to 10/10. Claude
  Code caps the skill listing at 1 percent of the context window and drops the
  least-invoked descriptions first, the five implementation descriptions total
  about 300 words, and most implementation loads arrive by implementer brief
  rather than description. Shortening them buys little and risks undoing that fix.
- **Claude Code facts this spec relies on** (code.claude.com docs, checked
  2026-11-09):
  - A `skills:` preload injects the full skill at subagent start. A skill with
    `disable-model-invocation: true` cannot be preloaded.
  - A subagent whose tool list includes the Skill tool, the default when `tools:`
    is omitted, can load skills itself. `code-reviewer`, `security-analyst`, and
    `agent-reviewer` declare `tools: Read, Glob, Grep, Bash` and cannot.
  - A `context: fork` command without `agent:` runs as a general-purpose subagent,
    which has the Skill tool.
  - Custom commands have been merged into skills, and the docs prefer skills for
    new work.
  - Anthropic's skill guidance: add only context the model lacks, keep reference
    files one level deep with a table of contents past 100 lines, build evals
    before extending a skill, compare with and without it, and test on each model
    in use.
- **Deviation, recorded.** This spec keeps `/debugger` and `/docs` as fork
  commands rather than skills with `context: fork`, against Claude Code's
  recommendation. All 30 Claude commands are command files, `skills/` is the
  harness-neutral shared tree, and the validator and index documents assume that
  split. Migrating commands to skills is a suite-wide layout change and goes on
  `docs/roadmap.md` as its own spec.
- **Eval harness.** Behavior cases assert with `order`, `tool_not_called`,
  `final_text`, `shell`, and `no_paths`. `order.first` takes `<tool[:regex]>`, and
  for non-Bash tools the regex runs against the call's input JSON, but
  `order.before` takes a bare tool name. Behavior cases take a fixture only from
  their own `fixture/` directory; routing cases already take
  `fixture: <path under evals/>`. `run-evals.py --model` pins the model; without it
  runs use the account default. None of the five existing behavior cases covers
  implementation work.
- **Platform scope.** The roster rule is Claude's alone; OpenCode keeps its 15
  agents. Skill edits reach all three harnesses. Verdicts here are measured on
  Opus 5.5 only, so a line cut as textbook may still have helped a different
  model under OpenCode or Codex; that is accepted.

## Approach

Evals first, then a rule-list cut, in two agent-suite branches of one session
each.

Branch 1 adds implementation evals with **red proofs**, the runner extension they
need, the roster change with ADR 0002, and an **ablation** per **style case**.
Branch 2 builds the rule list, which classifies every rule in scope as house style,
counter-correction, textbook, or restatement. The owner approves it; the cut
follows it one commit per file; `run-evals.py --base main` decides, and a
regression restores the rule as a single revert commit.

Red proof and ablation are different procedures. A red proof shows a case can fail
and needs one red run. An ablation tests whether the model follows a rule
unprompted: it removes every copy of the rule from everything the run loads (each
skill in the brief, `CLAUDE.md`, the implementer brief text), runs five times, and
only five green runs out of five mark the rule "textbook, candidate cut". Anything
less keeps the rule, recorded as guarded. A candidate cut still needs the owner's
approval in the rule list.

Every comparison, red proof, and ablation runs with `--model claude-opus-5-5`, and
each verdict records the model.

Alternatives considered: rewriting each skill from scratch against a budget (one
big behavior jump, regressions hard to attribute); ablating section by section
(costly, and anything the evals do not cover always looks cuttable); running real
`/implement-spec` per case (slow and flaky, and it measures orchestration rather
than the implementation skills).

## Components

### Part 1: agent roster (Claude only, Branch 1)

- **`docs/adr/0002-agents-earn-their-slot-by-use.md`.** A preload is not a
  capability on its own. An agent keeps its slot only for a harness-enforced
  capability that is exercised: tool limits, an MCP server, memory that gets
  written, or a model pin worth routing work off the session model. Agents with
  the same enforcement may stay separate when each is a natural-language routing
  target with its own preloaded method, because an agent with restricted tools has
  no Skill tool to load that method itself. It names the three agents removed here
  and says what evidence would bring one back. ADR 0001 gains a "see 0002" line.
- **`debugger` removed.** `platforms/claude/agents/debugger.md` deleted.
  `platforms/claude/commands/debugger.md` becomes `context: fork` and loads
  `debugging-methodology` plus `coding-guardrails`, following
  `commands/backend-engineer.md`. `evals/behavior/debugger-phase-0/case.yaml`
  keeps its prompt and assertions; its preload comment is rewritten for the fork.
  `evals/routing.yaml` line 309 becomes `expect: debugging-methodology`.
- **`documenter` removed.** `platforms/claude/agents/documenter.md` deleted.
  `platforms/claude/commands/docs.md` drops `agent: documenter` and loads
  `doc-templates` in its fork. `evals/routing.yaml` line 319 becomes
  `expect: doc-templates`. `platforms/claude/commands/implement-spec.md` line 8
  sends docs-only tasks to a general-purpose subagent whose brief names
  `doc-templates`.
- **`frontend-auditor` removed.** `platforms/claude/agents/frontend-auditor.md`
  deleted. `commands/frontend-audit.md` and `commands/frontend-critique.md` change
  `agent:` to `frontend-engineer` and open with "Report only; do not edit
  repository files." `frontend-audit.md`'s reference list drops
  `design-direction.md` and `verification.md`, which Branch 2 deletes.
  `frontend-engineer.md` gains one line: when the task says report only, browse
  and report, no edits. `evals/routing.yaml` line 324 becomes
  `expect: frontend-engineer`.
- **Index ripple.** `platforms/claude/CLAUDE.md` lines 11–14 (Routing: read-only
  list, memory, model pin), 41–42 and 49–50 (Commands table agent column), 81–82
  (Workflows rows stay; check wording). `scripts/test_evals.py` uses "debugger"
  only as synthetic parser data and stays.
- **Kept:** `code-reviewer`, `security-analyst`, `agent-reviewer`,
  `frontend-engineer`. Bodies trimmed in Branch 2.

### Part 2: implementation evals (Branch 1)

**Runner extension, `scripts/run-evals.py`.**

- `order.before` accepts `<tool[:regex]>` like `first`: `_order_problem` validates
  its pattern, `_check_order` passes it to `_first_index`.
- Behavior `case.yaml` gains an optional `fixture: <path under evals/>` key with
  the meaning routing cases already give it: added to `CASE_KEYS` and to case
  loading. A case may not carry both `fixture:` and a `fixture/` directory.
- Tests in `scripts/test_evals.py` for a path-qualified `before` passing and
  failing, and for the `fixture:` key; one line each in the Evals section of
  `AGENTS.md`.

**New fixture, `evals/fixtures/order-service/before/`.** Stdlib Python, no network:
`handlers.py` (thin HTTP route layer), `service.py`, `repo.py` (SQLite),
`payments.py` with `PaymentsClient.refund(order_id, amount, timeout=None)`,
`allowlist.py` with `is_allowed_ip`, `migrations/0001_init.sql` creating `orders`
with a `customer_email` column, and `test_*.py` green under `python3 -m unittest`.

**Two prompt shapes.**

- **Implementer-brief prompts** for style cases and `impl-clear-feature-finishes`:
  the fixture carries a one-task `spec.md`, and the prompt reads like the
  implementer brief without its commit and merge steps: "Implement task 1 of
  `spec.md`. Load `coding-guardrails`, `test-strategy`, and `<domain skill>`
  first." This measures the skill text under the pressure it actually runs under.
- **Plain prompts** for `impl-trivial-no-ceremony` and `impl-ambiguous-asks`, the
  two situations only the main thread meets.

**Style cases** guard a house-style rule. Each also gets an ablation of that rule.

| Case | Fixture | Task or prompt (gist) | Asserts | Red proof and ablation remove |
|---|---|---|---|---|
| `impl-test-first` | own `fixture/`: `ttl-cache` plus a ttl=0 expiry bug in `after/` and a `spec.md` | "Entries with ttl=0 never expire; fix it" | `order` `Edit:test_cache` before `Edit:/cache\.py` (and the Write pair); `shell` unittest `OK` | Test-first in `test-strategy`, the bug-fix line in `coding-guardrails` §4, and "builds the task test-first" in the brief |
| `impl-fixture-placeholders` | `fixtures/order-service` plus `spec.md` | "Add tests for `is_allowed_ip`: one blocked, one allowed address" | `shell` test file matches `192\.0\.2\.\|198\.51\.100\.\|203\.0\.113\.`, not `192\.168\.\|\b10\.\d` | Fixture Data in `test-strategy` |
| `impl-integration-timeout` | `fixtures/order-service` plus `spec.md` | "When an order is canceled, refund it through `PaymentsClient`" | `shell` diff contains `timeout=`; `service.py` imports neither `handlers` nor `http` (`grep … \|\| true`) | Integrations and Dependency Direction in `backend-patterns` |
| `impl-expand-contract` | `fixtures/order-service` plus `spec.md` | "Rename `customer_email` on orders to `email`" | `shell` new migration matches `(?i)ADD COLUMN`, not `(?i)DROP COLUMN\|RENAME COLUMN` | Migrations in `database-patterns` |
| `impl-frontend-tokens` | `fixtures/react-app` plus `spec.md` | "Add a status badge to Home: 'Synced' in the accent color, with an error variant" | `shell` added lines use `var\(--`, no hex color on `^\+` lines | "Reuse the existing visual system" in `frontend-patterns` |

**Freedom cases** guard against over-constraint; the red proof adds a constraining
rule and shows the case fails, except `impl-ambiguous-asks`, which guards the
opposite swing.

| Case | Fixture | Prompt (gist) | Asserts | Red proof |
|---|---|---|---|---|
| `impl-trivial-no-ceremony` | own `fixture/`: `ttl-cache` plus a docstring typo in `after/` | Plain: "Fix the typo in TTLCache's docstring" | `shell` diff touches only `cache.py`, one line; `final_text` has no `(?m)^\s*verify:` and does not end in `\?\s*$`; `tool_not_called: [Agent]` | Add "Present a numbered plan with verify lines and confirm before any edit" to `coding-guardrails` |
| `impl-clear-feature-finishes` | `fixtures/ttl-cache` plus `spec.md` | Brief: "Add `delete(key)` and make `len(cache)` count only live entries, with tests" | `shell` unittest `OK`; `def delete` and `def __len__` present; diff limited to `cache.py` and `test_cache.py`; `final_text` does not end in a question | Add "Confirm the interface with the user before adding any method" to `coding-guardrails` |
| `impl-ambiguous-asks` | `fixtures/order-service` | Plain: "Add discounts to orders" | `final_text` matches `\?`; `tool_not_called: [Edit, Write]` | Delete `coding-guardrails` §1 |

Common settings: `allowed_tools` of `Read`, `Glob`, `Grep`, `Edit`, `Write`,
`Bash(git diff*)`, `Bash(git status*)`, and `Bash(python3 -m unittest*)` (the
frontend case drops the unittest rule; its assertions are grep-based and need no
install); `timeout: 300`; `--model claude-opus-5-5` on every run. A full comparison
is 8 cases × 3 runs × 2 sides, about 48 runs; the ablations are 5 cases × 5 runs,
about 25, once in Branch 1.

A style case whose ablation stays green is kept as a regression guard, and its rule
enters the rule list as "textbook, candidate cut".

### Part 3: the skill cut (Branch 2)

**Rule list.** `docs/specs/2026-11-09-implementation-balance-rules.md`, one section
per skill plus agent bodies and index documents, headed with the model the
verdicts were measured on. Each row: the rule (quoted or paraphrased), its class,
its evidence (guarding case, ablation result, or judgment), and the decision
(keep, cut, rewrite, move). Ablation candidates arrive marked "candidate cut". The
owner approves the rule list before any skill is edited.

**Starting candidates** (the rule list decides):

| Skill | Keep | Cut or rewrite candidates |
|---|---|---|
| `coding-guardrails` | Simplicity test; ceremony versus architecture; surgical changes with reach versus shape; structure and error defaults (`run()` root, facades, errors with context and cause, no panics on recoverable paths) | The "bias toward caution over speed" opener and §1's broad ask list, rewritten to "ask when readings lead to materially different code and the repo cannot settle it"; the Guardrails table and Operating Loops (restate §1–4); Plan Template (ceremony); Naming and Comments to one pointer line |
| `test-strategy` | Vertical slices and tracer bullet; tautological assertions; three mocks or refactor; prefer fakes; spec-style test names; fixture placeholders | Coverage table (house targets or textbook, settled in the rule list); "skip tests of framework behavior"; the `code-review-checklist` pointer (cascade load) |
| `backend-patterns` | Dependency Direction; Validation table; Integrations; structured logs plus a metrics endpoint; fail closed | Routing table (restates the description); Request Path except "authn and authz handled separately" and "normalize once at the boundary"; the three Defaults bullets restating `coding-guardrails` §1 and §3 |
| `database-patterns` | Expand/migrate/contract; constraints before app checks; every delete rule explicit; indexes from evidence; no network call inside a transaction, outbox instead | Routing table and the closing pairing paragraph (one restates the other); textbook rows of the constraint and transaction tables |
| `frontend-patterns` | Non-negotiables; Context First table; Report | See below |

**`frontend-patterns` references.** Promote about ten house-taste lines into
`SKILL.md`: the AI-slop smells, one primary action per region, `gap` over margin
hacks, stable layout between loading and loaded states. Delete
`reference/design-direction.md` and `reference/verification.md`, which mostly
restate the skill. Keep `reference/accessibility-responsive.md`,
`reference/component-architecture.md`, and `reference/anti-patterns.md`, the full
catalog the audit commands point at. `component-architecture.md` (117 lines) gains
a table of contents. Update the router table.

**Descriptions.** Not cut. A description changes only where Branch 2 makes it
inaccurate (it advertises cut content or a deleted reference), with the matching
OpenCode and Codex rows, and that skill's routing cases must show no REGRESSION.

**Index documents.** The implementation bullet in `platforms/claude/CLAUDE.md`
General Guidelines drops to its load instruction ("Surface assumptions…, push
back…, smallest change" restates `coding-guardrails`); the same cut at
`platforms/opencode/AGENTS.md:149` and the matching line in
`platforms/codex/AGENTS.md`.

**Agent bodies.**

- `frontend-engineer`: How You Work to Playwright use, the report-only line from
  Part 1, and the output format; steps 1, 3, and 4 restate `frontend-patterns`.
- `security-analyst`: to scope plus theoretical-versus-practical exposure; steps
  2–5 restate `security-analysis`.
- `code-reviewer`, `agent-reviewer`: restatements only; the memory Bash fallback,
  the skill-reading paths, and the validator step stay.

One commit per skill or agent file, then a full `run-evals.py --base main
--model claude-opus-5-5` across implementation and routing cases.

## Testing

- **Validator** clean after every commit; the pre-commit hook enforces it.
- **Runner unit tests:** `scripts/test_evals.py` green, including the path-qualified
  `order.before` and behavior `fixture:` tests.
- **Branch 1:** each of the 8 implementation cases passes on head at two thirds or
  better; each red proof and ablation recorded in the table below; a full
  comparison against `main` with zero unexplained REGRESSION rows (the retargeted
  `debugger`, `documenter`, and `frontend-auditor` routing rows are explained in
  the PR).
- **Branch 2:** zero REGRESSION across all cases; before and after word counts per
  skill and agent in the PR body; every rule-list row marked cut has a matching
  deletion in the diff, and nothing else is deleted.

**Red proof and ablation results** (filled in by tasks 5 and 6; model
`claude-opus-5-5`):

| Case | Red proof | Red proof result | Ablation result (green of 5) | Verdict |
|---|---|---|---|---|
| `impl-test-first` | | | | |
| `impl-fixture-placeholders` | | | | |
| `impl-integration-timeout` | | | | |
| `impl-expand-contract` | | | | |
| `impl-frontend-tokens` | | | | |
| `impl-trivial-no-ceremony` | | | n/a | |
| `impl-clear-feature-finishes` | | | n/a | |
| `impl-ambiguous-asks` | | | n/a | |

## Risks & Open Questions

- **Risk:** rules no eval covers are protected only by rule-list approval.
  Mitigation: an explicit per-row decision, and a single revert commit per rule
  that later proves load-bearing, with a line added here.
- **Risk:** the softer `coding-guardrails` §1 could swing from over-asking to
  guessing. `impl-ambiguous-asks` guards that direction.
- **Risk:** verdicts hold for Opus 5.5 only. OpenCode and Codex share the skills
  under other models; accepted, since the runner drives only Claude Code and
  Opus carries nearly all implementer traffic.
- **Risk:** three runs per side is coarse. The runner confirms flagged cases with 5
  more runs; any other close call gets `--only <id> --runs 5`.
- **Risk:** the audit commands lose enforced read-only. They rely on an
  instruction, as the fork commands already do; an agent editing during an audit
  is the evidence ADR 0002 names for bringing `frontend-auditor` back.
- **Accepted:** `debugger` memory is lost with the agent. It was never written.
- **Open:** whether `test-strategy`'s coverage table holds house targets or
  textbook numbers. Settled in the rule list.

## Task Checklist

**Branch 1: `feat/impl-evals-and-roster`**

- [x] 1. `scripts/run-evals.py`: `order.before` accepts `<tool[:regex]>`
      (`_order_problem`, `_check_order`); behavior `case.yaml` gains optional
      `fixture: <path under evals/>` (`CASE_KEYS`, case loading; not combined with
      a `fixture/` directory). Tests in `scripts/test_evals.py`; one line each in
      the `AGENTS.md` Evals section.
- [x] 2. `evals/fixtures/order-service/before/`: `handlers.py`, `service.py`,
      `repo.py`, `payments.py` (`PaymentsClient.refund(order_id, amount, timeout=None)`),
      `allowlist.py` (`is_allowed_ip`), `migrations/0001_init.sql`
      (`orders.customer_email`), `test_*.py`; green under `python3 -m unittest`.
- [x] 3. Style cases `evals/behavior/impl-{test-first,fixture-placeholders,integration-timeout,expand-contract,frontend-tokens}/case.yaml`
      per the Part 2 table, with implementer-brief prompts and a one-task
      `spec.md` each; `impl-test-first` carries its own `fixture/`, the rest use
      `fixture:`. (blocked by 1, 2)
- [x] 4. Freedom cases `evals/behavior/impl-{trivial-no-ceremony,clear-feature-finishes,ambiguous-asks}/case.yaml`
      per the Part 2 table; `impl-trivial-no-ceremony` carries its own `fixture/`.
      (blocked by 1, 2)
- [ ] 5. Red proof for each of the 8 cases with
      `scripts/run-evals.py --only behavior/impl-<case> --model claude-opus-5-5`;
      restore and record in the results table. (blocked by 3, 4)
- [ ] 6. Ablation for each style case: grep every copy of the rule out of the
      loaded skills, `platforms/claude/CLAUDE.md`, and the brief text; run
      `--runs 5 --model claude-opus-5-5`; restore; record green-of-5 and the
      verdict. (blocked by 3)
- [x] 7. `docs/adr/0002-agents-earn-their-slot-by-use.md`; "see 0002" line in
      `docs/adr/0001-agents-earn-their-slot-by-capability.md`.
- [x] 8. Remove `debugger`: delete `platforms/claude/agents/debugger.md`;
      `platforms/claude/commands/debugger.md` to a fork loading
      `debugging-methodology` and `coding-guardrails`; rewrite the preload comment
      in `evals/behavior/debugger-phase-0/case.yaml`; `evals/routing.yaml:309` to
      `expect: debugging-methodology`.
- [x] 9. Remove `documenter`: delete `platforms/claude/agents/documenter.md`;
      `platforms/claude/commands/docs.md` drops `agent: documenter` and loads
      `doc-templates`; `evals/routing.yaml:319` to `expect: doc-templates`;
      `platforms/claude/commands/implement-spec.md` line 8 sends docs-only tasks to
      a general-purpose subagent briefed with `doc-templates`.
- [x] 10. Remove `frontend-auditor`: delete `platforms/claude/agents/frontend-auditor.md`;
      `commands/frontend-audit.md` and `commands/frontend-critique.md` to
      `agent: frontend-engineer` with a report-only opening line, and drop the
      `design-direction.md` and `verification.md` pointers; add the report-only
      line to `platforms/claude/agents/frontend-engineer.md`;
      `evals/routing.yaml:324` to `expect: frontend-engineer`.
- [x] 11. `platforms/claude/CLAUDE.md` lines 11–14, 41–42, 49–50, 81–82 for the
      three removals. (blocked by 8, 9, 10)
- [ ] 12. Validator; full `scripts/run-evals.py --base main --model claude-opus-5-5`;
      PR with the report; merge; add this spec and a "migrate Claude commands to
      skills" entry to `docs/roadmap.md`; bump the dotfiles pointer.
      (blocked by 1–11)

**Branch 2: `refactor/impl-skills-balance`**

- [ ] 13. Write `docs/specs/2026-11-09-implementation-balance-rules.md`: one
      section per skill plus agent bodies and index documents, seeded with task
      6's candidate cuts; owner approves. (blocked by 12)
- [ ] 14. `skills/coding-guardrails/SKILL.md` per the rule list. (blocked by 13)
- [ ] 15. `skills/test-strategy/SKILL.md` per the rule list. (blocked by 13)
- [ ] 16. `skills/backend-patterns/SKILL.md` per the rule list. (blocked by 13)
- [ ] 17. `skills/database-patterns/SKILL.md` per the rule list. (blocked by 13)
- [ ] 18. `skills/frontend-patterns/`: promote about ten lines into `SKILL.md`;
      delete `reference/design-direction.md` and `reference/verification.md`; add
      a table of contents to `reference/component-architecture.md`; update the
      router table; grep `platforms/` for the two deleted paths and fix every hit;
      correct the description and its OpenCode and Codex rows only if it now
      advertises deleted content. (blocked by 13)
- [ ] 19. Implementation bullet in `platforms/claude/CLAUDE.md` General Guidelines
      to its load instruction; same cut at `platforms/opencode/AGENTS.md:149` and
      in `platforms/codex/AGENTS.md`; agent bodies per the rule list:
      `frontend-engineer`, `security-analyst`, `code-reviewer`, `agent-reviewer`
      in `platforms/claude/agents/`. (blocked by 13, 18)
- [ ] 20. Validator; full `scripts/run-evals.py --base main --model claude-opus-5-5`;
      PR with word counts; merge; tick the roadmap row; bump the dotfiles pointer.
      (blocked by 14–19)
