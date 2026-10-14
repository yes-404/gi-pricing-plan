---
id: PL-1705
family: plan
kind: map
title: WK-1178 — SL-1543 (A-4) since PL-1542 was dated, the severity response claim_severity, the fit's loud refusal red, the synthetic book with the real-seed probe, SL 8003 before SL-1543, and the re-checked premises: a dated delta to PL-1542
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: 1e260c1553acf39844939fe12da685ccfb835e54
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1542, SL-1543, PL-1674, SL-1675, PL-1677, SL-1678, FD-1679, RL-1538, RL-1459, PL-1544]
---

# PL-1705 — WK-1178, SL-1543 (A-4): what has changed since PL-1542 was dated (delta to PL-1542)

*(Minted 2026-10-14 as PL-1705 from working id 8009, in the D15 batch mint PR.)*

> **For agentic workers:** this is a **dated delta** under Lean P2 L5 (`document-ids.md` §1.6,
> PL row: *"a change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's
> plan"*). It does not replace
> [`PL-1542`](PL-01542-wk-1178-a-4-the-exit-demo-walks-wf-699-s-peril-structure-path-leaf-plan.md)
> (A-4, `SL-1543`), whose body is frozen at its merge and is not edited. It follows the form of
> [`PL-1644`](PL-01644-wk-1178-exit-demo-b-wf-699-d4-s-fixed-property-declaration-and-the-lines-the-11-oct-merges-made-stale-plan-delta.md)
> (a delta to a frozen leaf plan), [`PL-1677`](PL-01677-wk-673-fd-1679-the-change-summary-refuses-two-versions-of-one-rate-table-slug-plan-delta.md)
> and [`PL-1682`](PL-01682-wk-1178-fd-1335-part-b-for-the-rate-table-import-route-a-typed-200-and-a-declared-201-plan-delta.md).
> It adds no slice row. **Read `PL-1542` in full, then
> [`PL-1674`](PL-01674-wk-1178-rows-whose-declared-weight-is-0-are-excluded-from-the-fit-and-every-diagnostic-plan-delta.md)
> (the slice before this one's severity steps), then this file. Where they differ, this file is
> the latest statement.** The executor of `SL-1543` binds what `PL-1542`'s header names
> (`python-test`, `test-driven-development`, `python-package`, `dev-commands`, `git-hygiene`),
> and is spawned from `.claude/roles/executor.md`.

Filed under **working id 8009**, reserved by the lead in `~/gi-pricing-plan.local/handover/eta.md`
at "2026-10-14 10:00:21 BST". Written 2026-10-14 from 10:03 BST (`TZ=Europe/London date`) by the
planner (seat planner-pl1542delta), on the lead's brief of the same morning. **Tree read:**
`origin/main` `1e260c1553acf39844939fe12da685ccfb835e54` (#1297) unless another ref is named. The
prep branch `origin/sl-1543-prep-on-1300` was read at `c5bc231def492b4c65b849afcad5020422d9c7dd`
(stacked on #1300, `SL-1675`). **No test or code was run at planning time**; every claim below
about behaviour is a reading of the code at the named tree.

Working ids cited below are written with a space (`SL 8003`, `PL 8002`, `RL 9996`, `LG 9879`)
because none is minted at this tree; the mint re-points them.

## Goal

Unchanged from `PL-1542` §"Goal" except C11: the freMTPL2 demo walks `WF-699`'s literal Peril
Structure path (a severity GLM, the AD Peril Structure reconciled and approved, B4's `model_call`,
the C1 pin). This delta records the inputs that changed since `PL-1542` was dated: how the
severity response reaches the Dataset Version, the fit's refusal red, where the T1/T2 tests run,
who fixes the signatures, E1's ordering behind `SL 8003`, and two premises the re-check moved.

## Status

`draft`. **DP-8009-1 (the refusal red's form, §"Decision points") is ruled (a)** (the maintainer (by delegation), "2026-10-14 10:09:06 BST"); every other change below is ruled by the entries quoted in §"The entries this delta records". The delta becomes `active` when it is minted. `SL-1543` stays `draft` in [`../roadmap.md`](../roadmap.md) at this tree; its GO is the
lead's, under §"Activation needs".

## The entries this delta records

All are local channel entries a repository reader cannot open (RFC-777), so the parts this delta
rests on are quoted verbatim. Each was read in full in the file named.

### 1. The severity response — the maintainer (by delegation), item (B)

The maintainer's (by delegation) entry in `~/gi-pricing-plan.local/channel/to-lead.md`, headed
*"2026-10-14 09:45:05 BST — PL 9997 DP-1..5 RULED; SL-1543 severity response RULED (amended: no
`_minor` name); E1 → SL 8003 on the G2 path CONFIRMED (re lead 09:43:40, 09:44:28)"*, item (B),
verbatim:

> **(B) SL-1543's severity response.** The plan is not silent on the formula: PL-1542 Task 1 Step 2 (:426-429) fixes the response as `claim_amount_minor / claim_count`, Gamma/log, weight `claim_count`, per 02 FR-111. It IS silent on how that reaches the Dataset Version the fit job reads. Ruled (a)(i), AMENDED:
> - **Name: `claim_severity`, NOT `claim_severity_minor`.** 00 FR-23 reserves `_minor` for integer minor units and is not scoped; a mean is a float ("keep the float, drop the suffix", OQ-544 / 01 FR-64). The name also matches FR-153's `ResponseKind` `claim_severity`.
> - Float64, computed in `seed.build_csv` as `claim_amount_minor / claim_count` (Polars true division, NO rounding), null where `claim_count = 0`, and cast in the ingest recipe. `claim_amount_minor` stays the integer money of record (FR-10). The float lives only as a fit input, which FR-10 permits.
> - The null rows are the weight-0 rows SL-1675 excludes and counts. Red required: a null or non-positive `claim_severity` on a row with `claim_count > 0` is REFUSED loudly by the fit (not silently dropped). Show it red, then green.
> - No placeholder response, no stubbed fit (05:39:20 stands). A derived-response expression in the Model Spec is refused for P2: it is a new capability with no spec.
> - (b) T1/T2 on a small synthetic DB-backed book: ACCEPTED for the slice tests, PROVIDED Task 0 Step 4's DP-A4-3 probe still runs on the real `--rows 20000` seed and the journey rehearsal walks the real seed end to end. The synthetic book never stands in for G2's evidence.
> - The `fit_severity_glm` / `create_ad_peril_structure` signatures are the executor's, shaped after `model.py` `_fit` and `compare_and_approve` and recorded in the LG. This is a dated pre-GO plan addition (PL-1542 is frozen at its merge: record it in SL-1543's LG and the next delta, not as an edit to the plan body).

### 2. E1 and SL 8003 — the maintainer (by delegation), 09:42:05 item 3 and 09:45:05 item (C)

The maintainer's (by delegation) entry headed *"2026-10-14 09:42:05 BST — RL 9996 (DP-P1)
CONFIRMED as drafted; fix slice to be cut now; G2 conditional; [SL 1695] fact corrected (re lead
09:41:01)"* (`to-lead.md`; the bracketed id is elided from its hyphen form because
it does not resolve in `docs/INDEX.md` at `1e260c15`), item 3, verbatim:

> 3. **G2 sequencing (yours, conditioned on the sl1543-prep read):** if E1's version pins two versions of one slug against an approved baseline, the fix slice JOINS the G2 path and merges before SL-1543. SL-1543 must not change E1's `expect=200`, re-order the journey to dodge the guard, or skip E1 (no faked step, as in my 12 Oct rulings). If E1 is not affected, the fix slice runs in parallel and is off the G2 path. Report the read and the decision to me, with the version and pins E1 drafts.

The 09:45:05 entry, item (C), verbatim:

> **(C) E1:** my 09:42:05 (3) condition is MET by your read (B1 → RV3 pins region@1 + region@2 against approved fremtpl2-demo@1 → `_pins_by_slug` 409 → E1 expect=200 fails). SL 8003 is ON the G2 path and merges BEFORE SL-1543. Identical-ref dedupe: a red in SL 8003, as you said. **Send a revised G2 ETA** with SL 8003 in series (it was about 1 executor-day per PL-1677 :157), together with the #1297 ETA.

### 3. The E1 read — the lead, 09:44:28 item (1)

The lead's entry in `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`, headed
*"2026-10-14 09:44:28 BST"*, item (1), verbatim:

> (1) E1 READ (executor-sl1543-prep, read-only, at main 36e2610a): TODAY E1 passes the SL-1678 guard — RV3 pins built at examples/fremtpl2/journey.py:653-658 from `table_refs` (dict keyed by factor; edits REPLACE the ref at :373 and :401; :728 asserts len(pins.rate_tables) == len(factors)); baseline = seed approved rating_version:fremtpl2-demo@1 (journey.py:1038), one seed @1 ref per slug. UNDER PL-1542 Task 3 B1 (a second `table` step on each seeded table's seed-origin version; check_step_refs_pinned requires every referenced table pinned) RV3 pins e.g. region@1 AND region@2 → `_pins_by_slug` (rating_versions.py:1405) raises 409 at the change-summary draft (:1335-1378) because a baseline exists → E1 expect=200 FAILS. Per the maintainer's 09:42:05 (3): the RL 9996 fix slice (SL 8003) JOINS G2 and merges BEFORE SL-1543. Open sub-question: whether Pins/create_rating_version dedupes IDENTICAL refs (else the seed baseline under B1 could trip it too) → to planner-dpp1fix as a red.

### 4. The Task 0 Step 2 re-check — the lead, 09:46:44

The lead's entry headed *"2026-10-14 09:46:44 BST"* (`from-lead-2026-10-09.md`), its sentence on
`executor-sl1543-prep`, verbatim:

> executor-sl1543-prep Task 0 step 2 (read-only at c5bc231d): P1, P2, P4 hold with moved lines; P3 STALE in our favour (decide_and_carry api/approvals.py:248 → perils_service.apply_approval_decision perils.py:498 now carries a decision to the structure); P5 CHANGED (DEMO_PREMIUM_IN * 2 gone; test_demo_rating_evidence.py derives _expected_minor :120); recorded in the LG at the GO.

**Checked against the primary source at `1e260c15`, not only the relay:** `decide_and_carry` is
defined at `backend/src/app/api/approvals.py:248` and its fan-out calls
`perils_service.apply_approval_decision(` at `:566`; that function is defined at
`backend/src/app/platform/perils.py:498`. `git grep -n DEMO_PREMIUM_IN 1e260c15 --
backend/tests/test_demo_rating_evidence.py` prints nothing, and `_expected_minor` is defined at
`backend/tests/test_demo_rating_evidence.py:120` (base × exp(Σ fitted log-relativities),
half-even to a whole minor unit).

## What changes in PL-1542

Each row names the frozen text it overrides. Nothing in `PL-1542` is deleted; where this table and
`PL-1542` differ, this table holds.

| # | `PL-1542` text (frozen) | Now | Authority |
|---|---|---|---|
| C1 | Acceptance 1: *"on the policies with at least one claim"*; Task 1 Step 2: *"builds the claims-only frame"* | The severity GLM fits the **full book**: the frequency GLM's `dataset_version_id`, `split_ref` and `holdout_part`, so `_refuse_unshared_holdout` (`backend/src/app/platform/perils.py`) passes and FR-190 is untouched. Rows with `claim_count = 0` carry weight 0 and are excluded and counted by `SL-1675` (`PartitionDiagnostics.rows_excluded_zero_weight`, `packages/model-schema/src/model_schema/diagnostics.py:164` at `c5bc231d`). | the maintainer's (by delegation) "2026-10-12 05:39:20 BST", (i) (quoted in `PL-1674` and in `LG 9879`); the `SL-1543` roadmap row's dated line of 2026-10-12 |
| C2 | Task 1 Step 2: response *"`claim_amount_minor / claim_count`"*, no column named | A new dataset column **`claim_severity`**, Float64, computed in `seed.build_csv` (`examples/fremtpl2/seed.py:121`) as `claim_amount_minor / claim_count` by Polars true division, **no rounding**, **null where `claim_count = 0`**, and **cast in the ingest recipe** (the `cast` step reads `NUMERIC`, `seed.py:71-80` and `:108`; the new entry is `"claim_severity": "float"`). `claim_amount_minor` is unchanged (FR-10). The spec is `response=ResponseKind.CLAIM_SEVERITY`, `response_column="claim_severity"`. | entry 1, bullets 1–2 |
| C3 | Acceptance 1: *"`ResponseType.CLAIM_SEVERITY`"* | The enum is **`ResponseKind.CLAIM_SEVERITY`** (`packages/model-schema/src/model_schema/modelling.py:786`, `:803`), carried on the spec's `response` field (`:831`). `ResponseType` does not exist at this tree. A stale name in the frozen text, corrected here. | this delta's read |
| C4 | none | **A new red, R1b** (§"Reds"): a null or non-positive `claim_severity` on a `claim_count > 0` row is refused loudly by the fit. Its form is DP-8009-1. | entry 1, bullet 3 |
| C5 | Acceptance 1 and 2 test on the seed | The tests for Acceptance 1 and 2 (`T1`, `T2`) run on a **small synthetic DB-backed book**, as `backend/tests/test_model_jobs.py`'s `TWEEDIE_BOOK` does. **Task 0 Step 4's DP-A4-3 probe runs on the real `--rows 20000` seed**, and **the journey rehearsal (Acceptance 7) walks the real seed end to end**. The synthetic book is never G2's evidence. | entry 1, bullet 5 |
| C6 | Task 1 Step 2 and Task 2 Step 2 name `fit_severity_glm` and `create_ad_peril_structure`, no signatures | The signatures are the executor's, **shaped after** `_fit` (`examples/fremtpl2/model.py:196`: `database, blob_store, workspace_id, actor, spec, label` → `UUID`) and `compare_and_approve` (`model.py:328`: `database, blob_store, workspace_id, actuary, approver, …` → `UUID`), and recorded in `SL-1543`'s ledger (`LG 9879`). **None was chosen at `c5bc231d`**: the prep branch carries no `fit_severity_glm` or `create_ad_peril_structure`. The next delta records them as the ledger states them. | entry 1, bullet 6 |
| C7 | Activation needs table (needs 1–8) | Replaced by §"Activation needs" below: needs 1–7 were MET at the 12 Oct GO; three needs are added. | entries 1–3; the roadmap row's dated line |
| C8 | none (E1 is not mentioned) | **E1 is out of `SL-1543`'s scope to change.** `SL 8003` (`PL 8002`, the `RL 9996` fix) merges first. `SL-1543` does not change E1's `expect=200` (`examples/fremtpl2/journey.py:954-960`), does not re-order the journey, and does not skip E1. Acceptance A11 below checks it. | entry 2 |
| C9 | P3: *"Today nothing moves the structure on a decision (P-need 2)"* | **Stale, in this slice's favour.** `decide_and_carry` (`approvals.py:248`) fans out to `perils_service.apply_approval_decision` (`:566` → `perils.py:498`). Task 2's approval goes through that carry. | entry 4, checked |
| C10 | P5: *"`test_demo_rating_evidence.py:72-73` asserts the fixture's golden quote (`DEMO_PREMIUM_IN * 2`)"* | **Changed.** The file derives each expected premium in `_expected_minor` (`:120`) from `_ESTIMATES` and `_BASE_MINOR`. Task 4 Step 2's "re-derive" means: replace `_expected_minor`'s formula with the ruled B1 combination (structure prediction × Π(pinned ÷ seed-origin cell)), computed in the test, never read back from the engine. | entry 4, checked |
| C11 | Goal: *"When this slice merges, G2 is met (PL-1544 Hand-off 6)"* | **Not this slice's claim.** G2 also waits for other slices under the maintainer's (by delegation) entries "2026-10-12 02:29:16 BST" item 3 and "2026-10-12 02:35:40 BST" (the roadmap's dated line under `PL-1544`'s slice), and `SL 8003` precedes this slice (entry 2). `LG 9879` already records this. | the roadmap's dated line of 2026-10-12; entry 2 |

**Not changed:** DP-A4-1 (B1, `RL-1538`), DP-A4-2 (c) and DP-A4-3 (the 7 factors, uncapped, tolerance
0.05, STOP above it), as ruled by `RL-1459`; the write set (no path under `backend/src/`,
`packages/`, `frontend/` or `docs/specs/`); Acceptance 2 to 9 except where a row above names them.
`examples/fremtpl2/seed.py` is already in `PL-1542`'s write set; C2 adds no path.

## Premises added at `1e260c15` (re-checked at Task 0)

- **P6. The fit refuses a null or non-positive response on a kept row, through the job.** Read,
  not run. `fit_glm`'s `except ValueError` (`packages/pricing-core/src/pricing_core/modelling/glm.py`,
  `:666-698` at `c5bc231d`) maps glum's refusals to `GlmFitError("GLM_FIT_FAILED", "glum refused
  the fit: …")`, naming among them *"`Some value(s) of y are out of the valid range for
  familyGammaDistribution.`"* and *"sklearn's `Input y contains NaN`"*. The fit handler maps a
  `GlmFitError` to a `PlatformError` with the same code (`backend/src/app/worker/model_handlers.py:395-401`
  at `1e260c15`), and `_fit` turns a non-`SUCCEEDED` job into `SystemExit(f"{label}: model.fit
  {status.value} — see job")` (`model.py:216-217`). `SL-1675` excludes only weight `== 0.0` rows
  (`weights.py` `drop_zero_weight_rows`, `:77-82` at `c5bc231d`: *"never `<= 0`, never a
  tolerance, never a null test"*), so a `claim_count > 0` row with a null or non-positive
  response reaches glum. **So the refusal R1b asks for probably exists already**, and R1b may be
  green on its first run. DP-8009-1 decides what "red first" means then.
- **P7. The ingest `cast` of `"float"` on an empty CSV field.** `build_csv` writes every column
  as text (`claim_amount_minor` is cast to `pl.Utf8`, `seed.py:150`), so a null `claim_severity`
  reaches the recipe as an empty field. Whether the `cast` step turns it into a null or refuses it
  is **not read here**. Task 0 checks it (new Step 6); if the cast refuses or fills it, STOP to
  the lead: the fix is in the platform's recipe, outside this write set.

## Reds — each by cause, with its assert and its expected failure

`R` numbers are this delta's. "Base" is the slice's base tree (main after `#1300` and `SL 8003`).
Each red is run once, its failure line copied verbatim into `LG 9879`.

| R | Test (file) | Exact assert(s) | Expected failure on base, by cause | Status at `c5bc231d` |
|---|---|---|---|---|
| R1 (T1) | `test_seed_fits_and_approves_a_severity_glm` (`backend/tests/test_demo_peril_structure.py`), on the synthetic book | the persisted model's spec: `spec.response == ResponseKind.CLAIM_SEVERITY`; `spec.response_column == "claim_severity"`; `spec.family == "gamma"`; `spec.link == "log"`; `spec.weight == WeightSpec(kind="column", column="claim_count")`; `spec.peril == "AD"`; `spec.dataset_version_id`, `spec.split_ref` equal the frequency GLM's; the model is `approved`; each partition's `rows_excluded_zero_weight` equals the synthetic book's `claim_count == 0` count in that partition | `AttributeError` naming `fit_severity_glm` on `examples.fremtpl2.model` — no severity path exists (`PL-1542` Task 1 Step 1's cause, *"no `claim_severity` model"*) | not written |
| R1b (new, C4) | `test_the_severity_fit_refuses_a_null_or_non_positive_severity_on_a_claim_row` (same file), parametrised over `None`, `0.0` and `-1.0` placed on one `claim_count > 0` row of the synthetic book | `pytest.raises(SystemExit)` around the executor's `fit_severity_glm`; the fit job's `status == JobStatus.FAILED`; its stored error `code == "GLM_FIT_FAILED"`; its detail contains `"glum refused the fit"`; no fitted model row reaches `fitted` | **DP-8009-1.** Under (a), recommended: on base, red by absence (`AttributeError`, as R1); then, once `fit_severity_glm` exists, if the assert passes at its first run, the red **by cause** is shown on deliberately broken input — a scratch, uncommitted planted `drop_nulls()`/`filter(> 0)` on the response in the fit path — printing the test's failure (`DID NOT RAISE <class 'SystemExit'>`) into `LG 9879`, then reverted | not written **Ruled shape (the maintainer (by delegation), "2026-10-14 10:09:06 BST"):** TWO cases, a null `claim_severity` and a `claim_severity` <= 0, each on a `claim_count > 0` row; each asserts code `GLM_FIT_FAILED` plus the family-domain sentence ("Gamma and Tweedie need strictly positive values") in the persisted error. |
| R2 (T2) | `test_the_ad_peril_structure_reconciles`, `test_the_ad_peril_structure_is_approved_through_the_workflow` (same file), on the synthetic book | as `PL-1542` Acceptance 2; the approval asserts the structure is `approved` after `decide_and_carry`'s carry (C9), with the approval event and the decision; Acceptance 2's negative grep prints nothing | `AttributeError` naming `create_ad_peril_structure` | not written |
| R3 (T3) | `test_b4_model_call_references_the_peril_structure` (`backend/tests/test_fremtpl2_algorithm.py`) | exactly one `model_call` step; `call.peril_structure_ref == structure`; `call.model_ref is None`; `call.mode == "exact"`; `set(call.feature_map) == set(_FACTORS)`; `call.result_type in ("decimal", "money_minor")` (`RL-1580`) | `TypeError`: `build_fremtpl2_algorithm()` got an unexpected keyword argument `peril_structure_ref` | **written** (`c5bc231d`); the commit message says it is red by that cause |
| R4 (T4) | `test_premium_is_the_ruled_combination` (`backend/tests/test_demo_peril_structure.py`) | as `PL-1542` Acceptance 4, with the expected values from `predict_glm` and the table cells, never from the engine; compared after the single half-even rounding, never as the raw decimal string (`LG 9879` Task 0 Step 5 (iii)) | on slice (a)'s algorithm the unedited-table premium is `base × Π relativities`, not the structure's prediction | not written |
| R5 (T5) | `test_b4_and_c1_are_walked_not_skipped` (`backend/tests/test_wf699_journey.py`), and the edits to `test_wf699_the_skip_and_known_gap_lines_are_exactly_the_ruled_ones` and `test_wf699_journey_runs_end_to_end` | `not [e for e in journey.SKIPS if e.step in {"B4", "C1′"}]`; `not [e for e in journey.SKIPS if "SL-1543" in e.line]`; the ruled-lines list no longer holds `"SKIPPED B4 model_call: FD-1456; SL-1543"` or `"SKIPPED C1′: FD-1456; SL-1543"`; `status[step] == "ok"` for `B4` and `C1′` | `journey.SKIPS` still carries both lines | **written** (`c5bc231d`) |

The executor may rename a test; the ledger then names the new name beside the one here.

## Activation needs, each with its state at `1e260c15`

`PL-1542`'s needs 1 to 7 were found MET at `604ea084` by the lead's GO (*"readiness found
activation needs 1-7 MET at `604ea084`"*, quoted in `LG 9879`). The needs below are what remains,
in order.

| # | Need | State at `1e260c15` |
|---|---|---|
| N1 | **`SL-1675` merged** (`PL-1674`, #1300): weight-0 rows excluded from the fit and every diagnostic | **open**: #1300 is `OPEN`, head `52e7ec5f` (`gh pr view 1300`, read 2026-10-14 10:0x BST) |
| N2 | **`SL 8003` merged** (`PL 8002`, the `RL 9996` fix; entry 2) | **open**: `PL 8002` is on `origin/pl-8002-wk673-dpp1-fix-2026-10-14` @`044396b5`, unminted; `RL 9996` is on `origin/rl-9996-dpp1-2026-10-14` @`0d8f1288`, unminted |
| N3 | **The severity ruling** (entry 1) | **MET**: the maintainer's (by delegation) "2026-10-14 09:45:05 BST" item (B) |
| N4 | DP-8009-1 ruled | **MET**: (a), the maintainer (by delegation), "2026-10-14 10:09:06 BST" |
| N5 | This delta minted, and the lead's GO for the build after N1 and N2 | — |

## Decision points

| DP | Question | Options | Recommendation | Owner | Blocks | Ruled |
|---|---|---|---|---|---|---|
| **DP-8009-1** | **What does "Show it red, then green" mean for R1b, if the platform fit already refuses (P6)?** | **(a)** R1b asserts the existing loud refusal (`GLM_FIT_FAILED`, the job `FAILED`, glum's cause in the detail) through `fit_severity_glm` on the synthetic book. Its first red is by absence (no `fit_severity_glm`); its red **by cause** is a broken-input proof: a scratch, uncommitted planted silent drop in the fit path, the test's failure printed into `LG 9879`, then reverted (`CLAUDE.md` §13: *"enforcement is proven on deliberately broken input"*). No new code. If R1b is instead red on base by cause (the null is in fact dropped silently), **STOP to the lead**: the fix is under `packages/` or `backend/src/`, outside this write set. **(b)** An examples-level precondition: `fit_severity_glm` checks the frame (`claim_count > 0` ⇒ `claim_severity` non-null and `> 0`) and raises before the fit job, with its own message. Red by cause on base (no check). Cost: the refusal is the seed's, not "the fit's" as entry 1 says, and it duplicates a refusal the platform already makes. **(c)** A dedicated platform refusal (a named code before glum, in `pricing-core`), red by cause. Cost: a `packages/` write, a permanent error code (`CLAUDE.md` §5) and a spec clause — a preceding slice, as `SL-1675` was, and a G2 slip | **(a).** Entry 1 says *"REFUSED loudly by the fit (not silently dropped)"*; P6 reads that the fit already does so, with glum's cause carried verbatim, and (a) proves it without a write outside `PL-1542`'s set. (b) refuses in the wrong place. (c) builds a second refusal for a case the first already covers, and costs G2 a slice | the maintainer (by delegation), on entry 1 | R1b only | **Ruled (a)**, the maintainer (by delegation), "2026-10-14 10:09:06 BST": assert the EXISTING refusal through `fit_severity_glm` (`glm.py`, the `except ValueError` clause below `LinAlgError`: `GlmFitError("GLM_FIT_FAILED", "glum refused the fit: … Gamma and Tweedie need strictly positive values … and both for nulls. Nothing was estimated.")`). R1b asserts the job fails with code `GLM_FIT_FAILED` AND the persisted error detail contains the family-domain sentence, in TWO cases: a null `claim_severity`, and a `claim_severity` <= 0, each on a row with `claim_count > 0`. Red by cause is the broken-input proof (a scratch silent drop of those rows before the fit makes R1b fail), printed in the `LG-`, then reverted. R1b red on the base tree means STOP (outside the write set). (b) and (c) rejected. |

No other decision is opened. The "probably" in P6 is a reading, and (a)'s STOP clause covers it
being wrong.

## Tasks

The additions to `PL-1542`'s tasks; every other step stands as `PL-1542` writes it.


- [ ] **Task 0 Step 1 (amended).** Confirm N1 and N2 at `origin/main`, by `git log` of the merge
  commits, and N4. If any is unmet, STOP.
- [ ] **Task 0 Step 2 (done, recorded).** P1–P5 as entry 4; record C9 and C10 in `LG 9879` with
  `1e260c15`'s lines.
- [ ] **Task 0 Step 3 (new, the seed census; the maintainer (by delegation), "2026-10-14 10:09:06 BST").** Before Step 4's probe, count on the real
  `--rows 20000` seed AND the full seed: the rows with `claim_count > 0` and `claim_amount_minor <= 0`,
  and the rows with `claim_count > 0` and a null amount. Record all four counts. If any is non-zero,
  the genuine severity fit refuses with `GLM_FIT_FAILED` (Gamma domain): STOP to the maintainer with
  the counts. No silent filter and no clipping: excluding nil-settlement claims is a modelling
  decision (FR-111 territory), not the executor's.
- [ ] **Task 0 Step 4 (amended, C5).** The DP-A4-3 probe runs on the **real** `--rows 20000` seed,
  never on the synthetic book. Record the reconciled ratio verbatim.
- [ ] **Task 0 Step 6 (new, P7).** On the real seed, after ingest: count the `claim_severity`
  nulls and the `claim_count = 0` rows of the Dataset Version; they must be equal, and no
  `claim_count > 0` row may hold a null or a value `<= 0`. Record both counts. If they differ, or
  the cast refused, STOP.
- [ ] **Task 1 (amended).** Step 1 writes R1 and R1b and records both reds. Step 2 adds the
  `claim_severity` column to `build_csv` and `"claim_severity": "float"` to `NUMERIC` (C2), then
  `fit_severity_glm` on the full book (C1), with `response=ResponseKind.CLAIM_SEVERITY` (C3). R1b
  goes green as DP-8009-1 rules. Step 3 records the signature in `LG 9879` (C6).
- [ ] **Task 2 (amended).** `create_ad_peril_structure`'s signature is recorded in `LG 9879`
  (C6). The approval goes through `decide_and_carry` (C9).
- [ ] **Task 4 Step 2 (amended, C10).** `_expected_minor` is replaced by the B1 combination,
  computed in the test.
- [ ] **Task 5 (amended, C8).** E1 is not edited. Before the gate, run A11's commands.
- [ ] **Task 6 Step 1 (amended, C5).** Acceptance 7's run is on the real seed (`--rows 20000`).

## Acceptance Standard

`PL-1542`'s Acceptance 1 to 9 stand, as changed by §"What changes in PL-1542". These are added;
each is checked by a command run from the repository root on the slice's merge tree.

10. **The severity column.** `git grep -n -E '"claim_severity": "float"' -- examples/fremtpl2/seed.py`
    prints one line; `git grep -n -E 'claim_severity_minor' -- examples backend/tests` prints
    nothing (FR-23); Task 0 Step 6's two counts are equal and recorded in `LG 9879`.
11. **E1 untouched (C8).** `git diff origin/main...HEAD -- examples/fremtpl2/journey.py | grep -nE '^[-+].*"E1"|^[-+].*change-summary-draft'`
    prints nothing, and `git grep -n -A5 '"E1",' -- examples/fremtpl2/journey.py` shows
    `expect=200` on E1's request, as at `1e260c15` `:954-960`. `SL 8003`'s squash commit on
    `main` (its sha named in `LG 9879`) is an ancestor of the slice head:
    `git merge-base --is-ancestor <that sha> HEAD` exits 0.
12. **R1b, red then green (C4).** `uv run pytest -q backend/tests/test_demo_peril_structure.py -k refuses`
    passes on the slice head, and `LG 9879` carries R1b's red line(s) as printed, of the form
    DP-8009-1 rules.
13. **The real seed.** `LG 9879` records the Task 0 Step 4 ratio and the Acceptance 7 run, both on
    `--rows 20000`, each with its command verbatim.
14. **The signatures (C6).** `LG 9879` quotes `fit_severity_glm`'s and `create_ad_peril_structure`'s
    `def` lines as committed; the next delta to `PL-1542` records them.

## Hand-off (not this plan's writes)

1. **The roadmap.** `SL-1543`'s row gains a dated line naming this delta and needs N1–N2; this
   planner writes `docs/roadmap.md` only for rows it cuts, so the line is the lead's.
2. **The next delta** records the signatures (C6) and DP-8009-1's ruling text, if it is ruled
   after this delta mints.
3. **Mint.** `PL-1705` mints from working id 8009; `SL 8003`, `PL 8002`, `RL 9996` and `LG 9879`
   are re-pointed where minted by then.

## Self-review

1. **Every item of the lead's brief is here.** Entry 1's eight points: C2 (name, Float64, no
   rounding, null, cast), C4 + R1b (the red), C5 (synthetic book, real-seed probe and rehearsal),
   C6 (signatures), "frozen body not edited" (this file's form). Entry 2 and item (3): C8, N2, A11.
   The 09:44:28 read: entry 3, C8. The 09:46:44 re-check: entry 4, C9, C10, checked at `1e260c15`.
   The prep branch: R3 and R5 read from `c5bc231d`; no T1, T2 or T4 red and no signature is on it.
2. **One decision opened, not picked:** DP-8009-1, with three options and a recommendation.
3. **What was not executed.** No test ran. P6 and P7 are readings; Task 0 Step 6 and DP-8009-1's
   STOP clause cover their being wrong.
4. **Type consistency.** `ResponseKind.CLAIM_SEVERITY`, `WeightSpec(kind="column", column=…)`,
   `JobStatus.FAILED` and `rows_excluded_zero_weight` were read at the trees named.
