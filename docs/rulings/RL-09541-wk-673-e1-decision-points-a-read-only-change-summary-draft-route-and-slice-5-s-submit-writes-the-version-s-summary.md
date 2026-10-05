---
id: RL-9541
family: ruling
title: WK-673 E1 decision points, as adopted — the change-summary draft is a read-only GET with one added clause on the RATING_VERSION_UNPINNED note, and Slice 5's submit writes the Rating Version's change summary; the draft-row residue is F27's
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-05            # working id; the mint date is set at the mint (check 31)
owner: decision-maker
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FR-242, FR-219, FR-231, FR-232, FR-237, FD-934, RL-1418, WK-673]
---

# RL 9541 (working id) — WK-673 E1: the decision points of PL 9564, as adopted

## How this was ruled

- **Filed under working id 9541.** The lead reserved it in `handover/eta.md` (the row
  "RL 9541 | RL | dm-e1 (opus)", 2026-10-05 17:35:16). Every working id in this record (RL 9541,
  PL 9564, SL 9565, PL 9590, RL 9620, RL 9668, RL 9766, RL 9695) becomes its minted id at the mint.
- **The decisions are not this record's.** The maintainer made them, by delegation, in the
  entry below (`~/gi-pricing-plan.local/channel/to-lead.md`, `:18237-18248` when it was
  read at 2026-10-05 17:37:48 BST). It is quoted here verbatim:

  > ## 2026-10-05 17:34:57 BST — E1 DPs (dm-e1 memo handover/dp-memo-e1-2026-10-05.md): all six ADOPTED as recommended; S1 yes; S2 yes; PL 9578 noted
  >
  > DP-E1-1 (a): the GET …/change-summary-draft route, read-only, plus T2, one clause on RATING_VERSION_UNPINNED's meaning note (03:967-970). Checked at origin/main: it is raised only in pricing_core (compile.py:547-591, runtime.py:611/659) and has no synchronous route.
  > DP-E1-2 (a), DP-E1-3 (a), DP-E1-4 (a) app/platform/change_summary.py.
  > DP-E1-5: the shape as proposed, plus structural_diff = None when the baseline has no algorithm_ref (its acceptance case). The names from_ref/to_ref are KEPT; no rename.
  > DP-E1-6 (a): S5's submit_for_review WRITES row.change_summary, with a red test. Checked: docs/contracts/schemas/rating-version.schema.json:8 lists change_summary as required and :36 sets minLength 1.
  >   THE RESIDUE IS NAMED, NOT FIXED HERE: the schema requires the field on EVERY rating version, but a draft row carries null until submit, so (a) closes it only from submit onward. The RL records this as the F27 schema-vs-code gap that it is, and it is carried by F27's owner. It does not widen E1 or S5.
  > S1: YES. DP-E1-6 (a) goes into PL 9590's scope (#1181; submit_for_review is already in its write set; contention unchanged). It is a pre-mint edit and is named in PL 9590's dispatch.
  > S2: YES. RL 9668 (#1137) is corrected PRE-MINT in one sentence: only the declaration exists; nothing writes the field; enforcement is on the ApprovalRequest (approvals.py:272-275).
  > PL 9564's missing blob_store kwarg: the planner fixes it pre-mint (as at api/models.py:1203).
  > Then dm-e1 files ONE RL quoting this entry verbatim (reserve its id). A planner folds PL 9564 and PL 9590.
  > PL 9578 #1186 @465971d4: the typing task moved FIRST, and the holds text fixed in 2 places. Good; it matches 17:30:02 item 4 literally.

- **The options and the evidence** are the decision-maker's memo
  `~/gi-pricing-plan.local/handover/dp-memo-e1-2026-10-05.md` (dm-e1, 2026-10-05, finished
  17:31:07 BST). The memo read origin/main `4d3be141` and PL 9564 at #1194 @ `b9e19cdb`. The
  memo is a local file, so its facts that the rulings rest on are restated under "Locators".
- **This record drafts the texts for those decisions and decides nothing beyond them.** A
  detail the entry does not name is taken from main and listed under "Details taken from
  main".

## Locators — read at `4d3be141`

- **`03` FR-242** (`03-rating-engine.md:139`): "Rating Versions carry a required **change
  summary**: what changed versus the previous version, why, and expected impact. It is
  generated as a draft from the structural and rate-table diffs and edited by the actuary."
  The row has no dated amendment.
- **`03` §5.1**, `### 5.1 REST API` at `:891`:
  - The submit row is at `:910`. It is the one line that starts
    `` | `POST` | `/api/v1/rating-versions/{id}/submit` | Submit for approval; `` (`grep -cF` = 1).
    The bare path matches 2 lines (`:177` and `:910`), so the bare path is not a find string.
  - A permission is stated in the Purpose cell, as in the Sub-graph rows (`:899`, "requires
    `rating:read`").
- **The `RATING_VERSION_UNPINNED` meaning note** is at `03:967-970`, inside §5.1 (no heading
  between `:891` and `:967`). It reads "The Rating Version cannot be compiled, or a compiled
  bundle cannot be loaded: it has no `algorithm_ref`, has no `pins`, or …".
  - Today the code is raised only in `pricing_core`, by `_raise_named` in `compile.py`. The
    entry cites `compile.py:547-591` and `runtime.py:611/659`.
  - No synchronous route answers with it. Compile is a **202** Job (§5.1 compile row, `:909`).
  - It is in the code registry at `backend/src/app/errors.py:321`.
- **`RatingVersion.change_summary`** is declared, and nothing writes it:
  - `change_summary: str | None = None` (`packages/model-schema/src/model_schema/rating.py:168`);
    the column is `RatingVersionRow.change_summary` (`backend/src/app/db/models.py:1997`).
  - `create_rating_version` builds the row at `backend/src/app/platform/rating_versions.py:254-262`
    without it.
  - `submit_for_review` (`:278`) passes the summary only to `approvals.submit`
    (`:327-333`). `git grep -n -E 'change_summary\s*=' 4d3be141 -- backend/src/app/platform/rating_versions.py`
    prints `:120` (`to_schema` reads the row) and `:332` (the keyword argument to
    `approvals.submit`), and no assignment.
  - The submit handler `submit_rating_version` (`backend/src/app/api/models.py:1198`) returns
    `rating_versions_service.to_schema(row)` (`:1229`). So the response carries
    `change_summary: null` for the summary the caller has just sent.
  - The blank-summary guard is on the Approval Request (`backend/src/app/platform/approvals.py:272-275`,
    422 `VALIDATION_FAILED` "A change summary is required").
- **The hand-authored contract** `docs/contracts/schemas/rating-version.schema.json` lists
  `change_summary` in `required` (`:8`) and gives it `"minLength": 1` (`:36`). No test compares
  it with `model-schema`: `backend/tests/test_contracts.py:105` reads
  `"rating-version": "shipped in model-schema, never compared — register F27"`.
- **Register finding F27** (`docs/findings/register.md:69`, the row self-naming `(F27)`;
  essay `FD-934`). Its third column, quoted: "deferred with an owner — the create-read-retire
  audit Work, for clause (c) only, 2026-09-27 (`CR-1167`, plan review 14 …)".
- **`rate_tables.diff`** (`backend/src/app/platform/rate_tables.py:291`) takes
  `blob_store: BlobStore` as a required keyword argument. `diff_needs_job` (`:262-288`) is
  true when either side is `storage: parquet`.

## Details taken from main (no new choice)

| Detail | Taken from |
|---|---|
| `rating:read` stated in the Purpose cell | `03:899` (the Sub-graph rows); no permission column at `4d3be141` |
| **404** `NOT_FOUND` for an unknown id or another workspace's | `load_rating_version` (`rating_versions.py:126`) |
| **409** for a version with no `algorithm_ref` or no `pins` | DP-E1-1 (a) as adopted; the code already names that state (`03:967-970`) |
| The baseline: the most recently approved other version of the same algorithm | `_baseline` (`rating_versions.py:704`) |
| A rate-table pair with a `storage: parquet` side is not computed | `diff_needs_job` (`rate_tables.py:262`) and FR-232 |
| `blob_store` passed from the route | `submit_rating_version`'s `blob_store: score_api.BlobStoreDep` (`api/models.py:1203`) |

## Ruled

1. **DP-E1-1 (a).** The draft is `GET /api/v1/rating-versions/{id}/change-summary-draft`. It
   requires `rating:read`, is read-only and stores nothing. The actuary edits the text and
   submits it through the existing submit route, which E1 does not change. The texts are T1
   (the §5.1 row) and T2 (one clause on the `RATING_VERSION_UNPINNED` meaning note).
2. **DP-E1-2 (a).** A rate-table pair with a `storage: parquet` side is returned with
   `pending: true` and no `diff`, and its line in `text` names the diff route to run. The
   call stays 200 and creates no Job.
3. **DP-E1-3 (a).** The `text` ends with the labels `Why:` and `Expected impact:`, each
   followed by nothing. The actuary writes them.
4. **DP-E1-4 (a).** The pure drafting lives in a backend module,
   `backend/src/app/platform/change_summary.py`. It gets no `03` §5.2 entry.
5. **DP-E1-5, as proposed, with one addition.**
   - `ChangeSummaryDraft`: `baseline: ArtifactRef | None`, `structural_diff: AlgorithmDiff | None`,
     `rate_tables: list[RateTableChange]` and `text: str`.
   - Each `RateTableChange` is `{slug, from_ref: ArtifactRef | None, to_ref: ArtifactRef | None,
     diff: RateTableDiff | None, pending: bool}`.
   - Both classes are `frozen=True, extra="forbid"`. **The names `from_ref` and `to_ref` are kept.**
   - **Added:** `structural_diff` is `None` when there is no baseline **and when the baseline
     has no `algorithm_ref`**. In each case the `text` says which, and each case has its own
     acceptance case.
6. **DP-E1-6 (a), and S1.**
   - Slice 5's `submit_for_review` writes `row.change_summary` from the submitted summary,
     with a red test. A submission after a return to `draft` overwrites it, as the evidence
     write at `:322-326` does.
   - **S1:** this goes into PL 9590's scope (#1181) as a pre-mint edit, and PL 9590's
     dispatch record names it. `submit_for_review` is already in that plan's write set, so
     no contention changes.
   - No spec text is needed: FR-242, `03` §4.3 and the hand-authored contract already say
     that the version carries the summary.
7. **The draft-row residue is named, not fixed here.**
   - `rating-version.schema.json` requires a non-empty `change_summary` on **every** Rating
     Version (`:8`, `:36`). A `draft` row carries null until it is submitted, so item 6
     closes the divergence only from submit onward.
   - This is the schema-vs-code gap of register finding **F27** (`FD-934`), the
     `rating-version` contract that nothing compares. It is carried by F27's owner, as the
     register row's third column names it.
   - It widens neither E1 nor Slice 5.
8. **S2.** RL 9668 (#1137) is corrected pre-mint in one sentence: the "field" of FR-242's
   required limb is only declared; nothing writes it; the requirement is enforced on the
   Approval Request (`approvals.py:272-275`). The correction is a dated pre-mint note in
   that record (#1137, head `542762d784019fd5f823322bff9de69e192c3f98`), not in this one.
9. **PL 9564's missing `blob_store`.** The planner fixes it before the mint. The service
   passes a `blob_store` to `rate_tables.diff`, and the route supplies it as
   `submit_rating_version` does (`api/models.py:1203`).

**Already ruled, recorded only** (the maintainer's, by delegation, entry "2026-10-05 17:28:27
BST", `channel/to-lead.md`):
- E1's §5.1 row **serialises**. It is applied after SL-1391, WK-675 S2 (RL 9766) and PL 9683
  (RL 9695) have merged.
- With Slice 5 (PL 9590), RL 9620 condition 2 holds both ways, so the two slices may run
  at the same time if both dispatch records name each other.

## The spec texts

Each item gives the file, the place, who applies it, and the exact bytes. Placement was read
at `origin/main` `4d3be141`.

The placeholders are:
- `<E1 date>`, the date of the E1 slice's commit that applies the item;
- `RL 9541`, this ruling's working id, which the mint replaces with the minted id.

Nothing else in a text is a placeholder. Both texts are applied by the E1 slice (SL 9565,
leaf plan PL 9564), in one commit with the code (`CLAUDE.md` §2). Before applying each text,
re-run its `grep -cF`. If the result is not 1, STOP and report it: do not choose another
anchor.

**T1 — `03` §5.1, the draft route (DP-E1-1, DP-E1-2).**

Placement: a new row **inserted immediately after** the line that starts

```text
| `POST` | `/api/v1/rating-versions/{id}/submit` | Submit for approval;
```

(`grep -cF` = 1 at `4d3be141`).

Insert, in the three-cell form of `4d3be141`:

```text
| `GET` | `/api/v1/rating-versions/{id}/change-summary-draft` | The drafted change summary (FR-242; WF-699 E1): the structural diff (FR-219) and each re-pinned rate table's diff (FR-231, unweighted) against the most recently approved other version of the same algorithm, and a `text` stating what changed, with `Why:` and `Expected impact:` left for the actuary to edit before submitting. Requires `rating:read`. Writes nothing; a pair with a `storage: parquet` side is named `pending`, not computed, and no Job is created. **404** `NOT_FOUND`; **409** `RATING_VERSION_UNPINNED` without an algorithm or pins. (**added <E1 date>, RL 9541, FR-242**) |
```

If a `Permission` column has landed in §5.1 by the time T1 is applied, use the same row with
"Requires `rating:read`. " taken out of the third cell and `rating:read` added as the fourth
cell.

**T2 — `03` §5.1, the `RATING_VERSION_UNPINNED` meaning note (DP-E1-1).**

Placement: **inserted immediately after** the line

```text
> matching pin list (`rate_tables`, `reference_tables`, `models`) at that exact version.
```

(`grep -cF` = 1 at `4d3be141`), inside the same blockquote. Insert

```text
> *(Use added <E1 date>, RL 9541, FR-242):* `GET /api/v1/rating-versions/{id}/change-summary-draft` refuses with **409** and this code when the version has no `algorithm_ref` or no `pins`, because there is nothing to diff.
```

## What it obliges

- **This commit:** this record and the regenerated `docs/INDEX.md` only. No spec, plan,
  `model-schema` or code file is edited here.
- **PL 9564 (#1194; the planner's file, not edited here), before the mint:**
  - adopt T1 and T2 as ruled, with the row's tail as above;
  - Acceptance 17 gains a `grep -cF` check for T2;
  - add the acceptance case for a baseline with no `algorithm_ref` (item 5);
  - add the `blob_store` fix (item 9);
  - §"Scope" points DP-E1-6 at PL 9590 (item 6).
- **PL 9590 (#1181; the planner's file, not edited here), before the mint:** add the write
  and its red test (item 6).
- **RL 9668 (#1137):** the S2 note, already pushed (item 8).
- **F27's owner:** this record names the draft-row residue (item 7). This record does not
  edit the register row.
- **At the mint:** the working ids above become minted ids. Nothing else is owed.

## Acceptance — the violation that must become detectable

The violation: **a Rating Version whose change summary is not drafted from its diffs, or
whose submitted summary the version itself does not carry.** Each test is shown failing on
deliberately broken input.

- **The draft from the approved baseline (E1).**
  - Setup: v1 is approved; v2 adds a step and re-pins one rows-stored table to a version
    with changed cells.
  - `GET …/change-summary-draft` on v2 answers 200, `baseline` is v1's ref, and
    `structural_diff` equals `diff_algorithms(v1, v2)`.
  - The table entry's `diff` equals the diff route's answer for the same pair.
  - Red on `4d3be141`: the route does not exist.
- **T1 and T2 applied.** `grep -c 'change-summary-draft' docs/specs/03-rating-engine.md`
  prints `2` (the T1 row and the T2 clause), and each text is present byte for byte.
- **The refusal.** A version with no `algorithm_ref`, and one with no `pins`, each give 409
  `RATING_VERSION_UNPINNED` naming the missing field. With the check removed, the test fails.
- **Read-only.** The version row (`status`, `change_summary`, `evidence`) and the count of
  Audit Events are unchanged after the call.
- **Parquet.** A pair with a parquet side answers 200, with the entry `pending: true` and no
  `diff`, and **no Job row** is written.
- **No baseline, and a baseline with no algorithm** (item 5). Each gives `structural_diff: null`
  and a `text` that names which case it is. With the second case treated as the first, the test fails.
- **Why and impact.** The `text` ends with `Why:` and `Expected impact:`, each followed by
  nothing.
- **The version carries its submitted summary (item 6, Slice 5).**
  - Both the submit response and a later `GET` of the version carry the submitted
    `change_summary`. Red on `4d3be141`: both are `null`.
  - After a return to `draft` and a second submission, the version carries the second summary.

Drafted as working id 9541.
