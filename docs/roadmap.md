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


### Plan review 3 — at W5's close, 2026-08-22

`CLAUDE.md` §14 requires a plan review at **each workstream close**. This is the third; the
procedure is `.claude/skills/phase-review`. **The output is a proposal, never a change** —
every recommendation below needs a dated maintainer acceptance line before it binds.

**1. Completion — derived, then evidenced, never recalled.**
`scope-audit.py MODEL`: **125 in scope, 111 evidenced (89 %), 14 without**; **41 of 41
endpoints**; catalogues clean. `req-coverage.py`: 495 specified, 248 marked repo-wide.
**Three disagreements with the roadmap, all corrected today**: the slice count said
twenty-two against a file whose own newest record called itself the twenty-seventh; the
buildable-slice counter said "one" with all five rows beneath it struck; and six verdicts in
the diagnostics table said "Not started" for requirements delivered between 2026-08-17 and
08-19. **No change proposed** — the machinery worked once it was run; what failed is that
nothing runs it between closes, which is question 5.

**2. Omission — what the phase needs that no row names.**
Four found. **(a) `NFR-MODEL-7` has no owner at all** — there is no Model export or import
path anywhere in the repository, and its parent FR-OVR-2 carries zero markers. It is a
capability nobody has been asked to build, and it is not a W5 defect: no row ever named it.
**(b) The constraint-level contract-drift guard** (`minLength`, `additionalProperties`,
`required`-set drift, and arm-level attribution inside `if`/`then`) is still unbuilt after
this slice closed the field-existence and nullability halves. **(c) `06` §3.3's "per-peril
model approvals"** is enforced nowhere and cannot be, while the models sit in JSONB.
**(d) `FR-MODEL-15`'s `source_level_stats`** is in the contract and not in the Python.
**Proposal:** (b) and (d) to **W6b** as the first consumer of these contracts; (c) to **W17**
as the workstream that owns evidence enforcement; **(a) needs a maintainer verdict before it
can have an owner** — it may simply be out of Phase 1 scope, in which case NFR-MODEL-7 should
say so rather than sit unevidenced.

**3. Skills and research — the gap analysis re-run, not appended to.**
Two skills updated **and their index rows with them**: `fastapi-service` gained the alembic
credential mismatch, `python-test` gained the shared-machine load caveat. `docs/skills-map.md`
needs **no change** — this slice added no tech dependency; Bühlmann–Straub's estimators are
pure NumPy, and the §8 SciPy row was corrected to say so rather than to claim more.
**One gap the re-run found and this slice did not fill:** no skill covers *writing a schema
guard*, and the three defects found inside the existing guards (a clobbering
`properties.update`, an invisible `const`, an `ENVELOPE_FIELDS` wrong in both directions)
are exactly the kind of knowledge that is expensive to rediscover. **Proposal:** a
`contract-guard` skill, or a section in `contract-schema`, owned by W6b.

**4. Specification accuracy — the review's main target.**
This is where the slice spent most of its effort, and the answer is that **`02` had drifted
further than the audit found**. §5.1's endpoint table matched on all 40 rows *in both
directions* — which is precisely how the parameters escaped scrutiny, since `--endpoints`
compares method and path. Underneath it: one `{id}` row wrong of 23, `?dataset={slug}`
returning **200 with the whole workspace**, nine §5.2 signatures drifted, and
`compute_gbm_diagnostics` never declared at all. §4.6 diverges from its parser in three ways.
Six hand-authored schemas disagreed with `model-schema` on ~150 points, including a
`fit_result` block no GBM or EBM fit could satisfy. **All resolved by amendment with the
losing side named, never by editing the spec down to what was built.**
**Proposal:** `scope-audit.py` gains a `--params` axis. Three axes exist and a wrong
*parameter* is invisible to all three — that is not an oversight in this audit, it is a hole
in the instrument, and it is the single change most likely to prevent a repeat.

**5. Shape — are the cuts still right?**
**One proposal, and it is the substantive one.** Three separate staleness defects had a
single cause: **a slice updates the row that describes itself, and every other place that
counts or judges slices is unowned.** #116 did it, #124 and #125 did it again, and the
diagnostics table has been wrong since August 17. Naming the mechanism in the roadmap (done)
does not fix it, because it depends on the next author reading a note. **Proposal:** the
derived counts stop living in prose. `CLAUDE.md` §0 already forbids writing counts into it
for exactly this reason — *"counts that change are not written here"* — and the roadmap is
the file that kept doing it. Either the slice count and the coverage figures are generated,
or they are deleted and the reader is pointed at `scope-audit.py`. **No change to the phase
or workstream boundaries is proposed**: W5's cut held, and the audit found defects *inside*
it rather than at its edges.

**Two answers of "no change", recorded because a silent question is indistinguishable from
one nobody asked:** the Phase 1b workstream rows need no re-cut, and no requirement needs
superseding beyond `transparency_artifact_id`, which this slice struck with its reason.

**Maintainer acceptance: accepted as proposed, 2026-08-22.** Each proposal below binds from
that date. Recorded per line rather than as one blanket sentence, because a single "accepted"
over five proposals leaves no way to tell later which of them anyone actually read.

- **Question 2, the owner assignments — accepted 2026-08-22.** (b) the constraint-level
  contract-drift guard and (d) `FR-MODEL-15`'s `source_level_stats` are **W6b's**, as the
  first consumer of these contracts; (c) `06` §3.3's per-peril model approvals are **W17's**,
  as the workstream that owns evidence enforcement.
- **Question 2 (a), `NFR-MODEL-7` — accepted 2026-08-22 at the option the proposal named:
  out of Phase 1 scope.** The review said it "may simply be out of Phase 1 scope, in which
  case NFR-MODEL-7 should say so"; it now does, in `02` §9. There is no Model export path and
  no import path anywhere — not a route, not a CLI, not a bundle schema — and its parent
  FR-OVR-2 carries zero markers. It is a capability nobody has been asked to build, and no row
  ever named it, so it was never a W5 defect. Saying so is the verdict §13 rule 1 requires;
  leaving it "unassigned" was the one row in the audit-remediation slice's verdict table that
  stated an absence of a verdict rather than a verdict.
- **Question 3, the `contract-guard` skill — accepted 2026-08-22, owned by W6b**, as either a
  skill of its own or a section in `contract-schema`. The author's discretion which; the
  binding part is that the schema-drift knowledge stops being rediscovered.
- **Question 4, `scope-audit.py` gains a `--params` axis — accepted 2026-08-22.** Three axes
  exist and a wrong *parameter* is invisible to all three. Accepted as the review argues: a
  hole in the instrument rather than an oversight in one audit.
- **Question 5, the derived counts stop living in prose — accepted 2026-08-22.** Either
  generated or deleted with the reader pointed at `scope-audit.py`; not left as prose to go
  stale a fourth time. This is the only structural proposal of the five and the only one that
  would have prevented the staleness that prompted it. **It does not bind retroactively**: the
  counts already written into this file stay as written, struck and corrected in place where a
  later slice re-derived them, because a roadmap row states what was known when it was written.
- **The two "no change" answers stand**, and needed no acceptance: the Phase 1b workstream
  rows are not re-cut, and no requirement is superseded beyond `transparency_artifact_id`.

### W5 — Modelling: closed 2026-08-22

**Scope, derived from `02` with `scope-audit.py` before opening any source file:
136 requirements** — 122 `FR-MODEL` and 14 `NFR-MODEL`, across the
module's eight deliverables. W5 is the largest single workstream in the project and the first
Phase-1b workstream to close.

**The roadmap's own figures disagreed with the specification in three places, and that
disagreement is the finding.** W5's row at the "Original scope" table claims "All **124**
`MODEL` requirements"; plan review 3, written at this close, states "125 in scope, 111
evidenced (89 %), 14 without". The spec holds 136. Neither number was wrong when
written — OQ-MODEL-23 through 28 have since appended FR-MODEL-114 to FR-MODEL-122, and
requirement ids only ever accumulate (`CLAUDE.md` §5), so a count written once goes stale by
construction rather than by error. The rows are left as written and this record carries the
correction. **This is the third time the same mechanism has bitten this workstream**, which is
why plan review 3's question 5 proposed that derived counts stop living in prose — accepted
2026-08-22, and it does not bind retroactively.

##### `CLAUDE.md` §13, rule by rule

1. **Scope derived from the specification first** — `scope-audit.py MODEL` run before any
   source file was opened; the three-way disagreement with the roadmap is recorded above as a
   finding rather than reconciled away. Every unevidenced requirement has one of the four
   verdicts, or a recorded measurement with the reason a test is the wrong instrument.
2. **Deliverables audited against the definition** — the roadmap row's eight, each checked to
   **exist** *and* **work**, in the table above.
3. **Gates green locally, both halves, each exit code read** — below.
4. **Enforcement proven on broken input** — four proofs, listed above, including one that
   showed the plan's own proposed implementation would have passed the wrong test.
5. **NFRs measured, not asserted** — fourteen, with the measurement and the budget beside it;
   two breached and said so.
6. **What was *not* delivered** — the three numbers, the sixteen verdicts, the items owned
   elsewhere, and the retrofit list.
7. **Documents updated in the same PR** — `02`, the roadmap, `open-questions.md` and
   `CLAUDE.md` §2's layout marks. The demo guide is derived (FR-PLAT-54), so there is nothing
   to write; that it still derives is checked by `backend/tests/test_demo_guide.py` in the run
   below.
8. **Repository clean** — no tracked build artifacts, verified by content below.

| Deliverable (roadmap §6) | Evidence |
|---|---|
| Factors | Four of FR-MODEL-1's eight types resolve — `identity`, `banding`, `grouping`, `interaction`. The other four are **refused by name**, not missing: `spline`/`polynomial` gated on continuous-factor rateability (FR-MODEL-115), `expression` on the Phase-2 grammar (FR-MODEL-6), `offset` superseded by `OffsetSpec` (FR-MODEL-114). `FactorIntent.OFFSET` and `.DIAGNOSTIC` are permanently refused on the layer argument (FR-MODEL-116/120) |
| Bandings | **6 of 6 methods** — manual, equal-width, quantile, exposure-quantile, credibility, tree. `propose_banding` returns a complete *editable* `Banding` with per-band exposure, frequency, severity and burning cost with intervals (FR-MODEL-10); `manual` is refused at the proposal call site because the boundaries are the actuary's |
| Groupings | **4 of 5 methods** — manual, credibility-weighted (both limited-fluctuation *and* Bühlmann–Straub, FR-MODEL-80), hierarchical clustering, tree. `reference_hierarchy` is **refused by name**: it rolls levels up through a Reference Table, which ADR-0001 forbids `pricing-core` from reading. `unseen_level_behaviour` is mandatory and type-enforced — there is no default, because a silent default is a mispricing |
| glum GLM | Poisson, Gamma and Tweedie with the power estimated by profile likelihood and its 95 % interval recorded (FR-MODEL-22); regularisation and CV selection (FR-MODEL-20/53); offsets including offset-from-another-model, GLM-to-GLM (FR-MODEL-24). Every coefficient carries estimate, standard error, z, p and interval, with the base level marked (FR-MODEL-21). Non-convergence, rank deficiency and separation are named errors, not silent results (FR-MODEL-23) |
| XGBoost | One `GbmSpec`, two backends, two translation paths. Offsets are handled per backend — XGBoost `base_margin`, LightGBM `init_score` — and `test_a_prediction_scales_exactly_with_exposure` pins that they agree (FR-MODEL-72). LightGBM is the declared secondary and is tested at parity; EBM via interpret-core exports terms and bins directly rather than a serialised estimator (FR-MODEL-37, ADR-0003) |
| Diagnostics | Always on **both** train and holdout with the weighting recorded (FR-MODEL-54/55). GLM: type-III p-values, deviance, residuals. GBM: eval curve, permutation importance, partial dependence with exposure share, monotonicity. A/E, lift, calibration and Gini are computed identically for both model types so a comparison holds (FR-MODEL-56), plus backtests (FR-MODEL-57). Deviance is computed once at fit time and diagnostics are insert-only, immutable at three layers |
| Transparency artifacts | The GLM approximation of a GBM is a **Model in its own right** (FR-MODEL-96), carrying R², deviance explained and worst regions named by factor level with exposure share. TreeSHAP comes from the backends' native implementations rather than the `shap` package (FR-MODEL-35, amended 2026-08-17). A rebuild now reuses those stored numbers instead of refitting (FR-MODEL-110, this slice) |
| Custom objectives — templates only | The template catalogue — **12 templates, each with a hand-written analytic gradient *and* hessian, so 24 analytic derivatives, every one checked against a Richardson-extrapolated numeric derivative of that template's own loss** (FR-MODEL-70), plus the certification machinery (FR-MODEL-75/76) built in Phase 1 as the 2026-08-15 decision required, and custom **metrics** on the same lifecycle and grammar (FR-MODEL-45/103/105–108). `kind: expression` is refused at the Pydantic type boundary for both objectives and metrics — the absence of a `parse_expression` stub *is* the statement |

**Gate (local, 2026-08-22, both halves, each command's own exit code read):** ruff 0 · mypy 131 source files · lint-imports **3 kept, 0 broken** (ADR-0001/0002/DEP-3) · `pytest -q` **1 720 passed, 1 xfailed** in 404 s · audit-docs all checks (506 requirements, 81 open questions all mirrored, 54 JSON schemas, 140 error codes with ownership exclusive) · req-coverage **506 specified / 257 marked** · `generate-contracts.py --check` **23 generated contracts match the models** · frontend install, `generate:api`, lint, type-check, **131 tests**, build — all 0. `alembic heads` is `9e4c7b21fa08`. The demo guide still derives (FR-PLAT-54): `test_demo_guide.py` runs inside the suite above.

> **One honest qualification on the frontend half:** `pnpm install --frozen-lockfile` ran
> against an already-populated `node_modules`, which `CLAUDE.md` §11 warns can hide a missing
> dependency. The lockfile was unchanged and CI runs it clean, so this is a caveat on the
> local evidence rather than a known defect.

**Coverage, re-derivable from the documents rather than recalled:**

| Command | Result |
|---|---|
| `scope-audit.py MODEL` | 136 in scope, 120 with evidence (88 %), 16 without |
| `scope-audit.py MODEL --endpoints` | **41 declared, 41 published (100 %)** |
| `scope-audit.py MODEL --catalogue` | Nothing to run — MODEL declares no catalogue |
| `alembic heads` | `9e4c7b21fa08`, matching the migration this workstream's last slice added |

**Enforcement proven, not assumed** (§13 rule 4). Every check this slice introduced was shown
to fail on deliberately broken input before it was trusted:

- **NFR-MODEL-8's position tests, in both directions.** Removing `node=` entirely fails both.
  More usefully, threading the *refused child* rather than its nearest positioned ancestor
  passes the subscript case and fails the operator case — which is precisely the distinction
  the second test exists to catch, and it means the ancestor walk is load-bearing rather than
  decorative.
- **NFR-MODEL-6's determinism test.** It passed on the first run, which proves nothing until
  it is shown capable of failing: refitting on one row fewer of 20 000 moves the intercept by
  5.8e-05, roughly six orders of magnitude above the 1e-10 gate.
- **FR-MODEL-110's call-count test.** Fails on the pre-change handler with both
  `build_glm_approximation` and `compute_diagnostics` recorded. Separately, swapping the
  probe's read session for `unit_of_work()` fails the leaves-no-reserved-surrogate test,
  proving the rollback is what keeps a failed build from leaving a surrogate behind.
- **A test that could not fail was deleted rather than kept.** A third FR-MODEL-110 test
  counting surrogate rows on the happy path passed in both the good and the deliberately
  broken state. Two tests that bite beat three with one that cannot.

**Specification defects found by implementing it** (§0 — resolved, not quietly reconciled):

| Defect | Resolution |
|---|---|
| FR-MODEL-110 said the branch **loads** the surrogate's `Diagnostics`. It is not implementable as a load — the result is consumed only inside the `should_fit` arm, so on the reuse path a load would be a query whose result is discarded | Requirement amended with a dated note: the branch **skips** that compute. The `glm_approximation` half was exactly right and is implemented as written |
| The roadmap's FR-MODEL-110 verdict, "Delivered but untested — a marker is owed, not a feature", was false on both counts | Struck rather than overwritten, with what was found and when. The marker it called owed would have been a false claim |
| `02` §4.4's `spec_hash` lineage note — written to reconcile the spec with the code comment — omitted `v3 → v4`, a transition **both** of its source records held | Restored to its chronological place with the omission named. The same failure one level up as the note exists to fix |
| `fit_glm` **and `fit_ebm`** accept a `seed` neither reads, and §5.2 publishes both parameters. Twenty call sites pass it, seven outside tests | **OQ-MODEL-29 — decided 2026-08-22 at option (b) and removed**, as FR-MODEL-123, pinned by a negative test asserting `seed=` now raises. `spec.seed` is the single seed for every fitter, which is what `spec_hash` pins — an argument-supplied seed would sit outside the digest and let two fits with one `spec_hash` differ, the precise thing NFR-MODEL-6 forbids. *(Original entry, kept:)* **OQ-MODEL-29**, open, with options and a recommendation; not deleted here, because nineteen call sites and a published signature are a maintainer's change |
| NFR-MODEL-7 carried "Owner: unassigned", which is a stated absence of a verdict rather than one of §13's four | Maintainer verdict 2026-08-22: **out of Phase 1 scope**. Not superseded — ids are permanent and the capability is real; it is out of *this phase's* scope |

#### The headline, as three numbers rather than one

`scope-audit.py` counts a requirement as evidenced when *any* test carries its marker, so
"120 of 136" means **declared-or-refused**, not built. Stated properly, at this close:

- **110 built** — implemented and evidenced by a test of the behaviour.
- **10 declared-and-refused-by-name.** Five where a capability is owed and the refusal stands
  in for it: FR-MODEL-59 (`separate_model`, `LOSS_TREATMENT_UNIMPLEMENTED`), FR-MODEL-87
  (whose subject *is* the staged contract), FR-MODEL-88 (`spline`/`polynomial`/`expression`
  refused at resolution), FR-MODEL-112 (the peril-reconciliation offset path), FR-MODEL-122.
  Five where the capability is **permanently withheld and the refusal *is* the requirement**:
  FR-MODEL-114 (`offset` as a Factor type), FR-MODEL-116 (`FactorIntent.OFFSET`),
  FR-MODEL-117 and FR-MODEL-120 (`FactorIntent.DIAGNOSTIC`), FR-MODEL-75 (`expression`
  objectives, gated off with the flag **on** as well as off).
- **16 unevidenced, each with a verdict** — every one below.

**The bucket grew from three to ten while `built` moved from 108 to 110**, because nine of
the eleven requirements appended since the last census are refusals or unbuilt. And this
slice's own FR-MODEL-112 marker raised `evidenced` from 119 to 120 **without moving `built`
at all** — it lands in the refusal bucket. That is precisely the overstatement the
three-number split exists to catch, and it happened inside the slice that reports it.

> **The weakest evidence in the module, named rather than averaged away.** FR-MODEL-122 is
> carried by a `@pytest.mark.xfail(strict=True)` — the only one in MODEL. That is not a
> refusal, it is a **pinned defect**: a GBM whose cross is sparse still dies inside
> `compute_gbm_diagnostics` with `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED`, and it dies *uncoded*,
> outside the block that maps a `GbmFitError` to a platform code. Counted in the refusal
> bucket because the test does mark the boundary, but it is the one entry there that a
> reader should not take comfort from. Owner: **W30**.

> **Three requirements whose evidence is thinner than their marker suggests** — found by
> reading the tests rather than trusting the marks (§13 rule 1: a marker is a claim, not a
> proof). **FR-MODEL-92** and **FR-MODEL-95** are each evidenced only by a test asserting the
> route is *published in the OpenAPI document*; no test in `backend/tests/` ever calls
> `GET /api/v1/models/backtests/{id}` or any `/custom-objectives` route. The routes exist and
> the service layer is tested, but the endpoint behaviour — the 200 and the 404 FR-MODEL-92
> names — is unproven, which is the failure FR-MODEL-92 was itself written to fix, one layer
> up. **FR-MODEL-109**'s only marker is a meta-test that every eligible schema is in the
> comparison list. These stay counted as built, because the capability is there and reachable;
> they are recorded so the next reader does not have to rediscover it. **Owner: W6b**, as the
> first consumer of these endpoints.

**Not delivered by W5.** Every unevidenced requirement, with the verdict §13 rule 1 requires
— one of delivered-but-untested, deferred with an owner, reassigned, or not started, or a
recorded measurement where a test is the wrong instrument:

| Requirement | Verdict | Owner |
|---|---|---|
| FR-MODEL-6 — `expression` factors | Not started | **W30**, accepted by the maintainer 2026-08-22 |
| FR-MODEL-40 — `expression` objectives | Not started. Its gate, FR-MODEL-75, *is* evidenced — as a refusal | **W30** (OQ-MODEL-1) |
| FR-MODEL-82 — proxy detection | Not started | **Phase 3 / W31** (OQ-MODEL-7) |
| FR-MODEL-115 — continuous Factor rateability | Not started. Gates `spline`/`polynomial`, which is why FR-MODEL-88 refuses them | **W30** |
| FR-MODEL-121 — an interaction measured jointly through its operands | Not started | **W30**. Its sibling FR-MODEL-122 is the pinned defect above |
| NFR-MODEL-1, -10 | **Measured by extrapolation** — 173 s of 600 s, 16.0 GB of 32 GB | The slice with a 16-core worker |
| NFR-MODEL-2 | **Measured once, growth unmeasured** — 963 s of 1 200 s on an *assumed* linearity | Same |
| NFR-MODEL-3 | **Measured and breached by all three grouping methods**; the cause is the one-way summary, not Ward. The remedy is to compute from the stored Profile — 2.60 s against a 5 s budget | The factor-workbench slice |
| NFR-MODEL-4 | **Measured and met** — 32.1 % at the worst measured arm against 50 % | None required |
| NFR-MODEL-5, -11 | **Measured and met**, 50× and 380× headroom | None required. NFR-MODEL-11's blob spill belongs to the slice that first stores a per-row residual series |
| NFR-MODEL-7 | **Out of Phase 1 scope** — maintainer verdict 2026-08-22, on plan review 3's question 2(a). No export path, no import path, no CLI, no bundle schema; parent FR-OVR-2 carries zero markers | **None in Phase 1.** Not superseded — the id is permanent and the capability is real |
| NFR-MODEL-12 | **Measured and held** — 0.22 s against 5.22 s | None required |
| NFR-MODEL-13 — the type-III per-factor block | **Measured and breached** at 678 013 × 60: more than 1.61× per tested factor against a 1.0× bound, and the observation is *censored* | **Phase 1b**, with the warm-denominator run the corrected multiples rest on |
| NFR-MODEL-14 — the GBM block | **Measured and met** — 0.0480 fits per scoring pass against 0.06 | None required; FR-MODEL-118's cap now bounds the sweep it prices |

**Also not delivered, and owned elsewhere rather than by W5** — listed so the boundary is
auditable rather than implied, each owner quoted from the document that assigns it:
`GroupingEvidence.source_level_stats` in the Python (FR-MODEL-15), `_sweep`'s two
`exposure_share` defects, the sweep running over source columns rather than resolved levels
(FR-MODEL-118 context), §5.3's absent intent controls and `rateable()`'s absence from §5.2
(FR-MODEL-116 context), the five constraint-level contract-drift classes (FR-PLAT-48,
FR-OVR-6) and every `02` §5.3 view — **all W6b's**; the EBM predict arm was listed here as
W6b's too and is **W32-4's**. Built 2026-08-23 (W32-4, the EBM predict arm). `custom_objective_ref`
on `Model`/`GlmSpec` (FR-MODEL-87) is **W30's**. The evidence-bundle checklist and FR-GOV-37's
unenforced half are **W17's**. Valid penalised inference (FR-MODEL-99) belongs to the slice
that builds the first of them.

**FR-MODEL-112(c) is W5's by the offsets slice's own list and is deliberately still refused.**
FR-MODEL-112 fixes the order — "(a) The next slice extends the reference to a fitted GBM … as
its own slice in Phase 1b. (c) The peril-reconciliation scoring path is **then** wired to the
resolver." Building (c) now would invert a recorded sequencing decision, and (a) is itself
demand-gated. It stays refused by name, which this slice made true in the code as well as the
sentence — that is a verdict, not a silence.

**Retrofit list (`docs/roadmap.md` §5) — where W5 leaves each item:**

| Item | State after W5 |
|---|---|
| **Append-only audit log, written in the caller's transaction** | **Delivered and used.** `audit.record(session, …)` takes the *caller's* `AsyncSession` — verified at the signature, not assumed — and the modelling write path calls it inside its own unit of work (`platform/modelling.py:248`, `:438`). W5 added the per-arm payload, because "what was fitted" is a different sentence per model type |
| **Artifact immutability + versioning + `parent_id`** | **Delivered and extended by W5.** Models, diagnostics and transparency artifacts are immutable once written, enforced by database trigger; the audit-remediation slice added `models.diagnostics_id` to that trigger by migration `9e4c7b21fa08`. Model lineage carries `parent_model_id` with a typed `change_reason` (FR-MODEL-65) |
| **`model-schema` as the single source of truth** | **Delivered and load-bearing.** All 49 `02` shapes live there; the contracts are generated and CI fails on drift (FR-PLAT-48). W5 hand-wrote no shared shape. The *constraint-level* drift guard remains unbuilt and is **W6b's** — the field-existence and nullability halves are done |
| **The Job model with progress and cancellation** | **Delivered by W2, used throughout W5.** Every long modelling operation is a Job taking `ProgressCallback` — `_fit`, `_compare`, `_transparency`, `_reconcile`, `_quantile_crossing`. W5's own defect here was the reverse of missing: a fit sat at one fraction for its whole duration until `progress` was restored to `fit_glm`'s signature |
| **Decimal money discipline** | **Delivered by W2, honoured by W5.** `DecimalStr` and `MoneyMinor` carry every monetary field crossing the boundary; W5 added the exact-decimal refusal of a float, which is a whole slice of this workstream |
| **`trace_id` propagation API → worker → core** | **Delivered by W2, inherited by W5.** The Job row carries `trace_id` from `current_trace_id()` at submission and the outbox payload carries it to the worker (`platform/jobs.py:123`, `:156`, `:327`), so a modelling handler needs no code of its own to stay traceable |
| **RBAC checks in the backend from the first endpoint** | **Delivered and used.** `Perm.MODEL_READ` / `MODEL_FIT` / `MODEL_SUBMIT` are FastAPI dependencies on the model routes (`api/models.py:104-106`). W5 added `reserve_model`'s refusals, which this slice moved *before* the expensive compute rather than after it |
| **Content-addressed blob store** | **Delivered by W2, used by W5.** Booster artifacts and split frames are content-addressed blobs read by digest. `02`'s "declarative JSON artifacts, never pickled objects" holds — the EBM path exports terms and bins rather than a serialised estimator (ADR-0003) |

**"W5 closed" must not be read as "the modelling module is finished."** It is not. Two NFRs
are measured and **breached** — NFR-MODEL-3 by all three grouping methods, and NFR-MODEL-13
at 678 013 × 60 on a *censored* observation, so the true multiple is unknown and worse than
1.61×. Three more are met only by extrapolation from a machine smaller than the one the
budget assumes. A sparse interaction still crashes the GBM diagnostics pass, uncoded. Every
`02` §5.3 view is unbuilt. What W5 closed is the **modelling engine and its API**: the maths,
the artifacts, the jobs, the lifecycle and the contracts — with 41 of 41 endpoints published,
and every remaining gap named above with an owner.

---

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
| Profile | `…/profile` | per-column cards; one-way charts with exact Poisson CI whiskers (ECharts); **histograms** — delivered 2026-08-19 by the profile-contract slice, which added `ColumnProfile.histogram` as **FR-DATA-48** and wired `HistogramChart.vue`; the **top-levels chip list now shows exposure per level** — delivered 2026-08-19 by the `top_levels` slice (FR-DATA-49) | **PSI comparison selector — built 2026-08-19.** `compareProfiles()` has its caller; the reference-version picker lives in the route query (**OQ-DATA-11**), and each column card carries a `ColumnDrift` block banded against `VR-DST-1`. |
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
| `--catalogue VR` | 38 / 38 | **38 / 38** — *was 1 / 38, corrected 2026-08-19; resolved 2026-08-23*. Not a regression: `scope-audit.py`'s catalogue check was fixed on 2026-08-15 (`d4a90c7`) to count ids the code carries **as data** rather than mentions in prose, and this row was left quoting the pre-fix instrument. The number the fixed check reports is recorded in the W7a record below, and has been since that day. Only `VR-STR-5` reached the code as a string constant at all, and incidentally — inside another rule's error message (`validate.py:1176`); the other 37 rules were implemented but unnameable, which is what `01` §4.4's "rule IDs here are stable and referenced by workflows and by the UI" asked for and did not have. Owner was **W6b**, alongside the rule set editor's threshold editing, which is the first screen that must reference a rule by id. **Resolved 2026-08-23 (W32-2) under FR-DATA-53**: the catalogue is `BUILTIN_RULES` in `model-schema`, seeded into every workspace and served by `GET /api/v1/validation-rules`. The single prior hit was one rule's id inside another rule's skip message, so the true starting count was zero. **Not resolved by this slice:** `frontend/src/api/profiles.ts:42` still hard-codes `VR-DST-1`'s PSI bands — a threshold written twice, which `CLAUDE.md` §2 forbids. The endpoint that lets the frontend ask now exists; changing the view is **W6b-13's**. Owner: W6b-13. FR-DATA-50, FR-DATA-51, FR-DATA-52, NFR-DATA-1 and NFR-DATA-2 remain without evidence and are untouched here — the first two are W32-3's, the last two are budgets needing a measurement rather than a marker |

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
| Pinia stores | **Registered, still unused — and the predicted trigger did not fire.** This row named the PSI comparison selector as the first thing that would need state to outlive a route. When that slice was built (2026-08-19) the premise did not hold: nothing requires the reference version to survive navigation, and the route query gives the selection reload-survival and shareability a store cannot. Recorded as **OQ-DATA-11**. The next candidate is the workspace selector W6b carries, and that one should be checked the same way rather than assumed. |
| TanStack Table, Vue Flow | **Later phases** (`03` §5.3). Declared in `skills-map.md`, not installed |
| Accessibility beyond semantics | **Partial.** Tables carry `aria-label`, alerts carry `role`, and every test queries by role or label — which keeps the semantics honest. NFR-OVR-10's tabular fallback for charts is **not** built; owner W6b |
| `07` §5.1's six `PLAT` endpoints | Unchanged from W2's record — still owned by W14 |
| **Six §5.3 Contents items** | **Added 2026-08-15.** Dataset status badge, last validated, owner; lineage graph; histograms; PSI comparison selector. Plus threshold editing in the rule set editor. The original record did not list them because it audited routes and not Contents. Owner: **W6b**, except the two blocked by a model/contract divergence (owner/status/validated, and `histogram`), which need a spec decision first — recorded as unresolved in `01`, not silently designed around. **Two of the six delivered 2026-08-19** — histograms, via FR-DATA-48, and the PSI comparison selector, whose `compareProfiles()` now has a caller; four remain |
| **Two unresolved model/contract divergences** | **Added 2026-08-15.** `Dataset` has no status, validated-at or owner while §5.3 asks to display all three; `ColumnProfile` has no `histogram` while `01` §4.7 *and* `docs/contracts/schemas/profile.schema.json` both define one. Four other divergences from the same fortnight got dated amendment notes; these two were built around in silence, which is the `CLAUDE.md` §0 failure the notes exist to prevent. **Both owned 2026-08-18.** The `ColumnProfile` half is **resolved 2026-08-19** by the profile-contract slice (W5): the contract was right and the requirement was incomplete, so `01` gained **FR-DATA-48**, both profiling engines compute the histogram, and the Profile view renders it. The `Dataset` half is not a slice task: it has two defensible answers, so it is recorded as **OQ-DATA-9** rather than picked. **Decided 2026-08-19, and the row closes with it:** two of the three are projections the list endpoint derives from the Dataset's versions (`FR-DATA-50`) and the third is a new explicit `Dataset.owner_id` (`FR-DATA-51`). Neither is built — the decision moved the divergence from *unanswerable* to *unbuilt*, owner W6b **Both built 2026-08-23 (W32-3), and the decision's field count was one short.** `FR-DATA-50` landed as **three** derived fields, not two: "where the two refer to different versions the list states which" cannot be satisfied by a bare `last_validated_at`, so `last_validated_version` travels with it and a validator refuses either alone. `FR-DATA-51`'s `owner_id` is a non-null column backfilled from the audit chain, with `PATCH /api/v1/datasets/{dataset_id}` as the Admin-or-owner change path the requirement implies and `01` §5.1 had nowhere to put. **The three view columns are still not rendered** — that half of this row stands, and is W6b-3's; this slice delivered the fields the columns need, not the columns |

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
| `pipelines/` — scheduled ingestion | **Deferred to W7.** `CLAUDE.md` §2 assigned it to 1a W4; W4's own roadmap row never named it, and `pipeline` as a Source *kind* is registrable without a scheduler. The mark is corrected rather than the gap hidden |
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
| FR-PLAT-15 — scheduled Jobs, and FR-PLAT-61's tick | not started; **unblocked 2026-08-23** — OQ-PLAT-2 decided against Dagster, and the mechanism is specified as FR-PLAT-61 | **Phase 4**, with the monitoring workstreams that need it (W27) |
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
| FR-GOV-10 — Evidence Bundle completeness at submission | ~~not started; the evidence artifacts do not exist yet~~ **Delivered 2026-08-17 for two of its three clauses**, by W5's model-lifecycle slice — a W3-era verdict nobody struck, found 2026-08-22. `_require_evidence` (in `platform/modelling.py`, and the same shape in `metrics.py` and `objectives.py`) raises `EVIDENCE_INCOMPLETE` against the FR-GOV-37 union of `06` §3.3's floor and the workspace policy, and **fails closed on any evidence kind it cannot verify** — proved by `test_submission_without_the_policys_evidence_is_refused`. The change-summary clause is enforced in `platform/approvals.py`. **The third clause is not built:** "a completed checklist for that artifact type" is declared six times in `06` and `grep -rn checklist backend/src` returns nothing. Recorded as delivered-in-part rather than delivered, because the row would otherwise close a clause nothing implements. | ~~**W4/W5**, then Phase 3~~ **W5** ✔ for the Evidence Bundle and the change summary · **W17** for the checklist, which owns FR-GOV-9..19 |
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

**W5 is not closed and this is not a closure record.** It is one slice of ~~seventy-eight~~
**125** requirements, written down so the next one starts from what is true. *(Corrected
2026-08-22, the audit-remediation slice, and the correction is not that the number grew.*
**"Seventy-eight" was never a count of `02`.** It is §6's Phase-1b coverage estimate — "≈ 78
of 375 module requirements" — borrowed from a planning table two pages away and read here as
a derivation. The derived count *on the day this record was written* was **85**:
`grep -cE '^\| \*\*(FR\|NFR)-MODEL-[0-9]+\*\*' docs/specs/02-modelling.md` at `ed3a733`.
Today `uv run python scripts/scope-audit.py MODEL` derives **125 in scope, 110 evidenced
(88 %), 15 without** — both requirement kinds across §3.1–§3.10 and §9. The original figure
is kept because what was believed on the day is what a governed record cannot lose; the
finding is that **an estimate lifted out of a planning table is indistinguishable, on the
page, from a number someone derived** — and that this very correction was written against
124 and had to be re-derived to 125 before it landed, because the slice writing it had
appended FR-MODEL-113 an hour earlier.*)

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
| FR-MODEL-52 — GBM diagnostics | ~~**Not started.**~~ **Delivered 2026-08-17** — the gradient-boosting slice, which is what "owned by the GBM slice" resolved to; §3.5 closed at 13 of 13 and §3.8 at 11 of 11, with six markers across `test_gbm.py` and `test_transparency.py`. Struck 2026-08-22 by the audit-remediation slice, which found it in the same table as the five rows below and **not** in the closure audit that listed them. *Believed on the day:* Nothing fits a GBM yet; the roadmap's own risk row makes FR-MODEL-50 the gate and 51/52 incremental. Owned by the GBM slice |
| FR-MODEL-53 — cross-validation | ~~**Not started.**~~ **Delivered 2026-08-21** — the regularisation-and-CV slice. Interacts with FR-MODEL-20's unimplemented regularisation path, which is where `select_by: cv` lives. Owned with it |
| FR-MODEL-56 — model comparison | ~~**Not started.**~~ **Delivered 2026-08-17** — the model-comparison slice, with `02` §4.11's artifact (which the spec did not define until that slice) and its two endpoints; 26 markers across the three packages. *Believed on the day:* Its own endpoint and artifact; `wf-01` E1 needs it |
| FR-MODEL-57 — backtest | ~~**Not started.**~~ **Delivered 2026-08-18** — its own artifact (`02` §4.12), two endpoints and a migration. The record is this file's backtest slice |
| FR-MODEL-63, 77, 78 — prediction intervals | ~~**Not started.**~~ **All three delivered** — 63 on 2026-08-18 by the prediction slice, when the covariance blob finally reached the signature; 77 and 78 on 2026-08-19 by the paired-quantile slice, which is where the `quantile` template and the GBM this row waited on both arrived. *Believed on the day:* 63 needs the covariance blob the fit stores but this signature does not receive; 77/78 need a GBM and the `quantile` template |
| FR-MODEL-64 — the rest of the lifecycle | ~~**Partial.**~~ **Complete 2026-08-17** — the model-lifecycle slice, which is what "the submission slice" resolved to. All six states are enforced by a CHECK constraint at a layer a direct `UPDATE` cannot walk past, and `review`, `approved`, `superseded` and `archived` all have transitions; 21 markers. *Believed on the day:* `draft → fitted` is enforced at three layers; `review`, `approved`, `superseded` and `archived` have no transitions. Owned by the submission slice |
| FR-MODEL-67 — `dataset_invalidated` | ~~**Not started.** Unowned~~ **Delivered 2026-08-17** — the model-lifecycle slice; the flag is computed at read rather than stored, and an invalidated dataset blocks `approved` (`test_a_model_whose_dataset_lost_its_standing_cannot_be_approved`). *"Unowned" was true when written and was answered nine slices later, which is the case for writing a verdict down rather than leaving silence.* |
| FR-MODEL-81 — complexity | **Corrected 2026-08-16.** This record read as delivered and was **half** delivered: the diagnostic was recorded, the *gate* was not, and the requirement counted as evidenced because a test marked it. The gate landed in the next slice. Left here rather than edited away, because which was believed is the thing a governed system cannot afford to lose (`CLAUDE.md` §0) |

> **Six of this table's verdicts were stale, struck 2026-08-22 by the audit-remediation
> slice.** Every one was answered by a later W5 slice between 2026-08-17 and 2026-08-19, and
> none of those slices came back to this table — which is the same mechanism that left the
> slice count and the buildable-slice counter stale: **a slice updates the row that describes
> *it*, and a verdict table written by an *earlier* slice is a second place nothing
> reconciles.** The closure audit that found five of the six missed FR-MODEL-52 entirely,
> and read FR-MODEL-64's "Partial." as "Not started" — so the audit of the stale table was
> itself slightly stale, which is the argument for deriving these from `scope-audit.py`
> rather than reading them off a page.

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
| FR-MODEL-67's propagation to Rating Versions and the Approvals inbox | **Not started** — `03` is Phase 2, and ~~FR-GOV-16's inbox is W6b~~ — **corrected 2026-08-23: it is `W18`'s, in Phase 3.** Three other statements in this file already read that way (§5's retrofit prose, W3's closure verdict, and the Phase 3 workstream table), W6b's own row has never named the inbox, and `06` assigns no owner, as a spec should not. One parenthetical against three and a silent owning row makes this the slip. The model-side flag and the block on `approved` are delivered |
| `If-Match` on every other mutating endpoint | **Partial, and stated.** The mechanism is shared; this slice wires it to the two routes that have a genuine precondition to express. W4's status routes remain guarded by their state machine alone, which is the reading above — not a gap discovered late |
| A `GET /models` list route | **Absent from the spec and from the code.** Noticed while writing the tests, which had to read a family slug from the database. Not added: an endpoint with no requirement behind it is the inverse of `01`'s reference-lifecycle omission. Worth a plan-review question rather than a quiet addition |
| `models.diagnostics_id` is not covered by the immutability trigger | **Found here, not fixed here.** The trigger refuses changes to `fit_result`, `spec`, `spec_hash` and `dataset_version_id` on a fitted model; `diagnostics_id` can be repointed, which would change the evidence behind an approval after the approval. The `diagnostics` rows themselves are insert-only (FR-DATA-42), so the artifact cannot be rewritten — only the pointer. Owner: the next slice to touch that trigger  **Discharged 2026-08-22 by the audit-remediation slice.** Migration `9e4c7b21fa08` adds `diagnostics_id` to `models_fit_immutable()`'s frozen set. The guard stays conditional on `OLD.fit_result IS NOT NULL` because `record_fit` writes the fit result, the pointer and the status in **one `UPDATE`** — checked in the handler rather than assumed, which is what the original note asked for. Proven three ways: the negative test fails at the pre-fix revision, a deliberately *naive* unconditional guard is caught by the positive control, and `downgrade -1` restores the exact prior function body. ~~Owner: the next slice to touch that trigger~~ — which is the phrasing §13 rule 1 does not accept, and it happened to be answered only because an audit went looking. |

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
| **FR-MODEL-37** — EBM shape functions | **Delivered 2026-08-21 (W5, the EBM slice).** `interpret-core==0.7.8`; term shape functions exported verbatim as additive lookup tables; transparency artifact built from the export with no approximation; universal diagnostics through the shared partition; scoring from the tables alone (ADR-0003). The third heavy dependency is now installed, so the 'one requirement for a model type nothing fits' objection is discharged |
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
| **`separate_model`** large-loss treatment (FR-MODEL-59) | **Deferred**, refused by name with `LOSS_TREATMENT_UNIMPLEMENTED` in `pricing-core` *and* before the Job is queued. It needs an excess-layer model, which nothing fits. Contract-level from the start, because FR-MODEL-59 names all four kinds. Owner: the slice that fits an excess-layer model  **Owner named 2026-08-22 (audit-remediation slice): Phase 1b, and if no Phase 1b slice claims it, it is a Phase 2 spec change rather than an implicit debt.** "The slice that fits an excess-layer model" is an event nothing schedules, which §13 rule 1 counts as silence rather than as one of its four verdicts. The refusal by name (`LOSS_TREATMENT_UNIMPLEMENTED`) is correct and stays; what changes is that the requirement is now **not started with a phase** instead of not started with a sentence. |
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
| `01` FR-DATA-47's three tables | **Not started, and not this slice's.** Owner: W5's next slice or W13, whichever reaches it first. The migration is three tables through the loop `a1b2c3d4e5f6` already writes, plus a negative test each. **Taken up 2026-08-18** by the FR-DATA-47 slice below, which found six tables rather than three |
| A backtest view (`02` §5.3) | **W6b**, a Vue view. No frontend work in this slice.  **Corrected 2026-08-23:** this cell cited a `02` §5.3 row that did not exist — the record owed a view the spec did not register. The row was added on 2026-08-23, addressed by backtest id (FR-MODEL-92), together with the prediction view its slice is paired with. The citation is now true; the obligation is unchanged |
| A backtest cited as approval evidence (`06` §3.3) | **Not started.** `06` §3.3's evidence table has no `backtest` kind, and adding one is a governance decision rather than a modelling one — the shape OQ-GOV-7 is already about |


#### W5 slice — custom objectives, and the tolerance that stopped checking, 2026-08-18

`02` §3.7 was the largest unbuilt block in the spec — **1 of 16 requirements evidenced**, and
five of `MODEL`'s six unpublished endpoints. It is now **16/17**, and `MODEL` moves
**27/33 → 34/35** endpoints (97%); the denominator rises because FR-MODEL-95 declares the two
read routes the §5.1 table omitted, and the one still unpublished is `POST /custom-metrics`.

**Templates only, per the 2026-08-15 decision — and that is what made the certification
machinery cheap rather than what made it unnecessary.** The twelve templates are the
platform's own analytic derivatives, so §4.7's checks are not verifying a user's arithmetic;
they are verifying a *parameterisation*, at the values this objective was actually given —
and two of the three findings below come from running them.

| Delivered | Evidence |
|---|---|
| `pricing_core.modelling.objectives` — the twelve-template catalogue, `compile_objective`, `certify_objective` | 23 tests, parametrised over the catalogue, so a thirteenth template inherits every one of them |
| The nine §4.7 checks, **all emitted for every objective, always** | Richardson-extrapolated central differences at `h = 1e-4`, with the agreement tolerance floored *and* offset by each point's own finite-difference noise. `certified_with_findings` is the ordinary outcome for a pricing loss; only `failed` blocks |
| `ObjectiveCertificate` wrapping `CertificateResult` | ADR-0001, made concrete: `pricing-core` cannot allocate an id, read a clock or know about a Job, so identity sits outside and findings inside. `CertificateResult.outcome_of` is the single place the verdict rule lives, enforced by a `model_validator` |
| `custom_objectives`, `objective_certificates`, migration `d0e1f2a3b4c5` | The definition is immutable while the lifecycle columns move — a certificate certifies the parameters it ran against, so an `UPDATE ... SET params` on a `certified` row is refused by trigger and proved so by test. Certificates are append-only |
| Seven endpoints (FR-MODEL-42/46/47/**95**, and `derive` refusing) | `POST /derive` exists **in order to refuse**, with `OBJECTIVE_KIND_NOT_ENABLED`: a declared endpoint that 404s says "wrong URL" where the truth is "not in this phase" |
| `fit_gbm`'s custom branch, both backends | Seven refusals by name, every one before the fit: not supplied, ref mismatch, not approved, response undeclared, not applicable, offset required, early stopping unsupported |
| FR-GOV-13 extended: a Custom Objective returns to **`certified`**, not `draft` | The certificate is pinned to the objective version (FR-MODEL-42) and the version did not change when an approver asked a question. Returning it to `draft` would discard evidence that is still valid |

**Three things the tests found rather than confirmed.**

**A defect in `predict_gbm`, in code this slice only had to read.** The LightGBM branch applied
`np.exp` to the raw score unconditionally, though `_OBJECTIVES` had carried the inverse link
as its third element all along. Correct for three of the four builtin objectives and wrong for
`binary:logistic`, which returned `exp(f)` where the model means `1 / (1 + exp(-f))` — a
"probability" above 1 for every row the model thought likely, and the two agree to within 1 %
at `f = 0`, so a weak-signal book would not have shown it. Nothing had yet asked a LightGBM
binomial model for a prediction. The custom path needed the link recorded anyway
(FR-MODEL-94), and the defect was visible the moment it was. Fixed, with a regression test
parametrised over both backends and over builtin/custom; artifacts predating the field keep
the old behaviour deliberately, because silently changing what a stored model predicts is the
worse failure. `02` §4.3 carries the note.

**Certification caught the platform's own arithmetic.** `minimum_at_truth` failed for
`asymmetric_poisson`: the implemented loss was not minimised at `f = log(y)`, and the spec was
right about what the objective meant. The code was fixed and the spec left alone — the one
direction of `CLAUDE.md` §0's rule that is easy to get backwards when the code is newer than
the words.

**The tolerance stopped checking, and nothing would have said so.** Raising the sampling floor
from 600 to 1 000 points made three of twelve templates warn on derivatives that were exactly
correct — the extra points reach where the true derivative is near zero and the difference
quotient is all noise. The fix was to subtract each point's own noise floor from the tolerance,
which is right, and which also loosens the check that exists to catch a wrong derivative. So
the loosening is now pinned from the other side: a 1 % relative error in either derivative
reaches `failed`, and an absolute error of `1e-08` in the Gamma hessian — two hundred times the
noise where that hessian is smallest — still reaches `failed`. The general rule went into
`.claude/skills/python-test`, because this will not be the last tolerance that gets loosened.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| **FR-MODEL-40/41's `expression` kind** — the grammar, the SymPy derivation, `POST /derive` | **Phase 2**, behind `expression_objectives_enabled`, and refused by name rather than absent. FR-MODEL-41 is evidenced only for the half that binds a template — the definition cannot be rewritten — not for the parser. Owner: the maintainer, with OQ-GOV-8 |
| **FR-MODEL-45 custom metrics**, and `POST /custom-metrics` — `MODEL`'s last unpublished endpoint | **Deferred to Phase 1b.** Evidenced only as the shape of its absence: under a callable objective both backends hand a builtin metric the raw score, so the metric early stopping names is not the metric it stops on. Refused with `OBJECTIVE_EARLY_STOPPING_UNSUPPORTED` and FR-MODEL-45 named in the message, because a wrongly-stopped fit produces a model that is merely worse and never one that errors |
| The sandbox question (`CLAUDE.md` §3's "arbitrary-code objective is a governance risk") | **Not answered, and deliberately not.** Templates execute no user text at all, so Phase 1 buys the capability without owing the answer. It comes due with the `expression` kind, not before |
| `02` §5.3's two views — `/objectives`, `/objectives/:slug@:version/certificate` | **Not started.** Owner: W6b. The §5.3 note records two things the views will need that the spec has wrong: "pass/warn/fail" is four statuses, and the expression editor has nothing to parse in Phase 1 |
| `06` §4.1's `custom_objective:author` / `custom_objective:submit` | **Superseded 2026-08-18.** The permissions do not exist and the spec was the wrong side; the built surface checks `model:read` / `model:fit` / `model:submit`, and separation of duty is bought by FR-GOV-11 and FR-MODEL-46 instead. Whether authoring an objective deserves its own permission is **OQ-GOV-8**, to be decided *with* the `expression` kind |
| `wf-05` Route B, and Phase C's compiled expression tree | **Phase 2**, unchanged. Route A is now real end to end except A3, and the journey carries a dated note saying which of its steps read differently |


#### W5 slice — FR-DATA-47, and a comment that had been wrong for three days, 2026-08-18

The backtest slice (#99) found three artifact tables carrying FR-DATA-42's grants and no
trigger, and raised FR-DATA-47 with an owner. This slice is that owner. It found **six**.

The difference is how the second measurement was taken. The first read the three tables it
already suspected; the second asked the database which tables the *schema* declares
append-only — grants of exactly `SELECT, INSERT` and nothing else — and then asked which of
those carry both triggers:

| Table | Layer 1 | Layer 2, before | After |
|---|---|---|---|
| `diagnostics`, `model_comparisons`, `transparency_artifacts` | grants | **nothing** | both |
| `objective_certificates` | grants | `TRUNCATE` only | both |
| `bandings`, `groupings` | grants | `TRUNCATE` only | both |

`objective_certificates` is mine, from the slice merged two hours earlier. `bandings` and
`groupings` are the ones worth recording: `c3d4e5f6a7b8` states the protection in a comment
— *"Insert-only at the privilege layer, so the rule survives a direct `UPDATE` from a psql
session"* — and then creates the `TRUNCATE` trigger alone. The sentence had been in the tree,
false, since #72 on 2026-08-15, and `test_transformations.py`'s test of it passes
because it does `SET LOCAL ROLE gip_app` first, which is the one connection the claim was not
about.

| Delivered | Evidence |
|---|---|
| `e1f2a3b4c5d6` attaches `artifact_append_only()` to all six | six `_no_modify` triggers, three `_no_truncate` |
| A negative test per table, run as the **owner** | `test_an_artifact_cannot_be_rewritten_from_the_owner_connection`, parametrised over the six: `UPDATE`, `DELETE` and `TRUNCATE` each refused, and the row still there |
| The invariant, checked as an invariant | `test_every_table_the_grants_call_append_only_carries_both_triggers` derives its table list from the grants, so a seventh table built with layer 1 alone fails on the day it is added |
| The derived test's own blind spot, closed | `test_the_application_role_holds_only_select_and_insert` now pins all eleven tables explicitly: a table regranted `UPDATE` would otherwise drop out of the derived set and be checked by nobody |
| `01` FR-DATA-47 and `02` §4.12 amended | The requirement is now stated as the invariant rather than as a list of three, with the corrected count and the date |

**Enforcement proven against broken input**, both layers: dropping `groupings_no_modify`
fails two tests (`DID NOT RAISE DBAPIError`, and `missing a trigger: [('groupings', 0, 1)]`);
granting `UPDATE` back on `diagnostics` fails two others, including the set-equality guard
that keeps the derived test from passing vacuously.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| The false comment in `c3d4e5f6a7b8` | **Left as written.** A merged migration is a dated record; `e1f2a3b4c5d6`'s docstring and this entry record that the claim was untrue and when it stopped being so. Editing the old file would remove the only evidence of how long it stood |
| `test_transformations.py`'s `SET LOCAL ROLE gip_app` test | **Left as written, and now honest.** It tests layer 1, which is what it does; the owner path it overstates is covered by the new test rather than by rewriting it |
| An artifact table checked at the ORM layer as well | **Not started, and probably never.** `DiagnosticsRow` and its siblings carry the claim in a docstring only. The database is the layer that cannot be bypassed, which is the whole argument of FR-DATA-42 |

#### W5 slice — five decisions, and §3.3 as an evidence floor, 2026-08-18

Five open questions decided in one pass, and the plan's own gate table repaired while doing
it. Four of the five appended a requirement and stopped there, which is the correct
deliverable for a later phase (`CLAUDE.md` §0); the fifth was buildable today and was built.

| Question | Decision | Requirement | Built? |
|---|---|---|---|
| **OQ-MODEL-10** | The GLM approximation of a GBM is a **Model** in its own right | `02` FR-MODEL-96 | No — **Phase 1b**, before anything references a transparency artifact by identifier. After that it is a migration rather than a decision |
| **OQ-MODEL-11** | An `approximation`-mode Rating Version must show a dislocation run against itself in `exact` mode, inside a workspace-declared threshold | `03` FR-RATE-61 | No — **Phase 2**, with the deployment path it gates |
| **OQ-MODEL-12** | An `interaction` operand must resolve to levels; no product term at any intent | `02` FR-MODEL-97 | Already built — the requirement ratifies the interaction slice's refusal and names the `diagnostic`-intent variant as the likely eventual answer |
| **OQ-MODEL-13** | One interval kind until a **named consumer** asks for a second | `02` FR-MODEL-98 | Already built — the requirement supplies the trigger the row could not, so "revisit when there is a consumer" stops depending on memory |
| **OQ-GOV-7** | `06` §3.3 is a **floor**; §4.2 may add and never remove | `06` FR-GOV-37 | **Yes** — its precondition had fired twice over |

**The floor, in three mechanisms.** The objection to a floor was never that it is wrong, it
is that a submission refused for evidence the policy does not mention is an error nobody can
act on. So the floor is restated in §4.2's own text; `PUT /approval-policy` refuses a policy
that drops below it with `POLICY_BELOW_EVIDENCE_FLOOR` naming the artifact type and the
kinds; and submission checks the **union** of floor and policy, so a policy stored before the
floor existed cannot sit below it either. `EVIDENCE_FLOOR` lives in `model-schema` beside
`DEFAULT_POLICY` — one shape, one place (`CLAUDE.md` §2).

**The enforced floor is §3.3's *checkable projection*, and the rest is named with an owner.**
Submission fails closed on a kind it cannot verify (`06` R4), so a floor naming
`model_comparison_if_predecessor` — which lives inside a comparison's `payload` and cannot be
queried — would have refused every model submission rather than raising the standard.
FR-GOV-37 says which kinds are enforced, which are not, and who owns each remainder.

**Two divergences found while building it, resolved rather than aligned.** `06` §4.2's `model`
entry lists three evidence kinds and `DEFAULT_POLICY` shipped one; §4.2's `rating_version`
entry lists six against three. The code was right for the day it was written and the page was
right about the destination, and §4.2 now carries a dated note saying so. The sharper one:
the submission check answered a kind it spelled `transparency_artifact` while the spec spells
it `transparency_artifact_if_non_glm` — so a workspace that copied the kind off the page got
a **fail-closed refusal for evidence it had**. Both spellings are accepted now and the spec's
is canonical.

**The gate table was missing four questions and double-counting a fifth.** `OQ-MODEL-12`,
`OQ-MODEL-13`, `OQ-MODEL-14` and `OQ-GOV-8` had been raised, mirrored and invisible to the
plan; `OQ-GOV-7` was counted at both 1b and Phase 3 because the Phase 3 row carried a
parenthetical naming it. That parenthetical is now prose beneath the table, where it cannot
be counted. This is the fourth time this exact defect has been recorded — `audit-docs.py`
checks the spec ↔ register mirror and cannot see this table at all, which is the argument for
the `docs-audit` skill's snippet being run at every raise *and* every decision, not only at a
raise.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| `02` FR-MODEL-96 — the approximating Model | ~~**Deferred, Phase 1b**, with the deadline stated in the requirement.~~ **Delivered 2026-08-19** (PR #120), and the deadline was the reason it landed when it did: before anything referenced a transparency artifact by identifier, so it stayed a decision instead of becoming a migration. See the GLM-approximation slice record below. *(Original verdict, kept:)* `approximating_model_id` stays `None` meanwhile, which is FR-MODEL-87's declared-and-unbuilt state with a trigger attached |
| `03` FR-RATE-61 — the approximation deployment gate | **Deferred, Phase 2.** Needs FR-RATE-46 built; nothing in Phase 1 deploys a Rating Version. Building it now would be building ahead of the phase |
| `model_comparison_if_predecessor` in the enforced floor | **Deferred**, owner: the slice that gives `model_comparisons` a queryable model reference. Named in FR-GOV-37 rather than left to be noticed  **Owner named 2026-08-22: W17**, which owns FR-GOV-9..19 and evidence enforcement, and is therefore where a queryable model reference on a comparison belongs. The same workstream took `06` §3.3's per-peril-model-approvals remainder on the same day, for the same reason — both are evidence kinds the floor cannot name while they live inside a JSONB payload, and both are W17's subject rather than a passing slice's. |
| §3.3's factor/banding/grouping **rationale** evidence | **Not started** — unmodelled, no artifact holds it. Owner: Phase 1b |
| §4.2's `rating_version` and `deployment` entries in `DEFAULT_POLICY` | **Left as they are.** Their floors are declared in `EVIDENCE_FLOOR` and enforced on any workspace that adds an entry; adding entries for artifacts nothing can submit yet would be shipping a policy for a Phase 2 capability |

#### W5 slice — what a penalised fit may claim, 2026-08-18

`glum` warns on every penalised fit that its covariance matrix *"will be incorrect"*, and the
suite has been printing that warning since the prediction slice. It is right: the matrix is
the information matrix of the **unpenalised** problem, and it knows nothing about the
shrinkage that produced the coefficients beside it. OQ-MODEL-14 asked what such a fit may
report. **`02` FR-MODEL-99 is the answer: report both numbers, and state the basis.**

**The recommendation on file was a rule about how to decide, not an answer** — *decide
FR-MODEL-21 and FR-MODEL-63 together, not for the interval alone* — and honouring it is what
settled the choice. The interval inherits the matrix from the standard errors rather than
introducing it, so refusing the interval would have had to take the standard errors with it,
leaving a penalised fit reporting **no uncertainty at all**. That is what ruled the honest-
looking option out: not that it was wrong about the matrix, but what it would have cost the
half of the question nobody was asking about.

| Delivered | Evidence |
|---|---|
| `UncertaintyBasis` — `information_matrix` \| `unpenalised_information_matrix` | One vocabulary for both halves, in `model-schema` beside `UncertaintyKind`. `02` R5 is about what the platform *claims*, and this is the claim |
| `GlmSpec.uncertainty_basis`, the **single** derivation | Derived from `alpha`, never stored on the fit result: the spec is pinned by `spec_hash` and immutable, so a stored copy could only agree or be wrong (`CLAUDE.md` §2). No migration, no nullable, no fallback |
| `Model.uncertainty_basis` | The reader for FR-MODEL-21's half — a coefficient surface asks the Model rather than deriving `alpha > 0` for itself. `None` for a GBM, where FR-MODEL-77 refuses an interval outright and there is no matrix to describe |
| `Uncertainty.basis` on every prediction | Populated from the spec in `_score_glm`. The validator **refuses an interval with no basis**, so the qualification cannot be dropped by the next caller rather than merely being present in this one |
| Both directions tested end to end | A penalised fit through the real Job reports `unpenalised_information_matrix`; an unpenalised one reports `information_matrix`. Without the second, a field hard-coded to the first would pass |

**Two things the build decided that the question had left open.** The basis is read from
`alpha`, **not** from `glum`'s warning text — the fit swallows that warning inside
`catch_warnings`, and a library's prose is not a mechanism; it can be reworded in a patch
release without anything failing. And `l1_ratio` alone does not make a fit penalised: at
`alpha = 0` there is no penalty to mix, so reading the basis off the mix would have labelled
every elastic-net default approximate. Both are pinned by tests rather than left in a comment.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| The **correct** penalised covariance — bootstrap or a penalty-aware sandwich | **Deferred with a named trigger**, which is the half of this decision that stops it decaying: built when the first consumer needs valid penalised inference — a surface that renders coefficient intervals on a penalised fit, or an approval that cites them. ~200 refits is a different cost class from a fit, so it is a Job and not a fit-time step. Owner: the slice that builds the first such consumer  **Owner named 2026-08-22: Phase 1b, gated on a consumer existing.** "The slice that builds the first such consumer" describes a trigger, not an owner — but unlike the other four this one is *genuinely* conditional, because the work is ~200 refits as a Job and nothing today renders or cites a coefficient interval on a penalised fit. The honest verdict is therefore **not started, Phase 1b, with the trigger stated**: the first view or export that shows an interval for a `select_by == "cv"` fit. Recording the trigger *and* a phase is the difference between a deferral and a silence. |
| A coefficient surface that renders the basis | **Not started, and nothing to start on.** Regularisation has no UI and nothing in `02` §4.11's comparison reads the intervals — which is why FR-MODEL-21's half ships as a property with a stated reader rather than as a rendered label |
| Suppressing `glum`'s warning now that the platform states the same fact | **Rejected.** The warning is the library telling the truth about its own return value, and a repository that silences it keeps the fact only where its own code remembers to look |

#### W5 slice — the boundary that keeps a scoring image cheap, 2026-08-18

OQ-PLAT-3 decided that scoring ships in the same image through Phases 1–2 and gets its own
from Phase 3. The image is Phase 3 and stays there. What cannot wait is the property that
makes it a repackaging rather than a rewrite: **the scoring path must never grow a dependency
on the libraries that fit models**, and two phases of modelling work sit between the decision
and the split.

`07` **NFR-PLAT-11** is that property, and it is enforced by scoring a real Model in a
subprocess where `glum`, `scikit-learn`, `celery` and `dagster` cannot be imported — asserting
the Poisson identity, so the design reconstructs, the base level resolves and the offset
applies with the fitting stack absent. ADR-0003 is what makes that possible at all; this is
the first check that it is *still* true.

**An import-linter contract is the wrong instrument, learnt by writing one.** The obvious
mechanism was a fourth contract in `.importlinter`, and it reported four violations on its
first run — `predict → glm → glum`, `predict → factors → bandings → sklearn`, and two more.
Every one of those imports is **already at its call site**, inside `fit_glm`,
`propose_banding` and `propose_grouping`, which is exactly the discipline the requirement
wants. import-linter reads the AST and cannot tell a function-scope import from a module-scope
one, so the only ways to green the contract were to weaken it or to move modules that have no
other reason to move. The requirement records this, because the next person to reach for
import-linter here should not have to rediscover it.

| Delivered | Evidence |
|---|---|
| `test_scoring_without_the_fitting_stack.py` | Fit in the parent, score in a child with a `MetaPathFinder` refusing the fitting stack. Artifacts cross as JSON, which is also the shape a scoring service receives them in (ADR-0003) |
| A test that the blocker blocks | Without it a `Blocker` returning `None` for everything would let the first test pass while importing `glum` freely — a green check proving nothing, which is what this kind of test is most prone to |
| `xgboost` / `lightgbm` deliberately **not** blocked | `02` FR-MODEL-62 scores a GBM by loading its JSON booster. Found by checking the requirement against FR-MODEL-62 rather than by reasoning about what a scoring service obviously needs — the first draft had both on the forbidden side |

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| The separate scoring image | **Phase 3**, unchanged by this. Building it now would be building ahead of the phase; the point of the slice is that it will be a repackaging |
| The scoring API entry point in the test's scope | **Not started — there is no scoring API.** `03` is Phase 2. The requirement names the extension explicitly: the slice that builds it adds that path to this test rather than adding a second mechanism |
| `03` FR-RATE-62/63/64 | **Spec only, Phase 2**, which is the rule and not a shortfall (`CLAUDE.md` §0) |

#### W5 slice — the profile contract, and a divergence that had been recorded for four days, 2026-08-19

`docs/roadmap.md` had carried a row since 2026-08-15 saying that `ColumnProfile` has no
`histogram` while `01` §4.7's example **and** `docs/contracts/schemas/profile.schema.json`
both declare one. It was recorded and then built around — the state `CLAUDE.md` §0 exists to
prevent, since a divergence written down and left alone is indistinguishable, from the next
slice's point of view, from one nobody noticed.

**The contract was right and the requirement was incomplete.** FR-DATA-25 enumerates the
statistics profiling produces and never named this one, so `01` gains **FR-DATA-48** rather
than the schema losing a field. Bins are equal-width over the observed `[min, max]` with
edges chosen in Python, not by either engine's own histogram function: FR-DATA-27 requires
one answer regardless of engine, and every divergence `test_the_two_profiling_paths_agree`
has ever caught came from an engine default.

| Delivered | Evidence |
|---|---|
| **FR-DATA-48** — `Histogram` on `ColumnProfile` | One frozen shape in `model-schema` with three invariants: one more edge than bins, strictly increasing edges, one exposure weight per bin when exposure is present |
| Both profiling engines compute it | `profile_frame` (Polars) and `profile_parquet` (DuckDB), sharing `_histogram_edges` so the bin boundaries cannot drift. `test_the_two_profiling_paths_agree` carries the histogram free and **agreed on the first attempt, with no tolerance added** |
| **FR-DATA-46** delivered | `severity_minor` → `mean_severity`, `burning_cost_minor` → `mean_burning_cost`. Both are ratios, not amounts; `_minor` is reserved for integer minor units (FR-OVR-7). The hand-written money-scan exclusion in `backend/tests/test_contracts.py` is **deleted, not grown** — the new names do not match the scan's pattern |
| `profile.schema.json` generated for the first time | 21 generated contracts, up from 20. The hand-written Phase-0 schema and the model were compared against each other for the first time and **six divergences** were reconciled, each with a written verdict for which side was wrong |
| `Profile.job_id` and `Profile.weight_column` | The contract declared both and the model carried neither. Both are now wired from the real profiling path: `store_profile` had always taken a `job_id` that `_profile_version` never passed, so `ProfileRow.job_id` and the `profile.created` audit event had been persisting `NULL` for **every** profiling Job since the handler was written |
| The Profile view renders histograms | `HistogramChart.vue`, ECharts, exposure plotted beside counts on a second axis when the profile carries it. `01` §5.3's Contents item, one of the six the W6a record listed as missing |
| The dtype label uncoloured | It was tinted by `psiBand(null)`, which returns `"stable"` before any threshold — so it was never showing a PSI band, only the colour of one, on a view with no comparison in it |

**What it found, beyond the histogram:**

- **`ColumnProfile.row_count`** — the one of the six nobody had predicted. Verdict: model
  right, and load-bearing: it is `VR-DST-6`'s standard-error divisor and gates the check.
- **The `job_id`/`weight_column` wiring shipped with zero assertions.** Deleting it left the
  whole suite green. Closed in `fe3e020`, and the obvious assertion was the wrong one — the
  model's default for `weight_column` and the fixture's exposure column are both
  `exposure_years`, so a backend assertion passes whether or not anything records the
  argument. The real proof profiles a frame whose exposure column is named `earned_years`.
- **`scope-audit.py DATA --catalogue VR` reads 1 / 38, not 38 / 38** — found by running the
  audit rather than quoting it. Not a regression; see the corrected W6a row above.
- **Five scalar-type divergences between the hand-authored contracts and the models**,
  found in this slice's closing review by reading the branch diff file by file rather than
  by any check. `mean_severity` and `mean_burning_cost` declared `MoneyMinor` —
  `{"type": "integer"}` — in both `profile.schema.json` and `banding.schema.json`, against
  `float` in `OneWayRow`; and `profile.schema.json` typed `severity_ci`'s two bounds as
  integers where `banding.schema.json`'s copy of the identical shape typed them as numbers.
  The published contract therefore asserted exactly the rounding **FR-DATA-46** exists to
  forbid, three commits after the rename that requirement asked for. **All five predate the
  slice** — `severity_minor: MoneyMinor` against `float | None` at the branch base — so the
  rename moved a divergence under new names without looking beneath them. Fixed here, with
  the record in `01` §4.7's note of 2026-08-19.

  The useful half is why nothing caught it: **every conformance test compared field names.**
  `test_the_column_profile_shape_matches_its_contract` was written specifically to look one
  level deeper than the flat tests and still compared only the property names it found
  there — the same claim the four earlier `Banding`/`Grouping` divergences also satisfied.
  `test_generated_and_authored_agree_on_scalar_types` now compares admitted JSON types
  across all six shapes carrying both a generated and a hand-authored contract, following
  `$ref`s between files and unwrapping `anyOf`. It deliberately ignores `null` (the two
  sides differ on nullability uniformly, which is its own reconciliation) and compares only
  paths present on both sides, so `top_levels` — a *structural* disagreement — stays
  FR-DATA-49's with an owner rather than becoming an exemption entry here.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| **FR-DATA-49** — `top_levels` carrying `exposure_years` per level | **Deferred, owned, and appended rather than negotiated away.** The contract declares `{level, count, exposure_years}`; the model carries a two-element `(str, int)`. Closing it means per-level exposure in both engines plus every reader that treats the item as `(str, int)` — 22 call sites across 7 non-generated files, including the distributional validation layer. That is a feature the size of this slice, not a reconciliation. The contract is **not** edited down to what was built (`CLAUDE.md` §14). Owner: W5's next slice, or whoever picks up FR-DATA-49 |
| **OQ-DATA-9** — `Dataset` has no status, validated-at or owner | **Raised open and deliberately not decided by this slice; decided by the maintainer 2026-08-19.** `01` §5.3's dataset list asks to display all three and §4.1 never defined them. There are two defensible answers — `Dataset` gains the three fields, or §5.3 means the *latest version's* status and validated-at plus a workspace-level owner — so it is recorded with options and a recommendation (read them off the latest version, but give `Dataset` an explicit `owner_id`, because no version carries ownership and `06`'s RBAC will need a subject) rather than being silently picked. **The recommendation was accepted 2026-08-19** and applied as `FR-DATA-50` (`latest_version_status` and `last_validated_at` derived per request, never stored — and the date scoped to the most recently *validated* version, not the latest, so a fresh draft above a validated version does not read as never validated) and `FR-DATA-51` (`Dataset.owner_id`, explicit). **Still not delivered: W6b's, with the trigger in each requirement** |
| **`01` §5.3's PSI comparison selector** | **Built 2026-08-19.** `compareProfiles()` has its caller; the reference-version picker lives in the route query (**OQ-DATA-11**), versions with no stored profile are disabled rather than offered, and each column card carries a `ColumnDrift` block banded against `VR-DST-1`. The Contents claim is now met rather than annotated. |
| The other four of the W6a record's six §5.3 Contents items | **Unchanged, still W6b's** — dataset status/validated/owner (**unblocked 2026-08-19** — OQ-DATA-9 decided, `FR-DATA-50`/`FR-DATA-51` say what to build), the lineage graph, and threshold editing in the rule set editor |
| `NFR-DATA-1` / `NFR-DATA-2` | **Unchanged** — measured, not tested; W4's verdict stands |

**Retrofit list (§5):** untouched. No new money field, no new artifact type, no schema
migration; `mean_severity` and `mean_burning_cost` were floats before the rename and are
floats after it, which is the whole point of FR-DATA-46. **In the model.** The published
contract had been calling both of them integers since before this slice began, which is the
one place a money-discipline claim actually reaches an external consumer — worth stating
plainly, because "the retrofit list is untouched" was true of the code and not of the
contract, and the two are the same promise.

**Gate (local, 2026-08-19, both halves, each exit code read on its own):** ruff clean ·
mypy --strict on 125 source files · import-linter 3 kept / 0 broken · **1264 python tests**,
zero skipped, with compose up so the Postgres-backed job tests actually ran ·
docs audit, 476 requirements across 8 specs · req-coverage 223 of 476 marked (46.8 %) ·
**21 generated contracts match** · `pnpm install --frozen-lockfile` · `generate:api` ·
eslint · `vue-tsc --build` · **109 frontend tests** · `pnpm build`.

**Enforcement proven against deliberately broken input** (§13 step 4): the nested contract
conformance test bit on all four mutations, in both directions; `job_id=None` in the worker
failed the artifact assertion with `assert None == UUID('01a018f2-…')` and, after this
slice added the assertion on the persisted column, fails there too; and passing
`weight_column="exposure_years"` in place of the recorded argument failed with
`assert 'exposure_years' == 'earned_years'`.

The type comparison added in the closing review was broken three ways before being trusted.
Restoring `MoneyMinor` on `banding`'s `mean_severity` failed with *"the model and the
contract disagree on the type of `band_stats.[].mean_severity` (model ['number'], contract
['integer'])"*. Retyping `profile`'s `severity_ci` bounds as integers failed the same way at
`one_ways.[].rows.[].severity_ci.[]` — **but only after a second fix**: the first walker read
`items` and not `prefixItems`, and Pydantic emits a fixed-length tuple as `prefixItems`, so
the deliberately broken interval passed. Every tuple field in every contract was invisible
and nothing said so. Removing the `prefixItems` line again fails
`test_the_type_comparison_reaches_the_one_way_row` on both shapes, naming the path it can no
longer see. That test names its three paths rather than counting them, because the first
attempt at a control — comparing aligned paths against a fraction of the walker's own output
— did **not** fire when the walker was crippled: a walker that stops descending shrinks the
numerator and denominator together, so the threshold moves out of the way of the defect it
exists to catch. An exemption entry for `top_levels` was written and then deleted for the
adjacent reason: with the walker fixed, that divergence is a path mismatch rather than a
type mismatch, so the entry suppressed nothing and only made the list look load-bearing.

#### W5 slice — `top_levels` carries exposure per level, 2026-08-19

**FR-DATA-49 delivered.** `ColumnProfile.top_levels` moves from an unnamed
`tuple[tuple[str, int], ...]` to `tuple[LevelCount, ...]` — `{level: str | None, count: int,
exposure_years: DecimalStr | None}` — computed by both profiling engines and read under
those names everywhere `top_levels` is read. **The authored contract needed no edit**:
`docs/contracts/schemas/profile.schema.json` had declared `{level, count, exposure_years}`
since Phase 0, so this slice moved the model to the document rather than the other way
round — the same direction the profile-contract slice moved a day earlier.

| Delivered | Evidence |
|---|---|
| `LevelCount` in `model-schema` | `{level, count, exposure_years}`, `frozen`, `extra="forbid"`. `exposure_years` carried its own `field_validator` refusing a `float` outright — the one strict `DecimalStr` field in the repository. **Superseded 2026-08-19** when `OQ-OVR-8` was decided: the rule moved onto `DecimalStr` itself and the field-scoped validator was deleted (FR-OVR-18) |
| Both profiling engines compute per-level exposure | `profile_frame` and `profile_parquet` share `_stored_exposure`, so the two cannot compute it two different ways |
| Every reader moved off positional access | `compare_profiles` and `_psi` in `pricing_core.data.profile`; `validate.py`'s `_level_counts`, `_psi_column` (`VR-DST-1`), `_new_level` (`VR-DST-2`) and `_vanished_level` (`VR-DST-3`) |
| `VR-DST-3`'s fallback corrected | Where no `one_ways` summary exists, the fallback now reads `exposure_years` and drops to `count` only when the version carried no exposure column — it previously used count *as if* it were exposure, contradicting the rule's own definition ("levels with material reference exposure") |
| Nulls excluded from three checks | `str(level)` no longer coerces a null to the literal `"None"`. `VR-DST-1`'s PSI, `VR-DST-2` and `VR-DST-3` now exclude nulls from both sides — **this moves published PSI numbers on columns carrying nulls**, and a column that had nulls in the reference and none now no longer reports a phantom vanished level. `VR-DST-4` null-rate-shift retains the signal; both changed checks were previously double-counting it under an accidental level name |
| The nested conformance test deepened | `test_the_column_profile_shape_matches_its_contract` now descends into `top_levels`' item and compares its property names, closing the exact blind spot that let the shape divergence hide behind a matching container name. **Proven against deliberately broken input**: an invented property added to the authored contract was confirmed named by the test, then reverted (`57a0cc0`) |
| The Vue chip list shows exposure per level | `ProfileView.vue`'s `top_levels` chips render `exposure_years` beside `count`; no new §5.3 Contents item — this corrected one that already existed |

**Both questions decided 2026-08-19** (they were raised by this slice and answered in the
next one; the slice record is below):

- **`OQ-DATA-10`** — **decided: defer both halves, together, until a consumer needs an
  exposure-ordered view.** Selection stays by count and `VR-DST-1`'s PSI stays
  count-weighted. FR-DATA-25 is amended to say so — the spec asked for two selections and
  the platform produces one, and the spec was the side that was wrong. The deferral, its
  trigger (a named reader: `02`'s factor workbench or a monitoring view) and its
  deliberately **unowned** status are **FR-DATA-52**.
- **`OQ-OVR-8`** — **decided: `DecimalStr` refuses a `float` at validation** (FR-OVR-18),
  delivered the same day, `Relativity` included. `LevelCount.exposure_years`'s field-scoped
  validator is deleted rather than duplicated.

**Gate (local, 2026-08-19, both halves, each exit code read on its own):** ruff clean ·
mypy --strict on 125 source files · import-linter 3 kept / 0 broken · **1281 python tests**,
zero skipped · docs audit, 478 requirements across 8 specs, 63 open questions all mirrored ·
req-coverage 224 of 478 marked (46.9 %) · **21 generated contracts match** ·
`pnpm install --frozen-lockfile` · `generate:api` · eslint · `vue-tsc --build` ·
**113 frontend tests** · `pnpm build`. `backend/tests/test_demo_guide.py` — 11 passed; the
guide is derived (FR-PLAT-54) and needed no hand edit.

#### Slice — the exact-decimal types refuse a float, and the audit that decided it (2026-08-19)

`OQ-OVR-8` and `OQ-DATA-10`, both raised by the `top_levels` slice the day before, decided
and applied. `OQ-DATA-10` is a deferral with a trigger (FR-DATA-52); `OQ-OVR-8` is a code
change (FR-OVR-18). **The audit the recommendation called "the real work" is what this
record is mostly about**, because it changed three things the decision had assumed.

| Delivered | Evidence |
|---|---|
| `DecimalStr` and `Relativity` reject a `float` | A shared `BeforeValidator` in `model_schema.money`. Refusal proven on a Python float, a float nested in a `tuple[DecimalStr, ...]`, `model_validate` of a dict, and `model_validate_json` of a JSON *number*; `str`, `int` and `Decimal` still accepted and the wire form still a string (`test_money.py`, five new `FR-OVR-7` tests) |
| `LevelCount.exposure_years`'s validator deleted | The inconsistency `OQ-OVR-8` recorded is resolved by generalising the strict field, not by leaving ten lax ones beside it |
| **The caller audit came back clean** | Every existing caller passes a `str`, an `int` or a `Decimal`. The paths that compute in float — both profiling engines, the numpy lift/AE bins, the double-lift bins — already quantised at the boundary, so `_stored_exposure` is now named in FR-OVR-18 as the pattern to copy. **No caller needed rerouting and the full suite passed unchanged**, which is the opposite of what the recommendation expected |
| **The affected-field count was wrong** | The question said "26 `DecimalStr` fields across 7 modules". There are **11, across 6** — the 26 was a count of every *line mentioning* `DecimalStr`, imports and `money.py`'s own definition included. Corrected in `docs/open-questions.md`, `00` §7 and here. A figure nobody had recomputed since it was written down, which is why `CLAUDE.md` §0 keeps counts out of prose |
| **A published contract was declaring three exact decimals as JSON numbers** | `docs/contracts/schemas/peril-structure.schema.json` typed `restoration_loading`, `ratio` and `tolerance` as `{"type": "number"}` while all three are `DecimalStr` the model has always serialised as strings — verified by dumping a real `Reconciliation` (`"1.010000"`, `"0.02"`). Wrong since Phase 0; strict input is what made it *reachable*, since a client following the contract now gets a 422 instead of a silent coercion. All three moved to the `Decimal` `$ref` every other schema in the suite already used, and the undeclared `loading_factor` added |
| The check that should have caught it, widened | `test_generated_and_authored_agree_on_scalar_types` compared **6** slugs while **12** schemas have both sides — and the six were never chosen, merely never added. Now 11, with `COMPARED_SLUGS` a named constant and `test_every_eligible_schema_is_compared` failing the day an eligible schema is neither compared nor pinned. **The check would have caught this contract on the day it was written** |
| The one divergence it surfaced is pinned, not fixed | Widening found `diagnostics`: `GlmDiagnostic.aliasing` is `tuple[str, ...]` against a contract declaring an array of untyped `object`. Neither side is obviously wrong — an object entry could carry `{term, aliased_with, reason}` — so it is **`OQ-MODEL-15`**, and `test_the_diagnostics_divergence_is_exactly_the_known_one` pins it at exactly that path. A *new* divergence in `diagnostics` still fails; the day `OQ-MODEL-15` is decided the pin fails and is deleted *(it was, 2026-08-21 — FR-MODEL-109: the names kept, the authored contract corrected to strings, the pin deleted)* |

**Enforcement proven against deliberately broken input**, all three, each reverted after:
the widened comparison fails on the pre-fix `peril-structure` contract; the coverage guard
fails when a slug is removed from `COMPARED_SLUGS`; the pin fails when a second divergence
is injected into `diagnostics.schema.json`.

**Not delivered, stated rather than left silent:** `ReconcileRequest.tolerance`
(`backend/src/app/api/peril_structures.py`) is a bare `Decimal`, so a JSON number is still
coerced there and stringified into the job parameters — the same hole one layer earlier,
and outside this change because it is an API request shape rather than an artifact field.
`ReconciliationResult` in `pricing-core` is a frozen dataclass and therefore unvalidated;
that is true of every `pricing-core` dataclass and singling one out would be arbitrary.
Both are recorded in `OQ-MODEL-15`'s neighbourhood rather than fixed here.

**Gate (local, 2026-08-19, both halves, each exit code read on its own):** ruff clean ·
mypy --strict on 125 source files · import-linter 3 kept / 0 broken · **1300 python tests**,
zero skipped · docs audit, 480 requirements across 8 specs, 64 open questions all mirrored ·
req-coverage 224 of 480 marked (46.7 %) · **21 generated contracts match** ·
`pnpm install --frozen-lockfile` · `generate:api` · eslint · `vue-tsc --build` ·
**113 frontend tests** · `pnpm build`. The docs audit failed once on the way, correctly: a
bolded `**FR-DATA-52**` used as a *cross-reference* reads as a second definition of it —
the trap `.claude/skills/spec-change` already documents, paid for again by not reading the
skill first.


#### W5 slice — paired quantile models, and the name a quantile pair had no right to (2026-08-19)

The twentieth slice, and the one that makes FR-MODEL-78 real: a GBM can now carry a
prediction interval, from two Models fitted with the `quantile` template and linked to the
model they bound. Two requirements appended, one open question raised and decided the same
day, and all four of `UnavailableReason`'s values reachable for the first time.

| Delivered | Evidence |
|---|---|
| `interval_for` on `GbmSpec`, joining `spec_hash` | `IntervalFor(model_id, model_version, alpha)`; `SPEC_HASH_VERSION` `v3 → v4` in the same commit as the field (FR-MODEL-86). Tests pin that two bounds against different central models, the two sides of one pair, and a bound versus an ordinary GBM all hash apart — the three collisions that would have let FR-MODEL-66 hand a caller somebody else's model |
| A bound must match the model it bounds | `_refuse_mismatched_interval_model` in `reserve_model`, before a Job exists: family, dataset version, split and **factor set** — the last compared as a *set*, since two specs listing the same factors in a different order describe the same design matrix |
| A bound must actually be a quantile fit | The rule the plan did not have and FR-MODEL-78's text does: the objective must resolve to the `quantile` template, at the same alpha `interval_for` declares. A bound fitted with `count:poisson` passes every structural rule and estimates the **mean** |
| One bound per side | FR-MODEL-100(iv). A second lower bound satisfies every other rule, and the response carries a single `level` with nothing to say which pair produced it |
| Bounds are findable | `load_interval_models`, ordered lower-first so no second caller sorts them another way, plus a **partial** functional index on `(spec -> 'interval_for' ->> 'model_id')` — partial because almost no model is a bound, and the common answer (none) is the one that must stay cheap |
| Crossing detected at fit time | `detect_quantile_crossing` in `pricing-core`, and `QuantileCrossing` on the **second** bound's `GbmDiagnostics`. The first has no counterpart when it is fitted and FR-MODEL-49 computes diagnostics once, so there is no later pass in which to fill it in |
| Crossing refused at predict time | 409 `MODEL_INTERVAL_UNAVAILABLE` naming the rows and the worst gap. Without it the honest finding reached `PredictedRow`'s ordering validator and became a 500 with the reason in a traceback |
| All four `UnavailableReason` values reachable | `_score_gbm`'s four arms, most-specific-first, and a test that pins the order |

**The requirement named a thing the contract had no word for, and that is the finding.**
FR-MODEL-98 (decided the day before, OQ-MODEL-13) fixed the platform at **exactly one**
interval kind, `confidence_interval_mean`, and reserved `prediction_interval` for a `φ·V(μ)`
computation over aggregates. FR-MODEL-78's deliverable is neither: a quantile pair covers
`Y`, not `E[Y|x]`, and it is produced per row by a different estimator entirely. Raised as
**OQ-MODEL-16** rather than picked (`CLAUDE.md` §0) and **decided by the maintainer the same
day** at the recommendation — a third member, `quantile_pair_interval`, specified as
**FR-MODEL-101**. Neither existing value is widened and the reserved name is left waiting for
the consumer that triggers it, so **FR-MODEL-98 is amended by addendum rather than edited**
(`CLAUDE.md` §14). The argument that admits it is FR-MODEL-98's own: it refused a second kind
shipped *before a consumer existed*, and FR-MODEL-78's pair is opt-in at 2–3× the fit cost,
so nobody receives one without having asked.

**FR-MODEL-77 named two reasons and did not say what they meant.** `interval_models_not_approved`
and `interval_models_stale` had been declared and unreachable since the prediction slice, and
each had two defensible readings. Making them reachable forced the choice, so it is recorded
as a requirement rather than made in code: **FR-MODEL-100(ii)** reads "not approved" as *less
reviewed than the model it bounds* — the strict reading would make the feature unusable at
exactly the point an actuary is deciding whether the bounds are any good — and **(iii)** reads
"stale" as *the central Model is `superseded`*, the literal reading of FR-MODEL-77's own
parenthetical, reachable because `SCOREABLE_MODEL_STATUSES` admits `superseded`. Both
alternatives are named in the requirement, so a later reader can see they were decided.

**Two orderings are load-bearing, and both are pinned by tests.** The pairing check runs
**before** the factor check: a bound naming the wrong dataset version also fails factor
resolution, and reported the other way round the caller re-checks factors that were never
wrong. And `_score_gbm`'s staleness arm runs before its approval arm, so a superseded model
with unapproved bounds is told the family has moved on rather than told to go and get bounds
approved for a version nobody should quote.

**Three fixtures were corrected by the platform rather than the other way round**, which is
the shape worth recording: a `custom_objectives` CHECK refused an objective stamped
`approved` without a certificate, so the fixture now certifies through the real Job; a factor
must name a column the dataset actually has; and FR-MODEL-44 requires a spec naming a custom
objective to declare its `response`. A fourth was mine alone — a `unit_of_work` opened inside
another takes a second connection and **deadlocks against the pool rather than failing**, so
the run hung with no output at all.

**Enforcement proven against broken input**, each neutralised in turn and restored:
the structural mismatch check reddens 3 tests; the quantile-template check 2; the
one-bound-per-side check 1; the fit-time crossing attachment reddens the pair test with
`assert None is not None`. The `Uncertainty` validator additionally refuses a `level` that
disagrees with the alphas it came from — a 0.05/0.95 pair covers 0.90, and a response
claiming 0.95 overstates its coverage by exactly the amount a reader cannot check.

**Not delivered, with owners.** **No frontend**: nothing renders a GBM interval or a
crossing figure, so both are reachable only over the API — `02` §5.3's model-detail view is
**W6b**'s and building it here would be building ahead of the row that owns it. The
`alpha != 0.5` refusal is a validator and **has no JSON Schema form**, so the published
contract carries the range and not the median rule; the type is its only enforcement.
FR-MODEL-100(ii) is implemented as the single case that matters — an `approved` central model
with a not-`approved` bound — rather than as a general lifecycle ordering, because `02`
declares no such ordering and inventing one would be specifying a comparison nothing needs.

**Bookkeeping corrected while here:** W5's row said "eighteen slices in" and the
exact-decimal slice (PR #116, 2026-08-19) had already landed without being added to it. The
row now reads twenty and names both.

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (125 source files) ·
import-linter 3 kept / 0 broken · **1339 python tests, zero skipped** in 315 s (was 1300) ·
audit-docs 0 — **482 requirements** across 8 specs (was 480), **65 open questions** all
mirrored (was 64) · req-coverage **227 of 482 marked, 47.1 %** (was 224 of 480) ·
`generate-contracts.py --check` 0, **21 generated contracts match** ·
`pnpm install --frozen-lockfile` · `generate:api` · eslint · `vue-tsc --build` no errors ·
**113 frontend tests** · `pnpm build`. `scope-audit.py MODEL --endpoints`: **FR-MODEL-78
leaves the unevidenced list**, which falls 21 → 20, and FR-MODEL-100/101 land evidenced —
113 in scope, 93 with evidence (82 %).

#### W5 slice — the GLM approximation as a Model, 2026-08-19

The twenty-first slice, and the one that discharged a deadline rather than answered a need:
FR-MODEL-96 had to land before anything referenced a transparency artifact by identifier,
after which it would have been a migration instead of a decision. **OQ-MODEL-10 was decided
by the maintainer as option A before execution began** — the inline coefficient table stays
as a legacy era, exclusive with `approximating_model_id`, rather than being migrated away.

| Delivered | Evidence |
|---|---|
| The approximation is a Model in its own right | `GlmSpec.approximates_model_id`, and `approximation_spec(spec, *, source_model_id)` deriving the surrogate's spec from the GBM's — `dataset_version_id`, `split_ref` and `factors` copied, `SURROGATE_RESPONSE_COLUMN` (`__gbm_prediction__`) as the response |
| The fidelity is measured against the booster **by mechanism** | `diagnostics.py` reads actuals as `data[spec.response_column]`, and that column *is* `__gbm_prediction__` — so the A/E is against the booster because the spec object says so, not because a comment does. Traced end to end in the final review rather than asserted |
| Two eras, mutually exclusive | A validator refusing a block that carries both inline coefficients and an `approximating_model_id`, and refusing one that carries neither |
| The legacy era cannot be deleted silently | Positive tests, added in the fix wave. Before them all three `GlmApproximation(` uses asserted *refusal*, so deleting the legacy fields would have left the gate green — the maintainer's option-A decision was protected by nothing the suite could see |
| A hand-written surrogate spec is refused | `_refuse_mismatched_approximation`, comparing exactly the three fields `approximation_spec` copies; `MODEL_APPROXIMATION_INVALID` declared in `02` §5.1 and registered in `errors.py` |
| `spec_hash` moved with the field | v4 → v5 in the same commit as `approximates_model_id`, contracts regenerated |
| FR-MODEL-102 appended | The maximum was 101, not the last id read. It carries the `-approx` slug convention the code needed and no spec stated: a source slug over 57 characters fails against the 64-character column |

**Three open questions raised, none decided here.** **OQ-MODEL-17** — a rebuild
(`should_fit=False`) pays a full GLM fit plus one type-III refit per factor for numbers it
then discards, because `store()` only persists them when `should_fit` is `True`.
**OQ-OVR-9** — nothing in this repository compares a spec's §5.1 error-code table against
`errors.py`; verified twice on this branch, and structural, applying to every module rather
than to `02` alone. **OQ-PLAT-7** — a `PlatformError` raised inside a Job handler loses its
`.code` to `JOB_HANDLER_FAILED`, which is why this slice's two refusal tests had to call the
handler directly instead of going through `execute_job`. *(OQ-MODEL-17 and OQ-OVR-9 decided
2026-08-21 — see §10; OQ-PLAT-7 remains open, placed on the any-time row.)*

**A check went red on purpose, from the first commit to the fifth.**
`test_errors.py::test_spec_error_codes_are_all_constructible` reads the spec's code list, so
declaring `MODEL_APPROXIMATION_INVALID` in `02` reddened it until the registration landed
four tasks later. Ruled deliberately rather than worked around: moving the registration into
the docs commit would have put a backend source edit inside a docs-only commit to buy a green
intermediate state nothing consumes. Same shape as PR #98 — a check that fires on the
*contract* goes red at a slice's first commit rather than its last.

**Measured, not asserted.** +0.26 s / ~7 % on the transparency Job, against a
**single-factor** fixture. That does not bound a multi-factor model — type-III diagnostics
refit the surrogate once per factor, which is exactly what OQ-MODEL-17 is about.
`type_iii=False` is the lever if it ever bites, and is not pulled without the maintainer.

**Not delivered, with owners.** No frontend renders the surrogate link or the approximation's
own model page — `02` §5.3's model-detail view is **W6b**'s. A stored block with *empty*
coefficients and no id is now refused on read; unreachable in practice, since the old builder
always emitted at least an intercept, so it is parked rather than guarded.

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (125 source files) ·
**1362 python tests, zero skipped** in 265 s (was 1339) · audit-docs 0 — **483 requirements**
(was 482), **69 open questions** all mirrored (was 66) · req-coverage **229 of 483 marked,
47.4 %** (was 227 of 482) · `generate-contracts.py --check` 0, **21 generated contracts
match**.

**Recorded late, and that is the process finding.** PR #120 updated W5's row in §6 and wrote
no slice record; this one was written 2026-08-19 from the branch's ledger and the merged
diff. It is the second such omission in W5 — the prediction slice (PR #102) is the first, and
is noted in the same row. A row's prose says a slice happened; only a record says what it
found.

#### W5 — outstanding work, derived 2026-08-19

**Derived from the specification first, then evidenced** (`CLAUDE.md` §13 rule 1):
`scope-audit.py MODEL`, then `--endpoints`. `02` declares no `XX-YYY-N` catalogue, so unlike
`01` there is no catalogue axis to check.

> **Superseded in part, 2026-08-20 — the custom-metrics slice landed.** The counts and the
> slice list below were true on 2026-08-19 and are no longer. Re-derived on 2026-08-20 by
> re-running the same two commands, with the current figures beside the originals; the
> 2026-08-19 column is kept rather than overwritten, because what was believed on the day a
> plan was made is the thing a governed record cannot lose. The requirement total rose by
> six because the slice appended FR-MODEL-103…108, all six of them evidenced; the
> unevidenced 19 are unchanged, and their verdicts below still stand.

| | Derived 2026-08-19 | Re-derived 2026-08-20 |
|---|---|---|
| Requirements in scope | **114** | **120** |
| With evidence | **95 (83 %)** | **101 (84 %)** |
| Without evidence | **19** | **19** |
| Endpoints declared in §5.1 | **35** | **40** |
| Endpoints published | **34 (97 %)** | **40 (100 %)** |

*(`uv run python scripts/scope-audit.py MODEL --endpoints` prints "declared: 40 · published:
40 (100%) · every declared endpoint is published in the contract";
`uv run python scripts/req-coverage.py` prints "requirements specified : 489 · requirements
marked : 235 (48.1%)" repository-wide.)*

~~**Five buildable slices remain**~~ — ~~**four**, corrected 2026-08-20: slice 1 below
is delivered~~ ~~**three**, corrected 2026-08-21: slices 1 and 2 below are delivered~~
~~**one**, corrected 2026-08-21: slices 3 and 4 below are delivered.~~ **None**, corrected
2026-08-22 by the audit-remediation slice: slice 5 — EBM — was delivered on 2026-08-21 by
the pass that struck its row below and left this counter at one. **Every row in this table
is now struck as delivered**, which is the state it was built to reach and the one thing it
never said. Four corrections in three days, each of them this counter lagging a strike made
in the same edit — the table below is the record and this line is a hand-maintained summary
sitting beside it, which is the arrangement §0 warns about.
Smallest first:

| Slice | Requirements | State, and what is actually missing |
|---|---|---|
| ~~**1. Custom metrics**~~ **— DELIVERED 2026-08-20** | ~~FR-MODEL-45's endpoint~~ FR-MODEL-45, 103–108 | ~~`POST /api/v1/custom-metrics` is the one unpublished endpoint of the 35. Deferred to Phase 1b by a dated amendment in `02` §5.1~~ **Built in the custom-metrics slice recorded below, not deferred to Phase 1b**: six routes rather than one, the artifact, table, certification Job and approval path, `eval_metrics` honoured (FR-MODEL-106) and early stopping on a Custom Metric (FR-MODEL-107). The deferral's reasoning — that a custom metric is `feval` and changes what early stopping optimises rather than what the model fits — turned out to be the argument *for* building it inside W5: FR-MODEL-107 made a Custom Metric the only way to early-stop under a callable objective at all |
| ~~**2. Regularisation and cross-validation**~~ **— DELIVERED 2026-08-21** | FR-MODEL-20, FR-MODEL-53 | ~~Already paired by a verdict on file — `select_by: cv` lives in the penalty path. The schema is ahead of the code: `GlmSpec` carries `alpha` and `l1_ratio`, and `cv_folds` exists. Missing are the documented penalty path, the CV selection option, declared fold construction (`random`, `temporal`, `grouped_by_key`) with a persisted seed, and per-fold metrics **and their dispersion** persisted as diagnostics rather than the mean alone~~ **DELIVERED 2026-08-21**: `GlmSpec.select_by`/`GlmSpec.cv` (FR-MODEL-20), `GlmCvSpec`'s three fold-construction methods via `pricing_core.data.splits.assign_folds` (FR-MODEL-53), `_fit_cv_path` in `pricing_core.modelling.glm`, and `Diagnostics.cross_validation` (`CrossValidationDiagnostics`/`CvPathPoint`/`CvFoldMetric`) persisting the full path and the selected alpha's per-fold dispersion. No new HTTP endpoint (the existing `GET /api/v1/models/{id}/diagnostics` surfaces it) and no frontend work (the Diagnostics view's CV screen remains W6b's). Two spec interactions found and resolved by dated amendment in `02-modelling.md`: K-fold `temporal` semantics (undefined by FR-DATA-33/FR-MODEL-53; resolved as contiguous time-ordered blocks) and FR-MODEL-99's `uncertainty_basis` under CV selection (resolved as unconditionally naive/penalised) |
| ~~**3. Tweedie power by profile likelihood**~~ **— DELIVERED 2026-08-21** | ~~FR-MODEL-22~~ | ~~Today `GlmSpec` only *validates* that a supplied power lies between the two families it spans. Missing: the grid, the persisted profile curve, and recording an estimated `p` as an estimate with its own uncertainty rather than silently baking it in as a constant~~ **DELIVERED 2026-08-21**: `GlmSpec.tweedie` carries the grid; `fit_glm` estimates p by profile likelihood (refit at each point, profile log-likelihood argmax scored with the Tweedie series density at the mean-deviance dispersion estimate), persists the curve on `GlmFitResult.tweedie`, and records the estimate with its 95% profile-likelihood CI — never a constant; a maximum at a scan edge is refused (`GLM_TWEEDIE_POWER_GRID_EDGE`); estimation × CV selection refused by name (FR-MODEL-87). |
| ~~**4. Offset from another model**~~ **— DELIVERED 2026-08-21** | FR-MODEL-24 | ~~`offset_model_ref` appears nowhere…~~ **— DELIVERED 2026-08-21:** `OffsetSpec.offset_model_ref` (renamed from the dead `model_ref` scaffold), GLM-to-GLM, resolved at fit/predict/backtest time, refused by name elsewhere. |
| ~~**5. EBM**~~ **— DELIVERED 2026-08-21** | FR-MODEL-37 | ~~Verdict on file: not started, owner is "the slice that first fits an `ebm` model" — and `ebm` is one of the four Model types in `CLAUDE.md` §7's vocabulary, so W5 owns it unless reassigned. The stated cost is `interpret` as a third heavy dependency serving one requirement~~ **DELIVERED 2026-08-21**: term shape functions exported verbatim as additive lookup tables; transparency artifact built from the export with no approximation; universal diagnostics through the shared partition; scoring from the tables alone (ADR-0003). The third heavy dependency is now installed, so the 'one requirement for a model type nothing fits' objection is discharged *(2026-08-21: delivered by the EBM slice — see the slice record below.)* |

**The NFR gap — 11 of 12 unevidenced**, and it is not one problem:

| NFRs | Verdict |
|---|---|
| NFR-MODEL-3, NFR-MODEL-12 | **Measured 2026-08-15 and recorded in `02` §9**, met for three of the four proposal methods. Unevidenced only because a measurement is not a marker — `CLAUDE.md` §13 rule 1's "evidence is not only markers" case. They need the measurement recognised as the evidence, not a test invented to stand in for it |
| NFR-MODEL-7, NFR-MODEL-8, NFR-MODEL-9 | **Testable today, no fixture needed.** Export/import round-trip with identical predictions; that user expressions never reach `eval`/`exec` and out-of-grammar input fails with a position-accurate error; that every named creation, fit and status transition emits an Audit Event with before/after state  ~~**Testable today**~~ **— two of the three were not, corrected 2026-08-22 by the audit-remediation slice, and each now has its own verdict in `02` §9.** **NFR-MODEL-9 was**, and is now evidenced (`backend/tests/test_model_nfrs.py`) for every act that has a before; five create events carry none, left as they are and pinned by a test, because a versioned artifact's create has no prior state. **NFR-MODEL-8 is half testable** — the `eval`/`exec` clause is now evidenced by removing both builtins and watching a legitimate expression still evaluate; the position-accurate error is **not met** (`ExpressionError` carries no `lineno`/`col_offset`) and the per-round time budget is implemented nowhere. **NFR-MODEL-7 has nothing to test**: a six-way search found **zero** Model export paths and zero import paths — no route, no CLI (`[project.scripts]` is empty), no bundle schema — and its parent FR-OVR-2 carries **zero markers**. Owner: **unassigned**, because it is a capability nobody has been asked to build |
| NFR-MODEL-4, NFR-MODEL-5, NFR-MODEL-11 | **Measurable today** against existing fixtures, because none of the three names a data scale: diagnostics adding no more than 30 % to fit wall-clock is a *ratio*, certification completes under 3 minutes, and a diagnostics artifact stays under 50 MB  **Measured 2026-08-22 and recorded in `02` §9.** NFR-MODEL-5 (0.42–3.56 s of 180 s) and NFR-MODEL-11 (0.13 MB of 50 MB, GBM path included) are **met with two orders of magnitude of headroom**. **NFR-MODEL-4 was not met as written** *(re-read 2026-08-22, OQ-MODEL-24 decided: re-scoped to exclude the per-factor block and re-set to 50 % at a named scale, it is now **met** at every measured arm; the type-III block moved to NFR-MODEL-13, which is **breached at 678 013 × 60**, and the GBM path to NFR-MODEL-14, which is met)*, and the cause is a sibling requirement rather than a slow function: FR-MODEL-51's type-III tests drop each factor and refit, so diagnostics cost one extra fit *per factor* — **510 %** of fit wall-clock at 12 factors, **1 388 %** at 24, **3 002 %** on the GBM path. Everything else `compute_diagnostics` does fits the budget at 9.0–9.5 %. The two requirements cannot both hold as written, so it is raised as **OQ-MODEL-24** with three options rather than tuned quietly |
| NFR-MODEL-1, NFR-MODEL-2, NFR-MODEL-10 | **Blocked on a fixture that does not exist.** All three name 5 M rows × 60 factors; freMTPL2 is 678 013 rows. Either a synthetic fixture is built, or they are measured at a stated smaller scale with the extrapolation written down. NFR-MODEL-2's second clause — a custom `expression` objective adding no more than 25 % — is **Phase 2** regardless, since expression objectives do not exist |
| NFR-MODEL-6 | **Evidenced.** The only one of the twelve carrying a marker today  ~~**Evidenced.**~~ **Half evidenced, corrected 2026-08-22.** The requirement asks for identical GLM coefficients to 1e-10 **and** an identical booster hash; the one marker it carries is the **booster** half, and nothing anywhere refits a GLM on the same `spec_hash` and seed to compare coefficients. Counted as evidenced because a marker existed — the same defect FR-MODEL-81 was caught by on 2026-08-16, applied to an NFR this time. **Owner: the GLM slice**, a two-fit determinism test beside the code it is about |

**Not W5, with the reason:**

| Requirement | Owner |
|---|---|
| FR-MODEL-40 — `expression` objectives | **Phase 2, W30**, behind `expression_objectives_enabled`. The route exists and answers `422` with that code rather than `404`, so a caller learns the capability is off rather than absent |
| FR-MODEL-6 — `expression` factors | **Phase 2, W30**, by OQ-MODEL-1's decision — its verdict on file reads "owned by that slice", and that slice is W30. **W30's carry-over list named FR-MODEL-40/41/75 and not FR-MODEL-6**; corrected 2026-08-19, **accepted by the maintainer 2026-08-22** — so W5 disowns it on a recorded decision rather than on a correction nobody signed. |
| FR-MODEL-82 — proxy detection | **Phase 3** by OQ-MODEL-7 (decided 2026-08-15), and by the requirement's own text. Through Phases 1–2 the platform's only treatment is FR-MODEL-5's `prohibited` flag, which refuses direct use and audits the attempt |
| `02` §5.3's model spec builder, model detail and diagnostics views | **W6b**, stated in the gradient-boosting and paired-quantile slice records |

**Three requirements had no verdict anywhere until this pass** — **FR-MODEL-20**,
**FR-MODEL-22** and **FR-MODEL-24** were unevidenced and unspoken for in every slice record,
which is the one option `CLAUDE.md` §13 rule 1 does not allow. They are recorded above as not
started, owner W5, by W5's own scope definition ("every `MODEL` requirement") rather than by
a new assignment. FR-MODEL-22's verdict is delivered by the 2026-08-21 Tweedie slice and
FR-MODEL-24's by the offset-from-another-model slice; FR-MODEL-23 is delivered: markers at `test_glm.py:134,:429` and `test_spec_hash.py:99,:114`, `GLM_SEPARATION_DETECTED` registered and declared — the 'remains unbuilt' lines were stale. The remainder — a bare non-`LinAlgError` `ValueError` from glum still reaches the job unwrapped — is recorded 2026-08-21 as unbuilt, owner W5.

#### W5 slice — custom metrics, and a field that was read by nothing, 2026-08-20

The twenty-second slice, spanning 2026-08-19 → 08-20. FR-MODEL-45 gives a Custom Metric
the same lifecycle and grammar as a Custom Objective, declared separately so it can be
reused across objectives — and the slice exists around a single finding: `GbmSpec.eval_metrics`
had been declared since Phase 0 and read by nothing. A caller could name a metric, builtin
or custom, and be told nothing was wrong while none were ever evaluated. FR-MODEL-106 now
requires it honoured.

| Delivered | Evidence |
|---|---|
| A Custom Metric artifact and table, declared separately from any objective | `custom_metrics` table keyed on `(workspace_id, slug, version)`, undeletable, definition frozen after creation (FR-MODEL-45/103) — nothing ties a metric to one objective, so the same metric ref resolves under any spec that names it |
| Six HTTP routes, mirroring `custom_objectives` | `POST /custom-metrics` (create/version), `GET /{id}`, `POST /{id}/certify` (202 + Job), `GET /{id}/certificate`, `POST /{id}/submit`, `GET /{id}/usage` (FR-MODEL-108) |
| `eval_metrics` honoured, not merely declared | `GbmSpec.eval_metrics` now drives `feval`/`custom_metric` wiring on both XGBoost and LightGBM, builtin and custom metrics alike (FR-MODEL-106) |
| `OBJECTIVE_EARLY_STOPPING_UNSUPPORTED` narrowed, not retired | Early stopping on a **builtin** metric under a callable objective is still refused — both backends hand it the raw score, not the transformed prediction. Only the availability of an alternative changed: declare a Custom Metric in `eval_metrics` and stop on that (FR-MODEL-107) |
| Two lifecycle edges that were declared and unreachable, now reachable | `draft → deprecated` (the certificate validator exempted only `draft`, so an uncertified metric could not be withdrawn — fixed in `30b6388`, verified to fail against the pre-fix validator); `review → approved` (no `apply_approval_decision` for metrics and no `DEFAULT_POLICY` entry, so `submit` 409'd before the edge was ever reached — fixed in `deb49e7`) |
| `06` §4.2's `custom_metric` approval-policy entry | Added in this slice's Step 0, resolving the spec-vs-code divergence `deb49e7` created — `certified → review` 409'd in every workspace without it. Dated note follows `peril_structure`'s precedent |
| A pre-existing bug, fixed out of scope, in its own commit | `custom_objectives.py` declared `params: dict[str, float]`, coercing money to float, and `TemplateParameter.check` **raises** for a non-int money value — so `capped_gamma` and `spliced_severity` could not be created through their own endpoint at all. Fixed in `040e6e8`. **Pre-existing, not part of FR-MODEL-45** |

**Two runtime defects found by running a fit, not by reading (`35ba563`).** XGBoost's
eval-log parser (`xgb.callback.EarlyStopping.after_iteration`) re-parses a formatted string
by splitting each `"name:value"` entry on a single `:`. A Custom Metric ref is
`custom_metric:<slug>@<version>` — already `kind:slug@version` — so declaring one raised
`too many values to unpack` the moment the name reached XGBoost's own log line; fixed by
`_xgb_safe_metric_name`, sanitising only the string handed to XGBoost and translating it
back in `_curve`. Separately, XGBoost was found to leak its own implicit default (`rmse`,
picked for a callable objective it cannot introspect) into the curve when only custom
`eval_metrics` were declared and `eval_metric` was therefore never set; fixed by setting
`disable_default_eval_metric` in that case. LightGBM needed neither fix.

**A backend asymmetry, found and fixed (`d8859a2`).** LightGBM's `_fit_lightgbm` reported
only the stopping target when several custom metrics were declared — `first_metric_only`
decides which metric drives early stopping, not which metrics get reported, and the
`stopping_on_custom` branch had narrowed `feval` to the stopping target alone, silently
dropping every other declared custom metric from the curve. XGBoost was unaffected. Fixed
by ordering the stopping target first in `feval`'s return rather than narrowing it, verified
against LightGBM's own `_EarlyStoppingCallback._init` — `first_metric` is
`evaluation_result_list[0].metric_name`, and that list's ordering is builtin `params["metric"]`
entries followed by `feval`'s in return order — so the fix is read against the mechanism it
depends on, not asserted.

**A milestone.** MODEL is now the first module in this repository with **every declared
endpoint published** — 40 of 40, up from 34 of 35 before this slice. Task 1 declared five
more endpoint rows in `02` §5.1 and Task 5 published all six of the Custom Metric routes,
closing the axis.

**Three failures, invisible to every per-task scoped test run, found only by the full gate.**
Each of the seven tasks in this slice ran green against its own test files. Only
`uv run pytest -q` across the whole suite surfaced these — the evidence for `CLAUDE.md`
§11's insistence on running both halves of the gate rather than trusting accumulated
per-task greens:

1. **`backend/tests/test_contracts.py::test_job_status_and_kind_enums_agree_with_the_contract`.**
   `JobKind` gained `metric.certify` in `49bc16d`, regenerating the *generated* schema, but
   the hand-authored `docs/contracts/schemas/job.schema.json` — `CLAUDE.md` §2's "partly
   generated, partly hand-written" seam — was never updated. Fixed by adding `metric.certify`
   to the authored file in the same position the generated one carries it.
2. **`tests/test_repository_invariants.py::test_every_error_code_pricing_core_raises_is_registered_and_declared`.**
   `METRIC_REF_UNRESOLVED`, `METRIC_NOT_APPLICABLE` and `METRIC_NOT_FITTABLE` were registered
   in `errors.py` and named in a prose "Amended 2026-08-19" note in `02` §5.1, but never added
   to the backtick-delimited catalogue list the test actually parses — every prior addition
   (e.g. `MODEL_APPROXIMATION_INVALID`) added the code to that list *and* a note; `49bc16d`
   wrote only the note. The dispatch that caused it said "nothing cross-checks those two
   lists (OQ-OVR-9)" — too broad: this repository checks the subset `pricing-core` raises
   against both `errors.py` and the spec catalogue, and that check is what caught this.
   Fixed by adding the three codes to the list; the existing note stands, now complete rather
   than replaced.
3. **`backend/tests/test_demo_guide.py::test_the_guide_names_the_endpoints_a_spec_declares_and_the_contract_lacks`.**
   Hardcoded `{"MODEL", "RATE"} <= modules` (modules with a declared-but-unpublished
   endpoint). MODEL correctly dropped out of that set once this slice closed its endpoint
   axis to 40 of 40 — the code was right, the test's assumption was stale. Narrowed to
   `{"RATE"}`, with a docstring sentence added: the set is *expected* to shrink as modules
   complete, so a future failure here most likely means a module finished, not that
   something broke.

All three were confirmed as genuine (not full-suite-only ordering or environment artefacts)
by re-running each failing test in isolation with the DSN exported — each reproduced
identically alone. After the three fixes, the full suite is green.

**Enforcement proven against broken input (`CLAUDE.md` §13.4).** The `draft → deprecated`
fix (`30b6388`) shipped with a positive test verified to fail against the pre-fix validator.
The `review → approved` fix (`deb49e7`) shipped with the full `certified → review → approved`
lifecycle test and a negative case mirroring `custom_objectives`' own — a decision about
another artifact type leaves the metric untouched. `test_repository_invariants.py`'s
error-code check is itself the proof for finding 2 above: it went red against `49bc16d`'s
incomplete catalogue entry, which is exactly the broken input it exists to catch.

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (129 source files) ·
`lint-imports` 0 (3 contracts kept) · **1412 python tests, zero skipped**, in 273 s ·
audit-docs 0 — **489 requirements** across 8 specs, **72 open questions** all mirrored,
**131 error codes** ownership-exclusive (was 128) · req-coverage **235 of 489 marked,
48.1 %** · `generate-contracts.py --check` 0, **23 generated contracts match** · frontend:
`pnpm install --frozen-lockfile`, `generate:api`, `lint`, `type-check`, **131 tests passed**,
`build` — all green, confirming the two new generated contracts (`custom-metric`,
`metric-certificate`) round-trip cleanly through the TypeScript client · `scope-audit.py
MODEL --endpoints`: **40 declared, 40 published (100%)**.

**Not delivered, with owners.** No frontend view renders a Custom Metric — `02` §5.3's
model spec builder is **W6b**'s, unchanged by this slice. `expression`-kind metrics remain
Phase 2 behind `expression_objectives_enabled`, per FR-MODEL-45's own template-only scope
for Phase 1. The four other buildable slices this workstream's outstanding-work table named
on 2026-08-19 (regularisation/CV, Tweedie power, offset-from-model, EBM) are untouched by
this slice.

**`custom_metric` has no evidence floor — deferred, then dropped from this record until the
whole-branch review found it (2026-08-20).** `06` §3.3 has no evidence row for
`custom_metric`, so `model_schema.approvals.EVIDENCE_FLOOR` has no entry for it and
`ApprovalPolicy.below_floor()` returns nothing: a workspace that edits `metric_certificate`
out of its own `06` §4.2 entry is accepted, and `metrics._require_evidence` then has nothing
to require. `custom_objective` **is** in the floor and is protected; the parallel this slice
claimed everywhere else does not hold here. What protects a metric today is the lifecycle,
not the policy — submission requires `certified`, only `record_certificate` sets it, it sets
it beside a `certificate_id`, and the `certified_metric_has_a_certificate` CHECK refuses the
pair coming apart. The gap is that the *policy reader* is told a floor exists where none
does. ~~**Owner: W5**, as a `06` §3.3 spec change plus the matching `EVIDENCE_FLOOR` entry,
in that order — adding the entry alone would put the code above its own specification. Not
folded into the fix wave that found it, because a new §3.3 evidence row is a governance
change rather than a defect fix.~~ **Closed 2026-08-22 by the audit-remediation slice, in
exactly that order.** `06` §3.3 gained the Custom Metric row — "Metric Certificate with
`overall ≠ failed`" (`02` FR-MODEL-45/105/108) — with a dated note recording that **§3.3 was
the side that was wrong**: the evidence was decided on 2026-08-20 when §4.2's
`DEFAULT_POLICY` gained the entry, and the floor that entry sits on was never written down.
Then `EVIDENCE_FLOOR` gained `"custom_metric": ("metric_certificate",)`, and FR-GOV-37 was
amended for the floor it now carries. Proved by `test_the_metric_floor_is_exactly_what_is_checkable`
— the entry is a *complete* projection of the §3.3 row, leaving none of the uncheckable
remainder `model_comparison_if_predecessor` is — and by the negative case this entry
described but nothing tested: an edited policy dropping `metric_certificate` now reports
`below_floor() == {"custom_metric": ("metric_certificate",)}` instead of nothing, and
`set_policy` refuses it. **The same pass found a second false premise and corrected it
rather than leaving it standing**: FR-GOV-37's `peril_structure` sentence rested on "an
artifact type with no §3.3 row", and §3.3 has carried a Peril Structure row since
2026-08-14 — four days *before* FR-GOV-37 was written. The empty floor survives on a reason
the original did not give, with **owner W17**. `metrics._require_evidence`'s docstring
asserted the protection existed until 2026-08-20, named the gap from then until 2026-08-22,
and now records the closure with both earlier states kept.

**LightGBM silently drops a declared builtin `eval_metric` when early stopping targets a
Custom Metric — raised as `OQ-MODEL-21`, not resolved.** Found in the same final review,
immediately before merge. Tested and named in FR-MODEL-107's 2026-08-20 amendment, but
whether a documented drop satisfies FR-MODEL-106's "honoured" is undecided. **Owner: W5**,
alongside the `06` §3.3 / `EVIDENCE_FLOOR` gap above. *(Decided 2026-08-21: the drop is
recorded on the fit — FR-MODEL-111; owner W5 stands.)*

#### W5 slice — regularisation and cross-validation, 2026-08-21

The twenty-third slice, 2026-08-21 (PR #124). FR-MODEL-20 and FR-MODEL-53 were two of the
three requirements the 2026-08-19 outstanding-work pass found with **no verdict anywhere** —
unevidenced and unspoken for in every slice record, the one option `CLAUDE.md` §13 rule 1
does not allow. They were paired before they were built, by a verdict on file rather than by
convenience: `select_by: cv` lives inside the penalty path, so cross-validation without
regularisation would have had nothing to select over. **The schema was ahead of the code** —
`GlmSpec` had carried `alpha` and `l1_ratio` since Phase 0 and `cv_folds` was declared and
read by nothing — which is the state FR-MODEL-87's staged contract exists to make visible
rather than to permit indefinitely.

| Delivered | Evidence |
|---|---|
| The documented penalty path (FR-MODEL-20) | `GlmSpec.select_by` (`fixed` default, or `cv`) and `GlmSpec.cv`; `_fit_cv_path` scans the elastic-net path into `glum` with `l1_ratio` held fixed across every point |
| Declared fold construction, not an implicit split (FR-MODEL-53) | `pricing_core.data.splits.assign_folds` generalises `01` FR-DATA-33's two-part cutoff to K folds: `random` reuses the same seeded draw, `temporal` cuts the sorted order into contiguous equal-count blocks, `grouped_by_key` keeps a key's groups whole across folds |
| One seed, not two | Fold assignment is reproducible from `ModelSpecCommon.seed` — the seed the spec already versions into `spec_hash`. `GlmCvSpec` carries none of its own, deliberately: a second field is a second thing that can disagree with the first |
| Per-fold metrics **and their dispersion**, not the mean alone | `Diagnostics.cross_validation` persists the whole scanned path and the selected alpha's per-fold spread. A CV mean with no dispersion beside it says a model was selected and not how close the race was |
| The empty fold is refused by name | `GLM_CV_FOLD_EMPTY`, registered and declared in `02` §5.1 in the same commit — the skew a fold count chosen against the whole book does not guarantee against, per fold. A fold cannot be scored, or trained, on nothing |
| `spec_hash` moved with the fields | `SPEC_HASH_VERSION` 5 → 6 (FR-MODEL-86); every `v5:` digest is stale and findable |
| Evidenced, not asserted | **39 new tests** — FR-MODEL-53 ×27, FR-MODEL-20 ×11, FR-MODEL-49 ×1, FR-MODEL-99 ×1, across three new test files, plus a CV-selected model fitted **through the real Job** recording its fold dispersion |
| Contracts regenerated | `openapi/generated.json` and three schemas (FR-PLAT-48) |

**Two spec interactions the code found, both resolved by dated amendment in `02` rather
than decided in the code and left unwritten** (§0). **K-fold `temporal` was undefined** —
neither FR-MODEL-53 nor `01` FR-DATA-33 said what it means, FR-DATA-33 defining only a
two-part cutoff; resolved as contiguous time-ordered blocks. **FR-MODEL-99's
`uncertainty_basis` predates `select_by == "cv"`**: under CV selection `GlmSpec.alpha` is
pinned to `0.0` and the effective penalty comes from `cv.alphas`, so the basis cannot be
read off the spec's alpha at all; resolved as unconditionally naive/penalised for every
`select_by == "cv"` fit. Conservative rather than exact, for a stated reason — the grid
starts at zero and moves away from it, so a fit landing back on exactly zero is the rare
point and the cautious label costs a display caveat rather than a wrong number.

**FR-MODEL-87's staged contract, eighth entry.** `select_by` and `cv` go live under a
**nested** `cv: GlmCvSpec` block rather than the flat `select_by`/`cv_folds` fields the
2026-08-17 decision named, mirroring `GbmSpec`'s nested `early_stopping`. FR-MODEL-87's row
and §4.4's note were amended to say the shape that was **built**, not the shape that was
predicted, and the fields leave the absent-entirely list by amendment rather than by being
quietly dropped from it.

**Three defects the slice's own final review found, all in validators that looked
complete.** `GlmCvSpec.alphas` let **NaN** through — `nan < 0` is `False` and `nan != nan`
defeats a distinctness check, so a path `glum` could never fit was storable.
`CrossValidationDiagnostics` checked fold coverage with **set equality**, so metrics for
folds `0,0,1,2` under `folds=3` passed and double-counted fold 0 in the dispersion. And
three `SplitError` branches had no negative test; they do now, with a note that Polars'
`arg_sort` puts null `time_column` rows in fold 0 — deliberate and deterministic, written
down so the next reader does not rediscover it as a bug.

**A §5.2 interface comment lagged the field it describes**, and was corrected in the slice:
`fit_glm`'s documented return read `.result, .covariance_bytes` after `GlmFit` gained `cv`,
so a caller copying the signature off the page would have missed the cross-validation
diagnostics the fit carries. The same shape as every §5.1 divergence this workstream has
found — the code moved and the page a caller copies from did not.

**Not delivered, with owners.** **No new HTTP endpoint** — the existing diagnostics route
surfaces `cross_validation`, and a second route for a field on an artifact already served
would have nothing of its own to say. **No frontend**: the CV screen is **W6b**'s.
FR-MODEL-99's exact answer for penalised inference — a bootstrap or penalty-aware sandwich
over ~200 refits, a Job rather than a fit-time step — remains owned by the first consumer
that renders or cites a coefficient interval on a penalised fit; CV selection does not
create one.

**Gate: not reconstructable, and deliberately not invented.** This record was written on
2026-08-22 from the merged commit, and the branch's ruff / mypy / test-count figures were
never written down at merge time. What is verifiable from the merged diff is stated above.
§13 rule 5 asks for a measurement or the reason a measurement is the wrong instrument; a
gate figure recalled four days later is neither.

**Recorded late, and that is the process finding.** PR #124 struck its row in the
outstanding-work table above and wrote no slice record; this one was written 2026-08-22 from
the merged diff. **It is the third such omission in W5** — the prediction slice (PR #102) is
the first, the GLM approximation (PR #120) the second, and the Tweedie slice below is the
fourth, from the same day and the same cause. The cause is now visible enough to name: a
slice whose entry in this file is a row it can *strike* treats the strike as the
bookkeeping and stops, while a slice with no such row writes a record. A row's strike says a
slice happened; only a record says what it found — and this one found three validator
defects and two undefined spec semantics the strike does not mention.

#### W5 slice — Tweedie power by profile likelihood, 2026-08-21

The twenty-fourth slice, 2026-08-21 (PR #125), and the one where the design on file turned
out to be wrong and building it is what proved so. FR-MODEL-22 is the last of the three
requirements the 2026-08-19 pass found with no verdict anywhere. Before this slice `GlmSpec`
only **validated** that a supplied Tweedie power lay between the two families it spans: `p`
was a constant an actuary typed, defaulting to 1.5, with no uncertainty attached and nothing
recording where it came from — `CLAUDE.md` §7's rule about surfacing uncertainty with every
estimate, broken by an estimate never presented as one.

| Delivered | Evidence |
|---|---|
| The grid, opt-in | `GlmSpec.tweedie` carrying `p_grid`; `null` under a fixed-power spec, so existing specs are unchanged. Default is a ten-point scan strictly inside `(1, 2)`; at least two points, strictly increasing. One point would be a fixed fit wearing a scan's clothes |
| A **true** profile likelihood, not a deviance argmin | `estimated_power` is the argmax of the Tweedie log-likelihood over `p_grid` — `μ̂(p)` the GLM refit at each scanned power, `φ̂(p)` the mean-deviance dispersion, and the Tweedie series density of Dunn and Smyth (2005) |
| The density is its own module, with its own tests | `pricing_core.modelling.tweedie_density` — the series density in log space, matching the R `tweedie` package's `dtweedie_series` |
| The estimate carries its own uncertainty | 95 % profile-likelihood interval, linearly interpolated between scanned points, persisted with the profile curve itself |
| It lives on the fit, not on Diagnostics | `TweediePowerFit` rides on `GlmFitResult` because the estimate feeds every downstream deviance recomputation, and all of those receive the fit as their first argument. On Diagnostics it would be a number beside the fit rather than a number the fit is made of |
| Never silently baked in as a constant — the defect the row named | `_power_of`: diagnostics, the type-III sweep and `backtest_model` all read `p` from the fit result instead of the spec's 1.5 default, and the type-III refits hold it fixed at the estimate |
| A maximum at a scan edge is refused, never reported | `GLM_TWEEDIE_POWER_GRID_EDGE`, registered and declared in the same commit. An argmax at either boundary reports the scan's edge as the answer, which is a statement about the grid dressed as a statement about the book |
| Three mutual exclusions refused by name | A non-Tweedie family; a fixed `family_params.power` supplied beside the grid; and estimation together with `select_by == "cv"`, since the profile is penalty-dependent and the two selections would each be conditioning on the other's answer |
| `spec_hash` moved with the field | `SPEC_HASH_VERSION` 6 → 7 (FR-MODEL-86): two specs differing only in `tweedie.p_grid` sharing a digest would hand the second caller the first caller's model under FR-MODEL-66 |
| Evidenced, not asserted | **25 new tests, every one marked FR-MODEL-22**, across three files, plus an estimated-`p` model fitted **through the unchanged fit Job**, its persisted result carrying the estimate, the interval and the curve |

**The design on file was wrong, and the code is what found it — §0 in its literal case.**
The planning-time design, written into this file's outstanding-work row and into the slice's
own opening tasks, was **deviance argmin**: scan `p`, refit, take the power minimising the
deviance. It is not a likelihood profile for Tweedie — the deviance carries a saturated term
and a `p`-dependent normaliser, and neither cancels out of the argmin. **Measured, not
argued**: at the slice's pinned seeds the deviance-argmin estimator came in at roughly
*truth + 0.25* and hit the grid edge at every seed. The estimator was replaced by the true
profile log-likelihood, and `02` §4.4's FR-MODEL-22 amendment records **which side was wrong
and why**, naming the replaced design rather than editing it away. Had the code been quietly
bent to the deviance design instead, the platform would have shipped a biased power estimate
with a confident-looking interval around it.

**A fixture defect the same measurement exposed.** The recovery test's data generator drew
the compound representation with claim shape 1, which is exact **only at p = 1.5** — so the
data was not Tweedie at the other scanned powers and the test was measuring the generator as
much as the estimator. It now draws the shape implied by the stated power, so the data is
Tweedie at every one, with bit-identical draws at the pinned seed. The test asserts the
profile curve is finite, that the argmax **is** the reported estimate, and that the interval
brackets the truth — three properties, where a single point estimate compared to a target
would have passed under the biased estimator too.

**Not delivered, with owners.** **No new HTTP endpoint** — `tweedie` rides on the fit result
the existing model read already serves. **No frontend**: nothing renders the profile curve
or the interval, and those views are **W6b**'s. **Estimation × CV selection is refused, not
built** — recorded on FR-MODEL-87's staged contract as a named refusal rather than a gap,
and owned by whoever first needs a penalised Tweedie fit with an estimated power, which
nothing does today.

**Gate: not reconstructable, and deliberately not invented** — as with the record above.
Verifiable from the merged diff and stated here: 25 tests all marked FR-MODEL-22, three
regenerated contracts, `SPEC_HASH_VERSION` 7, and `GLM_TWEEDIE_POWER_GRID_EDGE` registered
and declared. The one number this slice *did* measure is in the record where it belongs —
the deviance-argmin bias, which is the finding.

**Recorded late, and that is the process finding.** PR #125 struck its row in the
outstanding-work table above and wrote no slice record; this one was written 2026-08-22 from
the merged diff. **It is the fourth such omission in W5** — after PRs #102, #120 and #124,
the last of which merged three hours before this one and failed the same way for the same
reason. **This is the omission that costs the most**, and it is why the pattern is worth
naming rather than re-apologising for: the struck row says "DELIVERED 2026-08-21" and
nothing more, while the thing this slice actually found — that the design on file produced a
measurably biased estimator, and that the fixture built to check it was wrong in the same
direction — existed for four days only inside `02`'s amendment and a squashed commit
message.

#### W5 slice — offset from another model, and a scaffold field that was read by nothing, 2026-08-21

The twenty-fifth slice, spanning 2026-08-21. FR-MODEL-24 gives a GLM spec an
offset from another model — the referenced fitted GLM's linear predictor on the training
data, enabling residual modelling and "fit on top of the current rating structure" — and
the slice exists around a finding with the custom-metrics shape: `OffsetSpec`'s Phase-0
scaffold `model_ref: str` had been declared and read by nothing, while `fit_glm` passed
`kind="model"` silently with no offset at all. A caller could declare an offset from
another model and be told nothing was wrong while none was ever applied. FR-MODEL-24 as
amended 2026-08-21 now requires it honoured — the field live, the ref resolved, the fit
offset.

| Delivered | Evidence |
|---|---|
| `offset_model_ref` on `OffsetSpec`, and the named refusals | `OffsetSpec.offset_model_ref: ModelRef \| None` — the canonical `model:slug@version` string (ID-3), the pattern admitting `model:` refs and nothing else; validators require `kind == "model"` ⟺ ref set; `GbmSpec` refuses `kind="model"` by name (GLM specs only, FR-MODEL-24 as amended); `GlmFitResult.offset_model_ref` records the resolved pinned ref — what was actually constructed is recorded on the fit result (FR-MODEL-71's rule, applied to GLM) |
| `SPEC_HASH_VERSION` 7 → 8 in the same commit | `backend/src/app/platform/modelling.py` — the ref joins the canonicalised spec payload, so FR-MODEL-66's dedup must not match a fit offset against another model's structure to one with no offset (FR-MODEL-86) |
| pricing-core takes the resolved array — required, never silent | `model_offset` threaded through `fit_glm`, `linear_predictor`, `predict_glm`, `predict_glm_interval`, `score_fitted`, `compute_diagnostics` and `backtest_model`; every entry point that reaches a `kind="model"` spec without the array raises `MODEL_OFFSET_MISSING`, with length and finiteness validated — pricing-core never resolves the ref (ADR-0001), so the backend supplies η and pricing-core refuses to fit without it |
| The type-III reduced fit keeps the offset | The drop-one-term refits inside `_type_iii` pass the same `train` array; before the fix the pre-existing `except GlmFitError: continue` swallowed `MODEL_OFFSET_MISSING` and a model-offset fit with ≥ 2 factors got a **silently empty** type-III table — `test_type_iii_reduced_fits_keep_the_offset` pins presence for both terms and the insignificance of the factor whose effect lives inside the offset |
| The backend resolves the ref | `OffsetModelSource` + `resolve_offset_model` in `platform/modelling.py` (modelled on `_quantile_crossing` and `_refuse_mismatched_approximation`): the pinned row's spec, fit result, factors, bandings and groupings; refusals by name — not a model, not fitted, not a GLM, or link-mismatched (`MODEL_OFFSET_REF_INVALID`), missing row (`NOT_FOUND`) |
| Fit, prediction and backtest wired | `_fit` and `_backtest` in `model_handlers.py` resolve in `load()`, compute η on the worker thread and pass it to `fit_glm`/`compute_diagnostics`/`backtest_model`; `_score_glm` resolves per request and honours the offset in both `predict_glm` and `predict_glm_interval` |
| Spec validation resolves the ref before a Job is queued | `SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE`, raised by `validate_spec` for a ref that names nothing, an unfitted model, a non-GLM or a link mismatch (wf-01 D2's rule applied to offsets-from-model) |
| The code registered and catalogued in one commit | `MODEL_OFFSET_REF_INVALID` added to `errors.py`'s `MODELLING_ERROR_CODES` and `02` §5.1's backtick catalogue in the same commit as its first raise, with the dated blockquote note; `MODEL_OFFSET_MISSING`'s note gained a dated addendum for its fit-side uses |
| The spec amendment and the question it raised | FR-MODEL-24 amended 2026-08-21 (the ref is `model:slug@version`, GLM-to-GLM v1, what is refused by name); §4.4's `offset_model_ref` block declared; OQ-MODEL-22 recorded in `open-questions.md` and mirrored in `02` §10; this closure moves the field live on FR-MODEL-87's staged contract as the ninth live entry |

**The §0 divergence, resolved.** The code scaffold's `model_ref` was the outlier — the
spec's FR-MODEL-24 text and the hand-authored `docs/contracts/schemas/model-spec.schema.json`
have always named and typed the field `offset_model_ref` as an artifact-ref string, and the
scaffold field was read by nothing. Spec and contract agreed, and the code followed them: a
rename with the artifact-ref pattern, not a new field. And today's behaviour was a defect,
not an absence: `fit_glm` passed `kind="model"` silently with `offset = None`, fitting as
though no offset were declared — the silent-ignore defect is replaced by the implemented
path plus named refusals, `MODEL_OFFSET_MISSING` at every unwired pricing-core entry point,
`MODEL_OFFSET_REF_INVALID` at resolution, `MODEL_OFFSET_UNRESOLVABLE` at validation, and
GBM's accidental column-refusal replaced by the schema's deliberate one.

**Delivered on `worktree-offset-model` in nine commits** — `e3f6610` (the FR-MODEL-24
amendment and OQ-MODEL-22), `c37c717` (the schema field, refusals and `SPEC_HASH_VERSION`
8), `ab17018`, `af8f5c8` and `e781d8b` (pricing-core fit, scoring, diagnostics, backtest
and the type-III fix), `cd805e2` (the fit job), `6f9c740` (prediction), `c136440`
(backtest), `5b6ef87` (spec validation) — each tagged FR-MODEL-24.

**Not delivered, with owners.** GBM/EBM referenced models and `GbmSpec`-declared offsets
stay refused by name — OQ-MODEL-22 records the widening options, recommendation (a) then
(c) *(decided 2026-08-21: (a) then (c) — FR-MODEL-112)*; the peril-reconciliation scoring
path is declared-and-refused (`MODEL_OFFSET_MISSING`)
until W5 wires the resolver there; EBM as a model type is FR-MODEL-37's separate slice;
FR-MODEL-23's fit-error surfacing is delivered: markers at `test_glm.py:134,:429` and `test_spec_hash.py:99,:114`, `GLM_SEPARATION_DETECTED` registered and declared — the 'remains unbuilt' lines were stale. The remainder — a bare non-`LinAlgError` `ValueError` from glum still reaches the job unwrapped — is recorded 2026-08-21 as unbuilt, owner W5; `02` §5.3's model spec builder
is **W6b**'s, unchanged by this slice.

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (130 source files) ·
`lint-imports` 0 (3 contracts kept) · **1547 python tests** · audit-docs 0 —
**489 requirements** across 8 specs, **74 open questions** all mirrored, **134 error
codes** ownership-exclusive (was 133) · req-coverage **239 of 489 marked, 48.9 %** ·
`generate-contracts.py --check` 0, **23 generated contracts match** · frontend:
`install --frozen-lockfile` 0, `generate:api` 0, lint 0, type-check 0,
**131 vitest tests**, build 0.

#### W5 slice — EBM models via interpret-core, 2026-08-21

The twenty-sixth slice, spanning 2026-08-21 → 08-22. FR-MODEL-37 gives the platform its
fourth Model type: `ebm`, fitted by `interpret-core==0.7.8` and transparent by
construction — the term shape functions ARE the model, so they are exported verbatim as
additive lookup tables (ADR-0003: fit results are data, never pickles), and the
transparency artifact is built from that export with no approximation, no surrogate and
no booster blob. One requirement, one model type, pin exact: the `interpret` metapackage
would pull notebooks and visualisation extras, so only `interpret-core` is installed
(~115 MB incremental; the workspace's sklearn 1.9.0 satisfies its requirement).

| Delivered | Evidence |
|---|---|
| `EbmSpec`/`EbmFitResult`, and the verbatim export | `EbmSpec` (`objective` `rmse`/`mae`, `interactions` 0–1, `max_bins` a power of two in [16, 32768], `max_rounds` 50000, `monotone_constraints` map); `fit_ebm` exports interpret's additive lookups verbatim — term scores and bin weights in the library's own slot layout (numeric `len(cuts)+3`, categorical `len(levels)+2`, the 1-based level dict), `feature_order` and the index rule scoring uses; `fit_ebm` honours `spec.weight.kind == "column"` via `sample_weight` and draws `random_state=spec.seed` |
| The transparency artifact from the export, no approximation | `build_ebm_shape_functions` serialises the fit's own tables verbatim into `terms_blob`; `fidelity_statement` exact-by-construction prose; `monotonicity_verified` read from the exported tables in the declared directions; no surrogate reserved — FR-MODEL-33/36/84 |
| Universal diagnostics through the shared partition | `compute_ebm_diagnostics` reuses `_partition` with `family="gaussian"` (FR-MODEL-50's "all model types" taken literally); complexity is the total real bins across terms; no eval curve or importances — an EBM's dependence structure IS the exported tables, and duplicating it as a diagnostic would be a second statement of one fact (FR-MODEL-49/50/54/55/81) |
| Scoring from the tables alone | `predict_ebm` scores `intercept + Σ term scores` from the exported lookups — no estimator and no fitting-stack import, and `test_scoring_without_the_fitting_stack.py` gains `interpret` to its blocked set (FR-MODEL-37, ADR-0003, NFR-PLAT-11) |
| `spec_hash` v9 | `SPEC_HASH_VERSION` moves `8 → 9` in the same commit as the EBM fields joining the payload (FR-MODEL-86); the stale-digest LIKE clause names the stale version (`v8`), corrected from the plan's incoherent `'v9:%'` — every historical entry names the version it finds |
| Four plan-defect corrections, each with a dated note (2026-08-21) | The plan's interpret-internals facts were spike-unverified; the backstop caught each as prescribed, never a weakened test: (1) `feature_types` is `"nominal"`, not `"categorical"` — the banding `levels` are passed verbatim; (2) `monotone_constraints` is a positional int list, not the plan's `f"feature {i}"` keyed-dict convention (the plan's own Self-Review flagged it unverified); (3) `best_iteration_` is a 2-D `[stage, bag]` array — read via `np.ravel(...)[0]`; (4) the plan's own test direction was backwards (`<= 1e-9` asserted non-increasing for a +1 constraint) → `>= -1e-9`, tolerance untouched |
| The spec note the code disproved, amended in the same commit | The §5.1 blockquote claimed `interpret` raises a bare `ValueError` on a nominal constraint; pinned 0.7.8 silently zeroes the term — the pre-check is the whole refusal and the message says the true mechanism (amended 2026-08-21, the fit task; CLAUDE.md §0) |
| A second error code the plan never foresaw | `EBM_MONOTONE_CONSTRAINT_UNKNOWN`: a transparency-time refusal — a constraint naming a feature the fitted tables do not contain cannot be checked, and reporting `True`/`False` would fabricate a verdict. Registered in `MODELLING_ERROR_CODES` and declared in §5.1's catalogue with a dated blockquote (2026-08-22) in the same commit; the plan's "only one new code" premise is superseded by the design its own transparency task chose |
| Backend boundary refusals — the plan's new task 2b | Widening the `ModelSpec`/`FitResult` union broke the whole-repo mypy gate at three backend sites the plan's Task 2 verification form could not see (it never runs whole-repo mypy). Two became named refusals that double as the mypy narrowing: `prediction.py` refuses an EBM predict request with `MODEL_TYPE_UNSUPPORTED` (dated note, the real arm was attributed to W6b here and is **W32-4's**; built 2026-08-23 (W32-4, the EBM predict arm), which narrows this refusal to a spec/fit-result mismatch rather than deleting it), and `_resolve_candidate` refuses an EBM row with `MODELS_NOT_COMPARABLE` — wf-01 E1 is GLM-vs-GBM surrogate validation, and an EBM has no surrogate. The third site was fixed by Task 11's planned dispatch restructure |
| The early `EbmSpec`/`EbmFitResult` exports | The model-schema package-root exports landed ahead of Task 5 — `EbmSpec` with Task 2b and `EbmFitResult` with Task 3, one alphabetical import line each, because the boundary refusals' imports needed them; Task 5 completed the remaining names |
| Objectives refused by name, not extended | EBM's vocabulary is `rmse`/`mae` only (identity link); §7's families and binomial `log_loss` are **declared-and-refused by name** as `objective` values under FR-MODEL-87, with the dated note in §4.4; `interactions=2` (triples) is **declared-and-unbuilt** (a triple grid at even 64 bins is 262k cells — the JSONB envelope cannot bound cubic growth); custom objectives do not apply to EBM — `ObjectiveBackend` has no EBM member by design |
| The one authored-vs-generated divergence, hand-aligned | The comparison test compares type names and enum values only — constraint-level drift (`minLength`/`required`/`additionalProperties`) has **no mechanical guard** (Task 13's open item, owner W5). The slice found and hand-aligned exactly one divergence: `transparency-artifact.schema.json`'s hand-authored `ebm_shape_functions` block declared `terms_blob` with no `minLength` against the type's `min_length=1` — amended to `minLength: 1` with a dated note (a hand edit to a hand-authored file; regeneration never touches it) |
| Spec-hash counter coherence (Task 1's deferred minor) | §4.4's blockquotes show `spec_hash` moving `v4 → v5` (the approximation) beside `8 → 9` (the EBM fields); the vN lineage between v5 and v8 — v6 with regularisation/CV (FR-MODEL-20/53) and v7 with Tweedie power (FR-MODEL-22) — went unrecorded in the spec. Recorded here as a coherence follow-up, owner W5 |

**Recorded, not built, with owners.** `fit_gbm` ignores `spec.weight` — verified, no
reference in `gbm.py`; dated note 2026-08-21, owner W5. *(Corrected 2026-08-22: the note
was never written. `git log -S "dated note 2026-08-21"` shows the phrase entering the
repository only in `c2c54a6`, and only in this file — so FR-MODEL-87's obligation was
recorded as discharged while nothing in `02-modelling.md` said the field was unbuilt. The
gap is closed by building it rather than by writing the note; FR-MODEL-19 carries the
amendment.)* **FR-MODEL-111** (a declared eval
metric a backend could not evaluate is recorded on the fit) — the verdict is recorded here:
owned by W5, due before W5 closes; explicitly NOT this (EBM) slice. *(Delivered 2026-08-22
by the slice below, as this record scheduled it.)* **NFR-MODEL-7**
recorded as-is — the export/import round-trip NFR remains unevidenced for the suite; this
slice's EBM round-trip tests are evidence for the EBM artifact only, and the record says
exactly that rather than claiming closure. The `06` §3.3 custom-metric evidence-row gap and
OQ-GOV-7 remain as they were — unchanged by this slice. No frontend view renders an EBM
(W6b owns any that will); no alembic revision — `ModelRow.spec`/`fit_result` and
`TransparencyArtifactRow.payload` are JSONB columns, unchanged; the slice is API-only.

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (131 source files) ·
`lint-imports` 0 (3 contracts kept) · **1609 python tests** · audit-docs 0 —
**494 requirements** across 8 specs, **74 open questions** all mirrored, **136 error
codes** ownership-exclusive (was 134) · req-coverage **241 of 494 marked, 48.8 %** —
FR-MODEL-109 joins the marked set with the marker backfill that closes this record ·
`generate-contracts.py --check` 0, **23 generated contracts match** · frontend untouched
(W6b owns any view that renders an EBM — the slice is API-only).

#### W5 slice — GBM declared weights and the dropped eval metric record, 2026-08-22

The twenty-seventh slice, 2026-08-22. Two defects sharing one shape — FR-MODEL-106's own
words for the class: *a spec accepted, silently ignored, and reported to the caller as
configured*. `spec.weight` was declared on `ModelSpecCommon`, honoured by `fit_glm`,
`fit_ebm` and `compute_diagnostics`, and read by neither GBM backend; and a builtin eval
metric suppressed so it could not hijack a custom stopping target was dropped with nothing
on the artifact to say so. Both are closed in the fit path; no backend handler changed.

| Delivered | Evidence |
|---|---|
| `spec.weight` reaches both GBM backends | `_weights(data, weight)` mirrors `_offset`; `fit_gbm` resolves it once for the training frame and once for the holdout, and the `valid` tuple widens to carry it — a curve whose train half is weighted and whose holdout half is not would plot two quantities on one axis. `xgb.DMatrix(weight=)` via the `matrix()` closure, `lgb.Dataset(weight=)` on both sets. A missing column raises Polars' own `ColumnNotFoundError`, exactly as `fit_glm` has always done — no new error code, because one malformed spec must not be answered differently by model type (FR-MODEL-19/55) |
| The actuarial measurement that names the defect | `test_a_gamma_severity_fit_weighted_by_claim_count_predicts_the_weighted_mean` — a closed-form severity book whose unweighted mean is **5.0** and whose claim-count-weighted mean is **1.8**. Both backends fitted **5.0000** before and predict **1.8004** after. `test_non_uniform_weights_change_the_fit` pins that a non-uniform column moves the booster at all; `test_a_weight_column_of_ones_fits_identically_to_no_weight` is the control proving the plumbing is inert when the spec asks for nothing |
| The custom objective and custom metric receive the declared weights | `make_xgb_objective`/`make_lgb_objective` and both `_custom_feval` helpers already read `get_weight()` and fell back to `np.ones_like(y)`; nothing had ever set it, so **every custom objective and custom eval metric fitted before this date was uniform-weighted**. `test_a_custom_objective_receives_the_declared_weights` and `test_a_custom_eval_metric_receives_the_declared_weights` record the array the backend hands in and compare it to the column. `make_lgb_objective`'s docstring asserted "nothing is dropped", false from the day it was written; corrected with a dated note (FR-MODEL-19/42/103) |
| `GbmFitResult.dropped_eval_metrics` (FR-MODEL-111) | `DroppedEvalMetric` — `name` as `eval_metrics` spelled it, `reason` a closed set whose one member is `builtin_evaluated_before_custom_stopping_metric`. `_fit_lightgbm` populates it from the same `_builtin_eval_metric_names` list the non-stopping arm passes to `params["metric"]`; `_fit_xgboost` returns empty because it evaluates both lists. Negative tests first: a free-text reason and a twice-named metric are both refused. `test_lightgbm_records_the_builtin_eval_metric_it_dropped` pins the record, `test_a_fit_that_evaluated_everything_drops_nothing` the control, and the pre-existing `test_lightgbm_drops_a_builtin_eval_metric_rather_than_stop_on_it` is byte-unchanged — the drop behaviour did not move, only its visibility |
| `spec_hash` `v9` to `v10`, and the lineage it completes | **The first bump for an interpretation change rather than a payload one.** `weight` was always in the digest; what changed is that `fit_gbm` began honouring it, so a `v9:` digest over a weighted GBM spec names a fit this build produces differently and FR-MODEL-66's dedup would hand the next caller the unweighted one. Every `v9:` digest is stale and findable with `LIKE 'v9:%'` — including an unweighted GLM's, which the change cannot have affected; that over-invalidation is accepted because a targeted one has no mechanism here. `02` §4.4's lineage also catches up on `v5 → v6`, `v6 → v7` and `v7 → v8`, which it had skipped while the backend comment block carried them (FR-MODEL-86) |
| No new shape hand-written, no handler edit | `model_handlers.py` reads `fit.result` by attribute and `record_fit` persists the whole result, so the field rides along — 22 backend gbm/handler tests pass untouched. Contracts regenerated: `DroppedEvalMetric` with a single-member `const` reason, `dropped_eval_metrics` defaulting to `[]` so every artifact written before this date still validates (FR-PLAT-48) |

**Recorded, not built, with owners.** The **eleven unevidenced `NFR-MODEL` requirements**
(NFR-MODEL-1/2/3/4/5/7/8/9/10/11/12 — performance budgets, the export/import round-trip,
and determinism at suite scale) are unowned by this slice and remain the largest single
block of MODEL scope without evidence; NFR is 1 of 12 evidenced. **FR-MODEL-23's
remainder** — a bare non-`LinAlgError` `ValueError` from glum still reaches the job
unwrapped — owner W5, unchanged. The **`06` §3.3 custom-metric `EVIDENCE_FLOOR` gap** is
a spec change first and then code, in that order, owner W5. **FR-GOV-36** unchanged.
**FR-MODEL-112(c)** stays sequenced behind (a), per the 2026-08-21 decision. The EBM
**`interactions=2` triples** remain declared-and-unbuilt and ~~**no workstream has ever been
named for them** — itself an FR-MODEL-87 defect rather than merely a deferral, and stated
here as one.~~ **Owner named 2026-08-22 (audit-remediation slice): Phase 1b.** This entry was
right that an unowned residual is a defect and not a deferral, and it is the one item on the
2026-08-22 list that named the problem without applying the same judgment to the four
sibling owners phrased as events nothing schedules — all five now carry a phase or a
workstream. The **constraint-level contract-drift guard** (`minLength`/`required`/
`additionalProperties`) ~~still has no mechanical guard, owner W5.~~ **Partly built
2026-08-22.** The audit-remediation slice made the existence test resolve `allOf` and
`if`/`then`, made the type test compare **nullability** across the six MODEL-owned slugs,
taught `_scalar_types` to read `const`, and added a nested-path test — after finding that
the existing checks compared **top-level names only**, which is precisely how
`gbm.quantile_crossing` (FR-MODEL-78) and `gbm.tree_count` sat absent from the published
contract for months with every test green. Three defects in the checking machinery itself
were fixed on the way, including a `properties.update()` that **deleted** a conditional
branch's real field definitions. What remains uncovered is `minLength`/`additionalProperties`
and `required`-set drift, and **arm-level attribution** — the flattened union cannot tell
which `if`/`then` arm declares a field, so a GLM-only field declared on the GBM arm still
passes. **Owner for the remainder: W6b**, the first workstream to consume these contracts
from the frontend and therefore the first to be hurt by drift in them. **New finding, recorded
rather than fixed:** `02` §4.8 carries `fit_result` examples for GLM and EBM and **has
never carried one for a GBM**, so there was no example for `dropped_eval_metrics` to join;
FR-MODEL-111's amendment points readers at the generated contract instead. Writing one is
a spec change larger than this slice and is owned by W5. No frontend view renders either
field; no alembic revision — `ModelRow.fit_result` is JSONB and unchanged. *(Fixed 2026-08-22 by the audit-remediation slice: §4.8 now carries a GBM `fit_result` example, validated against `GbmFitResult` rather than hand-written, and naming every field the type declares.)*

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (131 source files) ·
`lint-imports` 0 (3 contracts kept) · **1625 python tests** (was 1609) · audit-docs 0 —
**494 requirements** across 8 specs, **74 open questions** all mirrored, **136 error
codes** ownership-exclusive and unchanged, this slice adding none by design ·
req-coverage **242 of 494 marked, 49.0 %** — FR-MODEL-111 joins the marked set ·
`generate-contracts.py --check` 0, **23 generated contracts match** · frontend:
`install --frozen-lockfile` 0, `generate:api` 0, lint 0, type-check 0,
**131 vitest tests**, build 0. MODEL scope-audit: **108 of 124 evidenced (87 %)**, up from
107 — the five unevidenced `FR`-MODEL requirements that remain are all gated
(FR-MODEL-6, 40, 82, 110, 112).

**Delivered on `worktree-ebm-slice` in fifteen commits** — `1bae625` (the `02`
amendment declaring the EBM arm and its fit/transparency shapes), `328f102` (`EbmSpec`
with the refused-by-name vocabulary), `0a0e83b` (the predict and comparison boundary
refusals), `cc75829` (`EbmFitResult` with the additive tables), `46a2a1e` (the
transparency artifact's EBM block), `bd80fdf` (the package-root exports), `157468e`
(`fit_ebm` via interpret-core, tables exported verbatim), `7acde30` (the shape-functions
blob and `EBM_MONOTONE_CONSTRAINT_UNKNOWN`), `1771254` (scoring from the tables alone),
`e9307c2` (universal diagnostics through the shared partition), `a94b4eb`
(`SPEC_HASH_VERSION` 9 with the EBM fields), `39e19f0` (the backend fit dispatch with
the named constraint refusal), `c2482c5` (the backend transparency artifact through
`model.transparency`), `e45d564` (contracts regenerated with the EBM arm) — each tagged
FR-MODEL-37; this record and the FR-MODEL-109 marker backfill close the slice.


#### W5 slice — the audit-remediation slice, 2026-08-22

The twenty-eighth slice, and the one that answers a closure audit rather than building a
capability. Six slices, four of them clearing defects the audit found and two clearing the
record itself. **It is not a closure record** — `CLAUDE.md` §13's verdicts are below, but W5
closes only when the maintainer accepts them and OQ-MODEL-24 is decided. **OQ-MODEL-24 was decided 2026-08-22** — option (a), denominator settled as fit wall-clock — so that half of the condition is discharged; the maintainer's acceptance of the verdicts below is the half that remains.

**The audit's own numbers moved while it was being answered, twice**, which is the first
finding: the requirement count was re-derived at 124 by the verification pass and was **125**
by the time the correction was applied, because this slice had appended FR-MODEL-113 an hour
earlier. Every number below is re-derived at the moment of writing and carries the command
that produced it.

##### What was built

| Delivered | Evidence |
|---|---|
| `models.diagnostics_id` joins the immutability trigger (`02` R2, `00` FR-OVR-1) | Migration `9e4c7b21fa08`. `record_fit` writes the fit result, the pointer and the status in **one `UPDATE`**, checked in the handler rather than assumed, so the guard freezes from the statement that sets it. Proven three ways: the negative test fails at the pre-fix revision; a deliberately *naive* unconditional guard is caught by the positive control; `downgrade -1` restores the exact prior function body |
| Submission resolves the artifact it pins (FR-GOV-36) | The suite's **first five FR-GOV-36 markers**. Fan-out in the route, mirroring `_carry_to_the_artifact` — DEP-1 satisfied with no registry, because a registry would be a second mechanism for a seam that already had one. Six of twenty types resolve; **an unresolvable type fails closed** with the new `06`-owned `ARTIFACT_TYPE_NOT_RESOLVABLE`, on `07`'s `JOB_HANDLER_NOT_REGISTERED` reasoning. Enforcement proven: removing the resolver gives 8 failures |
| `custom_metric`'s evidence floor (`06` §3.3, FR-GOV-19) | The §3.3 row **first**, then `EVIDENCE_FLOOR` — the order the code's own docstring demanded, since the entry alone would put the code above its specification. Three negative tests, each proven to fail without the entry |
| `GLM_FIT_FAILED` (FR-MODEL-23's remainder) | glum's `ValueError` refusals were escaping raw. Measured against glum 3.4.1 rather than assumed — a response outside the family's domain, a negative or all-zero weight vector, an all-zero response, non-finite input. **Not folded into `GLM_RANK_DEFICIENT`**, whose message names collinear terms — a lie for a non-positive response |
| A handler's `PlatformError` keeps its code (OQ-PLAT-7, decided (a)) | Marked **FR-PLAT-11**: this is platform job machinery, not modelling. The `RuntimeError` control **passed before the change too**, which is what makes it a control rather than a second copy of the same assertion |
| Bühlmann–Straub (FR-MODEL-80) | Built, per OQ-MODEL-5's 2026-08-15 decision that W5 builds *two* methods. The Poisson process-variance identity is what makes it estimable from a one-way summary at all. Degenerate cases **refused by name, never clamped** — FR-MODEL-113. The refusal test is **inverted, not deleted**, so the record of what was once refused survives |
| The contract half (FR-OVR-6, FR-PLAT-48, FR-MODEL-86/87) | Six MODEL-owned schemas reconciled, and the **guard tests fixed first** — see below |
| Twelve NFRs measured or given a verdict (`02` §9) | Five measurement blockquotes, each with machine, load average, budget and a met/not-met table |
| `GET /api/v1/models`, and the silent-ignore closed | Three list routes gain `extra="forbid"` query models |

##### The guard tests were the defect, not only the schemas

Fixing the existence test surfaced three defects **in the checking machinery**, none of which
was in the work order:

- `_type_map` did `properties.update(...)`, so the *last* variant naming a field replaced
  every earlier definition — and a conditional refinement is exactly that shape. Following
  `then` therefore **deleted** the real definitions and took the walker from 36 paths to 28.
- `const` was invisible to `_scalar_types`, so a `{"const": …}` branch was typeless.
- `ENVELOPE_FIELDS` was wrong **in both directions**: the literal
  `{id, slug, version, dataset_id}` — three real envelope fields out of fourteen, plus one
  that is not an envelope field at all. It had been hiding `TransparencyArtifact.id`,
  `created_at` and `Diagnostics.id` from a check they should always have failed.

**The broken-input proof earned its keep by finding two dead checks**, including the exact
mechanism by which `gbm.quantile_crossing` (FR-MODEL-78) and `gbm.tree_count` sat absent from
the published contract for months with every test green: the existence test compared
**top-level names only**, and the type test narrows only when a path stops being shared.

The sharpest single finding: `model.schema.json`'s `fit_result` was one flat block requiring
`converged`, which neither `GbmFitResult` nor `EbmFitResult` has — so **no GBM or EBM fit
could ever have validated against the published contract.**

##### `CLAUDE.md` §13, rule by rule

1. **Scope derived from the specification first.** `scope-audit.py MODEL`: **125 in scope,
   111 evidenced (89 %), 14 without** — and the roadmap's own claim of "seventy-eight
   requirements" was not stale but **never a count of `02`** (it is §6's Phase-1b planning
   estimate, borrowed from a table two pages away; the derived count on the day it was
   written was 85). Endpoints **41 of 41** after `GET /models`; catalogues clean.
2. **Deliverables audited against the definition.** The §5.1 endpoint table matched on all
   40 rows, which is *how the parameters went unexamined* — `--endpoints` compares method and
   path, so a wrong parameter is invisible to it. Checked by hand: `?dataset={slug}` returned
   **200 with every factor in the workspace**, one `{id}` row of 23 was wrong, and §5.2 had
   drifted on nine functions.
3. **Gates green locally, both halves, each exit code read.** ruff 0 · mypy 131 files ·
   lint-imports 3 kept 0 broken · `pytest backend/tests` **774 passed** ·
   `pytest tests/ packages/` **917 passed** · audit-docs all checks · req-coverage 495/248 ·
   `generate-contracts.py --check` 23 match · frontend install, generate:api, type-check,
   lint, **131 tests**, build — all 0.
4. **Enforcement proven on broken input**, every time: the trigger at the pre-fix revision and
   against a deliberately naive guard; the floor entry removed; the resolver removed; nine
   mutated schemas; `tasks.py` reverted to capture the before-output.
5. **NFRs measured, not asserted** — five blockquotes in `02` §9, each with the machine, the
   **load average** (the same proposal measured 8.58 s at load 1.6 and 20.01 s at load 8.4),
   the budget and the shortfall as a percentage.
6. **What was *not* delivered** — the three numbers, below.
7. **Documents updated in the same commit** as the code, including two skills and their index.
8. **Repository clean**: one branch, no tracked build artifacts, the generated frontend client
   still git-ignored.

##### The headline, as three numbers rather than one

`scope-audit.py` counts a requirement as evidenced when *any* test carries its marker, so
"111 of 125" means **declared-or-refused**, not built. The roadmap caught this once on
FR-MODEL-81 (2026-08-16) and never applied it to the headline. Stated properly:

- **108 built** — implemented and evidenced by a test of the behaviour.
- **3 declared-and-refused-by-name** — FR-MODEL-59 (`separate_model`, `LOSS_TREATMENT_UNIMPLEMENTED`),
  FR-MODEL-88 (`spline`/`polynomial`/`offset`/`expression` refused at resolution), and
  FR-MODEL-87, whose subject *is* the staged contract. **This was five before this slice**:
  FR-MODEL-23 and FR-MODEL-80 are now genuinely built.
- **14 unevidenced, each with a verdict** — every one below.

| Requirement | Verdict | Owner |
|---|---|---|
| FR-MODEL-6 — `expression` factors | Not started | **W30**, accepted by the maintainer 2026-08-22 |
| FR-MODEL-40 — `expression` objectives | Not started | **W30** (OQ-MODEL-1) |
| FR-MODEL-82 — proxy detection | Not started | **Phase 3 / W31** (OQ-MODEL-7) |
| FR-MODEL-110 — rebuild reuses stored numbers | **Built 2026-08-22** (W5, the closure slice), and the verdict this row carried was false. *(Original verdict, struck rather than overwritten:)* ~~**Delivered but untested** (OQ-MODEL-17, 2026-08-21)~~ — **it was neither.** The branch FR-MODEL-110 describes runs *before* `build_glm_approximation` and `compute_diagnostics`; in the handler both ran unconditionally and `should_fit` first appeared after them. A call-counting test on the pre-change code shows **both** running on a rebuild, so the marker this row said was owed would have been a false claim rather than a missing one. The requirement is amended in one clause by building it: the branch **skips** the surrogate's `Diagnostics` compute rather than **loading** it, because the result is consumed only inside the `should_fit` arm and loading it would be a query whose result is discarded — `02` FR-MODEL-110(ii) | ~~W5 — a marker is owed, not a feature~~ **Discharged by W5.** Three marks, and the audit found it rather than the Phase-1b measurement its owner clause named |
| FR-MODEL-112 — offsets-from-model widening | Not started, sequenced | **Phase 1b**, (a) then (c) |
| NFR-MODEL-1, -10 | **Measured by extrapolation** — 173 s of 600 s, 16.0 GB of 32 GB | The slice with a 16-core worker |
| NFR-MODEL-2 | **Measured once, growth unmeasured** — 963 s of 1 200 s on an *assumed* linearity | Same |
| NFR-MODEL-3 | **Measured and breached by all three grouping methods**; the cause is the one-way summary, not Ward | The factor-workbench slice |
| NFR-MODEL-4 | **Measured and met** since OQ-MODEL-24 was decided 2026-08-22 — re-scoped off FR-MODEL-51's block and re-set to 50 % at a named scale; 32.1 % at the worst measured arm | None required |
| NFR-MODEL-13 — the type-III block | **Measured and breached** at 678 013 × 60: more than 1.61× per tested factor against a 1.0× bound, and the observation is *censored* | **Phase 1b**, with the warm-denominator run the corrected multiples rest on |
| NFR-MODEL-14 — the GBM block | **Measured and met** — 0.0480 fits per scoring pass against 0.06, 1.25× headroom | None required. The sweep it prices is **no longer uncapped**: OQ-MODEL-26 decided 2026-08-22, FR-MODEL-118 bounds the categorical grid to the 20 most-exposed levels — 0.96 of one fit at this measured rate |
| NFR-MODEL-5, -11 | **Measured and met**, 50× and 380× headroom | None required |
| NFR-MODEL-7 | **Out of Phase 1 scope — maintainer verdict 2026-08-22**, on plan review 3's question 2(a). Zero export and import paths exist, no row ever named one, and its parent FR-OVR-2 carries zero markers. *(Original verdict, kept:)* **Nothing to test** — zero export and import paths exist | **None in Phase 1.** *(Original owner cell, kept:)* **Unassigned**, needs a verdict before it can have a test — which is the absence this verdict removes |
| NFR-MODEL-12 | **Measured and held** — 0.22 s against 5.22 s | None required |

Nine of the fourteen carry a **recorded measurement** rather than a marker, which §13 rule 1
admits as evidence where a test is the wrong instrument — and says so with the number.

##### Not delivered, and honestly so

- **OQ-MODEL-24 is decided** (2026-08-22, option (a)). NFR-MODEL-4 is re-scoped off
  FR-MODEL-51's block, given the wall-clock denominator in its own text, and re-set to 50 %
  at a named scale; the type-III block is NFR-MODEL-13 and the GBM block NFR-MODEL-14.
  **What the decision did not fix is stated rather than closed over**: NFR-MODEL-13 is
  breached at 678 013 × 60 on a *censored* observation, owned by Phase 1b, and the
  partial-dependence sweep NFR-MODEL-14 prices is uncapped — OQ-MODEL-26, **since
  decided** (2026-08-22, FR-MODEL-118).
- **OQ-MODEL-23 is decided** (2026-08-22). `offset` is superseded as a Factor type
  (FR-MODEL-114), the arm kept in the published contract because artifacts are immutable and
  a stored row must stay loadable. `spline` and `polynomial` are **not scheduled and not
  deferred into silence**: both stay declared and refused, gated on FR-MODEL-115, owned by
  W30. The blocker turned out to be neither of them — **no continuous Factor can be rated or
  reviewed today**, including the `identity`-over-numeric one that already resolves, because
  FR-MODEL-21's relativity table is categorical-only and FR-RATE-16 seeds from it. That gap
  appeared in none of the question's four options.
- ~~**`FactorIntent.OFFSET` is a live silent mis-fit**~~ — **decided 2026-08-22 as OQ-MODEL-25.**
  It was declarable through the API and read by neither fit path, so the factor was fitted
  with a free coefficient. FR-MODEL-116 supersedes the arm — on a **layer** argument, not the
  duplication one the question recommended, because `OffsetSpec` turns out to be strictly
  *less* expressive than a per-factor intent. Two things the question did not say: `intent` is read in
  exactly **two** places — `rateable()`, which nothing in production calls, and the
  `factor.created` audit event, which **records** the declared intent without gating on it,
  so the platform attested to a property the fit never had — and **`diagnostic` carried the identical
  defect** — refused by FR-MODEL-117 pending OQ-MODEL-27 rather than left live beside a
  fixed twin, and **since superseded with it** (2026-08-22, OQ-MODEL-27, FR-MODEL-120).
- ~~**`FactorIntent.DIAGNOSTIC` has no stated meaning**~~ — **decided 2026-08-22 as OQ-MODEL-27**,
  superseded by FR-MODEL-120 **without the missing meaning ever being supplied**, because both
  readings of it fail: the distinct one — resolved and reported, held out of the linear
  predictor — is a property of *one fit* mis-sited on a Factor reused by every spec that names
  it, and the redundant one is `control` already. The capability is real and is re-sited on the
  Model Spec, where `ModelSpecCommon.factors` is a flat `tuple[UUID, ...]` with no per-factor
  attribute to carry it; gated, owner W30. **FR-MODEL-117's ground for holding the question
  open was wrong against the decision that wrote it** — it measured `diagnostic` against the
  *duplication* argument, which OQ-MODEL-25 had refuted, rather than the *layer* argument it
  actually decided on. Corrected in place rather than quietly dropped.

- **No GBM could fit an `interaction` Factor at all**, from FR-MODEL-91 on 2026-08-18 until
  2026-08-22 — **found and fixed here** (FR-MODEL-119), not merely recorded. `resolve_factors`
  requires a cross's operands to be supplied and gives them no term of their own; `fit_glm`
  builds its design from the resolved *terms* and never sees them, while the GBM encoder
  iterated the *factor list* and raised `KeyError` on the first operand. One line of
  difference between two sibling paths. Behind it sat two more `IndexError` sites in the
  per-factor diagnostics blocks, masked by the first. All three went unseen because **only
  the GLM suite ever fitted a cross** — the GBM suite covers `interaction_constraints`, a
  backend parameter of a similar name and no relation. Found while deciding OQ-MODEL-26, by
  writing the test the requirement implied rather than by reading the code.
- **A GBM declaring a *sparse* interaction still could not produce diagnostics** — found
  2026-08-22 while deciding OQ-MODEL-28 (FR-MODEL-122), one day after FR-MODEL-119 was believed
  to have cleared that path, and **recorded rather than fixed**: the remedy is W30's slice.
  FR-MODEL-119 skipped the cross and left its **operands** in the list, and both per-factor
  blocks permute and sweep an operand's raw column *alone* — which recombines the operands into
  cells the fit never saw. Measured on a book carrying 3 of 9 cells, which FR-MODEL-91 says is
  what a real cross looks like: the fit succeeds, the booster's whole feature order is
  `('area_x_fuel',)`, and `compute_gbm_diagnostics` then raises
  `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` naming all six absent cells. It reaches production —
  `load_factors` returns `ordered + operands` — and dies **uncoded**, the raise landing outside
  the block that maps a `GbmFitError` to a platform error code, which is the same reader-facing
  failure FR-MODEL-119 recorded for the bare `KeyError` and believed it had removed. **A dense
  fixture hid both defects**: the suite's only cross draws its two sides independently, so every
  cell is populated and no shuffle there can produce an unseen pair. The lesson is a fixture
  one — a cross whose cells are all full is not a cross, and FR-MODEL-91 said so in writing
  before either defect was built.
- **Two of OQ-MODEL-28's four options turned out to be one option**, on the half the question
  believed separated them — recorded because the lesson is general to this codebase. "Permute
  the cross's combined column" is not reachable at all: `predict_gbm` re-resolves the cross from
  the operands' **raw** columns on every call, so **every per-factor GBM diagnostic is bounded by
  what can be expressed as a raw-column edit**. A shuffle applied to both operands under one
  shared order permutes the *pairs*, which is exactly a permutation of the resolved cross column
  — measured, the observed cell set is identical before and after and 67.8 % of holdout
  predictions move. The options differ only on the sweep grid, where the cross's observed cells
  score and the Cartesian product of operand levels does not: FR-MODEL-32 again, the wall that
  killed FR-MODEL-118's pooled `other` bar four requirements earlier.
- **Two defects in `_sweep` found and deliberately *not* fixed**, recorded rather than
  tuned away because neither is what OQ-MODEL-26 asked and both change numbers already
  persisted on fitted artifacts. First, `PartialDependencePoint.exposure_share` reports a
  **row-count** share while its name and its docstring say exposure — equal only on a book
  where every row carries the same exposure, which freMTPL2 is not. Second, on a *numeric*
  factor the share is `1/len(points)`, which the ten-quantile grid makes roughly true by
  construction and the grid's own de-duplication can make badly false: a low-cardinality
  numeric column collapses to a few points and each is then reported at an equal share it
  does not hold. The field exists to stop a reader taking a spike over thin exposure for a
  rating signal (`02` §4), so both are worth an owner. Owner: W6b, with the frontend that
  first plots the curve. Fixed 2026-08-23 (W32-5), under FR-MODEL-125 — all four sites
  moved together, the level ranking and the omission record's share included, because the
  requirement makes the ranking and the emitted share the same quantity. NFR-MODEL-14
  re-measured after the fix: 0.0356 fits per scoring pass against the 0.06 budget, at load
  average 0.85, on the 75 000 x 60 x 500 arm the 0.0480 reading was taken on.
- **The sweep runs over a factor's *source column*, not its resolved levels** — found while
  deciding OQ-MODEL-26, recorded not fixed. `_sweep` holds `source_columns[0]`, so a `grouping`
  factor collapsing a 10 000-code column to eight groups still costs 10 000 scoring passes and
  emits 10 000 points that take eight distinct values, and a `banding` factor gets a curve over
  raw ages rather than over its bands. FR-MODEL-118's cap bounds this — it is the pathological
  case the cap was written for — but the cap counts *source* levels, so the requirement says so
  rather than implying it counts the factor's own. Owner: W6b. Fixed 2026-08-23 (W32-5),
  under FR-MODEL-125 — a banding or grouping factor is now gridded over its resolved levels
  and the source column held at a representative raw value drawn from the frame, so
  `predict_gbm` runs `resolve_factors` exactly as it does in production. Cross factors are
  *not* covered: they still grid over their first source column, because a representative
  value for a cross level is a tuple across several columns. Owner: W6b, with the frontend
  that first plots a cross factor's curve.
- **Two §14 question-4 spec-accuracy findings against `02`**, both surfaced by OQ-MODEL-25 and
  neither fixed here, because §14's output is a proposal rather than an edit. §5.3's factor
  workbench Contents column claims "monotonic-direction and intent controls", and the built
  view contains the string `intent` **zero times** — so no actuary can declare a non-`risk`
  intent through the UI at all, which is also why the supersession's blast radius is as small as
  FR-MODEL-116 states. And `rateable()` is exported from `pricing-core` and absent from §5.2's
  signature table, in the code→spec direction. Owner: W6b.
- **`02` §4.6 diverges from the parser in three ways**, the third being that the implemented
  grammar is *wider* in operators and *narrower* in functions, and `where` — the one construct
  §4.6 singles out by name — **does not exist**. Recorded, not resolved: W30 owns that grammar.
- **FR-MODEL-15 is partly unmet** — `source_level_stats` is in the contract and not in the
  Python, so the marker on its test overstates it. Owner: W6b.
- **NFR-MODEL-6 is half evidenced** and the roadmap called it evidenced.
- **Five constraint-level contract-drift classes remain unguarded**, plus arm-level
  attribution. Owner: W6b.

##### Findings the audit did not name

- **FR-GOV-37's `peril_structure` justification was false when written** — it says the type
  "has no §3.3 row at all", and §3.3 has carried one since 2026-08-14, *four days earlier*.
  The conclusion survives on a different reason; the unenforced half is W17's.
- **`CLAUDE.md` §11's `alembic upgrade head` could never have worked** — the app defaults to
  `gip:gip`, compose provisions `gipricing`. Invisible because the tests carry their own DSN
  and CI sets the variable explicitly: **a defaults mismatch that every automated path routes
  around is invisible to every automated path.**
- **`ReconcileRequest.tolerance` published `anyOf: [number, string]`** — FR-OVR-18's audit
  swept fields that *were* `DecimalStr`, so one that should have been was invisible to it.
- **`transparency_artifact_id` is superseded, not owed.** `ix_transparency_model` is not
  unique, so a Model accumulates artifacts and a single back-pointer would be wrong the first
  time a second was written.
- **`00` §5.2 illustrated pagination with `GET /api/v1/models`** — an example route nothing
  implemented, which is why "40 of 40 endpoints" measured the spec against itself.

##### Three process findings

1. **A slice updates the row that describes itself, and every other place counting or judging
   slices is unowned.** That single mechanism produced the stale slice count, the
   buildable-slice counter left at one when every row beneath was struck, and six stale
   verdicts in the diagnostics table. #116 did it; #124 and #125 did it again.
2. **PRs #124 and #125 landed with no slice records** — the 3rd and 4th such omission. Both
   are now written from the merged diffs, each saying in the record that it was written late.
   The Tweedie one is the costliest: its struck row says "DELIVERED" while what it actually
   found — that the design on file produced a *measurably biased* estimator, and that the
   fixture built to check it was wrong in the same direction — lived only in a squashed
   commit message.
3. **This slice committed the defect it was fixing.** FR-MODEL-113 was appended and left
   unevidenced for two hours, exactly the marker-misattribution that had let Bühlmann–Straub
   read as covered while refused at runtime. Caught by re-deriving with `scope-audit.py`
   *after* editing — not by review, and not by care.

**Gate:** both halves, run locally, each exit code read. Recorded in rule 3 above.

#### W32-6 slice — the backtest and custom-objective endpoint tests, 2026-08-23

One of six concurrent test-hardening slices. **Nine routes that had two OpenAPI-presence
assertions between them now carry endpoint tests** — six over the backtest routes, sixteen
over the custom-objective ones. **No requirement id was allocated**: every marker names one
that already existed, which is also why the coverage total did not move (below).

##### What was built

| Delivered | Evidence |
|---|---|
| The backtest routes over HTTP (FR-MODEL-57, FR-MODEL-92) | `backend/tests/test_api_backtests.py` — **6 passed, 0 skipped**. 202-and-a-job on request, the stored summary on read, a 404 that names the id asked for, cross-workspace absence, and both refusals (`model:fit` to request, `model:read` to read) |
| The custom-objective routes over HTTP (FR-MODEL-95, FR-MODEL-75) | `backend/tests/test_custom_objectives_api.py` — **16 passed, 0 skipped**. Create, read, usage, certify and submit; two cross-workspace 404s; four RBAC refusals **each with a passing case beside it**; three conflicts (certify while under review, submit twice, evidence incomplete); and the `expression` kind refused by name |
| `backtests` joins the append-only row list (`00` FR-OVR-1) | `test_artifact_immutability.py`, 13 tests → **14**. The table carried both layers already — the narrowed grant and the `artifact_append_only` row and statement triggers — but was **absent from `_APPEND_ONLY_ROWS`**, the one list that makes the test fire against it |
| The derive refusal split in two (FR-MODEL-75) | `test_custom_objectives.py` — finding 1 below |

##### The findings, and which side was wrong in each

1. **The derive refusal proved something other than what it claimed — the test was wrong.**
   It granted the caller nothing and asserted `status_code in (403, 409)`. `FitModels` is a
   *route* dependency, resolved before the handler body, so the 409 arm was unreachable and
   the test could never observe the kind gate it was named for. Split in two: an ungranted
   caller must get **403 `PERMISSION_DENIED`**, and a caller holding `analyst` must get
   **409 `OBJECTIVE_KIND_NOT_ENABLED`**. Proven load-bearing by mutating the raised code to
   `VALIDATION_FAILED` — exactly one of the two fails, while the status stays 409, so the
   `["code"]` assertion and not merely the status is what carries the test.
2. **`backtests` was locked in the database and missing from the test's list — the test list
   was wrong.** Entry added, and the trigger shown to fire against a deliberate `INSERT`.
3. **The plan named FR-MODEL-40 as "backtest results" — the plan was wrong.** FR-MODEL-40 is
   the **symbolic derivation of gradient and hessian from an `expression` objective's loss**,
   a Phase 2 capability gated off by FR-MODEL-75 and implemented by nothing. Marking backtest
   tests with it would have put a traceability claim on a requirement no line of this
   repository satisfies — precisely the "a marker is a claim, not a proof" failure
   `CLAUDE.md` §13 rule 1 warns about. The backtest requirement is **FR-MODEL-57**, which
   `test_backtests.py` already carried; the new markers were corrected to it before commit.
   **Verdict on FR-MODEL-40: deferred, owner Phase 2**, recorded on its spec row.
4. **A docstring documented `n_points=300` — the comment was wrong**, and by more than
   staleness: `SamplingSpec` now forbids that value (`ge=1_000`). Corrected to name
   `COUNT_GRID`, which is where the real grid lives.
5. **`02` §5.1 said `/derive` answers 422; the code answers 409 — the spec was wrong.** The
   code is right: the kind gate fires before the request body is looked at, so there is
   nothing to report as a validation failure. Corrected by a dated §5.1 amendment.
6. **Three shape findings recorded rather than fixed**, each with an owner, below.
7. **Three read permits were granted by a principal holding both permissions — the
   tests were wrong.** Found by mutation while proving the suite load-bearing (§13
   rule 4): swapping `ReadModels` for `FitModels` on `GET /models/backtests/{id}`,
   `GET /custom-objectives/{id}` and `.../usage` left all 22 new tests green, because
   every permit read as the `analyst`, which holds `model:read` *and* `model:fit`. A
   route re-gated on `model:fit` would have kept them green while every read-only
   principal lost the artifact. Corrected: the three permits now read as the
   `auditor`, and the same mutation fails them.

##### Recorded, not fixed

- **`uq_backtests_model_version` is not workspace-scoped.** Every other uniqueness constraint
  on a workspace-owned table is. Whether that is a defect or a deliberate global identity is
  a governance question and a migration, not a test change. **Owner: unassigned — raise
  before the next slice that touches this table.** Recorded in `02` §4.12.
- **The `derive` route publishes a `200 CustomObjective` it can never return** — the only
  reachable outcome is the 409. A `model-schema` change. **Owner: the Phase 2 slice that
  lands `expression` objectives.** Recorded in `02` §5.1.
- **The custom-objective read routes are single-layer RBAC.** Consistent with the rest of the
  API, so this is noted rather than proposed as a change. **Owner: the next `06` RBAC slice.**

##### What did not move, and why that is the point

**This slice moved requirement coverage by zero** — measured on the branch with its two new
test files present and again with them moved aside, and identical both times (**263 of 507,
51.6%**, on the base it landed against). The plan predicted a rise on the strength of
FR-MODEL-40 gaining its first marker; finding 3 is why it did not. *(The plan's stated
starting figure of 258 was stale before this slice finished — W32-2, W32-3, W32-4 and `07`
FR-PLAT-57 all landed on `main` while it ran. The absolute figure is whichever of them landed
last; the movement attributable to W32-6 is zero against any of them.)* FR-MODEL-57, FR-MODEL-92, FR-MODEL-95 and FR-MODEL-75 were each
already marked somewhere, so **four requirements gained real endpoint evidence while the
count stood still** — the clearest demonstration to hand that the coverage number counts
markers, not proof, and that §13 rule 1's "a marker is a claim" is the load-bearing half.

`scope-audit.py MODEL --endpoints` is unchanged at **41 of 41 declared endpoints published**;
this slice added tests, not routes.

### Phase 1b — Modelling Workbench

**Goal:** factors, bandings, groupings, GLM and GBM fitting, diagnostics, transparency
artifacts, model versioning.

**Demo-able outcome:** the actuary bands and groups factors, fits a GLM and an XGBoost
model, compares them, and gets one approved — **`wf-01` end to end**.

| # | Workstream | Depends on | Notes |
|---|---|---|---|
| ~~**W5**~~ ✔ | Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective **templates only** | W4 (1a) | **Closed 2026-08-22** — 110 built · 10 declared-and-refused-by-name · 16 unevidenced with a verdict, of 136; 41/41 endpoints. See the closure record above. Every `MODEL` requirement — the largest single workstream in the project; `scope-audit.py MODEL` counts them, and per plan review 3's question 5 (accepted 2026-08-22) that is now the only place a reader should take a count from. **Started 2026-08-15**: ~~twenty-two~~ **twenty-eight** slices in — the GLM spine, bandings and groupings, the factor workbench, diagnostics, spec validation, the model lifecycle, model comparison, `wf-01`'s citation audit, gradient boosting with its transparency artifact, `wf-01` driven end to end, peril structures with their reconciliation, interaction factors, backtests, prediction, custom objectives, FR-DATA-47's artifact triggers, the profile contract, `top_levels`' exposure per level, the exact-decimal refusal of a float, paired quantile models, the GLM approximation as a Model (FR-MODEL-96, FR-MODEL-102 — measured at +0.26 s / ~7 % against a **single-factor** fixture; type-III diagnostics refit the surrogate once per factor, so this does not bound a multi-factor model, and `type_iii=False` is the lever if that ever bites, not pulled without the maintainer), and **custom metrics** (FR-MODEL-45/103/105/106/107/108 — a Custom Metric reaches `approved` on the same lifecycle and grammar as a Custom Objective, `GbmSpec.eval_metrics` is now honoured rather than merely declared, and MODEL's endpoint axis closed at **40 of 40**, the first module in this repository to publish every declared endpoint), **regularisation and cross-validation** (FR-MODEL-20/53), **Tweedie power by profile likelihood** (FR-MODEL-22), **offset from another model** (FR-MODEL-24), **EBM via interpret-core** (FR-MODEL-37) and **GBM declared weights with the dropped eval metric record** (FR-MODEL-19/111), and **the audit-remediation slice** (2026-08-22, this one); see the slice records below. *(The count said eighteen and omitted the exact-decimal slice, which had already landed as PR #116; corrected 2026-08-19 by the paired-quantile slice.)* *(It went stale the same way again and is corrected 2026-08-22 by the audit-remediation slice: five slices — regularisation/CV (#124), Tweedie (#125), offset (#126), EBM (#129) and GBM weights (#130) — landed between 08-21 and 08-22 with the count left at twenty-two, while this file's own newest record already called itself "the twenty-seventh slice". Both stale values are kept. **The mechanism is the same both times and is worth naming rather than re-fixing:** a slice's PR strikes its row in the outstanding-work table and stops there, and this count is a second place nothing reconciles against that table — #116 did it, then #124 and #125 did it again. The same mechanism left the buildable-slice counter at one when every row beneath it was struck, and left six verdicts stale in the diagnostics slice's table. **A slice updates the row that describes itself; every other place that counts slices is unowned.** The count is of **numbered** slices, so the three decision-only records of 2026-08-18 (PRs #106, #107, #108) have records and no number and have never been in it.)* **The prediction slice (PR #102, 2026-08-18) landed without a slice record** — the omission is recorded here rather than reconstructed from the diff; what it found is in `02`'s dated notes — FR-MODEL-93, OQ-MODEL-13 and OQ-MODEL-14, plus the `inverse`-link resolution at §3.4 — and in `.claude/skills/python-test`. **Scope set by the 2026-08-15 decisions:** templates only, with the certification machinery built here (FR-MODEL-75/76); both credibility methods, not one (FR-MODEL-80); SHAP interaction *suggestions* (FR-MODEL-79); the complexity diagnostic and its optional gate (FR-MODEL-81); paired quantile models as the only GBM interval (FR-MODEL-77/78). **W5 also finishes `wf-01`, and has**: the citation audit and the journey test landed 2026-08-17, and on 2026-08-18 the peril-structure and interaction slices drove the last three pinned steps, so FR-OVR-17(ii) for `wf-01` is **delivered** — the first of the five journeys. **The closure slice (2026-08-22) is the last, and the count above is deliberately not incremented to twenty-nine**: plan review 3's question 5 was accepted the same day, and adding a fourth hand-written count to the file whose staleness prompted the proposal would be the clearest possible way to ignore it. The slice records below are the list; `scope-audit.py` is the count |
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
| **W9** | Rating algorithm contract, validation, bundle compilation | `03` FR-RATE-1..13, 22..27 |
| **W10** | Rate tables incl. seeding from models, diffs, bulk operations, import/export | FR-RATE-14..21 |
| **W11** | Scoring: real-time, batch, trace, one shared evaluator | FR-RATE-34..42; NFR-RATE-1 is the hard target |
| **W12** | Testing: golden quotes, property assertions, regression runs | FR-RATE-43..45 |
| **W13** | Dislocation with attribution | FR-RATE-46..49 |
| **W14** | Deployment: environments, atomic switchover, rollback, shadow — **and the tenancy mechanics ADR-0006 requires** | FR-RATE-50..55; `07` FR-PLAT-28..31, and added 2026-08-15 by OQ-OVR-1's decision: **FR-PLAT-56** (a deployment refuses to start against another tenant's database) and **FR-OVR-16** (a Job records the platform build, because version skew between tenants is now permanent). Any earlier `Job` migration should carry FR-OVR-16's column rather than wait for this |
| **W15** | Frontend: **DAG designer (Vue Flow)**, rate table editor, quote sandbox + ladder waterfall, dislocation views | The DAG designer is the single largest frontend effort in the project |
| **W30** | **`expression` custom objectives** — SymPy derivation, the gradient/hessian compilation target, the authoring UI, and lifting `expression_objectives_enabled` **plus `custom_objective:author` and its check, which `06` FR-GOV-39 requires the `expression` kind to arrive with** | Added 2026-08-15 by OQ-MODEL-1's decision, which moved this work out of W5 rather than deleting it: `02` FR-MODEL-40/41, FR-MODEL-75, §4.6, and `wf-05` Route B. It depends on nothing in W9–W15 and could equally be pulled into 1b if W5 finishes early — but it must not start before the certification machinery it fronts (FR-MODEL-76) has run for a phase, which is the whole point of the decision |

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
| **Before Phase 1b** — *re-opened 2026-08-22* | ~~OQ-OVR-5~~ ✔ *2026-08-14*, ~~OQ-MODEL-1~~ ✔, ~~OQ-MODEL-5~~ ✔, ~~OQ-PLAT-6~~ ✔, ~~OQ-OVR-6~~ ✔ *all 2026-08-15*, ~~OQ-OVR-7~~ ✔, ~~OQ-DATA-8~~ ✔, ~~OQ-MODEL-8~~ ✔, ~~OQ-MODEL-9~~ ✔ *all 2026-08-17*, ~~OQ-MODEL-10~~ ✔, ~~OQ-GOV-7~~ ✔, ~~OQ-MODEL-14~~ ✔ *all 2026-08-18*, ~~OQ-DATA-9~~ ✔ *2026-08-19 — raised in W5 and never placed on this table until it was decided, so the gate it belonged to had already closed; it gates W6b's dataset list, which is Phase 1b work*, ~~OQ-MODEL-15~~ ✔, ~~OQ-MODEL-17~~ ✔, ~~OQ-MODEL-22~~ ✔ *all 2026-08-21, raised in W5 and never placed on this table until decided — FR-MODEL-109 delivered with the decision, FR-MODEL-110's trigger is Phase 1b's job-latency measurement, FR-MODEL-112's first slice is Phase 1b's*, ~~OQ-MODEL-25~~ ✔, ~~OQ-MODEL-26~~ ✔ *both raised **and decided** 2026-08-22, out of the two modelling decisions taken that day — the first a live silent mis-fit, the second an unbounded diagnostics sweep. This gate had been closed since 2026-08-21; it re-opened rather than pretending they arrived earlier, and closes again the same day. Neither landed where its question pointed: FR-MODEL-116 supersedes the offset **intent** on a layer argument, the duplication argument having failed checking, and half of OQ-MODEL-26 was withdrawn as a no-op. Each raised a successor owned by W30, which is Phase 2 — placed at that gate rather than held here*, ~~OQ-MODEL-29~~ ✔, ~~OQ-MODEL-30~~ ✔ *both raised 2026-08-22 by W32-1's constraint guard and never placed on this table at all — the fifth time a question has been decided without appearing here, and the reason the count below is a recount rather than an increment. The first was decided 2026-08-22 (an inert `seed` keyword removed), the second 2026-08-23 into FR-MODEL-126. Both gate Phase 1b slices, so they belong at this gate and not a later one* | 20 (0 open) |
| **Before Phase 2** — *re-opened 2026-08-22* | ~~OQ-RATE-1~~ ✔, ~~OQ-RATE-2~~ ✔ *both decided by spike*, ~~OQ-MODEL-3~~ ✔ *2026-08-17*, ~~OQ-MODEL-11~~ ✔, ~~OQ-MODEL-12~~ ✔, ~~OQ-RATE-3~~ ✔, ~~OQ-RATE-4~~ ✔, ~~OQ-RATE-6~~ ✔, ~~OQ-PLAT-3~~ ✔, ~~OQ-GOV-8~~ ✔ *all 2026-08-18*, ~~OQ-MODEL-23~~ ✔ *2026-08-22 — decided into FR-MODEL-114 and FR-MODEL-115; the continuous-effect gate it turns on is W30's, which is Phase 2 work*, ~~OQ-MODEL-27~~ ✔, ~~OQ-MODEL-28~~ ✔ *both raised 2026-08-22 out of the OQ-MODEL-25 and OQ-MODEL-26 decisions and **both decided the same day**, before the gate they were filed against — OQ-MODEL-27 into FR-MODEL-120, OQ-MODEL-28 into FR-MODEL-121 and FR-MODEL-122. Filing them here rested on a claim that held for one of them: "both have interim behaviour in place, so neither blocks" is true of `diagnostic`, which really is refused, and **false of the interaction**, whose skip-and-record leaves a sparse cross raising `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` out of `compute_gbm_diagnostics` (FR-MODEL-122). Deciding both early cost one day and turned an interim nobody had exercised into a measured defect with a remedy. W30 still owns the slices; what it no longer owns is the choice* | 13 (0 open) — *recounted 2026-08-23: this read `13 (2 open)` while every one of its thirteen ids was struck. The two it meant were decided on the day they were filed here, and the count was written from the intent to file rather than from the row* |
| ~~**Before Phase 3**~~ ✔ **all decided** | ~~OQ-GOV-1..6~~ ✔ *2026-08-18*, ~~OQ-OVR-1~~ ✔ *decided 2026-08-15 — ADR-0006, and it changes what W14 builds in Phase 2 rather than waiting for Phase 3*, ~~OQ-MODEL-7~~ ✔ *evidence in Phase 3 (W31), never a block* | 8 (0 open) |
| **Before Phase 4** | OQ-OPT-1..6, OQ-MON-1..5, ~~OQ-DATA-4~~ ✔ *decided 2026-08-14 — out of scope*, OQ-PLAT-8 *raised 2026-08-23 out of the scheduling decision: an idempotency key naming a Job that already failed. Filed here because the requirement that makes it load-bearing, FR-PLAT-61, is W27's* | 13 (12 open) |
| **Deferred / any time** | ~~OQ-OVR-3~~ ✔, ~~OQ-OVR-4~~ ✔ *both decided 2026-08-14*, ~~OQ-DATA-3~~ ✔, ~~OQ-DATA-5~~ ✔, ~~OQ-DATA-6~~ ✔ *all decided 2026-08-14*, ~~OQ-MODEL-2~~ ✔, ~~OQ-MODEL-4~~ ✔ *amended 2026-08-23 — the decision stands, its two-number evidence clause is withdrawn*, ~~OQ-MODEL-6~~ ✔ *all decided 2026-08-15*, OQ-MODEL-31 *raised 2026-08-23 out of that amendment: what evidence stands beside an interaction candidate, once a per-pair exposure share is shown to be `1.0` by construction*, ~~OQ-MODEL-13~~ ✔ *2026-08-18 — reopened by its own trigger, the first consumer of an aggregate interval*, ~~OQ-DATA-10~~ ✔ *2026-08-19 — a deferral with a trigger (FR-DATA-52), raised in W5 and never placed here until decided*, OQ-RATE-5 *raised 2026-08-19 in the FR-MODEL-96 slice and placed 2026-08-21*, ~~OQ-PLAT-2~~ ✔, ~~OQ-PLAT-4~~ ✔, ~~OQ-PLAT-5~~ ✔ *all decided 2026-08-23 on the maintainer's instruction to resolve them: no Dagster (FR-PLAT-61), no workspace quota (FR-PLAT-60), and a local-only identity provider behind an opt-in profile (FR-PLAT-58, FR-PLAT-59). The middle one is a **rejection**, not the deferral its recommendation asked for — that deferral's trigger had been dead since ADR-0006*, ~~OQ-PLAT-7~~ ✔ *decided 2026-08-22 and left unstruck here for a day* | 16 (2 open) |

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
