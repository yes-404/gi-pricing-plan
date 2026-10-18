---
id: FD-8102
family: finding
title: POST /bandings saves a slug that ArtifactRef later refuses, and the compile Job names neither the artifact nor the slug
status: active
created: 2026-10-17
owner: auditor
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
corrected_by: []
relates: [WK-1178, FD-1384, RL-1383, SL-1543, NFR-499]
---

# FD-8102 — POST /bandings saves a slug that ArtifactRef later refuses, and the compile Job names neither the artifact nor the slug

## Finding

**MEDIUM; owner WK-1178; verdict deferred with an owner, now with a deadline: before the P2
code freeze (Wed 4 Nov 2026), see Close.** Two defects in one chain, the
maintainer's entry "2026-10-17 21:04:43 BST" (`to-lead.md`, item 3): a validation missing at the
write boundary, and a cause that is not usable when the failure surfaces. Neither mispriced a
quote; both fail loudly, late.

1. **Missing boundary check.** `Banding.slug` is a plain `str`. `POST /bandings` accepts any
   string, persists it, and the same slug then cannot be wrapped in an `ArtifactRef`.
2. **Unusable cause.** A GLM pinned to that Banding fails `rating.compile`. The Job carries code
   `BUNDLE_COMPILE_FAILED` and a detail that keeps the rule's text but names no artifact type,
   slug or version.

A second symptom surfaced on 2026-10-18, below: the same missing check, hit on the GBM path.

Observed in SL-1543's test world: Banding `driv_age-banding` saved, compile `ValueError` "not a
valid artifact reference: the slug is outside the artifact type's slug grammar". (That slug
contains `_`, which only the `factor` grammar admits.)

## Evidence

At `origin/main` 9469721d (docs-d21 @50bc0ca2 contains it), read by the author:

- `packages/model-schema/src/model_schema/modelling.py:356` `Banding.slug: str`, no pattern;
  the model validator at `:383` checks boundaries and labels only.
- `backend/src/app/api/models.py:384-389` `POST /bandings` takes `body: Banding`;
  `backend/src/app/platform/transformations.py:260` `create_banding` uses `banding.slug` as is
  (version lookup, `BandingRow.slug`, audit `entity_ref`). Nothing validates the slug.
- `packages/model-schema/src/model_schema/refs.py:37` `_SLUG = [a-z0-9][a-z0-9-]{1,62}`; `:42`
  `_FACTOR_SLUG` admits `_` for the `factor` type only (RL-1383); `:132` `slug_is_admitted`;
  the `ArtifactRef` validator at `:112-114` raises `InputFreeError` "not a valid artifact
  reference: the slug is outside the artifact type's slug grammar" (no slug, type or version in
  the text).
- `packages/pricing-core/src/pricing_core/rating/compile.py:836` `_carry_glm_inputs` builds
  `ArtifactRef(type=kind, slug=item.slug, version=item.version)` for each Factor, Banding and
  Grouping of a GLM pin (`:859` from the `compile_bundle` path; `:1207`, `:1218` also).
- `backend/src/app/platform/rating_versions.py:826-833` catches the `ValueError`;
  `safe_error_detail` (`safe_error.py:180`) keeps a `ValidationError`'s text input-free (NFR-499);
  the handler re-raises `PlatformError("BUNDLE_COMPILE_FAILED", ..., 422, detail)`.
- **Measured** on docs-d21 @50bc0ca2 (`uv run --directory <wt> python`, probe in the session
  scratchpad): `ArtifactRef(type=t, slug="driv_age-banding", version=1)` then `safe_error_detail`:

  | type | result |
  |---|---|
  | banding | `1 validation error(s) for ArtifactRef: <root>: [value_error] Value error, not a valid artifact reference: the slug is outside the artifact type's slug grammar` |
  | grouping | the same text |
  | factor | accepted |

  So the cause **is not dropped** (a correction to the first reading of the symptom): the rule's
  text reaches the Job. What is missing is *which* artifact: no type, slug or version, and the
  allow-list forbids echoing input, so the fix has to name the offender from the carried item,
  not from the exception.

## Second symptom (2026-10-18)

The maintainer's entry "2026-10-18 03:02:03 BST" (`to-lead.md`, items 1 and 3), on SL-1734's
#1331 CI. SL-1734's 9270bb0d made `fit_gbm` run the FR-100 banding check
(`gbm.py:610` → `check_fit_bandings` → `check_banding`), and `check_banding` builds
`ArtifactRef(type="banding", slug=banding.slug, version=banding.version)` at
`packages/pricing-core/src/pricing_core/modelling/bandings.py:590`. SL-1758's fixture
(`test_rating_gbm_banded_refusal.py:53-54`) names the bandings `driver_age-bands` and
`veh_power-bands`; `_` is outside the `banding` slug grammar (`refs.py:38` `_SLUG`), so the
check raised a raw `ArtifactRef` `ValidationError` instead of the 7 cases' original refusal
codes. First red at c3cc2694; 49aaf6e4 and f40d130b are both 7F/3P. The test was a fixture
fault, fixed test-only (fix (A) of that entry; (B) refused).

The product exposure is the same gap as the first limb, read at `origin/main` 8ac6290b:
`Banding.slug` is `slug: str` at `packages/model-schema/src/model_schema/modelling.py:407`,
`Grouping.slug` likewise at `:557`, and `POST /bandings` persists a slug as given. After SL-1734 a
user can persist `driver_age-bands` and then meet a raw `ValidationError` fitting a GBM with it:
a user-reachable, opaque failure on a core path. Loud, not a mispricing, nothing released yet.

## Other artifact types with the same gap (checked, not widened)

Slug fields read at 9469721d. "Pattern at write" = the request or model type carries a slug
pattern; "ref type" = the type is in `ARTIFACT_TYPES` (`refs.py:24-35`).

| Type | Slug field | Pattern at write? | Same gap? |
|---|---|---|---|
| banding | `modelling.py:356` `str` | no | **yes** (this finding) |
| grouping | `modelling.py:506` `str`; `POST` takes `body: Grouping` (`api/models.py:480`) | no | **yes** by the same read; the `ArtifactRef` refusal for `grouping` measured above |
| factor | `modelling.py:134` `str`; `FactorCreate.slug` `str` (`api/models.py:207`) | no | already filed: **FD-1384** (its row says Banding and Grouping were "not swept"; this finding sweeps them) |
| reference_table | `api/reference_tables.py:65` `TableCreate.slug` pattern `^[a-z0-9][a-z0-9-]{1,62}$` | yes | no |
| validation_rule | `api/validation.py:89` `RuleCreate.slug` same pattern | yes | no |
| dataset | `datasets.py:164` pattern `^[a-z0-9][a-z0-9-]{1,62}$` | yes | no |
| types using `Slug` (`refs.py:62`) | rating algorithm, sub-graph, rate table, peril structure, custom objective/metric, deployment, regression suite (`rating.py`, `sub_graphs.py`, `perils.py`, `objectives.py`, `deployments.py`, `regression.py`) | yes | no |
| validation_rule_set | `validation.py:163` `str`; built at `platform/validation_rules.py:790` and `worker/data_handlers.py:240` | no pattern on the type | **not verified**: its slug is derived, not client-supplied, and no creation route was traced |
| model | `Model` family slug fields `modelling.py:818`, `:2041` `str` | no pattern on the type | **not verified**: not traced to a write route |

The opaque-error limb is general: it is in `_carry_glm_inputs`, so any Factor, Banding or
Grouping slug refused there fails the same way.

## Options (none picked)

- **(a) Validate at creation, in `model-schema`.** Give `Banding.slug` (and, by the same read,
  `Grouping.slug`) the `Slug` pattern. Every writer then gets it, `POST /bandings` answers 422
  naming the field, and `docs/contracts/` regenerates with the pattern (FR-451 drift check).
  `Factor` stays under FD-1384 with its own grammar. Needs a check for stored violators before
  the pattern lands.
- **(b) Name the offender in the compile failure.** Catch the refusal in `_carry_glm_inputs`
  and raise a named, input-free error carrying the artifact type and which pin (it has `kind`
  and `resolved` in hand), so the Job detail names what to fix.
- **(c) Both.** (a) closes the cause for new writes; (b) covers rows already stored and any
  future type with the same gap.

## Close (ruled 2026-10-18)

The maintainer's entry "2026-10-18 03:02:03 BST", item 3, rules the close as option (a), the
cause: `Banding.slug` and `Grouping.slug` typed `Slug` in `model_schema`, refused 422 at
`POST` with a typed code, `docs/contracts/` regenerated, and a red-first test at the API.
MEDIUM (loud, no mispricing); owner WK-1178; due **before the P2 code freeze, Wed 4 Nov
2026**, not deferred past it. Its own slice: SL 8116 under PL 8115 (reserved; its fix slice
gets its own GO). Option (b) stays open for rows already stored and is not ruled here.

## Disposition (as filed 2026-10-17; the Close above supersedes its "deferred" wording)

Deferred with an owner: WK-1178. Decision on the option is the lead's or an RL's; this record
picks none. The event that next discharges it: a merged change adding the pattern and/or the
named compile error, or a dated ruling accepting the absence. Filed under working id 8102; second symptom and Close appended 2026-10-18.
