# Work-item record — W37-5b (the group-A preconditions slice)

Audited 2026-09-02 against `origin/main...09b7e9b` (PRs `#593`–`#599`, `#600`–`#614`, twenty-one
PRs merged between the obligations list, `b648c22`, and this audit's measurement tree).
`origin/main` advanced twice more during this audit, to `2eef65b` (#615) then `3f41d60` (#616) —
both skill/agent documentation only, no touch on `docs/plans/2026-09-0[12]-w37-*`, `scripts/doc-id.py`,
`scripts/_docid.py`, `scripts/doc-index.py`, `scripts/audit-docs.py` or their tests, confirmed by
`git diff --stat 09b7e9b..3f41d60`. Nothing below is measured at a tree the drift could have changed.

**Auditor's role note (`.claude/roles/auditor.md`):** this record proposes verdicts; it does not
issue them. **A Slice closes on a clean audit and the lead's merge** (`CLAUDE.md` §13) — no
maintainer acceptance line applies here.

## 0. Scope, derived from the decision record before any evidence was sought

[`docs/plans/2026-09-02-w37-5b-slice-decision.md`](../../../plans/2026-09-02-w37-5b-slice-decision.md)
§3 states group A as **eighteen rows: 1–15, 30, 31, 36**, against
[`2026-09-02-w37-6-outstanding-obligations.md`](../../../plans/2026-09-02-w37-6-outstanding-obligations.md)
§3's 39-row table. Verified by reading both documents directly rather than accepting the partition
from the dispatch: the decision's own count table (§3) reads `18 = 16 built + 1 lead + 1 routed`,
and the 39-row obligations table's Gate column marks exactly rows 1–15, 30, 31, 36 as gate **A**
("before" the migration run) — the same eighteen, cross-checked both directions.

**One title/body disagreement in the obligations list itself, immaterial to this audit's scope**:
`b648c22`'s commit subject reads "one list, **35** items"; its own body (line 117–118, wrapping
across a line break that a single-line grep misses) reads "of **39** obligations, none is closed."
The §3 table itself runs 1–39. The scope this audit used is the table's, not the title's; flagged
so the title is not read as authoritative if anyone re-derives scope from it later.

## 1. The slice decision's own Acceptance Standard, checked item by item

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1 | W37-5b named in the W37 row's `Progress` clause, scope stated **by number**, not as a row of its own | **Substantially met, one literal gap** | `docs/roadmap.md`'s W37 row (added by `01bd0bd`) reads: *"**W37-5b inserted 2026-09-02** by the lead's decision at `docs/plans/2026-09-02-w37-5b-slice-decision.md`... carries the pre-run preconditions: the four discovery defects, Ruling 83's census, Rulings 79/80's parser fix, Ruling 76's three-site `is_vendored` class, F76's unguarded `build_corpus` call, and the two silent discovery functions the guards never covered — sixteen items..."* No row is created (verified: `grep -c '\*\*W37-5b\*\*'` returns 0). **Gap**: the clause states a count ("sixteen items") and a narrative description, never the literal row numbers (`1–13, 15, 30, 31`) the acceptance item's own words ask for ("stated as the group-A rows **by number**"). The decision file it cites does carry the numbers, so the information is one hop away rather than absent, but the acceptance item's letter is not met verbatim. Recommend: either read this as satisfied (the citation makes the numbers recoverable, which is the acceptance item's stated purpose) or append the row range to the roadmap clause in a two-line follow-up — the lead's call, not this audit's. |
| 2 | Every group-A row has a named owner (agent, role, or explicit deferral) | **Met — 18 of 18** | §2 below. No row is silent; sixteen are delivered-and-tested, two are ruled carve-outs (14 to the lead, 36 to the decision-maker), both discharged. |
| 3 | A new dated leaf plan for W37-6 is filed, superseding `2026-09-02-w37-6-migration-run-leaf-plan.md` by name and date, carrying Ruling 73's amendment in its own text | **Met** | [`2026-09-02-w37-6-migration-run-leaf-plan-v2.md`](../../../plans/2026-09-02-w37-6-migration-run-leaf-plan-v2.md), filed draft by `958cb7d`, lifted to `status: active` by `f9975f1` once Ruling 88 resolved its one blocking row. Its own header: *"Supersedes: [`2026-09-02-w37-6-migration-run-leaf-plan.md`]... which is frozen at its date and is not edited."* Item 11 is restated in full inline (not by reference), carrying Ruling 73's three-limb amendment. The frozen original is confirmed untouched: `git diff --stat b648c22..09b7e9b -- docs/plans/2026-09-02-w37-6-migration-run-leaf-plan.md` is empty. |
| 4 | This record cites the decision where W37-5b's close is recorded | **Met, by this document** | The roadmap's `Progress` clause already cites the decision file (item 1 above); this closure record cites both the decision (§0) and, by being filed, satisfies the "Work-level closure record" half for whenever W37 itself closes. |

## 2. Every group-A row, evidence or verdict

Verified independently at `09b7e9b` — commands re-run by this audit, not the PR bodies' word taken
for it (`CLAUDE.md` §13 rule 2). "Confirmed independently" below means this audit executed the
cited command itself, distinct from reading the test that also asserts it.

| Row | What it was | PR(s) | Verdict | Independent confirmation |
|---|---|---|---|---|
| 1 | Plan-reviews under-discovery (10 of 14, trailing-text anchor) | `4367cf7` (#602) | **Delivered, tested** | `_REVIEW_HEADING_RE` now `r"^###\s+(.+?),\s*(\d{4}-\d{2}-\d{2})(.*)$"` (`doc-id.py:1326`), captured trailing group confirmed by direct read. |
| 2 | `_discover_roadmap` converts 0 of 41 works, reports success | `4cbfa62` (#610) | **Delivered, tested** | Ran `_discover_roadmap(ROOT)` directly against the real tree: **41** works, phase split 7/5/14/8/7 = 41, matching the commit body exactly. |
| 3 | `_discover_register` matches 0 of 73 rows | `4cbfa62` (#610) | **Delivered, tested** | Ran `_discover_register(ROOT)` directly: **73** rows. |
| 4 | Ten `W5 —` closure headings raise on the first, stopping the run | `614c92c` (#599) | **Delivered, tested — see §3 for a correction to this commit's own body** | Independently counted `docs/audit/closure-records.md`'s real `###` headings: **21** total, reconciling to 8 `CR-work` + 1 `CR-phase` + 2 `RS-audit` + 10 `LG-` (the ten "W5 —" headings without a clean top-level closure, plus the one `W5 — Modelling: closed` heading folding into the 8). `test_closure_records_real_corpus_decomposes_into_ruling_84s_four_buckets` asserts the same breakdown against `ROOT`; ran narrowly (`pytest tests/test_doc_id_migrate.py -k closure_records -q`) — 10 passed. |
| 5 | Zero-drafts guards catch total silence, not undercount | `d7c9b08` (#608), `4367cf7` (#602) | **Delivered, tested** | `_reconcile_census` (`doc-id.py:2225`) refuses by naming every unmatched unit; read its body directly — a three-bucket (record / derived body / declared exception) reconciliation, not a count comparison. Positive control read directly in `d7c9b08`'s own body: "27 failed... 189 passed after." |
| 6 | `Ruling A1`–`A3`: family undetermined, blocking the census | derivation `04f47b2` (#595), ruled `cc17404` (#598, Ruling 86) | **Ruled — three `RL-` records, not yet coded (correct: coding happens at the real W37-6 run)** | Ruling 86 adopts three `RL-` records, verified independently against a ruling record that cites `Ruling A2` as precedent (line 237 of the W11 reopen-rulings record) — a citation form only a ruling can receive under §1.7. |
| 7 | "Pending proposals" container: family undetermined | derivation `44ec54e` (#597), ruled `f4cbbb7` (#601, Ruling 88), amended `22d8d64` (#612, Ruling 93) | **Ruled — `RFC-`, `kind: process`, `owner: maintainer`; fixture amended after row 14's own fix invalidated it** | `docs/audit/plan-reviews.md` independently re-counted: **0** level-2 headings, **12** level-3, **28** level-4 — matches Ruling 93's replacement fixture requirement (no level-2 headings left to key off) and the superseding leaf plan §6.1's "eleven `CR- kind: review` plus one `RFC-`" decomposition. |
| 8 | `_ROW_FIELDS` hardcoded and wrong both directions; `scan_phase_sections` unbounded lookahead | `e7e1d24` (#593) | **Delivered, tested** | `row_template_fields` (`_docid.py`) confirmed deriving the field set per family from the real template files, not a hardcoded frozenset — read directly. |
| 9 | `is_vendored` keys on `LICENSE`, exempting 2 of 28 | `574d536` (#611) | **Delivered, tested** | `_VENDORED_SKILLS` (`_docid.py:330`): counted **28** entries directly. `vendored_skills_ruff_exclude_mismatch(Path('.'))` run live: `(frozenset(), frozenset())` — zero mismatch either direction against `pyproject.toml`'s ruff exclude list. |
| 10 | `REFERENCE.md` still teaches the rejected criterion | `574d536` (#611) | **Delivered** | Read `docs/_templates/REFERENCE.md:39-49` directly: now states "a hand-kept list, not a filesystem property... Ruling 69 rejected that detection rule." |
| 11 | Five tests pin the rejected criterion | `574d536` (#611) | **Delivered, tested** | `tests/test_doc_id.py:372+` now monkeypatches `_VENDORED_SKILLS` for membership tests, no `LICENSE` inspection — read directly. |
| 12 | F76 — check 39's uncaught `HeaderError` silently drops six later checks | `35c1488` (#607) | **Delivered, tested** | `check_index_stable` (`audit-docs.py:2196`) now wraps `build_corpus` in `try/except (_doc_index.HeaderError, ValueError)`, with a docstring explaining the `_docid.HeaderError is _doc_index.HeaderError → False` module-identity trap. Register row F76 updated to **Resolved** (§4). |
| 13 | No check feeds a template's own example block to its consuming parser | `e7e1d24` (#593) | **Delivered, tested** | `tests/test_template_headers.py::test_document_template_parses_to_its_family_once_filled_in` and `::test_row_template_fenced_block_parses_through_doc_index_row_parser` exist and pass. |
| 14 | `plan-reviews.md` heading mis-nesting (carve-out — the lead's) | `2fbce0c` (#609) | **Delivered by the lead** | Structural fix confirmed (§7 above: 0/12/28 heading counts). |
| 15 | Does the multi-ruling splitter try to split the three h1 ruling files? | measured in `a31d509` (#603), `d7c9b08` (#608) | **Measured — no** | Ran `_discover_multi_ruling_files(ROOT)` directly: 35 source files touched, **none** of the three named h1 files (`2026-09-01-nt-0016-slice2-fr-data-32-ruling.md`, `2026-09-01-ruling-60-census-provenance-checkout-depth.md`, `2026-09-01-ruling-61-notes-tombstone-stubs-watched.md`) among them. Third independent confirmation of the same answer (two prior, by different methods, per `d7c9b08`'s own body). |
| 30 | `_discover_requirements`: no guard at all | `d7c9b08` (#608) | **Delivered, tested** | `_reconcile_census` call site at `doc-id.py:2559` confirmed by direct read. |
| 31 | Four more discovery functions silent by construction | `d7c9b08` (#608) | **Delivered, tested** | Confirmed all four remaining `_reconcile_census` call sites (`:2354` shared with row 4/7, `:2506`, `:2598`, `:2634` shared by both `_discover_notes`/`_discover_adrs` skip paths) by direct read — five call-site total matches "wired to five call sites" claim exactly. |
| 36 | §8-vs-Ruling-66 stage-boundary conflict (carve-out — routed) | derivation none needed, ruled `e74a683` (#596, Ruling 85) | **Ruled — reading 1: §8 is sequencing, not part of the accepted standard; Ruling 66 stands unamended** | Read Ruling 85 in full; its verdict rests on `docs/process/document-ids.md` (the maintainer-owned standard) lifting only §1.1–§1.13, never §4/§5/§7/§8 — confirmed the document's own title, "NT-0019 §1, lifted verbatim," by direct read. |

**Result: 18 of 18 group-A rows carry evidence or a discharged ruling. None is silent.** Sixteen
are code-delivered and test-covered; two (14, 36) are carve-out rulings/fixes outside an executor's
build, both discharged.

## 3. The `614c92c` correction — verify before writing either

The lead flagged that `614c92c`'s commit body states the closure-records census gap is open and
carried as a follow-up, and that the census in fact landed in the same commit. **Confirmed, with
one refinement the lead's framing did not carry.**

`614c92c`'s own commit body says, of two disclosed gaps: *"The census does not reach this file...
none of the census call sites covers closure-records.md... It is not closed here... Carried as a
named W37-5b row with an owner rather than left to be rediscovered."*

This is **false as a claim about the commit's own diff**. `git show 614c92c -- scripts/doc-id.py`
shows `+def _check_closure_records_not_silently_unrecognised(root: Path) -> None:` added in that
same commit (now at `doc-id.py:2384`), wired into `migrate()` at `:2990`, immediately after
`_discover_closure_records` runs. Its own docstring states plainly that it exists **because** the
general five-site census (from `d7c9b08`, merged 30 minutes earlier the same day) does not reach
this file's bespoke discovery loop, and reuses `_check_heading_split_not_silently_unrecognised` —
the same `_reconcile_census`-backed mechanism — to close exactly that gap for this one file.

Independently re-verified, not merely read:

- `test_closure_records_census_names_an_undercounted_heading` constructs a `###` heading with no
  date, asserts `NotImplementedError` naming it — ran narrowly, **passes**.
- `test_closure_records_census_is_silent_on_a_clean_file`, `..._treats_a_nested_subheading_as_body`,
  `..._is_silent_on_a_missing_file`, and `test_migrate_raises_via_the_closure_records_census_on_a_real_shaped_tree`
  all exist and pass — a genuine positive and negative control pair, not a check that has never
  printed a failure.
- Independently counted the real `docs/audit/closure-records.md`: 21 `###` headings, reconciling
  exactly to the claimed 8+1+2+10 split (§2 row 4 above).

**No register row exists anywhere for "the census does not reach closure-records.md"** (`grep -rn`
across `docs/audit/` and `docs/`), consistent with the gap being false rather than merely
unrecorded — there was nothing to carry forward.

**What was accurate in `614c92c`'s body**: its *second* disclosed gap — Ruling 84 §4's `slice:`
acceptance item being vacuously true — is correct, and is §5 below.

**Recommendation**: cite `614c92c` by hash wherever this correction is recorded (per the
maintainer's instruction relayed by the lead), rather than editing the commit body, which cannot
be amended after a squash-merge without a force-push `main-protection` forbids.

## 4. Register update — F76 resolved

`docs/audit/register.md`'s F76 row ("an uncaught `HeaderError` in check 39 silently drops six
later checks") predates this slice and named `W37-6` as owner via Ruling 79. Row 12's fix
(`35c1488`) discharges it in full: the guard exists, both crash paths (`_doc_index.HeaderError`
and a non-ISO `created:` `ValueError`) are caught, and the six-checks-survive property is proven
on broken input in `tests/test_audit_docs_ids.py`. **Annotated in place** (per this file's own
convention) as **Resolved 2026-09-02**, original verdict text kept below it rather than deleted.

## 5. The two named deferrals

### 5a. Ruling 84 §4's second acceptance item (`slice:` vacuity) — RULED mid-audit

Filed as register row **F77**
([essay](../../findings/F77.md)). Verified independently (§3 above and directly: `_stamp_header`'s
`elif key in ("slice", "deliverable", "lands_in", "trigger"): continue` at `doc-id.py:946` — no
`slice` parameter exists in the function's signature at all, so no caller can write it).

**This deferral was ruled while this audit was in progress.** `origin/main` fast-forwarded onto
`09b7e9b` (Ruling 94, PR #614) mid-session. Ruling 94 holds: *"an acceptance item that is
vacuously true does not satisfy itself"* (citing `CLAUDE.md` §13's "a check that has never printed
a failure has not been tested"), rejects narrowing the invariant (which would wrongly red the
first time a ledger legitimately carries `slice:`, since Ruling 84 §3 item 5 keeps it permitted
for every other ledger), and specifies a **substitute** instrument: count the `slice:` values on
emitted `LG-` records, require each to resolve, print the count, reddening on a **one-line
mutation of `_stamp_header`** rather than a fixture document.

Ruling 94 also names and corrects a stale-tree quotation error in an earlier version of the lead's
own report (the skip tuple misquoted as containing `phase`, `work` and `slice`, read from a
checkout still at `2fbce0c` rather than `614c92c`, which split `phase`/`work` into their own
resolving branches). **Neither this audit's own direct read (via `git show d47a5f5:scripts/doc-id.py`,
pinned, not a bare working-tree grep) nor this audit's fork essay (F77.md) repeated that error** —
both independently quoted the tuple correctly before Ruling 94 was written.

**What Ruling 94 leaves open, verified directly at `09b7e9b`**: neither the substituted
count-and-print check nor an equivalent guard for §4's *third* item ("`work:` resolves"; violation:
a ledger with neither axis) is implemented yet — `git diff --stat` for PR #614 touches exactly one
file, the ruling record. Item 3's resolution is confirmed *live and correct* on today's real corpus
(`_discover_roadmap`'s one `W5` draft, phase `P1b`, matches all ten real `LG-` drafts' `work_token`
— re-verified directly by this audit), but no guard exists that would catch a future regression,
and the existing unit test explicitly documents silent omission on an unresolved token as
intentional — correct for today, not a proof against tomorrow.

**Proposed verdict**: the interpretation question is **discharged by Ruling 94**, cited rather
than carried forward. The remaining implementation (the count-and-print check, and a "neither
axis" guard for item 3) is **not started**, owner **W37-6** — register row F77 updated
accordingly rather than left at its pre-ruling text.

### 5b. `#610`'s phase-spanning refusal — genuinely open, owner W37-6

Filed as register row **F78** ([essay](../../findings/F78.md)). `4cbfa62`'s own body: *"Disclosed
and not built: no fixture exercises the phase-spanning refusal... the gap is named as a follow-up
rather than the row being called done."* Confirmed independently: the refusal code exists
(`doc-id.py:1917-1925`, `unresolved_phase` → `NotImplementedError`), `grep -n "unresolved_phase\|phase_uncertain"` over `tests/test_doc_id_migrate.py` returns nothing, and running `_discover_roadmap(ROOT)` against the real tree confirms the branch is not entered today (all 41 works resolve to exactly one phase each).

**Proposed verdict**: **deferred with an owner — W37-6**, discharge is a fixture forcing two
leading rows of one work id into different phase sections and asserting the raise names both.

## 6. Findings surfaced during this audit, not in the original 39 rows

- **F79** — `scripts/register-lint.py`'s `assert classified == seen` is exactly the
  count-comparison shape Ruling 83 rules against, and was not retrofit by this slice (disclosed in
  `d7c9b08`'s own body: *"deliberately not fixed... does not itself satisfy Ruling 83"*).
  **Carry forward, unowned** — narrow fix, but touches a script wired into the gate as check 29.
- **The `owner:` field has no home for any document family** — surfaced resolving rows 6/7
  (`009cc8f`), partly addressed in code (`a31d509`, deriving ruling/plan owner rather than
  hardcoding it), and still open as an **RFC in draft**
  ([`2026-09-02-w37-rfc-bucket-c-owner-values.md`](../../../plans/2026-09-02-w37-rfc-bucket-c-owner-values.md),
  PR #613) awaiting the maintainer's accept-or-strike per §1.6's own RFC row. Confirmed still
  `draft`/undecided by direct read of the file's own framing note. Not this slice's to resolve —
  named so it is not mistaken for silence.
- **Two hardcoded-owner bugs and a wrapped-heading title truncation**, found incidentally while
  resolving row 6 and measuring row 15, fixed in `a31d509` (#603) — not one of the original 39
  rows, delivered and tested (`_ruling_file_owner`, `_PLAN_KIND_OWNER`, and the wrapped-title join
  fix all confirmed present with passing tests).
- **PR count**: the lead's dispatch said "seventeen" merged PRs. This audit counted **21** distinct
  PRs between the obligations list (`b648c22`, excluded) and this audit's tree (`09b7e9b`,
  included): `#593`–`#613` less none — every number in that range is present. Re-derived per the
  standing instruction to re-derive every figure; not reconciled to seventeen, and this audit could
  not determine which four the lower count excludes. Flagged rather than guessed at.

## 7. Gate, run at `09b7e9b` (register.md edits included)

Full `pytest -q` was **not** run, per instruction (concurrent full runs OOM'd the machine earlier
today; CI already runs it per-PR). Scoped to what this slice touched:

```
uv run ruff check .                                        → All checks passed
uv run mypy                                                 → Success: no issues found in 185 source files
uv run pytest tests/test_doc_id_migrate.py tests/test_doc_id.py \
    tests/test_template_headers.py tests/test_audit_docs_ids.py -q
                                                              → 302 passed in 14.15s
python3 scripts/audit-docs.py                                → All checks passed (exit 0)
uv run python scripts/req-coverage.py                        → exit 0
python3 scripts/register-lint.py                             → OK (0 violations)
```

`register.md`'s residue line moved from "47 of 73" to "50 of 76" (three new rows, two of them long)
— disclosed per Ruling 51, not a violation.

## 8. What this record does not do

- **Does not rule** row 36 (already ruled, Ruling 85) or the `owner:` RFC (still the maintainer's).
- **Does not edit** any frozen plan.
- **Does not close W37** or claim the retrofit-impossible mapping — that is a Work-level close,
  not this Slice's.
- **Does not merge itself** — proposed to the lead, who adopts, amends or rejects (`CLAUDE.md` §13).

## 9. Recommendation

**Close W37-5b.** All eighteen group-A rows carry evidence or a discharged ruling; the gate is
green; the one commit-body inaccuracy found (`614c92c`, §3) does not point to an actual gap in the
delivered code; both named deferrals now carry a verdict and an owner (one discharged by Ruling 94
mid-audit, one — F78 — still genuinely open for W37-6); three incidental findings (F79, the
`owner:` RFC, the PR-count mismatch) are named rather than left silent. The one open item against
the decision's own Acceptance Standard (§1 item 1's "by number" wording) is cosmetic and does not,
in this audit's judgement, block the close — but is the lead's call, not this audit's, per the same
standard's own §12 reservation.
