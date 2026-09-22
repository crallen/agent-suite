# Validator hardening and settings checks

## Goal

Make the tooling catch the classes of defect the 2026-09-22 suite review found by
hand: unparsed frontmatter, unknown keys, color collisions, index mentions that
match by accident, injection hazards, a missing or stale settings file, and link
drift. Checks run before a commit lands, not after CI notices, and the validator
has one parsing path instead of two.

## Context

- **`scripts/validate-config.py`** runs 13 checks from a registry in `main()`.
  Frontmatter parsing branches on whether PyYAML imported; the fallback scanner
  treats `model: sonnet # pinned…` as the literal value and accepted the invalid
  frontmatter fixed in commit 6da3f76. Locally PyYAML is absent; CI installs it,
  so the two never run the same checks.
- **`check_index`** verifies existence-to-mention with `if s not in text`, a
  substring test. `why`, `test`, and `docs` can never be reported missing.
- **No key validation.** Keys in use are stable: Claude agents use `name`,
  `description`, `tools`, `disallowedTools`, `skills`, `memory`, `model`,
  `mcpServers`, `color`; Claude commands `description`, `argument-hint`, `agent`,
  `context`, `disable-model-invocation`; OpenCode agents `description`, `mode`,
  `permission`, `color`, `hidden`; OpenCode commands `description`, `agent`,
  `subtask`; skills `name`, `description`, `argument-hint`.
- **Colors:** Claude collides twice (red: code-reviewer and security-analyst; cyan:
  documenter and frontend-engineer). OpenCode's fourteen hex values are unique;
  tech-lead has none. Claude accepts only its named palette, not hex.
- **No hooks in either repo.** `uv` is installed at `~/.local/bin/uv`; system
  Python is 3.14 with no yaml module and no distro package installed.
- **Dotfiles side:** `make check` runs `scripts/links.py` then the suite validator.
  `seed-settings` runs only from `make install`. Nothing verifies
  `claude/.claude/settings.json` afterwards, which is why this machine has had no
  deny list since 2026-09-09.
- **Three identical inventory functions** in the validator and a docstring saying
  "two agent-suite configs".

## Decisions

- YAML via a PEP 723 script header and a `uv` shebang; the fallback parser is deleted.
- Color uniqueness enforced on both platforms; the two Claude collisions are fixed.
  If the Claude roster ever exceeds the palette, uniqueness downgrades to a warning.
- `make check` verifies `settings.json` exists and carries every `permissions.deny`
  entry from the suite's example. Other keys stay machine-local and unchecked.
- Pre-commit hooks in both repos, path-filtered, wired by `make install`.

## Approach

Two branches, one per repo, landed suite first since the dotfiles hook calls into
it.

In agent-suite: convert the validator to a PEP 723 script run by `uv`, delete the
fallback parser, add four checks to the registry (keys, colors, index tokens,
injection lines), collapse the inventory functions, and add `.githooks/pre-commit`.
CI switches from `pip install pyyaml` to `astral-sh/setup-uv`.

In dotfiles: `scripts/links.py` grows a settings check, `make install` sets
`core.hooksPath` in both repos, and a tracked `.githooks/pre-commit` runs
`make check` when a commit touches a suite package or the submodule pointer. The
settings file on this machine gets seeded as part of landing.

## Components

**agent-suite, `scripts/validate-config.py`**

- **PEP 723 header and `uv` shebang.** First lines become
  `#!/usr/bin/env -S uv run --script` with a `# /// script` block declaring
  `requires-python = ">=3.12"` and `dependencies = ["pyyaml"]`. The
  `try: import yaml` block and the fallback scanner in `parse_frontmatter` are
  deleted. The docstring's "two agent-suite configs" becomes "the suite and its
  three platform views".
- **One inventory function.** `claude_skills`, `opencode_skills`, `codex_skills`
  collapse into `skill_dirs(root)`.
- **`check_frontmatter_keys`.** A dict of allowed keys per artifact type, with
  `name` and `description` required everywhere and `disable-model-invocation`
  required on Claude commands (moves here from `check_command_invocation`).
  Unknown key fails with the file and key named. `tools` and `disallowedTools`
  values are split on commas and checked against a `KNOWN_TOOLS` constant plus an
  `mcp__` prefix rule; the constant is filled from the Claude Code tools reference
  at implementation time, which also settles the routing spec's open question
  about Glob and Grep.
- **`check_colors`.** Claude agents: value must be in a `CLAUDE_COLORS` constant
  copied from the docs, and unique across the roster. OpenCode agents: value must
  match `#[0-9a-f]{6}`, be present, and be unique. Warning downgrade for palette
  overflow, with a comment saying so.
- **`check_index` mention test.** `if s not in text` is replaced by a regex that
  matches the identifier only as a backticked token: `` `name` ``, `` `/name` ``,
  `` `/name args` ``, `` `@name` ``, or `` `$name` `` for Codex. Loose-mention
  cases that surface get fixed in the index, not by loosening the regex.
- **`check_injection_lines`.** Any line starting with `` !` `` in `skills/**/*.md`
  or `platforms/*/agent*/*.md` fails unless inside a fenced code block. Commands
  are exempt, since injection is their feature.
- Registry in `main()` gains the four entries.

**agent-suite, hooks and CI**

- `.githooks/pre-commit`: POSIX sh. If `git diff --cached --name-only` matches
  `^(skills|platforms|scripts)/`, exec `scripts/validate-config.py -q`; otherwise
  exit 0. Executable bit tracked.
- `.github/workflows/validate.yml`: `setup-python` and `pip install pyyaml`
  replaced by `astral-sh/setup-uv` (version verified at implementation), then
  `uv run scripts/validate-config.py`.
- `AGENTS.md` Validating section: `uv` is the one prerequisite; mention the hook.
- `platforms/claude/agents/security-analyst.md` and `frontend-engineer.md`: new
  colors from the palette. `platforms/opencode/agent/tech-lead.md`: a hex color.

**dotfiles**

- `scripts/links.py`: new `check_settings()` called from `main()` after
  `check_live`. Skips with a note if `~/.claude/skills` is not stowed. Fails if
  `claude/.claude/settings.json` is missing, with the hint "run make
  seed-settings". Otherwise loads both files with `json` and fails listing every
  `permissions.deny` entry present in the example but absent from the live file.
- `Makefile`: `seed-settings` listed in help. New `hooks` target sets
  `core.hooksPath .githooks` in this repo and in `agent-suite`; `install` calls it
  after the submodule checkout. `suite-check` gains a `command -v uv` guard with
  an install hint. `check` prints a warning when `core.hooksPath` is unset.
- `.githooks/pre-commit`: if staged paths match `^(claude|codex|opencode)/` or
  equal `agent-suite`, run `make check -s`; otherwise exit 0.
- `CLAUDE.md` in dotfiles: "Managing it" names the hook and the `uv` prerequisite;
  the settings paragraph says `make check` now verifies the file.

## Testing

Each check is proven by breaking it once, on a scratch branch, then reverting.

- **Parser:** with `uv` absent from PATH, expect a clear shebang failure, not a
  traceback. With `uv` present, `model: sonnet # pinned…` parses to `sonnet`.
- **Keys:** add `disallowedtools:` (lowercase) to an agent; expect a failure
  naming file and key. Add `tools: Read, MultiEdit`; expect `MultiEdit` rejected.
- **Colors:** before the agent edits, the check fails twice on Claude; after, it
  passes. Two OpenCode agents on the same hex; expect failure.
- **Index tokens:** remove the `why` row from `CLAUDE.md`; expect "exists but is
  never mentioned". Restore.
- **Injection:** a line `` !`date` `` in a skill body fails; the same line inside
  a fence passes.
- **Hook, suite:** stage the broken-key edit and commit; refused. Stage a
  `README.md`-only change; no validator run, normal commit.
- **Settings:** move `settings.json` aside; `make check` fails with the seed hint.
  Restore, delete one deny entry; fails naming it. Restore; passes.
- **Hook, dotfiles:** commit under `tmux/`; silent. Commit under `claude/`;
  `make check` runs.
- **CI:** the suite PR's own workflow passes on `uv`.
- **This machine:** `~/.claude/settings.json` exists and `make check` is clean.

## Risks & Open Questions

- **Risk:** `uv` becomes a hard prerequisite. Accepted; installed here, one line
  in CI, and the alternative was a hand-rolled YAML subset that misparsed real files.
- **Risk:** hooks are per-clone config; a fresh machine has none until
  `make install`. Mitigated by `check` warning when unset.
- **Risk:** `make check` on package-touching dotfiles commits adds about a second
  and probes `~`. Acceptable; the path filter keeps it off unrelated commits.
- **Risk:** the Claude palette is small. Eight agents fit; the warning downgrade
  covers growth.
- **Open:** `KNOWN_TOOLS` contents, filled from the docs at implementation. If
  Glob and Grep are gone, the read-only agents' `tools:` lines shrink in the same
  commit.

## Task Checklist

**agent-suite, branch `feat/validator-hardening`**
- [ ] `scripts/validate-config.py`: PEP 723 block and `uv` shebang; delete the
      yaml fallback and the scanner branch of `parse_frontmatter`; fix the docstring.
- [ ] Collapse the three skill inventory functions into `skill_dirs(root)`.
- [ ] Add `check_frontmatter_keys` with per-type allowlists and `KNOWN_TOOLS`
      filled from the Claude Code tools reference.
- [ ] Add `check_colors` with `CLAUDE_COLORS` from the docs, hex validation for
      OpenCode, uniqueness on both, warning-downgrade comment.
- [ ] Replace the substring mention test in `check_index` with the backticked-token
      regex, including the `$name` Codex form.
- [ ] Add `check_injection_lines` over skills and agent bodies, fence-aware.
- [ ] Register the four checks in `main()`.
- [ ] Recolor `security-analyst.md` and `frontend-engineer.md`; add a hex color to
      `platforms/opencode/agent/tech-lead.md`.
- [ ] If `KNOWN_TOOLS` excludes Glob/Grep, trim `tools:` on the four read-only
      Claude agents and the agent-authoring examples.
- [ ] Create `.githooks/pre-commit`, executable, path-filtered.
- [ ] `.github/workflows/validate.yml`: swap to `astral-sh/setup-uv` and `uv run`.
- [ ] `AGENTS.md`: Validating section mentions `uv` and the hook.
- [ ] Run the break-and-revert tests; validator clean; push; CI green.

**dotfiles, branch `feat/check-settings-and-hooks`**
- [ ] `scripts/links.py`: add `check_settings()`; call it from `main()`.
- [ ] `Makefile`: list `seed-settings`; add `hooks`; call it from `install`; `uv`
      guard in `suite-check`; hooksPath warning in `check`.
- [ ] Create `.githooks/pre-commit`, executable, path-filtered, running
      `make check -s`.
- [ ] `CLAUDE.md`: update "Managing it" and the settings paragraph.
- [ ] Run `make seed-settings` and `make hooks` on this machine; `make check` clean.
- [ ] Run the settings and hook tests.
- [ ] Bump the submodule pointer once the suite branch merges; commit and push.
