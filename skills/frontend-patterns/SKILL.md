---
name: frontend-patterns
description: Frontend router — the non-negotiables for UI work, when to infer from precedent versus ask versus escalate, and which reference to load for design direction, anti-patterns, component architecture, accessibility and responsiveness, or verification. Load first for any UI component, page, form, layout, styling, or state-management task.
---

# Frontend Patterns

A router: gather the right context, decide whether to clarify or escalate, then consult only the `frontend-patterns/reference/*` file the task needs.

## Non-Negotiables

- Reuse the existing visual system before inventing a new one. Generic polished UI that ignores the product's workflow and tone is the failure to avoid.
- Cover the states that matter: loading, empty, error, disabled, focus, and success when relevant.
- Verify explicitly. Do not stop at "the JSX/CSS looks right."
- Escalate to `spec-writing` when the request is really about workflow, information architecture, or product direction.

## Context First

Read the target route or component, the shared primitives, tokens, and styling config, nearby screens that solve a similar problem, and existing copy and state handling. Clarify only what is missing and material: the user's goal, the important states, the interaction model (inline, modal, drawer, navigation), and design-system or accessibility constraints.

| Situation | Default move |
|---|---|
| Clear UI bug or scoped feature | Implement directly, following local patterns |
| Visually vague but nearby precedent exists | Infer from adjacent screens and shared primitives |
| Product intent unclear and several designs plausible | Ask concise clarifying questions before encoding assumptions |
| Implies workflow, information-architecture, or undecided brand-direction change | Recommend `spec-writing` before implementing |

## Route to the Reference

| If the task is mainly about... | Consult |
|---|---|
| Visual direction, hierarchy, typography, color, spacing, motion, interaction tone | `reference/design-direction.md` |
| AI-slop smells and overused polish patterns to check before refining a surface | `reference/anti-patterns.md` |
| Component boundaries, state placement, forms, tables, lists, page shells | `reference/component-architecture.md` |
| Keyboard, semantics, focus, overlays, narrow screens, overflow, touch | `reference/accessibility-responsive.md` |
| Proof, state coverage, handoff notes | `reference/verification.md` |

## Report

Name the precedent, primitives, or tokens that informed the change, and state what was verified directly versus what still needs browser or human confirmation.
