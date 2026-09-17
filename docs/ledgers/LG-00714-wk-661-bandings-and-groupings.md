---
id: LG-714
family: ledger
title: WK-661 — bandings and groupings
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-08-15
owner: executor
phase: P1b
work: WK-661
plans: [PL-NNNNN]              # every plan this ledger has executed; append, never remove
corrected_by: []
relates: []
was: docs/audit/closure-records.md
---

### WK-661 — bandings and groupings, 2026-08-15 *(in progress, not closed)*

The second slice, and the one the spine's own resolver named as missing: `resolve_factors`
refused `banding` and `grouping` by name rather than treating either as its raw column.
Both now resolve, which is FR-83's closed set going from one arm to three.

| Delivered | Evidence |
|---|---|
| `Banding`, `Grouping`, their proposals and `GroupingEvidence` in `model-schema` | §4.2's invariants at the type — strictly increasing boundaries, `labels` = `len(boundaries) - 1`, unique labels, a `null_level` that is not also a band. `unseen_level_behaviour` has **no default**, so FR-104's "mandatory" is a `422` rather than a convention |
| `propose_banding` — `equal_width`, `quantile`, `exposure_quantile`, `credibility` | an exposure quantile puts a fifth of the *exposure* in each of five bands on a book where a row quantile would put a third of the rows and a tenth of the exposure in the first. Both are tested, and that they *disagree* is tested too — otherwise neither test says which method ran |
| `propose_grouping` — `credibility_weighted`, `hierarchical_clustering` | twenty levels drawn from four true rates collapse to exactly four, splitting none of them |
| FR-107 evidence | deviance before and after as two one-factor Poisson fits against the same saturated model, so the difference is a likelihood-ratio statistic on `df_saved`. Collapsing twenty levels that are really four gives p ≈ 1; collapsing all twenty into one gives p < 1e-6, which is the test that stops the p-value being decoration |
| `apply_banding` / `apply_grouping`, and both through `resolve_factors` and `fit_glm` | a book with three flat frequency steps, banded on the step boundaries, recovers each band's relativity as the ratio of its step to the base band's |
| `POST`/`GET /bandings`, `POST`/`GET /groupings`, both `/propose` routes | proposing needs a `validated` version (R1) and persists nothing; persisting allocates the next version (FR-101) and audits it (FR-108). Insert-only at the privilege layer, so `UPDATE` and `DELETE` are refused for `gip_app` and not only by the service |
| **`spec_hash` carries its algorithm version** | `v1:sha256:…`, with the version inside the hashed payload as well as in front of it, `spec_hash_is_current` to find a stale one, and `models.spec_hash` widened 71 → 80 so the first tagged digest is not truncated into a different valid-looking one. OQ-582 named this as the precondition for the first new field |
| **`progress` restored to `fit_glm`** | `00` §5.5's injected callback, six stages, and `pricing_core.ScaledProgress` so the handler places the core's `0..1` in a window instead of the bar going backwards. A fit no longer sits at 35 % for its whole duration |

**Three defects found by building, each fixed here:**

- **`GLM_SEPARATION_DETECTED` was raised by `pricing-core` and registered nowhere.** The fit
  handler maps a `GlmFitError`'s code straight into a `PlatformError`, and an unregistered
  code raises `ValueError` *from inside the error path* — so the one failure FR-115
  exists to name arrived as a stack trace about error codes. Now registered, with a test
  derived from the `GlmFitError` call sites so the next one is covered on the day it lands.
- **`POST /factors` turned a `Factor` invariant into a 500.** The handler constructed the
  artifact itself, so every rule the type enforces — a prohibition with no reason, a
  monotonic direction with no rationale — reached the caller as an internal error. It is
  built during request validation now, and answers `422`.
- **Nothing tested that a factor's declared type is the transformation applied.** Deleting
  the banding branch of `resolve_factors`, so a `banding` silently returned its raw column,
  broke no test: the banding suite exercised `apply_banding` directly and the GLM suite only
  ever fitted `identity` factors. `test_factor_resolution.py` exists because of that
  injection.

**NFR-477 measured, and met for three of four methods.** `02` §9 carries the table:
bandings 0.11–0.24 s, `credibility_weighted` 4.24 s, `hierarchical_clustering` **6.52 s
against a 5 s budget** at the 10 000 levels the requirement names. Stated rather than
rounded away, with an owner — the factor workbench slice, which is the first caller that
will feel it. NFR-478 was added in the same pass, because computing the source summary
twice was 4 s of the original 8.59.

**Not delivered.** `scope-audit MODEL --endpoints` reads **10 of 25** and `--sections
3.1,3.2,3.3` reads 15 of 17. The two without evidence:

| Requirement | Verdict |
|---|---|
| FR-95 — `expression` factors | **not started.** Needs §4.6's restricted grammar, the parser, and its security review — the same machinery OQ-573 gates for custom objectives. Owned by that slice, not this one |
| FR-96 — factor versioning | **delivered and now tested.** `create_factor` has always allocated the next version; nothing asserted it until the audit said so |

**Three divergences from committed contracts, found when `main` moved under the branch and
fixed here.** All three were mine, and all three were readable in `docs/contracts/` before a
line of this slice was written:

| Divergence | Resolution |
|---|---|
| `credibility_standard` as a top-level field on `Grouping` | `grouping.schema.json` has carried `method_params.credibility_model` since Phase 0. The contract was right; the field is gone, `method_params` widened to hold a string and an object, and a typed `credibility_model` property reads it back. FR-106 (OQ-579, decided 2026-08-15 in #73) adds `credibility_pk` and `credibility_components`, now both carried |
| `band_stats` keyed by `level` while `banding.schema.json` said `label` | The two Phase-0 schemas disagreed with each other — `profile.schema.json` says `level` for the same statistics from the same requirement. Resolved toward `level`: a band **is** a level, so `banding.schema.json` now points at the one-way row shape rather than defining a second one |
| `Banding` carried no `minimums` | The schema declares them and FR-100 calls them configurable. They were arguments to `check_banding`, so the configured floor persisted nowhere — two fits of the same banding could apply different floors and the artifact would record neither. Now on the artifact, with the keyword arguments as an override for what-if evaluation |

The lesson is narrower than "read the contracts": these are **hand-authored Phase-0**
schemas that no generator checks, so nothing failed. `generate-contracts --check` compares
the *generated* files against the models and is silent about the twenty hand-written ones.

`reference_hierarchy` grouping is declared and **refused by name**: it needs a Reference
Table, which ADR-703 keeps out of the package. `tree` banding and `tree` grouping were
refused alongside it until **OQ-583** was decided (2026-08-17) — `pricing-core` now
declares `scikit-learn` and fits both with a depth-limited `DecisionTreeRegressor`
(FR-103). `buhlmann_straub` is refused the same way — **not** because OQ-579 is open (it was
decided in #73 while this branch was in review) but because FR-106 makes the model a
recorded property of the grouping, and its `credibility_components` would come back null
for a model that is supposed to persist them. In every case the alternative was a quantile
cut recorded under the label `tree`, which is a method recorded as one it is not.

**Still declared and unbuilt after this slice:** spec validation, diagnostics, transparency,
backtests, comparison, prediction, GBMs, custom objectives, custom metrics, peril
structures — and the factor workbench view (`00` §5.6's `/factors/:datasetVersionId`), which
has an API to talk to now and no screen.
