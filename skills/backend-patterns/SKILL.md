---
name: backend-patterns
description: House rules for application-layer code — the request path, inward dependency direction, where each kind of validation lives, constraints before app checks, and structured logs plus a metrics endpoint as defaults. Load for handlers, services, validation, auth, integrations, and app-layer refactors; pair with database-patterns when SQL behavior is the real concern.
---

# Backend Patterns

Load with `coding-guardrails` for handlers, controllers, services, validation,
authentication, authorization, external integrations, and request-flow refactors.

| Concern | Skill |
|---|---|
| Handlers, services, validation, auth, integrations, app-layer refactors | this skill |
| Schema, migrations, constraints, indexes, query plans, transactions, locks, ORM code where SQL behavior is the risk | `database-patterns` |

## Request Path

1. **Transport boundary** - parse, authenticate, validate shape, map transport
   concerns.
2. **Authorization** - may this caller perform this action on this resource?
   A separate decision from authentication, and unauthenticated and unauthorized
   are handled separately.
3. **Service layer** - business rules and orchestration: invariants spanning
   inputs, side-effect ordering, domain-level errors or results.
4. **Persistence and integration** - repositories, queues, third parties.
5. **Response mapping** - domain result to transport response and error envelope.

Handlers coordinate; they do not own deep business logic. Input is normalized once
at the boundary.

## Dependency Direction

Dependencies point inward. Transport depends on the service layer; the service
layer depends only on interfaces it owns, and never sees HTTP objects, framework
transport details, raw SQL design, or presentation concerns. When a service needs
the outside world, it declares the shape it needs and an outer layer supplies it.
Keep the import graph acyclic: a cycle means the seam is in the wrong place, so
extract the shared concept into its own module.

Inject dependencies explicitly at new seams. When editing code that already relies
on hidden globals, match the surrounding pattern rather than half-converting it.

## Validation

| Validation type | Where it belongs |
|---|---|
| Shape, type, required fields, format | Request boundary |
| Cross-field business rules | Service layer |
| Uniqueness and referential guarantees | Database constraints first, app checks second |

Do not rely on application checks alone for invariants the database can enforce.

## Integrations

Explicit timeouts; a retry policy that matches the idempotency of the call, never
a blind retry of a non-idempotent write; external responses validated before use;
external errors mapped into local semantics; correlation or trace context
preserved where the system uses it; provider-specific payload mapping kept at the
edge.

## Defaults

- Structured logs and a metrics endpoint are service defaults, not follow-up work.
  Logs carry request or actor context and never secrets or tokens.
- Security-sensitive defaults fail closed.
- Match existing error handling, serialization, logging, and dependency wiring.
- Surface ambiguous API contracts, authorization rules, or side effects before
  encoding them.
- Refactor the app layer only when it improves the requested change: extract a
  service when logic is duplicated, deeply nested, or untestable at the current
  boundary; keep module moves local; preserve public contracts unless the task
  includes coordinated caller updates.
