---
name: spec-writing
description: Dialogue-to-spec workflow — scope gate, one-question-at-a-time clarification with lettered options, recommended approaches, staged design, self-review, and a dated spec file. Load when a request needs a design before implementation, or when asked for a spec, plan, or design doc.
---

# Spec Writing

Work through the phases in order; drafting before scope and approach are settled is the failure this skill exists to prevent. The spec can be a few sentences for trivial work, but the design step still happens.

## Phase 1: Scope Gate

A request that describes one cohesive change with a clear boundary is a single spec. A request spanning several independent pieces ("auth, billing, chat, and analytics") is not: identify the independent sub-projects and what each owns, note which must be built first, and ask which to spec first. Each gets its own spec, plan, and implementation cycle. If the surface area keeps growing during dialogue, return here.

## Phase 2: Explore Project Context

Read the code the request will touch before speculating. Every non-trivial claim in the spec rests on something read: if the spec says the auth module handles X, the auth module was read. Note problems in surrounding code that materially affect this work (a file grown too large, tangled responsibilities) and include targeted improvements when they serve the goal; unrelated refactoring stays out.

## Phase 3: Clarifying Questions

One question per message. Prefer multiple choice; open-ended is fine when the problem is truly exploratory.

Letter the options inline (`A`, `B`, `C`) as a markdown list, one option per line with a blank line before the list, recommended option first and tagged "(Recommended)", in the same message as the reasoning. Do not use the harness's structured question tool: it shows the options without the surrounding context. The user answers by letter or in their own words.

Focus on purpose, constraints, and success criteria. Once those three are clear, stop asking.

## Phase 4: Propose Approaches

Propose two or three approaches with meaningfully different tradeoffs, and lead with the recommendation and why. When the approaches are essentially equivalent, say that one direction is clearly best rather than manufacturing alternatives.

```markdown
**Approach A: <name>** (Recommended)
- How it works: …
- Tradeoffs: …
- Why recommended: …

**Approach B: <name>**
- …

**Approach C: <name>**
- …
```


Wait for the user to pick or discuss before drafting.

## Phase 5: Present the Design in Stages

Section by section, confirming direction after each substantial one. Scale each section to its complexity and omit the ones that do not apply; a one-line fix may need only Goal and Task Checklist.

```markdown
## Goal
One-paragraph summary of what will be accomplished and why.

## Context
What the research revealed: relevant files, existing patterns, architectural constraints, and anything that shapes the approach.

## Approach
The chosen strategy and the reasoning behind it. Briefly note alternatives considered.

## Components
The units being added or changed. For each: what it does, how it's used, what it depends on.

## Data Flow  (when relevant)
How data moves through the system.

## Error Handling  (when relevant)
Failure modes and how they are handled.

## Testing
How correctness will be proven. Unit/integration/e2e split if applicable.

## Risks & Open Questions
- **Risk**: Description and mitigation.
- **Open**: Questions still unresolved.

## Task Checklist
- [ ] Task one
- [ ] Task two
- [ ] ...
```


Each task names the actual files, functions, and interfaces: "modify `src/auth/session.ts` to add a `refresh()` method that returns a new access token", never "update the auth module".

## Phase 6: Self-Review

Re-read with fresh eyes and fix inline; no second review after fixing.

- [ ] **Placeholders**: Any `TBD`, `TODO`, `...`, or vague requirements? Replace with concrete content or remove.
- [ ] **Internal consistency**: Do any sections contradict each other? Does the approach match the component list? Do the tasks match the approach?
- [ ] **Scope check**: Is this focused enough for a single implementation plan, or does it need decomposition? If it grew too large during dialogue, return to Phase 1.
- [ ] **Ambiguity**: Could any requirement be read two ways? Pick one interpretation and make it explicit.
- [ ] **Specificity**: Does the spec name the actual files, functions, and interfaces — or does it speak in generalities? Replace vague references with concrete ones.
- [ ] **Task checklist executability**: Is each task discrete, ordered, and clear enough for an executor to pick up without re-researching?


## Phase 7: User Review Gate and Handoff

Present the finished spec and ask for review. Apply requested changes and re-run the self-review; hand off only once the user approves. Do not begin implementation.

Save the approved spec as `docs/specs/YYYY-MM-DD-<topic>.md`, or follow the project's existing convention; a top-level `DESIGN.md` suits greenfield work. Confirm before writing the file.

## Design Principle: Depth

Divide the system by interface. Prefer few modules with small interfaces over many that each expose nearly everything they do; a module may be composed internally of small parts, and keeping those out of its interface is what makes it deep. `architecture-review/reference/vocabulary.md` holds the vocabulary, and `architecture-review` measures finished designs by it. Cut anything not required by the stated success criteria: configuration knobs nobody asked for, abstraction layers with one implementation, future-proofing for unstated requirements.
