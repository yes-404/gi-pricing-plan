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
- **2026-10-16 10:14 BST — Tasks 1 and 2 written, NOT RUN (the ALONE latency gate of SL-1455 is running; writing and git only).** Base `b2fc37d1`; #1309's diff (`git diff --stat origin/main 5098ebd1`) names no path of this write set except `docs/INDEX.md` and `docs/roadmap.md`, which this commit does not edit (after #1309 merges).
  - **Signatures (PL-1705 C6, as written; the prep tests' proposal is replaced).** `examples/fremtpl2/model.py`: `fit_severity_glm(database, blob_store, workspace_id, actuary, approver, frequency_id) -> UUID` (fits Gamma/log, weight `claim_count`, response `ResponseKind.CLAIM_SEVERITY` on `claim_severity`, no `loss_treatment`; its Dataset Version, split and factors are COPIED from the frequency model's own spec, so FR-190's shared holdout holds by construction (C1); approves it through `_approve_model`, extracted from `compare_and_approve`) and `create_ad_peril_structure(database, blob_store, workspace_id, actuary, approver, frequency_id, severity_id, *, tolerance: Decimal) -> UUID` (one `frequency_severity` component, `large_loss = LargeLossTreatment(kind=NONE)`; real `PERIL_STRUCTURE_RECONCILE` Job on `claim_amount_minor` / `exposure_years`; `submit_for_review`; `approval_service.decide`; `perils_service.apply_approval_decision`; no direct status write). `AD_RECONCILIATION_TOLERANCE = Decimal("0.05")` (DP-A4-3). The prep tests passed `version_id, split, factors` and a tuple of two approvers; they now pass `frequency_id` and one approver.
  - **Divergence from `PL-1542` Task 2 Step 2, named, not chosen silently.** The plan says `approval_service.decide` "with two principals". `DEFAULT_POLICY`'s `peril_structure` entry has `approvers_required=1` (`packages/model-schema/src/model_schema/approvals.py`, the entry after the 2026-08-18 comment), so one decision by a Principal who is neither submitter nor author reaches `approved`; a second decision would be refused (`APPROVAL_ALREADY_DECIDED`). The code decides once. **Ruled 2026-10-16 10:17:07 BST** (the maintainer's entry in `to-lead.md`, "2026-10-16 10:17:07 BST", DP-1543-APPROVERS (a)): the policy governs, per `docs/specs/06-governance.md:358` (`peril_structure`, `approvers_required` 1) and `DEFAULT_POLICY`; `PL-1542`'s "two principals" is the plan's error (corrected by a dated line in PL 8055; `PL-1542`'s body is frozen). The build stands: ONE approver, distinct from the submitter AND the author; `test_the_ad_peril_structure_is_approved_through_the_workflow` asserts exactly one decision, the approver's id differing from both, and `approved` after that one decide.
  - **`examples/fremtpl2/seed.py` (PL-1705 C2).** `build_csv` derives `claim_severity` (Float64 true division, no rounding, null where `claim_count = 0`; the raw `ClaimNb` is cast to Float64 for the test and the division, because the raw column is text); `NUMERIC` gains `"claim_severity": "float"`; `DICTIONARY` gains a `claim_severity` entry (`test_the_dictionary_covers_every_column_the_seed_produces`). `run` calls `fit_severity_glm` then `create_ad_peril_structure` after `compare_and_approve`, before the Rating Version.
  - **Stale cites found at base `b2fc37d1` (checked by symbol):** (1) `PL-1542` Task 1 Step 2 `model.py:169` for `_fit`: it is `model.py:196` (before this commit's edits); `PL-1705` C6 already says :196. (2) `PL-1705` C9 `approvals.py:248` names `decide_and_carry`, which is in `backend/src/app/api/approvals.py:248`, not `platform/approvals.py` (no such symbol there); the `:566` fan-out to `perils_service.apply_approval_decision` is in `api/approvals.py:566` and holds. (3) `PL-1705` C8 `journey.py:954-960` for E1's `expect=200`: those lines are the `submit` helper; E1's step opens at `journey.py:964` (`"E1"`) and records at `:971`. (4) `PL-1542` Task 2 Step 2 "two principals" against the policy's `approvers_required=1` (above).
  - **Owed runs (none run):** Task 0 Steps 3, 4 and 6 (the seed census, the DP-A4-3 probe on the real `--rows 20000` seed, the `claim_severity` null census); R1 and R2 red-by-absence are recorded on the prep branch, the green runs of `test_demo_peril_structure.py` need a DB window; `test_seed.py` (the dictionary test and the portfolio-frame test see the new column) and the full gate.
- **2026-10-16 10:26 BST — fix pass on the read-only review (still NOT RUN; ALONE gate).**
  - **Signatures, quoted verbatim from the commit (F10)** (`examples/fremtpl2/model.py`):
    `async def fit_severity_glm(database: Database, blob_store: BlobStore, workspace_id: UUID, actuary: Principal, approver: Principal, frequency_id: UUID) -> UUID:` and
    `async def create_ad_peril_structure(database: Database, blob_store: BlobStore, workspace_id: UUID, actuary: Principal, approver: Principal, frequency_id: UUID, severity_id: UUID, *, tolerance: Decimal) -> UUID:` (each parameter is on its own source line; joined here only for the ledger line).
  - **PL-1705 Acceptance 12's selector (F3).** `-k refuses` selects no test: the R1b tests are `test_a_clean_severity_book_fits` and `test_a_claimant_row_without_a_positive_severity_fails_the_fit_with_its_own_cause`. The corrected selector is `-k "clean_severity or without_a_positive_severity"`. `PL-1705` lets a renamed test stand when the ledger names it; the plan is frozen and not edited.
  - **The guard's red and green (lead ruling).** The Step 0 red of `test_guard_dp_a4_3_severity_is_uncapped_until_the_fr_127_glm_fix_merges` is run at `b2fc37d1` (the prep commit; red by absence: `AttributeError` naming `fit_severity_glm`) in a detached worktree; its green is run at the gated head, on the real asserts.
  - **The Task 0 Step 3 census decides the severity book (F5).** No code filters a claimant row whose `claim_severity` is not positive. `PL-1705` Task 0 Step 3 counts them on the real seed; a non-zero count is a STOP to the maintainer, not a silent filter in `build_csv` or the fit.
  - **The structure ref is looked up by slug (F9).** The AD Peril Structure is found by `AD_STRUCTURE_SLUG` (`fremtpl2-ad`), not from `last-seed.json`; to confirm at Task 3 (the journey), when `journey.py` first reads it.
  - **`_approve` (F8).** The test's own copy of the approval helper is deleted; `_structure_world` calls `demo_model._approve_model` (the signature fits: `change_summary` and `comment` are keyword arguments).
  - **Other review items done.** F1 the U+00D7 sign in `change_summary` is now `x`. F4 `test_claim_severity_is_the_mean_cost_per_claim_and_null_without_a_claim` in `examples/fremtpl2/test_seed.py` (count 2 with a total of 15,001 cents gives 7,500.5 exactly; null at count 0; `claim_amount_minor` stays the integer). F6 `create_ad_peril_structure` prints the reconciliation ratio, status and tolerance after the Job, and `fit_severity_glm` prints the deviance and AIC after the fit (Task 0 Step 4 and Task 1 Step 3 record them verbatim). F7 the book builds its own `np.random.default_rng(BOOK_SEED)` inside `_book`. F11 the structure docstring, the tolerance comment and `change_summary` carry DP-A4-3's words, "a simplification: no large-loss loading" (`RL-1459`).
  - **Owed after GATE END:** Task 0 Steps 3, 4 and 6; the guard red at `b2fc37d1`; the DB tests (`test_demo_peril_structure.py`); `test_seed.py`; ruff and mypy on `examples/fremtpl2` and the test file.

## PRs

- Not yet opened; the lead's merge-turn mint resolves the working id.
