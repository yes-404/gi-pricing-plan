---
id: PL-1791
family: plan
kind: map
title: WK-674 — SL-1258 owns the conversion of E4.3's seeded compose ingest test to the public upload path, red first by cause, once SL-1722 is on main; and the shared entrypoint with SL-1722, merge-second re-runs the other's guard — a dated Work-plan delta to PL-1714
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-18          # original date 2026-10-16, set at the filing; minted 2026-10-18
owner: planner
tree: 0877e6e7a756c4621890713a4d3b016e75e33654
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1714, PL-1690, PL-1666, PL-1721, SL-1258, SL-1722]
---

# PL-1791 — WK-674, SL-1258 owns the E4.3 ingest conversion; the shared entrypoint with SL-1722 (delta to PL-1714)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5 (`document-ids.md`
> §1.6, PL row: *"a change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's
> plan"*). It does not replace `PL-1666`, `PL-1690` or `PL-1714`; their bodies are frozen and are
> not edited. It adds no slice row. It **supersedes one clause of `PL-1714`** (line 73, quoted in
> §Authority) and adds **one task (E4.8), one shared-path rule (E4.9) and their acceptance items**
> to `SL-1258`. **Read `PL-1666`, then `PL-1690`, then `PL-1714`, then this file.** Where they
> differ, this file is the latest statement for what it changes. REQUIRED SUB-SKILL and bound
> skills: `PL-1666`'s list, unchanged; the executor is spawned from `.claude/roles/executor.md`.

Minted 2026-10-18 from working id 8061 as PL-1791, merged into the SL-1258 branch and minted in its mint commit (the maintainer (by delegation), to-lead 2026-10-18 03:38:37 BST and 03:19:27 BST).

Filed under **working id 8061**, reserved by the lead in `~/gi-pricing-plan.local/handover/eta.md`
at "2026-10-16 09:46:46 BST". Written 2026-10-16 from 09:48 BST (`TZ=Europe/London date`) by the
planner (seat planner-1714), on the lead's brief of the same morning. **Trees read:** `origin/main`
`0877e6e7a756c4621890713a4d3b016e75e33654` (#1307) for the plans and rulings; `SL-1258`'s branch
`origin/sl-1258-wk674-s4` at `7969b7782c1f45844d0b7db0ff5d6d246266f85f` for
`backend/tests/test_deploy_stack_runtime.py`, `backend/tests/test_worker_handler_coverage.py` and
its ledger (working id LG 9810); `SL-1722`'s branch `origin/sl-1722-wk1178-fd1730-upload-404` at
`0d4ebd898acc92892433d45efb6d9d349d671c2f` for its `docs/specs/07-platform.md` text. **No test or
code was run at planning time**; every claim below about behaviour is a reading of the code at
those trees.

## Authority

- **The ownership ruling:** the maintainer's (by delegation) entry in `to-lead.md`, "2026-10-16
  09:40:20 BST — Q1 RULED (P2, PL 8016): 11 + 1 is right, BY DERIVATION, not by count; …", its
  "Also ruled" bullet, verbatim: "**PL-1721's E4.3 acceptance conversion waiting for SL-1258:
  ACCEPTED, not dropped.** Its acceptance line must name SL-1258 as the owner of the conversion,
  and SL-1258's plan must carry it. Both are checked at their ACKs." This delta is the second
  half: SL-1258's plan carrying it.
- **SL-1722's GO:** the maintainer's (by delegation) entry "2026-10-16 09:42:48 BST — Maintainer:
  GO SL-1722 BUILD (FD-1730 upload-404 fix, PL-1721, WK-1178 P2)", conditions (b), verbatim: "The
  activation commit flips PL-1721 active. The acceptance line names SL-1258 as owner of E4.3 (my
  09:40:20).", and (e), verbatim: "Shared paths jobs.py/entrypoint.py with SL-1258: whichever
  merges second re-merges and re-gates the touched tests." (b) is the first half of the 09:40:20
  ruling, carried by `SL-1722`'s activation commit, not by this file; (e) is applied as E4.9.
- **The seeding permission it builds on:** the maintainer's (by delegation) entry "2026-10-14
  11:10:26 BST — Upload plan, the two points: "real io worker" defined (W2 OK, conditional); E4.3
  may seed now, with the conversion an OBLIGATION (re lead 11:09:44)", item (b), verbatim: "**PL
  8022 E4.3's compose ingest test may SEED NOW** (S4 is on the row-2 path, SL 8026 is not)", with
  the conditions that the `LG-` names the seeding, the test carries a marker comment naming SL
  8026 (now `SL-1722`), and "If SL 8026 has not merged by the 4 Nov freeze, the P2 closure record
  lists the seeded test as an open item." Item (a) defines "a real worker" (a separate Celery
  worker process from `app.worker.entrypoint` unmodified); E4.8's test is held to it as
  `PL-1714` E4.3 is.
- **The clause this delta supersedes:** `PL-1714` line 73 (the "E4.3's compose ingest test may
  seed (11:10:26 BST)" bullet), its clause: "the conversion to upload-url → PUT → complete → POST
  versions is an ACCEPTANCE line in SL-1722, not this delta's". **Superseded by the 09:40:20
  entry:** the conversion is `SL-1258`'s, carried here as E4.8. The rest of that bullet (the
  seeding now, the `LG-` naming it, the marker comment, the 4 Nov fallback, item (a)'s worker)
  stands. `SL-1722` converts nothing; its acceptance line names `SL-1258` as the owner.
- **DP-Q4 (b), so `backend/src/app/platform/jobs.py` is not S4's to write:** the maintainer's (by
  delegation) entry "2026-10-14 10:43:43 BST — PL 8022 RULED: DP-Q1 (b), DP-Q5 (a) + coverage
  sweep, DP-Q4 (b), DP-Q2 (a); red base @e1555803 OK (re lead 10:43:01)", verbatim: "**DP-Q4 →
  (b) now:** no route submits an allow-listed kind in P2, so a submit-time refusal guards nothing
  reachable. (a) lands in the first later-phase slice that adds such a route, recorded as an
  obligation line on LATER_PHASE_KINDS' docstring." The question was raised in the 10:36:42 entry
  ("Also decide in PL 8022 whether `jobs.submit` should REFUSE a kind with no production handler
  … Recommend; I rule."). `PL-1714`'s write set adds `jobs.py` "Under DP-Q4 (a) only" (its
  §"SL-1258's write set, widened"). Verified at the S4 branch: `git diff --stat
  origin/main...origin/sl-1258-wk674-s4 -- backend/src/app/platform/jobs.py` prints nothing at
  `7969b778`, and `LATER_PHASE_KINDS` is declared in `backend/tests/test_worker_handler_coverage.py:34`,
  not in `jobs.py`.
- **The reservation:** the lead's `eta.md` line "2026-10-16 09:46:46 BST", which names this
  delta's contents.

## Goal

The compose ingest proof of `PL-1714` E4.3 stops seeding: once `SL-1722`'s upload path is on
`main`, `SL-1258` rewrites it to walk upload-url → PUT → complete → POST versions through `lb`,
both Jobs `succeeded` on the compose `io` worker, red first by cause. The two slices that both
write `backend/src/app/worker/entrypoint.py` merge in either order without either slice's guard
going unseen. The Work's goal is `PL-1237`'s, unchanged.

## Premises (read at `0877e6e7`, `7969b778` and `0d4ebd89`)

- **P1 — the seeded test.** `backend/tests/test_deploy_stack_runtime.py:391` at `7969b778`,
  `test_a_dataset_ingest_job_succeeds_through_the_compose_io_worker`, calls
  `_seed_blob_inputs(workspace_id, csv, b"PAR1")` (`:404`), which writes the CSV blob and a
  `DatasetVersionRow` through the backend's own `Database` session (`:337-386`) so that
  `blob_readable_by` admits the digest; then `POST /api/v1/datasets/e43-ingest/versions` with
  `{"blob": csv_sha, "filename": "e43.csv"}`, asserts `job["queue"] == "io"` and calls
  `_wait_succeeded` (`:294-308`), which asserts `status == "succeeded"` and prints kind, queue,
  status, elapsed and bound. Its docstring (`:394-401`) opens "SEEDED, TO BE CONVERTED" and names
  the conversion as `SL-1258`'s (LG 9810).
- **P2 — the helper is shared.** `_seed_blob_inputs` also seeds the scoring frame for
  `test_a_score_batch_job_succeeds_through_the_compose_scoring_worker` (`:444`). That test is not
  in E4.8's scope; the helper stays while it has a caller.
- **P3 — the identity seeding is not the blob path.** `_stack_with_seeded_workspace` (`:315-334`)
  seeds the bench rating version and a key by `psql`. That is the caller's identity, the same
  carve-out `PL-1721` Task 2 makes for its `principal` and `grant` fixtures ("that carve-out is
  identity, not the blob path"). E4.8 does not remove it.
- **P4 — the public path `SL-1722` builds.** At `0d4ebd89`, `docs/specs/07-platform.md` (FR 8058,
  working id) states: `POST /api/v1/blobs/upload-url` records a Blob Upload and returns its `id`
  (the `blob_uploads.id` column row: "returned by `upload-url` and used in
  `/api/v1/blobs/uploads/{id}/complete`"); `POST /api/v1/blobs/uploads/{id}/complete` → **202**,
  Job `blob.promote`, whose result `JobResult(kind="blob")` names the digest. `PL-1721` Task 3
  routes `JobKind.BLOB_PROMOTE` to `JobQueue.IO`. So on compose the conversion needs the `io`
  worker twice (promotion, then ingestion), which `PL-1714` E4.2's derived consumer set covers
  without a compose edit: `io` is already a routed pool.
- **P5 — the red on a tree without `SL-1722`.** `PL-1721` Acceptance item 4 records R1's red on
  `main` as `KeyError: 'id'`: today's `upload-url` response carries no `id`. A converted test
  run against a compose built from a tree without `SL-1722` fails at that step, by that cause.
- **P6 — S4's guard reads registrars by name.** `backend/tests/test_worker_handler_coverage.py` at
  `7969b778` derives the routed kinds from `DEFAULT_QUEUE_FOR_KIND` (`:22`, `:79`) and collects
  the registered ones by parsing `entrypoint.py` for module-level calls of imported functions named
  `register_*_handlers` (`entrypoint_registrars`, `:45-52`). A handler registered any other way is
  invisible to it, and a routed kind it cannot see is reported as having no handler. `LATER_PHASE_KINDS`
  may never list a P2 kind (`:29-33`); `blob.promote` is P2 (`SL-1722`).
- **P7 — the shared paths today.** `SL-1258` writes `entrypoint.py` (`PL-1714` E4.4, E4.6, E4.7 (a));
  at `7969b778` it has not yet (its branch holds the pre-GO reds). `SL-1722` writes
  `entrypoint.py` (the `blob.promote` registration) and `jobs.py` (the `BLOB_PROMOTE` route,
  `PL-1721` Task 3); at `0d4ebd89` it has written neither. `SL-1258` does not write `jobs.py`
  (§Authority, DP-Q4 (b)), but its guard **reads** `jobs.py`'s table, so `SL-1722`'s route changes
  what S4's guard demands.

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | `SL-1258` — Slice 4: the deployment path | `PL-1714`'s scope, plus E4.8 and E4.9 below | `PL-1714`'s set, unchanged. **Cited, not added:** `07` FR-421 and FR 8058 (working id; `SL-1722`'s), the path E4.8 walks | `PL-1714`'s, plus: E4.8 needs `SL-1722` merged (§Ordering) | E4.8 + E4.9: under one hour of edit, plus one build-window run |

No requirement id is added or removed. E4.8 keeps the test's markers, `req("FR-415")` and
`req("FR-406")`; it does not mark `SL-1722`'s requirement, whose proof is `SL-1722`'s R1.

### Slice 4 (`SL-1258`) — changes since `PL-1714`

- **E4.8 — the conversion of E4.3's ingest test to the public upload path.** Owner `SL-1258` at filing; re-pointed at the mint to **SL 8111 (planned, PL 8113)** (the maintainer (by delegation), to-lead 2026-10-18 03:11:40 BST, DP-E1 (b)) (the
  09:40:20 entry). Built only once `SL-1722` is on `main` and in `SL-1258`'s base (§Ordering).
  - **The rewrite**, in `backend/tests/test_deploy_stack_runtime.py`, same test name, same markers,
    same `_stack_with_seeded_workspace` (P3), no `_seed_blob_inputs` call. All requests go
    through `lb` with `_api`, except the `PUT`, which goes to the presigned URL (MinIO) with no
    auth headers:
    1. `POST /api/v1/datasets` with `{"slug": "e43-ingest", "currency": "GBP"}`, as today.
    2. `POST /api/v1/blobs/upload-url` for the CSV as **one part** (`media_type` `text/csv`; the
       body's field names as `SL-1722`'s merged request model declares them, read at the base and
       quoted in the `LG-`). Keep `id` and the URL. One part is enough here: the multipart path
       is `SL-1722`'s R1's to prove (`PL-1721` Task 2); this test proves the compose `io` worker.
    3. `PUT` the CSV bytes to the URL with the media type `SL-1722`'s single-part PUT sends
       (its `3a489dbf`: "send the media type on a single-part PUT").
    4. `POST /api/v1/blobs/uploads/{id}/complete` → `202`; assert `job["queue"] == "io"`;
       `_wait_succeeded(job, headers, INGEST_BOUND_SECONDS)`; then assert the Job's
       `result == {"kind": "blob", "ref": hashlib.sha256(csv).hexdigest()}`.
    5. `POST /api/v1/datasets/e43-ingest/versions` with `{"blob": <that digest>, "filename":
       "e43.csv"}`; assert `job["queue"] == "io"`; `_wait_succeeded`; assert
       `result["ref"].startswith("dataset_version:")`.
  - **Both Jobs assert `succeeded` and their output**, never only terminal (the 10:36:42 entry's
    correction; the 09:42:48 entry's condition (d) holds `SL-1722`'s worker test to the same).
  - **The docstring** drops "SEEDED, TO BE CONVERTED" and names this delta and the 09:40:20 entry.
    `_seed_blob_inputs`' docstring drops "to be replaced by the public upload path in SL 8026" if
    the batch test is then its only caller, and says so (P2).
  - **Red first, by cause (committed before the rewrite's base contains `SL-1722`, or run on a
    compose built from such a tree):**
    - **Red A, no completion step:** the converted test against a compose built from `SL-1258`'s
      head before its re-merge of the `main` that contains `SL-1722` fails at step 2 with
      `KeyError: 'id'` (P5). Any other failure is a test defect.
    - **Red B, no `io` consumer:** on the merged tree, with the `io` worker service stopped
      (`docker compose stop` on the service `PL-1714` DP-Q1 (b) names for `io`), the
      `blob.promote` Job ends `queued` past its bound and `_wait_succeeded`'s message says
      `never consumed`. It shows the proof still rests on the compose `io` worker, as the
      seeded test's red did.
    - **Green:** on the merged tree with every worker service up, the test exits 0, printing both
      Jobs' kind, queue, status, elapsed and bound.
  - **Where it runs:** `PL-1666` D0.5 and `PL-1690` E4.3, unchanged: behind `GIP_DEPLOY_TESTS=1`,
    in a build window the lead grants, never in the gate. The `LG-` quotes the command, the
    output, the tree and both reds.
  - Acceptance items 2 and 3.

- **E4.9 — the shared path with `SL-1722`, merge-second re-runs the other's guard.**
  `PL-1721`'s side is its §"The write set", "Shared paths for the lead's census"
  (`PL-1721:344-346`); this is `SL-1258`'s.
  - **Paths:** `backend/src/app/worker/entrypoint.py` is written by both (P7).
    `backend/src/app/platform/jobs.py` is written by `SL-1722` only, and read by `SL-1258`'s guard
    (P6, P7).
  - **The rule:** whichever of `SL-1258` and `SL-1722` merges second re-merges `origin/main`
    (`git merge --no-ff`, never a rebase) after the first has merged, resolves `entrypoint.py`
    so that both slices' registrar calls are present, and re-runs, through
    `~/gi-pricing-plan.local/handover/run-small.sh` (three files, RL-1626), on the merged tree:
    `backend/tests/test_worker_handler_coverage.py`, `backend/tests/test_deploy_stack.py` and
    `backend/tests/test_upload_to_ingest.py`. The guard must pass **with `blob.promote` routed**,
    which means it sees `blob.promote` registered.
  - **The registration form the guard can see:** `SL-1722` registers `blob.promote` through a
    function named `register_*_handlers` that `entrypoint.py` imports and calls at module level
    (an existing registrar, such as the data handlers', or a new `register_blob_handlers`), never
    by a direct `registry` call in `entrypoint.py` (P6). If `SL-1722` merges first, `SL-1258`'s
    re-run is where a form the guard cannot see would show, as `blob.promote` named in the
    guard's `missing` list; `SL-1258` stops and reports it to the lead and does not edit
    `SL-1722`'s registration or the guard to pass. If `SL-1258` merges first, `SL-1722`'s
    Task 0 already confirms the guard (`PL-1721:225-227`).
  - **No allow-list entry:** `blob.promote` is never added to `LATER_PHASE_KINDS` (P6).
  - **The full gate** of whichever merges second runs on the merged tree, as each slice's own
    acceptance already requires; the three-file re-run is the targeted proof the `LG-` quotes
    before it.
  - Acceptance item 4.

### SL-1258's write set

`PL-1714`'s, unchanged in paths: E4.8 edits `backend/tests/test_deploy_stack_runtime.py`, already
in it. E4.9 adds no path; under it, `entrypoint.py` may carry `SL-1722`'s merged lines through
the re-merge. `jobs.py` stays out of `SL-1258`'s write set (DP-Q4 (b)).

## Ordering

- **E4.8 needs `SL-1722` merged.** The converted test calls `upload-url`'s `id` and the
  `complete` route, which exist only once `SL-1722` is on `main` (P4, P5). `SL-1722` converts
  nothing (`PL-1721` §"The write set", Out of scope: "the PL-1714 compose ingest proof (P10)"); it
  does not wait for `SL-1258` (DP-U2 ruled W2, `RL-1724`).
- **If `SL-1722` is on `main` before `SL-1258`'s merge:** `SL-1258` re-merges `main` (`PL-1666`
  D0.4), builds E4.8 in its own PR, and runs Red A against its pre-re-merge head.
- **If `SL-1258` is ready to merge before `SL-1722` is on `main`:** DP-E1.
- **If `SL-1722` has not merged by the 4 Nov freeze:** the P2 closure record lists the seeded test
  as an open item (the 11:10:26 entry, item (b)), owner `SL-1258`.

## Decision points

| DP | Question | Options | Recommendation | Kind | Blocking? | Resolved by |
|---|---|---|---|---|---|---|
| **DP-E1** | `SL-1258` is ready to merge and `SL-1722` is not on `main`: where does E4.8 land? | **(a) `SL-1258` waits** for `SL-1722` and carries E4.8 itself. **(b) `SL-1258` merges seeded**, as the 11:10:26 entry permits, and E4.8 becomes its **own slice id**, minted in the next batch, owner WK-674; `SL-1258`'s `LG-` names the seeded test as replaced by it. Under (b), E4.3's ownership moves to that new `SL-` in this delta before `SL-1258`'s PR. A second PR under `SL-1258`'s id is **refused** (lean P2 item 1: one slice = one PR + one `SL-`). *(Amended 2026-10-16, before the mint, by the planner, on the maintainer's (by delegation) entry "2026-10-16 09:55:22 BST — Maintainer: GO SL-1258 BUILD (WK-674 S4, compose stack + FD-1713)", item (3): the row's (b) put E4.8 in a follow-up PR under `SL-1258`'s id, and its (c) moved E4.8 to `SL-1722` or a new row; the ruling names (a) and (b) only.)* | **Ruled, no recommendation:** item (3), verbatim: "The lead picks (a) or (b) at S4's PR time from the gate queue. Under (b), E4.3 ownership moves to the new SL in PL 8061 before S4's PR." | scope (ruled by the 09:55:22 entry, item (3); the pick is the lead's) | no — only in that case, at `SL-1258`'s PR | the lead, (a) or (b), by a dated line at `SL-1258`'s PR time |

## Acceptance Standard

1. **This delta passes the docs checks on its own branch**, the working-id lines excepted (check 32's "does not resolve in docs/INDEX.md" on this plan's own id and check 39's stale `docs/INDEX.md`, both cleared at mint):
   `python3 scripts/audit-docs.py` exits 0 apart from them.
2. **E4.8, no blob seeding in the ingest test:** at `SL-1258`'s head that contains E4.8,
   ```
   git show <head>:backend/tests/test_deploy_stack_runtime.py | python3 -I -c "import ast,sys; s=sys.stdin.read(); f=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name=='test_a_dataset_ingest_job_succeeds_through_the_compose_io_worker'); b=ast.get_source_segment(s,f); bad=[w for w in ('_seed_blob_inputs','psql','unit_of_work','session.add','SEEDED, TO BE CONVERTED') if w in b]; print(bad); sys.exit(1 if bad else 0)"
   ```
   prints `[]` and exits 0, and `git grep -n -E "blobs/upload-url|/complete" <head> --
   backend/tests/test_deploy_stack_runtime.py` prints both routes inside that test.
3. **E4.8, the run:** in the build window,
   `GIP_DEPLOY_TESTS=1 GIP_N_SHA=<head> uv run pytest -q backend/tests/test_deploy_stack_runtime.py -k dataset_ingest`
   exits 0 with both Jobs printed `succeeded`, each with its bound and elapsed time; the `LG-`
   quotes Red A (`KeyError: 'id'`, with its tree) and Red B (`never consumed`, the `blob.promote`
   Job, the `io` service stopped), each by its stated cause.
4. **E4.9:** the `LG-` of whichever slice merges second names the merged tree and quotes rc 0 of
   `run-small.sh <worktree> backend/tests/test_worker_handler_coverage.py backend/tests/test_deploy_stack.py backend/tests/test_upload_to_ingest.py`
   on it; at that tree `git grep -n BLOB_PROMOTE -- backend/src/app/platform/jobs.py` prints the
   route and `git grep -n -E "register_[a-z_]+_handlers\(\)" -- backend/src/app/worker/entrypoint.py`
   prints both slices' registrar calls, and `git grep -n blob.promote --
   backend/tests/test_worker_handler_coverage.py` prints nothing (no allow-list entry).
5. **The ownership is stated twice and agrees:** `SL-1258`'s `LG-` carries E4.8 with owner
   `SL-1258`, citing this delta and the 09:40:20 entry; `SL-1722`'s activation commit names
   `SL-1258` as the owner (the 09:42:48 entry's condition (b)). Both are checked at their ACKs.
6. **DP-E1** carries a dated ruling if its case arises, or the `LG-` records that it did not.
7. `PL-1714` Acceptance items 2 to 10 hold unchanged; its item 4's ingest test is the seeded one
   until E4.8 lands, and E4.8's run replaces its ingest limb after.

## Activation

E4.9 binds both slices from this delta's mint. E4.8 is GO-able inside `SL-1258` when `SL-1722` is
on `main` and in `SL-1258`'s base. `SL-1258`'s own GO conditions are `PL-1714`'s Activation,
unchanged; this delta adds none to them. It goes `active` with the plans `SL-1258`'s activation
commit sets `active`, by its status line only.
