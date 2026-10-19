---
id: RL-8131
family: ruling
title: The PL-1237 carry form applies equally to O4 and NFR-501 under D5.3 (PL-1620), extending the deferral form for SL-1259
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-19   # filed 2026-10-19 under working id 8131
owner: decision-maker
tree: 1aab7a21fc5732ac6c0ea0c47d02ac4980638220
phase: P2
work: WK-674
slice: SL-1259
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1620, LG-1824, WK-674]
---

# RL-8131 — The PL-1237 carry form applies equally to O4 and NFR-501 under D5.3 (PL-1620), extending the deferral form for SL-1259

Filed 2026-10-19 under working id 8131 (a working id until a later seat mints it). The ruling is the maintainer's (by delegation).

## How this was ruled

The source is the entry "2026-10-19 04:41:23 BST" in `~/gi-pricing-plan.local/channel/to-lead.md`. The file is local, so the whole entry is quoted below, copied from it by `sed`. The entry asks that this ruling ride D26 as an RL beside the SL-1575 one (RL 8130).

## Verified first, at 1aab7a21fc5732ac6c0ea0c47d02ac4980638220

- `docs/plans/PL-01237-*` lines 128-131 hold the carry form: "If no dedicated host exists at Slice 5's close, the F1 / acceptance test's verdict is **measured, diagnostic** on the shared VM and **carried**, / owner the maintainer, discharge event **a dedicated host available**." (read at this tree).
- `docs/plans/PL-01620-*` lines 189-199 hold D5.3 (the host): the rehearsal, the verdict runs on the temporary dedicated VM, and the fallback "the fallback form of `PL-1237` Acceptance item 6 applies unchanged".
- Both plans are frozen and are not edited.

## Ruled

The maintainer's entry "2026-10-19 04:41:23 BST", verbatim:

> - **Accepted as given:**
>   - adopted: FR-268, FR-269, FR-272/NFR-498 rollback, NFR-497, D5.11, D5.13 static, D5.14;
>   - FR-452/D5.10 is owed before the PR (the two-case test, run after END);
>   - D5.12 delivered-untested, its run on nfr-bench-1.
> - **Correction 1 (owner):** a deferral's owner is a WORK ROW that will do the work, not the maintainer. The maintainer only coordinates the user's VM.
>   - Owner for NFR-489/490/493/494/501/502, F1, O4 and D5.12's run = the **WK-674 NFR measurement session on nfr-bench-1** (SL-1455 Task 4 lineage; name the exact row the roadmap carries, or "owner row to be added in D26" if none exists);
>   - the maintainer is named only as "VM coordination (user action)".
> - **Correction 2 (due):** **NFR-489 is a §12 row 2 exit criterion** (user 14 Oct 09:50). Its deferral reads "due before the 12 Nov exit demo", not open-ended. The others carry "due before P2 close", unless a ruling says otherwise.
> - **Ruled:** PL-1237:128-131's carry form applies equally to **O4 and NFR-501** under D5.3 (PL-1620:189-199). Cite this stamp in LG 8127, so the extension is a recorded ruling, not an inference. It rides D26 as an RL beside the SL-1575 one.
> - **Light seats:** exec-1770f and auditor-1259w are accepted under 04:39:47.

The extension this record exists for is the line beginning "**Ruled:**" in the quote: `PL-1237`:128-131's carry form applies equally to O4 and NFR-501 under D5.3 (`PL-1620`:189-199). The two corrections and the accepted verdicts in the same entry are the maintainer's verdicts on SL-1259's audit and are quoted for context; this record does not restate them.

## What it obliges

- `LG-1824` (SL-1259's ledger) cites the stamp "2026-10-19 04:41:23 BST", so the extension is a recorded ruling and not an inference (the entry says so).
- `PL-1237` and `PL-1620` are not edited.

## Acceptance — the violation that must become detectable

This ruling answers a scope question about which items may use a carry form; no check can fail on a broken input. The violation to catch by reading: *Violation: a deferral of O4 or NFR-501 carries a form other than PL-1237:128-131's, or cites no ruling for using it.* A reviewer reads `LG-1824`'s deferral rows against the quote.
