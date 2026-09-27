---
id: RS-708
family: research
kind: audit
title: WK-660 mid-workstream scope findings —
status: closed                  # draft → active → closed | retired (§1.2a)
created: 2026-08-14
owner: auditor
corrected_by: []
relates: []                     # ids only — the FR-/ADR-/RFC- target a spike's `closed` cites
was: docs/audit/closure-records.md
---

### WK-660 mid-workstream scope findings — 2026-08-14

**WK-660 is roughly half delivered, and the requirement-coverage number said otherwise.**
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
orchestration rather than computation — FR-41 ("persisted with the Dataset Version"),
FR-49 ("every non-pass outcome persists"), FR-60/62 ("runs automatically after
successful ingestion", "persisted as an artifact"), FR-50/51 (rule sets versioned and
governed). The functions those requirements need exist and are correct. Nothing stores
their output, nothing runs them after an ingestion, and nothing serves them over HTTP.

Concretely, still to build: `ValidationReport`, `Profile`, `ValidationRule` and
`ValidationRuleSet` persistence with their migrations; the acknowledgement record
(FR-46/47); validation and profiling as Jobs triggered by ingestion; and the §5.1
REST surface. NFR-471 and FR-54 wait on that layer, and NFR-473 waits on the
`sql` check, which does not exist.

**The same check found a gap in a closed workstream.** `scope-audit.py PLAT --endpoints`
reports 11 of 17 `PLAT` endpoints published: the blob upload-URL and download endpoints,
environments CRUD, and `/metrics` are declared in `07` §5.1 and were never built. WK-658's
closure record did not mention them, because nothing at the time compared the interface
table to the contract. They are reassigned to WK-660 (blobs, `/metrics`) and WK-674
(environments), and the WK-658 closure record is amended below rather than rewritten — a
closure record states what was known when it was written.

#### Position after the REST and handler slices

| Check | Then | Now |
|---|---|---|
| `scope-audit DATA` requirements | 44 / 50 | **48 / 50** |
| `scope-audit DATA --endpoints` | 0 / 28 | **28 / 28** |
| `scope-audit DATA --catalogue VR` | not measured | **38 / 38** |

Two of those moved because work landed. The third was a **third finding** of the same kind as the first two: a requirement can
summarise a catalogue it does not enumerate. FR-45 says "validation covers four
layers", which one test evidences honestly — while §4.4's catalogue of 38 named rules
behind it stood at 12. **Since closed**: all 38 are implemented, and writing the tests
found two defects in rules that already existed — `column_presence` passed when no columns
were declared, and `development_maturity` could never pass, because it measures against
the data's own latest period and the most recent rows are always immature.

`--catalogue PREFIX` was added to `scope-audit.py` so the number is re-derivable rather
than a one-off count, and it generalises: any spec declaring a catalogue of named ids can
be checked the same way.

**WK-660 was therefore not closeable at the time.** ~~What remains, with owners~~ — **superseded by the closure record above, 2026-08-15**; every row below was either delivered or given a verdict there:

| Item | Verdict |
|---|---|
| 26 of 38 built-in catalogue rules (§4.4) | ~~not started~~ ✔ **delivered 2026-08-15** — all 38 implemented and tested, each with a case where it fires and one where it does not |
| FR-54 streaming over parquet row groups | **not delivered** — the distributional half is done; the streaming half needs a real 10 M-row dataset to be designed against, so it is reassigned to **WK-665** alongside the freMTPL2 seed |
| NFR-465, NFR-466 throughput | **measured, not tested** — `scripts/bench-data.py` at 2 M × 80, extrapolated to 10 M: parquet ingest+prepare 5.2 s / 900 s, CSV 29.6 s / 1800 s, validation 0.3 s / 600 s, structural alone 0.1 s / 120 s. A timing assertion on a shared runner fails for reasons unrelated to the code |
| `GET /metrics` (FR-443, reassigned from WK-658) | **not started** — needs a Prometheus client dependency and a `07` §8 entry, and several required series (scoring latency, cache hit rate) belong to later phases |
| `POST /sources/{id}/preview` for `object_store` / `sql` sources | **partial** — implemented for uploaded bytes, the flow FR-29 is written around; the other source kinds need connectors WK-660 has not built |

What *is* done and was not before: the `01` REST surface end to end, validation and
profiling persistence, the four `dataset.*` job handlers, preparation recipes applied
during ingestion, the sandboxed `sql` check, and **Phase 1a's exit criterion as a passing
test** — `test_the_failure_loop_then_validated` ingests a file with a negative exposure,
watches promotion refused, fixes the data rather than the verdict, and promotes.

**WK-657 re-audited under §13, 2026-08-14.** WK-657 closed before the standard required a scope
derivation, so it was audited again from the specifications rather than from its own
record.

**Scope**, derived from what WK-657's named deliverables are required *by* — WK-657 produced
foundations, not a spec section, so its scope is the set of system-level requirements its
deliverables implement:

| Deliverable | Requirement | Verdict |
|---|---|---|
| `model-schema` | FR-4 artifact immutability | ✔ as types (`frozen`, `extra="forbid"`); persistence in WK-659 |
| `model-schema` | FR-9 shapes defined once | ✔ package in WK-657, generation and drift check in WK-658 (#25) |
| `model-schema` | FR-10 money discipline | ✔ `MoneyMinor`, `DecimalStr`, and the docs-audit check |
| `pricing-core` | FR-8 computation callable without the backend | ✔ enforced by the ADR-703 contract |
| compose stack | NFR-462 full stack local, no cloud | ✔ services and health checks declared |
| compose stack | NFR-529 usable state in < 5 min | ✔ **measured 21 s**; deliberately not a test |

**6 requirements in scope; 5 carry test evidence, all 6 carry evidence of some kind.**

**The re-audit found a gap in the standard, not in WK-657.** `scope-audit.py` sees
`@pytest.mark.req` markers and nothing else, so a requirement enforced by an import-linter
contract, a database privilege or a recorded measurement reads as unevidenced. WK-657 is the
extreme case — its deliverable *is* enforcement machinery — and the audit reported half its
scope missing while the enforcement worked perfectly in CI.

Rather than weaken the standard, the enforcement was made visible:
`tests/test_repository_invariants.py` links FR-8 to the import-linter run, FR-9 to
the contract configuration being non-empty, NFR-462 to the compose declaration, and
FR-10 to the docs-audit money check. A repository-level `tests/` root was added to
`testpaths`, which both traceability scripts read.

NFR-529 keeps its measurement rather than gaining a test: starting containers on every
push to assert a number that varies with the runner would be a slow check that fails for
reasons unrelated to the code.

*Nothing in WK-657's original closure was found to be wrong.* The record below stands; what was
missing was the scope derivation and the visibility of enforcement as evidence.

**WK-657 closure evidence** (re-verified 2026-08-14, and again on the rebuilt instance the same
day — `uv` had to be reinstalled durably, and the gate was re-run from a clean sync):

| Deliverable | Evidence |
|---|---|
| `uv` workspace | `pyproject.toml` + committed `uv.lock`; `uv sync --all-packages --dev` clean |
| `model-schema` | 4 modules; `MoneyMinor` strict, `DecimalStr` string-pinned, envelope frozen |
| `pricing-core` skeleton | 3 modules; `ProgressCallback` protocol, decimal money helpers |
| import-linter (ADR-703) | **3 contracts kept, 0 broken** — and proven to fail on injected violations |
| CI | `docs.yml` + `python.yml`, path-filtered per component, both green |
| docker compose | **21 s cold start** against NFR-529's 300 s; all three services healthy |
| Quality gates | ruff clean · mypy clean on 7 files · 21 tests · docs audit 14/14 |

**What WK-657 deliberately did *not* deliver.** It is *repo foundations*, so it landed the
**type-level** half of §5's retrofit list and the machinery that enforces it — not the
runtime half:

| §5 item | WK-657 | Lands in |
|---|---|---|
| Artifact immutability, versioning, `parent_id` | ✔ as types (`frozen=True`, `extra="forbid"`) | persistence in WK-659 |
| `model-schema` as single source of truth | ✔ as a package | ✔ **generation + CI drift check delivered in WK-658** (#25) |
| Decimal money discipline | ✔ as types + helpers | rating path in Phase 2 |
| The Job model | — only the `ProgressCallback` protocol | ✔ **delivered in WK-658** (#23) |
| Content-addressed blob store | — only the `BlobRef` type | ✔ **delivered in WK-658** (#24) — S3 + refcounts + conservative GC |
| `trace_id` propagation | — | **WK-658** |
| Append-only audit log in the caller's transaction | — | ✔ **sink delivered early in WK-658** (#23, DEP-537); RBAC and approvals remain WK-659 |
| RBAC checks in the backend | — authentication and workspace membership only (#28) | **WK-659** — roles, assignments and permission checks |

Stating this explicitly so nobody reads "WK-657 closed" as "the retrofit list is handled". It
is not; WK-657 made it *cheap*, which was its job.

**Coverage:** ≈ 99 of 375 module requirements (~26 %).

**Exit:** a freMTPL2 dataset version reaches `validated`, including at least one deliberate
round through the failure loop. The retrofit list (§5) is fully in place by the end of 1a —
that is the phase's other, quieter deliverable.

> **The second half was a gate, and it is met** *(plan review 2 accepted 2026-08-15;
> delivered the same day)*. **FR-40** and **FR-43** are in: ingestion refuses a
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

**WK-658 closure evidence** (2026-08-14). Closed under `CLAUDE.md` §13; the scope below was
re-derived from `07` §3 rather than from the build log, after an independent audit found
the earlier "not delivered" statement incomplete.

**Scope.** WK-658's named areas (`07` §3.1 auth, §3.2 jobs, §3.3 storage, §3.7 observability,
§3.8 configuration) plus FR-450/451 total **35** requirements — which is what the
roadmap's "~35 of 60" meant. FR-428, FR-429, FR-430, FR-431 belong to WK-674 and FR-439 to WK-665.

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

> **Amendment 2026-08-14, during WK-660.** `scope-audit.py PLAT --endpoints` — a check that
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
> Reassigned rather than reopened: the blob endpoints and `/metrics` to **WK-660**, which
> needs blob download URLs for parquet anyway; environments to **WK-674**, which owns
> `07` FR-428, FR-429, FR-430, FR-431. The record above stands as written — it states what was known
> when it was written, which is what a closure record is for.

**Enforcement proven, not assumed** (§13 rule 3). Each check was shown to fail on
deliberately broken input: the ADR-703 and DEP-3 import contracts (injected `import
fastapi` and `import app`); the contract drift check (both a changed model with a stale
contract and a hand-edited contract); `req-coverage` against a bogus requirement id in a
backend test; and the append-only audit table against `UPDATE`, `DELETE` and `TRUNCATE`.

**NFRs measured** (§13 rule 4):

| NFR | Budget | Measured |
|---|---|---|
| NFR-527 — submit to pickup | 5 s | **1.24 s max** over 6 runs (median 1.02 s) against the compose stack with worker and beat running. The ~1 s floor is the relay interval. |
| NFR-528 — progress interval | 5 s | **1.02 s max** gap between persisted updates over a 12 s run |
| NFR-532 — no secrets in logs or dumps | — | asserted per credential in `test_no_credential_survives_a_settings_dump` |

*Method note.* NFR-527 measures submit until the Job **leaves `queued`**. No job handler
exists yet — they arrive with WK-660 and WK-661 — so the worker dispatches and finds none. That
path is submit → running plus the dispatch check, making the figure an upper bound on the
requirement, not a proxy for it.

**Requirement coverage: 32 of 35 in-scope requirements carry test evidence (91 %).**

**What WK-658 did not deliver.** Stated explicitly, because "WK-658 closed" must not be read as
"`07` is done":

| Requirement | Status | Owner |
|---|---|---|
| FR-411 — scheduled Jobs, and FR-413's tick | not started; **unblocked 2026-08-23** — OQ-641 decided against Dagster, and the mechanism is specified as FR-413 | **Phase 4**, with the monitoring workstreams that need it (WK-687) |
| FR-423 — backups, PITR, tested restore | not started — an operational capability, not application code | **deployment, Phase 2** |
| FR-443 — Prometheus `/metrics` | ~~not started~~ ✔ **delivered by WK-660, 2026-08-15** — three of its five families; scoring latency and cache hit rate have nothing to report until WK-671 and are absent rather than zero | ~~WK-659 or an observability slice~~ **WK-660** |
| FR-410 — 13-month job retention | *partial*: the window is a declared setting with the 13-month floor enforced, but no sweeper purges beyond it. Nothing deletes job history today, so the floor holds by default rather than by design | WK-659 |
| FR-387 last clause — local development identity provider in the compose stack | not delivered; dev-header identity covers local work and is refused outside `local`/`dev` | deployment |
| `00` §5.4 `If-Match` optimistic concurrency | **not applicable to WK-658** — no WK-658 resource is a versioned entity. `CONFLICT_STALE_WRITE` is not yet in the error registry | ~~**WK-660**~~ → **WK-661** ✔ **delivered 2026-08-17**, with the code registered under `07`; see the model-lifecycle slice record |
| `00` §5.4 `Idempotency-Key` header | job submission is idempotent at the service layer (FR-404), but no HTTP endpoint creates a Job — by design, since Jobs are created by domain actions | ✔ **WK-660** — all four `202` endpoints |
| Out of WK-658 scope entirely | FR-424, FR-425, FR-426, FR-427 secrets backend, 28..31 environments (WK-674), 32..36 deployment, 37 demo seed (WK-665), 49 rate limiting, 50 webhooks | as noted |

Nine of the ten `PLAT` NFRs remain unmeasured beyond the three above; NFR-529 was
measured in WK-657 (21 s against 300 s).

**An audit finding worth recording.** The published contract described only success
shapes: a client generated from it was typed against FastAPI's default
`HTTPValidationError` — which the platform never emits — and had no type for the RFC 9457
problem it does. The drift check could not catch it, because the contract faithfully
described the code and both were wrong together. A generated artifact matching its source
is not the same as either being correct, and the fix (`app/api/responses.py`) is now
guarded by tests asserting the contract's error model directly.

**WK-659 closure evidence** (2026-08-14). Closed under `CLAUDE.md` §13, scope derived from
`06` §3 before any code was read.

**Scope.** WK-659's row reads *"Governance write path: audit log + hash chain, RBAC
enforcement, approval state machine"* with the qualifier *"§5 — skeleton only, no
governance UI"*. Mapped to the spec that is **23 requirements**: `06` §3.1 identity and
permissions (8), §3.4 audit log (7), the state-machine subset of §3.2 (FR-GOV-9, 11, 12,
13, 14, 15), and NFR-519 and NFR-525. **All 23 carry test evidence.**

| Deliverable (roadmap §6) | Evidence |
|---|---|
| Audit log + hash chain | Delivered in WK-658 under DEP-537; WK-659 adds the query, verify and export API (FR-371/372) |
| RBAC enforcement | 23 permissions, six built-in roles, scoped assignments, route-level checks, break-glass |
| Approval state machine | submit → decide → approved/rejected/changes_requested, withdrawal, per-workspace policy |

**Gate (local):** ruff clean · mypy --strict on 57 files · import-linter 3 kept / 0 broken ·
**318 tests** · contracts current · docs audit 14/14.

**NFRs measured** (§13 rule 5):

| NFR | Budget | Measured |
|---|---|---|
| NFR-518 — permission check overhead | 5 ms | **p95 1.74 ms**, median 1.36 ms over 200 checks — **but uncached** |
| NFR-519 — audit writes never fail silently | — | a rollback discards the change and its event together |
| NFR-525 — explicit negative tests in CI | — | asserted by name, not by count |

*NFR-518 is **partial**.* The requirement specifies the budget *"using a cached
effective-permission set invalidated on assignment changes"*. The budget is met without the
cache at this scale; the named mechanism does not exist, and will be needed when a
workspace has many assignments per principal. Recorded as met-on-measurement,
not-met-on-mechanism rather than as a pass.

**What WK-659 did not deliver.** WK-659 is the skeleton; `06` has 43 requirements and Phase 3
(WK-677–WK-682) owns the rest:

| Requirement | Status | Owner |
|---|---|---|
| FR-352 — Evidence Bundle completeness at submission | ~~not started; the evidence artifacts do not exist yet~~ **Delivered 2026-08-17 for two of its three clauses**, by WK-661's model-lifecycle slice — a WK-659-era verdict nobody struck, found 2026-08-22. `_require_evidence` (in `platform/modelling.py`, and the same shape in `metrics.py` and `objectives.py`) raises `EVIDENCE_INCOMPLETE` against the FR-364 union of `06` §3.3's floor and the workspace policy, and **fails closed on any evidence kind it cannot verify** — proved by `test_submission_without_the_policys_evidence_is_refused`. The change-summary clause is enforced in `platform/approvals.py`. **The third clause is not built:** "a completed checklist for that artifact type" is declared six times in `06` and `grep -rn checklist backend/src` returns nothing. Recorded as delivered-in-part rather than delivered, because the row would otherwise close a clause nothing implements. | ~~**WK-660/WK-661**, then Phase 3~~ **WK-661** ✔ for the Evidence Bundle and the change summary · **WK-677** for the checklist, which owns FR-351, FR-352, FR-353, FR-354, FR-355, FR-356, FR-357, FR-358, FR-359, FR-361, FR-363 |
| FR-358 — Approvals inbox with evidence inline | list and filter exist; *inline evidence* does not | **Phase 3, WK-678** |
| FR-359 — flags propagating into the approval surface | not started; the flags come from `01`/`02` | **Phase 3** |
| FR-361 — attestation | not started | **Phase 3** |
| FR-363 — required evidence per artifact type | not started; depends on FR-352 | **Phase 3** |
| FR-376, FR-377, FR-379, FR-380, FR-381, FR-382 — generated documentation and dossiers | not started | **Phase 3, WK-680** |
| FR-383, FR-384, FR-385 — change control across the platform | not started | **Phase 3** |
| NFR-520, NFR-521, NFR-522, NFR-523, NFR-524 | unmeasured; several depend on artifacts that do not exist | **Phase 3** |

*A marker was removed during this audit rather than kept.* A test had been marked
FR-358 while the closure record called the inbox deferred. The traceability record and
the closure record must not disagree, and the record was the honest one.

**Open questions.** OQ-633, OQ-634, OQ-635, OQ-636, OQ-637, OQ-638 are gated "Before Phase 3" and none blocked this
skeleton — checked before starting, not assumed. OQ-634 (are platform roles authoritative,
or IdP groups?) looked like a blocker for RBAC and is not: FR-344 and FR-345 already
make roles and scoped assignments platform objects, and FR-390 already specifies
group-to-role mapping as configuration. Both answers to OQ-634 need the model WK-659 built;
only the *source of assignments* is undecided.

*OQ-633's first half is settled by implementation.* WK-658 chained per workspace, which is
what the question's own recommendation says. The remaining half — optional external
anchoring of the chain head — is untouched and stays open for Phase 3.
