---
description: Guidelines for choosing test types, setting coverage targets, mocking strategies, and structuring test suites effectively
---

# Test Strategy

Use this skill when deciding how correctness will be proven. Tests are not just coverage artifacts — they are the primary way to turn vague requests into verifiable outcomes.

## Goal-Driven Verification Loops

- **Bug fixes** - Prefer a failing regression test or another repeatable reproduction before implementing the fix.
- **New features** - Decide up front which unit, integration, end-to-end, or manual checks will prove success.
- **Refactors** - Establish a behavior baseline before changing structure, then confirm the same behavior afterward.
- **Multi-step work** - Pair each implementation step with a `verify:` check so progress is observable.
- **Avoid speculative matrices** - Do not add large suites for hypothetical future behaviors that the code does not implement.

## TDD Workflow: Vertical Slices via Tracer Bullets

When building a feature test-first, use **vertical slices** — one test, one implementation, repeat. This is the correct approach.

**Do NOT write all tests first, then all implementation.** This is "horizontal slicing" and produces bad tests: they test imagined behavior rather than actual behavior, couple to shape rather than outcomes, and become insensitive to real changes.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED → GREEN: test1 → impl1
  RED → GREEN: test2 → impl2
  RED → GREEN: test3 → impl3
  ...
```

Each test responds to what you learned from the previous cycle. Because you just wrote the code, you know exactly what behavior matters and how to verify it.

### Planning Step

Before writing any test or code:
- Confirm with the user what interface changes are needed
- Confirm which behaviors to test (you can't test everything — prioritize critical paths)
- List the behaviors to test (not implementation steps) and get user approval
- Use the project's domain vocabulary (from `CONTEXT.md` if present) so test names match the project's language

### Tracer Bullet

Write ONE test that confirms ONE thing about the system:

```
RED:   Write test for first behavior → test fails
GREEN: Write minimal code to pass → test passes
```

This is your tracer bullet — proves the path works end-to-end.

### Incremental Loop

For each remaining behavior: one test → minimal code to pass. Never anticipate future tests. Keep tests focused on observable behavior.

### Refactor

After all tests pass, look for cleanup: extract duplication, deepen shallow modules, apply SOLID where natural. **Never refactor while RED.** Get to GREEN first.

### Checklist per Cycle

- [ ] Test describes behavior, not implementation
- [ ] Test uses public interface only
- [ ] Test would survive an internal refactor
- [ ] Code is minimal for this test
- [ ] No speculative features added

## Test Pyramid

Prioritize tests from bottom to top — more unit tests, fewer E2E tests:

```
        /  E2E  \          <- Few: slow, expensive, brittle
       /  Integ. \         <- Some: verify component interaction
      /   Unit    \        <- Many: fast, focused, reliable
```

### Unit Tests
- **What**: Individual functions, methods, or classes in isolation.
- **When**: Business logic, data transformations, utility functions, state machines, validation rules.
- **Speed**: Milliseconds per test.
- **Goal**: High coverage of logic branches.

### Integration Tests
- **What**: Multiple components working together through real interfaces.
- **When**: Database queries, API endpoint handlers, middleware chains, service-to-service communication.
- **Speed**: Seconds per test.
- **Goal**: Verify contracts between components.

### End-to-End Tests
- **What**: Full user workflows through the actual system.
- **When**: Critical user journeys (signup, checkout, deployment), smoke tests for production.
- **Speed**: 10+ seconds per test.
- **Goal**: Confidence that the complete system works. Cover only the critical paths.

## What to Test

### Always Test
- Business logic and domain rules
- Error handling and edge cases
- Input validation and boundary conditions
- State transitions and state machines
- Security-sensitive code paths (auth, authz, input sanitization)
- Data serialization/deserialization
- Public API contracts

### Usually Skip
- Trivial getters/setters with no logic
- Generated code (protobuf stubs, ORM models)
- Third-party library internals
- Private helper functions (test them through public interfaces)
- Pure configuration (test it through integration tests instead)

## Mocking Strategy

### When to Mock
- External HTTP services and APIs
- Databases (for unit tests; use real DB for integration tests)
- File system operations (when testing logic, not I/O)
- Time-dependent code (clocks, timers)
- Non-deterministic operations (random, UUIDs)

### When NOT to Mock
- Internal interfaces between your own modules (test the real thing)
- Simple data structures and value objects
- When the real implementation is fast and deterministic

### Mocking Rules
1. Mock at boundaries, not internals.
2. If you need more than 3 mocks for a single test, the code under test probably has too many dependencies — consider refactoring.
3. Verify mock interactions sparingly. Over-verifying mocks makes tests brittle.
4. Prefer fakes (in-memory implementations) over mocks when possible. They test more realistic behavior.

## Coverage Targets

| Category | Target | Rationale |
|---|---|---|
| Business logic | 80-90% branch coverage | This is where bugs cost the most |
| API handlers | 70-80% | Cover success, error, and auth cases |
| Utilities/helpers | 90%+ | Small, well-defined, easy to test |
| UI components | 60-70% | Focus on behavior, not rendering details |
| Infrastructure/config | 40-50% | Test through integration tests |
| Overall project | 70-80% | Diminishing returns above this |

Branch coverage matters more than line coverage. A line can be "covered" without testing all the paths through it.

## Test Organization

- Mirror source directory structure in test directories (or colocate test files with source).
- Group tests by behavior, not by method name.
- Use descriptive test names that read like specifications:
  - Good: `test_expired_token_returns_401_unauthorized`
  - Bad: `test_validate_token_3`
- Use setup/teardown (beforeEach/afterEach, setUp/tearDown) for shared state, but keep it minimal.
- Avoid test interdependence. Each test must be able to run independently and in any order.
