---
id: PL-1520
family: plan
kind: leaf
title: WK-1178 slice — F35 remedy, what the trace records per node and NFR-490's trace overhead (F35, F55, FD-1246; FR-258, NFR-490, NFR-500): leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-08            # original date 2026-10-01, set at the draft; minted 2026-10-08
owner: planner
tree: 19155b505741317da6967362707f387b39bd2cef
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-862, RL-863, CR-1247, FD-1246, RL-1261, RL-1263, PL-1348, PL-1237, PL-1254, PL-1359, SL-1259, SL-1345, SL-1360, RL-1518, RL-1519, PL-1435, SL-1436]
---

# PL-1520 — WK-1178: the F35 remedy, leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker and
> broken-input proofs), `test-driven-development` (every test is seen red before the code
> that turns it green), `dev-commands` (the two-half gate, the slot wrapper and the NFR
> measurement rules) and `git-hygiene`. Read [`README.md`](README.md)'s five unchecked
> conventions before the first step. The executor is spawned from `.claude/roles/executor.md`.

## Goal

Make a scoring trace record, per node, only what that node read and wrote, so that asking for
a trace stops costing about five times an untraced score. Today the trace copies the whole
accumulated evaluation context into every node entry, twice.

This is the remedy for register finding **F35** ("NFR-490 measured failing"). The same lever
discharges **F55** (`TraceStep.consumed`/`.produced` carry the full context) and is the one
`CR-1247` Proposal 11 names for **NFR-500**. The same ruling decides **FD-1246** (the trace
omits the `input` and `output` steps).

**Architecture.** Two changes, in this order:
1. **What the trace records** (`pricing_core.rating.score._build_trace`): each `TraceStep`
   carries the values of the names the step reads and the names it declares it produces.
   This is the content question, DP-F35-1.
2. **What the engine is asked to carry** (`pricing_core.rating.runtime.to_wire`): today every
   node sets `passThrough: true`, so the engine copies the whole context into every node's
   trace entry. That copy is the cost. Trimming in `_build_trace` alone cannot remove it: the
   research note measured our own post-processing at 12–25 % of the added time
   (`docs/research/w11-task-1-5-nfr-rate-1-2.md:207-241`; the 12–25 % sentence is `:226`, the
   conclusion `:239`). This is the mechanism question,
   DP-F35-4, which a spike (S1) informs before it is ruled. **M3, a trim in `_build_trace`
   only, does NOT satisfy NFR-490** (the maintainer's change of 2026-10-01 to this plan).

The result must not change: R3 (`03` §1.3) and NFR-490's second limb.

**Tech Stack:** Python 3.12, `zen-engine` 0.53.0 (`uv.lock`), pytest, `scripts/bench-rating.py`,
`scripts/bench-trace-size.py`.

**Spec:** [`03-rating-engine.md`](../specs/03-rating-engine.md) §1.3 (R3), §3.5 (FR-246), §3.8
(FR-258, FR-259, FR-262), §4.5 (`Trace`), §4.10 (`ScoreComparison`), §9 (NFR-489, NFR-490,
NFR-500). Rulings and records: `docs/rulings/RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md`
(§6 and the Addendum); `docs/rulings/RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md`
§4; `docs/closures/CR-01247-plan-review-16-at-wk-672-s-close-the-permission-source-of-record-f35-s-owner-the-dedicated-host-and-p2-s-exit.md`
Proposals 3 and 11; `docs/findings/register.md` rows F35, F55 and F37;
`docs/findings/FD-01246-a-scoring-trace-omits-the-algorithm-s-input-and-output-steps-where-fr-258-says-every-step.md`.

## The maintainer's decision, quoted verbatim

From `~/gi-pricing-plan.local/channel/to-lead.md` (a local channel file, not in the repository).

**2026-10-01 08:58:26 BST — "F35 RE-OWNED to WK-1178 (my decision); the remedy is planned inside P2, not carried":**

> **Not "carry forward" again:** NFR-490 is a P2 requirement failing on main by roughly 18×.
> **WK-1178 gets a leaf plan for F35's remedy before code freeze (4 Nov), and its first
> decision point is the design question F35 names: what the trace records per node** (a
> minimal per-node entry against the full `passThrough` payload). The decision-maker rules it.

> Lane order: F35's remedy queues after the parity check and FD-1357's fix on WK-1178
> (serial); its plan can be written now in parallel.

**2026-10-01 09:00:44 BST — "F35: the split ACCEPTED (remedy to WK-1178, measurement stays with SL-1259); the gate discharged":**

> **The code check is accepted:** RL-862's off-path capture **LANDED** (score.py:310-319
> untraced serving; `write_pending_trace` traces.py:159 plus the `SCORE_TRACE_PRODUCE` job;
> trace_handlers.py:90 refuses a changed bundle; :98 re-scores with trace=True; the
> reproduction check at traces.py:198-272; 7 tests incl. test_score.py:996). **F35's gate is
> discharged.** The cost that remains is `to_wire(passThrough: True)`
> (`pricing_core/rating/runtime.py:344`), as RL-862 §6 foresaw. *These bodies were read, not
> run:* **the leaf plan's Task 0 runs those 7 tests at its base and records the result**, so
> the discharge rests on a run before the build.

> **The remedy → WK-1178:** a leaf plan before code freeze; first DP the per-node trace content
> (minimal entry against the `passThrough` payload), for a decision-maker. **The gate is
> discharged, so it can be planned and built without a prerequisite**, queued on WK-1178 after
> the parity check and FD-1357's fix.

> **The measurement stays with SL-1259** (WK-674 Slice 5, which has NFR-490 in its title).
> **Its close shows NFR-490 passing after WK-1178's fix, or states the residual with an
> owner.** Record in F35's row, and in SL-1259's next dispatch record, that SL-1259's NFR-490
> limb **depends on** WK-1178's F35 slice (a cross-Work dependency, named both ways).

And the earlier acceptance this plan also honours, `CR-1247` Proposal 3, verbatim:
"Accepted: (a). F35's remedy is a WK-1178 slice before WK-674 Slice 5, after the TraceStep
ruling." Proposal 11: "Accepted: NFR-500 is raised as an OQ with the recommendation (a). The
decision-maker rules it."

**What this plan takes from those lines.**
- **DP-F35-1 is the first decision point**, and the decision-maker rules it. This plan gives
  options and a recommendation and picks nothing.
- **Task 0 runs the 7 tests** at the build base and records the result.
- **The NFR-490 verdict is SL-1259's.** This slice measures NFR-490 red at its base and again
  after the change, as evidence that the remedy moved the cost. It does not book a verdict.
  SL-1259's NFR-490 limb depends on this slice.
- **Build order on WK-1178:** after `SL-1360` (the permission-parity check) and after
  `FD-1357`'s fix (activation needs 5 and 6).

## Delta, 2026-10-05 (after 17:39:08 BST, pre-mint): re-planned against the ordered chain (PL-1435); DP-F35-7 open

This plan is still an unmerged draft. This delta records one ruling and what it does to the
plan's `passThrough`-off. It deletes no text: each part it changes keeps its text and carries a
pointer back here.

**The ruling.** The maintainer's (by delegation) entry "2026-10-05 17:39:08 BST — DP-R1 (PL 9567
#1193 @dd254b6d): (i) the ordered chain, with TWO conditions; PL 9776 re-plans after it; NFR-498
auditor yes", item 1's first line and item 2, verbatim:

> 1. DP-R1: (i) ADOPTED. It is the only option that removes the merge rather than relying on it. (ii) is subsumed by (c), and (iii) rests on an unread zen merge order.

> 2. PL 9776 (#1051, unminted): (i) lands FIRST. PL 9776 re-plans its passThrough-off against the chain pre-mint, because it is an optimisation and (i) is a correctness root. Both plans name the dependency.

The ruling record is RL-1423 (#1195; Amendment N2 records DP-R1). The plan that
builds the chain is PL-1435 (#1193; slice SL-1436, WK-673).

**1. The dependency: PL-1435 / SL-1436 merges FIRST.** This slice consumes SL-1436's output:
the chain wire in `to_wire` and the context pass-through in `_model_call_handler`. So the two
have a plan dependency under RL-1445 (b) and never run at once. **Activation need 10** is added
below the others:

```bash
S=<the squash SHA of SL-1436 on main, named in the dispatch record>; git merge-base --is-ancestor "$S" "$M" && echo MET
```

Expected: `MET`. SL-1436 and PL-1435 were working ids (9568, 9567) before their mint, so the lead names
the squash SHA rather than grepping for an id. Task 1's base measurement and Spike S1 run at or after that commit, because
the base they measure is the chain.

**2. What this plan turns off today, and where.** The write set (§"Write set", the `runtime.py`
row), DP-F35-4's (M1) and Task 4 Step 3 say the same thing:
- `"passThrough": False` in `_expression_node`, `_decision_table_node` and `_constraint_node`;
- `to_wire` wires an edge from the producer of each name a step references (`inputNode` for a
  raw input), so a node can have several incoming edges;
- every interior node whose output a later node does not overwrite is wired to `outputNode`,
  constraint and `model_call` nodes always, and `inputNode` is wired to `outputNode` too.

**3. The same thing, restated for the chain.** After SL-1436, the serving graph is one path:
`inputNode` → the first interior step → … → the last → `outputNode` (or `__exact_reads` →
`outputNode`), over `_dependency_order`. Every node has exactly one incoming edge, and every
node, `model_call` included, passes on the whole context it received. On that graph:
- **`passThrough` cannot be turned off on the serving path.** On one path, a node's output is
  the next node's only input. A node with `passThrough` off outputs only its own expressions,
  so every step after it loses every name produced before it. The first later step that reads
  an earlier name then fails. This is a property of the wire, not something a test needs to show.
- **M1 as written brings back what DP-R1 (i) removed.** Its reference edges give interior
  nodes a fan-in. Its `outputNode` wiring gives the sink a fan-in again: every node that is
  not overwritten, plus `inputNode`. Where two of those edges carry the same name, the result
  depends on how zen merges a fan-in. That is the basis the ruling rejected for (iii). So
  Spike S1 step 2's way out ("If the topologically later writer wins in both, M1 may wire
  every interior node to `outputNode`") can no longer justify a wire. Step 2 may still record
  the merge-order fact.
- **M4's "today's graph for untraced calls" now means the chain.**

So `passThrough` off, if it lands at all, can only be on a **separate traced graph**. The serving
chain stays as SL-1436 leaves it. That is a design choice the specs leave open, so it is
**DP-F35-7**, below, **open and blocking**. This item STOPS here for the lead. Task 4 is not
rewritten until DP-F35-7 is ruled. If the ruling changes Task 4's acceptance, a superseding `PL-`
is filed, by §"Status"'s rule on rulings that differ from a recommendation.

**4. NFR-490's measurement premise, re-checked under the chain.** Reasoned from the code at
`4d3be141`. **It is unmeasured.**
- **The instrument's structure** is `scripts/bench-rating.py`
  `_algorithm_payload(with_gbm=True, n_expr=187)` (`:197`, `N_EXPR_STEPS` `:91`). On today's wire:
  `s_expense` (`table`) and `s_risk` (`model_call`) both start at `inputNode`, and both feed
  `s_v000`, which also reads `driver_age` from `inputNode`. Then 186 expression steps form a
  chain, `s_v001` … `s_v186`. Only `s_v186`'s name is unconsumed, so the sink has **no** fan-in
  in this structure (`runtime.py:494-499`).
- **On the chain:** `inputNode` → `s_expense` → `s_risk` → `s_v000` → … → `s_v186` → sink.
  Three things change. `s_risk`'s input also holds `expense_factor`. `s_risk`'s output holds the
  whole context, not one key (`runtime.py:581` today; SL-1436's Task 2b Step 2). And `s_v000`
  receives one edge, not three. The entry count is the same, and each node still copies the
  whole context into its trace entry (P1). Only the `model_call` entry grows, by about one
  context, out of about 190 entries.
- **So the overhead case still holds.** By P4's bytes-to-cost ratio of about 1:1, the traced
  overhead on the chain is expected to stay where F35 measured it (+384 % to +723 %, by F35's row
  and the 08:57:07 entry), not to fall. The untraced figure U is expected to stay too: one extra
  dict copy per `model_call` call. **Both are unmeasured.** The remedy is still needed.
- **The prediction changes in one respect.** §"How NFR-490 is measured" says that M1 "also
  moves the untraced figure U … which moves the allowance itself". Under DP-F35-7 (a), the
  serving path is not changed, so U and the allowance (1.20 × U) do not move. Only T can fall.
- **Spike S1 and Task 1 read against the chain:** S1 step 3's "untraced on today's wire" means
  untraced on the chain; S1 step 4 compares the traced chain with the traced candidate; and Task 1's
  frozen base corpus is recorded at or after SL-1436's merge (activation need 10).

**5. What this delta changes in the plan:**
- **Activation needs:** need 10 (above).
- **Decision points:** DP-F35-7 appended to the table, open and blocking. DP-F35-4's row stays
  as written, and DP-F35-7 restates its options for the chain.
- **The write set's `runtime.py` row, DP-F35-4 (M1) and Task 4:** superseded by DP-F35-7
  until it is ruled. The text stays as written.
- **File contention:** a row for SL-1436 is appended (plan dependency, and `to_wire` and
  `_model_call_handler`).

## Delta 2, 2026-10-05 (after 17:51:03 BST, pre-mint): DP-F35-7 ruled (a), with two conditions; Task 4 rewritten

This plan is still an unmerged draft. This delta deletes no text: each part it changes keeps its
text and carries a pointer back here. Every code cite below was read at `origin/main`
`5fe56b87e55b0a29399f96f0af2e7c2e2ef9b72a`.

**The ruling.** The maintainer's (by delegation) entry "2026-10-05 17:51:03 BST — RL 9519 noted;
PL 9567 delta 4 accepted with one question on traces; DP-F35-7 = (a) with two conditions", item 3,
verbatim:

> 3. DP-F35-7: (a) ADOPTED, the traced-only wire admitted by a compile check, with trimming otherwise and R3 comparing every traced result. Two conditions:
>    - The SERVED price always comes from the serving chain, never from the traced wire. If R3 finds trace ≠ serve, the trace is refused or marked (an existing code, or spec first) and the served result stands. Its red is in the plan.
>    - NFR-490: the premise ("the bench is a near-chain; U does not move") is UNMEASURED, so it is MEASURED in the slice under the gate's own mode (OMP_NUM_THREADS=1 nice, inside a held slot, no concurrent heavy work), as CLAUDE.md 13 requires. It is not asserted in the plan.
>    Activation need 10 (SL 9568 merged plus DP-F35-7 ruled): the ruled half is discharged by this entry.

**1. DP-F35-7 is ruled (a).** A traced-only wire, admitted only where a compile check shows that
no name reaches `outputNode` by two edges; otherwise the trace is the chain's, trimmed in
`_build_trace` only (Task 3). R3 compares every traced result with the chain's. The DP-F35-7 row
in §"Decision points" carries a pointer here. DP-F35-4's row stays as written; DP-F35-7 restated
it for the chain and is now ruled, so DP-F35-4 is answered by DP-F35-7 (a) and is no longer an
activation need on its own (need 4, below).

**2. Activation need 10.** Its "DP-F35-7 ruled" half is **discharged** by the 17:51:03 entry
(the entry says so). Its "SL-1436 merged" half stays, with the same command. Need 4 (DP-F35-4
ruled and minted) is discharged with it: DP-F35-7 (a) is DP-F35-4 restated for the chain.

**3. Condition (i): the served price always comes from the chain. One mechanism, shared with
PL-1435.** PL-1435's Delta 5 (#1193, after 17:51:03 BST) answered the trace question at
`5fe56b87`:
- the off-path re-score compares its result with the stored served result:
  `backend/src/app/worker/trace_handlers.py:98-107` computes `summarise_result(result)`
  (`backend/src/app/platform/traces.py:143-156`, the four fields of `_SUMMARY_FIELDS`, `:64`:
  `outcome`, `decline_reasons`, `premium_ladder`, `outputs`), and `complete_pending_trace` sets
  `status = "complete" if reproduced_summary == row.served_summary else "mismatch"`
  (`traces.py:257`), keeping the body either way;
- the mark is the existing `ScoringTraceRow.status` value `mismatch`
  (`backend/src/app/db/models.py:2289-2296`);
- `GET /api/v1/traces` does not carry it today (`backend/src/app/api/traces.py` `TraceView`,
  `:100-116`), so PL-1435 Task 2d carries it, after **T-M1**, a spec text owed first by an RL.

**This slice uses the same comparator and the same mark.** No existing code in
`backend/src/app/errors.py` means "the trace did not reproduce" (the trace codes are
`TRACE_RETENTION_FLOOR` and `TRACE_NOT_PENDING`, `:375`, `:382`), and no `model-schema` field marks
a trace (`Trace`, `packages/model-schema/src/model_schema/scoring.py:187-201`, has none). So the
mark is `status` `mismatch`, read through T-M1's field. This slice does not add a second mark.

**Where the comparison runs is a question the ruling leaves open: DP-F35-8, below, open and
blocking Task 4.** It matters because of condition (i). A traced call that is served to its
caller must be served from the chain. Three paths ask for a trace at `5fe56b87`:
- `/score` with `options.trace` true, inline (`backend/src/app/api/score.py:374-375`);
- `/score/compare`, inline, both sides (`score.py:444-447`);
- the off-path producer, `score.trace_produce` (`trace_handlers.py:98`), which serves nothing:
  the served result was stored as `served_summary` when `/score` served the quote.

On an inline path, the served result and the traced wire's result are two evaluations. So a
traced call that also uses the traced wire costs at least U (the chain) plus the traced wire's
own time. Its overhead over U is then at least the traced wire's time over U, which is about
+100 % or more. NFR-490's budget is ≤ 20 %. On the off-path producer, the served result already
exists, so the traced wire is the only evaluation, and `traces.py:257` is the comparison.

**4. Condition (ii): NFR-490's premise is measured, Task 1B below.** "The bench is a near-chain;
U does not move" (this plan's Delta, item 4) is measured in the slice, in the gate's own mode:
`OMP_NUM_THREADS=1 nice`, inside a held gate slot, with no other heavy work running. The
method and the threshold are in Task 1B. Nothing in this plan asserts the premise.

**5. Task 4 is rewritten as Task 4R**, below, for DP-F35-7 (a) and DP-F35-8's recommendation.
Task 4's text stays, marked superseded. Under DP-F35-8 (a), Task 4R Steps 4 and 6 are rewritten
before dispatch, as Task 4R says.

**6. Is this a superseding `PL-`?** §"Status" says that a ruling which changes a Task's
**acceptance** is a superseding `PL-`. This plan is still an unminted draft, and the brief for
this delta (the lead's, on the 17:51:03 entry) is a pre-mint delta. So this is a dated pre-mint
delta: Acceptance 5 and 6 carry pointers to Task 4R, and Acceptance 13–16 are added. Whether
DP-F35-8's ruling then needs a superseding `PL-` is the lead's, by the same rule.

**7. What this delta changes in the plan:**
- **Activation needs:** need 4 and need 10's ruled half discharged; need 11 added (DP-F35-8
  ruled). T-M1's field lands in SL-1436 (PL-1435 Task 2d), so need 10 covers it.
- **Decision points:** DP-F35-7's row is marked ruled; DP-F35-8 is appended, open and blocking.
- **Tasks:** Task 1B added (condition (ii)); Task 4 superseded by Task 4R.
- **Acceptance:** items 5 and 6 point to Task 4R; items 13–16 added.
- **Write set:** a note under the table names Task 4R's paths. The `runtime.py` row and the
  Delta's note on it stay.
- **File contention:** A-1, A-2 and A-3 (`_model_call_handler`) are added in a note, and
  `trace_handlers.py` under DP-F35-8 (c).

### DP-F35-8 (added by Delta 2; open; blocking Task 4R)

| DP | Question | Options | Recommendation | Kind | Blocking? | Resolved by |
|---|---|---|---|---|---|---|
| **DP-F35-8** | **Where does R3's comparison run, so that the served price always comes from the chain (condition (i))?** | **(a) Inline in every traced call.** `score_one(trace=True)` scores the chain (the served result) and the traced wire (the trace), compares the two with `summarise_result`'s four fields, and returns the chain's result. On a difference the trace is marked or refused. Costs: two evaluations per traced call, so the inline traced overhead is at least the traced wire's time over U (about +100 % or more), and NFR-490 cannot pass on that path by construction; the comparator moves into `pricing-core` (the backend's `summarise_result` then calls it, so there is still one comparator); and the mark needs a field on `Trace` or `ScoringResult`, a spec text owed first (`03` §4.5), because no existing field or code fits. **(c) Only the off-path producer uses the traced wire.** `score.trace_produce` (`trace_handlers.py:98`) scores the traced wire where it is admitted (else the chain, trimmed); its result is compared with the stored `served_summary` at `traces.py:257` and marked `mismatch` there, unchanged; T-M1 carries the mark to the reader. `score_one(trace=True)`, which `/score` and `/score/compare` call inline, stays on the chain with Task 3's trim, so its result is the chain's by construction. Costs: the inline traced paths get no relief beyond the trim; `trace_handlers.py` gains one changed call (`backend/src/` joins the write set by one line); and NFR-490's instrument (`bench-rating.py`'s `trace=True` block, `:968-971`) measures the inline path, so the relief on the producer needs its own line in Task 6, and which line NFR-490's verdict reads is SL-1259's, by the decision-maker's reading. *(Excluded: the traced wire's result served on any path. Condition (i) forbids it.)* | **(c).** It meets condition (i) with no second evaluation, and it uses the one comparator and the one mark that already exist (`traces.py:257`; PL-1435's T-M1). Under (a), the traced wire would buy NFR-490 nothing on the inline path, because the comparison itself doubles the cost, so (a) costs more than DP-F35-7 (c) (trim only) on that path. The sampled stream that FR-259 persists and NFR-500 sizes is the producer's | decision point | **yes** (Task 4R) | decision-maker; **open** *(**Ruled (c)** 2026-10-05 by the maintainer (by delegation), 18:01:45 BST, item 2; see Delta 3.)* |

### Task 1B: NFR-490's premise, measured (condition (ii); added by Delta 2)

**What is measured.** The untraced figure U: the p99 of `scripts/bench-rating.py`'s "NFR-489
with GBM … trace=False" block (`:953` at `5fe56b87`), on the 200-step structure with one `exact`
GBM call. **NFR-490's own text** (`03:1331` at `5fe56b87`): "Tracing adds ≤ 20 % to scoring
latency and never changes the result (R3)." Its budget is relative to U: the allowance is
`BUDGET_TRACE_OVERHEAD` × U (`bench-rating.py:77`, 0.20). So a move in U moves the allowance.

**Three trees**, each a clean detached checkout, SHAs named in the ledger:
- **P (pre-chain):** the first parent of SL-1436's squash on `main`;
- **C (chain):** SL-1436's squash, this slice's base;
- **H:** this slice's HEAD after Task 4R.

**The near-chain half.** On C, record `to_wire`'s edge list for the bench structure
(`_algorithm_payload(with_gbm=True, n_expr=N_EXPR_STEPS)`, `bench-rating.py:197`): one path,
`input` → `s_expense` → `s_risk` → `s_v000` → … → `s_v186` → the sink, as the Delta's item 4
predicts. Record the same list on P. This measures structure, not time, and runs outside the
window.

**The mode, every timing run.** Inside a gate slot this measurement holds itself, taken through
the dev-commands slot wrapper (`.claude/skills/dev-commands/SKILL.md`), on the lead's grant, dated
in the dispatch record. No other gate, suite, benchmark or `migrate --verify` runs: the
`pgrep -af 'pytest|vitest|bench-|migrate --verify' | grep -v pgrep` line, `uptime`, `free -h` and
both `flock -n /tmp/slots/gate-{1,2} true; echo $?` reads at both ends of the window. Each run is
`OMP_NUM_THREADS=1 nice uv run python scripts/bench-rating.py`, default arguments, unmodified.

**Runs.** Five per tree, interleaved P, C, H, P, C, H, … (15 runs), in one window. The C and H
runs are the same runs as Task 6's base and HEAD timing runs where the windows coincide; the
ledger says which.

**The threshold.** NFR-490's text names no tolerance for U itself. It gives one figure, the 20 %
allowance over U. So, with s_U the sample standard deviation of U over C's five runs:
- **Holds:** |median U_P − median U_C| < s_U, and |median U_H − median U_C| < s_U.
- **Moved:** a difference ≥ s_U and < 0.20 × median U_C. The premise is false; the ledger
  records the numbers and the lead decides whether Task 6's reading stands. *(Delta 3: this band
  is the maintainer's (by delegation) call, not the lead's.)*
- **STOP for the maintainer (by delegation):** a difference ≥ 0.20 × median U_C. A U move of the
  whole allowance would by itself decide NFR-490's ratio.

The same table also records median T and the overhead per tree, as §"How NFR-490 is measured"
does. **This task books no NFR-490 verdict**; that stays SL-1259's.

### Task 4R: The traced-only wire, admitted by a compile check; served from the chain (DP-F35-7 (a); added by Delta 2)

**Written for DP-F35-8 (c)** (*ruled (c), Delta 3*). Under DP-F35-8 (a), Steps 4 and 6 are rewritten before dispatch
(the inline two-evaluation comparison, and a `03` §4.5 text for the mark), and the dispatch
record names each change.

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/runtime.py`: a new
  `_traced_wire_admitted(graph) -> bool`; a new `to_traced_wire(graph, payloads)`; the three node
  builders take a `pass_through: bool` argument (default `True`, so `to_wire` is unchanged);
  `_model_call_handler` (`:512`) gains the traced-wire mode (produced names only);
  `CompiledBundle` (`:625`) gains `traced_decision: Any | None = None`; `load_bundle` (`:646`)
  builds it when admitted. `to_wire` (`:412`), SL-1436's chain, is **not** edited.
- Modify: `packages/pricing-core/src/pricing_core/rating/score.py`: a new
  `reproduce_traced(compiled, ctx) -> ScoringResult`.
- Modify: `backend/src/app/worker/trace_handlers.py:98`: one call, `score_one(compiled, ctx,
  trace=True)` → `reproduce_traced(compiled, ctx)`.
- Test: `packages/pricing-core/tests/test_rating_trace_minimal.py` (append), and
  `backend/tests/test_score.py` (append one test).

- [ ] **Step 1: The admission check, red first.** Append:
  - `test_a_clamp_that_re_produces_a_declared_input_is_not_admitted`: an algorithm whose clamp
    consumes and re-produces a declared input (PL-1435 Task 2b's `_NL_CLAMP` shape, with `base`
    an input) gives `_traced_wire_admitted(...) is False`: `inputNode` and the clamp both reach
    `outputNode` with that name.
  - `test_the_scoring_fixture_is_admitted`: `_compiled()` gives `True`, and
    `compiled.traced_decision is not None`. If it gives `False`, STOP and report the name that
    reaches `outputNode` twice: either the count is wrong, or the fixture has a double writer
    (two `model_call` nodes both write `MODEL_CALL_ERROR_KEY`, `runtime.py:74`, so an algorithm
    with two of them is never admitted; record it).
  Red: `ImportError` on `_traced_wire_admitted`. The check counts, per name, every edge into
  `outputNode` that can carry it: `inputNode` for every context key (the declared inputs,
  `effective_date`, `purpose`); each wired interior node for its declared `produces`; each
  constraint for `<step_id>__violated`; each `model_call` for `MODEL_CALL_ERROR_KEY`. Admitted iff
  every count is at most 1.
- [ ] **Step 2: The traced wire.** `to_traced_wire` is Task 4's Step 3 sample (reference edges
  from `referenced_names`, `passThrough` off, the not-overwritten nodes and every constraint and
  `model_call` node wired to `outputNode`, `inputNode` wired to `outputNode`), built only for an
  admitted graph, over `_dependency_order` (SL-1436). The traced `model_call` node returns its
  produced names only (and the sentinel on failure), through the same single return expression
  SL-1436 introduced, with a mode argument. **Serialise with A-1, A-2 and A-3** on
  `_model_call_handler` (PL-1435 Delta 4 item 4).
- [ ] **Step 3: The payload bound, on the traced wire.** Task 4 Step 1's
  `test_engine_entry_input_is_bounded_by_its_references`, evaluating `compiled.traced_decision`
  in place of `compiled.decision`. Red before Step 2 (`traced_decision` is `None`: skip is not a
  pass; the test asserts it is set first).
- [ ] **Step 4: `reproduce_traced`** (DP-F35-8 (c)). It scores `compiled.traced_decision` with
  the engine trace on, when it is set, and otherwise calls `score_one(compiled, ctx, trace=True)`
  (the chain, trimmed). It builds the `ScoringResult` through `build_scoring_result`, as
  `score_one` does. It is never called by a serving route: `grep -rn reproduce_traced
  backend/src` prints `trace_handlers.py` only. Change `trace_handlers.py:98` to call it. Its
  result goes to `summarise_result` and `complete_pending_trace` unchanged, so `traces.py:257`
  is the comparison and `mismatch` is the mark.
- [ ] **Step 5: R3 over every traced result.** Task 4 Step 2's
  `test_the_remedy_changes_no_served_result` gains a second loop: over the frozen corpus, every
  admitted bundle's `reproduce_traced` result, with `trace` and `timing_ms` blanked, equals the
  corpus result. The first loop (the served `score_one` results) stays. Task 4 Step 5's
  broken-input proof runs against `to_traced_wire`: constraint nodes left off the `outputNode`
  wiring, the second loop fails naming a quote whose `outcome` moved; quote the line.
- [ ] **Step 6: Condition (i)'s reds.**
  - **The chain serves** (pricing-core, appended): `test_a_traced_call_is_served_from_the_chain`.
    It replaces `compiled.traced_decision` with a broken traced wire (Step 5's constraint-less
    wire) and asserts that `score_one(compiled, ctx, trace=True)`'s result, `trace` and
    `timing_ms` blanked, equals the untraced result on a context where a decline fires. It is a
    guard, so it is proved on broken input: make `score_one` evaluate `traced_decision` when it is
    set; expect FAIL naming `declined` → `quoted`; revert.
  - **A differing trace is marked, the served result stands** (backend, appended to
    `backend/tests/test_score.py`, mirroring its capture tests `test_a_sampled_trace_is_completed_by_the_off_path_job`
    and the planted-row form of PL-1435's withdrawn Step 1c):
    `test_a_traced_wire_that_does_not_reproduce_the_served_quote_is_marked_mismatch`. Serve a
    declining quote through `/score` at sample rate 1.0; keep the response body; inject a broken
    `traced_decision` (Step 5's wire) into the compiled bundle the handler resolves; run the
    `score.trace_produce` Job. Assert: the row's `status == "mismatch"`; the `/score` response
    body is unchanged (the served result stands); and `GET /api/v1/traces` lists the item with
    T-M1's field `mismatch` (PL-1435 Task 2d). Red before Step 4: the handler re-scores the chain,
    so the row is `complete` (`'complete' == 'mismatch'`). How the test injects the broken wire
    (a fixture over `BundleSlot`, or a monkeypatch of `_compiled_for` in `trace_handlers`) is the
    executor's, mirroring the module's shipped fixtures; record the form in the ledger.
- [ ] **Step 7: The admission count.** The ledger lists every algorithm of Task 6 Step 4, Spike
  S1's corpus and PL-1435 Task 2c's case set with admitted yes or no, and for each no, the name
  that reaches `outputNode` twice. An algorithm not admitted gets no NFR-490 relief.
- [ ] **Step 8: Run** `uv run pytest -q packages/pricing-core/tests/test_rating_trace_minimal.py
  packages/pricing-core/tests/test_rating_score.py packages/pricing-core/tests/test_rating_wire_order.py`,
  then the backend test alone, then `backend/tests/test_traces.py`, `test_traces_api.py` and
  Task 0 Step 1's 7 tests. Expected: green, no assert edited. A red in `test_rating_wire_order.py`
  or PL-1435 Task 2c's replay is a STOP: the chain moved.

```bash
git add packages/pricing-core/src/pricing_core/rating/runtime.py packages/pricing-core/src/pricing_core/rating/score.py backend/src/app/worker/trace_handlers.py packages/pricing-core/tests/test_rating_trace_minimal.py backend/tests/test_score.py
git commit -m "perf(rating): a traced-only wire where nothing merges at the sink; the chain still serves (WK-1178, F35, NFR-490)"
```

**Task 6 under Task 4R.** Task 6 Step 2's runs also time `reproduce_traced` on the 200-step
structure (a second traced line, labelled "producer path", beside the script's own `trace=True`
line, from a script pasted in the ledger with its sha256 prefix). Task 6 Step 3's stop rule reads
the producer line, because under DP-F35-8 (c) the inline `trace=True` line moves only by Task 3's
trim. Which of the two lines NFR-490's verdict reads is SL-1259's (the decision-maker's reading).

### Acceptance items added by Delta 2

13. **The admission check** (Task 4R Steps 1 and 7): both tests seen red first and green at HEAD;
    the ledger lists the admission count.
14. **Condition (i)** (Task 4R Step 6): `test_a_traced_call_is_served_from_the_chain` passes and
    failed once on its broken input; the backend test was red with `'complete' == 'mismatch'` and
    is green at HEAD, with the `/score` body unchanged and the route item marked `mismatch`.
15. **R3 over every traced result** (Task 4R Step 5): both loops pass; the broken traced wire
    fails the second loop; the line is quoted.
16. **Condition (ii)** (Task 1B): the ledger holds the 15-run table (P, C, H), the window record
    and the near-chain edge lists, and reads the premise as holds, moved or STOP by Task 1B's
    threshold.

### Write set and contention added by Delta 2

- `runtime.py`: Task 4R's functions above. `to_wire` is not edited (SL-1436's).
- `score.py`: `reproduce_traced`, new.
- `backend/src/app/worker/trace_handlers.py`: one call, under DP-F35-8 (c). Acceptance 12's
  "under `backend/src/` it names nothing" gains this line as an exception. No open PR touches
  the file (PL-1435 Delta 5 item 5's `gh pr list` filter, 95 open PRs, 2026-10-05).
- `backend/tests/test_score.py`: one appended test.
- **Contention:** A-1 (PL-1461), A-2 (PL-1464, #1178), A-3 (PL-1465), WK-1178:
  `_model_call_handler`, serialise (the same Work runs one slice at a time anyway). PL-1435 /
  SL-1436: plan dependency (need 10), and this slice consumes T-M1's field (Task 4R Step 6).

## Delta 3, 2026-10-05 (after 18:01:45 BST, pre-mint): DP-F35-8 ruled (c); Task 1B accepted

The maintainer's (by delegation) entry "2026-10-05 18:01:45 BST — Trace mismatch: a NEW small RL
for T-M1 AND an FD (it is live on main today); DP-F35-8 = (c); the U measurement accepted", items
2 and 3, verbatim:

> 2. DP-F35-8 = (c). Only the off-path producer (trace_handlers.py:98) uses the traced wire, via reproduce_traced; traces.py:257's existing comparison marks a mismatch. Inline traced calls (/score options.trace, /score/compare) stay on the chain with trim only. It is ONE mechanism shared with item 1, as required, and NFR-490 stays passable on the inline path. The second "producer path" timing line in Task 6 is accepted.
> 3. Condition (ii), PL 9776 Task 1B: ACCEPTED as written (U = p99 of bench-rating.py :953's trace=False GBM block; trees P, C and H; 5 interleaved runs each; the gate's mode inside a held slot with the wrapper on your grant; machine state at both ends; to_wire edges on P and C; the bands: holds below s_U, moved from s_U to 0.20·U_C (my call), STOP at or above 0.20·U_C against NFR-490 03:1331 and BUDGET_TRACE_OVERHEAD :77).
>    DP-F35-8 as a pre-mint delta: correct.

**What this delta changes in the plan:**
1. **DP-F35-8 is ruled (c).** Only the off-path producer (`trace_handlers.py:98`) uses the traced
   wire, through `reproduce_traced`; `traces.py:257`'s existing comparison marks a mismatch;
   inline traced calls (`/score` with `options.trace`, `/score/compare`) stay on the chain with
   Task 3's trim only. **Task 4R stands as written for (c).** Its note on DP-F35-8 (a) no longer
   applies. The DP-F35-8 row carries a pointer here.
2. **Activation need 11 is discharged** by this entry.
3. **Task 6's second, "producer path" timing line is accepted** (item 2).
4. **Task 1B is accepted as written**, bands included. **The "moved" band (s_U ≤ |ΔU| <
   0.20 × U_C) is the maintainer's (by delegation) call**, not the lead's (item 3: "my call").
   Task 1B's "the lead decides" for that band is superseded by this item; its text stays.
5. **The mark the reader sees** is PL-1435's Task 2d field, adopted by RL-1434 (a new
   RL, per item 1 of the same entry) and discharging FD-1433. Task 4R Step 6's
   backend test reads that field. Where Delta 2 says "T-M1", read "T-M1 as RL-1434 adopts it".

## Status

`draft`. It was filed with **five blocking decision points** (§"Decision points"); four are decided, see the amendment of 2026-10-05 below. It turns `active` only
when every activation need below is met, each shown by its command at a named `origin/main`
SHA in the dispatch record.

Filed under **working id 9776**, allocated by the lead (the only allocator); minted as
**PL-1520** in batch B4, 2026-10-08.

**Amended pre-merge, 2026-10-01, on the maintainer's five changes relayed by the lead:** DP-F35-5
moves to the decision-maker (blocking, verbatim text on NFR-490's row); M3 is stated not to
satisfy NFR-490; Spike S1's corpus is the real seeded algorithms (superseded by the correction below), with declines and errors,
compared byte for byte; DP-F35-1 waits on the auditor's FR-246 sweep; DP-F35-3 cites OQ-1373.
**Amended again pre-merge, 2026-10-01,** on the audit of `2ca7ce84` (M2, M3, L1–L8, adopted
by the lead) and the maintainer's corpus correction: S1 runs on every multi-step algorithm
existing when it runs and does not wait for G2 or `FD-1357`'s fix; S1 step 6 checks new
edges and cycles; `CompiledBundle.references` is defaulted. Then the auditor's delta audit of
`5a999fc1` (D1–D4): activation need 2 checks each DP separately and the P5 sweep FD by id;
S1 counts a clamp-fired class; P5 is corrected to the auditor's sweep. And FD-1374 (the P5
finding): DP-F35-1 cites it as its evidence record; DP-F35-1 (ii) rules FR-246's scope and
whether `consumes` is mandatory; Task 1A enforces it red first and fixes the four fixtures.
Then the maintainer's ruling on Task 1A: it implements DP-F35-1 as ruled; DP-F35-1 gains
(iii-a) the error code and (iii-b) a pinned bundle's fate; the FR-246 amendment and the
corrected example land, verbatim, in Task 1A's commit. And the example's range corrected to
`03:252-274` (five under-declaring steps at `:254-271`, and `s_out`'s unresolved consume),
which the ruled example must clear on both checks. And the delta audit's F4 (a compile-time
refusal only, with a release note) and F5 (the 12 backend files in Task 1A Step 7, in a gate
slot), the corrected example's raw names (P5a), and the maintainer's two `03` example tests.
Then the maintainer's widening: the ruled example is a complete valid algorithm, and it must
pass `model_validate` in full, then compile (stub payloads), then the declared-reads check.
Then the scoped re-check of `56460dd7` (F-1 to F-5 and the import merge).

**Amended 2026-10-05 before mint** (planner-amend-2, on the lead's brief of 2026-10-05 and the
triage it adopted; every item re-verified at `origin/main` `ef5dc6e7`): **DP-F35-1 (with
(i)–(iv), (iii-a), (iii-b)), DP-F35-2 and DP-F35-3 are decided by RL-1519, and DP-F35-5 by
RL-1518** (working ids 9771 and 9770, PR #1060, minted with this plan in batch B4), each as this plan recommended; the
§"Decision points" table's last column names the resolver. They stay activation need 2's (as written then)
until minted. DP-F35-4 (behind Spike S1) and DP-F35-6 (default (a)) stay open, so two
decision points remain, one blocking. Working ids minted since are re-pointed: FD 9773 →
`FD-1374` and OQ 9774 → `OQ-1373` (both #1077, 2026-10-03); a dated record above that
quotes the working id keeps it as written. `03` line cites are re-anchored by id or heading
to `ef5dc6e7` (§4.1's example is unchanged in content, +7 lines; §4.5's `s_minprem` entry
+24; NFR-489/490 +140), and `score.py` cites by symbol (`_build_trace`,
`_check_purpose_mount`, `_check_model_call_sentinel`; `backend/src/app/api/score.py`'s `score`,
`score_compare`, `_maybe_sample_trace`). Every other code and test cite stays a reading at
`tree:` `19155b50`, as §"Premises" says; `tree:` and `created:` change at the mint. OQ 9777
was since minted as OQ-1453 (#1230, 2026-10-06).

**SL.** WK-1178 is standing maintenance. The lead mints its slices at triage
([`document-ids.md`](../process/document-ids.md) §1.9). The proposed row text is in
§"Proposed SL row". This PR does not add it.

**Rulings that differ from a recommendation.** Tasks 2–6 below are written for the
recommended answers. Where a ruling differs:
- if it changes only a Task's **method**, the dispatch record names each difference, and the
  ruling wins;
- if it changes a Task's **acceptance**, a superseding `PL-` is filed instead of an activation
  (the rule `PL-1359` applied to `PL-1279`).

### Activation needs, in order

Run them from any checkout after `git fetch -q origin`. The SHA recorded is
`M=$(git rev-parse origin/main)`. **A need with no pasted output in the dispatch record is
unmet.** The lead's GO check starts here, before anything else.

1. **F35's re-own and OQ-1453 are on `main`** (PR #1048):
   ```bash
   git show "$M":docs/findings/register.md | grep -c 'measurement SL-1259'
   ```
   Expected: `1` or more. `0` means F35's row still names the closed WK-671 as owner:
   **unmet**.
2. **DP-F35-1, DP-F35-2, DP-F35-3 and DP-F35-5 are ruled and minted** (the decision-maker's
   `TraceStep` ruling, `CR-1247` Proposals 3 and 11, and the NFR-490 statistic):
   ```bash
   for dp in DP-F35-1 DP-F35-2 DP-F35-3 DP-F35-5; do printf '%s: ' "$dp"; git grep -lw -e "$dp" "$M" -- docs/rulings/ | sed 's/^[^:]*://' | tr '\n' ' '; echo; done
   ```
   Expected: four lines, each naming at least one path. One ruling may answer several DPs
   (the same path on several lines) or each its own (DP-F35-5, an NFR-490 interpretation,
   is likely separate). Each path's 5-digit id (`basename <path> | cut -c4-8`) is below
   `09000`. A line with no path, or only a `09xxx` working-id draft, is **unmet**. Then:
   ```bash
   git show "$M":docs/specs/03-rating-engine.md | grep -E '^\| \*\*FR-258\*\*' | grep -cE '(Clarified|Amended) 2026-1[0-2]'
   git show "$M":docs/open-questions.md | grep -c 'sampled-trace schema'
   git show "$M":docs/specs/03-rating-engine.md | grep -E '^\| \*\*NFR-490\*\*' | grep -cE '(Clarified|Amended) 2026-1[0-2]'
   P5FD='FD-1374'  # the P5 sweep's finding (filed as working id 9773, minted 2026-10-03, #1077)
   git grep -l --all-match -w -e 'DP-F35-1' -e "$P5FD" "$M" -- docs/rulings/
   git grep -l --all-match -w -e 'DP-F35-1' -e 'FR-246' -e 's_minprem' "$M" -- docs/rulings/
   ```
   Expected: `1`, `1` or more (`OQ-1373`'s row), `1` (DP-F35-5's dated clarification on
   NFR-490's row, verbatim as ruled), and at least one path: the DP-F35-1 ruling cites the P5
   sweep's governed record, **FD-1374**, by its minted id (DP-F35-1's precondition), and rules
   FR-246's step-type scope and whether `consumes` is mandatory. `P5FD` is set (amended
   2026-10-05 before mint: `FD-1374` is on `main`); if the command prints nothing, the need is
   **unmet**. The last prints at least one path: the DP-F35-1 ruling carries FR-246's
   amendment and the corrected §4.1 example verbatim, and rules (iii-a) and (iii-b); Task 1A
   applies that text to `03` in its own commit, so `03` itself is not checked here. The
   example's steps block is `03:259-281`. **Five evaluating steps** at `03:261-278` read names
   and declare no `consumes`: `s_area`'s `key_expr` (`:261-264`), `s_rp`'s `feature_map`
   (`:265`), `s_expense`'s `key_expr` (`:269`), `s_office`'s expression (`:272-274`) and
   `s_minprem`'s condition and clamp bound (`:275-278`). **And `s_out` (`:279-281`) consumes
   `payable_premium_pre_round`, which no step produces**, so the example also fails the
   existing graph invariant (`RATING_GRAPH_UNRESOLVED_REF`, `rating.py:419`), besides P5a's
   other defects. **The ruled §4.1 example must pass `RatingAlgorithm.model_validate` in full, then compile
   (`compile_bundle`), then the new declared-reads check** (the maintainer's widening of
   2026-10-01, superseding "passes both the existing invariant and the new check"), shown by
   Task 1A's two example tests, which extract it verbatim from `03`. The
   first two hold under DP-F35-1 (iii) (a) and DP-F35-3's recommended
   placement: the dated `03` text lands in the ruling's own commit. If the ruling instead
   assigns the `03` text to this slice, the first prints `0`, and the write set gains `03`
   §3.8 and §4.5; the dispatch record says so.
3. **Spike S1 is filed** (an `RS-` of `kind: spike`, by an executor, §"Spike S1"):
   ```bash
   git grep -l --all-match -e '^kind: spike' -e 'DP-F35-4' "$M" -- docs/research/
   ```
   Expected: at least one path whose 5-digit id is below `09000`. (`'Spike S1'` alone would
   also match `docs/research/track-a-findings.md`, an unrelated 2026-08-14 spike.)
4. **DP-F35-4 is ruled and minted** on S1's evidence:
   ```bash
   git grep -l -e 'DP-F35-4' "$M" -- docs/rulings/
   ```
   Expected: one path whose 5-digit id is below `09000`. **Where the ruling's wire rule and
   Task 4's sample differ, the ruling wins**, and the dispatch record names each difference.
   *(Discharged 2026-10-05 by Delta 2: DP-F35-7 (a), ruled by the maintainer (by delegation) at
   17:51:03 BST, is DP-F35-4 restated for the chain.)*
5. **`SL-1360` has merged** (the permission-parity check, `PL-1359`; first on WK-1178 by the
   maintainer's lane order):
   ```bash
   S=$(git log -n1 --format=%H -E --grep='^(test|feat|fix)\([^)]*\): SL-1360 ' "$M"); echo "squash=${S:-NONE}"; test -n "$S" && git merge-base --is-ancestor "$S" "$M" && echo MET
   ```
   Expected: `squash=<a 40-hex SHA>` and then `MET`. The `docs(plans,roadmap): activate …`
   commit does not match the `test|feat|fix` prefix, by design.
6. **`FD-1357`'s fix has merged** (second on WK-1178):
   ```bash
   S=$(git log -n1 --format=%H -E --grep='^(feat|fix)\([^)]*\): .*FD-1357' "$M"); echo "squash=${S:-NONE}"; test -n "$S" && git merge-base --is-ancestor "$S" "$M" && echo MET
   ```
   Expected: `squash=<a 40-hex SHA>` and `MET`. If the fix's PR title names only its `SL-`,
   the lead names that squash SHA in the dispatch record and runs
   `git merge-base --is-ancestor <sha> "$M" && echo MET` on it instead.
7. **`SL-1345` has merged** (file contention, §"File contention": `runtime.py`'s
   `_constraint_node` and `to_wire`, `score.py`, `03` §4.5):
   ```bash
   S=$(git log -n1 --format=%H -E --grep='^(feat|fix)\([^)]*\): SL-1345 ' "$M"); echo "squash=${S:-NONE}"; test -n "$S" && git merge-base --is-ancestor "$S" "$M" && echo MET
   ```
   Expected: `squash=<a 40-hex SHA>` and `MET`.
8. **This plan and its slice row are minted on `main`:**
   ```bash
   git grep -l -E '^title: WK-1178 slice — F35 remedy' "$M" -- docs/plans/
   git show "$M":docs/roadmap.md | grep -E '^#### SL-[0-9]+ — WK-1178 slice — F35 remedy'
   ```
   Expected: exactly one path whose 5-digit id is below `09000`, and exactly one heading whose
   `SL-` number is below `9000`. `09776` is the working-id draft: **unmet**.
9. **The status flip has merged, and the lead has given the go:**
   ```bash
   P=$(git grep -l -E '^title: WK-1178 slice — F35 remedy' "$M" -- docs/plans/ | sed 's/^[^:]*://'); git show "$M":"$P" | grep -m1 '^status:'
   git show "$M":docs/roadmap.md | awk '/^#### SL-[0-9]+ — WK-1178 slice — F35 remedy/{f=1} f && /^status:/{print; exit}'
   ```
   Expected: both lines begin `status: active`. Then the lead's go, dated, in the dispatch
   record, with the DP-resolver line.

10. **SL-1436 (PL-1435's slice, WK-673, the ordered chain) has merged** *(added 2026-10-05
    by the Delta after 17:39:08 BST; the maintainer's (by delegation) ruling, item 2)*:
    ```bash
    S=<the squash SHA of SL-1436 on main, named in the dispatch record>; git merge-base --is-ancestor "$S" "$M" && echo MET
    ```
    Expected: `MET`. Without it, **unmet**. And **DP-F35-7 is ruled and minted**:
    `git grep -l -e 'DP-F35-7' "$M" -- docs/rulings/` prints one path whose 5-digit id is below
    `09000`. *(Delta 2, 2026-10-05: the "DP-F35-7 ruled" half is **discharged** by the
    maintainer's (by delegation) 17:51:03 BST entry, item 3, which says so. The "SL-1436 merged"
    half stays.)*

11. **DP-F35-8 is ruled** *(added 2026-10-05 by Delta 2)*: where R3's comparison runs. Shown by
    the dated ruling line or record the lead names in the dispatch record. Without it, Task 4R
    does not start. *(Discharged 2026-10-05 by Delta 3: DP-F35-8 ruled (c) at 18:01:45 BST.)*

### Build-start conditions (Task 0, after activation; not activation needs)

- **A free lane under `RL-1263`:** at most two build slices at once, from different Works,
  each holding a gate slot, with no shared file outside the registry list. WK-1178's own
  slices run one at a time.
- **Two solo windows**, each granted by the lead and dated in the dispatch record: one for
  Task 1 (the base measured red) and one for Task 6 (base and HEAD interleaved). No other gate,
  suite, benchmark or `migrate --verify` runs during either (`delivery-process.md` §8, amended
  2026-09-29: "a measurement step runs alone").
- **The DB stack is up** for Task 0 Step 1 and the backend tests (`GIP_TEST_DATABASE_URL`).

## Acceptance Standard

Each item is checked by a command run from the repository root on the slice's merge tree,
unless it names the base.

1. **The 7 `RL-862` capture tests pass at the base and at HEAD** (Task 0 Step 1, Task 5
   Step 4). The command is in Task 0 Step 1. Expected: `7 passed` on each tree, both trees
   named. A setup `ERROR` is not a result.
2. **The trace-shape tests exist, were red before their code, and are green at HEAD.**
   `uv run pytest -q packages/pricing-core/tests/test_rating_trace_minimal.py` exits 0 and
   collects **7** tests (Task 2: 5; Task 4: 2). Five were seen red with the cause their task
   names: four of Task 2's at the base, and Task 4's payload-bound test. Two are guards that pass before and after their code, and are proved
   on broken input instead: Task 2's violation control, and Task 4's R3 differential
   (Acceptance 6). The ledger quotes each red's printed line. A red with another cause is a
   plan defect, not a pass.
2a. **FR-246 is enforced** (DP-F35-1 (ii); FD-1374): `uv run pytest -q
    packages/pricing-core/tests/test_rating_declared_reads.py` exits 0 and collects **6**
    tests: the two refusal tests and the extractor test, each seen red first (Task 1A Steps 2
    and 3); the control, proved on broken input (Task 1A Step 6); and the two `03` example
    tests, which extract §4.1's example verbatim from `03` and show it passes
    `RatingAlgorithm.model_validate` in full, then `compile_bundle` (stub payloads for its pins),
    then the declared-reads check: red against today's `03` on their named causes (Task 1A
    Step 3), green on the ruled complete example applied in the same commit (Step 8).
    **'Compiles' here means `compile_bundle` over stub payloads: the example is not hydrated
    by `load_bundle`, not scored, and its `sub_graphs` mount is not read (`_check_purpose_mount`'s docstring, `score.py:400-401` at `ef5dc6e7`);
    a dangling `mount_point` (e.g. `s_ncd`, not a step) also passes.** The 12 backend files of
    Step 7 pass; FD-1374's predicate prints
    0 undeclared reads over the merge tree (Task 1A Step 8).
3. **Each `TraceStep` carries exactly the step's reference set and declared produces**
   (DP-F35-1 (b)). On the `test_rating_score.py` fixture (`_compiled()`), `s_clamp`'s
   `consumed` is exactly `{"office_premium_minor", "min_premium_minor"}` (pre-clamp value),
   and `s_office`'s is exactly `{"risk_premium_minor", "expense_factor"}`.
4. **The `input` and `output` steps are traced** (DP-F35-2 (b)). Every `step_id` of the
   fixture's algorithm appears once in `trace.steps`.
5. *(Delta 2, 2026-10-05: read against Task 4R Step 3, on `compiled.traced_decision`.)* **The engine's per-node payload is bounded** (DP-F35-4 (M1)).
   `test_engine_entry_input_is_bounded_by_its_references` asserts, for every interior entry,
   that the entry's `input` keys are a subset of the step's reference set plus the request
   context's keys. It is red at the base (the `passThrough` context) and green at HEAD.
6. *(Delta 2, 2026-10-05: the differential gains Task 4R Step 5's second loop, and the broken-input proof runs on `to_traced_wire`.)* **The result did not change** (R3; NFR-490's second limb):
   - `packages/pricing-core/tests/test_rating_score.py::test_trace_true_returns_a_populated_trace_and_the_identical_premium`
     passes (traced equals untraced);
   - `test_the_remedy_changes_no_served_result` passes: over the frozen base corpus (Task 1
     Step 6), every `ScoringResult` at HEAD, with `trace` and `timing_ms` blanked, equals the
     base's as canonical JSON;
   - **broken-input proof:** with constraint nodes left off the `outputNode` wiring (Task 4
     Step 5), that test fails and names at least one quote whose `outcome` changed. The ledger
     quotes the failure line;
   - the 200-step structure: Task 6 Step 4's equality script prints `equal 1000 of 1000` at
     HEAD against the base.
7. **`score/compare` is re-proved on the trimmed trace** (`CR-1247` Proposal 3, fact 3):
   `uv run pytest -q backend/tests/test_score_compare.py` exits 0. The three existing diff
   tests carry Task 5's derived expectations, each seen red first with the cause Task 5 Step 1
   names; the own change is still exactly `s_expr`; and the new
   `test_a_step_whose_references_did_not_move_is_traced_and_not_listed` passes.
8. **NFR-490 is measured red at the base before any code, and again after** (Task 1, Task 6),
   each with the budget-margin statement of §"How NFR-490 is measured". The stop rule in Task 6
   Step 3 did not fire. **This is evidence for the remedy, not the NFR-490 verdict**, which is
   SL-1259's.
9. **NFR-500 is re-measured** under DP-F35-3's reading (`CR-1247` Proposal 11: "re-measured in
   the same WK-1178 slice"): `uv run python scripts/bench-trace-size.py` at the base and at
   HEAD, both outputs in the ledger, the projection read against 200 GB/year.
10. **The contract is regenerated, and only `TraceStep`'s description moved:**
    `uv run python scripts/generate-contracts.py --check` exits 0, and
    `git diff origin/main...HEAD -- docs/contracts/` changes only description text.
11. **The full two-half gate** of `CLAUDE.md` §11 exits 0 on the merge tree, under §"Gate
    evidence rules".
12. **The write set holds:** `git diff --stat origin/main...HEAD` names only the paths in
    §"Write set". Under `docs/specs/` it names only `03`, and `03`'s diff touches only
    FR-246's row, the §4.1 example's whole JSON block and the **Invariants** note after it
    (§4.1, `03:240-289` at `ef5dc6e7`) and, under (iii-a) (b), one owned-codes row,
    each byte-equal to the ruling's text (DP-F35-1 (iii)). Under `backend/src/` it names
    nothing, or under (iii-a) (b) only `backend/src/app/errors.py`, one `RATING_ERROR_CODES`
    entry. *(Amended 2026-10-05 before mint, on the lead's decision of 2026-10-05: the range
    was the example's steps, `03:252-274` as filed; RL-1519 (#1060) §(iii) replaces
    the whole fence (its T2) and the Invariants note (its T3), whose old text contradicts the
    corrected example, so this criterion, §"Write set" and Task 1A's Modify line name both.)*

## Global Constraints

- **Money is integer minor units, or `Decimal` in the rating path, never float** (R2;
  `CLAUDE.md` §7). This slice changes no arithmetic.
- **Tracing changes performance, never results** (R3, `03` §1.3). Acceptance 6.
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2).
  `TraceStep`'s shape does not change; its docstring does.
- **`pricing-core` stays importable standalone** (`CLAUDE.md` §2; `.importlinter`'s
  `core-has-no-infrastructure`). Nothing here imports outside `pricing_core` and
  `model_schema`.
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13). Acceptance 2, 5
  and 6.
- **NFRs are measured, not asserted** (`CLAUDE.md` §13). Acceptance 8 and 9.
- **Shared files** (`RL-1263` option (c)): two concurrent build slices may not both change the
  same existing function, class, spec section or policy table. `docs/INDEX.md` and
  `docs/contracts/schemas/generated/`, `docs/contracts/openapi/generated.json` are registry
  files, regenerated and never hand-merged.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice does | Marker |
|---|---|---|---|
| `03` §3.8 | FR-258 | The trace keeps every field FR-258 names; `consumed`/`produced` take DP-F35-1's reading; `input`/`output` steps are traced under DP-F35-2 (b) | `req("FR-258")` on the Task 2–4 tests |
| `03` §9 | NFR-490 | Both limbs. Latency: measured red at the base and after (evidence; the verdict is SL-1259's). Result: Acceptance 6 | `req("NFR-490")` on the R3 differential test |
| `03` §9 | NFR-500 | Re-measured under DP-F35-3's reading (`CR-1247` Proposal 11's placement) | none (a projection, in the ledger) |
| `03` §3.8 | FR-262 | `score/compare` re-proved on the trimmed trace | `req("FR-262")` on the appended compare test |
| `03` §3.8 | FR-259 | Read: the 7 capture tests run at base and HEAD; persisted traces shrink | none added |

**Not covered:** NFR-489 (SL-1259's; OQ-1453 asks whether it covers traced requests), FR-254
(batch takes no trace, RL-890), NFR-499 (unchanged: a trace still holds the quote inputs a
step reads, under the same access control), FR-246's enforcement (a proposed finding, §"Hand-off").

**Register rows this slice addresses:** F35 (remedy), F55 (the same lever), FD-1246 (DP-F35-2),
F37 (NFR-500's re-measure; the spec text lands with DP-F35-3's ruling). Closing each row is the
auditor's and the lead's, at the slice audit, never the executor's.

### Premises, read at `19155b50` (verified against the source, not the register's prose)

Each line names the file and line it was read at. Line numbers in older records have drifted;
these are current.

- **P1. The engine copies the whole context into each node.** `to_wire` sets
  `"passThrough": True` on every expression node (`runtime.py:162`), decision-table node
  (`:256`) and constraint node (`:322`), under "Step 3, rule 3" (`:152`); each consumed
  name's edge is added at `:412`. Its docstring (`:362-368`) states the consequence:
  "`passThrough` (rule 3) carries a node's entire received context forward … edges carry the
  whole merged dict".
- **P2. `_build_trace` passes the engine's dicts through.** `consumed=dict(entry.get("input") or {})`
  and `produced=dict(output)` (`score.py:726-727`, inside `_build_trace` at `:700-739`, at
  `19155b50`; at `ef5dc6e7` the same two lines are `:806-807`, inside `_build_trace` at
  `:781-822`). F55 cites `:686-687`, which is stale.
- **P3. The engine offers no slimmer trace.** `DecisionEvaluateOptions` has two keys,
  `max_depth` and `trace` (the installed `zen/__init__.pyi:5-7`, `zen-engine` 0.53.0, the
  version `uv.lock:2786-2787` pins). A smaller payload must come from the graph we hand it.
- **P4. Our own post-processing is the minor share.** 12–25 % of the added time, depending on
  the cut; about 88 % sits inside `async_evaluate()`, and engine-side cost tracks payload bytes
  at about 1:1 (`docs/research/w11-task-1-5-nfr-rate-1-2.md:192-241`; the 12–25 % sentence
  is `:226`, the conclusion "Not by trimming `_build_trace`" `:239`).
  `scripts/bench-rating.py`'s A/B/C decomposition (`_measure_abc`, `:415-470`) prints the split.
- **P5. Declared `consumes` under-declare what a step reads** (corrected 2026-10-01 to the
  auditor's sweep). **Four** constraint steps read a name their `consumes` does not list, all
  in tests: `packages/pricing-core/tests/test_rating_score.py:76` `s_clamp`
  (`min_premium_minor`), `:80` `s_decl_cap` (`sanity_cap_minor`), `:83` `s_decl_floor`
  (`sanity_floor_minor`), and `packages/model-schema/tests/test_rating_algorithm.py:65`
  `s_minprem` (`min_premium_minor`). **None** in the seed (`examples/`) or the bench
  structure. And `03`'s **own** §4.1 example (steps `03:259-281`) reads undeclared names in
  **five evaluating steps** at `03:261-278` (`s_area`, `s_rp`, `s_expense`, `s_office`,
  `s_minprem`), none declaring `consumes`; its `s_minprem` (`03:275`) reads
  `office_premium_minor` and `min_premium_minor`, which §4.5's trace example (`03:501`)
  records as `consumed`. Its `s_out` (`03:279-281`) also consumes `payable_premium_pre_round`,
  which no step produces, so the example fails FR-212's invariant as well. **The predicate:** for every non-`input`/`output` step, the names read by
  its `expr`, `condition`, `clamp_bounds` values and `key_expr` (string literals stripped;
  identifiers not followed by `(` and not preceded by `.` or `$`; minus `true`, `false`,
  `null`, `and`, `or`, `not`, `in`), plus its `feature_map` keys, minus its declared
  `consumes`; the same tokenizer as Task 1A's `referenced_names`. **The corpus:** every dict
  literal in a tracked `*.py` file with a string `step_id` and a non-`input`/`output` step
  `type`, and every step object in a tracked `*.json` file, at `19155b50`: 70 steps in 22
  files, 4 with an undeclared read, 12 with a field that is not a literal (not evaluated).
  Under `passThrough` these reads resolve silently. `03` FR-246 says an expression step
  "cannot reference anything outside their declared inputs"; nothing enforces it:
  `grep -rn "FR-246" packages/*/src` prints only the `now()` comment at
  `packages/pricing-core/src/pricing_core/rating/compile.py:49`. FR-246 names expression steps
  only, and all four under-declarers are constraint steps. P5's severity is the auditor's
  (held for the sweep's run on stored algorithms).
- **P5a. The §4.1 example at `19155b50`** (the JSON block at `03:233-278`, steps
  `03:252-274`; unchanged in content at `ef5dc6e7`, where they are `03:240-285` and
  `03:259-281`, and the cites below are given at `ef5dc6e7`), probed by `json.loads` of that block, `RatingAlgorithm.model_validate`
  repeated with each reported defect removed, and the P5 tokenizer over each step:
  - **`RatingAlgorithm` refuses it**, first on FR-214: declared outputs `premium_ladder`,
    `peril_risk_premium` and `decline_reasons` have no output step; then FR-212: `s_out`
    consumes `payable_premium_pre_round`, which no step produces; then FR-212 again:
    `office_premium_minor` is produced by `s_office` and `s_minprem` without a re-production
    chain (because `s_minprem` does not declare that it consumes it). Its sub-graph mount
    (`sub_graph:ncd-ladder@4` at `s_ncd`) was not reached.
  - **Raw names with no producer:** `postcode_outcode` (`s_area`'s `key_expr`) is in the
    `input_contract` (`03:247`) but no `input` step produces it; `distribution_channel`
    (`s_expense`), `commission_factor` and `profit_factor` (`s_office`) and
    `min_premium_minor` (`s_minprem`) are in neither the `input_contract` (`03:244-251`) nor
    any step's `produces`. Only `driver_age` has an `input` step (`s_input_age`, `03:259`).
  - **`s_area`'s `as_at: "effective_date"`** is a read too. FD-1374's predicate does not read
    `as_at` (a blind spot); this plan's `referenced_names` does (Task 1A Step 3).
  - So the decision-maker writes a complete valid algorithm (DP-F35-1 (ii)). **The corrected
    example adds**, at the decision-maker's choice of form: an `input` step
    for each raw name a step reads (`postcode_outcode`, `effective_date`, and the four above,
    each with an `input_contract` entry where missing), or a producing step for it; `consumes`
    on the five evaluating steps; a producer for `s_out`'s consume (or a different consume);
    and output steps for, or removal of, the three FR-214 outputs.
- **P6. The spec's own example is the minimal entry.** `03` §4.5's `s_minprem` step records
  `"consumed": {"office_premium_minor": 26_400, "min_premium_minor": 28_000}`: the premium and
  the bound it read, nothing else. `TraceStep`'s docstring
  (`packages/model-schema/src/model_schema/scoring.py:139-144`) records the opposite reading:
  "`03` does not specify a narrower shape than 'consumed values, produced value'".
- **P7. R3 says "full".** `03` §1.3: "**R3 — Every scoring call can produce a full Trace**,
  and a traced call and an untraced call return identical premiums." DP-F35-1 must say whether
  "full" means every step (FR-258) or every value.
- **P8. `own_change` reads `consumed` until WK-675 delivers `RL-1261`.** `03` §4.10
  (`:735`, `:737-738`). With the full context, a step downstream of an edit lists as `changed`
  even when the values it reads did not move. With the reference set, it does not list at all.
- **P9. `score/compare` traces both sides** (`backend/src/app/api/score.py`'s `score_compare`, `:443-447` at `ef5dc6e7`; `:359-362` at
  `19155b50`), so this
  is on a P2 deliverable's path (`CR-1247` Proposal 3, fact 2).
- **P10. The 7 capture tests exist at the cited lines:** `backend/tests/test_score.py:775`,
  `:996`, `:1047`; `backend/tests/test_traces.py:407`, `:415`, `:441`, `:469`, each marked
  `req("FR-259")`. Both citations of the serving path hold: `score.py:310-319` (the
  maintainer's) and `:379-441` (`_maybe_sample_trace`), at `19155b50`; at `ef5dc6e7` they are
  `score`'s `:373-384` and `_maybe_sample_trace` from `:464`.
- **P11. Changing `to_wire` does not change a bundle's hash.** `to_wire` runs inside
  `load_bundle` (`runtime.py:590`) over `bundle.graph`; `content_hash` is computed from the
  graph and pins (`compile.py`'s `bundle_hash`), so a pinned bundle re-scores under the new
  wire. Off-path reproduction (`trace_handlers.py:90-98`) therefore compares a result served by
  one wire with one reproduced by the other during a rolling deploy. Acceptance 6 is what
  makes that safe.

### Write set

| Path | This slice | Existing definitions edited |
|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/references.py` | **new**: `referenced_names(node)` over a `JdmGraph` node or a step dump (Task 1A) | — |
| `packages/pricing-core/src/pricing_core/rating/compile.py` | `_check_declared_reads` appended; one `ALGORITHM_CHECKS` entry; the import (Task 1A) | **yes**: the `ALGORITHM_CHECKS` tuple and the import block |
| `packages/pricing-core/tests/test_rating_declared_reads.py` | **new**: 6 tests, two of them reading `03` §4.1's example verbatim (Task 1A) | — |
| `packages/model-schema/tests/test_rating_algorithm.py` | its `s_minprem` (`:65`): `consumes` plus one `input` step (Task 1A) | **yes**: that fixture |
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | `to_wire` (reference edges, `outputNode` wiring), `_expression_node`, `_decision_table_node`, `_constraint_node` (`passThrough` off), `CompiledBundle` (a `references` field, defaulted), `load_bundle` (fills it), the module docstring's rule 3 | **yes**: those six |
| `packages/pricing-core/src/pricing_core/rating/score.py` | `_build_trace` (the reference-set trim; the `input`/`output` entries); `build_scoring_result` passes `bundle.references` | **yes**: those two |
| `packages/model-schema/src/model_schema/scoring.py` | `TraceStep`'s docstring only | **yes**: that docstring |
| `docs/contracts/schemas/generated/`, `docs/contracts/openapi/generated.json` | regenerated (the docstring is the schema `description`) | registry-exempt (`RL-1263:104-116`) |
| `packages/pricing-core/tests/test_rating_trace_minimal.py` | **new**: 7 tests | — |
| `packages/pricing-core/tests/data/trace_remedy_baseline.json` | **new**: the frozen base corpus (Task 1 Step 6) | — |
| `packages/pricing-core/tests/test_rating_score.py` | `_algorithm_payload` (three `input` steps; `consumes` on `s_clamp`, `s_decl_cap`, `s_decl_floor`; Task 1A); `test_trace_true_returns_a_populated_trace_and_the_identical_premium`: the `isdisjoint` assertion on `input`/`output` steps inverts (DP-F35-2 (b)) | **yes**: that fixture and that test |
| `backend/tests/test_score_compare.py` | the expectations of `test_compare_returns_both_traced_results_and_the_step_diff`, `test_exactly_one_step_is_the_own_change_at_the_http_layer` and `test_identical_refs_give_an_empty_diff` (Task 5's derivation); one appended test | **yes**: those three tests |
| `docs/specs/03-rating-engine.md` | FR-246's row (§3.5) and the §4.1 example's JSON block and Invariants note (§4.1, `03:240-289` at `ef5dc6e7`; RL-1519 §(iii) T2 and T3, amended 2026-10-05), verbatim from the DP-F35-1 ruling, in Task 1A's commit (the maintainer's executor carve-out); under (iii-a) (b), the new code's owned-codes row (§5.1) | **yes**: those rows and the example |
| `backend/src/app/errors.py` | under (iii-a) (b) only: the new code in `RATING_ERROR_CODES` | **yes**: that frozenset |
| `docs/ledgers/LG-<id>-….md` | new | none |
| `docs/INDEX.md` | regenerated | registry-exempt |

*(The Delta of 2026-10-05, after 17:39:08 BST: the `runtime.py` row above is superseded by DP-F35-7 until it is ruled. On SL-1436's chain, `passThrough` stays on in the serving graph.)*

**Read, not edited:** `backend/src/app/api/score.py`, `backend/src/app/worker/trace_handlers.py`,
`backend/src/app/platform/traces.py`, `pricing_core/rating/trace_diff.py`,
`03` apart from Task 1A's rows, the hand-authored `docs/contracts/schemas/scoring.schema.json` (its `TraceStep` carries
no description, `:72-86`), `scripts/bench-rating.py`, `scripts/bench-trace-size.py`.

### File contention

Read at `19155b50` against the merged plans and the open PRs. **Serialise** means the two do
not build concurrently, and the second merges `origin/main` first and re-runs its full gate.

| Other slice | Shared path or dependency | This slice | The other slice | Kind |
|---|---|---|---|---|
| **`SL-1345`** (lane A, WK-674 Slice 3L, `PL-1348`, `active`, PR #1045) | `pricing_core/rating/runtime.py` | `to_wire`, `_constraint_node`, the node builders | `to_wire`'s `string()` read; `_constraint_node`'s `__before`, `__min`, `__max` (`PL-1348:525-590`) | **serialise: this slice after `SL-1345` merges** (activation need 7). The same two functions |
| `SL-1345` | `pricing_core/rating/score.py` | `_build_trace`; `build_scoring_result`'s call to it | the ladder builder, `_build_outputs`, `build_scoring_result`'s raise, docstrings | same function (`build_scoring_result`): serialised by the row above |
| `SL-1345` | `model_schema/scoring.py` | `TraceStep`'s docstring | `LadderOperationKind`, `LadderOperation`, `LadderRung`, `Trace.ladder_check_version` | different classes; serialised anyway |
| `SL-1345` | `03` §4.5 | read only (the ruling writes `03`) | a note in §4.5 | none for this slice; the DP-F35-1 ruling's `03` edit is the decision-maker's, after `SL-1345` |
| `SL-1345` | `test_rating_score.py` | the `:530` test | the `:224` and `:262` tests | different functions |
| `SL-1345` | timing runs | Task 1, Task 6 (`bench-rating.py`) | its `bench-rating.py` run (`PL-1348` Acceptance 9) | **never the same window** |
| `SL-1345`; **`SL-1340`** (WK-1250 Slice 2) | `pricing_core/rating/compile.py` `ALGORITHM_CHECKS` and its import block | appends `_check_declared_reads` and one tuple entry (Task 1A) | `SL-1345` appends `_check_clamp_placement` (`PL-1348:528-590`); `SL-1340` edits `compile.py` | `SL-1345` merges first (need 7). Against `SL-1340`: serialise, or the append-only exception `PL-1348` used (both diffs append-only on the tuple, no existing line edited by both; the second to merge re-gates), shown in the dispatch record |
| `SL-1345`, `SL-1340`, WK-1250 later slices | `test_rating_score.py`'s `_algorithm_payload`; `test_rating_algorithm.py`'s fixture | Task 1A's fixture fix | tests that score through `_compiled()` | **a new step in a shared fixture**: every other open slice's tests scoring through it re-run on it; the second to merge re-gates |
| **`SL-1257`** (WK-674 Slice 3, environment half, `draft`) | `backend/src/app/api/score.py`, `observability/metrics.py` | read only | edits both (`PL-1348:584-586`) | no shared definition. Its dispatch record re-checks |
| **`SL-1259`** (WK-674 Slice 5, `draft`) | the NFR-490 measurement; `backend/src/app/api/score.py` (`/score` reads `live` once, `PL-1237` Task 5) | the base/HEAD evidence; reads `score.py` | the NFR-490 verdict | **dependency: SL-1259's NFR-490 limb comes after this slice** (the maintainer's 09:00:44 entry). Measurements never share a window. No shared file |
| **PL-1364** (WK-1178, `FD-1335` Part A, PR #1036, `draft`) | `backend/src/app/api/score.py` `responses=`; `backend/tests/test_score_compare.py` (one appended test); `generated.json` | reads `score.py`; edits three existing compare tests and appends one | edits the two decorators; appends one test | same Work, so **serial** by `RL-1263`. In the compare test file, no existing function is edited by both; the second to merge re-gates. `generated.json` is exempt: whichever lands second regenerates (once Part A's `$ref ScoringResult` lands, `TraceStep`'s description appears in more places) |
| **`SL-1360`** (WK-1178, `active`) | none | — | `tests/test_permission_parity.py` | order only (activation need 5) |
| **`FD-1357`'s fix** (WK-1178, not yet planned) | none (`rate_tables.py`, the seeding path) | — | — | order only (activation need 6) |
| **`SL-1340`** (WK-1250 Slice 2, `draft`) | `_build_trace` (inlined steps traced and attributable, FR-258's limb); possibly `TraceStep` | `_build_trace`, `TraceStep`'s docstring | its trace limb "starts only after" the `TraceStep` ruling (`PL-1254:171-177`) | **serialise.** Recommended order: this slice first, so `SL-1340` builds on the ruled content. The lead decides |
| **The `RL-1343` rule-4 slice** (WK-1178, not yet planned) | `score.py`, `model_schema/scoring.py`, `docs/contracts/` | `_build_trace`, `TraceStep`'s docstring | `outputs`' type (per PL-1364's contention section) | same Work: serial |
| **WK-675 S7b** (`PL-1286`, `draft`) | `trace_diff.py`, `score_compare`'s body (`RL-1261`) | read only | edits both | no shared definition. Behavioural: once `RL-1261` lands, `own_change` no longer reads `consumed`, so P8 stops mattering |
| **SL-1436** (WK-673, PL-1435, #1193; the ordered chain) *(added 2026-10-05 by the Delta after 17:39:08 BST)* | `runtime.py` `to_wire`, `_model_call_handler`, `_model_call_failure`, the docstring's wiring rules; **plan dependency**: this slice consumes the chain | `to_wire` and the node builders (DP-F35-7 decides how) | rewrites `to_wire` as one path; the `model_call` pass-through | **dependency: SL-1436 merges first** (activation need 10); RL-1445 (b) fails, so never at once |

## How NFR-490 is measured (red first at the base)

**The instrument** is `scripts/bench-rating.py`, unmodified, default arguments
(`uv run python scripts/bench-rating.py`). Its NFR-490 line is the p99 overhead of the
`trace=True` block over the `trace=False` block on the same 200-step structure with one
`exact` GBM call (`main`, `:959-973`), and its A/B/C block splits the added time into the
engine's share and ours (`:997-1028`). The budget is `BUDGET_TRACE_OVERHEAD` in that file, by
symbol.

**The statistic is DP-F35-5's ruling: p99, by RL-1518 (#1060), accepted by the maintainer 2026-10-01.** NFR-490 (`03:1331`) names none, so choosing one
interprets the spec, and the decision-maker rules it. This plan is written for **p99**,
the maintainer's lean, which holds only if NFR-489 states its scoring-latency budget at p99
(the decision-maker verifies; NFR-489's row, `03:1190` at `19155b50` and `03:1330` at
`ef5dc6e7`, reads "Real-time scoring p99 < 50 ms"). p99 is also the statistic the harness prints, F35 measured and `#1045`'s bench
line used. If the ruling names another statistic, the margin statement below uses it: a
method difference, named in the dispatch record.

**The latest figure at a base**, for orientation only (not this slice's measurement): the
maintainer's entry "2026-10-01 08:57:07 BST — #1045's budget line is complete" reads "NFR-490
≤ 20%; +384% and +556%; negative margins; run counts and window; traced p99 68.0 → 69.9 ms
against a stdev of about 5 ms" (solo window 08:35:36–08:40:11 BST, per F35's dated
observation in PR #1048). F35's own row records +497 % to +723 % across 5 of 5 runs.

**The budget-margin statement**, filled in for each tree, in each window:

| Field | Definition |
|---|---|
| Budget | traced p99 ≤ 1.20 × untraced p99 (`BUDGET_TRACE_OVERHEAD`) |
| Runs | **at least 5 per tree**, so the one-stdev watch rule rests on a usable stdev; each run is one full `bench-rating.py` invocation. Min and max are reported beside the median as well |
| Per run | untraced p99 U (the "NFR-489 with GBM … trace=False" block), traced p99 T (the "NFR-490 with GBM, trace=True" block), overhead O = the script's printed line, and the 1-minute load span the script prints for each block |
| Measured | median U, median T, median O; min and max O |
| Stdev | s = the sample standard deviation of T across the tree's runs (ms) |
| Margin | m = 1.20 × median U − median T (ms), and 20 % − median O (percentage points) |
| Window | start and end, BST, with `uptime`, `free -h`, both `flock -n` slot reads and the `pgrep` line at each end |
| Reading | m < 0: **over**. 0 ≤ m < s: **under, and a watch item** (the margin is inside one stdev). m ≥ s: **under** |

**The prediction, stated so it can be falsified:** F35's row extrapolates a minimal entry to
"roughly 1.6 ms against the 1.847 ms allowance". If that holds, the margin is about 0.25 ms,
well inside a 5 ms stdev, so **a pass on this box is expected to be a watch item at best**.
**And the 0.25 ms is an optimistic extrapolation of F35:** it scales cost to bytes with a zero
intercept, ignores the residual per-entry cost a trace keeps at any size, and ignores that M1
also moves the untraced figure U (smaller contexts on the serving path), which moves the
allowance itself.
That is why the verdict stays with SL-1259 on the dedicated host (`PL-1237` Task 5): a
shared-VM figure near a bound is diagnostic only.

## Decision points

DP-F35-1 is the maintainer's named first decision point. DP-F35-1, -2 and -3 are one ruling's
subject (`CR-1247` Proposal 3: "one ruling on F35, F55, the trace input/output finding and
Proposal 11's question"). DP-F35-4 waits on Spike S1. *(The Delta of 2026-10-05, after 17:39:08 BST: on the chain, DP-F35-4's options are restated as DP-F35-7, open and blocking.)*

| DP | Question | Options | Recommendation | Kind | Blocking? | Resolved by |
|---|---|---|---|---|---|---|
| **DP-F35-1** | **What does a `TraceStep` record per node?** (F35, F55; FR-258's "consumed values, produced value"; R3's "full Trace") | **(a)** Declared names: `consumed` = the values of the step's declared `consumes`; `produced` = its declared `produces` (F55's wording). **(b)** What the step reads: `consumed` = the values of every name the step references (declared `consumes` plus the names its `expr`, `condition`, `clamp_bounds`, `key_expr` or `feature_map` reads), as the step received them; `produced` = its declared `produces`. **(c)** The full accumulated context, as today. **(d)** (a) or (b) by default, and the full context only on an explicit caller option | **(b).** It is `03` §4.5's own example (P6). (a) silently drops a clamp bound or decline threshold the step used (P5), so a trace could not explain its own clamp. (c) leaves NFR-490 about 18× over and NFR-500 about 2.58× over. (d) turns `QuoteContextOptions.trace` from a bool into an enum, a contract change for a debugging aid no requirement names. Under (b), "full" in R3 reads as every step, which is FR-258's "every step" | decision point | **yes** | **Decided (b)** by RL-1519 (#1060, not yet minted). decision-maker (`RL-`). **Evidence record: FD-1374** (filed as working id 9773, PR #1053; the auditor's P5 sweep; MEDIUM, WK-1178, remedy via this plan). **Precondition (the maintainer, 2026-10-01): DP-F35-1 is not ruled before the auditor's sweep of undeclared reads (FR-246; P5) over every stored algorithm and seed is in the decision-maker's commission** |
| DP-F35-1 (i) | Does `produced` keep the engine's internal keys (`<step>__violated`; `SL-1345`'s `__before`, `__min`, `__max`)? | (a) no: declared `produces` only; the `violation` field already records a clamp or decline. (b) yes | **(a)** | decision point | yes (with DP-F35-1) | **Decided (a)** by RL-1519 (#1060, not yet minted). decision-maker |
| DP-F35-1 (ii) | **Refusal or ordering from reads; FR-246's step-type scope; whether `consumes` is mandatory** (FD-1374). Enforcement is **in this plan's scope** (the lead's instruction of 2026-10-01): Task 1A | **Mechanism:** (a) refuse an undeclared read at save time; (b) accept it and order and wire the graph from what each step reads. **Scope:** (a) every field a step evaluates, on every step type that has one: an `expression`'s `expr`, a `table`'s or `lookup`'s `key_expr`, a `model_call`'s `feature_map`, a `constraint`'s `condition` and `clamp_bounds` (`03`'s own §4.1 example under-declares in five evaluating steps, `03:261-278`, `s_area`'s `key_expr` among them); (b) `expression` only, as FR-246 is worded today. **Mandatory:** (a) yes: a step that reads a name declares it in `consumes`; (b) no: `consumes` stays advisory and only the trace uses the reference set. | **Mechanism (a), scope (a), mandatory (a).** (b) mechanism makes the declared graph a fiction the engine no longer follows, and a reviewer reading `consumes` would be misled. All four under-declarers in the code are constraint steps, and the spec's example adds `feature_map` and `key_expr` cases, so (b) scope would enforce nothing that exists. **The decision-maker writes a COMPLETE, VALID §4.1 algorithm (`03:259-281` and its `input_contract` and `outputs`):** an `input` step (and an `input_contract` entry) for every raw name a step reads, every declared output produced by an output step, `consumes` on every evaluating step, a producer for every consume; **all of P5a's defects fixed in one ruling** (accepted by the maintainer, 2026-10-01). It must pass **`RatingAlgorithm.model_validate` in full, then compile (`compile_bundle`, with stub payloads for its pinned refs, Task 1A), then the new declared-reads check** (the maintainer's widening, superseding "both the existing invariant and the new check"); (a) mandatory makes DP-F35-1's options (a) and (b) coincide for every algorithm that compiles; the code is (iii-a)'s question. **The undeclared reads also bear on M1 (DP-F35-4):** M1 wires edges from reference sets, so an undeclared read adds an edge the declared graph lacks, which can reorder evaluation or close a cycle that the engine refuses in `load_bundle` for a pinned bundle that hydrates today (P11: the content hash is unchanged). Task 1A's check stops new ones at save time; it does not reach a bundle already pinned: (iii-b) rules that, and Spike S1 step 6 lists those edges and cycles | decision point | yes (with DP-F35-1) | **Decided: mechanism (a), scope (a) with `as_at` named, mandatory (a)** by RL-1519 (#1060, not yet minted). decision-maker, with verbatim `03` text (FR-246 and the corrected §4.1 example, `03:259-281`) |
| DP-F35-1 (iii) | Who writes FR-258's dated clarification and the `TraceStep` reading into `03`? | (a) the ruling's own commit (the precedent `RL-1305` D4 set). (b) this slice | **(a).** It keeps `03` §3.8 and §4.5 out of this slice's write set (`SL-1345` also edits §4.5). **FR-246's amendment and the corrected §4.1 example are different:** they land in Task 1A's commit, beside the code that enforces them (the maintainer, 2026-10-01) | decision point | yes (with DP-F35-1) | **Decided (a)**, split T1–T5 Task 1A, T6–T9 the ruling's mint PR, T10 Task 3, by RL-1519 (#1060, not yet minted). decision-maker |
| DP-F35-1 (iii-a) | **The error code an undeclared read is refused with** | (a) reuse `RATING_GRAPH_UNRESOLVED_REF` (FR-212's "consumes undefined value"). (b) a **new** code (for example `RATING_STEP_UNDECLARED_READ`), with its row in `03`'s owned-codes table (§5.1) and its entry in `RATING_ERROR_CODES` (`backend/src/app/errors.py`) | **(b).** **Undeclared is not unresolved:** an FR-212 refusal means no step produces the name; here a producer exists and the step simply did not declare the read. One code for both would make a caller's fix ambiguous. Cost: `03` §5.1 and `errors.py` join the write set (Task 1A, same commit), and Acceptance 12's `backend/src/` exclusion admits that one registry line | decision point | yes (with DP-F35-1) | **Decided (b), `RATING_STEP_UNDECLARED_READ`, 422** by RL-1519 (#1060, not yet minted). decision-maker, with the code's verbatim `03` row |
| DP-F35-1 (iii-b) | **The fate of a stored or pinned bundle that fails the new check** | (a) refused at reload (`load_bundle` runs the check). (b) grandfathered: a bundle compiled before the check loads and scores as it did, and the check binds at save and compile only (the FR-4 pattern: a rule binds forward). (c) migrated: re-compiled with the reads added to `consumes`, which is a new bundle and a new hash, so a new Rating Version through approval | **(b).** (a) can take a live, approved Rating Version out of service on a code change, which R1 (`03` §1.3: a live version is immutable) forbids in spirit. (c) is a governed re-approval per bundle, not a code task. Under (b), M1 must still hydrate such a bundle: Spike S1 step 6 is the evidence, and **"0 stored rows in the local databases" does not settle other installs**, so the ruling states the behaviour, not the count | decision point | yes (with DP-F35-1; S1 step 6 reads against it) | **Decided (b)**: saved versions refused at next compile, compiled bundles grandfathered at reload, by RL-1519 (#1060, not yet minted). decision-maker |
| DP-F35-1 (iv) | Does `Trace` carry a marker of which reading a persisted trace holds? | (a) no marker: the shape is unchanged; a trace carries `bundle_hash` and its row a timestamp; no reader of persisted `consumed` exists yet (`05`'s monitors are a later phase). (b) an integer field on `Trace`, after `Trace.ladder_check_version`'s precedent (`SL-1345`) | **(a).** If `05`'s input-drift monitor (FR-307) later reads `consumed`, its spec states what it needs then (`CLAUDE.md` §0: a later phase is a spec change) | decision point | yes (with DP-F35-1) | **Decided (a)** by RL-1519 (#1060, not yet minted). decision-maker |
| **DP-F35-2** | **Are the `input` and `output` steps traced?** (FD-1246) | (a) FR-258 gains a dated clarification that they are not, and the code is unchanged. (b) the trace carries one entry per `input` step (`consumed` `{}`, `produced` its declared name and value, from the engine's `inputNode` entry) and per `output` step (`consumed` its declared name and value, from the `outputNode` entry), each with `elapsed_us` 0 because the engine evaluates them as one collapsed node | **(b).** FR-258 says "every step"; under DP-F35-1 (b) each such entry is a few bytes; and `SL-1340`'s inlined ports are then traceable without a second ruling. Cost: `score/compare`'s `unchanged` counts rise (Acceptance 7), and a test that pins today's omission inverts | decision point | **yes** | **Decided (b)**, `elapsed_us` 0, by RL-1519 (#1060, not yet minted). decision-maker (the same `RL-`) |
| **DP-F35-3** | **What does NFR-500's "sampled-trace schema" name?** (`CR-1247` Proposal 11; F37) | (a) the `Trace` contract after this slice's trim, measured uncompressed. (b) the persisted encoding with a named compression. (c) both: the trimmed `Trace`, persisted with a named compression, the budget stated for the persisted bytes | **(a)**, as `CR-1247` recommended and the maintainer accepted. Raised as **OQ-1373** (filed as working id 9774; NFR-500's sampled-trace schema; owner this plan), ruled in the same sitting | design unknown → `OQ-`, then `RL-` | **yes** (Acceptance 9 reads against it) | **Decided (a)** by RL-1519 (#1060, not yet minted), which closes `OQ-1373` (its T9). decision-maker |
| **DP-F35-4** | **How is the engine made to carry less?** (P1, P3, P4) | **(M1)** One graph: `passThrough` off on every node; an edge from the producer of each name a step references (the `inputNode` for a raw input); every node whose output a later node does not overwrite wired to `outputNode`; `inputNode` wired to `outputNode`. **(M2)** No engine trace: score untraced and rebuild each entry from the result; `elapsed_us` and `matched` (FR-258) are lost or recomputed in Python. **(M3)** Trim in `_build_trace` only. **(M4)** Two graphs: today's for untraced calls and M1's for traced ones; R3 then compares two graphs on every traced call | **M1, if S1 shows equality on the whole corpus and no mixed producer**; else **M4**, which leaves the serving path untouched. **M3 (trim only) does NOT satisfy NFR-490** (P4: our share is 12–25 %); it fixes F55 and NFR-500 only, and taking it means NFR-490 stays red with the residual owned by the maintainer's dated line. M2 loses two FR-258 fields | decision point (on S1's facts) | **yes** | decision-maker, after S1 |
| **DP-F35-5** | **Which statistic does NFR-490's "adds ≤ 20 %" name?** NFR-490 (`03:1331`) names none (`RL-862` Addendum: "NFR-490 names no statistic"), so choosing one interprets the spec | (a) p99. (b) the mean. (c) every quantile, as the harness's ratio ladder prints | **(a) p99, the maintainer's lean, IF NFR-489 (`03` §9's scoring-latency NFR) states its budget at p99**, which the decision-maker verifies (NFR-489's row, `03:1190` at `19155b50` and `03:1330` at `ef5dc6e7`, reads "Real-time scoring p99 < 50 ms"). One statistic for the two budgets on one path keeps them comparable | spec interpretation → decision point | **yes** (Tasks 1 and 6 read against it) | **Decided (a) p99** by RL-1518 (#1060, not yet minted); the maintainer's acceptance is dated in it (2026-10-01 10:30:00 BST). **decision-maker**, in the same session as DP-F35-1 to -3, with **verbatim text and placement**: a dated clarification on NFR-490's row (`03` §9) |
| DP-F35-6 | Does a passing NFR-490 trigger `RL-862`'s override ("if #416's audit shows traced cost can be brought inside NFR-490's ceiling — in which case always-capture becomes affordable and the simpler design returns")? | (a) no: the off-path design stays; any reversion is a new ruling. (b) yes, in this slice | default **(a)**: this slice touches no serving-path backend file (Acceptance 12; at most the `errors.py` registry entry under DP-F35-1 (iii-a) (b)) | scope | no: **default (a) applies throughout**; named in §"Hand-off" | decision-maker, if raised |
| **DP-F35-7** *(added 2026-10-05 by the Delta after 17:39:08 BST; DP-F35-4 restated for the chain)* | **On the ordered chain (PL-1435, DP-R1 (i)), how does a traced call carry less?** The serving chain needs `passThrough` on every node (the Delta, item 3), and M1 as written re-creates the fan-in DP-R1 (i) removed | **(a) Two graphs, the traced one admitted only where nothing merges.** Untraced serving stays on the chain, unchanged. A traced call scores on a second wire: `passThrough` off, reference edges, and the not-overwritten nodes wired to `outputNode`, as in Task 4 Step 3. That wire is built only when a compile-time check shows that **no name reaches `outputNode` by two edges**. The check counts `inputNode` as the writer of every context key, and counts each constraint's `<step>__violated` and the `model_call` error key. An algorithm that fails the check (for example, a clamp that re-produces a declared input) is traced on the chain with the `_build_trace` trim only, and the ledger counts those algorithms. R3 compares each traced result with the chain's. **(b) M2 on the chain:** no engine trace; each entry is rebuilt from the result, and FR-258's `elapsed_us` and `matched` are lost or recomputed in Python. **(c) M3 on the chain:** trim in `_build_trace` only; NFR-490 stays red, and the residual is owned by the maintainer's dated line. *(Excluded: the chain with `passThrough` off and each node re-emitting every earlier name as an expression. That is `passThrough` under another name, with the same payload.)* | **(a).** Every price stays on the chain, so the correctness root is not touched. The traced graph relies on no merge order, because no name arrives at the sink twice, and a union of disjoint dicts does not depend on order. Its costs: `load_bundle` builds two wires per bundle; the traced `model_call` node needs the handler to return only its produced names, which adds a mode to `_model_call_handler` (shared with A-1, A-2 and A-3, so serialise); and an algorithm that fails the check gets no NFR-490 relief. (b) loses two FR-258 fields. (c) does not remedy NFR-490 (P4) | decision point (on Spike S1's facts, re-read against the chain) | **yes** | decision-maker, after S1; **open** *(**Ruled (a)** 2026-10-05 by the maintainer (by delegation), 17:51:03 BST, item 3, with two conditions; see Delta 2. DP-F35-8 follows from condition (i).)* |

## Spike S1 — the fact DP-F35-4 needs (an `RS-` of `kind: spike`, before activation)

**Who and when.** An executor, before activation, as preparation. It measures **bytes and
equality, never time**, so it is not a measurement step under `RL-1263` item 3. Whether it may
run beside a build slice is the lead's call. It commits no code: its scripts go inline in the
`RS-`, each with its sha256 prefix.

**At the tree the spike names** (`origin/main` after `SL-1345` merges, if it has; the `RS-`
names the SHA either way):

1. **Reference sets.** For every algorithm in the corpus below, compute each interior step's
   reference set with Task 1A's `referenced_names` and list every step whose set is not a subset
   of its declared `consumes`, with the extra names. Check the extractor against the engine:
   for each expression, `zen.evaluate_expression` (or `zen.compile_expression`, whichever the
   binding exposes) with the reference set alone in the context must succeed, and with one
   name removed must fail. Report any expression where it does not. The fields are FD-1374's:
   `expr`, `condition`, `clamp_bounds`, `key_expr` and `feature_map`. **Apply this step, and
   step 6, explicitly to every real multi-table algorithm in the corpus**: that is where
   undeclared reads (P5) and M1's reference-set wiring interact. At `19155b50` the corpus has
   none; G2's algorithm is the first, at the Exit-demo re-run below.
2. **Merge order, then mixed producers.** First the engine fact: on a two-node probe, both
   nodes wired to `outputNode` and both writing key `k`, which value does the result keep,
   with the node list in order and with the edge list reversed? Record both. If the
   topologically later writer wins in both, M1 may wire every interior node to `outputNode`,
   and the rest of this step is moot. Otherwise, list every **mixed producer**: an interior
   node whose output holds a key a later node also writes and a key no later node writes.
   The `inputNode` counts as the writer of every raw input name. A constraint node always
   writes its own `<step>__violated` key and a `model_call` node its `$model_call_error`
   sentinel on failure (`MODEL_CALL_ERROR_KEY`, `runtime.py:74` at `ef5dc6e7`, read in `_check_model_call_sentinel`,
   `score.py:444`), both outside the declared
   `produces`; so **a clamp whose clamped name a later clamp re-produces is a mixed
   producer**, and so is a `model_call` whose produced name a later step re-produces (the clamp-in-place chain
   `packages/model-schema/tests/test_rating_algorithm.py:28` describes). A non-empty list goes
   to the decision-maker with the ruling: M1 cannot place such a node without the merge-order
   fact, and M4 is then the recommendation.
3. **Equality: the result UNCHANGED** (NFR-490's "never changes the result"; R3). Build the M1
   wire (Task 4's sample). Over the corpus of step 5, score every context untraced on today's
   wire, untraced on M1's, and traced on M1's. **The comparison:** the served `ScoringResult`
   serialised with `model_dump_json()` after `trace` and `timing_ms` are blanked, re-dumped as
   canonical JSON (`json.dumps(..., sort_keys=True, separators=(",", ":"))`), and compared
   **byte for byte**. A quote that raises compares its error code and message byte for byte.
   Report `equal N of N` per algorithm and per outcome class (quoted, **clamp-fired**,
   declined, error), and list every difference by quote and key. **Each of the four classes
   needs a non-zero count**, or the class is unproven and the `RS-` says so. The clamp-fired
   class is where M1's clamp-ordering risk lives (step 2).
4. **Payload bytes.** For the 63- and 200-step structures (`bench-trace-size.py`'s builder), record
   `len(json.dumps(out["trace"]))` from `async_evaluate(context, {"trace": True})` on both wires,
   the entry count, and the mean and maximum bytes per entry. Then predict the overhead from
   P4's 1:1 bytes-to-cost, labelled a prediction.
5. **Corpus: every multi-step algorithm that exists when S1 runs.** S1 does **not** wait for
   G2 or for `FD-1357`'s fix (the maintainer's correction of 2026-10-01: waiting would chain
   F35 behind G2).
   - **Committed seeds and fixtures, and any stored algorithm existing at run time:** each
     algorithm `examples/` seeds (at `19155b50` the freMTPL2 seed's is a three-step fixture,
     `examples/fremtpl2/model.py:327-330`), and each a stored Rating Version pins, if any
     exists when S1 runs (the auditor found none in the local databases on 2026-10-01). The
     `RS-` lists each with its `content_hash`.
   - **The richest fixtures:** every algorithm under `packages/pricing-core/tests/` that
     `compile_bundle` accepts and that exercises a table, a lookup, a clamp, a declining cap
     or a decline path, including `test_rating_score.py`'s `_compiled()` and
     `_compiled(glm=True)` (`s_clamp`, `s_decl_cap`, `s_decl_floor`), with 240 seeded
     contexts each (`driver_age` 17–99; both channels; `min_premium_minor` 0 and above the
     office premium, so the clamp fires; `sanity_cap_minor` and `sanity_floor_minor` set so
     each decline fires on some quotes); and the 200-step structure with 1000 seeded contexts.
   - **Declines and errors, on purpose:** contexts that fire each decline constraint; and
     contexts that raise, at least a rate-table miss (`RATE_TABLE_MISS`), an input-contract
     violation, and a `model_call` failure where the algorithm has one.
   - **The same harness re-runs later on G2's real freMTPL2 algorithm**, as an acceptance
     line of the Exit-demo slice (a line for that slice's plan to carry; the lead routes it).
     The re-run includes steps 1 and 6 (reference sets, added edges and cycles), not only
     step 3's equality, because it is the first real multi-table algorithm.
6. **New edges and cycles** (`load_bundle` safety for pinned bundles). M1 builds edges from
   reference sets, not from declared `consumes`. For an algorithm with an undeclared read
   (P5) that adds an edge the declared graph lacks, which can reorder evaluation or close a
   cycle the engine refuses at `create_decision` (`cyclicGraph`). Because `to_wire` runs in
   `load_bundle` and the content hash does not change (P11), a **pinned bundle that hydrates
   today would re-hydrate under the new wire**. Over the step 5 corpus **and any stored
   bundle existing at run time** (each compiled bundle a stored Rating Version holds), list
   every step whose reference set adds an edge beyond its declared `consumes`, with the
   source of that edge, and every added edge that closes a cycle; then call `load_bundle` on
   each stored bundle under the M1 wire and record each refusal. Expected: no cycle and no
   refusal. Any cycle, or a refusal, goes to the decision-maker with the ruling (DP-F35-1
   (iii-b)) (M4, which
   keeps today's wire for untraced calls, then still needs a traced graph that hydrates).

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1: Run the 7 `RL-862` capture tests at the base.** On a clean checkout of the
  base SHA, DB stack up, `GIP_TEST_DATABASE_URL` set as the slot wrapper sets it:
  ```bash
  uv run pytest -q \
    "backend/tests/test_score.py::test_a_decline_is_persisted_as_a_pending_trace_and_a_job_is_submitted" \
    "backend/tests/test_score.py::test_a_sampled_trace_is_completed_by_the_off_path_job" \
    "backend/tests/test_score.py::test_a_pinned_bundle_that_no_longer_resolves_is_refused_not_silently_rescored" \
    "backend/tests/test_traces.py::test_write_pending_trace_has_no_body_yet" \
    "backend/tests/test_traces.py::test_completing_a_pending_trace_that_reproduces_marks_it_complete" \
    "backend/tests/test_traces.py::test_completing_a_pending_trace_that_does_not_reproduce_keeps_the_body" \
    "backend/tests/test_traces.py::test_completing_a_pending_trace_with_no_reproduction_leaves_no_body"
  ```
  Expected: `7 passed`. Record the line, the SHA and `uptime`. **If any test fails, stop**:
  F35's gate-discharge record rests on this run, and the failure goes to the lead as a finding
  against the capture, before any code here.
- [ ] **Step 2:** Diff each minted ruling (activation needs 2 and 4) against this plan's
  recommendations, and name each difference in the dispatch record (§"Status").
- [ ] **Step 3:** Re-verify P1–P11 at the base: the three `passThrough` lines, `_build_trace`'s
  two lines, the `zen` stub, the fixture's two under-declared constraints. `SL-1345` moves
  lines in `runtime.py` and `score.py`; record the new numbers.
- [ ] **Step 4:** `gh pr list --state open`, and read anything that touches `runtime.py`,
  `score.py`, `TraceStep` or `03` §3.8/§4.5 (`SL-1340`, the `RL-1343` rule-4 slice, PL-1364).
  Name each head SHA in the ledger.

### Task 1: NFR-490 red at the base, and the frozen base corpus (solo window 1)

**Files:**
- Create: `packages/pricing-core/tests/data/trace_remedy_baseline.json`

- [ ] **Step 1:** In the lead's solo window, record `uptime`, `free -h`,
  `flock -n /tmp/slots/gate-1 true; echo $?`, `flock -n /tmp/slots/gate-2 true; echo $?` and
  `pgrep -af 'pytest|bench-|migrate --verify' | grep -v pgrep`. An rc of 1 means the slot is
  held: the window is not solo, so stop.
- [ ] **Step 2:** On the base checkout, run `uv run python scripts/bench-rating.py` five times
  in a row, with `LOKY_MAX_CPU_COUNT=4` and the dev-commands thread caps exported. Keep each
  full output.
- [ ] **Step 3:** Fill in the budget-margin statement (§"How NFR-490 is measured") for the
  base. **Expected: over** (m < 0), as F35 and `#1045` found. A base that reads under is a
  stop: report it to the lead before any code, because the premise has moved.
- [ ] **Step 4:** Record each run's A/B/C line (`engine-side (B-A)` and `ours (C-B)`). This is
  the base split that Task 6 compares.
- [ ] **Step 5:** `uv run python scripts/bench-trace-size.py` on the base. Record its output
  (NFR-500, bytes; not timing-sensitive, but run inside the window for one record).
- [ ] **Step 6: Freeze the base corpus, after Task 1A** (outside the solo window: it measures
  no time). Run this script on the tree Task 1A leaves, where the scoring code is still the
  base's and only the FR-246 check and the fixtures changed (the fixture change moves each
  bundle's hash, so a corpus frozen before it would differ in `bundle_hash` alone), and
  commit its output as Task 1A's last commit. It is the R3 baseline Task 4 compares against. Paste the script and its sha256 prefix in
  the ledger.

```python
"""Write the frozen base corpus for test_the_remedy_changes_no_served_result (PL-1520 Task 1)."""
import asyncio
import json
import random
import sys
from pathlib import Path

# Run from the repository root with `uv run python <this file>`.
sys.path.insert(0, str(Path("packages/pricing-core/tests").resolve()))

from test_rating_score import _compiled, _ctx  # noqa: E402

from pricing_core.rating.score import score_one  # noqa: E402


def contexts(seed: int, n: int) -> list[dict[str, object]]:
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        out.append({
            "driver_age": rng.randint(17, 99),
            "channel": rng.choice(["direct", "broker"]),
            "min_premium_minor": rng.choice([0, 0, 10**9]),
            "sanity_cap_minor": rng.choice([10**12, 10**12, 1]),
            "sanity_floor_minor": rng.choice([0, 0, 10**12]),
        })
    return out


async def served(compiled: object, inputs: dict[str, object]) -> dict[str, object]:
    """The served result with `trace` and `timing_ms` blanked, or the raised error's code."""
    try:
        result = await score_one(compiled, _ctx(inputs=inputs))  # type: ignore[arg-type]
    except Exception as exc:  # a raise is a result too; record which one
        return {"error": str(getattr(exc, "code", type(exc).__name__))}
    return json.loads(result.model_copy(update={"trace": None, "timing_ms": {}}).model_dump_json())


async def main() -> None:
    corpus = []
    for glm in (False, True):
        compiled = await _compiled(glm=glm)
        for inputs in contexts(seed=9776 + int(glm), n=240):
            corpus.append({
                "glm": glm,
                "inputs": inputs,
                "result": await served(compiled, inputs),
            })
    Path("packages/pricing-core/tests/data/trace_remedy_baseline.json").write_text(
        json.dumps(corpus, sort_keys=True, indent=1) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(corpus)} quotes")


asyncio.run(main())
```

  The five input names are the fixture's defaults (`test_rating_score.py:148-151`), and
  `_ctx(inputs=…)` replaces the whole dict. Check them against the fixture's `input_contract`
  at the base before running: **mirror the fixture, not this sample** ([`README.md`](README.md)
  convention 3). A quote that raises is recorded as `{"error": <code>}` in place of `result`,
  and the differential test compares the same way. Expected: `wrote 480 quotes`, with at least one `declined` and at least
  one clamped quote in each half (count them in the ledger).
- [ ] **Step 7:** Record `uptime` and `free -h` at the window's end.

```bash
git add packages/pricing-core/tests/data/trace_remedy_baseline.json
git commit -m "test(rating): freeze the base scoring corpus for the trace remedy's R3 check (WK-1178)"
```

### Task 1A: FR-246 enforced, red first; the four under-declaring fixtures fixed (DP-F35-1 (ii), FD-1374)

**Task 1A implements DP-F35-1 AS RULED. The design below is the RECOMMENDED branch; if the
ruling differs, a dated delta in the dispatch record rewrites 1A before it starts.** The
branch points are DP-F35-1 (ii) (refusal or ordering from reads; scope; mandatory
`consumes`), (iii-a) (the error code) and (iii-b) (the fate of a stored or pinned bundle).

**The ruled `03` text lands in this task's commit** (the maintainer's executor carve-out,
2026-10-01): FR-246's amendment (`03` §3.5) and the corrected §4.1 example with its Invariants note (§4.1, `03:240-289` at `ef5dc6e7`; RL-1519 §(iii) T2, T3), and,
under (iii-a) (b), the new code's owned-codes row. The executor applies the ruling's text
**byte for byte**, writes nothing of its own into `03`, and the ledger records
`git diff` of `03` beside the ruling's text.

**Files:**
- Modify: `docs/specs/03-rating-engine.md` (FR-246's row and the §4.1 example's JSON block and Invariants note, `03:240-289` at `ef5dc6e7`,
  verbatim from the ruling; under (iii-a) (b), also the code's owned-codes row)
- Create: `packages/pricing-core/src/pricing_core/rating/references.py`
- Create: `packages/pricing-core/tests/test_rating_declared_reads.py`
- Modify: `packages/pricing-core/src/pricing_core/rating/compile.py` (`_check_declared_reads`
  appended; one `ALGORITHM_CHECKS` entry; the import)
- Modify: `packages/pricing-core/tests/test_rating_score.py` (`_algorithm_payload`: three input
  steps, and `consumes` on `s_clamp`, `s_decl_cap`, `s_decl_floor`)
- Modify: `packages/model-schema/tests/test_rating_algorithm.py` (its `s_minprem`, `:65`, and one
  input step)
- Modify: `backend/src/app/errors.py` (the new code in `RATING_ERROR_CODES`; (iii-a) (b) only)

**Interfaces:**
- Produces: `referenced_names(node: Mapping[str, Any]) -> frozenset[str]` (Tasks 3 and 4 use it);
  `_check_declared_reads(algo: RatingAlgorithm) -> list[ValidationIssue]`.

**Written for the recommended answers:** DP-F35-1 (ii) refusal, scope every evaluated
field, `consumes` mandatory; (iii-a) (b) a new code, written below as
`RATING_STEP_UNDECLARED_READ` (the ruling names it; the executor uses the ruled name); (iii-b)
(b) grandfathered. A different scope changes `_DECLARED_READ_STEP_TYPES` only (method). Under
(iii-a) (b) the code's registry entry is added to `RATING_ERROR_CODES` in
`backend/src/app/errors.py`, which is in the write set for that branch only. **Under DP-F35-1
(ii) mandatory = no:** no `_check_declared_reads`, no refusal tests, Acceptance 2a reduces to
the example-validity test, and Task 3 still uses `referenced_names`.

**A compile-time refusal only** (the auditor's F4). The check runs inside `validate_algorithm`,
so it refuses at the save path (`backend/src/app/platform/rating_algorithms.py:91`,
`_issues_to_error`) and at compile (`compile.py:550`). A **previously saved** algorithm that
under-declares is refused at its next save or compile. An **already-compiled bundle is
unaffected**: `load_bundle` does not run `validate_algorithm`; its fate is DP-F35-1 (iii-b)'s
ruling. **Release note** (one paragraph in the squash-commit body and the ledger, as
`PL-1348` Acceptance 9 does): a deployment holding a saved algorithm whose steps read a name
they do not declare will have it refused, with the ruled code naming the step and the names,
at its next save or compile; already-compiled bundles keep loading and scoring, subject to
(iii-b); the fix is to add the names to `consumes` (and an `input` step for a raw name).

**Fixing a fixture needs an input step as well.** FR-212 requires every consumed name to have a
producer (`RatingAlgorithm._graph_invariants`, `packages/model-schema/src/model_schema/rating.py:394`;
the raise at `:419`, "consumes undefined value"),
and the scoring fixture has input steps only for `driver_age` and `channel`
(`test_rating_score.py:59-62`). So declaring `min_premium_minor` needs an `input` step producing
it. The four steps are **fixed**, not kept as negative fixtures, because `_compiled()` is the
positive fixture most of the pricing-core suite scores through; the old shape survives as the
**named negative fixture** in the new test module.

- [ ] **Step 1: Write the extractor test and the enforcement tests** (red: neither module
  function exists yet).

```python
"""PL-1520 Task 1A (FR-246, FD-1374): a step reads only names it declares."""

from __future__ import annotations

import copy

import pytest
from test_rating_score import _algorithm_payload

from model_schema.rating import RatingAlgorithm, RatingVersion
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle, validate_algorithm
from pricing_core.rating.references import referenced_names

#: DP-F35-1 (iii-a)'s ruled code; `RATING_STEP_UNDECLARED_READ` under the recommendation.
UNDECLARED_READ_CODE = "RATING_STEP_UNDECLARED_READ"


@pytest.mark.req("FR-258")
def test_referenced_names_reads_every_field_a_step_evaluates() -> None:
    clamp = {
        "type": "constraint", "consumes": ["office_premium_minor"], "produces": ["office_premium_minor"],
        "condition": "office_premium_minor >= min_premium_minor",
        "clamp_bounds": {"min": "min_premium_minor"},
    }
    assert referenced_names(clamp) == {"office_premium_minor", "min_premium_minor"}
    expr = {"type": "expression", "consumes": ["a"], "produces": "c", "expr": "a * b + round(a, 'half_even', 0)"}
    assert referenced_names(expr) == {"a", "b"}
    table = {"type": "table", "consumes": ["channel"], "produces": "f", "key_expr": ["channel"]}
    assert referenced_names(table) == {"channel"}
    model = {"type": "model_call", "consumes": ["driver_age"], "produces": ["r"],
             "feature_map": {"driver_age": "age_years"}}
    assert referenced_names(model) == {"driver_age"}
    quoted = {"type": "expression", "consumes": [], "produces": "c", "expr": "channel == 'broker_fee'"}
    assert referenced_names(quoted) == {"channel"}
    lookup = {"type": "lookup", "consumes": ["postcode_outcode"], "produces": "area",
              "key_expr": ["postcode_outcode"], "as_at": "effective_date"}
    assert referenced_names(lookup) == {"postcode_outcode", "effective_date"}


def _undeclared_clamp_payload() -> dict[str, object]:
    """The named negative fixture: the scoring fixture with `s_clamp` as it was before FD-1374's
    fix, reading `min_premium_minor` without declaring it."""
    payload = copy.deepcopy(_algorithm_payload())
    for step in payload["steps"]:  # type: ignore[union-attr]
        if step["step_id"] == "s_clamp":
            step["consumes"] = ["office_premium_minor"]
    return payload


def _fr246(issues: list[object]) -> list[object]:
    return [i for i in issues if "FR-246" in getattr(i, "message", "")]


@pytest.mark.req("FR-246")
def test_a_constraint_reading_an_undeclared_name_is_refused() -> None:
    issues = _fr246(validate_algorithm(RatingAlgorithm.model_validate(_undeclared_clamp_payload())))
    assert [(i.step_id, i.code) for i in issues] == [("s_clamp", UNDECLARED_READ_CODE)], issues
    assert "min_premium_minor" in issues[0].message


@pytest.mark.req("FR-246")
def test_an_expression_reading_an_undeclared_name_is_refused() -> None:
    payload = copy.deepcopy(_algorithm_payload())
    for step in payload["steps"]:  # type: ignore[union-attr]
        if step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor * expense_factor * sanity_cap_minor"
    issues = _fr246(validate_algorithm(RatingAlgorithm.model_validate(payload)))
    assert [(i.step_id, i.code) for i in issues] == [("s_office", UNDECLARED_READ_CODE)], issues


@pytest.mark.req("FR-246")
def test_the_fixed_fixture_declares_every_read() -> None:
    assert _fr246(validate_algorithm(RatingAlgorithm.model_validate(_algorithm_payload()))) == []


_SPEC_03 = Path(__file__).resolve().parents[3] / "docs" / "specs" / "03-rating-engine.md"


def _spec_example() -> dict[str, Any]:
    """`03` §4.1's example, verbatim: the first ```json block after the `### 4.1 ` heading."""
    lines = _SPEC_03.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("### 4.1 "))
    opening = next(i for i in range(start, len(lines)) if lines[i].startswith("```json"))
    closing = next(i for i in range(opening + 1, len(lines)) if lines[i].startswith("```"))
    payload: dict[str, Any] = json.loads("\n".join(lines[opening + 1 : closing]))
    return payload


class _StubResolver:
    """The example's own algorithm, and an approved stub payload for every other pinned ref.

    `compile_bundle` resolves each pin for its status and stores the payload verbatim
    (`compile.py:556-571`); it never parses a pinned payload, so a stub is enough for it to run.
    """

    def __init__(self, algorithm_ref: str, algorithm: dict[str, Any]) -> None:
        self._algorithm_ref = algorithm_ref
        self._algorithm = algorithm

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        if str(ref) == self._algorithm_ref:
            return ResolvedArtifact(status="approved", payload=self._algorithm)
        return ResolvedArtifact(status="approved", payload={"stub_for": str(ref)})


def _example_version(example: dict[str, Any]) -> RatingVersion:
    """A draft Rating Version pinning exactly the refs the example's steps name, mirroring
    `test_rating_score._version()` (`test_rating_score.py:118-134`)."""
    steps = example["steps"]
    rate = [s["rate_table_ref"] for s in steps if s.get("rate_table_ref")]
    reference = [s["reference_table_ref"] for s in steps if s.get("reference_table_ref")]
    models = [s.get("model_ref") or s["peril_structure_ref"] for s in steps if s["type"] == "model_call"]
    modes = {s["mode"] for s in steps if s["type"] == "model_call"}
    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": example["slug"],
        "version": example["version"], "status": "draft", "dataset_version_id": str(uuid4()),
        "model_ref": models[0] if models else None,
        "created_at": "2026-10-01T00:00:00Z", "created_by": str(uuid4()),
        "updated_at": "2026-10-01T00:00:00Z",
        "algorithm_ref": f"rating_algorithm:{example['slug']}@{example['version']}",
        "pins": {"rate_tables": rate, "models": models, "reference_tables": reference,
                 "custom_objectives": []},
        "model_reference_mode": modes.pop() if len(modes) == 1 else "exact",
    })


@pytest.mark.req("FR-246")
async def test_the_03_example_validates_in_full_and_compiles() -> None:
    """`RatingAlgorithm.model_validate` in full (FR-212, FR-214, every field), then
    `compile_bundle`, which runs `validate_algorithm` (`compile.py:550`) and so the
    declared-reads check once Step 4 registers it."""
    example = _spec_example()
    RatingAlgorithm.model_validate(example)
    version = _example_version(example)
    assert version.algorithm_ref is not None
    bundle = await compile_bundle(version, _StubResolver(str(version.algorithm_ref), example))
    assert bundle.content_hash.startswith("sha256:")


@pytest.mark.req("FR-246")
def test_the_03_example_declares_every_read() -> None:
    """The declared-reads check stated on its own, over the raw step dicts, so its red is
    visible even while the example fails validation."""
    undeclared = {
        step["step_id"]: sorted(referenced_names(step) - set(_as_list(step.get("consumes"))))
        for step in _spec_example()["steps"]
        if step["type"] not in ("input", "output")
    }
    undeclared = {sid: names for sid, names in undeclared.items() if names}
    assert undeclared == {}, f"03 §4.1 steps read undeclared names: {undeclared}"


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    return [str(v) for v in (value if isinstance(value, list) else [value])]
```

  Add `import json`, `from pathlib import Path`, `from typing import Any`, `from uuid import
  uuid4` and `from model_schema.refs import ArtifactRef` to the imports. `RatingVersion`,
  `ResolvedArtifact` and `compile_bundle` are already in the module's two single import lines
  above (as `test_rating_score.py:36-39` imports them).

  **How "then compile" is met: the test supplies stub payloads for the pinned refs**, so
  `compile_bundle` runs. The other option, a ruled example that pins fixture artifacts from the
  test corpus, is rejected: it would write test-fixture names (`rate_table:motor-expense@1`,
  `model:motor-freq@1`) into the governed spec's example, which must read as a real
  algorithm. Stubs suffice because `compile_bundle` resolves each pin for its status and
  stores the payload verbatim (`compile.py:556-571`) without parsing it. **What this does not
  cover:** hydration (`load_bundle`, where `to_wire` reads rate-table rows and boosters) needs
  real payloads for every pin and is not run on the example; and `compile_bundle` does not read
  `sub_graphs` at `19155b50` (`score.py:398-399`; at `ef5dc6e7`, `_check_purpose_mount`'s
  docstring, `:400-401`), so the example's sub-graph mount is not
  resolved. If `SL-1340` (the pin and inlining) has merged before Task 1A, `_StubResolver`
  serves the sub-graph ref as well and the dispatch record says so. If `RatingVersion`'s pins
  refuse the example's `peril_structure` ref under `models`, stop and report: the ruled
  example then needs a pinnable model ref.

- [ ] **Step 2: Run them, and record each red by its cause.**
  Run: `uv run pytest -q packages/pricing-core/tests/test_rating_declared_reads.py`.
  Expected: collection fails with `ModuleNotFoundError: No module named
  'pricing_core.rating.references'`. Any other cause is a plan defect.
- [ ] **Step 3: Write `references.py`.** Use the form Spike S1 verified against the engine. If
  S1 found a binding call that lists an expression's variables, use that instead of the
  tokenizer below, and the `RS-` records which. The tokenizer is the one FD-1374's sweep used.

```python
"""Which names a rating step reads (PL-1520; FR-246; DP-F35-1 (b)).

Used three ways: the save-time FR-246 check (`compile._check_declared_reads`), the trace's
`consumed` (`score._build_trace`) and M1's edges (`runtime.to_wire`). Computed once per
algorithm or bundle, never per quote.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

#: A ZEN expression's string literals, removed before identifiers are read.
_STRING = re.compile(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"")
#: An identifier not followed by `(` (a call) and not preceded by `.` or `$` (a member).
_NAME = re.compile(r"(?<![\w.$])([A-Za-z_][A-Za-z0-9_]*)\b(?!\s*\()")
_KEYWORDS = frozenset({"true", "false", "null", "and", "or", "not", "in"})


def _names_in(text: str) -> set[str]:
    return {m for m in _NAME.findall(_STRING.sub(" ", text)) if m not in _KEYWORDS}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    return [str(v) for v in (value if isinstance(value, list) else [value])]


def referenced_names(node: Mapping[str, Any]) -> frozenset[str]:
    """Declared `consumes` plus every name the node's evaluated fields read."""
    names = set(_as_list(node.get("consumes")))
    for field in ("expr", "condition"):
        if isinstance(node.get(field), str):
            names |= _names_in(node[field])
    for bound in (node.get("clamp_bounds") or {}).values():
        names |= _names_in(str(bound))
    for key in _as_list(node.get("key_expr")):
        names |= _names_in(key)
    if isinstance(node.get("as_at"), str):  # a lookup's as-at date names a context value
        names |= _names_in(node["as_at"])
    names |= set((node.get("feature_map") or {}).keys())
    return frozenset(names)
```

  `as_at` is read here although FD-1374's predicate does not read it (P5a). If Step 8's re-run
  with `as_at` finds an under-declaring step beyond the four, **stop and report**: the write
  set widens.

  A literal-number clamp bound gives `_names_in("28000") == set()`, which is right. Run the
  module again. Expected: the extractor test passes; the two refusal tests fail on an empty
  issue list (`[] == [("s_clamp", …)]`); the fixed-fixture control passes **only by accident**
  (no check yet), which Step 5 then makes real. **The two example tests are red against
  today's `03`, each on its own cause:** `test_the_03_example_validates_in_full_and_compiles`
  with a `ValidationError` from `RatingAlgorithm.model_validate` naming FR-214 (`declared output 'premium_ladder' has no output
  step`, the first of P5a's refusals); `test_the_03_example_declares_every_read` naming the
  five steps `s_area`, `s_rp`, `s_expense`, `s_office` and `s_minprem`. Any other cause is a
  plan defect.
- [ ] **Step 4: Append the check to `compile.py`** and register it in `ALGORITHM_CHECKS`
  (`compile.py:299-302`) as its last entry.

```python
#: FR-246's scope as DP-F35-1 (ii) ruled it: every step type that evaluates a field.
_DECLARED_READ_STEP_TYPES = frozenset({"expression", "table", "lookup", "model_call", "constraint"})


def _check_declared_reads(algo: RatingAlgorithm) -> list[ValidationIssue]:
    """FR-246: a step reads only names it declares in `consumes` (FD-1374; the DP-F35-1 ruling)."""
    issues: list[ValidationIssue] = []
    for step in algo.steps:
        if step.type not in _DECLARED_READ_STEP_TYPES:
            continue
        declared = set(_as_list(step.consumes))
        undeclared = sorted(referenced_names(step.model_dump()) - declared)
        if undeclared:
            issues.append(
                ValidationIssue(
                    code="RATING_STEP_UNDECLARED_READ",  # the code DP-F35-1 (iii-a) rules
                    message=(
                        f"step {step.step_id!r} reads {undeclared} without declaring them in "
                        "consumes (FR-246)"
                    ),
                    step_id=step.step_id,
                    field="consumes",
                )
            )
    return issues
```

  Cite the minted ruling id in the docstring. Confirm `ValidationIssue`'s fields
  (`compile.py:58-70`) before running.
- [ ] **Step 5: Fix the four fixtures.** In `test_rating_score.py`'s `_algorithm_payload`, add
  three `input` steps after `s_in_channel`, mirroring `s_in_age` (`input_name`,
  `on_missing: "error"`, `produces` the same name) for `min_premium_minor`, `sanity_cap_minor`
  and `sanity_floor_minor`; then set `s_clamp`'s `consumes` to `["office_premium_minor",
  "min_premium_minor"]`, `s_decl_cap`'s to `["office_premium_minor", "sanity_cap_minor"]` and
  `s_decl_floor`'s to `["office_premium_minor", "sanity_floor_minor"]`. In
  `packages/model-schema/tests/test_rating_algorithm.py`, give `s_minprem` (`:65`)
  `["office_premium_minor", "min_premium_minor"]` and add the matching `input` step, after
  checking that fixture's `input_contract` names `min_premium_minor` (add the field if not).
- [ ] **Step 6:** Run `uv run pytest -q packages/pricing-core/tests/test_rating_declared_reads.py`.
  Expected: 4 passed and the two example tests still failing (Step 8 turns them green). Then
  the broken-input proof of the control: revert Step 5's
  `s_decl_cap` line only, run `test_the_fixed_fixture_declares_every_read`, and expect FAIL
  naming `s_decl_cap` and `sanity_cap_minor`; restore Step 5's line.
- [ ] **Step 7:** Run the packages and the backend tests that compile algorithms, **in a gate
  slot** (more than one test file: the dev-commands slot wrapper, `SKILL.md:122-171`, with
  `LOKY_MAX_CPU_COUNT=4`; the DB stack up). The backend files come from this predicate, run at
  the base:
  ```bash
  git grep -l -E 'compile_bundle|validate_algorithm|/api/v1/rating-algorithms|rating\.compile|_run_compile_job|create_rating_algorithm' -- 'backend/tests/*.py'
  ```
  At `19155b50` it printed **11** files: `test_demo_rating_evidence.py`, `test_error_sinks.py`,
  `test_rating_algorithms.py`, `test_rating_pin_membership_api.py`,
  `test_rating_version_compile.py`, `test_rating_versions.py`, `test_regression_runs.py`,
  `test_score.py`, `test_score_compare.py`, `test_scoring_handlers.py`,
  `test_worker_raise_sites.py`. **Its blind spots:** a test that reaches compile or save through a
  service or helper whose name it does not match (`test_regression_suites.py` does, through
  `app.platform.regression_suites`, so it is **added by name**: 12 files); a route built from a
  variable; a fixture in `conftest.py` that compiles for a test that names none of these. A
  different count at the base is recorded with the new list. **Not deferred to the Task 7
  gate:** Task 1A changes what compiles, and FD-1374's sweep could not evaluate 12 steps whose
  fields are not literals, so these files are the evidence. Run:
  `uv run pytest -q packages/pricing-core/tests/ packages/model-schema/tests/ <the 12 files>`.
  Expected: green apart from the two example tests (Step 8). The scoring results do not change (input steps collapse into the engine's
  `inputNode`), but each fixture's bundle hash does. **A test outside the write set that pins
  the fixture's step list or hash is a stop**: report it, because it widens the write set.
- [ ] **Step 8:** Apply the ruling's FR-246 amendment and corrected §4.1 example to `03` byte
  for byte (and, under (iii-a) (b), the owned-codes row and the `errors.py` registry entry).
  Run the two example tests: expected **green** (the ruled example passes both checks). A
  ruled example that still fails is a stop, reported to the lead; the executor does not edit
  the ruled text. Run `python3 scripts/audit-docs.py`: expected only check 31's working-id
  line, or nothing once minted. Re-run FD-1374's predicate (P5) over the tree. Expected: 0 steps with an
  undeclared read. Record both in the ledger. Then commit the code, the fixtures and the `03`
  text as **one** commit, and run Task 1 Step 6.

```bash
# (iii-a) (b) only: also `git add backend/src/app/errors.py`
git add docs/specs/03-rating-engine.md packages/pricing-core/src/pricing_core/rating/references.py packages/pricing-core/src/pricing_core/rating/compile.py packages/pricing-core/tests/test_rating_declared_reads.py packages/pricing-core/tests/test_rating_score.py packages/model-schema/tests/test_rating_algorithm.py
git commit -m "fix(rating): a step reads only names it declares — FR-246 enforced, fixtures fixed (WK-1178, FD-1374)"
```

### Task 2: The trace-shape tests, red at the base

**Files:**
- Create: `packages/pricing-core/tests/test_rating_trace_minimal.py`

**Interfaces:**
- Consumes: `test_rating_score._compiled`, `_ctx`; `pricing_core.rating.score.score_one`.
- Produces: the module that Tasks 3 and 4 append to; `_by_id(trace)`.

- [ ] **Step 1: Write the failing tests.**

```python
"""PL-1520 (WK-1178, F35): a TraceStep records what its step read and declared, nothing more."""

from __future__ import annotations

import pytest
from test_rating_score import _compiled, _ctx

from model_schema.scoring import Trace, TraceStep
from pricing_core.rating.score import score_one


#: The fixture's default inputs; `_ctx(inputs=…)` replaces the whole dict (`test_rating_score.py:143-155`).
_DEFAULT_INPUTS = dict(_ctx().inputs)


def _by_id(trace: Trace) -> dict[str, TraceStep]:
    return {step.step_id: step for step in trace.steps}


async def _trace(**overrides: object) -> Trace:
    compiled = await _compiled()
    result = await score_one(compiled, _ctx(inputs={**_DEFAULT_INPUTS, **overrides}), trace=True)
    assert result.trace is not None
    return result.trace


@pytest.mark.req("FR-258")
async def test_an_expression_step_records_only_what_it_read() -> None:
    step = _by_id(await _trace())["s_office"]
    extra = set(step.consumed) - {"risk_premium_minor", "expense_factor"}
    assert not extra, f"consumed has keys beyond the step's references: {sorted(extra)}"
    assert set(step.consumed) == {"risk_premium_minor", "expense_factor"}


@pytest.mark.req("FR-258")
async def test_a_clamp_records_the_bound_it_read_and_the_pre_clamp_value() -> None:
    step = _by_id(await _trace())["s_clamp"]
    assert set(step.consumed) == {"office_premium_minor", "min_premium_minor"}, (
        f"consumed keys {sorted(step.consumed)}"
    )
    assert set(step.produced) == {"office_premium_minor"}, f"produced keys {sorted(step.produced)}"


@pytest.mark.req("FR-258")
async def test_produced_holds_only_declared_names() -> None:
    trace = await _trace()
    compiled = await _compiled()
    declared = {
        s.step_id: set([s.produces] if isinstance(s.produces, str) else s.produces)
        for s in compiled.algorithm.steps
    }
    for step in trace.steps:
        extra = set(step.produced) - declared[step.step_id]
        assert not extra, f"{step.step_id}: produced has undeclared keys {sorted(extra)}"


@pytest.mark.req("FR-258")
async def test_a_clamp_still_records_its_violation_after_the_trim() -> None:
    # A minimum premium above any office premium the fixture produces, so the clamp fires.
    step = _by_id(await _trace(min_premium_minor=10**9))["s_clamp"]
    assert step.violation is not None, "the clamp fired but the trace lost its violation"


@pytest.mark.req("FR-258")
async def test_every_algorithm_step_is_traced_once() -> None:
    trace = await _trace()
    compiled = await _compiled()
    traced = [s.step_id for s in trace.steps]
    expected = [s.step_id for s in compiled.algorithm.steps]
    missing = sorted(set(expected) - set(traced))
    assert not missing, f"steps missing from the trace: {missing}"
    assert sorted(traced) == sorted(expected)
```

  `_ctx(**overrides)` replaces top-level `QuoteContext` fields, so an input override passes a
  whole `inputs` dict, as `test_rating_score.py:201` and `:246` do.
- [ ] **Step 2: Run them at the base, and record each red's cause.**
  Run: `uv run pytest -q packages/pricing-core/tests/test_rating_trace_minimal.py`.
  Expected, each by its cause:
  - `test_an_expression_step_records_only_what_it_read`: FAIL, `consumed has keys beyond the
    step's references:` followed by the context keys (`channel`, `driver_age`, …);
  - `test_a_clamp_records_the_bound_it_read_and_the_pre_clamp_value`: FAIL, `consumed keys`
    listing the whole context;
  - `test_produced_holds_only_declared_names`: FAIL, `produced has undeclared keys`;
  - `test_a_clamp_still_records_its_violation_after_the_trim`: **PASS** at the base (the
    control: it guards the trim, and Task 3 must keep it green; Task 3 Step 9 proves it on
    broken input);
  - `test_every_algorithm_step_is_traced_once`: FAIL, `steps missing from the trace:` naming
    the `input` and `output` steps (FD-1246).

  A failure with any other cause is a plan defect: stop and report it.

```bash
git add packages/pricing-core/tests/test_rating_trace_minimal.py
git commit -m "test(rating): a trace step records what its step read and declared — red (WK-1178, F35)"
```

### Task 3: What the trace records (DP-F35-1 (b), DP-F35-2 (b))

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/runtime.py` (`CompiledBundle`, `load_bundle`)
- Modify: `packages/pricing-core/src/pricing_core/rating/score.py` (`_build_trace`, `build_scoring_result`)
- Modify: `packages/model-schema/src/model_schema/scoring.py` (`TraceStep`'s docstring)
- Modify: `packages/pricing-core/tests/test_rating_score.py` (the `:530` test's `isdisjoint` assertion)

**Interfaces:**
- Consumes: `referenced_names` (Task 1A).
- Produces: `CompiledBundle.references: Mapping[str, frozenset[str]]` (step id → reference set, interior
  steps only); `_build_trace(algorithm, engine_trace, references, rating_version_ref,
  bundle_hash, quote_id, ladder_reconciled) -> Trace`.

- [ ] **Steps 1–2:** `references.py` and its test already exist (Task 1A).
- [ ] **Step 3:** In `runtime.py`, add
  `references: Mapping[str, frozenset[str]] = field(default_factory=dict)` as the last field
  of `CompiledBundle` (import `field` from `dataclasses`), and in `load_bundle` fill it with
  `{sid: referenced_names(node) for sid, node in bundle.graph.nodes.items() if node["type"] in _ENGINE_NODE_TYPE}`.
  **Why a default:** the only other construction is the test double at
  `backend/tests/test_bundle_slot.py:83`, whose `decision=object()` never evaluates, so it
  never reaches `_build_trace`. A default keeps that file, and `backend/tests/` as a whole, out of
  the write set (Acceptance 12). It does not hide a missing set: `load_bundle` is the only
  production constructor and always fills it, and a `CompiledBundle` built without it that
  did trace would raise `KeyError` in `_build_trace` (`references[step.step_id]`), loudly.
  Grep `CompiledBundle(` in `packages/`, `backend/` and `scripts/` at the base: expected
  exactly those two sites (`runtime.py:597`, `test_bundle_slot.py:83`). A third is a stop.
- [ ] **Step 4: Rewrite `_build_trace`'s loop.** The signature gains `references` after
  `engine_trace`; `build_scoring_result` passes `bundle.references`. The loop body:

```python
    step_meta = {step.step_id: step for step in algorithm.steps}
    entries = sorted(engine_trace.values(), key=lambda entry: entry.get("order", 0))
    by_id = {str(entry.get("id")): entry for entry in entries}
    context = dict((by_id.get(_INPUT_NODE_ID) or {}).get("output") or {})
    result = dict((by_id.get(_OUTPUT_NODE_ID) or {}).get("input") or {})
    steps: list[TraceStep] = []
    # DP-F35-2 (b): input steps first, in algorithm order. The engine evaluates every input
    # step as one collapsed `inputNode`, so a per-step elapsed time does not exist: 0.
    for step in algorithm.steps:
        if isinstance(step, RatingInputStep):
            steps.append(TraceStep(
                step_id=step.step_id, type=step.type, label=step.label, consumed={},
                produced={n: context[n] for n in _as_list(step.produces) if n in context},
                elapsed_us=0,
            ))
    for entry in entries:
        step = step_meta.get(entry.get("id"))
        if step is None or isinstance(step, (RatingInputStep, RatingOutputStep)):
            continue  # the wire nodes; input/output steps are recorded above and below
        received = entry.get("input") or {}
        output = entry.get("output") or {}
        violation: dict[str, object] | None = None
        if isinstance(step, RatingConstraintStep) and bool(output.get(f"{step.step_id}__violated", False)):
            violation = {"reason_code": step.reason_code, "on_violation": step.on_violation}
        trace_data = entry.get("traceData")
        steps.append(TraceStep(
            step_id=step.step_id, type=step.type, label=step.label,
            consumed={n: received[n] for n in sorted(references[step.step_id]) if n in received},
            produced={n: output[n] for n in _as_list(step.produces) if n in output},
            matched=trace_data if isinstance(trace_data, dict) else None,
            violation=violation,
            elapsed_us=_parse_elapsed_us(str(entry.get("performance", "0"))),
        ))
    # Output steps last, in algorithm order, from what reached the `outputNode`.
    for step in algorithm.steps:
        if isinstance(step, RatingOutputStep):
            steps.append(TraceStep(
                step_id=step.step_id, type=step.type, label=step.label,
                consumed={n: result[n] for n in _as_list(step.consumes) if n in result},
                produced={}, elapsed_us=0,
            ))
```

  `_INPUT_NODE_ID` and `_OUTPUT_NODE_ID` are `runtime.py`'s `_INPUT_ID` (`"input"`) and
  `_OUTPUT_ID` (`"output"`), imported under those names; if the import-linter or the
  underscore convention objects, export them from `runtime.py` without the underscore. Confirm
  `RatingInputStep` is imported in `score.py` (it imports `RatingOutputStep` at `:200`). Keep the
  existing violation-flag read, which reads the engine's output **before** the trim.
- [ ] **Step 5:** Invert the `isdisjoint` assertion in
  `test_trace_true_returns_a_populated_trace_and_the_identical_premium`
  (`test_rating_score.py:545-550`) so it asserts the five `input`/`output` step ids are
  **present**, and update its comment to cite DP-F35-2 (b).
- [ ] **Step 6:** Replace `TraceStep`'s docstring (`scoring.py:139-144`) with the ruled reading:

```python
    """One node of a `Trace` (FR-258, `scoring.schema.json:71-86`).

    `consumed` holds the value of every name the step reads (its declared `consumes` and
    every name its expression, condition, clamp bounds, table key or feature map reads), as
    the step received it; `produced` holds its declared `produces`. Never the engine's
    accumulated context (F35, F55; the DP-F35-1 ruling). `input` and `output` steps are
    traced with `elapsed_us` 0, because the engine evaluates each kind as one node.
    """
```

  Cite the minted ruling id in place of "the DP-F35-1 ruling".
- [ ] **Step 7:** Run `uv run python scripts/generate-contracts.py` and confirm
  `git diff -- docs/contracts/` changes description text only (Acceptance 10).
- [ ] **Step 8:** Run `uv run pytest -q packages/pricing-core/tests/test_rating_trace_minimal.py packages/pricing-core/tests/test_rating_score.py`.
  Expected: all Task 2 tests pass. The engine still sends the whole
  context (P1); Task 4 removes that.
- [ ] **Step 9: The violation control, on broken input** (Acceptance 2). In the working tree,
  replace the `violation = {...}` assignment in `_build_trace` with `pass`, so `violation`
  stays `None`. Run `test_a_clamp_still_records_its_violation_after_the_trim`. Expected:
  FAIL, `the clamp fired but the trace lost its violation`. Quote the line in the ledger.
  Revert with `git checkout -- packages/pricing-core/src/pricing_core/rating/score.py`.

```bash
git add packages/pricing-core/src/pricing_core/rating/runtime.py packages/pricing-core/src/pricing_core/rating/score.py packages/model-schema/src/model_schema/scoring.py packages/pricing-core/tests/test_rating_trace_minimal.py packages/pricing-core/tests/test_rating_score.py docs/contracts/
git commit -m "fix(rating): a trace step records what its step read and declared (WK-1178, F35, F55, FD-1246)"
```

### Task 4: What the engine carries (DP-F35-4 (M1)), with R3 held

*(**Superseded 2026-10-05 by Delta 2's Task 4R**, written for DP-F35-7 (a). The text below stays as filed; Task 4R reuses its Step 1, Step 2, Step 3 sample and Step 5 by reference.)*

*(The Delta of 2026-10-05, after 17:39:08 BST: this task is written for M1 on today's wire. On SL-1436's chain it waits for DP-F35-7, and it is rewritten, or the plan superseded, once DP-F35-7 is ruled.)*

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/runtime.py` (`to_wire`, the three node builders, the module docstring's rule 3)
- Test: `packages/pricing-core/tests/test_rating_trace_minimal.py` (append two tests)

- [ ] **Step 1: Append the payload-bound test** (red at this point: `passThrough` is still on).

```python
@pytest.mark.req("FR-258")
async def test_engine_entry_input_is_bounded_by_its_references() -> None:
    compiled = await _compiled()
    ctx = _ctx()
    context_keys = {"effective_date", "purpose", *ctx.inputs}
    out = await compiled.decision.async_evaluate(
        {"effective_date": ctx.effective_date.isoformat(), "purpose": ctx.purpose, **ctx.inputs},
        {"trace": True},
    )
    for entry in out["trace"].values():
        sid = str(entry.get("id"))
        if sid not in compiled.references:
            continue  # the wire nodes
        extra = set(entry.get("input") or {}) - compiled.references[sid] - context_keys
        assert not extra, f"{sid}: the engine carried names the step never reads: {sorted(extra)}"
```

  Run it. Expected: FAIL, `the engine carried names the step never reads:` naming computed
  names such as `risk_premium_minor` on a step downstream of `s_risk` that does not read it.
- [ ] **Step 2: Append the R3 differential test.**

```python
import json
from pathlib import Path

_BASELINE = Path(__file__).parent / "data" / "trace_remedy_baseline.json"


@pytest.mark.req("NFR-490")
async def test_the_remedy_changes_no_served_result() -> None:
    corpus = json.loads(_BASELINE.read_text(encoding="utf-8"))
    compiled = {glm: await _compiled(glm=glm) for glm in (False, True)}
    changed: list[str] = []
    for i, case in enumerate(corpus):
        try:
            result = await score_one(compiled[case["glm"]], _ctx(inputs=case["inputs"]))
        except Exception as exc:
            now: dict[str, object] = {"error": str(getattr(exc, "code", type(exc).__name__))}
        else:
            now = json.loads(
                result.model_copy(update={"trace": None, "timing_ms": {}}).model_dump_json()
            )
        if now != case["result"]:
            changed.append(f"quote {i}: outcome {case['result'].get('outcome')} -> {now.get('outcome')}")
    assert not changed, f"{len(changed)} of {len(corpus)} served results changed: {changed[:5]}"
```

  It reads results exactly as Task 1 Step 6's `served()` wrote them. It passes now (Task 3
  changed no result).
- [ ] **Step 3: Change the wire.** In `to_wire`, keep the interior loop and change what it
  wires. Use the rule DP-F35-4's ruling adopts from Spike S1; this is the candidate:

```python
    refs = {sid: referenced_names(graph.nodes[sid]) for sid in interior_ids}
    produced_by: dict[str, str] = {}
    writes: dict[str, list[str]] = {}          # name -> every interior step writing it, in order
    for step_id in interior_ids:
        node = graph.nodes[step_id]
        sources = {produced_by.get(name, _INPUT_ID) for name in refs[step_id]}
        for source in sorted(sources):
            edges.append(_edge(source, step_id))
        # ... the existing per-type node construction, unchanged except `passThrough` ...
        for name in _as_list(node["produces"]):
            produced_by[str(name)] = step_id
            writes.setdefault(str(name), []).append(step_id)

    # The result must still hold every key the scoring tail reads: every produced name's
    # final value, every constraint's `__violated` flag, a model_call's error sentinel, and
    # the raw inputs. A node is wired to `outputNode` unless a later node overwrites every
    # name it produces. Constraint and model_call nodes are always wired: each writes a key
    # outside its declared `produces` that the tail reads from the result (a constraint's
    # `__violated`, read by `_apply_constraints`; a model_call's `$model_call_error`,
    # `MODEL_CALL_ERROR_KEY`, read in `score.py`'s `_check_model_call_sentinel`). Spike S1 step 2 showed either that the later
    # writer wins at `outputNode`, or that the corpus has no mixed producer.
    edges.append(_edge(_INPUT_ID, _OUTPUT_ID))
    for step_id in interior_ids:
        names = [str(n) for n in _as_list(graph.nodes[step_id]["produces"])]
        overwritten = [n for n in names if writes[n][-1] != step_id]
        if (names and len(overwritten) == len(names)
                and graph.nodes[step_id]["type"] not in ("constraint", "model_call")):
            continue
        edges.append(_edge(step_id, _OUTPUT_ID))
```

  This replaces the existing consumes-edge loop (`for name in _as_list(node["consumes"])`, the
  edge at `runtime.py:412`,
  which also fills `consumed_by_someone`) and the final `outputNode` wiring loop; the per-type
  node construction between them is unchanged except for `passThrough`. Set
  `"passThrough": False` in `_expression_node` (`:162`), `_decision_table_node` (`:256`) and
  `_constraint_node` (`:322`). Rewrite the module docstring's rule 3 and `to_wire`'s
  docstring paragraph on `passThrough` (`:362-368`) to state the new rule and cite the minted
  DP-F35-4 ruling. **If S1 found the later writer wins at `outputNode`, the ruling may simplify
  the rule to "wire every interior node"; use the ruling's form.**
- [ ] **Step 4:** Run `uv run pytest -q packages/pricing-core/tests/` (the whole pricing-core
  suite, a named directory). Expected: green, including the payload-bound test, the R3
  differential, `test_rating_score.py` and `SL-1345`'s ladder sweep. Any red in
  `test_rating_score.py` or the sweep is an R3 failure: **stop and report**; do not adjust an
  expected value.
- [ ] **Step 5: The broken-input proof** (Acceptance 6). In the working tree, change the
  last `if` so constraint nodes are skipped as well (delete `and graph.nodes[step_id]["type"] !=
  "constraint"` and add `or graph.nodes[step_id]["type"] == "constraint"` before the `continue`).
  Run the differential test. Expected: FAIL, `served results changed:` naming at least one quote
  whose outcome moved from `declined` to `quoted`. Quote the line in the ledger. Revert with
  `git checkout -- packages/pricing-core/src/pricing_core/rating/runtime.py`.

```bash
git add packages/pricing-core/src/pricing_core/rating/runtime.py packages/pricing-core/tests/test_rating_trace_minimal.py
git commit -m "perf(rating): the engine carries only what each node reads; result unchanged (WK-1178, F35, NFR-490)"
```

### Task 5: `score/compare` and the capture path, re-proved

**Files:**
- Modify: `backend/tests/test_score_compare.py`

**The derivation.** The fixture (`test_score_compare.py:55-115`, built on
`backend/tests/test_rating_version_compile.py:50-72`) has four steps: `s_in` (produces
`premium_in`), `s_expr` (reads `premium_in`, produces `payable`; `* 2` in version 1, `* 3` in
version 2), `s_adj` (reads `payable`, produces `adjusted`) and `s_out` (reads `adjusted`). At
the base only `s_expr` and `s_adj` are traced. Under DP-F35-1 (b) and DP-F35-2 (b):
- `s_in`: `consumed` `{}`, `produced` `{"premium_in": 1000}` on both sides: **unchanged**;
- `s_expr`: same `consumed`, different `produced`: **changed**, `own_change` true;
- `s_adj`: `consumed` moved: **changed**, `own_change` false;
- `s_out`: `consumed` `{"adjusted": …}` moved: **changed**, `own_change` false.

So three existing tests change, each red first:

- [ ] **Step 1:** Run `uv run pytest -q backend/tests/test_score_compare.py` at the end of
  Task 4, unchanged. Expected reds, each by its cause:
  - `test_compare_returns_both_traced_results_and_the_step_diff`: the step list is
    `["s_expr", "s_adj", "s_out"]` against the expected `["s_expr", "s_adj"]`;
  - `test_exactly_one_step_is_the_own_change_at_the_http_layer`: the downstream list is
    `["s_adj", "s_out"]` against `["s_adj"]` (its `unchanged == 0` would also fail: it is 1);
  - `test_identical_refs_give_an_empty_diff`: `"unchanged": 4` against 2.

  Any other red is a plan defect: stop.
- [ ] **Step 2:** Update the three expectations to the derivation above: the step list
  `["s_expr", "s_adj", "s_out"]`; downstream `["s_adj", "s_out"]`, each with `consumed` in its
  `changed_fields`, and `unchanged == 1`; `{"steps": [], "unchanged": 4}`. The own change is
  still exactly `["s_expr"]` (`RL-1172`'s one-step proof holds).
- [ ] **Step 3: Append the test the trimmed trace makes possible.**

```python
@pytest.mark.req("FR-262")
def test_a_step_whose_references_did_not_move_is_traced_and_not_listed(
    client: TestClient, reader_headers: dict[str, str], two_versions: None
) -> None:
    """F55's lever at the HTTP layer: `s_in` is in both traces, reads nothing the edit moved,
    and so is counted unchanged rather than listed."""
    body = client.post(COMPARE_URL, json=_body(), headers=reader_headers).json()
    assert "s_in" in {s["step_id"] for s in body["base"]["trace"]["steps"]}
    assert "s_in" not in {s["step_id"] for s in body["diff"]["steps"]}
    assert body["diff"]["unchanged"] == 1
```

  At the base it fails on the first assert (`s_in` is not traced, FD-1246). Run
  `uv run pytest -q backend/tests/test_score_compare.py`. Expected: green.
- [ ] **Step 4:** Run Task 0 Step 1's command again at HEAD. Expected: `7 passed`.

```bash
git add backend/tests/test_score_compare.py
git commit -m "test(scoring): score/compare re-proved on the trimmed trace (WK-1178, F35, FR-262)"
```

### Task 6: NFR-490 and NFR-500 after the change (solo window 2)

- [ ] **Step 1:** In the lead's second solo window, the same opening checks as Task 1 Step 1.
- [ ] **Step 2:** Run `uv run python scripts/bench-rating.py` ten times, alternating base and
  HEAD (five each), each on its own clean checkout, both SHAs named.
- [ ] **Step 3:** Fill in the budget-margin statement for each tree. **Stop rule:** if HEAD's
  median overhead is not below half of the base's median overhead in this window, the premise
  that bytes drive the cost (P4) has failed. Stop and report to the lead before merging; the
  slice does not merge on a remedy that did not move the cost. **The stop rule is a premise
  test, not a sufficiency test:** passing it does not mean NFR-490 passes. A HEAD that moved
  the cost but is still over NFR-490 merges on this slice's other acceptance items, and the
  remaining overhead goes to SL-1259's "residual with an owner" path (the maintainer's
  09:00:44 entry), stated in the ledger.
- [ ] **Step 4: The 200-step equality.** Run, on each tree, a script that scores 1000 seeded
  contexts on `bench-rating.py`'s 200-step structure untraced and prints each `ScoringResult`
  (trace and timing blanked) as canonical JSON, one line each; then `diff` the two outputs and
  print `equal N of 1000`. Paste the script and its sha256 prefix. Expected: `equal 1000 of
  1000`.
- [ ] **Step 5:** `uv run python scripts/bench-trace-size.py` at HEAD. Read the 200-step
  projection against 200 GB/year under DP-F35-3's ruled reading, beside Task 1 Step 5's base
  figure.
- [ ] **Step 6:** Record the A/B/C split at HEAD beside the base's. The engine-side share
  (B−A) is the one this remedy targets.
- [ ] **Step 7:** `uptime` and `free -h` at the end. A run with a held slot, or a load above
  the box's core count at either end of a run, is discarded and re-run. Never average a
  contended run in.

### Task 7: The gate and the ledger

- [ ] **Step 1:** Regenerate `docs/INDEX.md` after adding the ledger (`python3 scripts/doc-index.py`),
  and run `python3 scripts/doc-id.py migrate --verify <tmpdir> --ref HEAD`, reading row (a)
  (`delivery-process.md` §11a).
- [ ] **Step 2:** Run the full gate under §"Gate evidence rules".
- [ ] **Step 3:** The ledger records: Task 0's two capture-test runs; every red proof with its
  printed line (paraphrase a line that names an undefined id, [`README.md`](README.md) rule 2);
  both budget-margin statements; both NFR-500 projections; the A/B/C splits; the 200-step
  equality; the gate table.

## Gate evidence rules

For **every** suite-level run, the full gate and each solo window, the ledger records:

- **A clean checkout of the named SHA:** `git status --porcelain` prints nothing; `HEAD` quoted.
- **The dev-commands slot wrapper, verbatim** (`.claude/skills/dev-commands/SKILL.md:122-171`:
  the gate body and the two-slot `flock -n -E 99` / `flock -w 7200 -E 98` loop), with
  **`LOKY_MAX_CPU_COUNT=4`** exported beside the thread caps, in the foreground under a
  `timeout`.
- **`ruff check --no-cache`**, and **`mypy --no-incremental`** (or a fresh cache).
- **`uptime` and `free -h`** at the start and at the end.
- **The other slot's holder**, read with `flock -n /tmp/slots/gate-1 true; echo $?` and
  `flock -n /tmp/slots/gate-2 true; echo $?` before the run, and named as gate or not-gate. An
  rc of 1 means the slot is held.
- **The wall time and the pytest time** against the solo baseline `PL-1348` uses
  (`PL-1348:433-434`). A slower run is read as load first.
- **Every rc** of the two-half gate (`CLAUDE.md` §11), the `N passed` line, and `origin/main`'s
  `N passed` beside it. Only named single test files or node ids are exempt. Docs checks run on
  a clean detached checkout. After merging a `main` that adds a migration, run `alembic upgrade
  head` on the per-worktree test database first.
- **The solo window** (Tasks 1 and 6): no gate, suite, benchmark or `migrate --verify` runs
  during it, shown by the slot reads and the `pgrep` line at both ends, and the lead's grant is
  dated in the dispatch record.

## Risks

| Risk | Effect | Detection | Response |
|---|---|---|---|
| M1 changes a served result (a raw input or `__violated` key missing from the result, a merge-order clash at `outputNode`) | a mispricing, R3 broken | Spike S1 step 3; Acceptance 6's differential and its broken-input proof; `SL-1345`'s ladder sweep | stop. The decision-maker considers M4 (two graphs). Never adjust an expected value |
| An undeclared read (P5) adds an edge under M1's reference-set wiring | evaluation reorders, or a cycle closes and the engine refuses `cyclicGraph` in `load_bundle`, for a **pinned bundle that hydrates today** (the content hash is unchanged, so it reloads under the new wire) | Spike S1 step 6, over the corpus and every stored bundle | stop before DP-F35-4 is ruled for M1; the decision-maker weighs M4 or a guarded fallback for bundles that would not hydrate |
| An expression reads a name the tokenizer misses (a member access, a `$` reference, a name inside a nested call) | under M1 the engine lacks the name, and the step fails or reads null | Spike S1 step 1 checks every expression against the engine with its reference set alone | use the binding's own variable listing if S1 finds one; else extend the extractor and re-run S1 |
| The remedy cuts bytes but not latency | NFR-490 stays red; P4's premise was wrong | Task 6 Step 3's stop rule; the A/B/C split | stop before merge; the lead decides replan vs proceed (`delivery-process.md` §3) |
| A pass inside one stdev | a pass booked on noise | the margin statement's reading column | recorded as a watch item; SL-1259 measures on the dedicated host |
| A contended measurement | a slow figure booked as a pass or a fail | the slot reads, `uptime`, the `pgrep` line | discard and re-run in a new window |
| The rulings differ from the recommendations | Tasks 2–5 test the wrong content | activation needs 2 and 4; Task 0 Step 2 | method-only difference: the dispatch record names it. Acceptance difference: a superseding `PL-` |
| OQ-1373 is not ruled (its ruling's mint closes it) | DP-F35-3 cannot be ruled; Acceptance 9 has no reading | activation need 2's `grep -c 'sampled-trace schema'` | unmet; the lead raises it with the decision-maker |
| A rolling deploy mixes old-wire and new-wire workers | an off-path reproduction compares two wires (P11) | the reproduction check (`traces.py:198-272`) records `mismatch` | Acceptance 6 makes equality hold by test; a `mismatch` in production is a finding, not noise |
| `SL-1340` or the `RL-1343` rule-4 slice reaches `_build_trace` or `TraceStep` first | a merge on the same function | Task 0 Step 4 | serialise; the second merges `main` and re-gates |
| The DB stack is absent | mass fixture errors that look like failures | an `ERROR` at setup, not a `FAILED` assert | bring the stack up and re-run; an error at setup is never quoted as a red |
| Persisted traces from before the change keep the full context for 13 months (FR-259) | two readings in one store | DP-F35-1 (iv) | accepted under (iv) (a); a later `05` consumer states its need |

## Proposed SL row (the lead mints it; not added here)

````markdown
#### SL-<n> — WK-1178 slice — F35 remedy: what the trace records per node, and NFR-490's trace overhead (PL-<id>)

```yaml
id: SL-<n>
family: slice
title: WK-1178 slice — F35 remedy: what the trace records per node, and NFR-490's trace overhead (PL-<id>)
status: draft                   # draft → active → closed | retired (§1.2a)
created: <mint date>
owner: planner                   # cut by the planner (draft); lead dispatches (active)
tree: <mint tree>
phase: P2
work: WK-1178
corrected_by: []
relates: [PL-<id>, RL-862, CR-1247, FD-1246, SL-1259]
```

The scoring trace records, per node, the values its step reads and declares, not the engine's
accumulated context, and the engine is wired so that it carries only those values (register
F35 and F55; FD-1246; `CR-1247` Proposals 3 and 11). R3 is held by a frozen base corpus.
NFR-490 is measured red at the base and again after, as evidence; the verdict is SL-1259's,
whose NFR-490 limb depends on this slice. NFR-500 is re-measured here. Runs after `SL-1360`
and `FD-1357`'s fix on WK-1178, and after `SL-1345` (shared `runtime.py` and `score.py`
functions). Leaf plan `PL-<id>`.
````

## Size

Medium. About 90 lines of production change across `references.py` (new), `compile.py`, `runtime.py` and
`score.py`, a docstring, and about 200 lines of tests. Before activation: one ruling sitting
(DP-F35-1 to -3) and one spike plus a ruling (DP-F35-4). In the slice: two solo windows of
about 25 minutes and 50 minutes (five runs per tree), and one full gate (a gate slot under `RL-1263`).

## Hand-off

- **To the lead:** record in SL-1259's next dispatch record that its NFR-490 limb depends on
  this slice (the maintainer's 09:00:44 entry: "named both ways"). This plan names it here and
  in the SL row.
- **To the auditor:** P5 as a proposed finding: FR-246 ("cannot reference anything outside
  their declared inputs") is not enforced, and `passThrough` made undeclared references
  resolve; this slice's reference set makes them work without `passThrough`, which hides the
  same gap one level down. Filing it is the auditor's; whether compile should refuse it is
  DP-F35-1 (ii)'s `OQ-`.
- **At the slice audit:** F35's, F55's and FD-1246's rows take their dispositions from the
  auditor and the lead. F37's spec half is discharged by DP-F35-3's ruling text, and its
  measurement half by Acceptance 9.
- **`RL-862`'s override clause** stays unexercised (DP-F35-6 (a)). If NFR-490 passes at
  SL-1259 on the dedicated host, whether always-capture returns is a new ruling.
- **To `SL-1340`'s dispatch:** its trace limb builds on DP-F35-1 and DP-F35-2 as ruled, and on
  `CompiledBundle.references`, which an inlined step's references must join.

## Self-review

1. **Coverage of the maintainer's decision.** DP-F35-1 is first and is the decision-maker's
   (§"Decision points"). The 7 tests run in Task 0 Step 1 and again in Task 5 Step 4. The
   measurement verdict stays with SL-1259 (Acceptance 8; §"Hand-off"). The build order is
   activation needs 5 and 6.
2. **Coverage of `CR-1247`.** Proposal 3's three facts: the shared lever (Tasks 3–4), the
   compare path (Task 5), §4.10's `own_change` (P8; Acceptance 7). Proposal 11: DP-F35-3 and
   Acceptance 9. FD-1246: DP-F35-2.
3. **The trim alone is not offered as the remedy.** P4 is cited at the DP-F35-4 row and in the
   Architecture paragraph, so M3 cannot be ruled as if it closed NFR-490.
4. **Placeholder scan.** `<n>`, `<id>`, `<mint date>` and `<mint tree>` in the SL row are the
   lead's at minting. The minted ruling ids are named at Task 3 Step 6 and Task 4 Step 3 as
   "cite the minted id". No step says "add tests" without the test.
5. **Repository literals checked at `19155b50`:** `passThrough` at `runtime.py:162`, `:256`,
   `:322`; `to_wire` at `:344`; `_INPUT_ID`/`_OUTPUT_ID` at `:55-56`; `CompiledBundle` at
   `:549-568`; `load_bundle` at `:571-602`; `_build_trace` at `score.py:700-739`;
   `build_scoring_result` at `:747-788`; `RatingOutputStep` imported at `score.py:200`;
   `TraceStep` at `scoring.py:138-155`; `zen/__init__.pyi:5-7`; `uv.lock:2786-2787`; the 7
   tests' lines (P10); `test_score_compare.py`'s three tests (`:133-171`);
   `test_rating_score.py:530-556` and its fixture (`:46-105`, `:137-150`); `BUDGET_TRACE_OVERHEAD`
   in `scripts/bench-rating.py`; `asyncio_mode = "auto"` in `pyproject.toml`; the cross-module
   test import precedent (`test_quote_input_raise_sites.py:22`).
6. **Not executed.** Unlike `PL-1359`, these samples were not assembled and run: Task 3's
   samples depend on DP-F35-1's ruling, and Task 4's wire rule on Spike S1. Each sample that
   names a fixture literal says to mirror the fixture, and each predicted red names its cause.
7. **Delta 2 (2026-10-05).** Every cite it adds was read at `5fe56b87`:
   `trace_handlers.py:98-107`; `traces.py:64`, `:143-156`, `:257`; `db/models.py:2289-2296`;
   `api/traces.py:100-116`; `errors.py:375`, `:382`; `scoring.py:187-201`;
   `backend/src/app/api/score.py:374-375`, `:444-447`; `runtime.py:74`, `:412`, `:512`, `:625`,
   `:646`; `bench-rating.py:77`, `:197`, `:953`, `:968-971`; `03:1331`. DP-F35-8 is a consequence
   of condition (i) that the ruling leaves open; the planner recommends and does not pick.

Drafted as working id 9776, allocated by the lead; minted as PL-1520 on 2026-10-08 (batch B4).
