# Collapsing the agents

## Goal

Cut Claude's agent roster from 14 to 8 by removing six agents that exist only to
hold a persona and preload a skill. Recover roughly 740 tokens per turn — about
340 in agent descriptions and 400 in `CLAUDE.md` roster prose — and replace prose
routing (`Use the @tester subagent...`) with routing the harness performs.

OpenCode is out of scope and keeps all 15 of its agents.

## Context

`agents/` sits at the repo root labelled canonical, but it has exactly one
consumer: `claude/.claude/agents`, a single line in the dotfiles link manifest.
OpenCode's roster is 15 independent real files under `platforms/opencode/agent/`,
including a `tech-lead` that Claude does not have. Nothing is shared, so a change
to Claude's roster cannot reach OpenCode.

The two platforms also route differently. Claude wires five commands to an agent
through frontmatter and names an agent in body prose for thirteen more. OpenCode
wires every command structurally with `agent:` plus `subtask: true`. A prose
route is a request the model can ignore — the same class of defect as the
`disable-model-invocation` regression fixed in `3e6c991`.

Measured before any change:

```
3180 chars of agent description  ~795 tokens, every turn
3733 chars of roster prose       ~933 tokens, every turn  (When to Delegate + Agents table)
```

## Approach

Keep an agent only where it carries a capability a skill cannot express. Drop the
rest, fold whatever guidance is genuinely theirs into the skills they preloaded,
and move the surviving roster under `platforms/claude/` where its only consumer
lives.

**The rule this establishes: an agent must justify itself by a capability, not by
a topic.**

Alternatives considered. Folding the residue into command bodies instead of
skills keeps `skills/` untouched, but strands domain guidance in Claude-only
files and leaves `devops-engineer` — which has no command — with nowhere to put
its content. Deleting the six outright is a smaller diff but loses nine lines
that no skill covers.

## Components

### Agents that survive (8)

| Agent | Capability no skill can express |
|---|---|
| `code-reviewer` | `tools:` + `disallowedTools` enforce read-only |
| `security-analyst` | same |
| `agent-reviewer` | same |
| `frontend-auditor` | same, plus inline Playwright MCP |
| `frontend-engineer` | inline `mcpServers:` (Playwright) |
| `debugger` | `memory: local` |
| `documenter` | `model: sonnet` cost pin |
| `git-manager` | `model: sonnet` cost pin |

### Agents removed (6)

`agent-builder`, `architect`, `backend-engineer`, `database-specialist`,
`devops-engineer`, `tester`.

`architect` is already documented in `CLAUDE.md` as "do NOT delegate via subagent
task", so removing it costs nothing. `devops-engineer` has no command and no
`@`-reference anywhere; it is pure description tax today.

### Residue to fold into skills

Nine lines are not covered by the skill each agent preloaded. `architect` has no
residue — `spec-writing` already covers all of it.

| Destination | Lines to add |
|---|---|
| `backend-patterns` | auth/validation/integration as first-class concerns; match existing error, serialization, logging and DI patterns; surface ambiguous API contracts, authorization rules and side effects before encoding them |
| `database-patterns` | prefer explicit constraints and transaction boundaries over application-only assumptions |
| `test-strategy` | clarify expected behavior before cementing it in tests |
| `docker-best-practices` | minimal images, least privilege, no secrets baked into artifacts; health checks |
| `backend-patterns` (operability) | structured logging and metrics endpoints as service defaults |
| `agent-authoring` | least privilege — restrict with `tools:`, omit only when write access is genuine; keep agent bodies 40-80 lines with knowledge in skills |

Folding into shared skills means OpenCode's agents get the same sharpening, since
they preload the same files.

### Command routing after the change

```
/code-review, /security, /agent-review, /frontend-audit, /frontend-critique
    agent: <name> + context: fork      read-only enforced by tools:

/frontend, /frontend-polish, /debugger, /docs, /commit, /ship, /release
    agent: <name>                      capability: MCP, memory, model pin

/backend-engineer, /database-specialist, /test, /agent-builder
    context: fork, no agent:           isolation without a roster entry

/spec, /grill, /architecture, /ticket, /wayfinder, /prototype, /zoom-out
    inline, load the skill directly
```

The second group changes too: those seven name their agent in prose today. Moving
them to frontmatter removes the indirection and is free, since the agents survive.

Only five commands reference a removed agent: `/agent-builder`,
`/backend-engineer`, `/database-specialist`, `/prototype`, `/test`. The five
architect commands say "Operate as the architect" and need no change.

`backend-engineer.md` and `database-specialist.md` reference each other ("defer to
`@database-specialist` for that portion"). With both agents gone that handoff
becomes a skill-loading instruction.

### Relocation

`agents/` moves to `platforms/claude/agents/`, matching the move commands made in
`3e6c991`. Touches `scripts/links.py:38`, `validate-config.py:154`
(`CORE / "agents"` becomes `CLAUDE / "agents"`) and its comment at line 37, the
tree block in `AGENTS.md`, and the submodule tables in the dotfiles `CLAUDE.md`
and `README.md`.

## Testing

No test suite — correctness is proven by the validators and the live link chain.

- `scripts/validate-config.py` passes all checks. `check_index` fails on any agent
  named in an index but missing on disk, which catches stragglers in index
  documents.
- `make check` from dotfiles passes: every link resolves, then the suite validator.
- `ls -l ~/.claude/agents` resolves through both hops and lists 8 files.
- Re-measure description and roster prose to confirm the saving.

## Risks & Open Questions

- **Risk — content loss during folding.** Nine lines is small enough to drop by
  accident. Fold first, delete second, never the reverse.
- **Risk — `agent-authoring` double-write.** It is a real directory on both the
  canonical and OpenCode sides. Editing one copy leaves the other stale and the
  validator does not compare them.
- **Risk — role language inside shared skills.** `check_index` covers index
  documents only. The sweep found `backend-patterns` and `database-patterns`
  each carry an ownership-split table and a Collaboration section built on the
  two agent names (~10 lines each), and `frontend-patterns:16` escalates to
  `@architect`. OpenCode keeps those agents, so the names cannot simply be
  deleted from shared text. Decision: recast the split as domain boundaries —
  "backend work" vs "database work", hand-offs phrased as skill-loading — one
  neutral text serving both platforms. `@architect` escalation becomes `/spec`.
- **Resolved — the observability line splits.** Health checks are a Dockerfile
  and compose concern and stay in `docker-best-practices`; structured logging
  and metrics endpoints are application code and land in `backend-patterns` as
  service operability defaults. `ci-pipeline` gets nothing — none of the three
  are pipeline stages.

## Task Checklist

### Fold the residue first

- [ ] Add 3 lines to `skills/backend-patterns/SKILL.md`: auth/validation/integration as first-class; match existing error, serialization, logging and DI patterns; surface ambiguous contracts, authz rules and side effects before encoding
- [ ] Add 1 line to `skills/database-patterns/SKILL.md`: prefer explicit constraints and transaction boundaries over application-only assumptions
- [ ] Add 1 line to `skills/test-strategy/SKILL.md`: clarify expected behavior before cementing it in tests
- [ ] Add 2 lines to `skills/docker-best-practices/SKILL.md`: minimal images, least privilege, no baked secrets; health checks
- [ ] Add 1 line to `skills/backend-patterns/SKILL.md`: structured logging and metrics endpoints as service operability defaults
- [ ] Add 2 lines to **both** `skills/agent-authoring/SKILL.md` and `platforms/opencode/skills/agent-authoring/SKILL.md`: least privilege via `tools:`; agent bodies 40-80 lines with knowledge in skills
- [ ] Verify each new line greps in its destination, and that each residue line greps in **both** `agent-authoring` copies — the two are parallel platform-specific documents (343 vs 327 lines), so a whole-file match is not the test

### Rewrite the commands

- [ ] `/backend-engineer`, `/database-specialist`, `/test`, `/agent-builder` — replace `Use the @X subagent to...` with a direct instruction that loads the skills the agent used to preload (`backend-patterns`, `database-patterns`, or `test-strategy` plus `coding-guardrails`; `agent-authoring` plus `skill-design`), add `context: fork`, keep `disable-model-invocation: true`. Commands have no `skills:` key, so the body instruction is the only preload mechanism
- [ ] `/prototype` — drop `@backend-engineer`, keep `@frontend-engineer`, stay inline
- [ ] Rewrite the `@backend-engineer` / `@database-specialist` mutual handoff as a skill-loading instruction in both command bodies
- [ ] Move the seven prose-routed survivors to frontmatter `agent:` — `/frontend`, `/frontend-polish`, `/debugger`, `/docs`, `/commit`, `/ship`, `/release`

### Delete and relocate

- [ ] `git rm` the six: `agent-builder`, `architect`, `backend-engineer`, `database-specialist`, `devops-engineer`, `tester`
- [ ] `git mv agents platforms/claude/agents`
- [ ] Update `scripts/links.py:38` to `platforms/claude/agents`, `validate-config.py:154` to `CLAUDE / "agents"`, and the comment at line 37

### Documentation

- [ ] `platforms/claude/CLAUDE.md` — rewrite the routing model, don't just delete rows. Replace *When to Delegate* with a short *Routing* section built on the capability rule: agents for capabilities, skills for knowledge, `context: fork` for isolation. Shrink the *Agents* table to the 8 survivors, fix lines 9 and 16 (`@architect` guidance), line 155 (backend/database routing), the Agent column in the Commands table, and rephrase workflow rows that read as delegation chains
- [ ] `platforms/claude/CLAUDE.md` — drop the *Primary users* column from the skills table. Its entries are plain text `check_index` cannot see, and after the collapse most would name dead agents; the survivors' `skills:` frontmatter is the source of truth
- [ ] `AGENTS.md` — update the tree block and state the capability rule for what earns an agent
- [ ] Write `docs/adr/0001-agents-earn-their-slot-by-capability.md`: the rule, the trade-off (delegation ergonomics vs ~740 tokens of every-turn tax), and why OpenCode keeps its 15 (independent roster, structural `agent:` routing, no shared files)
- [ ] dotfiles `CLAUDE.md` and `README.md` — repoint `claude/.claude/agents` in the submodule table
- [ ] Recast the role language in shared skills as domain boundaries: the ownership tables and Collaboration sections in `skills/backend-patterns/SKILL.md` (lines 10, 16-22, 134-136) and `skills/database-patterns/SKILL.md` (lines 10, 16-21, 133-135) speak of backend work vs database work and skill-loading, not agent names; `skills/frontend-patterns/SKILL.md:16` escalates to `/spec`, not `@architect`
- [ ] Re-run the sweep for `@`-references to the six across skills and surviving agents to confirm nothing else surfaced

### Verify

- [ ] `scripts/validate-config.py` clean
- [ ] `make check` clean from dotfiles; `ls -l ~/.claude/agents` resolves and shows 8
- [ ] Re-measure the description tax and confirm roughly 740 tokens per turn recovered
