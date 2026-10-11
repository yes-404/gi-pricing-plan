---
id: FD-9808
family: finding
title: A formula that rating restates by hand in ZEN has no agreement check against the expression it came from, so a diverged copy misprices
status: active
created: 2026-10-11
owner: auditor
tree: 02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a
corrected_by: []
relates: [WK-1178, WK-690, RL-9934, OQ-9809]
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
- I have not measured how many Rating Versions on any deployment restate a formula; the platform has no live deployment
  (no live exposure is claimed or excluded by this record).

## Finding

If the two copies diverge (a changed constant, a different rounding, `%` against `mod`), the model is fed values it was not
trained on and every quote it prices is wrong, silently: there is no refusal and no signal. That is the "diverged shape is a
mispricing" failure `CLAUDE.md` §2 names for hand-written shapes, applied to a formula.

**Severity (proposed by the auditor): MEDIUM.** The reason: a silent mispricing path is HIGH by kind, but it needs a human to
write a copy that disagrees, the exposure is unmeasured, and the interim (S4 records the expression text in the Model's factor
record so a reviewer can compare) narrows the Slice 4 instance. The maintainer may raise it; I would not lower it.

## Remedy

The **design** of the check is OQ 9809 (options and a recommendation there); this finding decides none. Its resolution at the P2
close is either fixed, or carried to P3 with a named owner (`CLAUDE.md` §14).

## Disposition

**Owner: WK-1178** (P2's open maintenance Work). Decision: `fix before close with an owner: WK-1178`, or carry to P3 with a named
owner. Event that next confirms or discharges it: OQ 9809's decision, then the slice it names. Filed by the auditor, 2026-10-11;
the lead gives the verdict.
