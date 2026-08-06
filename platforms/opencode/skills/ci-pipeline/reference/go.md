# Go

The compiler covers boundary enforcement and type checking, so the pipeline is shorter than an interpreted stack's. Coverage is the one role Go leaves genuinely empty.

## GitHub Actions

```yaml
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
          cache: true
      - run: test -z "$(gofmt -l .)"
      - run: go vet ./...
      - uses: golangci/golangci-lint-action@v6
      - run: go test -race -covermode=atomic -coverprofile=cover.out ./...
      - name: Coverage gate
        run: |
          pct=$(go tool cover -func=cover.out | tail -1 | awk '{print $3}' | tr -d '%')
          echo "total coverage: $pct%"
          [ "${pct%.*}" -ge 80 ] || { echo "below 80% threshold"; exit 1; }
```

## Roles

| Role | Command |
|---|---|
| Format | `test -z "$(gofmt -l .)"` |
| Lint | `go vet ./...`, plus golangci-lint for the wider rule set |
| Type check | Covered by the compiler during `go build` / `go test` |
| Test + coverage | `go test -race -covermode=atomic -coverprofile=cover.out ./...` |
| Boundary enforcement | `internal/` packages and package-level exports, at compile time. `depguard` via golangci-lint for rules `internal/` can't express |

## Notes

- **`gofmt -l .` exits 0** whether or not it finds unformatted files — it only prints them. Wrapping it in `test -z "$(...)"` is what makes the step fail.
- **Go has no built-in coverage threshold**, so the gate parses `go tool cover -func` output. `${pct%.*}` truncates the decimal for integer comparison.
- **`-covermode=atomic` is required alongside `-race`**; the default `set` mode is not race-safe.
- **`internal/` is compile-time enforced**: a package under `internal/` is importable only from within the tree rooted at its parent. Reach for it before reaching for a lint rule.
