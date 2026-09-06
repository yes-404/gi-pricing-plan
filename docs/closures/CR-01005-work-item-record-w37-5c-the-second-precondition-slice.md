---
id: CR-1005
family: closure
kind: work
title: Work-item record — W37-5c (the second precondition slice)
status: active                  # write-once; this is the only value this family ever takes
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/work/W37-5c/README.md
---

# Work-item record — W37-5c (the second precondition slice)

Follows [`close-workstream`](../../.claude/skills/close-workstream/SKILL.md) (version
current through its 2026-08-31 §5b entry) and
[`work-item-close.md`](../process/checklists/work-item-close.md). **Proposed by the auditor; not a
close.** `CLAUDE.md` §13 closes a Slice on a clean audit and the lead's merge, and **every
verdict below is a proposal for the lead to adopt, amend or reject** (`CLAUDE.md` §12 — the four
verdicts are the main thread's, never a subagent's).

**Measurement tree: `d8d6e3f`.** The dispatch named `9e50556`; `origin/main` advanced twice while
this audit ran — `6e35b9c` (#645), which touches `scripts/doc-id.py` only, rewriting two
declared-exception *reason strings*; then `d8d6e3f` (#646), **filing F90**, which touches
`docs/findings/FD-01027-check-37-reds-on-95-of-95-post-migration-rulings-unconditional-on-the-flag-day-because-its-section-detector-cannot-see-a-level-heading.md` and `docs/findings/register.md` and nothing else
(`git show --stat --format='' d8d6e3f`).

Because `scripts/doc-id.py` is the subject of §2's abort-point verification, **every execution
below was run at `6e35b9c` and none was inherited from a finding measured at `359936b` or
`9e50556`**. `scripts/` is byte-identical at `6e35b9c` and `d8d6e3f` — `d8d6e3f` adds only two
files under `docs/audit/` — so those executions stand unchanged at the tree this record names.
Register-derived counts and the owed list in §9 are taken at `d8d6e3f`. Nothing here is taken
from a PR body.

**F90 landed mid-audit and is included.** The dispatch said it *"may not exist when you start"*;
it did not, and now does. §8 carries it.

**Verdicts adopted by the lead, 2026-09-02**, with four amendments, all applied below. §8 now
reads as adopted rather than as proposed; where an amendment changed a proposal, the row says so.
The lead's direction on the two record-corrections is quoted at §5: *"You are correcting a record
of state, not making a decision — that is inside an auditor's charter."*

## The one sentence this record exists to make unambiguous

**W37-5c did not achieve "the run no longer aborts."**

Four of Addendum B's abort points are cleared and verified by execution. A **fifth**,
`_discover_vendored_skill_manifests`, still fires on the real corpus and was **never touched by
`544b90c`**. The commit subject claiming otherwise is true of its three named gaps and **false of
the run**. The W37-6 re-ask condition *"F80–F82 shown cleared by execution"* is **satisfied
literally and not sufficiently**.

**And the mechanism, because it is why a fifth guard survived a slice cut to clear abort
points**: item 3's exemption serves those three files in `audit-docs.py` and **not** in
`doc-id.py` — one of two instruments reaching one population.

**No `CLAUDE.md` §14 phase review is raised by this record.** `work-item-close.md` is explicit:
*"A PR or slice close does not raise this question; only a workstream close does."* W37-5c is a
slice. WK-697 itself remains open.

---

## 0. Scope, derived from the decision record before any evidence was sought

Derived from the specification-side artifacts first, in this order, and **not** from the merge
list — `CLAUDE.md` §13 rule 1, whose failure mode is an audit that can only confirm what exists.

**Source 1 — [`2026-09-02-w37-5c-slice-decision.md`](../plans/PL-00957-w37-5c-the-slice-decision-and-gap-2-ruled.md)
§2**, filed `ba31cd1` (#622), stating **six items** against the maintainer's own criterion,
quoted in §1 of that record: *"everything that stops **or blinds** the run and is provable on
broken input outside it."*

**Source 2 — [`2026-09-02-w37-rfc-readme-row-and-stamp-set.md`](../plans/PL-00967-rfc-the-readme-row-the-cell-extent-rule-and-4-step-5-s-stamp-set.md)
§5**, filed `86ebb96` (#627), which **adds a seventh item after the decision record was
written**: *"F84 joins the slice, **discharged exactly per its falsifiable section** — discovery
**plus** a census that names the unmatched unit, proven on broken input. **Not** by the 17 landing
on the right owner."* The same RFC's §4 rules that **§4 step 5 governs the stamp set and gains
six** READMEs, which is a widening of item 2 rather than a new item.

**Source 3 — the same RFC's dated amendment**, filed `919aff4` (#643): the `README.md` at the
**vacated notes root under `.claude`** is **deleted**, §5.3 governs, and §4 step 4 changes. Also
a widening of item 2.

*(That file is named by description rather than by its literal path throughout this record.
`tests/test_notes_move_citations.py::test_no_living_file_cites_the_old_notes_path` forbids a
living tracked file from carrying the literal — an earlier draft of this record carried it three
times and the test caught it, which is the check working on the document auditing it. The
exemption list exists for documents that **specify** the path's deletion, and its own comment
records it growing from two members to four in about an hour; a closure record **citing** the
decision is not a specification of it, so the fix is the phrasing, not a fifth exemption.)*

So the scope is **six items plus F84 = seven**, not six. The count is stated here because the
roadmap, the decision record and the register each carry a different one.

```
W37-5c scope                                    7
  §2 items 1–6 (slice decision, ba31cd1)        6
  F84, added by RFC §5 (86ebb96)                1
  — item 2 widened twice, by RFC §4 and by
    the 919aff4 amendment: not new items
```

### 0a. The dispatch's merge list is incomplete — 12 of 20

The dispatch supplied twelve commits as the slice's build and asked that the list be confirmed
before use. **It is a correct subset and an incomplete one.** The slice was cut at `ba31cd1`
(2026-09-02 15:33, the commit that files the decision record); the build window is therefore
`ba31cd1..6e35b9c`, which holds **20** commits, not 12.

Predicate, runnable: `git log --oneline ba31cd1..6e35b9c | wc -l` → 20 at this tree.

**Eight in-window commits the dispatch's list omits**, each bearing on a scope item or on a
finding the slice filed:

| Commit | PR | Bears on |
|---|---|---|
| `ffdd54c` | #625 | Item 3 — F83's exemption *and* its custody conditions; `24193dd` (listed) only corrects its population |
| `aab6327` | #623 | Items 4/5 — the acceptance-item sweep; `c0739ac` (listed) only writes its dispositions |
| `86ebb96` | #627 | **Item 2's own governing ruling, and the source that adds F84 to the slice**; `919aff4` (listed) only amends this file |
| `5e62b37` | #628 | F85, filed |
| `c35dcf5` | #630 | `python-test` skill, written from *"a live W37-5c case"* (its own body) |
| `6bbfe63` | #631 | **Item 1 — Addendum B, four abort points not three**, the correction §2 below is scored against |
| `e63332c` | #632 | `CLAUDE.md` §13's predicate clause, the maintainer's amendment discharging F85 |
| `7186dca` | #633 | **F84's evidence corrected** — one reference, not zero |

**The dispatch also named `89dd2b1..origin/main` as the range.** That is 87 commits and is the
range for **WK-697 entire** (`89dd2b1` is RFC-937's own filing, #555, 2026-09-02 00:21) — every S1
slice, W37-5, W37-5b and W37-5c together. It is not this slice's range. Stated because a close
audit run against it would have credited W37-5c with W37-5b's eighteen rows.

**This is a note about the dispatch, not a finding against the slice.** Scope here is derived
from §0's three sources; the merge list is used only as evidence for individual items.

---

## 1. The slice decision's own Acceptance Standard — scored item by item

The record's stated Acceptance Standard is *"a slice built against a rule that was inferred
rather than ruled, or a scope narrower than 'everything that stops or blinds the run'."*

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1 | Every scope item in §2 traces to the maintainer's own words or to a numbered finding | **Met, with three rows on the looser limb — named rather than waved through** | Scored row by row against §2's own Evidence column, not summarised. **Rows 1, 4, 6 satisfy it strictly**: row 1's Item column names F80/F81/F82; row 4 cites *"register F77"*; row 6's Evidence reads *"Maintainer's instruction, verbatim"*. **Rows 2, 3 and 5 trace to a dated artifact that is neither an `F-` id nor a quotation** — row 2 to *"Handover §6"*, row 3 to RL-990, row 5 to *"Addendum A row 4"*. Each resolves, so none is the silent-provenance failure the standard was written against; but the standard's literal words are *"quotes the instruction or cites an `F-` id"*, and three rows do neither. Recorded so the gap is visible rather than scored away. |
| 2 | Every `owner:` value in §3 cites the §1.6 cell it is read from | **Met** | All four ruled rows carry a cell citation in §3's third column. The README row is explicitly *"not ruled"* and routed, so it has no value to source. |
| 3 | §4's two challenges are answered **before** the slice starts, not during it | **Not met at the time; resolved 2026-09-02 by #648** | **§4's own two are met**: §4.1 (`WK`) and §4.2 (`contracts/`) are both answered inside the decision record itself, before any build. **§5's exemption-versus-sidecar question was not**, and the gap is sharper than "undecided": the decision record says *"**The maintainer's call, and it is the only thing in §2 item 3 that is not already decided**"*, and that record **has never been amended** — `git log --oneline -- docs/plans/PL-00957-w37-5c-the-slice-decision-and-gap-2-ruled.md` shows one commit, `ba31cd1`. Nineteen minutes later `ffdd54c` filed F83 asserting *"the maintainer's ruling, 2026-09-02"*, and the register row repeats it. **No dated, quotable maintainer line choosing the exemption exists anywhere in the tree** — contrast the same slice decision's own §Authority, which quotes the maintainer literally: *"Decision: not yet. Date: 2026-09-02."* The code carries the gap forward: `scripts/audit-docs.py:2071-2073`'s `_VENDORED_MANIFEST_RULING` cites slice-decision §5 for *"a manifest that won't parse gets its header from a sidecar or an exemption, never an edit"* — a clause establishing that **both** options are edit-free, which does not choose between them. **Resolved 2026-09-02, and it was the lead's to resolve.** The maintainer *had* ruled the exemption over the sidecar; the ruling had simply never landed as a dated artifact, which `CLAUDE.md` §12 forbids — *"every decision lands as a dated artifact … never in chat."* **#648** files it verbatim with its date at `docs/rulings/RL-01001-the-vendored-manifest-exemption-the-maintainer-s-ruling-2026-09-02.md`, corrects the ruling's "63" to 65, and states that the exemption does not by itself let a run proceed. **Scored as met on the strength of that record, not on the assertion that preceded it** — the gap was the artifact's absence, never the decision's. The instrument itself was always sound (§6). See §3 item 3 and §6. |
| 4 | No frozen plan is edited by this decision | **Met on both leaf plans; one flagged edit to the ask** | `git diff --stat ba31cd1..6e35b9c -- docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md docs/plans/PL-00959-w37-6-the-migration-run-leaf-plan-superseding.md` is **empty**. The ask gained +54 lines (`6bbfe63`, Addendum B). **Flagged, not scored a violation**: the standard's violation clause is *"modified to agree with anything decided here"*, and Addendum B does the opposite — it corrects a factual error *against* what the decision record says, appended dated rather than edited in place. Recorded so the literal reading is not silently discarded. |
| 5 | The slice's own arithmetic closes over the **real corpus**, not a fixture | See §4 | Scored there against the mutation proofs. |

---

## 2. The four abort points, verified by execution at `6e35b9c` — and a fifth that still fires

`CLAUDE.md` §13: *"a citation can be correct while the content it vouches for is wrong."* The
dispatch asked for execution rather than a diff read, and the guards were called **with
`migrate()`'s own arguments, taken from its own call block** (`scripts/doc-id.py:4192`, `:4215`,
`:4216`, `:4225`, `:4239` at `6e35b9c`). **`migrate()` itself was never called** — its write is
the irreversible commit.

Both columns are the **real corpus**, not a fixture. The "before" column loads
`git show 544b90c^:scripts/doc-id.py` (tree `e63332c`) and calls each guard with **that tree's own
call-site arguments**, which is why row 3 needed the five-argument form: `extra_record_starts=`
did not exist before the fix, and calling the old function with the new signature raises
`AttributeError` for a reason that has nothing to do with the guard.

| # | Guard (by function name — the durable form, per Addendum B §B.2) | Gap | Before `544b90c` | At `6e35b9c` |
|---|---|---|---|---|
| 1 | `_check_multi_ruling_files_not_silently_unrecognised(root)` | **F81** | **FIRE** — `NotImplementedError: … 3 unit(s) an independent census found are neither a produced record, a derived body line, nor a declared exception` | **PASS** |
| 2 | `_check_plan_reviews_heading_census(root)` | **F80** | **FIRE** — `NotImplementedError: … docs/closures/INDEX.md#plan-reviewsmd carries heading(s) t…` | **PASS** |
| 3 | `_check_headed_split_file_not_silently_unrecognised(root, "docs/closures/INDEX.md#plan-reviewsmd", _REVIEW_HEADING_RE, 3, "plan reviews", extra_record_starts=_proposal_container_starts)` | **F80**, second guard on the same heading | **FIRE** — `NotImplementedError: … (plan reviews) -- 1 unit(s) …` (five-argument form, the call site at `e63332c:3121`) | **PASS** |
| 4 | `_check_requirements_not_silently_unrecognised(root)` | **F82** | **FIRE** — `NotImplementedError: … docs/specs/00-overview.md (requirement ids) -- 4 unit(s) …` | **PASS** |
| 5 | **`_discover_vendored_skill_manifests(root)`** | **F88 limb 1** | **FIRE** — `HeaderError: .claude/skills/create-adaptable-composable/SKILL.md:6` | **FIRE — unchanged** |

**Rows 1–4 are Addendum B's four, and all four are genuinely cleared.** Red-before / green-after,
on the live tree, not a fixture. The correction `6bbfe63` made — *four* abort points, not three —
is itself confirmed: row 3 is a real, independent guard that fires on the same heading as row 2,
one line apart, so clearing the census alone would still have aborted.

**Row 5 is the finding this record exists to make impossible to miss.** It is **not** the "fourth
abort point": Addendum B's fourth is row 3, and it is cleared. Row 5 is a **fifth**, of a
different kind — not a `_check_*` guard but a `_discover_*` function that raises out of discovery
before the stamp loop is entered — and it is **unchanged before and after `544b90c`**, because
`544b90c` never touched it.

**Therefore: `migrate()` still aborts on the real corpus at `6e35b9c`.** The commit subject
*"migrate() no longer aborts"* (`544b90c`) is true of the three gaps it names and **false of the
run**. Nothing in the slice's own records states this, and the W37-6 re-ask condition —
*"F80–F82 shown cleared by execution"* — is satisfied **literally and not sufficiently**: all
three named gaps are cleared, and the run still cannot complete.

**And five is the whole list.** A second, independent replay of **every one of `migrate()`'s
pre-write calls** — not just the five named above — found **no sixth abort point**: row 5 is the
only one of them that fails today. That matters because the four were derived from Addendum B's
table, and a table is a list someone wrote; the replay is the check that the list is complete.

**The fifth aborts *before any write*, so a run stops rather than half-migrating.** Asked
directly, and answered by measurement rather than by reading the comment that claims it:

```
migrate()                          scripts/doc-id.py:4164
  … 24 pre-write calls …
  _discover_vendored_skill_manifests(root)                :4239   ← row 5
  _write_document_drafts(root, drafts, roadmap_drafts)    :4254   ← the first write
```

No write operation appears in `migrate()`'s own body between `:4164` and `:4254`, and **none of
the 24 functions it calls in that span contains one** — searched for `write_text`, `.unlink(`,
`.mkdir(`, `.rename(`, `shutil.`, `.touch(` and `open(…, "w")`. **Positive control on that
predicate**, because a search that has never matched proves nothing: the same pattern against
`_write_document_drafts` (`:2554`), a known writer, returns **3** hits. So the predicate fires
when there is something to find, and finds nothing in the pre-write span.

The code says the same thing about its own intent — the hoist comment at `:4241-4244`: *"the
census must refuse on the **pre-migration** tree, not after `_write_document_drafts` has already
landed files on disk"* — and names task #34, the incident where a call **was** out of place and
`migrate()` crashed mid-write. **That failure mode is fixed; this one is a clean abort.** The
irreversible commit is not at risk from row 5. What is at risk is the run completing at all.

**How the two verifications differ, since agreement between them is only worth what their
independence is worth.** This audit loaded `scripts/doc-id.py` under `uv run python` (3.12.13)
against the live worktree, with the "before" side from `git show 544b90c^:`. The replay used
plain system `python3` (3.13.5) against a read-only `git archive 6e35b9c` snapshot in a separate
directory. Same PASS/FIRE pattern, same error text, same three named manifest files.

**Line numbers, with their tree** (`CLAUDE.md` §13; Addendum B §B.2 records that eight documents
carry `doc-id.py` line numbers naming no tree, and declines to renumber them because the durable
form is the function name — that reasoning is followed here, and the numbers are given only
alongside it):

| # | At `9e50556` | At `6e35b9c` / `d8d6e3f` |
|---|---|---|
| 1 | `:4190` | `:4192` |
| 2 | `:4213` | `:4215` |
| 3 | `:4214-4217` | `:4216-4219` |
| 4 | `:4223` | `:4225` |
| 5 | `:4237` | `:4239` |

**One structural point that changes how row 5 should be fixed.** Rows 1, 3 and 4 funnel through
one shared engine, `_reconcile_census` (`doc-id.py:2671`), whose guard is `if not unaccounted:
return`; row 2 has its own inline equivalent. In every case the guard **re-derives its own
denominator** rather than consuming the discovery call's output — deliberate, per RL-985's
rule that a guard may not take its denominator from the matcher it is checking. **Row 5 has no
guard shape at all.** It is an unguarded `_docid.parse_header(skill_md)` inside
`_discover_vendored_skill_manifests` (`doc-id.py:2482`) that propagates `HeaderError` — which is
F88's own point: it *"presents as a stack trace rather than as a guard naming what it cannot
handle."* Fixing it is therefore not the same shape of work as F80–F82 were.

Reproduce (probe script and the exact call block are quoted above):

```
uv run python -c "…load scripts/doc-id.py by path…; _discover_vendored_skill_manifests(ROOT)"
→ HeaderError: .claude/skills/create-adaptable-composable/SKILL.md:6: indented line —
  nested mappings are not in the closed field set (RFC-937 §1.5): '  author: …'
```

---

## 3. Every scope item, evidence or proposed verdict

Verified at `6e35b9c` by this audit; no PR body is taken on its word (`CLAUDE.md` §13 rule 2).
**Every verdict is a proposal** — §12 reserves the four verdicts to the lead.

| # | Item (slice decision §2) | Proposed verdict | Evidence, re-derived here |
|---|---|---|---|
| 1 | **F80, F81, F82** — the unconditional guards that abort a real `migrate()` run | **Delivered, tested** — but see §2 row 5 | §2 rows 1–4: FIRE→PASS by execution on the real corpus, each with its own tree's call-site arguments. `544b90c` (#629). |
| 2 | **The discovery-and-stamp path for `.claude/skills/`, `.claude/agents/`, `.claude/roles/` and the README population** | **Delivered, tested — partially; the 53-file deferral is §5's finding** | `47eb2ba` (#639). Governing rulings landed first: RFC §4 (`86ebb96`) — step 5 gains six READMEs, *"six reached, one exempt, five stamped"* — and the `919aff4` amendment deleting the vacated notes root's own `README.md`. All six named files confirmed tracked at `6e35b9c` (`git ls-files --error-unmatch`, each). |
| 3 | **The three unparseable vendored manifests** | **Delivered against the check-35 limb; NOT delivered against the migration limb** | `ffdd54c` (#625) + `24193dd` (#635) + `359936b` (#634) put the three in `audit-docs.py`'s exemption register. **That exempts them from checks 30–39. It does not stop `migrate()` aborting on them** — §2 row 5 is those same three files, and it still fires. Two different instruments, one population; the slice built one. |
| 4 | **R84 §4 item 2 built** (the `slice:` acceptance item, vacuous at birth) | **Delivered, tested** | `e2296ec` (#626) — the only build commit in the slice that also updated `docs/findings/register.md`. F77's row now carries the dated *"Built 2026-09-02 in W37-5c"* paragraph naming `_check_emitted_ledger_axes` and its two mutation tests. |
| 5 | **R86 §4 item 3 rebuilt so it can pass on some input** | **Delivered, tested** | `e2296ec` (#626), same row. |
| 6 | **Same discipline as W37-5b** — red-before/green-after; the arithmetic closes over the **real corpus** | **Met on everything this audit executed** | §2's five rows and §4's census proof all run against the live tree or a mutated copy of it. No claim below rests on `tmp_path`. |
| 7 | **F84** — added to the slice by RFC §5 (`86ebb96`), *"discharged exactly per its falsifiable section"* | **Delivered, tested — discharge condition met on both limbs** | §4. |

---

## 4. F84's discharge condition, scored against the clause and not the outcome

The condition is narrow and was written to refuse the easy pass. Quoted verbatim from
`docs/findings/register.md:123`:

> *"Discharged when `migrate()` discovers all 17 as `CR-` drafts **and** a census over that path
> names any file it cannot classify, proven on broken input per RL-985. **Not** discharged by
> the 17 merely receiving the right owner: a correct value reached by accident leaves the next
> corpus change unprotected."*

RFC §5 (`86ebb96`) says the same thing and adds why: *"§1's routing rule means the 17 no longer
take `lead`, so the symptom is gone. **The defect is not.**"* **The dispatch's account of this
clause was correct**, and it is scored against the clause below.

**Limb 1 — discovery.** `_discover_audit_closure_readmes(ROOT)`, called as `migrate()` calls it
(`scripts/doc-id.py:4204`):

```
17 records discovered, kinds {'phase', 'work'}   — this record absent
18 records discovered                             — this record present
```

**That difference is the positive control**, and it is the reason this limb is scored delivered
rather than asserted: the count moves with the corpus, so it is derived from disk and not a
constant. `tests/test_doc_id_migrate.py:3937` asserts `>= 17`, not `== 17`, so the population can
grow without the test going red for the wrong reason — which is why adding this very record does
not break it.

**Limb 2 — the census names what it cannot classify, proven on broken input.**
`_check_audit_closure_readmes_not_silently_unrecognised(root, audit_closure_drafts)`, migrate()'s
own two arguments (`scripts/doc-id.py:4205`):

| Input | Result |
|---|---|
| the real corpus at `6e35b9c` | **PASS** — census returns cleanly, 18 discovered |
| a **copy of the real corpus** with one file added carrying an unrecognised H1 (`# Not a record heading at all`) | **RED** |

```
RESULT: RED -> NotImplementedError
migrate: docs/audit/work/ (work closure records) -- 1 unit(s) an independent census found
are neither a produced record, a derived body line, nor a declared exception (RL-985):
  - docs/audit/work/BROKEN/README.md: BROKEN/README.md
migrate refuses to guess and silently report success instead.
```

**It names the file.** RL-985's property is *"the check must NAME the unmatched unit, never
compare counts"*, and the output does. **Proposed verdict: F84 discharged.**

**The mutation was made on a copy outside the repository tree**, deliberately: `F89` — filed by
this same slice — records that fixtures written into the real `docs/` red another run's gate.
Applying that finding while auditing it is the cheapest available proof it is real.

---

## 5. Two living records reported this slice's own state wrongly — corrected in this PR

**Adopted amendment 1, the lead's, 2026-09-02**: *"F80, F81 and F82 are closed in code and NOT
closed as records. A closure record that calls them closed while the register says otherwise is
the defect this slice spent the day filing. Update those rows in your PR, and the roadmap's
`:382` 'three independent guards' line with them. **You are correcting a record of state, not
making a decision** — that is inside an auditor's charter."*

Both are now corrected here, and the findings below are kept as the record of what was wrong
rather than rewritten into a clean sheet — a corrected document that hides having been wrong is
`RFC-756`'s failure with the evidence removed.

Both are `RFC-756`'s mechanism — a status duplicated into a second place, and the copy going
stale. Both are cheap to fix and neither is fixed here, because a closure record proposes.

### 5a. The register still reads `not started` for four items the slice built

Measured at `d8d6e3f`, `docs/findings/register.md` — re-verified there after `d8d6e3f` appended F90 as row `:131`, which shifts none of these four:

| Row | Line | Decision column opens | The slice's own claim |
|---|---|---|---|
| **F80** | `:121` | `not started` | `544b90c`'s subject: *"migrate() no longer aborts"* |
| **F81** | `:126` | `not started` | same commit |
| **F82** | `:127` | `not started` | same commit |
| **F84** | `:123` | `not started` | `47eb2ba`'s subject: *"F84's 17 closure records"* |

**Cause, verified rather than guessed:** neither commit touched the register at all.

```
git show --stat --format='' 544b90c -- docs/findings/register.md   → empty
git show --stat --format='' 47eb2ba -- docs/findings/register.md   → empty
```

The practice is **inconsistent inside the slice, not absent from it**: `e2296ec` (items 4 and 5)
*did* amend F77's row in the same commit as the build, dated and annotated in place. Three of the
slice's five build commits did not.

**Why it matters here rather than as tidiness.** `scripts/register-owed.py W37-5c`, run against
`9e50556`, returns **5 owed rows** — and F80 and F84 are two of them, described as work not
started. That block is what `work-item-close.md` requires be pasted into this record as generated
evidence (§7). Left alone, this record would carry a generated block asserting that four things it
has just proven working are not started.

### 5b. The roadmap's WK-697 row still says three abort points

`docs/roadmap.md:382` at `d8d6e3f`:

> *"a real `migrate()` run would abort at **three independent guards** against today's tree, in
> pipeline order F81 (`scripts/doc-id.py:2984`…), F80 (`:3000`…), F82 (`:3008`…)"*

Predicate: `awk 'NR==382' docs/roadmap.md | grep -o "abort at \*\*[a-z]* independent guards\*\*"`
→ `abort at **three independent guards**`.

`6bbfe63`'s Addendum B corrects this to **four**, at `:2969`/`:2985`/`:2986`/`:2994` measured at
`ba31cd1` — and its own body names *"the roadmap's WK-697 row"* as one of the four places the
three-guard collapse propagated to. **The ask was corrected; the roadmap was not.** The three
line numbers in the roadmap resolve at no tree the row names (Addendum B §B.2).

The row is also silent on every finding the slice produced: `grep -o 'F[89][0-9]'` over line 382
returns only `F80`, `F81`, `F82`. A W37-6 planner reading the roadmap sees three findings where
there are, at `d8d6e3f`, **ten** bearing on the run (F80–F84, F86–F90).

### 5c. Two counts in scope that reconcile only under an unstated predicate

Not a defect in the arithmetic — a defect in what the arithmetic states, which is precisely what
`CLAUDE.md` §13's predicate clause (added `e63332c`, **inside this slice's window**) now requires.

The slice decision §2 item 2 states *"the true raw count is **33**"* for READMEs. At `d8d6e3f`:

```
git ls-files | grep -cE '(^|/)README\.md$'                                   → 38
git ls-files | grep -E '(^|/)README\.md$' | grep -vc '^tests/fixtures/docs-migration/'  → 33
```

**33 is right, under an exclusion the record never states** — the five READMEs of the
`tests/fixtures/docs-migration/` fixture corpus. The onward arithmetic then closes exactly:
33 − 17 (become `CR-`) − 1 (`docs/findings/README.md`, deleted) − 1 (the vacated notes root's own
`README.md`, deleted per `919aff4`) = **14**, the population the record names. The 17 is independently
confirmed above by execution, not by counting paths.

---

## 6. Item 3, scored on both its limbs — and F83's two conditions

The slice decision routes item 3 through §5's exemption-versus-sidecar question, which it says is
*"the maintainer's call, and it is the only thing in §2 item 3 that is not already decided."*

**The exemption was built.** F83's register row records the ruling — *"**accept, with instrument**
— the maintainer's ruling, 2026-09-02. Exemption, **not** a sidecar"* — with two conditions
*"both enforceable and both owed by W37-5c"*. Both are scored here by execution.

**Condition 1 — every exempt entry cites its reason and the ruling permitting it. MET.**
Measured by symbol at `d8d6e3f`, never pasted (`CLAUDE.md` §13):

```
scripts/audit-docs.py:2088  UNSTAMPABLE_EXEMPTIONS   len = 65
  dataclass fields: ('path', 'reason', 'ruling')
  entries with an empty reason: 0        entries with an empty ruling: 0
  by suffix: json 60 · md 3 · yaml 1 · csv 1
```

The suffix split decomposes exactly against F83's corrected population: 59 `docs/contracts/`
schemas + `docs/process/delivery-process.core.json` = 60 json; the contracts `.yaml`; the
`file-census-5ef559d.csv`; and the **three vendored `SKILL.md` manifests**, all three present by
path. `docs/contracts/README.md` is correctly *absent* — RFC §2 rules it stampable, taking `lead`.

**Condition 2 — the exempt set is itself checked, naming the files rather than comparing totals.
MET, and proven non-trivial in three directions.** `_check_unstampable_register()`
(`scripts/audit-docs.py:2207`) reconciles the register against `nt0019_stamp_set()`
(`git ls-files`-derived, **424** files at `d8d6e3f`) and reports the symmetric difference by name.

Mutations applied to the check's own data, not to the tree — read from the module's own
`failures` list, which is the channel `fail()` writes to; an earlier pass of this probe read
stdout, found zero, and would have reported a live check as inert:

| Input | `failures` | The check's own words |
|---|---|---|
| register as shipped (control) | **0** | — |
| **A** — drop one real entry (65 → 64) | **1** | `check 35: .claude/skills/create-adaptable-composable/SKILL.md: in RFC-937's stamp set and cannot carry a header …` |
| **B** — register a path not in the tree | **1** | `check 35: docs/contracts/does-not-exist.json: in the F83 exemption register but not in RFC-937's stamp set — the file is untracked, deleted or moved, and the entry is stale` |
| **C** — duplicate an entry | **1** | `check 35: docs/contracts/openapi/generated.json: listed twice in the F83 exemption register — a duplicated entry inflates the register against the tree` |

**It names the file in every direction.** *"A check that has never printed a failure has not been
tested"* — this one now has, three ways, and the control stays green.

**And the limb that was not built.** The exemption is an `audit-docs.py` instrument. It exempts
the three manifests from **checks 30–39**. It does **not** stop `migrate()` aborting on them:
§2 row 5 is those same three files and it still fires. Item 3's population is served by one of
the two instruments that reach it.

**A measured aside, because it bears on F87.** `_id_scope_documents()` returns **1** document at
`d8d6e3f`, and **0** of the 65 exempt entries are in it. That is not a defect in condition 2 —
`audit-docs.py:2174-2183` says so in its own words, and routes the reconciliation to
`_check_unstampable_register` *"where those 62 **are** reachable"*. It is the measurement F87
exists for, confirmed independently here.

---

## 7. What the slice did not do that it said it would

### 7a. 53 files deferred, recorded in a squash-commit body and nowhere a planner reads

`47eb2ba`'s body states it plainly, and the reason is good:

> *"53 files deferred, not stamped, and named rather than skipped. All 46
> `.claude/skills/*/SKILL.md` and 7 `.claude/agents/*.md` already carry their own front matter,
> so a header must be merged rather than prepended, which requires declaring those keys in
> `docs/_templates/REFERENCE.md` — W37-6's §7.1 Task 1 under RL-981's licensing instrument.
> Building it in a precondition slice would be building ahead of the phase."*

**That is the right call** (`CLAUDE.md` §0's table — a later phase's capability is not built
early). **Where it is recorded is the finding.** Searched at `d8d6e3f`:

```
git grep -n "deferred_reference_stamps" -- docs .claude        → no hits
git grep -nE "53 (file|deferred)|deferred.{0,30}53" -- docs    → no hit naming this deferral
git grep -ln "already carry their own front matter" -- docs    → no hits
```

It survives in exactly two places: the **squash-commit body**, which cannot be amended
(`git show 47eb2ba`), and **at runtime** on `MigrateResult.deferred_reference_stamps`, printed by
`_cmd_migrate` — visible only to someone who has already run the migration this deferral is a
precondition of.

**The same 53 files are already in a plan, under a different description, and nothing joins
them.** The **frozen** leaf plan
[`2026-09-02-w37-6-migration-run-leaf-plan.md`](../plans/PL-00960-w37-6-the-migration-run-leaf-plan.md)
§ item 13 (`:1194`, evidence at `:748-761`) reaches the identical population from the other end:

> *"Check 30's unknown-field rule reds 53 files the moment they are stamped … all **46**
> `.claude/skills/*/SKILL.md` … all **7** `.claude/agents/*.md` … the migration must **merge** its
> fields into the existing front matter."*

**46 + 7 = 53, the same files and the same root cause.** And the **active superseding plan does
not carry it**: `grep -n "REFERENCE.md\|merge.*front matter\|Task 1"` over
`…-leaf-plan-v2.md` returns nothing. A W37-6 planner working from the active plan sees neither
the deferral nor its cause.

**Proposed disposition: carry forward, owner W37-6**, and record the join in a document rather
than leaving it to be re-derived from a commit body — one line naming the 53, the frozen plan's
item 13, and `47eb2ba`.

**Which document should hold it — a proposal, asked for and given as one.** Read against the
standard, three candidates and one answer:

- **The frozen leaf plan is out** — `CLAUDE.md` §2: *"a filed plan under `docs/plans/` is frozen
  at its date."* Its item 13 is correct at its own pin and is not edited.
- **The roadmap is the wrong altitude.** Its WK-697 row states scope and status, and `RFC-756` is
  the standing argument against putting a second copy of a detail there.
- **The register is where it belongs** — `RFC-778`, quoted by F83's own row: *"a deferred item
  with no owner is not deferred, it is lost."* That is exactly this item's shape: work
  deliberately not done, with a named reason, needing custody until someone does it. It also
  makes the deferral reachable by the one tool that generates owed lists —
  `register-owed.py W37-6` — which is how a W37-6 planner would find it without knowing to look.
- **And the active leaf plan should carry a pointer, not a copy** — one line under W37-6's own
  task list citing the new register row, so the plan a planner actually reads names the
  precondition without duplicating the figure that would then go stale.

**So: a register row, plus a citation from the active plan — and both now exist.** Filed as
**F92** on the lead's direction (register row, [`FD-01029-53-files-are-deferred-out-of-4-step-5-s-reference-stamp-set-and-the-deferral-lives-only-in-a-squash-commit-body.md`](../findings/FD-01029-53-files-are-deferred-out-of-4-step-5-s-reference-stamp-set-and-the-deferral-lives-only-in-a-squash-commit-body.md), and a
dated append under the active leaf plan's own `Corrections after filing` section — 37 insertions,
**zero** deletions, which is what keeps it inside `docs/plans/README.md`'s rule rather than an
edit to a filed plan). The precedent is already in this tree and is F87's: it was filed as a finding *because*, in its own words, the fact *"lived only
in a passing test … invisible to whoever plans W37-6, who is the person who needs it."* The 53
live in a commit body and a runtime print, which is the same invisibility by a different route.
**The lead's call, not this record's** — this states the reading and its authority.

### 7b. Item 3's second limb, restated as an owed item

Named again here because §6 buries it in a passing check: the three unparseable vendored
manifests are exempt from checks 30–39 and **still abort `migrate()`**. Proposed disposition:
**carry forward as F88 limb 1, owner W37-6, and treated as a run-blocking precondition rather
than a documentation gap** — it is the same class as F80/F81/F82, which were run-blocking.

---

## 8. Findings — every one, with its adopted decision and status

`work-item-close.md`'s table. **Adopted by the lead 2026-09-02**, with four amendments; where an
amendment changed what this record proposed, the row says which. `CLAUDE.md` §12 reserves the
four verdicts to the lead, and this table now records their exercise rather than a proposal.

**Four W37-6 preconditions — F87, F88, F90 and F92 — were found by this slice, and none of them
existed on any prior list.** Not in the map plan, not in either leaf plan, not in the W37-6
obligations list, not in the go-ahead ask. Each was produced by building the slice's own six
items and looking at what the instruments then reported. That is the sentence a W37-6 planner
needs from this record, and it is stated here rather than left to be inferred from four rows.
**F92 is the one of the four the slice itself created** — the other three were pre-existing gaps
its new instruments revealed.

| Finding id | Concerns | Adopted decision | Status |
|---|---|---|---|
| **F80** | `plan-reviews.md`'s "Pending proposals" container had no discovery; aborted every run | **fix before close — done.** `544b90c`, verified by execution (§2 rows 2 and 3, both guards) | **closed** — and closed *as a record* too: register `:121` annotated `DISCHARGED 2026-09-02` in this PR, per amendment 1 |
| **F81** | The real RL-902/A2/A3 file, ruled `RL-`, not discoverable; aborted every run | **fix before close — done.** `544b90c`, §2 row 1 | **closed** — register `:126` annotated in this PR |
| **F82** | Four module-less `DEP-` ids in `00-overview.md`; aborted every run | **fix before close — done.** `544b90c`, §2 row 4 | **closed** — register `:127` annotated in this PR |
| **F83** | 65 in-scope files cannot carry a header; custody by exemption | **accept, with instrument — both conditions met.** §6: reason and ruling on all 65; reconciliation proven red three ways. **Its authority now exists**: the maintainer's exemption ruling is filed dated by the lead in **#648** (`docs/rulings/RL-01001-the-vendored-manifest-exemption-the-maintainer-s-ruling-2026-09-02.md`), which also records that its "63" is 65 and that the exemption does not by itself let a run proceed | **closed** |
| **F84** | 17 closure records invisible to the migration, and nothing reported it | **fix before close — done, scored against the clause not the outcome.** §4: discovery 17→18 under a positive control; census reds **by name** on a mutated copy of the real corpus. **Not** discharged by the 17 receiving the right owner | **closed** — register `:123` annotated in this PR |
| **F77** | RL-986 §4's `slice:` acceptance item, vacuous at birth | **fix before close — done.** `e2296ec`, whose own commit updated the register row. Its text says the row *"is discharged when its owner accepts those two instruments"*; that acceptance is this close's | **closed** |
| **F85** | Four counts stated as measurements never measured | **accept — already discharged** by `e63332c`, which landed `CLAUDE.md` §13's predicate clause | **closed** |
| **F86** | RL-909's decay rule: no faithful check, wrong population, blind backstop | **Amendment 2, the lead's — carry forward, and the disposition is explicit decay.** No individual owner is assigned; absent a slice taking it, F86 decays to the next `CLAUDE.md` §14 plan review, which must give it a disposition rather than list it. Written into register `:128` in this PR **with the `§14` literal**, so `register-owed.py review` surfaces it. Its own row named *this close* as the owner-assigning event, and **a finding about unowned rows failing to name their own decay event must not be one** | **closed-with-findings** |
| **F87** | Widening `_ID_SCOPE_ROOTS` reaches no non-markdown file; 62 of 65 stay invisible to checks 30–39 | **Amendment 3 — carry forward as a W37-6 precondition, no individual owner, decaying to the next §14 review.** Re-measured here at `d8d6e3f`: `_id_scope_documents()` → **1** document, **0** of the 65 in scope. **Its row named no decay event at all**; that clause is added in this PR | **closed-with-findings — W37-6 precondition** |
| **F88** | Two §5.2-routed populations discovery does not reach; limb 1 **aborts every real run** | **Amendment 3 — carry forward as a W37-6 precondition, no individual owner, decaying the same way.** §2 row 5 **reclassifies limb 1 from *blinds* to *stops***: it is a fifth abort point, in the class F80–F82 were treated as run-blocking in, and it is pre-write, so the failure is a clean abort rather than a partial migration. Written into register `:129` in this PR. Limb 3 discharged in its filing commit | **closed-with-findings — W37-6 precondition, run-blocking** |
| **F89** *(amend, do not renumber)* | Five test fixtures written into the real `docs/plans/` — **plus a second instance found by this audit: an untracked closure README reds the suite** (§10b) | **Amendment 4 — closed as filed, with the second instance folded in as an amendment rather than a renumber.** F89's falsifiable clause already reopens on exactly this, and two matchers over one population disagreeing is RL-985's class. Adopted 2026-09-02 | **closed** |
| **F90** | Check 37 reds 95 of 95 post-migration rulings; its detector cannot see a `###` heading | **Amendment 3 — carry forward as a W37-6 precondition, no individual owner, decaying the same way.** Filed `d8d6e3f` (#646) after this audit began; its row already names the next go-ahead request as the event and lists four options, **one of which must be dispositioned before that ask is made** | **closed-with-findings — W37-6 precondition** |
| **F91** *(new, filed in this PR)* | The RFC-895 runtime-state writer has not run since 02:03Z, and `written_at` cannot say so | **carry forward, unowned** — the lead's direction: *"File it as a register row, no work item, carry forward. It is not this slice's defect and the closure record should say so."* **It is not this slice's defect.** Filed as register `:132` plus [`FD-01028-the-rfc-895-runtime-state-writer-has-not-run-since-02-03z-and-written-at-cannot-say-so.md`](../findings/FD-01028-the-rfc-895-runtime-state-writer-has-not-run-since-02-03z-and-written-at-cannot-say-so.md), split from the start because its essay is over threshold | **closed-with-findings** |
| **F92** *(new, filed in this PR)* | 53 files deferred out of §4 step 5's Reference stamp set, recorded only in a squash-commit body | **carry forward, with an owner — W37-6**, whose §7.1 Task 1 discharges it. Filed on the lead's direction after this record had adopted the disposition but declined to mint the id: *"Creating an `F-` id you have not directed is exactly how F88 limb 3 happened."* **`F92` verified free before use** — absent from `origin/main` and from this branch, `F91` the highest allocated. Register row plus [`FD-01029-53-files-are-deferred-out-of-4-step-5-s-reference-stamp-set-and-the-deferral-lives-only-in-a-squash-commit-body.md`](../findings/FD-01029-53-files-are-deferred-out-of-4-step-5-s-reference-stamp-set-and-the-deferral-lives-only-in-a-squash-commit-body.md), and a dated pointer appended to the **active** leaf plan | **closed-with-findings — W37-6 precondition** |
| *(was: no register row — **now fixed**)* | `docs/roadmap.md`:382 said three abort points, with line numbers resolving at no tree | **fix before close — done in this PR**, per amendment 1. Corrected to four, named by **function** rather than by line (Addendum B §B.2's own reasoning), with a dated clause recording that all four are now cleared and a fifth still fires | **closed** |
| *(was: no register row — **now fixed**)* | The register read `not started` for F80, F81, F82, F84 | **fix before close — done in this PR**, per amendment 1. Four rows annotated in place, each quoting the `not started` it supersedes, per the register's own annotated-in-place rule | **closed** |

**Every id in §9's generated block appears above with a resolution** — F77, F80, F83, F84, F86.
The table adds F81, F82, F85, F87, F88, F89, F90 and F91 (register rows the block does not
select, because their Work-item and Decision cells name W37-6 or no work item rather than
W37-5c), plus **F92**, which was left unallocated on purpose until the lead directed the id and is now
filed. **No finding in this record lacks a register row.**

**§9's block was generated before these amendments and is not regenerated.** It is evidence of
the register's state at the moment the owed list was taken, which is what a generated block is
for; four of its five rows are annotated `DISCHARGED` by this same PR, and the table above is
where that is recorded. Regenerating it would erase the before-state the close is being audited
against.

---

## 9. Owed list — generated, not recalled

Per `work-item-close.md` and RL-912. Verbatim output, command and revision named; **not** this
record's own findings table, which is §8 and is hand-written.

**One disclosed deviation from verbatim, of exactly one link.** The generated text links the
anchor text `FD-01020-63-in-scope-files-cannot-carry-a-header-and-their-custody-is-an-exemption-rather-than-a-sidecar.md` to the target `FD-01020-63-in-scope-files-cannot-carry-a-header-and-their-custody-is-an-exemption-rather-than-a-sidecar.md` — a path relative to `docs/audit/`,
where this file lives at `docs/audit/work/W37-5c/`. (The link syntax is described rather than
reproduced here: writing it out a second time re-creates the broken link this paragraph is
about, which is how the first attempt at this disclosure failed.) Pasted unchanged it is a broken
link, and `audit-docs.py` said so:
`broken link in closures/CR-01005-work-item-record-w37-5c-the-second-precondition-slice.md: FD-01020-63-in-scope-files-cannot-carry-a-header-and-their-custody-is-an-exemption-rather-than-a-sidecar.md`. The target is rewritten to
`../../FD-01020-63-in-scope-files-cannot-carry-a-header-and-their-custody-is-an-exemption-rather-than-a-sidecar.md` — same file, same anchor text, nothing else in the block altered.
Recorded here rather than done silently, because *"verbatim"* is the rule this is bending and a
reader comparing the block to a fresh `register-owed.py` run should know which byte differs.

```
Generated by `python3 scripts/register-owed.py W37-5c` against `d8d6e3f (`audit/w37-5c-closure`)`.
Mode: work item 'W37-5c'. 5 owed row(s), 0 matched but excluded as opening with a resolution marker (listed below — verify none carries a residual item; the register's own header names five rows where a status marker and further carried content share one cell).

- **RL-986 §4's second acceptance item — no emitted `LG-` carries a `slice:` resolving to no roadmap row, reddening on a broken fixture — is vacuously true and untestable as stated (F77)** (work item: 'W37-6', phase: '2') — carry forward, unowned — the interpretation question is **Ruled 2026-09-02** (RL-1000, `docs/rulings/RL-01000-the-property-stands-the-instrument-is-amended-because-a-broken-input-need-not-be-a-document.md`, PR #614), so what remains is implementation with no owner named yet; next event: the lead names an owner when adopting the W37-5b closure record. Superseding the deferral below on the interpretation only: vacuously true does not satisfy RL-986 §4's second item (`CLAUDE.md` §13 — "a check that has never printed a failure has not been tested"), and the remedy is not a reading that treats it as satisfied by construction but a **substitution**: a check that counts the `slice:` values on emitted `LG-` records, requires every one to resolve to an `SL-` row, and **prints the count it checked** (a passing zero must say which zero it counted, per `RFC-789`), reddening on a **one-line mutation of `_stamp_header`** — removing `slice` from the skip tuple at `:946` so the template's `slice: SL-NNNNN` placeholder is emitted — rather than a fixture document, since a fixture cannot carry a key the writer itself refuses to emit. RL-986 is not edited; its other three items stand, and its third (`work:` resolves) is confirmed **live, not vacuous** — verified directly at `09b7e9b`: `_discover_roadmap(ROOT)`'s one `old_token == "WK-661"` draft (`WK`, phase `P1b`) matches all ten real `_discover_closure_records` `LG-` drafts' `work_token`, so today's real corpus resolves cleanly — but no *guard* yet exists that would red if a future `LG-` record resolved to neither `work:` nor `slice:`: `tests/test_doc_id_migrate.py::test_write_document_drafts_resolves_a_ledgers_work_and_phase_from_the_roadmap` asserts the opposite (an unresolved `work_token` silently omits `work:` rather than raising), and both that test's and `_write_document_drafts`'s own docstrings are now stale, still describing "the real corpus's `roadmap_drafts` is empty" — true before `4cbfa62` (row 2/3), not after. **Not yet built**: as of `09b7e9b` neither the substituted count-and-print check (RL-1000 obligation 2) nor a guard for item 3's "neither axis" violation exists in `scripts/doc-id.py` or `tests/test_doc_id_migrate.py` — both are narrow, unassigned implementation gaps this row now tracks rather than the interpretation question RL-1000 already closed. Original deferral text kept below per this file's "annotated in place" rule: deferred with an owner — the decision-maker (per `614c92c`'s own routing), to rule whether the item is unreachable-by-construction (satisfied vacuously) or instead obliges row 24's general check-33 cross-reference validation to run before W37-6 closes. Falsifiable: discharged by that ruling, or by a corrected reading showing a code path can write `slice:` onto an `LG-` record after all. **Built 2026-09-02 in W37-5c, superseding the `Not yet built` sentence above:** RL-1000's substituted instrument is `_check_emitted_ledger_axes` in `scripts/doc-id.py`, called by `migrate()` after the roadmap restructure and reported by `_cmd_migrate` as three counts printed unconditionally, the zeros included (`RFC-789`). Non-vacuity proven with RL-1000's own named broken input rather than a fixture: `tests/test_doc_id_migrate.py::test_ledger_slice_check_reds_on_ruling_94s_stamp_header_mutation` loads `scripts/doc-id.py` with `slice` removed from `_stamp_header`'s skip tuple and measures 10 `slice:` values and 10 violations across the ten real `docs/closures/INDEX.md#closure-recordsmd` WK-661 records, against 0 and 0 unmutated over the identical ten. RL-986 §4 item 3's `neither axis` violation is built in the same pass, per RL-1000 §4, and exercised by `::test_ruling_84_item_3_reds_on_an_emitted_ledger_with_neither_axis`, whose broken input is again the real corpus — the roadmap's WK-661 draft withheld, which is the only way `_write_document_drafts` emits a ledger with neither axis. One interpretation flagged rather than made silently: a `slice:` violation raises out of `migrate()` while a `work:` violation is carried as a `MigrateResult` warning, because item 3 scopes itself to `once W37-6 has created the WK- rows` — a state no run reaches while F80-F82 abort it — so an aborting work-axis guard would add an unmeasured stop to an irreversible migration. This row is discharged when its owner accepts those two instruments; it reopens on a `slice:` or `work:` value the check cannot see.
- **`migrate()` cannot complete on the real corpus today: `docs/closures/INDEX.md#plan-reviewsmd`'s "Pending proposals" container has no discovery code, and the unconditional plan-reviews census is what catches it (F80)** (work item: 'W37-6', phase: '2') — not started — discovery code turning the "Pending proposals" heading into an `RFC-` draft, symmetric to what `d7c9b08`/`614c92c` already built for closure-records' `LG-` drafts. Owner not named here: candidates are the W37-6 executor (RL-980's own framing) or a narrow W37-5b/W37-5c follow-up (the same reasoning the slice decision used for row 9), and the choice is the lead's. Falsifiable: discharged when the discovery code lands and the census returns cleanly against the real tree, or by a corrected reading showing some other call path resolves this heading first.
- **63 in-scope files cannot carry a header at all, and their custody is an exemption rather than a sidecar (F83)** (work item: 'W37-5c', phase: '2') — **accept, with instrument** — the maintainer's ruling, 2026-09-02. Exemption, **not** a sidecar; the sidecar is recorded as the option not taken so the design is recoverable if the 63 ever need machine-readable ownership. Two conditions, both enforceable and both owed by W37-5c: **(1)** every exempt entry cites its reason and the ruling permitting it — a list whose entries carry no justification is indistinguishable from a list of things nobody got round to; **(2)** the exempt set is itself checked, the count of unstamped in-scope files equalling the exempt list, **so the list cannot grow silently**. Condition 2 is RL-985's property applied to an exemption rather than a census and inherits its reasoning: the check **names** the unstamped-and-not-exempt files, never compares two totals, because two errors that cancel pass a total-only check. Filed as a finding rather than left as an allowlist so the 63 have custody under `RFC-778` — a deferred item with no owner is not deferred, it is lost. **Corrected 2026-09-02, after the ruling: the population is 65, not 63.** This row's claim and evidence cells both state 63 and are superseded here rather than edited, per this file's annotated-in-place rule. Two tracked files in the ruled stamp set were never counted, both meeting the finding's own criterion that a format with no comment syntax cannot carry front matter: `docs/process/delivery-process.core.json` (CLAUDE.md §15's machine-readable extract, where front matter breaks `json.load` for the reason the 59 contracts schemas do) and `docs/research/file-census-5ef559d.csv`. So 60 plus 2 non-`.md` files, plus the 3 unparseable vendored manifests, is 65; measured at `7186dca` and stable across `e63332c` and `544b90c`, since #629 touched no file under `docs/`. **The counting predicate is stated once, in F83's own dated correction section, and deliberately not restated here** — it contains a shell pipe that would split this row, and `CLAUDE.md` §13 refuses a pasted constant for the same reason `RFC-756` refuses a duplicated status line: the copy is what goes stale. **The defect was the corpus, not the arithmetic** — the lead measured the two populations already in mind and reported their union as the unstampable files, never enumerating the stamp set the rule ranges over, which is the class `F85` describes, committed by `F85`'s own author four hours after §13 was amended to require the predicate a count was counted with. The two new entries ship flagged in their own `ruling` cell as found by this check and awaiting ratification, reversible by deleting two tuples. **Condition 2 found them**, on its first day against the real corpus, which is the property it was imposed for. Full correction with the predicate: [`FD-01020-63-in-scope-files-cannot-carry-a-header-and-their-custody-is-an-exemption-rather-than-a-sidecar.md`](../findings/FD-01020-63-in-scope-files-cannot-carry-a-header-and-their-custody-is-an-exemption-rather-than-a-sidecar.md), section *Dated correction — 2026-09-02*.
- **17 closure records have no discovery code and no guard — the migration cannot see them, and nothing reports that (F84)** (work item: 'W37-5c', phase: '2') — **not started** — on the *blinds* limb of W37-5c's criterion. Cost today is concrete: under the README row's second clause these 17 take `owner: lead` where their true family is `auditor`, and **nothing downstream catches it because both are valid role stems** — a check on the value's form passes on the wrong value, which is the hole RL-979 named, in a new place. Live rather than theoretical *because* of this finding: if anything converted them to `CR-` first the README clause would never reach them, and nothing does. Discharged when `migrate()` discovers all 17 as `CR-` drafts **and** a census over that path names any file it cannot classify, proven on broken input per RL-985. **Not** discharged by the 17 merely receiving the right owner: a correct value reached by accident leaves the next corpus change unprotected.
- **RL-909's decay rule has no faithful check, the wrong population, and a backstop that cannot express the shape it exists for (F86)** (work item: '—', phase: '2') — **carry forward, unowned** — and the event is named here rather than left to the proxy this row reports. **This row is therefore the 20th member of the population it reports on, and the first to name a genuine owner-assignment event.** **The event that next assigns an owner is W37-5c's close, and absent that this row decays to the next `CLAUDE.md` §14 plan review**, which must give it a disposition rather than list it. That sentence is written deliberately: a row filed against the decay rule that itself named no event would be the defect it reports, and it carries the §14 literal so `register-owed.py` can actually surface it — which it cannot do for F45, F47 or F54. **Not discharged by the three live rows receiving owners**: a correct value reached by hand leaves the next row unprotected, the same reasoning F84 was ruled on. The remedy is bounded and partial by design — a narrower predicate cannot fully separate *this event resolves who owns it* from *this event resolves the finding*, which is reading comprehension rather than lexis, but the current check reds on nothing and a narrower one reds on three, so the improvement is from zero to three rather than from three to perfect. Falsifiable: discharged when a predicate reds on a row naming no event (proven on the three live rows), the population excludes resolved rows (proven on F50 or F51), and the review-agenda predicate can surface a row naming no event (proven on F45).
```

---

## 10. "Provable on broken input outside the migration" — the slice's own criterion, scored

Acceptance-standard item 5's violation is *"a census or count in W37-5c evidenced only against
`tmp_path`."* Scored per build commit, by opening the tests each added and classifying what they
run against.

| Commit | Corpus the tests use | Red-before proof | Verdict |
|---|---|---|---|
| `544b90c` | **Mixed** — 6 real-corpus-in-place (`ROOT`, read-only) + ~16 pure-fixture (`FIXTURE_CORPUS` copied to `tmp_path`, mutated in the copy) | `pytest.raises(NotImplementedError, match=…)` on unruled/unnumbered headings | **Met** — the guards themselves are exercised against `ROOT`; §2 re-proves all four independently |
| `e2296ec` | **Real corpus, producer-source mutated** — reads `_discover_closure_records(ROOT)` / `_discover_roadmap(ROOT)`, then mutates `scripts/doc-id.py`'s **source text**, never the corpus | 10 violations mutated vs 0 unmutated over the same ten real WK-661 ledgers | **Met, and the strongest form in the slice** — the broken input is RL-1000's own named mutation |
| `359936b` | **Real-corpus-in-place** — the check walks the real `REPO` via `git ls-files`; `UNSTAMPABLE_EXEMPTIONS` is monkeypatched in memory. One `tmp_path` test, for a narrow helper probe | Yes | **Met** — §6 re-proves it three ways |
| `47eb2ba` | **Real-corpus-copy-then-mutated**, by explicit design — `_real_closure_dirs_copy`/`_real_claude_copy`, with the code comment *"per W37-5c's own Acceptance Standard item 5… `ROOT` is never written to"* | Four mutations red **by name** | **Met** — §4 re-proves it |
| `dc1666f` | **Synthetic, deliberately** — the module docstring says *"never against this repository's own history, which must not be mutated to manufacture a bad commit"* | Yes, on a purpose-built two-commit repo | **The one weak point — see below** |

**Independently re-proved here, not taken from the tests**: §2 (five guards, both trees), §4 (F84
discovery + census, mutated copy), §6 (F83 register, three mutation directions). Every one ran
against the live tree or a copy of it; none against `tmp_path` fixture data.

### 10a. Where the criterion is weakest, named rather than smoothed

**Corrected on challenge, 2026-09-02, before this record was adopted. An earlier draft of this
section said `dc1666f`'s freeze test "pins a hand-verified literal, not a measurement" and called
it the criterion's weak point. That was wrong, and the challenge that corrected it is the lead's:
a freeze test that derived its expected value from the symbol it guards would be vacuous, so
retyping the literal is the mechanism working, not failing.** The superseded sentence is named
rather than deleted. What follows is the finding as it should have been stated.

`tests/test_ruling_acceptance_census.py::test_named_exceptions_and_prose_only_rulings_are_frozen_at_the_flag_day`
asserts `frozenset({"44"}) == census._NAMED_EXCEPTIONS` and the same for
`_PROSE_ONLY_RULINGS`'s ten members. **Retyped on purpose**: the point of a freeze is to make
growth a deliberate two-place edit, and its docstring says so — *"growth after the flag-day is a
violation per the maintainer's ruling, not a maintenance action."* **No finding here.**

**The real gap is one level up, in the census rather than the test: the two sets are hand-built
and nothing re-derives their membership from disk.** The script states it itself, which is why
this is a disclosed limit rather than a defect: *"a **hand-verified list, not a derived one**,
and it is the one place this module's own promise … does not hold: a future ruling using this
same loose, marker-free style would land silently in `none` below, not in a bucket whose count
visibly moved."* The freeze catches a set that **changes**; nothing catches a corpus that grows
**into** the shape the set describes. The trade-off that produced it — not mutating real git
history to manufacture a bad commit — is sound.

**One residual, small and stated rather than pressed.** The freeze's growth-catching is proven
*"by hand (see module docstring)"*, not by an automated positive control. That is a real proof
and a weaker form of one than `CLAUDE.md` §13's *"proven on deliberately broken input"* asks for,
and it is the only place in the slice where the proof is an author's account rather than a
runnable artifact.

**And the census is not wired to anything.** `git grep -n "ruling-acceptance-item-census" --
'*.yml' '*.yaml' scripts/audit-docs.py` returns nothing at `d8d6e3f`. Its
*"0 post-flag-day violations"* holds only while someone runs it by hand. **Proposed
disposition: carry forward with an owner — W37-6** (or the next slice that touches the gate),
recorded here because a flag-day convention enforced by nobody decays to a convention.

### 10b. An untracked closure record reds the suite — found by this audit, on itself

While this record was still untracked, `tests/test_doc_id_migrate.py` ran **1 failed, 152
passed**: `test_readme_population_decomposes_exactly_as_the_rfc_ruled` reported
`Extra items in the right set: 'docs/closures/CR-01005-work-item-record-w37-5c-the-second-precondition-slice.md'`.

**Cause, verified:** `_discover_audit_closure_readmes` (`scripts/doc-id.py:1597`) walks the
**filesystem**; the README census in `_discover_reference_stamp_targets`
(`scripts/doc-id.py:3501`) walks **`git ls-files`**, deliberately — *"the tree that sentence
means is the tracked one … a walk would sweep in a `.venv/` … and quietly inflate every count."*
An **untracked** closure README is therefore visible to one and invisible to the other, and the
partition they are asserted to agree on does not close.

**Not a defect in any audited commit** — with this record staged, `tests/test_doc_id_migrate.py`
is **153 passed**. It is a real, narrow assumption worth naming: *the identity these tests assert
holds only when the working tree matches `HEAD`.* It is the same class as **F89** (working-tree
state leaking into a test's result), in a second place, and it is why §4's mutation was made on a
copy outside the tree.

**Proposed disposition: amend F89 with this second instance rather than file a new id** — F89's
falsifiable clause already says *"Re-opened if a new test adds a fixture inside a scanned root"*,
and this is the same mechanism reached from the other side.

---

## 11. Gate, run at `d8d6e3f` with every change of this PR in the tree

**The PR is no longer one Markdown file.** Adopting the verdicts (§8) made it four, and filing
F92 made it **six**: this record, `docs/findings/register.md` (seven rows annotated, **two** added),
`docs/roadmap.md` (the WK-697 row's abort-point sentence), `docs/findings/FD-01028-the-rfc-895-runtime-state-writer-has-not-run-since-02-03z-and-written-at-cannot-say-so.md`,
`docs/findings/FD-01029-53-files-are-deferred-out-of-4-step-5-s-reference-stamp-set-and-the-deferral-lives-only-in-a-squash-commit-body.md`, and a **37-line, zero-deletion append** to the active leaf plan
`docs/plans/PL-00959-w37-6-the-migration-run-leaf-plan-superseding.md`. **The test selection was widened to
match, and widening it is what caught a real failure** — see below.

| Command | Result |
|---|---|
| `python3 scripts/audit-docs.py` | **PASS** — *"All checks passed."* |
| `uv run python scripts/register-lint.py` | **PASS** — `0 violations`; residue `61 of 89`, unchanged in count by seven amendments and two new rows (F91 at 985 chars, F92 at 971, both split from the start) |
| `uv run pytest -q <13 files>` — every `tests/test_*.py` naming `roadmap.md` or `register.md`, plus `test_ruling_acceptance_census.py` | **515 passed** |
| `uv run python scripts/register-owed.py W37-5c` | **refuses, correctly** — *"has an uncommitted diff … RL-912 forbids citing a dirty worktree"*. §9's block was generated at `d8d6e3f` **before** these register edits, which is the state it is evidence of |
| Frontend half | **not run** — no frontend file touched; left to CI |
| `uv run mypy`, `ruff`, `lint-imports` | **not run** — no Python changed; left to CI |

**Full `uv run pytest -q` was not run — it OOMs this machine** (the dispatch's instruction).

### 11a. Two failures this gate found, both in this record

**Neither was in the slice. Both were in the document auditing it**, which is the more useful
kind of gate result and is recorded rather than quietly fixed.

**One — the broken relative link, twice.** `audit-docs.py` reported
`broken link in closures/CR-01005-work-item-record-w37-5c-the-second-precondition-slice.md: FD-01020-63-in-scope-files-cannot-carry-a-header-and-their-custody-is-an-exemption-rather-than-a-sidecar.md` — §9's pasted owed block carries a
path relative to `docs/audit/`, and this file lives one directory deeper. Fixed, disclosed in §9
— **and the disclosure re-created it**, because writing the link syntax out to describe it is
writing the link. The second fix describes the syntax instead of reproducing it.

**Two — the old notes path, caught only by widening the selection.**
`tests/test_notes_move_citations.py::test_no_living_file_cites_the_old_notes_path` failed naming
this record: it carried the literal vacated-notes path three times. **The narrower four-file
selection used before the verdicts were adopted does not reach that test**, so this would have
merged unnoticed had the PR stayed one file.

**The fix was the phrasing, not an exemption.** That test's exempt set is for documents that
**specify** the path's deletion; its own comment records the list growing *"two members to four
in about one hour"*, and a closure record **citing** the decision is not a specification of it.
The file is now named by description throughout. The test models the same move itself — it
builds the path by concatenation so that stating the rule does not violate it.

**Retry counters (RFC-895 artifact B):** `none recorded`, and the file is not being written —
see below; now filed as **F91**.

**And the state file is not merely stale — it has not been written at all since 02:03Z.**
Corrected on the lead's challenge, which asked for the stronger claim to be evidenced or
dropped. `written_at` alone cannot separate *"re-derived and unchanged"* from *"never touched"*
— that is `RFC-789`'s shape, a field that reads the same either way. **`mtime` separates them**,
and is the instrument `RFC-895` exists to be checked by:

```
/home/puzhenhao1989/gi-pricing-plan.local/handover/runtime-state.json
  mtime                      2026-09-02 02:03:05Z
  position.written_at        2026-09-02T02:02:13Z
  in_flight.written_at       2026-09-01T20:06:20Z
  read at                    2026-09-02T18:24:07Z
```

**16 h 21 min with no write**, across W37-5, W37-5b and W37-5c. `position.slice` still reads
`W37-4`. So the claim this record makes is *the writer has not run since 02:03Z* — evidenced by
`mtime`, not inferred from the field.

**What this record does not claim**, because `mtime` cannot distinguish them: whether the
watcher is alive and not writing, dead, or never re-armed this session. Naming the three is the
honest stopping point — `RFC-895`'s own reasoning is that an anomaly-only monitor's silence is
indistinguishable from its death, and reading the log or a `pgrep` would answer a different
question than the one asked. **Reported as an observation about the watcher, not a finding
against this slice**, and offered to the lead as a candidate register row if they read it as one.


---

## 12. What this record does not do

- **It does not close W37-5c.** `CLAUDE.md` §13: a Slice closes on a clean audit and **the
  lead's merge**. This is the audit; the merge is the lead's.
- **It does not write any verdict as decided.** §12 reserves the four verdicts to the lead;
  every Decision cell in §8 is a proposal.
- **It does not edit any filed plan, and it does append to one.** The **frozen** leaf plan is
  untouched — `git diff --stat origin/main...HEAD -- docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md`
  is empty. The **active** superseding plan gains **37 insertions and zero deletions** under its
  own `Corrections after filing` section: F92's pointer. **That is the distinction
  `docs/plans/README.md` draws** — *"Do not edit a filed plan to agree with today's
  repository"* forbids rewriting a claim, not a dated append that changes none. Verified rather
  than assumed: `b3471fb` (#621) set the precedent on **this same file**, 54 insertions and zero
  deletions, and this record's earlier version said flatly that it edits no plan, which stopped
  being true when F92 was filed.
- **It *does* now edit `docs/findings/register.md` and `docs/roadmap.md`** — reversing what this
  bullet said in the version of this record filed at `74ca19c`, which read *"It does not edit
  `docs/roadmap.md`, `docs/findings/register.md`, or any filed plan."* That was right while the
  verdicts were proposals and wrong once the lead adopted them and directed the correction (§5).
  **The distinction the lead drew is the one that makes it legitimate: correcting a record of
  state is not making a decision.** The seven annotations say what they supersede, per the
  register's own annotated-in-place rule; none rewrites a Decision's opening disposition.
- **It does not migrate the seven over-threshold rows it amended.** RL-911 makes migration
  opportunistic at a row's next substantive amendment, and seven at once for one reason is the
  **bulk sweep the same ruling forbids**. Disclosed rather than skipped silently; the residue
  line reports them (`61 of 88` at this tree, unchanged by these amendments).
- **It does not raise or answer a `CLAUDE.md` §14 plan review.** W37-5c is a slice.
- **It does not ask for, or bear on, W37-6's go-ahead.** No re-ask exists at `d8d6e3f`
  (`git grep -iln "re-ask" -- docs/plans` finds the phrase only inside the slice decision, the
  ask and the roadmap — never a standalone filing), and the maintainer's only dated line in
  `2026-09-02-w37-6-go-ahead-ask.md` §8 remains *"Decision: not yet. Date: 2026-09-02."*

---

## 13. Recommendation

**The slice did what it was cut to do, and the most valuable thing it produced is a finding that
contradicts its own headline.** Seven scope items, all delivered; six findings filed; and
`migrate()` still aborts.

**Five things were recommended to the lead; four are done in this PR and one is deliberately
left.** Recorded as disposed rather than deleted, so the record shows what was asked and what
became of it.

| # | Recommended | Disposition |
|---|---|---|
| 1 | Adopt §8's table, amending any verdict read differently | **Done** — adopted 2026-09-02 with four amendments, all applied. F86's owner and F89's are the two the lead amended |
| 2 | Correct the register and the roadmap before merging | **Done in this PR**, on the lead's direction and their reading of the charter boundary (§5) |
| 3 | Treat F88 limb 1 as run-blocking, not blinding | **Done** — register `:129` reclassified; the headline above states it in the record's own words |
| 4 | Resolve §1 item 3's authority gap | **Done, and it was the lead's to do.** The maintainer's exemption ruling existed but had never landed as a dated artifact. **#648** files it verbatim, corrects its "63" to 65, and states that the exemption does not by itself let a run proceed. `CLAUDE.md` §12 — a decision lands as a dated artifact, never in chat |
| 5 | Give the no-register-row findings a home | **All three done.** The roadmap and register corrections are made, and the 53-file deferral is filed as **F92** — id allocated by the lead after this record declined to mint one, which cost a round trip and is the correct price (F88 limb 3 is what minting it unilaterally looks like) |

**W37-6 preconditions, collected for whoever plans it** — **F87**, **F88** (limb 1 run-blocking
and pre-write, limb 2 open), **F90**, and **F92** (the 53-file deferral, with its join to the
frozen leaf plan's item 13 now stated). **None of the four existed on any prior list**; each was
produced by building this slice and reading what its own instruments then reported.

## Sign-off

A Slice closes on **a clean audit and the lead's merge** (`CLAUDE.md` §13). No maintainer
acceptance is required for a slice — that is reserved to a Work, Phase or Project close, and
saying so here keeps this record from reading as one.

| | |
|---|---|
| Audit proposed by | the auditor, 2026-09-02, at `d8d6e3f` |
| Verdicts adopted by | **the lead, 2026-09-02**, with four amendments — all applied above, each named in the row it changed |
| Closed by | **the lead's merge, 2026-09-02** — `#647` squash-merged as `c888b61`. **Both acts a Slice close requires are now on record**: the clean audit above, and this merge. No maintainer acceptance is sought or required. |
