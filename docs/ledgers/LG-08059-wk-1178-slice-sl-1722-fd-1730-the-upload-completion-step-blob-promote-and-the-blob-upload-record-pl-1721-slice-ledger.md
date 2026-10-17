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

### Pre-gate review fixes (executor, 2026-10-16, writing only — no run)

The lead adopted the findings of an independent pre-gate review. Each was verified against the code first; every one was real. Branch `sl-1722-wk1178-fd1730-upload-404`, from `63d26b48`. Line numbers are at this commit.

| Finding | Lead verdict | Change |
|---|---|---|
| F2 two `ONE_SIDED_SLUGS` lines were 101 and 102 characters (`pyproject.toml` `line-length = 100`; measured by character, not byte) | fix | `backend/tests/test_contracts.py:95-100`: each value wrapped in parentheses |
| F3 `__all__` unsorted (RUF022: SCREAMING_CASE, then CamelCase, then the rest) | fix | `backend/src/app/platform/blobs.py:60-64`: `STAGING_EXPIRY_DAYS`, `UPLOAD_COMPLETE_WITHIN` now follow `QUOTE_INPUT_BLOB_COLUMNS` and precede `BlobStore` |
| F4 `parts: list[dict[str, Any]]` extended with `list[PartTypeDef]`, an `arg-type` error under `mypy --strict` (TypedDict is not a `dict[str, Any]`) | fix, no cast | `blobs.py:58` imports `PartTypeDef` under `TYPE_CHECKING`; `blobs.py:414` `parts: list[PartTypeDef]`. The repo had no earlier boto3 type-def use (`git grep -n TypeDef -- backend/src` printed nothing before this change) |
| F5 multi-line `get_bucket_lifecycle_configuration(...)` that fits one line | fix | `backend/tests/test_blobs.py:329`: one line, as `ruff format` writes it |
| F6 `NoSuchUpload` branch: `head_object` unguarded, a raw `ClientError` on a 404 | fix + test | `blobs.py:431-436`: guarded; raises `_validation("The upload is missing", ...)`, the same failure the single-part branch raises |
| F7 `put_bucket_lifecycle_configuration` replaces every rule on the bucket | fix + test | `blobs.py:83` `_STAGING_RULE_ID`; `blobs.py:151-177`: read the configuration, drop only the rule with this ID, write it back with ours; `NoSuchLifecycleConfiguration` means no other rules |
| F8 `staging_key` and `s3_upload_id` were `String(255)`; `07` §4.5 says text | fix, spec unchanged | `backend/src/app/db/models.py:2621-2622` `Text`; `backend/migrations/versions/e7c3a9b15d82_blob_uploads.py:35-36` `sa.Text()` (the revision is new on this branch, absent from `origin/main`, so it is edited in place) |
| F9 `assert "2" in job["error"]["detail"]` | fix | `backend/tests/test_api_blob_uploads.py:202`: `== "Expected parts 1 to 2; missing part(s) 2."`, the exact text `_complete_staged` builds |
| Q3 `07` §5.1 `upload-url` row: the 2026-09-28 sentences | superseded, struck | `docs/specs/07-platform.md:352`: the clause "and nothing yet moves it ... a spec change of their own." is struck with `~~...~~` and a dated tag. "The object lands on a staging key" is still true and stays |

**Tests added** (all in `backend/tests/`, each with a named breaker):

- (a) `test_api_blob_uploads.py:206` `test_a_repeated_completion_after_a_failed_promotion_returns_the_first_job` (RL-1724 "Repeat completion").
- (b) `test_api_blob_uploads.py:235` `test_another_principal_with_write_in_the_workspace_may_complete` (RL-1724 "Who may complete"). No principal check was added to the route.
- (c) `test_blobs.py:395` `test_completing_a_finished_multipart_upload_again_finds_the_object` (the `NoSuchUpload` retry), and `test_blobs.py:409` `test_a_gone_multipart_upload_with_no_object_is_the_named_failure` (F6).
- F7: `test_blobs.py:337` `test_ensure_bucket_keeps_a_rule_it_does_not_own` (also calls `ensure_bucket` twice: our rule is replaced, not duplicated) and `test_blobs.py:361` `test_ensure_bucket_sets_the_rule_on_a_bucket_with_no_configuration`.

**OWED after GATE END (SL-1455); none of these was run in this window** (no pytest, uv, mypy, ruff, generate-contracts, audit-docs):

1. `uv run python scripts/generate-contracts.py`, then `--check` rc 0. The generated `upload-url-request` and `upload-url-response` schemas and `generated.json` are not committed yet. The `job.schema.json` `blob.promote` line must come from the generator, never from a hand edit.
2. `uv run ruff check .` and `uv run ruff format --check` (the wrapped `ONE_SIDED_SLUGS` values and the new test bodies are hand-formatted); `uv run mypy` (F4: `part["PartNumber"]` and `part["ETag"]` are `NotRequired` keys on `PartTypeDef`; F7: `LifecycleRuleOutputTypeDef` rules passed back as `LifecycleRuleUnionTypeDef`); `uv run lint-imports`.
3. The new tests, red first then green. Red: revert `blobs.py` for F6 and F7 and the F8 `Text` change is covered by the migration run; the API tests (a) and (b) are expected green at once, as they pin behaviour the route already has. Then `backend/tests/test_blobs.py`, `test_api_blob_uploads.py`, `test_contracts.py`.
4. `alembic upgrade head` on a fresh database, 1 head (F8 edits a revision in place), and the DP-7 head-order check.
5. Docs checks under the gate-2 flock: `audit-docs.py` (07 §5.1 strike), `doc-index.py --check`.

## Re-merge of main, 2026-10-16 (Europe/London)

- 2026-10-16 10:28 BST: `git merge --no-ff origin/main` (a2f77b2d, #1309 merged) into the branch at 2fad9e21. `merge-tree --write-tree` rc 1 beforehand: one conflict, `docs/INDEX.md` (generated), taken theirs; the regeneration is owed. No conflict in code, docs/specs, docs/contracts, roadmap or register. After the merge `git diff origin/main --name-only` lists no roadmap, register or openapi path: only this slice's own paths differ.
- Overlap with #1309 (`git diff --stat 0877e6e7 a2f77b2d`): `docs/contracts/openapi/generated.json` and `backend/tests/test_contracts.py` are in its change set; this branch edits `test_contracts.py` (6 lines) and has not yet generated `generated.json`, so the upload-url shapes are still missing from it.
- Owed after GATE END, in addition to the list above: regenerate `docs/INDEX.md` (`doc-index.py` under the gate-2 flock) and `generate-contracts.py` then `--check` against the merged tree.

## Re-merge of main, 2026-10-17 (Europe/London)

- 2026-10-17 11:3x BST (executor-1722): `git merge --no-ff origin/main` (055b5e6b) into a030b5ce; no conflict. Non-DB items run on the merged tree: `generate-contracts.py` regenerated `generated.json`, `job.schema.json` (`blob.promote`) and the two `upload-url-*` schemas, then `--check` rc 0 (51 match); `ruff check .` found I001 (`blobs.py` TYPE_CHECKING imports) and RUF022 (`model_schema/__init__.py` `__all__`), both fixed by `--fix`, rc 0 after; `mypy` rc 0; `lint-imports` rc 0 (4 kept); `doc-index.py` regenerated, `--check` rc 0; `register-lint.py` rc 0.
- `audit-docs.py`: check 13 was red (`07` §2 "Blob Upload" pointer row re-stated a term `00` §2.1 defines); the row is deleted, `00` §2.1 stays the one definition. Check 31 (gap between 1740 and the working id 8059) stays red until the mint; expected.
- DP-7: `e7c3a9b15d82` has `down_revision = "d4e81b7a2c95"`, the single head at `origin/main` 055b5e6b. `SL-1274` (`f2b6d90a4c17`) and `SL 8017` are not on main. Re-point NOT owed now.
- Still OWED (DB or the lead's window): the ten reds by cause, `test_api_blob_uploads.py`, `test_blobs.py`, `test_upload_to_ingest.py` (W2, read PASSED), `alembic upgrade head` and `downgrade -1 && upgrade head`, the single-head test, `pnpm generate:api` and `type-check`, FR 8058 marker at mint (A5), the mint.

## Owed non-DB items, 2026-10-17 (executor-1722b, `TZ=Europe/London`)

- Re-merge of `origin/main` (ebe3292c) into 4f7332fe: one conflict, `docs/INDEX.md`, taken theirs and regenerated under the gate-2 flock; pushed as db0e5f20.
- `pnpm --dir frontend generate:api` rc 0; `pnpm --dir frontend type-check` rc 0 (`vue-tsc --build --force`), at db0e5f20.
- **Task 0 MinIO spike** (compose container `gi-pricing-minio-1`, `minio/minio:latest`, image `sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e`, server `RELEASE.2025-09-07T16-13-09Z`). Throwaway bucket `spike-sl1722-throwaway`, created and deleted by the script; the repo's own `BlobStore.ensure_bucket` was run twice against it, then `get_bucket_lifecycle_configuration` read:
  - after the 1st call: `[{"Expiration": {"Days": 2}, "ID": "expire-staging", "Filter": {"Prefix": "staging/"}, "Status": "Enabled"}]`
  - after the 2nd call: 1 rule, identical to the 1st (idempotent).
  - **Answer:** `put_bucket_lifecycle_configuration` with the `AbortIncompleteMultipartUpload` clause is **accepted** (no refusal), and the `staging/` rule reads back, but the read-back carries **only `Expiration`**: the `AbortIncompleteMultipartUpload` clause is not returned by this MinIO. Whether it is stored and ignored or dropped is not established by this read. DP-U1.2's abort-incomplete-uploads effect is therefore unverified on MinIO; the 2-day object expiry is verified. `test_ensure_bucket_sets_the_staging_lifecycle_rule` asserts the `staging/` prefix only, so it does not depend on the clause.
- **Breakers:** the plan's breakers (Task 2 table, R3 to R9) are one-line mutations of the implementation, each shown red against a database. The tests that carry them are already written; no further test-writing is owed. Running them needs the DB window.
- **Deleted `07` §2 "Blob Upload" pointer row:** the row (added in f1eb0d9b) said only "defined in `00` §2.1; its record is §4.5 and its completion is FR 8058", so check 13 (`audit-docs.py:3986`, a term is not redefined in a module glossary once `00` defines it) was right to refuse it and its content lives in `00` §2.1:137 and `07` §4.5 / FR 8058. **But** RL-1724 acceptance item 11 (line 530) requires "T6's `**Blob Upload**` row in `07` §2" to be found at the slice head, so the deletion conflicts with the ruling as written. Not restored here; for the audit.

## Rulings DP-1722-A and DP-1722-B, 2026-10-17 (executor-1722db)

- **DP-1722-A (a)** (the maintainer (by delegation), `to-lead.md` "2026-10-17 13:05:25 BST — Maintainer: SL-1722 DP-A → (a); DP-B → (a)"): MinIO accepts the `staging/` rule and the 2-day `Expiration` is VERIFIED on read-back; the `AbortIncompleteMultipartUpload` clause is UNVERIFIED on MinIO (it is not echoed); the rule is still set, because it is S3's contract (PL-1721 DP-U1.2 anticipated this); Task 3 never relies on reading the abort back.
- **DP-1722-B (a)** (same entry): no `07` §2 row for "Blob Upload" — `CLAUDE.md` §7 makes `00-overview.md` §2 the one glossary (a new term goes there first), `00` §2.1 :137 defines Blob Upload, and a `07` §2 row would be the second copy that `audit-docs.py` check 13 refuses; RL-1724 acceptance item 11's intent (the term defined before first use) is met by `00` §2.1 plus `07` §4.5 / FR 8058.

## Scoped DB windows, 2026-10-17 (executor-1722db, `TZ=Europe/London`)

Authority: the maintainer's DB-WINDOW LANE ruling (`to-lead.md`, "2026-10-17 13:19:48 BST — Maintainer: MERGE-ACK #1319 (D18) now; a DB-WINDOW LANE beside the code gate"). Each window: the `small-test` slot, its own database made by `createdb -T gipricing` and dropped on exit, a hard `timeout`, started at load1 < 8. All three ran **beside a code gate** (gate-1 held by another seat's gate); load1 at start 3.29 to 4.52. The script is local (`gi-pricing-plan.local/scratch/sl1722-dbwin.sh`, modes `reds`, `w1`, `w2`); logs in `gi-pricing-plan.local/scratch/sl1722-dbwin/<mode>/`.

**Window reds — `3a489dbf`** (detached worktree `.claude/worktrees/sl-1722-reds`, tree `1145506e`; the template database, no `alembic upgrade` because that tree predates `e7c3a9b15d82`). 13:33:33 to 13:34:09, rc 1: `10 failed, 1 warning in 19.34s`. The ten, each red by cause (not by import or fixture error); the cause is the assertion/exception line of `--tb=line`:

| # | Node | Cause at `3a489dbf` |
|---|---|---|
| 1 | `test_api_blob_uploads.py::test_upload_url_records_an_upload_and_returns_its_id` | `KeyError: 'id'` (the response has no `id`), :86 |
| 2 | `…::test_completing_another_workspaces_upload_is_the_missing_404` | the control `POST …/uploads/{id}/complete` is `404 NOT_FOUND`, `assert 404 == 202`: route absent, :109 |
| 3 | `…::test_a_completion_past_the_deadline_is_refused` | "no Blob Upload was recorded, so there is no deadline to pass" (`upload_id: None` in the response), :154 |
| 4 | `…::test_a_repeated_completion_returns_the_first_job` | route absent, `404`, :172 |
| 5 | `…::test_a_missing_part_fails_the_promotion_by_name` | route absent, `404`, :197 |
| 6 | `…::test_identical_bytes_promote_to_one_blob` | route absent, `404`, :218 |
| 7 | `…::test_a_promoted_blob_is_retained` | route absent, `404`, :246 |
| 8 | `…::test_a_promoted_digest_downloads_only_in_its_workspace` | route absent, `404`, :261 |
| 9 | `test_blobs.py::test_ensure_bucket_sets_the_staging_lifecycle_rule` | `botocore ClientError NoSuchLifecycleConfiguration` |
| 10 | `test_upload_to_ingest.py::test_a_file_uploaded_through_the_public_api_ingests_to_a_succeeded_version` | `KeyError: 'id'`, :141 |

(Rows 1 to 8 are in file order, which the line numbers confirm.)

**Window 1 — head.** First run at `e0b740c7` (tree `ec4f62ea`): `2 failed, 32 passed` on `test_api_blob_uploads.py` + `test_blobs.py`. Three defects in the slice's own tests, none in the implementation, each fixed in a test-only commit:

| Defect | Evidence | Fix |
|---|---|---|
| R3 built the foreign caller with the `admin` role, which holds no dataset write: the foreign `complete` was `403`, not the `404` under test (so the R3 breaker was red for the wrong reason in that run) | `assert 403 == 404`; `BUILTIN_ROLES["admin"]` is read plus admin permissions | role `analyst`, like the `writer` fixture (`63d191a9`) |
| R6 read the prose from `job["error"]["detail"]`, which is `{}`; `tasks.py` stores `exc.detail or exc.title` in `message` | `assert {} == 'Expected parts 1 to 2; missing part(s) 2.'` | read `job["error"]["message"]` (`63d191a9`) |
| R3 compared the two `404` bodies including `trace_id`, which is per request | `{'trace_id': …} != {'trace_id': …}` | leave `trace_id` out with `detail` and `instance` (`2638ef0b`) |

The three `404` bodies differ in `detail`/`instance` (they name the id) and `trace_id` only; every other field is equal.

At `2638ef0b` (tree `1bfd13d6`), 13:39:42 to 13:42:22, rc 0: alembic `upgrade head` rc 0 on the window's own database; `green` `34 passed, 1 warning in 18.79s` (no skip); the breakers below; `green-after` (after all reverts, 0 dirty paths) `34 passed, 1 warning in 12.79s`.

| # | Breaker (one-line mutation, reverted by `git checkout`) | Run | Red by cause |
|---|---|---|---|
| R3 | drop the `upload.workspace_id != caller.workspace_id` filter in `api/blobs.py` | `1 failed` | `assert 202 == 404` |
| R4 | `if datetime.now(UTC) > upload.complete_by:` to `if False:` | `1 failed` | the Job is accepted (`202` body, `status: queued`) where a `409` is asserted, :161 |
| R5 | `if upload.job_id is not None:` to `if False:` | `1 failed` | two different Job ids, :175 |
| R6 | `if missing or extra:` to `if False:` in `platform/blobs.py` | `1 failed` | `JobStatus.SUCCEEDED is JobStatus.FAILED`, :200 |
| R7 | `stored = await session.get(BlobRow, digest) is not None` to `stored = False` (the plan's "skip the existence check") | **`1 passed` — NOT red** | see below |
| R7b | remove `.on_conflict_do_nothing(index_elements=["sha256"])` | `1 failed` | `IntegrityError … sqlstate 23505, constraint pk_blobs`, `FAILED` where `SUCCEEDED`, :264 |
| R8 | drop `await retain(session, digest)` | `1 failed` | `assert 0 == 1` (`ref_count`) |
| R9 | the Job-result owner in `blob_readable_by` matches `ref: "x"` | `1 failed` | `assert 404 == 307` |

**R7 finding (for the lead; not decided here).** The plan's R7 breaker ("skip the existence check → a second `put` and a primary-key error") is not what the code does: with the check skipped, `promote_upload` copies the staged object over the same content address (the same bytes, so the same object), and the `blobs` insert is `on_conflict_do_nothing`, so nothing fails. The existence check in `promote_upload` is an optimisation of the copy that no assertion in `test_identical_bytes_promote_to_one_blob` can see (still one row, `ref_count == 2`, one object under `blob/`). The guard the test does carry is `on_conflict_do_nothing` (R7b, red). Options: (a) accept R7b as R7's breaker and amend the plan's cell in a delta (about 10 min); (b) add an assertion that the second promotion issues no `copy` (about 30 min, a mock or a call count on the client); recommended (a), since the copy is idempotent and an unobservable optimisation is not a contract. Standing by.

**Window 2 — head `2638ef0b`** (tree `1bfd13d6`), 13:42:42 to 13:43:34, rc 0, own database `gipricing_sl1722_w2`: `alembic upgrade head` rc 0; `downgrade -1` rc 0 (`e7c3a9b15d82 -> d4e81b7a2c95`); `upgrade head` rc 0; `alembic heads`: `e7c3a9b15d82 (head)`, 1 head; `test_upload_to_ingest.py` `1 passed, 1 warning in 13.83s` (run with `-rs`: no skip, so PASSED); `test_contracts.py` `171 passed, 2 skipped, 1 warning in 13.10s` (run without `-rs`: the two skips' reasons are not recorded here); `tests/test_repository_invariants.py::test_the_migration_chain_has_exactly_one_head` `1 passed in 0.71s`.

Still OWED: the full two-half gate (a grant, S-13); the W2 test's both-Jobs-`succeeded`-with-output reading (d) beyond PASSED; the FR 8058 marker at the mint (A5); the mint; the audit.

## Delta 2026-10-17 13:5x BST (executor-1722db): R7 per DP-1722-C

- **Plan cell change** (the maintainer (by delegation), `to-lead.md` "2026-10-17 13:45:30 BST — Maintainer: SL-1722 DP-1722-C (breaker R7) → (b)"; option (a) refused): PL-1721's R7 breaker cell ("skip the existence check → a second `put` and a primary-key error") is read as: **skip the existence check → the second promotion issues an object-store copy**, which `test_identical_bytes_promote_to_one_blob` now asserts with a spy on `BlobStore._client.copy` (`copies == [f"blob/{sha[:2]}/{sha}"]`). The primary-key error belongs to the `on_conflict_do_nothing` guard (R7b, kept as a second breaker). The frozen plan is not edited; this line is the delta.
- Commit `01a79def` (tree `9d5cab1a`), window 13:46:06 to 13:48:35, beside a code gate, load1 at start 4.73, own database `gipricing_sl1722_w1`: `green` `34 passed, 1 warning in 16.60s`; **R7** (`stored = False`) `1 failed` with `AssertionError: assert ['blob/84/844…'] == ['blob/84/844…']` (two copies recorded where one is asserted); R7b, R3 to R6, R8, R9 each `1 failed` by the causes in the table above; after the reverts, 0 dirty paths and `green-after` `34 passed, 1 warning in 18.01s`; rc 0.

## PRs

- (none opened yet; the lead opens it.)
