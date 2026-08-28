#!/usr/bin/env python3
"""Validate the two agent-suite configs for reference integrity and parity.

Checks that identifiers match filenames, that every cross-reference resolves
(agent -> skill, command -> agent, skill -> reference file), that the index
documents (claude/.claude/CLAUDE.md, opencode/.../AGENTS.md) neither name
artifacts that don't exist nor omit ones that do, and that the shared skills
are in sync with their canonical claude/ source.

    scripts/validate-config.py          list every check and what it covered
    scripts/validate-config.py -q       print only failures and the summary

Frontmatter is parsed with PyYAML when available; without it the YAML-validity
check is skipped and a simple key scanner is used instead.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)

CLAUDE = ROOT / "claude/.claude"
OPENCODE = ROOT / "opencode/.config/opencode"

# Agent identifiers provided by the harness, so no file backs them.
BUILTIN_AGENTS = {"explore", "general", "plan", "build"}

problems: list[str] = []


def fail(msg: str) -> None:
    problems.append(msg)


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def split_frontmatter(path: Path) -> tuple[str | None, str]:
    text = path.read_text()
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 4:]


def parse_frontmatter(path: Path) -> dict | None:
    """Return the frontmatter as a dict, or None when it can't be parsed."""
    raw, _ = split_frontmatter(path)
    if raw is None:
        fail(f"{rel(path)}: no frontmatter block")
        return None
    if yaml is not None:
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as e:
            fail(f"{rel(path)}: invalid YAML frontmatter — {str(e).splitlines()[0]}")
            return None
        if not isinstance(data, dict):
            fail(f"{rel(path)}: frontmatter parsed as {type(data).__name__}, not a mapping")
            return None
        return data
    # Fallback: scalars plus simple block lists — enough for the reference
    # checks. Nested mappings are collapsed to a list, which no check reads.
    data: dict = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip().strip("\"'")
        if val:
            low = val.lower()
            data[key] = True if low in ("true", "yes") else False if low in ("false", "no") else val
            i += 1
            continue
        items = []
        j = i + 1
        while j < len(lines) and re.match(r"^\s+-\s+", lines[j]):
            items.append(re.sub(r"^\s+-\s+", "", lines[j]).strip().strip("\"'").rstrip(":"))
            j += 1
        data[key] = items
        i = j
    return data


# ---------------------------------------------------------------- inventories

def claude_skills() -> dict[str, dict]:
    out = {}
    for d in sorted((CLAUDE / "skills").iterdir()):
        f = d / "SKILL.md"
        if d.is_dir() and f.is_file():
            out[d.name] = parse_frontmatter(f) or {}
    return out


def opencode_skills() -> dict[str, dict]:
    out = {}
    for d in sorted((OPENCODE / "skills").iterdir()):
        f = d / "SKILL.md"
        if d.is_dir() and f.is_file():
            out[d.name] = parse_frontmatter(f) or {}
    return out


def md_files(directory: Path) -> dict[str, dict]:
    out = {}
    if directory.is_dir():
        for f in sorted(directory.glob("*.md")):
            out[f.stem] = parse_frontmatter(f) or {}
    return out


C_SKILLS = claude_skills()
O_SKILLS = opencode_skills()
C_AGENTS = md_files(CLAUDE / "agents")
O_AGENTS = md_files(OPENCODE / "agent")
O_COMMANDS = md_files(OPENCODE / "commands")

# claude implements slash commands as workflow skills. They used to be marked by
# disable-model-invocation, but the suite dropped that key (see the invocation
# note in claude/.claude/CLAUDE.md), so the discriminator is now structural: a
# reference skill opens its body with an `# H1 Title`, a workflow skill is a
# short task prompt with no heading. A misclassification is self-catching —
# check_index fails on the /name row the index still lists.
def is_workflow_skill(name: str) -> bool:
    _, body = split_frontmatter(CLAUDE / "skills" / name / "SKILL.md")
    return not re.search(r"^# ", body, re.M)


C_COMMANDS = {n: fm for n, fm in C_SKILLS.items() if is_workflow_skill(n)}


# -------------------------------------------------------------------- checks

def check_descriptions() -> str:
    n = 0
    for label, inv in (("claude skill", C_SKILLS), ("opencode skill", O_SKILLS),
                       ("claude agent", C_AGENTS), ("opencode agent", O_AGENTS),
                       ("opencode command", O_COMMANDS)):
        for name, fm in inv.items():
            n += 1
            if not fm.get("description"):
                fail(f"{label} '{name}': missing a description")
    return f"{n} artifacts carry a description"


def check_identifiers() -> str:
    for name, fm in C_AGENTS.items():
        if fm.get("name") and fm["name"] != name:
            fail(f"claude agent '{name}.md': name: is '{fm['name']}', must match the filename")
        if not fm.get("name"):
            fail(f"claude agent '{name}.md': missing required name: key")
    for name, fm in O_SKILLS.items():
        if fm.get("name") != name:
            fail(f"opencode skill '{name}': name: is {fm.get('name')!r}, must match the directory")
    return (f"{len(C_AGENTS)} claude agent files, {len(O_SKILLS)} opencode skill dirs "
            f"match their identifiers")


def check_agent_skill_refs() -> str:
    n = 0
    for name, fm in C_AGENTS.items():
        for s in fm.get("skills") or []:
            n += 1
            if s not in C_SKILLS:
                fail(f"claude agent '{name}' preloads unknown skill '{s}'")
            elif C_SKILLS[s].get("disable-model-invocation"):
                fail(f"claude agent '{name}' preloads '{s}', which sets "
                     f"disable-model-invocation — workflow skills cannot be preloaded")
    return f"{n} preload refs across {len(C_AGENTS)} claude agents resolve and are preloadable"


def check_command_agent_refs() -> str:
    for name, fm in C_COMMANDS.items():
        a = fm.get("agent")
        if a and a not in C_AGENTS and a not in BUILTIN_AGENTS:
            fail(f"claude workflow skill '{name}' routes to unknown agent '{a}'")
    for name, fm in O_COMMANDS.items():
        a = fm.get("agent")
        if a and a not in O_AGENTS and a not in BUILTIN_AGENTS:
            fail(f"opencode command '{name}' routes to unknown agent '{a}'")
    total = len(C_COMMANDS) + len(O_COMMANDS)
    routed = sum(1 for fm in list(C_COMMANDS.values()) + list(O_COMMANDS.values()) if fm.get("agent"))
    return (f"{routed} of {total} commands name an agent, all resolving "
            f"({len(C_COMMANDS)} claude workflow skills + {len(O_COMMANDS)} opencode commands)")


def check_reference_pointers() -> str:
    n_files = n_ptr = n_link = 0
    pat_scoped = re.compile(r"\b([a-z][a-z0-9-]*)/reference/([a-z0-9-]+\.md)\b")
    pat_link = re.compile(r"\]\(([A-Za-z0-9_./-]+\.md)\)")
    for root in (CLAUDE / "skills", OPENCODE / "skills"):
        for f in sorted(root.rglob("*.md")):
            text = f.read_text()
            n_files += 1
            for skill, fname in set(pat_scoped.findall(text)):
                n_ptr += 1
                if not (root / skill / "reference" / fname).is_file():
                    fail(f"{rel(f)}: pointer to missing {skill}/reference/{fname}")
            for target in set(pat_link.findall(text)):
                if target.startswith(("http", "/")):
                    continue
                n_link += 1
                if not (f.parent / target).resolve().is_file():
                    fail(f"{rel(f)}: markdown link to missing {target}")
    return f"{n_ptr} reference pointers + {n_link} markdown links across {n_files} files resolve"


def index_tokens(path: Path) -> tuple[set[str], set[str], set[str]]:
    """Backticked first-column identifiers, split into (skills, agents, commands)."""
    skills, agents, commands = set(), set(), set()
    for line in path.read_text().splitlines():
        m = re.match(r"^\|\s*`([^`]+)`\s*\|", line)
        if not m:
            continue
        tok = m.group(1).strip()
        if tok.startswith("@"):
            agents.add(tok[1:])
        elif tok.startswith("/"):
            commands.add(tok[1:].split()[0])
        else:
            skills.add(tok.split()[0])
    return skills, agents, commands


def check_index(index: Path, skills: dict, agents: dict, commands: dict) -> str:
    named_s, named_a, named_c = index_tokens(index)
    for s in sorted(named_s):
        if s not in skills:
            fail(f"{rel(index)}: lists skill '{s}', which does not exist")
    for a in sorted(named_a):
        if a not in agents and a not in BUILTIN_AGENTS:
            fail(f"{rel(index)}: lists agent '{a}', which does not exist")
    for c in sorted(named_c):
        if c not in commands:
            fail(f"{rel(index)}: lists command '{c}', which does not exist")

    # Existence -> mention. Loose on purpose: some artifacts are described in
    # prose or bold rather than a backticked table cell.
    text = index.read_text()
    for s in sorted(skills):
        if s not in text:
            fail(f"{rel(index)}: skill '{s}' exists but is never mentioned")
    for a in sorted(agents):
        if a not in text:
            fail(f"{rel(index)}: agent '{a}' exists but is never mentioned")
    for c in sorted(commands):
        if c not in text:
            fail(f"{rel(index)}: command '{c}' exists but is never mentioned")
    return (f"{len(named_s)}/{len(named_a)}/{len(named_c)} skills/agents/commands named all exist; "
            f"{len(skills)}/{len(agents)}/{len(commands)} on disk all mentioned")


def check_countable_claims(index: Path, skills: dict, root: Path) -> str:
    """Catch index prose stating a phase count or range the skill contradicts."""
    n = 0
    for line in index.read_text().splitlines():
        m = re.match(r"^\|\s*`([a-z][a-z0-9-]*)`\s*\|(.*)$", line)
        if not m:
            continue
        name, desc = m.group(1), m.group(2)
        if name not in skills:
            continue
        body = (root / name / "SKILL.md").read_text()
        actual = {int(x) for x in re.findall(r"^##\s+Phase\s+(\d+)", body, re.M)}
        if not actual:
            continue

        claimed = {int(x) for x in re.findall(r"\bPhase\s+(\d+)", desc)}
        for lo, hi in re.findall(r"\bphases\s+(\d+)\s*[\u2013\u2014-]\s*(\d+)", desc, re.I):
            claimed |= set(range(int(lo), int(hi) + 1))
        total = re.search(r"(\d+)[- ]phase\b", desc)

        if total and int(total.group(1)) != len(actual):
            fail(f"{rel(index)}: describes '{name}' as {total.group(1)}-phase, "
                 f"but the skill defines {len(actual)} phases")
        if not claimed <= actual:
            fail(f"{rel(index)}: describes '{name}' as having phase(s) "
                 f"{sorted(claimed - actual)}, which the skill does not define")
        if claimed or total:
            n += 1
    return f"{n} phase claim(s) in {rel(index)} match their skill's headings"


def check_index_description_parity() -> str:
    """A shared skill should carry the same description in both index documents.

    The sync script regenerates skill files but not the indexes, so a change made
    on the claude side alone leaves opencode's table stale and its agents reading
    a description that no longer matches the skill.
    """
    c_text = (CLAUDE / "CLAUDE.md").read_text()
    o_text = (OPENCODE / "AGENTS.md").read_text()

    def desc(text: str, skill: str) -> str | None:
        m = re.search(r"^\| `" + re.escape(skill) + r"` \| (.*?) \| .*$", text, re.M)
        return m.group(1).strip() if m else None

    n = 0
    for name in sorted(O_SKILLS):
        c_desc, o_desc = desc(c_text, name), desc(o_text, name)
        if c_desc is None or o_desc is None:
            continue  # coverage is already enforced by check_index
        n += 1
        if c_desc != o_desc:
            # Show the divergence, not the first 60 chars — the two often share a
            # long prefix, which makes a head-truncated message look identical.
            i = next((k for k, (a, b) in enumerate(zip(c_desc, o_desc)) if a != b),
                     min(len(c_desc), len(o_desc)))
            start = max(0, i - 15)
            fail(f"index descriptions disagree for shared skill '{name}' at char {i}: "
                 f"claude {'...' if start else ''}{c_desc[start:i + 45]!r}, "
                 f"opencode {'...' if start else ''}{o_desc[start:i + 45]!r}")
    return f"{n} shared skills carry the same description in both indexes"


def check_parity() -> str:
    script = ROOT / "scripts/sync-skills.sh"
    if not script.is_file():
        fail("scripts/sync-skills.sh is missing — cannot verify claude<->opencode parity")
        return ""
    r = subprocess.run([str(script), "--check"], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        for line in r.stdout.splitlines():
            if "DRIFT" in line or "ORPHAN" in line:
                fail(f"shared-skill drift: {line.split(None, 1)[-1].strip()}")
        fail("run scripts/sync-skills.sh to regenerate the opencode copies")
        return ""
    m = re.search(r"checked: (\d+) in sync", r.stdout)
    return f"{m.group(1) if m else '?'} generated files match their canonical claude/ source"


# ---------------------------------------------------------------------- main

def main() -> int:
    quiet = "-q" in sys.argv or "--quiet" in sys.argv

    print(f"validating {rel(CLAUDE)} and {rel(OPENCODE)}\n")
    if yaml is None:
        print("  note: PyYAML not installed — frontmatter validity check skipped\n")
    print(f"  inventory  claude: {len(C_SKILLS)} skills ({len(C_COMMANDS)} of them commands), "
          f"{len(C_AGENTS)} agents")
    print(f"             opencode: {len(O_SKILLS)} skills, {len(O_AGENTS)} agents, "
          f"{len(O_COMMANDS)} commands\n")

    checks = [
        ("descriptions", check_descriptions),
        ("identifiers", check_identifiers),
        ("agent skill refs", check_agent_skill_refs),
        ("command agent refs", check_command_agent_refs),
        ("reference pointers", check_reference_pointers),
        ("claude index", lambda: check_index(CLAUDE / "CLAUDE.md", C_SKILLS, C_AGENTS, C_COMMANDS)),
        ("opencode index", lambda: check_index(OPENCODE / "AGENTS.md", O_SKILLS, O_AGENTS, O_COMMANDS)),
        ("claude phase counts",
         lambda: check_countable_claims(CLAUDE / "CLAUDE.md", C_SKILLS, CLAUDE / "skills")),
        ("opencode phase counts",
         lambda: check_countable_claims(OPENCODE / "AGENTS.md", O_SKILLS, OPENCODE / "skills")),
        ("index description parity", check_index_description_parity),
        ("shared-skill parity", check_parity),
    ]

    for label, fn in checks:
        before = len(problems)
        detail = fn() or ""
        added = len(problems) - before
        if added:
            print(f"  FAIL  {label:<24}  {added} problem{'' if added == 1 else 's'}")
        elif not quiet:
            print(f"  ok    {label:<24}  {detail}")

    if problems:
        print("\nproblems:")
        for problem in problems:
            print(f"  - {problem}")
        print(f"\n{len(problems)} problem(s) found across {len(checks)} checks.")
        return 1
    print(f"\nall {len(checks)} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
