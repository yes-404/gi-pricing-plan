---
id: LG-9909
family: ledger
title: WK-1178 slice SL-9937 — a default-live POST /score passes the resolved Rating Version to score_one (PL-9908 slice ledger)
status: active
created: 2026-10-11
owner: executor
tree: d699a561d6a93f33b74beb9c07023f8e655bb8c7
phase: P2
work: WK-1178
slice: SL-9937
plans: [PL-9908]
corrected_by: []
relates: [PL-9908, PL-1544, PL-1454, FR-250, FR-259, NFR-499, WK-1178]
---

# LG-9909 — WK-1178 slice SL-9937: default-live `/score` passes the resolved ref

Executed by `executor-dlfix` from PL-9908, base `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7`. Times are BST unless marked.

**GO:** `to-lead.md`, "2026-10-11 11:29:37 BST — DISPATCH GO: SL 9937 (default-live /score fix, PL 9908, LG 9909), effective when PL 9908 is pushed with the acceptance below; the trace limb IN scope". PL-9908 pushed at `185c2bdf0909216e04f1d4ca7b515c8f41398084`.
**MERGE-ACK:** not yet given.

## Tasks

- [x] Task 1 — tests (a)–(e) and the fix, authored `0b46672a`, `7ec284f9`; (b) made field by field in the activation commit.
- [ ] Task 2 — in the gate slot: src-only revert of `backend/src/app/api/score.py` shows (a)–(e) red by cause, restored, green; then the full two-half gate.
- [ ] Task 3 — closing acts.

## Build log

### Defect and fix

`score()` resolved the live ref with `_serving_ref` and passed `ctx` unchanged to `score_one`, which refuses a context with no `options.rating_version_ref` (`packages/pricing-core/src/pricing_core/rating/score.py:945-952`). The default-live tests stub `score_one`, so they never saw it. The fix: `_with_resolved_ref(ctx, ref)` in `backend/src/app/api/score.py` returns an immutable `model_copy` carrying the ref (options created if absent; an explicit ref returns `ctx` untouched), and `score()` passes the copy to `score_one` and to `_maybe_sample_trace`.

### Callers (read at `7ec284f9`; predicate `git grep -n '_serving_ref(\|score_one(' -- backend/src`)

| Site | Where | Gap? |
|---|---|---|
| `_serving_ref` single caller | `backend/src/app/api/score.py:382` (def `:169`) | — |
| `score_one` in `/score` | `backend/src/app/api/score.py:393` | fixed: gets the copy |
| `score_one` in `/score/compare` | `backend/src/app/api/score.py:465`, context built at `:462-464` with the explicit `ref` | none |
| `score_one` in the trace worker | `backend/src/app/worker/trace_handlers.py:98`, re-scoring `QuoteContext.model_validate(row.pending_quote_context)` (`:79`) | **same gap**: the stored context lacked the ref, so a default-live sampled trace would have failed `INPUT_CONTRACT_VIOLATION`. Fixed in `score.py` by storing the copy; the handler is untouched. Test (c) runs `execute_job` to `SUCCEEDED`. |
| batch worker | `backend/src/app/worker/scoring_handlers.py:178` (`_score_one_ref`) stamps the resolved ref per frame; it has no `score_one` call | none |

### Red and guard classification (the lead's ruling, 2026-10-11)

The slot runs each test on the base `score.py` (`git show d699a561:backend/src/app/api/score.py`, src-only revert), one `-k` each, and records rc and the printed cause. Expected: (a), (b) HTTP and (c) red by `INPUT_CONTRACT_VIOLATION`; (e) and (b)'s created-options assert, which live in one unit test, red as `AttributeError` (the helper is absent on base, a valid red for a new helper). **(d), explicit-ref-wins, passes on base** (explicit refs already work), so it is recorded as a **GUARD** (green on base, green at the head), not a red.

### Gate

Not yet run.

## PRs

None yet.
