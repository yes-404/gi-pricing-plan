---
id: FD-8046
family: finding
title: NFR-485 names QuantileDMatrix/streaming construction, but the code builds a dense xgb.DMatrix, a LightGBM Dataset that keeps its raw data, and a dense GLM design matrix, and which side is wrong is open
status: active
created: 2026-10-14
owner: auditor
tree: a3fc2e8dd384de6abf909f662f43011b8078fb4e
corrected_by: []
relates: [WK-1178, PL-1735, SL-1736, NFR-485, NFR-475, P2]
---

# FD-8046 — NFR-485's construction clause and the code's construction disagree

*(Filed under working id 8046, reserved by the lead; a minter folds it into the docs batch.
Authority: the maintainer's (by delegation) entry "2026-10-14 12:07:40 BST" in
`channel/to-lead.md`, DP-5, verbatim: *"an FD, measure as-is: NFR-485 names
`QuantileDMatrix`/streaming, but the code uses `xgb.DMatrix` (gbm.py:895), LightGBM
`free_raw_data=False` (gbm.py:1108) and a dense GLM (glm.py:578). Which side is wrong is the FD's
§0 question. The 5M reading answers whether the gap matters."* Plan context: PL 1735 at
`origin/pl-8034-wk1178-p2-nfr-sweep-2026-10-14` @14b6d79ad5cb. Every citation below was read at
`origin/main` `a3fc2e8dd384de6abf909f662f43011b8078fb4e`.)*

## Finding

**Severity: MEDIUM, proposed by the auditor (to be ruled). Owner WK-1178.**

`docs/specs/02-modelling.md:2952`, NFR-485 in full: *"Memory: fitting a 5 M × 60 dataset stays
within 32 GB, using `QuantileDMatrix`/streaming construction rather than duplicating the design
matrix."* The row has no dated amendment of its own. The requirement has two clauses: a budget
(32 GB at 5 M × 60) and a method (`QuantileDMatrix`/streaming, not a duplicated matrix). The code
meets the method clause on none of the three paths, at `a3fc2e8d`:

| Path | Where | What it builds |
|---|---|---|
| XGBoost | `packages/pricing-core/src/pricing_core/modelling/gbm.py:895` | `xgb.DMatrix(features, label=…, base_margin=…, weight=…, enable_categorical=True)` from an in-memory `np.ndarray`. |
| LightGBM | `gbm.py:1106-1108` (and `:1119`) | `lgb.Dataset(x, …, free_raw_data=False)`: the raw array is kept beside the binned dataset. |
| GLM | `packages/pricing-core/src/pricing_core/modelling/glm.py:578` | `x = design.to_numpy()`, a dense float64 design matrix passed to `glum`. |

`git grep -n "QuantileDMatrix\|DataIter" a3fc2e8d -- packages backend` returns no line in code.
Whether `free_raw_data=False` is needed (a later `predict` or a refit on the raw array) was not
checked here; it is the first thing the owner reads.

## Evidence

The code citations are in the table above; the question CLAUDE.md §0 puts to this finding follows.

Code and spec disagree. Which is wrong is the question; this finding does not decide it.

**Reading 1, the spec is right and the code is wrong.** The method clause is a requirement: at 5 M
× 60 a dense float64 design is 5e6 × ~180 columns × 8 B ≈ 7 GB, and a second copy (the `DMatrix`,
the `Dataset`'s kept raw array) multiplies it. The WK-661 measurement
(`02-modelling.md` ~3131-3158, "NFR-475 and NFR-485 measured 2026-08-22") projects the GLM's peak
RSS to 16.0 GB by power-law fit and 25.9 GB linearly, 81 % of the budget, and says *"Memory is the
clause that fails first, and the one nothing here can falsify"*. The GBM path was not measured at
5 M at all: NFR-476's memory fit `m = 0.417·n^0.645` stops at 75 000 rows and is projected to
8.7 GB. Under this reading the remedy is code: stream or quantise the construction.

**Reading 2, the code is right and the spec is wrong.** The same measurement note states the
GLM's dense design is *"precisely the path `QuantileDMatrix` does not apply to"* (`glum` takes a
matrix, not a `DMatrix`), so for one of three paths the method clause cannot be met as worded. The
clause also names a mechanism where the requirement's purpose is the budget; if the budget holds at
5 M on the dense paths, the mechanism is an implementation preference that the spec wrote as a
requirement. Under this reading the remedy is a dated amendment narrowing the clause to the budget
(and to the GBM paths, if the GLM is exempt), kept append-only.

**What distinguishes them is a measurement, not an argument**, and PL 1735 already schedules it:
DP-4 (b) in the 12:07:40 entry puts a 5 M run per arm on nfr-bench-1 session 2 under
`MemoryMax=30G`, and a cap-kill is an FD. A 5 M run that stays inside 32 GB makes the budget clause
met and moves the dispute to whether the method clause was ever a requirement in its own right
(Reading 2 gains, but the spec still says something the code does not do, so the amendment is
owed). A run that is cap-killed or exceeds 32 GB makes Reading 1 correct on the budget as well as
the method. The 250 k to 1 M curve on the shared VM is a diagnostic projection only, never a
verdict, and does not answer this.

### Why MEDIUM, proposed

- Against HIGH: no wrong number reaches a customer and no data is lost; the failure mode is an
  out-of-memory kill of a fit, which is loud. The budget clause is already scheduled for
  measurement (DP-4 (b)).
- Against LOW: a P2 NFR sweep that reports NFR-485 "met" from a 5 M run would be silent about the
  method clause, so the spec would still say what the code does not do, which is the state
  CLAUDE.md §0 forbids leaving unrecorded. And 81 % of budget on a linear projection
  leaves little room if the GBM path doubles memory.
- Re-rate trigger: HIGH if the 5 M run is cap-killed or exceeds 32 GB on either arm.

## Disposition

The event that next discharges it: the SL 1736 5 M reading on nfr-bench-1 session 2, then a
maintainer ruling on Reading 1 or 2, then either the construction fix or a dated NFR-485
amendment, whichever is ruled.
