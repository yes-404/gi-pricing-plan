---
id: RL-977
family: ruling
title: the fix is inert on the real corpus, so the boundary is free; it lands on its own, and the reader and the writer land together
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-commit-boundary-and-plan-reviews-shape-rulings.md
---

# Where Rulings 79 and 80 land, and the shape `plan-reviews.md` actually has, ruled (2026-09-02)

**What this is.** Two questions routed by the lead while W37-6 waits on a maintainer
go-ahead. The first is a commit-boundary question about work already in flight; the second is
the fourth and last of the discovery defects, the one no regex reaches. They are ruled below
as Rulings 81 and 82.

**Both were routed with figures that did not survive measurement, and in the second case the
figures were the question.** The brief reported `docs/closures/INDEX.md#plan-reviewsmd` as *15 `###`
headings, 12 records, three undated*. Executed against the file, it is **14 headings, 10
records, four unmatched** — and the fourth unmatched heading is a **filed §14 plan review**,
not a proposal. That changes what is being decided: the brief asked whether to widen a
pattern for three sub-headings, and the measurement says a governed review is being destroyed
alongside them. The corrections are set out in their own section below rather than folded
silently into the rulings, because the lead asked for verification against the artifacts and a
corrected count is the useful half of that answer.

**Neither ruling edits [`RFC-937`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) §1 or
[`docs/process/document-ids.md`](../process/document-ids.md).** RL-977 decides only a
sequencing question inside an already-ruled body of work. RL-978 decides an exclusion and a
unit boundary, and hands the positive family assignment to the planner on the RL-975
precedent rather than exercising a predicate once and trusting it.

## Authority

- **RL-977 is a sequencing decision inside an identified decision point** — Rulings 79 and
  80 assigned an owner and did not fix a commit boundary, and the boundary became live when
  the lead dispatched an executor against `main`. **RL-978 is a spec-versus-code conflict**:
  RFC-937 §4 step 2 says *"`plan-reviews.md` → one `CR-` per review"*, and the file contains a
  dated section that is not a review and is not sub-content of one, which the rule does not
  reach. [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) places
  both with this role; `CLAUDE.md` §0 requires the second be resolved rather than quietly
  reconciled.
- **The lead routed them here under the maintainer's delegation of 2026-09-01**, recorded at
  [`RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`](RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md)
  §1, and neither falls in its §2 exclusions: neither is a fact only the maintainer holds,
  neither accepts a Work, Phase or Project close, and neither amends `CLAUDE.md`.
- **Every figure below is measured at `ffac8ba`**, which was `origin/main`'s tip when this
  record was written and still was when it was pushed (`git fetch origin && git rev-parse
  origin/main` re-run immediately before the commit). The branch is cut from that commit, so
  the measurement tree and the branch base are the same object — stated because the two came
  apart under a ruling record twice on 2026-09-01.
- **Re-read under [`delivery-process.md`](../process/delivery-process.md) §15 Rule 10** —
  *"a branch open when a ruling merges is re-read against that ruling before the branch itself
  merges."* No ruling merged during this branch's life; if one does, this record is re-read
  before it is merged.

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while
`check_plan_acceptance_standard`'s own docstring disclaims exactly that scope. That
disagreement is register finding F68 — see [`../findings/register.md`](../findings/register.md) —
carried forward with RFC-937's migration as its trigger. It is honoured here, and the check is
not patched from this branch.

1. `git grep -c '^## RL-977 —\|^## RL-978 —'` on this file returns `2`, and
   `git grep -n '^#\+ Ruling ' docs/plans/` shows 81–82 filling the gap immediately after
   RL-999 with no duplicate and no skip.
2. Each `### 2. Ruled` subsection names the chosen option **and every rejected option**, with
   the measured evidence that separated them.
3. Each ruling carries a `### 4.` section stating its acceptance as **a violation that must
   become detectable**, never as a description of correct behaviour — and each such violation
   is one an artifact can be edited to produce, not a human judgement.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-rulings-81-82-boundary-and-plan-reviews` names
   exactly this one new file. No note, no template, no script, no test, no fixture, no
   workflow and no roadmap row is edited by this branch — every change these rulings oblige is
   work for a named owner.
6. Every claim about a script's behaviour below was produced by **executing that script**
   against the real artifacts, not by reading it; the probe and its output are quoted inline.

---

## RL-977 — the fix is inert on the real corpus, so the boundary is free; it lands on its own, and the reader and the writer land together

### 1. Verified first, at `ffac8ba`

**(a) The two symbols are in `doc-index.py`, and the leaf plan's one-commit list is about a
different file.** This is the load-bearing correction, because the brief's whole case for
landing inside W37-6 rested on the opposite.

```
$ grep -n '_ROW_FIELDS = \|def scan_phase_sections' scripts/doc-index.py
268:_ROW_FIELDS = frozenset(
353:def scan_phase_sections(path: Path) -> list[PhaseSection]:
```

[`../plans/PL-00960-w37-6-the-migration-run-leaf-plan.md`](../plans/PL-00960-w37-6-the-migration-run-leaf-plan.md)
§7.3 is titled *"Task 3 — `audit-docs.py`'s parsers, regexes and pins"* and its **Files:** line
reads `scripts/audit-docs.py`, `tests/test_audit_docs_*.py`. `doc-index.py` appears in that
plan's task list twice and neither is this: §7.6 (*"any path constant naming a pre-migration
directory"*) and §7.8 (`.github/workflows/docs.yml`'s `paths:`). The row and phase parsers are
in neither. And the plan predates the rulings entirely:

```
$ grep -c 'RL-998\|RL-999' docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md
0
```

**(b) The leaf plan's own simultaneity criterion does not capture this fix.** Its Goal states
what must be in the one commit: *"land in the same commit every instrument an author would
otherwise follow to produce a document the widened checks reject."* That is RL-987's
instrument set — the things that **teach an author a form**. `doc-index.py`'s row and phase
parsers are readers, not instruments; no author follows them to produce anything.

**(c) The leaf plan disclaims commit boundaries as a requirement, in its own words.** §7.5,
about the commit it most wants isolated: *"This is not a required commit boundary — RL-989
settles what (g) means, not how many commits the branch has before it is squashed."* A plan
that declines to make a boundary binding for `migrate`'s own output does not impose one on a
parser fix it never mentions.

**(d) RFC-937 §4's "one scripted PR, once" scopes to `migrate`, not to the parsers.** The
section head is *"Migration — one scripted PR, once"* and its body opens *"`scripts/doc-id.py
migrate`, deterministic and idempotent, run once and retained as evidence"*, followed by eight
numbered steps. A `doc-index.py` reader fix is none of the eight. The phrase binds the
migration run; it does not annex every file the migration will later exercise.

**(e) The decisive fact — the fix is inert on the real corpus, measured by execution.**

```
$ grep -c 'WK-\|SL-' docs/roadmap.md
0
$ grep -cE '^## (P[0-9]|Phase )' docs/roadmap.md
0
$ grep -c '```yaml' docs/roadmap.md
0
```

and the parsers themselves, imported and called against the real file:

```
scan_phase_sections(docs/roadmap.md) -> []
scan_roadmap_rows(docs/roadmap.md)   -> []
scan_bold_id_rows(docs/roadmap.md)   -> 0
```

The second group is stronger than the `grep`s above it and is why it was run.
`_parse_row_block` raises `HeaderError` on an unknown key **before** the `family in ("work",
"slice")` filter, so a fenced block under any `###`+ heading carrying a stray field would
raise rather than return `[]`. It returned `[]` with no exception. Three independent
conditions each make both parsers inert: the roadmap has no `WK-`/`SL-` token, no `## P<n>`
heading for `scan_phase_sections`'s `^##\s+(P\d+[a-z]?)\s+—` to match, and no fenced `yaml`
block at all for either to read.

**One of the two is not even reachable from the gate.** `audit-docs.py` loads `doc-index.py`
as `_doc_index` and calls `build_corpus` once, in check 39. `build_corpus`'s body calls
`scan_document_family`, `scan_roadmap_rows` and `scan_bold_id_rows` — **not**
`scan_phase_sections`, whose only caller anywhere is `phase_report` (`doc-index.py:812`),
reached from `doc-index.py`'s own `--phase` CLI flag and from tests. So RL-999's half
cannot change a gate result at `ffac8ba` by any path.

**(f) The CI step that consumes them is green and self-describes as pre-migration.**
`.github/workflows/docs.yml:43` runs `python3 scripts/doc-index.py --check`:

```
$ python3 scripts/doc-index.py --check
docs/INDEX.md does not exist and zero governed records were found under
.../docs — nothing to check yet (pre-migration)
$ echo $?
0
```

**(g) What the fix does break is contained in its own branch, and none of it is a governed
document.** The phase sections in `tests/fixtures/docs-ids/w37-3-corpus/roadmap.md` (`## P9`)
and `tests/fixtures/docs-ids/w37-4-rollup-raise/roadmap.md` (`## P6`) are written as fenced
` ```yaml ` blocks, which is the form RL-999 removes. `docs/_templates/PHASE.md` shows the
unfenced form and says so in its own comment: *"a phase section is plain fields under a
heading, exactly as shown below, not YAML front matter"*. So those two fixtures' **phase
sections** must be rewritten unfenced in the same branch or `phase_report`'s tests go red.
Their `###`/`####` **row** blocks stay fenced — §1.5 requires it (*"as a fenced block under the
row's heading"*), `scan_roadmap_rows`'s docstring repeats it, and RL-998 changes which
fields a row block may carry, not whether it is fenced.

### 2. Ruled

**The fix lands as its own pull request, merged on its own, before W37-6 runs. Reader and
writer land together in it.**

**Why the boundary is free rather than forced.** The sub-question the lead identified as
decisive is a fact, and (e) answers it: fixing `_ROW_FIELDS` and `scan_phase_sections` before
the migration creates **no red state on `main`**, because both parsers read nothing from the
real corpus today and will read nothing after the fix. There is no intermediate state to be
red in. A boundary is forced only when a fix cannot be made green without the migration's
output; every input this fix needs — the two row templates, `PHASE.md`, and the fixture
corpus — exists at `ffac8ba`.

**Why separately, once free.** Four reasons, in the order they bind:

1. **The argument for landing inside was a misattribution.** It rested on the leaf plan's
   one-commit list containing these parsers. It contains `audit-docs.py`'s (§1(a)), and the
   plan's own simultaneity criterion is about instruments an author follows (§1(b)). With that
   removed, nothing in RFC-937, the leaf plan, or Rulings 79 and 80 asks for simultaneity.
2. **W37-6 is gated on a maintainer go-ahead that has not been requested.** "Inside W37-6"
   is therefore not a date; it is "whenever the gate opens", and an unmerged fix rots against
   a moving `main` in the meantime.
3. **It makes the supervised run smaller and less confounded.** The leaf plan §4.4 treats the
   irreversibility of that commit as the thing the maintainer is being asked to accept. A
   migration run against an already-correct parser is one fewer variable in the run that can
   least afford one.
4. **Its acceptance tests are satisfiable today.** Both rulings' §4 items name positive
   controls that fail at `ffac8ba` — `unknown row field 'tree'`, and `PHASE.md`'s own body
   yielding no phase. A fix whose failing control exists before the migration does not need
   the migration to prove itself.

**Rejected: landing inside W37-6's commit.** Rejected on (a)–(d): no artifact requires it, and
the one that was cited names a different file.

**Rejected: landing the reader fix early and deferring the `doc-id.py` emitters to W37-6.**
This is the tempting middle, and it is the one shape that would create the red state the
brief was worried about. RL-998 §3 item 4 obliges `migrate`'s row emission to derive from
the same template, and RL-999 §3 item 4 obliges `_PHASE_TEMPLATE` to be re-emitted unfenced.
Fix the reader and leave the writer and `migrate` emits blocks its own reader rejects — a new
latent defect, of exactly the species RL-998 exists to remove, created by the act of
splitting. **The split is between the fix and the migration, never between the reader and the
writer.**

### 3. What it obliges

1. **The executor's in-flight branch merges on its own**, and carries both halves of each
   ruling: `scripts/doc-index.py` (the readers) **and** `scripts/doc-id.py` (`migrate`'s row
   emission at `:1576-1583` and `_PHASE_TEMPLATE` at `:1531-1541`, with the docstring at
   `:1552` replaced by a citation to RL-999, per that ruling's §3 item 4).
2. **The two fixtures' phase sections are rewritten unfenced in that same branch** —
   `w37-3-corpus/roadmap.md` and `w37-4-rollup-raise/roadmap.md`. Their row blocks are not
   touched. Any other fixture the branch's own test run reddens is treated the same way.
3. **"Owner: W37-6" in Rulings 79 and 80 §3 item 5 is not superseded and is not re-opened.**
   It assigned scope, and this ruling decides only the commit the scope's work rides in. If
   the branch does not merge before W37-6's go-ahead arrives, the work reverts to W37-6 with
   no further ruling needed.
4. **W37-6's leaf plan gains nothing from this.** No task is added to it, no acceptance item
   changes, and this record does not amend a filed plan (`CLAUDE.md` §12). Its §7.3 stays what
   it is: `audit-docs.py`'s parsers.
5. **The measurement carried forward from Rulings 79 and 80's *Not ruled* table stands** —
   whether check 30 reaches a `WK-`/`SL-` row block after `_ID_SCOPE_ROOTS` widens is still
   W37-6's executor's to establish, and landing this fix early neither answers it nor
   discharges it.

### 4. Acceptance — the violation that must become detectable

**The violation: `doc-id.py migrate` emits a row or phase block that `doc-index.py`'s own
parser will not read.** That is the state a split between reader and writer produces, and
nothing today reports it.

- **A round-trip check: take `migrate`'s emitted row block and phase section, feed each to
  `scan_roadmap_rows` and `scan_phase_sections`, and require the fields to survive.**
  *Violation: the writer's output is rejected, or silently mis-read, by the reader in the same
  repository.* This must be a test in the branch that lands the fix, not a task carried into
  W37-6 — it is the check that makes item 3's split-forbidding enforceable rather than
  advisory.
- **The two positive controls the rulings already name must be shown failing at `ffac8ba`
  before the fix, in the branch's own evidence** — `unknown row field 'tree'` from the row
  template's fenced block, and `PHASE.md`'s filled body yielding no phase. *Violation: a
  positive control that has never printed a failure.*
- **`python3 scripts/doc-index.py --check` and `python3 scripts/audit-docs.py` both exit 0 on
  the branch**, and the branch's `git diff --stat` against `origin/main` names no file under
  `docs/` other than a ledger. *Violation: a parser fix that edits a governed document.*

---
