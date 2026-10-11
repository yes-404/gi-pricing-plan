---
id: FD-9704
family: finding
title: SL-1257's migration c5a91e7d3b26 has no committed round-trip test and no test that existing api_keys rows are unchanged
status: active
created: 2026-10-11
owner: auditor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
corrected_by: []
relates: [WK-674, SL-1257, PL-1583, LG-1634, RS-9703, FR-417]
---

# FD-9704 — no committed test for SL-1257's migration

Filed by the retro audit RS-9703. Reads are at the squash-merge `fe80aec6` (PR #1280).

## Evidence

- PL-1583 Acceptance 3 requires the round trip `upgrade` / `downgrade -1` / `upgrade` to exit 0 and "A test asserts that existing `api_keys` rows are unchanged by the upgrade".
- `git grep -n -E 'c5a91e7d3b26|environment_settings' fe80aec6 -- backend/tests` finds the revision only in the new `test_settings_environment.py`, `test_score.py` and `test_score_rate_limit.py` cleanup helpers; none upgrades or downgrades, and none reads `api_keys` before and after.
- LG-1634 records the round trip only as a slot-script result ("Phase 2 up/down/up rc 0/0/0", run 2), and nothing about `api_keys`.
- The revision itself (`backend/migrations/versions/c5a91e7d3b26_environment_settings.py`) creates one table and adds no backfill, so the risk is low; the gap is the missing guard.

## Finding

**Severity MEDIUM (proposed by the auditor):** the property the plan says is tested (existing keys survive) has no test, so a later edit to this revision or to a migration after it could change `api_keys` unseen. Verdict candidate: delivered but untested.

## Disposition

**Owner: WK-674.** Decision: `fix before close with an owner: WK-674` — one migration test (round trip plus an `api_keys` row count and hash comparison), in SL-1258 or a maintenance slice. Event that next confirms or discharges it: that test merged. Filed by the auditor, 2026-10-11; the lead gives the verdict.

## Discharge path

Required by the maintainer's condition, `to-lead.md` "2026-10-11 20:17:38 BST" item 4: "each retro FD names its DISCHARGE PATH and date, not only an owner, so \"delivered-but-untested\" is closed by a TEST that runs, before the P2 close".

Fold into WK-674 S4's write set (SL-1258, its next alembic slice) as a red-first migration round-trip test: `upgrade` / `downgrade -1` / `upgrade` on a database holding `api_keys` rows, asserting the rows unchanged. Date: merged with SL-1258 and no later than the P2 exit demo, Thu 2026-11-12 (`docs/roadmap.md`, "Target: the P2 exit demo").
