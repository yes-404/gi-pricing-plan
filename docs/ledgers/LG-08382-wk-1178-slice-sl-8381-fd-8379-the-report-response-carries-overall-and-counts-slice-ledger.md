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
- **Step 14** (the DB window for T4 and T5): run by exec-sl8381w on 2026-11-07 under the lead's written grant (to-lead "2026-11-07 22:30:36 GMT", via run-heavy --grant); the window was accepted by the maintainer, to-lead "2026-11-07 23:11:06 GMT". Its lines, from `scratch/sl-8381/LG-8382-window-lines.md` (SL 8381's own scratch dir; logs in that directory):

  - Gate: SL 8373 + SL 8381 (sl8381-gate.sh) on gate-1, stage pytest, START 2026-11-07T23:05:04+00:00 (gate.log); no "stage pytest END" at window END.
  - WINDOW START 23:05:41Z load1 1.91, avail 20/26 GB free line; template guard 1/3/1 (alembic_version=1 environments=3 tenant_marker=1); redis -n 13 dbsize 0, -n 0 = 56; gip:switch numsub 0; own DB gipricing_sl8381w_1 (-T gipricing, both URLs on it), bucket sl8381-w, GIP_REDIS_URL=redis://localhost:6379/13, GIP_GATE_SLOT=/tmp/slots/window-sl8381 quoted from a child's /proc environ (logs in this dir). Grant: to-lead "2026-11-07 22:30:36 GMT" via run-heavy --grant.
  - S4 base b2636e85 holds no T4; T4 red runs at R1 f985190a (lead-approved).
  - T4 @f985190a: FAILED test_an_actuary_acknowledges_a_warning_through_the_route, KeyError: 'overall' (test_api_acknowledge.py:91) [t4-red.log]
  - T5 @f985190a: 18 passed [t5-r1-green.log]; @7ef66d7b: 18 passed [t5-head-green.log]
  - M1 @f985190a (uncommitted, @computed_field on counts+overall): T5 test_presenting_a_report_never_writes_its_outcome_into_the_stored_body FAILED, ValidationError extra_forbidden at counts and overall (7 failed, 11 passed in the file) [t5-m1-red.log]. Reverted: git diff --stat empty, status empty; T5 re-run 18 passed [t5-after-revert.log]
  - T4 file @7ef66d7b: 4 passed [t4-head-green.log]
  - WINDOW END 23:08:27Z load1 5.03; redis -n 13 had 1 key before FLUSHDB then dbsize 0; -n 0 = 56; own DB count 0, gate DB count 1; bucket removed via mc rb, mc ls quoted in FINAL; template guard 1/3/1; no bind source under scratch/sl-8381; scratch worktrees removed.

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
- **T4 and T5**: run in the Step 14 window (lines above): T4 red at `f985190a` (`KeyError: 'overall'`), T5 green at the base by design and red under M1, T4 `4 passed` and T5 `18 passed` at `7ef66d7b`.
- **T1, T2, T3, T6 green at `ce3676c7`**: `179 passed, 2 skipped`; `10 passed`. The contract comparison's first read (the spike did not run it): T1 passed with `overall` and `counts.*` in the intersection, no comparator touched.
- **M2** (generator row back to `ValidationReport`, regenerated), head `ce3676c7`: `E       AssertionError: the contract declares fields the model lacks: ['counts', 'overall']`, `FAILED …test_an_artifact_shape_carries_exactly_what_its_contract_declares[validation-report]`, `1 failed, 178 passed, 2 skipped`. Reverted by `git restore -- scripts/generate-contracts.py docs/contracts`; `git status --short` and `git diff --stat` empty, `generate-contracts.py --check` rc 0, T1 file `179 passed, 2 skipped`.
- **A12 mutation** (the block's `counts.warn` becomes 2), on `ce3676c7` plus the R3 edits: `E         Value error, overall and counts are derived from results, never assigned (01 §4.6)`, `FAILED tests/test_spec_examples.py::test_a_class_marked_example_validates_in_full[01-data-management.md:582]`, `1 failed, 39 passed`. Reverted: `40 passed`.

### Audit

**Adopted** from-lead "2026-11-07 23:17:41 GMT" (lead 31, aud-sl8381 FINAL ADOPTED): the lead's verdicts on the auditor's proposals; the section below is the adopted draft `scratch/aud-sl8381/LG-8382-audit-section.md`, folded here at the mint (seat-brief-common item 34).

Auditor aud-sl8381 (Sonnet 5.5, medium). Object: read-only `origin/sl-8381-report-response` @7ef66d7baf089c06151e445b7cfb7b760d99c579 (the gated head; tree read in a scratch worktree). Ranges: `b2636e85d425fe23cbabb0244b41829dd855d3af...7ef66d7b` for SL 8381's own commits (`dd729ed0`, `f985190a`, `ce3676c7`, `6fa1339a`, `b2465654`, merge `7ef66d7b`), and `origin/main...7ef66d7b` (`e12dc849`) for the whole. Plan: PL 8380 A1 to A18. The red and green lines are in the LG before this audit (A15), apart from the window's (below).

| Item | Proposed | Evidence read |
|---|---|---|
| A1 write set | MET | `git diff --stat b2636e85...7ef66d7b^1` = the 20 files of PL 8380's Write set plus `frontend/src/api/__tests__/validation.test.ts` (disclosed deviation: `as unknown as`, TS2352; the lead's/maintainer's acceptance) and the plan file. No file outside. `docs/roadmap.md`, INDEX's final form and FD 8379's essay are the mint's (A14). |
| A2 red by cause | MET-BY-RECORD | T1 `the contract declares fields the model lacks: ['counts', 'overall']`, T2 `assert {'counts', 'overall'} <= {...}`, T4 `KeyError: 'overall'` (`scratch/sl-8381/t4-red.log`, `head=f985190a`, `test_api_acknowledge.py:91`). Not an import or fixture error. |
| A3 constraint proof red | MET-BY-RECORD | T3, T5 green at the base by design (stated). M1 (bare `@computed_field`): T3 `assert ['counts', 'overall'] == []`; T5 under M1 at `f985190a`: 7 failed, `extra_forbidden` at `counts` and `overall` (`t5-m1-red.log`); reverted, `git diff --stat` empty, 18 passed (`t5-after-revert.log`). |
| A4 fixture pre-fix by record | MET | `git log --diff-filter=A` names `f985190a`; the first commit after `b2636e85` touching `model_schema/validation.py` is `ce3676c7`; `git merge-base --is-ancestor f985190a ce3676c7` exit 0. LG quotes the capture command and base. |
| A5 stored bytes unchanged | MET-BY-RECORD | `ValidationReport` fields moved to `_ReportFields` in the same order, plus `ValidationReport` keeps `counts`/`overall` as `@property`; T3 passes in `model-schema` (`10 passed` per LG; I did not re-run it). |
| A6 old bodies read; view not a body | MET-BY-RECORD | T6 and T3 in the same file; `ValidationReport` is `extra="forbid"` and the view adds two fields, so a dumped view is refused (read in code). |
| A7 never written | MET (code) / MET-BY-RECORD (T5) | `git diff b2636e85...HEAD -- backend/src/app/db/models.py backend/migrations` is empty; `platform/validation.py` hunks start at `:38`, `:178` and later, none at `:114`; T5 18 passed at `f985190a` and `7ef66d7b` (window). |
| A8 response right | MET-BY-RECORD | T4 `4 passed` at `7ef66d7b` in the window (`t4-head-green.log`). |
| A9 derived, never assigned | MET-BY-RECORD | `_derived_never_assigned` raises `overall and counts are derived from results, never assigned (01 §4.6)`; A12's mutation shows it firing. `of()` builds from the report's own properties. |
| A10 one shape | MET (one nit) | `git grep` finds `class ValidationReportView` (`validation.py:639`) and `ReportCounts = TypedDict(` (`:543`), both only in `validation.py`; `ValidationReportView` and `ReportCounts` are in `__all__`. The plan's grep for `class ReportCounts` cannot match a functional `TypedDict`: plan wording, not a defect. `frontend/src/api/validation.ts` takes the type from the generated schema. |
| A11 contract | MET | `ce3676c7` is the commit that regenerated `docs/contracts/openapi/generated.json` and changed `validation.py`. At `7ef66d7b`: `components.schemas.ValidationReportView` has `overall` and `counts` required; no `ValidationReport` component; the generated `validation-report.schema.json` has both; the authored `required` list is unchanged (a `$comment` was inserted above it, so it is now at lines 8-9, not 7-8). `generate-contracts.py --check` rc 0 in the gate (`contracts.rc` 0). |
| A12 mark and counts | MET | `audit-docs` prints `63 json blocks: 33 schema, 30 illustrative, 0 unmarked`; `ILLUSTRATIVE_CEILING = 30`; the `01:582` id is present and passes (`219 passed` run). Mutation by record: `Value error, overall and counts are derived...`, `FAILED ...[01-data-management.md:582]`, reverted. |
| A13 one gate on the tree that lands | OWED-TO-GATE | `git merge-base --is-ancestor b2636e85d425 7ef66d7b` exit 0. The SOLO gate's pytest is at about 42 % at 23:15 GMT; T1 to T6 must be in its passed set by name; after SL 8373's squash and this slice's re-merge `git diff <gated head> HEAD` is read by the auditor. |
| A14 FD closing act | PROPOSED (drafts) | `FD-8379-essay.md` and `FD-8379-closing-act.md` in `~/gi-pricing-plan.local/scratch/aud-sl8381/`; minted and `closed` in the slice PR by the lead's mint. |
| A15 LG Audit section | OPEN | This section. The LG's Gate, Scope and Step 14 text is stale (Findings 1). |
| A16 guard row planted red | MET-BY-RECORD | M2 (generator row back to `ValidationReport`, regenerated): T1 `the contract declares fields the model lacks: ['counts', 'overall']`, `FAILED ...[validation-report]`, reverted, `generate-contracts.py --check` rc 0. |
| A17 OpenAPI move stated in PR body | OWED | No PR yet. `gh pr view <n> --json body` at the PR must state `ValidationReport` to `ValidationReportView` in `docs/contracts/openapi/generated.json` and that `ValidationReport` left the file. |
| A18 the window | MET-BY-RECORD (not yet in the LG) | `scratch/sl-8381/LG-8382-window-lines.md`: START 23:05:41Z, load1 1.91; own DB `gipricing_sl8381w_1`; `GIP_GATE_SLOT=/tmp/slots/window-sl8381` from a child's environ; `-n 13` dbsize 0; template guard 1/3/1; END 23:08:27Z, `-n 13` 1 key then 0; `-n 0` = 56; own DB 0. Accepted by the maintainer, to-lead "2026-11-07 23:11:06 GMT". The LG at the gated head still says Step 14 "not run": fold the window lines in before close. |

**My checks, `head=7ef66d7baf08` (`scratch/aud-sl8381/*.log`, each `head=` first and `rc=` last):** `run-small tests/test_spec_examples.py backend/tests/test_contracts.py` `219 passed, 2 skipped` rc 0; audit-docs rc 1 with FAILED (4) = the gate's four lines; `run-small tests/test_audit_docs_check_prefixes.py packages/pricing-core/tests/test_rating_declared_reads.py backend/tests/test_validation_reports.py`: `25 passed, 13 errors` (the 13 are the DB file, see Deviations).

**Code read (`packages/model-schema/src/model_schema/validation.py`, `platform/validation.py`, `api/validation.py`):** `_ReportFields` keeps the ten fields in stored order; `ValidationReport` is `_ReportFields` plus the properties; `ValidationReportView` adds `overall: OverallOutcome` and `counts: ReportCounts` with an `after` validator comparing both to `_overall_of`/`_counts_of`; `of()` dumps the report to JSON and validates (double validation per GET: no NFR budget names it; LOW observation). `load_report_view` merges acknowledgements with `model_copy` (unvalidated) and then `of()` revalidates, so a merged view cannot drift. G2 holds: only `load_report_view` and the route use the view; `store_report` is untouched.

**Findings (proposals)**
1. *Record:* the LG's Scope, Gate and Step 14 lines are stale at the head; window lines (A18) and the Audit section (A15) are still to be written in. Fix before close.
2. *Process (mint order, check 31):* `id 8380 is created: 2026-11-05, earlier than id 8374's 2026-11-07`. Same as LG 8374's Finding 1; the lead names the limb.
3. *LOW, nit:* the frontend export keeps the name `ValidationReport` for the view type (`validation.ts:4`, as planned: G4); a later reader could mistake it for the stored artifact. No action in this slice.
4. *Disclosure:* `ruff format --check` is rc 1 on four files not format-clean before this slice (LG Gate table); not this slice's.
5. *Owed to the gate:* DB-backed spec readers (`test_demo_guide`, `test_objective_submission`, ...), `test_api_authorisation_sweep.py` (item 43; the request shape is untouched, the response only) and `test_error_sinks.py` (item 45; no handler added), the frontend `Test Files N passed`, the demo. I have not read any of them and claim nothing.
6. *Item 42:* no `SL-8381` row exists at origin/main; closed by this audit's close commit or the slice stays open.

**Deviations named:** `as unknown as` in `validation.test.ts` (TS2352, outside the Write set, one line, accepted); `load_report_view` ends in one `return`; `ReportCounts` inline in `generated.json`. **My own:** see LG 8374's Audit section (the DB test file named in a run-small call; 13 ERRORs, no DB opened).

### Build log

- **2026-11-07 (R1, `f985190a`).** Fixture and tests committed alone. The base for A4: fixture added by `f985190a`, an ancestor of `ce3676c7`, the first commit in `b2636e85…..HEAD` touching `model_schema/validation.py` (`git log --diff-filter=A --format=%h -- packages/model-schema/tests/fixtures/validation-report-pre-fix.json`; `git log --reverse --format=%h b2636e85d425…HEAD -- packages/model-schema/src/model_schema/validation.py | head -1`).
- **2026-11-07 (R2, `ce3676c7`).** Deviation 1: `load_report_view` ends in one `return ValidationReportView.of(report)` after the optional acknowledgement merge, where Step 8 said both return paths end in `.of(...)`; the two are the same behaviour. Deviation 2 (a plan defect): Step 10 and the plan's frontend bullet said `validation.test.ts:30`'s `as` cast would still type-check without the two new keys; `pnpm --dir frontend type-check` returned `src/api/__tests__/validation.test.ts(21,10): error TS2352 … is missing the following properties … counts, overall`, rc 2. Fixed by casting that fixture through `unknown` with a comment (`frontend/src/api/__tests__/validation.test.ts`, outside the plan's Write set, one line); type-check then rc 0. No behaviour added (G4). `ReportCounts` is a functional `TypedDict` as Step 7 gave; it appears in `generated.json` inline as the `counts` schema (no separate component).
- **2026-11-07 (R3, `6fa1339a`).** `01` §4.6: the earlier "Clarified 2026-11-05" note (route does not yet serialise) is left as written and a new dated "Amended 2026-11-07" note follows it.

- **LOW note (audit Finding 4, adopted from-lead "2026-11-07 23:17:41 GMT"):** `ValidationReportView.of()` validates twice per `GET` (the report is dumped to JSON, then validated as the view, which runs `_derived_never_assigned`). No NFR names the route's cost, so there is no FD; recorded here so a later latency budget finds it.

## PRs

(none; no PR until the lead's word)
