---
id: LG-2081
family: ledger
title: SL-2080 — POST /api/v1/models/{id}/archive requires model:fit, not model:submit (FD-2079)
status: closed                 # active → closed (§1.2a)
created: 2026-11-07   # original date 2026-11-05, set at the draft; working id 8369, minted 2026-11-07
owner: executor
tree: e760450ec280c0ba5b84e91cb6c130d5419e0f95
phase: P2
work: WK-1178
slice: SL-2080
plans: []
corrected_by: []
relates: [FD-2079]
---

# LG-2081 — SL-2080: archive requires `model:fit`, not `model:submit`

*(Minted 2026-11-07 as LG-2081 from working id 8369, with SL-2080 (8368) and FD-2079 (8366), with the mint tool of record `mint-repoint.py`.)*

**GO:** the lead's ruling "2026-11-05 14:05:07 GMT" (option (a), conditional): fix = the permission and its test; red first; the state guard proven on an `approved` model; a dated line on `02` §5.1's archive row. Brief of record sha256 prefix `d7521045e7d7`.
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

`06` §4.1 (DP-A): `model:fit` is the Model write right; `model:submit` is "submitting a Model … for approval". The route `POST /api/v1/models/{id}/archive` (`backend/src/app/api/models.py` `archive_model`) and `backend/src/app/platform/modelling.py` `archive` both checked `model:submit`. Requirement: FR-202 (lifecycle; the archive edge is `draft | fitted | superseded → archived`). `SubmitModels` and `submit_for_review`'s check (modelling.py, the other `Permission.MODEL_SUBMIT`) are unchanged.

Who gains and loses (`model_schema/permissions.py` `BUILTIN_ROLES`): `analyst` (fit, no submit) GAINS archive; `pricing_actuary` (both) unchanged; no built-in role LOSES it. Only a stored custom role with `model:submit` and without `model:fit` would lose it; none is seeded. No spec row or test relied on the loss.

Existing fixtures: `test_model_lifecycle.py` and `test_model_nfrs.py` call `service.archive` with principals holding `analyst` + `pricing_actuary`, which hold `model:fit`; none was changed.

### Task list

1. Red first (commit 69d391f9, then 15993936 and a528160b): three tests in `backend/tests/test_api_model_lifecycle.py`, on the real route.
2. The two edits (commit fc1566c7): `caller: FitModels` on `archive_model`; `Permission.MODEL_FIT` in `archive`; docstring line in `archive`; the dated line on `02` §5.1's archive row.
3. Test fix (commit e760450e): the superseded case carries that version's `If-Match` (see Build log).

### Gate

The full two-half gate ran on the lead's slot under item 31, on the branch head `42009e0d15a918e4d869597cec1a57fe39d9e182` (tree `0f095cd9faa559e6c5f8baac81152c36f6a918a5`), range `origin/main...sl-8368-archive-permission`, START 2026-11-07T20:17:33Z, END 2026-11-07T22:29:14Z, `rc=1` (the END line of `~/gi-pricing-plan.local/scratch/sl8368-gate/gate/gate.log`). Range files at that head: `backend/src/app/api/models.py`, `backend/src/app/platform/modelling.py`, `backend/tests/test_api_model_lifecycle.py`, `docs/INDEX.md`, this ledger and `docs/specs/02-modelling.md`. The gate head predates the re-merge of `origin/main` `e12dc849` and the mint, which are docs only (the re-merge brought main's code in; the code-adjacent tests of the slice are the gate's own full suite).

| Stage (file in `gate/`) | rc | Result |
|---|---|---|
| ruff (`ruff.rc`) | 0 | `All checks passed!` |
| mypy (`mypy.rc`) | 0 | `Success: no issues found in 253 source files` |
| import-linter (`import_linter.rc`) | 0 | |
| generate-contracts --check (`contracts.rc`) | 0 | `58 generated contracts match the models` |
| req-coverage (`req_coverage.rc`) | 0 | |
| audit-docs (`audit_docs.rc`) | 1 | Own ids only, by the lead's reading (from-lead "2026-11-07 22:29:47 GMT"): check 31 three lines (`gap … between 2064 and 8366`, `gap … between 8366 and 8368`, `id 8369 is created: 2026-11-05, earlier than id 2064's 2026-11-06`) and check 25 one line (this ledger cites finding `FD 8366`, which resolved nowhere before the mint). Counts of every `  - check N:` line in that log, by `grep -E '^  - check [0-9]+:'`: check 2: 5; 5: 5; 25: 1; 30: 71; 31: 3; 32: 244; 35: 27; 36: 497. The post-mint run at the minted head is in the Build log below. |
| pytest (`pytest.rc`) | 1 | `13 failed, 7512 passed, 27 skipped, 5 xfailed, 156 warnings in 4737.18s (1:18:57)` |
| pnpm install / generate:api / lint / type-check / test / build | 0 each | vitest `Test Files  138 passed (138)`, `Tests  919 passed (919)` |
| demo `--journey wf-699 --no-compose` | 0 | PASS, `demo seconds` 1457; D7 `sum +489842011 minor units` |
| template guard / db 0 | | start and end `alembic_version=1 environments=3 tenant_marker=1`; `redis db 0 dbsize` 56 at start and end; keycloak bind source under tools-main |

**The 13 failing tests, by name, are item 31's set exactly** (eight docs-audit files; no other failure): `test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`; `test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`, `::test_doc_id_check_exits_0_on_the_real_tree`; `test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`, `::test_the_committed_digest_currently_matches_the_committed_spec`; `test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`; `test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`; `test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`, `::test_check_29_note_carries_the_residue_line`, `::test_phase1b_residue_count_matches_check_29s_own_count`; `test_register_owed.py::test_check_29_wiring_is_undisturbed`; `test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`, `::test_journey_citations_are_audited_in_ci`. The gate STANDS under item 31 by the maintainer's reading (to-lead after 22:29: "FD 8366's gate stands … Mint FD 8366, PR"; the lead's END read is from-lead "2026-11-07 22:29:47 GMT"). The skipped count is 27 at this tree (the lead: baseline 27, the head predates A's merge).

**Dislocation #1: 495 s, marked "side-run beside".** The lead's docs checks (doc-index regen and `--check`, audit-docs, register-lint, about one minute) ran on another branch at about 22:11:40–22:12:40 GMT, beside this gate's demo, which started 22:04:54 (from-lead "2026-11-07 22:12:40 GMT", BREACH). The reading is excluded from the quiet baseline; a PASS stands with that stated. For reference the gate log's own line: `dislocation #1 | 495 s (29 Oct passes: 422 / 387 / 383 s; this box 21:17:05 baseline 552 / 558 s)`.

### Audit

Tree read: sl-8368-archive-permission @1fedb56f0749f520d78186c0cf1b386e585f5a86, tree 199aa6c6. Range: `origin/main...HEAD` (merge-base 2f108b1e; origin/main is now bdad1322, one commit ahead, not an ancestor of the branch; `git merge-tree` of the two is clean).

Auditor aud-sl8368, 2026-11-05. Scope derived from the ruling first (to-lead "2026-11-05 14:05:07 GMT" (a), conditional; "14:07:26 GMT" the dated note; "15:57:59 GMT" FINAL accepted), then evidenced at the tree above. DB-free: nothing here ran a DB-backed test.

| # | Scope row | Evidence read | Verdict |
|---|---|---|---|
| 1 | Archive gets its own dependency; `SubmitModels` and every other route unmoved | `git diff origin/main...HEAD -- backend/src/app/api/models.py` is one line: `archive_model`'s `caller: SubmitModels` → `caller: FitModels`. `FitModels` is the alias that already existed (`models.py:118`); no new alias, `SubmitModels` (`:119`) is still used by `submit_model` (`:738`). Other `MODEL_SUBMIT` sites (`custom_objectives.py:78`, `peril_structures.py:64`, `custom_metrics.py:69`, `objectives.py:714`, `perils.py:312`, `metrics.py:505`, `modelling.py:1278`) are untouched (`git grep MODEL_SUBMIT`). | MET |
| 2 | The two edits as ruled | `modelling.py` `archive`: `Permission.MODEL_SUBMIT` → `Permission.MODEL_FIT` plus a docstring paragraph; `submit_for_review`'s check (`:1278`) untouched. The route reaches no other permission check (`archive_model` → `service.archive`; one `rbac.require_permission`). | MET |
| 3 | Who gains / loses | `permissions.py:136–142`: `analyst` holds `model:fit`; `pricing_actuary` = analyst + `model:submit`. `analyst` GAINS archive; no built-in role loses it; LG's statement matches. A stored custom role with submit and without fit would lose it: none seeded (read from the LG; not re-proved by a DB query, DB-free). | MET |
| 4 | Condition of 14:05:07: an `approved` model is refused by STATE for fit-only and for both-permissions callers; `superseded → archived` succeeds | `VALID_MODEL_TRANSITIONS` (`packages/model-schema/.../modelling.py:2113`): `APPROVED → {SUPERSEDED}`, `REVIEW → {APPROVED, FITTED}`, so neither reaches `ARCHIVED`; `_require_transition` raises 409 `VALIDATION_FAILED`. API tests: `test_an_approved_model_is_refused_archive_by_state_not_permission` (parametrized fit-only, both: asserts 409, `VALIDATION_FAILED`, then status still `approved`), `test_a_superseded_model_is_archived_by_a_fit_holder` (asserts 200, `archived`). The service-level `test_an_approved_model_cannot_be_archived` (`test_model_lifecycle.py:700`) already pinned the guard on main. | MET (build log quotes the green run: `4 passed`) |
| 5 | Both directions on the real route | `test_archiving_requires_model_fit_and_not_model_submit`: submit-only custom role → 403 `PERMISSION_DENIED`; fit-only → 200 `archived`. The caller carries ONLY the named permissions (`_caller_with` builds a custom role). | MET |
| 6 | Red first, by cause | Build log: head a528160b, `3 failed, 1 passed`, rc=1; the third failure's captured log read `permission denied … "permission":"model:submit"` then `403`. The summary was tailed to 40 lines: the first two failures' assert lines are not quoted (the LG says so). The red ran on a528160b (tests only), not on 69d391f9 (the committed-alone red test); `15993936` and `a528160b` changed tests after it. | **OWED**: re-run at a528160b in a clean checkout, in a window after M's, slot set, all three reds quoted by cause, LG line dated (FINAL accepted 15:57:59, "not mine" per brief). Not run by this audit. |
| 7 | Dated line on `02` §5.1's archive row | Present at `docs/specs/02-modelling.md:1920` (+1 −1), wording follows the ruling's. Two defects: (a) it is appended to the Purpose cell with no separator ("`If-Match` required Requires `model:fit` …"); (b) it conflicts with SL-2011's `Permission` column on the same row, which already carries `model:fit` as a fourth cell with the same ruling's footnote (`sl-8361-permission-column` @6ca44595, `02`:1920, :1943). `git merge-tree sl-8361-permission-column 1fedb56f` → CONFLICT in `docs/specs/02-modelling.md` only. FR-202 (`02`:402) is silent on who archives: the ruling's "and on FR-202 if its text needs the clause" is not triggered. | MET as to substance; **correction owed at the re-merge**: take SL-2011's row, re-add only the dated state-guard sentence in its place (see merge order). |
| 8 | Dated note on FD-2079 (the superseded trace, by citation) | Drafted: `FD-02079-essay.md`, "Dated note". The LG's Audit paragraph carries the same citations; deployment path read by citation, not proven by a test. | MET (draft) |
| 9 | Existing fixtures | `test_model_lifecycle.py` / `test_model_nfrs.py` call `service.archive` as the `_actuary` principal of `test_diagnostics.py` (`test_model_lifecycle.py:700` via `_fit`; role slug not opened, read by name) and, in `test_model_nfrs.py:126`, `analyst` + `pricing_actuary` (both hold `model:fit`); none changed by the slice (`git diff --stat`). The `_actuary` role was not opened: **by name only**; the DB-backed files are OWED-TO-GATE either way. | MET |

NFRs: none measured; the change adds no query and no check, it swaps one constant. Broken-input proof: the red above (the permission test red on the unfixed code); a mutation of the fix was not run by this audit (DB-backed).

Gaps (verdict, none silent):
- The `review` state is claimed refused by the §5.1 dated line ("an `approved` or `review` model") but no test archives a `review` model through the route: **delivered but untested** (the transition table refuses it; low).
- The two `_caller_with` custom-role seeds go through `seed_as_owner`: fine, not a product path.

Ancestor check (standing rule): 69d391f9, 15993936, a528160b, fc1566c7, e760450e each `git merge-base --is-ancestor <sha> 1fedb56f` exit 0. The slice names no plan or ruling head (`plans: []`). `origin/main` bdad1322 is not an ancestor: moved by one commit (docs batch 11, #1433), no overlap with the five files.

GREEN by import closure (item 29): changed source `backend/src/app/api/models.py`, `backend/src/app/platform/modelling.py`; importers are >15 files (every API and modelling test): **OWED-TO-GATE**, not looped. DB-free members were not run (every file touching `archive` is DB-backed).

Merge order: see the report; SL-2011 (sl-8361) first, then this slice re-merged over it, then the pin.

Mint-time notes (2026-11-07, executor, appended to the adopted audit; the table above is unchanged): the audit's lead adoption is from-lead "2026-11-05 17:20:17 GMT" ("aud-sl8368 FINAL ADOPTED, released: FD-2079 + pin; drafts scratch/aud-sl8368/"). Row 6's OWED red re-run was done in the window of 2026-11-05 17:43:32–17:45:11 UTC (Build log, last entry: three reds by cause at `a528160b`). The gap "the `review` state is untested" was closed by `test_a_model_in_review_is_refused_archive_by_state` (Build log, 2026-11-05 17:26 UTC entry; green and planted-red in the same window).

### Build log

- 2026-11-05 15:47–15:50 UTC, window "gate D, stage pytest", head a528160b (tests only, permission still `model:submit`), `-k archiv`: `3 failed, 1 passed, 8 deselected in 55.45s`, rc=1. FAILED: `test_archiving_requires_model_fit_and_not_model_submit`, `test_an_approved_model_is_refused_archive_by_state_not_permission[permissions0]` (fit only), `test_a_superseded_model_is_archived_by_a_fit_holder`. Passed: the both-permissions approved case (409 already, on main). The captured log of the last failure reads `permission denied … "permission":"model:submit"` then `403`. The red summary was tailed to 40 lines, so the first two failures' assert lines are not quoted.
- 2026-11-05 15:50:47–15:53:31 UTC, head fc1566c7 (permission edit): `1 failed, 3 passed, 8 deselected in 20.13s`, rc=1. The superseded test got `409` on `/archive`: its `If-Match` came from `GET /models/{slug}` (the latest version, v2) while the archived row is v1, a stale write. A defect in the test, not the code; it also masked the superseded case in the red run, whose 403 came from the permission.
- 2026-11-05 15:53:42–15:54:22 UTC, head e760450e (test passes `?version=`): `4 passed, 8 deselected in 22.03s`, rc=0.
- Window ends (both runs): template guard `alembic_version=1 environments=3 tenant_marker=1` at start and end; `-n 11 dbsize` 0 at start and end; `-n 0 dbsize` 56 at start and end; `gipricing_sl8368_win` rows 0 and `gipricing_sld_gate` rows 1 at END. The red run set no `GIP_GATE_SLOT` (the lead read `PUBSUB CHANNELS` empty, to-lead 15:49:09); both green runs set `GIP_GATE_SLOT=/tmp/slots/window-8368` on the inner command. Scripts: `~/gi-pricing-plan.local/scratch/sl8368/win.sh`.
- The superseded state is reached through `_supersede_earlier_versions` by approving the model and then a next version, but `_next_version_of` inserts that second version row (it is not refitted).
- `ruff check` on the test file: rc=0. `ruff format --check`: the file was not format-clean on main (about 14 older hunks); only my hunks were hand-formatted. `mypy` on the single test file reports errors of the same kind on lines that predate this slice.
- 2026-11-05 17:26 UTC, audit fix (to-lead "2026-11-05 17:20:43 GMT"): added `test_a_model_in_review_is_refused_archive_by_state` to `backend/tests/test_api_model_lifecycle.py`: a fitted model is submitted through `POST /models/{id}/submit` (state `review`, asserted), a `model:fit` caller archives it, and the route answers 409 `VALIDATION_FAILED` with the status still `review`. This is what makes "an `approved` or `review` model is refused" in the `02` §5.1 dated line true by a test and not by the transition table alone. **OWED to a DB window, not run:** the test is DB-backed, so neither its green run nor the planted removal of the state guard (`_require_transition` in `archive`, expected red: 200 and status `archived`) was run. The red re-run at `a528160b` stays owed in that same window. `ruff check` on the file: rc=0; `ruff format --check` on the file reports the same older hunks, none in the new test.
- 2026-11-05 17:43:32–17:45:11 UTC, window "FD-2079 ~2-min" (to-lead "2026-11-05 17:42:33 GMT"), beside gate D's pytest stage, own DB `gi_sl8368`, redis db 12, bucket `gip-test-blobs-sl8368b`, slot `GIP_GATE_SLOT=/tmp/slots/window-8368` (quoted from the pytest process's /proc environ in each run); script and logs `~/gi-pricing-plan.local/scratch/sl8368b/` (`win.sh`, `win.out`, `red.log`, `green.log`, `planted.log`). Three runs: (1) the red re-run at `a528160b` in a clean checkout (`.claude/worktrees/sl8368-red`), `-k archiv`: `3 failed, 1 passed, 8 deselected`, rc=1; by cause: `test_archiving_requires_model_fit_and_not_model_submit` `assert 200 == 403` (submit-only caller archived: the route still checked `model:submit`); `test_an_approved_model_is_refused_archive_by_state_not_permission[permissions0]` `assert 403 == 409` ("This action requires model:submit"); `test_a_superseded_model_is_archived_by_a_fit_holder` `assert 403 == 200` (same denial). This closes the OWED re-run of the audit's row 6. (2) `test_a_model_in_review_is_refused_archive_by_state` at `02406b30`: `1 passed, 12 deselected`, rc=0. (3) The same test with the state guard removed (`before = _require_transition(row, ModelStatus.ARCHIVED)` replaced by `before = ModelStatus(row.status)` in `archive`): `assert 200 == 409`, `1 failed`, rc=1, red by cause; restored with `git checkout` of that one file, porcelain 0 at `02406b30` (the first restore, a `sed` that matched a second identical line, was wrong and was undone by that checkout). START and END: template guard `alembic_version=1 environments=3 tenant_marker=1`; `-n 0 dbsize` 56; `-n 12 dbsize` 0; `PUBSUB CHANNELS 'gip:switch:*'` three gate-1 channels at START, none at END; `gi_sl8368` 0 rows and `gipricing_sld_gate` 1 row at END. The OWED lines above for the new test and the planted removal are discharged by this entry.

## PRs

This PR; its number, squash commit and merge date are written at the merge's date-of-record.

*(Dated note, 2026-11-08, docs batch 19, by the executor, on the maintainer (by delegation) ACK of merge 85, to-lead "2026-11-07 23:41:47 GMT": lines 51 and 57 cite `FD 8366`, which is minted as **FD-2079** (#1460). The ledger is append-only and its text is not edited.)*
