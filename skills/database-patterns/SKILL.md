---
name: database-patterns
description: House rules for database work — expand/migrate/contract migrations, the constraint-per-need table, transaction boundaries chosen by invariant, and evidence-based indexing. Load for schema design, migrations, indexes, query tuning, transaction boundaries, and ORM code where database behavior is the real concern.
---

# Database Patterns

## Constraints

Constraints capture invariants the application must not be trusted to protect
alone; they are the final line of defense, and ORM validations do not replace them.

| Need | Prefer |
|---|---|
| Referential integrity | Foreign key, with deletion behavior chosen on purpose |
| Valid value range or enum-like rule | Check constraint when practical |
| Derived or cross-table invariant | Database constraint if possible; otherwise explicit app logic plus compensating checks |

Nullability and defaults are decisions, not conveniences. Accidental cascades are
production incidents, so every delete rule is explicit.

## Migrations

When old and new code run against one schema (several instances, rolling
deploys), stage a breaking change as expand, migrate, contract: add the new shape
without breaking current code, move reads, writes, and data across, and remove
the old shape only after no caller depends on it.

Backfills are restartable and batched outside hot-path transactions. Schema
changes and data backfills are separate when risk or runtime is significant, and
irreversibility is stated when a down migration is not realistic.

## Indexes

An index exists because a query pattern in the code or the requirements needs it,
not from intuition. Design for the actual predicates, join paths, and sort order;
weigh write amplification against the table's update rate; measure the plan
before and after rather than guessing.

## Transactions

A transaction spans exactly the statements that must succeed or fail together,
and no longer. Never make a network call inside one: an external side effect
plus a database write takes an outbox or event pattern, or carefully ordered
compensation.

Isolation level is explicit when it matters; lock behavior is understood before
adding `FOR UPDATE`, bulk updates, or cross-table write sequences; retry on
deadlock or serialization failure is designed, not accidental. Read the generated
SQL when an ORM hides the transaction, lock, or index behavior, and drop to raw SQL
when the abstraction obscures it.

Pair with `backend-patterns` when schema or constraint work needs endpoint or
service changes, dual-write migrations need app coordination, query behavior
affects handler-level pagination or authorization, or integrity errors need
user-facing mapping.
