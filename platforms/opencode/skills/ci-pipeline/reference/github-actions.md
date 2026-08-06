# GitHub Actions

Platform mechanics. For the job steps themselves, read the stack file for the project's language.

## Workflow Skeleton

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  # stack-specific jobs — see reference/<stack>.md
```

`concurrency` cancels superseded runs on the same ref, so a force-push doesn't leave stale jobs burning minutes. Top-level `permissions` applies to every job; widen it per job only where one genuinely needs more.

## Caching

```yaml
# Node.js - cache node_modules via setup-node
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: npm

# Go - cache module downloads and build cache
- uses: actions/setup-go@v5
  with:
    go-version: '1.22'
    cache: true

# Rust - use swatinem/rust-cache
- uses: swatinem/rust-cache@v2

# Docker layers - use buildx cache
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

For a stack not listed, cache the ecosystem's download directory keyed on the lock file — the same shape every one of these actions implements internally.

## Matrix Builds

Test across multiple versions or platforms:

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        node-version: [20, 22]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
```

Matrix the dimensions that can actually break independently — the language versions the project supports, and the platforms it ships to. A matrix over dimensions that never diverge multiplies cost for no signal.
