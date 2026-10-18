---
id: RL-8122
family: ruling
title: RL-1793 is a duplicate mint of working id 8076 and is retired; RL-1755 is canonical (the correction for the ruling; PL-1794 is corrected by RL-8124)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-18
owner: decision-maker
tree: 3421b26b4cb7b622f9af55ca3e32ba8383e8ea4d
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1793
relates: [RL-1793, RL-8124, PL-1766, RL-1755, FD-8123]
---

# RL-8122 — RL-1793 is a duplicate mint of working id 8076 and is retired; RL-1755 is canonical (the correction for the ruling; PL-1794 is corrected by RL-8124)

## How this was ruled

- **The ruling is the maintainer's (by delegation)**: the entry "2026-10-18 22:50:32 BST — the
  duplicate-mint anomaly ruled" in `~/gi-pricing-plan.local/channel/to-lead.md`, item 2. That
  file is local, so the part relied on is quoted: *"PL-1794 and RL-1793 → `status: retired` with
  `corrected_by:` naming a correcting record, filed in D24 (a new RL, `corrects: [PL-1794,
  RL-1793]`, reason "duplicate mint of working id 8077/8076; canonical PL-1766/RL-1755"). Front
  matter only; bodies untouched (frozen records)."*
- **Why two correcting records, not one.** The entry names one RL with a list. `corrects:` is a
  scalar: `scripts/_docid.py` `_opt_str_field` returns nothing for a non-string, and check 34 in
  `scripts/audit-docs.py` fails a `corrected_by:` entry whose target's `corrects:` is not the
  frozen file's own id. So the correction is split by target: this record (`RL-8122`) corrects
  `RL-1793`; `RL-8124` corrects the other. Each cites the other. The lead ruled the split on
  2026-10-18 and the mint waits on the maintainer's word.

## The anomaly

Working id 8077 was minted twice: `PL-1766` (#1325, `status: active`) and `PL-1794` (#1338,
`status: draft`). Working id 8076 likewise: `RL-1755` (#1319, active) and `RL-1793` (#1338,
active). Both pairs were read at `origin/main` 84b0ff5765e55bc8edd139cd22bb57cd474de807.

The bodies are **identical apart from id re-points and the Minted provenance line**. Measured with
`diff` of the text after the front matter: `PL-1794` against `PL-1766` 38 diff lines, `RL-1793`
against `RL-1755` 14 diff lines. Every hunk is one of: the heading id; the `*(Minted … as PL-1766 /
RL-1755 …)*` line that only the canonical record carries; a cross-reference written as the unminted
working id in one and the minted id in the other (`RL 8076` against `RL-1793`, `PL 8077` against
`PL-1794`); the activation block's placeholder dates and `PL-____` in `PL-1794` against the filled
ones in `PL-1766`. No substantive clause differs.

## Ruled

1. **`PL-1766` and `RL-1755` are canonical**: first minted; `PL-1766` is active.
2. **`PL-1794` and `RL-1793` are retired** as duplicate mints of working ids 8077 and 8076. Their
   front matter gains `status: retired` and `corrected_by:` naming the correcting record; **their
   bodies are not edited** (frozen records).
3. **Citations.** Nothing outside `docs/INDEX.md` and the two records' own bodies names `PL-1794`
   or `RL-1793` at that tree, so no living cite needs re-pointing.

## What it obliges

- `RL-1793` front matter: `status: retired`, `corrected_by: [RL-8122]`; nothing else changes.
- `FD-8123` carries the process failure (the mint step did not refuse an already-minted working id).

## Acceptance — the violation that must become detectable

- *Violation: a retired duplicate still reads as live.* `grep -n '^status:' docs/plans/PL-01794-*.md
  docs/rulings/RL-01793-*.md` prints `status: retired` twice.
- *Violation: the correction is not linked back.* Each frozen file's `corrected_by:` names a record
  whose `corrects:` is that file's id; `python3 scripts/audit-docs.py` check 34 passes.
- *Violation: a frozen body was edited.* `git diff origin/main -- <the two files>` shows front-matter
  lines only.
