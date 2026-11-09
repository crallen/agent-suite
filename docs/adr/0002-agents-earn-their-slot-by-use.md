# Agents earn their slot by use

ADR 0001 kept any agent that carried a capability instructions cannot express. A
usage pass over session transcripts from 118 local projects (2026-11-09) found
three of those capabilities never exercised: `debugger` had no spawns and had
written memory in no project, `frontend-auditor` had no spawns and no run of
`/frontend-audit` or `/frontend-critique`, and `documenter` had 7 spawns, too few
for its `sonnet` pin to justify a separate route. We now hold Claude Code's roster
to this rule:

A preload is not a capability on its own. An agent keeps its slot only for a
harness-enforced capability that is exercised: tool limits, an MCP server, memory
that gets written, or a model pin worth routing work off the session model. Agents
with the same enforcement may stay separate when each is a natural-language
routing target with its own preloaded method, because an agent with restricted
tools has no Skill tool to load that method itself.

That removes `debugger`, `documenter`, and `frontend-auditor`, and keeps
`code-reviewer`, `security-analyst`, `agent-reviewer`, and `frontend-engineer`.
The first three share the same read-only tool list and stay separate under the
rule's last sentence. `/debugger` and `/docs` now fork on a general-purpose agent
that loads `debugging-methodology` or `doc-templates`. `/frontend-audit` and
`/frontend-critique` run on `frontend-engineer` and are read-only by instruction,
not by enforcement.

The evidence that would bring one back:

- `debugger`: failure modes that recur across debugging sessions in a project, so
  memory written by one investigation would be read by the next.
- `documenter`: documentation work frequent enough that routing it off the
  session model saves real cost.
- `frontend-auditor`: an audit or critique run that edits repository files
  despite its report-only instruction.
