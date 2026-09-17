---
id: RL-886
family: ruling
title: Finding 2: `deployment` has a floor and no policy entry; the spec is right and the code is short one entry
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slices-2-4-rulings.md
---

## RL-886 — Finding 2: `deployment` has a floor and no policy entry; the spec is right and the code is short one entry

`EVIDENCE_FLOOR` holds `"deployment": ("rating_version_approval", "uat_deployment")`
(`approvals.py:107`) and `DEFAULT_POLICY` has **no** `deployment` entry (`:202-261`), while `06`
§4.2's document does (`:271-273`). A deployment submission therefore never reaches an evidence
check: `approvals.submit` refuses at `backend/src/app/platform/approvals.py:181-188` with
*"No approval policy for this artifact type"*.

**Ruled: no spec change. `06` §4.2 is right; the code is short one entry, and it is WK-674's** —
the workstream that owns FR-267 and is the first to submit a deployment for approval. This is
the third instance of a defect class `06` §4.2 already documents twice, for `peril_structure`
(2026-08-18) and `custom_metric` (2026-08-20); the dated note recording it belongs in §4.2 with
the entry that fixes it, which is how both predecessors were handled, so it is not written now.

**Stated as the predicted failure by cause, not by status.** The refusal is a **422** whose title
is *"No approval policy for this artifact type"* — it fires **before** any evidence is consulted,
so both the status and the message point away from the actual gap. An executor who reads only the
status will look at the evidence machinery, which is working.

**Acceptance test — the violation that must become expressible.** A `deployment` submission
reaching the evidence check at all. Today it cannot, so no test can distinguish "evidence
incomplete" from "no policy"; once the entry exists, the two are separable refusals and each is
assertable.

---
