---
id: LG-2046
family: ledger
title: WK-1178 slice SL-2045 — FD-1691, A/E weighted by the declared weight column (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-06   # original date 2026-11-05, working id 8360, minted 2026-11-06
owner: executor
tree: 38459124248d9969aa8679859f8637595814b981   # sl-8359-m-weighted-ae, the last code/test commit this was written against (base 9c4e703a104adfb9dcf0189896d5d64b800e98e3)
slice: SL-2045
phase: P2
work: WK-1178
plans: [PL-2044]
corrected_by: []
relates: [FD-1691, OQ-1692, PL-2044, FR-171, FR-183, FR-184, FR-186]
---

# LG-2046 — WK-1178 slice SL-2045: A/E weighted by the declared weight column

**GO / definition of record:** to-lead "2026-11-05 11:55:25 GMT" (corrects and strikes the `_weights` clause of "2026-11-05 11:50:05 GMT"); plan PL-2044 at `9c4e703a`; brief sha256 prefix `53784750564c`; R0 accepted to-lead "2026-11-05 12:03:55 GMT".
**MERGE-ACK:** (added at merge.)

## Tasks

### R0 — the enumerations (tree `9c4e703a`, `git grep`/`git show` only)

**DP-M3, a spec declaring both an offset and a weight column.** Two predicates, two answers.
(1) Line-local: every `WeightSpec(kind="column"…)` / `CLAIM_WEIGHT` / `ZERO_WEIGHT` site in `examples scripts backend packages` (less `packages/model-schema/src` and `*.json`), flagged when `OffsetSpec(kind="(log_column|column)"` occurs within ±12 lines — **prints 0**.
(2) Read of the two helper defaults — `_spec` in `packages/pricing-core/tests/test_gbm.py` (`"offset": EXPOSURE`, `:63`) and in `test_glm.py` (`"offset": OffsetSpec(kind="log_column", …)`, `:75`) — **finds 5** sites that build a spec with both: `test_gbm.py:1694` (weight `ones`), `:1716` (`claim_count`), `:1786` (`_custom_spec(…, weight=claim_count)`), `:1829` (`_spec(…, weight=claim_count)`), `test_glm.py:699` (`claim_weight`, a refusal test that never reaches diagnostics). None in `examples/`, `scripts/`, `backend/src` or `packages/*/src`. Ruled to-lead "12:03:55": proceed, the weight column wins.
**Burning-cost / pure premium:** predicate `git grep -n -E 'family="tweedie"|"family": *"tweedie"|ResponseKind\.BURNING_COST|response_column="burning_cost"' 9c4e703a -- examples scripts backend packages ':!*.json'`. Every spec site carries exposure as an offset (`log_column "exposure_years"`: `test_wf01_journey.py:530`, `test_model_jobs.py:829`, `test_glm.py:458`, `test_tweedie_power.py:70`, `test_diagnostics.py:229`; `kind="model"`: `test_peril_structures.py:722`) or has none (`test_peril_structures.py:124,:278`, `test_glm.py:973,:476`, `test_expression_objective_fit.py:135`). **None declares exposure as its weight column**, so T3's weight-column-exposure case is a **constructed fixture**.

### Test-file predicate (A9)

`git grep -lE ae_overall 9c4e703a -- '*test*'` prints **21**; `… -- 'packages/*/tests/*.py' 'backend/tests/*.py'` prints **15**. Files whose expected values moved: **none so far** (the two pricing-core files changed here carry new tests only; the DB-backed backend files are read in the window, below).

### Commits (branch `sl-8359-m-weighted-ae`, unpushed)

1. `ffd7101a` — T1–T6, committed alone and unrun (TESTS HOLD).
2. `913b4674` — code (`ae_weights`, `_partition`, `comparison.py`) + FR-171/183/184 dated lines + OQ-1692 DECIDED in both mirrors, one commit (A2).
3. `38459124` — T6 fixture fix (see the T6 note).

### Red / green lines (each names its tree)

Run via `run-heavy.sh --over-load`; logs `~/gi-pricing-plan.local/scratch/sl-8359-m-weighted-ae/logs/`, `head=` first line, `rc=` last.
- **Red, clean tree at `ffd7101a`** (`git apply --check -R` rc 0 on patch sha256 prefix `898cf679e0befcd5`, `git checkout -- .` rc 0, porcelain 0): `test_diagnostics.py -k …` → `4 failed, 1 passed, 31 deselected`: T1 `0.9772727272727273` vs `22400/22000 = 1.018181818181818` (the per-row `4300/4400`); T3 weight arm `1.0` vs `0.7368421052631579`; T4 `3000.0` vs `19000`; T5 `(0.964, 1.036)` vs `(0.380, 1.620)`. **T2 passed at the base** (green before and after, as designed).
- **Green, `913b4674`:** `test_diagnostics.py` → `36 passed in 67.56s`, rc 0. Patch re-applied by `git apply` rc 0, `git diff` sha256 prefix `898cf679e0befcd5` (same).
- **T6, a wrong-cause red withdrawn.** The first T6 sliced `claims[1500:]` of fewer than 1500 claim rows and failed on `MODELS_NOT_COMPARABLE` (empty holdout) at the base *and* on HEAD — not on the A/E. Fixed at `38459124` (split 2:1). By cause: the fixed test against the **base source** (`diagnostics.py`/`comparison.py` checked out from `ffd7101a`, own worktree, restored) → `1 failed, 11 passed`, `0.9808003017095513` vs `0.9810919563411584`; on HEAD → `12 passed`, rc 0 (`t6-fix.log`).
- **T2's mutation** (`ae_w = _weights(spec, data)` in `_partition`, restored by `git checkout HEAD -- diagnostics.py`, porcelain 0): `3 failed, 33 passed in 28.04s`, rc 1 — T2 (the double count caught), T3's offset arm (`0.7368421052631579` vs `1.0`), and `test_diagnostics_report_train_and_holdout_side_by_side` (`t2-mutation.log`).
- **Lint:** `ruff check .` flagged one PT018 in my T2 (fixed, rerun owed). `ruff format --check` on the four changed files reports all four "would be reformatted" at lines this slice did not write (`comparison.py:300`, `diagnostics.py:276`, `test_comparison.py:70`, `test_diagnostics.py:74`); the files were unformatted at the base and are left alone.

### Notes owed

- **Process slips:** two Bash calls carried a `cd` (`cd $W` in a read-only spec look-up; `(cd /tmp && true)` in the sync command); neither wrote anything.
- **SL-1913:** no rehearsal note pinning a severity A/E was found by this seat; the lead lists any such note for a dated line.
- **Frequency byte-identity (DP-M1):** T2 asserts `ae_overall`, each cell's `actual`/`expected`/`ae` and `ci_95` equal to the base formulas with `==`, green at `ffd7101a` and at `913b4674`.

### Window and gate

**DB window, 2026-11-05 17:12:21 → 17:18:00 GMT** (to-lead "17:11:38 GMT" (2); beside D's PYTEST stage, gate-1, `gipricing_sld_gate`), tree head `091e2c4c4906ba37fb022116729eb8d34c25d98a`. Slot `/tmp/slots/window-8359` (quoted from `/proc/$$/environ` on each call), DB copy `gi_sl8359` from `createdb -T gipricing` (all three URLs name it), redis `-n 11`, bucket `gip-test-blobs-8359`. START: `-n 0 dbsize` 56, `-n 11 dbsize` 0, `PUBSUB CHANNELS 'gip:switch:*'` empty, template guard `alembic_version=1 environments=3 tenant_marker=1`. Seven files, one per `run-heavy` call, all rc 0: `backend/tests/` `test_api_backtests` 6 passed, `test_backtests` 10, `test_diagnostics` 9, `test_ebm_model_jobs` 9, `test_glm_approximation_model` 15, `test_model_jobs_gbm` 19, `test_wf01_journey` 1. **No value moved** (A9: no expected value re-derived; none on a no-weight model moved). END: `-n 11 dbsize` 0, `-n 0 dbsize` 56, own DB count 0, `gipricing_sld_gate` present, template guard rc 0. Driver `scratch/sl-8359-m-weighted-ae/win.sh`, log `win-run.log`.

The SOLO gate: **owed** — recorded here when run.

## PRs

None yet: the branch ends unpushed (brief item 10); the lead pushes and opens the PR.
