---
id: LG-1148
family: ledger
title: W37-11 — prove it, the instrument PR
status: active
created: 2026-09-27
owner: executor
tree: 9fe726b221f01c2055f818ea30ed84324cd84ab4
phase: P2
work: WK-697
plans: [PL-1144]
corrected_by: []
relates: []
---

# LG-1148 — W37-11 — prove it, the instrument PR

Executed task by task from `PL-1144` (`status: active`, frozen 2026-09-27), under
`RL-1145` (DP-2 (c), DP-3 (a), DP-4 (b), DP-5 (b), each with its amendments) and the
deputy's DP-1 line of 2026-09-27 11:16:34 BST. Cut from `origin/main` at
`9fe726b221f01c2055f818ea30ed84324cd84ab4` (#820, W37-11's activation). This ledger covers
**the code PR, Tasks 1–6**, on one branch (`w37-11-code`). Every task commit below is a
pre-squash branch commit of that PR. The PR's squash SHA on `main` is recorded once, in the
PRs table, when it is known. Tasks 7–14 (the docs PR and the close) are appended by whoever
executes them.

The lead's rulings on the executor's first report (2026-09-27, received after 12:05:10 BST)
bind this ledger. Q1: this ledger is created. Q2: the code PR edits the 22 instrument and
test files and the two skills. The six `docs/process/` documents and `docs/roadmap.md` are
left to their owners in the docs PR. Q3: the record's rows are written by the executor as
the W37-11 lead's instrument (`RL-1145` DP-3 amendment 5), in their own commits, and the
lead adopts or amends the row diff at review. Q4: C15 is **held** for the deputy's ruling.
The population may be derived as evidence, and no g2 per-file row is filed. Q5: F19
(`doc-id.py next` defaulting to `origin/main`) stays deferred with the lead.

## Tasks

### Task 1 — baseline and preconditions

**Step 1.** `readlink /proc/$$/cwd` printed `/home/puzhenhao1989/gi-pricing-plan`.
`git rev-parse HEAD origin/main` printed `9fe726b221f01c2055f818ea30ed84324cd84ab4` for
both, in the worktree
`/home/puzhenhao1989/.claude/jobs/66723b39/tmp/exec-w37-11/code` (branch `w37-11-code`)
and in the root checkout (`## main...origin/main`).

**Step 2, the preconditions.** Each one holds at `9fe726b2`:

- C16's register row is present. `grep -n 'FD-1147' docs/findings/register.md` returns
  `:154`, which opens *"The verify render hides the residue-ceiling block on an unchanged
  verdict set, so a residue-only exit 3 says the change "moved no row" (FD-1147; C16)"*.
- `grep -n 'OQ-1146' docs/open-questions.md` returns `:48`. The row reads *"DECIDED
  2026-09-27 — option (c): a second archived ref for the record only (`--record-ref`),
  defaulting to `--ref`, with CI passing the commit under test; a record missing at that
  ref is a refusal (exit 2), never an empty record"*.
- `RL-1145` is on `main`. `ls docs/rulings/RL-01145* | wc -l` prints `1`.

**Step 3, the baseline readings.** All were taken at `9fe726b2` on a clean tree
(`git status --porcelain | wc -l` → `0`), 2026-09-27 12:06:20 BST:

| Reading | Command, verbatim | Result |
|---|---|---|
| Docs audit | `python3 scripts/audit-docs.py; echo rc=$?` | rc `0`; `All checks passed.`; `DISCLOSED (865, at or under the W37-11 residue ceiling):` |
| Id lint | `python3 scripts/doc-id.py check; echo rc=$?` | rc `0` |
| Check-30 count (C11) | `python3 scripts/audit-docs.py 2>&1 \| grep -c '^  - check 30'` | `70` |
| Reserved count (C14) | `grep -c 'reserved (not yet materialised)' docs/INDEX.md` | `57` |
| Reference limb, first command (acceptance item 7) | `D=$(python3 -c "import sys; sys.path.insert(0,'scripts'); import _docid; print(dict(_docid.LEGACY_FORM_PATTERNS)['legacy audit path'].pattern)"); git ls-files "$D" \| wc -l` | `1` (the record) |
| Reference limb, second command | `git grep -l -F "$D" -- . ':!docs/REDIRECTS.csv' \| wc -l` | `183` |

The 183 files fall into five classes, with 0 files left unclassified. The classifier was a
path-prefix test, run in the order record, then INDEX, then frozen, then living, then
instruments:

- Frozen governed records: 150 in all. Closures 45, findings 42, plans 22, rulings 17,
  ledgers 11, research 7, rfcs 6.
- Living documents: 9 in all. `docs/process` 6, `.claude/skills` 2, `docs/roadmap.md` 1.
- Instruments and their tests: 22 in all. `scripts` 6, top-level `tests` modules 9,
  `tests/fixtures` 5, `backend/tests` 2.
- Generated `docs/INDEX.md`: 1.
- The record itself: 1.

So 150 + 9 + 22 + 1 + 1 = 183. This matches `RL-1145` DP-3 amendment 4, class by class.

**The standing verify, run as `.github/workflows/docs.yml`'s `doc-id migrate --verify`
step runs it.** `--ref` was read from `docs/process/delivery-process.core.json`
`meta.verified_against_tree` (= `0651c1e265648cbd3918adfc729ad965b83b1e0b`). The command
ran inside the `dev-commands` verify-slot wrapper, with the thread caps:
`python3 scripts/doc-id.py migrate --verify <throwaway dir> --ref 0651c1e265648cbd3918adfc729ad965b83b1e0b`.
It ran from 12:06 to 12:24:18 BST and exited `1`. Its render opens with
*"UNCHANGED: 1 fatal row(s), matching the recorded set of 1 in
`_docverify.EXPECTED_VERDICTS` — the standing red, and this change moved no row."* The one
`[FAIL]` row is (g). Its g2 reading is `classified-by-none=207`. The residue by cause is:

| Cause | Count |
|---|---|
| `cause3-legacy-path-citation` | 103 |
| `slash-compound-citation` (unassigned) | 29 |
| `unmapped-work-slice-key` | 28 |
| `cause2a-range-citation` | 15 |
| `other` | 12 |
| `cause1-foreign-frontmatter` | 11 |
| `cause4-compound-token-adjacent-uppercase` | 5 |
| `new-frontmatter-stamp-no-move` (unassigned) | 4 |
| **Sum** | **207** |

The parts sum to the whole, and the total equals the 207 of #757's squash body at
`29e7a9c`. The render prints no `RESIDUE CEILING`, `PROGRESSED` or `REGRESSION` line. This
is consistent with C16 (`FD-1147`). It is not evidence about the ceilings.

Landed in: this PR — the pre-squash branch commit that creates this file.

## PRs

| # | Branch | Squash SHA on `main` | Tasks | State |
|---|---|---|---|---|
| — | `w37-11-code` | — | 1–6 | in progress |
