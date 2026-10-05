---
name: spec-implementation
description: Implement a whole spec in one run — read its tasks as a task graph, work the ready frontier with parallel implementer subagents in their own worktrees, and land everything on one integration branch that is reviewed against the spec. Load when asked to implement a spec or a set of tickets end to end.
---

# Spec Implementation

Build an approved spec on a single **integration branch**. The spec's tasks are a **task graph**, not a list of steps: each task names the tasks that block it, so there is always a **frontier** of tasks whose blockers are done and which can be worked at once.

You orchestrate; subagents implement. Brief them with **context pointers** (the spec path, the task number, the notes path, the commits that landed before) and leave the content where it already lives. A brief that restates the spec is a second copy to drift.

## Steps

1. **Read the graph.** The source is the spec's Task Checklist with its "blocked by" edges, or a set of tickets with their Depends on lines. Where tasks carry no edges, derive them: a task that consumes another's interface or edits the same files is blocked by it, and everything else is independent. Show the user the graph and the first frontier. Done when every task has its edges and the user has confirmed them.

2. **Explore once.** When several tasks need the same background (how a module works, what an external API accepts), send one exploration subagent to write notes into a directory outside the repo that every later subagent can read. Skip this when the spec's Context section already covers it. Done when the notes answer every question two or more tasks share.

3. **Create the integration branch** from the default branch, named per `git-conventions`. Every task lands here and nowhere else. Done when the branch exists and the default branch is untouched.

4. **Work the frontier.** Start one implementer subagent per frontier task, concurrently, each in its own worktree on its own branch cut from the integration branch tip. Each implementer:
   - confirms its worktree is based on the integration branch tip, and resets onto it if not;
   - loads `coding-guardrails`, `test-strategy`, and the domain skill for the task, and builds the task test-first;
   - commits per `git-conventions`, then merges the current integration tip into its branch and re-runs the task's checks before reporting done.

   An implementer is done when its task's checks pass on a branch that contains the integration tip.

5. **Merge and advance.** As each implementer reports, merge its branch into the integration branch, one merge at a time, and run the checks there. Tick the task in the spec. Recompute the frontier and start an implementer for every task this unblocked, without waiting for the rest of the previous frontier. Done when every task is ticked.

6. **Review the whole.** Run the full test suite on the integration branch, then review its diff against the spec with `code-review-checklist`, through the harness's reviewer agent where it has one. Fix every CRITICAL and WARNING finding in a single pass and re-run the suite. Done when the suite is green and no CRITICAL or WARNING finding remains.

7. **Close out.** Remove the task worktrees with `git worktree remove` and delete the merged task branches. Report the integration branch, the tasks landed, the review result, and any safety claim left unproven. Open a pull request when the project lands work through them or the user asks; merging to the default branch is the user's call. Done when `git worktree list` shows no task worktree and the report is delivered.

## When a task fails

A task whose implementer cannot finish stays unticked, and every task it blocks stays off the frontier. Keep working the tasks it does not block, then report the stuck task with what was tried. A spec that turns out wrong mid-build goes back to the user as a spec change, never patched silently in code.

## Sizing

A linear chain has a frontier of one: work it in sequence, one fresh implementer per task. A spec of one or two small tasks needs no orchestration; implement it directly. In a harness without subagents or worktrees, work the frontier one task at a time on the integration branch and keep every other step.
