---
id: FD-1511
family: finding
title: The quantile template certifies convexity violated, and no second Approver is enforced
status: closed
created: 2026-10-08            # original date 2026-10-01, set at the draft; minted 2026-10-08
owner: auditor
tree: a978dc2297bc8bfcc1c4da09ded37cefdcf92156
corrected_by: []
relates: [WK-690, FR-152, FR-163, FR-354]
---

# FD-1511 — The quantile template certifies convexity violated, and no second Approver is enforced

**Working id 9780**, allocated by the lead and ordered by the maintainer on 2026-10-01: "the quantile template certifies convexity 'violated' (objectives.py:408-412, needing a second Approver) and nothing enforces it." Found by the decision-maker while ruling the DP-S3-4 question of PL 9789; its ruling, `RL-1362` (working id 9782 when this was filed; the draft PR #1040 was closed unmerged, and the record reached main separately), is on main. The header `tree:` is `origin/main^{tree}` at `ef5dc6e7` (re-pinned 2026-10-05, see the amendment below); the evidence below was measured at `101e32dc` (tree `934e9a44b99705466e9e612eb245761dc8e33884`) unless it says otherwise.

## Finding

**Severity: MEDIUM (provisional).** The maintainer's rule: "any approval already passed with a violated certificate raises it". **None was found** in this repository's reachable stores (Evidence 4), so it stays MEDIUM; the fixture-stamped rows of Evidence 4(c) are reported for the lead to rule on, not counted as approvals. **Owner WK-690**, fixed by Slice 3's DP-S3-4 (the DP-S3 ruling, `RL-1362`: `approvers_required` = policy + 1 when the latest certificate's convexity is `violated`, both kinds). The finding is that FR-152's "requires an additional Approver" is a numbered requirement with no enforcing code, and that one shipped template already meets the condition.

## Evidence

**1. The requirement, by locator.** `docs/specs/02-modelling.md`, FR-152: a non-convex objective "is flagged `convexity: violated`, requires the hessian clipping strategy to be declared (`clip_to_min`, `abs`, `gauss_newton`), and requires an additional Approver". FR-163: "`expression` objectives with `convexity: violated` need two Approvers (FR-152)". Neither carries a dated amendment narrowing the clause; the 2026-08-25 amendment to FR-152 is about the surface (a view must not render `violated` as a failure) and keeps the verdict `certified_with_findings`. `docs/specs/06-governance.md` FR-354: the Approval Policy defines "required approver count" per artifact type; FR-364 makes the policy a floor that may only add. Nothing in `06` lets a certificate change the count.

**2. The certificate says it.** `packages/pricing-core/src/pricing_core/modelling/objectives.py:408-412` (`_quantile_hess`): the pinball loss is piecewise linear, so its exact second derivative is negative on the under-prediction side, "why FR-152 exists, and why this template certifies `convexity: violated` and needs a declared strategy and a second Approver". `_convexity_check` (`:1278-1300`) emits `CheckStatus.VIOLATED` when any sampled hessian is negative, with the detail "FR-152 requires an additional Approver"; it is a prose string and nothing reads it back. `CertificateResult.outcome_of` (`packages/model-schema/src/model_schema/objectives.py:724-736`) maps `violated` to `certified_with_findings`, deliberately not `failed`.

**3. Where the second Approver should be required, and is not.** The path is `platform/objectives.py` `submit_for_review` (`:558`) → `_require_evidence` (call `:589`) → `approvals.submit` (`:591`) → `platform/approvals.py` `submit` (`:240`, was `:225`) → `decide` (`:345`, was `:330`).
- `_require_evidence` (`platform/objectives.py:830-`) checks only that `row.certificate_id is not None` for `objective_certificate`. It never loads the certificate payload.
- `approvals.submit` takes no certificate input and stores `approvers_required=entry.approvers_required` (`approvals.py:301`, was `:286`), the policy entry's number alone.
- The default entry is `packages/model-schema/src/model_schema/approvals.py:291-292` (was `:211-212`): `custom_objective`, `approvers_required=1`.
- `decide` resolves the outcome with `_resolve_status(decision, approvals, row.approvers_required)` (`approvals.py:462`, was `:447`), and `_resolve_status` (def `:596`, was cited `:588`) returns `APPROVED` once `approvals >= required` (`:603`).
- `git grep -n "convexity\|CheckStatus.VIOLATED\|\"violated\"" -- backend/src` returns two hits, both prose (`platform/metrics.py:6`, `platform/objectives.py:471`): no backend code reads a convexity status.

So at the default policy a `violated` objective is approved by one non-author Approver. FR-163's own text says two. Consequence: the objective reaches `approved`, and a Model fitted under it becomes approvable (`FITTABLE_OBJECTIVE_STATUSES`, `model_schema/objectives.py:177`, lets a fit use `certified`, `review` or `approved`, and a model "cannot be approved until the objective is"). The quantile template is also the one FR-199's paired-quantile bounds must use (`platform/modelling.py`, `_refuse_a_bound_that_is_not_a_quantile_fit` `:734`, the template refusal at `:760-:765`; was cited `:760`), so the interval bounds of a prediction rest on it.

**4. Reach (this repository's reachable stores only; not any deployment, of which there is none).**
(a) Committed code. Predicate: `git grep -nE "ObjectiveTemplate\.QUANTILE|template=\"quantile\"" 101e32dc -- backend/tests packages/pricing-core/tests`: 3 lines, all tests. `backend/tests/test_paired_quantile_models.py:97` builds the quantile objective and `mark_approved`s it with a stamped request of `approvers_required=1` (`backend/tests/approved_rows.py` `decided_request`, `:47-64`, was `:48-64`); its docstring says the approval is stamped and does not drive the two-person path. It is called 7 times (`git grep -c "_approved_quantile(" -- backend/tests`). `packages/pricing-core/tests/test_gbm.py:1576` is a core-only fit. No seed, example or script uses the template: `git grep -il quantile -- examples scripts ':!*.md'` lists three bench scripts, all statistical percentiles.
(b) Local Postgres, container `gi-pricing-postgres-1`, user `gipricing`, every database matching `gipricing%` (82 of them; 3 predate the objectives tables and error with "relation does not exist"). Script, run per database:
`select count(*) from custom_objectives where template='quantile'`;
objectives with a violated convexity check: `... exists (select 1 from objective_certificates c, jsonb_array_elements(c.payload->'checks') k where c.custom_objective_id=o.id and c.objective_version=o.version and k->>'name'='convexity' and k->>'status'='violated')`;
approvals with a violated certificate: `select count(*) from approval_requests r join custom_objectives o on r.artifact_ref='custom_objective:'||o.slug||'@'||o.version and r.workspace_id=o.workspace_id where r.status='approved' and <the exists clause>`.
Result: 77 databases hold none. **Two hold 32 quantile objectives each** (`gipricing_wt-ci-structure`, `gipricing_wt-paths-d9-d13`, scratch gate databases created 2026-09-06 and 2026-09-04), **all 32 with a violated convexity check** (32 of 32 in each; the template certifies `violated` every time it is certified). The control: the same join finds the 2 approved `poisson` requests in each of those databases, so the join is not blind.
**Approvals that passed with a violated certificate: 0** (`approval_requests` with `artifact_type='custom_objective'` on a quantile objective: 0 in all databases).
(c) The 32 objectives in each of the two databases have `status='approved'`, `approval_request_id` null, and audit events of `created` and `certified` only. They are test-fixture rows stamped approved (the `_approved_quantile` shape above) in databases that predate the approval guard trigger, **not approvals that passed**. They are reported because they are the only `approved` violated objectives in the reachable stores; the lead may treat them as the maintainer's trigger for HIGH, and I have not.
(d) Models on the quantile template: **23** `models` rows in each of those two databases (of 251 and 223) whose `spec` names one of the quantile objectives (`select count(*) from models m where exists (select 1 from custom_objectives o where o.template='quantile' and m.spec::text like '%custom_objective:'||o.slug||'@'||o.version||'%')`). They are the paired-quantile test models. No other database holds one.

## Disposition

**Owner WK-690, fixed by Slice 3's DP-S3-4** (the DP-S3 ruling, `RL-1362`; its draft PR #1040 was closed unmerged): `submit_for_review` passes an increment of one to `approvals.submit` when the latest certificate's `convexity` check is `violated`, so `approvers_required` is policy + 1, for both kinds; FR-163 gets a dated clause correction. That ruling's own red-first step counts the violated fixtures at the base, and this finding's counts are the base for it. The finding stays open until Slice 3 merges with a test that approves a `violated` quantile objective with one approver and finds it still in `review`. Recheck then: re-run the Evidence 4 SQL scoped to custom objectives, and `git grep` the backend for a convexity read.

**Amended 2026-10-05 before mint: citations re-anchored, nothing decided and the scope not widened.** Re-read at `origin/main`
`ef5dc6e7` (tree `a978dc2297bc8bfcc1c4da09ded37cefdcf92156`, now the header's `tree:`). The claim holds: `git grep -n "convexity\|CheckStatus.VIOLATED\|\"violated\"" origin/main -- backend/src`
still prints exactly two prose hits (`platform/metrics.py:6`, `platform/objectives.py:471`), so no backend code reads a convexity
status; `approvals.submit` still stores `approvers_required=entry.approvers_required` alone. Moved cites, each found by symbol:
`submit` `:225` → `:240`; `decide` `:330` → `:345`; `approvers_required=entry.approvers_required` `:286` → `:301`; the
`_resolve_status` call `:447` → `:462`; the `_resolve_status` def, cited `:588`, → `:596` (its return at `:603`); the default
`custom_objective` policy entry `model_schema/approvals.py:211-212` → `:291-292`; `decided_request` `:48-64` → `:47-64`; the
quantile-template refusal `platform/modelling.py:760` → inside `_refuse_a_bound_that_is_not_a_quantile_fit` (`:734`). Unmoved,
re-read: `_quantile_hess` (`objectives.py:407`, its comment at `:411`), `_convexity_check` `:1278`, `CertificateResult.outcome_of`
`:724`, `FITTABLE_OBJECTIVE_STATUSES` `:177`, `submit_for_review` `:558`, `_require_evidence` `:830`. Corrected predicate: Evidence 4(a)
named the pathspec `packages/*/tests`, which matches nothing under git's wildcard rule (it prints 1 line, not 3); the runnable
form `-- backend/tests packages/pricing-core/tests` prints the three lines the essay counts, at `101e32dc` and at `ef5dc6e7`
alike (`test_paired_quantile_models.py:97`, `test_gbm.py:1576` and `:1577`). Working ids re-pointed: `RL-1362` (the ruling, working id 9782);
`PL 9789` is `PL-1382` (minted 2026-10-03; `PL-1371` still reads "PL 9789 ... to mint", a frozen record). Evidence 4(b)-(d), the 82-database
SQL, is a dated 2026-10-01 measurement and was **not re-run** (a gate slot is held). **Not done here, by order:** the maintainer's
widening to six templates (asymmetric_squared, huber, pseudo_huber (violated only at δ=1), quantile, zero_inflated_poisson, focal_binomial)
and S3's evidence wait for S3's merged ledger and are a mint-time item.

## Resolution (2026-10-05)

Re-anchored 2026-10-05 at main `caa4e411`. **The defect is fixed by SL-1273** (WK-690 Slice 3, #1122, squash `36a9f483`; `git merge-base --is-ancestor 36a9f483 origin/main` exits 0; ledgered in `LG-1412`; the ruling is `RL-1362` DP-S3-4). The decision to mint this record closed is the maintainer's, by delegation, in the lead's channel file (`to-lead.md`), the entry headed *"2026-10-05 12:58:22 BST — DECISIONS (the maintainer, by delegation): FD-1511; DP-A; OQ 9739; RL 9715 DP-2; PL 9716 DP-B; the OQ 9739 row"*: **mint closed, fixed by SL-1273, MEDIUM; no widening.** Severity stays MEDIUM.

**What main does now**, read at `caa4e411`:
- `backend/src/app/platform/objectives.py` `submit_for_review` loads the latest `ObjectiveCertificateRow` for the objective, sets `non_convex` when any check of `to_certificate(latest).result.checks` has `name == "convexity"` and `status is CheckStatus.VIOLATED`, and passes `additional_approvers=1 if non_convex else 0` to `approvals.submit`. (The convexity read starts at the `# FR-152 / RL-1362 DP-S3-4` comment, `:745`; the `additional_approvers` argument is at `:772`.)
- `backend/src/app/platform/approvals.py` `submit` takes `additional_approvers: int = 0` and stores `entry.approvers_required + additional_approvers` (`:301`), fixed at submission. `decide` and `_resolve_status` are unchanged and compare against that stored count.

**The proof, read to its asserts.** `test_each_template_certified_violated_needs_the_extra_approver` (`backend/tests/test_objective_submission.py:387`) is parametrized over `_VIOLATED_TEMPLATES`, six templates: `asymmetric_squared`, `huber` (delta 1000), `pseudo_huber` (delta 1), `quantile` (alpha 0.9), `zero_inflated_poisson` and `focal_binomial`. For each, it certifies through the real `OBJECTIVE_CERTIFY` Job on the template's `default_sampling` grid and asserts the job `SUCCEEDED`, then asserts `convexity.status is CheckStatus.VIOLATED`, then `required == 2` after `_submit`, and then that one approval leaves the objective in `ObjectiveStatus.REVIEW`. The two-approver and three-approver cases at policy one and two are `test_a_violated_objective_needs_two_approvers_at_policy_one` and `..._three_approvers_at_policy_two`, for both kinds.

**The six-template widening owed in the amendment above is superseded**, not done: that test covers all six, on the certificate each one produces, so no separate widening of this record's Evidence 4 is owed. Evidence 4(b)–(d) stays a dated 2026-10-01 measurement (not re-run).

**Cites above are the defect-state and are not re-read.** Evidence 1–3 describe `101e32dc` and `ef5dc6e7`, before SL-1273. At `caa4e411` the claim "no backend code reads a convexity status" no longer holds: `git grep -n "convexity\|CheckStatus.VIOLATED" -- backend/src` now also hits `platform/objectives.py:745` and `:761`. Cites that moved at `caa4e411`, by symbol: `_quantile_hess` `objectives.py:408` (unmoved); `_convexity_check` `:1278` → `:1323`; `CertificateResult.outcome_of` `model_schema/objectives.py:724` → `:788`; `FITTABLE_OBJECTIVE_STATUSES` `:177` → `:179`; `approvals.decide` `:345` → `:354`; `_resolve_status` `:596` → `:605`; `_require_evidence` (objectives) `:830` → `:1012`; `approvals.submit` `:240` (unmoved). Left for the open follow-up: `LG-1412` records `pseudo_huber` at delta 100, 1000 and 100000 certifying `failed`, not `violated`; that is not this finding's and is unfiled.

**What the mint sets:** `status: closed` in this file's header (the form `FD-1200` uses), and the register row's Decision cell in the closed form this section's date and citation give.

**Re-measured 2026-10-08 at `origin/main` `d10420df`; closed.** `git merge-base --is-ancestor 36a9f483 origin/main` exits 0. `backend/src/app/platform/objectives.py`: the `# FR-152 / RL-1362 DP-S3-4` comment at `:745`, the `CheckStatus.VIOLATED` read at `:761`, `additional_approvers=1 if non_convex else 0` at `:772`. `backend/src/app/platform/approvals.py`: `additional_approvers: int = 0` at `:249`, `approvers_required = entry.approvers_required + additional_approvers` at `:301`. Tests at `backend/tests/test_objective_submission.py`: `test_a_violated_objective_needs_two_approvers_at_policy_one` `:348` and `test_each_template_certified_violated_needs_the_extra_approver` `:387`. The `:745`, `:761` and `:772` cites above were read at `caa4e411` and are unchanged at `d10420df`.
