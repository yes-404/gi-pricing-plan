---
id: FD-1491
family: finding
title: A custom metric whose certificate_id names no metric_certificate row passes the submission evidence check, because the check tests only that the column is not null
status: active
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: auditor
tree: 47d770e8fcbd2410fa101019ed8cf3aae69a1baa
corrected_by: []
relates: [WK-690, FR-157, FR-364]
---

# FD-1491 — a custom metric's `certificate_id` is never resolved before submission

*Disclosure: drafted under working id 9722; minted as FD-1491 on 2026-10-08, in the T2 batch mint PR.*

**Filed** by auditor-fdc2 on 2026-10-05, from the S3 slice audit's item A1
(`~/gi-pricing-plan.local/handover/audit-sl1273-2026-10-04.md`, section "A1") and the S3 dispatch record's
Delta 11. Every line number below was re-read at `origin/main` = `47d770e8fcbd2410fa101019ed8cf3aae69a1baa`,
which is the `tree:` above; none is copied from the audit.

*Re-anchored 2026-10-05 at main `caa4e411a9c07a389cf47092a923c7761b2b92dc`. The metric defect still stands there:
`metrics.py:794` is unchanged and `submit` (`:485`) still never loads the row `certificate_id` names. Moved cites:
`models.py` `:1857-1860` → `:1868-1871` and `:1900-1903` → `:1910-1914`. **The objective twin changed:** S3
(#1122) merged, and `submit_for_review` now resolves the pointer after `_require_evidence`
(`objectives.py:726-741`, same workspace and same objective, `VALIDATION_FAILED` 409); `_require_evidence`'s own
null test is now at `objectives.py:1022`. Where the body below says the objective twin is "unclosed" or "S3's
branch", that was true at `47d770e8` and is not true at `caa4e411`. The metric half, which this finding claims,
has no counterpart in S3 at main. `test_custom_metrics_api.py:133` and `:122` are unchanged.*

## Finding

`backend/src/app/platform/metrics.py` `_require_evidence` (`:759`), called from `submit` (`:517`), decides whether
a Custom Metric has its `metric_certificate` evidence with one expression:

```
backend/src/app/platform/metrics.py:794:    verifiable = {"metric_certificate": row.certificate_id is not None}
```

It never loads the row `certificate_id` names. `custom_metrics.certificate_id` is a bare UUID column with no
foreign key (`backend/src/app/db/models.py:1868-1871`, the comment there says so and gives the reason). So a metric
whose `certificate_id` is any non-null UUID, with no `metric_certificates` row behind it, satisfies the evidence kind
the Approval Policy requires and is submitted for review.

This is the same shape as the gap the S3 slice's Delta 7 (g) closed for custom **objectives**. On `main` the objective
path is still the unclosed form (`backend/src/app/platform/objectives.py:840`:
`verifiable = {"objective_certificate": row.certificate_id is not None}`); the audit says S3's branch adds the pointer
check there (`objectives.py:725-737` on that branch). I did not read that branch, and it is not on `main`, so the
objective half is **not** a claim of this finding. The metric half has no counterpart in S3.

**Reachable only through a hand-written row.** Through the routes, `record_certificate` (`metrics.py:430`) writes the
`MetricCertificateRow` and sets `certificate_id` to its id in one transaction (`:460`, `:473`), and a failed
re-certification clears the id (`:442`, `:460`). Nothing in the repository's route surface stamps an id that has no
row.

## Evidence

Commands run in a worktree at `47d770e8fcbd2410fa101019ed8cf3aae69a1baa` (`git rev-parse HEAD` printed that SHA).

```
$ grep -n "verifiable = " backend/src/app/platform/metrics.py backend/src/app/platform/objectives.py
backend/src/app/platform/objectives.py:840:    verifiable = {"objective_certificate": row.certificate_id is not None}
backend/src/app/platform/metrics.py:794:    verifiable = {"metric_certificate": row.certificate_id is not None}

$ sed -n 1857,1860p backend/src/app/db/models.py
    #: FR-157's evidence. Not a foreign key to `metric_certificates`, for
    #: `CustomObjectiveRow.certificate_id`'s reason: the certificate points back the other
    #: way, and the CHECK below is what makes a status past `draft` mean something.
    certificate_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

$ grep -n "certified_metric_has_a_certificate" backend/src/app/db/models.py
1902:            name="certified_metric_has_a_certificate",

$ grep -n "MetricCertificateRow" backend/src/app/platform/metrics.py
42:    MetricCertificateRow,
153:def to_certificate(row: MetricCertificateRow) -> MetricCertificate:
352:            select(MetricCertificateRow)
354:                MetricCertificateRow.workspace_id == workspace_id,
355:                MetricCertificateRow.custom_metric_id == metric_id,
357:            .order_by(MetricCertificateRow.certified_at.desc())
438:) -> tuple[CustomMetricRow, MetricCertificateRow]:
448:    certificate = MetricCertificateRow(
```

Reading the last output: the only places `metrics.py` touches `MetricCertificateRow` are the serialiser (`:153`), a
read-by-metric-id (`:352-357`, "the latest rather than the one `certificate_id` names", per the docstring at `:346`),
and `record_certificate` (`:438-448`). `submit` (`:485-545`) contains no read of it.

The database does constrain the pair `status` / `certificate_id`
(`models.py:1910-1914`: `status IN ('draft', 'deprecated') OR certificate_id IS NOT NULL`, named
`certified_metric_has_a_certificate`). It constrains presence, not that the id resolves. The `_require_evidence`
docstring (`metrics.py` docstring of `_require_evidence`, the paragraph beginning "What was never at risk") relies on this CHECK for "what was never at risk" and says an uncertified metric
cannot be submitted; that sentence is true and does not address a certified-looking metric with a dangling id.

**The test that stamps a random id.** `backend/tests/test_custom_metrics_api.py:133` is `row.certificate_id =
new_uuid7()`, inside `_advance` (`:122`), whose docstring says the CHECK "is the invariant, not a fixture detail".
It is the existence proof that a row with a random certificate id is storable. Its only caller moves a metric to
`review` to test a status filter (`:351`); no test submits such a metric.

**What I did not do.** I did **not** execute the reproduction. This environment has no Postgres client
(`createdb: command not found`) and no per-worktree test database; a targeted pytest run reported
`1 skipped` / a database-not-found warning. The claim that `submit` returns 2xx for a dangling id therefore rests on
reading `_require_evidence` and `submit` as above, which is a code reading and not a run. The audit describes the red
reproduction (certify a metric through the real route, `UPDATE custom_metrics SET certificate_id = <random uuid>`,
`POST .../submit`; at head it returns 2xx and the request is created; the fix expects 409 `VALIDATION_FAILED`). It
should be run as the red test of the fix.

### The requirement

`02-modelling.md` FR-157: "A Custom Metric carries a `MetricCertificate` before submission, on FR-146's argument: a
metric that early-stops a fit decides when boosting halts and therefore changes the model."

`06-governance.md` FR-364 (§3.3 floor): `custom_metric` — `metric_certificate`; the floor kind may be added to and never
removed. `RL-1404` quotes it as failing closed "on a kind it cannot verify". Here the kind is "verified" by a null test,
which is not verification that a certificate exists.

## Severity (proposed; the lead's)

**MEDIUM.** The S3 audit's reading of reachability supports MEDIUM, and the brief gave the same. It is not HIGH: a
metric certificate carries no convexity check (`metrics.py:4-6`), so there is no "violated → extra Approver" rule for the
dangling id to hide, and the CHECK plus `record_certificate` mean the routes cannot produce the state. It is not LOW
because the evidence gate the Approval Policy names reads as satisfied by a pointer to nothing, and the `custom_objective`
twin is the same shape.

**Owner: WK-690.**

## Disposition

**Proposed: fix before close, owner WK-690; the lead gives the verdict.** Remedy:

In `_require_evidence`, resolve `row.certificate_id` to a `MetricCertificateRow` in the same workspace **and** with
`custom_metric_id == row.id` before counting the evidence kind verifiable; a missing, cross-workspace or
other-metric pointer is refused 409 `VALIDATION_FAILED` (the code S3 uses for the objective). Red test first, through
`submit`, with a hand-written random id and with a certificate row of another metric. A foreign key is not proposed:
the model comment at `models.py:1868-1871` records why the column is not one.

## What this finding does NOT claim

- It does not claim the state is reachable through any route. The audit and this essay both say a hand-written row is
  required.
- It does not claim a run: the 2xx is a code reading (see "What I did not do").
- It does not claim the `custom_objective` path is fixed or broken on any tree other than `47d770e8`; on that tree it has
  the same null test (`objectives.py:840`). Whether S3's branch closes it is that slice's record's to say.
- It does not claim a mispricing. `grep -n certificate_id backend/src/app/platform/approvals.py` has no match: the approval path never reads the id, so the dangling id is not consumed downstream of the evidence check by that module.
- The audit cited `db/models.py:1740` for the column; at `47d770e8` line 1740 is not that column (the metric column is
  `:1860`; `:1733` is the objective model's). This essay uses the lines at `47d770e8`.
