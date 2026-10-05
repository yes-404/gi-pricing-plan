---
id: FD-9619
family: finding
title: OQ-1316 and OQ-1373 are missing from roadmap §10's decision-gate table
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: 809a3794af6d3a6ba688663b0d9b59f951190680
corrected_by: []
relates: [WK-1170, WK-1178, OQ-1316, OQ-1373]
---

# FD-9619 — two open questions are invisible to the plan: OQ-1316 and OQ-1373 have no row in `docs/roadmap.md` §10

**Filed** by auditor-oq-gate on the lead's order of 2026-10-05, from the maintainer's slot priority 3 (entry headed
"2026-10-05 15:19:09 BST — All four batches ACK-ready: noted; FD 9699 owner = WK-673; FD 9645 MEDIUM confirmed; the #1149 body incident; slot priorities",
`to-lead.md`, a local channel file, so cited by its header). Working id 9619 (reserved in the lead's `eta.md`).
`tree:` is `origin/main` at filing; every measurement below ran at that tree.

## Finding

**Severity: LOW; owner: WK-1170 — both ruled by the maintainer (by delegation), 2026-10-05 15:28:26 BST, entry headed "Wave results: D1 = (c); D2 PL 9624 DPs; D3 PL 9629 DP-6 + plan the 2 missing G2 items; C1′ is FD 9995 (no new finding); FD 9619 noted" (`to-lead.md`, a local channel file, so cited by its header) ("LOW, owner WK-1170, CONFIRMED").** Two open
questions are mirrored in `docs/open-questions.md` and in `03` §10 and are in no row of `docs/roadmap.md` §10's decision-gate
table, so the plan does not show when they must be answered. `.claude/skills/spec-change/SKILL.md` already requires the row
("A new `OQ-` also goes into `docs/roadmap.md` §10's decision-gate table, in the same commit") and says in the same place
that `audit-docs.py` does not check it. Nothing failed in CI; the gap was found only by running the `docs-audit` skill's
script by hand.

## Evidence

### 1. The measurement

The gate-table coverage script from `.claude/skills/docs-audit/SKILL.md` (section "The check the script does not do", the first
`python3 -` block), run verbatim from the repository root at `809a3794af6d3a6ba688663b0d9b59f951190680`:

```
missing   : ['OQ-1316', 'OQ-1373', 'OQ-538', 'OQ-539', 'OQ-549', 'OQ-602', 'OQ-603', 'OQ-604', 'OQ-652', 'OQ-656']
extra     : none
duplicated: none
```

The skill records eight of the ten as expected, decided ids "recorded rather than placed" (OQ-538, OQ-539, OQ-549, OQ-602,
OQ-603, OQ-604, OQ-652, OQ-656; the roadmap's 2026-08-26 note beneath the table). Its words: "Any id beyond those eight is a
real omission." Two are beyond them: **OQ-1316 and OQ-1373.** `grep -n -E 'OQ-1316|OQ-1373' docs/roadmap.md` finds only a prose
mention of OQ-1316 (line 924, inside a SL-1345 dated note), in no gate row.

### 2. Both are open, and neither is struck

`grep -n -E '\*\*OQ-(1316|1373)\*\*' docs/open-questions.md` gives lines 138 and 141. Both rows end `open (raised 2026-09-30)` and
`open (raised 2026-10-01)`. Owners on those rows: OQ-1316 WK-1178; OQ-1373 "the F35 plan (`PL 9776` (working id), WK-1178)".

### 3. When each was added, and which PR skipped the row

Predicate: `git log origin/main --format='%h %aI %s' -S'<id>' -- <path>`.

| Id | First on main | Commit | Roadmap §10 touched by that commit? |
|---|---|---|---|
| OQ-1316 | 2026-09-30 15:45:18 +01:00 | `fa9a73c2`, "RL-1312 + OQ-1316, RL-1313, PL-1314/SL-1315 (activated), FD-1317 — mint batch 4" (#994) | The commit's `docs/roadmap.md` edit (18 added lines) is the SL-1315 slice row, not a gate row: `git log -S'OQ-1316' -- docs/roadmap.md` finds only `f689c782` (#1027, 2026-10-01), which added the line-924 prose note. |
| OQ-1373 | 2026-10-03 16:22:41 +01:00 | `6891b30e`, "FD-1372, OQ-1373, FD-1374 — mint batch B" (#1077) | No: `git show --stat 6891b30e -- docs/roadmap.md` is empty. |

The #994 edit to `docs/roadmap.md` is the `SL-1315` slice row (`git show fa9a73c2 -- docs/roadmap.md`: 18 added lines, a heading, a yaml block and prose), not a gate row; #1077 carried no roadmap change (`git show --stat 6891b30e` lists INDEX, two essays, the register, `open-questions.md` and `03`). The skipped step is the same in both: the mint batch added the OQ row and its `03` mirror and not the §10 row.
Contrast: OQ-1321, raised the same day as OQ-1316 by the decision-maker, was placed (the roadmap's "2026-09-30 — OQ-1321
placed at Before Phase 3" note). The decision-maker's role file does not tell it to add the row (the roles PR #1159 does).

## Disposition

Open. Filed by the auditor, 2026-10-05; severity LOW and owner WK-1170 ruled as above. The gate row for each OQ is proposed below and ruled at the ACK.

**Remedy, proposed (two parts, the second is the cure for the class):**

1. **Add the two rows** to `docs/roadmap.md` §10, in one gate row each, in the compact id form, with no `OQ-` id in any
   explanatory italics (the skill's warning). Which gate each belongs to is proposed in §Proposed gate rows below.
   Recount each touched row's `N (M open)` with the skill's second script.
2. **Add the check to `audit-docs.py`**: the coverage script's three assertions (`missing`, `extra`, `duplicated`) with the eight
   recorded ids as a named exemption set, plus the count recount. `.claude/skills/docs-audit/SKILL.md` and
   `.claude/skills/spec-change/SKILL.md` both say today that the script does not do it; when the check lands, both sentences change
   in the same commit. Owner WK-1170 (the create-read-retire audit, which already owns FD-1280's and FD-1282's audit-docs guards) is ruled.

Event that next confirms or discharges it: the remedy PR merging, and the script printing `none` for `missing` beyond the
eight recorded ids.

## Proposed gate rows

The maintainer's 15:28:26 entry says the auditor proposes, for each OQ, the gate of the Work that owns its decision (a decided OQ gets a decided row), and that the maintainer confirms at the ACK. **Both are proposals: ruled by the maintainer (by delegation) at the ACK. This PR adds no row to `docs/roadmap.md`.** Both OQs are owned by WK-1178 (`docs/open-questions.md` :138 and :141); the §10 table has no WK-1178 row, so the proposal picks the existing row whose trigger matches what each answer changes.

| OQ | Proposed gate row | Reason |
|---|---|---|
| OQ-1316 | **Before Phase 3** | The OQ's own recommendation is "(c) now, then (a) when a concrete requirement for intermediate rounding appears": (c) is today's rule, so P2 does not block on the answer, and `round`, `floor` and `ceil` stay off the P2 allow-list meanwhile. This is the row where OQ-1321 (same Work, same RL-1312 lineage, an option (a) recommended post-P2) was placed on 2026-09-30. |
| OQ-1373 | **Before the P2 exit demo** | NFR-500 is measured failing (516.07 GB/year against 200 GB), the F35 plan (WK-1178, Phase 2 work) re-measures it under whichever reading is ruled (its DP-F35-3), and the plan cannot state its acceptance until the reading is ruled. That is a Phase 2 exit input, the same shape as the two findings already on that row. The alternative is **Before Phase 3**, the row OQ-1229 (also WK-1178, "answer changes what its tests must prove before the Phase 2 exit") was placed on; the proposal prefers the earlier row because this budget is measured failing now. |

When the rows are added, recount each touched row's `N (M open)` with the `docs-audit` skill's second script (the skill's warning stands: no `OQ-` id in explanatory italics).
