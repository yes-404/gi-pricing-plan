---
id: FD-8408
family: finding
title: NFR-476's expression limb is over: a custom expression objective costs 1.50 times the builtin against 1.25
status: active
created: 2026-11-07   # working id 8408, to be minted in the PR of docs batch 15
owner: lead
tree: a995b876dd07bbc8e6b5d8712fd085178ba77e91   # the tree the measurement ran at (head 6f958137b227)
corrected_by: []
relates: [WK-690, WK-1178, LG-1839, LG-2003, CR-8314, NFR-476]
---

# FD-8408 — NFR-476's expression limb is over: a custom expression objective costs 1.50 times the builtin against 1.25

*(Working id FD 8408, MEDIUM, owner WK-690. Ruled in to-lead "2026-11-07 19:37:24 GMT" (M), whose id was corrected in "2026-11-07 19:38:16 GMT". CR 8314 reads this finding. It is minted in docs batch 15 at the step before the PR.)*

## Finding

NFR-476 says a custom `expression` objective adds no more than 25 % overhead versus the equivalent builtin (`docs/specs/02-modelling.md`, NFR-476). S2 of nfr-bench-1 measured the expression limb at a median expression-to-builtin ratio of **1.502** against the limit of **1.25**. The limb is over. The harness claims no verdict only within 5 points of the bound; this reading is far outside that zone.

The reading is from an AMD EPYC 7B12, 8 vCPU; not like-for-like with S1; a lower bound on a non-spec host. A ratio is less host-bound than a wall time, but no claim is made that it would hold on 16 cores.

## Evidence

LG-1839 @2a8adfa0 (the addendum "Addendum 2026-11-07 — nfr-bench-1 session 2: item M"), quoted: "**Verdict: NFR-476 expression limb UNMET on this host — median expression / builtin ratio 1.502 over 3 pairs, spread [1.501, 1.529], against ≤ 1.25 (`EXPRESSION_OVERHEAD_LIMIT`, `scripts/bench-model.py`) → FD owed (owner WK-690, per the plan's row A).**"

| pair | builtin | expression | ratio |
|---|---|---|---|
| 1 | 119.06 s | 178.70 s | 1.501 |
| 2 | 119.10 s | 178.88 s | 1.502 |
| 3 | 117.15 s | 179.15 s | 1.529 |

Command: `uv run --directory <wt> python -u scripts/bench-model.py --only expression --rows 5000000 --factors 60 --rounds 500 --pairs 3`, run alone at head `6f958137b227` (tree `a995b876dd07`), 934 s wall. The three pairs agree within 0.03. The pairs ran in one process, which is the harness's design (`bench_expression_limb`).

Not read: the rows fitted were not separately read from the log, and the cause of the 50 % overhead is not investigated here. Nothing in this finding says the expression objective computes a wrong value.

## Disposition

MEDIUM, owner WK-690 (to-lead "2026-11-07 19:37:24 GMT" (M), id as corrected at "2026-11-07 19:38:16 GMT"). CR 8314 reads it. The remedy-or-budget decision is not made here: either the expression path is made cheaper or NFR-476's 25 % is re-decided, and the second is the maintainer's.
