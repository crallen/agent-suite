---
name: retro-methodology
description: Session retrospective aimed at the agent's environment rather than the code — find the friction in a finished session and propose the navigation pointer, automated check, review standard, or steering-file cut that removes it. Load when asked for a retro or retrospective on a coding session, or after a build or bug fix that went sideways.
---

# Retro Methodology

A **retrospective** looks back over one coding session and proposes changes to the **environment** the agent worked in: the steering files, checks, standards, and tooling that shape every future run. The code the session produced is out of scope; review owns that.

The output is a ranked list of proposals. Nothing is edited until the user picks.

## Steps

1. **Read the primary sources.** The session the user names, or the current one by default: the conversation or its log, the diff and commits it produced, and the steering files that were loaded (`CLAUDE.md`, `AGENTS.md`, any skill it used). Done when you can replay the session's turning points without guessing.

2. **List the friction.** Every moment the session lost time or went wrong, each as one concrete event with its evidence: a correction from the user, a wrong turn, the same lookup made twice, a failure caught late, an expensive call, a fact the agent needed and could not reach. Done when every correction and every wrong turn in the session is on the list.

3. **Route each event to a category** from the table below, and name the specific change. An event that fits no category is recorded as unrouted, never stretched to fit.

4. **Present the proposals**, most severe first. Each one carries the event that motivates it, the change, where the change lives, and its rung from `coding-guardrails/reference/encode-lessons-in-structure.md`. Then stop for the user's pick.

## Categories

| Category | Reach for it when | Typical change |
|---|---|---|
| **Navigation** | The session took long to find a file or fact, or tripped on a hidden dependency between files | A **navigation pointer**: one line in a steering file naming the doc or module and when to read it |
| **Automated checks** | The agent made a mistake a machine could have caught, or the repo has no guardrail at all | A lint rule, type, test, pre-commit hook, or CI job |
| **Review standards** | Review missed a mistake that takes judgement to see | A rule added to, clarified in, or removed from the standards the reviewer reads |
| **Steering-file weight** | An always-loaded file is large, or carries rules that belong in review or in a check | Move the rule down: to a check, to review standards, or behind a pointer |
| **No-ops** | A steering instruction did not change what the agent did | Delete the sentence |
| **Tool economy** | A tool call was expensive for what it returned | A narrower command, a script, or a cheaper tool for that lookup |
| **Information access** | A fact the agent needed was out of its reach | Logs teed to a file, read-only access to the service, a doc checked into the repo |

## Rules for routing

**Read the repo's own checks first.** Look at its lint, typecheck, and test commands and its CI workflow before proposing a new check. A check that exists but is unwired or silently broken is the finding; a duplicate is not. A repo with no pre-commit hook and no CI job running those commands is a finding in itself.

**Mechanical violations get a mechanism.** A fixed pattern, a banned API, an import shape, or a file-location rule becomes a deterministic check, in whichever of the repo's existing tools makes it cheapest. Written standards are for judgement calls no check could make: cross-file consistency, fit with the surrounding style.

**Standards belong to review.** The implementing agent explores, writes, and debugs, so its context is the scarcest in the pipeline. The reviewer receives a diff and has room to spare. A rule the reviewer can enforce from the diff goes in the review standards (`CODING_STANDARDS.md` or the repo's equivalent), which `code-review-checklist` defers to, and stays out of the always-loaded steering files.

**Steering files are for pointers.** `CLAUDE.md` and `AGENTS.md` are paid for on every turn of every session. Keep them to navigation pointers and the few rules that must hold before any file is read. Look for an existing doc before proposing a new one.
