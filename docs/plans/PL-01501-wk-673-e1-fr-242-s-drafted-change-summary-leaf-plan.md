---
id: PL-1501
family: plan
kind: leaf
title: WK-673 — WF-699 E1, FR-242's drafted change summary (the drafting limb), over HTTP: leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: planner
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1267, SL-1389, SL-1391, PL-1419, CR-838, PL-818, RL-1263]
---

# PL-1501 — WK-673: WF-699 E1, FR-242's drafted change summary, leaf plan

*(Minted 2026-10-08 as PL-1501 from working id 9564, in the T8 batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

Filed under working id 9564 (this plan) and slice working id 9565 (its `SL-` row under
`### WK-673` in [`../roadmap.md`](../roadmap.md), `draft`), both reserved by the lead in
`~/gi-pricing-plan.local/handover/eta.md` ("5 Oct 17:16:13"). The `tree:` above is the commit
`origin/main` `4d3be141` (its tree object `6ece3a63`). Every line number in this plan was read
at that commit, unless the cite names another ref.

**Ordered by** the maintainer (by delegation), entry "2026-10-05 17:14:54 BST — FD 9572
placement accepted; WK-673 S4/S5/S6, A-1, A-2 and CR-838 DECISIONS (1–8)" in
`~/gi-pricing-plan.local/channel/to-lead.md` (a local channel file, so cited by its header; the
brief that spawned this plan places it "after 17:15 BST", but its header reads 17:14:54), item 4,
verbatim:

> "4. E1 OWNER: its OWN small WK-673 slice beside S5 (it needs only diff_algorithms, the
> rate-table diff and _baseline, all on main; off the critical path). ACCEPTED; the planner cuts
> the row and leaf. "Unowned" is closed."

The same entry's item 8 makes this slice the owner of a correction, verbatim:

> "8. CR-838:40 records FR-242 "delivered" on marker evidence while its DRAFTING limb is unbuilt
> (AlgorithmDiff.summary never drafts): YES, record it, but FOLD it into RL 9668 (#1137,
> unmerged, already `corrects: CR-838`, and `corrects:` is scalar, so a second correcting RL for
> one CR is the wrong shape). A pre-mint edit adds the FR-242 limb with its evidence and cites
> E1's new slice as the owner of the fix."

**So this slice (SL-1502, then a working id) is the owner RL-1504 cites for CR-838's
FR-242 correction.** The evidence is dm-s45's memo
`~/gi-pricing-plan.local/handover/dp-memo-wk673-s4-s5-2026-10-05.md` §"E1 — the owner gap",
re-verified here at `4d3be141` (§"Premises").

### Pre-mint edit, 2026-10-05

Edited 2026-10-05 from 17:36:55 BST (`TZ=Europe/London date`), before this plan's mint, by the
planner, on the ruling of the maintainer (by delegation) in
`~/gi-pricing-plan.local/channel/to-lead.md`, entry "## 2026-10-05 17:34:57 BST — E1 DPs (dm-e1
memo handover/dp-memo-e1-2026-10-05.md): all six ADOPTED as recommended; S1 yes; S2 yes; PL 9578
noted". Its record is RL-1497 (then a working id, filed by dm-e1). Its lines that bear on this plan,
verbatim:

> DP-E1-1 (a): the GET …/change-summary-draft route, read-only, plus T2, one clause on RATING_VERSION_UNPINNED's meaning note (03:967-970). Checked at origin/main: it is raised only in pricing_core (compile.py:547-591, runtime.py:611/659) and has no synchronous route.
> DP-E1-2 (a), DP-E1-3 (a), DP-E1-4 (a) app/platform/change_summary.py.
> DP-E1-5: the shape as proposed, plus structural_diff = None when the baseline has no algorithm_ref (its acceptance case). The names from_ref/to_ref are KEPT; no rename.
> DP-E1-6 (a): S5's submit_for_review WRITES row.change_summary, with a red test. Checked: docs/contracts/schemas/rating-version.schema.json:8 lists change_summary as required and :36 sets minLength 1.
>   THE RESIDUE IS NAMED, NOT FIXED HERE: the schema requires the field on EVERY rating version, but a draft row carries null until submit, so (a) closes it only from submit onward. The RL records this as the F27 schema-vs-code gap that it is, and it is carried by F27's owner. It does not widen E1 or S5.
> S1: YES. DP-E1-6 (a) goes into PL 9590's scope (#1181; submit_for_review is already in its write set; contention unchanged). It is a pre-mint edit and is named in PL 9590's dispatch.
> PL 9564's missing blob_store kwarg: the planner fixes it pre-mint (as at api/models.py:1203).

The recommendations it adopts, with their evidence at `4d3be141`, are dm-e1's memo
`~/gi-pricing-plan.local/handover/dp-memo-e1-2026-10-05.md`. What this edit changed, each
marked in place with a dated note and with the text it replaces struck through, never deleted:

1. **DP-E1-1..5 are ruled** (§"Decision points"): (a), (a), (a), (a), and DP-E1-5 as proposed
   with `structural_diff: None` also when the baseline has no `algorithm_ref` (new Acceptance
   20); `from_ref`/`to_ref` kept.
2. **T2, a second spec text** (Appendix P2): one clause after `RATING_VERSION_UNPINNED`'s
   meaning note (`03:967-970`), found by its last line, which `grep -cF` matches once at
   `4d3be141`. Task 1 applies T1 and T2; new Acceptance 21 checks T2. T1's find string is the
   submit row's opening cells, never the bare submit path, which matches 2 lines (`:177` and
   `:910`). T2 is in the same `03` §5.1 as T1 (the note sits under `### 5.1 REST API`, `:891`,
   with no heading between), so the contention is unchanged.
3. **The `blob_store` fix.** `rate_tables.diff` takes `blob_store: BlobStore` as a required
   keyword (`backend/src/app/platform/rate_tables.py:291-300`). The service takes a
   `blob_store`, and the route takes `blob_store: score_api.BlobStoreDep` as
   `submit_rating_version` does (`backend/src/app/api/models.py:1203`), passing `cache=None`.
4. **Acceptance 12's 409 is this slice's own.** `errors.py:321` is only the code's registry
   entry; the 409 status comes from the `PlatformError("RATING_VERSION_UNPINNED", …,
   status_code=409, …)` this slice raises (`PlatformError.__init__`, `errors.py:425-432`). No
   existing mapping supplies it: today the code is raised only inside pricing-core, in the
   compile Job.
5. **P6 is now owned.** DP-E1-6 (a) is in PL-1499's scope (#1181, `SL-1389`): its
   `submit_for_review` writes `row.change_summary`. This slice still neither reads nor writes
   that field, and Acceptance 14 is unchanged. **The F27 draft residue is F27's, not E1's:**
   the hand-authored `rating-version.schema.json` requires `change_summary` (`:8`, `:36`) on
   every version, while a draft carries null until submit; that is register finding F27's
   schema-vs-code gap (`docs/findings/register.md:69` at `4d3be141`), carried by F27's owner.
6. **Two citations of WF-699 E1 are re-written as links** (Goal and §"Scope"): each wrote the
   padded file id outside a link target, which `scripts/audit-docs.py` check 32 reds (RFC-937
   §1.1 rule 2). The cited place, `:95`, is unchanged.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (each acceptance item is seen red, by its cause, before
> the code that turns it green), `python-package` (the new platform module and the
> `model-schema` shape), `fastapi-service` (Task 3's route), `contract-schema` (the generated
> contract), `spec-change` (Task 1, the ruled text only), `dev-commands` (the two-half gate)
> and `git-hygiene`. Read [`README.md`](README.md)'s unchecked conventions before the first
> step. The executor is spawned from `.claude/roles/executor.md`.

## Goal

A Pricing Actuary asks the platform for a **drafted** change summary for a Rating Version, and
gets one built from the version's diffs against "the previous version" (`03` FR-242, `:139`:
*"It is generated as a draft from the structural and rate-table diffs and edited by the
actuary."*). This is WF-699 E1 ([`:95`](../workflows/WF-00699-approved-models-to-approved-rating-version.md): *"Writes the change summary. It is drafted
automatically from the structural and rate diffs and then edited — the actuary explains *why*,
the platform states *what*."*), as one HTTP beat:

`GET /api/v1/rating-versions/{id}/change-summary-draft` (DP-E1-1 (a)) answers 200 with a
`ChangeSummaryDraft`: the baseline it drafted against, the structural diff, one entry per
pinned rate table whose version differs, and a deterministic `text` that states *what* changed
and leaves *why* and the expected impact to the actuary. The actuary edits the text and sends it
as `change_summary` on the existing submit route, which this slice does not change.

**Architecture.** Three things on main, composed, nothing rebuilt:
- the baseline is `_baseline` (`backend/src/app/platform/rating_versions.py:704-751`): the most
  recently approved other version of the same algorithm, by its `rating_version.approved`
  Audit Event;
- the structural diff is `diff_algorithms` (`packages/model-schema/src/model_schema/rating.py:571`)
  over the two versions' `RatingAlgorithm`s;
- each rate-table diff is `app.platform.rate_tables.diff` (`backend/src/app/platform/rate_tables.py:291`)
  with `against=<the baseline's pinned version number>`, on pins paired by slug
  (`Pins.rate_tables`, `rating.py:65-78`), and with `blob_store=` the route's
  `score_api.BlobStoreDep` and `cache=None` *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* A pair either side of which is `storage: parquet`
  (`diff_needs_job`, `:262-288`) is named and **not** computed (DP-E1-2 (a)).

The drafting is a pure function in a new backend module, `app/platform/change_summary.py`
(DP-E1-4 (a)); the service and the route are thin over it.

## Status

`draft`. ~~Five decision points are open (§"Decision points"); each has a recommendation. A
decision-maker rules them in an RL, which carries the exact `03` §5.1 row text (Appendix P1).~~
*(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* The five decision points are ruled, each as recommended, at 17:34:57 BST; the
RL that records them is RL-1497, carrying T1 (Appendix P1) and T2 (Appendix P2).
The plan moves to `active` only through a separate activation PR, after every activation need
below holds.

### Activation needs, in order

1. **This plan is merged, minted, and made `active` by a dated line.**
2. **The DP ruling is merged and minted**, carrying DP-E1-1..5 and the §5.1 row's exact text
   (RL-1497, then a working id; its texts are T1 and T2, Appendices P1 and P2 *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)*).
   Where the minted text differs from Appendix P1, the minted text governs, and the dispatch
   record names each difference. An unminted ruling is a stop.
3. **The lane is free** under `RL-1263` as amended by RL-1445 (then a working id; #1162, unmerged at
   this plan's tree): every path in §"Write set" classed SERIALISES is not in flight, or the
   maintainer has dated an option that allows the pair. Task 0 Step 3 re-runs the check.
4. **The maintainer's dispatch GO**, and the lead's go in a separate activation PR.

No activation need waits on another slice's output (§"Contention", condition (b)).

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red first"
means the named test was run, and failed **for the stated cause**, before the code that turns it
green existed. A test that fails with the right status but another cause is a plan defect
([`README.md`](README.md) rule 2). The ledger records each red with its failure line as
printed. Test modules: `D` is `backend/tests/test_change_summary_draft.py` (new, pure, no
database); `H` is `backend/tests/test_rating_version_change_summary_route.py` (new, HTTP).

**The pure draft (`D`; `uv run pytest backend/tests/test_change_summary_draft.py -q`)**

1. `test_each_structural_change_is_stated_by_step_id`. An `AlgorithmDiff` with one step added,
   one removed, one field change and one re-pointed table yields a `text` that names each step
   id and each re-pointed table ref, not counts only. Red: `ModuleNotFoundError` for
   `app.platform.change_summary`.
2. `test_each_rate_table_change_is_stated`. One table re-pinned `@3 → @4` with a
   `RateTableDiff(changed_cells=2, max_abs_change_pct=Decimal("12.5"))` yields a line naming the
   slug, both versions, `2` and `12.5`, and the words "unweighted" (no portfolio is joined:
   FR-231's weights are `SL-1391`'s).
3. `test_a_table_pinned_on_one_side_only_is_named` — added and removed, each.
4. `test_no_change_says_so`. Equal algorithms and pins yield the text "No structural change.
   No rate-table change." and empty lists.
5. `test_no_baseline_says_so`. No approved earlier version yields a `text` that says so,
   `baseline: null`, and no diff.
6. `test_the_draft_is_deterministic`. The same inputs, with the steps and pins supplied in
   another order, give a byte-identical `text` (sorted by `step_id` and by slug).
7. `test_a_percentage_is_never_rendered_through_float`. `Decimal("0.1000000000000000055511151231")`
   appears in the `text` exactly as `str()` gives it (a `float` round trip would not).
8. `test_why_and_impact_are_left_to_the_actuary`. The `text` ends with the labels `Why:` and
   `Expected impact:`, each followed by nothing (DP-E1-3 (a)).
9. `test_a_parquet_pair_is_named_pending_not_computed`. An entry marked pending carries no
   `diff` and its line names the diff route to run (DP-E1-2 (a)).

**The route (`H`; `uv run pytest backend/tests/test_rating_version_change_summary_route.py -q`)**

10. `test_wf699_e1_the_draft_is_built_from_the_approved_baseline`. v1 approved (its
    `rating_version.approved` Audit Event written); v2 a draft whose algorithm adds a step and
    re-pins one inline table to a version with changed cells. `GET …/change-summary-draft` on
    v2 answers 200; `baseline` is v1's ref; `structural_diff` equals `diff_algorithms(v1, v2)`;
    the one rate-table entry's `diff` equals `GET /api/v1/rate-tables/{slug}@{v}/diff?against=<v1's>`.
    Red: 404 from the router (no route), not `NOT_FOUND` from the service.
11. `test_the_baseline_is_the_most_recently_approved_not_the_highest_number`. Two approved
    earlier versions, approved out of number order: the later-approved one is the baseline
    (`_baseline`'s rule).
12. `test_a_version_without_an_algorithm_or_pins_is_refused`. 409 `RATING_VERSION_UNPINNED`
    (`errors.py:321`), the detail naming the missing field (DP-E1-1 (a)). *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)*
    `errors.py:321` is the registry entry only: the 409 is the status of this slice's own
    `PlatformError` (`status_code=409`); no existing mapping supplies it.
13. `test_another_workspaces_version_is_404` and `test_rating_read_is_required` (403 without
    `rating:read`).
14. `test_the_route_writes_nothing`. The version row (status, `change_summary`, `evidence`)
    and the Audit Event count are unchanged after the call.
15. `test_a_parquet_table_answers_200_with_the_entry_pending`. No Job is created.

**Contract, spec and gate**

16. `uv run python scripts/generate-contracts.py --check` exits 0 with the route and
    `ChangeSummaryDraft` (by `$ref`) in `docs/contracts/openapi/generated.json`; the response
    is typed, not an open object.
17. `grep -c 'change-summary-draft' docs/specs/03-rating-engine.md` prints ~~`1`~~ `2` (the T1
    row and the T2 clause), and the row is the ruling's text byte for byte (Appendix P1 as
    ruled). *(Pre-mint edit 2026-10-05, 17:42 BST, on RL-1497 (draft #1199 @`82d801c6`), which governs its T1 and T2 over this appendix's proposals.)* It also gains T2's check:
    `grep -cF 'refuses with **409** and this code when the version has no' docs/specs/03-rating-engine.md`
    prints `1`, and the clause is RL-1497's T2 byte for byte (Appendix P2 as ruled).
18. `python3 scripts/audit-docs.py` and `uv run python scripts/req-coverage.py` pass; FR-242 is
    marker-evidenced by at least items 1, 10 and 14.
19. The two-half gate (`dev-commands`) passes once, in a held gate slot.

**Added pre-mint** *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)*

20. (`D`) `test_a_baseline_without_an_algorithm_has_no_structural_diff`. A baseline whose
    `algorithm_ref` is null (a Phase-1b-era approved version; `RatingVersion.algorithm_ref:
    ArtifactRef | None`) yields `structural_diff: null`, the baseline still named in
    `baseline`, and a `text` that says the baseline has no algorithm (DP-E1-5 as ruled). Red:
    `ModuleNotFoundError` for `app.platform.change_summary`, as item 1.
21. *(Pre-mint edit 2026-10-05, 17:42 BST, on RL-1497 (draft #1199 @`82d801c6`), which governs its T1 and T2 over this appendix's proposals.)* Folded into item 17, as RL-1497 places it; kept here, not renumbered:
    ~~`grep -cF 'refuses with **409** and this code when the version has no' docs/specs/03-rating-engine.md`
    prints `1`, and the clause is the ruling's T2 byte for byte (Appendix P2 as ruled), in the
    `RATING_VERSION_UNPINNED` meaning note.~~

## Global Constraints

- **Money is integer minor units, or Decimal in the rating path — never float** (`CLAUDE.md` §7).
  A percentage in the draft is a `Decimal` from `RateTableDiff`, rendered by `str()`.
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2):
  `ChangeSummaryDraft` embeds `ArtifactRef`, `AlgorithmDiff` and `RateTableDiff` by type.
- **Never hand-write an API type in the frontend** (`CLAUDE.md` §3). This slice adds no
  frontend code; the generated client picks the route up on `generate:api`.
- **RFC 9457 problems on every refusal**, published in the route's `responses`
  (`fastapi-service`).
- **The submit route and `submit_for_review` are not touched.** They are `SL-1389`'s write set
  (§"Contention"). *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* DP-E1-6 (a) puts the `row.change_summary` write there, in
  PL-1499; this slice does not depend on it.

## Scope

### Requirement coverage, each id individually

- `03` **FR-242** (`:139`), the drafting limb only: *"generated as a draft from the structural
  and rate-table diffs and edited by the actuary"*. The required limb (the submit check) is on
  main and is not changed.
- `03` **FR-219** (`:88`) is consumed (its diff), not changed.
- `03` **FR-231** (`:122`) is consumed unweighted; its weight limb is `SL-1391`'s.
- WF-699 **E1** ([`:95`](../workflows/WF-00699-approved-models-to-approved-rating-version.md)), as one HTTP beat.

Not in scope: the frontend editing view (`03` §5.3; G2 is a scripted HTTP journey per RL 9623,
working id, #1160); the expected-impact figure (it comes from a Dislocation Run, `SL-1388`'s
artifact, which is a plan dependency DP-E1-3 (b) would create); `RatingVersion.change_summary`
being written at submit (see §"Premises" P6, ~~raised to the lead, not taken~~). *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)*
It is ruled into PL-1499's scope (DP-E1-6 (a), S1). The residue that a `draft` row carries null
while `rating-version.schema.json` requires the field is F27's, not this slice's.

### Premises read at `4d3be141`

- **P1.** The drafting limb is unbuilt. `AlgorithmDiff.summary` (`rating.py:554-568`) returns
  a count string; `git grep -n -E 'diff_algorithms|\.summary\b' 4d3be141 -- backend/src frontend/src`
  prints only `backend/src/app/platform/rating_algorithms.py:163`, which `model_dump()`s the
  diff, and a property is not dumped. No rate-table diff is summarised anywhere.
- **P2.** `_baseline` (`rating_versions.py:704-751`) returns `(row, GoldenQuoteCheck | None)`
  or `None`, keyed on the algorithm's slug and excluding the version itself. It is read, not
  edited.
- **P3.** `rate_tables.diff` (`platform/rate_tables.py:291`) takes `against: str | int`; an
  explicit version number is accepted (`_resolve_baseline`). It opens its own unit of work, so
  the service takes the `Database`, not a session. *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* It also takes `blob_store:
  BlobStore` as a required keyword (`:291-300`), so the service takes one too, from the route.
- **P4.** A table step's `rate_table_ref` must be in `pins.rate_tables` (`compile.py:545-552`),
  so pairing pins by slug covers every table the algorithm reads.
- **P5.** The rating-version routes live in `backend/src/app/api/models.py` (submit `:1188`,
  compile `:1232`); `load_rating_version` (`rating_versions.py:126-150`) gives the
  workspace-scoped 404.
- **P6 (raised, not taken).** `RatingVersion.change_summary` (`rating.py:168`) is never written:
  `git grep -n 'row.change_summary\|\.change_summary =' 4d3be141 -- backend/src` prints only
  reads (`approvals.py:681`, `deployments.py:167`, `rating_versions.py:120`), and
  `create_rating_version` (`:254-262`) does not set it. `submit_for_review` passes the summary to
  `approvals.submit` only (`:327-333`). FR-242's "Rating Versions carry a required change
  summary" therefore lives on the Approval Request, not the version. Writing it at submit would
  edit `submit_for_review`, `SL-1389`'s function. Reported to the lead as evidence for RL-1504's
  FR-242 limb; not in this scope. *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* Ruled: DP-E1-6 (a), in PL-1499.
- **P7.** Over HTTP no route yet sets a version's algorithm or pins (FD-1421, working id; its
  fix is PL-1429, #1140). This slice's tests seed them through the service, as
  `backend/tests/test_rating_version_compile.py` does. G2's journey needs PL-1429 as well; that
  is PL 9629's (#1164) dependency, not this slice's.
- **P8 (added pre-mint, 2026-10-05).** No synchronous route answers 409
  `RATING_VERSION_UNPINNED` today. `git grep -n RATING_VERSION_UNPINNED 4d3be141 -- backend/src`
  prints only the registry, `backend/src/app/errors.py:321`; the code is raised in pricing-core
  (`compile.py:538` `_raise_named`), inside the compile Job. This slice's refusal is a third
  use, which is why T2 extends the meaning note.

### Risks

- **Two baselines in one submission.** `SL-1389` persists a `structural_diff` at submit against
  *the current live version* (FR-257 limb (2)); this draft diffs against *the most recently
  approved* version. They are usually the same and may differ. The draft names its baseline
  in `text` and in `baseline`, so a reader never has to guess.
- **An unedited draft can be submitted.** The required limb refuses only a blank summary
  (FR-352). DP-E1-3 (b) would refuse an unedited one, at the cost of editing the submit path.

## Write set, and its contention (`RL-1263`, RL-1445)

Classes as in `PL-1419` §"Write set" (`docs/process/delivery-process.core.json`
`guards.parallelism.build_slices_across_works.no_shared_files`).

### By file and symbol, at `4d3be141`

| Path | Symbol or region | Change |
|---|---|---|
| `backend/src/app/platform/change_summary.py` | `draft_change_summary(...) -> ChangeSummaryDraft`, pure | new file |
| `backend/src/app/platform/rating_versions.py` | new ~~`draft_change_summary_for(database, *, workspace_id, rating_version_id) -> ChangeSummaryDraft`~~ `draft_change_summary_for(database, *, blob_store, workspace_id, rating_version_id) -> ChangeSummaryDraft` (pre-mint 2026-10-05: `blob_store`), after `_baseline` | added; no existing definition edited |
| `backend/src/app/api/models.py` | new handler `GET /rating-versions/{rating_version_id}/change-summary-draft`, after the submit handler (`:1188-1229`), taking `blob_store: score_api.BlobStoreDep` as `:1203` (pre-mint 2026-10-05) | added |
| `packages/model-schema/src/model_schema/rating.py` | new `ChangeSummaryDraft`, `RateTableChange`, after `RateTableDiff` (`:735-747`) | added classes; no existing class edited |
| `docs/specs/03-rating-engine.md` | §5.1: one row after the submit row (`:910`) (T1); one clause after `RATING_VERSION_UNPINNED`'s meaning note (`:967-970`) (T2, pre-mint 2026-10-05) | the ruled texts |
| `docs/contracts/openapi/generated.json` | regenerated | |
| `backend/tests/test_change_summary_draft.py`, `backend/tests/test_rating_version_change_summary_route.py` | new | Acceptance 1–15 |
| `docs/ledgers/LG-<n>-…md`; `docs/INDEX.md` | added; regenerated | |

**Not written:** `submit_for_review` and the submit handler; `_baseline`;
`platform/rate_tables.py`; `pricing-core`; `model_schema/__init__.py` (`rating.py`'s rate-table
classes are not exported there: `git grep -n "RateTableDiff" 4d3be141 -- packages/model-schema/src/model_schema/__init__.py`
prints nothing); `backend/src/app/errors.py` (`RATING_VERSION_UNPINNED`, `NOT_FOUND` exist);
the frontend.

### Contention

| Path | This slice | Other slice | Shared existing definition? | Class |
|---|---|---|---|---|
| `platform/rating_versions.py` | adds one function | **SL-1389** (PL-1499 #1181, **WK-673**): `submit_for_review` and new private gates; PL-1429 (WK-1178): `create_rating_version`; PL-1471, PL 9610: `_Resolver` | no | **ALLOWED one-sided**, named in the dispatch record with `git diff -U0 origin/main...<branch> -- backend/src/app/platform/rating_versions.py` |
| `model_schema/rating.py` | adds two classes after `RateTableDiff` | **SL-1391** (PL-1419): edits `RateTableDiff` (`:735-747`) and adds `RateTableDiffCell`; SL-1389: `RatingVersionEvidence`; PL-1429, PL 9610, PL-1476 (other classes) | no; **adjacent to SL-1391's edit** | **ALLOWED one-sided**; the second to merge merges main, re-reads `git merge-tree`'s exit code, and re-gates. If SL-1391 merges first, `RateTableChange.diff` carries its two new optional fields with no change here |
| `api/models.py` | adds one handler | PL-1429: the create handler; WK-675 S2 (PL-1476 #1131): `GET /rating-versions/{slug}@{version}` (RL-1473 T2, working id) | no | **ALLOWED one-sided**, named with the same `git diff -U0` check |
| `03` §5.1 | one row after `:910`; T2 after `:970` (pre-mint 2026-10-05: the same section, so no new pair) | **SL-1391**: T10 replaces `:904`, RL-1418 T1 inserts after it; **WK-675 S2**: RL-1473 T2 inserts after `:908`; **PL-1429**: RL-1428 T1 replaces `:908` | yes: one section; nearest hunk two rows away (`:908`) | **SERIALISES** with each by the file rule (`forbidden`: the same spec section). The lanes A/C option (b) of "2026-10-05 13:00:09 BST" names SL-1391 and WK-675 S2 only. **Either** this slice applies its row after those merge, **or** the maintainer dates an option for it. Not this plan's call: raised to the lead |
| `generated.json`, `docs/INDEX.md` | regenerated | every shape-changing slice | — | exempt (generated) |

**Same-Work pairs, RL-1445 condition 2, both ways.**
- **With SL-1389 (S5, PL-1499), which runs beside it:** (a) every shared path is one-sided
  (`rating_versions.py`, `rating.py`: different definitions) or exempt; S5 does not write
  `03` §5.1 (its `03` hunks are FR-224 `:110`, FR-257 `:174` and §4.6). (b) This slice does not
  consume S5's output: it reads `_baseline` and the diffs on main, not S5's `structural_diff`
  evidence or its live-version lookup. S5 does not consume this slice's output: its gates read
  the submitted `change_summary`, which this slice does not change. **They may run at once if
  the dispatch record names both.**
- **With SL-1391 (S7, PL-1419):** (a) `rating.py` one-sided as above; `03` §5.1 SERIALISES
  unless an option is dated. (b) This slice calls `rate_tables.diff` with no portfolio, whose
  existing keyword S7 keeps; it consumes no S7 output, and S7 consumes none of this slice's.
- **With SL-1388 (S4), SL-1390 (S6), SL-1387 (S3), PL-1447, and the FD-1425 slice (SL-1436,
  working id):** no shared path at `4d3be141` beyond the exempt files; no plan dependency.

### Size

Under one executor day: one pure module, one service function, one route, one shape, one spec
row, two test modules and one gate.

## Decision points

For the decision-maker to rule; the planner recommends, it does not pick. *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)*
**Ruled at 17:34:57 BST, all as recommended** (RL-1497, then a working id); each DP below carries
its ruled option, and DP-E1-1 and DP-E1-5 carry the ruling's additions.

- **DP-E1-1: the HTTP shape of the draft.**
  (a) `GET /api/v1/rating-versions/{id}/change-summary-draft`, `rating:read`, read-only,
  nothing stored; 404 `NOT_FOUND` for an unknown or another workspace's id; 409
  `RATING_VERSION_UNPINNED` for a version without `algorithm_ref` or `pins` (the code compile
  already raises for the same state, `compile.py:584-592`). The actuary edits client-side and
  submits through the existing route.
  (b) Draft at compile into `RatingVersion.change_summary`, plus a `PATCH` to edit it, and
  submit reads the stored text when the body omits it: two new write paths, and edits to
  `compile_rating_version` and `submit_for_review` (both other slices' functions).
  (c) Draft inside submit when the body omits `change_summary`: the actuary never edits, which
  FR-242 and E1 both require.
  **Recommendation: (a).** It is the smallest surface that is FR-242 and E1 as written, and it
  writes nothing, so it has no audit or concurrency obligations.
  **Ruled: (a), plus T2** *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)*: one clause on `RATING_VERSION_UNPINNED`'s meaning
  note (`03:967-970`), Appendix P2.
- **DP-E1-2: a rate-table pair with a `storage: parquet` side.**
  (a) The entry is returned with `pending: true`, no `diff`, and the `text` names the diff route
  to run; the call stays 200 and creates no Job.
  (b) 202 with a Job that drafts.
  (c) Compute synchronously anyway.
  **Recommendation: (a).** (c) defeats FR-232's reason for the Job; (b) adds a Job kind for a
  text. Reading the DP3 diff cache instead would call `DiffCache.key`, whose signature SL-1391
  changes, creating a dependency on S7.
  **Ruled: (a)** *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)*.
- **DP-E1-3: why and expected impact.**
  (a) The `text` ends with empty `Why:` and `Expected impact:` labels; the actuary writes them.
  (b) As (a), and submit refuses a summary that still equals the draft (edits `submit_for_review`,
  `SL-1389`'s function, and needs an `03` text).
  (c) Fill expected impact from the latest Dislocation Run (consumes `SL-1388`'s artifact, a
  plan dependency).
  **Recommendation: (a).** E1 says the actuary explains *why*. (b) and (c) can follow as their
  own decisions once S4 and S5 have merged.
  **Ruled: (a)** *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)*.
- **DP-E1-4: where the pure drafting lives.**
  (a) A backend module, `app/platform/change_summary.py`, with no `03` §5.2 entry.
  (b) `pricing-core`, with an `03` §5.2 signature, in the section `SL-1391` also edits (RL-1418
  T3 and T5, before and after the fence at `:1120`), so the two serialise.
  **Recommendation: (a).** The draft is prose over existing diffs, not rating mathematics, and
  (a) keeps the slice out of §5.2.
  **Ruled: (a), `app/platform/change_summary.py`** *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)*.
- **DP-E1-5: the `ChangeSummaryDraft` shape.** Proposed: `baseline: ArtifactRef | None`;
  `structural_diff: AlgorithmDiff | None`; `rate_tables: list[RateTableChange]`, each
  `{slug, from_ref: ArtifactRef | None, to_ref: ArtifactRef | None, diff: RateTableDiff | None,
  pending: bool}`; `text: str`. `frozen=True, extra="forbid"`, as the neighbouring classes.
  **Recommendation: as proposed**, or the ruling's amendment.
  **Ruled: as proposed, plus `structural_diff: None` when the baseline has no
  `algorithm_ref`** (as well as when there is no baseline; the `text` says which), Acceptance
  20. **`from_ref`/`to_ref` are kept; no rename** *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)*.

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** `git fetch origin`; branch from `origin/main`; `uv sync --all-packages`.
- [ ] **Step 2:** Read the minted DP ruling. List every difference from this plan in the ledger.
- [ ] **Step 3:** Re-run the contention check: for each slice in flight, `git diff --name-only
  origin/main...<its branch>`; for `03`, `git diff -U0 origin/main...<branch> --
  docs/specs/03-rating-engine.md` and the hunks' sections. Record each pair's class and
  RL-1445 (a)/(b) for SL-1389.
- [ ] **Step 4:** Re-read every `:line` cite in this plan at the dispatch tree; re-anchor any
  that moved, by symbol.

### Task 1: Spec — the ruled text

- [ ] Apply the ruled §5.1 row (Appendix P1 as ruled) after the submit row, byte for byte, in
  the three- or four-cell form the ruling gives. `python3 scripts/audit-docs.py`.
- [ ] *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* Find T1's anchor with `` grep -cF '| `POST` | `/api/v1/rating-versions/{id}/submit` | Submit for approval;' ``
  (`1` at `4d3be141`), never the bare submit path (`2`). Apply T2 (Appendix P2 as ruled) as
  the line after `` > matching pin list (`rate_tables`, `reference_tables`, `models`) at that exact version. ``
  (`grep -cF` = `1` at `4d3be141`). Acceptance 21.

### Task 2: The shape and the pure draft (Acceptance 1–9)

- [ ] Write `D`'s nine tests ~~;~~ and item 20's (pre-mint 2026-10-05: ten); run; record each red (item 1's `ModuleNotFoundError` first).
- [ ] Add `ChangeSummaryDraft` and `RateTableChange` to `model_schema/rating.py` after
  `RateTableDiff`.
- [ ] Write `app/platform/change_summary.py`: `draft_change_summary(baseline, structural_diff,
  rate_tables) -> ChangeSummaryDraft`. Lines sorted by `step_id` and slug; percentages by
  `str(Decimal)`; the two empty labels last.
- [ ] Green; `uv run ruff check backend/src/app/platform/change_summary.py && uv run mypy`.

### Task 3: The service and the route (Acceptance 10–15)

- [ ] Write `H`'s tests, seeding versions as `test_rating_version_compile.py` does; record each
  red (item 10: the router's 404).
- [ ] Add `draft_change_summary_for` to `rating_versions.py` after `_baseline`: load the version
  (`load_rating_version`), refuse a missing `algorithm_ref`/`pins` with `RATING_VERSION_UNPINNED`,
  call `_baseline`, load both algorithms, `diff_algorithms`, pair `pins.rate_tables` by slug,
  `diff_needs_job` then `rate_tables.diff(..., against=<baseline version number>)` per changed
  pair, and call the pure draft. It writes nothing. *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* It takes `blob_store` and
  calls `rate_tables.diff(..., blob_store=blob_store, cache=None)`; the refusal is
  `PlatformError("RATING_VERSION_UNPINNED", …, status_code=409, detail=<the missing field>)`;
  a baseline with no `algorithm_ref` gives `structural_diff=None` (Acceptance 20).
- [ ] Add the handler in `api/models.py` after the submit handler, `requires(Perm.RATING_READ)`,
  `responses=problems(401, 403, 404, 409, 422)`, `response_model=ChangeSummaryDraft`, with a
  `blob_store: score_api.BlobStoreDep` parameter passed to the service (as `:1203`; pre-mint
  2026-10-05).
- [ ] Green.

### Task 4: Contract, gate and ledger (Acceptance 16–19)

- [ ] `uv run python scripts/generate-contracts.py`; `--check`; `pnpm --dir frontend generate:api`.
- [ ] `uv run python scripts/req-coverage.py`: FR-242 evidenced.
- [ ] The two-half gate once, in a held slot; the ledger records each red, each green, the gate
  table and the tree.

## Hand-off

The ledger names: the dispatch tree; each DP as ruled and each difference from this plan; each
red with its printed line; the gate result with its tree; and, for the lead, P6 (the version's
`change_summary` is never written) if no record has taken it by then. *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* P6 is
taken: DP-E1-6 (a), in PL-1499. The ledger does not report it; the F27 draft residue is F27's.

## Appendix — proposed text (for the ruling to adopt, amend or reject)

### P1 — `03` §5.1, one row inserted immediately after the `…/submit` row (`:910`)

Three-cell form (if RL-1483's, working id, `Permission` column has not landed):

```
| `GET` | `/api/v1/rating-versions/{id}/change-summary-draft` | The drafted change summary (FR-242; WF-699 E1): the structural diff (FR-219) and each re-pinned rate table's diff (FR-231, unweighted) against the most recently approved other version of the same algorithm, and a `text` stating what changed, for the actuary to edit and submit. Writes nothing; a pair with a `storage: parquet` side is named `pending`, not computed. **404** `NOT_FOUND`; **409** `RATING_VERSION_UNPINNED` without an algorithm or pins. **Added <apply date>** (PL-1501, then a working id) |
```

Four-cell form: the same, with `rating:read` as the fourth cell.

**As ruled: RL-1497 T1, which governs** *(Pre-mint edit 2026-10-05, 17:42 BST, on RL-1497 (draft #1199 @`82d801c6`), which governs its T1 and T2 over this appendix's proposals.)* The proposal above is superseded by it; the
ruled text differs in the third cell (`Why:` and `Expected impact:` named, "Requires
`rating:read`." added per `03:899`, "and no Job is created" added) and in its tail. Placement:
immediately after the line that starts `` | `POST` | `/api/v1/rating-versions/{id}/submit` | Submit for approval; ``
(`grep -cF` = 1 at `4d3be141`; the bare path matches 2). Three-cell form:

```
| `GET` | `/api/v1/rating-versions/{id}/change-summary-draft` | The drafted change summary (FR-242; WF-699 E1): the structural diff (FR-219) and each re-pinned rate table's diff (FR-231, unweighted) against the most recently approved other version of the same algorithm, and a `text` stating what changed, with `Why:` and `Expected impact:` left for the actuary to edit before submitting. Requires `rating:read`. Writes nothing; a pair with a `storage: parquet` side is named `pending`, not computed, and no Job is created. **404** `NOT_FOUND`; **409** `RATING_VERSION_UNPINNED` without an algorithm or pins. (**added <E1 date>, RL-1497, FR-242**) |
```

If a `Permission` column has landed in §5.1 when T1 is applied, use the same row with
"Requires `rating:read`. " taken out of the third cell and `rating:read` added as the fourth
cell (RL-1497).

### P2 — `03` §5.1, T2: one clause after `RATING_VERSION_UNPINNED`'s meaning note (`:967-970`)

*(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* DP-E1-1 as ruled, the text from dm-e1's memo. Inserted as the line immediately
after `` > matching pin list (`rate_tables`, `reference_tables`, `models`) at that exact version. ``
(`grep -cF` = `1` at `4d3be141`):

```
> *(Use added <apply date>, PL-1501, then a working id, FR-242):* `GET /api/v1/rating-versions/{id}/change-summary-draft` refuses with **409** and this code when the version has no `algorithm_ref` or no `pins`, because there is nothing to diff.
```

**As ruled: RL-1497 T2, which governs** *(Pre-mint edit 2026-10-05, 17:42 BST, on RL-1497 (draft #1199 @`82d801c6`), which governs its T1 and T2 over this appendix's proposals.)* The proposal above is superseded by it; the
ruled text differs only in its tag (`<E1 date>, RL-1497`, not `<apply date>, PL-1501, working
id`). Placement as above, inside the same blockquote:

```
> *(Use added <E1 date>, RL-1497, FR-242):* `GET /api/v1/rating-versions/{id}/change-summary-draft` refuses with **409** and this code when the version has no `algorithm_ref` or no `pins`, because there is nothing to diff.
```

## Self-review

- Every requirement id is listed singly (FR-242, FR-219, FR-231); no range.
- The acceptance standard is a numbered list of commands, each red by a stated cause.
- Every cite was read at `4d3be141`; cites into unmerged drafts name their PR and branch.
- No ruling, severity, owner or scope is changed here: the owner is item 4's; the §5.1
  contention and P6 are raised to the lead, not decided.
- Nothing is minted: SL-1502 and PL-1501 are working ids.
- *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* Every ruled change is marked in place; no text was deleted. The ruling's
  locators were re-read at `4d3be141` (`rate_tables.py:291-300`, `api/models.py:1203`,
  `errors.py:321` and `:425-432`, `03:967-970`); RL-1497 is cited by working id and kept out
  of `relates:`.
- *(Pre-mint edit 2026-10-05, 17:42 BST, on RL-1497 (draft #1199 @`82d801c6`), which governs its T1 and T2 over this appendix's proposals.)* Appendix P1 and P2 now carry RL-1497's T1 and T2 verbatim, and Acceptance 17
  carries both checks (`2` for the bare grep; T2's `grep -cF` = 1). Where this plan's
  proposals differ from them, the RL's text wins.
