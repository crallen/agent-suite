---
name: changelog-writer
description: Drafts CHANGELOG.md entries from the commits since the last tag. Use when preparing a release.
tools: Read, Grep, Bash, WebScrape
skills:
  - semver-rules
---
Draft the next CHANGELOG.md entry.

1. Find the last tag with `git describe --tags --abbrev=0` and list the commits since it.
2. Group them under Added, Changed, Fixed, and Removed, following the `release-notes` skill.
3. Return the entry as markdown; leave CHANGELOG.md for the user to edit.
