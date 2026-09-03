# W37-6 — the extended window's second fail, and the handover (2026-09-03)

**Filed** 2026-09-03 by the lead, under delegation §8.3's rule that on a second fail the
handover is **committed as the first act of the halt, not its last**. The commit is the step,
not the writing.

**The maintainer authorised an early call**: *"if the resolver PR with both halves isn't green
by 20:15, call it a second fail early and write the handover with the 379 in it rather than a
rushed run."* **It is called at `16:50 BST`, three and a half hours early**, because the
grounds are wider than the resolver PR and no path to a passing gate by `21:00 BST` exists.

**Tree: `e5e20d6`.** All governance for this window is merged; nothing is uncommitted.

## 1. The call, and why it is not the resolver's fault

**Six of the nine NT-0019 §7 rows fail at `0de529e`, and one of them is content corruption
rather than metadata.** The resolver PR was on course — 167 → 0, bucket (iv) 0 unresolved,
`was:` 354/354 — and it is **not** what stopped this. What stopped it is that the gate widened
to sixteen rows at `16:20 BST` and **eleven of those rows had never been measured**. Measured,
they fail.

**This is the third window to halt rather than ship a bad one-way commit, and the third time
the gate found something no one knew was there.** The pattern is now the finding: see §7.

## 2. §7(a)–(i) as measured — the auditor's figures, at `0de529e`

Tree for every row: `0de529e`, migrated into a disposable snapshot by the preserved
instrument. Un-migrated control tree from the same archive, never migrated.

| item | verdict | figure |
|---|---|---|
| **(a)** one family per file, zero `none` | **PASS** | 465 = 465, `none` row **absent**. `plan 119 / ruling 107` — a **pre-registered** prediction, confirmed |
| **(b)** `doc-id.py check` | **FAIL** | 77 failures, **all `noncontiguous`**; duplicates **0**, `id != filename` **0** |
| **(c)** `doc-index.py --check` byte-stable | **PASS** | `OK (byte-stable)`, exit 0 |
| **(d)** the id/path grep returns nothing | **FAIL** | **12 of 13** alternatives non-zero |
| **(e)** no padded id in prose | **FAIL / ambiguous** | 2021 literal; **36** excluding path context, mostly the standard documenting itself |
| **(f)** `VR-DST-1` unchanged | **FAIL literal / PASS on intent** | 104 → 127 against `8f5d57d`; **127 → 127 across the migration itself** |
| **(g)** diff hunks neither header nor citation-token | **FAIL** | ≤ 1187 lines, and **391 mangled requirement citations, control 0** |
| **(h)** full gate green | **FAIL** | `audit-docs.py` exits **1** on the migrated tree — **547 failures** |
| **(i)** every §5 H row closed by a named commit | **SCOPE CORRECTION — see §5** | not measured |

**Two clauses of (b) pass and one fails.** Recorded because a single "77" hides that: one of
its zeros is real evidence and the other is not.

### §7(d), one row per alternative, both `was:` readings

**The FIELD reading is the ruled one and is the larger number wherever they differ** — the
substring reading **hides real hits** on three alternatives (`NT-00` 32→35,
`\bF[0-9]{2}\b` 1330→1340, `docs/audit/` 291→293). Counts are matching lines / files.

| alternative | substring | **field (ruled)** |
|---|---|---|
| `NT-00` | 32 / 14 | **35 / 15** |
| `F-W[0-9]` | **0 / 0** | **0 / 0** |
| `\bF[0-9]{2}\b` — *excluded from the zero requirement, disclosed* | 1330 / 172 | **1340 / 174** |
| `wf-0[0-9]` | 327 / 116 | 327 / 116 |
| `Ruling [0-9]+` | **74 / 22** | **74 / 22** |
| `ADR-0[0-9]{3}` | 37 / 18 | 37 / 18 |
| `(FR\|NFR\|OQ\|DEP)-[A-Z]+-[0-9]+` | 72 / 33 | 72 / 33 |
| `W[0-9]+[a-z]?-[0-9]+` | 1 / 1 | 1 / 1 |
| `docs/plans/2026-` | 66 / 45 | 66 / 45 |
| `docs/audit/` | 291 / 86 | **293 / 86** |
| `docs/notes/` | 118 / 46 | 118 / 46 |
| `docs/adr/` | 34 / 20 | 34 / 20 |
| `\.claude/notes/` | 1 / 1 | 1 / 1 |

**`Ruling [0-9]+` = 74. The bare count, as instructed** — the maintainer's words were *"I want
its count, not a recommendation."* **No reading and no option list accompanies it.** It is a
second deferral decision and it is the maintainer's.

**Only `F-W[0-9]` returns nothing, and its zero is the one that most needs a control** — it is
the single alternative that could be silent because it never matches rather than because the
corpus is clean.

## 3. The finding that is not metadata — 391 mangled requirement citations

**`git grep -nE '\b(FR|NFR|OQ|DEP)-[0-9]+/[0-9]+'` — migrated: 391. Un-migrated control: 0.**

The mechanism: a compound citation like `NFR-RATE-13/14` names **two** requirements in
shorthand. `_rewrite_citations` rewrites the first and **leaves `/14` orphaned**, so the
sentence now names one real requirement and one meaningless fragment. From
`.claude/roles/lead.md`:

```
-  close the hand-compiled owed list **lost NFR-RATE-13/14** (F41) …
+  close the hand-compiled owed list **lost NFR-775/14** (F41) …
```

**Verified independently by the lead at `origin/main`**, both sides:

```
git grep -cE '\b(FR|NFR|OQ|DEP)-[0-9]+/[0-9]+' origin/main        → 0 files   (control clean)
git grep -ohE '\b(FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+/[0-9]+' | wc -l    → 423 occurrences
git grep -lE  '\b(FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+/[0-9]+' | wc -l    → 159 files
```

**So 423 compound citations across 159 files are the population at risk, and 391 of them come
out mangled.** Examples: `FR-723/48`, `NFR-775/14`, `OQ-814/16`, `OQ-832/2`, `OQ-902/3/4`,
`OQ-907/2/3/5`.

**Why nothing would have caught it.** It changes what documents **say**, not where they point.
**Nothing dangles**, so condition 7 — under either its old or its redefined predicate — is
silent. **The mangled form matches no §7(d) alternative**, so §7(d) is silent. It is visible
only to §7(g), whose figure nobody had computed until today.

**This is the most serious thing found in three windows**, because it is the one class that a
`git revert` restores but a reader cannot detect: a sentence that reads plausibly and cites a
requirement that was never meant.

## 4. `audit-docs.py` on the migrated tree — and the vacuous passes matter more than the failures

```
cd <migrated snapshot> && python3 scripts/audit-docs.py   →  EXIT=1, FAILED (547)
```

110 of the 547 are check 28 — every migrated plan loses its `YYYY-MM-DD-` prefix, **which is
what the migration is supposed to do**, so `docs/plans/README.md` §Naming and check 28 are an
un-updated H row. 23 are check 32.

**The summary lines are the worse half, and they would have gone unread had the exit code been
0:**

```
0 requirements defined across 8 specs
0 open questions, all mirrored
journey citations: 0 endpoints, 0 functions, all declared
0 of 0 §10 mirror rows carry their register status
check 37: 1 document(s) checked in scope, 0 exempt as verbatim-migrated (`was:`), 1 shape-checked
```

**Post-migration, `audit-docs.py`'s spec parsers find nothing**, and every check that reports
green does so **over an empty population** —
[`NT-0007`](../notes/0007-context-bound-measures-cap-not-discipline.md) at scale. **And check
37 sees 1 document with 0 `was:` exemptions against the 292 it reported pre-migration**, which
is §6's `was:` breakage arriving from a second direction.

## 5. Two scope corrections, both against the lead

**(i) is W37-10's, not W37-6's, and §8.5 records it wrongly because the lead framed it
wrongly.** The map plan's own coverage table reads *"§5.2 → W37-6 (M rows, the roadmap
restructure, the process vocabulary) **and W37-10 (H rows)**"*, and W37-10's acceptance is
*"every §5.2 H row is named by a commit"* — **which is §7(i) verbatim.** NT-0019 §8 agrees by
sequencing: S2 is the migration PR, S3 is *"every remaining H row."*

**Verified by the lead at `origin/main`.** The lead put "(a)–(i)" to the maintainer having
already been corrected once on this same clause, and the maintainer ruled on the lead's
framing. **§8.5's nine rows should be eight**, and the correct split is:

| items | owner |
|---|---|
| **(a)–(h)** | **W37-6** |
| **(i)** | **W37-10** |
| **(j)–(k)** | **W37-11** |

**This needs the maintainer's confirmation rather than a lead correction**, because §8.5 is a
filed ruling: if (i) was ruled into W37-6 knowingly, that stands.

**And the S2-scoped reading of (i) fails anyway**: one of NT-0019 §8's named S2 H rows —
*"`audit-docs.py` parsers and roots"* — **is demonstrably not done**, proven by §4 above.

## 6. `was:` is right 3 times in 393 — and condition 2's pass rests on it

| at `0de529e`, stamped documents with a `was:` field | |
|---|---|
| total | **393** |
| names a **real pre-migration path** — true provenance | **3** |
| names **the file's own new path** — no provenance at all | **261** |
| names a path that never existed either way | **129** |
| — of those, names a **real post-migration file** | **90 — resolves and lies** |
| — of those, names nothing | 39 |

`docs/closures/CR-00017-phase-1a-exit-demo.md` carries
`was: docs/ledgers/LG-00030-w5-wf-01-driven-end-to-end.md` — a real 233 KB W5 execution
ledger, an entirely different document. **Twenty closure records claim provenance from that
one ledger.**

**Two bugs, and the author guarded exactly half.** `_write_document_drafts` (`:5786`) writes
`was:` **before** `_rewrite_citations` (`:6000`) sweeps, and the sweep has no `was:`
exclusion — producing the 261. The split-source collision compounds it into the 129.
`doc-id.py:6001-6004` says, in its own words: *"A `was:` written before the sweep would be
rewritten into the new path, destroying the one field that records where the file came from"* —
and that comment sits above `_stamp_regenerated_readmes`, **which defers to post-sweep for
exactly this reason. `_write_document_drafts` does not, and it writes the other ~390.**

**The consequence for the gate: check 37's exemption keys on `was:`.** The **"enforced
population is 0"** result recorded as **condition 2's evidence** — accepted once by the
maintainer with a disclosure under Ruling 96 — is granted on a field that is right 3 times in
393. **Condition 2's pass rests on a broken field.**

**A denominator to reconcile, not a disagreement.** The executor measures **354** documents,
354 correct after its fix, 351 of 354 corrupted on `main`. The auditor measures **393**, 3
correct. **They agree exactly on the 3 that were good.** The executor's population excludes
`was: ~` template nulls and covers `*.md` only. **Neither was told to change its number**;
which population the acceptance test wants is a question about the test.

## 7. The pattern across three windows — and it is now the finding

| window | what the gate caught | what would have shipped |
|---|---|---|
| 1st | `none` = 110 — `docs/audit/` not dissolved | a corpus failing §7(a) |
| 2nd | **36** dangling links, after all six conditions passed | broken citations in a one-way commit |
| 3rd (this) | **377** broken links · **391** mangled citations · `was:` 3/393 · `audit-docs` exit 1 | **documents that say the wrong thing** |

**Each defect was invisible to the gate as it stood, and each was found by widening a
predicate rather than by running the gate again.** Condition 7 alone has been redefined once
and had four blind spots measured in it. **The gate is not converging on the corpus; the
corpus is revealing that the gate's predicates were narrower than their names.**

**The load-bearing observation for whoever plans next:** every one of these was found by
someone measuring **a different thing from what the check measured** — full-scope instead of
indexed population, "broken" instead of "resolves to a deleted path", `^was:` as a field
instead of `was:` as a substring, per-alternative instead of aggregate. **A check's name is
not its predicate, and only the predicate is enforced.**

### 2.1 The link figure reconciled — 377, and neither 376 nor 379

**Relayed** (the auditor's measurement, not the lead's own run — see §12's rule):

```
379  post-migration docs/-citing broken links, as first counted
        = 158 (deleted target) + 221 (never existed)
 -3  non-link artefacts: `](work:`, `](...)`, `](…)` -- inside backticks, not links
+1   a REAL broken link the `was:` SUBSTRING skip was hiding
----
377  condition 7's figure under its new definition
```

**Measured directly rather than derived**, both sides at `0de529e` with the tightened
predicate:

```
UN-MIGRATED CONTROL: 1568 targets examined,  70 broken,   0 citing from docs/
MIGRATED:            1551 targets examined, 453 broken, 377 citing from docs/ (142 files)
```

**The control's `docs/`-citing figure is 0, so all 377 are introduced** — no subtraction, and
the total-versus-introduced ambiguity that produced the 376/379 confusion cannot recur in this
form. The 70 pre-existing are all `.claude/skills/**` prose and docstrings, none under `docs/`.

**Two of the three artefacts were the scanner matching its own description** — gate condition
7's own text, and the handover describing the instrument. The third is a Python type signature
in a table cell. **The tightening — a link target inside an inline code span is not a link —
cannot drop a real link**, because a real link with a backticked label has an even backtick
count before the `](`. Proven by enumeration: 11 items dropped, every one a placeholder or
signature inside backticks, 8 of them in Python docstrings outside `docs/` which is why
neither the lead nor the auditor had seen them.

**The lead's own contribution to this figure was an error.** The lead published a table reading
`376 = 158 + 221`, which sums to **379**; the maintainer caught it. The lead's subsequent
hypothesis — that the gap was the 3 artefacts — was right about the 3 and **missed the +1**.

### 2.2 Which condition-7 blind spots survive the redefinition

**Relayed.** Two retired, two survive — and **neither survivor is a condition 7 defect any
more**:

| blind spot | state |
|---|---|
| **1 — scope** (`git ls-files` read before `git add -A`) | **RETIRED.** A defect of the old instrument's population |
| **4 — deleted ≠ broken** | **RETIRED, absorbed into the definition.** The 221 are inside the 377 by construction |
| **2 — `was:` substring not field** | **SURVIVES, but in §7(d)'s predicate, not condition 7's.** Under the redefinition there is no `was:` skip at all. In §7(d) it changes three alternatives |
| **3 — semantic** (Ruling 101 §101.3) | **SURVIVES**, as the maintainer classified it. A link resolving to the wrong index section still resolves |

### 2.3 §7(h)'s frontend half — NOT MEASURED, owner named

**§13 admits no silence, so this is a verdict rather than an omission: not measured, owner the
executor's PR CI.** The Python half is green — **relayed**: 3010 passed, 2 skipped, 1 xfailed,
plus six static checks. The frontend half (`pnpm install`/`lint`/`type-check`/`test`/`build`)
on a **migrated** tree could not be landed with margin, and `CLAUDE.md` §11 records that a
Python-only "gate" has been green here while the frontend was red. **It is not recorded as a
pass.**

## 8. What is merged and in force

| PR | commit | what |
|---|---|---|
| #677 | `4528ac0` | **§8** — halt overridden, window extended to `23:00Z`, fail count reset, handover-first |
| #679 | `0de529e` | **Ruling 98's implementation** — a maintainer's dated decision migrates `RL-`, plus the RUF001 escape and a by-symbol predicate |
| #680 | `8c66f67` | **Ruling 101** — the undetermined citation resolves to the split's index entry; bucket (iv) 0 by construction |
| #681 | `e5e20d6` | **§8.5** — §7 (a)–(i) as gate conditions 8–16, §7(d) amended, the pre-registered prediction filed before its measurement |

**Nothing is uncommitted. No branch holds unmerged work except the resolver's**, below.

## 9. The resolver's work — real, measured, and not the reason for the halt

On `w37-6-split-source-resolver`, **not merged, not gate-complete**, all figures the
executor's own at its own tree:

- **Dangling links 167 → 0**, using the repo's committed `_dangling_links` predicate.
  **Measured with the retired deleted-target predicate**, so the **221 moved-citer** class is
  not covered by it.
- **Bucket (iv): 0 unresolved.** 356 citations rewritten to `docs/<family>/INDEX.md#…`,
  0 index-section violations.
- **`was:` 354 of 354 correct**, against 351-of-354 corrupted on `main`.
- **§7(a) `none` = 0** on the real migrated corpus.
- **Red-then-green done for both new checks** — the `was:` byte-identity test reddens when the
  exclusion is neutered; the index-section check reddens on three distinct broken inputs.

**The open technical question, unresolved at the halt:** the fix is a **fourth token form**
scoped to the cited file's directory with `posixpath.relpath`. That is sound for a **moved
target**. The lead's reading — put to the executor and unanswered when the halt was called —
is that **a token map cannot reach a moved citer**, because there the target never moved, so
there is no old path to key on and what changed is the **base** the relative path resolves
from. `_repoint_relative_links` (`:5150`) already handles both halves — its own docstring
names them — and **has exactly one caller, the five-README path at `:5518`.**

## 10. Three corrections the executor made to the lead's figures, all measured

- **The OQ collision population is 8 ids, not 1.** `OQ-OVR-11` is claimed by **three** records
  (`OQ-539`, `OQ-545`, `OQ-551`), not two, and seven more ids are multiply claimed
  (`OQ-OVR-12`, `OQ-DATA-11`, `OQ-MODEL-10/-11/-23/-24`, `OQ-GOV-8`). **The guard warns rather
  than raises**, naming every claimant and holding them out of the rewrite, **so it does not
  block a run.** Disclosed population, not a fix.
- **"137 citations in the disputed class" is not reproducible under any predicate.** The
  executor's census, instrumented inside the real resolver during a real run: **(i) 96,
  (ii) 0, (iii) 27, (iv) 356 — total 479, determined 123.** The sum closes. **It refused to
  reconcile to 137 and was right to**; 137 was unsourced and the lead passed it on as a figure.
- **A premise of Ruling 101 does not hold.** Clause 1 says `docs/<family>/INDEX.md` as though a
  split source had **one** family. **Three sources split across families** —
  `_discover_plain_plans` emits a whole-file `PL-` for a plan while `_discover_lettered_rulings`
  emits an `RL-` per `## Ruling N` heading **inside that same plan**. The executor placed the
  section in the **sorted-first target family** as a documented **placement** rule, with the
  section listing every target from every family, **so nothing about which document a citation
  meant is decided** — which preserves Ruling 101's own grounds. **It needs the maintainer's
  ruling and has not had it.** `_MIGRATION_DIFF_FAMILY_INDEXES` was added explicitly rather
  than silently extending Ruling 68's six-class enumeration.

### 10.1 Halt completion — every worktree, clean or pushed (appended 2026-09-03, 17:06 BST)

**The halt protocol's worktree clause discharged, one line each.** Every worktree was
`git status` clean **and** on a branch whose tip is on the remote, before removal — the
condition is both, not either, because a clean worktree on an unpushed branch is the
durability failure this halt was ordered to avoid.

| worktree | branch | tip | state at removal |
|---|---|---|---|
| *(shared checkout)* | `main` | `e5e20d6` | clean; not removed |
| `wt-ho` | `docs/w37-6-second-fail-handover` | `3d29170` | clean, pushed — **this record** |
| `wt-r102` | `docs/w37-6-ruling-102-verify-instrument` | `cb3ad85` | clean, pushed, **deliberately unmerged** |
| `w37-6-exec` | `w37-6-split-source-resolver` | **`61f4a97`** | clean, pushed — **the resolver work** |
| `w37-6-auditor3` | `audit-r98-rebase` | `5f32970` | clean; **no remote and none needed** — its content is `0de529e`, merged as #679 |
| `w37-planner` | `worktree-w37-planner` | `8c0793a` | clean, pushed; PR #678 closed unmerged, superseded by a direct recommendation |
| `agent-a225faa49dba12dea` | `w37-split-source-citations` | `2868b71` | clean, pushed — the dead predecessor's WIP, superseded by `w37-6-split-source-resolver` |
| `agent-a5894b03d1bda7b8d` | `w37-6-ruling-98-impl` | `33df3c4` | clean, pushed; superseded by #679's merge |

**One live violation was found and fixed rather than reported.** `w37-6-split-source-resolver`
existed **only** in a worktree — three commits and two modified files, no remote ref. The lead
pushed the committed tip from the shared checkout, which touches nothing in another agent's
working tree, and **did not commit the two modified files on the executor's behalf**: acting
inside another member's worktree has previously discarded that member's tracked edits. The
executor committed and pushed them itself as `61f4a97`.

**What that branch carries, and why the next session reads it before anything else** — the
executor's own measurements, at its own tree: the split-source resolver with both new checks
proven red-then-green, **dangling links 167 → 0**, **bucket (iv) 0 unresolved** with 356
citations routed to index entries, **`was:` 354 of 354 correct** against 351-of-354 on `main`,
and **§7(a) `none` = 0**. It is the first thing the next session builds on.

## 11. Open, with an owner or a named absence — §13 admits no silence

| item | state |
|---|---|
| **391 mangled compound citations** | **no owner.** The largest unfixed defect; 423 at risk across 159 files |
| **§7(b) 77 noncontiguous** | **no owner.** Became a gate row at `16:20 BST` |
| **`audit-docs.py` 547 failures / vacuous parsers on the migrated tree** | **no owner.** An un-updated S2 H row |
| **The 221 moved-citer links** | executor's, **mechanism disputed** (§9) |
| **`was:` 393 vs 354 denominator** | both measurements stand; **the test needs deciding** |
| **Condition 2's pass resting on `was:`** | **maintainer's** — a filed acceptance now resting on a broken field |
| **Ruling 101's cross-family placement** | **maintainer's** (§10) |
| **§7(i)'s owner** | **maintainer's** — §8.5 says W37-6, the map plan says W37-10 (§5) |
| **`Ruling [0-9]+` = 74** | **maintainer's** second deferral decision. The bare count is §2 |
| **§7(e) and §7(f) both ambiguous** | two readings each, both recorded, neither picked |
| **F95's register row stale** | fourth row overtaken by a merged decision (cf. F77, F90, F92) |
| **F96's mechanism gap** | open; #679 fixed its two live instances only |
| **8 multiply-claimed OQ ids** | disclosed, warns, does not block |
| **"Ruling 68 class-6 ratification" and "the lettered-ruling nested-span floor"** | **resolve to nothing in `docs/`** — dropped from any load count until cited |

## 12. What the lead got wrong this window, for the record

Recorded because §13's standard is that scope is derived and evidenced rather than recalled,
and because **every one of these was caught by an agent rather than by the lead**:

1. **"§7(a) is the bar; (b)–(k) at W37-11's close"** — wrong; withdrawn in §8.5. It had already
   produced a wrong instruction to the auditor that §7(b)'s 77 were "evidence only".
2. **"(a)–(i) are W37-6's"** — still wrong: **(i) is W37-10's**, and the maintainer ruled on
   this framing (§5).
3. **The ASCII-apostrophe ruff fix** — would have silently deleted typographic-apostrophe
   matching from a predicate stated as content-general. **Refused by the auditor before
   application.**
4. **"CI is green on the Ruling 98 branch"** — CI had **never run** on it; no PR, no run, absent
   from the last 200 runs.
5. **The `was:` defect classified second-kind** — it is **first-kind**, 90 instances that
   resolve and lie. Refuted on measurement after the lead asked to be attacked.
6. **A table published with `376 = 158 + 221`** — which sums to **379**. Caught by the
   maintainer; the lead had all three numbers in one message and did not check them.
7. **"137 in the disputed class"** and **"`OQ-OVR-11` claimed by `OQ-812` and `OQ-818`"** — both
   unsourced and both wrong; the executor refused to reconcile to either.
8. **The 167 and Ruling 101's 171 relayed as one class** — they are different populations, and
   **141 of the 167 are single-target moves Ruling 100 §2.3 leaves untouched.** Had that stood,
   141 determined citations would have been routed to an index entry.

**The common shape: the lead's errors are all relays** — a figure or a scope restated without
re-deriving it. Amendment 2 exists for exactly this and it caught six of the eight.

## Acceptance Standard

**This record is accepted when it is committed to `main`** — delegation §8.3 makes the commit
the halt's first act, and §4 of the delegation makes the commit the step rather than the
writing. **It binds nothing about the next window**, which is the maintainer's to open.

### Acceptance — the violation that must become detectable

*Violation: a run started from any tree while §7(b), (d), (g) or (h) fails, on the reading that
those rows are "close enough".*

*Violation: the 391 mangled compound citations treated as a citation-token class and therefore
excluded from §7(g)'s "neither header nor citation-token" requirement.*

*Violation: `was:` accepted as fixed on a probe that only tests whether the path exists — all
90 of the resolving-and-lying fields pass such a probe.*

*Violation: condition 2 re-recorded as MET without disposing of the fact that check 37's
exemption keys on `was:`.*

*Violation: §7(i) measured as W37-6's, or as W37-10's, without the maintainer's confirmation
of which — §8.5 and the map plan disagree.*

*Violation: any figure in this record carried into the next window without its tree, or
re-derived from this record rather than from the corpus.*
