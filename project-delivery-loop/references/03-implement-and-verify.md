# 03 — Implement, Verify, Recover

## Scope and baseline

Read the active task and neighboring code before editing. Inspect current Git
status/diff or equivalent source state; identify user-owned changes. Record the
baseline command and observed result before fixing a defect. If reproduction is
unavailable, keep the cause unconfirmed and state what access/data is needed.

Touch only the declared scope. Record small file amendments before editing;
material contract, data, cost, security, or scope changes require reapproval.
Keep tests close to the changed behavior and preserve the repository's conventions.
Do not reformat unrelated files or add dependencies solely for convenience.

One active task per owner. Use a failing regression case before the fix when
possible, then rerun it after the fix. Never claim the before/after comparison
unless both states were actually tested. Use an isolated fixture/worktree only
when authorized; never check out over user edits to reproduce an older version.

## Verification matrix

Discover commands in actual manifests, CI, scripts, or project instructions.
Record exact working directory and environment. No assumed `npm test` or made-up
build commands. Evaluate each relevant row and mark irrelevant rows with a reason.

| Check | Applies when | Evidence expected |
|---|---|---|
| Content consistency | Instructions, schemas, docs, adapters | References resolve, examples match schema, no contradictory gates |
| Build/lint/type | The project supplies these checks and affected artifacts use them | Final-state command, exit code, observed diagnostics |
| Unit/regression | Logic changes and defect fixes | Failure on baseline where practical, pass after fix, meaningful assertions |
| Integration/contract | Routes, storage, external APIs, CLI contracts | Real affected seam in a safe environment; compatibility checked |
| Negative/security | Input, auth, permissions, data boundaries, retries | Malformed/missing input, unauthorized access, tenant isolation, failure branches |
| Full relevant suite | Before DONE for code changes | Repository-wide relevant suite; state exact excluded modules/blocked checks |
| UI/accessibility | User-facing controls or flows | Actual smoke steps; loading/empty/error states, keyboard/focus, applicable layouts |
| Reliability | Async work, webhooks, caches, concurrency | Duplicate/retry/timeout/cancellation and race handling where affected |
| Performance | Performance claim or changed hot path | Comparable baseline and final measurement, workload/environment specified |
| Data | Migration or destructive data change | Isolated representative data; up/down or forward recovery; backup restore evidence |
| Operations/release | Deployment is explicitly requested | Release/environment identity, approval, health signals, rollback/stop criteria |

A full-suite failure is not automatically caused by this change. Reproduce the
baseline before calling it pre-existing. If not possible, label its origin
UNKNOWN. Do not hide failures in counts or change tests/policies to pass.

No harness? Use repeatable manual checks and actual output, explain the limitation,
and track missing automation if justified. Required verification blocked by access,
authentication, signing policy, or unavailable services remains BLOCKED/NOT_RUN.
Do not disable security controls or mock away the required behavior to get green.

## Evidence format

In a CHANGES.md entry, use `Status: VERIFIED|PARTIAL|FAILED|NOT_RUN` and
`Delivery: NOT_DEPLOYED|DEPLOYED|NOT_APPLICABLE`. Example structure below is
illustrative, not evidence that these commands ran in the current project:

```text
- Status: VERIFIED
- Delivery: NOT_DEPLOYED
- Verification:
  - Context: repository root; Python 3.x; local test environment; base SHA plus working-tree edits; actual timestamp
  - `python -m unittest discover -s tests` -> PASS (exit 0; observed test count and summary)
  - Manual: exact inputs and user action -> PASS (specific observed output)
  - Not covered: production rollout; not requested and no production access used.
```

Each executed command includes outcome and exit code. Manual checks name observed
behavior, not "looks fine." Context should identify the state tested; changes
made after the run require rerunning affected checks. Retain sanitized log/artifact
paths when useful; do not invent artifacts or store secrets. Link each acceptance
criterion to its evidence in the task. `Not covered: none within the task's scope`
is acceptable only when supported by the acceptance/check mapping.

For an unavailable check, record `BLOCKED (reason, owner, next action)` or
`NOT_RUN (reason)`, set change status PARTIAL/NOT_RUN as appropriate, and do not
mark the task DONE. A dependency/permission failure is not an application pass.
The mechanical checker can validate shape, not authenticate command execution.

## Defect protocol

1. Log the symptom, input/environment, expected/actual result, and severity before
   fixing. An unconfirmed user report stays OPEN with the missing repro named.
2. Isolate the mechanism using targeted diagnostics. Redact outputs before saving.
3. Record the root cause only when evidence supports it; otherwise UNKNOWN.
4. Add a regression test or repeatable manual regression procedure where a harness
   genuinely does not exist. Record whether the baseline failure was observed.
5. Search the affected subsystem for the same root cause. Log unrelated fixes as
   separate tasks, without expanding this change silently.
6. Mark FIXED only with root cause, regression evidence, a change reference, and
   a real closure timestamp. WONTFIX/CANNOT_REPRODUCE require rationale and notes.

S1: data loss/security/outage; S2: core flow broken without workaround;
S3: workaround exists; S4: cosmetic/rare. Severity is impact, not task size.

## Blocked and recovery

Stop after three failed attempts on one defect, or earlier for a new hazard,
unapproved scope, uncertain architecture, or a test/policy conflict. Preserve the
tree. Write: attempt → hypothesis → command/evidence → result → what was ruled
out → next discriminating check. Set BLOCKED with the required owner action.

Do not automatically reset/revert/stash or delete work. Explain the exact restore
operation and scope, identify user changes and backups, and wait for permission.
Use a forward fix when a database rollback would lose valid new data. For T3,
restore planning and safe testing happen before execution, not after failure.

## Completion and release gates

DONE requires:

- Acceptance criteria demonstrated on the final changed state.
- Applicable checks run with evidence; no unresolved required check or introduced failure.
- No weakened tests/security policies; defects and remaining limitations recorded.
- Scope honored, docs/contracts updated where behavior changed, no secrets exposed.
- A structurally valid VERIFIED change linked through its primary Task field.
- Task dependencies DONE, required approval recorded, memory/handoff updated.

DONE does not require an unauthorized commit or deployment. Use a real SHA if
available, otherwise `UNCOMMITTED — <reason>`; append a correction later rather
than trying to embed a commit's own not-yet-existing SHA into itself. Follow the
host's commit rules and repository style, including task IDs where compatible.

DEPLOYED additionally requires authorized execution, environment/release identity,
actual deploy output and health evidence, and tested rollback/stop criteria.
Local tests, a successful build, or opening a preview do not prove production health.
