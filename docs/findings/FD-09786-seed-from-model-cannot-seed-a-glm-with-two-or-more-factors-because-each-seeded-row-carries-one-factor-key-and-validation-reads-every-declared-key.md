---
id: FD-9786
family: finding
title: seed_from_model cannot seed a GLM with two or more factors, because each seeded row carries one factor key and validation reads every declared key
status: active
created: 2026-10-01
owner: auditor
tree: 0e2c6a1d7d1539b0f97447c8be43c5931d80cf68
corrected_by: []
relates: [WK-1178, FR-230, FR-228, FR-234]
---

# FD-9786 — seed_from_model cannot seed a GLM with two or more factors

**Filed under working id 9786** by auditor-rl9855, found while auditing the DP-5 ruling (working id 9855) (draft PR #941). The id is minted by the
lead at the merge turn. The `tree:` is the tree of `9b0fb97c`; main's code files are unchanged at `101e32dc`
(`git diff --stat 9b0fb97c 101e32dc -- packages backend` is empty).

## Finding

**Severity: HIGH; owner WK-1178** (the maintainer's ruling of 2026-10-01, which set it provisional HIGH, then MEDIUM on the auditor's reading of the shipped demo, then HIGH again on the reading of "the WF-699 demo path" that the roadmap gives; see "The WF-699 demo path"). FR-230 says a rate table can be seeded from a Model's GLM relativity table.
`seed_from_model` (`packages/pricing-core/src/pricing_core/rate_tables/operations.py:168`) fails for any GLM whose
relativity table has **two or more factors**, which is the ordinary motor or home model. A single-factor model seeds;
every multi-factor model raises `KeyError`.

**Cause.**
- `:191-194` declares one `RateTableKey` per factor, so a two-factor model has two key columns.
- `extract_relativity_table` (`:142`) builds each cell row as `{factor: level.level, value_name: ...}` (`:156`): a row
  carries **its own factor's** key column only.
- `validate_rate_table` (`:269`), which `seed_from_model` calls at `:197`, reads every declared key from every row at
  `:289` (`tuple(row[key] for key in key_names)`). The first row lacks the other factor's column, so it raises
  `KeyError`.
- The same unguarded read is at `:232` (`_value_issue`) and `:327` (`_index_rows`), so a table in that shape would also
  break `diff_vs_previous` and `diff_vs_seed`.
- `validate_rate_table` also demands full Cartesian coverage of the declared key domains (`product(...)`, `:307-318`),
  which a one-way relativity extract can never satisfy. The seeding path was therefore written for a table whose
  rows carry every key, and the extract does not produce one.

**Why HIGH.** The failure is loud, not a silent mispricing: no wrong figure is produced. It is HIGH because FR-230 is
unusable on a multi-factor GLM; the failure is an uncaught `KeyError` rather than a named refusal
(`platform/rate_tables.py:130` catches only `ValueError`, so the route answers 500; read from the code, not run); it
blocks the DP-5 ruling's seeding limb (working id 9855) and PL-1267 Slice 7's seeded red-first test; and, on the maintainer's
reading below, it blocks Phase 2's exit criterion G2. The existing tests all use one factor
(`packages/pricing-core/tests/test_rate_table_operations.py:150`, `_DRIVER_LEVELS`), which is how it passed.

## The WF-699 demo path

**The maintainer's test and ruling (2026-10-01).** The test was "the WF-699 demo path". Phase 2's exit criterion G2
(`docs/roadmap.md:566`, the Exit demo row at `:603`) defines that path as the **documented journey**, "`WF-699` Phases A to E
and its deploy step as one scripted journey". A1 and A2 call seed-from-model for every rateable factor on the seven-factor GLM,
so G2 is blocked. The shipped demo not walking A1 is a demo gap, not a mitigation. **HIGH stands.**

**What the auditor measured first (kept as the record of the shipped demo).** Does the shipped demo seed a rate table from a
GLM with two or more factors through `seed_from_model` / `extract_relativity_table`? **No.** Commands, at `101e32dc`:

```
grep -rniE 'seed-from-model|seed_from_model|extract_relativity_table|rate-tables|rate_table' examples scripts/demo.py
examples/fremtpl2/model.py:323:    "rate_tables": [], "models": [], "reference_tables": [], "custom_objectives": [],
```

The WF-699 journey has no test or script: `grep -rl "WF-699" backend/tests packages scripts frontend/src frontend/tests` prints nothing, so no
journey test reaches the seed path either. The one hit above is an empty pin list (`_EMPTY_PINS`, `model.py:322-324`). `seed.py` and `scripts/demo.py` seed the **dataset** (`fetch.py`,
`last-seed.json`), not a rate table. So the shipped demo does not reach the defect; the journey G2 requires does.

The demo's GLM carries seven identity factors, three continuous and four categorical (`model.py:57-66`, `:216`), so seeding it
through `POST /api/v1/rate-tables/{slug}/seed-from-model` would hit the defect (by reading; not run). The journey describes that call:
A1 "seed-from-model on the AD frequency model", A2 "repeats for every rateable factor"
(`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:41-42`).

## Evidence

Run on a scratch worktree of `origin/main` (`101e32dc`, code identical to `9b0fb97c`), with the repository's `.venv`.

**1. End to end, a two-factor model.** `/…/e2e.py`, using the test module's own `_glm_model` helper:
```python
from datetime import UTC, datetime
import test_rate_table_operations as t
from model_schema.modelling import ModelStatus, RelativityLevel
from pricing_core.rate_tables.operations import seed_from_model
rel = {
    "driver_age_band": t._DRIVER_LEVELS,
    "region": (
        RelativityLevel(level="north", relativity=0.9, estimate=-0.1),
        RelativityLevel(level="south", relativity=1.1, estimate=0.1),
    ),
}
model = t._glm_model(ModelStatus.APPROVED, relativities=rel)
seed_from_model(model, table_slug="two-factor", change_note="x", seeded_at=datetime(2026, 7, 2, tzinfo=UTC))
```
Command: `PYTHONPATH=<tree>/packages/pricing-core/src:<tree>/packages/model-schema/src:<tree>/packages/pricing-core/tests
<repo>/.venv/bin/python e2e.py`. Result: `KeyError: 'region'`, raised at `operations.py:289`
(`key_values = tuple(row[key] for key in key_names)`), reached from `seed_from_model`.

**2. Control, one factor.** The same script with `region` removed prints `SEEDED ['driver_age_band'] 3`.

**3. The row shape alone** (the first reproduction, before the end-to-end run):
```python
cells=[{"age":"a","relativity":"1.1"},{"region":"n","relativity":"0.9"}]   # what extract_relativity_table emits for 2 factors
validate_rate_table(cells, keys=[age, region], value, key_domains={"age":frozenset("a"),"region":frozenset("n")})
```
→ `KeyError 'region'`.

**Limit of the evidence.** The two runs prove the library function. The 500 from `POST /api/v1/rate-tables/{slug}/seed-from-model`
is read from the code (`platform/rate_tables.py:130`, `except ValueError` only), not exercised over HTTP. Nothing here
shows what shape a multi-factor seeded table should take; that is a design choice (below).

## What a fix must decide

The spec does not say which shape a seeded table has. `03` §4.2's seeded example is a one-key table, and FR-234
requires full coverage of the declared key domain, which is a Cartesian product. Two readings fit:

- **One table per factor**, each with a single key and `relativity` as the value (a one-way relativity table, which is
  what a GLM's relativities are). Coverage and the diff then work as they are.
- **One table with every key**, whose cells are the product of the factors' levels (a multiplied-out table). That
  changes what the seeded value means (a product of relativities) and needs interaction handling.

The shape is being defined by the decision-maker session `dm-9855b` in the amendment to the DP-5 ruling (working id 9855), so
no open-questions row is added here; the fix follows that amendment. The auditor's reading, for the record, is the first
option, since it keeps the relativity as the fit reported it.

## Disposition

**HIGH: the exit demo must walk A1-A2.** Owner WK-1178 (a defect in a delivered FR-230 path, found at the WK-673 boundary). It depends on the DP-5 ruling's amendment defining the seeded shape (`dm-9855b`, in progress), and it goes ahead of PL 9788 (FD-1335 Part A). Red-first: a two-factor fixture
seeds, and the test fails on the current tree with `KeyError`. Hardening: an unseedable shape raises a named
`ValueError` (mapped to 422), never a `KeyError`. The lead gives the verdict.
