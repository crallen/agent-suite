---
description: CI/CD pipeline patterns for GitHub Actions and GitLab CI — stage order, architecture and coverage enforcement gates, and a procedure for determining the toolchain of a stack with no reference file yet. Load when building or reviewing a pipeline, adding quality gates, or working out which checks a stack needs.
---

# CI Pipeline

Design and review CI/CD pipelines: what runs, in what order, and which conventions the build *enforces* rather than merely reports.

The judgment lives here; the YAML lives in `reference/`. Read the platform file for the project's CI system and the stack file for its language:

| Reference | Contents |
|---|---|
| `ci-pipeline/reference/github-actions.md` | Workflow skeleton, per-ecosystem caching, matrix builds |
| `ci-pipeline/reference/gitlab-ci.md` | Stages, cache keys, coverage reports |
| `ci-pipeline/reference/node.md` | Node / TypeScript jobs and roles |
| `ci-pipeline/reference/go.md` | Go jobs and roles |
| `ci-pipeline/reference/rust.md` | Rust jobs and roles |

Working in a stack with no file above? Follow **Determining a Stack's Toolchain** and write what you verify to `ci-pipeline/reference/<stack>.md`, so the next run starts from it instead of rediscovering.

## CI Pipeline Principles

1. **Fast feedback** - Fail fast. Run linting and unit tests first, slow integration tests later.
2. **Deterministic** - Same commit, same result. Pin dependency versions, use lock files, cache deterministically.
3. **Parallel where possible** - Independent jobs should run concurrently.
4. **Minimal permissions** - Each job gets only the permissions it needs.
5. **Cache aggressively** - Dependencies, build artifacts, and Docker layers should be cached between runs.

## Pipeline Stages (in order)

```
lint -> test -> build -> deploy
 |       |               |
 |       +-- unit         +-- staging
 |       +-- integration  +-- production
 +-- format
 +-- typecheck
 +-- boundaries
```

### Stage 1: Lint & Check
- Code formatting
- Linting
- Type checking, where it isn't already covered by the build
- Architecture rules (import direction and cycles — see `Enforcing Conventions`)
- Security scanning (dependency audit, SAST)
- Fastest stage. Catches most issues cheaply.

### Stage 2: Test
- Unit tests (fast, run first)
- Integration tests (slower, run after unit tests pass)
- Coverage measured and gated against the project's thresholds, not just reported

### Stage 3: Build
- Compile/bundle the application
- Build container images
- Generate artifacts

### Stage 4: Deploy
- Deploy to staging automatically
- Deploy to production with manual approval or after staging verification

## Enforcing Conventions

A convention that lives only in a review checklist decays. When a project agrees a rule a machine could check — the inward dependency direction in `backend-patterns`, a layer boundary, a module nothing else may import, a coverage floor — encode it so the build fails instead of a reviewer having to notice.

### Architecture rules

Prefer a boundary the compiler enforces over one a linter checks:

- **Go** — `internal/` packages and package-level exports; package cycles are a compile error.
- **Rust** — crate-level visibility and workspace splits; Cargo rejects crate cycles.
- **TypeScript, Python, JVM** — no compile-time equivalent, so the boundary needs a lint rule.

Where a lint rule is the only option:

| Rule | Tools |
|---|---|
| Import direction / forbidden imports | eslint `no-restricted-imports`, `eslint-plugin-boundaries`, dependency-cruiser (JS/TS); import-linter (Python); ArchUnit (JVM); `depguard` via golangci-lint (Go, for rules `internal/` can't express) |
| Import cycles | dependency-cruiser `no-circular`, `madge --circular` (JS/TS); import-linter (Python); ArchUnit (JVM) |

These are static and need no build, so they belong in Stage 1 alongside the other linters.

Add the rule when the boundary is agreed, not later. Retrofitting one onto an existing codebase means either a large cleanup or a graveyard of suppression comments; where violations already exist, baseline them and fail only on new ones.

### Coverage gates

Reporting a coverage number nobody gates on changes nothing. Configure the threshold where the runner can act on it so the run exits nonzero below target; the stack files give the mechanism per language. Take the per-category targets from `test-strategy`.

## Determining a Stack's Toolchain

The stage order above is language-independent — only the commands change. When the project's stack has no `reference/` file, derive one.

### 1. Identify the stack

Read the manifest at the repo root: `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `mix.exs`, `build.gradle(.kts)`, `pom.xml`, `Gemfile`, `composer.json`, `pubspec.yaml`, `*.csproj`, `deno.json`. A monorepo may hold several — each gets its own job.

### 2. Take the project's own commands first

Read, in order: existing CI config, `Makefile` / `justfile` / `Taskfile.yml`, the manifest's script or task section, `CONTRIBUTING.md`. Commands the project already runs beat any generic recommendation — the pipeline should run what a maintainer runs locally. Fill only the genuine gaps.

### 3. Fill each role

Map the five roles a pipeline needs onto the stack's tooling:

| Role | What to look for |
|---|---|
| Format | The language's canonical formatter, in `--check` mode |
| Lint | The standard static-analysis tool, plus its warnings-as-errors flag |
| Type check | A separate step only where types aren't already checked during build or test |
| Test + coverage | The test runner, and whether it can fail below a threshold |
| Boundary enforcement | A compile-time visibility mechanism first; a lint rule only if none exists |

Prefer first-party tooling that ships with the language toolchain — it needs no install step, versions with the compiler, and rarely breaks. Reach for third-party tools only for roles the toolchain leaves empty.

Where the language has one canonical formatter, a `--check` step is uncontroversial. Where the ecosystem has several competing linters, use whichever the project already has rather than introducing one.

### 4. Check what the compiler already enforces

Ask of the new stack what `Enforcing Conventions` asks of Go and Rust: does the language have a visibility or module mechanism that makes a boundary lint redundant? Answer that before adding a tool — a lint rule duplicating a compile error is pure pipeline latency.

### 5. Verify every command before writing it down

Do not write a flag from memory. For each command, confirm the tool exists, read its `--help`, and confirm the flag does what you intend.

Then prove the check can fail. Run it against a deliberately broken input — an unformatted file, coverage below threshold — and confirm a nonzero exit. A check that always passes is worse than no check: it reads as coverage in the pipeline and provides none. `gofmt -l .` exits 0 whether or not it finds unformatted files; `test -z "$(gofmt -l .)"` is the version that fails.

### 6. Write it down

Add `ci-pipeline/reference/<stack>.md` in the shape of the existing stack files: the job YAML, a roles table, and any role the stack leaves empty with a note on why. Record what you verified, not what you assumed.

## Toolchain Versions

Target the ecosystem's current supported release. "LTS" only means something in some ecosystems, so know which rule applies:

| Ecosystem | Target | How it works |
|---|---|---|
| Node | Active LTS | Even majors enter LTS each October. Current carries unreleased-feature risk; Maintenance LTS is an upgrade signal, not a resting place |
| Go | Latest stable | No LTS. Only the two most recent majors get security fixes, so one behind is the floor rather than the goal |
| Rust | `stable` channel | No LTS. Pin the channel and let the toolchain action resolve it |
| Python | Latest stable minor | No LTS. Each minor is supported roughly five years |
| Databases and services | Latest supported major | Postgres and peers support a major for about five years |

**Verify before pinning.** A version written from memory is stale the moment a release lands, and a stale pin in a template propagates into every project built from it:

```sh
curl -s https://nodejs.org/dist/index.json       # newest entry per major with lts != false
curl -s "https://go.dev/dl/?mode=json"           # stable releases, newest first
curl -s https://endoflife.date/api/python.json   # also postgresql, node, and most others
```

Pin the major in templates (`node:24-slim`, `go-version: '1.26'`) so patch releases arrive without an edit, and pin further — to a digest — in a production image where reproducibility outweighs convenience. Let Renovate or Dependabot raise the major bump as a reviewable PR instead of discovering it years later.

## Security in CI

- **Never echo secrets**. Use masked variables.
- **Prefer full SHA pinning** for third-party or security-sensitive actions. Major-version tags can be acceptable for official actions when your org accepts that tradeoff, but use them intentionally and review updates regularly.
- **Audit dependencies** as a CI step: `npm audit`, `go vuln check`, `cargo audit`.
- **Use OIDC** for cloud deployments instead of long-lived credentials.
- **Limit permissions** per job: `permissions: { contents: read }`.
