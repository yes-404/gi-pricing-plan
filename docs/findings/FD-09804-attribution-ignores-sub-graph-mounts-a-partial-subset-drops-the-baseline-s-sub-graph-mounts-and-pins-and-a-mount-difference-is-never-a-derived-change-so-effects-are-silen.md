---
id: FD-9804
family: finding
title: Attribution ignores sub-graph mounts: a partial subset drops the baseline's sub-graph mounts and pins, and a mount difference is never a derived change, so effects are silently misattributed
status: active
created: 2026-10-12
owner: auditor
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
corrected_by: []
relates: [WK-673, SL-1387, SL-1527, PL-1267, FR-266, FR-1399, RL-1449]
---

# FD-9804 — the attribution engine does not see sub-graph mounts

Found by SL-1527 (its ledger, id reserved and unmerged) at WF-699 D7, widened by the planner of the `WK-673` fix slice's code read, and re-rated by the maintainer (by delegation). Filed from the entries "2026-10-12 02:29:16 BST — SL-1527 D7: (A) ACCEPTED; FD owner WK-673 (not WK-1178), MEDIUM; (C) gets its OWN WK-673 slice before G2", "2026-10-12 02:34:38 BST — FD 9804 widened to 3 limbs: ACCEPTED, MEDIUM PROVISIONAL with a named re-rate trigger", "2026-10-12 02:35:40 BST — FD 9804 RE-RATED HIGH now (code read), confirmed or reverted by R3" and "2026-10-12 02:43:49 BST — DP-G: exemption (i) REFUSED" (`to-lead.md`, local, cited by header). Every `file:line` below was re-read at `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9` on 2026-10-12. The code is SL-1387's (WK-673 Slice 3). File: `packages/pricing-core/src/pricing_core/rating/analysis.py`.

## Evidence

1. **A subset keeps the baseline's mounts.** `_subset_algorithm` (`:742`) returns the baseline with each member's step, `input_contract` and `outputs` differences applied; `git grep -c sub_graph` over `analysis.py` prints 0. A partial subset therefore carries the **baseline's** `sub_graphs`, never the candidate's. A candidate that mounts or changes a sub-graph cannot compile in any partial subset at two or more groups.
2. **A subset drops the baseline's sub-graph pins.** `_subset_pins` (`:768-799`) builds its pins over `_PIN_KINDS` (`:484-489`: `rate_tables`, `models`, `reference_tables`, `custom_objectives`), which has no `sub_graphs`. A baseline that already mounts a sub-graph fails to compile at two or more groups even when no change touches it. The planner predicts `RATING_VERSION_UNPINNED` wrapped as `BUNDLE_COMPILE_FAILED`; PL 9807 Task 1 proves the exact outcome by test.
3. **A mount difference is not a derived change.** `_derive` (`:559-674`) never reads `diff.sub_graph_mounts` (the field is `model_schema/rating.py:860`; `git grep -n sub_graph_mounts -- packages/pricing-core backend/src` prints no hit under `pricing_core/rating/analysis.py`). So a re-point of a mount (`@4` to `@5`) plus one rate-table edit yields one derived change, the edit, and the report attributes the **total**, the ladder effect included, to a group whose only member is the edit. A mount-only change attributes 0 against a non-zero dislocation. Both are **silent**.

## Finding

**Severity HIGH (re-rated by the maintainer (by delegation), entry "2026-10-12 02:35:40 BST").** The first rating, MEDIUM PROVISIONAL (entry 02:34:38), held only if every limb failed loudly (`BUNDLE_COMPILE_FAILED`, never a misprice). Limb 3 does not: attribution is approval evidence (WF-699 E-steps), and a report that silently assigns a sub-graph's effect to an unrelated rate-table edit, or reports 0 against a non-zero dislocation, misleads the approver about why prices moved. It is user-reachable: any rating-version change that mounts or changes a sub-graph, not only the demo.

**Re-rate trigger (the 02:34:38 entry, kept).** If **any** partial subset compiles against a sub-graph version other than the baseline's pin (a silent compile through latest, default or cache), attribution returns wrong numbers with no error: that is HIGH and the maintainer is told at once. **R3** (PL 9807, a red-first test of limb 3 on `main`) confirms the code-read rating: if R3 is GREEN on `main` the work **stops** and the rating reverts to MEDIUM by a dated line.

## Disposition

**Owner: WK-673; the fix slice is `SL 9850` (working id) under `PL 9807` (working id), a dated delta to PL-1267.** Order (entries 02:35:40 and 02:43:49, DP-G, the latter superseding the former's "K at least 2" clause):

- **First, a loud guard.** In `attribute`, after `_check_groups`: refuse **any** attribution when the derived diff carries any `sub_graph_mounts` difference (add, remove, re-point, re-map), at **any** K including 0 and 1; and also refuse when either side mounts a sub-graph and K is two or more. Code `VALIDATION_FAILED` (FR-1399's refusal, no new code); the message names "sub-graph mount differences are not yet attributable" and FD-9804. `derive_changes`, the estimate and D6's dislocation are untouched. Exemption (i) ("one group holding every derived change") is refused: a group is reported by its members, so it mislabels the ladder effect.
- **Then the fix** (limbs 1 to 3: carry the mounts and their pins in a subset; a mount difference becomes a derived change), restoring WF-699 D7's two-group split from the salvage branch `salv-sl1527-d7-2group`.
- **G2 gains this slice** (a dated line under `docs/roadmap.md` G2). SL-1527 merges first with one group and prints "SKIPPED D7 decomposition — FD 9804".

Per `CLAUDE.md` §14 it is HIGH in P2 and needs a resolution before any P3 start. Event that next confirms or discharges it: `SL 9850`'s merge with R1 to R3 red on `fc4401dc` by their causes and green after. Filed by the executor from the entries, 2026-10-12.
