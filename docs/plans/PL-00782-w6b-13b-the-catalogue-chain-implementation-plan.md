---
id: PL-782
family: plan
kind: leaf
title: W6b-13b — The Catalogue Chain Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-24
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-24-w6b-13b-catalogue-chain.md
---

# W6b-13b — The Catalogue Chain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a built-in validation rule's catalogue lineage recordable through the API, and
its default thresholds readable from the catalogue rather than only from literals buried in
`pricing-core`.

**Architecture:** Two legs against one catalogue. **Leg A** restores `catalogue_id` to the
rule-create path — the column, the read-back and the DB constraint already exist, so only
`RuleCreate`, the handler and `create_rule` are missing, plus a refusal for an id that names
no catalogue entry. **Leg B** adds a `params` field to `BuiltinRule`, populates it for the
fifteen catalogue entries whose check actually reads a defaulted threshold, and has the seed
write it into the rule body instead of `{}`. The literals in `pricing_core.data.validate`
stay exactly where they are: they remain the floor for a *workspace-authored* rule that
supplies no params. The flow is catalogue → params, never params → thresholds, which is why
FR-56's "no parameter metadata exists from which a threshold allowlist could be derived"
does not block this — a catalogue entry declares its own defaults rather than filtering
someone else's.

**Tech Stack:** Python 3.12 + `uv` workspace · Pydantic v2 · FastAPI · SQLAlchemy 2.x async ·
pytest

**Spec:** [`../specs/01-data-management.md`](../specs/01-data-management.md) — FR-68 and
FR-56, and §4.4's catalogue.

## Global Constraints

- **`pricing-core` stays importable standalone** with zero FastAPI/SQLAlchemy/Redis
  dependencies. This plan adds no import to it; it only adds a test.
- **Nobody hand-writes a shape that already exists in `model-schema`.** `catalogue_id` is
  already declared on `ValidationRule`; Leg A wires the existing field through, it does not
  redeclare it.
- **Requirement IDs are permanent** — this plan takes no new id. Every `FR-` cited is defined
  in `01-data-management.md` today.
- **No pandas in new code.**
- `mypy --strict` and `ruff` must pass; run **both halves** of the gate before pushing
  (`.claude/skills/dev-commands`). This plan touches no frontend source, so the frontend half
  should be unchanged — run it anyway.
- **Money is integer pence/cents** (FR-10). `VR-ACT-12`'s two bounds are minor-unit money
  and are written as **integers** in the catalogue — `0` and `1_000_000_000_000`. This is the
  one place the catalogue value is not textually identical to its fallback; see Task 3.

## Scope boundary — read this before touching anything

**This slice changes catalogue *shape* and the seeded *body*. It does not change
`examples/fremtpl2/seed.py`.**

That sentence is the one a later reviewer needs, so here is its evidence rather than its
assertion. `seed.py` touches `BUILTIN_RULES` in exactly three places — an import at `:280`,
`rule.slug` at `:294` to build `catalogue_id_by_slug`, and `len(BUILTIN_RULES)` at `:426` in a
summary line. None of them reads a field this plan adds, and `seed.py` carries its own `RULES`
(`:197`) with its own populated params and its own slugs. Two further consequences checked and
recorded here so nobody re-derives them:

- `BuiltinRule` does **not** appear in `docs/contracts/`, so this adds no contract drift and
  requires no `generate:api` regeneration.
- No test enumerates `BuiltinRule`'s fields exhaustively; the catalogue tests read
  `.catalogue_id`, `.slug`, `.severity`, `.check` and `.layer` by name.
  `test_validation_catalogue.py:24` pins `len(BUILTIN_RULES) == 38`, which is a count of
  entries and not of fields, so an added field does not trip it.

An additive field with a default is therefore invisible to every existing consumer.

**The predicate that matters is a consumer *read* of the changed part, not the type being
touched.** "Does this change `BuiltinRule`?" answers yes and is the wrong question; "does any
consumer read what changed?" answers no and is the one that decides. Both are recorded here
because they disagree, and the first one alone would have reserved a file this slice never
opens.

## Two corrections to the inputs, recorded not applied

Filed plans are frozen (`README.md`), so neither of these edits an existing document.

1. **The slice map's cell over-scopes Leg B.**
   [`PL-00786-wk-664-the-revised-slice-map.md`](PL-00786-wk-664-the-revised-slice-map.md) §3 describes
   this slice as replacing "the seed's empty `params` for all 38 rules". It is **15 of 38**.
   The other 23 rules run checks that read no defaulted parameter, so their `params: {}` is
   correct rather than defective, and writing anything into them would invent a threshold the
   code does not have. The fifteen are enumerated in Task 3.
2. **FR-68's and FR-56's tails name owner `W6b-13`**, which the revised map re-cut
   into `W6b-13a`/`W6b-13b`. The owner clauses are stale in the same way the map's own P3 item
   describes for `01:844`. Tasks 1 and 4 amend those two tails as part of delivering them, so
   the staleness is resolved by the work rather than separately.

## `fail_above` is deliberately excluded

`psi_column` reads `fail_above` (default `0.25`, `validate.py:1460`), publishes it in
`CheckOutcome.threshold`, and **never branches on it** — the only comparison is against
`warn_above`. §4.4's 2026-08-15 amendment struck the two-band reading of VR-DST-1 and its tail
states that **two bands are two rules**: one `warn` at 0.10 and one `fail` at 0.25, both in the
set. The 0.25 band is therefore relocated to a second catalogue rule that does not exist yet,
not deleted.

**Consequence for this plan, ruled by the workstream lead on 2026-08-24:** VR-DST-1's catalogue
entry carries `warn_above` **only**. Promoting `fail_above` into the governed catalogue would
re-commit struck spec text as a shipped default. Three things are explicitly **out of scope**
and belong to a separate item with its own owner:

- the residual `fail_above` read at `validate.py:1460`,
- `frontend/src/api/profiles.ts:42,52-54`, which cites §4.4 for the two-band form and
  implements it,
- the missing second catalogue rule for the `fail` band.

Do not touch any of the three in this slice.

## File Structure

| File | Change | Responsible for |
|---|---|---|
| `packages/model-schema/src/model_schema/validation.py` | Modify `:205-235`, `:246+` | `BuiltinRule.params`, the `_rule` factory, the fifteen populated entries |
| `packages/model-schema/tests/test_validation_catalogue.py` | Modify | Catalogue-shape tests, including the negative control |
| `packages/pricing-core/tests/test_builtin_rule_checks.py` | Modify | Anti-drift: every catalogue key is one its check actually reads |
| `backend/src/app/api/validation.py` | Modify `:82-93`, `:263-289` | `RuleCreate.catalogue_id`, handler pass-through |
| `backend/src/app/platform/validation_rules.py` | Modify `:140`, `:160-236` | Seeded params, `create_rule`'s parameter and its refusal |
| `backend/tests/test_api_validation_rules.py` | Modify | Round-trip, refusal, and seeded-params tests |
| `docs/specs/01-data-management.md` | Modify FR-68 (`:166`), FR-56 (`:118`) | Retire the two "declared and unfixed/unbuilt" tails |

---

### Task 1: `catalogue_id` reaches the create path

FR-68's tail records the defect: *"the create handler drops `catalogue_id`, so that
derivation is unreachable through the API and the lineage this sentence relies on cannot be
recorded by any caller."* Everything downstream already exists — `ValidationRule.catalogue_id`
(`validation.py:100`) with its validator refusing unknown ids (`:103-106`), `to_schema` already
emitting `row.catalogue_id`, and the DB constraint `builtin_rule_names_its_catalogue_entry`
(`models.py:1120-1144`) already permitting a non-builtin row to carry one. Only the write path
is missing.

**Files:**
- Modify: `backend/src/app/api/validation.py:82-93` (`RuleCreate`), `:263-289` (handler)
- Modify: `backend/src/app/platform/validation_rules.py:160-236` (`create_rule`)
- Modify: `docs/specs/01-data-management.md:166` (FR-68's tail)
- Test: `backend/tests/test_api_validation_rules.py`

**Interfaces:**
- Consumes: nothing from other tasks. Task 1 is independent of Leg B and can be reviewed alone.
- Produces: `rule_service.create_rule(..., catalogue_id: str | None = None, ...)`. Task 4 does
  not call it — the seed builds `ValidationRuleRow` directly — so no later task depends on this
  signature.

- [ ] **Step 1: Write the failing round-trip test**

Add to `backend/tests/test_api_validation_rules.py`. Follow the file's existing client and
workspace fixtures rather than inventing new ones — read a neighbouring POST test first and
mirror its setup exactly.

```python
@pytest.mark.req("FR-68")
async def test_a_workspace_rule_can_record_the_catalogue_entry_it_derives_from(
    client: AsyncClient, analyst_headers: dict[str, str]
) -> None:
    """FR-68's lineage: a workspace version of a built-in names its catalogue entry.

    Without this the derivation is unreachable through the API — the column exists, the
    read-back exists, and no caller can write it.
    """
    response = await client.post(
        "/api/v1/validation-rules",
        headers=analyst_headers,
        json={
            "slug": "psi-column-stricter",
            "layer": "distribution",
            "check": "psi_column",
            "severity": "warn",
            "params": {"warn_above": 0.05},
            "catalogue_id": "VR-DST-1",
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["catalogue_id"] == "VR-DST-1"
```

- [ ] **Step 2: Run it to make sure it fails**

Run: `uv run pytest backend/tests/test_api_validation_rules.py::test_a_workspace_rule_can_record_the_catalogue_entry_it_derives_from -q`

Expected: FAIL with **422**, not a 500 or an assertion on the body. `RuleCreate` sets
`extra="forbid"`, so an unknown `catalogue_id` key is rejected before the handler runs. If it
fails any other way, stop and find out why before implementing — the failure mode is the
evidence that the field is genuinely absent.

- [ ] **Step 3: Add the field, the parameter and the row kwarg**

In `backend/src/app/api/validation.py`, add to `RuleCreate` (after `params`):

```python
    #: The `01` §4.4 entry this rule derives from (FR-68). A workspace authoring its own
    #: version of a built-in records the lineage here; a rule that derives from nothing
    #: leaves it unset.
    catalogue_id: str | None = None
```

In the same file's handler, add one argument to the `rule_service.create_rule(...)` call,
immediately after `params=body.params,`:

```python
            catalogue_id=body.catalogue_id,
```

In `backend/src/app/platform/validation_rules.py`, add a keyword-only parameter to
`create_rule` immediately after `params: dict[str, Any] | None = None,`:

```python
    catalogue_id: str | None = None,
```

and add one kwarg to the `ValidationRuleRow(...)` construction, immediately after
`severity=severity.value,`:

```python
        catalogue_id=catalogue_id,
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest backend/tests/test_api_validation_rules.py::test_a_workspace_rule_can_record_the_catalogue_entry_it_derives_from -q`

Expected: PASS.

- [ ] **Step 5: Write the failing refusal test — deliberately broken input**

CLAUDE.md §13: enforcement is proven on deliberately broken input, and a check that has never
printed a failure has not been tested.

```python
@pytest.mark.req("FR-68")
async def test_a_catalogue_id_naming_no_catalogue_entry_is_refused(
    client: AsyncClient, analyst_headers: dict[str, str]
) -> None:
    """Refused on the way in, not on the way out.

    `ValidationRule` already refuses an unknown id when a row is read back, so without this
    guard a bad id is *accepted* by the write and then makes the row permanently unreadable —
    a 500 on every subsequent GET, from data the API itself allowed in.
    """
    response = await client.post(
        "/api/v1/validation-rules",
        headers=analyst_headers,
        json={
            "slug": "not-a-real-derivation",
            "layer": "distribution",
            "check": "psi_column",
            "severity": "warn",
            "catalogue_id": "VR-DST-99",
        },
    )
    assert response.status_code == 422, response.text
```

- [ ] **Step 6: Run it to confirm it fails, and confirm *how***

Run: `uv run pytest backend/tests/test_api_validation_rules.py::test_a_catalogue_id_naming_no_catalogue_entry_is_refused -q`

Expected: FAIL. Record which status you actually got in the ledger. The predicted mode is a
**500** raised out of `to_schema`, because `VR-DST-99` matches `ValidationRule.catalogue_id`'s
pattern but not `BUILTIN_RULES`, so the row is written and then fails validation on read-back.
**Do not assume the predicted mode.** If the observed status is something else, the guard being
added is still correct, but say so in the ledger rather than repeating this prediction — a
plan-stated expectation that goes unchecked is exactly the false negative this repository has
already booked once against a §13 mutation proof.

- [ ] **Step 7: Implement the refusal**

In `backend/src/app/platform/validation_rules.py`, inside `create_rule`, immediately **before**
the `version = 1 + (...)` allocation — so a bad request never consumes a version number — add:

```python
    if catalogue_id is not None:
        try:
            builtin_rule(catalogue_id)
        except ValueError as exc:
            raise PlatformError(
                "VALIDATION_FAILED",
                "That catalogue entry does not exist",
                422,
                str(exc),
            ) from exc
```

Add `builtin_rule` to the existing `from model_schema import (...)` block at `:35` that already
imports `BUILTIN_RULES`, keeping the names alphabetically ordered as the block has them.
`builtin_rule` (`validation.py:432-444`) is the catalogue's own lookup and already raises a
`ValueError` whose message names the id and explains that a workspace's own rules are stored,
not defined here — reuse it rather than writing a second membership test, so there is one place
the catalogue is consulted.

- [ ] **Step 8: Run both tests**

Run: `uv run pytest backend/tests/test_api_validation_rules.py -q -k catalogue`

Expected: both PASS, and the pre-existing seeded-catalogue tests in that file (`:127`, `:142`,
`:157`, `:162`, `:213`) still pass.

- [ ] **Step 9: Amend FR-68's tail**

CLAUDE.md §2: the spec change lands in the same commit as the code that makes it true. Open
`docs/specs/01-data-management.md` at `:166` and read the whole row before editing — it is a
table row, so any literal `|` you introduce must be escaped as `\|`.

Replace the tail sentence — *"Declared and unfixed, owner `W6b-13` (found 2026-08-23): the
create handler drops `catalogue_id`, …"* — with a dated delivery note in the same voice,
recording that it **was** unreachable and now is not:

> Fixed 2026-08-24 (`W6b-13b`, found 2026-08-23): the create handler dropped `catalogue_id`,
> so the derivation was unreachable through the API. `RuleCreate` now carries it and
> `create_rule` refuses an id naming no catalogue entry.

Do **not** delete the record that the defect existed — §0's rule is that quietly making one
side match the other destroys the record of which was believed.

- [ ] **Step 10: Run the docs audit and commit**

```bash
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
git add backend/src/app/api/validation.py backend/src/app/platform/validation_rules.py backend/tests/test_api_validation_rules.py docs/specs/01-data-management.md
git commit -m "feat(w6b-13b): a workspace rule can record the catalogue entry it derives from"
```

---

### Task 2: `BuiltinRule` carries params, and stops quoting struck spec text

`BuiltinRule`'s docstring (`validation.py:208-211`) quotes §4.4's *"Thresholds are Rule Set
configuration, not code"* — a sentence the **2026-08-23 correction struck** — and reasons from
it that "thresholds are deliberately absent". FR-56's amendment reverses exactly that
conclusion. The docstring is not decoration here: it is the recorded justification for the
field this task adds, so it must be rewritten in the same change, not left to contradict the
code beneath it.

**Files:**
- Modify: `packages/model-schema/src/model_schema/validation.py:205-235`
- Test: `packages/model-schema/tests/test_validation_catalogue.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `BuiltinRule.params: dict[str, Any]`, defaulting to `{}`; and
  `_rule(catalogue_id, slug, check, severity, summary, params=None)`. Tasks 3 and 4 both
  depend on these names.

- [ ] **Step 1: Write the failing test**

Add to `packages/model-schema/tests/test_validation_catalogue.py`:

```python
@pytest.mark.req("FR-56")
def test_a_catalogue_entry_carries_its_default_params() -> None:
    """FR-56: a built-in's default thresholds belong in its catalogue entry.

    Empty for a rule whose check reads no defaulted parameter — that is not a gap, it is
    the accurate statement that the check has nothing to configure.
    """
    assert BUILTIN_RULES["VR-STR-1"].params == {}
    assert builtin_rule("VR-DST-1").params == {"warn_above": 0.10}
```

`builtin_rule` is already imported by this module at `:7`.

- [ ] **Step 2: Run it to make sure it fails**

Run: `uv run pytest packages/model-schema/tests/test_validation_catalogue.py::test_a_catalogue_entry_carries_its_default_params -q`

Expected: FAIL with `AttributeError: 'BuiltinRule' object has no attribute 'params'`.

- [ ] **Step 3: Add the field and rewrite the docstring**

In `packages/model-schema/src/model_schema/validation.py`, replace the docstring paragraph at
`:208-211` — the one beginning *"Thresholds are deliberately absent."* — with:

```
    Thresholds live here (FR-56). `01` §4.4's 2026-08-23 correction struck the claim that
    they are Rule Set configuration rather than code: before this field, every threshold in
    force was a literal inside `pricing_core.data.validate` that no caller could read, which
    left the frontend re-deriving bands it should be served. The literals stay as the fallback
    for a workspace-authored rule that supplies no params; for a built-in, this is the value
    the seed writes.
```

Then add the field, after `summary: str`:

```python
    #: Default thresholds for the parameters this rule's check reads, keyed exactly as the
    #: check reads them. Empty when the check reads none. `dict[str, Any]` rather than a
    #: narrower type because a param may be an int (`immature_months`) or a float, and
    #: `ValidationRule.params` — the field this is written into — is already `dict[str, Any]`.
    params: dict[str, Any] = Field(default_factory=dict)
```

`ValidationRule` at `:78-93` is the precedent: it is likewise `frozen=True, extra="forbid"` and
carries four `dict[str, Any]` fields with `default_factory=dict`. `frozen=True` on a model with
a dict field only fails if something hashes it, and nothing hashes a `BuiltinRule` — the
existing set comprehensions build sets of `.severity` and `.check`, and `set(BUILTIN_RULES)` is
a set of string keys.

Then widen the `_rule` factory at `:230-235`:

```python
def _rule(
    catalogue_id: str,
    slug: str,
    check: str,
    severity: Severity,
    summary: str,
    params: dict[str, Any] | None = None,
) -> BuiltinRule:
    return BuiltinRule(
        catalogue_id=catalogue_id,
        slug=slug,
        check=check,
        severity=severity,
        summary=summary,
        params=params or {},
    )
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest packages/model-schema/tests/test_validation_catalogue.py -q`

Expected: the new test still FAILS on the `VR-DST-1` line (nothing is populated yet — Task 3
does that), and every pre-existing test in the file PASSES. Confirm the failure is now an
assertion on `{} != {"warn_above": 0.1}` and no longer an `AttributeError`.

- [ ] **Step 5: Verify the struck quotation is gone from every surface**

```bash
git grep -n "Thresholds are Rule Set configuration" -- packages/ backend/ frontend/src docs/
```

Expected: hits **only** inside `docs/specs/01-data-management.md`'s dated correction block,
which quotes the struck sentence in order to strike it. Any hit in `packages/`, `backend/` or
`frontend/src` is another copy of this same defect — record it in the ledger. Do not fix a hit
in `frontend/src` here; that is the excluded `profiles.ts` item.

- [ ] **Step 6: Commit**

```bash
git add packages/model-schema/src/model_schema/validation.py packages/model-schema/tests/test_validation_catalogue.py
git commit -m "feat(w6b-13b): a catalogue entry can carry its default thresholds"
```

The one failing assertion is expected to survive this commit and is closed by Task 3. If your
execution process forbids committing with a red test, merge Tasks 2 and 3 into a single commit
instead — do not weaken the test to make it green.

---

### Task 3: Populate the fifteen entries

Fifteen of the thirty-eight catalogue entries name a check that reads a defaulted parameter.
Eighteen keys in total. The remaining twenty-three keep `params={}`.

Every value below is the literal `validate.py` already uses, at the line given. **Copy them
exactly** — a catalogue default that disagrees with its own fallback is worse than no catalogue
default, because the seeded rule and a workspace rule would then behave differently for no
visible reason.

| Catalogue id | Check | Params | Fallback at |
|---|---|---|---|
| `VR-STR-9` | `reject_rate` | `{"max_reject_rate": 0.001}` | `validate.py:400` |
| `VR-REF-2` | `reference_coverage` | `{"min_coverage": 0.5}` | `:543` |
| `VR-ACT-9` | `claim_amount_sign` | `{"max_negative_share": 0.01}` | `:912` |
| `VR-ACT-10` | `severity_outlier` | `{"percentile": 0.995}` | `:959` |
| `VR-ACT-11` | `frequency_plausible` | `{"min_frequency": 0.0, "max_frequency": 1.0}` | `:1043-1044` |
| `VR-ACT-12` | `severity_plausible` | `{"min_severity_minor": 0, "max_severity_minor": 1_000_000_000_000}` | `:1072-1073` |
| `VR-ACT-13` | `zero_claim_cohort` | `{"min_exposure_share": 0.01}` | `:1129` |
| `VR-ACT-14` | `development_maturity` | `{"immature_months": 3, "max_immature_exposure_share": 0.05}` | `:1183`, `:1207` |
| `VR-DST-1` | `psi_column` | `{"warn_above": 0.10}` | `:1459` |
| `VR-DST-3` | `vanished_level` | `{"min_exposure_share": 0.01}` | `:1573` |
| `VR-DST-4` | `null_rate_shift` | `{"max_shift_pp": 5.0}` | `:1341` |
| `VR-DST-5` | `volume_shift` | `{"max_shift_fraction": 0.2}` | `:1369` |
| `VR-DST-6` | `mean_shift` | `{"max_standard_errors": 5.0}` | `:1628` |
| `VR-DST-7` | `target_rate_shift` | `{"max_shift_fraction": 0.15}` | `:1699` |
| `VR-DST-8` | `mix_shift_exposure` | `{"warn_above": 0.10}` | `:1753` |

Three traps in that table:

- **`VR-ACT-12` is the one row that is not a byte-for-byte copy**, and the exception is
  required rather than optional. `validate.py:1071-1072` writes its fallbacks as `0.0` and
  `1e12`, but both are **minor-unit money**, and FR-10 makes money integer — `audit-docs.py`
  fails a document that writes a minor-unit amount fractionally, which is how this was found.
  The catalogue therefore carries `0` and `1_000_000_000_000`. **This changes no behaviour:**
  both reads are wrapped in `float(...)`, so `float(0)` and `float(0.0)` are the same value and
  the published `threshold` is a float either way. Verify that wrapper is still there before
  you rely on this.
- **`max_shift_fraction` has two different defaults** — `0.2` for `volume_shift`, `0.15` for
  `target_rate_shift`. Same key, different checks. Do not unify them.
- **`VR-DST-1` gets `warn_above` only.** See the `fail_above` section above. `validate.py:1460`
  keeps its `fail_above` read; that residue is a separate item.

**Files:**
- Modify: `packages/model-schema/src/model_schema/validation.py` (the `BUILTIN_RULES` literal)
- Test: `packages/pricing-core/tests/test_builtin_rule_checks.py`,
  `packages/model-schema/tests/test_validation_catalogue.py`

**Interfaces:**
- Consumes: `_rule(..., params=...)` from Task 2.
- Produces: populated `BUILTIN_RULES`. Task 4 reads `rule.params`.

- [ ] **Step 1: Write the failing anti-drift test**

This is the test that stops the catalogue and the code disagreeing later. It checks that every
key the catalogue declares is a key its check actually reads — a typo'd key would otherwise be
silently ignored, because every check reads its params with `.get(key, literal)` and would fall
straight back to the literal with no error anywhere.

Add to `packages/pricing-core/tests/test_builtin_rule_checks.py`:

```python
@pytest.mark.req("FR-56")
def test_every_catalogue_default_names_a_param_its_check_reads() -> None:
    """A catalogue key its check never reads is silently inert.

    Every check reads params as `.get(key, literal)`, so a misspelled catalogue key falls
    back to the literal and nothing raises. The seeded rule would then advertise a threshold
    it does not honour — which is the failure FR-56 exists to remove, reintroduced one
    level up.
    """
    import inspect

    unread = []
    for rule in BUILTIN_RULES.values():
        if not rule.params:
            continue
        source = inspect.getsource(CHECKS[rule.check])
        unread += [
            f"{rule.catalogue_id} -> {rule.check} never reads {key!r}"
            for key in rule.params
            if f'"{key}"' not in source
        ]
    assert not unread, unread


@pytest.mark.req("FR-56")
def test_the_anti_drift_check_is_not_trivially_satisfied() -> None:
    """The test above passes vacuously if no rule carries params, or if the substring test
    matches anything. A key that no check mentions must be caught."""
    import inspect

    source = inspect.getsource(CHECKS["psi_column"])
    assert '"warn_above"' in source
    assert '"warn_abovv"' not in source
    assert any(rule.params for rule in BUILTIN_RULES.values())
```

- [ ] **Step 2: Run both to make sure they fail**

Run: `uv run pytest packages/pricing-core/tests/test_builtin_rule_checks.py -q`

Expected: `test_the_anti_drift_check_is_not_trivially_satisfied` FAILS on its final assertion
(no rule carries params yet). The first test passes *vacuously* — which is precisely why the
second one exists. If `inspect.getsource(CHECKS[...])` raises instead, `CHECKS` maps to
something other than a plain function; adapt by reading `validate.py`'s `CHECKS` definition and
say so in the ledger.

- [ ] **Step 3: Populate the fifteen entries**

In the `BUILTIN_RULES` literal, add a `params=` argument to each of the fifteen `_rule(...)`
calls named in the table, leaving the other twenty-three untouched. For example, the
`VR-DST-1` call becomes:

```python
            _rule(
                "VR-DST-1",
                "psi-column",
                "psi_column",
                _W,
                "Population Stability Index for a column against the reference version",
                params={"warn_above": 0.10},
            ),
```

Keep each call's existing `summary` string byte-for-byte — it is §4.4's own wording, and a test
compares the catalogue to the spec.

- [ ] **Step 4: Run the tests to verify they pass**

```bash
uv run pytest packages/pricing-core/tests/test_builtin_rule_checks.py packages/model-schema/tests/test_validation_catalogue.py -q
```

Expected: all PASS, including Task 2's `VR-DST-1` assertion, which closes here.

- [ ] **Step 5: Prove the anti-drift test fails on deliberately broken input**

CLAUDE.md §13: a check that has never printed a failure has not been tested. Temporarily
misspell one key — change `VR-DST-4`'s `"max_shift_pp"` to `"max_shift_ppp"` — and run:

```bash
uv run pytest packages/pricing-core/tests/test_builtin_rule_checks.py::test_every_catalogue_default_names_a_param_its_check_reads -q
```

Expected: FAIL, naming `VR-DST-4 -> null_rate_shift never reads 'max_shift_ppp'`. Revert the
misspelling and re-run to confirm green. Record the observed failure text in the ledger; if it
passes, the test is inert and must be fixed before this task closes.

- [ ] **Step 6: Commit**

```bash
git add packages/model-schema/src/model_schema/validation.py packages/model-schema/tests/test_validation_catalogue.py packages/pricing-core/tests/test_builtin_rule_checks.py
git commit -m "feat(w6b-13b): the fifteen catalogue entries whose checks read thresholds carry their defaults"
```

---

### Task 4: The seed writes catalogue defaults instead of `{}`

`seed_builtin_rules` (`backend/src/app/platform/validation_rules.py:88-159`) writes
`"params": {}` at `:140` for all thirty-eight. This is the line FR-56's tail is about, and
the only line that makes the defaults reach a caller.

**Files:**
- Modify: `backend/src/app/platform/validation_rules.py:140`
- Modify: `docs/specs/01-data-management.md:118` (FR-56's tail)
- Test: `backend/tests/test_api_validation_rules.py`

**Interfaces:**
- Consumes: `BuiltinRule.params` (Task 2), populated (Task 3).
- Produces: seeded rows whose `body["params"]` is non-empty for fifteen rules.

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/test_api_validation_rules.py`, alongside the existing seeded-row tests at
`:157-162` — read those first and reuse their fixture for fetching seeded rows.

```python
@pytest.mark.req("FR-56")
async def test_seeded_builtins_carry_their_catalogue_default_thresholds(...) -> None:
    """FR-56: every threshold in force is readable by a caller.

    Both directions matter. A rule whose check reads a threshold must publish it, and a rule
    whose check reads none must publish nothing — an invented default would advertise
    configuration the code does not have.
    """
    by_catalogue_id = {row.catalogue_id: row for row in rows}
    assert by_catalogue_id["VR-DST-1"].body["params"] == {"warn_above": 0.10}
    assert by_catalogue_id["VR-ACT-14"].body["params"] == {
        "immature_months": 3,
        "max_immature_exposure_share": 0.05,
    }
    assert by_catalogue_id["VR-STR-1"].body["params"] == {}
    assert sum(1 for row in rows if row.body["params"]) == 15
```

Complete the signature and the `rows` binding from the neighbouring test at `:157`; do not
invent a new fixture.

- [ ] **Step 2: Run it to make sure it fails**

Run: `uv run pytest backend/tests/test_api_validation_rules.py -q -k catalogue_default`

Expected: FAIL — `{} != {"warn_above": 0.1}`, and the count assertion reporting `0 != 15`.

- [ ] **Step 3: Write the one-line change**

In `backend/src/app/platform/validation_rules.py`, at `:140`, replace:

```python
            "params": {},
```

with:

```python
            # FR-56: the catalogue carries a built-in's default thresholds, so the
            # seeded row publishes them rather than leaving every threshold a literal in
            # `pricing-core` that no caller can read. Copied, not aliased — the catalogue is
            # a process-wide constant and this dict is about to be handed to the ORM.
            "params": dict(rule.params),
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest backend/tests/test_api_validation_rules.py -q`

Expected: all PASS, including the pre-existing seeded-catalogue tests.

- [ ] **Step 5: Amend FR-56's tail**

Open `docs/specs/01-data-management.md` at `:118` and read the whole row. Replace the
**"A consequence, declared and unbuilt, owner `W6b-13`"** block — the one stating that the seed
writes `params: {}` for all 38 and that §4.4's "every threshold shown is a default" is false in
a second way — with a dated delivery note recording what was built and what deliberately was
not:

> Built 2026-08-24 (`W6b-13b`): a built-in's default thresholds are carried in its catalogue
> entry and written by the seed. Fifteen of the thirty-eight name a check that reads a
> defaulted parameter; the other twenty-three publish `params: {}`, which is the accurate
> statement that their check has nothing to configure. VR-DST-1 carries `warn_above` only —
> the `fail_above` band is a second rule under the 2026-08-15 amendment, and is not yet in
> the set.

Escape any literal `|` as `\|`. Leave the sentence about `params` mixing thresholds with
targeting intact: this slice did not change that, and it remains true.

- [ ] **Step 6: Run the full gate — both halves**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

`generate-contracts.py --check` is expected to report **no drift**: `BuiltinRule` is not in
`docs/contracts/`. If it does report drift, stop — something in this slice reached the
published contract and the scope boundary above is wrong.

If this worktree is fresh, run `uv sync --all-packages` first; without it `mypy` reports
hundreds of phantom errors that read as real defects.

- [ ] **Step 7: Commit**

```bash
git add backend/src/app/platform/validation_rules.py backend/tests/test_api_validation_rules.py docs/specs/01-data-management.md
git commit -m "feat(w6b-13b): the seed publishes each built-in's catalogue default thresholds"
```

---

## Self-review

**Spec coverage.** FR-68's tail → Task 1. FR-56's tail → Tasks 2, 3, 4. §4.4's
catalogue → Task 3's fifteen rows. Nothing else in `01` §4.3–§4.5 is in this slice's scope.

**One spec sentence this slice does *not* make true.** §4.4's closing line, *"Every threshold
shown here is a default carried by the rule"*, still cannot be checked against §4.4's own
table, because that table shows prose placeholders — "X percentage points", "N reference
standard errors", "a configured band" — rather than numbers. After this slice the thresholds
are readable from the catalogue, but §4.4 still shows none of them. **That is a spec defect,
not a code defect, and it is out of scope here**: filling those placeholders is a §0 spec change
needing its own owner, and it is now cheap because the fifteen values are enumerated in Task 3.
Raise it rather than fixing it inside this slice.

**Placeholder scan.** Two tests are written against fixtures rather than as complete functions
— Task 4 Step 1's signature and `rows` binding, and Task 1's `analyst_headers`. Both name the
exact neighbouring test to copy (`:157` and the file's existing POST tests) because the fixture
names in that module are the module's own and must not be reinvented. Every other code block is
complete.

**Type consistency.** `params` is `dict[str, Any]` in all four places it appears — on
`BuiltinRule` (Task 2), in `_rule`'s signature (Task 2), in the seeded body (Task 4), and on
`ValidationRule` where it already lives. `catalogue_id` is `str | None` on `RuleCreate` and on
`create_rule`, matching `ValidationRule.catalogue_id` at `validation.py:100`.

## Out of scope, with owners to assign

1. `validate.py:1460`'s inert `fail_above` read, `frontend/src/api/profiles.ts:42,52-54`'s
   two-band implementation, and the missing second VR-DST catalogue rule for the `fail` band —
   **one item**, per the lead's 2026-08-24 ruling.
2. §4.4's table showing prose placeholders where its own closing sentence promises defaults.
3. Nothing validates a printed spec example against the type it claims to be an example of
   (raised by the WK-664 executor, 2026-08-24) — its own unit, not folded in here.
4. **`validate.py:1071-1072` writes two minor-unit money fallbacks as floats** (`0.0`, `1e12`).
   FR-10 makes money integer, and `audit-docs.py` enforces that on documents but reaches no
   Python source, which is why this survived. This slice does not change those literals: they
   are behaviourally inert under the `float(...)` wrapper, and deciding whether the money rule
   binds a numeric fallback inside a check is a §0 question, not a silent pick for a plan to
   make on its way past. Raise it with the fifteen values already enumerated in Task 3.
