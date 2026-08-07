---
name: grill-methodology
description: Structured interrogation workflow for stress-testing a plan — round-by-round frontier questioning with a recommendation per question, codebase-grounded answers, and a shared-understanding gate before any action. Load when the user wants to grill a plan or design; pairs with domain-modeling for terminology and ADR writes.
---

# Grill Methodology

This skill drives a structured grilling session: a sustained, Socratic interrogation of a plan or design that challenges every assumption and anchors decisions in the real codebase. Load it when the user wants to stress-test a plan before or after speccing it.

Load `domain-modeling` alongside this skill: grilling reshapes the domain model as terms and decisions crystallize, and that skill owns the terminology lenses, CONTEXT.md upkeep, and ADR discipline.

## Interrogation Workflow

Map the plan as a **design tree**: every decision branches into the decisions that hang off it. Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format each question like so:

```
❓ **Q1** - **<question title>**: <question body, possibly multiple paragraphs, including multiple choices>

➡️ <your recommended answer and the reasoning behind it>
```

Never pose a neutral question — you're stress-testing, not surveying.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock the questions that depended on them. Anchor each agreed answer as a resolved decision, recompute the frontier, and ask the next round. A question whose answer depends on another question still open in this round belongs to a *later* round, not this one. If an answer reveals a contradiction or gap, that branch stays on the frontier until it's resolved.

Finding **facts** is your job, never the user's. When a frontier question needs a fact from the environment, read the relevant files — or dispatch a subagent for anything sizable — instead of asking. Don't block a round on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the report — ask the rest of the frontier now. **Decisions** belong to the user: put each one to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Implementation starts only after the user confirms shared understanding.

## Session Behaviors

Apply these lenses throughout the session:

**Stress-test with concrete scenarios** — for each significant decision, run at least one edge case through it. "What happens when X is empty?", "What if two users do this simultaneously?", "What does the caller do if this fails?" Vague designs collapse under concrete scenarios.

**Cross-reference the plan with code** — when a design refers to an existing module, pattern, or entity, read it. Confirm that the plan is consistent with what actually exists, not what someone remembers existing.
