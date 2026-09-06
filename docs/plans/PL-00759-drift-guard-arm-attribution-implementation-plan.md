---
id: PL-759
family: plan
kind: leaf
title: Drift Guard Arm Attribution Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-23
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-23-w32-1b-drift-guard-arm-attribution.md
---

# Drift Guard Arm Attribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the contract drift guard compare a tagged union arm by arm, so that moving a field
from one arm to another — which every walker currently reports as no change at all — fails.

**Architecture:** Three of the four walkers in `backend/tests/test_contracts.py` flatten a schema to
`dotted.path -> value` and merge every composition branch into that one namespace. `_variants`
(`:538-579`) is where the arm identity is dropped: it returns `(document, node)` pairs and discards
which `oneOf` branch or which `if`-guarded `then` a node came from. The fix is to carry a **set of
discriminator constraints** alongside each variant and key the walkers on `(arm, path)`. The
discriminator *value* — `glm`, `xgboost`, `ebm` — is the one identity both sides can produce: the
generated side reads it from `discriminator.mapping`, the authored side from the sibling `if`'s
`const` or `enum`. Because a constraint is a set of values, the asymmetry that made this hard —
four discriminator values mapping onto three `oneOf` branches, since `xgboost` and `lightgbm`
share one `GbmSpec` — resolves without a special case. An unconditional field expands to every arm
before comparison, so a document with no unions produces exactly today's behaviour.

**Tech Stack:** Python 3.12, `pytest`, JSON Schema 2020-12, OpenAPI 3.1.

**Spec:** [`../specs/07-platform.md`](../specs/07-platform.md) FR-451 (the contract must not
drift) and [`../specs/00-overview.md`](../specs/00-overview.md) FR-9, which the affected tests
are marked with. The guard's own contract is
[`../../.claude/skills/contract-guard/SKILL.md`](../../.claude/skills/contract-guard/SKILL.md).

**Proposed slice id:** `W32-1b`, keeping the name the `contract-guard` skill already uses for this
work. The WK-692 slice boundaries in [`PL-00753-wk-664-and-wk-692-the-slice-map.md`](PL-00753-wk-664-and-wk-692-the-slice-map.md) are
recorded as *pending* maintainer acceptance; this is a proposal.

## Global Constraints

- No new requirement ids and no spec change. This is a test-infrastructure defect: the guard does
  not enforce what FR-451 already requires. No `Next free:` marker.
- **The union in `_type_map` was added deliberately** (WK-661, 2026-08-22) and must not be reverted.
  Its docstring at `:698-706` records that `properties.update(...)` took the walker from 36 paths
  to 28 by deleting a conditional refinement's base definition. Per-arm keying keeps the union
  *within* an arm and stops it *across* arms; a change that loses reach is a regression even if it
  makes the arm test pass.
- **`if` is still not followed as a description.** `_variants:561-564` says so and is right — the
  discriminator test is not a declaration that the artifact has a `model_type` field of type
  `{"const": "glm"}`. This plan reads `if` for the arm **tag** only, never for types, closure or
  constraints.
- `_required_at` (`:814-855`) is untouched. It deliberately does not use `_variants` because
  `allOf` conjoins, `oneOf`/`anyOf` intersects and `then`/`else` contribute nothing
  unconditionally — that is correct requiredness logic, not the same defect.
- **Out of scope, deliberately, and each for its own reason:**
  - `UNRESOLVED_CONSTRAINT_DISAGREEMENTS` (`:1109`) — FR-158 decides it and
    [`../open-questions.md`](../open-questions.md) `:83` is directive that the carve-out is removed
    in the same commit that makes the two sides agree. Nothing in arm attribution touches it.
  - Giving `dataset-version` and `validation-report` a generated side. Real coverage, its own
    slice, and it lands the moment someone registers them in `scripts/generate-contracts.py` —
    `test_every_eligible_schema_is_compared` (`:1398`) already guards it.
- Conventional Commits. Commit at the end of every task.

---

### Task 1: An arm has an identity

**Files:**
- Modify: `backend/tests/test_contracts.py:538-579` (`_variants`)
- Test: `backend/tests/test_contracts.py` — new tests beside the walker-reach block at `:1196`

**Interfaces:**
- Produces: `Arm = frozenset[tuple[str, frozenset[str]]]` — a set of
  `(discriminator dotted path, admitted values)` constraints in force at a node. The empty
  frozenset is the unconditional arm.
- Produces: `_variants(...) -> list[tuple[dict, dict, Arm]]` — a third element per variant.
- Produces: `_arms(document, node, base) -> frozenset[Arm]` — every **complete** single-valued arm
  a document declares, or `frozenset({frozenset()})` when it declares no union.

Both sides must produce the same tag for the same arm from different spellings, which is the whole
problem:

| | how the arm is spelled | how the tag is read |
|---|---|---|
| Generated | `oneOf` of `$ref`s plus `discriminator: {propertyName, mapping}` | the mapping key whose value is this branch's `$ref` |
| Authored | flat properties plus `allOf: [{"if": {...}, "then": {...}}]` | the sibling `if`'s `properties.<discriminator>.const` or `.enum` |

- [ ] **Step 1: Write the failing tests**

Add to `backend/tests/test_contracts.py`, near the walker-reach tests at `:1196`:

```python
@pytest.mark.req("FR-451")
def test_a_generated_union_branch_is_tagged_with_its_discriminator_values() -> None:
    """The generated side spells an arm as a `$ref` and a `discriminator.mapping` entry.

    `xgboost` and `lightgbm` share one `GbmSpec`, so **four discriminator values map onto
    three branches** and a tag must be a set of values rather than one value. That asymmetry
    is the reason this is not a dictionary lookup.
    """
    document = _load(GENERATED / "model-spec.schema.json")
    tags = {arm for _, _, arm in _variants(document, document, GENERATED) if arm}
    values = {v for arm in tags for _, v in arm}
    assert frozenset({"xgboost", "lightgbm"}) in values
    assert frozenset({"glm"}) in values


@pytest.mark.req("FR-451")
def test_an_authored_conditional_arm_is_tagged_from_its_sibling_if() -> None:
    """The authored side spells the same arm as `{"if": ..., "then": ...}`.

    `if` is read for the **tag** and never for the types — folding `{"const": "glm"}` into
    `model_type`'s admitted types would invent a field declaration, which is what
    `_variants` has always refused and still refuses.
    """
    document = _load(AUTHORED / "model-spec.schema.json")
    values = {
        v
        for _, _, arm in _variants(document, document, AUTHORED)
        for _, v in arm
    }
    assert frozenset({"glm"}) in values


@pytest.mark.req("FR-451")
def test_both_sides_declare_the_same_complete_arms() -> None:
    """The comparison is only meaningful if the two arm sets are the same set.

    If they differ, the drift is in the union's shape itself and every later per-arm
    comparison would be comparing arms that do not correspond — a failure worth its own
    message rather than forty confusing ones.
    """
    assert _arms(
        _load(GENERATED / "model-spec.schema.json"), ..., GENERATED
    ) == _arms(_load(AUTHORED / "model-spec.schema.json"), ..., AUTHORED)


@pytest.mark.req("FR-451")
def test_a_document_with_no_union_has_one_unconditional_arm() -> None:
    """Most of the thirteen compared slugs have no union at all.

    They must keep behaving exactly as they did, which per-arm keying achieves by making
    their single arm the empty constraint set rather than by special-casing them.
    """
    document = _load(AUTHORED / "dataset.schema.json")
    assert _arms(document, document, AUTHORED) == frozenset({frozenset()})
```

Fill the `...` with whatever `GENERATED`/`AUTHORED` path constants and root-node argument the
module already uses — read `:20-60` and the top of `test_generated_and_authored_agree_on_scalar_types`
(`:744-760`) for the idiom rather than inventing one. `dataset` is a placeholder for any
union-free compared slug; pick one from `COMPARED_SLUGS` (`:34`) after checking it has no `oneOf`.

- [ ] **Step 2: Run the tests to verify they fail**

Run:
```bash
uv run pytest backend/tests/test_contracts.py -k "arm or discriminator or unconditional" -v
```
Expected: FAIL — `_variants` returns 2-tuples, so the `for _, _, arm in` unpacking raises
`ValueError: not enough values to unpack`, and `_arms` does not exist.

- [ ] **Step 3: Add the arm type and the two readers**

Above `_variants`:

```python
#: The discriminator constraints in force at a node: `(dotted path of the discriminator
#: property, the values that reach here)`. The empty set is the unconditional arm — the node
#: is reached whatever the discriminator says — and it is what every union-free document
#: produces, so those documents keep behaving exactly as they did.
Arm = frozenset[tuple[str, frozenset[str]]]


def _discriminated_branches(node: dict[str, Any]) -> dict[str, frozenset[str]]:
    """`$ref` -> the discriminator values that select it, from an OpenAPI discriminator.

    The generated side's spelling. `discriminator.mapping` is value -> `$ref`, and this
    inverts it, which is what collapses `xgboost` and `lightgbm` onto the single `GbmSpec`
    branch they share.
    """
    discriminator = node.get("discriminator")
    if not isinstance(discriminator, dict):
        return {}
    inverted: dict[str, set[str]] = {}
    for value, ref in discriminator.get("mapping", {}).items():
        inverted.setdefault(ref, set()).add(value)
    return {ref: frozenset(values) for ref, values in inverted.items()}


def _condition_values(test: dict[str, Any]) -> tuple[str, frozenset[str]] | None:
    """The authored side's spelling: `{"if": {"properties": {"<name>": {"const"|"enum"}}}}`.

    Returns the constraint the sibling `then` is guarded by, or `None` when the `if` tests
    something this walker cannot express as a discriminator — a `required` test, or two
    properties at once. Returning `None` degrades that branch to unconditional, which is
    what the walker did for **every** branch before this change: strictly no worse, and the
    `then`-arm test in Task 2 covers the case that matters.
    """
    properties = test.get("properties", {})
    if len(properties) != 1:
        return None
    (name, constraint), = properties.items()
    if "const" in constraint:
        return name, frozenset({constraint["const"]})
    if "enum" in constraint:
        return name, frozenset(constraint["enum"])
    return None
```

- [ ] **Step 4: Carry the tag through `_variants`**

Change the signature to accept and return the arm, threading the path prefix so a **nested** union's
discriminator cannot collide with the outer one — three unions live at three depths (`ModelSpec`,
`FitResult`, `EbmFeatureBins` at `modelling.py:1742`), and a bare property name would conflate them:

```python
def _variants(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    *,
    path: str = "",
    arm: Arm = frozenset(),
    _depth: int = 0,
) -> list[tuple[dict[str, Any], dict[str, Any], Arm]]:
```

In the body, after the `_deref`:

```python
    found = [(document, node, arm)]
    branch_tags = _discriminated_branches(node)
    for keyword in ("anyOf", "oneOf", "allOf"):
        for branch in node.get(keyword, []):
            values = branch_tags.get(branch.get("$ref", ""))
            child = (
                arm | {(f"{path}.{node['discriminator']['propertyName']}".lstrip("."), values)}
                if values
                else arm
            )
            found.extend(
                _variants(document, branch, base, path=path, arm=child, _depth=_depth + 1)
            )
```

The existing `then`/`else` loop follows this one and is rewritten next; leave it in place until
then, so the function still returns.

For that loop, read the **sibling `if`** — which the current code discards and which is
where the authored side's whole arm identity lives:

```python
    condition = node.get("if")
    guard = _condition_values(condition) if isinstance(condition, dict) else None
    for keyword in ("then", "else"):
        branch = node.get(keyword)
        if not isinstance(branch, dict):
            continue
        child = arm
        if guard is not None and keyword == "then":
            name, values = guard
            child = arm | {(f"{path}.{name}".lstrip("."), values)}
        found.extend(
            _variants(document, branch, base, path=path, arm=child, _depth=_depth + 1)
        )
```

`else` stays unconditional. Its true constraint is the complement of the `if`, which this
representation cannot express as a value set, and inventing one would be worse than the honest
under-constraint: an `else` field lands in every arm, so a comparison can produce a false pass
there but never a false failure. Say exactly that in a comment — an executor who "fixes" it later
needs to know it was considered.

Update the docstring: the two paragraphs about `then`/`else` and about `if` stand as written; add
one saying the sibling `if` is now read for the tag and still not for the description.

- [ ] **Step 5: Write `_arms`**

```python
def _arms(document: dict[str, Any], node: dict[str, Any], base: pathlib.Path) -> frozenset[Arm]:
    """Every **complete, single-valued** arm this document declares.

    A variant's own tag may name several values at once — the shared `GbmSpec` branch is
    tagged `{xgboost, lightgbm}` — so the tags are not themselves the arms. Splitting them
    to one value each gives the coordinate system both sides are expanded onto, and it is
    the same set whether it was built from a `discriminator.mapping` or from four `if`s.

    A document with no union yields `{frozenset()}`: one unconditional arm, which is what
    keeps the union-free majority of `COMPARED_SLUGS` comparing exactly as before.
    """
    by_property: dict[str, set[str]] = {}
    for _, _, arm in _variants(document, node, base):
        for name, values in arm:
            by_property.setdefault(name, set()).update(values)
    if not by_property:
        return frozenset({frozenset()})
    combinations: list[Arm] = [frozenset()]
    for name in sorted(by_property):
        combinations = [
            existing | {(name, frozenset({value}))}
            for existing in combinations
            for value in sorted(by_property[name])
        ]
    return frozenset(combinations)
```

The cartesian product across independent discriminators is deliberate and worth watching: two
unions of four values each give sixteen arms, and each walker's output grows with it. Three unions
at Phase 1b's sizes is fine; if a fourth appears and the suite slows, the fix is to key on the
constraint set rather than expand, not to drop arm attribution.

- [ ] **Step 6: Fix every other `_variants` caller**

```bash
grep -n "_variants(" backend/tests/test_contracts.py
```

Every call site unpacks 2-tuples today. Give each a third name — `_` where the arm is not used yet;
Tasks 2-4 replace those in turn.

- [ ] **Step 7: Run the tests to verify they pass**

Run:
```bash
uv run pytest backend/tests/test_contracts.py -v
```
Expected: the four new tests PASS and **every existing test still passes**. Nothing in this task
changes what any walker returns — only what `_variants` hands them — so a failure here is a
threading mistake, not a discovered drift.

- [ ] **Step 8: Commit**

```bash
git add backend/tests/test_contracts.py
git commit -m "test(w32-1b): a union branch carries its discriminator values"
```

---

### Task 2: `_type_map` compares arm by arm

**Files:**
- Modify: `backend/tests/test_contracts.py:680-742` (`_type_map`), `:744-812` (the test)
- Modify: `backend/tests/test_contracts.py:1306-1330` and `:1424-1490` (the two other `_type_map` consumers)
- Test: `backend/tests/test_contracts.py`

**Interfaces:**
- Consumes: `Arm`, `_variants`, `_arms` from Task 1.
- Produces: `_type_map(...) -> dict[tuple[Arm, str], frozenset[str]]`.
- Produces: `_expand(m, arms) -> dict[tuple[Arm, str], frozenset[str]]` — every entry re-keyed onto
  the complete arms it applies to.
- Produces: `_paths(m) -> dict[str, frozenset[str]]` — the arm-flattened view, which is exactly
  today's return value and is what the reach tests keep using.

**The expansion is the load-bearing idea, and it is not obvious.** The two sides do not put the
same field in the same place: the authored `model-spec.schema.json` is flat-plus-`if`/`then` by
deliberate design (its `$comment` at `:6` says so), so `model_family_slug` is declared
**unconditionally** — arm `∅`. The generated side declares `model_family_slug` inside each of
`GlmSpec`, `GbmSpec` and `EbmSpec` —
three non-empty arms. Comparing raw keys would report every shared field as drift. So each side is
expanded first: an entry constrained by `C` applies to every complete arm that satisfies `C`, and
`C = ∅` applies to all of them. After expansion the two sides are on the same coordinates and
equality means what it says.

- [ ] **Step 1: Write the failing test — the measured case**

The defect has a known, reproducible instance. Moving the `family` property from the glm arm to the
gbm arm in `docs/contracts/schemas/model-spec.schema.json` leaves the two `_type_map` outputs
**equal dict-for-dict** today; every comparison passes.

```python
@pytest.mark.req("FR-451")
def test_a_field_moved_between_arms_is_drift(tmp_path: pathlib.Path) -> None:
    """**The defect, on the case it was measured on.**

    `family` belongs to the glm arm. Moving it to the gbm arm is drift of the worst kind —
    the field set is unchanged, so a walker that merges the arms into one namespace sees
    nothing at all, and the guard reports a contract it has not checked. Every other test in
    this module went on passing with the schema in that state.
    """
    authored = _load(AUTHORED / "model-spec.schema.json")
    moved = _move_property_between_arms(authored, "family", source="glm", target="xgboost")

    generated = _load(GENERATED / "model-spec.schema.json")
    arms = _arms(generated, generated, GENERATED)
    before = _expand(_type_map(authored, authored, AUTHORED), arms)
    after = _expand(_type_map(moved, moved, AUTHORED), arms)
    assert before != after, (
        "moving a property between arms produced an identical map — the walker is still "
        "merging arms into one namespace"
    )


@pytest.mark.req("FR-451")
def test_an_arm_specific_type_is_not_unioned_across_arms() -> None:
    """`monotone_constraints` reports a union no single arm admits.

    Today one dotted path carries `{null, object, string}` — the merge of **two** arms:
    `GbmSpec`'s `Literal["derived_from_factors", "none"]` (`modelling.py:1327`, `string`) and
    `EbmSpec`'s `dict[str, int] | None` (`:1441`, `object` + `null`). `GlmSpec` has no such
    field. No arm admits all three types, so the guard is comparing a shape that does not
    exist and would accept a contract declaring any one of them in either arm.

    `GbmFitResult.monotone_constraints` (`:1640`) is **not** part of this union — measured,
    not assumed: it lands at `fit_result.monotone_constraints.[]` in `model.schema.json` and
    reports `{integer}`. Recorded because the three-way reading is the intuitive one and it
    is wrong.

    `keep_null=True` is required, not decoration: `model-spec` is in
    `NULLABILITY_COMPARED_SLUGS` (`:607-616`), so the comparison test walks it that way, and
    without it `null` is stripped and this assertion can never fail — it would pass today
    and after the fix, testing nothing.
    """
    generated = _load(GENERATED / "model-spec.schema.json")
    by_arm = _type_map(generated, generated, GENERATED, keep_null=True)
    for (arm, path), types in by_arm.items():
        if path.endswith("monotone_constraints"):
            assert types != frozenset({"null", "object", "string"}), (
                f"{arm} still carries the cross-arm union"
            )
```

Write `_move_property_between_arms` in the test module as a small pure helper over a deep-copied
document: find the `then` block whose sibling `if` names `source`, pop `family` from its
`properties`, and put it in the `target` arm's. Do **not** write the mutated schema to disk — this
test must not be able to leave `docs/contracts/` modified if it fails midway.

- [ ] **Step 2: Run the tests to verify they fail**

Run:
```bash
uv run pytest backend/tests/test_contracts.py -k "moved_between_arms or arm_specific_type" -v
```
Expected: the first FAILS on its own assertion message (the maps are equal — the defect,
reproduced); the second FAILS with `NameError` or on the union.

- [ ] **Step 3: Re-key `_type_map`**

Three changes to the body at `:707-742`:

1. `for owner, variant, arm in _variants(document, node, base):`
2. Key the `properties`/`elements` accumulators by `(arm, name)` rather than `name`, and pass the
   arm down the recursion so a nested variant's tag composes with its parent's.
3. Key `found` by `(arm, path)`. The union at `found[key] = found.get(key, frozenset()) | types`
   **stays** — it now unions within an arm, which is the WK-661 behaviour the docstring defends, and no
   longer across arms, which is the defect.

Then:

```python
def _expand(
    by_arm: dict[tuple[Arm, str], frozenset[str]], arms: frozenset[Arm]
) -> dict[tuple[Arm, str], frozenset[str]]:
    """Re-key each entry onto every complete arm its constraints admit.

    The two sides declare the same field in different places: the authored `model-spec` is
    flat-plus-`if`/`then` by design (its `$comment` says so), so `model_family_slug` is
unconditional,
    while the generated side declares it inside each arm's `$ref`ed subschema. Comparing raw
    keys would call every shared field drift. Expanding both onto the complete arm set puts
    them on one coordinate system, after which equality means what it says.
    """
    expanded: dict[tuple[Arm, str], frozenset[str]] = {}
    for (constraints, path), value in by_arm.items():
        for arm in arms:
            if _admits(constraints, arm):
                key = (arm, path)
                expanded[key] = expanded.get(key, frozenset()) | value
    return expanded
```

`_admits(constraints, arm)` asks whether a complete arm satisfies every constraint that reaches a
node — so `{("model_type", {"xgboost"})}` satisfies a `{("model_type", {"xgboost", "lightgbm"})}`
constraint, which is how the shared `GbmSpec` branch lands in both gbm arms:

```python
def _admits(constraints: Arm, arm: Arm) -> bool:
    """Does a complete `arm` satisfy every constraint in `constraints`?

    A constraint names the values that reach a node; the arm names one value per
    discriminator. The arm satisfies a constraint when its value is among them — and a
    discriminator the arm does not mention cannot satisfy a constraint on it.
    """
    chosen = {name: values for name, values in arm}
    return all(
        name in chosen and chosen[name] <= values for name, values in constraints
    )
```

Written as an explicit predicate rather than a `constraints <= arm` subset test, deliberately: the
subset relation between two constraint sets is the kind of expression that reads as correct while
being backwards, and it would be backwards here.

- [ ] **Step 4: Add `_paths` and keep the reach tests working**

```python
def _paths(by_arm: dict[tuple[Arm, str], frozenset[str]]) -> dict[str, frozenset[str]]:
    """The arm-flattened view: exactly what `_type_map` returned before arm attribution.

    The reach tests ask "does the walker get to this dotted path at all", which is a
    question about coverage and not about arms. Flattening here keeps that question
    answerable in one line rather than re-keying `REACHED_NESTED_PATHS`'s literals, which
    would make a coverage assertion depend on a union's shape.
    """
    flat: dict[str, frozenset[str]] = {}
    for (_, path), types in by_arm.items():
        flat[path] = flat.get(path, frozenset()) | types
    return flat
```

**`_type_map` is not in the walker-reach parametrize.** Its four entries at `:1189-1193` are
`_required_map` twice, `_closure_map` and `_constraint_map` — so
`test_each_new_walker_reaches_a_nested_path_it_is_supposed_to` (`:1196-1213`) needs **no change in
this task**. It is Tasks 3 and 4 that touch it. Do not add a `_type_map` entry to it either; the
reach control exists for the walkers that had none, and `_type_map`'s reach is asserted directly by
the two tests below.

Three tests consume `_type_map`'s keys and each needs `_paths`:

| Test | Line | What it does with the keys |
|---|---|---|
| `test_generated_and_authored_agree_on_scalar_types` | `:796-797` | compares the two maps — rewritten in Step 5 below, not with `_paths` |
| `test_the_comparison_reaches_the_nested_fields_this_slice_added` | `:1317-1318` | `set(...) & set(...)`, then membership |
| `test_the_type_comparison_reaches_the_one_way_row` | `:1441-1442`, and again at `:1481-1486` | two separate uses: an intersection, then a `startswith(f"{block}.")` filter |

The last one is easy to half-fix: `:1441` and `:1481` are in the **same test**, and the second use
filters on a path prefix, which a `(arm, path)` tuple key silently fails rather than errors —
`"…".startswith` on a tuple raises, but `path.startswith` where `path` is now a tuple element only
works if `_paths` was applied. Apply it at both sites and re-run that test specifically.

- [ ] **Step 5: Update the comparison test**

`test_generated_and_authored_agree_on_scalar_types` (`:744`) compares the two maps directly. It
becomes: build `arms` from the generated side, assert the two `_arms` sets are equal first (a
clearer failure than forty mismatched keys), then compare `_expand(...)` of each.

The failure message must name the arm. `"model_type=glm: .family generated={string} authored={}"`
is actionable; a bare dict diff over 200 keys is not.

- [ ] **Step 6: Run the tests to verify they pass**

Run:
```bash
uv run pytest backend/tests/test_contracts.py -v
```
Expected: all pass, **including** the two new ones.

If `test_generated_and_authored_agree_on_scalar_types` now fails on a real slug, the guard has
found genuine drift that arm-merging was hiding. **Do not adjust the walker to make it pass.**
Record it, and treat it under `CLAUDE.md` §0 — which of the two sides is wrong is a real question.
That outcome is a success for this slice, not a blocker; put it in the ledger and raise it.

- [ ] **Step 7: Commit**

```bash
git add backend/tests/test_contracts.py
git commit -m "test(w32-1b): scalar types are compared arm by arm"
```

---

### Task 3: `_closure_map` compares arm by arm

**Files:**
- Modify: `backend/tests/test_contracts.py:943-984` (`_closure_map`), `:989-1013` (the test)

**Interfaces:**
- Consumes: `Arm`, `_expand`, `_admits`, `_paths` from Tasks 1-2.
- Produces: `_closure_map(...) -> dict[tuple[Arm, str], <its existing value type>]`.

Same defect, same shape: `:943-984` merges arms into one namespace, so an arm that closes a map
and an arm that leaves it open are indistinguishable.

- [ ] **Step 1: Read it and confirm the shape matches**

```bash
sed -n '943,1033p' backend/tests/test_contracts.py
```

Confirm two things before changing anything: the accumulator merges across `_variants` exactly as
`_type_map` did, and the value type (a bool, a set, or something else) unions sensibly within an
arm. If the merge is a last-writer-wins `.update(...)` rather than a union, say so in the commit
message — the within-arm semantics need deciding, not just the across-arm keying.

- [ ] **Step 2: Write the failing test**

An arm-specific closure difference, in the same shape as Task 2 Step 1: mutate a deep copy so one
arm's open map becomes closed, and assert the expanded maps differ. Model the test's docstring on
what an open map means here — `additionalProperties` — and say why per-arm matters: a contract
that closes a map in one arm and leaves it open in another admits different documents per arm, and
a merged view reports whichever it saw last.

- [ ] **Step 3: Run it to verify it fails**

Run:
```bash
uv run pytest backend/tests/test_contracts.py -k closure -v
```
Expected: FAIL — the two maps are identical.

- [ ] **Step 4: Re-key and expand**

Mirror Task 2 Steps 3 and 5. **`_expand` is reused unchanged here** — `_closure_map` returns
`dict[str, frozenset[str]]` (`:943-984`), the same value type `_type_map` returns, and the same
`|` union is the right merge. No `_expand_closure`, no `TypeVar`: this is the one of the three
walkers whose values already fit. (Task 4's do not, and that task writes its own.)

- [ ] **Step 5: Run the tests to verify they pass**

Run:
```bash
uv run pytest backend/tests/test_contracts.py -v
```
Expected: all pass **after one required edit**, which is not optional and not conditional:
`_closure_map` **is** in the walker-reach parametrize, at `:1192`
(`(_closure_map, "model-spec", "family_params")`). The test does `path in reached`, and `reached`
is now keyed by tuples, so it goes red. Wrap that one entry with `_paths` — a lambda in the
parametrize, or a named adapter if Task 4 will want the same shape (it will). The other three
entries are untouched by this task.

- [ ] **Step 6: Commit**

```bash
git add backend/tests/test_contracts.py
git commit -m "test(w32-1b): open-map closure is compared arm by arm"
```

---

### Task 4: `_constraint_map` compares arm by arm

**Files:**
- Modify: `backend/tests/test_contracts.py:1035-1079` (`_constraint_map`), `:1116-1153` (the test),
  `:1158-1183` (the carve-out test), `:1193` (its walker-reach parametrize entry)

**Interfaces:**
- Consumes: `Arm`, `_admits`, `_paths` from Tasks 1-2. **Not `_expand`** — see below.
- Produces: `_constraint_map(...) -> dict[tuple[Arm, str], dict[str, Any]]`, and
  `_expand_constraints(m, arms) -> dict[tuple[Arm, str], dict[str, Any]]` beside it.

**`_expand` cannot be reused here, and this is the reason Task 3 could.** `_expand` merges values
with `|` because `_type_map` and `_closure_map` both return `frozenset[str]`. `_constraint_map`
returns `dict[str, Any]` (`:1042`), where `|` is dict-merge — last-writer-wins per keyword, the
exact defect Step 1's test exists to catch. Write `_expand_constraints` with the merge Step 3
decides, and do not let a passing type-check stand in for having chosen one: `dict | dict` is
valid Python 3.12 and silently reintroduces the bug.

**This one is worse than the other two.** `_constraint_map` ends in `.update(declared)`, which is
last-writer-wins **per keyword**: an arm declaring `minimum: 0` and another declaring `minimum: 1`
at the same path leave whichever the walk reached last, with no trace. The other two walkers at
least union.

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.req("FR-451")
def test_two_arms_declaring_different_bounds_are_both_kept() -> None:
    """**Last-writer-wins, per keyword** — the sharpest form of this defect.

    Two arms bounding the same path differently do not produce a conflict, a union or a
    failure: one silently replaces the other, and the guard then compares a bound only one
    arm declares against a contract where both do.
    """
```

Build a document with two arms constraining one path to different `minimum`s, walk it, and assert
both survive under their own arm keys.

- [ ] **Step 2: Run it to verify it fails**

Run:
```bash
uv run pytest backend/tests/test_contracts.py -k bounds -v
```
Expected: FAIL — one bound only.

- [ ] **Step 3: Re-key, and decide the within-arm merge**

Key by `(arm, path)` as before. Within one arm, two variants may still name the same keyword —
`allOf` conjunction is the legitimate case. `.update(...)` is wrong there too, but fixing it is a
second decision: **keep `.update` within an arm for this slice** and add a comment naming it as a
known remaining gap, or resolve it if the correct conjunction is unambiguous for the keywords
actually in use (`minimum`, `maximum`, `minItems`, `pattern`).

Whichever you choose, write it in the ledger as an explicit `CLAUDE.md` §13 verdict rather than
leaving it implicit in the code.

- [ ] **Step 4: Update the comparison test and the carve-out**

`test_generated_and_authored_agree_on_scalar_constraints` (`:1116`) consults
`UNRESOLVED_CONSTRAINT_DISAGREEMENTS` (`:1109`), whose one entry is keyed
`{"objective-certificate": {("result.checks", "minItems")}}` — a **bare path**, not an arm-keyed
one. `objective-certificate` has no union, so its only arm is `∅` and the carve-out still matches
after expansion. Confirm that rather than assume it: add an assertion, or check that
`test_the_escalated_constraint_disagreements_are_still_unresolved` (`:1158`) still passes and
**still fails when the carve-out is removed**, which is the only thing that proves it is still
doing its job.

- [ ] **Step 5: Fix the walker-reach parametrize entry**

`_constraint_map` is the fourth entry at `:1193`
(`(_constraint_map, "grouping", "evidence.source_level_stats.[].claim_count")`). Like Task 3's,
it now returns tuple keys and `path in reached` goes red. Wrap it with `_paths`, the same adapter
Task 3 introduced. All four entries in that parametrize are then either untouched (`_required_map`,
twice) or adapted; nothing in it is left comparing a tuple to a string.

- [ ] **Step 6: Run the tests to verify they pass**

Run:
```bash
uv run pytest backend/tests/test_contracts.py -v
```
Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add backend/tests/test_contracts.py
git commit -m "test(w32-1b): scalar constraints are compared arm by arm"
```

---

### Task 5: Correct the skill, run the gate, record the slice

**Files:**
- Modify: [`../../.claude/skills/contract-guard/SKILL.md`](../../.claude/skills/contract-guard/SKILL.md) — `:38-41` and `:203-217`
- Modify: [`../roadmap.md`](../roadmap.md) — a slice record, appended
- Create: `2026-08-23-w32-1b-drift-guard-arm-attribution-ledger.md`

**Interfaces:**
- Consumes: Tasks 1-4 complete and committed.

- [ ] **Step 1: Update the skill's walker contract**

`SKILL.md:38-41` describes the walkers as returning `dotted.path -> value`. That is now the
`_paths` view; the walkers return `(arm, path) -> value`. Rewrite the section to describe both, say
which one a new walker should return (arm-keyed), and state the expansion rule — an unconditional
declaration reaches every arm — because a walker author who misses it will produce false failures
on the flat-authored documents.

- [ ] **Step 2: Correct the stale counts in the same pass**

`SKILL.md:203-217` says **14** uncompared schemas and **three** Phase-1a ones. Both are stale:
W32-2 gave `validation-rule` a generated side, so it is **13** and **two**. `COMPARED_SLUGS`
(`:34`) holds 13 slugs while the skill and some docstrings still say "twelve".

`CLAUDE.md` §12: a skill that turns out to be wrong is fixed in the same session, with its
`Verified` date refreshed. Do both. Sweep the docstrings too:

```bash
grep -rn "twelve\|fourteen" backend/tests/test_contracts.py .claude/skills/contract-guard/
```

- [ ] **Step 3: Run the Python half of the gate**

```bash
uv run ruff check .
uv run mypy
uv run lint-imports
uv run pytest -q
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
```
Expected: every command exits 0. This slice changes no runtime code and no contract, so
`generate-contracts.py --check` must be clean; if it is not, something in Tasks 1-4 wrote to
`docs/contracts/` and Task 2 Step 1's "do not write the mutated schema to disk" was not followed.
Check `git status --short docs/contracts/` and restore.

The frontend half is **not** required: nothing here touches the OpenAPI document or the generated
client. Say so in the ledger rather than silently skipping it.

- [ ] **Step 4: Prove the guard now bites, on the real files**

The whole slice exists so that one class of change fails. Prove it end to end rather than only in
the unit test:

```bash
python3 - <<'PY'
import json, pathlib
p = pathlib.Path("docs/contracts/schemas/model-spec.schema.json")
d = json.loads(p.read_text())
# move `family` from the glm arm to the gbm arm
PY
uv run pytest backend/tests/test_contracts.py -k scalar_types -q
git checkout -- docs/contracts/schemas/model-spec.schema.json
git status --short docs/contracts/
```
Expected: the test FAILS naming the arm, and `git status` prints nothing after the restore. Paste
the failure message into the ledger — this is the `CLAUDE.md` §13 evidence that the enforcement was
proven on deliberately broken input, and the specific message is what makes it evidence rather than
an assertion.

If the heredoc is refused in this worktree, write the mutation as a file under
`$CLAUDE_JOB_DIR/tmp` and run it with `uv run python`.

- [ ] **Step 5: Write the ledger and the slice record**

Create `docs/plans/2026-08-23-w32-1b-drift-guard-arm-attribution-ledger.md` with the gate output,
Step 4's failure message, the Task 4 Step 3 decision about within-arm merging, and **any real drift
Task 2 Step 6 uncovered**, each with which side this slice believes is wrong and why — recorded,
not fixed, unless fixing it was trivially unambiguous.

Append the slice record to [`../roadmap.md`](../roadmap.md), following the W32-6 record's shape,
and note the two items this slice deliberately left: the `UNRESOLVED_CONSTRAINT_DISAGREEMENTS`
carve-out (FR-158's, not this one's) and the two schemas with no generated side.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/contract-guard/SKILL.md docs/
git commit -m "docs(w32-1b): record the drift guard slice and correct the guard's own counts"
```
