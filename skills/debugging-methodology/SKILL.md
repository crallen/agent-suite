---
name: debugging-methodology
description: Systematic debugging workflow covering reproduction, evidence gathering, hypothesis testing, root cause analysis, and fix verification
---

# Debugging Methodology

A phased workflow for investigating bugs end-to-end. The most important phase is Phase 0 — building a reliable feedback loop. Everything else is mechanical once you have one.

If `CONTEXT.md` exists at the repo root, read it before exploring — the domain glossary helps you orient to the relevant modules. Also check `docs/adr/` in the area you're touching for recorded decisions.

## Phase 0: Build a Feedback Loop

**This is the skill.** If you have a fast, deterministic, agent-runnable pass/fail signal for the bug, you will find the cause. If you don't, no amount of staring at code will save you. Spend disproportionate effort here.

### Strategies — try in roughly this order

1. **Failing test** at whatever seam reaches the bug — unit, integration, e2e.
2. **Curl / HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright / Puppeteer) — drives the UI, asserts on DOM/console/network.
5. **Replay a captured trace.** Save a real network request / payload / event log to disk; replay it through the code path in isolation.
6. **Throwaway harness.** Spin up a minimal subset of the system that exercises the bug code path with a single function call.
7. **Property / fuzz loop.** If the bug is "sometimes wrong output", run 1000 random inputs and look for the failure mode.
8. **Bisection harness.** If the bug appeared between two known states (commit, dataset, version), automate "boot at state X, check, repeat" so you can `git bisect run` it.
9. **Differential loop.** Run the same input through old-version vs new-version (or two configs) and diff outputs.
10. **Structured manual loop.** Last resort. If a human must click, produce a structured script so the loop is at least repeatable and captured output feeds back to you.

### Iterate on the loop itself

Once you have *a* loop, ask: Can I make it faster? Can I make the signal sharper (assert on the specific symptom, not "didn't crash")? Can I make it more deterministic (pin time, seed RNG, freeze network)? A 2-second deterministic loop is a debugging superpower. A 30-second flaky loop is barely better than nothing.

### Non-deterministic bugs

The goal is not a clean repro but a **higher reproduction rate**. Loop the trigger 100×, parallelise, add stress, narrow timing windows. A 50%-flake bug is debuggable; 1% is not — keep raising the rate.

### When you genuinely cannot build a loop

Stop and say so explicitly. List what you tried. Ask for: (a) access to the environment that reproduces it, (b) a captured artifact (log dump, HAR file, core dump), or (c) permission to add temporary production instrumentation. Do **not** proceed to hypothesise without a loop.

## Phase 1: Reproduce

Run the loop. Watch the bug appear.

Confirm:
- [ ] The loop produces the failure mode the **user** described — not a different failure that happens to be nearby. Wrong bug = wrong fix.
- [ ] The failure is reproducible across multiple runs (or at a high enough rate to debug against for non-deterministic bugs).
- [ ] You have captured the exact symptom (error message, wrong output, slow timing) so later phases can verify the fix actually addresses it.

## Phase 2: Gather Evidence

Collect information before forming theories.

**Read error output carefully:**
- Stack traces tell you the call chain. Read from bottom to top.
- Error messages often contain the exact cause. Don't gloss over them.
- Log timestamps reveal ordering and timing issues.

**Check recent changes:**
```bash
git log --oneline -20           # Recent commits
git log --oneline --all -20     # Including other branches
git diff HEAD~5                 # Changes in last 5 commits
git bisect start                # Binary search for breaking commit
```

**Inspect runtime state:**
- Add targeted logging at key decision points (input values, branch taken, return values).
- Check configuration values at runtime — are they what you expect?
- Inspect database state, file contents, environment variables.

**Check external dependencies:**
- Are external services responding? Check health endpoints.
- Are dependency versions what you expect? Check lock files.
- Has an external API changed its contract?

## Phase 3: Form Hypotheses

Generate **3–5 ranked hypotheses** before testing any of them. Single-hypothesis generation anchors on the first plausible idea.

Each hypothesis must be **falsifiable**: state the prediction it makes.

> Format: "If `<X>` is the cause, then `<changing Y>` will make the bug disappear / `<changing Z>` will make it worse."

If you cannot state the prediction, the hypothesis is a vibe — discard or sharpen it.

**Show the ranked list to the user before testing.** They often have domain knowledge that re-ranks instantly ("we just deployed a change to #3"), or know hypotheses they've already ruled out. Cheap checkpoint, big time saver. Don't block on it — proceed with your ranking if the user is AFK.

**Common root cause categories:**

| Category | Examples |
|---|---|
| Input handling | Unexpected nil/null, wrong type, missing field, encoding issue |
| State management | Stale cache, race condition, leaked state between requests |
| Logic error | Off-by-one, wrong operator, inverted condition, missing case |
| Resource issue | Connection pool exhaustion, memory leak, file descriptor leak |
| Dependency | Version mismatch, API contract change, transitive dependency conflict |
| Configuration | Wrong environment, missing env var, incorrect feature flag |
| Timing | Race condition, timeout too short, clock skew, retry storm |

## Phase 4: Test Hypotheses

Test each hypothesis systematically, starting with the most likely. **Change one variable at a time.**

**Tool preference:**
1. **Debugger / REPL inspection** if the env supports it. One breakpoint beats ten logs.
2. **Targeted logs** at the boundaries that distinguish hypotheses.
3. Never "log everything and grep".

**Tag every debug log** with a unique prefix, e.g. `[DEBUG-a4f2]`. Cleanup at the end becomes a single grep. Untagged logs survive; tagged logs die.

**Performance regressions:** logs are usually wrong. Instead: establish a baseline measurement (timing harness, `performance.now()`, profiler, query plan), then bisect. Measure first, fix second.

**Elimination techniques:**
- **Binary search (bisect)**: Narrow the problem space by half at each step.
- **Substitution**: Replace a suspected component with a known-good version. If the bug disappears, you've found the culprit.
- **Isolation**: Remove components until the bug disappears (or add components until it appears).

## Phase 5: Fix and Verify

Write the regression test **before the fix** — but only if there is a **correct seam** for it. A correct seam is one where the test exercises the *real bug pattern* as it occurs at the call site. A shallow seam (unit test that can't replicate the chain that triggered the bug) gives false confidence.

**If no correct seam exists, that itself is the finding.** Note it — the codebase architecture is preventing the bug from being locked down. This is a candidate for `/architecture` work.

If a correct seam exists:
1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail.
3. Apply the minimal fix that addresses the root cause.
4. Watch it pass.
5. Re-run the Phase 0 feedback loop against the original (un-minimised) scenario.
6. Check for variants — search the codebase for similar patterns that might have the same bug.
7. Run the full test suite to ensure the fix doesn't break anything else.

## Phase 6: Cleanup and Post-Mortem

Required before declaring done:

- [ ] Original repro no longer reproduces (re-run the Phase 0 loop)
- [ ] Regression test passes (or absence of seam is documented)
- [ ] All `[DEBUG-...]` instrumentation removed (`grep` the prefix)
- [ ] Throwaway prototypes or harnesses deleted
- [ ] The hypothesis that turned out correct is stated in the commit / PR message — so the next debugger learns

**Then ask: what would have prevented this bug?** If the answer involves architectural change (no good test seam, tangled callers, hidden coupling), hand off to `/architecture` with the specifics. Make the recommendation *after* the fix is in — you have more information now than when you started.

## Anti-Patterns

- **Shotgun debugging**: Changing things randomly hoping something works. This wastes time and can introduce new bugs.
- **Fixing symptoms**: Adding a nil check to prevent a crash without understanding why the value is nil.
- **Blame-driven debugging**: Assuming a specific component is at fault without evidence.
- **Tunnel vision**: Getting fixated on one hypothesis and ignoring contradicting evidence.
- **Skipping Phase 0**: Trying to fix a bug you can't reproduce. You'll have no way to verify the fix.
- **Moving on without a loop**: Hypothesising without a runnable pass/fail signal. Discipline here is everything.
