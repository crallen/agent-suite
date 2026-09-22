# Frontend Verification Reference

Use this reference when the work needs explicit proof: before handoff, after a risky UI change, or when the user asked for tests, validation, or confidence in what changed.

## Verification Ladder

Use the strongest practical proof available, and report both what you verified and what you could not.

1. **Static review** - structure, semantics, local consistency, state coverage.
2. **Targeted behavior proof** - focused tests when behavior is important or fragile.
3. **Visual/state review** - default, hover, focus, disabled, loading, empty, error, and success as applicable.
4. **Responsive review** - narrow and wide layouts, wrapping, overflow, alignment.
5. **Accessibility review** - keyboard access, focus visibility, labeling, non-color-only cues; `reference/accessibility-responsive.md` has the checklist.
6. **Build/lint proof** - the relevant build, lint, typecheck, or test command.

Browser or manual interaction plus targeted tests beats code inspection alone; a changed-state review with explicit notes beats a generic "looks good"; narrow-plus-wide viewport confirmation beats desktop-only reasoning.

## State Coverage

- Loading, skeleton, or busy state present when work is asynchronous, preserving layout stability
- Empty state explains the situation and the next action
- Error state visible, specific, and recoverable where possible
- Disabled state intentional and, when the reason matters, explained
- Success or confirmation state where user confidence matters

## Proof Note

```markdown
Verified:
- [what you checked directly]
- [tests/commands run]

Not verified directly:
- [browser/manual/device checks still needed]
```

> Verified the updated filter panel in default, open, keyboard-focus, loading, and empty-result states. Ran `pnpm test -- filter-panel` and `pnpm lint`. I could not run a browser in this environment, so final responsive spacing and mobile overflow behavior should be confirmed in-browser.

Name the states checked rather than "verified UI", the commands run rather than "tests passed", and the missing proof rather than implying certainty you do not have.
