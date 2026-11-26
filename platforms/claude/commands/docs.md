---
description: Generate or update project documentation
argument-hint: [doc type or target (optional)]
context: fork
disable-model-invocation: true
---

Load the `doc-templates` skill, then generate or update documentation for this project. Read the source code and existing documentation to ensure accuracy.

If no specific documentation type is requested, assess what documentation exists and what's missing, then create the most impactful additions and list the rest as suggestions in your report.

This runs in a fork with no conversation history. Work from the scope below; if it leans on context that is not here, stop and report what is missing rather than guessing.

$ARGUMENTS
