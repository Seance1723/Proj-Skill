# 06 — Gap Analysis: from seven steps to the loop

The original instruction set was sound in spine: analyse → research → judge
necessity → plan → implement → log → test → log bugs → keep memory. What follows
is what was missing, what breaks when it is missing, and where the fix lives.
Read this when you are tempted to drop a phase.

## Mapping

| Original | Becomes |
|---|---|
| 1. Analyse and sequence the ask | P1 Intake + tiering |
| 2. Research the web, compare to existing modules | P2 Research (inward **and** outward) |
| 3. Judge necessity, avoid over-engineering, update tasks | P3 Necessity gate + P4 Plan |
| 4. Implement, then log with timestamp | P5 Implement + P8 Log |
| 5. Test, log bugs, fix, log changes | P6 Verify + P7 Defects |
| 6. Create MEMORY.md, repeat for every change | P0 Orient + P9 Memory |
| 7. Keep all files well-maintained and readable | Ledger schemas + rotation + audit |

## The gaps

### G1 — Nothing said to *read* the files
The seven steps describe writing four documents and never describe reading them.
The stated goal — another agent picks up the state — only happens if session
start is itself a step. **Fix: P0 Orient**, with a fixed read order and a
five-line restatement.

### G2 — MEMORY.md created last, and only once
"Once these all are done create a MEMORY.md" makes memory a terminal artefact.
Memory that is written after the work is memory nobody used during the work.
**Fix:** `MEMORY.md` is bootstrapped first (P0), refreshed every loop (P9), and
capped so it stays readable.

### G3 — No brownfield bootstrap
Real repos have history before the workflow arrives. Starting from empty
templates throws that away. **Fix:** cold-repo path in P0 — reconstruct memory
from manifest, entry points, routes, schema, CI, README; file it as `T-0001`.

### G4 — No proportionality
Running full research and a necessity review on a typo is theatre, and theatre
gets abandoned within a week — after which nothing is logged at all. **Fix:**
T0–T3 tiers scaling rigor to blast radius (ref 01).

### G5 — No approval gate
"Once you have a concluded plan then update the tasks" leaves the agent as sole
judge of scope. **Fix:** T2/T3 require the plan block and an explicit go-ahead
before implementation.

### G6 — Research had no stopping rule and no storage
Unbounded research burns the session; unstored research is repeated next session.
**Fix:** per-tier source budgets, a saturation rule, and a mandatory
`DECISIONS.md` entry.

### G7 — "Don't over-engineer" was unenforceable
A value, not a test. **Fix:** the six-criterion necessity gate, including the
rule of three and an explicit dependency threshold — and, crucially, logged
**rejections**, so the same over-build is not re-proposed every session by an
agent with no memory of the last refusal.

### G8 — No IDs, so nothing cross-references
Four files with no keys cannot be linked, audited, or trusted. A change entry
that cannot name its task is an orphan. **Fix:** `T-/C-/B-/D-` IDs, referenced
everywhere, checkable by script.

### G9 — Unspecified timestamp format
"With timestamp" merges into gibberish once three tools with three locales write
to the same file. **Fix:** ISO-8601 with a fixed offset, everywhere.

### G10 — Unbounded growth
`CHANGES.md` at 4,000 lines is not context, it is a wall. The system quietly
stops working: the next agent skims. **Fix:** per-file caps, quarterly archive
rotation with stubs, and a hard cap on `MEMORY.md`.

### G11 — "Test it thoroughly" was undefined and unevidenced
Without named tiers and recorded evidence, "tested" degrades into "it ran once".
**Fix:** the test-tier table, the evidence format with a mandatory "Not covered"
line, and the rule that `DONE` requires evidence.

### G12 — No prohibition on green-by-weakening
The most common way an agent makes a suite pass is to make the suite ask less.
Nothing in the original forbade it. **Fix:** explicit non-negotiable; changing a
test is a logged decision, never a silent diff.

### G13 — No failure path
Every step assumed success. There was no route for "the fix does not work",
"tests cannot pass", "the design was wrong". Agents fill that vacuum by thrashing
or by declaring victory. **Fix:** three-strikes rule, `BLOCKED` status, revert to
last green, and a notes format that records what was ruled out.

### G14 — Bugs only entered through testing
Users report bugs too. **Fix:** a single intake door — `BUGS.md` first,
severity triage, then `TASKS.md`.

### G15 — Bug fixes without root cause or regression test
Symptom fixes reappear, and siblings of the same root cause stay hidden. **Fix:**
root cause and regression test are required fields; sibling search is a step.

### G16 — No scope fence during implementation
Nothing stopped a one-file fix becoming a forty-file diff. **Fix:** declared file
scope per task, amendments recorded, no drive-by refactors.

### G17 — No git linkage
A change log that cannot point at a commit cannot be verified. **Fix:** commit
SHA in every change entry; task ID in every commit message.

### G18 — No entry schemas
"Well maintained with a title and timestamp" produces five different formats from
five sessions. **Fix:** exact schemas per file (ref 04).

### G19 — Multi-agent concurrency unaddressed
Two agents, one `TASKS.md`, no ownership → overwritten work and duplicated
effort. **Fix:** claiming, stale-claim takeover with a note, append-only
sections, conflict guidance (ref 05).

### G20 — No secret or PII hygiene
Ledgers get committed and pasted into other agents' context. Nothing forbade
writing `.env` values into a bug repro. **Fix:** explicit prohibitions, redaction
convention, rotate-before-scrub for leaks.

### G21 — Documentation drift
Behaviour changes; README, `.env.example`, and API docs do not. The next setup
fails for reasons unrelated to the code. **Fix:** doc update in the definition of
done; doc drift is treated as a defect.

### G22 — No audit of the process itself
Nothing verified that the ledgers stayed consistent — done tasks with no change
entry, changes citing dead IDs, duplicate IDs, stale memory. **Fix:**
`ledger_check.py` at P9, cheap and mechanical.

### G23 — No handoff artefact
Even with perfect ledgers, the volatile state (branch, uncommitted work, the next
single action, what you just learned) had nowhere to go. **Fix:** the handoff
block, ending every session.

### G24 — No anti-fabrication rule
An agent under pressure reports steps it did not run. One fabricated line makes
the entire ledger untrustworthy, which is worse than having no ledger, because
the next agent trusts it. **Fix:** stated explicitly in P5, and evidence
requirements make it structurally harder.

## What was deliberately *not* added

The gate applies to the process too — this loop is itself a system that could be
over-engineered:

- No YAML/JSON ledgers. Markdown is what every agent reads natively.
- No required issue tracker sync. Optional, never load-bearing.
- No estimates or velocity metrics. They rot and nobody reads them.
- No approval gate on T0/T1. It would be ignored within a week, and a process
  that gets ignored takes the parts that mattered down with it.
- No mandatory CI enforcement. The loop must work in a solo repo on day one.
