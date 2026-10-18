---
id: LG-9810
family: ledger
title: WK-674 slice SL-1258 — Slice 4, the deployment path (PL-1537 row 1 and PL 9921 changes) (slice ledger)
status: active                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-10-11
owner: executor
tree: d699a561d6a93f33b74beb9c07023f8e655bb8c7
phase: P2
work: WK-674
slice: SL-1258
plans: [PL-1537]
corrected_by: []
relates: [PL-1237, PL-1537, SL-1258, FR-412, FR-415, FR-434, FR-435, FR-437, FR-452, NFR-531, NFR-534, FD-1211]
---

# LG-9810 — WK-674 slice SL-1258: Slice 4, the deployment path

Working id 9810 (lead-reserved); minted with its batch. Executed by `executor-wk674s4`, base
`origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7`, branch `sl-1258-wk674-s4`. **This slice is
AUTHORED, not activated:** no GO has been relayed and no gate has run (brief wave 2,
2026-10-11). PL 9921 (working id) is not minted; this ledger cites it by working id until it
is, and `PL-9921`'s changes for this slice are D0.1 to D0.3 and D4.1 to D4.3.

**GO:** not yet given.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Quoted from `PL-1537` row 1 (Tasks table) and its R4.1 to R4.3, with `PL-1237` Task 4: the compose
`api` service run as n replicas behind a stated load-balancing topology; a `worker` service to
which FR-412's memory half is applied; `api` with no compute pool (FR-434, NFR-534); migrations as
a pre-deploy step (FR-435, NFR-531); FD-1211's process lifecycle; the reference Keycloak
(FR-437); the load harness. Requirements, each id: FR-434, FR-435, FR-437, FR-412 (memory half),
FR-415 (worker service), FR-452 (management-API limb), NFR-531, NFR-534, register FD-1211.
PL 9921 changes for this slice: D0.1 (S4 on P2's exit path), D4.1 (R4.1 re-derived against S3's
limiter at the base), D4.2 (the harness prints issued and offered rate and the error count; a
short run is void), D4.3 (shared paths named at GO).

### Task list

- [x] A — FR-412 memory half: `resource_budget.memory_gb` read by the worker, typed error names
  the budget (`26604844`). Acceptance: `backend/tests/test_job_memory_budget.py`. **Not run.**
- [x] B1 — `deploy/Dockerfile` (one image, three roles), compose `migrate`, `api`, `worker`, `lb`
  behind the `app` profile, `deploy/lb.conf`, `.dockerignore`, shape tests
  `backend/tests/test_deploy_stack.py` with broken-input proofs (`d6ce0b82`). **Not run, not built.**
- [x] B2 — `scripts/bench-deploy-path.py` (R4.3, D4.2) and its record tests (`b5b9a335`). **Not run.**
- [x] B3 — NFR-534 and NFR-531 runtime proofs behind `GIP_DEPLOY_TESTS=1`,
  `deploy/docker-compose.isolated.yml` (`5d290f32`). **Not built, not run.**
- [x] B4 — FD-1211: design stated in compose (finalize, then replace); 25-run clean-exit test and
  its abort check (`1cebdade`). **Not run.**
- [x] B5 — FR-437 reference Keycloak under `deploy/keycloak/` with README (`b7b41063`). **Not run.**
- [ ] C — FR-452 management-API limit (R4.1, D4.1). **PARKED:** it re-derives against S3's limiter,
  which is not on main (`sl-1257-wk674-s3-env`). Lead's ruling: parked until S3 merges.
- [ ] D — closing acts, D4.3 shared-path census at GO, `deploy/README.md` section for the `app`
  profile.

### Gate

Not run. The full two-half gate runs only on the lead's grant for the final head.

### Audit

Not yet.

### Build log

- 2026-10-11: Tasks A and B1 to B5 authored and pushed per piece, without running any test or
  building any image (gate-1 held by another seat, load above 4.0; lead's instruction).
  Red-first for Task A could not be seen: at the parent the tests would fail on the absent
  `_resident_bytes`, not on a 3 GiB job proceeding.
- Decision recorded for the reader: `yaml` is imported directly by `test_deploy_stack.py`;
  PyYAML is a runtime dependency of `uvicorn[standard]`, declared by `backend/pyproject.toml`.
- Compose uses `${GIP_BUILD:-unset}`, not `:?`, because compose interpolates the whole file and
  the default `up` must keep working; the Dockerfile refuses a non-SHA build argument.

## Obligations carried into this slice (dated 2026-10-16, at `origin/main` `0877e6e7`)

- **E4.3's seeded ingest test is this slice's to convert.**
  `test_a_dataset_ingest_job_succeeds_through_the_compose_io_worker`
  (`backend/tests/test_deploy_stack_runtime.py`, from PL-1714 E4.3) seeds the blob and its owner by
  `psql`-style insertion (`_seed_blob_inputs`), because the public upload path has no completion step
  until SL-1722 merges (PL-1721 P10; the maintainer's (by delegation) entry "2026-10-14 11:10:26 BST"
  item (b)). Its docstring names the conversion. **Owner of the conversion: SL-1258**, on the
  maintainer's (by delegation) entry "2026-10-16 09:40:20 BST" ("SL-1258's plan must carry it"):
  once SL-1722 is on `main`, the test is rewritten to upload-url, PUT, complete, POST versions, with no
  seeding. If SL-1722 has not merged by the 4 Nov freeze, the P2 closure record lists the seeded test
  as an open item. PL-1714 line 73 words the conversion as an acceptance line "in SL-1722, not this
  delta's"; that wording and the 09:40:20 entry differ on the owner. PL-1714 is not edited by this
  ledger; the lead routes the reconciliation (a PL-1714 plan delta or a ruling).
- **Shared paths with SL-1722:** `backend/src/app/worker/entrypoint.py` (S4: E4.4, E4.6, E4.7 (a); SL-1722:
  the `blob.promote` handler) and `backend/src/app/platform/jobs.py` (SL-1722: `BLOB_PROMOTE` route; S4
  only under DP-Q4 (a) or E4.7, DP-Q4 ruled (b) at 10:43:43 BST). Whichever of the two merges second
  re-merges `origin/main` and re-runs the other's guard (`test_worker_handler_coverage.py` must see
  `blob.promote` registered).

## Activation (dated 2026-10-16, at `origin/main` `0877e6e7`)

The activation commit flips `PL-1666`, `PL-1690` and `PL-1714` from `draft` to `active` by their
status lines only (§1.5: a filed plan is frozen). Each trigger, from the maintainer's (by
delegation) entry "2026-10-16 09:55:22 BST — GO SL-1258 BUILD (WK-674 S4, compose stack +
FD-1713)" and the lead's "2026-10-16 09:54:55 BST" GO request:

- **PL-1666:** RL-1687 ("What it does not change", around :268) owes it `active` "by its own
  dated line" once RL-1687 is minted (minted in D14); PL-1690:130 repeats it. RL-1687 is on main.
- **PL-1690:** its "Decision points" read "None open"; DP-S4-1 is RL-1687's, DP-B1 the lead's.
- **PL-1714:** its decision points are all ruled (DP-Q1 (b), DP-Q2 (a), DP-Q3 (a), DP-Q4 (b), DP-Q5
  (a); the maintainer's (by delegation) entries of 2026-10-14 10:36:42 and 10:43:43 BST).
- **PL 8061** (the PL-1714 delta, unminted) flips once minted, not here.

**DP-E1 (ruled 2026-10-16 09:55:22 BST, condition 3):** no second PR under SL-1258's id. E4.8 is
not built here. At S4's PR time the lead picks (a) wait for SL-1722 and carry E4.8, or (b) merge
seeded with E4.8 as its own slice id.

## Build log, 2026-10-16

- Code written without running any test (condition 2: no extra load until SL-1455's GATE END):
  `deploy/docker-compose.yml` (one `worker-*` service per pool, sizes UNMEASURED, env-overridable),
  `RELAY_QUEUE` read by `task_default_queue` and the beat entry, `register_trace_handlers()` in
  the entrypoint (E4.7 (a)), entrypoint docstring (E4.6), `scripts/demo.py` queues derived from
  the routing table (E4.5), `BLOB_GC` in `LATER_PHASE_KINDS` (its FR-420 line is on main), the
  `rating.compile` runtime test asserting `succeeded` plus a result ref, and the shape/runtime tests
  adapted to the `worker-*` names. No migration (S4 adds none; verified: no file under
  `backend/migrations` is touched).
- **Not done:** PL-1690 E4.1 (Task C, FR-452 management-API limit; RL-1687) is not in the lead's
  dispatch (E4.2 to E4.7); see the report to the lead.

## Finding (b), 2026-10-16 10:09 BST: three routes are counted before their in-handler permission check

Read at `origin/sl-1258-wk674-s4` HEAD `9bbdd145`. `_count_management_request`
(`backend/src/app/api/authz.py:66`) is run by `counted_caller()` (`authz.py:93`, counts at once,
checks no permission) and by `requires()` (`authz.py:103`, counts at `authz.py:130`, after its own
permission check). A route that checks its permission inside the handler uses `counted_caller()`, so
the count runs first. Three POST routes do:

| Route | Dependency | In-handler permission check |
|---|---|---|
| `POST /validation-rules` | `AuthenticatedCaller = Depends(counted_caller)` (`api/validation.py:69`, used `:273`) | `platform/validation_rules.py:212` (`admin:manage_settings`, `sql` rule) or `:219` (`dataset:write`), in `create_rule` (`:185`) |
| `POST /environments/{env}/deployment-requests` | `AnyCaller = Depends(counted_caller)` (`api/deployments.py:38`, used `:50`) | `_authorised_environment` (`platform/deployments.py:77`, `deployment:promote` at `:84`), called from `submit_request` at `:224` |
| `POST /environments/{env}/deployments` | `AnyCaller` (`api/deployments.py:38`, used `:75`) | the same `_authorised_environment`, called from `deploy` at `:455` |

Counted for a caller later refused `403`: one management request, in the (Environment, Principal)
one-second window, before the refusal. The `403` still goes out; the refused call also uses a unit of
the caller's allowance. A caller without the permission can therefore exhaust its own management
limit by repeated refused calls to these routes. This departs from `RL-1687`'s order, which counts
"after the route's own permission check" (`docs/rulings/RL-01687-*.md:150-153`, and the amendment
text at `:239`: "so a `401` or a `403` is never counted"). The `403` from a `requires()` route is
never counted; the `403` from these three is. The `authz.py:72-76` docstring says the same
("`counted_caller()` (a route with no permission)"), which these three routes are not.

**Not changed here:** no code is touched by this entry, and the test seeds are not rewritten
(DP-S4-SEED, pending with the maintainer).

**RL-1687 does not rule whether a `429` must be declared on these routes: UNRULED.**
`docs/rulings/RL-01687-*.md:304` ("## Raised to the lead (not ruled here)"), first bullet, `:306-309`:
"**Whether each counted route's OpenAPI entry declares `429`.** ... Recommendation: declare it by
one mechanism on the included routers, regenerated in the same commit ... It is not in DP-S4-1's
options, so it is put, not picked." These three routes declare `problems(401, 403, 409, 422)`
(`api/validation.py:270`) and `problems(401, 403, 404, 409, 422)` (`api/deployments.py:47`, `:72`);
none lists `429`. Owner of the ruling: the lead / the maintainer (by delegation).

## DP-S4-SEED (a): the runtime-test seeds go onto the governed path, 2026-10-16 10:18 BST

**Ruling (verified against `~/gi-pricing-plan.local/channel/to-lead.md`, entry "2026-10-16 10:08:52 BST", and item 1 of "2026-10-14 11:43:57 BST"):** the maintainer (by delegation) ruled (a). The defect is the direct DB write (`scripts/bench-rating.py::_seed`), whatever status it writes. (1) Batch and sampled-trace seed an `approved` Rating Version through `demo_model.create_approved_rating_version`. (2) Compile is created through the same services; it may stay a draft only if PL-1690 specifies compiling a draft. (3) The batch assert is `succeeded` and an output row count equal to the input's row count, read from the input. (4) `bench-rating.py::_seed` stays a bench tool; no runtime test imports it.

**Change (writing only; nothing run, a gate was held):** one file, `backend/tests/test_deploy_stack_runtime.py`.

- `_governed_workspace(approved, permissions)` (new, `:120-246` at this commit) replaces `rating._seed`. Principals: the demo seed's `grant_demo_principals`. Model: `test_demo_rating_evidence._approved_model` (as WF-699's `_world` builds it). Rate Tables and algorithm: `examples/fremtpl2/model.py` services. `approved=True` runs `create_approved_rating_version` (create, executed regression evidence, submit, two approvers decide); it then asserts the row's `status` is `approved`. The only direct rows left are the Service Account and its key (no route creates one with `score:execute`, FR-347). The `psql UPDATE service_accounts` widening is gone: the key is created with the permissions the test needs.
- `_scoring_request` (was `_seeded_scoring_request`): same return shape, now backed by the approved version. It serves `test_the_scoring_api_runs_and_scores_with_no_worker_service` and `test_previous_version_serves_the_migrated_schema_and_rolls_forward_with_no_failures`, which called the bench seed too; item 4 needs them off it.
- `test_a_score_batch_job_succeeds_through_the_compose_scoring_worker`: approved version; the frame is built from the governed quote's inputs; after `succeeded` it reads the job's summary blob and the output parquet from the store and asserts `output.height == frame.height` and `row_count == frame.height`. `frame.height` is the input's own height, not the literal 20, and the test asserts it is non-zero.
- `test_a_sampled_trace_is_produced_through_the_compose_scoring_worker`: approved version; the scored body is the governed quote.
- `test_a_submitted_job_reaches_a_terminal_state_through_the_compose_worker` (the compile test): **DRAFT, created by `rating_versions.create_rating_version`** through the service, not by `_seed`. **PL-1690 specifies no draft-compile line:** `docs/plans/PL-01690-*.md` E4.3 (`:90-109`) says "One cheap Job ... The executor names its kind and queue in the `LG-`", and names no status. By the ruling's own text the approved version would then be used, but **`POST /rating-versions/{id}/compile` refuses any non-draft with 409 `RATING_VERSION_IMMUTABLE`** (`backend/src/app/api/models.py:1297-1300` docstring, `require_compilable` at `:1306`, FR-239, RL-1379), so an approved version cannot be compiled. The draft is the only version this route accepts. Raised to the lead as an open question; the test's docstring cites both.
- `test_a_dataset_ingest_job_succeeds_through_the_compose_io_worker`: needs only a workspace and a key; it now takes them from the same helper (no bench seed). Its blob seeding (`_put_blob_inputs`, renamed from `_seed_blob_inputs`) is unchanged and stays SL-1722's to convert.
- Removed: `_bench()` and every `scripts/bench-*.py` import from the test.

**Grep (item 4), at this tree:**

- `git grep -n '\._seed(' -- backend/tests deploy` prints nothing (rc 1): no caller of a bench `_seed`.
- `git grep -n 'bench-rating\|bench_rating\|bench-deploy-path\|bench_deploy_path' -- backend/tests deploy` prints only `backend/tests/test_bench_deploy_path.py` (`:4`, `:15`, `:19`) and `backend/tests/test_bench_rating_calls.py` (`:1`, `:17`, `:20`): tests OF the bench tools, not runtime tests. `backend/tests/test_deploy_stack_runtime.py` is not in the output.
- The literal `git grep -n '_seed' -- backend/tests deploy` (as the ruling words it) is a substring match and prints 38 KB of unrelated module-local helpers (`_seed_approved_model`, `_seed_body`, `_seed_rate_table`, ...). In the runtime test it now prints only `from backend.tests.test_wf699_journey import _seed_module`, the demo seed's module loader, not the bench `_seed`. `git grep -n '\b_seed\b' -- backend/tests deploy` lists thirteen files, none of them `test_deploy_stack_runtime.py`.

**Owed after GATE END, on compose (with `lslocks` clean):** `GIP_DEPLOY_TESTS=1 GIP_N_SHA=<head> GIP_N1_SHA=<parent> uv run pytest -q backend/tests/test_deploy_stack_runtime.py` (all tests, because tests one and two moved too), plus `ruff check`, `mypy`, and the PL-1690 Acceptance 5 red run. None ran: the file is `py_compile`d only. Risks the run decides: (i) the rolling-upgrade test seeds with N's code against N-1's schema; (ii) pre-existing lines over 100 columns at `:392`, `:396`, `:503`, `:526` were not touched.

## DP-S4-SEED-2: three rulings on the runtime-test seeds, 2026-10-16 10:19:57 BST

**Ruling (verified against `~/gi-pricing-plan.local/channel/to-lead.md`, entry "2026-10-16 10:19:57 BST — Maintainer: DP-S4-SEED-2 (SL-1258 @7120d200)"):** the maintainer (by delegation) ruled three points.

1. **Compile on a SERVICE-created draft: ACCEPTED.** The compile test uses a draft made by `rating_versions.create_rating_version`. `POST /rating-versions/{id}/compile` refuses any status but `draft` (`backend/src/app/api/models.py` `compile_rating_version`, docstring `:1295-1300`, `require_compilable` at `:1306` at main, FR-239, RL-1379), which meets the 10:08:52 condition "only if the spec compiles a draft". This closes the open question raised in the DP-S4-SEED (a) section above.
2. **`rating.trace_sample_rate` by psql INSERT: REFUSED, not a recorded exception.** The sampled-trace test now sets it through the governed path: `PUT /api/v1/settings` (`backend/src/app/api/settings.py` `update_settings`, `:78`), body `{"values": {"rating.trace_sample_rate": 1.0}}`, permission `admin:manage_settings` (`ManageSettings`, `settings.py:34`). The key is declared at `backend/src/app/platform/settings.py:217` (FLOAT, 0..1), so the declaration's validation, the setting write and the `setting.updated` audit row all run. The test's own Service Account key is created with `admin:manage_settings` added (`_stack_with_workspace(extra_permissions=...)`), for this one test only. The test asserts the response's `effective_value` is `1.0`. No psql or direct write for this key remains.
3. **`add_approved` for the UPSTREAM Model only: ACCEPTED as a SCOPED exception, the ONE accepted direct write.** `backend/tests/approved_rows.py:78` `add_approved` writes approval-evidence rows directly (evidence written and flushed first, then the row), so it is not the governed decide path. It is reached through `test_demo_rating_evidence._approved_model` (`:150`, call at `:156`), which `_governed_workspace` calls. Reason: item 1 of the 2026-10-14 11:43:57 BST entry governs the Rating Version under test (governed at 7120d200), and WF-699's end-to-end `_world` builds its upstream Model with the same helper. The Rating Version and the compile, batch and trace subjects stay governed.

**Direct-write grep of `backend/tests/test_deploy_stack_runtime.py`** (`grep -n 'psql\|INSERT\|UPDATE\|session.add\|add_approved\|mark_approved'`, at this commit's tree):

| Hit | What it is | Verdict |
|---|---|---|
| `psql` / `INSERT` in the sampled-trace test (was `:610-612`) | `workspace_settings` row | REMOVED: replaced by `PUT /api/v1/settings` (ruling 2) |
| `:216`, `:218` `session.add(ServiceAccountRow / ApiKeyRow)` in `_governed_workspace` | the test credential | Separate, EARLIER-recorded exception (this ledger, DP-S4-SEED (a): no route creates a Service Account with `score:execute`, FR-347). NOT the "one" of ruling 3, which scopes the Model approval write; flagged to the lead for confirmation that 10:19:57 does not withdraw it |
| `:478` `session.add(DatasetVersionRow)` in `_put_blob_inputs` (ingest and batch blob seeding) | Dataset Version rows making the blobs readable | NOT covered by any ruling in 10:19:57; pre-existing, recorded above as SL-1722's to convert. FLAGGED to the lead |
| `:458` the word `psql` in `_put_blob_inputs`' docstring | prose only | not a write |
| `add_approved`, `mark_approved` | no hit in this file; the one use is in `test_demo_rating_evidence._approved_model` | ruling 3 |

**Owed after GATE END, on compose (with `lslocks` clean):** the whole `GIP_DEPLOY_TESTS=1` file (as in the DP-S4-SEED (a) section). The settings change is `py_compile`d only; the risk it leaves is whether the workspace-level value resolves for the key's environment `uat` (`api/score.py:544` resolves with `caller.environment`).

## Finding (b) fixed inside S4 (the maintainer, 2026-10-16 10:14:17 BST, "FIX INSIDE S4, no FD")

**Ruling (verified against `~/gi-pricing-plan.local/channel/to-lead.md`, entry "2026-10-16 10:14:17 BST — Maintainer: SL-1258 counted_caller before the in-handler 403 — FIX INSIDE S4, no FD"):** a defect in a slice's own unmerged code is fixed in the slice, and `git grep counted_caller origin/main -- backend/src` prints nothing, so there is no finding on main to file. Test first (red-first commit `5618a57b`), then the fix.

**The form chosen, one for all three routes: the handler's service calls the counter after its own permission check.** A new dependency `management_counter()` (`backend/src/app/api/authz.py`) authenticates the caller and returns an awaitable `count` without running it. The route passes it to the service as `count_management=`; the service awaits it on the line after `rbac.require_permission` (`platform/validation_rules.py::create_rule`, after both branches; `platform/deployments.py::_authorised_environment`, which both `submit_request` and `deploy` use, before the retired check). `_count_management_request` already runs at most once per request, so `requires()` plus this form cannot double-count.

**Why this form, not a dependency that checks first.** (1) The permission is not a function of the route alone: a `sql` rule needs `admin:manage_settings` and every other rule `dataset:write` (OQ-559, "instead", not "as well"), and the deployment check takes the Environment row, loaded by the path slug, as its resource. A dependency that checked first would need the body and a second Environment lookup, so the check would live twice (dependency and service) and the two could diverge. In the service it lives once. (2) The service's refusal order stays as `RL-1401` item 3 and `RL-1301` B.2 fixed it (G3 `422`, unknown slug `404`, then the permission), which a dependency running before the body is parsed would change. (3) The count still runs before any write: it sits inside the unit of work before the first row is created, so a `429` writes nothing.

**Counted now:** only a caller who holds the permission. A permitted call that then ends `404`, `409` or `422` is counted once (the check passed; `RL-1687` (1a) refuses to count only `401` and `403`). A `sql` rule refused `409` (the Setting is off) is refused before the permission check and so is not counted; that order is the service's and is unchanged.

**Tests** (`backend/tests/test_management_rate_limit.py`, beside the existing rate-limit tests): `test_a_403_from_an_in_handler_permission_check_is_not_counted` and `test_a_permitted_call_to_an_in_handler_permission_route_is_counted_once`, each parametrised over the three routes. The counter is read as the number of `limiter.admit` calls for the request, before and after: a `403` leaves it unchanged; the positive control moves it by exactly 1. Red-first: the commit `5618a57b` holds the tests alone. **Runs owed after GATE END** (no pytest while SL-1455's gate holds the box): the refusal tests red at `5618a57b` by their assert, green at the fix; the existing rate-limit tests; `ruff`, `mypy`.

**Sweep of every `counted_caller` route** (finding (b)'s third limb). Predicate, run at `7120d200` (the parent of the red-first commit): `git grep -n 'counted_caller' -- backend/src` lists the five consumer files (`api/approvals.py`, `api/demo.py`, `api/deployments.py`, `api/me.py`, `api/validation.py`) plus `authz.py`; in each, a route is counted when a handler parameter is typed with the alias bound to `Depends(counted_caller)` (`AnyCaller` in approvals, demo and deployments; `CallerDep` in `me.py`; `AuthenticatedCaller` in validation), counted by `git show 7120d200:backend/src/app/api/<file>.py | grep -cE '(caller): (AnyCaller|CallerDep|AuthenticatedCaller)\b'`; each handler body and the service it calls were then read for `rbac.require_permission`, `has_permission` and a hand-raised `403`. **9 routes, 3 defective (fixed above), 6 clean.**

| Route | Alias | In-handler permission check | Verdict |
|---|---|---|---|
| `POST /validation-rules` | `AuthenticatedCaller` | `platform/validation_rules.py::create_rule`, per rule kind | defective; fixed |
| `POST /environments/{env}/deployment-requests` | `AnyCaller` | `_authorised_environment` | defective; fixed |
| `POST /environments/{env}/deployments` | `AnyCaller` | `_authorised_environment` | defective; fixed |
| `POST /approval-requests` | `AnyCaller` | none; the docstring says submitting is ungated and `platform/approvals.py::submit` has no `require_permission` (the only three in that module are `set_policy`, `decide`, `withdraw`) | clean |
| `GET /approval-requests` | `AnyCaller` | none | clean |
| `GET /approval-requests/{id}` | `AnyCaller` | none | clean |
| `GET /approval-policy` | `AnyCaller` | none (`PUT` uses `requires(admin:manage_roles)`) | clean |
| `GET /demo/guide` | `AnyCaller` | none | clean |
| `GET /me` | `CallerDep` | none; `rbac.effective_permissions` reports the set, it enforces nothing | clean |

Observation, not changed: `GET /me/workspaces` and `POST /me/workspace` depend on `IdentityDep`, not `counted_caller`, so neither is counted. Whether they should be is `RL-1687`'s scope question, not this fix's; put to the lead.

## Every accepted direct write in the slice's tests, one table (the maintainer (by delegation), 2026-10-16 10:27:41 BST, Q-a and Q-b)

**Ruling (verified against `~/gi-pricing-plan.local/channel/to-lead.md`, entry "2026-10-16 10:27:41 BST", Q-a and Q-b):** the 10:19:57 "ONE accepted direct write" was scoped to that decision point's seed set; an exception ruled earlier with its own dated basis stands; this ledger lists EVERY accepted direct write in one table, each with its ruling's stamp, and a row without one is a red. `_put_blob_inputs`' write stays and is recorded as "owed to E4.8, FD-1730".

**Predicate (run at the tree of this commit's parent, `9deddd85`):** the added lines of `git diff -U0 origin/main...HEAD -- backend/tests scripts/bench-rating.py scripts/bench-deploy-path.py`, matched with `session\.add|add_all|add_approved|mark_approved|INSERT|UPDATE |psql|insert\(|delete\(|\.execute\(|Row\(`. Hits that are reads (`select`) or prose are not rows.

| # | Where | What it writes | Stamp | Verdict |
|---|---|---|---|---|
| 1 | ~~`backend/tests/test_deploy_stack_runtime.py:216`, `:218` `session.add(ServiceAccountRow / ApiKeyRow)`~~ **REMOVED as a direct write** (this commit) | was the test credential | **10:31:43 BST (1a) and (1b)**, which CORRECTS 10:27:41 Q-a: the premise "no route creates a score:execute Service Account" was false (`POST /api/v1/service-accounts`, `service_accounts.py:179`) | the key is now created through the route by the demo `admin` (`_create_scorer`); every call needing a permission outside FR-389 uses a demo user principal. No direct row remains. See "10:31:43 items" below |
| 2 | `backend/tests/approved_rows.py:78` `add_approved`, reached through `test_demo_rating_evidence._approved_model` from `_governed_workspace` (no direct hit in the changed files; the call is indirect) | approval-evidence rows of the UPSTREAM Model only | **10:19:57 BST point 3** | accepted, scoped |
| 3 | `backend/tests/test_deploy_stack_runtime.py:478` `session.add(DatasetVersionRow)` in `_put_blob_inputs` | Dataset Version rows making the seeded blobs readable | **09:55:22 BST DP-E1** and **10:27:41 BST Q-b** | owed to E4.8, FD-1730 (the public upload path is broken on main; its fix is SL-1722; the conversion is E4.8's, carried by S4 or its own SL under DP-E1) |
| 4 | `backend/tests/test_management_rate_limit.py:68` `delete(WorkspaceSettingRow)` in the `limit` fixture's teardown (the set itself goes through `svc.set_workspace_setting`, a service) | removes the workspace's setting rows after the test | **10:31:43 BST (4)** ("fixture plumbing"; builds no product state a test asserts on) | accepted |
| 5 | `backend/tests/conftest_db.py:219` `grant` (roles, membership, assignment, built-in rules), used by `test_management_rate_limit.py` | the test principal's role and membership | **10:31:43 BST (5)** ("fixture plumbing"; on `origin/main`, predates the slice) | accepted |
| - | `scripts/bench-rating.py::_seed` | the bench tool's direct seed | 10:08:52 BST point 4 (stays a bench tool, no runtime test imports it) | not a test |

**Premise note on row 1 (not changed; for the lead).** `POST /api/v1/service-accounts` exists (`backend/src/app/api/service_accounts.py:179`, permission `admin:manage_service_accounts`) and creates a Service Account with `score:execute` and `score:batch` (`ALLOWED_PERMISSIONS`, `:44`). So "no route creates a score:execute Service Account" does not hold as worded. What the route cannot do is create a key with the other permissions `_governed_workspace` grants (`_ALL_PERMISSIONS`, and `admin:manage_settings` for the sampled-trace test), because `ALLOWED_PERMISSIONS` is capped to the two scoring permissions (FR-389). The tests that need only `_SCORING_PERMISSIONS` (`:242`) could use the route. The ruling stands as given; whether the narrower reason should replace the recorded one is the maintainer's (by delegation).

## Q-c: the `/me/workspaces` and `/me/workspace` management count (the maintainer (by delegation), 10:27:41 BST) is BLOCKED on a design choice

**Verified at `9deddd85`:** `GET /me` is counted (`me.py:42` `CallerDep = Annotated[Caller, Depends(counted_caller)]`). `GET /me/workspaces` (`:180`) and `POST /me/workspace` (`:215`) take `IdentityDep` and are NOT counted. The key `(environment, principal)` is available from `Identity`: `principal` is there, and `environment` is `None` for a bearer or development identity, as it already is on those callers' `Caller`. **The limit is not:** `rate_limit.enforce` resolves `platform.default_management_rate_limit_rps` through `settings_service.resolve(session, settings, workspace_id, ...)`, the Setting is declared `WORKSPACE_OR_ENVIRONMENT`, and the workspace layer reads `WorkspaceSettingRow` for a `workspace_id`. `Identity` carries no workspace selection by construction (`deps.py:92`, FR-397): it holds a set of zero or more memberships. No code written; stopped as ordered. Options and the recommendation are in the report to the lead.

## 10:31:43 BST items (the maintainer (by delegation), `to-lead.md` entry "2026-10-16 10:31:43 BST"; lead ruling `from-lead-2026-10-09.md` entry "2026-10-16 10:30:18 BST", concurred 10:30:57 BST)

**Nothing below was run.** The SL-1455 ALONE latency gate held the box (no pytest, generate-contracts, uv sync, ruff, mypy, docker, audit-docs). Each red, each green and each regeneration is OWED after GATE END; `py_compile` was the only check, and it is not a test result.

**Item 1 — DP-S4-ME (A): `GET /me/workspaces` and `POST /me/workspace` are counted with `workspace_id=None`.** The precising RL is drafted separately; this slice cites the 10:31:43 entry until it is minted.
- **Red, committed first** (`3ca5b80e`): `backend/tests/test_management_rate_limit.py`, `test_an_identity_route_is_counted_once` (parametrised over both routes, counter +1 exactly) and `test_an_identity_route_ignores_a_workspace_override` (a workspace limit of 1 does not refuse the second call; the counter is not asked because the default is unset). Red cause: the two routes take `IdentityDep` and are never counted. The red is NOT yet observed (owed after END).
- **Fix** (`1ea8c16d`): `counted_identity` (`backend/src/app/api/authz.py`) counts through `_count_management_request`, the helper `requires()` and `counted_caller()` use, with `workspace_id=None` and `environment=None`; `me.py` binds `IdentityDep` to it (`Annotated[Identity, Depends(counted_identity)]`), so both routes change by that one alias, the same form as the other counted routes.
- **Resolve path stated:** `rate_limit.enforce` -> `settings_service.resolve(session, settings, None, "platform.default_management_rate_limit_rps", None)`. With `workspace_id=None` `resolve` skips the `WorkspaceSettingRow` read (workspace candidate reported, no value); the effective value is the environment-variable layer (`GIP_SETTING_PLATFORM_DEFAULT_MANAGEMENT_RATE_LIMIT_RPS`), then the default (unset: no counter call). The Environment layer is skipped too: `Identity` has no environment (`None`, as for a bearer or development caller). `enforce` and `resolve` now take `UUID | None`.
- **Confirmed and corrected by the maintainer (by delegation), `to-lead.md` entry "2026-10-16 10:36:38 BST" (Q1, Q2, and a correction of the 10:31:43 label).** The clause being made precise is `RL-1687` (2a); the Service Account `rate_limit_rps` clause is untouched. Only the workspace layer is skipped; FR-446's order otherwise holds as `resolve` implements it: process variable `GIP_SETTING_<KEY>`, then Environment, then default. The Environment layer applies only to a key verified for an Environment, and (2a) already skips it for a bearer or development caller, so a typical `/me` call resolves process variable -> default. The per-route reds therefore include a BEARER caller: `test_an_identity_route_is_counted_once_for_a_bearer_caller` (both routes, counter +1, then `429` at limit 1), beside the development-caller reds and `test_an_identity_route_keeps_the_process_variable_layer`. Not yet run.
- Q-c is therefore no longer blocked.

**Item 2 — Q-a re-ruling (1a)/(1b); (4) and (5) stamped.**
- **(1a)** `_governed_workspace(approved, scoring)` (`test_deploy_stack_runtime.py`) no longer writes `ServiceAccountRow`/`ApiKeyRow`. `_create_scorer` calls `POST /api/v1/service-accounts` as the demo `admin` principal (development identity header `x-dev-principal-id`, which the compose default `GIP_DEV_AUTH_ENABLED: true` enables; the admin built-in role holds `admin:manage_service_accounts`, `permissions.py` `BUILTIN_ROLES`), with only `score:execute` (+ `score:batch` for the batch test).
- **(1b)** No test keeps a Service Account holding a permission outside `ALLOWED_PERMISSIONS`. Each call that needs one uses a demo USER principal that holds it through its built-in role (`_Workspace.users`, development identity): compile test -> `analyst` (`rating:compile`, `rating:read`, `job:read`); ingest test -> `analyst` (`dataset:write`, `job:read`); batch test -> scoring key for `POST /score/batch`, `analyst` for the Job read; sampled-trace test -> `admin` for `PUT /settings` (`admin:manage_settings`), the scoring key for `POST /score`, `analyst` for the Job and trace reads. `_ALL_PERMISSIONS` and the `extra_permissions` parameter are gone. No test needed a STOP.
- **(4), (5):** stamped 10:31:43 in the table above. Every row of that table now carries a stamp; none is UNSTAMPED.
- Premise note on row 1 above: superseded by (1a)/(1b); kept as written because the ledger is append-only.

**Item 3 — the lead's 429 ruling: ONE router-level mechanism** (`9b2f298a`).
- **Mechanism:** `backend/src/app/main.py` `counted(router)` = `app.include_router(router, prefix=API_PREFIX, responses=problems(429))`; every `/api/v1` router except `score.router` is included through it. `score.router` keeps its own `429` on `POST /score` (`score.py:389`, RL-1347 rule 4). `GET /api/v1/auth/config` is an `add_api_route`, never counted.
- **Test:** `backend/tests/test_management_429_declared.py` walks `app.openapi()`, asserts every `/api/v1` operation outside `auth/config` and the `/score` family lists `429`, and names the first missing operation (`first: METHOD path`). Broken-input red: remove `responses=problems(429)` from `counted()` and it fails naming `DELETE /api/v1/...` (first in sort order). Not yet observed.
- **`generated.json` regeneration is OWED and is amended into this commit's successor, before the gate.** The ruling puts the regeneration in the same commit as the limiter change; this commit changes the behaviour contract (the declared statuses) without `docs/contracts/openapi/generated.json`, so `generate-contracts.py --check` and `test_contracts.py` are RED at `9b2f298a` until the successor lands. The commit-level pairing is checked at the ACK. Observation for the lead: `POST /score/batch` and `POST /score/compare` do not declare `429` today (only `POST /score` does); they are inside the excluded `/score` family, so this test does not cover them.

**Item 3 amendment — the lead's, relayed to this seat and received at 2026-10-16 10:38:16 BST (my own `date`; the lead's message carries no entry heading, so the lead's entry id is not cited here).** Rule: an operation declares `429` if and only if it can return one; "excluding the /score family" was shorthand that fails for two routes. Read at this tree:
- `POST /score/compare` (`score.py` `@router.post("/score/compare")`): caller is `RatingReadDep` = `requires(RATING_READ)` (`rating_algorithms.py:32`), which counts against the management limit. It CAN return 429, so it now declares it by its own `problems(..., 429, ...)` entry (`score.router` is not included through `counted()`).
- `POST /score/batch`: caller is `ScoreBatchDep` = `requires(SCORE_BATCH, management_counted=False)` and the handler calls no limiter. It CANNOT return 429 and does not declare it.
- `POST /score`: scoring limiter, declares its own 429 (RL-1347), unchanged.
- The walk test's exclusion list is `_CANNOT_429` in `backend/tests/test_management_429_declared.py`, EXACTLY: `GET /api/v1/auth/config` (not authenticated) and `POST /api/v1/score/batch` (counted by neither limit), each with its reason. The test also fails if an excluded op declares 429. A second test reads each route's dependency tree (`MANAGEMENT_COUNTED_ATTRIBUTE`, stamped by `requires()`, plus `counted_caller`, `counted_identity`, `management_counter` and the scoring limiter) and fails if an excluded op gains a counting dependency or any other op has none. Not yet run; if a route outside the list has no counting dependency the second test names it.

- 2026-10-16 10:40:13 BST: re-merged `origin/main` a2f77b2d (`git merge --no-ff`, no conflicts; `merge-tree` rc 0 before). Merge commit bbed8cc3 (tree ef58066d). Overlap with #1309 (`git diff --stat 0877e6e7 a2f77b2d`, 13 files): none on authz.py, rate_limit.py, settings.py, main.py, score.py or test_score_rate_limit.py. Owed: `docs/INDEX.md` regeneration and `generate-contracts.py --check` (not run: ALONE latency gate in progress).

## Re-merge 2026-10-17 (2026-10-17 19:41:37 BST): `origin/main` 9469721d into `c27cf2b2`, SL-1455's per-request session against SL-1258's management count

Executor-1258m. Brief: the lead's, 2026-10-17 19:37:47 BST; authority: the maintainer to the lead, 2026-10-17 ~19:38 BST ("A per-hunk table for authz.py / score.py / rate_limit.py; any behaviour-changing resolution → STOP to me. SL-1455's one-session-per-request + resolve_caller must survive intact, quoted."). Merge: `git merge --no-ff origin/main` on `c27cf2b2`; four conflicted files (`docs/INDEX.md` taken from `origin/main`, regenerated below; `authz.py`, `score.py`, `rate_limit.py` by hand). The hand resolution is proved by this slice's own SOLO gate on the merged head, not by this table alone.

**What SL-1455 (#1323, merge `9c602fec`) changed** (`git show 9c602fec --stat`): `api/authz.py` 52, `api/deps.py` 59, `api/score.py` 106, `platform/rate_limit.py` 14. In short: `request_session` is the one session per request (`RequestSessionDep`); `resolve_caller` authenticates through it and leaves it open; `require_caller` closes it after; `requires()` reads its permission through it and closes it unless `keep_session=True` (`/score`); `rate_limit.enforce` takes the request `session`, not `Database`.

**Hunk table.** Behaviour change on either side? = does the resolution change what any request does that either parent did (a count, a refusal, a status, a connection held).

| # | file:line (merge-conflict hunk) | ours (SL-1258) | theirs (main, SL-1455) | resolution | why | behaviour change? |
|---|---|---|---|---|---|---|
| 1 | `authz.py` imports (:27) | imports `Identity`, `IdentityDep`, `SettingsDep`, `require_caller`, `Settings`, `Database`, `rate_limit`, `Principal`; `__all__` of 8 names | imports `RequestSessionDep`, `resolve_caller`; `__all__` of 2 names | both-combined; `Database` import dropped (nothing uses it now); `Request` and `AsyncSession` imports added | union of what both sides' code needs | no |
| 2 | `authz.py` (:61) `CallerDep`, `_database`/`DatabaseDep`, counting helpers | `CallerDep` = `require_caller`; `DatabaseDep`; `_count_management_request`, `_count_caller`, `counted_caller`, `counted_identity`, `management_counter` all take `database: Database`; `enforce(..., database, ...)` | `CallerDep` = `resolve_caller` (no `DatabaseDep`) | both-combined. `CallerDep` stays `require_caller` (ours): every counting dependency and every external user of `CallerDep` (`deployments.py`, `validation.py`) keeps the contract "session closed after resolve, the handler runs on its own". The helpers take `session: RequestSessionDep` and pass it to `enforce` (theirs). `DatabaseDep` removed (unused; `rate_limit.enforce` no longer takes a `Database`). `_count_management_request` ends with `await session.close()` | `enforce` now reads the Setting through the request session (theirs, forced by the `rate_limit.py` signature). Closing after the count keeps ours' old effect: `database.session()` released its connection when the count finished, so a counting dependency holds no pool slot for the handler. The already-counted early return also closes, so a second counting dependency on a route leaves nothing open | no: the same counts, 429s and Setting reads; the same one connection released as before |
| 3 | `authz.py` (:187) `requires()` | `requires(permission, *, management_counted=True)`; opens `database.session()` for the check, then counts via `_count_caller(..., database, settings)` | `requires(permission, *, keep_session=False)`; check through `RequestSessionDep`, then `session.close()` unless `keep_session` | both-combined: `requires(permission, *, keep_session=False, management_counted=True)`; depends on `resolve_caller` (theirs, not `CallerDep`: the check reads through the still-open session), check through `session`, then `if management_counted: count (closes the session) elif not keep_session: close`. `MANAGEMENT_COUNTED_ATTRIBUTE` stamp kept (ours) | each limb of each side survives: the count after the check (ours), the check on the request session and `keep_session` (theirs). `keep_session=True` is documented as used with `management_counted=False` because a count closes the session it reads through | no. `/score` is `keep_session=True, management_counted=False` (hunk 5): the session stays open, no count, as on main. All other routes: check, count, release, as on `c27cf2b2` but with one checkout fewer |
| 4 | `rate_limit.py:128` `enforce` docstring | adds the sentence on `workspace_id=None` | adds the paragraph on `session` | both-combined (the two docstring additions, no code in the hunk). The non-conflicting code hunks merged clean: `workspace_id: UUID \| None` (ours) with `session: AsyncSession` and no `database.session()` (theirs) | docstring only | no |
| 5 | `score.py:140` `ScoreExecuteDep` | `requires(SCORE_EXECUTE, management_counted=False)` | `requires(SCORE_EXECUTE, keep_session=True)` | both-combined: `requires(SCORE_EXECUTE, keep_session=True, management_counted=False)`; the comment extended with the `management_counted=False` reason | `/score` is counted by the scoring limit (ours), and its reads continue on the request session (theirs). `_enforce_score_rate_limit` already took `session` (theirs, merged clean) | no. `ScoreBatchDep` (`management_counted=False`, ours) merged clean and closes the session after the check (theirs' default) |

No hunk needed a choice of one side's behaviour; no STOP.

**SL-1455's `request_session` and `resolve_caller`, quoted from `origin/main` 9469721d, `backend/src/app/api/deps.py:102` and `:229`** (`git show origin/main:backend/src/app/api/deps.py`):

```python
async def request_session(database: DatabaseDep) -> AsyncIterator[AsyncSession]:
    """The one session a request reads through (RL-1685, PL-1454 DP-1 (a)).

    FastAPI resolves a dependency once per request however many dependencies and handlers
    name it, so API-key authentication, the permission check, FR-452's limit Setting and the
    route's own reads share one session and therefore one pool checkout. The session takes a
    connection only at its first statement and returns it when the request ends.
    """
    async with database.session() as session:
        yield session
```

```python
async def resolve_caller(
    request: Request,
    settings: SettingsDep,
    session: RequestSessionDep,
    workspace_id: Annotated[
        str | None, Header(alias="Workspace-Id", description=WORKSPACE_ID_DESCRIPTION)
    ] = None,
) -> Caller:
    """Resolve the caller, or refuse — leaving the request session as it found it.

    Only `requires()` depends on this directly, because it reads the permission through the
    same session next and releases it itself (RL-1685, PL-1454 DP-1 (a)). Every other route
    depends on `require_caller`, which closes the session this one may have left open.
    """
    # Taken as `str | None` and parsed here rather than annotated `UUID | None`: FastAPI
    # would answer a malformed UUID with a bare `422` outside the platform error
    # catalogue, and FR-397 requires the refusal to be a typed platform error.
    selected: UUID | None = None
    if workspace_id is not None:
        try:
            selected = UUID(workspace_id)
        except ValueError as exc:
            raise PlatformError(
                "WORKSPACE_SCOPE_DENIED",
                "Workspace scope denied",
                403,
                "The Workspace-Id header must be a UUID.",
            ) from exc

    authorization = request.headers.get("authorization", "")
    scheme, _, credential = authorization.partition(" ")
    scheme = scheme.lower()

    database: Database = request.app.state.database

    if scheme == "bearer" and credential:
        verifier: OidcVerifier = request.app.state.oidc_verifier
        async with database.unit_of_work() as session:
            identity = await authenticate_bearer(session, verifier, credential)
        return _select_workspace(identity, selected)

    api_key = credential if scheme == "apikey" else request.headers.get("x-api-key")
    if api_key:
        identity = await authenticate_api_key(session, api_key)
        if session.dirty:
            # The throttled `last_used_at` stamp (RL-1685 DP-1 (b)) is the only write this
            # path makes, and only about once a minute: commit it before the handler's reads.
            # A request that stamped nothing commits nothing, so it keeps its one connection.
            await session.commit()
        return _select_workspace(identity, selected)

    # The dev path consumes the same `Workspace-Id` header with the same membership
    # check as the bearer and API-key paths above. An earlier version of this comment
    # said the dev path read "a different header for a different purpose" — that was
    # true before W6b-11 (2026-08-26) removed `x-dev-workspace-id`, and describes no
    # code that exists now.
    return await _development_caller(request, settings, database, selected)
```

**After the merge, in this worktree's `backend/src/app/api/deps.py`:** `git diff origin/main -- backend/src/app/api/deps.py` is empty (the file is identical to main's); `diff` of the two quoted definitions against main's: rc 0 for both. No SL-1258 change touches `deps.py`.

**One session per request, by call site (merged `authz.py`, `score.py`, `rate_limit.py`):** `authz.py` and `rate_limit.py` call no `database.session()`, `unit_of_work()` or `resolve_caller` (apart from `requires()`'s `Depends(resolve_caller)`); `score.py` keeps main's two `database.unit_of_work()` sites unchanged by this merge (`git diff origin/main -- score.py` touches neither): the sampled-trace write, which main keeps on its own connection for FR-259's failure isolation, and the `/score/batch` Job submit (writes, after the check closed the session); every other site names `RequestSessionDep` (`counted_caller`, `counted_identity`, `management_counter`, `requires`, `_enforce_score_rate_limit`), which FastAPI resolves once per request. `rate_limit.enforce` opens none.

**Checks on this merge (tree: the working tree of `sl-1258-wk674-s4` on top of the pre-merge head `c27cf2b2`, before the merge commit):** ruff check and ruff format --check on `authz.py` rc 0; `ruff check` on `score.py`, `rate_limit.py` rc 0 (`ruff format` is not clean on `origin/main`'s own `rate_limit.py` and `score.py`, so those two were not reformatted: no churn in lines this merge did not touch); `uv run mypy` rc 0 (240 source files); `backend/tests/test_management_429_declared.py` 2 passed through `run-small.sh`. `backend/tests/test_api_authorisation_sweep.py` was also run and all 9 of its DB tests errored with `GIP_TEST_DATABASE_URL is not set, and the per-worktree test database ... does not exist yet`: not run, owed to the SOLO gate (no DB lane granted).

**AC2 gate stage (PL-1714 Acceptance Standard item 2):** added to `sl1258-gate.sh` after the python static checks. Pass condition: `git grep` rc 1 and `lines=0`. A dry run at `c27cf2b2` prints one hit, `backend/tests/test_deploy_stack_runtime.py:360` (a docstring: "A shape test proves `--queues default,compute` is declared"), so the stage as written reads rc 0 and will not pass: reported to the lead, not edited.

AC2's grep is literal; prose hit at :360 reworded, not a code change (the maintainer's ruling relayed in the lead's brief of 2026-10-17 19:43:48 BST, ruling stamped ~19:44 BST: option (a); (b) refused as it weakens the check, (c) refused as a red-by-design stage hides future hits).

**Rolling `api` roll = scale-out-then-in (NFR-531; mechanism: compose scale + container ids).** The smoke's roll (`up --scale api=2`) recreated both replicas at once: ~23.3 s with no healthy replica, 765 failed requests (to-lead.md 2026-10-18 01:33:32 BST, the cause reading; option (a) ruled 01:33:49 BST). `_roll_api` in `backend/tests/test_deploy_stack_runtime.py` now runs `up -d --no-deps --no-recreate --scale api=4 api`, waits (bounded 180 s, loud) until both new containers are healthy by id, then `docker stop` + `docker rm` the old ones one at a time, ending at api=2; `deploy/README.md` documents the same sequence; no `lb.conf` change. The test keeps `failed == 0` and adds an overlap assert: a sampler counts healthy `api` containers (`docker ps --filter health=healthy`, project-labelled) every 0.1 s across the roll and asserts `min >= 1`. Proof is the SL-1258 SOLO re-gate; not run here.

**One roll script, and a permanent per-failure record (NFR-531).** The roll sequence lives only in `deploy/roll-api.sh`; the README points at it and `test_deploy_stack_runtime.py` calls it by subprocess (to-lead.md 2026-10-18 01:38:19 BST). Run 2 at 2b92457d had 1 failed request (min healthy 2 over 189 samples); no fix is made before the evidence names H1 or H2, so the client loop now records each failed request's UTC ms timestamp, error class and elapsed time beside the roll step lines (01:40:16 BST; the network-disconnect drain and the lb non_idempotent retry are refused).

**Smokediag runs 1–3 and the `proxy_connect_timeout` fix (NFR-531).** Run 1 @74ec5ea0: 765 failed requests, both replicas recreated together (to-lead.md 2026-10-18 01:33:32 BST, option (a) ruled 01:33:49, the single roll script 01:38:19). Run 2 @2b92457d: 1 failed request, min 2 healthy over 189 samples, the roll order correct (01:40:16 BST: the per-request record first). Run 3 @ff7869ba: 1 failed request, min 2 healthy over 185 samples, a `read timeout` of 10011 ms on a request that started at 00:43:26.198, 107 ms after `removed old 22fe66c78840` (00:43:26.091) and before `stopped old b50fa6af8c32` (00:43:26.701). H1: nginx held a connect to the removed replica's address, cached under `resolver … valid=1s`, with `proxy_connect_timeout` at its 60 s default, so `proxy_next_upstream error timeout` could not fire inside the client's 10 s. H2, an in-flight cut, is ruled out: the request began after the container was gone, and a cut gives a reset or a fast 502, not a 10 s silent hang. The fix is `proxy_connect_timeout 1s;` in `deploy/lb.conf`, the only lb change; `roll-api.sh` is unchanged, and a connect timeout means the request was never sent, so the retry is safe for POST (to-lead.md 2026-10-18 01:44:33 BST). Run logs: `scratch/sl1258-smokediag.run1-74ec5ea0`, `.run2-2b92457d`, `sl1258-smokediag/` (local, not in the repository).

## PRs

None yet.
