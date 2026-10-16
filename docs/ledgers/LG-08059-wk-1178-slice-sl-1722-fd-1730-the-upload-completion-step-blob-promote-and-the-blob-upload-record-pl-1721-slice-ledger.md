---
id: LG-8059
family: ledger
title: WK-1178 slice SL-1722 — FD-1730, the upload-completion step (blob.promote and the Blob Upload record), PL-1721 slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-16
owner: executor
tree: bba89d66f28fb469e27b25cede67086d518c95ec
phase: P2
work: WK-1178
slice: SL-1722
plans: [PL-1721]
corrected_by: []
relates: [PL-1721, SL-1722, FD-1730, RL-1724, FR-421, FR 8058, SL-1258]
---

# LG 8059 — SL-1722: the upload-completion step

Working id 8059 (space form, unminted). Branch `sl-1722-wk1178-fd1730-upload-404`, worktree
`.claude/worktrees/sl-1722`. Plan `PL-1721` (`active`, activated at `d48705ac`), binding `RL-1724`.

**GO:** the maintainer's entry "2026-10-16 09:42:48 BST — Maintainer: GO SL-1722 BUILD (FD-1730
upload-404 fix, PL-1721, WK-1178 P2)" in `to-lead.md`. Conditions, in its words condensed:

- **(a)** the red-first commit `3a489dbf` is on `origin/sl-1722-wk1178-fd1730-upload-404`; this LG lists the 10 reds by node id with each one's cause at `3a489dbf`; a red by import or fixture error is not red by cause.
- **(b)** the activation commit flips `PL-1721` active; its acceptance line names `SL-1258` as owner of E4.3 (the 09:40:20 entry).
- **(c)** the column names follow `RL-1724`; any divergence is a STOP to the maintainer, never a silent pick.
- **(d)** the W2 worker test asserts BOTH Jobs `succeeded` with output (a blob ref; a Dataset Version id), never "terminal".
- **(e)** `jobs.py` / `entrypoint.py` are shared with `SL-1258`: whichever merges second re-merges and re-gates the touched tests. The SL-1722 PR also merges AFTER D18 (the GO's item (4)).
- **(f)** writing only in the window; the gate runs after SL-1543 and SL-1341 under the standard grant terms; today's last full-gate grant is 18:00, otherwise it gates next session.

**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1721` / `SL-1722`: the completion step `FR-421` implies and was never built (`FD-1730`) —
`POST /api/v1/blobs/uploads/{id}/complete` returning 202 and a `blob.promote` Job on the `io`
queue; the `blob_uploads` table (`BlobUploadRow`, migration `e7c3a9b15d82` on `d4e81b7a2c95`);
the staging lifecycle rule; the Job result owned by the caller's workspace. Requirement: FR 8058
(working id; spec commit `0d4ebd89`, `07` §2, §4.5, §5.1, §5.2), with `FR-421`. Glossary term
"Blob Upload": `00` §2.1 (authoritative), pointed at from `07` §2 (added in this ledger's
audit follow-up, A6).

### Task list

Discharged so far, in order (commit, first line):

1. `ca76bb4e` — red-first tests (446 lines over three files).
2. `3a489dbf` — red-first fix: media type on a single-part PUT; R4 asserts a Blob Upload was recorded before ageing it.
3. `0d4ebd89` — spec: FR 8058, Blob Upload, `blob.promote`.
4. `d48705ac` — activation of `PL-1721`, `SL-1258` owns E4.3's conversion.
5. `0f80af62` — implementation (`blob.promote` Job, `blob_uploads`, staging lifecycle).
6. `bba89d66` — the 09:46:32 renames (below).
7. Pre-gate fixes (this commit): A2 (docstring), A6 (glossary and §4.5 name marks), this ledger.

**The ten reds at `3a489dbf`, by node id** (every test the red-first commits add; the
cause column is to be filled from the run — see OWED):

| # | Node id | Cause at `3a489dbf` |
|---|---|---|
| 1 | `backend/tests/test_api_blob_uploads.py::test_upload_url_records_an_upload_and_returns_its_id` | OWED: run |
| 2 | `…::test_completing_another_workspaces_upload_is_the_missing_404` | OWED: run |
| 3 | `…::test_a_completion_past_the_deadline_is_refused` | OWED: run |
| 4 | `…::test_a_repeated_completion_returns_the_first_job` | OWED: run |
| 5 | `…::test_a_missing_part_fails_the_promotion_by_name` | OWED: run |
| 6 | `…::test_identical_bytes_promote_to_one_blob` | OWED: run |
| 7 | `…::test_a_promoted_blob_is_retained` | OWED: run |
| 8 | `…::test_a_promoted_digest_downloads_only_in_its_workspace` | OWED: run |
| 9 | `backend/tests/test_blobs.py::test_ensure_bucket_sets_the_staging_lifecycle_rule` | OWED: run |
| 10 | `backend/tests/test_upload_to_ingest.py::test_a_file_uploaded_through_the_public_api_ingests_to_a_succeeded_version` | OWED: run |

The list above is derived from the diff of `ca76bb4e` (`def test_` lines added), not from a
run; no cause is claimed until the reds are run at `3a489dbf`.

### The six column names (condition (c))

`RL-1724` describes the fields of the pending record without naming every column. Both rulings
are the maintainer's, in `to-lead.md`:

- "2026-10-16 09:44:39 BST — SL-1722 condition (c) — the three column names CONCURRED":
  `part_count`, `s3_upload_id`, `job_id` fill a gap and do not depart from the ruling. No rename.
  Riders: (1) a name that reaches an API response or request is a model-schema shape, regenerated
  into `docs/contracts`, never hand-written; (2) the spec says `s3_upload_id` is the API's
  `upload_id`.
- "2026-10-16 09:46:32 BST — SL-1722 condition (c), the second three names — 2 RENAMES before
  the gate": `principal_id` accepted; `digest` → `sha256` (a foreign key to `blobs.sha256`);
  `key` → `staging_key`. Applied at `bba89d66`. The 09:44:39 riders apply to all six.

`07` §4.5 marks `sha256` and `staging_key` as named by that ruling and the other four as
executor-named with the 09:44:39 concurrence.

### Pre-gate condition check (executor, 2026-10-16, writing only — no run)

Read at branch head `ac21f3cf` plus this commit, against the maintainer's entries in `to-lead.md`.
"Read" means read in the file, not run.

| Cond. | Source entry | Status | Locator |
|---|---|---|---|
| (a) | 09:42:48 | Red-first commit `3a489dbf` is an ancestor of the branch; the push is confirmed by `git ls-remote`. 10 test functions were added by `ca76bb4e` (the table above). The causes are OWED: not yet run. | `git log origin/main..HEAD`; table above |
| (b) | 09:42:48 | MET. `PL-1721` front matter `status: active`; the activation note names `SL-1258` as owner of E4.3's conversion. | `docs/plans/PL-01721-…md` :6 and the "Activated 2026-10-16" paragraph |
| (c) | 09:42:48, 09:44:39, 09:46:32 | MET as written. Six names agree across ORM, migration and spec: `principal_id`, `staging_key`, `s3_upload_id`, `part_count`, `job_id`, `sha256` (FK to `blobs.sha256`). No `digest` or `key` column remains. Rider (2): `07` §4.5 says `s3_upload_id` is the `upload_id` the response returns. Rider (1): see OPEN Q1. | `backend/src/app/db/models.py` `BlobUploadRow`; `backend/migrations/versions/e7c3a9b15d82_blob_uploads.py`; `docs/specs/07-platform.md` §4.5 |
| (d) | 09:42:48 | MET by reading. Both Jobs are asserted `== "succeeded"` (never "terminal"): the promote Job with `result == {"kind": "blob", "ref": digest}`, the ingest Job with `result["ref"]` starting `dataset_version:`. | `backend/tests/test_upload_to_ingest.py` :150-152, :161-163 |
| (e) | 09:42:48 | OWED at merge. Shared paths `jobs.py` (+1 line here) and `entrypoint.py` (not touched here); whichever of this and `SL-1258` merges second re-merges and re-gates the touched tests. Merge after D18. | `git diff --stat origin/main...HEAD` |
| (f) | 09:42:48 | MET. No run in this window. | — |
| glossary | 09:53:28 | MET after this commit. "Blob Upload" is defined in `00` §2.1 before any other use; `07` §2 now carries a pointer row (the ledger said so, but the row was missing at `ac21f3cf`; added in this commit). | `docs/specs/00-overview.md` §2.1; `docs/specs/07-platform.md` §2 |
| W2 PASSED | 09:53:28 | NOT MET YET (a run). The W2 fixture `io_worker` calls `pytest.skip` when Redis is unreachable. `python.yml` has a redis service, so CI reads PASSED; a local run must be read as a red if it prints `s`. OPEN Q2. | `backend/tests/test_upload_to_ingest.py` :71-74 |

### DP-7: migration head order (09:51:01, item 3)

`e7c3a9b15d82` (this slice) has `down_revision = "d4e81b7a2c95"`, which is the single head at
`origin/main` `0877e6e7`. `SL-1274`'s `f2b6d90a4c17` on `origin/sl-1274-wk690-s4-factor-expression`
also has `down_revision = "d4e81b7a2c95"`. If both reach `main`, there are two heads. Neither has
merged. `SL 8017` is a working id; its branch `origin/pl-8016-wk1178-fd8007-remedy-2026-10-14`
adds no migration at the time of reading, so it owes no re-point from this side. Rule (09:51:01):
whichever merges later re-points its `down_revision` to the earlier one's revision before its gate;
if the earlier merges after the later is gated, the re-point is the only allowed post-gate code
change, with a small-test run of `alembic upgrade head`, the single-head test and
`alembic downgrade -1 && upgrade head`, rc recorded here. Merge order is not decided. **Re-point owed
by: whichever of `e7c3a9b15d82` / `f2b6d90a4c17` merges second.** Not done in this commit.

### OPEN questions to the lead

1. **Rider (09:44:39 (1)).** `s3_upload_id` reaches the `upload-url` response as `upload_id`, and this
   slice adds `id` to it. That response (`UploadUrlResponse`) is a hand-written class in
   `backend/src/app/api/blobs.py`, as it was at `0877e6e7`; it is not in `model-schema`. The
   rider reads "regenerated into docs/contracts, never hand-written". Not moved here: moving a
   pre-existing shape into `model-schema` is a wider change than the write set. Lead to rule (STOP to
   the maintainer if it needs a move).
2. **A4.** Whether to turn the `io_worker` Redis `pytest.skip` into `pytest.fail`, so that the test
   cannot be skipped by construction. Not changed: it is stricter than the maintainer's reading rule.

### Gate

OWED. No gate has run on this branch. Under (f) it runs after SL-1543 and SL-1341 under the
standard grant terms. Reading rule adopted at A4: Acceptance 3 (the W2 worker test) must read
PASSED, never skipped, with both Jobs `succeeded` and output.

### Audit

The lead's pre-gate read, "2026-10-16 09:52:42 BST — Lead: SL-1722 PRE-GATE READ" in
`from-lead-2026-10-09.md`, at `origin/main...bba89d66f28fb469e27b25cede67086d518c95ec` (tree
`50bda9e4`). Verdicts (the lead's; the formal slice audit is the auditor's, later):

| # | Finding | Lead verdict | State |
|---|---|---|---|
| A1 | `generated.json` not regenerated (Acceptance 7; `generate-contracts --check` red). | HIGH if unfixed; known. | OWED: regenerate in the post-gate seat; verify `job.schema.json`'s `blob.promote` line is regen-reproduced byte for byte, not hand-edited. |
| A2 | `db/models.py` ~:2608 130-character line (E501); a stale "executor's names … (lead-accepted)" sentence after the rename. | MEDIUM; fix before the gate. | Done in this commit: line wrapped; the sentence now says the maintainer concurred (09:44:39) and ruled `sha256`/`staging_key` (09:46:32). |
| A3 | `blobs.py` `__all__` order (RUF022). | Confirm with ruff after GATE END; fix if red. | OWED. |
| A4 | The W2 test skips if Redis or MinIO is unreachable. | MEDIUM; adopted as a gate-reading rule: Acceptance 4 reads PASSED, never skipped. | Reading rule recorded in Gate. |
| A5 | No FR 8058 marker (`req("FR-<minted>")`). | Deferred with owner: the SL-1722 PR adds it at its mint, before merge; `req-coverage` must evidence it on the PR. | OWED: at mint. |
| A6 | "Blob Upload" is added to `07` §2 only; `CLAUDE.md` §7 puts a new term in `00` §2 first. | Owed before the gate. | Done in this commit: entry added to `00` §2.1; `07` §2 now points at it. |
| A7 | The red-first commits `ca76bb4e` / `3a489dbf` pre-date the GO (09:42:48). | LG note. | Recorded: the commits are 08:34:02Z and 08:36:09Z (`%aI`); the GO is 09:42:48 BST. Acceptance 3 requires only the spec before the source, which holds (`0d4ebd89` before `0f80af62`). |
| A8 | An orphan multipart upload is bounded by the 2-day lifecycle. | Accepted. | — |

Conformant by the lead's reading: columns in §4.5, model and migration agree; `e7c3a9b15d82` on
`d4e81b7a2c95`; `blob.promote` through `register_data_handlers`; no hand-written wire shape; the
15 changed paths all in the write set.

### OWED

- Task 0 spike (library behaviour, per the plan).
- The ten reds run at `3a489dbf`, each by node id and cause (condition (a)); R1's later points.
- `generate-contracts` regeneration and `--check` (A1).
- `ruff check` after the gate, for A3 (RUF022) and any other (E501 is fixed by A2).
- After GATE END (SL-1455), in this order, none run in this window:
  1. Task 0 MinIO spike (library behaviour, per the plan).
  2. The ten reds at `3a489dbf` by node id with each cause (fill the table; a red by import or fixture error is not red by cause).
  3. `uv run python scripts/generate-contracts.py` then `--check` (A1; `upload-url` response gains `id`, new route, `blob.promote` in `job.schema.json`).
  4. `uv run ruff check .` (A3 RUF022; the migration's tuple/format style).
  5. `run-small` R1–R9, `backend/tests/test_blobs.py`, the single-head migration test.
  6. W2 `test_upload_to_ingest.py`, read PASSED (not `s`).
  7. Docs checks under the gate-2 flock: `audit-docs.py`, `doc-index.py --check`.
- The runs: `run-small` R1–R9, `test_blobs`, one-head; the W2 worker test PASSED, both Jobs `succeeded` with output (d).
- The breakers (broken-input proofs of the new checks).
- The FR 8058 marker (`req("FR-<minted>")`) at mint (A5).
- The mint: working ids to minted ids; `status: closed` only at slice close.
- Merge after D18 and after `SL-1258` order is settled (e).

### Build log

- 2026-10-16: red-first commits `ca76bb4e`, `3a489dbf` (08:34Z, 08:36Z); spec `0d4ebd89`; activation `d48705ac`; implementation `0f80af62`; renames `bba89d66` (08:49Z).
- 2026-10-16: the lead's pre-gate read 09:52:42 BST; this ledger and fixes A2, A6 added by the executor in one commit, writing only (no test run, the SL-1455 latency window being open).

### DP-1722-WIRE: the route shapes move into model-schema (2026-10-16)

- **Ruling A** (the maintainer (by delegation), `to-lead.md` "2026-10-16 10:16:17 BST — Maintainer: DP-1722-WIRE → (a), BOTH shapes of the route move into model-schema inside SL-1722"): both hand-written shapes move into `packages/model-schema` inside SL 1722; the new routes' shapes are model-schema from the start. Wire names stay byte-identical (`key`, `upload_id`, `urls`, `expires_in_s`; `media_type`, `parts` ge=1 le=10000; `frozen`, `extra=forbid`); the API's `key` is not renamed (it is the staging key; the column is `staging_key`). Proof demanded: `generate-contracts.py --check` rc 0, `pnpm generate:api` and type-check rc 0, and a grep showing no `class UploadUrl` left in `backend/src`.
- **Ruling B** (the lead, `from-lead-2026-10-09.md` "2026-10-16 10:15:52 BST", endorsed by item 4 of ruling A): the `io_worker` fixture (`backend/tests/test_upload_to_ingest.py:63`, used only by the W2 test) changes its Redis-unreachable `pytest.skip` (was :71-74) to `pytest.fail` with the reason. Now at :74-76.
- **Write-set widening** (ruling A item 1): `packages/model-schema` (new `uploads.py`, two exports in `__init__.py`), `docs/contracts` (regeneration OWED, not hand-edited), plus the registrations the generator's own guards force: `scripts/generate-contracts.py` `GENERATED_SHAPES` (two slugs), `backend/tests/test_contracts.py` `ONE_SIDED_SLUGS` (two first-written-form entries; the guard fails a generated-only slug that is undeclared), `scripts/audit-docs.py` `_CONTRACT_ARTIFACT_PATHS` (two generated schema paths).
- **Moved classes** (old file:line, at this branch, which is `f1eb0d9b`; main had them at :58 and :65) to new file:line:
  - `UploadUrlRequest`: `backend/src/app/api/blobs.py:69` to `packages/model-schema/src/model_schema/uploads.py:23`.
  - `UploadUrlResponse`: `backend/src/app/api/blobs.py:76` to `packages/model-schema/src/model_schema/uploads.py:32`.
  - The route imports both from `model_schema`; the now-unused `BaseModel` and `ConfigDict` imports in `blobs.py` are dropped.
- **New wire shapes of the new routes:** none to add. `POST /blobs/uploads/{id}/complete` returns the existing `Job` (202), and the Blob Upload record is not on the wire. The one added field is `UploadUrlResponse.id` (SL 1722's own).
- **Observed now (git only):** `git grep -n 'class UploadUrl' -- backend/src` prints nothing, rc 1.
- **OWED after GATE END (SL-1455), none run in this window** (no pytest, uv, mypy, ruff, pnpm, generate-contracts, audit-docs):
  1. `uv run python scripts/generate-contracts.py`, then `--check` rc 0; the `docs/contracts` diff quoted here, and it must show ONLY the move (`UploadUrlRequest`/`UploadUrlResponse` now also as `schemas/generated/upload-url-request.schema.json` and `upload-url-response.schema.json`, the OpenAPI components unchanged in shape), the one added field `id`, and the new route `POST /blobs/uploads/{upload_id}/complete` (and `blob.promote` in `job.schema.json`). Anything else in the diff is a defect to explain.
  2. `pnpm --dir frontend generate:api` and `type-check`, rc 0 each.
  3. `uv run ruff check .`, `uv run mypy`, `uv run lint-imports`.
  4. `backend/tests/test_contracts.py` (the `ONE_SIDED_SLUGS` guard and the generated-versus-authored comparisons), `backend/tests/test_deployment_route_types.py`, `backend/tests/test_api_blob_uploads.py`; then the W2 `test_upload_to_ingest.py` once with Redis down (the fixture must FAIL with the reason, not skip: a broken-input proof of ruling B) and once up (PASSED).
  5. Docs checks under the gate-2 flock: `audit-docs.py` (the `_CONTRACT_ARTIFACT_PATHS` entries need the regenerated files to exist), `doc-index.py --check`.

## PRs

- (none opened yet; the lead opens it.)
