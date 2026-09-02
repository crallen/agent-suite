---
name: backend-patterns
description: Backend application patterns for handlers, services, validation, auth/authz, integrations, and app-layer refactors
---

# Backend Patterns

Load this skill for backend and application-layer implementation work: handlers, controllers, services, validation, authentication, authorization, external integrations, and request-flow refactors. Use it alongside `coding-guardrails`.

When schema, SQL, migrations, indexes, transaction design, or database-heavy ORM behavior are central to the task, load `database-patterns` alongside this skill rather than treating the database as an implementation detail.

## Scope Boundaries

| Concern | Guidance lives in |
|---|---|
| HTTP handlers, controllers, routes, RPC methods | this skill |
| Service-layer business logic | this skill |
| Validation, auth, authz, request orchestration | this skill |
| External API and queue integrations | this skill |
| Schema design, migrations, constraints, indexes | `database-patterns` |
| Query plans, transaction boundaries, lock behavior | `database-patterns` |
| ORM/query-builder code where SQL behavior is the real risk | `database-patterns` |

## Request Flow Design

Prefer a predictable request path:

1. **Transport boundary** - Parse request, authenticate caller, validate shape, map transport concerns.
2. **Authorization** - Decide whether the caller may perform the action.
3. **Service layer** - Execute business rules and orchestration.
4. **Persistence/integration** - Call repositories, queues, or third-party systems.
5. **Response mapping** - Convert domain result into transport response and errors.

### Dependency direction

Dependencies point inward. Transport depends on the service layer; the service layer depends only on interfaces it owns. When a service needs the outside world, it declares the shape it needs and an outer layer supplies it — `Avoid in services` below lists the concrete cases.

Keep the import graph acyclic. A cycle between modules means the seam sits in the wrong place; extract the shared concept into its own module instead of importing both ways.

## Handler and Controller Rules

- Keep handlers thin. They should coordinate, not own deep business logic.
- Normalize input once near the boundary.
- Return consistent status codes or error envelopes.
- Inject dependencies explicitly at new seams rather than reaching for hidden globals. Match the surrounding pattern when editing code that already relies on them.
- Preserve idempotency for retried writes when the API contract expects it.

### Handler Checklist

- [ ] Request parsing is narrow and explicit
- [ ] Validation happens before business logic
- [ ] Authentication and authorization are separate decisions
- [ ] Business logic lives outside the handler when reused or non-trivial
- [ ] Errors are mapped consistently
- [ ] Logging includes useful request or actor context without leaking secrets

## Service-Layer Guidance

Services own application rules and orchestration.

### Good service responsibilities

- Enforce domain invariants that span multiple inputs
- Coordinate repository calls and external integrations
- Decide side-effect ordering
- Produce domain-level errors or result objects

### Avoid in services

- HTTP request or response objects
- Framework-specific transport details
- Raw SQL design decisions that need database review
- UI-oriented formatting or presentation concerns

## Validation

Validate at the boundary closest to untrusted input.

| Validation type | Where it belongs |
|---|---|
| Shape/type parsing | Request boundary |
| Required fields and format | Request boundary |
| Cross-field business rules | Service layer |
| Database-backed uniqueness or referential guarantees | Database constraints first, app checks second |

Rules:

- Reject malformed input early.
- Keep validation messages consistent with project norms.
- Do not rely on application checks alone for invariants that the database can enforce.

## Authentication and Authorization

Separate identity from permission.

- **Authentication** answers: who is the caller?
- **Authorization** answers: may this caller do this action on this resource?

### Auth/Authz checklist

- [ ] Unauthenticated and unauthorized cases are handled separately
- [ ] Resource ownership or tenant boundaries are explicit
- [ ] Security-sensitive defaults fail closed
- [ ] Audit or security logs follow existing conventions
- [ ] Secrets and tokens are never logged

## Integration Boundaries

When calling external systems:

- Set explicit timeouts.
- Decide retry behavior intentionally; do not blindly retry non-idempotent writes.
- Map external errors into local error semantics.
- Preserve correlation IDs or trace context if the system uses them.
- Keep provider-specific payload mapping at the edge of the integration.

### Integration review checklist

- [ ] Timeout behavior is explicit
- [ ] Retry policy matches idempotency reality
- [ ] External responses are validated before use
- [ ] Partial failure behavior is defined
- [ ] Side effects are ordered intentionally

## Refactoring the App Layer

Refactor only when it improves the requested change.

- Extract a service when logic is duplicated, deeply nested, or impossible to test at the current boundary.
- Keep module moves local; avoid repo-wide renames unless the request demands them.
- Preserve public contracts unless the task includes coordinated caller updates.
- Pair structural changes with behavior checks.

## When Database Behavior Takes Over

Load `database-patterns` when any of the following are true:

- A migration is required
- The change depends on new constraints or indexes
- Query performance or execution plans matter
- Transaction boundaries or lock behavior could change correctness
- ORM or query-builder code needs SQL-aware reasoning
- Data backfills, online migration safety, or rollback plans matter

## Execution Defaults

- Treat auth, validation, and integration boundaries as first-class concerns, not afterthoughts.
- Match existing error handling, serialization, logging, and dependency wiring patterns.
- Surface ambiguous API contracts, authorization rules, or side effects before encoding them.
- Emit structured logs and expose a metrics endpoint as service defaults, not follow-up work.

## Anti-Patterns

- Fat handlers that mix transport, business rules, and persistence details
- Authorization checks hidden deep inside unrelated helpers
- Validation scattered across multiple layers without a clear boundary
- App-only enforcement of invariants that belong in database constraints
- Integration code without timeouts, retries, or failure semantics
