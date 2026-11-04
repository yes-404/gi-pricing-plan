---
id: FD-1768
family: finding
title: Attribution words a purposes-only change to a sub-graph mount as "mount ports re-mapped"
status: closed
created: 2026-10-17
owner: auditor
tree: cf509df89dbebff329bb6b319bcc9bcd2a2c2352
corrected_by: []
relates: [WK-1250, SL-1341, SL-1696, FD-1660, SL-1989, LG-1990, PL-1991]
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

***Resolved 2026-11-04*** — closed in place 2026-11-04 by the executor, as the closing act of the mint of SL-1989 (WK-1250, LG-1990, PL-1991; this PR, its number and squash written at the merge's date-of-record), on the lead's brief under the GO "2026-11-03 17:30:53 GMT" (`to-lead.md`, a local channel file). Delivered remedy: the mount loop of `packages/pricing-core/src/pricing_core/rating/analysis.py` words the `before == after` branch by its flags, "mount ports re-mapped" when `ports_changed`, otherwise "mount purposes changed", with "; purposes changed" appended when both changed, and the re-point branch appends "; purposes changed" when purposes also changed (FR-1399, DP-5, DP-6; the spec sentence carries a dated amendment, DP-7 (a)). Red first: `test_mount_purposes_changed_forms` failed on the description (actual "mount ports re-mapped", expected "mount purposes changed") before the fix; `test_mount_purposes_alone_is_one_structural_mount_change_with_before_equal_after` verifies at base that `rating.py` already reports a purposes-only change as one mount change, so `rating.py` is not edited. Gate evidence is in LG-1990: the full gate at `322b20ec` (python half: 13 failed, exactly the eight docs-audit files of the common seat brief's item 31, 22 skipped = baseline; frontend lint, type-check, test and build all rc 0, vitest 905 of 905; demo designed stop, dislocation #1 586 s).
