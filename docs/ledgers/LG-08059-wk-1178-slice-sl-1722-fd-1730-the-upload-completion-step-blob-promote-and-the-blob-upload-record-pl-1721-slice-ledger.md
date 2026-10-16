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
- The runs: `run-small` R1–R9, `test_blobs`, one-head; the W2 worker test PASSED, both Jobs `succeeded` with output (d).
- The breakers (broken-input proofs of the new checks).
- The FR 8058 marker (`req("FR-<minted>")`) at mint (A5).
- The mint: working ids to minted ids; `status: closed` only at slice close.
- Merge after D18 and after `SL-1258` order is settled (e).

### Build log

- 2026-10-16: red-first commits `ca76bb4e`, `3a489dbf` (08:34Z, 08:36Z); spec `0d4ebd89`; activation `d48705ac`; implementation `0f80af62`; renames `bba89d66` (08:49Z).
- 2026-10-16: the lead's pre-gate read 09:52:42 BST; this ledger and fixes A2, A6 added by the executor in one commit, writing only (no test run, the SL-1455 latency window being open).

## PRs

- (none opened yet; the lead opens it.)
