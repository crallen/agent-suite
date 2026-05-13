---
description: Frontend router for product context gathering, work-mode selection, escalation, and targeted reference selection
---

# Frontend Patterns

Load this skill first for frontend work. It is a router: gather the right context, decide whether to clarify or escalate, and then consult only the `frontend-patterns/reference/*` material that matches the task.

## Non-Negotiables

- Reuse the existing visual system before inventing a new one.
- Avoid generic AI-polished UI that ignores the product's actual workflow and tone.
- Cover the states that matter: loading, empty, error, disabled, focus, and success when relevant.
- Verify explicitly. Do not stop at "the JSX/CSS looks right."
- Escalate to `@architect` or `/spec` when the request is really about workflow, information architecture, or product direction.

## 1. Gather Product and Screen Context

Before changing UI, gather enough context to avoid shipping a generic answer.

### Read These Sources First

- The target route, page, or component entry point
- Shared UI primitives, layout wrappers, tokens, and styling config
- Nearby screens that solve a similar product problem
- Existing copy, empty states, and loading/error handling
- Tests, stories, snapshots, or docs if they exist

### Clarify When These Are Missing

- Primary user goal or success condition
- Important states (loading, empty, error, disabled, success)
- Interaction model (inline edit, modal, drawer, navigation change)
- Constraints from existing design system, brand, or accessibility expectations

## 2. Choose the Work Mode

| Situation | Default move |
|---|---|
| Clear UI bug or scoped feature | Implement directly, following local patterns |
| Request is visually vague but nearby precedent exists | Infer from adjacent screens and shared primitives |
| Product intent is unclear and multiple designs are plausible | Ask concise clarifying questions before encoding assumptions |
| Request implies broader workflow or information architecture changes | Recommend spec/design clarification before large implementation |

## 3. Route to the Right Frontend Reference

Consult only what the task needs. One small UI fix does not need the whole frontend stack in context.

| If the task is mainly about... | Consult this reference |
|---|---|
| Visual direction, hierarchy, typography, color, spacing, motion, interaction tone, or avoiding generic UI | `reference/design-direction.md` |
| AI-slop smells, repeated UI mistakes, overused polish patterns, or what to avoid before refining a surface | `reference/anti-patterns.md` |
| Component boundaries, state placement, extraction, forms, tables, lists, page shells, or UI composition | `reference/component-architecture.md` |
| Keyboard behavior, semantics, labels, focus, dialogs/menus/drawers, narrow screens, overflow, or touch behavior | `reference/accessibility-responsive.md` |
| Proof, state coverage, QA checklist, or concise frontend handoff notes | `reference/verification.md` |

### Common Load Sets

| Task shape | Typical skill load |
|---|---|
| Small component or form refinement | `reference/component-architecture.md` + `reference/accessibility-responsive.md` |
| Visually weak or under-specified screen | `reference/design-direction.md` + whichever implementation reference fits |
| Complex screen update with meaningful UI behavior | `reference/component-architecture.md` + `reference/accessibility-responsive.md` + `reference/verification.md` |
| Audit or critique of an existing surface | `reference/design-direction.md` + `reference/anti-patterns.md` + `reference/verification.md` |
| Final pass before handoff | `reference/verification.md`, plus any missing design/accessibility reference |

## 4. Escalate Instead of Improvising

- Escalate when the request changes navigation, information architecture, or multi-screen workflow.
- Escalate when brand direction or visual tone is explicitly undecided and multiple valid answers would materially change the implementation.
- Escalate when the current design system is too incomplete to support a confident change without inventing too much.
- For local UI work, prefer inference from adjacent screens over asking broad design questions.

## 5. Report What You Loaded and Verified

- Name the local precedent, primitives, or tokens that informed the change when helpful.
- State which frontend references guided the work if the decision-making would otherwise be opaque.
- Report what you verified directly and what still needs browser or human confirmation.

## Anti-Patterns

- Generic "dashboard polish" that ignores the product's real tone and structure
- Pulling every frontend reference into a small, local change
