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
| (c) `doc-index.py --check` byte-stable | PASS — `OK (byte-stable)`, exit 0 | **FAIL** — `is stale`, exit 1, when run with **the migrated tree's own** `doc-index.py`; `audit-docs.py` check 39 independently agrees | **no — see §5** |
| (d) the id/path grep returns nothing | FAIL — 12 of 13 alternatives non-zero | FAIL — 12 of 13 non-zero; **12 of 13 figures reproduce exactly** once §7(d)'s leading `\b` is applied, `NT-00` apart | yes, after the retraction in §6 |
| (e) no padded id in prose | FAIL/ambiguous — 2021 literal, 36 excluding path context | FAIL — 2042 occurrences, 77 on a path-context filter of my own | direction yes, neither figure reproducible — §7 |
| (f) `VR-DST-1` unchanged | FAIL literal / PASS on intent — 104 → 127; 127 → 127 across the migration | 104 at `8f5d57d`; 127 control; 127 migrated | yes, exactly |
| (g) diff hunks neither header nor citation-token | FAIL — ≤ 1187 lines; 391 mangled citations, control 0 | 391 reproduced exactly; **plus 216 mangled finding ids, control 0** — §3 | 391 yes; the row is wider than reported |
| (h) full gate green | FAIL — `audit-docs.py` exit 1, 547 failures; 110 check 28, 23 check 32 | FAIL — exit 1, **548**; **109** check 28, **22** check 32, remainder **+3** | direction yes; **not an off-by-one** — §4.1 |
| (i) every §5 H row closed by a named commit | scope correction, not measured | not measured — out of scope, and see §8 | yes |

**Six of nine agree.** §6's retraction moved (d) into the agreeing column; §5 then moved (c) out
of it, and in the opposite direction from any other disagreement here — **(c) is the only row
where my measurement makes the corpus look worse rather than the same.** The three that do not
agree are:

- **(c)** — recorded by the handover as one of only two passes. It fails at the merge tree. §5.
- **(e)** — neither side publishes its filter. §7.
- **(h)** — 548 against 547, and the decomposition disagrees by more than the total does. §4.1.

**Row (d) disagreed only because the auditor mis-transcribed §7(d)'s predicate; the handover was
right — see §6.**

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


### 4.1 The 548-against-547 gap is not an off-by-one — the decomposition disagrees by more

The first filing called this "count off by one". That framing was wrong, and it was wrong in the
direction that makes a disagreement look benign. The handover names two sub-populations of its
547, so the total can be decomposed rather than compared whole. Mine, at `0de529e` migrated,
each figure taken with **two independent predicates that agree**:

| population | predicate A | predicate B | mine | handover |
|---|---|---|---|---|
| check 28 | `grep -c 'check 28'` | `grep -c 'kind-suffixes'` | **109** | 110 |
| check 32 | `grep -c 'check 32'` | (same population by message shape) | **22** | 23 |
| broken links | `grep -c 'broken link'` | — | **390** | — |
| everything else | the complement | — | **27** | — |
| **total** | | | **548** | 547 |

`109 + 22 + 390 + 27 = 548`, so **the parts sum to the whole** on my side.

Against the handover: check 28 is **one lower**, check 32 is **one lower**, and the remainder is
**three higher** — 417 against 414. **Three offsetting differences that net to +1.** A total
differing by one is what you see; three sub-populations differing in two directions is what is
there. Comparing only the totals would have reported a near-agreement over a decomposition that
does not agree at all.

**Still unexplained and still not reconciled.** Unlike §6's `NT-00` residual, this one has no
one-document signature — a single extra or missing document cannot move three populations in two
directions.

### 4.2 More of the gate is inert than the handover recorded

Handover §4 records the empty-population **summary lines**. Two failure lines in the same run say
something stronger — six checks do not execute at all:

```
  - docs/notes does not exist — checks 16-20 cannot run
  - docs/notes does not exist — check 25 cannot scan it
```

`docs/notes/` is a directory the migration dissolves, and five checks plus one more are keyed to
its existence. They are not passing over an empty population; they are **not running**. A row (h)
that is read as "how many failures" counts these as 2, when what they report is 6 checks' worth
of coverage absent from every other number in the run.

## 5. Row (c) is a FAIL, not a PASS — the pass came from running a script that is not in the tree under test

**This section replaces its first filing (`3b2b501`), which recorded (c) as reproducing the
handover's PASS with a vacuity caveat. The caveat stands and is kept below as §5.2, but the
verdict is wrong: at the migration tree, row (c) fails.**

### 5.1 The same command, the same tree, two verdicts

```
snapshot's own copy:   python3 scripts/doc-index.py --root <snap>/docs --check
                       -> "<snap>/docs/INDEX.md is stale — run ... to regenerate"     exit 1
main's copy:           python3 <checkout>/scripts/doc-index.py --root <snap>/docs --check
                       -> "<snap>/docs/INDEX.md: OK (byte-stable)"                    exit 0
```

Both run twice, both reproducible, on the migrated snapshot of `0de529e`. **The verdict depends
on which copy of `doc-index.py` runs the check, not on the corpus.**

**A third measurement breaks the tie, and it is already in the run.** `audit-docs.py` executed
inside the snapshot loads the snapshot's `doc-index.py` by path and reaches the same conclusion:

```
check 39: docs/INDEX.md is stale against a fresh regeneration (479 governed record(s))
```

It is one of the 548 failures of §4. **Two of the three measurements say stale. The only one
that says pass is the one using a script from outside the tree under test.**

### 5.2 The cause: a citation rewrite inside a string literal that is part of generated output

Rendering `docs/INDEX.md` with each copy against the same corpus — both produce **479 records**
and differ by exactly one line:

| | line 3 of the rendered index |
|---|---|
| committed `docs/INDEX.md` | ``Generated by `scripts/doc-index.py`. Do not hand-edit — see NT-0019 §1.4.`` |
| rendered by **main's** `doc-index.py` | identical — **byte-identical to the committed file** |
| rendered by the **migrated tree's** `doc-index.py` | ``... see **RFC-216** §1.4.`` |

The migration generated `docs/INDEX.md` with the pre-migration renderer, which emits `NT-0019`,
and then rewrote the citation `NT-0019` to `RFC-216` inside `scripts/doc-index.py`'s own banner
string — **without regenerating the index**. Generator and generated artifact now disagree by
exactly the token the migration rewrote in one and not the other.

**NT-0019 §5.7 predicted this class in one clause** — *"Every touched file is compiled and its
suite run (§7 (h)): a rewrite inside an asserted string is the reason."* The clause anticipated
a rewrite inside a string a **test** asserts. This is a rewrite inside a string the **product
output** contains, which is the same mechanism one step further out, and it defeats the
acceptance row rather than a test.

### 5.3 Why the pass was recorded, and the rule it argues for

Nothing was done wrong procedurally: pointing a checkout's script at a snapshot is the obvious
way to measure a snapshot, and it is what I did first. But NT-0019 §7's own preamble scopes the
whole row set — *"At the migration PR's merge tree"* — and a script is part of that tree.
`scripts/doc-index.py` is rewritten by the migration, so the merge tree's generator is not the
one in any auditor's checkout.

**The generalisable rule, offered rather than proposed:** an acceptance row that runs a program
must run **the tree's own copy** of that program. Where it does not, the row silently tests a
different artifact than the one being accepted, and the failure mode is a green.

**This bears directly on the instrument.** `doc-id.py migrate --verify <snapshot>` runs from the
checkout that invokes it. If it computes (c) — or any row that shells out — with its own
`doc-index.py` rather than the snapshot's, **row (c) passes forever and this defect is
undetectable by the thing built to detect it.**

### 5.4 The vacuity caveat from the first filing, unchanged and still true

`doc-index.py --check` exits 0 on the pass, on an **un-migrated control** (`INDEX.md does not
exist and zero governed records were found ... nothing to check yet (pre-migration)`), and on a
**mis-rooted call** — passing the repository root instead of `<root>/docs` produces the same
reassuring line and the same exit 0 on a fully migrated tree. Three different states, one exit
code. An instrument computing (c) must assert the `OK (byte-stable)` line and treat
`nothing to check yet` as a failure.

### 5.5 Bounded: rows (a) and (b) do not flip

Checked rather than assumed, since `scripts/doc-id.py` is also rewritten by the migration. Run
with the **snapshot's own** copy: (a) `total 465`, no `none` row; (b) exit 1, 77 `noncontiguous`,
0 duplicate. Identical to the figures obtained with the checkout's copy. **Only (c) changes
verdict.**

## 6. Row (d) — RETRACTED AND REPLACED 2026-09-03: the handover's figures are right and mine were wrong

**This section as first filed (commit `3b2b501`) said that four of the handover's thirteen
§7(d) figures were unreproducible, that the difference could not be traced because no command
was published, and that this was a finding about the record of the same shape as F85. All three
claims are withdrawn.** The difference is traceable, it is mine, and the predicate was published
— it is NT-0019 §7(d)'s own regex, which I mis-transcribed. What follows replaces the retracted
text; nothing in §3 (the mangled finding ids) depends on it, and §3 is re-verified below.

**The error.** §7(d) is **one** regular expression:

```
\b(NT-00|F-W[0-9]|\bF[0-9]{2}\b|wf-0[0-9]|Ruling [0-9]+|ADR-0[0-9]{3}|(FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+|W[0-9]+[a-z]?-[0-9]+|docs/(plans/2026-|audit/|notes/|adr/)|\.claude/notes/)
```

**Every alternative inherits the leading `\b`.** Measuring "one row per alternative" means
running `\b(<alternative>)`, not `<alternative>` on its own. I ran each alternative standalone
and dropped the anchor, so every figure I reported was an over-count. Re-run with the anchor
restored, on the same snapshot at `0de529e`:

```bash
FILES=$(git ls-files | grep -v REDIRECTS.csv)
git grep -nE "\b(<alternative>)" -- $FILES | grep -v 'was:' | wc -l
```

| alternative | handover | mine, as first filed | mine, with the inherited `\b` |
|---|---|---|---|
| `NT-00` | 32 | 35 | 33 |
| `F-W[0-9]` | 0 | 0 | **0** |
| `\bF[0-9]{2}\b` | 1330 | 1330 | **1330** |
| `wf-0[0-9]` | 327 | 328 | **327** |
| `Ruling [0-9]+` | 74 | 77 | **74** |
| `ADR-0[0-9]{3}` | 37 | 38 | **37** |
| `(FR\|NFR\|OQ\|DEP)-[A-Z]+-[0-9]+` | 72 | 92 | **72** |
| `W[0-9]+[a-z]?-[0-9]+` | 1 | 4 | **1** |
| `docs/plans/2026-` | 66 | 66 | **66** |
| `docs/audit/` | 291 | 291 | **291** |
| `docs/notes/` | 118 | 118 | **118** |
| `docs/adr/` | 34 | 34 | **34** |
| `\.claude/notes/` | 1 | 88 | **1** |

**Twelve of thirteen reproduce the handover exactly**, including both figures I had singled out.

`NT-00` remains one line apart, and it is worth stating precisely rather than as "unexplained",
because the offset has a signature. Under **both** `was:` readings my figure is exactly one
larger: substring 33 against 32, and field 36 against 35. The same `+1` appears in §9's two
`was:` populations — 394 against 393, and 355 against 354. **Four measurements, four different
predicates, the same offset of one.**

That pattern is what a **one-document population difference** looks like, not what a predicate
difference looks like — a predicate difference would move each figure by a different amount, as
the anchor error above did. Against it: row (a)'s family census is **465 on both sides**, so the
governed-record population is identical, and I could not find the document. `.claude/notes/README.md`
was the obvious candidate and is not it — it carries no `was:` field at all.

**Recorded as an unresolved one-document offset**, most consistent with a file included in one
side's filter and excluded from the other's, and **not** as a defect on either side. It changes
no verdict: every affected row fails on both readings.

**A second error, corrected here rather than left standing.** The retracted text read "Five agree
exactly. Four differ by one to three ... One differs by 87." The true tally of the first filing
was **six agreeing and seven differing**. The "four" was wrong when written, and it propagated
out of this record into two messages and into a directive from the lead before it was caught. It
is exactly the class of defect this record exists to find, produced by the auditor.

### 6.1 What survives, and it is a finding about §7(d) rather than about the handover

The 88 strings are still in the tree. What changes is whose predicate they escape.

```bash
git grep -hoE '.{1}\.claude/notes/' -- $FILES | cut -c1 | sort | uniq -c
```

returns 76 preceded by a backtick, 8 by a space, 2 by a double quote, 1 by `/`, 1 by `\`, and
**1 by the letter `n`**. `\b` asserts a word boundary, and `.` is not a word character, so
`\b\.claude/notes/` can only match where a **word character immediately precedes the dot**. A
path citation in prose is always preceded by a backtick, a space or a quote. **The alternative
therefore cannot fire in any of the contexts it exists to police.**

Its single match is an accident:

```
tests/test_audit_docs_ids.py:604:   "docs/findings/register.md\n.claude/notes/0001-x.md\n",
```

— the `n` of a `\n` escape inside a Python string literal.

**So `\.claude/notes/` is inert by construction, and 87 of the 88 real residual citations sit
outside §7(d)'s reach.** Those 88 are read and confirmed by hand — `.claude/notes/README.md:13`,
`.claude/skills/docs-audit/SKILL.md:253`, `docs/plans/PL-00103-...:304` — and 79 of them are
under `docs/`.

This is the same class as §3 and it is the third instance in this record: **the check's name
says no `.claude/notes/` path citations remain; its predicate says no such citation preceded by
a word character remains.** Unlike §3 the cause is not corruption — the alternative was never
able to fail. A row that cannot fail is a row that was never enforceable, which is Ruling 102
§1's own test, and it reached three windows of hand-run gates without firing once.

**Whether §7(d) should be amended is the maintainer's**, and the wording is not proposed here.
The measurable claim offered to that decision is: with the alternative as written, 1; with the
leading `\b` not applied to this alternative, 88; the corpus is the same corpus.

### 6.2 What this retraction does not disturb

**§3 stands, re-verified after the correction.** `F-W[0-9]` is 0 under both readings, because
`\bF-W[0-9]` still matches `F-W11-1-3` — `F` is a word character preceded by a space or a
backtick, so the anchor fires — and still fails to match `F-WK-952-1-3`, because `K` is not a
digit. Checked directly:

```bash
echo 'see F-W11-1-3'    | grep -cE '\b(F-W[0-9])'   # 1
echo 'see F-WK-952-1-3' | grep -cE '\b(F-W[0-9])'   # 0
```

The 216 mangled finding ids, the 214-line positive control, and the conclusion that §7(d)'s
`F-W[0-9]` row reads zero **because** the corruption moved the tokens out of its reach are all
unaffected by this section's error.

**One hypothesis tested and refuted, recorded so it is not retried.** Before finding the anchor
I tested whether the stale-index effect of §4 explained the differences. It does not, and it
fails in the opposite direction: measured on a migrated snapshot **without** `git add -A`, the
thirteen alternatives read 10, 0, 372, 183, 22, 13, 52, 4, 41, 104, 43, 16, 9 — one agreement
out of thirteen and every non-trivial figure far below the handover's, not above.

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
