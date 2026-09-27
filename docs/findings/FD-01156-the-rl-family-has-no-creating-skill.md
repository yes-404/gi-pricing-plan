---
id: FD-1156
family: finding
title: The RL- family has no creating skill; rulings are born from the decision-maker's charter alone
status: active
created: 2026-09-27
owner: auditor
tree: 3749db65eb29fbe95dd46e6b787960fa8386af0b
corrected_by: []
relates: [PL-1144, LG-1148, RL-1075]
---

# FD-1156 — The RL- family has no creating skill; rulings are born from the decision-maker's charter alone

Filed by the auditor at 2026-09-27 14:59:20 BST, on the deputy's DP-1 line of 2026-09-27 14:47:04 BST
(item 1: *"The gap is a finding, filed by the Task 10 auditor with the closure record"*).
It is filed in one commit with FD-1154 to FD-1162, before `LG-1148`'s (j) row for Ruling
cites it and before the W37 closure record does (condition 1 of the deputy's ruling of
11:16:34 BST).

## Finding

RFC-937 §7 (j) asks for *"one new item per family born through its skill with a number from
`doc-id.py next`"*. The Ruling family has no skill that creates it. `.claude/skills/README.md`'s
`Creates` column names no skill for `RL-`. Rulings are created from
`.claude/roles/decision-maker.md` alone: its Owns clause says *"A ruling is one `RL-` file
under `docs/rulings/`, with an id from `python3 scripts/doc-id.py next`"*.

The deputy ruled (j)'s Ruling row **discharged in substance** on this ground (option (b)): the
item was created by the governed instrument the repository has for the family. That is the
decision-maker's charter, which is the procedure for `RL-`. The item took its number from
`next`, and `doc-id.py check` gave rc 0 at its creating commit. The row records the creating
instrument as *"the decision-maker role file"*. The gap itself is this finding: every other
discharged document family has a creating skill in the `Creates` column, and Ruling does not.

## Evidence

At `3749db65`, on a detached copy:

- **The `Creates` column.** Over the two tables in `.claude/skills/README.md` whose header row
  ends `Creates` (`:115` and `:147`), 33 data rows carry the column. They name `ADR-`,
  `CR- kind: review`, `CR- kind: work` and `FD-`, the requirement and `OQ-` rows, `LG-`, `PL-`,
  `RS- kind: spike`, and a Reference `SKILL.md`. **None names `RL-`**; 25 cells read `—`.
  Predicate: an `awk -F'|'` pass over the rows after each `Creates` header, reading the last
  cell and testing `/RL-/`. It read `rows=33 RL=0`.
- **The family is not empty.** `git log --diff-filter=A --name-only --format= 71f5a22..3749db65 -- docs/rulings`
  lists 8 `RL-` files created since the migration merge: `RL-1075`, `RL-1076`, `RL-1077`,
  `RL-1078`, `RL-1138`, `RL-1140`, `RL-1142` and `RL-1145`.
- **(j)'s item.** `RL-1075` was created at `38033319` (2026-09-19). Its commit says the
  rulings were *"filed by the decision-maker from its role file"*, and `doc-id.py check` gave
  rc 0 at that commit (`LG-1148` Task 9, row 10).

## Disposition

**Deferred with an owner — the lead** (the deputy, 2026-09-27 14:47:04 BST). Event: the
charter investigation's first slice (RFC-937 §8). The fix is the owner's choice. The options
are a creating skill for `RL-`, or a declared row in the `Creates` column saying that the
decision-maker's charter is the creating instrument. Option (c), recording Ruling as owed, was
refused: the family has eight real members on `main`.
