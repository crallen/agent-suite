---
description: Research a question against primary sources in a background agent and save cited findings as a Markdown file
argument-hint: [question to research]
disable-model-invocation: true
---
Launch a background subagent to research the question below, and keep working while it reads. Brief it to:

1. Investigate against primary sources: official docs, source code, specs, first-party APIs. Follow every claim back to the source that owns it; a secondary write-up is a lead, not a source.
2. Write the findings to one Markdown file, each claim cited, with anything it could not confirm marked as unconfirmed.
3. Save the file where this repo already keeps such notes, or under `docs/research/` when there is no convention, and report the path.

Existing notes directories:
!`for d in docs/research docs/notes research notes; do [ -d "$d" ] && echo "$d"; done | grep . || echo "(none yet)"`

$ARGUMENTS
