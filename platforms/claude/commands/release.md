---
description: Prepare a release with changelog, version bump, and release notes
argument-hint: [version hint (optional)]
disable-model-invocation: true
---

Use the `@git-manager` subagent to prepare a release for this project. Analyze the commit history since the last tag to determine the appropriate version bump and generate release notes.

Recent tags:
!`git tag --sort=-version:refname | head -5`

Commits since last tag:
!`if git describe --tags --abbrev=0 >/dev/null 2>&1; then git log "$(git describe --tags --abbrev=0)"..HEAD --oneline; else git log --oneline -20; fi`

$ARGUMENTS
