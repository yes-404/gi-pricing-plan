---
id: RL-9757
family: ruling
title: PL 9764 DP-1 to DP-4 decided — a re-seed starts its own seed origin (the spec's "first version" clause and the code's against=seed resolver were both wrong); an unbound lineage takes a seed only through its one same-named key; the seed request and its 201 are generated model-schema shapes
status: draft                  # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-01
owner: decision-maker
tree: 8bd782acbbdde8e3b4195b5a0acb89183b5a0253
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FD-1357, RL-1361, FR-228, FR-229, FR-230, FR-451, ADR-704]
---

# RL 9757 — PL 9764 DP-1 to DP-4 decided: a re-seed starts its own seed origin, an unbound lineage takes a seed only through its one same-named key, and the seed request and its 201 are generated model-schema shapes

## How this was ruled

**Ruled 2026-10-01 10:31 BST at effort `medium`** by the decision-maker session `dm-1357`,
spawned from `.claude/roles/decision-maker.md`. The session printed `CLAUDE_EFFORT=medium`.
A `ps` search for its own command line found no match, so the model and name flags are not
evidenced here beyond the commission. Every stamp in this record is from
`TZ=Europe/London date` on this session's clock.

- **Commission.** The lead, with the maintainer's approval (entry received 10:25 BST,
  2026-10-01, as the lead relayed it; this session did not read the channel entry). Rule
  DP-1 to DP-4 of PL 9764 (working id), the FD-1357 fix leaf plan, against its draft PR
  #1057 at head `205e71e2c39c3d35bb2a25757adb79fca185c807`. DP-5 (a) and DP-6 (a) are the
  lead's and are not re-ruled here.
- **The auditor's F1, relayed by the lead after this session had found the same thing.**
  auditor-1057 found that DP-1's framing was wrong about the code: `against=seed` resolves to
  the **first** seeded version, so the plan's "(a) changes no code" and "(b) defeats FR-230"
  were both false. The lead restated DP-1's real options as (a1), (a2) and (b). DP-1 below
  rules on those options. The planner is correcting PL 9764 for F1 and three other findings.
  The lead says none of those changes alter the questions of DP-2 to DP-4. **This ruling
  cites head `205e71e2`.** When the planner's new head lands, a dated line here names it and
  confirms that each ruling still answers its DP, or amends it.
- **Re-checked against PL 9764 head `62fdc94c9a255d581a9bc7fa2bc6feb20d5e4343`, 2026-10-01
  10:35 BST** (parent `205e71e2`, "audit fixes F1-F4 from auditor-1057 (pre-merge)"). At
  that head the DP-1 row (`:302`) carries options (a1), (a2) and (b), as the lead relayed
  them. DP-1 below rules on those options, and its item 6 answers the row's new diff-cache
  point. The DP-2 (`:303`), DP-3 (`:304`) and DP-4 (`:305`) rows read the same as at
  `205e71e2`. Each ruling below still answers its DP, and none is amended.
- **Evidence tree.** `origin/main` `1dd5e264195677b4a13268b80ac8673c2c027135` (tree
  `8bd782acbbdde8e3b4195b5a0acb89183b5a0253`), re-fetched at 10:31 BST and unchanged. Every
  `file:line` below is at that tree unless marked otherwise.

## Ruled

One record carries all four decision points. Each is ruled below with its evidence.

### DP-1 — `seeded_from` on a re-seed, and what `against=seed` means

#### What each side says (read to the clause)

- **The spec.** `docs/specs/03-rating-engine.md:334-335`, the §4.2 blockquote "Seed lineage
  survives every derivation", says: "`seeded_from` is set only by seed-from-model, on the
  first version of a lineage". FR-230 (`03:121`) says the seed records "the source model
  reference", and "Subsequent manual edits are diffed against that seed".
- **The code, write path.** Platform `seed_from_model`
  (`backend/src/app/platform/rate_tables.py:95-173`) appends the next version when the table
  exists (`:133-150`), and it sets `seeded_from=result.seeded_from` on that version (`:162`).
  So a re-seed records its own model.
- **The code, read path.** `_resolve_baseline` (`:419-460`), `against == "seed"` branch
  (`:433-453`): it takes the **lowest** `version_number` whose `seeded_from` is not null. So
  `against=seed` always answers against the lineage's **first** seed. It has two callers,
  `diff_needs_job` (`:226`) and `diff` (`:269`). The worker passes `against` through
  unchanged (`backend/src/app/worker/rate_table_handlers.py:27`).
- **The test that pins the read path.**
  `backend/tests/test_api_rate_tables.py::test_diff_vs_seed_compares_against_the_origin_not_the_previous_version`
  (`:224-262`). It seeds three different models into one slug and asserts that `@3`
  `against=seed` gives 2 changed cells, "from the origin" (v1).

The code disagrees with itself. Version 3 in that test carries model 3 in `seeded_from`, but
it is diffed against version 1, which came from model 1. The anchor and the baseline name
different models.

#### History (each read with `git show`)

- `4a8729ee` (2026-08-28T12:56:02+01:00, #302, W10-2) shipped seeding, the append, the write
  of `seeded_from` on every seed, and the lowest-version resolver, together.
- `2bb781dd` (2026-08-28T13:54:19+01:00, #306, W10-3) added the §4.2 blockquote, about an
  hour later, from that day's W10 rulings file (DP4). DP4's question was **derived** versions
  only: a bulk operation or an import inherits the baseline's `seeded_from`. Its rationale
  says "a bulk op or import is a manual edit with a recorded mechanism, not a new lineage".
  It does not consider a seed into an existing lineage. The clause "on the first version of a
  lineage" went beyond the question the ruling decided.

#### The options (the lead's restatement)

| | `seeded_from` on a re-seed | `against=seed` on version N | Code change | Verdict |
|---|---|---|---|---|
| (a1) | the re-seed's own model | the lineage's first seed | none; the §4.2 clause is reworded to say that a re-seed records its model but is not a baseline | **refused** |
| (a2) | the re-seed's own model | the seed that created N's `seeded_from` | `_resolve_baseline`'s seed branch only | **ruled** |
| (b) | inherited from the first version | the lineage's first seed | the write path at `:162` | **refused** |

- **(b) is refused.** The re-seeded version's cells come from the new model. Recording the
  first model in its `seeded_from` is false provenance, and FR-230 requires "recording the
  source model reference". The new model would be recorded nowhere on the version.
- **(a1) is refused.** Every version derived from a re-seed would carry one model in
  `seeded_from` and be diffed against another model's cells. FR-230 says edits are "diffed
  against **that** seed", meaning the seed that recorded the source model. Under (a1),
  `seeded_from` and `diff_vs_seed` answer different questions. After a refit, "how far have
  we moved from the technical rate?" would be measured from a technical rate that the table
  has already replaced.
- **(a2) is ruled.** A re-seed is a new technical rate. `seeded_from` names it, and
  `against=seed` measures from it. RL-1361 section A presumes that seeds append ("Seeding
  into an existing table appends its next version … A newer version of the same Factor is
  accepted"), and (a2) gives that append a coherent baseline.

#### Ruled: (a2)

1. **A re-seed records its own source model** in `seeded_from`. This is the current
   behaviour at `platform/rate_tables.py:162`, unchanged.
2. **`against=seed` on version N resolves to the lowest-numbered version of the same table
   whose `seeded_from` equals N's `seeded_from`.** The comparison is equality of the whole
   stored value (`model_ref` and `seeded_at`). Two seeds of the same model therefore stay
   distinct, because `seeded_at` is the time of the seed (`:127`). The FR-234 equality guard
   (`_guard_seed_lineage`, `:577-600`) makes every derived version carry its baseline's value
   exactly, so this is the version that created N's anchor. If N has no `seeded_from`, the
   answer is the existing 404 `RATE_TABLE_MISS` "No seed origin" (`:446-451`). This is a
   change for one case only: a version created before its table's first seed. Today such a
   version resolves to a later seed. It can only be made by direct insert, because a derived
   version of an unseeded baseline carries no seed.
3. **Which side was wrong (`CLAUDE.md` §0).** **The spec was wrong**: the clause "on the
   first version of a lineage" (`03:335`) went beyond the W10 DP4 ruling that introduced it.
   **The code was wrong in one place and right in another.** The write path (`:162`) was
   right. The `against=seed` resolver (`:433-453`) was wrong, and so was the test that pins
   it (`test_api_rate_tables.py:224-262`). Both encode the same reading as the spec clause:
   one seed origin per lineage. This is recorded so the slice's commit does not look like
   one side being fixed to match the other.
4. **What the slice must change** (an obligation on PL 9764; the planner writes the acceptance
   items, and this ruling does not edit the plan):
   - `_resolve_baseline`'s seed branch, as in item 2. It is one function with two callers.
     There is no change to `RateTableDiff`, to the diff computation or to any diff route's
     shape, so this is not FD-1358's ground. The file is already on the plan's write set and
     serialises with WK-673 Slice 7.
   - `test_diff_vs_seed_compares_against_the_origin_not_the_previous_version` keeps its name
     and its assertions (`@3`: 1 changed cell against `previous`, 2 against `seed`). Its
     versions 2 and 3 must be **derived** versions, not re-seeds. Under (a2), a re-seeded v3
     diffed against its own seed gives 0 changed cells.
   - A new red-first test: seed v1 (model A), derive v2, re-seed v3 (model B), derive v4.
     `against=seed` on `@4` resolves to v3 and on `@2` to v1, and v3's `seeded_from` names
     model B. **Red at `1dd5e264`:** `@4` resolves to v1.
   - Every other test that seeds one slug twice and then diffs `against=seed` is found and
     updated. Find them with
     `grep -n '"against": "seed"' backend/tests/test_api_rate_tables.py backend/tests/test_rate_tables_service.py`
     and read each test's seed calls. At `1dd5e264` that grep prints `:258`, `:491` and `:638`
     in the API module and `:556` in the service module (as `against="seed"`, a different
     form, found by `grep -n 'against="seed"'`). Only `:258` re-seeds. The others seed once
     or derive by import.
5. **The spec text is T-A below.** It amends the clause in place with a strike, so that a
   reader sees the correction where the error was.
6. **The diff cache needs no change.** The cache key is computed **after** the baseline is
   resolved, from the content hashes of the current and baseline cells and the portfolio
   identity (`platform/rate_tables.py:283-289`, `cache.key(version_content_hash(current_cells),
   version_content_hash(baseline_cells), portfolio_dataset_version_id)`). A version whose
   seed baseline moves under (a2) hashes a different baseline, so it gets a different key.
   No entry computed before the change can answer it. This answers the cache risk in
   PL 9764's DP-1 row at `62fdc94c`.
7. **The interplay with WK-673 and FD-1358, with owners** (the maintainer's condition on
   (a2)):
   - **WK-673 Slice 7** (owner WK-673, `docs/roadmap.md` `### WK-673`; PL-1267 Slice 7)
     edits `diff` in the same file to take a `portfolio`, and applies RL-1361 T10 to the §5.1
     diff row. (a2) edits `_resolve_baseline` only, a different function. It changes which
     version the seed baseline is. It does not change how a diff is computed or weighted.
     T10's text does not define `against=seed`, so T-A and T10 do not conflict. The two
     slices serialise on `backend/src/app/platform/rate_tables.py` (PL 9764's write set
     already says so), with this slice first under DP-5 (a). Slice 7's own tests that diff
     `against=seed` after a re-seed are written to (a2).
   - **FD-1358** (owner WK-673; its fix is not decided, RL-1361 section F) is the per-cell
     weight in the diff **output** (`RateTableDiff`). (a2) does not touch `RateTableDiff` or
     the weighting. Whatever FD-1358's fix decides, it weights the diff between the resolved
     pair, and (a2) only chooses the pair. This ruling decides nothing for FD-1358.

### DP-2 — a re-seed into a lineage whose current key is not bound to the named Factor

#### Ruled: (a), made total

RL-1361 section A rules only "the slug the lineage's key is bound to". This ruling covers
every other lineage. **A seed into an existing table is accepted only when the table's
current version has exactly one key, and either:**

1. the key's `factor_ref` names the named Factor's slug, at any version (RL-1361 section A);
   or
2. the key has neither `factor_ref` nor `banding_ref`, and its `name` equals the named
   Factor's slug.

**Every other existing table refuses the seed with 422 `VALIDATION_FAILED`.** The detail
names the table slug and the current version's key names. This covers: a one-key table bound
to another Factor's slug (RL-1361's own case), a one-key unbound table with another name, a
one-key table bound by `banding_ref`, and any table with two or more keys, bound or not. The
new version's key is bound by `factor_ref` in both accepted cases.

**Why.** RL-1361 "What it obliges" says that a table seeded before `factor_ref` "must be
re-seeded to be weighted through a Factor". Case 2 lets that re-seed keep its lineage and its
`diff_vs_previous`. Every pre-fix seed has this shape: the old code named each key after its
relativity entry (`packages/pricing-core/src/pricing_core/rate_tables/operations.py:191-194`),
and no seed of two or more factors ever succeeded (FD-1357). Option (b), refusing every
unbound lineage, breaks that re-seed. Option (c), accepting any unbound lineage, lets a
vehicle × area table (FR-228, FR-232) take a one-key seed that silently drops a dimension. A
`banding_ref` key is refused because seeding would replace a declared Banding binding with a
Factor binding. That is a change of meaning, and the caller should make it on a new slug.

**The error code.** `VALIDATION_FAILED` is **not** in `03`'s owned-codes paragraph. The
lead's premise that it is was checked and is false: `grep -c 'VALIDATION_FAILED'` over
`03:810-845` prints 0. It is one of the generic codes "raised by the shared request
machinery rather than owned by one module" (`backend/src/app/errors.py:382-385`,
`_GENERIC_ERROR_CODES`), and `03` §5.1 already uses it (`:781`). RL-1361 T7 uses it for this
same route's 422s. So it is an existing code that the error catalogue knows, and no new
code is needed. The raise follows the existing pattern
(`PlatformError("VALIDATION_FAILED", …, 422, detail)`, `platform/rate_tables.py:454-459`).
DP-6 (a) also relies on this code, through `_map_operation_error` (`:83-92`). The lead
decided that, and it is not re-ruled here.

**The spec text is T-B below.** `T7`'s refusal list (RL-1361, applied byte for byte) covers
case 1's refusal. T-B states the full rule in §4.2, next to the lineage note. T7 is not
amended.

### DP-3 — the typed seed request

#### Ruled: (a)

- **Class.** `SeedFromModelRequest(BaseModel)` in
  `packages/model-schema/src/model_schema/rating.py`, the module that holds `RateTableVersion`
  (`:851`). It is exported from `model_schema/__init__.py`.
- **Config.** `model_config = ConfigDict(frozen=True, extra="forbid")`. This follows the
  request precedent `ScoreCompareRequest` (`model_schema/scoring.py:262-266`) and
  `RateTableKey` (`rating.py:665`).
- **Fields, exactly three**, as T7 states the body (`{"model_ref", "factor", "change_note"}`):
  - `model_ref: ArtifactRef`. `ArtifactRef` accepts the canonical string
    (`model_schema/refs.py:77-79`, `_accept_the_canonical_string`). A `model_validator(mode="after")`
    refuses a type other than `model` with the message
    `model_ref must reference a model artifact`, which is today's wording
    (`backend/src/app/api/rate_tables.py:80-86`).
  - `factor: str`, with `min_length=1`.
  - `change_note: str`. It is stripped, and it is refused when empty after stripping, with
    the message `change_note is required and must be non-empty (FR-229)`, which is today's
    wording (`api/rate_tables.py:88-94`). The stripped value is what is stored, as today
    (`:95`).
- **No `rateable` field.** `_seed_body` never read one, and the route never passes one
  (`api/rate_tables.py:135-144`), so it was always the platform default. Under
  `extra="forbid"` a body carrying it, or any other unknown field, is refused 422 with a
  field error. Today it is silently ignored. The `BREAKING CHANGE:` footer says so.
- **How a refusal arrives.** The route takes `body: SeedFromModelRequest`. FastAPI's
  `RequestValidationError` is answered as RFC 9457 `VALIDATION_FAILED` with field errors
  (`errors.py:456`, `:574`). `_seed_body` is deleted.
- **Spec text: none.** T7's §5.1 row already states the body. RL-1361 T7 was checked
  verbatim: "The body is `{"model_ref", "factor", "change_note"}`; `factor` is required and
  is the Factor's slug". FR-229 (`03:120`) requires the change note. The field-level shape is
  published by the generated contract (DP-4), the one-way seam `CLAUDE.md` §2 names.
  Restating it in `03` would write the shape a second time by hand. The sub-graph request
  shapes were published the same way, with no spec note
  (`scripts/generate-contracts.py`, comment above `"sub-graph-create"`, read at `:151-155`).
  RL-1361's "Whether the body gains a typed `model-schema` shape is not decided by this
  ruling" is decided here.

### DP-4 — where the typed 201 and the request are published

#### The slug registry on main (the maintainer's condition)

Run at `1dd5e264`, the commands and their output, pasted:

```text
$ awk 'NR>=38 && /^}/ && NR>38{exit} NR>=38' scripts/generate-contracts.py | grep -n '^    "'
2:    "job": "Job",
3:    "audit-event": "AuditEvent",
4:    "problem-detail": "ProblemDetail",
5:    "blob-ref": "BlobRef",
6:    "artifact-ref": "ArtifactRef",
7:    "artifact-envelope": "ArtifactEnvelope",
11:    "banding": "Banding",
12:    "grouping": "Grouping",
16:    "diagnostics": "Diagnostics",
17:    "dataset-split": "DatasetSplit",
21:    "model-comparison": "ModelComparison",
28:    "model-spec": "MODEL_SPEC_ADAPTER",
29:    "model": "Model",
33:    "transparency-artifact": "TransparencyArtifact",
41:    "peril-structure": "PerilStructure",
46:    "backtest": "Backtest",
52:    "custom-objective": "CustomObjective",
53:    "objective-certificate": "ObjectiveCertificate",
58:    "objective-usage": "ObjectiveUsage",
64:    "custom-metric": "CustomMetric",
70:    "metric-certificate": "MetricCertificate",
77:    "profile": "Profile",
85:    "validation-rule": "ValidationRule",
93:    "dataset-version": "DatasetVersion",
94:    "validation-report": "ValidationReport",
97:    "oidc-auth-config": "OidcAuthConfig",
101:    "dataset-lineage": "DatasetLineage",
105:    "regression-suite": "RegressionSuite",
108:    "regression-run": "RegressionRun",
112:    "score-comparison": "ScoreComparison",
117:    "sub-graph": "SubGraph",
118:    "sub-graph-create": "SubGraphCreate",
119:    "sub-graph-body": "SubGraphBody",

$ awk 'NR>=69 && /^}/ && NR>69{exit} NR>=69' backend/tests/test_contracts.py | grep -o '^    "[a-z0-9-]*":'
    "backtest":
    "custom-metric":
    "dataset-lineage":
    "dataset-split":
    "model-comparison":
    "score-comparison":
    "sub-graph":
    "sub-graph-create":
    "sub-graph-body":
    "objective-usage":
    "oidc-auth-config":
    "problem-detail":
    "metric-certificate":
    "approval-request":
    "dislocation-run":
    "dossier":
    "gipp-check":
    "monitoring":
    "optimisation-run":
    "rate-table":
    "rating-algorithm":
    "rating-version":
    "scoring":
    "money":
    "provenance":

$ ls docs/contracts/schemas/ | grep -i 'rate\|seed'
rate-table.schema.json
```

(Line numbers in the first block count from `GENERATED_SHAPES`'s opening line, `:38`.)
`GENERATED_SHAPES` has 33 slugs, and neither `rate-table-version` nor
`seed-from-model-request` is among them. `ONE_SIDED_SLUGS` (`backend/tests/test_contracts.py:69`)
declares `rate-table` as "shipped in model-schema, never compared — register F27" (`:92`).
`test_every_one_sided_slug_is_declared` (`:2641-2665`) fails on an undeclared one-sided
slug and on a stale declaration, so each new generated-only slug must be declared.

#### Ruled: (a), for both shapes

- **`GENERATED_SHAPES` gains two entries:** `"rate-table-version": "RateTableVersion"` and
  `"seed-from-model-request": "SeedFromModelRequest"`. The generated files are
  `docs/contracts/schemas/generated/rate-table-version.schema.json` and
  `docs/contracts/schemas/generated/seed-from-model-request.schema.json`, regenerated and
  never hand-edited.
- **`ONE_SIDED_SLUGS` gains two entries.** Their reason strings are code, not spec, and are
  given here so that no executor writes them. `<RL id>` is this ruling's minted id:

  ```text
      "rate-table-version": "first written form of the seed route's 201 (<RL id> DP-4); the authored rate-table contract is F27(c)'s, never compared",
      "seed-from-model-request": "first written form — 03 §5.1 seed row (<RL id> DP-3, FR-230)",
  ```

- **The 201 is typed with `response_model=RateTableVersion`**, and the handler returns the
  `RateTableVersion` instance. This is the typed-201 precedent `sub_graphs.py:42`
  (`response_model=SubGraph`). NFR-502's "no `response_model`" is scoped to "The scoring
  endpoint" (`03:1206`) and does not bind this route. The `$ref` target must be the component
  named exactly `RateTableVersion`. If FastAPI emits a suffixed name (for example
  `RateTableVersion-Output`), the executor stops and reports to the lead. No
  `generated.json` component named `RateTableVersion` exists at `1dd5e264`
  (`grep -o '"#/components/schemas/RateTable[A-Za-z-]*"'` prints only `RateTableDiff`).
- **The authored `docs/contracts/schemas/rate-table.schema.json` is not edited.** It stays
  F27(c)'s, which is deferred with an owner, the create-read-retire audit Work
  (`docs/findings/register.md:69`, CR-1167). The slice's ledger records the new divergence
  (`factor_ref` on the generated side only) for that owner.
- **Why not (b) or (c).** (b) pairs the generated shape with the authored file. That makes
  the comparison walkers reconcile F27's known divergences inside a seeding fix, which is
  F27(c)'s Work. (c) gives no file under `generated/`, which fails the maintainer's rule (ii).

## Spec texts this ruling carries

Placement was read at `origin/main` `1dd5e264`. Each find string was counted with
`grep -cF` over `docs/specs/03-rating-engine.md`, and each prints 1. The placeholders are
`<fix date>`, the date of FD-1357's fix commit written `YYYY-MM-DD`, and `<RL id>`, this
ruling's minted id written `RL-NNNN`. Nothing else in a text is a placeholder.

**T-A — `03` §4.2, the seed-lineage note (DP-1), FD-1357's fix.** Placement:
`docs/specs/03-rating-engine.md:334-335`, the first two lines of the blockquote "Seed lineage
survives every derivation", **replaced**. Replace

```text
> **Seed lineage survives every derivation.** `seeded_from` is set only by
> seed-from-model, on the first version of a lineage; every derived version — manual
```

with

```text
> **Seed lineage survives every derivation.** `seeded_from` is set only by
> seed-from-model, ~~on the first version of a lineage~~ on every version a seed creates:
> the first version of a lineage, or a re-seed appended to it, which records its own
> source model and starts a new seed origin (**amended <fix date>, `<RL id>` DP-1**).
> `against=seed` on a version resolves to its seed origin: the lowest-numbered version of
> the table whose `seeded_from` equals that version's. Every derived version — manual
```

**T-B — `03` §4.2, re-seeding an existing table (DP-2), FD-1357's fix.** Placement: a new
blockquote paragraph **inserted** after the line below, the last line of the same
blockquote (`03:343`), with one blank line before it. The existing blank line before
`### 4.3 \`RatingVersion\`` stays.

```text
> `created_by_import` remain mutually exclusive.
```

```text
> **Re-seeding an existing table (added <fix date>, `<RL id>` DP-2, FR-230).** A seed
> into an existing table is accepted only when its current version has exactly one key,
> and that key either carries a `factor_ref` naming the named Factor's slug, at any
> version, or carries neither `factor_ref` nor `banding_ref` and is named after that slug,
> as every key seeded before `factor_ref` existed is. The new version's key is bound by
> `factor_ref`. Any other existing table refuses the seed with **422**
> `VALIDATION_FAILED`, naming the table and its keys; seed a new table slug instead.
```

T-A and T-B are applied in the slice's one commit, with RL-1361's `[seeding]` texts. T-A
edits lines `:334-335`, and RL-1361's T5 inserts after `:310`. The two do not overlap.

The executor applies each text above byte-for-byte; authorship stays with the decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296 precedent). Any executor wording is a stop.

If a find string is not found exactly once at the activation SHA, that is a stop, reported
to the lead. The executor does not re-word it.

## What it obliges

- **This commit:** this record only. PL 9764 and `03` are not edited.
- **PL 9764 (working id), the planner's file:** DP-1 to DP-4's resolver cells cite this
  record once it is minted. DP-1's options were restated per the auditor's F1 at
  `62fdc94c`; its recommendation becomes (a2). The acceptance items DP-1 item 4 names are added: the resolver change, the rewritten
  test and the new re-seed test. Acceptance 9's text table gains T-A and T-B. Acceptance
  3(e) is widened to DP-2's full refusal set. Acceptance 6 and 7 keep the slug names
  `seed-from-model-request` and `rate-table-version`.
- **The lead:** release working id 9756, which this ruling did not use. One record carries
  all four DPs.

## Acceptance — the violation that must become detectable

- `@N` `against=seed`, after a re-seed, diffs against a seed that is not N's own: the new
  re-seed test is red at `1dd5e264`.
- A seed into a two-key, `banding_ref`-bound or differently named unbound table succeeds:
  route tests for each are red at `1dd5e264` (201).
- A seed body with an unknown field, or without `factor`, is accepted: red at `1dd5e264`
  (201).
- The seed route's `requestBody` or 201 is an open object in `generated.json`: red at
  `1dd5e264`.

## Amendment 2026-10-01 10:43 BST — auditor-1065's F1 to F4, adopted by the lead

auditor-1065 audited this record at `cb3f9705`. The lead adopted F1 to F4 and asked for
them as one dated amendment. Nothing above is edited. Where this section and a clause
above differ, this section governs. F5 (RL-1361 T7's `:783` locator, now `:786`) goes to
the dispatch record, not here.

**Re-checked at `origin/main` `92b4e4ac155536f80a5be183ad21be88cc92868f`, 2026-10-01
10:43 BST (F4).** `git diff --stat 1dd5e264 92b4e4ac -- docs/specs backend packages scripts tests`
prints nothing. No file that this record cites under those paths has moved, and every
`file:line` above still holds.

**F1 (MED), adopted: DP-4 also registers the two generated files with F83.** DP-4's ruled
(a) gains two edits, made in the slice's one commit. Each was read at `92b4e4ac`.
`scripts/audit-docs.py`'s `_CONTRACT_ARTIFACT_PATHS` (`:2620`) lists each generated schema
by literal path. Without the entries, checks 30 and 35 fail on the new files. The auditor
showed this with a dummy `rate-table-version.schema.json`, following the PL-1325 precedent
(67 → 70). `<fix date>` and `<RL id>` are as defined in *Spec texts this ruling carries*.

1. `scripts/audit-docs.py`: three lines **inserted** after the line below (`:2667`; it
   occurs exactly once), before
   `    "docs/contracts/schemas/generated/problem-detail.schema.json",`.

   ```text
       "docs/contracts/schemas/generated/sub-graph-body.schema.json",
   ```

   ```text
       # <fix date>, FD-1357 fix (<RL id> DP-4)
       "docs/contracts/schemas/generated/rate-table-version.schema.json",
       "docs/contracts/schemas/generated/seed-from-model-request.schema.json",
   ```

2. `tests/test_audit_docs_ids.py` (`:2117`): the line below is **replaced**.

   ```text
       assert len(non_markdown) == 70, len(non_markdown)
   ```

   It is replaced with:

   ```text
       # 70 became 72 (WK-1178, FD-1357 fix, <fix date>): the generated
       # `rate-table-version` and `seed-from-model-request` schemas, registered for F83's reason.
       assert len(non_markdown) == 72, len(non_markdown)
   ```

   If the count on the slice's base is not 70, because another slice registered files
   first, the executor stops and reports to the lead. The executor does not re-count.

The lead proposed the comment date "2026-10-01". The text uses `<fix date>` instead. Each
precedent comment carries the date of the slice that registers the files, and the fix may
land later.

*What it obliges* gains: PL 9764's write set and Acceptance 7 add `scripts/audit-docs.py`
and `tests/test_audit_docs_ids.py`. Its acceptance gains "checks 30 and 35 are green with
both generated files present". Red before the edit: both checks fail on the new files.

**F2 (LOW), adopted: T-A's count predicate.** T-A's first find line also appears unchanged
in its replacement, so a line-based count of that line stays 1. The predicates for
Acceptance 9 are, each `grep -cF` over `docs/specs/03-rating-engine.md`:

- find, before 1 and after 0:
  `> seed-from-model, on the first version of a lineage; every derived version — manual`
- replacement, before 0 and after 1:
  `> \`against=seed\` on a version resolves to its seed origin: the lowest-numbered version of`

T-B is an insert. Its anchor `> \`created_by_import\` remain mutually exclusive.` stays at
1, and its replacement predicate (before 0, after 1) is
`> **Re-seeding an existing table (added <fix date>, \`<RL id>\` DP-2, FR-230).** A seed`,
with both placeholders filled.

**F3 (LOW), adopted: DP-1 item 4's account of `:491` was wrong.** Item 4 says the tests
other than `:258` "seed once or derive by import". `:491` does neither. It belongs to
`test_diff_seed_without_a_seed_origin_404s` (`test_api_rate_tables.py:441-495`), which
inserts an unseeded v1 directly and expects 404 `RATE_TABLE_MISS` "No seed origin". (a2)
keeps that answer: v1 has no `seeded_from`, so DP-1 item 2's no-anchor case applies, and the
test is unchanged. `:638` seeds once, and the service module's `:556` derives by import.
Only `:258` re-seeds.

## Amendment 2026-10-01 10:45 BST — F1's count edit follows the merged count (the lead, on the maintainer's serialisation rule)

The maintainer's serialisation rule says that whichever of the FD-1357 fix and WK-674 S2
(PL 9765, working id, which adds about ten generated schemas) merges second re-bumps on
the merged count and re-gates. The first amendment's F1 item 2 conflicts with that rule.
It fixes `== 70` → `== 72` and stops on any other base count, so it would stop on a
sanctioned state. **F1 item 2 is superseded by the text below.** F1 item 1 (the three
`_CONTRACT_ARTIFACT_PATHS` lines) is unchanged. Its anchor line
`    "docs/contracts/schemas/generated/sub-graph-body.schema.json",` must still occur exactly
once. The three lines are inserted after it, even when another slice's lines already
follow it.

**F1 item 2, as amended.** In `tests/test_audit_docs_ids.py`,
`test_widening_the_scope_roots_reaches_every_non_markdown_file_the_register_exempts`
(`:2072`; the assert is at `:2117` at `92b4e4ac`), the line below is **replaced**.
`N` is the integer in that assert on the slice's base. It is 70 at `92b4e4ac`, and it is a
measured figure that the executor records in the ledger with the base SHA.

```text
    assert len(non_markdown) == N, len(non_markdown)
```

It is replaced with the following. `N+2` is written as the computed integer, and
`<fix date>` is filled as before.

```text
    # N became N+2 (WK-1178, FD-1357 fix, <fix date>): the generated
    # `rate-table-version` and `seed-from-model-request` schemas, registered for F83's reason.
    assert len(non_markdown) == N+2, len(non_markdown)
```

**When it stops.** A base `N` other than 70 is expected if WK-674 S2 merged first, and it
is **not** a stop. The executor stops and reports to the lead only if `N` disagrees with the
registered set's actual length at the base. The check is that this test, run unmodified on
the base, fails:
`uv run pytest -q "tests/test_audit_docs_ids.py::test_widening_the_scope_roots_reaches_every_non_markdown_file_the_register_exempts"`.
The executor quotes the base run's exit code with the base SHA. After the edit, the same
test passes on the slice's tree. If the slice merges second, it re-bumps on the merged count
and re-gates, per the maintainer's rule.

## Amendment 2026-10-01 10:47 BST — auditor-rc2's two LOW findings, adopted by the lead

**LOW-a: F2's predicates, in a form grep can use.** In the first amendment's F2, the
backslashes inside the inline code spans are literal, so copying them into `grep -cF`
counts 0. Those predicates are superseded by the four below, one per fenced block, exactly
as `grep -cF` must receive them. Each is counted over `docs/specs/03-rating-engine.md`.

T-A find (1 before, 0 after):

```text
> seed-from-model, on the first version of a lineage; every derived version — manual
```

T-A replacement (0 before, 1 after):

```text
> `against=seed` on a version resolves to its seed origin: the lowest-numbered version of
```

T-B anchor (1 before, 1 after; T-B is an insert):

```text
> `created_by_import` remain mutually exclusive.
```

T-B replacement (0 before, 1 after). Fill `<fix date>` and `<RL id>` before counting:

```text
> **Re-seeding an existing table (added <fix date>, `<RL id>` DP-2, FR-230).** A seed
```

**LOW-b: the stop condition, stated plainly.** In the 10:45 amendment, the sentence "The
check is that this test, run unmodified on the base, fails" is superseded by this one.
The executor stops and reports to the lead if the unmodified
`test_widening_the_scope_roots_reaches_every_non_markdown_file_the_register_exempts`
**fails** on the base. On a consistent base it passes, and the executor then proceeds with
`N` read from its assert, whatever `N` is.
