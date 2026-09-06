---
id: PL-746
family: plan
kind: review
title: Slice 6a — the eight stale claims, verified 2026-08-22
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-22
owner: auditor
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-22-slice-6a-verified.md
---

# Slice 6a — the eight stale claims, verified 2026-08-22

Verification is **complete**; application to `docs/roadmap.md` is **not started**. The full
recommended replacement prose (including two complete slice-record drafts for PRs #124 and
#125) is held in the verification agent's transcript and can be recovered by resuming it.

`docs/roadmap.md` md5 at verification time: `1663344193c72be757ddba911d3b57b8`. **Re-check
before applying** — several agents write this tree, and the FR-95 acceptance hunk
(lines 2589, 2984) is already applied.

**Trap, confirmed twice in this repo's history (PRs #85 and #109):** escape `|` as `\|`
inside any table-row replacement text, even inside a code span. An unescaped pipe splits the
row and breaks `audit-docs.py`'s cell-count check.

## Verdicts

| # | Line | Claim | Verified verdict |
|---|---|---|---|
| 1 | 2906 | "twenty-two slices in" | **27.** Derived two ways that coincide: 27 slice-record headings, and the file's own self-numbering (`:2838` already calls itself "the twenty-seventh slice" — the contradiction is *inside one file*). Omits regularisation/CV (#124), Tweedie (#125), offset (#126), EBM (#129), GBM weights (#130) |
| 2 | 2561-2563 | "**one** buildable slice remains" | **Zero.** All five rows at 2568-2572 are struck as delivered; row 5 (EBM) was struck by the same pass that left the counter at one |
| 3 | 1444-1450 | six requirements "Not started" | **All stale — and the audit under-counted.** They occupy **four** rows, not six. **FR-202 reads "Partial.", not "Not started".** And **FR-174 at :1444 is a seventh stale row the audit missed** — delivered 2026-08-17, six markers |
| 4 | 1240 | FR-352 "not started" | **Delivered in two of three clauses.** Evidence Bundle + change summary are built and fail closed. **The third clause — "a completed checklist" — has no implementation**: `grep -rn "checklist" backend/src` is empty. Do not write a flat "delivered". Cite the test *name*, not its line: it is `:246` at HEAD and `:372` in the tree |
| 5 | 65 | AST parser "Phase 1, WK-661" | **Stale, and the contradiction is a three-way split.** The *parser* was built in **WK-660** for `01` FR-36; `02` §4.6's *grammar* is **Phase 2, WK-690** by OQ-573 (2026-08-15). Line 65 hands the same spec section to a different phase than WK-690's own row at :2981 |
| 6 | 1291 | "seventy-eight requirements" | **124** — and the finding is sharper than staleness: **78 was never a count of `02`.** It is §6's Phase-1b planning estimate ("≈ 78 of 375") borrowed from a table two pages away. The derived count *on the day it was written* was **85** |
| 7 | 264-265 | "writing that skill is the outstanding item" | **False when committed.** `1ab7b1b` (2026-08-15, PR #66) added `.claude/skills/phase-review/SKILL.md` (112 lines) **and this sentence, in the same commit** |
| 8 | — | PRs #124/#125 have no slice records | **Confirmed — the 3rd and 4th omissions.** The file names #102 and #120 (at :2521-2524 and :2906) and not these. Both drafts written |
| 9 | 2704-2718 | custom-metrics "Not delivered: `custom_metric` evidence floor, owner WK-661" | **Delivered today**, in the order the entry itself specified. Strike the verdict clauses; keep the diagnosis |

## Where the audit itself was wrong

1. **"Corrected twice before"** (item 1) is wrong. There is **one** recorded prior correction
   (2026-08-19, PR #117, eighteen → twenty), written in two places — which is probably what
   read as two. The count has gone stale **twice** and been corrected **once**.
2. Item 3 under-counted: seven stale rows, not six, and one verdict misquoted.
3. Item 4 overstates: two of three clauses, not all three.
4. Item 6 mis-diagnoses: not stale, **wrong on the day**.

## The mechanism behind items 1, 2 and 8 — worth naming once rather than re-fixing

Verified in the diffs: **#124 and #125 did touch `docs/roadmap.md`.** Both spent that edit
striking their row in the outstanding-work table and stopped. The count at :2906 and the
counter at :2561 are *second places* nothing reconciles against that table. #116 did it, then
#124 and #125 did it again.

A slice whose entry in this file is a row it can **strike** treats the strike as the
bookkeeping; a slice with no such row writes a record. A row's strike says a slice happened —
only a record says what it found. The Tweedie slice is the sharpest case: its strike says
"DELIVERED 2026-08-21", while what it actually found — that the design on file
(deviance argmin) produced a **measurably biased** estimator, ~truth + 0.25 and grid-edge at
every seed, and that the fixture built to check it was wrong in the same direction — lived
for four days only inside `02`'s amendment and a squashed commit message.
