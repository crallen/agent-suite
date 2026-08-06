#!/usr/bin/env bash
#
# Sync shared skills from the canonical claude/ package into opencode/.
#
# claude/.claude/skills/<name>/ is the single source of truth for every skill the
# two packages share. opencode's copies are generated: identical bodies, plus the
# `name:` frontmatter key its loader requires.
#
#   scripts/sync-skills.sh           write the opencode copies
#   scripts/sync-skills.sh --check   report drift and exit 1 (for CI / pre-commit)
#
# A skill is treated as shared when its opencode counterpart directory already
# exists. That keeps claude's workflow skills (the /-commands) out of opencode,
# which has its own commands/ tree. To start sharing a new skill, create the
# destination directory once and rerun.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

SRC_ROOT="claude/.claude/skills"
DST_ROOT="opencode/.config/opencode/skills"

# Never synced:
#   agent-authoring - documents each platform's own frontmatter schemas and layout
SKIP="agent-authoring"

# Both packages use the same directory name for every shared skill, so there is no
# name mapping. claude's `grill` workflow skill has no opencode counterpart and is
# excluded by the opt-in-by-existence rule below, not by SKIP.

CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1

is_skipped() {
  for s in $SKIP; do [ "$s" = "$1" ] && return 0; done
  return 1
}

# Platform vocabulary: claude wording -> opencode wording, applied to every
# generated file. Keep this table small and unambiguous -- each entry names a
# tool or file that genuinely differs between the two harnesses. Anything that
# needs more than a phrase swap belongs in SKIP instead.
platformize() {
  sed -e 's/Agent tool/Task tool/g' "$1"
}

# opencode's schema requires `name:` to match the directory name; claude omits it.
render_skill() {
  awk -v n="$2" 'NR==1 {print; print "name: " n; next} {print}' "$1" \
    | sed -e 's/Agent tool/Task tool/g'
}

drift=0 wrote=0 same=0 unshared=""

emit() { # emit <rendered-file> <dest-path> <label>
  if cmp -s "$1" "$2" 2>/dev/null; then
    same=$((same + 1))
  elif [ "$CHECK" = 1 ]; then
    printf '  DRIFT   %s\n' "$3"; drift=$((drift + 1))
  else
    mkdir -p "$(dirname "$2")"; cp "$1" "$2"
    printf '  synced  %s\n' "$3"; wrote=$((wrote + 1))
  fi
}

for src in "$SRC_ROOT"/*/; do
  name=$(basename "$src")
  is_skipped "$name" && continue
  [ -f "$src/SKILL.md" ] || continue

  dst="$DST_ROOT/$name"
  if [ ! -d "$dst" ]; then
    unshared="$unshared $name"
    continue
  fi

  tmp=$(mktemp)
  render_skill "$src/SKILL.md" "$name" > "$tmp"
  emit "$tmp" "$dst/SKILL.md" "$name/SKILL.md"
  rm -f "$tmp"

  # Sibling docs at the skill root (e.g. GLOSSARY.md) and reference/ files are
  # copied verbatim -- no frontmatter to adjust.
  for extra in "$src"*.md "$src"reference/*.md; do
    [ -f "$extra" ] || continue
    base=$(basename "$extra")
    [ "$base" = "SKILL.md" ] && continue
    case "$extra" in
      *"/reference/"*) rel="reference/$base" ;;
      *)               rel="$base" ;;
    esac
    tmp=$(mktemp)
    platformize "$extra" > "$tmp"
    emit "$tmp" "$dst/$rel" "$name/$rel"
    rm -f "$tmp"
  done

  # Flag opencode-side files with no counterpart in claude.
  for orphan in "$dst"/*.md "$dst"/reference/*.md; do
    [ -f "$orphan" ] || continue
    base=$(basename "$orphan")
    case "$orphan" in
      *"/reference/"*) counterpart="$src/reference/$base" ;;
      *)               counterpart="$src/$base" ;;
    esac
    [ -f "$counterpart" ] || printf '  ORPHAN  %s/%s (no source in claude)\n' "$name" "$base"
  done
done

printf '\n%s: %d in sync' "$([ "$CHECK" = 1 ] && echo checked || echo synced)" "$same"
[ "$wrote" -gt 0 ] && printf ', %d written' "$wrote"
[ "$drift" -gt 0 ] && printf ', %d drifted' "$drift"
printf '\n'
[ -n "$unshared" ] && printf 'claude-only (no opencode counterpart):%s\n' "$unshared"

if [ "$drift" -gt 0 ]; then
  printf '\nRun scripts/sync-skills.sh to regenerate the opencode copies.\n'
  exit 1
fi
