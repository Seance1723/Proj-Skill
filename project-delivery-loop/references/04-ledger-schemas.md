# 04 — Ledger Schemas and Mechanical Audit

## Conventions

Use the existing project ledger location. Default: repository root; archives:
`docs/agent-archive/`. Actual timestamps use ISO-8601 with seconds and offset
(`+00:00` preferred; `Z` accepted). Record actual agent/human identity, not a
fabricated model version. IDs are `T-0001`, `C-0001`, `B-0001`, `D-0001`, unique
across live and archived entries. Never recycle or renumber them.

Tasks use `### T-nnnn — title`; other entries use `## X-nnnn — title`. Fields are
unindented `- Name: value`; continuation lines are indented. Field names are
case-sensitive. Code-fenced examples are not real records. Use one field of each
name per entry. Replace placeholders before treating a record as completed work.
The templates illustrate fields; initialization omits fictional changes/bugs/
decisions and creates only the planned memory-reconstruction task.

## MEMORY.md

A source-backed snapshot, capped at 400 lines, with:

- `_Last updated: <actual timestamp> by <author>_`.
- What the app/tool is, users, maturity, goal/milestone, actual current state.
- Runtime/topology and relevant versions, supported by inspected manifests.
- Exact discovered commands, working directory, prerequisites by NAME only,
  observed outcomes, last checked revision/date, and verification limitations.
- A map of actual paths, invariants/contracts, critical user flows, and applicable
  security/accessibility/performance/operational requirements.
- Material unknowns and assumptions, with state, source or missing check, and owner.
- Active/blocked task IDs, next action/owner, known gotchas and useful source links.

Do not invent deployment state, imply an unexecuted command passed, or turn an
old inference into a fact. Refresh changed facts and their sources; refresh the
review date only after a real review. UNKNOWN with a reason is preferable to
filler. Remove `Bootstrap: REQUIRED` only when reconstruction is actually complete.

## TASKS.md

Maintain Active, Queued, and Recently done sections. Preserve full completed task
entries or archive them manually with approval; do not discard definitions just
because a task ID appears in CHANGES.md. The rotation script does not rotate tasks.

Example structure (values must come from the current task):

```markdown
### T-0042 — Rate-limit verification
- Status:     IN_PROGRESS        <!-- BACKLOG|PLANNED|IN_PROGRESS|BLOCKED|IN_REVIEW|DONE|DROPPED -->
- Tier:       T2
- Owner:      <actual owner>      <!-- who has claimed it -->
- Priority:   HIGH
- Created:    <actual timestamp>
- Updated:    <actual timestamp>
- Depends:    T-0041
- Decision:   D-0009
- Ask:        <requirement and its source>
- Baseline:   <observed behavior and evidence>
- Assumptions:<explicit reversible defaults or none>
- Scope fence:<implementation, test, documentation paths>
- Out of scope:<excluded adjacent work>
- Acceptance: <each criterion mapped to proposed check, then actual change evidence>
- Approval:   APPROVED by <owner> at <timestamp>: <scope/action and approval source>
- Rollback:   <safe recovery and action-specific permission requirements>
- Notes:      <attempts, scope amendments, blocker, next action/owner>
```

Always required: Status, Tier, Created, Updated, Ask, Scope fence, Acceptance.
Started/review/done work requires Owner. Started T2/T3 additionally requires
Approval beginning APPROVED, Rollback, and a Decision reference. Dependencies
must be real task IDs or `—`, `-`, `NONE`; no cycles. Started dependencies must
be DONE. BLOCKED/DROPPED require useful Notes. The audit checks presence, not
whether the owner really approved or the rollback is safe; review that evidence.

Transitions: BACKLOG → PLANNED → IN_PROGRESS → IN_REVIEW → DONE. A task can go
BLOCKED when work cannot safely proceed; record the resume condition. DROPPED
requires a reason, and a decision link for a principled rejection. DONE can be
reopened when later evidence invalidates it; preserve prior history and explain.

## CHANGES.md

Append new entries at the top for actual work. Required fields: When, Author,
Task, Commit, What, Why, Files, Status, Delivery, Verification.

```text
## C-0031 — Rate limiting on verification
- When: <actual timestamp>
- Author: <actual author>
- Task: T-0042
- Commit: UNCOMMITTED — owner has not requested a commit
- What: <specific implementation>
- Why: <requirement/bug reference>
- Files: <actual changed paths>
- Status: VERIFIED
- Delivery: NOT_DEPLOYED
- Verification:
  - Context: <working directory, environment, revision/tree state, timestamp>
  - `<actual command>` -> PASS (exit 0; <observed results>)
  - Manual: <actual steps> -> PASS (<specific observed behavior>)
  - Not covered: <limits and follow-up; or none within the declared scope>
- Follow-ups: <IDs or none>
```

Status: VERIFIED, PARTIAL, FAILED, NOT_RUN. Delivery: NOT_DEPLOYED, DEPLOYED,
NOT_APPLICABLE. DEPLOYED requires `Deployment evidence` naming the actual approved
release/environment, execution output, and health checks. A non-deployable skill
or library can use NOT_APPLICABLE; that does not excuse missing code verification.

Commit is a real 7–40 character hexadecimal SHA, or `UNCOMMITTED — reason`, or
`NOT_APPLICABLE — reason` for a non-Git project. Never invent a hash. The audit
checks syntax, not Git history. Later commit linkage is an append-only correction
referencing the earlier C-ID; no self-referential not-yet-existing commit SHA.

VERIFIED requires observed PASS evidence and command exit 0; Context and Not
covered are required. Failed/blocked required checks mean PARTIAL/FAILED/NOT_RUN,
not DONE. Every DONE task must be a primary Task in a valid VERIFIED change.
IDs in Follow-ups or narrative do not complete a task. Corrections are new entries;
never edit evidence to disguise prior failure.

## BUGS.md

```markdown
## B-0012 — Verification accepts unlimited guesses
- Found:      <actual timestamp> by <author and report/observation source>
- Status:     FIXED          <!-- OPEN|CONFIRMED|IN_PROGRESS|FIXED|WONTFIX|CANNOT_REPRODUCE -->
- Severity:   S2             <!-- S1 data loss/security/outage · S2 core broken · S3 workaround · S4 cosmetic -->
- Repro:      <exact safe input, steps, environment/revision, observed rate>
- Expected:   <contract and source>
- Actual:     <observed output; state if report not yet reproduced>
- Root cause: <mechanism and evidence; UNKNOWN until confirmed>
- Fix:        C-0031 (T-0042)
- Regression: <test/procedure and actual baseline/final results>
- Siblings:   <other affected uses and task references, or inspected scope with none found>
- Notes:      <attempts, limitations, workaround, next owner action>
- Closed:     <actual closure timestamp>
```

Required: Found, Status, Severity, Repro, Expected, Actual. FIXED additionally
requires a confirmed Root cause, Regression, Fix change reference, and Closed.
WONTFIX/CANNOT_REPRODUCE require Notes. Unresolved bugs remain pinned during rotation.
Do not invent a root cause to satisfy the schema.

## DECISIONS.md

```markdown
## D-0009 — How to rate-limit verification
- When:     <actual timestamp> | Author: <actual author> | Task: T-0042
- Status:   ACCEPTED       <!-- ACCEPTED|REJECTED|REJECTED_FOR_NOW|SUPERSEDED_BY_D-00xx -->
- Question: <decision and requirement source>
- Options:  <evidence-based comparison including reuse/do nothing>
- Decision: <choice, rationale, and limitations>
- Gate:     <six necessity criteria>
- Assumptions / unknowns: <states, evidence and next checks>
- Revisit:  <specific changed condition>
- Sources:  <inspected file/symbol/revision or actually retrieved URL/version>
```

All example fields except Assumptions/unknowns are required. ACCEPTED is a design
ruling, not permission for an unrelated operation. Rejections are retained to
avoid re-proposing settled ideas; superseded decisions point at an existing D-ID.

## Audit capabilities and limits

Run `python <skill-dir>/scripts/ledger_check.py --root <repo> [--strict]`.
Exit 0: no errors (warnings may exist unless strict); exit 1: invalid ledger;
exit 2: invocation/setup/read error. It checks real primary task links, duplicate
IDs across archives, missing/placeholder required fields, statuses, ownership,
approval shape, dependency cycles/readiness, evidence shape, timestamps, size,
stale memory, dangling references, and probable secrets without echoing values.

It does not execute tests, authenticate claims/approvals, check semantic coverage,
resolve live Git SHAs, prove deployment health, or comprehensively detect secrets.
Fenced examples are ignored for records, but still inspected for secret-like data.
Do not weaken the checker to hide a valid defect. Migrate older records honestly;
mark unsupported completion partial and append corrections rather than inventing evidence.

## Rotation and archiving

| File | Threshold | Handling |
|---|---|---|
| MEMORY | 400 lines | Keep snapshot concise; retain source pointers |
| TASKS | 900 lines / about 20 recent completions | Preserve definitions; approved manual archiving, not deletion |
| CHANGES | 50 entries / 1500 lines | Rotate oldest entries |
| BUGS | 20 recent + all unresolved / 1200 lines | Rotate only resolved older entries |
| DECISIONS | 40 recent + active/rejected decisions / 1200 lines | Preserve active/rejected rulings; rotate superseded entries |

Preview with `python <skill-dir>/scripts/ledger_rotate.py --root <repo> --dry-run`.
Review the actual entries, ensure no concurrent writer, and obtain approval before
rewriting ledgers. Archives retain full entries in `<FILE>-<YYYY>-Q<n>.md`; live
files retain pointers. Read required archives during orientation, not the entire
history every session. Run the audit again after rotation.
