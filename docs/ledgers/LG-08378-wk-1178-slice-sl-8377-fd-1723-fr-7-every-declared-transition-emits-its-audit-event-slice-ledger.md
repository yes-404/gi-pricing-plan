---
id: LG-8378
family: ledger
title: WK-1178 slice SL-8377 — FD-1723's FR-7 limb, every declared transition emits its audit event (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05             # filed under working id 8378
owner: executor
tree: 921d9270cd2a8f7afb232e13ad2f0aeadbe595c2   # sl-8377-fr7-events, the T2 writer commit this was first written against (base ac123679f741c02ec86504b1b017b923a93b4151)
slice: SL-8377
phase: P2
work: WK-1178
plans: [PL-8376]
corrected_by: []
relates: [FD-1723, PL-8376, FR-7, FR-368, FR-146, FR-157, FR-238, FR-349, FR-351]
---

# LG-8378 — WK-1178 slice SL-8377: every declared transition emits its audit event

**GO:** to-lead "2026-11-05 16:50:00 GMT" (accepted; GO behind M; T1 and T2 must land, T3 may stay a named exception), on the 15 rulings of "2026-11-05 16:39:14 GMT". The lead's order of 2026-11-05 (after the T1 and T2 commits): T3 GO, tests committed alone first, built DB-free up to window 2.
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

The slice's row is SL 8377 in `PL-8376` ("SL 8377: the row. Scope: A1 to A14"), read at origin/draft/pl-1723-2026-11-05 @ac123679. Requirements: `00` FR-7; `06` FR-368, FR-349, FR-351; `02` FR-146, FR-157, FR-154, FR-163; `03` FR-238. Ruled decisions DP-1 to DP-15 are cited by the entry "2026-11-05 16:39:14 GMT". The branch was cut from the plan's head, not from origin/main (the brief's order); `git merge-base --is-ancestor ac123679 HEAD` printed success at the start.

### Task list

- **T1** (DP-1, DP-2, DP-3; A1 to A4). Tests `8cefe0f3`, writer `c9cf0f1a`. `record_certificate` in `objectives.py` and `metrics.py` names `certification_failed` for a failed run from `draft` or `certified`, and on a run that ends outside `draft` and `certified` keeps the certificate row, moves no status, leaves `certificate_id` and records `certificate_recorded`. Clauses at `02` FR-146 and FR-157 and `06` FR-368. The first-of-two row pins `approval_request.approve`.
- **T2** (DP-6; A5). Tests `a175b786`, writer `921d9270`. `rating_version.submitted` after the `draft` to `review` write; `deployment_request.executed` inside the deploy transaction after the guarded status update. Clauses at `03` FR-238 and the Audit actions bullet of §4.12.
- Housekeeping `refactor(audit)` commit: reverts two lines `ruff format` rejoined in `metrics.py`, on the lead's order (CI does not run `ruff format`).
- **T3** (A6, A7, A13, A14; DP-4, DP-9 to DP-14). Tests `48a2feed` (committed alone), spec side `fd24e47b`, FR-7 clause and OQ 8391 / OQ 8392 with both mirrors `4368c005`. 68 rows (57 transition rows + 11 creation rows) x 2 legs = 136 cases, plus two DB-free guards: 138. **The four `rate_table_version.*` creation rows (STOP-1, ruled (b) by to-lead "2026-11-05 18:08:06 GMT"):** their writers (`rate_tables.py`: `seed_from_model`, `import_confirmed`, `manual_edit_confirmed`, `bulk_operation`) open their own unit of work, so their rollback leg is a fault injected from the test: `test_a_declared_transition_writes_its_event_in_its_transaction_rate_tables`, 4 actions x 2 legs, the seam `app.platform.rate_tables.audit.record` patched by `monkeypatch` inside that one test (never autouse, never in a conftest); the patch writes the real event then raises `_InjectedError`; the test asserts that exact exception propagated and that neither a `RateTableVersionRow` for `slug@2` nor an event of the action remains. No source edit. NFR-498 is not cited for this proof. A6's total is 144 (136 + 8), plus two guards, 146 collected. The roadmap rows (SL row, DP-11's §10 gate row) are NOT written: the brief bans roadmap edits; the mint carries them.
- **T4** (A7, A8, A9, A12): A7's two plants and A9 are below; A8's eleven and A12 await window 2.

### Gate

(Written by the gate holder, not by this executor.)

DB-free checks on this executor's side, tree `921d9270`: `ruff check backend` rc 0; `audit-docs.py` (`--light`, `env -C` the worktree) FAILED (2): `check 31: gap in the full allocation between 2010 and 8376` (the working ids), `check 39: docs/INDEX.md is stale against a fresh regeneration (2194 governed record(s))` (the mint's, ruled by the lead).

### Audit

(The auditor's.)

### Build log

- 2026-11-05 17:48 UTC. T1 and T2 tests and writers committed, in the order `8cefe0f3`, `a175b786`, `c9cf0f1a`, `921d9270`. **Window 1** runs `backend/tests/test_audit_transitions.py` twice in one DB window: at the test commit `a175b786` in a throwaway checkout (expected red: 14; green: the one pin), then at head. The reds therefore stay provable though the writers are in later commits. **Window 1 lines** (23:57 to 00:01 UTC, DB `gipricing_w1_sl8377` `-T gipricing`, redis -n 12, bucket `gip-w1-sl8377`, `GIP_GATE_SLOT=/tmp/slots/window-sl8377`, beside the pair's pytest, to-lead "2026-11-05 23:47:23 GMT"). Template guard `alembic_version=1 environments=3 tenant_marker=1` at START and END; db 0 = 56 at both; END: redis db 12 dbsize 0, own DB count 0, bucket removed (`mc rb`, `mc ls` shows no `w1`), `pg_database` after = before.
  - RED, tests of `a175b786` at src base, 15 cases: `14 failed, 1 passed`. By cause: the 4 `test_a_failed_certificate_says_so` cases fail at `assert last.action == f"{kind.prefix}.certification_failed"` (`'custom_metric.certified'`, `'custom_objective.certified'`); the 8 `test_a_late_certificate_moves_nothing` cases fail on the status (`'certified' == 'review'`, `'draft' == 'review'`, `'certified' == 'approved'`, `'draft' == 'approved'`), so DP-3's limb stands; the two T2 cases fail at the event unpack (`not enough values to unpack (expected 1, got 0)`); the first-of-two pin passes. **A surprise, found in this window and a fault of the test, not of a writer:** the first red run (log `head=a175b786`) had the 4 objective late cases fail at head for `ObjectiveCertificate`'s nine-check battery (FR-158): a one-check result is refused when `submit_for_review` reads it. Fixed in `e4c283f5` (each kind brings its own battery); the red run above is `a175b786`'s source with `e4c283f5`'s test file, and it is the one of record. The red of those 4 at `a175b786`'s own file was therefore a validation error, not the status.
  - GREEN, head `e4c283f539888771ed3938bec1328656564146c9`, same 15 cases (`-k "not test_a_declared_transition and not test_every_declared and not test_a_not_built"`): `15 passed`, rc 0.
  - **Window 2 lines** (02:22 to 02:30 UTC 2026-11-06, DB `gipricing_w2_sl8377` `-T gipricing`, redis -n 12, bucket `gip-w2-sl8377`, `GIP_GATE_SLOT=/tmp/slots/window-sl8377w2`, beside H's pytest, hard end 03:20). Tree under test `f591306639beb53422d81561bd127e6acab250fb`. Template guard `alembic_version=1 environments=3 tenant_marker=1` at START and END; db 0 = 56 both; END: redis db 12 dbsize 0, own DB count 0, bucket removed, `pg_database` after = before, `git status --porcelain` 0 lines.
    - **A6, the 144 cases** (`-k test_a_declared_transition_writes_its_event_in_its_transaction`, in four calls, each `head=` first): A 86 passed; B 28 passed (rating_version, deployment_request, validation_report and the 8 rate-table legs); C (model, 18 cases) **17 passed, 1 FAILED**; D (peril_structure, 12) 12 passed. 143 passed, 1 failed.
    - **The one red, no mutation (A10, reported and not softened):** `model:draft>fitted:model.fitted-commit`: `assert (event.before or {}).get("status") == row.before` gave `None == 'draft'`. `record_fit` in `modelling.py` writes the `model.fitted` event with `after=` only, no `before=`. Awaiting the lead's ruling: (a) `before={"status": "draft"}` in `record_fit`, a source edit outside the plan's write set, or (b) the row asserts `after` only for this edge, with a named reason.
    - **A12:** baseline `test_rbac.py::test_break_glass_is_time_boxed_and_expires`: 1 passed. With the two lines of `effective_permissions`' `expires_at` check deleted (`rbac.py:190-191`): FAILED at `assert Permission.APPROVAL_DECIDE not in held`; reverted, `git diff --quiet -- backend/src` rc 0.
    - **A8, the eleven mutations** (the one `audit.record` of the named writer deleted by `ast`, the matching row's commit leg run, reverted, `git diff --quiet -- backend/src` rc 0 after each): `objectives.record_certificate` FAILED `custom_objective:draft>certified`; `metrics.record_certificate` FAILED `custom_metric:draft>certified`; `approvals.decide` FAILED `approval_request:review>approved` and `review>review`; `rating_versions.submit_for_review` FAILED `rating_version:draft>review`; `deployments.deploy` (the `deployment_request.executed` call, not `deployment.created`) FAILED `deployment_request:approved>executed`; `datasets._transition` FAILED three `dataset_version:*>validating` rows; `modelling.submit_for_review` FAILED `model:fitted>review`; `perils.submit_for_review` FAILED `peril_structure:reconciled>review`; `validation_rules.submit_for_review` FAILED `validation_rule:draft>review`; `reference.publish_version` FAILED `reference_table_version:draft>published`; `jobs.transition` FAILED `job:queued>running`. A first `deployments` mutation deleted `deployment.created` by mistake (ast order) and its row correctly stayed green; the one of record deletes the `executed` call.
- 2026-11-05 18:11 UTC. **A7, DB-free, at head `4368c005`.** Planted edge (`review -> draft` added to `VALID_OBJECTIVE_TRANSITIONS`): `test_every_declared_edge_has_a_row_or_a_reason` FAILED, `Extra items in the left set: ('custom_objective', 'review', 'draft')`; reverted, `git diff --quiet -- backend/src packages` rc 0. Planted writer (`_PLANT = ObjectiveStatus.DEPRECATED.value` appended to `objectives.py`): `test_a_not_built_edge_has_no_writer` FAILED, `'app/platform/objectives.py: ObjectiveStatus.DEPRECATED'`; reverted, rc 0. Both without a DB. Also red by cause at the tests commit `48a2feed` before the maps were corrected: extra declared edges `('rating_version','draft','approved')`, `('approval_request','changes_requested','draft')`, `('approval_request','draft','review')`; green after `fd24e47b`.
- **A9, the census** at `4368c005`: `git grep -n -F 'audit.record(' 4368c00515dcd360bf2b87de892d3ac3db26c8a7 -- backend packages ':!*/tests/*'` prints 85 lines; the AST count (`ast.Call` with `func` `audit.record`, over `backend` and `packages` outside `tests`) is 84; the one line the AST does not count is the `RuntimeError` text at `platform/audit.py`. At the base `ac123679` the two counts were 83 and 82 (`fd1723-d0-enumeration-2026-11-05.md`, sha256 prefix `16fbc1666b30`); this slice adds two sites (`rating_versions.py`, `deployments.py`). The sites that match no row are D0 §3's census-only list (the list of rows is the plan's table, never derived from the sites); this slice does not reproduce it a second time.
- 2026-11-05. DP-3's limb stands unless window 1 finds the eight `certificate_recorded` cases green at `a175b786`; if so, the limb is withdrawn (`moved` and `.certificate_recorded` dropped) and this ledger says so.

- **A10 ruling and window 3** (2026-11-06). The one unplanned red of window 2 (`model:draft>fitted` commit leg, `model.fitted` with no `before`) was ruled by to-lead "2026-11-06 02:27:13 GMT", widened to five parts, delta acked by id before the fix; one commit `41775aeb`: `record_fit` reads `before_status = row.status` before the assignment and records `before` and `after.status`; `test_model_nfrs.py` pins four creates and gives `model.fitted` its own asserts; `02` NFR-484 amended and a dated correction beside the §9 text of 2026-08-22 (that text untouched); `PL 8376`'s Write set gains `modelling.py` and `test_model_nfrs.py`, `:115`'s "949" re-read (the status assignment; the `audit.record` is at `:986` at base). No status guard. Window 3 (02:31 to 02:34 UTC, DB `gipricing_w3_sl8377`, redis -n 12, bucket `gip-w3-sl8377`, slot `window-sl8377w3`, beside H's pytest), head `41775aebee547eff86b828af89255845eb08b290`: the 18 model cases of the table (`-k "test_a_declared_transition_writes_its_event_in_its_transaction and model"`) `18 passed`, rc 0 (the `draft>fitted` case is green; with window 2's 126 other table cases at `f5913066` that makes 144 of 144, the fix touching only `record_fit`); `test_model_nfrs.py` `3 passed`, rc 0; `test_ebm_model_jobs.py` `9 passed`, rc 0. END: template guard `alembic_version=1 environments=3 tenant_marker=1`, db 0 = 56, redis db 12 dbsize 0, own DB count 0, bucket removed.

## PRs

(None yet: the executor does not push or open the PR.)
