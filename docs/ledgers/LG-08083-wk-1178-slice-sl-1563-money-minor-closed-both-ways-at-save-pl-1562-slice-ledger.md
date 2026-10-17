---
id: LG-8083
family: ledger
title: WK-1178 slice SL-1563 — money_minor closed both ways at save, the numeric type check (PL-1562), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-17
owner: executor
tree: 6bdd2571c9069c163ecab248630e75f93be280be
phase: P2
work: WK-1178
slice: SL-1563
plans: [PL-1562]
corrected_by: []
relates: [FD-1424, RL-1564, OQ-1560, PL-1627, RL-1445, FR-227, FR-226]
---

# LG-8083 — WK-1178 slice SL-1563: money_minor closed both ways at save

Executed by executor-1563 from PL-1562 (with PL-1627 §A's delta). Branch
`sl-1563-wk1178-fd1424-prep-2026-10-16`, merged with `origin/main` 6bdd2571. Times are BST.

**GO:** `to-lead.md` "2026-10-17 13:23:18 BST — Maintainer: GO SL-1563 …" and RL-1445 (a)/(b),
written in the activation commit `fe91ffec`.

## Named deltas

- **A-2 control replaced** per `to-lead.md` 2026-10-05 17:49:25 item 1 and the maintainer's
  2026-10-17 13:25:47 ruling (a): PL-1562 Task 3 Step 3's "unedited" premise was false at main.
  In `test_rating_glm_model_call.py`, `("money_minor","decimal")` leaves the legal control
  (which keeps `("decimal","decimal")`) and `"decimal"` joins the refused list; the
  `"model_call" in message` assert becomes `"money_minor"` (PL-1627 §A1, :463), because the
  A-2 branch is removed.
  Red under D1, cause quoted: `RATING_TYPE_MISMATCH: output 'risk_out' is declared 'decimal' but
  its producing step yields 'money_minor' (FR-227)`.
- **Sweep hit 1, PL-1562 item 7, ruled 2026-10-17 13:31:51:** `test_a_model_call_equals_predict_glm_at_full_precision`
  (`test_rating_glm_model_call.py`) fed a `money_minor` `model_call` into a `decimal` output (D1). Red:
  same message as above, raised by `compiled_bundle`. Now a single `decimal` → `decimal` run.
- **Sweep hit 2, PL-1562 item 7, ruled 2026-10-17 13:31:51:** `test_testing.py` `_variant`'s `optional_output`
  branch fed an `int` input `promo` into a `money_minor` output (D10). Red: `RATING_TYPE_MISMATCH: output
  'extra_minor' is declared 'money_minor' but its producing step yields 'int' (FR-227)`. **Deviation
  from the ruling's literal form, confirmed by the maintainer at 2026-10-17 13:40:06 BST (the 13:31:51 form
  had a false premise):** `RatingInputType` (`model_schema/rating.py`) has no `money_minor`
  member, so `promo` stays `int` and an explicit `money_minor` expression step (`s_promo_money`) feeds
  the output (OQ-1560 A1's form). The fail and pass asserts are unchanged and green.

## Tasks

### Task 0 / Task 1: reads and sweep

- Re-anchored by symbol: `_compatible`, `output_type_issues`, `_check_result_types`,
  `fragment_output_type_issues`, the mount-port caller (`_refuse_mount_port_type_mismatch`).
- Sweep, non-test sources: `closed_rule` applied to `scripts/bench-score-batch.py`,
  `bench-compiled-for.py`, `bench-rating.py` (3 builds): 0 hits; `examples/fremtpl2/algorithm.py:166-191`
  read by hand: `decimal` → `money_minor` at an output step (A2), 0 hits.
- Sweep, tests: a probe plugin wrapping `_compatible` over nine `packages/pricing-core/tests` files
  (compile_bundle, ladder_control, ladder_exact, pin_membership, runtime, score, testing,
  glm_model_call, quote_input_raise_sites): hits 1 and 2 above, plus A-2's own refusal cases.
  Backend DB-backed files are swept in the DB window (owed).
- Item 11 (/score vs batch): FD-1561 is cited, not rediscovered; the read-only comparison is owed.

### `_compatible` callers, with the flag each passes

`output_type_issues` ← `_check_result_types` (`at_output_step=True`) and
`fragment_output_type_issues` (`False`); the mount-port check in `compile.py` (`False`, brief
condition 1). No other caller in `packages`, `backend/src`.

### Task 5

RL-1564 Form A applied to FR-227's row (`03-rating-engine.md`) after A-2's existing dated
amendment, dated 2026-10-17 (the applying commit). RL-1564 calls it FR-227's first dated
amendment; it is the second, A-2's (2026-10-10) being already on the row.

### Item 11: /score vs batch, read-only (executor-1563db, 2026-10-17 13:53 BST, head 713d296a)

One allowed widening, `int` and `count` step into a declared `decimal` output, built from
`test_rating_score_batch_outputs.py` `_probe_payload` (`result_type` set to the producer type,
declared `decimal`, expr `driver_age`), compiled (accepted at save), then `score_one` and
`score_batch` over three rows. `/score` served the JSON integer (`18`, `22`, `25`, python `int`);
batch served the decimal string (`"18"`, `"22"`, `"25"`). **They differ for an allowed pair**: PL-1562
item 11 option (b), reported to the lead for an auditor to file; the slice continues. No stored
refused pair is involved. Script: `~/gi-pricing-plan.local/scratch/sl1563-dbwin/item11.py`, run with
`uv run --directory <detached worktree at 713d296a> python -I`; rc 0.

### DB window 1 and backend sweep start (executor-1563db, 2026-10-17 13:58-14:02 BST)

- Probe plugin proof (`probe_compat.py`, run through `run-small.sh` over `test_testing.py` and
  `test_rating_glm_model_call.py` in a detached worktree at 713d296a with those two files from ac7d0f0e): it
  logged hit 2 (`int->money_minor` in `test_testing.py`) and hit 1 (`money_minor->decimal` in
  `test_rating_glm_model_call.py`), so it sees a refusal. Log: `scratch/sl1563-dbwin/proof.log`.
- Red-first, item 4, base ac7d0f0e with `test_sub_graphs_api.py` from 3a19a47d: `test_a_sub_graph_port_feeding_money_minor_into_decimal_is_refused`
  FAILED `assert 201 == 422`, the quoted red. (Two other failures there were `BLOB_NOT_FOUND`, the template-DB `blobs` trap, a wrong-cause red.)
- Window 1 at 3a19a47d (tree a828ea0f), own DB, `truncate blobs cascade`, bucket `gip-test-sl1563`: `test_sub_graphs_api.py` 32 passed,
  `test_sub_graphs_service.py` 12 passed, `test_rating_algorithms.py` 24 passed; END rc=0.
- Sweep hits in window 1 (all three are deliberate negative tests asserting `422 RATING_TYPE_MISMATCH`; not fixed, STOP to the lead per PL-1562 item 7):
  `test_sub_graphs_api.py::test_an_output_port_type_mismatch_is_refused_rating_type_mismatch` (`string->money_minor`),
  `test_sub_graphs_api.py::test_a_sub_graph_port_feeding_money_minor_into_decimal_is_refused` (`money_minor->decimal`, item 4's test),
  `test_sub_graphs_service.py::test_a_refused_write_leaves_no_row_and_no_event` (`string->money_minor`).

### Backend sweep, windows 2-7 (executor-1563db, 2026-10-17 14:02-14:11 BST, head 276e6a9b)

The lead's ruling (2026-10-17, relayed): a refused `_compatible` call inside a test that asserts that refusal and passes is not a
sweep hit; a hit is a refused call in a test that fails, or in a fixture whose test expects success. The three window-1 refusals
above are therefore "logged by the probe, deliberate refusal tests, not hits". Windows (own DB, blobs truncated, bucket
`gip-test-sl1563`, probe loaded, each END rc=0, alembic 1 head): w2 `test_fr240_governance` 9, `test_rating_version_dislocation_gate` 25,
`test_bundle_slot` 17; w3 `test_rating_version_change_summary_route` 21, `test_custom_objectives` 31, `test_score_as_at` 8; w4 `test_score` 52,
`test_dislocation_runs` 24, `test_fremtpl2_algorithm` 13; w5 `test_rating_algorithm_validate` 15, `test_rating_versions` 48,
`test_regression_runs` 13; w6 `test_rating_version_compile` 25, `test_regression_suites` 15, `test_score_compare` 21; w7 `test_wf699_journey` 12
(all passed). Probe refusals logged: only `test_rating_algorithm_validate.py::test_a_type_mismatch_is_reported_on_its_step` and
`::test_the_first_reported_issue_is_the_code_save_refuses_with[type_mismatch]` (`string->money_minor`, deliberate, passing); no other file logged any.
**Hits: 0.** Item 4, `test_sub_graphs_service.py` and `test_rating_algorithms.py` are no longer owed.

## Owed

Full two-half gate (grant needed), the auditor's re-check, the mint step.

## PRs

None opened by the executor; the lead opens and merges. Branch `sl-1563-wk1178-fd1424-prep-2026-10-16`.

## Delta — literal code assert (2026-10-17)

Named delta, per the maintainer (by delegation) entry "2026-10-17 14:12:05 BST — Maintainer: SL-1563 review hit → (b); sweep DONE noted" in `to-lead.md`: a one-line literal assert `saved.json()["code"] == "RATING_TYPE_MISMATCH"`, guarded to the `type_mismatch` param, added to `backend/tests/test_rating_algorithm_validate.py::test_the_first_reported_issue_is_the_code_save_refuses_with`, applied before the gate so the gate covers it; no separate small run.
