#!/usr/bin/env python3
"""Rotate old ledger entries into docs/agent-archive/, leaving a findable stub.

    python3 ledger_rotate.py --root /path/to/repo [--keep 50] [--dry-run]

Entries are blocks starting with '## X-nnnn'. Newest-first order is assumed.
OPEN bugs and ACCEPTED decisions are never rotated.
"""
import argparse
import datetime as dt
import pathlib
import re
import sys

HEAD_RE = {
    "CHANGES.md": re.compile(r"(?=^##\s+C-\d{4})", re.M),
    "BUGS.md": re.compile(r"(?=^##\s+B-\d{4})", re.M),
    "DECISIONS.md": re.compile(r"(?=^##\s+D-\d{4})", re.M),
}
KEEP_DEFAULT = {"CHANGES.md": 50, "BUGS.md": 20, "DECISIONS.md": 40}


def quarter(now: dt.datetime) -> str:
    return f"{now.year}-Q{(now.month - 1) // 3 + 1}"


def keepable(fname: str, block: str) -> bool:
    """Entries that must never rotate out regardless of age."""
    if fname == "BUGS.md":
        return bool(re.search(r"^-\s*Status:\s*(OPEN|CONFIRMED|IN_PROGRESS)", block, re.M))
    if fname == "DECISIONS.md":
        return bool(re.search(r"^-\s*Status:\s*(ACCEPTED|REJECTED(_FOR_NOW)?)", block, re.M))
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--keep", type=int, default=None, help="override entries kept per file")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.root).expanduser().resolve()
    archive_dir = root / "docs" / "agent-archive"
    q = quarter(dt.datetime.now())
    touched = False

    for fname, splitter in HEAD_RE.items():
        path = root / fname
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        parts = splitter.split(text)
        header, blocks = parts[0], [b for b in parts[1:] if b.strip()]
        keep_n = args.keep if args.keep is not None else KEEP_DEFAULT[fname]
        if len(blocks) <= keep_n:
            print(f"{fname}: {len(blocks)} entries, under keep={keep_n} - nothing to do")
            continue

        kept, moved = [], []
        for i, b in enumerate(blocks):
            (kept if (i < keep_n or keepable(fname, b)) else moved).append(b)
        if not moved:
            print(f"{fname}: all remaining entries are pinned - nothing to do")
            continue

        ids = re.findall(r"^##\s+([A-Z]-\d{4})", "".join(moved), re.M)
        rng = f"{ids[-1]}..{ids[0]}" if ids else "?"
        arch_path = archive_dir / f"{path.stem}-{q}.md"
        stub = (
            f"\n> Archived {len(moved)} earlier entries ({rng}) -> "
            f"`{arch_path.relative_to(root)}` on {dt.date.today().isoformat()}\n"
        )
        new_text = header.rstrip() + "\n" + stub + "\n" + "".join(kept)

        if args.dry_run:
            print(f"{fname}: would archive {len(moved)} entries ({rng}) -> {arch_path}")
        else:
            archive_dir.mkdir(parents=True, exist_ok=True)
            prev = arch_path.read_text(encoding="utf-8") if arch_path.exists() else f"# {path.stem} archive — {q}\n"
            arch_path.write_text(prev.rstrip() + "\n\n" + "".join(moved), encoding="utf-8")
            path.write_text(new_text, encoding="utf-8")
            print(f"{fname}: archived {len(moved)} entries ({rng}) -> {arch_path.relative_to(root)}")
        touched = True

    if not touched:
        print("nothing rotated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
