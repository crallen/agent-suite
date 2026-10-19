#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Run the routing and behavior evals against a base ref and the working tree.

Each side gets its own Claude Code config directory built from that side's
suite, so the same prompts run once against `--base` (a detached worktree) and
once against this working tree, uncommitted edits included.

    scripts/run-evals.py                          every case against main, 3 runs each
    scripts/run-evals.py --base REF               compare against another ref
    scripts/run-evals.py --only 'behavior/*'      only the cases whose id matches
    scripts/run-evals.py --runs 5 --out r.md      more runs; report to a file

Cases always come from this working tree's evals/; the base ref supplies only
the suite under test. Case ids, for --only (an fnmatch glob):

    behavior/<dir>        one per evals/behavior/<dir>/case.yaml
    routing/<target>      one per evals/routing.yaml entry, named for its
                          `expect`, or the first `any_of` member; a name used
                          by more than one entry gets -1, -2, ... in file
                          order on every use (routing/none-1 .. none-6)

The report (markdown, stdout unless --out) ends with the marker that
scripts/check-eval-report.py looks for. Exit status: 2 on a setup problem, 1
when any case is a REGRESSION, 0 otherwise.

Auth comes from CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY in the
environment, or else from `.env` at the suite root (see `.env.example`;
--env-file names another file). The value is placed only in the environment
of the `claude` subprocesses; it is never printed or written anywhere else.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
from collections.abc import Iterable, Iterator, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import yaml

AUTH_VARS = ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY")

# Builtin plugins the CLI enables by default. cc-plugin-plugin-authoring adds a
# model-invocable skill that would compete in routing; all three are disabled
# so the model sees the suite under test and nothing else.
BUILTIN_PLUGINS = (
    "cc-plugin-plugin-authoring@builtin",
    "cc-plugin-agents-md@builtin",
    "cc-plugin-telemetry@builtin",
)

# The tool that spawns a subagent: `Task` in the init event's tool list,
# `Agent` in tool_use blocks.
AGENT_TOOLS = {"Agent", "Task"}

# Marks a slash command the CLI could not expand, such as a `!` shell line
# whose command the allowed tools do not cover. The run then ends without a
# model call and with a clean, empty result.
LOCAL_COMMAND_ERROR = "<local-command-stderr>"

# Grace period between SIGTERM and SIGKILL for a claude process group.
KILL_GRACE_SECONDS = 5


class SetupError(Exception):
    """A preflight check failed; the message says how to fix it."""


# --- Preflight --------------------------------------------------------------


def load_env(path: Path) -> dict[str, str]:
    """Read KEY=VALUE lines from a dotenv file; a missing file yields {}.

    Blank lines and `#` comments are skipped, whitespace around keys and
    values is dropped, and a value wrapped in matching single or double quotes
    is unquoted. No interpolation, no `export` prefix.
    """
    if not path.is_file():
        return {}
    pairs = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        pairs[key.strip()] = value
    return pairs


def resolve_auth(environ: Mapping[str, str], env_file: Path) -> dict[str, str] | None:
    """Pick the auth variable for the claude subprocesses, or None.

    A non-empty variable already in the environment wins; the dotenv file is
    read only when the environment has none.
    """
    for source in (environ, load_env(env_file)):
        for name in AUTH_VARS:
            if source.get(name):
                return {name: source[name]}
    return None


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


@dataclass(frozen=True)
class Setup:
    auth: dict[str, str]
    base_sha: str


def preflight(
    head: Path, base_ref: str, environ: Mapping[str, str], env_file: Path | None = None
) -> Setup:
    """Check the prerequisites for a run, or raise SetupError with the fix.

    `env_file` defaults to `<head>/.env`. Also prunes worktree records left by
    a run that was killed before cleanup.
    """
    if shutil.which("claude") is None:
        raise SetupError(
            "claude is not on PATH. Install Claude Code "
            "(https://docs.claude.com/en/docs/claude-code) and re-run."
        )
    env_file = env_file or head / ".env"
    auth = resolve_auth(environ, env_file)
    if auth is None:
        raise SetupError(
            "no auth for claude. Run `claude setup-token`, then copy "
            f"{head / '.env.example'} to {env_file} and fill in "
            "CLAUDE_CODE_OAUTH_TOKEN, or export CLAUDE_CODE_OAUTH_TOKEN or "
            "ANTHROPIC_API_KEY."
        )
    try:
        base_sha = git(head, "rev-parse", "--verify", "--end-of-options", f"{base_ref}^{{commit}}")
    except subprocess.CalledProcessError:
        raise SetupError(
            f"--base {base_ref} does not resolve to a commit. Fetch it "
            f"(`git fetch origin {base_ref}`) or pass an existing ref."
        ) from None
    git(head, "worktree", "prune")
    return Setup(auth=auth, base_sha=base_sha)


# --- Config directories and the base worktree -------------------------------


def suite_skills(root: Path) -> list[str]:
    """Names of the skills whose SKILL.md git at `root` tracks or would add.

    Untracked skills count, since head is the working tree with its
    uncommitted edits; gitignored ones, skills/synced/ among them, are left
    out so both sides of a comparison see the same kind of suite.
    """
    paths = git(root, "ls-files", "--cached", "--others", "--exclude-standard",
                "--", "skills/*/SKILL.md").splitlines()
    return sorted({Path(p).parent.name for p in paths})


def build_config(root: Path) -> Path:
    """Build a CLAUDE_CONFIG_DIR exposing the Claude Code suite at `root`.

    The directory is private (mode 0700) and holds links to the agents,
    commands, and index under platforms/claude/, one link per suite_skills() name,
    and settings.json from the example with the builtin plugins disabled.
    The caller removes it with remove_tree().
    """
    root = root.resolve()
    platform = root / "platforms" / "claude"
    config = Path(tempfile.mkdtemp(prefix="evals-cfg-"))
    config.chmod(0o700)
    for name in ("agents", "commands", "CLAUDE.md"):
        (config / name).symlink_to(platform / name)
    skills = config / "skills"
    skills.mkdir()
    for name in suite_skills(root):
        (skills / name).symlink_to(root / "skills" / name)
    settings = json.loads((platform / "settings.json.example").read_text())
    settings["enabledPlugins"] = {plugin: False for plugin in BUILTIN_PLUGINS}
    (config / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    return config


def remove_tree(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


@contextmanager
def base_worktree(head: Path, sha: str) -> Iterator[Path]:
    """Check `sha` out as a detached worktree; remove it on exit."""
    parent = Path(tempfile.mkdtemp(prefix="evals-base-"))
    tree = parent / "suite"
    try:
        git(head, "worktree", "add", "--detach", "--quiet", str(tree), sha)
        yield tree
    finally:
        subprocess.run(
            ["git", "-C", str(head), "worktree", "remove", "--force", str(tree)],
            capture_output=True,
        )
        remove_tree(parent)
        subprocess.run(["git", "-C", str(head), "worktree", "prune"], capture_output=True)


@dataclass(frozen=True)
class Side:
    """One side of the comparison: its config dir and the HOME its runs use.

    home/.claude links to config, because command `!` lines name
    `~/.claude/...` literally and would otherwise run the live suite's files.
    """

    name: str
    config: Path
    home: Path


@contextmanager
def side_dirs(name: str, root: Path) -> Iterator[Side]:
    config = build_config(root)
    home = Path(tempfile.mkdtemp(prefix="evals-home-"))
    try:
        (home / ".claude").symlink_to(config)
        yield Side(name=name, config=config, home=home)
    finally:
        remove_tree(home)
        remove_tree(config)


@dataclass(frozen=True)
class Sides:
    base: Side
    head: Side


@contextmanager
def eval_sides(head: Path, base_sha: str) -> Iterator[Sides]:
    """Yield both sides; remove their directories and the base worktree on exit."""
    with base_worktree(head, base_sha) as base_root:
        with side_dirs("base", base_root) as base, side_dirs("head", head) as head_side:
            yield Sides(base=base, head=head_side)


# --- Running claude ---------------------------------------------------------


def claude_command(
    prompt: str,
    *,
    agent: str | None = None,
    allowed_tools: Sequence[str] = (),
    model: str | None = None,
) -> list[str]:
    """The argv for one eval run, ready for run_claude().

    prompt         the user message, a `/command args` line included
    agent          run as this agent (`--agent`); None for the default thread
    allowed_tools  pre-approved tools (`--allowedTools`); anything else is
                   denied, since the run has no one to ask
    model          `--model`; None for the config's default

    The prompt sits right after `-p` and `--allowedTools` comes last, because
    that flag is variadic and would swallow a prompt placed after it.
    """
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json", "--verbose", "--include-partial-messages",
        "--strict-mcp-config", "--permission-mode", "acceptEdits",
    ]
    if agent:
        cmd += ["--agent", agent]
    if model:
        cmd += ["--model", model]
    if allowed_tools:
        cmd += ["--allowedTools", *allowed_tools]
    return cmd


def child_env(
    config: Path, home: Path, auth: Mapping[str, str], parent: Mapping[str, str] = os.environ
) -> dict[str, str]:
    """The environment for a claude subprocess using `config` and `home`.

    Every inherited CLAUDE* variable goes (a parent Claude Code session exports
    CLAUDECODE, session ids, and effort), so a run from inside an agent matches
    a run from a plain terminal. Every GIT_* variable goes too, so a runner
    started from a hook or `git rebase -x` cannot point the run's git at the
    outer repository. Then the config dir, HOME, and auth are set.
    """
    env = {k: v for k, v in parent.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env["CLAUDE_CONFIG_DIR"] = str(config)
    env["HOME"] = str(home)
    env.update(auth)
    return env


@dataclass(frozen=True)
class ToolCall:
    name: str
    input: dict
    # None on the main thread. Inside a subagent, the id of the Agent call
    # that spawned it; inside a `context: fork` command, the synthetic id
    # `forked-command-<name>`.
    parent_tool_use_id: str | None


@dataclass(frozen=True)
class RunResult:
    """What one claude run did.

    tool_calls   every tool call in stream order, subagent calls included
    routes       skills and agents the main thread loaded within the window
    final_text   the last result's text, or the last main-thread text if killed
    stop         route (killed at an Agent call) or window (killed once the
                 window closed), result (the stream ended after a result
                 event), or eof (it ended without one)
    exit_status  the process exit status; None when parsed from a recording
    error_class  none, timeout, or error; `error` runs are left out of a rate
    plugins      plugins the init event reports; any at all breaks isolation
    model        the model the first init event reports; "" without one
    """

    tool_calls: tuple[ToolCall, ...]
    routes: tuple[str, ...]
    final_text: str
    stop: str
    exit_status: int | None
    error_class: str
    plugins: tuple[str, ...]
    model: str


def route_of(call: ToolCall) -> str | None:
    """The skill or agent a tool call loads, or None if it loads neither."""
    if call.name == "Skill":
        return call.input.get("skill")
    if call.name in AGENT_TOOLS:
        # Claude Code runs an Agent call without a type as general-purpose.
        return call.input.get("subagent_type") or "general-purpose"
    if call.name == "Read":
        path = Path(str(call.input.get("file_path", "")))
        if path.name == "SKILL.md":
            return path.parent.name
    return None


def classify(stop: str, is_error: bool, exit_status: int | None, timed_out: bool) -> str:
    """The error class of a run. `subtype` is never consulted: an API error
    still reports `subtype: success`, with `is_error: true`."""
    if timed_out:
        return "timeout"
    if stop in ("route", "window"):
        return "none"  # killed on purpose; the exit status is the signal's
    if stop != "result" or is_error or exit_status not in (0, None):
        return "error"
    return "none"


@dataclass(frozen=True)
class _Stream:
    """What the stream alone says, before the process exit is known."""

    tool_calls: tuple[ToolCall, ...]
    routes: tuple[str, ...]
    final_text: str
    stop: str
    is_error: bool
    plugins: tuple[str, ...]
    model: str

    def finish(self, exit_status: int | None, timed_out: bool) -> RunResult:
        return RunResult(
            tool_calls=self.tool_calls,
            routes=self.routes,
            final_text=self.final_text,
            stop=self.stop,
            exit_status=exit_status,
            error_class=classify(self.stop, self.is_error, exit_status, timed_out),
            plugins=self.plugins,
            model=self.model,
        )


def read_stream(lines: Iterable[str], route_window: int | None) -> RunResult:
    """Parse stream-json lines from a live process or a recording.

    With a route window, reading stops at the `assistant` event carrying an
    Agent call (the subagent starts there) or once the main thread has made
    `route_window` calls. Skill loads and SKILL.md reads in the window are
    routes too, but reading goes on past them: a skill load has no side
    effects, and the expected skill may load after another one. With None it
    reads to the end, past any number of `result` events; the final text is
    the last one's.
    """
    return _parse(lines, route_window).finish(exit_status=None, timed_out=False)


def _is_local_command_error(event: dict) -> bool:
    """A main-thread user message whose string content is the CLI's report of
    a slash command it could not expand. A tool result quoting the marker (a
    file being read, a subagent's output) is a list of blocks, not this."""
    content = event.get("message", {}).get("content")
    return (event.get("parent_tool_use_id") is None and isinstance(content, str)
            and LOCAL_COMMAND_ERROR in content)


def _parse(lines: Iterable[str], route_window: int | None) -> _Stream:
    calls: list[ToolCall] = []
    routes: list[str] = []
    agent_routed = False
    plugins: tuple[str, ...] = ()
    model = ""
    last_text = ""
    result_text: str | None = None
    is_error = False
    main_calls = 0
    stop = "eof"

    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "init":
            plugins = tuple(p.get("name", "") for p in event.get("plugins") or ())
            model = model or event.get("model") or ""
        elif kind == "result":
            # Not the end: a main thread that launched a background agent
            # reports a result at once, then takes another turn when the
            # agent finishes. The process exits after the last one.
            result_text = event.get("result") or ""
            is_error = is_error or bool(event.get("is_error"))
            stop = "result"
        elif kind == "user" and _is_local_command_error(event):
            is_error = True
        elif kind == "assistant":
            parent = event.get("parent_tool_use_id")
            for block in event.get("message", {}).get("content", ()):
                if block.get("type") == "text" and parent is None:
                    last_text = block.get("text", "")
                if block.get("type") != "tool_use":
                    continue
                call = ToolCall(block.get("name", ""), block.get("input") or {}, parent)
                calls.append(call)
                if parent is not None:
                    continue
                main_calls += 1
                route = route_of(call)
                if route and (route_window is None or main_calls <= route_window):
                    routes.append(route)
                    agent_routed = agent_routed or call.name in AGENT_TOOLS
            if route_window is not None and agent_routed:
                stop = "route"
                break
            if route_window is not None and main_calls >= route_window:
                stop = "window"
                break

    return _Stream(
        tool_calls=tuple(calls),
        routes=tuple(routes),
        final_text=result_text if result_text is not None else last_text,
        stop=stop,
        is_error=is_error,
        plugins=plugins,
        model=model,
    )


# Live claude process groups, so a stop signal can reach them: each run starts
# a new session, which keeps the terminal's Ctrl-C from arriving on its own.
_live: set[subprocess.Popen] = set()
_live_lock = threading.Lock()
# Set by the stop-signal handler; no run starts after it.
_stopping = threading.Event()


class Interrupted(Exception):
    """A run was not started because the runner is shutting down."""


def _kill_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(KILL_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def kill_live_runs() -> None:
    with _live_lock:
        procs = list(_live)
    for proc in procs:
        _kill_group(proc)


def run_claude(
    cmd: Sequence[str],
    env: Mapping[str, str],
    scratch: Path,
    timeout: float,
    route_window: int | None,
) -> RunResult:
    """Run claude in `scratch` and parse its stream until it is done.

    The process is killed at an Agent call or when the route window closes
    (see read_stream), or after `timeout` seconds. stdin is /dev/null, so the
    CLI does not wait for piped input, and stderr is discarded. Raises
    Interrupted instead of starting once a stop signal has arrived.
    """
    # Started under the lock, so a stop signal either sees this process in _live
    # or is seen here before it starts.
    with _live_lock:
        if _stopping.is_set():
            raise Interrupted
        proc = subprocess.Popen(
            list(cmd), cwd=scratch, env=dict(env), stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            start_new_session=True,
        )
        _live.add(proc)
    timed_out = threading.Event()

    def expire() -> None:
        timed_out.set()
        _kill_group(proc)

    timer = threading.Timer(timeout, expire)
    timer.daemon = True
    timer.start()
    try:
        stream = _parse(proc.stdout, route_window)
    finally:
        timer.cancel()
        if proc.poll() is None:
            _kill_group(proc)
        exit_status = proc.wait()
        proc.stdout.close()
        with _live_lock:
            _live.discard(proc)
    return stream.finish(exit_status, timed_out.is_set())


# --- Cases ------------------------------------------------------------------

# A routing run's route is what the main thread loads in its first 3 calls.
ROUTE_WINDOW = 3
# Seconds. A negative case answers without tools, so it runs to the result.
ROUTING_TIMEOUT = 180
DEFAULT_BEHAVIOR_TIMEOUT = 300
SHELL_ASSERT_TIMEOUT = 60
CASE_KEYS = {"prompt", "allowed_tools", "timeout", "stage", "assert"}


@dataclass(frozen=True)
class RoutingCase:
    """An evals/routing.yaml entry. `targets` holds the names that pass it:
    the `expect` name or the `any_of` members; empty for `expect: none`."""

    id: str
    prompt: str
    targets: frozenset[str]


@dataclass(frozen=True)
class BehaviorCase:
    """An evals/behavior/<dir>/case.yaml. `fixture` is the case's fixture/
    directory, or None when it has none (an empty fixture)."""

    id: str
    prompt: str
    allowed_tools: tuple[str, ...]
    timeout: float
    stage: bool
    asserts: tuple[dict, ...]
    fixture: Path | None


Case = RoutingCase | BehaviorCase


def _load_yaml(path: Path, where: str) -> object:
    try:
        return yaml.safe_load(path.read_text())
    except (OSError, yaml.YAMLError) as err:
        raise SetupError(f"{where}: cannot load {path}: {err}") from None


def routing_ids(keys: Sequence[str]) -> list[str]:
    """`routing/<key>` per entry; a key used more than once is numbered on
    every use, in file order (`routing/none-1`, `routing/none-2`)."""
    total = {key: keys.count(key) for key in keys}
    seen: dict[str, int] = {}
    ids = []
    for key in keys:
        if total[key] == 1:
            ids.append(f"routing/{key}")
        else:
            seen[key] = seen.get(key, 0) + 1
            ids.append(f"routing/{key}-{seen[key]}")
    return ids


def load_routing(path: Path) -> list[RoutingCase]:
    entries = _load_yaml(path, "evals/routing.yaml")
    if not isinstance(entries, list):
        raise SetupError("evals/routing.yaml: expected a list of entries")
    parsed = []
    for n, entry in enumerate(entries, 1):
        where = f"evals/routing.yaml entry {n}"
        if not isinstance(entry, dict) or not isinstance(entry.get("prompt"), str):
            raise SetupError(f"{where}: needs a prompt")
        if ("expect" in entry) == ("any_of" in entry):
            raise SetupError(f"{where}: needs exactly one of expect or any_of")
        if "expect" in entry:
            expect = entry["expect"]
            if not isinstance(expect, str) or not expect:
                raise SetupError(f"{where}: expect names a skill, an agent, or none")
            parsed.append((expect, frozenset() if expect == "none" else frozenset({expect})))
        else:
            members = entry["any_of"]
            if not isinstance(members, list) or not members or not all(
                isinstance(m, str) and m for m in members
            ):
                raise SetupError(f"{where}: any_of is a non-empty list of names")
            parsed.append((members[0], frozenset(members)))
    ids = routing_ids([key for key, _ in parsed])
    return [
        RoutingCase(id=case_id, prompt=entry["prompt"], targets=targets)
        for case_id, entry, (_, targets) in zip(ids, entries, parsed)
    ]


def load_behavior(case_dir: Path) -> BehaviorCase:
    case_id = f"behavior/{case_dir.name}"
    data = _load_yaml(case_dir / "case.yaml", case_id)
    if not isinstance(data, dict) or not isinstance(data.get("prompt"), str):
        raise SetupError(f"{case_id}: case.yaml needs a prompt")
    if unknown := sorted(set(data) - CASE_KEYS):
        raise SetupError(f"{case_id}: unknown case.yaml keys {unknown}")
    asserts = data.get("assert")
    if not isinstance(asserts, list) or not asserts:
        raise SetupError(f"{case_id}: assert needs at least one assertion")
    for assertion in asserts:
        if problem := assertion_problem(assertion):
            raise SetupError(f"{case_id}: {problem}")
    tools = data.get("allowed_tools") or []
    if not isinstance(tools, list) or not all(isinstance(t, str) for t in tools):
        raise SetupError(f"{case_id}: allowed_tools is a list of tool rules")
    fixture = case_dir / "fixture"
    if fixture.is_dir() and not (fixture / "before").is_dir():
        raise SetupError(f"{case_id}: fixture/ needs a before/ directory")
    return BehaviorCase(
        id=case_id,
        prompt=data["prompt"],
        allowed_tools=tuple(tools),
        timeout=float(data.get("timeout", DEFAULT_BEHAVIOR_TIMEOUT)),
        stage=bool(data.get("stage", False)),
        asserts=tuple(asserts),
        fixture=fixture if fixture.is_dir() else None,
    )


def load_cases(root: Path) -> list[Case]:
    """Every case under `root/evals/`: routing entries first, then behavior
    cases by directory name. Raises SetupError on a malformed case."""
    evals = root / "evals"
    cases: list[Case] = list(load_routing(evals / "routing.yaml"))
    behavior = evals / "behavior"
    if behavior.is_dir():
        cases += [load_behavior(d) for d in sorted(behavior.iterdir())
                  if (d / "case.yaml").is_file()]
    return cases


def select(cases: Sequence[Case], pattern: str | None) -> list[Case]:
    """The cases whose id matches the --only glob; all of them for None."""
    if pattern is None:
        return list(cases)
    chosen = [c for c in cases if fnmatch.fnmatchcase(c.id, pattern)]
    if not chosen:
        raise SetupError(
            f"--only {pattern!r} matches no case. Ids look like routing/why, "
            "routing/none-1, or behavior/commit-conventions."
        )
    return chosen


# --- Fixtures ---------------------------------------------------------------

FIXTURE_IDENTITY = (("user.name", "evals"), ("user.email", "evals@localhost"))


def _fixture_git_env() -> dict[str, str]:
    """No GIT_* variables from a calling hook, and no global or system
    config, so signing, hooks, or templates on this machine stay out."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return env


def prepare_fixture(fixture: Path | None, scratch: Path, stage: bool) -> None:
    """Make `scratch` a git repo holding the case's fixture.

    The repo gets the fixed identity in its local config; before/ becomes
    exactly one commit; after/ is then copied over as uncommitted changes,
    staged when `stage` is set. With no fixture the repo is left empty, with
    the identity and no commit.
    """
    env = _fixture_git_env()

    def run_git(*args: str) -> None:
        subprocess.run(["git", "-C", str(scratch), *args], env=env, check=True,
                       capture_output=True)

    run_git("init", "-q", "-b", "main")
    for key, value in FIXTURE_IDENTITY:
        run_git("config", key, value)
    if fixture is None:
        return
    shutil.copytree(fixture / "before", scratch, dirs_exist_ok=True)
    run_git("add", "-A")
    run_git("commit", "-q", "-m", "Initial commit")
    after = fixture / "after"
    if after.is_dir():
        shutil.copytree(after, scratch, dirs_exist_ok=True)
        if stage:
            run_git("add", "-A")


# --- Assertions -------------------------------------------------------------
#
# Each assertion is a one-key mapping, {type: spec}. Every regex is applied
# with re.search and no default flags; a case writes (?i) or (?m) inline.


def _patterns_problem(spec: dict, keys: Sequence[str]) -> str | None:
    for key in keys:
        patterns = spec.get(key, [])
        if not isinstance(patterns, list) or not all(isinstance(p, str) for p in patterns):
            return f"{key} is a list of regexes"
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as err:
                return f"bad regex {pattern!r}: {err}"
    return None


def _order_problem(spec: object) -> str | None:
    if not isinstance(spec, dict) or not all(isinstance(spec.get(k), str) for k in ("first", "before")):
        return "order needs first: <tool[:regex]> and before: <tool>"
    return _patterns_problem({"first": [spec["first"].partition(":")[2]]}, ["first"])


def _names_problem(kind: str) -> object:
    def problem(spec: object) -> str | None:
        if not isinstance(spec, list) or not spec or not all(isinstance(s, str) for s in spec):
            return f"{kind} is a non-empty list of names"
        return None
    return problem


def _final_text_problem(spec: object) -> str | None:
    if not isinstance(spec, dict) or set(spec) - {"match", "not_match"} or not spec:
        return "final_text takes match and/or not_match"
    return _patterns_problem(spec, ["match", "not_match"])


def _shell_problem(spec: object) -> str | None:
    if not isinstance(spec, dict) or not isinstance(spec.get("run"), str) \
            or set(spec) - {"run", "match", "not_match"}:
        return "shell takes run and match and/or not_match"
    return _patterns_problem(spec, ["match", "not_match"])


ASSERTION_SHAPES = {
    "order": _order_problem,
    "tool_not_called": _names_problem("tool_not_called"),
    "final_text": _final_text_problem,
    "shell": _shell_problem,
    "no_paths": _names_problem("no_paths"),
}


def assertion_problem(assertion: object) -> str | None:
    """Why `assertion` is malformed, or None when it is well formed."""
    if not isinstance(assertion, dict) or len(assertion) != 1:
        return f"an assertion is a one-key mapping, not {assertion!r}"
    [(kind, spec)] = assertion.items()
    if kind not in ASSERTION_SHAPES:
        return f"unknown assertion type {kind!r} (known: {', '.join(ASSERTION_SHAPES)})"
    return ASSERTION_SHAPES[kind](spec)


def _is_tool(call: ToolCall, tool: str) -> bool:
    return call.name == tool or (call.name in AGENT_TOOLS and tool in AGENT_TOOLS)


def _call_subject(call: ToolCall) -> str:
    """What a `<tool>:<regex>` regex runs against: a Bash call's command,
    otherwise the call's whole input as JSON."""
    if call.name == "Bash":
        return str(call.input.get("command", ""))
    return json.dumps(call.input, sort_keys=True)


def _first_index(calls: Sequence[ToolCall], tool: str, pattern: str = "") -> int | None:
    for index, c in enumerate(calls):
        if _is_tool(c, tool) and (not pattern or re.search(pattern, _call_subject(c))):
            return index
    return None


def _regex_failure(text: str, spec: dict, what: str) -> str | None:
    for pattern in spec.get("match", ()):
        if not re.search(pattern, text):
            return f"{what} does not match {pattern!r}"
    for pattern in spec.get("not_match", ()):
        if re.search(pattern, text):
            return f"{what} matches {pattern!r}"
    return None


def _check_order(spec: dict, result: RunResult, scratch: Path, env: Mapping[str, str]) -> str | None:
    tool, _, pattern = spec["first"].partition(":")
    first = _first_index(result.tool_calls, tool, pattern)
    if first is None:
        return f"order: no {spec['first']} call"
    before = _first_index(result.tool_calls, spec["before"])
    if before is not None and before < first:
        return f"order: {spec['before']} (call {before + 1}) came before {spec['first']} (call {first + 1})"
    return None


def _check_tool_not_called(spec: list, result: RunResult, scratch: Path,
                           env: Mapping[str, str]) -> str | None:
    called = sorted({c.name for c in result.tool_calls for tool in spec if _is_tool(c, tool)})
    return f"tool_not_called: {', '.join(called)} called" if called else None


def _check_final_text(spec: dict, result: RunResult, scratch: Path,
                      env: Mapping[str, str]) -> str | None:
    failure = _regex_failure(result.final_text, spec, "final_text")
    return failure and f"{failure}; text: {result.final_text[:300]!r}"


def _check_shell(spec: dict, result: RunResult, scratch: Path, env: Mapping[str, str]) -> str | None:
    try:
        proc = subprocess.run(spec["run"], shell=True, cwd=scratch, env=dict(env),
                              stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              timeout=SHELL_ASSERT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return f"shell `{spec['run']}` timed out"
    return _regex_failure(proc.stdout, spec, f"shell `{spec['run']}`")


def _check_no_paths(spec: list, result: RunResult, scratch: Path, env: Mapping[str, str]) -> str | None:
    found = sorted({str(p.relative_to(scratch)) for pattern in spec for p in scratch.glob(pattern)})
    return f"no_paths: found {', '.join(found)}" if found else None


CHECKS = {
    "order": _check_order,
    "tool_not_called": _check_tool_not_called,
    "final_text": _check_final_text,
    "shell": _check_shell,
    "no_paths": _check_no_paths,
}


def check_assertion(assertion: dict, result: RunResult, scratch: Path,
                    env: Mapping[str, str]) -> str | None:
    """Why the run fails a well-formed assertion, or None when it holds.

    Tool calls are judged in stream order, subagent and fork calls included.
    `shell` runs in `scratch` with `env`; `no_paths` globs relative to it.
    """
    [(kind, spec)] = assertion.items()
    return CHECKS[kind](spec, result, scratch, env)


# --- Scoring ----------------------------------------------------------------


@dataclass(frozen=True)
class Verdict:
    """One run judged. Error runs are not `counted`; timeouts are, as fails."""

    passed: bool
    counted: bool
    detail: str


def judge(case: Case, result: RunResult, scratch: Path, env: Mapping[str, str]) -> Verdict:
    """A routing run passes when its route holds a target (other loads
    alongside it notwithstanding), or is empty for `expect: none`; a behavior
    run passes when every assertion holds."""
    if result.error_class == "error":
        return Verdict(False, False, f"error: {result.final_text[:120]!r}")
    if result.error_class == "timeout":
        return Verdict(False, True, "timeout")
    if isinstance(case, RoutingCase):
        routes = set(result.routes)
        passed = bool(case.targets & routes) if case.targets else not routes
        return Verdict(passed, True, "route: " + (", ".join(result.routes) or "none"))
    failures = [f for a in case.asserts if (f := check_assertion(a, result, scratch, env))]
    return Verdict(not failures, True, "; ".join(failures) or "every assertion holds")


@dataclass(frozen=True)
class Rate:
    passes: int
    counted: int
    errors: int

    @classmethod
    def of(cls, verdicts: Iterable[Verdict]) -> Rate:
        verdicts = list(verdicts)
        counted = [v for v in verdicts if v.counted]
        return cls(passes=sum(v.passed for v in counted), counted=len(counted),
                   errors=len(verdicts) - len(counted))

    @property
    def passing(self) -> bool:
        return 3 * self.passes >= 2 * self.counted

    def __str__(self) -> str:
        text = f"{self.passes}/{self.counted}"
        return f"{text}, {self.errors} err" if self.errors else text


def status(base: Rate, head: Rate) -> str:
    """A side passes at >= 2/3 of its counted runs; fewer than 2 counted
    runs on either side is INCONCLUSIVE, so errors never pose as regressions."""
    if base.counted < 2 or head.counted < 2:
        return "INCONCLUSIVE"
    if base.passing and head.passing:
        return "PASS"
    if not base.passing and not head.passing:
        return "FAIL"
    return "REGRESSION" if base.passing else "FIXED"


def exit_code(statuses: Iterable[str]) -> int:
    return 1 if "REGRESSION" in statuses else 0


@dataclass(frozen=True)
class Row:
    case_id: str
    base: Rate
    head: Rate

    @property
    def status(self) -> str:
        return status(self.base, self.head)


# --- Report -----------------------------------------------------------------

NOTABLE = ("REGRESSION", "FIXED", "INCONCLUSIVE")
STATUSES = (*NOTABLE, "PASS", "FAIL")
TIERS = (("routing/", "Routing"), ("behavior/", "Behavior"))


def render_report(
    rows: Sequence[Row], *, base_sha: str, base_ref: str, head_sha: str, dirty: bool,
    model: str, runs: int, plugins: Sequence[str] = (),
) -> str:
    """The markdown report: summary, notable cases, a table per tier, marker."""
    head = head_sha[:12] + ("-dirty" if dirty else "")
    counts = {s: sum(r.status == s for r in rows) for s in STATUSES}
    lines = [
        "## Eval report",
        "",
        f"{len(rows)} cases, {runs} runs per case per side, base `{base_ref}` "
        f"(`{base_sha[:12]}`) vs head `{head}`: "
        + " · ".join(f"{counts[s]} {s}" for s in STATUSES),
        "",
    ]
    notable = [r for s in NOTABLE for r in rows if r.status == s]
    lines += [f"- {r.status} `{r.case_id}`: base {r.base}; head {r.head}" for r in notable] \
        or ["No regressions, fixes, or inconclusive cases."]
    if plugins:
        lines += ["", f"> Isolation warning: init listed plugins ({', '.join(plugins)}); "
                      "they may have competed with the suite."]
    for prefix, title in TIERS:
        tier = [r for r in rows if r.case_id.startswith(prefix)]
        if not tier:
            continue
        lines += ["", f"### {title}", "", "| Case | Base | Head | Status |", "|---|---|---|---|"]
        lines += [f"| `{r.case_id}` | {r.base} | {r.head} | {r.status} |" for r in tier]
    lines += ["", f"<!-- evals: base={base_sha[:12]} head={head} model={model} runs={runs} -->", ""]
    return "\n".join(lines)


# --- Running the cases ------------------------------------------------------


@dataclass(frozen=True)
class Outcome:
    case_id: str
    side: str
    verdict: Verdict
    plugins: tuple[str, ...]
    model: str


def run_one(case: Case, side: Side, auth: Mapping[str, str], model: str | None) -> Outcome:
    """One run of `case` against `side` in a fresh scratch dir, judged and
    cleaned up. Routing runs start in an empty directory.

    An exception from the run (fixture setup, parsing, an assertion) comes
    back as an uncounted error outcome naming it, so one bad run cannot abort
    the others or the report. Interrupted still propagates.
    """
    scratch = Path(tempfile.mkdtemp(prefix="evals-run-"))
    try:
        env = child_env(side.config, side.home, auth)
        if isinstance(case, BehaviorCase):
            prepare_fixture(case.fixture, scratch, case.stage)
            cmd = claude_command(case.prompt, allowed_tools=case.allowed_tools, model=model)
            result = run_claude(cmd, env, scratch, case.timeout, route_window=None)
        else:
            cmd = claude_command(case.prompt, model=model)
            result = run_claude(cmd, env, scratch, ROUTING_TIMEOUT, route_window=ROUTE_WINDOW)
        # Shell assertions get the run's HOME and config, but not the token.
        verdict = judge(case, result, scratch, child_env(side.config, side.home, {}))
        return Outcome(case.id, side.name, verdict, result.plugins, result.model)
    except Interrupted:
        raise
    except Exception as err:
        verdict = Verdict(False, False, f"error: {type(err).__name__}: {str(err)[:200]}")
        return Outcome(case.id, side.name, verdict, (), "")
    finally:
        remove_tree(scratch)


def run_all(cases: Sequence[Case], sides: Sides, auth: Mapping[str, str], model: str | None,
            runs: int, jobs: int) -> list[Outcome]:
    """Every (case, side, run) through a pool of `jobs` workers, base and head
    interleaved so both meet the same rate limits. Progress goes to stderr."""
    work = [(case, side, n) for case in cases for n in range(1, runs + 1)
            for side in (sides.base, sides.head)]
    outcomes = []
    pool = ThreadPoolExecutor(max_workers=jobs)
    try:
        futures = {pool.submit(run_one, case, side, auth, model): (case, side, n)
                   for case, side, n in work}
        for done, future in enumerate(as_completed(futures), 1):
            case, side, n = futures[future]
            outcome = future.result()
            outcomes.append(outcome)
            verdict = outcome.verdict
            mark = "pass" if verdict.passed else "fail" if verdict.counted else "error"
            print(f"[{done}/{len(work)}] {side.name} {case.id} #{n}: {mark} ({verdict.detail})",
                  file=sys.stderr)
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
    return outcomes


def rows_of(cases: Sequence[Case], outcomes: Sequence[Outcome]) -> list[Row]:
    def rate(case_id: str, side: str) -> Rate:
        return Rate.of(o.verdict for o in outcomes if o.case_id == case_id and o.side == side)
    return [Row(c.id, rate(c.id, "base"), rate(c.id, "head")) for c in cases]


# --- Entry point ------------------------------------------------------------


def suite_root() -> Path:
    return Path(git(Path(__file__).resolve().parent, "rev-parse", "--show-toplevel"))


def head_revision(head: Path) -> tuple[str, bool]:
    """HEAD's sha, and whether the working tree differs from it (untracked
    files included: a new command file is loaded without being committed)."""
    return git(head, "rev-parse", "HEAD"), bool(git(head, "status", "--porcelain"))


# Each one stops the runner. Runs start their own session, so a signal sent
# to the runner reaches its claude children only through this handler.
STOP_SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)


def raise_interrupt(signum: int, frame: object) -> None:
    """Stop the claude process groups, then unwind through cleanup."""
    _stopping.set()
    kill_live_runs()
    raise KeyboardInterrupt


def install_stop_handlers() -> None:
    for signum in STOP_SIGNALS:
        signal.signal(signum, raise_interrupt)


def run(args: argparse.Namespace) -> int:
    head = suite_root()
    try:
        cases = select(load_cases(head), args.only)
        setup = preflight(head, args.base, os.environ, args.env_file)
    except SetupError as err:
        print(f"run-evals: {err}", file=sys.stderr)
        return 2
    head_sha, dirty = head_revision(head)
    print(f"run-evals: {len(cases)} cases x {args.runs} runs x 2 sides, {args.jobs} jobs; "
          f"base {args.base} ({setup.base_sha[:12]})", file=sys.stderr)
    with eval_sides(head, setup.base_sha) as sides:
        outcomes = run_all(cases, sides, setup.auth, args.model, args.runs, args.jobs)
    rows = rows_of(cases, outcomes)
    report = render_report(
        rows, base_sha=setup.base_sha, base_ref=args.base, head_sha=head_sha, dirty=dirty,
        model=next((o.model for o in outcomes if o.model), args.model or "unknown"),
        runs=args.runs, plugins=sorted({p for o in outcomes for p in o.plugins}),
    )
    if args.out:
        Path(args.out).write_text(report)
        print(f"run-evals: report written to {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(report)
    return exit_code(r.status for r in rows)


def positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, not {value}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog="Case ids: routing/<target> (repeats numbered, e.g. routing/none-1) "
               "and behavior/<dir>.",
    )
    parser.add_argument("--base", default="main", help="ref to compare against (default: main)")
    parser.add_argument("--runs", type=positive_int, default=3,
                        help="runs per case per side (default: 3)")
    parser.add_argument("--jobs", type=positive_int, default=4,
                        help="claude processes at once (default: 4)")
    parser.add_argument("--model", help="model for every run (default: the config's)")
    parser.add_argument("--only", metavar="GLOB", help="run only the case ids matching GLOB")
    parser.add_argument("--out", metavar="FILE", help="write the report here, not to stdout")
    parser.add_argument("--env-file", type=Path, metavar="FILE",
                        help="dotenv file holding the auth variable (default: <suite root>/.env)")
    args = parser.parse_args()
    install_stop_handlers()
    try:
        return run(args)
    except KeyboardInterrupt:
        print("run-evals: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
