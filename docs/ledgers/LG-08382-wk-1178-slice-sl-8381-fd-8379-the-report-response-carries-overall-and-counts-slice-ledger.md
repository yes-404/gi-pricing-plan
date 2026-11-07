---
id: LG-8382
family: ledger
title: WK-1178 slice SL 8381 — FD-8379, the report response carries overall and counts, the stored body unchanged (slice ledger)
status: active
created: 2026-11-07
owner: executor
tree: 57d206061b89395f1374d675c34d1e2a01f273b9
phase: P2
work: WK-1178
slice: SL-8381
plans: [PL-8380]
corrected_by: []
relates: [FD-8379, PL-8380]
---

# LG-8382 — WK-1178 slice SL 8381: the report response carries `overall` and `counts`

**GO:** to-lead "2026-11-07 19:29:19 GMT" (Maintainer): "GO SL 8381 on brief 263dfa3fb39c, read by me: NEW branch sl-8381-report-response from origin/sl-8373-spec-examples at b2636e85d425 (ls-remote agrees), NEW worktree sl-8381; PL 8380 @56f21fe3 accepted 16:55:19; DB-free first, each red first; T4 + T5's window only on the lead's written grant under Needs (a)–(j), else the gate lane; contracts regenerated with the shape, never hand-written; frontend light checks only; no session line; the bans."
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL 8380 (a dated Work-plan delta of WK-1178), slice SL 8381, acceptance A1 to A18. Base: SL 8373's S4 head `b2636e85d425fe23cbabb0244b41829dd855d3af` (`origin/sl-8373-spec-examples` at spawn: `git rev-parse origin/sl-8373-spec-examples` printed the same sha; it is an ancestor of this branch, `git merge-base --is-ancestor` rc 0). Branch `sl-8381-report-response`, worktree `.claude/worktrees/sl-8381`, seat exec-sl8381 (Sonnet 5.5, medium). Requirements: FR-42, FR-49, FR-451, NFR-469 (PL 8380 `relates:`). Plan merged in at `dd729ed0` (`docs/INDEX.md` conflict: took theirs, regenerated, `doc-index.py --check` rc 0).

### Task list

- **R1** (Steps 1 to 5, commit `f985190a`): fixture `packages/model-schema/tests/fixtures/validation-report-pre-fix.json` captured at the base by `~/gi-pricing-plan.local/scratch/sl-8381/capture_pre_fix.py` (`uv run --directory <wt> python …capture_pre_fix.py > <fixture>`, run at head `dd729ed043225c97a448415d09d7c7c85cc40dff`, no source change yet); tests T1, T2, T3, T4, T5.
- **R2** (Steps 6 to 13, commit `ce3676c7`): T6 (in `test_validation_report_stored_form.py`), `ValidationReportView` and `ReportCounts` in `model_schema/validation.py`, exports, `load_report_view` and the route, the generator row, the authored contract's three DP-5 limbs, regeneration, the frontend alias.
- **R3** (Steps 15 to 17, commit `6fa1339a`): `01` §4.6 fence `schema=ValidationReportView`, counts `{"pass": 0, "warn": 1, …}`, a dated amendment, `ILLUSTRATIVE_CEILING` 31 to 30.
- **Step 14** (the DB window for T4 and T5): not run; owed to the lead's written grant, else the gate lane (see Gate).

### Gate

No gate of this slice's own (A13). Checks at the code head `6fa1339a` (tree `57d206061b89395f1374d675c34d1e2a01f273b9`), each `head=` first and `rc=` last in `~/gi-pricing-plan.local/scratch/sl-8381/`:

| Check | rc / summary |
|---|---|
| `uv run --directory <wt> ruff check .` | rc 0, `All checks passed!` |
| `uv run --directory <wt> mypy` | rc 0, `Success: no issues found in 256 source files` |
| `ruff format --check` on the changed .py files | rc 1 on four files that were not format-clean before this slice (`api/validation.py:420`, `platform/validation.py:375`, `model_schema/validation.py` `_rule(` calls, `scripts/generate-contracts.py:233`); `ruff format --diff` on the model-schema file shows no hunk of this slice's code; the one hunk it did show in `_derived_never_assigned` was fixed. The new test file: `1 file already formatted`, rc 0 |
| `generate-contracts.py --check` | rc 0, `58 generated contracts match the models` |
| `run-small` `backend/tests/test_contracts.py` | `179 passed, 2 skipped, 2 warnings` (T1, T2 included) |
| `run-small` `packages/model-schema/tests/test_validation_report_stored_form.py` | `10 passed` (T3, T6) |
| `run-small` `tests/test_spec_examples.py` | `40 passed` |
| `pnpm --dir <wt>/frontend install --frozen-lockfile` / `generate:api` / `type-check` / `lint` | rc 0 / 0 / 0 / 0 (type-check first rc 2, see Build log) |
| `audit-docs.py` (via gate-2 flock) | rc 1; check 40: `63 json blocks: 33 schema, 30 illustrative, 0 unmarked` (A12). The expected check 31/32 reds on working ids: `gap in the full allocation between 2070 and 8374`, `…between 8374 and 8379`, `id 8380 is created: 2026-11-05, earlier than id 8374's 2026-11-07`, `the LG 8374 file, line 11: SL 8373 does not resolve`, `the PL 8380 file, line 15: LG 8382 does not resolve` (the last resolves once this file is in INDEX). The rest of its output is the tree's standing residue (checks 2, 5, 30, 35, 36, and check 32 on old records), none from a file this slice edits; a base-tree comparison was not obtained (an archive of the base has no git, and the script needs it) |

`tests/test_audit_docs_ids.py` (item 39, spec-reading tests run on the same tree; list by `git grep -l -E 'docs/specs|"docs" */ *"specs"' -- backend/tests tests`): `2 failed, 153 passed` over the six DB-free spec readers run, the two failures `test_the_real_tree_passes_all_ten_checks` and `test_doc_id_check_exits_0_on_the_real_tree`, with this FAILED block whole: `check 31: gap in the full allocation between 2070 and 8374`; `check 31: gap in the full allocation between 8374 and 8379`; `check 31: id 8380 is created: 2026-11-05, earlier than id 8374's 2026-11-07 — created must be non-decreasing with the number`; `check 32: the LG 8374 file, line 11: SL 8373 does not resolve in docs/INDEX.md`; `check 32: the PL 8380 file, line 15: LG 8382 does not resolve in docs/INDEX.md`. All five are working-id checks (item 31's class). DB-backed spec readers (test_demo_guide, test_objective_submission, test_rating_version_create_pins, test_settings_environment, test_severity_population_golden) are for the gate.

**Green set (item 29), by import closure.** Changed source modules: `git diff --name-only b2636e85d425...HEAD -- packages backend/src scripts` = `model_schema/validation.py`, `model_schema/__init__.py`, `app/platform/validation.py`, `app/api/validation.py`, `scripts/generate-contracts.py`. The importers of `ValidationReport`, `model_schema.validation`, `app.platform.validation` or `app.api.validation`: `git grep -l -E 'model_schema\.validation|app\.platform\.validation\b|app\.platform import[^\n]*\bvalidation\b|app\.api\.validation|from app\.platform import .*validation|ValidationReport' -- backend/tests 'packages/*/tests' tests` (26 files, 24 DB-backed). `model_schema/__init__.py` is imported by nearly every test, so the closure beyond these is the gate's full suite. DB-free members, run: `test_approval_guard.py`, `test_revalidation_sweep.py`, `test_validation_catalogue.py`: `22 passed, 2 warnings` (head `ce3676c7`). Item 43 (`test_api_authorisation_sweep.py`) and item 45 (`test_error_sinks.py`) need the database (31 and 14 database-fixture hits): they, T4, T5 and the 24 DB-backed importers are the gate's.

### Red and green lines

- **T1, T2 red at the base (A2)**, head `dd729ed043225c97a448415d09d7c7c85cc40dff` plus the R1 tests uncommitted: `E       AssertionError: assert {'counts', 'overall'} <= {'dataset_ver... 'started_at'}` (T2, `test_contracts.py:256`) and `E       AssertionError: the contract declares fields the model lacks: ['counts', 'overall']` (T1, `test_contracts.py:786`); `2 failed, 177 passed, 2 skipped, 2 warnings`, rc 1. T1's message is the plan's cause string; T2's names `counts` and `overall` absent from the route schema's `required`.
- **T3 green at the base by design (DP-3)**: `2 passed in 0.81s` at that head.
- **M1** (bare `@computed_field` on `counts` and `overall`, uncommitted), head `dd729ed0…`: T3 red, `E       AssertionError: assert ['counts', 'overall'] == []` (`1 failed, 1 passed`). Reverted: `git diff --stat -- packages/model-schema/src` empty; T3 `2 passed`. (The first M1 run named only `overall`, because the test asserted one key at a time; the assert was changed to name both and M1 re-run: both runs in `scratch/sl-8381/r1-m1-t3-*.log` and `r1-m1-t3b-*.log`.)
- **T4 and T5**: not run yet. T4's natural red at the base (`KeyError: 'overall'`), T5 green at the base by design, and T5 under M1 are owed to the window; on the gate-lane fallback they are not run, T2 stays the response limb's red and T3 under M1 the constraint's.
- **T1, T2, T3, T6 green at `ce3676c7`**: `179 passed, 2 skipped`; `10 passed`. The contract comparison's first read (the spike did not run it): T1 passed with `overall` and `counts.*` in the intersection, no comparator touched.
- **M2** (generator row back to `ValidationReport`, regenerated), head `ce3676c7`: `E       AssertionError: the contract declares fields the model lacks: ['counts', 'overall']`, `FAILED …test_an_artifact_shape_carries_exactly_what_its_contract_declares[validation-report]`, `1 failed, 178 passed, 2 skipped`. Reverted by `git restore -- scripts/generate-contracts.py docs/contracts`; `git status --short` and `git diff --stat` empty, `generate-contracts.py --check` rc 0, T1 file `179 passed, 2 skipped`.
- **A12 mutation** (the block's `counts.warn` becomes 2), on `ce3676c7` plus the R3 edits: `E         Value error, overall and counts are derived from results, never assigned (01 §4.6)`, `FAILED tests/test_spec_examples.py::test_a_class_marked_example_validates_in_full[01-data-management.md:582]`, `1 failed, 39 passed`. Reverted: `40 passed`.

### Audit

(none yet)

### Build log

- **2026-11-07 (R1, `f985190a`).** Fixture and tests committed alone. The base for A4: fixture added by `f985190a`, an ancestor of `ce3676c7`, the first commit in `b2636e85…..HEAD` touching `model_schema/validation.py` (`git log --diff-filter=A --format=%h -- packages/model-schema/tests/fixtures/validation-report-pre-fix.json`; `git log --reverse --format=%h b2636e85d425…HEAD -- packages/model-schema/src/model_schema/validation.py | head -1`).
- **2026-11-07 (R2, `ce3676c7`).** Deviation 1: `load_report_view` ends in one `return ValidationReportView.of(report)` after the optional acknowledgement merge, where Step 8 said both return paths end in `.of(...)`; the two are the same behaviour. Deviation 2 (a plan defect): Step 10 and the plan's frontend bullet said `validation.test.ts:30`'s `as` cast would still type-check without the two new keys; `pnpm --dir frontend type-check` returned `src/api/__tests__/validation.test.ts(21,10): error TS2352 … is missing the following properties … counts, overall`, rc 2. Fixed by casting that fixture through `unknown` with a comment (`frontend/src/api/__tests__/validation.test.ts`, outside the plan's Write set, one line); type-check then rc 0. No behaviour added (G4). `ReportCounts` is a functional `TypedDict` as Step 7 gave; it appears in `generated.json` inline as the `counts` schema (no separate component).
- **2026-11-07 (R3, `6fa1339a`).** `01` §4.6: the earlier "Clarified 2026-11-05" note (route does not yet serialise) is left as written and a new dated "Amended 2026-11-07" note follows it.

## PRs

(none; no PR until the lead's word)
