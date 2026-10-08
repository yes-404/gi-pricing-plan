---
id: PL-1499
family: plan
kind: leaf
title: WK-673 Slice 5 — the approval gate, part one, structural_diff, FR-257 limb (2), FR-224: leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: planner
tree: 137bc817ef1fb40ea57e9053e0ad40b73bdff3a8
phase: P2
work: WK-673
slice: SL-1389
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-1389, PL-1267, PL-1371, RL-1184, RL-1263, RL-1264, RL-881, SL-1256, SL-1388, SL-1390]
---

# PL-1499 — WK-673 Slice 5: the approval gate, part one — `structural_diff`, FR-257 limb (2), FR-224: leaf plan

*(Minted 2026-10-08 as PL-1499 from working id 9590, in the T8 batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor is spawned from `.claude/roles/executor.md` and also
> binds `test-driven-development` (every task is red first), `python-package` and
> `contract-schema` (Tasks 2 and 5: `model-schema` shape changes), `python-test`
> (requirement markers that name the limb, negative tests), `spec-change` (Task 1),
> `fastapi-service`, `dev-commands` (the two-half gate) and `git-hygiene`. Read
> [`README.md`](README.md)'s five unchecked conventions before the first step.

Filed under working id **9590**, reserved by the lead and named in the lead's brief
`~/gi-pricing-plan.local/handover/brief-prep-wave-2026-10-05.md`, section AQ (written for
planner-673s46). Drafted from 17:01:31 BST (`TZ=Europe/London date`) on 2026-10-05 against
origin/main `137bc817ef1fb40ea57e9053e0ad40b73bdff3a8`. Every locator below was read at that
tree unless another tree or a branch head is named. Unminted records are cited by working id
and kept out of `relates:` (check 32): PL-1500 (WK-673 Slice 4, draft #1176, head
`ac8221ec`), PL-1452 (Slice 3, #1138), PL-1447 (the FD-1420 fix, WK-673, #1145, head
`2f3269c8`), PL-1429 (the FD-1421 fix, WK-1178, #1140, head `f18549bb`), PL-1471 (the FR-240
family fix, WK-673, #1152), PL 9616 (the FD-1416 fix, #1168, head `0b60c81b`), PL 9629 (the
exit-demo plan, #1164, head `68dd997c`), RL 9614 (FD-1244 and FD-1245, #1167, head
`b71f0da2`), RL 9607 (PL 9616's ruling), RL-1445 (the RL-1263 amendment, #1162).

### Pre-mint edit, 2026-10-05

Edited 2026-10-05 from 17:40:00 BST (`TZ=Europe/London date`), before this plan's mint, by the
planner, on the ruling of the maintainer (by delegation) in
`~/gi-pricing-plan.local/channel/to-lead.md`, entry "## 2026-10-05 17:34:57 BST — E1 DPs (dm-e1
memo handover/dp-memo-e1-2026-10-05.md): all six ADOPTED as recommended; S1 yes; S2 yes; PL 9578
noted". Its record is RL-1497 (then a working id, filed by dm-e1). Its lines that bear on this plan,
verbatim:

> DP-E1-6 (a): S5's submit_for_review WRITES row.change_summary, with a red test. Checked: docs/contracts/schemas/rating-version.schema.json:8 lists change_summary as required and :36 sets minLength 1.
>   THE RESIDUE IS NAMED, NOT FIXED HERE: the schema requires the field on EVERY rating version, but a draft row carries null until submit, so (a) closes it only from submit onward. The RL records this as the F27 schema-vs-code gap that it is, and it is carried by F27's owner. It does not widen E1 or S5.
> S1: YES. DP-E1-6 (a) goes into PL 9590's scope (#1181; submit_for_review is already in its write set; contention unchanged). It is a pre-mint edit and is named in PL 9590's dispatch.

The evidence is dm-e1's memo `~/gi-pricing-plan.local/handover/dp-memo-e1-2026-10-05.md`
§"DP-E1-6", at origin/main `4d3be141`; `backend/src/app/platform/rating_versions.py`,
`packages/model-schema/src/model_schema/rating.py` and `backend/src/app/api/models.py` are
byte-identical at `137bc817` and `4d3be141` (`git diff --stat 137bc817 4d3be141 -- <the three>`
prints nothing), so the locators below hold at both. What this edit changed, each marked in
place with a dated note, nothing deleted:

1. **Scope gains one write** (§"Scope", premise m, new Task 7, new Acceptance 14):
   `submit_for_review` assigns `row.change_summary = change_summary` beside the evidence write
   (`:322-326`), so the version carries the summary it was submitted with (`03` FR-242, "Rating
   Versions carry a required change summary"; `03` §4.3's example, `03:386`). A resubmission
   overwrites it, as the evidence write already does.
2. **The write set is unchanged.** The path and the symbol are already in §"Write set":
   `backend/src/app/platform/rating_versions.py`, `submit_for_review` (`:278-338`), named at
   this plan's premise a (`:183` before this edit), its write-set row (`:220` before this edit)
   and Task 2's Files (`:323` before this edit). The test goes in `backend/tests/test_rating_versions.py`, already in
   the write set for the shared fixture. No path, symbol or spec section is added.
3. **The contention is unchanged**, including with E1 (SL-1502, PL-1501, #1194, both working
   ids): E1 adds `draft_change_summary_for` to `rating_versions.py` (a different function), and
   neither reads nor writes `RatingVersion.change_summary` (its Acceptance 14 only asserts its
   own GET leaves the field unchanged). RL-1445 condition 2 still holds both ways: (a) every
   shared path is one-sided or exempt; (b) neither slice consumes the other's output. Both
   dispatch records name the pair (the 17:28:27 BST entry).
4. **Out of scope, named: the F27 draft residue.** The hand-authored
   `docs/contracts/schemas/rating-version.schema.json` requires `change_summary` (`:8`,
   `minLength` 1 at `:36`) on every version, while a `draft` row carries null until submit.
   This write closes that only from submit onward. The rest is register finding F27's
   schema-vs-code gap (`docs/findings/register.md:69` at `4d3be141`), carried by F27's owner,
   not this slice.

### Second pre-mint edit, 2026-10-05: RL-1503

Edited 2026-10-05 from 18:40:26 BST (`TZ=Europe/London date`), before this plan's mint, by the
planner, on the lead's brief `~/gi-pricing-plan.local/handover/brief-capacity-fill-2026-10-05.md`
Part B. The authority is **RL-1503** (then a working id, #1191, head
`7bbdd9c076e6e69f9824770a7dddf299bf65caa6`, filed, unminted). It rules this plan's DP-S5-1 to
DP-S5-5 (its §"Ruled", items 6 to 10, lines 120–159 at that head) and states what this slice
owes (§"What it obliges", lines 285–297). Its one text addressed to the planner is **C1**
(lines 264–273: "The planner applies C1 before the mint"). Its texts **T3, T4 and T5** (lines
239–262) are the slice's to apply with the code: T3 adopts this plan's P1 unchanged; T4 and T5
amend P2 and P3 for the ruled default and the unset rule. Nothing is re-decided here. Each edit
below carries the RL-1503 item it applies and is marked in place.

1. **C1, applied byte for byte.** Premise h's evidence cell now lists `Environment`'s fields
   as read at `4d3be141` (`model_schema/deployments.py:55`; re-read for this edit, the class
   holds exactly those seven fields). DP-S5-1 option (c) now reads "the Environment with the
   highest `promotion_order`". The conclusion is unchanged.
2. **The five decision points are ruled** (§"Status", activation need 4 and §"Decision
   points"). DP-S5-1 (a), item 6. DP-S5-2 (a) amended, item 7: the default is the maintainer's
   option D, `{quantile: 0.99, max_abs_change_pct: 10}`, and **an entry that leaves the field
   unset is governed by the default, not refused**. This replaces the "`None` fails closed"
   reading of (a). No value switches the gate off. DP-S5-3 (a), item 8. DP-S5-4 (a), item 9.
   DP-S5-5 (a), item 10. Need 4 still waits on RL-1503's mint.
3. **Task 1 applies RL-1503's T3, T4 and T5, never this plan's Appendix.** The Appendix is
   marked as ruled.
4. **Two acceptance items are added from RL-1503's own text.** Acceptance 15 is its
   "Acceptance" bullet "The threshold (DP-S5-2)". Acceptance 16 is item 7's condition (ii): the
   ledger records the observed quantiles of the slice's first freMTPL2 run. Task 5 Step 3 and
   Task 6 Step 2 name them.
5. **The write set is unchanged.** `DEFAULT_POLICY`'s `rating_version` entry is already in it
   (§"Write set", the `approvals.py` row); the default's value changes, and the path and symbol
   do not. The contention is unchanged.
6. **Found, not decided: §4.6's dated note has no ruled text.** §"Write set" and Task 1's Files
   name a dated `03` §4.6 note for DP-S5-3 and DP-S5-4. RL-1503 gives T3 to T5 only, and T4 cites
   §4.6 for the observed figure. Under this plan's own rule ("the ruled texts"), Task 1 writes
   no §4.6 text unless a ruling supplies one. This is reported to the lead.

**Counts, per edit**, by `str.count` on this file before and after the edit set (each find
string exactly 1 before; an insertion keeps its anchor, so its find string stays 1). The
strings are not repeated here, so the count stays true.

| Edit | Find string | New text |
|---|---|---|
| delta section (new) | 1 → 1 | 0 → 1 |
| C1 premise h | 1 → 0 | 0 → 1 |
| Status sentence | 1 → 0 | 0 → 1 |
| need 4 | 1 → 1 | 0 → 1 |
| DP-S5-1 cell | 1 → 0 | 0 → 1 |
| DP-S5-2 cell | 1 → 0 | 0 → 1 |
| DP-S5-3 cell | 1 → 0 | 0 → 1 |
| DP-S5-4 cell | 1 → 0 | 0 → 1 |
| DP-S5-5 cell | 1 → 0 | 0 → 1 |
| C1 DP-S5-1 (c) | 1 → 0 | 0 → 1 |
| Task 1 Step 1 | 1 → 0 | 0 → 1 |
| Acceptance 15, 16 (new) | 1 → 1 | 0 → 1 |
| Task 5 Step 3 | 1 → 1 | 0 → 1 |
| Task 6 Step 2 | 1 → 0 | 0 → 1 |
| Appendix header | 1 → 1 | 0 → 1 |

### Third pre-mint edit, 2026-10-05: RL-1503 T7 and its three reds

Edited 2026-10-05 from 18:57:14 BST (`TZ=Europe/London date`), before this plan's mint, by the
planner, on the lead's brief `~/gi-pricing-plan.local/handover/brief-t7-accept-2026-10-05.md`
Part B. The authority is the maintainer (by delegation), `~/gi-pricing-plan.local/channel/to-lead.md`,
entry "## 2026-10-05 18:54:06 BST — RL 9566 T7 (#1191 @bb70663b): case (a) accepted; T7's three
choices ACCEPTED; the recurring cd: fix the role files". Its lines that bear on this plan,
verbatim:

> T7's three choices are ACCEPTED as the maintainer's (by delegation), each to be named in the RL as such:
>  (1) NEAREST RANK at ⌈q × n⌉, with "1" = the max; exact on integers.
>  (2) The decimal string rounded ONCE to 6 places TOWARD +∞: conservative for an upper-bound gate (the values are absolute changes, so non-negative).
>  (3) n = 0: every value null, and FR-224's gate REFUSES the run (no vacuous pass).
> Each gets a red in S5: a nearest-rank case where interpolation would differ; a value whose 7th place would round DOWN under half-even (proving +∞); an empty banded set refused.

The text applied is **RL-1503's T7** (working id, #1191, read at head
`bb70663b405dab9f219417f6789df68ffeef7934`, lines 276–291: `03` §4.6, inside "Bands and
movers", find ``an empty band has `policies` 0. A **mover** is``, counted once at `ecbd1954`).
Its §"What it obliges" (line 320 at that head) reads "Slice 5 (PL-1499) applies T3 to T5 and
T7". Nothing is re-decided here. Each edit below is marked in place.

1. **Three acceptance items, each red first with its exact fixture** (Acceptance 17, 18, 19).
   Each is also shown red on a deliberately broken variant of the code that makes the other
   choice, scratch-reverted, so the red proves the ruled choice and not only a missing field.
   The figures were checked in the repository's environment (Python 3.12, `decimal`, Polars
   1.44.2 as `uv.lock` pins it): on the absolute changes 1, 2, 3, 4,
   `pl.Series.quantile(0.5, "linear")` is 2.5, Polars' default `quantile(0.5)` (interpolation
   `nearest`) is 3.0, and nearest rank is 2; 100/3 quantized to 6 places is `33.333333` under
   `ROUND_HALF_EVEN` and `33.333334` under `ROUND_CEILING`.
2. **Task 4 owns them** (it computes `abs_change_pct_quantiles`); Acceptance 19's gate half is
   Task 5's. Task 4 Step 3's quantile clause now follows T7: the banded set, not "quoted in
   both", is what n counts.
3. **Task 1 applies T7 with T3 to T5.** This answers the second pre-mint edit's item 6: a ruling
   now supplies the §4.6 text, so the write-set row and Task 1's §4.6 mention stand.
4. **The write set gains no path.** The three tests go in `G`, already new in §"Write set";
   its row's Acceptance list gains 17–19. The contention is unchanged.

**Counts, per edit**, by `str.count` on this file before and after the edit set (each find
string exactly 1 before; an insertion keeps its anchor, so its find string stays 1).

| Edit | Find string | New text |
|---|---|---|
| delta section (new) | 1 → 1 | 0 → 1 |
| Acceptance 17–19 (new) | 1 → 1 | 0 → 1 |
| write set `G` row | 1 → 0 | 0 → 1 |
| Task 1 Step 1 | 1 → 0 | 0 → 1 |
| Task 4 Step 1 | 1 → 1 | 0 → 1 |
| Task 4 Step 3 | 1 → 0 | 0 → 1 |
| Task 5 Step 1 | 1 → 0 | 0 → 1 |
| Task 6 Step 2 | 1 → 1 | 0 → 1 |
| self-review item 8 (new) | 1 → 1 | 0 → 1 |

### Fourth pre-mint edit, 2026-10-05: the two test files the write set missed

Edited 2026-10-05 from 19:01:25 BST (`TZ=Europe/London date`), before this plan's mint, by the
planner, on the lead's (team-lead) message to the planner after the third pre-mint edit
(head `619e2b8b`): "Task 4's Files name backend/tests/test_dislocation_runs.py and
packages/model-schema/tests/test_dislocation.py, but the write set table lists neither."
Both are real writes of Task 4 Step 1, so the write set gains them; Task 4 is unchanged.

1. **`packages/model-schema/tests/test_dislocation.py`: appended.** The file exists at
   `ecbd1954` (Slice 2, `PL-1403`). Task 4 Step 1 appends the `DislocationSpec` test (an
   `exact` override with `baseline_ref != candidate_ref` refused). **Slice 3** (PL-1452, #1138,
   head `e810b785`) also edits it: `_SLICE_3_FIELDS`, `_NULLABLE` and
   `test_dislocation_run_fields_match_the_hand_authored_contract` (`:161` at `ecbd1954`; its
   write-set row, Acceptance 17). Slice 4 (PL-1500, #1176, head `f229528f`) does not name it.
   Shared with SL-1387, serial through Slice 4 (activation need 2), the same order as the
   existing `dislocation.py` row: S3, then S4, then S5.
2. **`backend/tests/test_dislocation_runs.py`: appended; created by Slice 4.** It is not on
   `ecbd1954`. PL-1500 (#1176, head `f229528f`) creates it (its write set: "new", Acceptance
   1–8; its `B`). Task 4 Step 1 appends the handler tests (the exact-mode run writes no
   `rating_versions` row; the six quantile keys). **Shared with SL-1388**: Slice 4 creates it and
   merges first; this slice appends after, on a tree where it exists (activation need 2).
3. **Sweep.** Every open PR's added lines, read at 19:00 BST, were searched for both paths
   (`gh pr diff <n> | grep '^+' | grep -c 'tests/test_dislocation\.py\|tests/test_dislocation_runs\.py'`):
   #1181 (this plan), #1176 (PL-1500) and #1138 (PL-1452) only. On main, `docs/plans/` names
   `test_dislocation.py` in `PL-1403` (Slice 2) and this plan only.
4. **The contention table gains two rows**, both SERIAL through activation need 2; no new pair.

## Goal

Make `submit_for_review` (`backend/src/app/platform/rating_versions.py:278`) enforce three
more things before it opens the Approval Request: **`structural_diff`** — FR-219's diff
computed at submission, persisted as a content-addressed blob into
`RatingVersionEvidence.structural_diff_blob`, with a verifier for the kind (`06` FR-364's
2026-09-28 amendment, `RL-1184` E4); **FR-257 limb (2)** — a Dislocation Run (Slice 4's row)
whose candidate is this version at its current bundle hash and whose baseline is the current
live version, refused with `EVIDENCE_INCOMPLETE` otherwise; and **FR-224** — for an
`approximation`-mode version, a Dislocation Run whose baseline is the same version in `exact`
mode, inside the threshold on the `rating_version` `ApprovalPolicyEntry` (`RL-1264` DP-3 (b)),
never read from Settings, with FR-136's fidelity statement as the cheap pre-check.

**Architecture.** The gate stays a sequence of direct checks in `submit_for_review`, after
`_regression_run_gate` (`:317`) and before `approvals.submit` (`:327`), each writing its
evidence id into `row.evidence` as `:322-326` does. Slice 6 replaces the direct checks with
the `effective_evidence` floor loop; this slice writes each check as a function Slice 6's
`verifiable` map can call. The threshold is a `model-schema` field, generated to
`docs/contracts/`.

**Tech stack.** Python 3.12, Pydantic v2, SQLAlchemy 2 async, Polars. No new dependency.

**Spec.** [`03-rating-engine.md`](../specs/03-rating-engine.md) FR-219 (`:88`), FR-223 and
FR-224 (`:109-110`, in §3.2, not §3.1 as `PL-1267`'s scope table says), FR-238 (`:135`),
FR-257 (`:174`), §4.6 (`:514`); [`02-modelling.md`](../specs/02-modelling.md) FR-136
(`:195`); [`06-governance.md`](../specs/06-governance.md) FR-364 (`:145`, the 2026-09-28
amendment) and §4.2 (`:344`); `RL-1264` (DP-3 (b), and its negative test).

## Status

`draft`. **The five decision points are ruled by RL-1503** (then a working id, #1191, unminted; pre-mint 2026-10-05; §"Second pre-mint edit"); until its mint they still block
(activation need 4). The plan moves to `active` only through a separate activation PR, after every
need below holds.

### Activation needs, in order

1. **This plan is merged, minted and made `active` by a dated line.**
2. **`SL-1388` (Slice 4) is closed.** This slice reads its `DislocationRunRow` and
   `fetch_run`, edits its `dislocation.run` handler (DP-S5-4) and its `POST` validation
   (DP-S5-3), and uses its `WorkspaceResolver` (PL-1500 Task 3). Where Slice 4's merged code
   differs from this plan, the merged code governs and the dispatch record names each
   difference.
3. **`SL-1256` (WK-674 Slice 2) is closed** — met at `137bc817` (`docs/roadmap.md`, the
   `SL-1256` row, `status: closed`). Premise j of `PL-1267`: nothing is `live` without its
   Deployment record.
4. **A ruling on DP-S5-1 to DP-S5-5** is merged and minted, adopting or amending the texts
   in §"Appendix". An unminted ruling is a stop. *(That ruling is RL-1503, #1191: it adopts P1 as
   its T3 and amends P2 and P3 as its T4 and T5; pre-mint 2026-10-05; §"Second pre-mint edit".)*
5. **RL 9614 (working id, #1167) is minted.** Its DP-2 (a) keeps FR-257's gate at
   `POST /rating-versions/{id}/submit` (FD-1245); this slice builds there. If the minted text
   moves the gate, the slice follows it (`PL-1267` Slice 5).
6. **The lane is free under `RL-1263`** as RL-1445 amends it, with the same-Work conditions
   in the dispatch record (§"Contention").
7. **The maintainer's dispatch GO**, and the lead's go in a separate activation PR.

## Acceptance Standard

Each item is a named test or command a fresh reviewer can re-run, in the executor's own
worktree, against `origin/main...HEAD`. Every test is shown red before its code exists, and
the ledger quotes the red by its cause (README convention 2). `S` is
`backend/tests/test_rating_versions.py`; `G` is the new `backend/tests/test_rating_version_dislocation_gate.py`;
`M` is `packages/model-schema/tests/test_approvals.py`.

1. **`structural_diff` is persisted at submission.** `G::test_submission_persists_the_structural_diff_as_a_blob`:
   after a successful submit, `row.evidence["structural_diff_blob"]` names a stored blob whose
   bytes are `AlgorithmDiff.model_dump_json()` of the ruled baseline's algorithm against this
   version's (DP-S5-1), and `structural_diff_verified(row)` returns `True`.
2. **FR-257 limb (2) refuses**, each a named test with `@pytest.mark.req("FR-257")` and a
   docstring naming limb (2) only (the register row's requirement):
   `G::test_limb_2_refuses_with_no_dislocation_run`,
   `G::test_limb_2_refuses_a_run_on_a_stale_candidate_bundle_hash`,
   `G::test_limb_2_refuses_a_run_whose_baseline_is_not_the_current_live_version`. Each answers
   422 `EVIDENCE_INCOMPLETE` whose `detail` names the limb and the reason; a 422 with another
   code or reason is a plan defect.
3. **FR-257 limb (2) accepts the right run** and records it:
   `G::test_limb_2_accepts_a_run_against_the_live_version_and_records_it`:
   `row.evidence["dislocation_run_id"]` equals the run's id.
4. **The first-version case** follows DP-S5-1's ruling:
   `G::test_limb_2_with_nothing_live_<ruled behaviour>`.
5. **FR-224 refuses above the threshold**, naming the quantile and the observed deviation
   (`03:110`): `G::test_fr224_refuses_an_approximation_version_above_the_threshold`;
   `G::test_fr224_refuses_an_approximation_version_with_no_exact_baseline_run`; and
   `G::test_fr224_accepts_inside_the_threshold_and_records_the_figures`. An `exact`-mode version
   is untouched: `G::test_fr224_does_not_apply_to_an_exact_mode_version`.
6. **The threshold is never read from Settings** (`RL-1264`'s named violation, this slice's):
   `G::test_fr224_threshold_ignores_environment_variables`: with
   `GIP_APPROVAL_DEVIATION_THRESHOLD` and every `GIP_`-prefixed variable a Settings field
   could map to set to a permissive value, a version above the policy's threshold is still
   refused. Shown red on a deliberately broken gate that reads the threshold from
   `load_settings()` (`backend/src/app/config.py:270`), scratch-reverted.
7. **The threshold field is validated.** `M::test_the_deviation_threshold_is_only_on_rating_version_entries`
   and `M::test_the_deviation_threshold_bounds` (the ruled shape, DP-S5-2).
8. **FR-136's pre-check runs first** (DP-S5-5): `G::test_fr136_precheck_refuses_before_any_run`
   (the ruled refusal, at the ruled place).
9. **Every new refusal surfaces before `approvals.submit`**: no Approval Request row exists after
   any refusal in items 2, 4–6 and 8 (asserted in each test).
10. **The existing gate is unchanged.** `uv run pytest backend/tests/test_rating_versions.py
    backend/tests/test_regression_runs.py -q` passes, with existing submit tests given the
    evidence they now need through one shared fixture (named in the ledger), not by weakening
    any assertion.
11. **Contracts.** `uv run python scripts/generate-contracts.py --check` exits 0;
    `uv run pytest backend/tests/test_contracts.py -q` passes.
12. **The two-half gate** passes on the slice head, and the four docs checks with their rc and
    summary lines quoted.
13. **The slice closes on the maintainer's MERGE-ACK and a clean audit** (`PL-1267`
    Acceptance 8).
14. **The version carries the summary it was submitted with** *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)*
    `S::test_submit_writes_the_change_summary_on_the_version`, `@pytest.mark.req("FR-242")`:
    a submit with `change_summary="<text>"`, through the shared fixture (Acceptance 10),
    answers with `change_summary == "<text>"`, and a later `GET /api/v1/rating-versions/{id}`
    carries the same text. Red first: the submit response's `change_summary` is `None`
    (`AssertionError` on `None == "<text>"`), because nothing writes the field (premise m). A
    red for any other cause, a gate refusal included, is a fixture defect.
15. **An unset threshold is governed by the default** (RL-1503 item 7 and its "Acceptance" bullet
    "The threshold (DP-S5-2)"; pre-mint 2026-10-05; §"Second pre-mint edit").
    `G::test_fr224_an_unset_threshold_is_governed_by_the_default`: with the `rating_version`
    entry's `approximation_deviation` unset, a run whose observed 0.99 quantile is above 10 % is
    refused at submission and one at or below is accepted; a workspace entry of
    `{quantile: 0.99, max_abs_change_pct: 5}` refuses the second run too. Shown red on a
    deliberately broken gate that reads an unset entry as "no gate", scratch-reverted.
16. **The default is re-readable** (RL-1503 item 7, condition (ii); pre-mint 2026-10-05; §"Second pre-mint edit"). The ledger records the
    observed `abs_change_pct_quantiles` (the six keys of item 9) of the slice's first Dislocation
    Run on freMTPL2 (`examples/fremtpl2/`), with the tree and the run's spec, for the
    maintainer's re-read at the next checkpoint.
17. **The quantiles are nearest rank, never interpolated** (RL-1503 T7, choice (1); pre-mint 2026-10-05, T7; §"Third pre-mint edit").
    `G::test_quantiles_are_nearest_rank_not_interpolated`, `@pytest.mark.req("FR-224")`.
    Fixture: four policies, each quoted in both with baseline payable premium `10000` minor
    units; candidate `9900`, `10200`, `9700`, `10400`. The changes are −1, +2, −3, +4 %, so the
    banded set's absolute changes are 1, 2, 3, 4 (n = 4). Expected `abs_change_pct_quantiles`:
    `"0.5"` → `"2.000000"` (rank ⌈0.5 × 4⌉ = 2), `"0.9"` → `"4.000000"` (rank ⌈3.6⌉ = 4), and
    `"0.95"`, `"0.99"`, `"0.999"`, `"1"` → `"4.000000"`. Linear interpolation gives 2.5 and 3.7;
    Polars' default `quantile` gives 3.0 at 0.5; a signed (not absolute) order gives −1 at 0.5.
    Red first: the field is absent. Then red on a broken variant that takes
    `pl.Series.quantile(q, "linear")`: `"2.500000" != "2.000000"`; scratch-reverted, both quoted.
18. **Rounding is once, to 6 places, toward +∞** (RL-1503 T7, choice (2); pre-mint 2026-10-05, T7; §"Third pre-mint edit").
    `G::test_quantiles_round_once_toward_positive_infinity`, `@pytest.mark.req("FR-224")`.
    Fixture: two policies quoted in both: baseline `30000`, candidate `40000` (+100/3 %, exactly
    33.333…, so the 7th place is 3 and half-even rounds it **down**); baseline `10000`,
    candidate `11000` (+10 %, exact at 6 places). n = 2. Expected: `"0.5"` → `"10.000000"`
    (rank 1; an exact value is not moved), and `"0.9"`, `"0.95"`, `"0.99"`, `"0.999"`, `"1"` →
    `"33.333334"` (rank 2). Red first: the field is absent. Then red on a broken variant that
    quantizes with `ROUND_HALF_EVEN`: `"33.333333" != "33.333334"`; scratch-reverted, both
    quoted. A variant that adds `0.000001` unconditionally fails on `"10.000001"`.
19. **An empty banded set has no figure, and FR-224's gate refuses it** (RL-1503 T7, choice
    (3); pre-mint 2026-10-05, T7; §"Third pre-mint edit"). `G::test_an_empty_banded_set_has_null_quantiles_and_fr224_refuses`,
    `@pytest.mark.req("FR-224")`. Fixture: two policies quoted in both, each with baseline
    payable premium `0` (both counted in `zero_baseline`), candidate `5000`; the banded set is
    empty (n = 0, `03` §4.6 "Outcomes, and the two sets"). Expected (run half, Task 4): the run
    completes, and `abs_change_pct_quantiles` holds all six keys, each `null` (no key omitted).
    Expected (gate half, Task 5): an `approximation`-mode version whose exact-mode baseline run
    carries that map, under the default threshold, is refused as Acceptance 5's refusal is,
    the detail naming the quantile and that the run has no figure; no Approval Request row
    exists (Acceptance 9). Red first: the field is absent, then the submission succeeds. Then
    red on a broken gate that reads `null` as 0: the submission is accepted; scratch-reverted,
    both quoted.

## Global Constraints

- **Money is integer minor units** (`CLAUDE.md` §7). The deviation is a **percentage** (a
  derived view, `PL-1267` Global Constraints), compared to a percentage threshold; no money
  figure is a float.
- **The threshold lives on the `rating_version` `ApprovalPolicyEntry`, never in Settings**
  (`RL-1264` DP-3 (b)): no code path from `load_settings()`, `workspace_settings` or an
  environment variable reaches it.
- **Nobody hand-writes a shape `model-schema` owns** (`CLAUDE.md` §2): the field, the
  evidence additions and any `DislocationSpec` change are `model-schema` changes, generated.
- **`submit_for_review`'s refusals fail closed** (R4): a check that cannot decide refuses.
- **Requirement markers name the limb** for FR-257 (`PL-1267` Acceptance 2).
- **No new permission.** The existing `rating:submit` check (`rating_versions.py:297`) governs
  every new check (`PL-1267` Global Constraints).

## Scope

### Requirement coverage, each id individually

| Id | Where | What this slice builds | Task |
|---|---|---|---|
| FR-364 (`06`) | `06:145`, 2026-09-28 amendment | `structural_diff` persisted at submission and its verifier | 2 |
| FR-219 | `03:88` | the diff "attached to the approval request" (as evidence) | 2 |
| FR-257 limb (2) | `03:174` | a Dislocation Run against the current live version over an agreed portfolio | 3 |
| FR-224 | `03:110` | the `approximation`-mode gate, its threshold on the policy entry, FR-136 first | 4, 5 |
| FR-136 (`02`) | `02:195` | its statement as the pre-check, surfaced, never the gate | 4 |
| FR-242 (pre-mint 2026-10-05, DP-E1-6 (a)) | `03:139` | the version carries the submitted summary: `submit_for_review` writes `row.change_summary` | 7 |

**Not in scope:** the floor wiring (`effective_evidence("rating_version")`), Slice 6;
FR-257 limbs (1), (3), (4) (`PL-1267` Scope); FR-242's drafted change summary (see
§"Needs this slice serves"). *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* Also not in scope: the F27 draft residue (a
`draft` row's `change_summary` is null while `rating-version.schema.json` requires it), which
is F27's.

### Premises read at `137bc817`

| # | Premise | At `137bc817` | Status |
|---|---|---|---|
| a | The submit sequence | `submit_for_review` (`rating_versions.py:278`): permission `:297`, load `:303`, `DRAFT` only `:306-312`, `_golden_quote_gate` `:314`, `_regression_run_gate` `:317`, evidence written `:322-326`, `approvals.submit` `:327`, status `REVIEW` `:334-335` | reproduces |
| b | The refusal helper | `_evidence_incomplete(ref, why)` (`:687-689`): `PlatformError("EVIDENCE_INCOMPLETE", "Required evidence is missing", 422, f"{ref}: {why}.")` | reproduces |
| c | The evidence fields exist | `RatingVersionEvidence` (`model_schema/rating.py:119`): `dislocation_run_id: UUID \| None` (`:125`), `structural_diff_blob: str \| None` (`:127`) | reproduces |
| d | The diff | `diff_algorithms(old, new) -> AlgorithmDiff` (`model_schema/rating.py:571`); Slice 3 adds `input_contract_deltas` and `output_deltas` (PL-1452 DP-S3-2 (a)) | reproduces |
| e | No threshold field | `ApprovalPolicyEntry` (`model_schema/approvals.py:125`): `artifact_type`, `approvers_required`, `approver_roles`, `environment`, `evidence`, `skippable_predecessors` (validator `:147`) | reproduces (`RL-1264` premise note) |
| f | No public live resolution | `_live_by_environment` (`backend/src/app/platform/environments.py:67`) is private; `DeploymentRow.rating_version_ref` (`db/models.py:2490`) | reproduces; Task 3 adds a public reader |
| g | `live` is per Environment | FR-238 (`03:135`): "the same Rating Version can be `live` in `uat` and not in `prod`"; FR-257 does not name an Environment | reproduces; DP-S5-1 |
| h | No production marker on an Environment | `Environment` (`model_schema/deployments.py:55`): `slug`, `name`, `description`, `promotion_order`, `requires_prior_environment`, `retired_at`, `live_deployments`; no production marker *(RL-1503 C1, read at `4d3be141`; pre-mint 2026-10-05; §"Second pre-mint edit".)*; `DEFAULT_POLICY`'s `deployment` entry names `environment="prod"` (`approvals.py:354-360`) | reproduces; DP-S5-1 |
| i | The mode | `ModelReferenceMode = Literal["exact", "approximation"]` (`rating.py:135`); `RatingVersion.model_reference_mode` (`:164`); Slice 3 refuses a mode difference inside `derive_changes` (PL-1452 DP-S3-9 (a)) | reproduces; `attribute` is not used for FR-224's run (DP-S5-3) |
| j | The fidelity statement is prose | `fidelity_statement(...) -> str` (`pricing_core/modelling/transparency.py:550`); its numbers (`r_squared`, `deviance_explained`) are on `GlmApproximation` | reproduces; DP-S5-5 |
| k | The run's figures | `DislocationRun` (`model_schema/dislocation.py:116`) holds bands and totals, no per-policy quantile | reproduces; DP-S5-4 |
| l | Settings' prefix | `Settings` (`backend/src/app/config.py:88`), `env_prefix="GIP_"` (`:96`) | reproduces; Acceptance 6 |
| m | `RatingVersion.change_summary` is never written (pre-mint 2026-10-05, read at `4d3be141`) | the field `rating.py:168`, the column `RatingVersionRow.change_summary` (`backend/src/app/db/models.py:1997`); `create_rating_version` builds the row without it (`rating_versions.py:254-262`); `submit_for_review` passes it only to `approvals.submit` (`:327-333`); `to_schema` (`:120`) reads it, so `submit_rating_version` (`api/models.py:1222-1229`) answers `change_summary: null` | reproduces; DP-E1-6 (a), Task 7 |

### Risks

- **Existing submit tests lack the new evidence.** Every test that submits a version now
  needs a Dislocation Run and a live version or the DP-S5-1 fallback. One shared fixture,
  added in Task 3, supplies them (Acceptance 10).
- **The exit-demo journey depends on the ruled first-version behaviour.** PL 9629's E3 ("the
  first submission is refused: the dislocation run is stale") and E4 need a run against a
  baseline. If nothing is live in the demo's `prod` at E2, DP-S5-1's ruling decides what the
  demo must seed.

## Write set, and its contention (`RL-1263`, RL-1445)

Classes as in PL-1500 §"Write set" (`docs/process/delivery-process.core.json`
`guards.parallelism.build_slices_across_works.no_shared_files`).

### By file and symbol, at `137bc817`

| Path | Symbol or region | Change |
|---|---|---|
| `docs/specs/03-rating-engine.md` | FR-224 row `:110` (§3.2); FR-257 row `:174` (§3.8); §4.6 (a dated note, DP-S5-3 and DP-S5-4) | the ruled texts |
| `docs/specs/06-governance.md` | §4.2 (`:344-…`): the threshold field's dated note; the `rating_version` entry's example | the ruled texts |
| `packages/model-schema/src/model_schema/approvals.py` | `ApprovalPolicyEntry` (`:125-164`), its validator; `DEFAULT_POLICY`'s `rating_version` entry (`:344-349`) | one field + its rule; the default |
| `packages/model-schema/src/model_schema/rating.py` | `RatingVersionEvidence` (`:119-132`) | the FR-224 record (DP-S5-4) |
| `packages/model-schema/src/model_schema/dislocation.py` | `DislocationSpec` (`:35`), `DislocationRun` (`:116`) | DP-S5-3 (a) and DP-S5-4 (b) fields |
| `backend/src/app/platform/rating_versions.py` | `submit_for_review` (`:278-338`) (pre-mint 2026-10-05: it also writes `row.change_summary`, DP-E1-6 (a); no new symbol); new `_structural_diff_gate`, `_dislocation_gate`, `_approximation_gate`, `structural_diff_verified`, `dislocation_run_verified` | edited; added |
| `backend/src/app/platform/environments.py` | new public `live_rating_version_ref(session, *, workspace_id, environment_slug) -> str \| None`, beside `_live_by_environment` (`:67`) | added |
| `backend/src/app/platform/dislocation_runs.py` (Slice 4) | new `latest_run_for(session, *, workspace_id, candidate_ref, candidate_bundle_hash, baseline_ref)` | added |
| `backend/src/app/worker/dislocation_handlers.py` (Slice 4) | `_dislocation_run`: the exact-mode baseline (DP-S5-3) and the quantiles (DP-S5-4) | edited |
| `backend/src/app/api/dislocation_runs.py` (Slice 4) | `POST`'s validation (DP-S5-3, DP-S5-5) | edited |
| `docs/contracts/` generated files | regenerated | |
| `backend/tests/test_rating_version_dislocation_gate.py` | new | Acceptance 1–9; 17–19 (pre-mint 2026-10-05, T7; §"Third pre-mint edit") |
| `backend/tests/test_rating_versions.py`, `backend/tests/conftest.py` or the module's fixture file | the shared fixture (Acceptance 10); Acceptance 14's test (pre-mint 2026-10-05) | edited |
| `packages/model-schema/tests/test_approvals.py` | new tests | Acceptance 7 |
| `packages/model-schema/tests/test_dislocation.py` | Task 4 Step 1's `DislocationSpec` test (pre-mint 2026-10-05, write-set gap; §"Fourth pre-mint edit") | appended; shared with SL-1387 (§"Contention") |
| `backend/tests/test_dislocation_runs.py` (created by Slice 4, PL-1500) | Task 4 Step 1's handler tests (pre-mint 2026-10-05, write-set gap; §"Fourth pre-mint edit") | appended after Slice 4 creates it; shared with SL-1388 (§"Contention") |
| `docs/ledgers/LG-<n>-…md`; `docs/INDEX.md` | added; regenerated | |

**Not written:** `packages/pricing-core/`; `backend/src/app/platform/approvals.py`;
`backend/src/app/errors.py` (`EVIDENCE_INCOMPLETE` exists, `:285`); `_regression_run_gate`
(Slice 6 moves its call); permissions.

### Contention

| Path | This slice | Other slice | Shared existing definition? | Class |
|---|---|---|---|---|
| Slice 4's files (`dislocation_runs.py`, `dislocation_handlers.py`, `api/dislocation_runs.py`) | edits | **SL-1388** (PL-1500, WK-673) | plan dependency: consumes Slice 4's output | **SERIAL** (activation need 2) |
| `dislocation.py`, `03` §4.6 | DP-S5-3, DP-S5-4 | **SL-1387** (PL-1452) | serial through Slice 4 | serial |
| `packages/model-schema/tests/test_dislocation.py` | appends Task 4's `DislocationSpec` test | **SL-1387** (PL-1452, #1138): `_SLICE_3_FIELDS`, `_NULLABLE`, the field-match test (`:161`) | yes: one module | **SERIAL** through Slice 4 (activation need 2): S3, S4, then S5; a hunk of this slice inside Slice 3's symbols is named in the dispatch record (pre-mint 2026-10-05, write-set gap; §"Fourth pre-mint edit") |
| `backend/tests/test_dislocation_runs.py` | appends Task 4's handler tests | **SL-1388** (PL-1500, #1176): **creates** it (Acceptance 1–8) | yes: Slice 4's new module | **SERIAL** (activation need 2): Slice 4 creates and merges first; this slice appends after (pre-mint 2026-10-05, write-set gap; §"Fourth pre-mint edit") |
| `03` §3.2 | FR-224 `:110` | **PL-1447** (the FD-1420 fix, **WK-673**, SL-1448): FR-221 `:107`; **PL-1429** (WK-1178) under its DP-1 (a): FR-223 `:109`; **A-3** (PL-1465, WK-1178, #1174 head `7b3df510`): the `model_call` row `:100`; **A-2** (PL-1464, #1178 head `477265e4`): `03` only as its ruling words it | **yes**: one section; hunks one to ten lines apart | **SERIALISES** with each (`forbidden`: the same spec section; for PL-1447 and PL-1429 the hunks are adjacent; A-3's is ten lines away but in the same section, and no dated option extends the non-adjacency allowance to this pair). A-2 joins if its ruling's text lands in §3.2. For PL-1447 (same Work) RL-1445 (a) fails, so the pair is serial |
| `03` §3.8 | FR-257 `:174` | none found | — | none |
| `model_schema/approvals.py` | `ApprovalPolicyEntry`, `DEFAULT_POLICY` | **PL 9616** (the FD-1416 fix, WK-1178): `ApprovalRequest` (`:405-431`), and `ApprovalDecision` (`:394-402`) only under its DP-5/DP-1 | no (different classes) | **ALLOWED one-sided**, the dispatch record naming the path and the check `git diff -U0 origin/main...<branch> -- packages/model-schema/src/model_schema/approvals.py` (hunks: this slice inside `:125-164` and `:344-349`; PL 9616 inside `:394-431`); the second merges main and re-gates |
| `model_schema/rating.py` | `RatingVersionEvidence` (`:119-132`) | PL-1429 (`RatingVersionCreate` after `:170`), PL 9610 (`Pins` `:65-78`, `SubGraphRef`, `AlgorithmDiff`), PL 9609, PL-1476 (`RatingAlgorithm`), PL-1419 (`RateTableDiff`) | no (different classes) | **ALLOWED one-sided**, named with the same `git diff -U0` check per pair |
| `platform/rating_versions.py` | `submit_for_review` and new private gates | **PL-1471** (WK-673): `_Resolver` (moved by Slice 4); **PL-1429**: `create_rating_version` (`:230-275`); **PL 9610**: `_Resolver` | no (different functions) | **ALLOWED one-sided**, named in the dispatch record with the `git diff -U0` check; for PL-1471 (same Work) RL-1445 (b) holds (neither consumes the other's output: this slice reads no compile behaviour PL-1471 changes) and is named both ways |
| `06` §4.2 | the threshold note, the example | **RL 9607** (PL 9616's ruling): `06` `:67`, `:483`, `:640`; **RL 9614** T3: `06` §5.1 `:558` | no (other sections) | none |
| `06` §4.2 | the threshold note (P3, after the `skippable_predecessors` note), the example's `rating_version` entry (`:360-362`) | **A-1** (PL-1461, WK-1178, #1177 head `5d5e5b8e`), **only under its DP-1 (a)**: §4.2's floor note (`:405-408`) | **yes** if A-1's DP-1 is (a): the same spec section | **SERIALISES** under A-1 DP-1 (a); none otherwise. Task 0 Step 3 records A-1's ruled option |
| `backend/tests/test_rating_versions.py` | the shared fixture used by existing submit tests | **PL-1429** adds tests to its create path; **PL 9616** asserts on approval responses | possibly the same module | **other shared path**: appends only, named in the dispatch record |
| generated files, `docs/INDEX.md` | regenerated | every shape-changing slice | — | exempt |

**Same-Work pairs, RL-1445 condition 2, both ways.** With **SL-1388**: consumes its output →
serial. With **SL-1390** (Slice 6): Slice 6 consumes this slice's gates → serial after it.
With **PL-1447**: `03` §3.2 SERIALISES → serial. (A-2 and A-3 are WK-1178, not same-Work pairs; §3.2 serialises them by the file rule.) With **PL-1471**: (a) every shared path is
one-sided or exempt, and (b) no plan dependency either way; they may run at once if the
dispatch record names both. *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* With **E1** (SL-1502, PL-1501 #1194, working ids,
filed after this plan): `rating_versions.py` one-sided (E1 adds `draft_change_summary_for`;
this slice edits `submit_for_review`), `rating.py` one-sided (E1 adds classes after
`RateTableDiff`), `api/models.py` E1 only, `03` §5.1 E1 only; (b) neither consumes the other's
output, and DP-E1-6 (a)'s write changes neither: E1 never reads or writes
`RatingVersion.change_summary`. They may run at once if both dispatch records name the pair.

### Size

About two executor days: three gates, two `model-schema` shape changes, one handler and one
route edit, and the fixture work for the existing submit tests.

## Needs this slice serves (PL 9629 #1164, its step table)

| Need | Step | What this slice provides |
|---|---|---|
| G2, PL 9629 activation need 5 | E3 the first submission is refused: the dislocation run is stale → 422 `EVIDENCE_INCOMPLETE` | Task 3 (limb (2)'s stale-hash refusal) |
| G2, need 5 | E4 re-run dislocation, resubmit → accepted | Task 3 |
| G2, need 5 (with need 6) | E9 the evidence ids on the decision | Tasks 2, 3 (the ids written to `row.evidence`) |
| G1 | WK-673 resolved | this slice |

**PL 9629's need 5 also names E1, "change summary drafted from the structural and rate
diffs"** (`03` FR-242's draft). Neither `SL-1389`'s row nor `PL-1267` Slice 5 scopes FR-242,
and FR-242 was verdicted delivered in WK-669 (`CR-838`) for its required summary; its
drafting half is not this slice's. This plan does not add it (a scope change is the
maintainer's); it is reported to the lead with PR #1176's report.
*(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* The drafting is now its own slice, SL-1502 (PL-1501, #1194, working ids); PL
9629's need 5 is re-pointed there by PL 9629's owner. This slice takes only DP-E1-6 (a), the
version's `change_summary` written at submit (Task 7).

## Decision points

Rows of kind "decision point" are the decision-maker's, resolved in one ruling that also
adopts or amends the Appendix texts. The slice may not move `draft → active` while any is open.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S5-1 | **Which version is "the current live version" (FR-257), and what when nothing is live?** `live` is per Environment (premise g) and no Environment is marked production (premise h). The structural diff (FR-219, "between two algorithm versions") needs a baseline too | (a) A new `dislocation_baseline_environment` field on the `rating_version` policy entry, default `"prod"` (the slug `DEFAULT_POLICY`'s `deployment` entry already uses); the live version there is the baseline; **with nothing live there**, the most recently approved other version of the same algorithm (`_baseline`, `rating_versions.py:704`, the golden-quote precedent) is the baseline; with neither (a first version), limb (2) is satisfied by recording `"no_baseline": "first_version"` on the evidence and the structural diff is taken against an empty algorithm. (b) Literally the Environment with slug `prod`; nothing live → refused. (c) The Environment with the highest `promotion_order` *(RL-1503 C1; pre-mint 2026-10-05; §"Second pre-mint edit".)*; nothing live → refused | **(a).** (b) and (c) refuse every first version for ever: nothing can be live before it is approved and deployed. (a)'s fallback reuses the approved-baseline rule the golden-quote gate already applies, and records the first-version case rather than hiding it. FR-257 gains a dated clarification (P1). The structural diff uses the same baseline, so the approver reads one comparison | decision point | yes — Tasks 2, 3 | **ruled (a)**, RL-1503 item 6 (pre-mint 2026-10-05; §"Second pre-mint edit") |
| DP-S5-2 | **The threshold's shape and default** (FR-224: "a maximum absolute percentage deviation at a declared portfolio quantile") | (a) `approximation_deviation: {quantile: Decimal, max_abs_change_pct: Decimal} \| None` on `ApprovalPolicyEntry`, allowed only on `rating_version` entries, `0 < quantile ≤ 1`, `max_abs_change_pct ≥ 0`; `DEFAULT_POLICY` sets `{quantile: 0.99, max_abs_change_pct: 1.0}`; an entry with `None` refuses every `approximation`-mode submission (fail closed). (b) as (a) with no default (every workspace must declare one). (c) two flat fields | **(a)**, and the default figures are an **actuarial choice the ruling must state or replace**: 1 % at the 99th percentile is offered as a starting point, not derived. `None` fails closed so a workspace cannot opt out by omission | decision point | yes — Task 5 | **ruled (a), amended**, RL-1503 item 7: default `{quantile: 0.99, max_abs_change_pct: 10}` (the maintainer's option D); an entry left unset is governed by the default, not refused; no value switches the gate off (pre-mint 2026-10-05; §"Second pre-mint edit") |
| DP-S5-3 | **How is FR-224's "same version in `exact` mode" run produced?** `DislocationSpec` names two refs; `attribute` refuses a mode difference (premise i) | (a) `DislocationSpec` gains `baseline_mode_override: Literal["exact"] \| None`, valid only when `baseline_ref == candidate_ref`; the handler compiles an ephemeral `exact`-mode bundle of the same version through `WorkspaceResolver` (FR-1398's ephemeral rules: never a row); attribution is not run for such a spec. (b) The analyst creates a real second Rating Version in `exact` mode with identical pins; the gate checks the baseline's `algorithm_ref` and `pins` equal the candidate's and its mode is `exact`. (c) Submission runs it synchronously | **(a)**, as `PL-1267` Slice 5 says ("built by DP-1's mechanism with `model_reference_mode` set to `exact`"). (b) needs no shape change but leaves an `exact` twin in every version list. (c) puts a portfolio pass on a request thread | decision point | yes — Task 4 | **ruled (a)**, RL-1503 item 8 (pre-mint 2026-10-05; §"Second pre-mint edit") |
| DP-S5-4 | **Where does the observed deviation live?** The run has bands, not a per-policy quantile (premise k) | (a) `DislocationRun` gains `abs_change_pct_quantiles: dict[str, float]` for a fixed set (`"0.5"`, `"0.9"`, `"0.95"`, `"0.99"`, `"0.999"`, `"1"`), computed by the handler from the policy frame; the policy's `quantile` must be one of them (validated at `PUT /approval-policy`). (b) the handler persists the per-policy change frame as a quote-input blob and the gate computes any quantile at submission. (c) the gate re-runs the comparison | **(a).** The figure is on the citable artifact the approver reads (FR-265), the gate reads one number, and no per-policy frame is kept. (b) adds a second quote-input blob for one number | decision point | yes — Tasks 4, 5 | **ruled (a)**, RL-1503 item 9 (pre-mint 2026-10-05; §"Second pre-mint edit") |
| DP-S5-5 | **What does FR-136's pre-check refuse, and where?** "The cheap pre-check that runs first … a plainly poor surrogate is refused before a portfolio run is spent" (`03:110`); the statement is prose (premise j) | (a) At `POST /dislocation-runs` with `baseline_mode_override`, and again at submission: every model the version references in `approximation` mode has a transparency artifact **with a GLM approximation** (the statement is not the "No GLM approximation was built" case), else 422 `EVIDENCE_INCOMPLETE` naming the model; the statement is copied onto the evidence for the approver. (b) (a) plus an `r_squared` floor on the policy entry. (c) No refusal; surface only | **(a).** A model with no approximation cannot be rated in `approximation` mode at all (FR-133), so refusing it before the run is the "plainly poor" case with no new threshold. (b) adds a second actuarial figure with no spec basis | decision point | yes — Task 4 | **ruled (a)**, RL-1503 item 10 (pre-mint 2026-10-05; §"Second pre-mint edit") |

## Tasks

### Task 0: Preconditions (no code)

**Files:** the slice ledger `docs/ledgers/LG-<working id>-….md` (the executor's).

- [ ] **Step 1:** Confirm each activation need at the dispatch tree
  (`git -C <worktree> log -1 --format='%H %aI' origin/main`; `SL-1388` and `SL-1256`
  `closed`; the DP ruling and RL 9614 resolve by minted id; this plan `active`).
- [ ] **Step 2:** `uv sync --all-packages`.
- [ ] **Step 3:** Contention, re-run and recorded, as PL-1500 Task 0 Step 3, plus
  `git diff -U0 origin/main...origin/<branch> -- docs/specs/03-rating-engine.md` for any
  active slice: a hunk inside §3.2 (`:90-114` at `137bc817`) is a stop.
- [ ] **Step 4:** Copy the ruling's texts and Slice 4's merged signatures (`DislocationRunRow`,
  `fetch_run`, `WorkspaceResolver`, the handler's steps) into the ledger with line numbers.
- [ ] **Step 5:** Baseline `uv run pytest backend/tests/test_rating_versions.py
  backend/tests/test_dislocation_runs.py packages/model-schema/tests/test_approvals.py -q` and
  the four docs checks; record rc and the summary lines.

### Task 1: Spec — the ruled texts

**Files:** `docs/specs/03-rating-engine.md` (FR-224 `:110`, FR-257 `:174`, §4.6);
`docs/specs/06-governance.md` (§4.2).

- [ ] **Step 1:** Apply the ruling's texts verbatim from the ledger copy (RL-1503's T3, T4 and T5,
  and T7 for §4.6 (pre-mint 2026-10-05, T7; §"Third pre-mint edit"), not this plan's Appendix; pre-mint 2026-10-05; §"Second pre-mint edit"); re-count each find
  string with `grep -cF` (1 each).
- [ ] **Step 2:** `python3 scripts/audit-docs.py` (only check 31 may fail while ids are working
  ids).
- [ ] **Step 3: Commit** `docs(specs): FR-224's threshold, FR-257's baseline, §4.2's field (SL-1389)`.

### Task 2: `structural_diff` persisted, with its verifier (FR-364 E4)

**Files:**
- Modify: `backend/src/app/platform/rating_versions.py` (`submit_for_review`; new `_structural_diff_gate`, `structural_diff_verified`)
- Test: `backend/tests/test_rating_version_dislocation_gate.py` (new)

**Interfaces:**
- Produces: `async def _structural_diff_gate(session, *, workspace_id: UUID, row: RatingVersionRow, baseline: RatingVersionRow | None, blob_store: BlobStore) -> str`
  (the blob's sha256), computing `diff_algorithms(baseline_algorithm or <empty>, candidate_algorithm)`
  and storing `model_dump_json()` bytes as `application/json`.
- Produces: `def structural_diff_verified(row: RatingVersionRow) -> bool` — the evidence names a
  blob digest (Slice 6's `verifiable` entry).
- Consumes: the baseline from Task 3's `_dislocation_baseline` (Task 3 is written first if the
  executor prefers; the two share it).

`submit_for_review` takes no `BlobStore` today. Pass one in from the route (as the compile and
regression routes obtain theirs; mirror `models.py`'s `submit_rating_version`, `:1198`, route at `:1189`), and
make it keyword-only with no default: a caller that forgets it fails at once (fail closed).

- [ ] **Step 1: Write the failing test** — Acceptance 1.
- [ ] **Step 2:** Run it. Expected: FAIL on `row.evidence["structural_diff_blob"]`, a
  `KeyError` (nothing writes it). A failure earlier in the submit (another gate refusing) is a
  fixture defect: give the version its regression run as `test_rating_versions.py` does.
- [ ] **Step 3:** Implement; write the digest into `row.evidence` beside the existing keys
  (`:322-326`).
- [ ] **Step 4:** Run (PASS).
- [ ] **Step 5: Commit** `feat(rating): persist FR-219's structural diff at submission (06 FR-364 E4)`.

### Task 3: FR-257 limb (2)

**Files:**
- Modify: `backend/src/app/platform/environments.py` (new `live_rating_version_ref`)
- Modify: `backend/src/app/platform/dislocation_runs.py` (new `latest_run_for`)
- Modify: `backend/src/app/platform/rating_versions.py` (new `_dislocation_baseline`, `_dislocation_gate`, `dislocation_run_verified`)
- Modify: the existing submit tests' shared fixture (Acceptance 10)
- Test: `backend/tests/test_rating_version_dislocation_gate.py`

**Interfaces:**
- Produces: `async def live_rating_version_ref(session, *, workspace_id: UUID, environment_slug: str) -> str | None`
  (from `_live_by_environment`, `environments.py:67`).
- Produces: `async def _dislocation_baseline(session, *, workspace_id, row, policy) -> tuple[str | None, str]`
  — the baseline ref and the reason (`"live:<env>"`, `"approved"`, `"first_version"`), per DP-S5-1.
- Produces: `async def _dislocation_gate(...) -> UUID | None` — the run id, or `None` only in the
  first-version case, refusing with `_evidence_incomplete(ref, "FR-257 limb (2): …")` otherwise.
- Produces: `def dislocation_run_verified(row) -> bool` (Slice 6's `verifiable` entry).

The check, in order: the latest run (`latest_run_for`) whose `candidate_ref` is this version,
whose `candidate_bundle_hash` equals the version's compiled bundle hash, and whose
`baseline_ref` equals the baseline; refuse naming which of the three failed (no run; stale hash;
wrong baseline). The run's portfolio is recorded on the evidence; "an agreed portfolio" is
the approvers' judgement at review, not a check.

- [ ] **Step 1: Write the failing tests** — Acceptance 2, 3, 4 and 9 (for limb (2)).
- [ ] **Step 2:** Run them. Expected: the three refusal tests FAIL because the submission
  **succeeds** (201/200, the request opened); the acceptance test FAILS on
  `row.evidence["dislocation_run_id"]` (`KeyError`). Any other first failure is a plan defect.
- [ ] **Step 3:** Implement; insert the call after `_regression_run_gate` (`:317`).
- [ ] **Step 4:** Give the existing submit tests their evidence through one shared fixture;
  run Acceptance 10 (PASS, no assertion weakened; the ledger lists every test the fixture now
  serves).
- [ ] **Step 5: Commit** `feat(rating): FR-257 limb (2), a Dislocation Run against the live version`.

### Task 4: FR-224's run and its pre-check (DP-S5-3, DP-S5-4, DP-S5-5)

**Files:**
- Modify: `packages/model-schema/src/model_schema/dislocation.py` (`DislocationSpec.baseline_mode_override`; `DislocationRun.abs_change_pct_quantiles`)
- Modify: `backend/src/app/worker/dislocation_handlers.py`, `backend/src/app/api/dislocation_runs.py`
- Test: `packages/model-schema/tests/test_dislocation.py`; `backend/tests/test_dislocation_runs.py`; `backend/tests/test_rating_version_dislocation_gate.py`

- [ ] **Step 1: Write the failing tests** — a spec with `baseline_mode_override="exact"` and
  `baseline_ref != candidate_ref` refused by `DislocationSpec` (`ValidationError` naming the
  field); the handler, given such a spec, persists a run whose baseline bundle hash differs
  from the candidate's and writes **no** `rating_versions` row; `abs_change_pct_quantiles`
  holds the six keys and `"1"` equals the largest absolute change; Acceptance 8.
  Acceptance 17, 18 and 19's run half, each with its fixture (pre-mint 2026-10-05, T7; §"Third pre-mint edit").
- [ ] **Step 2:** Run them. Expected: `ValidationError` for an unknown field on the first
  (`extra="forbid"`), proving the field is absent; the others fail on the missing field.
- [ ] **Step 3:** Implement the two fields, the handler's ephemeral `exact` compile (an
  in-memory `RatingVersion` copy with `model_reference_mode="exact"`, compiled through
  `WorkspaceResolver`, never persisted), the quantiles ~~(Polars, from the policy frame, null
  when no policy is quoted in both)~~ (T7: over the banded set's absolute percentage changes, nearest rank ⌈q × n⌉ chosen exactly on
  the integers, written as a decimal string rounded once to 6 places toward +∞, each `null`
  when the banded set is empty; never Polars' interpolating `quantile`; pre-mint 2026-10-05, T7; §"Third pre-mint edit"), and the pre-check at `POST`.
- [ ] **Step 4:** `uv run python scripts/generate-contracts.py`; run the tests (PASS) and
  `backend/tests/test_contracts.py` (the authored `dislocation-run.schema.json` gains the two
  fields by the governing path at this tree, which Slice 4 made generated-and-compared; a
  disagreement is a stop).
- [ ] **Step 5: Commit** `feat(dislocation): FR-224's exact-mode baseline run and its quantiles`.

### Task 5: FR-224's gate and the threshold field (DP-S5-2)

**Files:**
- Modify: `packages/model-schema/src/model_schema/approvals.py` (`ApprovalPolicyEntry`, its validator, `DEFAULT_POLICY`)
- Modify: `packages/model-schema/src/model_schema/rating.py` (`RatingVersionEvidence`: `approximation_check`)
- Modify: `backend/src/app/platform/rating_versions.py` (new `_approximation_gate`)
- Test: `packages/model-schema/tests/test_approvals.py`; `backend/tests/test_rating_version_dislocation_gate.py`

**Interfaces:** Produces `ApprovalPolicyEntry.approximation_deviation` (DP-S5-2's shape) and
`RatingVersionEvidence.approximation_check: ApproximationCheck | None` with
`dislocation_run_id`, `quantile`, `observed_abs_change_pct`, `max_abs_change_pct`,
`fidelity_statements`.

- [ ] **Step 1: Write the failing tests** — Acceptance 5, 6 and 7, and Acceptance 19's gate half (pre-mint 2026-10-05, T7; §"Third pre-mint edit").
- [ ] **Step 2:** Run them. Expected: `ValidationError` (unknown field) for Acceptance 7;
  Acceptance 5's refusal tests FAIL because the submission succeeds.
- [ ] **Step 3:** Implement; the gate reads the threshold only from
  `(await approvals.policy_for(session, workspace_id))` (`platform/approvals.py:166`), the
  `rating_version` entry; it runs only when `row.model_reference_mode == "approximation"`.
  `DEFAULT_POLICY`'s `rating_version` entry carries `{quantile: 0.99, max_abs_change_pct: 10}`;
  an entry that leaves the field unset is governed by that default, never refused and never
  ungated (Acceptance 15; RL-1503 item 7; pre-mint 2026-10-05; §"Second pre-mint edit").
  The refusal's `why` names the quantile, the observed figure and the threshold.
- [ ] **Step 4:** Acceptance 6's broken-input proof: make the gate read the threshold from
  `load_settings()`; the test must fail naming the accepted submission; revert; quote both.
- [ ] **Step 5:** Regenerate the contracts; run the tests (PASS).
- [ ] **Step 6: Commit** `feat(rating): FR-224's approximation gate, its threshold on the policy entry (RL-1264 DP-3)`.

### Task 7: The version's change summary, written at submit (DP-E1-6 (a))

*(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* Numbered 7 so no task is renumbered; **run it before Task 6**, whose gate
and ledger cover it.

**Files:**
- Modify: `backend/src/app/platform/rating_versions.py` (`submit_for_review`, the evidence
  write at `:322-326`)
- Test: `backend/tests/test_rating_versions.py`

- [ ] **Step 1: Write the failing test** — Acceptance 14, through the shared fixture.
- [ ] **Step 2:** Run it. Expected: FAIL, the submit response's `change_summary` is `None`.
- [ ] **Step 3:** Implement: `row.change_summary = change_summary`, beside the `row.evidence`
  write (`:322-326`), under the same "written at submit" comment. Nothing else changes: the
  blank-summary refusal stays `approvals.submit`'s (`approvals.py:272-275`).
- [ ] **Step 4:** Run (PASS); re-run `S` whole.
- [ ] **Step 5: Commit** `fix(rating): a rating version carries its submitted change summary (FR-242, DP-E1-6)`.

### Task 6: The gate and the ledger

- [ ] **Step 1:** The full two-half gate (`dev-commands`); `generate-contracts.py --check`;
  the four docs checks; `req-coverage.py` (FR-224, FR-257 and `06` FR-364 each listed with a
  test in `G`). Quote every rc and summary line with the tree.
- [ ] **Step 2:** The ledger: Task 0's records, every red quoted by its cause, Acceptance
  1–13 ~~with evidence~~ and 14 (pre-mint 2026-10-05) ~~with evidence~~, 15 and 16 (RL-1503;
  pre-mint 2026-10-05; §"Second pre-mint edit") with evidence, 17, 18 and 19 (pre-mint 2026-10-05, T7; §"Third pre-mint edit") with
  evidence, each with its broken-variant red, and `RL-1264`'s environment-variable violation discharged by name.

## Hand-off

The executor works in its own worktree on a branch from origin/main after `SL-1388` merges.
The slice closes on a clean audit and the lead's merge. **Slice 6 (`SL-1390`) inherits:**
`structural_diff_verified`, `dislocation_run_verified` and the direct gates it replaces with
the `effective_evidence("rating_version")` loop; the existing `_regression_run_gate` call
(`:317`) it also folds in.

## Appendix — proposed texts (for the ruling to adopt, amend or reject)

*(Ruled by RL-1503: P1 adopted unchanged as its T3, P2 amended as its T4, P3 amended as its T5.
Task 1 applies T3 to T5 from RL-1503, never the texts below; pre-mint 2026-10-05; §"Second pre-mint edit".)*

### P1 — `03` FR-257 (`:174`), appended at the row's end (DP-S5-1 (a))

```markdown
*(Clarified <date>, WK-673 Slice 5, RL-<n>.)* "The current live version" is the Rating Version live in the Environment the `rating_version` approval policy entry names in `dislocation_baseline_environment` (default `prod`, `06` §4.2). With nothing live there, the baseline is the most recently approved other version of the same algorithm; with neither, the version is the algorithm's first, limb (2) records `first_version` on the evidence, and no run is required. The run must name this version at its current bundle hash as its candidate and the baseline as its baseline; a run on an earlier bundle hash is stale and refused with `EVIDENCE_INCOMPLETE`.
```

### P2 — `03` FR-224 (`:110`), appended at the row's end (DP-S5-2 to DP-S5-5)

```markdown
*(Decided <date>, WK-673 Slice 5, `RL-1264` DP-3 (b), RL-<n>.)* The threshold is `approximation_deviation` on the `rating_version` `ApprovalPolicyEntry` (`06` §4.2), a `quantile` and a `max_abs_change_pct`; it is never read from Settings or an environment variable. The exact-mode baseline is a Dislocation Run whose spec names the version as both baseline and candidate with `baseline_mode_override: "exact"`; its baseline bundle is ephemeral (FR-1398). The observed figure is the run's `abs_change_pct_quantiles` at the declared quantile (§4.6). The pre-check refuses, before a run and again at submission, a version referencing in `approximation` mode a model whose transparency artifact has no GLM approximation (`02` FR-133, FR-136), naming the model.
```

### P3 — `06` §4.2, a dated note after the `skippable_predecessors` note (DP-S5-1, DP-S5-2)

```markdown
> **`approximation_deviation` and `dislocation_baseline_environment`, dated <date> (WK-673 Slice 5; `RL-1264` DP-3 (b); RL-<n>).** The `rating_version` entry carries FR-224's threshold, `{"quantile": 0.99, "max_abs_change_pct": 1.0}` by default, and the Environment whose live version is FR-257's baseline, `"prod"` by default. Both are refused on any other artifact type. An entry with no threshold refuses every `approximation`-mode submission. Neither is a Setting (`07` FR-446 does not reach them).
```

`<date>` is the code commit's date and `RL-<n>` the ruling's minted id. The default figures in
P3 are DP-S5-2's open actuarial choice.

## Self-review

1. **Spec coverage.** `06` FR-364's E4 amendment and FR-219 → Task 2. FR-257 limb (2) →
   Task 3. FR-224 → Tasks 4, 5. FR-136 → Task 4 (DP-S5-5). `RL-1264`'s environment-variable
   violation → Task 5 Step 4. `PL-1267` Acceptance 7's four cases → Acceptance 2 (three) and 5.
2. **Placeholder scan.** `<date>`, `RL-<n>`, `LG-<n>` are fixed at the code commit, the mint
   and the executor's ledger. Acceptance 4's `<ruled behaviour>` is DP-S5-1's outcome.
3. **Type consistency.** `structural_diff_verified`, `dislocation_run_verified`,
   `_dislocation_baseline`, `live_rating_version_ref`, `latest_run_for`,
   `baseline_mode_override`, `abs_change_pct_quantiles`, `approximation_deviation` and
   `approximation_check` are spelled the same in Interfaces, Steps, Acceptance and the
   Appendix (grepped).
4. **Rulings between sweep and filing.** Open PRs read at 17:01 BST, and A-1 to A-3 (#1177, #1178, #1174) read before 17:08:50 BST after the first push: RL 9614 (#1167) keeps the
   gate at the submit route (activation need 5); RL-1445 (#1162) is applied in §"Contention";
   PL 9616's `06` texts (RL 9607) are in other `06` sections. No open PR rules on FR-224,
   FR-257 or `06` §4.2's `rating_version` entry.
5. **A stale locator in a frozen record, noted, not edited.** `PL-1267`'s scope table places
   FR-224 in `03` §3.1; at `137bc817` it is in §3.2 (`:110`, after `### 3.2` at `:90`).
6. **Pre-mint edit, 2026-10-05** *(Pre-mint edit 2026-10-05, on the 17:34:57 BST ruling; see §"Pre-mint edit, 2026-10-05".)* DP-E1-6 (a) adds one assignment, one test,
   Task 7 and Acceptance 14; the write set and the contention are unchanged (§"Pre-mint
   edit, 2026-10-05", items 2 and 3); the F27 draft residue is named out of scope. RL-1497 is
   cited by working id and kept out of `relates:`.
7. **Second pre-mint edit, 2026-10-05 (RL-1503).** C1 is applied byte for byte. The five
   decision points carry their rulings. Acceptance 15 and 16 come from RL-1503's own text.
   The write set and the contention are unchanged. The §4.6 note's missing text is reported,
   not supplied. RL-1503 is cited by working id and kept out of `relates:` (check 32).
8. **Third pre-mint edit, 2026-10-05 (RL-1503 T7).** Task 1 applies T7 with T3 to T5. Acceptance
   17, 18 and 19 carry the three reds the 18:54:06 BST entry names, each with an exact fixture
   and a broken-variant red; their figures were run, not derived by hand. The write set gains
   no path. Task 4 Step 3's "quoted in both" is struck for T7's banded set. C1, DP-E1-6 (a)
   and the earlier deltas are unchanged.
9. **Fourth pre-mint edit, 2026-10-05 (the write-set gap).** Task 4's two test files are in the
   write set and the contention table: `test_dislocation.py` appended, shared with Slice 3;
   `test_dislocation_runs.py` created by Slice 4, appended here after it. Task 4 is unchanged.
