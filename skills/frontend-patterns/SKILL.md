---
name: frontend-patterns
description: Frontend house rules and router — the non-negotiables and house taste for UI work, when to infer from precedent versus ask versus escalate, and which reference to load for anti-patterns, component architecture, or accessibility and responsiveness. Load first for any UI component, page, form, layout, styling, or state-management task, including a single component pasted into the conversation, and for questions about where UI state belongs or how a component should be split.
---

# Frontend Patterns

Gather the right context, decide whether to clarify or escalate, then consult only the `frontend-patterns/reference/*` file the task needs.

## Non-Negotiables

- Generic polished UI that ignores the product's workflow and tone is the failure to avoid.
- Cover the states that matter: loading, empty, error, disabled, focus, and success when relevant.
- Verify explicitly. Do not stop at "the JSX/CSS looks right."
- Escalate to `spec-writing` when the request is really about workflow, information architecture, or product direction.

## House Taste

- Pick one dominant move per screen: clearer, quieter, bolder, tighter, or more breathable.
- Hierarchy comes from typography before decoration: a small set of text styles, heavier weights only for true emphasis.
- Color reinforces meaning (success, danger, selection); neutral surfaces and spacing do the structural work. New tokens prefer `oklch` or `color-mix` over ad hoc HSL.
- Tighten inside groups and loosen between them, with `gap` and layout primitives rather than margin hacks.
- One primary action per region.
- No reflex gradients, glows, or cards inside cards; add a container only where containment helps.
- Loading and busy states keep the layout of the loaded state.
- Motion explains a state change: brief, opacity and transform, `prefers-reduced-motion` respected.
- Feedback sits at the interaction point: inline validation, a busy button, in-place confirmation rather than a toast.
- Buttons name the action, empty states teach the next step, and errors say what failed and what to do.

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
| Auditing or refining a surface: the full catalog of AI-slop smells and overused polish patterns | `frontend-patterns/reference/anti-patterns.md` |
| Component boundaries, state placement, forms, tables, lists, page shells | `frontend-patterns/reference/component-architecture.md` |
| Keyboard, semantics, focus, overlays, narrow screens, overflow, touch | `frontend-patterns/reference/accessibility-responsive.md` |

## Report

Name the precedent, primitives, or tokens that informed the change. Name the states checked and the commands run, rather than "verified UI" or "tests passed", and state what still needs browser or human confirmation.
