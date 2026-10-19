#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Fail a pull request whose body carries no eval report and no opt-out.

CI runs this on PRs touching skills/ or platforms/. It makes no model calls:
it only checks that the body holds the marker scripts/run-evals.py prints, or
an explicit `evals: n/a — <reason>` line.

    PR_BODY="$body" scripts/check-eval-report.py

The body arrives through the environment, never interpolated into a shell
command, so a crafted PR description cannot run code in the workflow.
"""

from __future__ import annotations

import os
import re
import sys

MARKER = re.compile(
    r"<!-- evals: base=[0-9a-f]{7,40} head=[0-9a-f]{7,40}(?:-dirty)?"
    r" model=\S+ runs=\d+ -->"
)
# An em dash per the spec; an en dash or ASCII hyphens are accepted too,
# since that is what a keyboard produces. [ \t] rather than \s, so the reason
# must be on the opt-out's own line.
OPT_OUT = re.compile(r"^[ \t]*evals: n/a[ \t]*(?:—|–|--?)[ \t]*\S", re.MULTILINE)


def has_report(body: str) -> bool:
    return bool(MARKER.search(body) or OPT_OUT.search(body))


def main() -> int:
    if has_report(os.environ.get("PR_BODY", "")):
        print("eval report: found")
        return 0
    print(
        "eval report: missing. This PR changes skills/ or platforms/, so its "
        "body needs either the report from `scripts/run-evals.py --base main` "
        "(it ends with an `<!-- evals: ... -->` marker) or a line "
        "`evals: n/a — <reason>` when the change cannot affect behavior.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
