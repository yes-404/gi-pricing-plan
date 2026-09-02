# W37's field-set defects — where `decision:` lives, how a finding is scoped to a phase, and how a map plan rolls up, ruled (2026-09-02)

**What this is.** Three defects in NT-0019's field specification, found during execution by
the W37-3 executor and relayed by the lead. They are ruled below as Rulings 70, 71 and 72.
None is a `Decision points` row of
[`2026-09-01-nt-0019-id-standard-map-plan.md`](2026-09-01-nt-0019-id-standard-map-plan.md);
all three were discovered by building against
[`NT-0019`](../notes/0019-one-id-per-document.md) §1, which is the same provenance as
Ruling 69 in
[`2026-09-02-w37-migration-preconditions-rulings.md`](2026-09-02-w37-migration-preconditions-rulings.md).

**They are ruled now rather than after W37-4 because W37-4 builds checks 30–39 against
exactly this field set.** Check 30 requires *"no unknown field; required fields per family"*;
check 33 is built on the `execution` derivation Ruling 72 settles. A check written against a
defective field specification is a check that enforces the defect.

**Nothing in NT-0019 §1 is edited, and neither is
[`docs/process/document-ids.md`](../process/document-ids.md).** §1 is the maintainer's own
text; `document-ids.md` §1.1–§1.13 is a verbatim lift of it and says so in its own opening
paragraph; §1.6 makes `process/` the maintainer's, amendable only by an `RFC-` plus an `RL-`.
All three rulings resolve inside the implementation, which is the constraint Ruling 69 set for
this class and which this record follows.

## Authority

- **All three are spec-versus-implementation conflicts**, which
  [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) and
  [`delivery-process.md`](../process/delivery-process.md) §3 already place with this role
  (*"Rules decision points and spec-vs-code conflicts before a plan or slice can proceed"*).
- **The lead routed them here under the maintainer's delegation of 2026-09-01**, recorded at
  [`2026-09-01-maintainer-delegation-and-nt-0019-precedence.md`](2026-09-01-maintainer-delegation-and-nt-0019-precedence.md)
  §1: *"I authoris the lead to allocate technical questions to decision-maker to make decision
  on behalf of me."* **The routing is recorded because it happened, not because it was
  needed** — as with Ruling 69, the charter already reaches these, so none of the three rests
  on the delegation. That distinction matters: a reader must be able to tell which rulings
  would fall if the delegation were withdrawn, and none of these three would.
  **The maintainer did not rule any of these personally.**
- **Nothing here reopens D0–D14.** D0 (*"register dispositions live in `decision:`"*) is
  load-bearing for Ruling 70 and is applied, never questioned.
- **Nothing was declined**, and the boundary that would have made me decline is stated at the
  end under *What would have gone back to the maintainer*. Two of the three came within one
  step of it.

**Numbering continues at 70.** Verified rather than relayed:
`git grep -hoE '^#+ Ruling [0-9]+' origin/main -- docs/plans` yields a maximum of **69**, and
`git grep -nE '\bRuling 7[0-9]\b' origin/main -- docs .claude` returns nothing.

**Evidence tree.** Every measurement below was taken at `f226891`, `origin/main` when this
session started, and re-confirmed at **`2204ffb`** — `origin/main` after W37-2 merged as #567
mid-session, which this record is rebased onto. The `docs/` corpus is unchanged between the
two: `git show --name-only --format= 2204ffb -- docs` is empty, so every count over the note,
the templates and the registers holds at both. The one exception is the three defects in
Ruling 72, which are read from `origin/w37-3-doc-index` at `1c487b8`, the **unmerged** W37-3
branch, and are named with that revision each time. Where a figure is quoted from another
document, the tree that document states is named with it.

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while
`check_plan_acceptance_standard`'s own docstring disclaims exactly that scope. That
disagreement is register finding (F68) — see [`../audit/register.md`](../audit/register.md) —
carried forward with NT-0019's migration as its trigger. It is honoured here rather than
evaded, and the check is not patched from this branch.

1. `git grep -c '^## Ruling 7[0-2] —' docs/plans/2026-09-02-w37-field-set-and-rollup-rulings.md`
   returns `3`, and `git grep -n '^#\+ Ruling ' docs/plans/` shows 70–72 filling the gap
   immediately after Ruling 69 with no duplicate and no skip.
2. Each `### 2. Ruled` subsection names the chosen option **and every rejected option** in its
   opening paragraph, with the measured evidence that separated them.
3. Each ruling carries a `### 4.` section stating its acceptance as **a violation that must
   become detectable**, never as a description of correct behaviour.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-field-set-rulings-70-72` names exactly this one new
   file. No note, no frozen plan, no template, no script and no roadmap row is edited by this
   branch — every change these rulings oblige is work for a named slice.
6. Every numeric claim below names the tree it was measured at and the command that produced
   it, per `CLAUDE.md` §13's reference rule.

---

## Ruling 70 — `decision:` is a register-row field, not an essay header field; the contradiction dissolves rather than needing a widened field set

### 1. Verified first, at `f226891`

The reported contradiction is that NT-0019 §1.2a mandates `decision:` on every finding while
§1.5 declares the header field set closed (*"Unknown field → lint failure"*) and does not name
`decision:` among the family-specific extras it lists.

| Claim | Verdict |
|---|---|
| §1.5's extras parenthesis omits `decision:` | **Confirmed.** It names `deliverable`, `lands_in`, `trigger` for RFC; `gates`, `exit_criteria` for a phase section; `prs:` for a ledger. `decision:` is absent |
| §1.2a mandates `decision:` on a finding | **Confirmed, and the wording is the answer.** *"A finding's **register** disposition ... lives in its own `decision:` field"*. §1.2's FD row: *"`decision:` carries the **register** disposition"*. D0: *"**register** dispositions live in `decision:`"*. Three independent statements, each scoping the field to the register |
| The note says where the register carries it | **Confirmed, and this is the fact the report did not reach.** §5.2's migration cell for `audit/register.md` reads: *"each **row** gains `status:` (`active`, or `closed` where a **Resolved** annotation exists) and `decision:` (the existing Decision cell); the phase register's rows merge in with `phase: P1b` (NT-0003: no second copy)"*. The carrier is the register row, named as such |
| §1.5's closed field set governs the register row | **Refuted.** §1.5 scopes itself: *"On every document-family file, every Reference file, and (as a fenced block under the row's heading) every `WK-`/`SL-` row."* An `FD-` register row is none of the three. §1.5 governs the **essay's** front matter, and `decision:` was never a candidate for it |
| So §1.2a and §1.5 contradict | **Refuted.** They address different carriers. The apparent collision comes from reading §1.5's field set as the finding's whole field set, which its own scope sentence rules out |
| W37-1's merged `docs/_templates/FD.md` put `decision:` in the essay's front matter | **Confirmed**, with a comment declaring it *"this family's declared extra (§1.2's family table)"*. It is the only template extra at `f226891` outside §1.5's parenthesis — an `awk` over the front matter of all thirteen files in `docs/_templates/` returns RFC's three, LG's `plans:` (already in the closed set) and FD's `decision:`, and nothing else |
| An essay can carry `decision:` safely | **Refuted, and this is decisive independent of the wording.** §1.2 makes an `FD-` a *"living row + frozen essay"*, and check 34 permits a frozen file only `status:` (forward only), `superseded_by:`, an append to `corrected_by:`, or — ledgers only — an append to `plans:`. A disposition changes: register row F61's Decision cell at `f226891` still reads *"Two dispositions are open, not one"*, while [`2026-09-01-maintainer-delegation-and-nt-0019-precedence.md`](2026-09-01-maintainer-delegation-and-nt-0019-precedence.md) §7 chose branch (b) and left amending the row to the auditor — a change to that field is owed right now. An essay-borne `decision:` is therefore illegal to update under check 34, or legal only by removing `finding` from check 34's frozen set — which surrenders body-freeze protection on the essay to make one metadata field writable. Both horns are worse than putting the field where the note already puts it |
| §1.5's parenthesis is exhaustive after all | **Confirmed in one direction, refuted in the other, and the divergence runs both ways.** With `decision:` off the essay, every remaining template extra is one §1.5 names. But `prs:`, which §1.5 assigns to a ledger, is declared in no template: `docs/_templates/LG.md` records PRs in a `## PRs` body section instead. So the parenthesis is neither a complete register of extras nor a licensing instrument; its own sentence names the template as both |

### 2. Ruled

**Chosen: `decision:` is a field of the `FD-` register row and is not permitted in an `FD-`
essay's front matter.** The note says so three times in §1 and once in §5.2, its own freeze
machinery makes the alternative unmaintainable, and it needs no widening of §1.5's closed
field set — so **nothing in §1 moves.** §1.2a's *"so `status:` and `decision:` cannot be
confused"* is satisfied at the carrier level as well as the name level: the status the essay
carries and the disposition the row carries are on different artifacts.

**Rejected: reading §1.5's parenthesis as a gloss and licensing `decision:` on the essay via
the template.** This was the reading W37-1 implemented and it is the reading Ruling 69 applied
to the *vendored* parenthesis in the same paragraph, so it deserved the weight it got. It
fails here for a reason that did not apply there: Ruling 69's parenthesis was a **detector**
for a set, and a wrong detector can be replaced by a declaration. This parenthesis sits behind
a **scope sentence** that excludes the register row outright, and the field's own three
definitions name the register. Licensing it onto the essay would also put a mutable value in a
frozen file, which no amount of template declaration fixes.

**Rejected: adding `decision:` to §1.5's closed field set.** That is an edit to §1 —
the maintainer's text, byte-identical in `document-ids.md` — and it would have gone back to
the maintainer rather than being ruled here. It is unnecessary, which is why the question does
not arise.

**Rejected: keeping `decision:` on both the row and the essay.** §5.2's own parenthetical
*"(NT-0003: no second copy)"* is aimed at the phase register, but the mechanism it names is
general and this is the same mechanism: two copies of a value that changes, one of them in a
frozen file, is [`NT-0003`](../notes/0003-duplicated-status-goes-stale.md) with the staler
copy guaranteed in advance.

**The mechanism, in three parts.**

1. **The per-family header field policy is read from `docs/_templates/`, never transcribed
   from §1.5's parenthesis.** §1.5's operative clause is *"declared in that family's template
   and permitted only there"* — the template is the licensing instrument the sentence itself
   names, and it is machine-readable. The permitted set for a family is the set of keys in
   that family's template front matter; the required subset is that set less the keys the
   template's own comment marks conditional. **The parenthesis is illustration of why extras
   exist, not the register of which ones do** — at `f226891` it diverges from the templates in
   both directions at once.
2. **The consequence for `prs:`, stated so it is not re-derived.** §1.5 names it; no template
   declares it; therefore it is not a permitted ledger header field, and a ledger writing it
   fails check 30. `LG.md`'s `## PRs` body section is this repository's ledger PR record, and
   §1.9's PR-title lint reads that. `LG.md`'s comment gains one line saying so, so the next
   reader of §1.5 does not re-open it.
3. **The template's front matter is not at line 1, and this is measured, not predicted.** Every
   file in `docs/_templates/` opens with an HTML comment block, and `scripts/_docid.py`'s
   `parse_header` returns `None` unless `lines[0]` is exactly `---`. Running it over the
   directory at `2204ffb` — the merged W37-2 parser — returns **0 of 13 templates parsed**. A
   check 30 that consumes the templates through the shared parser therefore derives an
   **empty** policy and passes everything, silently, and does so on the very first run. The
   template reader must skip a leading comment block, and check 30 must assert its own coverage
   over `_templates/` rather than infer it from a green run.

### 3. What it obliges

- **W37-4** builds check 30 to reject `decision:` in an `FD-` essay header and to require it on
  every register row; derives the per-family permitted set from `docs/_templates/`; and asserts
  template-parse coverage.
- **W37-4** corrects `docs/_templates/FD.md`: `decision:` comes out of the front matter, and
  the template comment states where the field lives and cites NT-0019 §5.2. The `## Disposition`
  body section stays — it explains the row's value and is the essay's job. **W37-1 is not
  reopened**; the correction is a one-file edit inside the slice that consumes the template.
- **W37-4** adds the `prs:` line to `docs/_templates/LG.md`'s comment.
- **W37-6** rewrites the register's header prose — which §5.2 already requires (*"header prose
  rewritten"*) — so that the row's field set is declared there in one place, since a register
  row is not a header-bearing record and §1.5's template mechanism does not reach it.
- **Nothing in `docs/notes/0019-one-id-per-document.md` or `docs/process/document-ids.md` is
  edited.** §1 stays byte-identical to the maintainer's original.

### 4. Acceptance — the violation that must become detectable

1. **The field on the wrong carrier.** A fixture `FD-` essay whose front matter carries
   `decision:` must fail check 30, and a fixture register row with no `decision:` must fail
   check 30. **Violation: either passes.**
2. **A hardcoded field policy.** Add a key to one template's front matter and a header using
   that key must become permitted; remove it and the same header must red. **Violation: check
   30's verdict on that header is unchanged by editing the template** — which is the signature
   of a policy transcribed into the checker instead of read from the declaration §1.5 names.
3. **Silent empty coverage.** **Violation: check 30 parses zero of the thirteen files under
   `docs/_templates/` and still exits 0.** The count must be reported, not inferred from
   greenness; a check that has never seen a template cannot be enforcing a template-derived
   policy. This is not a hypothetical: the shared parser as merged at `2204ffb` returns exactly
   that zero today, so a check 30 built on it starts in the violating state.
4. **The ledger extra.** A fixture ledger header carrying `prs:` must fail check 30.
   **Violation: it passes** — which would mean the policy came from the parenthesis after all.

---

## Ruling 71 — the phase report's findings element is phase-scoped from the register; project-wide is a defect, not correct behaviour

### 1. Verified first, at `f226891`

The reported defect is that `FD` is absent from §1.5's applicability comments for `phase:`
(*"every WK, SL, PL, LG, RL, CR, RS"*) and `work:` (the same list), so §1.10(c)'s *"findings
opened vs discharged and the unowned-decay count"* cannot be scoped from header fields alone.
`scripts/doc-index.py` at `1c487b8` therefore reports the element project-wide and labels it so.

| Claim | Verdict |
|---|---|
| `FD` is absent from both applicability lists | **Confirmed**, in NT-0019 §1.5 and identically in the verbatim lift at `docs/process/document-ids.md` §1.5 |
| W37-1's `docs/_templates/FD.md` bars both fields from the essay | **Confirmed** — *"`kind:`, `phase:`, `work:`, `slice:`, `plans:`, `supersedes:` and `superseded_by:` do not apply to this family and must not appear here"* — and, given Ruling 70's carrier finding, **correct**. The essay is not where a finding's placement lives |
| The scoping information does not exist | **Refuted, and quantified.** `docs/audit/register.md` at `f226891` has **67 data rows; 67 of 67 carry a Phase cell and 56 of 67 carry a Work-item cell**, counted by an `awk` over the table that begins `\| Finding id \| Concerns \| Work item \| Phase \| Decision \|`. A second register, `docs/audit/phases/1b/register.md`, holds 25 rows. Every finding in this repository is already scoped to a phase, today, before any migration |
| The note carries that scoping forward | **Confirmed.** §5.2: *"the phase register's rows merge in with `phase: P1b` (NT-0003: no second copy); **per-phase views come from `doc-index.py --phase`**"*. §5.5's row for `register-lint.py` / `register-owed.py` names *"`WK-`/`SL-` in the Work-item column"* as surviving work |
| §1.10(c) can be satisfied project-wide | **Refuted by §5.4.** The `phase-review` skill's row reads *"runs `doc-index.py --phase P<n>` and reads the generated report (**which is also the phase's register view**)"*. A per-phase register view whose findings element is project-wide is not a view of that phase's register; it is the whole register with a label |
| So the report must read the essays | **Refuted.** The essays carry no placement and, under Ruling 70, no disposition either. The register row carries both. The report reads the register |
| The unowned-decay count is derivable from an absent `decision:` | **Refuted, and it reads zero by construction after migration.** `doc-index.py` at `1c487b8` computes it as `status == "active" and not extra["decision"]`. The register's own header prose at `f226891` requires the opposite: *"A Decision cell opens with one of ..."* — every row has one — and *"Every row carries one of the five ownership shapes: workstream, event, trigger, next-toucher, unowned-pending-authorisation."* Unowned is an **ownership shape inside the disposition**, not an absent disposition. §5.2 migrates the existing Decision cell into `decision:` unchanged, so after W37-6 the predicate matches nothing and the count is a permanent, silent zero |
| Project-wide is right for the decay count specifically | **Partly — and this is the one place the executor's instinct was sound.** The register's prose: *"Absent a named event it decays to the next `CLAUDE.md` §14 plan review, which must give it a disposition rather than merely list it."* An unowned row from an earlier phase does not stop being the next review's problem. That is a **carry-in**, reported as its own labelled figure, not a reason to leave the phase's own count unscoped |

### 2. Ruled

**Chosen: a defect, fixed in implementation. `doc-index.py --phase P<n>`'s findings element is
derived from `docs/findings/register.md` and scoped by the row's own `phase:`.** No field is
added to any family, no template changes, and §1.5's applicability comments stand exactly as
written — because they govern the essay's header, and the essay was never the carrier for a
finding's placement. Three figures, each labelled with what it counts:

- **opened in P\<n\>** — register rows with `phase: P<n>`.
- **discharged** — of those, rows whose `status:` is `closed` or `retired` (§1.2a: `closed`
  covers *resolved*; `retired` is §1.6's outcome for `decision: accept`).
- **unowned-decay** — of those, rows still `active` whose disposition names no owner and no
  event, **plus a separately labelled carry-in** of rows still `active` and unowned whose
  `phase:` is earlier than P\<n\>. Two numbers, never summed into one.

**Rejected: accepting the project-wide figure with its label.** The label is honest and the
number is still wrong for the use §5.4 names. A phase review reading *"findings opened: 87"*
learns nothing about the phase it is reviewing, and the figure grows monotonically forever.
Honesty about a number's scope does not make it the number that was asked for.

**Rejected: adding `phase:` and `work:` to the `FD-` essay header.** It contradicts §1.5's own
applicability comment, and §1.5 is the maintainer's text — that route would have gone back to
the maintainer, not been ruled here. It also duplicates what the register row holds, which is
the failure mode §5.2 flags in the same sentence.

**Rejected: deriving a finding's phase from its `created:` date against the phase sections'
`opened:` dates.** `docs/_templates/PHASE.md` does carry `opened:` and `target:`, so this is
constructible — and it was my own first answer before I read §5.2. It is wrong because it
invents a derivation the note does not state while a **stated, already-populated** field sits
in the register, and because a finding's phase is not always the phase it was written in: 67
of 67 rows at `f226891` carry a Phase cell that someone set deliberately, and 11 of them name
no work item at all. A date bucket would silently overwrite that judgement.

**Rejected: keeping `not decision` as the unowned predicate.** It is not merely imprecise; it
is a zero by construction the moment §5.2's migration fills every `decision:` — the exact
shape of failure [`NT-0007`](../notes/0007-context-bound-measures-cap-not-discipline.md)
records, where a boundary metric reads zero because of where the boundary sits rather than
because the population is empty.

**The mechanism, in three parts.**

1. **One source, named.** The findings element reads `docs/findings/register.md` and nothing
   else. The essays are not consulted for it, so the essay/row divergence Ruling 70 leaves
   possible cannot reach a reported number.
2. **Coverage is asserted, not inferred.** The count of rows the parser accepted must equal the
   count of data rows in the file, and the report fails loudly when they differ. A register
   whose table shape changes must break the report, not quietly shrink it.
3. **The unowned predicate is stated in the register, tested against a positive control.** The
   ownership shapes are the register's own five; whichever spelling W37-6's rewritten header
   prose fixes on, the test corpus must contain at least one row that the predicate matches and
   at least one it does not, so the number can never be trusted merely because it is small.

### 3. What it obliges

- **W37-3** replaces the project-wide element and its label with the three scoped figures, and
  points the derivation at the register. Its module docstring's second *"interpretation this
  module makes where NT-0019 is silent"* is retired and replaced by a citation to this ruling —
  the note was not silent; the statement was in §5.2 and §5.4 rather than §1.5.
- **W37-4** builds check 33's register-row checks against the same field set, and the
  broken-input proof for the coverage assertion.
- **W37-6** rewrites the register's header prose (§5.2) so the row's fields, including the
  unowned ownership shape, are declared in one place.
- **Nothing in NT-0019 or `document-ids.md` is edited**, and no template gains a field.

### 4. Acceptance — the violation that must become detectable

1. **Unscoped.** A fixture register with rows in two phases, reported with `--phase P2`, must
   count only P2's rows as opened. **Violation: the opened count equals the register's total
   row count** — the project-wide symptom, stated as the thing that must red.
2. **Silently empty.** **Violation: the report renders with a parsed row count lower than the
   register's data-row count, and still exits 0.** A register the parser cannot read must break
   the report; it must not produce a smaller, plausible number.
3. **The zero-by-construction predicate.** A fixture register in which **every** row carries a
   `decision:` and exactly one names no owner must report unowned-decay `1`. **Violation: it
   reports 0** — which is precisely what the `not decision` predicate returns on that corpus,
   and what it will return on the real corpus after W37-6.
4. **Lost carry-in.** A fixture with an `active`, unowned row in P1b, reported with
   `--phase P2`, must show that row in the carry-in figure. **Violation: it appears nowhere in
   the report** — the register's own decay rule dropped on a phase boundary, which is the one
   place it exists to survive.

---

## Ruling 72 — the map-plan roll-up runs through the slices, and has no catch-all

### 1. Verified first, at `1c487b8` (`origin/w37-3-doc-index`, unmerged)

The lead flagged this item as lower confidence and invited a finding that it is not ripe. **It
is ripe.** §1.7's roll-up sentence is *"A map plan rolls up from its slices' leaf plans (all
`closed` → `closed`; any `in progress` → `in progress`)"* — two rules over a seven-value
vocabulary, with no field naming the linkage. `_rollup_map_plan` infers the linkage as
*every `kind: leaf` plan carrying the same `work:`* and completes the rules with
`all in {closed, executed} → executed` and a bare `return "not started"`. The inference is
documented honestly in the function docstring and in the module docstring, which is the
behaviour worth keeping cheap. It is also wrong in three ways that a reader of the docstring
would not predict.

| Claim | Verdict |
|---|---|
| The `work:` proxy is well-founded | **Partly. It is sound in the direction the docstring argues** — a leaf plan's `slice:` resolves to an `SL-` under the same `work:` the map plan carries — **and unsound in the direction that matters**: it enumerates plans, not slices. A slice that has been cut but has no leaf plan yet contributes no child and is invisible to the roll-up |
| Defect 1 — a half-planned Work can read `closed` | **Confirmed by reading the body.** `children` is built from plans only; `if not children: return "not started"`; then `all(s == "closed")`. A Work with five slices where two have closed leaf plans and three have no plan at all yields `children == [closed, closed]` and returns **`closed`**. That is a roadmap reporting progress the repository does not have, which is the failure `CLAUDE.md` §13 exists to prevent |
| Defect 2 — mid-flight reads as not started | **Confirmed.** `states == ["closed", "not started"]` matches no branch and falls to the trailing `return "not started"`. A Work with one slice delivered and one not begun reports **`not started`** |
| Defect 3 — a replanned Work reads as not started | **Confirmed, and it is the worst of the three.** `derive_execution` returns `f"superseded → {superseded_by}"` for a superseded leaf. A slice replanned once and then completed yields `states == ["superseded → PL-m", "closed"]`, matches no branch, and returns **`not started`**. §1.6 makes replanning the normal path (*"planner: new `PL-` with `supersedes:`"*), so this fires on ordinary work, not on an edge case |
| All three share one cause | **Confirmed.** Every one is the trailing `return "not started"` absorbing a combination nobody enumerated. A catch-all in a derivation whose whole purpose is to report state truthfully converts every unhandled case into the most reassuring possible answer |
| §1.7 settles the missing rules | **Refuted.** It states two of them. The rest is genuinely open, which is why this is a ruling and not a bug report |
| The `execution` vocabulary is closed | **Confirmed** — §1.7's table gives exactly `not started`, `in progress`, `executed`, `closed`, `superseded → PL-m`, `retired`, `terminal` |

### 2. Ruled

**Chosen: the roll-up is computed over the map plan's *slices*, one live child per slice, with
an explicit precedence table and no catch-all.** §1.7 says *"its **slices'** leaf plans"*, and
routing through the slices is both what the sentence says and what makes an unplanned slice
visible.

**Children.** For each `SL-` row whose `work:` equals the map plan's `work:`, take that
slice's live leaf plan — the `PL- kind: leaf` whose `slice:` names it and whose `status:` is
neither `superseded` nor `retired`. A slice with no live leaf plan is still a child, and its
state is read from the slice row itself: `draft` → `not started`, `active` → `in progress`,
`closed` → `closed`, `retired` → excluded. A slice with more than one live leaf plan is a
check 33 disagreement, not a case to resolve silently.

**Precedence, in order, over the children that are not excluded:**

| # | Condition | Roll-up |
|---|---|---|
| 1 | no children at all | `not started` |
| 2 | every child excluded, at least one as `retired` | `retired` |
| 3 | any child `in progress` | `in progress` |
| 4 | any child `not started` **and** any child in {`executed`, `closed`} | `in progress` |
| 5 | every child `closed` | `closed` |
| 6 | every child in {`closed`, `executed`} | `executed` |
| 7 | every child `not started` | `not started` |
| — | anything else | **raise; check 33 reports it** |

Rows 3 and 5 are §1.7's two stated rules, in its own order. Row 4 is the correction of defect 2
and is forced by them: a Work part-delivered and part-unstarted is in progress under any
reading of the word. Row 6 completes the vocabulary — everything ran, not everything is closed
out. Rows 1, 2 and 7 are the boundary cases. **The last row is the ruling's substance**: the
derivation has no default, and an unenumerated combination is loud.

**Rejected: keeping the `work:` proxy and only fixing the branch list.** It fixes defects 2 and
3 and leaves defect 1 — the one that reports a half-planned Work as closed — exactly where it
is, because the invisible children are invisible to any branch list.

**Rejected: requiring a new field on the map plan naming its slices.** `plans:` is ledger-only
by §1.5 and a new field is an edit to a closed field set, so this would have gone back to the
maintainer. It is also unnecessary: the linkage already exists, carried by the leaf plan's
`slice:` and the slice row's `work:`, and §1.7's own derivation table is built from exactly
those hops.

**Rejected: leaving the roll-up under-specified and letting check 33 arbitrate.** Check 33
*"fails when the sources disagree"*; it cannot arbitrate a rule that was never written down.
An unwritten rule gets re-invented once per reader, and NT-0019 §1.7's whole design is that
execution is **derived** and therefore has exactly one definition.

**Rejected: declaring the item not ripe and returning it.** The three defects are readable in
the function body at `1c487b8` and each produces a specific wrong value on an ordinary corpus.
Deferring would put check 33 on top of them.

### 3. What it obliges

- **W37-3** replaces `_rollup_map_plan` with the slice-routed derivation and the precedence
  table, removes the trailing catch-all, and keeps the docstring's honest account of what §1.7
  states versus what this ruling adds — citing this record instead of describing the inference
  as its own.
- **W37-4** builds check 33's map-plan comparison against this table, including the
  more-than-one-live-leaf-plan-per-slice disagreement.
- **Nothing in NT-0019 or `document-ids.md` is edited**, and no field is added to any family.

### 4. Acceptance — the violation that must become detectable

1. **The invisible slice.** Fixture: a Work with three slices, one carrying a `closed` leaf
   plan and two carrying no plan and a `draft` slice row. The map plan must read `in progress`.
   **Violation: it reads `closed`** — defect 1, stated as the value that must never appear.
2. **Mid-flight.** Fixture: two slices, one `closed` leaf plan, one `not started`. The map plan
   must read `in progress`. **Violation: it reads `not started`** — defect 2.
3. **Replanned then completed.** Fixture: one slice whose leaf plan A is `superseded` by leaf
   plan B, with B `closed`. The map plan must read `closed`. **Violation: it reads
   `not started`** — defect 3.
4. **No catch-all.** Fixture: a Work every one of whose slices is `retired`. The map plan must
   read `retired`. **Violation: it reads `not started`** — a value produced by a default rather
   than by a rule, which is the single cause all three defects share and the property this
   ruling exists to remove.

---

## What would have gone back to the maintainer

Stated so the boundary is visible rather than implied, and so a future reader can tell that the
delegation was read narrowly by the party it empowered. Two of the three came within one step
of it.

- **Widening §1.5's closed field set** to admit `decision:` on an essay header, which was the
  obvious repair for Ruling 70's reported contradiction. It is an edit to §1 — the maintainer's
  own text, byte-identical in `document-ids.md` — and it would have gone back. It is not made,
  because the field belongs on the register row and §1.5 never reached it.
- **Adding `phase:` and `work:` to the `FD-` essay header**, which was the obvious repair for
  Ruling 71. Same reason: it contradicts §1.5's own applicability comment, so it would have
  gone back. It is not made, because §5.2 already puts the placement on the register row.
- **Any edit to `docs/process/document-ids.md`.** §1.6 makes `process/` the maintainer's,
  amendable only by an `RFC-` plus an `RL-`, and the file declares itself a verbatim lift.
  None is made.
- **Any change to NT-0019 §2's D0–D14.** None is made. D0 is applied in Ruling 70 and is the
  reason its answer is a carrier question rather than a field-set question.
- **Reopening W37-1.** Not needed and not proposed: the two template corrections Ruling 70
  obliges are one-file edits inside W37-4, the slice that consumes the templates and that has
  not been dispatched.

## Provenance

Written 2026-09-02 by the decision-maker role, under the maintainer's delegation of 2026-09-01
as routed by the lead — recorded above with its date, and recorded there also as **not
load-bearing**, because
[`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) already reaches all
three. **The maintainer did not rule any of these personally.**

Every claim in each `### 1.` table was checked against the repository in this session by the
command named beside it — at `f226891` for the note, the templates and the registers, and at
`1c487b8` for `scripts/doc-index.py`, which is unmerged and named with that revision every time
it is cited. **Nothing was taken from the lead's relay.** Two of the three items were relayed
with a framing this record does not adopt: item 1 was relayed as a contradiction between §1.2a
and §1.5 requiring one of them to yield, and is ruled instead as two carriers that never
collided; item 2 was relayed as a question about `phase:` applicability, and is settled by §5.2
and §5.4, which the relay did not cite and which say the opposite of the answer the §1.5
reading suggested. Item 3's framing — an inference documented in a docstring, offered with low
confidence — was accurate, and the defects it leads to were found by reading the function body
rather than the docstring.
