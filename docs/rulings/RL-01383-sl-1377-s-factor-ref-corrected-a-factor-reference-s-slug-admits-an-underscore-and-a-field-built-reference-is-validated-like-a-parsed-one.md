---
id: RL-1383
family: ruling
title: SL-1377's factor_ref corrected — a factor reference's slug admits an underscore, because a Factor's slug is a term name; the ArtifactRef grammar is type-dependent for factor alone, and a field-built reference is validated like a parsed one
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-03              # the mint date (check 31); ruled 2026-10-03
owner: decision-maker
tree: 33cbff79ba83dbdf7912c5ddbfc6448008a8a451
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1361
relates: [RL-1361, FD-1384, RL-1375, PL-1376, SL-1377, FD-1357, FR-9, FR-228, FR-230, FR-4, FR-96, FR-209]
---

# RL-1383 — SL-1377's `factor_ref` corrected: a `factor` reference's slug admits `_`

## How this was ruled

- **Filed under working id 9743; minted 2026-10-03 as RL-1383.** In the minting commit,
  `RL-1361`'s header gains this record's minted id in `corrected_by:` (the append check 34
  allows). The finding this record proposes was filed in the same PR under working id 9742
  and is minted as FD-1384 in the same commit.
- **Ruled 2026-10-03 at effort `medium`** by the decision-maker session `dm-1377`
  (`echo $CLAUDE_EFFORT` printed `medium`). The lead's GO names medium: to-lead.md entry
  headed "2026-10-03 17:27:58 BST — LANE B STOP accepted; GO dm-1377 (opus, medium,
  decision-maker.md) to rule A/B/C on factor_ref vs the slug grammar; what the brief must
  require". The charter's raise to `high` is the maintainer's, and none was made.
- **The question** came from executor-1377 through the lead: from-lead-2026-10-03.md entry
  headed "2026-10-03 17:27:30 BST — LANE B STOP: SL-1377 premise defect (factor_ref as
  ArtifactRef cannot hold underscore Factor slugs); DM ruling GO asked". Its options: (A)
  admit `_` for the `factor` type only; (B) a local `factor_ref` shape; (C) constrain Factor
  slugs to the grammar. The executor recommended (A).
- **Every premise below was re-read** at `origin/main` `d672f991` (tree `33cbff79`), not
  taken from the relay. Two relayed locators were wrong, and the corrected ones are used
  here: `Factor.slug` is `modelling.py:133` (the class opens at `:122`), and the platform
  re-reads a stored definition at `platform/rate_tables.py:276` and `:557`, not `:267`.

## Verified first, at `d672f991`

| Premise | Where | What the source says |
|---|---|---|
| The reference slug grammar | `packages/model-schema/src/model_schema/refs.py:33` | `_SLUG = r"[a-z0-9][a-z0-9-]{1,62}"`, with no `_`. `_REF_RE` (`:37-39`), `Slug` (`:41`), `ModelRef` (`:46`) and `REF_PATTERN` (`:51-53`) are all built from it |
| A field-built reference is not checked | `refs.py:71-73`, `:78-98` | `slug: str`. Only the `mode="before"` validator checks the grammar, and only when the input is a string. `ArtifactRef(type=…, slug=…, version=…)` skips it |
| `Factor.slug` has no grammar | `model_schema/modelling.py:133`; `backend/src/app/api/models.py:207` (`FactorCreate`) | `slug: str` in both |
| The envelope's slug pattern | `docs/specs/00-overview.md:295` (§4.3); `02-modelling.md` §4, "All entities carry `ArtifactEnvelope` (`00` §4.3)" | `"slug": "string, ^[a-z0-9][a-z0-9-]{1,62}$"` |
| The spec's own Factor slugs | `02-modelling.md:386` (§4.1 example); `:715`, `:839`, `:1211`, `:1364`, `:1413` | `driver_age_banded` as the Factor's slug, and the same name as an interaction constraint, a monotone-constraint key, a GLM term (`driver_age_banded[17-20]`), a GBM `feature_order` entry and an EBM term |
| `RL-1361`'s texts use it | `RL-1361` T4 | `"factor_ref": "factor:driver_age_banded@3"` |
| The demo's Factor slugs | `examples/fremtpl2/model.py:60-74` | slug = column name: `driv_age`, `veh_age`, `veh_power` (continuous); `veh_brand`, `veh_gas`, `area`, `region` (categorical) |
| The audit log already writes them | `backend/src/app/platform/modelling.py:260` | `entity_ref=f"factor:{factor.slug}@{version}"`, unvalidated (`AuditEvent.entity_ref: str`, `model_schema/audit.py:59`) |
| Models pin Factors by id, not by `ArtifactRef` | `modelling.py:842` | `factors: tuple[UUID, ...] = ()`; `banding_id`, `grouping_id`, `operand_factor_ids` are UUIDs too |
| Where a stored rate-table definition is re-read | `backend/src/app/platform/rate_tables.py:276` (`diff`), `:557` (`_to_version`) | `RateTable.model_validate(version_row.definition)`. `_to_version` serves export CSV (`:318`), export XLSX (`:333`), import preview (`:356`), import confirmed (`:388`) and bulk operation (`:761`) |

**Probe** (scratch `/tmp/dm1377_probe.py`, sha256 prefix `d6d1e3e4e5632eab`, run with
`PYTHONPATH=<worktree>/packages/model-schema/src` so it imports this tree's `model_schema`):

| Input | Result |
|---|---|
| `Factor(slug=…)` with `""`, `"Veh Brand"`, `"a:b@1"`, a 65-character slug, `"veh_brand"` | all five accepted |
| `ArtifactRef(type="factor", slug="veh_brand", version=1).model_dump(mode="json")` | `factor:veh_brand@1` |
| `ArtifactRef.model_validate("factor:veh_brand@1")` | `1 validation error for ArtifactRef` ("not a valid artifact reference") |

So a seeded key dumps and is stored, and the next read of that version fails validation. That
is every route in the last table row above, not only the diff: a 500 on G2's exit-demo path.

## Reach, measured

**1. Every place on `main` that refers to a Factor by slug.** Predicate:
`grep -rn 'factor_slug\|factor_ref\|by factor slug\|per factor slug\|Factor slug\|factor slug' --include=*.py --include=*.ts --include=*.vue packages backend/src frontend/src`
(excluding `/generated/`), and the name-keyed fields read from the classes.

| Kind | Where | Typed as |
|---|---|---|
| GLM terms and relativities, keyed by Factor slug | `pricing_core/modelling/factors.py:89` (`FactorMatrix.terms`); `GlmFitResult.relativities` | `str` |
| GBM monotone constraints, per Factor slug | `model_schema/modelling.py:1478` | `dict[str, int]` |
| Diagnostics curves, GBM feature errors | `pricing_core/modelling/gbm.py:1295`; `test_gbm.py:712-723` | `str` |
| Rate-table key `name` (RL-1361: named after the Factor's slug) | `model_schema/rating.py:667` | `str` |
| Audit `entity_ref` on `factor.created` | `platform/modelling.py:260` | `str`, unvalidated |
| The DB lineage key | `backend/src/app/db/models.py:1323`, `:1331` | `String(64)`, unique `(workspace_id, slug, version)` |

**Every one of these is a plain `str`.** None parses the reference grammar.

**2. Does anything already pin a Factor through `ArtifactRef`?** No. Predicate:
`grep -rn '"factor:\|factor:[a-z]\|type="factor"\|ArtifactRef(type="factor"' --include=*.py --include=*.ts --include=*.vue --include=*.json packages backend frontend/src examples scripts | grep -v generated`
prints one line, the unvalidated audit f-string above. A Model pins its Factors by UUID
(`modelling.py:842`). **`RateTableKey.factor_ref` (SL-1377's WIP, `f08fa07e`, unmerged) would
be the first.** So option (B) would leave nothing else broken, and option (A) breaks nothing
that exists.

**3. Factor slugs with `_`.**

- **Examples:** `examples/fremtpl2/model.py:60-74`: **5 of the demo's 7** (`driv_age`,
  `veh_age`, `veh_power`, `veh_brand`, `veh_gas`). Of the four categorical Factors, the only
  ones FR-230 can seed, **2 of 4** (`veh_brand`, `veh_gas`). `examples/fremtpl2/seed.py`
  creates no Factor. Its `:180` `veh_brand` is a dataset column, and that column is the slug
  `model.py` gives the Factor.
- **Literals in the code and the tests:**
  `grep -rhoE "slug=[\"'][a-z0-9]+_[a-z0-9_]*[\"']" --include=*.py backend packages examples scripts`
  prints 3 (`exposure_offset`, `age_spline`, `age_over_ncd`, in 1 file);
  `grep -rhoE "[\"']slug[\"']: *[\"'][a-z0-9]+_[a-z0-9_]*[\"']" --include=*.py --include=*.ts --include=*.json backend packages examples scripts frontend/src`
  prints 2 (`driver_age_banded`, `age_x_vehicle`, both in
  `packages/model-schema/tests/test_factor.py`). The f-string `crossed_{…}` slugs in the
  backend tests are not counted by either predicate. They appear in the databases below.
- **Every `gipricing*` database** on the local `gi-pricing-postgres-1` container, read-only,
  2026-10-03 at about 17:32 BST. For each database
  `select datname from pg_database where datname like 'gipricing%' or datname='gip'` returns,
  this runs through `docker exec gi-pricing-postgres-1 psql -U gipricing -d "$db" -Atc`:

  ```sql
  select count(*),
         count(*) filter (where slug ~ '_'),
         count(*) filter (where slug !~ '^[a-z0-9][a-z0-9-]{1,62}$'),
         count(distinct slug) filter (where slug ~ '_')
  from factors
  ```

  82 databases. 3 have no `factors` table. 73 have no Factor row with `_`. **6 hold 45 rows
  with `_`**: `gipricing` 1 (`resid_flag`), `gipricing_tree-s3` 1,
  `gipricing_w37-6-run2-gate-1789690960` 1, `gipricing_wt-d9d13-redo` 8,
  `gipricing_wt-paths-d9-d13` 18 (8 distinct: `claim_amount_minor`, `resid_flag` and six
  `crossed_<hex>`), and `gipricing_gate-1369m_daab5cee` 16. The last is a live gate
  database: it held 2 rows at 17:31 and 184 at 17:36. **In every database, the rows outside
  today's reference grammar are exactly the rows with `_`.** Re-run with the third predicate
  replaced by the grammar ruled below, `slug !~ '^[a-z0-9][a-z0-9_-]{1,62}$'`: **0 rows in
  every database.** The `bandings` and `groupings` tables hold 1 row each in one database,
  and both are inside today's grammar. None of these databases holds the freMTPL2 demo
  seed.

**What the numbers mean.** Nobody seeds an underscore Factor today only because seeding has
never bound a Factor. The first seed of `veh_brand` (G2's A1 on the seven-factor GLM) is the
failure. No stored rate table carries `factor_ref` yet, because the field is unmerged.

## Which side was wrong (`CLAUDE.md` §0)

**The specification contradicted itself, and the half that was wrong is the grammar's reach
over Factor.** `00` §4.3 gives every persisted entity the slug pattern
`^[a-z0-9][a-z0-9-]{1,62}$`, and `02` §4 says every one of its entities carries that
envelope. But `02`'s own Factor example has been `driver_age_banded` since Phase 0, and so has
every place the spec names a term: `interaction_constraints`, `monotone_constraints`, GLM
coefficient terms, GBM `feature_order`, EBM terms and diagnostics. The code followed the
examples: `Factor` never carried the envelope, and its `slug` is a plain `str`. The demo uses
the column name as the slug.

**Why the examples are right and the pattern is wrong for Factor.** A Factor's slug is not
only a handle. It is the name its term carries in every downstream artifact: the design
matrix, a feature list, a monotone-constraint key, and (RL-1361 section A) the name of a
seeded rate table's one key. A rate-table key with no binding joins a portfolio "by the column
of its own name" (RL-1361 Ruled item 2), and the dataset columns it must meet are
underscored. A hyphen-only Factor slug would make the term name and the column name differ
for every multi-word column.

**`RL-1361` inherited the contradiction.** It ruled `factor_ref: ArtifactRef` (Ruled item 9)
and wrote its own T4 example as `factor:driver_age_banded@3`, a string its chosen type
refuses. Its locator table read `ArtifactRef` for the `factor` type and the `version: int`
pin (`:113`), but not the slug grammar. This record corrects that premise. **No text of
`RL-1361` changes: T1, T4 and T5 stay byte-exact**, and `factor:driver_age_banded@3` becomes a
valid reference.

**The code was half wrong too.** `Factor.slug` has the right alphabet but no grammar at all:
the probe accepts `""`, a space, `:` and `@`, and 65 characters against a `String(64)`
column. That is a defect in its own right, separate from this decision, and FD-1384 proposes
it. A `factor_ref` ruled here cannot depend on that fix, so the seed refuses an out-of-grammar
slug itself (Ruled item 3).

## The options, weighed

| | (A) `_` for `factor` only | (B) a local `factor_ref` shape | (C) constrain Factor slugs to today's grammar |
|---|---|---|---|
| Canonical form (ID-3) | One reference form. Its slug grammar has one per-type case, built in one place (`refs.py`) | A second reference shape for one type. ID-3 says the canonical external reference to *any* artifact is `{type}:{slug}@{version}`; `CLAUDE.md` §2 refuses a second definition of a shape | Unchanged |
| The audit log | Its existing `factor:<slug>@<n>` strings (`platform/modelling.py:260`) become canonical, and so parseable | Stays unparseable | New rows parse; existing rows do not |
| Stored data | No migration. Nothing stores `factor_ref` yet; Factor rows are untouched | No migration | **Impossible without breaking FR-4 and FR-96.** A slug is the lineage key and stored versions are immutable. Refusing on read fails the whole workspace's factor list, the failure FR-209 records for `to_factor` |
| The open-source install base | Widening: every reference valid before is valid after. A client that validates with the old published pattern refuses the new `factor:` strings, which the audit log already emits | No change for others; clients meet a second format | Breaks every install that has an underscore Factor: 45 rows in 6 of 79 local databases, and 5 of the demo's 7 |
| Spec examples | All stand | RL-1361 T1, T4 and T5 re-worded | `02` §4 rewritten throughout; the slug and the column name diverge |
| Cost | `refs.py`, one hand-authored contract, regenerated contracts, three spec notes | Rate tables only, but a new shape | Largest |

**Ruled (A).** (C) is refused outright: it is the only option that breaks stored data, and
immutability forbids the repair. (B) is refused because it solves a grammar question by
duplicating a shape, and it leaves the audit log's references outside the grammar. A
type-dependent grammar is a cost, and it is kept small: one extra case, for the one type
whose slug is a term name, generated into the contract from the same constants as the parser.

**Why not widen every type.** One pattern for all types would be simpler. But then the
published reference pattern would accept `model:motor_gb@1` while `ModelRef`, `Slug` and every
envelope refuse it. The contract would be looser than the code, the defect
`test_authored_pattern_accepts_exactly_what_the_parser_accepts` exists to refuse.

## Ruled

1. **The grammar.** In `refs.py`, `_SLUG` stays `[a-z0-9][a-z0-9-]{1,62}`. A new constant,
   `_FACTOR_SLUG = r"[a-z0-9][a-z0-9_-]{1,62}"`, is the slug grammar of the `factor` type and
   of no other. `Slug` and `ModelRef` are unchanged. `REF_PATTERN` is built from the two
   constants and `ARTIFACT_TYPES`, and its value is exactly (verified by
   `/tmp/dm1377_pat.py`, sha256 prefix `c5bd112fa9844419`, which builds it from this tree's
   `ARTIFACT_TYPES` and checks 15 cases):

   ```text
   ^((banding|custom_metric|custom_objective|dataset|dataset_version|dossier|gipp_check|grouping|model|monitor|optimisation_run|peril_structure|rate_table|rating_algorithm|rating_version|reference_table|regression_suite|sub_graph|validation_rule|validation_rule_set):[a-z0-9][a-z0-9-]{1,62}|factor:[a-z0-9][a-z0-9_-]{1,62})@[1-9][0-9]*$
   ```

   The parser (`_REF_RE` with `parse` and the `mode="before"` validator) accepts exactly the
   strings this pattern accepts. A non-`factor` reference whose slug contains `_` is refused
   with a message that contains "artifact", like every other malformed form.
2. **A field-built reference is validated like a parsed one.** `ArtifactRef` gains a
   `mode="after"` check: `type` is in `ARTIFACT_TYPES`, and `slug` fully matches its type's
   grammar. `ArtifactRef(type="model", slug="motor_gb", version=1)` raises
   `ValidationError`, as `ArtifactRef.model_validate("model:motor_gb@1")` already does. This
   closes the class, not just the instance: a reference that can be built is a reference
   that can be re-read. **Blast radius, measured:** 51 `ArtifactRef(` construction sites in
   `backend packages examples scripts`
   (`grep -rn "ArtifactRef(" --include=*.py backend packages examples scripts | grep -v "ArtifactRef(BaseModel"`),
   and none passes a literal slug containing `_`, an upper-case letter or a space. A site
   that builds from an unconstrained field and now raises was already writing an
   unparseable reference. If the full suite finds one outside the tests, the executor stops
   and reports it as a finding. The check is never weakened to let it pass.
3. **Seeding refuses an out-of-grammar Factor slug by name.** If the Factor that a seed
   binds has a slug that `_FACTOR_SLUG` does not admit (for example `Region` or `x`, which
   `Factor` accepts today), the seed is refused: 422 `VALIDATION_FAILED`, with a detail that
   names the slug. It is never a 500, at the seed or at a later read.
4. **No migration.** No stored rate table carries `factor_ref`. Stored Factor rows, audit
   rows and every other reference are unchanged. Every reference valid before this ruling
   is valid after it.
5. **RL-1361 and RL-1375 are unchanged.** `factor_ref: ArtifactRef | None`, of type `factor`
   (RL-1361 Ruled item 9), stands. RL-1361's T1 to T12 and RL-1375's T-A and T-B are applied
   as written.
6. **The unconstrained `Factor.slug` is not fixed by SL-1377.** It is filed as FD-1384,
   with an owner and a severity that were the lead's and the maintainer's to set; they are set at
   the mint (see FD-1384's Disposition).

## Spec and contract texts this ruling carries

They land in SL-1377's commit with the `refs.py` change (`CLAUDE.md` §2: spec, code and tests
land as one commit). The executor copies them from this file on `main` once it is minted,
never from a relay. Placement was read at `d672f991`. The placeholders are: `<fix date>`, the
date of SL-1377's commit, written `YYYY-MM-DD`; `<RL id>`, this ruling's minted id, written
`RL-NNNN`; `<FD id>`, FD-1384's minted id, written `FD-NNNN`. Nothing else is a placeholder.

**T-C — `00` ID-3, appended.** Placement: `docs/specs/00-overview.md`, the ID-3 row (`:282`).
The text is **appended** to the end of the second cell, after `when generation compared the
two.` and one space, before the closing ` |`. Nothing is struck.

```text
**Amended <fix date> (`<RL id>`): a `factor` reference's slug may contain `_`.** For every other type the slug is `[a-z0-9][a-z0-9-]{1,62}`, the `slug` pattern of §4.3. For `factor` it is `[a-z0-9][a-z0-9_-]{1,62}`, because a Factor's slug is the name of its term in a design matrix, a feature list and a rate-table key (`02` §4.1), and `02`'s own example, `driver_age_banded`, contains one. A reference whose slug its type's pattern does not admit is refused, whether it is parsed from the string or built from its fields.
```

**T-D — `00` §4.3, inserted.** Placement: after the envelope's closing fence (`:307`, the
first line that is exactly three backticks after the `"description": "string|null"` line) and
one blank line, before the `---` that ends §4.

```text
> **A Factor's slug, noted <fix date> (`<RL id>`).** The `slug` pattern above holds for
> every entity except a Factor, whose slug is `^[a-z0-9][a-z0-9_-]{1,62}$`: it may contain
> `_`, because it names the Factor's term wherever the term appears (`02` §4.1, ID-3).
```

**T-E — `02` §4.1, inserted.** Placement: `docs/specs/02-modelling.md`, after the line below
(`:420`; it occurs exactly once in the file) and one blank line, before
``### 4.2 `Banding` ``.

```text
  believing they fixed both.
```

```text
**Noted <fix date> (`<RL id>`): the slug may contain `_`.** A Factor's `slug` is
`^[a-z0-9][a-z0-9_-]{1,62}$`, the one exception to `00` §4.3's slug pattern. It is the name of
the Factor's term in the design matrix, in `feature_order` and `monotone_constraints`, and in
a seeded rate table's key (`03` FR-230), and those names follow the dataset's columns, as
`driver_age_banded` above does. A pinned reference to a Factor is `factor:<slug>@<version>` in
this pattern (`00` ID-3). The `Factor` type does not yet refuse a slug outside it
(`<FD id>`); seeding refuses one by name.
```

**T-F — the hand-authored reference contract, replaced.** Placement:
`docs/contracts/schemas/common/artifact-ref.schema.json`, the `"pattern"` line (`:7`). Replace

```text
  "pattern": "^(banding|custom_metric|custom_objective|dataset|dataset_version|dossier|factor|gipp_check|grouping|model|monitor|optimisation_run|peril_structure|rate_table|rating_algorithm|rating_version|reference_table|regression_suite|sub_graph|validation_rule|validation_rule_set):[a-z0-9][a-z0-9-]{1,62}@[1-9][0-9]*$",
```

with

```text
  "pattern": "^((banding|custom_metric|custom_objective|dataset|dataset_version|dossier|gipp_check|grouping|model|monitor|optimisation_run|peril_structure|rate_table|rating_algorithm|rating_version|reference_table|regression_suite|sub_graph|validation_rule|validation_rule_set):[a-z0-9][a-z0-9-]{1,62}|factor:[a-z0-9][a-z0-9_-]{1,62})@[1-9][0-9]*$",
```

The generated contracts (`docs/contracts/schemas/generated/`, `docs/contracts/openapi/generated.json`)
are regenerated by `scripts/generate-contracts.py`, never hand-edited.
`test_artifact_ref_pattern_matches_the_authored_contract` holds T-F equal to the generated
pattern. `frontend/src/api/comparisons.ts:59`'s `MODEL_REF` matches `model:` only and is
unaffected.

## The effect on PL-1376: the dispatch-record delta

PL-1376 is merged, so it is frozen. The lead appends this delta, dated, to SL-1377's dispatch
record. The text, verbatim:

```text
**Delta <date of append> — RL-NNNN (the factor_ref slug grammar; filed as RL 9743).**
Write set, added:
- packages/model-schema/src/model_schema/refs.py — `_FACTOR_SLUG`; `REF_PATTERN`, `_REF_RE`
  and the per-type slug check; the `mode="after"` check on `ArtifactRef` (RL-NNNN Ruled
  items 1–2). Shared with: any slice editing refs.py (none found at d672f991). Serialises.
- docs/contracts/schemas/common/artifact-ref.schema.json — T-F. Hand-authored, not
  registry-exempt: serialises.
- docs/specs/00-overview.md — T-C (ID-3 row), T-D (§4.3 note). Serialises with any slice
  editing ID-3 or §4.3.
- docs/specs/02-modelling.md — T-E (§4.1). Serialises with any slice editing §4.1.
- packages/model-schema/tests/test_refs.py — Acceptance 18 appended.
Write set, widened:
- backend/tests/test_contracts.py — the parametrize list of
  test_authored_pattern_accepts_exactly_what_the_parser_accepts gains Acceptance 17's
  cases (an edit to an existing definition: serialises, as the ONE_SIDED_SLUGS edit does).
- packages/model-schema/tests/test_rate_tables.py — Acceptance 16 appended.
- backend/tests/test_api_rate_tables.py — Acceptance 19; Acceptance 4's Factor slug
  contains `_`.
- packages/pricing-core/src/pricing_core/rate_tables/operations.py — the seed refuses an
  out-of-grammar Factor slug (RL-NNNN Ruled item 3).
- docs/contracts/ generated files — regenerated (already in the write set).
Acceptance, added (each red first, as the plan's standard requires):
16. A key bound to an underscore Factor survives a re-read (FR-228). In
    test_rate_tables.py, test_a_factor_ref_with_an_underscore_slug_round_trips: a
    RateTableKey with factor_ref factor:veh_brand@1, and a RateTable holding it, each equal
    their own model_validate(model_dump(mode="json")). Red on f08fa07e: ValidationError,
    "not a valid artifact reference".
17. The published pattern and the parser agree per type (FR-9). The parametrize list gains
    ("factor:veh_brand@1", True), ("factor:driver_age_banded@3", True),
    ("model:motor_gb@1", False), ("banding:driver_age@1", False),
    ("factor:Veh_brand@1", False), ("factor:x@1", False). Red on d672f991: the two True
    cases fail.
18. A reference that can be built can be re-read (FR-9). In test_refs.py, after a positive
    control (ArtifactRef(type="factor", slug="veh_brand", version=1) constructs, and
    ArtifactRef.parse(str(ref)) equals it), each of ArtifactRef(type="model",
    slug="motor_gb", version=1), ArtifactRef(type="factor", slug="veh brand", version=1)
    and ArtifactRef(type="widget", slug="x-y", version=1) raises ValidationError. Red on
    d672f991: all three construct.
19. Through the route, nothing 500s on an underscore Factor (FR-230). After a seed of
    Factor driver_age_band, GET /api/v1/rate-tables/{slug}@1/export/csv answers 200, and
    Acceptance 4's re-seed into that lineage answers 201 with factor_ref
    factor:driver_age_band@2. A seed binding a Factor whose slug is outside the factor
    grammar (`Region`) answers 422 VALIDATION_FAILED naming the slug. Red with Tasks 1–3
    and no refs.py change: the export answers 500 (_to_version,
    platform/rate_tables.py:557), and the `Region` seed answers 201.
Acceptance 9 covers T-C, T-D and T-E as append/insert texts (anchor 1, text 1 after; text
0 before) and T-F as a replace text (find 1→0, replacement 0→1), counted with grep -cF
over the named file. Placeholders filled: <fix date>, <RL id> = RL-NNNN, <FD id> = FD 9742's
minted id.
Unchanged: Acceptance 1–15; RL-1361 T1–T12 and RL-1375 T-A/T-B, byte for byte.
```

The executor's WIP `f08fa07e` (Tasks 1–2, pushed to `sl-1377-fd-1357-multi-factor-seed`, no PR) needs no rework beyond the
added items: its `factor_ref: ArtifactRef | None` is the type this ruling keeps.

## What it obliges

- **SL-1377** applies Ruled items 1–3 and T-C to T-F in one commit with its code and tests,
  and meets Acceptance 16–19 through the delta above.
- **The lead** appends the delta to SL-1377's dispatch record, mints this record and
  FD-1384, and appends this record's minted id to `RL-1361`'s `corrected_by:`.
- **Nobody** rewrites a stored Factor, a stored rate table or an audit row.

## Acceptance — the violation that must become detectable

A reference that the platform builds and then cannot re-read. After SL-1377, a test that
builds `factor:veh_brand@1` and re-validates its dump passes (Acceptance 16). A test that
builds `ArtifactRef(type="model", slug="motor_gb", version=1)` fails at construction
(Acceptance 18), so the asymmetry that hid this defect can no longer be built for any type.

*Drafted as working id 9743; minted 2026-10-03 as RL-1383 (with FD 9742 -> FD-1384, in the same PR).*
