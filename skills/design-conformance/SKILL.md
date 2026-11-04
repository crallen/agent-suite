---
name: design-conformance
description: Judge whether a change fits the system's recorded design — ADR precedent, ownership, existing mechanisms, contract growth, spec scope — with every claim cited and a conditional path per plausible intent. Load when reviewing a pull request or branch against the ADRs, specs, or domain model, or when a change adds public contract surface (API fields, token claims, schema, events).
---

# Design Conformance

A design review asks one question: does this change fit the decisions the system
has already recorded? It is a separate axis from code quality and security, and
it runs on the **design record**, the written decisions, not on taste. Work the
steps in order; each ends on its completion criterion.

## Steps

### 1. Reconstruct the intent

Read the PR body, every commit message, and the whole diff. Write down:

- **Stated intent**: what the author says the change is for, quoted. Mark
  anything you infer beyond that as inference.
- **Concepts touched**: each domain concept, named in the project's own
  vocabulary from `CONTEXT.md` where it defines one.
- **Contract surface**: every addition or change other code or other teams can
  depend on: API fields and endpoints, token claims, schema columns and tables,
  events and message shapes, config keys read by another service, published
  types. Each item gets a `file:line`.

Done when every contract-surface item in the diff is listed with its location,
and the stated intent is quoted or recorded as absent.

### 2. Collect the design record

| Source | What it settles |
|---|---|
| `CONTEXT.md`, `CONTEXT-MAP.md` | vocabulary, and which context owns which responsibility |
| `docs/adr/` | decided cases: precedent, including rejected options |
| `docs/design/`, `docs/specs/` | goals, non-goals, and the contract a phase of work was allowed to add |
| `docs/runbooks/`, `README.md`, `AGENTS.md` | mechanisms the system already provides and how they are meant to be used |
| the workspace's cross-repo map, when its instructions name one | which repo owns a responsibility that spans services |

Read every ADR title. Read in full each ADR, spec, and design doc that touches a
concept from step 1, and search the record for each concept's term and its
synonyms. Note each ADR's status: a superseded or rejected ADR is history, and
the one that replaced it is the precedent.

Done when every record document touching a step-1 concept has been read in full,
or the record is confirmed absent. An absent record is a finding in its own right.

### 3. Run the checks

Apply each check to every concept and contract-surface item.

| Check | Question | Settled by |
|---|---|---|
| **Precedent** | Does an ADR decide this case, or one of the same shape? | an ADR whose reasoning covers the change |
| **Ownership** | Does the responsibility sit in the subsystem that owns it? | `CONTEXT.md` ownership, the cross-repo map |
| **Existing mechanism** | Does it rebuild something the system already provides? | a runbook, doc, or code path showing the mechanism |
| **Contract growth** | Does it add public surface with no recorded decision behind it? | an ADR or spec that authorizes the surface |
| **Scope** | Is it inside the goals of the spec it claims, or quietly new? | the spec's goals and non-goals |

Match precedent by the *reasoning* of a decision, not its nouns. An ADR that
moved `can_approve_refunds` out of the user profile and into a role, because a
permission stored as a profile attribute bypasses the role model, also decides a
later `approval_regions` profile field. The name differs; the shape is the same.

Done when each check has a result for each item: a cited conflict, a cited fit,
or "the record is silent".

### 4. Interrogate the intent

The author's need is the unknown; treat the change as a reasonable answer to a
question you have not yet heard. Enumerate the two to four plausible uses, say
which one the evidence favors and why, and give each a **conditional path**:
what the author does under that answer, what changes in the PR, and whether a
new ADR is needed.

A **blocking question** is one whose answer changes the verdict or the path.
Each one carries the citation that makes it blocking. A question whose answer
changes neither is not blocking; drop it.

Done when every plausible use has a path and every blocking question cites the
record.

### 5. Give the verdict

| Verdict | When |
|---|---|
| **fits** | Every check finds a cited fit, or a silence on surface that is easy to reverse. |
| **fits with conditions** | It fits once named, specific changes land: a missing doc row, a typed shape in place of a raw string, an ADR for surface the record already leans toward. |
| **conflicts** | An accepted ADR, ownership rule, or spec non-goal decides against the change under its evidenced intent. |
| **needs a decision** | The record is silent and the change adds hard-to-reverse contract surface, or reasonable intents lead to different verdicts. The outcome is an ADR before the merge. |

When the intent is unconfirmed and the paths diverge, give the verdict for the
use the evidence favors and mark it provisional on the blocking question.

## Citations

Every claim about the record cites `path:line` or a line range, with the decisive
phrase quoted briefly. A claim about an existing mechanism also cites the code or
runbook that provides it. A claim you cannot cite is labeled inference, and a
verdict never rests on inference alone.

## Boundaries

Code quality and security belong to their own reviews. When you notice an issue
on either axis, note it once in a line pointing to that review, without a
finding. Recording a new decision follows `domain-modeling` (Writing ADRs);
reconstructing why existing code took its shape follows `why`.

## Report Format

- `## Verdict`: the verdict, one sentence of reason, and "provisional on Q1" when
  step 5 says so.
- `## Intent`: the stated intent quoted, concepts touched, and the contract-surface
  list with locations.
- `## Findings`: one subsection per check that found something, each claim cited.
  Checks that found a fit get one line each.
- `## Blocking Questions`: numbered, each with its citation.
- `## Paths`: lettered, one per plausible use: "If used for X → do A", and
  whether an ADR is needed.
- `## Other Reviews`: one-line pointers for anything on the quality or security
  axis, or "none".

A paste-ready PR review comment is optional; when asked for one, follow
`design-conformance/reference/pr-comment.md`. The draft goes back to the user,
who decides whether and where to post it.
