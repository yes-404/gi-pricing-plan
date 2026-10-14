---
id: FD-8021
family: finding
title: A routed job never completes on a real worker — io and scoring have no consumer, and score.trace_produce has no registered handler
status: active
created: 2026-10-14
owner: auditor
tree: 1e260c1553acf39844939fe12da685ccfb835e54
corrected_by: []
relates: [WK-674, WF-698, FR-405, FR-406, FD-1661]
---

# FD-8021 — A routed job never completes on a real worker

*(Filed under working id 8021, reserved by the lead in the eta log, 2026-10-14 10:14:33 BST (a local file). Authority: the maintainer's (by delegation) entry "2026-10-14 10:13:50 BST — Unconsumed worker queues: the finding is WIDER (io too); (a) AMENDED to a DERIVED consumer set; (b) one finding for the class" and its follow-up "2026-10-14 10:36:42 BST" (both `to-lead.md`), which put the unregistered trace handler inside this finding. Every `file:line` was read at `origin/main` `1e260c1553acf39844939fe12da685ccfb835e54`; the run is below. A minter folds the working id into the docs batch.)*

## Finding

**Proposed severity: HIGH** (the auditor proposes; the lead decides). Reasoning is in *Severity*.

The class is *a routed job never completes on a real worker*. Two causes, one run proves both:

1. **No worker consumes `io` or `scoring`.** `DEFAULT_QUEUE_FOR_KIND` (`backend/src/app/platform/jobs.py:58-85`) routes `DATASET_INGEST`, `EXPORT_REGULATORY` and `BLOB_GC` to `io`, and `SCORE_BATCH` and `SCORE_TRACE_PRODUCE` to `scoring`. Every worker command in the repository consumes at most `default,compute`. A Job on `io` or `scoring` stays `queued` for ever: no error and no failed status.
2. **`score.trace_produce` has no registered handler.** `backend/src/app/worker/entrypoint.py` registers six handler groups and never calls `register_trace_handlers` (`worker/trace_handlers.py:120`). Only `backend/tests/test_score.py:1073, :1125, :1667, :1798` call it. Even a worker that consumes `scoring` fails this kind with `JOB_HANDLER_NOT_REGISTERED` (`worker/tasks.py:132`).

## Evidence

### 1. Read: every routed queue, every `--queues`

```bash
git grep -n -E "^    JobKind\.[A-Z_]+: JobQueue\." origin/main -- backend/src/app/platform/jobs.py
git grep -n -i -E "\-\-queues|-Q [a-z]|worker_queues|task_queues|task_routes" origin/main -- . ':!docs/findings' ':!docs/closures' ':!docs/ledgers'
git grep -n -E "default,compute|--queues" origin/docs-d14-2026-10-12 -- 'docs/plans/*1690*'
```

The routing table (first command): `io` carries `DATASET_INGEST`, `EXPORT_REGULATORY`, `BLOB_GC`; `scoring` carries `score.batch`, `score.trace_produce`; `default` carries `RATING_COMPILE`, `MONITOR_RUN`, `DOSSIER_GENERATE`; the other 16 kinds are `compute`.

The consumers (second command), complete for the tree:

| Where | `--queues` |
|---|---|
| `backend/src/app/worker/entrypoint.py:3` (docstring) | `compute` |
| `scripts/demo.py:216-224` (`worker_command`) | `default,compute` |
| `.claude/skills/dev-commands/SKILL.md:964` | `compute,default,io,scoring` (a documentation line; the only place all four appear) |
| `deploy/docker-compose.yml` | **no worker service at all** (`FD-1661`) |
| `.github/`, `Makefile`, systemd units, Dockerfiles | none |

The not-yet-merged plan for the compose worker (PL 1690, `origin/docs-d14-2026-10-12`, E4.2) hard-codes `default,compute` and a shape test asserting exactly that set: it would bless the gap.

Beat's relay task is routed to `default` (`worker/entrypoint.py`, `beat_schedule`, `"options": {"queue": "default"}`), so a worker on `compute` alone, the entrypoint docstring's own example, would not even relay the outbox.

`backend/tests/test_jobs.py:73` (`test_every_kind_has_a_queue`) proves every kind has a queue. No test, check or doc proves every queue has a consumer, nor that every routed kind has a handler on the worker.

### 2. Does G2 hit this? Read: no, by accident of route

- The seed ingests **inline**: `examples/fremtpl2/seed.py:512-520` submits `JobKind.DATASET_INGEST` and calls `execute_job(database, job.id, blob_store)` in the same process, as do `:549` and `:586`. No broker, no worker, no queue is touched.
- The WF-699 journey (`examples/fremtpl2/journey.py`) submits no `dataset.ingest` and no `score.batch`: its Jobs are rate-table diffs, `rating.compile`, regression runs and dislocation (`compute`/`default`). `scripts/demo.py:269` calls `run_wf699_journey` with no `run_job`, so its Jobs go through the real worker on `default,compute`, which is exactly the two queues they use. Its `/score` calls (`journey.py:1141-1183`) are the synchronous route.
- So the demo's green path is consistent with the defect; the defect is outside that path, not absent from the platform.

### 3. Run: the Jobs, with and without a consumer

Scratch run at `1e260c15`, in the worktree `fd-8021`, Redis database 13 (empty before, flushed after), scratch database `gipricing_queues_5ec80135` from `createdb -T gipricing`, `alembic upgrade head`, queued behind `flock -w 3600 /tmp/slots/gate-1` as a background job (slot acquired 2026-10-14T09:46:25Z), `OMP_NUM_THREADS=1 nice`. Driver `/tmp/queues-run/driver.py` (scratch, not committed). One uvicorn, one beat, two workers started from `app.worker.entrypoint` and killed by their own PIDs at the end; the database was dropped (`dropped gipricing_queues_5ec80135`).

Five Jobs were submitted in one fresh workspace through `job_service.submit`, the call the routes make: `dataset.ingest` (the `POST /datasets/{slug}/versions` parameters), `score.batch`, `score.trace_produce`, `dataset.validate` (a `compute` control) and `rating.compile` (a `default` control). The parameters carry only the workspace and actor (and, for the ingest, the real dataset and blob), so `failed JOB_HANDLER_FAILED` on a control or on `score.batch` means "a handler ran and refused my parameters", which is what proves consumption. The thing observed is whether a Job leaves `queued`.

| t (s) | Phase | Job statuses | Redis `LLEN` default/compute/io/scoring |
|---|---|---|---|
| +10.0 | API only, no beat, no worker | all five `queued` | 0/0/0/0 |
| +28.1 | + beat, no worker | all five `queued` | 5/0/0/0 |
| +33.1 | + worker `default,compute` (+5 s) | all five `queued` | 10/0/0/0 |
| +38.1 | worker `default,compute` (+10 s) | `rating.compile` and `dataset.validate` **`failed JOB_HANDLER_FAILED`** (they ran); `dataset.ingest`, `score.batch`, `score.trace_produce` still **`queued`** | 0/0/**3**/**2** |
| +48.1 | same (+20 s) | unchanged | 0/0/3/2 |
| +53.1 | + second worker `io,scoring` (+5 s) | unchanged | 0/0/3/2 |
| +58.1 | `io,scoring` (+10 s) | **`dataset.ingest` `succeeded`**; `score.batch` `failed JOB_HANDLER_FAILED`; **`score.trace_produce` `failed JOB_HANDLER_NOT_REGISTERED`** | 0/0/0/0 |
| +68.1 | `io,scoring` (+20 s) | unchanged | 0/0/0/0 |

Readings:

- With the repository's own worker command (`default,compute`, as in `scripts/demo.py`), `dataset.ingest` and both `scoring` kinds sat `queued` for 20 s after the controls on the same worker had finished (the 20 s is the observed window, not a bound). The messages were in Redis (`io` 3, `scoring` 2) with no reader. The extra copies are the relay publishing an outbox row on each tick before the row is marked; that is a separate question and is not claimed here.
- With a worker on `io,scoring`, `dataset.ingest` `succeeded` within 10 s. So the cause is the missing consumer, not a defect in the handler.
- `score.batch` ran its registered handler (`JOB_HANDLER_FAILED`, my parameters were empty); a `succeeded` score.batch was **not** shown by this run, which had no model or deployment to score.
- `score.trace_produce` failed `JOB_HANDLER_NOT_REGISTERED` on a worker that *does* consume `scoring`. That is the second limb, shown by the run, not by reading.
- The API route itself could not be used to submit the ingest: `POST /datasets/{slug}/versions` answered **404 "Blob not found"** for a freshly stored blob in the first (discarded) attempt, because `blob_readable_by` (`platform/blobs.py:508-534`) allows only a blob that a dataset version or a job result already owns; `POST /blobs/upload-url` has no completion step (`api/blobs.py`, its docstring). So a first upload cannot reach `dataset.ingest` over HTTP at this tree. That is outside this finding and is stated so a reader does not reproduce the 404 as a queue fault.
- Discarded run: a first attempt read the whole `jobs` table of a database cloned from `gipricing` and so showed other workspaces' Jobs; it proved nothing and was dropped. The reported run filters on its own `workspace_id`.

### 4. Does anything consume `io` or `scoring` today?

No. Section 1's table is the complete list at this tree, by the command shown. The only text naming all four is a skill's example line.

## Severity

**Proposed HIGH.** The argument for:

- The failure is **silent and permanent**: a `queued` Job and an empty error field; the run shows no failed status to alert on. A pricing actuary's first step on the shipped topology, WF-698 step 1, an ingest started through the API, never starts.
- It is the **only** topology the repository writes down: the demo's worker, the entrypoint's documented command and the compose worker the plan is about to ship all omit `io`. The fix is a one-line list in each, but the *test* planned to guard it asserts the wrong set.
- `score.batch` and `score.trace_produce` are the quote pipeline's own pool; trace sampling (WF-701 C7) cannot pass until both limbs are fixed.
- A plan has already ruled the wrong set into a test (`PL 1690`, E4.2).

The argument against: nothing is mispriced and no data is lost; G2's path is unaffected (section 2); compose has no worker at all yet (`FD-1661`), so no *deployed* stack is broken today, only the one being built. If the lead weighs "deployed stack" strictly, MEDIUM is defensible. I propose HIGH because the defect is certain on the topology that will ship, silent, and sits under the first step of the first workflow.

## Disposition

**Remedy (ruled, not built here).**

Per the maintainer's (by delegation) entry "2026-10-14 10:13:50 BST" (a) and "2026-10-14 10:36:42 BST":

1. The compose worker(s) consume **every** pool in the routing table; the pool-to-worker split is the S4 planner's to recommend and the lead's to rule.
2. The E4.2 shape test asserts `consumed ⊇ set(DEFAULT_QUEUE_FOR_KIND.values())`, **derived** from the table, never a literal set.
3. `scripts/demo.py`'s worker command takes the same derived set (`worker_command`, `:208-229`).
4. `worker/entrypoint.py` registers `register_trace_handlers`, and a derived guard asserts every routed kind has a registered handler on the worker, with an allow-list for later-phase kinds.
5. **The reds assert `succeeded`, never "reaches a terminal state".** This run is the proof: a terminal-state assert passes `score.trace_produce` here, because `failed JOB_HANDLER_NOT_REGISTERED` is terminal. One `dataset.ingest` Job and one `score.batch` (or `score.trace_produce`) Job must each reach `succeeded` through a real worker, with no inline `execute_job`.

**Owner: WK-674** (S4 discharges it). **Event that next confirms or discharges it:** a merged change after which a real-worker test submits `dataset.ingest`, `score.batch` and `score.trace_produce` and each ends `succeeded`, and a derived assert covers the queue and handler sets.

## Disclosures

Two `cd` commands to the scratch directory were run by mistake in this session's shell (the shell resets its directory each time; nothing was written outside `/tmp/queues-run` and the worktree).
