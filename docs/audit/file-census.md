# File census — NT-0016 Stage 0

`docs/plans/2026-08-31-nt-0016-investigation.md` §7 (Slice 2). This is the evidence NT-0016's
Q1, Q2 and Q3 need: one row per tracked file, over a corpus that is stated rather than
implied, produced by `scripts/file-census.py`.

## The artifact

`docs/audit/file-census-5ef559d.csv` — **1319 data rows**, one per tracked file, header
`path,area,name_pattern,size_bytes,mutability,referenced_by`.

## The tree

**Commit `5ef559d`** — `5ef559d5f964eba85eeaa4238c71e4eb20e31f4b`, `main`'s tip at the start
of this slice's Slice 2 execution session, 2026-09-01
(`fix(reporter): log the Slack response and rendered post, not just ok (#536)`).

An earlier census committed by this slice's first (interrupted) pass was generated at
`b2fb122`, main's tip on 2026-08-31. By the time that work resumed, five more PRs had merged
(`#532`–`#536`), so the tracked corpus had changed and the old CSV's row count no longer
equalled `git ls-files | wc -l` at the branch's tree. This document and CSV supersede that
one; the earlier `docs/audit/file-census-b2fb122.csv` was removed rather than kept alongside,
so exactly one census file is ever committed at a time.

The census documents commit `5ef559d`'s tree specifically — **not** the commit that adds this
script, its test, and these two census artifacts. That is a deliberate, non-circular choice
rather than an oversight: a file cannot truthfully embed the hash of the commit that first
introduces it (the hash is a function of the tree, which would have to include the file
naming its own not-yet-computed hash). `5ef559d` is a concrete, already-existing, independently
checkable commit — the same citation style `docs/plans/2026-08-31-nt-0016-investigation.md`
§1 uses for `b551060`. Consequently, `scripts/file-census.py`, `tests/test_file_census.py`,
this document and the CSV itself are **not** part of the 1319 rows: they postdate the stated
tree by construction. (Verified directly: `git grep -c '^scripts/file-census.py,'
docs/audit/file-census-5ef559d.csv` returns 0, and likewise for
`tests/test_file_census.py` and any `docs/audit/file-census` path.)

## The corpus rule

The corpus is **`git -C <root> ls-files -z`**, never a working-tree walk (`find`,
`grep -r --exclude-dir=.git`). §1 of the investigation plan measured the difference: a
working-tree walk in this repository picks up `.venv/`, `graphify-out/` and `node_modules/`
when they exist locally — directories that are not tracked and differ between two checkouts
of the same commit. `git ls-files` reads the index, so it reproduces from a stated commit
regardless of which machine or checkout runs it; a working-tree census does not, which is
disqualifying for something meant to stand as evidence.

Row count equals `git ls-files | wc -l` at commit `5ef559d`: **1319**, confirmed by checking
out that commit in a separate worktree and running `git ls-files | wc -l` directly.

## Column rules

- **`area`** — the first path segment (`rel_path.split("/", 1)[0]`). A root-level file's
  area is its own name (e.g. `README.md`). The script forms no opinion on whether a
  first-segment split is a good cluster boundary; clustering into a taxonomy is Slice 3's, by
  a human reading the CSV — a script that proposed categories would make Slice 3 review its
  own output.
- **`name_pattern`** — the basename with every `\d{4}-\d{2}-\d{2}` run replaced by `DATE`,
  then every remaining run of digits replaced by `N`. E.g.
  `2026-08-29-w11-3-batch-scoring.md` -> `DATE-wN-N-batch-scoring.md`;
  `0016-file-taxonomy.md` -> `N-file-taxonomy.md`.
- **`mutability`** — **a guess, and labelled one.** Derived from directory prefix only, and
  from nothing else — no header marker, front-matter field or content sniff is read, because
  a heuristic that reads well and cannot be checked from the directory prefix alone is
  exactly what this plan forbids inventing:
  - `docs/plans/` and `docs/audit/work/` -> `frozen`
  - `docs/contracts/` -> `generated`
  - `docs/specs/` and `docs/process/` -> `living`
  - everything else -> `unknown`

  At commit `5ef559d`: **1109 `unknown`, 138 `frozen`, 61 `generated`, 11 `living`** (1319
  total). The large `unknown` count is expected and is itself a Stage 1 input, not a defect
  in this script — most of `.claude/` (429 of the 1319 tracked files, the largest single
  `area`) carries no directory-level mutability signal this rule can see, and the plan is
  explicit that inventing one to shrink that number is the wrong move.
- **`referenced_by`** — counts *tracked files whose content contains the target's basename*,
  excluding the target file itself, matched by full path rather than by basename (a sibling
  file that happens to share a basename in a different directory is not excluded from
  referencing, or being referenced by, the target). This over-counts a common basename (a
  `README.md` mentioned inside another file's prose, whether or not it is actually citing
  that particular `README.md`) and under-counts a file cited only by a fuzzy description
  rather than its literal filename. Both are acceptable and neither is silent, because the
  rule is written down here.

## Per-area counts at `5ef559d` (top areas)

| area | files |
|---|---|
| `.claude` | 429 |
| `docs` | 255 |
| `backend` | 237 |
| `frontend` | 211 |
| `packages` | 137 |
| `scripts` | 16 |
| `tests` | 9 |
| `.github` | 6 |
| `examples` | 6 |
| `deploy` | 3 |

(20 areas total; the remainder are single root-level files such as `pyproject.toml`,
`uv.lock`, `README.md`.) Full per-`name_pattern` counts are available via
`python3 scripts/file-census.py --summary` (printed to stderr, not persisted here — the CSV
itself is the artifact of record).

## Reproducing this census

```
git worktree add /tmp/census-check 5ef559d5f964eba85eeaa4238c71e4eb20e31f4b
python3 scripts/file-census.py --root /tmp/census-check --out /tmp/c.csv
diff /tmp/c.csv docs/audit/file-census-5ef559d.csv
git worktree remove /tmp/census-check
```

`--root` targets the historical tree explicitly, rather than relying on the checkout the
script itself happens to run from — the point of naming the tree at all is that the census
does not depend on which commit `scripts/file-census.py` is invoked from.

## Broken-input proof

`scripts/file-census.py` exits `1` with a message naming the cause when `--root` is not a
git repository, rather than emitting an empty CSV — an empty census is indistinguishable from
a genuinely clean repository and would otherwise be committed as evidence of one. Proved
against a real non-git temporary directory as part of this slice's acceptance evidence
(`docs/plans/2026-08-31-nt-0016-investigation.md` §7 Step 5), and covered by
`tests/test_file_census.py::test_non_git_root_exits_non_zero_naming_the_cause` and
`test_cli_subprocess_non_git_root_exits_non_zero`.

## Consumers

Slice 3 (the taxonomy draft) consumes this CSV to build a human-reviewed clustering; this
script and this document take no view on what that clustering should be.
