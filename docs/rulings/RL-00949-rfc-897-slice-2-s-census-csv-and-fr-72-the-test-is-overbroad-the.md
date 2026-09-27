---
id: RL-949
family: ruling
title: RFC-897 Slice 2's census CSV and FR-72: the test is overbroad, the
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-01
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-01-nt-0016-slice2-fr-data-32-ruling.md
---

# RL-949 — RFC-897 Slice 2's census CSV and FR-72: the test is overbroad, the
requirement is not (2026-09-01, corrected before merge 2026-09-01 — see §7)

**What this is.** PR #537 (`exec-nt-0016-slice2-file-census`, RFC-897 Slice 2, plan
[`../plans/PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md`](../plans/PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md) §7) added
`docs/research/file-census-5ef559d.csv` under an **accepted** plan (`f57d335`, "RFC-897
investigation plan accepted as filed, 2026-09-01"). `python.yml` on that PR is red:

```
backend/tests/test_lineage.py:644
test_no_reference_rows_are_bundled_in_the_repository  [FR-72]
AssertionError: unexpected bundled data: [PosixPath('docs/research/file-census-5ef559d.csv')]
```

Per `CLAUDE.md` §0, this is ruled rather than quietly patched either way. This record rules
it. It does not implement anything: `backend/tests/test_lineage.py` is unedited by this
record, per this role's charter and the dispatch that opened this decision point.

## Acceptance Standard

The testable definition of "done" for this ruling record:

1. `git grep -c "^## RL-949" docs/rulings/RL-00949-rfc-897-slice-2-s-census-csv-and-fr-72-the-test-is-overbroad-the.md`
   returns `1`, and `git grep -n "^## Ruling " docs/plans/` shows 59 filling the gap
   immediately after RL-948 (`2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md`) with no
   duplicate and no skip.
2. §2 below names both the chosen resolution and the two rejected ones, each with the
   evidence that separated them, before any implementation detail is stated.
3. §3 states, precisely enough for an executor to implement without further judgement calls,
   what the carve-out predicate must check and what it must NOT accept as sufficient (a bare
   path/directory allowlist).
4. §4 states three broken-input cases the resolution must still catch, in a form an
   executor can turn directly into tests: a file matching the registered pattern whose
   content does not match its named tree, and a file naming an unresolvable tree, must both
   still fail `test_no_reference_rows_are_bundled_in_the_repository` — never a silent
   exemption in either case.
5. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
6. `git grep -nE '\bFR-[A-Z]+-[0-9]|\bNFR-[A-Z]+-[0-9]|\bOQ-[A-Z]+-[0-9]|\bADR-[0-9]'
   docs/rulings/RL-00949-rfc-897-slice-2-s-census-csv-and-fr-72-the-test-is-overbroad-the.md` returns matches only to
   `FR-72` itself (the requirement under discussion) — no new requirement id is minted
   and §5 states explicitly that no spec amendment follows from this ruling.
7. `git diff --stat <merge-base>..<branch> -- docs/` names exactly this one new file under
   `docs/plans/` — no frozen plan is edited, and `docs/specs/01-data-management.md` is
   untouched.

---

## 1. Verified first, at `5ef559d` (`origin/main`, fetched immediately before this record)

| Claim | Verdict |
|---|---|
| PR #537 is open, its `python` check is `FAILURE`, `docs` check is `SUCCESS` | **Confirmed** — `gh pr view 537`: `ruff · mypy · import-linter · pytest` conclusion `FAILURE`, `specification audit` conclusion `SUCCESS` |
| FR-72's text is about **loaders for named UK reference sets** and licence-gated redistribution, not about generated repository metadata | **Confirmed** — `docs/specs/01-data-management.md:179`: "ships **loaders** for the common UK reference sets: ONS postcode directory, ABI vehicle group tables, occupation/industry code lists, and a bank-holiday calendar... Actual rows are shipped only where the licence is unambiguously permissive... ABI vehicle group tables are never shipped" |
| No reference-loader output directory exists yet anywhere in the tree — not even for the two OGL (shippable) sources | **Confirmed** — `backend/src/app/data/reference_loaders.py` defines `Licence`, `ReferenceLoader`, `LOADERS`, `may_ship_data`; no code path writes a data file, and `find backend -iname "*.csv" -o -iname "*.parquet"` (excluding `.venv`) returns nothing. `may_ship_data` is a metadata predicate on a `ReferenceLoader`, not a bundled artifact |
| The test's own docstring already draws the exemption this ruling turns on | **Confirmed** — `backend/tests/test_lineage.py:600-613`: "FR-72 is about UK *reference* sets whose rows are not ours to redistribute, not about a third-party payload committed under its own licence. So the exemption is bought by that licence: a skill may carry data only while its LICENSE travels with it in the same directory... Delete the licence and this fails, which is the point." |
| The test's predicate is a repo-wide extension sweep with no awareness of provenance | **Confirmed** — `test_lineage.py:631-643`: `root.rglob(pattern)` over `*.csv`, `*.parquet`, `*.xlsx`, excluding only `.venv`, `.git`, and `licensed_vendored_skill` paths |
| Slice 2's CSV is generated from `git ls-files`, carries no reference-set content, and its own plan states it must reproduce byte-for-byte at its own tree | **Confirmed** — plan §7: "The corpus is `git ls-files`... Re-running the script at the same commit reproduces the committed CSV byte for byte" (acceptance item 3); header is `path,area,name_pattern,size_bytes,mutability,referenced_by` — file metadata about this repository's own tracked files, not reference-set rows |
| Slice 3's artifact (`docs/research/RS-00953-file-taxonomy-draft-rfc-897-stage-1.md`) does not recur this problem | **Confirmed** — plan §8: `.md`, not matched by the `*.csv`/`*.parquet`/`*.xlsx` sweep |
| §3 point 2 as originally filed ("regenerate... against the current tree") is itself broken, independent of any future merge | **Confirmed, independently, 2026-09-01, correcting this record** — cloned the repo fresh, checked out PR #539's branch tip `aace8d6`, ran `scripts/file-census.py --out` bare (i.e. against "the current tree" as originally worded): 1324 rows, not 1320 — `diff` is non-empty. The PR's own checkout already contains `scripts/file-census.py`, `tests/test_file_census.py`, `docs/research/RS-00952-file-census-rfc-897-stage-0.md` and the CSV itself, none of which existed at `5ef559d`, so "the current tree" is never the tree the filename names, not even at the moment the PR is opened. The companion document already states this in words (`docs/research/RS-00952-file-census-rfc-897-stage-0.md`: "they postdate the stated tree by construction"); this confirms it against the artifact rather than the document describing it |
| Regenerating at the **named** tree reproduces byte-for-byte, and the cheaper path-list check agrees | **Confirmed, independently** — `git worktree add /tmp/census-check 5ef559d...` then `scripts/file-census.py --root /tmp/census-check --out` diffs empty against the committed CSV (byte-identical, 1319 rows); `git -C /tmp/census-check ls-tree -r --name-only 5ef559d...` sorted, diffed against the CSV's `path` column sorted, also empty (1319/1319) |
| A shallow CI checkout cannot resolve an ancestor SHA locally, and a targeted fetch can | **Confirmed, independently** — `.github/workflows/python.yml` sets no `fetch-depth`, so `actions/checkout@v4`'s documented default (`1`) applies; reproduced locally with `git clone --depth 1`: `git rev-parse --verify 5ef559d...^{commit}` exits `1` (unresolvable) before a fetch, and `git fetch --depth 1 origin 5ef559d...` then resolves it via `FETCH_HEAD` with the correct 1319-entry tree. A fetch-by-SHA against GitHub's own hosted remote depends on `uploadpack.allowAnySHA1InWant`/`allowReachableSHA1InWant`, on by default for github.com; not independently re-verified against github.com itself in this session, only against a local `file://` remote, which is a strictly easier case — flagged rather than asserted as fact for the CI-hosted case |
| This class already has a named precedent in the register | **Confirmed** — `docs/findings/FD-00954-audit-docs-py-check-1-s-link-checker-has-no-code-span-awareness.md`: "a syntactic proxy used where a semantic distinction... was needed, and the proxy was never scoped to make that distinction," citing `a3b9c9e` as the prior instance of the same shape. Grepped `docs/findings/register.md` for `FR-72`, `file-census`, `test_no_reference_rows`: no existing row names this specific conflict — it is not already filed, so this ruling is not a duplicate |

## 2. Ruled

**Is `docs/research/file-census-5ef559d.csv` within FR-72's scope? No.**

**Chosen: (b) — add a second conditional carve-out, alongside the existing licensed-vendored-
skill one, bought by provable reproducibility from the tracked corpus rather than by
directory location alone.**

**Rejected: (a) — narrow the test's scan root to match FR-72 literally.** Rejected
because there is currently nothing to narrow it *to*: no reference-loader output directory
exists anywhere in the tree, not even for the two OGL sources FR-72 already permits to
ship. A directory-scoped rewrite today would either fail to compile against a real path, or
scope to an empty set and pass vacuously — which is the exact "empty census reads as a clean
repository" failure mode Slice 2's own plan calls out as the one that matters
(`2026-08-31-nt-0016-investigation.md` §7, Step 5). It would also give up real protection:
the guard's stated value ("this is the test that says so before a licence holder does") is
that it catches a reference-set drop *anywhere* in the tree, including a scratch export or a
mis-placed unzip nobody thought to gitignore — not only inside a designated directory. A
narrower scan answers today's false positive by creating tomorrow's false negative, in
exchange for nothing: it does not even fix the immediate case, since the census is
legitimately produced under `docs/audit/`, a directory a narrowed scan would still have to
either include (defeating the narrowing) or exclude by the same allowlist-by-location
reasoning rejected below.

**Rejected: (c) — change the artifact's format so it stops matching `*.csv`.** Rejected on
the dispatch's own stated grounds, verified rather than assumed: the plan's §7 Interfaces
section requires "a CSV whose header is exactly `path,area,name_pattern,size_bytes,
mutability,referenced_by`" as an **accepted, frozen** plan clause — changing the format to
dodge a mis-scoped guard would mean editing a frozen plan to route around a defect that is
not in the plan, which `CLAUDE.md` §12 already forbids regardless of this ruling. It also
does not answer the class: the next generated tabular artifact — another re-census at a
later tree, or a future audit script's CSV output — hits the identical wall the moment it is
committed, so (c) is a per-file dodge repeated indefinitely rather than a rule.

### Why (b) and not a bare path allowlist

The dispatch is right to be suspicious of "a path allowlist that rots," and the existing
vendored-skill carve-out is not actually a location check — the exemption fires on the
**presence of a positive, checkable fact** (a `LICENSE`/`LICENSE.txt` file in the same
directory), not on the directory name itself; the test's own comment makes the point
explicit ("delete the licence and this fails"). A `docs/audit/` location check alone would
be weaker than that precedent: anyone could drop an actual ABI extract under `docs/audit/`
and have it silently exempted forever, which is precisely the failure FR-72 exists to
prevent.

The equivalent positive, checkable fact for a generated repository self-census is
**reproducibility**: Slice 2's plan already requires, as an executable acceptance
criterion, that re-running `scripts/file-census.py` at the same commit reproduces the
committed CSV byte for byte. That is a fact about the file's *provenance*, not its location,
and it cannot be satisfied by real reference-set rows — real ABI or ONS data does not equal
the output of a script that walks `git ls-files` and writes `path,area,name_pattern,
size_bytes,mutability,referenced_by`. "Delete the correspondence [substitute the file's
content for anything the generator would not itself produce] and this fails" is the same
shape as "delete the licence and this fails," and it is what makes this carve-out narrow
rather than a rotting allowlist.

## 3. What the carve-out must check, precisely

An executor implementing this (not this record) adds, alongside `licensed_vendored_skill`,
a second predicate — call it `generated_from_tracked_corpus` — with these properties, all of
which must hold together:

1. **A closed, explicit registry**, not a directory prefix. A small tuple/mapping in the
   test module of `(generator script path, filename pattern the generator owns)` —
   initially exactly one entry: `("scripts/file-census.py",
   re.compile(r"^docs/audit/file-census-[0-9a-f]{7,40}\.csv$"))`. A candidate file is a
   carve-out *candidate* only if its path matches some registered pattern; everything else
   still goes through the unmodified whole-tree sweep.
2. **Verified against the tree the filename names, never "the current tree."**
   `docs/audit/file-census-<sha>.csv` documents commit `<sha>`'s tree specifically — never
   the tree of whatever commit `pytest` happens to be running at. **This binds the original
   wording of this point, filed 2026-09-01 and corrected the same day before merge**: "the
   current tree" is wrong even for the PR that introduces the file, because that checkout
   already contains the generator script, its test, and the census's own companion
   document — none of which existed at `5ef559d` and all of which the census correctly
   excludes (`docs/research/RS-00952-file-census-rfc-897-stage-0.md`: "they postdate the stated tree by construction").
   Verified directly: regenerating bare inside PR #539's own branch tip produces 1324 rows
   against the committed 1320 — not a future-merge risk, a same-PR one. Every future merge
   to `main` only widens the gap.

   The registered pattern already captures the tree as its own capture group
   (`[0-9a-f]{7,40}` inside `file-census-(?P<sha>[0-9a-f]{7,40})\.csv$`); the check
   resolves against **that** commit, not `HEAD`:

   - Attempt local resolution first: `git rev-parse --quiet --verify "<sha>^{commit}"`.
   - If that fails, attempt `git fetch --depth 1 origin <sha>` and retry resolution against
     `FETCH_HEAD`. Verified mechanically against a local shallow clone (`git clone --depth
     1`): the ancestor SHA is unresolvable before the fetch and resolves correctly,
     1319-entry tree included, after it. `actions/checkout@v4` in this workflow sets no
     `fetch-depth`, so its documented default (a single-commit shallow clone) applies — the
     fetch step is not defensive padding, it is required on every ordinary CI run of this
     test, not only a hypothetical one.
   - **If resolution still fails after the fetch attempt, the test fails outright** —
     naming the unresolved SHA and the file — and the candidate is **not** exempted. A
     carve-out that falls back to "cannot verify, so allow it" is a carve-out satisfied by
     absence, the failure class this repository already keeps re-finding; this design
     refuses that fallback by construction rather than by discipline.
   - Once the commit resolves: `git ls-tree -r --name-only <sha>`, sorted, compared against
     the CSV's own `path` column, sorted, for **exact equality of the full list** — not a
     set (a set would hide a duplicated or dropped row). The header row is checked
     separately against the exact string `path,area,name_pattern,size_bytes,mutability,
     referenced_by` from §7's Interfaces contract.
   - **This checks the property FR-72 actually cares about — provenance of rows — and
     deliberately stops there.** It does not re-derive `area`, `name_pattern`, `mutability`
     or `referenced_by`; those are Slice 2's own correctness, already the subject of
     `tests/test_file_census.py`'s byte-for-byte acceptance criterion (plan §7, item 3), and
     re-deriving them here would run the same expensive full-repo `referenced_by` content
     scan a second time, for a purpose (licensing) that a wrong `mutability` guess cannot
     touch. Real reference-set rows (ONS postcode, ABI vehicle groups, occupation codes)
     cannot satisfy "the `path` column, sorted, equals `git ls-tree -r --name-only <sha>`,
     sorted" for any resolvable `<sha>` in this repository's history, which is the fact that
     matters for this requirement.
3. **Exemption fires only on an exact match.** A candidate that matches a registered
   filename pattern but whose header or sorted `path` column does **not** exactly equal the
   named tree's (point 2) is *not* exempted — it falls through to the existing
   `assert data_files == []` and fails the test, exactly as unregistered bundled data does
   today. (Amended with point 2, §7: the match is against the named tree's `git ls-tree`
   output, not a byte-for-byte regeneration of the whole file.)
4. **Nothing about this predicate may be satisfied by a file's location or name alone.**
   The filename-pattern match in point 1 only narrows which files are even *offered* the
   chance to prove reproducibility; it never itself grants the exemption. This is the
   difference from a bare allowlist, and it is the property to test for in review: a
   reviewer should be able to construct a file that matches the registered pattern and is
   real reference data, and watch the test still catch it (§4).
5. **The registry is maintained going forward**, the same way `.claude/skills/README.md`
   records each vendored skill's carve-out — a new generated tabular artifact under
   `docs/audit/` (or anywhere else) is added to the registry in the same PR that introduces
   its generator, never assumed to be covered by an existing entry.

## 4. Broken-input proof this resolution must be provable against

Per `CLAUDE.md` §13, a carve-out that has never printed a failure has not been tested. Three
cases, all against a synthetic fixture git repository (mirroring
`tests/test_file_census.py`'s own synthetic-tree pattern, not the live repository — the
whole-tree sweep is an integration-style check over the real tree and cannot host a
deliberately-broken fixture inside itself, and the live repository's own history should not
be mutated to manufacture a bad commit):

- **Positive control.** A file whose name matches the registered pattern and whose `path`
  column, sorted, genuinely equals `git ls-tree -r --name-only <sha>`, sorted, at a real
  commit in the fixture repo's own history is exempted, and the whole-tree sweep passes.
  Verified for the real artifact independently in this session (§1): the committed
  `file-census-5ef559d.csv`'s path column matches `git ls-tree -r --name-only 5ef559d...`
  exactly, 1319/1319.
- **Mismatched content, resolvable SHA.** A file matching the registered pattern, naming a
  commit that *does* resolve in the fixture repo, but whose `path` column diverges from that
  commit's `git ls-tree` (e.g. rows describing an ABI vehicle-group table, or the fixture
  tree's own generator/test files spliced in the way the real "current tree" mistake would
  produce) is **not** exempted, and the whole-tree sweep still reports it in
  `data_files` — the test fails exactly as it does today for real bundled data.
- **Unresolvable SHA.** A file matching the registered pattern but naming a commit absent
  from the fixture repo and unreachable by fetch (no matching remote, or a remote lacking
  that object) causes the **test itself to fail** naming the unresolved SHA — never a silent
  exemption and never a silent pass-through. This is the case the "fetch-then-hard-fail"
  design in §3 point 2 exists for, and it is the one the dispatch's own "carve-out satisfied
  by absence" warning is about; it needs its own assertion, not only the other two.

All three are the executor's task, filed here as the acceptance condition the fix is not
done without; none is performed by this ruling record.

## 5. Spec amendment: not needed

FR-72's text already scopes itself correctly — "loaders for the common UK reference
sets," an enumerated list, licence-gated. Nothing in it purports to govern generated
repository metadata, and nothing about this conflict shows the requirement's substance is
wrong. The disagreement is between the **enforcement mechanism** (a file-extension sweep
with no provenance awareness) and its **own cited requirement**, not between the requirement
and what the platform should do — the same shape `docs/findings/FD-00954-audit-docs-py-check-1-s-link-checker-has-no-code-span-awareness.md` already names
for `audit-docs.py` check 1 ("a syntactic proxy used where a semantic distinction... was
needed"). No requirement id is amended, appended to, or superseded by this ruling.

One thing this ruling deliberately does **not** decide, because it is a different question:
whether the repository wants a *separate*, general "no unreviewed data files anywhere"
hygiene guard, independent of FR-72's licensing concern. If that is wanted, it is a new
requirement (or NFR) with its own spec-change slice, not a reading of FR-72 — raising it
here would be inventing scope this ruling was not asked to open. Left unopened rather than
silently decided either way.

## 6. Where I disagree with the dispatch that opened this decision point

The dispatch's reading of the proxy/authority mismatch is correct and is adopted as this
ruling's basis — verified independently against the requirement text, the test's own
docstring, and the actual absence of any reference-loader output directory, not relayed. Two
narrow corrections to how the dispatch framed the options, neither changing its overall
direction:

- The dispatch frames (b)'s existing carve-out as bought by "a LICENSE travelling in the
  same directory" and asks what would buy an equivalent for the census. On inspection the
  LICENSE check is itself a **presence** check, not a validated legal one — the test does
  not read the licence's content, only that a file named `LICENSE`/`LICENSE.txt` exists
  beside the data. A reproducibility check (§3) is not just "equally checkable" as that
  precedent, it is strictly *harder to satisfy by accident or by a careless drop* than the
  precedent it is modelled on, since it requires the file to actually equal a script's
  output rather than merely requiring a second file's presence. Worth stating because the
  dispatch's phrasing ("equally checkable") undersells what's achievable here.
- The dispatch asks whether this "needs a spec change" as a live open question. §5 above
  answers it: no, and the reasoning is that the two rulings (scope, and resolution) are the
  same evidence read twice — once the test is found to cite a requirement it doesn't
  actually reach, there is nothing left in FR-72's text for an amendment to fix.

No other part of the dispatch was found wrong. The F66 analogy holds on independent
re-reading of both texts, not only on the dispatch's say-so.

## 7. Correction, before merge (2026-09-01)

**§3 point 2 as first filed bound reproducibility to "the current tree." That binding was
itself defective**, caught by the lead before merge — not a hypothetical about a future
`main` moving past `5ef559d`, but a same-PR defect: PR #539's own checkout already contains
`scripts/file-census.py`, `tests/test_file_census.py` and `docs/research/RS-00952-file-census-rfc-897-stage-0.md`, none
of which existed at `5ef559d` and all of which the census correctly excludes, so "the
current tree" was never the tree the filename names, not even at the moment the file is
first committed. Left as filed, the carve-out this ruling specifies would never fire and
`test_no_reference_rows_are_bundled_in_the_repository` would stay red permanently —
defeating the point of ruling (b) over (a) or (c) in the first place.

**Independently re-verified before correcting**, not accepted on the strength of the
dispatch alone (this role's charter): cloned the repository fresh, checked out PR #539's
branch tip `aace8d6`, ran `scripts/file-census.py --out` bare — 1324 rows against the
committed 1320, non-empty diff, confirming the defect directly against the artifact rather
than trusting the companion document's account of it. Separately confirmed the corrected
mechanism actually works: `git worktree add` to `5ef559d` reproduces the committed CSV
byte-for-byte, and the cheaper `git ls-tree -r --name-only 5ef559d... | sort` matches the
CSV's sorted `path` column exactly, 1319/1319. Also confirmed the shallow-checkout concern
is real rather than theoretical: `.github/workflows/python.yml` sets no `fetch-depth`, and a
local `git clone --depth 1` cannot resolve `5ef559d` until an explicit `git fetch --depth 1
origin <sha>` is run, after which it resolves correctly — verified against a local `file://`
remote; not independently re-verified against `github.com`'s own SHA-fetch policy in this
session, and §1's evidence table flags that gap rather than silently assuming it away.

**Corrected: §3 point 2 now resolves the named tree (from the filename's own captured SHA)
rather than "the current tree," with an explicit local-resolve-then-fetch procedure and a
hard failure — never a silent exemption — when the commit cannot be resolved even after the
fetch. §4 gained a third proof case (an unresolvable SHA) the original two-case version did
not cover, which is exactly the "carve-out satisfied by absence" failure mode named in the
correction that prompted this.** Everything else in this record — the verdict, the chosen
and rejected limbs in §2, the no-spec-amendment finding in §5, and both corrections to the
dispatch in §6 — is unchanged and re-stands on its original evidence.
