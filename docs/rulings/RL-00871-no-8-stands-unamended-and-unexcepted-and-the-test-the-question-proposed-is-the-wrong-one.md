---
id: RL-871
family: ruling
title: No. §8 stands, unamended and unexcepted — and the test the question proposed is the wrong one
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slice-parallelism-ruling.md
---

# WK-671 — may two Slices run at once? `delivery-process.md` §8 against the map's permission (2026-08-29)

**What this is.** The ruling on the general question the lead escalated: **may two children of
the same layer — concretely, two WK-671 Slices — be built concurrently?** `delivery-process.md` §8
bars it; the frozen WK-671 map permits it for one pair. The conflict has been unresolved long
enough to cost real time twice, and it is a process question rather than a lead preference,
which is why it came here.

**Numbering continues at 33.** Rulings 1–30 are catalogued in
[`RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md`](RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md),
which added 31 and 32.

**Mints no `FR-`/`NFR-`/`OQ-` id and no error code, and edits no file.** `delivery-process.md`
is the lead's to write (`CLAUDE.md` §15); this ruling decides what it should say and does not
say it. The recommended text is offered in §7 below for the lead to apply or not.

**Read against `origin/main` at `c79a39d`.**

---

## RL-871 — No. §8 stands, unamended and unexcepted — and the test the question proposed is the wrong one

**Ruled: two Slices of the same Work may not be built concurrently. §8 is not excepted for
WK-671, and it should not be amended yet.** The reasoning matters more than the answer, because
the question was framed against an interest §8 does not protect.

### 1. §8 protects resource contention, not replan churn

The lead's proposed test — *"whether the second slice's plan can be invalidated by the first"*
— tests plan stability. **§8 is not about plan stability.** It says so in its own words:
sequential processing of a layer's children is *"the same bound on **context/resource usage per
session** RFC-840 §7 intended."*

Traced to source rather than taken from the citation. The intent is stated verbatim in the
design proposal reproduced inside `.claude/rfcs/RFC-00840-a-layered-slice-based-workflow-project-phase-work-slice-gated-at-every-layer.md` at
`:322-327`:

> **## 7. Parallelism**
>
> **Not used at any layer in this version.** Every "process children" loop runs strictly one
> child at a time, at every layer including Slice. **This bounds context/resource usage per
> session.** This was deliberately chosen over a parallel-fan-out design that was considered
> and rejected — **revisit only if resource budget materially changes.**

And RFC-840's own §3 restates it in the note's voice: *"§7 removes parallelism everywhere, to
bound context and resource usage per session. That is sound for child processing."*

**The consequence for how this is argued.** Two slices can be perfectly plan-independent — as
Slice 4's Slice-1-only tasks are — and running them concurrently still breaches §8, because
plan-independence is not the interest at stake. **An exception argued on plan-independence
argues past the rule.** That is the correction the question needed, and it is why the pair-wise
test the lead proposed cannot settle it.

*(Citation note for the lead: §8's *"RFC-840 §7"* points at the **reproduced proposal's** §7,
not at RFC-840's own §7, which is about a lead-row disagreement between two notes. The
citation resolves only for a reader who already knows which numbering it means —
[`RFC-777`](../rfcs/RFC-00777-a-reference-that-resolves-only-in-the-writer-s-context.md)'s
shape. A one-line disambiguation is recommended in §7.)*

### 2. The rule names its own revision trigger, and it has not fired

*"Revisit only if resource budget materially changes."* It has not changed, and the evidence
runs the other way:

- **§8's own recorded incident.** An executor and an auditor each ran the full suite on the
  same PR; *"two suites at once drove load average past 11 and both read as stalled agents for
  twenty minutes"*, and §8 draws the lesson that *"the symptom of contention is slowness, which
  is indistinguishable from a hang."*
- `CLAUDE.md` §11 records the same hazard from the other side: a benchmark taken on this shared
  machine can read as a 2.3x regression that is not real.
- The machine is shared by the whole team and by other sessions concurrently. Nothing about the
  budget has improved since the rule was written; the rule was written *because* of what
  happened on it.

### 3. For WK-671 specifically, concurrency can silently falsify an exit criterion

This is the argument that decides the concrete instance, and it is stronger than "it would be
slow".

WK-671's slices carry **NFR measurements**, and the exit criteria depend on their numbers: Slice 1
Task 1.5's latency harness, NFR-493's ≥ 1 M risks/hour for Slice 3, and — precisely the task
the question proposes to run alongside Slice 2 —
[`../plans/PL-00850-wk-671-slice-4-trace-sampling-the-row-plus-blob-store-and-the-retention-floor.md`](../plans/PL-00850-wk-671-slice-4-trace-sampling-the-row-plus-blob-store-and-the-retention-floor.md)'s
**Task 4D, *"NFR-500 projection … a projection from the measured serialised size"***.
Slice 2's own Task 2.1 carries a sustained-load re-run.

**A measurement taken while another slice's suite or load test is running is not a
measurement.** `CLAUDE.md` §13 requires NFRs *measured, not asserted*; a contended measurement
is an asserted one wearing a number, and it fails in the direction that gets booked as a pass.
This is a correctness risk, not a throughput one, and it is the reason the answer for WK-671 would
be "no" even if the resource budget had improved.

### 4. And today the permission buys nothing

`ListAgents`, run at the time of this ruling, shows the team as lead, watcher, reporter,
auditor, scope-derivation and **one executor** (`w11-executor-tooling`). Two Slices cannot be
built at once by one builder. An earlier unblock buys no wall-clock without a second
independent executor, so the time this question has cost was spent on a permission that had
nothing to spend it on. **If the question returns, it returns first as "should there be a
second executor?" — which is the lead's, not this role's.**

### 5. §8's own mitigation is currently half-built, which is an independent reason not to relax it

§8 does not rely on prohibition alone. It requires *"announce an expensive verification to the
team when you start it, and check for one already in flight before starting"*, and it is
explicit that *"the announcement is the load-bearing half"* because *"coordination state must be
visible, not relayed pairwise."*

**The publisher of that state has been withdrawn.**
`/home/puzhenhao1989/w11-handover-2026-08-29/roster-state.md` is headed *"WITHDRAWN, do not read
as team state"* — its contents were false, produced by a script emitting a fixed roster with
only the timestamp substituted (register finding **F31**) — and `.claude/roles/watcher.md`'s
roster bullet is marked **UNIMPLEMENTED**. Until something publishes what is running, the
"check" half is unactionable, which §8 itself names as the form that let the finding recur
twice in an hour.

Relaxing the prohibition while its compensating control is unbuilt would remove the only half
that currently works.

### 6. The map does not authorise the instance, and does not outrank §8 in any case

[`../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md`](../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md):217 reads: *"Slices 3 and 4 may run in
either order, or in parallel in separate worktrees, once Slice 1 is clean."*

Two things follow:

- **It names Slices 3 and 4.** The question asks about Slice 4 alongside **Slice 2**, which that
  sentence does not cover. Even on its own terms the map does not permit the instance.
- **A work plan does not override the process document.** `CLAUDE.md` §15 makes
  `docs/process/delivery-process.md` the process; a filed plan is frozen at its date (§2) and
  governs *what* is built, not *how the team runs*. Where they conflict, **§8 governs and the
  map's sentence is inoperative.** The map is frozen and is not edited; this ruling is the
  record of which one binds.

Note also that "in separate worktrees" answers a different objection than §8 raises: worktrees
isolate the filesystem, not the machine. Two worktrees contend for exactly the same CPU.

### 7. Amend rather than except — but not yet, and here is the trigger

**Not an exception.** Granting one per pair would relitigate this at every pair, and — per §1 —
each relitigation would be argued on plan-independence, the wrong test. A rule excepted case by
case is a rule that has to be re-derived by whoever asks next, which is what has already cost
the time twice.

**An amendment, when the trigger fires.** The trigger is the proposal's own: *a material change
in resource budget*. When it fires, the amendment's condition should be stated in the
**resource** terms §8 actually protects, not in plan terms. Recommended shape, for the lead to
write or reject — `delivery-process.md` is the lead's file:

> Two children of a layer may be built concurrently only when all three hold: **(i)** two
> independent executors exist, so the concurrency buys wall-clock at all; **(ii)** neither
> child's in-flight work includes an NFR measurement or a benchmark, because a contended
> measurement is not a measurement (`CLAUDE.md` §13); and **(iii)** coordination state is
> actually published, so §8's "check for one already in flight" is actionable rather than
> nominal. Read-only evidence fan-out remains unrestricted regardless.

**(iii) is false today** (§5), and **(i) is false today** (§4), which is why the amendment is
described and not adopted.

**The lead is also recommended** to apply the one-line citation disambiguation from §1, so that
§8's stated rationale is traceable without knowing which document's §7 is meant.

### 8. What remains permitted, unchanged

§8's existing carve-out is untouched and is wider than it is often read: **unrestricted
read-only fan-out for evidence gathering within a layer.** So while Slice 2 is in flight, Slice
4's *planning*, its evidence sweeps, its scope derivation and its spec reading may all proceed
in parallel. What may not proceed is a second Slice's **build/test/gate** loop. The distinction
is between reading and running.

**The ruling is overridden** if a second independent executor is stood up and coordination
state is published, at which point §7's amendment is due rather than another exception — or if
a measurement shows this machine carries two concurrent gate runs without contention, which
would be the *"resource budget materially changes"* the proposal names.

---

## Verification

- **Tree:** `c79a39d`, `origin/main` re-fetched immediately before this was written.
- **§8 was read in full** at `docs/process/delivery-process.md:139-168`, not summarised from
  the escalation, and its rationale was traced to source rather than accepted from its own
  citation — which is how the citation's ambiguity (§1's note) was found.
- **The proposal's §7 was quoted from the reproduction inside RFC-840** (`:322-327`), the
  durable copy, because the original reached this project as a loose file outside the
  repository — the custody problem [`RFC-778`](../rfcs/RFC-00778-seven-deferred-items-with-no-durable-custody.md)
  records and that RFC-840 reproduces the wording to solve.
- **The team composition was derived live from `ListAgents`**, not from
  `roster-state.md`, which is withdrawn and whose own withdrawal notice instructs exactly that
  derivation. One executor at the time of writing; a later change to the roster changes §4's
  premise and is named in the override condition.
- **The map's sentence was read at its own line** rather than recalled, which is how the
  Slices-3-and-4 scoping — and therefore its silence on the actual question — was found.
- **Task 4D's measurement character** was read from Slice 4's own leaf plan sequencing and
  requirement tables, not inferred from the task name.
- `python3 scripts/audit-docs.py` — run before commit.
- Mints no id and registers no error code, so it owes no
  [`../open-questions.md`](../open-questions.md) mirror row and no
  [`../roadmap.md`](../roadmap.md) §10 gate row. It edits no governed file: the amendment in §7
  is a recommendation to the lead, and `delivery-process.md` is unchanged by this commit.
