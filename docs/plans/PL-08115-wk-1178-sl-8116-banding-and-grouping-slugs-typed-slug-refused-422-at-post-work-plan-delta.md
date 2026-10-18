---
id: PL-8115
family: plan
kind: map
title: WK-1178 — SL-8116, Banding and Grouping slugs typed `Slug` and a bad slug refused 422 at POST (FD 8102's close) — a dated Work-plan delta
status: active                 # draft → active → superseded | retired (§1.2a) — activated 2026-10-18 on the maintainer's GO; DP-1 / DP-2 ruled
created: 2026-10-18
owner: planner
tree: 8ac6290b63a27a3161f447259bf58d215e6e5837
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-8116, FR-101, FR-108, FR-98, FR-105, FR-451, FD-1384, RL-1383, SL-1734, SL-1758, PL-1769]
---

# PL 8115 — WK-1178: Banding and Grouping slugs typed `Slug`, refused 422 at POST (SL 8116)

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L5 (`document-ids.md`
> §1.6, PL row). It carries one slice, SL 8116 (roadmap row under WK-1178, `draft`). The
> executor is spawned from `.claude/roles/executor.md` and binds `test-driven-development`,
> `python-test`, `spec-change`, `contract-guard`, `dev-commands` and `git-hygiene`. Its
> ledger is **LG 8117**, filed by the executor at build; this plan names it and does not
> create it.

Written 2026-10-18 04:55 BST by the planner (planner-8115) on the lead's brief
`brief-planner-8115-2026-10-18.md`. Evidence read at `origin/main` `8ac6290b` unless a line
names another tree. Working ids PL 8115, SL 8116 and LG 8117 are the lead's (`eta.md`,
2026-10-18 04:31:43 BST). FD 8102 is filed in D21 (`origin/docs-d21-2026-10-17` `0c38c276`,
unminted); this plan cites it and does not file it.

## The ruling this plan carries out

`~/gi-pricing-plan.local/channel/to-lead.md`, **"2026-10-18 03:02:03 BST — Maintainer: #1331 —
attribution correction ACCEPTED; fix (A) now; FD 8102 carries (C) with a deadline; the
process line ADOPTED"**, item 3, verbatim: *"PRODUCT EXPOSURE (I checked):
model_schema/modelling.py:407 `slug: str` (Banding; Grouping :557 likewise) and `POST
/bandings` (backend/src/app/api/models.py:9) persist a slug as given. So after SL-1734 a user
can persist `driver_age-bands` and then hit a raw ValidationError when fitting a GBM with it:
a user-reachable, opaque failure on a core path. It is loud, not a mispricing, and nothing is
released yet. FD 8102 (in D21) gets this as its 2nd symptom and (C) as its CLOSE:
Banding.slug and Grouping.slug typed `Slug` in model_schema, refused 422 at POST with a typed
code, contracts regenerated, a red-first test at the API. Severity MEDIUM (loud, no
mispricing); owner WK-1178; due BEFORE the P2 code freeze (Wed 4 Nov), not deferred. Its fix
slice gets its own GO."*

The "(C)" there is the ruling's own label for the fix it then defines. It is **not** FD 8102's
option (c) ("Both"): FD 8102's options are (a) validate at creation, (b) name the offender in
the compile failure, (c) both. The ruled close is FD 8102's option (a). DP-2 asks what
happens to limb 2.

## Goal

A Banding or Grouping slug that the `banding` / `grouping` grammar does not admit is refused
at every write route, with 422 and a field-level code, so no stored artifact can later fail
`ArtifactRef` construction.

## Premises (each read at `8ac6290b`)

- **P1. The two fields are untyped.** `packages/model-schema/src/model_schema/modelling.py:407`
  `slug: str` (class `Banding`, :391) and `:557` `slug: str` (class `Grouping`, :546). `Slug`
  is already imported at `:35` and used at `:1069`.
- **P2. The grammar.** `packages/model-schema/src/model_schema/refs.py:38`
  `_SLUG = r"[a-z0-9][a-z0-9-]{1,62}"`; `:62` `Slug = Annotated[str,
  Field(pattern=rf"^{_SLUG}$")]`. `:56` `slug_is_admitted` gives `_FACTOR_SLUG` (`:42`, which
  admits `_`) to `factor` only. `banding` and `grouping` are in `ARTIFACT_TYPES` and are not
  `factor`, so their grammar is `_SLUG`.
- **P3. The spec already states the grammar.** `docs/specs/00-overview.md` §4.2 ID-3 (line
  290): *"For every other type the slug is `[a-z0-9][a-z0-9-]{1,62}`, the `slug` pattern of
  §4.3"*, and *"A reference whose slug its type's pattern does not admit is refused, whether it
  is parsed from the string or built from its fields."* §4.3 (line 303): the envelope's
  `"slug": "string, ^[a-z0-9][a-z0-9-]{1,62}$"`, on *"Every persisted entity"*. So the code
  disagrees with the spec, and the spec is right (the 03:02:03 ruling says so). What the spec
  does **not** state is the refusal's code at these routes: `02-modelling.md` §5.1 lines 1829
  and 1833 say only "**201** Persist a Banding" / "**201** Persist a Grouping".
- **P4. The four write routes** (`backend/src/app/api/models.py`): `POST /bandings` (:383,
  `body: Banding`), `POST /groupings` (:473, `body: Grouping`), `POST /bandings/propose`
  (:329, `body: BandingProposalRequest`) and `POST /groupings/propose` (`body:
  GroupingProposalRequest`). The two request types are at `:242` and `:253`, each with
  `slug: str`. `propose_banding` passes `body.slug` (`:352`) through
  `platform/transformations.py:91` into `pricing_core.modelling.bandings` (`:74`
  `slug: str`), which builds a `Banding`. **Consequence:** if only `Banding.slug` is typed,
  a bad slug at `/bandings/propose` raises a pydantic `ValidationError` inside the service.
  No handler maps that (`backend/src/app/errors.py:636-640`: `PlatformError`,
  `RequestValidationError`, `StarletteHTTPException`, `DBAPIError`, `Exception`), so it
  becomes a 500. The two proposal request types are in scope for that reason. `POST
  /bandings/evaluate` and `/groupings/evaluate` take `BandingEvaluation.banding: Banding` /
  `GroupingEvaluation.grouping: Grouping` (`modelling.py:697`, `:709`), so the type change
  covers them.
- **P5. The typed code.** `backend/src/app/errors.py:518` `_handle_validation_error` answers a
  `RequestValidationError` with 422, `code = "VALIDATION_FAILED"`, and one `errors[]` item per
  pydantic error: `field` from the location without its first segment (`slug`), `code` from
  the pydantic type upper-cased (`string_pattern_mismatch` → `STRING_PATTERN_MISMATCH`).
  `message` is input-free (`_field_error_message`, `:504`; `00` §5.3, NFR-499). The precedent
  for this exact response is `backend/tests/test_api_transformations.py:133`
  `test_an_invalid_banding_is_refused_at_the_edge` (422, `VALIDATION_FAILED`).
- **P6. Reads re-validate.** `backend/src/app/platform/transformations.py:72` `to_banding` and
  `:78` `to_grouping` call `Banding.model_validate` / `Grouping.model_validate` on the stored
  `row.body`. After the type change, a stored row whose slug the grammar refuses fails on
  **every read** (`GET /bandings`, `GET /groupings`, and each fit or compile that loads it),
  through `_handle_unexpected`. That is DP-1's stake. The table columns are
  `backend/src/app/db/models.py:1351` `bandings.slug` and `:1379` `groupings`, with `body`
  as JSONB. PL-1769 (at `8ac6290b`, `status: draft`) marks both `append_only` (its rows 7 and
  21).
- **P7. In-repo constructions with `_`.** These are the sites that become red when the type
  lands, found by `git -C <wt> grep -n -E "slug[\"']?\s*[:=]\s*[f]?[\"'][a-z0-9-]*_[a-z0-9_-]*[\"']|slug=f\""`
  over the files that `git grep -l -E "Banding\(|Grouping\(|/bandings|/groupings" -- backend
  packages examples frontend/src scripts` lists. That grep finds candidates, and each one
  needs a read. One Banding site is a certain red:
  `backend/tests/test_fremtpl2_algorithm.py:54` `slug=f"{column}-banding"` with `column` =
  `"driv_age"` / `"veh_age"` (`:91`, `:114`). Others are Factor slugs (`_` is admitted; not in
  scope), for example `test_rate_table_diff_portfolio.py:298` and `test_glm.py:224`.
  `test_rating_gbm_banded_refusal.py:60` already replaces `_` (the 03:02:03 fix (A)).
  `examples/fremtpl2/model.py:251` and `FactorWorkbenchView.vue:143` `slugFor` already
  replace `_`. Task 2 makes the census complete.
- **P8. The contracts.** `docs/contracts/schemas/generated/banding.schema.json`,
  `.../grouping.schema.json` and `docs/contracts/openapi/generated.json` are generated
  (`scripts/generate-contracts.py`, FR-451). The hand-authored `docs/contracts/schemas/banding.schema.json`
  and `grouping.schema.json` have no `slug` line (`git grep -c slug` rc 1). So the executor
  reads `.claude/skills/contract-guard` before saying whether the guard compares the new
  `pattern`. The frontend client is generated (`pnpm --dir frontend generate:api`) and
  VCS-ignored. A `pattern` does not change a TypeScript `string`.
- **P9. `check_banding`.** `packages/pricing-core/src/pricing_core/modelling/bandings.py:590`
  `ArtifactRef(type="banding", slug=banding.slug, …)`. When P1 is typed, a `Banding` that
  reaches this line already has a grammar-valid slug. The slice does not change this line.

## Scope

1. **Spec first** (`.claude/skills/spec-change`). Add a dated amendment to the `02-modelling.md` §5.1 rows
   `POST /api/v1/bandings`, `POST /api/v1/groupings`, `POST /api/v1/bandings/propose` and
   `POST /api/v1/groupings/propose`: *"A `slug` that `00` §4.2 ID-3 / §4.3's pattern does not admit is refused
   422 `VALIDATION_FAILED`, `errors[].field` `slug`, `errors[].code`
   `STRING_PATTERN_MISMATCH` (FD 8102 (filed in D21); to-lead 2026-10-18 03:02:03 BST item
   3)."* This adds no new requirement id. The rule is ID-3's. The amendment names the code
   where `00` §5.3 says each spec enumerates its codes.
2. **Type the fields.** `Banding.slug: Slug`, `Grouping.slug: Slug`,
   `BandingProposalRequest.slug: Slug`, `GroupingProposalRequest.slug: Slug`. No new type
   and no validator: `Slug` exists (P2).
3. **Fix the fixtures that P7's census finds.** Change only the slug literal, with
   `.replace("_", "-")` as in the 03:02:03 fix (A). Keep every assert. A Factor slug is
   not touched.
4. **Regenerate the contracts** (`uv run python scripts/generate-contracts.py`). Never
   hand-edit them (`CLAUDE.md` §2).
5. **Red-first API tests**, in `backend/tests/test_api_transformations.py`, one per route in
   item 1. Each one posts a body that is otherwise valid, with slug `driver_age-bands` (the
   ruling's own example) for the bandings routes and `vehicle_group-groups` for the groupings
   routes. Each one asserts 422, `code == "VALIDATION_FAILED"`, an `errors[]` item with `field
   == "slug"` and `code == "STRING_PATTERN_MISMATCH"`, and that the message does not contain
   the submitted slug (NFR-499). The two persist tests also assert that a following `GET` with
   that `dataset_id` returns no row with that slug. Markers: `req("FR-101")` and
   `req("FR-108")` for the persist routes, `req("FR-98")` and `req("FR-105")` for propose.
6. **Out of scope:** `Factor.slug` (FD-1384; RL-1383 grammar), `validation_rule_set` and the
   `model` family slug fields (FD 8102's "not verified" rows). Also out: the compile-error
   naming (FD 8102 option (b); DP-2) and `bandings.py:590` (P9).

## Decision points

**DP-1. An already-stored bad slug (P6).** After the type lands, each such row fails every read
with a 500. The maintainer decides.

| Option | What | For | Against |
|---|---|---|---|
| **(a)** No migration. A read-only census first (Task 0). Zero on every database is the evidence that nothing is stranded. | Census only | Simplest. Nothing is released (03:02:03). Adds no migration to the chain. | If a later database has a bad row, it fails at read time with an opaque 500. Only the census guards against that. |
| **(b)** An Alembic **guard** revision. It counts the rows in `bandings` and `groupings` whose `slug` or `body->>'slug'` fails `^[a-z0-9][a-z0-9-]{1,62}$`. If the count is not zero, it aborts `upgrade` with a message that names the tables and the count, and no values. It writes no data. | Loud at deploy | Deploy fails loudly and early, with the cause named. It does not touch the append-only rows (PL-1769). | One more revision and its test. A dev database with test data cannot upgrade until someone removes those rows. |
| **(c)** A rewrite migration, `_` → `-`. | Data change | Stored rows keep working. | It edits rows that PL-1769 makes append-only. It breaks every `ArtifactRef` and Model pin that names the old slug. The new slug can collide with an existing one (FR-101 versioning). **Not recommended.** |
| **(d)** A lenient read type for stored rows. | Two shapes | No data change. | It defines one shape twice (`CLAUDE.md` §2: *"a diverged shape is a mispricing"*). The bad slug still fails at `ArtifactRef`. **Not recommended.** |

**Ruled — dated 2026-10-18, on the maintainer, to-lead 2026-10-18 04:42:19 BST (GO; DP-1 (a) with Task 0 in two limbs, (c)/(d) refused; DP-2 (i), the named compile error stays FD 8102's residue, WK-1178, due before the P2 close; the WF-699 demo must pass in this slice's gate): DP-1 is (a), no migration, after a read-only census with Task 0 in two limbs: (1) the SQL census of stored banding and grouping slugs on the dev database `gipricing`; (2) a CODE census of every place that builds a Banding or Grouping slug, test fixtures included. Any non-conforming fixture is fixed test-only in this slice, asserts unchanged. If limb (1) is non-zero, the executor STOPS and (b) becomes the DP. (c) and (d) are refused.**

**Recommendation: (a), with (b) as the fallback when the census is not zero.** The census
query is in Task 0. It is read-only, and the lead must grant it (DB lane, common brief item
12). If every database reads 0, the slice lands with no migration, and LG 8117 quotes the
census. If any database reads more than 0, the executor STOPS, and DP-1 returns to the
maintainer with the counts. With counts in hand, (b) is the recommended remedy.

**DP-2. FD 8102's limb 2 (the opaque compile error).** FD 8102 has two limbs: limb 1 is the
missing boundary check, and limb 2 is that `rating.compile` names no artifact
(`_carry_glm_inputs`). The ruled close fixes limb 1 only.

- **(i)** SL 8116 closes limb 1 only. FD 8102 stays `active` with limb 2 named as its
  residue (owner WK-1178), or the maintainer accepts that limb 2 is absent with a dated line.
  **Recommended.** It is the ruled scope, and after this slice no write route can produce the
  limb-2 input for banding or grouping.
- **Ruled — dated 2026-10-18, on the maintainer, to-lead 2026-10-18 04:42:19 BST (GO; DP-1 (a) with Task 0 in two limbs, (c)/(d) refused; DP-2 (i), the named compile error stays FD 8102's residue, WK-1178, due before the P2 close; the WF-699 demo must pass in this slice's gate): DP-2 is (i).** The named compile error stays FD 8102's second limb as a named residue, owner WK-1178, due before the P2 close (not accepted as absent). The WF-699 demo must pass in this slice's gate.
- **(ii)** Add FD 8102 option (b) to SL 8116: a named, input-free compile error that carries
  the artifact type and pin. This is wider: it touches the rating path and needs its own
  red-first test.

## Acceptance Standard

1. **Census (DP-1).** LG 8117 quotes Task 0's output for each database the lead names, with
   its tree. Zero is required to go on under DP-1 (a).
2. **Red first.** The four tests of Scope item 5 (one per route; the persist pair adds the `GET`
   assert) are committed **before** Scope items 2-3. On that commit, `bash
   ~/gi-pricing-plan.local/handover/run-small.sh backend/tests/test_api_transformations.py`
   shows the four refusal tests FAILED: 201 or 200 where 422 is expected for the persist and
   propose routes. LG 8117 quotes the FAILED lines and the tree. A red for any other cause is
   a test defect.
3. **Green.** At the slice head, the same run passes the whole file. P7's fixed files and
   `packages/pricing-core/tests/test_rating_gbm_banded_refusal.py` each pass through run-small
   (item 21 of the common brief: the test files that import `model_schema.modelling`'s
   `Banding` / `Grouping` and that the census names).
4. **Census completeness.** At the slice head,
   `git -C <wt> grep -n -E "slug[\"']?\s*[:=]\s*[f]?[\"'][a-z0-9-]*_[a-z0-9_-]*[\"']"` over
   the files of P7's `git grep -l` prints no Banding or Grouping construction. LG 8117 lists
   every remaining hit as a Factor or another type.
5. **Contracts.** `uv run python scripts/generate-contracts.py --check` rc 0. `git diff
   origin/main -- docs/contracts` shows only the `pattern` added to the four slug properties
   (the Banding and Grouping schemas, and the two proposal request bodies in
   `openapi/generated.json`). LG 8117 lists the keys.
6. **Frontend.** `pnpm --dir <wt>/frontend generate:api` and `pnpm --dir <wt>/frontend
   type-check` rc 0 (the generated client is VCS-ignored).
7. **Spec.** `python3 scripts/audit-docs.py` under the gate-2 flock reds only on the slice's
   working ids, which the lead classes. The four §5.1 rows carry Scope item 1's amendment.
8. **`check_banding`.** `git diff origin/main -- packages/pricing-core/src/pricing_core/modelling/bandings.py`
   is empty (P9).
9. **The gate.** The full two-half gate (`CLAUDE.md` §11), on a free slot when the lead grants
   it. Both halves read against the lead's baseline. `uv run ruff check .` rc 0.

## Tasks

0. **Census (read-only, a lead grant).** Run this on each database the lead names (the shared
   stack's `gi-pricing-postgres-1` databases that hold a `bandings` table):
   `SELECT 'bandings', count(*) FROM bandings WHERE slug !~ '^[a-z0-9][a-z0-9-]{1,62}$' OR
   body->>'slug' !~ '^[a-z0-9][a-z0-9-]{1,62}$' UNION ALL SELECT 'groupings', count(*) FROM
   groupings WHERE slug !~ '^[a-z0-9][a-z0-9-]{1,62}$' OR body->>'slug' !~
   '^[a-z0-9][a-z0-9-]{1,62}$';`. It returns counts only, with no values (NFR-499 spirit).
   Quote the output into LG 8117.
1. **Base.** Branch from the current `origin/main`. Quote the head.
2. **Census of fixtures.** Run P7's two greps and read each hit. List each Banding or Grouping
   site that has `_` in LG 8117.
3. **Spec** (Scope 1). `audit-docs` under the flock.
4. **Red.** Commit Scope 5's tests. Run them. Quote the red (Acceptance 2).
5. **Type + fixtures** (Scope 2-3). Commit.
6. **Contracts** (Scope 4). Commit `docs/contracts/` alone. Run `--check`.
7. **Green + frontend** (Acceptance 3-6). Quote the results into LG 8117.
8. **Gate** (Acceptance 9), when the lead grants it.

## Sequencing

One slice, with no dependency on an open slice. It must merge **before the P2 code freeze,
Wed 4 Nov 2026** (03:02:03 item 3). Task 0 comes before Task 5, because DP-1 (a) rests on the
census. If PL-1769's slice merges first, it does not change this slice. This slice does not
write to `bandings` or `groupings` rows.

## Activation

ACTIVE. *Dated 2026-10-18, on the maintainer, to-lead 2026-10-18 04:42:19 BST (GO; DP-1 (a) with Task 0 in two limbs, (c)/(d) refused; DP-2 (i), the named compile error stays FD 8102's residue, WK-1178, due before the P2 close; the WF-699 demo must pass in this slice's gate):* the one-line GO is given and DP-1 and DP-2 are ruled (below). The
activation commit sets `status: active` here and on the SL 8116 row.

## Self-review before freeze

- Every requirement id in scope is listed by id: FR-101, FR-108, FR-98, FR-105, FR-451, and
  NFR-499 as a constraint. The rule is `00` ID-3 / §4.3, cited by section. No ranges.
- Each premise names its file and line at `8ac6290b`. P7's census predicate is verbatim, and
  the plan does not treat it as complete (Task 2).
- The plan picks no option silently. DP-1 and DP-2 are the maintainer's.
- The plan adds no new type, validator or handler. `Slug` and `_handle_validation_error`
  already exist.
