# Ruling 59 — NT-0016 Slice 2's census CSV and FR-DATA-32: the test is overbroad, the
requirement is not (2026-09-01)

**What this is.** PR #537 (`exec-nt-0016-slice2-file-census`, NT-0016 Slice 2, plan
[`2026-08-31-nt-0016-investigation.md`](2026-08-31-nt-0016-investigation.md) §7) added
`docs/audit/file-census-5ef559d.csv` under an **accepted** plan (`f57d335`, "NT-0016
investigation plan accepted as filed, 2026-09-01"). `python.yml` on that PR is red:

```
backend/tests/test_lineage.py:644
test_no_reference_rows_are_bundled_in_the_repository  [FR-DATA-32]
AssertionError: unexpected bundled data: [PosixPath('docs/audit/file-census-5ef559d.csv')]
```

Per `CLAUDE.md` §0, this is ruled rather than quietly patched either way. This record rules
it. It does not implement anything: `backend/tests/test_lineage.py` is unedited by this
record, per this role's charter and the dispatch that opened this decision point.

## Acceptance Standard

The testable definition of "done" for this ruling record:

1. `git grep -c "^## Ruling 59" docs/plans/2026-09-01-nt-0016-slice2-fr-data-32-ruling.md`
   returns `1`, and `git grep -n "^## Ruling " docs/plans/` shows 59 filling the gap
   immediately after Ruling 58 (`2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md`) with no
   duplicate and no skip.
2. §2 below names both the chosen resolution and the two rejected ones, each with the
   evidence that separated them, before any implementation detail is stated.
3. §3 states, precisely enough for an executor to implement without further judgement calls,
   what the carve-out predicate must check and what it must NOT accept as sufficient (a bare
   path/directory allowlist).
4. §4 states a broken-input case the resolution must still catch, in a form an executor can
   turn directly into a test: a file under the same reserved location that is **not**
   reproducible from any registered generator must still fail
   `test_no_reference_rows_are_bundled_in_the_repository`.
5. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
6. `git grep -nE '\bFR-[A-Z]+-[0-9]|\bNFR-[A-Z]+-[0-9]|\bOQ-[A-Z]+-[0-9]|\bADR-[0-9]'
   docs/plans/2026-09-01-nt-0016-slice2-fr-data-32-ruling.md` returns matches only to
   `FR-DATA-32` itself (the requirement under discussion) — no new requirement id is minted
   and §5 states explicitly that no spec amendment follows from this ruling.
7. `git diff --stat <merge-base>..<branch> -- docs/` names exactly this one new file under
   `docs/plans/` — no frozen plan is edited, and `docs/specs/01-data-management.md` is
   untouched.

---

## 1. Verified first, at `5ef559d` (`origin/main`, fetched immediately before this record)

| Claim | Verdict |
|---|---|
| PR #537 is open, its `python` check is `FAILURE`, `docs` check is `SUCCESS` | **Confirmed** — `gh pr view 537`: `ruff · mypy · import-linter · pytest` conclusion `FAILURE`, `specification audit` conclusion `SUCCESS` |
| FR-DATA-32's text is about **loaders for named UK reference sets** and licence-gated redistribution, not about generated repository metadata | **Confirmed** — `docs/specs/01-data-management.md:179`: "ships **loaders** for the common UK reference sets: ONS postcode directory, ABI vehicle group tables, occupation/industry code lists, and a bank-holiday calendar... Actual rows are shipped only where the licence is unambiguously permissive... ABI vehicle group tables are never shipped" |
| No reference-loader output directory exists yet anywhere in the tree — not even for the two OGL (shippable) sources | **Confirmed** — `backend/src/app/data/reference_loaders.py` defines `Licence`, `ReferenceLoader`, `LOADERS`, `may_ship_data`; no code path writes a data file, and `find backend -iname "*.csv" -o -iname "*.parquet"` (excluding `.venv`) returns nothing. `may_ship_data` is a metadata predicate on a `ReferenceLoader`, not a bundled artifact |
| The test's own docstring already draws the exemption this ruling turns on | **Confirmed** — `backend/tests/test_lineage.py:600-613`: "FR-DATA-32 is about UK *reference* sets whose rows are not ours to redistribute, not about a third-party payload committed under its own licence. So the exemption is bought by that licence: a skill may carry data only while its LICENSE travels with it in the same directory... Delete the licence and this fails, which is the point." |
| The test's predicate is a repo-wide extension sweep with no awareness of provenance | **Confirmed** — `test_lineage.py:631-643`: `root.rglob(pattern)` over `*.csv`, `*.parquet`, `*.xlsx`, excluding only `.venv`, `.git`, and `licensed_vendored_skill` paths |
| Slice 2's CSV is generated from `git ls-files`, carries no reference-set content, and its own plan states it must reproduce byte-for-byte at its own tree | **Confirmed** — plan §7: "The corpus is `git ls-files`... Re-running the script at the same commit reproduces the committed CSV byte for byte" (acceptance item 3); header is `path,area,name_pattern,size_bytes,mutability,referenced_by` — file metadata about this repository's own tracked files, not reference-set rows |
| Slice 3's artifact (`docs/audit/file-taxonomy-draft.md`) does not recur this problem | **Confirmed** — plan §8: `.md`, not matched by the `*.csv`/`*.parquet`/`*.xlsx` sweep |
| This class already has a named precedent in the register | **Confirmed** — `docs/audit/findings/F66.md`: "a syntactic proxy used where a semantic distinction... was needed, and the proxy was never scoped to make that distinction," citing `a3b9c9e` as the prior instance of the same shape. Grepped `docs/audit/register.md` for `FR-DATA-32`, `file-census`, `test_no_reference_rows`: no existing row names this specific conflict — it is not already filed, so this ruling is not a duplicate |

## 2. Ruled

**Is `docs/audit/file-census-5ef559d.csv` within FR-DATA-32's scope? No.**

**Chosen: (b) — add a second conditional carve-out, alongside the existing licensed-vendored-
skill one, bought by provable reproducibility from the tracked corpus rather than by
directory location alone.**

**Rejected: (a) — narrow the test's scan root to match FR-DATA-32 literally.** Rejected
because there is currently nothing to narrow it *to*: no reference-loader output directory
exists anywhere in the tree, not even for the two OGL sources FR-DATA-32 already permits to
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
and have it silently exempted forever, which is precisely the failure FR-DATA-32 exists to
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
2. **Actual regeneration, not a claim.** For a candidate, the test invokes the registered
   generator script (loaded the way Slice 2's own `tests/test_file_census.py` loads
   `scripts/file-census.py` — by path, via `importlib.util.spec_from_file_location`, since
   the hyphenated filename is not import-name-clean) against the current tree, and diffs
   its output byte-for-byte against the committed file's content.
3. **Exemption fires only on an exact match.** A candidate that matches a registered
   filename pattern but does **not** reproduce byte-for-byte is *not* exempted — it falls
   through to the existing `assert data_files == []` and fails the test, exactly as
   unregistered bundled data does today.
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

Per `CLAUDE.md` §13, a carve-out that has never printed a failure has not been tested. The
executor must demonstrate, as a test on a synthetic fixture (mirroring
`tests/test_file_census.py`'s own synthetic-tree pattern, not the live repository — the live
sweep is an integration-style check over the real tree and cannot host a deliberately-broken
fixture inside itself):

- A file at a path matching the registered pattern (e.g.
  `docs/audit/file-census-abc1234.csv`) whose **content is not** what
  `scripts/file-census.py` would produce for that fixture tree (e.g. a hand-written CSV
  simulating a genuinely bundled ABI/ONS extract, or simply the wrong header) is **still
  reported by `generated_from_tracked_corpus` as not exempt**, and a whole-tree sweep over a
  fixture containing only that file still asserts `data_files == [that path]` — i.e. the
  test fails exactly as it does today for real bundled data.
- The genuine, actually-reproducible census file continues to pass (the positive control),
  so the proof is a contrast, not a single assertion — per the standing rule that a positive
  control must exercise the same predicate the guard fires on, not an easier case.

This is the executor's task, filed here as the acceptance condition the fix is not done
without; it is not performed by this ruling record.

## 5. Spec amendment: not needed

FR-DATA-32's text already scopes itself correctly — "loaders for the common UK reference
sets," an enumerated list, licence-gated. Nothing in it purports to govern generated
repository metadata, and nothing about this conflict shows the requirement's substance is
wrong. The disagreement is between the **enforcement mechanism** (a file-extension sweep
with no provenance awareness) and its **own cited requirement**, not between the requirement
and what the platform should do — the same shape `docs/audit/findings/F66.md` already names
for `audit-docs.py` check 1 ("a syntactic proxy used where a semantic distinction... was
needed"). No requirement id is amended, appended to, or superseded by this ruling.

One thing this ruling deliberately does **not** decide, because it is a different question:
whether the repository wants a *separate*, general "no unreviewed data files anywhere"
hygiene guard, independent of FR-DATA-32's licensing concern. If that is wanted, it is a new
requirement (or NFR) with its own spec-change slice, not a reading of FR-DATA-32 — raising it
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
  actually reach, there is nothing left in FR-DATA-32's text for an amendment to fix.

No other part of the dispatch was found wrong. The F66 analogy holds on independent
re-reading of both texts, not only on the dispatch's say-so.
