import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time

import ledger_init

SKILL = "project-delivery-loop"
MANIFEST = ".delivery-loop-manifest.json"
BEGIN = "<!-- BEGIN project-delivery-loop -->"
END = "<!-- END project-delivery-loop -->"


def digest(content):
    return hashlib.sha256(content).hexdigest()


def safe_path(path):
    path = Path(os.path.abspath(path.expanduser()))
    for part in (path, *path.parents):
        if ledger_init.is_link(part):
            raise ValueError(f"linked path refused: {part}")
    return path


def current(path):
    safe_path(path)
    if path.exists() and not path.is_file():
        raise ValueError(f"expected file: {path}")
    return path.read_bytes() if path.exists() else None


def package_files(source):
    paths = [source / "SKILL.md", source / "README.md"]
    for folder, extensions in (("references", {".md"}), ("templates", {".md"}), ("adapters", {".md", ".mdc"}), ("scripts", {".py"})):
        safe_path(source / folder)
        paths.extend(p for p in sorted((source / folder).iterdir())
                     if p.suffix in extensions and not p.name.startswith("test_"))
    return {path.relative_to(source).as_posix(): safe_path(path).read_bytes() for path in paths}


def skill_plan(source, skills_dir):
    dest = safe_path(skills_dir) / SKILL
    safe_path(dest)
    if dest == source or source in dest.parents or dest in source.parents:
        raise ValueError("source and destination must not overlap; install from a separate package directory")
    payload = package_files(source)
    manifest_path = dest / MANIFEST
    manifest_bytes = current(manifest_path)
    previous = json.loads(manifest_bytes) if manifest_bytes is not None else {}
    if not isinstance(previous, dict) or any(not isinstance(k, str) or not isinstance(v, str) or not re.fullmatch(r"[a-f0-9]{64}", v) for k, v in previous.items()):
        raise ValueError("invalid ownership manifest; inspect it manually")
    plan = []
    for relative, content in payload.items():
        path = dest / relative
        old = current(path)
        if old is not None and old != content and previous.get(relative) != digest(old):
            raise ValueError(f"local or unmanaged file would be overwritten: {path}")
        if old != content:
            plan.append((path, old, content))
    updated = {**previous, **{name: digest(content) for name, content in payload.items()}}
    encoded = (json.dumps(updated, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if encoded != manifest_bytes:
        plan.append((manifest_path, manifest_bytes, encoded))
    return plan


def adapter_plan(target, source):
    target = safe_path(target)
    incoming = safe_path(source).read_text(encoding="utf-8-sig")
    old = current(target)
    existing = old.decode("utf-8-sig") if old is not None else ""
    if incoming.count(BEGIN) != 1 or incoming.count(END) != 1:
        if old is not None and existing != incoming:
            raise ValueError(f"unfenced adapter conflict: {target}")
        new = incoming
    else:
        block = incoming[incoming.index(BEGIN):incoming.index(END) + len(END)]
        if existing.count(BEGIN) != existing.count(END) or existing.count(BEGIN) > 1:
            raise ValueError(f"malformed adapter markers: {target}")
        if BEGIN in existing:
            if existing.index(END) < existing.index(BEGIN):
                raise ValueError(f"reversed adapter markers: {target}")
            new = existing[:existing.index(BEGIN)] + block + existing[existing.index(END) + len(END):]
        elif existing:
            new = existing.rstrip("\r\n") + "\n\n" + block + "\n"
        else:
            new = incoming
    content = new.encode("utf-8")
    return [] if old == content else [(target, old, content)]


def apply(plan, dry_run=False):
    unique = {}
    for path, old, content in plan:
        if path in unique and unique[path] != (old, content):
            raise ValueError(f"conflicting destinations: {path}")
        unique[path] = (old, content)
    for path, (old, _) in unique.items():
        if current(path) != old:
            raise ValueError(f"destination changed during preflight: {path}")
    for path, (old, content) in unique.items():
        if dry_run:
            print(f"would {'update with backup' if old is not None else 'create'}: {path}")
            continue
        safe_path(path)
        if current(path) != old:
            raise ValueError(f"destination changed during installation: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        if old is not None:
            backup = path.with_name(path.name + f".delivery-loop-backup-{time.time_ns()}")
            with backup.open("xb") as stream:
                stream.write(old)
        fd, temporary = tempfile.mkstemp(prefix=".delivery-loop-", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            if current(path) != old:
                raise ValueError(f"destination changed before replacement: {path}")
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        print(f"{'updated (backup retained)' if old is not None else 'created'}: {path}")
    if not unique:
        print("Already up to date; no files changed.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--source", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--skills-dir", action="append", default=[])
    parser.add_argument("--adapter", nargs=2, action="append", default=[])
    parser.add_argument("--init-ledgers", action="store_true")
    parser.add_argument("--name")
    parser.add_argument("--offset", default="+00:00")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        root, source = safe_path(Path(args.repo)), safe_path(Path(args.source))
        if not root.is_dir() or not source.is_dir():
            raise ValueError("repository and source must be existing directories")
        ledger_init.now(args.offset)
        plan = []
        for folder in args.skills_dir or [root / ".devin" / "skills"]:
            plan.extend(skill_plan(source, Path(folder)))
        for target, adapter in args.adapter:
            plan.extend(adapter_plan(Path(target), Path(adapter)))
        if args.init_ledgers:
            plan.extend((path, None, text.encode("utf-8")) for path, text in ledger_init.prepare(root, args.name, args.offset, source / "templates").items())
        apply(plan, args.dry_run)
        print("Dry run complete; no writes." if args.dry_run else "Installation complete. Existing unrelated files were preserved.")
        if args.init_ledgers:
            print("Ledger initialization is not project verification; complete the bootstrap task from source evidence.")
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        print("Stopped without deleting directories. Completed file updates, if any, retain backups; review before retrying.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
