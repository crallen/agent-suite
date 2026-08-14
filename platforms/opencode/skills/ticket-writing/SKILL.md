---
name: ticket-writing
description: Ticket writing for JIRA/Linear — turn a spec, requirements, or conversation into tickets a human can scan quickly. Load when drafting stories, tasks, or bug reports, or when splitting a spec into tracker tickets with testable acceptance criteria.
---

# Ticket Writing

Turn a spec, a set of requirements, or a conversation into JIRA or Linear tickets. A ticket is read by a busy human in under a minute — on a board, in a standup, mid-review — so every rule here serves scannability: the reader learns what the work is, why it matters, and how to tell it is done, without opening anything else.

## Core Principles

- **One ticket, one outcome.** A ticket describes a single shippable change. When the description needs "and also", it is two tickets.
- **Why before what.** Open with 2–3 sentences of context: the problem or need, in the reader's terms. The description of the change comes second.
- **Acceptance criteria are observable.** Each criterion is a check a reviewer can run and answer yes or no — a behavior, a response, a rendered state. A criterion no one can check is a wish, not a criterion.
- **Link, never paste.** Reference the spec or discussion by link or path. The ticket carries a self-contained summary; the link carries the depth.
- **Outcome over implementation.** Describe the result the work must produce. Name an implementation detail only when it is a real constraint ("must reuse the existing auth middleware"), and name it as a constraint.
- **Plain register.** Tickets follow the Register rules in the `doc-templates` skill: name the mechanism, not a metaphor for it, and cut emphasis that adds nothing.

## From Spec to Tickets

1. **Collect the source.** A spec file, a requirements list, or the conversation so far. Done when the goal fits in one sentence.
2. **List the outcomes.** Each independently shippable, user-visible change is a candidate ticket. Internal work (a refactor, a migration) earns its own ticket only when it ships alone.
3. **Slice vertically.** Each ticket cuts through every layer its outcome needs — UI, API, storage together. "Build the endpoints" plus "build the UI" leaves nothing shippable until both land.
4. **Order by dependency.** When a ticket needs another to land first, record the blocker in its Depends on line and sequence the list accordingly.
5. **Check coverage.** Done when every requirement in the source appears in exactly one ticket, every ticket traces back to the source, and anything deliberately excluded sits on an Out of scope line.

Most bug fixes and small features are a single ticket — splitting is for specs and multi-outcome requirements, never a quota.

## Story/Task Template

```
Title: Add CSV export to the transactions list

**Context**
Finance reconciles transactions in a spreadsheet today and re-keys the data
by hand. Exporting what the list already shows removes that step.
Spec: docs/specs/2026-08-14-transaction-export.md

**What**
Add an "Export CSV" action to the transactions list that downloads the
current filtered view.

**Acceptance criteria**
- [ ] Export action appears on the transactions list for signed-in users
- [ ] Downloaded CSV contains the same rows and columns as the current filter
- [ ] An empty filter result downloads a CSV with headers only
- [ ] Exporting 10k rows completes without a timeout

**Out of scope**
Scheduled exports; XLSX format.

**Depends on**
PROJ-142 (filter state in the URL)
```

**Title**: imperative verb, names the user-visible outcome, roughly 70 characters or fewer, and understandable alone on a board — "Add CSV export to the transactions list", never "CSV work" or "Implement TransactionExportService".

**Sections**: Context is 2–3 sentences of why plus the source link. What is the scope of the change in a few sentences. Acceptance criteria run 3–7 checkboxes; more than 7 signals the ticket wants splitting. Out of scope and Depends on appear only when they have content — an empty section is deleted, never filled with "N/A".

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
- **JIRA**'s current editor accepts pasted markdown; older instances use wiki markup, where checkboxes may not survive the paste — a plain `-` list is the safe fallback.
- Keep formatting to bold labels, lists, and code spans — the subset both trackers render.
- Priority, estimate, assignee, and labels are tracker fields, set in the tracker — they stay out of the ticket body.

## Anti-Patterns

| Anti-pattern | Instead |
|---|---|
| The whole spec pasted into the description | 2–3 sentences of context plus a link |
| "Works correctly", "handles errors gracefully" as criteria | The observable check: "returns 422 with a field-level message on invalid input" |
| Prescribing the implementation ("add a UserExporter class") | The outcome; real constraints named as constraints |
| First description line restating the title | Open with why |
| One ticket per layer ("backend part", "frontend part") | Vertical slices — each ticket ships alone |
| Emoji, dense bolding, headings over one-line sections | Plain prose; delete empty sections |
| A ticket readable only next to the spec | A self-contained summary; the link is for depth |
