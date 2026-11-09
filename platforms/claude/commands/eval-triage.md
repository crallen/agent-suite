---
description: Turn an eval findings file into a fix brief — one section per suite target to apply with /agent-builder, plus hand-applied eval-case changes
argument-hint: [findings file]
context: fork
disable-model-invocation: true
---

Load the `skill-design` and `agent-authoring` skills, then diagnose the eval failures in the findings file below and write a fix brief. This runs in a fork with no conversation history: the findings file and the suite files it names are the whole record. Write only the brief; the fixes are applied later, a section at a time.

Suite root, against which every path in the findings resolves:
!`dirname "$(readlink -f ~/.claude/skills)" 2>/dev/null || echo "(not found: ~/.claude/skills is not linked to the suite)"`

## Read

If the findings file is missing, unreadable, or not the runner's JSON, stop and print the command that produces one, run from the suite root: `scripts/run-evals.py --base main --findings evals/triage/findings.json`. If its `cases` is empty, report that there is nothing to fix and write no brief.

Read the findings one case at a time, never the whole file at once (for example `jq '.cases | length'`, then `jq '.cases[N]'`). For each case, read its `case_file` and every target file it names: for routing cases each name in `targets` and each suite name in failing runs' `evidence.routes` (what loaded instead often holds the description to fix; an `expect: none` case has no targets, so what loaded is its target), at `skills/<name>/SKILL.md`, `platforms/claude/agents/<name>.md`, or `platforms/claude/commands/<name>.md`; for behavior cases the command its `prompt` invokes and the skills that command loads. For a REGRESSION, also read `git diff <base sha> -- <file>` for each of those files: the change that broke it is there. A case whose case file or target file no longer exists went stale when the suite changed; it goes to Not actionable, never to a guess.

Diagnose from the quoted evidence: what loaded instead, which assertion failed, what the final text said. A case is Not actionable when it is INCONCLUSIVE, when most of its runs are errors, or when a failing run routed to a plugin's skill or agent (a route containing a colon, such as `frontend-design:frontend-design`) rather than to anything in the suite. A plugin merely listed in a run's `plugins` is not contamination on its own.

## Overfitting guard

- A change to a description names the class of request it widens to, and never copies the eval prompt's wording into the description.
- A description change verifies with `--only 'routing/*'`, since routes shift between neighboring skills. A section-local glob verifies only a behavior change.
- Blame the eval only with at least 2 quoted failing replies and an argument that they meet the intent of the case: the comment beside it, or the spec row it encodes. Without that, the fix belongs to the suite.

## Write the brief

Write `<suite root>/evals/triage/<YYYY-MM-DD>-brief.md`, dated today. Each suite section is self-contained, since `/agent-builder` applies one at a time with nothing else in view: quote the old text it replaces. Group every case a target fails under that target's one section.

```markdown
# Eval triage — <date>, base <sha> vs head <sha>

## Suite changes (apply with /agent-builder, one section at a time)
### 1. <target> (<skill|agent|command>) — <file path>
- Cases: <id> (base x/y, head x/y), …
- Evidence: what loaded instead, or which assertion failed, quoted from runs
- Diagnosis: why the artifact produces this behavior
- Change: the concrete edit, with the old text it replaces
- Generalization: the class of request this widens to, beyond the eval prompt
- Verify: `scripts/run-evals.py --only '<glob>' --runs 5`, expecting <status>

## Eval case changes (apply by hand)
### E1. <case id> — <case file>
- Failing replies: at least 2, quoted
- Case intent: the spec row or comment the case encodes
- Change: the assertion or prompt edit
- Why the replies meet the intent

## Not actionable
- <case id>: INCONCLUSIVE, error-dominated, plugin-contaminated, or its file is gone; `scripts/run-evals.py --only '<id>' --runs 5`

## Apply order
Section numbers in order, sections touching the same file grouped.
```

Every case in the findings lands in exactly one section. End by printing the brief's path and the count of entries in each section.

$ARGUMENTS
