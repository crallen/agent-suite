# Agent suite

Agents, skills, and commands shared across Claude Code, OpenCode, and Codex, and the
evals that show they shape behavior.

## Language

### Artifacts

**Preload**:
A skill injected whole into an agent's context at start through its `skills:`
frontmatter. Not a capability on its own: it is how an agent whose tool list lacks
the Skill tool gets its method and report format.
_Avoid_: bundled skill

**Implementer brief**:
The prompt `spec-implementation` gives each implementer subagent: spec path, task
number, and the skills to load. The path most implementation-skill loads arrive by.
_Avoid_: task prompt

### Evals

**Style case**:
A behavior case asserting that one house-style rule shows in the output.

**Freedom case**:
A behavior case asserting the suite leaves the model's judgment intact: no ceremony
on trivial work, clear tasks finished, a question only when a request is genuinely
ambiguous.
_Avoid_: negative case

**Red proof**:
A run with a case's guarded rule removed, or a constraining rule added, showing the
case's assertions can fail. It proves the case can catch something, not that the
rule is needed.
_Avoid_: ablation

**Ablation**:
Five runs of a style case with every copy of one rule removed from everything the
run loads, testing whether the model follows the rule unprompted. Only five green
runs out of five make the rule a cut candidate.
_Avoid_: red proof

### Rule classes

**Rule list**:
The per-skill table that classifies every rule, cites its evidence, and records the
owner-approved decision before a cut.
_Avoid_: ledger

**House style**:
A rule stating the owner's preference that the model would not follow unprompted.

**Counter-correction**:
A rule that corrects a known model tendency, such as over-abstracting or widening a
diff.

**Textbook**:
A rule the model follows without being told, shown by ablation or judged so in the
rule list.
_Avoid_: common knowledge

**Restatement**:
A rule already stated in another file the same run loads: a skill, an agent body,
an index document, or the implementer brief.
_Avoid_: duplicate
