---
description: Design principles for writing and reviewing skills well — predictability, information hierarchy, leading words, progressive disclosure, and the failure modes that make a skill unpredictable. Load when authoring, refactoring, or critiquing a skill's content (distinct from agent-authoring, which covers file layout and frontmatter schemas).
---

# Skill Design

Where `agent-authoring` covers the **mechanics** of a skill — file location, frontmatter keys, the validation checklist — this skill covers its **design**: what makes the content itself good. Load both when writing or reviewing a skill.

A skill exists to wrangle determinism out of a stochastic system. **Predictability** — the agent taking the same *process* every run, not producing the same output — is the root virtue; every lever below serves it. A brainstorming skill should predictably diverge: its tokens vary, its behaviour doesn't.

Terms in **bold** are defined in [`GLOSSARY.md`](GLOSSARY.md), the disclosed reference for this skill. Reach for it when a term needs its full meaning.

## Invocation

This suite has two skill kinds, and they map onto one design axis — whether the **agent** can reach the skill or only the **human** can:

- A **reference skill** (no `disable-model-invocation`) keeps its **description**, so the agent can fire it autonomously, other skills can reach it, and it can be preloaded into an agent via `skills:`. It pays a permanent **context load** — the description sits in the window every turn, and a preloaded body is injected whole at startup. This is the model-invoked kind.
- A **workflow skill** (`disable-model-invocation: true`, the `/`-commands) strips the description from the agent's reach: only the human, typing its name, invokes it, and no other skill can. Zero context load, but it spends **cognitive load** — the human is the index that must remember it exists. This is the user-invoked kind, and it can never be preloaded.

Choose the reference kind only when the agent must reach the skill on its own, or another skill or agent must preload it. If it only ever fires by hand, make it a workflow skill and pay no context load.

When workflow skills multiply past what the human can hold in their head, that piled-up cognitive load is cured by a **router skill**: one workflow skill that names the others and when to reach for each. (`frontend-patterns` plays an analogous routing role, though for reference files rather than workflow skills.)

## Writing the description

A reference skill's **description** does two jobs — state what the skill is, and list the **branches** that should trigger it. Every word adds **context load**, so a description earns harder pruning than the body:

- **Front-load the leading word.** The description is where a **leading word** does its invocation work.
- **One trigger per branch.** Synonyms renaming a single branch are **duplication** — collapse them; keep only genuinely distinct branches.
- **Cut identity already in the body.** Keep the description to triggers plus any "when another skill needs…" reach clause.

## Information hierarchy

Skill content is **steps** and **reference**, mixed freely — a skill can be all steps, all reference, or both. The **information hierarchy** ranks each piece by how immediately the agent needs it:

1. **In-skill step** — an ordered action in `SKILL.md`, the primary tier. Each step ends on a **completion criterion**: the condition telling the agent the work is done. Make it *checkable* (can it tell done from not-done?) and, where it matters, *exhaustive* ("every modified model accounted for", not "produce a change list") — a vague criterion invites **premature completion**.
2. **In-skill reference** — a definition, rule, or fact consulted on demand. Often a legitimately flat peer-set (every rule of a review on one rung) — a fine arrangement, not a smell.
3. **Disclosed reference** — reference pushed into a separate file (`GLOSSARY.md`, `reference/*.md`), reached by a **context pointer** and loaded only when the pointer fires.

Push too little down and the top bloats (**sprawl**); push too much and you hide material the agent needs. That tension is the whole decision.

**Progressive disclosure** is the move down the ladder — out of `SKILL.md` into a linked file — so the top stays legible. In this suite it is the reference-file pattern: a router `SKILL.md` plus `reference/*.md` loaded on demand. **Branching** is the cleanest disclosure test: inline what every branch needs, push behind a pointer what only some branches reach. A **context pointer**'s *wording*, not its target, decides when and how reliably the agent reaches the material — a must-have target behind a weak pointer is a variance bug, so sharpen the wording before inlining.

Where the ladder decides *how far down* a piece sits, **co-location** decides *what sits beside it*: keep a concept's definition, rules, and caveats under one heading rather than scattered, so reading one part brings its neighbours.

Preloaded skills are injected whole, so keep a preloadable reference skill lean and disclose its depth into `reference/*.md` the agent Reads on demand.

## When to split

**Granularity** is how finely you divide skills; each cut spends one of the two loads, so split only when the cut earns it:

- **By invocation** — split off a reference skill when a distinct **leading word** should trigger it on its own, or an agent must preload it. You pay **context load** for the always-loaded description, so that independent reach must be worth it.
- **By sequence** — split a run of **steps** when the steps still ahead (a step's **post-completion steps**) tempt the agent to rush the one in front (**premature completion**). Hiding them across a real context boundary — a workflow hand-off or a `context: fork` subagent, since an inline reference-skill call clears nothing — encourages more **legwork** on the current step.

## Leading words

A **leading word** is a compact concept already living in the model's pretraining that the agent thinks with while running the skill (e.g. *lesson*, *fog of war*, *tracer bullets*). Repeated as a token — never restated as a sentence — it accumulates a distributed definition and anchors a whole region of behaviour in the fewest tokens, by recruiting priors the model already holds.

It serves predictability twice. In the body it anchors *execution*: the agent reaches for the same behaviour every time the word appears. In the description it anchors *invocation*: when the same word lives in your prompts, docs, and code, the agent links that shared language to the skill and fires it more reliably — so word a description with the leading words you already reach for.

Hunt for restatements a leading word retires: a triad spelled out at three sites, a description spending a sentence to gesture at one idea. "fast, deterministic, low-overhead" collapses to a *tight* loop; "a loop you believe in" becomes the loop going *red* on the bug — a fuzzy gate turned into a binary observable. Reach for an existing pretrained word first; a coined word recruits no priors and you pay its definition in tokens.

## Pruning

Keep each meaning in a **single source of truth** — one authoritative place, so changing the behaviour is a one-place edit.

Check every line for **relevance**: does it still bear on what the skill does? Then hunt **no-ops** sentence by sentence — run the no-op test on each in isolation, and when one fails, delete the whole sentence rather than trim its words. Be aggressive: most prose that fails should go, not be rewritten.

## Failure modes

Use these to diagnose a skill under review — each names a symptom and the lever that cures it:

- **Premature completion** — ending a step before it's genuinely done, attention slipping to *being done*. Sharpen the completion criterion first (cheap, local); only if it is irreducibly fuzzy *and* you observe the rush, hide the post-completion steps by splitting.
- **Duplication** — the same meaning in more than one place. Costs maintenance and tokens, and inflates a meaning's rank on the ladder past its real weight.
- **Sediment** — stale layers that settle because adding feels safe and removing feels risky. The default fate of any skill without a pruning discipline.
- **Sprawl** — a skill simply too long, even when every line is live and unique. The cure is the ladder: disclose reference behind pointers, and split by branch or sequence so each path carries only what it needs.
- **No-op** — a line the model already obeys by default, so you pay load to say nothing. The test: does it change behaviour versus the default? A weak leading word (*be thorough* when the agent already is) is a no-op; the fix is a stronger word (*relentless*), not a different technique.
- **Negation** — steering by prohibition backfires: *don't think of an elephant* names the elephant and makes it more available. Prompt the **positive** — state the target behaviour so the banned one is never spoken; keep a prohibition only as a hard guardrail you can't phrase positively, and even then pair it with what to do instead.
