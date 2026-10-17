---
id: FD-1768
family: finding
title: Attribution words a purposes-only change to a sub-graph mount as "mount ports re-mapped"
status: active
created: 2026-10-17
owner: auditor
tree: cf509df89dbebff329bb6b319bcc9bcd2a2c2352
corrected_by: []
relates: [WK-1250, SL-1341, SL-1696, FD-1660]
---

# FD-1768 — Attribution words a purposes-only change to a sub-graph mount as "mount ports re-mapped"

*(Minted 2026-10-17 as FD-1768 from working id 8085, in the D19 batch mint PR.)*

## Finding

**MEDIUM; owner WK-1250; verdict `fix before close`** (the maintainer's entry "2026-10-17
13:58:04 BST" in `to-lead.md`, "ADOPT … F2 → D19 FD MEDIUM WK-1250"). Wording only, no
pricing effect. `packages/pricing-core/src/pricing_core/rating/analysis.py:635-644`
(SL-1696, merged as #1310) words a sub-graph mount whose `before` equals its `after` as
`"{point}: mount ports re-mapped ({mount.after})"` (`:638`). Once SL-1341 adds a `purposes`
selector to the mount and `purposes_changed` to the mount diff, a change to `purposes` alone
reaches that branch, so the attribution text names ports for a purposes change. No test crosses
the two.

## Evidence

The SL-1341 slice ledger (its branch-local id, released and re-minted at the slice's PR turn; branch `origin/sl-1341-wk1250-s3-purpose-mount`,
head `94bc4a230d5f1d7137da86f79800d678281c0aca`), section "## Audit", finding F2: "delivered
but untested", lead verdict 2026-10-17 13:59:02 BST: "F2 → an FD in the next D batch (MEDIUM,
owner WK-1250)". Re-read by this author: at `origin/main`
`cf509df89dbebff329bb6b319bcc9bcd2a2c2352` the `elif mount.before == mount.after:` branch is at
`analysis.py:636-638`; the slice branch has the same lines. `purposes_changed` exists only on
the slice branch (`packages/model-schema/src/model_schema/rating.py:911`; `backend/src/app/
platform/change_summary.py:145` reads it), so the defect is live when SL-1341 merges, not on
`main` today. The slice cannot edit `analysis.py` without a re-gate, per the same audit.

## Disposition

Fix with an owner: WK-1250, in a follow-up slice after SL-1341 merges: the `before == after`
branch words ports and purposes separately by `ports_changed` / `purposes_changed`, with a test
that changes `purposes` alone. The event that next discharges it: the merge of that slice.
