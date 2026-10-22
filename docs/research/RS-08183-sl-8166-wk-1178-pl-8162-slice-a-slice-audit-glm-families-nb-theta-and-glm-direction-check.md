---
id: RS-8183
family: research
kind: audit
title: SL-8166 (WK-1178) PL-8162 slice A slice audit — glum family translation, NB deviance and θ boundary, GLM direction check
status: draft
created: 2026-10-22
owner: auditor
tree: 58390b34bed8926b64951335c149d23afc3e1173
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-8166, LG-8167, PL-8162, FD-1723, FR-89, FR-110]
---

# RS-8183 — SL-8166 slice audit (PL 8162 slice A)

*(Working id 8183, written by `aud-8166` (auditor, sonnet, effort medium), 2026-10-22 17:35 BST, from `brief-aud-8166-2026-10-22.md` (lead 26). Check 31 on this id is expected until the mint. Slice and ledger are cited by their working ids `SL-8166` and `LG-8167`.)*

## Question

Does `origin/main...sl-8166-wk1178-pl8162-a` meet PL 8162 slice A's acceptance items and the maintainer's rulings of 2026-10-22 16:02:49 BST, and is the evidence for each item reachable and honest?

## Method

Range `origin/main...sl-8166-wk1178-pl8162-a`; `origin/main` `71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5`; branch tip `eece638c23b122c17ce899a9f78eb2d6de726a9e`, tree `58390b34bed8926b64951335c149d23afc3e1173`; merge-base `f3462d8fc1336dc4583fe8a7af92fed399993a55` (main has since moved by #1359). 17 commits, 16 files, +804/−18 (`git diff --stat origin/main...<tip>`). Read by `git show/diff` only. No test, DB, docker or gate was run by this seat. Two static runs on a `git archive` copy of the tip: `ruff check` on the 9 changed `.py` files (rc 0, "All checks passed!") and a Python `ast` import scan (below). `PL-8162` read at `draft/pl-8162` `6b1de3a9`; the maintainer's rulings from `to-lead.md` "2026-10-22 16:02:49 BST".

**The branch is not on origin.** `git ls-remote origin sl-8166-wk1178-pl8162-a` prints nothing; the tip exists only in the local worktree `.claude/worktrees/sl-8166` (`git branch -a --list '*8166*'`). Audited from the local ref; the executor must push before any PR (seat-brief item 8).

## Findings

### Verdict proposal: NOT-CLEAN — 4 blocking items, none of them a maths or code defect

The maths, the θ boundary and the direction rule are correct (sections 2 and 3). The blocks are record and evidence defects, each cheap to fix. Verdict is the lead's.

| # | Blocking item | Fix |
|---|---|---|
| B1 | Spec-first order broken (acceptance item 3); not disclosed in LG-8167 | lead rules: accept the deviation (recorded in the LG) or reorder |
| B2 | "GREEN by import closure" was a text grep; the true closure is larger and part of it was never run (item 29) | gate full suite decisive; LG wording corrected; frontend router tests added |
| B3 | 2 backend skips are unnamed and may be `conftest_db` skips; 3 of 4 pricing-core skips are inferred, not read | rerun that batch with `-rs` (lead grants) |
| B4 | Branch unpushed, based on `f3462d8f`; LG has stale or wrong fields; audit section empty | push; re-merge main (item 21); LG corrections below |

### 1. Scope from PL 8162 slice A, then evidence (acceptance items 3–6, 8–10; item 7 is `power(k)`, slice C's strike)

| Item | Evidence | Result |
|---|---|---|
| 3 Spec first | `git log --reverse -- docs/specs/` shows `db41422c` only. Order: `c885191c`, `b44f8d3c`, `fc9107a8` (reds), **`e29cefcc` (model-schema code), `53d0433f` (pricing-core code), then `db41422c` (FR-89)** | **B1** |
| 4 All 7 families fit (A-R1) | red: 3 glum `ValueError` for NB/IG/θ (`exec-a-red2.log`); green: `test_glm.py` 99 passed with the other two files | delivered, tested |
| 5 θ declared, never defaulted (A-R2) | `GlmSpec._a_negative_binomial_declares_its_theta_and_no_other_family_does` (`modelling.py`): NB needs `0 < θ < inf` (NaN fails `0.0 < nan`); other families refuse a θ. Red: 9 `DID NOT RAISE ValidationError` | delivered, tested |
| 6 NB deviance uses θ (A-R3) | section 2 | delivered, tested |
| 8 Direction checked (A-R4) | section 3 | delivered, tested |
| 9 One contract | contracts changed: `openapi/generated.json`, `schemas/generated/diagnostics.schema.json` only; LG records `generate-contracts.py --check` rc 0. **Not re-run by this seat** | delivered, not re-verified here; the gate re-proves it |
| 10 Builder sends θ | red `Unable to find a label with the text of: /theta/i`; green 11/11. The view starts empty, posts `family_params.theta` only for NB and only when set; the test covers empty, 2, and switching to gamma | delivered, tested |
| Spec §4 contract field list | `02-modelling.md` carries the two new fields only inside FR-89's amendment; no §4 listing of `GlmDiagnostics` fields exists to extend (`grep` for `type_iii_omitted`/`GlmDiagnostics` hits FR-89, 173, 178, 183 only) | nothing to extend; verdict: no gap |

FR-110's θ and NB clauses are slice C's by the plan and the LG says so; slice A cannot merge before slice C (LG says the same). Not a defect.

### 2. NB deviance and the θ↔α boundary (do 2)

Code (`diagnostics.py` `unit_deviance`): `2·[y·ln(y/μ) − (y+θ)·ln((y+θ)/(μ+θ))]`, with the `y>0` guard on the first term (the `y=0` limit is `−2θ·ln(θ/(μ+θ))`). Matches the brief's formula. NB no longer shares the Poisson branch. Recomputed independently in plain Python: `y=0, μ=1, θ=2` gives 1.6218604324326578 (test pins ...575, abs 1e-12 passes); `y=2` gives 0.4711321426255344 (exact match); `θ=1e9` is within 1.7e-7 of Poisson (test tolerance 1e-6). So the hand values in the test are correct.

Boundary: `glum_family("negative_binomial", theta=θ_R)` returns `NegativeBinomialDistribution(1/θ_R)`; glum's variance is `μ + θ_g·μ²`, so `θ_g = 1/θ_R` is the right translation. The test checks `unit_variance(mu) == mu + mu²/θ_R` against glum's own object, not a re-statement of the code, and a float32 round trip. The conversion is written once (`glum_family`); `r_theta_from_glum_theta` is used only by the test. A missing θ raises `ValueError` (never glum's 1.0). `unit_deviance` also refuses `θ ≤ 0` and `None`; `θ=inf` passes that check and returns NaN, but `GlmSpec` refuses inf, so it is unreachable from a spec.

All deviance call sites with a GLM spec pass θ: `diagnostics.py` (`compute_diagnostics` ×2, `_partition` via `compute_diagnostics` and `backtest_model`, `_type_iii`), `comparison.py:277`, `glm.py` CV `deviance(...)`. The remaining callers are GBM `_permutation_importances` (family from `objective_family(spec)`, no NB), `glm.py:471` (`family="tweedie"`) and `transparency.py:236-237` (`gamma`). `git grep -n -i negative_binomial` over `packages/*/src` outside the GLM files finds nothing, so no GBM path can reach the new `ValueError`. Predicate: `git grep -n -E '\b(unit_)?deviance\(' <tip> -- packages backend`, non-test lines.

### 3. The GLM direction check (do 2)

`_glm_monotonicity`: for each factor with a declared direction, hold the factor's source column at each axis value, predict, take the mean, difference successively, `worst = max(0, max(against))`, `holds = worst <= 1e-9`. Same rule as the GBM block. Omissions by reason: interaction operand (`_skipped_ids`), expression factor, everything else non-numeric / non-banding (`unordered_levels`, which also covers cross and interaction types). Numeric identity: 10-point 5th–95th percentile grid, de-duplicated and sorted. Banding: the banding's own `labels` order, via `_resolved_axis`/`_representatives` (reused, not a second axis rule, as A5 requires). A declared direction yields a check or an omission, never nothing, matching the amended FR-89.

Negative control (LG `exec-a-nc.log`): HEAD `b08fbef6`, scratch mutation `sorted(bandings[...].labels)`, `test_diagnostics.py` `1 failed, 30 passed`, failing test `test_a_banded_glm_factor_is_swept_in_band_order_not_label_order`, `holds=False, worst_violation=0.1244`. A mutation that sorts the labels is caught, so the test pins band order. I read the log and the commit; I did not re-run it.

Residual observation, not blocking: a factor sourcing the same column as a second factor is swept by holding the column for both; an edge nobody declared today.

### 4. Red-first (do 3)

| Red | Committed before its code? | Cause by name |
|---|---|---|
| A-R3 `c885191c` | yes (before `53d0433f`) | `TypeError: unit_deviance() got an unexpected keyword argument 'theta'` |
| A-R1/A-R2 `b44f8d3c`, `7a379e25` | yes | glum `ValueError` family refusal (3); `ImportError glum_family` (2); `DID NOT RAISE` (10) |
| A-R4 `fc9107a8` | yes | `AttributeError: 'GlmDiagnostics' object has no attribute 'monotonicity'` (5; absence reds) |
| builder `2cb4ab3b` | yes | missing θ label |
| banded A-R4 `9e5cf93d` | **no — after the code (`53d0433f`)** | none at base; proven by the sorted-labels negative control instead (disclosed in the LG) |
| fixture `b08fbef6` | test-only fix after the red | `KeyError: 'area[urban]'` ×5 in the first run |

Disclosed and accepted as disclosed: the first run (`exec-a-red1.log`, 25 failed) had five reds from a fixture defect in the new test (the base level was sometimes `urban`), not from the feature; they were fixed in `b08fbef6`, and the recorded red (`exec-a-red2.log`, `21 failed, 78 passed`) is `fc9107a8` with an **uncommitted overlay** of `b08fbef6`'s test files, so no commit in the history is red by exactly the recorded causes. Accept, but the LG should say the overlay is the recorded state.

LG defect: its cause tally for the 21 failures (1+5+6+2+1+9) sums to 24. The log gives: 5 `AttributeError`, 3 glum `ValueError`, 2 `ImportError`, 1 `TypeError`, 9 model-schema `DID NOT RAISE`, and 1 `Failed: DID NOT RAISE ValueError` (the NB deviance without θ), which is 21 (`grep -c '^FAILED'` = 21). The glum count is 3, not 6. Correct in the LG.

### 5. GREEN set and skips (do 4)

Item 29 (the maintainer, "2026-10-22 13:36:57 BST" and "13:47:41 BST") bars a text grep of module names. The LG's set is `grep -lE "GlmSpec|GlmDiagnostics|fit_glm|...|deviance|from pricing_core.modelling|..." -r packages/*/tests backend/tests`: a text grep (75 files = 45 + 30), and the LG labels it "import-closure". **B2.**

Independent static closure (`ast` scan of the tip, `python3 -I`, predicate: changed modules `model_schema.modelling`, `model_schema.diagnostics`, `pricing_core.modelling.{comparison,diagnostics,glm}`; level-1 importers; level-2 importers; every test importing any of them): **312 test files** (141 under `packages/`, 171 under `backend/tests`). The LG's 75 are a subset (`comm -13` of the two lists is empty). The width comes from the `model_schema` package re-export hub (it imports both changed `model_schema` modules), so it is an upper bound under the rule as written. It is evidence for the rule's consequence, not a request to run 312 files through `small-test`: **the slice's gate full suite is the decisive green**, and the MERGE-ACK quotes its "Test Files N passed" line (item 29).

Frontend: `ModelSpecBuilderView.vue` is imported by `router/index.ts` (level 1), which `main.ts`, `DiagnosticsView.test.ts`, `ModelComparisonView.test.ts`, `ModelDetailView.test.ts` import (level 2); tests importing the router or the view: `ModelSpecBuilderView.test.ts` (run, 11 passed), plus `router/__tests__/reachability.test.ts`, `router/__tests__/routeGraph.test.ts`, `DemoView.test.ts`, `DiagnosticsView.test.ts`, `ModelComparisonView.test.ts`, `ModelDetailView.test.ts` (**not run**). `reachability` and `routeGraph` are the SL-1554 class (graph-shaped tests the slice's view can break). Predicate: `grep -rlE "ModelSpecBuilderView|router/index|@/router" --include=*.test.ts frontend/src` on the tip copy.

Skips:
- **Pricing-core batch `test_glm_model_offset.py test_glm_scalar_predict.py test_groupings.py` (`72 passed, 4 skipped`, `green-closure3.log`)**: the markers read in the source are `test_glm_scalar_predict.py:330` (`pytest.skip("examples/fremtpl2/data is not fetched ...")`) and `:438` (`pytest.skip(f"the Factor shape refuses a bare {kind.value!r} ...")`, per-kind); the other two files have none. 4 = 1 + 3 is **inferred, not read** (the run had no `-rs`). Both are about scalar prediction on a dataset / Factor kinds, not the slice's code; they do not hide it.
- **Backend batch `test_artifact_usage_counts.py test_backtests.py test_contracts.py` (`187 passed, 2 skipped`, `db-window.log:66`)**: **unnamed.** None of the three files contains a `pytest.skip`/`skipif`; the skip must come from `backend/tests/conftest_db.py:190,197,214` (Postgres unreachable, no migrations, MinIO unreachable) or another helper. If it is `conftest_db`, two DB-backed tests, possibly the backtest ones that call `backtest_model`, did not run. **B3**: rerun that batch with `-rs`, or read the skip reasons from the gate run.

Item 21 (re-merge): the branch base is `f3462d8f`; main is `71e481fa` (#1359). The closure and the contract regeneration must be re-checked at the re-merged head.

### 6. A0 / NB today (do 5)

Conclusion in the LG: no path to a persisted NB model today. Checked: `ModelRow(` is constructed once in `backend/src` (`platform/modelling.py:561`), `fit_result` is written only at `worker/model_handlers.py:573`, `:1146` (surrogate, `gamma`) and `platform/modelling.py:947` (`git grep -n -E 'ModelRow\(|fit_result *=' origin/main -- backend/src`). At the base, `fit_glm` passed `negative_binomial` to glum, which refused it (`exec-a-red2.log`: "The family must be an instance of class ExponentialDispersionModel or an element of [... 'negative.binomial' ...]"), so no NB fit result could be written, and with no fit there is no diagnostics row. The reasoning holds by reading; I accept the conclusion. Labelling is honest: the LG says the DB count (`gipricing` 0, fresh slice DB 0 "by construction") is not evidence and rests on code reading. One consequence not stated in the LG: a *draft* NB spec without a θ, if one is stored in a deployment, now fails `GlmSpec` validation on load (the validator is not version-gated); a count of such rows is owed per environment, not provable from the template DB. Pre-release, low risk; the verdict is "deferred with an owner" — the lead names it.

### 7. Disclosures (do 6) and spec changes (do 7)

- **W2 overlap**: disclosed in the LG build log (small-test pytest pid 1798645 held the slot at 16:22 BST during W2's ALONE window). Disclosed; consequence is the lead's. Noted: the DB window then ran 16:14:19–16:31:01Z overlapping that time, and "no harm" rests on the lead's report; this seat did not check the channel for a ruling on it.
- **`/tmp` logs moved to scratch**: the LG cites `…/scratch/sl-8166/` paths; all cited files exist there (`exec-a-red1.log`, `exec-a-red2.log`, `exec-a-nc.log`, `exec-a-fe-red.log`, `exec-a-fe-green.log`, `green-closure3.log`, `db-window.log`, `exec-a-closure.txt`, `exec-a-pk.txt`). The files for batches 1–12 of the pricing-core closure are in `exec-a-green-closure*.log` at an earlier HEAD (`b08fbef6`), not at `44be7b58`; the LG says so.
- **`pkill -f`**: disclosed, with the rule against reuse. Nothing else to add.
- **Spec**: FR-89's amendment cites the working ids `PL-8162`/`SL-8166` (fine until mint, then re-point, seat-brief item 26 whole-tree grep). The amendment adds to the original FR-89 sentence without contradicting it (the original said "checked (not enforced) for GLMs", and the amendment says it is now built). Ten sections intact (one-row diff to one table cell). **Spec-first order broken: B1.** The amendment text is accurate against the code (axis, `1e-9`, three omission reasons).

### 8. LG-8167 corrections owed (B4)

1. Front matter `tree: b08fbef6…` is stale (the tip is `eece638c`); the file's own status is "Audit: Not yet".
2. Red-cause tally (section 4) sums to 24 for 21 failures.
3. "import-closure" label on a text grep (section 5).
4. The spec-first deviation (B1) is not mentioned.
5. State that the recorded red is an overlay run.

## Proposed record

NOT-CLEAN, 4 blocking items (B1–B4), all fixable without changing the code. The lead's decisions: B1 accept-and-record or reorder; B2 gate wording and the 6 frontend files; B3 `-rs` rerun; B4 push + re-merge + LG edits. After those, a narrow re-audit (the RE-audit rule) of B1–B4 only, named against the re-merged range.
