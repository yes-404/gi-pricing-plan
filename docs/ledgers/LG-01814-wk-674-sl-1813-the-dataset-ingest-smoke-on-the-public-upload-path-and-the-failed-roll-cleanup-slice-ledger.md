---
id: LG-1814
family: ledger
title: WK-674 slice SL-1813 — the dataset-ingest smoke on the public upload path (E4.8) and the failed-roll cleanup, FD-1804 (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-10-18                # minted 2026-10-18; filed 2026-10-18 as working id 8114
owner: executor
tree: ~
phase: P2
work: WK-674
slice: SL-1813
plans: [PL-1812]
corrected_by: []
relates: [PL-1812, SL-1813, SL-1258, SL-1722, FR-415, FR-406, FR-1776, NFR-531]
---

# LG-1814 — WK-674 slice SL-1813: E4.8 and the failed-roll cleanup

Working id (lead-reserved). Executed by `executor-8111`, branch `pl-8113-wk674-e48-2026-10-18`.
**Authority:** the maintainer, to-lead "2026-10-18 09:56:08 BST" (build SL-1813 now; its SOLO compose
gate at a free window) and PL-1812's GO at to-lead "2026-10-18 03:19:27 BST". The plan is PL-1812
(`docs/plans/PL-1812-…`); E4.8's text is PL 8061 (now `PL-1791`) §"Slice 4 — changes since
`PL-1714`", E4.8, `docs/plans/PL-01791-…:149-188`.

## Tasks

PHASE A — writing only (2026-10-18).

- **Base (Task 1).** Branch was `7886614a`; merged `origin/main` `eea416cab3c698a12bfc1f3620af0bc7906e4587`
  (`--no-ff`; only `docs/INDEX.md` conflicted, taken theirs, then regenerated in its own commit).
  `git merge-base --is-ancestor eea416ca HEAD` rc 0; `git merge-base --is-ancestor 39da0e1b HEAD`
  (SL-1722) rc 0.
- **Field names (Task 2).** Read at the base from `UploadUrlRequest`,
  `packages/model-schema/src/model_schema/uploads.py:23-29`: `media_type: str`, `parts: int`
  (1..10000, default 1), `extra="forbid"`. Response `UploadUrlResponse` (`:32-41`): `id`, `key`,
  `upload_id`, `urls`, `expires_in_s`. The single-part PUT sends `Content-Type: text/csv`
  (`backend/tests/test_api_blob_uploads.py`, SL-1722's `3a489dbf`).
- **Commit 1 — E4.8 rewrite, red first, not run:** `bd0edf1b8b8b48a90ec6adf72e904c664e8b6ff5`. The ingest test
  now runs upload-url → PUT → complete → POST versions, asserting both Jobs `succeeded` and their
  `result`. `_put_blob_inputs` stays (its caller is the score-batch test).
- **Commit 2 — FD-1804 failed-roll test, red first, not run:** `c708bfba3e7e69320d73097fcae7b67cce728bbf`. Committed
  before any trap; no change to `deploy/` yet.

PHASE B — the `GIP_DEPLOY_TESTS=1` runs (2026-10-18 12:19–12:40 BST; written by `executor-8111b`
under the lead's grant in `brief-executor-8111b-2026-10-18.md`). Every run: isolated project
`gip-s4-runtime` (own postgres/redis/minio on ephemeral ports, `lb` on 18000); gate-1 and
gate-1b free at each start; load1 at start 2.78–5.66 except NFR-531 (2.66, `small-test` free).

- **Red A, first run (a test defect, not the planned red).** Test at `51ad8a3a`, image
  `e2a2f79e0bba9f05b29ee585b52a9248899e4cf3`, `-k dataset_ingest`: rc 1, `socket.gaierror: [Errno -2]
  Name or service not known` at the PUT — the presigned URL names the compose-internal
  `minio:9000`, which the test process cannot resolve. Not `KeyError: 'id'`: the old image does
  return `urls`, so the failure came earlier than step 2's `upload['id']`.
- **Fix, test only** (`576c0294725366d36e16eca64f213f315e552b65`): connect to the published
  MinIO port (`_mapped('minio', 9000)`) and send the signed `Host: minio:9000` header unchanged.
- **Red A** (test with the fix, image `e2a2f79e`): rc 1, `E       KeyError: 'id'`, 55.86s.
- **Red B** (image and tree `51ad8a3a` + the same fix, `worker-io` left out of `_worker_services`
  by a scratch plugin not committed): rc 1, `AssertionError: job 01a14ec1-98a4-766f-b635-439dc909a9b7
  (blob.promote, queue io) is 'queued' after 90s: never consumed`.
- **Green, E4.8** (tree `576c0294`, every worker up): rc 0, `1 passed in 63.43s`;
  `job 01a14ec4-1cf7-7b6f-833d-56344c1bc29e kind=blob.promote queue=io -> succeeded in 1.0s (bound 90s)`;
  `job 01a14ec4-2159-77ac-bbd9-db2026c58a12 kind=dataset.ingest queue=io -> succeeded in 2.1s (bound 90s)`.
  The `ast` check of PL 8061 Acceptance 2 at `576c0294`: `[]`, rc 0; `git grep` shows both routes
  at `:663` and `:676`.
- **Red, FD-1804** (tree `576c0294`, untrapped `roll-api.sh`). First run: rc 1, `docker compose …
  up -d --wait --scale api=2 lb` returned non-zero in the test's setup, not reproduced by the same
  command by hand or on the re-run (cause unknown, recorded). Re-run: rc 1, `FAIL: 30a7a4712d2c not
  healthy within 30s`, then `AssertionError: a failed roll must leave exactly the pre-roll api
  containers ['54ade431c576', '9875870a0677'], found ['30a7a4712d2c', '54ade431c576', '8d65b5425209',
  '9875870a0677']` — the planned cause, four containers remain.
- **The trap + README sentence** (`f950840a3bfb8e956fa86d45d43456fef8d617f6`): `cleanup_new` on `EXIT`,
  armed before the scale-out, cleared before the first old stop.
- **Green, FD-1804** (tree `f950840a`): rc 0, `1 passed in 85.78s`; output
  `FAIL: 03ee49e152b3 not healthy within 30s`, `cleanup: removed new 03ee49e152b3`,
  `cleanup: removed new 07ec2a8ee4d1`, `cleanup: api containers now: 174ea5906811 5e748816f69c`.
- **NFR-531** (`-k previous_version_serves`, tree `f950840a`, load1 2.66 at start, `small-test` free):
  rc 0, `healthy api replicas across the roll: min=2 over 155 samples; failed requests=0`.
- **Script:** `bash -n deploy/roll-api.sh` rc 0; `shellcheck`: absent (`command not found`, rc 127).
  `ruff check .` rc 0; `mypy` rc 0; `ruff format --check backend/tests/test_deploy_stack_runtime.py`
  rc 1, and the file at `eea416ca` (before this slice) is also not format-clean (18 hunks at the
  head), so it is not reformatted here.
- **After:** no container of this project remains; keycloak bind
  `/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/tools-main/deploy/keycloak-local`; the four
  `gi-pricing-app:<sha>` tags built here were removed; `/` at 79% after, 74% before.

**Gate (Acceptance 7, closed):** SOLO compose-changer gate at head `229ac59bc2530464d8523a530c1e88966ff08c88`, tree `87b6d91c`; END `2026-10-18T13:28:30Z`; GREEN per the maintainer's entry "2026-10-18 14:29:09 BST" (`to-lead.md`). pytest `13 failed` (the known working-id cascade), `6306 passed`; smoke `7 passed`; demo journey 1210 s; D7 sum `+489842011`. The gate log is not pasted (it carries credential locals); it is read in `scratch/sl8111-gate/`.

**Owed:** FD (LOW, owner WK-674, D22): `deploy/roll-api.sh` builds `old` from running containers only, so a stopped pre-roll api container is removed as new on a failed roll (audit A4); ruled in the maintainer's entry "2026-10-18 14:33:47 BST" (`to-lead.md`).

## PRs

The PR is the one opened from `pl-8113-wk674-e48-2026-10-18` at the mint; its number is not recorded here, because the ledger is committed before the PR exists.

## Audit

*(Written by `auditor-8111`, 2026-10-18, on head `229ac59bc2530464d8523a530c1e88966ff08c88`, tree `87b6d91c2191df637ef8813ac1ad1ba3c63864c2`, range `origin/main...origin/pl-8113-wk674-e48-2026-10-18`. Code read-only; no test run by the auditor (no pytest, no docker); the gate is the lead's.)*

**1. Change set** (`git diff --stat origin/main...229ac59b`, 7 paths, +422 -10): `backend/tests/test_deploy_stack_runtime.py` (+96), `deploy/roll-api.sh` (+24), `deploy/README.md`, this ledger, PL 8113, `docs/roadmap.md` (SL 8111 row), `docs/INDEX.md`. No spec, `lb.conf`, or compose file changed (PL 8113 Scope (ii) item 2).

**2. Obligations, derived from PL 8113's Acceptance Standard and Scope first, then evidenced:**
- **Ancestry (two-way ledger match, `git merge-base --is-ancestor <sha> 229ac59b`):** `bd0edf1b`, `c708bfba`, `51ad8a3a`, `576c0294`, `f950840a`, `eea416ca`, `39da0e1b` all rc 0 (7/7). Every SHA the ledger names is reachable.
- **E4.8, no seeding (Scope i; Acc. 2):** `test_a_dataset_ingest_job_succeeds_through_the_compose_io_worker` (`test_deploy_stack_runtime.py:~648-690` at head) runs upload-url (`parts: 1`, `media_type: text/csv`) → PUT → complete → POST versions. Asserts READ: PUT `response.status == 200`; `promote["queue"] == "io"`; `promoted["result"] == {"kind": "blob", "ref": sha256(csv)}`; `job["queue"] == "io"`; `ingested["result"]["ref"].startswith("dataset_version:")`; `_wait_succeeded` (`:568`) returns the Job dict. PL-1791 Acceptance 2's `ast` check, run by the auditor on `git show 229ac59b:backend/tests/test_deploy_stack_runtime.py` (the command in PL 1791's Acceptance, `:247` of its file): `[]`, rc 0. **Met.**
- **Presigned PUT through the published MinIO port, signed Host kept (ruling 12:18:59/12:40:00):** the test splits the presigned URL, replaces `netloc` with `127.0.0.1:{_mapped('minio', 9000)}` and sends `Host: <signed netloc>` unchanged, with `Content-Type: text/csv` (the signed media type). No auth headers. Matches the ledger's Red A fix `576c0294`. **Met.**
- **Red first, E4.8 (Acc. 1):** Red A `KeyError: 'id'` at image `e2a2f79e` (after a first-run test defect, `socket.gaierror`, disclosed and fixed test-only in `576c0294`); Red B `never consumed` with `worker-io` left out. Both quoted with trees. Not re-run by the auditor. Red B used an uncommitted scratch plugin: not reproducible from the branch (A3). **Met, as recorded.**
- **FD 8112 trap (Scope ii.1):** `deploy/roll-api.sh` `cleanup_new` armed by `trap cleanup_new EXIT` before the scale-out (`:56`, scale-out `:59`), so a failure inside `up` is covered; the added ids are derived again (`comm -13` of the pre-roll `old` against `docker ps -aq`), not from `new`; each removed with `docker rm -f` and one `cleanup: removed new <id>` line; a final `cleanup: api containers now: …` line; exits with the original status (`local status=$?`, `exit "$status"`); `trap - EXIT` at `:74`, before the first `docker stop "$old"` (`:76`). The header comment says so in one sentence. Success path, step lines and timeout unchanged (diff shows only added lines plus the header). **Met.**
- **Red/green FD 8112 test (Acc. 3, 4):** `test_a_failed_api_roll_leaves_the_pre_roll_replicas_and_no_never_healthy_one` (`:~407-450`; `req("NFR-531")`; extra compose file in `tmp_path`, healthcheck `exit 1`; `roll-api.sh -t 30`). Asserts READ: `returncode != 0`; `sorted(_api_containers_all_states()) == old` (so none of the new ids exists, `docker ps -a`); `_api_containers(healthy_only=True) == old`; 20 requests via `lb` all `200`. Red at `576c0294`: four containers remain (planned cause); green at `f950840a`: `1 passed`, cleanup lines quoted. A first-run setup failure (`up -d --wait --scale api=2 lb` non-zero, not reproduced) is recorded "cause unknown". **Met.** See A2 on the `cleanup:` lines.
- **NFR-531 unchanged (Acc. 5):** `-k previous_version_serves` `min=2 over 155 samples; failed requests=0` at `f950840a`; and the gate smoke at head (below). **Met.**
- **Script (Acc. 6):** `bash -n` rc 0; `shellcheck` absent, quoted (rc 127); `ruff check .` rc 0 (ledger); `mypy` rc 0. **Met.**
- **README (Scope ii.3):** the F4 sentence (naming FD 8112) is replaced by one sentence; read in the diff. **Met.**
- **Score-batch seeding out of scope (P1):** `_put_blob_inputs` kept (`:607`), caller at `:723`. **As planned.**
- **FD 8112 on main:** the findings essay for FD 1804 on `origin/main` (its front matter carries the id and "filed under working id 8112"; it is not in this branch's INDEX, which predates it). **Verified.**

**3. Gate at head (Acc. 7), read in `scratch/sl8111-gate/` (not pasted; the log carries credential locals):** `gate.log` START `head 229ac59b…`, `tree 87b6d91c2191df637ef8813ac1ad1ba3c63864c2` = `git rev-parse 229ac59b^{tree}` (match); both slots held at start; END `2026-10-18T13:28:30Z`. ruff, mypy, import_linter, contracts, req_coverage rc files read; frontend `fe-test.log` `125 files, 795 tests passed`, type-check no errors; `pytest.log` `13 failed, 6306 passed, 16 skipped` (the 13 FAILED names are `test_audit_docs_*`/`test_doc_index`/`test_register_*`/`test_repository_invariants`, the known cascade of the working-id red; I did not re-derive that cascade, the maintainer's comm at 14:29:09 does); `smoke.log` `7 passed in 425.97s`, including the ingest test, the failed-roll test and `previous_version_serves…`; demo `journey done in 1210s`, D7 line present; keycloak restored from `tools-main`, bind source quoted at END. The slice smoke ran on the same SHA as the head. The audit-docs red is expected to be check 31 only (§5).

**4. Findings.**
- **A1 (LOW):** this ledger's `**Owed:** Acceptance 7` line and `## PRs` "None yet" are stale against the accepted gate; the gate record lives only in `scratch/`. The lead fixes at mint (a Gate line citing the head, tree and END).
- **A2 (LOW):** Acceptance 4 requires the output to carry one `cleanup: removed new <id>` line per new id; the test prints the output but asserts only the end state, not the lines. The state asserts are the stronger evidence; the lines were observed in the recorded run. Observation, no fix required.
- **A3 (LOW, disclosed):** Red B relied on an uncommitted scratch plugin; the red's cause (`never consumed`) is quoted but the method is not reproducible from the branch.
- **A4 (LOW, observation):** `cleanup_new` removes every `api` container of the project absent from `old`, and `old` is built from `docker ps -q` (running only). A non-running api container that pre-dates the roll would be removed on a failed roll. Such a container is not in rotation; PL 8113 §Scope is silent. Not constructed or run.
- **A5 (LOW, disclosed in the ledger):** a first-run setup failure (FD 8112 test) is "observed once, cause unknown" and did not recur in the gate smoke. Not a closure blocker; to be re-checked if it recurs.
- **A6:** `ruff format --check` on `test_deploy_stack_runtime.py` is red at `eea416ca` (before the slice) as well; not introduced here.
- **Mint note (2026-10-18, minter-8111):** the audit above is kept as written, quoting the working ids it was written against (PL 8113 = `PL-1812`, SL 8111 = `SL-1813`, LG 8114 = `LG-1814`, FD 8112 = `FD-1804`). A1 is fixed in the mint commit (the Gate and Owed lines above). A4 is owed as an FD (LOW, owner WK-674, D22), ruled in the maintainer's entry "2026-10-18 14:33:47 BST". A2, A3, A5 accepted as recorded; A6 no change.

**5. Working ids to re-point at the mint** (`git grep -n -E 'FD 8112|PL 8113|SL 8111|LG 8114' 229ac59b -- .`): live in code: `backend/tests/test_deploy_stack_runtime.py:411`, `:412`, `:652` (docstrings; they also use the mint's id in commit subjects, which are not edited). Live docs: `docs/ledgers/LG 08114` (lines 4, 20, 21, 41, 65, 73, plus the `docs/INDEX.md:1969` row, generated: regenerate), `docs/plans/PL 08113` (23 lines, its own text; `relates:` already uses hyphen ids), `docs/roadmap.md:1271` (SL 8111 row prose: "FD 8112", "PL 8113") and `docs/roadmap.md:1174` (a dated line in the SL-1258 row: "`SL 8111` (planned, `PL 8113`)", living doc). Frozen/quoted: `docs/ledgers/LG-01792-…:471` (closed ledger, quoting the F4 line: leave, or correct by a correcting record); `docs/plans/PL-01791-…:20` and `:149` (an active plan on main, quoting the re-point; the mint decides whether a plan delta edits it, under the "a plan is frozen from its first merge" rule).

**6. Proposed verdict:** every PL 8113 obligation (E4.8 on the public upload path with the presigned PUT through the published MinIO port, signed Host kept; the EXIT trap removing its own new replicas before the old are stopped; the red-first failed-roll test; NFR-531 unchanged; the SOLO gate at the head's tree) is delivered and evidenced; no requirement without evidence; findings A1–A6 are LOW and none blocks. Proposal only; the lead adopts, amends or rejects. MERGE-ACK: not yet given.
