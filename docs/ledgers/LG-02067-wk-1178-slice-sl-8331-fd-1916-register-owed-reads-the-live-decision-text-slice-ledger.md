---
id: LG-2067
family: ledger
title: WK-1178 slice SL-2066 — FD-1916, register-owed.py reads the live decision text (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-07   # original date 2026-11-05, working id 8332, minted 2026-11-07
owner: executor
tree: 966f817fa707322b32e6e733e9cc88bc6318511d   # the tree of commit afe1ee99 (sl-8343-table-row-parser, the code head this was written against; base c8d8522758859d23fac5542815ccaa59c5a4b087). Corrected 2026-11-05 17:12 GMT: the field held the commit id.
slice: SL-2066
phase: P2
work: WK-1178
plans: [PL-2065]
corrected_by: []
relates: [FD-1916, PL-2065, LG-2070]
---

# LG-2067 — WK-1178 slice SL-2066: `register-owed.py` reads the live decision text

*(Minted 2026-11-07 as LG-2067 from working id 8332, in the SL-2069 batch (T folded: SL-2066 with SL-2069), with the mint tool of record `mint-repoint.py`. Plans PL-2065 (8330) and PL-2068 (8342), slices SL-2066 (8331) and SL-2069 (8343), ledgers LG-2067 (8332) and LG-2070 (8344) minted together, in that order.)*

**GO:** to-lead "2026-11-05 09:58:58 GMT"; "2026-11-05 10:36:35 GMT" (all nine plans accepted; T folded onto the FD-1484 branch and gate).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-2065, "SL-2066 — `_live_text`". No requirement id: tooling. Register: FD-1916. The commits ride `sl-8343-table-row-parser`; one gate covers both slices (LG-2070).

### Task list

1. **R1 — red first.** `731df717`: `tests/test_register_owed.py`, T1 `test_review_mode_ignores_a_superseded_opening`, T2 `test_work_mode_ignores_a_superseded_opening`; T3 and T4 are controls. Committed alone.
2. **R2 — green.** `b9214ae6`: `scripts/register-owed.py`: `_SUPERSEDED_OPENING` once, `_live_text`, used by `_matches_review` and `_matches_work_id` (the work-item cell is unchanged). `_is_resolved` is unchanged and `scripts/register-lint.py` is untouched by this slice (its change is SL-2069's).

### Gate

Runs on the executor's tree through `run-heavy.sh --over-load "2026-11-05 13:58:21 GMT"`.

**Red first, by cause, on base `c8d85227`** (the new test file copied into a detached worktree of base):

- T1: `assert [<_register_owed_under_test.Match object ...>] == []`, `Left contains one more item`: row 1 matched `review`.
- T2: the same assert shape: row 1 matched `WK-B`.
- `3 failed, 13 passed`: T1, T2 and `test_check_29_wiring_is_undisturbed` (red on base because `audit-docs.py` exits 1 on the working-id gaps and the stale INDEX, as in LG-2070). T3 and T4 are green at base.

**Green, slice tree:** `tests/test_register_owed.py`: `15 passed, 1 failed in 61.13s`; the one failure is `test_check_29_wiring_is_undisturbed`, for the audit-docs cause above.

**A4, the real register, `python3 scripts/register-owed.py review`:**

- Base `c8d85227`: `31 owed row(s), 11 matched but excluded as opening with a resolution marker`.
- Head `b9214ae6`: `11 owed row(s), 1 matched but excluded`.
- The 20 rows that left, each with the live text before the marker (a script check read `docs/findings/register.md`; none has `§14` before the marker, `bad 0`): FR-240 (F-W9-3); 03 rating shapes vs hand-authored contracts (F27); RFC-840/841 adoption pilot (F28); Error codes across the spec/code boundary (F29); Roster publishing emits a constant (F31); mypy files coverage (F33); NFR-499 rate limits (F48); `register-owed.py WK-671` finds 10 open rows … (F63); `.claude/roles/reporter.md`'s Mechanism section …; The "never end your turn with outstanding background work" rule …; RL-909's decay rule has no faithful check …; Five test fixtures are written into the real `docs/plans/` …; Check 37 reds on 95 of 95 post-migration rulings …; RFC-937 §1.5 requires the vendored manifest …; The plan's ruling-heading census …; A filed ruling that omits the `## Ruling N` heading …; A session ends leaving the shared checkout …; A guard disarmed by the very event it was written to survive; Two freeze-clause breaches on `PL-1070`; Four frozen plans state row (d)'s criterion in a superseded form. Each opens `**deferred with an owner — <the lead | the maintainer | the create-read-retire audit Work | WK-674>**` above its marker.
- The 20 that left are under the plan's upper bound of 28 (rows with `§14` only after the marker, counted over the whole row). The auditor re-runs the count after the closing act (A7).

### Audit

~~(To be written by the auditor.)~~

*(Written 2026-11-05 17:06 GMT by aud-sl8343 (sonnet, 5.5), adopted by the lead in from-lead "2026-11-05 17:08:05 GMT" ("aud-sl8343 FINAL ADOPTED"), committed 2026-11-07 in this slice's audit commit, as the slice audit of SL-2066, proposed to the lead, whose verdict it is. Scope derived from PL-2065 first (Acceptance Standard items 1–2 and A1–A7, the FD-1916 essay's *Remedy* and *Broken-input proof*), then evidenced. Object: detached worktree at `5748acc7` (tree `861047d3`), range `origin/main...5748acc7`; base `c8d85227` for the "base" figures. SL-2066 rides the FD-1484 branch and gate (the entry "2026-11-05 10:36:35 GMT", T folded), so "the slice's diff" below means its two commits, `731df717` and `b9214ae6`, both ancestors of `5748acc7` (exit 0).)*

**Scope and verdicts, PL-2065.**

| Item | Verdict | Evidence (auditor-run) |
|---|---|---|
| Plan 1, plan 2 | MET | `audit-docs.py` at `5748acc7` fails only on check 31 working-id gaps; no range line in PL-2065. |
| A1 write set | MET-BY-RECORD (fold) | The two commits change `scripts/register-owed.py` (15 lines) and `tests/test_register_owed.py` (44 lines) only (`git diff --stat 731df717^ b9214ae6`). `origin/main...HEAD` as a whole is wider because SL-2069 rides the branch, by the 10:36:35 entry. |
| A2 red first, by cause | MET | Auditor re-run: head's `tests/test_register_owed.py` copied into a detached worktree of base `c8d85227`, `-k "superseded or live_text or no_marker"`: **T1 `test_review_mode_ignores_a_superseded_opening` and T2 `test_work_mode_ignores_a_superseded_opening` fail** (`assert [<Match>] == []`, `Left contains one more item`); T3 and T4 pass (`2 failed, 2 passed, 12 deselected`). At head all four pass. |
| A3 green, full file | MET-BY-RECORD (conditional) | `tests/test_register_owed.py` at `5748acc7`: `15 passed, 1 failed in 72.09s`; the failure is `test_check_29_wiring_is_undisturbed`, which asserts `audit-docs.py` rc 0 and gets the two check-31 working-id lines (printed in its assertion). It clears at the mint; re-run the file after the mint (OWED-TO-GATE / mint). The plan said `run-small.sh`; the auditor ran it through `run-heavy.sh --over-load "2026-11-05 15:37:39 GMT"` beside the gate-1 D pytest, DB-free env, under the grant's cap, load1 about 12–13, and says so. |
| A4 the real register | MET | `register-owed.py review`: base **31 owed, 11 excluded**; head **11 owed, 1 excluded**, both reproduced. A probe over `parse_register` and the script's own predicates: base owed 31, head owed 11, **20 rows left, 0 entered**; of the 20, 0 name `§14` in the live text before the marker, 0 lack the marker, none has a live text under 40 characters; each opens `deferred with an owner — <owner>` above the marker, and the kept opening follows it (`: carry forward …`, `**Fixed** …`, or a repeat of the `deferred` text). The 20 are those the LG lists. "No row that names §14 before the marker has left": holds. |
| A5 `_is_resolved` unchanged, `register-lint.py` not edited | MET | `git diff 731df717^ b9214ae6 -- scripts/register-lint.py` is empty; `_is_resolved` is not in the diff hunks. (`register-lint.py` changes on the branch are SL-2069's, `96300754`.) |
| A6 the gate | **OWED-TO-GATE** | Folded onto the FD-1484 gate. GREEN set by import closure: `tests/test_register_owed.py` loads `register-owed.py` and `register-lint.py`, and the eight item-31 docs-audit files and `test_register_lint.py` load the scripts SL-2069 changed; more than 15 files, named in LG-2070's audit, not looped. |
| A7 closing act and audit | landed in this commit | `drafts/resolved-FD-1916.txt` and `closing-acts.patch`. **Order trap, measured:** `register-owed.py` refuses a dirty register (RL-912), so the auditor probed `select_matches` directly on the register with both closing acts applied (then reverted): `review` still lists **11 owed, and FD-1916's own row is among them**, because the FD-1842 form appends the `***Resolved***` paragraph at the end and `_is_resolved` reads the cell's prefix (`fix before close …`), which also names `§14`; the `WK-1178` list likewise keeps the two closed FD rows (142 owed), as FD-2001's row does. The count to quote after the closing act is therefore 11, with that one row in it; either accept that (the precedent form) or open the cell with the status marker. The lead's call; the draft follows the precedent. |

**What the code does, read (`scripts/register-owed.py` at `5748acc7`).** `_SUPERSEDED_OPENING = re.compile(r"supersedes[^.]{0,80}opening kept below", re.IGNORECASE)` once; `_live_text` cuts at the first match, else returns the cell whole; `_matches_review` and `_matches_work_id` search the live text, `work_item` unchanged; the docstring states the two limits (no marker: read whole; live text naming `§14` before the marker still matches). The essay's three-row broken-input proof is T1, T3, T4 plus T2 for the Work-id predicate. Plan G1–G4 hold: one regex, stdlib only, no `@dataclass`, no test weakened.

**Residual, named.** The 28-row bound in the plan (`§14` only after the marker, whole row) was an upper bound; 20 left. The marker regex's 80-character window (`{0,80}`) is the register's existing phrase length; a row whose marker is phrased differently is read whole, which is the safe direction (the owed list errs long, never short).

**Gate and merge.** OWED-TO-GATE with LG-2070: the SOLO gate, MERGE-ACK, CI by id; after the closing act and the re-merge, `register-owed.py review` re-run at the merged tree, count quoted (the essay's event).

**Proposed verdict (the lead's to adopt):** slice audit clean; SL-2066 evidenced; A3 and A6 close at the mint and the gate. Nothing unowned. Correct the `tree:` header (it holds the commit `afe1ee99…`; its tree is `966f817f…`), as in LG-2070.

### Build log

- 2026-11-05: T1–T4 `731df717`, `_live_text` `b9214ae6`, on `sl-8343-table-row-parser`.

- 2026-11-07: closed by the audit commit of the slice's PR (the audit of 2026-11-05 adopted by the lead, from-lead "2026-11-05 17:08:05 GMT"); the status was `active` through the mint (item 42).

## PRs

(Added at the PR.)
