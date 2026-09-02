# W37-6 — the twelve non-close records in `closure-records.md`: a family derivation

**Goal:** Answer the question [Ruling 78](2026-09-02-w37-6-leaf-plan-findings-rulings.md) §2
part 3 routes here — *"Which family the other twelve take is the planner's derivation under
§5.2's own rules"* — as an **enumerated table with a stated expected output**, not as a
predicate exercised once and trusted. Ruling 78 fixes only that the twelve may not be `CR-`
and may not be dropped; the positive answer is this document's.

**Architecture:** A derivation, not a plan. It carries the 21-row table Ruling 78 §2 part 1
requires W37-6's ledger to hold, one row per `###` heading, with its destination family and
`kind:`. Two of the three shapes are determined by NT-0019 §5.2 and §5.4's own rules and are
decided here. **The third is not determined by §5.2, for a reason that has nothing to do with
these records**, and is handed back with options and a recommendation rather than stretched to
fit — the outcome the dispatch named as legitimate.

**Spec:** [`../notes/0019-one-id-per-document.md`](../notes/0019-one-id-per-document.md) §1.2
(the family table, its units and status subsets), §1.5 (the closed field set, declared per
family in `docs/_templates/`), §1.6 (roles per family), §5.2 (the `docs/` impact rows) and
§5.4 (the bespoke-audit rule). Rulings [77 and 78](2026-09-02-w37-6-leaf-plan-findings-rulings.md).

**Filed:** 2026-09-02 (UTC), against `origin/main` at **`9367eac`** — the tree after W37-5
(`doc-id.py migrate`) merged as #578. `docs/audit/closure-records.md` is byte-identical between
`6d03a5e` and `9367eac` (`git diff --stat 6d03a5e 9367eac -- docs/audit/closure-records.md` is
empty), so the enumeration below holds at both. Frozen at this date.

---

## Acceptance Standard

Each item is a violation that must become detectable. Item 1 is the one this document exists
for: it converts a private judgement into a test, which is Ruling 78's whole point.

1. **The enumeration is asserted before the split, not after.** Before `migrate` runs, the
   executor derives the 21 `###` headings from `docs/audit/closure-records.md` and compares
   them line-for-line against §1's table. **Violation: any heading in the file that §1's table
   does not carry; any row in §1's table whose line number or verbatim heading text does not
   match the file; or a total that is not 21.**
2. **The split's output is asserted against the destination column.** After the split,
   **exactly 9** documents derived from this file are `CR-` — 8 `kind: work` and 1
   `kind: phase` — and **exactly 2** are `RS- kind: audit`. **Violation: any `CR-` whose body
   contains `in progress, not closed`; a `CR- kind: work` for the Phase 1a record; a `CR-` for
   either audit record; or a count other than 9 and 2.**
3. **Every heading is accounted for, and absence is loud.** **Violation: fewer than 21
   `REDIRECTS.csv` rows sourced from this file's headings**, or any heading whose body lines
   appear inside a document derived from a *different* heading. §4 shows this is not
   hypothetical: the merged implementation does exactly that today for eleven of the 21.
4. **The undetermined ten are not silently assigned.** **Violation: the ten W5 slice records
   materialising as any family before the decision §3 asks for is recorded**, or materialising
   as `LG-` with a `slice:` value that resolves to no roadmap row.
5. **The same defect class is swept, not just its reported instance.** `plan-reviews.md` gets
   its own enumerated table under the same rule. **Violation: a `CR- kind: review` minted from
   any of the three `## Pending proposals` candidates, or any of the three dropped.**

---

## 1. The enumeration — 21 rows, derived from the file

Derived by `git show 9367eac:docs/audit/closure-records.md | grep -nE '^### '`, not taken from
any report. Line numbers are the file's own. **21 = 8 work closes + 1 phase close + 12
non-close records**, which is the arithmetic behind Ruling 78's twelve: the ninth close is a
*phase*, not a work, which is why "only 8 of 21 are work closures" and "twelve are not closes"
are both true at once.

| # | Line | Heading (verbatim) | Destination | Determined by |
|---|---|---|---|---|
| 1 | 8 | `Phase 1a — exit demo accepted 2026-08-15` | `CR-`, **`kind: phase`** | §1.2 (`CR` unit is *"one work, phase or review close"*); §5.2's `audit/phases/1b/README.md` row |
| 2 | 40 | `W6b — the frontend of Phase 1b: closed 2026-08-27` | `CR-`, `kind: work` | §5.2 |
| 3 | 227 | `W7 — freMTPL2 modelling half: closed 2026-08-27` | `CR-`, `kind: work` | §5.2 |
| 4 | 323 | `W32 — the backend of Phase 1b: closed 2026-08-24` | `CR-`, `kind: work` | §5.2 |
| 5 | 920 | `W5 — Modelling: closed 2026-08-22` | `CR-`, `kind: work` | §5.2 |
| 6 | 1121 | `Independent audit — 2026-08-15, and what it changed` | **`RS-`, `kind: audit`**, owner auditor | §5.4's bespoke-audit rule; §5.2's `w11-process-conformance-audit.md` row |
| 7 | 1175 | `W7b — The demo entrance: closed 2026-08-15` | `CR-`, `kind: work` | §5.2 |
| 8 | 1271 | `W6a — Frontend Data Workbench: closed 2026-08-15` | `CR-`, `kind: work` | §5.2 |
| 9 | 1376 | `W7a — freMTPL2 data seed: closed 2026-08-15` | `CR-`, `kind: work` | §5.2 |
| 10 | 1429 | `W4 — Data Workbench: closed 2026-08-15` | `CR-`, `kind: work` | §5.2 |
| 11 | 1555 | `W4 mid-workstream scope findings — 2026-08-14` | **`RS-`, `kind: audit`**, owner auditor | §5.4's bespoke-audit rule |
| 12 | 1862 | `W5 — the GLM spine, 2026-08-15 *(in progress, not closed)*` | **UNDETERMINED — §3** | §5.2 points at `LG-`; `LG-` is unusable |
| 13 | 1904 | `W5 — bandings and groupings, 2026-08-15 *(in progress, not closed)*` | **UNDETERMINED — §3** | as above |
| 14 | 1982 | `W5 — the factor workbench, 2026-08-15 *(in progress, not closed)*` | **UNDETERMINED — §3** | as above |
| 15 | 2014 | `W5 — diagnostics, and the holdout that was not one, 2026-08-16 *(in progress, not closed)*` | **UNDETERMINED — §3** | as above |
| 16 | 2073 | `W5 — spec validation, and the half of FR-MODEL-81 the last slice missed, 2026-08-16 *(in progress, not closed)*` | **UNDETERMINED — §3** | as above |
| 17 | 2107 | `W5 — the model lifecycle, and \`If-Match\` against a real precondition, 2026-08-17 *(in progress, not closed)*` | **UNDETERMINED — §3** | as above |
| 18 | 2160 | `W5 — model comparison, and the artifact the spec never defined, 2026-08-17 *(in progress, not closed)*` | **UNDETERMINED — §3** | as above |
| 19 | 2223 | `W5 — \`wf-01\`'s citation audit, 2026-08-17 *(in progress, not closed)*` | **UNDETERMINED — §3** | as above |
| 20 | 2269 | `W5 — gradient boosting on both backends, 2026-08-17 *(in progress, not closed)*` | **UNDETERMINED — §3** | as above |
| 21 | 2343 | `W5 — \`wf-01\` driven end to end, 2026-08-17 *(in progress, not closed)*` | **UNDETERMINED — §3** | as above |

**The twelve are three shapes, not one.** Rows 6 and 11 are audit records; rows 12-21 are
per-slice delivery records. Treating them as one class is what produced a single wrong
predicate, and it is why this table has a `Determined by` column per row rather than a rule
stated once.

---

## 2. The two that §5.2 and §5.4 determine

### 2.1 Row 6 — `Independent audit` → `RS-`, `kind: audit`, owner auditor

Read rather than inferred from the title. The record opens: *"Five auditors ran over Phase 1a's
closed work, none of them allowed to read the closure records they were auditing: each derived
what should exist from the specs and then went looking."* It states its method, carries a
`Claim | What was true` evidence table, and reports findings — one of which
(*"pandera as the Layer-1 mechanism … a dependency of nothing"*) is still cited in `CLAUDE.md`
§3 today.

**§5.4's bespoke-audit rule is on point and is quoted, not paraphrased:** *"a bespoke audit is a
slice whose record is a research document of kind `audit`, owner the auditor, every finding its
own finding record; **never a plan, never a closure**."* §5.2 supplies the worked precedent in
its own table — `plans/2026-08-29-w11-process-conformance-audit.md` →
*"`research/RS-0nnnn-w11-process-conformance-audit.md`, `kind: audit`, owner auditor"*. Ruling 77
applied the same rule to the auditor's NT-0019 sweep record. Three independent statements of one
rule, all pointing the same way.

`RS-`'s status subset is `draft → active → closed | retired` (§1.2), so a historical, discharged
audit takes **`status: closed`** — which `CR-` could not express and is half of why it is not a
`CR-`.

### 2.2 Row 11 — `W4 mid-workstream scope findings` → `RS-`, `kind: audit`, owner auditor

The same rule, and the record is the same shape one workstream down. It opens *"**W4 is roughly
half delivered, and the requirement-coverage number said otherwise.** `scope-audit.py DATA`
reported 44 of 50 requirements evidenced — 88 % — which reads as nearly finished. It is not"*,
and carries a `Check | Result` table (`0 of the 28 endpoints`, `19 of 50`). That is the audit
method — derive the expected scope from the spec, measure the delivered position, report the
gap — applied mid-workstream instead of at a close.

**`kind: audit`, not `kind: measurement`.** §1.2 gives `RS` the three kinds
`spike · measurement · audit`. A measurement reports a number against a budget; this reports a
*position against a specification*, which is what §5.4's rule calls an audit, and it names
findings rather than values.

**No `FD-` rows are minted retroactively from either record.** §5.2's precedent is precise about
this: the `w11-process-conformance-audit.md` row promotes *"its two **unowned follow-ups**"* to
`FD-` rows, not its findings generally. `docs/audit/register.md` holds **open** findings, so a
finding already discharged by the work that followed does not gain a row now. **This is stated
as a falsifiable rule rather than a judgement:** *any finding in either record that is still open
and unowned at the migration tree gets an `FD-` row; any that is discharged does not.* The
executor checks each against the register rather than assuming the count is zero.

---

## 3. The ten that §5.2 does not determine — handed back

### 3.1 The family §5.2 points at, and why the content agrees

The ten are per-slice delivery records. The clearest evidence is that one of them says so
outright — row 12's closing paragraph: *"**W5 is not closed and this is not a closure record.**
It is one slice of … requirements, written down so the next one starts from what is true."* Each
carries a `Delivered | Evidence` table, a numerically-stated not-delivered position
(*"`scope-audit MODEL --endpoints` reads **4 of 23**"*), and the spec corrections found by
building it.

§1.2 gives exactly one family that unit: **`LG` — Ledger — `docs/ledgers/` — *"one slice's
execution"* — append-only — `active → closed`.** And §5.2 supplies the precedent in its own
table: *"16 `-ledger.md` → `ledgers/`"* — an existing per-slice execution record becomes an
`LG-`. The ten are the same content written before the `-ledger.md` convention existed.

### 3.2 Why `LG-` cannot be used, measured

**`docs/_templates/LG.md` declares `slice: SL-NNNNN` in its front matter and does not mark it
conditional.** Its comment marks `kind:`, `supersedes:`, `superseded_by:` as inapplicable and
`prs:` as not permitted; `slice:` is named in none of those. Under Ruling 70's mechanism — *"the
permitted set for a family is the set of keys in that family's template front matter; the
required subset is that set less the keys the template's own comment marks conditional"* —
`slice:` is **required** on every ledger, and check 30 enforces it.

**There is no `SL-` for any of the ten to name, and not because of anything about W5.**
Measured at `9367eac`:

```
git show 9367eac:docs/roadmap.md | grep -cE '^\| \*\*W[0-9]+[a-z]?-[0-9]+\*\*'   →  0
```

**`docs/roadmap.md` carries zero per-slice rows for any work in the project.** Every bolded row
is a work (`W4`, `W5`, `W32`, `W30`…), never a slice. W5's own row names twenty-eight slices in
prose and then says *"The slice records in `docs/audit/closure-records.md` are the list"* — the
roadmap points at the very file being dissolved.

So NT-0019 §4 step 3's *"each slice an `SL-` row under it"* **has no source in the roadmap to
convert**. This is not a W5 problem and not a problem with these twelve: it blocks the `slice:`
field of all 16 existing `-ledger.md` files equally, and it is the reason `LG-` is unavailable
here.

**One clarification, so the severity is not overstated.** Check 33's *"`work:`/`slice:`/`phase:`
resolving to roadmap rows"* sub-clause is **not implemented today** — its own docstring says
those sub-clauses *"need a corpus with roadmap/ledger/OQ content that does not exist inside"* the
S1 scope. So the failure today is check **30**'s (a required field absent), not check 33's. The
resolution clause becomes buildable precisely when W37-6 widens the corpus, which is when a
`slice:` naming nothing would start to red.

### 3.3 Options, with a recommendation — the decision is not this role's

`CLAUDE.md` §10: a genuinely open design choice is recorded with options and a recommendation,
never silently picked.

| # | Option | Assessment |
|---|---|---|
| (a) | `LG-`, with `SL-` rows minted retroactively for W5's slices | **Rejected.** §1.6 makes `SL` *"planner, cut in the map plan"*; W5 had no map plan. The roadmap names 28 slices in prose and only 10 have records, so minting from the records leaves 18 named-but-rowless and minting from the prose invents 28 rows of history nobody cut |
| (b) | `RS-`, `kind: audit` or `measurement` | **Rejected.** Wrong unit. These are delivery records, and row 12 explicitly distinguishes itself from the audit shape |
| (c) | `CR-` | **Rejected by Ruling 78**, and independently by §1.2: `CR`'s status subset is the single value `active`, with no non-closed member |
| (d) | Consolidate the ten into one document | **Rejected.** Destroys the per-slice unit that is the only record of ten slices, and matches no §5.2 rule |
| (e) | **`LG-`, with `slice:` made conditional in `docs/_templates/LG.md` for a ledger predating the `SL-` family, carrying `work:` only** | **Recommended.** Minimal, uses the licensing route Ruling 70 already established, and fixes the same blockage for all 16 existing ledgers rather than only these ten |

**Why (e) still needs a ruling rather than being taken here.** Making a declared field
conditional is narrower than adding one to §1.5's closed set — Ruling 70 held that adding
`decision:` *"is an edit to §1 … and it would have gone back to the maintainer"* — but it is not
cosmetic: §1.7 computes a plan's *execution* axis by routing through slices, so a ledger with no
`slice:` is invisible to that derivation. That consequence belongs to whoever owns the
derivation, not to the planner filing the record. **Recommendation (e), decision to the
decision-maker; the `SL-`-rows-do-not-exist defect underneath it is a spec question about §4
step 3 and is larger than these ten records.**

Rows 12-21 stay `UNDETERMINED` in §1's table until that is recorded, and Acceptance Standard
item 4 makes materialising them early a detectable violation.

---

## 4. A finding against merged code — `migrate` produces 10 of 21, not 21

Run, not reasoned about, against `scripts/doc-id.py` at `9367eac` (load the module, call
`_discover_closure_records(repo_root)`, compare its drafts to the file's `^### ` headings):

```
### headings in the file : 21
drafts migrate produces  : 10
prefixes: ['CR']   kinds: ['work']   statuses: ['active']
```

`_discover_closure_records` passes a hard-coded `"CR"` and `_discover_headed_split_file` sets
`kind="work"` for every draft, so **every record it does produce is a `CR- kind: work`** —
including row 1, which is a phase close, and row 11, which is not a close at all.

**And eleven headings produce no draft.** `_CLOSURE_HEADING_RE` requires the heading to end with
its date (`(\d{4}-\d{2}-\d{2})\s*$`). The ten W5 records end with `*(in progress, not closed)*`
**after** the date, and row 6 ends with `, and what it changed`. None matches. Because
`_discover_headed_split_file` slices each section from one *matched* heading to the next, the
eleven unmatched records' body lines **fold into the preceding matched record**:

- Row 6 (`Independent audit`) folds into row 5, the **W5 closure record**.
- Rows 12-21 (all ten W5 slice records) fold into row 11, `W4 mid-workstream scope findings` —
  producing one `CR- kind: work` document containing ten slice records **for a different
  workstream**.

**Acceptance (g) does not catch this.** Ruling 68 class 4 requires the outputs' concatenation to
reproduce the input's body lines in order; it does, because nothing is dropped — only
misattributed. **Ruling 78's acceptance item 2 does catch it, but only by its second limb:** the
tree would hold 10 `CR-` documents rather than 21, so the *"21 `CR-` documents"* clause stays
silent, while *"fewer than 21 `REDIRECTS.csv` rows sourced from that file's headings"* fires.
That limb is load-bearing and should not be trimmed.

This is the "branch open across a ruling's merge" hazard in its concrete form: W37-5 was in
flight when Ruling 78 merged, so its splitter implements the shape Ruling 78 forbids. **It is a
finding against the merged implementation, not against W37-5's executor**, and it is filed here
rather than fixed here because `scripts/` is not this role's to write.

---

## Self-review

- **Every figure re-derived at a named tree.** 21 headings, 8 work closes, 1 phase close, 12
  non-close records, 0 per-slice roadmap rows, 10 drafts from 21 headings — all at `9367eac`,
  each with the command that produced it. The lead's relayed figures were re-derived rather than
  taken, as the dispatch required, and they reproduce.
- **Enumerated and asserted, not judged once.** §1 is a 21-row table; Acceptance Standard item 1
  asserts it against the file before the split, which is the shape Ruling 78 ruled for.
- **Every id cited individually.** Rulings 68, 70, 77 and 78 are each named where they bind; no
  bare numeric range appears.
- **The undetermined case is handed back rather than stretched.** §3 gives five options, a
  recommendation, and the reason the decision is not the planner's — and names the larger §4
  step 3 defect underneath it rather than routing around it.
- **A claim about content was read, not inferred from a title.** Rows 6, 11 and 12 were each
  opened and quoted; the classification rests on what the records say they are, and row 12 says
  so in its own words.
- **No acceptance line.** Nothing here is accepted by its author.
