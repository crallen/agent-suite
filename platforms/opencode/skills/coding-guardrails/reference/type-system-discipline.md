# Type System Discipline

The type checker is a proof assistant. Use it to eliminate impossible states, mismatched primitives, and unhandled variants at compile time. A case the types let you ignore becomes a runtime failure the compiler could have stopped. Prefer defining errors and special cases out of existence over proliferating handlers.

Applies to any statically-typed language. A stack skill (e.g. a `typescript-*` or `rust-*` patterns skill) grounds these in specific syntax.

## Patterns

- **Make illegal states unrepresentable.** Model variants as sum types — discriminated unions, enums with payloads, sealed classes, ADTs. Don't model state as a bag of optional fields where contradictory combinations compile. `{ completed: boolean; completedAt?: Date }` admits `completed: true, completedAt: undefined`, which is meaningless. Model the variants: `{ kind: 'open' } | { kind: 'done'; at: Date }`. If a bug forces the question "can this combination actually happen?", the type is too loose.
- **Types are constructions, not restrictions.** Build the type up from the values you want rather than carving them out of a looser type with checks. A non-empty list is a head plus a rest, not a list with a length check. A valid range is a start plus a duration, not two timestamps you must keep ordered. Choose the shape that cannot build the illegal value, then expose the interface callers need on top.
- **Brand semantic primitives.** `UserId` and `OrderId` are strings underneath but must not be interchangeable. Newtypes, opaque types, value classes, branded types — pick your language's tool. Validate once at creation, trust the type downstream.
- **External data is untyped until parsed.** RPC payloads, JSON, IPC messages, CLI args, config files, env vars, database rows. Put a parse function at every boundary that turns unstructured input into the typed model. `backend-patterns` covers where validation lives.
- **Don't lie to the type system.** Casts, unsafe coercions, and assertion functions that bypass the compiler are runtime crashes waiting to happen. If the compiler can't prove a fact, prove it — validate, narrow, refine the model — or accept the cast is a hazard. The cast you bury today is the postmortem you write next week.
- **Exhaustive matching is the compiler's job.** When you match on a sum type, adding a new variant without handling it must fail compilation. Use the idiom your language provides (a `never`-typed fallthrough, an unannotated `match`, an incomplete-pattern warning promoted to error).
- **Derive types from authoritative schemas.** When a protobuf, OpenAPI spec, GraphQL schema, migration, or token file defines a shape, derive from it instead of hand-rolling a parallel type that drifts. See `coding-guardrails/reference/encode-lessons-in-structure.md`.
- **Strengthen a type only where partiality appears.** A runtime assertion or "this should never happen" throw marks a type that is too weak — push that check up into the type, then stop. Prefer total functions: `sum` of an empty list is 0 so it takes the plain list; `head` of an empty list has no answer so it demands the non-empty one. Precision beyond what keeps functions total costs reuse and buys no safety.

## Tests

- "Can I write a comment explaining when this combination of fields is valid?" If yes, split it into a sum type.
- "Do two arguments share a primitive type but mean different things?" Brand them.
- "Where did this cast / `any` / `assertNotNull` come from?" Trace it to the boundary and validate there.
- "If a new variant is added next month, will the compiler point the next reader at every site to update?" If no, the match isn't exhaustive.
- "Is this type duplicating a shape another file owns?" Derive instead.
- "Am I strengthening this type to keep a function total, or just to be more precise?" If nothing would otherwise fail, keep the plain type.
