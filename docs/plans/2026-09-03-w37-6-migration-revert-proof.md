# W37-6 gate condition 6 — the migration commit is proven revertible, 2026-09-03

**Executed** 2026-09-03 against condition 6 of
[`2026-09-03-w37-6-time-boxed-delegation.md`](2026-09-03-w37-6-time-boxed-delegation.md)
§2: *"A `git revert` of the migration commit is proven on the snapshot to restore the tree
byte-identical."*

That record states why this one exists rather than an argument: **condition 6 is the one
that makes the delegation delegable at all.** A one-way irreversible write is not something
to authorise on delegated authority; a write *proven reversible* is. The instrument's own
danger notice records what `scripts/doc-id.py`'s `migrate()` is —
`_write_document_drafts` applies each write directly with `Path.write_text` in a loop,
`migrate()` wraps none of it in `try`, and the deletion pass follows the write loop. So the
condition is discharged by **performing the revert and comparing**, never by reasoning about
whether a revert would work.

**Verdict: the revert restores the tree byte-identically. Condition 6 holds at
`15ed00d0f005a5348753f2665175033143b1e4b1`.** Twice, on two independently built snapshots.

## 1. Trees, and what each figure was measured at

Every figure below is measured on a **disposable snapshot**, never on a checkout. No
`migrate()` in this record ran against the shared repository, this worktree, or any tracked
tree. The snapshots were built by
`~/gi-pricing-plan.local/drafts/w37-6-slot3-harness/mksnap.py`, whose jobs-path assertion and
refusal of `HEAD` by name were used as written and not relaxed.

| Thing | Value |
|---|---|
| Corpus and code source | `origin/main` = `15ed00d0f005a5348753f2665175033143b1e4b1` |
| Snapshot A | `/tmp/w37-6-revert/jobs/snap001` |
| Snapshot B | `/tmp/w37-6-revert/jobs/snap002` |
| A pre-migration commit | `55e19e9a6068b1e4485a834f39915fdd4bc16a6a` |
| A migration commit | `5f1ca43746bff0082df2d1ff0e9d0183d8b49d92` |
| A revert commit | `95fb78c85b38de47546ac8bc86bff8232ef72372` |
| B pre-migration commit | `7d17551fb0fd0cd7c2dcd92d5bcba5ec6d0ab5e5` |
| B migration commit | `9489c389daf606ca3259d7b4e25e97af2843dc5d` |
| B revert commit | `269fb677a7849c3593296798c268ab78d8f7e06b` |

Snapshot build predicate, verbatim and runnable, once per snapshot:

```
python3 ~/gi-pricing-plan.local/drafts/w37-6-slot3-harness/mksnap.py \
  <this worktree> /tmp/w37-6-revert/jobs/snapNNN 15ed00d0f005a5348753f2665175033143b1e4b1
```

## 2. The migration that was reverted was a real one

`migrate()` ran **to completion** on each snapshot — it returned a `MigrateResult` rather
than raising, so the body reached its return.

Run A predicate: `python3 family_trace.py /tmp/w37-6-revert/jobs/snap001` (the same harness,
unmodified). Run B predicate: `python3 /tmp/w37-6-revert/outside_check.py
/tmp/w37-6-revert/jobs/snap002` (§5).

| Figure | Run A | Run B |
|---|---|---|
| `result.files_written` | 1092 | 1092 |
| `result.files_deleted` | 204 | 204 |
| `result.warnings` | 0 | 0 |
| write events traced | 1402 | — |
| migration commit `git show --stat` | 1132 files changed, 45545 insertions(+), 39198 deletions(-) | — |

The migrated tree object was **`f2bbbbc898cdd8e81d950838ce2d990044fd0d18` in both runs** —
`git rev-parse <migration commit>^{tree}` in each snapshot. Two independent runs from the
same source producing one tree hash is a determinism result for `migrate()` at this tree; it
is a by-product of running the proof twice, not the condition.

**Deltas against the harness README's `32fc63c` baseline are corpus-sized, not structural.**
`_rewrite_citations` 1082 → 1086 and `_write_document_drafts` 290 → 292 moved because slices
added documents; the mechanism set is unchanged and `RS` is still 2. That reading is the
README's own rule and belongs to gate condition 1, not to this one — it is recorded here
only so a reader does not mistake the movement for a finding this record suppressed.

## 3. Instrument 1 — `git diff <pre-migration sha> HEAD`, run after the revert

Predicates, verbatim, run inside the snapshot:

```
git diff 55e19e9a6068b1e4485a834f39915fdd4bc16a6a HEAD | wc -c
git diff --name-only 55e19e9a6068b1e4485a834f39915fdd4bc16a6a HEAD | wc -l
git rev-parse 55e19e9a6068b1e4485a834f39915fdd4bc16a6a^{tree} HEAD^{tree}
git status --porcelain --ignored | wc -l
```

| Measurement | Snapshot A | Snapshot B |
|---|---|---|
| `git diff <pre> HEAD` bytes | 0 | 0 |
| `git diff --name-only <pre> HEAD` lines | 0 | 0 |
| pre-migration tree object | `90ee12ff602bdeea5344c2f55941e600754b0b39` | `90ee12ff602bdeea5344c2f55941e600754b0b39` |
| post-revert `HEAD` tree object | `90ee12ff602bdeea5344c2f55941e600754b0b39` | `90ee12ff602bdeea5344c2f55941e600754b0b39` |
| `git status --porcelain --ignored` lines | 0 | 0 |

The **tree-object equality is the stronger form of the empty diff**, and it is recorded
because it says more: an identical recursive tree hash means the same path set, the same
blob content, and the same **file mode** for every tracked entry. An empty `git diff` alone
would not have carried the mode.

## 4. Instrument 2 — a full-tree digest, which cannot fail the way instrument 1 fails

**`git diff <ref> HEAD` reports tracked files only.** On a freshly migrated tree the newly
created drafts — which is exactly where the migration's writes land — are untracked and
therefore invisible to it. Instrument 1 alone would report an empty diff over a tree
carrying a migration write that landed in a gitignored path. So the second instrument is not
git-based at all.

`/tmp/w37-6-revert/digest.py` walks the snapshot with `rglob("*")`, skips only `.git/`, and
records one line per entry: **every regular file with its sha256, every symlink with its
target, and every directory** — tracked, untracked or ignored alike. Predicate:

```
python3 /tmp/w37-6-revert/digest.py /tmp/w37-6-revert/jobs/snapNNN <out.tsv>
diff <pre.tsv> <post-revert.tsv>
```

| Measurement | Snapshot A | Snapshot B |
|---|---|---|
| digest entries, pre-migration | 1754 | 1754 |
| digest entries, post-migration | 1835 | — |
| digest entries, post-revert | 1754 | 1754 |
| `diff pre.tsv post-revert.tsv` | empty, exit 0 | empty, exit 0 |

**The digest is line-for-line identical**, so every path, every file's sha256, every symlink
target and every directory is restored. Directory rows matter on their own: git does not
track empty directories, so a revert could in principle leave `docs/rulings/` behind as an
empty husk that instrument 1 could not see. It did not — `ls docs/rulings` after the revert
reports `No such file or directory`.

### File count — the predicate, not just the number

```
find /tmp/w37-6-revert/jobs/snapNNN -path '*/.git' -prune -o \( -type f -o -type l \) -print | wc -l
```

Regular files **and symlinks**, everything under the snapshot except `.git/`, with no regard
to whether git tracks or ignores them.

| Point in the cycle | Snapshot A | Snapshot B |
|---|---|---|
| pre-migration | 1541 | 1541 |
| post-migration | 1632 | — |
| post-revert | **1541** | **1541** |

The post-migration row is in the table on purpose: **a count that never moves proves
nothing.** 1541 → 1632 → 1541 shows the instrument responding to the migration and then
reporting the restoration, rather than reading 1541 because it was measuring something the
migration does not touch.

### The bridge between "the commit is reverted" and "the tree is restored"

`git status --porcelain --ignored` reported **0 lines** immediately after the migration
commit in both snapshots. Nothing was left untracked, ignored or unstaged, so the commit
captured the migration's entire filesystem effect — which is what makes reverting the commit
equivalent to restoring the tree. Had `migrate()` written into a gitignored path, that line
count would have been non-zero and this record would say so.

**One item of instrument residue was removed before committing, and it was not the
migration's.** Loading `scripts/doc-id.py` by `importlib` creates `scripts/__pycache__/`,
which the repository's `.gitignore` ignores; it appeared as the single `!!` line in
`git status --porcelain --ignored` after the run. It was deleted before `git add -A` in both
snapshots. It is disclosed rather than silently dropped, because it is the one thing that
would otherwise have made the digest comparison fail for a reason unrelated to the
migration — and because a reader checking the ignored-file count needs to know that the zero
above was reached by removing something, not by nothing being there.

## 5. Writes outside the snapshot root — measured, not assumed

Both instruments are rooted at the snapshot, so **a write to an absolute path outside it is
invisible to both.** `/tmp/w37-6-revert/outside_check.py` closes that gap for run B: it
wraps `Path.write_text`, `Path.open`, `builtins.open` (write modes) and `Path.unlink`,
resolves every target, and reports those not under the snapshot root.

```
python3 /tmp/w37-6-revert/outside_check.py /tmp/w37-6-revert/jobs/snap002
```

```
returned MigrateResult; files_written 1092 files_deleted 204 warnings 0
write/unlink targets recorded (incl. write_text's inner open): 3007
distinct resolved targets: 1298
targets NOT under /tmp/w37-6-revert/jobs/snap002: 0
```

The 3007 deliberately double-records — `Path.write_text` calls `Path.open("w")` internally,
and this probe, unlike `family_trace.py`, does not suppress the inner call. That is correct
here: the question is *which paths were touched*, not how many events occurred, so
over-recording is the safe direction. The harness README's fourth trap is about the event
*total*, which this probe does not claim.

## 6. What this proof would NOT have caught

Stated rather than left implied, because the two examples the lead supplied were both real
and both about an instrument's blind spot rather than about a wrong number.

1. **`git diff --name-only <ref>` sees tracked files only.** Instrument 1 could not, on its
   own, have caught a migration write to a gitignored path. §4's digest and the
   `--ignored` status count are what cover it — and the second instrument is not a variant
   of the first, which is the property that matters.
2. **A `Path.write_text` trace misses `_write_redirects`, which uses `Path.open("w")`.** Both
   probes used here wrap `Path.open` and `builtins.open` as well, so `_write_redirects`
   appears — it is the `1 _write_redirects` row in run A's mechanism table. Neither probe
   wraps `os.open`, `os.replace`, `os.rename`, `shutil.*`, or any write issued below the
   Python level. §5's "0 targets outside the snapshot" is therefore a statement about the
   four wrapped APIs, not about every possible write. Instruments 1 and 2 are *not* limited
   this way — they compare the resulting tree, however it was written — so the residual
   exposure is confined to writes landing **outside** the snapshot root through an unwrapped
   API.
3. **Neither instrument sees file metadata beyond content, symlink target, and (for tracked
   files) mode.** Modification times, ownership, extended attributes and hardlink identity
   are outside both. Nothing in `migrate()`'s observed behaviour manipulates them, but this
   record does not claim they were restored.
4. **The proof is scoped to one tree and one corpus.** It says a `git revert` of a migration
   commit produced at `15ed00d0f005a5348753f2665175033143b1e4b1` restores that tree. A later
   change to `scripts/doc-id.py`, or a corpus change that alters what `migrate()` writes,
   is outside it — as is any migration commit that is *not* a single commit capturing a
   clean working tree, since §4's bridge is what makes the revert equivalent to the
   restoration.
5. **It says nothing about whether the migration is correct** — only that it is undoable. A
   migration that corrupts the corpus and a migration that improves it are equally
   revertible, and condition 6 asks only the second question.
6. **It says nothing about reverting after further commits land on top.** Both runs reverted
   the migration commit while it was `HEAD`. A revert against a later `HEAD` can conflict,
   and that case was not exercised.

## 7. Reproducing this

```
python3 ~/gi-pricing-plan.local/drafts/w37-6-slot3-harness/mksnap.py <worktree> \
    /tmp/w37-6-revert/jobs/snapNNN 15ed00d0f005a5348753f2665175033143b1e4b1
cd /tmp/w37-6-revert/jobs/snapNNN
git rev-parse HEAD                                   # the pre-migration sha
python3 /tmp/w37-6-revert/digest.py "$PWD" /tmp/pre.tsv
python3 ~/gi-pricing-plan.local/drafts/w37-6-slot3-harness/family_trace.py "$PWD"
rm -rf scripts/__pycache__                           # instrument residue, §4
git status --porcelain --ignored | grep '^!!'        # must be empty: no ignored writes
git add -A && git commit -m migration
git status --porcelain --ignored | wc -l             # must be 0: the commit caught it all
git revert --no-edit HEAD
git diff <pre-migration sha> HEAD | wc -c            # must be 0
git rev-parse <pre-migration sha>^{tree} HEAD^{tree} # must print the same hash twice
python3 /tmp/w37-6-revert/digest.py "$PWD" /tmp/post.tsv
diff /tmp/pre.tsv /tmp/post.tsv                      # must be empty
find "$PWD" -path '*/.git' -prune -o \( -type f -o -type l \) -print | wc -l
```

`digest.py` and `outside_check.py` live beside the harness they extend, outside the
repository, for the reason the harness README already records: **the deciding property is
reads versus writes.** `digest.py` only reads and could be committed; `outside_check.py`
runs `migrate()` and must not be, and splitting the pair across the boundary would leave the
committed half with no explanation of what it was for.

## Acceptance Standard

Condition 6 is discharged when **both** instruments report restoration on a disposable
snapshot after an actually-executed `migrate()`, `git revert` pair, and the record states
what neither instrument could have seen. Both reported; §6 states the gaps. **This record
does not accept anything** — it discharges one mechanical gate condition and reports the
result. Whether the six conditions together license the migration is the lead's read under
the delegation §2, and the W37 Work close remains the maintainer's.

### Acceptance — the violation that must become detectable

*Violation: condition 6 recorded as satisfied on the strength of `git diff <ref> HEAD`
alone. That command reports tracked files only; on a migrated tree the newly created drafts
are untracked and invisible to it, so an empty diff is compatible with an unreverted write.
A second instrument that cannot fail the same way is required, and a file count taken with a
git-based predicate is not one.*

*Violation: a file count offered without its predicate, or offered only at the endpoints. A
count that reads the same before and after a migration is measuring something the migration
does not touch; the post-migration value (1632 here) must be shown to move.*

*Violation: `migrate()` run against any checkout — the shared repository, a worktree, or any
tracked tree — or `mksnap.py`'s jobs-path assertion or its refusal of `HEAD` relaxed to make
a run convenient. Detectable as any snapshot path in this record's evidence that is not
under a `jobs/` directory and named `snap*`.*

*Violation: instrument residue (`scripts/__pycache__/`) removed from a snapshot without the
removal being disclosed, so that a reported zero ignored-file count reads as "the migration
wrote nothing ignored" when it means "something was deleted first".*

*Violation: this record cited as evidence that the migration is safe, correct, or approved.
It establishes revertibility at one named tree and nothing else.*
