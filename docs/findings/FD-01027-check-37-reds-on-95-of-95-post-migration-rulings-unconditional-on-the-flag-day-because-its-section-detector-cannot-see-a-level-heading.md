---
id: FD-1027
family: finding
title: check 37 reds on 95 of 95 post-migration rulings, unconditional on the flag-day, because its section detector cannot see a `###`-level heading
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F90.md
---

# F90 — check 37 reds on 95 of 95 post-migration rulings, unconditional on the flag-day, because its section detector cannot see a `###`-level heading

**Raised** 2026-09-02 by `sweep-acceptance-items`, from the lead's W37-6 precondition sweep
against piece 1 of the ruling-form flag-day (`#640`, merged `dc1666f`). Work item **W37-6**,
scope: `check_shape` (check 37) over the `family: ruling` population. Phase 2.

**F87's shape, in a second place.** F87 found `_ID_SCOPE_ROOTS`'s widening necessary but not
sufficient, because the glob excludes 62 of 65 files regardless of the roots. This finding
is the same class one mechanism over: widening the scope *and* migrating the corpus is
still not sufficient for check 37, because its `##`-only detector cannot see how any real
ruling — including ones written specifically to comply — is actually structured.

## The defect

`required_sections('ruling')` derives its required set from `docs/_templates/RL.md`'s own
`##`-level body headings — Question, Ruling, Rationale, and, since piece 1 (`936e808`),
Acceptance. `check_shape` compares that set against `_template_body_sections(path)`, which
matches only `_SECTION_HEADING_RE = ^##\s+` — never `###` or deeper.

Every real ruling lives, pre-migration, as one `## Ruling N — <title>` heading inside a
multi-ruling file under `docs/plans/`. `doc-id.py`'s migration (`_discover_multi_ruling_
files`) preserves that heading verbatim as the split boundary and carries the body beneath
it unchanged — numbered `###` subsections or bold-lead-in prose, never sibling `##`
headings. A migrated ruling document therefore has exactly one `##`-level heading — its own
`## Ruling N` — and it never reads "Question", "Ruling", "Rationale" or "Acceptance — the
violation that must become detectable". `required_sections` demands four; `_template_body_
sections` can structurally find at most one, and that one never matches any of them. Every
migrated ruling reds on all four, independent of which ones the ruling-form flag-day
(`aab6327`) already covers.

## The measurement

Tree: `docs/skills-marker-vs-property` @ `4df1c45` (PR #640's tip, containing piece 1) — not
literal `origin/main`, which does not carry piece 1's fourth section, so cannot show
whether *it* adds a hazard. A disposable local clone, discarded after measuring; nothing
written outside it.

PR #634's technique (root substitution: `_ID_SCOPE_ROOTS = (ROOT, .claude/roles,
.claude/skills, .claude/agents)`, `_widened_roots` in `tests/test_audit_docs_ids.py`) is
necessary but not sufficient here — check 37's targets do not exist as documents until
migration runs, unlike check 35's F83 register, which is why the root substitution alone
was sufficient there and not here. Extension: `doc-id.py`'s own unmodified splitter
(`_discover_multi_ruling_files`, `_discover_lettered_rulings`, `compute_next`,
`_assign_numbers`, `_write_document_drafts`) run narrowly — the ruling family only, not the
full `migrate()`, which aborts on unrelated roadmap/note/ADR shapes that have nothing to do
with this question — against the clone, to materialise real stamped `RL-*.md` files with
verbatim bodies (no synthesis: `_discover_multi_ruling_files` slices `section_text =
text[start:end]` directly from the source). Then the widened roots, then the real,
unmodified `check_shape()`.

| | Count |
|---|---|
| Ruling headings `doc-id.py`'s splitter discovers | **95** |
| Of those, parsed successfully as `family: ruling` (confirmed below) | **95** |
| Of those, red on check 37 | **95** |

**Confirmed independently that all 95 parsed before checking which reded** — zero were
silently excluded by `HeaderError`, so the clean-looking part of this result (a full 95
denominator) is not parse failure in disguise.

Reproduce with the shipped symbols, against a disposable clone (never the real tree):

```python
import importlib.util, pathlib, sys
CLONE = pathlib.Path("<disposable clone of this repo>")
sys.path.insert(0, str(CLONE / "scripts"))

def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, CLONE / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

d = load("d", "scripts/doc-id.py")
a = load("a", "scripts/audit-docs.py")

drafts = d._discover_multi_ruling_files(CLONE) + d._discover_lettered_rulings(CLONE)
d._assign_numbers(drafts, d.compute_next(CLONE))
written, _ = d._write_document_drafts(CLONE, drafts, roadmap_drafts=())

setattr(a, "_ID_SCOPE_ROOTS", (a.ROOT, a.REPO / ".claude" / "roles",
                                a.REPO / ".claude" / "skills", a.REPO / ".claude" / "agents"))
a.failures.clear()
a.check_shape()
ruling_fails = [f for f in a.failures
                if f.startswith("check 37:") and "for family 'ruling'" in f]
len(written), len(ruling_fails)   # 95, 95
```

## The exemplar: a compliant ruling still reds

RL-984 (`` owner: `` is who may amend; the A-series takes `` decision-maker ``) is in the
`w37` bucket of `scripts/ruling-acceptance-item-census.py`'s own classification — it carries
a real, correctly-written, post-flag-day acceptance item, by that script's own (intentionally
depth-agnostic) test. Its migrated body reads:

```
## RL-984 — `owner:` is who may amend; the A-series takes `decision-maker`
### 1. Verified first, at `64f63ee`
### 2. Ruled
### 3. What it obliges — and what is *not* struck
### 4. Acceptance — the violation that must become detectable
```

The literal required phrase is there, verbatim — **at `###`, one level under the split
boundary.** `_template_body_sections` cannot see it. This is the sharper claim than "35
rulings lack a section": **the 30 rulings written specifically to satisfy the flag-day fail
the same way as the 35 that were never asked to.** A ruling written today, correctly, in
the exact form the flag-day requires, still reds.

## Does check 37 honour the flag-day

No — plainly, not at all. No `_FLAG_DAY_COMMIT`, no per-heading introduction date, nothing
date-conditional anywhere in `required_sections`/`check_shape`; the same rule applies to a
ruling filed in 2026-01 and one filed today. But say precisely what that does and does not
mean: a date carve-out modelled on the census script's `flag_day_split` would correctly
exempt the 35 `none`-bucket rulings, and would **not** fix the 30 — their defect is heading
depth, not age, as RL-984 shows directly.

## Secondary finding — a third instance of RL-985's matcher-mismatch class

Census's `classify()` places rulings 59 and 61 in `standalone` and 60 in `prose_only` — 3 of
its 98 — but `_discover_multi_ruling_files`/`_discover_lettered_rulings` (`doc-id.py`'s own
splitter) discovers none of the three; confirmed by diffing the two id sets directly, not
assumed. RL-985 (`docs/rulings/RL-00985-the-census-must-not-be-counted-with-the
-splitter-s-own-pattern-585-s-shape-does-not-generalise-and-a-matcher-derived-denominator-is-why.md:121`, read directly before this citation was written) already ruled on exactly
this class of risk — a census counted against its own matcher rather than the splitter's,
because the two can diverge — for a different pair of matchers. It recurring between a
third pair (the acceptance-item census and the migration splitter) is the point: two
independently-written matchers over the same corpus disagreeing is not a one-off here.
**Not chased further** — outside what was asked, and the 95 above does not depend on it
either way: it is what this splitter itself produces. If some other migrate() path also
converts 59/60/61, the true post-W37-6 ruling population is 98, not 95, and this
measurement does not speak to those three.

## Custody

Per [`RFC-778`](../rfcs/RFC-00778-seven-deferred-items-with-no-durable-custody.md), a deferred item
with no owner is not deferred, it is lost. This one is owned — **W37-6** — but the event
that discharges it is not automatic: the four options below must be dispositioned before
the next W37-6 go-ahead request is made, the same shape of gate F87 is already filed
against (work item W37-6, fix before close). Absent that disposition, this row decays to
the next `CLAUDE.md` §14 plan review, which must give it a disposition rather than list it
— the register row carries the `§14` literal for that reason, independent of whether the
W37-6 tracking catches it first.

## Options — not dispositioned here; the register row names the same four

1. **Date-grandfather check 37**, mirroring `flag_day_split`. Exempts the 35. Leaves the 30
   red — their problem is depth, not date.
2. **Make the section optional in the template, required only for post-flag-day rulings.**
   Same gap: a post-flag-day ruling still nests Acceptance at `###`, so this does not turn
   the 30 green either, absent a depth fix.
3. **Accept that W37-6 backfills the section into the 35.** Does not reach green on any of
   the 95 as measured: Question/Ruling/Rationale are `##`-unmet by all 95 independent of
   piece 1 (that requirement predates it), so a 35-document Acceptance backfill still
   leaves 95 red on the other three sections.
4. **Make `_template_body_sections`/check 37's detector depth-agnostic**, mirroring the
   census script's own design (`docs/_templates/RL.md`'s comment: the phrase match is "any
   heading depth, case-sensitive"). The only option of the four that makes RL-984 pass
   as measured. Changes behaviour for all ten families sharing `check_shape`, not just
   rulings, and needs its own broken-input proof — the way the flag-day's own carve-out
   (piece 2) got one before it was trusted.

## Falsifiable

**On the detector, not the count.** Discharged when `check_shape`, unmodified in its
matching logic, reports RL-984's migrated form (or an equivalent hand-built fixture
carrying the same `###`-nested Acceptance heading) as satisfying `required_sections`'s
Acceptance clause — a compliant ruling passing, not the red count dropping, because a count
can drop for reasons unrelated to the detector (fewer rulings in scope, a narrower
`_ID_SCOPE_ROOTS`) without the mismatch this finding reports being fixed at all.

**Not discharged by**: the flag-day census reporting fewer `none`-bucket rulings (piece 2
measures a different, phrase-based, depth-agnostic marker — it is already green on Ruling
95 today, which is exactly why the two mechanisms disagreeing is the finding); by
`origin/main` showing zero check-37 ruling failures (true today only because no migrated
ruling document exists yet — F87's exact shape, a check reporting green over a scope that
excludes everything it was built to police); or by backfilling the 35 alone (leaves 95 red
on the other three sections, per option 3 above).

---

## Amendment, 2026-09-02 — the measurement is re-pinned to a reachable tree, and option 4 does not work

Added by the W37-6 F90 executor on the lead's dispatch, which asked for the four options to
be verified before any of them is built. **No remedy is dispositioned here** — that remains
the event this finding's register row names. Three of this finding's own statements are
corrected, all by execution rather than by reading.

### A. Re-pinned: 95 of 95 reproduces at `origin/main` `32fc63c`

The measurement above is taken at `4df1c45`, which the WK-697 roadmap row records as reachable
in one local checkout and in no remote ref. Re-run at **`32fc63c`** — `origin/main`, which
carries piece 1 as `dc1666f` — against a disposable snapshot (`git archive origin/main | tar
-x -C <tmp>`), using this finding's own reproducer verbatim:

| | Count at `4df1c45` | Count at `32fc63c` |
|---|---|---|
| Ruling headings the splitter discovers, written as `RL-*.md` | 95 | **95** |
| Of those, red on check 37 | 95 | **95** |

The count stands. **It is now pinned to a commit a fresh clone can resolve**, which is what
the roadmap row asked this finding's disposition to do.

### B. Correction — option 4 does **not** make the exemplar pass

The option list says option 4 is *"the only option of the four that makes RL-984 pass as
measured."* Run, it makes nothing pass. Measured over all 95 migrated documents at
`32fc63c`, counting how many carry each required section as a heading text:

| Required section (from `docs/_templates/RL.md`) | Exact, at `##` | Exact, at any depth | Any depth, after stripping a leading `N. ` |
|---|---|---|---|
| `Question` | 0 | **0** | **0** |
| `Ruling` | 0 | **0** | **0** |
| `Rationale` | 0 | **0** | **0** |
| `Acceptance — the violation that must become detectable` | 0 | **0** | **30** |

Two things follow, and both enlarge the problem rather than restating it:

1. **Depth is not the only mismatch.** Every real ruling numbers its subsections — `### 4.
   Acceptance — the violation that must become detectable` — so a depth-agnostic literal
   match still finds nothing. A detector has to be depth-agnostic **and** tolerant of an
   ordinal prefix before the 30 compliant rulings turn green. Confirmed by running a
   depth-agnostic `check_shape` end to end: check-37 ruling failures go 95 → **95**.
2. **Three of the four required sections do not exist in the corpus under any name, at any
   depth, numbered or not.** `Question`, `Ruling` and `Rationale` are 0 of 95 in every
   column. No change to the detector can make a single migrated ruling pass check 37,
   because the sections it requires were never written. **The template's body shape does not
   describe how rulings are actually written**; it describes how a ruling authored from
   `RL.md` after the standard lands would be written. That is the real disagreement, and it
   is not a matching bug.

### C. Correction — "exactly one `##`-level heading" is false for 55 of 95

The defect section states a migrated ruling *"has exactly one `##`-level heading — its own
`## Ruling N`."* Measured over the 95 at `32fc63c`, the distribution of `##`-level headings
per document is:

| `##` headings | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Documents | 3 | 40 | 17 | 18 | 7 | 7 | 3 |

The splitter carries the source file's own preamble sections with the ruling — `Authority`
(11), `Acceptance Standard` (16), `Verification` (12), `Provenance` (12), `Not ruled — and
where each goes` (10). The exemplar itself, migrated as
`docs/rulings/RL-00082-owner-is-who-may-amend-the-a-series-takes-decision-maker.md`, carries
**four** `##` headings. **The conclusion is unchanged** — none of those headings is a
required one, so all four still red — but the stated mechanism was wrong, and a reader
sizing a remedy from "one heading" would size it wrongly.

### D. What the option list now has to answer

Options 1, 2 and 4 were each scoped against a single missing section. Against the table in
§B, none of the four reaches green, and a fifth shape is implied by the data rather than
proposed here for adoption:

- **1 (date-grandfather)** — exempts the 35 by age. The 30 stay red, and now for two reasons
  rather than one.
- **2 (post-flag-day-only section)** — same, and no better than 1 against §B.
- **3 (backfill the 35)** — leaves 95 red on `Question`/`Ruling`/`Rationale`.
- **4 (depth-agnostic detector)** — measured at 95 → 95. Insufficient alone; and it is not
  free elsewhere, see §E.
- **5 (implied by §B, not proposed)** — treat a verbatim-migrated body as out of check 37's
  scope, or reconcile `RL.md`'s declared body shape with the shape rulings are actually
  written in. Only a remedy of this kind can reach green, because three of the four required
  sections are absent from the corpus rather than mis-detected.

### E. What option 4 does to the other families sharing `check_shape`

`check_shape` serves twelve families through `_TEMPLATE_FAMILY`; nine currently have a
non-empty required set. Making `_template_body_sections` depth-agnostic **on both sides** —
template and document, as the option is worded — changes what two families require:

| Family | Template | Required now | Required if depth-agnostic |
|---|---|---|---|
| `slice` | `SL.md` | *(none)* | `SL-NNNNN — <Title>` |
| `work` | `WK.md` | *(none)* | `WK-NNNNN — <Title>` |
| The other ten | — | unchanged | unchanged |

Both new requirements are **template placeholders**, which no real document can satisfy.
`_template_body_sections`'s own docstring records the assumption this breaks — *"No template's
own body heading uses a `<Title>`/`NNNNN` placeholder (verified by reading all thirteen)"* —
which is true at `##` and false at `###`, and it is the `##` restriction that is currently
holding it up. `PHASE.md` carries a `##`-level placeholder (`## P<n> — <Title>`) and is safe
only because it declares no header block and so maps to no family.

**Stated as a measurement rather than as a prediction, because the two differ here.** Run
symmetrically against the fully migrated corpus (§F), check-37 failures are **284 before and
284 after** — no `slice` or `work` failure appears, because **that corpus contains zero
documents of either family**: `WK-` and `SL-` are roadmap *rows*, not documents, so nothing
is in check 37's scope to red. The requirement change is real and the placeholder is real;
the damage is **latent**, arriving with the first `slice` or `work` document rather than at
the migration. A remedy built on option 4 should still exclude a placeholder heading
explicitly rather than rely on that emptiness, which nothing enforces.

**An asymmetric variant** — derive the required set from the template at `##` as now, scan
the document at any depth — leaves all twelve required sets byte-identical (verified by
running `required_sections` for every family both ways) and can only ever turn a red green.
It was run end to end and still gives 95 to 95 on rulings, per §B, so it does not on its own
discharge this finding either; it is recorded because it is the variant that does not carry
the placeholder cost above.

### F. The population is 284 documents across six families, not 95 across one

This finding scopes itself to `family: ruling`, which is what it was asked about. Run against
a **fully migrated** corpus — `migrate()` to completion on a disposable snapshot of
`origin/main` `32fc63c`, then the real `check_shape()` with `_ID_SCOPE_ROOTS` widened —
check 37 examines **529** documents and reds **284**:

| Family | Red on check 37 |
|---|---|
| `plan` | 119 |
| `ruling` | **95** |
| `closure` | 38 |
| `proposal` | 20 |
| `ledger` | 10 |
| `research` | 2 |
| **Total** | **284** |

The 95 is **a third of the problem**, and every other red is the same mismatch: a template
body shape that describes how a document would be authored from the template, applied to a
body the migration carried over verbatim from a pre-standard file. A remedy scoped to
`family: ruling` leaves 189 documents red on the same cause. **This does not change any
disposition here** — it changes the size of what a disposition has to cover, and it is the
number a W37-6 go-ahead disclosure needs rather than the 95.

### Reproducer for this amendment

Against a disposable snapshot of the tree, never the repository — materialised with
`git archive`, then `git init` plus one commit so `ls-files` resolves:

- **§A, §B, §C** — run `doc-id.py`'s splitter narrowly (`_discover_multi_ruling_files` +
  `_discover_lettered_rulings`, `_assign_numbers`, `_write_document_drafts`) to materialise
  the 95, then count required-section headings per document under three patterns —
  `^##\s+`, `^#{2,6}\s+`, and `^#{2,6}\s+` with a leading `\d+\.\s+` stripped from the
  captured text — and run the real `check_shape()` once unmodified and once with
  `_template_body_sections` widened on the document side only.
- **§E, §F** — run `migrate()` to completion on a second snapshot, then `check_shape()` with
  `_ID_SCOPE_ROOTS` widened, once with the shipped `_SECTION_HEADING_RE` and once with it
  replaced by `^#{2,6}\s+`, bucketing failures by the family named in each message.

`scripts/` is unmodified by this amendment, and nothing was written outside the snapshots.
