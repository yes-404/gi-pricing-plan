# Ruling acceptance-item sweep — audit record

| | |
|---|---|
| **Date** | 2026-09-02 |
| **Auditor** | this session, dispatched by the lead to sweep every filed ruling's acceptance item after Ruling 94 routed it |
| **Pin** | `5c0d24df5ce4b58411eb0e67bf7cc2b91a44a3ca` throughout §§1-6 below; one explicit, dated post-sweep note in §3 re-checks a later tip (`2e48960`) and says so |
| **Corrects** | [Ruling 93](../plans/2026-09-02-w37-ruling-88-acceptance-amendment.md) ("twelve ruling records now carry acceptance items") and [Ruling 94](../plans/2026-09-02-w37-vacuous-acceptance-item-ruling.md) ("Fourteen ruling records now carry acceptance items") — both figures were asserted in the paragraph that routed this sweep, not independently derived. §6 states the growth-versus-undercount split per figure. Neither ruling is edited; this record is filed alongside them, findable from a `corrects:`-shaped cross-reference in the same spirit as the `614c92c` correction (`CLAUDE.md` §15). |
| **Why this exists** | `docs/plans/README.md`'s own documented trap — a heading-only sweep misses an addendum filed under a prose heading — and this repo's history of a stale count surviving because "nobody re-derives from a subagent's session" (the lead's words routing this record's filing). Filed so the count is re-runnable rather than trusted. |
| **Scope** | Every ruling heading under `docs/plans/` matching `^#{1,3} Ruling (\d+\|A\d+)( —\|'s)`: 98 rulings (1-95 contiguous, no gaps or duplicates once the one title false-positive is excluded, + A1-A3), across 41 ruling-record files. |

## 1. Method — exact searches, not descriptions

Enumeration (every command below was run against `docs/plans/`, from the repo root):

```
grep -rlE "^#{1,3} Ruling ([0-9]+|A[0-9]+)( —|'s)" docs/plans/
grep -rhoE "^#{1,3} Ruling [0-9]+( —|'s)" docs/plans/ | grep -oE "[0-9]+" | sort -n | uniq -c
grep -rn "^#\+ .*Acceptance.*violation that must become detectable" docs/plans/
grep -rn "violation that must become expressible" docs/plans/ docs/research/
grep -rn "Acceptance test" docs/plans/ docs/research/
grep -rnE "^#{1,4}\s+.*\bRuling\s+[0-9A-Z]+\b" docs/plans/ | grep -vE "^\S+:[0-9]+:#{1,3} Ruling [0-9]+( —|'s)"
grep -n -i "violation\|must fail\|must red\|the check is\|testable definition" <each file with zero hits from the above>
```

The last command's output was read in full for every file it touched — a hit is a candidate,
never a reading (`docs/skills-map.md`-adjacent house rule, applied here to acceptance items
rather than to citations). The standalone-file convention (`## N. Broken-input proof`, Rulings
59-61) and Ruling 44's own phrasing ("Two tests, each stated as a violation that must become
impossible:", no "accept" substring anywhere) were found only by reading full ruling bodies —
no keyword distinguishes either from the other conventions or from ordinary prose.

**"Genuine" acceptance item, defined** — the adjective doing the work in "31 files carry a
genuine item," and the one a challenge would target: an item counts only if it sits inside
that specific ruling's own numbered section (never the file-level `## Acceptance Standard`
check-28 boilerplate, never a citation of a *different* ruling's item, never a governance
sign-off table) **and** states or names a violation/failure condition tied to that ruling's own
substance. It does not count merely because code elsewhere happens to satisfy it — an item is
only as genuine as the ruling's own stated check, not as the ruling's own subject matter.
Rulings 52 and 53 (§2) are the corpus's own worked counterexample: real, enforced code exists
for both, and neither ruling states a check.

**Rule for the next sweep, stated because it will otherwise be re-derived from scratch every
time:** an **"Overridden if `<X>`"** clause is near-universal across this repo's ruling
convention (confirmed present on Rulings 14, 15, 20, 26, 29, 39, 44-53, 55-58, 62-65 — a
formulaic template, not an exception) and **never itself constitutes an acceptance item**. It
states a hypothetical future condition in plain prose and names no check, script, or
procedure. Only a **separately and explicitly labelled acceptance sentence** counts — contrast
Ruling 47, self-titled "The acceptance test, stated as the violation that must become
impossible," against Rulings 55-58, which have an override clause and nothing else. Two of
this sweep's own rows (Rulings 55-58, and independently 52/53) were first mis-admitted on the
looser reading and corrected after a second, dedicated read of their source files.

**A last note on this section's own drafting.** `python3 scripts/audit-docs.py` caught two
defects in this record's own first draft, before it was ever committed: two relative links to
Rulings 93 and 94 missing the `../plans/` prefix required from `docs/audit/`, and an unescaped
literal `|` inside a regex shown in the Scope row's table cell — which had silently shifted
that row's own column count — fixed per `docs/plans/README.md`'s documented `\|`-in-a-table-
cell convention (visible in the Scope row above, as filed). Both are exactly the class of
defect the check exists to catch, caught on the document that documents the check. Recorded
because it is evidence that the gate ran on this artifact, not because it is remarkable.

## 2. The classifier — `scripts/ruling-acceptance-item-census.py`

Implements the enumeration half of this sweep as a re-runnable script, carrying Ruling 83's
property (`docs/plans/2026-09-02-w37-guard-arithmetic-and-ledger-family-rulings.md`): **every
candidate heading falls into exactly one bucket, and the buckets sum to the total.** Run:

```
python3 scripts/ruling-acceptance-item-census.py
```

At this record's pin:

| Bucket | Count | How found |
|---|---|---|
| `w37` | 30 | regex: `### N. Acceptance — the violation that must become detectable` |
| `w11` | 20 | regex: bold `**Acceptance test` inline marker |
| `standalone` | 2 | regex: `## N. Broken-input proof` heading (Rulings 59, 61 — **not** 60, see below) |
| `exception` | 1 | Ruling 44, hand-verified, named because a regex fitted to one sentence would not generalise |
| `prose_only` | 10 | **hand-verified, not regex-derived** — Rulings 40, 42, 43, 45, 46, 47, 50, 51, 54, 60 |
| `none` | 35 | no marker of any kind found |
| **total** | **98** | |

**The honest limit of this tool, stated rather than hidden.** The "three conventions plus
Ruling 44" framing this sweep was asked to commit understates the corpus by ten rulings. Each
of the ten states a genuine, testable check in ordinary prose with **no shared marker** —
"§13's broken-input proof:", "Its acceptance evidence is...", "so this is testable rather than
hortatory," and (Ruling 60, its own sub-case) a re-confirmation of a **different, named**
ruling's broken-input cases rather than a fresh statement of its own. No regex loose enough to
catch all ten avoids also matching ordinary prose that is not an acceptance item — the
`prose_only` set is therefore a committed, hand-verified list, not a derived one, and it is the
one bucket where this module's own promise ("the arithmetic catches an undercount") does not
hold: a future ruling using this same marker-free style lands silently in `none`, not in a
bucket whose count visibly moved. Any addition to `_PROSE_ONLY_RULINGS` must cite the reading
that found it, in the commit that adds it — the same discipline `_NAMED_EXCEPTIONS` already
carries for Ruling 44.

**Not this record's to decide, and not implemented:** whether a *future* ruling must use one of
the three conventions. `docs/_templates/RL.md` is a frozen template edit, `CLAUDE.md` §2 forbids
editing a filed plan to conform, and the choice is the maintainer's. **Recommendation:** require
the W37-series form (`### N. Acceptance — the violation that must become detectable`) going
forward — it is the only one of the three that is both fully regex-derivable *and* already
paired with a structural convention (`### N. Verified first` / `### N. Ruled` / `### N. What it
obliges` preceding it) that gives every ruling a predictable place to state one. This does not
touch the 65 already-filed rulings using another form or none.

## 3. Defective items — full proofs

Five items across five rulings needed more than CONSTRUCTIBLE. The CSV (`ruling-acceptance-
item-sweep-5c0d24d.csv`, same directory) carries the remaining 93.

**Ruling 84 §4 item 2 (VACUOUS AT BIRTH) — REPLACE shape.** Original text: *"A check that no
emitted `LG-` carries a `slice:` whose value resolves to no roadmap row."* `scripts/doc-id.py:946`
(`_stamp_header`): `elif key in ("slice", "deliverable", "lands_in", "trigger"): continue` — an
unconditional skip for every caller, and the function's signature carries no `slice` parameter
at all. No code path in `migrate()` can ever write a `slice:` value onto an emitted `LG-`
record, so the check can never see the fixture it names. Register **F77**. Ruled by Ruling 94
(substitution: count-and-print + a `_stamp_header`-mutation broken-input test) — the item
checked a positive obligation its own ruling imposed and the code never attempted, so it had to
be **replaced**, and was. As of this pin, the substitute is designed but **not yet built**: no
commit had touched `scripts/doc-id.py` or `tests/test_doc_id_migrate.py` for this purpose since
`09b7e9b`.

**Ruling 88 §4 item 2 (INVALIDATED).** Original text named "a fixture whose only level-2
heading is followed by three record headings" in `docs/audit/plan-reviews.md`. Was constructible
when written — Ruling 88 measured "exactly one level-2 heading" at its own pin. PR #609
(`2fbce0c`, confirmed an ancestor of this record's pin) demoted that heading to level-3;
`grep -c '^## ' docs/audit/plan-reviews.md` returns **0** at this pin. The fixture the item names
cannot be built the way it is stated. Rebuilt by Ruling 93 on a property (shared heading level
with no higher level anywhere in the file) rather than a specific level number.

**Ruling 61 (INVALIDATED) — documented, deliberate trade, not a silent accident.** §4
("Broken-input proof") required `check_notes_tombstone()` to red on two named broken-input
cases — a stray file in the old notes root under `.claude`, and an edited stub body. `grep -c "def
check_notes_tombstone" scripts/audit-docs.py` returns **0**. The module's own docstring
(`scripts/audit-docs.py:55-64`) names the resolution: NT-0019 §5.5 gave slot 30 to its own
header-field check (`check_header_fields`) and resolved the collision by replacing
`check_notes_tombstone` rather than renumbering either — *"`check_notes_tombstone`'s protective
job over the tombstone stubs ends with this commit, by that same resolution, **until W37-6
deletes the stubs entirely**."* The successor, `check_redirects` (slot 36), watches
`docs/REDIRECTS.csv`, not the old notes root under `.claude`. So: today, neither of Ruling 61's two named
fixtures is caught by anything in the gate — constructible and passing when written,
invalidated by a later, recorded, and bounded resolution (its own stated horizon is W37-6),
not a silent regression.

**Ruling 86 §4 item 3 (INVALIDATED) — confirmed by a later commit, not merely by a later
ruling.** Original text: *"Each of the three new `RL-` records carries an `owner:` that is not
`decision-maker`."* Ruling 95 (`7082c38`/#618, landed during this sweep) reversed the decision
this item encoded, ruling `owner: decision-maker` for the A-series. At this record's pin, the
code had not yet caught up (the departure machinery was "still live... its removal in flight,"
per the go-ahead ask). **Post-sweep, at `2e48960`/#620 (merged after this record's pin, checked
separately and dated here rather than silently folded in):** `_ruling_file_owner`
(`scripts/doc-id.py:1142`) now unconditionally returns `_RULING_DEFAULT_OWNER` for every input
— the departure regexes are deleted, not left inert. Ruling 86 item 3's assertion (`owner ≠
decision-maker`) now fails on *every* input, by construction, exactly as the invalidation
predicted before the fix landed. **This is the strongest form the proof can take: a structural
prediction, made before the code changed, confirmed by an independent later change made for an
unrelated reason (implementing Ruling 95's own obligation, not this record's finding).** A
prediction later confirmed by an independent event is stronger evidence than either the
prediction or the confirmation would be alone.

**Ruling 95 §3 item 3 / §4 item 3 (VACUOUS AT BIRTH) — RE-INSTRUMENT shape, distinct from
Ruling 84's.** §4 item 3: *"Ruling 87's `decision-maker` for the three standalone ruling files
still holds after this amendment."* At this pin: `_discover_plain_plans` uses
`owner=_PLAN_KIND_OWNER[kind]`, and `_PLAN_KIND_OWNER["leaf"] == "planner"` — no code path
anywhere emitted `decision-maker` for those three files (verified: zero hits). This is a
**non-interference claim** — did Ruling 95's own diff disturb territory it deliberately left
alone — whose **property holds** (nothing was disturbed, because nothing implementing Ruling
87 existed yet to disturb) while its **stated instrument has nothing to observe**. Distinct
from Ruling 84's shape: Ruling 84 checked a positive obligation the code never attempted
(replace); this checks a negative one whose target has no positive case yet to falsify against
(re-instrument). **Post-sweep, at `2e48960`/#620:** re-instrumented, not merely noted —
`test_ruling_87_standalone_files_are_untouched_by_this_amendment` now pins the three files
resolving through `_discover_plain_plans` with `owner="planner"` (documented as known-wrong,
not blessed) and `_discover_multi_ruling_files` matching none of them, proven non-vacuous by
two independent mutations (`_PLAN_KIND_OWNER["leaf"]` and `_RULING_HEADING_RE`).

## 4. Withdrawn — a shape neither VACUOUS nor INVALIDATED

Two items fire constantly and return the **wrong verdict** — false positives and false
negatives together — rather than never firing. Folded into CONSTRUCTIBLE in §5's tally (their
replacements are genuine, buildable checks) but named here because the six-class taxonomy this
sweep was asked to use has no slot for "tests, but proves the wrong thing":

- **Ruling 66 acceptance item 2** (original, reversion-based), withdrawn by Ruling 73: measured
  against the shipped `sweep_legacy_forms` on the real corpus, false positives on 8 non-members
  (including `repo-architecture`, `git-hygiene`), false negatives on 4 real members (including
  `subagent-driven-development`, a primary instrument), and no under-inclusion limb at all.
- **Ruling 16 acceptance item 1**, withdrawn via a same-day cross-file correction filed under a
  non-canonical heading in a *different* file — `docs/plans/2026-08-29-w11-algorithm-pin-
  maturity.md:124`, "## Correction to Ruling 16, discharging register row F32" — exactly the
  addendum trap `docs/plans/README.md` §"enumerate the rulings by diffing the record" warns a
  heading-only sweep misses. Register **F32**, confirmed verbatim: *"Only Ruling 16's
  acceptance item 1 is withdrawn; item 2 (the degraded read) stands."*

**Forward pointer, added 2026-09-02 alongside §11.** This section names the shape; §11 is
where it is dated and given a name — the seventh class, `WITHDRAWN`, on the maintainer's
ruling of 2026-09-02. The observation here precedes its own classification there.

## 5. Class counts

Mechanically verified against the CSV (`cut -d, -f3 ruling-acceptance-item-sweep-5c0d24d.csv |
sort | uniq -c`), not hand-totalled:

| Class | Count |
|---|---|
| CONSTRUCTIBLE | 54 |
| NONE_FOUND | 35 |
| INVALIDATED | 3 |
| VACUOUS AT BIRTH | 2 |
| INDICATIVE | 2 |
| CANNOT_DETERMINE | 2 |
| **Total** | **98** |

**INDICATIVE** (new class, added mid-sweep at the lead's instruction): an item that asserts an
outcome rather than specifying a check, so it reads as already-satisfied and nothing ever
builds or runs it. Two confirmed: Ruling 21's "Acceptance test" is a standard for judging a
future *auditor's* correctness ("...has mis-applied this ruling"), not a system check — a count
is derivable, no violation threshold is stated, and a verifying subagent was observed supplying
that threshold itself rather than finding it stated. Ruling 51's "acceptance evidence is the
aggregate line's count... with the delta explained" is the same shape: the measurement is real
and built, the pass/fail line is never drawn.

**CANNOT_DETERMINE** (2): Ruling 85 item 3 has no `Violation:` clause among two genuine
siblings in the same §4 — reads as disclosure prose for the maintainer's weighing, and the
question "is this vacuous" may be the wrong one to ask of it. Ruling 29's own override clause
("unowned"/"owner TBD" in the cell) is textually triggered by register row F72 today; whether
Ruling 49's later register-conformance sentence retroactively legitimises that phrasing, or
F72 is the live regression Ruling 29 exists to catch, is not resolved here.

## 6. The growth-versus-undercount split

Ruling 93's own commit: `22d8d64`, `2026-09-02T12:53:04+01:00`. First-commit timestamp of every
one of the 30 files carrying a genuine item (`git log --format=%aI --follow -- <path> | tail
-1`):

**28 of 30 existed at or before Ruling 93's own commit; 2 arrived after** — Ruling 94's own
file (`13:27:48`) and Ruling 95's own file (`14:28:36`). Of the gap between Ruling 93's
"twelve" and this record's 30: **2 is growth, 16 is undercount** (28 files already carried a
genuine item when Ruling 93 said twelve). Ruling 94's "fourteen," filed at `13:27`, could in
principle have seen up to 29 of the 30 (everything but Ruling 95's own file, filed after it) —
so that revision undercounted by at least 15.

## 7. Behavioural evidence, where it exists

Ruling 21 is the only item in this sweep with an *observed* failure rather than a mood
judgement: a verifying subagent built the check the item describes, then had to invent the
pass/fail threshold itself, live, because the ruling never states one. Every other INDICATIVE
or CANNOT_DETERMINE finding above is a structural reading (a clause present or absent, a
`Violation:` sentence present or absent) — real, but not behaviourally demonstrated the same
way.

## 8. Full table

**Filed here directly as of 2026-09-02, replacing the standalone CSV this section used to
point at** (`ruling-acceptance-item-sweep-5c0d24d.csv`, same directory — dropped this
commit). CI's `test_no_reference_rows_are_bundled_in_the_repository`
(`backend/tests/test_lineage.py`, FR-DATA-32) flagged the CSV as bundled reference data.
Ruling 59's carve-out
(`generated_from_tracked_corpus`) does not cover it, and is not being extended to: that
predicate is bought by **provable reproducibility** — a file earns the exemption because
anyone can regenerate it from tracked source and diff it against `git ls-tree`. This
table's `class` column is not derivable by any script (§2's own docstring says so) — it
took reading governed code and ruling text and exercising judgement, so there is no
generator to diff against. A carve-out whose condition cannot be met is not one to extend;
it is one to stay outside of. **What is lost is a format, not a capability**: the
mechanised half of this sweep (§2, `scripts/ruling-acceptance-item-census.py`) is
unaffected, committed, and independently re-runnable; only the hand-classified half moves
from a separate file into this table.

**A second reason the CSV was less machine-readable than it appeared, found while making
this move rather than before it:** 16 of the 98 rows carried an unescaped literal comma
inside `item_summary` or `evidence`, splitting past 5 fields under a standard `csv.reader`.
`ruling`/`record_file`/`class` — fields 1-3 — were never affected, so the class tally below
and in §5 does not move, but a reader loading the old file with ordinary CSV tooling rather
than `cut` would already have hit this. Reconstructed by hand against each row's own text
before this table was built; the tally was re-verified after and matches §5 and the
original CSV exactly: CONSTRUCTIBLE 54, NONE_FOUND 35, INVALIDATED 3, VACUOUS 2,
INDICATIVE 2, CANNOT_DETERMINE 2.

Pinned to `5c0d24df5ce4b58411eb0e67bf7cc2b91a44a3ca`, the same tree named in this record's
own header — 98 rows, one per ruling:

| Ruling | Record file | Class | Item summary | Evidence |
|---|---|---|---|---|
| 1 | 2026-08-29-w11-prework-rulings.md | NONE_FOUND |  |  |
| 2 | 2026-08-29-w11-prework-rulings.md | NONE_FOUND |  |  |
| 3 | 2026-08-29-w11-prework-rulings.md | NONE_FOUND |  |  |
| 4 | 2026-08-29-w11-prework-rulings.md | NONE_FOUND |  |  |
| 5 | 2026-08-29-w11-prework-rulings.md | NONE_FOUND |  |  |
| 6 | 2026-08-29-w11-slice1-rulings.md | CONSTRUCTIBLE | bench tooling not reaching pyproject.toml/CI | scripts/bench-rating.py exists stdlib-only; lockfile/CI grep = 0 |
| 7 | 2026-08-29-w11-slice1-rulings.md | NONE_FOUND |  | full section read; no phrasing hit under any form |
| 8 | 2026-08-29-w11-slice1-rulings.md | CONSTRUCTIBLE | booster deserialised once per N quotes | packages/pricing-core/tests/test_rating_runtime.py:282 passes |
| 9 | 2026-08-29-w11-slice1-rulings.md | CONSTRUCTIBLE | two firing constraints both in decline_reasons | packages/pricing-core/tests/test_rating_score.py:239 passes |
| 10 | 2026-08-29-w11-slice1-rulings.md | NONE_FOUND |  | full section read; none |
| 11 | 2026-08-29-w11-slice1-rulings.md | NONE_FOUND |  | full section read; none |
| 12 | 2026-08-29-w11-slice1-rulings.md | NONE_FOUND |  | full section read incl. addendum/findings; none |
| 13 | 2026-08-29-w11-slice1-rulings.md | NONE_FOUND |  | full section read; none |
| 14 | 2026-08-29-w11-slice2-rulings.md | CONSTRUCTIBLE | null rating_version_ref -> 409; override clause not triggered | backend/tests/test_score.py:139 passes; schema check confirms not triggered |
| 15 | 2026-08-29-w11-slice2-rulings.md | CONSTRUCTIBLE | blank change_summary refused 422; override not triggered | backend/tests/test_rating_versions.py:270 passes |
| 16 | 2026-08-29-w11-slices-2-4-rulings.md | CONSTRUCTIBLE | item1 WITHDRAWN (originality not substance) + item2 degraded-read built | register F32; docs/plans/2026-08-29-w11-algorithm-pin-maturity.md:124 Correction to Ruling 16 |
| 17 | 2026-08-29-w11-slices-2-4-rulings.md | CONSTRUCTIBLE | malformed ScoringResult returned verbatim 200 not 500 | backend/tests/test_score.py:340 passes |
| 18 | 2026-08-29-w11-slices-2-4-rulings.md | CONSTRUCTIBLE | unscoped account refused + RBAC no-builtin-role guard | backend/tests/test_score.py:230 + test_rbac.py:101 both pass |
| 19 | 2026-08-29-w11-slices-2-4-rulings.md | CONSTRUCTIBLE | EVIDENCE_FLOOR vs FR-GOV-37 named list, one read of each | docs/specs/06-governance.md:145 carries the amendment citing Ruling 19 |
| 20 | 2026-08-29-w11-slices-2-4-rulings.md | CONSTRUCTIBLE | deployment submission reaching evidence check; not yet built as ruled | DEFAULT_POLICY has no deployment entry consistent with disposition |
| 21 | 2026-08-29-w11-slices-2-4-rulings.md | INDICATIVE | standard for judging a future auditor not a system check | measurement derivable (extraction command given); no violation threshold stated; subagent had to supply the pass/fail judgment itself |
| 22 | 2026-08-29-w11-1-2-rate-table-maturity-ruling.md | CONSTRUCTIBLE | status-column tripwire + no resolver hardcode | backend/tests/test_rating_version_compile.py:240 passes; compile.py:311 |
| 23 | 2026-08-29-w11-slices-3-4-rulings.md | CONSTRUCTIBLE | trace-delete refusal under NFR-OVR-6 floor | backend/tests/test_traces.py:258,284 both pass |
| 24 | 2026-08-29-w11-slices-3-4-rulings.md | CONSTRUCTIBLE | per-run threshold above workspace setting refused | backend/tests/test_scoring_handlers.py:292,323 both pass |
| 25 | 2026-08-29-w11-slices-3-4-rulings.md | CONSTRUCTIBLE | batch-produced traces excluded from GET /traces | backend/tests/test_traces_api.py:275 passes |
| 26 | 2026-08-29-w11-ruling-vs-plan-scope.md | CONSTRUCTIBLE | merged PR touching scoped-out file with no ruling citation; not yet built | proposed obligation absent from delivery-process.md |
| 27 | 2026-08-29-w11-ruling-vs-plan-scope.md | CONSTRUCTIBLE | no resolver hardcodes status; was failing at filing now fixed | historically red at 39cb58e; fixed by Ruling 28 |
| 28 | 2026-08-29-w11-algorithm-pin-maturity.md | CONSTRUCTIBLE | maturity-check tripwire on algorithm status | compile.py:430; backend/tests/test_rating_version_compile.py:260 passes |
| 29 | 2026-08-29-w11-algorithm-pin-maturity.md | CANNOT_DETERMINE | unowned register row with no decay event | F72's Decision cell literally contains unowned; whether Ruling 49's later conformance sentence legitimises that is open |
| 30 | 2026-08-29-w11-fr-rate-65-attribution.md | CONSTRUCTIBLE | FR-RATE-65 absent from roadmap; fix outstanding | grep -c FR-RATE-65 docs/roadmap.md = 0; known tracked gap |
| 31 | 2026-08-29-w11-3-d6-batch-resumability-ruling.md | NONE_FOUND |  | confirmed empty directly and against register |
| 32 | 2026-08-29-w11-3-d6-batch-resumability-ruling.md | NONE_FOUND |  | confirmed empty; addendum at :340 is citation fixes only |
| 33 | 2026-08-29-w11-slice-parallelism-ruling.md | NONE_FOUND |  | confirmed empty |
| 34 | 2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md | NONE_FOUND |  | violation hits are ordinary NFR-violation prose not an item |
| 35 | 2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md | NONE_FOUND |  | full section read; none |
| 36 | 2026-08-30-w11-nfr-rate-11-quote-input-stores-ruling.md | NONE_FOUND |  | violation hits are ordinary prose not an item |
| 37 | 2026-08-30-w11-2b-bundle-resolution-ruling.md | NONE_FOUND |  | confirmed empty |
| 38 | 2026-08-30-w11-service-account-permissions-ruling.md | NONE_FOUND |  | confirmed empty |
| 39 | 2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md | NONE_FOUND |  | own text has none; the "maintainer acceptance" sentence is a sign-off superseded by reopen-direction.md §4 |
| 40 | 2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md | CONSTRUCTIBLE | retry-cap hook: synthetic runtime state at cap+1 and cap-1 | tests/test_retry_cap_hook.py cites Ruling 40 §5 verbatim; 11 tests pass |
| 41 | 2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md | NONE_FOUND |  | no formal Acceptance section anywhere in the ruling (5 subsections none titled Acceptance); an indicative-mood aside in §3 prose ("a per-request read is provable") was never promoted to a stated item |
| 42 | 2026-08-30-w11-reopen-scope-and-batch-frame-contract-rulings.md | CONSTRUCTIBLE | three concrete prohibitions - stated by the ruling as testable not hortatory | docs/audit/work/W11/README.md §10.5 confirms all three citing Ruling 42 |
| 43 | 2026-08-30-w11-reopen-scope-and-batch-frame-contract-rulings.md | CONSTRUCTIBLE | (a) field-exclusion test + (b) output-serialisation totality test | packages/pricing-core/tests/test_rating_score_batch.py; 11 tests pass |
| 44 | 2026-08-30-w11-4b-trace-environment-ruling.md | CONSTRUCTIBLE | two tests: multi-env key resolves to issued env; no-env caller writes no row | backend/tests/test_score.py:796,843 cite Ruling 44 part3; auth/service.py:230-234 implements it |
| 45 | 2026-08-30-nt-0014-q1-q3-q4-rulings.md | CONSTRUCTIBLE | digest+commit-pairing broken-input proof for the process-core extract | scripts/audit-docs.py:778 check_process_core_digest (check 27) built |
| 46 | 2026-08-30-nt-0014-q1-q3-q4-rulings.md | CONSTRUCTIBLE | three-case cutoff-date proof for the plan acceptance-standard check | check_plan_acceptance_standard (check 28) + tests/test_audit_docs_plan_acceptance_standard.py |
| 47 | 2026-08-30-nt-0014-q1-q3-q4-rulings.md | CONSTRUCTIBLE | no-op watcher cycle must be byte-identical | tests/test_watcher_runtime_state.py:51 test_a_cycle_with_no_change_is_byte_identical |
| 48 | 2026-08-30-nt-0014-q1-q3-q4-rulings.md | NONE_FOUND |  | pure doc-text correction; no check described |
| 49 | 2026-08-30-nt-0015-q1-q5-rulings.md | NONE_FOUND |  | own text is a one-time PR with no stated check; its Text A/B/C become testable via Ruling 50 |
| 50 | 2026-08-30-nt-0015-q1-q5-rulings.md | CONSTRUCTIBLE | three broken fixtures + live-register positive control for register-lint | scripts/register-lint.py check_decision_grammar/check_resolution_annotation/check_unowned_decay - exactly the three named |
| 51 | 2026-08-30-nt-0015-q1-q5-rulings.md | INDICATIVE | aggregate residue-count delta at two trees; report not test | register-lint.py residue/residue_line built and run; no violation threshold stated anywhere |
| 52 | 2026-08-30-nt-0015-q1-q5-rulings.md | NONE_FOUND |  | corrected from an earlier CONSTRUCTIBLE call; the three constraints are content requirements on a closure record not a stated run/observe test - code enforcing constraint 1 exists (register-owed.py) but the ruling itself never states a violation |
| 53 | 2026-08-30-nt-0015-q1-q5-rulings.md | NONE_FOUND |  | corrected from an earlier CONSTRUCTIBLE call; only sub-rules plus an override clause, no stated violation - findings/README.md ties to the convention but the ruling itself states no check |
| 54 | 2026-08-31-f62-timing-ms-ruling.md | CONSTRUCTIBLE | file-level Acceptance Standard doubling as the ruling's own (single-ruling file); items 1-4 | grep commands with stated expected output all verified; item 5 explicitly disclaimed as not a check |
| 55 | 2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md | NONE_FOUND |  | corrected from an earlier CONSTRUCTIBLE call; only an Overridden-if clause in prose, no separately labelled acceptance sentence |
| 56 | 2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md | NONE_FOUND |  | same correction as 55 |
| 57 | 2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md | NONE_FOUND |  | same correction as 55 |
| 58 | 2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md | NONE_FOUND |  | same correction as 55; one disjunct of its own override clause is a self-acknowledged subjective call |
| 59 | 2026-09-01-nt-0016-slice2-fr-data-32-ruling.md | CONSTRUCTIBLE | three named broken-input census cases (Broken-input proof convention) | backend/tests/test_lineage_census_carveout.py cites Ruling 59 x2; all 3 cases present |
| 60 | 2026-09-01-ruling-60-census-provenance-checkout-depth.md | CONSTRUCTIBLE | checkout-depth config confirms Ruling 59's cases still hold | .github/workflows/python.yml:124-126 fetch-depth:0 matches §3 |
| 61 | 2026-09-01-ruling-61-notes-tombstone-stubs-watched.md | INVALIDATED | check_notes_tombstone() must red on a stray file and on an edited stub body | function absent (0 matches); scripts/audit-docs.py:55-64 module docstring: slot 30 given to NT-0019's header check protective job ends with this commit by that same resolution until W37-6 deletes the stubs entirely; name repurposed to check_redirects/slot 36 which watches REDIRECTS.csv not the old notes root under .claude |
| 62 | 2026-09-01-nt-0016-q1-q2-q3-q7-general-rulings.md | NONE_FOUND |  | only an Overridden-if clause; lapsed by its own clause per NT-0019 §9 |
| 63 | 2026-09-01-nt-0016-q1-q2-q3-q7-general-rulings.md | NONE_FOUND |  | only an Overridden-if clause; lapsed by its own clause per NT-0019 §9 |
| 64 | 2026-09-01-nt-0016-q1-q2-q3-q7-general-rulings.md | NONE_FOUND |  | only an Overridden-if clause; kept and reassigned as check 38 elsewhere but states no test itself |
| 65 | 2026-09-01-nt-0016-q1-q2-q3-q7-general-rulings.md | NONE_FOUND |  | only an Overridden-if clause; lapsed by its own clause per NT-0019 §9 |
| 66 | 2026-09-02-w37-migration-preconditions-rulings.md | CONSTRUCTIBLE | item1 checks 30/31/33/36 built; item2 (reversion-based) WITHDRAWN by Ruling 73 | check 34 DP-7 shared predicate confirmed shared between doc-id.py and audit-docs.py |
| 67 | 2026-09-02-w37-migration-preconditions-rulings.md | CONSTRUCTIBLE | three items: load-bearing exclusions, positive control, one shared constant | LEGACY_FORM_PATTERNS / check 36 shared constant confirmed |
| 68 | 2026-09-02-w37-migration-preconditions-rulings.md | CONSTRUCTIBLE | three items: filter fails on body-line change and on unclassifiable hunk; one predicate | frozen_file_matches_after_migration_stamp shared between doc-id.py and audit-docs.py |
| 69 | 2026-09-02-w37-migration-preconditions-rulings.md | CONSTRUCTIBLE | four items: population drift loud, under/over-exemption, recorded deviation | _VENDORED_SKILLS exists in scripts/_docid.py; reconciliation tests in tests/test_doc_id.py |
| 70 | 2026-09-02-w37-field-set-and-rollup-rulings.md | CONSTRUCTIBLE | four items: wrong-carrier check, hardcoded-policy check, silent-coverage check, ledger extra | check_header_fields/derive_field_policies read from templates; FD.md already excludes decision: citing Ruling 70 |
| 71 | 2026-09-02-w37-field-set-and-rollup-rulings.md | CONSTRUCTIBLE | four items: unscoped/silent-empty/zero-by-construction/lost-carry-in | scripts/doc-index.py _findings_figures returns (opened,discharged,unowned_decay,carry_in); uses r.unowned not not decision |
| 72 | 2026-09-02-w37-field-set-and-rollup-rulings.md | CONSTRUCTIBLE | four fixtures: invisible slice, mid-flight, replanned, no-catch-all | _rollup_map_plan docstring cites Ruling 72; precedence table present, no trailing catch-all |
| 73 | 2026-09-02-w37-6-leaf-plan-findings-rulings.md | CONSTRUCTIBLE | withdrawal of Ruling 66 item2 + 2a/2b/2c substitute; own §5 two falsifiability items | sweep_legacy_forms measured wrong in both directions on the real corpus |
| 74 | 2026-09-02-w37-6-leaf-plan-findings-rulings.md | CONSTRUCTIBLE | git-hygiene exclusion re-testable via limb 2b; gap not mis-described as closed | sweep_legacy_forms over git-hygiene returns 0 hits |
| 75 | 2026-09-02-w37-6-leaf-plan-findings-rulings.md | CONSTRUCTIBLE | RL- route end to end; no docs/audit/ path survives in a charter | this record is its own worked exemplar of the RL- route |
| 76 | 2026-09-02-w37-6-leaf-plan-findings-rulings.md | CONSTRUCTIBLE | no rejected criterion states anywhere; absent check reds; re-assignment visible | _VENDORED_SKILLS confirmed to exist (was absent when this ruling was filed) |
| 77 | 2026-09-02-w37-6-leaf-plan-findings-rulings.md | CONSTRUCTIBLE | backstop zero-none row; two files findable; findings clause not half-applied | acceptance item (a)'s zero-none-row check is the backstop |
| 78 | 2026-09-02-w37-6-leaf-plan-findings-rulings.md | CONSTRUCTIBLE | predicate asserted not trusted; result checkable after the fact; class swept not instance | _discover_closure_records verified directly: 8 CR-work + 1 CR-phase + 2 RS-audit + 10 LG- of 21 real records |
| 79 | 2026-09-02-w37-template-parser-conflicts-rulings.md | CONSTRUCTIBLE | three items: row-template parses; Ruling 70 mutation; kind: on WK- rejected | tests/test_template_headers.py:378,407,426 all pass |
| 80 | 2026-09-02-w37-template-parser-conflicts-rulings.md | CONSTRUCTIBLE | three items: phase body parses; no-field no-borrow; template mutation | tests/test_template_headers.py:479,507,541 all pass |
| 81 | 2026-09-02-w37-commit-boundary-and-plan-reviews-shape-rulings.md | CONSTRUCTIBLE | three items: round-trip check; two positive controls; dual exit-0 | tests/test_doc_id_migrate.py:807; both doc-index.py --check and audit-docs.py exit 0 live |
| 82 | 2026-09-02-w37-commit-boundary-and-plan-reviews-shape-rulings.md | CONSTRUCTIBLE | three items: coverage assertion; 11-review split; legacy-guard generalised | _check_plan_reviews_heading_census live; _discover_plan_reviews verified to return 11 drafts |
| 83 | 2026-09-02-w37-guard-arithmetic-and-ledger-family-rulings.md | CONSTRUCTIBLE | five items: census fails today naming real headings; two mutations; legacy-guard nuance; roadmap arithmetic not yet built | _check_multi_ruling_files_not_silently_unrecognised live; _reconcile_census raises citing Ruling 83 §3 item 3 |
| 84 | 2026-09-02-w37-guard-arithmetic-and-ledger-family-rulings.md | VACUOUS | item2 (original text): no emitted LG- carries a slice: resolving to no roadmap row | scripts/doc-id.py:946 elif key in (slice,...): continue - unconditional, no slice parameter in _stamp_header's signature; register F77; items 1/3/4 CONSTRUCTIBLE and built |
| 85 | 2026-09-02-w37-stage-boundary-authority-ruling.md | CANNOT_DETERMINE | item3 has no Violation clause among two genuine siblings in the same §4 | reads as disclosure prose for the maintainer's weighing; items 1-2 CONSTRUCTIBLE |
| 86 | 2026-09-02-w37-ruling-a-series-and-standalone-ruling-files.md | INVALIDATED | item3: each new RL- record carries an owner: that is not decision-maker | Ruling 95 (a later ruling) reverses the decision this item encoded; post-sweep confirmed by commit 2e48960/#620: _ruling_file_owner now unconditionally returns decision-maker for every input |
| 87 | 2026-09-02-w37-ruling-a-series-and-standalone-ruling-files.md | CONSTRUCTIBLE | three items: no PL- body-heading; depth-independent classifier; non-constant owner - not yet built | _discover_plain_plans still returns the three files as PL-; _PLAN_KIND_OWNER[leaf]=planner still hardcoded |
| 88 | 2026-09-02-w37-container-family-and-line-citations-rulings.md | INVALIDATED | item2 (original text): a fixture whose only level-2 heading is followed by three record headings | PR #609/2fbce0c demoted the heading; grep -c '^## ' docs/audit/plan-reviews.md = 0; rebuilt by Ruling 93 on a property not a level |
| 89 | 2026-09-02-w37-container-family-and-line-citations-rulings.md | CONSTRUCTIBLE | three items: no legacy-path-offset citation; ledger disposition recorded; one instrument fixed | the 17-citation corpus reproduced exactly by the stated grep |
| 90 | 2026-09-02-w37-roadmap-transform-rulings.md | CONSTRUCTIBLE | closed-work counts non-zero; 41 ids in 41 WK- rows out | _discover_roadmap(root) verified by execution to return 41 distinct ids |
| 91 | 2026-09-02-w37-roadmap-transform-rulings.md | CONSTRUCTIBLE | body-fragment merge from every source row; disagreement forces refusal | body_fragments unconditional list comprehension; NotImplementedError on len(known_signals)>1 |
| 92 | 2026-09-02-w37-roadmap-transform-rulings.md | CONSTRUCTIBLE | every Depends-on id resolves to a WK- row (W6 control); W6 retired with successors named | W6 verified by execution: status=retired, body names W6a/W6b |
| 93 | 2026-09-02-w37-ruling-88-acceptance-amendment.md | CONSTRUCTIBLE | rebuilt property-based fixture + positively-identified container (replaces Ruling 88 item2) | grep -c '^## ' docs/audit/plan-reviews.md = 0 confirmed at current tree |
| 94 | 2026-09-02-w37-vacuous-acceptance-item-ruling.md | CONSTRUCTIBLE | substituted count-and-print check + _stamp_header mutation test (replaces Ruling 84 item2); design constructible | register F77: not yet built as of this pin - no commit had touched scripts/doc-id.py or tests/test_doc_id_migrate.py for this purpose since 09b7e9b |
| 95 | 2026-09-02-w37-gap-1-ruling-86-owner-ruling.md | VACUOUS | item3 (originally worded): Ruling 87's decision-maker owner for the 3 standalone files still holds after this amendment | scripts/doc-id.py:1541 owner=_PLAN_KIND_OWNER[leaf]=planner; zero code paths emitted decision-maker for those 3 files as of this pin - non-interference property holds, nothing to observe; re-instrumented post-sweep by commit 2e48960/#620 (test_ruling_87_standalone_files_are_untouched_by_this_amendment) |
| A1 | 2026-08-30-nt-0012-0013-0014-adoption.md | NONE_FOUND |  | two-sentence placement Ruled clause; no test stated |
| A2 | 2026-08-30-nt-0012-0013-0014-adoption.md | NONE_FOUND |  | placement decision only |
| A3 | 2026-08-30-nt-0012-0013-0014-adoption.md | NONE_FOUND |  | placement decision only |

## 9. Provenance — how 31 became 30, not just that it did

The count was not 30 on the first pass. It was **31**, reported to the lead, then corrected
down by one file after applying the lead's own stated boundary — *"an `Overridden if `<X>``
clause is never itself an acceptance item"* — back onto this sweep's own data. The path:

1. First pass counted `nt-0015-q1-q5-rulings.md` (Rulings 49-53) as carrying acceptance items
   for Rulings 50, 51, **52, and 53** — the last two admitted because real, running code
   enforces their substance (`register-owed.py`'s dirty-worktree refusal for Ruling 52; the
   findings-directory naming convention `docs/audit/findings/README.md` ties to Ruling 53).
2. Re-reading Rulings 52 and 53's *own text* against the boundary found neither states a
   `Violation:` clause or any check — only "Three constraints" / "Three sub-rules" plus an
   "Overridden if" clause. **The code enforcing their substance is real; the ruling stating a
   check is not the same fact**, and only the second counts as "genuine" under §1's own
   definition. This is the identical conflation a verifying subagent had already been caught
   making on Ruling 41 earlier in the same sweep — found a second time, in this sweep's own
   output, by applying the same rule to itself rather than assuming the first catch was the
   only instance.
3. Rulings 52 and 53 moved CONSTRUCTIBLE → NONE_FOUND. Rulings 50 and 51 still carry genuine
   items (50 built and tested; 51 reclassified INDICATIVE separately, §5), so
   `nt-0015-q1-q5-rulings.md` stays in the count. **`nt-0016-q4-q5-q6-q7-notes-rulings.md`
   (Rulings 55-58) did not survive the same re-read** — all four of its rulings state only an
   override clause, with no exception — and dropped out of the file count entirely: 31 → 30.

Recorded as a path rather than a number because the number alone does not show the count was
**measured against a stated rule** rather than **settled on and then defended** — a sweep that
only ever revises upward on a second look is fitting its own expectation; one that revises
against its own reported total, by the same rule it was just handed, is checking itself.

## 10. On verifying a count — a total validates the total, and nothing else

The lead verified this record's first class-count line (`CONSTRUCTIBLE=52 ... NONE_FOUND=37`,
since corrected to `54 ... 35`) by confirming the six numbers summed to 98. They did. **So
does the corrected set** — two buckets had moved by 2 in opposite directions, and a sum is
invariant under a transfer between buckets, so that check was not unlucky: it was
**structurally incapable** of detecting the error it was run against. Recorded here, in the
artifact the error nearly entered, rather than only in the chat thread that caught it, because
it generalises past this one count: **a total validates the total and nothing else.** This is
the same reason `scripts/ruling-acceptance-item-census.py` (§2) asserts bucket membership by
naming which heading fell into which bucket, not by confirming a printed sum — Ruling 83's own
census property, restated: the arithmetic only catches an undercount if the check names units,
not if it only re-adds what it was given.

## 11. Dated correction — 2026-09-02 (same day, after filing): WITHDRAWN, a seventh class

**This class was absent from the brief this sweep was commissioned against.** The brief named
two failure shapes — VACUOUS AT BIRTH and INVALIDATED — and this record added INDICATIVE and
CANNOT_DETERMINE while the sweep was in progress. A fifth shape surfaced only after filing,
while answering a follow-up question about which rulings a downstream migration slice applies
to, and the six classes above cannot express it. Filed as a correction to this record, not an
edit to §5's table or the CSV — the six-class count in §5 stands as filed, exactly as Rulings
93 and 94 stand as filed under this record's own `Corrects` header.

**The shape: an item that fires constantly and returns the wrong verdict, in both directions
at once — false positives *and* false negatives.** It is not VACUOUS AT BIRTH, because it
fires; not INVALIDATED, because nothing broke it — it was wrong on the day it was written; not
INDICATIVE, because it is a genuine, running check, just of the wrong thing. Named
**WITHDRAWN**, after the disposition both of its instances actually received.

- **Ruling 66 acceptance item 2** (original, reversion-based test), withdrawn by Ruling 73.
  Measured against the shipped `sweep_legacy_forms` on the real corpus: **8 false positives**
  on non-members that pass (`repo-architecture`, `dev-commands`, `git-hygiene`, `CLAUDE.md`,
  four role files), **4 false negatives** on real members that fail — one of them
  `subagent-driven-development`, a **primary** instrument the criterion exists to protect —
  and no under-inclusion limb at all, so a member nobody thought to list could never have been
  caught either way. §5's CONSTRUCTIBLE count for Ruling 66 reflects its live replacement
  (2a/2b/2c, demonstrated falsifiable against the real corpus in Ruling 73's own §5); the
  original item is what this correction names.
- **Ruling 16 acceptance item 1**, withdrawn the same day it was filed (`docs/plans/2026-08-
  29-w11-algorithm-pin-maturity.md:124`, "Correction to Ruling 16," discharging register row
  F32): the property it claimed "becomes expressible for the first time" in a later slice had
  already shipped and passed in an earlier one. Never a standing defect — found and closed
  same-day — which is why it counts as an instance of the shape rather than as an open
  finding.

**Both instances are closed, not open.** Verified 2026-09-02 against the item-4 follow-up
this correction arose from: does a downstream migration slice apply to either withdrawn item?
No — the *withdrawn* items are superseded by live, sound replacements, and nothing currently
scheduled depends on the withdrawn text. Filed here as taxonomy, not as outstanding work.

**The finding this correction states about itself, plainly rather than softened:** a
taxonomy commissioned to classify every defect a corpus contains, and missing a slot for a
defect that same corpus actually contains, is the same failure this sweep exists to find,
recurring in the sweep's own instrument. It was not caught by the brief, the sweep's own
first pass, or either verifying subagent; it surfaced only because a downstream question
("does this still apply") forced a second look at material already filed as resolved.

## 12. Status note, added 2026-09-02: two findings converted to scheduled work

Not a correction to this record's own content — a pointer, so a reader arriving later does not
have to re-derive that these two items are no longer merely findings. **W37-5c**, a precondition
slice cut after this sweep, scopes itself to "everything that stops or blinds" the migration
run. On the *blinds* limb: **Ruling 84 §4 item 2's substituted check (Ruling 94) is to be
built**; **Ruling 86 §4 item 3 is to be rebuilt so it can pass on some input**. Neither stops
the run by itself — both are checks meant to police it that currently cannot fail — which is
exactly "blinds" rather than "stops," and exactly why both are in W37-5c's scope rather than
already fixed. Status as of this note: scheduled, not yet built. See `docs/roadmap.md` and
W37-5c's own filed plan for current state; this record does not track it further.

## 13. Dispositions — 2026-09-02, the lead's. The four items this record left undecided

**This section is the verdict half of `CLAUDE.md` §13** — *every requirement without evidence
gets one of four verdicts; silence is not one of them.* The record above classified; it
deliberately wrote no dispositions. The evidence behind each was gathered by this record's own
author on request and is cited inline; **the verdicts are the main thread's and were not written
by a subagent.**

Nothing here edits the record above. Six of the seven classes were already disposed of by events
rather than by argument, and are restated only so no reader has to re-derive them:

| Class | Disposition | Where it went |
|---|---|---|
| VACUOUS AT BIRTH (2) | built | W37-5c items 4 and 5, landed `e2296ec` |
| INVALIDATED (3) | rebuilt or a bounded trade | R88 by Ruling 93; R86 by `e2296ec`; R61 a documented trade, horizon W37-6 |
| WITHDRAWN (2) | taxonomy | §11 above; superseded by live replacements |
| NONE_FOUND (35) | grandfathered by date | the ruling-form flag-day at `aab6327`; the census `none` bucket reds for post-flag-day rulings only |

### CANNOT_DETERMINE 1 of 2 — Ruling 29 versus register row F72: **no violation**

**Determinable after all, and the answer is that the override applies.** Ruling 29's clause
(`docs/plans/2026-08-29-w11-algorithm-pin-maturity.md:233-237`) ends *"This ruling is overridden
if a row is filed with 'unowned' or 'owner TBD' in that cell."* F72's Decision cell opens with the
literal word `unowned`. The override is scoped to that cell and fires on the marker's presence.

**The lead raised this as a live violation and was wrong**, having escalated before reading the
rule's own scope sentence. Recorded because the correction is the useful part: a cited rule
usually scopes itself, and that clause decides whether a violation is real.

**What is open is a different, later rule.** Ruling 49 Text B — *"An unowned row must name the
event that next confirms or assigns its owner"* — asks for an owner-assignment event; F72 names a
discharge condition, which is not plainly the same thing. **19 of 82 rows carry the same
`unowned` marker** and `check_unowned_decay` reports zero across all of them, because it enforces
`_UNOWNED_MIN_LEN = 40`, a length proxy its own comment at `scripts/register-lint.py:103-104`
says presumes rather than verifies. Being checked against `F64` and `F79` — two open findings
already against this script, both the same shape of a check reporting zero because it cannot see
— before anything new is filed.

### CANNOT_DETERMINE 2 of 2 — Ruling 85 item 3: **not an acceptance item**

**Ruling 85 §4 carries two acceptance items, not three.** Items 1 and 2 each carry a `Violation:`
clause and hold regardless of any later choice. Item 3 carries none and says of itself that it is
*"stated concretely because the maintainer will weigh it"* — a consequence disclosed under a
reading the ruling declines to adopt. **It has no failing case by construction**, and a
`Violation:` clause added to it would re-scope item 2's violation to a date range rather than
instrument anything new.

**The consequence worth more than the row.** The classifier counted it, so the classifier's
predicate selects on **position under a §4 heading** rather than on the presence of a checkable
property. One instance is not a rebuild; it is recorded here so the next reader knows the
population is a ceiling rather than a measurement.

### INDICATIVE, both members: **confirmed, and neither is a defect**

**Ruling 21.** The ruling is *"no change"*, and its own text puts the unresolved question outside
its role — *"a scope question, and `CLAUDE.md` §12 puts scope outside this role."* An item that
establishes a standard for judging a future **auditor** is a real thing and is not a system check.
Its one live hit, `CONTROL_FACTOR_IN_RATEABLE_PATH`, **already has custody and needs no new
finding**: register row `FR-RATE-25` (`F-W9-3`) clause (5) records *"no `control`-intent factor
in a rateable path (`02` FR-MODEL-3) — no implementation anywhere"* with a disposition attached.
Verified at `7186dca`: the code is declared in `docs/specs/03-rating-engine.md:617` and
`docs/workflows/wf-02-model-to-rating-version.md`, and is absent from
`backend/src/app/errors.py`.

**Ruling 51.** Its §2 says in its own words *"This ruling does not fix its value; it fixes its
form."* An item asking for a count at two trees with the delta narrated, and stating no
threshold, is exactly what a form-fixing ruling should produce.

### The class-level disposition, which is the part that generalises

**INDICATIVE is not a defect class. It is a shape.** Both members decline to set a threshold **in
their own text**, deliberately and with reasons given. Booking either as a defect would
miscategorise a deliberate act.

**The defect is never the item; it is a downstream reader booking one as satisfied.** That is
Ruling 94's *"a vacuously true acceptance item does not satisfy itself"* arriving by the opposite
mechanism: **a vacuous item cannot fail, and an indicative item cannot pass.** Both are unusable
as evidence, for symmetric reasons.

**So: an INDICATIVE acceptance item discharges nothing, and no close, audit or plan review may
cite one as evidence that a property holds.** Where such an item is the only acceptance evidence
a ruling offers, the ruling's property is unverified and must be said to be unverified — which is
`CLAUDE.md` §13's *a check that has never printed a failure has not been tested*, applied to a
check that cannot print one in either direction.
