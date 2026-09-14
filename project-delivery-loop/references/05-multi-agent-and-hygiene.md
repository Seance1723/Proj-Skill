# 05 — Concurrency, Hygiene, Handoff and Portability

## Coordination without imaginary ownership

Use multiple agents only when the user and host permit delegation. Otherwise
work sequentially. A Markdown Owner field is coordination, not a lock.

- Claim one task per owner with IN_PROGRESS, Owner, and actual Updated timestamp
  before editing. Re-read current task/file state before writing a change.
- Separate subsystem boundaries and scope fences. Two agents touching the same
  behavior can conflict even if they edit different files.
- Designate one coordinator for shared ledger updates and ID allocation. Allocate
  IDs after checking live ledgers and archives. Do not invent IDs from a cached
  summary, duplicate IDs, or silently renumber existing records.
- Do not seize another owner's task because a timestamp is old. Ask the owner or
  coordinator, verify branch/worktree activity, and record the agreed transfer.
- Tool results from another agent are leads/evidence, not automatic completion.
  Inspect the diff and actual verification results before integrating claims.
- Shared installs/rotation are single-writer operations. Stop on observed drift;
  the file tools and ledgers do not provide a distributed concurrency lock.

## Ledger update discipline

Update state when it changes: claim before implementation, blockers immediately,
evidence before DONE. Batch adjacent edits sensibly, not all updates at session
end. Avoid reformatting, resorting, or rewriting unrelated history.

On conflict, preserve both real records, reconcile duplicate IDs with the owners,
and audit cross-links. Do not choose one side just to make a clean merge. Record
corrections explicitly. Follow the host's commit permissions; never create a WIP
commit, stash, or force-push merely to satisfy a workflow instruction.

## Handoff and context recovery

Post a compact handoff at session end and before a context reset. For unfinished
work, save the durable parts in task Notes and MEMORY.md without duplicating the
whole transcript. Read the task, current source state, and verification evidence
again on resume; summaries and graphs can be stale.

```text
HANDOFF — <actual timestamp>
Goal:          <approved outcome/current milestone>
Branch / tree: <observed branch and changed files, or no Git>
Completed:     <DONE task IDs -> VERIFIED change IDs>
Partial:       <implemented but not verified/released work>
Blocked:       <task, exact reason, attempts and evidence, required owner action>
Verification:  <actual commands/results and revision/environment; explicit limits>
Delivery:      <NOT_DEPLOYED / DEPLOYED with evidence / NOT_APPLICABLE>
Next action:   <single concrete step, task and owner>
Approval:      <pending action-specific authorization, or none>
Learned:       <source-backed fact and where it was saved; UNKNOWN where unresolved>
```

Do not call a handoff "complete delivery" if required checks are blocked. Preserve
all requested work in the queue and explain any deferral to the user immediately.
Do not substitute speculative follow-ups for finishing the approved scope.

## Secret and sensitive-data hygiene

Never save credentials, session data, `.env` values, connection strings, private
keys, customer PII, or credential-bearing logs in ledgers, research queries,
examples, artifacts, or commit messages. Use names, synthetic values, safe shapes,
and explicit `<redacted>` replacements. Review before copying tool output.

For reports involving real data, describe its shape and failure behavior, not
identifying values. The audit's pattern matching is only a safety net and cannot
prove the absence of secrets. Diagnostics must identify a location without
printing the matched value.

If a credential leak is discovered: stop further exposure, notify the owner,
record only safe metadata, and obtain permission for revocation/rotation and any
history repair. Do not retrieve additional secrets, scrub history, or rotate
credentials autonomously. Follow the organization's incident process.

## Portability and installation

This skill is the process source; ledgers are project-state records requiring
revalidation, not infallible authority. Keep project facts out of SKILL.md and
avoid tool-specific UI instructions in ledgers.

Locate the actual skill path reported by the host. New default installs use
`.devin/skills/project-delivery-loop/`; global installs requested with --user/-User
use `~/.config/devin/skills/`. Compatibility paths/adapters require explicit
`--all-tools` / `-AllTools`. Do not create competing global copies without approval.

Each adapter carries an essential fallback and points to the full skill. Read
references when the risk demands it; do not blindly run unavailable tools or
assume the same runtime/permissions in a different agent. Keep adapters aligned
when core safety or evidence rules change.

Install from a separate extracted source directory. Preview with --dry-run/-DryRun.
The shared backend checks paths and ownership before writing, rejects linked
paths and locally modified managed files, preserves unrelated files, and retains
backups for updates. It does not delete old files or perform automatic rollback.
A failed write may leave a partial installation; inspect the output and backups
before retrying. Do not bypass signing/execution policy to run the installer.
