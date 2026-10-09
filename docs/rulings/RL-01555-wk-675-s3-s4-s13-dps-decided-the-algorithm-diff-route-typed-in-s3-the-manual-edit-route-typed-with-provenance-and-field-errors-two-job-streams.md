---
id: RL-1555
family: ruling
title: WK-675 S3, S4 and S13 decision points decided — the algorithm diff route typed in S3's first commit, the manual-edit route typed with a created_by_edit record and FR-234's failures as field errors, and the Jobs list holding at most two event streams
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-09            # original date 2026-10-05, set at the draft; minted 2026-10-09
owner: decision-maker
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1286, PL-1364, FR-219, FR-229, FR-231, FR-234, FD-1335, FD-1366, RL-1184, RL-1361, RL-1418]
---

# RL-1555 — WK-675 S3, S4 and S13: the decision points that block activation, decided

*(Minted 2026-10-09 as RL-1555 from working id 9543, in the D3 batch mint; citations of the ids minted in this batch, and of ids already minted on main (RL-1474, RL-1475, RL-1473, RL-1445, PL-1476, SL-1477, FD-1437, RL-1438), are re-pointed outside quotes, quoted text and quoted channel entries stay as quoted, and cites of PL 9576, PL 9574, SL 9577 and SL 9575 stay working ids. (Re-minted +1 on 2026-10-09 by the minting rewrite, on the lead's 13:09:28 BST ruling (1): first minted as RL 1554, before the D1 mint moved the allocation.))*

## How this was ruled

- **The decisions are not this record's.** They are the maintainer's, by delegation, in two
  entries in `~/gi-pricing-plan.local/channel/to-lead.md`, quoted verbatim below: "2026-10-05
  17:26:46 BST" (S4) and "2026-10-05 17:30:02 BST" (S3 and S13, items 4 and 5). Each answers
  the decision-maker's memo `~/gi-pricing-plan.local/handover/dp-memo-wk675-s3-s4-s13-2026-10-05.md`
  (first filed as `dp-memo-wk675-s4-2026-10-05.md`), commissioned by the entry "2026-10-05
  17:17:37 BST — DISPATCH GO: WK-673 Slice 7 (SL-1391 / PL-1419) on LANE A", whose last line
  reads: "S4's DP-S4-1 (FD-1366 typing of the manual-edit route) and DP-S4-2 (FR-234 surfaces
  only the first issue) go to a DM memo before S4 activates; S2 and S4 serialise."
- **This record** writes the rulings down, gives the spec texts (T1–T4) and the plan texts
  (P1–P14) that carry them, and states the acceptance. Filed by decision-maker `dm-675s4`
  under working id 9543, reserved by the lead.
- **The plans it rules on** are unmerged drafts: PL-1558 (WK-675 S4, #1187), PL-1556 (S3,
  #1186) and PL 9576 (S13, #1185), all working ids at filing. Their planner applies the P-texts as a
  dated pre-mint edit. This record edits no plan.

## The maintainer's entries, verbatim

**"2026-10-05 17:26:46 BST — WK-675 S4 DP memo (handover/dp-memo-wk675-s4-2026-10-05.md) RULED"**, in full:

> DP-S4-1: (a), confirmed by symbol (RateTableDiff rating.py:735; RateTableVersion :899; no overlap with RL-1418's stored-version diff/cells). The T-text ADDS the existing 409 VALIDATION_FAILED when the base is not the latest version (_persist_new_version), and states that the 200 is a BARE RateTableDiff (the import route's 200 is ImportPreview, a different shape).
>
> DP-S4-1c (provenance, scope, mine): (ii) `created_by_edit {applied_to, edited_cells}`, copying ImportVerdict.applied_to's form. A hand-edited version MUST be distinguishable from a re-seed: that is the audit trail a governed pricing table needs (CLAUDE.md §1, auditability). It is a model-schema field, so contracts and the client are regenerated in the same commit. Red test: an edit's version carries it, and a seed's does not.
>
> DP-S4-2: the DM's NEW option (d), not the plan's (a). Each cell issue is a FieldError{field: "edits.<i>.<value>", code, message} inside ProblemDetail's existing `errors` (model_schema/problem.py:35, extra="forbid"). It keeps FR-450's ONE error shape (a second shape under the same name is the "shape defined twice" CLAUDE.md §2 forbids); no new type, no errors.py or problem.py change; RL 9767's own precedent reuses FieldError.
>
> The plan's BUG (apply_cell_edits raises "UNKNOWN_KEY: …" → _map_operation_error → PlatformError("UNKNOWN_KEY"), which is not in _KNOWN_CODES, so PlatformError.__init__ raises ValueError → a 500): (d) avoids it, and the slice adds a red test showing an unknown-key edit returns 422 with a FieldError, never 500.
>
> RL 9753 T4's anchor (#1067 :176-178, ending "diff?against=` |") WILL NOT MATCH once S7 applies RL-1361 T10 (the row becomes ".../diff?against=&portfolio="): re-anchor RL 9753 PRE-MINT on the prefix without the closing backtick (grep -cF = 1 at main AND after RL-1418 T1). The DM drafts the exact text; #1067's owner applies it before #1067 mints.
>
> S4 SERIALISES with S7 (the shared paths as listed); add model_schema/__init__.py to PL 9582's write set (S4's exports), so the contention check sees it.
>
> S3 and S13's DPs: in the same memo when added.

**"2026-10-05 17:30:02 BST — Rulings: T2 routing (RL 9562 mints ahead of PL 9560); _NUMERIC FD go; WK-675 DP-S3-1 (a) with the FD-1335 reading; DP-S13-1 (a′)"**, items 4 and 5:

> 4. WK-675 DP-S3-1: (a). The DATED LINE, by the maintainer (by delegation): "FD-1335 item 5 (:333-335, 'fixed before that slice dispatches') is read, for the consuming slice's OWN route only, as satisfied when that slice types the route in its FIRST commit, before any frontend code consumes the route, with generate-contracts --check green at that commit. The hold stays as written for every other route of the 12 and for any slice that does not type the route itself. Precedent: FD-1366 rule (ii)." Checked at origin/main: item 5 reads as quoted. The PL-1364 guard dependency is accepted: a dispatch delta goes on whichever of S3 or SL-1367 dispatches SECOND (the pending list holds 11 if S3 is first), and both dispatch records name test_contracts.py as the shared file.
>
>    DP-S3-2 (a): noted. S14's prefix link: a dispatch note, not a DP. Agreed.
>
> 5. DP-S13-1: (a′), cap 2 SSE streams, closed on visibilitychange (hidden). Checked: deploy/ has only docker-compose.yml, README.md and the keycloak realm; there is no reverse proxy, so the per-origin HTTP/1.1 limit argument holds. Record the multi-tab limit and the absence of HTTP/2 in the RL as the reason; reopening comes when a proxy with HTTP/2 lands. Polling (b): not chosen.

## Locators — read at `4d3be141`

- `algorithm_diff`, `backend/src/app/api/rating_algorithms.py:53-68`, typed `-> dict[str, Any]`;
  `diff_between`, `backend/src/app/platform/rating_algorithms.py:157`, returns
  `diff_algorithms(base, current).model_dump()`; `diff_algorithms`,
  `packages/model-schema/src/model_schema/rating.py:571`, `-> AlgorithmDiff` (`:541`).
  `ArtifactRef`'s `@model_serializer` (`packages/model-schema/src/model_schema/refs.py:143-145`)
  renders its string in python and JSON mode alike, and no step field is a `Decimal`, so typing
  the route does not change its JSON.
- `FD-1335` *Disposition*, Part B item 5, `docs/findings/FD-01335-*.md:333-335`.
- `PL-1364`'s guard test `test_every_untyped_body_exclusion_is_still_untyped`, specified in
  `docs/plans/PL-01364-*.md` (Acceptance, about `:357`): "So a route typed later fails".
- `RateTableDiff`, `rating.py:735`; `RateTableVersion`, `:899`, with `_one_creation_path`,
  `:941-947`; `ImportVerdict`, `:842`, whose `applied_to` names the base; `ImportPreview`,
  `:860`.
- `ProblemDetail` and `FieldError`, `packages/model-schema/src/model_schema/problem.py:35` and
  `:20`, both `extra="forbid"`; `ProblemDetail.errors` is `tuple[FieldError, ...]`.
- `PlatformError.__init__` (`backend/src/app/errors.py`) raises `ValueError` for a code not in
  `_KNOWN_CODES`; `UNKNOWN_KEY` is not in it. `_map_operation_error`
  (`backend/src/app/platform/rate_tables.py`) turns any `UPPER_SNAKE: ` prefix into that code.
- `_persist_new_version` (`backend/src/app/platform/rate_tables.py`) answers **409**
  `VALIDATION_FAILED`, "Rate table version already exists", on an `IntegrityError`.
- `stream_job_events`, `backend/src/app/api/jobs.py:254-310`: one row polled, then
  `asyncio.sleep(1.0)` (`:306`). `deploy/` holds `README.md`, `docker-compose.yml` and
  `keycloak-local/realm-gi-pricing.json`: no reverse proxy, so the app is served over HTTP/1.1.
- `03` §5.1's manual-edit row, `docs/specs/03-rating-engine.md:901`; `03` §4.2's example and
  notes, `:290-360`.

## Ruled

**S4 (PL-1558).**

1. **DP-S4-1: (a), edits only.** The request body is `RateTableManualEdit` `{base_version: int
   ≥ 1, edits: list[RateTableCell] (one or more; each an existing key's full row; a key at most
   once), change_note: str (non-blank, FR-229), confirm: bool = false}`, `extra="forbid"`.
   **200** is a **bare** `RateTableDiff` (not the import route's `ImportPreview`), and nothing
   is created. **201** is the `RateTableVersion` at `base_version + 1`. **409**
   `VALIDATION_FAILED` where `base_version + 1` already exists, that is, the base is not the
   latest version (`_persist_new_version`'s existing refusal). `RateTableCell` is RL-1475 T5's
   type (working id, #1067).
2. **DP-S4-1c: (ii), provenance.** `RateTableVersion` gains `created_by_edit: ManualEdit |
   None`, `ManualEdit` being `{applied_to: ArtifactRef, edited_cells: int ≥ 1}` (`applied_to`
   the base, in `ImportVerdict.applied_to`'s form; `edited_cells` the number of edits applied).
   At most one of `created_by_operation`, `created_by_import` and `created_by_edit` is set
   (`_one_creation_path` widens). A version made by the manual-edit route carries it; a seeded
   version does not. `docs/contracts/` and the frontend client are regenerated in the same
   commit (FR-451).
3. **DP-S4-2: (d).** Every failure of a manual edit is one `FieldError` in `ProblemDetail`'s
   existing `errors`, with `field` `edits.<index>.<value name>` for the edit it concerns. No new
   type, and no edit to `errors.py` or `problem.py`. FR-234's `NULL_VALUE` and
   `OUT_OF_BOUNDS` come under code `RATE_TABLE_INCOMPLETE`; the edit-addressing faults
   `UNKNOWN_KEY` and `DUPLICATE_KEY` come under code `VALIDATION_FAILED`, and are never passed
   to `_map_operation_error`. An unknown-key edit answers **422** with a `FieldError`, never 500.
4. **S4 serialises with WK-673 S7** (`SL-1391`) on the shared paths, and
   `packages/model-schema/src/model_schema/__init__.py` joins PL 9582's write set.
5. **RL-1475 T4's anchor** was re-set before mint on #1067 itself (head `511af512`, the
   amendment "2026-10-05 17:29 BST"), on the 17:26:46 entry's order. It is recorded here and not
   repeated: the find string is `` | `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against= ``.

**S3 (PL-1556).**

6. **DP-S3-1: (a)**, on the dated line in item 4 above. S3 types `GET
   /api/v1/rating-algorithms/{slug}@{version}/diff` as `-> AlgorithmDiff` in its **first
   commit**, before any frontend code consumes the route, with `generate-contracts.py --check`
   green at that commit. The hold stays for every other route of `FD-1335`'s twelve.
7. **The PL-1364 guard dependency is accepted.** Whichever of S3 and `SL-1367` dispatches
   second carries a dispatch delta (the pending list holds 11 entries if S3 is first), and both
   dispatch records name `backend/tests/test_contracts.py` as the shared file.
8. **DP-S3-2: (a)**, the default: drag-to-connect is not in S3.

**S13 (PL 9576).**

9. **DP-S13-1: (a′).** The Jobs list holds **at most two** event streams, for the newest
   non-terminal rows on the visible page, and **none while the document is hidden**: a
   `visibilitychange` to hidden aborts every stream; back to visible re-reads page one and
   re-opens them. **The reason:** the app is served over HTTP/1.1 (no reverse proxy in
   `deploy/`), and the browser's limit of six connections per origin is shared by every tab,
   so a per-page cap of four lets two tabs block every other request of the app. **Reopen
   trigger:** a reverse proxy serving HTTP/2 lands in `deploy/`; then the cap is re-decided.
   Polling, option (b), was not chosen.

**Noted, not a decision point.** S14 (PL 9574, #1189)'s result link by reference prefix is a
dispatch note (item 4 above, "a dispatch note, not a DP").

## The spec texts

Find strings are counted with `grep -cF` over `docs/specs/03-rating-engine.md` at origin/main
`4d3be141`; each is **1**. S4 applies T1–T4 byte for byte with its code, in one commit.

**T1 — `03` §5.1, the manual-edit row (`:901`; DP-S4-1, DP-S4-1c, DP-S4-2).** Find
`Owner: WK-675's editor slice. |`. Append after `Owner: WK-675's editor slice.` and one space,
before the closing ` |`. Nothing is struck.

```text
**Typed <date> (`RL-<this>`, DP-S4-1, DP-S4-1c and DP-S4-2; FD-1366's template line).** The body is `RateTableManualEdit`: `base_version` (an integer ≥ 1, the version edited), `edits` (one or more `RateTableCell`s, each the full row of a key that `base_version` has; a key appears at most once), `change_note` (required, non-blank, FR-229) and `confirm` (default `false`); an unknown field is refused. Requires `rating:write`. **200** a bare `RateTableDiff` of the would-be version against `base_version`; nothing is created. **201** `RateTableVersion` with `confirm: true`: version `base_version + 1`, its cells the base's with each edit's value, `seeded_from` inherited from the base, and `created_by_edit` recording the base and the number of edits (§4.2). **409** `VALIDATION_FAILED` where `base_version + 1` already exists (the base is not the latest). **422** with every failure in the problem's `errors`, one field error per failure, its `field` `edits.<index>.<value name>` for the edit it concerns: `UNKNOWN_KEY` (no such key in the base) and `DUPLICATE_KEY` (a key edited twice) under code `VALIDATION_FAILED`; FR-234's `NULL_VALUE` and `OUT_OF_BOUNDS` under code `RATE_TABLE_INCOMPLETE`. **404** `NOT_FOUND` for an unknown table or `base_version`. A key cannot be added or removed here; that is the import route's.
```

If RL 9907 (working id)'s `Permission` column has landed in `03` §5.1 when T1 is applied, the
sentence "Requires `rating:write`." is left out and the row's fourth cell carries
`rating:write`.

**T2 — `03` §4.2, the example (DP-S4-1c).** Find `  "created_by_import": null,`. Insert
after that line:

```text
  "created_by_edit": {"applied_to": "rate_table:motor-driver-age-relativity@5", "edited_cells": 1},
```

**T3 — `03` §4.2, the creation-record note (DP-S4-1c).** Find
``hand, so both are `null`.``. Replace that line with:

```text
> hand, so both are `null` and it carries `created_by_edit` instead.
>
> **`created_by_edit` added <date> (`RL-<this>`, DP-S4-1c).** A version created by the
> manual-edit route (§5.1) carries `{"applied_to", "edited_cells"}`: `applied_to` names the
> base version edited, in `created_by_import.applied_to`'s form, and `edited_cells` is the
> number of edits applied. It is set at creation and immutable with the version, and it is
> what tells a hand-edited version from a re-seed.
```

**T4 — `03` §4.2, seed lineage and exclusivity (DP-S4-1c).** Two finds, each replaced.
Find `` > the resolved baseline — `BulkOperation.applied_to` or `created_by_import.applied_to` — ``;
replace with:

```text
> the resolved baseline — `BulkOperation.applied_to`, `created_by_import.applied_to` or `created_by_edit.applied_to` —
```

Find `` > `created_by_import` remain mutually exclusive. ``; replace with:

```text
> `created_by_import` remain mutually exclusive, and `created_by_edit` with both (amended <date>, `RL-<this>`).
```

## The plan texts

Each find string is counted with `grep -cF` over the plan file at the PR head named; each is
**1**. The planner applies them as one dated pre-mint edit per plan and adds the note
"P-texts of RL-1555 applied <date>".

**PL-1558 (S4), #1187 at `800d3a70`** (the plan file is unchanged since `feb8510f`).

- **P1, the DP table.** After the line beginning `| **DP-S4-4** |`, insert a blank line and:
  `**Ruled 2026-10-05 (RL 9543, working id):** DP-S4-1 (a), its 200 a bare `RateTableDiff` and a 409 for a base that is not the latest; DP-S4-1c (ii), `created_by_edit`; DP-S4-2 (d), every failure a `FieldError` in the problem's existing `errors`; DP-S4-3 and DP-S4-4 as recommended.`
- **P2, the write set.** Find (the fenced line, byte for byte)
  ```text
  | same | new `RateTableCell`; the DP-S4-1 request and response types | added |
  ```
  replace with
  `` | same | new `RateTableCell`, `RateTableManualEdit` and `ManualEdit`; `RateTableVersion.created_by_edit` and `_one_creation_path` widened (RL 9543) | added | ``
  and insert after it
  `` | `packages/model-schema/src/model_schema/__init__.py` | the new types' exports (RL 9543 item 4) | changed | ``.
- **P3, Acceptance 7.** Find ``   base answers 409 (the existing `_persist_new_version` refusal).``; append
  `` The new version carries `created_by_edit` `{applied_to: <the base>, edited_cells: <the number of edits>}`, and a seeded version carries none (red first, RL 9543 item 2).``
- **P4, Acceptance 8.** Find ``   errors (DP-S4-2) name that cell's key; a float-typed JSON value → 422 (FR-21); an unknown``;
  replace with
  ``   errors are `FieldError`s with `field` `edits.<i>.<value name>` (RL 9543 item 3); an unknown-key edit → 422 with a `FieldError` coded `UNKNOWN_KEY`, never 500; a float-typed JSON value → 422 (FR-21); an unknown``.
- **P5, the test.** Find
  ``    assert {"area": "A", "relativity": "-1"} in [e["key"] for e in r.json()["errors"]]``;
  replace with
  ``    assert [(e["field"], e["code"]) for e in r.json()["errors"]] == [("edits.0.relativity", "OUT_OF_BOUNDS")]``.
- **P6, Task 3 Step 3.** Find
  ``  runs through `validate_rate_table` (`:323`); every issue goes into the DP-S4-2 extension,``;
  replace with
  ``  runs through `validate_rate_table` (`:323`); every issue becomes one `FieldError` (RL 9543 item 3),``.
  Then find ``  located by key. The handler is typed `-> RateTableDiff` and sets 201 on confirm with a``;
  replace with
  ``  `field` `edits.<i>.<value name>`; `UNKNOWN_KEY` and `DUPLICATE_KEY` are collected the same way under `VALIDATION_FAILED` and never reach `_map_operation_error`, which would raise a 500 (`UNKNOWN_KEY` is not in `_KNOWN_CODES`); the confirmed version sets `created_by_edit`. The handler is typed `-> RateTableDiff` and sets 201 on confirm with a``.
  The pure-core tests' raise form (`apply_cell_edits`, Step 1) is the planner's to keep or
  reshape, provided P4's Acceptance holds.

**PL-1556 (S3), #1186 at `20ba9a2e`; re-counted at `c5d1d03a` (amendment of 2026-10-05 17:42 BST below).**

- **P7, Status.** Find (the fenced line, byte for byte)
  ```text
  `draft`. DP-S3-1 and DP-S3-2 (below) are open and are the maintainer's (by delegation). The
  ```
  replace with (the fenced line, byte for byte)
  ```text
  `draft`. DP-S3-1 and DP-S3-2 (below) are decided by the maintainer (by delegation), recorded in RL 9543 (working id): DP-S3-1 (a), DP-S3-2 (a). The
  ```
- **P8, Activation need 4.** Find `4. **DP-S3-1 and DP-S3-2 decided**, each by a dated line.`;
  append
  `` Decided (RL 9543). The dispatch record names `backend/tests/test_contracts.py` as shared with `SL-1367`; whichever of S3 and `SL-1367` dispatches second carries the pending-list delta (11 entries if S3 is first; RL 9543 item 7).``
- **P9, Acceptance 21.** *(Discharged before mint: the planner's dated note at `c5d1d03a` already carries it; not applied. See the amendment below.)* Find
  ``21. **The diff route is typed** (DP-S3-1, if (a)). In `generated.json`, the 200 response of``;
  replace with
  ``21. **The diff route is typed in the slice's first commit** (DP-S3-1 (a), RL 9543 item 6), before any frontend code consumes it, with `generate-contracts.py --check` green at that commit. In `generated.json`, the 200 response of``.
- **P10, Task 5.** *(Discharged before mint: at `c5d1d03a` the task is Task 0A, the slice's first commit, and Task 5 is a tombstone; not applied. See the amendment below.)* Find `### Task 5: The diff route typed; the contract and the client (DP-S3-1)`;
  insert after it a blank line and
  `**Order (RL 9543 item 6):** Step 1 and the contract regeneration are the slice's first commit, made before Task 1.`

**PL 9576 (S13), #1185 at `06fb5ca3`.**

- **P11, Status.** Find (the fenced line, byte for byte)
  ```text
  `draft`. One decision point is open and blocks activation (DP-S13-1). The plan stays
  ```
  replace with (the fenced line, byte for byte)
  ```text
  `draft`. DP-S13-1 is decided, (a′), in RL 9543 (working id). The plan stays
  ```
- **P12, Acceptance 5.** Find
  `5. The same file shows the live behaviour DP-S13-1 rules. Under recommendation (a): at most`;
  replace with
  `5. The same file shows the live behaviour DP-S13-1 rules, (a′) (RL 9543 item 9): at most`.
  Then find
  ``   four streams are open at once, for the newest non-terminal rows; a `progress` event updates``;
  replace with
  ``   two streams are open at once, for the newest non-terminal rows, and none while the document is hidden (hidden aborts every stream; visible re-reads page one and re-opens them); a `progress` event updates``.
- **P13, the test case.** Find
  ``  5. six running rows open exactly four `streamJobEvents` calls, for the four newest ids;``;
  replace with
  ``  5. six running rows open exactly two `streamJobEvents` calls, for the two newest ids; a `visibilitychange` to hidden aborts both, and back to visible re-reads page one and re-opens two;``.
- **P14, `syncStreams`.** Find
  ``  - `syncStreams()` (DP-S13-1 (a)): the four newest rows whose status is not in `TERMINAL` ``
  (no trailing space in the file; the find ends at `` `TERMINAL` ``); replace that prefix with
  ``  - `syncStreams()` (DP-S13-1 (a′), RL 9543): while `document.visibilityState` is `visible`, the two newest rows whose status is not in `TERMINAL` ``.

## What it obliges

- **This commit:** this record only. No spec, plan or code file is edited here.
- **The planner** applies P1–P6 to PL-1558, P7 and P8 to PL-1556 (P9 and P10 are discharged) and P11–P14 to PL 9576 before
  each mints, citing this record. If a find string no longer counts 1 at the plan's head, the
  planner stops and reports it to the decision-maker; it is never re-anchored by guess.
- **WK-675 S4** applies T1–T4 with its code in one commit, with `docs/contracts/` and the
  frontend client regenerated (FR-451). **WK-675 S3** types the diff route in its first commit.
  **WK-675 S13** builds the two-stream rule.
- **The dispatch records**: S4's names its serialisation with `SL-1391`; S3's and `SL-1367`'s
  each name `backend/tests/test_contracts.py`, and the second carries the pending-list delta.
- **At the mint:** `RL-<this>` resolves; the working ids RL-1475, RL 9907, PL-1558, PL-1556 and
  PL 9576 are re-pointed to their minted ids in the same run where they have minted.

## Acceptance — the violation that must become detectable

Each is a test that is red on the code before its slice and green after it.

1. **S4, the bare 200.** A manual-edit preview's body validates as `RateTableDiff` and has no
   `created_by_import` or `diff` member; nothing is created.
2. **S4, the stale base.** A confirm against a base that is not the latest answers 409
   `VALIDATION_FAILED`.
3. **S4, provenance.** A version created by the manual-edit route carries `created_by_edit`
   with `applied_to` the base and `edited_cells` the number of edits; a seeded version carries
   none; a `RateTableVersion` with two of the three creation records set is refused.
4. **S4, every failure located.** An edit with two out-of-bounds values answers 422 with two
   `FieldError`s, `edits.0.<value>` and `edits.1.<value>`, both `OUT_OF_BOUNDS`.
5. **S4, never a 500.** An edit naming a key the base lacks answers 422 with one `FieldError`
   coded `UNKNOWN_KEY`. Before the fix this path is the 500 from `PlatformError.__init__`.
6. **S4, one error shape.** `generate-contracts.py --check` is green, and the manual-edit
   route's 422 is the shared `ProblemDetail` schema; `problem.py` is unchanged.
7. **S3, typed first.** At S3's first commit, the diff route's 200 in
   `docs/contracts/openapi/generated.json` is a `$ref` to `AlgorithmDiff`, and
   `generate-contracts.py --check` is green there.
8. **S13, two streams, none hidden.** Six running rows open exactly two streams; hiding the
   document aborts both; showing it re-reads page one and re-opens two.

## What this record does not decide

- **The FD-1335 reading for any other route.** Item 4 confines it to the consuming slice's own
  route.
- **Polling for the Jobs list** (DP-S13-1 (b)): not chosen; a change to `PL-1286`'s "live over
  the SSE stream" stays the maintainer's.
- **A multiplexed job-events route** for the list: a new backend route, out of S13.
- **`NFR-498` for Rate Table Versions.** Observed while reading for DP-S4-1c: `NFR-498`
  (`03:1339`) requires Audit Events with before/after state for "rate table versions, bulk
  operations", and neither `backend/src/app/api/rate_tables.py` nor
  `backend/src/app/platform/rate_tables.py` writes one at `4d3be141` (`git grep -i audit`: no
  hit). `created_by_edit` is the version's own record and does not discharge it. Routed to the
  lead as a possible finding; not ruled here.

## Amendment, 2026-10-05 17:42 BST: P7–P10 re-counted at PL-1556's new head, before mint

Plan-text update only; nothing ruled above changes (decision-maker `dm-675s4`, on the lead's
order). PL-1556 (#1186) moved from `20ba9a2e` to `c5d1d03acdb292e34ff30ebaf58ff87ab3f918d3`:
the planner moved the diff-route typing to a new Task 0A, "the slice's FIRST commit", left
Task 5 as a tombstone ("### Task 5: moved to Task 0A (dated pre-mint note)"), and added a
dated note to Acceptance 21. Each find string was re-counted with Python `str.count` on the
plan file at `c5d1d03a`:

| P-text | Find string (start) | Count at `c5d1d03a` | Disposition |
|---|---|---|---|
| P7 | `` `draft`. DP-S3-1 and DP-S3-2 (below) are open `` | 1 | applies as written |
| P8 | `4. **DP-S3-1 and DP-S3-2 decided**, each by a dated line.` | 1 | applies as written (no `SL-1367` delta is in the plan's activation needs yet; `SL-1367` appears only in `relates:` and Task 0 row 0.13) |
| P9 | `21. **The diff route is typed** (DP-S3-1, if (a)).` | 1 | **discharged**: the line's own dated note now reads "this holds in the slice's **first** commit (Task 0A), before any frontend code consumes the route, with `generate-contracts --check` exiting 0 at that commit", which is P9's content; applying P9 would state it twice |
| P10 | `### Task 5: The diff route typed; the contract and the client (DP-S3-1)` | **0** | **discharged**: the heading is now `### Task 0A: The diff route typed; the contract and the client (DP-S3-1) — the slice's FIRST commit` (count 1), which is P10's order |

So the planner applies P7 and P8 only. PL-1558 (`800d3a70`) and PL 9576 (`06fb5ca3`) are
unchanged at their heads (ls-remote at 17:42 BST), so P1–P6 and P11–P14 stand as counted.

## Pre-mint note, 2026-10-05 18:45 BST: P2, P7 and P11's find strings re-quoted as fenced lines (extended 18:47 BST: P7 and P11's replace strings)

Presentation only; nothing ruled or applied changes (decision-maker, on the maintainer's (by
delegation) entry of 2026-10-05 18:43:10 BST in the lead's channel: "P2, P7 and P11's find
strings count 0 when read LITERALLY and 1 only under CommonMark code-span padding removal …
Or RL-1555 re-quotes those three without the padding; the DM picks one form"). The three were
code spans padded with a space so that they could open with a backtick or a pipe; read
literally the padding is part of the string, and the count is 0. P7 and P11 carried a leading
space only, which CommonMark itself does not strip, so a padding-rule sentence would not have
resolved them. Each is now a fenced line: the find string is that line's bytes, without the
two-space list indentation every continuation line in this list carries. Counted with Python
`str.count` on the plan file at its pre-apply head, each is **1**: P2 in PL 9582 at
`800d3a7082b1aa4ab51019cc2a8993c9510129ff`, P7 in PL 9578 at
`c5d1d03acdb292e34ff30ebaf58ff87ab3f918d3`, P11 in PL 9576 at
`06fb5ca3745e12379d0763cdfe63359155c9acce`. The planner applied them in this reading (PL 9582
#1187 at `3b15a829`, PL-1556 #1186 at `aea4b634`, PL 9576 #1185 at `0857c5e1`).

**Extended 2026-10-05 18:47 BST** (on the lead's order): P7 and P11's replace strings carried
the same leading-only space and are fenced the same way, so a reader re-deriving the plans gets
the applied bytes, which have no leading space. Counted with Python `str.count` on the applied
plan, each is **1**: P7 in PL-1556 at `aea4b634`, P11 in PL 9576 at `0857c5e1`.
