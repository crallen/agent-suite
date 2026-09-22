---
name: database-patterns
description: House rules for database work — expand/migrate/contract migrations, the constraint-per-need table, transaction boundaries chosen by invariant, and evidence-based indexing. Load for schema design, migrations, indexes, query tuning, transaction boundaries, and ORM code where database behavior is the real concern.
---

# Database Patterns

Load with `coding-guardrails` for schema design, migrations, indexes, query
tuning, transaction boundaries, integrity rules, and ORM or query-builder work
where database behavior is the primary concern.

| Concern | Skill |
|---|---|
| Tables, constraints, migrations, indexes, query plans, transactions, isolation, locks | this skill |
| Controllers, services, auth flows, API contracts | `backend-patterns` |

## Constraints

Constraints capture invariants the application must not be trusted to protect
alone; they are the final line of defense, and ORM validations do not replace them.

| Need | Prefer |
|---|---|
| Row identity | Primary key |
| Prevent duplicate business key | Unique constraint or index |
| Referential integrity | Foreign key, with deletion behavior chosen on purpose |
| Valid value range or enum-like rule | Check constraint when practical |
| Derived or cross-table invariant | Database constraint if possible; otherwise explicit app logic plus compensating checks |

Nullability and defaults are decisions, not conveniences. Accidental cascades are
production incidents, so every delete rule is explicit. Timestamps, soft deletes,
and tenant scoping follow the project's existing convention.

## Migrations: Expand, Migrate, Contract

1. **Expand** - add nullable columns, tables, or dual-write paths without
   breaking current code.
2. **Migrate** - backfill and move reads and writes gradually. Backfills are
   restartable and batched outside hot-path transactions.
3. **Contract** - remove old columns or constraints only after no caller depends
   on them.

Each migration is small enough to reason about and roll forward. Schema changes
and data backfills are separate when risk or runtime is significant, blocking
operations stay out of peak windows, and irreversibility is stated when a down
migration is not realistic.

## Indexes

An index exists because a query pattern in the code or the requirements needs it,
not from intuition. Design for the actual predicates, join paths, and sort order;
weigh write amplification against the table's update rate; measure the plan
before and after rather than guessing.

## Transactions

A transaction spans exactly the statements that must succeed or fail together,
and no longer. Choose the boundary by invariant:

| Situation | Guidance |
|---|---|
| Single-row write with no cross-row invariant | Often no explicit multi-step transaction needed |
| Multi-statement invariant | One transaction around the full invariant |
| External side effect plus DB write | Outbox or event pattern, or carefully ordered compensation; never a network call inside the transaction |
| Long backfill | Batch outside hot-path transactions |

Isolation level is explicit when it matters; lock behavior is understood before
adding `FOR UPDATE`, bulk updates, or cross-table write sequences; retry on
deadlock or serialization failure is designed, not accidental. Read the generated
SQL when an ORM hides the transaction, lock, or index behavior, and drop to raw SQL
when the abstraction obscures it.

Pair with `backend-patterns` when schema or constraint work needs endpoint or
service changes, dual-write migrations need app coordination, query behavior
affects handler-level pagination or authorization, or integrity errors need
user-facing mapping.
