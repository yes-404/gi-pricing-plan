---
id: FD-1756
family: finding
title: Polars 2 and PyArrow 26 are pending majors of the core data stack (Dependabot #1316 and #1315) and need a library-spike over our data paths before any bump, so they are deferred to Phase 3 under WK-1178
status: active
created: 2026-10-17
owner: auditor
tree: 055b5e6b74f9d4b10f6df54570e33ed2805ae9a8
corrected_by: []
relates: [WK-1178, FD-1240, P3]
---

# FD-1756 — Polars 2 and PyArrow 26: pending majors of the core data stack, spike first, deferred to Phase 3

*(Minted 2026-10-17 as FD-1756 from working id 8078, in the D18 batch mint PR.)*

*(Filed under working id 8078, reserved by the lead in `eta.md` "2026-10-17 11:13:28 BST"; a minter folds it into the next docs batch. Authority: the maintainer's entry "2026-10-17 11:12:48 BST" in `channel/to-lead.md`, the #1315/#1316 bullet, read in full. Every fact below was read on 2026-10-17 from `origin/main` `055b5e6b74f9d4b10f6df54570e33ed2805ae9a8`, from `gh pr view`, PyPI and the GitHub releases API, not from the lead's relay.)*

## Finding

**Severity: MEDIUM, proposed by the auditor (to be ruled).** Why not HIGH: nothing is broken today; the lockfile holds both packages at the last stable majors and CI installs with `--frozen`, so the exposure is conditional on a bump being merged or on a re-resolve. Why not LOW: Polars is the dataframe engine of every data path (`CLAUDE.md` §3: Polars + DuckDB; no pandas), the pins are floors with no ceiling, and a Polars 2 change that alters a result silently on the pricing path would be a mispricing the goldens may not catch. This is a **dependency risk on the pricing path, not a process finding**, so it is a register row here and not a process-backlog row (Lean P2 L3 does not apply).

Dependabot opened two major-version PRs against the core data stack:

| PR | Change | Head SHA | Files |
|---|---|---|---|
| #1315 | `pyarrow` 25.0.1 → 26.0.0 | `5b9a1deb7566fca11d3d30c3749a1a116a973cd7` | `uv.lock` only |
| #1316 | `polars` 1.44.2 → 2.0.0 | `111212019b4813a14d93dea7fe90d093930b41b6` | `uv.lock` only |

Both are authored by `app/dependabot` and OPEN. The maintainer ruled (entry above) that neither is taken in Phase 2: a Polars major 17 days before the 4 Nov code freeze (`docs/roadmap.md:588`, "Code freeze: Wed 2026-11-04") puts every data path at risk. The upgrade is deferred to Phase 3, after the 12 Nov exit demo, under WK-1178, and **requires a `library-spike` run over our data paths before any bump**. Without a record the two PRs would be closed with no owner, and without an `ignore` rule Dependabot re-opens them weekly.

## Evidence

**Where each is pinned** (`git grep -n -E 'polars|pyarrow' -- '*.toml'` at `055b5e6b`):
- `backend/pyproject.toml:19` `"polars>=1.9"`;
- `packages/pricing-core/pyproject.toml:23` `"polars>=1.9"` and `:27` `"pyarrow>=17"`.

All three are **floors with no upper bound**, so `pyproject` permits Polars 2 and PyArrow 26 today; only `uv.lock` holds them back. `uv.lock` resolves `polars` `1.44.2` (`:1654-1655`, with `polars-runtime-32` 1.44.2 at `:1666`) and `pyarrow` `25.0.1` (`:1800-1803`). `duckdb` resolves `1.5.6` (`:492-493`); whether PyArrow 26 and Polars 2.0 interoperate with it on our paths is unverified.

**How many modules import Polars** (predicate: `git grep -l -E '^\s*(import polars|from polars)' -- '*.py'` at `055b5e6b`, files counted): **90 files**. By directory (the same command piped to `awk -F/ '{print $1"/"$2}' | sort | uniq -c`): `packages/pricing-core` 59 (22 under `packages/pricing-core/src`, the rest tests), `backend/tests` 13, `backend/src` 10, `examples/fremtpl2` 3, `scripts/` 5 (`bench-data.py`, `bench-model.py`, `bench-rating.py`, `bench-score-batch.py`, `measure-attribution-cost.py`). Shipped code is 32 files (22 + 10).

**PyArrow has no direct import.** `git grep -l -E '^\s*(import pyarrow|from pyarrow)' -- '*.py'` prints 0 files, and `git grep -n -E 'to_arrow|from_arrow|pyarrow|\.pl\(\)|\.arrow\(\)|to_pandas' -- '*.py'` prints 0 lines. It is a declared dependency (`pricing-core`, `>=17`) used, if at all, through Polars or DuckDB interop. **Which path actually needs it was not traced**; that is the first question for the spike, and "nothing needs it" would change the ask.

**What upstream says (Polars read; PyArrow not read).** PyPI (`https://pypi.org/pypi/polars/json`): `2.0.0rc1` 2026-09-02, `2.0.0rc2` 2026-09-20, `2.0.0` 2026-10-06 (the latest stable is 2.0.0, so #1316 targets the newest release). PyArrow (`https://pypi.org/pypi/pyarrow/json`): `25.0.1` 2026-08-10, `26.0.0` 2026-10-09 (the latest stable, 8 days old at this record). Release notes read from the GitHub releases API for `pola-rs/polars`: tag `py-2.0.0` ("Breaking changes": SQL window functions over grouped rows and QUALIFY order, exact SQL numeric literals typed as Decimal and `%`/DIV truncated, deterministic expression plugins may opt into CSE/CSPE, Parquet ENUM read as `pl.String`, "More map operations", `cut`/`qcut` deprecated); `py-2.0.0-rc.1` (default SQL engine is the streaming engine); `py-2.0.0-rc.2` (also: legacy `POLARS_STREAMING_CHUNK_SIZE` removed, a new `Map` dtype, changed behaviour of DataFrame/LazyFrame functions on 0-width input). That is the union of the three notes' breaking lists, not a claim that it is complete: the release notes are a changelog, not a migration guide, and the rc notes may not repeat items. **PyArrow 26: release notes not read** (`https://arrow.apache.org/release/26.0.0.html`, named by the release body, was not fetched).

**What this repository calls, checked against that list.** `git grep -n -E '\.(cut|qcut)\(|SQLContext|pl\.sql|\.sql\(' -- '*.py'` prints 0 lines at `055b5e6b`, so the named SQL, `cut` and `qcut` changes do not touch a call site we have. Parquet ENUM read, the `Map` dtype, 0-width inputs, Decimal and Float handling, joins, `group_by` ordering and the lazy/streaming engine default are **not checked**; they are what the spike is for. This is a list of candidates, not evidence of compatibility, and not evidence of incompatibility.

**The precedent.** FD-1240 (zen-engine, the rating evaluator, Dependabot #882, major bump, `library-spike` first, deferred with owner WK-1178) is the same shape: a floor or pin verified on one version, a major PR, a spike, an `ignore` rule in `.github/dependabot.yml` (`update-types: ["version-update:semver-major"]`, lines 36-40 at `055b5e6b`). The existing `ignore` entry covers `zen-engine` and `hypothesis`; polars and pyarrow have none.

**Why now is the wrong time.** Phase 2's G1 gate and the 4 Nov code freeze leave no room for a spike plus a fix cycle over 90 importing files; Python CI also carries a known budget problem (the maintainer's entry: python CI cancels at 30 min until SL 8064 merges), so a full-pytest verdict on a Polars major is not obtainable cheaply today. The maintainer's entry says "17 days" to the code freeze; the calendar distance from 2026-10-17 to 2026-11-04 is 18 days, and the conclusion does not depend on the day.

## Disposition

**Proposed by the auditor; the decision is the lead's.**

**deferred with an owner — WK-1178**, Phase 3 (after the 12 Nov exit demo), as ruled by the maintainer in the entry "2026-10-17 11:12:48 BST". Event that confirms or discharges it: a `library-spike` run (the skill's method, wheels fetched without pip, the version pinned exactly) of one named candidate pair, Polars `2.0.x` and PyArrow `26.x`, over our data paths: the 32 shipped importing files' operations (read/ingest, joins, group-bys, the GLM/GBM input frames, rating-table cells), the Parquet and Excel readers, DuckDB/Arrow interop, and the golden tests; a ruling or an ADR addendum records the result; the pins then move as one governed change with `docs/skills-map.md` (the Polars row, line 52) and each spec §8 that names them updated in the same PR (`CLAUDE.md` §10). The spike also decides whether `pyarrow>=17` should stay a declared dependency, and whether `polars>=1.9` should gain a ceiling until then.

Follow-ups the maintainer's entry orders, none done by this record: (1) a small WK-1178 change adding `ignore` entries for `polars` and `pyarrow` with `update-types: ["version-update:semver-major"]` to `.github/dependabot.yml`, with a dated comment naming this record; (2) closing #1315 and #1316 with a comment citing it (reversible with `@dependabot recreate`), **only after this record is minted**, so nothing is unowned.

Ownership shape: event.
