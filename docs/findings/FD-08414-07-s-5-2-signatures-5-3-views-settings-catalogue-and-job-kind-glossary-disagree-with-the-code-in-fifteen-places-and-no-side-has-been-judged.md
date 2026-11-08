---
id: FD-8414
family: finding
title: 07's §5.2 signatures, §5.3 views, settings catalogue and Job Kind glossary disagree with the code in fifteen places, and no side has been judged
status: active
created: 2026-11-08
owner: auditor
tree: 374a22bf33ad
corrected_by: []
relates: [FD-1284, OQ-1285, FD-1693, FD-2034]
---

# FD-8414 — 07's §5.2 signatures, §5.3 views, settings catalogue and Job Kind glossary disagree with the code in fifteen places

*(Working id 8414, born open, filed 2026-11-08 by the auditor on the P28 recon of module 07 and the §14 review accepted at to-lead "2026-11-08 09:02:21 GMT". Severity LOW: no limb names a wrong number or a price. Owner Work: P3-D.)*

## Finding

`docs/specs/07-platform.md` does not match the code at the tree below in fifteen places. **Which side is wrong is the owning P3 Work's first act, per limb**; this record judges neither side.

- **Predicate and corpus.** One row per spec statement whose quoted text does not match the quoted code, within §5.2, §5.3, the §4.4 / §3.8 catalogues and the glossary job kinds of `07`. Count 15, by hand, no script. The §5.1 endpoint tables were not re-checked (the review found them clean). Frontend routes were read in `frontend/src/router/index.ts`.
- **Tree.** `374a22bf33ad`. Paths are relative to it.

| Limb | Spec says | Code does | Consequence |
|---|---|---|---|
| 1 | `07:408-410` `submit(kind, params: BaseModel, principal, *, idempotency_key, queue: str)` | `backend/src/app/platform/jobs.py:95` `submit(session, kind, parameters: dict, principal, *, workspace_id, source=JobSource.API, idempotency_key=None, queue: JobQueue \| None=None)` | Does not type-check from the spec: `session` and `workspace_id` are required; `source` absent. |
| 2 | `07:411` `cancel(job_id, principal)` | `jobs.py:266` `request_cancellation(session, job_id, *, actor)` | Name, an extra `session`, and `principal` is `actor` (keyword-only). |
| 3 | `07:424-425` `platform/secrets.py`, `resolve(ref) -> SecretValue` | No `secrets.py` under `backend/src/app/platform/` at this tree | The spec's §5.2 surface is absent at the stated path. **Owned: WK-1251 (P3)**, by the dated line at `docs/roadmap.md:4328` (2026-10-14, the maintainer's line-read ruling, item 4): "`07` FR-423 … and FR-424, FR-425, FR-426 (a pluggable secret backend, secrets resolved at use, never logged or audited) are **NOT DELIVERED and owned by this Work, in P3**". Whether the behaviour exists elsewhere is WK-1251's first act; this record does not say more. §13 verdict (the lead, 2026-11-08, corrected the same day): REASSIGNED, WK-1251. |
| 4 | `07:413-416` `class JobProgress(ProgressCallback)` in `platform/jobs.py` | `backend/src/app/worker/progress.py:88` `class JobProgress:` with no base; `ProgressCallback` is a `Protocol` (`pricing_core/progress.py:28`) | Wrong module and not a subclass; constructor not in the spec. `update` and `check_cancelled` match. |
| 5 | `07:419` module-level `put(content: bytes \| AsyncIterator[bytes], media_type)` | `platform/blobs.py:206` `BlobStore.put(self, session, content: bytes \| Iterable[bytes], media_type)` | A method; `session` required; sync iterable. |
| 6 | `07:420` `presign_upload(media_type, parts)` | `blobs.py:304` method; `parts=1`; `expires_in_s=3600` added. `PresignedUpload` is hand-written at `blobs.py:97` | Minor. The recon did not check whether `model-schema` holds the same shape (`CLAUDE.md` §2, ADR-704). |
| 7 | `07:421` `promote_upload(upload_id)` | `blobs.py:357` method; also takes `database` | Same pattern as limb 5. |
| 8 | `07:422` `open(ref)` | `blobs.py:257` method | Signature agrees except it is a method; listed so the pattern is not dropped. |
| 9 | `07:428-429` sync `get(key, workspace_id, environment=None)` | `platform/settings.py:406` `async resolve(session, settings, workspace_id \| None, key, environment=None)`; also `resolve_all` | Name, async, two extra leading parameters, and the order of `workspace_id` and `key` is swapped: a positional caller copying the spec passes them crossed. |
| 10 | `07` §5.3 `Jobs` (`/jobs`) and `Job detail` (`/jobs/:id`) | No `/jobs` or `/jobs/:id` route and no view | **Later phase, and unowned.** `docs/roadmap.md:1583` (P3 note, 2026-10-09) moves WK-675 Slices 13 (Jobs) and 14 (Job detail) from P2 to P3, after `FD-1284` option D. `WK-675` is `status: closed` (`docs/roadmap.md`, its row block), and no P3 Work row names either view (`git grep -n -i -E "jobs list|job detail|Slice 13|Slice 14" origin/main -- docs/roadmap.md` finds line 1583 and nothing else in a Work row). Placing them is this record's owner's first act (P3-D). Spec-only note until a Work holds them. |
| 11 | `07` §5.3 `/admin/environments`, `/admin/service-accounts`, `/admin/settings`, `/admin/status` | No `/admin/*` route and no view | **Later phase.** Service accounts: P3, WK-676; Settings and System status: WK-1288 (`docs/roadmap.md`, owns `/admin/status` and `/admin/settings`), per `FD-1284` option D. Environments: `OQ-1285` is open. Spec-only notes. |
| 12 | `07` Demo entrance: `/demo` "absent where `dev_auth_enabled` is false" | `frontend/src/router/index.ts:29-33` routes `/demo` unconditionally; the API answers the not-enabled response (`backend/src/app/api/demo.py:42-48`) | "Absent" holds of the API route, not the page. The Contents cell was not compared with `DemoView.vue`. |
| 13 | `07:448` (FR-448) flag names `sql_validation_check_enabled`, `expression_objectives_enabled`; FR-449 | `platform/settings.py:290, :302` keys are `features.`-prefixed | A bare name sent to the settings API is unknown; not verified at runtime. |
| 14 | `07` FR-446–FR-449 settings catalogue | `settings.py` REGISTRY also declares `features.date_routing_enabled` (`:315`), `features.shadow_scoring_enabled` (`:326`), `rate_tables.cell_threshold` (`:279`) | **Confirmed by the auditor at this tree:** `git grep -n -c -E "date_routing_enabled|shadow_scoring_enabled|cell_threshold" 374a22bf33ad -- docs/specs/07-platform.md` printed no match (rc 1). The `FD-1693` pattern: three registry keys unlisted. |
| 15 | `07:57` glossary Job Kind: 13 kinds, no "e.g." | `packages/model-schema/src/model_schema/jobs.py:41-75` `JobKind` has 25 members (hand count); the 12 absent: `dataset.profile`, `dataset.derive`, `model.transparency`, `model.backtest`, `model.compare`, `peril_structure.reconcile`, `metric.certify`, `rating.regression`, `rate_table.diff`, `rate_table.diff_cells`, `score.trace_produce`, `blob.gc` | The glossary reads as the catalogue and is not. Whether another section holds the full catalogue was not checked. |

## Evidence

The recon is `~/gi-pricing-plan.local/scratch/p28/recon-07.md` (local, not committed). The auditor re-read at `374a22bf33ad` the `def` lines of `submit` and `request_cancellation` (`jobs.py:95`, `:266`) and `resolve` (`settings.py:406`) with `git grep -n -E "^\s*(async )?def (submit|request_cancellation|resolve)\(" 374a22bf33ad -- backend/src/app/platform/jobs.py backend/src/app/platform/settings.py`, and limb 14's spec grep above. The remaining quotations are the recon's. Not checked by the recon: `07` §4.2, §4.3 and §4.5 shapes against `model-schema`, a money-as-float scan of the spec, and the money fields.

## Disposition

**deferred with an owner: P3-D.** The Work's first act is, per limb, to decide which side was wrong, then amend the spec (with a dated line) or the code. Limbs 10 and 11 are Phase 3 views, so a spec-side note only until their Works are activated; limb 10 has no Work and P3-D places it. Limb 3 is reassigned to WK-1251 and is not P3-D's.
