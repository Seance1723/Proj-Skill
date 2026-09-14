# project-delivery-loop — v1.1.0

An evidence-first Agent Skill for managing software changes without losing
context, expanding scope silently, or claiming work that was never verified.
It keeps five Markdown ledgers and scales the workflow to the risk of the task.
It reduces unsupported claims; it does not guarantee zero hallucinations.

## What is stronger in 1.1.0

- Facts, inferences, assumptions, and unknowns are explicitly separated.
- Source/version checks precede architecture claims, commands, APIs, and edits.
- Tasks have dependency, readiness, scope, approval, and measurable acceptance gates.
- Verification records distinguish PASS, FAIL, BLOCKED, and NOT_RUN; implemented,
  verified, committed, and deployed are not interchangeable.
- The checker rejects incomplete/placeholder evidence, false completion links,
  missing ownership, unapproved started T2/T3 work, and dependency cycles.
- Recovery preserves user edits instead of automatically resetting the tree.
- Installers preflight conflicts, preserve unrelated files, retain update backups,
  avoid shell eval, propagate failure, and support write-free dry runs.

## Install safely

Requires **Python 3.10+**, standard library only. Run from this extracted package
folder into a separate existing project. Inspect the dry-run before installing.

Bash:

```bash
bash ./install.sh --repo "/path/to/your/repo" --dry-run
bash ./install.sh --repo "/path/to/your/repo" --init-ledgers --name "My App" --offset +05:30
```

PowerShell:

```powershell
.\install.ps1 -Repo "C:\code\my-app" -DryRun
.\install.ps1 -Repo "C:\code\my-app" -InitLedgers -Name "My App" -Offset "+05:30"
```

The PowerShell wrapper must be permitted by your organization's signing/execution
policy. Do not disable that policy. In an environment where running the Python
entry point is approved, the equivalent default installation is:

```text
python -B scripts/install_skill.py --repo <existing-project> --dry-run
python -B scripts/install_skill.py --repo <existing-project> --init-ledgers
```

The default destination is `.devin/skills/project-delivery-loop/`. Add `--user`
(`-User`) only when you want an additional global copy under
`~/.config/devin/skills/`. It does not install into other tools by default.

Add **`--all-tools` / `-AllTools`** explicitly to also write compatibility copies
and adapters. Review those paths in dry-run; only use this when those tools are
part of your workflow. This is a deliberate change from the v1.0 all-tools default.

| Scope | Paths |
|---|---|
| Default | `.devin/skills/project-delivery-loop/` |
| Opt-in compatibility skills | `.agents/skills/`, `.claude/skills/`, `.codex/skills/`, `.github/skills/` |
| Opt-in root adapters | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONVENTIONS.md` |
| Opt-in tool adapters | Existing package mappings for Copilot, Cursor, Windsurf, Cline, Roo, Amazon Q, Junie, Zed |
| Explicit global copy | `~/.config/devin/skills/project-delivery-loop/` |

Adapters contain a fallback contract and point to the full skill. Host instruction
precedence and tool permissions always apply. Installation is not permission to
commit, deploy, rotate secrets, or operate on production.

## Upgrade and conflict behavior

- Re-running identical installation makes no changes. Existing ledgers are never
  overwritten. Initialization produces a planned reconstruction task, not fake
  changes, bugs, decisions, or proof that the app works.
- Ownership hashes track installed skill files. An unchanged managed file can be
  upgraded; a locally modified or unmanaged conflicting file stops installation
  during preflight. Identical legacy files can be adopted without replacing them.
- Before updates, previous file contents are retained as
  `<filename>.delivery-loop-backup-<unique-number>`. Review backups manually; they
  are not deleted automatically. Protect them as carefully as the originals.
- Fenced adapters preserve surrounding instructions and retain backups on update.
  Malformed/duplicate markers and unfenced conflicting adapters are refused.
- Symlink/junction destinations and overlapping source/destination paths are
  refused. Older linked installs need a human-reviewed migration; do not delete
  or replace those links blindly.
- Installation is preflighted and file replacements are atomic, but the whole
  multi-file operation is not transactional. I/O failures may leave partial
  updates. Review output and backups before retrying; no automatic rollback.
- Old package files are not deleted. Use a single installer writer at a time.

## The ledgers

| File | Purpose |
|---|---|
| `MEMORY.md` | Source-backed snapshot, commands, invariants, unknowns, handoff; max 400 lines |
| `TASKS.md` | IDs, risk, owner, priority, dependencies, scope, approval, acceptance |
| `CHANGES.md` | Actual implementation and verification evidence; append-only corrections |
| `BUGS.md` | Repro, expected/actual, confirmed root cause, regression evidence |
| `DECISIONS.md` | Alternatives, rationale, evidence, rejected ideas, revisit triggers |

Read-only project questions do not create or mutate ledgers. For an existing
project adopting the workflow, reconstruct memory from inspected source and
observed commands. Record UNKNOWN where evidence is unavailable; remove the
bootstrap marker only after reconstruction. The generated template is expected
to fail the audit until completed honestly.

## Audit, initialization, and rotation

From the extracted package:

```text
python -B scripts/ledger_init.py --root <repo> --dry-run
python -B scripts/ledger_check.py --root <repo>
python -B scripts/ledger_check.py --root <repo> --strict
python -B scripts/ledger_rotate.py --root <repo> --dry-run
```

From an installed project's root:

```text
python -B .devin/skills/project-delivery-loop/scripts/ledger_check.py --root .
```

Checker exits: 0 = no errors (warnings may remain without --strict), 1 = ledger
validation failed, 2 = setup/read error. The checker validates record structure,
links, timestamps, dependencies, evidence shape and probable secrets. It does
**not** execute recorded commands, authenticate approvals, validate Git SHAs,
prove factual accuracy, or confirm production deployment. Review the evidence.

For old ledgers, use the new templates/reference schema. Do not backfill invented
approvals or results: preserve historical records, mark unsupported work partial,
and append corrections with fresh evidence. Preview rotation and obtain approval
before rewriting ledgers. Completed task definitions must remain live or be
archived in full; the rotation script does not rotate TASKS.md.

## Verify this package

From the extracted package folder:

```text
python -B -m unittest discover -s scripts -p "test_*.py"
```

Tests use synthetic data and temporary directories; they do not install globally
or touch a real application's data. Installer tests cover conflict preflight,
idempotency, backups, path quoting, dry runs, and wrapper behavior. Bash/PowerShell
checks require the corresponding shell. The symlink test is explicitly skipped
when the OS denies creating the test link. A PowerShell policy denial is reported
as a failed native-wrapper check, not silently bypassed or called a pass.

## Layout

- `SKILL.md`: source of the workflow, version 1.1.0.
- `references/01–06`: tiering, grounding, verification, schemas, hygiene, rationale.
- `templates/`: five ledger schemas; placeholder examples are not project history.
- `scripts/`: checker, initializer, rotator, shared installer backend, regression tests.
- `adapters/`: per-tool compatibility instructions.
- `install.sh`, `install.ps1`: argument-safe wrappers around the shared backend.

Tune risk tiers to actual blast radius, keep memory short, and use existing
project tools. No mandatory issue tracker, new service, external model API,
automatic deployment, or speculative framework is required.
