---
name: test-strategy
description: House rules for proving correctness — test-first vertical slices, the mock limit, coverage targets by category, test naming, and reserved fixture placeholders. Load when deciding how a change will be verified, writing or reviewing tests, or setting a coverage gate.
---

# Test Strategy

Tests are how a vague request becomes a verifiable outcome. `coding-guardrails`
owns the verification loop per work type; this skill owns the house rules for the
tests themselves.

Clarify before encoding: if the expected behavior is unclear, settle it before
cementing it in a test. A test is an assertion about intent, and a wrong one is
harder to dislodge than wrong code. Do not add suites for hypothetical behavior
the code does not implement.

## Test-First: Vertical Slices

Build test-first in **vertical slices**: one test, the minimal code to pass it,
repeat. Each test responds to what the previous cycle taught. Writing all the
tests first and then all the code produces tests of imagined behavior, coupled to
shape rather than outcome.

Before the first test, confirm the interface changes and list the behaviors to
test in the project's domain vocabulary (`CONTEXT.md` where present), prioritized
to the critical paths. The first test is the **tracer bullet**: one behavior,
end to end, red then green. Then one test per remaining behavior, never
anticipating the next. Refactor only at green, never while red; the smell baseline
in `code-review-checklist` is the checklist for that pass.

Each test describes behavior through the public interface and would survive an
internal refactor.

## Mocks

Mock at boundaries (external services, databases in unit tests, clocks, randomness),
never internal interfaces between your own modules. Prefer fakes (in-memory
implementations) over mocks. If a single test needs more than three mocks, the code
under test has too many dependencies; refactor it rather than the test. Verify mock
interactions sparingly.

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
path through it. Skip tests of language or framework behavior itself, generated
code, and private helpers reached through their public callers.

## Naming

Test names read like specifications: `test_expired_token_returns_401_unauthorized`,
not `test_validate_token_3`. Name helpers and fixtures for the scenario they stand
in for, not for the fact that they fail: `raise_access_denied`, not `_boom`.
`doc-templates` holds the general naming and register rules. Tests run
independently in any order.

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
