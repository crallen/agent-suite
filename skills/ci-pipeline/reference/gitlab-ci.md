# GitLab CI

Platform mechanics. For the job steps themselves, read the stack file for the project's language.

## Stages and Cache

```yaml
stages:
  - lint
  - test
  - build
  - deploy

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .cache/          # point at the ecosystem's download directory

lint:
  stage: lint
  script:
    - # format, lint, typecheck, boundary check — see reference/<stack>.md

test:
  stage: test
  script:
    - # test runner with coverage, gated at the project's threshold
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

build:
  stage: build
  script:
    - # build command
  artifacts:
    paths:
      - dist/
```

## Notes

- **`coverage:` reports, it does not gate.** The regex scrapes a percentage out of job output for GitLab's UI and merge-request widget. The actual gate is the test runner's own threshold flag exiting nonzero — see the stack file.
- **`cache:key` on the ref slug** keeps branches from evicting each other's caches. Use `key:files:` against the lock file when you want the cache to survive across branches with identical dependencies.
- **Cobertura** is the widely supported coverage report format; most runners emit it directly or via a converter.
- Stages are a hard barrier: every job in `lint` finishes before `test` starts. Use `needs:` to opt individual jobs out of that ordering when they don't depend on the whole previous stage.
