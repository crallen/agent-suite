---
name: test-strategy
description: House rules for proving correctness — test-first vertical slices, the mock limit, coverage targets by category, test naming, and reserved fixture placeholders. Load when deciding how a change will be verified, writing or reviewing tests, or setting a coverage gate.
---

# Test Strategy

House rules for the tests themselves.

## Test-First: Vertical Slices

Build test-first in **vertical slices**: one test, the minimal code to pass it,
repeat. Each test responds to what the previous cycle taught. Writing all the
tests first and then all the code produces tests of imagined behavior, coupled to
shape rather than outcome.

Before the first test, list the behaviors to test in the project's domain
vocabulary (`CONTEXT.md` where present), critical paths first. The first test is
the **tracer bullet**: one behavior, end to end, red then green. Then one test per
remaining behavior, never anticipating the next. Refactor only at green, never
while red.

Each test describes behavior through the public interface and would survive an
internal refactor.

Expected values come from a source independent of the code: a known-good literal,
a worked example, the spec. An assertion that recomputes the expected value the
way the code does (`assert add(a, b) == a + b`, a snapshot derived by the same
steps) is **tautological**: it passes by construction and can never disagree with
the code.

## Mocks

Mock at boundaries (external services, databases in unit tests, clocks, randomness),
never internal interfaces between your own modules. Prefer fakes (in-memory
implementations) over mocks. If a single test needs more than three mocks, the code
under test has too many dependencies; refactor it rather than the test.

## Coverage Targets

| Category | Target | Rationale |
|---|---|---|
| Business logic | 80-90% branch coverage | This is where bugs cost the most |
| API handlers | 70-80% | Cover success, error, and auth cases |
| Utilities/helpers | 90%+ | Small, well-defined, easy to test |
| UI components | 60-70% | Focus on behavior, not rendering details |
| Infrastructure/config | 40-50% | Test through integration tests |
| Overall project | 70-80% | Diminishing returns above this |

Branch coverage, not line coverage: a line can be covered without testing every
path through it.

## Naming

Test names read like specifications: `test_expired_token_returns_401_unauthorized`,
not `test_validate_token_3`.

## Fixture Data

Never put real account numbers, ARNs, hostnames, or customer identifiers in
fixtures. A test file is readable by everyone with repo access and long outlives
the reason someone pasted a real value into it.

Use the reserved placeholder for each provider:

| Kind | Placeholder |
|---|---|
| AWS account ID | `123456789012` (also moto's default) |
| Domain names | `example.com`, `example.org`, `example.net` |
| IPv4 | `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` |
| Phone (US) | `555-0100` to `555-0199` |

Do not invent an "obviously fake" value instead. All-zeros and all-ones look safe
but are not reserved, and may belong to a real account or host. Use the documented
placeholder, and the same one across a repo, so a real value stands out in review.
