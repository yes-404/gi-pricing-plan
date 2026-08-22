# W32-1 — Contracts and the drift guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give `GroupingEvidence` the `source_level_stats` its contract has declared since
Phase 0, and close the three constraint-level holes in the contract-drift guard that let it
hide — `required`-set drift, `additionalProperties`, and scalar constraints — so the next
field declared in a contract and missing from the model fails on the day it diverges.

**Architecture:** One Pydantic field, one construction-site argument, one hand-authored
schema reconciled with the model it describes, and three new comparisons in
`backend/tests/test_contracts.py` built on the walkers already there. No new dependency, no
new file except the skill. The guard's four existing walkers (`_deref`, `_variants`,
`_scalar_types`, `_type_map`) are reused unchanged; the new comparisons mirror `_type_map`'s
traversal exactly so a path in one is a path in the other.

**Tech Stack:** Python 3.12, Pydantic v2, pytest. `scripts/generate-contracts.py` regenerates
the committed contract; CI fails on drift (`FR-PLAT-48`).

**Spec:**
- [`../specs/02-modelling.md`](../specs/02-modelling.md) — `FR-MODEL-15` and its 2026-08-22
  amendment, which names this slice's owner.
- [`../specs/00-overview.md`](../specs/00-overview.md) §4.3 — the artifact envelope;
  `FR-OVR-6`.
- [`../specs/07-platform.md`](../specs/07-platform.md) — `FR-PLAT-48`, the committed contract
  and its drift check.
- [`../roadmap.md`](../roadmap.md) — plan review 3, question 2(b) and 2(d), accepted
  2026-08-22, which assign all three parts of this slice together.
- [`2026-08-22-w6b-slice-map.md`](2026-08-22-w6b-slice-map.md) — where this slice sits.
- [`../adr/ADR-0002-model-schema-single-source-of-truth.md`](../adr/) — the rule this guard
  enforces.

---

## Global Constraints

Copied from [`../../CLAUDE.md`](../../CLAUDE.md) and
`.claude/skills/contract-schema`. Every task's requirements implicitly include this section.

- **Nobody hand-writes a shape that already exists in `model-schema`** (§2). The contract is
  generated; the hand-authored file is a *published specification* that must agree with it,
  not a second definition.
- **`docs/contracts/` is never hand-edited on the generated side.** `generated/` is output.
  The files under `docs/contracts/schemas/*.schema.json` (no `generated/`) are the Phase 0
  hand-authored contracts and *are* edited by hand.
- **Requirement IDs are permanent** (§5): append, never renumber, mark superseded rather than
  removing. This slice appends none — everything it builds is already specified.
- **When code and spec disagree, resolve it — do not quietly change one to match the other**
  (§0). Two tasks below hinge on this: say in the commit which side was wrong and why.
- **A generated artifact matching its source proves neither is correct** (§13 rule 4). Every
  new check in this slice must be shown to fail on deliberately broken input.
- **Money is integer minor units; exact decimals are strings** (`FR-OVR-7`). `OneWayRow`
  carries both, and its ratios (`frequency`, `mean_severity`, `mean_burning_cost`) are
  **float statistics, not amounts** — `FR-DATA-46` is explicit, and getting this backwards is
  the defect that motivated the type comparison in the first place.
- **A curated list needs the thing that notices it went stale.** Every scoped list this slice
  adds gets a meta-guard, the way `COMPARED_SLUGS` has `test_every_eligible_schema_is_compared`.
- **The worktree guard refuses compound shell commands.** Run each command plainly, or write a
  script and run it as one command.

### The gate — run both halves, read each command's own exit code

```bash
uv sync --all-packages --dev
uv run ruff check .
uv run mypy
uv run lint-imports
uv run pytest -q
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
```

A fresh worktree has no `.venv`; without `uv sync --all-packages --dev` first, mypy reports
several hundred phantom errors that read as real defects. The frontend half is untouched by
this slice — no file under `frontend/` changes — so `frontend.yml` cannot go red from it,
**except** that it also triggers on `docs/contracts/openapi/**`. Task 1 regenerates the
contract, so run the frontend half once at the end:

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend type-check
```

`pnpm` is at `~/.npm-global/bin` and not on the default PATH.

---

## File structure

| File | Responsibility | Change |
|---|---|---|
| `packages/model-schema/src/model_schema/modelling.py` | `GroupingEvidence` — the artifact shape | +1 field |
| `packages/pricing-core/src/pricing_core/modelling/groupings.py` | `grouping_evidence()` — the only construction site | +1 argument |
| `packages/pricing-core/tests/test_groupings.py` | the maths tests | +2 tests |
| `docs/contracts/schemas/grouping.schema.json` | the hand-authored contract | reconcile the evidence block |
| `docs/contracts/schemas/generated/grouping.schema.json` | generated output | regenerated, never edited |
| `backend/tests/test_contracts.py` | **the whole guard** — one file, no other holds any part | +3 comparisons, +3 meta-guards |
| `.claude/skills/contract-guard/SKILL.md` | new — how to write and extend a schema guard | new file |
| `.claude/skills/contract-schema/SKILL.md` | authoring a contract | one stale paragraph corrected |
| `.claude/skills/README.md` | the skill index | +1 row, +1 pairing row |

---

## What the measurement found, before any code

Run on 2026-08-22 against the twelve slugs with both an authored and a generated side. It is
recorded here because it **sized three of these tasks**, and a plan that specifies a guard
without knowing how red it lands is specifying a guard someone will switch off.

| Axis | Reach | Disagreements | Where |
|---|---|---|---|
| `required`, naively unioned across every combinator | 18 paths, 7 of 12 slugs | — | **Rejected. See below** |
| `required`, combinator-correct, in the dangerous direction | all 12 slugs | **2 names, 1 path, 1 slug** | `model.fit_result.terms.[]` — `bin_weights`, `standard_deviations` |
| `additionalProperties`, both forms | 17 shared paths, 9 slugs | **1** | `custom-objective.params` — model admits `integer\|number`, contract only `number` |
| Scalar constraints | 185 shared paths, 214 shared keywords | **3** | `grouping.evidence.source_level_count` and `target_level_count` (`minimum` model 0, contract 1); `objective-certificate.result.checks` (`minItems` model 1, contract **8**) |

**Six real defects across three new guards**, and each lands on one or two slugs rather than
seven. That is what makes them switch-on-able.

**Two design facts the measurement forced, and both are load-bearing.**

*`required` is not symmetric, so it is compared in one direction.* Pydantic's generated
`required` lists the fields with **no default** — a fact about *construction*. A hand-authored
contract's `required` lists what a *reader* may rely on. A field carrying a default is still
always serialised, so "the contract requires more than the model" is safe and accounted for
most of the naive count. The dangerous direction is the other one: a field the model demands
and the contract calls optional is a request a client builds from the published contract,
sends, and has refused — naming a field the contract said was not needed.

*`required` must respect what each combinator means, or it invents requirements.* The naive
walker unions across every branch, and that is wrong for a disjunction. `model.fit_result.bins.[]`
is `oneOf: [EbmNumericBins, EbmCategoricalBins]` with a discriminator; the first requires
`cuts`, the second requires `levels`, and **no single bin requires both**. Unioning reported
`{cuts, levels}` as model-required, and a plan that told an executor to add both to the
contract's `required` array would have made the contract *wrong* — it would refuse every valid
categorical bin. `allOf` is conjunction and unions; `oneOf`/`anyOf` is disjunction and
**intersects**; `then`/`else` are conditional and contribute nothing unconditionally. Under
those semantics the two false positives disappear and the two real ones remain.

`dataset_id` on `banding` and `grouping` is already a recorded divergence with a named owner
in `MODEL_ONLY_UNRECONCILED`, so the guard reuses that exemption rather than re-finding it.

---

### Task 1: `source_level_stats` on the model and its one construction site

`FR-MODEL-15` requires a Grouping to store "its method, parameters, **source Level
statistics**, the resulting target Level statistics, and the change in fit". The artifact
carries the target half and not the source half, so "which thin cells went into G1, and what
were they worth?" cannot be answered from it.

The value is **already computed**. `grouping_evidence()` binds `before` — the pre-merge
`OneWaySummary` — and already uses it for `source_level_count=len(before.rows)`.

**Files:**
- Modify: `packages/model-schema/src/model_schema/modelling.py:460-483` (`GroupingEvidence`)
- Modify: `packages/pricing-core/src/pricing_core/modelling/groupings.py:644-654`
- Test: `packages/pricing-core/tests/test_groupings.py`

**Interfaces:**
- Consumes: `OneWayRow` from `model_schema.profiles` — already imported by `modelling.py` for
  `target_level_stats`.
- Produces: `GroupingEvidence.source_level_stats: tuple[OneWayRow, ...]`, defaulting to `()`.
  Task 3 names its dotted paths; Task 2 types it in the contract.

- [ ] **Step 1: Write the failing test**

In `packages/pricing-core/tests/test_groupings.py`, beside the existing
`FR-MODEL-15` tests. `_book()`, `_proposal()` and `DATASET` are the module's existing
fixtures; the proposal collapses 20 source levels into 4.

```python
@pytest.mark.req("FR-MODEL-15")
def test_the_evidence_carries_the_source_levels_it_collapsed() -> None:
    """FR-MODEL-15 asks for source Level statistics, and the artifact carried none.

    `source_level_count` said twenty and nothing said *which* twenty, so "what were the
    cells we merged worth?" needed the one-way re-run against the dataset version the
    grouping was derived on — which is the recomputation the artifact exists to avoid.
    Declared in `grouping.schema.json` since Phase 0 and absent from the Python until
    2026-08-22; nothing caught it because the field is nested under `evidence` and the
    field-name comparison reads top-level names only.
    """
    grouping = propose_grouping(_book(), _proposal(), dataset_id=DATASET, slug="vg-4")
    evidence = grouping.evidence
    assert evidence is not None

    assert len(evidence.source_level_stats) == evidence.source_level_count == 20
    assert len(evidence.target_level_stats) == evidence.target_level_count == 4

    # The rows are the *source* levels, not the targets — the distinction the field exists
    # to make. Target names are generated (`_target_name`); source names come from the book.
    assert {row.level for row in evidence.source_level_stats} == set(_TRUE_EFFECT)
    assert {row.level for row in evidence.source_level_stats}.isdisjoint(
        {row.level for row in evidence.target_level_stats}
    )
```

- [ ] **Step 2: Run it and watch it fail**

```bash
uv run pytest packages/pricing-core/tests/test_groupings.py::test_the_evidence_carries_the_source_levels_it_collapsed -q
```

Expected: FAIL — `AttributeError: 'GroupingEvidence' object has no attribute
'source_level_stats'`.

- [ ] **Step 3: Add the field**

In `modelling.py`, immediately **above** `target_level_stats` so the pair reads as a pair and
the order mirrors the contract:

```python
    #: The source levels the grouping collapsed, carrying the statistics a target level
    #: carries — so "which thin cells went into G1, and what were they worth?" is answered
    #: from the artifact rather than by re-running the one-way against the dataset version
    #: (FR-MODEL-15). Declared in the contract since Phase 0; added to the model 2026-08-22.
    source_level_stats: tuple[OneWayRow, ...] = ()
```

- [ ] **Step 4: Pass the already-computed value at the construction site**

In `groupings.py`, in the `return GroupingEvidence(...)` at the end of `grouping_evidence()`,
add one line above `target_level_stats`:

```python
        source_level_stats=tuple(before.rows),
```

`before` is bound earlier in the same function and is already read for
`source_level_count=len(before.rows)`. There is no new computation and no new branch.

- [ ] **Step 5: Run the test and the module's suite**

```bash
uv run pytest packages/pricing-core/tests/test_groupings.py -q
```

Expected: PASS, including the three existing `FR-MODEL-15` tests.

- [ ] **Step 6: Regenerate the contract**

```bash
uv run python scripts/generate-contracts.py
```

Then confirm the generated side gained the field:

```bash
python3 -c "import json; d=json.load(open('docs/contracts/schemas/generated/grouping.schema.json')); print(sorted(d['\$defs']['GroupingEvidence']['properties']))"
```

Expected: `source_level_stats` present in the list.

- [ ] **Step 7: Commit**

```bash
git add packages/model-schema/src/model_schema/modelling.py packages/pricing-core/src/pricing_core/modelling/groupings.py packages/pricing-core/tests/test_groupings.py docs/contracts/schemas/generated/grouping.schema.json
git commit -m "feat(model): FR-MODEL-15 — the grouping evidence carries its source levels"
```

---

### Task 2: reconcile the authored contract's evidence block with `OneWayRow`

Task 1 exposes a second divergence in the same block, and it is the more interesting one. The
hand-authored `target_level_stats` item declares a shape that is **wrong in both directions**:

| | |
|---|---|
| Authored item properties | `level`, `exposure_years`, `claim_count`, `relativity` |
| `OneWayRow` properties | `level`, `exposure_years`, `claim_count`, `claim_amount_minor`, `frequency`, `frequency_ci`, `mean_severity`, `severity_ci`, `mean_burning_cost` |

`relativity` **does not exist on `OneWayRow`**, and six model fields are undeclared. Both are
invisible today: the type comparison intersects paths, so a path on one side only is skipped
rather than reported.

**This is a `CLAUDE.md` §0 resolution, not a tidy-up.** The verdict this plan proposes: the
**model is right and the contract is wrong**. `OneWayRow` is computed once and shared by `01`'s
profile and `02`'s factor workbench precisely so both see the same numbers; a hand-copy of it
in a third place that names a field the shared shape never had is the shape-defined-twice
failure §2 forbids. `relativity` is recoverable from the rows beside it. Record that verdict in
the commit message and in the schema's `description`.

**Files:**
- Modify: `docs/contracts/schemas/grouping.schema.json:63-77`

**Interfaces:**
- Consumes: `OneWayRow`'s field list, from Task 1's regenerated
  `generated/grouping.schema.json` `$defs.OneWayRow`.
- Produces: an authored `evidence` block whose `source_level_stats` and `target_level_stats`
  items both describe `OneWayRow`. Task 3 asserts the paths this creates.

- [ ] **Step 1: Write the failing test**

This one belongs with the guard, in `backend/tests/test_contracts.py`, because it is a
statement about the contract rather than about the maths. Add it after
`test_the_type_comparison_reaches_the_one_way_row`:

```python
@pytest.mark.req("FR-MODEL-15")
@pytest.mark.parametrize(
    "block", ["evidence.source_level_stats.[]", "evidence.target_level_stats.[]"]
)
def test_the_grouping_evidence_rows_are_the_shared_one_way_row(block: str) -> None:
    """Both halves of the evidence describe `OneWayRow`, and describe it the same way.

    The authored contract hand-copied a four-field subset of `OneWayRow` into
    `target_level_stats` and gave it a `relativity` the shared model has never had, while
    `source_level_stats` was `{"items": {"type": "object"}}` — untyped, describing nothing.
    Neither was visible: the type comparison reads only paths present on both sides, so a
    field on one side alone is skipped rather than reported, and a wholly untyped item has
    no leaves to compare at all.
    """
    generated = _load(GENERATED / "grouping.schema.json")
    authored = _load(AUTHORED / "grouping.schema.json")

    produced = _type_map(generated, generated, GENERATED)
    declared = _type_map(authored, authored, AUTHORED)

    fields = {
        path.rsplit(".", 1)[-1] for path in produced if path.startswith(f"{block}.")
    }
    assert fields, f"the model produces no leaves under {block}"
    missing = {
        f"{block}.{name}" for name in fields
    } - set(declared)
    assert not missing, f"the contract does not declare: {sorted(missing)}"

    extra = {
        path for path in declared if path.startswith(f"{block}.")
    } - set(produced)
    assert not extra, f"the contract declares fields the model lacks: {sorted(extra)}"
```

- [ ] **Step 2: Run it and watch it fail**

```bash
uv run pytest backend/tests/test_contracts.py::test_the_grouping_evidence_rows_are_the_shared_one_way_row -q
```

Expected: FAIL on both parameters — the `source_level_stats` case because the authored item is
untyped so nothing is declared, the `target_level_stats` case reporting
`evidence.target_level_stats.[].relativity` as declared-and-absent.

- [ ] **Step 3: Rewrite the evidence block's two row shapes**

In `docs/contracts/schemas/grouping.schema.json`, replace the `source_level_stats` and
`target_level_stats` entries with a shared `$defs` entry, so the file states the shape once:

```json
        "source_level_stats": {
          "$ref": "#/$defs/OneWayRows",
          "description": "The source levels this grouping collapsed (FR-MODEL-15). Added to the model 2026-08-22 having been declared here since Phase 0 and absent from GroupingEvidence throughout - nothing caught it because the field is nested under evidence and the field-name comparison reads top-level names only."
        },
        "target_level_stats": {
          "$ref": "#/$defs/OneWayRows",
          "description": "The resulting target levels, carrying the statistics a source level carries."
        }
```

and add, beside the existing `invariants` key at the document root:

```json
  "$defs": {
    "OneWayRows": {
      "type": "array",
      "description": "OneWayRow as model_schema.profiles defines it (FR-DATA-26). Stated once here because both halves of the evidence are the same shape. Corrected 2026-08-22: this block hand-copied a four-field subset and declared a 'relativity' OneWayRow has never carried, while source_level_stats was an untyped array of objects. The model was right and the contract was wrong - OneWayRow is computed once and shared by 01's profile and 02's factor workbench so both see the same numbers, and a third hand-copy of it is the shape-defined-twice CLAUDE.md 2 forbids.",
      "items": {
        "type": "object",
        "required": ["level", "exposure_years"],
        "properties": {
          "level": {"type": "string"},
          "exposure_years": {"$ref": "common/money.schema.json#/$defs/Decimal"},
          "claim_count": {"type": "integer", "minimum": 0},
          "claim_amount_minor": {"$ref": "common/money.schema.json#/$defs/MoneyMinor"},
          "frequency": {"type": ["number", "null"]},
          "frequency_ci": {"type": ["array", "null"], "items": {"type": "number"}},
          "mean_severity": {"type": ["number", "null"]},
          "severity_ci": {"type": ["array", "null"], "items": {"type": "number"}},
          "mean_burning_cost": {"type": ["number", "null"]}
        }
      }
    }
  },
```

`frequency`, `mean_severity` and `mean_burning_cost` are `number` and **not** `MoneyMinor`:
`FR-DATA-46` is explicit that a mean is a statistic, not an amount, and typing them as integers
is the exact defect the type comparison was built to catch.

`required` drops to `["level", "exposure_years"]`, matching `OneWayRow` — `claim_count` has a
default of `0` on the model. This is deliberate and is the safe direction described in the
measurement above.

- [ ] **Step 4: Run the test and the whole contract suite**

```bash
uv run pytest backend/tests/test_contracts.py -q
```

Expected: PASS. If `test_generated_and_authored_agree_on_scalar_types` now reports a `grouping`
disagreement, that is this task's own work — the new paths are shared for the first time, so
they are compared for the first time. Fix the contract, not the model.

- [ ] **Step 5: Confirm the file still parses and carries no duplicate key**

```bash
python3 -c "import json,collections; raw=open('docs/contracts/schemas/grouping.schema.json').read(); json.loads(raw, object_pairs_hook=lambda p:(_ for _ in ()).throw(ValueError(f'duplicate {[k for k,c in collections.Counter(k for k,_ in p).items() if c>1]}')) if len({k for k,_ in p})!=len(p) else dict(p)); print('parses, no duplicate keys')"
```

`json.load` silently keeps the last of a duplicated key, which is how a second `allOf` block
discards the first. The audit catches it too; this is the faster loop.

- [ ] **Step 6: Commit**

```bash
git add docs/contracts/schemas/grouping.schema.json backend/tests/test_contracts.py
git commit -m "fix(contracts): the grouping evidence rows are OneWayRow, in both halves

The authored contract hand-copied a four-field subset of OneWayRow into
target_level_stats with a 'relativity' the shared model has never carried, and left
source_level_stats an untyped array of objects. CLAUDE.md 0: the model was right --
OneWayRow is computed once and shared, and a third copy of it is the shape defined twice
2 forbids. Both halves now \$ref one \$defs entry."
```

---

### Task 3: the nested-path control for `grouping`

Task 1's field and Task 2's shape are both **nested**, and nested fields are exactly what this
suite has twice lost silently: `gbm.quantile_crossing` and `gbm.tree_count` were absent from
`diagnostics.schema.json` for months with every check green. The instrument for that is
`REACHED_NESTED_PATHS` — name the paths that matter so their removal is noticed.

It currently holds five slugs — `model`, `model-spec`, `diagnostics`,
`transparency-artifact`, `peril-structure` — and **no `grouping` entry**. That absence is why
this slice exists.

**Files:**
- Modify: `backend/tests/test_contracts.py` — `REACHED_NESTED_PATHS`

**Interfaces:**
- Consumes: the dotted paths Task 1 and Task 2 created.
- Produces: nothing later tasks read.

- [ ] **Step 1: Add the entry**

```python
    "grouping": frozenset(
        {
            "evidence.source_level_stats.[].level",
            "evidence.source_level_stats.[].exposure_years",
            "evidence.source_level_stats.[].claim_count",
            "evidence.target_level_stats.[].level",
            "evidence.target_level_stats.[].exposure_years",
            "evidence.target_level_stats.[].claim_count",
        }
    ),
```

- [ ] **Step 2: Run the control**

```bash
uv run pytest backend/tests/test_contracts.py::test_the_comparison_reaches_the_nested_fields_this_slice_added -q
```

Expected: PASS.

- [ ] **Step 3: Prove it fails on broken input — `CLAUDE.md` §13 rule 4**

A check that has never been seen to fail is a check nobody has tested. Delete
`source_level_stats` from the **authored** contract temporarily:

```bash
python3 -c "import json,pathlib; p=pathlib.Path('docs/contracts/schemas/grouping.schema.json'); d=json.loads(p.read_text()); del d['properties']['evidence']['properties']['source_level_stats']; p.write_text(json.dumps(d, indent=2))"
```

```bash
uv run pytest backend/tests/test_contracts.py -q
```

Expected: FAIL, naming the three `evidence.source_level_stats.[]` paths. Then restore:

```bash
git checkout docs/contracts/schemas/grouping.schema.json
```

- [ ] **Step 4: Prove it fails the other way too**

Remove the field from the **model** and regenerate, which is the direction a future refactor
would actually take:

```bash
python3 -c "import pathlib; p=pathlib.Path('packages/model-schema/src/model_schema/modelling.py'); s=p.read_text(); p.write_text(s.replace('    source_level_stats: tuple[OneWayRow, ...] = ()\n', ''))"
```

```bash
uv run python scripts/generate-contracts.py
```

```bash
uv run pytest backend/tests/test_contracts.py -q
```

Expected: FAIL. Then restore both:

```bash
git checkout packages/model-schema/src/model_schema/modelling.py docs/contracts/schemas/generated/grouping.schema.json
```

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_contracts.py
git commit -m "test(contracts): name the grouping evidence's nested paths so their removal is noticed"
```

---

### Task 4: the `required`-set guard, in the direction that pays

**Files:**
- Modify: `backend/tests/test_contracts.py`
- Modify: `docs/contracts/schemas/model.schema.json` (the four names the guard finds)

**Interfaces:**
- Consumes: `_variants`, `_deref`, `_MAX_COMPOSITION_DEPTH`, `MODEL_ONLY_UNRECONCILED`,
  `COMPARED_SLUGS` — all already in the module.
- Produces: `_required_at(document, node, base, *, _depth=0) -> frozenset[str]`,
  `_required_map(document, node, base, path="") -> dict[str, frozenset[str]]`, and the
  constant `_ROOT_PATH: Final = "<root>"`. Tasks 5, 6 and 7 use `_ROOT_PATH`; the two walkers
  are Task 4's alone.

- [ ] **Step 1: Write the failing test**

Add after the scalar-types test. The rule it asserts is stated in the docstring because it is
not obvious and a reader who does not know it will "fix" the test the wrong way.

```python
_ROOT_PATH: Final = "<root>"


def _required_at(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    *,
    _depth: int = 0,
) -> frozenset[str]:
    """The keys required **at this node**, respecting what each combinator means.

    `_variants` deliberately flattens every combinator into one list, which is right for
    asking "what fields exist anywhere in this shape?" and wrong for asking "what must be
    present?". So this does not use it. `allOf` is conjunction — every branch's obligations
    hold, so union them. `oneOf`/`anyOf` is disjunction — a key is required only if
    **every** arm demands it, so intersect. `then`/`else` are conditional on an `if` this
    suite does not evaluate, and contribute nothing unconditionally.

    Getting this wrong **invents** requirements rather than missing them, which is the more
    expensive failure. `model.fit_result.bins.[]` is
    `oneOf: [EbmNumericBins, EbmCategoricalBins]` with a discriminator: the first requires
    `cuts`, the second requires `levels`, and no single bin requires both. A union reports
    both as model-required, and a contract "corrected" to match would then refuse every
    valid categorical bin — a guard that manufactures the defect it reports.
    """
    if _depth > _MAX_COMPOSITION_DEPTH:
        raise AssertionError(
            f"more than {_MAX_COMPOSITION_DEPTH} composition levels — the document nests "
            "without bottoming out"
        )
    node, document = _deref(document, node, base)
    here = set(node.get("required", ()))
    for branch in node.get("allOf", []):
        here |= _required_at(document, branch, base, _depth=_depth + 1)
    for keyword in ("oneOf", "anyOf"):
        arms = [b for b in node.get(keyword, []) if b.get("type") != "null"]
        if not arms:
            continue
        common = _required_at(document, arms[0], base, _depth=_depth + 1)
        for arm in arms[1:]:
            common &= _required_at(document, arm, base, _depth=_depth + 1)
        here |= common
    return frozenset(here)


def _required_map(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    path: str = "",
) -> dict[str, frozenset[str]]:
    """Flatten a schema to `dotted.path -> the keys required at that path`.

    Descends the way `_type_map` does — `_variants` to find children, the same `.[]`
    collapse for arrays — so a path here is a path there and the two maps can be read
    against each other. What is required *at* each node comes from `_required_at` instead,
    because **finding children and deciding obligations are different questions** and only
    the first one wants a flattened view.
    """
    found: dict[str, frozenset[str]] = {}
    required = _required_at(document, node, base)
    if required:
        found[path or _ROOT_PATH] = required

    for owner, variant in _variants(document, node, base):
        for name, child in variant.get("properties", {}).items():
            subtree = _required_map(owner, child, base, f"{path}.{name}".lstrip("."))
            for key, keys in subtree.items():
                found[key] = found.get(key, frozenset()) | keys
        elements = list(variant.get("prefixItems", ()))
        if "items" in variant:
            elements.append(variant["items"])
        for child in elements:
            subtree = _required_map(owner, child, base, f"{path}.[]".lstrip("."))
            for key, keys in subtree.items():
                found[key] = found.get(key, frozenset()) | keys
    return found


@pytest.mark.req("FR-PLAT-48")
@pytest.mark.req("FR-OVR-6")
@pytest.mark.parametrize("slug", COMPARED_SLUGS)
def test_the_contract_never_marks_optional_what_the_model_requires(slug: str) -> None:
    """One direction, deliberately, and the direction is the whole design.

    The two sides answer different questions. Pydantic's `required` lists the fields with
    no default — a fact about *construction*. A hand-authored contract's `required` lists
    what a reader may rely on. A field carrying a default is still always serialised, so
    "the contract requires more than the model" is safe, and on 2026-08-22 it accounted for
    fourteen of the eighteen differences across the twelve compared slugs. Asserting
    equality would land red on seven schemas for a reason that is mostly not a defect, and
    a guard that lands like that is one somebody switches off.

    The other direction is a live bug. A field the model demands and the contract calls
    optional is a request a client will build from the published contract, send, and have
    refused — and the refusal names a field the contract said was not needed.

    The two this found on the day it was written are `model.fit_result.terms.[]`'s
    `bin_weights` and `standard_deviations`, which `EbmTerm` requires and the contract
    marks optional.

    It found them only because `_required_at` respects combinators. The naive union also
    reported `bins.[].cuts` and `bins.[].levels`, which are **not** defects: `bins.[]` is a
    discriminated `oneOf` and no single arm requires both.

    `dataset_id` on `banding` and `grouping` is not among them because it is already a
    recorded divergence with a named owner (`MODEL_ONLY_UNRECONCILED`) — the same field,
    the same finding, and re-reporting it here would be a second account of one fact.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")

    produced = _required_map(generated, generated, GENERATED)
    declared = _required_map(authored, authored, AUTHORED)

    exempt = MODEL_ONLY_UNRECONCILED.get(slug, frozenset())
    if _composes_the_envelope(authored):
        exempt |= ENVELOPE_FIELDS

    optional_but_demanded = {
        path: sorted(produced[path] - declared.get(path, frozenset()) - exempt)
        for path in sorted(set(produced) & set(declared))
        if produced[path] - declared.get(path, frozenset()) - exempt
    }
    assert not optional_but_demanded, (
        "the model requires fields the contract marks optional, so a client following the "
        "published contract builds a request the platform refuses: "
        + ", ".join(f"{p} ({', '.join(n)})" for p, n in optional_but_demanded.items())
    )
```

- [ ] **Step 2: Run it and watch it fail on exactly one slug**

```bash
uv run pytest backend/tests/test_contracts.py::test_the_contract_never_marks_optional_what_the_model_requires -q
```

Expected: 11 passed, 1 failed — `model`, naming `fit_result.terms.[]` with
`bin_weights, standard_deviations` and nothing else.

If `bins.[]` also appears with `cuts` and `levels`, `_required_at` is unioning across the
`oneOf` — that is the bug it exists to avoid, and the fix is the walker, **not** the contract.
If any other slug fails, **stop and re-measure rather than widening the exemption**. The
measurement in this plan is dated 2026-08-22; a slug that has moved since is a finding.

- [ ] **Step 3: Resolve the two, in the contract**

Read the model side first — `EbmTerm` in `packages/model-schema/src/model_schema/modelling.py`
— and confirm `bin_weights` and `standard_deviations` genuinely have no default. They do not:
`EbmTerm` requires `bin_weights`, `scores`, `standard_deviations`, `term_features` and
`term_name`. The model requires them and the contract is the wrong side.

In `docs/contracts/schemas/model.schema.json`, add both names to the `required` array of the
block declaring `fit_result.terms`' item, and record why in that block's `description`:

```json
"description": "Corrected 2026-08-22: EbmTerm requires bin_weights and standard_deviations and this contract marked them optional, so a client building a fit_result from the published contract omitted them and had the request refused naming a field the contract said was not needed."
```

Leave the contract's own `kind` requirement on `bins.[]` and `level` on `fit_result.tweedie`
alone — those are the safe direction, and changing them is a different question with a
different owner.

- [ ] **Step 4: Run it green**

```bash
uv run pytest backend/tests/test_contracts.py::test_the_contract_never_marks_optional_what_the_model_requires -q
```

Expected: 12 passed.

- [ ] **Step 5: Prove it fails on broken input**

```bash
python3 -c "import json,pathlib; p=pathlib.Path('docs/contracts/schemas/grouping.schema.json'); d=json.loads(p.read_text()); d['\$defs']['OneWayRows']['items']['required']=['level']; p.write_text(json.dumps(d, indent=2))"
```

```bash
uv run pytest backend/tests/test_contracts.py::test_the_contract_never_marks_optional_what_the_model_requires -q
```

Expected: FAIL on `grouping`, naming `exposure_years`, which `OneWayRow` has no default for.
Then restore:

```bash
git checkout docs/contracts/schemas/grouping.schema.json
```

- [ ] **Step 6: Commit**

```bash
git add backend/tests/test_contracts.py docs/contracts/schemas/model.schema.json
git commit -m "test(contracts): the contract may not mark optional what the model requires

One direction on purpose. Pydantic's required set is about construction, a hand-authored
contract's is about what a reader may rely on, and 14 of the 18 differences measured today
are the safe direction. The dangerous one is a request a client builds from the published
contract and has refused; it found four, all in model.fit_result."
```

---

### Task 5: the `additionalProperties` guard

`additionalProperties` carries **two different meanings** in this suite, and a guard that reads
only one of them is green because it compared nothing.

- **The boolean form.** `extra="forbid"` generates `"additionalProperties": false`. Every
  generated schema declares it at the root; **no authored schema declares it in boolean form
  anywhere.**
- **The schema form.** A `dict[str, float]` field generates
  `"additionalProperties": {"type": "number"}` — a statement about the *values* an open map
  admits. This is the form the authored contracts use: `labels`, `mapping`, `params`,
  `progress.counters`, `glm.vif`, `fit_result.categorical_maps`, `spec.family_params` and
  eleven more.

A comparison written for the boolean form alone would intersect an all-root generated map with
an empty authored one and pass, having compared nothing — the exact failure this file's own
`test_the_type_comparison_reaches_the_one_way_row` exists to prevent. So `_closure_map`
records both, distinguishably.

**Files:**
- Modify: `backend/tests/test_contracts.py`

**Interfaces:**
- Consumes: `_variants`, `_scalar_types`, `_ROOT_PATH` from Task 4.
- Produces: `_closure_map(document, node, base, path="") -> dict[str, frozenset[str]]`.

- [ ] **Step 1: Write the failing test**

```python
def _closure_map(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    path: str = "",
) -> dict[str, frozenset[str]]:
    """Flatten a schema to `dotted.path -> what `additionalProperties` says there`.

    Both spellings land in one vocabulary so they cannot be silently compared against each
    other: the boolean form becomes `{"CLOSED"}` or `{"OPEN"}`, the schema form becomes the
    JSON types its value schema admits. A path where one side says `CLOSED` and the other
    says `number` is then a reported disagreement rather than an accidental match.

    Only nodes that *state* `additionalProperties` are recorded. Absence is not `OPEN`:
    JSON Schema's default is open, but a hand-authored contract that says nothing is silent
    rather than deliberate, and reporting every silence would bury the real disagreements —
    which measured **one** across the whole compared suite.
    """
    found: dict[str, frozenset[str]] = {}
    for owner, variant in _variants(document, node, base):
        extra = variant.get("additionalProperties")
        if extra is not None:
            key = path or _ROOT_PATH
            if isinstance(extra, bool):
                says = frozenset({"OPEN" if extra else "CLOSED"})
            else:
                says = frozenset(_scalar_types(owner, extra, base)) or frozenset({"ANY"})
            found[key] = found.get(key, frozenset()) | says
        for name, child in variant.get("properties", {}).items():
            for key, says in _closure_map(
                owner, child, base, f"{path}.{name}".lstrip(".")
            ).items():
                found[key] = found.get(key, frozenset()) | says
        elements = list(variant.get("prefixItems", ()))
        if "items" in variant:
            elements.append(variant["items"])
        for child in elements:
            for key, says in _closure_map(
                owner, child, base, f"{path}.[]".lstrip(".")
            ).items():
                found[key] = found.get(key, frozenset()) | says
    return found


@pytest.mark.req("FR-PLAT-48")
@pytest.mark.parametrize("slug", COMPARED_SLUGS)
def test_generated_and_authored_agree_on_what_an_open_map_admits(slug: str) -> None:
    """An open map's value type is published, and a client validates against it.

    Seventeen paths declare `additionalProperties` on both sides and nothing has ever read
    one. The measured disagreement is `custom-objective.params`: the model admits
    `integer | number` and the contract admits `number` alone, so an objective parameterised
    with a whole number — a period, a count, a cap in whole units — is a document the
    published contract rejects and the platform accepts. That is the direction that wastes
    an author's afternoon, because the thing refusing them is their own validator.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")

    produced = _closure_map(generated, generated, GENERATED)
    declared = _closure_map(authored, authored, AUTHORED)

    disagreed = {
        path: (sorted(produced[path]), sorted(declared[path]))
        for path in sorted(set(produced) & set(declared))
        if produced[path] != declared[path]
    }
    assert not disagreed, (
        "the model and the contract disagree on what extra properties are admitted at "
        + ", ".join(f"{p} (model {g}, contract {a})" for p, (g, a) in disagreed.items())
    )
```

- [ ] **Step 2: Run it and watch it fail on exactly one slug**

```bash
uv run pytest backend/tests/test_contracts.py::test_generated_and_authored_agree_on_what_an_open_map_admits -q
```

Expected: 11 passed, 1 failed — `custom-objective`, naming `params (model ['integer',
'number'], contract ['number'])`.

If **nothing** fails, the walker is not reaching the schema form and the comparison is empty
on one side — check `_closure_map` against `grouping`, which declares `labels` and `mapping`,
before believing the suite is clean.

- [ ] **Step 3: Resolve the one, in the contract**

`ObjectiveParams`' value type in `packages/model-schema/src/model_schema/objectives.py` admits
`int | float`. The model is right: a Tweedie power of `2`, a cap in whole units, or an integer
period are all legitimate parameter values, and JSON has no way to mark `2` as a float. In
`docs/contracts/schemas/custom-objective.schema.json`, widen `params`' `additionalProperties`
to `{"type": ["integer", "number"]}` and note the correction in its `description`.

- [ ] **Step 4: Prove it fails on broken input**

Re-narrow it, which is the state Step 3 just left:

```bash
python3 -c "import json,pathlib; p=pathlib.Path('docs/contracts/schemas/custom-objective.schema.json'); d=json.loads(p.read_text()); d['properties']['params']['additionalProperties']={'type':'string'}; p.write_text(json.dumps(d, indent=2))"
```

```bash
uv run pytest backend/tests/test_contracts.py::test_generated_and_authored_agree_on_what_an_open_map_admits -q
```

Expected: FAIL on `custom-objective`, naming `contract ['string']`. Restore:

```bash
git checkout docs/contracts/schemas/custom-objective.schema.json
```

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_contracts.py docs/contracts/schemas/custom-objective.schema.json
git commit -m "test(contracts): the two sides agree on what an open map admits

Reads both spellings of additionalProperties into one vocabulary -- the boolean form the
generated side uses and the schema form every authored contract uses -- because a guard
written for one of them intersects an empty map and passes. Found custom-objective.params,
where the contract refuses the integer the platform accepts."
```

---

### Task 6: the scalar-constraint guard

`minLength`, `maxLength`, `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`,
`multipleOf` and `pattern` are the constraints a client validates against before sending.
Seven `minLength` declarations sit in the compared set and none is read.

**Files:**
- Modify: `backend/tests/test_contracts.py`

**Interfaces:**
- Consumes: `_variants`, `_MAX_COMPOSITION_DEPTH`.
- Produces: `_constraint_map(document, node, base, path="", *, _depth=0) ->
  dict[str, dict[str, Any]]` and `_COMPARED_CONSTRAINTS: Final[frozenset[str]]`.

- [ ] **Step 1: Write the failing test**

```python
#: The constraint keywords compared. Written out rather than "every keyword that is not a
#: structural one", because the structural set grows with the spec and a negative list would
#: quietly start comparing things this guard has no opinion about.
_COMPARED_CONSTRAINTS: Final[frozenset[str]] = frozenset(
    {
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
        "pattern",
        "minItems",
        "maxItems",
    }
)


def _constraint_map(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    path: str = "",
    *,
    _depth: int = 0,
) -> dict[str, dict[str, Any]]:
    """Flatten a schema to `dotted.path -> the constraint keywords declared there`.

    Only keywords in `_COMPARED_CONSTRAINTS`, and only where a side declares one: a path
    constrained on neither side is not a disagreement, and a path constrained on one side
    only is reported by the comparison rather than by this walker.
    """
    if _depth > _MAX_COMPOSITION_DEPTH:
        raise AssertionError(
            f"more than {_MAX_COMPOSITION_DEPTH} composition levels — the document nests "
            "without bottoming out"
        )
    found: dict[str, dict[str, Any]] = {}
    properties: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {}
    elements: list[tuple[dict[str, Any], dict[str, Any]]] = []

    for owner, variant in _variants(document, node, base):
        declared = {k: v for k, v in variant.items() if k in _COMPARED_CONSTRAINTS}
        if declared:
            found.setdefault(path or _ROOT_PATH, {}).update(declared)
        for name, child in variant.get("properties", {}).items():
            properties.setdefault(name, []).append((owner, child))
        if "items" in variant:
            elements.append((owner, variant["items"]))
        elements.extend((owner, entry) for entry in variant.get("prefixItems", ()))

    for name in sorted(properties):
        for owner, child in properties[name]:
            for key, declared in _constraint_map(
                owner, child, base, f"{path}.{name}".lstrip("."), _depth=_depth + 1
            ).items():
                found.setdefault(key, {}).update(declared)
    for owner, child in elements:
        for key, declared in _constraint_map(
            owner, child, base, f"{path}.[]".lstrip("."), _depth=_depth + 1
        ).items():
            found.setdefault(key, {}).update(declared)
    return found


@pytest.mark.req("FR-PLAT-48")
@pytest.mark.parametrize("slug", COMPARED_SLUGS)
def test_generated_and_authored_agree_on_scalar_constraints(slug: str) -> None:
    """A bound is part of the published contract, and a wrong one is refused input.

    The type comparison above answers "may this be a string?" and stops. It says nothing
    about a `minLength: 1` the model enforces and the contract omits — under which a client
    posts the empty string the contract permitted and meets a 422 naming a rule it was
    never told. Only keywords declared on **both** sides are compared, for the same reason
    the type comparison intersects paths: a constraint on one side alone is a difference of
    intent, and `test_an_artifact_shape_carries_exactly_what_its_contract_declares` is
    where intent is arbitrated.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")

    produced = _constraint_map(generated, generated, GENERATED)
    declared = _constraint_map(authored, authored, AUTHORED)

    disagreed: dict[str, dict[str, tuple[Any, Any]]] = {}
    for path in sorted(set(produced) & set(declared)):
        for keyword in sorted(set(produced[path]) & set(declared[path])):
            if produced[path][keyword] != declared[path][keyword]:
                disagreed.setdefault(path, {})[keyword] = (
                    produced[path][keyword],
                    declared[path][keyword],
                )
    assert not disagreed, (
        "the model and the contract disagree on a bound at "
        + "; ".join(
            f"{p}: " + ", ".join(f"{k} model={g} contract={a}" for k, (g, a) in d.items())
            for p, d in disagreed.items()
        )
    )
```

- [ ] **Step 2: Run it and watch it fail on two slugs**

```bash
uv run pytest backend/tests/test_contracts.py::test_generated_and_authored_agree_on_scalar_constraints -q
```

Expected: 10 passed, 2 failed. It reaches 185 shared paths and 214 shared keywords, and
disagrees on **three**:

| Path | Model | Contract |
|---|---|---|
| `grouping.evidence.source_level_count` | `minimum: 0` | `minimum: 1` |
| `grouping.evidence.target_level_count` | `minimum: 0` | `minimum: 1` |
| `objective-certificate.result.checks` | `minItems: 1` | `minItems: 8` |

- [ ] **Step 3: Resolve the three — and the third is not a typo**

The two `grouping` counts are a §0 question with an easy answer: `Field(ge=0)` on the model
against `minimum: 1` in the contract. A grouping with zero source levels is not a thing the
platform can produce, so the *contract* states the real invariant and the model is loose.
Tighten the model to `Field(ge=1)` and regenerate — this is the case where the spec was right.
Re-run `packages/pricing-core/tests/test_groupings.py` after, because a fixture constructing an
empty evidence would now be refused.

**`objective-certificate.result.checks` is the interesting one.** The contract requires **at
least eight** checks on a certificate and the model requires one. `FR-MODEL-76`'s certification
machinery is what publishes this artifact, and "a certificate carries at least eight checks" is
either a real obligation the model does not enforce or a number nobody has justified since
Phase 0. **Do not silently pick.** Read `02` §4.6 and the certificate's own check catalogue; if
the eight are named there, the model is wrong and gains the bound; if they are not, this is an
open question for the maintainer with options and a recommendation, recorded in
[`../open-questions.md`](../open-questions.md) — and this slug is scoped out of the guard with
the question's id beside it, not exempted silently.

Either way the slice does not end with a guard that is red.

- [ ] **Step 4: Prove it fails on broken input**

`OneWayRow.claim_count` is `Field(ge=0)`, which generates `"minimum": 0`, and Task 2 declared
the same bound in the authored contract. Move it:

```bash
python3 -c "import json,pathlib; p=pathlib.Path('docs/contracts/schemas/grouping.schema.json'); d=json.loads(p.read_text()); d['\$defs']['OneWayRows']['items']['properties']['claim_count']['minimum']=1; p.write_text(json.dumps(d, indent=2))"
```

```bash
uv run pytest backend/tests/test_contracts.py::test_generated_and_authored_agree_on_scalar_constraints -q
```

Expected: FAIL on `grouping`, naming `minimum model=0 contract=1`. Restore:

```bash
git checkout docs/contracts/schemas/grouping.schema.json
```

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_contracts.py docs/contracts/schemas packages/model-schema/src/model_schema/modelling.py
git commit -m "test(contracts): the two sides agree on the bounds they publish

185 shared paths, 214 shared keywords, three disagreements. Two are grouping level counts
where the contract stated the real invariant and the model was loose -- CLAUDE.md 0, the
spec was right. The third is objective-certificate.result.checks, minItems 8 against the
model's 1, which is a question rather than a fix."
```

---

### Task 7: the meta-guards that stop the three new lists going stale

Every scoped list in this file has something that notices when it goes stale —
`COMPARED_SLUGS` has `test_every_eligible_schema_is_compared`, the envelope carve-out has
`test_the_envelope_gap_is_still_the_shape_the_carve_out_assumes`. The three walkers added
above have a subtler failure mode: a walker that stops descending finds nothing and passes.

**Files:**
- Modify: `backend/tests/test_contracts.py`

**Interfaces:**
- Consumes: `_required_map`, `_closure_map`, `_constraint_map`.
- Produces: nothing.

- [ ] **Step 1: Write the test**

```python
@pytest.mark.req("FR-PLAT-48")
@pytest.mark.parametrize(
    ("walker", "slug", "path"),
    [
        (_required_map, "grouping", "evidence.source_level_stats.[]"),
        (_required_map, "model", "fit_result.bins.[]"),
        (_closure_map, "model-spec", "family_params"),
        (_constraint_map, "grouping", "evidence.source_level_stats.[].claim_count"),
    ],
)
def test_each_new_walker_reaches_a_nested_path_it_is_supposed_to(
    walker: Any, slug: str, path: str
) -> None:
    """The control for the three comparisons above, at the depth where they go quiet.

    A comparison that intersects two maps is green when both maps are empty. Counting what
    a walker produced does not catch a walker that stopped descending — the count shrinks
    with it, so any threshold expressed as a fraction of its own output moves out of the
    way of the defect it exists to catch. So this names one path per walker instead, each
    one nested at least two levels down and each chosen because a plausible refactor of the
    walker would lose it.
    """
    authored = _load(AUTHORED / f"{slug}.schema.json")
    reached = walker(authored, authored, AUTHORED)
    assert path in reached, (
        f"{walker.__name__} no longer reaches {path} in {slug} — the comparison built on "
        "it is now silent about everything beneath that point"
    )
```

- [ ] **Step 2: Run it**

```bash
uv run pytest backend/tests/test_contracts.py::test_each_new_walker_reaches_a_nested_path_it_is_supposed_to -q
```

Expected: PASS on all four.

The `_closure_map` case names `model-spec.family_params` rather than the root **on purpose**:
no authored schema declares `additionalProperties` in boolean form anywhere, so a root anchor
would assert a path that has never existed on that side and would be red from the first run.
That mistake was made while drafting this plan and is recorded here because the next person
extending `_closure_map` will reach for the root first too.

- [ ] **Step 3: Prove it fails on broken input**

Break the walker itself, which is the failure this guards:

```bash
python3 -c "import pathlib; p=pathlib.Path('backend/tests/test_contracts.py'); s=p.read_text(); p.write_text(s.replace('        elements.extend((owner, entry) for entry in variant.get(\"prefixItems\", ()))\n        for name, child in variant.get(\"properties\", {}).items():', '        for name, child in {}.items():', 1))"
```

If that replacement does not match, make the equivalent edit by hand: stop `_required_map`
descending into `properties`. Then:

```bash
uv run pytest backend/tests/test_contracts.py -q
```

Expected: FAIL — the meta-guard names the path the walker stopped reaching. Restore:

```bash
git checkout backend/tests/test_contracts.py
```

Then re-apply Tasks 4–7's edits, or stash before breaking. Simpler: make this proof the last
thing done before the commit, and use `git stash` rather than `git checkout`.

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_contracts.py
git commit -m "test(contracts): control the three new walkers at the depth where they go quiet"
```

---

### Task 8: the `contract-guard` skill, and one stale paragraph

Plan review 3 accepted this on 2026-08-22: *"the schema-drift knowledge stops being
rediscovered"*, owned by this workstream, as either a new skill or a section in
`contract-schema`. **A new skill.** `contract-schema` is about *authoring* a contract and is
already 143 lines; the guard is a different job with a different reader — someone changing
`test_contracts.py`, not someone changing a schema.

And `contract-schema` carries a paragraph that was **measured false on 2026-08-22**:

> Compare the admitted types with `null` removed, or the comparison reports a divergence on
> nearly every optional field and gets ignored.

The measurement that day found 70 of 417 authored paths nullable, 43 divergences of which 20
were real and were fixed, and one that was a re-published pre-fix bug. `CLAUDE.md` §12 forbids
leaving a known-stale skill in place.

**Files:**
- Create: `.claude/skills/contract-guard/SKILL.md`
- Modify: `.claude/skills/contract-schema/SKILL.md` — the nullability paragraph, and its
  `## Verified` block
- Modify: `.claude/skills/README.md` — the index row and the superpowers pairing row

**Interfaces:**
- Consumes: everything Tasks 1–7 learned.
- Produces: nothing code reads.

- [ ] **Step 1: Correct the stale paragraph**

In `.claude/skills/contract-schema/SKILL.md`, replace the paragraph beginning "Related, when
comparing a generated schema against a hand-authored one" with:

```markdown
Related, when comparing a generated schema against a hand-authored one: the generated side
marks every `X | None` nullable through `anyOf` and the authored side often does not. The
advice here used to be "compare with `null` removed", and it was **measured false on
2026-08-22**: 70 of 417 authored paths are nullable, the comparison found 43 divergences
rather than the predicted noise, 20 were real and were fixed, and one was a bug this skill's
own advice had helped re-publish. Nullability is compared for the slugs in
`NULLABILITY_COMPARED_SLUGS` and the remainder is scoped, not excused. See
`.claude/skills/contract-guard`.
```

- [ ] **Step 2: Append to `contract-schema`'s `## Verified` block**

Newest first, above the 2026-08-19 entry:

```markdown
2026-08-22 — W32-1, the contracts-and-drift-guard slice. The nullability paragraph above was
reversed: it advised stripping `null` before comparing, and the measurement that tested the
advice found 43 real divergences under it. The lesson is the one `CLAUDE.md` §0 states about
counts and this skill restated about a grep — an assertion about how noisy a check *would* be
is a prediction, and a prediction in a skill is read as a finding.
```

- [ ] **Step 3: Write the skill**

`.claude/skills/contract-guard/SKILL.md`. Frontmatter `name` must equal the folder name. It
must carry every non-obvious fact this slice paid for:

- **The walkers and what each is for** — `_deref` (cross-file `$ref`, bounded), `_variants`
  (flattens `anyOf`/`oneOf`/`allOf`/`then`/`else`, and **deliberately not `if`**, which is the
  discriminator test rather than a description), `_scalar_types`, `_type_map`.
- **A comparison that intersects two maps is green when both are empty.** Name paths;
  never count them. A threshold expressed as a fraction of the walker's own output moves out
  of the way of the defect it exists to catch.
- **The four defects found inside the guards themselves**, because each is a walker-writing
  trap rather than a schema trap: a clobbering `properties.update` that deleted a block's real
  definition when a conditional arm re-named it (36 paths to 28); a `const` with no `type`,
  which makes a branch read as typeless; an `ENVELOPE_FIELDS` literal wrong in both
  directions, under-declaring by eleven and carrying a field the envelope never had; and a
  `prefixItems` blindness that made every tuple field invisible while reporting success.
- **`required` is not symmetric.** Pydantic's set is about construction, an authored
  contract's is about what a reader may rely on. Compare one direction — the contract must
  never mark optional what the model requires — and say why in the test.
- **`_variants`' flattening is right for finding fields and wrong for deciding obligations.**
  `allOf` is conjunction and unions; `oneOf`/`anyOf` is disjunction and **intersects**;
  `then`/`else` contribute nothing unconditionally. A walker that unions everything invents
  requirements: it reported `bins.[].cuts` **and** `.levels` as model-required when
  `bins.[]` is a discriminated `oneOf` and no single arm requires both, and a contract
  "corrected" to match would have refused every valid categorical bin. **A guard that
  manufactures the defect it reports is worse than no guard**, because someone will fix it.
- **`additionalProperties` has two meanings** — `false` from `extra="forbid"`, and a value
  schema for an open map. The generated side uses the first and every authored contract uses
  the second, so a comparison written for one of them intersects an empty map and passes.
- **A hand-copy of a shared shape is where divergence starts.** `OneWayRow` was copied into
  three contracts; two of the copies required `claim_count` the model defaults, and one
  invented a `relativity` the model never had.
- **Every scoped list needs a meta-guard.** `COMPARED_SLUGS` /
  `test_every_eligible_schema_is_compared` is the pattern.
- **14 authored schemas have no generated counterpart** and are compared against nothing —
  three of them (`dataset-version`, `validation-report`, `validation-rule`) describe artifacts
  Phase 1a built. Named so the next reader does not rediscover it.
- A `## Verified` line: the date and **how** the procedure was confirmed, citing a failure it
  caught — this slice's `source_level_stats`, absent from the model since Phase 0 with every
  check green.

- [ ] **Step 4: Add both index rows**

In `.claude/skills/README.md`, add a row to the written-for-this-repo table. It has four
columns, and the first is the skill name linked to `contract-guard/SKILL.md` — a path that
resolves from `.claude/skills/README.md`, which is why it is described here rather than
written out.

| Column | Value |
|---|---|
| Skill | `contract-guard`, linked to its `SKILL.md` the way every neighbouring row links to its own |
| Purpose | Write or extend the schema-drift guard in `backend/tests/test_contracts.py` — what each walker reaches, why `if` is not followed, why `required` is compared in one direction only, the four defects found inside the guards themselves, and why a comparison that counts paths cannot catch a walker that stopped descending |
| Source | `self-written` |
| Last verified | `2026-08-22` |

A Purpose that names the concrete traps rather than the topic is the house style — compare
the `contract-schema` row above it.

Then add the superpowers pairing row in the table further down, matching its existing
three-column format.

- [ ] **Step 5: Add it to `CLAUDE.md` §12's list of self-written skills**

The sentence beginning "**Written for this repo:**" gains `contract-guard`.

- [ ] **Step 6: Run the docs audit and the full gate**

```bash
python3 scripts/audit-docs.py
```

```bash
uv run pytest -q
```

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/contract-guard/SKILL.md .claude/skills/contract-schema/SKILL.md .claude/skills/README.md CLAUDE.md
git commit -m "docs(skills): contract-guard, and correct contract-schema's nullability advice

Plan review 3, question 3, accepted 2026-08-22. The nullability paragraph advised stripping
null before comparing; the measurement that tested it found 43 divergences, 20 of them real.
CLAUDE.md 12 forbids leaving a known-stale skill in place."
```

---

## Closing the slice

- [ ] **Run the whole gate, both halves, reading each command's own exit code.** The commands
      are in Global Constraints above. `generate-contracts.py --check`, not the plain
      regenerate — the point is that the committed contract is already correct.
- [ ] **Confirm the frontend absorbed the contract change.** `pnpm --dir frontend generate:api`
      then `type-check`. `frontend.yml` triggers on `docs/contracts/openapi/**`, so this job
      can go red with no file under `frontend/` touched.
- [ ] **Record what was *not* delivered** (`CLAUDE.md` §13 rule 6). At minimum:
      **arm-level attribution is not in this slice.** Plan review 3 named four constraint-level
      axes and this delivers three. Attribution requires threading arm identity through
      `_variants`' return type and every caller — a GLM-only field declared on the GBM arm
      still passes, because `_type_map` unions every arm's contribution onto one dotted path.
      The design is recorded in `contract-guard`; the work is its own slice, `W32-1b`, owned by
      W32.
- [ ] **Update `docs/roadmap.md`** — plan review 3's questions 2(b) and 2(d) are discharged in
      part, and 3 in full. Do not mark 2(b) closed: three axes of four.
- [ ] **Write the ledger** — `docs/plans/2026-08-22-w6b-contracts-and-drift-guard-ledger.md`,
      per [`README.md`](README.md)'s table of the four file kinds.

---

## Self-Review

Run against the spec and the measurement, 2026-08-22.

**1. Spec coverage.** `FR-MODEL-15`'s "source Level statistics" — Task 1, with the contract in
Task 2 and the control in Task 3. `FR-PLAT-48`'s drift check — Tasks 4, 5, 6, controlled by
Task 7. `FR-OVR-6` — Task 4's marker. Plan review 3's question 2(b), the constraint-level
guard: **three of four axes**; arm-level attribution is named as out of scope in Closing rather
than silently dropped. Question 2(d), `source_level_stats`: covered. Question 3, the
`contract-guard` skill: Task 8. Two things this slice does **not** touch and that are not its
scope: the 14 uncompared authored schemas (recorded in the slice map §5, owner named there),
and the envelope gap, which `ENVELOPE_GAP_IS_RECORDED_NOT_FIXED` already owns.

**2. Placeholder scan.** Every guard task now states its measured expected result — Task 4:
one slug, one path, two names; Task 5: one slug, `custom-objective.params`; Task 6: two slugs,
three keywords. The first draft of this plan left Tasks 5 and 6 unpredicted, and writing the
measurement that removed the guesswork is what found the `oneOf` defect in Task 4's walker, so
the guesswork was not a harmless omission. Task 7's step 3 gives a `python3` edit that may not
match and names the manual equivalent — kept, because the *proof* is required and the
mechanism is incidental. One genuine unknown remains and is marked as a decision rather than a
gap: Task 6's `objective-certificate.result.checks`, where `minItems` 8 against 1 is a question
for the maintainer, with the alternative recorded.

**3. Type consistency.** `_required_map`, `_closure_map` and `_constraint_map` all take
`(document, node, base, path="")` and return a `dict` keyed by dotted path, matching
`_type_map`'s shape so a reader learns one idiom. Only `_required_at` and `_constraint_map`
carry `*, _depth=0`, because only they recurse through combinators themselves;
`_required_map` and `_closure_map` delegate that to `_variants`, which has its own guard.
`_ROOT_PATH` is defined once in Task 4 and used in Tasks 5, 6 and 7. `source_level_stats` is
`tuple[OneWayRow, ...]` in Task 1, `$ref`s `#/$defs/OneWayRows` in Task 2, and is named at
`evidence.source_level_stats.[]` in Tasks 3, 4 and 7 — the same path spelling `_type_map`
produces.

**Two risks worth stating.**

*Task 2 widens what is compared, and the widening is the point.* Six model fields become
*shared* paths for the first time, so `test_generated_and_authored_agree_on_scalar_types` and
Task 6's constraint guard both see them for the first time. Task 2 step 4 says to fix the
contract rather than the model — but if a disagreement runs the other way, that is a §0
question and stops the task rather than being resolved inside it.

*Task 6 step 3 changes a model constraint*, tightening `source_level_count` and
`target_level_count` to `ge=1`. That is the one place in this slice where the **spec wins over
the code**, and it can break a test fixture that builds an empty evidence. Run
`packages/pricing-core/tests/test_groupings.py` immediately after, not at the end.
