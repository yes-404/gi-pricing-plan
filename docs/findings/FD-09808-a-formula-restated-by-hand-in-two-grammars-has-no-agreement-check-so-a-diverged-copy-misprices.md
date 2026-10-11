---
id: FD-9808
family: finding
title: A formula that rating restates by hand in ZEN has no agreement check against the expression it came from, so a diverged copy misprices
status: active
created: 2026-10-11
owner: auditor
tree: 02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a
corrected_by: []
relates: [WK-1178, WK-690, OQ-9809]
---

# FD-9808 — formula parity: two hand-kept copies of one formula, no check

**Working id 9808, to be minted in the D11 batch.** Filed at the lead's entry "2026-10-11 11:25:51 BST — DP-S4-1 RULED (a2);
DP-S4-2 ADOPTED (both points); need 4.5 = an FD AND an OQ, not an OQ alone", item 3(a), and recorded by RL 9934
("Need 4.5 — formula parity, routed three ways"). The design question is OQ 9809, the interim is item 3(c).

## Evidence

- A model's feature can be an expression evaluated over data in the `02` §4.6 grammar: a preparation `derive_expression` column
  (the `recipe` profile, `01` FR-36; `02` §4.6 :941) or, under WK-690 Slice 4, an `expression` Factor (the `factor` profile).
- A Rating Version scores a model through `model_call`, whose required inputs are the model's feature slugs
  (`required_model_inputs`, FR-240). Rating is not a §4.6 profile (RL-1265 DP-5); its `expression` steps use FR-244's grammar.
  So the rating graph must **write the same formula again** in ZEN to produce the feature's value at quote time.
- Nothing compares the two. The training-side copy (a Recipe step or a Factor's `expression`) and the rating-side copy (an
  `expression` step) are separate strings in two grammars; the compile checks the names a step reads (FR-246, FD-1374) and the
  model's input coverage (SL-1541), not that the formula produces the training-side values.
- **The instance that exists on main:** a `derive_expression` column feeding a Model that a Rating Version scores (`prepare.py:165`
  evaluates it for training; the rating graph restates it). **The instance WK-690 Slice 4 would add:** an `expression` Factor
  (dm-wk690's memo, `handover/dm-wk690-dps4-1-2026-10-11.md` §4, which says the `derive_expression` path "ALREADY exists").
- Exposure is measured below (section "Exposure, measured"); the result is zero committed or stored instances.

## Finding

If the two copies diverge (a changed constant, a different rounding, `%` against `mod`), the model is fed values it was not
trained on and every quote it prices is wrong, silently: there is no refusal and no signal. That is the "diverged shape is a
mispricing" failure `CLAUDE.md` §2 names for hand-written shapes, applied to a formula.

**Severity (proposed by the auditor): MEDIUM, conditional on the exposure measurement below, which found 0 committed and 0 stored instances.** The reason: a silent mispricing path is HIGH by kind, but it needs a human to write a copy that disagrees, no instance exists at the measured tree, and the interim (S4 records the expression text in the Model's factor record so a reviewer can compare) narrows the Slice 4 instance. Any instance found later moves it to HIGH (the lead's rule, "2026-10-11 11:5x BST" ruling on FD 9808); the path in measurement (3) is open today, so the severity does not fall below MEDIUM.

## Exposure, measured

Measured 2026-10-11 by the auditor, read-only, one command at a time under `nice -n 19` beside the held gate-1. Tree: `origin/main` `02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a` for (1) and (3); the dev database of the local stack (`gi-pricing-postgres-1`, Up 2 hours, healthy) for (2). `P="docker exec gi-pricing-postgres-1 psql -U gipricing -d gipricing -At"` below.

**(1) Committed instances: 0.** Predicate: a file in `examples/` or a test fixture that both defines a rating path and restates a `derive_expression` formula.
- `git -C <wt> grep -l "derive_expression" origin/main -- examples ':(glob)**/fixtures/**' ':(glob)**/tests/**'` returns 3 files, all data-preparation tests (`packages/pricing-core/tests/test_expression_nfrs.py`, `test_expression_profiles.py`, `test_prepare.py`). None defines a Rating Algorithm.
- `git -C <wt> grep -n -i "derive" origin/main -- examples` returns 8 lines, all English "derive", `dataset.derive` or `derived_from`; the narrower `git -C <wt> grep -n -i "derive_expression" origin/main -- examples` returns 0.
- Rating definitions in `examples/`: `git -C <wt> grep -l -E '"steps"|RatingAlgorithm|"sub_graphs"' origin/main -- examples` returns 4 files (`examples/fremtpl2/model.py` and three `examples/fremtpl2/rating/fremtpl2-rate.*.json`). Their `expression` steps (read with `json.load`, v1 and v2) are the rating arithmetic (`s_freq` = a constant times the relativities, `s_risk`, `s_load`, `s_cap`, `s_adj`, `s_pay`), not a restated feature formula. `git -C <wt> grep -c '"model_call"' origin/main -- examples` prints nothing, so 0 files carry a `model_call`.

**(2) Stored instances: 0.**
- `$P -c "select body->>'type', count(*) from factors group by 1"` returns `identity|18`: all 18 stored Factors are identity; `select count(*) from factors where body ? 'expression' and body->>'expression' is not null` returns 0.
- A loop over every base table of schema `public` running `select count(*) from "<t>" x where x::text like '%derive_expression%'` found 0 rows in every table (dataset versions and jobs included), so no stored Preparation Recipe contains a `derive_expression` step.
- `select count(*) from rating_algorithms where content::text like '%derive%'` returns 0, and `select count(*) from rating_versions where bundle::text like '%derive%' or pins::text like '%derive%'` returns 0. The one stored algorithm (`demo-fixture-motor` v1) has 3 steps and 0 `model_call` steps; `sub_graph_versions` has 0 rows.

**(3) The code path through which a `derive_expression` column reaches rating** (open today):
`pricing_core/data/prepare.py:165` (`case "derive_expression"`) evaluates the formula into a Dataset Version column; a Factor reads that column (`pricing_core/modelling/factors.py`, `identity` today, `expression` under WK-690 S4); `required_model_inputs` (`factors.py:338`) returns the feature slugs the Model needs; `pricing_core/rating/compile.py:938-968` requires a `model_call`'s `feature_map` to cover them (SL-1541); the Rating Version's graph must then produce each slug's value, and for a derived feature the only way is an `expression` step that writes the formula again (FR-244). Nothing on this path reads the Recipe's text.

Conclusion at this tree: the path exists and is exercised by no committed or stored definition. A later instance, found by this predicate, makes the finding HIGH.

## Remedy

The **design** of the check is OQ 9809 (options and a recommendation there); this finding decides none. Its resolution at the P2
close is either fixed, or carried to P3 with a named owner (`CLAUDE.md` §14).

## Disposition

**Owner: WK-1178** (P2's open maintenance Work). Decision: `fix before close with an owner: WK-1178`, or carry to P3 with a named
owner. Event that next confirms or discharges it: OQ 9809's decision, then the slice it names. Filed by the auditor, 2026-10-11;
the lead gives the verdict.
