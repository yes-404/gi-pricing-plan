---
id: PL-805
family: plan
kind: leaf
title: W6b-15 — The `_minor` Rename Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-26
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-26-w6b-15-minor-rename.md
---

# W6b-15 — The `_minor` Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Drop the `_minor` suffix from the five statistics the decision OQ-538 (b)
released — the two reconciliation burning-cost fields and the three severity fields — keep
every type as it stands, and regenerate every artifact the published names reach (FR-23).

**Architecture:** The rename starts in `model-schema`, where the two burning-cost fields
live, and in the validation-rule catalogue. The generated contracts and the frontend schema
follow from the source of truth (FR-451). The severity trio lives in `pricing-core`'s
check code and in the catalogue entry. Backend and frontend consumers rename in the same
change set. Filed plans and decided register rows stay frozen. The plan appends dated
notes where a reader can mistake a pre-rename name for a live one.

**Tech Stack:** Pydantic v2 in `model-schema` (frozen, `extra="forbid"`), pytest,
`scripts/generate-contracts.py` + `openapi-typescript`, Vue 3 Composition API with
`<script setup lang="ts">`, Vitest.

**Spec:** FR-23 ([`../specs/00-overview.md`](../specs/00-overview.md) `:226`), FR-10
(`:213`), OQ-539 (`:541`) and OQ-538 (`:542`) in the same file, their mirror rows in
[`../open-questions.md`](../open-questions.md) (`:34`, `:35`), and the reconciliation sample
in [`../specs/02-modelling.md`](../specs/02-modelling.md) `:1456-1461`. The rule the
rename serves is FR-23. The type rule is FR-10. The releases are the two OQ rows.

**Slice source:** [`PL-00810-wk-664-the-slice-map-revised-again.md`](PL-00810-wk-664-the-slice-map-revised-again.md)
§3, line 162 — *"The `_minor` rename — `OQ-538` decided (b): statistics mislabelled
`_minor` drop the suffix under `FR-23`. The integer type stays. ... The plan sweeps the
class."* Lines 172, 185 and 195 confirm the plan can land at any time and must sweep the
class.

**Highest ids in use, published at the revised-2 anchor (`b989097`):** FR-58,
NFR-474, OQ-570. Next free: `FR-59`, `NFR-DATA-11`, `OQ-DATA-16`.
This plan mints none of them. The rename is released mechanical work. It cites
requirements that already exist.

## Global Constraints

- **FR-23 reserves `_minor` for integer minor units.** The suffix is the defect, not
  the type. The five statistics drop the suffix and keep their types.
- **The integer type stays on the burning-cost pair.** FR-190's sum-of-rounded-parts
  invariant (`packages/model-schema/src/model_schema/perils.py:364-367`) is the reason the
  type survives the rename.
- **The severity trio keeps its floats.** Bounds on, or measures of, a statistic are
  statistics (FR-10). The float is permitted, not a defect.
- **The fix inverts between the two groups.** `threshold_minor` and `largest_minor`
  denominate money. Their name is correct and their type is the defect (OQ-539). W6b-15
  records them and does not rename them (Finding 4).
- **Nobody hand-writes a published shape.** The contracts regenerate from `model-schema`
  (FR-451). The frontend types regenerate from the committed OpenAPI. A hand edit
  fails the drift check.
- **A change that spans spec and code lands as one commit.** The branch is squash-merged,
  so the PR carries both halves together (CLAUDE.md §0).
- **Both halves of the gate must pass locally before a push**
  ([`../../CLAUDE.md`](../../CLAUDE.md) §11). A Python-only run is not a gate run for a
  slice that touches the frontend.
- **A fresh worktree needs `uv sync --all-packages` first**, or `mypy` reports phantom
  errors that read as real defects.
- **Prose in this plan and in the commits is ASD-STE100.** No contractions, no `-ing`
  forms, no semicolons, no `should`/`would`/`may`/`might`/`could`. Verbatim code and quoted
  text stay unchanged.
- **Run every command from the repository root** of the executor's worktree.

---

## Findings the plan is built on

Each was verified against shipped source at `bc8674b` (#249) by a full-repo sweep. The
sweep and this section enumerate the class. The tasks rename only the five members the
decisions release.

### Finding 1 — the class, swept

Every `_minor` identifier in the repository falls into one of three groups.

**Rename — statistics mislabelled `_minor` (built here, five names):**

| Old name | New name | Type stays | Verified sites |
|---|---|---|---|
| `observed_burning_cost_minor` | `observed_burning_cost` | int | `model-schema/perils.py:306,338,353,355`, `modelling/perils.py:93,230`, `model_handlers.py:1504`, tests, contracts |
| `modelled_burning_cost_minor` | `modelled_burning_cost` | int | `model-schema/perils.py:290,307,337,364,365,367`, `modelling/perils.py:85,94,217,224,231`, `model_handlers.py:1500,1505`, tests, contracts |
| `min_severity_minor` | `min_severity` | float | `data/validate.py:1072,1078`, `model-schema/validation.py:386` |
| `max_severity_minor` | `max_severity` | float | `data/validate.py:1073,1078`, `model-schema/validation.py:386` |
| `mean_severity_minor` | `mean_severity` | float | `data/validate.py:1077` |

**Retype — money, name correct, type the defect (released by OQ-539, NOT built here,
two names):** `threshold_minor` (`data/validate.py:957,971,978`) and `largest_minor`
(`:982`) denominate a claim-amount cut and a largest claim amount. Their `float` is the
defect. Finding 4 records the pair as released and unscheduled.

**Conform — integer minor units or column names, stay (the rest):** `claim_amount_minor`
(a dataset column name), `total_negative_minor` (`data/validate.py:918`, `int(...)`-cast),
every `MoneyMinor` field, the locals `observed_minor`/`modelled_minor`
(`modelling/perils.py:192,224`), `_MONEY_SUFFIX = "_minor"` (`data/profile.py:90`), the
`min_frequency`/`max_frequency` neighbours, and the column names in
`examples/fremtpl2/seed.py` and the bench scripts.

### Finding 2 — the register understates the consumer set

The OQ-538 register text names *"the two perils test suites, and the generated
contracts"* as the consumers. The verified consumer set is wider:
`backend/src/app/worker/model_handlers.py:1500-1505` constructs the artifact, three backend
test files assert the wire names, `frontend/src/components/ReconciliationPanel.vue:43,47`
reads them, and `docs/specs/02-modelling.md:1456-1461` publishes them in a sample payload.
This plan renames every consumer.

### Finding 3 — a user-visible string asserts minor units on a statistic

`packages/pricing-core/src/pricing_core/data/validate.py:1079`:

```python
        detail=f"mean severity is {severity:,.0f} minor units",
```

The field it describes is a statistic. OQ-539 records the string as a surface neither
rule governs. A rename without the string still ships a payload that tells a reader mean
severity is in minor units. Task 3 fixes the string with the fields.

### Finding 4 — the retype pair is released and unscheduled

OQ-539's decision releases both corrections. W6b-15's slice row names only the rename
members. The retype pair therefore has no slice. The next slice-map revision must attach
one. This plan records the pair in its scope and does not build it. The planner flags the
pair to the manager in the same report as this plan.

### Finding 5 — old seeded rules keep their behaviour

The VR-ACT-12 catalogue entry (`packages/model-schema/src/model_schema/validation.py:386`)
carries `min_severity_minor` and `max_severity_minor` as its default params. The check
reads them with `.get(key, default)`. After the rename, a workspace seeded before the
change holds the old keys and reads the same defaults (0.0 and 1e12) it reads today.
Behaviour is preserved for old seeds and new seeds.

### Finding 6 — the decision records keep the pre-rename names

OQ-539, OQ-538 and FR-23 quote the pre-rename names as their record. After the
rename, a reader who greps an old name lands on a requirement row that reads as a live
violation. Task 6 appends dated notes to the rows in both mirrors instead of a rewrite. Filed plans that quote the old names stay frozen. The residual-grep whitelist in
Task 7 names them.

---

## Task 1: Rename the burning-cost fields in model-schema and regenerate the contracts

**Files:**
- Modify: `packages/model-schema/src/model_schema/perils.py:290,306-307,337-338,353-355,364-367`
- Modify: `packages/model-schema/tests/test_perils.py` (occurrences at `:109,114,117,118,310,315,320,331,344,356,361,372`, verified by sweep)
- Regenerate: `docs/contracts/schemas/peril-structure.schema.json`, `docs/contracts/openapi/generated.json`

**Interfaces:**
- Consumes: FR-23's rule and OQ-538's decision (b).
- Produces: `ReconciledPeril.modelled_burning_cost`, `Reconciliation.observed_burning_cost`
  and `Reconciliation.modelled_burning_cost` — the names Tasks 2, 4, 5 and 6 consume.

- [ ] **Step 1: Rename the field names in the model-schema tests**

Replace `observed_burning_cost_minor` with `observed_burning_cost` and
`modelled_burning_cost_minor` with `modelled_burning_cost` in
`packages/model-schema/tests/test_perils.py`. The file constructs `ReconciledPeril` and
`Reconciliation` with keyword arguments.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest packages/model-schema/tests/test_perils.py -q`
Expected: FAIL. The models receive unexpected keyword arguments — `Reconciliation()` does
not yet accept `observed_burning_cost`. A failure with any other cause is a plan defect:
stop and report it.

- [ ] **Step 3: Rename the fields and their read sites in perils.py**

In `packages/model-schema/src/model_schema/perils.py`:

- `:290` — `ReconciledPeril.modelled_burning_cost_minor` becomes
  `modelled_burning_cost`.
- `:306-307` — the two `Reconciliation` fields become `observed_burning_cost` and
  `modelled_burning_cost`.
- `:337` — the validator's sum `p.modelled_burning_cost_minor` becomes
  `p.modelled_burning_cost`.
- `:338` — the `ratio` computed field's two references rename.
- `:353-355` — the `observed_burning_cost_minor <= 0` comparison and the string
  `"observed_burning_cost_minor must be positive: ..."` rename.
- `:364-367` — the `total != modelled_burning_cost_minor` comparison and the string
  `f"modelled_burning_cost_minor {...} is not the sum..."` rename.

The error strings carry the old names. They are user-visible. They rename with the fields.
Types stay `MoneyMinor` and the validators stay untouched.

- [ ] **Step 4: Regenerate the contracts**

Run: `uv run python scripts/generate-contracts.py`
Expected: `docs/contracts/schemas/peril-structure.schema.json` and
`docs/contracts/openapi/generated.json` carry the new names. Do not hand-edit them.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run pytest packages/model-schema/tests/test_perils.py -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add packages/model-schema docs/contracts
git commit -m "refactor(w6b-15): drop the _minor suffix from the burning-cost fields in model-schema"
```

---

## Task 2: Rename the burning-cost fields in pricing-core

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/perils.py:85,93-94,217,224,230-231`
- Modify: `packages/pricing-core/tests/test_perils.py` (occurrences at `:166,167,235,236`, verified by sweep)

**Interfaces:**
- Consumes: the field names Task 1 produces.
- Produces: `ReconciledPerilResult.modelled_burning_cost`, `ReconciliationResult.observed_burning_cost`
  and `ReconciliationResult.modelled_burning_cost` — the names `model_handlers.py` consumes
  in Task 4.

- [ ] **Step 1: Rename the field names in the pricing-core tests**

Replace both names in `packages/pricing-core/tests/test_perils.py`. The locals
`observed_minor` and `modelled_minor` in the source stay — they hold integer minor units
and conform (Finding 1).

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest packages/pricing-core/tests/test_perils.py -q`
Expected: FAIL. The dataclasses receive unexpected keyword arguments.

- [ ] **Step 3: Rename the fields and the construction sites**

In `packages/pricing-core/src/pricing_core/modelling/perils.py`:

- `:85` — `ReconciledPerilResult.modelled_burning_cost_minor: int` becomes
  `modelled_burning_cost`.
- `:93-94` — the two `ReconciliationResult` fields rename.
- `:217` — the construction `modelled_burning_cost_minor=_to_minor(modelled)` renames.
- `:224` — the sum `p.modelled_burning_cost_minor` in the sum-of-rounded-parts total
  renames.
- `:230-231` — the `ReconciliationResult(...)` construction renames.

Types stay `int`. The locals `observed_minor` and `modelled_minor` stay.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest packages/pricing-core/tests/test_perils.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add packages/pricing-core
git commit -m "refactor(w6b-15): drop the _minor suffix from the burning-cost fields in pricing-core"
```

---

## Task 3: Rename the severity trio and fix the detail string

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/data/validate.py:1072-1079`
- Modify: `packages/model-schema/src/model_schema/validation.py:386`
- Modify: `packages/pricing-core/tests/test_catalogue.py:441-455` (the VR-ACT-12 test)

**Interfaces:**
- Consumes: OQ-539's classification — the trio are bounds on, or measures of, a
  statistic.
- Produces: the rule params `min_severity` / `max_severity` and the measured key
  `mean_severity` — wire names in the rule catalogue and the validation-report payload.

- [ ] **Step 1: Extend the VR-ACT-12 test with an acceptance assertion on the new keys**

In `packages/pricing-core/tests/test_catalogue.py`, in
`test_vr_act_12_severity_plausible_catches_a_units_error` (`:441-455`), rename the two
bounds keys and add the wire-key assertions after the first `run`:

```python
    bounds = {"min_severity": 50_000, "max_severity": 1_000_000}
    outcome = run("severity_plausible", {"t": minor}, params=bounds)
    assert outcome.violating_rows == 0
    assert outcome.measured["mean_severity"] == pytest.approx(250_000.0)
    assert outcome.threshold == {"min_severity": 50_000.0, "max_severity": 1_000_000.0}

    pounds = minor.with_columns(pl.col("claim_amount_minor") // 100)
    assert run("severity_plausible", {"t": pounds}, params=bounds).violating_rows == 1
```

Leave `total_negative_minor` (`:378`), `threshold_minor` (`:399`) and `largest_minor`
(`:402`) untouched — they are not in the rename group (Finding 1).

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest packages/pricing-core/tests/test_catalogue.py -q`
Expected: FAIL. The check reads `.get("min_severity", 0.0)` and `.get("max_severity",
1e12)`, so the renamed bounds fall back to the defaults. The pounds case (mean 2,500) sits
inside the default band, the assertion `violating_rows == 1` fails, and the measured-key
assertions raise `KeyError`. A failure with any other cause is a plan defect: stop and
report it.

- [ ] **Step 3: Rename the catalogue entry**

In `packages/model-schema/src/model_schema/validation.py:386`, rename the two params of
the VR-ACT-12 entry:

```python
                params={"min_severity": 0, "max_severity": 1_000_000_000_000},
```

The values stay integers. Old seeded rules read the same defaults as before (Finding 5).

- [ ] **Step 4: Rename the check's read sites, measured keys and detail string**

In `packages/pricing-core/src/pricing_core/data/validate.py:1072-1079`:

```python
    low = float(rule.params.get("min_severity", 0.0))
    high = float(rule.params.get("max_severity", 1e12))
    severity = rates["severity"]
    return CheckOutcome(
        violating_rows=0 if low <= severity <= high else 1,
        measured={"mean_severity": round(severity, 2), "claims": rates["claims"]},
        threshold={"min_severity": low, "max_severity": high},
        detail=f"mean severity is {severity:,.2f}",
    )
```

The detail string no longer asserts minor units (Finding 3). Do not touch
`_severity_outlier`'s `threshold_minor` and `largest_minor` (Finding 4).

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run pytest packages/pricing-core/tests/test_catalogue.py -q`
Expected: PASS. The new wire-key assertions pass.

- [ ] **Step 6: Commit**

```bash
git add packages/pricing-core packages/model-schema
git commit -m "refactor(w6b-15): drop the _minor suffix from the severity band names"
```

---

## Task 4: Rename the backend consumers

**Files:**
- Modify: `backend/src/app/worker/model_handlers.py:1500-1505`
- Modify: `backend/tests/test_contracts.py:2225`
- Modify: `backend/tests/test_peril_structures.py:474-475`
- Modify: `backend/tests/test_wf01_journey.py:624-625`

**Interfaces:**
- Consumes: the field names Tasks 1 and 2 produce.
- Produces: a backend that constructs and asserts the new wire names. Task 5's frontend
  builds on the same names.

- [ ] **Step 1: Rename the construction sites**

In `backend/src/app/worker/model_handlers.py:1500-1505`, rename
`modelled_burning_cost_minor` (two sites) and `observed_burning_cost_minor` (one site).
The keyword arguments now match the regenerated `Reconciliation` model from Task 1.

- [ ] **Step 2: Rename the wire-name assertions**

In the three backend test files, replace both burning-cost names at the cited lines. The
sites are: `test_contracts.py:2225` (a contract path string),
`test_peril_structures.py:474-475` and `test_wf01_journey.py:624-625` (payload fixtures or
assertions).

- [ ] **Step 3: Run the tests to verify they pass**

Run: `uv run pytest backend/tests/test_contracts.py backend/tests/test_peril_structures.py backend/tests/test_wf01_journey.py -q`
Expected: PASS.

- [ ] **Step 4: Run the residual grep**

Run: `git grep -n "burning_cost_minor" -- packages/ backend/`
Expected: zero hits. Any hit outside `docs/` is a missed consumer: rename it.

- [ ] **Step 5: Commit**

```bash
git add backend
git commit -m "refactor(w6b-15): rename the burning-cost fields in the backend consumers"
```

---

## Task 5: Rename the frontend consumers

**Files:**
- Regenerate: `frontend/src/api/generated/schema.d.ts`
- Modify: `frontend/src/components/ReconciliationPanel.vue:43,47`
- Modify: `frontend/src/components/__tests__/ReconciliationPanel.test.ts` (occurrences at `:15,16,18,19,75,76`)
- Modify: `frontend/src/views/__tests__/PerilStructureDetailView.test.ts` (occurrences at `:38,39,40`)

**Interfaces:**
- Consumes: the regenerated OpenAPI from Task 1.
- Produces: a frontend whose only `_minor` names are the money fields that conform.

- [ ] **Step 1: Regenerate the frontend schema**

Run: `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api`
Expected: `frontend/src/api/generated/schema.d.ts` carries the new field names. The file is
VCS-ignored. It is a build input, not evidence.

- [ ] **Step 2: Rename the component read sites**

In `frontend/src/components/ReconciliationPanel.vue:43,47`, replace
`modelled_burning_cost_minor` with `modelled_burning_cost`. The prop type
(`components["schemas"]["Reconciliation"]`) comes from the regenerated schema. The
`type-check` step verifies the two stay in agreement.

- [ ] **Step 3: Rename the test fixtures**

In `ReconciliationPanel.test.ts` and `PerilStructureDetailView.test.ts`, replace both
burning-cost names at the cited lines.

- [ ] **Step 4: Run the frontend checks**

Run: `pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend test`
Expected: all green.

- [ ] **Step 5: Run the residual grep**

Run: `git grep -n "burning_cost_minor" -- frontend/`
Expected: zero hits.

- [ ] **Step 6: Commit**

```bash
git add frontend/src
git commit -m "refactor(w6b-15): rename the burning-cost fields in the frontend consumers"
```

---

## Task 6: Amend the spec sample and the decision records

**Files:**
- Modify: `docs/specs/02-modelling.md:1456-1461`
- Modify: `docs/specs/00-overview.md:213` (FR-10), `:226` (FR-23), `:541` (OQ-539), `:542` (OQ-538)
- Modify: `docs/open-questions.md:34` (OQ-539), `:35` (OQ-538)

**Interfaces:**
- Consumes: the five new names from Tasks 1-3.
- Produces: a spec suite whose live rows cite the new names and whose records say the old
  names are the record, in both mirrors.

- [ ] **Step 1: Rename the sample payload keys in 02**

In `docs/specs/02-modelling.md:1456-1461`, rename the five keys in the reconciliation
sample:

```json
    "perils": [{"peril": "AD", "large_loss_kind": "capped",
                "modelled_burning_cost": 15_000},
               {"peril": "TP_BI", "large_loss_kind": "separate_model",
                "modelled_burning_cost": 2_337},
               {"peril": "WINDSCREEN", "large_loss_kind": "none",
                "modelled_burning_cost": 1_000}],
    "observed_burning_cost": 18_412, "modelled_burning_cost": 18_337,
```

The values stay. This is the only occurrence of the pair in 02 (verified by sweep).

- [ ] **Step 2: Append a dated note to FR-23**

In `docs/specs/00-overview.md:226`, append a note to the FR-23 row:

*Renamed 2026-08-26 (W6b-15): the five names cited above are `min_severity_minor` to
`min_severity`, `max_severity_minor` to `max_severity`, `mean_severity_minor` to
`mean_severity`, and the burning-cost pair to `observed_burning_cost` and
`modelled_burning_cost`. The OQ-539 and OQ-538 register rows keep the pre-rename
names as their record.*

Do not rewrite the row's earlier clauses.

- [ ] **Step 3: Append a one-line pointer to FR-10**

In `docs/specs/00-overview.md:213`, append a note to the FR-10 row:

*Renamed 2026-08-26 (W6b-15): the `validate.py` names cited above are pre-rename names.
FR-23's row carries the rename note.*

- [ ] **Step 4: Append dated notes to both OQ-539 rows**

Append the same note to `docs/open-questions.md:34` and to
`docs/specs/00-overview.md:541`:

*Renamed 2026-08-26 (W6b-15): `min_severity_minor`, `max_severity_minor` and
`mean_severity_minor` become `min_severity`, `max_severity` and `mean_severity`.
`threshold_minor` and `largest_minor` keep their names. Their float-to-int correction
stays released and unscheduled. The names cited above are the pre-rename names, kept as
the record.*

- [ ] **Step 5: Append dated notes to both OQ-538 rows**

Append the same note to `docs/open-questions.md:35` and to
`docs/specs/00-overview.md:542`:

*Renamed 2026-08-26 (W6b-15): `observed_burning_cost_minor` and
`modelled_burning_cost_minor` become `observed_burning_cost` and
`modelled_burning_cost`, types unchanged. The names cited above are the pre-rename names,
kept as the record.*

- [ ] **Step 6: Run the docs gate**

Run: `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`
Expected: PASS. The plan cites only defined requirement ids. The OQ rows carry their
register status in both mirrors (check 23).

- [ ] **Step 7: Commit**

```bash
git add docs
git commit -m "docs(w6b-15): rename the burning-cost and severity names in the spec and register"
```

---

## Task 7: Sweep the residual names and run the full gate

**Files:**
- Verify: every renamed source file, plus the frozen whitelist in `docs/`.

**Interfaces:**
- Consumes: all five renames from Tasks 1-3.
- Produces: a branch whose every `_minor` identifier either conforms or sits in a frozen
  record.

- [ ] **Step 1: Sweep each old name across the repository**

Run:

```bash
git grep -n "observed_burning_cost_minor\|modelled_burning_cost_minor" -- packages/ backend/ frontend/src/ scripts/
git grep -n "min_severity_minor\|max_severity_minor\|mean_severity_minor" -- packages/ backend/ frontend/src/ scripts/
```

Expected: zero hits. The residual hits sit in `docs/` only — the frozen whitelist:

```bash
git grep -ln "burning_cost_minor\|severity_minor" -- docs/
```

The expected files: `docs/open-questions.md`, `docs/specs/00-overview.md` (the decided
rows and FR-23, amended in Task 6), the filed plans named in Finding 6, and this
plan's own prose. Every hit must be one of those. A hit in any other file is a missed
consumer: rename it. The frozen files keep their text verbatim.

- [ ] **Step 2: Run the Python half of the gate**

Run: `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`
Expected: all green. Run the drift check explicitly — a regenerated contract that was not
committed fails CI even though every test passes:

Run: `uv run python scripts/generate-contracts.py --check`
Expected: PASS.

- [ ] **Step 3: Run the frontend half of the gate**

Run: `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api && pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend test && pnpm --dir frontend build`
Expected: all green.

- [ ] **Step 4: Run the docs gate once more**

Run: `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`
Expected: PASS.

- [ ] **Step 5: Commit any straggler**

```bash
git status --short
git add -A
git commit -m "refactor(w6b-15): sweep the residual _minor names"
```

If `git status` is clean, skip the commit.

---

## Self-review

**1. Spec coverage.** FR-23's rule and OQ-538's decision (b) → Tasks 1-3 and
6. FR-10's type rule → the types stay, stated per task and enforced by the unchanged
type annotations. OQ-539's two-group classification → Finding 1 and Task 3's explicit
exclusion of the retype pair. FR-190's rounded-parts invariant → Task 1 Step 3 keeps
the validator and the integer type. The slice row's sweep obligation → Finding 1 and Task
7 Step 1. The slice row's members that conform → Finding 1, untouched by every task.

**2. Placeholder scan.** No TBD or TODO. Every step carries its exact sites and its
predicted failure cause. The two convention guards (the test-failure causes in Tasks 1-3)
name the mode that must fail. A failure with a different cause reads as a plan defect
rather than a pass.

**3. Type consistency.** `observed_burning_cost`, `modelled_burning_cost`, `min_severity`,
`max_severity` and `mean_severity` are defined once in Finding 1 and used under the same
names in Tasks 1-6. The contract regeneration in Task 1 produces the wire names Task 4's
contract test asserts. The frontend prop type in Task 5 resolves to the same fields the
regenerated schema carries. The catalogue params in Task 3 match the check's `.get` keys.

**Gaps found in review, fixed inline:** the VR-ACT-12 test originally asserted nothing
about the measured and threshold keys, so the wire-key rename had no acceptance test.
Task 3 Step 1 adds the assertions. The `:1079` detail string was a fifth rename surface
no decision names. Task 3 Step 4 fixes it with the fields. The register rows were a live
citation surface after the rename. Task 6 Steps 2-5 append the notes.
