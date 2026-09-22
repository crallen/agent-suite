---
name: git-conventions
description: Commit, branch, and pull-request rules — the project's own conventions first, then Conventional Commits with the type-to-bump mapping, short bodies, no attribution footers, and filesystem safety for git work. Load before committing, branching, opening a pull request, or preparing a release.
---

# Git Conventions

## Project Conventions Win

A project with its own commit, branch, or PR conventions overrides this skill.
Look for a stated rule in `CLAUDE.md` or `AGENTS.md` first; where none is written
down, read `git log` and the existing branch names and follow the pattern already
there. Everything below is the default for a project that has not settled its own.

## Commits

Conventional Commits: `<type>(scope): description`, then an optional body and
footers. Subject under 72 characters, lowercase, imperative, no period. Scope names
stay consistent within a project.

Type decides the version bump: `feat` is minor; `fix` and `perf` are patch;
`docs`, `style`, `refactor`, `test`, `build`, `ci`, and `chore` bump nothing;
`revert` varies. A breaking change takes `!` after the type or scope and a
`BREAKING CHANGE:` footer with migration instructions, and bumps major.

The body is a short summary of why, a few lines at most, and only when the subject
alone does not carry it. Most commits need no body. Footers are for issue
references (`Closes #42`) and breaking changes. Never add a `Co-Authored-By: Claude`
trailer, a "Generated with Claude Code" line, or a session link.

```
feat(auth): add OAuth2 login with Google provider

Google is the identity provider most requested by enterprise
customers, and supporting it removes the main blocker on SSO
onboarding.

Closes #128
```

One logical change per commit, formatting separate from function, no generated
files or IDE configuration, never a secret. A fixup of a recent commit uses
`git commit --fixup` and is squashed before merging.

## Branches

`<type>/<short-description>`: `feat/user-auth`, `fix/null-pointer-login`,
`release/v1.2.0`. `main` is always deployable and never committed to directly;
branches are short-lived and deleted after merging.

## Pull Requests

- Title in the commit-subject format.
- The description is a few sentences or a handful of bullets covering what changed
  and why. The diff and commit list carry the detail; the description orients the
  reviewer.
- Describe only what the PR contains: no "things to verify", no follow-up lists.
  Work the PR does not do belongs in an issue.
- No boilerplate sections unless the repo's template asks for them, and no
  attribution footer or session link.

## Filesystem Safety

Git work is not filesystem manipulation.

- Never run destructive filesystem commands (`rm`, `rm -rf`, moving, overwriting,
  or truncating files) inside or against the working tree.
- Never create temporary files or directories inside the working tree to test or
  verify behavior. If a scratch path is genuinely needed, use a system temp
  directory outside the repo, never a path that shadows a real repo directory.
- Verify with non-mutating, read-only commands. `git check-ignore <path>` matches
  a path string and does not require the path to exist; never create a file to
  test ignore rules.
- If a verification appears to require creating or deleting files on disk, stop
  and report instead of proceeding.
