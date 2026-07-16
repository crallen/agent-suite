---
name: grill
description: Structured interrogation workflow for stress-testing a plan — one question at a time with a recommendation, codebase-grounded answers, and a shared-understanding gate before any action. Load when the user wants to grill a plan or design; pairs with domain-modeling for terminology and ADR writes.
---

# Grill

This skill drives a structured grilling session: a sustained, Socratic interrogation of a plan or design that challenges every assumption and anchors decisions in the real codebase. Load it when the user wants to stress-test a plan before or after speccing it.

Load `domain-modeling` alongside this skill: grilling reshapes the domain model as terms and decisions crystallize, and that skill owns the terminology lenses, CONTEXT.md upkeep, and ADR discipline.

## Interrogation Workflow

Work through the plan branch by branch, resolving dependencies between decisions one at a time. Do not move to the next question until the current one is settled — if a question reveals a contradiction or gap, stay on it until it's resolved.

**For each question:**
1. **Explore first** — facts live in the environment: if the codebase can answer it, read the relevant files instead of asking. Decisions belong to the user: put each one to them and wait.
2. **State your recommendation** — do not ask a neutral question; you're stress-testing, not surveying. Pose the question, then give your best answer and the reasoning behind it.
3. **Wait for feedback** — one question per message, always. Batching lets the user skim past the hard ones.
4. **Anchor the answer** — once agreed, note it as a resolved decision before moving on.

Keep going until the entire plan has been walked down. The goal is zero unresolved branches — and implementation starts only after the user confirms shared understanding.

## Session Behaviors

Apply these lenses throughout the session:

**Stress-test with concrete scenarios** — for each significant decision, run at least one edge case through it. "What happens when X is empty?", "What if two users do this simultaneously?", "What does the caller do if this fails?" Vague designs collapse under concrete scenarios.

**Cross-reference the plan with code** — when a design refers to an existing module, pattern, or entity, read it. Confirm that the plan is consistent with what actually exists, not what someone remembers existing.
