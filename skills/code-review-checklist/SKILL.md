---
name: code-review-checklist
description: The review rubric and report format — spec fidelity as its own axis, the house rules for naming and error shape, the Fowler design-smell baseline, and severity calibration. Load when reviewing a diff, a pull request, or a file for quality.
---

# Code Review Checklist

Two rules govern every item:

- **The repo overrides.** Documented project standards (`CONTRIBUTING.md`,
  `CODING_STANDARDS.md`, `CONTEXT.md`, style guides) win over any generic item
  here. Where the repo endorses something this rubric would flag, follow the repo.
- **Skip what tooling enforces.** Report only what the project's linters,
  formatters, and type-checkers can't see.

## Review Output Format

- `## Summary` - one-paragraph overall assessment.
- `## Findings` - split by severity using `### CRITICAL`, `### WARNING`, and
  `### INFO` subsections. Under each populated subsection, a markdown table with
  columns `Location | Issue | Impact | Suggestion`. Omit empty sections; if there
  are no findings, say so plainly.
- `## Recommendations` - prioritized follow-up list.
- Keep rows concise. A finding that needs nuance gets a short note below its
  table, not wider columns.

Severity:

- **CRITICAL**: must fix before merge. Security vulnerabilities, data corruption
  risks, correctness bugs in critical paths.
- **WARNING**: should fix before merge. Performance issues, missing error handling,
  maintainability problems.
- **INFO**: consider addressing. Style suggestions, minor improvements.

Calibration:

- **Axes don't mask each other.** Spec fidelity and code quality are separate
  axes; report findings on one even when the other is clean.
- **Smells are judgement calls.** Design-smell findings land at INFO, or WARNING
  when the impact in this diff is concrete, never CRITICAL.

## Scope and Spec Fidelity

`coding-guardrails` defines the diff discipline the change should have met.
Review what's absent, not just what changed: anything the request or spec asked
for that is missing or only partially implemented, assumptions that should have
been surfaced, and a materially simpler approach that would have met the
requirement.

## Correctness, Performance, Security

Trace the logic by hand and check the edges: empty input, nulls, boundaries,
concurrency, failure conditions, type conversions. For performance, look for
N+1 access, unbounded result sets, and work in hot paths that a cache or a better
algorithm removes. Security findings follow `security-analysis`; apply its
taxonomy and report exploitable issues at CRITICAL.

## Maintainability

- Could a clearer name remove the need for the comment? Where a comment earns its
  place, does it name the mechanism rather than a metaphor for it?
- Are identifiers named for the scenario they represent, not for a failure or a
  vaguer alias? (`raise_access_denied`, not `_boom`)
- Is in-code prose lean: no step narration, no banner comments inside literals, no
  documenting trivial items to satisfy a lint?
- Do docs and comments the change touches stay true to the code, without
  aspirational or stale claims?
- Does a seam earn its place because something real varies across it?
- Do dependencies point one way, with business logic free of transport, framework,
  and persistence types, and no new import cycle?

The smell baseline below covers duplication and structure, and flags a name that
reveals nothing. The items above catch the different failure: a name or comment
that reads as precise but is not. `doc-templates` holds the full register and
naming rules.

## Error Handling

- Errors carry context and cause across boundaries, and are never swallowed.
- No error types or variants nothing branches on; model the distinctions callers
  act on, not more.
- Recoverable errors propagate rather than panicking; abort is for startup
  invariants and tests.
- Cleanup runs on error paths, and retries with backoff exist only for transient
  failures.

## Testing

New and changed code has tests covering the happy path and the error cases, and
they are deterministic. Coverage adequacy follows the category targets in
`test-strategy`.

## Design Smells (Fowler baseline)

A fixed baseline (*Refactoring*, ch. 3) that applies even when the repo documents
no standards of its own. Report each as a possibility ("possible Feature Envy"),
never a hard violation. Each entry reads *what it is* → *how to fix*:

- **Mysterious Name** — a name that doesn't reveal what it does or holds. →
  Rename it; if no honest name comes, the design is murky.
- **Duplicated Code** — the same logic shape in more than one hunk or file. →
  Extract the shared shape and call it from both.
- **Feature Envy** — a method that reaches into another object's data more than
  its own. → Move the method onto the data it envies.
- **Data Clumps** — the same few fields or parameters keep travelling together. →
  Bundle them into one type.
- **Primitive Obsession** — a primitive standing in for a domain concept. → Give
  the concept its own small type.
- **Repeated Switches** — the same `switch`/`if` cascade on the same type recurs.
  → Polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many
  files. → Gather what changes together into one module.
- **Divergent Change** — one module is edited for several unrelated reasons. →
  Split it so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks nothing present
  requires. → Delete it; inline until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't
  depend on. → Hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly delegates onward. → Cut it and
  call the real target.
- **Refused Bequest** — an implementer that ignores most of what it inherits. →
  Drop the inheritance and use composition.
