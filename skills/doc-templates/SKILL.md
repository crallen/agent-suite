---
description: Templates and structure for READMEs, API documentation, changelogs, and inline code documentation, plus the register and naming rules for prose humans read (name the mechanism, not a metaphor for it) — ADRs defer to the domain-modeling skill
---

# Documentation Templates

Reusable templates for common documentation artifacts: READMEs, API docs, changelogs, and inline code comments. ADRs defer to the `domain-modeling` skill.

## README Template

```markdown
# Project Name

One-sentence description of what this project does and who it's for.

## Quick Start

Prerequisites:
- Dependency 1 (version)
- Dependency 2 (version)

\```bash
# Clone and install
git clone <repo-url>
cd <project>
<install-command>

# Run
<run-command>
\```

## Usage

Brief usage examples showing the most common operations.

\```bash
# Example 1: Description
<command or code>

# Example 2: Description
<command or code>
\```

## Project Structure

\```
project/
├── src/           # Source code
├── test/          # Tests
├── docs/          # Documentation
└── ...
\```

## Development

\```bash
# Run tests
<test-command>

# Run linter
<lint-command>

# Build
<build-command>
\```

## Contributing

Brief contribution guidelines or link to CONTRIBUTING.md.

## License

<License type>. See [LICENSE](LICENSE) for details.
```

## API Documentation Template

For each endpoint or public function:

```markdown
### `METHOD /path/to/endpoint`

Brief description of what this endpoint does.

**Authentication**: Required / Optional / None

**Parameters**:

| Name | Type | In | Required | Description |
|------|------|----|----------|-------------|
| id   | string | path | yes | Resource identifier |
| limit | integer | query | no | Max results (default: 20, max: 100) |

**Request Body** (if applicable):

\```json
{
  "field": "value",
  "nested": {
    "key": "value"
  }
}
\```

**Response** `200 OK`:

\```json
{
  "data": { ... },
  "meta": {
    "total": 42,
    "page": 1
  }
}
\```

**Errors**:

| Status | Code | Description |
|--------|------|-------------|
| 400 | INVALID_INPUT | Request body validation failed |
| 401 | UNAUTHORIZED | Missing or invalid authentication |
| 404 | NOT_FOUND | Resource does not exist |

**Example**:

\```bash
curl -X GET https://api.example.com/resource/123 \
  -H "Authorization: Bearer <token>"
\```
```

## Architecture Decision Records (ADRs)

ADRs follow the `domain-modeling` skill — it owns the three-part gate for when a decision deserves one, the `docs/adr/` layout, and the canonical minimal format (a title plus 1-3 sentences, with optional Status / Considered Options / Consequences sections). Load it before writing an ADR.

## Changelog Template

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- New feature description (#issue-number)

### Changed
- Modified behavior description (#issue-number)

### Fixed
- Bug fix description (#issue-number)

### Removed
- Removed feature description (#issue-number)

## [1.0.0] - YYYY-MM-DD

### Added
- Initial release features
```

## Code Comment Guidelines

### When to Comment

- **WHY, not WHAT**: The code shows what happens. Comments explain why.
- **Non-obvious behavior**: Workarounds, business rules, performance tricks.
- **Important context**: Links to specs, issue numbers, external docs.
- **Public API**: Document parameters, return values, error conditions, and usage examples.

### When NOT to Comment

- Don't restate the code: `i++ // increment i` adds nothing.
- Don't leave commented-out code. Delete it; git has the history.
- Don't use comments as section dividers where functions would be better.
- Don't write TODOs without an associated issue or ticket number.

### Format

```
// Good: Explains WHY
// Rate limit is 100 req/min per the API docs (https://example.com/limits).
// We use 80 to leave headroom for retries.
const maxRequestsPerMinute = 80

// Bad: Restates WHAT
// Set max requests to 80
const maxRequestsPerMinute = 80
```

## Register

Applies to every prose surface a human reads: comments, README and API docs,
changelog entries, and commit bodies.

Name the mechanism, not a metaphor for it. Colloquial phrasing reads as
precision but carries less information: it gestures at what happened instead of
saying it.

| Instead of | Write |
|---|---|
| "blows up with a `SettingsError`" | "raises `SettingsError`" |
| "clobbers the value" | "overwrites the value" |
| "so keep it honest" | "so the entry stays current" |
| "fails loudly" | "fails", or "exits non-zero" |
| "under the hood" | name the layer actually doing the work |

Cut emphasis that adds nothing: "before this validator *ever* runs" says no more
than "before this validator runs".

Keep the words that are load-bearing, though. "A real value here **silently**
becomes the image tag" earns its adverb — the absence of any error is the whole
reason the surrounding check exists.

## Naming

The same standard applies to identifiers, and vague naming does more damage
there, because a reader cannot skip a name the way they can skip a comment.

- Name a test helper for the scenario it represents, not for the fact that it
  fails: `raise_access_denied`, not `_boom`.
- Do not alias a well-known framework fixture to a vaguer name. `monkeypatch`
  used directly reads as what it is; returning it as `clean_env` produces
  `clean_env.setattr(...)`, which describes neither the environment nor the
  patching.
- If an assertion refers to an identifier by name, the name should make the
  assertion self-explanatory without a comment.
