---
name: wayfinder-methodology
description: Chart an effort too big for one session as a map of decision tickets in the repo, then resolve them one per session — destination, fog of war, frontier, and the four ticket types. Load when planning work that spans multiple sessions, or when working through an existing wayfinder map.
---

# Wayfinder Methodology

A loose idea has arrived, too big for one session and wrapped in fog: the way from here to the **destination** is not visible yet. Wayfinding finds that way rather than charging at the destination. This skill charts the way as a **map** in the repo, then works its **decision tickets** — questions whose resolution is a decision, not slices of a build to execute — one at a time until the route is clear.

## When a map earns its keep

A map costs a file and a session spent charting, so reach for it only when the effort outlives a single session:

- **`/grill`** — one sitting, one thread of questions. No artifact beyond CONTEXT.md and ADRs.
- **`/spec`** — one sitting, and the shape is already knowable. Produces a spec plus a task checklist.
- **`/wayfinder`** — the effort will not fit in one session and the shape is fogged. The artifact is a map that survives across sessions. A map's destination is often *a spec `/spec` can then write*.
- **`/ticket`** — downstream of a settled spec, splitting it into build slices. Wayfinder tickets are decisions, never build slices.

If charting surfaces no fog — the way is already clear, the whole journey fits one session — say so and stop. An unfogged effort wants `/spec`, not a map.

## Plan, don't do

Wayfinding is **planning**. Each ticket resolves a decision, and the map is done when nothing is left to decide before someone goes and does the thing. The pull to just do the work is the signal that you have reached the edge of the map and it is time to hand off. An effort can override this in its **Notes**, carrying execution into the map itself; absent that, produce decisions, not deliverables.

## Refer by name

In everything the user reads, refer to a ticket by its **title**, never by its handle. A wall of `tenancy-shape, key-tiers, session-store` is opaque; titles read at a glance. Handles exist to wire `after:` lines, nothing else.

## The map

One file per effort at `docs/wayfinder/<effort-slug>.md`, the canonical artifact. It holds the destination, the live tickets, and a one-line index of every decision already made.

```markdown
# <Effort name>

## Destination

<what reaching the end of this map looks like: the spec, decision, or change this
effort is finding its way to. One or two lines; every session orients here first.>

## Notes

<domain; skills every session should load; standing preferences for this effort>

## Tickets

### tenancy-shape — What is the tenant boundary

grilling

<the decision or investigation this ticket resolves>

### session-store — Which substrate holds the session record

grilling · after: tenancy-shape

<the question>

## Decisions so far

- **Keys are per-user, not per-tenant** — chosen for individual erasure. ADR-0004.

## Not yet specified

- <in-scope fog you cannot ticket yet; graduates as the frontier advances>

## Out of scope

- <gist> — <why it sits past the destination>
```

### Tickets

A ticket is one `###` section under **Tickets**, sized to a single session. Its heading carries a kebab-case **handle** and the question as a title; the line under it carries the type, and the handles of any tickets that must resolve first:

```
### session-store — Which substrate holds the session record

grilling · after: tenancy-shape, key-tiers
```

Living under **Tickets** is what makes a ticket open, so there is no status to maintain and none to fall out of date. A ticket is **unblocked** when no handle on its `after:` line still appears under **Tickets**. The **frontier** is every unblocked ticket — the edge of the known, and what a session picks from.

Resolving a ticket **removes its section** and leaves one line under **Decisions so far**. The map therefore holds only live tickets plus a growing index, and stays small however long the effort runs.

## Ticket types

Every ticket is either **HITL** — worked *with* the user, who speaks for themselves — or **AFK**, driven by the agent alone. A HITL ticket resolves only through that live exchange; standing in for the user's side of it breaks the type. A grilling agent that answers its own questions has produced nothing.

| Type | Mode | What it is |
|---|---|---|
| `research` | AFK | Surfacing a fact a decision waits on, from outside the working directory: third-party docs, an API's real behaviour, a local knowledge base. Dispatch a subagent — `Explore` for in-repo questions, `general-purpose` when the answer lives on the web. |
| `prototype` | HITL | Raise the fidelity of the discussion with a cheap, rough, concrete artifact to react to. Load `prototype-methodology`. Reach for it when *how should it look* or *how should it behave* is the open question. |
| `grilling` | HITL | Conversation, and the default case. Load `grill-methodology` and `domain-modeling`. |
| `task` | Either | Manual work that must happen before a decision can be made: signing up for a service so its API can be judged, provisioning access, moving data so its shape is visible. The one type that *does* rather than decides, and it earns its place by unblocking a decision. The agent drives it alone where it can; otherwise it hands the user a precise checklist. Its resolution records what was done plus any facts later tickets depend on. |

## Recording a resolution

A resolved ticket leaves **one line** under **Decisions so far**: the decision in bold, the reason it went that way, and a pointer to wherever the detail now lives.

Where the detail lives depends on how hard the decision is to reverse. Load `domain-modeling` for the ADR test and apply it here:

- **Hard to reverse** — write an **ADR** in `docs/adr/` and cite it from the map line. This is the same durable-decision mechanism `/grill` and `/architecture` already use, so a wayfinder decision lands where every other architectural decision in the repo lands. The map holds the gist; the ADR holds the argument.
- **Easy to reverse** — the one-line gist on the map is the whole record. Do not manufacture an ADR for it.
- **A term the domain now needs** — add it to `CONTEXT.md`, again per `domain-modeling`.

Because the substance graduates out, the map can be deleted once the effort lands, with nothing of value lost.

## Fog of war

The map is *deliberately* incomplete: do not chart what you cannot yet see. Beyond the live tickets lies the **fog of war** — decisions you can tell are coming but cannot pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever became specifiable into fresh tickets, until the way to the destination is clear and no tickets remain.

**Not yet specified** is where that dim view is written down. Everything there is in scope, just not sharp enough to ticket. It doubles as a signpost for anyone reading where the effort is headed.

The test is whether you can state the question precisely now, **not** whether you can answer it now:

- **Ticket it** when the question is already sharp, even if it is blocked and you cannot act on it yet.
- **Leave it in the fog** when you cannot yet phrase it that sharply. Fog is coarser than a ticket; one patch may graduate into several tickets, or none.

**Not yet specified** excludes what is already decided, already a live ticket, or out of scope.

## Out of scope

Fog gathers only *toward* the destination. The destination fixes the scope, so work beyond it is **out of scope**: it is not fog, and it does not belong in **Not yet specified**. Scope, not sharpness, lands it there. Out-of-scope work never graduates, so it returns only if the destination is redrawn — and then as a fresh effort, not a resumption.

When a ticket turns out to sit past the destination, remove its section and leave one line under **Out of scope**: the gist and why it is out. Keep it out of **Decisions so far**, which records the route actually walked; a scope boundary is not a step on it.

## Chart the map

The user arrives with a loose idea. Charting is one session's work and hand-resolves nothing.

1. **Name the destination.** Load `grill-methodology` and `domain-modeling`, and pin down what this map is finding its way to. The destination fixes the scope, so it settles first. Done when the user has agreed to a destination you can state in two lines.
2. **Map the frontier.** Grill again, **breadth-first** — fan out across the whole space rather than deep on any one thread, surfacing the open decisions and the steps takeable now. Done when the user has nothing further to add and you can name both the sharp questions and the fogged areas.
3. **Write the map**, with the destination and notes filled in, Decisions-so-far empty, and the fog sketched into **Not yet specified**.
4. **Write every ticket you can specify now**, wiring `after:` handles as you go. Done when at least one ticket is unblocked and every fogged area is either a ticket or a line under **Not yet specified**.
5. **Resolve the research tickets.** Dispatch a subagent per `research` ticket to run them in parallel, then record each resolution as below.
6. **Stop.** Report the map path, the destination, and the frontier.

## Work through the map

The user arrives with a map, and optionally a ticket. Without one, you pick the next decision, not the user. **Never resolve more than one ticket per session** — research tickets excepted, since they are AFK and parallel.

1. **Read the map**, and orient to the destination before choosing anything.
2. **Choose the ticket.** Use the one the user named, otherwise the first unblocked ticket under **Tickets**. If nothing is unblocked, say so rather than picking a blocked one.
3. **Resolve it.** Work it by its type, loading whichever skills the **Notes** block names; when in doubt, `grill-methodology` and `domain-modeling`.
4. **Record the resolution** per *Recording a resolution*: remove the ticket's section, add its line to **Decisions so far**, and write the ADR or CONTEXT.md entry if the decision earns one.
5. **Advance the frontier.** Add newly surfaced tickets, and graduate any fog the answer made specifiable — clearing each graduated patch from **Not yet specified** so it lives only as its ticket. If the answer puts a ticket past the destination, rule it out of scope rather than resolving it. If it invalidates part of the map, update or delete the affected tickets.
6. **Report** the decision made, what it unblocked, and the new frontier. When no tickets remain, say the way is clear and name the handoff — usually `/spec`.
