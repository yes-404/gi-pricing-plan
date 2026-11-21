---
id: ADR-2160
family: decision
title: The decided items of Work #1506, the read-side Provenance object and the finer-level actual-versus-expected
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-17
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 089d83857046e2aef4a7b6b3574387b5b728b72a
supersedes: []
superseded_by: [ADR-2170]   # in part: one point, see the status line
corrected_by: []
relates: [FR-6, FR-104, FR-109, FR-170, FR-2159]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2160 — The decided items of Work #1506, the read-side Provenance object and the finer-level actual-versus-expected

- **Status:** Accepted (front matter `active`). Superseded in part by [ADR-2170](ADR-02170-a-parent-the-reference-form-cannot-name-is-reported-and-never-fails-a-read.md) (2026-11-21), for one point only: #1868's "`subject_refs` is never empty" does not apply to a parent the reference form cannot name. Supersedes nothing. It lands `active` because its six decision issues, and the in-Work rulings it lists, are already decided and this record states them ([#1506, comment of 2026-11-17](https://github.com/yes-404/gi-pricing-plan/issues/1506#issuecomment-6945539154)).
- **Deciders:** the maintainer, for #1519 and #1810 ("Decided by the maintainer, 2026-11-14"). On the maintainer's behalf, by delegation: #1868, #1869 and #1870 on 2026-11-15, and #1908, the ruling on slice 4 and decisions (B) and (c) on slice 5 on 2026-11-17.
- **Decision issues:** [#1519](https://github.com/yes-404/gi-pricing-plan/issues/1519) (OQ-1910), [#1810](https://github.com/yes-404/gi-pricing-plan/issues/1810), [#1868](https://github.com/yes-404/gi-pricing-plan/issues/1868), [#1869](https://github.com/yes-404/gi-pricing-plan/issues/1869), [#1870](https://github.com/yes-404/gi-pricing-plan/issues/1870) and [#1908](https://github.com/yes-404/gi-pricing-plan/issues/1908). Each decision comment is linked in the table below.
- **Work:** [#1506](https://github.com/yes-404/gi-pricing-plan/issues/1506) (WK-1914). Plan accepted in the [comment of 2026-11-17](https://github.com/yes-404/gi-pricing-plan/issues/1506#issuecomment-6945235881); its new requirement is `00` FR-2159 ([comment](https://github.com/yes-404/gi-pricing-plan/issues/1506#issuecomment-6945244701)).
- **Number:** reserved on the coordination record of #1489 ([comment](https://github.com/yes-404/gi-pricing-plan/issues/1489#issuecomment-6888603081)). That row names five decisions (#1519, #1810, #1868, #1869 and #1870). #1506's [comment of 2026-11-17, 10:37Z](https://github.com/yes-404/gi-pricing-plan/issues/1506#issuecomment-6945638148) adds #1908, so this record covers six. When this record was written, the row on #1489 still read five.
- **Enacted by:** the pull request of #1506 that adds this record, in the slices named below. This record claims no slice that pull request does not contain.
- **Recorded after the fact.** Written on 2026-11-17, after the decisions.

## Context

FR-6 and FR-109 were both amended on 2026-10-22 down to what was built, and each left a half without an owner. FR-6 was narrowed to the producing-Job id, `job_id: UUID | None`, on ten governed shapes, and no view reads it. FR-109's chain is stored (`Grouping.parent_grouping_id`) and read by nothing, and "until it is owned, no behaviour may be built on the stored chain". #1506 owns both: the display of the producing Job on the ten shapes, and the finer-level diagnostics on a chained grouping.

Six questions had to be decided before or during the Work, each on its own decision issue with options and a recommendation. Under `CLAUDE.md` §7 a decision reached in an issue is written in `docs/adrs/` by the pull request that enacts it. One record covers all six, as [ADR-2149](ADR-02149-the-1497-plans-decided-items.md) did for #1497, at the maintainer's direction (#1506, comment of 2026-11-17, 10:33Z).

## Decision

| Issue | Question | Decided | Decision comment | Enacted by, in #1506 |
|---|---|---|---|---|
| #1519 (OQ-1910) | What is the shared `provenance` object a provenance display reads, and which artifacts carry it? | **(b)**: a read-side `Provenance` class in `model-schema`, composed by the API from the artifact's identity and its producing-Job id, and never persisted. The six artifact types that record no producing Job are brought in only by their own requirement, one artifact at a time | [2026-11-14](https://github.com/yes-404/gi-pricing-plan/issues/1519#issuecomment-6881062595), "Decided by the maintainer, 2026-11-14: option (b)" | Slice 1: `00` FR-2159, which re-widens FR-6 to the object, and `00` §10's OQ-1910 row marked decided (`docs/open-questions.md` is frozen and is not edited). Slice 2: the class, and its composition on the ten read routes. Slice 3: the badge reads it |
| #1810 | What happens to the hand-authored `docs/contracts/schemas/common/provenance.schema.json`, which nothing emits? | **B**: it is replaced by the schema generated from the `Provenance` class of #1519, with the entity reference in the `refs` form, and it leaves the drift guard's exclusion list. Whether the object keeps `computed_at` was left to the specification slice | [2026-11-14](https://github.com/yes-404/gi-pricing-plan/issues/1810#issuecomment-6881063079), "Decided by the maintainer, 2026-11-14: option B" | Slice 2: the generated contract replaces the file, and `backend/tests/test_contracts.py` stops excluding it. Slice 1 settles `computed_at` (below) |
| #1868 | What does the `refs`-form entity reference name, when none of the ten shapes is an `ArtifactRef` type? | **(a)**: the shape's own identity (`entity_type`, and `entity_id` as a UUID) plus `subject_refs`, the governed artifacts it is about, each in the `refs` form. Conditions: `subject_refs` is never empty for a shape with a governed parent; the order of two or more references is stated per shape and tested; the requirement says both kinds of identity in words | [2026-11-15](https://github.com/yes-404/gi-pricing-plan/issues/1868#issuecomment-6893365442), "Decided: option (a)" | Slice 1: FR-2159's reference clause, with the order for `ModelComparison` (`summary.model_refs` order), `DislocationRun` (baseline, then candidate) and `RegressionRun` (suite, then rating version). Slice 2: the class, and the tests of both conditions |
| #1869 | With no Job view in the frontend, what does a provenance badge do with the producing Job? | **(a)**: the badge shows the producing Job's id as text, and "not recorded" for a null id. The Work that builds the Jobs view at `/jobs` (`07`) adds the link. #1506's Outcome is read accordingly: "can see which Job produced it" is delivered by #1506; "and open that Job" is delivered when the Jobs view exists | [2026-11-15](https://github.com/yes-404/gi-pricing-plan/issues/1869#issuecomment-6893366755), "Decided: option (a)" | Slice 3: `ProvenanceBadge` and the ten views. Slice 1 states it in FR-2159 |
| #1870 | When is FR-109's finer-level actual-versus-expected computed, given that FR-170 computes diagnostics once at fit time? | **(b)**: at fit time, stored as an optional field on `Diagnostics`, and never computed on read. A model fitted before the change shows "not available" until it is refitted, in those words, never an empty table. `model_schema/diagnostics.py` and `worker/model_handlers.py` are added to #1506's paths, and slice 5 is built after #1510's change to those files (merged as #1882) | [2026-11-15](https://github.com/yes-404/gi-pricing-plan/issues/1870#issuecomment-6893368026), "Decided: option (b)" | Slice 1: `02` FR-109's dated amendment of 2026-11-17 (slice 1), the §5.1 diagnostics read and the new §5.3 row. Slice 4: the pure `pricing-core` function, which is the same under every option. Slice 5: the optional field on `Diagnostics`, the fit handler, the read and the view |
| #1908 | What column does each level of a Grouping chain read, for FR-109's finer-level diagnostics? | **(B)**: each finer level is rebuilt from the deepest grouping's `column` by applying the chain in order up to that level. A level whose column is not in the frame is stored as not available, never as an empty table. Whether a `GROUPING` Factor on a chained grouping follows the chain when it resolves is a question about the scoring path and is not decided | [2026-11-17](https://github.com/yes-404/gi-pricing-plan/issues/1908#issuecomment-6945637204), "Decided, 2026-11-17: option (B)" | Slice 4: the rule in `02` beside FR-109 (its dated amendment of 2026-11-17, slice 4), `groupings.py`, and a test on a chain where the two readings differ. Slice 5 stores and shows it |

**Also settled on #1506 itself, and recorded here because the decisions above depend on them:**

- **The acceptance of 2026-11-17** ([comment](https://github.com/yes-404/gi-pricing-plan/issues/1506#issuecomment-6945235881)) accepted the slice 2 approach as written: read-side subclasses in `model_schema/provenance.py`, each the persisted class plus a `provenance` field, with the persisted classes, their stored rows and every stored hash untouched. It accepted slice 1's text as written: the object omits `computed_at`, because it is composed on every read and nothing in it is an honest source for that value. That answers what #1810 left to slice 1. It added `backend/src/app/api/validation.py` and `frontend/src/api/metrics.ts` to the permitted paths.
- **In-Work question 1, where the finer-level view lives:** a level selector on the existing Diagnostics view plus a `02` §5.3 row that records it, option (b). This was the plan's recommendation, accepted with the plan. Slice 1 adds the row.
- **The ruling of 2026-11-17, 11:36Z, on slice 4** ([comment](https://github.com/yes-404/gi-pricing-plan/issues/1506#issuecomment-6946916523)), on a case #1908 did not name. A row whose raw value the deepest grouping refuses (a null, or an unseen level under `error`, FR-104) is stored as "not available" at that finer level and at every coarser one, and the fit does not fail. Two conditions. (1) The rows stay visible: "not available" is a named row of the finer-level table with its own row count and exposure, so the table's totals equal the fit's. (2) Only the diagnostic chain is lenient: if the refusing grouping is the one the rating Factor itself uses, FR-104's `error` behaviour is unchanged and the fit is refused as today. Enacted by slice 4: its dated amendment beside FR-109, and its tests in `packages/pricing-core/tests/test_groupings.py` and `test_diagnostics.py`. The same ruling notes that #1909 also adds a dated clause beside FR-109; the two do not contradict each other, and whichever pull request merges second keeps both.
- **Decision (B) of 2026-11-17, 15:25Z, on slice 5** ([comment 6952446272](https://github.com/yes-404/gi-pricing-plan/issues/1506#issuecomment-6952446272)), on where the stored field lives:
  - The finer-level actual-versus-expected is one optional top-level field on `Diagnostics`, `finer_level_ae`, holding train and holdout. That is what #1870 (b) says, and it leaves the Backtest's published shape alone.
  - The hand-authored `docs/contracts/schemas/diagnostics.schema.json` gains that one field by hand, under the grant in the same comment, edited under the contract-schema skill with its `invariants` annotation.
  - The proof asked for is twofold. The drift guard is seen red with the class changed and the authored file not, and green with both. `python3 scripts/generate-contracts.py --check` passes at the slice's head.
  - Enacted by slice 5.
- **Decision (c) of 2026-11-17, 15:59Z, on slice 5** ([comment 6953338935](https://github.com/yes-404/gi-pricing-plan/issues/1506#issuecomment-6953338935)), on the surrogate and the three cases:
  - A surrogate's diagnostics compute and store the finer level like any GLM's, and it is read under FR-141.
  - One condition. The view shows a surrogate's finer-level section under the same FR-141 label as the surrogate's other actual-against-expected tables, and a test asserts the label is present on that section. Where the label is rendered once for the whole page and already covers the section, the pull request says so and points to the test that holds it.
  - The view tells three cases apart, with a test for each: a model with no Factor on a chained grouping shows no finer-level section; such a Factor fitted before the change shows "not available"; one fitted after shows the tables.
  - Enacted by slice 5. How the view tells the first two cases apart was not part of (c), and this record does not decide it.

## Options not taken

From each issue:

- **#1519:** (a) no shared object, each view reading the artifact's own `job_id` (each view writes its own provenance block); (c) a persisted `provenance` field on every governed artifact (changes persisted shapes and write paths, needs a migration, and can move a stored hash).
- **#1810:** A, a class matching the hand-authored contract with a UUID-only `entity_id`, which cannot name an artifact addressed as `{type}:{slug}@{version}`; C, retiring the contract, which drops a published contract for a shape API responses carry.
- **#1868:** (b) extending `ARTIFACT_TYPES` with the ten shapes, which have no slug and no version of their own and would change the shared reference contract; (c) a UUID-only reference, the form #1810 set aside.
- **#1869:** (b) a minimal Job route and view built by #1506, outside its paths and ahead of `07`, which owns `/jobs`.
- **#1870:** (a) on read, which breaks FR-170 and answers a long-running action synchronously; (c) a separate Job and artifact, with a new shape, table, migration, route and Job type.
- **#1908:** (A) each level reads its own grouping's `column`, which repeats the raw level and never produces the middle one under the chain test's reading; (C) factor resolution also follows the chain, which changes the rating and scoring path and is not part of a diagnostics slice.
- **The ruling on slice 4:** failing the fit; dropping the refused rows from the finer-level table and saying how many were dropped.
- **In-Work question 1:** (a) a new route, `/models/:slug/diagnostics/finer?version=`.
- **Decision (B):** (A) the field on each partition, which would have added to Backtest's shape a field a backtest never fills.
- **Decision (c):** (a) no finer-level section for a surrogate, which needs §5.3's row amended; (b) distinct wording for a surrogate, which no spec text gives.

## Consequences

**Positive.**

- Every provenance display reads one shape, defined once in `model-schema`, and its contract is generated rather than hand-written, so the drift guard covers it.
- No persisted shape, stored row, migration or stored hash changes for provenance. #1870 (b) moves no stored hash either: `Diagnostics` has no content hash, and an existing row still loads with the optional field absent.
- FR-170 holds: no diagnostic is computed on read.
- No price moves. `resolve_factors` is unchanged, so the expected values the finer-level table compares against are the ones scoring uses.

**Negative.**

- Until the Jobs view exists, an actuary can see which Job produced an artifact but cannot open it from the badge. Half of #1506's Outcome as first written is delivered by another Work.
- The object carries two kinds of identity: `entity_id` is a UUID, not a reference, and the order of `subject_refs` is a per-shape contract that only tests hold.
- The published provenance contract loses `computed_at`, which the hand-authored file declared and nothing emitted.
- A model fitted before slice 5 shows "not available" for the finer level until it is refitted.
- The diagnostic chain is lenient where scoring is not: a value the chain refuses becomes a count in the "not available" row, not an error, so a reader has to read that row to see it.
- `DatasetVersion`, `Model`, `CustomObjective`, `RateTable`, `RateTableVersion` and `RatingVersion` still record no producing Job.
- One record holds six decision issues and the in-Work rulings listed under Decision. A later change to any one of them is a new record that supersedes this one and says which items it keeps.

**Neutral.**

- Whether a `GROUPING` Factor on a chained grouping follows the chain when it resolves is left open by #1908, and is looked at on its own.
- Slice 6 of #1506 (#1796, the lineage graph) depends on none of these decisions.
