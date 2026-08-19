---
description: Structured interrogation workflow for stress-testing a plan — one frontier question at a time with a recommendation, codebase-grounded answers, and a shared-understanding gate before any action. Load when the user wants to grill a plan or design; pairs with domain-modeling for terminology and ADR writes.
---

# Grill Methodology

This skill drives a structured grilling session: a sustained, Socratic interrogation of a plan or design that challenges every assumption and anchors decisions in the real codebase. Load it when the user wants to stress-test a plan before or after speccing it.

Load `domain-modeling` alongside this skill: grilling reshapes the domain model as terms and decisions crystallize, and that skill owns the terminology lenses, CONTEXT.md upkeep, and ADR discipline.

## Interrogation Workflow

Map the plan as a **design tree**: every decision branches into the decisions that hang off it. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard yet.

Ask **one frontier question per message**, always. Batching lets the user skim past the hard ones. Pick the frontier question that constrains the most of what's left — the one whose answer reshapes the largest part of the tree — and put that one, with your recommended answer. Then wait.

Present each question in two parts: the reasoning as prose, then the decision through the cleanest control the harness offers.

**Lead with prose.** A short bold title carrying the question's number (`**Q3 — <title>**`), the challenge and any context, then your recommended answer on its own line, clearly marked. Rich reasoning lives here, where markdown renders it properly. Do not use decorative emoji.

**Then take the answer** with the harness's structured question tool when it has one — for example `AskUserQuestion` in Claude Code and T3 Code: a concise restatement of the choice, concise option labels, the recommended option first and tagged "(Recommended)". The options capture the decision; the argument stays in the prose above, never crammed into an option label. When the harness offers no such tool, list the options inline and wait.

Never pose a neutral question — you're stress-testing, not surveying, so a recommendation is mandatory. Number questions consecutively across the whole session, so an earlier decision can be referred to by its number.

Each answer reshapes the tree: a settled decision pushes the frontier outward and unblocks the questions that depended on it. Anchor the agreed answer as a resolved decision, recompute the frontier, then ask the next question. Do not move on while the current question is unsettled — if an answer reveals a contradiction or gap, stay on that branch until it's resolved.

Finding **facts** is your job, never the user's. When a frontier question needs a fact from the environment, read the relevant files — or dispatch a subagent for anything sizable — instead of asking. Don't block on it: a running exploration is an unsettled prerequisite, so ask a frontier question that doesn't depend on it while the report comes back. **Decisions** belong to the user: put each one to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Implementation starts only after the user confirms shared understanding.

## Session Behaviors

Apply these lenses throughout the session:

**Stress-test with concrete scenarios** — for each significant decision, run at least one edge case through it. "What happens when X is empty?", "What if two users do this simultaneously?", "What does the caller do if this fails?" Vague designs collapse under concrete scenarios.

**Cross-reference the plan with code** — when a design refers to an existing module, pattern, or entity, read it. Confirm that the plan is consistent with what actually exists, not what someone remembers existing.
