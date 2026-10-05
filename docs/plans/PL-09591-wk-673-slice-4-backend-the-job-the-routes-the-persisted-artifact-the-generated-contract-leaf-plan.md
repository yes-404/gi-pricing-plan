---
id: PL-9591
family: plan
kind: leaf
title: WK-673 Slice 4 — backend, the Job, the routes, the persisted artifact, the generated contract: leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05
owner: planner
tree: 137bc817ef1fb40ea57e9053e0ad40b73bdff3a8
phase: P2
work: WK-673
slice: SL-1388
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-1388, PL-1267, PL-1371, LG-1400, RL-1236, RL-1263, RL-1264, RL-1394, RL-1402, SL-1386, SL-1387, SL-1389, SL-1391]
---

# PL 9591 (working id) — WK-673 Slice 4: backend — the Job, the routes, the persisted artifact, the generated contract: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor is spawned from `.claude/roles/executor.md` and also
> binds `test-driven-development` (every task is red first), `fastapi-service` (Task 5: the
> routes, RFC 9457 problems), `python-package` (Tasks 2–4: where code lives), `python-test`
> (requirement markers, negative tests), `contract-guard` and `contract-schema` (Task 6),
> `spec-change` (Task 1), `dev-commands` (the two-half gate, the alembic DSN) and
> `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before the first
> step.

Filed under working id **9591**, reserved by the lead and named in the lead's brief
`~/gi-pricing-plan.local/handover/brief-prep-wave-2026-10-05.md`, section AQ (written for
planner-673s46). Drafted from 16:54:45 BST (`TZ=Europe/London date`) on 2026-10-05 against
origin/main `137bc817ef1fb40ea57e9053e0ad40b73bdff3a8` (`git rev-parse origin/main` after
`git fetch`). Every locator below was read at that tree unless another tree or a branch head
is named. Unminted records are cited by working id and kept out of `relates:` (check 32):
PL 9689 (WK-673 Slice 3, draft #1138, head `e810b785`), PL 9716 (Slice 7, #1127, head
`305ffca9`), PL 9649 (the FR-240 family fix, WK-673, #1152, head `df8ba756`), PL 9688 (the
FD 9707 fix, WK-673, #1145, head `2f3269c8`), PL 9683 (the FD 9708 fix, #1140, head
`f18549bb`), PL 9616 (the FD-1416 fix, #1168, head `0b60c81b`), PL 9610 (WK-1250 S2, #1170,
head `ca407ed9`), PL 9629 (the exit-demo plan, #1164, head `68dd997c`), RL 9620 (the RL-1263
amendment, #1162, head `381254c3`), RL 9614 (FD-1244 and FD-1245, #1167, head `b71f0da2`),
and the A-1 to A-3 plans (PL 9599, PL 9597, PL 9595; not pushed at 16:54 BST).

## Goal

Make the Dislocation Run a backend artifact: the `dislocation.run` Job handler, which owns
the Job identity, the output location and resumability that `pricing-core` may not acquire;
`POST /api/v1/dislocation-runs` (202 plus a Job) and `GET /api/v1/dislocation-runs/{id}`
with RBAC and RFC 9457 problems (`03` §5.1); the run persisted as a citable row with its
large part as a content-addressed blob (FR-265); attribution (FR-266, Slice 3's `attribute`)
run inside the same Job; and `DislocationRun` registered for generation, `docs/contracts/`
regenerated and the slug moved from `ONE_SIDED_SLUGS` to `COMPARED_SLUGS` (`PL-1267`
Acceptance 6).

**Architecture.** Everything new is backend. `pricing-core` is called, never edited:
`dislocation_frame`, `select_movers` and `summarise_dislocation` (`analysis.py:177`, `:264`,
`:325`, Slice 2) and `derive_changes` and `attribute` (Slice 3, PL 9689). The handler follows
`_rating_regression` (`backend/src/app/worker/rating_handlers.py:130`): load in one
`run_on_loop` call, compute on the worker thread, persist in one unit of work through a single
writer. `attribute` is `async` because its resolver is; it never runs inside `run_on_loop`
(the 30 s hang `scoring_handlers.py` documents). The handler first resolves every artifact the
two versions pin into an in-memory resolver, then runs `attribute` on the worker thread with
no database I/O. Contract and frontend client are generated, never hand-written.

**Tech stack.** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 async, Alembic, Polars,
Celery (the existing worker). No new dependency.

**Spec.** [`03-rating-engine.md`](../specs/03-rating-engine.md) FR-263 (`:186`), FR-265
(`:188`), FR-266 (`:189`), FR-1397, FR-1398, FR-1399 (`:190-192`), §4.6 (`:514`), §5.1's two
rows (`:919-920`) and the owned-codes list (`:924-…`), §5.2 (`:1049-1062`, `:1124`);
[`06-governance.md`](../specs/06-governance.md) §4.1's catalogue (`:281-290`, `RL-1236`);
`RL-1264` (the feasibility rule, "the estimated count shown before launch"); `LG-1400` Task 7
(the negative-test table).

## Status

`draft`. **Five decision points are open** (§"Decision points"); DP-S4-1 to DP-S4-3 and
DP-S4-5 are the decision-maker's and block. The plan moves to `active` only through a
separate activation PR, after every need below holds.

### Activation needs, in order

1. **This plan is merged, minted and made `active` by a dated line.**
2. **`SL-1387` (Slice 3) is closed.** `PL-1267`'s one-slice-at-a-time order is
   1 → 2 → 7 → 3 → 4 → 5 → 6 (`PL-1267` §"Sequencing"); this slice consumes Slice 3's
   `derive_changes`, `attribute`, `estimate_attribution_ratings`, `AttributionError`,
   `BundleDelta` and `Attribution`, and `DislocationRun`'s four attribution fields (PL 9689
   Task 2, Tasks 3–6). Where Slice 3's merged signatures differ from what this plan quotes,
   the merged code governs and the dispatch record names each difference.
3. **A ruling on DP-S4-1, DP-S4-2, DP-S4-3 and DP-S4-5** is merged and minted, adopting or
   amending the texts in §"Appendix". An unminted ruling is a stop.
4. **The lane is free under `RL-1263`** as RL 9620 amends it (if minted by then), with the
   same-Work conditions written into the dispatch record (§"Write set, and its contention").
5. **The maintainer's dispatch GO**, and the lead's go in a separate activation PR.

Not needs: `SL-1256` (Slice 5's, not this one's: nothing here reads a live version); FD-1245
(RL 9614 DP-2 (a) keeps FR-257's gate at `POST /rating-versions/{id}/submit`, which this
slice does not touch).

## Acceptance Standard

Each item is a named test or a command a fresh reviewer can re-run, in the executor's own
worktree (`env -C <worktree> …`), against `origin/main...HEAD`. Every test is shown red before
its code exists, and the ledger quotes the red by its cause, not its status (README
convention 2). `B` is `backend/tests/test_dislocation_runs.py`.

1. **The run persists as a citable row.** `B::test_a_dislocation_run_persists_with_its_job_id_and_movers_blob`:
   after `execute_job` returns `JobStatus.SUCCEEDED`, one `dislocation_runs` row exists whose
   `run` validates as `DislocationRun`, whose `run["job_id"]` equals the Job's id, and whose
   `movers_blob_sha256` equals `run["largest_movers_blob"]`'s digest. The Job's result is
   `JobResult(kind="artifact", ref="dislocation_run:<row id>")`.
2. **The movers blob is never served by the generic blob route** (NFR-499).
   `B::test_the_generic_blob_route_refuses_a_movers_blob`: `GET /api/v1/blobs/{sha256}` on the
   movers digest answers 404 `NOT_FOUND`, the same answer as an unknown digest. Shown red with
   the column left out of `QUOTE_INPUT_BLOB_COLUMNS`.
3. **A subset bundle never becomes a Rating Version** (`RL-1264`; `LG-1400` Task 7, row 1).
   `B::test_dislocation_subset_bundles_never_become_rating_versions`: a run with K = 3 derived
   changes leaves the `rating_versions` row count and `GET /api/v1/rating-versions` unchanged,
   and the artifact records 2^3 = 8 compiled subset hashes. Shown red on a deliberately broken
   handler that persists one subset as a `RatingVersionRow` (scratch-reverted).
4. **A bad partition is refused at the route before any Job** (`LG-1400` Task 7, row 3).
   `B::test_post_refuses_groups_that_do_not_partition_the_derived_changes`: a spec whose
   `change_groups` leaves `c2` out answers 422 `VALIDATION_FAILED` naming `c2`, and no Job row
   is written. A matching status with a differing `code` or an unnamed change is a plan defect.
5. **Reconciliation failure surfaces by its own code.**
   `B::test_a_run_that_does_not_reconcile_fails_with_attribution_reconciliation_failed`: with
   `attribute` patched to raise `AttributionError(code="ATTRIBUTION_RECONCILIATION_FAILED")`,
   the Job ends `failed` with that code and no `dislocation_runs` row exists.
   `ATTRIBUTION_RECONCILIATION_FAILED` is in `RATING_ERROR_CODES`
   (`backend/src/app/errors.py:309`).
6. **The routes enforce the ruled permissions** (DP-S4-2). `B::test_post_needs_<ruled permission>`
   and `B::test_get_needs_rating_read`: a principal without the permission gets 403
   `PERMISSION_DENIED` (`backend/src/app/platform/rbac.py:100-105`); another workspace's run id gets 404 `NOT_FOUND`. Under DP-S4-2 (b) the
   built-in `analyst` and `pricing_actuary` roles start a run (WF-699 D6's actor is the
   Analyst) and `auditor` cannot.
7. **The estimated rating count is shown before launch** (`RL-1264`, DP-S4-5).
   `B::test_the_estimate_is_returned_before_any_job` (under DP-S4-5 (a)): the estimate
   answers 200 with `derived_changes`, `policies` and `estimated_ratings` equal to
   `estimate_attribution_ratings(k, policies, grouped=…)`, and writes no Job.
8. **Identical inputs give a byte-identical artifact** (NFR-495 as `PL-1267` applies it).
   `B::test_two_runs_of_the_same_spec_are_byte_identical`: two Jobs over the same spec persist
   `run` values equal after removing `job_id`, and the same movers digest.
9. **`dislocation-run` is compared, not one-sided** (`PL-1267` Acceptance 6).
   `grep -n '"dislocation-run"' backend/tests/test_contracts.py` prints one line, inside
   `COMPARED_SLUGS`, none inside `ONE_SIDED_SLUGS`; `uv run python scripts/generate-contracts.py
   --check` exits 0; `uv run pytest backend/tests/test_contracts.py -q` passes.
10. **Requirement markers.** `uv run python scripts/req-coverage.py` lists FR-265, FR-263,
    FR-1398 and FR-266 with at least one test in `B`.
11. **The resolver move changed no behaviour.** `uv run pytest
    backend/tests/test_rating_version_compile.py -q` passes unmodified before and after Task 3,
    and `git diff origin/main...HEAD -- backend/tests/test_rating_version_compile.py` is empty.
12. **The two-half gate passes** on the slice head (`dev-commands`), and the four docs checks
    (`audit-docs.py`, `doc-id.py check`, `doc-index.py --check`, `register-lint.py`) with
    their rc and summary lines quoted.
13. **The slice closes on the maintainer's MERGE-ACK and a clean audit** (`PL-1267`
    Acceptance 8): no maintainer acceptance line is required for a slice.

## Global Constraints

- **Money is integer minor units, never float** (`CLAUDE.md` §7). The row stores the
  `DislocationRun` JSON exactly as `model-schema` dumps it; no column holds a money figure as
  a float.
- **`pricing-core` stays importable standalone** (`CLAUDE.md` §2): no edit under
  `packages/pricing-core/` in this slice. The Job identity, output location and resumability
  are the handler's (`PL-1267` Global Constraints).
- **Nobody hand-writes a shape `model-schema` owns** (`CLAUDE.md` §2): the routes take and
  return `DislocationSpec` and `DislocationRun`; a route-local response model is refused. The
  estimate's response, if DP-S4-5 is (a), is a new `model-schema` type.
- **No pandas** (`CLAUDE.md` §3): the movers blob is Parquet written by Polars.
- **`docs/contracts/` generated files are never hand-edited**; the hand-authored
  `dislocation-run.schema.json` stays as the authored side of the comparison (`COMPARED_SLUGS`
  holds both sides, `test_contracts.py:5-9`). A disagreement the comparison surfaces is a
  stop for the decision-maker (`CLAUDE.md` §0), never fixed by editing whichever side is
  convenient.
- **NFR-499: no Quote Context in a log line, error message or audit payload.** A movers row
  carries every portfolio column (`03:1124`), so its blob is a quote-input store.
- **Permissions come from `RL-1236`'s catalogue**; no new permission (a new name is a scope
  change, `PL-1267` Slice 4). FD-1197 is cited.

## Scope

### Requirement coverage, each id individually

| Id | Where | What this slice does | Task |
|---|---|---|---|
| FR-263 | `03:186` | the run reachable over HTTP and persisted (the computation is Slice 2's) | 4, 5 |
| FR-265 | `03:188` | the persisted, citable artifact; its id is what Slice 5's gate reads | 2, 4 |
| FR-266 | `03:189` | attribution run inside the Job and persisted on the artifact (computed by Slice 3) | 4 |
| FR-1397 | `03:190` | the reconciliation failure's code registered and surfaced (checked by Slice 3) | 1, 4 |
| FR-1398 | `03:191` | subset bundles never a Rating Version, at the only layer that could write one | 4 |
| FR-1399 | `03:192` | the partition refusal at the route, before any Job | 5 |
| NFR-495 | `03` §9 | identical inputs, byte-identical artifact, through the Job | 4 |
| `RL-1264` item 3 | the feasibility rule | the estimated rating count shown before launch | 5 |

**Not in scope:** the computation (Slices 2 and 3); FR-224, FR-257 limb (2), `06` FR-364
(Slices 5 and 6); the Dislocation view (WK-675 Slice 8, which depends on this slice).

### Premises read at `137bc817`

| # | Premise | At `137bc817` | Status |
|---|---|---|---|
| a | The Job kind exists, with no handler | `JobKind.DISLOCATION_RUN = "dislocation.run"` (`model_schema/jobs.py:63`), queue `COMPUTE` (`backend/src/app/platform/jobs.py:79`); no `register_handler(JobKind.DISLOCATION_RUN, …)` | reproduces |
| b | The handler registry | `HANDLERS` and `register_handler` (`backend/src/app/worker/handlers.py:27`, `:30`, refusing a duplicate at `:37-38`); `register_rating_handlers` (`rating_handlers.py:218`) called from `entrypoint.py:73` | reproduces |
| c | The 202 + Job route precedent | `start_regression_run` (`backend/src/app/api/models.py:1274`): `requires(Perm.RATING_COMPILE)` (`:1276`), `job_service.submit(…, JobKind.RATING_REGRESSION, {**job_identity(caller), …}, caller.principal, workspace_id=caller.workspace_id)` (`:1291-1297`), 202 and `Location: /api/v1/jobs/{job.id}`; the read `get_regression_run` (`:1320`) with `RATING_READ` | reproduces |
| d | The citable-row precedent | `RegressionRunRow` (`backend/src/app/db/models.py:2178`): `run` JSONB, copied query columns, a scalar blob digest column; single writer `persist_run` (`platform/regression_runs.py:27`) | reproduces |
| e | The quote-input deny list | `QUOTE_INPUT_BLOB_COLUMNS` (`platform/blobs.py:496`) holds `ScoringTraceRow.blob_sha256` and `RegressionRunRow.cases_blob_sha256`; `blob_readable_by` refuses any digest a listed column holds | reproduces |
| f | The compile resolver is not reachable from a worker | `class _Resolver` is nested inside `compile_rating_version` (`platform/rating_versions.py:445`) | reproduces; Task 3 moves it (DP-S4-4) |
| g | `attribute` is async and takes a resolver | `03:1060-1062` | reproduces (Slice 3 builds it) |
| h | A long coroutine in one `run_on_loop` call hangs | `scoring_handlers.py:195-203` (the 30 s `JobProgress` timeout) | reproduces; the handler pre-resolves, then runs `attribute` off the loop |
| i | No built-in human role holds `score:batch` | `BUILTIN_ROLES` (`model_schema/permissions.py:135-146`): `analyst` and `pricing_actuary` hold `rating:read`, `rating:compile`, `dataset:read`, not `score:batch` | reproduces; decides DP-S4-2 |
| j | The contract is one-sided | `"dislocation-run"` in `ONE_SIDED_SLUGS` (`backend/tests/test_contracts.py:98`); `GENERATED_SHAPES` (`scripts/generate-contracts.py:38`) has no `"dislocation-run"` | reproduces |
| k | The migration head | `backend/migrations/versions/e5b7d9f1a3c6_custom_objective_expression_storage.py` | re-read at dispatch; a later head is the parent |
| l | `03` §5.1's rows carry no permission or codes | `:919` `**202** Baseline vs candidate over a portfolio (FR-263)`; `:920` `Dislocation artifact` | reproduces; Task 1 applies the ruled texts |

### Risks

- **The Job's duration.** 2^K full-portfolio passes in one Job. Slice 3's ledger gives the
  measured rate; DP-S4-1 decides whether one Job is enough.
- **`_Resolver` is edited by three in-flight plans** (PL 9649, PL 9610, and A-1, PL 9599).
  A move that lands between their edits conflicts with each. Task 3 is a pure move, re-read on
  the dispatch tree; §"Contention" serialises it.
- **The authored contract may disagree with the generated one.** Slices 1–3 hand-edited it;
  the comparison is its first check. A disagreement is a stop (Global Constraints).

## Write set, and its contention (`RL-1263`, RL 9620)

**Classes**, cited by key in `docs/process/delivery-process.core.json`
`guards.parallelism.build_slices_across_works.no_shared_files`: **exempt** —
`registry_exempt_append_only` (`backend/src/app/db/models.py`: a new class appended;
`backend/src/app/main.py`: a router registration; `backend/migrations/versions/`: a new
revision, the second merge re-pointing `down_revision`; `generated`; `ONE_SIDED_SLUGS`
key-disjoint); **other shared path** — `serialise_unless_dispatch_record_names_path_and_check`;
**SERIALISES** — `forbidden` (`both_change_same_existing_function_class_method_spec_section_or_policy_table`).
**Same-Work pairs** (RL 9620, its condition 2, working id, unminted at this tree): two
WK-673 slices run at once only when the dispatch record shows (a) the file sets resolved by
these rules and (b) no plan dependency, neither consuming the other's output, named both ways.

### By file and symbol, at `137bc817`

| Path | Symbol or region | Change |
|---|---|---|
| `docs/specs/03-rating-engine.md` | §5.1 rows `:919-920`; the owned-codes list (`ATTRIBUTION_RECONCILIATION_FAILED` is Slice 3's P1, not re-added); a new §5.1 row if DP-S4-3 (b) or DP-S4-5 (a) | the ruled texts (Appendix) |
| `backend/src/app/db/models.py` | new `DislocationRunRow`, appended | exempt (new class) |
| `backend/migrations/versions/<rev>_dislocation_runs.py` | new revision | exempt (new revision) |
| `backend/src/app/platform/dislocation_runs.py` | new: `persist_run`, `fetch_run` | new file |
| `backend/src/app/platform/blobs.py` | `QUOTE_INPUT_BLOB_COLUMNS` (`:496-499`) | one entry appended |
| `backend/src/app/platform/rating_versions.py` | `_Resolver` (`:445-555`) moved to module level as `WorkspaceResolver`; `compile_rating_version` (`:423`) instantiates it | pure move (DP-S4-4) |
| `backend/src/app/worker/dislocation_handlers.py` | new: `_dislocation_run`, `register_dislocation_handlers` | new file |
| `backend/src/app/worker/entrypoint.py` | `:70-74` | one `register_dislocation_handlers()` call appended |
| `backend/src/app/api/dislocation_runs.py` | new router | new file |
| `backend/src/app/main.py` | `:128-153` | one `include_router` line (exempt) |
| `backend/src/app/errors.py` | `RATING_ERROR_CODES` (`:309`) | `ATTRIBUTION_RECONCILIATION_FAILED` appended |
| `packages/model-schema/src/model_schema/dislocation.py` | new `DislocationEstimate` (DP-S4-5 (a) only) | added after Slice 3's types |
| `packages/model-schema/src/model_schema/__init__.py` | `__all__` | `DislocationEstimate` appended (name-disjoint exempt) |
| `scripts/generate-contracts.py` | `GENERATED_SHAPES` (`:38`) | `"dislocation-run": "DislocationRun"` appended |
| `backend/tests/test_contracts.py` | `COMPARED_SLUGS` (`:38-59`); `ONE_SIDED_SLUGS["dislocation-run"]` (`:98`) | slug added; key removed (key-disjoint exempt) |
| `docs/contracts/schemas/generated/dislocation-run.schema.json`, `docs/contracts/openapi/generated.json` | generated | regenerated |
| `backend/tests/test_dislocation_runs.py` | new | Acceptance 1–8 |
| `docs/ledgers/LG-<n>-…md`; `docs/INDEX.md` | added; regenerated | registry |

**Not written:** anything under `packages/pricing-core/`; `docs/contracts/schemas/dislocation-run.schema.json`
(the authored side; a disagreement is a stop); `frontend/` (the generated client is
VCS-ignored); `06`; `approvals.py` (either); `docs/roadmap.md` (except the activation PR).

### Contention

| Path | This slice | Other slice | Shared existing definition? | Class |
|---|---|---|---|---|
| everything Slice 3 writes (`analysis.py`, `dislocation.py`, `03` §4.6, §5.1 codes, §5.2) | consumes | **SL-1387** (PL 9689, WK-673) | plan dependency: this slice consumes Slice 3's output | **SERIAL** (same Work, RL 9620 (b) fails) — activation need 2 |
| `03` §5.1 | rows `:919-920` | **SL-1391** (PL 9716, WK-673): the diff row `:904`, a cells row after it, the owned-codes list | no (different rows) | serial anyway: Slice 7 precedes Slice 3, which precedes this slice |
| `platform/rating_versions.py` `_Resolver` | moved (DP-S4-4) | **PL 9649** (the FR-240 family fix, **WK-673**, SL 9647): a `factor` branch in `_Resolver.resolve`; **PL 9610** (WK-1250 S2, SL-1340): a `sub_graph` branch; **A-1** (PL 9599, WK-1178, not pushed): the peril branch (the maintainer's entry "2026-10-05 16:43:31 BST", item 1) | **yes**: the same class | **SERIALISES** with each. For PL 9649 (same Work): RL 9620 (a) fails on this class, so the pair is serial whatever (b) says. Order: whichever merges second merges main and re-applies its change to the class where it then lives; the move is mechanical, so this slice prefers to merge **after** all three, re-reading the class on the dispatch tree (Task 0 Step 3) |
| `backend/src/app/errors.py` `RATING_ERROR_CODES` | one name appended | **PL 9649** (WK-673): appends `CONTROL_FACTOR_IN_RATEABLE_PATH`; **PL 9683** (WK-1178) under its DP-1 (a): `MODEL_REFERENCE_MODE_INCONSISTENT`; **PL 9776** (WK-1178) conditionally | the same `frozenset` literal's tail | **other shared path**: allowed only if the dispatch record names the path and the check `git diff -U0 origin/main...<branch> -- backend/src/app/errors.py` showing one added line per slice and different names; the second to merge merges main and re-gates. For PL 9649 (same Work) RL 9620 (b) also needs "no plan dependency": neither consumes the other's output (this slice calls `compile_bundle` through `attribute`, which PL 9649 changes for control-intent factors, but no test here depends on that behaviour) — the dispatch record names that both ways |
| `scripts/generate-contracts.py` `GENERATED_SHAPES` | one key appended | **PL 9683** (`rating-version-create`), **PL 9616** (`approval-request`) | the same dict's tail | **other shared path**: the dispatch record names the path and the check (one added key each, different keys); the second merges main, regenerates, re-gates |
| `backend/tests/test_contracts.py` | `COMPARED_SLUGS` + one; `ONE_SIDED_SLUGS` − `"dislocation-run"` | **PL 9683** (+ one `ONE_SIDED_SLUGS` key), **PL 9616** (edits `ONE_SIDED_SLUGS["approval-request"]`, a new `SHIPPED_NOT_COMPARED`), **PL 9713** (conditional) | `ONE_SIDED_SLUGS`: key-disjoint (exempt); `COMPARED_SLUGS`: no other plan edits it | exempt (keys named in the dispatch record); `COMPARED_SLUGS` one-sided |
| `backend/migrations/versions/` | one new revision | **PL-1342** (WK-674 S3, `SL-1257`): one new revision | no existing file | exempt; the second re-points `down_revision` to the one head |
| `backend/src/app/db/models.py` | new class appended | **PL-1342**: `EnvironmentSettingRow` appended | no | exempt |
| `backend/src/app/main.py` | one `include_router` | **PL 9728** (WK-1178): a `gc.freeze()` lifespan hook (DP-4 (a) only); **PL-1342**: a router include | no | exempt |
| `backend/src/app/platform/blobs.py` `QUOTE_INPUT_BLOB_COLUMNS` | one entry | none found | — | none |
| `backend/src/app/worker/entrypoint.py` | one call appended | **PL 9716** registers in `register_rate_table_handlers`, not here | no | none |
| `docs/contracts/openapi/generated.json`, `docs/INDEX.md` | regenerated | every slice that changes a shape | — | exempt (generated) |

**Same-Work pairs, RL 9620 condition 2, both ways.** With **SL-1387** (Slice 3): this slice
consumes its output, so they are serial. With **SL-1389 / SL-1390** (Slices 5, 6): they
consume this slice's row (`DislocationRunRow`, `fetch_run`), so they are serial after it. With
**PL 9649** (SL 9647): (a) `_Resolver` SERIALISES; so serial. With **PL 9688** (SL 9685): no
shared path in either write set (it writes `03` FR-221 `:107` and `pricing-core` files), and
neither consumes the other's output; (a) and (b) both hold, so they may run at once if the
dispatch record says so.

### Size

About one and a half executor days: one migration, one table, one handler, two or three
routes, a pure move, and the contract registration. No measurement window (the cost figure is
Slice 3's).

## Needs this slice serves (PL 9629 #1164, its step table)

| Need | Step | What this slice provides |
|---|---|---|
| G2, PL 9629 activation need 4 | D6 `POST /dislocation-runs` → 202; run persisted | Tasks 4, 5 |
| G2, need 4 with need 3 | D7–D8 the run's segments, movers and attribution, persisted and cited by id | Tasks 2, 4 |
| G2, need 4 | E4 re-run dislocation, resubmit → 202, then accepted | Task 5 (the resubmit's acceptance is Slice 5's) |
| G1 | WK-673 resolved, with every slice closed | this slice |
| WK-675 Slice 8 | the Dislocation view reads `GET /dislocation-runs/{id}` | Task 5 |

PL 9629's D6 actor is the Analyst (`WF-699` D6, `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:86`).
DP-S4-2 (a) would refuse it with 403; this is why DP-S4-2 recommends (b).

## Decision points

Kind and blocking per `document-ids.md` §1.7. Rows of kind "decision point" are the
decision-maker's, resolved in one ruling that also adopts or amends the Appendix texts. The
slice may not move `draft → active` while any blocking row is open.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S4-1 | **Is the attribution fanned out across workers?** `PL-1267` Slice 4 says "the subset re-rates fanned out across workers"; `SL-1388`'s row does not. `attribute` (Slice 3) rates all 2^K subsets inside one call, so a fan-out needs it split into per-subset rating and assembly, an `03` §5.2 change to Slice 3's interface | (a) **one Job**: the handler calls `attribute` once; no fan-out in this slice; the fan-out becomes an owned follow-up only if Slice 3's measured figure for K = 6 on the full portfolio (derived, PL 9689 DP-S3-10 (b)) exceeds a Job duration the decision-maker names. (b) **child Jobs per subset**: a new `JobKind`, `attribute` split into `rate_subset` and `assemble_attribution`, an `03` §5.2 amendment and a Slice 3 interface change. (c) a process pool inside one worker (not "across workers") | **(a).** It keeps `pricing-core` unedited, uses Slice 3's surface as merged, and decides the fan-out on a measured figure rather than in advance. (b) reopens Slice 3's interface and adds a Job kind for a cost not yet measured. (a) narrows `PL-1267` Slice 4's text, so the ruling also routes that delta to the maintainer, as a dispatch-record delta against frozen `PL-1267` | decision point | yes — Task 4 | open |
| DP-S4-2 | **Which permission starts a run?** `PL-1267` names `score:batch` as the likely pick. No built-in human role holds it (premise i), and WF-699 D6's actor is the Analyst | (a) `score:batch` (a batch re-rate; a Service Account may hold it). (b) `rating:compile`, as `start_regression_run` (`models.py:1276`), the other run started against a Rating Version; `analyst` and `pricing_actuary` hold it. (c) `rating:read` | **(b)** for `POST`, plus `dataset:read` on the portfolio Dataset Version; **`rating:read`** for `GET`. (a) refuses D6's actor, and fixing that grants a role a new capability (a scope change). (c) lets a read-only principal spend worker-hours. FD-1197 is cited; this slice adds no name and does not settle FD-1197's name disagreement | decision point | yes — Task 5 | open |
| DP-S4-3 | **How are the movers read?** A movers row carries every portfolio column (`03:1124`), so the blob is a quote-input store (NFR-499); FR-263 asks for "drill-down to individual quotes" | (a) register `dislocation_runs.movers_blob_sha256` in `QUOTE_INPUT_BLOB_COLUMNS`; no route reads the blob in this slice; the read route is owned by WK-675 Slice 8, the view that needs it. (b) as (a), plus `GET /api/v1/dislocation-runs/{id}/movers` (`rating:read`), the regression case-log precedent (`03` §5.1 `…/regression-runs/{run_id}/cases`, FR-1221), with a new `03` §5.1 row. (c) leave it on the generic blob route | **(b).** A blob nothing can read is not a drill-down, and the precedent is exact; the route is small. (b) adds a route `SL-1388`'s row does not name, so the ruling records it as within FR-263. (c) breaks NFR-499 | decision point | yes — Tasks 2, 5 | open |
| DP-S4-4 | **How does a worker get an `ArtifactResolver`?** `_Resolver` is nested in `compile_rating_version` (premise f) | (a) move it to module level as `WorkspaceResolver(session, workspace_id)`, unchanged in body; `compile_rating_version` instantiates it. (b) a second resolver in the handler, duplicating the branches | **(a)**: one resolver, so a subset resolves exactly as a real compile does (FR-1398). (b) would let the two drift, the mispricing `CLAUDE.md` §2 warns of | slice design (planner) | no | **decided (a)** here; sequencing in §"Contention" |
| DP-S4-5 | **How is the estimated rating count shown before launch?** `RL-1264` item 3; PL 9689's P4: "so a caller can show it before launch" | (a) `POST /api/v1/dislocation-runs/estimate` takes a `DislocationSpec`, answers 200 with a new `DislocationEstimate` (`derived_changes`, `policies`, `estimated_ratings`, `method`), writes no Job; a new `03` §5.1 row. (b) the 202 body carries the estimate (after launch, not before). (c) a `dry_run` field on `DislocationSpec` (a shape change on the spec every run carries) | **(a).** Only (a) answers before launch without changing the run's own shape. The partition check runs in the same code path, so a bad grouping is refused at the estimate too | decision point | yes — Task 5 | open |

## Tasks

### Task 0: Preconditions (no code)

**Files:** the slice ledger `docs/ledgers/LG-<working id>-….md` (the executor's).

- [ ] **Step 1:** Confirm each activation need at the dispatch tree:
  `git -C <worktree> log -1 --format='%H %aI' origin/main`; the DP ruling resolves
  (`grep -l '^id: RL-<n>' docs/rulings/*.md`); this plan is `active`; `SL-1387` is `closed`
  and `SL-1388` `active` in `docs/roadmap.md`.
- [ ] **Step 2:** `uv sync --all-packages`; record the Alembic head
  (`uv run alembic heads` from the repository root, `alembic.ini`, with the DSN `dev-commands` gives).
- [ ] **Step 3:** Contention, re-run and recorded:
  ```bash
  git fetch -q origin
  gh pr list --state open --json number,headRefName --jq '.[] | "\(.number) \(.headRefName)"'
  grep -n -B3 "^status: active" docs/roadmap.md | grep "id: SL"
  git diff --name-only origin/main...origin/<each active slice branch>
  git grep -n "class _Resolver\|class WorkspaceResolver" -- backend/src/app/platform/rating_versions.py
  ```
  Record whether PL 9649, PL 9610 and A-1 have merged. If any of them is **active and
  unmerged**, stop: Task 3's move SERIALISES with it (§"Contention").
- [ ] **Step 4:** Read Slice 3's merged surface and copy into the ledger, with line numbers:
  the signatures of `derive_changes`, `attribute`, `estimate_attribution_ratings`, the
  `AttributionError.code` values, and `DislocationRun`'s four attribution fields. Every later
  step uses the ledger copy where it differs from this plan.
- [ ] **Step 5:** Copy the DP ruling's texts into the ledger with their minted ids; re-count
  each find string with `grep -cF` on the dispatch tree (each must be 1).
- [ ] **Step 6:** Baseline `uv run pytest backend/tests/test_rating_version_compile.py
  backend/tests/test_regression_runs.py backend/tests/test_contracts.py -q` and the four docs
  checks on the untouched tree; record rc and the summary lines.

### Task 1: Spec — the ruled texts and the error code

**Files:**
- Modify: `docs/specs/03-rating-engine.md` (§5.1 `:919-920`, and the new rows the ruling adopts)
- Modify: `backend/src/app/errors.py` (`RATING_ERROR_CODES`, `:309`)
- Test: `backend/tests/test_dislocation_runs.py` (new)

**Interfaces:** Produces the code `ATTRIBUTION_RECONCILIATION_FAILED` in `RATING_ERROR_CODES`,
which Task 4's handler raises through `PlatformError`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_dislocation_runs.py
from app.errors import RATING_ERROR_CODES


@pytest.mark.req("FR-1397")
def test_the_reconciliation_failure_code_is_registered() -> None:
    assert "ATTRIBUTION_RECONCILIATION_FAILED" in RATING_ERROR_CODES
```

Mirror the `req` marker import and the module's fixtures from
`backend/tests/test_regression_runs.py` (`:9-21`) rather than this sample.

- [ ] **Step 2:** Run `uv run pytest backend/tests/test_dislocation_runs.py -q`. Expected:
  FAIL on the `assert`, the name absent from the set. An `ImportError` is a plan defect.
- [ ] **Step 3:** Append `"ATTRIBUTION_RECONCILIATION_FAILED",` to `RATING_ERROR_CODES` and
  apply the ruling's §5.1 texts verbatim (the ledger copy).
- [ ] **Step 4:** Run the test (PASS) and `python3 scripts/audit-docs.py` (only check 31 may
  fail while ids are working ids; any other failure is a stop).
- [ ] **Step 5: Commit** `feat(rating): register ATTRIBUTION_RECONCILIATION_FAILED; 03 §5.1 dislocation rows (SL-1388)`.

### Task 2: The persisted row, its single writer, and the movers deny

**Files:**
- Modify: `backend/src/app/db/models.py` (append `DislocationRunRow` after the last class)
- Create: `backend/migrations/versions/<rev>_dislocation_runs.py`
- Create: `backend/src/app/platform/dislocation_runs.py`
- Modify: `backend/src/app/platform/blobs.py` (`QUOTE_INPUT_BLOB_COLUMNS`, `:496-499`)
- Test: `backend/tests/test_dislocation_runs.py`

**Interfaces:**
- Produces: `DislocationRunRow` (`__tablename__ = "dislocation_runs"`): `id` (UUID7 primary
  key, `default=new_uuid7`), `workspace_id`, `run` (JSONB, the `DislocationRun`),
  `baseline_ref` and `candidate_ref` (`String(100)`), `baseline_bundle_hash` and
  `candidate_bundle_hash` (`String(71)`), `portfolio_dataset_version_id` (UUID),
  `movers_blob_sha256` (`String(64)`), `job_id` (UUID, unique), `created_at`, `created_by`;
  indexes on (`workspace_id`, `candidate_ref`, `candidate_bundle_hash`) for Slice 5's
  lookup, and on `movers_blob_sha256`.
- Produces: `async def persist_run(session, *, workspace_id: UUID, run: DislocationRun,
  baseline_bundle_hash: str, candidate_bundle_hash: str, actor_id: UUID) -> DislocationRunRow`
  (the single writer; every copied column taken from `run` in the same call) and
  `async def fetch_run(session, *, workspace_id: UUID, run_id: UUID) -> DislocationRunRow`
  (404 `NOT_FOUND` for an unknown id or another workspace's).

Mirror `RegressionRunRow` (`models.py:2178-2215`) and `platform/regression_runs.py`
(`persist_run` `:27`, `fetch_run` `:51`) for column types, docstring and the scalar-digest
reason; do not reinvent them.

- [ ] **Step 1: Write the failing tests** — `test_the_scalar_movers_digest_equals_the_runs_movers_blob`,
  `test_fetch_is_scoped_to_the_workspace`, and Acceptance 2's
  `test_the_generic_blob_route_refuses_a_movers_blob` (persist a row whose movers digest names
  a stored blob, then `GET /api/v1/blobs/{sha256}` as the run's own workspace: 404).
- [ ] **Step 2:** Run them. Expected: FAIL at import (`DislocationRunRow` undefined) for the
  first two; after Step 3 the third must still fail **by answering 200** until Step 4. A 404
  for another reason (no owner row) is a plan defect: give the blob an owner in the test as
  `blob_readable_by` (`blobs.py:508-530`) requires.
- [ ] **Step 3:** Write the class, the migration (`down_revision` = the Task 0 head) and the
  service. Run `uv run alembic upgrade head` against the dev DSN.
- [ ] **Step 4:** Append `DislocationRunRow.movers_blob_sha256` to `QUOTE_INPUT_BLOB_COLUMNS`
  and extend its comment by one clause naming FR-263's movers.
- [ ] **Step 5:** Run the three tests (PASS) and `uv run pytest backend/tests/test_regression_runs.py -q` (unchanged).
- [ ] **Step 6: Commit** `feat(dislocation): the dislocation_runs row, its single writer, the movers deny (FR-265, NFR-499)`.

### Task 3: The workspace resolver, moved (DP-S4-4)

**Files:**
- Modify: `backend/src/app/platform/rating_versions.py` (`_Resolver`, `:445-555`; `compile_rating_version`, `:423-577`)
- Test: `backend/tests/test_dislocation_runs.py`

**Interfaces:** Produces `class WorkspaceResolver` with `__init__(self, session: AsyncSession,
workspace_id: UUID)` and `async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact`, the
nested class's body unchanged. Produces `class PreloadedResolver` (in
`backend/src/app/worker/dislocation_handlers.py`): built from a `dict[ArtifactRef,
ResolvedArtifact]`, `resolve` returns the entry or raises `ValueError("NOT_FOUND: …")`.

- [ ] **Step 1: Write the failing test** `test_the_preloaded_resolver_serves_exactly_both_versions_pins`:
  build `PreloadedResolver` from two `RatingVersion`s' algorithm refs and pins via
  `WorkspaceResolver`; every pinned ref resolves, a ref neither pins raises.
- [ ] **Step 2:** Run it. Expected: FAIL at import (`WorkspaceResolver` undefined).
- [ ] **Step 3:** Move the class out unchanged (cut and paste, then make its closure
  variables, `session` and `workspace_id`, constructor arguments). Nothing else in the body
  changes.
- [ ] **Step 4:** Run the test (PASS) and Acceptance 11 (`test_rating_version_compile.py`
  unmodified, PASS). `git diff -w` on the class body shows only the indentation and the two
  constructor lines.
- [ ] **Step 5: Commit** `refactor(rating): lift the compile resolver to WorkspaceResolver (no behaviour change)`.

### Task 4: The `dislocation.run` handler

**Files:**
- Create: `backend/src/app/worker/dislocation_handlers.py`
- Modify: `backend/src/app/worker/entrypoint.py` (`:70-74`)
- Test: `backend/tests/test_dislocation_runs.py`

**Interfaces:**
- Consumes: `WorkspaceResolver`, `PreloadedResolver` (Task 3); `persist_run` (Task 2);
  `dislocation_frame`, `select_movers`, `summarise_dislocation` (`analysis.py:177`, `:264`,
  `:325`); `derive_changes`, `attribute`, `AttributionError` (Slice 3, the ledger copy).
- Produces: Job parameters `{**job_identity(caller), "spec": DislocationSpec.model_dump(mode="json")}`;
  `JobResult(kind="artifact", ref=f"dislocation_run:{row.id}")`; `register_dislocation_handlers()`.

The handler, in order:
1. `prepare()` in one `run_on_loop` call: load both Rating Versions by ref
   (`resolve_rating_version_ref`, `rating_versions.py:169`), refuse with 409
   `BUNDLE_COMPILE_FAILED` if either has no compiled bundle (the regression handler's text,
   `rating_handlers.py:150-155`), read both bundles (`load_bundle`), read the portfolio
   Dataset Version's table (as `scoring_handlers.py:319-353`), and resolve every pinned ref of
   both versions through `WorkspaceResolver` into a `PreloadedResolver`.
2. On the worker thread: `frame = dislocation_frame(b, c, portfolio, spec)`;
   `run = summarise_dislocation(frame, spec)`; `movers = select_movers(frame, spec)`.
3. Attribution, per DP-S4-1 (a): `asyncio.run(attribute(baseline_v, candidate_v, portfolio,
   spec, preloaded))` on the worker thread (no database I/O inside it); its fields set on
   `run`. An `AttributionError` becomes `PlatformError(exc.code, …, 422, str(exc))`.
4. `persist()` in one unit of work: the movers frame written as Parquet to the blob store,
   `largest_movers_blob` and `job_id` set, `persist_run` called.

Resumability: no partial row is ever written (step 4 is one transaction); a re-submission
recomputes, and Acceptance 8 shows the result is byte-identical; blob writes are
content-addressed, so a repeated `put` is idempotent.

- [ ] **Step 1: Write the failing tests** — Acceptance 1, 3, 5 and 8, using the Slice 3
  fixture `examples/fremtpl2/rating/` (PL 9689 DP-S3-6 (a)) or the smaller score fixture
  Slice 3's tests use, whichever its ledger names as fast.
- [ ] **Step 2:** Run them. Expected: FAIL with `KeyError`/"no handler" for
  `JobKind.DISLOCATION_RUN` from `handler_for` (`handlers.py:42`). Any other first failure is
  a plan defect.
- [ ] **Step 3:** Write the handler and register it.
- [ ] **Step 4:** Run the tests (PASS). For Acceptance 3, break the handler deliberately to
  persist one subset bundle as a `RatingVersionRow`; the test must fail naming the row count;
  revert; quote both in the ledger.
- [ ] **Step 5: Commit** `feat(dislocation): the dislocation.run handler, attribution in one Job (FR-263, FR-265, FR-266, FR-1398)`.

### Task 5: The routes

**Files:**
- Create: `backend/src/app/api/dislocation_runs.py`
- Modify: `backend/src/app/main.py` (one `include_router`)
- Modify: `packages/model-schema/src/model_schema/dislocation.py`, `__init__.py` (DP-S4-5 (a) only: `DislocationEstimate`)
- Test: `backend/tests/test_dislocation_runs.py`

**Interfaces:**
- `POST /api/v1/dislocation-runs`: body `DislocationSpec`; the ruled permission (DP-S4-2) and
  `dataset:read` on the portfolio Dataset Version; runs `derive_changes` and the partition
  check before submitting (422 `VALIDATION_FAILED`, naming each change left out or placed
  twice); 202, `Location: /api/v1/jobs/{job.id}`, body the `Job`.
- `GET /api/v1/dislocation-runs/{id}`: `rating:read`; 200 `DislocationRun`; 404 `NOT_FOUND`.
- Under DP-S4-3 (b): `GET /api/v1/dislocation-runs/{id}/movers`, `rating:read`, the Parquet
  rows as JSON, mirroring `get_regression_run_cases` (`models.py:1337`).
- Under DP-S4-5 (a): `POST /api/v1/dislocation-runs/estimate`, the same permissions and
  checks as `POST`, 200 `DislocationEstimate`, no Job.

- [ ] **Step 1: Write the failing tests** — Acceptance 4, 6 and 7, and the movers route's
  200 and 403 under DP-S4-3 (b).
- [ ] **Step 2:** Run them. Expected: 404 from the router (the path is unregistered). A 405 or
  422 is a plan defect.
- [ ] **Step 3:** Write the router, mirroring `start_regression_run` and `get_regression_run`
  (`models.py:1269-1335`) for the dependency form and the 202 headers.
- [ ] **Step 4:** Run the tests (PASS).
- [ ] **Step 5: Commit** `feat(api): POST and GET /dislocation-runs (FR-263, FR-265; RL-1264 estimate)`.

### Task 6: The generated contract

**Files:** `scripts/generate-contracts.py` (`GENERATED_SHAPES`, `:38`);
`backend/tests/test_contracts.py` (`COMPARED_SLUGS`, `ONE_SIDED_SLUGS`); generated files.

- [ ] **Step 1:** Move `"dislocation-run"` from `ONE_SIDED_SLUGS` to `COMPARED_SLUGS` first,
  and run `uv run pytest backend/tests/test_contracts.py -q`. Expected: FAIL in the
  every-one-sided-slug or compared-pair test, naming `dislocation-run` as having no generated
  side.
- [ ] **Step 2:** Add `"dislocation-run": "DislocationRun",` to `GENERATED_SHAPES`; run
  `uv run python scripts/generate-contracts.py`; rerun the test.
- [ ] **Step 3:** If the comparison reports a field-type disagreement between the authored
  and generated sides, **stop** and report both sides to the lead (Global Constraints). Do not
  edit either side.
- [ ] **Step 4:** `uv run python scripts/generate-contracts.py --check` (exit 0);
  `pnpm --dir frontend generate:api` (the client regenerates; nothing is committed under
  `frontend/src/api/generated`).
- [ ] **Step 5: Commit** `feat(contracts): generate and compare dislocation-run (PL-1267 Acceptance 6)`.

### Task 7: The gate and the ledger

- [ ] **Step 1:** The full two-half gate (`dev-commands`) on the slice head; `generate-contracts.py
  --check`; the four docs checks; `req-coverage.py`. Quote every rc and summary line with the
  tree.
- [ ] **Step 2:** The ledger: Task 0's records, every red quoted by its cause, Acceptance
  1–13 each with its evidence, and `LG-1400` Task 7 rows 1 and 3 discharged by name.

## Hand-off

The executor works in its own worktree on a branch from origin/main after `SL-1387` merges,
spawned from `.claude/roles/executor.md` with this plan and the dispatch record. The slice
closes on a clean audit and the lead's merge. **Slice 5 (`SL-1389`) inherits:**
`DislocationRunRow` and `fetch_run`, the (`workspace_id`, `candidate_ref`,
`candidate_bundle_hash`) index for its limb (2) lookup, and `RatingVersionEvidence.dislocation_run_id`
(`model_schema/rating.py:125`) to fill. **WK-675 Slice 8 inherits:** the two (or four) routes.
**From Slice 3, received:** the backend registration of `ATTRIBUTION_RECONCILIATION_FAILED`
(Task 1), `test_dislocation_subset_bundles_never_become_rating_versions` (Task 4), the route's
422 for a bad partition (Task 5), the contract's generation (Task 6), and the measured cost
(DP-S4-1).

## Appendix — proposed texts (for the ruling to adopt, amend or reject)

### P1 — `03` §5.1, the two rows at `:919-920` (DP-S4-2 (b), DP-S4-3 (b), DP-S4-5 (a))

Replace the two rows with:

```markdown
| `POST` | `/api/v1/dislocation-runs` | **202** Baseline vs candidate over a portfolio (FR-263), with attribution where the versions differ in more than one respect (FR-266); body a `DislocationSpec`; requires `rating:compile` and `dataset:read` on the portfolio Dataset Version; 202 with the `Job`; **422** `VALIDATION_FAILED` when the change groups do not partition the derived changes (FR-1399), naming each change; the Job ends `failed` with `BUNDLE_COMPILE_FAILED` (a subset, FR-1398) or `ATTRIBUTION_RECONCILIATION_FAILED` (FR-1397). *(Amended <date>, WK-673 Slice 4, RL-<n>.)* |
| `POST` | `/api/v1/dislocation-runs/estimate` | The rating count a run with this `DislocationSpec` would perform (`RL-1264`'s feasibility rule), before launch; the same permissions and the same 422 as the run; **200** with a `DislocationEstimate`; no Job. *(Added <date>, WK-673 Slice 4, RL-<n>.)* |
| `GET` | `/api/v1/dislocation-runs/{id}` | Dislocation artifact (FR-265); requires `rating:read`; **404** `NOT_FOUND` for an unknown id or another workspace's. *(Amended <date>, WK-673 Slice 4, RL-<n>.)* |
| `GET` | `/api/v1/dislocation-runs/{id}/movers` | The run's movers (FR-263's drill-down); requires `rating:read`; the only route that reads this blob, which `GET /api/v1/blobs/{sha256}` refuses (NFR-499). *(Added <date>, WK-673 Slice 4, RL-<n>.)* |
```

`<date>` is the code commit's date and `RL-<n>` the ruling's minted id. Under DP-S4-2 (a) the
first row names `score:batch`; under DP-S4-3 (a) or DP-S4-5 (b) or (c) the corresponding new
row is dropped.

## Self-review

1. **Spec coverage.** FR-263, FR-265 → Tasks 2, 4, 5. FR-266, FR-1398 → Task 4. FR-1397 →
   Tasks 1, 4. FR-1399's partition at the route → Task 5. NFR-495 → Task 4 (Acceptance 8).
   `RL-1264` item 3 → Task 5 (DP-S4-5). `PL-1267` Acceptance 6 → Task 6. `LG-1400` Task 7
   rows 1 and 3 → Tasks 4, 5.
2. **Placeholder scan.** `<date>`, `RL-<n>`, `<rev>` and `LG-<n>` are values fixed at the
   code commit, the mint and the executor's ledger; each is named where it is filled. The
   `<ruled permission>` in Acceptance 6 is DP-S4-2's outcome.
3. **Type consistency.** `WorkspaceResolver`, `PreloadedResolver`, `DislocationRunRow`,
   `persist_run`, `fetch_run`, `DislocationEstimate` and `movers_blob_sha256` are spelled the
   same in Interfaces, Steps and Acceptance (grepped).
4. **Rulings between sweep and filing.** `gh pr list --state open` read at 16:54 BST: RL 9614
   (#1167) keeps FR-257's gate at the submit route (not this slice's); RL 9620 (#1162) is the
   same-Work rule applied above; no open PR rules on FR-263, FR-265 or `03` §5.1's dislocation
   rows. The maintainer's entry "2026-10-05 16:43:31 BST" (Option A) adds A-1's `_Resolver`
   peril branch, which §"Contention" serialises.
5. **Found, outside this slice, for the lead.** PL 9629's need 5 attributes WF-699 E1
   ("change summary drafted from the structural and rate diffs", `03` FR-242's draft) to
   Slice 5; `SL-1389` and `PL-1267` Slice 5 do not scope it. Reported, not changed here.
