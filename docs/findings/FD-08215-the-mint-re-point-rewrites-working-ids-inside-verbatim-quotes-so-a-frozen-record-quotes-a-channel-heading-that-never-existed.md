---
id: FD-8215
family: finding
title: The mint re-point rewrites working ids inside verbatim quotes, so a frozen record quotes a channel heading that never existed
status: active
created: 2026-10-25
owner: auditor
tree: ff976406f1bf133cfe040d2c44d383011503988a
corrected_by: []
relates: [WK-1178]
---

# FD-8215 — The mint re-point rewrites working ids inside verbatim quotes, so a frozen record quotes a channel heading that never existed

## Finding

**LOW; owner WK-1178 (tooling).** Authority: the maintainer's (by delegation) entry "2026-10-23 11:58:33 BST — Maintainer: SL 8178 RS 8214 CLEAN adoption CONFIRMED (4 LG lines + strict red-first); quote-alteration-at-mint class → one LOW FD, no body edits" (`to-lead.md`), item (B): no body edit to RL-1848 or any merged record; one LOW FD carrying the mechanism, the instances from one docs-only alternation sweep, and the remedy; the FD is the accepted disclosure for every listed instance; no per-instance correcting RL; an unmerged record is fixed in place before merge.

**The defect.** A record drafted under a working id quotes a `to-lead.md` entry heading that carries that working id ("RL 8176 ADOPTED"). At the mint the id is re-pointed over the whole tree. The re-point does not distinguish a citation from a verbatim quotation, so the quoted heading becomes "RL-1848 ADOPTED", which `to-lead.md` never contained. The known instance: RL-1848 on `origin/main` quotes the entry as "…RL-1848 ADOPTED, option (A) with one amendment…" where the heading reads "RL 8176 ADOPTED, option (A) with one amendment…" (2026-10-22 17:21:38 BST, `to-lead.md`). Others known: RS 8214 B1 and LG-8179 (both unmerged, fixed in place).

## Mechanism

There is no re-point script. `scripts/doc-id.py` has only `next`, `check`, `widen`, `migrate`, `migrate-verify`; the `repoint` helpers in it serve the W37-6 relative-link migration. The mint re-point is a seat-run whole-tree rename procedure written in prose:

- `.claude/skills/mint-and-finish/SKILL.md` §1 step 4: rename each old id, highest first, in one commit, then `git grep -c` of each OLD id = 0 "outside verbatim quotes".
- Common seat brief item 26 (the maintainer, "2026-10-18 09:17:30 BST"): grep the WHOLE tree for each working id (space and hyphen forms) "and re-point every hit".

Item 26 says every hit; step 4 exempts quotes; step 7 of the same skill says "Quoted channel headers keep their working ids" but gives no way to find them. An unmechanised rename over every hit, with an exemption that only a reader applies, rewrites quotes. Nothing then compares a quoted heading with `to-lead.md`: `audit-docs.py` has no such check, so the altered quote merges.

## Evidence

Command (one pass, docs only, over `origin/main` ff976406f1bf; run read-only):

owed: the sweep — the command, the hit table (file:line, quoted text, cited to-lead heading, working id or minted id, instance or not) and the count are filled in when the lead opens a SWEEP GAP.

Known instance, read now: `git -C <repo> show origin/main:docs/rulings/RL-01848-environment-scoped-writes-keep-load-first-the-404-is-accepted-and-the-order-is-written-into-06-fr-343.md` line 25 reads "RL-1848 ADOPTED"; `to-lead.md` line 29659 reads "RL 8176 ADOPTED".

## Remedy (not made here)

1. The re-point skips spans inside quotation marks (the mint-and-finish procedure and, if it is ever scripted, the script).
2. The auditor's mint check greps each quoted heading and requires it to exist verbatim in `to-lead.md`.

## Disposition

Accepted disclosure for every instance listed above, per the maintainer's (by delegation) entry "2026-10-23 11:58:33 BST". No body edit to any merged record and no per-instance correcting RL. The remedy is owned by WK-1178 (tooling).
