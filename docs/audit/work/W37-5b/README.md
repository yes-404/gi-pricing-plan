# Work-item record — W37-5b (the group-A preconditions slice)

Follows [`close-workstream`](../../../../.claude/skills/close-workstream/SKILL.md) (version
current through its 2026-08-31 §5b entry) and
[`work-item-close.md`](../../checklists/work-item-close.md). Proposed by the auditor; **not a
close** — `CLAUDE.md` §13 closes a Slice on a clean audit and the lead's merge, and every
verdict below is a proposal for the lead to adopt, amend or reject.

**Measurement tree: `3f41d60`.** The dispatch named `d47a5f5`; `origin/main` advanced three
commits while this audit ran — `09b7e9b` (#614, Ruling 94), `2eef65b` (#615, `git-hygiene`
traps), `3f41d60` (#616, `ci-watcher`). None touches group-A code
(`git diff --stat 09b7e9b..3f41d60` names only skill/agent documentation), but `09b7e9b`
directly rules one of the two named deferrals below, so citing the later tree is what lets
this record report the true current state rather than one already superseded when filed.
Every count below is re-derived at `3f41d60`, none inherited from a PR body.

## 0. Scope, derived from the decision record before any evidence was sought

[`2026-09-02-w37-5b-slice-decision.md`](../../../plans/2026-09-02-w37-5b-slice-decision.md)
§3 states group A as **eighteen rows: 1–15, 30, 31, 36**, against
[`2026-09-02-w37-6-outstanding-obligations.md`](../../../plans/2026-09-02-w37-6-outstanding-obligations.md)
§3's 39-row table. Verified both directions: the decision's own count table reads
`18 = 16 built + 1 lead (14) + 1 routed (36)`, and the obligations table's Gate column marks
exactly rows 1–15, 30, 31, 36 as gate **A** ("before" the migration run).

**One title/body disagreement in the obligations list itself, immaterial to scope**:
`b648c22`'s commit subject reads "one list, **35** items"; its body (a sentence wrapping
across a line break a single-line grep misses) reads "of **39** obligations, none is
closed." The §3 table runs 1–39. Scope here is the table's, not the title's — flagged so the
title is never read as authoritative.

```
group A                        18   (1–15, 30, 31, 36)
  built in W37-5b               16   (1–13, 15, 30, 31)
  carve-out 1 — the lead         1   (14)
  carve-out 2 — routed           1   (36)
```

## 1. The slice decision's own Acceptance Standard — scored item by item

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1 | W37-5b named in the W37 row's `Progress` clause, scope stated **by number**, not as a row of its own | **Partially met** | `docs/roadmap.md`'s W37 row (added `01bd0bd`) names the slice and its decision file, and describes scope by category and count ("sixteen items") rather than the literal row numbers the acceptance item's words ask for. No row is created (`grep -c '\*\*W37-5b\*\*' docs/roadmap.md` → 0, correct). **Corrected in this PR**: the Progress clause now cites every row number against its evidence inline (see the roadmap diff in this PR). |
| 2 | Every group-A row has a named owner | **Met — 18 of 18** | §2 below. Sixteen delivered-and-tested; two (14, 36) are discharged carve-out rulings/fixes. None silent. |
| 3 | A new dated leaf plan for W37-6, superseding the frozen one by name and date, carrying Ruling 73's amendment inline | **Met** | [`2026-09-02-w37-6-migration-run-leaf-plan-v2.md`](../../../plans/2026-09-02-w37-6-migration-run-leaf-plan-v2.md), filed draft (`958cb7d`), lifted to `status: active` (`f9975f1`) once Ruling 88 resolved its one blocking row. Header states: *"Supersedes: [the frozen plan]... which is frozen at its date and is not edited."* Item 11 restated in full inline, not by reference. Frozen original confirmed untouched: `git diff --stat b648c22..3f41d60 -- docs/plans/2026-09-02-w37-6-migration-run-leaf-plan.md` is empty. |
| 4 | This record cited where W37-5b's close is recorded | **Met** | The roadmap's `Progress` clause cites the decision file and, in this PR, this record; this record cites both. |

## 2. Every group-A row, evidence or verdict

Verified independently at `3f41d60` — commands re-run by this audit, not PR bodies taken on
their word (`CLAUDE.md` §13 rule 2).

| Row | What it was | PR(s) | Verdict | Independent confirmation |
|---|---|---|---|---|
| 1 | Plan-reviews under-discovery (10 of 14, trailing-text anchor) | `4367cf7` (#602) | **Delivered, tested** | `_discover_plan_reviews(ROOT)` → **11** (of 14 headings); `_REVIEW_HEADING_RE` now captures a trailing group instead of anchoring on `\s*$` — read directly. |
| 2 | `_discover_roadmap` converts 0 of 41 works, reports success | `4cbfa62` (#610) | **Delivered, tested** | `_discover_roadmap(ROOT)` → **41** works, phase split 7+5+14+8+7=41, status closed 15 / active 25 / retired 1. |
| 3 | `_discover_register` matches 0 of 73 rows | `4cbfa62` (#610) | **Delivered, tested** | `_discover_register(ROOT)` → **73**. |
| 4 | Ten `W5 —` closure headings raise on the first, stopping the run | `614c92c` (#599) | **Delivered, tested — see §3 for a correction to this commit's own body** | Independently counted `docs/audit/closure-records.md`: **21** real `###` headings, reconciling to 8 `CR-work` + 1 `CR-phase` + 2 `RS-audit` + 10 `LG-`, exact match to `_discover_closure_records(ROOT)`'s live output and to `test_closure_records_real_corpus_decomposes_into_ruling_84s_four_buckets` (ran narrowly, passes). |
| 5 | Zero-drafts guards catch total silence, not undercount | `d7c9b08` (#608), `4367cf7` (#602) | **Delivered, tested** | `_reconcile_census` (`doc-id.py:2225`) read in full: a three-bucket (record / derived body / declared exception) reconciliation that names every unmatched unit, not a count comparison. Red-before/green-after read directly in `d7c9b08`'s own body: "27 failed... 189 passed after." |
| 6 | `Ruling A1`–`A3`: family undetermined, blocking the census | derivation `04f47b2` (#595), ruled `cc17404` (#598, Ruling 86) | **Ruled — three `RL-` records; discovery code not yet written — filed as F81** | The guard still, correctly, reds on the real file today: `_check_multi_ruling_files_not_silently_unrecognised(ROOT)` raises naming `docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md`'s real `### Ruling A1` heading as unclassified — proving the guard works and the discovery gap is real, not that row 6 failed. See §6, F81. |
| 7 | "Pending proposals" container: family undetermined | derivation `44ec54e` (#597), ruled `f4cbbb7` (#601, Ruling 88), amended `22d8d64` (#612, Ruling 93) | **Ruled — `RFC-`, `kind: process`, `owner: maintainer`; discovery code not yet written — see F80** | `docs/audit/plan-reviews.md` re-counted: **0** level-2 headings, **12** level-3, **28** level-4, matching Ruling 93's replacement-fixture requirement. But the guard this slice itself built (row 1) now correctly reds on this same container's *undecided disposition*: `_check_plan_reviews_heading_census(ROOT)` raises naming line 1155's "Pending proposals" heading — filed as **F80** (§6). |
| 8 | `_ROW_FIELDS` hardcoded and wrong both directions; `scan_phase_sections` unbounded lookahead | `e7e1d24` (#593) | **Delivered, tested** | `row_template_fields` (`_docid.py`) derives the field set per family from the real template files — read directly, part of the 302 green tests. |
| 9 | `is_vendored` keys on `LICENSE`, exempting 2 of 28 | `574d536` (#611) | **Delivered, tested** | `_VENDORED_SKILLS`: **28** entries, counted directly. `vendored_skills_ruff_exclude_mismatch(Path('.'))` → `(frozenset(), frozenset())` — zero mismatch either direction against `pyproject.toml`'s ruff exclude list. |
| 10 | `REFERENCE.md` still teaches the rejected criterion | `574d536` (#611) | **Delivered** | `docs/_templates/REFERENCE.md:39-49` now states "a hand-kept list, not a filesystem property... Ruling 69 rejected that detection rule" — read directly. |
| 11 | Five tests pin the rejected criterion | `574d536` (#611) | **Delivered, tested** | `tests/test_doc_id.py`'s `is_vendored` tests now monkeypatch `_VENDORED_SKILLS` for membership, no `LICENSE` inspection — read directly. |
| 12 | F76 — check 39's uncaught `HeaderError` silently drops six later checks | `35c1488` (#607) | **Delivered, tested** | `check_index_stable` wraps `build_corpus` in `try/except (_doc_index.HeaderError, ValueError)`, covering both crash paths. Register row F76 updated to **Resolved** (§4). |
| 13 | No check feeds a template's own example block to its consuming parser | `e7e1d24` (#593) | **Delivered, tested** | `test_document_template_parses_to_its_family_once_filled_in` and `test_row_template_fenced_block_parses_through_doc_index_row_parser` exist and pass. |
| 14 | `plan-reviews.md` heading mis-nesting (carve-out — the lead's) | `2fbce0c` (#609) | **Delivered by the lead** | Structural fix confirmed: 0 level-2 / 12 level-3 / 28 level-4 headings, matching the leaf plan's decomposition. |
| 15 | Does the multi-ruling splitter try to split the three h1 ruling files? | measured in `a31d509` (#603), `d7c9b08` (#608) | **Measured — no** | Ran `_discover_multi_ruling_files(ROOT)` directly: 35 source files touched, none of the three named h1 files among them. **One false lead corrected in drafting this record**: `docs/plans/2026-09-02-w37-ruling-88-acceptance-amendment.md`'s h1 title, "# Ruling 88's second acceptance item...", matches a loose `^# Ruling [0-9]` grep but is not a standalone ruling record in canonical form — it is Ruling 93's own file, titled as a description of the ruling it amends. Confirmed by reading the heading directly; the count stays **three**, per the obligations list. |
| 30 | `_discover_requirements`: no guard at all | `d7c9b08` (#608) | **Delivered, tested — guard's own live finding is new and unowned, see F-note below** | `_discover_requirements(ROOT)` → **660** (unchanged count, confirming nothing regressed). The new guard correctly reds today, naming `docs/specs/00-overview.md`'s real, unclassified `DEP-1`, `DEP-1a`, `DEP-2`, `DEP-3` — a genuine disclosed gap the guard was built to find, not a false positive. |
| 31 | Four more discovery functions silent by construction | `d7c9b08` (#608) | **Delivered, tested** | All five `_reconcile_census` call sites confirmed by direct read (`:2354` shared by rows 4/7, `:2506`, `:2559` [row 30], `:2598`, `:2634` shared by `_discover_notes`/`_discover_adrs`). |
| 36 | §8-vs-Ruling-66 stage-boundary conflict (carve-out — routed) | ruled `e74a683` (#596, Ruling 85) | **Ruled — reading 1: §8 is sequencing, not part of the accepted standard; Ruling 66 stands unamended** | Ruling 85's verdict rests on `docs/process/document-ids.md` (the maintainer-owned standard) lifting only §1.1–§1.13, never §4/§5/§7/§8 — confirmed by direct read of the document's own title, "NT-0019 §1, lifted verbatim." |

**Result: 18 of 18 group-A rows carry evidence or a discharged ruling. None is silent.**
Rows 6, 7, 12 and 30's own new guards are now, correctly, live-red on the real tree — that is
the fix working, not a defect in it, and none of it was any group-A row's own job to also
resolve (§6, "What `migrate()` cannot do today").

## 3. The `614c92c` correction — verified before writing either

The dispatch flagged that `614c92c`'s commit body states the closure-records census gap is
open and carried as a follow-up, and that the census in fact landed in the same commit.
**Confirmed, with one refinement.**

`614c92c`'s own body says, of two disclosed gaps: *"The census does not reach this file...
none of the census call sites covers closure-records.md... It is not closed here... Carried
as a named W37-5b row with an owner rather than left to be rediscovered."*

**This is false as a claim about the commit's own diff.** `git show 614c92c --
scripts/doc-id.py` shows `+def _check_closure_records_not_silently_unrecognised(root: Path)
-> None:` added in that same commit (`doc-id.py:2384`), wired into `migrate()` at `:2990`
immediately after `_discover_closure_records` runs. Its docstring states plainly it exists
*because* the general five-site census (`d7c9b08`, merged ~30 minutes earlier the same day)
does not reach this file's bespoke discovery loop, and reuses
`_check_heading_split_not_silently_unrecognised` — the same `_reconcile_census`-backed
mechanism — to close exactly that gap for this file.

Independently re-verified, not merely read: `test_closure_records_census_names_an_undercounted_heading`
constructs a dateless `###` heading and asserts the raise names it (ran narrowly, passes);
`..._is_silent_on_a_clean_file`, `..._treats_a_nested_subheading_as_body`,
`..._is_silent_on_a_missing_file` and `test_migrate_raises_via_the_closure_records_census_on_a_real_shaped_tree`
all exist and pass — a genuine positive/negative control pair, not a check that has never
printed a failure. **No register row exists anywhere for "the census does not reach
closure-records.md"** — consistent with the claim being false rather than merely unrecorded.

**What was accurate in `614c92c`'s body**: its *second* disclosed gap — Ruling 84 §4's
`slice:` acceptance item being vacuously true — is correct (§5a below).

**Recommendation**: cite `614c92c` by hash wherever this correction is recorded, per the
maintainer's instruction, rather than editing the squashed commit body, which cannot be
amended without a force-push `main-protection` forbids.

## 4. Register update — F76 resolved

F76 ("an uncaught `HeaderError` in check 39 silently drops six later checks") predates this
slice, named `W37-6` as owner via Ruling 79, and was never revisited after row 12's fix
landed (`35c1488`) — a silent-staleness gap in the register itself, independent of any PR's
own claims. **Annotated in place** as **Resolved 2026-09-02**, original verdict text kept
below it per the register's own convention, rather than deleted.

## 5. The two named deferrals

### 5a. Ruling 84 §4's second acceptance item (`slice:` vacuity) — ruled mid-audit

Filed as register row **F77** ([essay](../../findings/F77.md)). Verified independently:
`_stamp_header`'s `elif key in ("slice", "deliverable", "lands_in", "trigger"): continue`
(`doc-id.py:946`) — no `slice` parameter exists in the function's signature at all, so no
caller can ever write it.

**This deferral was ruled while this audit was in progress.** `origin/main` advanced onto
`09b7e9b` (Ruling 94, PR #614) mid-session. Ruling 94 holds: *"an acceptance item that is
vacuously true does not satisfy itself"* (`CLAUDE.md` §13: "a check that has never printed a
failure has not been tested"); rejects narrowing the invariant (it would wrongly red the
first time a ledger legitimately carries `slice:`, since Ruling 84 §3 item 5 keeps it
permitted for every other ledger); and specifies a **substitute** instrument — count the
`slice:` values on emitted `LG-` records, require each to resolve, print the count, reddening
on a **one-line mutation of `_stamp_header`** rather than a fixture document.

Ruling 94 also corrects a stale-tree quotation error in an earlier version of the lead's own
report (the skip tuple misquoted as containing `phase`, `work` and `slice`, read from a
checkout still at `2fbce0c`). **This audit's own direct read (pinned via `git show
d47a5f5:scripts/doc-id.py`) and this audit's fork essay (`F77.md`) both independently quoted
the tuple correctly before Ruling 94 was written.**

**What Ruling 94 leaves open**, verified directly at `3f41d60`: neither the substituted
count-and-print check nor an equivalent guard for §4's *third* item ("`work:` resolves";
violation: a ledger with neither axis) is implemented — `git diff --stat` for PR #614
touches exactly one file, the ruling record. Item 3's resolution is *live and correct* on
today's real corpus (`_discover_roadmap`'s one `W5` draft, phase `P1b`, matches all ten real
`LG-` drafts' `work_token`), but no guard would catch a future regression, and the existing
unit test documents silent omission on an unresolved token as intentional — correct for
today, not a proof against tomorrow.

**Proposed verdict**: the interpretation question is **discharged by Ruling 94**, cited
rather than carried forward. The remaining implementation (count-and-print check, "neither
axis" guard) is **not started**, no owner yet named — register row F77 updated accordingly.

### 5b. `#610`'s phase-spanning refusal — genuinely open, owner W37-6

Filed as register row **F78** ([essay](../../findings/F78.md)). `4cbfa62`'s own body:
*"Disclosed and not built: no fixture exercises the phase-spanning refusal... named as a
follow-up rather than the row being called done."* Confirmed independently: the refusal code
exists (`doc-id.py:1917-1925`, `unresolved_phase` → `NotImplementedError`); no test exercises
either direction; `_discover_roadmap(ROOT)` confirms the branch is not entered today (all 41
works resolve to exactly one phase each).

**Proposed verdict**: **deferred with an owner — W37-6**; discharge is a fixture forcing two
leading rows of one work id into different phase sections and asserting the raise names both.

## 6. What `migrate()` cannot do today — new, not one of the 39 rows

Not a group-A shortfall — no row promised this — but measured directly and stated plainly,
because no merged PR body states it as a set: **running the real W37-6 migration against
today's tree would abort at the first of at least three independent, unrelated guards**, each
one this slice's own new instrumentation correctly catching a real, pre-existing gap:

1. `_check_multi_ruling_files_not_silently_unrecognised` — the real Ruling A1/A2/A3 file
   (`docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md`), ruled `RL-` (Rulings 86/87) but
   with no discovery code yet — earliest in the pipeline (`doc-id.py:2984`), so a real run
   would halt here first. Filed as **F81** ([essay](../../findings/F81.md)), unowned.
2. `_check_plan_reviews_heading_census` — the "Pending proposals" container, ruled `RFC-`
   (Ruling 88/93) but with no discovery code yet (`doc-id.py:3000`). Filed as **F80**
   ([essay](../../findings/F80.md)), unowned. Not one of the obligations list's 39 rows:
   Ruling 88 postdates `b648c22` by several commits, so the list could not have named a
   defect in a ruling that did not yet exist.
3. `_check_requirements_not_silently_unrecognised` — `DEP-1`, `DEP-1a`, `DEP-2`, `DEP-3` in
   `docs/specs/00-overview.md`, module-less by design and invisible to the matcher's
   module-coded assumption (`doc-id.py:3008-3009`). Filed as **F82**
   ([essay](../../findings/F82.md)), unowned.

(`_check_roadmap_not_silently_unrecognised` does **not** belong on this list — it runs only
inside `migrate()`'s zero-discovery `else` branch, which is not today's case; calling it
standalone, outside `migrate()`, raises on a real defect that `migrate()` itself would never
reach, and is not evidence of anything.)

This is the same reasoning the slice decision's §2.1 used to justify W37-5b's own existence
("a slice whose acceptance standard cannot pass is not a slice that should be authorised"),
now applying to a gap discovered one ruling later than the obligations list could see. It
does not retroactively fault this slice's own eighteen rows — it is disclosure for whoever
next asks for W37-6's go-ahead.

## 7. Other findings surfaced during this audit

- **F79** — `scripts/register-lint.py`'s `assert classified == seen` is exactly the
  count-comparison shape Ruling 83 rules against, not retrofit by this slice (disclosed in
  `d7c9b08`'s own body: *"deliberately not fixed... does not itself satisfy Ruling 83"*).
  **Carry forward, unowned.**
- **Row 6's guard finding (F81) and row 30's guard finding (F82)** are the same *kind* of
  gap as F80 — a new guard correctly catching a pre-existing defect outside its own row's
  job to fix — and are filed as their own findings/register rows (§6) rather than folded
  into rows 6/30's verdict cells, since each names a distinct file, defect and remedy.
- **The `owner:` field has no home for any document family** — surfaced resolving rows 6/7
  (`009cc8f`), partly addressed in code (`a31d509`), still open as an **RFC in draft**
  ([`2026-09-02-w37-rfc-bucket-c-owner-values.md`](../../../plans/2026-09-02-w37-rfc-bucket-c-owner-values.md),
  PR #613) awaiting the maintainer's accept-or-strike. Not this slice's to resolve.
- **Two hardcoded-owner bugs and a wrapped-heading title truncation**, found incidentally
  resolving row 6 and measuring row 15, fixed in `a31d509` (#603) — delivered and tested,
  not one of the original 39 rows.
- **PR count**: the dispatch said "seventeen" merged PRs. This audit counted **21** distinct
  PRs between the obligations list (`b648c22`, excluded) and `09b7e9b` (included): `#593`
  through `#613`, every number present. Not reconciled to seventeen; this audit could not
  determine which four the lower count excludes. Flagged rather than guessed at.

## 8. Owed list — generated, not recalled

```
$ python3 scripts/register-owed.py W37-5b
```

Generated against `471972b` (`audit/w37-5b-closure`), committed revision, per Ruling 52's
requirement that the script refuse a dirty worktree:

> 2 owed row(s), 1 matched but excluded as opening with a resolution marker (F76, correctly
> excluded — resolved in this PR, §4).
>
> - **F77** (work item `W37-6`, phase 2) — carry forward, unowned: the interpretation is
>   ruled (Ruling 94); implementation has no owner yet. *Reconciled above, §5a.*
> - **F80** (work item `W37-6`, phase 2) — not started: discovery code for the "Pending
>   proposals" `RFC-` draft. *Reconciled above, §6.*

Every id above appears in this record with a resolution. This table adds only what carries
no register row: rows 6's and 30's own guard findings (§7), and the two document-staleness
items (F76, the roadmap's own Progress clause — both resolved in this PR).

## 9. Gate, run at `3f41d60` (this PR's edits included)

Full `pytest -q` was **not** run, per instruction (concurrent full runs OOM'd the machine
earlier today; CI runs the identical command per-PR). Scoped to what this slice touched:

```
uv run ruff check .                                          → All checks passed
uv run mypy                                                   → Success: no issues found in 185 source files
uv run pytest tests/test_doc_id_migrate.py tests/test_doc_id.py \
    tests/test_template_headers.py tests/test_audit_docs_ids.py -q
                                                                → 302 passed in 14.15s
python3 scripts/audit-docs.py                                  → All checks passed (exit 0)
uv run python scripts/req-coverage.py                           → exit 0
python3 scripts/register-lint.py                                → OK (0 violations)
```

`register.md`'s residue line moved from "47 of 73" to "51 of 77" (four new rows) — disclosed
per Ruling 51, not a violation.

`audit-docs.py` failed once, honestly, during this audit's own drafting: a broken relative
link from this very file to `.claude/skills/close-workstream/SKILL.md`, undercounting the
`../` needed from `docs/audit/work/W37-5b/` to the repository root by one level — the
link-checker catching a defect in this record's own first draft, corrected above.

## 10. What this record does not do

- **Does not rule** row 36 (already ruled, Ruling 85) or the `owner:` RFC (the maintainer's).
- **Does not edit** any frozen plan.
- **Does not close W37** or claim the retrofit-impossible mapping — that is a Work-level
  close, not this Slice's.
- **Does not merge itself** — proposed to the lead, who adopts, amends or rejects
  (`CLAUDE.md` §13).

## 11. Recommendation

**Close W37-5b.** All eighteen group-A rows carry evidence or a discharged ruling; the gate
is green; the one commit-body inaccuracy found (`614c92c`, §3) does not point to an actual
gap in the delivered code; both named deferrals carry a verdict and a path to an owner (one
discharged by Ruling 94 mid-audit, one — F78 — still open for W37-6); one new, materially
important finding (F80, §6) shows the real migration cannot complete today for reasons
outside this slice's own scope, and is disclosure for the W37-6 go-ahead ask rather than a
reason to withhold this slice's own close. The one open item against the decision's own
Acceptance Standard (§1 item 1's "by number" wording) is corrected in this same PR. Sign-off
is the lead's, per `CLAUDE.md` §13 — a Slice closes on a clean audit and the lead's merge,
not the maintainer's acceptance.
