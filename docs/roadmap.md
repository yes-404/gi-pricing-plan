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
| **Code written** | Each phase section's `status:` line is the authority (`## P1a`, `## P1b`, `## P2` below). This row does not restate it, because a restated status goes stale (RFC-756). *Pointer since 2026-09-28, item E11.* |

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
status: closed
opened: 2026-08-14
target: ~
gates: ~
exit criteria: ~
works: WK-657, WK-658, WK-659, WK-660, WK-663, WK-666, WK-667

*Status set to `closed` 2026-09-28 (item E11 in the deputy's OQ-stream entry; Maintainer decision by delegation (deputy, on the maintainer's instruction of 2026-09-28 11:24 BST), 2026-09-28 11:33:12 BST). The authority is the exit demo's acceptance on 2026-08-15, recorded in the Phase 1a status table below and in `CR-717` (`kind: phase`). The header had been left `active`.*

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

The closure records, plan reviews and the retrofit-impossible list moved to `docs/audit/` on 2026-08-27 (RFC-813). This page is the forward-looking plan; the archive is at [`docs/findings/README.md`](findings/README.md).

## P1b — Modelling Workbench
status: closed
opened: 2026-08-14
target: ~
gates: ~
exit criteria: ~
works: WK-661, WK-662, WK-664, WK-665, WK-692

*Status set to `closed` 2026-09-28 (item E11 in the deputy's OQ-stream entry; Maintainer decision by delegation (deputy, on the maintainer's instruction of 2026-09-28 11:24 BST), 2026-09-28 11:33:12 BST). The authority is the phase's acceptance as closed on 2026-08-27, recorded in `CR-822`. The header had been left `active`.*

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
target: 2026-11-12
gates: ~
exit criteria: G1–G6 of [`CR-1212`](closures/CR-01212-plan-review-15-p2-exit-criteria-budget-sequencing-and-the-open-finding-set.md), as accepted by the maintainer 2026-09-28, listed below
works: WK-668, WK-669, WK-670, WK-671, WK-672, WK-673, WK-674, WK-675, WK-690, WK-693, WK-694, WK-695, WK-696, WK-697, WK-1169, WK-1170, WK-1178, WK-1250

**P2's exit criteria** — [`CR-1212`](closures/CR-01212-plan-review-15-p2-exit-criteria-budget-sequencing-and-the-open-finding-set.md) Proposal 1, **accepted by the maintainer 2026-09-28** (the deputy's entry of 19:05:44 BST, quoted whole in that record's "Acceptance"), with its two amendments: G1–G6 are **exit criteria only** — `gates:` holds the three dated freeze gates (`process/document-ids.md` §1.3, §1.10(b)) and, with `target:`, stays `~` until the lead proposes dates after WK-672 closes and the deputy puts them to the maintainer, who accepts them before the first freeze passes (the deputy's entry of 2026-09-28 19:05:44 BST; that clause is that entry's, not CR-1212's text); and G5 is stated by symbol, with no pasted number. The criteria's full predicates, greps and per-id lists are in that record, which is the authority; this list is a pointer to them.

- **G1.** Every P2 Work is resolved: closed by a `CR- kind: work` carrying the maintainer's dated acceptance line, or moved out of P2 by a dated maintainer line. WK-1178, the standing maintenance Work, is exempt and is dispositioned under G3. Check: every `### WK-` section in `## P2` reads `status: closed`, or is WK-1178, or is named in a dated move line.
- **G2.** The exit demo is `WF-699` end to end on the freMTPL2 seed, with its deploy step: through approved models, a Rating Version compiled with pins, golden quotes, a regression run, a dislocation run with attribution, submission, and approval by a principal who is neither submitter nor author (#861, FR-353), then deployment to `uat` and then `prod` (`07-platform.md` FR-429), from one command to a served page, in Phase 1b's form. It is recorded in a `CR- kind: phase` with the maintainer's acceptance. By CR-1212's accepted P12 resolution, `prod` here is the platform's environment (FR-429), not production packaging.
- **G3.** Every open P2 finding is fixed, carried with a named owner, or accepted by a dated line (`CLAUDE.md` §14). FD-1200 is fixed on main (`e6a9ca71`, FR-351) and FD-1199 is triaged with a root cause or a dated acceptance.
- **G4.** Every P2 NFR is measured on the exit tree or carried with an owner, per the per-id list in the record.
  *(Amended 2026-09-29, the lead, quoting the maintainer's entry "2026-09-29 16:08:24 BST · maintainer (acting on the maintainer's behalf) · HOST FALLBACK accepted; DEPENDABOT plan approved (the maintainer)", §1. It applies to the near-bound measured verdicts that need a dedicated host: F1 (PL-1237 acceptance item 5), NFR-489, NFR-502, the NFR-493 linearity limb and NFR-494 (item 6). NFR-490 is unaffected. The entry's wording:)*
  > "*(Amended 2026-09-29 by the maintainer: no dedicated host is committed. These verdicts are **measured, diagnostic** on the shared VM; the verdict is **carried**, owner the maintainer, discharge event **a dedicated host available**. No near-bound pass or fail is claimed from the shared VM.)*"
- **G5.** On the exit tree, `audit-docs.py` exits 0 with "All checks passed." (its ceiling is the governed record at `_docid.W37_11_RECORD_PATH`), the other three docs checks exit 0, and the two-half gate of `CLAUDE.md` §11 passes.
- **G6.** ~~A plan review 16 is filed after G1–G5 and before the demo (`CLAUDE.md` §14).~~
  The pre-exit-demo plan review (CLAUDE.md §14; option C rule 1 once its RFC lands) is filed after G1–G5 are met and before the demo.
  *(Amended 2026-09-29 on `CR-1247`, and the maintainer's entry "2026-09-29 17:27:28 BST · maintainer (acting on the maintainer's behalf) · ACCEPTANCES: the WK-672 Work close (#906) and plan review 16 (#905), per proposal", §2 row 8: "Accepted: G6 is restated without the number: 'The pre-exit-demo plan review (CLAUDE.md §14; option C rule 1 once its RFC lands) is filed after G1–G5 are met and before the demo.'" The restated sentence above is the maintainer's wording, verbatim. The old text is kept, struck: "plan review 16" now names `CR-1247`, a review that is not G6, and a reader checking G6 by that number would read it as met.)*

#### P2 freeze dates and target

*(Added 2026-09-29 by the lead, as a milestone-section edit, quoting verbatim the maintainer's entry "2026-09-29 20:45:24 BST · maintainer (acting on the maintainer's behalf) · P2 FREEZE DATES AND TARGET (§5a), accepted by the user". The user (the maintainer), about 20:26 BST: "accept the P2 dates as proposed".)*

*(Weekdays corrected 2026-09-29 by the lead, quoting the maintainer's entry "2026-09-29 21:03:52 BST · maintainer (acting on the maintainer's behalf) · CORRECTION to the 20:45:24 P2 dates: the WEEKDAYS were wrong; the DATES stand (a)": "the DATES stand. … Only the weekday labels change." The 20:45:24 entry read Fri 2026-10-03, Tue 2026-11-04, Wed 2026-11-05 and Wed 2026-11-12; `date -d` gives Sat, Wed, Thu and Thu. The block below carries the corrected weekdays; everything else in it is verbatim.)*

> **P2 freeze dates and target** (accepted 2026-09-29 by the maintainer; sized by the planner's "Inputs to the maintainer's §5a" at main 5638f691: 20 best / 37 likely / 87 worst working days from WK-674 S1 going active, at the measured 2 code slices per day):
> - **Scope freeze: Sat 2026-10-03.** No new Work enters P2 after this date. WK-1250 is the last addition, and WK-675's map plan is drafted by then.
> - **Code freeze: Wed 2026-11-04.** G1: the seven P2 Works delivered.
> - **Docs freeze: Thu 2026-11-05.**
> - **Target: the P2 exit demo, Thu 2026-11-12** (the likely band plus about 20%).
> - **Re-baseline after WK-674 Slices 1–2:** re-measure the throughput and restate these dates if the band moves. The dates assume work every day, as practised; on a weekdays-only rhythm they slip about two weeks.

*(Added 2026-09-29 by the lead, quoting the user (the maintainer), relayed in the maintainer's
entries "2026-09-29 22:49:26 BST — THE USER'S STANDING PRIORITY: finish without delay, bounded only
by resources" and "2026-09-29 22:49:59 BST — DATES NEVER BLOCK A START": "ok plz go ahead, plz mind
the dates are for reference purpose. we need to complete the works without delay subject to
resources (server and usage)", and "the dates never block a work can start earlier". The dates above
are therefore a forecast for reference, not targets. No Work, slice, plan, ruling or merge waits for
a date. The freeze gates limit only what may **enter** P2, never when a start happens.)*

#### Phase 2 status

*(Added 2026-09-29 on `CR-1247`, and the maintainer's entry "2026-09-29 17:27:28 BST · maintainer (acting on the maintainer's behalf) · ACCEPTANCES: the WK-672 Work close (#906) and plan review 16 (#905), per proposal", §2 row 12: "Accepted: (a). An 'Exit demo' row under P2, owned by the lead, discharging FD-1209." The form is Phase 1b's status table.)*

| WS | Scope | Status |
|---|---|---|
| **Exit demo** | Phase 2's exit criterion G2: `WF-699` end to end on the freMTPL2 seed, with its deploy step. Its scope is the real freMTPL2 rating algorithm in the seed, `WF-699` Phases A to E and its deploy step as one scripted journey, and the journey test that cites `WF-699` by id; **the script walks `WF-699` A1–A2 (seed-from-model) on the 7-factor freMTPL2 GLM** — added 2026-10-01 by the maintainer (entry "2026-10-01 08:01:45 BST — FD 9786 severity: HIGH"), on FD-1357 (multi-factor seeding). **Owner: the lead.** It is sequenced after WK-673 and WK-674, because it needs dislocation and deployment. It can be cut in parallel with WK-675 where no view is needed, still one slice at a time (`delivery-process.md` §8). It discharges FD-1209's event. The two `WF-699` findings, FD-1244 (D4 against FR-261) and FD-1245 (E2 against FR-257), are on the §10 gate "Before the P2 exit demo", for the decision-maker | **not started**: opened 2026-09-29 (`CR-1247` Proposal 12) |

### WK-668 — **Spike S1/S2 resolution and ADR-706 confirmation**

```yaml
id: WK-668
family: work
title: **Spike S1/S2 resolution and ADR-706 confirmation**
status: closed
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 373): **Spike S1/S2 resolution and ADR-706 confirmation** | Must complete before WK-669. If S1 fails, this phase is re-planned **Closed 2026-09-28 by the deputy's dated line, by delegation, on [`CR-1171`](closures/CR-01171-wk-668-work-close-the-auditor-s-restatement-of-cr-826-at-main.md).**


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
status: closed
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 377): Testing: golden quotes, property assertions, regression runs | FR-260, FR-261, FR-262, FR-1221 (added 2026-09-29 at the close: named by `03`'s WK-672 Slice 3 note (`03:180`), in no plan's Scope; delivered and tested by #910) — **Closed 2026-09-29 by the maintainer's dated line, by delegation, on [`CR-1243`](closures/CR-01243-wk-672-work-close-testing-golden-quotes-property-assertions-and-regression-runs.md).**

**2026-09-28 — the charter, named against its own ids** (WK-672 Slice 1, `PL-1177`; `RL-1172` items 4 and 5, the latter quoting the deputy's DP1 decision by delegation, option A). **FR-260:** golden quotes, and the promotion re-scoring that refuses on a mismatch beyond the declared tolerance. **FR-261:** property assertions over generated quote contexts, and the regression runs that execute a suite (`POST /api/v1/rating-versions/{id}/regression-runs`, recorded as `03` §4.9 `RegressionRun`). **FR-262: the backend limb only** — `POST /api/v1/score/compare`, one quote scored against two Rating Versions with the step-level diff; the Quote Sandbox view over it is WK-675's, and FR-262 is delivered only when both limbs have landed. **FR-257 limb (1)** — the approval gate's passing-Regression-Suite check — is also this Work's (`RL-1172` item 4). Slices run 1 → 2 → 3 → 4, one at a time.


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

From “Workstreams” (line 383): Dislocation with attribution | FR-263, FR-264, FR-265, FR-266, FR-224, FR-257 limb (2), `06` FR-364, FR-231 (F-W10-2), NFR-495, NFR-496 (applied to this Work's artifacts)

*(Amended 2026-09-30 by the lead, on `PL-1267` §Activation item 2 and the maintainer's entry "2026-09-30 02:33:58 BST — MERGE-ACK #844 and ACCEPTANCE of PL-1267 (WK-673 map plan)", whose carry-forward reads "the lead's next roadmap PR adds the plan's ids to `### WK-673`'s "From Workstreams" line".)* FR-224, FR-257 limb (2), `06` FR-364 and FR-231 (finding F-W10-2, the exposure-weight limb only) are added to WK-673's scope, as `PL-1267` proposes. NFR-495 and NFR-496, applied to this Work's artifacts, are added from the same entry's acceptance line, whose Scope clause reads "takes FR-224, FR-257 limb (2), `06` FR-364, FR-231 (the F-W10-2 weight limb) and NFR-495/NFR-496 (applied to this Work's artifacts) from RL-1264 and CR-1212". The line named FR-263 to FR-266 only.

#### SL-1385 — Slice 1: spec — FR-266's amendment, the hard gate as requirements, the contract and the types

```yaml
id: SL-1385
family: slice
title: Slice 1: spec — FR-266's amendment, the hard gate as requirements, the contract and the types
status: closed                 # draft → active → closed | retired (§1.2a)
created: 2026-10-03
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 2411060d81b8821193c5e7239a2423c6a9cf1667
phase: P2
work: WK-673
corrected_by: []
relates: [PL-1267, PL-1395, RL-1264, RL-1184]
```

Spec only, no application code beyond one test-file label. FR-266's dated amendment (exact Shapley over the declared changes for K ≤ 6, largest-remainder allocation to integer minor units, the isolated and cumulative views, the residual line, the above-six rule); the hard gate appended to `03` §3.9 as requirements; `03` §4.6 reconciled with the contract and extended with the attribution fields; `03` §4.8's portfolio frame schema; `RL-1264`'s DP-1 and DP-2 obligations as spec text; `03` §5.2's `DislocationSpec`, `BundleDelta`, `Attribution` and `attribute`'s amended signature; `00` §2 glossary terms first; the `test_contracts.py:84` label and `_round_minor`'s docstring corrected. `PL-1267` Slice 1. First in the chain: nothing in WK-673 precedes it, and it does not depend on WK-674. Its leaf plan states, as a decision point or a premise, what the portfolio frame does with a column the contract does not declare (the `03` §4.8 undeclared-column pass-through), per the maintainer's acceptance of `PL-1267`, "2026-10-03 17:53:43 BST — ACCEPTANCE: PL-1267 (WK-673 map plan, dislocation with attribution) by the maintainer (by delegation); GO planner-673act", condition 2.
(Activated 2026-10-03 as WK-673 Slice 1, on the maintainer's GO check, "2026-10-03 21:17:03 BST — DISPATCH GO: WK-673 Slice 1 (SL-1385 / PL-1395) on lane B; executor-1385 starts after #1087, #1093 and #1092 have merged"; dispatch record DISPATCH-WK-673-SL1385-2026-10-03.)

(Closed 2026-10-03 as a Slice, on a clean audit and the lead's merge: audit `handover/audit-1385-2026-10-03.md`, verdict CLEAN; dispatch record `DISPATCH-WK-673-SL1385-2026-10-03` Deltas 1 and 2; ledger `LG-1400`. The three requirement working ids RW1 to RW3 were minted as FR-1397 to FR-1399 at the mint moment.)

#### SL-1386 — Slice 2: the Dislocation Run on ZEN, in integer minor units

```yaml
id: SL-1386
family: slice
title: Slice 2: the Dislocation Run on ZEN, in integer minor units
status: closed                 # draft → active → closed | retired (§1.2a)
created: 2026-10-03
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: d672f991bdc59008e09cf3f464cd7cffe5699553
phase: P2
work: WK-673
corrected_by: []
relates: [PL-1267, PL-1403]
```

`dislocate(baseline, candidate, portfolio, spec)` in `pricing_core/rating/analysis.py`: two `score_batch` passes joined per policy on integer minor units; distribution bands, averages overall and by segment, exposure and policy counts per band, movers beyond the spec's thresholds (FR-263); slicing by any portfolio Factor and by the first differing ladder rung (FR-264); `DislocationSpec` and `DislocationRun` in `model-schema`; NFR-495 (byte-identical repeat run) and NFR-496 (totals equal the sum of per-policy minor units) tested. `PL-1267` Slice 2. Starts after Slice 1 closes.
(Activated 2026-10-04 as WK-673 Slice 2, on the maintainer's GO check, "2026-10-04 13:03:47 BST — DISPATCH GO: WK-673 Slice 2 (SL-1386 / PL-1403) on lane B; executor-1386 starts after #1101 merges. N1: the S5 mint-pass note on RL 9733 is ACCEPTED (text below)"; dispatch record DISPATCH-WK-673-SL1386-2026-10-04.)

(Closed 2026-10-04 as a Slice, on a clean audit and the lead's merge: audit `handover/audit-sl1386-2026-10-04.md`; dispatch record `DISPATCH-WK-673-SL1386-2026-10-04` Delta 3; ledger `LG-1406`.)

#### SL-1387 — Slice 3: attribution — exact Shapley, largest remainder, the broken-input proof, the cost

```yaml
id: SL-1387
family: slice
title: Slice 3: attribution — exact Shapley, largest remainder, the broken-input proof, the cost
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-10-03
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: d672f991bdc59008e09cf3f464cd7cffe5699553
phase: P2
work: WK-673
corrected_by: []
relates: [PL-1267, RL-1264]
```

`attribute` per Slice 1's signature: declared changes derived and grouped per DP-2; the 2^K subset bundles built per DP-1 and rated on ZEN; exact Shapley per policy, largest-remainder allocation to minor units, the isolated and cumulative views, the residual line, the labelled above-six fallback; `BundleDelta` and `Attribution` in `model-schema`. Reconciliation asserted on every run and proven on broken input; the feasibility rule (measured `score_batch` rate, ladder replay proven equal to a true re-rate, the estimated rating count shown before launch); the F3 carried items. `PL-1267` Slice 3. Starts after Slice 7 closes, in the plan's one-slice-at-a-time order 1 → 2 → 7 → 3 → 4 → 5 → 6 (its data dependency is Slice 2); serialised against any WK-1250 slice that edits `compile_bundle` or the trace.

#### SL-1388 — Slice 4: backend — the Job, the routes, the persisted artifact, the generated contract

```yaml
id: SL-1388
family: slice
title: Slice 4: backend — the Job, the routes, the persisted artifact, the generated contract
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-10-03
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: d672f991bdc59008e09cf3f464cd7cffe5699553
phase: P2
work: WK-673
corrected_by: []
relates: [PL-1267, RL-1236]
```

The `dislocation.run` handler owning the Job identity, output location and resumability; `POST /api/v1/dislocation-runs` (202 plus a Job) and `GET /api/v1/dislocation-runs/{id}` with RBAC and RFC 9457 errors; the artifact persisted as a citable row with content-addressed blobs (FR-265); `DislocationRun` registered for generation, `docs/contracts/` regenerated and the slug moved to `COMPARED_SLUGS`. Route permissions picked from `RL-1236`'s catalogue, citing FD-1197. `PL-1267` Slice 4. Starts after Slice 3 closes.

#### SL-1389 — Slice 5: the approval gate, part one — structural_diff, FR-257 limb (2), FR-224

```yaml
id: SL-1389
family: slice
title: Slice 5: the approval gate, part one — structural_diff, FR-257 limb (2), FR-224
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-10-03
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: d672f991bdc59008e09cf3f464cd7cffe5699553
phase: P2
work: WK-673
corrected_by: []
relates: [PL-1267, RL-1264]
```

`06` FR-364's `structural_diff` persisted at submission with a verifier registered; FR-257 limb (2) on `submit_for_review` (refused with `EVIDENCE_INCOMPLETE` without a Dislocation Run on the current bundle hash against the current live version); FR-224's exact-mode comparison for an `approximation`-mode version, its threshold a new `ApprovalPolicyEntry` field and never read from Settings. `PL-1267` Slice 5. Starts after Slice 4 closes and after WK-674 Slice 2 (`SL-1256`) has merged; serialised against `SL-1256` on `approvals.py` and `06` §4.2. Leaf plan PL 9590 (working id, `draft`; filed 2026-10-05). **Activation needs:** the plan made `active` by a dated line; `SL-1388` closed; `SL-1256` closed (met); a ruling on its DP-S5-1 to DP-S5-5 merged and minted; RL 9614 minted (FR-257's gate stays at the submit route); the lane free under `RL-1263` as amended, with the same-Work conditions in the dispatch record (its FR-224 edit in `03` §3.2 serialises with PL 9688 and PL 9683); the maintainer's dispatch GO and the lead's go in a separate activation PR. *(Plan cite added 2026-10-05 by the planner; working id 9590 reserved by the lead.)*

#### SL-1390 — Slice 6: the approval gate, part two — the floor wiring

```yaml
id: SL-1390
family: slice
title: Slice 6: the approval gate, part two — the floor wiring
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-10-03
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: d672f991bdc59008e09cf3f464cd7cffe5699553
phase: P2
work: WK-673
corrected_by: []
relates: [PL-1267]
```

`submit_for_review` checks `policy.effective_evidence("rating_version")` against a verifiable map (`structural_diff`, `regression_run`, `dislocation_run`), replacing the direct limb checks, limb (1)'s `_regression_run_gate` call included; a workspace policy naming a kind nothing can verify is refused by name (`06` FR-364). `PL-1267` Slice 6. Starts after Slice 5 closes, and so transitively after `SL-1256`.

#### SL-1391 — Slice 7: FR-231's exposure weights through the portfolio frame (F-W10-2)

```yaml
id: SL-1391
family: slice
title: Slice 7: FR-231's exposure weights through the portfolio frame (F-W10-2)
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-10-03
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: d672f991bdc59008e09cf3f464cd7cffe5699553
phase: P2
work: WK-673
corrected_by: []
relates: [PL-1267, RL-1361, RL-1375]
```

The weight limb of FR-231: the rate-table diff shows the exposure weight behind each cell, from a portfolio Dataset Version. `03` §5.1's diff route gains the portfolio parameter and the refusal `RL-1361` settles (DP-5); the portfolio frame aggregated to Σ exposure per cell key in Polars and passed as `weights`, on the 202 path too; negative tests for an absent key column, an unweighted diff that says so, and a hand-computed weighted mean; register row `FR-231 (F-W10-2)` discharged on merge. `PL-1267` Slice 7. Starts after Slice 2 closes and runs before Slice 3, one slice at a time; unblocks WK-675 Slice 5. Per the maintainer's acceptance of `PL-1267` (the 17:53:43 BST entry above), condition 1: `RL-1375` DP-1 (a2) applies, so the FD-1357 slice `SL-1377` merges first and this slice never runs concurrently with it (shared `RateTableKey`, `operations.py`, the `rate_tables` routes); its leaf plan also carries FD-1358 (the per-cell weight display) as `RL-1361` §F placed it.


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

From “Workstreams” (line 384): Deployment: environments, atomic switchover, rollback, shadow — **and the tenancy mechanics ADR-710 requires** | FR-267, FR-268, FR-269, FR-270, FR-271, FR-272; `07` FR-428, FR-429, FR-430, FR-431, and added 2026-08-15 by OQ-540's decision: **FR-436** (a deployment refuses to start against another tenant's database) and **FR-18** (a Job records the platform build, because version skew between tenants is now permanent). Any earlier `Job` migration should carry FR-18's column rather than wait for this *(Corrected 2026-09-29 by the lead, per `PL-1237`'s Scope note, amended by the maintainer's answer Q843-2: "The roadmap WK-674 row edit is the lead's, after the map is accepted." Added: `07` **FR-437** (the reference identity provider, `07:153`), **FR-412**'s memory half (`07:101`) and **FR-415**'s worker service (`07:104`); and `CR-1212`'s **FR-434**, **FR-435**, **NFR-531**, **NFR-534**, **NFR-489**, **NFR-490**, **NFR-502**, **NFR-493**'s linearity limb and **NFR-496**'s prod-sampling limb. **The F1 obligation:** the Work is done only when the switchover meets the F1 acceptance test on the deployment path this Work builds, not on a loopback mirror (`PL-1237` Goal).)*

#### SL-1255 — Slice 1: tenancy and provenance (FR-436, FR-18)

```yaml
id: SL-1255
family: slice
title: Slice 1: tenancy and provenance (FR-436, FR-18)
status: closed                 # draft → active → closed | retired (§1.2a)
created: 2026-09-29
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 0d5b0765f76320518bfe76ddb30e5013525797c0
phase: P2
work: WK-674
corrected_by: []
relates: [PL-1237, PL-1239, RL-1253]
```

A deployment is bound to one tenant and refuses to start when its database, blob or broker marker names another; every Job records the platform build it ran on. `PL-1237` Task 1; leaf plan `PL-1239`, its decision points ruled by `RL-1253`. First in the chain: nothing precedes it. *(Closed 2026-09-30 by the auditor: `#933` merged as `aa14e90dd77c7461aa35cc6461557b129959463f` on the maintainer's MERGE-ACK; auditor-933's slice audit: the full audit at `7a63809d` was NOT CLEAN, solely on F1 (the check-31 id gap 1260→1262, a merge-order finding that cleared when #927 merged), closed at `a8d2dfd9`; CLEAN at the deltas `a8d2dfd9` and `7f4468a5`; acceptance verified on `origin/main` at that SHA; `LG-1262` set `closed`. The FR-18 dossier half (`06` FR-376) is carried to WK-680, not delivered here.)*

#### SL-1302 — Slice 2a: the approval guard (only the decision path writes approved; FR-351)

```yaml
id: SL-1302
family: slice
title: Slice 2a: the approval guard (only the decision path writes approved; FR-351)
status: closed                 # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: daa7f5f8d6f0ff80dee7dfccf8ca18309d626816
phase: P2
work: WK-674
corrected_by: []
relates: [PL-1237, PL-1303]
```

A database trigger, primary, on every approval-capable table refuses `approved` outside the approval decision path; the test database is shown to carry it. Cut 2026-09-30 from Slice 2 by the maintainer's acceptance of the split (to-lead.md, `2026-09-30 11:48:28 BST`; "S2a (the approval guard, first) and S2 (deployment), per #973's self-review option (b)"). Leaf plan `PL-1303` (minted 2026-09-30 with this row in the lead's mint train; filed under working ids 9923 and 9922); the guard is `RL-1301`'s (#971) evidence-based trigger: an artifact row reaches `approved` only with a matching approved approval request, the validation tables accept evidence or the decision flag while their allowance lasts, and `approval_requests` takes the flag behind `decide`'s guards. Starts after Slice 1 closes (it has); **Slice 2 follows it**, in the same lane, never concurrently.

**Closed 2026-09-30** at #997's merge, `8d5c67a56c27a9dcbba8d4e4ad28a1895e1dd862`, on a CLEAN slice audit (auditor-close1255 at `4a2423f2`, per the lead handover `lead-handover-2026-09-30.md`) and the lead's merge (CLAUDE.md §13); the maintainer's MERGE-ACK ("2026-09-30 16:58:01 BST — MERGE-ACK #997") and read-back ("2026-09-30 16:58:35 BST — #997 read-back verified") confirm it. Its ledger is `LG-1324`. The row read `active` after the merge and was flipped here, a forward status, by the auditor at `origin/main` 248dbf11.

#### SL-1256 — Slice 2: the Environment and Deployment record (FR-267, FR-428, FR-429, FR-272 audit and NFR-498 for deploy)

```yaml
id: SL-1256
family: slice
title: Slice 2: the Environment and Deployment record (FR-267, FR-428, FR-429, FR-272 audit and NFR-498 for deploy)
status: closed                 # draft → active → closed | retired (§1.2a)
created: 2026-09-29
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 0d5b0765f76320518bfe76ddb30e5013525797c0
phase: P2
work: WK-674
corrected_by: []
relates: [PL-1237]
```

The Environment and Deployment records, promotion order and their audit limb for deploy (FR-272, NFR-498), with the carried rulings. `PL-1237` Task 2. Starts after Slice 1 closes; its leaf plan also waits on `OQ-1234` (the maintainer's acceptance line on `PL-1237`).

*Dated 2026-10-03 (at PL-1392's mint): the leaf plan is now **`PL-1392`**, which **supersedes `PL-1306`** on the maintainer's entry "2026-10-01 10:10:32 BST — WK-674 S2 currency audit: ORDER AMENDED to (b) S2 → FD-1356 fix; a superseding PL for S2; …" and its 10:10:46 addendum: the 7 new routes typed both ways, Acceptance 8 Branch A, order (b) S2 → the FD-1356 fix, and never concurrent with FD-1335 Part A's slice (both edit `score.py`). This row's status and fields are unchanged.*
(Activated 2026-10-03 as WK-674 Slice 2, on the maintainer's GO check, "2026-10-03 20:02:13 BST — DISPATCH GO: WK-674 Slice 2 (SL-1256 / PL-1392) on lane A; executor-1256 starts after #1087 merges"; dispatch record DISPATCH-WK-674-SL1256-2026-10-03.)

(Closed 2026-10-04 as a Slice, on a clean audit and the lead's merge: audit `handover/audit-sl1256-2026-10-04.md`; dispatch record `DISPATCH-WK-674-SL1256-2026-10-03` Delta 10; ledger `LG-1405`.)

#### SL-1257 — Slice 3: environment isolation (FR-430, FR-431, register F54 and F48, NFR-496 prod-sampling limb)

```yaml
id: SL-1257
family: slice
title: Slice 3: environment isolation (FR-430, FR-431, register F54 and F48, NFR-496 prod-sampling limb)
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-09-29
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 0d5b0765f76320518bfe76ddb30e5013525797c0
phase: P2
work: WK-674
corrected_by: []
relates: [PL-1237]
```

Per-environment keys, rate limits and monitoring configuration, and environment configuration as a Setting. `PL-1237` Task 3. Starts after Slice 2 closes, and is gated by `OQ-1235`.

*Dated 2026-09-30: the **ladder half** of this slice (RL-1329 in full, FD-1336 with NFR-496, FD-1330, R2, the release note, the OQ-1316 note) is carved out to `SL-1345` on the maintainer's entry "2026-09-30 23:57:25 BST — DECISION on the S3 halt: (A) carve the ladder half into its own slice; lane B takes WK-1250 S1 now". This slice keeps the environment half and stays `draft` behind Slice 2; `PL-1342` is not edited. DP-S3-1 and DP-S3-2 are assigned by the new leaf plan to the half that needs them.*

*Dated 2026-10-01, mint batch 13a: **FR-452 (the `/score` limb, `RL-1347`)** is this slice's, with DP-S3-2 resolved by `RL-1347` (assigned here by `PL-1348`). FR-452's **management-API limb** is owned by WK-674 (the maintainer's entry "2026-09-30 23:48:24 BST — OWNER DECISION: FR-452 → WK-674, not WK-1178") and is carried to a later WK-674 slice, which a planner names in a dispatch record before WK-674 closes; that slice's row is annotated when named. DP-S3-1 is resolved by `RL-1346` and belongs to `SL-1345`.*

#### SL-1345 — Slice 3L: the premium ladder — exact unrounded rungs, true operations, one rounding (FR-247, FR-248, NFR-496, FD-1336, FD-1330; RL-1329)

```yaml
id: SL-1345
family: slice
title: Slice 3L: the premium ladder — exact unrounded rungs, true operations, one rounding (FR-247, FR-248, NFR-496, FD-1336, FD-1330; RL-1329)
status: closed                   # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 248dbf11aa0a044ff4eaadcaa32aa82960aa6740
phase: P2
work: WK-674
corrected_by: []
relates: [PL-1342, RL-1329]
```

Carved from `SL-1257` on the maintainer's entry "2026-09-30 23:57:25 BST — DECISION on the S3 halt: (A) carve the ladder half into its own slice; lane B takes WK-1250 S1 now": the ladder half of `PL-1342`, which depends on nothing in Slice 2. A new leaf plan (a planner, quoting `PL-1342`'s text, never editing it) carries it; its decision points are minted before activation. It takes the first free lane after activation. The work already built for it is on a salvage branch from the halted WK-674 S3 dispatch. Minted as `SL-1345` at this PR's merge turn, 2026-09-30, with `python3 scripts/doc-id.py next --ref origin/main` at `248dbf11`.

*Dated 2026-10-01, mint batch 13a: its leaf plan is `PL-1348` (draft until activation). DP-S3-1 is resolved by `RL-1346`. The activation needs are `PL-1348`'s own, each a command with an expected output.*

#### SL-1258 — Slice 4: the deployment path (FR-437, FR-412 memory half, FR-415, FR-434, FR-435, NFR-531, NFR-534, FD-1211)

```yaml
id: SL-1258
family: slice
title: Slice 4: the deployment path (FR-437, FR-412 memory half, FR-415, FR-434, FR-435, NFR-531, NFR-534, FD-1211)
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-09-29
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 0d5b0765f76320518bfe76ddb30e5013525797c0
phase: P2
work: WK-674
corrected_by: []
relates: [PL-1237]
```

The compose `api` and `worker` services, the reference identity provider, the memory budget and the explicit migration step: the path Slice 5 measures on. `PL-1237` Task 4. Starts after Slice 3 closes.

#### SL-1259 — Slice 5: atomic switchover, rollback and the measurements (FR-268, FR-269, FR-272 audit and NFR-498 for rollback, NFR-494, NFR-489, NFR-502, NFR-490, NFR-493 linearity limb, NFR-497 mechanism)

```yaml
id: SL-1259
family: slice
title: Slice 5: atomic switchover, rollback and the measurements (FR-268, FR-269, FR-272 audit and NFR-498 for rollback, NFR-494, NFR-489, NFR-502, NFR-490, NFR-493 linearity limb, NFR-497 mechanism)
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-09-29
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 0d5b0765f76320518bfe76ddb30e5013525797c0
phase: P2
work: WK-674
corrected_by: []
relates: [PL-1237]
```

Atomic switchover and rollback on the Slice 4 path, with the rollback's audit limb (FR-272, NFR-498), the F1 acceptance test and the measured verdicts. NFR-497's degraded read is kept reachable against the `live` reference; the availability verdict is the lead's at the close. `PL-1237` Task 5. Starts after Slice 4 closes; its measured verdicts wait on a dedicated host (maintainer-owned).

#### SL-1260 — Slice 6: date-based routing and shadow scoring (FR-270, FR-271, FR-272 audit and NFR-498 for routing and shadow)

```yaml
id: SL-1260
family: slice
title: Slice 6: date-based routing and shadow scoring (FR-270, FR-271, FR-272 audit and NFR-498 for routing and shadow)
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-09-29
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 0d5b0765f76320518bfe76ddb30e5013525797c0
phase: P2
work: WK-674
corrected_by: []
relates: [PL-1237]
```

Date-based routing and shadow scoring, both built and default off per environment (`RL-1232` Part A, DP-2 (a)), with the audit limb for routing and shadow configuration changes (FR-272, NFR-498). `PL-1237` Task 6. Starts after Slice 5 closes.


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

**2026-09-28 — the Quote Sandbox's backend is WK-672's** (`RL-1172` item 5, the deputy's DP1 decision by delegation, option A). The quote sandbox view in this Work consumes `POST /api/v1/score/compare`, which WK-672 builds and tests; this Work builds the view only. FR-262 is delivered only when both limbs have landed.

**2026-10-03 — Slice 12 (the Deployments view) moves to Phase 3** (`PL-1371` §9 DP-2 (a), the maintainer's acceptance by delegation in the entry "2026-10-03 14:56:08 BST — PL 9746 (#1076 @ee0ea8d2): ACCEPTED with your four amendments; DP-1 (a), DP-2 (a), DP-3 (a); amendment 4 answered; DP-4 to the user; no separate audit"). Deferred with an owner: the maintainer; event: the P2 phase closure record, for Phase 3's first plan. DP-7 (OQ-1285) moves with it. The rest of this Work stays in P2; the conditional cuts (S13 and S14, then S9) are `PL-1371` DP-3's trigger, each brought to the maintainer when it fires, never applied automatically.

#### SL-1369 — Slice 1: chart foundation — ChartFigure's column descriptors per RL-1307, its 13 call sites migrated, and register F39's socket diagnosis (NFR-463)

```yaml
id: SL-1369
family: slice
title: Slice 1: chart foundation — ChartFigure's column descriptors per RL-1307, its 13 call sites migrated, and register F39's socket diagnosis (NFR-463)
status: closed                 # draft → active → closed | retired (§1.2a)
created: 2026-10-01
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
phase: P2
work: WK-675
corrected_by: []
relates: [PL-1368, RL-1307, PL-1286, SL-1275]                      # ids only
```

`PL-1286` S1 (`:303`), cut as a draft row for its leaf plan, `PL-1368`
(`docs/plans/PL-01368-wk-675-slice-1-chartfigure-accessible-table-per-rl-1307-leaf-plan.md`). `ChartFigure`
becomes generic over the caller's row objects, with one `{ key, label, value }` descriptor per
column. That is `RL-1307`'s option (c), which supersedes `PL-1286`'s stale DP-1 text
(`:240`, `:249-250`, `:415-416`). The 13 call sites (`git grep -n '<ChartFigure' origin/main --
'frontend/src/*.vue'` at `1dd5e264`) move to the new API. The dev-only arity guard retires;
the slice adds a duplicate-key refusal that runs in every build (a visible error in place of the
table, never a silent key collision), `<th scope="row">` row headers, and empty-state
text that names no module. `cellUnder`'s stale text is corrected. The slice also diagnoses
register row F39 (port 3000 opened by the frontend test run). The auditor writes F39's dated
register resolution at close. First in the Work: nothing precedes it (`PL-1286` Sequencing).
It is ordered against WK-690 Slice 5 (SL-1275), which adds a `ChartFigure` caller: whichever
lands second migrates or uses the new API. **Gate:** the leaf plan's Activation needs, in a
separate activation PR: the maintainer's agreement and the lead's go.
Drafted as working id 9768; minted 2026-10-01 as SL-1369 (its leaf plan, drafted as working id 9769, minted as PL-1368).
(Activated 2026-10-03 as WK-675 Slice 1, on the maintainer's GO check of 2026-10-01, "2026-10-01 11:04:02 BST — GO: WK-675 Slice 1 (SL-1369, PL-1368) on lane A, with ONE correction to the dispatch record (DP-4's label is (b), not (a)); this entry is PL-1368 activation need 1's dated maintainer agreement"; dispatch record DISPATCH-WK-675-SL1369-2026-10-01.)
*(Closed 2026-10-03 on a clean slice audit (`audit-1369-2026-10-03.md`, range `origin/main...44bfbafe`, verdict CLEAN) and the dispatch record's Deltas 1 to 4; ledger `LG-1378`, minted from working id 9745. Precedent: `SL-1360` / `LG-1370`.)*


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

From “Workstreams” (line 386): **`expression` custom objectives** — SymPy derivation, the gradient/hessian compilation target, the authoring UI, and ~~lifting `expression_objectives_enabled`~~ making `expression_objectives_enabled` liftable **plus `custom_objective:author` and its check, which `06` FR-367 requires the `expression` kind to arrive with** | Added 2026-08-15 by OQ-573's decision, which moved this work out of WK-661 rather than deleting it: `02` FR-144/145, FR-150, §4.6, and `WF-702` Route B. It depends on nothing in WK-669–WK-675 and could equally be pulled into 1b if WK-661 finishes early — but it must not start before the certification machinery it fronts (FR-151) has run for a phase, which is the whole point of the decision

*(Amended 2026-09-30 by the lead, on `PL-1268` §Activation item 2 and `RL-1265` DP-1 to DP-3.)* Two corrections. First, "lifting `expression_objectives_enabled`" reads "making `expression_objectives_enabled` liftable", because DP-3 (a) keeps the default off: WK-690 switches it on nowhere, and enabling it for a workspace is a separate, dated maintainer decision after WK-690 closes (`RL-1265` DP-3). The `### WK-690` heading and its `title:` still read "lifting" and are deliberately left unchanged, because they are the row's identity string; this From line carries the correction. Second, FR-85, FR-86's field, FR-210 with FR-208's `spline` and `polynomial` arms, and FR-154's expression half left WK-690 for Phase 3 (`RL-1265`), spec change first, deferred with an owner: the maintainer, with the event being the P2 phase closure record, which lists them for P3's first plan.

**2026-09-28 — the start gate is MET** (item E3 in the deputy's OQ-stream entry; Maintainer decision by delegation (deputy, on the maintainer's instruction of 2026-09-28 11:24 BST), 2026-09-28 11:33:12 BST). The gate above says this work must not start before the certification machinery it fronts (FR-151) has run for a phase. That machinery shipped in WK-661 (`CR-754`, closed 2026-08-22). It has since run for a phase: P1b was accepted closed on 2026-08-27 (`CR-822`). **WK-690 must add `sympy`**: `grep -c -i sympy uv.lock` prints 0 at `12431a88`. It lands together with the `docs/skills-map.md` update that the dependency requires (`CLAUDE.md` §10). The first slice is the parser, brought to `02` §4.6's profiles (item E2, filed in the Track E spec PR).


#### SL-1271 — Slice 1: the parser brought to §4.6's four profiles, with its limits and the sympy pin (FR-144, FR-145, FR-36, NFR-483, `01` §4.5 `expression` check, `02` §4.6)

```yaml
id: SL-1271
family: slice
title: Slice 1: the parser brought to §4.6's four profiles, with its limits and the sympy pin (FR-144, FR-145, FR-36, NFR-483, `01` §4.5 `expression` check, `02` §4.6)
status: closed                  # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: dee49f781fd23f9df2e72161885c77fa17a6f1ab
phase: P2
work: WK-690
corrected_by: []
relates: [PL-1268]
```

`pricing_core.data.expressions` gains the `objective`, `factor`, `recipe` and `check` profiles, `where()`, and the node and depth limits, measured on the corpus before they are enforced. `sympy` is added at one exact pin with its `docs/skills-map.md` row. `03` FR-244 and the matching `02` §4.6 note land in one commit (`RL-1265` DP-5). `PL-1268` Slice 1. First in the chain: nothing precedes it. **Gate:** its leaf plan waits on **OQ-1266** (the exact `sympy` pin) being ruled. *(Title completed 2026-09-30 on auditor-plans' F1 for #943: it now lists every id that `PL-1268`'s Core scope table assigns to this slice.)*
Minted as `SL-1271` at #943's merge turn, 2026-09-30, with `python3 scripts/doc-id.py next --ref origin/main` at `08bd1c5a` (working id 9950 before the mint).
**Closed 2026-09-30** at #981's merge, `bd67fb5127e0ed57e6c5f4d360bdc4c1ce5ff3bc`, on a CLEAN slice audit (auditor-924d at `df66226c`) and the lead's merge (CLAUDE.md §13); its ledger is `LG-1304`. It was dispatched on 2026-09-30 by the lead from `PL-1295` on lane B. The `draft → active` flip was **not recorded at dispatch**. It is noted here rather than back-dated, and the row goes straight from `draft` to `closed`.

#### SL-1272 — Slice 2: symbolic derivation, the compilation target and the expression certificate (FR-144, FR-146, FR-147, FR-148, FR-149, FR-165, NFR-476, NFR-483, `02` §4.7 expression half)

```yaml
id: SL-1272
family: slice
title: Slice 2: symbolic derivation, the compilation target and the expression certificate (FR-144, FR-146, FR-147, FR-148, FR-149, FR-165, NFR-476, NFR-483, `02` §4.7 expression half)
status: closed                 # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: dee49f781fd23f9df2e72161885c77fa17a6f1ab
phase: P2
work: WK-690
corrected_by: []
relates: [PL-1268]
```

SymPy derivation of the gradient and hessian, a vectorised compiler through the platform's own expression tree (never `lambdify`), FR-165's per-round budget for both kinds (`RL-1265`), and the `symbolic_vs_numeric` certificate checks. `PL-1268` Slice 2. Starts after Slice 1 closes. *(Title completed 2026-09-30 on auditor-plans' F1 for #943: it now lists every id that `PL-1268`'s Core scope table assigns to this slice.)*
Minted as `SL-1272` at #943's merge turn, 2026-09-30, with `python3 scripts/doc-id.py next --ref origin/main` at `08bd1c5a` (working id 9951 before the mint).

**Closed 2026-10-01** at its mint PR #1025 (mint commit `ab2a1a7a`): slice audit CLEAN at `36a2f672` after F1–F6; ledger `LG-1350`; spike `RS-1351`. The row read `active` until the auditor's forward status flip (§1.6).

#### SL-1273 — Slice 3: the `expression` kind through the platform, behind the flag, with `custom_objective:author` (FR-144, FR-146, FR-150, FR-152, FR-163, FR-207, FR-366, FR-367, FR-448, FR-449, NFR-480, NFR-484)

```yaml
id: SL-1273
family: slice
title: Slice 3: the `expression` kind through the platform, behind the flag, with `custom_objective:author` (FR-144, FR-146, FR-150, FR-152, FR-163, FR-207, FR-366, FR-367, FR-448, FR-449, NFR-480, NFR-484)
status: closed                 # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: dee49f781fd23f9df2e72161885c77fa17a6f1ab
phase: P2
work: WK-690
corrected_by: []
relates: [PL-1268, PL-1382]
```

`kind: expression` in `model-schema`, `/derive`, the flag made liftable with its default off (`RL-1265` DP-3), certification as a job, and the objective error codes registered. `custom_objective:author`: the `06` §4.1 row, the enum member and the route check land in one commit. `PL-1268` Slice 3. Starts after Slice 2 closes. **Gate:** `CR-1247` Proposal 1 (c) is delivered first. That means the decision-maker's `RL-` (or ADR) with the `06` amendment, and WK-1178's permission-parity check, both merged before the commit that adds `custom_objective:author`. *(Title completed 2026-09-30 on auditor-plans' F1 for #943: it now lists every id that `PL-1268`'s Core scope table assigns to this slice.)*
**Closed 2026-10-05** on the slice audit (`handover/audit-sl1273-2026-10-04.md`, local) and its re-check of 2026-10-05, at the mint of ledger `LG-1412` (the executor's closing acts, `executor.md` mint step; `document-ids.md` §1.6).
(Activated 2026-10-04 as WK-690 Slice 3, on the maintainer's GO check, "2026-10-04 16:54:04 BST — DISPATCH GO: WK-690 Slice 3 (SL-1273 / PL-1382) on lane A; executor-1273 starts after #1106 merges"; dispatch record DISPATCH-WK-690-SL1273-2026-10-03.)
Minted as `SL-1273` at #943's merge turn, 2026-09-30, with `python3 scripts/doc-id.py next --ref origin/main` at `08bd1c5a` (working id 9952 before the mint).

#### SL-1274 — Slice 4: `expression` Factors (FR-95, FR-208's expression arm)

```yaml
id: SL-1274
family: slice
title: Slice 4: `expression` Factors (FR-95, FR-208's expression arm)
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: dee49f781fd23f9df2e72161885c77fa17a6f1ab
phase: P2
work: WK-690
corrected_by: []
relates: [PL-1268]
```

`Factor` gains the expression field and its validator arm. `resolve_factors` resolves it through the `factor` profile, and a numeric result is refused by name, with the message naming FR-210 (`RL-1265` DP-4). `PL-1268` Slice 4. It waits only on Slice 1, and on a free lane under `RL-1263`.
Minted as `SL-1274` at #943's merge turn, 2026-09-30, with `python3 scripts/doc-id.py next --ref origin/main` at `08bd1c5a` (working id 9953 before the mint).

#### SL-1275 — Slice 5: the authoring view, and `WF-702` Route B end to end (`02` §5.3)

```yaml
id: SL-1275
family: slice
title: Slice 5: the authoring view, and `WF-702` Route B end to end (`02` §5.3)
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: dee49f781fd23f9df2e72161885c77fa17a6f1ab
phase: P2
work: WK-690
corrected_by: []
relates: [PL-1268]
```

The Custom objective library's editor with live parse errors, the derived gradient and hessian display, and the loss-curve preview. It consumes OQ-550's ruling (WK-675's) if one exists by then, and otherwise records its `ChartFigure` caller in OQ-550's call-site count. One HTTP test file runs `WF-702` Route B. The flag's default is unchanged. `PL-1268` Slice 5. Starts after Slice 3 closes.
Minted as `SL-1275` at #943's merge turn, 2026-09-30, with `python3 scripts/doc-id.py next --ref origin/main` at `08bd1c5a` (working id 9954 before the mint).

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
status: closed
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 379): The register is a ledger, evidence is a file — RFC-896, P1–P5 | Adopted 2026-09-01 from RFC-896 by the reconciliation's dated acceptance line. **P1–P5 all merged 2026-08-31** (`fa87086`, `890b06e`, `f99b55d`, `cfed4f0`, `6b3459a`, `365ad18`, the `lead.md` enter step): the decision grammar held by check 29 via `scripts/register-lint.py`; `scripts/register-owed.py` generates the owed list a close compiled by hand; the ledger/evidence split is real at `docs/audit/findings/` with **F27** the worked exemplar; migration opportunistic-on-amendment with a falsifiable residue line (38 of 61 rows over the 1000-character threshold at landing). **Three findings filed from the work itself**: **F62**, **F63** (ten WK-671-attributed register rows in no closure record — disposition reserved to the maintainer, reopening a Work close is theirs alone), **F64**. **One deviation deliberately not back-dated**: no adoption plan was filed for work that landed ahead of this row — named here rather than closed over; the next §14 review disposes of it. **Closed 2026-09-28 by the deputy's dated line, by delegation, on [`CR-1173`](closures/CR-01173-wk-694-work-close-the-register-is-a-ledger-evidence-is-a-file.md)**, with RFC-896 §8 (b) deferred to WK-1170 as FD-1174.


### WK-695 — **File taxonomy, reference coding and custody — RFC-897 Stages 2–5**

```yaml
id: WK-695
family: work
title: **File taxonomy, reference coding and custody — RFC-897 Stages 2–5**
status: closed
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 380): **File taxonomy, reference coding and custody — RFC-897 Stages 2–5** | [`RFC-897`](rfcs/RFC-00897-file-taxonomy-reference-coding-and-custody-investigation-rev-2.md) §4–§7, built against the ruled inputs (Rulings 55–65). **Stage 2 — the reference-coding standard:** filename grammar and header block per category, over the twelve-category set as amended by RL-941 (the closure/audit record's three homes documented; the map/leaf and rulings-record grammar splits resolved here as the named items RL-941 hands over); one home per category per RL-942 (rulings and ledgers stay in `docs/plans/` under filename grammar; closure/audit records keep their three homes; register + findings keep their two); citation forms per RL-944's mixed grammar — spec, ADR, note, register/findings and workflow journey cite by their existing id, while plan, rulings record, ledger, closure/audit record, contract and process/charter/skill cite by dated filename — prospective only, no frozen retrofit (RL-944 §2a, matching RL-948 for the notes family); `docs/INDEX.md` as the legacy mapping so the standard covers every file without moving one (C1); `scripts/file-lint.py` wired into the gate warn-then-red with a dated flag-day; the five creating skills (`writing-plans`, `close-workstream`, `phase-review`, `adr-write`, `spec-change`) updated to emit the standard. **Stage 3 — the ownership map:** the category × role matrix (creates/amends/retires) as a living file in `docs/process/` (RL-945), every cell citing the charter line that grants it, empty rows and columns filed as findings per RFC-896's grammar. **Stage 4 — the workflow-loop audit:** the lifecycle triple per category (which step creates, reads, retires), the four verdicts, and the unreferenced population — 39 files at `4f95fb3`, 40 at `052afe3` — decomposed into verdict-2 findings or declared verdict-4; verdict-4 status is **derived** from an existing closure record wherever one covers the file, and an explicit declaration is required only for the residual — the 3 verdict-2 files plus any future file with no covering closure record — in whichever of the two forms the implementing slice chooses (RL-943). **Stage 5 — migration and enforcement:** the prospective standard live from the flag-day; legacy migrates opportunistically-on-amendment only, never a bulk rename (C1); the census re-runs at every phase close, with growth in uncategorised or verdict-2 files a red flag in the phase review. **Dependencies:** Stage 4 needs the committed census (`docs/research/file-census-5ef559d.csv`) and Stage 3's matrix; Stage 5 needs Stage 2; Stages 2 and 3 are independent now that Stage 1 and the gate ruling have landed (the note's §8 dependency chain). **Acceptance:** the note's §11 items (a)–(g). The notes move (the note's former S0) already landed as the investigation plan's Slice 4 (`1ec453b`, PR #544) **SUPERSEDED IN PART 2026-09-02 by WK-697.** [`RFC-937`](rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) §9 replaces **Stages 2 and 5** outright — its §1 standard and §4 one-time scripted migration do that work across the whole corpus rather than over the twelve categories alone — **lifts constraints C1 and C2**, and lapses **Rulings 63 and 65** by their own override clauses. RL-943 survives as check 38; Rulings 55–58 are absorbed; RL-941's category set and the Stage 0 census are kept as inputs. **Stages 3 and 4 survive and are not lost with this clause**: they become the two downstream Works RFC-937 §8's closing sentence names — the charter investigation (§1.6 made binding in each charter, with a directory-level `owner:`) and the create-read-retire audit (the process step per transition in §1.2's state machines). The row is kept, not reclaimed (`CLAUDE.md` §5). **Do not plan against Stages 2 or 5 from here.** The direct contradiction, named rather than left for a reader to hit: this row's C1 says legacy migrates opportunistically-on-amendment and *never a bulk rename*, and a bulk rename is precisely what RFC-937 authorises — two live rows planning one corpus in opposite directions is what this clause exists to prevent. Disposition by the lead under the maintainer's 2026-09-01 delegation, recorded at `docs/rulings/RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`. **Closed 2026-09-28 by the deputy's dated line, by delegation, on [`CR-1183`](closures/CR-01183-wk-695-work-close-file-taxonomy-reference-coding-and-custody.md)**, with Stages 2 and 5 delivered by WK-697 (`CR-1164`) and Stages 3 and 4 taken over by WK-1169 and WK-1170.


### WK-696 — A public face for a public repository — RFC-898, the residue

```yaml
id: WK-696
family: work
title: A public face for a public repository — RFC-898, the residue
status: closed
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 381): A public face for a public repository — RFC-898, the residue | Adopted 2026-09-01 from RFC-898 by the reconciliation's dated acceptance line. The content landed 2026-08-30 under the note's §7 light path (`README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `.github/` templates — the clause-2 exception's second instance); the exposure is discharged. **The residue: two impact rows.** Row 9 — this roadmap row existing — is discharged by this row itself. Row 6 — the two repository settings (private vulnerability reporting; issues with templates) — is **not verifiable from the tree**: it is evidenced by a dated maintainer line, which is the maintainer's to write and nobody else can supply it. **Acceptance:** the note's §8 (a) and (c)–(e) — the link check, a test issue filed through each form, and the auditor's outsider read of the `README` **Closed 2026-09-28 by the deputy's dated line, by delegation, on [`CR-1179`](closures/CR-01179-wk-696-work-close-the-closure-record.md).**


### WK-697 — **One id per governed thing — RFC-937, the whole standard**

```yaml
id: WK-697
family: work
title: **One id per governed thing — RFC-937, the whole standard**
status: closed
created: 2026-08-14
owner: maintainer
phase: P2
```

From “Workstreams” (line 382): **One id per governed thing — RFC-937, the whole standard** | Adopted 2026-09-01 from [`RFC-937`](rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) by the note's **own dated `accepted` status**, which the maintainer ruled that day is this row's acceptance line: RFC-937 arrived accepted rather than being moved to accepted by a reconciliation, so the *"reconciliation's dated acceptance line"* that WK-693, WK-694 and WK-696 cite has no referent here, and WK-695 already cites neither — the register admits more than one authority form. The ruling is recorded at `docs/rulings/RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md` §4, and the derivation rather than the conclusion is in the map plan's Authority section. **Scope:** the note's §1 standard in full — one global integer sequence across every row and document family, the five-word status vocabulary of §1.2a, the family-per-directory layout, the YAML header with its closed field set, roles per family, phase-as-milestone, and the generated index, ownership matrix and phase report; its §4 one-time scripted migration; its §5 impact map — root governance, all of `docs/`, seven role charters, two agents, every skill (twenty-six substantively, a header on all forty-six), fourteen scripts, twelve tests, two CI workflows, and every code and test file citing a document or requirement; and its §7 acceptance items (a)–(k). **Population, carried with its tree and its predicate because both matter:** the note's "767 files" at `8f5d57d` re-measures to **770** at `89dd2b1` and **771** at `bc7bc36`, but that figure uses a pattern including `VR-` product identifiers, which D5 places permanently out of scope — so the in-scope population at `bc7bc36` is **768**, with 3 files matching only via a `VR-` id. The corpus also grows with every new file citing a requirement, so a slice re-derives both numbers rather than quoting these. The auditor's pinned sweep at `89dd2b1` further corrects the note's own §5.6 evidence in two material places — `backend/src/app` and `backend/tests` each claim roughly the *combined* backend total (measured 88 + 93 + 28 = 209 against ~410 claimed), and `backend/migrations` is claimed at 3 against 28 measured — so W37-6's leaf plan is written from that sweep, never from §5's table. **Eleven slices** cut from §8's stages S1–S4 by `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`: four building the instruments in parallel, one building the migration script against a fixture corpus, **one supervised run that moves the whole corpus and must land at a gap with no open branches** and is never fanned out, four applying the conventions, and one proving acceptance (j) and (k). **Supersedes WK-695 in part** — see that row. **Decision points — updated 2026-09-02.** The plan recorded eight, two disposed of in it. **DP-1, DP-2 and DP-3 are ruled** as Rulings 66, 67 and 68 (`docs/rulings/INDEX.md#2026-09-02-w37-migration-preconditions-rulingsmd`), together with **RL-990** on a fourth point raised during execution — §1.5's vendored-skill criterion names `graphify`, `systematic-debugging` and the `vue-*` skills as vendored while defining vendored as *"anything shipping its own `LICENSE`"*, which exactly two of twenty-eight do; the parenthesis is ruled a gloss, not a detector. **Two consequences this row must carry.** First, **DP-2 blocks W37-4, not only W37-6** — item (d) and check 36 read one shared constant, so the earlier slice carries the earlier date. Second, **RL-987 enlarges W37-6's commit** by folding the creating instruments into it, ruled as a criterion — every instrument whose output checks 30–39 test — with the note's seven as a floor and `git-hygiene` and the skills README named for explicit disposition; **the maintainer's go-ahead for W37-6 must disclose that enlargement**, which the existing precondition does not cover. Still open: **DP-6**, blocking W37-9, discharged by a dated maintainer line on that slice's PR (`CLAUDE.md` §12 reserves an amendment to what that file requires), and **DP-4**, non-blocking, applied at W37-11. **`CLAUDE.md` §5's never-renumber rule yields to this work**, at two sites, by the maintainer's dated precedence ruling of 2026-09-01; a rule that yields still yields visibly. **Acceptance:** the note's §7 (a)–(k) **Progress, 2026-09-02.** **S1 complete** — W37-1 the standard and thirteen templates, W37-2 `doc-id.py`, W37-3 `doc-index.py`, W37-4 `audit-docs.py` checks 30-39 with ten broken-input proofs. **W37-5 merged**: `migrate` built and proven on a fixture corpus, then hardened after four defects were found in already-merged code by running it against the real tree. **W37-5b and W37-5c closed 2026-09-02** (PRs #617 and #647), each on a clean audit and the lead's merge per `CLAUDE.md` §13 — not the maintainer's, a Slice's close is the lead's. Full narrative, every precondition found only by building the slice, and every finding's adopted verdict (F76-F82, F86-F92 raised, discovery defects, the `RS` family `KeyError` fix, the vendored-manifest fifth abort point cleared): [`docs/closures/CR-01004-work-item-record-w37-5b-the-group-a-preconditions-slice.md`](closures/CR-01004-work-item-record-w37-5b-the-group-a-preconditions-slice.md) and [`docs/closures/CR-01005-work-item-record-w37-5c-the-second-precondition-slice.md`](closures/CR-01005-work-item-record-w37-5c-the-second-precondition-slice.md) — not restated here at length, per this file's own restated-status-goes-stale lesson ([`RFC-756`](rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md)). On a throwaway snapshot of the real corpus, `migrate()` ran to completion at that close. **W37-6 run 2 — the real migration — merged to `main` 2026-09-17**, across four PRs, in order: `#784` (`0651c1e265648cbd3918adfc729ad965b83b1e0b`, the sentinel h1-check36 row) → `#782` (`71f5a2208c7a92bad486ae128775a4a42c7ebc63`, the migration itself — squash of the tool's own run at `M=0651c1e`, commit 1's tree `6d058ba642481404815ab573e848a8cf34e671ee`, plus commit 2's restores, reflows, test dispositions, `docs.yml` verify-ref fix and sweep-enumeration fix) → `#785` (`1cd489c870f9f117c19f009f0a096dc8ac748929`, the closure/(g) record `CR-1063` and this ledger's UNFREEZE, `#757` recorded as the first W37-11 item) → `#783` (`4d9fe1d62328285ac0483b047c3959e39e0f5bd6`, skills — `doc-id-migration-run` added, five skill/role updates capturing what the run learned). **`4d9fe1d` is HEAD at this writing.** **Standing state at `4d9fe1d`, RFC-937 §7:** (a)-(f) and (h) evidenced (checkpoint 3's close record re-measures every delivered-but-untested item); (g) a standing, disclosed FAIL — `CR-1063` §6 breaks down `classified-by-none = 251` of 971 by cause — deferred to W37-11 with `#757` its first item; (i) — "every H row in §5 closed by a named commit" — walked in checkpoint 3's close record. `_docverify.EXPECTED_VERDICTS`: 8 PASS, 15 DISCLOSE, 1 FAIL (g), 24 rows. Register: F87 discharged (proven on `docs/contracts/openapi/gi-pricing.yaml`, a real non-markdown F83-exempt file, not a fixture); F90 no-change, already ruled at the right authority (`CR-1050`); F92 owner of record W37-11, count corrected 53→50; F107-F110 filed at checkpoint 3, each with an FD- essay: F107 the idempotence gap, F108 check-35's two-clause shape (its `W37-10` owner-tag literal corrected to `W37-7`), F109 the pinned-base CI-verify read (a design choice for W37-11's own leaf plan Decision points table, not a silent pick), F111 the vendored-sweep mechanism gap (fixed before close for the two corrupted scripts, PR #788; the sweep-reaches-vendored gap itself is W37-11's), F110 the `(d → W37-11)` docstring/`tracked_files` mismatch — all four owned W37-11 or lead→W37-11. **Checkpoint 3** (`.claude/skills/close-workstream`'s checklist, `docs/plans/PL-01058-w37-6-migration-run-ledger.md:37-38`, corrected 2026-09-18 per `CLAUDE.md:283`): this row's own rewrite, the register updates above and the checkpoint's close record, [`CR-01065`](closures/CR-01065-w37-6-checkpoint-3-close.md), are one PR — see that record for the full re-measure of every delivered-but-untested item and RFC-937 §7(i)'s row-by-row commit walk. **Next: Stage 3** — W37-7, W37-8, W37-9 and W37-10 (the four "applying the conventions" slices and the one proving acceptance (j) and (k), per the map plan's eleven-slice cut). **W37-11's first item was `#757`**, and it had already merged when this paragraph was written: `29e7a9c` (`29e7a9ce41459ff1f4b4b2658d177c6109d35a58`, 2026-09-18 01:45:22 BST), rebased onto `71f5a22` with its own gate and CI, per the deputy's ruling of 2026-09-17. It took row (g)'s g2 `classified-by-none` from 251 to 207, and (g) stayed the standing FAIL. *Corrected 2026-09-27 by W37-11 (`PL-1144` Task 11; the deputy's condition 4 of 11:16:34 BST). The clause said "(rebase onto `71f5a22`, …)", as work still to do.* The idempotence gap (F107), the census-row shrink, the check-35 shape (F108), the pinned-base read (F109), and the docstring mismatch (F110) are also W37-11's. **Progress, 2026-09-27.** W37-7 (#795, `4ed1f88e`; `LG-1137`), W37-8 (#806 to #814; `LG-1141`), W37-9 (#817, `49c06ad7`; `LG-1143`) and W37-10 (#804, `536d3cc3`; `LG-1139`) are closed, each on the auditor's closing record and the lead's merge (#815, #818, #819). **W37-11** runs under `PL-1144` and `RL-1145`. Its instrument PR merged as #821 (`47065da5`). Its evidence for rows (g), (k) and (j) is in `LG-1148`. At `47065da5`, (g) reads `classified-by-none=207`, the same as at `29e7a9c`, with every file assigned to a cause, and stays the standing FAIL, deferred with an owner under RL-1145 DP-4 (b). ~~**The Work close is pending.** It is recorded in the closure record [`CR-1164`](closures/CR-01164-wk-697-work-close-the-closure-record.md), and the row's `status:` stays `active` until the maintainer's dated line (D7, by delegation) accepts the close (`CLAUDE.md` §13).~~ **Closed 2026-09-27 15:25:01 BST by the maintainer's dated line (5), by delegation (D7), on [`CR-1164`](closures/CR-01164-wk-697-work-close-the-closure-record.md).** *Struck and closed 2026-09-27 on the D7 line; `status:` moved from `active` to `closed`.*


### WK-1169 — The charter investigation — RFC-937's binding charters

```yaml
id: WK-1169
family: work
title: The charter investigation — RFC-937's binding charters
status: active
created: 2026-09-28
owner: maintainer
phase: P2
```

Minted 2026-09-28 by `CR-1167` Proposal 5.1 (plan review 14, accepted by delegation 2026-09-27 16:18:24 BST), the first of the two downstream Works RFC-937's closing section names. **Subject:** the ownership table of `document-ids.md` section 1.6 made binding in each role charter, with a directory-level `owner:`. **Scope, by reference and not restated** (a restated list is the copy that goes stale, RFC-756): every item `CR-1164` (the WK-697 closure record) section 10 lists as taken over with the event "the charter investigation's first slice", and every register row `CR-1167` dispositions to that event. **Status `active`: listed, not started.** Its first slice is the event those rows wait on; no map plan exists yet.

**2026-09-28:** also carries RFC-897 §5 (Stage 3, the ownership map), transferred at WK-695's close (`CR-1183`), 2026-09-28.

### WK-1170 — The create-read-retire audit — RFC-937's transition steps

```yaml
id: WK-1170
family: work
title: The create-read-retire audit — RFC-937's transition steps
status: active
created: 2026-09-28
owner: maintainer
phase: P2
```

Minted 2026-09-28 by `CR-1167` Proposal 5.1 (plan review 14, accepted by delegation 2026-09-27 16:18:24 BST), the second of the two downstream Works RFC-937's closing section names. **Subject:** the process step for each transition in the state machines of `document-ids.md` section 1.2, and the register, instrument and verify tooling those transitions depend on. **Scope, by reference and not restated** (a restated list is the copy that goes stale, RFC-756): every item `CR-1164` (the WK-697 closure record) section 10 lists as taken over with the event "the create-read-retire audit's first slice", and every register row `CR-1167` dispositions to that event. **Status `active`: listed, not started.** Its first slice is the event those rows wait on; no map plan exists yet.

**2026-09-28:** also carries RFC-897 §6 (Stage 4, the create-read-retire verdicts, including the unreferenced-plans decomposition), transferred at WK-695's close (`CR-1183`), 2026-09-28.

**2026-09-30:** also owns FD-1280's draft-RL guard and FD-1282's frozen-file enforcement, 2026-09-30, the maintainer's entry 06:00:41. *(Amended 2026-09-30 by the lead, on the maintainer's entries "2026-09-30 06:00:41 BST — MERGE-ACK #947 (FD-1280..1282, the F-W10-2 owner); DECISIONS on FD-1280 and FD-1282" and "2026-09-30 06:19:28 BST — MERGE-ACK #921 (FD-1283); WK-1170 confirmed as owner of the FD-1280/1282 checks", which gives this line's wording. PL-1276 takes them into its scope at activation.)*

### WK-1178 — P2 standing maintenance: hotfixes, dependency bumps and security findings

```yaml
id: WK-1178
family: work
title: 'P2 standing maintenance: hotfixes, dependency bumps and security findings'
status: active
created: 2026-09-28
owner: maintainer
phase: P2
```

Minted 2026-09-28 on the maintainer's instruction of that day ("yes record and implement", answering the deputy's GitHub security review; the deputy's entry 13:10:06 BST in the channel, item 1). `process/document-ids.md` (section 1.9, the PR-title rule) routes a PR that arrives without an `SL-` — *"a hotfix, an external contributor, a dependency bump"* — to *"the phase's standing `WK- maintenance`"*, and Phase 2 had none. **Scope:** work that belongs to no other Work; each item names its `FD-` or its trigger. **First items:** the dependency and workflow hardening finding filed with the GitHub security review, discharged by that review's hardening PR. **Status `active`:** a standing item; it closes with its phase.

**FR-177 is WK-1178 scope** (`specs/02-modelling.md`: the joint measurement of an `interaction` Factor, permutation importance and partial dependence through its operands' source columns). FR-176, FR-177 and FR-178 moved here from WK-690, which is `expression` custom objectives, by FD-1195. **Dated 2026-09-28:** the deputy's ruling DP-FD1195-2 (entry of 21:41:20 BST) delivers FR-178 only in the FD-1195 PR and makes FR-177 **its own WK-1178 PR**; FR-177 carries a dated amendment naming the owner as WK-1178, and it is not built at that date. **FR-178 is delivered in two parts:** partial dependence in #880 (`9fa2b833`); the permutation-block omission record in #887 (open) — the deputy's correction of 2026-09-28 22:52:41 BST, which withdraws its earlier reading that #880 delivered FR-178.

**NFR-526, NFR-527 and NFR-536 are measured under WK-1178**, on the exit tree *(added 2026-09-29 on `CR-1247`, and the maintainer's entry "2026-09-29 17:27:28 BST · maintainer (acting on the maintainer's behalf) · ACCEPTANCES: the WK-672 Work close (#906) and plan review 16 (#905), per proposal", §2 row 7: "NFR-526, 527 and 536 are measured under WK-1178.")*. They measure paths built today (API metadata p95, Job submission latency and trace propagation), so G4 reads them as measured, not carried.

#### SL-1300 — WK-1178 fix slice — compile_bundle refuses a step ref not pinned at its exact version (FR-237)

```yaml
id: SL-1300
family: slice
title: WK-1178 fix slice — compile_bundle refuses a step ref not pinned at its exact version (FR-237)
status: closed                 # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut by the planner (draft); lead dispatches (active)
tree: eeda8f4ba20d247ac18d6a35d7f81589c8527ed2
phase: P2
work: WK-1178
corrected_by: []
relates: [PL-1299, FD-1297, RL-1298]
```

`compile_bundle` refuses a `table`, `lookup` or `model_call` step whose ref is not pinned at its exact version, with `RATING_VERSION_UNPINNED`. `03` §5.1 gives that code a meaning, spec first, in the same commit. The model path's bare `KeyError`s at score become coded. The owner, severity, scope, acceptance and order are the maintainer's, as FD-1297 records under *Disposition*. Leaf plan `PL-1299`. *(Minted 2026-09-30 as SL-1300. The id was assigned in the lead's mint train, stacked on #964's RL-1298: `doc-id.py next --ref origin/main` printed 1298 at `4009de14`. It was filed under working id 9872.)* **Order:** it merges before WK-1250 Slice 1 is dispatched, since `compile.py` has a single writer. It takes the next free `RL-1263` slot and does not pre-empt WK-674 Slice 2 or WK-690 Slice 1. **Gate:** its leaf plan's DP-F1 to DP-F3 are ruled by RL-1298.
**Closed 2026-09-30** at #988's merge, `2118679b3e1cb0bce5ffae01dc02a54ad651890a`, on a CLEAN slice audit (auditor-plans at `5578bdf8`) and the lead's merge (CLAUDE.md §13); its ledger is `LG-1308`. `FD-1297` is resolved by it.

#### SL-1315 — WK-1178 slice — FR-244's enforced allow-list and FR-274's guard over every authored rating string

```yaml
id: SL-1315
family: slice
title: WK-1178 slice — FR-244's enforced allow-list and FR-274's guard over every authored rating string
status: closed                  # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut by the planner (draft); lead dispatches (active)
tree: 9f63d0feee524815e7e0c68c99a53ac3f80e6c37
phase: P2
work: WK-1178
corrected_by: []
relates: [PL-1314, RL-1312, RL-1313]
```

The code that the FR-244 ruling, RL-1312, assigns to WK-1178. FR-244's operator and function allow-list is enforced at save over every authored string: `expr`, `condition`, clamp bounds and `key_expr`. FR-276's compile, FR-274's division guard, and the determinism and scale checks are widened to the same strings, and `??` is never a guard. A residual evaluation failure at scoring gets its own code, not `RATE_TABLE_MISS`. It discharges the finding filed as #968 (FD working id 9885). Leaf plan `PL-1314`. *(Minted 2026-09-30 as SL-1315, by hand in the lead's batch-4 mint turn. It was filed under working id 9832.)* **Order:** after the fix slice (PL-1299) and before WK-1250 Slice 1, serialised on `compile.py` under `RL-1263`. **Gate:** its DP-G1, DP-G3, DP-G4 and DP-G5, ruled by RL-1313. DP-G1 is where FR-244's amended text lands: WK-690 Slice 1, Task 6.

**Closed 2026-09-30** at #1012's merge, `3a5f7cd5ba869eddf913761dba29d636e66afe94`, on a CLEAN slice audit (auditor at `3fa635eb60c18e05103205696cfd504ad69ba5ca`, recorded in the maintainer's channel entry "2026-09-30 18:07:45 BST") and the lead's merge (CLAUDE.md §13); the maintainer's MERGE-ACK and read-back ("2026-09-30 19:28:53 BST — #1012 read-back verified; SL-1315 closed") confirm it. Its ledger is `LG-1332`. The row read `active` after the merge and was flipped here, a forward status, by the auditor at `origin/main` 248dbf11.

#### SL-1352 — WK-1178 hotfix — runner-independent template-certificate test

```yaml
id: SL-1352
family: slice
title: WK-1178 hotfix — runner-independent template-certificate test
status: closed                  # draft → active → closed | retired (§1.2a)
created: 2026-10-01
owner: executor
tree: 7190787f494a921f89339ae62f8e3ae666bc4e2b
phase: P2
work: WK-1178
corrected_by: []
relates: [FD-1354, LG-1353, LG-1350]
```

Test-only hotfix for main's red CI after #1025: `test_template_certificate_unchanged` pinned a runner-dependent `max relative error` figure. The comparison normalises every measured figure a template certificate prints and bounds the two finite-difference errors by the engine's tolerance; a guard test fails if any other figure survives. No leaf plan; the dispatch record `DISPATCH-WK-1178-HOTFIX-9790-2026-10-01.md` (local) and the maintainer's ruling of 2026-10-01 are the scope. *(Minted 2026-10-01 as SL-1352; filed under working id 9790. Ledger `LG-1353`, finding `FD-1354`.)*

*(Reopened 2026-10-01 05:11 BST to `active`: CI run 36812617020 at `5a4beb63` failed on a second runner-dependent figure the first fix did not normalise; the lead's Delta 5 and Delta 6 are the rework scope. A fresh auditor re-closes.)*

#### SL-1360 — WK-1178 slice — the permission-parity check (PL-1359, RL-1305)

```yaml
id: SL-1360
family: slice
title: WK-1178 slice — the permission-parity check (PL-1359, RL-1305)
status: closed                  # draft → active → closed | retired (§1.2a)
created: 2026-10-01
owner: planner                   # cut by the planner (draft); lead dispatches (active)
tree: f95e10007329575aac81283d7c3832d8b2db1164
phase: P2
work: WK-1178
corrected_by: []
relates: [PL-1359, RL-1305, CR-1247, RL-1236, PL-1268]
```

A pytest invariant fails the gate in three cases: `06` §4.1's permission tables and `model_schema.Permission` disagree; a Built name has no check site (a flattened, reach-proved `requires()` route dependency, or an AST-found `require_permission(` call) and no owner; or a Built name has a check site and still carries an owner (`CR-1247` Proposal 1 (c), decided by `RL-1305`). It must merge before WK-690 Slice 3's commit that adds `custom_objective:author` (`PL-1268` Slice 3). It retires `RL-1236`'s interim re-derive-at-each-close rule when it merges. Leaf plan `PL-1359`, which supersedes `PL-1279`, activated with this row. *(Minted and activated 2026-10-01 as SL-1360, on the maintainer's entry "2026-10-01 08:04:53 BST — correction ACCEPTED (RL 9856 = RL-1305, already minted); lane B proposal AGREED, with the delta in the dispatch record".)* *(Closed 2026-10-01 on a clean slice audit: the executor ledger is `LG-1370`, and the slice delivers in PR #1049 with the merge to come.)*

#### SL-1367 — WK-1178 slice — FD-1335 Part A: the /score and /score/compare 200 responses documented, and one untyped-body guard over 2xx responses and JSON request bodies

```yaml
id: SL-1367
family: slice
title: WK-1178 slice — FD-1335 Part A: the /score and /score/compare 200 responses documented, and one untyped-body guard over 2xx responses and JSON request bodies
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-10-01
owner: planner                   # cut by the planner (draft); lead dispatches (active)
tree: 9b0fb97c9ed1cea743639897351191bc1a862041
phase: P2
work: WK-1178
corrected_by: []
relates: [FD-1335, FD-1366, PL-1364, PL-1348, SL-1345, RL-1343, RL-1365]
```

`FD-1335` Part A: `responses={200: {"model": ScoringResult}}` on `POST /api/v1/score` and the `ScoreComparison` equivalent on `POST /api/v1/score/compare`, with the raw `Response` kept and no outbound validation (`NFR-502`); `docs/contracts/` regenerated (`FR-451`); `NFR-502` measured again in a solo window; and a guard in `backend/tests/test_contracts.py` over both forms of an untyped JSON 2xx response, each form proven red first, with four permanent exclusions and twelve marked `pending FD-1335 part B`. Leaf plan `PL-1364`. **Serialised after `SL-1345` merges**, by the lead's decision on the evidence: both edit the `responses=` argument on the same two `score.py` decorators, which is not registry-exempt (`RL-1263`), and the contract must document the post-ladder rung shape. It lands before WK-675 dispatches a slice that consumes `/score` or `/score/compare` (`FD-1335` *Disposition* item 1). Filed under working ids 9787 (this row) and 9788 (the plan), allocated by the lead; both are minted at the plan PR's merge turn.

*(Amended before mint, 2026-10-01, by the maintainer's decision, relayed by the lead.)* The guard is now one guard over both 2xx responses and JSON request bodies, folding in `FD-1366` (filed as working id 9779). Each side is shown red first on broken input. Multipart bodies are excluded with a citation. The five untyped request routes are temporary exceptions: four are marked `pending FD-1366 Part B`, and `seed-from-model` is marked `pending FD-1357's fix DP`. No handler outside `score.py` is edited. `FD-1366` Part B types the four existing shapes in a later slice. DP-A1 and DP-A2 are ruled by `RL-1365` (filed as working id 9783). *(Minted 2026-10-01 as SL-1367, filed under working id 9787; its plan is PL-1364, mint batch A.)*

#### SL-1377 — WK-1178 fix slice — FD-1357: multi-factor seeding per RL-1361, typed seed request and 201

```yaml
id: SL-1377
family: slice
title: WK-1178 fix slice — FD-1357, multi-factor seeding per RL-1361, typed seed request and 201
status: closed                  # draft → active → closed | retired (§1.2a)
created: 2026-10-03
owner: planner                   # cut by the planner (draft); lead dispatches (active)
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
phase: P2
work: WK-1178
corrected_by: []
relates: [FD-1357, RL-1361, PL-1267]
```

`seed_from_model` seeds a GLM with two or more factors: one seed request names one Factor and gives one table with one key, bound by `factor_ref` to the Factor version the model pins (`RL-1361` sections A and D; FD-1357, HIGH, on G2's path). The seed route's request body becomes a typed `model-schema` request and its 201 a typed response, both published under `docs/contracts/schemas/generated/` (the maintainer's rules (i) and (ii); the seed-from-model entry of `FD-1366`). The `[seeding]` texts of `RL-1361` are applied byte for byte. Leaf plan `PL-1376`, `active`. **Order:** lane B, after `SL-1360` and before the FD-1356 fix, the RL-1343 decimal-output fix and `PL-1364` (the maintainer, 2026-10-01, about 10:10 BST). *(Filed 2026-10-01 under working id 9763, reserved by the lead. Minted 2026-10-03 as SL-1377; its plan is PL-1376, the FD-1357 batch.)*
(Activated 2026-10-03 as the FD-1357 fix (WK-1178), on the maintainer's GO check, "2026-10-03 16:59:11 BST — DISPATCH GO: the FD-1357 fix (SL-1377, PL-1376; WK-1178) on lane B; this entry is PL-1376 activation need 7's maintainer agreement"; dispatch record DISPATCH-WK-1178-SL1377-2026-10-03.)

#### SL-1409 — WK-1178 fix slice — FD-1356: a validation rule is approved only through the approval workflow

```yaml
id: SL-1409
family: slice
title: WK-1178 fix slice — FD-1356: a validation rule is approved only through the approval workflow
status: closed                 # draft → active → closed | retired (§1.2a)
created: 2026-10-04
owner: planner                   # cut by the planner (draft); lead dispatches (active)
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
phase: P2
work: WK-1178
corrected_by: []
relates: [FD-1356, RL-1301, PL-1306, SL-1256, RL-1407, PL-1408]
```

`FD-1356`'s fix (HIGH): rule approval goes through `approvals.submit` and `approvals.decide`, `_carry_to_the_artifact` gains the validation-rule branch, and the direct approve route becomes a thin client of the decide path or is removed (DP-1). A quorum of 2 leaves the rule in `review` after one approval. A dry-run whose outcome is `error` is refused at submit and at approve, one red-first case per cause (missing column, unknown check, missing table), and a `fail` outcome stays accepted. `RL-1301` A.4.5's temporary `approve_rule` allowance is removed red first. Rule approvals that no approval request backs are reset to `review`, with the count recorded (follow-on 2). Task 0 is the maintainer's containment query over every `gipricing*` database, with a STOP on a non-zero result; it printed 5 at planning time. The maintainer decided DP-0 as (c): export the rows, drop the scratch database, re-run. The re-run printed 0 on 2026-10-01, to be re-confirmed at dispatch. The remedies of FD-1415 (an approved rule's dry run cannot be replaced) and FD-1414 (a Rule Set runs only approved, existing members) also ride in this slice, as the maintainer decided. RL-1407 rules the plan's decision points and these remedies. Leaf plan PL-1408 (`active`). **Activation needs:** WK-674 S2 (`SL-1256`) merged (the maintainer, 2026-10-01 ~10:10 BST, order (b) S2 → this fix); lane B order `SL-1360` → the FD-1357 fix → this slice → the `RL-1343` decimal fix → FD-1335 Part A; the plan's decision points ruled; the maintainer's agreement and the lead's go in a separate activation PR. *(Filed 2026-10-01 under working ids 9761 (this row) and 9762 (the plan), reserved by the lead. Minted 2026-10-04 as SL-1409; its plan is PL-1408 and its ruling RL-1407.)*
**Closed 2026-10-05** on the slice audit (LG-1417 §"Closing note"; local working copy: `handover/audit-sl1409-2026-10-05.md`) and its re-check, at the mint of ledger `LG-1417` (the executor's closing acts, `executor.md` mint step; `document-ids.md` §1.6).
(Activated 2026-10-05 as the WK-1178 FD-1356 fix slice, on the maintainer's GO check, "2026-10-05 09:44:39 BST — DISPATCH GO: FD-1356 fix (SL-1409 / PL-1408) on lane B, option (b); executor-1409 starts once the `__all__` registry amendment merges (or once WK-690 S3 merges, if that comes first)"; dispatch record DISPATCH-WK-1178-SL1409-2026-10-04.)


### WK-1250 — Sub-graph composition and MTA/cancellation pricing — FR-217's inlining and FR-218's authoring half

```yaml
id: WK-1250
family: work
title: Sub-graph composition and MTA/cancellation pricing — FR-217's inlining and FR-218's authoring half
status: active
created: 2026-09-29
owner: maintainer
phase: P2
```

Opened `draft` 2026-09-29 on `CR-1247`, and the maintainer's entry "2026-09-29 17:27:28 BST · maintainer (acting on the maintainer's behalf) · ACCEPTANCES: the WK-672 Work close (#906) and plan review 16 (#905), per proposal", §2 row 10: "Accepted as amended. #907 is the interim fail-closed fix (HIGH). A **new P2 Work** for FR-217's inlining and FR-218's authoring half is opened `draft` by the lead, its map plan by the planner. WK-669 is not reopened; CR-838 is corrected (16:25:49 item 4)." **Scope** (`CR-1247` Proposal 10, option (a)): FR-217's inlining limb, where `compile_bundle` resolves `SubGraphRef.mount_point` and inlines the pinned sub-graph; and FR-218, where the `purpose` mount is declared on the Rating Version and version-pinned, and the interim guard is replaced by the real check. **Sequenced after WK-674 and before WK-675**, so that WK-675's DAG designer authors a sub-graph against a backend that inlines one. *(Amended 2026-09-30 by the lead, on `RL-1263` item 5.)* The "after WK-674" is not a blanket dependency: it names no WK-674 slice or artifact, so under item 5 it is bare sequencing and is lifted (`PL-1278` re-derives it so). What orders WK-1250 against WK-674 is lane and file contention under `RL-1263`: at most two build slices at once, and slices that change the same file serialise. The designer's sub-graph view stays WK-675's. **Predecessors:** FD-1241 (`CR-838` marks FR-217 delivered, but its versioned-artifact, pin and bundle-time inlining limbs are not built); the interim fail-closed fix, #907 (`a78fe98f`, under WK-1178); and FR-218's interim rule, `RL-1242` (#911). **Its map plan is the planner's**, and its activation is the maintainer's, on that map plan. **Minted 2026-09-29** at #916's merge turn, from `doc-id.py next --ref origin/main` at `a380aa7a` (working id 9670).

**Goal:** DAG designer, rate tables, reference data, real-time + batch scoring, dislocation.

**Demo-able outcome:** **`WF-699` end to end** plus the deployment half of `WF-701` — an
approved model becomes rate tables, becomes a rating version, passes regression and
dislocation, and serves a live quote inside the latency budget.

Set `active` 2026-09-30 on the maintainer's entry "2026-09-30 22:33:30 BST — DECISIONS on your 23:05 (WK-1250 S1 blocked; lane re-order; ci-1018)", Decision 1, quoted verbatim: *"2026-09-30 — the maintainer (by delegation) accepts PL-1254 (the WK-1250 map, three slices) as the plan for WK-1250. Resolvers: DP-1, DP-3 and DP-4 by RL-1309. **DP-2 is open** (blocking Slices 2 and 3). Per PL-1254's Activation step 1 the plan stays `draft` until DP-2 has a resolver. WK-1250 is set `active`, and its three `SL-` rows are cut `draft`."* The form follows WK-675 (an active Work with a draft map, `PL-1286`). DP-2's ruling is in preparation; when it mints, `PL-1254` goes `active` (a status flip) and then `PL-1325`.

*Dated 2026-09-30, on the maintainer's entry "2026-09-30 22:33:30 BST", Decision 2: `PL-1254` goes `active` (a status flip), because every blocking decision point now has a resolver. DP-1, DP-3 and DP-4 are resolved by `RL-1309`. DP-2 is resolved by `RL-1344`, minted in mint batch 12 (#1022, 36b2a121). The frozen plan's resolver column is not edited; this line records the resolvers (`PL-1254` Activation step 1). `PL-1325` goes `active` in the same PR, because its prerequisite 2 ("PL-1254 `active`, and WK-1250's `SL-` rows cut") holds at merge.*

#### SL-1339 — Slice 1: the sub-graph as a stored, versioned artifact (FR-217's artifact limb)

```yaml
id: SL-1339
family: slice
title: Slice 1: the sub-graph as a stored, versioned artifact (FR-217's artifact limb)
status: closed                   # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 8cef871d4ec30869dc3ef20559f3cac64e239a5c
phase: P2
work: WK-1250
corrected_by: []
relates: [PL-1254]
```

`PL-1254` Task 1; leaf plan `PL-1325` (draft until `PL-1254` is active, its prerequisite 2). Minted as `SL-1339` at this PR's merge turn, 2026-09-30, with `python3 scripts/doc-id.py next --ref origin/main` at `8cef871d` (1339 onward).

**Closed 2026-10-01** at its mint PR #1034 (mint commit `0e04c4ea`): slice audit CLEAN at `04e8e53e`, adopted items closed CLEAN at `78674b7e`; gate 7/7 at `44bd29e0`; ledger `LG-1355` (re-minted from 1352 when #1035 took 1352 to 1354). The row read `active` until the auditor's forward status flip (§1.6).

#### SL-1340 — Slice 2: the pin and the inlining (FR-217's pin and inlining limbs; FR-258's inlined steps)

```yaml
id: SL-1340
family: slice
title: Slice 2: the pin and the inlining (FR-217's pin and inlining limbs; FR-258's inlined steps)
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 8cef871d4ec30869dc3ef20559f3cac64e239a5c
phase: P2
work: WK-1250
corrected_by: []
relates: [PL-1254]
```

`PL-1254` Task 2. ~~Blocked on DP-2 (open).~~ *DP-2 ruled 2026-09-30 by `RL-1344` (mint batch 12); still waits on the slices before it.* Minted as `SL-1340` at this PR's merge turn, 2026-09-30, with `python3 scripts/doc-id.py next --ref origin/main` at `8cef871d` (1339 onward).

#### SL-1341 — Slice 3: FR-218's purpose mount and the real check (retires `RL-1242`)

```yaml
id: SL-1341
family: slice
title: Slice 3: FR-218's purpose mount and the real check (retires `RL-1242`)
status: draft                  # draft → active → closed | retired (§1.2a)
created: 2026-09-30
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: 8cef871d4ec30869dc3ef20559f3cac64e239a5c
phase: P2
work: WK-1250
corrected_by: []
relates: [PL-1254]
```

`PL-1254` Task 3. ~~Blocked on DP-2 (open).~~ *DP-2 ruled 2026-09-30 by `RL-1344` (mint batch 12); still waits on the slices before it.* Minted as `SL-1341` at this PR's merge turn, 2026-09-30, with `python3 scripts/doc-id.py next --ref origin/main` at `8cef871d` (1339 onward).



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
works: WK-676, WK-677, WK-678, WK-679, WK-680, WK-681, WK-682, WK-691, WK-1251, WK-1288

**2026-09-29: requirements carried into Phase 3 without a Work.** CR-1212 P12 records that FR-432, FR-433, FR-434, FR-435 and FR-438 were on no roadmap row. FR-434 and FR-435 went to WK-674 in P2 (CR-1212 P12; placed in PL-1237). The other three are carried to P3, and no P3 Work names them yet:

- **FR-433** (the Helm chart and Kubernetes manifests) moves to Phase 3 by `RL-1232` DP-1 (b), and `07` FR-437 and FR-433 carry the dated amendment. It is deferred with an owner, the maintainer. **Event:** the P2 closure record, which names the Work that takes it.
- **FR-432** and **FR-438** are carried to P3 by CR-1212 P12, which names no owner. They are listed here so the gap is visible. Their owner is a question for plan review 16.

No Work is created by this note. Creating one is a scope decision, and the maintainer's.

*(Amended 2026-09-29: the scope decision is made. `CR-1247` Proposal 7, accepted in the maintainer's entry "2026-09-29 17:27:28 BST · maintainer (acting on the maintainer's behalf) · ACCEPTANCES: the WK-672 Work close (#906) and plan review 16 (#905), per proposal", §2 row 7, creates WK-1251 (production packaging and supply chain, below), which owns FR-432, FR-433 and FR-438. FR-433's event, "the P2 closure record, which names the Work that takes it", will be met when the P2 closure record names WK-1251.)*

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

**2026-09-30:** also owns `07` §5.3's Service accounts view (`/admin/service-accounts`), placed here in P3 by FD-1284 option D and the maintainer's entry "2026-09-30 05:35:06 BST — SCOPE DECISION: #949 [FD-1284, cited by its working id in the entry], the `07` §5.3 platform views, option D (split by view)" ("Service accounts to **WK-676**"). **A spec change comes first:** `07` §5.1 declares create, rotate and revoke for service accounts but no list `GET` route, and the view needs one. This is placement, not a cut, and nothing is built ahead of P3 (`CLAUDE.md` §0). (Amended 2026-09-30 by the lead, on FD-1284 and the maintainer's entry 05:35:06.)


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

*(Dated 2026-09-30 by the lead, on the maintainer's entry "2026-09-30 11:56:33 BST — DECISIONS: slice order after the split; FR-384 confirmed; FR-383 and FR-385 owners": `06` FR-385 (expedited changes, an `ApprovalPolicy` feature, `06` §4.2) was held by no roadmap row; it is already raised as `FD-1281`, whose register owner cell names this Work. It is **owned by this Work** and joins its requirement list by a dated amendment when its map plan is cut.)*


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

*(Dated 2026-09-30 by the lead, on the maintainer's entry "2026-09-30 11:56:33 BST — DECISIONS: slice order after the split; FR-384 confirmed; FR-383 and FR-385 owners": `06` FR-383 (the uniform per-artifact history view, `06` line 179, route `06` §5.1 line 542) was held by no roadmap row. It is **owned by this Work** — its content (versions, transitions, actors, timestamps, justifications, diffs) is audit-derived. It joins this Work's requirement list by a dated amendment when its map plan is cut.)*


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

*(Dated 2026-09-30 by the lead, on the maintainer's entries "2026-09-30 11:52:53 BST — #983's closure sweep: accepted (no §13 verdict owed); DECISIONS on the recurrence and FR-384" and "2026-09-30 11:56:33 BST — DECISIONS: slice order after the split; FR-384 confirmed; FR-383 and FR-385 owners": `06` FR-384 (artifact dependencies / blast radius, route `GET /api/v1/artifacts/{ref}/dependencies`, `06` §5.1; view "Dependencies", `06` §5.3 line 588) was held by no roadmap row (`PL-1237` line 525). It is **owned by this Work**, confirmed by the maintainer, with two conditions: (i) this Work's map plan builds FR-384 — the dependency graph, its route and the view — in its **first slice**, before FR-379's bundle and FR-380's as-at regeneration, which reuse its down traversal; (ii) WK-681 reuses that slice for FR-382 and builds no second traversal. FR-384 joins this Work's requirement list by a dated amendment when its map plan is cut.)*


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


### WK-1251 — Production packaging and supply chain

```yaml
id: WK-1251
family: work
title: Production packaging and supply chain
status: draft
created: 2026-09-29
owner: maintainer
phase: P3
```

Opened `draft` 2026-09-29 on `CR-1247`, and the maintainer's entry "2026-09-29 17:27:28 BST · maintainer (acting on the maintainer's behalf) · ACCEPTANCES: the WK-672 Work close (#906) and plan review 16 (#905), per proposal", §2 row 7: "Accepted: (a). A new **P3** packaging Work (FR-432, FR-433, FR-438 and the three NFRs), opened `draft` on the roadmap by the lead. NFR-526, 527 and 536 are measured under WK-1178. Nothing is built ahead of P3 (CLAUDE.md §0)." **It owns:** FR-432 (container images), FR-433 (the Helm chart and Kubernetes manifests, in P3 by `RL-1232` DP-1 (b)), FR-438 (signed images and an SBOM), and the three NFRs `CR-1247` Proposal 7 names: NFR-530 (RPO and RTO, with a restore exercised in CI), NFR-533 (which follows FR-438) and NFR-461. NFR-526, NFR-527 and NFR-536 are **not** this Work's; they are measured under WK-1178 in P2. **Nothing is built ahead of P3** (`CLAUDE.md` §0). Its activation is the maintainer's. **Minted 2026-09-29** at #916's merge turn, next after WK-1250 (working id 9671).

### WK-1288 — Platform administration views: Settings and System status

```yaml
id: WK-1288
family: work
title: Platform administration views: Settings and System status
status: draft
created: 2026-09-30
owner: maintainer
phase: P3
```

Opened `draft` 2026-09-30 on the maintainer's entry "2026-09-30 07:07:58 BST — SCOPE DECISION: the P3 home for Settings and System status = a NEW P3 Work (option (a))", which completes the entry "2026-09-30 05:35:06 BST — SCOPE DECISION: #949 [FD-1284, cited by its working id in the entry], the `07` §5.3 platform views, option D (split by view)" (FD-1284 option D). **It owns, with each spec change listed first:**

- **`07` §5.3 System status (`/admin/status`).** **Spec changes first:** `07` declares no route that serves the view, and the cache hit rate it shows is not emitted. Then the backend route, then the view.
- **`07` §5.3 Settings (`/admin/settings`).** No spec change is named: the backend is built (`backend/src/app/api/settings.py`, `GET` at :58 and `PUT` at :72). The view only.
- **`07` FR-446** (settings precedence, the effective value and its source inspectable by an Admin), and **FR-443** and **FR-444** (metrics and health, which the System status view surfaces).

It is a P3 roadmap row only: **nothing is built ahead of P3** (`CLAUDE.md` §0), and it is **not a P2 scope addition**. Its map plan comes in P3; its activation is the maintainer's. (Amended 2026-09-30 by the lead, on the maintainer's entries 07:07:58 and 05:35:06. Minted as WK-1288 at #952's merge turn, 2026-09-30, with `python3 scripts/doc-id.py next --ref origin/main` at `df0d4635` printing 1288 (working id 9985 before the mint).)


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

From “Workstreams” (line 499): Alerting lifecycle and routing | FR-334, FR-335, FR-336, FR-337, FR-338, FR-453 (added 2026-09-29, `CR-1247` Proposal 5: both limbs, alert routing and deployment notifications)

**FR-453, both limbs** (`07`: signed webhooks for alert routing and for deployment notifications, with retries, backoff and observable delivery status) *(added 2026-09-29 on `CR-1247`, and the maintainer's entry "2026-09-29 17:27:28 BST · maintainer (acting on the maintainer's behalf) · ACCEPTANCES: the WK-672 Work close (#906) and plan review 16 (#905), per proposal", §2 row 5: "Accepted. OQ-1233 → (b): FR-453 (both limbs) is named on WK-688's row, and the OQ moves to Before Phase 4. FR-272's notification limb is deferred to P4. OQ-1234 (before WK-674 Slice 2) and OQ-1235 (before Slice 3) are ruled by the decision-maker.")*. So `03` FR-272's notification limb is delivered here, in P4, through FR-453's deployment-notification limb. WK-674 delivers FR-272's Audit Event limb in P2 (`RL-1232` DP-4).


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
| **Before Phase 2** — *re-opened 2026-08-22* | ~~OQ-614~~ ✔, ~~OQ-615~~ ✔ *both decided by spike*, ~~OQ-575~~ ✔ *2026-08-17*, ~~OQ-576~~ ✔, ~~OQ-584~~ ✔, ~~OQ-616~~ ✔, ~~OQ-617~~ ✔, ~~OQ-619~~ ✔, ~~OQ-642~~ ✔, ~~OQ-632~~ ✔ *all 2026-08-18*, ~~OQ-571~~ ✔ *2026-08-22 — decided into FR-209 and FR-210; the continuous-effect gate it turns on is WK-690's, which is Phase 2 work*, ~~OQ-597~~ ✔, ~~OQ-598~~ ✔ *both raised 2026-08-22 out of the two modelling decisions taken that day and **both decided the same day**, before the gate they were filed against — the first into FR-86, the second into FR-177 and FR-178. Filing them here rested on a claim that held for one of them: "both have interim behaviour in place, so neither blocks" is true of `diagnostic`, which really is refused, and **false of the interaction**, whose skip-and-record leaves a sparse cross raising `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` out of `compute_gbm_diagnostics` (FR-178). Deciding both early cost one day and turned an interim nobody had exercised into a measured defect with a remedy. WK-690 still owns the slices; what it no longer owns is the choice*, ~~OQ-1185~~ ✔ *raised and decided 2026-09-28 by delegation: the spec's objective grammar is right, and WK-690's first slice fixes the parser (FR-144)*, ~~OQ-1187~~ ✔ *raised 2026-09-28: WK-673's attribution method, decided the same day on the F3 spike's record, exact Shapley with largest-remainder allocation*, **OQ-1222**, **OQ-1223**, **OQ-1224** *raised open 2026-09-28 (WK-672 Slice 3, working ids): the `monotone` grid's GBM thresholds (WK-1178), ordinal inputs (WK-675) and pinned Bandings (WK-1178)* | 18 (3 open) — *recounted 2026-09-29 (`CR-1247` Proposal 5): one id moved to Before Phase 4 and one to Before WK-674 Slice 2. Before that:* 20 (5 open) — *recounted 2026-09-29 (`RL-1232`): two ids raised open. Before that:* 18 (3 open) — *recounted 2026-09-28 (WK-672 Slice 3): three ids raised open. Before that:* 15 (0 open) — *recounted 2026-09-28, for the two ids placed and decided that day.* Earlier, *recounted 2026-08-23: this read `13 (2 open)` while every one of its thirteen ids was struck. The two it meant were decided on the day they were filed here, and the count was written from the intent to file rather than from the row* |
| **Before WK-674 Slice 2** — *added 2026-09-29 (`CR-1247` Proposal 5)* | ~~OQ-1234~~ ✔ *decided 2026-09-30 by `RL-1296` (#935, minted from working id 9901): option (b), a field on the Approval Policy's environment-qualified `deployment` entry, empty by default, used only through an approval request whose predecessor-deployment evidence is its reason (owner WK-674, delivery in Slice 2); raised open 2026-09-29 on the maintainer's answer to `RL-1232` (Q848-2), moved here from Before Phase 2* | 1 (0 open) — *recounted 2026-09-30 (`RL-1296`): decided. Before that:* 1 (1 open) |
| **Before WK-674 Slice 3** — *added 2026-09-29* | ~~OQ-1235~~ ✔ *decided 2026-09-30 by `RL-1311` (#939, minted from working id 9903): option (a), an Environment-setting layer below the process override and above the workspace setting, with a per-key scope and Environment-only keys the process layer never supplies (owner WK-674, delivery in Slice 3); raised open 2026-09-29 on the maintainer's answer QDP-2 to `RL-1232`* | 1 (0 open) — *recounted 2026-09-30 (the ruling of #939): decided. Before that:* 1 (1 open) |
| ~~**Before WK-674 Slice 3 merges**~~ ✔ **all decided** — *added 2026-09-30 (the maintainer's P1 ruling on batch 10)* | ~~**OQ-1334**~~ ✔ *(raised 2026-09-30 in `FD-1333`: should `/score` serve a declared `decimal` output as a JSON string (typed), and may a `decimal` output carry money?) — decided 2026-09-30 by `RL-1343`: (a), a declared `decimal` output is served on every scoring path as an exact decimal string rounded once, and it may carry money; owner WK-1178, delivery immediately after WK-674 Slice 3 merges, no interim (the maintainer's entry "2026-09-30 22:43:26 BST"). Recounted at mint batch 12.* | 1 (0 open) |
| **Before WK-690 Slice 1** — *added 2026-09-29* | ~~OQ-1266~~ ✔ *decided 2026-09-30 by `RL-1289`: `sympy==1.14.0`, cited by `02` §4.6/§4.7 via `uv.lock` (owner WK-690, delivery in Slice 1); raised open 2026-09-29 in `RL-1265`* | 1 (0 open) — *recounted 2026-09-30 (`RL-1289`): decided. Before that:* 1 (1 open) |
| **Before WK-675's map plan** — *added 2026-09-29 (the decision-maker's gate on `OQ-1231`, at the maintainer's instruction of 2026-09-29 19:49:56 BST)* | ~~OQ-1231~~ ✔ *decided 2026-09-29 by `RL-1261`, option (b); raised open 2026-09-29: whether `StepChange.own_change` is derived from step-definition equality instead of `consumed` equality (owner WK-675). Gated before the map plan, not the compare-view slice, because answer (b) adds backend scope to `POST /api/v1/score/compare` and `diff_traces` and so changes WK-675's slice cuts* | 1 (0 open) — *recounted 2026-09-29 (`RL-1261`): decided. Before that:* 1 (1 open) |
| **Before WK-675 S12** — *added 2026-09-30* | **OQ-1285** *raised open 2026-09-30 in PL-1286 (#920): /rating/environments vs /admin/environments (owner WK-675, for the decision-maker)* | 1 (1 open) |
| **Before the P2 exit demo** — *added 2026-09-29* | FD-1244 *(`WF-699` D4 against FR-261)*, FD-1245 *(`WF-699` E2 against FR-257)*: two findings for the decision-maker to rule, placed by `CR-1247` Proposal 12 | 2 (2 open) |
| **Before Phase 3** — *re-opened 2026-08-29* | ~~OQ-633, OQ-634, OQ-635, OQ-636, OQ-637, OQ-638~~ ✔ *2026-08-18*, ~~OQ-540~~ ✔ *decided 2026-08-15 — ADR-710, and it changes what WK-674 builds in Phase 2 rather than waiting for Phase 3*, ~~OQ-581~~ ✔ *evidence in Phase 3 (WK-691), never a block*, ~~OQ-620~~ ✔ *(raised 2026-08-29 from WK-671 Task 1.2; decided 2026-09-28 by delegation, option (b), into `03` FR-1186. It keeps this row for its revisit: whether a Rate Table Version is pinned by more than one Rating Version)*, **OQ-1229** *(raised 2026-09-29 from FD-1227, owner WK-1178: whether NFR-481's fitting determinism must hold across processes or only within one)*, **OQ-1321** *(raised 2026-09-30 in `RL-1322`, owner WK-1178: whether a `lookup` step's output is typed from its reference table's declared column type; `number()` meanwhile)* | 11 (2 open) |
| **Before Phase 4** | ~~OQ-621, OQ-622, OQ-623, OQ-624, OQ-625~~ ✔, ~~OQ-626~~ ✔ *resolved 2026-08-14*, ~~OQ-627, OQ-628, OQ-629, OQ-630, OQ-631~~ ✔, ~~OQ-560~~ ✔ *decided 2026-08-14 — out of scope*, ~~OQ-647~~ ✔ *raised and decided 2026-08-23 out of the scheduling decision: an idempotency key naming a Job that already failed. FR-404's 24-hour window is withdrawn, keys are permanent, and a terminally failed Job releases its key so the period can be attempted again (`07` FR-414). Decided at this gate rather than deferred to it because WK-687 would otherwise build FR-413 against an unanswered question; the code delta stays WK-687's*, ~~OQ-1233~~ ✔ *moved here 2026-09-29 (`CR-1247` Proposal 5): the owner of `07` FR-453's deployment-notification limb, accepted by the maintainer as WK-688 (P4); decided 2026-09-29 by `RL-1252`, which closes it. It keeps this row, because WK-688 delivers it here* | 14 (0 open) — *recounted 2026-09-29 (`RL-1252`): OQ-1233 decided. Before that:* 14 (1 open) — *recounted 2026-09-29 (`CR-1247` Proposal 5): one id moved here. Before that:* 13 (0 open) |
| **Deferred / any time** | ~~OQ-542~~ ✔, ~~OQ-545~~ ✔ *both decided 2026-08-14*, ~~OQ-559~~ ✔, ~~OQ-561~~ ✔, ~~OQ-564~~ ✔ *all decided 2026-08-14*, ~~OQ-574~~ ✔, ~~OQ-578~~ ✔ *amended 2026-08-23 — the decision stands, its two-number evidence clause is withdrawn*, ~~OQ-580~~ ✔ *all decided 2026-08-15*, ~~OQ-601~~ ✔ *raised and decided 2026-08-23 out of that amendment: what evidence stands beside an interaction candidate, once a per-pair exposure share is shown to be `1.0` by construction — its **holdout strength ratio**, the ranker's own statistic recomputed on the holdout partition and published against the in-sample value (`02` FR-168). Deferred no longer as a question; the panel that displays it is still unscheduled*, ~~OQ-585~~ ✔ *2026-08-18 — reopened by its own trigger, the first consumer of an aggregate interval*, ~~OQ-566~~ ✔ *2026-08-19 — a deferral with a trigger (FR-67), raised in WK-661 and never placed here until decided*, ~~OQ-618~~ ✔ *raised 2026-08-19 in the FR-137 slice and placed 2026-08-21*, ~~OQ-641~~ ✔, ~~OQ-643~~ ✔, ~~OQ-645~~ ✔ *all decided 2026-08-23 on the maintainer's instruction to resolve them: no Dagster (FR-413), no workspace quota (FR-415), and a local-only identity provider behind an opt-in profile (FR-398, FR-437). The middle one is a **rejection**, not the deferral its recommendation asked for — that deferral's trigger had been dead since ADR-710*, ~~OQ-646~~ ✔ *decided 2026-08-22 and left unstruck here for a day*, ~~OQ-569~~ ✔ *raised 2026-08-24 in WK-664 — whether a Column Profile's `pii_class` of `NONE` records "classified as not personal" or "never classified", and the same silence on `semantic_type`. Placed here because no phase blocks on it: the default is already live on every ingestion path and the frontend already renders it, so the answer changes what a displayed value **means**, not whether a slice can start. It is on this table on the day it was raised — six questions before it, each reached a decision before reaching a gate row, and the rows above record that as the defect it was*, ~~OQ-654~~ ✔ *raised 2026-08-24 in WK-664 — what `req-coverage.py` should do about three inflation modes that turned out not to be the three that were reported. Here rather than at a phase gate because it bears on every workstream close rather than on any one boundary: its live mode is clause-conflation, which no cheap instrument change reaches, so its legitimate discharge is a standing reporting rule plus a named §13 verdict on each conflated clause* ~~OQ-613~~ ✔ *raised 2026-08-26 out of the FR-141 ruling of that day — a surrogate's source is pinned by UUID while its slug-derived address resolves to the family's latest version; placed here because nothing blocks on it (the pin is exact; rendering and derived addresses are what is at stake)*, **OQ-550** *(re-opened 2026-09-28: its trigger fired, and it is now a WK-675 entry decision, due at WK-675's map plan)*, ~~OQ-551, OQ-552, OQ-553~~ ✔, ~~OQ-567, OQ-568~~ ✔, ~~OQ-570~~ ✔, ~~OQ-609~~ ✔, ~~OQ-649, OQ-650~~ ✔, ~~OQ-651, OQ-653~~ ✔, ~~OQ-655~~ ✔ *all placed 2026-08-26*, ~~OQ-555~~ ✔ *(raised 2026-09-03, RL-1044 §1.7; decided 2026-09-03, RL-1046 D6)*, ~~OQ-1146~~ ✔ *(raised 2026-09-27, RL-1145; decided 2026-09-27, RL-1145 DP-2)*, ~~OQ-554~~ ✔ *(raised 2026-08-27; placed and decided 2026-09-28 by delegation: a review step at each close, FR-1188)* | 35 (1 open) |

**2026-09-30 — a gate row Before WK-674 Slice 3 merges added, and OQ-1334 placed on it.** *Raised in `FD-1333` (a declared `decimal` output is served on `/score` as a float) and mirrored in `docs/open-questions.md` and `03` §10. This row gates Slice 3's MERGE, not its start: `decimal` outputs are out of Slice 3's scope (`RL-1329`), and the question's own trigger is "(d) is the interim if (a) is not ready when Slice 3 merges." (OQ-1334's row, verbatim). Slice 3's dispatch record carries that Slice 3 does not merge until OQ-1334 is ruled (a), or (d) is ruled as the interim. The question is the maintainer's (it changes a served JSON type); this row only places it. The count is recounted from the row's ids: 1 (1 open). The row Before WK-674 Slice 3 keeps its own count, 1 (0 open). (Amended 2026-09-30 by the lead, on the maintainer's P1 ruling on batch 10, option (i); this replaces an earlier placement of OQ-1334 on the row Before WK-674 Slice 3 in the same batch, which would have held Slice 3's start on an out-of-scope question.)*

**2026-09-30 — OQ-1321 placed at Before Phase 3.** *Raised by the decision-maker in `RL-1322` (correcting `RL-1312`), on the maintainer's scope decision "2026-09-30 16:01:23 BST — DECISION (scope): numeric use of reference-table values must remain possible in P2", and mirrored in `docs/open-questions.md` and `03` §10. Its recommendation is option (a), typed lookup outputs, **post-P2**, with `number()` (`RL-1322`) enough for P2 meanwhile, so the answer is needed before Phase 3 builds (a), not before Phase 2's exit; placed here as OQ-1229 was. The question is the decision-maker's to rule; this row only places it. The count is recounted from the row's ids: 11 (2 open). (Amended 2026-09-30 by the lead, on the maintainer's MERGE-ACK #999, which puts OQ-1321's roadmap row in batch 7.)*

**2026-09-30 — OQ-1234 decided, and the row Before WK-674 Slice 2 closed.** *Decided by `RL-1296` (#935, minted from working id 9901), ruled by the decision-maker at high effort on the maintainer's raise: FR-429's promotion-skip permission is a field on the environment-qualified `deployment` entry of `ApprovalPolicyEntry`, empty by default, so the unqualified fallback entry can never grant a blanket skip. It is used only through an approval request, its reason is that request's predecessor-deployment evidence item pinned at submission (`06` FR-356), and it is granted through `set_policy` under `admin:manage_roles`. The ruling adds a dated clause to `07` FR-429 and closes the question in `open-questions.md` and `07` §10, and it leaves `06` §4.2 to WK-674 Slice 2. That the fallback cannot grant a blanket skip rests on a validator Slice 2 writes, and the maintainer's entry of 2026-09-30 carries it into Slice 2's acceptance, shown red on a planted blanket-skip entry and on the fallback path. The count is recounted from the row's ids: 1 (0 open). WK-674 Slice 2's dispatch record cites this change. (Amended 2026-09-30 by the lead, on `RL-1296`.)*
**2026-09-30 — OQ-1235 decided, and the row Before WK-674 Slice 3 closed.** *Decided by `RL-1311` (#939, minted from working id 9903), ruled by the decision-maker at high effort on the maintainer's raise. `07` FR-446's precedence gains an Environment setting between the process environment variable and the workspace setting. Each setting declares a scope (workspace-only by default, workspace-or-Environment, or Environment-only), and a write at a disallowed level is refused. The process environment variable never supplies an Environment-only setting: one present at startup prevents startup naming the key, and one seen at resolve is skipped and logged. `RL-1232` DP-2's FR-270 and FR-271 flags are Environment-only. The ruling adds a dated clause to `07` FR-446 and closes the question in `open-questions.md` and `07` §10. The code, the `SettingSource` member and the contract regeneration are WK-674 Slice 3's, as is the new startup check the separate FR-447 finding (#965, working id 9881) requires. The count is recounted from the row's ids: 1 (0 open). WK-674 Slice 3's dispatch record cites this change. (Amended 2026-09-30 by the lead, on the ruling of #939.)*

**2026-09-30 — OQ-1266 decided, and the row Before WK-690 Slice 1 closed.** *Decided by `RL-1289` (merged by #937), ruled by the decision-maker at medium effort under the maintainer's entry "08:00 CHECKPOINT DECISION": Slice 1 pins `sympy==1.14.0` in `packages/pricing-core/pyproject.toml`, and in that same commit `02` §4.6, §4.7 and §8 cite the `uv.lock` pin. The certification was re-run at the ruling tree and reproduced by the auditor. The count is recounted from the row's ids: 1 (0 open). This meets `PL-1268` Slice 1's second gate. (Amended 2026-09-30 by the lead, on `RL-1289`.)*

**2026-09-30 — a gate row Before WK-675 S12 added, and OQ-1285 placed on it.** *Raised open in `PL-1286` (#920), WK-675's map plan, and mirrored in `docs/open-questions.md` and `03` §10. The maintainer's acceptance of `PL-1286` (entry "2026-09-30 07:03:45 BST — MERGE-ACK #920 and ACCEPTANCE of PL-1286 (WK-675 map plan), with OQ-1285") reads "DP-7 = OQ-1285 (`/rating/environments` against `/admin/environments`), owned by WK-675 for the DM, which gates S12's leaf". The question is the decision-maker's to rule; this row only places it. The count is recounted from the row's ids: 1 (1 open). (Amended 2026-09-30 by the lead, on the maintainer's entry 07:03:45 and PL-1286.)*

**2026-09-29 — a gate row Before WK-690 Slice 1 added, and OQ-1266 placed on it.** *Raised by the decision-maker in `RL-1265`, on the maintainer's recommendation of 2026-09-29 14:19:05 BST. Slice 1 adds `sympy` at one exact pin, so the version must be settled before that slice starts. The count is recounted from the row's ids: 1 (1 open).*

**2026-09-29 — one question moved from Before Phase 2 to Before Phase 4, a second moved to a new gate row Before WK-674 Slice 2, and a gate row Before the P2 exit demo added.** *On `CR-1247`, and the maintainer's entry "2026-09-29 17:27:28 BST · maintainer (acting on the maintainer's behalf) · ACCEPTANCES: the WK-672 Work close (#906) and plan review 16 (#905), per proposal", §2 rows 5 and 12. The deployment-notification owner question, accepted as (b) with FR-453 named on WK-688's row, now sits at Before Phase 4, where its Work is. The promotion-skip question moves to Before WK-674 Slice 2, where it gates that slice's leaf plan: the maintainer's accepted line reads "(before WK-674 Slice 2)" for it. Every count is recounted, not decremented. Closing that question's row, citing its resolver, is the decision-maker's. The promotion-skip and per-environment-configuration questions are the decision-maker's to rule; their rows are not changed. The new row holds two findings, not open questions, so the coverage and recount snippets (which scan only rows naming an `OQ-` id) do not read it. Its count is findings.*

**2026-09-29 — a gate row Before WK-674 Slice 3 added, and OQ-1235 placed on it.** *Raised by the decision-maker in `RL-1232`, on the maintainer's answer QDP-2 (entry `2026-09-29 14:20:41 BST · maintainer (acting on the maintainer's behalf) · QDP-1/2/3 (WK-674 DP mechanisms)`), which names this gate. It sits inside Phase 2 because WK-674 Slice 3 (environment isolation) is the first slice that isolates per-environment configuration (`07` FR-430). The count is recounted from the row's ids: 1 (1 open).*

**2026-09-29 — OQ-1233 and OQ-1234 placed at Before Phase 2.** *Raised by the decision-maker in `RL-1232`, on the maintainer's answers Q848-1 and Q848-2 (entry `2026-09-29 14:15:43 BST · maintainer (acting on the maintainer's behalf) · WK-674 chain: answers to Q856-1/2 and Q848-1/2/3`). Placed here because both change what WK-674, a Phase 2 Work, builds: the first decides whether FR-272's notification is delivered in Phase 2, and the second is where Slice 2's shared promotion-order predicate reads its skip. The count is recounted from the row's ids, not incremented: Before Phase 2 reads 20 (5 open).*

**2026-09-29 — OQ-1229 placed at Before Phase 3.** *Raised from FD-1227 (WK-1178): NFR-481's determinism evidence is within-process only. Placed here because WK-1178 is Phase 2 work and the answer changes what its tests must prove before the Phase 2 exit. The count is recounted from the row's ids, not incremented: Before Phase 3 reads 10 (1 open).*

**2026-09-28 — five gate-table edits from the deputy's decisions by delegation, filed in `RL-1184`.** *OQ-1185 is placed at Before Phase 2 and decided. OQ-1187 is placed there, because WK-673's attribution method is a Phase 2 entry decision. OQ-620 is decided at Before Phase 3 and keeps its row for its revisit. OQ-554 sat on no gate row from its raising on 2026-08-27 (the omission recorded on 2026-09-03 below); it is placed at Deferred and decided. OQ-550 is re-opened at Deferred: the cell showed it struck while its trigger had fired. OQ-1187 was then decided the same day on the F3 spike's record. Every count is recounted, not incremented: Before Phase 2 reads 15 (0 open), Before Phase 3 reads 9 (0 open), and Deferred reads 35 (1 open).*

**2026-09-27 — OQ-1146 placed at Deferred and decided in the same commit.** *Raised by the decision-maker in W37-11's activation, as `CR-1064`:545 requires, and decided there by `RL-1145` DP-2 (option (c): a separately archived `--record-ref`). Placed at Deferred because no phase boundary blocks on it: it governs where the standing docs verify reads the residue-ceiling record, which is W37-11's own mechanism. Written by the lead as a pointer to a decided question, on the deputy's ruling of 2026-09-27 11:28:23 BST (item 3), at 2026-09-27 11:40:09 BST by `date` in the writing command. The count is recounted, 34 (0 open), not incremented.*

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
