#!/usr/bin/env python3
"""Bootstrap the five ledger files into a repository.

Never overwrites an existing file. Safe to re-run.

    python3 ledger_init.py --root /path/to/repo [--name "My App"] [--offset +05:30]
"""
import argparse
import datetime as dt
import pathlib
import re
import stat
import sys

LEDGERS = ["MEMORY.md", "TASKS.md", "CHANGES.md", "BUGS.md", "DECISIONS.md"]


def now(offset: str) -> str:
    if not re.fullmatch(r"[+-](?:[01]\d|2[0-3]):[0-5]\d", offset):
        raise ValueError("offset must be +/-HH:MM with hours 00-23 and minutes 00-59")
    sign = -1 if offset.startswith("-") else 1
    hh, mm = map(int, offset[1:].split(":"))
    tz = dt.timezone(sign * dt.timedelta(hours=hh, minutes=mm))
    return dt.datetime.now(tz).replace(microsecond=0).isoformat()


def is_link(path):
    return path.is_symlink() or (path.exists() and bool(
        getattr(path.lstat(), "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    ))


def prepare(root, name=None, offset="+00:00", templates=None):
    stamp = now(offset)
    tpl = pathlib.Path(templates) if templates else pathlib.Path(__file__).resolve().parent.parent / "templates"
    planned = {}
    for filename in LEDGERS:
        dest = root / filename
        if is_link(dest):
            raise ValueError(f"refusing linked ledger: {filename}")
        if dest.exists():
            if not dest.is_file():
                raise ValueError(f"ledger path is not a file: {filename}")
            continue
        text = (tpl / filename).read_text(encoding="utf-8-sig")
        text = text.replace("<PROJECT NAME>", (name or root.name).replace("\n", " ").replace("\r", " "))
        text = text.replace("<ISO-8601 with offset>", stamp)
        if filename in {"CHANGES.md", "BUGS.md", "DECISIONS.md"}:
            text = re.split(r"(?m)^## [CBD]-\d{4}\b", text)[0].rstrip() + "\n"
        elif filename == "TASKS.md":
            text = text.split("## Active")[0] + f"""## Active

## Queued

### T-0001 — Reconstruct project memory
- Status: PLANNED
- Tier: T1
- Owner: —
- Created: {stamp}
- Updated: {stamp}
- Depends: —
- Ask: Reconstruct project state from inspected source files and observed commands.
- Scope fence: MEMORY.md, TASKS.md, CHANGES.md, BUGS.md, DECISIONS.md
- Acceptance: Memory has source-backed facts, explicit unknowns, verified command outcomes, and no template placeholders.
- Notes: Bootstrap only; no project analysis or application verification has run.

## Recently done
"""
        planned[dest] = text
    return planned


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--name", default=None, help="project name; defaults to the repo dir name")
    ap.add_argument("--offset", default="+00:00", help="fixed UTC offset, e.g. +05:30")
    ap.add_argument("--templates", default=None, help="templates dir (default: ../templates)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = pathlib.Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print("error: root must be an existing directory", file=sys.stderr)
        return 2
    try:
        planned = prepare(root, args.name, args.offset, args.templates)
        for dest, text in planned.items():
            if not args.dry_run:
                with dest.open("x", encoding="utf-8", newline="\n") as stream:
                    stream.write(text)
            print(f"{'would create' if args.dry_run else 'created'}: {dest.name}")
    except (OSError, UnicodeError, ValueError) as error:
        print(f"error: initialization stopped ({type(error).__name__}); existing ledgers were not overwritten", file=sys.stderr)
        return 2
    if planned:
        print("Next: complete T-0001 from source evidence. Bootstrap is not verified project state.")
    else:
        print("All ledgers already present; untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
