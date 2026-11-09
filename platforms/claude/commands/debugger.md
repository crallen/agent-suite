---
description: Start a systematic debugging session for a described issue
argument-hint: [issue description]
context: fork
disable-model-invocation: true
---

Load the `debugging-methodology` and `coding-guardrails` skills, then investigate the following issue. Build the Phase 0 feedback loop before forming any theory, then follow the remaining phases in order. Report the root cause and the fix or, if the cause stays out of reach, what was ruled out and what remains.

This runs in a fork with no conversation history. Work from the issue below and any paths it names; if it leans on context that is not here, stop and report what is missing rather than guessing.

$ARGUMENTS
