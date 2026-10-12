---
id: PL-1668
family: plan
kind: map
title: WK-675 — Slice 5 (SL-1547) after RL-1613 and the 02:58:33 DP-0 ruling, the contract-changing ordered input, the bulk-operation typing dependency, and the S5/S6 drift rule: a dated Work-plan delta to PL-1546
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-12
owner: planner
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1546, PL-1286, RL-1613, OQ-1223, SL-1547, SL-1548, FD-1366, SL-1600, RL-1445]
---

# PL-1668 — WK-675 Slice 5 after RL-1613: the contract-changing `ordered` input, the bulk-operation typing dependency and the S5/S6 drift rule (delta to PL-1546)

*(Minted 2026-10-12 as PL-1668 from working id 9867, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"a change is one dated Work-plan delta, a new `PL-` that
> `relates:` the Work's plan"*). It changes **one row** of
> [`PL-1546`](PL-01546-wk-675-slices-5-to-11-work-plan-delta.md) (WK-675's S5–S11 delta),
> row 1, `SL-1547`. `PL-1546`'s body is frozen and is not edited. **Read `PL-1286`'s S5 row, then
> `PL-1546` row 1 and R5.1–R5.3, then this file; where they differ, this file is the later
> statement.** S5's executor binds what `PL-1546`'s header names. This delta adds
> `contract-schema` (the authored `rating-algorithm.schema.json`), `spec-change` (FR-213,
> FR-261) and `python-package` (`model-schema`, `pricing-core`). The executor is spawned from
> `.claude/roles/executor.md`; its `LG-` quotes `PL-1546` row 1 and this file's §"Tasks" (S5's
> row, as amended) as its scope.

Filed under **working id 9867**, reserved by the lead (`~/gi-pricing-plan.local/handover/eta.md`,
"2026-10-12 02:54:24 BST", free-checked 0/0/0). Written 2026-10-12 by the planner (seat
planner-wk1250-s3), on the same branch as `PL-1667` (the bulk-operation typing slice, SL-1669,
WK-1178). **Tree read:** `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9`. Every
`file:line` below was read there. **No test was run at planning time.**

## Context — what changed since `PL-1546` (filed 2026-10-08, tree `60e9254c`)

Quoted verbatim from `~/gi-pricing-plan.local/channel/to-lead.md` (local, so quoted; RFC-777) and
from `RL-1613` on `main`:

1. **`RL-1613`** (D11, 2026-10-11) decided `OQ-1223` (a) and made S5 contract-changing.
   *"What it obliges"* items 2 and 3 (`RL-1613:74-113`) are S5's build. Its title: *"WK-675 S5 is
   contract-changing"*.
2. **"2026-10-12 02:51:32 BST"**, item (2): *"(2) must carry RL-1613's contract-changing scope
   (model-schema `ordered`, contracts and frontend regenerated, FR-213/FR-261 amendments) and name
   its overlap with (1) on test_contracts.py's UNTYPED_REQUEST_PENDING."*
3. **"2026-10-12 02:53:52 BST"**, item 1: *"The S5 `ordered` drift is recorded in eta: whichever of
   S5/S6 merges second re-merges and re-gates its quote-form tests."*
4. **"2026-10-12 02:58:33 BST — DP-0: (b), stated as SUPERSEDING my 2026-10-11 10:55:02 item 2
   (DP-A (a))"**, condition 4: *"PL 9867 (the S5 delta) names SL 9868 as an activation need, plus
   RL-1613's scope."* Condition 3: *"FALLBACK TRIGGER: if SL 9868 is not merged when S6 merges,
   bring it to me. S5 then either waits or reverts to DP-A (a), my ruling at that time."* **The
   10:55:02 entry's item 2 ("S5 types POST bulk-operation itself, in its FIRST commit") is
   superseded.** `PL-1546` never carried it, so nothing here strikes it.

## Goal

Make `SL-1547` (WK-675 S5) GO-able against a plan that matches the tree and the rulings since
`PL-1546` was filed. That means RL-1613's contract-changing scope, SL-1669 as the slice that
discharges the bulk-operation typing hold, the S5/S6 drift rule, and the overlap on the contract
guard. Done when `SL-1547` closes on its `LG-`, which quotes `PL-1546` row 1 and this file's
§"Tasks" as its scope.

## Tasks

Under L5 a Work plan's tasks are its slice rows (`PL-1546` §Tasks); S5's steps are written in its
`LG-` by its executor. This delta's one task is **S5's row, as amended**:

`PL-1546` row 1 stands except as amended below. Its scope (`PL-1286` S5 row, R5.1–R5.3) and its
requirements (`03` §3.3 FR-230, FR-231, FR-232, FR-233, FR-235; `00` FR-25; NFR-463; register
F-W10-1, F-W10-2 view limb) are unchanged. **Added** to the requirements, each individually:
`03` **FR-213** (the input contract; RL-1613's dated clarification) and `03` **FR-261** (the
`monotone` property; RL-1613's dated amendment). **Added** to the dependencies: SL-1669 (R5.3,
as amended).

### R5.3, amended — the bulk-operation typing hold is discharged by SL-1669

- **Was** (`PL-1546:163-166`): *"S5 calls `bulk-operation`, so it waits until that route is typed
  — the FD-1366 residue, which WK-1178 builds in P2"*.
- **Now:** the slice that types it is **SL-1669** (WK-1178, `PL-1667`): the request
  (`BulkOperationRequest`, discriminated on `kind`) and the 201 (`RateTableVersion`).
- **S5 does not type the route, and does not edit `backend/src/app/api/rate_tables.py`'s
  bulk-operation handler.** S5's dialog posts with the generated `BulkOperationRequest` type and
  reads the generated `RateTableVersion`.
- **If S5 finds it must edit that handler**, `FD-1366`'s per-route hold (ii) applies, and S5
  stops and reports.
- **Fallback (02:58:33 condition 3):** if SL-1669 has not merged when `SL-1548` (S6) merges, the
  lead takes it to the maintainer. S5 then waits, or reverts to DP-A (a) by a new ruling, not by
  this plan.

### R5.4 — RL-1613's contract-changing scope (new)

These are `RL-1613`'s words, *"What it obliges"* item 2 (`:82-104`) and item 3 (`:105-113`).
Each line is S5's to deliver in S5's one PR (`CLAUDE.md` §2: spec, code and tests in one
commit chain):

- **`03` FR-213** (`03:82`), a dated clarification: an `enum` Rating Input may declare
  `ordered: true`, valid only with a non-empty `domain`, whose list order is the declared level
  order. `ordered` is `false` by default.
- **`03` FR-261** (`03:182`), a dated amendment: case (4)'s "not orderable" admits an `ordered`
  enum; a `monotone` property on it sweeps the levels of `domain` in declared order. **How the run
  labels that grid, and how `lower`/`upper` apply to levels, are S5's to specify in this
  amendment** (`RL-1613:90-92`). The spec text is shown in full in the `LG-` and read at the ACK.
  An unordered `enum`, and every `string`, `date` and `bool` input, stays refused with
  `REGRESSION_PROPERTY_INVALID`.
- **`model-schema`**: `ordered: bool = False` on `InputContractField`
  (`model_schema/rating.py:290-302`). A validator refuses `ordered: true` on any type but `enum`,
  or without a non-empty `domain`. **The exception class is now fixed** (R5.5).
- **`pricing-core`**: `properties.py` admits an ordered enum and sweeps its levels in order. The
  refusal is at `properties.py:144-147` (`if field.type not in (RatingInputType.INT,
  RatingInputType.DECIMAL): raise UnsweepableProperty(... "not orderable")`). `ordered` is left out
  of each field's dump when `false` and kept when `true`, at `to_jdm`
  (`compile.py:600`, the dump at `:626`; R5.7).
- **The hash condition, red first** (RL-1613 ruling item 2 (i)–(iv)): see the Acceptance additions.
- **Contracts and frontend:** `docs/contracts/openapi/generated.json` is regenerated on S5's merge
  base; `pnpm --dir frontend generate:api`. The frontend shows an ordered input's levels in
  declared order, display only, from the generated type (R5.8 names where).

### R5.5 — the validator's exception class: `InputFreeError` (resolved since RL-1613)

`RL-1613` left the class to S5's GO: *"It raises `InputFreeError` if `SL-1600` has merged by S5's
base, and otherwise `ValueError`"* (`:95-96`). **`SL-1600` merged as `02f23b4a` (#1273)**, and
`InputFreeError` exists at `packages/model-schema/src/model_schema/input_free.py:32`
(`class InputFreeError(ValueError)`). So the validator raises **`InputFreeError`**. S5's Task 0
re-reads the line, and stops if the class is gone.

### R5.6 — the authored `rating-algorithm.schema.json` is hand-edited, not regenerated (a locator correction to RL-1613)

`RL-1613` item 3 says `docs/contracts/schemas/rating-algorithm.schema.json` is *"regenerated on
S5's merge base"*. At `fc4401dc` it is **not a generated file**. `scripts/generate-contracts.py`
writes `docs/contracts/schemas/generated/` and `openapi/generated.json`, and there is no
`schemas/generated/rating-algorithm.schema.json`. `backend/tests/test_contracts.py:105` lists it
as *"shipped in model-schema, never compared — register F27"*.

- **The precedent:** `SL-1340` (#1263, `a3572d1a`) edited it by hand for `sub_graphs`.
- **What S5 does:** it adds `ordered` to the `input_contract` item schema by hand, under
  `contract-schema` (at `:21`, beside `"domain"`), with the same constraint, and regenerates
  `openapi/generated.json`.
- **This is not a change to the ruling.** RL-1613's obligation, that the published contracts
  carry `ordered`, is met by both files.

### R5.7 — the omission covers every hashed dump, not only `to_jdm` (a sweep obligation)

`RL-1613` names `to_jdm`'s dump (`compile.py:626`). A stored Rating Version's bundle hash is
re-checked at load: `backend/src/app/platform/rating_versions.py:880`,
`if bundle.content_hash != row.bundle.get("content_hash")`. So any other dump of
`InputContractField` that reaches a hash would also move it. Two ways to meet this:

- **Recommended:** implement the omission **once, on `InputContractField`'s serialisation**, so
  every dump site omits `ordered: false`.
- **Otherwise:** omit it at `to_jdm` only. Then S5's Task 0 must sweep
  `grep -rn 'input_contract' packages/*/src backend/src --include=*.py`, read each hit, and
  record in the `LG-` that none other is hashed or stored.

Either way, the Acceptance's existing-hash test is the proof.

### R5.8 — the S5/S6 drift rule (02:53:52 item 1)

- **Where the drift is.** `SL-1548` (S6, building; GO 02:53:52) renders the sandbox quote form
  from the generated `InputContractField` (FR-213). S5 adds `ordered` to that generated type and
  asks for an ordered input's levels to show in declared order.
- **Where S5 displays it.** S5's `LG-` names the display site.
  - If it is S6's quote form (`frontend/src/…` as S6 lands it), then **whichever of S5 and S6
    merges second re-merges `main` and re-gates its quote-form tests** (02:53:52 item 1).
  - If it is in S5's own views only, the rule still binds through the regenerated type, so the
    second to merge re-runs `pnpm --dir frontend type-check` and the quote-form tests on its
    merge tree.
- **Expected order.** One WK-675 slice builds at a time (`PL-1546` Global Constraints), so S5
  starts after S6 merges. S5 is therefore expected to be second.

### R5.9 — the overlap with SL-1669 on the contract guard and the generated contract

| Shared path | SL-1669 (WK-1178) | S5 (WK-675) | Rule |
|---|---|---|---|
| `backend/tests/test_contracts.py` `UNTYPED_REQUEST_PENDING` (`:3201-3213`) and `UNTYPED_2XX_PENDING_PART_B` (`:3187-3196`) | removes the bulk-operation entries (`:3202-3205`, `:3192`) | **adds none**; re-adding a bulk-operation entry is a stop | **SL-1669 merges first** (an activation need below). S5 re-merges `main` before its gate and does not touch these lists. Otherwise `test_every_untyped_body_exclusion_is_still_untyped` (`:3273-3290`) is the check that reds |
| `docs/contracts/openapi/generated.json` | regenerated (the typed route) | regenerated (`ordered`) | generated, never hand-merged: **the second to merge regenerates on its own merge base** (`uv run python scripts/generate-contracts.py`, then `--check`) |
| `packages/model-schema/src/model_schema/rating.py` | the bulk-operation block (`:1215-1300`) | `InputContractField` (`:290-302`) | **name-disjoint by definition** (`RL-1263` as amended by `RL-1445`) |
| `docs/specs/03-rating-engine.md` | §5.1 bulk-operation row (`:1039`) | FR-213 (`:82`), FR-261 (`:182`) | different rows; no serialisation |

WK-1250 S3 (`SL-1341`, READY plan-side, lane B, not dispatched) also edits `model_schema/rating.py`
(`SubGraphRef`), the authored `rating-algorithm.schema.json` and `generated.json`. The same two
rules apply if it builds near S5: name-disjoint definitions, and the second to merge regenerates.
Both slices also carry a **hash-stability invariant** on the same `bundle_hash` (`compile.py:661`).
S3 has DP-S3-2's "only when non-empty"; S5 has RL-1613's "omit when false". **Whichever merges
second re-runs the other's existing-hash test on its own tree** (`PL-1629` acceptance 7 already
binds S3 to this).

## S5's activation needs, as amended (each with its state at `fc4401dc`)

1. **S4 closed.** **MET**: `SL-1559` closed (#1281, `372fa92a`).
2. **OQ-1223 decided** (`PL-1546` acceptance 6). **MET**: `docs/open-questions.md:135` struck,
   resolver `RL-1613`.
3. **`SL-1391` closed.** **MET** (`PL-1546` row 1).
4. **SL-1669 (WK-1178, `PL-1667`) merged.** **OPEN.** Its own GO waits on its DP-2 (`PL-1667`).
   This need replaces `PL-1546` row 1's "the FD-1366 bulk-operation typing slice (WK-1178)
   merged" by naming the slice.
5. **`SL-1548` (S6) merged**, because one WK-675 slice builds at a time (`PL-1546` Global
   Constraints). **OPEN** (S6 building). The fallback (R5.3) is checked at this merge.
6. **This delta minted**, or GO'd on its working id as the lead dispatches. **OPEN.**
7. **The lead's GO**, lane or team fixed at it; the dispatch record quotes `RL-1613` items 2–3
   and R5.3–R5.9. **OPEN.**

## Decision points

None new. `RL-1613:90-92` leaves the grid's labels and `lower`/`upper` on levels to S5's spec
amendment, by design. That is S5's specification work, read at the ACK, not a decision point of
this plan. R5.7's two implementation routes are both inside `RL-1613`; the executor records
which route it took.

## Acceptance Standard

These are **additions to `PL-1546`'s items 1–8**, for S5 only.
Each item is checked by a command a fresh reviewer can run from the repository root, at S5's
head unless stated.

1. **An unordered input's hash does not move** (`RL-1613` item 2 (ii)). A test recomputes the
   `content_hash` of an existing fixture bundle and shows it equal to the value recorded at S5's
   base. It is **shown red** when the omission is removed (a dump that keeps `ordered: false`).
   The pinned `_SCORE_FIXTURE_HASH` tests stay green and unchanged:
   `git diff origin/main -- packages/pricing-core/tests/test_rating_shadowed_inputs.py packages/pricing-core/tests/test_rating_wire_order.py`
   prints nothing (`:74`, `:145`).
2. **Opt-in enters the hash** (item 2 (iv)): a bundle with `ordered: true` hashes differently
   from the same bundle without it.
3. **`ordered` is refused where invalid:** negative tests for `ordered` on `int`, on `enum`
   without `domain`, and on `enum` with `domain: []`. Each raises `InputFreeError` (R5.5), and each
   reds if the validator is removed.
4. **No input becomes sweepable unasked:** `backend/tests/test_regression_suites.py:332`'s
   `not-orderable` row stays green and unchanged. A new row beside it, an unordered `enum`, is
   refused with `REGRESSION_PROPERTY_INVALID`.
5. **Levels are swept in declared order:** a planted inversion between two adjacent declared
   levels is reported as a counterexample naming those two levels.
6. **The contracts carry `ordered`:** `uv run python scripts/generate-contracts.py --check` exits
   0; `grep -c '"ordered"' docs/contracts/schemas/rating-algorithm.schema.json` ≥ 1 (R5.6); and
   `pnpm --dir frontend generate:api` leaves tracked files clean.
7. **S5 typed nothing on the bulk-operation route and re-added no guard entry:**
   `git diff origin/main...<S5 branch> -- backend/src/app/api/rate_tables.py` changes no line of
   the bulk-operation handler, and `grep -n 'bulk-operation' backend/tests/test_contracts.py`
   shows no entry in either pending list.
8. **The drift rule held:** S5's `LG-` names which of S5/S6 merged second. Whichever did shows its
   quote-form tests and `pnpm --dir frontend type-check` green on a merge tree that contains the
   other.

## Global Constraints

`PL-1546`'s apply unchanged. In addition:
- `CLAUDE.md` §2: the generated contract is regenerated on the merge base, never hand-merged.
  The authored `rating-algorithm.schema.json` is the one hand-edited contract here (R5.6).
- `RL-1613`'s rule: *"a runtime change must not reprice or rehash an unchanged bundle"*.

## Hand-off (not this plan's writes)

- **`SL-1547`'s roadmap row** names "the FD-1366 bulk-operation typing slice merged" as a need.
  At this delta's mint, the minter appends a dated line naming SL-1669's minted id and this
  delta. The planner may write it, since it cut that row, but a minted id is needed first.
- **WK-675's roadmap row** lists this delta (the lead's or the D13 minter's).
- **The fallback trigger** (R5.3) is the lead's to watch at `SL-1548`'s merge.

## Self-review

- **Coverage of RL-1613.** Item 2's five bullets map to R5.4, and item 2's hash conditions
  (i)–(iv) map to Acceptance 1–2. Item 3 maps to R5.4 and R5.6. The *Acceptance* section's six
  violations map to Acceptance 1–6.
- **The ask.** The 02:51:32 item (2) overlap is R5.9. The 02:53:52 drift rule is R5.8. The
  02:58:33 condition 4 dependency is need 4 and R5.3.
- **Two facts RL-1613 did not have:** SL-1600 has merged (R5.5), and the authored contract is not
  generated (R5.6). Each is a locator correction, stated where it applies (convention 5), not a
  change to the ruling.
- **Literals.** Every `file:line` was read at `fc4401dc`. The `RL-1613` line ranges are its own
  lines on `main`.
- **Convention 4.** `gh pr list --state open` (~02:50 BST) returned only #1289. The to-lead
  entries from 2026-10-08 to 02:58:33 were read for this subject: 10:55:02, 11:00:57 (RL-1613's
  source), 02:51:32, 02:53:52 and 02:58:33.
