# Rust

The compiler covers boundary enforcement and type checking. Coverage needs a third-party subcommand, but it gates natively once installed.

## GitHub Actions

```yaml
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy
      - uses: swatinem/rust-cache@v2
      - uses: taiki-e/install-action@cargo-llvm-cov
      - run: cargo fmt --check
      - run: cargo clippy --all-targets --all-features -- -D warnings
      - run: cargo llvm-cov --workspace --fail-under-lines 80
```

## Roles

| Role | Command |
|---|---|
| Format | `cargo fmt --check` |
| Lint | `cargo clippy --all-targets --all-features -- -D warnings` |
| Type check | Covered by the compiler |
| Test + coverage | `cargo llvm-cov --workspace --fail-under-lines 80` |
| Boundary enforcement | `pub(crate)` / `pub(super)` visibility within a crate; workspace crate splits between crates, where a crate reaches only what its `Cargo.toml` declares. Cargo rejects crate cycles |

## Notes

- **`cargo llvm-cov` runs the tests itself**, so a separate `cargo test` step is redundant. Keep one or the other.
- **`--all-features` can fail** on crates with mutually exclusive features. Drop it, or enumerate the feature sets that matter, when that happens.
- **Cycle rejection is crate-level.** Modules within a single crate may reference each other cyclically without error; only crate-to-crate cycles are rejected. A workspace split is what buys the guarantee.
- **`-D warnings` on clippy** is what makes lint findings fail the build rather than scroll past.
