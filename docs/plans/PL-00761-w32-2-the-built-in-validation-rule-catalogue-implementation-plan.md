---
id: PL-761
family: plan
kind: leaf
title: W32-2 — The built-in validation-rule catalogue Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-23
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-23-w32-2-validation-rule-catalogue.md
---

# W32-2 — The built-in validation-rule catalogue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `01` §4.4's 38 named validation rules from prose a human reads into a catalogue
the platform holds — seeded into every workspace, served over an API, and provably complete
against the spec that names them.

**Architecture:** The catalogue is a module-level constant in `model-schema`, following
`BUILTIN_ROLES`'s precedent exactly: a `Final` mapping, an accessor that raises naming the
alternative, and prose in `#:` comments citing the requirement that forces each choice. The
backend seeds it into a workspace the way `seed_builtin_roles` seeds roles — the same
signature, the same idempotence, the same `flush()`-not-`commit()` discipline — because a rule
set references rules by stored row id (`_to_rule_set`,
`backend/src/app/platform/validation_rules.py:406-425`), so a built-in rule that has no row
cannot be put in a rule set. A collection endpoint then serves them, which is what unblocks
W6b-13.

**Tech Stack:** Python 3.12, Pydantic v2, SQLAlchemy 2.x async, Alembic, PostgreSQL 16,
FastAPI, pytest. `scripts/scope-audit.py` is the acceptance instrument.

**Spec:**
- [`../specs/01-data-management.md`](../specs/01-data-management.md) — §4.4's four rule tables
  (lines 335–434) are the source of truth for the catalogue's contents; FR-42…24 govern
  rules and rule sets; FR-50 governs a rule's review; §4.5 (line 435) is the rule
  lifecycle; §5.1's endpoint table gains a row.
- [`../roadmap.md`](../roadmap.md) — line 1028, where `--catalogue VR` is recorded at 1 of 38.
- [`PL-00753-wk-664-and-wk-692-the-slice-map.md`](PL-00753-wk-664-and-wk-692-the-slice-map.md) — this slice's row, and line
  114 where W6b-13 is recorded as depending on it.
- [`../adrs/ADR-00704-model-schema-is-the-single-source-of-truth-for-shared-shapes.md`](../adrs/ADR-00704-model-schema-is-the-single-source-of-truth-for-shared-shapes.md)
  — why the catalogue lives in `model-schema` and nowhere else.

---

## Global Constraints

Copied from [`../../CLAUDE.md`](../../CLAUDE.md). Every task's requirements implicitly
include this section.

- **`model-schema` is the single source of truth** (§2, ADR-704). Nobody hand-writes a shape
  that already exists there — not the backend, not the frontend, not a fixture. This slice
  exists because a threshold *is* currently written twice (Task 5 records where).
- **`pricing-core` imports no FastAPI, SQLAlchemy or Redis** (ADR-703). Task 1's second test
  lives in `packages/pricing-core/tests/` and imports only `model_schema` and
  `pricing_core.data.validate`.
- **Requirement IDs are permanent** (§5): append, never renumber. This slice appends one
  requirement to `01` §3. Highest ids in use: FR-67, NFR-474.
  Next free: `FR-68` — and this plan takes it. No other plan of this date touches the DATA range.
- **Audit writes share the caller's transaction** (§0's retrofit list).
  `app.platform.audit.record` raises `RuntimeError` unless `session.in_transaction()`
  (`backend/src/app/platform/audit.py:71-76`), so seeding must happen inside the caller's
  unit of work and must never open its own.
- **There is no `ForeignKey` anywhere in `backend/src/app/db/models.py`** — deliberate, and
  the rule is stated at `:1282-1285`. Task 3 adds a column, not a reference.
- **When code and spec disagree, resolve it — do not quietly change one to match the other**
  (§0). Task 2 and Task 5 carry four resolutions between them.
- **A negative test for every invariant** (§13), and enforcement proven on deliberately broken
  input (§13 rule 4).
- **A fresh worktree has no `.venv`.** Run `uv sync --all-packages --dev` first, or `mypy`
  reports several hundred phantom errors that read as real defects.
- **The worktree guard refuses compound shell commands.** Run each command plainly rather
  than joining them with `&&`.

### The gate

Run all of this before opening a PR, reading each command's **own** exit code.

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

**Both halves are required.** Task 2 changes a shape in `model-schema`, which regenerates
`docs/contracts/openapi/generated.json`, and `.github/workflows/frontend.yml` triggers on
`docs/contracts/openapi/**` — so a contract change runs the frontend workflow whether or not
any `.vue` file was touched.

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend lint
pnpm --dir frontend type-check
pnpm --dir frontend test
pnpm --dir frontend build
```

Database tests need the compose stack. Without it they **skip** rather than fail, which is
exactly how a seeding change reaches `main` unproven:

```bash
docker compose -f deploy/docker-compose.yml up -d --wait
```

### The acceptance instrument

```bash
uv run python scripts/scope-audit.py DATA --catalogue VR
```

Today it exits **1** with `STR 1/9`, `REF 0/5`, `ACT 0/16`, `DST 0/8`, `TOTAL 1/38`. The
single hit is not a catalogue entry at all — it is
`packages/pricing-core/src/pricing_core/data/validate.py:1176`, where the string `VR-STR-5`
appears inside a *different* rule's skip message. At the end of Task 1 this must read
`TOTAL 38/38` and exit 0.

Read `scripts/scope-audit.py:150-207` before assuming where the catalogue may live: it scans
`packages/` and `backend/src` **only**, and excludes any path with `tests` among its parts. A
catalogue defined in a test file scores zero. Its own docstring names `BUILTIN_ROLES` as the
reference implementation, which is why Task 1 copies that shape rather than inventing one.

---

## File structure

| File | Change | Responsibility |
|---|---|---|
| `packages/model-schema/src/model_schema/validation.py` | Add `BuiltinRule`, `BUILTIN_RULES`, `builtin_rule()`; add one field to `ValidationRule` | The catalogue, and the field that lets a stored rule name its catalogue entry |
| `packages/model-schema/src/model_schema/__init__.py` | Modify `:212-218`, `:263-275`, `:277+` | Re-export, in the three blocks the module already keeps sorted |
| `packages/model-schema/tests/test_validation_catalogue.py` | Create | Completeness against §4.4, and the accessor's refusal |
| `packages/pricing-core/tests/test_builtin_rule_checks.py` | Create | Every catalogue `check` is a registered check — the test that makes the catalogue real |
| `backend/src/app/db/models.py` | Modify `:1033-1077` | A `builtin` column, and the CHECK constraint arm that lets a built-in rule be approved |
| `backend/migrations/versions/<new>_builtin_validation_rules.py` | Create | The column, the constraint swap, no backfill |
| `backend/src/app/platform/validation_rules.py` | Modify `:70-84`, add `seed_builtin_rules` | Projection carries the catalogue id; seeding mirrors `seed_builtin_roles` |
| `backend/src/app/api/validation.py` | Add one route | `GET /api/v1/validation-rules` — W6b-13's blocker |
| `backend/tests/test_api_validation_rules.py` | Create | The endpoint's happy path, its 403, and its cross-workspace 404 |
| `backend/tests/conftest_db.py` | Modify `:108` | The `grant` fixture seeds rules beside roles |
| `examples/fremtpl2/seed.py` | Modify `:193-257`, `:300`, `:362-374` | Call the seeder; drop the nine hand-written rules that duplicate catalogue entries |
| `scripts/generate-contracts.py` | Modify `:38-112` | `validation-rule` joins `GENERATED_SHAPES` |
| `backend/tests/test_contracts.py` | Modify `:34-47` | and `COMPARED_SLUGS` |
| `docs/contracts/schemas/validation-rule.schema.json` | Regenerate | Replaces the hand-authored file that has diverged |
| `docs/specs/01-data-management.md` | Modify §3, §5.1 | the requirement Task 5 appends; the endpoint row |
| `docs/roadmap.md` | Modify `:1028` | The catalogue count, resolved |

**Ordering.** Task 1 → Task 2 → Task 3 → Task 4 → Task 5, strictly. Task 2 changes a shape
Task 1 defines; Task 3 seeds what Task 1 holds; Task 4 serves what Task 3 stores. Task 1 and
Task 2 both edit `validation.py` and must not run in parallel — W32-1's ledger recorded that
fan-out is bounded by file collisions.

---

### Task 1: The catalogue

**Files:**
- Modify: `packages/model-schema/src/model_schema/validation.py` — append after
  `ValidationRuleSet` (`:167`)
- Modify: `packages/model-schema/src/model_schema/__init__.py` — `:212-218`, `:263-275`,
  and `__all__` from `:277`
- Test: `packages/model-schema/tests/test_validation_catalogue.py` (create)
- Test: `packages/pricing-core/tests/test_builtin_rule_checks.py` (create)

**Interfaces:**
- Consumes: `ValidationLayer` (`:40-46`, members `STRUCTURAL`, `REFERENTIAL`,
  `ACTUARIAL_SANITY`, `DISTRIBUTIONAL`), `Severity` (members `WARN`, `FAIL` — there is no
  `INFO`), and `pricing_core.data.validate.CHECKS`, the registry `register_check` populates
  (`packages/pricing-core/src/pricing_core/data/validate.py:96-107`).
- Produces:
  - `BuiltinRule` — frozen Pydantic model, fields `catalogue_id: str`, `slug: str`,
    `check: str`, `severity: Severity`, `summary: str`, and a `layer` **property** derived
    from the id prefix.
  - `BUILTIN_RULES: Final[Mapping[str, BuiltinRule]]`, keyed by catalogue id, in §4.4's order.
  - `builtin_rule(catalogue_id: str) -> BuiltinRule`, raising `ValueError` on an unknown id.

**Why `check` is listed and not derived.** The obvious economy — `check = slug.replace("-", "_")`
— is wrong for **nine** of the 38, and the exceptions are not typos: `nullability` runs
`not_null`, `primary-key-unique` runs `unique_key`, `date-parse` runs `date_parsed`,
`reference-resolve` runs `reference_lookup`, `exposure-period-consistent` runs
`period_consistent`, `no-overlapping-exposure` runs `no_overlap`, and **three separate rules**
— `exposure-positive`, `exposure-plausible` and `claim-count-non-negative` — all run `range`
with different bounds. A rule's name and its implementation are different things and the
catalogue must say both.

**Why `layer` is derived and not listed.** The id prefix *is* the layer: `VR-STR-*` is
structural, `VR-REF-*` referential, `VR-ACT-*` actuarial sanity, `VR-DST-*` distributional.
Listing it beside the id would let the two disagree. `READ_PERMISSIONS` in
`packages/model-schema/src/model_schema/permissions.py:74-88` is the module's precedent for
deriving rather than re-listing.

- [ ] **Step 1: Write the failing completeness test**

Create `packages/model-schema/tests/test_validation_catalogue.py`:

```python
"""The catalogue against `01` §4.4, which is the only place these 38 rules are named."""

from __future__ import annotations

import pytest

from model_schema import BUILTIN_RULES, Severity, ValidationLayer, builtin_rule


@pytest.mark.req("FR-45")
def test_the_catalogue_holds_every_rule_01_section_4_4_names() -> None:
    """Counts per layer, from the four tables at `01` lines 361-413.

    Asserted as counts *and* as ids because a count alone passes if a rule is duplicated
    and another is missing — which is exactly the failure a hand-transcribed table of 38
    rows produces.
    """
    per_layer = {
        ValidationLayer.STRUCTURAL: 9,
        ValidationLayer.REFERENTIAL: 5,
        ValidationLayer.ACTUARIAL_SANITY: 16,
        ValidationLayer.DISTRIBUTIONAL: 8,
    }
    assert len(BUILTIN_RULES) == sum(per_layer.values()) == 38
    for layer, count in per_layer.items():
        got = [r.catalogue_id for r in BUILTIN_RULES.values() if r.layer is layer]
        assert len(got) == count, f"{layer}: {got}"

    prefixes = {"STR": 9, "REF": 5, "ACT": 16, "DST": 8}
    for prefix, count in prefixes.items():
        expected = {f"VR-{prefix}-{n}" for n in range(1, count + 1)}
        assert expected <= set(BUILTIN_RULES), sorted(expected - set(BUILTIN_RULES))


@pytest.mark.req("FR-45")
def test_a_catalogue_id_is_its_own_key_and_its_layer() -> None:
    for key, rule in BUILTIN_RULES.items():
        assert key == rule.catalogue_id
        assert rule.layer.value.startswith(
            {"STR": "struct", "REF": "refer", "ACT": "actuar", "DST": "distrib"}[
                key.split("-")[1]
            ]
        )


@pytest.mark.req("FR-45")
def test_slugs_are_unique_and_match_the_rule_slug_pattern() -> None:
    """`ValidationRule.slug` is `^[a-z0-9][a-z0-9-]{1,62}$` and a seeded row uses it.

    A duplicate slug would collide on `uq_validation_rule_version` at seed time — in the
    migration, on a live database, which is the worst place to discover it.
    """
    import re

    slugs = [rule.slug for rule in BUILTIN_RULES.values()]
    assert len(set(slugs)) == len(slugs)
    for slug in slugs:
        assert re.fullmatch(r"[a-z0-9][a-z0-9-]{1,62}", slug), slug


@pytest.mark.req("FR-45")
def test_every_severity_is_warn_or_fail() -> None:
    """`Severity` has exactly two members; the committed JSON Schema claims three.

    Task 2 resolves that divergence by generating the schema. This test is what stops it
    coming back through the catalogue.
    """
    assert {r.severity for r in BUILTIN_RULES.values()} <= {Severity.WARN, Severity.FAIL}


@pytest.mark.req("FR-45")
def test_an_unknown_catalogue_id_is_refused_by_name() -> None:
    with pytest.raises(ValueError, match="VR-STR-99"):
        builtin_rule("VR-STR-99")


@pytest.mark.req("FR-45")
def test_a_known_catalogue_id_returns_its_rule() -> None:
    """Beside the refusal, because a refusal test alone passes if the accessor always raises."""
    rule = builtin_rule("VR-STR-1")
    assert rule.slug == "column-presence"
    assert rule.check == "column_presence"
    assert rule.severity is Severity.FAIL
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest packages/model-schema/tests/test_validation_catalogue.py -q`
Expected: FAIL at import — `cannot import name 'BUILTIN_RULES' from 'model_schema'`.

- [ ] **Step 3: Add `BuiltinRule` and the layer derivation**

Append to `packages/model-schema/src/model_schema/validation.py`, after `ValidationRuleSet`:

```python
#: The layer each catalogue-id prefix belongs to. Derived rather than listed per rule: the
#: prefix *is* the layer (`01` §4.4's four tables are the four layers of FR-45), and a
#: rule carrying both could carry them inconsistently.
_LAYER_BY_PREFIX: Final[Mapping[str, ValidationLayer]] = MappingProxyType(
    {
        "STR": ValidationLayer.STRUCTURAL,
        "REF": ValidationLayer.REFERENTIAL,
        "ACT": ValidationLayer.ACTUARIAL_SANITY,
        "DST": ValidationLayer.DISTRIBUTIONAL,
    }
)


class BuiltinRule(BaseModel):
    """One rule the platform ships, from `01` §4.4's catalogue (the requirement Task 5 appends).

    Distinct from `ValidationRule`, which is a *stored* rule: it carries a workspace-scoped
    `id` and a `version`, and a built-in rule has neither until it is seeded into a
    workspace. Keeping them apart is what stops the catalogue needing a fabricated UUID at
    import time.

    Thresholds are deliberately absent. `01` §4.4 line 415 — "Thresholds are Rule Set
    configuration, not code. Every threshold shown is a default." — and a catalogue that
    carried them would be a second place a threshold is written.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    catalogue_id: str = Field(pattern=r"^VR-(STR|REF|ACT|DST)-\d{1,2}$")
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")
    #: The registered check this rule runs — `pricing_core.data.validate.CHECKS`. **Not**
    #: derivable from the slug: nine of the 38 differ, and `range` backs three of them.
    check: str
    severity: Severity
    #: `01` §4.4's third column, trimmed to one line. The spec's own wording, so that a
    #: reader comparing the two can see they are the same rule.
    summary: str

    @property
    def layer(self) -> ValidationLayer:
        return _LAYER_BY_PREFIX[self.catalogue_id.split("-")[1]]
```

Add `from types import MappingProxyType` and `from collections.abc import Mapping` to the
module's imports if they are not already there, and `Final` to the `typing` import.

- [ ] **Step 4: Add the 38 entries**

Append below `BuiltinRule`. Every `summary` is `01` §4.4's third column with its markdown
stripped; every `severity` is the second column. Transcribe them exactly:

```python
def _rule(catalogue_id: str, slug: str, check: str, severity: Severity, summary: str) -> BuiltinRule:
    return BuiltinRule(
        catalogue_id=catalogue_id, slug=slug, check=check, severity=severity, summary=summary
    )


_W, _F = Severity.WARN, Severity.FAIL

#: `01` §4.4's catalogue, in the order the spec lists it. Keyed by catalogue id because that
#: is the identifier `01` §4.4 line 337 calls stable and says workflows and the UI reference.
#:
#: A rule appears here and nowhere else. Before this constant existed the ids lived only in
#: prose, and `scripts/scope-audit.py DATA --catalogue VR` scored 1 of 38 — the one hit being
#: a `VR-STR-5` mention inside another rule's skip message, which is to say zero.
BUILTIN_RULES: Final[Mapping[str, BuiltinRule]] = MappingProxyType(
    {
        r.catalogue_id: r
        for r in (
            _rule("VR-STR-1", "column-presence", "column_presence", _F, "Every column declared in the schema exists"),
            _rule("VR-STR-2", "dtype-match", "dtype_match", _F, "Each column's Arrow dtype matches the declaration (no silent coercion)"),
            _rule("VR-STR-3", "nullability", "not_null", _F, "Columns declared non-nullable contain no nulls"),
            _rule("VR-STR-4", "primary-key-unique", "unique_key", _F, "Declared primary key is unique and non-null (policy id x exposure period)"),
            _rule("VR-STR-5", "date-parse", "date_parsed", _F, "All date columns parsed to date32/timestamp with no fallback-to-string"),
            _rule("VR-STR-6", "encoding", "encoding", _W, "No mojibake / invalid UTF-8 sequences in string columns"),
            _rule("VR-STR-7", "allowed-values", "allowed_values", _F, "Categorical columns contain only values in the declared domain"),
            _rule("VR-STR-8", "no-unexpected-columns", "no_unexpected_columns", _W, "No columns present that are absent from the schema"),
            _rule("VR-STR-9", "reject-rate", "reject_rate", _F, "Quarantined rows <= threshold (default 0.1 % of rows read) - FR-32"),
            _rule("VR-REF-1", "reference-resolve", "reference_lookup", _F, "Every value of a reference-backed column resolves in the pinned Reference Table Version, evaluated as at the declared date column (FR-71)"),
            _rule("VR-REF-2", "reference-coverage", "reference_coverage", _W, "At least X % of reference table keys are exercised by the data (catches a stale or wrong reference version)"),
            _rule("VR-REF-3", "effective-date-in-range", "effective_date_in_range", _F, "The declared as-at date lies within the Reference Table Version's covered period"),
            _rule("VR-REF-4", "cross-table-key", "cross_table_key", _F, "Every claim.policy_id exists in policy_exposure"),
            _rule("VR-REF-5", "code-list-drift", "code_list_drift", _W, "New codes present that did not exist in the reference dataset version"),
            _rule("VR-ACT-1", "exposure-positive", "range", _F, "exposure_years > 0 for every row"),
            _rule("VR-ACT-2", "exposure-plausible", "range", _F, "exposure_years <= 1.05 per row; annual policies sum to about 1.0 per policy year"),
            _rule("VR-ACT-3", "exposure-period-consistent", "period_consistent", _F, "exposure_end > exposure_start; exposure_years is about (end - start)/365.25 within tolerance"),
            _rule("VR-ACT-4", "no-overlapping-exposure", "no_overlap", _F, "A single policy_id has no overlapping exposure intervals"),
            _rule("VR-ACT-5", "claim-date-in-exposure", "claim_date_in_exposure", _F, "date_of_loss is in [exposure_start, exposure_end) for the linked row (FR-38)"),
            _rule("VR-ACT-6", "claim-linkage-complete", "claim_linkage_complete", _F, "100 % of claims link to exactly one exposure row"),
            _rule("VR-ACT-7", "claim-not-multi-linked", "claim_not_multi_linked", _F, "No claim links to more than one exposure row"),
            _rule("VR-ACT-8", "claim-count-non-negative", "range", _F, "claim_count >= 0, integer"),
            _rule("VR-ACT-9", "claim-amount-sign", "claim_amount_sign", _W, "Negative incurred amounts exist only where recoveries/reversals are expected; flagged with counts"),
            _rule("VR-ACT-10", "severity-outlier", "severity_outlier", _W, "Claims above a configurable threshold (absolute, or a percentile of the peril's own distribution) are flagged for large-loss treatment - never auto-removed"),
            _rule("VR-ACT-11", "frequency-plausible", "frequency_plausible", _W, "Portfolio and per-peril frequency within a configured band (e.g. motor AD 0.02-0.25)"),
            _rule("VR-ACT-12", "severity-plausible", "severity_plausible", _W, "Portfolio and per-peril mean severity within a configured band"),
            _rule("VR-ACT-13", "zero-claim-cohort", "zero_claim_cohort", _W, "No factor level with material exposure (> 1 % of total) has exactly zero claims where the prior version had claims"),
            _rule("VR-ACT-14", "development-maturity", "development_maturity", _W, "The most recent N months of experience are flagged as immature (IBNR risk) with the configured development pattern; modelling on them without an adjustment is a warning"),
            _rule("VR-ACT-15", "currency-consistency", "currency_consistency", _F, "All monetary columns share the Dataset's declared currency; no mixed-currency rows"),
            _rule("VR-ACT-16", "duplicate-claim", "duplicate_claim", _W, "No two claims share (policy, date_of_loss, peril, amount) - a classic double-load signature"),
            _rule("VR-DST-1", "psi-column", "psi_column", _W, "Per-column PSI against the reference version, for categorical, ordinal and boolean columns only"),
            _rule("VR-DST-2", "new-level", "new_level", _W, "Categorical levels present now, absent in reference"),
            _rule("VR-DST-3", "vanished-level", "vanished_level", _W, "Levels with material reference exposure now absent"),
            _rule("VR-DST-4", "null-rate-shift", "null_rate_shift", _W, "Null rate moved by more than X percentage points (a broken feed's clearest signal)"),
            _rule("VR-DST-5", "volume-shift", "volume_shift", _W, "Row count against the reference version's row count"),
            _rule("VR-DST-6", "mean-shift", "mean_shift", _W, "Numeric column mean moved more than N reference standard errors"),
            _rule("VR-DST-7", "target-rate-shift", "target_rate_shift", _W, "Observed frequency / severity / burning cost moved more than X % vs reference"),
            _rule("VR-DST-8", "mix-shift-exposure", "mix_shift_exposure", _W, "Exposure distribution across a declared key factor moved (PSI on the exposure weights, not the row counts)"),
        )
    }
)


def builtin_rule(catalogue_id: str) -> BuiltinRule:
    """One catalogue entry by its `01` §4.4 id.

    Raises rather than returning `None` because every call site has a specific id in hand;
    a missing one means the caller's id is wrong, not that there is nothing to return.
    """
    try:
        return BUILTIN_RULES[catalogue_id]
    except KeyError:
        raise ValueError(
            f"unknown built-in rule {catalogue_id!r}; the catalogue is `01` §4.4's 38 rules, "
            "and a workspace's own rules are stored, not defined here"
        ) from None
```

**`VR-DST-1`'s severity cell is not a plain token** — §4.4 gives it as "the rule's own
severity, at `warn_above`". The 2026-08-15 amendment immediately below the tables settled that
a rule carries **one** severity, and that neither two-band form is reachable, so the catalogue
records `warn`. Add a `#:` comment on that entry saying so and citing the amendment; do not
leave a reader to wonder whether the transcription lost something.

- [ ] **Step 5: Re-export from the package**

In `packages/model-schema/src/model_schema/__init__.py`:
- add `BUILTIN_RULES`, `BuiltinRule` and `builtin_rule` to the validation import block at
  `:212-218`;
- add them to the validation re-export block at `:263-275`;
- add `"BUILTIN_RULES"`, `"BuiltinRule"` and `"builtin_rule"` to `__all__`, which opens at
  `:277` and is sorted — `"BUILTIN_RULES"` lands at what is currently line 281, immediately
  after `"BUILTIN_ROLES"`.

- [ ] **Step 6: Run the catalogue test**

Run: `uv run pytest packages/model-schema/tests/test_validation_catalogue.py -q`
Expected: PASS, 6 tests.

- [ ] **Step 7: Write the check-registration test**

This is the test that makes the catalogue a catalogue rather than 38 strings. Create
`packages/pricing-core/tests/test_builtin_rule_checks.py`:

```python
"""Every catalogue rule names a check that exists.

`01` §4.4 gives each rule a name and an English description; the *check* is the function in
`pricing_core.data.validate` that runs it, and nothing before this test connected the two. A
typo in the catalogue would otherwise surface as a seeded rule that fails at validation time
in a workspace, long after the transcription.
"""

from __future__ import annotations

import pytest

from model_schema import BUILTIN_RULES
from pricing_core.data.validate import CHECKS


@pytest.mark.req("FR-45")
def test_every_builtin_rule_names_a_registered_check() -> None:
    missing = sorted(
        f"{rule.catalogue_id} -> {rule.check}"
        for rule in BUILTIN_RULES.values()
        if rule.check not in CHECKS
    )
    assert not missing, missing


@pytest.mark.req("FR-45")
def test_the_registry_is_not_trivially_satisfied() -> None:
    """The check above passes vacuously if `CHECKS` is empty or over-broad.

    Six registered checks back no catalogue rule — `regex`, `relationship`, `expression`,
    `aggregate`, `distribution_compare` and `sql` are the primitives a *custom* rule is
    built from (`01` §4.5). Asserting the gap exists is what proves membership means
    something.
    """
    used = {rule.check for rule in BUILTIN_RULES.values()}
    assert len(CHECKS) > len(used)
    assert {"expression", "sql"} <= set(CHECKS) - used
```

- [ ] **Step 8: Run it**

Run: `uv run pytest packages/pricing-core/tests/test_builtin_rule_checks.py -q`

Expected: PASS, 2 tests. **If the first fails, the catalogue is wrong and the spec is not** —
the check names in Step 4 were read off `@register_check` decorators in
`packages/pricing-core/src/pricing_core/data/validate.py`, so a miss means a transcription
error to fix in the catalogue, not a check to add.

- [ ] **Step 9: Run the acceptance instrument**

Run: `uv run python scripts/scope-audit.py DATA --catalogue VR`
Expected: `STR 9/9`, `REF 5/5`, `ACT 16/16`, `DST 8/8`, `TOTAL 38/38`, exit **0**.

- [ ] **Step 10: Prove the instrument can still fail**

§13 rule 4: a check that has never failed is not known to work. Delete one entry from
`BUILTIN_RULES`, re-run the command, confirm it reports 37/38 and exits 1, then restore the
entry and re-run to confirm 38/38.

- [ ] **Step 11: Commit**

```bash
git add packages/model-schema/src/model_schema/validation.py packages/model-schema/src/model_schema/__init__.py packages/model-schema/tests/test_validation_catalogue.py packages/pricing-core/tests/test_builtin_rule_checks.py
git commit -m "feat(w32-2): the 38 built-in validation rules, as a catalogue in model-schema"
```

---

### Task 2: A stored rule names its catalogue entry

**Files:**
- Modify: `packages/model-schema/src/model_schema/validation.py` — `ValidationRule`, `:74-91`
- Modify: `scripts/generate-contracts.py` — `GENERATED_SHAPES`, `:38-112`
- Modify: `backend/tests/test_contracts.py` — `COMPARED_SLUGS`, `:34-47`
- Regenerate: `docs/contracts/schemas/validation-rule.schema.json`
- Test: `packages/model-schema/tests/test_validation_catalogue.py` — append

**Interfaces:**
- Consumes: `BuiltinRule` from Task 1.
- Produces: `ValidationRule.catalogue_id: str | None = None`. `None` means a workspace's own
  rule; a `VR-…` value means the row came from the catalogue. Task 3's seeder sets it and
  Task 4's endpoint filters on it.

**The resolution this task carries.** `docs/contracts/schemas/validation-rule.schema.json` is
hand-authored, has no generated twin, and **nothing compares it to the model**. It has
therefore drifted in three ways: its `severity` enum contains `"info"`, which `Severity` has
never had; its `check` enum is missing most of the registry; and it carries two fields the
model does not — `owner` and `dry_run_result_id` (note the name, which is not even
`dry_run_report_id`). Patching those three would leave the mechanism that produced them in
place. Generating the file instead removes the class of defect, and is what FR-451 exists
for.

- [ ] **Step 1: Write the failing test**

Append to `packages/model-schema/tests/test_validation_catalogue.py`:

```python
@pytest.mark.req("FR-45")
def test_a_stored_rule_can_name_the_catalogue_entry_it_came_from() -> None:
    """Without this the only link back is the slug, which a workspace may version away from.

    The frontend needs the id to show "VR-DST-1" beside a rule, and `profiles.ts` currently
    hard-codes that rule's thresholds precisely because it has no way to ask.
    """
    from uuid import uuid4

    from model_schema import ValidationRule

    seeded = ValidationRule(
        id=uuid4(), slug="psi-column", version=1, layer=ValidationLayer.DISTRIBUTIONAL,
        check="psi_column", severity=Severity.WARN, catalogue_id="VR-DST-1",
    )
    assert seeded.catalogue_id == "VR-DST-1"

    own = ValidationRule(
        id=uuid4(), slug="our-own-rule", version=1, layer=ValidationLayer.STRUCTURAL,
        check="column_presence", severity=Severity.FAIL,
    )
    assert own.catalogue_id is None


@pytest.mark.req("FR-45")
def test_a_catalogue_id_that_names_no_catalogue_entry_is_refused() -> None:
    """`extra="forbid"` catches a misspelled *field*; nothing caught a misspelled *value*."""
    from uuid import uuid4

    import pydantic

    from model_schema import ValidationRule

    with pytest.raises(pydantic.ValidationError):
        ValidationRule(
            id=uuid4(), slug="psi-column", version=1, layer=ValidationLayer.DISTRIBUTIONAL,
            check="psi_column", severity=Severity.WARN, catalogue_id="VR-DST-99",
        )
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest packages/model-schema/tests/test_validation_catalogue.py -q -k catalogue_entry`
Expected: FAIL — `extra="forbid"` rejects `catalogue_id` as an unexpected field.

- [ ] **Step 3: Add the field and its validator**

In `ValidationRule` (`packages/model-schema/src/model_schema/validation.py:74-91`), after
`status`:

```python
    #: The `01` §4.4 catalogue entry this row was seeded from, or `None` for a workspace's
    #: own rule (the requirement Task 5 appends). Not a foreign key and not a slug: a workspace may version a
    #: seeded rule and change its slug, and the catalogue id is what survives that.
    catalogue_id: str | None = None

    @model_validator(mode="after")
    def _catalogue_id_names_a_catalogue_entry(self) -> ValidationRule:
        if self.catalogue_id is not None and self.catalogue_id not in BUILTIN_RULES:
            raise ValueError(
                f"catalogue_id {self.catalogue_id!r} names no rule in `01` §4.4's catalogue"
            )
        return self
```

`BUILTIN_RULES` is defined *below* `ValidationRule` in the module, which is fine — the
validator body runs at call time, not at class-definition time. Do not reorder the module to
"fix" this: `BuiltinRule` is documented in terms of `ValidationRule` and reads better after it.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest packages/model-schema/tests/test_validation_catalogue.py -q`
Expected: PASS, 8 tests.

- [ ] **Step 5: Bring the schema under generation**

Add `validation-rule` to `GENERATED_SHAPES` in `scripts/generate-contracts.py:38-112`, mapping
the slug to `model_schema.ValidationRule`, following the entries already there. Add the same
slug to `COMPARED_SLUGS` in `backend/tests/test_contracts.py:34-47`.

- [ ] **Step 6: Regenerate and read the diff**

```bash
uv run python scripts/generate-contracts.py
git diff docs/contracts/
```

Expected: `docs/contracts/schemas/validation-rule.schema.json` is rewritten. **Read the diff
rather than accepting it.** Three things must disappear — the `"info"` severity, the `owner`
field and `dry_run_result_id` — and `catalogue_id` must appear. A generated artifact matching
its source proves neither is correct (§13 rule 4), so confirm each removal is a removal of
something the model genuinely does not have, and not of something the model is missing.

- [ ] **Step 7: Verify the drift guard**

Run: `uv run python scripts/generate-contracts.py --check`
Expected: PASS with no diff.

- [ ] **Step 8: Prove the guard fails on broken input**

Edit one field name in `docs/contracts/schemas/validation-rule.schema.json` by hand, re-run
`--check`, confirm it exits non-zero and names the file, then `git checkout` the file and
re-run to confirm it passes. Without this the new `COMPARED_SLUGS` entry is assumed to work
rather than known to.

- [ ] **Step 9: Commit**

```bash
git add packages/model-schema/src/model_schema/validation.py packages/model-schema/tests/test_validation_catalogue.py scripts/generate-contracts.py backend/tests/test_contracts.py docs/contracts/
git commit -m "feat(w32-2): a stored rule names its catalogue entry; generate its schema"
```

---

### Task 3: Seed the catalogue into a workspace

**Files:**
- Modify: `backend/src/app/db/models.py` — `ValidationRuleRow`, `:1033-1077`
- Create: `backend/migrations/versions/<rev>_builtin_validation_rules.py`
- Modify: `backend/src/app/platform/validation_rules.py` — `to_schema` `:70-84`, and append
  `seed_builtin_rules`
- Modify: `backend/tests/conftest_db.py:108`
- Modify: `examples/fremtpl2/seed.py` — `:193-257`, `:300`, `:362-374`
- Test: `backend/tests/test_api_validation_rules.py` (create; Task 4 adds to it)

**Interfaces:**
- Consumes: `BUILTIN_RULES` (Task 1), `ValidationRule.catalogue_id` (Task 2), and
  `seed_builtin_roles(session, workspace_id) -> list[RoleRow]` at
  `backend/src/app/platform/rbac.py:110-139` as the shape to mirror.
- Produces: `async def seed_builtin_rules(session: AsyncSession, workspace_id: UUID) -> list[ValidationRuleRow]`
  — idempotent, takes the caller's session, ends with `await session.flush()` and **never**
  `commit()`, exactly as `seed_builtin_roles` does.

**The constraint that blocks this, and the honest way past it.**
`ValidationRuleRow.__table_args__` carries `approved_rule_dry_run_and_separate_approver`:

```
status <> 'approved' OR (approved_by IS NOT NULL
    AND approved_by <> authored_by AND dry_run_report_id IS NOT NULL)
```

A built-in rule must be `approved` — an unapproved rule cannot go in a rule set — and it has
no workspace author, no workspace approver and no dry run. `examples/fremtpl2/seed.py:362-374`
gets past this today by fabricating `dry_run_report_id=new_uuid7()`, a UUID pointing at no
report. Do **not** copy that. Add a `builtin` column and widen the constraint so a built-in row
is an explicit alternative arm:

```
builtin IS TRUE
    OR status <> 'approved'
    OR (approved_by IS NOT NULL AND approved_by <> authored_by
        AND dry_run_report_id IS NOT NULL)
```

That is a governance statement, not a loophole, and Task 5 writes it into the requirement it appends: a
built-in rule's review happened in this repository, in a pull request, under `01` §4.4's
change control — not in a workspace by two of its members. The workspace path is unchanged and
still requires both an independent approver and a dry run.

- [ ] **Step 1: Write the failing seeding test**

Create `backend/tests/test_api_validation_rules.py`. Copy the structure from
`backend/tests/test_custom_metrics_api.py` — it is 141 lines and is this suite's template:

```python
"""The built-in rule catalogue, seeded and served."""

from __future__ import annotations

import pytest

from model_schema import BUILTIN_RULES


@pytest.mark.req("FR-45")
def test_seeding_puts_every_catalogue_rule_in_the_workspace(api_client, workspace_id) -> None:
    response = api_client.get("/api/v1/validation-rules", headers=_headers(READ_ROLE))
    assert response.status_code == 200, response.text
    ids = {item["catalogue_id"] for item in response.json()["items"]}
    assert ids == set(BUILTIN_RULES), sorted(set(BUILTIN_RULES) - ids)


@pytest.mark.req("FR-45")
def test_seeding_twice_creates_no_duplicates(api_client, workspace_id) -> None:
    """Idempotent like `seed_builtin_roles`, and for the same reason: it runs on a path
    that may be retried, and `uq_validation_rule_version` turns a second run into an
    IntegrityError that surfaces far from its cause."""
    ...


@pytest.mark.req("FR-45")
def test_a_seeded_rule_is_approved_without_a_fabricated_dry_run(api_client) -> None:
    """The constraint's new arm, asserted from the outside.

    Before this slice the only way to seed an approved rule was to invent a
    `dry_run_report_id` pointing at no report — which is what `examples/fremtpl2/seed.py`
    did, and what Step 7 removes.
    """
    ...
```

Fill the two elided bodies with the same idiom as the first. Take `_headers` from
`backend/tests/test_api_datasets.py:27-31` and the role fixtures from `:34-43`; use the
`api_client` fixture (`backend/tests/conftest.py:56-60`), **not** the plain `client` fixture at
`:30-35`, which has no database.

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest backend/tests/test_api_validation_rules.py -q`

Expected: FAIL with 404 — the route does not exist until Task 4. **If it reports `SKIPPED`,
the compose stack is down**; bring it up with the command in the gate block and re-run.
Database tests skip rather than fail when the DSN is unreachable, and a skipped suite is how a
seeding change reaches `main` unproven.

- [ ] **Step 3: Add the column and widen the constraint**

In `backend/src/app/db/models.py`, add to `ValidationRuleRow` after `dry_run_report_id`:

```python
    builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
```

`RoleRow` at `:494-518` has the same column for the same reason; match its declaration. Then
replace the `approved_rule_dry_run_and_separate_approver` CheckConstraint with the widened
form above, and extend the comment beside it to say what the new arm means and why — the
existing comment already explains the other two arms, and an unexplained arm in a governance
constraint is the one a later reader deletes.

- [ ] **Step 4: Write the migration**

```bash
uv run alembic revision -m "builtin validation rules"
```

Fill it in. It does three things and no backfill:
- `op.add_column("validation_rules", sa.Column("builtin", sa.Boolean(), nullable=False, server_default=sa.false()))`,
  then `op.alter_column("validation_rules", "builtin", server_default=None)` — the pattern
  `backend/migrations/versions/55b2bea92837_*.py` established for a non-null column on a
  populated table.
- `op.drop_constraint("approved_rule_dry_run_and_separate_approver", "validation_rules", type_="check")`
  then `op.create_check_constraint(...)` with the widened predicate.
- `downgrade()` reverses both, dropping any `builtin` rows first — a downgrade that leaves
  built-in rows behind and restores the narrow constraint fails on the next write.

Confirm the chain: the new revision's `down_revision` must be `9e4c7b21fa08`, the current head.

- [ ] **Step 5: Apply it**

```bash
GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing uv run alembic upgrade head
```

The bare command does **not** work against the compose stack: `backend/src/app/config.py`'s
`database_url` defaults to `gip:gip@localhost:5432/gip` while compose provisions
`gipricing:gipricing@…/gipricing`, and Alembic reads `Settings`, so it dies with
`InvalidPasswordError`.

Then run the downgrade and the upgrade again, to prove `downgrade()` is not decorative — no
migration in this tree has a test, and this is the only check the slice can give it:

```bash
GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing uv run alembic downgrade -1
GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing uv run alembic upgrade head
```

- [ ] **Step 6: Write the seeder**

Append to `backend/src/app/platform/validation_rules.py`, and carry `catalogue_id` through
`to_schema` (`:70-84`) at the same time:

```python
async def seed_builtin_rules(
    session: AsyncSession, workspace_id: UUID, *, authored_by: UUID
) -> list[ValidationRuleRow]:
    """`01` §4.4's catalogue, as rows in one workspace (the requirement Task 5 appends).

    Mirrors `app.platform.rbac.seed_builtin_roles`: the caller's session, idempotent, a
    `flush()` rather than a `commit()` so the rows join whatever transaction the caller
    already has. Rules need rows and not just a constant because `_to_rule_set` resolves a
    set's members by `(workspace_id, id)` — a catalogue entry with no row cannot be put in
    a rule set, which is the only thing a rule is for.

    Idempotent by catalogue id rather than slug: a workspace may version a seeded rule and
    change its slug, and re-seeding must not then insert a second copy.
    """
    existing = set(
        (
            await session.execute(
                select(ValidationRuleRow.catalogue_id).where(
                    ValidationRuleRow.workspace_id == workspace_id,
                    ValidationRuleRow.builtin.is_(True),
                )
            )
        ).scalars()
    )
    created: list[ValidationRuleRow] = []
    for rule in BUILTIN_RULES.values():
        if rule.catalogue_id in existing:
            continue
        row = ValidationRuleRow(
            workspace_id=workspace_id,
            slug=rule.slug,
            version=1,
            layer=rule.layer.value,
            check=rule.check,
            severity=rule.severity.value,
            body={"message": rule.summary, "rationale": rule.summary},
            status="approved",
            authored_by=authored_by,
            builtin=True,
        )
        session.add(row)
        created.append(row)
    await session.flush()
    return created
```

`catalogue_id` must also be a column on `ValidationRuleRow` for the `select` above to work —
add it in Step 3 beside `builtin` (`String(16)`, nullable, indexed with `workspace_id`), and in
the migration in Step 4. `to_schema` then reads it straight through.

- [ ] **Step 7: Wire the three call sites**

- `backend/tests/conftest_db.py:108` — the `grant` fixture already calls `seed_builtin_roles`;
  call `seed_builtin_rules` beside it, with the fixture's principal as `authored_by`. This is
  the leverage point: **there is no workspace-creation service** — a workspace is a bare
  `UUID` column — and every DB test builds its workspace through this fixture.
- `examples/fremtpl2/seed.py:300` — the one production call to `seed_builtin_roles`. Call the
  new seeder beside it.
- `examples/fremtpl2/seed.py:193-257` — `RULES` holds nine hand-written rules, none carrying a
  VR id. Any whose slug now collides with a catalogue slug will fail
  `uq_validation_rule_version`. Run
  `grep -n '"slug"' examples/fremtpl2/seed.py` and compare against Task 1's 38 slugs: delete
  every entry the catalogue now supplies, keep only those genuinely specific to freMTPL2, and
  remove the `dry_run_report_id=new_uuid7()` fabrication at `:362-374` for any that remain
  only if they no longer need it. **If all nine are catalogue duplicates, delete `RULES`
  entirely** rather than leaving an empty list nobody can explain.

- [ ] **Step 8: Run the seeding tests**

Run: `uv run pytest backend/tests/test_api_validation_rules.py -q -k seed`
Expected: the two seeding tests PASS; the endpoint test still fails with 404.

- [ ] **Step 9: Run the whole backend suite**

Run: `uv run pytest backend -q`

Expected: PASS. The `grant` fixture now inserts 38 rows per test workspace, so watch for two
things: any test asserting a rule *count* in a fresh workspace, and any test asserting an
empty rule list. Both are legitimate breakages to fix in the test, not in the seeder.

- [ ] **Step 10: Run the seed script end to end**

Run: `uv run python scripts/demo.py --rows 60000`

Expected: it completes and the seeded workspace has both roles and rules. This is the only
exercise the production seeding path gets.

- [ ] **Step 11: Commit**

```bash
git add backend/src/app/db/models.py backend/migrations/versions backend/src/app/platform/validation_rules.py backend/tests/conftest_db.py backend/tests/test_api_validation_rules.py examples/fremtpl2/seed.py
git commit -m "feat(w32-2): seed the built-in rule catalogue into every workspace"
```

---

### Task 4: `GET /api/v1/validation-rules`

**Files:**
- Modify: `backend/src/app/api/validation.py` — add one route
- Modify: `docs/specs/01-data-management.md` — §5.1's endpoint table
- Test: `backend/tests/test_api_validation_rules.py` — append

**Interfaces:**
- Consumes: `Page[T]` at `backend/src/app/api/pagination.py:48-61` (`DEFAULT_LIMIT` 50,
  `MAX_LIMIT` 200, `COUNT_CAP` 10 000), `to_schema` from Task 3, and the `ReadDatasets`
  permission the module's other read routes use.
- Produces: `GET /api/v1/validation-rules` → `Page[ValidationRule]`, with an optional
  `builtin: bool | None` query filter. This is W6b-13's blocker; the shape it returns is what
  that slice's view renders.

**Why the route is missing rather than broken.** `backend/src/app/api/validation.py` has eight
routes (`:115`, ~`:140`, `:164`, `:198`, `:237`, `:256`, `:285`, `:302`) and none of them is a
collection over rules — there is no way to ask what rules exist. It is absent from `01` §5.1's
table too, so this is an omission in the spec and the code together (§14 question 2), not a
code gap against a written requirement.

- [ ] **Step 1: Write the failing tests**

Append to `backend/tests/test_api_validation_rules.py`. Three tests, because a route needs its
happy path, its refusal and its isolation:

```python
@pytest.mark.req("FR-45")
def test_the_collection_is_paginated_and_filterable_by_builtin(api_client) -> None:
    page = api_client.get(
        "/api/v1/validation-rules?builtin=true&limit=10", headers=_headers(READ_ROLE)
    )
    assert page.status_code == 200, page.text
    body = page.json()
    assert len(body["items"]) == 10
    assert all(item["catalogue_id"] is not None for item in body["items"])
    assert body["next_cursor"]


@pytest.mark.req("FR-45")
def test_reading_rules_without_the_permission_is_refused(api_client) -> None:
    """A role with no dataset-read permission, so the refusal is the route's and not the
    fixture's absence of a workspace."""
    response = api_client.get("/api/v1/validation-rules", headers=_headers(NO_READ_ROLE))
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "FORBIDDEN"


@pytest.mark.req("FR-45")
def test_rules_seeded_in_another_workspace_are_not_visible(api_client) -> None:
    """The highest-value test here. Isolation is a folded `workspace_id` predicate, so a
    dropped `.where` clause leaks every workspace's rules and no other test would see it.

    Shaped after `backend/tests/test_api_models.py:254-272`, which seeds under a stranger
    rather than merely asking as one.
    """
    ...
```

Fill the third body using the `_seed()` loop idiom at `backend/tests/test_api_models.py:61-96`
— and note that `dispose()` is mandatory there. Never nest `unit_of_work()`:
`.claude/skills/python-test/SKILL.md:526-560` records that it hangs with no output at all.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest backend/tests/test_api_validation_rules.py -q -k "collection or without_the_permission or another_workspace"`
Expected: all three FAIL with 404.

- [ ] **Step 3: Add the route**

In `backend/src/app/api/validation.py`, following the module's existing route idiom for
dependency injection, permission checking and problem+json errors:

```python
@router.get("/validation-rules", response_model=Page[ValidationRule])
async def list_validation_rules(
    builtin: bool | None = None,
    ...,
) -> Page[ValidationRule]:
    """Every rule this workspace can put in a rule set (the requirement Task 5 appends).

    Includes the 38 built-in rules `01` §4.4 names, which are seeded into every workspace,
    and the workspace's own. `builtin` separates them: a screen offering "add a rule to this
    set" wants both, and one showing "what we have changed" wants only the second.
    """
```

Order by `(builtin DESC, catalogue_id, slug)` so the catalogue arrives in its documented order
and a workspace's own rules follow. Scope every query by `workspace_id`, the way the module's
other routes do.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest backend/tests/test_api_validation_rules.py -q`
Expected: PASS, all six.

- [ ] **Step 5: Add the endpoint to `01` §5.1**

Add the row to `docs/specs/01-data-management.md`'s §5.1 endpoint table, matching the columns
its neighbours use — method, path, permission, request, response. Then:

Run: `uv run python scripts/scope-audit.py DATA --endpoints`

Expected: the new endpoint is counted as implemented. A row added to §5.1 with no route
published makes the count *worse*, so this step must run after Step 3, never before.

- [ ] **Step 6: Regenerate the contract**

```bash
uv run python scripts/generate-contracts.py
uv run python scripts/generate-contracts.py --check
```

Expected: `docs/contracts/openapi/generated.json` gains the path; `--check` then passes.

- [ ] **Step 7: Commit**

```bash
git add backend/src/app/api/validation.py backend/tests/test_api_validation_rules.py docs/specs/01-data-management.md docs/contracts/
git commit -m "feat(w32-2): publish GET /api/v1/validation-rules"
```

---

### Task 5: Resolve the spec and the roadmap

**Files:**
- Modify: `docs/specs/01-data-management.md` — §3's requirement table
- Modify: `docs/roadmap.md:1028`

**Interfaces:**
- Consumes: everything Tasks 1–4 built.
- Produces: no code. CLAUDE.md §0's resolution step, and §13 rule 6's statement of what was
  *not* delivered.

**Four findings, four verdicts.**

1. **No requirement said built-in rules exist.** FR-42…24 govern rules and rule sets;
   §4.4 names 38 of them and calls their ids stable and referenced by workflows and the UI
   (line 337); nothing says the platform *holds* them, seeds them, or serves them. The whole
   slice was implementable and unrequired. Step 1 appends it.
2. **The roadmap records `--catalogue VR` at 1 of 38, citing `validate.py:1175`.** The
   citation is off by one — the string is at `:1176` — and the count is now 38 of 38. Both
   corrected in place with a date.
3. **`frontend/src/api/profiles.ts:42` hard-codes VR-DST-1's PSI bands** (warn 0.10, fail
   0.25). That is a threshold written twice, which CLAUDE.md §2 forbids, and §4.4 line 415
   says thresholds are Rule Set configuration rather than code. **Not fixed here** — the
   endpoint that would let the frontend ask now exists, but changing the view is W6b-13's
   work. Recorded with that owner.
4. **The five DATA requirements with no evidence are unchanged by this slice.**
   `scope-audit.py DATA` reports FR-55, FR-82, FR-67, NFR-465 and
   NFR-466 without evidence. The first two are W32-3's; the last two are performance
   budgets needing a measurement rather than a marker. Say so rather than letting a reader
   infer this slice moved them.

- [ ] **Step 1: Append the requirement to `01` §3**

The requirement rows in `01` §3 are single lines of the form `| **FR-DATA-N** | text |`.
Insert the row reproduced after the marker below — everything from the first `|` onward, as
one line — immediately after FR-67's row.

Next free: `FR-68` — the row to insert is: `| **FR-68** | The 38 rules §4.4 names are **built-in**: held as a catalogue in `model-schema`, seeded into every workspace as approved rules, and served by `GET /api/v1/validation-rules`. Added 2026-08-23 (W32-2). Before this date they existed only as prose — `scope-audit.py DATA --catalogue VR` scored 1 of 38, and its single hit was one rule's id appearing inside a different rule's skip message. A stored rule carries `catalogue_id`, which is what survives a workspace versioning a seeded rule and changing its slug; `None` means the workspace's own rule. A built-in rule is `approved` on seeding **without** an in-workspace approver or dry run, and the `builtin IS TRUE` arm of `approved_rule_dry_run_and_separate_approver` is where that is enforced: its review happened in this repository under §4.4's change control, in a pull request with a named author and reviewer, and requiring a workspace to re-approve 38 shipped rules would make the approval a formality — which is worse than not asking. The workspace path is unchanged and still requires an approver who is not the author, and a dry run. Thresholds stay out of the catalogue, per §4.4's rule that every threshold shown is a default and belongs to Rule Set configuration. |`

- [ ] **Step 2: Retarget the test markers**

Tasks 1–4 marked their tests `@pytest.mark.req("FR-45")` — the requirement that says
"§4.4 enumerates the built-in rules", and the closest existing one. It is not wrong, but it is
not what those tests prove: FR-45 is about a Rule Set covering four layers, and these
tests are about the catalogue existing, being seeded and being served.

Now that Step 1 has defined the new requirement, change the marker on every test in the four
files below to the id allocated on Step 1's line. Sixteen markers, all currently
`FR-45`:

```bash
grep -rn 'pytest.mark.req("FR-45")' packages/model-schema/tests/test_validation_catalogue.py packages/pricing-core/tests/test_builtin_rule_checks.py backend/tests/test_api_validation_rules.py
```

Leave any marker that genuinely belongs to FR-45 — none of these do; every one was
written for the new requirement and parked on the nearest existing id because
`scripts/audit-docs.py` refuses a plan citing an id no spec defines. That is a constraint on
the plan document, not on the code, and this step is where it is discharged.

- [ ] **Step 3: Correct the roadmap's catalogue record**

At `docs/roadmap.md:1028`, replace the `1/38` figure with `38/38`, correct the line citation
from `validate.py:1175` to `:1176`, and append:

```
Resolved 2026-08-23 (W32-2) under the requirement Step 1 appends: the catalogue is `BUILTIN_RULES` in
`model-schema`, seeded per workspace and served by `GET /api/v1/validation-rules`. The single
prior hit was one rule's id inside another rule's skip message, so the true starting count was
zero.

**Not resolved by this slice:** `frontend/src/api/profiles.ts:42` still hard-codes VR-DST-1's
PSI bands — a threshold written twice, which `CLAUDE.md` §2 forbids. The endpoint that lets the
frontend ask now exists; changing the view is W6b-13's. Owner: W6b-13.

FR-55, FR-82, FR-67, NFR-465 and NFR-466 remain without evidence and are
untouched here — the first two are W32-3's, the last two are budgets needing a measurement.
```

- [ ] **Step 4: Run the documentation checks**

```bash
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
```

Expected: both PASS, with the appended requirement covered once Step 2 has retargeted the markers.

- [ ] **Step 5: Run the full gate**

Run every command in both gate blocks at the top of this plan, each on its own line, reading
each one's own exit code. The frontend half is required: Task 2 and Task 4 both changed
`docs/contracts/openapi/generated.json`.

- [ ] **Step 6: Commit**

```bash
git add docs/specs/01-data-management.md docs/roadmap.md
git commit -m "docs(w32-2): the built-in-rule requirement, and the catalogue count resolved"
```

---

## Closing the slice

- [ ] Every task's steps are checked.
- [ ] `scope-audit.py DATA --catalogue VR` reports 38/38 and exits 0, and was shown to report
      37/38 and exit 1 on a deliberately removed entry.
- [ ] `generate-contracts.py --check` passes, and was shown to fail on a hand-edited schema.
- [ ] The migration was downgraded and re-upgraded against the compose stack.
- [ ] `demo.py` runs end to end with the new seeding on the production path.
- [ ] Backend tests ran against a live database — no `SKIPPED` in the DB suite.
- [ ] The three findings recorded but not fixed each have an owner written down.
- [ ] The branch is pushed and a PR is open. Do not force-push, do not merge, do not push to
      `main`.

## Self-Review

**1. Spec coverage.** §4.4's four tables are transcribed entry-for-entry in Task 1 Step 4, and
Task 1 Step 1 asserts the counts per layer and the id sets, so a dropped row fails rather than
passing quietly. §4.4 line 415's rule about thresholds is honoured by omitting them and said
out loud in `BuiltinRule`'s docstring. §4.5's lifecycle is left intact — the constraint gains
an arm for built-ins and the workspace path is untouched. W6b-13's blocker (the collection
route) is Task 4. The one thing §4.4 states that this slice does *not* encode is VR-DST-1's
graded severity cell, and Task 1 Step 4 says why and cites the amendment that settled it.

**2. Placeholder scan.** Three test bodies are elided with `...` — Task 3 Step 1's second and
third, and Task 4 Step 1's third — and each names the exact file and line range of the idiom
to copy (`test_api_models.py:61-96`, `test_api_models.py:254-272`) rather than saying "similar
to the above". Task 3 Step 7 and Task 4 Step 3 describe an edit whose surrounding code the
implementer must read, and both name the file, the line range and the ordering rule. The
requirement id is deferred to Task 5 Step 1 only because `audit-docs.py` exempts an
undefined id solely on a line already carrying `Next free:`.

**3. Type consistency.** `BuiltinRule.catalogue_id` (Task 1), `ValidationRule.catalogue_id`
(Task 2), `ValidationRuleRow.catalogue_id` (Task 3) and the endpoint's `catalogue_id` field
(Task 4) are one name across all four layers, `str` at the schema level and `str | None` where
a workspace's own rule can appear. `seed_builtin_rules(session, workspace_id, *, authored_by)`
is called with that signature at both wiring sites in Task 3 Step 7. `builtin_rule` is the
accessor's name throughout, singular, matching `role_permissions`'s pattern of an accessor
beside a constant.
