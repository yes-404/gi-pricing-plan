# File census — NT-0016 Stage 0

`docs/plans/2026-08-31-nt-0016-investigation.md` §7 (Slice 2). This is the evidence NT-0016's
Q1, Q2 and Q3 need: one row per tracked file, over a corpus that is stated rather than
implied, produced by `scripts/file-census.py`.

## The artifact

`docs/audit/file-census-b2fb122.csv` — **1317 data rows**, one per tracked file, header
`path,area,name_pattern,size_bytes,mutability,referenced_by`.

## The tree

**Commit `b2fb122`** — `b2fb122a3aeae34f68f26786a5a7dadb5d2045d5`, `main`'s tip at
2026-08-31, the commit this slice's branch was cut from
(`fix(reporter): get_eta accepts GB-local stamps and strips its own Headline label (#530)`).

The census documents that commit's tree specifically — **not** the commit that adds this
script, its test, and these two census artifacts. That is a deliberate, non-circular choice
rather than an oversight: a file cannot truthfully embed the hash of the commit that first
introduces it (the hash is a function of the tree, which would have to include the file
naming its own not-yet-computed hash). `b2fb122` is a concrete, already-existing, independently
checkable commit — the same citation style `docs/plans/2026-08-31-nt-0016-investigation.md`
§1 uses for `b551060` — so anyone can verify this census without depending on this PR's own
eventual squash-merge commit identity. Consequently, `scripts/file-census.py`,
`tests/test_file_census.py`, this document and the CSV itself are **not** part of the 1317
rows: they postdate the stated tree by construction.

## The corpus rule

The corpus is **`git -C <root> ls-files -z`**, never a working-tree walk (`find`,
`grep -r --exclude-dir=.git`). §1 of the investigation plan measured the difference: a
working-tree walk in this repository picks up `.venv/`, `graphify-out/` and `node_modules/`
when they exist locally — directories that are not tracked and differ between two checkouts
of the same commit. `git ls-files` reads the index, so it reproduces from a stated commit
regardless of which machine or checkout runs it; a working-tree census does not, which is
disqualifying for something meant to stand as evidence.

Row count equals `git ls-files | wc -l` at commit `b2fb122`: **1317**, confirmed by checking
out that commit and running `git ls-files | wc -l` directly.

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

  At commit `b2fb122`: **1108 `unknown`, 137 `frozen`, 61 `generated`, 11 `living`** (1317
  total). The large `unknown` count is expected and is itself a Stage 1 input, not a defect
  in this script — most of `.claude/` (429 of the 1317 tracked files, the largest single
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

## Per-area counts at `b2fb122` (top areas)

| area | files |
|---|---|
| `.claude` | 429 |
| `docs` | 253 |
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
git worktree add /tmp/census-check b2fb122a3aeae34f68f26786a5a7dadb5d2045d5
python3 scripts/file-census.py --root /tmp/census-check --out /tmp/c.csv
diff /tmp/c.csv docs/audit/file-census-b2fb122.csv
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
