# W37-6 — Ruling 99: three `docs/audit/` files no NT-0019 clause maps (2026-09-03)

**What this is.** The last residue of the post-migration `none` count. F95
(`docs/audit/findings/F95.md`) covers the two families (`WF`, `FD`) NT-0019 declares but
`doc-id.py` does not implement. **These three files are a different kind of gap**: no clause
in NT-0019 names them at all — they postdate the tree its own classification sweep ran
against, or are explicitly marked "no §5.2 row of its own" in the shipped code. §7(a) requires
`none: 0`; this ruling is what the maintainer has said takes the count from 3 to 0.

**Filed under** delegation §1, *"NT-0019 §1/§4 amendments needed to reach a completing, green
run — owner values, scope markers, stamp-set membership, **exemption dispositions**"*
(`docs/plans/2026-09-03-w37-6-time-boxed-delegation.md:19-21`). Each file below is an
exemption disposition: which of NT-0019 §1.4's four dissolution destinations, or retirement,
a specific file takes, because no general rule reaches it.

## Authority

- The decision is the maintainer's scope authority, delegated for this window by §1. Cells
  named by the maintainer: NT-0019 §1.4 line 100's four destinations, plus retirement with a
  `REDIRECTS.csv` row for a file cited by nothing, using check 38's own predicate as written.
- Halt condition (delegation record, line 33) — checked per file in §2; **not triggered for
  any of the three**, on the evidence below.

## 1. Verified first, at `735c828`

**(a) Why these are undeclared rather than missed — the load-bearing distinction.** NT-0019
§1.13 opens: *"Every governance file **at `8f5d57d`** classifies under §4's rules (0
unmapped, §10)"* (`docs/notes/0019-one-id-per-document.md:238`). `8f5d57d` is dated
2026-09-01 (`git log -1 --format=%ad --date=short 8f5d57d`). Files 1 and 2 were **first
committed 2026-09-02** — `git log --follow --diff-filter=A` on each gives `04ec6bf`
(`docs/audit/nt-0019-verification-and-impact-sweep.md`) and `aab6327`
(`docs/audit/ruling-acceptance-item-sweep.md`), both dated 2026-09-02. **NT-0019 cannot have
named them**; §1.13's "0 unmapped" is a true claim about `8f5d57d`, not a claim these three
falsify. File 3 (`docs/audit/work/nt-0010-0011-adoption/pilot-findings.md`) predates
`8f5d57d` (first committed `27d98bb`, 2026-08-29) but is **declared-undeclared in code**:
`_AUDIT_CLOSURE_CENSUS_EXCEPTIONS["docs/audit/work"]["nt-0010-0011-adoption/pilot-
findings.md"]` (`scripts/doc-id.py:3316-3320`) states, verbatim: *"It has no §5.2 row of its
own; reported as a residual rather than migrated by this slice."*

**(b) NT-0019 §1.4's own dissolution destinations, quoted in full.** *"`docs/audit/`
dissolves into `findings/`, `closures/`, `research/` and `process/`"*
(`docs/notes/0019-one-id-per-document.md:100`). A fifth option, named by the maintainer
rather than found in NT-0019's own text: retirement with a `REDIRECTS.csv` row, for a file
that is one of §1.4's four destinations for **nothing** — the halt condition below is what a
file reaching none of the five looks like.

**(c) The LOOP check's own predicate, read as written, not reconstructed.** Check 38
(`scripts/audit-docs.py:2673-2686`, `check_loop_signal`): *"a `PL-`/`RS-`/`RFC-` **cited by
nothing outside `INDEX.md`**"* is the sub-clause the docstring states; the function's body
today is a pre-migration no-op (*"no `PL-`/`RS-`/`RFC-`/phase population in scope yet"*) — it
has nothing to run against a legacy file, so its predicate is applied here by hand, at face
value: does anything **other than a generated, whole-corpus listing** (the role `INDEX.md`
plays — the reason it is the one named exception) cite the file? `docs/audit/file-census-
5ef559d.csv` is the pre-migration analogue of that same role — a mechanical enumeration of
every tracked file, provenance-locked at `4f95fb3`
(`tests/test_notes_move_citations.py:59-62`) — and is excluded from "cited" for the identical
reason `INDEX.md` is: it lists everything by construction, so its presence discriminates
nothing. No other exclusion is added.

**(d) Measured per file**, `git grep -l <basename>` against the whole tracked tree at
`735c828`:

| File | Cites it (excluding self and the census CSV) |
|---|---|
| `nt-0019-verification-and-impact-sweep.md` | `docs/audit/README.md`; `docs/plans/2026-09-02-w37-6-leaf-plan-findings-rulings.md`; `docs/plans/2026-09-02-w37-6-migration-run-leaf-plan.md`; `tests/test_notes_move_citations.py` (the guard's own `_SPECIFICATIONS_OF_THE_OLD_PATH` entry, mechanism-level, same class as check 30's self-citation carve-out already established in that file) |
| `ruling-acceptance-item-sweep.md` | `scripts/ruling-acceptance-item-census.py` (filed alongside it as a companion instrument, per that script's own docstring: *"Filed alongside `docs/audit/ruling-acceptance-item-sweep.md` §8's table"*) |
| `pilot-findings.md` | `docs/audit/plan-reviews.md` (three citations, `:1169`, `:2620`, `:2627`, `:2781`); `docs/audit/register.md:70` (**by name, as the essay behind register finding F28**); `docs/audit/work/nt-0010-0011-adoption/README.md:152,203`; two `docs/plans/` leaf plans; `scripts/doc-id.py`'s own exception dict |

**None of the three is cited by nothing.** Each has at least one substantive, non-mechanical
citation. **The retirement destination therefore does not apply to any of the three** — this
is a finding, not an assumption: the halt condition names "reaches none of the five," and all
three reach at least the citation test that would otherwise open the door to retirement, so
retirement is closed off by evidence before content is even read.

**(e) Content, read past the title, for files 1 and 2.** Both carry an identical header
shape — `| **Date** | ... | **Auditor** | this session, dispatched by the lead ... | **Pin**
| <sha> | ...` — and both bodies are a dispatched auditor's verification record: file 1
re-derives PR #555's transcription claim and NT-0019's own impact-map populations by direct
measurement (`diff -u`, line counts, heading cross-references); file 2 re-derives and
**corrects** two prior rulings' acceptance-item counts (*"Corrects: Ruling 93 ... and Ruling
94 ... both figures were asserted ... not independently derived"*), with a stated, re-runnable
method (§1's exact `grep` commands) and a named companion script. This is what NT-0019 §1.2
defines `RS`'s unit as: *"one spike, measurement or audit"*, `kind:` *"`spike` · `measurement`
· `audit`"* (`docs/notes/0019-one-id-per-document.md:39`) — and specifically what §1.6's `RS`
`audit` row assigns to the auditor role: *"a bespoke audit's method, evidence and verdicts"*
(`:151`). **This is a content match, not a title match** — the self-titles *"— audit record"*
independently agree with it, and that agreement is named separately in (f) precisely so it is
not mistaken for the basis of the ruling.

**(f) The title pattern, named and set aside as what it is.** Both files self-title *"— audit
record"*, which by pattern also fits `RS- kind: audit`. **Pattern-fit is not a cell** — a title
matching a kind's name is not the same fact as a family's own row assigning that content
there, and this ruling does not rest on the title. It is named here only because the
maintainer asked that the distinction be visible to a reader, not because it adds weight to
(e).

**(g) File 3's destination, from its own citation rather than its content shape.**
`pilot-findings.md` is not itself written as an audit record — it is a findings essay: `docs/
audit/register.md:70` cites it explicitly as the disposition trail for **register finding
F28** ("NT-0010/0011 adoption pilot (F28)"), with the row's own text explaining why one row
carries several dispositions rather than one row per item (*"Precedent for one row carrying
several owners is F-W10-1"*) and naming `pilot-findings.md` §Dispositions as where each is
recorded. NT-0019 §1.2 defines `FD`'s home as *"`docs/findings/` (register row + essay)"*
(`:41`) — **F28's row already lives in `docs/audit/register.md`, migrating into
`findings/register.md` by the existing, unrelated `_discover_register` mechanism; this file is
the essay half that mechanism does not reach**, which is exactly the shape
`_AUDIT_CLOSURE_CENSUS_EXCEPTIONS`'s own comment (§1(a) above) names: *"the pilot's findings
essay, not the adoption's record."*

## 2. Ruled

| File | Destination | Why |
|---|---|---|
| `docs/audit/nt-0019-verification-and-impact-sweep.md` | **`research/`, `RS-`, `kind: audit`, `owner: auditor`** | §1(e): content is a dispatched audit with method and evidence, matching `RS`'s unit and kind vocabulary directly; corroborated, not established, by its self-title |
| `docs/audit/ruling-acceptance-item-sweep.md` | **`research/`, `RS-`, `kind: audit`, `owner: auditor`** | Same as above; additionally corrects two named rulings' figures with a re-runnable method, which is exactly what an `audit`-kind `RS-` is for |
| `docs/audit/work/nt-0010-0011-adoption/pilot-findings.md` | **`findings/`, as the essay half of `FD-`-migrated finding F28** | §1(g): cited by `docs/audit/register.md:70` as F28's own disposition trail; `_AUDIT_CLOSURE_CENSUS_EXCEPTIONS`'s own comment names it "the pilot's findings essay" |

**No halt.** Every file reaches a destination among §1.4's four plus retirement, each on
evidence rather than a stretch to avoid the halt; retirement is affirmatively excluded by
citation count (§1d) for all three before content was read at all.

## 3. What it obliges

- `_discover_research` (or its equivalent, once `RS` migration code reaches legacy files
  outside `docs/research/`) must place `nt-0019-verification-and-impact-sweep.md` and
  `ruling-acceptance-item-sweep.md` as `RS-` drafts, `kind: audit`, `owner: auditor`, `was:`
  each file's current path.
- `pilot-findings.md` is placed as the essay half of the `FD-` draft `_discover_findings`
  (F95's own scope) must also produce for register row **F28** — not a new, separate
  finding, and not folded into any of the 31 `docs/audit/findings/F*.md` essays, which is a
  different population.
- This ruling does not build any of the three placements; it rules the target each must
  reach, per delegation §1's own framing (rule the classification, the lead draws the
  consequence for the run).

## 4. The option not taken, priced, per file

| File | Alternative | Cost |
|---|---|---|
| Files 1 & 2 | `process/` (Reference), by weaker analogy to `retrofit-impossible.md`/`security-posture.md` | Wrong unit: Reference is *"a living or generated document"* (`:42`) with no id and no frozen mutability; both files are frozen, dated, auditor-verdict records — exactly `RS`'s *"frozen"* mutability (`:39`), not Reference's. Filing them as Reference would strip the `id:`/`created:`/`owner:` header §1.5 requires of every `RS-` and lose the audit trail's own governance weight. |
| Files 1 & 2 | Retirement with `REDIRECTS.csv`, on the reading that a sweep's job is done once read | Closed by evidence, not preference: §1(d) shows both are actively cited by other live governance documents (a plan, the audit README, a companion script) — retiring a cited document leaves those citations dangling, which is exactly what `REDIRECTS.csv`/`was:` exist to prevent for a *moved* document, not license for a *removed* one that is still in use. |
| File 3 | `research/`, `RS- kind: audit`, by the same content-shape reasoning as files 1 & 2 | Wrong on the evidence, not merely a weaker fit: `pilot-findings.md` does not self-title as an audit record and its own citing document (`register.md:70`) names it as a finding's essay, not a sweep — following files 1/2's pattern here would be exactly the "pattern-fit is not a cell" trap §1(f) warns against, applied to a file where the pattern does not even hold. |
| File 3 | A new, standalone finding (its own `F<n>`) rather than F28's essay | Duplicates governance already on record: F28 exists, is open, and already names this file as its evidence in the register's own words. A new finding would be the second copy `NT-0003` exists to prevent. |

## Acceptance Standard

The violation this record must make detectable: **any of the three files stamped a family
this ruling does not name, or the `none` count including any of the three after this ruling's
destinations are built.**

### Acceptance — the violation that must become detectable

1. *Violation: `nt-0019-verification-and-impact-sweep.md` or `ruling-acceptance-item-sweep.md`
   placed under any family other than `RS-`, or with any `kind:` other than `audit`.*
2. *Violation: `pilot-findings.md` placed as a standalone document family, or as part of a
   `docs/audit/findings/F*.md`-sourced `FD-` draft rather than F28's own.*
3. *Violation: any of the three retired (a `REDIRECTS.csv` row with no corresponding
   placement) rather than placed.* §1(d)'s citation count rules retirement out for all three.
4. *Violation: the destination for files 1 or 2 justified in a future record by title alone,
   without the content evidence §1(e) states.* The distinction in §1(f) exists so this cannot
   happen silently.
5. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
