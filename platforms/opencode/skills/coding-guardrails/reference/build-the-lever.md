# Build the Lever

When the work isn't trivial, build the tool that does it instead of doing it by hand. The bar is triviality, not repetition — even a one-off earns a lever when the lever is what makes the work checkable.

## Why

Two payoffs. **Throughput:** a codemod, generator, or script does the work the same way every time and reruns for free. **Confidence:** the tool is a single artifact a reviewer can read and rerun to check the work. A hand-done change can only be re-verified by redoing it; a deterministic script turns "trust me" into "run this".

## Pattern

Default to building the lever. Skip it only when the task is genuinely trivial — a couple of obvious edits you can see at a glance.

- Do the first unit by hand to learn the recipe, then build the tool. Prove it by rerunning it on that unit and diffing against your hand-done version.
- Make the lever safe to rerun — a reviewer will. Idempotent where it touches state (see `coding-guardrails/reference/idempotency.md`).
- Match the tool to the job: a codemod or script for edits, a generator for repetitive files, a dump-to-SQLite query for analysis, a rerunnable check for verification.
- A deterministic lever beats fan-out. If one pass can process every unit, run it yourself; don't spread hand-application across delegates that a script could do uniformly.
- Commit the lever when the work outlives the session, so the next run reruns it instead of redoing it.

## Balance

Build the smallest script that does or proves the job, never a framework — the simplicity guardrail still applies to the lever itself. Distinct from encoding a lesson in structure (a durable guardrail against a recurring mistake, `coding-guardrails/reference/encode-lessons-in-structure.md`); the lever is throughput and reviewability on the work in front of you.

If you invoked this principle and the diff contains no script, codemod, or generator, you didn't apply it — you described it.
