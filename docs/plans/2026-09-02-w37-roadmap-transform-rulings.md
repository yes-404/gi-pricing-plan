# What the roadmap transform produces — closed works, multi-row works, and the archival mention, ruled (2026-09-02)

**What this is.** Three questions routed together by the lead because they are one subject: what
`§4 step 3` actually emits. `_discover_roadmap` converts 0 of 41 works today and the executor
rebuilding it refuses all-or-nothing rather than converting the unambiguous subset — *"a file
with some works converted and others still in legacy prose is a fourth, worse shape"* — so these
three block the restructure entirely. Ruled below as Rulings 90, 91 and 92.

**None of the three is the maintainer's.** The lead offered to carry Q1 in the go-ahead package
on the ground that it touches what the roadmap *means*. It does not need to: **acceptance item
(k) already decides it**, mechanically, and §1 below shows how. The other two are settled by
§1.2's own columns and by a dependency reference in the corpus.

**One thing found while verifying, which the routing brief had slightly wrong and which changes
Q3's grounds rather than its answer.** `W6`'s row is **not** under *"Original scope, for
reference"*. That heading (line 317) contains only Goal and Demo-able-outcome prose; `W6`'s row
is at line 336, under the **sibling** heading `### Workstreams` (327). Q3 therefore cannot be
answered by asking how far an archival heading's scope reaches — and it does not need to be.

## Authority

- **Routed by the lead** under the maintainer's delegation of 2026-09-01
  ([`2026-09-01-maintainer-delegation-and-nt-0019-precedence.md`](2026-09-01-maintainer-delegation-and-nt-0019-precedence.md))
  §1; none of the three falls in its §2 exclusions, and §2 of each ruling below says what makes
  it a derivation from the standard rather than a scope choice.
- **Every figure is measured at `f4cbbb7`**, `origin/main`'s tip when this record was written
  and this branch's base.
- **No note, template or filed plan is edited.** Two limitations in the standard are surfaced
  for the maintainer's `RFC-` route rather than worked around silently.

## Acceptance Standard

`audit-docs.py` check 28 requires this section on dated `docs/plans/` files outside four
suffixes while its own docstring disclaims that scope — register finding F68, whose discharge
Ruling 87 showed unsound. Honoured; the check is not patched from this branch.

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 90–92 immediately after 89, no duplicate, no
   skip.
2. Each ruling states the chosen answer **and what happens to what it does not choose** — the
   lead's explicit condition on Q2, applied to all three.
3. Each acceptance is a violation that must become detectable.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-rulings-90-92-roadmap-transform` names exactly this
   one new file.
6. Every count and every heading attribution below was produced by the command shown, not read
   off a summary — including the one that corrected the routing brief.

---

## Ruling 90 — a work recorded as closed converts, as a `WK-` row with `status: closed`

### 1. Verified first, at `f4cbbb7`

**§1.2's `WK` row supplies the vocabulary directly:**

```
| Row | Work | `WK` | docs/roadmap.md, under its milestone | one work item | living row
| draft → active → closed | retired | — |
```

`closed` is in the subset. A standard that offers a status for closed works and then does not
emit them would have written a word it never uses.

**And acceptance item (k) settles it mechanically.** §7(k) requires *"`doc-index.py --phase P1b`
produces the report §1.10 describes"*. `phase_report` (`scripts/doc-index.py:811`) opens with:

```python
closed_works = [w.header for w in work_headers if w and w.header.status == "closed"]
retired_works = [w.header for w in work_headers if w and w.header.status == "retired"]
```

**Its first line is a count of closed and retired works.** P1a and P1b are the closed phases. If
closed works do not convert, (k)'s report for the phase it names reports zero closed works —
a report that is not the one §1.10 describes, on the phase the acceptance item picks.

### 2. Ruled

**A work recorded as closed converts, as a `WK-` row carrying `status: closed`, under its
milestone.** The six ids the executor blocked on — `W7a`, `W9`, `W10`, `W11`, `W32`, `W33` —
convert on that basis.

**Why this is not the maintainer's**, which the lead invited me to test: the question reads like
one about what the roadmap means, and it is answered without deciding that. §1.2 supplies the
status word and §7(k) requires a report that counts it. **A ruling that has to choose between
two readings of the roadmap's purpose would be the maintainer's; this one only reads the
standard.**

**`status:` comes from the Status cell, never from the decoration.** Ruling 83 §1(g) established
that `W5` and `W7` each head rows carrying both the struck and unstruck forms, so a strike is
typography. The date and word in the Status cell are the source.

### 3. What happens to what it does not choose

Nothing is dropped: this ruling adds no exclusion. The alternative — not converting closed
works — would have silently removed 6 ids from the corpus and left every citation of them
unresolvable, which is the shape §4 step 3 exists to prevent.

### 4. Acceptance — the violation that must become detectable

**The violation: a work with a closed Status cell is absent from the migrated roadmap.**

- **`doc-index.py --phase P1a` and `--phase P1b` each report a non-zero closed-work count**, and
  the ids match the Status cells read from the pre-migration file. *Violation: a phase report
  whose closed-work list is empty for a closed phase* — which is the state the rejected reading
  produces, and it passes every other check.
- **A count assertion with its denominator: 41 work ids in, 41 `WK-` rows out.** *Violation: a
  conversion that silently drops a partition.* Derived from the census, not hand-written
  (Ruling 83).

---

## Ruling 91 — a work's several rows merge into one `WK-` row; every row's prose survives in its body

### 1. Verified first, at `f4cbbb7`

**56 leading rows over 41 ids**, nine ids with more than one. A work heads a row in up to three
tables: a phase *plan* table, a phase *status* table, and the original-scope table.

**The rows agree on status and differ in prose.** This is the fact the question turns on and it
was not in the brief. `W1`'s three rows (207, 218, 331) and `W5`'s three (232, 283, 335), Status
cells only:

```
W1  207  **Closed 2026-08-14** — see the status table below
W1  218  ✔ **closed 2026-08-14**
W1  331  **Closed 2026-08-14** — see the status table below

W5  232  ✔ **closed 2026-08-22** — see docs/audit/closure-records.md
W5  283  **Closed 2026-08-22** — 110 built · 10 declared-and-refused-by-name · 16 unevidenced …
W5  335  **Closed 2026-08-22** — 136 in scope at close, of which 110 built. All ~~124~~ MODEL …
```

**Same word, same date, three different amounts of detail.** So the merge does not have to
arbitrate a status conflict — it has to avoid losing prose.

### 2. Ruled

**One `WK-` row per work id, under the milestone of the phase the work was executed in. The
several source rows merge; they do not become several rows and none is chosen over the others.**

§1.2 fixes it: the unit is *"one work item"* and the row lives *"under its milestone"* — singular
on both counts. Three rows for `W1` would be three ids for one work, which is the thing
[`NT-0019`](../notes/0019-one-id-per-document.md) is titled after.

### 3. What happens to what it does not choose — the lead's condition, answered

**Three obligations, because "merge" without them leaves the executor to invent the hard part.**

1. **`status:` is taken from the Status cells, which must agree.** Verified agreeing for `W1` and
   `W5`. **Where they disagree, `migrate` refuses and names the work and its rows** — it does not
   pick the first, the last, or the richest. A status conflict across a work's own rows is a
   data defect in the roadmap, and resolving it is a human's.
2. **Every source row's Notes prose is preserved in the merged row's body, each labelled with
   the table it came from.** `W5`'s three cells carry three different measurements — a pointer
   to the closure record, a delivery breakdown, and a scope-at-close figure. **Dropping two
   thirds of that is a content loss the standard nowhere authorises**, and the richest cell is
   not a superset of the others.
3. **The tables the rows came from are not silently deleted.** They are prose a reader uses
   today. Whether the restructure keeps them, folds them, or replaces them is the executor's —
   **but the migration diff must show what happened to each**, and a table that vanishes with no
   hunk accounting for it is a violation, not a tidy-up.

### 4. Acceptance — the violation that must become detectable

**The violation: a work's content is reduced by the merge without the diff saying so.**

- **41 ids in, 41 `WK-` rows out, and no `WK-` id appears twice.** *Violation: a work with two
  rows, or a work with none.*
- **For each of the nine multi-row works, the merged body contains a fragment from every source
  row.** *Violation: a merge that keeps one cell and drops the rest.* `W5` is the positive
  control: three cells, three distinct figures, all three must be findable after the merge.
- **A fixture in which one work's two rows carry different status words must make `migrate`
  refuse**, naming the work. *Violation: a status conflict resolved by precedence rather than by
  refusal* — the check that proves obligation 1 is real rather than aspirational.

---

## Ruling 92 — `W6` converts, as a `WK-` row with `status: retired`

### 1. Verified first, at `f4cbbb7` — and the brief's premise corrected

**`W6`'s row is not under the archival heading.** Measured:

```
317  ### Original scope, for reference     ← Goal + Demo-able outcome prose only, 317–326
327  ### Workstreams                       ← sibling heading; W6's row is at 336, under this
```

Both are `###` siblings under `## Historical record` (269) — **whose own body says it is a
signpost, not a container**: *"This page is the forward-looking plan; the archive is at
`docs/audit/README.md`."* It is also the only unnumbered `##` in a file whose other eleven are
numbered. **So the nesting that would have to answer Q3 as posed is itself unreliable**, and
this is the third instance of that shape in this migration, after `plan-reviews.md`'s single
level-2 heading and `#### Phase 1b status` sitting inside `### Phase 1a`.

**The question does not need the nesting, because a dependency answers it.** Line 337:

```
| **W7** | freMTPL2 demo seed **and the demo entrance** | W4, W5, W6 | …
```

**`W7`'s `Depends on` cell names `W6`.** If `W6` does not convert, that dependency names a work
with no `WK-` id, and §1.7's resolver — which requires `WK-0*(\d+)` — cannot reach it. `W6` is
also referenced in the roadmap's own prose at 339 and in one filed plan.

**What `W6` is:** the pre-split frontend work, re-cut into `W6a` and `W6b`, both of which have
their own rows and are closed. The heading above its table says the original goal is *"now
superseded by the split above"*.

### 2. Ruled

**`W6` converts, as a `WK-` row with `status: retired`, its body naming `W6a` and `W6b` as the
works its scope was re-cut into.**

**`retired`, not `closed`.** §1.2a: `retired` is *"ended without completing — withdrawn, dropped,
rejected, deprecated, archived; **the reason is in the body**"*. `W6` ended without completing
*as `W6`*; its scope was delivered under two other ids. `closed` — *"completed its purpose"* — is
false of `W6` itself.

**`superseded` would be the exact word and is not available.** §1.2's `WK` status subset is
`draft → active → closed | retired`; `superseded` is not in it, and §1.2a is explicit that *"a
family uses a subset and never a synonym"*. So `retired` is the available term and the precision
lost goes into the body, where §1.2a says the reason belongs. **This is a real limitation of the
row vocabulary meeting a real case, and it is surfaced below rather than worked around.**

**Rejected: dropping `W6` as archival-only.** It is a live dependency target (§1). Dropping it
converts a resolvable reference into a dangling one inside the commit that cannot be re-run.

**Rejected: deciding it by how far the archival heading's scope reaches.** §1 shows that
question has no reliable answer in this document — and answering Q3 by it would have made the
outcome depend on a nesting the file does not honour.

### 3. What happens to what it does not choose

The archival framing is not discarded: *"now superseded by the split above"* is exactly the
reason §1.2a requires in the body, so the prose that would have justified dropping `W6` becomes
the justification for its `retired` status instead.

### 4. Acceptance — the violation that must become detectable

**The violation: a work id referenced by another row's dependency has no `WK-` row.**

- **Every work id named in any `Depends on` cell resolves to a `WK-` row after the migration.**
  *Violation: a dependency naming a work that does not exist.* `W6` is the positive control and
  the corpus supplies it — the check must fail today under the drop-it reading.
- **`W6`'s migrated row is `status: retired` and its body names `W6a` and `W6b`.** *Violation: a
  retired row with no reason* — which §1.2a requires and no check enforces.

---

## Surfaced for the maintainer's `RFC-` route — two vocabulary limits, batched

Neither blocks anything; both are cases where the corpus is wider than §1's words, found by
migrating rather than by reading. They join the `exit_criteria` / `exit criteria` divergence and
§8's *"eleven primary skills"* already on that route.

1. **`WK` has no `superseded`.** Ruling 92 uses `retired` for a work whose scope was re-cut into
   named successors, because the subset offers nothing better. Document families have
   `superseded` and `superseded_by:`; the two row families that can be re-cut — `WK` and `SL` —
   do not.
2. **`## Historical record` is a signpost at container level.** Not a standard defect, but the
   roadmap restructure will have to decide where its two lines go, and its own body says the
   archive is elsewhere.

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **Which milestone section a multi-phase work sits under** | Ruling 91 fixes *"the phase the work was executed in"*; if any work was executed across two phases the rule needs a tie-break, and I did not measure whether one exists | **W37-6's executor**, as a measurement; a new finding only if a work spans phases |
| **Whether the restructure keeps, folds or replaces the source tables** | An editorial choice about the migrated document, not a standard question. Ruling 91 §3 item 3 constrains only that the diff must account for each | **The executor**, with the lead reviewing the shape |
| **The `#### Phase 1b status` inside `### Phase 1a` mis-nesting** | A structural defect in a governed document, same class as Ruling 82 §3 item 4 | **The lead**, as a finding — the roadmap's instance of a shape now seen three times |
| **Whether `owner:` follows §1.6 or the historical author** | Routed at Ruling 88 and still open | **The planner**, unchanged |

## Provenance

Routed by the lead on 2026-09-02 as one package, with rulings requested rather than options, an
explicit invitation to hand Q1 to the maintainer, and a condition that any answer to Q2 must say
what happens to the rows it does not choose. Q1 is ruled rather than handed over, on the ground
in Ruling 90 §2. Q3's premise was corrected by measurement before it was answered, and the
answer rests on a dependency reference rather than on the nesting the brief assumed.
