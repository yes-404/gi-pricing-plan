---
id: RL-1485
family: ruling
title: OQ-1486 raised — is a Validation Rule Set a Governed Artifact?
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-08            # original date 2026-09-30, set at the draft; minted 2026-10-08
owner: decision-maker
tree: 65b334792e65704206d2c21015690d7c613092cc
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-1486]
---

# RL-1485 — OQ-1486 raised: is a Validation Rule Set a Governed Artifact?

*Disclosure: drafted under working id 9989; minted as RL-1485 on 2026-10-08, in the T1 batch mint PR.*

## How this was ruled

- **Effort and source.** Filed at effort `medium`, on the maintainer's entry "2026-09-30
  11:23:26 BST — DECISION: validation-rule approval bypass: HIGH (not CRITICAL); owner and
  order; two follow-ons" (`~/gi-pricing-plan.local/channel/to-lead.md`). That entry reads:
  "Rule Sets are not in 06:64's Governed Artifact list: a separate spec question, not this
  defect. The DM files an OQ (options: govern rule-set composition; or keep it derived from
  approved rules; recommendation included), owner WK-1178". The lead relayed it.
- **What this record does.** It **decides nothing**. It raises the question and records the
  disposition of the two mirror rows it adds, because a spec edit is never made without a
  ruling record naming it (`.claude/roles/decision-maker.md`, *Tools*). The precedent is
  `RL-1265`, which raised `OQ-1266`.
- **Working ids.** 9989 for this record and 9987 for the question. Each was checked free on
  every `origin/*` branch, in every open PR's title and body, and in the channel files. Both
  are minted at the merge turn.

## Verified first, at 65b334792e65704206d2c21015690d7c613092cc

| Premise | Where | Present? | What the source says |
|---|---|---|---|
| Rule Set is not a Governed Artifact | `docs/specs/06-governance.md:64` | **absent** | The list names Validation Rule, but not Rule Set |
| No §3.3 evidence row, no evidence-floor key | `06` §3.3 (`:105-120`); `packages/model-schema/src/model_schema/approvals.py:101-108` | **absent** | `EVIDENCE_FLOOR` has `validation_rule`, not a rule-set key |
| A set version is published approved | `backend/src/app/platform/validation_rules.py:538` (`replace_rule_set`), `:643` (`status=APPROVED`); `backend/src/app/db/models.py:1195` (column default `"approved"`) | present | No review, and no `approvals.submit` call |
| Who may publish | `backend/src/app/api/validation.py:400-417` (`PUT /datasets/{slug}/rule-set`, `WriteDatasets`); `validation_rules.py:554-560` | present | `dataset:write` on the Dataset |
| Unapproved members refused | `validation_rules.py:582-591` | present | 409 `RULE_NOT_APPROVED` (FR-50) |
| A lowered severity refused | `validation_rules.py` after `:593` | present | 409, because an override may only raise (`01` §4.3) |
| The job runs the latest version | `validation_rules.py:439` (`rule_set_for`: `order_by(version.desc()).limit(1)`); `backend/src/app/worker/data_handlers.py:247`, `:272` | present | No status filter is needed today, since every version is approved |
| A missing layer is only a warning | `docs/specs/01-data-management.md` FR-45 (`:107`) | present | "a Rule Set with an empty layer is a configuration warning" |
| The Reference Dataset Version is pinned on the set | `01` FR-57 (`:119`) | present | So re-pointing it is a new set version |
| Precedent for "reviewed at the point of use" | `06` §3.3's struck Rate Table Version row; `03` FR-1186 | present | Its diffs reach approval inside the Rating Version |

Auditor-922's measurement is cited by the maintainer's entry, not re-run here. It shows an
approved rule reaching a Rule Set with 0 approval requests, and it is reported to
auditor-928 for the validation-rule finding.

## Ruled

**Nothing is decided.** `OQ-1486` is raised with four options and a recommendation, (a).
Its text lives in its two mirror rows, which are this record's disposition:
- `docs/open-questions.md`, the GOV section: full options, trade-offs and recommendation;
- `06` §10: the open row, which mirrors it.

The owner is WK-1178. The question is separate from the validation-rule approval-bypass
defect (HIGH), whose fix slice is WK-1178's too. The two are not folded together.

## What it obliges

- **This commit:** the two mirror rows, and this record.
- **The lead (roadmap §10 is the lead's file):** place `OQ-1486` on a decision-gate row.
  `.claude/skills/spec-change` says a new OQ goes onto the gate table in the same commit, but
  that table is not this role's file, so this record hands it to the lead. The suggestion is
  a gate before the WK-1178 validation-rule fix slice's leaf plan, since option (a) or (c)
  changes that slice's write set.
- **The resolver:** a ruling on `OQ-1486`. Under (a) or (c) that adds a `06` §2 entry, a §3.3
  row and an evidence-floor key, spec first.

## Acceptance — the violation that must become detectable

None yet. The acceptance belongs to the ruling that decides `OQ-1486`. Under (a), for
example: a new Rule Set version that removes a member is not run by validation until an
approval request for it is approved.

## Amended 2026-10-05 before mint: currency at origin/main `47d770e8`

*By the decision-maker session `dm-amend` (effort `medium`), on the lead's brief of
2026-10-05 09:55 BST. Citation and currency only: the question raised, its options and its
recommendation are unchanged. Every fact below was re-read at origin/main
`47d770e8fcbd2410fa101019ed8cf3aae69a1baa`, each code cite found by its symbol first. The
`tree:` field stays `65b33479`, because the table above is headed as verified there and its
cites are true there; this section carries their locations at `47d770e8`.*

- **J1: the premises still hold, at moved lines.**
  - `06-governance.md:64` still lists Validation Rule, but not Rule Set. `06` §3.3 is now
    `:105-149`. `EVIDENCE_FLOOR` is `packages/model-schema/src/model_schema/approvals.py:105-112`
    and still has `validation_rule` and no rule-set key.
  - `replace_rule_set` is `backend/src/app/platform/validation_rules.py:549` (was `:538`).
    It still creates the new set version with `status=APPROVED` at `:654` (was `:643`). The
    column default `"approved"` is `backend/src/app/db/models.py:1247` (was `:1195`), on
    `ValidationRuleSetRow` (`:1227`).
  - `PUT /datasets/{slug}/rule-set` (`WriteDatasets`) is `backend/src/app/api/validation.py:400-432`
    (was `:400-417`). The service's own `require_permission(… DATASET_WRITE …)` is
    `validation_rules.py:565-571` (was `:554-560`).
  - The unapproved-member refusal (409 `RULE_NOT_APPROVED`) is `validation_rules.py:593-602`
    (was `:582-591`). The lowered-severity refusal follows, from `:604` (was "after `:593`").
  - `rule_set_for` is `validation_rules.py:450` (was `:439`), still
    `order_by(ValidationRuleSetRow.version.desc())` (`:461`) with no status filter. The worker
    calls it at `backend/src/app/worker/data_handlers.py:247` and passes it on at `:272`
    (both unchanged).
- **J2: a related ruling has landed since this was raised, and decides nothing here.**
  `RL-1407` (merged by `c08a48e5`, #1109) rules FD-1414's remedy: **a rule set
  runs only approved, existing members**, delivered by `SL-1409` (PL-1408). That check is
  ruled, but it is **not yet in the code** at `47d770e8`: `rule_set_for` has no status
  filter. It closes a different gap from this question. It stops an unapproved member from
  running; it does not review a change of composition (a removed member, a re-pointed
  Reference Dataset Version). Whether it changes the weight of option (b) or (c) is for the
  ruling that decides `OQ-1486`. It is not re-weighed here.
- **J3: who depends on this.** `PL-1408` names this question at `:508`, `:610`, `:703` and
  `:1212`; its `replace_rule_set` allowance is temporary "pending OQ 9987 (working id)"
  (`:703`).
