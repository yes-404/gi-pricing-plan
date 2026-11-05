---
id: PL-8330
family: plan
kind: map
title: WK-1178 — register-owed.py reads the live decision text, not the superseded opening kept below it (FD-1916), SL-8331 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-05             # filed under working id 8330
owner: planner
tree: dae9637ea6f6a56f6502e9db70392cdfb2f3983d
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1916, FD-1820, FD-1165, CR-1247]
---

# PL-8330 — WK-1178: `register-owed.py` reads the live decision text (SL 8331, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It holds one slice row, SL 8331, and edits no filed plan.
> The executor's skills are `superpowers:test-driven-development`, `.claude/skills/python-test` and
> `git-hygiene`. PL 8330, SL 8331 and LG 8332 are working ids reserved by the lead. FD-1484, the
> group's other row, is split out to PL 8342 by the entry "2026-11-05 09:58:58 GMT".

## Authority

- **The order.** The maintainer's entry "2026-11-05 09:58:58 GMT" in
  `~/gi-pricing-plan.local/channel/to-lead.md`.
- **The finding.** FD-1916 (LOW, owner WK-1178), the maintainer's "2026-10-25 11:47:10 GMT", item T1
  (1). The essay's *Remedy* and *Broken-input proof the fix must carry* are the design, and this plan
  follows them. Its event: "the fix's merge with the red in row 1 shown on the base tree by its cause,
  and `register-owed.py review` re-run on the merged tree with the count quoted."
- **The triage** (`b28ba8e9454c`) §3, Slice T, notes plan review 17's skeleton item 0b relies on this
  script. The §14 review is Mon 16–Tue 17 Nov 2026: the fix is worth having before it.

## Goal

`register-owed.py` no longer lists a row because of text in a superseded opening. The owed list a §14
review reads is the true list. FD-1916 closes.

## Evidence at `dae9637e`

- `scripts/register-owed.py:102` `_REVIEW_MARKER = re.compile(r"§14")`; `:139-142` `_matches_work_id`
  searches `row.fields[2]` and all of `row.fields[4]`; `:145-146` `_matches_review` searches all of
  `row.fields[4]`; `_is_resolved` (`:125`) is prefix-based and needs no change. The essay's lines hold.
- **Run here, through the gate-2 flock:** `python3 scripts/register-owed.py review` at `dae9637e`:
  **31 owed, 11 excluded** (rc 0). The essay's 33 and "drop to 12" were at `ff976406`; **the numbers
  have moved and neither is the target.**
- **The marker, run here:** over the `|` rows of `docs/findings/register.md`, 49 match
  `supersedes[^.]{0,80}opening kept below` (case-insensitive), and **no row has the phrase "opening
  kept below" without matching that regex**, so the regex loses nothing. Of the 49, 28 have `§14` only
  after the marker, counted over the whole row (all columns, not the Decision cell, and not limited to
  the owed set). That is an upper bound, not the expected drop.
- `tests/test_register_owed.py:54` `_row(finding, work, phase, decision)`, `:40` `_parse`, `:171`
  `test_review_mode_matches_a_row_naming_the_14_review`: the form for the new tests. It loads the
  script as a module. The file is one of the 8 docs-audit pytest files (common seat brief, item 30).
- `Match`'s docstring (`:105`): no `@dataclass` here, for the loading reason it gives.

## Decision points

None open: the essay's remedy is complete, and this plan adds no choice. **Can go `active` at its mint
with no ruling.**

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's
merge tree. Items 1 and 2 apply to this plan; A1 to A7 apply to the slice.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no
   failing line except check 31 / check 32 lines naming working ids 8330, 8331 or 8332. After the
   mint, `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints
   no line that stands for a set of ids.

The slice:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists `scripts/register-owed.py`,
  `tests/test_register_owed.py`, LG 8332, and the mint's files (Write set). Nothing else.
- **A2. Red first, by cause.** LG 8332 quotes, from the slice's named base, T1 failing because row 1
  matched `review`, and T2 failing because row 1 matched `WK-B`. T3 and T4 are controls: green at base
  and head.
- **A3. Green.** `tests/test_register_owed.py` passes in full through
  `~/gi-pricing-plan.local/handover/run-small.sh`.
- **A4. The real register.** LG 8332 quotes `register-owed.py review` before and after, at named trees,
  with the owed and excluded counts, and lists each row that left. For each, it quotes the row's live
  text up to the marker, showing the live owner (the essay's "each … shown to carry its live owner
  before the marker"). **No row that names §14 before the marker has left.** The line of the event, a
  re-run at the merged tree with the count quoted, is the auditor's.
- **A5. `_is_resolved` is unchanged**, and `register-lint.py` is not edited:
  `git diff origin/main...HEAD -- scripts/register-lint.py` is empty.
- **A6. The gate.** The diff leaves `docs/` (`scripts/**`, `tests/**`), so the **full code gate, both
  halves, SOLO** (common seat brief, item 30). See G for the option.
- **A7. The closing act and the audit.** **FD closing act in the FD-1842 form, in the slice's own PR,
  by the slice's auditor:** FD-1916's `status: closed`, `relates:` gaining the slice's ids, a
  `***Resolved <date>***` paragraph naming the delivered remedy, its red, its LG and the count, the same
  on the register row, and the PR number and squash at the merge's date of record. **The LG Audit
  section, with the lead's adoption, lands in the audit's own commit**, and `docs/INDEX.md` is
  regenerated after the closing acts (common seat brief, item 17). **Order inside the slice:** the
  auditor re-runs the count after the closing act, since closing FD-1916's own row changes the register.

## Global Constraints

- **G1. One regex.** `_SUPERSEDED_OPENING` is defined once. `register-lint.py` owns it only if lint ever
  needs it (the essay; FD-1165's reason). Not now.
- **G2. The limits the essay states go in the code's docstring:** a row with no marker is read whole,
  and a live text naming §14 before the marker still matches, correctly.
- **G3. Stdlib only**, as the script is. No `@dataclass` in it (`:105`).
- **G4. Red first, by cause. No test is weakened** (common seat brief, item 13).

## Needs

No DB, no Redis, no docker, nothing on the NFR VM. Small runs only. `register-owed.py` runs through the
gate-2 flock (common seat brief, item 6).

## Tasks

### SL 8331 — `_live_text`

**The row.** WK-1178 fix slice. One `sonnet` executor. Register: FD-1916 (LOW), closing at the merge
(A7). Depends on: the maintainer's GO; a gate slot. **Size:** 1 h. SOLO gate about 2.5 h, not counted.
Merged before Thu 12 Nov 2026; still red at Wed 11 Nov 12:00 → the exception list.

**R1 — red first.** `tests/test_register_owed.py`, by the essay's three rows, with
`marker = "This supersedes the owner and event of the opening kept below."`:

- **T1** `test_review_mode_ignores_a_superseded_opening`: live "deferred with an owner: WK-A", then the
  marker, then "decays to the next CLAUDE.md §14 plan review". `select_matches(rows, "review")` is
  empty. **Red:** the row matches.
- **T2** `test_work_mode_ignores_a_superseded_opening`: same shape, the opening naming `WK-B`.
  `select_matches(rows, "WK-B")` is empty. **Red:** the row matches.
- **T3** `test_a_live_text_naming_the_review_before_the_marker_still_matches`. Control.
- **T4** `test_a_row_with_no_marker_is_read_whole`. Control.

**R2 — green.** In `scripts/register-owed.py`, beside `_REVIEW_MARKER`:

```python
_SUPERSEDED_OPENING = re.compile(r"supersedes[^.]{0,80}opening kept below", re.IGNORECASE)


def _live_text(decision: str) -> str:
    """The Decision cell above the superseded opening the register keeps below it (FD-1916).

    A row with no marker is read whole. A live text naming the target before the marker still
    matches, correctly. `_is_resolved` reads the cell's prefix and does not need this.
    """
    marker = _SUPERSEDED_OPENING.search(decision)
    return decision[: marker.start()] if marker else decision
```

`_matches_review`: `_REVIEW_MARKER.search(_live_text(row.fields[4]))`. `_matches_work_id`:
`pattern.search(_live_text(decision))`, `work_item` unchanged.

**R3 — the real register.** A4's before-and-after, in LG 8332, at named trees, through the gate-2 flock.

**G — the gate.** Full code gate, both halves, SOLO, after a re-merge of `origin/main`. **Option for the
lead:** this slice and LAST-2 (FD-1484) both touch `scripts/`, and T's code is 1 h against a 2.5 h gate.
Folding T's commits onto LAST-2's branch spends one gate rather than two, at the cost of tying a LOW to
the chain's last slice; T's PR stays separate only if the two must not wait for each other. The
09:58:58 entry says "one PL per group", so the plans stay separate either way. CI: `python`, `docs`,
`history-policy`.

### Write set

- `scripts/register-owed.py`, `tests/test_register_owed.py`.
- LG 8332 under `docs/ledgers/`.
- At the mint: the SL 8331 row in `docs/roadmap.md`, `docs/INDEX.md`, this plan's `status:`, FD-1916's
  essay and `docs/findings/register.md` (A7).

### Files shared with other groups

**LAST-2 (FD-1484):** `scripts/` generally; its plan names whether `register-owed.py` or
`register_lint`'s parser moves. Serial if so. **Safe in parallel with D, R, C, A, H, F.**

## Hand-off (not this plan's writes)

- **FD-1820 is not a slice** (the brief): "a local idsweep edit + a docs line". It stays with the lead:
  `scratch/idsweep.sh` gains the predicate, the sweep run on a ref that mints an id already minted on
  main must report a collision (the essay's red-first proof), and the mint procedure's text gains
  `git grep -n "under working id <N>" origin/main -- docs`, which must print nothing. Its closing act is
  the lead's to route. The script is local and not in the repository.
- The GO: the maintainer. The row, the mint, the gate slot and G's option: the lead. The LG: the
  executor. A7: the auditor.

## Self-review

1. **Every cite was read** at `dae9637e`, and the counts were run there. 2. **Requirement ids:** none
apply; a tooling fix. No range. 3. **No placeholder.** 4. **The red is by cause.** 5. **The essay's stale
figures are not carried:** 31, not 33, and no predicted count; A4 measures it. 6. **Calendar:** 12 Nov
2026 is a Thursday, 11 Nov a Wednesday.
