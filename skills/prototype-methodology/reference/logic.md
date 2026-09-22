# Logic Prototype

A tiny interactive terminal app that lets the user drive a state model by hand. Use this when the question is about **business logic, state transitions, or data shape** — the kind of thing that looks reasonable on paper but only feels wrong once you push it through real cases.

## When This Is the Right Shape

- "I'm not sure if this state machine handles the edge case where X then Y."
- "Does this data model actually let me represent the case where..."
- "I want to feel out what the API should look like before writing it."
- Anything where the user wants to **press buttons and watch state change**.

## Process



### 1. Isolate the Logic in a Portable Module

Put the actual logic behind a small, pure interface that could be lifted into the real codebase later. The TUI around it is throwaway; the logic module shouldn't be.

Right shapes to consider:
- **A pure reducer** — `(state, action) => state`. Good when actions are discrete events and state is a single value.
- **A state machine** — explicit states and transitions. Good when "which actions are even legal right now" is part of the question.
- **A small set of pure functions** over a plain data type. Good when there's no implicit current state — just transformations.
- **A class or module with a clear method surface** when the logic genuinely owns ongoing internal state.

Keep it pure: no I/O, no terminal code, no `console.log` for control flow. The TUI imports it and calls into it; nothing flows the other direction.

### 2. Build the Smallest TUI That Exposes the State

Build it as a **lightweight TUI** — on every tick, clear the screen and re-render the whole frame. The user should always see one stable view, not an ever-growing scrollback.

Each frame has two parts:

1. **Current state**, pretty-printed and diff-friendly (one field per line, or formatted JSON). Use **bold** for field names or section headers and **dim** for less important context (timestamps, IDs, derived values). Native ANSI escape codes are fine — `\x1b[1m` bold, `\x1b[2m` dim, `\x1b[0m` reset.
2. **Keyboard shortcuts** listed at the bottom: `[a] add user  [d] delete user  [t] tick clock  [q] quit`.

Behaviour:
1. Initialise state — a single in-memory object/struct. Render the first frame on start.
2. Read one keystroke (or one line) at a time, dispatch to a handler that mutates state.
3. Re-render the full frame after every action — don't append, replace.
4. Loop until quit.

The whole frame should fit on one screen.


### 3. Hand It Over

Give the user the run command. They'll drive it themselves; the interesting moments are "wait, that shouldn't be possible" or "huh, I assumed X would be different" — those are the bugs in the *idea*. If they want new actions added, add them.

### 4. Capture the Answer

When the prototype has done its job, ask what it taught them (or leave a `NOTES.md` if running AFK). The validated reducer / machine / function set can be lifted into the real module — the TUI shell gets deleted.
