---
description: Turn a spec, requirements, or the current conversation into paste-ready JIRA/Linear tickets
argument-hint: [spec file, requirements, or feature description]
disable-model-invocation: true
---

Draft tracker tickets from the material below. Use the Skill tool to load `ticket-writing` for the splitting workflow, templates, and acceptance-criteria rules. Identify the source first: the argument if one is given, otherwise the most recent spec under `docs/specs/`, otherwise the conversation so far. When the source yields more than one ticket, present the proposed split — titles plus a one-line outcome each — for confirmation before drafting. Then produce each ticket as a paste-ready block.

Recent specs:
!`ls -t docs/specs/*.md 2>/dev/null | head -5 || echo "(no docs/specs directory)"`

$ARGUMENTS
