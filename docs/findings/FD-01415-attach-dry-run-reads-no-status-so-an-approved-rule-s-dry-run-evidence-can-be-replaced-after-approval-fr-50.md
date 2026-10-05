---
id: FD-1415
family: finding
title: attach_dry_run reads no status, so an approved rule's dry-run evidence can be replaced after approval (FR-50)
status: active
created: 2026-10-05            # the mint date (check 31); filed 2026-10-01
owner: auditor
tree: 49cd25be441382aebc1cc9c9ff325bd73fd81bc1
corrected_by: []
relates: [WK-1178, FD-1356, FR-4, FR-50]
---

# FD-1415 — attach_dry_run reads no status (FR-50)

## Finding

**Severity: MEDIUM** (FD 9754's class: an approved artifact's evidence can move after approval).
**Owner: WK-1178.** **The remedy rides in the FD-1356 fix slice (PL 9762).** All three are the
maintainer's, in the entry headed *"2026-10-01 11:07:12 BST — #1070 audit: observation (1) → its
OWN FD (option ii), MEDIUM, deadline before the P2 exit demo; observation (2) → an FD, MEDIUM,
remedy RIDES in the FD-1356 fix slice; F1–F4 adopted"* (lead's channel, `to-lead.md`). **Working
id 9747**, minted at the records PR. Raised as an observation by the decision-maker `dm-1356` in
RL 9750 (#1070, "Observed, not ruled") and confirmed by auditor-1070.

> **Amended 2026-10-05 before mint:** working ids that have since minted, re-pointed. **`RL 9750` is
> `RL-1407`** (`docs/rulings/RL-01407-…`, merged as #1070; its §"FD 9747 (working id)" rules the remedy
> as a refusal with the new code `RULE_VERSION_IMMUTABLE` (409), which settles the error-code question
> left to `dm-1356` in §Disposition below); **`PL 9762` is `PL-1408`** (`docs/plans/PL-01408-…`,
> Acceptance 19, Step 3a; `status: draft` at that tree, activation PR #1112 open); **`FD 9754` is
> `FD-1393`**. The working ids still written in this essay stand as what was written then. **Code
> cites re-checked at `origin/main` `ef5dc6e7317281ac9d1840fa61861597e3c1b8b1`:** `attach_dry_run`
> `validation_rules.py:352-363` and `01-data-management.md:520-523` unchanged; the handler's
> `store_report` then `attach_dry_run` calls are now `data_handlers.py:289-293` (the call at `:293`);
> `seed.py:443` unchanged; the two `models.py` cites moved and are re-pointed by symbol below.
> The remedy is not built (`PL-1408` Step 3a). The finding's substance is unchanged.

**FR-4** (`docs/specs/00-overview.md`, "Every Artifact is immutable once it leaves `draft`") and
`01` §4.5 step 4 (`docs/specs/01-data-management.md:523`): *"`approved` rules are immutable; edits
create a new rule version needing re-approval."* Step 2 (`:520-521`): the dry-run result is the
evidence the Approver judges.

**What happens today.** `attach_dry_run` (`backend/src/app/platform/validation_rules.py:352-363`)
is: `load_rule`, `row.dry_run_report_id = report_id`, `session.flush()`. **It reads no
`status`.** Its callers add none:

- the route `POST /api/v1/validation-rules/{rule_id}/dry-run`
  (`backend/src/app/api/validation.py:302-330`) loads the rule with `load_rule` and submits a
  `DATASET_VALIDATE` job with `dry_run_rule_id`; no status read, any rule, any status;
- the handler (`backend/src/app/worker/data_handlers.py:289-296`) stores the report, then calls
  `attach_dry_run(rule_id=…, report_id=row.id)` for any `dry_run_rule_id`.

So **an `approved` rule can be dry-run again and its `dry_run_report_id` re-pointed at a new
report**: one that records an `error` outcome, or one against a different Dataset Version. The
approval stands, the approver's `approval_requests`/decision rows stand, and the evidence the
approver judged is no longer the evidence the rule row points at.

**Nothing at the database stops it.** The `validation_rules` CHECK
(`backend/src/app/db/models.py`, `ValidationRuleRow`'s `approved_rule_dry_run_and_separate_approver` `CheckConstraint`, `:1205-1209` at `origin/main` `ef5dc6e7317281ac9d1840fa61861597e3c1b8b1`) requires only `dry_run_report_id IS NOT NULL` for an
approved non-built-in row; `dry_run_report_id` has no foreign key (`models.py`, the `dry_run_report_id` column, `:1174` at that tree). The
RL-1301 approval trigger fires on `NEW.status = 'approved'`; an update of this column on a row
already backed by an approved request meets its evidence condition, so I expect it passes. **I
did not run it.**

## Why it matters

1. **It defeats the check PL 9762 builds.** The FD-1356 fix refuses an `error` or unreadable dry
   run at submit, at the generic resolver and at the carry (RL 9750 DP-3). All three points are
   *before* `approved`. After approval nothing reads the report again, so the evidence check is
   satisfied once and then replaceable.
2. **It is the same class as FD 9754.** An approved artifact changed in place, which FR-4 and
   `01` step 4 forbid, with an audit trail at best. A `validation_rule.approved` event citing a
   report that the row later stops pointing at makes the audit say one thing and the row
   another.
3. **DP-1's legacy path needs `attach_dry_run` from `review`, not from `approved`.** RL 9750 DP-1
   names it: a rule in `review` with no request, or whose report dangles, is dry-run again from
   `review`. A refusal for `approved` alone leaves that path intact.

## Evidence

**Code:** the chain above, at tree `49cd25be441382aebc1cc9c9ff325bd73fd81bc1`.

**Red reproduction: reasoned from code, not run** (shared test database, F45). A red test:
walk a rule to `approved` (`backend/tests/approved_rows.py`'s `mark_approved`, or the API chain),
POST `/dry-run` against a version whose data makes the rule `error`, drive the Job, and assert the
route refuses (409) and `dry_run_report_id` is unchanged. Today the Job succeeds and the row
points at the new report.

**Exposure, measured 2026-10-01 at 11:09 BST (10:09 UTC), read-only,** `docker exec
gi-pricing-postgres-1 psql -U gipricing -d <db>` over every `gipricing%` database, each inside
`BEGIN READ ONLY … ROLLBACK`:

```sql
BEGIN READ ONLY;
select count(*) filter (where r.builtin is not true and r.status='approved'),
 count(*) filter (where r.builtin is not true and r.status='approved' and r.dry_run_report_id is not null and v.id is null),
 count(*) filter (where r.builtin is not true and r.status='approved' and v.error_count>0),
 count(*) filter (where r.builtin is not true and r.status='approved' and v.id is not null and v.error_count=0)
from validation_rules r left join validation_reports v on v.id=r.dry_run_report_id and v.workspace_id=r.workspace_id;
ROLLBACK;
```

Result over the **77 databases that have both tables: 314 approved non-built-in rules; 314 whose
`dry_run_report_id` names no report in their workspace (the demo seed's `new_uuid7()`,
`examples/fremtpl2/seed.py:443`); 0 whose report records an `error`; 0 whose report exists and is
clean.** So **no local approved rule's evidence has been replaced by an `error` report**, and
every user-authored approved rule in a local database already has dangling evidence (RL 9750 DP-3
(iii) and DP-5). **Limits:** local databases only; 3 of the 80 `gipricing%` databases are not
counted (no such tables, or an error I did not inspect); the query shows the evidence now, not
whether it was ever replaced (no history of `dry_run_report_id` is kept; `validation_rule.*`
audit events carry none of it); and an all-dangling population cannot show that the `error_count`
filter fires on a real report.

## Severity (the maintainer's): MEDIUM · Owner (the maintainer's): WK-1178

## Disposition (the maintainer's, 11:07:12)

**The remedy rides in the FD-1356 fix slice (PL 9762): refuse `attach_dry_run` on an `approved`
rule, allowed from `review` (as DP-1's legacy path needs), red first.** One refusal in the same
file and the same approval-integrity theme. The refusal belongs in `attach_dry_run` (the service),
not only the route, so the handler cannot bypass it (the auditor's addition to the
maintainer's entry). The error code (a new one, or an existing
`409` such as the `ARTIFACT_IMMUTABLE` that FD 9754's recommendation names) is for `dm-1356`, who
adds the verbatim `01` text if needed. PL 9762's acceptance gains the item before it merges,
in place.

## Disposition

Open. Filed by the auditor, 2026-10-01, on the maintainer's 11:07:12 decision; the verdict is the
lead's.
