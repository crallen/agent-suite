---
description: Run tests, analyze results, and suggest improvements
argument-hint: [scope (optional)]
context: fork
disable-model-invocation: true
---

Load the `test-strategy` and `coding-guardrails` skills, then run the project's test suite and analyze the results. If tests fail, investigate the failures and suggest fixes. If coverage data is available, identify areas with low coverage.

This runs in a fork with no conversation history. Work from the scope below; if it leans on context that is not here, stop and report what is missing rather than guessing.

$ARGUMENTS
