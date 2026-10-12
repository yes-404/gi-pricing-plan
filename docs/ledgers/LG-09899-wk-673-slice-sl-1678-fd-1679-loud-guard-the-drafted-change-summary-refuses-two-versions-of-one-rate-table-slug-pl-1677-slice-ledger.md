---
id: LG-9899
family: ledger
title: WK-673 slice SL-1678 — FD-1679 loud guard, the drafted change summary refuses two versions of one rate-table slug (PL-1677), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: f7ca32ec5450d61aa6948e82fbf6262ac1ed307a
phase: P2
work: WK-673
slice: SL-1678
plans: [PL-1677, PL-1267]
corrected_by: []
relates: [PL-1677, PL-1267, SL-1678, FD-1679, SL-1503, RL-1498, RL-1538, SL-1543, FR-242, FR-237]
---

# LG-9899 — WK-673 slice SL-1678: the FD-1679 loud guard

*(Working id 9899, reserved by the lead. The id is minted at the merge turn; until then every citation of this record is by working id.)*

**GO:** the lead's from-lead entry "2026-10-12 06:05:28 BST — GO SL-1678 (WK-673, FD-1679 loud guard) → executor-sl1678 (sonnet)" (`channel/from-lead-2026-10-09.md`), citing the maintainer's (by delegation) entries "2026-10-12 05:57:57 BST" (ACK: DP-K rate_tables only, DP-G1 409, DP-G2 inside `_pins_by_slug`) and "2026-10-12 05:58:56 BST" (FD-1679 mints in the same PR) in `to-lead.md`.
**MERGE-ACK:** not yet given.

## Tasks

Base: branch `sl-1678-wk673-fd1679-guard`, worktree `.claude/worktrees/sl-1678`, cut from `origin/pl-9896-wk673-fd9895-guard` at `f7ca32ec5450d61aa6948e82fbf6262ac1ed307a` (PR #1294, the mint of `PL-1677`/`SL-1678`/`FD-1679`, not yet on `origin/main` `604ea084c96efe93f521fb9ba17738e05241e61a`). `origin/main` is merged in once #1294 lands. The activation commit is the branch's first.

### Task 0 — preconditions (`PL-1677` Task 0)

- Premise c re-read at the base: `backend/src/app/platform/rating_versions.py` `_pins_by_slug` still reads `return {ref.slug: ref for ref in Pins.model_validate(pins).rate_tables}`; premises a, b, d–i to be re-read and recorded here before Task 2.
- `gh pr list --state open` at the start: #1292, #1293, #1294 (no other writer on the write set). `to-lead.md` read to its tail: the last entry on `FD-1679` is the maintainer's (by delegation) "2026-10-12 05:58:56 BST"; nothing later rules on `pins_by_slug`, the change summary, DP-K, DP-G1 or DP-G2.

(Task 1 to 3 entries are appended below as they are done.)

## PRs

- Not yet opened (the slice PR is opened at the first gate-ready push).
