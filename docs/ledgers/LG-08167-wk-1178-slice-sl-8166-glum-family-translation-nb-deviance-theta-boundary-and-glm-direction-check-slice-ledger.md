---
id: LG-8167
family: ledger
title: WK-1178 slice SL-8166 — PL-8162 slice A, the glum family translation, the NB deviance, the θ boundary and the GLM direction check, slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: 31e03c8ebd3c37b0e42b658b82775339fa95fb19                  # the tree of merge 480d73ea (origin/main 71e481fa into the slice); the LG edits after it are under docs/ledgers and docs/INDEX.md only
phase: P2
work: WK-1178
slice: SL-8166
plans: [PL-8162]
corrected_by: []
relates: [PL-8162, SL-8166, FD-1723, FR-89, FR-110]
---

# LG-8167 — WK-1178 slice SL-8166: PL-8162 slice A

*(Working ids SL 8166 and LG 8167, reserved by lead 26 on 2026-10-22; unminted.)*

**GO:** to-lead.md "2026-10-22 16:02:49 BST — Maintainer: PL 8162 (FD-1723's residual limbs) ACCEPTED; …" (slices C, then A, then B).
**MERGE-ACK:** not yet given. Slice A merges after slice C (its FR-110 clauses).

## Tasks

Base: `origin/main` `f3462d8f`. Branch `sl-8166-wk1178-pl8162-a`, worktree `.claude/worktrees/sl-8166`.

### Scope

`PL-8162` slice A: FR-110 (glum family-name translation for all seven `GlmSpec.family` members; the NB θ declared and required; the NB deviance) and FR-89 (the GLM direction check, `GlmDiagnostics.monotonicity` and `monotonicity_omitted`), the builder's θ input. **Where the rulings of to-lead.md "2026-10-22 16:02:49 BST" differ from the plan draft @6b1de3a9, the rulings govern:** θ is R/MASS `glm.nb`'s (variance μ + μ²/θ, ruling 3), converted once to glum's α = 1/θ_R; the plan's DP-T (a)/A-R3 text states glum's form and is brought into line by exec-c at its activation (lead 26, 2026-10-22). `power(k)` is struck in slice C (ruling 1): no DP-K build. DP-M (b) adopted as recommended. FR-110 θ/NB spec text is slice C's; FR-89 text is here.

**NB-fits-today (ruling 2), by code reading only:** no path. Only `ModelRow(...)` constructor in `backend/src` is `platform/modelling.py:561` (`reserve_model`, status draft, no `fit_result`); `fit_result` is written only at `worker/model_handlers.py:573` (after `fit_glm`), `:1146` (surrogate; `approximation_spec` hardcodes `family="gamma"`, `pricing_core/modelling/transparency.py:113`) and `platform/modelling.py:947`; readers refuse an unfitted row (`_resolve_candidate` `model_handlers.py:691`, backtest `:1232` `MODEL_NOT_FITTED`); migrations only `UPDATE models SET status/diagnostics_id`; no import route in `api/models.py`; no NB in `examples/` or `scripts/`. At the base glum raised for the underscore names (`glum._glm.get_family` accepts `negative.binomial`, `inverse.gaussian` only). A draft NB spec can be stored. **Owed (DB window):** the read-only count of stored draft NB rows.

### Task list

| Task | Commit(s) |
|---|---|
| A1 reds (A-R1, A-R2, A-R3, A-R4, builder) | `c885191c`, `b44f8d3c`, `7a379e25`, `fc9107a8`, `2cb4ab3b`; banded test `9e5cf93d` (after the code: negative control below); fixture fix `b08fbef6` |
| A2 spec (FR-89 dated amendment) | `db41422c` |
| A3 model-schema | `e29cefcc` |
| A4/A5 pricing-core, A6 builder | `53d0433f` |
| static fixes; contracts regenerated | `cd9b3a9a`, then the `chore(contracts)` commit |

### Gate

All runs `run-small.sh` / the single-file vitest guard, under the `small-test` flock; whole files, no `-k`. Logs are copied to `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/` (the `/tmp/exec-a-*.log` originals are no longer cited; the durable copies are these files); each opens with `HEAD=`. The closure list is `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-closure.txt`, the pricing-core part `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-pk.txt`.

**Static at head `cd9b3a9a`→`b08fbef6`:** `ruff check` on the 9 changed `.py` files: `All checks passed!`; `mypy`: `Success: no issues found in 244 source files`; `lint-imports`: `Contracts: 4 kept, 0 broken.`; `generate-contracts.py --check`: rc 0, `54 generated contracts match the models`; `pnpm install --frozen-lockfile` and `generate:api` rc 0.

**RED, Python** (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-red2.log`): `HEAD=fc9107a803c0bf7012364abdbd91de500b643a18` plus an uncommitted overlay of `test_diagnostics.py` and `test_glm.py` from `b08fbef6`; files `test_diagnostics.py`, `test_glm.py`, `test_glm_spec_theta.py`: `21 failed, 78 passed, 1 warning in 10.66s` (an UNCOMMITTED overlay of `b08fbef6`'s two test files on the `fc9107a8` tree, not a commit's tree; recounted from the log by `grep -E "^E  +\w*(Error|Failed)" exec-a-red2.log`, 21 = 9+5+3+2+1+1). By cause: `TypeError: unit_deviance() got an unexpected keyword argument 'theta'` (1); `AttributeError: 'GlmDiagnostics' object has no attribute 'monotonicity'` (5, one is the banded test: "absence red"); `ValueError: The family must be an instance of class ExponentialDispersionModel or an element of [...]` from glum (3: `negative_binomial`, `inverse_gaussian`, and the theta-reaches-glum test; corrected from 6, RS 8183 B4); `ImportError: cannot import name 'glum_family'` (2); `Failed: DID NOT RAISE ValueError` (1) and `DID NOT RAISE ValidationError` (9). The five other families' fit tests and every pre-existing test pass. *First run (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-red1.log`, `HEAD=fc9107a8`, no overlay): 25 failed, 73 passed; five of the 25 were `KeyError: 'area[urban]'`, a defect in the new test (the base level is the most-exposed one, and `urban` was sometimes it), fixed in `b08fbef6` by making `rural` the majority.*

**Property red, negative control** (test written after the code; `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-nc.log`): `HEAD=b08fbef6a915deb3710d43964ed7733d0726ef06`, scratch mutation `for label in sorted(bandings[factor.banding_id].labels)` in `_glm_monotonicity` (`diagnostics.py | 2 +-`), `test_diagnostics.py`: `1 failed, 30 passed in 8.76s`, `FAILED …::test_a_banded_glm_factor_is_swept_in_band_order_not_label_order`, `AssertionError: assert False is True … holds=False, worst_violation=0.12444261908499157`; restored with `git checkout -- .`, porcelain 0.

**RED, frontend** (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-a-fe-red.log`): `HEAD=2cb4ab3bf4359488315b44390e877ea1a2cf2a71`, load1 4.91, `src/views/__tests__/ModelSpecBuilderView.test.ts` alone: `Test Files  1 failed (1)`, `Tests  1 failed | 10 passed (11)`, `Unable to find a label with the text of: /theta/i`.

**GREEN at `b08fbef6a915deb3710d43964ed7733d0726ef06`:** `test_diagnostics.py`+`test_glm.py`+`test_glm_spec_theta.py` `99 passed, 1 warning in 10.01s`; frontend file `Test Files  1 passed (1)`, `Tests  11 passed (11)`; text-grep derived set, NOT an import closure (corrected 2026-10-22 on RS 8183 B2; RS 8183's static import closure is 312 files, an upper bound, and this set of 75 is not a subset-proof of it); the gate's FULL suite is the decisive green (`grep -lE "GlmSpec|GlmDiagnostics|fit_glm|compute_diagnostics|compare_models|backtest_model|unit_deviance|deviance|from pricing_core.modelling|import pricing_core.modelling|DiagnosticsResult" -r packages/*/tests backend/tests`, 75 files; 45 under `packages/`, 30 under `backend/tests` DB-backed): model-schema 9 files `54 passed`, `36 passed`, `30 passed`; `test_backtests`+`test_bandings`+`test_comparison` `47 passed in 7.68s`. **Pricing-core closure, all 45 files (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/green-closure3.log` for files 13-45, run after W2 END at `HEAD=44be7b58877c93d6a9ac5aeb85e29af746a344fe`, whose only changes since `b08fbef6` are under `docs/ledgers`; load1 2.21-4.97 printed per batch):** `60 passed`, `51 passed`, `227 passed, 4 warnings`, `72 passed, 4 skipped`, `47 passed`, `136 passed`, `73 passed`, `29 passed`, `53 passed`, `21 passed`, `53 passed`, each `rc=0`, 0 failed. **DB window, 2026-10-22T16:14:19Z to 16:31:01Z** (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/db-window.log`; script `db-window-commands.sh` v3; `HEAD=08bbecac01e8e75e2b394aa3f7841f294f3832ac`; `GIP_GATE_SLOT=unset`; redis `PUBSUB CHANNELS 'gip:switch*'` = `gip:switch:local:local:{prod,uat,dev}`, each NUMSUB 2, under the maintainer's extension of the switch exception, to-lead 17:12:17, while FD-1838's gate ran). `createdb gipricing_sl-8166_1c95b45f` (hyphenated) rc=0; `alembic upgrade head` rc=0. **A0 (read-only):** `gipricing` 0; `gip` database absent; the fresh slice DB 0 (fresh DB, 0 by construction, not evidence). `gipricing` is the migrations-only template, so its 0 shows no NB row in the template and says nothing of other deployments. **Backend closure, 30 files, 10 `run-small.sh` runs, every rc=0, nothing failed:** `94 passed, 21 warnings`; `187 passed, 2 skipped, 1 warning`; `62 passed, 1 warning`; `35 passed, 10 warnings`; `49 passed, 1 warning`; `41 passed, 8 warnings`; `46 passed, 1 warning`; `60 passed, 11 warnings`; `41 passed, 1 warning`; `30 passed, 2 warnings`. `dropdb rc=0`; leftover databases like `sl-8166`: 0. No failure, so no read against the switch overlap was needed.

### Deviation (RS 8183 B1, disclosed post hoc 2026-10-22)

The FR-89 spec commit `db41422c` landed AFTER the code commits `e29cefcc` and `53d0433f`, against `PL-8162` acceptance item 3 (spec first). History is not rewritten; the order is recorded here and was found by the auditor on RS 8183 B1.

### GREEN additions, 2026-10-22 (exec-8166b, tree of merge 480d73ea, load1 3.2-3.6, `GIP_GATE_SLOT` unset)

- **Re-merge of `origin/main` `71e481fa`** (RS 8183 B4): `git merge-tree` rc=1, `docs/INDEX.md` the only conflict, main's taken and regenerated (`doc-index.py` rc 0); merge commit `480d73ea`; `generate-contracts.py --check` rc 0 (`54 generated contracts match the models`); `pnpm generate:api` rc 0.
- **The six frontend files RS 8183 B2 found never run**, each alone under the item-28 guard (`test -f`, exact path, `Test Files  1 passed (1)` shown), all rc 0: `src/router/__tests__/reachability.test.ts` 2 tests; `routeGraph.test.ts` 9; `src/views/__tests__/DemoView.test.ts` 7; `DiagnosticsView.test.ts` 16; `ModelComparisonView.test.ts` 6; `ModelDetailView.test.ts` 20.
- **Skips named (RS 8183 B3)**, `PYTEST_ADDOPTS=-rs` through `run-small.sh`, own database `gipricing_sl-8166_1c95b45f` (created from the template, migrated, dropped; leftover 0), log `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/exec-b-skips.log`: `test_artifact_usage_counts.py`+`test_backtests.py`+`test_contracts.py` `187 passed, 2 skipped, 1 warning in 23.79s`, rc 0; the 2 skips are `backend/tests/test_contracts.py:1341` and `:2072`, both `got empty parameter set for (slug)` (a parametrize over an empty slug list), NOT a database or MinIO skip. `test_glm_scalar_predict.py` `34 passed, 4 skipped`: `:398`, `:408` and `:546` `examples/fremtpl2/data is not fetched (sha256-pinned, gitignored)`, and `:438` `the Factor shape refuses a bare 'expression' before any resolver sees it`. Redis `gip:switch:local:local:gate-1b:{uat,dev,prod}` were present (FD-1838's gate), none of them the slice's; `gip:switch` NUMSUB 0.

### Open observation (RS 8183 B4)

A stored draft negative-binomial `GlmSpec` without θ now fails `GlmSpec` validation on load. Counted read-only on 2026-10-22 (exec-8166b, 16:45Z, one SELECT per database, no open transaction) at the maintainer's direction (to-lead "2026-10-22 17:41:48 BST" item 3). `\l` lists `gipricing`, `gipricing_fd-1838_gate`, `postgres`, `template0`, `template1`; the `gip` database is absent. Persisting: `gipricing` (the compose database that survives a run). Per-run: `gipricing_fd-1838_gate` (FD-1838's gate database), counted anyway; `postgres`, `template0` and `template1` are system databases. The only column holding a spec is `models.spec` (JSONB; the one `jsonb` column with `spec` in its name, and the θ is `spec->'family_params'->>'theta'`, per `GlmSpec` in `packages/model-schema/src/model_schema/modelling.py`), draft and non-draft alike. SQL verbatim: `select count(*) as nb_models, count(*) filter (where (spec->'family_params'->>'theta') is null) as nb_without_theta from models where spec->>'family'='negative_binomial'`. Result: `gipricing` 0 NB models, 0 without θ; `gipricing_fd-1838_gate` 0, 0 (`gipricing` holds 0 models in all). The count is 0 everywhere countable here; it says nothing of a deployment this box does not hold. Verdict: **deferred with owner WK-1178**.

### Evidence (RS 8188) — re-run and persisted 2026-10-22 (exec-8166c, head `afdea77451f0c8edcf6a1530ac1677a10c001ecf`, tree `71504d9806e236d419a4f3ed1181462b26ecf0fd`)

RS 8188 found the claims above had no durable log. Each log below opens with `git rev-parse HEAD`, `HEAD^{tree}`, `date -Is` and load1, and ends `rc=0`. This is a re-run on the head above, not the original runs.

- **B2, the six frontend files**, each alone under the item-28 guard (`test -f` printed, exact path, load1 < 6, flock `small-test`), each log showing `Test Files  1 passed (1)`:
  - `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/evidence-8188/reachability.log` — `src/router/__tests__/reachability.test.ts`: `Tests  2 passed (2)`, rc=0.
  - `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/evidence-8188/routeGraph.log` — `src/router/__tests__/routeGraph.test.ts`: `Tests  9 passed (9)`, rc=0.
  - `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/evidence-8188/DemoView.log` — `src/views/__tests__/DemoView.test.ts`: `Tests  7 passed (7)`, rc=0.
  - `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/evidence-8188/DiagnosticsView.log` — `src/views/__tests__/DiagnosticsView.test.ts`: `Tests  16 passed (16)`, rc=0.
  - `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/evidence-8188/ModelComparisonView.log` — `src/views/__tests__/ModelComparisonView.test.ts`: `Tests  6 passed (6)`, rc=0.
  - `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/evidence-8188/ModelDetailView.log` — `src/views/__tests__/ModelDetailView.test.ts`: `Tests  20 passed (20)`, rc=0.
- **B4, contracts:** `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/evidence-8188/contracts.log` — `54 generated contracts match the models`, rc=0.
- **B4, the NB count:** `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/evidence-8188/nb-count.log` — the SQL verbatim above, run read-only on each database `\l` lists that holds the `models` table: `gipricing` `0 | 0`, `gipricing_fd-1838_gate` `0 | 0`, `gipricing_sl-8185_215125e7` `0 | 0`, each rc=0 (`gipricing_sl-8185_215125e7` is another seat's per-run database, counted anyway; `postgres` and the templates are system databases).
- **B3, skips:** `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl-8166/evidence-8188/b3-scalar-predict-rs.log` — `PYTEST_ADDOPTS=-rs` through `run-small.sh`, `test_glm_scalar_predict.py` `34 passed, 4 skipped in 3.47s`, rc=0 (the four skips as named above; a first attempt was refused by `run-small.sh` at load1 6.44, exit 66, and re-run when the box was quieter).

### Audit

Not yet.

### Build log

- **2026-10-22 — design.** `glm_family` / `r_theta_from_glum_theta` in `glm.py` are the only place the family names and θ conversion are written; `unit_deviance`/`deviance` take `theta` and raise for NB without it; `_theta_of` threads it to the partition, type-III, backtest and comparison call sites. `_glm_monotonicity` reuses `_resolved_axis`, `_representatives` and `_skipped_ids`; a numeric identity factor is swept over its 5th–95th percentile grid and a banding in its own `labels` order; operands, expression factors and unordered factors are recorded as omissions. A GBM-style `_sweep` reuse was not taken: it is bound to `predict_gbm` and sorts labels.
- **2026-10-22 — DEVIATION, disclosed (lead 26):** the executor's small-test pytest (pid 1798645, `sl-8166`, the loop batch `test_demo_b4_premium.py test_diagnostics.py test_ebm.py`) held `/tmp/slots/small-test` at 16:22 BST, during W2's ALONE window and after the lead's "W2 START". The loop had started the batch before the message was read, and the executor then stopped the loop; the lead reports W2 is a functional red, so no harm. Nothing of the executor's ran after.
- **2026-10-22 — `pkill -f <pattern>` was used to stop that loop** and also ended the executor's own shell; a pattern kill can hit other seats' processes and is not to be used (lead 26): only own PIDs are stopped. The batch re-runs after W2 END.

## PRs

(none yet)
