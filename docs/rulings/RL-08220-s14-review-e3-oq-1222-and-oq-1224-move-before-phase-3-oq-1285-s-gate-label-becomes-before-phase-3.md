---
id: RL-8220
family: ruling
title: §14 review E3 — OQ-1222 and OQ-1224 move to "Before Phase 3" with owner WK-1178; OQ-1285's gate label "Before WK-675 S12" becomes "Before Phase 3"
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; working id until minted in the §14 review PR
created: 2026-10-25
owner: decision-maker
tree: ff976406f1bf133cfe040d2c44d383011503988a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [OQ-1222, OQ-1224, OQ-1285, WK-1178, WK-675, PL-1371, RL-1645, RL-1524]   # CR 8219 added at the mint
---

# RL-8220 — §14 review E3: three gate placements

*(Working id 8220, reserved by lead 28 in `handover/eta.md` at 2026-10-25 11:35:25 GMT. It
mints in the §14 review's PR, with the review `CR 8219`. Working ids in prose are in space
form and are not minted.)*

## How this was ruled

- **The decision is not this record's.** It is the maintainer's, in
  `~/gi-pricing-plan.local/channel/to-lead.md` (a local file, cited by entry header), entry
  *"2026-10-25 11:32:17 GMT — Maintainer: §14 note r5 — the six owed rulings, decided now
  (dated lines for the review's rows)"*, line 1, verbatim:

  > **E3-B — ACCEPTED: (i) "Before Phase 3" for both OQ-1222 and OQ-1224**, owner WK-1178
  > unchanged, for the reasons r5 gives (the interim is loud; OQ-1224's `model-schema` change
  > would re-hash the demo's approved version). **E3-C — ACCEPTED:** OQ-1285's row label
  > "Before WK-675 S12" → "Before Phase 3" (S12 moved 2026-10-03, roadmap:1302). One **RL**,
  > decision-maker, three lines; the §10 row edits (Before-Phase-2 count 2 open → 0,
  > Before-Phase-3 gains the three ids, each with a dated move line) by the lead in the RL's
  > PR. No dated line inside the OQ texts — the gate row carries the timing.

  This line is the dated acceptance line of review items E3-B and E3-C. This record carries
  it as a dated artifact (`CLAUDE.md` §12). It is decided, so it carries no DRAFT banner.
- **The proposal it accepts** is the r5 note
  `~/gi-pricing-plan.local/handover/s14-review-items-draft-2026-10-25-r5.md`, §E3-B and §E3-C.
- **Facts checked at `ff976406`** (`origin/main`, 2026-10-25):
  - `docs/roadmap.md:3510`, the "Before Phase 2" row, holds `**OQ-1222**` and `**OQ-1224**`
    as its only two bold (open) ids, with 22 distinct `OQ-` ids in the cell and the count
    "22 (2 open)".
  - `docs/roadmap.md:3517`, the "Before WK-675 S12" row (*added 2026-09-30*), holds
    `**OQ-1285**` only, with the count "1 (1 open)".
  - `docs/roadmap.md:3524`, the "Before Phase 3" row, holds 17 distinct `OQ-` ids, 8 of them
    bold, with the count "17 (8 open)".
  - `docs/roadmap.md:1302`, verbatim in its part: *"**2026-10-03 — Slice 12 (the
    Deployments view) moves to Phase 3** (`PL-1371` §9 DP-2 (a) …). … DP-7 (OQ-1285) moves
    with it."*
  - The three OQ rows: `docs/open-questions.md:139` (OQ-1222), `:141` (OQ-1224), `:143`
    (OQ-1285), and their `03` §10 mirrors at `docs/specs/03-rating-engine.md:1591`, `:1593`,
    `:1595`. Each is `open`.
  - The counting predicate for each row, runnable at that tree:
    `sed -n '<line>p' docs/roadmap.md | awk -F'|' '{print $3}' | grep -o -E 'OQ-[0-9]+' | sort -u | wc -l`
    for the ids, and the same with `grep -o -E '\*\*OQ-[0-9]+\*\*'` for the open ids.

## Ruled

1. **OQ-1222 is placed "Before Phase 3".** Its owner stays WK-1178. The interim is loud: a run
   states `grid: uniform+sampled`. No P2 plan schedules the per-library verification, and the
   exit demo's property is already ruled around the weaker grid (`RL-1645`).
2. **OQ-1224 is placed "Before Phase 3".** Its owner stays WK-1178. Its option (a) is a
   `model-schema` change that moves every bundle hash, so landing it before the exit demo
   would re-hash the demo's approved Rating Version. The weakness is pinned by the S3
   known-limit test, and `RL-1524` and `RL-1645` rule the demo around it.
3. **OQ-1285's gate label "Before WK-675 S12" becomes "Before Phase 3".** S12 moved to Phase 3
   on 2026-10-03 (`docs/roadmap.md:1302`, "DP-7 (OQ-1285) moves with it"). Its owner, WK-675,
   and its text are unchanged.

**No dated line goes inside any of the three OQ texts** (both mirrors untouched). The gate row
carries the timing.

## What it obliges

The §10 row edits below are the lead's, in this record's PR.

The edits are the lead's (the 11:32:17 line 1). They are listed here so that they can be
checked against this record. Line numbers are at `ff976406`; the review's PR may shift them.

| Row (`docs/roadmap.md`) | Edit to the ids cell | Count cell: old → new |
|---|---|---|
| **Before Phase 2** (:3510) | Remove `**OQ-1222**` and `**OQ-1224**` from the cell. Keep the struck `~~OQ-1223~~ ✔` and its italic note; reword the note's lead-in so that it does not name the two moved ids, or the recount predicate still counts them. | "22 (2 open)" → "**20 (0 open)** — *recounted 2026-10-25 (`RL-8220`): two ids moved to Before Phase 3. Before that:* 22 (2 open) …" (the existing history is kept after it). This follows the `CR-1247` Proposal 5 precedent in the same cell, where a move lowered the total ("20 (5 open)" → "18 (3 open)"). |
| **Before WK-675 S12** (:3517) | Label: "**Before WK-675 S12** — *added 2026-09-30*" → "**~~Before WK-675 S12~~ Before Phase 3** — *added 2026-09-30; relabelled 2026-10-25 (`RL-8220`): S12 moved to Phase 3 on 2026-10-03 (roadmap:1302); its id moved to the Before Phase 3 row*". Ids cell: remove `**OQ-1285**` and its note (it goes to the Before Phase 3 row). | "1 (1 open)" → "**0 (0 open)** — *recounted 2026-10-25 (`RL-8220`): one id moved to Before Phase 3. Before that:* 1 (1 open)" |
| **Before Phase 3** (:3524) | Append three bold ids, each with a dated move line: `**OQ-1222**` *(moved 2026-10-25 from Before Phase 2 by `RL-8220`, owner WK-1178: the `monotone` grid's GBM split thresholds)*; `**OQ-1224**` *(moved 2026-10-25 from Before Phase 2 by `RL-8220`, owner WK-1178: pinned Bandings, a `model-schema` change that moves every bundle hash)*; `**OQ-1285**` *(moved 2026-10-25 from Before WK-675 S12 by `RL-8220`, owner WK-675: `/rating/environments` vs `/admin/environments`; S12 moved to Phase 3 on 2026-10-03)*. | At `ff976406`: "17 (8 open)". The decision-maker's branch for this review (`draft/dm-14`) first adds `OQ 8222` and `OQ 8223` to this row (records of the same review; the decision-maker writes the gate row of an OQ it raises), so the row the lead edits reads "19 (10 open)". New: "**22 (13 open)** — *recounted 2026-10-25 from the row's ids: three ids moved here by `RL-8220`. Before that:* 19 (10 open) …". Recount it from the row's ids after all edits. Do not add to the old count. |

**On the S12 row.** Read alone, "row label → Before Phase 3" relabels row :3517 in place. The
same line says that "Before-Phase-3 gains the three ids". A relabel in place would leave two
rows labelled "Before Phase 3". So the label edit is applied as a move into the existing row,
and the old row keeps a dated tombstone label and a zero count, not a deletion
(`.claude/skills/spec-change`: *"deleting the row loses the appointment"*). If the lead
prefers to delete row :3517 instead, the ruling is not changed. That form is the lead's
choice, as the row edits are.

## Acceptance — the violation that must become detectable

- *Violation: a moved id is still bold under "Before Phase 2", or the count cell still reads
  2 open.* The bold-id predicate above, run on row "Before Phase 2" at the review's merged
  tree, prints 0 ids. The count cell reads "20 (0 open)".
- *Violation: an id is lost in the move.* `grep -c -E '\*\*OQ-(1222|1224|1285)\*\*'` on the
  "Before Phase 3" row prints 3, and on every other §10 row it prints 0.
- *Violation: a dated line is written into an OQ text.* `git diff origin/main...<review
  branch> -- docs/open-questions.md docs/specs/03-rating-engine.md` shows no hunk on the
  OQ-1222, OQ-1224 or OQ-1285 rows.
