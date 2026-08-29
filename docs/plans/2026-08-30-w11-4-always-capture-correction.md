# W11 Slice 4 — the always-capture design pins the traced fraction at 1, and NFR-RATE-1 fails on all real-time traffic (2026-08-30)

**What this is.** A correction record against
[`2026-08-29-w11-4-trace-sampling-persistence.md`](2026-08-29-w11-4-trace-sampling-persistence.md),
merged and frozen. Its Task 4B Step 5 makes a design choice — always capture a trace, discard it
when unsampled — and attaches an escalation clause to it. **The clause has fired.** This records
that, and what the measurement shows that Ruling 34 could not.

**The frozen plan is not edited** ([`README.md`](README.md): *"a filed plan is a record, not an
instruction"*, and *"do not edit a filed plan to agree with today's repository"*). This document
is its sibling, the same treatment the addendum to Ruling 31 gave that ruling.

**Record only. The remedy is the decision-maker's** (`delivery-process.md` §3), and this document
recommended none — deliberately, and see §6.

> **RESOLVED, same day, by Ruling 35** (`fdbcb90`, PR #427 —
> [`2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md`](2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md)).
> Trace *production* moves off the serving request. **§8 carries the ruling, the two safety
> conditions, the limb it does not fix, and one binding constraint on the carrier that an
> executor must read before building Slice 4's Task 4B or Slice 2's Task 2B.** §1–§7 are left
> as filed: they are the finding as raised, and the ruling corrects one of their premises.

**Tree:** `2e2da7c`, `git rev-parse origin/main`, verified equal before this was written.

**Highest ids in use, re-derived at `2e2da7c`:** FR-RATE-65, NFR-RATE-14, OQ-RATE-7.
Next free: `FR-RATE-66`, `NFR-RATE-15`, `OQ-RATE-8`.

**This document mints none of them**, raises no open question and registers no error code.

---

## 1. The clause, and that it fired

Task 4B Step 5 of the frozen plan
([`:317-331`](2026-08-29-w11-4-trace-sampling-persistence.md), read at `2e2da7c`) chose the
mechanism and wrote its own failure condition:

> **A declined or errored quote is sampled at 100 %, which means `trace=True` must be decided
> *before* the outcome is known** — the request either always requests a trace and discards it
> when not sampled, or re-scores, and re-scoring is not acceptable on a 50 ms budget. Take the
> first …

and, in the note beneath it:

> **If measurement in 4D shows always-capturing breaches NFR-RATE-1, that is a finding for the
> decision-maker, not a licence to drop the 100 % rule** — the rule is FR-RATE-42's text.

**The measurement arrived from Slice 1 before 4D ran.** That is the only part of the clause that
did not happen as written, and it does not weaken it: the clause names the finding's owner and
the thing that must not be inferred from it, both of which still hold.

## 2. The measurement, and where it currently lives

Measured on a 200-step motor structure, one machine, one run per configuration:

| | mean | p99 |
|---|---|---|
| untraced | 9.235 ms | 12.537 ms |
| traced | 75.511 ms | **103.227 ms** |

NFR-RATE-1's budget is **p99 < 50 ms**. A traced request is roughly **2x the budget**.

**Provenance, stated because it is not yet durable.** These figures come from Task 1.5's research
note, which at `2e2da7c` is **in PR #416 and unmerged** — `docs/research/` on `main` holds six
notes and none of them is Task 1.5's (`git ls-tree origin/main --name-only docs/research/`
matching `task-1-5` or `bench-rating` returns nothing). Ruling 34 already rests on the same
measurements (it quotes the two means), so this record introduces no dependency the
decision-maker has not already accepted; it says so rather than presenting them as merged fact.
**If #416's figures change before it lands, every number above changes with them and the
structural argument in §3 does not**, because §3 turns on the traced fraction rather than on the
cost of a traced request.

## 3. The finding: the design pins *p* = 1, so the breach is unconditional

Ruling 34 ([`2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md`](2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md))
does the arithmetic with the traced fraction as a **free variable**, in its own notation:

- §2: *"Let **p** be the fraction of real-time requests traced"*, and the mixture's 99th
  percentile falls in the untraced population **iff *p* ≤ 1 %**.
- §3: with *d* the decline-and-error rate, *"**p** = **d** + 0.01(1 − **d**)"*, so *p* ≤ 0.01
  **iff *d* = 0** — *"the design admits a compliant p99 only when the decline-and-error rate is
  exactly zero."*

**Slice 4's design pins *p* at 1, and no step of the chain is optional:**

1. FR-RATE-42 requires **100 % of declines and errors** to be traced.
2. `score_one(bundle, ctx, *, trace: bool = False)` takes `trace` as an **input**; the sampling
   rule depends on the **outcome**.
3. The outcome is not knowable before scoring.
4. So the request either always requests a trace and discards it when unsampled, or re-scores —
   and Task 4B Step 5 refused re-scoring on the 50 ms budget and took the first.
5. Therefore **every real-time request runs `trace=True` and pays trace-enabled evaluation.
   Sampling decides what is *persisted*, never what is *paid*.**

**So *p* = 1, and NFR-RATE-1 fails on 100 % of real-time traffic** — at a traced p99 of
103.227 ms against a 50 ms budget — not on a 1 % sample and not on the decline population.

**Why this is stronger than Ruling 34, and in a way that ruling could not see.** Ruling 34 left
exactly one compliant point, *d* = 0. **That point is closed by the capture mechanism**: at
*d* = 0 the platform still cannot know an outcome in advance, so it still always-captures, so
*p* is still 1. **The breach is unconditional in *d*.** Ruling 34's algebra is correct about the
sampling *policy* — what gets persisted; it is the *capture mechanism* — what gets executed —
that decides who pays, and the mechanism is a plan's choice rather than a requirement's text.

**This is also independent of PR #416's outstanding attribution audit.** Nothing above turns on
which component owns the traced overhead. Only §2's magnitudes do.

## 4. What is established, and what is not

**Established:** that Slice 4's chosen mechanism traces every real-time request; that this
violates Ruling 34's own compliance condition at every value of *d*; and that a traced request as
measured is about twice NFR-RATE-1's budget.

**Not established, and not asserted anywhere above:**

- **That any deployed system has failed.** Nothing is deployed; Slice 2's endpoint is planned and
  unbuilt. This is a property of a *design on paper* meeting a *measurement*, which is the
  cheapest moment to find it and the reason the escalation clause existed.
- **That the measured figures are final.** See §2 — they are in an open PR.
- **That FR-RATE-42's 100 %-of-declines rule is wrong.** The frozen plan's own clause forbids
  reading the finding that way, and this record repeats the prohibition rather than relying on
  the reader to remember it.

## 5. Provenance of the analysis, in prose rather than as a resolvable link

The chain in §3 was raised by the planner on 2026-08-30 and the clause verified by the lead
against the merged Slice 4 plan. Its working lives in a **handover note outside this repository**
— handover material is local to the machine and session that produced it, never committed
([`README.md`](README.md)'s "Live plan state is *not* here", and the same treatment
[`2026-08-29-w11-decision-points-recovery.md`](2026-08-29-w11-decision-points-recovery.md) gave
an unfiled orientation report). **So the substance is quoted and restated here rather than
pointed at**, and every load-bearing claim was re-verified at `2e2da7c` against the artifact that
carries it: Ruling 34's *p* and *d* algebra against the ruling itself, Task 4B Step 5's wording
against the merged plan, `score_one`'s signature against
`packages/pricing-core/src/pricing_core/rating/score.py`, and the absence of a Task 1.5 note
against `docs/research/` on `main`.

## 6. Why this record recommends nothing

The handover analysis observes that the remedy space is wider than "cut the cost or amend a
budget" — that a third shape exists, removing the need to decide `trace` before the outcome is
known, so that an unsampled request never pays. **That is recorded here as part of the finding's
consequence, not as a recommendation**, and this document deliberately stops there.

Two reasons, and the second is the operative one:

- The lead's instruction on this record is *"record only; the remedy is the decision-maker's"*.
- **A planner who has proved a defect does not thereby acquire the choice of its fix.** That is
  the exact overreach the addendum to Ruling 31 corrected in
  [`2026-08-29-w11-3-batch-scoring.md`](2026-08-29-w11-3-batch-scoring.md) hours earlier: this
  role raised a citation error correctly and then picked the replacement test shape, and the
  replacement was rejected. Evidence quality does not widen a charter, and the temptation is
  strongest exactly when the evidence is strongest.

**What the decision-maker is owed, and is not given here:** whether the remedy is a change to
`score_one`'s trace mechanism, a change to what FR-RATE-42 requires be captured versus persisted,
an amendment to NFR-RATE-1's population, or something not listed — with the options and a
recommendation, from whoever's charter owns it.

> **Added after Ruling 35, because the outcome is evidence about this section rather than only
> about the finding.** The remedy ruled is *"something not listed"* — off-path re-score — and it
> is the option this record's own §3, quoting the frozen plan, had already dismissed. Had this
> record recommended, it would have recommended from the same three shapes the plan was reasoning
> inside, and the answer was outside them. **The reason for not recommending was a charter rule,
> and it happened also to be the reason the recommendation would have been wrong** — a planner
> deep enough in a design to prove a defect in it is, for that same reason, poorly placed to
> pick its remedy.
## 7. What this does not change

- **Slice 4's other three tasks are untouched.** 4A (the row-plus-blob store), 4C
  (`GET /api/v1/traces` and its access control) and 4D (the NFR-RATE-12 projection) do not depend
  on the capture mechanism. Only 4B's Step 5 wiring does, and its Steps 1–4 — the pure sampling
  decision function and its boundary tests — stand as written.
- **Ruling 25 is untouched.** Batch contributes nothing to the sampled production stream, and
  `score_batch` takes no sampling policy. The finding above is about the real-time path only.
- **Ruling 23 is untouched.** The storage shape, the one-serialisation constraint and the
  retention floor are unaffected by when a trace is captured.
- **Slice 2's plan is untouched but is where this lands.** Its Task 2B builds the route that would
  do the always-capturing, and its Task 2D measures NFR-RATE-1 at the full HTTP path. Whichever
  remedy is ruled, Slice 2 is the slice that implements it.

## 8. Resolved by Ruling 35 — and it corrects a premise of §3

**Ruled** (`fdbcb90`, PR #427): *"trace **production** is decoupled from the serving request."*
The quoting path scores **untraced** and responds; where FR-RATE-42 requires a trace — every
decline, every error, the sampled fraction — it is produced by re-scoring the same Quote Context
against the same **pinned** bundle, off the request path. **FR-RATE-42's 100 % rule is not
weakened and no requirement is amended.**

### 8.1 The premise of this record that the ruling corrects

§3 above reproduces Task 4B Step 5's chain, and step 4 of that chain is where the plan went
wrong — not in the arithmetic, which stands, but in the option it eliminated. The plan wrote:
*"re-scoring is not acceptable on a 50 ms budget."* Ruling 35 §2:

> That is true of a re-score performed **inside** the request — and the option it chose instead
> is worse on the same metric, for every request rather than a fraction. … The dismissal treated
> "re-score" as necessarily synchronous; nothing requires that.

| | request-path cost | share of traffic breaching 50 ms |
|---|---|---|
| Always capture and discard (the plan's choice) | traced, p99 103.2 ms | **100 %** |
| Synchronous re-score on decline | untraced, plus traced for declines | *d* + sample |
| **Off-path re-score (ruled)** | **untraced, p99 12.5 ms** | **0 %** |

**The comparison that was never made is the third row.** NFR-RATE-1 bounds what the *serving
request* costs, and a trace produced after the response has been sent is not in its population.

**This is a sharper defect than the one this record was filed to raise**, and it is worth naming
as such rather than letting the resolution read as vindication. §3's finding — that *p* = 1 makes
the breach unconditional — is correct and is what the ruling acts on. But the reason *p* = 1 was
a dismissal made against no baseline: the plan rejected an option for costing more than nothing,
rather than comparing it to the option it took. **A rejected alternative with no stated
comparator is not an eliminated one**, and the eliminated one here turned out to be the answer.

### 8.2 The two safety conditions, both load-bearing

- **(a) The re-score addresses the *pinned* bundle, never the live one.** `ScoringResult` already
  carries `rating_version_ref` and `bundle_hash`; the re-score uses both. A trace produced
  against a later bundle documents a quote that was never served — *"the failure mode is silent
  and it is an audit failure, not a performance one."*
- **(b) The re-score verifies it reproduced the served quote, and says so when it did not.** The
  persisted trace is checked against the premium actually served and a mismatch is **recorded,
  not swallowed**; FR-RATE-43's *"exact for money"* is the available standard. *"A trace that
  silently does not match the quote it purports to explain is worse than no trace."* The ruling
  notes this also converts the cross-process determinism assumption into a check, which matters
  because NFR-RATE-7's *"across machines and platform versions"* limb is only partly evidenced.

### 8.3 What the ruling does not fix — do not book NFR-RATE-2 as satisfied

**NFR-RATE-2 remains failing.** It is a per-request ratio, so it is violated wherever a trace is
produced at all, on-path or off. Moving the cost off the request path removes it from
NFR-RATE-1's population; **it does not make tracing cheaper.** Roughly *d* + 1 % of requests
still pay a ~8.2× traced cost, off-path.

So the remedy **discharges the NFR-RATE-1 limb and leaves the NFR-RATE-2 limb open**, still gated
on PR #416's owner question. Ruling 34 §4's remaining candidates apply to that limb alone. This
record's §4 already refused to claim more than was established; the same discipline applies to
the resolution, and the ruling states plainly why: *"a remedy that fixes one and is reported as
fixing 'the interaction' would leave NFR-RATE-2 booked as delivered."*

### 8.4 Binding constraint on the carrier — the Quote Context must not travel in `JobRow.parameters`

Ruling 35 routed a governance question to the lead and it is answered. **This is the clause an
executor is most likely to breach by taking the obvious route**, because putting the context in
the Job payload is the natural way to hand work to a worker.

**Why it is forbidden**, re-verified here at `fdbcb90` rather than taken from the ruling:

- `Job.parameters: dict[str, Any]` is a **returned** field of the API model —
  `packages/model-schema/src/model_schema/jobs.py:220`.
- `get_job` returns that `Job` — `backend/src/app/api/jobs.py:164-168`.
- `_load_scoped` (`backend/src/app/api/jobs.py:91`) scopes a read by **workspace only**:
  `if row is None or row.workspace_id != caller.workspace_id`.

So that carrier would place full quote inputs on a surface whose access control was designed for
job metadata. **NFR-RATE-11 forbids exactly this:** *"quote inputs are never logged in full
outside sampled traces, **which are access-controlled**"* — and Slice 4's Task 4C is what builds
that separate control. The distinction the ruling draws is precise: it is **not a new class of
exposure, it is a different access control**.

**Required instead.** At serve time, persist into the access-controlled trace store a **pending
row** carrying the Quote Context, `rating_version_ref`, `bundle_hash` and the **served premium**;
the Job payload carries **only that row's id**. The re-score fills in the body.

**This costs nothing extra**, which is what makes it the right shape rather than a tax: condition
(b) already requires the served premium to be stored somewhere for the reproduction check, so
**the row that solves the access-control problem is the row condition (b) needed anyway.**

### 8.5 Where this lands

- **Slice 4 Task 4A** — the row gains a pending state and the fields above. Its
  one-serialisation constraint (Ruling 23) is unaffected: the pending row is written at serve
  time and the body at re-score time, which are already two writes.
- **Slice 4 Task 4B** — Step 5's wiring is replaced. The sampling decision function of Steps 1–4
  is unchanged, but it now selects what is **re-scored**, not what is **captured**.
- **Slice 2 Task 2B** — the serving route scores **untraced** and writes the pending row. It
  never sets `trace=True`.
- **A capacity fact the ruling records and nobody had costed:** always-capture is ~8.2× CPU on
  all traffic, so sustaining NFR-RATE-1's 200 rps per replica would have needed roughly **eight
  times the fleet**. The remedy removes that.

## 9. Verification

- **Tree:** `2e2da7c`; `git rev-parse HEAD` equal to `git rev-parse origin/main`, clean working
  tree, `git fetch origin` first.
- **Ruling 34's algebra was read at source, not from the relay that reported it.** §2's *"Let
  **p** be the fraction of real-time requests traced"* and §3's *"**p** = **d** + 0.01(1 − **d**)"*
  were quoted from
  `docs/plans/2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md` — the claim that the ruling
  treats the fraction as a free variable is the whole basis for calling this finding stronger, so
  taking it on report would have been the defect this record is about.
- **Task 4B Step 5's wording** was read from the merged Slice 4 plan at `:317-331`, and the
  escalation clause quoted verbatim rather than paraphrased.
- **The measurement's non-merged status** was established by listing `docs/research/` at
  `origin/main` and by `gh pr view 416 --json state` returning `OPEN`, not by assuming from the
  commit log.
- **Ruling 35's three code claims behind the carrier constraint (§8.4) were re-read at
  `fdbcb90`, not adopted from the ruling**: `parameters: dict[str, Any]` as a field of the `Job`
  API model (`model_schema/jobs.py:220`), `get_job` returning `Job`
  (`backend/src/app/api/jobs.py:164-168`), and `_load_scoped`'s workspace-only predicate
  `row.workspace_id != caller.workspace_id` (`:91`). The constraint is binding on an executor,
  so its premises are checked here rather than cited.
- `python3 scripts/audit-docs.py` — clean, run before commit.
- Mints no id and raises no `OQ-`, so it owes no [`../open-questions.md`](../open-questions.md)
  mirror row and no [`../roadmap.md`](../roadmap.md) §10 gate row.
