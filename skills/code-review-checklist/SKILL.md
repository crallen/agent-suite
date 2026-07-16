---
description: Structured code review rubric covering spec fidelity, correctness, security, performance, maintainability, error handling, testing, and a design-smell baseline
---

# Code Review Checklist

Work through each section systematically. Not every item applies to every review — focus on what's relevant to the changes at hand.

Two rules govern every item:

- **The repo overrides.** Documented project standards (`CONTRIBUTING.md`, `CODING_STANDARDS.md`, `CONTEXT.md`, style guides) win over any generic item here. Where the repo endorses something this rubric would flag, follow the repo.
- **Skip what tooling enforces.** Report only what the project's linters, formatters, and type-checkers can't see.

### 0. Scope & Spec Fidelity

- [ ] Do the changed lines trace directly to the user's request or approved spec?
- [ ] Is anything the request or spec asked for missing or only partially implemented? Review what's absent, not just what changed.
- [ ] Did the implementation make assumptions that should have been clarified or documented?
- [ ] Is there a materially simpler approach that would meet the requirement?
- [ ] Did the author avoid drive-by refactors, style churn, and unrelated cleanup?
- [ ] Are verification steps and tests proportional to the risk and clearly tied to the goal?

### 1. Correctness

- [ ] Does the code do what it's supposed to do? Trace the logic manually.
- [ ] Are there off-by-one errors in loops, slices, or range operations?
- [ ] Are edge cases handled? (empty input, nil/null/undefined, zero values, max values)
- [ ] Are there race conditions in concurrent code? (shared mutable state, missing locks)
- [ ] Are type conversions safe? (integer overflow, lossy float-to-int, string encoding)
- [ ] Is the code correct under failure conditions? (network timeout, disk full, OOM)

### 2. Security

- [ ] Is all user input validated and sanitized before use?
- [ ] Are SQL queries parameterized? (no string concatenation for queries)
- [ ] Is output properly escaped for the context? (HTML, JSON, shell, SQL)
- [ ] Are authentication and authorization checks present on all protected endpoints?
- [ ] Are secrets (API keys, passwords, tokens) kept out of code and logs?
- [ ] Are dependencies up to date? Are there known vulnerabilities?
- [ ] Is sensitive data encrypted at rest and in transit?
- [ ] Are CORS, CSP, and other security headers configured correctly?
- [ ] Does file handling prevent path traversal attacks?
- [ ] Are cryptographic operations using current, non-deprecated algorithms?

### 3. Performance

- [ ] Are there N+1 query patterns? (loading related data in a loop)
- [ ] Are database queries using appropriate indexes?
- [ ] Are there unnecessary memory allocations in hot paths? (allocating in loops, string concatenation)
- [ ] Is pagination implemented for unbounded result sets?
- [ ] Are expensive computations cached when the result is reusable?
- [ ] Are there blocking operations on the main thread / hot path?
- [ ] Is the algorithmic complexity appropriate? (O(n^2) where O(n log n) is possible)

### 4. Maintainability

- [ ] Are functions small and focused? (single responsibility)
- [ ] Is the code self-documenting, or does it need explanatory comments?
- [ ] Are abstractions at the right level? (not too abstract, not too concrete)
- [ ] Is the module/package structure logical?
- [ ] Would a new team member understand this code without explanation?

Naming, duplication, and structural design problems are covered by the smell baseline in section 8.

### 5. Error Handling

- [ ] Are all errors checked? (no ignored return values, uncaught exceptions)
- [ ] Do error messages include enough context for debugging? (what failed, what input caused it)
- [ ] Are errors propagated correctly? (wrapped with context, not swallowed)
- [ ] Is cleanup performed on error paths? (defer/finally, resource release, transaction rollback)
- [ ] Are retries implemented with backoff for transient failures?
- [ ] Are error types specific enough for callers to handle different cases?

### 6. Testing

- [ ] Are there tests for the new/changed code?
- [ ] Do tests cover the happy path AND error cases?
- [ ] Are edge cases tested? (boundary values, empty inputs, concurrent access)
- [ ] Are tests deterministic? (no time dependencies, no test ordering dependencies)
- [ ] Do tests document expected behavior? (descriptive names, clear assertions)
- [ ] Is test coverage adequate for the risk level of the code?

### 7. API Design (if applicable)

- [ ] Is the API consistent with existing patterns in the codebase?
- [ ] Are breaking changes clearly marked and documented?
- [ ] Are input constraints validated and documented?
- [ ] Are error responses consistent and informative?
- [ ] Is the API versioned appropriately?

### 8. Design Smells (Fowler baseline)

A fixed baseline of code smells (*Refactoring*, ch. 3) that applies even when the repo documents no standards of its own. Report each smell as a possibility ("possible Feature Envy"), never a hard violation — severity follows the calibration rules under Review Output Format. Each entry reads *what it is* → *how to fix*:

- [ ] **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → Rename it; if no honest name comes, the design is murky.
- [ ] **Duplicated Code** — the same logic shape appears in more than one hunk or file. → Extract the shared shape and call it from both.
- [ ] **Feature Envy** — a method that reaches into another object's data more than its own. → Move the method onto the data it envies.
- [ ] **Data Clumps** — the same few fields or parameters keep travelling together. → Bundle them into one type and pass that.
- [ ] **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → Give the concept its own small type.
- [ ] **Repeated Switches** — the same `switch`/`if` cascade on the same type recurs across the change. → Replace with polymorphism, or one map both sites share.
- [ ] **Shotgun Surgery** — one logical change forces scattered edits across many files. → Gather what changes together into one module.
- [ ] **Divergent Change** — one file or module is edited for several unrelated reasons. → Split it so each module changes for one reason.
- [ ] **Speculative Generality** — abstraction, parameters, or hooks added for needs nothing present requires. → Delete it; inline until a real need shows.
- [ ] **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → Hide the walk behind one method on the first object.
- [ ] **Middle Man** — a class or function that mostly just delegates onward. → Cut it and call the real target directly.
- [ ] **Refused Bequest** — a subclass or implementer that ignores most of what it inherits. → Drop the inheritance and use composition.

## Review Output Format

Use this default review shape:

- `## Summary` - one-paragraph overall assessment.
- `## Findings` - split by severity using `### CRITICAL`, `### WARNING`, and `### INFO` subsections.
- Under each populated severity subsection, use a markdown table with columns `Location | Issue | Impact | Suggestion`.
- `## Recommendations` - prioritized follow-up list.
- Omit empty severity sections. If there are no findings, say so plainly under `## Findings`.
- Keep rows concise. If a finding needs extra nuance, add a short note below the relevant severity table instead of widening the columns.
- Example: `reference/review-table.md`

Categorize findings by severity:

- **CRITICAL**: Must fix before merge. Security vulnerabilities, data corruption risks, correctness bugs in critical paths.
- **WARNING**: Should fix before merge. Performance issues, missing error handling, maintainability problems.
- **INFO**: Consider addressing. Style suggestions, minor improvements, optional optimizations.

Two calibration rules:

- **Axes don't mask each other.** Spec fidelity (section 0) and code quality (sections 1-8) are separate axes — report findings on one even when the other is clean.
- **Smells are judgement calls.** Section 8 findings land at INFO, or WARNING when the impact in this diff is concrete — never CRITICAL.

Each table row should include:
1. **Location**
2. **Issue**
3. **Impact**
4. **Suggestion**
