---
id: FD-1618
family: finding
title: A default-live /score is refused with INPUT_CONTRACT_VIOLATION, because the handler and the trace worker pass score_one a context with no rating_version_ref
status: closed
created: 2026-10-11
owner: auditor
tree: 02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a
corrected_by: []
relates: [WK-1178]
---

# FD-1618 — a default-live `/score` never reaches a price

**Minted 2026-10-11 as FD-1618 from working id 9806, in the D11 batch mint PR.** Filed at the lead's entries in `to-lead.md`:
"2026-10-11 11:25:16 BST — DEFAULT-LIVE /score: CONFIRMED by reading (no wait for a run); FD + fix slice NOW; SL-1526's demo
script checked before its window" (item 2), and "2026-10-11 11:29:37 BST — DISPATCH GO: SL 9937 …" (item 1: the trace limb is
in scope). Every line number below is at `origin/main` `02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a`, read for this record.

## Evidence

1. **The handler.** `backend/src/app/api/score.py:369` resolves `ref, deployment_id = await _serving_ref(database, caller, ctx)`
   (the Environment's live Deployment when the request names no ref), and `:375` calls `score_one(compiled, ctx, trace=trace)`
   with `ctx` unchanged. The resolved `ref` is never written back into `ctx.options`.
2. **The refusal.** `packages/pricing-core/src/pricing_core/rating/score.py:945-952`: when
   `ctx.options.rating_version_ref` is `None`, `score_one` raises `INPUT_CONTRACT_VIOLATION` ("… Slice 1 builds no default-live
   resolution (DP1, Slice 2), so score_one cannot guess which version it is scoring against"). A request without a ref therefore
   reaches the refusal whenever it reaches `score_one`. The reading is decisive; no run was needed (11:25:16).
3. **The trace worker.** `backend/src/app/worker/trace_handlers.py:79-80` loads the stored `row.pending_quote_context` into a
   `QuoteContext` and the ref from `row.rating_version_ref`; `:98` calls `score_one(compiled, ctx, trace=True)`. The stored
   context is the ref-less one the handler held, so a sampled default-live trace is re-scored without a ref and refused the
   same way (`_maybe_sample_trace`, `score.py:384`, stores the context it was given).
4. **Why no test saw it.** The default-live tests (`test_score.py` :1379 ff., as the lead read them) stub `score_one`.
   Explicit-ref requests work on main, which is why the exit demo's scripted calls (an explicit `rating_version_ref`,
   `examples/fremtpl2/model.py` :629; `scripts/demo.py` has no `/score`) have not hit it (11:27:42).

## Finding

On main a default-live `POST /score` is refused on a P2 serving path, and a sampled default-live quote's trace can never be
reproduced. No price is returned wrongly: the failure is a refusal, not a mispricing.

**Severity (proposed by the auditor): HIGH.** The reason: it is the platform's principal serving path in its documented
default form (a request with no ref is served by the Environment's live Deployment, as `_serving_ref`'s docstring at `backend/src/app/api/score.py:169-185` states, citing `03` §4.12), and PL-1544's exit demo needs it
(PL-1544 :377, "POST /score with its key and no ref"). The reason it is not CRITICAL: the failure is a loud 4xx refusal,
never a wrong price, and explicit-ref callers are unaffected.

## Remedy (ruled, 11:25:16 item 3; 11:29:37 item 1)

SL 9937 (PL 9908, LG 9909; working ids): `_with_resolved_ref(ctx, ref)`, an immutable `model_copy` that never overrides an explicit
ref and creates `options` if absent, passed to `score_one` AND `_maybe_sample_trace`, so the stored context carries the resolved
ref and the trace re-scores. No bundle or price changes. NFR-499 is unaffected: the trace store already holds the full quote input.

## Disposition

**Owner: WK-1178**, discharged by **SL 9937**. Decision: `fix before close with an owner: WK-1178`. Event that next
confirms or discharges it: SL 9937's merge with its red-first DB test (`score_one` not stubbed, a Deployment present,
default-live request) red on base and green after. Filed by the auditor, 2026-10-11; the lead gives the verdict.
