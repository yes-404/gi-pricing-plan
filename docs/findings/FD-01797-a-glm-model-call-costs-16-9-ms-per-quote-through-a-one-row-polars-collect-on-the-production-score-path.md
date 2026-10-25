---
id: FD-1797
family: finding
title: A GLM model_call costs 16.9 ms per quote through a one-row polars collect on the production score path
status: closed
created: 2026-10-18   # filed 2026-10-17 under working id 8097; minted 2026-10-18 as FD-1797
owner: auditor
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
corrected_by: []
relates: [WK-1178, SL-1543, PL-1772, SL-1773, LG-1774, NFR-489]
---

# FD-1797 — A GLM model_call costs 16.9 ms per quote through a one-row polars collect on the production score path

## Finding

**HIGH; owner WK-1178; disposition: fix owned by its own slice (PL 8098 / SL 8099).** The
maintainer, about 20:48 BST on 2026-10-17: "SL-1543 diagnosis ACCEPTED: 1. An FD HIGH
(WK-1178): a model_call to a GLM costs ~16.9 ms/quote via a one-row polars collect (8.6×). It
is on the production /score + batch path, NFR-489-relevant, and blocks G2. Into D21 with the
profiles."

**Consequence.** Any algorithm whose decision graph has a `model_call` to a GLM pays a
one-row polars frame build plus a lazy `collect` for every quote, for every peril component.
That is the real-time `/score` path and the batch path. It is the cause of the SL-1543 solo
gate stall: the dislocation run over 20,000 policies did not finish within the 900 s profiling
cap. It blocks G2 (SL-1543's gate). NFR-489 (`docs/specs/03-rating-engine.md:1511`) sets
real-time p99 < 50 ms with one GBM call and < 15 ms without; a GLM `model_call` is not a
GBM call, and 16.9 ms/quote of mean sampled cost exceeds the 15 ms no-GBM ceiling before any
queueing (the figure is a mean under a py-spy sampler that itself costs about 1.8x, so
read the 8.6x ratio, not the milliseconds, as the evidence).

## Evidence

All profiles and logs are in `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1543d/`
(`main.raw`, `slice.raw` py-spy raw output; `main.demo.log`, `slice.demo.log`; `window.log`,
`window.sh`, `top.py`) and the executor's write-up
`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1543-diag2.md`. Same driver both sides:
`scripts/demo.py --journey wf-699`, one `dislocation.run` Job profiled with `py-spy record
--rate 100`. Main = `origin/main` 9469721d; slice = SL-1543 @4c948c8a.

- Main Job: 232.3 s (py-spy inflated; 126 s unsampled), 61.8% self in the native ZEN call
  (`_score_context_sync`, `score.py:1144`).
- Slice Job: still `running` at the 900 s cap, progress `attributing` 0.5. A new 59% sits
  under ZEN's `model_call` node; the single top leaf is polars `LazyFrame.collect`
  (`lazyframe/engine.py:443`), 43.6% self (40,800 of 93,685 samples); `resolve_factors`
  inclusive 45.9%.
- Per quote, baseline pass: 33,788 samples / 19,985 quotes = 16.9 ms vs main 3,935 = 2.0 ms
  (8.6x). Candidate pass 6.2x.
- Portfolio is identical both sides: 20,000 rows, 19,985 validated.
- `runtime.py`, `predict.py` and `factors.py` are byte-identical between slice and main, so the
  slice adds no engine cost; its demo algorithm (7fdb8089, wired by de027a55) exercises the
  existing `model_call` path at scale for the first time.

Code path at `origin/main` 9469721d, `packages/pricing-core/src/pricing_core/` (read by the
author; `git grep -n` at that commit):

1. `rating/analysis.py:221-222` `_score_pass` (`:173`) for baseline and candidate, from
   `dislocation_frame` (`:206`);
2. `rating/score.py:1143` `bundle.decision.evaluate` runs the graph;
3. `rating/runtime.py:745` `handler`, `:766` `_predict_model(` — and `:672` from
   `_score_peril_structure` (`:646`);
4. `rating/runtime.py:628` `glm_scorers[ref_str].predict(feature_row)`, the method at `:822`;
5. `modelling/predict.py:230` `predict_glm` → `:198` `linear_predictor` → `:219`
   `_term_vectors` (`:90`) → `:109` `resolve_factors`;
6. `modelling/factors.py:114` `resolve_factors`, `:243` `frame.with_columns(...)`, collected.

Line numbers in the executor's profile (`runtime.py:762`, `factors.py:243`) are from the slice
tree; the files are byte-identical, and the numbers above are re-read on main.

## Remedy (ruled)

The maintainer ruled **(A)** as its own small slice (PL 8098 / SL 8099, not a widening of
SL-1543): a scalar one-row predict path, with a **bit-identical** test against the polars path
over the goldens and seed quotes (exact equality), plus a diagnostic per-quote timing.
**(C)** (single-thread polars) may be run as data only. **(B)** (batch the model_call), **(D)**
(shrink the demo workload) and **(E)** (raise the demo cap) are refused. SL-1543 keeps B4,
waits for the fix to merge, then re-merges and re-gates solo. The separate
`test_wf699 -k end_to_end` golden mismatch has its own granted DB-lane run; its cause is named
separately and is not claimed here.

## Disposition

Fix owned by its own slice (PL 8098 / SL 8099). Discharged when SL 8099 merges with the
bit-identical test and a per-quote timing at or below main's ~2 ms. Filed under working id 8097.

Fixed by #1327 / 3999e0e2dc217def6d0e1e1a82dee2c37afad1f9 (PL-1772 / SL-1773 / LG-1774; the slice cites this
finding as "FD-1797 (filed in D21)"; the maintainer, `to-lead.md` "2026-10-17 21:35:45 BST": the link is
made from this side, the slice's frozen bodies are not re-pointed).
