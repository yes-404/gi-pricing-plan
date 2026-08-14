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
| **Phase 0 (Specification)** | Effectively complete — 8 specs, 5 workflows, 5 ADRs, 31 contracts, 408 requirements |
| **Blocking Phase 1** | **7 decisions** (§3). Spike S3 closed 2026-08-14. Track A research **closed**; 45 of 46 open questions remain but only 7 gate Phase 1 |
| **Code written** | None, by design (`CLAUDE.md` §0) |

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
large-loss treatment, and full-snapshot ingestion. Three remain before 1b:

| Question | Gates | Why it blocks |
|---|---|---|
| **OQ-PLAT-1** Celery vs a transactional Postgres queue | **1a** ✔ *decided* | Job submission is in the first sprint, and transactional enqueue interacts directly with the audit rule (`06` R2) |
| **OQ-DATA-1** large-loss capping: dataset or model? | **1a** ✔ *decided* | It *is* the 1a/1b boundary — deferring it makes it a contract change rather than a decision |
| **OQ-DATA-2** append ingestion vs full snapshots | **1a** ✔ *decided* | W4, and only if the first real dataset is large enough that full snapshots hurt |
| **OQ-OVR-2** project licence | **1a** ✔ *decided* | Blocks nothing technically; blocks every external contribution and the public-repo story |
| **OQ-MODEL-1** expression objectives in 1b? | 1b | Decides whether the AST parser and SymPy derivation are in scope — a material slice of W5 |
| **OQ-MODEL-5** credibility standard | 1b | Needed to implement `credibility_weighted` grouping |
| **OQ-OVR-5** notebook escape hatch | 1b | Affects whether a client library is in scope |

The four marked **1a** are the ones that actually gate the start of work. The other 39
can wait for the phase that needs them (§10).

---

### Outstanding work — consolidated

Everything still open before Phase 1a can start, in one place. Tracks A–C above explain
*why*; this is the list. The **Gates** column shows which half of Phase 1 each blocks.

| # | Task | Kind | Owner | Blocks |
|---|---|---|---|---|
| ~~1~~ | ~~**OQ-OVR-2**~~ ✔ — project licence | decision | maintainer | **1a** — public contribution, not code |
| **2** | **OQ-OVR-5** — notebook escape hatch | decision | maintainer | **1b** — client library scope |
| ~~3~~ | ~~**OQ-PLAT-1**~~ ✔ — Celery vs a transactional Postgres queue | decision | maintainer | **1a** — W2, first sprint |
| ~~4~~ | ~~**OQ-DATA-1**~~ ✔ — where large-loss capping lives | decision | maintainer | **1a** — it *is* the 1a/1b boundary; a contract change if deferred |
| ~~5~~ | ~~**OQ-DATA-2**~~ ✔ — append ingestion vs full snapshots | decision | maintainer | **1a** — W4, only if the first dataset is large |
| **6** | **OQ-MODEL-1** — do expression objectives ship in Phase 1b? | decision | maintainer | **1b** — W5 scope, materially |
| **7** | **OQ-MODEL-5** — credibility standard | decision | maintainer | **1b** — W5 grouping implementation |
| ~~8~~ | ~~**S3** — LightGBM `init_score`~~ ✔ **done** | spike | — | Closed. Found a real asymmetry → FR-MODEL-72 |
| ~~9~~ | ~~**Phase 1 split** — accept or reject 1a/1b~~ ✔ **ACCEPTED 2026-08-14** | decision | maintainer | Now the plan; `CLAUDE.md` §9 updated |

**Not blocking Phase 1, but do not lose them:**

| Task | Kind | Due |
|---|---|---|
| 5 Phase-2 decisions (OQ-RATE-3/4/6, OQ-MODEL-3, OQ-PLAT-3) | decisions | Before Phase 2 — OQ-RATE-2 now decided |
| Sustained-load test at 200 rps (S2 measured per-request only) | test | Phase 2 W11 |
| 7 Phase-3 decisions · 12 Phase-4 decisions · 12 any-time | decisions | Per gate (§10) |
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

| # | Workstream | Depends on | Notes |
|---|---|---|---|
| ~~**W1**~~ ✔ | Repo foundations: `uv` workspace, `model-schema`, `pricing-core` skeleton, CI with import-linter contract (ADR-0001), docker compose | — | **Closed 2026-08-14** — see the status table below |
| **W2** | Platform core: jobs, blobs, settings, OIDC auth, health, tracing | W1 | ~35 of 60 `PLAT` requirements |
| **W3** | Governance write path: audit log + hash chain, RBAC enforcement, approval state machine | W1, W2 | §5 — skeleton only, no governance UI |
| **W4** | Data: sources, ingestion, preparation recipes, parquet, profiling, the four validation layers + built-in rule catalogue, reference tables | W2, W3 | All 49 `DATA` requirements |
| **W6a** | Frontend: app shell, dataset views, **validation report view** | W4 | `01` §5.3 puts its interaction requirement here — "why can I not fit a model on this?" answerable in one screen |

#### Phase 1a status

| WS | Scope | Status |
|---|---|---|
| **W1** | Repo foundations | ✔ **closed 2026-08-14** |
| ~~**W2**~~ ✔ | Platform core — jobs, blobs, settings, auth, health, tracing | ✔ **closed 2026-08-14** — see the closure record below |
| ~~**W3**~~ ✔ | Governance write path — audit log, RBAC, approval state machine | ✔ **closed 2026-08-14** — see the closure record below |
| **W4** | Data — ingestion, preparation, validation, profiling, reference data | next |
| **W6a** | Frontend — app shell, dataset views, validation report view | with W4 |

Closing a workstream follows `CLAUDE.md` §13 and the `close-workstream` skill: every
deliverable re-verified against its row above, the gate run locally, each new check proven
to fail on broken input, NFRs measured against their budget, and what was *not* delivered
stated explicitly. A closure record without those is an assertion, not evidence.

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
| FR-PLAT-40 — Prometheus `/metrics` | not started | **W3 or an observability slice** |
| FR-PLAT-14 — 13-month job retention | *partial*: the window is a declared setting with the 13-month floor enforced, but no sweeper purges beyond it. Nothing deletes job history today, so the floor holds by default rather than by design | W3 |
| FR-PLAT-1 last clause — local development identity provider in the compose stack | not delivered; dev-header identity covers local work and is refused outside `local`/`dev` | deployment |
| `00` §5.4 `If-Match` optimistic concurrency | **not applicable to W2** — no W2 resource is a versioned entity. `CONFLICT_STALE_WRITE` is not yet in the error registry | first workstream with versioned artifacts (**W4**) |
| `00` §5.4 `Idempotency-Key` header | job submission is idempotent at the service layer (FR-PLAT-12), but no HTTP endpoint creates a Job — by design, since Jobs are created by domain actions | **W4** |
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

### Phase 1b — Modelling Workbench

**Goal:** factors, bandings, groupings, GLM and GBM fitting, diagnostics, transparency
artifacts, model versioning.

**Demo-able outcome:** the actuary bands and groups factors, fits a GLM and an XGBoost
model, compares them, and gets one approved — **`wf-01` end to end**.

| # | Workstream | Depends on | Notes |
|---|---|---|---|
| **W5** | Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective templates | W4 (1a) | All 78 `MODEL` requirements — the largest single workstream in the project |
| **W6b** | Frontend: **factor workbench**, model detail, diagnostics | W5 | `02` §5.3's interaction requirement — an edit's consequence visible before saving |
| **W7** | freMTPL2 demo seed | W5, W6b | `07` FR-PLAT-37 — one command to a working system |

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
| **W2** | Platform core: jobs, blobs, settings, OIDC auth, health, tracing | W1 | ~35 of 60 `PLAT` requirements |
| **W3** | Governance write path: audit log + hash chain, RBAC enforcement, approval state machine | W1, W2 | §5 — skeleton only, no governance UI |
| **W4** | Data: sources, ingestion, preparation recipes, parquet, profiling, the four validation layers + built-in rule catalogue, reference tables | W2, W3 | All 49 `DATA` requirements |
| **W5** | Modelling: factors, bandings, groupings, glum GLM, XGBoost, diagnostics, transparency artifacts, custom objective templates | W4 | All 78 `MODEL` requirements — the largest single workstream |
| **W6** | Frontend: app shell, dataset views, **validation report view**, **factor workbench**, model detail, diagnostics | W4, W5 | The two bolded views are where `01` §5.3 and `02` §5.3 place their interaction requirements |
| **W7** | freMTPL2 demo seed | W4, W5, W6 | `07` FR-PLAT-37 — one command to a working system |

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
| Custom objectives are a research task, not a coding task | Answer OQ-MODEL-1; if templates-only, Phase 1 shrinks materially |
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
| **W14** | Deployment: environments, atomic switchover, rollback, shadow | FR-RATE-50..55; `07` FR-PLAT-28..31 |
| **W15** | Frontend: **DAG designer (Vue Flow)**, rate table editor, quote sandbox + ladder waterfall, dislocation views | The DAG designer is the single largest frontend effort in the project |

### Requirement coverage

≈ **67 `RATE` + ~25 remaining `PLAT`** requirements.

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
| ~~**Before Phase 1a**~~ ✔ **all decided 2026-08-14** | ~~OQ-OVR-2~~, ~~OQ-PLAT-1~~, ~~OQ-DATA-1~~, ~~OQ-DATA-2~~ | 4 (0 open) |
| **Before Phase 1b** | OQ-OVR-5, OQ-MODEL-1, OQ-MODEL-5 | 3 |
| **Before Phase 2** | ~~OQ-RATE-1~~ ✔, ~~OQ-RATE-2~~ ✔ *both decided by spike*, OQ-RATE-3, OQ-RATE-4, OQ-RATE-6, OQ-MODEL-3, OQ-PLAT-3 | 7 (5 open) |
| **Before Phase 3** | OQ-GOV-1..6, OQ-OVR-1, OQ-MODEL-7 | 8 |
| **Before Phase 4** | OQ-OPT-1..6, OQ-MON-1..5, OQ-DATA-4 | 12 |
| **Deferred / any time** | OQ-OVR-3, OQ-OVR-4, ~~OQ-DATA-3~~ ✔ *decided 2026-08-14*, OQ-DATA-5, OQ-DATA-6, OQ-MODEL-2, OQ-MODEL-4, OQ-MODEL-6, OQ-RATE-5, OQ-PLAT-2, OQ-PLAT-4, OQ-PLAT-5 | 12 |

**OQ-RATE-1 was the one question able to invalidate an accepted ADR. It has been answered**
— by a spike, not an opinion — and ADR-0004 survived
([`research/track-a-findings.md`](research/track-a-findings.md) F1).

**OQ-RATE-2 has also now been answered** by spike S2 — `exact` mode costs ~2 % of the
budget, so OQ-MODEL-3 remains a design choice rather than being decided by force.

**Every question that could only be answered with code has been.** What remains is
judgement, not measurement.

---

## 11. Sizing

Effort is expressed relative to the requirement surface and the number of independently
parallelisable workstreams. **No dates, because team size is unknown.**

| Phase | Requirement share | Parallelisable streams | Relative size | Shape |
|---|---|---|---|---|
| 0 — Specification | — | — | done | — |
| On-ramp (§3) | — | 3 | XS | ~~Research~~ ✔ · ~~3 spikes~~ ✔ · **7 decisions outstanding** |
| **1a — Data Workbench** | ~26 % | 3 after W1 | **L** | W1–W4 + dataset views; ends at a `validated` dataset |
| **1b — Modelling Workbench** | ~21 % | 2 | **L** | W5–W7; ends at `wf-01` end to end |
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
