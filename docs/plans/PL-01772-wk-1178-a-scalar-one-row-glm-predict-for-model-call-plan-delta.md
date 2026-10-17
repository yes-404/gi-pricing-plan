---
id: PL-1772
family: plan
kind: map
title: WK-1178 — a scalar one-row GLM predict for model_call, bit-identical to the polars path (SL-1773) — a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a) — activated 2026-10-17 on the maintainer's "plan + GO now" (2026-10-17 20:48:15 BST); no decision point is open
created: 2026-10-17
owner: planner
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-1773, SL-1543, SL-1274, SL-1341, SL-1547, SL-1258, SL-1740, FR-11, FR-188, FR-193, FR-222, NFR-489]
---

# PL-1772 — WK-1178: a scalar one-row GLM predict for `model_call`, bit-identical to the polars path (SL-1773)

Minted 2026-10-17 from working id 8098 on the maintainer's re-allocation (to-lead 2026-10-17 21:30:18 BST).

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L5 (`document-ids.md`
> §1.6, PL row). It carries one fix slice, SL-1773 (roadmap row under WK-1178). The executor
> is spawned from `.claude/roles/executor.md` and binds `test-driven-development`,
> `python-test`, `python-package`, `dev-commands` and `git-hygiene`. Its ledger is
> **LG-1774**, filed by the executor at build; this plan names it and does not create it.

Written 2026-10-17 20:51 BST by the planner (planner-fix) on the lead's brief
`brief-planner-fix-2026-10-17.md`. Evidence read at `origin/main` `9469721d`. Working ids
PL-1772, SL-1773, LG-1774 are the lead's (`from-lead-2026-10-09.md:5201`).

## The ruling this plan carries out

The maintainer, 2026-10-17 20:48:15 BST, verbatim (relayed in the brief; the lead's channel
line `from-lead-2026-10-09.md:5201` records the same routing):

> "SL-1543 diagnosis ACCEPTED: 1. An FD HIGH (WK-1178): a model_call to a GLM costs ~16.9
> ms/quote via a one-row polars collect (8.6×). It is on the production /score + batch path,
> NFR-489-relevant, and blocks G2. Into D21 with the profiles. 2. FIX = (A) as its OWN small
> slice (plan + GO now; gate on a free slot after the proof pair), not a widening of SL-1543.
> A scalar one-row predict path with a BIT-IDENTICAL test vs polars over the goldens + seed
> quotes (exact equality), plus a diagnostic per-quote timing. (C) may be run as data. (B),
> (D), (E) refused. 3. SL-1543 keeps B4, waits for the fix to merge, then re-merges and
> re-gates SOLO. 4. GRANTED: one DB-lane run of test_wf699 -k end_to_end printing the
> failing goldens (own redis/bucket); its cause is named separately."

The finding is **FD 8097** (HIGH, WK-1178), drafted in D21. The evidence is the SL-1543
diagnosis (`gi-pricing-plan.local/scratch/sl1543-diag2.md`, answer 5): on SL-1543
@`4c948c8a`, 59% of the `dislocation.run` samples sit under `model_call` →
`runtime.py` `_score_peril_structure` (:672 on `9469721d`) → `_predict_model` →
`_GlmScorer.predict` (:822) → `predict_glm` (`modelling/predict.py:230`) →
`linear_predictor` (:198) → `_term_vectors` (:90) → `resolve_factors`
(`modelling/factors.py:114`; the sampled line is :243, `frame.with_columns(...)`) → polars
`LazyFrame.collect`, 43.6% self. 16.9 ms/quote sampled vs main's 2.0 ms (8.6×). The engine
files are byte-identical between SL-1543 and main: the cost is the engine's, exposed by the
first demo algorithm that calls a GLM per quote.

## Goal

`_GlmScorer.predict` (one quote, one GLM) scores without building a polars frame or running
a lazy `collect`. The frame path (`predict_glm`, `linear_predictor`) stays for every batch
caller (backtest, diagnostics, comparison). The result is **bit-identical**: the same
`float` for every input, so `_decimal(repr(value))` and every Decimal premium the rating
path composes (`CLAUDE.md` §7; FR-188) are unchanged, and FR-11 (scoring reproduces
identical outputs) is kept by proof, not argument.

**Not in scope, refused by the ruling:** (B) batching `model_call` across quotes; (D)
shrinking the demo portfolio or journey; (E) raising the gate demo cap. **(C)** —
`POLARS_MAX_THREADS=1` — may be run once as a measurement and recorded in LG-1774 as data;
it is not a fix and ships no config change.

**No spec change.** FR-193, FR-222 and NFR-489 already state what is required; this changes
how `pricing-core` meets them. If the executor finds a case the scalar path cannot make
bit-identical, that is a STOP and a report, not a tolerance (the ruling says exact).

## Design constraints (each is a review item)

1. **One design, two evaluators.** `_term_vectors`' docstring requires that no two callers
   build different design matrices from one model. The scalar path iterates
   `fit.coefficients` in the same order, parses terms with the same `_DUMMY` pattern, and
   raises the same `PredictionError` codes (`MODEL_TERM_UNRESOLVED`, `MODEL_OFFSET_MISSING`,
   `MODEL_LINK_UNSUPPORTED`, `MODEL_CALL_FEATURE_COLLISION`) for the same inputs.
2. **One source per mapping.** Banding and grouping levels come from the existing
   `apply_banding` (`bandings.py:419`) and `apply_grouping` (`groupings.py:525`) or from a
   scalar core extracted from them that both paths then call. A second implementation of a
   banding or grouping rule is refused: it is the diverged shape `CLAUDE.md` §2 forbids.
   Level text must equal what `cast(pl.String)` gives on the frame path.
3. **Same IEEE operations, same order.** `η` starts at `0.0` and adds
   `estimate * value` per coefficient in coefficient order, then the offset — as
   `linear_predictor` does. The inverse link is `_inverse_link` itself, applied to a
   shape-(1,) `float64` array (never `math.exp`, whose last bit can differ from numpy's).
   The log-exposure offset uses `np.log`, as `_offset` does.
4. **The offset-from-model source** (`_GlmScorer.offset_source`) goes through the same
   scalar path; otherwise its `linear_predictor(frame)` keeps the collect.
5. **Supported factor kinds are stated, and an unsupported kind is decided at bundle load.**
   On `9469721d` the kinds are `identity`, `banding`, `grouping`, `interaction`. A scorer
   whose factors include a kind the scalar path does not cover keeps the frame path, chosen
   once in `_load_glm_scorers`, never per quote, and a test names that choice. (SL-1274 adds
   `expression` factors — see the census.) **Replaced by the Delta 2026-10-17 below; the
   text above is kept as the record of what was planned.**
6. **Return type unchanged:** `float`, read by `_decimal` at `runtime.py`. No Decimal or
   rounding change.

## Delta 2026-10-17 — no load-time fallback; the apply_grouping widening

A pre-merge dated delta, written 2026-10-17 21:34 BST on branch
`pl-8098-glm-scalar-predict-2026-10-17` at `a4ca8b00`. The plan is unmerged, so this edit is
allowed. Authority: the maintainer's entry "2026-10-17 21:26:31 BST — Maintainer: SL-1773
@a7977a49 — both departures ACCEPTED with conditions; the parity limb must be shown RUN" in
`to-lead.md`, conditions (1) and (2), and its refinement "2026-10-17 21:26:53 BST —
Maintainer: SL-1773 refinement: the old apply_grouping behaviour pinned as FIXTURE
expectations (not a copied module)".

1. **Constraint 5 is replaced.** Old: "an unsupported factor kind keeps the frame path,
   chosen at bundle load". New: **the scalar path reads the frame path's own resolution
   (`resolve_factor_columns`), so every factor kind is covered or refused identically on
   both paths.** There is no load-time choice in `_load_glm_scorers`. Task 3's "the
   load-time choice for unsupported kinds" and the census row's "load-time frame-path list
   (constraint 5)" fall away with it. The constraint is held by two tests in
   `packages/pricing-core/tests/test_glm_scalar_predict.py` at `a4ca8b00`:
   - `test_every_factor_kind_scores_bit_identically` — the covered kinds (`identity`,
     `banding`, `grouping`, `interaction`) score bit-identically;
   - `test_a_factor_kind_the_resolver_refuses_is_refused_identically_on_both_paths` — the
     all-kinds refusal test, parametrised over `spline`, `polynomial`, `offset`,
     `expression`: the same `FactorResolutionError` text on both paths.
2. **The apply_grouping widening is accepted scope** (condition (1) of 21:26:31). The
   single-value branch in `apply_grouping` (`packages/pricing-core/src/pricing_core/modelling/groupings.py`)
   is shared with the batch path. The old behaviour is pinned as fixture expectations (inputs
   → outputs and refusal texts captured from `c62f1ff6`), not a copied module (21:26:53):
   test `test_apply_grouping_reproduces_every_recorded_expectation_of_c62f1ff6` in
   `packages/pricing-core/tests/test_glm_scalar_predict.py`, data file
   `packages/pricing-core/tests/data/apply_grouping_c62f1ff6.json`. The other conditions of
   21:26:31 (1) stand as written there: the `test_groupings*.py` single-file runs at the
   head, the full gate as the batch-path proof, and one LG line naming the widening and the
   stamp.
3. **SL-1274.** Whichever of SL-1773 and SL-1274 merges second adds **expression-kind parity
   CASES** to the scalar-path tests (bit-identical scores for `expression` factors, as for
   the covered kinds). It does not add a frame-path list: none exists after this delta.

## Decision points

None open. The ruling decided the option ((A); (C) as data; (B), (D), (E) refused), the
proof (exact equality over the goldens and seed quotes) and the sequencing. Where the
scalar path lives and how it shares the design are the constraints above, not choices left
open. A case that cannot be made bit-identical is a STOP for the decision-maker, not a
decision point the executor rules.

## Acceptance Standard

1. **Red first (iii).** The first commit adds the parity test and a scalar entry point that
   raises `NotImplementedError`; run through `run-small.sh`, it is red. LG-1774 records that
   run's rc and FAILED line, the commit sha and the tree.
2. **Bit-identical (i).** One test asserts `scalar == frame` (Python `==` on the `float`, no
   `approx`, no tolerance) for every predicted value over:
   (a) the demo goldens — `examples/fremtpl2/model.py` `demo_golden_cases` (:518), for the
   frequency and the severity GLM;
   (b) the seed quotes — the seed's validated dislocation portfolio rows
   (`examples/fremtpl2/seed.py` `PORTFOLIO_VALIDATED_ROWS`, :93), every row;
   (c) one synthetic case per supported factor kind, per link (`log`, `identity`, `logit`,
   `inverse`), and per offset kind (`none`, `column`, `log_column`, `model`).
   It also asserts the same `PredictionError` code on both paths for: an unresolved term,
   a missing offset column, a non-positive exposure under `log_column`, and a feature
   collision. If (a) or (b) cannot be built without a database, the executor STOPS and
   reports: the DB lane is the lead's to grant.
3. **Diagnostic timing (ii).** A test or a script under the slice prints ms/quote for both
   paths over the seed quotes, with the tree sha and `nproc`. It asserts nothing about time.
   Its output goes into LG-1774 verbatim. (C), if run, is a third printed column.
4. **The wiring.** `_GlmScorer.predict` calls the scalar path; a test proves a
   `model_call` to a GLM no longer calls `resolve_factors` (patched to raise) while the
   frame path still does.
5. **Small runs** only through `gi-pricing-plan.local/handover/run-small.sh`, ≤3 files: the
   new parity test file, `packages/pricing-core/tests/test_rating_peril_scoring.py`, and
   `packages/pricing-core/tests/test_quote_input_raise_sites.py` (common brief item 11,
   which binds when a slice adds or changes a quote-input raise site; the scalar path's
   `PredictionError` raises are checked against that file's census).
6. **Census (iv)** re-run at the build's base against the branches in the table below; any
   new overlap is reported before the gate.
7. **Gate (v).** One full gate on a free slot after the proof pair, on an isolated
   template, when the lead grants it. Both halves rc 0. `python3 scripts/audit-docs.py`
   rc 0 apart from id-state reds the lead classes.

## Shared-path census (iv) — at `origin/main` `9469721d`, 2026-10-17 20:50 BST

Predicate, verbatim: `git -C /home/puzhenhao1989/gi-pricing-plan diff --stat origin/main...<branch> --
packages/pricing-core/src/pricing_core/rating packages/pricing-core/src/pricing_core/modelling/predict.py
packages/pricing-core/src/pricing_core/modelling/factors.py packages/pricing-core/src/pricing_core/modelling/bandings.py
packages/pricing-core/src/pricing_core/modelling/groupings.py packages/pricing-core/tests`, each branch read at
its local ref (local = origin for every branch below).

| Slice | Branch @ head | Overlap with this slice's files | What it means |
|---|---|---|---|
| SL-1543 | `sl-1543-fix-2026-10-17` @`4c948c8a` | `rating/score.py`, `compile.py`, `properties.py`; no change to `runtime.py`, `predict.py`, `factors.py` | No textual overlap. SL-1543 waits for this merge, re-merges main and re-gates SOLO (ruling item 3); its B4 goldens then run on the scalar path. |
| SL-1274 | `sl-1274-wk690-s4-factor-expression` @`bba2e0ae` | **`runtime.py` `_GlmScorer` (:799, :818 hunks)**, **`factors.py` (`resolve_factors` :190; +108 lines after `_grouping`)**, **`bandings.py`** | **The real overlap.** It adds the `expression` factor kind and the collision check (the check is already on main). Whichever merges second resolves `_GlmScorer.predict` and adds `expression` either to the scalar path (with parity cases) or to the load-time frame-path list (constraint 5), with a test. |
| SL-1341 | `sl-1341-wk1250-s3-purpose-mount` @`f269c5ca` | `runtime.py`: `_model_call_handler` :738, `_load_glm_scorers` :903–907, `_load_boosters`, `load_bundle` | Adjacent: `_load_glm_scorers` is where constraint 5's choice is made. A merge resolution there; no semantic conflict found. |
| SL-1547 | `sl-1547-wk675-s5` @`4c45b8f2` | `rating/properties.py`, `replay.py`, `testing.py` | None. |
| SL-1258 | `sl-1258-wk674-s4` @`776e4f99` | none in these paths | None. |
| SL-1740 | no branch (`git ls-remote --heads origin` and local refs: no match for `1740`); roadmap row `draft` | — | Nothing to census yet. |

## Tasks

1. **Red first.** Add the parity test (Acceptance 2) and a scalar entry point beside
   `linear_predictor` in `modelling/predict.py` that raises `NotImplementedError`. Run it
   (Acceptance 5): red. Commit. Record in LG-1774.
2. **The scalar path.** Implement it under the design constraints. Run the parity test
   until it is green with exact equality. Commit.
3. **The wiring.** `_GlmScorer.predict` and its `offset_source` use it; the load-time
   choice for unsupported kinds; the wiring test (Acceptance 4). Commit.
4. **Timing.** The diagnostic (Acceptance 3); (C) once if wanted, as data. Commit.
5. **Census and gate.** Re-run the census at the base; report; the gate when granted.
   Close the LG-1774 entry.

## Sequencing

SL-1773 goes first. After it merges, SL-1543 re-merges main and re-gates SOLO with B4 kept
(ruling item 3). The ruling's item 4 (one DB-lane run of `test_wf699 -k end_to_end`,
printing the failing goldens) is separate and is not part of this slice.

## Self-review before freeze

- Every acceptance item is a command or a recorded run; none is a time assert.
- Refused options are named and not planned. (C) is data only.
- No number range in scope; every id listed singly.
- Return type and Decimal composition are unchanged (constraint 6); no spec text changes.
