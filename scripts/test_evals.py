#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Tests for the eval runner. No model calls: the stream parser reads recordings.

    scripts/test_evals.py           run every test
    scripts/test_evals.py -v        name each test as it runs

The scripts under test have hyphenated names, so they load through importlib.
"""

from __future__ import annotations

import importlib.util
import json
import os
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
RECORDINGS = ROOT / "evals" / "recordings"


def load_script(filename: str):
    sys.dont_write_bytecode = True  # no scripts/__pycache__ left behind
    name = filename.removesuffix(".py").replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolve annotations through here
    spec.loader.exec_module(module)
    return module


run_evals = load_script("run-evals.py")


def read_recording(name: str, route_window: int | None = 3):
    with (RECORDINGS / f"{name}.jsonl").open() as lines:
        return run_evals.read_stream(lines, route_window)


class StreamParserTest(unittest.TestCase):
    def test_skill_call_is_a_route_but_reading_continues(self):
        # The recording was cut right after the Skill call, so the stream
        # ends without a result: the parser kept reading instead of stopping.
        result = read_recording("route-skill")
        self.assertEqual(result.routes, ("docker-best-practices",))
        self.assertEqual(result.stop, "eof")
        self.assertEqual([c.name for c in result.tool_calls], ["Skill"])

    def test_skill_loads_are_collected_until_the_window_closes(self):
        lines = [
            assistant_tool_use("Skill", {"skill": "coding-guardrails"}, parent=None),
            assistant_tool_use("Skill", {"skill": "backend-patterns"}, parent=None),
            assistant_tool_use("Read", {"file_path": "app.py"}, parent=None),
            assistant_tool_use("Skill", {"skill": "test-strategy"}, parent=None),
        ]
        result = run_evals.read_stream(lines, route_window=3)
        self.assertEqual(result.routes, ("coding-guardrails", "backend-patterns"))
        self.assertEqual(result.stop, "window")
        self.assertEqual(result.error_class, "none")
        self.assertEqual(len(result.tool_calls), 3)

    def test_skill_load_then_an_answer_reads_to_the_result(self):
        lines = [
            assistant_tool_use("Skill", {"skill": "why"}, parent=None),
            json.dumps({"type": "result", "is_error": False, "result": "Because."}),
        ]
        result = run_evals.read_stream(lines, route_window=3)
        self.assertEqual((result.routes, result.stop), (("why",), "result"))
        self.assertEqual(result.final_text, "Because.")

    def test_agent_call_stops_the_stream_after_earlier_skill_loads(self):
        lines = [
            assistant_tool_use("Read", {"file_path": "skills/why/SKILL.md"}, parent=None),
            assistant_tool_use("Agent", {"subagent_type": "debugger"}, parent=None),
            assistant_tool_use("Read", {"file_path": "a.py"}, parent=None),
        ]
        result = run_evals.read_stream(lines, route_window=3)
        self.assertEqual(result.routes, ("why", "debugger"))
        self.assertEqual(result.stop, "route")
        self.assertEqual(len(result.tool_calls), 2)

    def test_init_event_model_is_reported(self):
        self.assertEqual(read_recording("no-route").model, "claude-sonnet-5-5")

    def test_agent_call_routes_to_its_subagent_type(self):
        result = read_recording("route-agent")
        self.assertEqual(result.routes, ("security-analyst",))
        self.assertEqual(result.stop, "route")
        self.assertEqual(result.tool_calls[0].name, "Agent")
        self.assertIsNone(result.tool_calls[0].parent_tool_use_id)

    def test_read_of_a_skill_file_routes_to_that_skill(self):
        result = read_recording("route-read")
        self.assertEqual(result.routes, ("git-conventions",))
        self.assertEqual(result.stop, "eof")  # cut after the Read; no kill there

    def test_answer_without_tools_has_no_route_and_keeps_the_final_text(self):
        result = read_recording("no-route")
        self.assertEqual(result.routes, ())
        self.assertEqual(result.tool_calls, ())
        self.assertEqual(result.stop, "result")
        self.assertEqual(result.error_class, "none")
        self.assertTrue(result.final_text.startswith("A process is an independent"))

    def test_window_closes_after_three_calls_without_a_route(self):
        result = read_recording("window")
        self.assertEqual(result.routes, ())
        self.assertEqual(result.stop, "window")
        self.assertEqual(result.error_class, "none")
        self.assertEqual(
            [c.input["file_path"] for c in result.tool_calls],
            ["$TMP/a.txt", "$TMP/b.txt", "$TMP/c.txt"],
        )

    def test_window_counts_only_the_calls_it_allows(self):
        result = read_recording("window", route_window=2)
        self.assertEqual(result.stop, "window")
        self.assertEqual(len(result.tool_calls), 2)

    def test_no_window_reads_to_the_end(self):
        result = read_recording("window", route_window=None)
        self.assertEqual(result.stop, "eof")
        self.assertEqual(len(result.tool_calls), 3)

    def test_error_result_classifies_as_error_despite_success_subtype(self):
        result = read_recording("error")
        self.assertEqual(result.error_class, "error")
        self.assertEqual(result.stop, "result")
        self.assertIn("no-such-model-xyz", result.final_text)

    def test_init_event_plugins_are_reported(self):
        result = read_recording("no-route")
        self.assertEqual(
            set(result.plugins),
            {"cc-plugin-agents-md", "cc-plugin-telemetry", "cc-plugin-plugin-authoring"},
        )

    def test_subagent_calls_are_kept_but_do_not_count_toward_the_window(self):
        lines = [
            assistant_tool_use("Agent", {"subagent_type": "debugger"}, parent=None),
            assistant_tool_use("Bash", {"command": "ls"}, parent="toolu_parent"),
            assistant_tool_use("Bash", {"command": "ls"}, parent="toolu_parent"),
            assistant_tool_use("Skill", {"skill": "why"}, parent="toolu_parent"),
            assistant_tool_use("Read", {"file_path": "a.txt"}, parent=None),
        ]
        result = run_evals.read_stream(lines, route_window=None)
        self.assertEqual(len(result.tool_calls), 5)
        self.assertEqual(result.tool_calls[1].parent_tool_use_id, "toolu_parent")
        self.assertEqual(result.routes, ("debugger",))

    def test_background_subagent_run_reads_past_the_first_result(self):
        # /debugger launches the agent in the background: the main thread
        # returns a result at once, then the subagent works, then a second
        # main-thread turn ends with the result that matters.
        result = read_recording("subagent", route_window=None)
        self.assertEqual(result.stop, "result")
        self.assertEqual(result.error_class, "none")
        self.assertTrue(result.final_text.startswith("Fixed. An order of exactly 10"))
        agent_call = result.tool_calls[0]
        self.assertEqual((agent_call.name, agent_call.parent_tool_use_id), ("Agent", None))
        subagent_calls = [c.name for c in result.tool_calls
                          if c.parent_tool_use_id == "toolu_015KM4KLp8pnxHeXAW9JTrXc"]
        self.assertEqual(subagent_calls, ["Bash", "Bash", "Bash", "Edit", "Edit"])
        self.assertEqual(result.tool_calls[-1].parent_tool_use_id, None)

    def test_forked_command_calls_carry_the_fork_as_parent(self):
        result = read_recording("fork", route_window=None)
        self.assertEqual(
            [(c.name, c.parent_tool_use_id) for c in result.tool_calls],
            [("Read", "forked-command-code-review"), ("Glob", "forked-command-code-review")],
        )
        self.assertIn("db.py:25", result.final_text)
        self.assertEqual(result.error_class, "none")

    def test_command_whose_shell_injection_was_denied_is_an_error(self):
        # The CLI never calls the model and reports a clean, empty result.
        result = read_recording("command-denied", route_window=None)
        self.assertEqual(result.tool_calls, ())
        self.assertEqual(result.error_class, "error")

    def test_stderr_marker_in_a_tool_result_is_not_a_failed_command(self):
        # Only the CLI's own main-thread string message marks a denied `!`
        # line; a tool result that merely contains the text (a file being
        # read, a subagent's output) does not.
        def user(content, parent):
            return json.dumps({"type": "user", "parent_tool_use_id": parent,
                               "message": {"role": "user", "content": content}})
        tool_result = [{"type": "tool_result", "tool_use_id": "toolu_x",
                        "content": "<local-command-stderr>quoted</local-command-stderr>"}]
        clean = json.dumps({"type": "result", "is_error": False, "result": "Done."})
        for line in (user(tool_result, None), user(tool_result, "toolu_parent"),
                     user("<local-command-stderr>x</local-command-stderr>", "toolu_parent")):
            with self.subTest(line=line):
                result = run_evals.read_stream([line, clean], route_window=None)
                self.assertEqual(result.error_class, "none")

    def test_task_is_accepted_as_the_agent_tool_name(self):
        lines = [assistant_tool_use("Task", {"subagent_type": "Plan"}, parent=None)]
        self.assertEqual(run_evals.read_stream(lines, 3).routes, ("Plan",))


def assistant_tool_use(name: str, tool_input: dict, parent: str | None) -> str:
    return json.dumps({
        "type": "assistant",
        "parent_tool_use_id": parent,
        "message": {"content": [{"type": "tool_use", "id": "toolu_x", "name": name,
                                 "input": tool_input}]},
    })


# Stands in for claude: replays a recording, then sleeps and exits as told.
FAKE_CLAUDE = (
    "import sys, time\n"
    "sys.stdout.write(open(sys.argv[1]).read()); sys.stdout.flush()\n"
    "time.sleep(float(sys.argv[2])); sys.exit(int(sys.argv[3]))\n"
)


class RunClaudeTest(unittest.TestCase):
    def run_fake(self, recording: str | Path, sleep: float, exit_code: int, timeout: float,
                 route_window: int | None = 3):
        stream = recording if isinstance(recording, Path) else RECORDINGS / f"{recording}.jsonl"
        cmd = [sys.executable, "-c", FAKE_CLAUDE, str(stream), str(sleep), str(exit_code)]
        with tempfile.TemporaryDirectory() as scratch:
            return run_evals.run_claude(cmd, dict(os.environ), Path(scratch), timeout,
                                        route_window)

    def test_process_is_killed_at_an_agent_call(self):
        result = self.run_fake("route-agent", sleep=60, exit_code=0, timeout=30)
        self.assertEqual(result.stop, "route")
        self.assertEqual(result.error_class, "none")
        self.assertNotEqual(result.exit_status, 0)

    def test_process_outlives_a_skill_load_until_the_window_closes(self):
        with tempfile.TemporaryDirectory() as tmp:
            stream = Path(tmp) / "stream.jsonl"
            stream.write_text("\n".join([
                assistant_tool_use("Skill", {"skill": "why"}, parent=None),
                assistant_tool_use("Bash", {"command": "git log"}, parent=None),
                assistant_tool_use("Bash", {"command": "git blame"}, parent=None),
            ]) + "\n")
            result = self.run_fake(stream, sleep=60, exit_code=0, timeout=30)
        self.assertEqual((result.routes, result.stop), (("why",), "window"))
        self.assertEqual(result.error_class, "none")

    def test_silent_process_times_out(self):
        result = self.run_fake("route-skill", sleep=60, exit_code=0, timeout=0.5,
                               route_window=None)
        self.assertEqual(result.error_class, "timeout")

    def test_nonzero_exit_after_a_clean_result_is_an_error(self):
        result = self.run_fake("no-route", sleep=0, exit_code=1, timeout=30)
        self.assertEqual(result.exit_status, 1)
        self.assertEqual(result.error_class, "error")

    def test_interrupt_stops_live_runs(self):
        # What the SIGINT handler does before cleanup unwinds.
        results = []
        worker = threading.Thread(target=lambda: results.append(
            self.run_fake("window", sleep=60, exit_code=0, timeout=60, route_window=None)))
        worker.start()
        deadline = time.monotonic() + 10
        while not run_evals._live and time.monotonic() < deadline:
            time.sleep(0.05)
        run_evals.kill_live_runs()
        worker.join(15)
        self.assertFalse(worker.is_alive())
        self.assertEqual(results[0].error_class, "error")

    def test_sigterm_and_sighup_stop_the_runner_like_sigint(self):
        # Runs start their own session, so only the runner's handler can reach
        # them; a SIGTERM or SIGHUP that skipped it would orphan them.
        saved = {s: signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
        self.addCleanup(lambda: [signal.signal(s, h) for s, h in saved.items()])
        self.addCleanup(run_evals._stopping.clear)
        run_evals.install_stop_handlers()
        for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            with self.subTest(signal=signum.name):
                run_evals._stopping.clear()
                with self.assertRaises(KeyboardInterrupt):
                    os.kill(os.getpid(), signum)
                    time.sleep(1)  # the handler runs between bytecodes
                self.assertTrue(run_evals._stopping.is_set())

    def test_clean_exit_after_a_result_counts(self):
        result = self.run_fake("no-route", sleep=0, exit_code=0, timeout=30)
        self.assertEqual((result.exit_status, result.error_class), (0, "none"))


class ClassifyTest(unittest.TestCase):
    def test_timeout_wins_over_everything(self):
        self.assertEqual(run_evals.classify("eof", False, -15, timed_out=True), "timeout")

    def test_killed_at_a_route_is_not_an_error(self):
        self.assertEqual(run_evals.classify("route", False, 143, timed_out=False), "none")

    def test_nonzero_exit_after_a_result_is_an_error(self):
        self.assertEqual(run_evals.classify("result", False, 1, timed_out=False), "error")

    def test_stream_ending_without_a_result_is_an_error(self):
        self.assertEqual(run_evals.classify("eof", False, 0, timed_out=False), "error")


class LoadEnvTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / ".env"

    def tearDown(self):
        self.dir.cleanup()

    def test_reads_pairs_skipping_comments_and_blank_lines(self):
        self.path.write_text("# a comment\n\nFOO=bar\n  # indented comment\nBAZ = qux \n")
        self.assertEqual(run_evals.load_env(self.path), {"FOO": "bar", "BAZ": "qux"})

    def test_strips_matching_quotes(self):
        self.path.write_text("A=\"double\"\nB='single'\nC=\"unbalanced\nD=in\"side\n")
        self.assertEqual(
            run_evals.load_env(self.path),
            {"A": "double", "B": "single", "C": "\"unbalanced", "D": "in\"side"},
        )

    def test_value_keeps_its_own_equals_signs(self):
        self.path.write_text("K=a=b==\n")
        self.assertEqual(run_evals.load_env(self.path), {"K": "a=b=="})

    def test_missing_file_is_empty_not_an_error(self):
        self.assertEqual(run_evals.load_env(self.path), {})

    def test_environment_wins_over_the_file(self):
        self.path.write_text("CLAUDE_CODE_OAUTH_TOKEN=from-file\n")
        auth = run_evals.resolve_auth({"CLAUDE_CODE_OAUTH_TOKEN": "from-env"}, self.path)
        self.assertEqual(auth, {"CLAUDE_CODE_OAUTH_TOKEN": "from-env"})

    def test_file_supplies_auth_when_the_environment_has_none(self):
        self.path.write_text("ANTHROPIC_API_KEY='from-file'\n")
        self.assertEqual(run_evals.resolve_auth({}, self.path), {"ANTHROPIC_API_KEY": "from-file"})

    def test_empty_values_are_not_auth(self):
        self.path.write_text("CLAUDE_CODE_OAUTH_TOKEN=\n")
        self.assertIsNone(run_evals.resolve_auth({"ANTHROPIC_API_KEY": ""}, self.path))


class ChildEnvTest(unittest.TestCase):
    def test_strips_inherited_claude_variables_and_sets_config_and_auth(self):
        parent = {"PATH": "/usr/bin", "CLAUDECODE": "1", "CLAUDE_EFFORT": "high",
                  "CLAUDE_CODE_SESSION_ID": "abc", "CLAUDE_CONFIG_DIR": "/elsewhere"}
        env = run_evals.child_env(Path("/cfg"), Path("/home-tmp"),
                                  {"CLAUDE_CODE_OAUTH_TOKEN": "t"}, parent)
        self.assertEqual(env, {"PATH": "/usr/bin", "CLAUDE_CONFIG_DIR": "/cfg",
                               "HOME": "/home-tmp", "CLAUDE_CODE_OAUTH_TOKEN": "t"})

    def test_assertion_env_has_the_runs_home_and_config_but_no_auth(self):
        parent = {"PATH": "/usr/bin", "ANTHROPIC_API_KEY": "inherited",
                  "CLAUDE_CODE_OAUTH_TOKEN": "inherited", "GIT_DIR": "/outer/.git"}
        env = run_evals.assertion_env(Path("/cfg"), Path("/home-tmp"), parent)
        self.assertEqual(env, {"PATH": "/usr/bin", "CLAUDE_CONFIG_DIR": "/cfg",
                               "HOME": "/home-tmp"})

    def test_strips_inherited_git_variables(self):
        # A runner started from a hook or `git rebase -x` carries these; a
        # /commit run would otherwise act on the outer repository.
        parent = {"PATH": "/usr/bin", "GIT_DIR": "/outer/.git",
                  "GIT_INDEX_FILE": "/outer/.git/index", "GIT_WORK_TREE": "/outer"}
        env = run_evals.child_env(Path("/cfg"), Path("/home-tmp"), {}, parent)
        self.assertEqual(env, {"PATH": "/usr/bin", "CLAUDE_CONFIG_DIR": "/cfg",
                               "HOME": "/home-tmp"})


class ClaudeCommandTest(unittest.TestCase):
    def test_prompt_follows_p_and_allowed_tools_come_last(self):
        cmd = run_evals.claude_command("hi", allowed_tools=["Read", "Edit"], model="m")
        self.assertEqual(cmd[:3], ["claude", "-p", "hi"])
        self.assertEqual(cmd[-3:], ["--allowedTools", "Read", "Edit"])
        for flag in ("--strict-mcp-config", "--include-partial-messages", "--verbose"):
            self.assertIn(flag, cmd)
        self.assertEqual(cmd[cmd.index("--model") + 1], "m")
        self.assertEqual(cmd[cmd.index("--permission-mode") + 1], "acceptEdits")

    def test_omits_optional_flags(self):
        cmd = run_evals.claude_command("hi")
        for flag in ("--agent", "--model", "--allowedTools"):
            self.assertNotIn(flag, cmd)


class BuildConfigTest(unittest.TestCase):
    def build(self, root: Path) -> Path:
        cfg = run_evals.build_config(root)
        self.addCleanup(run_evals.remove_tree, cfg)
        return cfg

    def test_working_tree_config_links_the_claude_platform(self):
        cfg = self.build(ROOT)
        self.assertEqual(stat.S_IMODE(cfg.stat().st_mode), 0o700)
        for name in ("agents", "commands", "CLAUDE.md"):
            link = cfg / name
            self.assertTrue(link.is_symlink(), name)
            self.assertEqual(link.resolve(), (ROOT / "platforms/claude" / name).resolve())

    def test_every_skill_link_resolves_to_a_skill(self):
        skills = self.build(ROOT) / "skills"
        self.assertFalse(skills.is_symlink())
        names = sorted(p.name for p in skills.iterdir())
        self.assertIn("debugging-methodology", names)
        self.assertNotIn("synced", names)
        for name in names:
            self.assertTrue((skills / name / "SKILL.md").is_file(), name)

    def test_settings_disable_the_builtin_plugins_and_keep_the_deny_list(self):
        settings = json.loads((self.build(ROOT) / "settings.json").read_text())
        self.assertEqual(settings["enabledPlugins"], {
            "cc-plugin-plugin-authoring@builtin": False,
            "cc-plugin-agents-md@builtin": False,
            "cc-plugin-telemetry@builtin": False,
        })
        self.assertIn("Read(**/.env)", settings["permissions"]["deny"])

    def test_ignored_skills_are_excluded_but_new_untracked_ones_are_kept(self):
        # Head is the working tree with uncommitted edits, so a skill not yet
        # added is part of it; gitignored skills/synced/ is not.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path, body in {
                ".gitignore": "skills/synced/\n",
                "platforms/claude/agents/a.md": "a",
                "platforms/claude/commands/c.md": "c",
                "platforms/claude/CLAUDE.md": "index",
                "platforms/claude/settings.json.example": '{"enabledPlugins": {"x@y": true}}',
                "skills/tracked/SKILL.md": "t",
                "skills/synced/skill-creator/SKILL.md": "s",
                "skills/untracked/SKILL.md": "u",
            }.items():
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_text(body)
            git = ["git", "-C", tmp]
            subprocess.run([*git, "init", "-q"], check=True)
            subprocess.run([*git, "add", ".gitignore", "platforms", "skills/tracked"], check=True)
            names = sorted(p.name for p in (self.build(root) / "skills").iterdir())
        self.assertEqual(names, ["tracked", "untracked"])

    def test_side_home_links_dot_claude_to_its_config_and_both_are_removed(self):
        with run_evals.side_dirs("head", ROOT) as side:
            self.assertTrue((side.home / ".claude").is_symlink())
            self.assertEqual((side.home / ".claude").resolve(), side.config.resolve())
            self.assertTrue((side.home / ".claude" / "skills" / "why" / "SKILL.md").is_file())
        self.assertFalse(side.home.exists())
        self.assertFalse(side.config.exists())


# --- Task 3: cases, fixtures, assertions, scoring, report ------------------


def call(name: str, parent: str | None = None, **tool_input) -> object:
    return run_evals.ToolCall(name, tool_input, parent)


def run_result(*calls, final_text: str = "", error_class: str = "none",
               routes: tuple[str, ...] = (), plugins: tuple[str, ...] = ()) -> object:
    return run_evals.RunResult(
        tool_calls=tuple(calls), routes=routes, final_text=final_text, stop="result",
        exit_status=0, error_class=error_class, plugins=plugins, model="claude-sonnet-5-5",
    )


def git_out(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, check=True).stdout


class CaseLoadingTest(unittest.TestCase):
    def test_routing_ids_name_the_target_and_number_only_repeats(self):
        self.assertEqual(
            run_evals.routing_ids(["why", "none", "debugger", "none"]),
            ["routing/why", "routing/none-1", "routing/debugger", "routing/none-2"],
        )

    def test_the_suites_cases_load_with_unique_ids(self):
        cases = run_evals.load_cases(ROOT)
        ids = [c.id for c in cases]
        self.assertEqual(len(ids), len(set(ids)))
        routing = {c.id: c for c in cases if isinstance(c, run_evals.RoutingCase)}
        self.assertEqual(len(routing), 39)
        self.assertEqual(routing["routing/why"].targets, frozenset({"why"}))
        self.assertEqual(routing["routing/code-reviewer"].targets,
                         frozenset({"code-reviewer", "code-review-checklist"}))
        self.assertEqual(routing["routing/none-6"].targets, frozenset())
        behavior = {c.id: c for c in cases if isinstance(c, run_evals.BehaviorCase)}
        self.assertEqual(sorted(behavior), [
            "behavior/commit-conventions", "behavior/debugger-phase-0",
            "behavior/reviewer-planted-bug", "behavior/spec-asks-first",
        ])
        self.assertIsNone(behavior["behavior/spec-asks-first"].fixture)
        self.assertTrue(behavior["behavior/commit-conventions"].stage)
        self.assertEqual(behavior["behavior/commit-conventions"].timeout, 180)

    def test_only_filters_ids_by_glob(self):
        cases = run_evals.load_cases(ROOT)
        self.assertEqual(len(run_evals.select(cases, "behavior/*")), 4)
        self.assertEqual(len(run_evals.select(cases, "routing/none-*")), 6)
        self.assertEqual([c.id for c in run_evals.select(cases, "routing/why")], ["routing/why"])
        self.assertEqual(len(run_evals.select(cases, None)), len(cases))

    def test_only_matching_nothing_is_a_setup_error(self):
        with self.assertRaises(run_evals.SetupError):
            run_evals.select(run_evals.load_cases(ROOT), "routing/no-such-target")

    def write_suite(self, routing: str, case: str | None = None) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "evals").mkdir()
        (root / "evals" / "routing.yaml").write_text(routing)
        if case is not None:
            (root / "evals" / "behavior" / "c").mkdir(parents=True)
            (root / "evals" / "behavior" / "c" / "case.yaml").write_text(case)
        return root

    def test_routing_entry_with_two_target_keys_is_a_setup_error(self):
        root = self.write_suite("- prompt: hi\n  expect: why\n  any_of: [why]\n")
        with self.assertRaisesRegex(run_evals.SetupError, "routing.yaml entry 1"):
            run_evals.load_cases(root)

    def test_unknown_assertion_type_is_a_setup_error(self):
        root = self.write_suite("[]\n", "prompt: hi\nassert:\n  - says_hello: true\n")
        with self.assertRaisesRegex(run_evals.SetupError, "says_hello"):
            run_evals.load_cases(root)

    def test_shell_without_match_or_not_match_is_a_setup_error(self):
        root = self.write_suite("[]\n", "prompt: hi\nassert:\n  - shell: {run: git log}\n")
        with self.assertRaisesRegex(run_evals.SetupError, "behavior/c: shell"):
            run_evals.load_cases(root)

    def test_invalid_regex_is_a_setup_error(self):
        root = self.write_suite("[]\n", "prompt: hi\nassert:\n  - final_text: {match: ['(']}\n")
        with self.assertRaisesRegex(run_evals.SetupError, "behavior/c"):
            run_evals.load_cases(root)


class FixtureTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.fixture = Path(tmp.name) / "fixture"
        self.scratch = Path(tmp.name) / "scratch"
        self.scratch.mkdir()
        for path, body in {"before/a.txt": "one\n", "before/sub/c.txt": "c\n",
                           "after/a.txt": "two\n", "after/b.txt": "new\n"}.items():
            (self.fixture / path).parent.mkdir(parents=True, exist_ok=True)
            (self.fixture / path).write_text(body)

    def status(self) -> list[str]:
        return sorted(git_out(self.scratch, "status", "--porcelain").splitlines())

    def test_before_is_exactly_one_commit_with_the_fixed_identity(self):
        run_evals.prepare_fixture(self.fixture, self.scratch, stage=False)
        self.assertEqual(git_out(self.scratch, "rev-list", "--count", "HEAD").strip(), "1")
        self.assertEqual(git_out(self.scratch, "log", "-1", "--format=%an <%ae>").strip(),
                         "evals <evals@localhost>")
        self.assertEqual(git_out(self.scratch, "config", "--local", "user.name").strip(), "evals")
        self.assertEqual(git_out(self.scratch, "show", "HEAD:a.txt"), "one\n")
        self.assertEqual(git_out(self.scratch, "show", "HEAD:sub/c.txt"), "c\n")

    def test_after_overlays_as_unstaged_changes(self):
        run_evals.prepare_fixture(self.fixture, self.scratch, stage=False)
        self.assertEqual(self.status(), [" M a.txt", "?? b.txt"])
        self.assertEqual((self.scratch / "a.txt").read_text(), "two\n")

    def test_after_overlays_as_staged_changes_when_stage_is_set(self):
        run_evals.prepare_fixture(self.fixture, self.scratch, stage=True)
        self.assertEqual(self.status(), ["A  b.txt", "M  a.txt"])

    def test_no_fixture_is_an_empty_repo_with_identity_and_no_commit(self):
        run_evals.prepare_fixture(None, self.scratch, stage=False)
        self.assertEqual(git_out(self.scratch, "config", "--local", "user.email").strip(),
                         "evals@localhost")
        head = subprocess.run(["git", "-C", str(self.scratch), "rev-parse", "--verify", "HEAD"],
                              capture_output=True)
        self.assertNotEqual(head.returncode, 0)
        self.assertEqual([p.name for p in self.scratch.iterdir()], [".git"])


class AssertionTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.scratch = Path(tmp.name)

    def check(self, assertion: dict, result) -> str | None:
        return run_evals.check_assertion(assertion, result, self.scratch, dict(os.environ))

    # order

    def test_order_passes_when_first_precedes_before(self):
        result = run_result(call("Bash", command="python3 -m unittest -v"),
                            call("Edit", file_path="a.py"))
        self.assertIsNone(self.check({"order": {"first": "Bash:unittest", "before": "Edit"}},
                                     result))

    def test_order_fails_when_before_comes_first(self):
        result = run_result(call("Edit", file_path="a.py"),
                            call("Bash", command="python3 -m unittest"))
        self.assertIsNotNone(self.check({"order": {"first": "Bash:unittest", "before": "Edit"}},
                                        result))

    def test_order_fails_when_first_never_occurs(self):
        result = run_result(call("Bash", command="ls"), call("Read", file_path="a.py"))
        self.assertIsNotNone(self.check({"order": {"first": "Bash:unittest", "before": "Edit"}},
                                        result))

    def test_order_passes_when_before_never_occurs(self):
        result = run_result(call("Bash", command="python3 -m unittest"))
        self.assertIsNone(self.check({"order": {"first": "Bash:unittest", "before": "Write"}},
                                     result))

    def test_order_counts_subagent_calls_in_stream_order(self):
        result = run_result(
            call("Agent", subagent_type="debugger"),
            call("Bash", "toolu_agent", command="python3 -m unittest"),
            call("Edit", "toolu_agent", file_path="a.py"),
        )
        self.assertIsNone(self.check({"order": {"first": "Bash:unittest", "before": "Edit"}},
                                     result))

    def test_order_regex_has_no_default_flags(self):
        result = run_result(call("Bash", command="python3 -m unittest"))
        self.assertIsNotNone(self.check({"order": {"first": "Bash:UNITTEST", "before": "Edit"}},
                                        result))
        self.assertIsNone(self.check({"order": {"first": "Bash:(?i)UNITTEST", "before": "Edit"}},
                                     result))

    def test_order_without_a_regex_matches_the_tool_name(self):
        result = run_result(call("Read", file_path="a.py"), call("Edit", file_path="a.py"))
        self.assertIsNone(self.check({"order": {"first": "Read", "before": "Edit"}}, result))

    def test_debugger_case_counts_only_a_unittest_run_as_the_reproduction(self):
        case = next(c for c in run_evals.load_cases(ROOT) if c.id == "behavior/debugger-phase-0")
        order = case.asserts[0]
        searched = run_result(call("Bash", command="grep -rn unittest ."),
                              call("Edit", file_path="pricing.py"))
        self.assertIsNotNone(self.check(order, searched))
        for command in ("python3 -m unittest", "python3 -m unittest -v test_pricing"):
            with self.subTest(command=command):
                ran = run_result(call("Bash", command=command), call("Edit", file_path="pricing.py"))
                self.assertIsNone(self.check(order, ran))

    # tool_not_called

    def test_tool_not_called_passes_when_absent(self):
        result = run_result(call("Read", file_path="a.py"))
        self.assertIsNone(self.check({"tool_not_called": ["Write", "Edit"]}, result))

    def test_tool_not_called_fails_on_a_forked_call(self):
        result = run_result(call("Write", "forked-command-spec", file_path="docs/x.md"))
        self.assertIsNotNone(self.check({"tool_not_called": ["Write", "Edit"]}, result))

    # final_text

    def test_final_text_passes_when_every_match_hits_and_no_not_match_does(self):
        result = run_result(final_text="Found it in db.py:25.\nA) one\nB) two")
        self.assertIsNone(self.check(
            {"final_text": {"match": [r"db\.py:25", "(?m)^B\\)"], "not_match": ["LGTM"]}},
            result))

    def test_final_text_fails_on_a_missing_match(self):
        result = run_result(final_text="LGTM")
        self.assertIsNotNone(self.check({"final_text": {"match": [r"db\.py"]}}, result))

    def test_final_text_fails_on_a_not_match_hit(self):
        result = run_result(final_text="## Task Checklist\n- [ ] 1.")
        self.assertIsNotNone(self.check({"final_text": {"not_match": ["## Task Checklist"]}},
                                        result))

    def test_final_text_line_anchors_need_an_inline_flag(self):
        result = run_result(final_text="intro\nA) one")
        self.assertIsNotNone(self.check({"final_text": {"match": [r"^A\)"]}}, result))

    # shell

    def test_shell_matches_the_commands_stdout_in_scratch(self):
        (self.scratch / "marker.txt").write_text("fix(greet): add --shout\n")
        self.assertIsNone(self.check(
            {"shell": {"run": "cat marker.txt", "match": [r"^fix\(greet\): "],
                       "not_match": ["Co-Authored-By"]}}, run_result()))

    def test_shell_fails_on_a_not_match_hit(self):
        self.assertIsNotNone(self.check(
            {"shell": {"run": "echo 'Co-Authored-By: someone'", "not_match": ["Co-Authored-By"]}},
            run_result()))

    def test_shell_fails_on_a_missing_match(self):
        self.assertIsNotNone(self.check({"shell": {"run": "echo 1", "match": ["^2$"]}},
                                        run_result()))

    def test_shell_fails_when_the_command_exits_nonzero(self):
        # `git log` in a repo without commits prints nothing, which a
        # not_match alone would accept.
        failure = self.check({"shell": {"run": "echo partial; exit 3",
                                        "not_match": ["Co-Authored-By"]}}, run_result())
        self.assertIsNotNone(failure)
        self.assertIn("3", failure)

    # no_paths

    def test_no_paths_passes_when_nothing_matches(self):
        (self.scratch / "docs").mkdir()
        self.assertIsNone(self.check({"no_paths": ["docs/specs/*"]}, run_result()))

    def test_no_paths_fails_when_a_file_matches(self):
        (self.scratch / "docs" / "specs").mkdir(parents=True)
        (self.scratch / "docs" / "specs" / "2026-10-19-backup.md").write_text("# spec\n")
        self.assertIsNotNone(self.check({"no_paths": ["docs/specs/*"]}, run_result()))


class JudgeTest(unittest.TestCase):
    def routing(self, *targets: str):
        return run_evals.RoutingCase(id="routing/x", prompt="p", targets=frozenset(targets))

    def judge(self, case, result):
        return run_evals.judge(case, result, Path("/nonexistent"), {})

    def test_expected_skill_passes(self):
        self.assertTrue(self.judge(self.routing("why"), run_result(routes=("why",))).passed)

    def test_extra_loads_alongside_the_target_still_pass(self):
        result = run_result(routes=("coding-guardrails", "backend-patterns"))
        self.assertTrue(self.judge(self.routing("backend-patterns"), result).passed)

    def test_any_of_member_passes(self):
        case = self.routing("code-reviewer", "code-review-checklist")
        self.assertTrue(self.judge(case, run_result(routes=("code-review-checklist",))).passed)

    def test_wrong_route_fails(self):
        self.assertFalse(self.judge(self.routing("why"), run_result(routes=("Explore",))).passed)

    def test_no_route_fails_a_case_that_expects_one(self):
        self.assertFalse(self.judge(self.routing("why"), run_result()).passed)

    def test_expect_none_passes_only_on_an_empty_route(self):
        self.assertTrue(self.judge(self.routing(), run_result()).passed)
        self.assertFalse(self.judge(self.routing(), run_result(routes=("why",))).passed)

    def test_error_run_does_not_count(self):
        verdict = self.judge(self.routing("why"), run_result(routes=("why",), error_class="error"))
        self.assertFalse(verdict.counted)

    def test_timeout_counts_as_a_failure(self):
        verdict = self.judge(self.routing(), run_result(error_class="timeout"))
        self.assertTrue(verdict.counted)
        self.assertFalse(verdict.passed)
        self.assertIn("timeout", verdict.detail)

    def test_behavior_case_passes_when_every_assertion_does(self):
        case = run_evals.BehaviorCase(
            id="behavior/x", prompt="p", allowed_tools=(), timeout=60, stage=False,
            asserts=({"tool_not_called": ["Write"]}, {"final_text": {"match": ["ok"]}}),
            fixture=None)
        self.assertTrue(self.judge(case, run_result(final_text="ok")).passed)
        verdict = self.judge(case, run_result(call("Write", file_path="x")))
        self.assertFalse(verdict.passed)
        self.assertIn("Write", verdict.detail)


class RunOneTest(unittest.TestCase):
    def test_a_run_that_raises_is_an_error_outcome_not_an_abort(self):
        # An empty before/ makes the fixture's `git commit` fail before claude
        # starts; the run must come back as an uncounted error naming the cause.
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "fixture"
            (fixture / "before").mkdir(parents=True)
            case = run_evals.BehaviorCase(
                id="behavior/x", prompt="p", allowed_tools=(), timeout=60, stage=False,
                asserts=({"tool_not_called": ["Write"]},), fixture=fixture)
            side = run_evals.Side(name="head", config=Path(tmp) / "cfg", home=Path(tmp) / "home")
            outcome = run_evals.run_one(case, side, {}, model=None)
        self.assertEqual((outcome.case_id, outcome.side), ("behavior/x", "head"))
        self.assertFalse(outcome.verdict.counted)
        self.assertIn("CalledProcessError", outcome.verdict.detail)
        self.assertEqual(run_evals.Rate.of([outcome.verdict]).errors, 1)


class StatusTest(unittest.TestCase):
    def rate(self, passes: int, counted: int, errors: int = 0):
        return run_evals.Rate(passes=passes, counted=counted, errors=errors)

    def test_regression_when_base_passes_and_head_fails(self):
        self.assertEqual(run_evals.status(self.rate(3, 3), self.rate(1, 3)), "REGRESSION")

    def test_fixed_when_base_fails_and_head_passes(self):
        self.assertEqual(run_evals.status(self.rate(0, 3), self.rate(2, 3)), "FIXED")

    def test_pass_and_fail_when_both_sides_agree(self):
        self.assertEqual(run_evals.status(self.rate(2, 3), self.rate(3, 3)), "PASS")
        self.assertEqual(run_evals.status(self.rate(1, 3), self.rate(0, 3)), "FAIL")

    def test_two_thirds_is_the_pass_line(self):
        self.assertEqual(run_evals.status(self.rate(4, 5), self.rate(3, 5)), "REGRESSION")
        self.assertEqual(run_evals.status(self.rate(2, 2, 1), self.rate(2, 3)), "PASS")

    def test_fewer_than_two_counted_runs_is_inconclusive_never_regression(self):
        self.assertEqual(run_evals.status(self.rate(3, 3), self.rate(0, 1, 2)), "INCONCLUSIVE")
        self.assertEqual(run_evals.status(self.rate(0, 0, 3), self.rate(3, 3)), "INCONCLUSIVE")

    def test_rate_excludes_errors_and_counts_timeouts_as_failures(self):
        verdicts = [run_evals.Verdict(True, True, ""), run_evals.Verdict(False, True, "timeout"),
                    run_evals.Verdict(False, False, "error")]
        self.assertEqual(run_evals.Rate.of(verdicts), self.rate(1, 2, 1))

    def test_exit_code_is_one_only_with_a_regression(self):
        self.assertEqual(run_evals.exit_code(["PASS", "FIXED", "INCONCLUSIVE", "FAIL"]), 0)
        self.assertEqual(run_evals.exit_code(["PASS", "REGRESSION"]), 1)


check_eval_report = load_script("check-eval-report.py")


class ReportTest(unittest.TestCase):
    def render(self, rows, plugins=()):
        return run_evals.render_report(
            rows, base_sha="0123456789abcdef0123456789abcdef01234567", base_ref="main",
            head_sha="fedcba9876543210fedcba9876543210fedcba98", dirty=True,
            model="claude-sonnet-5-5", runs=3, plugins=plugins)

    def rows(self):
        r = run_evals.Rate
        return [
            run_evals.Row("routing/why", r(3, 3, 0), r(0, 3, 0)),
            run_evals.Row("routing/none-1", r(3, 3, 0), r(3, 3, 0)),
            run_evals.Row("behavior/spec-asks-first", r(1, 1, 2), r(3, 3, 0)),
        ]

    def test_marker_is_accepted_by_the_report_check(self):
        report = self.render(self.rows())
        self.assertTrue(check_eval_report.has_report(report))
        self.assertTrue(report.rstrip().endswith(
            "<!-- evals: base=0123456789ab head=fedcba987654-dirty "
            "model=claude-sonnet-5-5 runs=3 -->"))

    def test_report_lists_notable_cases_and_one_table_per_tier(self):
        report = self.render(self.rows())
        self.assertIn("1 REGRESSION", report)
        self.assertIn("- REGRESSION `routing/why`", report)
        self.assertIn("- INCONCLUSIVE `behavior/spec-asks-first`", report)
        self.assertIn("| `routing/why` | 3/3 | 0/3 | REGRESSION |", report)
        self.assertIn("| `behavior/spec-asks-first` | 1/1, 2 err | 3/3 | INCONCLUSIVE |", report)
        self.assertLess(report.index("### Routing"), report.index("### Behavior"))

    def test_isolation_warning_names_the_plugins(self):
        report = self.render(self.rows(), plugins=("cc-plugin-telemetry",))
        self.assertIn("cc-plugin-telemetry", report)
        self.assertIn("isolation", report.lower())
        self.assertNotIn("isolation", self.render(self.rows()).lower())



class CheckEvalReportTest(unittest.TestCase):
    MARKER = "<!-- evals: base=0123456 head=89abcde model=claude-sonnet-5-5 runs=3 -->"

    def test_marker_passes(self):
        self.assertTrue(check_eval_report.has_report(f"Summary.\n\n{self.MARKER}\n"))

    def test_dirty_head_marker_passes(self):
        self.assertTrue(check_eval_report.has_report(self.MARKER.replace("89abcde", "89abcde-dirty")))

    def test_opt_out_with_a_reason_passes(self):
        for dash in ("—", "–", "-", "--"):
            with self.subTest(dash=dash):
                self.assertTrue(check_eval_report.has_report(f"Fix.\n\nevals: n/a {dash} typo only\n"))

    def test_opt_out_without_a_reason_fails(self):
        self.assertFalse(check_eval_report.has_report("evals: n/a —\n"))
        self.assertFalse(check_eval_report.has_report("evals: n/a\n"))
        # The reason must sit on the opt-out's own line.
        self.assertFalse(check_eval_report.has_report("evals: n/a —\n\n## Summary"))
        self.assertFalse(check_eval_report.has_report("evals: n/a\n- tightened wording"))

    def test_absent_report_fails(self):
        self.assertFalse(check_eval_report.has_report(""))
        self.assertFalse(check_eval_report.has_report("Tightened the why description."))

    def test_malformed_marker_fails(self):
        self.assertFalse(check_eval_report.has_report("<!-- evals: base=main head=HEAD -->"))

    def test_main_reads_the_body_from_the_environment(self):
        script = SCRIPTS / "check-eval-report.py"
        def run(body):
            env = {**os.environ, "PR_BODY": body}
            return subprocess.run([sys.executable, str(script)], env=env,
                                  capture_output=True, text=True).returncode
        self.assertEqual(run(self.MARKER), 0)
        self.assertEqual(run("no report"), 1)

if __name__ == "__main__":
    unittest.main()
