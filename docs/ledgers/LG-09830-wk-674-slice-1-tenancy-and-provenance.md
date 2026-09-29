---
id: LG-9830
family: ledger
title: WK-674 Slice 1 — Tenancy and provenance (FR-436, FR-18)
status: active
created: 2026-09-29
owner: executor
tree: e537e50e92046732fc539f1916ee0fd7829be144
phase: P2
work: WK-674
plans: [PL-1239]
corrected_by: []
relates: [RL-1253, PL-1237, RL-1232]
---

# LG-9830 — WK-674 Slice 1 — Tenancy and provenance (FR-436, FR-18)

Executed from `PL-1239` (SL-1255) under `RL-1253`. Branch `wk674-s1-build`, from
`origin/main` `97b15726b1dd60ba407c6aba44735ad5cbe207ed` (#924). `LG-9830` is a working id,
to be re-minted at the lead's mint turn.

## Tasks

### Task 0 — preconditions

Tree `e537e50e92046732fc539f1916ee0fd7829be144` (`git rev-parse HEAD^{tree}` at `97b15726`).
`uv sync --all-packages` rc 0.

| # | Premise | Result at this tree |
|---|---|---|
| a | No tenant id | `grep -rn -i -E 'tenant_id\|tenant_marker' backend/src packages/*/src \| wc -l` prints `0` |
| b | No build field on the Job | `grep -rn -E 'platform_version\|build_version\|platform_build\|build_sha' backend/src packages/*/src docs/contracts \| wc -l` prints `6` (the plan says 6, all `build_shap_summary`) |
| c | `Settings` frozen, `GIP_`, `extra="forbid"`, `version="0.1.0"` | `backend/src/app/config.py:84-100` read: holds |
| e | `ensure_bucket()` in the lifespan | `backend/src/app/main.py:92`: holds |
| f | No worker start-up signal | `grep -n -E 'worker_process_init\|worker_init' -r backend/src` prints nothing |
| g | Running transition in the worker | `backend/src/app/worker/tasks.py:134` `jobs.transition(session, job_id, JobStatus.RUNNING, actor=SYSTEM)`: holds |
| d, h, i, j | not re-read at Task 0 | re-read at the task that touches each |

Open PRs read (`gh pr list --state open`, 15 rows at this time): none rules on FR-436, FR-18,
the Job contract or `Settings` by title. Working ids in use on open PR titles: 9018 9021 9029
9030 9104 9601 9640 9650 9670 9680 9681 9690 9691 9692 9760 9811 9812 9820; this ledger takes
9830.

### Task 1 — spec, `07` §4.1

`docs/specs/07-platform.md`: `"platform_build": "0.1.0+97b15726b1dd60ba407c6aba44735ad5cbe207ed"`
added after `trace_id` in the §4.1 example, and a dated paragraph (WK-674 Slice 1, 2026-09-29,
FR-18) added after the `progress_at`/`stalled` note. FR-436 and FR-18 not reworded.
`python3 scripts/audit-docs.py`: rc 0, "All checks passed."

## PRs

None opened yet; the draft PR is opened after Task 1's commit is pushed.
