---
description: Implement or modify backend application code
argument-hint: [request]
disable-model-invocation: true
---

Use the `@backend-engineer` subagent to implement or modify backend application code for the following request. This includes API handlers, controllers, services, validation, auth/authz, integrations, and app-layer refactors; involve `@database-specialist` if the real work is schema, SQL, migrations, indexes, transaction behavior, or database-heavy ORM/query-builder behavior.

If the request is ambiguous, cross-cutting, or really needs design before implementation, say so plainly and recommend `/spec` before coding.

$ARGUMENTS
