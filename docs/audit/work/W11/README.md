# Work-item record — W11 (Scoring)

**Re-opened in part 2026-08-30 — see §9. §§1–8 are the record as at close and are not
amended.**

**Closed 2026-08-30 as a reduced-scope close.** Scope and evidence audited against
`origin/main` `97965be`.

**Read the two sentences below before the tables, because a close is easy to misread as a
delivery.**

**W11's named hard target, NFR-RATE-1, is measured and failing** — not unmeasured, not
marginal. **Three of its ten functional requirements were never started**, because the
maintainer stopped the workstream at the end of Slice 2. This record closes W11 on what it
actually delivered and reassigns the rest with named owners; it does not report scoring as
complete.

**Closed under a delegation.** `CLAUDE.md` §12 reserves acceptance of a Work close to the
maintainer. On 2026-08-30 the maintainer delegated this one to the lead — *"I have already
authorised you to decide W11 close"* — recorded alongside the adoption's delegation in
`docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md` §1.1. The delegation is read narrowly:
it covers this close, not W12 and not any later phase.

---

## 1. Scope, derived from the specification first

`docs/specs/03-rating-engine.md` **§3.7 Scoring** and **§3.8 Trace, testing and promotion
evidence** contain **thirteen** requirement ids: FR-RATE-34..45 and FR-RATE-64.

The roadmap's W11 row names **ten**: `FR-RATE-34..42, FR-RATE-64`.

**The row is right and the section boundary is the wrong scope line.** `FR-RATE-43..45` —
Golden Quotes, the Regression Suite, the Quote Sandbox — are named explicitly in **W12's own
row** (`docs/roadmap.md:377`, "Testing: golden quotes, property assertions, regression runs |
FR-RATE-43..45"). §3.8 straddles two workstreams: FR-RATE-41 and 42 (trace) are W11's, and 43
to 45 (testing) are W12's. No correction to either row is needed; this paragraph exists
because deriving from the section heading alone would have over-scoped W11 by three
requirements, and the next reader will make the same derivation.

**W11's scope is therefore:**

- **Ten FRs** — FR-RATE-34 to 42, and FR-RATE-64.
- **Three NFRs named in the row** — NFR-RATE-1 as "the hard target", joined by NFR-RATE-13
  and 14, carried forward from W9 via register row F-W9-1.
- **Five further NFRs the work actually touched, claimed by no row** — NFR-RATE-2, 9, 10, 11
  and 12. They are verdicted here rather than left silent; §3 records which of them is a
  roadmap gap rather than a delivery gap.

## 2. What was delivered, by slice

Slice 1 completed in full. Slice 2 completed in full. **Slices 3 and 4 were never started.**

| Slice | PR(s) | Delivered |
|---|---|---|
| **1 — evaluator core** | #406, #415, #416, and Task 1.1 at `0d942b3` | `CompiledBundle`, `load_bundle`, JDM wire translation, `score_one` on `async_evaluate()`, the bare-metal latency harness, Ruling 28's maturity check |
| **2 — real-time scoring endpoint** | `378483d`, #443, #446, #452 | `NO_LIVE_RATING_VERSION` and the per-worker bundle slot; `POST /api/v1/score` with bundle resolution and Service Account enforcement; the blank-change-summary guard and its documented 422; **the full-path NFR-RATE-1 measurement** |
| **3 — batch scoring** | — | **nothing.** Plan filed (`docs/plans/2026-08-29-w11-3-batch-scoring.md`), every blocking decision ruled (D6, Rulings 31/32), no code |
| **4 — trace sampling and persistence** | — | **nothing.** Plan filed (`docs/plans/2026-08-29-w11-4-trace-sampling-persistence.md`), Rulings 34/35 and the always-capture correction landed, no code |

Slices 3 and 4 inherit **plans and rulings and no code**. That is a good state to hand on and
it is not a delivery.

## 3. Requirement verdicts

Every requirement gets one of §13's four verdicts. Silence is not one of them.

### 3.1 Functional requirements

| Requirement | Verdict | Evidence |
|---|---|---|
| **FR-RATE-34** | **delivered and tested** | Real-time scoring of one quote. 5 markers, `backend/tests/test_score.py:123,146,162,…`. Three limbs (F43): L1 ref resolution and L2 explicit ref delivered; **L3, the p99 budget, is NFR-RATE-1 and it fails — see §3.2** |
| **FR-RATE-35** | **delivered in part; the remainder deferred with an owner (W14)** | Explicit `rating_version_ref` delivered and tested, 1 marker at `test_score.py:527`. The requirement's other content is **one** restriction, not two — approved-only *and* a rewritten `what_if` purpose both sit inside its own `prod` clause, and W11 has no environments. Deferred deliberately by **Ruling 14 clause 3**, documented three ways (the ruling, `score.py:226-229`, the test docstring). Not a bare gap |
| **FR-RATE-36** | **not started** | Batch scoring route `POST /api/v1/score/batch`. Zero markers. No route registered, no `SCORE_BATCH` job kind. Slice 3 never ran |
| **FR-RATE-37** | **not started** | Chunked, resumable, progress-reporting batch. Zero markers. **`def score_batch` exists nowhere in the tree**; `pricing-core/rating/score.py:8` says so in terms — *"not built here"*. **This is 0 of 3 limbs built, not "2 of 3 broken"** — an earlier reading in the backlog said the latter and was wrong: nothing exists to be broken |
| **FR-RATE-38** | **delivered and tested** | Error taxonomy on the scoring path. 8 markers, the best-evidenced requirement in the workstream |
| **FR-RATE-39** | **delivered and tested** | 4 markers across `backend/tests/test_score.py` and `pricing-core/tests/test_rating_score.py` |
| **FR-RATE-40** | **delivered in part; three limbs reassigned** | The approval-evidence gate, 1 marker at `test_rating_versions.py:270`. F44's four limbs: the gate is W11's and delivered; the **regression-suite** limb is **W12's**, the **dislocation-run** limb is **W13's**, and the **GIPP** limb is a permission with no failing case — untestable until something exercises it |
| **FR-RATE-41** | **delivered and tested** | Trace production. 1 marker at `pricing-core/tests/test_rating_score.py:494`, **stacked with NFR-RATE-2** — see §3.2 for why that stack matters |
| **FR-RATE-42** | **not started** | Production trace sampling. Zero markers. Slice 4 never ran. **Its own amendment already settles the batch question** (2026-08-29): batch contributes nothing to the sampled stream, so `score_batch` takes no sampling policy |
| **FR-RATE-64** | **delivered and tested** | 3 markers in `pricing-core/tests/test_rating_score.py` |

**Seven of ten evidenced; three not started.** The three are FR-RATE-36, 37 and 42 — the whole
of batch scoring and the whole of production sampling.

### 3.2 Non-functional requirements named in the row

| Requirement | Verdict | Evidence |
|---|---|---|
| **NFR-RATE-1** | **measured and FAILING — the workstream's named hard target** | Task 2D (#452, `98eca40`), `docs/research/w11-task-2d-nfr-rate-1-full-path.md`. `_fetch_bundle` **alone** costs p99 **66.294 ms** against a **50 ms whole-request** budget on a 2,039,114 B bundle; without GBM, p99 **44.283 ms** against 15 ms. **Over budget at every rung from 10 rps** — 5 % of the required 200. At that rung p99 queue wait is 7.179 / 4.191 ms, so **the cause is fetch, not saturation and not the box**. Resolving *which* bundle to score costs about **three times** what scoring it costs |
| **NFR-RATE-13** | **owed, not delivered** | Bounded but **not isolated**. The ~12 ms residual after subtracting fetch and `score_one` from the handler mean contains framework, routing, auth, DI *and* serialisation. An upper bound containing four other things is not a measurement of the one, and booking it against W8's 0.070 ms would be a synthetic-for-real substitution. The executor declined to report it as delivered; that judgement is adopted |
| **NFR-RATE-14** | **delivered** | Measured in W8: p99 1.626 ms, 3.3 % of its budget. 2 markers |

### 3.3 Non-functional requirements the work touched, claimed by no roadmap row

| Requirement | Verdict | Evidence |
|---|---|---|
| **NFR-RATE-2** | **split: correctness delivered and tested; latency measured and failing** | 1 marker at `test_rating_score.py:494-495`, which correctly checks the R3 clause (traced-vs-untraced equality). The **≤ 20 % latency clause has zero assertions anywhere** and is measured at **+723 %**, over by ~36×. See F35's 2026-08-30 correction: `req-coverage.py` has no per-clause granularity, so one marker on a two-clause requirement reads as whole coverage |
| **NFR-RATE-9** | **degradation delivered and tested; availability limb deferred with an owner (W14)** | 5 markers including an end-to-end HTTP degraded read at `test_score.py:587`. The 99.95 % monthly target is unmeasurable pre-deployment — no measurement code for it exists anywhere. See F41's 2026-08-30 amendment |
| **NFR-RATE-10** | **delivered and tested, and unplanned** | Audit events on compile, `e16c459`, marker at `test_rating_version_compile.py:655`. **It appears in no plan and no roadmap row** — the scope derivation found it, not the plan. Recorded here rather than as a register row, because the register holds open findings and this is closed |
| **NFR-RATE-11** | **two clauses of four delivered and tested; one not started; one ruled** | 3 markers at `test_score.py:214,231,563`, all exercising **authentication and scoped credentials**. The **per-client rate limit is enforced by nothing** — `rate_limit_rps` is written, stored, returned and consulted by nothing; `RATE_LIMITED` is registered and raised nowhere in `src/`. Register row **F48**. The quote-input-logging clause is settled by **Ruling 36** |
| **NFR-RATE-12** | **not started** | Trace storage under 200 GB/year at 1 % sampling. Zero markers, and it cannot be evidenced before FR-RATE-42 exists — sampling is what it measures |

**A roadmap gap, not a delivery gap.** NFR-RATE-2, 9, 10, 11 and 12 were all worked on inside
W11 and are named by no workstream row. That is the same class as FR-RATE-65 (Ruling 30):
evidenced and claimed by nobody. It is recorded here and **not** corrected in the roadmap by
this close, because assigning five NFRs to rows is re-planning and re-planning is not a
close's to do.

## 4. NFRs measured, not asserted

`CLAUDE.md` §13 requires NFRs to be measured and enforcement proven on deliberately broken
input. What this workstream actually measured, with its own limits stated:

| | measured | budget | verdict |
|---|---|---|---|
| NFR-RATE-1, fetch alone, with GBM | p99 **66.294 ms** | 50 ms *whole request* | **FAIL** |
| NFR-RATE-1, fetch alone, without GBM | p99 **44.283 ms** | 15 ms *whole request* | **FAIL** |
| NFR-RATE-2, traced vs untraced | **+723 %** | ≤ 20 % | **FAIL**, ~36× over |
| NFR-RATE-14 | p99 1.626 ms | 50 ms | pass, 3.3 % of budget |

**Limits, from the measurement's own record and not softened here.** One pass. The 200 rps
rungs are **void** — the load generator itself fell behind, issuing 149.5 and 142.1 against
200 offered — and are kept rather than deleted so the failure is visible. The two GBM
conditions ran under different load and are comparable each to its own budget, not to each
other. No hydration, no cold start, synthetic fixture.

**Per F38's own standard this is *measured*, not *established*** — each figure is one
observation. **A fetch p99 of 66 ms against a 50 ms whole-request budget is not a margin that
repetition reverses**, and the record says exactly that rather than overclaiming or hedging.

## 5. Why NFR-RATE-1's failure does not block the close

It is the workstream's named hard target and it fails, so this needs stating rather than
assuming.

**The failure is not in what W11 built.** `score_one` on the real fixture costs mean 12.326 ms
— comfortably inside the budget. The cost is in `_fetch_bundle`, which resolves a `ref` to the
*currently live* bundle on every request: two `SELECT`s, a full object-store read, and a
`Bundle.model_validate_json` over 2 MB.

**That is a deliberate correctness choice with an unmeasured cost, not a broken cache**, and it
must not be recorded as one. The `slot.hash_for(ref)` memo that would skip the fetch is wired
to the NFR-RATE-9 degradation branch and **cannot move to the happy path as it stands** — a
re-pointed ref would then serve a stale bundle. Correctness traded for latency, silently.

**So the remedy is an architectural ruling, not a fix inside W11's scope**, and holding the
workstream open for a decision nobody has taken would not produce it. What W11 owes is the
measurement that makes the decision possible, and it delivered that. **The failure is carried
forward with a named owner** (§6).

## 6. Open findings and their resolutions

`CLAUDE.md` §14 requires every open finding to be listed here with its resolution.

| Finding | Resolution |
|---|---|
| **NFR-RATE-1 fails at the full path** | **carry forward, owner: an architectural ruling before W14 deployment.** The question is whether a `ref` may be served from a memo without a metadata read, and what staleness window that admits. Register row owed at the next register pass |
| **NFR-RATE-13 owed, not delivered** | carry forward with the same owner — isolating it needs the same instrumentation an NFR-RATE-1 remedy would add |
| **NFR-RATE-2 latency, +723 %** | carry forward. F35, corrected 2026-08-30. Remedy gated on Ruling 35's off-path capture |
| **FR-RATE-36, 37, 42 not started** | **reassigned** — a future batch-scoring slice (36, 37) and a future sampling slice (42). Both have filed plans and complete rulings; neither has a workstream row yet, and creating one is re-planning |
| **NFR-RATE-12 not started** | reassigned with FR-RATE-42; it cannot be evidenced before sampling exists |
| **NFR-RATE-11's rate limit (F48)** | carry forward, provisionally W14 — a limit enforced in one replica's memory is not a limit |
| **F41, F35 stale rows** | **fixed** 2026-08-30 (#454), as dated amendments quoting what they supersede |
| **F45, F46, F47, F48** | filed 2026-08-30 (#447); all carry forward unowned or with the owners stated in their rows |
| **F49 session links** | **accepted with an instrument** — the maintainer's ruling; squash-time strip, landed in `delivery-process.md` §15 and `git-hygiene` |
| **F27(c), F29, F33 — one gate-coverage item** | **F33 materially advanced** by `c8d3c81`: mypy now covers the test trees and reports no issues over 163 files. **F27(c) and F29 remain open**, and the NT-0014 adoption record names them so a later reader cannot mistake silence for a decision |
| **The §14 plan review** | **runs with this close** — see §7 |

## 7. §14 plan review

`CLAUDE.md` §14 triggers a plan review at each workstream close. It runs here, and its output
is a proposal, never a change.

**Question 1 — do the phase boundaries still make sense?** Yes, with one observation. The
W11/W12/W13/W14 cut held: FR-RATE-40's four limbs distributed cleanly across exactly those
workstreams, which is evidence the boundary was drawn on something real.

**Question 2 — do the workstream cuts?** **No, for W11 specifically.** Four slices in one
workstream, where slices 3 and 4 depend on slice 1 and on nothing else, meant a stop after
slice 2 left two independent bodies of work unstarted rather than one workstream part-done.
**Proposal: batch scoring and trace sampling should each have been their own workstream.**
Recommendation only.

**Question 3 — does the requirement set still make sense?** One real problem. **Five NFRs
were worked on inside W11 while being claimed by no roadmap row** (§3.3). This is the third
instance of the class — FR-RATE-65 and FR-RATE-64 preceded it. **Proposal: the roadmap's
workstream rows should name NFRs explicitly**, since the current rows name FRs by range and
NFRs only when someone remembers.

**Question 4 — does the spec still describe the code?** Yes, with the corrections already
landed this session: `delivery-process.md`'s own `CLAUDE.md` back-reference (§12 → §15) and
FR-RATE-26's citation of FR-RATE-31 where it means FR-RATE-53 — **the latter is still
outstanding**, two characters, owed at the next docs pass.

**Question 5 — what did running the plan teach?** That a measurement task can be the most
valuable thing in a workstream. Task 2D produced no feature and settled the question the whole
workstream existed to answer.

**Acceptance line:** accepted by the lead, 2026-08-30, under the delegation recorded in
`docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md` §1.1.

## 8. Close

**W11 is closed 2026-08-30 as a reduced-scope close**, on seven of ten functional requirements
delivered and tested, three not started and reassigned, and its named hard target measured and
failing with the failure carried forward to an architectural ruling.

Accepted by the lead under the maintainer's delegation of 2026-08-30.

## 9. Reopened 2026-08-30

**This section is a change of scope, not a correction of belief.** §§1–8 above are the record
of what was believed and evidenced at the 2026-08-30 close and are neither corrected nor
withdrawn by anything below.

**The direction, quoted and dated.** Received by the maintainer in the message opening this
session, 2026-08-30, recorded verbatim in
[`docs/plans/2026-08-30-w11-reopen-direction.md`](../../../plans/2026-08-30-w11-reopen-direction.md)
§1 (filed by the decision-maker, because the dispatch that requested the governing rulings
asserted the direction as fact and no artifact in the tree carried it until that record):

> *"read handover in /home/puzhenhao1989/gi-pricing-plan.local, spawn the team; landing
> NT0012, 13 and 14; reopen the uncompleted W11, follow the process to the end of W11"*

**Scope of the reopen**, fixed by
[Ruling 39](../../../plans/2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md#ruling-39--w11-is-reopened-under-its-own-id-the-closure-record-is-appended-to-never-amended-and-the-roadmaps-status-marker-moves-while-its-close-note-stays-verbatim)
§1: **FR-RATE-36, FR-RATE-37, FR-RATE-42**, and — riding with FR-RATE-42 — **NFR-RATE-12**,
which §6 above tied to it. **Adoption slices E, F and G are not part of this reopen**; they
continue under `docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md`, a separate Work with its
own filed record and its own bounded delegation.

**§6's resolutions superseded, named exactly.** For the four rows above — FR-RATE-36, 37, 42
and NFR-RATE-12 — §6's *"reassigned — a future batch-scoring slice (36, 37) and a future
sampling slice (42)"* (and, for NFR-RATE-12, *"reassigned with FR-RATE-42; it cannot be
evidenced before sampling exists"*) is **superseded**: the work is back under W11 rather than
awaiting a future slice's workstream row. No other row of §6 is touched by this section.

**§6's NFR-RATE-1 carry-forward row is discharged, not resolved as passing.** §6 recorded:
*"carry forward, owner: an architectural ruling before W14 deployment. The question is whether
a `ref` may be served from a memo without a metadata read, and what staleness window that
admits."*
[Ruling 41](../../../plans/2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md#ruling-41--a-ref-may-not-be-served-from-the-memo-without-a-metadata-read-and-it-does-not-need-to-be-the-content-hash-is-already-in-hand-after-the-first-read-and-is-discarded)
answers that question — **a `ref` may not be served from the memo without a metadata read, and
it does not need to be**, because the version row's `content_hash` is already read and
discarded on the very first statement of `_fetch_bundle`, before the expensive blob read and
2 MB parse the measurement's cost sits in. That discharges this carry-forward row: the
architectural question §6 named an owner for has an answer.

**Read honestly: this is not a fix and NFR-RATE-1 is not shown reachable.** Ruling 41 mints no
requirement id, amends nothing in `docs/specs/`, and is explicit that its own shape *"does not
establish that NFR-RATE-1 passes."* With the fetch's dominant cost already excluded, the
without-GBM limb's own component re-measure reads **p99 23.027 ms against a 15 ms budget** —
over. Ruling 41 §4 names this as "the requirement's own half" still in the dock, and states
that if a re-measurement with the blob read actually removed still fails that 15 ms limb, that
failure is the trigger for a further decision on NFR-RATE-1 itself — not answered here, not
assumed here. NFR-RATE-1's remediation (the code change Ruling 41 §2 describes) is, per
`docs/plans/2026-08-30-w11-reopen-direction.md` §3, explicitly **not** decided as part of this
reopen's scope; that is a maintainer question, raised and not settled.

**Register rows filed alongside this reopen**, both concerning code and a research artifact
this record's own evidence rests on, neither superseding anything in §§1–8:
[`docs/audit/register.md`](../../register.md) F50 (the `bundle_slot.py:28-31`
immutability argument Ruling 41 §3 found wrong as stated) and F51 (a false premise in
`docs/research/w11-task-2d-nfr-rate-1-full-path.md:74-75` that Ruling 41 §2 refutes).

**The re-close, when the reopened work finishes, is `## 10. Second close`, appended here** —
audited under `close-workstream` against the reopened scope only (FR-RATE-36, 37, 42,
NFR-RATE-12, and NFR-RATE-1's disposition), re-verdicting none of the seven requirements
closed on 2026-08-30, and accepted by the maintainer with a fresh dated line — the 2026-08-30
delegation does not reach it (Ruling 39 §5).

## 10. Second close

**Audited against `origin/main` `b749acb`** (Ruling 39/42's reopened scope: FR-RATE-36,
FR-RATE-37, FR-RATE-42, NFR-RATE-12, and NFR-RATE-1's disposition). §§1–9 above are not
edited by this section (Ruling 39 §2, Ruling 42 §6) — verified: the only two commits ever to
touch this file are the original close (`1da81cd`) and the §9 reopen append (`8fd48b7`), and
their diff adds a banner line and appends §9 with zero removed lines.

This audit ran the `close-workstream` checklist as carried in this tree at `b749acb`. Per
the constraint given for this task, the full `pytest` suite was not re-run — CI is green on
every merged commit in the range; the targeted suites below were run directly instead.

### 10.1 Scope, derived from the specification first

`scripts/scope-audit.py RATE --sections 3.7,3.8 --extra
FR-RATE-36,FR-RATE-37,FR-RATE-42,NFR-RATE-12` confirms Ruling 39 §1's four-item list against
`03-rating-engine.md` directly: 14 requirements in scope under that section/extra
combination, all four reopened ids evidenced by marker. The three `NO EVIDENCE` ids the same
run reports (FR-RATE-43/44/45) are W12's, per §1 above — correctly outside this scope, not a
gap in it.

### 10.2 Requirement verdicts

| Requirement | Verdict | Evidence |
|---|---|---|
| **FR-RATE-36** (batch scoring route) | **delivered and tested** | `POST /api/v1/score/batch` (`backend/src/app/api/score.py:394`, Task 3C, `3dc8d6b`/#475) submits a `score.batch` Job and nothing else. 1 marker, `backend/tests/test_score_batch_api.py:143`. `--endpoints` confirms the route is published in the generated contract (absent from the missing-endpoint list) |
| **FR-RATE-37** (chunked, resumable, progress-reporting batch) | **delivered and tested** | `score_batch` (`packages/pricing-core/src/pricing_core/rating/score.py:979`, Task 3A, `59407f2`/#465) is a pure chunked transform taking a `ProgressCallback`; the `score.batch` worker handler (Task 3B, `eda70d6`/#471) drives it. 4 markers: `packages/pricing-core/tests/test_rating_score_batch.py:156,203`, `backend/tests/test_scoring_handlers.py:193,397` |
| **FR-RATE-42** (production trace sampling) | **delivered and tested** | `decide_sampling` (100 % of declines/errors, configured rate otherwise) and off-path trace production per Ruling 35's correction (Task 4B, `003f9d4`/#485); trace rows and migration (Task 4A, `25c5688`/#480); `GET /api/v1/traces` and its access control (Task 4C, `87dd4b7`/#490). 20 markers across `backend/tests/test_traces.py`, `test_traces_api.py`, `test_score.py` |

**Targeted suites re-run this audit, not taken from CI history**: `backend/tests/test_score_batch_api.py`,
`test_scoring_handlers.py`, `test_traces.py`, `test_traces_api.py` — 53 passed; `packages/pricing-core/tests/test_rating_score_batch.py` — 11 passed. Zero failures, zero skips.

**All three of the reopen's FRs: delivered and tested.**

### 10.3 NFR-RATE-12 — measured, not asserted

| | measured | budget | verdict |
|---|---|---|---|
| NFR-RATE-12, blob storage at the ~200-step reference structure | 516.07 GB/year | 200 GB/year | **PROJECTED OVER, ~2.58×** |
| NFR-RATE-12, row storage (upper-bounded) | 0.23 GB/year | — | negligible, does not change the verdict |

Task 4D (`docs/research/w11-task-4d-nfr-rate-12.md`, `dc451d5`/#501, `scripts/bench-trace-size.py`)
measures real serialised `Trace` bytes (no estimate) at five step counts and multiplies the
~200-step reference figure (1,032,137 B) by NFR-RATE-12's own stated volume (500,000 sampled
quotes/year). **The projection is conservative, not an upper bound**: it excludes
FR-RATE-42's 100 % decline/error sampling floor, so real persisted volume is higher than
this figure, not lower. 1 marker, `backend/tests/test_traces.py:316`.

**One correction owed, folded in below rather than opened as a separate PR** (the lead's
relayed instruction called it non-blocking): the note states the exclusion, and therefore
that 2.58× is conservative, only in a §5 caveat-list bullet, thirteen lines below the
headline and result table. A reader who stops at §0 or §4 can misread 2.58× as an upper
bound. **Fixed in this PR** — see 10.7.

**Register disposition — F55, largest driver of the overage.** `TraceStep.consumed`/
`.produced` (`pricing_core/rating/score.py:660`) carry the zen-engine's full accumulated
per-node context, not each step's own declared `consumes`/`produces` — found by Task 4D
(§2 of its note) and filed as its own row (F55) rather than fixed, since trimming it is a
schema/semantics change outside Task 4D's measurement scope. **Verdict: NFR-RATE-12 is
measured and FAILING, with its largest remediation lever (F55) identified but not applied,
and the projection is a lower bound on real production volume rather than a worst case.**

### 10.4 NFR-RATE-5 — its first verdict, split at both clauses (F52)

Absent from §3.1/§3.2 above because Slice 3 had not run at the first close — its first
verdict anywhere in this record:

| | measured | budget | verdict |
|---|---|---|---|
| NFR-RATE-5, throughput/worker | 5,093,947 risks/hour/worker | ≥ 1,000,000 | **PASS, 5.09×** |
| NFR-RATE-5, linear in workers | — | — | **NOT MEASURED** — one worker ran |

Task 3D (`docs/research/w11-task-3d-nfr-rate-5.md`, `7b4f603`/#478, real Postgres/MinIO I/O,
300,000 rows) measured the throughput clause directly against the handler and left the
linearity clause honestly unattempted, per its own acceptance standard's instruction to
"mark the linearity untested rather than implying it." Register row **F52**
(`9f116ea`/#479): carry forward, unowned — no later workstream names an owner for a
multi-worker run. This section discharges the register row's own request that "the W11
second close... needs to add NFR-RATE-5 to its NFR table for the first time, split at its
two clauses" — done above; F52 itself stays open, unowned, per its filed disposition.

### 10.5 NFR-RATE-1 — discharged, not passing

Ruling 41 answers §6's architectural question (a `ref` may not be served from the memo
without a metadata read, and does not need to be — the content hash is already read and
discarded on `_fetch_bundle`'s first statement) and Ruling 42 rules the resulting code
change **into** the reopen while explicitly ruling NFR-RATE-1's verdict **out** of it.
Verified against Task 3B's landing (`eda70d6`/#471) and its measurement note
(`docs/research/w11-3b-compiled-for-content-hash-delta.md`):

- The code change lands: `_fetch_bundle` checks a freshly re-read `content_hash` against the
  slot before touching the blob store, removing the blob PK lookup, the ~2 MB object-store
  read and the full `model_validate_json` on a hit.
- The component delta is measured with tree, host, pass count and ref cardinality all
  named, exactly as Ruling 42 §4/§6 requires: hit mean 3.657 ms vs. full-path mean
  11.637 ms, on `feat/w11-3b-batch-handler` off `59407f2`, one run, one ref, a shared 4-core
  box — explicitly **not** an NFR-RATE-1 re-measurement, on a minimal no-GBM fixture not
  comparable to NFR-RATE-1's own budget.
- **NFR-RATE-1's verdict does not move: measured and FAILING.** The without-GBM limb's own
  component re-measure (Ruling 41 §4, unchanged by Task 3B) reads p99 **23.027 ms against a
  15 ms budget**, with the fetch already excluded — over. No artifact produced this reopen
  describes NFR-RATE-1 as passing, improved to passing, or re-measured; `bundle_slot_capacity`
  is not raised. Ruling 41 §4's 15 ms trigger — the condition that would put NFR-RATE-1 itself
  in further question — is **not** treated as fired by this delta, per Ruling 42 §4's explicit
  prohibition.
- **Carry forward, owner W14**: the requirement re-measurement on a dedicated host, more than
  one pass, and any `bundle_slot_capacity`/TTL/refresh-channel change (Ruling 16 clause 4),
  unchanged from §6 except that the *architectural* question §6 named an owner for now has an
  answer — the *measurement* question does not.

**Register — F50 and F51, both resolved.** F50 (`bundle_slot.py:28-31`'s false immutability
argument) and F51 (`w11-task-2d-nfr-rate-1-full-path.md:74-75`'s false premise) were both
assigned to this same task by Ruling 42 §7 and both closed by `eda70d6`/#471 — verified
against the diff, not the commit message: the docstring now states the true safety argument
(safe because the memo is read only on the NFR-RATE-9 degradation branch, never the happy
path), and the research note carries a dated, quoting annotation at `:76-89` correcting the
premise while leaving its measured figures untouched.

### 10.6 Carried items from §6, revisited

None of these are in the reopen's requirement scope; each is checked for whether anything
in this reopen's work changed its state.

| Item | §6 disposition | This audit |
|---|---|---|
| **NFR-RATE-13** owed | carry forward, same owner | **Unchanged.** No instrumentation for isolating it landed this reopen; still owed |
| **NFR-RATE-2 latency, +723 %** (F35) | carry forward, remedy gated on Ruling 35's off-path capture landing | **Its blocking precondition is now met** — Ruling 35's off-path capture landed with Task 4B (`003f9d4`), for the production/sampled stream. **The latency clause itself is unchanged and still failing**: the explicit `ctx.options.trace=True` synchronous path (FR-RATE-41's, which is what F35 measured) is untouched by Task 4B — the commit message states this directly ("FR-RATE-41's caller-requested `ctx.options.trace` is unchanged"). Flagged rather than re-verdicted: the remedy (trimming what a trace records per node) is now unblocked and shares its lever with F55 (10.3) — nobody has connected the two, and the lead should decide whether to note the now-open gate in F35's row |
| **NFR-RATE-11 rate limit** (F48) | carry forward, provisionally W14 | **Unchanged.** `rate_limit_rps` is still accepted, persisted and returned, and consulted by nothing; `RATE_LIMITED` is still raised nowhere under `src/` |
| **F27(c), F29** (gate-coverage bundle with F33) | open, owner: the §14 review at W11's close | **Unchanged.** F33's partial landing (`3edd75a`, mypy `files` widened) predates the reopen (2026-08-29, before `8fd48b7`); nothing in this reopen's work touches error-code cross-checking (F29) or the `03` shape-vs-contract comparison (F27(c)) |

### 10.7 New findings from this audit

| Finding | Concerns | Decision | Status |
|---|---|---|---|
| **`w11-task-4d-nfr-rate-12.md`'s conservative caveat is buried** | Readability of the NFR-RATE-12 research note | fix before close | closed — one sentence added to §0's headline verdict line, cross-referencing §5's existing caveat rather than duplicating it; §5's bullet is unchanged |

No other new register rows are filed by this audit. F53 (`scoring_traces` `UPDATE`
revocation untested against `gip_app`) and F54 (Service Account key issuance mints only
`environments[0]`) were both filed earlier today against work this reopen's scope touches
or is adjacent to (Task 4A and Task 4B respectively) and are unchanged by this audit:
F53 stays **delivered but untested, carry forward unowned**; F54 stays **not started,
unowned**, attributed to `main` rather than to any W11 task.

### 10.8 Preconditions

`docs/roadmap.md`'s W11 row states two, neither waivable by the lead: every reopened slice
complete, and the auditor satisfied. On the first: Slice 3's four tasks (3A `59407f2`, 3B
`eda70d6`, 3C `3dc8d6b`, 3D `7b4f603`) and Slice 4's four tasks (4A `25c5688`, 4B `003f9d4`,
4C `87dd4b7`, 4D `dc451d5`) are all merged to `origin/main` as of `b749acb` — verified by
commit, not by plan status. On the second, see 10.9.

### 10.9 Auditor's proposed verdicts and satisfaction

**Proposed verdicts** (for the lead to adopt, amend or reject, per `CLAUDE.md` §12):
FR-RATE-36 delivered and tested; FR-RATE-37 delivered and tested; FR-RATE-42 delivered and
tested; NFR-RATE-12 measured and FAILING (~2.58× over, conservative); NFR-RATE-5 measured
and split — throughput PASS at 5.09×, linearity NOT MEASURED (F52, unowned); NFR-RATE-1
discharged architecturally, verdict unchanged — measured and FAILING, carried to W14.

**I am satisfied.** Every reopened requirement has a verdict backed by re-run tests or a
measurement note read to its own numbers, §§1–9 are unedited, Ruling 42's five prohibitions
all hold (no artifact in this reopen's work claims NFR-RATE-1 passing, the 15 ms trigger is
not treated as fired, `bundle_slot_capacity` is untouched, the delta measurement carries its
host/pass-count/ref-cardinality, F50/F51 are closed against the diff rather than the commit
message), and every register row this scope touches — F50, F51 (closed), F52, F53, F54, F55
(open, each with a stated disposition) — has one of §14's three resolutions rather than
silence. The one paper cut found (10.7) is fixed in this PR. Nothing found here bars
acceptance.

### Sign-off

Proposed verdicts above are the auditor's; acceptance under the maintainer's conditional
delegation (`docs/plans/2026-08-30-w11-reopen-direction.md` §4) is the lead's to record here
with a dated line, per Ruling 39 §5's supersession.
