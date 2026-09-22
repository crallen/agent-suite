# Skills density cut

## Goal

Cut roughly a quarter of the skills tree, about 1,300 of 5,700 lines, without
losing a house convention. Every skill ends up front-loading its trigger and its
non-obvious rules, states each rule once, describes success rather than
enumerating failure, and carries no general engineering knowledge a Fable-class
model already has. agent-authoring becomes one shared skill with per-platform
references, and skill-design's glossary folds into its SKILL.md.

## Context

- **The cutting rule is already in the repo.** skill-design defines the no-op test
  ("does it change behaviour versus the default?") and names duplication,
  sediment, sprawl, and negation as failure modes. Current-model prompt guidance
  says the same: delete a line if removing it changes neither what is permitted
  nor how success is judged; keep numbered steps only where order matters; prefer
  positive statements. This spec applies those rules to the suite's own skills.
- **Cluster sizes and reviewer cut estimates (2026-09-22):**

| Cluster | Lines | Estimated cut |
|---|---|---|
| Engineering: coding-guardrails, backend, database, frontend, test-strategy, code-review-checklist, security-analysis, debugging, git-conventions, ci-pipeline, docker | 2,846 | 650–750 |
| Meta and writing: agent-authoring (two copies), skill-design plus GLOSSARY, doc-templates, unslop | 1,785 | 400–430 |
| Methodology: spec-writing, grill, wayfinder, architecture-review, domain-modeling, prototype, ticket-writing, why, blast-radius | 1,107 | 140–150 |

- **Where the weight is.** Engineering: textbook restated (test pyramid, OWASP Top
  10, Conventional Commits table, EXPLAIN workflow), the same verification loop in
  coding-guardrails and test-strategy, backend/database routing said four times,
  the frontend state list seven times and the escalation rule three. Meta: the
  README, API, and changelog templates, the glossary, the two agent-authoring
  copies. Methodology: spec-writing is the outlier at 202 lines with a section
  table duplicating its template, anti-pattern lists in five skills, and the
  isolation principles restated across spec-writing and architecture-review.
- **Load-bearing and staying:** coding-guardrails' four references and plan
  template; test-strategy's coverage table and fixture placeholders;
  code-review-checklist's Fowler baseline and output format; security-analysis'
  report format and severity matrix; debugging Phase 0; ci-pipeline's audit and
  toolchain procedures; docker gotchas; git-conventions' "most commits need no
  body"; wayfinder's map format; domain-modeling's type gate and ADR format;
  grill's frontier mechanics; the frontend router shape.
- **Descriptions.** Nine engineering skills describe identity rather than
  triggers. After the platform spec, Claude reads descriptions only from
  frontmatter via the harness listing, and OpenCode and Codex rows must match
  each other. A description rewrite touches frontmatter plus two index rows.
- **Dependencies.** Lands after the routing spec (harness-neutral wording,
  factual fixes, CI pins already done) and the validator spec (key allowlists,
  `check_shared_links` carve-out to remove). The platform spec's parity change
  makes the index edits two-sided rather than three.

## Decisions

- agent-authoring becomes one shared skill: neutral `SKILL.md` plus
  `reference/claude.md` and `reference/opencode.md`; the OpenCode copy becomes a
  symlink; the exception clause and validator carve-out go.
- skill-design's GLOSSARY.md is deleted; its six unique entries fold into
  SKILL.md at first use.

## Approach

Three branches, one per cluster, each a single session: meta first because
agent-authoring's restructure changes what the validator carves out, then
engineering, then methodology. Each branch has one commit per skill so a bad cut
reverts alone.

Per skill, the procedure is fixed: classify every line as trigger, non-obvious
rule, house format, or other; delete "other" that fails the no-op test; state
surviving rules once in the section that owns them; rewrite prohibitions as the
target behavior; move the trigger and non-obvious rules above the fold; rewrite
the description as triggers. Line counts before and after go in the PR body per
skill.

## Components

**Branch 1, meta: `refactor/skills-meta`**

- `skills/agent-authoring/SKILL.md` becomes the harness-neutral core, about 120
  lines: what agents, skills, and commands are; the agent body template;
  skill-writing conventions with the "self-contained" bullet deleted and the
  disclosure rule kept; cross-cutting rules; the checklist. Stale text goes: the
  color table, the `/debug`/`/review`/`/verify` bundled-skill list, "workflow
  skills are prompts", the four repeated explanations of
  `disable-model-invocation`, the mixed path frames.
- `skills/agent-authoring/reference/claude.md`: Claude Code frontmatter for
  agents, skills, commands; tools and `disallowedTools`; `memory`; `mcpServers`;
  `context: fork` and routing styles; the named color palette; paths under
  `~/.claude/`. Gains the three-sentence `experimental.cacheTtl` note from the
  platform spec.
- `skills/agent-authoring/reference/opencode.md`: `mode`, `permission`, `hidden`,
  `subtask`, hex colors; `opencode.json` removed; "Restrict with `tools:`"
  corrected to `permission:`; no `skills:` preload claim.
- `platforms/opencode/skills/agent-authoring` deleted as a directory, recreated
  as a symlink. `AGENTS.md` loses the exception paragraph; README's "one skill is
  deliberately not shared" paragraph goes. `scripts/validate-config.py`
  `check_shared_links` drops the `hand_maintained` set.
  `platforms/claude/agents/agent-reviewer.md` and
  `platforms/opencode/agent/agent-builder.md` gain one line: load the reference
  for the harness you are on.
- `skills/skill-design/SKILL.md`: fold in completion criterion, legwork,
  premature completion, co-location, external reference, cognitive load at first
  use; drop the "bold terms are defined in GLOSSARY" sentence; add the one clause
  that a reference skill may take arguments; opener restating the description
  goes. `GLOSSARY.md` deleted. `agent-reviewer.md` line 17 points at SKILL.md.
- `skills/doc-templates/SKILL.md`: README, API endpoint, and changelog templates
  become one-line section orders each, keeping only the `(#issue-number)` house
  style; the comment-format example, the Diátaxis prose padding, and the seven
  "Don't" bullets go, the latter rewritten as three positive lines. Register,
  Naming, Accuracy, and the opinionated comment rules stay verbatim. About 282
  lines to 140.
- `skills/unslop/SKILL.md`: drop the Wikipedia-derived tells that don't occur in
  developer prose and the paragraph duplicating doc-templates' Register; keep the
  punctuation, formatting, and rule-of-three lists. About 18 lines out.

**Branch 2, engineering: `refactor/skills-engineering`**

- `coding-guardrails/SKILL.md`: delete the Diff Discipline checkbox restatement
  and the Anti-Patterns index; trim §1 to its "when to ask" list; description
  rewritten as triggers. References untouched.
- `test-strategy/SKILL.md`: delete the verification-loop bullets duplicated from
  coding-guardrails, keeping "clarify before encoding"; the TDD section to about
  15 lines around the vertical-slice rule; the pyramid and unit/integration/e2e
  definitions go, keeping "three mocks or refactor" and "prefer fakes" as two
  lines. Coverage table, fixture rules, helper naming stay. About 185 to 85.
- `code-review-checklist/SKILL.md`: §0 to "review what's absent" plus a pointer
  to coding-guardrails; §2 to one line pointing at security-analysis; §6 to a
  pointer at test-strategy's coverage table; §1, §3, §5, §7 to their
  house-specific lines; delete the row-format restatement.
  `reference/review-table.md` deleted; the in-file column spec suffices.
- `security-analysis/SKILL.md`: report format and severity matrix move to the
  top; Phase 1 to the three trust-boundary questions; Phase 3 to category
  headings with CWE ids plus the dependency tool list; remediation table deleted.
  `reference/security-table.md` deleted.
- `backend-patterns/SKILL.md` and `database-patterns/SKILL.md`: one two-row
  routing table each, trailing "when the other takes over" sections deleted;
  handler, auth, and integration checklists deleted from backend; schema
  checklist, index rules of thumb, EXPLAIN workflow, ORM guidance deleted from
  database. Expand/Migrate/Contract, the transaction boundary table, the
  constraint table, dependency direction, and the observability defaults stay.
- `debugging-methodology/SKILL.md`: Phase 5 to the seam rule plus re-run and
  variant search; the root-cause table, "read stack traces bottom up", `git log`,
  `git bisect start`, and Anti-Patterns go. Phase 0, hypothesis format, log
  tagging, Phase 6 stay.
- `git-conventions/SKILL.md`: type table to a type-to-bump list; one example;
  hygiene section deleted. Filesystem Safety from the routing spec stays.
- `ci-pipeline/SKILL.md`: principles to the stage diagram plus the non-obvious
  sixth principle; `reference/gitlab-ci.md` loses the Jest-specific coverage
  regex. `docker-best-practices/SKILL.md`: the two generic layer-hygiene sections
  deleted.
- `frontend-patterns/`: SKILL.md deletes Common Load Sets and §4; the state list
  lives at line 14 only; `reference/verification.md` §3–4 deleted;
  `reference/design-direction.md` §9 and its "watch for" lists merged into
  `anti-patterns.md`; the generic good-defaults prose trimmed to the opinionated
  lines; `accessibility-responsive.md` and `component-architecture.md` lose their
  re-summarising sections. About 683 to 500.
- All nine identity-style descriptions rewritten as triggers, with the matching
  OpenCode and Codex rows.

**Branch 3, methodology: `refactor/skills-methodology`**

- `spec-writing/SKILL.md`: delete the section table (template stays),
  Anti-Patterns, Proportionality, YAGNI, the exploration bullets except the
  targeted-fixes rule, and one of the two "no skipping" sentences; Isolation and
  Clarity to three lines pointing at architecture-review's vocabulary, adopting
  "module"; the spec path convention moves up into Phase 7; description gains a
  trigger; opener goes. About 202 to 135.
- `architecture-review/`: SKILL.md loses the duplicate "read vocabulary first"
  and the reconciliation paragraph; `reference/vocabulary.md` deletes
  Relationships and the spec-writing exception clause and absorbs the
  deletion-test and test-surface rules from `deepening.md`, which points at it.
- `grill-methodology/SKILL.md`: delete Session Behaviors (domain-modeling owns
  it) and the intro restating the description.
- `domain-modeling/SKILL.md`: delete Anti-Patterns; trim the CONTEXT-MAP lookup
  prose to "create files lazily"; the fuzzy-word list stays, surrounding prose
  goes.
- `prototype-methodology/reference/logic.md`: delete State the Question, Pick the
  Language, Make it Runnable, and the anti-pattern list; `reference/ui.md` keeps
  only the two structural anti-patterns.
- `ticket-writing/SKILL.md`: anti-pattern table to the two rows with new content.
- `wayfinder-methodology/SKILL.md`: the command comparison to the decisive line
  plus the `/ticket` distinction. why and blast-radius unchanged beyond the
  routing spec.

## Testing

- **Validator clean after every commit**, with the meta branch's
  `check_shared_links` change first.
- **Line counts per skill** before and after in each PR body. Pass is the cluster
  within 20 percent of its estimate; a skill far under estimate gets a second
  look for over-cutting.
- **Harness grep:** zero hits for harness terms in `skills/` after the meta
  branch, since agent-authoring's neutral core must not name either harness.
- **Behavior smoke tests, one per cluster, fresh session each:**
  - Meta: `/agent-review` on the suite reports the platform reference it loaded
    and finds a deliberately planted color collision.
  - Engineering: ask for a bug fix in a scratch repo; the model writes the
    failing test first and stops at the "three mocks" rule when tempted. Ask for
    a review; the output uses the checklist's table format with severities.
  - Methodology: `/spec` on a toy goal asks one lettered question at a time,
    presents in stages, and saves under `docs/specs/` with the dated name.
- **Preload size:** the per-agent prefix script from the platform spec, run
  after the meta branch; agent-reviewer under 20 KB.
- **OpenCode:** `@agent-builder` loads `reference/opencode.md` when asked to
  create an agent and produces valid `permission:` frontmatter.

## Risks & Open Questions

- **Risk:** over-cutting a rule that was quietly load-bearing. One commit per
  skill and the per-cluster smoke test are the safeguards.
- **Risk:** the neutral agent-authoring core still needs to say which reference
  to load. The one-line instruction in the two agent bodies covers the agents; a
  human typing `/agent-builder` on Claude gets the command, which names the
  platform. Codex has no agent-authoring link and none is planned.
- **Risk:** three sessions of judgment calls drift in strictness. The fixed
  per-skill procedure and the line-count check keep them comparable. Meta first
  calibrates the rule on the skills that define it.
- **Risk:** description rewrites change when skills trigger. Intended; the
  engineering smoke test catches a trigger that stops firing for its core use.
- **Open:** whether `reference/review-table.md` and `security-table.md` have
  external readers. Grep shows only their own skills. Deleted unless the grep at
  implementation time says otherwise.

## Task Checklist

Each branch in agent-suite, one commit per skill, validator after each. Order:
meta, engineering, methodology.

**Branch 1: meta**
- [ ] Restructure `skills/agent-authoring/`: neutral `SKILL.md`,
      `reference/claude.md`, `reference/opencode.md`; stale lines out; `cacheTtl`
      note in.
- [ ] Replace `platforms/opencode/skills/agent-authoring` with a symlink; update
      `AGENTS.md`, `README.md`, and `check_shared_links`.
- [ ] Add the load-your-platform-reference line to `agent-reviewer.md` and
      OpenCode `agent-builder.md`.
- [ ] `skills/skill-design/SKILL.md`: fold in the six glossary entries; drop the
      bold-term contract; add the arguments clause; delete `GLOSSARY.md`; repoint
      `agent-reviewer.md`.
- [ ] `skills/doc-templates/SKILL.md`: templates to section orders; positive
      rewrite of the Don't list; Register, Naming, Accuracy untouched.
- [ ] `skills/unslop/SKILL.md`: remove the non-developer tells and the Register
      duplicate.
- [ ] Line counts, harness grep, meta smoke test, agent-reviewer preload size;
      merge.

**Branch 2: engineering**
- [ ] `coding-guardrails`: Diff Discipline checkboxes, Anti-Patterns, §1 trim,
      description.
- [ ] `test-strategy`: loop bullets, TDD trim, pyramid out, mock rules kept as
      two lines.
- [ ] `code-review-checklist`: §0, §2, §6 to pointers; §1/3/5/7 trimmed; delete
      `reference/review-table.md`.
- [ ] `security-analysis`: format first; Phase 1 and 3 trimmed; remediation
      table and `reference/security-table.md` deleted.
- [ ] `backend-patterns`, `database-patterns`: one routing table each;
      checklists deleted; keep the named tables.
- [ ] `debugging-methodology`: Phase 5 trim; generic sections and Anti-Patterns
      deleted.
- [ ] `git-conventions`: type-to-bump list; one example; hygiene deleted.
- [ ] `ci-pipeline`, `docker-best-practices`: principles trim; gitlab regex;
      layer-hygiene sections.
- [ ] `frontend-patterns`: SKILL.md and five references per Components.
- [ ] Nine descriptions to trigger form plus OpenCode and Codex rows.
- [ ] Line counts, engineering smoke test; merge.

**Branch 3: methodology**
- [ ] `spec-writing`: per Components; path convention into Phase 7; description
      trigger.
- [ ] `architecture-review`: SKILL.md duplicates out; vocabulary.md absorbs
      deepening.md's shared rules.
- [ ] `grill-methodology`: Session Behaviors and intro out.
- [ ] `domain-modeling`: Anti-Patterns out; lookup prose trimmed.
- [ ] `prototype-methodology` references: duplicate steps and anti-pattern lists
      out.
- [ ] `ticket-writing`: anti-pattern table to two rows.
- [ ] `wayfinder-methodology`: command comparison trimmed.
- [ ] Line counts, methodology smoke test; merge.

**Close**
- [ ] Bump the submodule pointer in dotfiles after each merged branch.
