---
name: git-conventions
description: Conventional Commits format, branching model, short-summary commit and PR style, and git workflow rules for clean version control history
---

# Git Conventions

Rules for clean version control history: Conventional Commits format, branching model, and commit hygiene.

## Project Conventions Win

A project with its own commit, branch, or PR conventions overrides this skill — match the repo, not the defaults below. Look for a stated rule in `CLAUDE.md` or `AGENTS.md` first; where none is written down, read `git log` and the existing branch names and follow the pattern already there. Everything that follows is the default for a project that has not settled on its own.

## Conventional Commits Specification

Every commit message must follow this format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to use | Version bump |
|---|---|---|
| `feat` | A new feature or capability | minor |
| `fix` | A bug fix | patch |
| `docs` | Documentation-only changes | none |
| `style` | Formatting, whitespace, semicolons (no code change) | none |
| `refactor` | Code restructuring without behavior change | none |
| `perf` | Performance improvement | patch |
| `test` | Adding or correcting tests | none |
| `build` | Build system or external dependency changes | none |
| `ci` | CI configuration changes | none |
| `chore` | Maintenance tasks that don't modify src or test | none |
| `revert` | Reverts a previous commit | varies |

### Rules

1. **Subject line**: `<type>(scope): description` — max 72 characters, lowercase, imperative mood, no period.
2. **Scope** (optional): The area of the codebase affected. Use consistent scope names within a project (e.g., `auth`, `api`, `ui`, `db`).
3. **Body** (optional): A short summary of WHY — a few lines at most, and only when the subject alone doesn't carry it. Most commits need no body. Wrap at 72 characters. Separate from subject with a blank line.
4. **Footer** (optional): Reference issues (`Closes #42`), note breaking changes (`BREAKING CHANGE: description`), or add metadata.
5. **Breaking changes**: Add `!` after type/scope (`feat!: remove legacy API`) AND/OR add a `BREAKING CHANGE:` footer with migration instructions.
6. **No tool attribution**: never add a `Co-Authored-By: Claude` trailer, a "Generated with Claude Code" line, or a session link. The footer in rule 4 is for issue references and breaking changes only.

### Examples

A body carrying a why the subject can't, plus an issue footer:

```
feat(auth): add OAuth2 login with Google provider

Google is the identity provider most requested by enterprise
customers, and supporting it removes the main blocker on SSO
onboarding.

Closes #128
```

A breaking change — `!` on the subject and a `BREAKING CHANGE:` footer with migration instructions:

```
feat!: change API response format to JSON:API spec

BREAKING CHANGE: All API endpoints now return responses in JSON:API
format. The previous flat JSON format is no longer supported.
Clients must update their response parsing logic.

Migration guide: https://example.com/migration
```

## Branching Model

### Branch Naming

```
<type>/<short-description>
```

Examples:
- `feat/user-auth`
- `fix/null-pointer-login`
- `chore/update-deps`
- `docs/api-reference`
- `release/v1.2.0`

### Branch Rules

- `main` / `master` is always deployable. Never commit directly to it.
- Feature branches branch from and merge back to the main development branch.
- Delete branches after merging.
- Keep branches short-lived. Long-lived branches cause merge conflicts.

## Pull Requests

- Title follows the same `<type>(scope): description` format as a commit subject.
- The description is a short summary: a few sentences — or a handful of bullets — covering what changed and why. The diff and commit list already tell the detailed story; the description orients the reviewer, it doesn't retell the work.
- Describe only what the PR contains. No "additional things to verify", no follow-up TODO lists, no suggested next steps — that is work the PR doesn't do, and it belongs in an issue if it belongs anywhere.
- Skip boilerplate sections (test plans, checklists, headings) unless the repo's PR template asks for them.
- The description ends on its last real line. Never append a "Generated with Claude Code" footer or a session link — the body passed to `gh pr create` gets no attribution.

## Filesystem Safety

Git work is not filesystem manipulation.

- Never run destructive filesystem commands (`rm`, `rm -rf`, moving, overwriting, or truncating files) inside or against the working tree.
- Never create temporary files or directories inside the working tree to test or verify behavior. If a scratch path is genuinely needed, use a system temp directory outside the repo — never a path that shadows a real repo directory.
- Verify with non-mutating, read-only commands. In particular, `git check-ignore <path>` matches a path string and does not require the path to exist — never create a file or directory to test ignore rules.
- If a verification appears to require creating or deleting files on disk, stop and report instead of proceeding.

## Commit Hygiene

- One logical change per commit. Atomic commits are easier to review, revert, and bisect.
- Don't mix formatting changes with functional changes.
- Don't commit generated files, build artifacts, or IDE configuration.
- Never commit secrets, credentials, or private keys.
- If you need to fixup a recent commit, use `git commit --fixup` and squash before merging.
