---
id: RL-8024
family: ruling
title: RL-1685 corrected — its gc.freeze test ("gc.get_freeze_count() is non-zero once the app has started") was vacuous; the ruled test is a call spy and an effect delta
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-14
owner: decision-maker
tree: 4420f91fa4112a1fcabcae23d3d50a1ad4fcbb59
phase: P2
work: WK-1178
slice: SL-1455
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1685
relates: [RL-1685, SL-1455, PL-1454, NFR-489, NFR-454]
---

# RL-8024 — RL-1685 corrected: the `gc.freeze()` test could not fail

*Disclosure: drafted under **working id RL 8024**, reserved by the lead (team-lead) in
`~/gi-pricing-plan.local/handover/eta.md` at the 2026-10-14 10:55 line, for D16. The mint sweep
replaces `RL-8024` here, and in `RL-1685`'s `corrected_by:`, with the minted id.*

## How this was ruled

- **The ruling is the maintainer's (by delegation).** The entry "2026-10-14 10:54:56 BST —
  RL-1685's gc.freeze test: VACUOUS, confirmed; spy form ACCEPTED + an effect delta; recorded by
  a CORRECTING RL, not a line in RL-1685 (re lead 10:54:25)" in
  `~/gi-pricing-plan.local/channel/to-lead.md`. That file is local, so the part relied on is
  quoted below (RFC-777).
- **It records a correction, not a new design.** `RL-1685` DP-4 = (a), `gc.freeze()` at the end of
  the lifespan's start-up, stands. What is wrong is one clause of its Task 3 (`RL-1685`, the line
  "with a timing-free red-first test that `gc.get_freeze_count()` is non-zero once the app has
  started"), the test that is supposed to prove it.
- **`RL-1685` is minted and frozen, so its body is not edited.** Its front matter gains
  `corrected_by: [RL-8024]` (front matter only), as the entry orders.

## The probe evidence

From the lead's entry "2026-10-14 10:54:25 BST" in
`~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`, on SL-1455's tree:

- `gc.get_freeze_count()` was **375** after `create_app(settings)` alone, before the lifespan
  or a `TestClient` ran.
- A `gc.freeze` wrapper plugin saw **no call**.
- `sys.setprofile` saw **no freeze `c_call`**.
- There is **no `gc.freeze` in `backend/src` or `packages`**.
- So the count is non-zero with no freeze anywhere, and the source of the 375 objects is
  **UNKNOWN** on that thread. It is recorded as unknown in SL-1455's ledger and not chased: whether it
  matters is the bench's question (the gen2 pause with and without the freeze), not the unit
  test's.

The ruled form of `RL-1685` ("non-zero once the app has started") therefore **passes with no freeze
call in the code**. A test that cannot fail is not a test.

## Ruled

The maintainer's (by delegation) entry, verbatim in the part relied on:

> The seat's probe shows the ruled form ("gc.get_freeze_count() is non-zero once the app has
> started") passes with no gc.freeze anywhere (count 375 after create_app alone; no call seen by a
> wrapper plugin or sys.setprofile; `gc.freeze` absent from backend/src and packages). A test that
> cannot fail is not a test.
> **Ruled test, two asserts, both red on the base tree:**
> 1. **Call:** monkeypatch `gc.freeze` with a spy wrapping the real one; start the app (lifespan);
> assert exactly ONE call, made after the lifespan's last start-up step (rate_limiter on app.state
> at the call). Red: `assert [] == [True]`.
> 2. **Effect (relative, not absolute):** with the REAL gc.freeze, `gc.get_freeze_count()` read
> immediately before the lifespan start and again at `yield` is strictly greater at `yield`. Red on
> base by cause: the delta is 0 with no freeze call. This is the half that proves the freeze
> actually moved objects to the permanent generation, which the spy alone cannot. The unexplained
> 375 baseline is why it must be a delta.
> Fix: `gc.freeze()` in the lifespan just before `yield`, as proposed. The 375-object baseline's
> source is recorded as UNKNOWN in the SL-1455 LG, not chased now. Whether it matters is the
> bench's question (the gen2 pause measured with and without the freeze), not the unit test's.

So:

1. **Assert (1), the call.** A spy that wraps the real `gc.freeze`; exactly one call, made after the
   lifespan's last start-up step (`rate_limiter` already on `app.state`). Red on the base tree:
   `assert [] == [True]`.
2. **Assert (2), the effect.** With the real `gc.freeze`, `gc.get_freeze_count()` just before the
   lifespan starts is strictly less than at `yield`. Red on the base tree: the delta is 0. It is a
   delta, not an absolute, because of the unexplained 375 baseline.
3. **The fix is unchanged from `RL-1685` DP-4 = (a):** `gc.freeze()` in the lifespan just before
   `yield`.

## What it obliges

- **SL-1455 Task 3** writes both asserts and shows each red by its stated cause on the base tree
  before the fix.
- **SL-1455's ledger** records the 375 baseline's source as UNKNOWN.
- **`RL-1685`** gains `corrected_by: [RL-8024]` in its front matter. Nothing else in it changes.

## Acceptance — the violation that must become detectable

The violation: **the app starts without ever calling `gc.freeze()` and the test suite stays green**,
which is what `RL-1685`'s "non-zero once the app has started" form allowed (the count was 375 with
no freeze anywhere).

- *Violation: no freeze call.* SL-1455's spy test reds on the base tree with `assert [] == [True]`.
  The slice shows that red, by cause, in its `LG-` before the fix.
- *Violation: the call moves nothing.* SL-1455's effect test reds on the base tree with a freeze-count
  delta of 0 between the lifespan's start and `yield`; it goes green only when the real
  `gc.freeze()` runs just before `yield`.
- *Violation: the correction is not linked.* `RL-1685`'s front matter reads `corrected_by: [RL-8024]`
  (`grep -n '^corrected_by:' docs/rulings/RL-01685-*.md`), and its body is unchanged.
