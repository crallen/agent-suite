# PR Body Extras

Three optional additions to the short description `git-conventions` asks for. Each
appears only when it has something to show; a PR that needs none of them stays a
few sentences. They are lines and blocks inside the description, not headed
sections.

## A visual, when the shape changed

When the change alters structure (control flow, call order, file layout, a
component tree), one small sketch orients the reviewer faster than prose. Pick the
smallest view that makes the point, and keep only the calls, files, and states
that carry it.

| The change is about | Show it as |
|---|---|
| Logic or an algorithm | Pseudocode |
| Runtime control flow | A call tree |
| UI structure | A component tree, with the state that matters |
| File responsibility, a broad refactor | A shallow file tree with one-line roles |
| Interaction between components | A Mermaid sequence diagram |

When the surrounding shape already exists and the point is what moved, sketch it as
a `diff` block over that tree or pseudocode:

```diff
 submitForm
   createSession
     persistPrompt
+    expandSkillMention
     launchAgent
```

One visual is the norm. A change to behavior inside an unchanged shape needs none.

## Evidence, when behavior changed

One before and after pair that shows the change works: the test that failed and
now passes, command output, or a screenshot for a visual change. Name the exact
test or command so the reviewer can run it. Prefer evidence that was executed over
a description of what should happen.

```markdown
**Before:** `test_expired_token_returns_401` fails: 200 returned
**After:** passes; full suite green
```

## Reversibility, when the merge is a one-way door

A merge that is cheap to roll back needs no comment. A **one-way door** does: a
destructive migration, a published API or event shape, deleted data, anything a
revert does not undo. State that it is one, what cannot be walked back, and what
it reaches beyond the diff. `blast-radius` produces these facts; quote its
critical safety fact and the rung it was verified to.

```markdown
**One-way door:** drops `users.legacy_token`; a revert restores the column, not the data. Verified no reader remains (executed: grep plus the integration suite).
```
