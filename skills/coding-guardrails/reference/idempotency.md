# Make Operations Idempotent

Design state-mutating operations to converge to the same end state regardless of how many times they run or where a previous run stopped. Crashes, restarts, and retries are normal, not exceptional — an operation that assumes it runs exactly once, start to finish, breaks the first time one doesn't.

Applies to commands, lifecycle steps (startup, migration, deploy), and processing loops that mutate durable state.

## Patterns

- **Converge on startup.** Scan the current state and reconcile to the target rather than assuming a clean slate. Clean up half-finished artifacts from a prior crashed run before proceeding.
- **Compare by content, not by time.** Decide whether work is needed from what the state *is* (a hash, a version, a present-or-absent artifact), not from a timestamp or a "did I already run" flag that a crash can leave lying.
- **Detect stale locks.** A lock file whose owning process is gone must not block forever. Record the PID (or a lease) and reclaim the lock when the owner is provably dead.
- **Regenerate work after failure.** A scheduler or queue should re-derive outstanding work from the desired state, so a job lost to a crash comes back on the next pass instead of vanishing.
- **Guard external effects with keys.** For effects you can't take back — a payment, an email, a remote write — carry an idempotency key so a retry is recognized as the same operation, not a second one.

## Tests

- Run it twice back to back. Does the second run change anything it shouldn't?
- Kill it partway through (before, during, and after the critical write) and run it again. Does it converge?
- If correctness depends on *history* — how many times it ran, in what order — that history needs an explicit reconciliation step, not an assumption.
