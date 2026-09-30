---
id: RL-9989
family: ruling
title: OQ-9987 raised — is a Validation Rule Set a Governed Artifact?
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 65b334792e65704206d2c21015690d7c613092cc
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-9987]
---

# RL-9989 — OQ-9987 raised: is a Validation Rule Set a Governed Artifact?

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

**Nothing is decided.** `OQ-9987` is raised with four options and a recommendation, (a).
Its text lives in its two mirror rows, which are this record's disposition:
- `docs/open-questions.md`, the GOV section: full options, trade-offs and recommendation;
- `06` §10: the open row, which mirrors it.

The owner is WK-1178. The question is separate from the validation-rule approval-bypass
defect (HIGH), whose fix slice is WK-1178's too. The two are not folded together.

## What it obliges

- **This commit:** the two mirror rows, and this record.
- **The lead (roadmap §10 is the lead's file):** place `OQ-9987` on a decision-gate row.
  `.claude/skills/spec-change` says a new OQ goes onto the gate table in the same commit, but
  that table is not this role's file, so this record hands it to the lead. The suggestion is
  a gate before the WK-1178 validation-rule fix slice's leaf plan, since option (a) or (c)
  changes that slice's write set.
- **The resolver:** a ruling on `OQ-9987`. Under (a) or (c) that adds a `06` §2 entry, a §3.3
  row and an evidence-floor key, spec first.

## Acceptance — the violation that must become detectable

None yet. The acceptance belongs to the ruling that decides `OQ-9987`. Under (a), for
example: a new Rule Set version that removes a member is not run by validation until an
approval request for it is approved.
