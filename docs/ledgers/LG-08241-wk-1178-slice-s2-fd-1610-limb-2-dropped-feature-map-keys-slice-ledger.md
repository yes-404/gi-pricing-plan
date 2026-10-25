---
id: LG-8241
family: ledger
title: WK-1178 slice S2 — FD-1610 limb 2, the feature_map keys a model_call drops are traced, then refused when they feed a required input (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-25
owner: executor
tree: 3ffdbe3f787c195e43ebd3f8ae6a17143777d2e8
phase: P2
work: WK-1178
plans: [PL-8227]
corrected_by: []
relates: [FD-1610, PL-8227]
---

# LG-8241 — WK-1178 slice S2: FD-1610 limb 2, dropped feature_map keys

Working id 8241 (LG), unminted; the slice row S2 of PL 8227 has no working SL id. Branch `draft/s2-fd1610`.

**GO:** the maintainer's entry "2026-10-25 22:16:18 GMT" (`to-lead.md`), amended by "2026-10-25 22:26:43 GMT" (S2-C0 RULED option (1)) and ruled on by "2026-10-25 22:38:42 GMT" (S2-C0 option (a); S2's ledger = LG 8241; format split).
**MERGE-ACK:** not yet given.

## Tasks

### Scope

PL 8227's S2 section (FD-1610 limb 2): (d) `TraceStep.dropped_inputs`, then (c) `MODEL_CALL_REQUIRED_INPUT_ABSENT`; requirement FR-222 (03).

### Task list

S2-D1 / (d), (c), spec lines, contracts regeneration, and S2-C0 (the exposure measurement); the lines below are each task's evidence.

### Gate

(left for the lead's gate)

### Audit

(not yet seated)

### Build log

**Disclosure (2026-10-25).** (c) was built at b919b9f1 under the lead's 21:54:12 brief, before S2-C0 ran. The maintainer's "2026-10-25 22:38:42 GMT" rules this a disclosed line, not a defect; red-first standing accepted (red at 7231abea precedes b919b9f1).

**Red / green / static (exec-s2run, from-lead "2026-10-25 22:36 GMT"; head 3ffdbe3f787c195e43ebd3f8ae6a17143777d2e8, tree 5658a53e):**
- GREEN @ab7e107b: "27 passed in 7.64s" rc 0 and "25 passed in 1.44s" rc 0. RED @7231abea: "5 failed, 22 passed in 8.01s" rc 1 (all 5 in test_rating_model_call_dropped_inputs.py) and "25 passed in 1.49s" rc 0 (trace_diff and scoring_compare are regression guards, they do not go red).
- ruff check rc 1 @ab7e107b (E501 :1:101), rc 0 @072e7ac5. mypy "Success: no issues found in 250 source files" rc 0 @ab7e107b.
- contracts: write rc 0; `generate-contracts.py --check` "58 generated contracts match the models" rc 0 @3ffdbe3f; `git diff --stat` of docs/contracts/: 3 files, +33/-3.

**S2-C0 — exposure measurement (2026-10-25, per the maintainer's "2026-10-25 22:26:43 GMT"):**
head=3ffdbe3f787c195e43ebd3f8ae6a17143777d2e8
- Instrument: scratch script (uncommitted), parses each blob as `pricing_core.rating.compile.Bundle`, hydrates it with `runtime.load_bundle`, per model_call step counts feature_map keys outside input_contract names plus earlier steps' `produces`; required_hits = such keys feeding `required_model_inputs`.
- Proof (instrument check), run via run-heavy under the 22:26:43 grant: throwaway `s2-pg-3ffdbe3f` (127.0.0.1:32771, postgres:16-alpine 75f5a96988cd, alembic head rc 0) and `s2-minio-3ffdbe3f` (127.0.0.1:32772, minio/minio:latest 69b2ec208575); one planted Bundle with `driver_years`→`age_years` on step s_risk → "rows=1 blobs_read=1 hits=1 required_hits=1" rc 0. `docker rm -fv` of both rc 0; `docker ps -a --filter name=s2-` 0 before, 0 after; dangling volumes 16 before, 16 after; no prune.
- Real run (read-only), command (a): `docker exec gi-pricing-postgres-1 psql -U gipricing -At -c "select id, status, algorithm_ref, bundle->>'blob_sha256' from rating_versions where bundle is not null"` rc 0, zero rows. Command (b): one read-only GET per blob_sha256 from bucket `gip-blobs` (Settings.blob_bucket default, `backend/src/app/config.py`; `deploy/` sets no override) at http://127.0.0.1:9000 — **bucket named and not read**: no row, so no GET was issued.
- rows=0 blobs_read=0 hits=0 required_hits=0 rc=0 — a **boundary zero, not hits=0 alone**. exposure on the dev DB: none measurable — 0 compiled rating versions at 3ffdbe3f787c195e43ebd3f8ae6a17143777d2e8; the proof row is the instrument check.

**Correction to PL 8227's S2-C0 text (2026-10-25; the plan is frozen, this ledger carries it):** the measurement reads the compiled Bundle blob, not the `rating_versions.bundle` column — that column is `BundleMetadata` (`model-schema` `rating.py`:88–122, `extra=forbid`: content_hash, bytes, compiled_at, blob_sha256), so the plan's `select … bundle::text` query measures nothing (ruled option (1), "2026-10-25 22:26:43 GMT").

## PRs

(none yet)
