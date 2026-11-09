# Eval failure triage

## Goal

Turn eval failures into fixes that can be applied. `scripts/run-evals.py` gains a
`--findings FILE` option that writes the per-run evidence of each case needing triage (neither PASS nor FIXED) as JSON.
A new `/eval-triage <findings>` command reads that file and the suite files it
points at. It writes one brief with a numbered section per suite target, each
applied with `/agent-builder`, and a separate eval-case section applied by hand.
Every recommendation ends with the `--only` command that should prove it.

## Context

- `run_one` keeps only `Verdict.detail` (plus plugins and model) and discards the
  `RunResult`: its tool calls, routes, and final text. `run_all` knows each run's
  number, but `Outcome` does not carry it.
- `render_report` prints rates only. The runner makes no model calls of its own, and
  that stays true.
- Known gaps are YAML comments in `evals/routing.yaml`, not data. Triage treats
  every FAIL alike; every FAIL is backlog either way.
- `/agent-builder` takes free text and edits only agents, skills, and commands. An
  "apply section N of `<brief>`" request needs no change to it. Eval files are
  outside its reach, which is why eval-case changes are applied by hand.
- `scripts/validate-config.py` fails a command that `platforms/claude/CLAUDE.md`
  never mentions.
- `scripts/test_evals.py` stubs `run_one`/`run_claude` and calls `render_report`
  directly; the new code fits the same pattern.
- `README.md` does not list runner flags, so it needs no change.

## Approach

The runner records evidence and a command diagnoses it. Alternatives considered:
the runner calling a model after scoring (cost on every PR, a non-deterministic
report) and `/agent-builder` parsing the run log directly (unstructured stderr, and
it mixes diagnosis into the edit step).

Two decisions settled in dialogue:

- **Triage may blame the eval.** Eval-case findings go in their own hand-applied
  section, never to `/agent-builder`, and must quote the failing replies.
- **One brief, applied a section at a time.** Each target gets a self-contained
  numbered section; sections touching the same file are grouped in the apply order.

## Components

1. **Evidence on each outcome** (`scripts/run-evals.py`). A frozen `RunEvidence`
   dataclass holds `routes`, `calls` (tool calls as `name: subject`, via the existing
   `_call_subject`), and `final_text`. A routing run keeps main-thread calls only; a
   behavior run keeps subagent and fork calls too, tagged `[sub]`, since its
   assertions judge every call. Caps: `EVIDENCE_CALLS = 40`,
   `SUBJECT_CHARS = 200` (a Write's subject is its whole input), `TEXT_CHARS = 2000`.
   `Outcome` gains `n: int = 0` and `evidence: RunEvidence | None = None`; the
   defaults keep existing constructors valid. Error outcomes carry no evidence.
2. **`--findings FILE`** (`scripts/run-evals.py`). `findings_of(cases, rows,
   outcomes, *, base_sha, base_ref, head_sha, dirty, model, runs, plugins) -> dict`
   builds:

   ```json
   {
     "base": {"ref": "main", "sha": "…"},
     "head": {"sha": "…", "dirty": true},
     "model": "…", "runs": 3, "plugins": [],
     "cases": [{
       "id": "routing/doc-templates-1", "tier": "routing", "status": "FAIL",
       "base": "0/3", "head": "0/3",
       "prompt": "…", "targets": ["doc-templates"],
       "asserts": null, "case_file": "evals/routing.yaml",
       "runs": [{"side": "base", "n": 1, "passed": false, "counted": true,
                 "detail": "route: none", "plugins": [],
                 "evidence": {"routes": [], "calls": ["Read: …"], "final_text": "…"}}]
     }]
   }
   ```

   Only cases needing triage appear (neither PASS nor FIXED), with every run on both sides, confirmation runs
   included. Each run carries the plugins its init event listed, so triage can tell
   which cases a plugin may have competed in. Behavior cases carry `asserts` and `targets: null`; their `case_file`
   is `evals/behavior/<dir>/case.yaml`. `run()` writes `json.dumps(…, indent=2)`
   alongside the report, which is unchanged.
3. **`/eval-triage <findings>`** (`platforms/claude/commands/eval-triage.md`).
   `context: fork`, `disable-model-invocation: true`, `argument-hint: [findings
   file]`. It loads `skill-design` and `agent-authoring`, finds the suite root with
   `dirname "$(readlink -f ~/.claude/skills)"`, reads the findings case by case and
   every target file they name, and writes `evals/triage/<YYYY-MM-DD>-brief.md`. It
   ends by printing the brief path and the count per section. The method lives in
   the command body, not a skill: it is Claude-only, and a skill's description would
   cost context every session.
4. **The brief.**

   ```markdown
   # Eval triage — <date>, base <sha> vs head <sha>

   ## Suite changes (apply with /agent-builder, one section at a time)
   ### 1. <target> (<skill|agent|command>) — <file path>
   - Cases: <id> (base x/y, head x/y), …
   - Evidence: what loaded instead, or which assertion failed, quoted from runs
   - Diagnosis: why the artifact produces this behavior
   - Change: the concrete edit, with the old text it replaces
   - Generalization: the class of request this widens to, beyond the eval prompt
   - Verify: `scripts/run-evals.py --only '<glob>' --runs 5`, expecting <status>

   ## Eval case changes (apply by hand)
   ### E1. <case id> — <case file>
   - Failing replies: at least 2, quoted
   - Case intent: the spec row or comment the case encodes
   - Change: the assertion or prompt edit
   - Why the replies meet the intent

   ## Not actionable
   - <case id>: INCONCLUSIVE, error-dominated, plugin-contaminated, or its file is
     gone; the re-run command

   ## Apply order
   Section numbers in order, sections touching the same file grouped.
   ```

5. **Docs and wiring.** `.gitignore` adds `evals/triage/`. The `AGENTS.md` Evals
   section gains a triage paragraph. `platforms/claude/CLAUDE.md` gains a command
   row and a workflow row: `run-evals --findings` → `/eval-triage` → `/agent-builder`
   per section → `run-evals --only`.

## Data Flow

1. `run_one` → `Outcome(…, n, evidence)`, evidence built from the `RunResult`.
2. `evaluate` → rows and every outcome, confirmation runs included.
3. `findings_of` → JSON of cases needing triage → `--findings FILE`.
4. `/eval-triage FILE` → reads findings and target files → writes the brief.
5. `/agent-builder apply section N of <brief>` → edit → `run-evals.py --only …`.

## Error Handling

- Findings file missing or unreadable: `/eval-triage` stops and prints the
  `run-evals` command that produces one.
- No case needs triage: the runner writes `"cases": []`; triage reports nothing to fix
  and writes no brief.
- A case's case file or target file no longer exists: the case goes to "Not
  actionable" (the suite changed since the run), not a guess.

## The Overfitting Guard

Rules in the command body:

- A section that edits a description names the class of request it widens to, and
  never copies the eval prompt's own wording into the description.
- A description change verifies with `--only 'routing/*'`, since routes shift
  between neighboring skills; a section-local glob is only for behavior changes.
- Loosening an assertion or prompt needs at least 2 quoted failing replies and an
  argument that they meet the intent of the case's spec row.

## Testing

All in `scripts/test_evals.py`, no model calls:

- `run_one` with a fake `run_claude`: evidence holds the routes, the capped calls
  with capped subjects, and the truncated text; an error outcome carries none.
- `run_all` with a stubbed `run_one`: `n` is set, and confirmation runs number
  from `runs + 1`.
- `findings_of`: no PASS or FIXED cases, every run on both sides, `targets` for routing
  and `asserts` for behavior, the `case_file` path for each.
- `run()` with `--findings`: writes valid JSON, leaves the report unchanged, and
  writes `"cases": []` when everything passes.

`/eval-triage` gets no behavior eval in this change; task 6 exercises it on a real
failing report.

## Risks & Open Questions

- **Risk**: the brief goes stale mid-application, when an earlier section changes
  text a later one quoted. Mitigation: sections carry intent plus old text,
  `/agent-builder` re-reads the file, and the apply order groups shared files.
- **Risk**: fork context size; 13 FAILs is a few hundred KB of findings.
  Mitigation: the evidence caps, and triage reads the findings case by case.
- **Risk**: this PR touches `platforms/`, so it needs an eval report. The new
  command row changes always-loaded context, so run the full set rather than
  `evals: n/a`.

## Task Checklist

- [x] 1. `scripts/run-evals.py`: add the frozen `RunEvidence` dataclass and the
  `EVIDENCE_CALLS`, `SUBJECT_CHARS`, `TEXT_CHARS` caps; add `n: int = 0` and
  `evidence: RunEvidence | None = None` to `Outcome`; `run_one` takes `n` and builds
  evidence from the `RunResult`; `run_all` passes `n`. Add the `run_one` evidence and
  `run_all` numbering tests to `scripts/test_evals.py`.
- [x] 2. `scripts/run-evals.py`: add `findings_of` with the shape above and the
  `--findings FILE` flag; `run()` writes it alongside the report. Add the
  `findings_of` and `run()` tests. (blocked by 1)
- [x] 3. Create `platforms/claude/commands/eval-triage.md`: frontmatter as in
  Component 3; a body that loads `skill-design` and `agent-authoring`, finds the
  suite root, reads findings case by case, applies the overfitting guard, follows the
  brief template and the error handling above, and writes
  `evals/triage/<YYYY-MM-DD>-brief.md`.
- [x] 4. `platforms/claude/CLAUDE.md`: add the `/eval-triage` command row and an
  "Eval failures → fixes" workflow row. (blocked by 3)
- [x] 5. `.gitignore`: add `evals/triage/`. `AGENTS.md` Evals section: add a
  "Triage" paragraph covering `--findings`, `/eval-triage`, applying the brief
  section by section with `/agent-builder`, and the `--only` check. (blocked by 2, 3)
- [x] 6. End to end: `scripts/run-evals.py --base main --findings
  evals/triage/findings.json --out evals/triage/report.md`, then the user runs
  `/eval-triage evals/triage/findings.json`; confirm the brief has suite and eval
  sections with verify commands. Run `scripts/test_evals.py` and
  `scripts/validate-config.py`. (blocked by 2, 3, 4, 5)
