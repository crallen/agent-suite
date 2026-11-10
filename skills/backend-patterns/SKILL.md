---
name: backend-patterns
description: House rules for application-layer code — authentication apart from authorization, an acyclic import graph, where each kind of validation lives, retries matched to idempotency, and structured logs plus a metrics endpoint as defaults. Load for handlers, services, validation, auth, integrations, and app-layer refactors; pair with database-patterns when SQL behavior is the real concern.
---

# Backend Patterns

## Boundaries

Authentication and authorization are separate decisions, and unauthenticated and
unauthorized are handled separately. Input is normalized once at the boundary.

Keep the import graph acyclic: a cycle means the seam is in the wrong place, so
extract the shared concept into its own module. Inject dependencies explicitly at
new seams. When editing code that already relies on hidden globals, match the
surrounding pattern rather than half-converting it.

## Validation

| Validation type | Where it belongs |
|---|---|
| Shape, type, required fields, format | Request boundary |
| Cross-field business rules | Service layer |
| Uniqueness and referential guarantees | Database constraints first, app checks second |

## Integrations

A retry policy that matches the idempotency of the call, never a blind retry of a
non-idempotent write; external responses validated before use; external errors
mapped into local semantics; correlation or trace context preserved where the
system uses it; provider-specific payload mapping kept at the edge.

## Defaults

- Structured logs and a metrics endpoint are service defaults, not follow-up work.
  Logs carry request or actor context and never secrets or tokens.
- Security-sensitive defaults fail closed.
