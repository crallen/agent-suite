# UI Prototype

Generate **several radically different UI variations** on a single route, switchable from a floating bottom bar. The user flips between variants in the browser, picks one (or steals bits from each), then throws the rest away.

## When This Is the Right Shape

- "What should this page look like?"
- "I want to see a few options for this dashboard before committing."
- "Try a different layout for the settings screen."
- Any time the user would otherwise spend a day picking between three vague mockups in their head.

## Two Sub-Shapes — Strongly Prefer Sub-Shape A

A UI prototype is much easier to judge when it's **butting up against the rest of the app** — real header, real sidebar, real data, real density. Default to sub-shape A whenever there's a plausible existing page to host the variants.

### Sub-Shape A — Adjustment to an Existing Page (Preferred)

The route already exists. Variants are rendered **on the same route**, gated by a `?variant=` URL search param. The existing data fetching, params, and auth all stay — only the rendering swaps.

If the prototype is for something that doesn't yet have a page but *would naturally live inside one*, that's still sub-shape A — mount the variants inside the host page.

### Sub-Shape B — A New Page (Last Resort)

Only use this when the thing being prototyped genuinely has no existing page to live inside (an entirely new top-level surface, a flow that can't be embedded anywhere sensible).

Create a throwaway route following whatever routing convention the project already uses. Name it so it's obviously a prototype (e.g., include "prototype" in the path or filename).

Before committing to sub-shape B: is there really no existing page this could be embedded in? An empty route hides design problems that a populated one would expose.

## Process

### 1. State the Question and Pick N

Default to **3 variants**. More than 5 stops being radically different and starts being noise.

Write down the plan in one line:
> "Three variants of the settings page, switchable via `?variant=`, on the existing `/settings` route."

### 2. Generate Radically Different Variants

Draft each variant. Hold each one to:
- The page's purpose and the data it has access to.
- The project's component library / styling system (TailwindCSS, shadcn, MUI, plain CSS, whatever).
- A clear exported component name: `VariantA`, `VariantB`, `VariantC`.

Variants must be **structurally different** — different layout, different information hierarchy, different primary affordance, not just different colours. Three slightly-tweaked card grids isn't a UI prototype. If two drafts come out too similar, redo one with an explicit constraint ("do not use a card grid").

### 3. Wire Them Together

```tsx
// pseudo-code — adapt to the project's framework
const variant = searchParams.get('variant') ?? 'A';
return (
  <>
    {variant === 'A' && <VariantA {...data} />}
    {variant === 'B' && <VariantB {...data} />}
    {variant === 'C' && <VariantC {...data} />}
    <PrototypeSwitcher variants={['A','B','C']} current={variant} />
  </>
);
```

For sub-shape A: keep all existing data fetching above the switcher; only the rendered subtree changes per variant.

### 4. Build the Floating Switcher

A small fixed-position bar at the bottom-centre with three pieces:
- **Left arrow** — cycles to the previous variant (wraps around).
- **Variant label** — shows the current variant key and, if the variant exports a name, that name. e.g. `B — Sidebar layout`.
- **Right arrow** — cycles forward (wraps around).

Behaviour:
- Clicking an arrow updates the URL search param (use the framework's router — `router.replace` on Next, `navigate` on React Router, etc.) so the variant is shareable and reload-stable.
- Keyboard: `←` and `→` arrow keys also cycle. Don't intercept arrow keys when an `<input>`, `<textarea>`, or `[contenteditable]` is focused.
- Visually distinct from the page (high-contrast pill, subtle shadow) so it's obviously not part of the design being evaluated.
- Hidden in production builds — gate on `process.env.NODE_ENV !== 'production'` or equivalent.

Put the switcher in a single shared component so both sub-shapes can reuse it.

### 5. Hand It Over

Surface the URL and the `?variant=` keys. The interesting feedback is usually "I want the header from B with the sidebar from C" — that's the actual design they want.

### 6. Capture the Answer and Clean Up

Once a variant has won, write down which one and why (commit message, ADR, issue, or `NOTES.md`). Then:
- **Sub-shape A** — delete the losing variants and the switcher; fold the winner into the existing page.
- **Sub-shape B** — promote the winning variant to a real route, delete the throwaway route and the switcher.

## Anti-Patterns

- **Variants that differ only in colour or copy.** Real variants disagree about structure.
- **Sharing too much code between variants.** A shared `<Header>` is fine; a shared `<Layout>` defeats the point.
- **Wiring variants to real mutations.** Read-only prototypes are fine; point mutations at a stub.
- **Promoting the prototype directly to production.** Rewrite it properly when folding it in — the variant code was written under prototype constraints.
