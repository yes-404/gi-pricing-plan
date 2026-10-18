---
id: PL-1812
family: plan
kind: map
title: WK-674 — SL-1813, the compose dataset-ingest smoke on the public upload path (E4.8) and a failed api roll that removes its own new replicas — a dated Work-plan delta
status: active                 # draft → active → superseded | retired (§1.2a) — active 2026-10-18 on the maintainer, to-lead 2026-10-18 03:19:27 BST (GO)
created: 2026-10-18                # minted 2026-10-18; filed 2026-10-18 as working id 8113
owner: planner
tree: 8cfa1c96d13f67d52eeb3bbdfe54ffdc2d848725
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-1813, SL-1258, SL-1722, PL-1714, PL-1237, FR-1776, FR-415, FR-406, FR-435, NFR-531]
---

# PL-1812 — WK-674: the dataset-ingest smoke on the public upload path, and the failed-roll cleanup (SL-1813)

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L5 (`document-ids.md`
> §1.6, PL row). It carries one slice, SL-1813 (roadmap row under WK-674, `draft`). The
> executor is spawned from `.claude/roles/executor.md` and binds `test-driven-development`,
> `python-test`, `dev-commands` and `git-hygiene`. Its ledger is **LG-1814**, filed by the
> executor at build; this plan names it and does not create it.

Written 2026-10-18 03:15 BST by the planner (planner-8111) on the lead's brief
`brief-planner-8111-2026-10-18.md`. Evidence read at `origin/main` `8cfa1c96`, at
`origin/sl-1258-wk674-s4` `2134a9b6` (the audited code head is `e2a2f79e`), and at
`origin/pl-8061-pl1714-delta-2026-10-16` `33446114`. Working ids PL-1812, SL-1813 and
LG-1814 are the lead's (`eta.md`). FD-1804 is filed in D21; this plan cites it and does not
file it.

## The rulings this plan carries out

All in `~/gi-pricing-plan.local/channel/to-lead.md`, read in full:

- **"2026-10-18 03:11:40 BST — Maintainer: SL-1258 audit @2134a9b6 (audited e2a2f79e) — lead
  verdict CONFIRMED with two amendments"**, item 1, verbatim: *"DP-E1: (b) CONFIRMED. SL-1258
  merges with the seeded dataset-ingest smoke; E4.8 (the conversion to upload-url / PUT /
  complete, possible since SL-1722 merged at 39da0e1b) becomes SL-1813, owner WK-674, DUE
  BEFORE the code freeze (Wed 4 Nov). "Or listed at the P2 close" is NOT accepted as an
  alternative: it is §12 row 2's deployment path, so it lands. Its plan gets a GO from me in
  the usual one line."* Item 3 (F4) rules the finding that is FD-1804 (filed in D21):
  *"a failed api roll leaves never-healthy replicas in DNS rotation", MEDIUM … owner WK-674,
  fixed in SL-1813's scope or alongside it. The fix: an EXIT trap in roll-api.sh that, once
  the scale-out has happened and before the old ones are stopped, stops and removes the NEW
  container ids on failure, returning to the pre-roll 2, plus a red-first failure-path test
  (e.g. an image whose healthcheck never passes)."*
- **"2026-10-16 09:55:22 BST — Maintainer: GO SL-1258 BUILD (WK-674 S4, compose stack +
  FD-1713)"**, condition (3), DP-E1, option (b): *"S4 merges seeded, and E4.8 becomes its OWN
  slice id (minted in the next batch, owner WK-674) with the seeded test named in S4's LG as
  replaced by it."*
- **"2026-10-18 01:38:19 BST"** (one shipped `deploy/roll-api.sh`, called by the README and
  the test; the sampler and asserts stay in the test as the outside check), **"01:40:16"**
  (the permanent per-request failure record) and **"01:44:33"** (`proxy_connect_timeout 1s`
  in `deploy/lb.conf`; roll-api.sh's sequence proven right; NFR-531's red and green).

## Goal

The compose dataset-ingest smoke proves the deployment path through the public upload path,
with no seeded blob or Dataset Version; and a failed api roll, before the old replicas are
stopped, leaves the project on its pre-roll replicas with no never-healthy replica in
rotation. The Work's goal is PL-1237's, unchanged.

## Premises (each read at the tree named)

- **P1 — the seeded test.** At `2134a9b6`, `backend/tests/test_deploy_stack_runtime.py:586`
  `test_a_dataset_ingest_job_succeeds_through_the_compose_io_worker` calls
  `_put_blob_inputs(workspace_id, csv, b"PAR1")` (`:600`), which writes the CSV blob and a
  `DatasetVersionRow` by the backend's own session (`:547-581`, the `session.add` at `:568`).
  LG 9810's accepted-direct-write table row 3 (`:244` of the ledger) owes it to E4.8. The
  helper also seeds the scoring frame for `test_a_score_batch_job_succeeds_through_the_compose_scoring_worker`
  (`:643`); that test is out of scope here, and the helper stays while it has a caller.
- **P2 — E4.8 is already specified.** PL 8061 (unminted, `33446114`) §"Slice 4 — changes
  since PL-1714", E4.8: the five-step rewrite, both Jobs asserted `succeeded` with their
  output, the docstring change, Red A and Red B, and where it runs. This plan **carries that
  text as SL-1813's scope unchanged except for its owner** (SL-1258 → SL-1813, by DP-E1 (b)).
  E4.9 (the shared-entrypoint rule) stays with PL 8061 and SL-1258.
- **P3 — the public path is on main.** At `8cfa1c96`: `POST /api/v1/blobs/upload-url`
  (`backend/src/app/api/blobs.py:70`) takes `UploadUrlRequest` (`media_type`, `parts`, default
  1; `packages/model-schema/src/model_schema/uploads.py:23-29`) and returns `UploadUrlResponse`
  with `id` and `urls` (`:32-41`); `POST /api/v1/blobs/uploads/{upload_id}/complete`
  (`blobs.py:111`) returns 202 with a `blob.promote` Job on `io`
  (`backend/src/app/platform/jobs.py:63`), result `JobResult(kind="blob", ref=<sha256>)`
  (`07-platform.md` FR-1776).
- **P4 — the red tree.** `e2a2f79e` and `2134a9b6` do not contain `39da0e1b` (SL-1722):
  `git merge-base --is-ancestor 39da0e1b e2a2f79e` exits 1. A compose image built from
  `e2a2f79e` has no Blob Upload `id`, so a converted test run against it fails at step 2 —
  PL-1721's recorded red, `KeyError: 'id'`.
- **P5 — the failed roll.** At `2134a9b6`, `deploy/roll-api.sh` runs `set -euo pipefail`,
  records the old ids (`:34`), scales to 4 with `--no-recreate` (`:38`), derives the new ids
  (`:40`), and exits 1 on a wrong new count (`:41`) or a new replica not healthy within the
  timeout (`:47`) — with no cleanup, so all 4 replicas stay in the project and in Docker's DNS
  (lb.conf's `resolver`, which does not filter on health). Old ids are stopped and removed
  from `:53`. After the first old stop, removing the new ids would leave none: from there a
  failure stays loud and is not undone.

## Scope

**(i) E4.8**, as PL 8061 specifies it (P2), owner SL-1813. **(ii) FD-1804's fix:**

1. **The trap.** `deploy/roll-api.sh` arms `trap … EXIT` immediately **before** the scale-out
   (`:38`), so a failure inside `up` itself is covered. On a non-zero exit the handler stops
   and removes every `api` container of the project that is not in `old` (derived again
   inside the handler, not from `new`, which may be unset or short at `:41`), prints one
   `roll-api … cleanup: removed new <id>` line per container and a final line naming the
   remaining ids, and exits with the **original** status. The trap is cleared
   (`trap - EXIT`) **before the first old stop** (`:53`): past that point a failure exits 1
   with no cleanup, and the script's header comment says so in one sentence.
2. **No other script change.** The success-path sequence, its step lines and the
   timeout are unchanged (01:44:33 item 2). `deploy/lb.conf` is unchanged.
3. **The README.** The line F4 lands at SL-1258's mint (naming FD-1804) is replaced by one
   sentence: a failed roll before the old replicas are stopped returns to the pre-roll
   replicas.

**Not in scope:** the score-batch test's seeding (P1); E4.9; any change to the success path,
`lb.conf` or the compose file; a spec change. NFR-531 (`07-platform.md:520`) already states
the requirement; this changes how the deploy path meets it on failure.

## Decision points

None open. DP-E1 is ruled (b) (03:11:40 item 1); the fix's mechanism is ruled (item 3). Where
the trap is armed and cleared is fixed by item 3's words ("once the scale-out has happened and
before the old ones are stopped") and P5. A case where the handler cannot return the project
to the old ids alone is a STOP for the decision-maker, not a choice the executor makes.

## Acceptance Standard

1. **Red first, E4.8.** The converted test (PL 8061 E4.8 steps 1-5) is committed before any
   run. Red A: `GIP_DEPLOY_TESTS=1 GIP_N_SHA=e2a2f79e0bba9f05b29ee585b52a9248899e4cf3 uv run
   pytest -q backend/tests/test_deploy_stack_runtime.py -k dataset_ingest` fails at step 2
   with `KeyError: 'id'` (P4). Red B: on the slice head, with the `io` worker service
   stopped, the `blob.promote` Job fails `_wait_succeeded` with `never consumed`. Any other
   failure is a test defect. LG-1814 quotes both, each with its tree.
2. **Green, E4.8.** On the slice head with every worker service up, the same command exits 0
   and prints both Jobs `succeeded` with kind, queue, elapsed and bound; the `blob.promote`
   result is `{"kind": "blob", "ref": <sha256 of the CSV>}`. PL 8061 Acceptance item 2's
   `ast` check, run on `backend/tests/test_deploy_stack_runtime.py` at the slice head, prints
   `[]` and exits 0.
3. **Red first, FD-1804.** A new test in `backend/tests/test_deploy_stack_runtime.py`
   (behind `GIP_DEPLOY_TESTS=1`, marked `req("NFR-531")`) brings up the 2-replica stack, then
   runs `deploy/roll-api.sh -t 30` with an extra compose file written to `tmp_path` that sets
   the `api` healthcheck to a command that always fails (the "image whose healthcheck never
   passes"; no shipped compose file changes). It asserts: the script exits non-zero; the
   project's `api` containers afterwards are exactly the old ids, both `healthy`; none of the
   new ids exists (`docker ps -a`); and 20 requests through `lb` all succeed. Committed and
   run **before** the trap: red at the slice head without the trap, by the cause "4 api
   containers remain" (the new-ids assert). LG-1814 quotes the FAILED line and the tree.
4. **Green, FD-1804.** With the trap, the test in item 3 passes, and the script's output
   carries one `cleanup: removed new <id>` line per new id.
5. **NFR-531 unchanged.** `test_previous_version_serves_the_migrated_schema_and_rolls_forward_with_no_failures`
   passes at the slice head with `failed requests=0` and min healthy ≥ 1, quoted.
6. **The script.** `bash -n deploy/roll-api.sh` rc 0; `shellcheck deploy/roll-api.sh` rc 0,
   or "absent" quoted (01:38:19 item 3); `uv run ruff check .` rc 0.
7. **The gate.** One SOLO compose-changer gate at the slice head when the lead grants it
   (the slice changes `deploy/`; the maintainer's entry "2026-10-18 01:51:05 BST" names the
   form: the isolated template, the minio guard, the shared stack restored from `tools-main`
   with keycloak's bind source quoted at END). Both halves read against the lead's baseline;
   `python3 scripts/audit-docs.py` reds only on working ids the lead classes.

## Tasks

1. **Base.** Branch from the `main` that contains SL-1258 and SL-1722; quote the head and
   `git merge-base --is-ancestor` for both merge commits.
2. **E4.8 red.** Rewrite the ingest test (PL 8061 E4.8 steps 1-5; request field names read
   from `UploadUrlRequest` at the base and quoted in LG-1814). Commit. Red A, then Red B
   (Acceptance 1).
3. **E4.8 green.** Fix only the test until Acceptance 2 holds. Commit.
4. **FD-1804 red.** Add the never-healthy failure-path test (Acceptance 3). Commit. Run it
   against the untrapped script: red.
5. **FD-1804 green.** Add the trap and the README sentence (Scope (ii)). Commit. Acceptance 4,
   5 and 6.
6. **Gate.** Acceptance 7 when granted. Close the LG-1814 entry.

## Sequencing

- **After SL-1258 merges.** `deploy/roll-api.sh`, the compose test file's roll helpers and
  the seeded test exist only on SL-1258's branch (P1, P5). SL-1813 branches from the `main`
  that contains both SL-1258 and SL-1722.
- **Due before the code freeze, Wed 4 Nov 2026, firm** (03:11:40 item 1). It is not an item a
  P2 closure may list instead.
- **S5 (SL-1259):** PL-1766 DP-S5-Q7, ruled (a) under DP-E1 (b): S5 writes its runtime tests in
  a new module; whichever of SL-1813 and SL-1259 merges second re-merges and re-runs the
  other's named tests. That binds here unchanged.

## Activation

The maintainer's one-line GO (03:11:40 item 1). This plan stays `draft` until that line; its
activation commit sets `PL-1812` and `SL-1813` `active` by their status lines only, citing it.

## Self-review before freeze

- Every acceptance item is a command or a recorded run; none asserts a time.
- No number range; every id listed singly. FD-1804 and PL 8061 are cited in space form, out of
  `relates:` (FD-1804 by the brief; PL 8061 because it is unminted and would not resolve).
- **Open for the lead:** PL 8061's E4.8 still names SL-1258 as owner; 09:55:22 (3) says
  *"Under (b), E4.3 ownership moves to the new SL in PL 8061 before S4's PR."* This plan does
  not edit PL 8061; that edit (pre-merge, so permitted) is the lead's to route.
