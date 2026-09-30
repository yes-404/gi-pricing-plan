---
id: RL-9857
family: ruling
title: CR-1212's "docs-only" label for WK-1170 and WK-1169 is corrected — both Works carry code slices (the maintainer's DP-1 decisions, recorded)
status: active                 # accepted by the maintainer 2026-09-30 05:50:03 BST (see Accepted); active → superseded | retired (§1.2a)
created: 2026-09-30
owner: maintainer               # records scope decisions the maintainer made by delegation; drafted by the decision-maker (§1.6 RL row)
tree: 880feb499eddb9e854c525770e95fb19373a2311
phase: P2
work: WK-1170
supersedes: []
superseded_by: ~
corrected_by: []
corrects: CR-1212
relates: [CR-1212, PL-1276, PL-1277, RL-1263, WK-1169]
---

# RL-9857 (working id) — CR-1212's "docs-only" label for WK-1170 and WK-1169 is corrected

> **This record makes no new decision.** It records two scope decisions the maintainer already
> made by delegation. It exists because `CR-1212` is write-once and cannot be edited in place.
> It was `draft` until the maintainer accepted it on 2026-09-30 (see Accepted).

## Verified first, at `880feb499eddb9e854c525770e95fb19373a2311`

**The label.** `CR-1212` (`docs/closures/CR-01212-plan-review-15-p2-exit-criteria-budget-sequencing-and-the-open-finding-set.md`),
under "Proposal 2 — the extended goal's sequencing under the budget" (`:277`), reads at
`:289`:

> 4. **WK-1170, then WK-1169** (docs-only), in gaps;

That is the only "docs-only" in the file (`grep -n "docs-only"` gives `:289` alone).

**Why it cannot be edited in place.** `CR` is write-once (`docs/process/document-ids.md:53`).
Only `status:`, `superseded_by:` and `corrected_by:` are edited after a file freezes (`:134`).
Check 34 (`:230`) accepts only those edits, and requires every `corrected_by:` entry to be a
record whose `corrects:` names the file.

**The precedent.** `RL-1263` obligation 3
(`docs/rulings/RL-01263-…-on-the-maintainer-s-behalf.md:173-175`) amends `CR-1212`'s "§8
stands" by a separate ruling that `corrects: CR-1212`. `CR-1212` gains only a `corrected_by:`
entry. This record follows that model: its front matter mirrors `RL-1263`'s, with `owner:
maintainer` and `corrects: CR-1212`.

**The two plans already say the label is to be corrected elsewhere.**
- `PL-1276` (WK-1170's map plan), DP-1 at `:233`, "Resolved by": "**(a) accepted:** the
  maintainer, by delegation, 2026-09-29 22:58:26 BST entry … `CR-1212:289`'s label gets a dated
  correction citing that entry; it is not this plan's to write".
- `PL-1277` (WK-1169's map plan), DP-1 at `:201`, "Resolved by": "**(a) accepted:** the
  maintainer, by delegation, 2026-09-29, entry 'DECISIONS: WK-1169 map plan #931' … `CR-1212`'s
  "docs-only" label is corrected by the same dated note as `PL-1276`'s DP-1; it is not this
  plan's to write".

**The decisions, in the lead's channel file** (`to-lead.md`, local, not in the repository).
They are cited by entry heading, with the line each held when read on 2026-09-30. *In the two quoted titles, the minted plan id is shown in square brackets where the entry has the working id (9811, 9812). The rest of each title is verbatim.*

| Work | Decision entry | Acceptance entry |
|---|---|---|
| **WK-1170** | "2026-09-29 22:58:26 BST — DECISIONS: WK-1170 map plan #930 ([PL-1276]), DP-1 to DP-3" (`:12324`): "**DP-1: (a) ACCEPTED.** WK-1170 takes its code slices (S3–S6). CR-1212:289's "docs-only" label is corrected by a dated note, citing this entry." | "2026-09-30 04:11:59 BST — MERGE-ACK #930 and ACCEPTANCE of PL-1276 (WK-1170 map plan)" (`:12762`). Its DP-1 line (`:12779`) reads: "code slices S3–S6, which the maintainer decided 2026-09-29 22:58:26". |
| **WK-1169** | "2026-09-29 23:05:29 BST — DECISIONS: WK-1169 map plan #931 ([PL-1277]) DP-1, …" (`:12373`): "**DP-1: (a).** S3 (the binding check) stays in WK-1169 as code, the same as WK-1170 DP-1. CR-1212's "docs-only" label for WK-1169 is corrected by the same dated note." | "2026-09-30 04:39:07 BST — MERGE-ACK #931 and ACCEPTANCE of PL-1277 (WK-1169 map plan)" (`:12791`). Its DP-1 line (`:12808`) reads: "S3 is code, and lives in `audit-docs.py` per document-ids §1.11". |

## Ruled

This section records decisions already made. It rules nothing new.

1. **WK-1170 carries code slices S3–S6.** This is `PL-1276` DP-1 (a), accepted by the
   maintainer by delegation on 2026-09-29 at 22:58:26 BST.
2. **WK-1169 carries code slice S3**, the binding check, which lives in `scripts/audit-docs.py`
   per `document-ids.md` §1.11. This is `PL-1277` DP-1 (a), accepted by the maintainer by
   delegation on 2026-09-29 at 23:05:29 BST.
3. **`CR-1212:289`'s "(docs-only)" no longer holds for either Work.**
   - `CR-1212`'s text is unchanged. It records what was believed on 2026-09-28.
   - This record is its correction, and `CR-1212` gains `corrected_by:` naming it.
   - The sequencing in that line ("WK-1170, then WK-1169 … in gaps") is not touched here. The
     two Works' code slices take gate slots under the lanes rule like any other build slice
     (the 22:58:26 entry).

## Accepted

**The maintainer's acceptance, by delegation, quoted whole** from the entry "2026-09-30
05:50:03 BST — ACCEPTANCE of #948 (RL-9857, the correcting RL for CR-1212's "docs-only"
labels)" in `~/gi-pricing-plan.local/channel/to-lead.md`:

> **RL-9857 accepted** by the maintainer, 2026-09-30 (dated line by delegation). **What was read at 9e570bd7:**
> - **It records, and rules nothing new:** WK-1170's code slices S3–S6 (PL-1276 DP-1 (a), 2026-09-29 22:58:26) and WK-1169's code slice S3 in `audit-docs.py` (PL-1277 DP-1 (a), 23:05:29).
> - **Effect:** CR-1212:289's "(docs-only)" no longer holds for either Work. CR-1212's text is unchanged.
> - **Its only edit to CR-1212** is `corrected_by: [RL-1263]` → `[RL-1263, <minted id>]`, as check 34 permits.
> - **The sequencing in CR-1212:289 is not changed.** The two Works' code slices take lanes under RL-1263.

**The instrument, corrected (2026-09-30).** The same entry records that the maintainer's
2026-09-29 22:58:26 BST instruction to put "a dated note" on `CR-1212` was the wrong
instrument, because a closure record is write-once (`document-ids.md:53`, `:134`). A
correcting RL is the right instrument, and this record supersedes that instruction.

## What it obliges

- **`CR-1212`'s front matter** gains this record in `corrected_by:`. It is appended beside
  `RL-1263`, in this record's own PR, as the only edit to `CR-1212`, which check 34 permits.
- **At the mint turn,** the working id is replaced by the minted id in both files.
- **A reader of `CR-1212` Proposal 2** follows `corrected_by:` to here before treating either
  Work as docs-only.

## Acceptance — the violation that must become detectable

A frozen `CR-1212` edited in its body instead of corrected by a separate record fails check 34
(`document-ids.md:230`). A `corrected_by:` entry on `CR-1212` whose record does not name
`CR-1212` in `corrects:` also fails check 34. This record satisfies both: its `corrects:` is
`CR-1212`, and the only `CR-1212` change is the `corrected_by:` append.
