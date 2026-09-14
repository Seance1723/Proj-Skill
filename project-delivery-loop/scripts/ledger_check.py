#!/usr/bin/env python3
"""Audit ledger consistency. Run at P9, before ending a session.

    python3 ledger_check.py --root /path/to/repo [--max-memory-age-days 14]

Exit codes: 0 clean, 1 problems found, 2 setup error.
Checks are mechanical on purpose - they catch the failure modes that make a
ledger untrustworthy, not the ones that need judgement.
"""
import argparse
import datetime as dt
import pathlib
import re
import sys

ID_RE = re.compile(r"^#{2,3}[ \t]+([TCBD]-\d{4})\b[^\n]*", re.M)
TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-](?:[01]\d|2[0-3]):[0-5]\d|Z)")
LOOSE_TS_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?(?:[+-]\d{2}:\d{2}|Z)?")
CAPS = {"MEMORY.md": 400, "CHANGES.md": 1500, "TASKS.md": 900, "BUGS.md": 1200, "DECISIONS.md": 1200}
FILES = list(CAPS)
TASK_STATUSES = {"BACKLOG", "PLANNED", "IN_PROGRESS", "BLOCKED", "IN_REVIEW", "DONE", "DROPPED"}
STARTED = {"IN_PROGRESS", "IN_REVIEW", "DONE"}
PLACEHOLDER_RE = re.compile(r"<[^>\n]*>|\b(?:TBD|TODO|FIXME)\b", re.I)


def parse_timestamp(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def substantive(value):
    value = value.strip()
    return bool(value and value.upper() not in {"—", "-", "N/A", "NONE", "UNKNOWN"}
                and not PLACEHOLDER_RE.search(value.replace("<redacted>", "REDACTED")))


def prose(text):
    lines, fence = [], None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            lines.append("")
        else:
            lines.append(line if fence is None else "")
    return re.sub(r"<!--.*?-->", "", "\n".join(lines), flags=re.S)


def fields(block):
    result = {}
    key = None
    for line in block.splitlines():
        match = re.match(r"^-[ \t]+([^:\n]+):[ \t]*(.*)$", line)
        if match:
            key = match.group(1).strip()
            if key in result:
                raise ValueError("duplicate field")
            result[key] = match.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            result[key] += "\n" + line
        else:
            key = None
    return result


def entries(text):
    heads = list(re.finditer(r"^#{1,3}[ \t]+[^\n]*", text, re.M))
    for index, head in enumerate(heads):
        match = ID_RE.match(head.group())
        if match:
            end = heads[index + 1].start() if index + 1 < len(heads) else len(text)
            yield match.group(1), text[head.start():end]


def audit(root, max_age):
    problems, warnings = [], []
    docs = {}
    for name in FILES:
        path = root / name
        if not path.is_file():
            problems.append(f"missing ledger: {name} (run ledger_init.py)")
        docs[name] = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    archive = root / "docs" / "agent-archive"
    if archive.is_dir():
        for path in sorted(archive.glob("*.md")):
            docs[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8-sig")
    clean = {name: prose(text) for name, text in docs.items()}
    records = {}

    # 1. duplicate IDs
    for name, text in clean.items():
        for ident, block in entries(text):
            if ident in records:
                problems.append(f"{name}: duplicate id {ident} (including archives)")
                continue
            try:
                data = fields(block)
            except ValueError:
                problems.append(f"{name}: {ident} has duplicate fields")
                data = {}
            records[ident] = (name, block, data)
            title = block.splitlines()[0].split(ident, 1)[1].lstrip(" —-")
            if not substantive(title):
                problems.append(f"{ident}: missing or placeholder title")
            expected = {"TASKS.md": "T", "CHANGES.md": "C", "BUGS.md": "B", "DECISIONS.md": "D"}.get(name)
            if expected and not ident.startswith(expected):
                problems.append(f"{name}: {ident} is in the wrong ledger")
    tasks = {i: r[2] for i, r in records.items() if i.startswith("T-")}
    changes = {i: r[2] for i, r in records.items() if i.startswith("C-")}

    def require(ident, data, *names):
        for key in names:
            if not substantive(data.get(key, "")):
                problems.append(f"{ident}: missing or placeholder {key}")

    # 2. changes must reference a real task
    verified_tasks = set()
    for cid, data in changes.items():
        before = len(problems)
        require(cid, data, "When", "Author", "Task", "Commit", "What", "Why", "Files", "Verification")
        primary = data.get("Task", "").split("|")[0].strip()
        refs = re.findall(r"\bT-\d{4}\b", primary)
        if not refs or any(t not in tasks for t in refs):
            problems.append(f"{cid}: Task must reference existing task IDs")
        commit = data.get("Commit", "")
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}|(?:UNCOMMITTED|NOT_APPLICABLE)\s+[—-]\s+\S.*", commit):
            problems.append(f"{cid}: Commit needs a SHA or an explicit uncommitted/not-applicable reason")
        status = data.get("Status", "")
        if status not in {"VERIFIED", "PARTIAL", "FAILED", "NOT_RUN"}:
            problems.append(f"{cid}: invalid or missing verification Status")
        delivery = data.get("Delivery", "")
        if delivery not in {"NOT_DEPLOYED", "DEPLOYED", "NOT_APPLICABLE"}:
            problems.append(f"{cid}: invalid or missing Delivery")
        if delivery == "DEPLOYED":
            require(cid, data, "Deployment evidence")
        evidence = data.get("Verification", "")
        for key in ("Context", "Not covered"):
            match = re.search(rf"^\s+- {key}:[ \t]*(.+)$", evidence, re.M)
            if not match or not substantive(match.group(1)):
                problems.append(f"{cid}: Verification needs {key}")
        results = re.findall(r"^\s+- (?:`[^`]+`|Manual:[^\n]+?)\s*(?:->|→)\s*(PASS|FAIL|BLOCKED|NOT_RUN)\b([^\n]*)", evidence, re.M)
        if status == "VERIFIED":
            if not results or any(result != "PASS" or not substantive(detail) for result, detail in results):
                problems.append(f"{cid}: VERIFIED requires observed PASS evidence without failed or unrun checks")
            for line in evidence.splitlines():
                if re.match(r"\s+- `", line) and not re.search(r"(?:->|→)\s*PASS\b.*\bexit 0\b", line):
                    problems.append(f"{cid}: verified commands must record PASS and exit 0")
        if len(problems) == before and status == "VERIFIED":
            verified_tasks.update(refs)

    # 3. DONE tasks need a change entry
    dependencies = {}
    for tid, data in tasks.items():
        require(tid, data, "Status", "Tier", "Created", "Updated", "Ask", "Scope fence", "Acceptance")
        status = data.get("Status", "")
        tier = data.get("Tier", "")
        if status not in TASK_STATUSES:
            problems.append(f"{tid}: invalid or missing task Status")
        if tier not in {"T0", "T1", "T2", "T3"}:
            problems.append(f"{tid}: invalid or missing Tier")
        if status in STARTED:
            require(tid, data, "Owner")
            if tier in {"T2", "T3"}:
                require(tid, data, "Approval", "Rollback", "Decision")
                approval = data.get("Approval", "")
                if not re.match(r"APPROVED by .+ at ", approval) or not TS_RE.search(approval):
                    problems.append(f"{tid}: T2/T3 work requires explicit APPROVED evidence with owner and timestamp")
                if not re.search(r"\bD-\d{4}\b", data.get("Decision", "")):
                    problems.append(f"{tid}: T2/T3 work requires a decision ID")
        if status in {"BLOCKED", "DROPPED"}:
            require(tid, data, "Notes")
        if status == "DONE" and tid not in verified_tasks:
            problems.append(f"{tid}: DONE needs a valid VERIFIED change with this primary Task")
        depends = data.get("Depends", "—")
        if not re.fullmatch(r"(?:—|-|NONE|T-\d{4}(?:[ ,]+T-\d{4})*)", depends):
            problems.append(f"{tid}: Depends must contain task IDs or an explicit empty marker")
        dependencies[tid] = re.findall(r"\bT-\d{4}\b", depends)
        for dep in dependencies[tid]:
            if dep not in tasks:
                problems.append(f"{tid}: unknown dependency {dep}")
            elif status in STARTED and tasks[dep].get("Status") != "DONE":
                problems.append(f"{tid}: started with unfinished dependency {dep}")
    pending = {tid: set(deps) & tasks.keys() for tid, deps in dependencies.items()}
    while pending:
        ready = {tid for tid, deps in pending.items() if not deps}
        if not ready:
            problems.append("TASKS.md: dependency cycle (or tasks blocked by a cycle)")
            break
        pending = {tid: deps - ready for tid, deps in pending.items() if tid not in ready}

    # 4. bug hygiene
    for ident, (_, _, data) in records.items():
        if ident.startswith("B-"):
            require(ident, data, "Found", "Status", "Severity", "Repro", "Expected", "Actual")
            if data.get("Status") not in {"OPEN", "CONFIRMED", "IN_PROGRESS", "FIXED", "WONTFIX", "CANNOT_REPRODUCE"}:
                problems.append(f"{ident}: invalid bug Status")
            if data.get("Severity") not in {"S1", "S2", "S3", "S4"}:
                problems.append(f"{ident}: invalid Severity")
            if data.get("Status") == "FIXED":
                require(ident, data, "Root cause", "Regression", "Fix", "Closed")
                if not re.search(r"\bC-\d{4}\b", data.get("Fix", "")):
                    problems.append(f"{ident}: FIXED requires a change reference")
                if re.match(r"(?:UNKNOWN|UNCONFIRMED|ASSUMED|INFERRED)\b", data.get("Root cause", ""), re.I):
                    problems.append(f"{ident}: FIXED requires a confirmed root cause")
                if not TS_RE.fullmatch(data.get("Closed", "")):
                    problems.append(f"{ident}: Closed requires a timestamp with offset")
            if data.get("Status") in {"WONTFIX", "CANNOT_REPRODUCE"}:
                require(ident, data, "Notes")
        if ident.startswith("D-"):
            require(ident, data, "When", "Status", "Question", "Options", "Decision", "Gate", "Revisit", "Sources")
            if not re.fullmatch(r"ACCEPTED|REJECTED|REJECTED_FOR_NOW|SUPERSEDED_BY_D-\d{4}", data.get("Status", "")):
                problems.append(f"{ident}: invalid decision Status")
            successor = data.get("Status", "").removeprefix("SUPERSEDED_BY_")
            if successor.startswith("D-") and (successor not in records or successor == ident):
                problems.append(f"{ident}: invalid superseding decision reference")
            author = re.search(r"\bAuthor:[ \t]*([^|]+)", data.get("When", ""))
            if not substantive(data.get("Author", "")) and (not author or not substantive(author.group(1))):
                problems.append(f"{ident}: missing decision author")

    # 5. timestamps
    now = dt.datetime.now(dt.timezone.utc)
    for name, text in clean.items():
        for number, line in enumerate(text.splitlines(), 1):
            for match in LOOSE_TS_RE.finditer(line):
                raw = match.group()
                try:
                    if not TS_RE.fullmatch(raw):
                        raise ValueError()
                    stamp = parse_timestamp(raw)
                    if stamp > now + dt.timedelta(minutes=5):
                        problems.append(f"{name}:{number}: future timestamp")
                except ValueError:
                    problems.append(f"{name}:{number}: invalid timestamp or missing offset")
    for ident, (_, _, data) in records.items():
        keys = ("Created", "Updated") if ident.startswith("T-") else (("Found",) if ident.startswith("B-") else ("When",))
        for key in keys:
            valid = TS_RE.fullmatch(data.get(key, "")) if ident.startswith("T-") else TS_RE.match(data.get(key, ""))
            if not valid:
                problems.append(f"{ident}: {key} needs an ISO-8601 timestamp with offset")
        if ident.startswith("T-"):
            try:
                if parse_timestamp(data["Updated"]) < parse_timestamp(data["Created"]):
                    problems.append(f"{ident}: Updated precedes Created")
            except (KeyError, ValueError, TypeError):
                pass
    memory = clean["MEMORY.md"]
    mem_match = re.search(r"Last updated: (\S+) by (.+?)_?$", memory, re.M)
    if not mem_match or not TS_RE.fullmatch(mem_match.group(1)) or not substantive(mem_match.group(2)):
        problems.append("MEMORY.md: missing Last updated timestamp or author")
    if PLACEHOLDER_RE.search(memory.replace("<redacted>", "REDACTED")) or "Bootstrap: REQUIRED" in memory:
        problems.append("MEMORY.md: unfinished bootstrap or template placeholders")

    # 6. size caps
    for name, cap in CAPS.items():
        count = len(docs[name].splitlines())
        if count > cap:
            (problems if name == "MEMORY.md" else warnings).append(f"{name}: {count} lines exceeds cap {cap}")

    # 7. memory freshness
    if mem_match:
        try:
            updated = parse_timestamp(mem_match.group(1))
            if now - updated > dt.timedelta(days=max_age):
                warnings.append("MEMORY.md: stale; revalidate facts before relying on them")
        except (ValueError, TypeError):
            pass

    # 8. secret smell test
    secret = re.compile(r"(?i)(?:\b(?:api[_-]?key|secret|password|passwd|token)\s*[:=]\s*[\"']?([^\s\"'`,;]+)|bearer\s+[A-Za-z0-9._-]{12,}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{16,}|-----BEGIN [A-Z ]*PRIVATE KEY)")
    for name, text in docs.items():
        for number, line in enumerate(text.splitlines(), 1):
            for match in secret.finditer(line):
                if match.group(1) in {"<redacted>", "NAMES", "ONLY", "—", "-"}:
                    continue
                problems.append(f"{name}:{number}: possible secret; inspect locally and redact (value withheld)")
                break

    # 9. dangling references
    for name, text in clean.items():
        for ref in sorted(set(re.findall(r"\b[TCBD]-\d{4}\b", text))):
            if ref not in records:
                problems.append(f"{name}: reference to unknown ID {ref}")
    return problems, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--max-memory-age-days", type=int, default=14)
    ap.add_argument("--strict", action="store_true", help="also fail on warnings")
    args = ap.parse_args()
    root = pathlib.Path(args.root).expanduser().resolve()
    if not root.is_dir() or args.max_memory_age_days < 0:
        print("error: root must exist and maximum memory age must be nonnegative", file=sys.stderr)
        return 2
    try:
        problems, warnings = audit(root, args.max_memory_age_days)
    except (OSError, UnicodeError):
        print("error: cannot read ledgers as UTF-8; check paths and permissions", file=sys.stderr)
        return 2
    print(f"ledger_check: {root}")
    for problem in problems:
        print(f"  FAIL  {problem}")
    for warning in warnings:
        print(f"  WARN  {warning}")
    if not problems and not warnings:
        print("  clean (structure only; execution, claims and approvals require independent review)")
    print(f"\n{len(problems)} problem(s), {len(warnings)} warning(s)")
    return 1 if problems or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
