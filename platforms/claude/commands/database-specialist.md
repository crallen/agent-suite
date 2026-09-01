---
description: Design or modify database schemas, migrations, queries, and indexes
argument-hint: [request]
disable-model-invocation: true
---

Use the `@database-specialist` subagent to handle the database-heavy portion of the following request. Focus on schema design, migrations, constraints, indexes, transaction boundaries, query tuning, and ORM or query-builder work where database behavior is the real concern.

If the request is ambiguous, cross-cutting, or really needs design before implementation, say so plainly and recommend `/spec` before changing the schema or queries.

$ARGUMENTS
