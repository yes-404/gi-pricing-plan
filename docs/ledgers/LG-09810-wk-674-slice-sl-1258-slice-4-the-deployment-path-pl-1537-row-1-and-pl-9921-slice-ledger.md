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

## PRs

None yet.
