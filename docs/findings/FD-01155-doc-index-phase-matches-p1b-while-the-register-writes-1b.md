---
id: FD-1155
family: finding
title: doc-index.py --phase matches the register's Phase cell against "P1b" while the register writes "1b", so the findings element reads zero
status: active
created: 2026-09-27
owner: auditor
tree: 3749db65eb29fbe95dd46e6b787960fa8386af0b
corrected_by: []
relates: [PL-1144, LG-1148, RL-1145]
---

# FD-1155 — doc-index.py --phase matches the register's Phase cell against "P1b" while the register writes "1b", so the findings element reads zero

Filed by the auditor at 2026-09-27 14:59:20 BST, on the deputy's DP-1 line of 2026-09-27 14:47:04 BST
(its (k) paragraph: *"Element 5's cause … is a spelling mismatch between an instrument and its
corpus: the Task 10 auditor files it"*). It is filed in one commit with FD-1154 to FD-1162, before
the W37 closure record cites it.

## Finding

RFC-937 §7 (k)'s report, `python3 scripts/doc-index.py --phase P1b`, prints element 5 as
`0 opened in P1b, 0 discharged, 0 unowned-decay in P1b, plus 0 unowned-decay carried in from an
earlier phase`. The zero is not a proven absence. The instrument and its corpus spell the
phase differently:

- `scripts/doc-index.py`'s `_findings_figures` keeps the rows whose `Phase` cell equals the
  report's phase id: `in_phase = [r for r in rows if r.phase == phase_id]` (`:1098` at
  `3749db65`). The id is `P1b`.
- `docs/findings/register.md` writes the Phase cell without the `P`: `1b`, `2`, `2/3/4`.
- `_phase_rank` (`:1079`) parses only `P(\d+)([a-z]*)$`. It returns `(2**31, phase)` for
  `1b`, `2` and `2/3/4`, so every row sorts last and none counts as carried in from an
  earlier phase.

So the findings element of the phase report is structurally zero for every phase the
register records.

## Evidence

- **Element 5, first count** (`LG-1148` Task 8, at `47065da5`): the instrument's line, quoted
  above.
- **Second count** (`LG-1148` Task 8, at `47065da5`). An `awk -F'|'` pass over the register's
  data rows, on the fourth cell, found 121 rows: `1b` 20, `2` 100, `2/3/4` 1. Over the 20
  rows of `1b`, with the instrument's own status rules, it found 20 opened, 16 discharged
  and 0 unowned-decay.
- **Re-read at `3749db65`**, the same predicate on this branch's register: `1b` 20, `2` 105,
  `2/3/4` 1 (126 rows; `273e3e0f` added five phase-2 rows). No cell reads `P1b` or any other
  `P`-prefixed value.
- The docstring of `_phase_rank` says that an unparseable value is *"not exercised by this
  slice's fixtures"*. The real register exercises it on every row.

Under `RL-1145` DP-5 (b), as amended, the (k) row reports both counts with their predicates
and does not pick one. This finding records the cause of the disagreement.

## Disposition

**Deferred with an owner — the lead** (the deputy, 2026-09-27 14:47:04 BST). Event: the
create-read-retire audit's first slice. The fix is the owner's choice: one normalisation in
`_phase_rank` and the matcher (accept `1b` for `P1b`), or one column convention in the
register. Elements 6 and 7's disagreements are **not** filed. The deputy rules that they are
stated as causes in the (k) row: a per-directory `INDEX.md` counted as a citer, and no
`active` date in the headers of pre-migration plans.
