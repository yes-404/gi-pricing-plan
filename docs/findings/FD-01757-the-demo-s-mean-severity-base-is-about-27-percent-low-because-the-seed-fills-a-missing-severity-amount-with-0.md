---
id: FD-1757
family: finding
title: The demo's mean-severity base is about 27% low, because the seed fills a missing freMTPL2sev amount with 0
status: closed
created: 2026-10-17
owner: auditor
tree: 055b5e6b74f9d4b10f6df54570e33ed2805ae9a8
corrected_by: []
relates: [WK-673, SL-1543]
---

# FD-1757 — The demo's mean-severity base is about 27% low

*(Minted 2026-10-17 as FD-1757 from working id 8079, in the D18 batch mint PR.)*

## Finding

**MEDIUM; owner WK-673; verdict `fix before close`, discharged by SL-1543** (the maintainer's
entry "2026-10-17 11:23:17 BST" in `to-lead.md`, census DP → (c), last paragraph). The demo's
mean-severity base (`demo_base_premium`, `examples/fremtpl2/model.py:478-500`; the ruling cites
`:482-495`) is €1659.44, against €2265.43 over known amounts, because
`examples/fremtpl2/seed.py:149-150` fills a missing freMTPL2sev amount with 0: 9116 claimants
(`ClaimNb>0`), every one with no sev row. Those amounts are unknown, not nil.

## Evidence

`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1543-census-cause.md` (read-only, at
`origin/main` `055b5e6b74f9d4b10f6df54570e33ed2805ae9a8`): the 9116 rows are exactly the
`ClaimNb>0` policies with no sev row; no sev amount is below 1.0. The two line ranges above were
re-read by the auditor at that tree (`seed.py:149-150` is `.join(totals, … how="left")` then
`fill_null(0)`; `model.py:478-500` computes Σ `claim_amount_minor` ÷ Σ `claim_count`).

## Disposition

Fix with an owner: WK-673, in SL-1543 (seed writes null for an unknown amount; the base is
computed over known amounts; FR-111 declares the severity population). The event that next
discharges it: the merge of SL-1543 with the re-derived base recorded in its ledger.


***Resolved 2026-10-18*** — closed in place 2026-11-03 by the auditor, on CR-1981 §5b (`docs/closures/CR-01981-wk-673-close-audit.md`) and the maintainer's ruling (C) in `to-lead.md` "2026-11-03 16:03:37 GMT" (a local channel file): fixed by SL-1543, PR #1335, squash `4a53f19492ad73ebfb699cabcab19765c68a5a76`: `examples/fremtpl2/seed.py:150-157` keeps an unknown claimant amount null (`ClaimNb > 0` with no severity row) and fills 0 only for a policy with no claim, so the mean severity base is taken over known amounts (FR-111). *Date of record: 2026-10-18 — #1335, squash 4a53f194.*
