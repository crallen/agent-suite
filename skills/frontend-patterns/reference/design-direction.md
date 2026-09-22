# Frontend Design Direction Reference

Use this reference when the work needs design judgment: shaping a screen, improving hierarchy, or making a surface feel intentional without drifting into redesign. `reference/anti-patterns.md` holds the smells to check afterwards.

## Start With Screen Intent

Before styling details, answer: what is the user's main task here, what should feel primary versus secondary, what must be scannable in a few seconds, and which nearby screen or shared primitive already sets the local visual language. If those are unclear, clarify before making elaborate styling decisions.

## Choose One Move

Pick one dominant move per screen or component; several at once produce muddled UI.

| Move | When it helps | Typical result |
|---|---|---|
| **Clearer** | The UI is confusing or dense | Stronger hierarchy, better labels, cleaner grouping |
| **Quieter** | The UI is visually loud or unfocused | Fewer accents, calmer surfaces, clearer primary action |
| **Bolder** | The UI hides the important thing | Deliberate emphasis, stronger contrast, one focal point |
| **Tighter** | Related information feels disconnected | Reduced spacing inside groups, better pairings, less chrome |
| **More breathable** | Scanning feels cramped | More section spacing, fewer competing borders and fills |

## Typography

Hierarchy comes from typography before decoration, with a small set of text styles per screen and heavier weights reserved for true emphasis. Reuse the product's type system; introduce a new treatment only when the screen genuinely lacks a usable pattern. Long passages get width constraints, not smaller text.

| Layer | Job | Common mistake |
|---|---|---|
| Page title | Establish the screen's purpose | Styled too similarly to section titles |
| Section title | Group related content | Loud enough to compete with the page title |
| Label / metadata | Support scanning | Too small or faint to read quickly |
| Helper / hint text | Reduce uncertainty | Repeats the label |

## Color and Surfaces

Color is semantic reinforcement (success, warning, danger, selection, emphasis); neutral surfaces and spacing do the structural work, and contrast goes on the most important action or fact rather than everywhere. New tokens prefer perceptually steady color functions (`oklch`, `color-mix`) over ad hoc HSL tweaks, and neutrals tint toward the product palette only subtly and only where the established system already does.

## Space and Layout

Spacing communicates grouping, rhythm, and importance: align to the established layout rhythm, increase separation between groups before adding decoration inside them, keep label/value, title/action, and field/error pairs tight, and prefer `gap` and layout primitives over margin piles. Density matches the product context: operational tools can be denser, decision-heavy screens need room.

| Problem | Better move |
|---|---|
| The screen feels noisy | Remove chrome first, then rebalance spacing |
| Users miss the main action | Increase hierarchy contrast near the action, not everywhere |
| Content feels disconnected | Tighten inside groups, expand between groups |
| Everything looks equally important | Reduce accents and title count; create one focal path |

## Motion and Interaction Tone

Motion explains state changes rather than calling attention to itself: brief, tied to interaction, opacity and transform over layout-janking animation, calm easing, and `prefers-reduced-motion` respected. Feedback stays close to the interaction point: inline validation, button busy state, in-place confirmation. Controls carry coherent default, hover, focus, pressed, disabled, and loading states, with hover and focus related rather than two design systems.

## Copy

Labels reflect the real task, not implementation language. Buttons name the action (`Save changes`, `Invite member`, `Retry sync`). Empty states teach the next step, error messages are specific enough to unblock, helper text reduces uncertainty rather than restating the label, and confirmation is inline when the action scope is local.

## When It Still Feels Generic

Ask which is missing: a clearer task hierarchy, stronger use of local precedent, less decorative clutter, or more explicit state handling.
