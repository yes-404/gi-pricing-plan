# NT-0019 §7 — an independent second measurement of the corpus (2026-09-03)

**What this is.** A second, independent measurement of the `docs/notes/0019-one-id-per-document.md`
§7 acceptance rows, run by the auditor in its own worktree with its own commands, against the
same corpus the second-fail handover measured. It is **not** a review of
`scripts/doc-id.py`'s implementation. Ruling 102 §1 makes the acceptance standard an
instrument; this record exists so that the instrument's figures have something to disagree
with that was not derived from the instrument.

Filed under `CLAUDE.md` §13. Every figure below carries its tree, its corpus and the predicate
it counted with, runnable as written. Nothing here is a verdict: the four verdicts and the
merge are the lead's.

## 1. Method, and where it could fail the same way

**Trees.** Two snapshots of `0de529e` taken with `git archive`, extracted to a temporary
directory, each made a git repository of its own and committed. One is migrated with
`python3 scripts/doc-id.py migrate --repo-root <snapshot>` run from `origin/main` at
`e97b97a`; the other is never migrated and is the control. `scripts/doc-id.py` is byte-identical
at `0de529e` and `e97b97a`, verified with `diff -q`, so the migrating instrument is the same one
the handover used. No real checkout was migrated. Every row was also re-measured on a second
pair of snapshots at `e97b97a`; where that changes a figure it is said so.

**Where my method and the instrument's could fail the same way.** Both run the same
`doc-id.py migrate`, so **no row below is an independent check of the migration itself** —
only of what the migration produced. A defect in `migrate` that both my predicates and the
instrument's predicates are blind to stays invisible to both. The place this bit is §7(d), and
§3 below is what came of asking the question anyway.

**Reproducibility caveat, and it is load-bearing for the instrument.** In the migrated
snapshot the probes below are run after `git add -A`. Without it the git index still describes
the pre-migration tree and `git ls-files` returns the wrong population. This is not
hypothetical — see §4.

## 2. The nine rows, mine beside the handover's

Handover column: `docs/plans/2026-09-03-w37-6-second-fail-handover.md` §2, at `0de529e`.
Mine: the snapshot pair described above, same tree.

| row | handover | mine | agree? |
|---|---|---|---|
| (a) one family per file, zero `none` | PASS — 465, `plan 119 / ruling 107`, no `none` | PASS — 465, `plan 119 / ruling 107`, no `none` row | yes, exactly |
| (b) `doc-id.py check` | FAIL — 77, all `noncontiguous`; dup 0; `id != filename` 0 | FAIL — 77 `noncontiguous`, 0 duplicate, 0 filename mismatch, exit 1 | yes, exactly |
| (c) `doc-index.py --check` byte-stable | PASS — `OK (byte-stable)`, exit 0 | PASS — `OK (byte-stable)`, exit 0 | yes, but see §5 |
| (d) the id/path grep returns nothing | FAIL — 12 of 13 alternatives non-zero | FAIL — 12 of 13 non-zero, and **four figures I cannot reproduce** | direction yes, figures no — §6 |
| (e) no padded id in prose | FAIL/ambiguous — 2021 literal, 36 excluding path context | FAIL — 2042 occurrences, 77 on a path-context filter of my own | direction yes, neither figure reproducible — §7 |
| (f) `VR-DST-1` unchanged | FAIL literal / PASS on intent — 104 → 127; 127 → 127 across the migration | 104 at `8f5d57d`; 127 control; 127 migrated | yes, exactly |
| (g) diff hunks neither header nor citation-token | FAIL — ≤ 1187 lines; 391 mangled citations, control 0 | 391 reproduced exactly; **plus 216 mangled finding ids, control 0** — §3 | 391 yes; the row is wider than reported |
| (h) full gate green | FAIL — `audit-docs.py` exit 1, 547 failures | FAIL — exit 1, **548** failures, denominators collapse as reported | direction yes, count off by one — §4 |
| (i) every §5 H row closed by a named commit | scope correction, not measured | not measured — out of scope, and see §8 | yes |

**Six of nine agree.** The three that do not are (d), (e) and (h), and in every case the
disagreement is about a predicate that is not written down rather than about the corpus.

## 3. The finding: the token-boundary defect also mangles finding ids, and §7(d) goes green because of it

**Not previously recorded.** `git grep -n 'F-WK' origin/main -- docs/ .claude/` returns nothing,
and the handover's only two mentions of `F-W` are the §7(d) row and the note that its zero
needs a control.

Predicates, in the migrated snapshot after `git add -A`, with
`FILES=$(git ls-files | grep -v REDIRECTS.csv)`:

```bash
git grep -nE 'F-WK-[0-9]' -- $FILES | grep -v 'was:' | wc -l    # 216 lines, 66 files
git grep -nE 'F-W[0-9]'   -- $FILES | grep -v 'was:' | wc -l    # 0
```

and in the un-migrated control, the same patterns with no pathspec:

```bash
git grep -nE 'F-WK-[0-9]' | wc -l                     # 0
git grep -nE 'F-W[0-9]' | grep -v 'was:' | wc -l      # 214 lines, 57 files
```

**Mechanism.** `F-W11-1-3` becomes `F-WK-952-1-3`: the rewrite matched the work key `W11`
inside the finding id. It is the same class as `NFR-RATE-13/14` becoming `NFR-775/14` — a
rewrite matching inside a longer identifier — on a different token family. In shipped code, at
`backend/src/app/main.py:80`:

```
control : # (W11 Task 1.4, F-W11-1-3 — the function has existed since W9-2 with no
migrated: # (WK-952 Task 1.4, F-WK-952-1-3 — the function has existed since WK-950-2 with no
```

**The positive control asked for, and its result.** §7(d)'s `F-W[0-9]` alternative returning
zero is the one zero that could be silent. Running the gate's own regex body unmodified against
input it must match — the same tree, un-migrated — returns **214 matching lines across 57
files**, among them `backend/src/app/main.py`, `.claude/skills/close-workstream/SKILL.md` and
`docs/audit/register.md`. **The pattern is not silent.**

**But the zero is not a clean corpus either.** Of the 57 control files carrying `F-W` tokens,
23 still exist after the migration. Their tokens were not resolved to a finding id; they were
mangled into `F-WK-*`, a form that matches **no** §7(d) alternative, because `F-WK` has a letter
where `F-W[0-9]` requires a digit.

**So §7(d)'s `F-W[0-9]` row reaches zero partly because the corruption moved the tokens out of
the predicate's own reach.** The check's name says no legacy finding ids remain; its predicate
says no string `F-W<digit>` remains; mangling satisfies the predicate while inverting the name.
This is handover §7's pattern one turn further on, and the first instance where the defect and
the green come from the same edit.

**The general form, offered for the row set rather than as a proposal.** Every §7(d) alternative
states what a token must no longer look like. None states what it must look like instead, so
each is satisfiable by corruption as well as by migration. A row set with only
legacy-form predicates cannot distinguish a migrated corpus from a damaged one.

### 3.1 What the (g) fix must cover, measured against the branch

At `3cfffbf` on `w37-6-token-boundary`, `pytest tests/test_doc_id_migrate.py -k "token or
boundary or compound or mangle"` gives **5 failed, 3 passed**. The broken-input proof genuinely
reddens on the unfixed code, and it covers two-, four- and twelve-part slash compounds and the
ADR, NT/RFC and Ruling families — materially wider than the named `NFR-RATE-13/14`.

Compound arity in the migrated corpus, so the multi-part case is sized rather than assumed:

```bash
git grep -hoE '\b(FR|NFR|OQ|DEP)-[0-9]+(/[0-9]+)+' -- $FILES | awk -F/ '{print NF-1}' | sort | uniq -c
```

272 have one slash, 88 two, 35 three, 9 four, 16 five or more, the longest eleven
(`FR-278/4/10/11/12/14/15/16/19`). **Multi-part is 30% of the population.**

**The gap.** The proof's identifier case is `slice-id-inside-a-longer-task-id`: `W9-3-2`
containing `W9-3`, a **suffix** extension. `F-W9-3` is a **prefix** extension with nothing after
the token, so a guard keyed on a trailing `-<digit>` cannot see it. Run against the branch's own
`_rewrite_one_file`:

```
F-W9-3     + {W9-3: SL-00123}  ->  F-SL-00123        rewritten (nothing follows the token)
F-W9-3-2   + {W9-3: SL-00123}  ->  F-SL-00123-2      rewritten
F-W11-1-3  + {W11: WK-00952}   ->  F-WK-00952-1-3    rewritten
W9-3       + {W9-3: SL-00123}  ->  SL-00123          rewritten  (live control, correct)
```

`F-W9-3` is 48 occurrences in the control, the commonest `F-W` token there. **A fix that guards
only the right-hand side leaves it mangled and leaves §7(d) green over it.**

## 4. Row (h): 548, not 547 — and the count depends on the git index

`audit-docs.py` on the migrated snapshot exits 1. My count is **548**; the handover's is 547.
Same tree, same migrating script, and the two snapshots are byte-identical outside
`__pycache__` (`diff -rq --exclude=.git`). The one-failure difference is **not reconciled**, and
I am not adopting 547.

What I can say is that the count is stable under repetition and unstable under one specific
thing:

```
migrate, then audit-docs.py BEFORE `git add -A`  ->  FAILED (549)
migrate, then `git add -A`, then audit-docs.py   ->  FAILED (548)
```

Three consecutive runs on each of two independently built snapshots give 548 every time after
`git add -A`. So `audit-docs.py`'s population on a migrated tree **depends on the git index
state**, deterministically. Handover §2.2 records this scope blind spot — `git ls-files` read
before `git add -A` — as **RETIRED**, being a defect of the old link instrument's population.
**It is retired for condition 7 and alive in row (h).** An instrument that migrates a snapshot
and runs `audit-docs.py` without refreshing the index reports a different number, and the
number it reports is larger, so the failure is not one that would draw attention to itself.

**The denominators, checked as asked — a green over an empty population is not a pass.**
Same command, both trees:

| summary line | control | migrated |
|---|---|---|
| requirements defined across 8 specs | 533 | **0** |
| open questions, all mirrored | 118 | **0** |
| journey citations | 31 endpoints, 8 functions | **0 endpoints, 0 functions** |
| §10 mirror rows carrying register status | 118 of 118 | **0 of 0** |

Confirms handover §4. One line to add: the migrated tree also reports
`docs/notes does not exist — checks 16-20 cannot run`, so checks 16 to 20 do not execute at all.

**A figure of the handover's I could not reproduce.** Handover §4 says check 37 sees 1 document
"against the 292 it reported pre-migration". Running `audit-docs.py` on my **un-migrated
control** at `0de529e` gives `check 37: 1 document(s) checked in scope, 0 exempt as
verbatim-migrated`, and the string `292` does not occur anywhere in that log. The 292 is not
what `audit-docs.py` prints on this tree. I do not know what predicate produced it and am not
reconciling to it.

## 5. Row (c) passes, and the same command passes on an un-migrated tree

`python3 scripts/doc-index.py --root <snapshot>/docs --check` prints `OK (byte-stable)` and
exits 0 on the migrated snapshot, reproducing the handover. On the **control** it prints
`INDEX.md does not exist and zero governed records were found ... nothing to check yet
(pre-migration)` and **also exits 0**. Passing the repository root instead of `<root>/docs`
produces the same reassuring line and the same exit 0 on a fully migrated tree.

So exit 0 is returned by the pass, by an un-migrated tree, and by a mis-rooted invocation.
**Row (c) as stated is satisfied by an exit code that three different states share.** An
instrument computing (c) must assert the `OK (byte-stable)` line and treat the
`nothing to check yet` line as a failure, or the row is vacuous whenever the root is wrong.

## 6. Row (d): four alternatives I cannot reproduce, and why I am not reconciling

All thirteen alternatives, migrated snapshot at `0de529e`, `git add -A` applied, `was:` lines
dropped as a substring, `REDIRECTS.csv` excluded:

```bash
FILES=$(git ls-files | grep -v REDIRECTS.csv)
git grep -nE '<alternative>' -- $FILES | grep -v 'was:' | wc -l
```

| alternative | handover (substring) | mine | control (un-migrated) |
|---|---|---|---|
| `NT-00` | 32 | **35** | 1465 |
| `F-W[0-9]` | 0 | 0 | 214 |
| `\bF[0-9]{2}\b` | 1330 | 1330 | — |
| `wf-0[0-9]` | 327 | **328** | 268 |
| `Ruling [0-9]+` | 74 | **77** | 2840 |
| `ADR-0[0-9]{3}` | 37 | **38** | 440 |
| `(FR\|NFR\|OQ\|DEP)-[A-Z]+-[0-9]+` | 72 | **92** | 14982 |
| `W[0-9]+[a-z]?-[0-9]+` | 1 | **4** | 2531 |
| `docs/plans/2026-` | 66 | 66 | 654 |
| `docs/audit/` | 291 | 291 | 913 |
| `docs/notes/` | 118 | 118 | 269 |
| `docs/adr/` | 34 | 34 | 63 |
| `\.claude/notes/` | 1 | **88** | 181 |

Five agree exactly. Four differ by one to three, which four commits of drift cannot explain
because this is the handover's own tree. **One differs by 87.**

**`\.claude/notes/` is the one that matters.** My 88 are real residual path citations, read and
confirmed by hand — `.claude/notes/README.md:13`, `.claude/skills/docs-audit/SKILL.md:253`,
`docs/plans/PL-00103-...:304`, and 79 of the 88 sit under `docs/`. Most are bare directory
mentions rather than citations of a file, which is what a predicate written as a bare directory
prefix matches. To reach 1 a measurement must have required a filename after the directory. That
is a narrower predicate than the alternative NT-0019 §7 actually writes, and it is narrower in
the direction that hides work.

**The handover publishes no command for this table.** It states thirteen alternatives and two
readings but not the invocation, so the difference cannot be traced to a pathspec, an exclusion
list or a regex body. Under `CLAUDE.md` §13 as amended 2026-09-02, a count carries the predicate
it counted with; **the §7(d) table does not, and four of its thirteen figures are consequently
unreproducible by a second measurer.** That is offered as a finding about the record, not about
the corpus, and it is the same shape as F85.

I am **not** reconciling my figures to the handover's. Mine are stated with the command above
and re-run at both `0de529e` and `e97b97a`.

## 7. Row (e): the two readings are 2042 and 77, and the gap is the whole question

```bash
PAD='\b(FR|NFR|DEP|OQ|WK|SL|WF|ADR|RFC|PL|LG|RL|RS|CR|FD)-0[0-9]+\b'
git grep -hoE "$PAD" -- $FILES | wc -l      # 2042 occurrences, migrated
                                            #  610 occurrences, control
```

On a filter of my own that drops lines carrying the padded id inside a link target or a path,
77 remain. The handover reports 2021 and 36 for the same two questions. **Neither side's
narrow figure is reproducible, because neither publishes the filter**, and the two narrow
figures differ by a factor of two while the two broad ones differ by 1%.

This is direct evidence for Ruling 102 §2 row 5: (e) needs one ruled reading, and the reason is
not tidiness. The row's verdict does not change — it fails under both readings — but its size
moves by a factor of 26 depending on an unstated filter, and the work list moves with it.

## 8. Row (i), and a contradiction inside Ruling 102 itself

Ruling 102 §1 says the instrument "computes all **nine** §7 (a)–(i) rows". Ruling 102 §3 says
"**Confirmed: (a)–(h) are W37-6's, (i) is W37-10's** ... **Eight rows, not nine.**" The two
statements are in the same record. §3 is the later and more specific, is headed as a correction,
and gives the maintainer's words for it, so §3 governs on its face — but §1 is the clause that
specifies what the instrument must compute, and it is the clause an implementer reads.

Raised as a finding rather than resolved: an instrument built to §1 computes and gates on a row
that §3 assigns to another Work, and an instrument built to §3 omits a row §1 requires. **Which
it is, is the maintainer's**, and the lead's brief to this auditor restated the nine, so the
superseded count is still travelling.

## 9. The `was:` populations — the denominators differ, the numerator does not

Migrated snapshot at `0de529e`:

```bash
grep -rlE '^was:' . | grep -v '^./.git/' | wc -l                          # 395 files
grep -rlE '^was:' --include='*.md' . | grep -v '^./.git/' | wc -l         # 394
grep -rlE '^was: [^~]' --include='*.md' . | grep -v '^./.git/' | wc -l    # 355
```

and resolving each non-null `was:` value against the control tree — 357 values — gives **3 that
name a real pre-migration path** and 354 that do not.

The two standing populations are 393 (auditor) and 354 (executor). Mine are 394 and 355: **each
is one larger than its counterpart, the same offset in both**, which is consistent with one
document included here and excluded there rather than with two different rules. I have not
chased the single file.

**The finding is that the denominator does not matter to the verdict.** Every population I
measured — 357, 394, 395 — returns the same numerator of **3**, and my 3 agrees with the
auditor's 3 and the executor's 3. Three measurements agreeing on 3 is worth stating carefully:
we may share a formulation rather than a check, since all three resolve the field against a
pre-migration path. What would break that agreement is a `was:` value that is a real
pre-migration path but the wrong document's, and none of the three methods can see it. **The
field is broken under every reading; which population the acceptance test wants is a question
about the test, not a disagreement about the corpus**, and it should be ruled rather than
reconciled.

## 10. Delivery verification, as at this record's date

| branch | state | verified |
|---|---|---|
| `w37-6-token-boundary` (executor-g) | `3cfffbf`, 6 commits ahead of `origin/main` | broken-input proof **reddens as required** — 5 failed, 3 passed. Fix not yet written: 391 and 216 both still present at that commit. Gap in §3.1 |
| `w37-6-verify-instrument` (executor-verify) | at `origin/main`, no commits | nothing to verify yet. `doc-id.py migrate --verify` does not exist on any branch |
| `w37-6-h-rows` (executor-h) | at `origin/main`, no commits | nothing to verify yet |

## 11. What this record does not do

It issues no verdict, closes nothing, and proposes no change to the §7 row set. The rows are the
maintainer's under Ruling 102 §1; the four verdicts and the merge are the lead's. The
unreproducible figures of §4, §6 and §7 are recorded as unreproducible rather than corrected,
because a second measurer who cannot see the first measurer's predicate is not entitled to
declare the first wrong — only to decline to adopt it.
