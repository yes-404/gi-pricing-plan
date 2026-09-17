---
id: FD-1015
family: finding
title: RL-986 §4's second acceptance item is vacuously true: no code path can ever write the `slice:` value the acceptance item asks a broken fixture to test
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F77.md
---

# F77 — RL-986 §4's second acceptance item is vacuously true: no code path can ever write the `slice:` value the acceptance item asks a broken fixture to test

Evidence essay for the register row self-named `(F77)` in `docs/findings/register.md`. Filed
by the W37-5b auditor, from a gap the executor who implemented RL-986 disclosed in their
own PR body rather than one this audit discovered independently.

## Provenance

`614c92c` (PR #599, "closure-records' not-closed WK-661 headings become LG- ledgers") ends its
own commit body with two disclosed gaps. The second reads in full:

> RL-986 §4's second acceptance item is vacuously true. It asks for a check that no
> emitted `LG-` carries a `slice:` resolving to no roadmap row, reddening on a fixture
> carrying `slice: SL-99999`. `_stamp_header` skips the `slice` key unconditionally, so no
> code path can write that value onto these records at all. Nothing is ever wrong because
> nothing is ever written, and there is therefore no guard and no red-on-broken-input test.
> Whether that satisfies the acceptance item is an interpretation of a merged ruling and is
> routed rather than decided here.

This essay verifies the claim rather than repeating it, and files the register row that
tracks it — the same shape F76 was filed for (a real gap, correctly disclosed by its own
author, with no register row before this audit).

## The defect, verified directly at `d47a5f5`

RL-986 §4's second acceptance item (`docs/rulings/RL-00986-the-ten-wk-661-slice-records-become-lg-carrying-work-and-no-slice-no-template-edit-is-needed.md:163-165`):

> A check that no emitted `LG-` carries a `slice:` whose value resolves to no roadmap row.
> *Violation: a `slice:` naming nothing.* … it must red on a deliberately broken fixture
> carrying `slice: SL-99999`.

`scripts/doc-id.py`'s `_stamp_header` (`:888-953`) renders every document family's
front-matter block by substituting the template's own placeholder lines. Its per-key
branch for `slice` (`:946`) reads:

```python
elif key in ("slice", "deliverable", "lands_in", "trigger"):
    continue  # not populated by this slice's migration — no data source for them
```

`continue` skips appending the line to `rendered` — for **every** caller, not only the
`LG-` path; the function takes no per-family branch that would exempt `LG-` from this and
populate `slice` some other way. Confirmed by search: `grep -n '"slice"' scripts/doc-id.py`
returns exactly this one site and two unrelated ones (a family-rank tie-break comment, and
`_write_document_drafts`'s docstring), never a write. A fixture carrying `slice:
SL-99999` on an `LG-` record therefore cannot be produced by any code path this migration
runs — the acceptance item's own broken-input scenario is unreachable, not merely untested.
`grep -rn "SL-99999" tests/ scripts/` returns nothing: no test attempts this proof, which is
consistent with there being nothing for such a test to exercise.

## Why this is not the same shape as "a guard nobody wrote yet"

RL-986 §4's first, third and fourth acceptance items are ordinary un-implemented
guards — a census assertion, a `work:`-resolves check, and a `status:`-per-record test —
each of which names something the code *could* violate today if it were wrong, and each of
which W37-5b's `d7c9b08`/`614c92c` pair does implement and test. The second item is
different in kind: there is no state that would make the guarded property false, because
the only value the property is stated *over* (`slice:` on an `LG-` record) is never written
at all. A check that "no code path can write X" is a true statement about the code, provable
by reading `_stamp_header` once; it is not a check that reddens on broken input, because no
input can break it.

## Scope of this finding

- **Not fix-before-close for W37-5b.** The census, the `work:` resolution, and the
  `status:`-per-record test — items 1, 3 and 4 — are built and tested
  (`tests/test_doc_id_migrate.py::test_closure_records_real_corpus_decomposes_into_ruling_84s_four_buckets`,
  `::test_write_document_drafts_resolves_a_ledgers_work_and_phase_from_the_roadmap`,
  `::test_closure_records_ledger_disposition_reads_the_trailer_not_the_body`, all green at
  `d47a5f5`). Only the second item is affected.
- **The question this row asks, rather than answers**: does "vacuously true because nothing
  is ever written" satisfy RL-986 §4's second acceptance item, or does the acceptance
  item need amending to say so explicitly (so a future reader does not go looking for a
  guard that was never going to exist), or does `slice:` need an actual data source before
  W37-6 runs (in which case the guard becomes buildable and testable)? This is an
  interpretation of a merged ruling, which `CLAUDE.md` §12 and this repository's practice
  reserve to the decision-maker, not to the executor who found it or the auditor who
  verified it.
- **Proposed disposition** (a proposal; the verdict is the lead's): deferred with an
  owner — **the decision-maker**, to rule which of the three readings above applies.
- **Falsifiable**: discharged when the decision-maker's ruling lands (accepting the vacuous
  reading in RL-986's own text, amending the acceptance item, or specifying a `slice:`
  data source), or by a corrected reading showing `_stamp_header` does have a path that
  writes `slice:` today.

## Update, 2026-09-02 — ruled while this essay was in review

The decision-maker has ruled ([RL-1000](../rulings/RL-01000-the-property-stands-the-instrument-is-amended-because-a-broken-input-need-not-be-a-document.md),
PR #614, merged `09b7e9b`), one commit after this essay's own tree (`d47a5f5`). None of the
three readings above is the one adopted — RL-1000 takes a fourth: **vacuously true does
not satisfy** (this essay's own conclusion, confirmed), and the acceptance item is neither
accepted-as-satisfied nor left to a `slice:` data source, but **substituted** for an
instrument that keeps the property instead of narrowing it: count the `slice:` values on
emitted `LG-` records, require each to resolve, print the count, and red on a **one-line
mutation of `_stamp_header`** (removing `slice` from its skip tuple) rather than a fixture
document — the shape RL-981 item 2 already established and Rulings 79/80 already use.

RL-1000 also corrects a citation this essay did not make but a routing brief did: at
`614c92c`, `_stamp_header`'s skip tuple already read `("slice", "deliverable", "lands_in",
"trigger")` — `phase` and `work` are separately guarded and are written when they resolve.
This essay's own code excerpt (above) already quoted the tuple correctly and drew no
conclusion about `phase`/`work` either way, so it needs no correction on that point.

**What remains open, verified directly at `09b7e9b`**: neither RL-1000's substituted check
(the count-and-print mechanism, tested via a `_stamp_header` mutation) nor an equivalent
guard for RL-986 §4's *third* item (`work:` must resolve; violation: a ledger with
neither axis) has been implemented — `git diff --stat` for PR #614 touches exactly one file,
the ruling record itself, no code. Item 3's underlying *resolution* is confirmed live and
correct on today's real corpus (`_discover_roadmap`'s one `WK-661` draft resolves against all
ten real closure-records `LG-` drafts), but no guard exists that would red if it ever did
not, and the existing unit test
(`tests/test_doc_id_migrate.py::test_write_document_drafts_resolves_a_ledgers_work_and_phase_from_the_roadmap`)
explicitly documents the opposite behaviour (silent omission, never a raise) as intentional —
correct for today's data, not a proof against tomorrow's. The register row (F77) is updated
to carry this rather than the pre-ruling deferral. Recommended verdict, proposed to the lead
rather than decided here: **not started** (`CLAUDE.md` §13) for both the substituted
count-and-print check and a "neither axis" guard for item 3, owner not yet named.

## Update, 2026-09-02 — built, and proven on the broken input RL-1000 named

Landed in W37-5c (scope item 4 of
[`../plans/PL-00957-w37-5c-the-slice-decision-and-gap-2-ruled.md`](../plans/PL-00957-w37-5c-the-slice-decision-and-gap-2-ruled.md)),
which took this row in as *"blinds the run"* rather than *"stops"* it. Written against
`ba31cd1`. **This supersedes the "Not yet built" finding of the section above**, which was
true at `09b7e9b` and is not true now; nothing else in this essay is retracted.

**What was built.** `_check_emitted_ledger_axes` in `scripts/doc-id.py`, with
`_emitted_ledger_headers` and `_resolves_to_row` beneath it. It reads the `LG-` documents
present under the ledger family directory of the migrated tree — from disk, never from
`migrate`'s own draft bookkeeping, the reason `migration_diff_violations` already gives —
counts the `slice:` values on them, requires each to resolve to an `SL-` row of that tree's
own `docs/roadmap.md`, and carries the three counts out on `MigrateResult` so `_cmd_migrate`
prints them unconditionally, the zeros included.

**Why it had to read the written files.** `slice:` exists nowhere in `_Draft`; it exists
only as the placeholder line of `docs/_templates/LG.md` that `_stamp_header` refuses to
emit. A draft-level check could not see RL-1000's mutation at all, which is the concrete
form of its point that the broken input for a writer is the writer.

**The mutation, run against the real corpus.**
`tests/test_doc_id_migrate.py::test_ledger_slice_check_reds_on_ruling_94s_stamp_header_mutation`
loads `scripts/doc-id.py` as shipped with one substring replaced — `slice` removed from
`_stamp_header`'s skip tuple — writes the ten real `WK-661 ... (in progress, not closed)`
records of `docs/closures/INDEX.md#closure-recordsmd` through it, and measures **10 `slice:` values and
10 violations**, each naming the template's own `SL-NNNNN`. The identical ten through the
unmutated module measure **0 and 0**. Both states are asserted in the one test, because the
signature RL-1000 §4 names as the violation is a check that reads the same before and
after.

**The resolve limb needed a second, hand-built pair**, and this is the one thing the ruling's
own broken input cannot reach: the mutation can only ever emit the placeholder, so it proves
the check reds on a `slice:` naming nothing and proves nothing about a `slice:` naming
something. `::test_ledger_slice_check_separates_a_resolving_slice_from_a_dangling_one` puts
two ledgers against one `SL-` row — one resolving, one dangling — and requires exactly one
violation. Written padded in the row and unpadded in the ledgers, so the resolution is shown
to go through `_docid.ID_RE` and not through string equality.

**RL-986 §4's third item is built in the same pass**, as RL-1000 §4 obliges — *"an
emitted `LG-` with `work=None` must red ... Violation: assuming an item is satisfied because
its sibling was found vacuous"*. Its violation clause is *"a ledger with neither axis"*, and
its broken input is again real: withhold the roadmap's `WK-661` draft and `_write_document_drafts`
omits `work:` from all ten, which
`::test_ruling_84_item_3_reds_on_an_emitted_ledger_with_neither_axis` measures as ten
violations against zero when the draft is present.

**One interpretation, flagged rather than made silently.** A `slice:` violation raises out of
`migrate()`; a `work:` violation is carried as a `MigrateResult` warning instead. The
asymmetry is deliberate and each half has its reason. The `slice:` count is zero by
construction today, so raising there adds no way for a real run to stop. Item 3 scopes itself
to *"once W37-6 has created the `WK-` rows"* — a state no run reaches while the three
unconditional guards (F80-F82) abort it first — so an aborting work-axis guard would be an
unmeasured new stop on an irreversible migration, which is the class W37-5c exists to remove
rather than add to. Both limbs are hard assertions in the tests either way. If the
decision-maker wants the work limb to abort as well, it is one line.

**What this row still waits on.** A verdict from its owner on those two instruments. It is
not claimed here that the row is discharged.
