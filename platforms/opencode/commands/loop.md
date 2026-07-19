---
description: Run a prompt or command on a recurring interval — omit the interval to let the agent self-pace
---

Arm a recurring loop in this session using the `loop_start` tool.

## Parse the arguments

Accept `/loop [interval] <prompt>`.

- **Leading interval** — `5m /code-review`, `30s check status`, `2h run the report`.
- **Trailing interval** — `check the deploy every 5m`, `run tests every 10 minutes`.
- **No interval** — dynamic mode: you choose the delay after each tick.
- **Empty prompt** — reply `Usage: /loop [interval] <prompt>` and stop.

Convert the interval to seconds for `intervalSeconds` (`30s` → 30, `5m` → 300, `2h` → 7200). Strip the interval out of the prompt you pass through — `check the deploy every 5m` becomes the prompt `check the deploy`. A prompt starting with `/` is dispatched as that command, so `/loop 5m /code-review` re-runs `/code-review` each tick.

## Arm it

Call `loop_start` with the prompt, the interval in seconds, and `mode`:

- `fixed` when the user gave an interval — it re-arms itself until stopped.
- `dynamic` when they did not. Pick a sensible first delay, then call `loop_schedule` at the end of **every** tick or the loop ends. Match the delay to what you're waiting on: poll external state (a CI run, a deploy) on its own timescale; when there's no specific signal, 20–30 minutes is a reasonable idle cadence. Don't schedule tight polls for work that will notify you anyway.

Then **run the prompt once immediately** — the first tick only fires after the interval elapses, so arming alone leaves the user waiting.

## Report

After arming, confirm in a sentence or two: the interval (or that you're self-pacing), that the prompt already ran once, when the next tick lands, and that it repeats until stopped.

On later ticks, give a **short** update on what changed since the last one — not a full re-report. If nothing changed, say so in a line.

## Stopping

Call `loop_stop` when the user asks, when the loop's purpose is satisfied, or when the prompt keeps failing for the same reason. Say what stopped it. `loop_status` reports the current loop.

Only one loop runs per session — arming a second one replaces the first, so check with `loop_status` before replacing a loop the user may still want.

$ARGUMENTS
