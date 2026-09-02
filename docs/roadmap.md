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

*SHA-citation convention, dated 2026-08-25 (W6b decision maker):* slice records cite commits by 7-hex abbreviation. A citation written before this date may name the **pre-squash worktree tip** — a commit that resolves only in the worktree where the slice was built, never in a fresh clone; **34 such citations stood at the time of this note**. Each cited commit was an ancestor of its slice's branch tip, and a squash merge preserves the tip's tree, so the cited change is present in the landed commit unless a later commit on the same branch reverted it. The landed commits, by slice: offset `e36e5d0` (#126), custom metrics `8cac13f` (#122), profile `667c8fe` (#113), top levels `9c30182` (#115), EBM `c2c54a6` (#129), W32-8 `946725f` (#157), W32-7 `60f6e46` (#164), the W32 closure record `c024f3e` (#161). Alembic revision ids (`9e4c7b21fa08`, `c9d0e1f2a3b4`, `a1b2c3d4e5f6`, `d0e1f2a3b4c5`, `c3d4e5f6a7b8`, `e1f2a3b4c5d6`, `82edffbe1dce`) are migration ids under `backend/migrations/versions/`, not git objects — they resolve in the migration history, not in git; a UUID fragment (`01a018f2`) is a test-assertion value. The class is enumerable: sweep this document for 7-40-hex tokens and test each with `git merge-base --is-ancestor` against `origin/main`.

Plan-ledger SHA-citation convention, dated 2026-08-26 (W6b decision maker): the 2026-08-25 note rules the roadmap; docs/plans/ ledgers predate it and are frozen, so the same rule extends to them. A ledger may cite a pre-squash worktree SHA — it resolves in the object store with its subject verbatim but fails an ancestry check against main; verify by subject, never by merge-base. The sweep of 2026-08-26 measured 162 non-matching facts across all shipped plans, the dominant class exactly this. A failed ancestry check is expected, never a defect.

---

## 2. Where the project is

| | |
|---|---|
| **Phase 0 (Specification)** | Closed 2026-08-14 — 8 specs, 5 workflows, 5 ADRs, 31 contracts; `scripts/audit-docs.py` prints the current requirement count, which changes whenever an implementation proves the spec wrong |
| **Blocking Phase 1** | **Nothing.** All seven of Track C's decisions are taken — the last six (OQ-MODEL-1, 2, 4, 5, 6, 7) on 2026-08-15. What remains open gates Phase 2 or later (§10) |
| **Code written** | Phase 1a complete, Phase 1b started — the closure records in [`docs/audit/closure-records.md`](audit/closure-records.md) are the authority, not this row |

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
| 1 | Custom objectives end to end | **Partly closed.** SymPy derivation ✔ (F2) and XGBoost `base_margin` ✔ (F5) verified empirically; the certification design was found *wrong* and rewritten (F3 → FR-MODEL-68..70). Two fragments re-homed ↓ |
| 2 | ZEN Engine decimal semantics | **Closed** ✔ — `rust_decimal`, ADR-0004 confirmed, OQ-RATE-1 decided (F1) |
| 3 | glum standard errors | **Closed** ✔ — `std_errors()`/`covariance_matrix()` confirmed to exist (F8) |
| 4 | Polars at 10 M+ rows | **Partly closed.** Streaming-engine status and an open group-by memory regression found (F10), validating ADR-0005's split. Benchmark re-homed ↓ |
| 5 | Pydantic v2 → JSON Schema | **Closed** ✔ — discriminated unions confirmed, and a `Decimal` gap found that would let a lossy payload satisfy the contract (F6/F7) |
| 6 | Vue Flow custom nodes | **Documentation only.** `isValidConnection`, node memoisation, Web Workers (F12). Re-homed ↓ |
| 7 | Low-latency Python serving | **Documentation only**, but actionable: Pydantic costs ~1 ms of the 50 ms budget → NFR-RATE-13 (F11). Re-homed ↓ |

#### Re-homed, not dropped

| Fragment | New home | Why there |
|---|---|---|
| Restricted AST parser for the expression grammar | ~~**Phase 1, W5**~~ **Split, corrected 2026-08-22: the parser landed in Phase 1 W4; `02` §4.6's grammar is Phase 2 W30** | Both halves of the original sentence turned out to be about different things, which is why this row could sit here contradicting §7 for a week. **The parser**: `pricing_core.data.expressions` was built for `01` FR-DATA-10 in **W4**, and translates to Polars rather than sandboxing `eval` — the risk this fragment was really about, discharged early and by another workstream. **The grammar this row names**: `02` §4.6 is `expression` custom objectives, sent to **Phase 2, W30** by OQ-MODEL-1 on 2026-08-15 — the same §4.6 that W30's own row in §7 lists as carried over, so `roadmap.md` handed one spec section to two different phases. FR-MODEL-40 and FR-MODEL-6 are unevidenced today and owned by W30 by recorded verdict, so W5 never owed this row anything. It was stale from the day OQ-MODEL-1 was decided, and is struck rather than deleted because an on-ramp fragment that was re-homed twice is the record of how the estimate moved. *Believed on the day:* nothing left to research|
| LightGBM `init_score` symmetry | ~~Spike S3~~ **run 2026-08-14** | Symmetric at fit, **asymmetric at scoring** — `predict()` has no offset parameter. Now FR-MODEL-72 (F13) |
| Polars 10 M-row benchmark | **Phase 1, W4 acceptance** | It is NFR-DATA-1/3, measured against real data — an acceptance test, not reading |
| Vue Flow depth | **Phase 2 on-ramp, W15** | Does not block Phase 1; belongs with the DAG designer it serves |
| Low-latency measurement | **Spike S2** / Phase 2 W11 | Already partly discharged into NFR-RATE-13; the rest is measurement |

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
| ~~**S1**~~ ✔ **CLOSED 2026-08-14** | FR-RATE-56/57/59 | Engine arithmetic is exact — but the **Python binding has no decimal type**, so F1's "workaround not required" was wrong. Money now crosses as integer minor units. Also found: `log`/`sqrt` don't exist in ZEN (the old requirement guarded nothing), while **division by zero returns `null` silently**. |
| ~~**S2 — `exact`-mode GBM latency**~~ ✔ **CLOSED 2026-08-14** | OQ-RATE-2 | **Comfortably viable** — p99 1.09 ms, ~2 % of the 50 ms budget. OQ-MODEL-3 stays a real design choice rather than being forced. `nthread=1` per request (NFR-RATE-14). *(W8 re-measured 2026-08-27: p99 1.626 ms — see NFR-RATE-14/OQ-RATE-2.)* |
| ~~**S3 — LightGBM `init_score`**~~ ✔ **CLOSED 2026-08-14** | FR-MODEL-72 | The assumption was **half wrong**: symmetric at fit time, but `Booster.predict()` has no offset parameter at all, so a scoring path ported from XGBoost silently omits the offset entirely. Fixed as FR-MODEL-72 (F13). |

**All three spikes are now closed.** Every one changed the specification; none confirmed
its assumption unchanged — which is the argument for having run them rather than reasoned
about them.

### Track C — The decision backlog, sequenced

**All four Phase 1a gates were decided on 2026-08-14** — Apache-2.0, Celery, fit-time
large-loss treatment, and full-snapshot ingestion. **The three 1b gates are now decided too** —
OQ-OVR-5 on 2026-08-14, OQ-MODEL-1 and OQ-MODEL-5 on 2026-08-15. Nothing in this
table blocks work:

| Question | Gates | Why it blocks |
|---|---|---|
| **OQ-PLAT-1** Celery vs a transactional Postgres queue | **1a** ✔ *decided* | Job submission is in the first sprint, and transactional enqueue interacts directly with the audit rule (`06` R2) |
| **OQ-DATA-1** large-loss capping: dataset or model? | **1a** ✔ *decided* | It *is* the 1a/1b boundary — deferring it makes it a contract change rather than a decision |
| **OQ-DATA-2** append ingestion vs full snapshots | **1a** ✔ *decided* | W4, and only if the first real dataset is large enough that full snapshots hurt |
| **OQ-OVR-2** project licence | **1a** ✔ *decided* | Blocks nothing technically; blocks every external contribution and the public-repo story |
| **OQ-MODEL-1** expression objectives in 1b? | **1b** ✔ *decided 2026-08-15* | Templates only in Phase 1; expressions in Phase 2 (FR-MODEL-75/76). The AST parser turned out to be built already — W4 needed it for `01` FR-DATA-10 — so what left W5 is the SymPy derivation and the gradient/hessian compilation target |
| **OQ-MODEL-5** credibility standard | **1b** ✔ *decided 2026-08-15* | Both, limited fluctuation as the default, recorded per grouping (FR-MODEL-80) — so W5 builds two methods rather than choosing one. **Both are built as of 2026-08-22**: limited fluctuation shipped 2026-08-15, Bühlmann–Straub in the audit-remediation slice, which found it had been refused at runtime for a week with the refusal test marked FR-MODEL-14 rather than FR-MODEL-80 — so `scope-audit.py` credited the wrong requirement and the gap read as covered |
| **OQ-OVR-5** notebook escape hatch | **1b** ✔ *decided 2026-08-14* | Client library in Phase 1; embedded notebooks revisited in Phase 4 |

The four marked **1a** are the ones that actually gate the start of work. The other 39
can wait for the phase that needs them (§10).

---

### Outstanding work — consolidated

Everything still open before Phase 1a can start, in one place. Tracks A–C above explain
*why*; this is the list. The **Gates** column shows which half of Phase 1 each blocks.

| # | Task | Kind | Owner | Blocks |
|---|---|---|---|---|
| ~~1~~ | ~~**OQ-OVR-2**~~ ✔ — project licence | decision | maintainer | **1a** — public contribution, not code |
| ~~2~~ | ~~**OQ-OVR-5**~~ ✔ — notebook escape hatch | decision | maintainer | **1b** — decided 2026-08-14: client library |
| ~~3~~ | ~~**OQ-PLAT-1**~~ ✔ — Celery vs a transactional Postgres queue | decision | maintainer | **1a** — W2, first sprint |
| ~~4~~ | ~~**OQ-DATA-1**~~ ✔ — where large-loss capping lives | decision | maintainer | **1a** — it *is* the 1a/1b boundary; a contract change if deferred |
| ~~5~~ | ~~**OQ-DATA-2**~~ ✔ — append ingestion vs full snapshots | decision | maintainer | **1a** — W4, only if the first dataset is large |
| ~~6~~ | ~~**OQ-MODEL-1**~~ ✔ — do expression objectives ship in Phase 1b? | decision | maintainer | **1b** — decided 2026-08-15: templates only, expressions in Phase 2 |
| ~~7~~ | ~~**OQ-MODEL-5**~~ ✔ — credibility standard | decision | maintainer | **1b** — decided 2026-08-15: both, limited fluctuation by default |
| ~~8~~ | ~~**S3** — LightGBM `init_score`~~ ✔ **done** | spike | — | Closed. Found a real asymmetry → FR-MODEL-72 |
| ~~9~~ | ~~**Phase 1 split** — accept or reject 1a/1b~~ ✔ **ACCEPTED 2026-08-14** | decision | maintainer | Now the plan; `CLAUDE.md` §9 updated |

**Not blocking Phase 1, but do not lose them:**

| Task | Kind | Due |
|---|---|---|
| ~~**1 Phase-2 decision (OQ-GOV-8)**~~ ✔ **none left** | decisions | Before Phase 2. Was five: OQ-RATE-2 decided by spike, OQ-MODEL-3 on 2026-08-17, and OQ-MODEL-11, OQ-MODEL-12, OQ-RATE-3, OQ-RATE-4, OQ-RATE-6 and OQ-PLAT-3 all on 2026-08-18. **OQ-GOV-8 is correctly the last one standing** rather than the one nobody got to: it asks whether an `expression` Custom Objective needs an authoring permission distinct from `model:fit`, and `expression` objectives are themselves Phase 2 — deciding it against the template catalogue would be deciding it against the wrong artifact. **Deferred 2026-08-18 with a trigger rather than left open**: `06` FR-GOV-38 makes answering it a precondition of lifting `expression_objectives_enabled`, so W30 cannot ship the capability without closing it |
| Sustained-load test at 200 rps (S2 measured per-request only) | test | Phase 2 W11 |
| ~~6 Phase-3~~ ✔ *all decided 2026-08-18* · 11 Phase-4 · 5 any-time decisions still open | decisions | Per gate (§10) — OQ-MODEL-2, 4, 6, 7 and OQ-OVR-1 and 6 all came off this list on 2026-08-15 |
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

### Phase 1a — Data Workbench

**Goal:** ingestion, preparation, the four-layer validation gate, profiling, reference data
— everything up to a dataset that is fit to model on.

**Demo-able outcome:** an actuary loads freMTPL2, watches validation **fail on a real
problem**, fixes the preparation recipe, acknowledges a warning with a justification, and
drives the version to `validated` — with the report and profile visible. This is
`wf-01` phases A–B end to end.

> **The loop itself passes as of W4's close (2026-08-15)**, in
> `backend/tests/test_data_jobs.py::test_the_failure_loop_then_validated`: a file with a
> negative exposure is ingested, validation fails on it, promotion is refused, the *data*
> is fixed rather than the verdict, and the new version reaches `validated` — after which
> `fittable_or_refuse` opens for it and still refuses the first. What Phase 1a still owes
> the demo is the screen (W6a) and freMTPL2 itself (W7); the machinery under both is done.

| # | Workstream | Depends on | Notes |
|---|---|---|---|
| ~~**W1**~~ ✔ | Repo foundations: `uv` workspace, `model-schema`, `pricing-core` skeleton, CI with import-linter contract (ADR-0001), docker compose | — | **Closed 2026-08-14** — see the status table below |
| ~~**W2**~~ ✔ | Platform core: jobs, blobs, settings, OIDC auth, health, tracing | W1 | **Closed 2026-08-14** — ~35 of 61 `PLAT` requirements |
| ~~**W3**~~ ✔ | Governance write path: audit log + hash chain, RBAC enforcement, approval state machine | W1, W2 | **Closed 2026-08-14** — §5 skeleton only, no governance UI |
| ~~**W4**~~ ✔ | Data: sources, ingestion, preparation recipes, parquet, profiling, the four validation layers + built-in rule catalogue, reference tables | W2, W3 | **Closed 2026-08-15** — 48 of **50** `DATA` requirements (the row's "49" predates FR-DATA-40), 28/28 endpoints, 38/38 catalogue rules |
| ~~**W6a**~~ ✔ | Frontend: app shell, dataset views, **validation report view** | W4 ✔ | **Closed 2026-08-15** — all **7** of `01` §5.3's views, 75 frontend tests |
| ~~**W7b**~~ ✔ | **The demo entrance** and its derived guide | W6a ✔, W7a ✔ | **Closed 2026-08-15** — FR-PLAT-53/54. Split from W7 for the same reason W7a was: the entrance needs no modelling, and Phase 1a's exit demo needs the entrance |

#### Phase 1a status

| WS | Scope | Status |
|---|---|---|
| **W1** | Repo foundations | ✔ **closed 2026-08-14** |
| ~~**W2**~~ ✔ | Platform core — jobs, blobs, settings, auth, health, tracing | ✔ **closed 2026-08-14** — see [`docs/audit/closure-records.md`](audit/closure-records.md) |
| ~~**W3**~~ ✔ | Governance write path — audit log, RBAC, approval state machine | ✔ **closed 2026-08-14** — see [`docs/audit/closure-records.md`](audit/closure-records.md) |
| ~~**W4**~~ ✔ | Data — ingestion, preparation, validation, profiling, reference data | ✔ **closed 2026-08-15** — see [`docs/audit/closure-records.md`](audit/closure-records.md) |
| ~~**W7a**~~ ✔ | freMTPL2 data seed — the demo dataset through the real Job path | ✔ **closed 2026-08-15** — see [`docs/audit/closure-records.md`](audit/closure-records.md) |
| ~~**W6a**~~ ✔ | Frontend — app shell, dataset views, validation report view | ✔ **closed 2026-08-15** — see [`docs/audit/closure-records.md`](audit/closure-records.md) |
| ~~**W7b**~~ ✔ | Demo entrance — one command to a browser, with a derived guide | ✔ **closed 2026-08-15** — see [`docs/audit/closure-records.md`](audit/closure-records.md) |
| ~~**Exit demo**~~ ✔ | Phase 1a's exit criterion exercised through `/demo` | ✔ **accepted 2026-08-15** — one command to a served page in 27 s, the failure loop on real data, two defects found. Exercised over HTTP by Claude; the maintainer accepted without driving it, deferring hands-on testing until more functionality exists |
| ~~**Exit gate**~~ ✔ | FR-DATA-41 (ingestion refuses a `direct_identifier` column) · FR-DATA-42 (append-only triggers on `validation_reports`, `profiles`, `validation_acknowledgements`) | ✔ **delivered 2026-08-15** — five injections, five caught. `blobs` left the list when building it proved it could not be append-only; the requirement was corrected rather than the table dropped |

#### Phase 1b status

| WS | Scope | Status |
|---|---|---|
| **W5** | Modelling workbench — model detail, comparison, diagnostics, transparency, objective library, perils, factors | ✔ **closed 2026-08-22** — see [`docs/audit/closure-records.md`](audit/closure-records.md) |
| **W6b** | Modelling-workbench UI — dataset list, rule set editor, model spec builder, browser auth, workspace selector, lineage, rating-version demo seam | ✔ **closed 2026-08-27** — see [`docs/audit/closure-records.md`](audit/closure-records.md) |
| ~~**W7**~~ ✔ | freMTPL2 demo seed — **the modelling half** | ✔ **closed 2026-08-27** — see [`docs/audit/closure-records.md`](audit/closure-records.md) |
| ~~**Exit demo**~~ ✔ | Phase 1b's exit criterion — the core `wf-01` journey (dataset → factors → GLM + GBM fits → comparison → approval → rating version) — exercised over HTTP; bandings, Peril Structure and reconciliation are recorded as Phase 2 | ✔ **accepted 2026-08-27** — scripted HTTP run of the journey with the postconditions verified in **90 s** (NFR-PLAT-4: < 300 s); one approved model, approved rating version `model:fremtpl2-glm-04da49@1`, comparison artifact present. See [`docs/audit/exit-demo-uat.md`](audit/exit-demo-uat.md); the UI is available for hands-on driving |
| ~~**Phase 1b**~~ ✔ | Modelling Workbench — `wf-01` end to end on freMTPL2 | ✔ **closed 2026-08-27** — exit criterion (the core `wf-01` journey over HTTP) met and the demo UAT signed off. See [`docs/audit/phases/1b/README.md`](audit/phases/1b/README.md) and [`docs/audit/phases/1b/register.md`](audit/phases/1b/register.md) |

Closing a workstream follows `CLAUDE.md` §13 and the `close-workstream` skill: every
deliverable re-verified against its row above, the gate run locally, each new check proven
to fail on broken input, NFRs measured against their budget, and what was *not* delivered
stated explicitly. A closure record without those is an assertion, not evidence.

**And a plan review runs at the same moment** (`CLAUDE.md` §14, from `NT-0001` accepted
2026-08-15). §13 asks whether a workstream did what it said; §14 asks whether the plan still
says the right thing — omission, skills drift, document drift, and whether the remaining
phases are cut in the right place. It runs at **each workstream close and again before a
phase's exit demo**, and its output is a proposal on this page, never an edit made on its own
authority.

~~Two~~ **Three** runs so far: [review 1](#plan-review-1--at-w6as-close-2026-08-15) at
W6a's close, [review 2](#plan-review-2--at-w7bs-close-and-before-phase-1as-exit-demo-2026-08-15)
at W7b's close and before the exit demo, and
[review 3](#plan-review-3--at-w5s-close-2026-08-22) at W5's close. Each proposal carries its
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

The closure records, plan reviews and the retrofit-impossible list moved to [`docs/audit/`](audit/) on 2026-08-27 (NT-0009). This page is the forward-looking plan; the archive is at [`docs/audit/README.md`](audit/README.md).

### Phase 1b — Modelling Workbench

**Goal:** factors, bandings, groupings, GLM and GBM fitting, diagnostics, transparency
artifacts, model versioning.

**Demo-able outcome:** the actuary bands and groups factors, fits a GLM and an XGBoost
model, compares them, and gets one approved — **`wf-01` end to end**.

| # | Workstream | Depends on | Notes |
|---|---|---|---|
| ~~**W5**~~ ✔ | Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective **templates only** | W4 (1a) | **Closed 2026-08-22** — 110 built · 10 declared-and-refused-by-name · 16 unevidenced with a verdict, of 136; 41/41 endpoints. See [`docs/audit/closure-records.md`](audit/closure-records.md). Every `MODEL` requirement — the largest single workstream in the project; `scope-audit.py MODEL` counts them, and per plan review 3's question 5 (accepted 2026-08-22) that is now the only place a reader should take a count from. **Started 2026-08-15**: ~~twenty-two~~ **twenty-eight** slices in — the GLM spine, bandings and groupings, the factor workbench, diagnostics, spec validation, the model lifecycle, model comparison, `wf-01`'s citation audit, gradient boosting with its transparency artifact, `wf-01` driven end to end, peril structures with their reconciliation, interaction factors, backtests, prediction, custom objectives, FR-DATA-47's artifact triggers, the profile contract, `top_levels`' exposure per level, the exact-decimal refusal of a float, paired quantile models, the GLM approximation as a Model (FR-MODEL-96, FR-MODEL-102 — measured at +0.26 s / ~7 % against a **single-factor** fixture; type-III diagnostics refit the surrogate once per factor, so this does not bound a multi-factor model, and `type_iii=False` is the lever if that ever bites, not pulled without the maintainer), and **custom metrics** (FR-MODEL-45/103/105/106/107/108 — a Custom Metric reaches `approved` on the same lifecycle and grammar as a Custom Objective, `GbmSpec.eval_metrics` is now honoured rather than merely declared, and MODEL's endpoint axis closed at **40 of 40**, the first module in this repository to publish every declared endpoint), **regularisation and cross-validation** (FR-MODEL-20/53), **Tweedie power by profile likelihood** (FR-MODEL-22), **offset from another model** (FR-MODEL-24), **EBM via interpret-core** (FR-MODEL-37) and **GBM declared weights with the dropped eval metric record** (FR-MODEL-19/111), and **the audit-remediation slice** (2026-08-22, this one); see the slice records in [`docs/audit/closure-records.md`](audit/closure-records.md). *(The count said eighteen and omitted the exact-decimal slice, which had already landed as PR #116; corrected 2026-08-19 by the paired-quantile slice.)* *(It went stale the same way again and is corrected 2026-08-22 by the audit-remediation slice: five slices — regularisation/CV (#124), Tweedie (#125), offset (#126), EBM (#129) and GBM weights (#130) — landed between 08-21 and 08-22 with the count left at twenty-two, while this file's own newest record already called itself "the twenty-seventh slice". Both stale values are kept. **The mechanism is the same both times and is worth naming rather than re-fixing:** a slice's PR strikes its row in the outstanding-work table and stops there, and this count is a second place nothing reconciles against that table — #116 did it, then #124 and #125 did it again. The same mechanism left the buildable-slice counter at one when every row beneath it was struck, and left six verdicts stale in the diagnostics slice's table. **A slice updates the row that describes itself; every other place that counts slices is unowned.** The count is of **numbered** slices, so the three decision-only records of 2026-08-18 (PRs #106, #107, #108) have records and no number and have never been in it.)* **The prediction slice (PR #102, 2026-08-18) landed without a slice record** — the omission is recorded here rather than reconstructed from the diff; what it found is in `02`'s dated notes — FR-MODEL-93, OQ-MODEL-13 and OQ-MODEL-14, plus the `inverse`-link resolution at §3.4 — and in `.claude/skills/python-test`. **Scope set by the 2026-08-15 decisions:** templates only, with the certification machinery built here (FR-MODEL-75/76); both credibility methods, not one (FR-MODEL-80); SHAP interaction *suggestions* (FR-MODEL-79); the complexity diagnostic and its optional gate (FR-MODEL-81); paired quantile models as the only GBM interval (FR-MODEL-77/78). **W5 also finishes `wf-01`, and has**: the citation audit and the journey test landed 2026-08-17, and on 2026-08-18 the peril-structure and interaction slices drove the last three pinned steps, so FR-OVR-17(ii) for `wf-01` is **delivered** — the first of the five journeys. **The closure slice (2026-08-22) is the last, and the count above is deliberately not incremented to twenty-nine**: plan review 3's question 5 was accepted the same day, and adding a fourth hand-written count to the file whose staleness prompted the proposal would be the clearest possible way to ignore it. The slice records in [`docs/audit/closure-records.md`](audit/closure-records.md) are the list; `scope-audit.py` is the count |
| ~~**W6b**~~ ✔ | Frontend: **factor workbench**, model detail, diagnostics — **and the frontend platform**: browser authentication, accessibility beyond semantics, the workspace selector's **shell control only**, and the audit's two enforcement gaps — **FR-DATA-41** and **FR-DATA-42** | W5, W6a ✔, OQ-PLAT-6 ✔ | **Closed 2026-08-27** — see [`docs/audit/closure-records.md`](audit/closure-records.md). `02` §5.3's interaction requirement — an edit's consequence visible before saving. The platform half was added by plan review 1 (accepted 2026-08-15): **FR-PLAT-55** (authorization code + PKCE — until it ships, only the dev proxy reaches the API from a browser), **NFR-OVR-10**'s tabular fallback for charts, and a workspace selector, which `07` §3.1 needs the moment a principal belongs to more than one. **Corrected 2026-08-23 (W6b slice-map backlog item 2): that clause read as a citation and was a forecast — §3.1 had never contained the requirement.** It does now, as FR-PLAT-62 (a Workspace becomes a named entity; there was no `workspaces` table, so a selector had nothing to render) and FR-PLAT-63 (the selection, verified against membership). **Both are W32's, not W6b's** — a table, a migration and an API — and the transport is OQ-PLAT-9. W6b keeps the shell control and stays blocked until the backend half lands. |
| ~~**W32**~~ ✔ | Everything in Phase 1b that is not a browser — the contract guards, `model-schema` shapes, a migration, backend defects, endpoint tests and one skill | W5 | **Added 2026-08-24** (`plans/2026-08-23-w32-closure-proposal.md` Part B1, accepted by the maintainer that day). **Split from W6b 2026-08-22** and accepted the same day (`plans/2026-08-22-w6b-slice-map.md` §1, acceptance table row 1) — but the split created a workstream name without creating a row, so for two days work merged under a name this plan did not contain, and the coverage figure under Phase 1b described a scope that excluded it. **Eleven slices**, W32-1 … W32-11 — ten as scoped on 2026-08-22, plus **W32-11** allocated 2026-08-24 by the closure proposal's Part C decisions, which W32's close waits on. **W32-11 is the terminal slice**, picked up 2026-08-24 by the closure-execution session and confirmed by the maintainer the same day; findings it cannot resolve are booked forward with an owner rather than held against the close — see the decision record in [`docs/audit/closure-records.md`](audit/closure-records.md); **W6b-1 and W6b-5 depend on W32-1, W6b-13 on W32-2, and W6b-3 on W32-3** — all three merged, so **those four W6b slices** wait on nothing but this workstream's close. **`W6b-11` is not among them and does wait on unbuilt W32 code**: FR-PLAT-62 and FR-PLAT-63 are **W32-7's**, and W32-7 is unstarted — there is no `workspaces` table (only `workspace_members` and `workspace_settings`), `record_switch` appears nowhere in `backend`, `packages` or `frontend`, no migration mentions a workspace, and `deps.py`'s `_single_workspace` still refuses a multi-membership caller outright. *(Corrected 2026-08-24: this clause read "W6b-1, -3, -5 and -13 are blocked on it", and two W6b sessions reached opposite readings of "it" — W32-11, the nearest noun, versus W32, the row's subject. Arbitrated against `plans/2026-08-22-w6b-slice-map.md` §5's slice table: those four are **exactly** the W6b rows whose dep column names a W32 slice, the other nine naming a W6b row or nothing. A dependency discovered after 2026-08-22 would have no reason to fall on precisely that pre-existing subset, so the clause compressed the column rather than recording something new. The frozen map needs no amendment.)* *(Corrected again 2026-08-24, hours later — the clause above was itself correction text, and the correction introduced this defect. It ended "all three merged, **so no W6b slice waits on unbuilt W32 code**; what they wait on is this workstream's close." The compression to the frozen dependency column is sound and is left standing; the trailing clause **generalised from the four slices that column names to all thirteen**, and that universal is false. `W6b-11`'s dependency on W32 was created **2026-08-23** by FR-PLAT-62/63 — *after* `plans/2026-08-22-w6b-slice-map.md` §5's table was frozen — so it is invisible in the very column the compression is derived from, and the **W6b row immediately above already said the opposite**: "W6b keeps the shell control and stays blocked until the backend half lands." Two consecutive rows of one table asserted contradictory things for as long as the clause stood. Found by `w6b-decision-maker`, routed via `w6b-lead`, verified here against five independent sources, one of them the code. **The mechanism is that a frozen dependency column ages into a false "ready"**: every dep it names merges, the row reads unblocked, and a dependency discovered later is nowhere in it to say otherwise. **A claim derived from a frozen column describes the column, never the world** — the compression was legitimate up to the em-dash and became a forecast after it. **The clause is in fact refutable on its own text, with the W6b row unread**: the justification licensing it — "a dependency discovered after 2026-08-22 would have no reason to fall on precisely that pre-existing subset" — is exactly the assertion that **the subset is not the population**. The premise that makes the narrow claim sound is the one that refutes the broad one. Diagnosed against the neighbouring row you fix a sentence; diagnosed against the quantifier you fix the class, which is why it is written this way round. Cost had it stood: a W6b session builds a workspace selector against a table that does not exist.)* *(Corrected 2026-08-24 at `60f6e46`, the last feature SHA. The closing commit is `e2ae7c6` (#165): **the `W6b-11` clause above is now false in every particular, and is left standing because it was true when written.** W32-7 merged (#164) and ships the `workspaces` table, its migration, `record_switch` in `platform/workspace_switch.py`, and a `deps.py` that resolves a verified `Workspace-Id` header instead of refusing a multi-membership caller outright. **`W6b-11` no longer waits on unbuilt W32 code**; what it waits on is this workstream's close, recorded above. **One residual remains and it is not a build dependency**: FR-PLAT-63's fourth obligation — a switch audited into both chains — is delivered as a mechanism and tested, and **unenforced on the request path**, because `require_caller` runs once per request and cannot observe that a selection *changed*. Deferred with an owner, **owner W6b-11**, tracked as **`OQ-PLAT-12`**. A W6b session building the selector will find the table and the header; it will not find a request-path trigger, and it owns writing one. **And `plans/2026-08-22-w6b-slice-map.md` is frozen at its date and was not corrected by this close** — `CLAUDE.md` §2 freezes a filed plan, and editing one destroys the record of what was believed at its date while reading as though it had always been right. Its **line 192** still tells `W6b-11` it waits only on W32 building the header half, which was accurate when written and now misleads the one session it gates. **This clause is the live correction; that map is not current.**)* Slice records are in [`docs/audit/closure-records.md`](audit/closure-records.md) — W32-1 … W32-5 back-filled 2026-08-24, which is the same omission in its second form, and the workstream's closure record is in [`docs/audit/closure-records.md`](audit/closure-records.md) |
| ~~**W7**~~ ✔ | freMTPL2 demo seed — **the modelling half** | W5, W6b | **Closed 2026-08-27** — see [`docs/audit/closure-records.md`](audit/closure-records.md): a fitted GLM, a rating version, and `wf-01` end to end. The data half closed as **W7a**, the entrance and its guide as **W7b** (FR-PLAT-53/54, `NT-0002`) — both in Phase 1a, because neither needed modelling and Phase 1a's exit demo needed both |

**Coverage:** ≈ 78 of 375 module requirements (~21 %).

**Exit:** the core [`wf-01`](workflows/wf-01-dataset-to-model.md) journey on freMTPL2 —
dataset → factors → GLM + GBM fits → comparison → approval → rating version — exercised
over HTTP. Bandings, Peril Structure and reconciliation are recorded as Phase 2 (plan
review 6, accepted 2026-08-27).

W5's *frontend* work (W6b) can start as soon as the `02` contracts are frozen, which is the
main parallelisation opportunity inside 1b.

> **2026-08-23 — the W6b slice map's specification backlog is resolved.** Its §4 listed
> eleven items, each blocking a W6b or W32 slice from starting, and the plan is frozen at
> its date so the resolutions live in the specs rather than in it. Four were **spec gaps**
> and are now requirements: `07` FR-PLAT-58 (a local OIDC provider behind an opt-in compose
> profile), FR-PLAT-62 and FR-PLAT-63 (a Workspace becomes a named entity; the selection is
> verified against membership), `01` FR-DATA-54 (a threshold edit authors a new rule
> version) and `02` FR-MODEL-127 (the three artifact libraries are listable). Four were
> **the spec being wrong** and are corrected on the spec's side: `02` §5.3's three stale
> routes and its two-state certificate cell, `01` §4.4's "thresholds are Rule Set
> configuration, not code", and FR-MODEL-79's promise of an exposure share that is `1.0` by
> construction and a holdout lift defined nowhere. Two were **shapes that escaped the
> contract**: `01` §4.9 now types the lineage response, and `02` §5.3 registers the two
> views W32 built without rows. Three new questions came out of the work rather than being
> answered inside it — OQ-MODEL-31, OQ-PLAT-8 and OQ-PLAT-9 — and each is on a gate row.
> **What is not resolved here is the code**: every item names an owning workstream, and
> `W6b-11` stays blocked until OQ-PLAT-9 is decided. *(Amended 2026-08-23: all three were decided that
> same day — FR-MODEL-128, FR-PLAT-64 and FR-PLAT-65. `W6b-11` is no longer blocked on a decision and
> now waits only on W32 building the header half.)*

### Original scope, for reference

**Goal (`CLAUDE.md` §9, now superseded by the split above):** dataset upload + validation + profiling, GLM and XGBoost fitting
(incl. custom objectives), factor management, diagnostics, model versioning. Demo on
freMTPL2.

**Demo-able outcome:** an actuary loads freMTPL2, watches validation fail on a real
problem, fixes it, acknowledges a warning, bands and groups factors, fits a GLM and an
XGBoost model, compares them, and gets one approved — i.e. **`wf-01` executed end to end**.

### Workstreams

| # | Workstream | Depends on | Notes |
|---|---|---|---|
| ~~**W1**~~ ✔ | Repo foundations: `uv` workspace, `model-schema`, `pricing-core` skeleton, CI with import-linter contract (ADR-0001), docker compose | — | **Closed 2026-08-14** — see the status table below |
| ~~**W2**~~ ✔ | Platform core: jobs, blobs, settings, OIDC auth, health, tracing | W1 | **Closed 2026-08-14** — ~35 of 61 `PLAT` requirements |
| ~~**W3**~~ ✔ | Governance write path: audit log + hash chain, RBAC enforcement, approval state machine | W1, W2 | **Closed 2026-08-14** — §5 skeleton only, no governance UI |
| ~~**W4**~~ ✔ | Data: sources, ingestion, preparation recipes, parquet, profiling, the four validation layers + built-in rule catalogue, reference tables | W2, W3 | **Closed 2026-08-15** — 48 of **50** `DATA` requirements (the row's "49" predates FR-DATA-40), 28/28 endpoints, 38/38 catalogue rules |
| ~~**W5**~~ ✔ | Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective templates | W4 | **Closed 2026-08-22** — 136 in scope at close, of which 110 built. All ~~**124**~~ `MODEL` requirements — the largest single workstream. *(Re-derived 2026-08-22 with `scope-audit.py MODEL`; the row said 78, the count when it was written. Requirement ids only ever accumulate — §5 — so a number written once goes stale by construction rather than by error.)* |
| **W6** | Frontend: app shell, dataset views, **validation report view**, **factor workbench**, model detail, diagnostics | W4, W5 | The two bolded views are where `01` §5.3 and `02` §5.3 place their interaction requirements |
| **W7** | freMTPL2 demo seed **and the demo entrance** | W4, W5, W6 | `07` FR-PLAT-37, plus FR-PLAT-53/54 (`NT-0002`). The data half closed early as **W7a** |

W4 and W5 are sequential in contract terms but their *frontend* work (W6) can start as soon
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
| ~~Custom objectives are a research task, not a coding task~~ **retired 2026-08-15** — OQ-MODEL-1 decided: templates only, and the parser the risk was really about was built in W4 for `01` FR-DATA-10 | What is left in Phase 1 is the certification machinery (FR-MODEL-76), which certifies losses `pricing-core` already differentiates. The research risk moves to Phase 2 with the expressions (W30) |
| Polars/DuckDB performance at 10 M rows discovered late | Test against a realistic dataset in W4, not at the end |
| Diagnostics scope creep — `02` lists a lot of them | FR-MODEL-50 (universal) is the gate; 51/52 can land incrementally |

---

## 7. Phase 2 — Rating Engine

**Goal:** DAG designer, rate tables, reference data, real-time + batch scoring, dislocation.

**Demo-able outcome:** **`wf-02` end to end** plus the deployment half of `wf-04` — an
approved model becomes rate tables, becomes a rating version, passes regression and
dislocation, and serves a live quote inside the latency budget.

### Workstreams

| # | Workstream | Notes |
|---|---|---|
| **W8** | **Spike S1/S2 resolution and ADR-0004 confirmation** | Must complete before W9. If S1 fails, this phase is re-planned |
| ~~**W9**~~ ✔ | Rating algorithm contract, validation, bundle compilation | `03` FR-RATE-1..13, 22..27, 56/57/58/59, FR-RATE-60 (added 2026-08-17 with `02` OQ-MODEL-3 — the row's original "FR-RATE-1..13, 22..27, 56/57/58/59" omitted it) — **Closed 2026-08-27** — see the W9 closure record (`docs/audit/work/W9/README.md`). The RatingAlgorithm contract (#291), the save-time validation and boundary guards (#292), and the bundle compilation (#293) shipped |
| ~~**W10**~~ ✔ | Rate tables incl. seeding from models, diffs, bulk operations, import/export | `03` FR-RATE-14..21, FR-RATE-62 (added 2026-08-18 with OQ-RATE-3 — the row's original "FR-RATE-14..21" omitted it) — **Closed 2026-08-28** — see the W10 closure record (`docs/audit/work/W10/README.md`). Seeding, diffs and validation (#297/#302), the four bulk operations, CSV/XLSX import/export and the parquet spill (#304/#307/#310), and the 202-with-Job diff with the DP3 cache (#311) shipped |
| ~~**W11**~~ ✔ | Scoring: real-time, batch, trace, one shared evaluator | FR-RATE-34..42, FR-RATE-64 (added 2026-08-18 with OQ-RATE-6 — the row's original "FR-RATE-34..42" omitted it); NFR-RATE-1 is the hard target, joined by NFR-RATE-13/14 (carried forward from W9 via register row F-W9-1 — omitted from this row until now) — **Closed 2026-08-30 as a REDUCED-SCOPE close** — see the W11 closure record (`docs/audit/work/W11/README.md`). **Seven of ten FRs delivered and tested; FR-RATE-36, 37 and 42 never started** — batch scoring and production sampling, reassigned to future slices whose plans and rulings are filed. **NFR-RATE-1, this row's own hard target, is measured and FAILING**: `_fetch_bundle` alone costs p99 66.294 ms against a 50 ms whole-request budget, over budget from 10 rps, cause resolved to fetch rather than saturation. Carried forward to an architectural ruling before W14. NFR-RATE-13 is recorded **owed, not delivered**. Closed by the lead under the maintainer's delegation of 2026-08-30 — **RE-OPENED IN PART 2026-08-30**, on the maintainer's direction (`docs/plans/2026-08-30-w11-reopen-direction.md` §1), in the shape Ruling 39 fixed. **The close note above stays verbatim and is not withdrawn**: it was correct at its date, and only the status marker moved — a ✔ over live work is §13's own defect inverted. Back in scope: **FR-RATE-36, FR-RATE-37, FR-RATE-42** and, riding with FR-RATE-42, **NFR-RATE-12**. Adoption slices E/F/G are a separate Work and are **not** part of this reopen. The §6 carry-forward naming an architectural ruling for NFR-RATE-1 is **discharged by Ruling 41** — a `ref` may not be served from the memo without a metadata read and does not need to be — but **NFR-RATE-1 is neither amended nor shown reachable**: the without-GBM limb reads component p99 23.027 ms against 15 ms with the fetch already excluded. The second close is appended to the closure record as §10, is scoped to the reopened requirements only, and is **the lead's to accept under the maintainer's conditional delegation of 2026-08-30** (`docs/plans/2026-08-30-w11-reopen-direction.md` §4), which supersedes Ruling 39 §5. **Two preconditions, neither waivable by the lead**: every reopened slice complete (W11-3's four tasks and W11-4's four, plus any further slice a ruling adds to the reopen), and the auditor satisfied with the closure audit — an unresolved auditor objection bars acceptance rather than informing it, and the disagreement route is escalation to the maintainer, never overruling the auditor — **SECOND CLOSE ACCEPTED 2026-08-30** by the lead under the conditional delegation, both preconditions met (all eight reopened tasks merged; the auditor satisfied in its own words). **All three reopened FRs — FR-RATE-36, FR-RATE-37, FR-RATE-42 — delivered and tested**, so the first close's *never started* is discharged. **NFR-RATE-12 measured and FAILING** at ~2.58× over a 200 GB/yr budget, on a conservative basis. **NFR-RATE-5 given its first verdict**, split: throughput PASS at 5.09×, linearity NOT MEASURED. **NFR-RATE-1's verdict is unchanged — still measured and FAILING**; Ruling 41 discharged the architectural question, not the requirement. The full record is §10 of the closure record |
| **W12** | Testing: golden quotes, property assertions, regression runs | FR-RATE-43..45 |
| ~~**W33**~~ ✔ | Machine-readable process core — NT-0014, adopted remainder (Slices E/F/G) | Adopted 2026-09-01 from NT-0014 by the reconciliation's dated acceptance line — the note's Slices A–D had landed 2026-08-30/31 under a dated delegation (the clause-2 exception's first instance, below). E/F/G landed with them: the process core held by `audit-docs` checks 26/27, the plan validator check 28, artifact B and the C2 retry-cap hook; C3 dissolved by Ruling 40, not built. **Closed** at [`docs/audit/work/nt-0012-0013-0014-adoption/README.md`](audit/work/nt-0012-0013-0014-adoption/README.md), accepted by the lead under the adoption record's §1.1 delegation. **Three findings carried open, not absorbed**: **F61** — C2's hook layer is bypassable and has no CI-equivalent backstop; **F58** — artifact B has no live writer; **F57** — zero retry-cap cycles have run, so §7's caps still have no data toward their own revisit condition |
| **W34** | The register is a ledger, evidence is a file — NT-0015, P1–P5 | Adopted 2026-09-01 from NT-0015 by the reconciliation's dated acceptance line. **P1–P5 all merged 2026-08-31** (`fa87086`, `890b06e`, `f99b55d`, `cfed4f0`, `6b3459a`, `365ad18`, the `lead.md` enter step): the decision grammar held by check 29 via `scripts/register-lint.py`; `scripts/register-owed.py` generates the owed list a close compiled by hand; the ledger/evidence split is real at `docs/audit/findings/` with **F27** the worked exemplar; migration opportunistic-on-amendment with a falsifiable residue line (38 of 61 rows over the 1000-character threshold at landing). **Three findings filed from the work itself**: **F62**, **F63** (ten W11-attributed register rows in no closure record — disposition reserved to the maintainer, reopening a Work close is theirs alone), **F64**. **One deviation deliberately not back-dated**: no adoption plan was filed for work that landed ahead of this row — named here rather than closed over; the next §14 review disposes of it |
| **W35** | **File taxonomy, reference coding and custody — NT-0016 Stages 2–5** | [`NT-0016`](../docs/notes/0016-file-taxonomy-reference-coding-and-custody-investigation.md) §4–§7, built against the ruled inputs (Rulings 55–65). **Stage 2 — the reference-coding standard:** filename grammar and header block per category, over the twelve-category set as amended by Ruling 62 (the closure/audit record's three homes documented; the map/leaf and rulings-record grammar splits resolved here as the named items Ruling 62 hands over); one home per category per Ruling 63 (rulings and ledgers stay in `docs/plans/` under filename grammar; closure/audit records keep their three homes; register + findings keep their two); citation forms per Ruling 65's mixed grammar — spec, ADR, note, register/findings and workflow journey cite by their existing id, while plan, rulings record, ledger, closure/audit record, contract and process/charter/skill cite by dated filename — prospective only, no frozen retrofit (Ruling 65 §2a, matching Ruling 58 for the notes family); `docs/INDEX.md` as the legacy mapping so the standard covers every file without moving one (C1); `scripts/file-lint.py` wired into the gate warn-then-red with a dated flag-day; the five creating skills (`writing-plans`, `close-workstream`, `phase-review`, `adr-write`, `spec-change`) updated to emit the standard. **Stage 3 — the ownership map:** the category × role matrix (creates/amends/retires) as a living file in `docs/process/` (Ruling 55), every cell citing the charter line that grants it, empty rows and columns filed as findings per NT-0015's grammar. **Stage 4 — the workflow-loop audit:** the lifecycle triple per category (which step creates, reads, retires), the four verdicts, and the unreferenced population — 39 files at `4f95fb3`, 40 at `052afe3` — decomposed into verdict-2 findings or declared verdict-4; verdict-4 status is **derived** from an existing closure record wherever one covers the file, and an explicit declaration is required only for the residual — the 3 verdict-2 files plus any future file with no covering closure record — in whichever of the two forms the implementing slice chooses (Ruling 64). **Stage 5 — migration and enforcement:** the prospective standard live from the flag-day; legacy migrates opportunistically-on-amendment only, never a bulk rename (C1); the census re-runs at every phase close, with growth in uncategorised or verdict-2 files a red flag in the phase review. **Dependencies:** Stage 4 needs the committed census (`docs/audit/file-census-5ef559d.csv`) and Stage 3's matrix; Stage 5 needs Stage 2; Stages 2 and 3 are independent now that Stage 1 and the gate ruling have landed (the note's §8 dependency chain). **Acceptance:** the note's §11 items (a)–(g). The notes move (the note's former S0) already landed as the investigation plan's Slice 4 (`1ec453b`, PR #544) **SUPERSEDED IN PART 2026-09-02 by W37.** [`NT-0019`](../docs/notes/0019-one-id-per-document.md) §9 replaces **Stages 2 and 5** outright — its §1 standard and §4 one-time scripted migration do that work across the whole corpus rather than over the twelve categories alone — **lifts constraints C1 and C2**, and lapses **Rulings 63 and 65** by their own override clauses. Ruling 64 survives as check 38; Rulings 55–58 are absorbed; Ruling 62's category set and the Stage 0 census are kept as inputs. **Stages 3 and 4 survive and are not lost with this clause**: they become the two downstream Works NT-0019 §8's closing sentence names — the charter investigation (§1.6 made binding in each charter, with a directory-level `owner:`) and the create-read-retire audit (the process step per transition in §1.2's state machines). The row is kept, not reclaimed (`CLAUDE.md` §5). **Do not plan against Stages 2 or 5 from here.** The direct contradiction, named rather than left for a reader to hit: this row's C1 says legacy migrates opportunistically-on-amendment and *never a bulk rename*, and a bulk rename is precisely what NT-0019 authorises — two live rows planning one corpus in opposite directions is what this clause exists to prevent. Disposition by the lead under the maintainer's 2026-09-01 delegation, recorded at `docs/plans/2026-09-01-maintainer-delegation-and-nt-0019-precedence.md`. |
| **W36** | A public face for a public repository — NT-0017, the residue | Adopted 2026-09-01 from NT-0017 by the reconciliation's dated acceptance line. The content landed 2026-08-30 under the note's §7 light path (`README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `.github/` templates — the clause-2 exception's second instance); the exposure is discharged. **The residue: two impact rows.** Row 9 — this roadmap row existing — is discharged by this row itself. Row 6 — the two repository settings (private vulnerability reporting; issues with templates) — is **not verifiable from the tree**: it is evidenced by a dated maintainer line, which is the maintainer's to write and nobody else can supply it. **Acceptance:** the note's §8 (a) and (c)–(e) — the link check, a test issue filed through each form, and the auditor's outsider read of the `README` |
| **W37** | **One id per governed thing — NT-0019, the whole standard** | Adopted 2026-09-01 from [`NT-0019`](../docs/notes/0019-one-id-per-document.md) by the note's **own dated `accepted` status**, which the maintainer ruled that day is this row's acceptance line: NT-0019 arrived accepted rather than being moved to accepted by a reconciliation, so the *"reconciliation's dated acceptance line"* that W33, W34 and W36 cite has no referent here, and W35 already cites neither — the register admits more than one authority form. The ruling is recorded at `docs/plans/2026-09-01-maintainer-delegation-and-nt-0019-precedence.md` §4, and the derivation rather than the conclusion is in the map plan's Authority section. **Scope:** the note's §1 standard in full — one global integer sequence across every row and document family, the five-word status vocabulary of §1.2a, the family-per-directory layout, the YAML header with its closed field set, roles per family, phase-as-milestone, and the generated index, ownership matrix and phase report; its §4 one-time scripted migration; its §5 impact map — root governance, all of `docs/`, seven role charters, two agents, every skill (twenty-six substantively, a header on all forty-six), fourteen scripts, twelve tests, two CI workflows, and every code and test file citing a document or requirement; and its §7 acceptance items (a)–(k). **Population, carried with its tree and its predicate because both matter:** the note's "767 files" at `8f5d57d` re-measures to **770** at `89dd2b1` and **771** at `bc7bc36`, but that figure uses a pattern including `VR-` product identifiers, which D5 places permanently out of scope — so the in-scope population at `bc7bc36` is **768**, with 3 files matching only via a `VR-` id. The corpus also grows with every new file citing a requirement, so a slice re-derives both numbers rather than quoting these. The auditor's pinned sweep at `89dd2b1` further corrects the note's own §5.6 evidence in two material places — `backend/src/app` and `backend/tests` each claim roughly the *combined* backend total (measured 88 + 93 + 28 = 209 against ~410 claimed), and `backend/migrations` is claimed at 3 against 28 measured — so W37-6's leaf plan is written from that sweep, never from §5's table. **Eleven slices** cut from §8's stages S1–S4 by `docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md`: four building the instruments in parallel, one building the migration script against a fixture corpus, **one supervised run that moves the whole corpus and must land at a gap with no open branches** and is never fanned out, four applying the conventions, and one proving acceptance (j) and (k). **Supersedes W35 in part** — see that row. **Decision points — updated 2026-09-02.** The plan recorded eight, two disposed of in it. **DP-1, DP-2 and DP-3 are ruled** as Rulings 66, 67 and 68 (`docs/plans/2026-09-02-w37-migration-preconditions-rulings.md`), together with **Ruling 69** on a fourth point raised during execution — §1.5's vendored-skill criterion names `graphify`, `systematic-debugging` and the `vue-*` skills as vendored while defining vendored as *"anything shipping its own `LICENSE`"*, which exactly two of twenty-eight do; the parenthesis is ruled a gloss, not a detector. **Two consequences this row must carry.** First, **DP-2 blocks W37-4, not only W37-6** — item (d) and check 36 read one shared constant, so the earlier slice carries the earlier date. Second, **Ruling 66 enlarges W37-6's commit** by folding the creating instruments into it, ruled as a criterion — every instrument whose output checks 30–39 test — with the note's seven as a floor and `git-hygiene` and the skills README named for explicit disposition; **the maintainer's go-ahead for W37-6 must disclose that enlargement**, which the existing precondition does not cover. Still open: **DP-6**, blocking W37-9, discharged by a dated maintainer line on that slice's PR (`CLAUDE.md` §12 reserves an amendment to what that file requires), and **DP-4**, non-blocking, applied at W37-11. **`CLAUDE.md` §5's never-renumber rule yields to this work**, at two sites, by the maintainer's dated precedence ruling of 2026-09-01; a rule that yields still yields visibly. **Acceptance:** the note's §7 (a)–(k) **Progress, 2026-09-02.** **S1 complete** — W37-1 the standard and thirteen templates, W37-2 `doc-id.py`, W37-3 `doc-index.py`, W37-4 `audit-docs.py` checks 30-39 with ten broken-input proofs. **W37-5 merged**: `migrate` built and proven on a fixture corpus, then hardened after four defects were found in already-merged code by running it against the real tree. **W37-6 has not run and its go-ahead has not been asked for.** **Rulings 70-80 filed** since this row's decision-point clause was written; note especially that **Ruling 73 withdrew Ruling 66's acceptance item 2** rather than sharpening it — run as written it returned zero for four of thirteen instruments, so it would have ordered them removed from the commit that exists to carry them. **Four discovery defects are filed against merged W37-5 code and owned by W37-6**: every `_discover_*` function was written against the fixture corpus and four do not match the real tree — the roadmap (41 works, 0 converted, success reported) and the register (0 discovered) are guarded but their patterns unfixed; closure-records (21 headings, 10 records) is fixed by accounting for every heading; `plan-reviews` is neither fixed nor guarded — **its figures here were wrong and are corrected 2026-09-02**: the file has **14** `###` headings (11 reviews, 3 non-review sub-content), not 15, and `_discover_plan_reviews` produces **10** records, not 12. `_REVIEW_HEADING_RE` requires the date to end the heading line and `Plan review 9`'s carries trailing text, so it is never discovered and its whole body — with three sub-content headings — folds into `Plan review 1`'s record, dated fifteen days earlier. The same end-anchor defect PR #585 fixed for `closure-records.md`. The file-level guard cannot see it: it trips on zero, and this is ten of eleven. Measured by running the function at `ffac8ba`; the original figures were relayed from a report rather than run. See `docs/plans/2026-09-02-w37-6-go-ahead-withheld.md`, and three of its headings carry no date at all, so the per-heading model may be the wrong shape for that file. **The guards catch zero-discovered, not undercount** — they would not have caught the closure-record defect that found them. Also owned by W37-6: `is_vendored`'s `LICENSE` probe, which Ruling 69 rejected and Ruling 76 re-assigned as a class with a sweep, and the roadmap restructure itself, deferred because Rulings 79 and 80 declare its target parsers wrong with the fixes not yet landed. **W37-5b inserted 2026-09-02** by the lead's decision at `docs/plans/2026-09-02-w37-5b-slice-decision.md`, deciding §7 of the obligations list (`docs/plans/2026-09-02-w37-6-outstanding-obligations.md`, 39 obligations, none in a fixed state). It sits between W37-5 and W37-6 and carries the pre-run preconditions: the four discovery defects, Ruling 83's census, Rulings 79/80's parser fix, Ruling 76's three-site `is_vendored` class, F76's unguarded `build_corpus` call, and the two silent discovery functions the guards never covered — sixteen items, each provable on deliberately broken input outside the irreversible commit. **The deciding fact is that W37-6 cannot pass its own acceptance item 13 until this lands**: exactly two tracked files meet that item's description and the shipped `LICENSE` probe treats neither as vendored, so the run rewrites both. Two of its rows are group A but not this slice's to build — `plan-reviews.md`'s heading mis-nesting stays with the lead so an executor does not restructure the document its own parser fix is tested against, and the identifier standard's §8-versus-Ruling-66 stage-boundary conflict is routed to the decision-maker because re-cutting a stage of an accepted standard may be an amendment reserved to the maintainer. A slice is named here rather than given a row of its own, which is how every slice in this file is recorded. **W37-5b progress, corrected 2026-09-02 — the paragraph above is stale from the moment of insertion and is kept, not rewritten, because it is what the slice decision itself pointed at; this sentence is the update.** All sixteen built rows have landed, each proven on deliberately broken input against the real tree, not a fixture: the roadmap now converts 41 of 41 works (`4cbfa62`, rows 2/91/92, reproduced independently at `d47a5f5`: phase totals 7+5+14+8+7=41) and the register 73 of 73 rows (`4cbfa62`, row 3/34); the plan-reviews heading anchor and Ruling 83's census land together (`4367cf7`, row 1: 10 of 14 headings becomes 11 of 14, with a class-wide guard rather than a single-file patch); the closure-records "not closed" abort becomes ten `LG-` records (`614c92c`, row 4, verified 8 `CR- work` + 1 `CR- phase` + 2 `RS- audit` + 10 `LG-` = 21, reproduced independently); the five silent discovery functions gain the same three-bucket census (`d7c9b08`, `a31d509`, rows 5/15/30/31); the vendored-skill class lands as a declared 28-member constant reconciled against ruff's exclude list, both empty both directions (`574d536`, rows 9/10/11, reproduced independently); F76's check-39 guard is fixed and proven on a malformed header without disarming the six checks behind it (`35c1488`, row 12); `doc-index.py`'s row and phase field policy is derived per family from the templates rather than hand-transcribed, and a template's own example block now parses through the real row parser that consumes it (`e7e1d24`, rows 8 and 13); Ruling A1–A3's family (row 6, derivation `04f47b2`, ruled `RL-` by Rulings 86–87) and the "Pending proposals" container's family (row 7, derivation `44ec54e`, ruled `RFC-` by Rulings 88/89/93) are both ruled, with the discovery code that would emit either as a draft not yet written — filed as **F81** and **F80** respectively, both blocking a real `migrate()` run today for reasons no group-A row promised to fix (see the closure record's §6). Row 14 (`plan-reviews.md`'s heading mis-nesting) was fixed by the lead directly (`2fbce0c`), not built inside the slice, as planned. Row 36 (§8 vs. Ruling 66) is ruled, not amended — Ruling 85: "§8 is sequencing… No amendment is needed and Ruling 66 stands as issued." A new dated leaf plan for W37-6 supersedes the frozen one by name (`2026-09-02-w37-6-migration-run-leaf-plan-v2.md`, `status: active` since Ruling 88 resolved its one blocking row), restating acceptance item 11 with Ruling 73's amendment in its own text. Two gaps each row's own author disclosed rather than called done, now register rows: F77 (Ruling 84 §4's `slice:` acceptance item is vacuously true — ruled by Ruling 94, 2026-09-02, PR #614; the ruled instrument is not yet implemented, no owner named) and F78 (`_discover_roadmap`'s phase-spanning refusal has no fixture, owner W37-6). F79 carries obligations row 34's disclosed non-reuse of `register-lint.py`'s counting technique for the new census. F76's register row, previously mis-tracking this fix as owed to W37-6, is corrected in place. Full evidence and every unevidenced item's verdict: [`docs/audit/work/W37-5b/README.md`](audit/work/W37-5b/README.md). **W37-5b CLOSED 2026-09-02** on a clean audit and the lead's merge (`64f63ee`, PR #617), per `CLAUDE.md` §13 — a Slice's close is the lead's, not the maintainer's acceptance, and this line records it rather than requesting it. The audit carries one item outside the slice's own scope forward to W37-6: a real `migrate()` run would abort at **four independent guards** — this sentence read *"three"* until 2026-09-02 and the correction is Addendum B's to `docs/plans/2026-09-02-w37-6-go-ahead-ask.md`, which found F80's gap covered by **two** guards one line apart, so clearing the census alone still aborted. Named by function rather than by line, because Addendum B B.2 records that every `doc-id.py` line number in eight tracked documents, this row included, was measured at a tree none of them names: in pipeline order `_check_multi_ruling_files_not_silently_unrecognised` (F81, the `RL-`-ruled Ruling A1/A2/A3 file with no discovery code), `_check_plan_reviews_heading_census` and `_check_headed_split_file_not_silently_unrecognised` (both F80, the `RFC-`-ruled "Pending proposals" container), and `_check_requirements_not_silently_unrecognised` (F82, four module-less `DEP-` ids in `docs/specs/00-overview.md` invisible to the module-coded matcher). Each is this slice's own new instrumentation correctly catching a pre-existing gap rather than a shortfall in any of the eighteen rows; all were unowned at this close; and they are disclosure for the W37-6 go-ahead ask, not grounds to withhold this slice's close. **Superseded 2026-09-02 as a statement of current state, and kept as the record of what W37-5b's close reported**: all four are cleared by `544b90c` (#629), verified by execution at `6e35b9c` in [`docs/audit/work/W37-5c/README.md`](audit/work/W37-5c/README.md) §2 — and a **fifth** abort point, `_discover_vendored_skill_manifests` (F88 limb 1), still fires on the real corpus and was never touched by that commit, so `migrate()` still cannot complete. **Superseded 2026-09-02 (PR #649) for the fifth point and kept as the record of what W37-5c's close reported: it is cleared.** `_discover_vendored_skill_manifests` classifies with `_front_matter_state`, which is textual and cannot raise, and returns a closed partition instead of a list — clearing the abort *and* the silent skip of 25 of 28 manifests that the same wrong predicate caused. Verified as a whole run rather than as one function: `migrate()` reaches `_write_document_drafts`, its first write, on a git-tracked snapshot of the real corpus with the tree byte-unchanged, while the shipped `doc-id.py` at `c888b61` aborts on that identical snapshot at `.claude/skills/create-adaptable-composable/SKILL.md:6`. **That is five of five cleared, and no sixth abort point exists before the first write** — the replay reached the first write rather than enumerating the pre-write calls, so a call nobody listed cannot be missed by it; a sixth appearing inside any `_discover_*` reds `test_exactly_one_discovery_writer_claims_the_closure_readmes`. **It does not say the run succeeds, and the first thing past the first write is a mid-write crash.** Running `migrate()` to completion on a throwaway snapshot of the real corpus — never the repository — raises `KeyError: 'RS'` inside `_write_document_drafts` **after writing 125 of the 290 document drafts and deleting none** — 165 never reached: `_discover_closure_records` emits two `RS-` document drafts from `docs/audit/closure-records.md`, and neither `_DOCUMENT_FAMILY_DIR` (6 keys, no `RS`) nor `_MIGRATE_TEMPLATE_FILENAME` (7 keys, no `RS`) has an entry for the research family, though `docs/_templates/RS.md` exists. **This is task #34's mode, one layer down** — a partial migration rather than a clean abort — and it was invisible while the fifth abort point stopped the run before it. **It pre-exists the fix in this PR and is revealed by it, not introduced**: the shipped `doc-id.py` at `c888b61`, on a `c888b61` snapshot with only the fifth abort neutralised, raises the identical `KeyError` after the identical 125 writes. **The count was first given here as 126 and is corrected**: that figure counted `scripts/__pycache__/register-lint.cpython-312.pyc`, a bytecode cache the import machinery wrote, as a migration output. 125 is measured by tracing every `Path.write_text` the real writer performs — 125 calls, 125 distinct paths, none repeated, none outside `docs/` — and agrees with the first `RS` draft sitting at index 125 of the 290, read inside `_write_document_drafts` rather than reconstructed from the discovery order (a reconstruction that disagreed by one and is discarded). **Fixed, and the sentence this replaces was wrong.** It read *"what the `RS-` family's target directory and template are is a disposition, not a defect with one right answer, and it is the lead's"* — **NT-0019 §1 already states both**, so there was nothing to dispose of. Its Research row gives `RS` the directory `docs/research/`, the unit *one spike, measurement or audit*, and the kind vocabulary `spike` · `measurement` · `audit` (quoted verbatim in `docs/audit/findings/F88.md`, which is not a table row and can carry the row's own pipes); `docs/_templates/RS.md` exists; and D13 routes `RS- kind: audit` to `auditor` — which `_discover_closure_records` already sets. **The writer was incomplete, not the classifier**; emitting `RS` for two audits sitting in a closure-records file is correct and was not changed. **The set was closed rather than the instance**: every prefix a `_Draft(materialize="document")` can carry is derived from the source by an AST walk — resolving a variable through its assignments and a parameter through its call sites — and independently by running every discovery over the real corpus. The two agree exactly: **`{ADR, CR, LG, PL, RFC, RL, RS}`**, and `RS` was the only member missing from either table, missing from **both**. `REFERENCE` sits in `_MIGRATE_TEMPLATE_FILENAME` and not in `_DOCUMENT_FAMILY_DIR` legitimately — it is stamped in place and carries no `id:` — and that asymmetry is now asserted as an equality so a second one cannot appear unnoticed. `_check_every_document_draft_is_placeable` refuses in the pre-write span if a document draft names a prefix either table lacks; it **cannot fire on any corpus**, only on a source change, so it adds no corpus-triggerable stop while converting a mid-write `KeyError` into a named refusal. With this, `migrate()` **runs to completion** on a throwaway snapshot of the real corpus — 1,085 files written, 202 deleted — and no seventh failure follows. **W37-5c inserted 2026-09-02** by the maintainer's dated line withholding W37-6's go-ahead a second time (`docs/plans/2026-09-02-w37-6-go-ahead-ask.md` §8) and cutting a second precondition slice, recorded at `docs/plans/2026-09-02-w37-5c-slice-decision.md`. It sits between W37-5b and W37-6. **Its scope criterion is wider than the three abort guards and is the maintainer's own: everything that stops *or blinds* the run and is provable on broken input outside it** — a check that cannot fail blinds the run as surely as a guard that aborts stops it. Six items: F80, F81 and F82; the discovery-and-stamp path for `.claude/skills/`, `.claude/agents/`, `.claude/roles/` and the README population; the three unparseable vendored manifests; **R84 §4 item 2 built** (vacuous at birth — `_stamp_header` skips `slice` unconditionally, so nothing can write the value the check reads); and **R86 §4 item 3 rebuilt so it can pass on some input** (after `2e48960` the value it demands cannot be produced by any input, by construction). Same discipline as W37-5b: red-before/green-after, and the arithmetic closes over the real corpus, not a fixture. **Gap 2 is ruled in the same instruction** so the slice builds against a rule: `Phase` takes `lead`, `WK` takes `maintainer`, skills take one standing `lead`, `contracts/` takes `executor`; the README row is routed to the planner. **Two of those changed on challenge and the slice decision's §4 carries both**: `contracts/` cannot take a generator-emitted header at all — 59 of its 61 files are JSON, which has no comment syntax, so front matter makes them unparseable — and the maintainer's pre-authorised `generated: true` exemption in check 35 is taken instead; and `WK`'s author-equals-acceptor collapse is real but narrower than `Phase`'s, because §1.6's WK cell names no routine maintainer of the row for the value to have been read from. **The re-ask is one document**, not a package: §3 and §4 re-derived at that tree, the addendum merged and re-run, and F80-F82 shown cleared by execution. **W37-5c CLOSED 2026-09-02** on a clean audit and the lead's merge (`c888b61`, PR #647), per `CLAUDE.md` §13 — a Slice's close is the lead's, not the maintainer's acceptance, and this line records it rather than requesting it, on W37-5b's precedent one clause above. Every scope item delivered, scored item by item in the record's §1 and §3; the four abort points named above are verified cleared **by execution** at `6e35b9c`, which is the re-ask condition *"F80–F82 shown cleared by execution"* discharged. **The slice's most valuable output contradicts its own headline: `migrate()` still does not complete.** **Four W37-6 preconditions were found and none of them existed on any prior list** — not in the map plan, not in either leaf plan, not in the withheld go-ahead's six conditions; each was produced by building the slice and reading what its own new instruments then reported, which is the sentence a W37-6 planner needs. **F87** — `_id_scope_documents()` returns **1** document at `d8d6e3f`, so checks 30–39 see **0 of the 65** files the widened `_ID_SCOPE_ROOTS` was meant to reach: the *glob*, not the roots, bounds those checks, and this one **passes** rather than aborting, so it blinds the run where F80–F82 stopped it. **F88 limb 1** — `_discover_vendored_skill_manifests` is the **fifth abort point**, reclassified from *blinds* to *stops* by the record's §2 row 5, pre-write and therefore a clean abort rather than a partial migration. **F90** — check 37 reds **95 of 95** ruling documents at migration, its `^##\s+` detector unable to see the `###` nesting every ruling uses — a count produced by running `doc-id.py`'s unmodified splitter against a clone to materialise real stamped `RL-*.md` files and then the real `check_shape()`, at `4df1c45`. **That tree resolves inside this checkout and nowhere else**: it is PR #640's tip, and #640 squash-merged as `dc1666f`, so `4df1c45` is an ancestor of no remote ref and a single local branch is all that keeps it reachable — a fresh clone cannot resolve it today, and §5.4's own gap condition, which releases every agent worktree before the migration branch is cut, deletes the last ref that does. **F90's disposition should re-pin the measurement to a reachable commit or re-run it**, rather than add a tree it already has, including the thirty written after the flag-day *to comply*; it predates the flag-day commit, which is why that commit merged rather than being held. **F92** — 53 files deferred out of §4 step 5's Reference stamp set, recorded only in a squash-commit body, which no planner reads; W37-6's §7.1 Task 1 discharges it. **F86**, **F89** and **F91** were also filed; F86 carries an explicit decay to the next `CLAUDE.md` §14 plan review, its own row having named this close as the owner-assigning event. Full evidence and every finding's adopted verdict, including the four the lead amended: [`docs/audit/work/W37-5c/README.md`](audit/work/W37-5c/README.md). **Superseded 2026-09-02 (PR #649) as a statement of current state, and kept as the record of what W37-5c's close reported:** the fifth abort point is cleared and so is the mid-write `KeyError: 'RS'` behind it, which no run had been able to reach before it was; on a throwaway snapshot of the real corpus `migrate()` now runs to completion. The clause earlier in this row carries the evidence and the predicates; this sentence exists only so the row does not end on a state that has moved. |
| **W13** | Dislocation with attribution | FR-RATE-46..49 |
| **W14** | Deployment: environments, atomic switchover, rollback, shadow — **and the tenancy mechanics ADR-0006 requires** | FR-RATE-50..55; `07` FR-PLAT-28..31, and added 2026-08-15 by OQ-OVR-1's decision: **FR-PLAT-56** (a deployment refuses to start against another tenant's database) and **FR-OVR-16** (a Job records the platform build, because version skew between tenants is now permanent). Any earlier `Job` migration should carry FR-OVR-16's column rather than wait for this |
| **W15** | Frontend: **DAG designer (Vue Flow)**, rate table editor, quote sandbox + ladder waterfall, dislocation views | The DAG designer is the single largest frontend effort in the project |
| **W30** | **`expression` custom objectives** — SymPy derivation, the gradient/hessian compilation target, the authoring UI, and lifting `expression_objectives_enabled` **plus `custom_objective:author` and its check, which `06` FR-GOV-39 requires the `expression` kind to arrive with** | Added 2026-08-15 by OQ-MODEL-1's decision, which moved this work out of W5 rather than deleting it: `02` FR-MODEL-40/41, FR-MODEL-75, §4.6, and `wf-05` Route B. It depends on nothing in W9–W15 and could equally be pulled into 1b if W5 finishes early — but it must not start before the certification machinery it fronts (FR-MODEL-76) has run for a phase, which is the whole point of the decision |

### NT-0014 … NT-0017 — the four notes, reconciled 2026-09-01

**A note decides nothing** (`docs/notes/README.md`). Four working notes are filed and
`open` — proposed, not adopted — and each proposes work large enough that adopting it would
change this page. They are recorded here so a reader cannot mistake "filed" for "planned",
and so the reconciliation has a fixed moment rather than happening whenever someone
remembers. **Reconciled 2026-09-01 — accepted as proposed, all four dispositions dated in the
reconciliation's own acceptance line.** Each note's row below records its conversion; the note
statuses remain the record of what landed, not of adoption.

**The rule, three clauses:**

1. **All four are reconciled at the W11 close — at the same moment as its `CLAUDE.md` §14
   plan review, but as its own dated record, not inside it.** The trigger is shared because
   §14's is already fixed at every workstream close, and because §14 asks whether the plan
   still says the right thing now that some of the work is real — an unadopted proposal is
   precisely a claim about what the plan is missing. **The documents stay separate because
   they are different instruments**: a §14 review answers five fixed questions and outputs a
   proposal carrying one maintainer acceptance line, while a reconciliation walks each note
   section by section and outputs adopt / reject / defer per note. **Bundling them would make
   that single acceptance line ambiguous** — accepting "the review" would silently accept four
   adoptions — and the NT-0010/0011 reconciliation set the precedent by running as its own
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
   instances: NT-0014's Slices A–D and NT-0017's S1/S2 (both 2026-08-30), and NT-0016's four
   investigation slices and eleven rulings (2026-09-01).
3. **A note that is neither adopted nor rejected keeps a named owner and a next trigger.**
   Silence is not an outcome, the same rule `CLAUDE.md` §13 applies to an unevidenced
   requirement. A rejected note is recorded as rejected, with its date and reason, and its
   number is retired with it.

**Nothing here is committed work.** The table is the reconciliation's agenda, not a plan.

| Note | Proposes | State entering the reconciliation |
|---|---|---|
| [`NT-0014`](../docs/notes/0014-machine-readable-process-core.md) | A machine-readable core for the delivery process — a checkable extract of the rules that are prose today | **Landed 2026-08-31 — all eight slices merged** (`33b5ef1`, `0be9c3c`, `97965be`, `b551060`, `26de823`, `53257b4`, `9e8783d`): the process core is filed and held by `audit-docs` checks **26** (citations) and **27** (content digest), the plan validator is check **28**, artifact B and the C2 retry-cap hook are built. **C3 dissolved by Ruling 40, not built.** Closed at [`docs/audit/work/nt-0012-0013-0014-adoption/README.md`](audit/work/nt-0012-0013-0014-adoption/README.md), accepted by the lead under the adoption record's §1.1 delegation. **Three findings carried open, not absorbed**: **F61** — C2's hook layer is bypassable and, unlike the C3 that Ruling 40 dissolved, has no CI-equivalent backstop; **F58** — artifact B has no live writer; **F57** — zero retry-cap cycles have run, so §7's caps still have no data toward their own revisit condition. **Reconciled 2026-09-01 — adopted; converted to W33 above** |
| [`NT-0015`](../docs/notes/0015-the-register-is-a-ledger-evidence-is-a-file.md) | Naming the register's decision grammar, a decay rule for unowned rows, a linter for what is named, splitting ledger from evidence, and generating the owed list a close compiles by hand | **Landed 2026-08-31 — P1–P5 all merged** (`fa87086`, `890b06e`, `f99b55d`, `cfed4f0`, `6b3459a`, `365ad18`, and the `lead.md` enter step): the decision grammar is held by `audit-docs` check **29** via `scripts/register-lint.py`; `scripts/register-owed.py` generates the owed list a close previously compiled by hand, cited in both close checklists and in `lead.md`; the ledger/evidence split is real at `docs/audit/findings/` with **F27** migrated as the worked exemplar (4268 → 818 chars), and migration is opportunistic-on-amendment with an aggregate residue line making that claim falsifiable (**38 of 61** rows over the 1000-character threshold at landing). **Three findings filed from the work itself**: **F62** — `03` §4.4's `timing_ms` example disagrees with what `score_one` emits; **F63** — ten W11-attributed register rows appear in no W11 closure-record findings section, all predating the close, disposition reserved to the maintainer because reopening a Work close is theirs alone (`CLAUDE.md` §13); **F64** — check 29's own parser read 48 of 59 rows while reporting `OK`, one of three silent row-losses in that script fixed the same day. **One impact-matrix row deliberately not built**: no `docs/plans/<date>-nt-0015-adoption.md` was filed, and none has been back-dated — the slices were dispatched and merged without one, and writing a plan today for work already landed would record a sequencing that did not happen. Named here rather than closed over; the deviation is the next §14 review's to dispose of. **Reconciled 2026-09-01 — adopted; converted to W34 above** |
| [`NT-0016`](../docs/notes/0016-file-taxonomy-reference-coding-and-custody-investigation.md) | A closed file taxonomy across `docs/` and `.claude/`, a reference-coding standard, an ownership map per category, and an audit of whether each category is genuinely created-read-retired | Filed 2026-08-30, `open`. Includes a proposed relocation of the notes themselves, so its adoption would move the other three. **Reconciled 2026-09-01 — adopted; converted to W35 above** |
| [`NT-0017`](../docs/notes/0017-a-public-repository-needs-a-public-face.md) | A root `README`, a `SECURITY.md` with a private reporting channel, a `CONTRIBUTING.md` and intake templates | Filed 2026-08-30, `open`. **The repository went public on 2026-08-30 with none of these**, so this one has a live exposure behind it rather than a tidiness argument — see [`docs/audit/security-posture.md`](audit/security-posture.md). §5's three policy questions are **ruled** — [`docs/plans/2026-08-30-nt-0017-maintainer-decisions.md`](../docs/plans/2026-08-30-nt-0017-maintainer-decisions.md) — and that record is explicit that the ruling authorises the *content*, not the *adoption*: the note **stays `open`** here, its disposition still the joint reconciliation's. Landing under the note's own §7 light path ahead of that reconciliation, the same way NT-0014's Slices A–D landed ahead of it (row above): **S1** (`SECURITY.md` + the two repository settings) then **S2** (`README.md`, `CONTRIBUTING.md`, `.github/` templates), as separate commits, both filed 2026-08-30. **Reconciled 2026-09-01 — adopted; converted to W36 above** |

### Requirement coverage

≈ **67 `RATE` + ~25 remaining `PLAT`** requirements, plus the `MODEL` requirements W30 carries over (FR-MODEL-6, FR-MODEL-40/41/75 and the `expression` half of §4.6/§4.7). **FR-MODEL-6 added 2026-08-19, accepted by the maintainer 2026-08-22**: `expression` factors are an expression feature, and the verdict on file sends them to “the slice OQ-MODEL-1 gates”, which is this row — but the list named only the objective half, leaving the requirement owned by a slice that did not list it.

### Top risks

| Risk | Mitigation |
|---|---|
| ~~OQ-RATE-1 — ZEN decimal semantics invalidates ADR-0004~~ **retired 2026-08-14**: the engine uses `rust_decimal`, so this risk did not materialise. Replaced by two silent-failure risks at the boundary (FR-RATE-56/57) | Re-scoped S1 before W9; integer-minor-units is no longer needed as a mitigation |
| NFR-RATE-1 (p99 < 50 ms) missed and expensive to recover | Build the latency harness in W11 alongside the evaluator, not after |
| DAG designer is under-estimated | It is a graph editor with live validation — treat as its own project with its own spike |
| Rate table scale (vehicle × area = millions of cells) | OQ-RATE-3; the recommendation already sets a spill threshold |

---

## 8. Phase 3 — Governance

**Goal:** RBAC, approvals, audit UI, model documentation generation.

**Demo-able outcome:** **`wf-05` end to end** — a custom objective authored, certified,
two-approver reviewed, used, and audited — plus a generated dossier that would survive
external review.

### Workstreams

| # | Workstream | Notes |
|---|---|---|
| **W16** | Full scoped RBAC, custom roles, break-glass | `06` FR-GOV-1..8 |
| **W17** | Approval policies, escalation, evidence enforcement, attestations | FR-GOV-9..19 |
| **W18** | **Approvals inbox with inline evidence** | FR-GOV-16 — "the screen where the platform earns its keep" |
| **W19** | Audit explorer, chain verification, export | FR-GOV-20..26 |
| **W20** | Dossier generation, commentary blocks, PDF, point-in-time regeneration | FR-GOV-27..31 |
| **W21** | Regulatory evidence export | FR-GOV-32 |
| **W22** | Model risk tiering, if OQ-GOV-4 is accepted | Small addition to Approval Policy |
| **W31** | **Proxy assessment** — an insurer-supplied reference table, association measures (mutual information, exposure-weighted AUC), evidence attached to the approval request | Added 2026-08-15 by OQ-MODEL-7's decision: `02` FR-MODEL-82. **Evidence, never a block** — it belongs beside `04` FR-OPT-24's outcome disparity report, and both exist to inform a legal judgement the platform must not make |

Much of the *write path* already exists from Phase 1 (§5). Phase 3 is largely the
**surfacing** of it — which is why it is comparatively low-risk despite being 43
requirements.

---

## 9. Phase 4 — Optimisation & Monitoring

**Goal:** demand models, constrained optimisation, drift monitoring, GIPP consistency.

**Demo-able outcome:** **`wf-03` end to end** plus the monitoring half of `wf-04` — a rate
change proposed by the optimiser with GIPP evidence, deployed, then measured against what
it promised.

### Workstreams

| # | Workstream | Notes |
|---|---|---|
| **W23** | Demand models, price-variation reporting, elasticity with CIs | `04` FR-OPT-1..7 |
| **W24** | Optimisation runs, constraints, binding analysis, frontier | FR-OPT-8..17 |
| **W25** | GIPP checks, price-walking, disparity reporting | FR-OPT-18..24 |
| **W26** | Materialisation into rate tables | FR-OPT-25..28 |
| **W27** | Monitoring: monitors, drift, A/E, demand, rate achieved, operational | `05` FR-MON-1..27 |
| **W28** | Alerting lifecycle and routing | FR-MON-28..32 |
| **W29** | Dashboards and monitoring packs | FR-MON-33..35 |

**Sequencing note:** W27 (monitoring) delivers value the moment Phase 2 is live and does
**not** depend on W23–W26. If Phase 4 is long, **pull monitoring forward** — a deployed
rating structure with no monitoring is the least comfortable state the platform can be in.

---

## 10. Decision gates

Which open questions must be answered before which phase. Answer them in this order and
you never block on a decision you have not reached.

| Gate | Questions | Count |
|---|---|---|
| ~~**Before Phase 1a**~~ ✔ **all decided** | ~~OQ-OVR-2~~, ~~OQ-PLAT-1~~, ~~OQ-DATA-1~~, ~~OQ-DATA-2~~ *all 2026-08-14*, ~~OQ-DATA-7~~ *2026-08-15, raised and decided inside the phase by driving the exit demo*, ~~OQ-OVR-8~~ ✔, ~~OQ-MODEL-16~~ ✔, ~~OQ-MODEL-18~~ ✔, ~~OQ-MODEL-19~~ ✔, ~~OQ-MODEL-20~~ ✔, ~~OQ-DATA-11~~ ✔ *all 2026-08-19, raised and decided inside the phase*, ~~OQ-OVR-9~~ ✔, ~~OQ-MODEL-21~~ ✔ *2026-08-21, raised and decided inside the phase — FR-OVR-19's delivery precedes the exit demo, FR-MODEL-111 is a W5 obligation*, ~~OQ-MODEL-24~~ ✔ *2026-08-22, raised and decided inside the phase from the first measurement of NFR-MODEL-4 — it gated W5's closure, because the answer changes whether a delivered requirement is in breach* | 14 (0 open) |
| **Before Phase 1b** — *re-opened 2026-08-22* | ~~OQ-OVR-5~~ ✔ *2026-08-14*, ~~OQ-MODEL-1~~ ✔, ~~OQ-MODEL-5~~ ✔, ~~OQ-PLAT-6~~ ✔, ~~OQ-OVR-6~~ ✔ *all 2026-08-15*, ~~OQ-OVR-7~~ ✔, ~~OQ-DATA-8~~ ✔, ~~OQ-MODEL-8~~ ✔, ~~OQ-MODEL-9~~ ✔ *all 2026-08-17*, ~~OQ-MODEL-10~~ ✔, ~~OQ-GOV-7~~ ✔, ~~OQ-MODEL-14~~ ✔ *all 2026-08-18*, ~~OQ-PLAT-9~~ ✔ *raised and decided 2026-08-23 — how a chosen workspace reaches the API: a verified `Workspace-Id` request header, checked against the principal's own memberships, absent one refused rather than defaulted (`07` FR-PLAT-65). `W6b-11` is unblocked as a decision and waits on W32's backend half*, ~~OQ-DATA-9~~ ✔ *2026-08-19 — raised in W5 and never placed on this table until it was decided, so the gate it belonged to had already closed; it gates W6b's dataset list, which is Phase 1b work*, ~~OQ-MODEL-15~~ ✔, ~~OQ-MODEL-17~~ ✔, ~~OQ-MODEL-22~~ ✔ *all 2026-08-21, raised in W5 and never placed on this table until decided — FR-MODEL-109 delivered with the decision, FR-MODEL-110's trigger is Phase 1b's job-latency measurement, FR-MODEL-112's first slice is Phase 1b's*, ~~OQ-MODEL-25~~ ✔, ~~OQ-MODEL-26~~ ✔ *both raised **and decided** 2026-08-22, out of the two modelling decisions taken that day — the first a live silent mis-fit, the second an unbounded diagnostics sweep. This gate had been closed since 2026-08-21; it re-opened rather than pretending they arrived earlier, and closes again the same day. Neither landed where its question pointed: FR-MODEL-116 supersedes the offset **intent** on a layer argument, the duplication argument having failed checking, and half of the second was withdrawn as a no-op. Each raised a successor owned by W30, which is Phase 2 — placed at that gate rather than held here*, ~~OQ-MODEL-29~~ ✔, ~~OQ-MODEL-30~~ ✔ *both raised 2026-08-22 by W32-1's constraint guard and never placed on this table at all — the fifth time a question has been decided without appearing here, and the reason the count below is a recount rather than an increment. The first was decided 2026-08-22 (an inert `seed` keyword removed), the second 2026-08-23 into FR-MODEL-126. Both gate Phase 1b slices, so they belong at this gate and not a later one*, ~~OQ-MODEL-35..41~~ ✔ *placed 2026-08-26* | 28 (0 open) |
| **Before Phase 2** — *re-opened 2026-08-22* | ~~OQ-RATE-1~~ ✔, ~~OQ-RATE-2~~ ✔ *both decided by spike*, ~~OQ-MODEL-3~~ ✔ *2026-08-17*, ~~OQ-MODEL-11~~ ✔, ~~OQ-MODEL-12~~ ✔, ~~OQ-RATE-3~~ ✔, ~~OQ-RATE-4~~ ✔, ~~OQ-RATE-6~~ ✔, ~~OQ-PLAT-3~~ ✔, ~~OQ-GOV-8~~ ✔ *all 2026-08-18*, ~~OQ-MODEL-23~~ ✔ *2026-08-22 — decided into FR-MODEL-114 and FR-MODEL-115; the continuous-effect gate it turns on is W30's, which is Phase 2 work*, ~~OQ-MODEL-27~~ ✔, ~~OQ-MODEL-28~~ ✔ *both raised 2026-08-22 out of the two modelling decisions taken that day and **both decided the same day**, before the gate they were filed against — the first into FR-MODEL-120, the second into FR-MODEL-121 and FR-MODEL-122. Filing them here rested on a claim that held for one of them: "both have interim behaviour in place, so neither blocks" is true of `diagnostic`, which really is refused, and **false of the interaction**, whose skip-and-record leaves a sparse cross raising `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` out of `compute_gbm_diagnostics` (FR-MODEL-122). Deciding both early cost one day and turned an interim nobody had exercised into a measured defect with a remedy. W30 still owns the slices; what it no longer owns is the choice* | 13 (0 open) — *recounted 2026-08-23: this read `13 (2 open)` while every one of its thirteen ids was struck. The two it meant were decided on the day they were filed here, and the count was written from the intent to file rather than from the row* |
| **Before Phase 3** — *re-opened 2026-08-29* | ~~OQ-GOV-1..6~~ ✔ *2026-08-18*, ~~OQ-OVR-1~~ ✔ *decided 2026-08-15 — ADR-0006, and it changes what W14 builds in Phase 2 rather than waiting for Phase 3*, ~~OQ-MODEL-7~~ ✔ *evidence in Phase 3 (W31), never a block*, **OQ-RATE-7** *(raised 2026-08-29 from W11 Task 1.2)* | 9 (1 open) |
| **Before Phase 4** | ~~OQ-OPT-1..5~~ ✔, ~~OQ-OPT-6~~ ✔ *resolved 2026-08-14*, ~~OQ-MON-1..5~~ ✔, ~~OQ-DATA-4~~ ✔ *decided 2026-08-14 — out of scope*, ~~OQ-PLAT-8~~ ✔ *raised and decided 2026-08-23 out of the scheduling decision: an idempotency key naming a Job that already failed. FR-PLAT-12's 24-hour window is withdrawn, keys are permanent, and a terminally failed Job releases its key so the period can be attempted again (`07` FR-PLAT-64). Decided at this gate rather than deferred to it because W27 would otherwise build FR-PLAT-61 against an unanswered question; the code delta stays W27's* | 13 (0 open) |
| **Deferred / any time** | ~~OQ-OVR-3~~ ✔, ~~OQ-OVR-4~~ ✔ *both decided 2026-08-14*, ~~OQ-DATA-3~~ ✔, ~~OQ-DATA-5~~ ✔, ~~OQ-DATA-6~~ ✔ *all decided 2026-08-14*, ~~OQ-MODEL-2~~ ✔, ~~OQ-MODEL-4~~ ✔ *amended 2026-08-23 — the decision stands, its two-number evidence clause is withdrawn*, ~~OQ-MODEL-6~~ ✔ *all decided 2026-08-15*, ~~OQ-MODEL-31~~ ✔ *raised and decided 2026-08-23 out of that amendment: what evidence stands beside an interaction candidate, once a per-pair exposure share is shown to be `1.0` by construction — its **holdout strength ratio**, the ranker's own statistic recomputed on the holdout partition and published against the in-sample value (`02` FR-MODEL-128). Deferred no longer as a question; the panel that displays it is still unscheduled*, ~~OQ-MODEL-13~~ ✔ *2026-08-18 — reopened by its own trigger, the first consumer of an aggregate interval*, ~~OQ-DATA-10~~ ✔ *2026-08-19 — a deferral with a trigger (FR-DATA-52), raised in W5 and never placed here until decided*, ~~OQ-RATE-5~~ ✔ *raised 2026-08-19 in the FR-MODEL-96 slice and placed 2026-08-21*, ~~OQ-PLAT-2~~ ✔, ~~OQ-PLAT-4~~ ✔, ~~OQ-PLAT-5~~ ✔ *all decided 2026-08-23 on the maintainer's instruction to resolve them: no Dagster (FR-PLAT-61), no workspace quota (FR-PLAT-60), and a local-only identity provider behind an opt-in profile (FR-PLAT-58, FR-PLAT-59). The middle one is a **rejection**, not the deferral its recommendation asked for — that deferral's trigger had been dead since ADR-0006*, ~~OQ-PLAT-7~~ ✔ *decided 2026-08-22 and left unstruck here for a day*, ~~OQ-DATA-14~~ ✔ *raised 2026-08-24 in W6b — whether a Column Profile's `pii_class` of `NONE` records "classified as not personal" or "never classified", and the same silence on `semantic_type`. Placed here because no phase blocks on it: the default is already live on every ingestion path and the frontend already renders it, so the answer changes what a displayed value **means**, not whether a slice can start. It is on this table on the day it was raised — six questions before it, each reached a decision before reaching a gate row, and the rows above record that as the defect it was*, ~~OQ-PLAT-15~~ ✔ *raised 2026-08-24 in W6b — what `req-coverage.py` should do about three inflation modes that turned out not to be the three that were reported. Here rather than at a phase gate because it bears on every workstream close rather than on any one boundary: its live mode is clause-conflation, which no cheap instrument change reaches, so its legitimate discharge is a standing reporting rule plus a named §13 verdict on each conflated clause* ~~OQ-MODEL-43~~ ✔ *raised 2026-08-26 out of the FR-MODEL-102 ruling of that day — a surrogate's source is pinned by UUID while its slug-derived address resolves to the family's latest version; placed here because nothing blocks on it (the pin is exact; rendering and derived addresses are what is at stake)*, ~~OQ-OVR-13..16~~ ✔, ~~OQ-DATA-12..13~~ ✔, ~~OQ-DATA-15~~ ✔, ~~OQ-MODEL-42~~ ✔, ~~OQ-PLAT-10..11~~ ✔, ~~OQ-PLAT-13..14~~ ✔, ~~OQ-PLAT-16~~ ✔ *all placed 2026-08-26* | 32 (0 open) |

**2026-08-26 — OQ-MODEL-43 placed at Deferred.** *OQ-MODEL-43 raised 2026-08-26 out of OQ-MODEL-34's ruling — a surrogate's source is pinned by UUID while its slug-derived address resolves to the family's latest version; placed here because nothing blocks on it (the pin is exact; rendering and derived addresses are what is at stake).* The row entry keeps its note free of OQ ids, because the decision-gate check counts every id a row cell contains and naming OQ-MODEL-34 there would book a decided question as open — the table's other rows predate that rule, and their prose citations are the pre-existing drift this PR records rather than repairs.

2026-08-26 — the open half placed, the decided half recorded. Twenty open questions sat on no gate row; all are placed now — seven at Before Phase 1b (OQ-MODEL-35..41) and thirteen at Deferred (OQ-OVR-13..16, OQ-DATA-12/13/15, OQ-MODEL-42, OQ-PLAT-10/11/13/14/16). Before Phase 4 reads 13 (10 open): OQ-OPT-6 resolved 2026-08-14. Eight decided ids are recorded rather than placed, the pattern the rows above record as the defect it was — OQ-OVR-10, OQ-OVR-11, OQ-OVR-12, OQ-MODEL-32, OQ-MODEL-33, OQ-MODEL-34, OQ-PLAT-12, OQ-PLAT-17: each reached a decision without appearing on this table; the register is the record of each. Counts count the entry list, never prose citations; the id-free row-cell rule stands.

**2026-08-18 — the six `GOV` questions decided, and Phase 3's gate closes.** OQ-GOV-1 (the
audit chain stays per workspace and self-held, claimed as tamper-*evident* against modification
below the application, with an optional chain-head anchor — FR-GOV-40), OQ-GOV-2 (the IdP owns
identity and role membership, the platform owns scope — FR-GOV-41), OQ-GOV-3 (an Admin may
override a flag, and it leaves a permanent scar — FR-GOV-42), OQ-GOV-4 (`risk_tier` on Model
Family and Rating Algorithm, which the policy may key on — FR-GOV-43), OQ-GOV-5 (exactly two
mandatory Commentary Blocks, no default text — FR-GOV-44) and OQ-GOV-6 (TAS 200 v2.0 **does**
cover pricing — FR-GOV-45). All are Phase 3 obligations: a later phase is a spec change and not
code (`CLAUDE.md` §0).

**OQ-GOV-6 was not a design choice and was not decided like one.** The row said so — *"a lookup
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

**Every decision gate on this table is now closed except Phase 1b's, Phase 4's and the any-time rows.** Phase 1b's re-opened on 2026-08-22: deciding OQ-MODEL-23 and OQ-MODEL-24 surfaced two defects neither question had asked about, and a gate that closes over a question raised after it is a gate recording the wrong thing.
Phases 1a, 1b, 2 and 3 all read 0 open, while Phase 1a is still being built — which is the
order §10 exists to produce, and the first time the table has been in it.

**2026-08-18 (same day, at the maintainer's direction) — OQ-GOV-8 decided, and every gate
on this table is now closed.** An `expression` Custom Objective needs `custom_objective:author`,
distinct from `model:fit` and held by no built-in role by default (`06` FR-GOV-39). **Before
Phase 2 reads 10 (0 open)**, so Phases 1a, 1b and 2 are all decided while Phase 1a is still
being built. *(Corrected 2026-08-22: Before Phase 2 now reads 11 (0 open) with
OQ-MODEL-23 placed, and Before Phase 1b has re-opened at 18 (2 open). The sentence stands as
what was true on 2026-08-18. **Superseded later the same day**: OQ-MODEL-25 and OQ-MODEL-26
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

**2026-08-18 — OQ-GOV-8 deferred to Phase 2, with a trigger and an owner.** Whether an
`expression` Custom Objective needs an authoring permission distinct from `model:fit` is not
answerable yet, and the register says so rather than manufacturing an answer: it turns on how
much of the review an Objective Certificate can carry, which nobody knows until a
user-authored loss has been through one. **The deferral is the decision, and `06` FR-GOV-38 is
what makes it one** — the question must be answered *before* `expression_objectives_enabled`
may be lifted, and **W30 owns it** because W30 is the workstream that lifts the flag. A
deferral with a trigger, an owner and a written form binds something; a deferral with only a
phase attached is a note nobody is holding.

So **Before Phase 2 now reads 10 (1 deferred) rather than 10 (1 open)**, and no gate row on
this table is unowned. *(Superseded within the hour — the row reads 10 (0 open); the note
above records the decision. Left as written, because how briefly the deferral stood is
part of what the second look found.)* What is deferred is an *additional* control, not the only one:
FR-GOV-11 keeps the submitter out of the approval and `02` FR-MODEL-46 requires a non-author
Approver, both of which apply to an expression objective the day it exists. That is why
waiting is affordable — and stating it is what stops the deferral being read as a gap.

**2026-08-18 — the four Phase-2 design questions decided, leaving one.** OQ-RATE-3 (rate
tables as rows, spilling to parquet above a configurable cell count — `03` FR-RATE-62),
OQ-RATE-4 (one algorithm for the risk price, refund maths in a sub-graph mounted on `purpose`
— FR-RATE-63), OQ-RATE-6 (annual premium plus an optional `instalment_loading` rung; APR and
schedules stay downstream — FR-RATE-64) and OQ-PLAT-3 (one image now, a scoring image from
Phase 3 — `07` NFR-PLAT-11, **built**). **Only OQ-GOV-8 still gates Phase 2**, and it is
correctly waiting: it asks whether an `expression` Custom Objective needs its own authoring
permission, and `expression` objectives are themselves Phase 2.

Three of the four are **spec changes only**, which is the rule rather than a shortage of
appetite: a later phase's capability is not built early (`CLAUDE.md` §0). The fourth is not an
exception to that rule but an instance of a different one — OQ-PLAT-3's *decision* is a Phase
3 image, and what shipped is the **boundary that keeps that image cheap to build**, which is
worth nothing if it arrives with the image.

**Two defects the decisions found in the specification they were being written into.**
OQ-RATE-4's recommendation mounts its sub-graph on `purpose ∈ {mid_term_adjustment,
cancellation}` and **`cancellation` was not a value `purpose` had** — `03` §2 and §4.4 both
enumerated four — so the recommendation as filed keyed on something that did not exist. And
NFR-PLAT-11's first draft forbade `xgboost` and `lightgbm` on the scoring path, which `02`
FR-MODEL-62 contradicts outright: a GBM is scored by *loading its JSON booster*, so a boosting
library is a scoring dependency by design. Both were caught by checking the decision against
the spec it cited rather than against what sounded right.

**2026-08-18 (later the same day) — OQ-MODEL-14 closes the 1b gate.** A penalised GLM reports its standard errors and its interval as before, and every response carrying them now says which matrix they came from (`02` FR-MODEL-99, **built**). **Every question gating Phase 1b is decided**, three days after the gate was placed and while 1a is still open — which is the order this table exists to produce. What remains is Phase 2's five, Phase 3's six, Phase 4's eleven and four any-time.

The decision is worth one line of why, because the recommendation on file was a *sequencing*
rule rather than an answer — decide FR-MODEL-21 and FR-MODEL-63 together — and following it
is what produced the answer: both are read off one matrix, so refusing the interval would
have had to take the coefficient standard errors with it. A rule about *how* to decide,
honoured, decided it.

**2026-08-18 — five decisions, and the table was repaired to take them.** OQ-MODEL-10 (the
approximation is a Model, `02` FR-MODEL-96), OQ-MODEL-11 (a dislocation gate on
`approximation` mode, `03` FR-RATE-61), OQ-MODEL-12 (no continuous interaction operand, `02`
FR-MODEL-97), OQ-MODEL-13 (one interval kind until a named consumer, `02` FR-MODEL-98) and
OQ-GOV-7 (§3.3 is a floor, `06` FR-GOV-37, **built**). **Before Phase 1b now has one question
left**, OQ-MODEL-14 — *decided later the same day, which is what the note above records; this
sentence is left as it was written rather than corrected, because when the gate stood at one
is part of how fast it closed.*

**OQ-GOV-7 is gated at 1b and appears once.** It used to appear twice — the Phase 3 row
carried a parenthetical naming it, which reads as a placement to a counter that cannot tell
prose from a cell. Four other ids appeared nowhere at all: **OQ-MODEL-12**, **OQ-MODEL-13**,
**OQ-MODEL-14** and **OQ-GOV-8**, each raised in a spec, correctly mirrored into
`open-questions.md`, and invisible to the plan. Two of them were decided on the day they were
placed, which is the failure mode this table exists to prevent: a question the plan never saw
cannot be scheduled, and one nobody scheduled gets answered by whoever trips over it.
**OQ-MODEL-12 and OQ-MODEL-11 sit at Phase 2 while already decided**, because each names a
revisit that belongs against a rate table that exists; **OQ-MODEL-13** sits in *Deferred* for
the same reason, holding the trigger FR-MODEL-98 names. A decided row still needs a gate — it
is where the revisit is scheduled, not only where the answer was due.

**OQ-RATE-1 was the one question able to invalidate an accepted ADR. It has been answered**
— by a spike, not an opinion — and ADR-0004 survived
([`research/track-a-findings.md`](research/track-a-findings.md) F1).

**OQ-RATE-2 has also now been answered** by spike S2 — `exact` mode costs ~2 % of the
budget, so OQ-MODEL-3 remained a design choice rather than being decided by force. **It was taken on 2026-08-17**: both modes are supported, and the mode belongs to the
Rating Version rather than to the step (`03` FR-RATE-60). What an `approximation`-mode
version must *prove* before it may deploy was the part the question did not settle, and
is now OQ-MODEL-11 rather than an assumption.

**Every question that could only be answered with code has been.** What remains is
judgement, not measurement.

Six of the 1a/1b gate entries were raised *during* the phase rather than before it — by
driving the exit demo (OQ-DATA-7), by plan review 2 (OQ-OVR-6, OQ-PLAT-6), by auditing the
GLM spine (OQ-MODEL-8), and by building bandings and groupings (OQ-OVR-7, OQ-MODEL-9) — and
none of them reached this table on the day it was raised. All six were added on 2026-08-15,
the last two while resolving a rebase, which is not a reliable mechanism. **A question raised
in a spec belongs in this table in the same commit** — the `spec-change` skill now says so,
because `audit-docs.py` checks the spec ↔ register mirror and cannot see this table at all.
A gate row is only as good as its habit of being written down.

**2026-08-17 — the three `MODEL` questions were decided, and recounting this table found it
had been over-claiming since it was written.** OQ-MODEL-8 (a GBM's evidence obligation) and
OQ-MODEL-9 (supervised banding) closed against appended requirements and tests; OQ-MODEL-3
closed as above. Three ids reached no row at all: **OQ-MODEL-10** and **OQ-GOV-7** are gated
at 1b, and **OQ-MODEL-11** at Phase 2. OQ-MODEL-10's placement is the substantive one — it
was blocked on OQ-MODEL-3 and is now unblocked, and it must be answered before anything
references a transparency artifact by identifier, because `TransparencyArtifact` carries no
`status` and so cannot satisfy FR-OVR-14's approved-or-better pin check. OQ-GOV-7 moves
forward from Phase 3 for a plainer reason: its own recommendation says it is cheap to build
*once a second evidence kind exists*, and the transparency kind became checkable on the same
day. Both placements are proposals in §14's sense — a maintainer may move either row.

The recount is the finding the count column exists to produce. The **Before Phase 1b** cell
claimed 10 entries while naming 9, and had done so since it was written; the six other rows
were consistent. It now reads 11 because two ids were placed, not because one was found.
**Recount the row from its names — never decrement the number you found.**

**2026-08-15 — the six `MODEL` judgement calls were taken**, and none of them enlarged Phase 1:
expressions moved to Phase 2 while their certification machinery stayed here (OQ-MODEL-1);
the cheap prediction interval was refused outright rather than made optional (OQ-MODEL-2);
SHAP interaction detection ships as suggestion, not action (OQ-MODEL-4); credibility gained a
second method because the choice belongs per grouping (OQ-MODEL-5); the complexity gate is
unset by default because the judgement belongs to an Approver (OQ-MODEL-6); and proxy
detection became a Phase 3 deliverable that produces evidence and never a refusal (OQ-MODEL-7).
The register carries the reasoning; `02` §3 carries the obligations, as FR-MODEL-75..82.

**2026-08-15 — two `OVR` questions followed.** OQ-OVR-1 chose **deployment-per-tenant**, which
is the largest architectural commitment since ADR-0004 and is recorded as **ADR-0006**:
isolation becomes an infrastructure property rather than a promise that every query is
correct forever, at a cost that is linear in tenants and permanent. OQ-OVR-6 chose the
journey citation audit now and one end-to-end test per journey as its last module lands
(FR-OVR-17). Note what the first one moved: a question the table gated at Phase 3 turned out
to change what W14 builds in Phase 2, which is the argument for answering gates early rather
than at the boundary they are filed under.

**2026-08-21 — six questions decided, and the table gained the rows it was missing.**
OQ-OVR-9 (the audit cross-checks every §5.1 error-code table against `errors.py` — FR-OVR-19,
owner the maintainer, before Phase 1a's exit demo), OQ-DATA-10 (decided 2026-08-19 —
FR-DATA-52; the register row was stale and is brought into line), OQ-MODEL-15 (aliasing
entries are bare names — FR-MODEL-109, **delivered**: the authored contract corrected and the
pin deleted), OQ-MODEL-17 (a rebuild reuses the surrogate's stored numbers — FR-MODEL-110,
Phase 1b before its job-latency measurement), OQ-MODEL-21 (the LightGBM drop is recorded on
the fit — FR-MODEL-111, W5), OQ-MODEL-22 (GBM-referenced offsets next, then the scoring path
— FR-MODEL-112). **All thirteen rows the gate-table invariant reported missing are now
placed** — the six above, the six decided 2026-08-19 that had never reached the table
(OQ-OVR-8, OQ-DATA-11, OQ-MODEL-16, OQ-MODEL-18, OQ-MODEL-19, OQ-MODEL-20), and OQ-PLAT-7,
still open, on the any-time row. A question invisible to the plan gets answered by whoever
trips over it; this is the fourth time the `missing` half of the check has caught a batch,
and the first where the batch included questions still open.

**2026-08-23 — FR-DATA-50 and FR-DATA-51 delivered (W32-3), and what stays open beside them.**
Both were "Not delivered. Phase 1b, owner W6b". `GET /api/v1/datasets` now derives the status
badge and the last-validated date per request, storing neither, and `Dataset` carries a
non-null `owner_id` with an audited Admin-or-owner change route. FR-DATA-50 landed as **three**
fields rather than the two it named — its own "states which" clause needs the version beside the
date — which is recorded on the requirement rather than smoothed over. `01` §5.1's endpoint
table gained the `PATCH` row and `scope-audit.py DATA --endpoints` counts 38 of 38.

**Still open, and deliberately so:** `FR-DATA-52` is a decided deferral with **no owner, by its
own terms** — its trigger is a named reader asking for an exposure-ordered view, and assigning
it to a workstream would schedule work nobody has asked for. It appears in
`scope-audit.py DATA`'s unevidenced list beside the two delivered above and **should not be read
as a gap**; that adjacency is the whole reason this paragraph exists.

**Still open, and owned elsewhere:** `NFR-DATA-1` and `NFR-DATA-2` are budgets, not behaviour.
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
| **1a — Data Workbench** | ~26 % | 3 after W1 | **L** | ~~W1–W4~~ ✔ **all closed** + dataset views (W6a); the `validated` loop passes headless |
| **1b — Modelling Workbench** | ~21 % | 2 | **L** | W5–W7; ends at `wf-01` end to end. W6b also carries the frontend platform — browser auth, accessibility, and the workspace selector's shell control (its table, API and transport are W32's and OQ-PLAT-9's, split out 2026-08-23) — after plan review 1 |
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
| 1b | [`wf-01`](workflows/wf-01-dataset-to-model.md) end to end on freMTPL2 |
| 2 | [`wf-02`](workflows/wf-02-model-to-rating-version.md) end to end, plus `wf-04` phases A–D, meeting NFR-RATE-1 |
| 3 | [`wf-05`](workflows/wf-05-custom-objective-lifecycle.md) end to end, plus a dossier that survives external review |
| 4 | [`wf-03`](workflows/wf-03-rate-change-impact.md) end to end, plus `wf-04` phases E–H |

The workflow documents were written with timing tables for exactly this purpose.
