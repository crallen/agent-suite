---
name: agent-authoring
description: Conventions, body templates, and the validation checklist for creating or modifying agents, skills, and slash commands, plus per-harness frontmatter and permission references. Load when adding or changing any of the three artifact types.
---

# Agent Authoring

Conventions for the three artifact types this suite ships, and the per-harness
schemas behind them. The harness-specific half is disclosed: read
`agent-authoring/reference/claude.md` when working on Claude Code artifacts and
`agent-authoring/reference/opencode.md` for OpenCode. Codex consumes skills only.

For the design of a skill's content (predictability, information hierarchy,
leading words, disclosure, failure modes) use `skill-design`; this skill covers
mechanics.

## The Three Artifacts

| Artifact | Lives at | Identifier | Reached by |
|---|---|---|---|
| Agent | the harness's agent directory, one file each | filename without `.md`, as `@name` | delegation, routing, or `@mention` |
| Skill | `skills/<name>/SKILL.md`, shared by every harness | directory name, matching `name:` | the harness's skill tool, or preloaded into an agent |
| Command | the harness's command directory, one file each | filename without `.md`, as `/name` | the user typing `/name` |

Skills are harness-neutral by rule: no tool names, invocation syntax, or machinery
specific to one harness. Anything that cannot be said neutrally belongs in a
platform's index or in this skill's references. Every skill carries `name:`
matching its directory, which is what lets one file serve all three harnesses.

Commands are platform-specific by nature. A command names its harness's agents and
uses its invocation syntax, so each platform keeps its own set. Commands are short
task prompts, not reference documents: most fit in 5–15 lines, and every command
that accepts input ends with `$ARGUMENTS`.

An agent earns its slot by a capability instructions cannot express: a tool
restriction the harness enforces, an MCP server, persistent memory, or a model pin.
A definition that only carries a persona and preloads a skill is a skill and a
command, not an agent.

## Agent Body

Keep the body to a concise workflow, roughly 30–60 lines. Detailed procedural
knowledge belongs in a skill the agent preloads or loads, not inline; the body is
read on every run.

```markdown
One sentence naming the agent's focus.

## How You Work

1. **Step one** - The first phase.
2. **Step two** - Name the skills that carry the method and what each provides.
3. **Step three** - The core work.
4. **Step four** - Verification, output, or handoff.

## Output Format (analysis agents only)

The report shape, or a pointer to the skill that owns it.

## Guidelines

- Standing rules that no step above and no loaded skill already states.
```

A Guidelines bullet that restates a step or a skill's rule is duplication, not
emphasis. A read-only agent's body states the restraint in words as well, because
a shell can still write files.

## Skill Body

Skills are reference documents, not personas. Open with a single H1 and a one- or
two-sentence intro that says what the skill covers and when to load it, then
headed sections of rules, tables, and examples. State the target behavior rather
than a list of prohibitions.

Keep `SKILL.md` lean, since an agent that preloads it pays for every line on
every run. When the domain is too large for one file, `SKILL.md` becomes a router
and the depth moves to `reference/*.md` files loaded on demand:

```
skills/<name>/
├── SKILL.md         # trigger, non-obvious rules, and a map of the references
└── reference/
    └── topic.md
```

Pointers to a reference use the form `<skill>/reference/<file>.md`; the validator
checks they resolve.

Never leave a shell-injection token bare at the start of a line in a skill or
agent file. It belongs inside inline code, as in the command references, or the
harness will run it whenever the file loads. The validator checks this too.

## Cross-Cutting Skills

- `coding-guardrails` for any agent that writes, refactors, fixes, or reviews
  code or configuration.
- `spec-writing` for design-first planning.

Wire them in through the harness's preload mechanism rather than a runtime
instruction, so they are present even for agents whose tool set excludes the
skill tool.

## Validation Checklist

`scripts/validate-config.py` enforces most of this; run it after any change.

- [ ] Filename matches identifier: agent filename = `@name` = `name:`; skill
      directory = `name:`; command filename = `/name`, with no `name:` key.
- [ ] Every frontmatter key is one the harness reads, and every tool name exists.
- [ ] Cross-references resolve: command → agent, agent → skill, skill →
      reference file.
- [ ] Colors follow the harness's rule and are unique across its roster.
- [ ] Read-only agents restrict writes through the harness's mechanism and say so
      in the body.
- [ ] Every skill an agent depends on is preloaded or loadable by that agent.
- [ ] Guidance is stated once: no Guidelines bullet repeats a step or a skill.
- [ ] A new or edited skill passes `skill-design`: the description names its
      triggers, depth is disclosed, and the body is free of the failure modes it
      catalogs.
- [ ] The platform's index document lists the new artifact where that harness
      needs it (see the references), and any README stays in sync.
