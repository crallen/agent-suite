# Node / TypeScript

Fills all five roles explicitly — nothing in the language enforces boundaries or checks types at build time, so both need their own step.

## GitHub Actions

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npx depcruise src --config .dependency-cruiser.js

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm test -- --coverage
      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run build
```

## GitLab CI

```yaml
variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .npm/
    - node_modules/

lint:
  stage: lint
  script:
    - npm ci
    - npm run lint
    - npm run typecheck
    - npx depcruise src --config .dependency-cruiser.js

test:unit:
  stage: test
  script:
    - npm ci
    - npm test -- --coverage
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
```

## Roles

| Role | Command |
|---|---|
| Format | `prettier --check .`, usually folded into `npm run lint` |
| Lint | `eslint` |
| Type check | `tsc --noEmit` |
| Test + coverage | `npm test -- --coverage`; threshold in Jest `coverageThreshold` or Vitest `coverage.thresholds` |
| Boundary enforcement | dependency-cruiser or `eslint-plugin-boundaries` — nothing in the language enforces it |

## Notes

- **The coverage gate lives in the runner config, not the CI file.** With a threshold configured, `npm test -- --coverage` exits nonzero on its own; the CI file only uploads the report.
- **`npm ci`, not `npm install`** — it installs from the lock file and fails when the lock and manifest disagree, which is the determinism the pipeline wants.
- **dependency-cruiser covers both roles at once**: forbidden-import rules and `no-circular` live in the same config, so one step enforces direction and acyclicity.
