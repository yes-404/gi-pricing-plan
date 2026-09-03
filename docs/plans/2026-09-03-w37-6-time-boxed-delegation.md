# W37-6 — the maintainer's time-boxed delegation, 2026-09-03

**Issued** 2026-09-03 by the maintainer. **Filed** the same day by the lead, on the
maintainer's own instruction that *"nothing below is in force until that PR is merged"* —
so this record is the instrument, not a note about one. Work item **W37-6**, phase 2.

**Window: eight hours from `2026-09-03T00:07:32Z`, so it expires at `2026-09-03T08:07:32Z`.**
The timestamp is this record's own filing time, read at the moment of writing rather than
carried from an earlier command, because a stamp fetched once and pasted later is how
`eta.md` drifted 4h31m while its body was rewritten
([`NT-0004`](../notes/0004-a-reference-that-resolves-only-for-the-writer.md)).

**It amends nothing in `CLAUDE.md` §12.** It delegates the maintainer's standing
reservations for the window and no longer. §12's text is untouched, and every reservation
below returns to the maintainer when the window closes.

## 1. Delegated to the decision-maker

**NT-0019 §1/§4 amendments needed to reach a completing, green run** — owner values, scope
markers, stamp-set membership, exemption dispositions, and template body shapes
(`docs/_templates/`).

Ruled as **dated sibling records in the pattern of today's**, not as edits to this one.

Two conditions on each ruling:

- **It cites the cell or §1 sentence it reads from.** Not a summary of it, and not a
  paraphrase in quotation marks — a citation names the file and the line it was taken from.
  Quoting accurately from one document while attributing to another is the same defect as
  inventing the words, and harder to catch because the string is genuinely findable.
- **It prices the option not taken.**

**Two options with no cell to read from is a halt, not a coin-flip.** That case is reserved
(§3) and stops the window if it blocks the critical path.

## 2. Delegated to the lead — the W37-6 go-ahead, on a mechanical gate

**All six, or none.** The gate is mechanical by design: each condition is checked by
running something, not by judging it.

| # | Condition |
|---|---|
| 1 | The auditor's **independent instrument** reports `migrate()` **completes** on a snapshot at the quiet tree, with the write trace **summing by family** to the leaf plan's expected count |
| 2 | **check 37 reds 0** on the fully migrated snapshot, F90 slice merged |
| 3 | **Every `register-owed.py W37-6` row dispositioned** — discharged, disclosed, or deferred **by name** |
| 4 | The re-ask **under 300 lines** at that tree, `SLOT`s 0–3 filled, **§9 recommends go** |
| 5 | **No open branches** at the tree |
| 6 | **A `git revert` of the migration commit is proven on the snapshot to restore the tree byte-identical** |

**Condition 6 is the one that makes this delegable at all**, in the maintainer's own words.
A one-way irreversible write is not a thing anyone should authorise on delegated authority;
a write proven reversible is. It is therefore not a formality and not satisfiable by
argument — it is satisfied by performing the revert on the snapshot and comparing.

**If all six hold**: sign §10 of the re-ask
`on delegated authority, 2026-09-03, gate 1–6 verified at <tree>`, run the migration, land
it as a PR, merge it. **Then stop.**

**The Work close of W37 is not delegated.** Do not start W37-7 or any later slice.

## 3. Reserved — halts the window if it blocks the critical path

- `CLAUDE.md` amendments.
- **Work or Phase close acceptance.**
- Any deletion **outside the 20 tombstones §4 step 4 names**.
- Anything touching **repository settings or controls**.
- **Installing any external skill or agent.**
- **A PR by any author other than `yes-404`.**
- **A gate condition that fails twice.**
- **A decision the decision-maker finds no cell for.**

## 4. Halt protocol

**Triggers**: any reserved item blocking the path; the eight hours elapsing; or CI red on
`main` that cannot be cleared in one PR.

1. **Merge or close every green PR whose merge needs nothing from the maintainer.**
2. **Commit or stash every worktree**, `git worktree prune`, and **verify `git status` clean
   in each**.
3. **Write the handover** in the shape of
   [`2026-08-20-w5-worker-handover.md`](2026-08-20-w5-worker-handover.md) — final state, the
   tree, open PRs **by number**, the reserved decision **with its options priced**, and the
   **resume command per agent** — and **commit it to `main`**.
4. `shutdown -h now`.

**A handover written and not committed is the failure the W5 record exists to prevent.**
Step 3's commit is the step, not the writing.

## 5. Reporting

**Status goes to the `docs/roadmap.md` W37 row and to `register-owed.py`, not to chat** —
the maintainer reads the tree on return. **One line in the handover per hour elapsed**:
tree, PRs merged, what changed hands.

## Acceptance Standard

**This record is accepted when it is merged**, because the maintainer conditioned the whole
delegation on that merge: *"nothing below is in force until that PR is merged."* Until then
the lead holds no delegated authority and the decision-maker holds none either.

### Acceptance — the violation that must become detectable

*Violation: any action taken under this delegation before this record is merged.*

*Violation: a ruling filed under §1 that cites no cell, or that names no priced alternative.*

*Violation: the migration run with any of the six gate conditions unverified, or verified by
argument rather than by execution — condition 6 above all.*

*Violation: the window's expiry passing without the halt protocol running to step 4.*

*Violation: a handover written and not committed to `main`.*
