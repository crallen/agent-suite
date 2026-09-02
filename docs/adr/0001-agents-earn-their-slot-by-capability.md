# Agents earn their slot by capability, not by topic

Claude Code's roster had grown to 14 agents, most of which carried only a persona
and a `skills:` preload. Every one of them costs its `description` in context on
every turn whether or not it is used — roughly 740 tokens per turn across the
descriptions and the roster prose in the index. We cut the roster to 8, keeping
only agents that express something instructions cannot: tool restrictions the
harness enforces (`code-reviewer`, `security-analyst`, `agent-reviewer`,
`frontend-auditor`), an inline MCP server (`frontend-engineer`), persistent
project-local memory (`debugger`), or a model pin (`documenter`, `git-manager`).
The guidance the removed agents carried was folded into the skills they preloaded
first, so nothing was lost; their commands now load those skills directly and run
with `context: fork` where isolation was the real benefit.

The trade-off is ergonomic. `@backend-engineer` was a nice thing to type, and
`/backend-engineer` forking with `backend-patterns` loaded is a slightly longer
road to the same place. We took it because a per-topic agent buys nothing the
harness enforces: its persona is prose, and prose is what a skill already is.

OpenCode keeps all 15 of its agents. Its roster is a separate set of real files
that has never shared anything with Claude's, and it routes every command
structurally with `agent:` plus `subtask: true` — which makes a per-topic agent
the unit routing acts on rather than dead weight. The rule is Claude's alone.
