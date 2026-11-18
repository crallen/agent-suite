---
name: ticket-writing
description: Ticket writing for JIRA/Linear — turn a spec, requirements, or conversation into tickets a human can scan quickly. Load when drafting stories, tasks, subtasks, or bug reports, when splitting a spec into tracker tickets with testable acceptance criteria, or when rewriting a ticket that is hard to read.
---

# Ticket Writing

Turn a spec, a set of requirements, or a conversation into JIRA or Linear tickets, or rewrite an existing one. A ticket is read by a busy human in under a minute — on a board, in a standup, mid-review — so every rule here serves scannability: the reader learns what the work is, why it matters, and how to tell it is done, without opening anything else.

## Core Principles

- **One ticket, one outcome.** A ticket describes a single shippable change. When the description needs "and also", it is two tickets. When production waits on a staging soak, split per environment and link the two with Depends on.
- **Summary first.** Open with one or two plain sentences saying what is different once the ticket ships and why that matters, written so someone from another team could repeat it. Background the reader needs to follow the change comes after, under Context.
- **Acceptance criteria are observable.** Each item under Done when is a check a reviewer can run and answer yes or no — a behavior, a response, a rendered state. A criterion no one can check is a wish, not a criterion.
- **Link, never paste.** Cite the spec or discussion by link or path. The ticket carries a self-contained summary; the link carries the depth.
- **Outcome over implementation.** Describe the result the work must produce. Name an implementation detail in prose only when it is a real constraint ("must reuse the existing auth middleware"), and name it as a constraint.
- **One thread at a time.** When a ticket spans environments or parties, group What changes by that axis, so the reader follows staging start to finish before production begins.
- **The description states the plan.** It says what will be true when the ticket is done. Work already finished elsewhere goes under Already done elsewhere with its link, and progress goes in comments. When the plan changes, rewrite the affected sentence rather than annotating it.
- **Subtasks stand alone.** A subtask follows the same template. Its Summary states its slice in plain words, so a reader who lands on it from a board knows what it does without opening the parent, and its Done when checks only that slice.
- **Plain register.** Tickets follow the Register rules in the `doc-templates` skill: name the mechanism, not a metaphor for it, and cut emphasis that adds nothing. Bullets are plain sentences; bold marks section labels.

## Names and Identifiers

A ticket full of identifiers reads as a lookup table to its author and as noise to everyone else. Prose names things; Reference maps those names to identifiers.

- **One name per thing.** Give each system, service, and environment a plain name at first use, with a few words on what it is when the reader may not know ("the orders replica, a read-only copy of the orders database"), and use only that name afterward. Where two things share a word, qualify every use: "the reporting service" and "the reporting database", never a bare "reporting".
- **Identifiers live in Reference.** IDs, CIDRs, ARNs, file paths, zone IDs, and PR numbers go in the closing Reference section, keyed by the plain names the prose uses. Refer to a thing by its name, not its address: "every host in the reporting network", not `198.51.100.0/24`. Three kinds stay in place: the source link stays in Context, a ticket key stays on the line that cites it, and prose may carry an identifier a Done when item acts on — the hostname it connects to, the command it runs.

## From Spec to Tickets

1. **Collect the source.** A spec file, a requirements list, or the conversation so far. Done when the goal fits in one sentence.
2. **List the outcomes.** Each independently shippable, user-visible change is a candidate ticket. Internal work (a refactor, a migration) earns its own ticket only when it ships alone.
3. **Slice vertically.** Each ticket cuts through every layer its outcome needs — UI, API, storage together. "Build the endpoints" plus "build the UI" leaves nothing shippable until both land.
4. **Order by dependency.** When a ticket needs another to land first, record the blocker in its Depends on line and sequence the list accordingly. Record only blockers that genuinely gate the work: the Depends on lines form the task graph `spec-implementation` works from, and a false edge serializes work that could run in parallel. A prefactor that makes the change easy is its own ticket, first, blocking the tickets it eases.
5. **Check coverage.** Done when every requirement in the source appears in exactly one ticket, every ticket traces back to the source, and anything deliberately excluded sits on an Out of scope line.
6. **Read it back.** Read each ticket's title, Summary, and Done when alone. Done when those three say what changes and how to tell it worked, and every identifier outside Reference is one the Names and Identifiers rules keep in place.

**A wide refactor is the exception to vertical slicing.** One mechanical change whose effect fans across the codebase (renaming a column, retyping a shared symbol) breaks every call site at once, so no vertical slice lands green. Sequence it as expand, migrate, contract: one ticket adds the new form beside the old; one ticket per batch of call sites (per package or directory) migrates them, each blocked by the expand; a final ticket deletes the old form, blocked by every batch.

Most bug fixes and small features are a single ticket — splitting is for specs and multi-outcome requirements, never a quota.

When drafting more than one ticket, separate the drafts with a horizontal rule (`---`) so each reads as its own paste-ready unit.

## Story/Task Template

```
Title: Move staging month-end reports onto the orders replica

**Summary**
Month-end reports run against the orders database and slow checkout while
they run. After this, the reporting service in staging reads from the
orders replica, a read-only copy of the orders database, so reports no
longer compete with checkout.

**Context**
The orders replica already stays within seconds of the orders database,
which reports tolerate. Only its access rule and the reporting service's
connection setting are missing.
Spec: docs/specs/2026-08-14-reporting-replica.md

**What changes**
- The orders replica accepts connections from the reporting network
- The reporting service connects to the orders replica

**Done when**
- [ ] A month-end report completes with no queries on the orders database
- [ ] Hosts outside the reporting network are refused by the orders replica
- [ ] Reports match the previous month-end run row for row

**Already done elsewhere**
PROJ-139 added replica lag alerts.

**Out of scope**
Production, which follows in PROJ-145 after a staging month-end run.

**Reference**
| Item | Value |
|---|---|
| Orders replica host | `orders-ro.staging.example.com` |
| Reporting network | `198.51.100.0/24` |
| Connection setting | `deploy/staging.yaml`, `db.url` |
```

**Title**: imperative verb, names the outcome, roughly 70 characters or fewer, and understandable alone on a board — "Move staging month-end reports onto the orders replica", never "Replica work" or "Update db.url".

**Sections**: Summary is one or two sentences. Context is 2–3 sentences of background plus the source link, and is dropped when the Summary leaves nothing to explain. What changes is the scope in a few lines. Done when runs 3–7 checkboxes; more than 7 signals the ticket wants splitting. Already done elsewhere, Out of scope, Depends on, and Reference appear only when they have content — an empty section is deleted, never filled with "N/A".

## Bug Template

```
Title: Transactions list shows stale totals after applying a filter

**Environment**
Production, web app v2.41, Chrome 127 on macOS

**Steps to reproduce**
1. Open the transactions list
2. Apply the "last 30 days" filter
3. Compare the totals row against the visible rows

**Expected**
Totals row sums the filtered rows.

**Actual**
Totals row still sums the unfiltered list.

**Evidence**
Screenshot attached. `GET /api/transactions/summary` is called without the
filter params (network log below) — likely lead, unverified.

**Impact**
Finance reads wrong monthly totals from every filtered view.
```

**Title**: the symptom, not the diagnosis — "shows stale totals", never "summary endpoint drops filter params". A diagnosis may be wrong; put it in Evidence, marked as a lead.

**Sections**: Steps to reproduce are numbered and minimal — the shortest path that shows the bug. Expected and Actual are one sentence each. Impact says who is affected and how badly; it is what sets priority, so it earns a concrete claim.

## Platform Notes

- **Linear** renders the templates above as written — markdown, including checkboxes.
- **JIRA** turns markdown checkboxes into literal `[ ]` text, both from older wiki-markup editors and when markdown is sent through the API. Write Done when as a plain `-` list there.
- Keep formatting to bold labels, lists, code spans, and the two-column table Reference uses. Where a table will not render, write Reference as `name: value` lines.
- Priority, estimate, assignee, and labels are tracker fields, set in the tracker — they stay out of the ticket body.

## Anti-Patterns

| Anti-pattern | Instead |
|---|---|
| First description line restating the title | Open with the Summary |
| Emoji, headings over one-line sections | Plain prose; delete empty sections |
