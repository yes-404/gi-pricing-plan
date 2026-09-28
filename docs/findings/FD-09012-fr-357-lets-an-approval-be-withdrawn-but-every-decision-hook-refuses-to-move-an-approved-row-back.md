---
id: FD-9012
family: finding
title: FR-357 lets an approval be withdrawn, but every decision hook refuses to move an approved row back
status: active
created: 2026-09-28
owner: auditor
tree: 9f6bfed1a94838d92bdc76475e03f8b5b078527a
corrected_by: []
relates: [FD-1200]
---

# FD-9012 — FR-357 lets an approval be withdrawn, but every decision hook refuses to move an approved row back

The auditor filed this finding on 2026-09-28, on the lead's instruction. auditor-a raised it as
O2 in the audit of #864 (recorded in auditor-a's local job directory, not in the repository), and
the lead routed it to the deputy in the lead's local channel file `to-deputy.md` (line 19913).
It is a `CLAUDE.md` §0 disagreement between the spec and the code. **This record does not say
which side is wrong.**

**The deputy's routing, verbatim.** This is his entry in the lead's local channel file
`to-lead.md` stamped 2026-09-28 17:44:58 BST (line 8775): its heading and item (1), in full. He
first sent it as a direct message about 17:41 BST and filed it as this dated record. Item (2)
concerns another PR and is not quoted.

```text
## 2026-09-28 17:44:58 BST · deputy · Two instructions I sent only as direct messages, filed here as the dated record (CLAUDE.md §12; the lead's catch): (1) #864's audit and O2 (FR-357); (2) #833 (RS-1201) held for the 14:05:30 F3 amendment

**(1) #864, the approval-status fix: its audit is NOTED, and O2 is ROUTED (sent ~17:41 BST by message; filed now).**
- The audit is noted: 41/41 cases, and **the hole is closed**. The mutation reds were exact (M1 → 6, M2 → 1).
- The two MED findings are fixed inside #864:
  - **F1:** a stale request on a draft Rating Version from before the fix can be closed and the version resubmitted;
  - **F2:** the data query's SQL goes into the PR body, is re-run, and its result is quoted.
- **O2, a CLAUDE.md §0 disagreement:** `06` FR-357 permits an `APPROVED` → `WITHDRAWN` request transition, and every module refuses to move an approved row back. **Routed to plan review 15, and not left silent:** auditor-b files an FD now (#865, working FD-9012) quoting **both sides verbatim** (FR-357 and `06:453`; `model_schema/approvals.py:73`; each refusing site by file and line), with **no verdict**. Owner the lead, event plan review 15. **The question the review must decide:** can an approval be withdrawn after a deployment, and if so, what happens to the deployed version? It is decided there, **not in #864**.
- #864's MERGE-ACK follows your request once F1 and F2 are in and CI is green.
```

## Finding

`06` FR-357 allows an **approved** approval to be **withdrawn** before deployment. The approval
state machine in code allows it too. But the withdraw route then carries the withdrawal into the
artifact, and every artifact module with a decision hook refuses to move an `approved` row to any
state that a withdrawal maps to. So on the code's path, withdrawing an approved request fails for
every hooked type, while the spec says it is allowed.

## Evidence

### The spec side

At `origin/main` `9f6bfed1`:

- `docs/specs/06-governance.md:98`, FR-357, verbatim: *"An approval can be **withdrawn** before
  deployment by an Approver or an Admin with a reason; it cannot be withdrawn after the artifact
  is live (the correct action is then a rollback or a new version)."*
- `docs/specs/06-governance.md:453`: `POST /api/v1/approval-requests/{id}/withdraw`, *"Withdraw
  before deployment (FR-357)"*.

### The code side

At `9f6bfed1`, found by `grep -rnE "WITHDRAWN" backend/src packages/model-schema/src` and
`grep -rnE "(ModelStatus|ObjectiveStatus|MetricStatus)\.APPROVED: *frozenset"
packages/model-schema/src`:

**The approval machine permits the withdrawal.**
`packages/model-schema/src/model_schema/approvals.py:73`:
`ApprovalStatus.APPROVED: frozenset({ApprovalStatus.WITHDRAWN}),`.
`backend/src/app/platform/approvals.py:405` checks that transition, and `:408` sets `WITHDRAWN`.

**The route carries the withdrawal into the artifact.** `backend/src/app/api/approvals.py`
`withdraw_request` (`:277`) calls `_carry_to_the_artifact` after `service.withdraw`. That calls
each module's `apply_approval_decision` (`:492`, `:498`, `:504`, `:510`). Its comment reads:
*"A withdrawn request leaves the artifact where a rejected one does: back in its pre-submission
state."*

**Each hook maps a withdrawal to the pre-submission state, which the approved row cannot reach:**

| Type | Withdrawal maps to | The approved row may only go to | Refused at |
|---|---|---|---|
| Model | `ApprovalStatus.WITHDRAWN: ModelStatus.FITTED` (`platform/modelling.py:1389`) | `ModelStatus.APPROVED: frozenset({ModelStatus.SUPERSEDED})` (`model_schema/modelling.py:2015`) | `_require_transition` (`platform/modelling.py:1068`), `if target not in VALID_MODEL_TRANSITIONS[current]:`, called from the hook at `:1354` |
| Custom Objective | `ApprovalStatus.WITHDRAWN: ObjectiveStatus.CERTIFIED` (`platform/objectives.py:876`) | `ObjectiveStatus.APPROVED: frozenset({ObjectiveStatus.DEPRECATED})` (`model_schema/objectives.py:163`) | `platform/objectives.py:667`, `if target not in VALID_OBJECTIVE_TRANSITIONS[before]:` |
| Custom Metric | `ApprovalStatus.WITHDRAWN: MetricStatus.CERTIFIED` (`platform/metrics.py:828`) | `MetricStatus.APPROVED: frozenset({MetricStatus.DEPRECATED})` (`model_schema/metrics.py:67`) | `platform/metrics.py:595`, `if target not in VALID_METRIC_TRANSITIONS[before]:` |

**Rating Version.** At `9f6bfed1`, the Rating Version hook does not read the request's status at
all. It "approved" on a withdrawal: that is `FD-1200`'s second defect, so the refusal did not
apply to it. #864, merged as `e6a9ca71`, adds
`approvals.require_in_review(ref, row.status)` (`rating_versions.py:299` at `e6a9ca71`) and maps
`ApprovalStatus.WITHDRAWN: RatingVersionStatus.DRAFT` (`:326`). From #864 on, an approved Rating
Version is refused too. **For the three siblings the disagreement predates #864; for the Rating
Version it is new with #864, which did not introduce the conflict and does not fix it.**

## Disposition

**Deferred with an owner — the lead.** Event: plan review 15 (#863), where the governance
question *"can an approval be withdrawn after a deploy?"* is decided. That decision settles which
side is corrected (`CLAUDE.md` §0). It is not fixed in #864.
