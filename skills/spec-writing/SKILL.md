---
description: Collaborative workflow for turning ideas into design specs — scope decomposition, clarifying dialogue, approach exploration, staged design presentation, and spec self-review
---

# Spec Writing

This skill covers the dialogue and drafting workflow for turning a request into an approved design spec before implementation starts. Load it when an agent needs to decompose scope, ask focused clarifying questions, compare approaches, and hand back an execution-ready task checklist.

## Workflow

A spec is a written design that precedes implementation. This skill guides the dialogue and drafting process that produces one. Work through the phases in order — do not jump ahead to drafting before scope and approach are settled.

### Phase 1: Scope Gate

Before asking any clarifying questions, assess the scope of the request.

- **Single spec candidate**: The request describes one cohesive change with a clear boundary. Proceed to Phase 2.
- **Multi-subsystem request**: The request describes several independent pieces (e.g., "build a platform with auth, billing, chat, and analytics"). Do **not** start a single spec. Instead, propose a decomposition:
  1. Identify the independent sub-projects and what each owns.
  2. Note dependencies between them (which must be built first).
  3. Ask the user which sub-project to spec first.
  4. Each sub-project gets its own spec → plan → implementation cycle.

Do not skip this gate on "simple" requests. "Simple" projects are where unexamined assumptions cause the most wasted work. The spec can be short — a few sentences for genuinely trivial work — but a design step must still happen.

### Phase 2: Explore Project Context

Ground the dialogue in the actual codebase before speculating about design.

- Read the files the request will likely touch. Trace their dependencies.
- Check recent commits and open work to understand direction.
- Identify existing patterns, conventions, and architectural constraints that the new work must respect.
- Note any problems in surrounding code that materially affect this work (a file that has grown too large, unclear boundaries, tangled responsibilities). Include targeted improvements in the spec if they serve the current goal. Do not propose unrelated refactoring.

### Phase 3: Clarifying Questions

Ask questions one at a time. Do not dump a list.

- **Prefer multiple choice** — easier to answer quickly than open-ended questions. Open-ended is fine when the problem is truly exploratory.
- **One question per message**. If a topic needs more exploration, break it into multiple questions across multiple turns.
- **Focus on**: purpose (why), constraints (what must be true), and success criteria (how will we know it worked).
- **Stop when you have enough**. Once purpose, constraints, and success criteria are clear, move on — do not ask more questions for the sake of thoroughness.

### Phase 4: Propose Approaches

Before writing a design, surface alternatives.

- Propose **2–3 approaches** with meaningfully different tradeoffs.
- For each: summarize the approach, its tradeoffs, and its fit to the constraints.
- **Lead with your recommendation** and explain why. Do not hide your opinion behind a neutral survey of options.
- If the approaches are essentially equivalent, don't manufacture alternatives — state that one direction is clearly best and why.

Template:

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

Wait for the user to pick or discuss before drafting the design.

### Phase 5: Present the Design in Stages

Do **not** dump a full design document in one message. Present it section by section. After each substantial section, confirm direction before continuing.

Scale each section to its complexity: a few sentences if straightforward, a few paragraphs if nuanced. Cover only what is relevant — a one-line fix does not need every section.

Sections, in the order they should appear:

| Section | Content |
|---|---|
| Goal | One paragraph: what will be accomplished and why. |
| Context | Relevant files, existing patterns, architectural constraints discovered in Phase 2. |
| Approach | The chosen strategy and the reasoning. Briefly note alternatives considered. |
| Components | Units being added or changed. For each: what it does, how it's used, what it depends on. |
| Data flow | How data moves through the system (when relevant). |
| Error handling | Failure modes and how they're handled (when relevant). |
| Testing | What tests will prove it works. Unit/integration/e2e split if applicable. |
| Risks & open questions | Known risks with mitigations; questions still unresolved. |
| Task checklist | Discrete, ordered tasks suitable for direct execution. |

Use this template for the finished spec, omitting sections that do not apply:

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

A one-line fix may only need `Goal` and `Task Checklist`. Do not add ceremony for its own sake.

### Phase 6: Spec Self-Review

Before presenting the finished spec for final approval, re-read it with fresh eyes and fix issues inline. No need to re-review after fixing — fix and move on.

- [ ] **Placeholders**: Any `TBD`, `TODO`, `...`, or vague requirements? Replace with concrete content or remove.
- [ ] **Internal consistency**: Do any sections contradict each other? Does the approach match the component list? Do the tasks match the approach?
- [ ] **Scope check**: Is this focused enough for a single implementation plan, or does it need decomposition? If it grew too large during dialogue, return to Phase 1.
- [ ] **Ambiguity**: Could any requirement be read two ways? Pick one interpretation and make it explicit.
- [ ] **Specificity**: Does the spec name the actual files, functions, and interfaces — or does it speak in generalities? Replace vague references with concrete ones.
- [ ] **Task checklist executability**: Is each task discrete, ordered, and clear enough for an executor to pick up without re-researching?

### Phase 7: User Review Gate

Present the finished spec and ask for review. If the user requests changes, apply them and re-run the self-review. Only hand off once the user approves.

Suggested wording:

> "Here's the spec. Let me know if you want any changes before we hand this to the tech-lead for execution — or I can save it as a file first."

## Design Principles

These principles should guide every spec.

### Isolation and Clarity

Break the system into smaller units that each have one clear purpose, communicate through well-defined interfaces, and can be understood and tested independently.

For each unit, you should be able to answer:
- What does it do?
- How do you use it?
- What does it depend on?

Litmus tests:
- Can someone understand what a unit does without reading its internals? If not, the interface leaks implementation detail.
- Can you change the internals without breaking consumers? If not, the boundary is in the wrong place.
- Is the file small enough to hold in context? Large files are usually doing too much.

### YAGNI — You Aren't Gonna Need It

Ruthlessly remove unnecessary features from the design. If something isn't required to meet the stated success criteria, cut it. Options to be suspicious of:
- Configuration knobs nobody asked for
- Abstraction layers with only one implementation
- "Future-proofing" that anticipates requirements nobody has stated
- Features that exist because they'd be "nice to have"

### Proportionality

Match the design's depth to the complexity of the work.

- **Trivial change**: A few sentences of goal + task list is a complete spec.
- **Small feature**: Goal, approach, components, tasks. Skip sections that don't add value.
- **Substantial feature**: All sections, each sized to the material it covers.

Padding a spec with ceremony does not make it better. A spec should be as short as it can be while still being precise.

### Grounded, Not Imagined

Every non-trivial claim in the spec should be backed by something you've read. If the spec says "the auth module handles X," you should have read the auth module. If it says "this pattern is consistent with existing conventions," you should be able to point to an example.

## Anti-Patterns

- **"This is too simple to need a design."** Every project goes through the process. The design can be short, but it cannot be skipped.
- **Asking five questions at once.** One at a time, multiple choice when possible.
- **Presenting the full design in one wall of text.** Stage it; confirm direction section by section.
- **Neutral option surveys with no recommendation.** Always lead with what you think is best and why.
- **Vague task lists.** "Update the auth module" is not a task. "Modify `src/auth/session.ts` to add a `refresh()` method that returns a new access token" is a task.
- **Designing from imagination.** Never draft a spec for files you haven't read.
- **Scope creep during dialogue.** If the conversation keeps growing the surface area, stop and return to the scope gate.
- **Skipping the self-review.** Fresh-eyes review catches placeholders, contradictions, and ambiguity that the drafter glossed over.

## Handoff

The terminal state of this workflow is delivering an approved spec back to the main conversation (the tech lead) for execution. Do not begin implementation yourself. If the user wants the spec saved as a file, ask for confirmation and write it to disk with a date-stamped filename like `docs/specs/YYYY-MM-DD-<topic>.md` (or follow the project's existing convention if one exists). For greenfield projects or early-stage work, a top-level `DESIGN.md` is also appropriate.
