#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Run the routing and behavior evals against a base ref and the working tree.

Each side gets its own Claude Code config directory built from that side's
suite, so the same prompts run once against `--base` (a detached worktree) and
once against this working tree, uncommitted edits included.

    scripts/run-evals.py                 compare against main
    scripts/run-evals.py --base REF      compare against another ref

Auth comes from CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY in the
environment, or else from `.env` at the suite root (see `.env.example`). The
value is placed only in the environment of the `claude` subprocesses; it is
never printed or written anywhere else.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
from collections.abc import Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

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


def preflight(head: Path, base_ref: str, environ: Mapping[str, str]) -> Setup:
    """Check the prerequisites for a run, or raise SetupError with the fix.

    Also prunes worktree records left by a run that was killed before cleanup.
    """
    if shutil.which("claude") is None:
        raise SetupError(
            "claude is not on PATH. Install Claude Code "
            "(https://docs.claude.com/en/docs/claude-code) and re-run."
        )
    auth = resolve_auth(environ, head / ".env")
    if auth is None:
        raise SetupError(
            "no auth for claude. Run `claude setup-token`, then copy "
            f"{head / '.env.example'} to {head / '.env'} and fill in "
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


def tracked_skills(root: Path) -> list[str]:
    """Names of the skills whose SKILL.md is tracked in git at `root`.

    Untracked skill directories, skills/synced/ among them, are left out so
    both sides of a comparison see the same kind of suite.
    """
    paths = git(root, "ls-files", "--", "skills/*/SKILL.md").splitlines()
    return sorted({Path(p).parent.name for p in paths})


def build_config(root: Path) -> Path:
    """Build a CLAUDE_CONFIG_DIR exposing the Claude Code suite at `root`.

    The directory is private (mode 0700) and holds links to the agents,
    commands, and index under platforms/claude/, one link per tracked skill,
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
    for name in tracked_skills(root):
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


@contextmanager
def config_dir(root: Path) -> Iterator[Path]:
    config = build_config(root)
    try:
        yield config
    finally:
        remove_tree(config)


@dataclass(frozen=True)
class Sides:
    base_config: Path
    head_config: Path


@contextmanager
def eval_sides(head: Path, base_sha: str) -> Iterator[Sides]:
    """Yield a config for each side; remove both and the base worktree on exit."""
    with base_worktree(head, base_sha) as base_root:
        with config_dir(base_root) as base_cfg, config_dir(head) as head_cfg:
            yield Sides(base_config=base_cfg, head_config=head_cfg)


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
    config: Path, auth: Mapping[str, str], parent: Mapping[str, str] = os.environ
) -> dict[str, str]:
    """The environment for a claude subprocess using `config`.

    Every inherited CLAUDE* variable goes (a parent Claude Code session exports
    CLAUDECODE, session ids, and effort), so a run from inside an agent matches
    a run from a plain terminal; then the config dir and auth are set.
    """
    env = {k: v for k, v in parent.items() if not k.startswith("CLAUDE")}
    env["CLAUDE_CONFIG_DIR"] = str(config)
    env.update(auth)
    return env


@dataclass(frozen=True)
class ToolCall:
    name: str
    input: dict
    # None on the main thread; the spawning Agent call's id inside a subagent.
    parent_tool_use_id: str | None


@dataclass(frozen=True)
class RunResult:
    """What one claude run did.

    tool_calls   every tool call in stream order, subagent calls included
    routes       skills and agents the main thread loaded within the window
    final_text   the result text, or the last main-thread text if killed early
    stop         why reading stopped: route, window, result, or eof
    exit_status  the process exit status; None when parsed from a recording
    error_class  none, timeout, or error; only `none` runs count toward a rate
    plugins      plugins the init event reports; any at all breaks isolation
    """

    tool_calls: tuple[ToolCall, ...]
    routes: tuple[str, ...]
    final_text: str
    stop: str
    exit_status: int | None
    error_class: str
    plugins: tuple[str, ...]


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

    def finish(self, exit_status: int | None, timed_out: bool) -> RunResult:
        return RunResult(
            tool_calls=self.tool_calls,
            routes=self.routes,
            final_text=self.final_text,
            stop=self.stop,
            exit_status=exit_status,
            error_class=classify(self.stop, self.is_error, exit_status, timed_out),
            plugins=self.plugins,
        )


def read_stream(lines: Iterable[str], route_window: int | None) -> RunResult:
    """Parse stream-json lines from a live process or a recording.

    With a route window, reading stops at the `assistant` event carrying the
    first route (the tool starts executing there) or once the main thread has
    made `route_window` calls without one. With None it reads to the end.
    """
    return _parse(lines, route_window).finish(exit_status=None, timed_out=False)


def _parse(lines: Iterable[str], route_window: int | None) -> _Stream:
    calls: list[ToolCall] = []
    routes: list[str] = []
    plugins: tuple[str, ...] = ()
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
        elif kind == "result":
            result_text = event.get("result") or ""
            is_error = bool(event.get("is_error"))
            stop = "result"
            break
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
            if route_window is not None and routes:
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
    )


# Live claude process groups, so a SIGINT can reach them: each run starts a
# new session, which keeps the terminal's Ctrl-C from arriving on its own.
_live: set[subprocess.Popen] = set()
_live_lock = threading.Lock()


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

    The process is killed at the first route or when the route window closes
    (see read_stream), or after `timeout` seconds. stdin is /dev/null, so the
    CLI does not wait for piped input, and stderr is discarded.
    """
    proc = subprocess.Popen(
        list(cmd), cwd=scratch, env=dict(env), stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
        start_new_session=True,
    )
    with _live_lock:
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


# --- Entry point ------------------------------------------------------------


def suite_root() -> Path:
    return Path(git(Path(__file__).resolve().parent, "rev-parse", "--show-toplevel"))


def raise_interrupt(signum: int, frame: object) -> None:
    """SIGINT: stop the claude process groups, then unwind through cleanup."""
    kill_live_runs()
    raise KeyboardInterrupt


def run(args: argparse.Namespace) -> int:
    head = suite_root()
    try:
        setup = preflight(head, args.base, os.environ)
    except SetupError as err:
        print(f"run-evals: {err}", file=sys.stderr)
        return 2
    with eval_sides(head, setup.base_sha) as sides:
        print(f"base {setup.base_sha[:12]}: config at {sides.base_config}")
        print(f"head {head}: config at {sides.head_config}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="main", help="ref to compare against (default: main)")
    args = parser.parse_args()
    signal.signal(signal.SIGINT, raise_interrupt)
    try:
        return run(args)
    except KeyboardInterrupt:
        print("run-evals: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
