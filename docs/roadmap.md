# Roadmap

**Status:** draft · **Derived from:** the Phase 0 specification suite, not from `CLAUDE.md`
§9 alone. Where this document and `CLAUDE.md` §9 differ, §9 is authoritative and the
difference is flagged as a recommendation for the maintainer to accept or reject.

---

## 1. How to read this

`CLAUDE.md` §9 fixes five phases. This roadmap adds what the specs now make computable:
the **build order forced by module dependencies**, the **things that cannot be retrofitted**
and therefore must land earlier than their owning phase, the **decisions that gate each
phase**, and where the **effort is actually concentrated**.

Three things this document deliberately does not do:

- It does not re-order or rename the phases. That is `CLAUDE.md` §9's call.
- It does not give dates. Sizing is relative and the assumption is stated in §10.
- It does not resolve open questions. It says *which* ones block *what*, so you can answer
  them in the order that unblocks work, rather than all 46 at once.

*SHA-citation convention, dated 2026-08-25 (WK-664 decision maker):* slice records cite commits by 7-hex abbreviation. A citation written before this date may name the **pre-squash worktree tip** — a commit that resolves only in the worktree where the slice was built, never in a fresh clone; **34 such citations stood at the time of this note**. Each cited commit was an ancestor of its slice's branch tip, and a squash merge preserves the tip's tree, so the cited change is present in the landed commit unless a later commit on the same branch reverted it. The landed commits, by slice: offset `e36e5d0` (#126), custom metrics `8cac13f` (#122), profile `667c8fe` (#113), top levels `9c30182` (#115), EBM `c2c54a6` (#129), W32-8 `946725f` (#157), W32-7 `60f6e46` (#164), the WK-692 closure record `c024f3e` (#161). Alembic revision ids (`9e4c7b21fa08`, `c9d0e1f2a3b4`, `a1b2c3d4e5f6`, `d0e1f2a3b4c5`, `c3d4e5f6a7b8`, `e1f2a3b4c5d6`, `82edffbe1dce`) are migration ids under `backend/migrations/versions/`, not git objects — they resolve in the migration history, not in git; a UUID fragment (`01a018f2`) is a test-assertion value. The class is enumerable: sweep this document for 7-40-hex tokens and test each with `git merge-base --is-ancestor` against `origin/main`.

Plan-ledger SHA-citation convention, dated 2026-08-26 (WK-664 decision maker): the 2026-08-25 note rules the roadmap; docs/plans/ ledgers predate it and are frozen, so the same rule extends to them. A ledger may cite a pre-squash worktree SHA — it resolves in the object store with its subject verbatim but fails an ancestry check against main; verify by subject, never by merge-base. The sweep of 2026-08-26 measured 162 non-matching facts across all shipped plans, the dominant class exactly this. A failed ancestry check is expected, never a defect.

---

## 2. Where the project is

| | |
|---|---|
| **Phase 0 (Specification)** | Closed 2026-08-14 — 8 specs, 5 workflows, 5 ADRs, 31 contracts; `scripts/audit-docs.py` prints the current requirement count, which changes whenever an implementation proves the spec wrong |
| **Blocking Phase 1** | **Nothing.** All seven of Track C's decisions are taken — the last six (OQ-MODEL-1, 2, 4, 5, 6, 7) on 2026-08-15. What remains open gates Phase 2 or later (§10) |
| **Code written** | Phase 1a complete, Phase 1b started — the closure records in [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md) are the authority, not this row |

The remaining Phase 0 work is a **decision backlog, not a writing backlog**. Every open
question already carries options, trade-offs, and a recommendation.

---

## 3. Before Phase 1 — the on-ramp

Three tracks that can run concurrently and mostly do not need each other.

### Track A — Skills research · **CLOSED 2026-08-14**

Track A is closed. **Not because every question was answered** — three were not — but
because **nothing left in it belongs in it**. Each unfinished fragment turned out to be
build work, an acceptance test, or a spike, and has been re-homed to where it will actually
get done. A research track that keeps items it cannot discharge is a parking lot.

Evidence: [`research/track-a-findings.md`](research/track-a-findings.md).

| # | Item (`skills-map.md` §7) | Outcome |
|---|---|---|
| 1 | Custom objectives end to end | **Partly closed.** SymPy derivation ✔ (F2) and XGBoost `base_margin` ✔ (F5) verified empirically; the certification design was found *wrong* and rewritten (F3 → FR-147, FR-148, FR-149). Two fragments re-homed ↓ |
| 2 | ZEN Engine decimal semantics | **Closed** ✔ — `rust_decimal`, ADR-706 confirmed, OQ-614 decided (F1) |
| 3 | glum standard errors | **Closed** ✔ — `std_errors()`/`covariance_matrix()` confirmed to exist (F8) |
| 4 | Polars at 10 M+ rows | **Partly closed.** Streaming-engine status and an open group-by memory regression found (F10), validating ADR-707's split. Benchmark re-homed ↓ |
| 5 | Pydantic v2 → JSON Schema | **Closed** ✔ — discriminated unions confirmed, and a `Decimal` gap found that would let a lossy payload satisfy the contract (F6/F7) |
| 6 | Vue Flow custom nodes | **Documentation only.** `isValidConnection`, node memoisation, Web Workers (F12). Re-homed ↓ |
| 7 | Low-latency Python serving | **Documentation only**, but actionable: Pydantic costs ~1 ms of the 50 ms budget → NFR-502 (F11). Re-homed ↓ |

#### Re-homed, not dropped

| Fragment | New home | Why there |
|---|---|---|
| Restricted AST parser for the expression grammar | ~~**Phase 1, WK-661**~~ **Split, corrected 2026-08-22: the parser landed in Phase 1 WK-660; `02` §4.6's grammar is Phase 2 WK-690** | Both halves of the original sentence turned out to be about different things, which is why this row could sit here contradicting §7 for a week. **The parser**: `pricing_core.data.expressions` was built for `01` FR-36 in **WK-660**, and translates to Polars rather than sandboxing `eval` — the risk this fragment was really about, discharged early and by another workstream. **The grammar this row names**: `02` §4.6 is `expression` custom objectives, sent to **Phase 2, WK-690** by OQ-573 on 2026-08-15 — the same §4.6 that WK-690's own row in §7 lists as carried over, so `roadmap.md` handed one spec section to two different phases. FR-144 and FR-95 are unevidenced today and owned by WK-690 by recorded verdict, so WK-661 never owed this row anything. It was stale from the day OQ-573 was decided, and is struck rather than deleted because an on-ramp fragment that was re-homed twice is the record of how the estimate moved. *Believed on the day:* nothing left to research|
| LightGBM `init_score` symmetry | ~~Spike S3~~ **run 2026-08-14** | Symmetric at fit, **asymmetric at scoring** — `predict()` has no offset parameter. Now FR-129 (F13) |
| Polars 10 M-row benchmark | **Phase 1, WK-660 acceptance** | It is NFR-465/467, measured against real data — an acceptance test, not reading |
| Vue Flow depth | **Phase 2 on-ramp, WK-675** | Does not block Phase 1; belongs with the DAG designer it serves |
| Low-latency measurement | **Spike S2** / Phase 2 WK-671 | Already partly discharged into NFR-502; the rest is measurement |

#### What Track A cost and returned

Four executable spikes. It closed one open question, **found two specification defects**
that would otherwise have surfaced in Phase 1 as confusing failures, and **corrected one
fabricated figure** presented as a measurement. That last one is the strongest argument for
running research against a spec rather than reading about it.

**Practice items** (`skills-map.md` §8–§9) were never in scope for Track A as *research* —
they are working habits, several already exercised: requirement traceability, audit
automation, and the walking-skeleton framing that produced §5 below. They stay live as
practice, not as an open task.

### Track B — Spikes that need code

**Track A research (2026-08-14) has already run four spikes** and closed the substance of
S1 — see [`research/track-a-findings.md`](research/track-a-findings.md). Remaining:

| Spike | Question | Why it cannot wait |
|---|---|---|
| ~~**S1**~~ ✔ **CLOSED 2026-08-14** | FR-273/274/276 | Engine arithmetic is exact — but the **Python binding has no decimal type**, so F1's "workaround not required" was wrong. Money now crosses as integer minor units. Also found: `log`/`sqrt` don't exist in ZEN (the old requirement guarded nothing), while **division by zero returns `null` silently**. |
| ~~**S2 — `exact`-mode GBM latency**~~ ✔ **CLOSED 2026-08-14** | OQ-615 | **Comfortably viable** — p99 1.09 ms, ~2 % of the 50 ms budget. OQ-575 stays a real design choice rather than being forced. `nthread=1` per request (NFR-501). *(WK-668 re-measured 2026-08-27: p99 1.626 ms — see NFR-501/OQ-615.)* |
| ~~**S3 — LightGBM `init_score`**~~ ✔ **CLOSED 2026-08-14** | FR-129 | The assumption was **half wrong**: symmetric at fit time, but `Booster.predict()` has no offset parameter at all, so a scoring path ported from XGBoost silently omits the offset entirely. Fixed as FR-129 (F13). |

**All three spikes are now closed.** Every one changed the specification; none confirmed
its assumption unchanged — which is the argument for having run them rather than reasoned
about them.

### Track C — The decision backlog, sequenced

**All four Phase 1a gates were decided on 2026-08-14** — Apache-2.0, Celery, fit-time
large-loss treatment, and full-snapshot ingestion. **The three 1b gates are now decided too** —
OQ-546 on 2026-08-14, OQ-573 and OQ-579 on 2026-08-15. Nothing in this
table blocks work:

| Question | Gates | Why it blocks |
|---|---|---|
| **OQ-640** Celery vs a transactional Postgres queue | **1a** ✔ *decided* | Job submission is in the first sprint, and transactional enqueue interacts directly with the audit rule (`06` R2) |
| **OQ-557** large-loss capping: dataset or model? | **1a** ✔ *decided* | It *is* the 1a/1b boundary — deferring it makes it a contract change rather than a decision |
| **OQ-558** append ingestion vs full snapshots | **1a** ✔ *decided* | WK-660, and only if the first real dataset is large enough that full snapshots hurt |
| **OQ-541** project licence | **1a** ✔ *decided* | Blocks nothing technically; blocks every external contribution and the public-repo story |
| **OQ-573** expression objectives in 1b? | **1b** ✔ *decided 2026-08-15* | Templates only in Phase 1; expressions in Phase 2 (FR-150/151). The AST parser turned out to be built already — WK-660 needed it for `01` FR-36 — so what left WK-661 is the SymPy derivation and the gradient/hessian compilation target |
| **OQ-579** credibility standard | **1b** ✔ *decided 2026-08-15* | Both, limited fluctuation as the default, recorded per grouping (FR-106) — so WK-661 builds two methods rather than choosing one. **Both are built as of 2026-08-22**: limited fluctuation shipped 2026-08-15, Bühlmann–Straub in the audit-remediation slice, which found it had been refused at runtime for a week with the refusal test marked FR-105 rather than FR-106 — so `scope-audit.py` credited the wrong requirement and the gap read as covered |
| **OQ-546** notebook escape hatch | **1b** ✔ *decided 2026-08-14* | Client library in Phase 1; embedded notebooks revisited in Phase 4 |

The four marked **1a** are the ones that actually gate the start of work. The other 39
can wait for the phase that needs them (§10).

---

### Outstanding work — consolidated

Everything still open before Phase 1a can start, in one place. Tracks A–C above explain
*why*; this is the list. The **Gates** column shows which half of Phase 1 each blocks.

| # | Task | Kind | Owner | Blocks |
|---|---|---|---|---|
| ~~1~~ | ~~**OQ-541**~~ ✔ — project licence | decision | maintainer | **1a** — public contribution, not code |
| ~~2~~ | ~~**OQ-546**~~ ✔ — notebook escape hatch | decision | maintainer | **1b** — decided 2026-08-14: client library |
| ~~3~~ | ~~**OQ-640**~~ ✔ — Celery vs a transactional Postgres queue | decision | maintainer | **1a** — WK-658, first sprint |
| ~~4~~ | ~~**OQ-557**~~ ✔ — where large-loss capping lives | decision | maintainer | **1a** — it *is* the 1a/1b boundary; a contract change if deferred |
| ~~5~~ | ~~**OQ-558**~~ ✔ — append ingestion vs full snapshots | decision | maintainer | **1a** — WK-660, only if the first dataset is large |
| ~~6~~ | ~~**OQ-573**~~ ✔ — do expression objectives ship in Phase 1b? | decision | maintainer | **1b** — decided 2026-08-15: templates only, expressions in Phase 2 |
| ~~7~~ | ~~**OQ-579**~~ ✔ — credibility standard | decision | maintainer | **1b** — decided 2026-08-15: both, limited fluctuation by default |
| ~~8~~ | ~~**S3** — LightGBM `init_score`~~ ✔ **done** | spike | — | Closed. Found a real asymmetry → FR-129 |
| ~~9~~ | ~~**Phase 1 split** — accept or reject 1a/1b~~ ✔ **ACCEPTED 2026-08-14** | decision | maintainer | Now the plan; `CLAUDE.md` §9 updated |

**Not blocking Phase 1, but do not lose them:**

| Task | Kind | Due |
|---|---|---|
| ~~**1 Phase-2 decision (OQ-632)**~~ ✔ **none left** | decisions | Before Phase 2. Was five: OQ-615 decided by spike, OQ-575 on 2026-08-17, and OQ-576, OQ-584, OQ-616, OQ-617, OQ-619 and OQ-642 all on 2026-08-18. **OQ-632 is correctly the last one standing** rather than the one nobody got to: it asks whether an `expression` Custom Objective needs an authoring permission distinct from `model:fit`, and `expression` objectives are themselves Phase 2 — deciding it against the template catalogue would be deciding it against the wrong artifact. **Deferred 2026-08-18 with a trigger rather than left open**: `06` FR-366 makes answering it a precondition of lifting `expression_objectives_enabled`, so WK-690 cannot ship the capability without closing it |
| Sustained-load test at 200 rps (S2 measured per-request only) | test | Phase 2 WK-671 |
| ~~6 Phase-3~~ ✔ *all decided 2026-08-18* · 11 Phase-4 · 5 any-time decisions still open | decisions | Per gate (§10) — OQ-MODEL-2, 4, 6, 7 and OQ-540 and 6 all came off this list on 2026-08-15 |
| Vue Flow depth · Polars benchmark · AST parser | re-homed from Track A | Within their phases |

**Nothing in the document suite is outstanding.** Specs, workflows, ADRs, contracts and the
audit are complete and passing; the remaining Phase 0 work is entirely decisions and
spikes — **nothing before 1a can start** — all four gating decisions were made on 2026-08-14. Three decisions remain before 1b, and the spike backlog is empty.

---

## 4. Build order, and why it is not negotiable

`00-overview.md` DEP-1 fixes the dependency direction:

```
PLAT ──▸ GOV ──▸ DATA ──▸ MODEL ──▸ RATE ──┬─▸ OPT
                                            └─▸ MON
```

A module never imports from a module to its right. Two consequences worth internalising:

- **`MON` cannot be built before `RATE`**, because it consumes production traces. Any
  attempt to start monitoring early produces a system monitoring nothing.
- **`OPT` needs both `MODEL` (demand models) and `RATE` (batch scoring, baseline pricing)**,
  which is why it sits in Phase 4 despite being conceptually independent.

---

## 6. Phase 1 — split into 1a and 1b · **accepted 2026-08-14**

> The split recommended here was **accepted by the maintainer on 2026-08-14** and is now
> the plan, not a proposal. `CLAUDE.md` §9 updated to match.
>
> **Why it was accepted:** Phase 1 as originally scoped was ~47 % of the platform's
> requirement surface with no intermediate demo — the single most likely place for the
> project to stall. The split falls on the existing `DATA` / `MODEL` module boundary, so it
> costs nothing structurally, and it buys a working demo months earlier plus an honest
> checkpoint on whether the validation design survives contact with real data.
>
> **A second benefit emerged on splitting the decision gates:** only **4** of the 7 Phase 1
> decisions block 1a. Work can start once four questions are answered, not seven.

## P1a — Data Workbench
status: active
opened: 2026-08-14
target: ~
gates: ~
exit criteria: ~
works: WK-657, WK-658, WK-659, WK-660, WK-663, WK-666, WK-667

### WK-657 — Repo foundations: `uv` workspace, `model-schema`, `pricing-core` skeleton, CI with import-linter contract (ADR-703), docker compose

```yaml
id: WK-657
family: work
title: Repo foundations: `uv` workspace, `model-schema`, `pricing-core` skeleton, CI with import-linter contract (ADR-703), docker compose
status: closed
created: 2026-08-14
owner: maintainer
phase: P1a
```

From “Phase 1a — Data Workbench” (line 207): Repo foundations: `uv` workspace, `model-schema`, `pricing-core` skeleton, CI with import-linter contract (ADR-703), docker compose | — | **Closed 2026-08-14** — see the status table below

From “Phase 1a status” (line 218): Repo foundations | ✔ **closed 2026-08-14**

From “Workstreams” (line 331): Repo foundations: `uv` workspace, `model-schema`, `pricing-core` skeleton, CI with import-linter contract (ADR-703), docker compose | — | **Closed 2026-08-14** — see the status table below


### WK-658 — Platform core: jobs, blobs, settings, OIDC auth, health, tracing

```yaml
id: WK-658
family: work
title: Platform core: jobs, blobs, settings, OIDC auth, health, tracing
status: closed
created: 2026-08-14
owner: maintainer
phase: P1a
```

From “Phase 1a — Data Workbench” (line 208): Platform core: jobs, blobs, settings, OIDC auth, health, tracing | WK-657 | **Closed 2026-08-14** — ~35 of 61 `PLAT` requirements

From “Phase 1a status” (line 219): Platform core — jobs, blobs, settings, auth, health, tracing | ✔ **closed 2026-08-14** — see [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md)

From “Workstreams” (line 332): Platform core: jobs, blobs, settings, OIDC auth, health, tracing | WK-657 | **Closed 2026-08-14** — ~35 of 61 `PLAT` requirements


### WK-659 — Governance write path: audit log + hash chain, RBAC enforcement, approval state machine

```yaml
id: WK-659
family: work
title: Governance write path: audit log + hash chain, RBAC enforcement, approval state machine
status: closed
created: 2026-08-14
owner: maintainer
phase: P1a
```

From “Phase 1a — Data Workbench” (line 209): Governance write path: audit log + hash chain, RBAC enforcement, approval state machine | WK-657, WK-658 | **Closed 2026-08-14** — §5 skeleton only, no governance UI

From “Phase 1a status” (line 220): Governance write path — audit log, RBAC, approval state machine | ✔ **closed 2026-08-14** — see [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md)

From “Workstreams” (line 333): Governance write path: audit log + hash chain, RBAC enforcement, approval state machine | WK-657, WK-658 | **Closed 2026-08-14** — §5 skeleton only, no governance UI


### WK-660 — Data: sources, ingestion, preparation recipes, parquet, profiling, the four validation layers + built-in rule catalogue, reference tables

```yaml
id: WK-660
family: work
title: Data: sources, ingestion, preparation recipes, parquet, profiling, the four validation layers + built-in rule catalogue, reference tables
status: closed
created: 2026-08-14
owner: maintainer
phase: P1a
```

From “Phase 1a — Data Workbench” (line 210): Data: sources, ingestion, preparation recipes, parquet, profiling, the four validation layers + built-in rule catalogue, reference tables | WK-658, WK-659 | **Closed 2026-08-15** — 48 of **50** `DATA` requirements (the row's "49" predates FR-34), 28/28 endpoints, 38/38 catalogue rules

From “Phase 1a status” (line 221): Data — ingestion, preparation, validation, profiling, reference data | ✔ **closed 2026-08-15** — see [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md)

From “Workstreams” (line 334): Data: sources, ingestion, preparation recipes, parquet, profiling, the four validation layers + built-in rule catalogue, reference tables | WK-658, WK-659 | **Closed 2026-08-15** — 48 of **50** `DATA` requirements (the row's "49" predates FR-34), 28/28 endpoints, 38/38 catalogue rules


### WK-663 — Frontend — app shell, dataset views, validation report view

```yaml
id: WK-663
family: work
title: Frontend — app shell, dataset views, validation report view
status: closed
created: 2026-08-14
owner: maintainer
phase: P1a
```

From “Phase 1a — Data Workbench” (line 211): Frontend: app shell, dataset views, **validation report view** | WK-660 ✔ | **Closed 2026-08-15** — all **7** of `01` §5.3's views, 75 frontend tests

From “Phase 1a status” (line 223): Frontend — app shell, dataset views, validation report view | ✔ **closed 2026-08-15** — see [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md)


### WK-666 — freMTPL2 data seed — the demo dataset through the real Job path

```yaml
id: WK-666
family: work
title: freMTPL2 data seed — the demo dataset through the real Job path
status: closed
created: 2026-08-14
owner: maintainer
phase: P1a
```

From “Phase 1a status” (line 222): freMTPL2 data seed — the demo dataset through the real Job path | ✔ **closed 2026-08-15** — see [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md)


### WK-667 — Demo entrance — one command to a browser, with a derived guide

```yaml
id: WK-667
family: work
title: Demo entrance — one command to a browser, with a derived guide
status: closed
created: 2026-08-14
owner: maintainer
phase: P1a
```

From “Phase 1a — Data Workbench” (line 212): **The demo entrance** and its derived guide | WK-663 ✔, WK-666 ✔ | **Closed 2026-08-15** — FR-408/409. Split from WK-665 for the same reason WK-666 was: the entrance needs no modelling, and Phase 1a's exit demo needs the entrance

From “Phase 1a status” (line 224): Demo entrance — one command to a browser, with a derived guide | ✔ **closed 2026-08-15** — see [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md)


**Goal:** ingestion, preparation, the four-layer validation gate, profiling, reference data
— everything up to a dataset that is fit to model on.

**Demo-able outcome:** an actuary loads freMTPL2, watches validation **fail on a real
problem**, fixes the preparation recipe, acknowledges a warning with a justification, and
drives the version to `validated` — with the report and profile visible. This is
`WF-698` phases A–B end to end.

> **The loop itself passes as of WK-660's close (2026-08-15)**, in
> `backend/tests/test_data_jobs.py::test_the_failure_loop_then_validated`: a file with a
> negative exposure is ingested, validation fails on it, promotion is refused, the *data*
> is fixed rather than the verdict, and the new version reaches `validated` — after which
> `fittable_or_refuse` opens for it and still refuses the first. What Phase 1a still owes
> the demo is the screen (WK-663) and freMTPL2 itself (WK-665); the machinery under both is done.


#### Phase 1a status

| WS | Scope | Status |
|---|---|---|
| ~~**Exit demo**~~ ✔ | Phase 1a's exit criterion exercised through `/demo` | ✔ **accepted 2026-08-15** — one command to a served page in 27 s, the failure loop on real data, two defects found. Exercised over HTTP by Claude; the maintainer accepted without driving it, deferring hands-on testing until more functionality exists |
| ~~**Exit gate**~~ ✔ | FR-40 (ingestion refuses a `direct_identifier` column) · FR-43 (append-only triggers on `validation_reports`, `profiles`, `validation_acknowledgements`) | ✔ **delivered 2026-08-15** — five injections, five caught. `blobs` left the list when building it proved it could not be append-only; the requirement was corrected rather than the table dropped |

#### Phase 1b status

| WS | Scope | Status |
|---|---|---|
| ~~**Exit demo**~~ ✔ | Phase 1b's exit criterion — the core `WF-698` journey (dataset → factors → GLM + GBM fits → comparison → approval → rating version) — exercised over HTTP; bandings, Peril Structure and reconciliation are recorded as Phase 2 | ✔ **accepted 2026-08-27** — scripted HTTP run of the journey with the postconditions verified in **90 s** (NFR-529: < 300 s); one approved model, approved rating version `model:fremtpl2-glm-04da49@1`, comparison artifact present. See [`docs/closures/CR-00821-phase-1b-exit-demo-uat-acceptance-record.md`](closures/CR-00821-phase-1b-exit-demo-uat-acceptance-record.md); the UI is available for hands-on driving |
| ~~**Phase 1b**~~ ✔ | Modelling Workbench — `WF-698` end to end on freMTPL2 | ✔ **closed 2026-08-27** — exit criterion (the core `WF-698` journey over HTTP) met and the demo UAT signed off. See [`docs/closures/CR-00822-phase-record-1b-modelling-workbench.md`](closures/CR-00822-phase-record-1b-modelling-workbench.md) and [`docs/findings/register.md`](findings/register.md) |

Closing a workstream follows `CLAUDE.md` §13 and the `close-workstream` skill: every
deliverable re-verified against its row above, the gate run locally, each new check proven
to fail on broken input, NFRs measured against their budget, and what was *not* delivered
stated explicitly. A closure record without those is an assertion, not evidence.

**And a plan review runs at the same moment** (`CLAUDE.md` §14, from `RFC-711` accepted
2026-08-15). §13 asks whether a workstream did what it said; §14 asks whether the plan still
says the right thing — omission, skills drift, document drift, and whether the remaining
phases are cut in the right place. It runs at **each workstream close and again before a
phase's exit demo**, and its output is a proposal on this page, never an edit made on its own
authority.

~~Two~~ **Three** runs so far: [review 1](#plan-review-1--at-w6as-close-2026-08-15) at
WK-663's close, [review 2](#plan-review-2--at-w7bs-close-and-before-phase-1as-exit-demo-2026-08-15)
at WK-667's close and before the exit demo, and
[review 3](#plan-review-3--at-w5s-close-2026-08-22) at WK-661's close. Each proposal carries its
own maintainer acceptance line; two of review 2's are still pending, and **all of review 3's
are**.

After this has run twice the procedure becomes `.claude/skills/phase-review` (`CLAUDE.md`
§14). It has now run twice — ~~writing that skill is the outstanding item.~~ **and the skill
was written the same day, 2026-08-15, in PR #66 — by the very commit that added this
sentence** (`1ab7b1b`, which added `.claude/skills/phase-review/SKILL.md` at 112 lines
alongside review 2 below). *(Corrected 2026-08-22, the audit-remediation slice.* The sentence
was not overtaken by later work; it was **false when committed**, because it described the
state at the top of the PR that closed it and nobody re-read it at the bottom. Kept and
struck rather than deleted: a claim of outstanding work that shipped inside its own fix is
exactly what §13 rule 2 is about — "exists" and "works" are different claims, and so are
"planned" and "done".*)


## Historical record

The closure records, plan reviews and the retrofit-impossible list moved to [`docs/audit/`](audit/) on 2026-08-27 (RFC-813). This page is the forward-looking plan; the archive is at [`docs/findings/README.md`](findings/README.md).

## P1b — Modelling Workbench
status: active
opened: 2026-08-14
target: ~
gates: ~
exit criteria: ~
works: WK-661, WK-662, WK-664, WK-665, WK-692

### WK-661 — Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective templates

```yaml
id: WK-661
family: work
title: Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective templates
status: closed
created: 2026-08-14
owner: maintainer
phase: P1b
```

From “Phase 1b status” (line 232): Modelling workbench — model detail, comparison, diagnostics, transparency, objective library, perils, factors | ✔ **closed 2026-08-22** — see [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md)

From “Phase 1b — Modelling Workbench” (line 283): Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective **templates only** | WK-660 (1a) | **Closed 2026-08-22** — 110 built · 10 declared-and-refused-by-name · 16 unevidenced with a verdict, of 136; 41/41 endpoints. See [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md). Every `MODEL` requirement — the largest single workstream in the project; `scope-audit.py MODEL` counts them, and per plan review 3's question 5 (accepted 2026-08-22) that is now the only place a reader should take a count from. **Started 2026-08-15**: ~~twenty-two~~ **twenty-eight** slices in — the GLM spine, bandings and groupings, the factor workbench, diagnostics, spec validation, the model lifecycle, model comparison, `WF-698`'s citation audit, gradient boosting with its transparency artifact, `WF-698` driven end to end, peril structures with their reconciliation, interaction factors, backtests, prediction, custom objectives, FR-44's artifact triggers, the profile contract, `top_levels`' exposure per level, the exact-decimal refusal of a float, paired quantile models, the GLM approximation as a Model (FR-137, FR-141 — measured at +0.26 s / ~7 % against a **single-factor** fixture; type-III diagnostics refit the surrogate once per factor, so this does not bound a multi-factor model, and `type_iii=False` is the lever if that ever bites, not pulled without the maintainer), and **custom metrics** (FR-154/155/157/159/160/162 — a Custom Metric reaches `approved` on the same lifecycle and grammar as a Custom Objective, `GbmSpec.eval_metrics` is now honoured rather than merely declared, and MODEL's endpoint axis closed at **40 of 40**, the first module in this repository to publish every declared endpoint), **regularisation and cross-validation** (FR-112/182), **Tweedie power by profile likelihood** (FR-114), **offset from another model** (FR-116), **EBM via interpret-core** (FR-140) and **GBM declared weights with the dropped eval metric record** (FR-111/161), and **the audit-remediation slice** (2026-08-22, this one); see the slice records in [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md). *(The count said eighteen and omitted the exact-decimal slice, which had already landed as PR #116; corrected 2026-08-19 by the paired-quantile slice.)* *(It went stale the same way again and is corrected 2026-08-22 by the audit-remediation slice: five slices — regularisation/CV (#124), Tweedie (#125), offset (#126), EBM (#129) and GBM weights (#130) — landed between 08-21 and 08-22 with the count left at twenty-two, while this file's own newest record already called itself "the twenty-seventh slice". Both stale values are kept. **The mechanism is the same both times and is worth naming rather than re-fixing:** a slice's PR strikes its row in the outstanding-work table and stops there, and this count is a second place nothing reconciles against that table — #116 did it, then #124 and #125 did it again. The same mechanism left the buildable-slice counter at one when every row beneath it was struck, and left six verdicts stale in the diagnostics slice's table. **A slice updates the row that describes itself; every other place that counts slices is unowned.** The count is of **numbered** slices, so the three decision-only records of 2026-08-18 (PRs #106, #107, #108) have records and no number and have never been in it.)* **The prediction slice (PR #102, 2026-08-18) landed without a slice record** — the omission is recorded here rather than reconstructed from the diff; what it found is in `02`'s dated notes — FR-195, OQ-585 and OQ-586, plus the `inverse`-link resolution at §3.4 — and in `.claude/skills/python-test`. **Scope set by the 2026-08-15 decisions:** templates only, with the certification machinery built here (FR-150/151); both credibility methods, not one (FR-106); SHAP interaction *suggestions* (FR-135); the complexity diagnostic and its optional gate (FR-185); paired quantile models as the only GBM interval (FR-198/199). **WK-661 also finishes `WF-698`, and has**: the citation audit and the journey test landed 2026-08-17, and on 2026-08-18 the peril-structure and interaction slices drove the last three pinned steps, so FR-19(ii) for `WF-698` is **delivered** — the first of the five journeys. **The closure slice (2026-08-22) is the last, and the count above is deliberately not incremented to twenty-nine**: plan review 3's question 5 was accepted the same day, and adding a fourth hand-written count to the file whose staleness prompted the proposal would be the clearest possible way to ignore it. The slice records in [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md) are the list; `scope-audit.py` is the count

From “Workstreams” (line 335): Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective templates | WK-660 | **Closed 2026-08-22** — 136 in scope at close, of which 110 built. All ~~**124**~~ `MODEL` requirements — the largest single workstream. *(Re-derived 2026-08-22 with `scope-audit.py MODEL`; the row said 78, the count when it was written. Requirement ids only ever accumulate — §5 — so a number written once goes stale by construction rather than by error.)*


### WK-662 — Frontend: app shell, dataset views, **validation report view**, **factor workbench**, model detail, diagnostics

```yaml
id: WK-662
family: work
title: Frontend: app shell, dataset views, **validation report view**, **factor workbench**, model detail, diagnostics
status: retired
created: 2026-08-14
owner: maintainer
phase: P1b
```

From “Workstreams” (line 336): Frontend: app shell, dataset views, **validation report view**, **factor workbench**, model detail, diagnostics | WK-660, WK-661 | The two bolded views are where `01` §5.3 and `02` §5.3 place their interaction requirements

Retired rather than closed (RL-993): this work's own row carries no closed signal, and its scope was re-cut into WK-successors before it completed under this name — see the successors named below. Successors: WK-663, WK-664.


### WK-664 — Frontend: **factor workbench**, model detail, diagnostics — **and the frontend platform**: browser authentication, accessibility beyond semantics, the workspace selector's **shell control only**, and the audit's two enforcement gaps — **FR-40** and **FR-43**

```yaml
id: WK-664
family: work
title: Frontend: **factor workbench**, model detail, diagnostics — **and the frontend platform**: browser authentication, accessibility beyond semantics, the workspace selector's **shell control only**, and the audit's two enforcement gaps — **FR-40** and **FR-43**
status: closed
created: 2026-08-14
owner: maintainer
phase: P1b
```

From “Phase 1b status” (line 233): Modelling-workbench UI — dataset list, rule set editor, model spec builder, browser auth, workspace selector, lineage, rating-version demo seam | ✔ **closed 2026-08-27** — see [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md)

From “Phase 1b — Modelling Workbench” (line 284): Frontend: **factor workbench**, model detail, diagnostics — **and the frontend platform**: browser authentication, accessibility beyond semantics, the workspace selector's **shell control only**, and the audit's two enforcement gaps — **FR-40** and **FR-43** | WK-661, WK-663 ✔, OQ-644 ✔ | **Closed 2026-08-27** — see [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md). `02` §5.3's interaction requirement — an edit's consequence visible before saving. The platform half was added by plan review 1 (accepted 2026-08-15): **FR-393** (authorization code + PKCE — until it ships, only the dev proxy reaches the API from a browser), **NFR-463**'s tabular fallback for charts, and a workspace selector, which `07` §3.1 needs the moment a principal belongs to more than one. **Corrected 2026-08-23 (WK-664 slice-map backlog item 2): that clause read as a citation and was a forecast — §3.1 had never contained the requirement.** It does now, as FR-395 (a Workspace becomes a named entity; there was no `workspaces` table, so a selector had nothing to render) and FR-396 (the selection, verified against membership). **Both are WK-692's, not WK-664's** — a table, a migration and an API — and the transport is OQ-648. WK-664 keeps the shell control and stays blocked until the backend half lands.


### WK-665 — freMTPL2 demo seed **and the demo entrance**

```yaml
id: WK-665
family: work
title: freMTPL2 demo seed **and the demo entrance**
status: closed
created: 2026-08-14
owner: maintainer
phase: P1b
```

From “Phase 1b status” (line 234): freMTPL2 demo seed — **the modelling half** | ✔ **closed 2026-08-27** — see [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md)

From “Phase 1b — Modelling Workbench” (line 286): freMTPL2 demo seed — **the modelling half** | WK-661, WK-664 | **Closed 2026-08-27** — see [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md): a fitted GLM, a rating version, and `WF-698` end to end. The data half closed as **WK-666**, the entrance and its guide as **WK-667** (FR-408/409, `RFC-712`) — both in Phase 1a, because neither needed modelling and Phase 1a's exit demo needed both

From “Workstreams” (line 337): freMTPL2 demo seed **and the demo entrance** | WK-660, WK-661, WK-662 | `07` FR-439, plus FR-408/409 (`RFC-712`). The data half closed early as **WK-666**


### WK-692 — Everything in Phase 1b that is not a browser — the contract guards, `model-schema` shapes, a migration, backend defects, endpoint tests and one skill

```yaml
id: WK-692
family: work
title: Everything in Phase 1b that is not a browser — the contract guards, `model-schema` shapes, a migration, backend defects, endpoint tests and one skill
status: closed
created: 2026-08-14
owner: maintainer
phase: P1b
```

From “Phase 1b — Modelling Workbench” (line 285): Everything in Phase 1b that is not a browser — the contract guards, `model-schema` shapes, a migration, backend defects, endpoint tests and one skill | WK-661 | **Added 2026-08-24** (`plans/PL-00776-wk-692-what-closure-needs-and-why-it-cannot-happen-yet.md` Part B1, accepted by the maintainer that day). **Split from WK-664 2026-08-22** and accepted the same day (`plans/PL-00753-wk-664-and-wk-692-the-slice-map.md` §1, acceptance table row 1) — but the split created a workstream name without creating a row, so for two days work merged under a name this plan did not contain, and the coverage figure under Phase 1b described a scope that excluded it. **Eleven slices**, W32-1 … W32-11 — ten as scoped on 2026-08-22, plus **W32-11** allocated 2026-08-24 by the closure proposal's Part C decisions, which WK-692's close waits on. **W32-11 is the terminal slice**, picked up 2026-08-24 by the closure-execution session and confirmed by the maintainer the same day; findings it cannot resolve are booked forward with an owner rather than held against the close — see the decision record in [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md); **W6b-1 and W6b-5 depend on W32-1, W6b-13 on W32-2, and W6b-3 on W32-3** — all three merged, so **those four WK-664 slices** wait on nothing but this workstream's close. **`W6b-11` is not among them and does wait on unbuilt WK-692 code**: FR-395 and FR-396 are **W32-7's**, and W32-7 is unstarted — there is no `workspaces` table (only `workspace_members` and `workspace_settings`), `record_switch` appears nowhere in `backend`, `packages` or `frontend`, no migration mentions a workspace, and `deps.py`'s `_single_workspace` still refuses a multi-membership caller outright. *(Corrected 2026-08-24: this clause read "W6b-1, -3, -5 and -13 are blocked on it", and two WK-664 sessions reached opposite readings of "it" — W32-11, the nearest noun, versus WK-692, the row's subject. Arbitrated against `plans/PL-00753-wk-664-and-wk-692-the-slice-map.md` §5's slice table: those four are **exactly** the WK-664 rows whose dep column names a WK-692 slice, the other nine naming a WK-664 row or nothing. A dependency discovered after 2026-08-22 would have no reason to fall on precisely that pre-existing subset, so the clause compressed the column rather than recording something new. The frozen map needs no amendment.)* *(Corrected again 2026-08-24, hours later — the clause above was itself correction text, and the correction introduced this defect. It ended "all three merged, **so no WK-664 slice waits on unbuilt WK-692 code**; what they wait on is this workstream's close." The compression to the frozen dependency column is sound and is left standing; the trailing clause **generalised from the four slices that column names to all thirteen**, and that universal is false. `W6b-11`'s dependency on WK-692 was created **2026-08-23** by FR-395/396 — *after* `plans/PL-00753-wk-664-and-wk-692-the-slice-map.md` §5's table was frozen — so it is invisible in the very column the compression is derived from, and the **WK-664 row immediately above already said the opposite**: "WK-664 keeps the shell control and stays blocked until the backend half lands." Two consecutive rows of one table asserted contradictory things for as long as the clause stood. Found by `w6b-decision-maker`, routed via `w6b-lead`, verified here against five independent sources, one of them the code. **The mechanism is that a frozen dependency column ages into a false "ready"**: every dep it names merges, the row reads unblocked, and a dependency discovered later is nowhere in it to say otherwise. **A claim derived from a frozen column describes the column, never the world** — the compression was legitimate up to the em-dash and became a forecast after it. **The clause is in fact refutable on its own text, with the WK-664 row unread**: the justification licensing it — "a dependency discovered after 2026-08-22 would have no reason to fall on precisely that pre-existing subset" — is exactly the assertion that **the subset is not the population**. The premise that makes the narrow claim sound is the one that refutes the broad one. Diagnosed against the neighbouring row you fix a sentence; diagnosed against the quantifier you fix the class, which is why it is written this way round. Cost had it stood: a WK-664 session builds a workspace selector against a table that does not exist.)* *(Corrected 2026-08-24 at `60f6e46`, the last feature SHA. The closing commit is `e2ae7c6` (#165): **the `W6b-11` clause above is now false in every particular, and is left standing because it was true when written.** W32-7 merged (#164) and ships the `workspaces` table, its migration, `record_switch` in `platform/workspace_switch.py`, and a `deps.py` that resolves a verified `Workspace-Id` header instead of refusing a multi-membership caller outright. **`W6b-11` no longer waits on unbuilt WK-692 code**; what it waits on is this workstream's close, recorded above. **One residual remains and it is not a build dependency**: FR-396's fourth obligation — a switch audited into both chains — is delivered as a mechanism and tested, and **unenforced on the request path**, because `require_caller` runs once per request and cannot observe that a selection *changed*. Deferred with an owner, **owner W6b-11**, tracked as **`OQ-652`**. A WK-664 session building the selector will find the table and the header; it will not find a request-path trigger, and it owns writing one. **And `plans/PL-00753-wk-664-and-wk-692-the-slice-map.md` is frozen at its date and was not corrected by this close** — `CLAUDE.md` §2 freezes a filed plan, and editing one destroys the record of what was believed at its date while reading as though it had always been right. Its **line 192** still tells `W6b-11` it waits only on WK-692 building the header half, which was accurate when written and now misleads the one session it gates. **This clause is the live correction; that map is not current.**)* Slice records are in [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md) — W32-1 … W32-5 back-filled 2026-08-24, which is the same omission in its second form, and the workstream's closure record is in [`docs/closures/INDEX.md#closure-recordsmd`](ledgers/LG-00730-wk-661-wf-698-driven-end-to-end.md)


**Goal:** factors, bandings, groupings, GLM and GBM fitting, diagnostics, transparency
artifacts, model versioning.

**Demo-able outcome:** the actuary bands and groups factors, fits a GLM and an XGBoost
model, compares them, and gets one approved — **`WF-698` end to end**.


**Coverage:** ≈ 78 of 375 module requirements (~21 %).

**Exit:** the core [`WF-698`](workflows/WF-00698-dataset-to-approved-model.md) journey on freMTPL2 —
dataset → factors → GLM + GBM fits → comparison → approval → rating version — exercised
over HTTP. Bandings, Peril Structure and reconciliation are recorded as Phase 2 (plan
review 6, accepted 2026-08-27).

WK-661's *frontend* work (WK-664) can start as soon as the `02` contracts are frozen, which is the
main parallelisation opportunity inside 1b.

> **2026-08-23 — the WK-664 slice map's specification backlog is resolved.** Its §4 listed
> eleven items, each blocking a WK-664 or WK-692 slice from starting, and the plan is frozen at
> its date so the resolutions live in the specs rather than in it. Four were **spec gaps**
> and are now requirements: `07` FR-398 (a local OIDC provider behind an opt-in compose
> profile), FR-395 and FR-396 (a Workspace becomes a named entity; the selection is
> verified against membership), `01` FR-56 (a threshold edit authors a new rule
> version) and `02` FR-167 (the three artifact libraries are listable). Four were
> **the spec being wrong** and are corrected on the spec's side: `02` §5.3's three stale
> routes and its two-state certificate cell, `01` §4.4's "thresholds are Rule Set
> configuration, not code", and FR-135's promise of an exposure share that is `1.0` by
> construction and a holdout lift defined nowhere. Two were **shapes that escaped the
> contract**: `01` §4.9 now types the lineage response, and `02` §5.3 registers the two
> views WK-692 built without rows. Three new questions came out of the work rather than being
> answered inside it — OQ-601, OQ-647 and OQ-648 — and each is on a gate row.
> **What is not resolved here is the code**: every item names an owning workstream, and
> `W6b-11` stays blocked until OQ-648 is decided. *(Amended 2026-08-23: all three were decided that
> same day — FR-168, FR-414 and FR-397. `W6b-11` is no longer blocked on a decision and
> now waits only on WK-692 building the header half.)*

### Original scope, for reference

**Goal (`CLAUDE.md` §9, now superseded by the split above):** dataset upload + validation + profiling, GLM and XGBoost fitting
(incl. custom objectives), factor management, diagnostics, model versioning. Demo on
freMTPL2.

**Demo-able outcome:** an actuary loads freMTPL2, watches validation fail on a real
problem, fixes it, acknowledges a warning, bands and groups factors, fits a GLM and an
XGBoost model, compares them, and gets one approved — i.e. **`WF-698` executed end to end**.



WK-660 and WK-661 are sequential in contract terms but their *frontend* work (WK-662) can start as soon
as the contracts are frozen, which is a Phase 1 parallelisation opportunity worth taking.

### Requirement coverage

≈ **177 of 375** module requirements — **roughly 47 % of the entire platform's requirement
surface sits in Phase 1.**

> **Accepted 2026-08-14.** This callout is retained as the record of the reasoning; the
> split is specified above and in `CLAUDE.md` §9.

### Top risks

| Risk | Mitigation |
|---|---|
| Validation engine is under-estimated — 48 built-in rules across four layers with sandboxing | Build layers 1 and 3 first (they gate fitting); layers 2 and 4 can follow |
| ~~Custom objectives are a research task, not a coding task~~ **retired 2026-08-15** — OQ-573 decided: templates only, and the parser the risk was really about was built in WK-660 for `01` FR-36 | What is left in Phase 1 is the certification machinery (FR-151), which certifies losses `pricing-core` already differentiates. The research risk moves to Phase 2 with the expressions (WK-690) |
| Polars/DuckDB performance at 10 M rows discovered late | Test against a realistic dataset in WK-660, not at the end |
| Diagnostics scope creep — `02` lists a lot of them | FR-171 (universal) is the gate; 51/52 can land incrementally |

---

## P2 — Rating Engine
status: active
opened: 2026-08-14
target: ~
gates: ~
exit criteria: ~
works: WK-668, WK-669, WK-670, WK-671, WK-672, WK-673, WK-674, WK-675, WK-690, WK-693, WK-694, WK-695, WK-696, WK-697

### WK-668 — **Spike S1/S2 resolution and ADR-706 confirmation**

```yaml
id: WK-668
family: work
title: **Spike S1/S2 resolution and ADR-706 confirmation**
status: active
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 373): **Spike S1/S2 resolution and ADR-706 confirmation** | Must complete before WK-669. If S1 fails, this phase is re-planned


### WK-669 — Rating algorithm contract, validation, bundle compilation

```yaml
id: WK-669
family: work
title: Rating algorithm contract, validation, bundle compilation
status: closed
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 374): Rating algorithm contract, validation, bundle compilation | `03` FR-RATE-1..13, 22..27, 56/57/58/59, FR-223 (added 2026-08-17 with `02` OQ-575 — the row's original "FR-RATE-1..13, 22..27, 56/57/58/59" omitted it) — **Closed 2026-08-27** — see the WK-669 closure record (`docs/closures/CR-00838-work-item-record-wk-669-the-rating-contract-validation-and-bundle-compilation.md`). The RatingAlgorithm contract (#291), the save-time validation and boundary guards (#292), and the bundle compilation (#293) shipped


### WK-670 — Rate tables incl. seeding from models, diffs, bulk operations, import/export

```yaml
id: WK-670
family: work
title: Rate tables incl. seeding from models, diffs, bulk operations, import/export
status: closed
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 375): Rate tables incl. seeding from models, diffs, bulk operations, import/export | `03` FR-228, FR-229, FR-230, FR-231, FR-233, FR-234, FR-235, FR-236, FR-232 (added 2026-08-18 with OQ-616 — the row's original "FR-228, FR-229, FR-230, FR-231, FR-233, FR-234, FR-235, FR-236" omitted it) — **Closed 2026-08-28** — see the WK-670 closure record (`docs/closures/CR-00834-work-item-record-wk-670-rate-tables.md`). Seeding, diffs and validation (#297/#302), the four bulk operations, CSV/XLSX import/export and the parquet spill (#304/#307/#310), and the 202-with-Job diff with the DP3 cache (#311) shipped


### WK-671 — Scoring: real-time, batch, trace, one shared evaluator

```yaml
id: WK-671
family: work
title: Scoring: real-time, batch, trace, one shared evaluator
status: closed
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 376): Scoring: real-time, batch, trace, one shared evaluator | FR-250, FR-251, FR-253, FR-254, FR-255, FR-256, FR-257, FR-258, FR-259, FR-252 (added 2026-08-18 with OQ-619 — the row's original "FR-250, FR-251, FR-253, FR-254, FR-255, FR-256, FR-257, FR-258, FR-259" omitted it); NFR-489 is the hard target, joined by NFR-502/501 (carried forward from WK-669 via register row F-W9-1 — omitted from this row until now) — **Closed 2026-08-30 as a REDUCED-SCOPE close** — see the WK-671 closure record (`docs/closures/CR-00927-work-item-record-wk-671-scoring.md`). **Seven of ten FRs delivered and tested; FR-RATE-36, 37 and 42 never started** — batch scoring and production sampling, reassigned to future slices whose plans and rulings are filed. **NFR-489, this row's own hard target, is measured and FAILING**: `_fetch_bundle` alone costs p99 66.294 ms against a 50 ms whole-request budget, over budget from 10 rps, cause resolved to fetch rather than saturation. Carried forward to an architectural ruling before WK-674. NFR-502 is recorded **owed, not delivered**. Closed by the lead under the maintainer's delegation of 2026-08-30 — **RE-OPENED IN PART 2026-08-30**, on the maintainer's direction (`docs/rulings/RL-00918-wk-671-reopen-the-maintainer-s-direction-recorded-2026-08-30.md` §1), in the shape RL-919 fixed. **The close note above stays verbatim and is not withdrawn**: it was correct at its date, and only the status marker moved — a ✔ over live work is §13's own defect inverted. Back in scope: **FR-253, FR-254, FR-259** and, riding with FR-259, **NFR-500**. Adoption slices E/F/G are a separate Work and are **not** part of this reopen. The §6 carry-forward naming an architectural ruling for NFR-489 is **discharged by RL-921** — a `ref` may not be served from the memo without a metadata read and does not need to be — but **NFR-489 is neither amended nor shown reachable**: the without-GBM limb reads component p99 23.027 ms against 15 ms with the fetch already excluded. The second close is appended to the closure record as §10, is scoped to the reopened requirements only, and is **the lead's to accept under the maintainer's conditional delegation of 2026-08-30** (`docs/rulings/RL-00918-wk-671-reopen-the-maintainer-s-direction-recorded-2026-08-30.md` §4), which supersedes RL-919 §5. **Two preconditions, neither waivable by the lead**: every reopened slice complete (W11-3's four tasks and W11-4's four, plus any further slice a ruling adds to the reopen), and the auditor satisfied with the closure audit — an unresolved auditor objection bars acceptance rather than informing it, and the disagreement route is escalation to the maintainer, never overruling the auditor — **SECOND CLOSE ACCEPTED 2026-08-30** by the lead under the conditional delegation, both preconditions met (all eight reopened tasks merged; the auditor satisfied in its own words). **All three reopened FRs — FR-253, FR-254, FR-259 — delivered and tested**, so the first close's *never started* is discharged. **NFR-500 measured and FAILING** at ~2.58× over a 200 GB/yr budget, on a conservative basis. **NFR-493 given its first verdict**, split: throughput PASS at 5.09×, linearity NOT MEASURED. **NFR-489's verdict is unchanged — still measured and FAILING**; RL-921 discharged the architectural question, not the requirement. The full record is §10 of the closure record


### WK-672 — Testing: golden quotes, property assertions, regression runs

```yaml
id: WK-672
family: work
title: Testing: golden quotes, property assertions, regression runs
status: active
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 377): Testing: golden quotes, property assertions, regression runs | FR-260, FR-261, FR-262


### WK-673 — Dislocation with attribution

```yaml
id: WK-673
family: work
title: Dislocation with attribution
status: active
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 383): Dislocation with attribution | FR-263, FR-264, FR-265, FR-266


### WK-674 — Deployment: environments, atomic switchover, rollback, shadow — **and the tenancy mechanics ADR-710 requires**

```yaml
id: WK-674
family: work
title: Deployment: environments, atomic switchover, rollback, shadow — **and the tenancy mechanics ADR-710 requires**
status: active
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 384): Deployment: environments, atomic switchover, rollback, shadow — **and the tenancy mechanics ADR-710 requires** | FR-267, FR-268, FR-269, FR-270, FR-271, FR-272; `07` FR-428, FR-429, FR-430, FR-431, and added 2026-08-15 by OQ-540's decision: **FR-436** (a deployment refuses to start against another tenant's database) and **FR-18** (a Job records the platform build, because version skew between tenants is now permanent). Any earlier `Job` migration should carry FR-18's column rather than wait for this


### WK-675 — Frontend: **DAG designer (Vue Flow)**, rate table editor, quote sandbox + ladder waterfall, dislocation views

```yaml
id: WK-675
family: work
title: Frontend: **DAG designer (Vue Flow)**, rate table editor, quote sandbox + ladder waterfall, dislocation views
status: active
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 385): Frontend: **DAG designer (Vue Flow)**, rate table editor, quote sandbox + ladder waterfall, dislocation views | The DAG designer is the single largest frontend effort in the project


### WK-690 — **`expression` custom objectives** — SymPy derivation, the gradient/hessian compilation target, the authoring UI, and lifting `expression_objectives_enabled` **plus `custom_objective:author` and its check, which `06` FR-367 requires the `expression` kind to arrive with**

```yaml
id: WK-690
family: work
title: **`expression` custom objectives** — SymPy derivation, the gradient/hessian compilation target, the authoring UI, and lifting `expression_objectives_enabled` **plus `custom_objective:author` and its check, which `06` FR-367 requires the `expression` kind to arrive with**
status: active
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 386): **`expression` custom objectives** — SymPy derivation, the gradient/hessian compilation target, the authoring UI, and lifting `expression_objectives_enabled` **plus `custom_objective:author` and its check, which `06` FR-367 requires the `expression` kind to arrive with** | Added 2026-08-15 by OQ-573's decision, which moved this work out of WK-661 rather than deleting it: `02` FR-144/145, FR-150, §4.6, and `WF-702` Route B. It depends on nothing in WK-669–WK-675 and could equally be pulled into 1b if WK-661 finishes early — but it must not start before the certification machinery it fronts (FR-151) has run for a phase, which is the whole point of the decision


### WK-693 — Machine-readable process core — RFC-895, adopted remainder (Slices E/F/G)

```yaml
id: WK-693
family: work
title: Machine-readable process core — RFC-895, adopted remainder (Slices E/F/G)
status: closed
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 378): Machine-readable process core — RFC-895, adopted remainder (Slices E/F/G) | Adopted 2026-09-01 from RFC-895 by the reconciliation's dated acceptance line — the note's Slices A–D had landed 2026-08-30/31 under a dated delegation (the clause-2 exception's first instance, below). E/F/G landed with them: the process core held by `audit-docs` checks 26/27, the plan validator check 28, artifact B and the C2 retry-cap hook; C3 dissolved by RL-920, not built. **Closed** at [`docs/closures/CR-00933-audit-record-nt-0012-0013-0014-adoption-docs-audit-checklists-work-item-close-md.md`](closures/CR-00933-audit-record-nt-0012-0013-0014-adoption-docs-audit-checklists-work-item-close-md.md), accepted by the lead under the adoption record's §1.1 delegation. **Three findings carried open, not absorbed**: **F61** — C2's hook layer is bypassable and has no CI-equivalent backstop; **F58** — artifact B has no live writer; **F57** — zero retry-cap cycles have run, so §7's caps still have no data toward their own revisit condition


### WK-694 — The register is a ledger, evidence is a file — RFC-896, P1–P5

```yaml
id: WK-694
family: work
title: The register is a ledger, evidence is a file — RFC-896, P1–P5
status: active
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 379): The register is a ledger, evidence is a file — RFC-896, P1–P5 | Adopted 2026-09-01 from RFC-896 by the reconciliation's dated acceptance line. **P1–P5 all merged 2026-08-31** (`fa87086`, `890b06e`, `f99b55d`, `cfed4f0`, `6b3459a`, `365ad18`, the `lead.md` enter step): the decision grammar held by check 29 via `scripts/register-lint.py`; `scripts/register-owed.py` generates the owed list a close compiled by hand; the ledger/evidence split is real at `docs/audit/findings/` with **F27** the worked exemplar; migration opportunistic-on-amendment with a falsifiable residue line (38 of 61 rows over the 1000-character threshold at landing). **Three findings filed from the work itself**: **F62**, **F63** (ten WK-671-attributed register rows in no closure record — disposition reserved to the maintainer, reopening a Work close is theirs alone), **F64**. **One deviation deliberately not back-dated**: no adoption plan was filed for work that landed ahead of this row — named here rather than closed over; the next §14 review disposes of it


### WK-695 — **File taxonomy, reference coding and custody — RFC-897 Stages 2–5**

```yaml
id: WK-695
family: work
title: **File taxonomy, reference coding and custody — RFC-897 Stages 2–5**
status: active
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 380): **File taxonomy, reference coding and custody — RFC-897 Stages 2–5** | [`RFC-897`](rfcs/RFC-00897-file-taxonomy-reference-coding-and-custody-investigation-rev-2.md) §4–§7, built against the ruled inputs (Rulings 55–65). **Stage 2 — the reference-coding standard:** filename grammar and header block per category, over the twelve-category set as amended by RL-941 (the closure/audit record's three homes documented; the map/leaf and rulings-record grammar splits resolved here as the named items RL-941 hands over); one home per category per RL-942 (rulings and ledgers stay in `docs/plans/` under filename grammar; closure/audit records keep their three homes; register + findings keep their two); citation forms per RL-944's mixed grammar — spec, ADR, note, register/findings and workflow journey cite by their existing id, while plan, rulings record, ledger, closure/audit record, contract and process/charter/skill cite by dated filename — prospective only, no frozen retrofit (RL-944 §2a, matching RL-948 for the notes family); `docs/INDEX.md` as the legacy mapping so the standard covers every file without moving one (C1); `scripts/file-lint.py` wired into the gate warn-then-red with a dated flag-day; the five creating skills (`writing-plans`, `close-workstream`, `phase-review`, `adr-write`, `spec-change`) updated to emit the standard. **Stage 3 — the ownership map:** the category × role matrix (creates/amends/retires) as a living file in `docs/process/` (RL-945), every cell citing the charter line that grants it, empty rows and columns filed as findings per RFC-896's grammar. **Stage 4 — the workflow-loop audit:** the lifecycle triple per category (which step creates, reads, retires), the four verdicts, and the unreferenced population — 39 files at `4f95fb3`, 40 at `052afe3` — decomposed into verdict-2 findings or declared verdict-4; verdict-4 status is **derived** from an existing closure record wherever one covers the file, and an explicit declaration is required only for the residual — the 3 verdict-2 files plus any future file with no covering closure record — in whichever of the two forms the implementing slice chooses (RL-943). **Stage 5 — migration and enforcement:** the prospective standard live from the flag-day; legacy migrates opportunistically-on-amendment only, never a bulk rename (C1); the census re-runs at every phase close, with growth in uncategorised or verdict-2 files a red flag in the phase review. **Dependencies:** Stage 4 needs the committed census (`docs/research/file-census-5ef559d.csv`) and Stage 3's matrix; Stage 5 needs Stage 2; Stages 2 and 3 are independent now that Stage 1 and the gate ruling have landed (the note's §8 dependency chain). **Acceptance:** the note's §11 items (a)–(g). The notes move (the note's former S0) already landed as the investigation plan's Slice 4 (`1ec453b`, PR #544) **SUPERSEDED IN PART 2026-09-02 by WK-697.** [`RFC-937`](rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) §9 replaces **Stages 2 and 5** outright — its §1 standard and §4 one-time scripted migration do that work across the whole corpus rather than over the twelve categories alone — **lifts constraints C1 and C2**, and lapses **Rulings 63 and 65** by their own override clauses. RL-943 survives as check 38; Rulings 55–58 are absorbed; RL-941's category set and the Stage 0 census are kept as inputs. **Stages 3 and 4 survive and are not lost with this clause**: they become the two downstream Works RFC-937 §8's closing sentence names — the charter investigation (§1.6 made binding in each charter, with a directory-level `owner:`) and the create-read-retire audit (the process step per transition in §1.2's state machines). The row is kept, not reclaimed (`CLAUDE.md` §5). **Do not plan against Stages 2 or 5 from here.** The direct contradiction, named rather than left for a reader to hit: this row's C1 says legacy migrates opportunistically-on-amendment and *never a bulk rename*, and a bulk rename is precisely what RFC-937 authorises — two live rows planning one corpus in opposite directions is what this clause exists to prevent. Disposition by the lead under the maintainer's 2026-09-01 delegation, recorded at `docs/rulings/RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`.


### WK-696 — A public face for a public repository — RFC-898, the residue

```yaml
id: WK-696
family: work
title: A public face for a public repository — RFC-898, the residue
status: active
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 381): A public face for a public repository — RFC-898, the residue | Adopted 2026-09-01 from RFC-898 by the reconciliation's dated acceptance line. The content landed 2026-08-30 under the note's §7 light path (`README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `.github/` templates — the clause-2 exception's second instance); the exposure is discharged. **The residue: two impact rows.** Row 9 — this roadmap row existing — is discharged by this row itself. Row 6 — the two repository settings (private vulnerability reporting; issues with templates) — is **not verifiable from the tree**: it is evidenced by a dated maintainer line, which is the maintainer's to write and nobody else can supply it. **Acceptance:** the note's §8 (a) and (c)–(e) — the link check, a test issue filed through each form, and the auditor's outsider read of the `README`


### WK-697 — **One id per governed thing — RFC-937, the whole standard**

```yaml
id: WK-697
family: work
title: **One id per governed thing — RFC-937, the whole standard**
status: active
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 382): **One id per governed thing — RFC-937, the whole standard** | Adopted 2026-09-01 from [`RFC-937`](rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) by the note's **own dated `accepted` status**, which the maintainer ruled that day is this row's acceptance line: RFC-937 arrived accepted rather than being moved to accepted by a reconciliation, so the *"reconciliation's dated acceptance line"* that WK-693, WK-694 and WK-696 cite has no referent here, and WK-695 already cites neither — the register admits more than one authority form. The ruling is recorded at `docs/rulings/RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md` §4, and the derivation rather than the conclusion is in the map plan's Authority section. **Scope:** the note's §1 standard in full — one global integer sequence across every row and document family, the five-word status vocabulary of §1.2a, the family-per-directory layout, the YAML header with its closed field set, roles per family, phase-as-milestone, and the generated index, ownership matrix and phase report; its §4 one-time scripted migration; its §5 impact map — root governance, all of `docs/`, seven role charters, two agents, every skill (twenty-six substantively, a header on all forty-six), fourteen scripts, twelve tests, two CI workflows, and every code and test file citing a document or requirement; and its §7 acceptance items (a)–(k). **Population, carried with its tree and its predicate because both matter:** the note's "767 files" at `8f5d57d` re-measures to **770** at `89dd2b1` and **771** at `bc7bc36`, but that figure uses a pattern including `VR-` product identifiers, which D5 places permanently out of scope — so the in-scope population at `bc7bc36` is **768**, with 3 files matching only via a `VR-` id. The corpus also grows with every new file citing a requirement, so a slice re-derives both numbers rather than quoting these. The auditor's pinned sweep at `89dd2b1` further corrects the note's own §5.6 evidence in two material places — `backend/src/app` and `backend/tests` each claim roughly the *combined* backend total (measured 88 + 93 + 28 = 209 against ~410 claimed), and `backend/migrations` is claimed at 3 against 28 measured — so W37-6's leaf plan is written from that sweep, never from §5's table. **Eleven slices** cut from §8's stages S1–S4 by `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`: four building the instruments in parallel, one building the migration script against a fixture corpus, **one supervised run that moves the whole corpus and must land at a gap with no open branches** and is never fanned out, four applying the conventions, and one proving acceptance (j) and (k). **Supersedes WK-695 in part** — see that row. **Decision points — updated 2026-09-02.** The plan recorded eight, two disposed of in it. **DP-1, DP-2 and DP-3 are ruled** as Rulings 66, 67 and 68 (`docs/rulings/INDEX.md#2026-09-02-w37-migration-preconditions-rulingsmd`), together with **RL-990** on a fourth point raised during execution — §1.5's vendored-skill criterion names `graphify`, `systematic-debugging` and the `vue-*` skills as vendored while defining vendored as *"anything shipping its own `LICENSE`"*, which exactly two of twenty-eight do; the parenthesis is ruled a gloss, not a detector. **Two consequences this row must carry.** First, **DP-2 blocks W37-4, not only W37-6** — item (d) and check 36 read one shared constant, so the earlier slice carries the earlier date. Second, **RL-987 enlarges W37-6's commit** by folding the creating instruments into it, ruled as a criterion — every instrument whose output checks 30–39 test — with the note's seven as a floor and `git-hygiene` and the skills README named for explicit disposition; **the maintainer's go-ahead for W37-6 must disclose that enlargement**, which the existing precondition does not cover. Still open: **DP-6**, blocking W37-9, discharged by a dated maintainer line on that slice's PR (`CLAUDE.md` §12 reserves an amendment to what that file requires), and **DP-4**, non-blocking, applied at W37-11. **`CLAUDE.md` §5's never-renumber rule yields to this work**, at two sites, by the maintainer's dated precedence ruling of 2026-09-01; a rule that yields still yields visibly. **Acceptance:** the note's §7 (a)–(k) **Progress, 2026-09-02.** **S1 complete** — W37-1 the standard and thirteen templates, W37-2 `doc-id.py`, W37-3 `doc-index.py`, W37-4 `audit-docs.py` checks 30-39 with ten broken-input proofs. **W37-5 merged**: `migrate` built and proven on a fixture corpus, then hardened after four defects were found in already-merged code by running it against the real tree. **W37-6 has not run and its go-ahead has not been asked for.** **Rulings 70-80 filed** since this row's decision-point clause was written; note especially that **RL-970 withdrew RL-987's acceptance item 2** rather than sharpening it — run as written it returned zero for four of thirteen instruments, so it would have ordered them removed from the commit that exists to carry them. **Four discovery defects are filed against merged W37-5 code and owned by W37-6**: every `_discover_*` function was written against the fixture corpus and four do not match the real tree — the roadmap (41 works, 0 converted, success reported) and the register (0 discovered) are guarded but their patterns unfixed; closure-records (21 headings, 10 records) is fixed by accounting for every heading; `plan-reviews` is neither fixed nor guarded — **its figures here were wrong and are corrected 2026-09-02**: the file has **14** `###` headings (11 reviews, 3 non-review sub-content), not 15, and `_discover_plan_reviews` produces **10** records, not 12. `_REVIEW_HEADING_RE` requires the date to end the heading line and `Plan review 9`'s carries trailing text, so it is never discovered and its whole body — with three sub-content headings — folds into `Plan review 1`'s record, dated fifteen days earlier. The same end-anchor defect PR #585 fixed for `closure-records.md`. The file-level guard cannot see it: it trips on zero, and this is ten of eleven. Measured by running the function at `ffac8ba`; the original figures were relayed from a report rather than run. See `docs/rulings/RL-00969-w37-6-s-go-ahead-is-withheld-the-maintainer-s-decision-of-2026-09-02-and-what-yet-costs.md`, and three of its headings carry no date at all, so the per-heading model may be the wrong shape for that file. **The guards catch zero-discovered, not undercount** — they would not have caught the closure-record defect that found them. Also owned by W37-6: `is_vendored`'s `LICENSE` probe, which RL-990 rejected and RL-973 re-assigned as a class with a sweep, and the roadmap restructure itself, deferred because Rulings 79 and 80 declare its target parsers wrong with the fixes not yet landed. **W37-5b inserted 2026-09-02** by the lead's decision at `docs/plans/PL-00956-w37-5b-the-lead-s-decision-on-the-obligations-proposal-2026-09-02.md`, deciding §7 of the obligations list (`docs/plans/PL-00961-w37-6-everything-it-owns-before-the-run-one-list-with-each-item-s-state-and-what-discharges-it.md`, 39 obligations, none in a fixed state). It sits between W37-5 and W37-6 and carries the pre-run preconditions: the four discovery defects, RL-985's census, Rulings 79/80's parser fix, RL-973's three-site `is_vendored` class, F76's unguarded `build_corpus` call, and the two silent discovery functions the guards never covered — sixteen items, each provable on deliberately broken input outside the irreversible commit. **The deciding fact is that W37-6 cannot pass its own acceptance item 13 until this lands**: exactly two tracked files meet that item's description and the shipped `LICENSE` probe treats neither as vendored, so the run rewrites both. Two of its rows are group A but not this slice's to build — `plan-reviews.md`'s heading mis-nesting stays with the lead so an executor does not restructure the document its own parser fix is tested against, and the identifier standard's §8-versus-Ruling-66 stage-boundary conflict is routed to the decision-maker because re-cutting a stage of an accepted standard may be an amendment reserved to the maintainer. A slice is named here rather than given a row of its own, which is how every slice in this file is recorded. **W37-5b progress, corrected 2026-09-02 — the paragraph above is stale from the moment of insertion and is kept, not rewritten, because it is what the slice decision itself pointed at; this sentence is the update.** All sixteen built rows have landed, each proven on deliberately broken input against the real tree, not a fixture: the roadmap now converts 41 of 41 works (`4cbfa62`, rows 2/91/92, reproduced independently at `d47a5f5`: phase totals 7+5+14+8+7=41) and the register 73 of 73 rows (`4cbfa62`, row 3/34); the plan-reviews heading anchor and RL-985's census land together (`4367cf7`, row 1: 10 of 14 headings becomes 11 of 14, with a class-wide guard rather than a single-file patch); the closure-records "not closed" abort becomes ten `LG-` records (`614c92c`, row 4, verified 8 `CR- work` + 1 `CR- phase` + 2 `RS- audit` + 10 `LG-` = 21, reproduced independently); the five silent discovery functions gain the same three-bucket census (`d7c9b08`, `a31d509`, rows 5/15/30/31); the vendored-skill class lands as a declared 28-member constant reconciled against ruff's exclude list, both empty both directions (`574d536`, rows 9/10/11, reproduced independently); F76's check-39 guard is fixed and proven on a malformed header without disarming the six checks behind it (`35c1488`, row 12); `doc-index.py`'s row and phase field policy is derived per family from the templates rather than hand-transcribed, and a template's own example block now parses through the real row parser that consumes it (`e7e1d24`, rows 8 and 13); RL-902–A3's family (row 6, derivation `04f47b2`, ruled `RL-` by Rulings 86–87) and the "Pending proposals" container's family (row 7, derivation `44ec54e`, ruled `RFC-` by Rulings 88/89/93) are both ruled, with the discovery code that would emit either as a draft not yet written — filed as **F81** and **F80** respectively, both blocking a real `migrate()` run today for reasons no group-A row promised to fix (see the closure record's §6). Row 14 (`plan-reviews.md`'s heading mis-nesting) was fixed by the lead directly (`2fbce0c`), not built inside the slice, as planned. Row 36 (§8 vs. RL-987) is ruled, not amended — RL-997: "§8 is sequencing… No amendment is needed and RL-987 stands as issued." A new dated leaf plan for W37-6 supersedes the frozen one by name (`2026-09-02-w37-6-migration-run-leaf-plan-v2.md`, `status: active` since RL-979 resolved its one blocking row), restating acceptance item 11 with RL-970's amendment in its own text. Two gaps each row's own author disclosed rather than called done, now register rows: F77 (RL-986 §4's `slice:` acceptance item is vacuously true — ruled by RL-1000, 2026-09-02, PR #614; the ruled instrument is not yet implemented, no owner named) and F78 (`_discover_roadmap`'s phase-spanning refusal has no fixture, owner W37-6). F79 carries obligations row 34's disclosed non-reuse of `register-lint.py`'s counting technique for the new census. F76's register row, previously mis-tracking this fix as owed to W37-6, is corrected in place. Full evidence and every unevidenced item's verdict: [`docs/closures/CR-01004-work-item-record-w37-5b-the-group-a-preconditions-slice.md`](closures/CR-01004-work-item-record-w37-5b-the-group-a-preconditions-slice.md). **W37-5b CLOSED 2026-09-02** on a clean audit and the lead's merge (`64f63ee`, PR #617), per `CLAUDE.md` §13 — a Slice's close is the lead's, not the maintainer's acceptance, and this line records it rather than requesting it. The audit carries one item outside the slice's own scope forward to W37-6: a real `migrate()` run would abort at **four independent guards** — this sentence read *"three"* until 2026-09-02 and the correction is Addendum B's to `docs/plans/PL-00958-w37-6-the-migration-run-the-go-ahead-ask-with-condition-6-discharged.md`, which found F80's gap covered by **two** guards one line apart, so clearing the census alone still aborted. Named by function rather than by line, because Addendum B B.2 records that every `doc-id.py` line number in eight tracked documents, this row included, was measured at a tree none of them names: in pipeline order `_check_multi_ruling_files_not_silently_unrecognised` (F81, the `RL-`-ruled RL-902/A2/A3 file with no discovery code), `_check_plan_reviews_heading_census` and `_check_headed_split_file_not_silently_unrecognised` (both F80, the `RFC-`-ruled "Pending proposals" container), and `_check_requirements_not_silently_unrecognised` (F82, four module-less `DEP-` ids in `docs/specs/00-overview.md` invisible to the module-coded matcher). Each is this slice's own new instrumentation correctly catching a pre-existing gap rather than a shortfall in any of the eighteen rows; all were unowned at this close; and they are disclosure for the W37-6 go-ahead ask, not grounds to withhold this slice's close. **Superseded 2026-09-02 as a statement of current state, and kept as the record of what W37-5b's close reported**: all four are cleared by `544b90c` (#629), verified by execution at `6e35b9c` in [`docs/closures/CR-01005-work-item-record-w37-5c-the-second-precondition-slice.md`](closures/CR-01005-work-item-record-w37-5c-the-second-precondition-slice.md) §2 — and a **fifth** abort point, `_discover_vendored_skill_manifests` (F88 limb 1), still fires on the real corpus and was never touched by that commit, so `migrate()` still cannot complete. **Superseded 2026-09-02 (PR #649) for the fifth point and kept as the record of what W37-5c's close reported: it is cleared.** `_discover_vendored_skill_manifests` classifies with `_front_matter_state`, which is textual and cannot raise, and returns a closed partition instead of a list — clearing the abort *and* the silent skip of 25 of 28 manifests that the same wrong predicate caused. Verified as a whole run rather than as one function: `migrate()` reaches `_write_document_drafts`, its first write, on a git-tracked snapshot of the real corpus with the tree byte-unchanged, while the shipped `doc-id.py` at `c888b61` aborts on that identical snapshot at `.claude/skills/create-adaptable-composable/SKILL.md:6`. **That is five of five cleared, and no sixth abort point exists before the first write** — the replay reached the first write rather than enumerating the pre-write calls, so a call nobody listed cannot be missed by it; a sixth appearing inside any `_discover_*` reds `test_exactly_one_discovery_writer_claims_the_closure_readmes`. **It does not say the run succeeds, and the first thing past the first write is a mid-write crash.** Running `migrate()` to completion on a throwaway snapshot of the real corpus — never the repository — raises `KeyError: 'RS'` inside `_write_document_drafts` **after writing 125 of the 290 document drafts and deleting none** — 165 never reached: `_discover_closure_records` emits two `RS-` document drafts from `docs/closures/INDEX.md#closure-recordsmd`, and neither `_DOCUMENT_FAMILY_DIR` (6 keys, no `RS`) nor `_MIGRATE_TEMPLATE_FILENAME` (7 keys, no `RS`) has an entry for the research family, though `docs/_templates/RS.md` exists. **This is task #34's mode, one layer down** — a partial migration rather than a clean abort — and it was invisible while the fifth abort point stopped the run before it. **It pre-exists the fix in this PR and is revealed by it, not introduced**: the shipped `doc-id.py` at `c888b61`, on a `c888b61` snapshot with only the fifth abort neutralised, raises the identical `KeyError` after the identical 125 writes. **The count was first given here as 126 and is corrected**: that figure counted `scripts/__pycache__/register-lint.cpython-312.pyc`, a bytecode cache the import machinery wrote, as a migration output. 125 is measured by tracing every `Path.write_text` the real writer performs — 125 calls, 125 distinct paths, none repeated, none outside `docs/` — and agrees with the first `RS` draft sitting at index 125 of the 290, read inside `_write_document_drafts` rather than reconstructed from the discovery order (a reconstruction that disagreed by one and is discarded). **Fixed, and the sentence this replaces was wrong.** It read *"what the `RS-` family's target directory and template are is a disposition, not a defect with one right answer, and it is the lead's"* — **RFC-937 §1 already states both**, so there was nothing to dispose of. Its Research row gives `RS` the directory `docs/research/`, the unit *one spike, measurement or audit*, and the kind vocabulary `spike` · `measurement` · `audit` (quoted verbatim in `docs/findings/FD-01025-discovery-does-not-reach-two-populations-5-2-routes-one-aborts-every-real-run-one-is-silent.md`, which is not a table row and can carry the row's own pipes); `docs/_templates/RS.md` exists; and D13 routes `RS- kind: audit` to `auditor` — which `_discover_closure_records` already sets. **The writer was incomplete, not the classifier**; emitting `RS` for two audits sitting in a closure-records file is correct and was not changed. **The set was closed rather than the instance**: every prefix a `_Draft(materialize="document")` can carry is derived from the source by an AST walk — resolving a variable through its assignments and a parameter through its call sites — and independently by running every discovery over the real corpus. The two agree exactly: **`{ADR, CR, LG, PL, RFC, RL, RS}`**, and `RS` was the only member missing from either table, missing from **both**. `REFERENCE` sits in `_MIGRATE_TEMPLATE_FILENAME` and not in `_DOCUMENT_FAMILY_DIR` legitimately — it is stamped in place and carries no `id:` — and that asymmetry is now asserted as an equality so a second one cannot appear unnoticed. `_check_every_document_draft_is_placeable` refuses in the pre-write span if a document draft names a prefix either table lacks; it **cannot fire on any corpus**, only on a source change, so it adds no corpus-triggerable stop while converting a mid-write `KeyError` into a named refusal. With this, `migrate()` **runs to completion** on a throwaway snapshot of the real corpus — **1,085 files written *as `MigrateResult.files_written` reports it*, deduped; the count of distinct paths actually written is 1,087**, the two the report omits being `docs/INDEX.md` and `docs/REDIRECTS.csv` (`_write_redirects` uses `.open("w")`, which a `write_text` trace does not see) — 202 deleted, and no seventh failure follows. **W37-5c inserted 2026-09-02** by the maintainer's dated line withholding W37-6's go-ahead a second time (`docs/plans/PL-00958-w37-6-the-migration-run-the-go-ahead-ask-with-condition-6-discharged.md` §8) and cutting a second precondition slice, recorded at `docs/plans/PL-00957-w37-5c-the-slice-decision-and-gap-2-ruled.md`. It sits between W37-5b and W37-6. **Its scope criterion is wider than the three abort guards and is the maintainer's own: everything that stops *or blinds* the run and is provable on broken input outside it** — a check that cannot fail blinds the run as surely as a guard that aborts stops it. Six items: F80, F81 and F82; the discovery-and-stamp path for `.claude/skills/`, `.claude/agents/`, `.claude/roles/` and the README population; the three unparseable vendored manifests; **R84 §4 item 2 built** (vacuous at birth — `_stamp_header` skips `slice` unconditionally, so nothing can write the value the check reads); and **R86 §4 item 3 rebuilt so it can pass on some input** (after `2e48960` the value it demands cannot be produced by any input, by construction). Same discipline as W37-5b: red-before/green-after, and the arithmetic closes over the real corpus, not a fixture. **Gap 2 is ruled in the same instruction** so the slice builds against a rule: `Phase` takes `lead`, `WK` takes `maintainer`, skills take one standing `lead`, `contracts/` takes `executor`; the README row is routed to the planner. **Two of those changed on challenge and the slice decision's §4 carries both**: `contracts/` cannot take a generator-emitted header at all — 59 of its 61 files are JSON, which has no comment syntax, so front matter makes them unparseable — and the maintainer's pre-authorised `generated: true` exemption in check 35 is taken instead; and `WK`'s author-equals-acceptor collapse is real but narrower than `Phase`'s, because §1.6's WK cell names no routine maintainer of the row for the value to have been read from. **The re-ask is one document**, not a package: §3 and §4 re-derived at that tree, the addendum merged and re-run, and F80-F82 shown cleared by execution. **W37-5c CLOSED 2026-09-02** on a clean audit and the lead's merge (`c888b61`, PR #647), per `CLAUDE.md` §13 — a Slice's close is the lead's, not the maintainer's acceptance, and this line records it rather than requesting it, on W37-5b's precedent one clause above. Every scope item delivered, scored item by item in the record's §1 and §3; the four abort points named above are verified cleared **by execution** at `6e35b9c`, which is the re-ask condition *"F80–F82 shown cleared by execution"* discharged. **The slice's most valuable output contradicts its own headline: `migrate()` still does not complete.** **Four W37-6 preconditions were found and none of them existed on any prior list** — not in the map plan, not in either leaf plan, not in the withheld go-ahead's six conditions; each was produced by building the slice and reading what its own new instruments then reported, which is the sentence a W37-6 planner needs. **F87** — `_id_scope_documents()` returns **1** document at `d8d6e3f`, so checks 30–39 see **0 of the 65** files the widened `_ID_SCOPE_ROOTS` was meant to reach: the *glob*, not the roots, bounds those checks, and this one **passes** rather than aborting, so it blinds the run where F80–F82 stopped it. **F88 limb 1** — `_discover_vendored_skill_manifests` is the **fifth abort point**, reclassified from *blinds* to *stops* by the record's §2 row 5, pre-write and therefore a clean abort rather than a partial migration. **F90** — check 37 reds **95 of 95** ruling documents at migration, its `^##\s+` detector unable to see the `###` nesting every ruling uses — a count produced by running `doc-id.py`'s unmodified splitter against a clone to materialise real stamped `RL-*.md` files and then the real `check_shape()`, at `4df1c45`. **That tree resolves inside this checkout and nowhere else**: it is PR #640's tip, and #640 squash-merged as `dc1666f`, so `4df1c45` is an ancestor of no remote ref and a single local branch is all that keeps it reachable — a fresh clone cannot resolve it today, and §5.4's own gap condition, which releases every agent worktree before the migration branch is cut, deletes the last ref that does. **F90's disposition should re-pin the measurement to a reachable commit or re-run it**, rather than add a tree it already has, including the thirty written after the flag-day *to comply*; it predates the flag-day commit, which is why that commit merged rather than being held. **F92** — 53 files deferred out of §4 step 5's Reference stamp set, recorded only in a squash-commit body, which no planner reads; W37-6's §7.1 Task 1 discharges it. **F86**, **F89** and **F91** were also filed; F86 carries an explicit decay to the next `CLAUDE.md` §14 plan review, its own row having named this close as the owner-assigning event. Full evidence and every finding's adopted verdict, including the four the lead amended: [`docs/closures/CR-01005-work-item-record-w37-5c-the-second-precondition-slice.md`](closures/CR-01005-work-item-record-w37-5c-the-second-precondition-slice.md). **Superseded 2026-09-02 (PR #649) as a statement of current state, and kept as the record of what W37-5c's close reported:** the fifth abort point is cleared and so is the mid-write `KeyError: 'RS'` behind it, which no run had been able to reach before it was; on a throwaway snapshot of the real corpus `migrate()` now runs to completion. The clause earlier in this row carries the evidence and the predicates; this sentence exists only so the row does not end on a state that has moved.


**Goal:** DAG designer, rate tables, reference data, real-time + batch scoring, dislocation.

**Demo-able outcome:** **`WF-699` end to end** plus the deployment half of `WF-701` — an
approved model becomes rate tables, becomes a rating version, passes regression and
dislocation, and serves a live quote inside the latency budget.



### RFC-895 … RFC-898 — the four notes, reconciled 2026-09-01

**A note decides nothing** (`docs/rfcs/README.md`). Four working notes are filed and
`open` — proposed, not adopted — and each proposes work large enough that adopting it would
change this page. They are recorded here so a reader cannot mistake "filed" for "planned",
and so the reconciliation has a fixed moment rather than happening whenever someone
remembers. **Reconciled 2026-09-01 — accepted as proposed, all four dispositions dated in the
reconciliation's own acceptance line.** Each note's row below records its conversion; the note
statuses remain the record of what landed, not of adoption.

**The rule, three clauses:**

1. **All four are reconciled at the WK-671 close — at the same moment as its `CLAUDE.md` §14
   plan review, but as its own dated record, not inside it.** The trigger is shared because
   §14's is already fixed at every workstream close, and because §14 asks whether the plan
   still says the right thing now that some of the work is real — an unadopted proposal is
   precisely a claim about what the plan is missing. **The documents stay separate because
   they are different instruments**: a §14 review answers five fixed questions and outputs a
   proposal carrying one maintainer acceptance line, while a reconciliation walks each note
   section by section and outputs adopt / reject / defer per note. **Bundling them would make
   that single acceptance line ambiguous** — accepting "the review" would silently accept four
   adoptions — and the RFC-840/841 reconciliation set the precedent by running as its own
   pass rather than writing a proposal straight into the governed file.
2. **An adopted note converts to a Work row** — here, under the phase that will carry it,
   with a workstream id and dependencies like any other row. Adoption is not a status change
   on the note; it is a row on this page. Until that row exists, nothing is scheduled.
   **The reconciliation's acceptance line is the maintainer's** (instruction, 2026-08-30),
   which is the same rule `CLAUDE.md` §12 applies to a Work close and for the same reason:
   adopting a note **schedules work**, and scheduling is not a lead's to decide. So the
   reconciliation is written as a **proposal** — each note carried to a recommended
   disposition with its reasoning, and the acceptance line left **undated** until the
   maintainer signs it. **No adoption is implemented before that signature**, and no Work row
   is added on the strength of a recommendation alone. **Added 2026-09-01, accepted the same
   date — the exception the reconciliation's §7 proposed:** a note may land work ahead of its
   reconciliation under a dated maintainer delegation or a light-path ruling, and the
   reconciliation then records what landed rather than authorising it. Three recorded
   instances: RFC-895's Slices A–D and RFC-898's S1/S2 (both 2026-08-30), and RFC-897's four
   investigation slices and eleven rulings (2026-09-01).
3. **A note that is neither adopted nor rejected keeps a named owner and a next trigger.**
   Silence is not an outcome, the same rule `CLAUDE.md` §13 applies to an unevidenced
   requirement. A rejected note is recorded as rejected, with its date and reason, and its
   number is retired with it.

**Nothing here is committed work.** The table is the reconciliation's agenda, not a plan.

| Note | Proposes | State entering the reconciliation |
|---|---|---|
| [`RFC-895`](rfcs/RFC-00895-a-machine-readable-core-for-the-delivery-process-so-the-rules-a-script-can-check-stop-being-prose.md) | A machine-readable core for the delivery process — a checkable extract of the rules that are prose today | **Landed 2026-08-31 — all eight slices merged** (`33b5ef1`, `0be9c3c`, `97965be`, `b551060`, `26de823`, `53257b4`, `9e8783d`): the process core is filed and held by `audit-docs` checks **26** (citations) and **27** (content digest), the plan validator is check **28**, artifact B and the C2 retry-cap hook are built. **C3 dissolved by RL-920, not built.** Closed at [`docs/closures/CR-00933-audit-record-nt-0012-0013-0014-adoption-docs-audit-checklists-work-item-close-md.md`](closures/CR-00933-audit-record-nt-0012-0013-0014-adoption-docs-audit-checklists-work-item-close-md.md), accepted by the lead under the adoption record's §1.1 delegation. **Three findings carried open, not absorbed**: **F61** — C2's hook layer is bypassable and, unlike the C3 that RL-920 dissolved, has no CI-equivalent backstop; **F58** — artifact B has no live writer; **F57** — zero retry-cap cycles have run, so §7's caps still have no data toward their own revisit condition. **Reconciled 2026-09-01 — adopted; converted to WK-693 above** |
| [`RFC-896`](rfcs/RFC-00896-the-register-is-a-ledger-evidence-is-a-file.md) | Naming the register's decision grammar, a decay rule for unowned rows, a linter for what is named, splitting ledger from evidence, and generating the owed list a close compiles by hand | **Landed 2026-08-31 — P1–P5 all merged** (`fa87086`, `890b06e`, `f99b55d`, `cfed4f0`, `6b3459a`, `365ad18`, and the `lead.md` enter step): the decision grammar is held by `audit-docs` check **29** via `scripts/register-lint.py`; `scripts/register-owed.py` generates the owed list a close previously compiled by hand, cited in both close checklists and in `lead.md`; the ledger/evidence split is real at `docs/audit/findings/` with **F27** migrated as the worked exemplar (4268 → 818 chars), and migration is opportunistic-on-amendment with an aggregate residue line making that claim falsifiable (**38 of 61** rows over the 1000-character threshold at landing). **Three findings filed from the work itself**: **F62** — `03` §4.4's `timing_ms` example disagrees with what `score_one` emits; **F63** — ten WK-671-attributed register rows appear in no WK-671 closure-record findings section, all predating the close, disposition reserved to the maintainer because reopening a Work close is theirs alone (`CLAUDE.md` §13); **F64** — check 29's own parser read 48 of 59 rows while reporting `OK`, one of three silent row-losses in that script fixed the same day. **One impact-matrix row deliberately not built**: no `docs/plans/<date>-nt-0015-adoption.md` was filed, and none has been back-dated — the slices were dispatched and merged without one, and writing a plan today for work already landed would record a sequencing that did not happen. Named here rather than closed over; the deviation is the next §14 review's to dispose of. **Reconciled 2026-09-01 — adopted; converted to WK-694 above** |
| [`RFC-897`](rfcs/RFC-00897-file-taxonomy-reference-coding-and-custody-investigation-rev-2.md) | A closed file taxonomy across `docs/` and `.claude/`, a reference-coding standard, an ownership map per category, and an audit of whether each category is genuinely created-read-retired | Filed 2026-08-30, `open`. Includes a proposed relocation of the notes themselves, so its adoption would move the other three. **Reconciled 2026-09-01 — adopted; converted to WK-695 above** |
| [`RFC-898`](rfcs/RFC-00898-a-public-repository-needs-a-public-face.md) | A root `README`, a `SECURITY.md` with a private reporting channel, a `CONTRIBUTING.md` and intake templates | Filed 2026-08-30, `open`. **The repository went public on 2026-08-30 with none of these**, so this one has a live exposure behind it rather than a tidiness argument — see [`docs/process/security-posture.md`](process/security-posture.md). §5's three policy questions are **ruled** — [`docs/rulings/RL-00914-rfc-898-the-maintainer-s-three-policy-decisions-recorded-2026-08-30.md`](rulings/RL-00914-rfc-898-the-maintainer-s-three-policy-decisions-recorded-2026-08-30.md) — and that record is explicit that the ruling authorises the *content*, not the *adoption*: the note **stays `open`** here, its disposition still the joint reconciliation's. Landing under the note's own §7 light path ahead of that reconciliation, the same way RFC-895's Slices A–D landed ahead of it (row above): **S1** (`SECURITY.md` + the two repository settings) then **S2** (`README.md`, `CONTRIBUTING.md`, `.github/` templates), as separate commits, both filed 2026-08-30. **Reconciled 2026-09-01 — adopted; converted to WK-696 above** |

### Requirement coverage

≈ **67 `RATE` + ~25 remaining `PLAT`** requirements, plus the `MODEL` requirements WK-690 carries over (FR-95, FR-144/145/150 and the `expression` half of §4.6/§4.7). **FR-95 added 2026-08-19, accepted by the maintainer 2026-08-22**: `expression` factors are an expression feature, and the verdict on file sends them to “the slice OQ-573 gates”, which is this row — but the list named only the objective half, leaving the requirement owned by a slice that did not list it.

### Top risks

| Risk | Mitigation |
|---|---|
| ~~OQ-614 — ZEN decimal semantics invalidates ADR-706~~ **retired 2026-08-14**: the engine uses `rust_decimal`, so this risk did not materialise. Replaced by two silent-failure risks at the boundary (FR-273/274) | Re-scoped S1 before WK-669; integer-minor-units is no longer needed as a mitigation |
| NFR-489 (p99 < 50 ms) missed and expensive to recover | Build the latency harness in WK-671 alongside the evaluator, not after |
| DAG designer is under-estimated | It is a graph editor with live validation — treat as its own project with its own spike |
| Rate table scale (vehicle × area = millions of cells) | OQ-616; the recommendation already sets a spill threshold |

---

## P3 — Governance
status: active
opened: 2026-08-14
target: ~
gates: ~
exit criteria: ~
works: WK-676, WK-677, WK-678, WK-679, WK-680, WK-681, WK-682, WK-691

### WK-676 — Full scoped RBAC, custom roles, break-glass

```yaml
id: WK-676
family: work
title: Full scoped RBAC, custom roles, break-glass
status: active
created: 2026-08-14
owner: maintainer
phase: P3
```

From “Workstreams” (line 467): Full scoped RBAC, custom roles, break-glass | `06` FR-342, FR-343, FR-344, FR-345, FR-346, FR-347, FR-348, FR-349


### WK-677 — Approval policies, escalation, evidence enforcement, attestations

```yaml
id: WK-677
family: work
title: Approval policies, escalation, evidence enforcement, attestations
status: active
created: 2026-08-14
owner: maintainer
phase: P3
```

From “Workstreams” (line 468): Approval policies, escalation, evidence enforcement, attestations | FR-351, FR-352, FR-353, FR-354, FR-355, FR-356, FR-357, FR-358, FR-359, FR-361, FR-363


### WK-678 — **Approvals inbox with inline evidence**

```yaml
id: WK-678
family: work
title: **Approvals inbox with inline evidence**
status: active
created: 2026-08-14
owner: maintainer
phase: P3
```

From “Workstreams” (line 469): **Approvals inbox with inline evidence** | FR-358 — "the screen where the platform earns its keep"


### WK-679 — Audit explorer, chain verification, export

```yaml
id: WK-679
family: work
title: Audit explorer, chain verification, export
status: active
created: 2026-08-14
owner: maintainer
phase: P3
```

From “Workstreams” (line 470): Audit explorer, chain verification, export | FR-368, FR-369, FR-370, FR-371, FR-372, FR-374, FR-375


### WK-680 — Dossier generation, commentary blocks, PDF, point-in-time regeneration

```yaml
id: WK-680
family: work
title: Dossier generation, commentary blocks, PDF, point-in-time regeneration
status: active
created: 2026-08-14
owner: maintainer
phase: P3
```

From “Workstreams” (line 471): Dossier generation, commentary blocks, PDF, point-in-time regeneration | FR-376, FR-377, FR-379, FR-380, FR-381


### WK-681 — Regulatory evidence export

```yaml
id: WK-681
family: work
title: Regulatory evidence export
status: active
created: 2026-08-14
owner: maintainer
phase: P3
```

From “Workstreams” (line 472): Regulatory evidence export | FR-382


### WK-682 — Model risk tiering, if OQ-636 is accepted

```yaml
id: WK-682
family: work
title: Model risk tiering, if OQ-636 is accepted
status: active
created: 2026-08-14
owner: maintainer
phase: P3
```

From “Workstreams” (line 473): Model risk tiering, if OQ-636 is accepted | Small addition to Approval Policy


### WK-691 — **Proxy assessment** — an insurer-supplied reference table, association measures (mutual information, exposure-weighted AUC), evidence attached to the approval request

```yaml
id: WK-691
family: work
title: **Proxy assessment** — an insurer-supplied reference table, association measures (mutual information, exposure-weighted AUC), evidence attached to the approval request
status: active
created: 2026-08-14
owner: maintainer
phase: P3
```

From “Workstreams” (line 474): **Proxy assessment** — an insurer-supplied reference table, association measures (mutual information, exposure-weighted AUC), evidence attached to the approval request | Added 2026-08-15 by OQ-581's decision: `02` FR-91. **Evidence, never a block** — it belongs beside `04` FR-302's outcome disparity report, and both exist to inform a legal judgement the platform must not make


**Goal:** RBAC, approvals, audit UI, model documentation generation.

**Demo-able outcome:** **`WF-702` end to end** — a custom objective authored, certified,
two-approver reviewed, used, and audited — plus a generated dossier that would survive
external review.



Much of the *write path* already exists from Phase 1 (§5). Phase 3 is largely the
**surfacing** of it — which is why it is comparatively low-risk despite being 43
requirements.

---

## P4 — Optimisation & Monitoring
status: active
opened: 2026-08-14
target: ~
gates: ~
exit criteria: ~
works: WK-683, WK-684, WK-685, WK-686, WK-687, WK-688, WK-689

### WK-683 — Demand models, price-variation reporting, elasticity with CIs

```yaml
id: WK-683
family: work
title: Demand models, price-variation reporting, elasticity with CIs
status: active
created: 2026-08-14
owner: maintainer
phase: P4
```

From “Workstreams” (line 494): Demand models, price-variation reporting, elasticity with CIs | `04` FR-277, FR-278, FR-279, FR-280, FR-281, FR-282, FR-283


### WK-684 — Optimisation runs, constraints, binding analysis, frontier

```yaml
id: WK-684
family: work
title: Optimisation runs, constraints, binding analysis, frontier
status: active
created: 2026-08-14
owner: maintainer
phase: P4
```

From “Workstreams” (line 495): Optimisation runs, constraints, binding analysis, frontier | FR-284, FR-285, FR-286, FR-287, FR-288, FR-289, FR-290, FR-291, FR-292, FR-293


### WK-685 — GIPP checks, price-walking, disparity reporting

```yaml
id: WK-685
family: work
title: GIPP checks, price-walking, disparity reporting
status: active
created: 2026-08-14
owner: maintainer
phase: P4
```

From “Workstreams” (line 496): GIPP checks, price-walking, disparity reporting | FR-294, FR-297, FR-298, FR-299, FR-300, FR-301, FR-302


### WK-686 — Materialisation into rate tables

```yaml
id: WK-686
family: work
title: Materialisation into rate tables
status: active
created: 2026-08-14
owner: maintainer
phase: P4
```

From “Workstreams” (line 497): Materialisation into rate tables | FR-303, FR-304, FR-305, FR-306


### WK-687 — Monitoring: monitors, drift, A/E, demand, rate achieved, operational

```yaml
id: WK-687
family: work
title: Monitoring: monitors, drift, A/E, demand, rate achieved, operational
status: active
created: 2026-08-14
owner: maintainer
phase: P4
```

From “Workstreams” (line 498): Monitoring: monitors, drift, A/E, demand, rate achieved, operational | `05` FR-307, FR-308, FR-309, FR-310, FR-311, FR-312, FR-313, FR-314, FR-315, FR-316, FR-317, FR-318, FR-319, FR-320, FR-321, FR-322, FR-323, FR-324, FR-325, FR-326, FR-327, FR-328, FR-329, FR-330, FR-331, FR-332, FR-333


### WK-688 — Alerting lifecycle and routing

```yaml
id: WK-688
family: work
title: Alerting lifecycle and routing
status: active
created: 2026-08-14
owner: maintainer
phase: P4
```

From “Workstreams” (line 499): Alerting lifecycle and routing | FR-334, FR-335, FR-336, FR-337, FR-338


### WK-689 — Dashboards and monitoring packs

```yaml
id: WK-689
family: work
title: Dashboards and monitoring packs
status: active
created: 2026-08-14
owner: maintainer
phase: P4
```

From “Workstreams” (line 500): Dashboards and monitoring packs | FR-339, FR-340, FR-341


**Goal:** demand models, constrained optimisation, drift monitoring, GIPP consistency.

**Demo-able outcome:** **`WF-700` end to end** plus the monitoring half of `WF-701` — a rate
change proposed by the optimiser with GIPP evidence, deployed, then measured against what
it promised.



**Sequencing note:** WK-687 (monitoring) delivers value the moment Phase 2 is live and does
**not** depend on WK-683–WK-686. If Phase 4 is long, **pull monitoring forward** — a deployed
rating structure with no monitoring is the least comfortable state the platform can be in.

---

## 10. Decision gates

Which open questions must be answered before which phase. Answer them in this order and
you never block on a decision you have not reached.

| Gate | Questions | Count |
|---|---|---|
| ~~**Before Phase 1a**~~ ✔ **all decided** | ~~OQ-541~~, ~~OQ-640~~, ~~OQ-557~~, ~~OQ-558~~ *all 2026-08-14*, ~~OQ-562~~ *2026-08-15, raised and decided inside the phase by driving the exit demo*, ~~OQ-547~~ ✔, ~~OQ-588~~ ✔, ~~OQ-590~~ ✔, ~~OQ-591~~ ✔, ~~OQ-592~~ ✔, ~~OQ-556~~ ✔ *all 2026-08-19, raised and decided inside the phase*, ~~OQ-548~~ ✔, ~~OQ-593~~ ✔ *2026-08-21, raised and decided inside the phase — FR-22's delivery precedes the exit demo, FR-161 is a WK-661 obligation*, ~~OQ-572~~ ✔ *2026-08-22, raised and decided inside the phase from the first measurement of NFR-479 — it gated WK-661's closure, because the answer changes whether a delivered requirement is in breach* | 14 (0 open) |
| **Before Phase 1b** — *re-opened 2026-08-22* | ~~OQ-546~~ ✔ *2026-08-14*, ~~OQ-573~~ ✔, ~~OQ-579~~ ✔, ~~OQ-644~~ ✔, ~~OQ-543~~ ✔ *all 2026-08-15*, ~~OQ-544~~ ✔, ~~OQ-563~~ ✔, ~~OQ-582~~ ✔, ~~OQ-583~~ ✔ *all 2026-08-17*, ~~OQ-577~~ ✔, ~~OQ-639~~ ✔, ~~OQ-586~~ ✔ *all 2026-08-18*, ~~OQ-648~~ ✔ *raised and decided 2026-08-23 — how a chosen workspace reaches the API: a verified `Workspace-Id` request header, checked against the principal's own memberships, absent one refused rather than defaulted (`07` FR-397). `W6b-11` is unblocked as a decision and waits on WK-692's backend half*, ~~OQ-565~~ ✔ *2026-08-19 — raised in WK-661 and never placed on this table until it was decided, so the gate it belonged to had already closed; it gates WK-664's dataset list, which is Phase 1b work*, ~~OQ-587~~ ✔, ~~OQ-589~~ ✔, ~~OQ-594~~ ✔ *all 2026-08-21, raised in WK-661 and never placed on this table until decided — FR-173 delivered with the decision, FR-138's trigger is Phase 1b's job-latency measurement, FR-117's first slice is Phase 1b's*, ~~OQ-595~~ ✔, ~~OQ-596~~ ✔ *both raised **and decided** 2026-08-22, out of the two modelling decisions taken that day — the first a live silent mis-fit, the second an unbounded diagnostics sweep. This gate had been closed since 2026-08-21; it re-opened rather than pretending they arrived earlier, and closes again the same day. Neither landed where its question pointed: FR-84 supersedes the offset **intent** on a layer argument, the duplication argument having failed checking, and half of the second was withdrawn as a no-op. Each raised a successor owned by WK-690, which is Phase 2 — placed at that gate rather than held here*, ~~OQ-599~~ ✔, ~~OQ-600~~ ✔ *both raised 2026-08-22 by W32-1's constraint guard and never placed on this table at all — the fifth time a question has been decided without appearing here, and the reason the count below is a recount rather than an increment. The first was decided 2026-08-22 (an inert `seed` keyword removed), the second 2026-08-23 into FR-158. Both gate Phase 1b slices, so they belong at this gate and not a later one*, ~~OQ-605, OQ-606, OQ-607, OQ-608, OQ-612, OQ-611, OQ-610~~ ✔ *placed 2026-08-26* | 28 (0 open) |
| **Before Phase 2** — *re-opened 2026-08-22* | ~~OQ-614~~ ✔, ~~OQ-615~~ ✔ *both decided by spike*, ~~OQ-575~~ ✔ *2026-08-17*, ~~OQ-576~~ ✔, ~~OQ-584~~ ✔, ~~OQ-616~~ ✔, ~~OQ-617~~ ✔, ~~OQ-619~~ ✔, ~~OQ-642~~ ✔, ~~OQ-632~~ ✔ *all 2026-08-18*, ~~OQ-571~~ ✔ *2026-08-22 — decided into FR-209 and FR-210; the continuous-effect gate it turns on is WK-690's, which is Phase 2 work*, ~~OQ-597~~ ✔, ~~OQ-598~~ ✔ *both raised 2026-08-22 out of the two modelling decisions taken that day and **both decided the same day**, before the gate they were filed against — the first into FR-86, the second into FR-177 and FR-178. Filing them here rested on a claim that held for one of them: "both have interim behaviour in place, so neither blocks" is true of `diagnostic`, which really is refused, and **false of the interaction**, whose skip-and-record leaves a sparse cross raising `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` out of `compute_gbm_diagnostics` (FR-178). Deciding both early cost one day and turned an interim nobody had exercised into a measured defect with a remedy. WK-690 still owns the slices; what it no longer owns is the choice* | 13 (0 open) — *recounted 2026-08-23: this read `13 (2 open)` while every one of its thirteen ids was struck. The two it meant were decided on the day they were filed here, and the count was written from the intent to file rather than from the row* |
| **Before Phase 3** — *re-opened 2026-08-29* | ~~OQ-633, OQ-634, OQ-635, OQ-636, OQ-637, OQ-638~~ ✔ *2026-08-18*, ~~OQ-540~~ ✔ *decided 2026-08-15 — ADR-710, and it changes what WK-674 builds in Phase 2 rather than waiting for Phase 3*, ~~OQ-581~~ ✔ *evidence in Phase 3 (WK-691), never a block*, **OQ-620** *(raised 2026-08-29 from WK-671 Task 1.2)* | 9 (1 open) |
| **Before Phase 4** | ~~OQ-621, OQ-622, OQ-623, OQ-624, OQ-625~~ ✔, ~~OQ-626~~ ✔ *resolved 2026-08-14*, ~~OQ-627, OQ-628, OQ-629, OQ-630, OQ-631~~ ✔, ~~OQ-560~~ ✔ *decided 2026-08-14 — out of scope*, ~~OQ-647~~ ✔ *raised and decided 2026-08-23 out of the scheduling decision: an idempotency key naming a Job that already failed. FR-404's 24-hour window is withdrawn, keys are permanent, and a terminally failed Job releases its key so the period can be attempted again (`07` FR-414). Decided at this gate rather than deferred to it because WK-687 would otherwise build FR-413 against an unanswered question; the code delta stays WK-687's* | 13 (0 open) |
| **Deferred / any time** | ~~OQ-542~~ ✔, ~~OQ-545~~ ✔ *both decided 2026-08-14*, ~~OQ-559~~ ✔, ~~OQ-561~~ ✔, ~~OQ-564~~ ✔ *all decided 2026-08-14*, ~~OQ-574~~ ✔, ~~OQ-578~~ ✔ *amended 2026-08-23 — the decision stands, its two-number evidence clause is withdrawn*, ~~OQ-580~~ ✔ *all decided 2026-08-15*, ~~OQ-601~~ ✔ *raised and decided 2026-08-23 out of that amendment: what evidence stands beside an interaction candidate, once a per-pair exposure share is shown to be `1.0` by construction — its **holdout strength ratio**, the ranker's own statistic recomputed on the holdout partition and published against the in-sample value (`02` FR-168). Deferred no longer as a question; the panel that displays it is still unscheduled*, ~~OQ-585~~ ✔ *2026-08-18 — reopened by its own trigger, the first consumer of an aggregate interval*, ~~OQ-566~~ ✔ *2026-08-19 — a deferral with a trigger (FR-67), raised in WK-661 and never placed here until decided*, ~~OQ-618~~ ✔ *raised 2026-08-19 in the FR-137 slice and placed 2026-08-21*, ~~OQ-641~~ ✔, ~~OQ-643~~ ✔, ~~OQ-645~~ ✔ *all decided 2026-08-23 on the maintainer's instruction to resolve them: no Dagster (FR-413), no workspace quota (FR-415), and a local-only identity provider behind an opt-in profile (FR-398, FR-437). The middle one is a **rejection**, not the deferral its recommendation asked for — that deferral's trigger had been dead since ADR-710*, ~~OQ-646~~ ✔ *decided 2026-08-22 and left unstruck here for a day*, ~~OQ-569~~ ✔ *raised 2026-08-24 in WK-664 — whether a Column Profile's `pii_class` of `NONE` records "classified as not personal" or "never classified", and the same silence on `semantic_type`. Placed here because no phase blocks on it: the default is already live on every ingestion path and the frontend already renders it, so the answer changes what a displayed value **means**, not whether a slice can start. It is on this table on the day it was raised — six questions before it, each reached a decision before reaching a gate row, and the rows above record that as the defect it was*, ~~OQ-654~~ ✔ *raised 2026-08-24 in WK-664 — what `req-coverage.py` should do about three inflation modes that turned out not to be the three that were reported. Here rather than at a phase gate because it bears on every workstream close rather than on any one boundary: its live mode is clause-conflation, which no cheap instrument change reaches, so its legitimate discharge is a standing reporting rule plus a named §13 verdict on each conflated clause* ~~OQ-613~~ ✔ *raised 2026-08-26 out of the FR-141 ruling of that day — a surrogate's source is pinned by UUID while its slug-derived address resolves to the family's latest version; placed here because nothing blocks on it (the pin is exact; rendering and derived addresses are what is at stake)*, ~~OQ-550, OQ-551, OQ-552, OQ-553~~ ✔, ~~OQ-567, OQ-568~~ ✔, ~~OQ-570~~ ✔, ~~OQ-609~~ ✔, ~~OQ-649, OQ-650~~ ✔, ~~OQ-651, OQ-653~~ ✔, ~~OQ-655~~ ✔ *all placed 2026-08-26*, ~~OQ-555~~ ✔ *(raised 2026-09-03, RL-1044 §1.7; decided 2026-09-03, RL-1046 D6)* | 33 (0 open) |

**2026-09-03 — OQ-555 placed at Deferred.** *OQ-555 raised 2026-09-03 by the decision-maker out of RL-1044 §1.7. Placed here because nothing blocks on it today — `audit-docs.py` check 32 is gated on `docs/INDEX.md` existing and is quiet until it does — but note its real trigger is that index landing with the RFC-937 migration, not a phase boundary. The count is recounted rather than incremented: the id cell names 32 distinct ids once its ranges are expanded, all struck, so the cell was right at 32 (0 open) and is now 33 (1 open). **Raised separately with the lead: `OQ-554` sits on no gate row at all** — the omission `spec-change` warns about and that `audit-docs.py` does not check. It is not placed here, because placing another raiser's question is not this raiser's to do.*

**2026-09-03 — OQ-555 decided, the same day it was placed.** *RL-1046 D6 closes it on RL-1044 §1.7's option (a): the id standard's specimens become placeholders in RFC-937 §1.1 rule 3 and its verbatim lift at `docs/process/document-ids.md`, so no specimen can resolve through the generated `docs/INDEX.md`. The row is struck and kept, not deleted — what it now holds is the revisit appointment, which is the RFC-937 migration landing and check 32 activating with it. The count returns to 33 (0 open) by the same recount that produced 33 (1 open) above, not by decrement. `OQ-554` still sits on no gate row; that remains open with the lead.*

**2026-08-26 — OQ-613 placed at Deferred.** *OQ-613 raised 2026-08-26 out of OQ-604's ruling — a surrogate's source is pinned by UUID while its slug-derived address resolves to the family's latest version; placed here because nothing blocks on it (the pin is exact; rendering and derived addresses are what is at stake).* The row entry keeps its note free of OQ ids, because the decision-gate check counts every id a row cell contains and naming OQ-604 there would book a decided question as open — the table's other rows predate that rule, and their prose citations are the pre-existing drift this PR records rather than repairs.

2026-08-26 — the open half placed, the decided half recorded. Twenty open questions sat on no gate row; all are placed now — seven at Before Phase 1b (OQ-605, OQ-606, OQ-607, OQ-608, OQ-612, OQ-611, OQ-610) and thirteen at Deferred (OQ-550, OQ-551, OQ-552, OQ-553, OQ-567/568/570, OQ-609, OQ-649/650/651/653/655). Before Phase 4 reads 13 (10 open): OQ-626 resolved 2026-08-14. Eight decided ids are recorded rather than placed, the pattern the rows above record as the defect it was — OQ-549, OQ-539, OQ-538, OQ-602, OQ-603, OQ-604, OQ-652, OQ-656: each reached a decision without appearing on this table; the register is the record of each. Counts count the entry list, never prose citations; the id-free row-cell rule stands.

**2026-08-18 — the six `GOV` questions decided, and Phase 3's gate closes.** OQ-633 (the
audit chain stays per workspace and self-held, claimed as tamper-*evident* against modification
below the application, with an optional chain-head anchor — FR-373), OQ-634 (the IdP owns
identity and role membership, the platform owns scope — FR-350), OQ-635 (an Admin may
override a flag, and it leaves a permanent scar — FR-360), OQ-636 (`risk_tier` on Model
Family and Rating Algorithm, which the policy may key on — FR-365), OQ-637 (exactly two
mandatory Commentary Blocks, no default text — FR-378) and OQ-638 (TAS 200 v2.0 **does**
cover pricing — FR-362). All are Phase 3 obligations: a later phase is a spec change and not
code (`CLAUDE.md` §0).

**OQ-638 was not a design choice and was not decided like one.** The row said so — *"a lookup
with a spec consequence"* — and the lookup was done: TAS 200 v2.0 §1.2 lists **Pricing
frameworks** among the work in scope, and its glossary defines a pricing framework as the
pricing principles *and the methodologies, assumptions and models implementing them* behind an
insurer's premium rates. `insurer` carries no life/general split. So the conservative interim
position the row recommended — assume TAS 100 only — was the wrong way round, and the platform's
models, assumptions and rationale are framework components by the standard's own definition.
Two things the question did not anticipate: the unit of scope is the **framework, not the
quote**, and there is **no pricing-specific provisions section**, so §1's P1.1–P1.4 bind
together with TAS 100. Verified against the FRC's published PDF rather than a summary — the
row's warning that public summaries do not state the scope was accurate.

**Every decision gate on this table is now closed except Phase 1b's, Phase 4's and the any-time rows.** Phase 1b's re-opened on 2026-08-22: deciding OQ-571 and OQ-572 surfaced two defects neither question had asked about, and a gate that closes over a question raised after it is a gate recording the wrong thing.
Phases 1a, 1b, 2 and 3 all read 0 open, while Phase 1a is still being built — which is the
order §10 exists to produce, and the first time the table has been in it.

**2026-08-18 (same day, at the maintainer's direction) — OQ-632 decided, and every gate
on this table is now closed.** An `expression` Custom Objective needs `custom_objective:author`,
distinct from `model:fit` and held by no built-in role by default (`06` FR-367). **Before
Phase 2 reads 10 (0 open)**, so Phases 1a, 1b and 2 are all decided while Phase 1a is still
being built. *(Corrected 2026-08-22: Before Phase 2 now reads 11 (0 open) with
OQ-571 placed, and Before Phase 1b has re-opened at 18 (2 open). The sentence stands as
what was true on 2026-08-18. **Superseded later the same day**: OQ-595 and OQ-596
were both decided, closing Before Phase 1b again at 18 (0 open), and their two successors
re-opened Before Phase 2 at 13 (2 open). Three readings of one table in one day is what a
hand-maintained count costs — each is right because it was recounted rather than
decremented.)*

**Worth recording why the deferral did not survive a second look**, because the failure is
instructive rather than embarrassing: it rested on "the answer depends on how much of the
review a certificate can carry", and that is the wrong dependency. Certification analyses the
*artifact* and the non-author Approver gates *approval*; both act after authoring, and neither
is an authorisation of the author. A `draft` objective can already fit models whose numbers
reach a pack. Once the dependency was named precisely it stopped being load-bearing — which is
the argument for stating a deferral's dependency explicitly rather than deferring on a feeling.

**2026-08-18 — OQ-632 deferred to Phase 2, with a trigger and an owner.** Whether an
`expression` Custom Objective needs an authoring permission distinct from `model:fit` is not
answerable yet, and the register says so rather than manufacturing an answer: it turns on how
much of the review an Objective Certificate can carry, which nobody knows until a
user-authored loss has been through one. **The deferral is the decision, and `06` FR-366 is
what makes it one** — the question must be answered *before* `expression_objectives_enabled`
may be lifted, and **WK-690 owns it** because WK-690 is the workstream that lifts the flag. A
deferral with a trigger, an owner and a written form binds something; a deferral with only a
phase attached is a note nobody is holding.

So **Before Phase 2 now reads 10 (1 deferred) rather than 10 (1 open)**, and no gate row on
this table is unowned. *(Superseded within the hour — the row reads 10 (0 open); the note
above records the decision. Left as written, because how briefly the deferral stood is
part of what the second look found.)* What is deferred is an *additional* control, not the only one:
FR-353 keeps the submitter out of the approval and `02` FR-163 requires a non-author
Approver, both of which apply to an expression objective the day it exists. That is why
waiting is affordable — and stating it is what stops the deferral being read as a gap.

**2026-08-18 — the four Phase-2 design questions decided, leaving one.** OQ-616 (rate
tables as rows, spilling to parquet above a configurable cell count — `03` FR-232),
OQ-617 (one algorithm for the risk price, refund maths in a sub-graph mounted on `purpose`
— FR-218), OQ-619 (annual premium plus an optional `instalment_loading` rung; APR and
schedules stay downstream — FR-252) and OQ-642 (one image now, a scoring image from
Phase 3 — `07` NFR-535, **built**). **Only OQ-632 still gates Phase 2**, and it is
correctly waiting: it asks whether an `expression` Custom Objective needs its own authoring
permission, and `expression` objectives are themselves Phase 2.

Three of the four are **spec changes only**, which is the rule rather than a shortage of
appetite: a later phase's capability is not built early (`CLAUDE.md` §0). The fourth is not an
exception to that rule but an instance of a different one — OQ-642's *decision* is a Phase
3 image, and what shipped is the **boundary that keeps that image cheap to build**, which is
worth nothing if it arrives with the image.

**Two defects the decisions found in the specification they were being written into.**
OQ-617's recommendation mounts its sub-graph on `purpose ∈ {mid_term_adjustment,
cancellation}` and **`cancellation` was not a value `purpose` had** — `03` §2 and §4.4 both
enumerated four — so the recommendation as filed keyed on something that did not exist. And
NFR-535's first draft forbade `xgboost` and `lightgbm` on the scoring path, which `02`
FR-193 contradicts outright: a GBM is scored by *loading its JSON booster*, so a boosting
library is a scoring dependency by design. Both were caught by checking the decision against
the spec it cited rather than against what sounded right.

**2026-08-18 (later the same day) — OQ-586 closes the 1b gate.** A penalised GLM reports its standard errors and its interval as before, and every response carrying them now says which matrix they came from (`02` FR-197, **built**). **Every question gating Phase 1b is decided**, three days after the gate was placed and while 1a is still open — which is the order this table exists to produce. What remains is Phase 2's five, Phase 3's six, Phase 4's eleven and four any-time.

The decision is worth one line of why, because the recommendation on file was a *sequencing*
rule rather than an answer — decide FR-113 and FR-194 together — and following it
is what produced the answer: both are read off one matrix, so refusing the interval would
have had to take the coefficient standard errors with it. A rule about *how* to decide,
honoured, decided it.

**2026-08-18 — five decisions, and the table was repaired to take them.** OQ-577 (the
approximation is a Model, `02` FR-137), OQ-576 (a dislocation gate on
`approximation` mode, `03` FR-224), OQ-584 (no continuous interaction operand, `02`
FR-93), OQ-585 (one interval kind until a named consumer, `02` FR-196) and
OQ-639 (§3.3 is a floor, `06` FR-364, **built**). **Before Phase 1b now has one question
left**, OQ-586 — *decided later the same day, which is what the note above records; this
sentence is left as it was written rather than corrected, because when the gate stood at one
is part of how fast it closed.*

**OQ-639 is gated at 1b and appears once.** It used to appear twice — the Phase 3 row
carried a parenthetical naming it, which reads as a placement to a counter that cannot tell
prose from a cell. Four other ids appeared nowhere at all: **OQ-584**, **OQ-585**,
**OQ-586** and **OQ-632**, each raised in a spec, correctly mirrored into
`open-questions.md`, and invisible to the plan. Two of them were decided on the day they were
placed, which is the failure mode this table exists to prevent: a question the plan never saw
cannot be scheduled, and one nobody scheduled gets answered by whoever trips over it.
**OQ-584 and OQ-576 sit at Phase 2 while already decided**, because each names a
revisit that belongs against a rate table that exists; **OQ-585** sits in *Deferred* for
the same reason, holding the trigger FR-196 names. A decided row still needs a gate — it
is where the revisit is scheduled, not only where the answer was due.

**OQ-614 was the one question able to invalidate an accepted ADR. It has been answered**
— by a spike, not an opinion — and ADR-706 survived
([`research/track-a-findings.md`](research/track-a-findings.md) F1).

**OQ-615 has also now been answered** by spike S2 — `exact` mode costs ~2 % of the
budget, so OQ-575 remained a design choice rather than being decided by force. **It was taken on 2026-08-17**: both modes are supported, and the mode belongs to the
Rating Version rather than to the step (`03` FR-223). What an `approximation`-mode
version must *prove* before it may deploy was the part the question did not settle, and
is now OQ-576 rather than an assumption.

**Every question that could only be answered with code has been.** What remains is
judgement, not measurement.

Six of the 1a/1b gate entries were raised *during* the phase rather than before it — by
driving the exit demo (OQ-562), by plan review 2 (OQ-543, OQ-644), by auditing the
GLM spine (OQ-582), and by building bandings and groupings (OQ-544, OQ-583) — and
none of them reached this table on the day it was raised. All six were added on 2026-08-15,
the last two while resolving a rebase, which is not a reliable mechanism. **A question raised
in a spec belongs in this table in the same commit** — the `spec-change` skill now says so,
because `audit-docs.py` checks the spec ↔ register mirror and cannot see this table at all.
A gate row is only as good as its habit of being written down.

**2026-08-17 — the three `MODEL` questions were decided, and recounting this table found it
had been over-claiming since it was written.** OQ-582 (a GBM's evidence obligation) and
OQ-583 (supervised banding) closed against appended requirements and tests; OQ-575
closed as above. Three ids reached no row at all: **OQ-577** and **OQ-639** are gated
at 1b, and **OQ-576** at Phase 2. OQ-577's placement is the substantive one — it
was blocked on OQ-575 and is now unblocked, and it must be answered before anything
references a transparency artifact by identifier, because `TransparencyArtifact` carries no
`status` and so cannot satisfy FR-20's approved-or-better pin check. OQ-639 moves
forward from Phase 3 for a plainer reason: its own recommendation says it is cheap to build
*once a second evidence kind exists*, and the transparency kind became checkable on the same
day. Both placements are proposals in §14's sense — a maintainer may move either row.

The recount is the finding the count column exists to produce. The **Before Phase 1b** cell
claimed 10 entries while naming 9, and had done so since it was written; the six other rows
were consistent. It now reads 11 because two ids were placed, not because one was found.
**Recount the row from its names — never decrement the number you found.**

**2026-08-15 — the six `MODEL` judgement calls were taken**, and none of them enlarged Phase 1:
expressions moved to Phase 2 while their certification machinery stayed here (OQ-573);
the cheap prediction interval was refused outright rather than made optional (OQ-574);
SHAP interaction detection ships as suggestion, not action (OQ-578); credibility gained a
second method because the choice belongs per grouping (OQ-579); the complexity gate is
unset by default because the judgement belongs to an Approver (OQ-580); and proxy
detection became a Phase 3 deliverable that produces evidence and never a refusal (OQ-581).
The register carries the reasoning; `02` §3 carries the obligations, as FR-150, FR-151, FR-198, FR-199, FR-135, FR-106, FR-185, FR-91.

**2026-08-15 — two `OVR` questions followed.** OQ-540 chose **deployment-per-tenant**, which
is the largest architectural commitment since ADR-706 and is recorded as **ADR-710**:
isolation becomes an infrastructure property rather than a promise that every query is
correct forever, at a cost that is linear in tenants and permanent. OQ-543 chose the
journey citation audit now and one end-to-end test per journey as its last module lands
(FR-19). Note what the first one moved: a question the table gated at Phase 3 turned out
to change what WK-674 builds in Phase 2, which is the argument for answering gates early rather
than at the boundary they are filed under.

**2026-08-21 — six questions decided, and the table gained the rows it was missing.**
OQ-548 (the audit cross-checks every §5.1 error-code table against `errors.py` — FR-22,
owner the maintainer, before Phase 1a's exit demo), OQ-566 (decided 2026-08-19 —
FR-67; the register row was stale and is brought into line), OQ-587 (aliasing
entries are bare names — FR-173, **delivered**: the authored contract corrected and the
pin deleted), OQ-589 (a rebuild reuses the surrogate's stored numbers — FR-138,
Phase 1b before its job-latency measurement), OQ-593 (the LightGBM drop is recorded on
the fit — FR-161, WK-661), OQ-594 (GBM-referenced offsets next, then the scoring path
— FR-117). **All thirteen rows the gate-table invariant reported missing are now
placed** — the six above, the six decided 2026-08-19 that had never reached the table
(OQ-547, OQ-556, OQ-588, OQ-590, OQ-591, OQ-592), and OQ-646,
still open, on the any-time row. A question invisible to the plan gets answered by whoever
trips over it; this is the fourth time the `missing` half of the check has caught a batch,
and the first where the batch included questions still open.

**2026-08-23 — FR-55 and FR-82 delivered (W32-3), and what stays open beside them.**
Both were "Not delivered. Phase 1b, owner WK-664". `GET /api/v1/datasets` now derives the status
badge and the last-validated date per request, storing neither, and `Dataset` carries a
non-null `owner_id` with an audited Admin-or-owner change route. FR-55 landed as **three**
fields rather than the two it named — its own "states which" clause needs the version beside the
date — which is recorded on the requirement rather than smoothed over. `01` §5.1's endpoint
table gained the `PATCH` row and `scope-audit.py DATA --endpoints` counts 38 of 38.

**Still open, and deliberately so:** `FR-67` is a decided deferral with **no owner, by its
own terms** — its trigger is a named reader asking for an exposure-ordered view, and assigning
it to a workstream would schedule work nobody has asked for. It appears in
`scope-audit.py DATA`'s unevidenced list beside the two delivered above and **should not be read
as a gap**; that adjacency is the whole reason this paragraph exists.

**Still open, and owned elsewhere:** `NFR-465` and `NFR-466` are budgets, not behaviour.
§13 rule 5 makes them a recorded `bench-data.py` measurement rather than a `@pytest.mark.req`
marker, and taking one is not this slice's work — nor is it honest on a machine running five
concurrent agent sessions, where the same measurement has varied 2.3x with load.

**Not delivered here:** `01` §5.3's Dataset list columns. The fields exist and the endpoint
returns them; rendering them is **W6b-3's**.

---

## 11. Sizing

Effort is expressed relative to the requirement surface and the number of independently
parallelisable workstreams. **No dates, because team size is unknown.**

| Phase | Requirement share | Parallelisable streams | Relative size | Shape |
|---|---|---|---|---|
| 0 — Specification | — | — | done | — |
| On-ramp (§3) | — | 3 | XS | ~~Research~~ ✔ · ~~3 spikes~~ ✔ · **7 decisions outstanding** |
| **1a — Data Workbench** | ~26 % | 3 after WK-657 | **L** | ~~WK-657–WK-660~~ ✔ **all closed** + dataset views (WK-663); the `validated` loop passes headless |
| **1b — Modelling Workbench** | ~21 % | 2 | **L** | WK-661–WK-665; ends at `WF-698` end to end. WK-664 also carries the frontend platform — browser auth, accessibility, and the workspace selector's shell control (its table, API and transport are WK-692's and OQ-648's, split out 2026-08-23) — after plan review 1 |
| 2 — Rating Engine | ~24 % | 2–3 | **L** | Deep; one large frontend, one hard NFR |
| 3 — Governance | ~11 % | 3 | **M** | Mostly surfacing Phase 1 foundations |
| 4 — Optimisation & Monitoring | ~18 % | 2 independent halves | **L** | Two loosely-coupled halves; monitoring can come early |

The distribution is why the split was accepted: **Phase 1 was not "the first phase", it was
nearly half the platform.** Split on the module boundary, each half is a normal-sized phase
with its own demo.

---

## 12. What "done" looks like, per phase

Each phase is complete when its workflow document executes end to end against real data —
not when its requirements are individually ticked off.

| Phase | Exit criterion |
|---|---|
| 0 | An engineer could start Phase 1 from the docs alone (`CLAUDE.md` §9) |
| 1a | A freMTPL2 dataset version reaches `validated`, including at least one deliberate round through the validation-failure loop |
| 1b | [`WF-698`](workflows/WF-00698-dataset-to-approved-model.md) end to end on freMTPL2 |
| 2 | [`WF-699`](workflows/WF-00699-approved-models-to-approved-rating-version.md) end to end, plus `WF-701` phases A–D, meeting NFR-489 |
| 3 | [`WF-702`](workflows/WF-00702-custom-objective-lifecycle.md) end to end, plus a dossier that survives external review |
| 4 | [`WF-700`](workflows/WF-00700-rate-change-impact-optimisation-dislocation-gipp-decision.md) end to end, plus `WF-701` phases E–H |

The workflow documents were written with timing tables for exactly this purpose.
