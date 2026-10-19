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
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
RECORDINGS = ROOT / "evals" / "recordings"


def load_script(filename: str):
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
    def test_skill_call_is_a_route_and_stops_the_stream(self):
        result = read_recording("route-skill")
        self.assertEqual(result.routes, ("docker-best-practices",))
        self.assertEqual(result.stop, "route")
        self.assertEqual(result.error_class, "none")
        self.assertEqual([c.name for c in result.tool_calls], ["Skill"])

    def test_agent_call_routes_to_its_subagent_type(self):
        result = read_recording("route-agent")
        self.assertEqual(result.routes, ("security-analyst",))
        self.assertEqual(result.stop, "route")
        self.assertEqual(result.tool_calls[0].name, "Agent")
        self.assertIsNone(result.tool_calls[0].parent_tool_use_id)

    def test_read_of_a_skill_file_routes_to_that_skill(self):
        result = read_recording("route-read")
        self.assertEqual(result.routes, ("git-conventions",))
        self.assertEqual(result.stop, "route")

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
        env = run_evals.child_env(Path("/cfg"), {"CLAUDE_CODE_OAUTH_TOKEN": "t"}, parent)
        self.assertEqual(env, {"PATH": "/usr/bin", "CLAUDE_CONFIG_DIR": "/cfg",
                               "CLAUDE_CODE_OAUTH_TOKEN": "t"})


class ClaudeCommandTest(unittest.TestCase):
    def test_prompt_follows_p_and_allowed_tools_come_last(self):
        cmd = run_evals.claude_command("hi", agent="debugger", allowed_tools=["Read", "Edit"],
                                       model="m")
        self.assertEqual(cmd[:3], ["claude", "-p", "hi"])
        self.assertEqual(cmd[-3:], ["--allowedTools", "Read", "Edit"])
        for flag in ("--strict-mcp-config", "--include-partial-messages", "--verbose"):
            self.assertIn(flag, cmd)
        self.assertEqual(cmd[cmd.index("--agent") + 1], "debugger")
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

    def test_untracked_skills_are_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path, body in {
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
            subprocess.run([*git, "add", "platforms", "skills/tracked"], check=True)
            names = sorted(p.name for p in (self.build(root) / "skills").iterdir())
        self.assertEqual(names, ["tracked"])


if __name__ == "__main__":
    unittest.main()
