import datetime as dt
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent
PACKAGE = SCRIPTS.parent
STAMP = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def run_script(name, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
    )


def task(tid="T-0001", status="DONE", depends="—"):
    return f"""### {tid} — Verify ledger integrity
- Status: {status}
- Tier: T1
- Owner: Test runner
- Created: {STAMP}
- Updated: {STAMP}
- Depends: {depends}
- Ask: Reject incomplete completion records.
- Scope fence: scripts/ledger_check.py
- Acceptance: Invalid records return exit 1.
- Notes: Controlled synthetic fixture.
"""


def change():
    return f"""## C-0001 — Validate records
- When: {STAMP}
- Author: Test runner
- Task: T-0001
- Commit: UNCOMMITTED — local verification only
- What: Validate completion records.
- Why: Avoid unsupported completion claims.
- Files: scripts/ledger_check.py
- Status: VERIFIED
- Delivery: NOT_DEPLOYED
- Verification:
  - Context: local Python; current working tree; {STAMP}
  - `python -m unittest` -> PASS (exit 0; 3 tests passed)
  - Not covered: production deployment; not requested.
"""


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="delivery-loop-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docs = {
            "MEMORY.md": f"# MEMORY — Fixture\n_Last updated: {STAMP} by Test runner_\n## What this is\nSynthetic ledger test.\n",
            "TASKS.md": "# TASKS\n\n" + task(),
            "CHANGES.md": "# CHANGES\n\n" + change(),
            "BUGS.md": "# BUGS\n",
            "DECISIONS.md": "# DECISIONS\n",
        }

    def check(self, expected=1, *args):
        for name, text in self.docs.items():
            (self.root / name).write_text(text, encoding="utf-8")
        result = run_script("ledger_check.py", "--root", self.root, *args)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout

    def test_valid_completion(self):
        self.check(0)

    def test_templates_are_not_verified_project_state(self):
        result = run_script("ledger_check.py", "--root", PACKAGE / "templates")
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_empty_verification_rejected(self):
        self.docs["CHANGES.md"] = change().split("- Verification:")[0] + "- Verification:\n"
        self.check()

    def test_placeholder_evidence_rejected(self):
        self.docs["CHANGES.md"] = change().replace("3 tests passed", "<observed result>")
        self.check()

    def test_unknown_primary_task_is_error(self):
        self.docs["CHANGES.md"] = change().replace("- Task: T-0001", "- Task: T-9999")
        self.check()

    def test_followup_mention_does_not_complete_task(self):
        self.docs["TASKS.md"] += "\n" + task("T-0002")
        self.docs["CHANGES.md"] += "- Follow-ups: T-0002\n"
        self.check()

    def test_owner_missing(self):
        self.docs["TASKS.md"] = task(status="IN_PROGRESS").replace("- Owner: Test runner\n", "")
        self.check()

    def test_status_missing(self):
        self.docs["TASKS.md"] = task().replace("- Status: DONE\n", "")
        self.check()

    def test_blocked_notes_cannot_be_empty(self):
        self.docs["TASKS.md"] = task(status="BLOCKED").replace("Controlled synthetic fixture.", "")
        self.check()

    def test_approval_required_for_started_t2(self):
        self.docs["TASKS.md"] = task(status="IN_PROGRESS").replace("- Tier: T1", "- Tier: T2")
        self.check()

    def test_dependency_cycle(self):
        self.docs["TASKS.md"] = task(depends="T-0002") + "\n" + task("T-0002", "PLANNED", "T-0001")
        self.check()

    def test_unfinished_dependency_blocks_start(self):
        self.docs["TASKS.md"] = task(depends="T-0002") + "\n" + task("T-0002", "PLANNED")
        self.check()

    def test_partial_evidence_cannot_complete_task(self):
        self.docs["CHANGES.md"] = change().replace("- Status: VERIFIED", "- Status: PARTIAL")
        self.check()

    def test_failed_command_cannot_be_verified(self):
        self.docs["CHANGES.md"] = change().replace("PASS (exit 0; 3 tests passed)", "FAIL (exit 1; assertion failed)")
        self.check()

    def test_fixed_bug_requires_real_root_cause(self):
        self.docs["BUGS.md"] = f"""## B-0001 — Invalid record accepted
- Found: {STAMP} by Test runner
- Status: FIXED
- Severity: S3
- Repro: Run checker on empty verification block.
- Expected: Exit 1.
- Actual: Exit 0.
- Root cause: —
- Fix: C-0001
- Regression: test_empty_verification_rejected fails on original script.
"""
        self.check()

    def test_missing_timestamp_offset(self):
        self.docs["TASKS.md"] = task().replace(STAMP, STAMP[:-6])
        self.check()

    def test_future_timestamp(self):
        future = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=2)).replace(microsecond=0).isoformat()
        self.docs["TASKS.md"] = task().replace(STAMP, future)
        self.check()

    def test_secret_diagnostics_do_not_echo_values(self):
        synthetic = "SYNTHETIC_TEST_VALUE_NOT_A_CREDENTIAL"
        self.docs["MEMORY.md"] += f"\npassword={synthetic}\n"
        output = self.check()
        self.assertNotIn(synthetic, output)

    def test_duplicate_archived_id(self):
        archive = self.root / "docs" / "agent-archive"
        archive.mkdir(parents=True)
        (archive / "TASKS-2025-Q1.md").write_text(task(), encoding="utf-8")
        self.check()

    def test_archived_completion_is_resolved(self):
        archive = self.root / "docs" / "agent-archive"
        archive.mkdir(parents=True)
        (archive / "CHANGES-2025-Q1.md").write_text(change(), encoding="utf-8")
        self.docs["CHANGES.md"] = "# CHANGES\n"
        self.check(0)

    def test_fenced_examples_are_not_real_entries(self):
        self.docs["TASKS.md"] += "\n```markdown\n" + task() + "```\n"
        self.check(0)

    def test_missing_root_is_setup_error(self):
        result = run_script("ledger_check.py", "--root", self.root / "missing")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_init_rejects_invalid_offset_without_writing(self):
        result = run_script("ledger_init.py", "--root", self.root, "--offset", "+12:99")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_init_is_idempotent_and_creates_no_fictional_history(self):
        first = run_script("ledger_init.py", "--root", self.root)
        self.assertEqual(first.returncode, 0, first.stderr)
        for name, prefix in (("CHANGES.md", "C"), ("BUGS.md", "B"), ("DECISIONS.md", "D")):
            self.assertNotRegex((self.root / name).read_text(encoding="utf-8"), rf"(?m)^## {prefix}-\d{{4}}")
        (self.root / "MEMORY.md").write_text("user-owned content", encoding="utf-8")
        second = run_script("ledger_init.py", "--root", self.root)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual((self.root / "MEMORY.md").read_text(encoding="utf-8"), "user-owned content")


    def test_invalid_offset_minutes(self):
        self.docs["TASKS.md"] = task().replace(STAMP, STAMP[:-6] + "+00:99")
        self.check()

    def test_fixed_bug_unknown_cause_and_invalid_closed(self):
        self.docs["BUGS.md"] = f"""## B-0001 — Empty evidence accepted
- Found: {STAMP} by Test runner
- Status: FIXED
- Severity: S3
- Repro: Run empty evidence fixture.
- Expected: Exit 1.
- Actual: Exit 0.
- Root cause: UNKNOWN — investigation pending
- Regression: Empty evidence fixture fails before fix.
- Fix: C-0001
- Closed: yesterday
"""
        self.check()

    def test_placeholder_title_rejected(self):
        self.docs["TASKS.md"] = task().replace("Verify ledger integrity", "<title>")
        self.check()

    def test_approved_t2_needs_actual_decision_id(self):
        self.docs["TASKS.md"] = task().replace("- Tier: T1", "- Tier: T2") + f"- Approval: APPROVED by Owner at {STAMP}: fixture scope\n- Rollback: Restore only fixture changes after permission.\n- Decision: We decided this verbally.\n"
        self.check()


    def test_partial_record_is_allowed_without_claiming_done(self):
        self.docs["TASKS.md"] = task(status="IN_REVIEW")
        self.docs["CHANGES.md"] = change().replace("- Status: VERIFIED", "- Status: PARTIAL").replace("PASS (exit 0; 3 tests passed)", "BLOCKED (test service unavailable; owner must provide sandbox)")
        self.check(0)

    def test_missing_coverage_limits_rejected(self):
        self.docs["CHANGES.md"] = change().replace("  - Not covered: production deployment; not requested.\n", "")
        self.check()

    def test_duplicate_field_rejected(self):
        self.docs["TASKS.md"] = task() + "- Status: PLANNED\n"
        self.check()

    def test_utc_z_timestamps(self):
        self.docs = {name: text.replace(STAMP, STAMP[:-6] + "Z") for name, text in self.docs.items()}
        self.check(0)

    def test_started_t2_with_recorded_approval_and_decision(self):
        self.docs["TASKS.md"] = task().replace("- Tier: T1", "- Tier: T2") + f"- Approval: APPROVED by Owner at {STAMP}: fixture scope\n- Rollback: Restore fixture edits after permission.\n- Decision: D-0001\n"
        self.docs["DECISIONS.md"] = f"""## D-0001 — Reuse the existing parser
- When: {STAMP} | Author: Test runner | Task: T-0001
- Status: ACCEPTED
- Question: How to validate completion links?
- Options: Reuse the parser or replace it; source inspected in scripts/ledger_check.py.
- Decision: Reuse existing parser boundaries.
- Gate: Traceable, needed, bounded, no dependency, no abstraction, reversible.
- Revisit: New ledger format requirements.
- Sources: scripts/ledger_check.py::audit inspected in this synthetic fixture.
"""
        self.check(0)

    def test_init_dry_run_has_no_writes(self):
        result = run_script("ledger_init.py", "--root", self.root, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_rotation_preserves_resolvable_history(self):
        self.check(0)
        result = run_script("ledger_rotate.py", "--root", self.root, "--keep", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        checked = run_script("ledger_check.py", "--root", self.root)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertNotIn("## C-0001", (self.root / "CHANGES.md").read_text(encoding="utf-8"))


class ContentTests(unittest.TestCase):
    def test_fenced_adapters_match_canonical_contract(self):
        import re
        pattern = r"<!-- BEGIN project-delivery-loop -->.*?<!-- END project-delivery-loop -->"
        canonical = re.search(pattern, (PACKAGE / "adapters" / "AGENTS.md").read_text(encoding="utf-8"), re.S).group()
        for path in (PACKAGE / "adapters").glob("*.md"):
            with self.subTest(path=path.name):
                match = re.search(pattern, path.read_text(encoding="utf-8"), re.S)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(), canonical)

    def test_skill_reference_paths_exist(self):
        import re
        skill = (PACKAGE / "SKILL.md").read_text(encoding="utf-8")
        for relative in re.findall(r"`(references/[^`]+\.md)`", skill):
            self.assertTrue((PACKAGE / relative).is_file(), relative)
        self.assertIn("version: 1.1.0", skill)
        self.assertLessEqual(len(skill.splitlines()), 300)

    def test_all_adapters_keep_essential_safeguards(self):
        for path in (PACKAGE / "adapters").iterdir():
            text = path.read_text(encoding="utf-8")
            for phrase in ("v1.1.0", "VERIFIED", "INFERRED", "ASSUMED", "UNKNOWN", "APPROVED", "BLOCKED", "NOT_RUN", "UNCOMMITTED", "DEPLOYED", "Not covered", "authorization"):
                with self.subTest(path=path.name, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_python_sources_compile(self):
        for path in SCRIPTS.glob("*.py"):
            compile(path.read_text(encoding="utf-8"), str(path), "exec")

    def test_reparse_detection_does_not_require_python312_path_api(self):
        import ledger_init
        from types import SimpleNamespace
        from unittest.mock import Mock, patch
        path = Mock()
        path.is_symlink.return_value = False
        path.exists.return_value = True
        path.lstat.return_value = SimpleNamespace(st_file_attributes=0x400)
        with patch.object(ledger_init.stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400, create=True):
            self.assertTrue(ledger_init.is_link(path))
            path.lstat.return_value = SimpleNamespace(st_file_attributes=0)
            self.assertFalse(ledger_init.is_link(path))
        path.is_junction.assert_not_called()

    def test_no_automatic_destructive_recovery_in_instructions(self):
        for path in [PACKAGE / "SKILL.md", *(PACKAGE / "adapters").iterdir(), *(PACKAGE / "references").glob("*.md")]:
            text = path.read_text(encoding="utf-8").lower()
            for phrase in ("revert to last green", "revert the working tree", "new dependency removes ≥100"):
                self.assertNotIn(phrase, text, str(path))


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="delivery installer '")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dest = self.root / ".devin" / "skills" / "project-delivery-loop"

    def install(self, *args, expected=0):
        result = run_script("install_skill.py", "--repo", self.root, *args)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def test_dry_run_is_write_free(self):
        self.install("--dry-run", "--init-ledgers")
        self.assertEqual(list(self.root.iterdir()), [])

    def test_reinstall_preserves_unrelated_files_and_ledgers(self):
        self.install("--init-ledgers")
        custom = self.dest / "local-notes.txt"
        custom.write_text("user-owned", encoding="utf-8")
        before = self.snapshot()
        self.install("--init-ledgers")
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / ".claude").exists())

    def test_local_edit_conflict_is_preflighted(self):
        self.install()
        (self.dest / "SKILL.md").write_text("locally edited", encoding="utf-8")
        before = self.snapshot()
        self.install("--init-ledgers", expected=2)
        self.assertEqual(self.snapshot(), before)

    def test_unmanaged_existing_file_is_preserved(self):
        self.dest.mkdir(parents=True)
        (self.dest / "SKILL.md").write_text("custom skill", encoding="utf-8")
        before = self.snapshot()
        self.install(expected=2)
        self.assertEqual(self.snapshot(), before)

    def test_source_overlap_is_rejected(self):
        result = run_script("install_skill.py", "--repo", PACKAGE, "--skills-dir", PACKAGE.parent)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_upgrade_creates_backup(self):
        import shutil
        source = self.root / "source"
        shutil.copytree(PACKAGE, source, ignore=shutil.ignore_patterns("__pycache__"))
        self.install("--source", source)
        old = (self.dest / "SKILL.md").read_bytes()
        (source / "SKILL.md").write_bytes(old + b"\nUpgrade fixture.\n")
        self.install("--source", source)
        backups = list(self.dest.glob("SKILL.md.delivery-loop-backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), old)
        self.assertEqual((self.dest / "SKILL.md").read_bytes(), old + b"\nUpgrade fixture.\n")

    def test_adapter_preserves_surrounding_content(self):
        target = self.root / ".devin" / "instructions.md"
        target.parent.mkdir()
        target.write_text("User rules before.\n", encoding="utf-8")
        self.install("--adapter", target, PACKAGE / "adapters" / "AGENTS.md")
        text = target.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("User rules before."))
        self.install("--adapter", target, PACKAGE / "adapters" / "AGENTS.md")
        self.assertEqual(target.read_text(encoding="utf-8"), text)

    def test_malformed_adapter_blocks_all_writes(self):
        target = self.root / ".devin" / "instructions.md"
        target.parent.mkdir()
        target.write_text("<!-- BEGIN project-delivery-loop -->\nunclosed", encoding="utf-8")
        before = self.snapshot()
        self.install("--adapter", target, PACKAGE / "adapters" / "AGENTS.md", expected=2)
        self.assertEqual(self.snapshot(), before)

    def test_corrupt_manifest_is_preserved(self):
        self.install()
        (self.dest / ".delivery-loop-manifest.json").write_text("broken", encoding="utf-8")
        before = self.snapshot()
        self.install(expected=2)
        self.assertEqual(self.snapshot(), before)

    def test_linked_destination_is_refused(self):
        target = self.root / "outside"
        target.mkdir()
        try:
            (self.root / ".devin").symlink_to(target, target_is_directory=True)
        except OSError:
            self.skipTest("OS does not allow this user to create symbolic links")
        self.install(expected=2)
        self.assertEqual(list(target.iterdir()), [])

    def test_shell_wrapper_handles_spaces_and_apostrophes(self):
        import shutil
        shell = shutil.which("bash")
        if not shell:
            self.skipTest("Bash is unavailable")
        result = subprocess.run([shell, str(PACKAGE / "install.sh"), "--repo", str(self.root), "--init-ledgers", "--name", "App 'quoted'"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.dest / "SKILL.md").is_file())

    def test_powershell_wrapper_dry_run(self):
        import shutil
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell is unavailable")
        result = subprocess.run([shell, "-NoProfile", "-File", str(PACKAGE / "install.ps1"), "-Repo", str(self.root), "-DryRun", "-InitLedgers", "-AllTools"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_shell_failure_propagates(self):
        import shutil
        shell = shutil.which("bash")
        if not shell:
            self.skipTest("Bash is unavailable")
        result = subprocess.run([shell, str(PACKAGE / "install.sh"), "--repo", str(self.root), "--offset", "invalid"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
