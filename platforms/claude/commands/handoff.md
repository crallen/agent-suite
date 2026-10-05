---
description: Compact this conversation into a handoff document a fresh session can pick up
argument-hint: [what the next session will focus on (optional)]
disable-model-invocation: true
---
Write a handoff document that lets a fresh agent continue this work, and save it to the system temp directory, outside the workspace. Report the path.

Cover the goal, the current state, the decisions made and why, and the next step. Point at anything already captured elsewhere (specs, ADRs, issues, commits, diffs) by path or URL rather than copying it. Add a "Suggested skills" section naming the skills the next agent should load. Replace every secret and personal identifier with `<REDACTED>`.

If a focus is given below, tailor the document to it.

Current repository state:
!`git status --short --branch 2>/dev/null || echo "(not a git repository)"`

$ARGUMENTS
