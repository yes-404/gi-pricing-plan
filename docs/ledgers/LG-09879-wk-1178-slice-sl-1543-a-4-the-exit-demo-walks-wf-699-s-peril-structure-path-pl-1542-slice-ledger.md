---
id: LG-9879
family: ledger
title: WK-1178 slice SL-1543 — A-4, the exit demo walks WF-699's Peril Structure path (PL-1542), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: 604ea084c96efe93f521fb9ba17738e05241e61a
phase: P2
work: WK-1178
slice: SL-1543
plans: [PL-1542]
corrected_by: []
relates: [PL-1542, SL-1543, RL-1538, RL-1459, RL-1580, FD-1209, FD-1374, FD-1660]
---

# LG-9879 — WK-1178 slice SL-1543: A-4, the Peril Structure path

*(Working id 9879, reserved by the lead. The id is minted at the merge turn; until then every citation of this record is by working id.)*

**GO:** the lead's from-lead entry "2026-10-12 05:31:21 BST" (GO SL-1543; readiness found activation needs 1-7 MET at `604ea084`; ledger working id 9879). Authority for the scope: the maintainer's (by delegation) entries in `to-lead.md` "2026-10-10 21:33:57 BST" item 2 (A-4's needs), "2026-10-10 21:41:05 BST" item 8 (Task 0 carries RL-1580's `result_type` point and DP-A3-1 (c)), "2026-10-11 23:27:48 BST" and "2026-10-11 23:46:22 BST" (the SKIPPED set is B4 `model_call` and C1′), "2026-10-12 02:29:16 BST" item 3 (D7's fix is WK-673's SL 9850, not this slice's) and "2026-10-12 03:54:25 BST" (G2 is not met until SL 9850).

**G2 is not claimed by this slice.** PL-1542 Goal's sentence "When this slice merges, G2 is met" is stale: the maintainer's (by delegation) entry "2026-10-12 03:54:25 BST" holds G2 open until WK-673's SL 9850 merges. `examples/fremtpl2/journey.py` is shared with SL 9850; the second to merge re-merges main and re-gates.

**MERGE-ACK:** not yet given.

## Tasks

Base: `origin/main` `604ea084c96efe93f521fb9ba17738e05241e61a`. The activation commit is the branch's first.

### Task 0

### Task 0 — plan defect: the severity GLM cannot share the frequency GLM's holdout (2026-10-12)

**Finding (base `604ea084`).** `backend/src/app/platform/perils.py:639` `_refuse_unshared_holdout` refuses a structure whose component models do not cite one (`dataset_version_id`, `split_artifact_id`, `holdout_part`); `_reconcile` (`worker/model_handlers.py:1348`) derives its single holdout from the first candidate's spec. PL-1542 Acceptance 1 and Task 1 Step 2 fit the severity GLM on a claims-only frame, a different Dataset Version, so `create_structure` would refuse it. Fitting it on the full-book version fails instead: `pricing_core/modelling/glm.py` ~:671-692 documents that a nil-settlement row in a Gamma response raises `GLM_FIT_FAILED`. PL-1542 does not mention the shared-holdout rule.

**Spike (scratch, no commits; `pricing_core.modelling.fit_glm` and `compute_diagnostics` called directly, which is what the fit job calls at `model_handlers.py:374` and `:446`; a synthetic frame of 20,000 rows, 3 areas).** Option A (non-claimants carry response 1.0 and weight 0): the fit succeeds with one glum `RuntimeWarning: divide by zero encountered in divide` (`glum/_distribution.py:165`); the coefficients equal a claims-only fit's to the 14th digit (intercept 7.806226313974, `area[a]` -0.897677907610, `area[b]` -0.512106638573). The holdout diagnostics do not drop the zero-weight rows: `PartitionDiagnostics.rows` 14,000 against 1,939 claimant rows; `ae_overall` 0.1388 against 0.9987 claims-only; AE cell expected for area a 4,618,661.7 against actual 627,919.5; lift bin 1 has predicted 0.0 and actual 0.0. No fit-time row filter, exclusion or null-response handling exists in `model_handlers.py`, `platform/modelling.py`, `pricing_core/modelling/glm.py` or `diagnostics.py`, nor in `02` FR-111 or `ModelSpecCommon`.

**Ruling.** The maintainer's (by delegation) entry in `to-lead.md`, header "2026-10-12 05:39:20 BST — SL-1543 severity block: (i) a small PRECEDING WK-1178 slice ACCEPTED; the diagnostics finding is RESTATED (your "actual weighted, expected not" does not match the code); S4 beat-as-fixture reading OK" (read in full by the executor from the file; the lead's relay of it was paraphrase and is not the source), quoted:

> (i) ACCEPTED: exclude weight-0 rows from the fit AND from every diagnostic statistic. [...] The severity GLM then shares dataset_version, split and holdout_part with frequency, so FR-190's holdout rule stands untouched. No placeholder response anywhere.
> (ii) is refused for now: it changes FR-190's meaning. (iii) is refused: the structure is A-4's point.
> [...] G2 slips by this slice. SL-1543 continues only its non-severity Task 0 steps; record the slip in eta.

**The diagnostics finding, restated by the same entry (it corrects this record's spike reading).** "_partition :358-363: y = the raw response, ae_overall = Σy / Σmu, BOTH UNWEIGHTED; by-level A/E :373-374: both unweighted; calibration :408: divides by bin_exposure (weighted, via _weights :131-138)." The spike's numbers above stand as measured; the cause the executor gave ("actual weighted, expected not") was wrong, and the entry files the real defect (a declared weighting scheme applied to some statistics and not others) as MEDIUM, owner WK-1178, with an open question on which A/E the platform defines (the lead's working ids FD 9889 and OQ 9891). The preceding slice fixes only the weight-0 exclusion. This slice's severity work (Tasks 1 and 2, and what depends on them) waits for SL 9887; the gate turn moves behind it.

**Side finding (FD 9895, working id, D14).** `_pins_by_slug` (`platform/rating_versions.py:1404`) keys a version's rate-table pins by slug, so a version diff over a B1 version, which pins two versions of one slug, silently keeps one pin. Not in PL-1542's scope.

### Task 0 Step 5 — the B1 probes (RL-1538 item 3), engine level, scratch, 2026-10-12

Scratch script, not committed; `compile_bundle` + `load_bundle` over `test_rating_runtime.py`'s helpers, a fake resolver, an algorithm of two `table` steps (`rate_table:motor-expense@1` edited, `direct` 1.3; `@2` seed origin, `direct` 1.1) and one `expression` step. The `model_call` was left out (A-2/A-3 own it); the test below Task 4 adds it.

- **(i) Two versions of one slug pinned.** `RatingVersion.model_validate` accepts `pins.rate_tables = [@1, @2]` (no uniqueness validator in `Pins`); `create_rating_version` (`platform/rating_versions.py:258`) stores pins unresolved ("whether each ref exists ... is compile's"). `compile_bundle` accepted both and produced one bundle. **Not yet proven through the backend create route and `last-seed` rows** (to do with Task 3). One consequence found by reading: `_pins_by_slug` (`rating_versions.py:1404`) keys by slug, so a version diff over a version pinning two versions of one slug silently keeps one; a diff of a B1 version would read the later pin only.
- **(ii) The JDM table node reads both.** Evaluating the bundle returned `pinned_factor 1.3` and `origin_factor 1.1` for `channel=direct`.
- **(iii) The engine's decimal division.** The unguarded expression `100000 * pinned_factor / origin_factor` is refused by compile: `EXPRESSION_UNGUARDED_DIVISION ... (FR-274)`. The guarded form `origin_factor != 0 ? 100000 * pinned_factor / origin_factor : 0` compiles, and the engine returned `__exact__office_premium_minor = '118181.81818181818181818181818'` (and the float twin `118181.81818181818`). Python `Decimal(100000)*Decimal("1.3")/Decimal("1.1")` is `118181.8181818181818181818182` (28 significant digits); both round half-even to 118182, and they differ only at the 1e-23 place, so a golden test compares after the single rounding, not the raw string. Three evaluations were identical (replay-identical True). A non-terminating ratio (1.3/1.1) therefore replays exactly; neither probe fails, so B2 is not required by Task 0 (RL-1538 item 3 STOP not triggered), subject to the end-to-end run in Task 3/4.

## Build log

- **2026-10-16 09:37 BST — the 11:29:53 guard written** (`PL-1705` "The guard test", Acceptance 16): `test_guard_dp_a4_3_severity_is_uncapped_until_the_fr_127_glm_fix_merges` in `backend/tests/test_demo_peril_structure.py`, on the maintainer's (by delegation) entry "2026-10-14 11:29:53 BST" in `to-lead.md`. It asserts the persisted severity model's `GlmSpec.loss_treatment.kind == "none"` and every AD structure peril's `large_loss.kind == LargeLossKind.NONE`. It reads `fit_severity_glm` and `create_ad_peril_structure`, which do not yet exist on this branch, so it is red by absence (as R2) until Tasks 1 and 2 land, then green. It changes only together with the FR-127 GLM fix's merge, cited here. Not yet run (SL-1455 latency window).

## PRs

- Not yet opened; the lead's merge-turn mint resolves the working id.
