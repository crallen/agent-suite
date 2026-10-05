---
description: Implement or modify backend application code
argument-hint: [request]
context: fork
disable-model-invocation: true
---

Load the `backend-patterns` and `coding-guardrails` skills, then implement or modify backend application code for the following request. This includes API handlers, controllers, services, validation, auth/authz, integrations, and app-layer refactors. If the real work turns out to be schema, SQL, migrations, indexes, transaction behavior, or database-heavy ORM/query-builder behavior, load `database-patterns` for that portion.

If the request is ambiguous, cross-cutting, or really needs design before implementation, say so plainly and recommend `/spec` before coding.

This runs in a fork with no conversation history. Work from the request below and any spec or findings path it names; if it leans on context that is not here, stop and report what is missing rather than guessing.

$ARGUMENTS
