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

---

## 2. Where the project is

| | |
|---|---|
| **Phase 0 (Specification)** | Closed 2026-08-14 — 8 specs, 5 workflows, 5 ADRs, 31 contracts; `scripts/audit-docs.py` prints the current requirement count, which changes whenever an implementation proves the spec wrong |
| **Blocking Phase 1** | **Nothing.** All seven of Track C's decisions are taken — the last six (OQ-MODEL-1, 2, 4, 5, 6, 7) on 2026-08-15. What remains open gates Phase 2 or later (§10) |
| **Code written** | Phase 1a complete, Phase 1b started — the closure records in §6 are the authority, not this row |

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
| Restricted AST parser for the expression grammar | **Phase 1, W5** | Nothing left to research — `02` §4.6 specifies the grammar. This is build work, and the only place user input reaches the numerical core |
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
| ~~**S2 — `exact`-mode GBM latency**~~ ✔ **CLOSED 2026-08-14** | OQ-RATE-2 | **Comfortably viable** — p99 1.09 ms, ~2 % of the 50 ms budget. OQ-MODEL-3 stays a real design choice rather than being forced. `nthread=1` per request (NFR-RATE-14). |
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
| **OQ-MODEL-5** credibility standard | **1b** ✔ *decided 2026-08-15* | Both, limited fluctuation as the default, recorded per grouping (FR-MODEL-80) — so W5 builds two methods rather than choosing one |
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
| 5 Phase-2 decisions (OQ-RATE-3/4/6, OQ-PLAT-3, OQ-MODEL-11) | decisions | Before Phase 2 — OQ-RATE-2 decided by spike, OQ-MODEL-3 decided 2026-08-17 and OQ-MODEL-11 raised by it |
| Sustained-load test at 200 rps (S2 measured per-request only) | test | Phase 2 W11 |
| 6 Phase-3 · 11 Phase-4 · 4 any-time decisions still open | decisions | Per gate (§10) — OQ-MODEL-2, 4, 6, 7 and OQ-OVR-1 and 6 all came off this list on 2026-08-15 |
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

## 5. What cannot be retrofitted

**This is the most important section of this document.** Several capabilities belong to
later phases by ownership but must be built into Phase 1's foundations, because
retrofitting them is a rewrite rather than an addition.

| Must land in Phase 1 | Owning spec | Why retrofitting fails |
|---|---|---|
| **Append-only audit log, written in the caller's transaction** | `06` R2, FR-GOV-20 | Every write path must call it. Adding audit later means revisiting every mutation in the codebase and still having no history for anything already done. |
| **Artifact immutability + versioning + `parent_id`** | FR-OVR-1, ID-2 | If entities are mutable in v1, every artifact table needs a data migration and the historical record is simply gone. |
| **`model-schema` as the single source of truth** | ADR-0002 | Generated OpenAPI and TS types are trivial from day one and a large refactor once shapes exist in three places. |
| **The Job model with progress and cancellation** | FR-OVR-10, FR-PLAT-7..16 | Synchronous endpoints that later become jobs change every caller, including the frontend's whole interaction model. |
| **Decimal money discipline** | FR-OVR-7, `03` R2 | Retrofitting is a data migration *plus* a correctness audit of every computed figure ever displayed. |
| **`trace_id` propagation API → worker → core** | FR-OVR-3, `07` R4 | Cheap to thread through from the start; invasive afterwards. |
| **RBAC checks in the backend from the first endpoint** | `06` FR-GOV-2 | "We'll add auth later" reliably produces endpoints that assume no caller identity. |
| **Content-addressed blob store** | ID-4 | Changing storage layout later invalidates every stored reference. |

None of these require the *full* module. Phase 1 needs the audit **write path**, not the
audit explorer UI; the approval **state machine**, not the inbox. The user-facing surface
is Phase 3's job.

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
| ~~**W2**~~ ✔ | Platform core — jobs, blobs, settings, auth, health, tracing | ✔ **closed 2026-08-14** — see the closure record below |
| ~~**W3**~~ ✔ | Governance write path — audit log, RBAC, approval state machine | ✔ **closed 2026-08-14** — see the closure record below |
| ~~**W4**~~ ✔ | Data — ingestion, preparation, validation, profiling, reference data | ✔ **closed 2026-08-15** — see the closure record below |
| ~~**W7a**~~ ✔ | freMTPL2 data seed — the demo dataset through the real Job path | ✔ **closed 2026-08-15** — see the closure record below |
| ~~**W6a**~~ ✔ | Frontend — app shell, dataset views, validation report view | ✔ **closed 2026-08-15** — see the closure record below |
| ~~**W7b**~~ ✔ | Demo entrance — one command to a browser, with a derived guide | ✔ **closed 2026-08-15** — see the closure record below |
| ~~**Exit demo**~~ ✔ | Phase 1a's exit criterion exercised through `/demo` | ✔ **accepted 2026-08-15** — one command to a served page in 27 s, the failure loop on real data, two defects found. Exercised over HTTP by Claude; the maintainer accepted without driving it, deferring hands-on testing until more functionality exists |
| ~~**Exit gate**~~ ✔ | FR-DATA-41 (ingestion refuses a `direct_identifier` column) · FR-DATA-42 (append-only triggers on `validation_reports`, `profiles`, `validation_acknowledgements`) | ✔ **delivered 2026-08-15** — five injections, five caught. `blobs` left the list when building it proved it could not be append-only; the requirement was corrected rather than the table dropped |

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

Two runs so far: [review 1](#plan-review-1--at-w6as-close-2026-08-15) at W6a's close, and
[review 2](#plan-review-2--at-w7bs-close-and-before-phase-1as-exit-demo-2026-08-15) at
W7b's close and before the exit demo. Each proposal carries its own maintainer acceptance
line; two of review 2's are still pending.

After this has run twice the procedure becomes `.claude/skills/phase-review` (`CLAUDE.md`
§14). It has now run twice — writing that skill is the outstanding item.

### Phase 1a — exit demo accepted 2026-08-15

**Accepted by the maintainer. What it was accepted on is worth stating exactly**, because
the criterion's own words are "a person driving the screen", and this record first claimed
more than happened.

| | |
|---|---|
| The stack came up in one command | `uv run python scripts/demo.py`, **27 s** to a served page against NFR-PLAT-4's 300 s |
| The failure loop ran on real data | version 1 fails on 571 rows of genuine exposure above 1.0, promotion refused with `VALIDATION_HAS_FAILURES`, version 2 reaches `validated` after one preparation step |
| The screens were exercised **by Claude, over HTTP**, not by a person in a browser | the entrance, the guide, the dataset list, the version timeline |
| The maintainer **accepted it without driving it**, deferring hands-on testing until more functionality exists | their words: *"I cannot really test anything on the demo platform, I will test more after more functions added"* |

So the exit criterion's mechanical half is met and evidenced; its *human* half is
outstanding by the maintainer's own choice, and the phase closes on that basis rather than
on a claim nobody made. The entrance exists and works, which is what W7b owed; the person
driving it comes when there is more to drive.

**Two defects found by exercising it, neither by any test.** That is the argument
FR-PLAT-53 makes for the entrance, and it holds even though the exercising was done over
HTTP rather than in a browser:

| Found | State |
|---|---|
| The dataset list's **latest version** column was empty for every row — the list called `to_schema(row)` with no version while the detail route passed one. `01` §5.3 names it as one of four columns the list must show, and it is the demo's first screen | **Fixed**, with the injection proof |
| **Nothing in the platform ever sets a version to `failed`.** `DatasetStatus.FAILED` is in the enum and in `VALID_DATASET_TRANSITIONS`, and no code path transitions to it — so a version whose first validation fails rests in `validating`, which every status screen reads as "still running" | **OQ-DATA-7**, open, recommendation `failed`; specified as **FR-DATA-43**, not implemented |

Neither was visible to an audit. The first was a column nobody asserted; the second is a
*state* rather than a requirement, so no marker could be missing and no coverage number
could drop. A person opening the screen saw both in under a minute.

### Plan review 2 — at W7b's close and before Phase 1a's exit demo, 2026-08-15

`CLAUDE.md` §14's second run. Both triggers fire at the same moment: W7b closed, and the
exit demo is the next milestone. Five questions, in order, each answered — **including the
ones whose answer is "no change"**.

This review is short on questions 1 and 4 on purpose. The independent audit that ran hours
earlier is the evidence for both, and repeating its work would be re-deriving from the same
sources rather than testing the plan.

**1. Completion — derived, not recalled.**

| Module | §5.1 endpoints published | Requirements evidenced |
|---|---|---|
| `DATA` | **34 / 34** | 48 / 52 |
| `PLAT` | 18 / 21 | 40 / 65 |
| `GOV` | 11 / 20 | 23 / 43 |
| `OVR` | — | 8 / 25 |

423 requirements specified, 121 marked (28.6 %) — the phase covers `DATA` and the `PLAT`
and `GOV` foundations under it, which is what Phase 1a's rows claim and no more. `DATA`'s
four unevidenced requirements each carry a verdict: NFR-DATA-1/2 measured rather than
tested, FR-DATA-41 and FR-DATA-42 appended this morning and owned by W6b. `PLAT`'s three
unpublished endpoints are W14's environments routes.

**The plan and the derivation now agree** — because the audit made them agree this morning,
not because they always did. Three closure records claimed more than they established and
were rewritten; that reconciliation is recorded above and is not repeated here.

**2. Omission — what the phase needs that no row names.**

*The workflow journeys are evidenced by nothing.* `docs/workflows/wf-01…05` are the
cross-module contracts — a module spec says what one module does, a workflow says what
actually happens — and **no test in the repository cites one**. Phase 1a's exit criterion is
a slice of `wf-01`, covered by `test_data_jobs.py::test_the_failure_loop_then_validated`,
which does not name it. `audit-docs.py` check 14 reports "workflow coverage: DATA 50 %",
which measures whether the workflow *documents mention* a requirement id — not whether the
journey runs. No workstream row owns "the journeys work", and none of the five has been
read against the code since it was written.

This is the same shape as the audit's other findings: a number exists, it is not measuring
the thing its name suggests, and nobody had looked.

> **Recorded as OQ-OVR-6** *(2026-08-15)*, with a recommendation: a mechanical audit that
> every journey step cites an endpoint, requirement or artifact that exists — the
> `--endpoints` idea one level up — **now**; one end-to-end journey test per workflow as its
> modules land; and explicitly **not** a marker on an existing test, which would claim a
> journey where one slice is covered. A journey belongs to the workstream that completes
> the last module it touches, so `wf-01` is W5's to finish. Phase 1a's exit demo walks its
> data half and is that half's first evidence.
>
> **Accepted 2026-08-15**, unchanged, as **FR-OVR-17**. Writing it down sharpened two things:
> the audit's real content is **endpoint and `pricing-core` function** citations, because
> requirement ids and `§` references are already checked; and the ownership rule needs no
> new machinery, since "the workstream that completes the last module" is in every case the
> phase whose exit criterion names that journey (§12).

*Two model/contract divergences have no owner.* `Dataset` carries no status, validated-at or
owner while `01` §5.3 asks the dataset list to display all three; `ColumnProfile` has no
`histogram` while `01` §4.4 **and** `docs/contracts/schemas/profile.schema.json` both define
one. W6b cannot build those view items until someone says which side is wrong, and no row
owns the deciding.

*Not omissions:* Playwright E2E is deferred with a stated reason, `pipelines/` is W7's, and
the six `PLAT` endpoints remain W14's.

**3. Skills and research — re-run, not appended to.**

`docs/skills-map.md`'s pandera row was retired this morning (it read ★★ **Verified** for a
library this repository depends on nowhere). Nothing else in the map is now ahead of or
behind the code. No new external skill is proposed, and none would be installed without the
maintainer's approval.

One gap, from this week rather than from the map: **`close-workstream` does not warn that a
proof can pass for the wrong reason.** §13 rule 4 requires a check be shown to fail on
deliberately broken input. The catalogue check was shown exactly that — and the injection
deleted an id from a *docstring*, so it proved the counter could count while the counter was
counting prose. The skill should say that the injection must break the thing the check
*claims* to measure, not merely something the check happens to read.

`close-workstream` also carries no `Verified` date, alone among the eleven written here.

**4. Document drift.**

Repaired this morning across three commits: the specs now describe what was built, the three
closure records say what the audits establish, and `CLAUDE.md` §2's tree is accurate. What
remains unchecked is `docs/workflows/` — see question 2 — along with `docs/README.md` and
`docs/phase-0-status.md`, neither of which has been read against the repository since Phase
0 closed.

**5. Shape — two proposals.**

*Proposal A — Phase 1a cannot exit as its criterion is written.* §6's exit reads: "a
freMTPL2 dataset version reaches `validated`, including at least one deliberate round
through the failure loop. **The retrofit list (§5) is fully in place by the end of 1a** —
that is the phase's other, quieter deliverable." The first half holds and is now drivable by
hand. The second does not: FR-DATA-42, artifact immutability, is on that list and is
enforced by nothing — `frozen=True` is a rule about one process, and an audit rewrote 190
stored reports in a single statement. It is owned by W6b, in Phase 1b.

> **Recommendation:** land **FR-DATA-41 and FR-DATA-42 before the exit demo**, keeping the
> criterion as written. They are small — a check at ingestion and four append-only triggers
> with their broken-input proofs — and everything Phase 1b builds sits on artifacts that
> nothing currently protects. The alternative, amending the criterion to exclude
> immutability enforcement, is coherent but should be chosen deliberately and with the risk
> stated, not arrived at by the demo happening first.
>
> **Maintainer accepted 2026-08-15.** FR-DATA-41 and FR-DATA-42 are a **gate on Phase 1a's
> exit demo**: the criterion stands as written, and the demo does not run until artifact
> immutability is enforced in the database rather than asserted in Python.
>
> The bookkeeping is stated rather than tidied away: **W6b's row still names both
> requirements**, and W6b is a Phase 1b row. The work therefore lands in Phase 1a while its
> nominal owner sits in 1b. That is the maintainer's decision, taken twice; recording it
> this way keeps the record honest about where the work happened, which matters more than
> which row it hangs from.

*Proposal B — W6b is now three workstreams in one row.* It carries `02` §5.3's factor
workbench, model detail and diagnostics — a full frontend workstream on its own — plus
browser authentication (FR-PLAT-55), accessibility beyond semantics (NFR-OVR-10), workspace
selection, the audit's six missing `01` §5.3 Contents items, threshold editing, and the two
enforcement gaps. **The last two are not frontend work at all**, and a row whose scope spans
a Vue view, an OIDC flow and a database trigger is a row nothing can be said to have closed.

> **Recommendation:** split the non-frontend half out under its own id when Phase 1b is
> planned, leaving W6b the views and the browser. No id is proposed here — naming one is
> the maintainer's, and the last two attempts at it cost two corrections.
>
> **Maintainer accepted 2026-08-15.** The non-frontend half splits out when Phase 1b is
> planned; W6b keeps the views and the browser. The id is assigned at that point, not here.

*No change* to the phase boundaries, to W5, to W7's remaining modelling half, or to Phases
2–4. Nothing this review found argues for re-cutting them.

### Independent audit — 2026-08-15, and what it changed

Five auditors ran over Phase 1a's closed work, none of them allowed to read the closure
records they were auditing: each derived what should exist from the specs and then went
looking. The maintainer asked for it after noticing that every audit so far had been a
self-audit — every one of these five PRs merged with **zero reviews**.

**No security holes.** Separation of duties holds in three independent layers, workspace
isolation refuses cross-tenant ids indistinguishably from missing ones, secrets are never
returned, the dev identity grants no permissions and never reaches the production bundle.

**The finding was consistent across all five: the code mostly does what it says; the
records and checks claimed more than they establish.**

| Claim | What was true |
|---|---|
| "38 of 38 catalogue rules" | the check counted ids **in prose**; one docstring reading `VR-ACT-1/2/8` became three, two of which appear in no source file. The truthful count is 1, and that one is an error message |
| "all 7 of `01` §5.3's views" | true of the router; **6 of their 27 Contents items** are missing — lineage graph, histograms, PSI selector, status badge, last validated, owner |
| the frontend contract-drift check | ran `git diff` on a git-ignored path that CI creates in the same step. It could not fail |
| "a renamed heading breaks the guide loudly, and the test is in the gate" | it did not: two specs were covered by accident, five and the roadmap by nothing |
| FR-DATA-13's refusal, FR-DATA-15's immutability | specified, cited, and enforced nowhere |
| pandera as the Layer-1 mechanism | named in four places; a dependency of nothing |

**Three tests proved nothing**, shown by injection: authorisation was tested on three of
fifty-nine operations and a downgraded permission left all 609 green; the acknowledge route
had no HTTP test and swapping its two path parameters passed; the determinism fixture held
one rule, so randomising result order passed.

**What it changed**, in two commits:

- **Tier 1** (`fix/audit-tier-1`) — the checks that could not fail, and the tests that
  proved nothing. Each fix demonstrated against the injection that used to pass.
- **Tier 2** — this spec upgrade. The specs now describe what was built (pandera withdrawn,
  the rule-format params corrected, the reference publish lifecycle declared, `06`'s
  authentication-only routes stated, §5.2's signatures corrected) and carry the two
  obligations the code does not meet as **FR-DATA-41** and **FR-DATA-42**, unevidenced and
  owned by **W6b** — and **delivered the same day** as Phase 1a's exit gate (plan review 2).
  Artifact immutability stopped being a convention on 2026-08-15.

**Tier 3, done 2026-08-15: the closure records for W4, W6a and W7b are rewritten.** Each had
measured a proxy — a route exists, a marker exists, an id appears — and reported it as the
thing. The corrections are made *in place with the original claim shown*, not by quietly
restating the record: W4's "38 of 38 catalogue rules" against what the check now reports,
W6a's seven views against §5.3's twenty-seven Contents items, W7b's "a renamed heading
breaks it loudly" against the auditor's rename that it did not catch.

The old wording is kept beside the correction on purpose. A record that silently becomes
right destroys the evidence of what was believed, which is the thing `CLAUDE.md` §0 says a
governed system cannot afford to lose — and these records exist to be the evidence.

`CLAUDE.md` §14 now makes the specification the plan review's main target at every stage
boundary, for the reason this audit demonstrated: a divergence left in a spec is a defect
the next workstream inherits and builds on.

### W7b — The demo entrance: closed 2026-08-15

**Scope, derived from `07` §3.9 before writing anything: two requirements** — FR-PLAT-53
(one documented command from a clean checkout to an authenticated browser) and FR-PLAT-54
(a guide to what is testable, derived rather than written). Both were added by `NT-0002`,
accepted 2026-08-15, whose deliverable was *spec change first*; this is the code half.

Split from W7 into Phase 1a for the reason W7a was: the entrance needs no model, and
Phase 1a's exit demo needs the entrance. What remains in W7 is the half that needs a
fitted model.

| Deliverable | Evidence |
|---|---|
| One command | `uv run python scripts/demo.py` — compose, migrations, freMTPL2 seeded through the real Job path, API, frontend, development identity for the seeded workspace, and the URL |
| The entrance | `/demo`, listing what is built, what is not, and the routes that can be opened without an id |
| The derived guide | `GET /api/v1/demo/guide`, built on every request from four files |
| One switch | 404 from the whole surface where `dev_auth_enabled` is false, refused **before** authentication so the answer is "does not exist" rather than "authenticate and retry" |

**Derived, and therefore incapable of going stale.** FR-PLAT-54 says the guide must not
restate capability from memory. It restates nothing at all: every line is one file agreeing
with another —

| Section | Source | The claim it makes |
|---|---|---|
| Views | each spec's §5.3 table | what the design says exists |
| — built? | `frontend/src/router/index.ts` | the router routes that path |
| API | `docs/contracts/openapi/generated.json` | the published surface (FR-PLAT-48) |
| Workstreams | this file's phase status tables | the roadmap's own words, not a second judgement |

There is no stored copy, so there is no drift check to remember to run.

> **Corrected 2026-08-15, the day after this record was written.** The sentence that stood
> here — "a renamed heading breaks it silently, and `test_demo_guide.py` is that check, in
> the gate" — **was false.** An auditor renamed `07`'s §5.3 heading and the roadmap's
> status heading: six views and *every* workstream vanished from the guide, with the docs
> audit and the whole suite green. The test asserted that `/data` and `/reference` existed,
> so `01` and `02` were protected by accident and `03` to `07` by nothing.
>
> The check is real now and derived from the files: every spec that declares a view table
> must contribute one, and the roadmap must yield workstreams. Both injections fail loudly.
>
> Two more claims on this page were overstated the same way, and are fixed in the same
> commit: the page reported "**63 endpoints published**" with no denominator while 85
> declared routes did not exist, and "**7/7 workstreams closed**" — a 100 % signal for a
> plan four phases from done, because only Phase 1a has a status table. It now reads 63 of
> 148, names the phases with no status table, and does not count a route inside a `//`
> comment as built.

Today it reports **8 of 51 views built** (the entrance is now declared in `07` §5.3, so it
appears in its own guide), 63 of 148 endpoints published, and Phase 1a's workstreams alone.
Naming what is *not* built is the point: a page showing only what works invites the reader
to assume the rest works too.

**NFRs measured, not asserted** (NFR-PLAT-4: a usable seeded state in < 5 min).

| Measured | | Budget |
|---|---|---|
| Cold — `compose down` first, images cached | **24 s** | 300 s |
| Warm — containers already up | **19 s** | 300 s |

> **Caveat, added 2026-08-15.** Both numbers were measured before `scripts/demo.py`
> refused a held port, and the measurement path was not self-verifying: `wait_for` returned
> on *any* answer, so a run could time a server the previous run had left behind. One such
> false reading was caught during the work (a "5 s" that was a stale probe); these two were
> taken with the ports verified free first, which is why they stand. The command now
> refuses a held port before starting anything, so a repeat measurement cannot make that
> mistake. NFR-PLAT-4 remains **measured, not tested**, and `scope-audit` correctly lists
> it among PLAT's unevidenced requirements.

Both include a 60 000-row seed through the real Job path, both versions, the validation
failure loop and the acknowledgement. The full 678 013-row seed adds ~10 s (W7a's record).

**Three defects, all found by running it rather than by testing it.** This is the whole
argument for FR-PLAT-53: a passing test and a person driving the thing are different
evidence.

- **Ctrl-C left the frontend running.** `pnpm` spawns `sh -c vite`, so signalling the
  direct child stopped the shell and orphaned the server; the next run then found port 5173
  held and failed for a reason that looked unrelated. Fixed with `start_new_session` plus
  `killpg`, and confirmed by watching both ports go free.
- **Vite silently moved to another port** when 5173 was taken — and the command then
  printed a URL for a server it had not started, with a different identity, answering
  happily. `--strictPort` makes the clash an error.
- **The banner never appeared** when stdout was a file: Python buffers, the subprocesses do
  not, so step headers printed after the output they introduced and the final "open this
  URL" sat in the buffer. Every print is flushed.

**Not delivered by W7b:**

| Item | Verdict |
|---|---|
| A browser session authenticated by OIDC | **Not started** — FR-PLAT-55, owned by W6b. The entrance uses the development identity the dev proxy injects, which is what FR-PLAT-53 asks for and no more |
| The modelling half of the demo | **W7**, where it belongs: a fitted GLM, a rating version, `wf-01` end to end |
| A guide covering more than views, endpoints and workstreams | Deliberate. Each section is a file agreeing with another file; a section without such a source would be the hand-written list FR-PLAT-54 exists to prevent |

### Plan review 1 — at W6a's close, 2026-08-15

The first run of `CLAUDE.md` §14, raised as `NT-0001`. §13 asks whether a workstream did
what it said; this asks whether the plan still says the right thing. Five questions, in
order, each with a written answer — **"no change" included**, because a silent question is
indistinguishable from one nobody asked.

**1. Completion — what is actually done, derived from the specs.**

`scope-audit.py` and `req-coverage.py`, not recollection. Phase 1a's workstreams W1, W2,
W3, W4, W7a and W6a are closed with records on this page. `DATA` stands at 48/50
requirements (the two are measured NFRs), **33/33** endpoints and **38/38** catalogue
rules; `PLAT` is unchanged since W2 at ~35 of 61 with six endpoints owned by W14.

One disagreement with the plan, and it is the finding: the W6a row said "app shell,
dataset views, validation report view" — three items — while `01` §5.3 names **seven**
views. The row was written before the spec's view table was read against it. All seven
shipped, so the plan under-described the work rather than the work under-delivering; the
row is left as written and the closure record carries the correction, as W2's and W4's do.

**2. Omission — what the phase needs that no row names.**

*Browser authentication.* No workstream row mentions it. `07` §3.7 specifies the API side
completely and the client side not at all, and the gap was invisible from either end: the
backend's tests authenticate through dependency overrides, the frontend's stub `fetch`.
A real browser got 401 on everything. Raised as **OQ-PLAT-6** with a recommendation
(PKCE), fixed for the dev loop only.

*The pattern behind it.* Three of this workstream's six API findings — the version
timeline, the approve route, the reference read routes — were endpoints the spec's §5.1
table never declared. `scope-audit.py --endpoints` compares that table against the
published contract, so **an endpoint missing from both reads as complete coverage**. This
is the same shape as §13's "requirement coverage is not interface coverage", one level up,
and the honest mitigation is the one used here: derive the surface from what §5.3's views
must *do*, not from what §5.1 lists.

*Not an omission:* `pipelines/` remains correctly assigned to W7, and Playwright E2E is
deferred to W7 for a stated reason rather than forgotten.

**3. Skills and research — re-run, not appended to.**

`docs/skills-map.md`'s frontend rows survive contact with the code: Vue 3, Router, Pinia,
Tailwind, ECharts, openapi-typescript and Vitest are all cited and all still accurate.
`.claude/skills/vue-frontend` gains the development-identity procedure, which is exactly
the kind of non-obvious dev-loop step §12 exists to capture — it cost an entire workstream
before anyone noticed.

Two rows are now *ahead* of the code rather than behind it: TanStack Table and Vue Flow
are declared and not installed, which is right for their phases. One is behind: Pinia is
installed and registered with no store, because nothing has yet needed to outlive a route.
No skill has gone stale. No new external skill is proposed — and none would be installed
without the maintainer's approval in any case.

**4. Document drift.**

`CLAUDE.md` §2's `frontend/` mark and its "add with the code" note on `frontend.yml` were
both stale and are corrected in this PR. `01` §5.1 now carries four dated amendments from
W6a's findings. `open-questions.md` gains OQ-PLAT-6. The roadmap's own Phase 1a percentage
("~26 %") is an estimate from before any code existed and is left alone: it is a planning
figure, and re-deriving it per workstream would make it a second progress table
disagreeing with the one above it.

**5. Shape — are the remaining phases still cut in the right place?**

Yes, with one proposal.

*No change* to the 1a/1b split, to W5–W7, or to any phase boundary. Taking W7a (the data
seed) before W6a was the right call and the reason W6a rendered real data from day one;
nothing suggests a second such reordering is needed.

*Proposal — three items name `W6b` as their owner and W6b's row does not cover them.*
NFR-OVR-10's tabular chart fallback, browser authentication once OQ-PLAT-6 is decided, and
the frontend half of governance surfacing all point at W6b in closure records, while the
row itself reads "factor workbench, model detail, diagnostics" — modelling views only. An
owner naming a scope that does not include the work is how work becomes nobody's.

> **Correction, 2026-08-15.** As first written this said W6b "is not yet a row and should
> be". It is a row, at Phase 1b, and had been since the 1a/1b split; the review missed it.
> The substance survives — the three items still had no owner — but the change is to
> **extend** W6b, not to create it. Recorded rather than edited away, because a review that
> quietly fixes its own premise leaves nobody able to tell what was believed.

> **Recommendation:** extend `W6b` to `Frontend: factor workbench, model detail,
> diagnostics — **and the frontend platform**: browser authentication (FR-PLAT-55),
> accessibility beyond semantics (NFR-OVR-10), workspace selection`. It gains a dependency
> on OQ-PLAT-6 being decided. Spec and plan only; no code follows from a review
> (`CLAUDE.md` §14 rule 3).
>
> **Maintainer accepted 2026-08-15**, together with OQ-PLAT-6's recommendation (PKCE in the
> SPA for Phases 1–2, now FR-PLAT-55). Applied to W6b's row and to the Phase 1b table
> below.

### W6a — Frontend Data Workbench: closed 2026-08-15

**Scope, derived from `01` §5.3 before opening any frontend file: seven views**, plus the
one seam `CLAUDE.md` §2 defines — `model-schema` → `docs/contracts/` → generated client —
and the API conventions `00` §5 requires every caller to honour (the single error shape,
cursor pagination, `202`-plus-Job, the idempotency key).

W6a owns no `FR` of its own: the frontend is where other modules' requirements become
visible, so its evidence is the views and their tests rather than markers. That is also why
the closure below leans on the two audits that *are* derivable — endpoints and catalogue —
and on what building the screens found in the API beneath them.

> **This table was rewritten on 2026-08-15**, after an independent auditor read `01` §5.3's
> **Contents** column against the components. The version it replaces listed seven views
> and, as their "evidence", restated the Contents column — including four items that are
> not built. Every view is routed and none is a stub; that is a fact about the router, and
> the record reported it as a fact about the screens.
>
> **Six of the twenty-seven Contents items are missing**, and three of the six have a
> working backend endpoint and a dead client wrapper.

| Deliverable (`01` §5.3) | Route | Built | Not built |
|---|---|---|---|
| App shell + generated client | — | client generated from the committed contract; no hand-written shape in `src/` | the CI drift check was inert until 2026-08-15 — it diffed a git-ignored path. `type-check` against the fresh client is the check now |
| Dataset list | `/data` | name, line of business, territory, currency, latest version | **status badge**, **last validated**, **owner** — and `Dataset` carries none of the three, so §4.1 never defined what §5.3 asks to display |
| Dataset detail | `/data/:slug` | version timeline (newest first, tested), rule set link in both states, data dictionary editor for `description` and `pii_class` | **lineage graph** — `getLineage()` exists, is typed, and is called by nothing while `GET …/lineage` serves it. `semantic_type` is read-only; `unit` and `reference_table` are not rendered |
| Version detail | `/data/:slug/v/:version` | all five: table inventory, row counts, totals, schema viewer, rejected-rows drawer | — (the drawer's populated branch is untested: both fixtures have zero rejects) |
| **Validation report** | `…/validation` | all six, and the interaction requirement genuinely holds — DOM order asserted, not presence | the offending sample is a `<ul>`, not the table §5.3 names; `empty_layers` is surfaced on the rule-set screen and not on this one |
| Profile | `…/profile` | per-column cards; one-way charts with exact Poisson CI whiskers (ECharts) | **histograms** — and `ColumnProfile` has no `histogram` field while `01` §4.4 *and* the committed JSON schema define one. **PSI comparison selector** — `compareProfiles()` has no caller, and `psiBand(null)` colours the dtype label, which reads as PSI support and is not |
| Rule set editor | `/data/:slug/rules` | rules by layer, enable/disable (full-membership round-trip tested), severity override, custom-rule builder with dry-run | **threshold editing** — thresholds render read-only; changing one means retyping the whole rule into the builder |
| Reference tables | `/reference` | all four: table list, version timeline, effective-date viewer, lookup debugger | — **nothing wrong found in this view** |

**Gate (local, 2026-08-15):** ruff clean · mypy --strict on 84 source files · import-linter
3 kept / 0 broken · **591 python tests** · 7 generated contracts match · docs audit 20/20 ·
req-coverage · eslint `--max-warnings 0` · `vue-tsc --build` · **75 frontend tests** ·
`pnpm build`.

| `scope-audit.py DATA …` | At W4's close | Now |
|---|---|---|
| requirements | 48 / 50 | **48 / 50** (NFR-DATA-1/2 measured, not tested — W4's verdict stands) |
| `--endpoints` | 28 / 28 | **33 / 33** |
| `--catalogue VR` | 38 / 38 | **38 / 38** |

**What building the screens found in the API — six defects, none in a view.** This is the
workstream's most useful output and the reason a frontend is not merely a rendering of a
finished backend:

| Found | Was |
|---|---|
| `GET /datasets/{slug}/versions` | §5.3 requires a version timeline; §5.1 offered only `latest_version`, so a client drew it one request per version |
| `source_names` on `DatasetTable` | The table inventory could not name its sources |
| `empty_layers` on `ValidationRuleSet` | A plain `@property`, so it never reached the contract — FR-DATA-16's warning had nothing to surface, while `ValidationReport` beside it carried the same list as a field |
| `POST /validation-rules/{id}/approve` | Absent. A rule could be authored, dry-run and submitted, then sit in `review` for ever — and a Rule Set refuses anything not `approved`, so nothing authored through the API could ever be used |
| `rules` in the rule-set replace body | Took bare ids, so `enabled` and `severity_override` were unreachable and the "an override may only raise" invariant guarded something no caller could attempt |
| Three reference read routes | The surface was write-plus-lookup; §5.3's table list, timeline and effective-date viewer had nothing to call |

Each landed as a spec change **and** the code, in one commit, with the amendment dated in
`01` §5.1 — because which of the two was wrong is the thing a governed system cannot
afford to lose (`CLAUDE.md` §0).

**Enforcement proven, not assumed** (§13 rule 4). Every claim a test makes was broken on
purpose first:

- the rule-set editor's carry-through — rebuilding the replace body from ids alone
  re-enables every other disabled entry; the test goes red
- `waitForJob` — returning the first poll instead of looping makes the builder submit a
  rule whose dry run had not finished
- the severity-downgrade guard — removing it turns a 409 into a 500 from
  `RuleSetEntry`'s own validator, which is *why* the service-level refusal exists
- `covers_to` — computed as `max(effective_to)` it reports a table that never expires as
  expiring in July
- the reference view's opening version — the newest rather than the newest **published**
  shows a draft no quote can have used

**The one thing that had never been exercised: the browser could not authenticate.** The
SPA sends no credential, and the platform refuses an unauthenticated request (`07` §3.7),
so a real browser got 401 on every request while all seven views and their tests passed —
the tests stub `fetch`, and nothing touched the transport. Confirmed against a live server
(`401` direct), fixed for the dev loop by injecting the development identity headers in the
**Vite proxy** — never in `client.ts`, because a header the browser sets is a credential the
user can edit in devtools and a code path that would ship in the production bundle
(`grep` of `dist/`: zero occurrences). The seed now prints the two ids. Real browser
authentication is **OQ-PLAT-6**, open, recommendation recorded.

**Not delivered by W6a:**

| Item | Verdict |
|---|---|
| Browser authentication | **Not started, and correctly so.** OQ-PLAT-6 was open when W6a closed; it was decided the same day — PKCE in the SPA, **FR-PLAT-55**, owned by W6b. The dev proxy remains a dev loop, named so it cannot be mistaken for a mechanism |
| Playwright E2E | **Deferred to W7.** `01` §5.3's journeys are worth one E2E each *once the demo entrance exists*; before that an E2E asserts a fixture |
| Pinia stores | **Registered, unused.** No state has yet needed to outlive a route: every view takes props and fetches its own data. The first store arrives when something must survive navigation — the PSI comparison selector, or a workspace selector, which W6b now carries |
| TanStack Table, Vue Flow | **Later phases** (`03` §5.3). Declared in `skills-map.md`, not installed |
| Accessibility beyond semantics | **Partial.** Tables carry `aria-label`, alerts carry `role`, and every test queries by role or label — which keeps the semantics honest. NFR-OVR-10's tabular fallback for charts is **not** built; owner W6b |
| `07` §5.1's six `PLAT` endpoints | Unchanged from W2's record — still owned by W14 |
| **Six §5.3 Contents items** | **Added 2026-08-15.** Dataset status badge, last validated, owner; lineage graph; histograms; PSI comparison selector. Plus threshold editing in the rule set editor. The original record did not list them because it audited routes and not Contents. Owner: **W6b**, except the two blocked by a model/contract divergence (owner/status/validated, and `histogram`), which need a spec decision first — recorded as unresolved in `01`, not silently designed around |
| **Two unresolved model/contract divergences** | **Added 2026-08-15.** `Dataset` has no status, validated-at or owner while §5.3 asks to display all three; `ColumnProfile` has no `histogram` while `01` §4.4 *and* `docs/contracts/schemas/profile.schema.json` both define one. Four other divergences from the same fortnight got dated amendment notes; these two were built around in silence, which is the `CLAUDE.md` §0 failure the notes exist to prevent |

**Retrofit list (`docs/roadmap.md` §5):** unchanged by W6a. The frontend consumes the
contract; it does not touch audit-in-transaction, artifact immutability, integer money or
the Job model. Money crossing into TypeScript is handled the one way `vue-frontend`
records: minor units are integers formatted at the edge, exact decimals stay strings and
are never parsed, and the two `_minor` fields that are float **ratios** are rendered as
statistics rather than currency — with a type-level test, because `expectTypeOf` erased at
runtime and passed while asserting the wrong thing.

### W7a — freMTPL2 data seed: closed 2026-08-15

The data half of W7 (`07` FR-PLAT-37), taken before W6a so the frontend has real data to
render and so the platform meets a dataset nobody generated. Phase 1a's exit criterion is
now runnable rather than only tested:

```bash
uv run python examples/fremtpl2/fetch.py && uv run python examples/fremtpl2/seed.py
```

**678 013 rows, two versions, 13.4 s end to end**, driving real Jobs through
`execute_job` — the path a worker takes in production, not the services underneath it.

| | Result |
|---|---|
| v1, the file as uploaded | **fails** — 571 rows carry an exposure up to 2.01 (VR-ACT-2). Promotion refused with `VALIDATION_HAS_FAILURES` |
| v2, one preparation step later | `pass_with_warnings` — 125 claims ≥ €35 630 flagged for large-loss treatment and **not removed**; acknowledged by an actuary; **`validated`** |

The 571 figure agrees with an independent `awk` count over the raw file, and nothing about
the failure is injected: freMTPL2's exposure anomaly is in the file as published.

**Measured on real data** — corroborating rather than replacing W4's synthetic
extrapolations:

| | 678 013 rows | → 10 M | Budget |
|---|---|---|---|
| Ingest + prepare + profile | 2.9 s | 43 s | 900 s (NFR-DATA-1) |
| Validation, 9 rules | 0.3 s | 4.4 s | 600 s (NFR-DATA-2) |

#### Three defects in W4, found by real data after W4 closed

Recorded here rather than by amending W4's record: the record states what was known when it
was written, and this is what a real dataset was always going to add.

| Defect | Resolution |
|---|---|
| **`allowed_values` read `values` where `01` §4.5 names the parameter `allowed`.** Its declared domain was therefore always empty, so it **failed every row** — naming as offenders the very values the author had allowed. It refused a 50 000-row dataset on the first run of the seed | Both names accepted, `allowed` preferred; an absent domain now **skips**. `case_sensitive` implemented, which §4.5 also declares |
| **Seven of the eleven check names `01` §4.5 declares for custom rules were unregistered.** A rule authored exactly as the spec documents produced `unknown_check` → an `error`, making FR-DATA-21 undeliverable. `scope-audit --catalogue VR` could not see it, because that audits the built-in rule *ids* while this is the custom-rule *vocabulary* — two different lists, and only one had a check | `regex`, `relationship`, `expression`, `aggregate` and `distribution_compare` implemented; `set_membership` and `uniqueness` aliased to the built-ins they duplicate, so a rule set citing either keeps working. 11/11 |
| **The whole-catalogue probe tested one direction only.** It asserted no check reports `pass` with nothing to check, and never that none reports `fail` — which is why the first defect survived it. The first attempt to extend it did not bite either: its target column was absent, so every check errored before it could condemn anything | Split into two tests, one per direction, the second against a frame whose columns *exist* and whose rules carry no configuration. Proven against the real defect: it names `allowed_values` and its alias |

Two further findings needed no code change and are recorded in
[`examples/fremtpl2/README.md`](../examples/fremtpl2/README.md): `IDpol` normalises to
`i_dpol` (no mechanical splitter can know `ID` is the acronym; `source_names` keeps the
original and the recipe renames it), and `ingest_upload` accepts one table per version
while `01` §4.2's `tables[]` is plural — **multi-table ingestion is a gap**, and the seed
joins the two source files before upload as an analyst would today.

**Not delivered by W7a.** The rest of FR-PLAT-37 — models and a rating version in the
seeded workspace — needs W5, and `NFR-PLAT-4`'s "usable seeded state in < 5 min" is not
yet measured from a cold compose stack. Both stay with **W7**.

---

### W4 — Data Workbench: closed 2026-08-15

**Scope, derived from `01` §3 before opening any source file: 50 requirements** — 40
`FR-DATA` (§3.1 nine, §3.2 six, §3.3 ten, §3.4 four, §3.5 four, §3.6 four, §3.7 three) and
10 `NFR-DATA`. Plus three endpoints reassigned from W2 by the interface audit: the two blob
routes and `/metrics`.

**The roadmap's row says "All 49 `DATA` requirements"; the spec holds 50.** The
disagreement is a finding, not a rounding: FR-DATA-40 ("ingestion produces full snapshots",
OQ-DATA-2) was appended in PR #16 *after* the row was written in PR #15. Exactly the shape
of W2's "of 60" against a spec holding 61. The row is left as written and this record
carries the correction — a roadmap row states what was known when it was written.

| Deliverable (roadmap §6) | Evidence |
|---|---|
| Sources | Register, list, preview; credentials held by reference and absent from every response shape, asserted rather than redacted |
| Ingestion | Blob → version → profile in one Job; rejects quarantined as a table on the version (FR-DATA-7); idempotent by source fingerprint |
| Preparation recipes | Applied **during** ingestion and stored with the version; `explode_period` preserves exposure exactly; expressions compile to Polars through a restricted AST, never `eval` |
| Parquet | Content-addressed blobs, deduplicated across versions by digest, presigned download |
| Profiling | Aggregated in DuckDB; the frame and parquet paths produce identical Profiles; one-ways read from storage and never recomputed |
| Four validation layers + built-in catalogue | **38 check implementations**, each with a firing and a non-firing case; the `sql` escape hatch sandboxed. **Not 38 shipped rules** — corrected 2026-08-15, see below |
| Reference tables | Effective-dated versions, half-open intervals, overlap refused by a `btree_gist` exclusion constraint, publish-then-pin |
| *(reassigned from W2)* Blob endpoints, `/metrics` | Presigned upload and 307 download; Prometheus exposition with bounded label cardinality |

**Gate (local, 2026-08-15):** ruff clean · mypy --strict on 83 source files · import-linter
3 kept / 0 broken · **565 tests** · 7 generated contracts match the models · docs audit
15/15 · req-coverage 118 of 418 requirements marked.

**Coverage, all three axes re-derivable from documents:**

| `scope-audit.py DATA …` | Result |
|---|---|
| requirements | **48 / 50** (96 %) |
| `--endpoints` | **28 / 28** (100 %) |
| `--catalogue VR` | **1 / 38** — the number this check reports since it was fixed on 2026-08-15. It read 38/38 by counting ids in **prose** |

**Enforcement proven, not assumed** (§13 rule 3). Every check the workstream added was
shown to fail on deliberately broken input, with the exit code read from the check itself
rather than from a `grep` in the pipeline after it:

- `--endpoints` against a contract with one path deleted → 27/28, exit 1.
- `--catalogue VR` against a rule id removed from source → 37/38, exit 1. **This one was
  silently weak**: it scanned test files too, so a rule existing nowhere but in a test read
  as implemented. The broken run failed to notice the deletion, which is how the weakness
  was found; the scan was made source-only.

  > **It was still weak, and the injection above is why the second weakness survived.**
  > Deleting an id from a *docstring* also makes the count drop, so the proof passed while
  > the check was measuring prose. An independent audit found the whole 38 were docstring
  > mentions — and that one reading `VR-ACT-1/2/8` was slash-expanded into three, two of
  > which (`VR-ACT-2`, `VR-ACT-8`) appear in no source file at all.
  >
  > Corrected 2026-08-15: the scan parses to an AST and counts ids a program **evaluates**.
  > It reports **1 of 38**, and that one is an id inside an error message.
  >
  > **What W4 shipped is 38 reusable check implementations and no built-in rule
  > catalogue.** `01` §4.4 says "Rule IDs here are stable and referenced by workflows and
  > by the UI", which is a claim about data — `BUILTIN_ROLES` is what it looks like when it
  > is true. The rules the freMTPL2 seed installs are constructed in `examples/`, not
  > shipped by the platform. The capability §4.4 describes is **not delivered**; the
  > checks behind it are.
- The DuckDB sandbox: dropping `enable_external_access` makes three tests fail, and
  removing the interrupt watchdog hangs the timeout test rather than failing it.
- The two profiling paths: reinstating either the tie-break or the quantile default breaks
  the agreement test.
- Metrics cardinality: resolved-path labels, path-labelled 404s, status codes instead of
  classes, and a gauge that never clears — four injections, four caught.
- The catalogue rules: five injections, **four** caught on the first pass. The miss was
  real — the `vanished_level` fixture had no level below the materiality threshold, so
  deleting the filter changed nothing. It has one now.

**NFRs measured, not asserted.**

| NFR | Measured | Budget |
|---|---|---|
| NFR-DATA-1 parquet ingest + prepare | 5.2 s | 900 s |
| NFR-DATA-1 CSV ingest + prepare | 29.6 s | 1800 s |
| NFR-DATA-2 validation, ~50 rules | 0.3 s | 600 s |
| NFR-DATA-2 structural layer alone | 0.1 s | 120 s |
| NFR-DATA-3 profiling | 91.7 s | 300 s |
| NFR-DATA-3 memory | 113 MB → 236 MB above baseline over a 10× payload increase | does not scale with rows |
| NFR-DATA-7 report summary, 500 rules | 30 ms | 500 ms |

`scripts/bench-data.py` at 2 M rows × 80 columns, extrapolated to 10 M; the machine has
13 GB and 80 float64 columns at 10 M rows is 6.4 GB resident before any operation runs.

**Specification defects found by implementing it.** Five, each resolved in the spec rather
than worked around:

| Defect | Resolution |
|---|---|
| NFR-DATA-3 bounded profiling memory at "2× the largest column's compressed size" — 30.7 MB, while a Python process with `polars`, `duckdb`, `scipy` and `pydantic` imported occupies 140 MB before reading a byte | Amended to the property that is protective *and* measurable: memory does not scale with row count |
| `01` §4.6's `overall` invariant left unnamed the state every report with warnings is in when written, and made an immutable artifact's verdict depend on acknowledgements arriving days later | `overall` is now a function of the rule results alone; acknowledgement is a fact *about* a report, checked at promotion |
| `01` §5.1 had no code for a duplicate acknowledgement | `ACKNOWLEDGEMENT_ALREADY_RECORDED` appended |
| `01` §4.5 read as requiring an Admin author *in addition to* `dataset:write`, leaving no built-in role able to author a `sql` rule | Read as *instead of*, per §4.5 step 5; the permission depends on the check |
| `07` §3 had no requirement about metric label cardinality — a property whose violation is silent | `FR-PLAT-52` appended |

**Not delivered by W4.** Every unevidenced requirement with a verdict:

| Item | Verdict |
|---|---|
| NFR-DATA-1, NFR-DATA-2 | **Measured, not tested.** Numbers above. A timing assertion on a shared runner fails for reasons unrelated to the code and teaches everyone to re-run it — the same reasoning that left NFR-PLAT-4 measured rather than asserted |
| FR-DATA-24, streaming half | **Reassigned to W7.** The distributional half is delivered — those rules read the reference Profile instead of re-scanning. Streaming structural rules over parquet row groups needs a real 10 M-row dataset to be designed against, which arrives with the freMTPL2 seed |
| `POST /sources/{id}/preview` for `object_store` / `sql` sources | **Partial.** Implemented for uploaded bytes, the flow FR-DATA-4 is written around. The other source kinds need connectors, which no requirement in W4's scope asked for |
| `pipelines/` — Dagster | **Deferred to W7.** `CLAUDE.md` §2 assigned it to 1a W4; W4's own roadmap row never named it, and `pipeline` as a Source *kind* is registrable without a scheduler. The mark is corrected rather than the gap hidden |
| `GET`/`POST /api/v1/environments`, `PUT .../settings` | **W14**, which owns `07` FR-PLAT-28..31 |
| `00` §5.4 `If-Match` optimistic concurrency | **Delivered in W5, 2026-08-17** — see the model-lifecycle slice record, which also corrects the reasoning below. *(Original W4 verdict, kept:)* **Not delivered, reassigned to W5.** W2 named W4 as "the first workstream with versioned artifacts", which was right — but W4's mutating endpoints act on a version's *status*, and the transition state machine already refuses every unsafe move by reading the current status under a row lock. An ETag would add a second, weaker guard over the same field. `CONFLICT_STALE_WRITE` is still absent from the error registry; the first genuine lost-update risk is a Model's editable metadata in W5, and it should be built there against a real one |
| FR-DATA-13's refusal | **Not delivered, and not previously stated.** `DIRECT_IDENTIFIER_PRESENT` is registered and raised nowhere; `modelling_forbidden_columns` has no caller; all four FR-DATA-13 markers sit on `pseudonymise`, the other half of the requirement. Closed as **FR-DATA-41** on 2026-08-15. Found by an independent audit, not by this record |
| pandera | **Not a dependency, and never was.** W4 delivered the structural layer over Polars while `01` named pandera as its mechanism in four places and `skills-map.md` marked it ★★ *Verified*. The spec is corrected (2026-08-15); the layer itself is delivered and tested |
| `00` §5.4 `Idempotency-Key` header | **Delivered, after the audit found it wrong.** All four `202` endpoints accept it. It had been implemented as a *query parameter* on one of them — a retry is generated by an HTTP client that knows nothing about the endpoint's query string, and a key in the URL is also a key in every access log |

**Retrofit list (§5) — where W4 leaves each item:**

| Item | State after W4 |
|---|---|
| Append-only audit in the caller's transaction | **Delivered and used.** Every W4 mutation — version transitions, acknowledgements, dictionary edits, rule-set replacement, reference loads, schema corrections — writes through `audit.record` inside the caller's unit of work. 46 audit tests |
| Artifact immutability + versioning + `parent_id` | ~~**Delivered.**~~ **Partial — corrected 2026-08-15, then completed the same day.** Every W4 artifact is `frozen=True` *in Python*, versions are allocated under an advisory lock and never reused, and `derived_from` carries lineage. But **nothing stops the database being written directly**: only `audit_events` has append-only triggers, and an audit rewrote 190 stored reports from `fail` to `pass` in one statement. A `frozen` Pydantic model is a rule about one process; the retrofit list means the guarantee. Closed as **FR-DATA-42** on 2026-08-15: append-only triggers and `SELECT, INSERT`-only privileges on the three artifact tables, five injections proven. The check constraint named here does hold — but see the note under W6a about the state FR-DATA-23 leaves it in |
| `model-schema` as SSOT | **Delivered.** `Dataset`, `DataDictionaryEntry`, `PiiClass`, `RecordGrain`, `Profile`, `ValidationReport` and the rule shapes all live there; the contract regenerates and CI fails on drift |
| Job model with progress and cancellation | **Delivered and exercised.** The four `dataset.*` handlers run through it; progress and cooperative cancellation are the `pricing-core` `ProgressCallback` |
| Decimal money discipline | **Delivered.** `MoneyMinor` and `DecimalStr` throughout `01`'s shapes; one-way ratios derive from the stored Decimal so a published frequency equals published claims ÷ published exposure |
| `trace_id` propagation | **Delivered by W2, used by W4.** Carried into every Job and every audit event W4 writes |
| RBAC from the first endpoint | **Delivered.** Every route declares its permission; acknowledgement raises the spec's own `ACKNOWLEDGE_FORBIDDEN_ROLE` rather than a generic denial |
| Content-addressed blob store | **Delivered by W2, load-bearing in W4.** Parquet tables are blobs; identical tables across versions are stored once, asserted by test |

---

### W4 mid-workstream scope findings — 2026-08-14

**W4 is roughly half delivered, and the requirement-coverage number said otherwise.**
`scope-audit.py DATA` reported 44 of 50 requirements evidenced — 88 % — which reads as
nearly finished. It is not, and the gap is a property of what the evidence *is* rather
than a miscount.

Two checks added while measuring the NFRs make the real position visible:

| Check | Result |
|---|---|
| `scope-audit.py DATA --endpoints` | **0 of the 28 endpoints `01` §5.1 declares are published** |
| Requirements evidenced only by `pricing-core` / `model-schema` tests | **19 of 50** |

`@pytest.mark.req` markers do not distinguish "the maths is right" from "the platform does
this". Nineteen `DATA` requirements are satisfied by pure-function tests over Polars
frames, and several of those requirements are explicitly about persistence and
orchestration rather than computation — FR-DATA-14 ("persisted with the Dataset Version"),
FR-DATA-20 ("every non-pass outcome persists"), FR-DATA-25/27 ("runs automatically after
successful ingestion", "persisted as an artifact"), FR-DATA-21/22 (rule sets versioned and
governed). The functions those requirements need exist and are correct. Nothing stores
their output, nothing runs them after an ingestion, and nothing serves them over HTTP.

Concretely, still to build: `ValidationReport`, `Profile`, `ValidationRule` and
`ValidationRuleSet` persistence with their migrations; the acknowledgement record
(FR-DATA-17/18); validation and profiling as Jobs triggered by ingestion; and the §5.1
REST surface. NFR-DATA-7 and FR-DATA-24 wait on that layer, and NFR-DATA-9 waits on the
`sql` check, which does not exist.

**The same check found a gap in a closed workstream.** `scope-audit.py PLAT --endpoints`
reports 11 of 17 `PLAT` endpoints published: the blob upload-URL and download endpoints,
environments CRUD, and `/metrics` are declared in `07` §5.1 and were never built. W2's
closure record did not mention them, because nothing at the time compared the interface
table to the contract. They are reassigned to W4 (blobs, `/metrics`) and W14
(environments), and the W2 closure record is amended below rather than rewritten — a
closure record states what was known when it was written.

#### Position after the REST and handler slices

| Check | Then | Now |
|---|---|---|
| `scope-audit DATA` requirements | 44 / 50 | **48 / 50** |
| `scope-audit DATA --endpoints` | 0 / 28 | **28 / 28** |
| `scope-audit DATA --catalogue VR` | not measured | **38 / 38** |

Two of those moved because work landed. The third was a **third finding** of the same kind as the first two: a requirement can
summarise a catalogue it does not enumerate. FR-DATA-16 says "validation covers four
layers", which one test evidences honestly — while §4.4's catalogue of 38 named rules
behind it stood at 12. **Since closed**: all 38 are implemented, and writing the tests
found two defects in rules that already existed — `column_presence` passed when no columns
were declared, and `development_maturity` could never pass, because it measures against
the data's own latest period and the most recent rows are always immature.

`--catalogue PREFIX` was added to `scope-audit.py` so the number is re-derivable rather
than a one-off count, and it generalises: any spec declaring a catalogue of named ids can
be checked the same way.

**W4 was therefore not closeable at the time.** ~~What remains, with owners~~ — **superseded by the closure record above, 2026-08-15**; every row below was either delivered or given a verdict there:

| Item | Verdict |
|---|---|
| 26 of 38 built-in catalogue rules (§4.4) | ~~not started~~ ✔ **delivered 2026-08-15** — all 38 implemented and tested, each with a case where it fires and one where it does not |
| FR-DATA-24 streaming over parquet row groups | **not delivered** — the distributional half is done; the streaming half needs a real 10 M-row dataset to be designed against, so it is reassigned to **W7** alongside the freMTPL2 seed |
| NFR-DATA-1, NFR-DATA-2 throughput | **measured, not tested** — `scripts/bench-data.py` at 2 M × 80, extrapolated to 10 M: parquet ingest+prepare 5.2 s / 900 s, CSV 29.6 s / 1800 s, validation 0.3 s / 600 s, structural alone 0.1 s / 120 s. A timing assertion on a shared runner fails for reasons unrelated to the code |
| `GET /metrics` (FR-PLAT-40, reassigned from W2) | **not started** — needs a Prometheus client dependency and a `07` §8 entry, and several required series (scoring latency, cache hit rate) belong to later phases |
| `POST /sources/{id}/preview` for `object_store` / `sql` sources | **partial** — implemented for uploaded bytes, the flow FR-DATA-4 is written around; the other source kinds need connectors W4 has not built |

What *is* done and was not before: the `01` REST surface end to end, validation and
profiling persistence, the four `dataset.*` job handlers, preparation recipes applied
during ingestion, the sandboxed `sql` check, and **Phase 1a's exit criterion as a passing
test** — `test_the_failure_loop_then_validated` ingests a file with a negative exposure,
watches promotion refused, fixes the data rather than the verdict, and promotes.

**W1 re-audited under §13, 2026-08-14.** W1 closed before the standard required a scope
derivation, so it was audited again from the specifications rather than from its own
record.

**Scope**, derived from what W1's named deliverables are required *by* — W1 produced
foundations, not a spec section, so its scope is the set of system-level requirements its
deliverables implement:

| Deliverable | Requirement | Verdict |
|---|---|---|
| `model-schema` | FR-OVR-1 artifact immutability | ✔ as types (`frozen`, `extra="forbid"`); persistence in W3 |
| `model-schema` | FR-OVR-6 shapes defined once | ✔ package in W1, generation and drift check in W2 (#25) |
| `model-schema` | FR-OVR-7 money discipline | ✔ `MoneyMinor`, `DecimalStr`, and the docs-audit check |
| `pricing-core` | FR-OVR-5 computation callable without the backend | ✔ enforced by the ADR-0001 contract |
| compose stack | NFR-OVR-9 full stack local, no cloud | ✔ services and health checks declared |
| compose stack | NFR-PLAT-4 usable state in < 5 min | ✔ **measured 21 s**; deliberately not a test |

**6 requirements in scope; 5 carry test evidence, all 6 carry evidence of some kind.**

**The re-audit found a gap in the standard, not in W1.** `scope-audit.py` sees
`@pytest.mark.req` markers and nothing else, so a requirement enforced by an import-linter
contract, a database privilege or a recorded measurement reads as unevidenced. W1 is the
extreme case — its deliverable *is* enforcement machinery — and the audit reported half its
scope missing while the enforcement worked perfectly in CI.

Rather than weaken the standard, the enforcement was made visible:
`tests/test_repository_invariants.py` links FR-OVR-5 to the import-linter run, FR-OVR-6 to
the contract configuration being non-empty, NFR-OVR-9 to the compose declaration, and
FR-OVR-7 to the docs-audit money check. A repository-level `tests/` root was added to
`testpaths`, which both traceability scripts read.

NFR-PLAT-4 keeps its measurement rather than gaining a test: starting containers on every
push to assert a number that varies with the runner would be a slow check that fails for
reasons unrelated to the code.

*Nothing in W1's original closure was found to be wrong.* The record below stands; what was
missing was the scope derivation and the visibility of enforcement as evidence.

**W1 closure evidence** (re-verified 2026-08-14, and again on the rebuilt instance the same
day — `uv` had to be reinstalled durably, and the gate was re-run from a clean sync):

| Deliverable | Evidence |
|---|---|
| `uv` workspace | `pyproject.toml` + committed `uv.lock`; `uv sync --all-packages --dev` clean |
| `model-schema` | 4 modules; `MoneyMinor` strict, `DecimalStr` string-pinned, envelope frozen |
| `pricing-core` skeleton | 3 modules; `ProgressCallback` protocol, decimal money helpers |
| import-linter (ADR-0001) | **3 contracts kept, 0 broken** — and proven to fail on injected violations |
| CI | `docs.yml` + `python.yml`, path-filtered per component, both green |
| docker compose | **21 s cold start** against NFR-PLAT-4's 300 s; all three services healthy |
| Quality gates | ruff clean · mypy clean on 7 files · 21 tests · docs audit 14/14 |

**What W1 deliberately did *not* deliver.** It is *repo foundations*, so it landed the
**type-level** half of §5's retrofit list and the machinery that enforces it — not the
runtime half:

| §5 item | W1 | Lands in |
|---|---|---|
| Artifact immutability, versioning, `parent_id` | ✔ as types (`frozen=True`, `extra="forbid"`) | persistence in W3 |
| `model-schema` as single source of truth | ✔ as a package | ✔ **generation + CI drift check delivered in W2** (#25) |
| Decimal money discipline | ✔ as types + helpers | rating path in Phase 2 |
| The Job model | — only the `ProgressCallback` protocol | ✔ **delivered in W2** (#23) |
| Content-addressed blob store | — only the `BlobRef` type | ✔ **delivered in W2** (#24) — S3 + refcounts + conservative GC |
| `trace_id` propagation | — | **W2** |
| Append-only audit log in the caller's transaction | — | ✔ **sink delivered early in W2** (#23, DEP-1a); RBAC and approvals remain W3 |
| RBAC checks in the backend | — authentication and workspace membership only (#28) | **W3** — roles, assignments and permission checks |

Stating this explicitly so nobody reads "W1 closed" as "the retrofit list is handled". It
is not; W1 made it *cheap*, which was its job.

**Coverage:** ≈ 99 of 375 module requirements (~26 %).

**Exit:** a freMTPL2 dataset version reaches `validated`, including at least one deliberate
round through the failure loop. The retrofit list (§5) is fully in place by the end of 1a —
that is the phase's other, quieter deliverable.

> **The second half was a gate, and it is met** *(plan review 2 accepted 2026-08-15;
> delivered the same day)*. **FR-DATA-41** and **FR-DATA-42** are in: ingestion refuses a
> column the dictionary classifies `direct_identifier` unless it is dropped or
> pseudonymised, and `validation_reports`, `profiles` and `validation_acknowledgements`
> carry append-only triggers plus `SELECT, INSERT`-only privileges on the pattern
> `audit_events` uses.
>
> Immutability was `frozen=True` in Python until then — a rule about one process — and an
> audit rewrote 190 stored reports in a single statement. It cannot now.
>
> Building it corrected the requirement: `blobs` cannot be append-only, because `ref_count`
> changes on every reference and reference-counted GC deletes unreferenced rows. Its content
> columns are guarded instead, which is the honest form of immutability for a table keyed by
> the digest of its own bytes.

**W2 closure evidence** (2026-08-14). Closed under `CLAUDE.md` §13; the scope below was
re-derived from `07` §3 rather than from the build log, after an independent audit found
the earlier "not delivered" statement incomplete.

**Scope.** W2's named areas (`07` §3.1 auth, §3.2 jobs, §3.3 storage, §3.7 observability,
§3.8 configuration) plus FR-PLAT-47/48 total **35** requirements — which is what the
roadmap's "~35 of 60" meant. FR-PLAT-28..31 belong to W14 and FR-PLAT-37 to W7.

| Deliverable (roadmap §6) | Evidence |
|---|---|
| Jobs | Lifecycle, progress, cooperative cancellation, idempotency, queue routing; 5 REST endpoints |
| Blobs | Content-addressed S3 store, reference counts, conservative dry-run-by-default GC |
| Settings | Three-layer resolution with sources (`07` §4.4), typed registry, feature flags |
| Auth | OIDC verification, service accounts with rotatable keys, workspace membership |
| Health | `/healthz` / `/readyz` / `/version`, concurrent probes with per-probe timeout |
| Tracing | W3C `trace_id` from edge to worker, in every log line, problem response and audit event |
| Contracts | OpenAPI + JSON Schema generated from the models, CI fails on drift |

**Gate (local):** ruff clean · mypy --strict on 49 files · import-linter 3 kept / 0 broken ·
**246 tests** · generated contracts current · docs audit 14/14 · req-coverage 47 of 417.

> **Amendment 2026-08-14, during W4.** `scope-audit.py PLAT --endpoints` — a check that
> did not exist when this record was written — reports **11 of the 17 endpoints `07` §5.1
> declares are published**. Six were never built: `GET /api/v1/blobs/{id}`,
> `POST /api/v1/blobs/upload-url`, `GET`/`POST /api/v1/environments`,
> `PUT /api/v1/environments/{name}/settings`, and `GET /metrics`.
>
> The closure was not careless about this; nothing at the time compared the spec's
> interface table to the published contract, and all 35 in-scope requirements did have
> evidence. That is precisely the blind spot: requirement markers sit on service-layer
> tests, so a module can satisfy every requirement and still not be reachable over HTTP.
>
> Reassigned rather than reopened: the blob endpoints and `/metrics` to **W4**, which
> needs blob download URLs for parquet anyway; environments to **W14**, which owns
> `07` FR-PLAT-28..31. The record above stands as written — it states what was known
> when it was written, which is what a closure record is for.

**Enforcement proven, not assumed** (§13 rule 3). Each check was shown to fail on
deliberately broken input: the ADR-0001 and DEP-3 import contracts (injected `import
fastapi` and `import app`); the contract drift check (both a changed model with a stale
contract and a hand-edited contract); `req-coverage` against a bogus requirement id in a
backend test; and the append-only audit table against `UPDATE`, `DELETE` and `TRUNCATE`.

**NFRs measured** (§13 rule 4):

| NFR | Budget | Measured |
|---|---|---|
| NFR-PLAT-2 — submit to pickup | 5 s | **1.24 s max** over 6 runs (median 1.02 s) against the compose stack with worker and beat running. The ~1 s floor is the relay interval. |
| NFR-PLAT-3 — progress interval | 5 s | **1.02 s max** gap between persisted updates over a 12 s run |
| NFR-PLAT-7 — no secrets in logs or dumps | — | asserted per credential in `test_no_credential_survives_a_settings_dump` |

*Method note.* NFR-PLAT-2 measures submit until the Job **leaves `queued`**. No job handler
exists yet — they arrive with W4 and W5 — so the worker dispatches and finds none. That
path is submit → running plus the dispatch check, making the figure an upper bound on the
requirement, not a proxy for it.

**Requirement coverage: 32 of 35 in-scope requirements carry test evidence (91 %).**

**What W2 did not deliver.** Stated explicitly, because "W2 closed" must not be read as
"`07` is done":

| Requirement | Status | Owner |
|---|---|---|
| FR-PLAT-15 — Dagster schedules and sensors | not started; blocked on **OQ-PLAT-2**, which is deferred | whichever phase resolves OQ-PLAT-2 |
| FR-PLAT-23 — backups, PITR, tested restore | not started — an operational capability, not application code | **deployment, Phase 2** |
| FR-PLAT-40 — Prometheus `/metrics` | ~~not started~~ ✔ **delivered by W4, 2026-08-15** — three of its five families; scoring latency and cache hit rate have nothing to report until W11 and are absent rather than zero | ~~W3 or an observability slice~~ **W4** |
| FR-PLAT-14 — 13-month job retention | *partial*: the window is a declared setting with the 13-month floor enforced, but no sweeper purges beyond it. Nothing deletes job history today, so the floor holds by default rather than by design | W3 |
| FR-PLAT-1 last clause — local development identity provider in the compose stack | not delivered; dev-header identity covers local work and is refused outside `local`/`dev` | deployment |
| `00` §5.4 `If-Match` optimistic concurrency | **not applicable to W2** — no W2 resource is a versioned entity. `CONFLICT_STALE_WRITE` is not yet in the error registry | ~~**W4**~~ → **W5** ✔ **delivered 2026-08-17**, with the code registered under `07`; see the model-lifecycle slice record |
| `00` §5.4 `Idempotency-Key` header | job submission is idempotent at the service layer (FR-PLAT-12), but no HTTP endpoint creates a Job — by design, since Jobs are created by domain actions | ✔ **W4** — all four `202` endpoints |
| Out of W2 scope entirely | FR-PLAT-24..27 secrets backend, 28..31 environments (W14), 32..36 deployment, 37 demo seed (W7), 49 rate limiting, 50 webhooks | as noted |

Nine of the ten `PLAT` NFRs remain unmeasured beyond the three above; NFR-PLAT-4 was
measured in W1 (21 s against 300 s).

**An audit finding worth recording.** The published contract described only success
shapes: a client generated from it was typed against FastAPI's default
`HTTPValidationError` — which the platform never emits — and had no type for the RFC 9457
problem it does. The drift check could not catch it, because the contract faithfully
described the code and both were wrong together. A generated artifact matching its source
is not the same as either being correct, and the fix (`app/api/responses.py`) is now
guarded by tests asserting the contract's error model directly.

**W3 closure evidence** (2026-08-14). Closed under `CLAUDE.md` §13, scope derived from
`06` §3 before any code was read.

**Scope.** W3's row reads *"Governance write path: audit log + hash chain, RBAC
enforcement, approval state machine"* with the qualifier *"§5 — skeleton only, no
governance UI"*. Mapped to the spec that is **23 requirements**: `06` §3.1 identity and
permissions (8), §3.4 audit log (7), the state-machine subset of §3.2 (FR-GOV-9, 11, 12,
13, 14, 15), and NFR-GOV-2 and NFR-GOV-8. **All 23 carry test evidence.**

| Deliverable (roadmap §6) | Evidence |
|---|---|
| Audit log + hash chain | Delivered in W2 under DEP-1a; W3 adds the query, verify and export API (FR-GOV-23/24) |
| RBAC enforcement | 23 permissions, six built-in roles, scoped assignments, route-level checks, break-glass |
| Approval state machine | submit → decide → approved/rejected/changes_requested, withdrawal, per-workspace policy |

**Gate (local):** ruff clean · mypy --strict on 57 files · import-linter 3 kept / 0 broken ·
**318 tests** · contracts current · docs audit 14/14.

**NFRs measured** (§13 rule 5):

| NFR | Budget | Measured |
|---|---|---|
| NFR-GOV-1 — permission check overhead | 5 ms | **p95 1.74 ms**, median 1.36 ms over 200 checks — **but uncached** |
| NFR-GOV-2 — audit writes never fail silently | — | a rollback discards the change and its event together |
| NFR-GOV-8 — explicit negative tests in CI | — | asserted by name, not by count |

*NFR-GOV-1 is **partial**.* The requirement specifies the budget *"using a cached
effective-permission set invalidated on assignment changes"*. The budget is met without the
cache at this scale; the named mechanism does not exist, and will be needed when a
workspace has many assignments per principal. Recorded as met-on-measurement,
not-met-on-mechanism rather than as a pass.

**What W3 did not deliver.** W3 is the skeleton; `06` has 43 requirements and Phase 3
(W17–W22) owns the rest:

| Requirement | Status | Owner |
|---|---|---|
| FR-GOV-10 — Evidence Bundle completeness at submission | not started; the evidence artifacts do not exist yet | **W4/W5**, then Phase 3 |
| FR-GOV-16 — Approvals inbox with evidence inline | list and filter exist; *inline evidence* does not | **Phase 3, W18** |
| FR-GOV-17 — flags propagating into the approval surface | not started; the flags come from `01`/`02` | **Phase 3** |
| FR-GOV-18 — attestation | not started | **Phase 3** |
| FR-GOV-19 — required evidence per artifact type | not started; depends on FR-GOV-10 | **Phase 3** |
| FR-GOV-27..32 — generated documentation and dossiers | not started | **Phase 3, W20** |
| FR-GOV-33..35 — change control across the platform | not started | **Phase 3** |
| NFR-GOV-3..7 | unmeasured; several depend on artifacts that do not exist | **Phase 3** |

*A marker was removed during this audit rather than kept.* A test had been marked
FR-GOV-16 while the closure record called the inbox deferred. The traceability record and
the closure record must not disagree, and the record was the honest one.

**Open questions.** OQ-GOV-1..6 are gated "Before Phase 3" and none blocked this
skeleton — checked before starting, not assumed. OQ-GOV-2 (are platform roles authoritative,
or IdP groups?) looked like a blocker for RBAC and is not: FR-GOV-3 and FR-GOV-4 already
make roles and scoped assignments platform objects, and FR-PLAT-4 already specifies
group-to-role mapping as configuration. Both answers to OQ-GOV-2 need the model W3 built;
only the *source of assignments* is undecided.

*OQ-GOV-1's first half is settled by implementation.* W2 chained per workspace, which is
what the question's own recommendation says. The remaining half — optional external
anchoring of the chain head — is untouched and stays open for Phase 3.

### W5 — the GLM spine, 2026-08-15 *(in progress, not closed)*

Phase 1b opened with the thinnest path that produces a real fitted model, so the remaining
`MODEL` requirements have a working spine to build on rather than a design:

**dataset → Factor → `GlmSpec` → `model.fit` Job → coefficients on screen.**

| Delivered | Evidence |
|---|---|
| `Factor`, `GlmSpec`, `Coefficient`, `GlmFitResult`, `Model` in `model-schema` | R2 and R5 structural: everything frozen, and a `Coefficient` cannot exist without a standard error and an interval that contains its estimate |
| GLM fitting with `glum` 3.4.1 | a Poisson book generated from known coefficients is recovered at 20 000 rows; standard errors from the observed information, since `glum` returns none |
| `model.fit` through the Job path | end to end via `execute_job`: urban rows carry twice the claims of rural ones and the fitted relativity lands near 2 |
| `POST`/`GET /factors`, `POST`/`GET /models` | R1 refused before a Job exists; FR-MODEL-66 returns the existing model on a `spec_hash` match |
| `/models/:slug` | every estimate with its interval, a coefficient spanning zero marked, the base level shown at 1.000 |

**Not delivered, and the audit says so numerically:** `scope-audit MODEL --endpoints` reads
**4 of 23**. Bandings, groupings, spec validation, diagnostics, transparency, backtests,
comparison, prediction, GBMs, custom objectives, custom metrics and peril structures are
declared and unbuilt. Only the six error codes the spine can raise are registered — the
other sixteen arrive with the slices that raise them, rather than sitting in the catalogue
looking implemented.

**Two `02` corrections, both found by building it**: `@version` in a path becomes
`?version=` in §5.1 and §5.3 (an `@` must be percent-encoded by every client, and
`family@7` then reads as `family%407` in every log and support conversation), and
`POST /models` answers 202-with-a-Job **or** 200-with-the-Model rather than 202 always.

**W5 is not closed and this is not a closure record.** It is one slice of seventy-eight
requirements, written down so the next one starts from what is true.

### W5 — bandings and groupings, 2026-08-15 *(in progress, not closed)*

The second slice, and the one the spine's own resolver named as missing: `resolve_factors`
refused `banding` and `grouping` by name rather than treating either as its raw column.
Both now resolve, which is FR-MODEL-1's closed set going from one arm to three.

| Delivered | Evidence |
|---|---|
| `Banding`, `Grouping`, their proposals and `GroupingEvidence` in `model-schema` | §4.2's invariants at the type — strictly increasing boundaries, `labels` = `len(boundaries) - 1`, unique labels, a `null_level` that is not also a band. `unseen_level_behaviour` has **no default**, so FR-MODEL-13's "mandatory" is a `422` rather than a convention |
| `propose_banding` — `equal_width`, `quantile`, `exposure_quantile`, `credibility` | an exposure quantile puts a fifth of the *exposure* in each of five bands on a book where a row quantile would put a third of the rows and a tenth of the exposure in the first. Both are tested, and that they *disagree* is tested too — otherwise neither test says which method ran |
| `propose_grouping` — `credibility_weighted`, `hierarchical_clustering` | twenty levels drawn from four true rates collapse to exactly four, splitting none of them |
| FR-MODEL-15 evidence | deviance before and after as two one-factor Poisson fits against the same saturated model, so the difference is a likelihood-ratio statistic on `df_saved`. Collapsing twenty levels that are really four gives p ≈ 1; collapsing all twenty into one gives p < 1e-6, which is the test that stops the p-value being decoration |
| `apply_banding` / `apply_grouping`, and both through `resolve_factors` and `fit_glm` | a book with three flat frequency steps, banded on the step boundaries, recovers each band's relativity as the ratio of its step to the base band's |
| `POST`/`GET /bandings`, `POST`/`GET /groupings`, both `/propose` routes | proposing needs a `validated` version (R1) and persists nothing; persisting allocates the next version (FR-MODEL-12) and audits it (FR-MODEL-16). Insert-only at the privilege layer, so `UPDATE` and `DELETE` are refused for `gip_app` and not only by the service |
| **`spec_hash` carries its algorithm version** | `v1:sha256:…`, with the version inside the hashed payload as well as in front of it, `spec_hash_is_current` to find a stale one, and `models.spec_hash` widened 71 → 80 so the first tagged digest is not truncated into a different valid-looking one. OQ-MODEL-8 named this as the precondition for the first new field |
| **`progress` restored to `fit_glm`** | `00` §5.5's injected callback, six stages, and `pricing_core.ScaledProgress` so the handler places the core's `0..1` in a window instead of the bar going backwards. A fit no longer sits at 35 % for its whole duration |

**Three defects found by building, each fixed here:**

- **`GLM_SEPARATION_DETECTED` was raised by `pricing-core` and registered nowhere.** The fit
  handler maps a `GlmFitError`'s code straight into a `PlatformError`, and an unregistered
  code raises `ValueError` *from inside the error path* — so the one failure FR-MODEL-23
  exists to name arrived as a stack trace about error codes. Now registered, with a test
  derived from the `GlmFitError` call sites so the next one is covered on the day it lands.
- **`POST /factors` turned a `Factor` invariant into a 500.** The handler constructed the
  artifact itself, so every rule the type enforces — a prohibition with no reason, a
  monotonic direction with no rationale — reached the caller as an internal error. It is
  built during request validation now, and answers `422`.
- **Nothing tested that a factor's declared type is the transformation applied.** Deleting
  the banding branch of `resolve_factors`, so a `banding` silently returned its raw column,
  broke no test: the banding suite exercised `apply_banding` directly and the GLM suite only
  ever fitted `identity` factors. `test_factor_resolution.py` exists because of that
  injection.

**NFR-MODEL-3 measured, and met for three of four methods.** `02` §9 carries the table:
bandings 0.11–0.24 s, `credibility_weighted` 4.24 s, `hierarchical_clustering` **6.52 s
against a 5 s budget** at the 10 000 levels the requirement names. Stated rather than
rounded away, with an owner — the factor workbench slice, which is the first caller that
will feel it. NFR-MODEL-12 was added in the same pass, because computing the source summary
twice was 4 s of the original 8.59.

**Not delivered.** `scope-audit MODEL --endpoints` reads **10 of 25** and `--sections
3.1,3.2,3.3` reads 15 of 17. The two without evidence:

| Requirement | Verdict |
|---|---|
| FR-MODEL-6 — `expression` factors | **not started.** Needs §4.6's restricted grammar, the parser, and its security review — the same machinery OQ-MODEL-1 gates for custom objectives. Owned by that slice, not this one |
| FR-MODEL-7 — factor versioning | **delivered and now tested.** `create_factor` has always allocated the next version; nothing asserted it until the audit said so |

**Three divergences from committed contracts, found when `main` moved under the branch and
fixed here.** All three were mine, and all three were readable in `docs/contracts/` before a
line of this slice was written:

| Divergence | Resolution |
|---|---|
| `credibility_standard` as a top-level field on `Grouping` | `grouping.schema.json` has carried `method_params.credibility_model` since Phase 0. The contract was right; the field is gone, `method_params` widened to hold a string and an object, and a typed `credibility_model` property reads it back. FR-MODEL-80 (OQ-MODEL-5, decided 2026-08-15 in #73) adds `credibility_pk` and `credibility_components`, now both carried |
| `band_stats` keyed by `level` while `banding.schema.json` said `label` | The two Phase-0 schemas disagreed with each other — `profile.schema.json` says `level` for the same statistics from the same requirement. Resolved toward `level`: a band **is** a level, so `banding.schema.json` now points at the one-way row shape rather than defining a second one |
| `Banding` carried no `minimums` | The schema declares them and FR-MODEL-11 calls them configurable. They were arguments to `check_banding`, so the configured floor persisted nowhere — two fits of the same banding could apply different floors and the artifact would record neither. Now on the artifact, with the keyword arguments as an override for what-if evaluation |

The lesson is narrower than "read the contracts": these are **hand-authored Phase-0**
schemas that no generator checks, so nothing failed. `generate-contracts --check` compares
the *generated* files against the models and is silent about the twenty hand-written ones.

`reference_hierarchy` grouping is declared and **refused by name**: it needs a Reference
Table, which ADR-0001 keeps out of the package. `tree` banding and `tree` grouping were
refused alongside it until **OQ-MODEL-9** was decided (2026-08-17) — `pricing-core` now
declares `scikit-learn` and fits both with a depth-limited `DecisionTreeRegressor`
(FR-MODEL-85). `buhlmann_straub` is refused the same way — **not** because OQ-MODEL-5 is open (it was
decided in #73 while this branch was in review) but because FR-MODEL-80 makes the model a
recorded property of the grouping, and its `credibility_components` would come back null
for a model that is supposed to persist them. In every case the alternative was a quantile
cut recorded under the label `tree`, which is a method recorded as one it is not.

**Still declared and unbuilt after this slice:** spec validation, diagnostics, transparency,
backtests, comparison, prediction, GBMs, custom objectives, custom metrics, peril
structures — and the factor workbench view (`00` §5.6's `/factors/:datasetVersionId`), which
has an API to talk to now and no screen.

### W5 — the factor workbench, 2026-08-15 *(in progress, not closed)*

The third slice, and the first one with a screen. `02` §5.3's factor workbench is routed at
`/factors/:datasetVersionId` and reachable from a `validated` version — which turns the
previous slice's API into something a person can drive, and the exit demo's outstanding
half ("accepted without being driven") into something with more to drive.

**Two gaps found by building the view, both spec changes made before the code:**

| Gap | What it was |
|---|---|
| **FR-MODEL-83** *(new)* — evaluate a Banding or Grouping **without persisting it** | §5.3's interaction requirement — that an edit's consequence is visible before saving — was **unmeetable**. `/propose` derives boundaries from a *method* and has no way to accept an edited one, so "the proposal is always editable" (FR-MODEL-9, FR-MODEL-14) meant editable but unmeasurable. `POST /bandings/evaluate` and `POST /groupings/evaluate` are the answer |
| **`GET /dataset-versions/{id}`** — added to `01` §5.1 | Nine routes in that table are children of `/dataset-versions/{id}` and **the parent was not among them**. The only version detail route was `/datasets/{slug}/versions/{version}`, so anything holding a version id and not a dataset slug could not resolve it — which is exactly the position a view routed on `:datasetVersionId` is in. Not a new capability, so no new requirement: the row the table should always have had |

| Delivered | Evidence |
|---|---|
| `/factors/:datasetVersionId` — banding and grouping editors | 12 view tests. Moving a boundary calls `/bandings/evaluate`; re-pointing a level calls `/groupings/evaluate`; deleting either call fails a test rather than silently making the preview local |
| The edit that cannot be valid | A boundary crossing its neighbour is marked and **not sent**. The platform would refuse it correctly with a `422`, and a 422 per keystroke is not an editor — so the last valid evaluation stays on screen |
| The merge verdict in words | `02` §4.3's p-value read out loud: above 0.05 "the data does not distinguish these levels", below 0.01 "this merge discards real signal". One place says it, so a later dossier cannot describe the same number differently |
| Reachability | Linked from a version's detail view, and **only from a `validated` one** — `02` R1 means a link on a draft leads to a 409 the screen cannot explain |

**Not delivered, and §5.3 says so rather than the note quietly dropping it:** drag handles
on the boundaries (numeric inputs meet the requirement and can express a cut the mouse
cannot land on), the merge-tolerance slider (it is a *proposal* parameter — re-proposing on
every drag would discard the actuary's edits), inline profile one-ways in the column list,
and the monotonic-direction and intent controls, which belong with creating the Factor that
pins a banding.

**FR-PLAT-55 still gates real browser use.** Until PKCE ships (W6b), the SPA reaches the
API only through the dev proxy, so this view is drivable via `scripts/demo.py` and not from
a deployed browser.

### W5 — diagnostics, and the holdout that was not one, 2026-08-16 *(in progress, not closed)*

The fourth slice. `02` §3.8 was 0 of 10 and `02` §4.8's invariant — `status ≥ fitted ⟹
diagnostics_id` — was unmeetable, which OQ-MODEL-8 had cited as its own worked example.

**Two defects found before a line of the slice was written, both in closed work:**

| Found | What it was |
|---|---|
| **`record_split` had no route** | FR-DATA-36's service function, its table and its negative tests have existed since W4; no HTTP route reached it and `01` §5.1 declared none. The endpoint audit compares the spec's table against the published contract, so an endpoint missing from *both* is invisible to it — the same blind spot that hid `01`'s reference publish lifecycle, and W4 closed through it. Now `POST`/`GET /dataset-versions/{id}/splits`, with the §5.1 rows |
| **Derived versions inherited their parent's data** | `dataset.derive` recorded the operation and set `child.tables = parent.tables`, conflating FR-DATA-34's "inherits schema, Data Dictionary and Rule Set" with inheriting the *rows*. A 1 % sample held 100 % of the rows; a train/test split produced two versions each containing everything. A model "fitted on train" was fitted on all of it, and its holdout contained every training row — diagnostics that look excellent and mean nothing. **`split` is materialised now** (FR-DATA-44); `sample`, `filter`, `join` and `aggregate` are **not**, and were OQ-DATA-8 — **decided 2026-08-17**: each is materialised in the slice that first needs it, and refused with `DERIVATION_NOT_MATERIALISED` until then (FR-DATA-45), so no version can claim an operation nobody performed |

| Delivered | Evidence |
|---|---|
| `compute_diagnostics` — universal (FR-MODEL-50) and GLM (FR-MODEL-51), train and holdout side by side | Built on a book with known relativities, so the tests assert what the numbers *are*. Train A/E is exactly 1.0 for a Poisson log-link fit with an intercept — the identity `Σy = Σμ`, which only holds if design columns, base level and offset are all reconstructed correctly |
| **The type-III test separates signal from noise** | A real factor returns p < 1e-10 and a column drawn independently of the response returns p > 0.01, on the same fit. Without both halves the p-value is decoration. Degrees of freedom are asserted too: levels − 1, and a wrong df gives a wrong p-value from a right statistic |
| `predict_glm` / `linear_predictor` (FR-MODEL-62, point predictions) | Scoring from the artifact alone, no `glum` — ADR-0003. Written because diagnostics need predictions on two frames; exposing it rather than hiding it avoids writing the same arithmetic twice when `03` calls it |
| **Deviance, computed at last** | `GlmFitResult.deviance` was declared by the spine and always `None`. Now computed per family from the unit deviance, with AIC and BIC from an exact log-likelihood |
| **A Tweedie fit reports no AIC rather than a wrong one** | Tweedie's density has no closed form. `aic`/`bic` are `None` with the reason stated, not a deviance-based stand-in that would differ from every other tool's AIC by an additive constant and read as a disagreement between two correct numbers |
| `split_ref` and `diagnostics_id` live; `spec_hash` → `v2` | OQ-MODEL-8's "re-widen as the slices land", and the version tag the previous slice built doing its job: every `v1:` digest is findable with `LIKE 'v1:%'` |
| The invariant, at three layers | The type refuses a `Model` beyond `draft` with no `diagnostics_id`; a database CHECK refuses it against a direct `INSERT`; the fit path writes model and diagnostics in **one transaction**. A fit with no split is refused with `MODEL_SPLIT_REQUIRED` before compute is spent |
| `GET /models/{slug}/diagnostics`, `POST`/`GET /dataset-versions/{id}/splits` | Published in the contract, not merely routed — asserted against `docs/contracts/openapi/generated.json`, the file the endpoint audit reads |
| `diagnostics` is insert-only | `GRANT SELECT, INSERT` and `REVOKE UPDATE, DELETE` for `gip_app`, asserted from `information_schema`. FR-MODEL-49 makes diagnostics computed once and read thereafter; a row that could be updated would let the evidence behind an approval change after the approval |

**A defect the fixture found.** The deterministic test book fits exactly, so its deviance
is 0 — and floating-point accumulation returned **−4.7e-17**. Deviance cannot be negative.
It is clamped within a scaled tolerance and **raises** beyond it, because silently zeroing a
genuinely negative total would turn a wrong unit-deviance formula into a plausible number.

**The money-discipline scan was narrowed, and the narrowing was proved.** FR-MODEL-81's
`exposure_per_parameter` is a ratio, not an exposure, and the name-based scan flagged it.
Excluded by `_per_parameter` — a rule rather than two more names on the allow-list OQ-OVR-7
objects to — and deliberately *not* a general `_per_\w+`, since `premium_per_policy` is
money. Injecting a float `exposure_years` into a generated schema still fails the check.

**Not delivered.** `scope-audit MODEL --endpoints` reads **13 of 27** and 31 of 95
requirements; §3.8 is 6 of 10. The verdicts:

| Requirement | Verdict |
|---|---|
| FR-MODEL-52 — GBM diagnostics | **Not started.** Nothing fits a GBM yet; the roadmap's own risk row makes FR-MODEL-50 the gate and 51/52 incremental. Owned by the GBM slice |
| FR-MODEL-53 — cross-validation | **Not started.** Interacts with FR-MODEL-20's unimplemented regularisation path, which is where `select_by: cv` lives. Owned with it |
| FR-MODEL-56 — model comparison | **Not started.** Its own endpoint and artifact; `wf-01` E1 needs it |
| FR-MODEL-57 — backtest | ~~**Not started.**~~ **Delivered 2026-08-18** — its own artifact (`02` §4.12), two endpoints and a migration. The record is this file's backtest slice |
| FR-MODEL-63, 77, 78 — prediction intervals | **Not started.** 63 needs the covariance blob the fit stores but this signature does not receive; 77/78 need a GBM and the `quantile` template |
| FR-MODEL-64 — the rest of the lifecycle | **Partial.** `draft → fitted` is enforced at three layers; `review`, `approved`, `superseded` and `archived` have no transitions. Owned by the submission slice |
| FR-MODEL-67 — `dataset_invalidated` | **Not started.** Unowned |
| FR-MODEL-81 — complexity | **Corrected 2026-08-16.** This record read as delivered and was **half** delivered: the diagnostic was recorded, the *gate* was not, and the requirement counted as evidenced because a test marked it. The gate landed in the next slice. Left here rather than edited away, because which was believed is the thing a governed system cannot afford to lose (`CLAUDE.md` §0) |

### W5 — spec validation, and the half of FR-MODEL-81 the last slice missed, 2026-08-16 *(in progress, not closed)*

The fifth slice, and it opens by correcting the fourth. **FR-MODEL-81 was recorded as
delivered and was half delivered:** the diagnostics slice recorded factor counts,
parameter counts and the two ratios, and shipped **no gate** —
`MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT` was registered nowhere and neither
`POST /model-specs/validate` nor `POST /models` refused anything. The requirement counted
as evidenced because a test marked it, which is exactly `CLAUDE.md` §13's "a marker is a
claim, not a proof" — found by reading the requirement rather than the marker, one slice
later than it should have been.

| Delivered | Evidence |
|---|---|
| `POST /model-specs/validate` (FR-MODEL-44, `wf-01` D2) | **200 with `ok: false`**, not a 4xx: a spec that cannot be fitted is a complete answer to the question asked, and §5.3's live validation would otherwise error on every keystroke. A version that does not exist *is* a 404 — a bad reference rather than an invalid spec |
| Every problem, not the first | A spec with a missing factor, an unresolvable one and a bad response column reports all three. A validator that stopped at the first would make a ten-factor spec a ten-round conversation |
| **The FR-MODEL-81 gate, on both entry points** | The requirement names `/model-specs/validate` **and** `POST /models`; a gate on the validator alone is advisory, because a caller can skip validation and post. Both call one `complexity_or_refuse`, so they cannot drift apart |
| The refusal is audited | `model_spec.refused_for_complexity`, asserted from the audit table. Only the complexity refusal — auditing every keystroke of a live-validating form would bury the governance events |
| Unset by default, and proved so | OQ-MODEL-6 refused a platform-wide constant. Both settings resolve to `None`, and with neither set the gate returns before reading the version or its profile |
| **It costs nothing** | The parameter count comes from the stored profile's `distinct_count` and the exposure from the version's recorded totals — no parquet is read, which is what makes "before any compute is spent" true rather than aspirational |

**The estimate is named an estimate.** A banded factor is counted at its *unbanded* levels,
so the gate is conservative in the direction that refuses a spec which would have fitted.
Reading the data to count exactly would be the compute the gate exists to avoid; the
diagnostics record the true count after the fit, and that is the number a reviewer reads.

**Both directions are tested.** The same spec is accepted, then refused once the limit
moves below it — a test that only saw the refusal would pass against a gate that refused
everything, and one that only saw the acceptance would pass against a gate that never
fired.

**Not delivered.** FR-MODEL-44's *objective applicability* half — which responses and
backends an objective admits — is unbuilt, because no custom objective exists to be
applicable or not. Owned by the custom-objective slice (FR-MODEL-75/76).

### W5 — the model lifecycle, and `If-Match` against a real precondition, 2026-08-17 *(in progress, not closed)*

The sixth slice, and it opens the arm of `wf-01` that had no code at all. FR-MODEL-64's six
states existed as an enum: `draft → fitted` was enforced at three layers and **nothing beyond
it existed**, so E6–E10 — submit, pin, review, approve, transition — were unreachable, and an
approved *request* would have sat beside a model still in `review` with nothing joining them.

| Delivered | Evidence |
|---|---|
| The lifecycle as data (FR-MODEL-64) | `VALID_MODEL_TRANSITIONS` in `model-schema`, following `01`'s `VALID_DATASET_TRANSITIONS`. The tests assert the edges that must **not** exist, because a table only ever asked about legal moves is a lookup rather than an invariant |
| `POST /models/{id}/submit` | Declared in `02` §5.1 since Phase 0, served by nothing. `fitted → review`, the approval request, `approval_request_id` and the audit event in one transaction |
| `POST /models/{id}/archive` | **Added to `02` §5.1** — FR-MODEL-64 names `archived` and no endpoint reached it. One unreachable state of six is how a partial machine gets recorded as complete |
| The decision reaches the artifact (`wf-01` E10) | `06` FR-GOV-9 stops the approval machine at `approved`. The `decide` route carries the decision across **in the same transaction**, because `MODEL` depends on `GOV` and never the reverse (DEP-1) — the seam W3 established with `withdraw`'s `artifact_is_live` |
| `superseded`, automatically | Approving version *n* supersedes every earlier **approved** version of the family, each audited. A family with two approved versions has nothing to say which one a Rating Version means. A merely `fitted` predecessor is left alone — it is a candidate, not something that was once in force |
| FR-MODEL-67's flag | **Computed, not stored.** `01` FR-DATA-23 makes validation re-runnable, so a column written at fit time would answer `[]` for exactly the model the requirement exists to stop. A flagged model cannot reach `approved`; the refusal rolls the decision back with it |
| `models.status` finally enumerates its lifecycle | A `String(16)` with no constraint until now: `'live'` was a legal status, and a model holding one is skipped by every lifecycle query rather than refused. The existing CHECKs hid half the gap — a bogus status was caught *if* it had no `fit_result`, and accepted on a fitted model |
| **`00` §5.4 `If-Match`, and `CONFLICT_STALE_WRITE` registered** | `app/api/concurrency.py`, required on both lifecycle routes, checked **inside the transaction holding the row lock**. `If-Match: *` is refused rather than honoured: RFC 9110 gives it the meaning "if the resource exists", which is the precondition `00` §5.4 replaces, and a rule one character can disable is not one |
| Two declared-and-inert things made real | **`model:submit`** — a permission held by `pricing_actuary` that gated nothing; and **`EVIDENCE_INCOMPLETE`** — registered in the error catalogue and raised by nothing, the shape of gap `01` had with `RULE_TIMEOUT`. It now **fails closed** on an evidence kind this build cannot verify, so a policy tightening cannot silently do nothing |

**W4's reasoning about `If-Match` was right about the mechanism and wrong about the value.**
It deferred the header because an ETag over a status guarded by a state machine and a row lock
is "a second, weaker guard over the same field" — which is true. What it misses is that the
two produce the same 409 with different meanings: without the header a stale client is told
"your transition is invalid" and cannot tell that from "you asked for something never legal";
with it, the answer is "what you read is stale, read it again", and only that one is
actionable by a screen. The header is a precondition on the **caller's view**, and the record
now says so rather than claiming a lost-update guard the mechanism does not provide.

**Two divergences resolved rather than absorbed** (`CLAUDE.md` §0):

* **`06` FR-GOV-13 amended.** It returned a `changes_requested` artifact to `draft`; for a
  Model that is wrong, because `02` uses `draft` for *reserved but not yet fitted* and R2
  makes the coefficients immutable — a model cannot un-fit. It now reads "its pre-submission
  state", which is `draft` for most types and `fitted` for a Model.
* **`06` FR-GOV-36 appended.** `POST /approval-requests` validates the grammar of an artifact
  reference and never resolves it, so a request can be pinned to a version that was never
  created — and FR-GOV-14's pinning then pins nothing. This is the case where the **spec is
  right and the code is not**, so the spec gained the obligation rather than being edited down
  to what was built. Owner: W5's peril-structure slice, the first to add a second artifact type
  to the same path. Until then a decision on an unresolvable `model:` reference moves nothing
  rather than failing, because a request nobody can close is worse than one that decides
  without effect.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| `06` §3.3's fuller Model evidence — transparency artifact, model comparison, factor rationale, dataset lineage | **Deferred.** §3.3 and §4.2's defaults disagree about what a submission requires, and the code enforces §4.2 because that is the artifact a workspace can edit and a check can read. Raised as **OQ-GOV-7** with a recommendation (§3.3 as a floor, §4.2 may only add) rather than settled here. Comparison is FR-MODEL-56, the next slice |
| FR-MODEL-67's propagation to Rating Versions and the Approvals inbox | **Not started** — `03` is Phase 2, and FR-GOV-16's inbox is W6b. The model-side flag and the block on `approved` are delivered |
| `If-Match` on every other mutating endpoint | **Partial, and stated.** The mechanism is shared; this slice wires it to the two routes that have a genuine precondition to express. W4's status routes remain guarded by their state machine alone, which is the reading above — not a gap discovered late |
| A `GET /models` list route | **Absent from the spec and from the code.** Noticed while writing the tests, which had to read a family slug from the database. Not added: an endpoint with no requirement behind it is the inverse of `01`'s reference-lifecycle omission. Worth a plan-review question rather than a quiet addition |
| `models.diagnostics_id` is not covered by the immutability trigger | **Found here, not fixed here.** The trigger refuses changes to `fit_result`, `spec`, `spec_hash` and `dataset_version_id` on a fitted model; `diagnostics_id` can be repointed, which would change the evidence behind an approval after the approval. The `diagnostics` rows themselves are insert-only (FR-DATA-42), so the artifact cannot be rewritten — only the pointer. Owner: the next slice to touch that trigger |

### W5 — model comparison, and the artifact the spec never defined, 2026-08-17 *(in progress, not closed)*

The seventh slice. `wf-01` E1/E2 — the actuary compares candidates on a shared holdout and
selects one — and the first slice whose **artifact had to be designed rather than
implemented**: `02` §5.2 named `ModelComparison` as a return type from Phase 0 and no section
defined it. No §4 subsection, no type, no contract. §4.11 is that design, and
`model-comparison.schema.json` is the first generated contract here with no hand-authored
Phase-0 counterpart — the others exist to compare a written promise against the emitted
shape, and this shape had no written promise to check.

| Delivered | Evidence |
|---|---|
| `ModelComparison` (§4.11) | Every invariant is a choice with its reason recorded: two or more models, a baseline inside the set, a value for every model with null where a metric does not apply, and `leader = null` on a tie as well as on an unordered metric |
| `MetricDirection` has three arms, not a boolean | `closer_to_one_is_better` exists because A/E has no better direction — 1.4 and 0.6 are equally wrong, and every higher-is-better table would rank 1.4 first |
| `compare_models` in `pricing-core` | Aligned metrics, double lift, factor-by-factor relativity differences. The Gini and binning helpers are **imported** from `diagnostics`: a second exposure-weighted Gini would let the comparison disagree with the diagnostics each model already carries |
| Double lift, binned by the **ratio** | Sorting by either prediction gives two lift curves side by side; the ratio answers "where they disagree, which one does the data support?" — what a selection turns on. The tests pin it: the ratio increases across bins and the bins partition the holdout exactly |
| `POST /models/compare` → 202 + Job | The comparison reads the holdout and scores every candidate, which is work. `POST /models` draws the same line |
| `GET /models/comparisons/{id}` | **Added to `02` §5.1** — the table declared the `POST` and no read, and a 202 whose artifact nothing can fetch is complete to the endpoint audit and unusable to a caller |
| Four refusals, before a Job exists | `MODELS_NOT_COMPARABLE`, each naming the specific thing that differs — both split ids in the message, because "these are not comparable" without saying which two things is a refusal nobody can act on. Checked **again** in `pricing-core`: `reserve_model`'s reason, plus `compare_models` being reachable from a notebook where the platform is not |
| The artifact is insert-only | `model_comparisons` grants `SELECT, INSERT` and revokes the rest (FR-DATA-42). `06` §3.3 makes a comparison required evidence for a Model approval where a predecessor exists |
| `MODEL` endpoints **18 of 29**, was 16 of 28 | `scope-audit.py MODEL --endpoints` |

**Three defects fixed that predate the slice**, all found by building it:

* **§5.2's `compare_models` signature could not be written** — the *third* instance of one
  defect. It took `Sequence[Model]`, and a `Model` carries references whose resolution needs a
  database ADR-0001 forbids `pricing-core`. `predict_glm` and `compute_diagnostics` were
  corrected the same way on 2026-08-16. That three signatures were written this way says the
  §5.2 table was drafted before the ADR's consequence was concrete; the remaining unbuilt
  signatures should be read with that in mind rather than trusted.
* **`PartitionDiagnostics.double_lift` was populated by nothing, and nothing could populate
  it.** FR-MODEL-50 listed double lift among *universal* diagnostics, but it is pairwise, the
  comparison model is unknown at fit time, and FR-MODEL-49 makes diagnostics computed once and
  read thereafter — so the field could not be filled later either. Removed, FR-MODEL-50
  amended, and the removal is assertable because `extra="forbid"` refuses it as an input. A
  field that is structurally always null is worse than an absent one: a reader takes it for a
  measurement that came out empty.
* **The Job runner never told a handler which Job it was.** Three handlers read
  `parameters.get("job_id")` to stamp the artifact they produce, and no caller ever put it in
  the payload — `job_identity` carries the actor and the workspace, `fit_payload` carries the
  model — so `diagnostics.job_id` and `models.job_id` were **silently always NULL** and the
  trail from an artifact back to the run that made it did not exist. Fixed in `tasks.py`, so
  the next handler cannot be written without it, and tested there rather than per handler. The
  runner overrides a payload-supplied id: an artifact stamped with somebody else's Job is
  worse than one stamped with nothing.

**A test premise that was wrong, kept because the correction is the interesting part.** Two
fits of one factor differing only in regularisation **tie on Gini** — it is computed from the
ordering of predicted rates, and shrinkage moves both levels toward the grand mean without
ever swapping them. `holdout_deviance` separates them, being sensitive to magnitude. The test
now asserts both, which is only possible because a tie yields no leader rather than whatever
dictionary order gave.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| A GBM among the candidates (`wf-01` E1 compares a GLM *and* an XGBoost) | **Deferred — §3.5 is 0/12 and no GBM exists to compare.** `ComparisonCandidate` is shaped so a non-`glm` model is a new arm rather than a new subsystem. Owner: the GBM slice |
| FR-MODEL-57's backtest | ~~**Not started**~~ **Delivered 2026-08-18**, its own requirement, artifact and two endpoints |
| `02` §5.3's comparison view (`/models/compare?ids=`) | **W6b**, a Vue view |
| OQ-GOV-7's evidence floor | **Still open, and now cheaper.** This slice created the second evidence kind the floor needs; the recommendation stands and the decision is the maintainer's |
| An intercept-only "null model" baseline | **Not available, and noticed here.** `fit_glm` refuses a spec with no factors — "the design matrix has no columns" — so the standard actuarial baseline of comparing against a constant-rate model cannot be built. No requirement asks for it; recorded because a comparison feature is where someone will look for it |

### W5 — `wf-01`'s citation audit, 2026-08-17 *(in progress, not closed)*

The eighth slice, and the smallest: FR-OVR-17(i), `audit-docs.py`'s **check 21**. The roadmap
put it before `wf-01`'s journey test, and that ordering was right — the audit is what gives the
journey test something to stand on, because a journey citing an interface no spec declares is
drift no other check in this repository can see. `audit-docs.py` check 14's "workflow coverage"
measures whether a journey *mentions* a requirement id, which is the weaker question plan
review 2 found it was answering.

| Delivered | Evidence |
|---|---|
| Check 21 | Every `` `METHOD /path` `` and `` `name()` `` in `wf-01…05` must be declared in a spec's §5.1 or §5.2. Current run: **30 endpoint citations, 7 function citations, all declared** |
| It runs in CI already | `docs.yml` triggers on `docs/**` and runs the script; no workflow change was needed, which is what FR-OVR-17's "on every docs change" asked for |
| The enforcement is **visible** | `tests/test_repository_invariants.py` marks it `FR-OVR-17`, so `req-coverage.py` can see it. Re-auditing W1 reported half its scope missing while the enforcement worked perfectly in CI; this is the fix for that class of blindness, applied at the time rather than later |
| A citation **form**, in `docs/workflows/README.md` | An endpoint is `` `METHOD /path` ``; a `pricing-core` function is `` `name()` `` — the parentheses are what distinguish a citation from a column name, a parameter or prose in the same cell. Without them the check is a heuristic over every backticked token in a row, and `control`, `_rejected`, `f`, `where` and `Piecewise` all appear in exactly those rows |
| Both halves proved by injection | An undeclared endpoint and an undeclared function each failed, and the summary line reports the count rather than saying "all declared" above a `FAILED` block |

**It found real drift on its first run.** wf-01 A8 cited `profile_version()`; `01` §5.2 was
corrected to `profile_frame` / `profile_parquet` on 2026-08-15 and the journey was not updated,
so the journey named a function that never existed. The spec was right and the journey wrong —
resolved by correcting the journey to `profile_frame()`, which is what the profiling handler
actually calls.

**One deliberate looseness, counted and printed.** A journey writes
`POST /environments/prod/deployments` where `03` §5.1 declares `/environments/{env}/deployments`
— and the journey is *right* to be concrete, since which environment is deployed to is the
step's content. So a declared `{}` segment matches a literal one, after an exact match is tried
first. The cost is that a citation of `/models/nonsense` would match a declared `/models/{}`;
the audit prints how many citations used the fallback (currently 4, all of them environments)
so the looseness is visible rather than assumed away. Refusing it instead would report four
declared, working endpoints as missing, and a check that cries wolf is one everybody learns to
skip.

**One thing worth a plan-review question rather than a unilateral change.** The *number* of
checks is stated in six places — `CLAUDE.md` three times, `docs.yml`'s comment,
`.claude/skills/README.md`, and the `docs-audit` skill's frontmatter — and adding one check
meant editing all six. `CLAUDE.md` §0's own rule is that counts which change do not belong in
it, and this is a count that changes. Updated everywhere for now; whether the number should be
stated at all is the maintainer's call.

**Not delivered:** FR-OVR-17(ii), one end-to-end test per journey. Still W5's for `wf-01`, and
now writable — both arms of that journey run, selection (E1/E2) since the comparison slice and
approval (E6–E10) since the lifecycle slice. The requirement's own text refuses the cheap
version: marking an existing test with a journey id claims a journey where one slice is
covered.

### W5 — gradient boosting on both backends, 2026-08-17 *(in progress, not closed)*

The ninth slice, and the largest: `02` §3.5 stood at **0 of 12**. Shipped as two PRs, because
one carrying a discriminated-union migration, two heavy dependencies, a per-backend scoring
path and TreeSHAP is not reviewable — **A** the contract, the fit and the platform seam,
**B** the transparency artifact.

| Delivered | Evidence |
|---|---|
| `GbmSpec`, `GbmFitResult`, and `ModelSpec`/`FitResult` as real discriminated unions | §4.4 has called `ModelSpec` a tagged union since Phase 0; the tag existed and the union did not, so `GlmSpec.model_validate` was the only reader. 19 tests, every one a prohibition |
| `fit_gbm` / `predict_gbm` on XGBoost **and** LightGBM | 36 tests, every backend-independent one parametrized over both. One `GbmSpec` fits either; the objective, the metric names and the interaction-constraint form are translated here so the contract does not fork |
| **FR-MODEL-72's per-backend offset**, the requirement that shaped the module | Doubling exposure must exactly double the prediction, asserted on each backend. **Proven by breaking it:** removing `raw + margin` from the LightGBM branch fails both LightGBM tests and neither XGBoost one |
| FR-MODEL-52 in full — six things, not "eval curves and importances" | Evaluation curve on train and holdout, gain/cover/frequency, permutation importance on the holdout, partial dependence with each point's exposure share, monotonicity verified against the fitted response, tree/depth summary |
| The universal diagnostics are the **same code** for both arms | `_partition` takes `mu` and the family rather than a `GlmFitResult`, so a GBM and a GLM on one holdout report A/E, lift and calibration computed identically — which is what makes FR-MODEL-56's comparison a comparison |
| One Job kind fits either arm | A second `model.gbm_fit` would have made every caller, status screen and audit query ask which of two names to look for |
| The booster stored in the model row's own transaction | `pricing-core` computes the content-addressed reference and cannot store the payload (ADR-0001), so the failure to exclude is a committed model pointing at an object nobody wrote. The test reads the bytes back |
| FR-MODEL-44's *objective applicability* half | An objective outside FR-MODEL-26's set, or a Custom Objective while FR-MODEL-38 is unbuilt, is a `200 ok:false` before a Job exists. The set is exported from `pricing-core` and read by both the validator and the fit |
| §3.6's transparency artifact, both forms | GLM approximation with R², deviance explained and worst regions named by factor level with their exposure share; TreeSHAP mean \|contribution\| on a persisted sample and seed; a generated fidelity statement that says *where* the approximation fails. 19 tests |
| `GET /models/{id}/transparency` — **FR-MODEL-84, appended** | §5.1 declared the `POST` and no read: a 202 whose artifact nothing can fetch, invisible to the endpoint audit because that compares the spec against the contract and this was in neither |

**Five spec corrections, all resolved in `02` rather than diverged from** (`CLAUDE.md` §0):

1. `GbmSpec.backend` removed — `model_type` *is* the backend. Two fields carried the same two
   strings and nothing downstream could say which to believe.
2. `GbmSpec.base_margin` removed — FR-MODEL-27 says the platform *constructs* it from the
   declared offset, so a second declaration was a second source of truth for the one number
   the fit silently depends on.
3. `loss_treatment` sits on the **common block**, not the GBM arm: capping applies to the
   response, not the learner. `spec_hash` went to **v3** for it, paid visibly as v1→v2 was.
4. `predict_gbm` took a `Model` — the third instance of the ADR-0001 defect, now the third
   fixed. `fit_gbm` also gains `factors`, `holdout` and a `GbmFit` return.
5. The evaluation curve belongs in **diagnostics**, not on the fit result. Here the *code* was
   wrong: `diagnostics.schema.json` has had it under `gbm` since Phase 0 and FR-MODEL-52 asks
   for train *and* holdout, which is FR-MODEL-54's shape. The curve moved and gained its train
   series.

**`shap` is not a dependency** (`02` §8 amended). XGBoost's `pred_contribs` and LightGBM's
`pred_contrib` are the same TreeSHAP on the same trees, already linked against the booster —
and `shap` would have pulled scikit-learn into the package ADR-0001 keeps importable
standalone, for plotting the frontend does and aggregation that is fifteen lines. The cost is
reported rather than hidden: LightGBM has no interaction-value equivalent, so
`ShapSummary.interactions_available` is a capability flag, because an empty list with no flag
reads as "this model has no interactions" — a finding that backend cannot make.

**The defect this slice found is not in this slice.** `PlatformError` refuses a code it does
not know and the fit handler maps `pricing-core`'s codes straight across, so **eleven** GBM and
transparency codes would have turned a named refusal into `ValueError: unknown error code` from
inside the error path. Second occurrence: `GLM_SEPARATION_DETECTED` was unregistered from the
spine until diagnostics tripped it. `tests/test_repository_invariants.py` now ASTs the source
for every code `pricing-core` raises and asserts each is registered *and* declared — proven
against a deliberately unregistered one. Five refusals reuse codes §5.1 already declared rather
than getting parallel names.

**Environment, worth recording:** LightGBM's Linux wheel links the OpenMP runtime and does not
vendor it, so `import lightgbm` fails on a host without `libgomp1` while XGBoost — which does
vendor one — imports fine. A suite exercising only the primary backend would have called the
pair healthy. Declared as a step in `python.yml` rather than left to the runner image, and
written into `.claude/skills/python-package`.

**Numbers.** `scope-audit MODEL --sections 3.5,3.6` reads **17 of 19**; `--endpoints` reads
**20 of 30**, up from 18 of 29 (FR-MODEL-84 added one declared and two published). Suite: 952
Python tests, 105 frontend.

**Not delivered, with verdicts:**

| Requirement | Verdict |
|---|---|
| **FR-MODEL-74** — reconciliation accounts for the loss treatment | **Reassigned.** Its other half is FR-MODEL-60's peril-structure reconciliation, which does not exist. Owner: the peril structure slice |
| **FR-MODEL-37** — EBM shape functions | **Not started.** `interpret` is a third heavy dependency serving one requirement for a model type nothing fits. Owner: the slice that first fits an `ebm` model |
| `loss_treatment` `spliced` / `excess` | **Declared and refused by name.** Narrowing the enum would have cost a `spec_hash` version to widen later; applying them as `none` would fit an uncapped model under a spec that records a treatment |
| **R3 enforcement** | **Deferred to `03`, by the requirement's own wording.** FR-MODEL-33 binds at the point a *Rating Version* references the model, which is a later phase. This slice provides the artifact that check will read, and `02` R3 is where the obligation stays |
| Frontend | **W6b.** §5.3's model spec builder, the diagnostics view's GBM eval curves and FR-MODEL-79's interaction suggestions are view work. `ModelDetailView.vue` is narrowed to the GLM arm so `vue-tsc` keeps naming the GBM view as missing |
| **OQ-MODEL-10** raised | Whether the GLM approximation is a Model in its own right. Bound to OQ-MODEL-3 — it needs an independent identity only if something may rate on it — and recommended to wait rather than build an artifact nothing references |

### W5 — `wf-01` driven end to end, 2026-08-17 *(in progress, not closed)*

The tenth slice: FR-OVR-17(ii) for `wf-01`, the requirement the citation-audit slice left
outstanding and the GBM slice made writable. One test, `backend/tests/test_wf01_journey.py`,
walking the journey's own phases in order through the same Jobs and services a caller reaches
— not a marker on an existing test, which FR-OVR-17 refuses by name.

| Delivered | Evidence |
|---|---|
| A→E2 and E6→E10 in one test | Ingest, **the failure loop** (a version that fails validation, is corrected, and passes), profiling, a materialised train/test split, a banding, a grouping, a GLM fit, an XGBoost fit on the same factors and split, diagnostics on both, the transparency artifact, the comparison, submission, the self-approval refusal, and approval — each block naming the step it executes |
| The split is **materialised**, not asserted | `dataset.derive` produces both parts as real versions. A faked split gives every fit a holdout identical to its training set, and every diagnostic downstream reports the model's own memory |
| E9 walks the refusal, not the happy path | `SUBMITTER_CANNOT_APPROVE` (`06` R1) is asserted inside the journey, because a journey test that only walked the happy path would not reach the one step that has to fail |
| E1 compares **both** candidates | The artifact is read back through `load_comparison` and its `holdout_deviance` asserted to carry a number for each model ref — the job succeeding proves nothing, since a comparison that silently dropped the GBM would also succeed |
| The three steps the platform cannot drive are **pinned, not skipped** | D7 (an `interaction` Factor) and E4/E5 (the Peril Structure, FR-MODEL-58..61) are inverted assertions: each passes while the capability is absent and **fails the day it lands**, so the slice that builds either must come back and extend the journey. A comment would have said the same and gone stale |

**Model comparison gained its GBM arm here, because the journey asked for it.** `wf-01` E1
compares "the GLM and GBM candidates" and FR-MODEL-56 is type-agnostic, so a comparison that
could only read a `GlmSpec` was code failing the spec rather than a capability nobody had
specified — the comparison slice's own verdict said as much, deferring it to "the GBM slice".
Three sites: `ComparisonCandidate` takes a `GlmFitResult | GbmFitResult` and requires the
booster bytes alongside a GBM fit (ADR-0001 — this package is handed artifacts, never ids),
`_score` dispatches to `predict_gbm`, and the backend's `_resolve_candidate` validates through
the union adapters and fetches the booster. `relativity_differences` is computed for the GLM
candidates alone and returns empty below two, because a relativity is a ratio between level
effects and a booster has none — `02` §3.6's transparency artifact is where a GBM's factor
story lives.

**The defect the journey found is in the encoding, and it is the kind only an end-to-end run
produces.** D5's banding and D8's monotone constraint met for the first time here. A banded
Factor was being handed to both backends as an **unordered categorical**, with its levels coded
in *lexicographic* order — so `"10-49"` sorted between `"0-1"` and `"2-4"`, and a declared
`decreasing` constraint would have held over the alphabet rather than over age. On LightGBM it
was worse than wrong: a monotone constraint on a categorical feature **aborts the process**
(`[LightGBM] [Fatal] The output cannot be monotone with respect to categorical features`, 4.7.0)
rather than raising, so the failure arrives as a dead worker with no error to map. Resolved in
`02` §4.4 (amended, dated) rather than diverged from: a banding is **ordinal** — coded in the
artifact's own label order and declared to the backend as ordered integers — while identity
categoricals and groupings stay unordered, since the platform has no order to assert for them.
FR-MODEL-28 refuses a direction on those two and only those two. The dtype vocabulary is now
named: `f64`, `ord`, `cat`. Proven behaviourally on both backends: band-midpoint predictions
never rise under a `decreasing` constraint, and the encoding map's order is asserted to equal
the banding's labels.

**Two stale tests, corrected against the spec rather than against the code.** Both pinned
`OverallOutcome.FAIL` for an unacknowledged warning; `01` §4.6 was amended on 2026-08-14 so
that `overall` derives from rule results alone and acknowledgement is checked at promotion
(FR-DATA-17). The code was right, the tests were the survivors — and the property they
asserted deadlocked promotion, since a report that can never leave `fail` can never be
acknowledged into `validated`. The test now names what it asserts:
`test_an_unacknowledged_warning_is_pass_with_warnings_and_still_blocks_promotion`.

**Numbers.** Suite: **961 Python tests**, 105 frontend. `req-coverage` reads 182 of 443
marked (41.1 %). `scope-audit MODEL --sections 3.5,3.6` is unchanged at **17 of 19** — a
journey test evidences the seams between requirements rather than adding to their count, which
is the point of having both measures.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| **D7** — an `annual_mileage x driver_age` interaction factor | **Not started.** `resolve_factors` implements `identity`, `banding` and `grouping` and refuses `interaction` by name. Owner: the interaction-factor slice, which must extend this journey test |
| **E4/E5** — the Peril Structure and its reconciliation (FR-MODEL-58..61) | **Not started** — no contract, no table, no code. Owner: the peril-structure slice, which also owns FR-MODEL-74 |
| FR-OVR-17(ii) for `wf-02…05` | **Outstanding**, each owned by the phase whose exit criterion names it (`§12`) — unchanged by this slice |
| `wf-01` as a **Phase 1b exit** claim | **Not yet.** The exit is the journey end to end *on freMTPL2* through the UI; this test drives the platform on a synthetic frame, which is what makes it a test rather than the demo. W7's modelling half is the other half |

#### W5 slice — peril structures and the risk-premium reconciliation, 2026-08-18

`02` §3.9 built end to end: FR-MODEL-58, 59, 60, 61 and **FR-MODEL-74**, which the GBM slice
reassigned here. `scope-audit MODEL --sections 3.9` moves from **0 of 4** to **5 of 5** — the fifth is
FR-MODEL-90, appended by this slice — and §3.5 completes at **12 of 12**, FR-MODEL-74 having
been the one requirement the GBM arm reassigned rather than evidenced. Declared endpoints go
from **20 of 30** to **24 of 32**: two of the four new routes were declared and unbuilt, and
two the spec did not declare at all.

**The inverted assertion did what it was built to do.** `wf-01`'s
`test_wf01_names_the_steps_it_cannot_yet_drive` went red the moment `PerilStructure` landed,
which was this slice's cue to drive E4/E5 for real rather than to delete the assertion. The
journey now composes a structure over the selected model, reconciles it through the real
worker, and submits and approves it beside the model. FR-OVR-17(ii) for `wf-01` stays
**partial** with **one** step named instead of three.

**Five spec defects found by building, all resolved in the spec rather than absorbed:**

1. **`02` §5.2's two signatures were unwritable** — the *fifth* instance of the
   Model-parameter defect, and the two `TODO.local.md` predicted by name. A `PerilStructure`
   carries model refs, and resolving one needs the database ADR-0001 forbids `pricing-core`.
2. **§5.1 declared a create and a reconcile and no read** — a `POST` whose artifact nothing
   can fetch, plus an approvable artifact with no way to submit it. FR-MODEL-90 appended.
   Invisible to the endpoint audit for the third time now, for the structural reason it will
   stay invisible: the audit compares the spec against the contract, and an endpoint in
   neither is in neither.
3. **FR-MODEL-61 was unreachable.** `approvals.submit` is fully generic and `peril_structure`
   has been a valid artifact type since Phase 0 — but `06` §4.2's `DEFAULT_POLICY` had no
   entry, so submission was refused with "no approval policy for this artifact type". A
   correct refusal, which is exactly what made it invisible.
4. **§4.10's example was not a contract**, and building one settled six things it left open
   — derived `ratio`/`status`, the per-peril breakdown FR-MODEL-74 needs, required
   calibration evidence, `BlobRef` as an object rather than a string, exact-decimal money,
   and a lifecycle whose `draft → review` edge does not exist.
5. **FR-MODEL-60 does not say where observed burning cost comes from**, and it cannot be
   derived. The caller declares the column, with no default.

**Three things the tests found rather than confirmed:**

- **`job_kind` is a Postgres ENUM.** This is the first slice ever to add a `JobKind`, so the
  Job insert was refused by the database from inside `job_service.submit` — after the route
  had validated everything it could see. The migration carries the `ALTER TYPE`; a downgrade
  cannot remove the value and says so.
- **A `computed_field` breaks its own artifact's round trip.** `ratio` and `status`
  serialise, and `extra="forbid"` then rejects the payload coming back — which
  `load_structure` hit on its first run. They are dropped and recomputed on input, so a
  stored or hand-edited ratio has no way to be believed.
- **A punitive tolerance does not produce a failing reconciliation** on this book: the fit
  reconciles to the penny. The failing test doubles a restoration loading instead, which
  drives FR-MODEL-74 through the platform path and is a better test than the one intended.

**Enforcement proven against deliberately broken input** (§13.4), not assumed: with the
restoration loading removed, the same capped peril fails the reconciliation it passes with
it; with the total rounded independently instead of summed from the rounded parts, the
penny-drift test reports 99 against 100.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| **`separate_model`** large-loss treatment (FR-MODEL-59) | **Deferred**, refused by name with `LOSS_TREATMENT_UNIMPLEMENTED` in `pricing-core` *and* before the Job is queued. It needs an excess-layer model, which nothing fits. Contract-level from the start, because FR-MODEL-59 names all four kinds. Owner: the slice that fits an excess-layer model |
| **`/peril-structures/:slug@:version`** view (`02` §5.3) | **Not started.** Owner: W6b, unchanged |
| **`03-rating-engine`'s consumption** of an approved structure (FR-MODEL-61's second half) | **Not started, and correctly so** — Phase 2. A later phase is a spec change, not code (`CLAUDE.md` §0) |
| `wf-01` **D7**, the interaction factor | **Not started**, unchanged. Still pinned as the one inverted assertion |
| `wf-01` E4 as **frequency × severity** | **Driven as burning cost**, a fixture limit rather than a platform one — severity responds to cost *per claim* and every claim-free row in the fixture book carries a zero a Gamma refuses. The arithmetic is covered directly in `packages/pricing-core/tests/test_perils.py`. Recorded in the journey test and in FR-OVR-17 |

#### W5 slice — interaction factors, and `wf-01` complete, 2026-08-18

FR-MODEL-1 has listed `interaction` as a Factor type since Phase 0 and the contract had no
field to express one, so the type was selectable and unresolvable. `operand_factor_ids` is
that field and FR-MODEL-91 is the rule. §3.1 moves **6/8 → 7/9**; FR-MODEL-88's list of
unimplemented arms drops from **five to four**.

**`wf-01` is now driven end to end, and the pinned test is deleted.** It held three inverted
assertions — D7, E4, E5 — each passing while its capability was absent and failing the day it
landed. Every one fired as designed and was driven by the slice that broke it. **FR-OVR-17(ii)
for `wf-01` is delivered**, the first of the five journeys to get there.

**The design decision, and why it was not silently taken.** An interaction crosses **Factors,
not columns**: every other place the spec names one names factors, and an operand is usually
itself a banding or a grouping — crossing raw `driver_age` with raw `region` gives one cell
per policy, crossing `driver_age_banded` with `vehicle_group_rated` gives a table. What an
interaction may cross is the genuinely open half, and it is **OQ-MODEL-12** rather than a
choice buried in a commit: a continuous operand is refused by name with its remedy, because
refusing is additive to undo and a product term shipped today is a model someone has fitted
by the time `03` finds no rate-table cell for it.

**Three consequences the build forced, each a defect if left implicit:**

1. **Only observed combinations become levels.** A full Cartesian product puts a coefficient
   on cells with no exposure, and on any real cross most cells have none.
2. **An operand contributes no design column of its own.** A full cross spans every cell, so
   its operands' main effects are collinear with it. This was not a preference: with the rule
   removed the fit test fails with `the design matrix is singular`, which is the broken-input
   run saying it.
3. **Type III now compares an interaction against the *main-effects* model.** It falls out of
   (2) — drop the cross and its operands become terms again — and it is the better question:
   "does this interaction earn its place over the main effects" is what an actuary means.

**Found by the tests rather than confirmed by them:** `diagnostics._term_count` resolved each
factor **alone** to count its degrees of freedom, which an interaction cannot survive, and
`_type_iii` would have dropped an operand out of the list and left the cross unresolvable.
Both are seams no unit test reaches — the fit and the diagnostics run in one handler — and
the end-to-end backend test is what surfaced them.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| A **continuous** operand (a varying slope) | **Refused by name**, OQ-MODEL-12, with the recommendation and its reasoning on file. Owner: the maintainer, revisited when `03`'s rate-table shape is built rather than specified |
| `spline`, `polynomial`, `offset`, `expression` | **Not started**, unchanged. FR-MODEL-88 now names four rather than five; each needs its own contract field and its own argument |
| The factor workbench's interaction UI (`02` §5.3, FR-MODEL-79's suggestions with exposure share and holdout lift) | **Not started.** Owner: W6b, unchanged |
| `wf-01` as a **Phase 1b exit** claim | **Still not yet**, and unchanged by this slice: the exit is the journey on freMTPL2 through the UI. What is delivered is FR-OVR-17(ii)'s *test* |

#### W5 slice — backtests, and a `Diagnostics` field nothing could ever fill, 2026-08-18

FR-MODEL-57 has named the backtest since Phase 0 and **no section defined what it produces**.
`02` §4.12 is that definition, `FR-MODEL-92` is the read endpoint the table omitted, and
`MODEL` moves **24/32 → 26/33** endpoints — the denominator rises because the read route the table omitted is now declared in it.

**`Diagnostics.backtest` is removed rather than populated.** It was declared from Phase 0 and
typed `null`, and nothing could ever have filled it: FR-MODEL-49 computes diagnostics once at
fit time, while a backtest runs later — and again for every period after that, which one field
on one immutable artifact has no room for. It is the same defect FR-MODEL-50's `double_lift`
had, found the same way and resolved the same way. `cross_validation` stays, because
FR-MODEL-53 computes it at fit time and `Diagnostics` is where it will land.

| Delivered | Evidence |
|---|---|
| `pricing_core.modelling.backtest_model` | Reuses `_partition`, so "the same diagnostic shapes" is the same arithmetic and not two implementations that agree today. Proved by the degenerate case: backtest against the training frame and every figure equals the fit's train partition |
| Both model types, one path | `score_fitted`'s dispatch; parametrised over XGBoost **and** LightGBM, for FR-MODEL-72's reason — the scoring-side offset is per backend, and dropping it would report the offset as deterioration |
| `POST /models/{id}/backtest` → 202 Job, `GET /models/backtests/{id}` | FR-MODEL-57 and **FR-MODEL-92**. Four refusals, all before the queue hop |
| `backtests` table, migration `c9d0e1f2a3b4` | Unique on `(model_id, dataset_version_id)` — a model has many backtests, one per period, and re-running one pair would be a second answer to one question |
| The **first test in this repository to exercise an artifact trigger** | `backend/tests/test_backtests.py` runs an `UPDATE` as the owner and asserts it is refused. Every other artifact table's test checks the grants only |
| `SCOREABLE_MODEL_STATUSES` consolidated into `model-schema` | Two private copies already existed (comparison, peril structures) and this slice needed a third. `CLAUDE.md` §2's rule, applied at the point it became visible |

**Two things the tests found rather than confirmed.**

**The refusal order is load-bearing.** A split's `train` and `test` parts are derived Dataset
Versions that stay `draft`, so `01` §1.3's validated gate answered a request to backtest the
model's own holdout with *"that version is not validated"* — true, unhelpful, and an
instruction to go and validate the holdout, after which the request would have been allowed.
The definitional refusal now runs first. `datasets.load_version` was made public for it, which
is the gate-free half `fittable_or_refuse` was already built from.

**A GBM test asserting calibration must first assert it converged.** At 30 boosting rounds the
booster's own train A/E was 0.53, and the backtest on a book with 30 % more claims read 0.65 —
a number that is entirely shrinkage. A test that checked only the later figure would have
calibrated its bound against an unconverged fit. It now runs 300 rounds and asserts train
A/E ≈ 1.000 before reading the backtest.

**`01` FR-DATA-47 appended, from a gap this slice measured.** FR-DATA-42's trigger exists
because revoking `UPDATE` from the *owner* does nothing. `diagnostics`, `model_comparisons`
and `transparency_artifacts` were each created with the grants and **no trigger at all** —
verified on a migrated database: two triggers each on the FR-DATA-42 tables and on
`backtests`, zero on those three. Each is evidence something is approved against. Recorded
with an owner rather than fixed here, because it is a different requirement's scope.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| A **list** of a model's backtests (`GET /models/{id}/backtests`) | **Not built, deliberately.** It is what `05-monitoring.md` reads and nothing consumes it yet; `CLAUDE.md` §0 puts a later phase's capability in the spec rather than the code. Named in FR-MODEL-92. Owner: the monitoring workstream |
| `POST /models/{id}/predict` (FR-MODEL-63, 77, 78) | **Not started.** The other of the two shortest remaining endpoints; 63 still needs the covariance blob `predict_glm`'s signature deliberately does not take |
| `01` FR-DATA-47's three tables | **Not started, and not this slice's.** Owner: W5's next slice or W13, whichever reaches it first. The migration is three tables through the loop `a1b2c3d4e5f6` already writes, plus a negative test each |
| A backtest view (`02` §5.3) | **W6b**, a Vue view. No frontend work in this slice |
| A backtest cited as approval evidence (`06` §3.3) | **Not started.** `06` §3.3's evidence table has no `backtest` kind, and adding one is a governance decision rather than a modelling one — the shape OQ-GOV-7 is already about |


### Phase 1b — Modelling Workbench

**Goal:** factors, bandings, groupings, GLM and GBM fitting, diagnostics, transparency
artifacts, model versioning.

**Demo-able outcome:** the actuary bands and groups factors, fits a GLM and an XGBoost
model, compares them, and gets one approved — **`wf-01` end to end**.

| # | Workstream | Depends on | Notes |
|---|---|---|---|
| **W5** | Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective **templates only** | W4 (1a) | Every `MODEL` requirement — the largest single workstream in the project; `scope-audit.py MODEL` counts them. **Started 2026-08-15**: twelve slices in — the GLM spine, bandings and groupings, the factor workbench, diagnostics, spec validation, the model lifecycle, model comparison, `wf-01`'s citation audit, gradient boosting with its transparency artifact, `wf-01` driven end to end, peril structures with their reconciliation, and interaction factors; see the slice records below. **Scope set by the 2026-08-15 decisions:** templates only, with the certification machinery built here (FR-MODEL-75/76); both credibility methods, not one (FR-MODEL-80); SHAP interaction *suggestions* (FR-MODEL-79); the complexity diagnostic and its optional gate (FR-MODEL-81); paired quantile models as the only GBM interval (FR-MODEL-77/78). **W5 also finishes `wf-01`, and has**: the citation audit and the journey test landed 2026-08-17, and on 2026-08-18 the peril-structure and interaction slices drove the last three pinned steps, so FR-OVR-17(ii) for `wf-01` is **delivered** — the first of the five journeys |
| **W6b** | Frontend: **factor workbench**, model detail, diagnostics — **and the frontend platform**: browser authentication, accessibility beyond semantics, workspace selection, and the audit's two enforcement gaps — **FR-DATA-41** and **FR-DATA-42** | W5, W6a ✔, OQ-PLAT-6 ✔ | `02` §5.3's interaction requirement — an edit's consequence visible before saving. The platform half was added by plan review 1 (accepted 2026-08-15): **FR-PLAT-55** (authorization code + PKCE — until it ships, only the dev proxy reaches the API from a browser), **NFR-OVR-10**'s tabular fallback for charts, and a workspace selector, which `07` §3.1 needs the moment a principal belongs to more than one |
| **W7** | freMTPL2 demo seed — **the modelling half** | W5, W6b | `07` FR-PLAT-37. What remains is the half that needs a model: a fitted GLM, a rating version, and `wf-01` end to end. The data half closed as **W7a**, the entrance and its guide as **W7b** (FR-PLAT-53/54, `NT-0002`) — both in Phase 1a, because neither needed modelling and Phase 1a's exit demo needed both |

**Coverage:** ≈ 78 of 375 module requirements (~21 %).

**Exit:** [`wf-01`](workflows/wf-01-dataset-to-model.md) end to end on freMTPL2.

W5's *frontend* work (W6b) can start as soon as the `02` contracts are frozen, which is the
main parallelisation opportunity inside 1b.

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
| **W5** | Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective templates | W4 | All 78 `MODEL` requirements — the largest single workstream |
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
| **W9** | Rating algorithm contract, validation, bundle compilation | `03` FR-RATE-1..13, 22..27 |
| **W10** | Rate tables incl. seeding from models, diffs, bulk operations, import/export | FR-RATE-14..21 |
| **W11** | Scoring: real-time, batch, trace, one shared evaluator | FR-RATE-34..42; NFR-RATE-1 is the hard target |
| **W12** | Testing: golden quotes, property assertions, regression runs | FR-RATE-43..45 |
| **W13** | Dislocation with attribution | FR-RATE-46..49 |
| **W14** | Deployment: environments, atomic switchover, rollback, shadow — **and the tenancy mechanics ADR-0006 requires** | FR-RATE-50..55; `07` FR-PLAT-28..31, and added 2026-08-15 by OQ-OVR-1's decision: **FR-PLAT-56** (a deployment refuses to start against another tenant's database) and **FR-OVR-16** (a Job records the platform build, because version skew between tenants is now permanent). Any earlier `Job` migration should carry FR-OVR-16's column rather than wait for this |
| **W15** | Frontend: **DAG designer (Vue Flow)**, rate table editor, quote sandbox + ladder waterfall, dislocation views | The DAG designer is the single largest frontend effort in the project |
| **W30** | **`expression` custom objectives** — SymPy derivation, the gradient/hessian compilation target, the authoring UI, and lifting `expression_objectives_enabled` | Added 2026-08-15 by OQ-MODEL-1's decision, which moved this work out of W5 rather than deleting it: `02` FR-MODEL-40/41, FR-MODEL-75, §4.6, and `wf-05` Route B. It depends on nothing in W9–W15 and could equally be pulled into 1b if W5 finishes early — but it must not start before the certification machinery it fronts (FR-MODEL-76) has run for a phase, which is the whole point of the decision |

### Requirement coverage

≈ **67 `RATE` + ~25 remaining `PLAT`** requirements, plus the `MODEL` requirements W30 carries over (FR-MODEL-40/41/75 and the `expression` half of §4.6/§4.7).

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
| ~~**Before Phase 1a**~~ ✔ **all decided** | ~~OQ-OVR-2~~, ~~OQ-PLAT-1~~, ~~OQ-DATA-1~~, ~~OQ-DATA-2~~ *all 2026-08-14*, ~~OQ-DATA-7~~ *2026-08-15, raised and decided inside the phase by driving the exit demo* | 5 (0 open) |
| **Before Phase 1b** | ~~OQ-OVR-5~~ ✔ *2026-08-14*, ~~OQ-MODEL-1~~ ✔, ~~OQ-MODEL-5~~ ✔, ~~OQ-PLAT-6~~ ✔, ~~OQ-OVR-6~~ ✔ *all 2026-08-15*, ~~OQ-OVR-7~~ ✔, ~~OQ-DATA-8~~ ✔, ~~OQ-MODEL-8~~ ✔, ~~OQ-MODEL-9~~ ✔ *all 2026-08-17*, **OQ-MODEL-10**, **OQ-GOV-7** | 11 (2 open) |
| **Before Phase 2** | ~~OQ-RATE-1~~ ✔, ~~OQ-RATE-2~~ ✔ *both decided by spike*, ~~OQ-MODEL-3~~ ✔ *2026-08-17*, OQ-RATE-3, OQ-RATE-4, OQ-RATE-6, OQ-PLAT-3, OQ-MODEL-11 | 8 (5 open) |
| **Before Phase 3** | OQ-GOV-1..6 *(OQ-GOV-7 is gated at 1b, not here — see below)*, ~~OQ-OVR-1~~ ✔ *decided 2026-08-15 — ADR-0006, and it changes what W14 builds in Phase 2 rather than waiting for Phase 3*, ~~OQ-MODEL-7~~ ✔ *evidence in Phase 3 (W31), never a block* | 8 (6 open) |
| **Before Phase 4** | OQ-OPT-1..6, OQ-MON-1..5, ~~OQ-DATA-4~~ ✔ *decided 2026-08-14 — out of scope* | 12 (11 open) |
| **Deferred / any time** | ~~OQ-OVR-3~~ ✔, ~~OQ-OVR-4~~ ✔ *both decided 2026-08-14*, ~~OQ-DATA-3~~ ✔, ~~OQ-DATA-5~~ ✔, ~~OQ-DATA-6~~ ✔ *all decided 2026-08-14*, ~~OQ-MODEL-2~~ ✔, ~~OQ-MODEL-4~~ ✔, ~~OQ-MODEL-6~~ ✔ *all decided 2026-08-15*, OQ-RATE-5, OQ-PLAT-2, OQ-PLAT-4, OQ-PLAT-5 | 12 (4 open) |

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

---

## 11. Sizing

Effort is expressed relative to the requirement surface and the number of independently
parallelisable workstreams. **No dates, because team size is unknown.**

| Phase | Requirement share | Parallelisable streams | Relative size | Shape |
|---|---|---|---|---|
| 0 — Specification | — | — | done | — |
| On-ramp (§3) | — | 3 | XS | ~~Research~~ ✔ · ~~3 spikes~~ ✔ · **7 decisions outstanding** |
| **1a — Data Workbench** | ~26 % | 3 after W1 | **L** | ~~W1–W4~~ ✔ **all closed** + dataset views (W6a); the `validated` loop passes headless |
| **1b — Modelling Workbench** | ~21 % | 2 | **L** | W5–W7; ends at `wf-01` end to end. W6b also carries the frontend platform — browser auth, accessibility, workspace selection — after plan review 1 |
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
