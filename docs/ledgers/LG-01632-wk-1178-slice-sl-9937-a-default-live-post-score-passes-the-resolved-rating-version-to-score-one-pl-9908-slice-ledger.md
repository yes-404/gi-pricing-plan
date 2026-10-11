---
id: LG-1632
family: ledger
title: WK-1178 slice SL-1631 — a default-live POST /score passes the resolved Rating Version to score_one (PL-1630 slice ledger)
status: closed
created: 2026-10-11
owner: executor
tree: d699a561d6a93f33b74beb9c07023f8e655bb8c7
phase: P2
work: WK-1178
slice: SL-1631
plans: [PL-1630]
corrected_by: []
relates: [PL-1630, PL-1544, PL-1454, FR-250, FR-259, NFR-499, WK-1178]
---

# LG-1632 — WK-1178 slice SL-1631: default-live `/score` passes the resolved ref

Executed by `executor-dlfix` from PL-1630, base `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7`. Times are BST unless marked.

**GO:** `to-lead.md`, "2026-10-11 11:29:37 BST — DISPATCH GO: SL 9937 (default-live /score fix, PL 9908, LG 9909), effective when PL 9908 is pushed with the acceptance below; the trace limb IN scope". PL-1630 pushed at `185c2bdf0909216e04f1d4ca7b515c8f41398084`.
**MERGE-ACK:** not yet given.

## Tasks

- [x] Task 1 — tests (a)–(e) and the fix, authored `0b46672a`, `7ec284f9`; (b) made field by field in the activation commit.
- [x] Task 2 — in the gate slot: src-only revert of `backend/src/app/api/score.py` shows (a)–(e) red by cause, restored, green; then the full two-half gate.
- [x] Task 3 — closing acts (LG and SL-1631 `closed` at the head).

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

Full gate at HEAD `466f85e6926bfb42c4b0e75f5704aaf0acc6e264` (tree `8eac9f851f8bbe3c09860bc65486fef33890c5b9`), gate-1, 12:47:18–13:29:57 BST. Script `~/gi-pricing-plan.local/scratch/sl9937/slot.sh`; output `slot-run.out`; per-stage logs `gatelogs/` beside it.

**Preflight abort proofs.** (1) A wrong expected sha (`000…0`) printed `HEAD guard: 466f85e6… != 0000…` and exited 9 (the HEAD guard, not the preflight block). (2) The first queue (12:47:05) hit a real preflight abort: the worktree `.venv` lacked `alembic` (`error: Failed to spawn: \`alembic\``), printing `alembic rc=2` then `PREFLIGHT ABORT: alembic upgrade head rc=2`, and the slot released. Fixed with `uv sync --all-packages --frozen`; the second run printed `alembic rc=0` / `preflight ok`.

| stage | rc | class |
|---|---|---|
| red_a (`...scored_by_the_real_evaluator_against_the_live_version`) | 1 | expected red, `INPUT_CONTRACT_VIOLATION` ×2 |
| red_b_http (`...no_options_object_is_scored_by_the_real_evaluator`) | 1 | expected red, ICV ×1 |
| red_c (`...resolved_version`) | 1 | expected red, ICV ×1 |
| red_d_guard (`...explicit_ref_wins...`, test_score.py:1710) | 0 | guard: passes on base by design (an explicit ref already won), 1 passed; proves no regression, not a failing case |
| red_e_b_unit (`...stamped_on_a_copy...`) | 1 | expected red, `AttributeError` ×2 (helper absent on base) |
| green (whole `test_score.py`) | 0 | |
| ruff / mypy / import_linter / req_coverage / contracts | 0 | |
| audit_docs | 1 | mint artefact: only `check 31` ×2, gaps 1608–9908 and 9909–9937 (working ids unminted) |
| pytest | 1 | mint artefact: 13 failed, 5461 passed, 4 skipped (2338.74s); every failure is a real-tree audit / contiguity assertion carrying the same check-31 gap (e.g. `doc-id.py check: [noncontiguous] docs/INDEX.md has a gap between 1608 and 9908`) |
| fe_install / generate / lint / typecheck / test / build | 0 ×6 | DagDesigner F39 (FD-1611, now on main) did not appear: `fe_test` rc 0 |

The 13 pytest failures: `test_audit_docs_finding_citations` (1), `test_audit_docs_ids` (2), `test_audit_docs_process_core_digest` (2), `test_audit_docs_w37_11_ceiling` (1), `test_doc_index` (1), `test_register_lint` (3), `test_register_owed` (1), `test_repository_invariants` (2). None is own; the mint turn's rerun after the ids are minted must show them green.

## PRs

None yet.
