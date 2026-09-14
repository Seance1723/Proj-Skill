# 06 — Gap Analysis and Safeguard Rationale

## From a checklist to an evidence-first delivery loop

The workflow's useful spine is: orient → intake → research → necessity → plan →
implement → verify → log → refresh memory. Defects enter the loop whenever found;
fixes return to verification. Rigor scales with risk, not document count.

The v1.1.0 hardening addresses gaps in both the instructions and their mechanical
enforcement. Rules reduce avoidable mistakes but cannot guarantee truthful model
output or authenticate prose written by an agent.

| Gap | Failure mode | Safeguard / location |
|---|---|---|
| Memory written but never read | Cold starts lose project context | P0 orientation and scoped source revalidation |
| Empty bootstrap looks complete | Templates are mistaken for app knowledge | Actionable bootstrap task, no fictional history, unfinished-memory audit |
| No distinction between fact and inference | Plausible claims become project truth | VERIFIED / INFERRED / ASSUMED / UNKNOWN evidence contract |
| Missing source/version checks | Invented APIs, commands, dependencies, links | Inspect code, manifests, command definitions and version-matched primary docs |
| Negative searches overclaimed | "Not found" becomes "does not exist" | Report inspected scope and unresolved searches |
| Retrieved content treated as authority | Untrusted instructions redirect the task | Host precedence and untrusted-content boundary |
| No proportionality | Process is abandoned on small changes | Lightweight T0/T1; read-only work stays read-only |
| Arbitrary dependency thresholds | Guessed LOC counts or unsafe custom security code | Maintenance/safety justification and existing package policies |
| Research has no endpoint | Time/context spent without a decision | Source ceilings, saturation, bounded experiments |
| Research/rejections are forgotten | Same over-engineering returns every session | Source-backed decisions and explicit revisit triggers |
| Tasks are just an unordered list | Prerequisites/cycles and priorities are missed | Dependencies, readiness gate, owner, priority, milestone when needed |
| Approval is implied | Agent expands risk without consent | T2/T3 named scope/action approval; reapproval for material changes |
| Scope grows during a fix | One-file task becomes an unreviewable rewrite | Scope fence, declared amendments, separate unrelated tasks |
| Happy path shipped without protection | Security/data-integrity work deferred | Essential negative cases belong in the first shippable slice |
| "Verification" heading is enough | Empty or placeholder evidence passes audit | Required context, result/exit code, coverage limits, status |
| Any task mention counts as completion | Follow-up text falsely supports DONE | Primary Task linkage to a valid VERIFIED change |
| No distinction between working and released | Local tests are reported as deployment | Separate verification status and delivery state; release evidence gate |
| Tests weakened to pass | Confidence increases while protection decreases | Never hide failures, weaken tests, or bypass security/signing policy |
| Baseline failures assumed | New breakages called pre-existing | Reproduce baseline or mark failure origin UNKNOWN |
| Mandatory commits create invented SHAs | Unauthorized commits or fictional Git links | Real SHA or explicit UNCOMMITTED/NOT_APPLICABLE reason |
| Recovery discards work | Reset/revert destroys another person's edits | Preserve tree, record attempts, ask before destructive recovery |
| Three-strikes has no useful handoff | Repeated blind fixes across sessions | Hypothesis/attempt/evidence/ruled-out/next-check record |
| Bugs require premature certainty | Root cause fabricated to fill a field | UNKNOWN while investigating; evidence required for FIXED |
| IDs/archives lose integrity | Duplicate IDs and dangling references | Audit live and archived definitions; preserve task entries |
| Stale owner claim implies takeover | Concurrent agents overwrite active work | Coordinator and explicit transfer; owner fields are not locks |
| Ledger secret checks echo values | Safety audit becomes a leak | Location-only diagnostics; synthetic data and redaction |
| Installers delete target directories | Local skill customizations disappear | Full preflight, ownership hashes, conflicts, retained backups, no directory deletion |
| Shell arguments evaluated as code | Quoted paths/names break or execute unexpectedly | Argument arrays and shared Python backend; no eval |
| Dry-run is not real | "Preview" creates files or initializes ledgers | Preflight-only path including initialization; regression coverage |
| Multiple global copies drift | Different tools silently load different rules | Devin-only default; compatibility/global installation explicitly requested |
| Adapter instructions lag behind skill | Lightweight hosts follow old unsafe rules | Shared fallback contract and consistency tests |

## What the audit can and cannot establish

The checker finds structural contradictions, incomplete required fields,
placeholder completion evidence, bad statuses, absent ownership/approval shape,
dependency problems, invalid timestamps, duplicate/dangling IDs, stale memory,
size limits, and probable secrets. It ignores fenced examples as actual records.

It cannot prove a command ran, a source supports a claim, an approval came from
the owner, a SHA exists, tests cover every requirement, or deployment is healthy.
These need independent review and direct observation. A fabricated but correctly
formatted record can still pass. Do not present the checker as hallucination-proof.

## Deliberately not added

- No mandatory issue-tracker service, database, orchestration framework, or model API.
- No new Python dependency; the audit/install/test tools use the standard library.
- No estimates, velocity claims, or percentage progress invented from a task count.
- No automatic deployment, rollback, credential rotation, history rewrite, or agent spawning.
- No mandatory global installation or compatibility configuration in every tool.
- No retrospective invention of missing evidence to make legacy ledgers pass.

Process changes should satisfy the same necessity gate as app changes. Prefer
fewer meaningful gates that are followed over many ceremonial records that drift.
