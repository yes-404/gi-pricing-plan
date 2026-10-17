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

## Audit

*(Written by `auditor-1563`, 2026-10-17 17:23 BST, on head `3e8cc2f4f8db17efb329d2def4d6d034f9f67a44` (tree `5ae23b6eee120445ff0ca3a42440acfa0d5ed380`, equal to the gate's START tree), range `origin/main...3e8cc2f4`, `origin/main` = `9469721d` at fetch, merge-base `6bdd2571`. Code read-only; no test run by the auditor; the gate is the lead's.)*

**1. Change set** (`git diff --stat origin/main...3e8cc2f4`, 12 paths, +598 -70): `compile.py`; tests `test_rating_compile.py`, `test_rating_decimal_money_rounds_once.py` (new), `test_rating_glm_model_call.py`, `test_testing.py`, `backend/tests/test_sub_graphs_api.py`, `backend/tests/test_rating_algorithm_validate.py`; `03-rating-engine.md` (FR-227 row), `roadmap.md` and `PL-1562` (`draft` → `active`), `INDEX.md`, this ledger. Beyond PL-1562's write set: `test_testing.py` (hit 2) and `test_rating_algorithm_validate.py` (literal assert), both ruled (13:31:51, 14:12:05); `test_rating_glm_model_call.py` is PL-1627 DP-7 (i).

**2. Obligations, derived from PL-1562's Acceptance Standard, FD-1424's Disposition and the rulings first, then evidenced:**
- **Items 1-3 (one red per refused direction, three paths):** `test_output_type_issues_refuses_a_closed_direction`, `test_an_algorithm_output_refuses_a_closed_direction`, `test_a_fragment_port_refuses_a_closed_direction` are parametrised over D1-D8, D10-D25 (D9 added on items 1 and 3); each asserts the code `RATING_TYPE_MISMATCH` and the step (`s_probe_out` / `s_last`), not only a count. The served half (D1 fractional expression) is `test_a_money_minor_expression_feeding_a_decimal_output_is_refused`. **Met.**
- **Item 4 (route end to end):** `test_a_sub_graph_port_feeding_money_minor_into_decimal_is_refused` asserts `422` then `code == "RATING_TYPE_MISMATCH"`; ledger quotes the red (`201 == 422`, with the two `BLOB_NOT_FOUND` failures disclosed as the wrong-cause trap). **Met.**
- **Item 5 (one refusal):** `test_a_refused_pair_raises_exactly_one_issue`, expression and `model_call` producers, `len == 1`; A-2's `model_call_money_issues` and `_money_model_call_names` are gone (`git grep` finds none outside records). **Met.**
- **Item 6 (controls):** A1, A3-A7 on all paths (`test_a_widening_pair_is_allowed`), A2 (`test_a_decimal_into_a_money_minor_output_step_is_allowed`), the A1-expression control, and the mount-port allowed set. **Met.**
- **Item 7 (sweep):** non-test sources and tests swept (ledger Task 0/1); backend DB windows 1-7 report 0 hits. Five refusals logged by the probe are all passing negative tests that assert the code: `test_sub_graphs_api.py::test_an_output_port_type_mismatch_is_refused_rating_type_mismatch` (`string->money_minor`, `:97` code), `..::test_a_sub_graph_port_feeding_money_minor_into_decimal_is_refused` (`money_minor->decimal`), `test_sub_graphs_service.py::test_a_refused_write_leaves_no_row_and_no_event` (`string->money_minor`, `:146` code), `test_rating_algorithm_validate.py::test_a_type_mismatch_is_reported_on_its_step` (`string->money_minor`, code in the found-set) and `::test_the_first_reported_issue_is_the_code_save_refuses_with[type_mismatch]` (code asserted by the 14:12 literal). I read all five asserts. **Met.**
- **Item 8:** `git grep "the bundle compilation resolves" -- packages/pricing-core/src` prints nothing; `_compatible`'s docstring states the rule and cites 17:36:28 and 17:42:06. **Met.**
- **Item 9 (gate):** see section 4. **Met, with the cascade.**
- **Item 10 (write set):** section 1; every extra path has a ruling. **Met.**
- **Item 11 (/score vs batch):** the ledger records the differing values (`18` vs `"18"`), option (b). The finding is `FD 1767` (on `origin/main` at `1959b861`, MEDIUM). **Met; the ledger does not cite FD 1767 (A1).**
- **Item 12 (a)(b)(c):** (a) `test_a_fragment_with_a_decimal_money_port_saves`; (b) `test_a_decimal_into_a_money_minor_output_step_rounds_once` asserts `served == 1358`, `type(served) is int`, and `test_a_second_rounding_would_differ_from_the_single_one` asserts `1357.840 -> 1358` against the double-rounded `1357`; (c) `test_a_mounted_decimal_port_rounds_once_at_the_parent_output` exists (`SL-1340` merged first, #1263, so this slice owed it). **Met; the ledger does not name (b)/(c) (A1).**

**3. Named deltas against their rulings:**
- **A-2 control (13:25:47 (a)):** `("money_minor","decimal")` leaves the legal control, `"decimal"` joins the refused list, the assert is `"money_minor" in issues[0].message`, and the message does say `yields 'money_minor'`. **Matches.**
- **Hit 1 (13:31:51):** `test_a_model_call_equals_predict_glm_at_full_precision` is a single `decimal` -> `decimal` run, `pytest.approx(expected, rel=1e-14)` kept. **Matches.** Cost, disclosed: the `money_minor` leg of that equality no longer runs (ruled).
- **Hit 2 (13:40:06, A1 form):** `s_promo_money`, an `expression` step with `result_type: money_minor` over the `int` input, feeds `s_out_promo`; the input stays `int`. **Matches.**
- **Literal assert (14:12:05):** `if name == "type_mismatch": assert saved.json()["code"] == "RATING_TYPE_MISMATCH"`, after the report/save equality. **Matches.**
- **Fourth caller:** `_refuse_mount_port_type_mismatch` passes `at_output_step=False` (`compile.py:683` at this head; the brief's and PL-1627's `:702` is the pre-edit line). `git grep` of `_compatible(` finds its three callers only; `test_a_mount_port_refuses_a_closed_direction` (D1-D25 + D9) and the allowed set cover it. **Matches.**
- **Spec (RL-1564 Form A):** the FR-227 amendment equals RL-1564 `:227` byte for byte once `2026-10-05` is replaced by `2026-10-17` (checked by script, `True`). **Matches.** RL-1564 calls it FR-227's *first* dated amendment; it is the second (A-2's is first); the ledger discloses this.

**4. Gate at `3e8cc2f4`** (`scratch/sl1563-gate/`, gate-1b 16:13:04-17:18:13 BST; START tree `5ae23b6e` = this head's tree): ruff, mypy, import_linter, req_coverage, contracts rc 0; frontend lint, type-check, test, build rc 0; `audit_docs` rc 1 with one line, `check 31: gap in the full allocation between 1757 and 8083` (working-id artefact, clears at mint); pytest rc 1, `13 failed, 5987 passed, 6 skipped`, the 13 FAILED names all `test_audit_docs_*`, `test_doc_index`, `test_register_*`, `test_repository_invariants` (the docs-audit cascade). Accepted by the maintainer ("green apart from the cascade; only-new 0"). The auditor did not re-derive "only-new 0" by diffing the 13 names against a baseline.

**5. Findings.**
- **A1 (LOW, fixed here):** the ledger's `Owed` section ("Full two-half gate ... the auditor's re-check") was stale after the gate, and it records no gate rc, no item 12 (b)/(c), no item 5/6 tests and no FD 1767; sections 2 and 4 above carry them. The executor's body is not edited.
- **A2 (LOW, observation):** the branch is behind `origin/main` (`6bdd2571` vs `9469721d`); `docs/INDEX.md` will conflict and is regenerated at merge (common brief item 5); not tested here.
- **A3 (LOW, observation):** `_NUMERIC` is now used by no code in `compile.py`; it stays as the vocabulary `score.py:993` and `test_rating_score_batch_outputs.py:227` cite. No action.
- **A4 (disclosed):** item 11's difference is FD 1767, already registered; it is not this slice's to fix.

**6. Requirements without evidence:** none. PL-1562 items 1-12 are delivered and tested; FR-227's amendment is delivered. Owed: the mint of `LG-8083`/`SL-1563` (clears check 31 and the cascade), the lead's merge.

**7. Proposed verdict:** all obligations delivered and evidenced; no unevidenced requirement. Proposal only; the lead adopts, amends or rejects. Status left `active`. MERGE-ACK: not yet given.
