---
id: RL-1524
family: ruling
title: FD-1244 and FD-1245 — WF-699 D4 and E2 move to the requirements, not FR-261 or FR-257, and 06's generic approval route names the Rating Version submit route
status: active                 # active → superseded | retired (§1.2a)
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: decision-maker
tree: cdaaa57345cb765f96034ce1ec2733c338f1c3cd
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1244, FD-1245, WF-699, FR-257, FR-260, FR-261, FR-351, FR-352, OQ-1224]   # at the mint, add PL 9629's minted id
---

# RL-1524 — FD-1244 and FD-1245: WF-699 D4 and E2 move, and 06's generic route names the submit route

*(Minted 2026-10-08 as RL-1524 from working id 9614, in the G2-a batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

## How this was ruled

- **Filed under a working id the lead reserved.** `RL-1524` in this draft, and `RL-1524` in
  the texts below, stand for this ruling's minted id. `PL 9629` (draft #1164) is a working id,
  re-pointed at its mint.
- **The decisions are not this record's.** They are the maintainer's, by delegation, in
  `~/gi-pricing-plan.local/channel/to-lead.md`, entry
  *"2026-10-05 15:35:48 BST — MERGE-ACK #1157 (SL-1409, the FD-1356 fix) at 912baf4a…; DP-1
  and DP-2 for RL 9614 RULED"*, quoted verbatim under **Ruled**. They were put on the
  decision-maker's memo `handover/dp-memo-rl9614-fd1244-fd1245-2026-10-05.md` (local), written
  2026-10-05 at `origin/main` `809a3794`. This record carries the decisions as a dated artifact
  (`CLAUDE.md` §12) and applies them. It decides nothing beyond them.
- **Why the memo, not an open-DP draft RL:** check 33 (`scripts/audit-docs.py`
  `_STATUS_SUBSET`) allows `RL` only `active`, `superseded` and `retired`, so a ruling cannot
  be filed `draft` with its decision points open. This record is filed after the ruling,
  `active`.
- **Scope of the question.** FD-1244 and FD-1245 are each `CLAUDE.md` §0's question — which of
  a journey step and the requirement it cites is wrong. Both register rows
  (`docs/findings/register.md`, the rows keyed `(FD-1244)` and `(FD-1245)`) name the
  decision-maker as owner, event "the decision-maker's ruling", no later than the gate before
  the P2 exit demo.
- **Re-verified at `origin/main` `cdaaa57345cb765f96034ce1ec2733c338f1c3cd`**, 2026-10-05. From
  `809a3794` to `cdaaa573`, `03-rating-engine.md`, `docs/workflows/` and `open-questions.md`
  did not change; `06-governance.md` changed in FR-351 and FR-363's Validation Rule row only
  (FR-351's refusal clause, quoted below, is unchanged); `backend/src/app/api/approvals.py`
  changed, so its locator below is by symbol.

## Locators — read at `cdaaa573`

- `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:84`, D4:
  *"A property assertion fails: `monotone_in_age` breaks between 63 and 64 because two rate
  tables band age differently. Hypothesis shrinks it to a minimal counterexample."*
  (`03` FR-261).
- The same file `:96`, E2: *"`POST /approval-requests`. Evidence completeness is checked at
  submission: …"* (`03` FR-257, `06` FR-352/363).
- `03-rating-engine.md:178`, FR-261, the 2026-09-28 clarification: the grid is *"one fixed set
  of at most ten points per property"*; *"A counterexample is the base context and the two
  adjacent grid values at which the order broke"*; *"the compiled bundle pins no Banding, so no
  band edge is in the grid, and an inversion narrower than the spacing between the grid and
  sampled points may not be detected until `OQ-1224` lands."* `03:766-769`: a failing
  property records `shrink`, `counterexample_minimal` and `counterexample_points`.
- `open-questions.md:135`, `OQ-1224`: open, owner WK-1178 (pin Bandings, `grid: banding-edges`).
- `03:174`, FR-257: *"It applies forward, at submit."* `03:177`, FR-260 amendment (1): *"The
  check runs at `POST /api/v1/rating-versions/{id}/submit`."* `03:910`, that route's §5.1 row.
- `backend/src/app/api/models.py:1189`, `submit_rating_version`, route
  `"/rating-versions/{rating_version_id}/submit"`, docstring *"Move a rating version from draft
  to review, creating an approval request."*
- `backend/src/app/api/approvals.py`, `_resolve_rating_version`: calls
  `service.require_in_review(artifact_ref, row.status)` (`app/platform/approvals.py`
  `require_in_review`: *"Refuse an approval subject that is not in its type's reviewable
  state"*). `backend/tests/test_rating_versions.py:1394`,
  `test_golden_bypass_a_draft_cannot_be_put_to_approval_directly`.
- `06-governance.md:92`, FR-351: *"`POST /approval-requests` refuses any other state with
  `APPROVAL_SUBJECT_NOT_IN_REVIEW` (409)"*; the reviewable state for `rating_version` is
  `review`.
- `06-governance.md:558`: *"| `POST` | `/api/v1/approval-requests` | Submit an artifact;
  validates evidence and checklist (FR-352) |"* — no Rating Version exception.

## Ruled

Quoted verbatim from the entry named above (the lines after its first paragraph):

> RL-1524 (FD-1244 / FD-1245), on the memo handover/dp-memo-rl9614-fd1244-fd1245-2026-10-05.md:
>  DP-1 (FD-1244): OPTION (a): change the STEP (WF-699 D4 describes a break between two adjacent grid ages from an inverted band wider than the grid spacing; a narrower inversion may be missed until OQ-1224 lands), not FR-261. Consequence BOUND: PL 9629's demo data must contain an inverted band wider than the grid spacing, or D4 does not fire. PL 9629 states its band and the spacing.
>  DP-2 (FD-1245): OPTION (a): E2 names `POST /rating-versions/{id}/submit` ("moves the version from draft to review and opens its Approval Request"), citing 03 FR-257 and FR-260. Spec, code and test agree (03:177, 03:910, models.py:1189, approvals.py:416, test_rating_versions.py:1394).
>  06-governance.md:558 (the generic `POST /api/v1/approval-requests` row gives no Rating Version exception, yet the route refuses a draft one): FOLD it into RL-1524, not FD-1416. It is the same decision as DP-2 seen from 06's side: a dated T-text on 06:558 saying a Rating Version is submitted through its own route (03 FR-260 (1)), so the generic route refuses it. FD-1416 is about the request's SHAPE, a different defect.
>  File RL-1524 `active` with the WF-699 edits and the 06 T-text in one commit, as the DM set up. RL-1449's `status: draft` → `active` at its mint (check 33): noted as owed.

`approvals.py:416` in the quote was the line at `809a3794`; at `cdaaa573` the function is
`_resolve_rating_version`, cited by symbol above.

1. **DP-1 (FD-1244): the step moves, FR-261 does not.** The spec was clarified deliberately on
   2026-09-28 with the weakness stated, and `OQ-1224` owns the stronger form. Text T1.
2. **DP-1's binding:** the G2 exit demo runs `WF-699` end to end, so **PL 9629's demo data must
   contain an inverted band wider than the grid spacing, or D4 does not fire.** PL 9629 states
   its band and the spacing. That is PL 9629's text (planner-demo2's), not this record's; this
   record only records the binding.
3. **DP-2 (FD-1245): the step moves, FR-257 and FR-260 do not.** Text T2.
4. **`06:558`, folded here as the same decision seen from `06`'s side.** Text T3. It is not
   FD-1416's (that finding concerns the request's shape).

## The spec texts

Each find string counted with `grep -cF` = 1 at `cdaaa573`, and applied in this record's commit.

### T1 — `WF-699` D4's description cell

Find:

```
A property assertion fails: `monotone_in_age` breaks between 63 and 64 because two rate tables band age differently. Hypothesis shrinks it to a minimal counterexample.
```

Replace:

```
A property assertion fails: `monotone_in_age` breaks between two adjacent grid ages, because two rate tables band age differently and the inverted band is wider than the grid spacing. Hypothesis shrinks the base context; the counterexample is that base context and the two grid ages (`grid: uniform+sampled`). An inversion narrower than the grid spacing may not be detected until `OQ-1224` lands. *(Amended 2026-10-05, `RL-1524` DP-1.)*
```

The citation cell stays `` `03` FR-261 ``. D5 is unchanged and stays true: the defect is one a
golden-quote suite alone would have missed.

### T2 — `WF-699` E2's row

Find:

```
| E2 | Pricing Actuary | `POST /approval-requests`. Evidence completeness is checked at submission: structural diff, rate diffs, regression run, dislocation run, GIPP check where enabled, change summary. | `03` FR-257, `06` FR-352/363 |
```

Replace:

```
| E2 | Pricing Actuary | `POST /rating-versions/{id}/submit`, which moves the version from `draft` to `review` and opens its Approval Request. Evidence completeness is checked at submission: structural diff, rate diffs, regression run, dislocation run, GIPP check where enabled, change summary. *(Amended 2026-10-05, `RL-1524` DP-2.)* | `03` FR-257/260, `06` FR-352/363 |
```

### T3 — `06-governance.md` §5.1, the `POST /api/v1/approval-requests` row

Find:

```
| `POST` | `/api/v1/approval-requests` | Submit an artifact; validates evidence and checklist (FR-352) |
```

Replace:

```
| `POST` | `/api/v1/approval-requests` | Submit an artifact; validates evidence and checklist (FR-352) *(Clarified 2026-10-05, `RL-1524` DP-2: a Rating Version is submitted through its own route, `POST /api/v1/rating-versions/{id}/submit` (`03` FR-260 (1)), which moves it to `review` and opens its request. This route refuses a Rating Version that is not in `review` with `APPROVAL_SUBJECT_NOT_IN_REVIEW` (FR-351).)* |
```

**One precision against the ruling's wording, stated rather than smoothed.** The entry says
*"so the generic route refuses it"*. The code refuses a Rating Version **not in `review`**
(`require_in_review`), and FR-351 says the same; it does not refuse every Rating Version. T3
says what the code and FR-351 say. If the maintainer (by delegation) meant the stronger rule
(the generic route refuses a Rating Version in any state), that is a code change and a new
decision, not this text.

## What it obliges

- **At the merge (the lead):** annotate the register rows keyed `(FD-1244)` and `(FD-1245)`
  **Resolved**, naming this record's minted id and the squash commit.
- **PL 9629 (planner-demo2):** state the demo data's inverted band and the grid spacing (DP-1's
  binding).
- **At the mint:** re-point `RL-1524` in T1–T3 and this record to the minted id; add PL 9629's
  minted id to `relates:`; re-count T1–T3's replacement strings at the then-current main.
- No code changes. No requirement is amended: FR-257, FR-260 and FR-261 stand as written.

## Acceptance — the violation that must become detectable

- `grep -cF 'between 63 and 64' docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`
  is 0, and `grep -cF 'POST /approval-requests' docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`
  is 0 (both 1 at `cdaaa573`; 0 with T1 and T2 applied).
- `grep -cF 'POST /rating-versions/{id}/submit' docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`
  is 1.
- A G2 demo run whose regression run reports no `monotone` failure at D4 is the observable
  breach of DP-1's binding; PL 9629's acceptance carries that check.
