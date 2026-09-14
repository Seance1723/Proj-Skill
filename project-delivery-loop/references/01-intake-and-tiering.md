# 01 — Intake, Tiering and Sequencing

## Risk tiers

Choose by blast radius, uncertainty, sensitive data, and reversibility, not line
count. Take the higher tier when uncertain; explain why. A dependency patch is
not automatically trivial, and a UI can still affect permissions or payments.

| Tier | Typical scope | Gate and evidence |
|---|---|---|
| T0 — trivial | Copy/format changes with no behavior or policy impact | Brief necessity check; batch under one task ID; relevant content/build checks only |
| T1 — standard | Contained behavior change within an existing seam | Local research; explicit scope/acceptance; targeted tests plus relevant full suite; outward research only when useful |
| T2 — significant | New dependency/service, schema, integration, auth/permissions, public contract, cross-cutting workflow change | Written options/decision, explicit approval before implementation, integration and negative checks, rollback plan |
| T3 — hazardous | Production data operations, billing, credential rotation, teardown, sensitive-data exposure, hard-to-reverse actions | T2 plus action-specific owner approval, backup/restore validation, staged rollout or dry run, stop conditions |

Risk controls remain mandatory for T0/T1. Neither a low tier nor a broad request
permits deleting files, deploying, installing globally, or changing host policy.

## Outcome and decomposition

For each request record:

- **Goal/user:** what outcome improves and for whom; retain the user's terminology.
- **Requirement source:** the request, issue, contract, or observed bug.
- **Baseline:** current behavior and what evidence establishes it; UNKNOWN if not checked.
- **Acceptance:** observable inputs and outputs, including key failure cases.
- **Non-goals:** adjacent features/refactors deliberately excluded.
- **Priority:** HIGH, NORMAL, or LOW, with the reason; no invented deadlines.
- **Milestone:** only when the request genuinely spans multiple deliverables.

Prefer bounded vertical slices that can be tested independently. "Email login
with validation and authorization" is safer than "all schema, then all APIs,
then all UI." Do not defer security, data-integrity, or mandatory error handling
to a later "hardening" slice. Read-only functionality can precede writes when it
creates a useful, safe checkpoint.

## Sequencing and dependencies

1. Identify hard prerequisites using task IDs.
2. Front-load small experiments that resolve expensive design uncertainty.
3. Unblock the highest-value approved work; prioritize active safety incidents.
4. Apply reversible changes before irreversible operations, respecting rollout
   compatibility between old/new code and schema.

State each ordering reason. Dependencies form a DAG: unknown IDs and cycles must
be resolved before work starts. One IN_PROGRESS task per owner; multiple owners
are allowed only with explicit coordination and disjoint scope. BACKLOG is not
permission to implement. Do not silently change the current milestone.

## Ambiguities and readiness gate

Ask about design-changing ambiguity: data ownership, authorization, external
contracts, compatibility, scope, or destructive actions. Batch related questions.
For harmless details, state a reversible assumption and proceed.

Before PLANNED → IN_PROGRESS, confirm:

- The goal, acceptance checks, exact scope, and non-goals are understood.
- Dependencies are DONE; any changed dependency plan was explicitly recorded.
- Required tools/access and a safe test environment exist, or the task is split
  to isolate the part that can proceed honestly.
- Material unknowns are resolved, or an approved bounded experiment is the task.
- The baseline and rollback are known; user changes are identified and protected.
- T2/T3 approval names the scope/action, approver, timestamp, and evidence source.

Record `APPROVED by ... at ...: ...` only after actual approval. PENDING does not
count. Material changes in scope, risk, cost, contract, or data impact return to
the approval gate; minor file amendments need a note before editing.

## Plan block

```text
PLAN — <title>
Tier / reason: <T0–T3 and blast radius>
Goal / source: <user outcome and requirement reference>
Baseline:     <observed behavior, evidence, explicit unknowns>
Units:        <task IDs, priority, dependencies and ordering reasons>
Scope fence:  <implementation, test, documentation paths>
Non-goals:    <what is deliberately excluded>
Assumptions:  <defaults and how they will be checked>
Prior art:    <inspected existing seam and relevant version-matched source>
Acceptance:   <criterion -> exact proposed check; not a claimed result>
Risks:        <failure mode, detection, stop condition>
Rollback:     <reversible steps, required backup/restore evidence and approval>
Approval:     <PENDING for T2/T3 until the owner responds>
```

Keep T0/T1 plans short. Escalate an unforeseen destructive action even if the
larger plan was approved. Permission is specific, not transferable to new risk.
