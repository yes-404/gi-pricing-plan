---
id: FD-1147
family: finding
title: The verify render hides the residue-ceiling block on an unchanged verdict set, so a residue-only exit 3 says the change moved no row
status: active
created: 2026-09-27
owner: auditor
tree: b5fa806241ac9955f276125cdde2d61f39f05b69
corrected_by: []
relates: [RL-1145, PL-1144]
---

# FD-1147 — The verify render hides the residue-ceiling block on an unchanged verdict set, so a residue-only exit 3 says the change moved no row

Filed by the auditor at 2026-09-27 11:38:08 BST, on the activation branch of W37-11, as the single commit
`PL-1144` names (`:113`, *"the auditor's single commit filing C16's `FD-` register row
and essay"*). This is **C16** in `PL-1144` Scope A (`:301`) and Acceptance item 16
(`:249-254`). The decision-maker found the defect while verifying `RL-1145` (section *"A
defect found while verifying, which none of the DPs named"*) and reported it for filing.

## Finding

`scripts/_docverify.py`'s `render` ends by extending its output with
`_set_change_block(result)`. **`_set_change_block` is the only caller of
`_residue_change_block`**, and it returns early when `result.set_changes` is empty.
The early return is a one-element list that holds the `UNCHANGED:` line. So when the
verdict set is unchanged, the residue-ceiling block is unreachable, whatever
`result.residue_changes` holds.

This is wrong for two reasons. The two quantities are independent, and the exit code
already reads both.

- `VerifyResult.exit_code` returns `3` when `self.set_changes` is non-empty **or** any
  `self.residue_changes` entry is fatal. Its docstring states that a fatal residue change
  *"is the identical kind of news and sets the identical exit code"*.
- `_residue_change_block`'s docstring states why it exists: a ruled row's verdict label
  *"alone cannot report a regression into it"*. So a residue change is by design the case
  where the verdict set does **not** move. That is exactly the case the early return
  suppresses.

The result is that the render contradicts the exit code on a residue regression. It also
cannot report residue progress on any run whose verdict set is unchanged, and that is
every standing CI run on `main` today.

## Evidence

**Source, by symbol.** At `b5fa806241ac9955f276125cdde2d61f39f05b69`, the function is
`_docverify._set_change_block`. Its early `if not changes: return [...]` holds the text
*"UNCHANGED: … — the standing red, and this change moved no row."* Its last statement is
`out.extend(_residue_change_block(result))`. The line numbers are a hint only: `def` at
`:4439`, the early return at `:4449-4454`, the call at `:4474`. The blob of
`scripts/_docverify.py` is identical at `271088b0`, at `724409bf` (`main`, #819) and at
this tree: `git rev-parse <ref>:scripts/_docverify.py` gives `6fc40501` at all three. So
every reading below applies to all three trees.

**The decision-maker's probe, at `271088b0`** (`RL-1145`, *"A defect found while
verifying"*). It was built on the test suite's own `_result` pattern, `_result` in
`tests/test_doc_id_verify.py`. It gave two readings:

1. A recorded ceiling now measures 0. `residue_changes` holds one `PROGRESSED (W37-11
   record can shrink)`, and the exit is `1`. The rendered text does **not** contain
   `RESIDUE CEILING`.
2. A residue grows into a file the record does not name. `residue_changes` holds one
   `REGRESSION`, and the exit is **`3`**. The rendered text still says *"UNCHANGED …
   this change moved no row"* and does not contain `RESIDUE CEILING`.

**A second probe, built differently, by the auditor at this tree.** The first probe varies
the record and the measured residue. This one leaves every row at `EXPECTED_VERDICTS` and
substitutes `residue_changes` directly: a `VerifyResult` subclass whose property returns
one `_docid.ResidueChange` of each kind. For each case the probe calls `render` and
checks the text for two substrings, `'RESIDUE CEILING'` and `'moved no row'`:

```
PROGRESSED (W37-11 record can shrink): fatal=False set_changes=0 exit=1 RESIDUE_CEILING_in_text=False moved_no_row_in_text=True
REGRESSION (residue exceeds W37-11 ceiling): fatal=True set_changes=0 exit=3 RESIDUE_CEILING_in_text=False moved_no_row_in_text=True
```

The two probes differ in how they produce the residue change, and they agree on the
render. Neither probe is committed. The committed proof is the pair of render tests that
Acceptance item 16 requires.

**Main's CI.** `docs` workflow run `36310860577` is a `push` run at
`271088b0ef99c48156ad7e96e7043bb8a3f6b613`, conclusion `success`. The auditor read its log
with `gh run view 36310860577 --log`: 1462 lines. `grep -c 'RESIDUE CEILING'` gives
`0`, and `grep -c 'PROGRESSED\|REGRESSION'` gives `0`. The `doc-id migrate --verify`
step prints `UNCHANGED: 1 fatal row(s), matching the recorded set of 1 …`. **That absence
agrees with this defect, and for that reason it is not evidence of anything else.** On an
unchanged verdict set, the render cannot print the line whatever the residue measures.

## Consequence

- **`PL-1144` Acceptance item 6 cannot fail as written before the fix.** Before the
  census-row shrink, the standing verify must print no `PROGRESSED (W37-11 record can
  shrink)` line for the census rows. On an unchanged verdict set it can never print one.
  So a render-read check of item 6 passes whether the census rows measure 0 or not.
  `PL-1144` item 6 already accounts for this: its exit is read from
  `VerifyResult.measured_residue`, or from the render only after C16's fix lands, and
  never from the render before that (`:190-197`; `RL-1145` DP-2 amendments 3 and 4).
- **A residue-only exit 3 misreports itself.** A residue regression into a ruled row sets
  exit 3, the signal a reviewer acts on, while the only explanatory text says the change
  *"moved no row"*. A reviewer who reads the text before the code sees a contradiction and
  no cause. This is the F102 case (a new failure that cannot be told apart from the
  standing red) moved from the exit code into the text.

## Disposition

**Fix before close, owner W37-11.** C16 is a named acceptance item under `RL-1145` DP-2
obligation 2, amendment 3 (the deputy adopted it on 2026-09-27 at 11:28:23 BST). It is
**fixed in W37-11 by the code PR (Tasks 2–6), C16 / `PL-1144` item 16; the closure record
states the squash.** The exit criteria are the two render tests. The first renders an
unchanged verdict set with one `PROGRESSED` change and asserts that `RESIDUE CEILING` is
present. The second does the same with one fatal change and asserts the line, exit `3`,
and that the text no longer says the change *"moved no row"*. Each test is shown
**failing at `271088b0`** and **passing at the code PR's head**. The auditor sets this
record `closed` in place, and cites the PR, once the closure record exists.
