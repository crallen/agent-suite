# Design Review PR Comment

The comment is addressed to the author, a colleague whose need is real even when
the shape of the change is not yet right. It carries the report's substance in
the order the author needs it, and nothing from the other review axes.

## Shape

1. **Opening**: one or two sentences. Credit what works, then say plainly that
   the comment steps back to the design before the details.
2. **`### The blocking question: …`**: the question as its own heading, stated
   once in bold. Quote the author's own description of the change when it is what
   raises the question.
3. **Why it matters**: one bullet per finding, each opening with a bold one-line
   claim, followed by the cited evidence in a sentence or two. Name the document
   and path, and quote the decisive phrase.
4. **`### Where to go from here`**: one bold lettered path per plausible use, in
   the form "**A. If … (my expectation):**", with the path the evidence favors
   first and marked. Under each path, the concrete reshaping steps, and an ADR
   where the path needs one.
5. **Close**: offer a route for the author who would rather hand the design
   question over, such as an issue describing what the consumer needs.

Write in the reviewer's first person, in plain sentences. Leave out the verdict
label, line-level code findings, and test gaps; those belong to the report and
the code review respectively.

## Example (abridged)

> Thanks for this. The plumbing is solid. Before going further, though, I want
> to step back on the design, because the system has already decided a case very
> like this one.
>
> ### The blocking question: what is `approval_regions` used for?
>
> The PR describes it as "regions the user can approve refunds in". That sounds
> like an authorization decision, so **which services will read this field, and
> what will they decide with it?**
>
> - **Permissions live in roles, not profile fields.** `CONTEXT.md:12` gives this
>   service ownership of "identity, sessions, and role policy".
> - **We've made this call once.** `docs/adr/0004-refund-approval-is-a-role.md:5`
>   moved `can_approve_refunds` out of the profile and into a role, so that every
>   permission is granted, audited, and revoked in one place. This looks like the
>   same pattern.
> - **Roles can already express it.** A role binding can be scoped to one
>   resource (`docs/runbooks/roles.md:30`), so per-region approval could be a
>   region-scoped binding.
> - **A new profile field is a contract change.** The current spec adds no
>   profile fields (`docs/specs/profile-v2.md:18`), and once consumers adopt this
>   one, removing it breaks them.
>
> ### Where to go from here
>
> **A. If services will gate approvals with it (my expectation):** reshape along
> the lines of ADR-0004. Grant region-scoped roles instead of storing a profile
> column, and have consumers check roles the way they check everything else.
>
> **B. If it is display context only (a default region in a form):** a profile
> attribute is defensible. Write a short ADR on why this differs from ADR-0004,
> document the field as advisory, and return a list rather than a delimited
> string.
>
> If you'd rather hand the design over, open an issue describing what the
> consuming service needs, and I'll fit it into the role model.
