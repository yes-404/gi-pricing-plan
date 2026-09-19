---
id: RL-1078
family: ruling
title: DP-7-6 — the reserved block is a deferred allocation and must become visible to the index, not skipped by the allocator
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-19
owner: decision-maker
tree: 38033319b2654072bb8825529fc6da09f99dc788
phase: P2
work: WK-697
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1070, RL-1075, RL-1046, RFC-937, FD-1074]
---

# RL-1078 — DP-7-6: the reserved block is a deferred allocation and must become visible to the index, not skipped by the allocator

## Verified first, at 38033319b2654072bb8825529fc6da09f99dc788

This rules `PL-1070`'s **DP-7-6**, the reserved-identifier gap that `RL-1075` disclosed,
sized and expressly declined to dispose of (`RL-1075`, *"What it obliges"*, final bullet:
*"I have measured it, not disposed of it"*).

Everything below was read in worktree `agent-a4658afb041c6b641`, `git status --short` empty
at branch point, `HEAD` = `origin/main` = `38033319b2654072bb8825529fc6da09f99dc788`, with
`/usr/bin/git show <ref>:<path>` and line numbers from `grep -n` on that ref's content.
Where a second tree is named it is `a800c57`, the unmerged W37-7 branch. Clock at ruling:
2026-09-19.

**The block's two ends are written bare throughout — 1063 and 1136 — never as
family-qualified id tokens.** `RFC-937:30` gives the reason and **both of its failure modes
are live here**: the top of the block has no `docs/INDEX.md` row at all and an id token
would report dangling under check 32, while the bottom of the block *does* resolve — to an
unrelated live governed document. An id token would be wrong at each end for a different
reason, which is the defect being reported, not a way to report it.

### 1. What the block is — a deferred allocation, not a stale column

`docs/REDIRECTS.csv` carries 74 rows whose `new_path` is `docs/findings/register.md`:
legacy findings-register **rows**, which never become files. Their `new_id` numbers run
1063 to 1136 inclusive, contiguous, all of family `FD`. Predicates, runnable at any tree:

```bash
/usr/bin/git show <tree>:docs/REDIRECTS.csv > /tmp/red.csv
awk -F, '$6 ~ /^"?title:/ {print $2}' /tmp/red.csv | grep -oE '[0-9]{4}' | sort -u   # the block
awk -F, '$6 ~ /^"?title:/ {print $2}' /tmp/red.csv | grep -oE '^[A-Z]+' | sort | uniq -c
```

At this tree the first prints 74 numbers, 1063 through 1136 with no gap; the second prints
`74 FD` — the block is one family, entirely.

**Those rows have not been applied.** `docs/findings/register.md` at this tree still carries
the legacy citation forms the block is supposed to replace — `register.md:48` reads
*"WF-698 §4 surfaces (F9)"* and `:56` reads *"FR-12 (F19)"*, for the rows whose reserved
`new_id`s are the 1066 and 1074 marks. No file under `docs/findings/` bears any number in
the block: `ls docs/findings/` tops out at the `FD-01074` essay, and the five `FD-0106x` /
`FD-01074` essays that do exist are **newer, unrelated findings**, not these legacy rows.

**But the block is not inert, and must not be read as spare.** Its deferral is a maintainer
ruling of 2026-09-03, quoted verbatim inside the tool that implements it —
`scripts/doc-id.py:9906`, in the comment governing `_is_fd_canonical`:

> The essays get ids and paths now; `F<n>` stays a resolver alias to W37-11

and the same comment block states that `REDIRECTS.csv` *"still carries the pair regardless
(`assigned`/`redirect_rows` record it unconditionally, for W37-11's resolver)"*. The
code enforces it: `doc-id.py:9927` excludes every `FD`-canonical `new_id` from
`forward_id_map`, so the citation-rewrite sweep deliberately leaves `F<n>` bare.

**So the 74 numbers are allocated within the meaning of `RFC-937` §1.1 rule 1 — reserved
for named governed rows by a maintainer ruling — and their application is W37-11's.** Any
reading that treats them as unallocated, and therefore free, contradicts a maintainer
ruling and destroys W37-11's input. That reading is refused below as the fourth option it
is, not left implicit.

### 2. The two harms, measured at two trees by the same commands

```bash
/usr/bin/git show <tree>:docs/REDIRECTS.csv > /tmp/red.csv
/usr/bin/git show <tree>:docs/INDEX.md      > /tmp/idx.md
awk -F, '$6 ~ /^"?title:/ {print $2}' /tmp/red.csv | grep -oE '[0-9]{4}' | sort -u > /tmp/block.txt
grep -oE '^\| [A-Z]+-[0-9]{4}' /tmp/idx.md | grep -oE '[0-9]{4}' | sort -u > /tmp/idxall.txt
grep -oE '^\| FD-[0-9]{4}'     /tmp/idx.md | grep -oE '[0-9]{4}' | sort -u > /tmp/idxfd.txt
comm -12 /tmp/block.txt /tmp/idxall.txt | wc -l    # (i) number reuse, any family
comm -12 /tmp/block.txt /tmp/idxfd.txt  | wc -l    # (ii) mis-resolution, same family
```

| Tree | (i) any family | (ii) family `FD` |
|---|---|---|
| `3803331` (`origin/main`) | **15** — 1063 through 1077, consecutive | **5** — the 1066, 1067, 1068, 1069 and 1074 marks |
| `a800c57` (unmerged W37-7) | **16** | **6** |

**The growth is measured, not predicted.** Both trees are immutable and both figures come
from the commands above, unchanged. The sixteenth is the 1078 mark and it is an `FD`, so
between those two trees **both** harms grew by one. That pair is the whole case for the
lead's scoping constraint, and it is why a remedy scoped to (ii) alone is refused.

(i) decomposes by family, and the parts sum to the whole:

| Family of the live `INDEX.md` row | Marks | Count |
|---|---|---|
| `CR` | 1063, 1064, 1065 | 3 |
| `FD` | 1066, 1067, 1068, 1069, 1074 | 5 |
| `PL` | 1070, 1071, 1072, 1073 | 4 |
| `RL` | 1075, 1076, 1077 | 3 |
| — total | — | **15** |

The five `FD` rows are the mis-resolutions: one number naming two governed things in one
family. `RL-1075` verified the sharpest of them individually and its reading holds at this
tree — the redirect row reserving the 1074 mark names a legacy overview requirement clause,
while the live `FD-1074` is *"No SL- row exists for any slice, and no PL- carries a slice
field"*. A reader following that row's legacy citation lands on an unrelated finding.

The other ten are reuse without ambiguity of resolution, and they are **not** the lesser
harm: `RFC-937` §1.1 rule 1 is one sequence shared by every family — *"No number is used
twice"* — and `doc-id.py`'s own `find_duplicate_ids` docstring (`:465-468`) states the
consequence in terms: keyed on the bare number, never `(prefix, number)`, because *"the
number, not the prefix, is what 'no number is used twice' protects."*

### 3. Why neither instrument sees it, pinned by symbol

`compute_next` (`scripts/doc-id.py:421`) is *"`max` across all four RFC-937 §1.7 sources,
plus one"*, and those four are `scan_header_ids`, `scan_spec_bold_ids`,
`scan_roadmap_row_ids`, `scan_index_ids`. `RFC-937` §1.7 names the same four in prose
(*"every header, every spec bold-id, every roadmap row and `INDEX.md`"*). `REDIRECTS.csv`
is in neither list. **The brief's framing is correct and I confirm it: the standard and the
tool are wrong in the same place, and the fix changes both in one commit or neither.**

`audit-docs.py` check 31 cannot see it either, for two separate reasons, and both matter to
the remedy. Its duplicate clause (`:1801-1812`) iterates `_id_scope_documents()` — files
with headers — and a register row is not a file. Its contiguity clause (`:1818-1823`) reads
`docs/INDEX.md`, **where the block is absent by construction**.

### 4. The finding that disqualifies all three drafted options

`docs/INDEX.md`'s allocation at this tree is **contiguous from 0 to 1077 with zero gaps** —
1078 distinct numbers, no pair non-consecutive. Measured against check 31's own predicate,
read by symbol rather than re-typed:

```bash
python3 -c "
import sys; sys.path.insert(0,'scripts'); import _docid
ns = sorted({int(m.group(2)) for m in _docid.ID_RE.finditer(open('docs/INDEX.md').read())})
print(len(ns), ns[0], ns[-1], [(a,b) for a,b in zip(ns,ns[1:]) if b != a+1])
"
```
→ `1078 0 1077 []` at `3803331`.

Check 31's contiguity clause therefore **passes today and is load-bearing**: it fails on
*"gap in the full allocation between {lower} and {upper}"*. Now apply each drafted option:

- **(a) a fifth scanner.** `compute_next`'s max becomes 1136, so `next` returns 1137.
  `docs/INDEX.md` still tops out at 1077. The first document minted puts a
  **1078-to-1136 hole** in the full allocation and check 31 reds.
- **(c) a floor above the block's top.** Identical arithmetic, identical hole, identical
  red — and additionally a pasted constant, which `CLAUDE.md` §13's predicate clause and
  `RFC-756` both refuse, since the copy is
  what goes stale when the block next moves.
- **(b) re-point the legacy block.** Re-pointing it above the live maximum does not remove
  the hole, it relocates it: the block is still absent from `docs/INDEX.md`, so the gap
  simply opens wherever the block now sits. And re-pointing it *without* (a) is strictly
  worse than doing nothing — the allocator, still blind, would mint straight into the new
  block from 1078 upward and reproduce the identical defect within days.

**None of the three, as drafted, leaves the gate green.** The hole is not incidental to
them; it is what "reserve a block the index cannot see" means. That is the finding that
decides this row, and it is not in the draft.

### 5. Testing the draft's cross-cutting argument

The draft holds that *"two independent authorities"* foreclose moving the minted side:
`CLAUDE.md` §5's permanence rule, and `RFC-937` §1.7's *"a collision at rebase is fixed by
renumbering the unmerged item."*

**The conclusion is right; the second authority is not one.** §1.7's sentence sits inside a
paragraph about `doc-id.py next` and governs an **allocation race between two minted
documents**: two branches both take the same number, one merges, the other renumbers. Here
one side is not a minted document at all — it is a reservation row in a migration map whose
application a maintainer deferred. §1.7 says nothing about reservations, and reading it as
if it did is the *"a decision travels, its rationale does not"* failure: the sentence would
be carried onto a case it was not written for.

**`CLAUDE.md` §5 carries the conclusion by itself, and needs no help.** The 15 colliding
documents are merged, indexed and cited; their ids are permanent. The minted side does not
move. I adopt that conclusion and reject the claim that it rests on two authorities, because
a planner or executor who later discovers §1.7 does not reach the case must still find the
conclusion standing — which, on §5, it does.

## Ruled

**The remedy is (a) in substance — the allocator must see the reservation — implemented at
`docs/INDEX.md` rather than as a fifth `compute_next` scanner. (b) and (c) are refused.
So is the unlisted fourth option of releasing the block.**

### (i) The reservation becomes a row in `docs/INDEX.md`

`scripts/doc-index.py` emits every `REDIRECTS.csv` reserved allocation — each row whose
`new_id` parses through `_docid.ID_RE` and whose `new_path` is the findings register — as
an `INDEX.md` row carrying its reserved number, its family, the title the redirect row's
own `title:` field already holds, a status marking it reserved-not-yet-applied, and
`W37-11` as owner, that being where the 2026-09-03 maintainer ruling put it.

This is the whole remedy, and it is one change rather than three, because `docs/INDEX.md`
is the single artifact **all three instruments already read**:

- `compute_next` gains the reservation through `scan_index_ids`, which it already calls.
  **No fifth scanner is written and `RFC-937` §1.7's list of four sources is correct as it
  stands** — the source was never missing, the index was incomplete.
- check 31's contiguity clause sees 0 through 1136 unbroken, so §4's hole never opens.
- check 32 resolves a citation to any reserved mark instead of reporting it dangling,
  which is the second of `RFC-937:30`'s two failure modes, closed.

**Why the executor must not write the fifth scanner.** It is the change the draft
recommends and it is the one that reds the gate, for the reason §4 measures. If
implementation shows the index route cannot be built — a `Record` needs a `Header`, a path
and a body, and a register row has none of the first — the answer is a synthesised record
sourced at `docs/REDIRECTS.csv`, the same shape `scan_bold_id_rows` already uses for
requirement rows that are not files. It is **not** a silent fallback to the fifth scanner.
If the route genuinely fails, the task stops and returns here; it does not choose.

### (ii) The specification change that lands in the same commit

`RFC-937` §1.7's allocation paragraph is amended to state that `docs/INDEX.md` carries
**reserved allocations as well as materialised ones**, and that a reservation recorded in
`docs/REDIRECTS.csv` is an allocation for the purposes of §1.1 rule 1. The four-source
sentence is not renumbered to five and not otherwise altered.

`CLAUDE.md` §0 asks which of spec and code was wrong. **The answer here is neither of the
two the draft names.** §1.7's four sources are right; `compute_next`'s four scanners are
right; `doc-index.py` was wrong, by omitting from the index an allocation the corpus had
made. A spec change is still required, because §1.7 never says what `docs/INDEX.md` must
contain, and that silence is what let the omission look correct.

### (iii) Why (b) is refused

Three grounds, each sufficient.

1. **It does not satisfy the lead's binding constraint on its own.** (b) heals the 15 and
   leaves the allocator blind; §4 shows the blind allocator walks straight into the
   re-pointed block. Stopping (i) growing is (a)'s work, in every world.
2. **The block is not W37-7's to move.** Its content and its deferral are a maintainer
   ruling of 2026-09-03 and its application is W37-11's. `docs/process/document-ids.md:152`
   gives me decision points, not scope; that file's own table routes a scope question to
   the maintainer. A decision-maker re-pointing 74 rows of another slice's ruled input on
   its own authority is precisely the overreach my charter names.
3. **It is causally downstream of (a), so "one commit" is wrong for it.** The re-pointed
   numbers must come from a fixed allocator, or they are hand-picked — the hand-minting
   `RFC-937` forbids. (a) must therefore land first. Bundling them inverts the order.

### (iv) Why (c) is refused

It stops the growth and teaches the allocator nothing: the floor is a constant, the next
reservation reintroduces the identical defect, and the constant is the copy that goes stale
(`RFC-756`). It also opens §4's hole.
Refused on the draft's own reasoning, which I adopt, plus §4's, which the draft lacks.

### (v) Why releasing the block is refused

Not on the ballot, and reached on the evidence, so it is refused explicitly rather than
passed over. Because no block id is borne by any file, index row or register row today, it
is available to read the `new_id` column as vestigial and blank it, whereupon nothing is
reused and the 15 stand as correct. **That reading is wrong**: §1 quotes the maintainer
ruling that put those pairs there for W37-11's resolver, and the code that preserves them.
Blanking the column would destroy W37-11's input to make a gate green. Recorded here so the
argument is not rediscovered and acted on by someone who reaches only its first half.

### (vi) The 15 already minted are not this slice's to heal

They are on `main`, they are permanent under `CLAUDE.md` §5, and healing them means moving
W37-11's ruled input — (iii) ground 2. After (i) lands they are a **closed set that cannot
grow**, which is the property that makes deferring them safe and is exactly what deferring
them was unsafe without.

They are therefore a disclosed class, not silence, and the disclosure carries its own
predicate: the (i) and (ii) commands of §2, re-runnable at any tree. Whether that class
becomes a `FD-` row, whose owner it is, and whether it is discharged in W37-11 or accepted,
is **the lead's** under `CLAUDE.md` §12 — a verdict, not a decision point. I have ruled the
gap; I have not disposed of the residue, for the same reason `RL-1075` did not.

**What this ruling does not decide**: the precedented mechanism for a class that must be
visible but non-fatal (`RL-1046` §B's *disclosed by count, does not set the exit code*) may
or may not be needed for the 15 once they appear twice in the index. That is an
implementation question the executor raises if it arises, and a verdict question if it must
be ruled — not a silent choice at the keyboard.

## What it obliges

- **W37-7's executor**, at `PL-1070` Task 16: implements (i) and (ii) in one commit, spec
  and code together. Does not write the fifth `compute_next` scanner. Does not touch
  `docs/REDIRECTS.csv`. Re-derives §2's two predicates at the tree branched from and again
  after, records both with their trees in the slice ledger, and regenerates `docs/INDEX.md`
  rather than hand-editing it.
- **The lead**: adopts, amends or rejects this ruling; then writes `RL-1078` into DP-7-6's
  `Resolved by` cell. That edit is the lead's, not this role's
  (`docs/process/document-ids.md:152`). Separately, gives the §(vi) residue class its
  verdict and its owner.
- **The planner**: Task 16's Step 3 as drafted offers the executor a choice between three
  options and its Step 4 expects *"a non-zero exit naming the offending reservation"*.
  Neither matches what is ruled. Task 16 needs rewriting against (i) and (ii) before it is
  dispatched. Its ETA basis also no longer applies.
- **This ruling deliberately does not decide**: the disposition, owner and home of the 15
  existing collisions (the lead's); whether `RFC-937`'s reserved-allocation clause should
  also govern future reservations of other families (the maintainer's, and no reservation
  of another family exists — every one of the 74 is `FD`); and anything about W37-11's
  scope beyond naming it as the block's owner of record.

## Acceptance — the violation that must become detectable

**The violation: a number reserved in `docs/REDIRECTS.csv` is minted again by
`doc-id.py next`, and nothing reds.** That is the class this ruling closes, and it is the
class — not the instance — that must become checkable. A test asserting that `next` returns
1137 proves only that a number was changed.

- **A test that derives the reservation and the allocation and compares them.** It reads
  the reserved set out of `REDIRECTS.csv` and the allocated set out of `docs/INDEX.md`, and
  fails when a reserved number is absent from the index. *Violation: on constructed input,
  a `REDIRECTS.csv` carrying a reserved mark that the generated index omits — and the test
  must red.* Pinned by symbol throughout, never by a pasted 1136 or a re-typed `FD-[0-9]+`
  literal: `doc-id.py:9919`'s `_is_fd_canonical` already parses `new_id` through
  `_docid.ID_RE` and compares the captured family group, and its own comment gives the
  reason a re-typed literal is refused. A pasted bound is a tautology that survives the
  block moving under it.

- **A test that check 31's contiguity clause is armed against this specific hole.**
  *Violation: an index whose allocation skips a reserved block — construct one in a
  `tmp_path` copy and check 31 must print "gap in the full allocation".* This is the
  failure §4 measures and the one the draft's own recommendation would have shipped, so it
  is the one worth arming. Built on constructed input, not by mutating the real tree.

- **Shown red before this ruling is applied, not after.** The executor demonstrates both
  reds on deliberately broken input and pastes the failing output into the slice ledger. A
  check that has never printed a failure has not been tested (`CLAUDE.md` §13).

## Identifier disclosure — 2026-09-19

**This record takes 1078, which `doc-id.py next` gave it. That number collides twice, and
I tried to avoid the second collision, failed, and record the failure because it is §4's
own mechanism proving itself against me.**

1. **Against the reserved block.** `python3 scripts/doc-id.py next` returned **1078** at
   `origin/main` = `3803331`, and `docs/REDIRECTS.csv` reserves that mark for a legacy W9
   register row. Taken knowingly, as `RL-1075` took 1075 and for the same reason: every
   mark below 1137 collides equally, the lead's policy of 2026-09-19 is that ids stand as
   minted, and choosing above the block by hand is the hand-minting the process forbids.
   Counted with its scope, it is the **sixteenth** instance against `3803331`'s 15. **It is
   the first minted after the defect was ruled**, which is the strongest available argument
   that (i) must land before many more documents are filed, and it is offered as that
   rather than excused.

2. **Against an unmerged sibling.** `next` reads a committed ref through
   `compute_next_at_ref`, so it is blind to sibling branches, and **`a800c57` already
   carries `FD-1078`** — *"Two freeze-clause breaches on PL-1070, and the gap that nothing
   catches a spawn against a draft plan"* — verified in that tree's `docs/INDEX.md`. That
   is `RFC-937` §1.7's own case and its own remedy is *"a collision at rebase is fixed by
   renumbering the unmerged item."* Both items are unmerged, so whichever merges second
   renumbers. **This record does not pre-empt that, because it cannot.**

3. **Why it cannot — measured, not reasoned.** This record was first written as 1079,
   precisely to step over `a800c57`'s 1078 before the rebase rather than after it. On a
   branch from `3803331`, `python3 scripts/audit-docs.py` then returned exit 1 with:

   ```
   check 31: gap in the full allocation between 1077 and 1079
   ```

   **Check 31's contiguity clause forbids renumbering ahead of a rebase**, because the
   number being stepped over is not on the branch's own base. §1.7's remedy is therefore
   available only *after* the other item merges, never before — and the id was moved back
   to 1078 for that reason. This is §4's finding arriving from the opposite direction, on
   the first document written after it was ruled: any attempt to hold a number out of
   `docs/INDEX.md`, whether a 74-row reservation or a single-number courtesy, reds check 31.
   It is recorded here because a reader who takes only §4's conclusion would not predict it,
   and because the next person to try the same courtesy should find it already measured.

**So: at merge, whichever of this record and `a800c57`'s `FD-1078` lands second renumbers,
under §1.7, and it is the lead's call which that is.** Renumbering this record is cheap
while it is unmerged and I will do it on request.
