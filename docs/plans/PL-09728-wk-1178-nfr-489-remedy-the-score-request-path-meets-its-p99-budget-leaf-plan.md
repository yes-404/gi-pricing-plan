---
id: PL-9728
family: plan
kind: leaf
title: WK-1178 — NFR-489 remedy, the /score request path meets its p99 budget at 25 to 200 rps (NFR-489, NFR-454, NFR-497, FR-243, FR-259): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-04
owner: planner
tree: 47d770e8fcbd2410fa101019ed8cf3aae69a1baa
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1411, SL-1259, SL-1409, PL-1408, PL-1371, RL-921, RL-882, RL-1379, RL-1263, LG-1405]
---

# PL 9728 (working id) — WK-1178: the NFR-489 remedy, the `/score` request path meets its p99 budget, leaf plan

Filed under working id 9728 (this plan) and slice working id 9727 (its `SL-` row under WK-1178 in
[`../roadmap.md`](../roadmap.md), `draft`), both reserved by the lead. The lead mints both at the merge
turn. The finding this plan remedies is **FD-1411** (HIGH; filed as working id 9729 and minted at #1111,
`main` `47d770e8`).

**Ordered by** the maintainer's (by delegation) entry in `to-lead.md` headed *"2026-10-04 19:18:54 BST — NFR-489 ON MAIN
(c08a48e5, uncontended): the FD is FILED NOW at severity HIGH, not in the batch; its remedy is pulled
forward ahead of other WK-1178 items; the no-GBM anomaly is re-measured"*, action 2: *"a leaf plan for
"the bundle is resolved once per deployed version per worker, not per request" (or whatever the
measurement shows), planned NOW, read-only beside lane A. It is dispatched on lane B **immediately after
the FD-1356 fix**, ahead of the other WK-1178 items, under PL-1371's G2 priority."* **Amended by** the
entry headed *"2026-10-04 19:42:49 BST — NFR-489 re-run accepted (the no-GBM 1017 ms does not reproduce;
200–300 ms in-handler stalls in both arms; all six runs over budget): severity HIGH stands; the remedy
plan MUST attribute the stalls before choosing a fix"*, whose PL 9728 bullets this plan implements:
Task 0 attributes; the fix is chosen from Task 0's evidence; a timing-free CI regression guard; an
unreachable budget is a decision point, not a silent re-baseline.

Planned read-only: no code was run, no benchmark, no pytest. Every figure below is copied from a named
record; every code fact was read at `origin/main` `4eb1364428a2861fbc8014957e89924f631dd1ff` and is
re-pinned to `47d770e8fcbd2410fa101019ed8cf3aae69a1baa` (2026-10-05): `git diff --name-only 4eb13644
47d770e8 --` over activation need 4's eight source files plus `backend/src/app/config.py` and
`scripts/demo.py` prints nothing, so every path:line below holds at `47d770e8`. The delta between the two
trees is FD-1411's record and its register row (#1111).

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or
> executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking. The executor also binds `systematic-debugging` (Task 0: the cause is found before a fix is
> chosen), `test-driven-development` (every behaviour change is seen red, by its cause, first),
> `python-test` (the `req` marker), `fastapi-service` (Task 3), `dev-commands` (the benchmark, the
> scratch database, the alembic DSN, the two-half gate) and `git-hygiene`. The measurement steps may be
> delegated to the `performance-engineer` agent, which returns evidence only. Read
> [`README.md`](README.md)'s unchecked conventions before the first step. The executor is spawned from
> `.claude/roles/executor.md`.

## Goal

`POST /api/v1/score` meets NFR-489 on one replica — p99 under 50 ms with one `exact` GBM call and
under 15 ms without — at 25, 50, 100 and 200 rps offered, measured with `scripts/bench-rating.py
--http`. The fix is chosen from a per-phase attribution of the served request (Task 0), not from the
side measurement that first suggested it. This discharges the remedy half of FD-1411
(HIGH); the NFR-489 verdict on the exit tree stays SL-1259's.

**Architecture:** two stages with a ruling between them. Stage 1 (Task 0) instruments a scratch copy
of `main` and attributes every per-request millisecond and every stall of 100 ms or more to a phase.
The decision-maker then rules DP-1 to DP-4 from that record (DP-6 is already ruled (b), §"Decision
points"). Stage 2 (Tasks 1 to 6) corrects the
harness, adds timing-free CI guards red first, applies the ruled fix in the layer that owns each cost,
and measures the acceptance sweep alone on the box.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2 async (asyncpg), PostgreSQL 16, uvicorn, pytest,
`scripts/bench-rating.py`. Stdlib instruments only in Task 0 (`asyncio` debug mode, `gc.callbacks`,
SQLAlchemy pool events); `py-spy` only as an un-installed `uvx` scratch tool, never a dependency.

**Spec:** [`03-rating-engine.md`](../specs/03-rating-engine.md) §9 (NFR-489, NFR-497), §3 (FR-243,
FR-259, FR-268); [`00-overview.md`](../specs/00-overview.md) §9 (NFR-454);
[`07-platform.md`](../specs/07-platform.md) (FR-452, read only).

## Status

`draft`. DP-1 to DP-4 cannot be ruled before Task 0 runs, by the maintainer's (by delegation) own order ("the fix is
chosen FROM Task 0's evidence"). The plan therefore activates in two steps: Task 0 is dispatched on the
activation needs below and commits nothing but its ledger; Tasks 1 to 6 start only after the
decision-maker's ruling on DP-1 to DP-4 is merged. DP-6 is ruled (b) by the maintainer, by delegation
(its `Resolved by` cell). DP-5 goes to the maintainer only if it fires.

### Activation needs, in order

1. **Lane B: dispatched after the FD-1356 fix (SL-1409, PL-1408) merges**, ahead of the other WK-1178
   items, under `PL-1371`'s G2 priority (the maintainer's (by delegation) entry above, action 2).
   **Lane B's order since then** (pre-mint, 2026-10-05): the HIGH G2-blocking fixes go first. The
   FD 9707 fix (working id) goes before this plan (`to-lead.md` entry headed *"2026-10-05 13:11:05 BST — FD 9707 (B3, as_at lookup ignores effective dating): HIGH, provisional on the upstream-filter check; its fix goes FIRST in lane B after SL-1409"*, item 3), and the FR-240 family
   fix (PL 9649, working id) goes before this plan when it takes lane B (entry headed *"2026-10-05 14:28:35 BST — PL 9649 / SL 9647 (the FR-240 fix, #1152 @dc13400e): DP-5 OK; DP-6 scoped; lane placement"*). The dispatch record names the order that holds at dispatch.
2. **FD-1411 minted** — met: #1111 merged it at `47d770e8`; the ledger and the ruling cite FD-1411.
3. **An exclusive measurement window** under `RL-1263` ("a measurement runs alone"): no gate, no
   `migrate --verify`, no other benchmark on the box during Task 0's runs or Task 4's sweep. The
   executor records `pgrep -c pytest` and `uptime` at the start and end of every pass. "No other
   work" includes `gate-runner`, `performance-engineer` runs other than this slice's own, and
   `ci-watcher` agents polling from this box. Even uncontended, the box is the shared VM, so every
   figure is diagnostic under G4 (Acceptance 2).
4. **Re-read at dispatch** (`docs/plans/README.md` convention 4): `git diff --name-only
   47d770e8 origin/main -- backend/src/app/api/score.py backend/src/app/api/deps.py
   backend/src/app/api/authz.py backend/src/app/auth/service.py backend/src/app/db/session.py
   backend/src/app/main.py backend/src/app/platform/bundle_slot.py scripts/bench-rating.py`. Any
   non-empty output: re-derive §"Where the time goes" for those files before Task 0.
5. **Before Task 1 only:** the decision-maker's ruling on DP-1 to DP-4, merged; the lead's go. (DP-6 is
   ruled (b); its `Resolved by` cell.)

## Acceptance Standard

Each item is checked by a command run from the repository root on the slice's head. "Red first" means
the named test ran and failed **for the stated cause** before the code that turns it green
([`README.md`](README.md) rule 2); each red is recorded in the ledger with its printed failure line.

1. **Attribution recorded (Task 0).** The ledger carries Task 0's phase table (p50, p99, max per
   phase, both arms, 25 and 50 rps, three runs each), Step 4's sampling profile (its top frames by
   self time, or the printed reason `py-spy` could not run), and a list of every event of 100 ms or more with
   the phase or mechanism it was attributed to, or "unattributed" with the instruments that saw
   nothing. **The exit demo's `/score` path is a measured path too:** the same table for Task 0
   Step 3b's default-live arm, and its one-line answer on whether it does the same per-request work
   as the `bench-rating.py` path. The DP ruling cites this table.
2. **NFR-489, the untraced arms, full path, uncontended.** Predicate, verbatim from
   [`03-rating-engine.md`](../specs/03-rating-engine.md) NFR-489: *"Real-time scoring p99 < 50 ms
   server-side at 200 rps per replica for a ~200-step motor structure with one `exact` GBM call
   (NFR-454). Without a GBM call, p99 < 15 ms."* Command, on the slice's head, one rate per
   invocation, **three invocations per rate** at 25, 50, 100 and 200:
   `GIP_TEST_DATABASE_URL=<scratch DSN> timeout 1500 uv run python scripts/bench-rating.py --http --rates <R> --port 8000`
   (plus `--workers <N>` only under DP-3 (b)). **In budget** (the diagnostic reading, not a verdict):
   in **every** one of the 12 invocations, both arms' HTTP rung prints p99 under its budget (50 ms
   with GBM, 15 ms without), issued rps equals offered rps (no void rung), and errors are 0. DP-6 is
   ruled (b), so the default-live (exit-demo path) variant of each arm is measured in the same
   invocations against that arm's budget.
   **Untraced only (OQ 9777, working id, decided (a)).** `to-lead.md` entry headed
   *"2026-10-05 10:47:03 BST — OQ 9777 (#1048) DECIDED (a); the combined mint order ACCEPTED; pairing coupled records in one mint PR ACCEPTED (max 3 records per PR)"*: *"NFR-489's p99 ceiling (< 50 ms with one GBM call, < 15 ms without) governs UNTRACED real-time requests. A traced request (a caller-requested FR-258 inline trace) is bounded by NFR-490 instead (tracing adds ≤ 20 % to scoring latency)."* Its consequence for this plan, verbatim: *"Acceptance 2 measures the untraced default-live arm against NFR-489; any traced arm is checked against NFR-490's ratio."* Every arm
   above is untraced: the HTTP sweep's body is `_ctx()` (`scripts/bench-rating.py:1084`), whose
   `QuoteContextOptions` sets only `rating_version_ref` (`:347`), and `trace` defaults to `False`
   (`packages/model-schema/src/model_schema/scoring.py:93`). This slice adds no traced arm; a traced
   arm is NFR-490's, and PL 9776's (working id, #1051; §"Scope"). The ledger records, per invocation: start and end time (UTC
   and BST), `uptime` load at both ends, `pgrep -c pytest`, and the full rung lines.
   **G4's shared-VM caveat binds this item.** `docs/roadmap.md` §G4, amended 2026-09-29 by the
   maintainer for NFR-489 among others: *"These verdicts are **measured, diagnostic** on the shared VM;
   the verdict is **carried**, owner the maintainer, discharge event **a dedicated host available**.
   No near-bound pass or fail is claimed from the shared VM."* This sweep runs on the shared VM
   (e2-standard-8). Its result is therefore reported as **measured, diagnostic**: an in-budget table
   is the slice's acceptance evidence that the remedy worked, not a PASS of NFR-489. The NFR-489
   verdict stays carried per G4 and is SL-1259's on the exit tree. A table over budget is reported
   as measured and goes to the lead (Task 4 Step 3); if the cause is the machine and not the code,
   that is DP-5.
3. **Component half unchanged.** The same invocations' component lines (`score_one` alone) still print
   PASS for both arms against 50 ms and 15 ms. A p99 that moves by more than run-to-run noise (the
   spread of the three runs) is reported, not explained away.
4. **CI regression guard, timing-free (Task 2).** `uv run pytest -q
   backend/tests/test_score_request_cost.py` passes, and each of its tests was seen red on `main`'s
   code by its stated cause: the per-request statement and checkout counts exceed the ruled bound
   (DP-1), and, under any new cache DP-2 admits, the invalidation tests listed in Task 2.
5. **Existing guards still pass:** `test_a_repeat_request_does_not_re_read_the_blob_store`
   (`backend/tests/test_score.py:689`), `test_an_already_served_ref_survives_metadata_storage_failing`
   (`:627`), the FR-259 sampling tests (`:775` to `:996`), and the default-live tests (`:1379` to
   `:1541`), unchanged.
6. **The harness says what it measures (Task 1).** `scripts/bench-rating.py --http` prints the
   `_fetch_bundle` miss figure under a label that says "miss", and a hit figure from a shared slot
   beside it; its `_measure_fetch` docstring no longer claims every request pays the miss.
7. **The two-half gate** (`CLAUDE.md` §11) passes on the head, through the gate-runner, outside the
   measurement window.
8. **Write set:** `git diff --stat origin/main...HEAD` lists only §"Write set" paths; the ledger
   records it.
9. **The exit demo's `/score` call (DP-6).** Under DP-6 (a): `uv run pytest -q
   backend/tests/test_demo_command.py` passes, and Task 6's test was seen red by its stated cause.
   Under DP-6 (b) or (c): the ledger quotes the ruling and the Hand-off item 4 line, naming the
   owner of the scripted journey's `/score` step. Under DP-6 (a) or (b), Acceptance 2 includes the
   default-live arm.

## Global Constraints

- **Money and maths are untouched**: `ScoringResult` is byte-identical for the bench quote before
  and after (Task 3 Step 5). This compares this slice's head with its own base only. It pins no
  spelling: FD-1333 and FD-1337 will change how decimals serialise, and a later fix for them is not
  bound by this comparison.
- **RL-921 stands unless ruled otherwise**: no ref is served from the `ArtifactRef → content_hash`
  memo without a metadata read on the happy path (`bundle_slot.py`, the "Corrected 2026-08-30" and
  "Corrected 2026-10-04 (RL-1379)" paragraphs).
- **RL-882 clause 4 stands**: the slot gains no refresh, poll, pub/sub or environment pointer; those
  are WK-674's (SL-1259 for FR-268's pre-warm).
- **NFR-497's degraded read is preserved** (`_compiled_for`'s `except Exception` branch).
- **FR-259's sampling is preserved**: 1 % default, 100 % of declines and errors, off the request
  path.
- **The handler stays `async def`** (`score.py:16-19`; `BundleSlot` is unsynchronised).
- **No new runtime dependency.** A tooling dependency is a `skills-map.md` change (`CLAUDE.md` §10)
  and is out of scope; `py-spy` runs through `uvx` in scratch only.
- **A measurement runs alone** (`RL-1263`).
- **No spec text unless a ruling carries it verbatim** (DP-3 (b), DP-5).

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `03` §9 | NFR-489 | the remedy, measured at 25, 50, 100, 200 rps (Acceptance 2), diagnostic on the shared VM per G4; the verdict is carried per G4 and on the exit tree stays SL-1259's | none (an NFR is measured, not unit-tested) |
| `00` §9 | NFR-454 | the platform-level twin of NFR-489; held by the same measurement | none |
| `03` §9 | NFR-497 | preserved: the degraded read still serves a held bundle (Acceptance 5) | existing `:627` |
| `03` §3 | FR-243 | preserved: `CompiledBundle` is held per worker and never serialised | existing |
| `03` §3 | FR-259 | preserved: sampling rate and the off-path write (Acceptance 5) | existing `:775`–`:996` |
| `03` §3 | FR-268 | **not built**: pre-warm and atomic switchover stay SL-1259's | none |
| `03` §9 | NFR-490 | **not in scope**: trace overhead is PL 9776's (working id, #1051) | none |

### Where the time goes today — read, not measured

The bench caller is a Service Account API key scoped to `uat` (`scripts/bench-rating.py` `_seed`), so
`caller.environment` is set and every branch below runs. FastAPI resolves `require_caller` once per
request (dependency caching), so the counts are per request.

| Step | Path:line at `4eb13644` = `47d770e8` | Pool checkouts | Statements | Notes |
|---|---|---|---|---|
| Authenticate the API key | `backend/src/app/api/deps.py:238-239` (`unit_of_work`) → `backend/src/app/auth/service.py:175` (SELECT key by prefix), `:186` (`session.get` ServiceAccount), `:226` (`key.last_used_at = now`, flush) | 1 | 3 + COMMIT | **a write on every request**, to one `api_keys` row shared by every request on that key |
| Permission check | `backend/src/app/api/authz.py:62` (`database.session`) → `backend/src/app/platform/rbac.py:142` `effective_permissions`, SELECT at `:177` | 1 | 1 | runs even though the key's own `permissions` carry `score:execute` |
| Live Deployment | `backend/src/app/api/score.py:186-201` (`_serving_ref`) | 1 | 1 | `LG-1405` Task 7: 0 to 3.8 ms at p50, not resolved from noise at p99 |
| Version row | `score.py:235-237` (`_fetch_bundle` → `rating_versions_service.resolve_rating_version_ref`) | 1 | ≥ 1 | the authoritative re-read RL-921 requires |
| Bundle | `score.py:250-254`: `slot.get(content_hash)` hit, `slot.put` memo | 0 | 0 | **steady state is a hit**: `_seed` writes `bundle.content_hash` into `row.bundle`, `load_bundle` copies it to `CompiledBundle.content_hash` (`packages/pricing-core/src/pricing_core/rating/runtime.py:673`), the slot is built once per process (`backend/src/app/main.py:182`, capacity 1, `backend/src/app/config.py:186`) and each arm has its own server. Guarded by `test_score.py:689` |
| Evaluate | `score.py:375` `score_one` | 0 | 0 | component p99 11.3 ms with GBM, 7.8 ms without (baseline record); CPU on the event loop |
| Sampling | `score.py:384` → `:484-486` (`unit_of_work`, `settings_service.resolve`, `backend/src/app/platform/settings.py:302`) | 1 | 1 + COMMIT (+ 1 % a trace row and a Job) | the rate is re-read per request |
| Pool | `backend/src/app/db/session.py:40-48` | — | +1 per checkout | `pool_pre_ping=True` adds a round-trip on **every** checkout; no `pool_size`/`max_overflow`, so SQLAlchemy's 5 + 10 |

**Per request: 5 pool checkouts, 5 pre-pings, at least 7 statements, 2 commits, 1 UPDATE.** Serving
config (`scripts/bench-rating.py` `_serve`, `:729-758`): one `uvicorn` process, no `--workers`;
client open-loop, `httpx.Limits(max_connections=1024)`, timeout 60 s (`_drive`, `:776`).

**What the slot avoids today:** the blob row lookup, the object-store read, `Bundle.model_validate_json`
and `load_bundle`, on every request after the first per hash per process. **What it does not avoid:**
the version-row read (by design, RL-921), and every other step in the table, none of which is the
bundle's.

**The 78 ms "every request pays this" figure is the miss path, not the served path.** The baseline
record and FD-1411 quote `_fetch_bundle` alone at mean 78.0 ms (GBM) and 33.9 ms (no
GBM), labelled by the harness "every request pays this" (`scripts/bench-rating.py:1075`). The harness
builds **a fresh, empty `BundleSlot()` per call** (`:709-722`, its own comment: "a shared one would
turn every call after the first into a hit"), so each call pays the blob read, the parse and
`load_bundle`. Its docstring (`:678-688`) describes the pre-RL-921 code ("consults the slot only
*after* `_fetch_bundle` has returned"), which `score.py:250-254` no longer is. The maintainer's (by delegation) working
hypothesis ("the BundleSlot memo is not effective across requests on this path") is therefore **not
supported by reading**; Task 0 Step 3 confirms it empirically with a hit/miss counter. The ~200–300 ms
outliers in those `_fetch_bundle` blocks ran **in the harness process, not the server**, so they are
not evidence about the served path; the in-handler 320 ms tail (re-run 2, no GBM, handler p99 320.4 ms,
queue plus loopback 3.2 ms) is.

**What the evidence does support.** Handler time is about 35 to 52 ms in **both** arms (`LG-1405`
Task 7; the baseline re-run), while `score_one` alone is 5 to 11 ms, so roughly 25 to 40 ms per request
is GBM-independent. The table's five checkouts, five pings, seven statements and two commits are the
candidates. The harness's own ceiling model (`--speedup 2.10`, `Rung.implied_ceiling_rps`, `:564-575`)
puts a ~38 ms mean at about 55 rps, which matches the knee at 50 rps in both records. At 200 rps on
one process the mean must fall to about 10 ms, which `score_one`'s own 5 to 8 ms p50 leaves almost no
room for. That is why DP-3 exists.

### Task 0 at planning time

Not run (read-only planning). Task 0 is the first dispatched step.

### Write set, and its contention (`RL-1263`)

| Path | Change | Other work touching it | Consequence |
|---|---|---|---|
| `scripts/bench-rating.py` | edited: `_measure_fetch` (label, docstring, a shared-slot hit figure); `_serve` (`--workers` passthrough, DP-3 (b) only); `main` (the flag) | **PL 9776** (working id, #1051, F35 remedy, `draft`) names this file in its tech stack | different functions; the second to merge re-reads |
| `backend/src/app/db/session.py` | edited per DP-1 (b)/(d): `Database.__init__` pool arguments; added `request_session` only under DP-1 (a) | none found | none |
| `backend/src/app/config.py` | added: pool settings under DP-1 (d) | any slice adding a setting | registry-like: append |
| `backend/src/app/api/deps.py` | edited: `require_caller` (`:201-247`) under DP-1 (a) | none found | none |
| `backend/src/app/api/authz.py` | edited: `requires` (`:54-77`) under DP-1 (a)/(c) | none found | none |
| `backend/src/app/auth/service.py` | edited: `authenticate_api_key` (`:163`), the `last_used_at` write, under DP-1 (b) | none found | none |
| `backend/src/app/api/score.py` | edited: `score` (`:351-386`), `_serving_ref` (`:169-204`), `_fetch_bundle` (`:207-271`) session handling only, `_maybe_sample_trace` (`:464-530`) | **PL 9776** reads `score_compare`; **SL-1259** (WK-674 S5, `draft`) will edit the bundle path for FR-268; **FD-1333** (a `decimal` output served as a float) and **FD-1335** (the 200 response has no OpenAPI schema), both WK-1178-owned and unplanned, will edit this handler's response path and the contract | this slice precedes SL-1259; `score_compare` is not edited here. If a FD-1333 or FD-1335 fix is dispatched before or beside this slice, `score.py` is shared: the lead serialises the two under `RL-1263`, and the second to merge re-reads |
| `backend/src/app/main.py` | edited: `create_app` lifespan, `gc.freeze()` only under DP-4 (a) | none found | none |
| `backend/src/app/platform/bundle_slot.py` | **read only**, unless DP-2 (c) is ruled in | SL-1259 | a DP-2 (c) edit is a replan trigger to the lead |
| `backend/tests/test_score_request_cost.py` | added | none | none |
| `scripts/demo.py`, `backend/tests/test_demo_command.py` | edited under DP-6 (a) only (Task 6) | SL-1409 edited `scripts/demo.py` (merged); the plan for `PL-1371` §3.8 item 7 (unplanned) | under DP-6 (b)/(c) not touched |
| `backend/tests/test_score.py` | read only; must stay green | PL 9776 cites its lines | none |
| `docs/specs/03-rating-engine.md`, `docs/specs/00-overview.md` | edited only under DP-3 (b) or DP-5, with ruling text verbatim | **WK-690 S3** — see below | re-read at dispatch |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | every PR | registry |

**Lane A (WK-690 S3, `SL-1273`) at `origin/sl-1273-custom-objective-expression` =
`5af9d321f3ce4e6fab53dcd34e9289e20ae65884`** (committed 2026-10-05T08:43:48Z; read 2026-10-05 09:54 BST
against `origin/main` `47d770e8`; the branch was `c1aab29c` when this plan was first drafted and moves).
`git diff --name-only origin/main origin/sl-1273-custom-objective-expression` lists 35 paths; the
branch's own change set (`git diff --name-only origin/main...origin/sl-1273-custom-objective-expression`)
lists 33. Intersecting each list with the table above (and with `scripts/demo.py` and
`backend/tests/test_demo_command.py`, DP-6) leaves only `docs/INDEX.md`, the exempt generated registry.
**No overlap with S3's own change set**; S3 edits `backend/src/app/errors.py`, which this slice does not
touch. Re-read at dispatch: the branch moves.

**Open PRs at `4eb13644`, 2026-10-04; working ids as then (`gh pr list --state open`):** #1111 (FD-1411, this plan's finding; merged since, `47d770e8`); #1051
(PL 9776, above); #1048 (OQ 9777, working id: does NFR-489 cover traced requests — **decided (a), 2026-10-05:
NFR-489 governs untraced requests, so Acceptance 2 is the untraced arms and no traced arm is added**,
Acceptance 2); #1060
(rulings on PL 9776). None rules on this slice's subject.

### Register rows this plan reads

- **F50** (`bundle_slot.py` immutability argument): resolved 2026-08-30; its lesson binds DP-2 — a
  happy-path memo needs a fresh metadata read, and RL-1379 narrows the mutable case to `draft` refs.
- **F38** (NFR-489's without-GBM half not established): two of five component runs breached 15 ms;
  why Acceptance 3 compares three runs rather than one.
- **F35** (NFR-490 measured failing): out of scope (PL 9776), named so a traced arm is not
  mistaken for this slice's.
- **FD-1411** (HIGH, WK-674 / SL-1259): this plan's own finding. Its figures are quoted above; its
  Disposition item 2 names this plan as the remedy, item 3 the discharge event (Hand-off 2).
- **FD-1333** (a declared `decimal` output served on `/score` as a float, MEDIUM, WK-1178) and
  **FD-1335** (the `/score` 200 response has no OpenAPI schema, MEDIUM, WK-1178): both edit
  `score.py`'s response path (§"Write set", the contention), and Task 3 Step 5's byte-identity
  must not be read as freezing the spelling FD-1333 will change.
- **FD-1337** (`DecimalStr` and `Relativity` serialise in exponent form, which changes a content hash,
  MEDIUM, WK-1178): the same reason — Task 3 Step 5 compares before and after this slice only.
- **FD-1246** (a scoring trace omits the algorithm's `input` and `output` steps, low, WK-1178):
  `_maybe_sample_trace` is in the write set; this slice moves its session handling only and does not
  change what a trace contains.
- **FD-1244** and **FD-1245** (`WF-699` steps D4 and E2, low, WK-1178): read before Task 6 under
  DP-6 (a), which adds a step to the same journey.
- **FD-1196** (the per-worktree test database name collides across worktrees sharing a leaf name,
  WK-1178) and **FD-1218** (the shared template `gipricing` holds an abandoned test session and a
  stale schema, WK-1178): Task 0 Step 1 and Task 4 Step 1 create the scratch database with
  `createdb -T gipricing`. The executor names the scratch database uniquely (not after the worktree
  leaf), checks the template's schema head against the tree's alembic head before copying it, and
  records both in the ledger.
- **NFR-502/501 (F-W9-1)**: `nthread=1` per model call and validate-inbound-never-outbound are
  constraints the fix must not undo.

### Size

Medium: Task 0 about half a day (six instrumented passes), Tasks 1 to 3 about a day, Task 4's sweep
about 2.5 hours of exclusive box time (12 invocations; the 200 rps pass ran 18 min on `main`). One
two-half gate run.

## Decision points

DP-1 to DP-4 are the decision-maker's, ruled from Task 0's record. DP-6 was ruled (b) by the maintainer,
by delegation, before Task 0 (its `Resolved by` cell). DP-5 is the maintainer's. The
recommendations below are conditional on Task 0 confirming what reading suggests.

| DP | Question | Options | Recommendation | Owner | Blocks | Resolved by |
|---|---|---|---|---|---|---|
| **DP-1** | Which per-request costs are removed, and where | (a) one request-scoped session for the read path (auth, permission, Deployment, version row), so one checkout and one ping; (b) `last_used_at` written only when older than a fixed interval (e.g. 60 s), not per request; (c) skip the role query when the credential's own `permissions` already hold the permission; (d) pool sizing (`pool_size`, `max_overflow`) and `pool_pre_ping` replaced by `pool_recycle`; (e) the sampling read deferred so a quoted outcome whose roll exceeds the setting's maximum reads nothing | (a) + (b) if Task 0 shows checkouts and the UPDATE dominate; (d) only with a measured pool-wait figure; (c) needs RL-924's reading confirmed (it may change who may score); (e) last | decision-maker | Tasks 2, 3 | open: ruled from Task 0's record |
| **DP-2** | Is any new cross-request cache admitted (credential, permission, setting, Deployment, ref → hash) | (a) none: request-scoped consolidation only; (b) a short TTL cache for the sampling rate and permissions, with a stated staleness window; (c) a happy-path ref → hash memo for **non-draft** refs, relying on RL-1379, superseding RL-921's refusal for that case | (a). A cached credential would let a revoked key score for the TTL (a security change); a cached permission likewise; (c) saves one indexed read and contradicts a ruling and F50's lesson. Revisit only if (a) misses the budget with Task 0's numbers | decision-maker (RL-921 is a ruling) | Task 3 | open: ruled from Task 0's record |
| **DP-3** | What "per replica" means for the measurement: worker count | (a) one process, as the harness runs today; (b) one replica = N `uvicorn` workers, N stated, with the harness given `--workers` | (a) is the basis of Acceptance 2. `NFR-489` and `NFR-454` say "per replica" and no spec defines it. If Task 0 shows (a) is unreachable because `score_one`'s CPU alone exceeds one event loop at 200 rps, the decision-maker raises (b) as a spec clarification, never a silent harness change | decision-maker; spec text by ruling | Task 1 Step 3, Acceptance 2 | open: ruled from Task 0's record |
| **DP-4** | The ~200–300 ms in-handler stall: what fixes it | (a) GC: `gc.freeze()` after startup, or raised thresholds; (b) a reconnect or pool wait: DP-1 (d); (c) synchronous I/O on the loop: move it off; (d) unattributed after three runs: STOP and report | chosen only from Task 0's attribution; never a guess. (d) is a permitted outcome | decision-maker | Task 3 | open: ruled from Task 0's record |
| **DP-6** | Where the scripted exit-demo journey's `/score` call on the G2 path is built and accepted (Task 0 Step 3b found that no exit-demo code calls `/score` today) | (a) **this slice**: Task 1 adds a default-live arm to `bench-rating.py` (it seeds a `uat` Deployment and omits the ref), Acceptance 2 measures it, and Task 6 adds the `/score` call to `scripts/demo.py` with a wiring test in `backend/tests/test_demo_command.py`; (b) **split**: this slice adds and measures the default-live arm (Task 1, Acceptance 2), and the scripted journey's `/score` step is built and accepted by the plan for `PL-1371` §3.8 item 7 ("Exit demo (b): the scripted `WF-699` journey", **unplanned**, WK-1178), which receives Acceptance 1's third-arm table and Acceptance 2's default-live readings as its input; (c) **all to item 7**: this slice measures only the bench path, and item 7's plan owns both the arm and the step | (b). Item 7 depends on WK-673 S6 and WK-674 S2, 3, 5 and 6 (`PL-1371` §3.8 row 7), so a journey step written here would precede the journey it belongs to; but the latency on the G2 path is this slice's subject, so the arm is measured here, not deferred. (c) leaves the exit-demo path unmeasured after this slice merges. (a) is right only if item 7 is planned into this slice by the lead | decision-maker; the lead routes (b)/(c) to item 7's planner | Task 1 Step 2b, Task 6, Acceptance 2, Acceptance 9 | **(b)**, the maintainer by delegation: `to-lead.md` entry headed *"2026-10-05 09:59:49 BST — A10 early ACCEPTED (start when dm-9718 reports, about 10:10, solo 30 min); RL 9907 Q1 RULED "in scope"; PL 9728 DP-6 RULED (b) with a binding condition. Both ruled by me (the maintainer, by delegation), so no DM is needed"*. **Binding condition, verbatim:** *"item 7's record names NFR-489 (p99 < 50 ms with GBM, < 15 ms without, per replica) as an ACCEPTANCE of the demo's own /score call on the G2 path, measured uncontended, ≥3 runs. So the demo path cannot fall between the two owners."* Carried in Hand-off item 4. Task 6 is therefore not executed |
| **DP-5** | The budget is unreachable on this machine class (e2-standard-8) for a reason outside the code | (a) the maintainer amends or carries NFR-489 by a dated line; (b) the measurement moves to a defined reference machine | raised only if Task 0 or Task 4 shows it; the plan does not re-baseline. G4 (amended 2026-09-29) already carries NFR-489's verdict to "a dedicated host available", so (b) is G4's discharge event; DP-5 asks only whether the code-side remedy is complete when the shared VM cannot show it | **maintainer** | Acceptance 2 | not raised |

## Tasks

### Task 0: Attribute the per-request time and the stalls, on `main` (no committed code)

**Files:**
- Scratch only: a detached worktree of `origin/main`; a patch applied there and never committed.
- Ledger: `docs/ledgers/LG-<n>` (the only committed file).

- [ ] **Step 1: Set up.** Detached worktree at the dispatch tree; `uv sync --all-packages`; scratch
  database per `dev-commands` (`createdb -T gipricing`, then alembic with `-c <wt>/alembic.ini`).
  Record `git rev-parse HEAD`, `uptime`, `pgrep -c pytest`.
- [ ] **Step 2: Instrument the scratch copy.** Add per-phase timers to `score` and its dependencies,
  logged as extra fields on the request log line `TraceMiddleware` already writes
  (`backend/src/app/observability/middleware.py:61`):

```python
# scratch only — backend/src/app/api/_phase.py
import time
from contextvars import ContextVar

PHASES: ContextVar[dict[str, float] | None] = ContextVar("phases", default=None)

class phase:
    def __init__(self, name: str) -> None:
        self.name = name
    def __enter__(self) -> None:
        self.t = time.perf_counter()
    def __exit__(self, *exc: object) -> None:
        d = PHASES.get()
        if d is not None:
            d[self.name] = d.get(self.name, 0.0) + (time.perf_counter() - self.t) * 1000
```

  Wrap: `auth` (`deps.py:238-239`), `rbac` (`authz.py:62-73`), `serving_ref`, `fetch_bundle`,
  `score_one`, `sample_trace`, `serialise` (`result.model_dump_json()`). Add SQLAlchemy pool event
  listeners on `database.engine.sync_engine` (`checkout`, `connect`) timing checkout wait and new
  connections; a slot hit/miss counter around `score.py:251`; and `gc.callbacks` recording each
  collection's generation and duration. Start the server with `PYTHONASYNCIODEBUG=1` and
  `loop.slow_callback_duration = 0.05` so the loop logs every callback that blocks it for 50 ms or
  more, with its source.
- [ ] **Step 3: Run.** `bench-rating.py --http --rates 25`, three times; then `--rates 50`, three times.
  Per pass record start and end (UTC and BST), `uptime`, `pgrep -c pytest`.
- [ ] **Step 3b: The exit demo's `/score` path, measured beside it.** Added at the maintainer's (by delegation)
  order, `to-lead.md` entry "2026-10-04 19:46:13 BST — #1111 (FD 9729, NFR-489) noted; mint it before
  the ACK; the demo-path disclosure stays and PL 9728 Task 0 traces the demo's /score calls". Fact,
  read at planning time on `2cd4896f`: **no exit-demo code calls `/score` today.** `scripts/demo.py`
  calls only `GET /api/v1/demo/guide` (`:265`) and `GET /api/v1/models` (`:308`);
  `examples/fremtpl2/model.py:413` scores the golden quote in-process with `score_one`, not over
  HTTP; no frontend view posts to `/api/v1/score`; the P2 exit-demo row is "not started"
  (`docs/roadmap.md:603`) and its scripted journey is "unplanned" (`PL-1371` §3.8, item 7). The path
  is therefore the one G2 specifies (`docs/roadmap.md:566`: deployment to `uat` and then `prod`,
  `07` FR-429), whose consumer is a Service Account scoped per environment (`WF-701` prerequisites,
  `07` FR-389/430). **It differs from the bench path in one branch:** the bench sends an explicit
  ref (`scripts/bench-rating.py:347`) with a `uat` key (`:645`–`:653`) against a `draft` Rating
  Version and seeds no Deployment, so `_serving_ref`'s Deployment query
  (`backend/src/app/api/score.py:186`–`:204`) returns no row; the demo's default-live quote sends no
  ref and that query returns the live Deployment, which supplies the ref and `served_by`. Auth
  (API key), the statement count and the bundle-slot path are otherwise the same by reading; Step 3b
  measures it rather than assuming it. In the scratch worktree, seed the bench workspace's bundle
  as a Deployment of the key's environment (`DeploymentRow` on `uat`, the scratch copy only), drive
  the same `_drive` loop with the request body's `options.rating_version_ref` removed, at 25 and 50
  rps, three times each, under the same Step 2 instruments and the same per-pass record. Step 5
  tabulates it as a third arm, "exit-demo path (default-live, Deployment hit)", and states in one
  line whether it does the same per-request work as the bench path, naming any phase that differs.
- [ ] **Step 4: Sampling profile (required).** One 25 rps pass per arm with the server under
  `uvx py-spy record -o <scratch>/profile-<arm>.svg -- <the uvicorn command>`, and the top frames by
  self time in the ledger beside Step 5's phase table. The maintainer's (by delegation) order names "plus a sampling
  profiler" (§Self-review 1), so this step is not optional. **Its only exit:** `uvx` cannot fetch
  `py-spy`, or it cannot attach on this box. Then the ledger says so, with the printed error, and Step 5
  attributes from Step 2's instruments alone. Do not install it.
  Task 0's figures are **attribution, not an NFR reading**: asyncio debug mode, the per-phase timers,
  the pool listeners and `py-spy` all perturb latency. No Task 0 number is quoted as an NFR-489 result;
  Task 4 runs the head un-instrumented.
- [ ] **Step 5: Tabulate in the ledger.** Per arm and rate: p50, p99, max for each phase; checkouts
  and pool-wait p99; slot hits and misses (expect misses = 1 per process); GC counts and the longest
  pause per generation; every slow-callback line; every request of 100 ms or more with its dominant
  phase. Then state, in one line each: (i) the GBM-independent per-request cost and its top two
  phases; (ii) the stall's cause, or "unattributed"; (iii) whether one process can serve 200 rps given
  `score_one`'s share (DP-3, DP-5).
- [ ] **Step 6: STOP.** Hand the ledger to the lead for the DP-1 to DP-4 ruling (DP-6 is ruled (b)). Drop the scratch
  database; remove the scratch worktree.

### Task 1: The harness says what it measures (Acceptance 6)

**Files:** Modify `scripts/bench-rating.py` (`_measure_fetch`, `:675-726`; `_run_http_sweep`,
`:1075-1076`; under DP-3 (b) also `_serve`, `:729-758`, and `main`'s argument parser).

- [ ] **Step 1:** Rename the printed label at `:1075` to `_fetch_bundle alone, {label}, cold (slot
  miss: blob read, parse, load_bundle)`, and correct the docstring at `:678-688` to say the served
  path checks `content_hash` against the slot before the blob (`score.py:250-254`, RL-921) and that
  this figure is the miss path.
- [ ] **Step 2:** Add a warm figure: the same loop with one `BundleSlot()` created before it and
  reused, printed as `_fetch_bundle alone, {label}, warm (slot hit: version row read only)`.
- [ ] **Step 2b (DP-6 (a) or (b)):** a default-live arm in the HTTP sweep: `_seed` also writes a
  Deployment of the seeded Rating Version to the key's environment (`uat`), and the arm's request body
  omits `options.rating_version_ref`, so `_serving_ref` resolves the ref from the Deployment
  (`backend/src/app/api/score.py:186`–`:204`) as the G2 path does. It is printed as its own rung per
  arm, labelled "default-live (exit-demo path)". This is Task 0 Step 3b's scratch method made
  permanent in the harness, so Task 4 measures it un-instrumented on the head.
- [ ] **Step 3 (DP-3 (b) only):** `--workers N` passed through to `_serve`'s `uvicorn` argument list
  as `"--workers", str(N)`, default absent.
- [ ] **Step 4:** `uv run python scripts/bench-rating.py --help` shows the flag (if added); one
  `--rates 25` run prints both fetch lines. Commit.

### Task 2: The timing-free regression guard, red first (Acceptance 4)

**Files:** Create `backend/tests/test_score_request_cost.py`, reusing `test_score.py`'s fixtures
(`client`, `scoring_headers`, `compiled_version`) through its `conftest` or an import.

- [ ] **Step 1: Write the failing tests.** The bound `MAX_STATEMENTS` and `MAX_CHECKOUTS` are the
  values DP-1's ruling fixes; the code below shows the form.

```python
import pytest
from sqlalchemy import event

pytestmark = pytest.mark.req("NFR-489")

MAX_CHECKOUTS = 1      # DP-1 (a) as ruled
MAX_STATEMENTS = 3     # DP-1 as ruled; the ruling's number replaces this one

def _count(engine):
    seen = {"stmt": 0, "checkout": 0}
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def _s(*a, **k): seen["stmt"] += 1
    @event.listens_for(engine.sync_engine, "checkout")
    def _c(*a, **k): seen["checkout"] += 1
    return seen

def test_a_warm_score_request_stays_within_its_database_budget(client, scoring_headers, compiled_version):
    body = _quote({"rating_version_ref": SCORED_REF})
    assert client.post(SCORE_URL, json=body, headers=scoring_headers).status_code == 200  # warm
    seen = _count(client.app.state.database.engine)
    assert client.post(SCORE_URL, json=body, headers=scoring_headers).status_code == 200
    assert seen["checkout"] <= MAX_CHECKOUTS, seen
    assert seen["stmt"] <= MAX_STATEMENTS, seen
```

  Under DP-1 (b) add `test_last_used_at_is_not_written_on_every_request` (two requests inside the
  interval; the second issues no `UPDATE api_keys`, counted by statement text) and
  `test_last_used_at_is_written_once_the_interval_has_passed` (the clock patched past the interval;
  one `UPDATE`). Under any cache DP-2 admits, add one test per cache that the cached value is not
  served after its source changes past the stated window (a revoked key, a removed permission, a
  changed setting). The sampling rate at 0 and 1 keeps its existing tests (`test_score.py:904`,
  `:928`).
- [ ] **Step 2: Run red.** `uv run pytest -q backend/tests/test_score_request_cost.py`. Expected:
  FAIL on `main`'s code because `seen["checkout"]` is 5 and `seen["stmt"]` is at least 7 (Task 0's
  count governs; a different cause is a plan defect). Record the line.
- [ ] **Step 3:** Commit the red tests with `xfail(strict=True)` removed in Task 3's commit, or as
  one commit with Task 3 — the ledger records the red either way.

### Task 3: The ruled fix, in the layer that owns each cost

**Files:** per DP-1, DP-2, DP-4 as ruled (§"Write set").

- [ ] **Step 1 (DP-1 (a)):** add `Database.request_session` in `backend/src/app/db/session.py` and a
  request-scoped dependency that yields one `AsyncSession` per request; `require_caller`'s API-key
  branch, `requires`, `_serving_ref` and `_fetch_bundle` take it instead of opening their own. The
  authentication write, if any remains, commits on that session before the handler's reads. The
  sampling write keeps its own `unit_of_work` (FR-259's failure isolation, `score.py:477-482`).
- [ ] **Step 2 (DP-1 (b)):** in `authenticate_api_key` (`auth/service.py:226`), set `last_used_at` only
  when it is `None` or older than the ruled interval.
- [ ] **Step 3 (DP-1 (d), DP-4):** pool arguments and the stall fix exactly as ruled.
- [ ] **Step 4:** Task 2's tests pass; `uv run pytest -q backend/tests/test_score.py
  backend/tests/test_traces.py backend/tests/test_score_request_cost.py` passes (Acceptance 5).
- [ ] **Step 5:** Byte-identity: the bench quote's `/score` response body on `main` and on the head,
  `cmp` equal except `trace`-free fields that carry time or ids (named in the ledger). Commit.

### Task 4: The acceptance sweep, alone on the box (Acceptance 2, 3)

- [ ] **Step 1:** Exclusive window confirmed (activation need 3). Scratch database as in Task 0. The
  server runs the head **un-instrumented**: none of Task 0's timers, listeners, debug mode or profiler.
- [ ] **Step 2:** For R in 25, 50, 100, 200, three invocations each, in the order 25, 50, 100, 200,
  25, 50, 100, 200, 25, 50, 100, 200 (interleaved, so drift does not land on one rate). Record per
  invocation everything Acceptance 2 names.
- [ ] **Step 3:** Table in the ledger: rate × run × arm with p50, p99, handler p99, issued rps,
  errors, load start/end. Reading per cell against the budget, labelled "measured, diagnostic (G4)";
  never written as an NFR-489 PASS or FAIL. Any OVER: stop, report to the lead; do
  not tune and re-run inside the same window without a new go.

### Task 6 (DP-6 (a) only): the scripted journey calls `/score` on the G2 path (Acceptance 9)

**Files:** Modify `scripts/demo.py`; modify `backend/tests/test_demo_command.py`. Read FD-1244 and
FD-1245 first (both `WF-699` step defects, WK-1178): this task adds a step to that journey and must not
build on either defect.

- [ ] **Step 1: Write the failing test.** In `test_demo_command.py`, a test that runs the demo
  command's scripted journey against the test app and asserts that it issues one `POST
  /api/v1/score` with **no** `options.rating_version_ref`, authenticated as a Service Account scoped
  to the deployed environment (`07` FR-389/430, `WF-701` prerequisites), and that the response's
  `served_by` names the live Deployment. Run it: expected FAIL because `scripts/demo.py` calls only
  `GET /api/v1/demo/guide` and `GET /api/v1/models` (Task 0 Step 3b). Record the line.
- [ ] **Step 2:** Add the call to `scripts/demo.py`, after the deployment step it depends on. Run the
  test green. Commit.

### Task 5: The gate and the ledger

- [ ] **Step 1:** The two-half gate through the gate-runner, outside the measurement window
  (Acceptance 7). Record each rc and the tree.
- [ ] **Step 2:** Ledger: Task 0's table, the ruling's id, every red with its line, Task 4's table,
  `git diff --stat origin/main...HEAD` against §"Write set" (Acceptance 8).

## Hand-off

1. The lead mints PL 9728 and SL 9727 (working ids) at the merge turn and dispatches Task 0 only after
   activation needs 1 to 4 hold; Tasks 1 to 6 after need 5 (Task 6 under DP-6 (a) only).
2. On merge, FD-1411's remedy event is met; its own discharge also needs SL-1259's NFR-489 verdict
   on the exit tree, or the maintainer amending or carrying NFR-489 by a dated line (FD-1411
   §Disposition item 3). Under G4 that verdict is carried on the shared VM (Acceptance 2). The
   auditor closes the row.
3. If DP-3 (b) or DP-5 is ruled, the spec text and the measurement basis change for SL-1259 too; the
   lead routes that to SL-1259's planner.
4. **The scripted journey's `/score` step (DP-6).** Under DP-6 (b) or (c), its owner is the plan for
   `PL-1371` §3.8 item 7 ("Exit demo (b): the scripted `WF-699` journey", WK-1178, unplanned). The
   lead routes the ruling, this slice's Acceptance 1 third-arm table and (under (b)) Acceptance 2's
   default-live readings to that plan's planner. That plan's acceptance names the `/score` call on the
   G2 path, a wiring test for it, and NFR-489's budgets on that path. **DP-6 is ruled (b)**, with this
   binding condition (`to-lead.md` entry headed *"2026-10-05 09:59:49 BST — A10 early ACCEPTED (start when dm-9718 reports, about 10:10, solo 30 min); RL 9907 Q1 RULED "in scope"; PL 9728 DP-6 RULED (b) with a binding condition. Both ruled by me (the maintainer, by delegation), so no DM is needed"*), verbatim: *"item 7's record names NFR-489 (p99 < 50 ms with GBM, < 15 ms without, per replica) as an ACCEPTANCE of the demo's own /score call on the G2 path, measured uncontended, ≥3 runs. So the demo path cannot fall between the two owners."* The lead's
   dispatch-record delta for `PL-1371` §3.8 item 7 carries it to that plan's planner. Until it is planned, the
   exit-demo `/score` risk is owned by WK-1178 through that item, not by this slice. Under DP-6 (a),
   Task 6 discharges it here.

## Self-review

1. **The maintainer's (by delegation) order, clause by clause.** "Task 0 attributes the stalls … per-request phase timing
   (auth, bundle resolve/fetch, deserialise, score_one, trace sampling, response), plus a sampling
   profiler": Task 0 Steps 2 and 4 (Step 4 required; its only exit is `py-spy` unavailable, stated). "Candidates to test, not assume: synchronous blob/DB I/O inside the
   async handler, per-request bundle deserialisation, GC pauses, worker count": Step 2's slow-callback
   log, hit/miss counter, `gc.callbacks`; DP-3. "The fix is chosen FROM Task 0's evidence": Status;
   DP-1 to DP-4. "Acceptance … 25/50/100/200 rps per replica, uncontended, ≥3 runs per rate,
   per-pass times and load": Acceptance 2. "A regression guard that runs in CI": Acceptance 4, Task 2.
   "If … unreachable … a decision point, not a silent re-baseline": DP-5.
1a. **The audit of 2026-10-05 (`audit-pl9728`), five corrections.** The profiler is required (Task 0
   Step 4); the exit-demo `/score` call is DP-6, with Task 6 and Hand-off item 4; G4's caveat is in
   Acceptance 2 and Tasks 0 and 4; FD-1411 is cited and the tree and S3 figures are re-pinned; the
   register rows the audit listed are read below, with FD-1333/FD-1335's `score.py` contention named.
1b. **Pre-mint edits of 2026-10-05, on the maintainer's rulings by delegation.** DP-6 carries its
   resolver, the entry headed *"2026-10-05 09:59:49 BST — A10 early ACCEPTED (start when dm-9718 reports, about 10:10, solo 30 min); RL 9907 Q1 RULED "in scope"; PL 9728 DP-6 RULED (b) with a binding condition. Both ruled by me (the maintainer, by delegation), so no DM is needed"*, and its binding condition verbatim (DP-6 row, Hand-off item 4);
   Acceptance 2 is the untraced arms against NFR-489, on the entry headed *"2026-10-05 10:47:03 BST — OQ 9777 (#1048) DECIDED (a); the combined mint order ACCEPTED; pairing coupled records in one mint PR ACCEPTED (max 3 records per PR)"*; the Status,
   activation need 5, the DP preamble and Task 0 Step 6 no longer wait on a DP-6 ruling. Working ids
   re-checked against `origin/main` `072c56e1`: PL 9776 (#1051) and OQ 9777 (#1048) are unminted, so
   none is re-pointed.
1c. **Pre-mint check of 2026-10-05 15:26 BST, at `origin/main` `809a3794`.** No cited code path
   changed since `47d770e8` (activation need 4's files, `config.py`, `scripts/demo.py`, the cited
   tests); the `03` and `roadmap.md` lines cited are unmoved. PL 9776 (#1051) and OQ 9777 (#1048) are
   still unminted. Lane B's order is recorded under activation need 1. The G2 ruling (`to-lead.md`
   entry headed *"2026-10-05 13:05:42 BST — RULING (the maintainer, by delegation): G2's "in Phase 1b's form" = a scripted HTTP journey plus a served page; WK-675 is OFF G2's critical path"*)
   changes no step here: the scripted journey stays with `PL-1371` §3.8 item 7, and DP-6 (b) stands.
   Item 7's leaf plan (`PL-1371` Task 3, ordered 2026-10-05) carries DP-6's binding condition. This
   plan does not cite that leaf by working id, because a record that cites another mints after it,
   and this plan mints first.
2. **The bundle-cache hypothesis is tested, not built.** Reading shows the slot already hits on the
   served path (§"Where the time goes"); Task 0 Step 5 confirms it with a counter.
3. **Placeholders.** The statement and checkout bounds in Task 2 are fixed by DP-1's ruling, stated as
   such; no other value is left open.
4. **Ids.** Every `FR-`/`NFR-` cited is defined in `03`, `00` or `07`; FD-1411 is minted; PL 9776, OQ 9777 and
   this plan's own ids are written as working ids, never hyphenated.
