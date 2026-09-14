#!/usr/bin/env bash
# Install the project-delivery-loop skill + per-tool adapter files.
#
#   ./install.sh --repo /path/to/repo          # project scope (default)
#   ./install.sh --repo /path/to/repo --user   # also install for the user globally
#   ./install.sh --repo /path/to/repo --init-ledgers --name "My App" --offset +05:30
#   ./install.sh --repo /path/to/repo --dry-run
#
# Idempotent. Existing ledgers are never overwritten. Adapter blocks are fenced
# with markers, so re-running updates the block in place instead of duplicating.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL="project-delivery-loop"
REPO=""; DO_USER=0; DO_INIT=0; DRY=0; ALL_TOOLS=0; NAME=""; OFFSET="+00:00"
PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 10))' >/dev/null 2>&1; then
    PYTHON="$candidate"; break
  fi
done
[ -n "$PYTHON" ] || { echo "error: Python 3.10+ is required" >&2; exit 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --repo|--name|--offset)
      [ $# -ge 2 ] || { echo "error: missing value for $1" >&2; exit 2; }
      case "$1" in
        --repo) REPO="$2" ;;
        --name) NAME="$2" ;;
        --offset) OFFSET="$2" ;;
      esac
      shift 2 ;;
    --user) DO_USER=1; shift ;;
    --all-tools) ALL_TOOLS=1; shift ;;
    --init-ledgers) DO_INIT=1; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: install.sh --repo PATH [--dry-run] [--init-ledgers] [--name NAME] [--offset +HH:MM] [--user] [--all-tools]' 'Default: .devin/skills only. --all-tools explicitly enables compatibility adapters.'
      exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
[ -n "$REPO" ] && [ -d "$REPO" ] || { echo "error: --repo must name an existing directory" >&2; exit 2; }
ARGS=("$SRC/scripts/install_skill.py" --repo "$REPO" --source "$SRC" "--offset=$OFFSET")

copy_skill() {  # $1 = destination skills dir
  ARGS+=(--skills-dir "$1")
}

link_dir() {  # $1 = alias dir that should point at .agents/skills
  copy_skill "$1"
}

write_block() {  # $1 = target file, $2 = source adapter (fenced block appended/updated)
  ARGS+=(--adapter "$1" "$2")
}

copy_skill "$REPO/.devin/skills"
if [ "$ALL_TOOLS" = 1 ]; then
  copy_skill "$REPO/.agents/skills"
  link_dir "$REPO/.claude/skills"
  link_dir "$REPO/.codex/skills"
  link_dir "$REPO/.github/skills"
  A="$SRC/adapters"
  for target in AGENTS.md CLAUDE.md GEMINI.md CONVENTIONS.md .github/copilot-instructions.md .windsurf/rules/delivery-loop.md .clinerules/delivery-loop.md .roo/rules/delivery-loop.md .amazonq/rules/delivery-loop.md .junie/guidelines.md .zed/rules.md; do
    write_block "$REPO/$target" "$A/AGENTS.md"
  done
  write_block "$REPO/.cursor/rules/delivery-loop.mdc" "$A/cursor-project-delivery-loop.mdc"
fi
if [ "$DO_USER" = 1 ]; then copy_skill "$HOME/.config/devin/skills"; fi
if [ "$DO_INIT" = 1 ]; then ARGS+=(--init-ledgers); fi
if [ "$DRY" = 1 ]; then ARGS+=(--dry-run); fi
if [ -n "$NAME" ]; then ARGS+=(--name "$NAME"); fi
PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 "$PYTHON" -B "${ARGS[@]}"
