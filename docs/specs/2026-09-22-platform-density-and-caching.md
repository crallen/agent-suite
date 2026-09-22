# Platform-layer density and caching

## Goal

Shrink the always-loaded Claude prefix and each subagent's prefix to what a
Fable-class model actually needs, and remove the platform layer's triple-stated
rules, restated agent bodies, and dated prompt patterns. The Claude index drops
from about 16 KB to roughly 8 KB per session. The validator keeps enforcing
description parity between the OpenCode and Codex indexes.

## Context

- **Caching mechanics, from the Claude Code docs.** The system prompt and project
  context (CLAUDE.md) are cached once per session and re-read at the cached rate
  every turn. Skills and commands inject as messages and never invalidate the
  prefix. CLAUDE.md edits don't apply mid-session. A `model:` on a command is a
  full cache miss for that turn; none in the suite has one. Subagents build their
  own prefix from body plus preloaded skills, on a five-minute TTL. Inline
  `mcpServers` on an agent keeps Playwright out of the main conversation.
- **What the harness already injects.** Every session gets the skill list with
  descriptions and the agent-type list with descriptions. CLAUDE.md's Skills table
  (4.4 KB) and Agents table (1.3 KB) repeat them. Commands with
  `disable-model-invocation` are hidden, so the Commands table is the only listing
  the model cannot otherwise see.
- **CLAUDE.md sections by size:** How I Work 3.1 KB, Skills 4.4 KB, Commands
  3.0 KB, General Guidelines 2.4 KB, Workflows 1.8 KB, Agents 1.3 KB.
  `/coding-guardrails` appears three times, "surface assumptions" and "smallest
  change" twice each, `/spec`-first twice. Line 10 names `TaskCreate` and
  `TaskUpdate`, which don't exist in this harness build.
- **Subagent prefixes (body + preloaded skills):** agent-reviewer 35 KB
  (agent-authoring alone is 24 KB), code-reviewer 20 KB, debugger 18 KB,
  frontend-engineer 16 KB, security-analyst 12 KB. The skill halves shrink in the
  skills density spec; this spec handles the bodies.
- **Validator coupling.** `check_index_description_parity` reads CLAUDE.md as the
  core index and compares OpenCode and Codex rows to it. `check_index` requires
  every skill and agent to be mentioned in CLAUDE.md.
- **Reviewer findings on bodies (2026-09-22):** command bodies for `/frontend`,
  `/frontend-polish`, `/frontend-audit`, `/frontend-critique`, `/commit`, `/ship`
  restate the agent they route to; security-analyst re-specifies the report format
  its skill owns; frontend-engineer says the same quality bar three ways with five
  "avoid" bullets; OpenCode tech-lead's delegate list restates the OpenCode index
  it is always loaded next to; OpenCode agent-builder carries a 90-line body half
  of which is agent-reviewer; the four architect-persona commands explain a
  frontmatter choice to the maintainer and restate their skill; OpenCode's index
  keeps a "Primary users" column and a no-op "use the commands as appropriate"
  line.
- **Dated patterns present:** `Do NOT route away`, "Be specific / Be constructive"
  virtue lists, `CRITICAL` in OpenCode agent-builder and security-analyst, persona
  openers on every agent.
- **Dependencies.** The routing spec changes `CLAUDE.md` lines 23, 42, 59,
  106–108 and several command bodies. This spec lands after it and the validator
  spec, and edits the resulting text.

## Decisions

- Drop the Skills and Agents tables from CLAUDE.md; keep Routing, Commands,
  Workflows, General Guidelines.
- Cut How I Work to Routing plus the load-bearing lines; each rule stated once.
- No subagent TTL changes; document the tradeoff instead.

## Approach

One branch in agent-suite after the routing and validator specs merge, five
commits: index, validator, Claude agents, Claude commands, OpenCode layer. Every
cut is checked against one rule from the prompt-audit guidance: delete a line if
removing it changes neither what is permitted nor how success is judged. Persona
lines shrink to one focus-setting sentence rather than vanish. The settings
example gains a comment on TTLs, not a setting.

Before and after, `/context` in a fresh session records the CLAUDE.md token
count, and a scripted byte count records each subagent prefix, so the result is a
number rather than an impression.

## Components

**1. `platforms/claude/CLAUDE.md`**

- Delete the Skills and Agents tables and their headings.
- Replace How I Work with a Routing section of about 12 lines: the capability
  rule, the route-to bullets as they stand after the routing spec, "do the work
  yourself for everything else", "scope down the mechanism, not the goal", and one
  sentence that commands are explicit-only and should be recommended by name,
  never invoked. The persona sentence, the four numbered steps, the
  `TaskCreate`/`TaskUpdate` reference, and the eight Guidelines bullets go.
- General Guidelines becomes the single home for each rule: concise-but-complete
  reporting, the T3 Code paragraph, CONTEXT.md precedence, `/spec` for ambiguous
  work, `coding-guardrails` plus the domain skill for implementation, surface
  assumptions, smallest change, `gh` for GitHub, commit-message brevity, no
  follow-up lists, no attribution, no secret files. Each once.
- Commands and Workflows tables stay as they are.
- Target: about 8 KB, measured.

**2. `scripts/validate-config.py`**

- `check_index` for CLAUDE.md drops the "every skill and agent must be mentioned"
  half; commands still must be. Named-must-exist stays for all three token kinds.
- `check_index_description_parity` compares OpenCode rows against Codex rows
  directly; CLAUDE.md leaves the comparison. Coupling rows to the frontmatter
  description was considered and rejected: it would force every index row to carry
  the long trigger clause in two always-loaded documents. The frontmatter stays
  the trigger; the index rows stay the short blurb, identical across the two
  platforms that have them. The "zero rows compared" guard stays.

**3. Claude agents (`platforms/claude/agents/`)**

- Every body: persona opener cut to one sentence naming the focus.
- `security-analyst.md`: Output Format becomes one pointer to the skill's report
  format. Guidelines keep only the secret-file rule and "distinguish theoretical
  from practical exposure".
- `frontend-engineer.md`: Execution Defaults, Quality Bar, and Guidelines merge
  into one positive list of five bullets. Step 5's Playwright instruction and the
  Output Format stay.
- `code-reviewer.md`, `debugger.md`, `documenter.md`, `frontend-auditor.md`,
  `agent-reviewer.md`: Guidelines lose "be specific", "be constructive", "be
  proportionate", and any bullet that restates a How You Work step or a preloaded
  skill's rule. Memory sections stay, with the routing spec's Bash fallback line.

**4. Claude commands (`platforms/claude/commands/`)**

- `frontend.md`, `frontend-polish.md`, `frontend-audit.md`, `frontend-critique.md`:
  body is the task sentence plus `$ARGUMENTS`.
- `ship.md`: "Same as `/commit`, then push to the tracking branch", plus the
  injected state.
- `spec.md`, `grill.md`, `architecture.md`, `wayfinder.md`: delete the "runs
  inline because a fork cannot pause" sentence and "operating as the architect".
  Body becomes "Load `<skill>` and follow it for the goal below", injected state,
  `$ARGUMENTS`.

**5. OpenCode layer (`platforms/opencode/`)**

- `agent/tech-lead.md`: When to Delegate shrinks to the exceptions the index
  table cannot express: architect never via Task, the built-in explore and general
  agents, and the do-not-delegate cases. Duplicate architect paragraph and the
  Guidelines that repeat the index go.
- `agent/agent-builder.md`: Reviewing Existing Artifacts and Output Format
  replaced by "for review, use `@agent-reviewer`". `CRITICAL` markers become plain
  sentences. Index row becomes "Creates and modifies".
- `agent/security-analyst.md`, `agent/frontend-engineer.md`, `agent/debugger.md`,
  `agent/documenter.md`: same trims as their Claude twins.
- `AGENTS.md`: drop the "Primary users" column and the "use `/code-review`,
  `/security`… as appropriate" line. The permission-model paragraph stays; add
  the half-sentence that `/full-review` routes a primary as a subtask.

**6. `platforms/claude/settings.json.example`**

- A comment block next to `effortLevel`: main-conversation cache is one hour on
  a subscription within plan usage and five minutes on an API key or usage
  credits; `promptCacheTtl: "1h"` restores it in the latter case; subagent TTLs
  are left at default on purpose. The skills density spec puts the same three
  sentences in `agent-authoring` under `experimental.cacheTtl`.

## Testing

- **Byte and token counts.** Before: `wc -c` on CLAUDE.md, the per-agent prefix
  script, and `/context` in a fresh session. After: the same three numbers in the
  PR body. Pass is CLAUDE.md at or under 9 KB and no agent prefix larger than
  before.
- **Validator.** Passes with the two check changes. Break test: remove the `why`
  row from OpenCode's index; expect "exists but is never mentioned" from the
  OpenCode check and silence from the Claude check. Change one Codex row; expect
  the parity failure to name Codex and OpenCode, not CLAUDE.md.
- **Behavior smoke test, fresh session:** ask for a code review; the model routes
  to `@code-reviewer` without CLAUDE.md naming it. Ask "what commands do I have";
  the model lists them from the Commands table. Ask for a backend change; the
  model loads `backend-patterns` from the harness listing.
- **Command smoke test:** `/frontend`, `/spec`, `/ship` each run as intended after
  their bodies shrink.
- **OpenCode:** `/full-review` still runs; tech-lead still delegates to architect
  by direct invocation.

## Risks & Open Questions

- **Risk:** the harness listing changes shape. If a future build stops injecting
  skill descriptions, CLAUDE.md needs the table back. Revert is one commit.
- **Risk:** over-cutting agent bodies. Mitigated by the deletion rule, the smoke
  tests, and agents in their own commit.
- **Risk:** OpenCode and Codex indexes still carry full tables. Deliberate;
  neither harness injects the listing the way Claude Code does.
- **Open:** exact token figure. `/context` gives it; bytes are the proxy until then.

## Task Checklist

Branch `refactor/platform-density` in agent-suite, after the routing and
validator specs merge.

**1. Index**
- [ ] Record baseline: `wc -c platforms/claude/CLAUDE.md`, the per-agent prefix
      script output, and `/context` in a fresh session.
- [ ] `platforms/claude/CLAUDE.md`: delete the Skills and Agents sections; rewrite
      How I Work as the ~12-line Routing section; merge Guidelines into General
      Guidelines with each rule once; remove `TaskCreate`/`TaskUpdate`.

**2. Validator**
- [ ] `scripts/validate-config.py` `check_index`: Claude index no longer requires
      skill or agent mentions; commands still required.
- [ ] `check_index_description_parity`: compare OpenCode rows to Codex rows;
      CLAUDE.md out of the comparison; keep the zero-rows guard.
- [ ] Run the two break tests; validator clean.

**3. Claude agents**
- [ ] All eight bodies: one-sentence focus opener.
- [ ] `security-analyst.md`: Output Format to a pointer; Guidelines to two bullets.
- [ ] `frontend-engineer.md`: three lists merged into one positive five-bullet list.
- [ ] `code-reviewer.md`, `debugger.md`, `documenter.md`, `frontend-auditor.md`,
      `agent-reviewer.md`: remove virtue bullets and restated rules.

**4. Claude commands**
- [ ] Four frontend commands: task sentence plus `$ARGUMENTS`.
- [ ] `ship.md`: reference `/commit`.
- [ ] `spec.md`, `grill.md`, `architecture.md`, `wayfinder.md`: drop maintainer
      notes and persona phrase; "Load X and follow it".

**5. OpenCode**
- [ ] `agent/tech-lead.md`: delegate list to the exceptions only; remove the
      duplicate paragraph and index-repeating guidelines.
- [ ] `agent/agent-builder.md`: remove the review half; plain sentences for
      `CRITICAL`; index row reworded.
- [ ] `agent/security-analyst.md`, `frontend-engineer.md`, `debugger.md`,
      `documenter.md`: mirror the Claude trims.
- [ ] `AGENTS.md`: drop the Primary users column and the no-op line; add the
      `/full-review` subtask note.

**6. Settings and verification**
- [ ] `settings.json.example`: TTL comment block.
- [ ] Record the after numbers; CLAUDE.md at or under 9 KB.
- [ ] Run the behavior, command, and OpenCode smoke tests; note results in the
      PR body.
- [ ] Merge; bump the submodule pointer in dotfiles.
