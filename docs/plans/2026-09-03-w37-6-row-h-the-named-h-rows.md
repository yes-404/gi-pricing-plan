# W37-6 row (h) — the named H rows, with the parser failure each one is named by (2026-09-03)

**Filed** 2026-09-03 by the executor. **What this is.** Ruling 102 §3 quotes the maintainer's
carve-out on row (h) and then says the naming is owed:

> **"Any H row without which `audit-docs.py` finds zero requirements lands with the run. Name
> them."**

Ruling 102 §3: *"which H rows those are is a list nobody has produced, and inventing it would
be the same relay failure decision 7 exists to stop. It is assigned, not assumed."* This is
that list. **Every row below was derived by running the migration on a disposable snapshot and
reading `audit-docs.py`'s own output on it** — not composed from `NT-0019` §5 by reading, and
not taken from any dispatch or summary.

## 1. The instrument, and the two trees every figure here is measured on

Two trees, one corpus:

| Tree | What it is |
|---|---|
| **control** | the un-migrated tree — `origin/main` as it stands, or this branch. Baseline figures below are at `4b9117a`; post-change figures at this branch rebased onto `2cb4808` |
| **migrated** | the same tree, `git archive`d into a temporary directory, `git init`ed, and `python3 scripts/doc-id.py migrate --repo-root .` run in it. **Never a real checkout.** |

Both figures for every row come from `python3 scripts/doc-id.py migrate --verify --ref <ref>`
(Ruling 102 §1's instrument, `scripts/_docverify.py`), run by the executor in
`gi-pricing-plan.local/wt-h`. The vacuity predicate is the instrument's own
`_docverify._VACUITY_PROBES`, row `h2`: *a probe whose migrated denominator is 0 while the
un-migrated control's is non-zero is a vacuous pass.*

**Why the failure count is the lesser half.** On the migrated tree the un-fixed
`audit-docs.py` exits 1 — but its *passing* lines read `0 requirements defined across 8
specs`, `0 open questions, all mirrored`, `journey citations: 0 endpoints, 0 functions, all
declared` and `0 of 0 §10 mirror rows carry their register status`. Nine of the ten checks in
the 30-39 family reported `1 governed document(s) checked in scope` over a corpus of ~460
stamped documents. **Fix every failure and the script would have exited 0 while measuring
nothing.** That is the state row (h) is vacuous in, and it is why the acceptance test here is
a **denominator**, never an exit code (`NT-0007`).

## 2. The named rows

A row is on this list when a named parser, root, glob or path constant **in
`scripts/audit-docs.py`** stops resolving on the migrated tree, and the summary line it feeds
therefore prints a zero. Each row is cited by symbol and by the line it sits on at `4b9117a`
(`origin/main` before this change).

### (1) `NT-0019` §5.5 — `audit-docs.py` · kind **H + M**

The row reads *"check 16 → front-matter parser; path roots → new directories; `_FINDING_ID` →
`FD-0*\d+`; requirement-id regexes → `(FR|NFR|DEP|OQ)-\d+`; per-module numbering check →
global uniqueness; … `check_notes_tombstone` → `check_redirects`; … new checks 30–39"*. Eight
distinct parser sites inside it fail, each with its own summary line:

| # | Symbol / site at `4b9117a` | What stops resolving | Summary line, control → migrated |
|---|---|---|---|
| 1a | `main()` line 2807, `re.finditer(r"\*\*((?:FR\|NFR)-[A-Z]+-\d+)\*\*", …)` | the spec form becomes `**FR-1187**` (D2); the module segment the pattern requires is gone | `533 requirements defined across 8 specs` → **`0`** |
| 1b | `main()` line 2830, the citation pattern `\b((?:FR\|NFR)-[A-Z]+-\d+)\b` | same | check 2 stops resolving every citation in `docs/`; 0 of them checked |
| 1c | `main()` lines 2849/2851 and `check_open_question_columns` / `check_open_question_mirror_status` (lines 236, 277, 305), `OQ-[A-Z]+-\d+` | `**OQ-816**` | `118 open questions` → **`0`**; `118 of 118 §10 mirror rows` → **`0 of 0`** |
| 1d | `main()` lines 2835-2843, the `by_prefix` per-module contiguity loop | ids come from **one global sequence** (D1), so `FR` gaps are not defects | would red on every correctly-numbered tree; the check has no meaning post-migration |
| 1e | `NOTES = REPO / "docs" / "notes"` (line 129), used by `check_notes` (430) and `check_finding_citations`'s `scan_dirs` (709) | the family becomes `RFC` under `docs/rfcs/` (D7) | hard failure *"docs/notes does not exist — checks 16-20 cannot run"*, plus check 25 silently loses its third scan root |
| 1f | `ROOT / "audit" / "register.md"` (lines 166 and 608), `(ROOT/"audit"/"phases").glob`, `(ROOT/"audit"/"work").glob`, `closure-records.md` | the registers merge into `docs/findings/register.md` and the closure records become `docs/closures/CR-*.md` | check 29 **skipped**; 20 × *"cites finding F<n>, which resolves nowhere"* |
| 1g | `ROOT.glob("workflows/wf-*.md")` (line 3117) | journeys become `WF-00979-*.md`; `glob` is case-sensitive on Linux | `journey citations: 31 endpoints, 8 functions` → **`0 endpoints, 0 functions, all declared`** |
| 1h | `_ID_SCOPE_ROOTS` (line 1029) | its own comment says *"WK-978-6 replaces it with the whole corpus in the same commit that migrates"* — D14, enforcement red from the migration PR | checks 30-39: `1 governed document(s) checked in scope` over ~460 stamped documents |

Two further defects were found **by** fixing the above, and are in the same row because the
same parser owns them:

- **`ADR-(\d{4})` (lines 2863/2865, and 418 inside `check_notes`)** reads the *first four*
  digits of a five-digit padded filename, so `ADR-00005` parsed as a citation of `ADR-0000`
  and check 5 failed with *"ADR-0000 referenced but no file exists"* — a real-looking failure
  manufactured entirely by the width of the pattern. Comparing **integers** is width-agnostic
  in both directions.
- **check 14's workflow-coverage** derived the module from `rid.split("-")[1]`, which
  post-migration is the *number*: coverage was reported per requirement — `356 100%, 357 0%,
  358 0%` — in ~450 buckets of one, with the 10% floor firing on individual requirements.
  The module now comes from the defining spec's own `**Module code:**` line. Its
  substring membership test (`rid in wf_text`) also matched `FR-DATA-1` inside `FR-DATA-12`;
  with a `\b` boundary the control tree's coverage figures drop (DATA 39%→33%, PLAT 18%→13%
  and so on). **This is the same token-boundary class Ruling 102 §2 row (g) names, present in
  `audit-docs.py` on the un-migrated tree today.**

### (2) `NT-0019` §5.5 — `req-coverage.py` · kind **H + M**

The row reads *"spec regex `\*\*(FR|NFR)-\d+\*\*`"*. `scripts/req-coverage.py:44` carries the
module-scoped pattern; on the migrated tree it matches nothing and the script dies at line 56
with `ZeroDivisionError: division by zero`. **§7(h) names `req-coverage.py` by name**, so this
row is inside (h) whatever view is taken of the carve-out's wording, and it is literally a
script that "finds zero requirements".

### (3) `NT-0019` §5.2 — `plans/2026-*.md (125) + README` · kind **M + H**, the **H** half

The row's H half is *"README: naming and four-kinds table → pointer"*. `check 28`
(`_PLAN_FILENAME_DATE`, line 891; `_PLAN_KIND_EXCLUDED_SUFFIXES`, line 890) takes a plan's
filing date and kind from its **filename**, and cites `docs/plans/README.md` §Naming as its
authority in the failure text. Post-migration a plan is `PL-<nnnnn>-<slug>.md`: the date and
the kind have moved into `created:` and `kind:` — which is what the migration is *for*.

Measured: **110 failures** (*"carries no `YYYY-MM-DD-` date prefix"*) **and**
`check 28: 0 plan(s) filed on/after 2026-08-31 checked for an acceptance standard` — wrong in
both directions at once over the same 114 files. `docs/plans/README.md` §Naming is the
document the check cites, so it changes in the same commit.

### (4) `NT-0019` §5.7 — the fixture tests · kind **H**

`tests/test_audit_docs_scan_roots.py` asserts on the literal source line
`NOTES = REPO / "docs" / "notes"` as a deliberate canary (*"the NOTES constant has moved —
re-derive this test before trusting it"*). Row (1e) moves it, so the canary fires and
`pytest tests/` — which §7(h) names — goes red. The canary is re-derived, not deleted: it now
pins the *definition line* whatever it names, and still refuses to run if the shape changes
again.

## 3. Rows considered and left off, with the reason

**Named here rather than silently dropped**, so the boundary is reviewable. Ruling 102 §3
confirms §7(i) — §5's H rows in general — is **W37-10's**; only the carve-out's subset is
W37-6's.

| Row | Kind | Why it is not on the list |
|---|---|---|
| §5.5 `scope-audit.py` | H + M | Its requirement-id regex does break on a migrated tree, but §7(h) does not name it and `audit-docs.py` never calls it. No summary line of `audit-docs.py` goes to zero without it. **W37-10.** |
| §5.5 `register-lint.py` / `register-owed.py` | H + M | Check 29's dependency. Its parser is **not** broken by the migration: once root (1f) is fixed it runs and reports **11 real grammar violations** — rows merged in from `docs/audit/phases/1b/register.md`, which was never held to RL-193's Decision-cell grammar. A wider population, not a blind parser. The 11 belong to whoever merges the two registers. **W37-10.** |
| §5.2 `process/delivery-process.core.json` (regenerated digest) | H + M | Check 27 reports the digest as stale on the migrated tree, which is **correct** — the migration rewrote `delivery-process.md` and did not re-pin the extract. A true failure from a working parser is not vacuity. Belongs to the migration script. |
| §5.5 `file-census.py`, `graphify-docs-extract.py` | H / H + M | Neither is called by `audit-docs.py` and neither is named by §7(h). **W37-10.** |
| §5.8 `.github/workflows/docs.yml` | H | CI path filter and steps. Not a parser; no denominator depends on it. **W37-10.** |
| §5.1 `CLAUDE.md`, §5.3 charters, §5.4 skills | H | Widening `_ID_SCOPE_ROOTS` (row 1h) does put `.claude/roles`, `.claude/skills` and `.claude/agents` in scope, and 92 files there are unstamped on the migrated tree. Those are **content** rows: the checks now *see* them, which is row (h)'s job; making them pass is W37-10's. |

## 4. What is still red on the migrated tree, and whose it is

After this change, `migrate --verify` reports **(h2) PASS** and **(h3) PASS**, and **(h1)
still FAIL**. The failure *count* goes **up**: `FAILED (552)` at `4b9117a`, `FAILED (12271)`
on this branch rebased onto `2cb4808` — that is the point. Roughly 11 700 defects that a
parser reading a path or an id form the migrated tree does not have could not report. The
residue is not (h)'s.

**The total moves with the tree** — every document added to `docs/` adds citations to check
and `main` gains several a day — so the taxonomy below is pinned to one tree and totals
**12 160** there, not to the branch tip.

**Taxonomy at `987c154`** (this record's own first commit; the predicate is
`sed -n '/^FAILED/,$p' <log> | grep '^  - ' | sed -E 's/^(check [0-9]+):.*/\1/; s/^broken link in .*/check 1/' | sort | uniq -c`):

| Class | Count | Owner |
|---|---|---|
| check 32 — a cited id does not resolve in `docs/INDEX.md`, or is padded in prose | 8 711 | the migration's citation rewriting — rows (d) and (g) |
| check 36 — a pre-migration form survives outside `REDIRECTS.csv` | 2 884 | same |
| check 1 — broken relative link (a moved file's link not rewritten) | 391 | same |
| check 35 — an unstamped file now in the enforced scope | 79 | W37-10 (§5.1, §5.3, §5.4 content rows) |
| check 30 — no front-matter header on a file now in scope | 77 | same |
| check 29 — merged phase-register rows failing RL-193's Decision-cell grammar | 11 | W37-10 (§5.2's register merge) |
| check 31 — id/filename disagreement | 2 | the migration |
| check 2 / check 5 — `FR-1187`, `ADR-1/2/3` cited illustratively in `document-ids.md` | 4 | a documents-defining-an-id-form case; W37-10 |
| check 27 — process-core digest not re-pinned after the migration rewrote its source | 1 | the migration script |

**Every one of these was invisible before this change**, because the parser that would have
reported it was reading a path or a form the migrated tree does not have.

## 5. One finding raised, not fixed here

`_docid.in_stamp_set` puts `docs/INDEX.md` and `docs/REDIRECTS.csv` — both **generated** by
the migration — and all thirteen `docs/_templates/*.md` into the checks-30-39 stamp set on a
migrated tree. The templates case contradicts `_id_scope_documents`'s own stated invariant
(*"never `_templates/` itself, which checks 30 and 37 read as a field-policy and shape
source"*, `NT-0019` §1.4, Ruling 70), which had only ever been enforced for the case where
`_templates/` was named as a root in its own right. **The templates exemption is applied by
path here**, because it implements a rule already written down. `INDEX.md` and `REDIRECTS.csv`
are **left in scope and left failing** rather than excluded by a rule nobody has ruled: that
is a stamp-set predicate question for W37-2's `_docid`, and inventing an exclusion is what
this whole row exists to stop.

## 6. The one thing that keeps `(h2)` red, and why it is not this row's

`(h2)` carries **two** clauses. The zero-denominator one — the carve-out's own words — is
cleared by this change on all six probes. A second clause, **OVER-EXEMPT**, was added to the
instrument after this work started (`2cb4808`) and fires here:

> *"OVER-EXEMPT: check 37 exempts 363 of 431 document(s) (84%) on the `was:` field, which is a
> large population almost entirely excused rather than an empty one — the zero-denominator
> rule cannot see this shape"*

**Widening the checks-30-39 scope is what makes that visible**, and the visibility is the
point: before this change check 37's population was `1`, so an 84% exemption rate had nothing
to be a rate *of*. But the exemption itself is not a parser defect. `check_shape` already keys
on the **parsed** `header.was` field, not on a substring — so Ruling 102 §5's *"the exemption
currently keys on a substring test"* does not describe this site. What is wrong is upstream:
Ruling 102 §5 measured that of 393 stamped documents carrying `was:`, **3** carry correct
provenance — 261 name the file's own new path and 129 name a path that never existed. **The
migration is writing the field wrongly**, and Ruling 96's verbatim-migration exemption is then
honoured over a field that does not mean what it says.

**Owner: not W37-6's row (h).** It is the migration's `was:` write path plus Ruling 102 §5's
re-measurement of condition 2. Raised here, deliberately not fixed here: fixing another row's
ruled defect inside this PR is the silent scope-widening the boundary in §3 exists to prevent.

## Acceptance Standard

This record is accepted when its PR merges. It binds nothing on its own; it discharges the
naming Ruling 102 §3 assigns and does not attempt.

**Its falsifiable claim, in one line:** run
`python3 scripts/doc-id.py migrate --verify --ref <the merge tree>` and rows **(h2)** and
**(h3)** reads **PASS**, and `(h2)`'s migrated denominators are non-zero on all **six**
probes — `(h2)`'s own verdict stays FAIL on its second, OVER-EXEMPT clause, which §6 shows is
not this row's. Measured on the branch at `c7302aa`, rebased onto `2cb4808`: `requirements defined=533; open questions=119; journey
endpoint citations=31; §10 mirror rows=119; check 37 documents in scope=431; check 37 was:
exemptions=363` — the first four are the corpus and are stable; the last two move with the
document count and are quoted for shape, not as constants.

Run the same command at `4b9117a` and `(h2)` reads **FAIL** — *"vacuous on: requirements
defined, open questions, journey endpoint citations, §10 mirror rows"*, all four migrated
denominators `0` against a non-zero control — and `(h3)` reads **FAIL**, *"empty population —
0 requirements on the migrated tree"*. **If either verdict is the same at both trees, this
record is wrong.**

**Implementation:** this PR. **Not discharged here:** §7(i) — every §5 H row closed by a named
commit — which Ruling 102 §3 assigns to W37-10.
