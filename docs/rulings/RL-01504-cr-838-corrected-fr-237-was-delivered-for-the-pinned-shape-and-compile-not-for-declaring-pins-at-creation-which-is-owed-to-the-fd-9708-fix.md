---
id: RL-1504
family: ruling
title: CR-838 corrected — FR-237 was delivered for the pinned shape and for compile, not for declaring the pins when a Rating Version is created, which is owed to the FD-1421 fix in WK-1178; and FR-242 was not delivered for drafting the change summary, which is owed to a WK-673 slice
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: decision-maker
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: CR-838
relates: [CR-838, WK-669, WK-1178, FR-237, FR-242, WK-673]
---

# RL-1504 — CR-838 corrected: FR-237 was not delivered for the create route, nor FR-242 for the drafted summary

*(Minted 2026-10-08 as RL-1504 from working id 9668, in the T8 batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

## How this was ruled

- **This record rules nothing new.** The decision that CR-838 needs a correcting record is
  the maintainer's, by delegation, in
  `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed *"2026-10-05 13:15:53 BST —
  DECISIONS 17–21 (PL-1452 DP-S3-2/3/6; FD-1420 DP-1; RL-1428 follow-ups)"*, item 21(ii):
  *"CR-838 marks FR-237 delivered without the create route: YES, a correcting record is needed
  (document-ids.md :136 `corrects:`; check 34 allows only an append to the frozen record's
  `corrected_by:`). It states the false "delivered", cites FD-1421, and corrects CR-838."*
  The decision-maker session `dm-9708` (`echo $CLAUDE_EFFORT` printed `medium`) drafted this
  record on the lead's relay of that item and re-read every site below at `origin/main`
  `caa4e411a9c07a389cf47092a923c7761b2b92dc`, 2026-10-05. Unminted records (FD-1421,
  RL-1428) are cited in working-id form and kept out of `relates:` (check 32).
- **Who may write it.** `docs/process/document-ids.md` §1.6 gives the **RL** row's author as
  *"decision-maker; the maintainer may author one on scope or process"*. Its **CR** row gives
  the closure's author as the auditor, its acceptance (*"maintainer accepts a Work or Phase
  close"*), and no correction path (`—`). So the RL family is this role's to write, but what
  it corrects is a maintainer-accepted close. Per the same item 21(ii), **the maintainer (by delegation) accepts
  this record at its ACK**; it binds nothing before then.
- **The form** follows RL-1496 (#1119, `corrects: RL-1401`): a correcting record whose
  `corrects:` names the frozen file, and the frozen file's body is never edited.
  `document-ids.md:136` gives `corrects:` as a scalar, *"the frozen id it corrects"*, and
  RL-1496 writes it that way. This record does too, `corrects: CR-838`, where the lead's brief
  wrote the list form.

## The false verdict

`docs/closures/CR-00838-work-item-record-wk-669-the-rating-contract-validation-and-bundle-compilation.md:40`,
verbatim:

> `| FR-237, FR-238, FR-239, FR-240, FR-241, FR-242 | delivered | marker-evidenced (22: 3, 23: 1, 24: 4, 25: 1, 26: 1, 27: 1) |`

and its slice row, `:33`: W9-3 (#293) delivered *"FR-237 (pins)"*, evidenced by the *"widened
`RatingVersion` (spec-reconciled vs `03` §4.3); `compile_bundle`/`to_jdm`/`bundle_hash` …;
`POST /rating-versions/{id}/compile`"*.

## What it missed

| Fact | Where |
|---|---|
| At CR-838's own tree, `3a4958a9b67936efe7cb25079be46741fff0df89` (its line 16), `03` §5.1 already had the row `` `POST` `/api/v1/rating-versions` `` *"Create a draft Rating Version with pins"*, and the WF-699 journey's C1 said that call *"declares the algorithm version and every pin"* | `git grep` at `3a4958a`: `docs/specs/03-rating-engine.md:483`; WF-699's file at that tree (its pre-migration name), line 56 |
| At that tree no route created a Rating Version at all: `class RatingVersionCreate` does not exist there | `git grep -n 'class RatingVersionCreate' 3a4958a -- backend` prints nothing |
| The create route came two days after the close, without pins: `RatingVersionCreate` takes `slug`, `dataset_version_id` and `model_ref` only, under `extra="forbid"` | first added by `0d942b3e` (2026-08-29T17:01:09+01:00, #371, *"wire POST /rating-versions and /submit routes"*); at `caa4e411`, `backend/src/app/api/models.py:271-276` |
| No HTTP route sets `algorithm_ref` or `pins` today; the demo seed writes them to the ORM row | FD-1421 (#1130, working id), its tables; `examples/fremtpl2/model.py:396-397` at `caa4e411` |
| The spec governs and the code is behind: `POST /rating-versions` is to accept `algorithm_ref` and the pins, checked at compile, in a WK-1178 slice | RL-1428 (#1133, working id), decided by the maintainer (by delegation) at 13:12:56 BST, item 15 |

So the evidence CR-838 cited — FR-237's markers, the widened shape, and compile reading the
pins — proves that a Rating Version *can hold* pins and that compile *uses* them. It does not
reach the part of FR-237 that the spec routes through `POST /rating-versions`: a client
*declaring* the algorithm and the pins. That part was not built at the close and is not built
at `caa4e411`. The verdict "delivered" was therefore false for that limb at CR-838's own tree.

## Ruled

The correction:

> **FR-237 is partly delivered.** Delivered, at CR-838's tree: the pinned `RatingVersion` shape
> (`algorithm_ref`, `pins`, `model_reference_mode`) and its use by `compile_bundle` (W9-3, #293).
> **Not delivered:** declaring the algorithm version and the pins when a Rating Version is
> created, which `03` §5.1's `POST /api/v1/rating-versions` row and `WF-699` step C1 require.
> That limb is owed to the FD 9708 fix in WK-1178, as RL 9695 decided. FR-238 to FR-241 and
> every other verdict in CR-838 are unaffected by this correction. *(Amended 2026-10-05
> before the mint: this read "FR-238 to FR-242"; FR-242 is corrected in the next section.)*

The verdict for this limb is **deferred with an owner** (`CLAUDE.md` §13's four verdicts):
owner WK-1178, the FD-1421 fix slice, deadline before the P2 exit demo (the maintainer's (by delegation)
13:12:56 BST entry, item 15). WK-669 stays closed; the owed work is WK-1178's, not a reopen.

## FR-242 — the drafting limb (added 2026-10-05, 17:21 BST, before the mint)

- **The decision is the maintainer's, by delegation:** `channel/to-lead.md`, the entry headed
  *"2026-10-05 17:14:54 BST — FD 9572 placement accepted; WK-673 S4/S5/S6, A-1, A-2 and
  CR-838 DECISIONS (1–8)"*, item 8, verbatim:
  *"CR-838:40 records FR-242 "delivered" on marker evidence while its DRAFTING limb is
  unbuilt (AlgorithmDiff.summary never drafts): YES, record it, but FOLD it into RL-1504
  (#1137, unmerged, already `corrects: CR-838`, and `corrects:` is scalar, so a second
  correcting RL for one CR is the wrong shape). A pre-mint edit adds the FR-242 limb with its
  evidence and cites E1's new slice as the owner of the fix."*
- **The false verdict** is the same row as FR-237's, CR-838 `:40` (quoted above): FR-242,
  "delivered", "marker-evidenced".

**What it missed.** FR-242 has two limbs: the summary is **required**, and it is **"generated
as a draft from the structural and rate-table diffs and edited by the actuary"**.

| Fact | Where |
|---|---|
| At CR-838's tree the requirement already had both limbs, under its pre-migration id | `git grep -n 'required \*\*change summary\*\*' 3a4958a -- docs/specs/03-rating-engine.md`: `:138`, the same row under its pre-migration id, "It is generated as a draft from the structural and rate-table diffs and edited by the actuary." At `4d3be141` the same text is FR-242, `:139` |
| The **required** limb was built: the field and the submit guard | `RatingVersion.change_summary: str \| None` (`model_schema/rating.py:127` at `3a4958a`; `:168` at `4d3be141`); the guard raises `VALIDATION_FAILED` "A change summary is required" (`backend/src/app/platform/approvals.py:275` at `4d3be141`; PL-847 `:511-513` cites it at an earlier line) |
| The **drafting** limb was not built, then or now | `AlgorithmDiff.summary` (`model_schema/rating.py:513` at `3a4958a`, `:554` at `4d3be141`) returns a count string ("2 step(s) added, …") and drafts nothing. Its only backend caller path is `diff_algorithms(...)`'s `.model_dump()` (`backend/src/app/platform/rating_algorithms.py:141` at `3a4958a`, `:163` at `4d3be141`), and a property is not dumped. `git grep -n -i -E 'draft.{0,30}change.summary\|change.summary.{0,30}draft' <tree> -- backend/src packages` prints nothing at either tree. No rate-table diff is summarised anywhere |
| The plan had scoped it | PL-818 (WK-669) `:160`: "Add the change summary (FR-242): a required field, drafted from the diffs and edited by the actuary" |

*(Pre-mint note, 2026-10-05 17:36:36 BST, dm-e1, on the maintainer's (by delegation) entry
"2026-10-05 17:34:57 BST — E1 DPs …: all six ADOPTED as recommended; S1 yes; S2 yes; PL 9578
noted", S2: the row above is corrected in one sentence. **The "field" is only declared:
nothing writes `RatingVersion.change_summary` at `4d3be141` (`create_rating_version` builds the
row at `rating_versions.py:254-262` without it, and `submit_for_review` passes the summary only
to `approvals.submit`, `:327-333`), so the required limb is enforced on the Approval Request,
by the guard at `backend/src/app/platform/approvals.py:272-275`, not on the version.**)*

So the marker evidence proves the summary is required. It does not reach the draft, which the
spec and WF-699 step E1 (`:95`, "drafted automatically from the structural and rate
diffs and then edited") both need. "Delivered" was false for that limb at CR-838's own tree.

**The correction:**

> **FR-242 is partly delivered.** Delivered, at CR-838's tree: the required change summary
> (the field and the submit guard). **Not delivered:** generating the summary as a draft from
> the structural and rate-table diffs. That limb is owed to WK-673's E1 slice, SL 9565 with
> leaf plan PL 9564 (working ids), which RL 9566 (working id, #1191) item 12 records as the
> maintainer's (by delegation) decision of 17:14:54 BST, item 4.

The verdict for this limb is **deferred with an owner** (`CLAUDE.md` §13's four verdicts):
owner WK-673, the E1 slice; needed for G2 (WF-699 E1 in the P2 exit demo, the entry headed
*"2026-10-05 17:07:00 BST"*, "G2 needs an owner"). WK-669 stays closed.

## What it obliges

- **This draft:** this record only. CR-838 is not edited.
- **The mint turn (the lead, in merge order):** this record's working id becomes its minted id
  everywhere this commit writes it, and CR-838's header gains `corrected_by: [<this record's
  minted id>]`. That append is CR-838's only edit, in the same PR. **Owed at the mint.**
- **The FD-1421 fix slice (WK-1178):** its ledger names this record as discharged when the
  create route accepts the pins, so the "deferred with an owner" verdict above closes.
- **The E1 slice (WK-673, SL-1502; added 2026-10-05 before the mint):** its ledger names this
  record as discharged for FR-242 when a Rating Version's change summary is drafted from the
  structural and rate-table diffs, so the FR-242 verdict above closes.

## Acceptance — the violation that must become detectable

- *Violation: after the mint, CR-838's `corrected_by:` names this record while this record's
  `corrects:` does not name CR-838.* `audit-docs.py` check 34 reports it (`check_freeze`).
  **The other direction is not checked:** a `corrects:` with no `corrected_by:` back passes
  check 34, which is why this draft is green before the mint. The mint turn's read-back of
  CR-838's header is the only guard on that direction.
- *Violation: the mint edits any other line of CR-838.* Check 34 reports a frozen-family diff
  that is not a `status:`, `superseded_by:` or `corrected_by:` change.
- *Violation: FR-237's create limb is claimed delivered while the route takes no pins.* The
  FD-1421 slice's acceptance (RL-1428, its first violation) fails: a create carrying
  `algorithm_ref` and `pins` is refused 422.

- *Violation (added 2026-10-05 before the mint): FR-242's drafting limb is claimed delivered
  while nothing drafts.* The E1 slice's acceptance fails: a Rating Version with a structural
  change and a re-pointed rate table gets no drafted summary naming both.

## Observed, not ruled (for the lead)

CR-838 already carries a body edit: a blockquote headed *"Dated correction, 2026-09-29 (the
auditor), on the maintainer's decision"* at `:46`, about FR-217. It predates the RL-1496 form
and is not touched here. Whether it needs a correcting record of its own is not this
record's question.

*(Pre-mint note, 2026-10-05 15:58 BST, dm-finals2: the maintainer (by delegation) routed this in
the entry headed "2026-10-05 13:24:03 BST — RL 9668 (#1137) noted for its ACK; DP-S3-1 addendum
ACCEPTED; CR-838:46 is a data point for FD-1282", item 2: not ruled, not edited, and added to
FD-1282's register row as a second observed case. That row merged in `c37bf921` (#1139).)*
