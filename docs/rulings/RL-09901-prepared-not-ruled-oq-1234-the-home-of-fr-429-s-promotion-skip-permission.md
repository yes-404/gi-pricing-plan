---
id: RL-9901
family: ruling
title: PREPARED, NOT RULED — OQ-1234, the home of FR-429's promotion-skip permission
status: draft                  # NOT a permitted RL status (§1.2: active → superseded | retired); deliberate, see "Status of this record"
created: 2026-09-30
owner: decision-maker
tree: aa14e90dd77c7461aa35cc6461557b129959463f
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-1234, RL-1232, PL-1237, CR-1247]
---

# RL-9901 — PREPARED, NOT RULED: OQ-1234, the home of FR-429's promotion-skip permission

## Status of this record — read this first

**Nothing here is ruled.** This is a *prepared* ruling, written at effort `medium` under the
maintainer's decision by delegation of 2026-09-30 00:42:01 BST (`to-lead.md`, entry headed
"#933 READ BACK; DECISION: the DM PREPARES the blocked rulings on medium now, and RULES only
on effort high"). It is not filed as decided, and nothing may rely on it: `OQ-1234` stays
**open**, no spec text is amended, the roadmap §10 gate row "Before WK-674 Slice 2" stays
open, and **SL-1256 (WK-674 Slice 2) does not activate on it**. The ruling is the later pass
at effort `high`, which re-reads this record, confirms or revises it, and only then rules.

**`status: draft` is not a status a ruling may carry.** `document-ids.md` §1.2 gives RL the
lifecycle `active → superseded | retired`, and `scripts/audit-docs.py` check 33
(`_STATUS_SUBSET["RL"]`) refuses anything else. The status is kept at `draft` on purpose, and
check 33's failure on this file is expected: a prepared record that the gate refuses cannot
be merged as a ruling by accident. **Proposed form for the ruling pass:** set `status:
active`, retitle without the "PREPARED, NOT RULED" prefix, mint the id, and apply the
disposition in the same commit. The alternative — `status: active` now — would make the
header say "authoritative" about a record that is not.

Working id 9901, checked free at the time of filing: no `[A-Z]{2,3}-0?9901` token on
`origin/main` or any `origin/*` or local branch, nor in `~/gi-pricing-plan.local/channel/`.

## Verified first, at aa14e90dd77c7461aa35cc6461557b129959463f

**The question** (`docs/open-questions.md:195`; mirror `docs/specs/07-platform.md:512`):
where does `07` FR-429's *"unless the workspace policy explicitly permits skipping with a
recorded reason"* live, and where is the recorded reason held?

**Why it blocks.** FR-429 as amended by `RL-1232` DP-7 (`07-platform.md:140`): the deploy
route refuses with `PROMOTION_ORDER_VIOLATION`, the `prod` approval submission requires
`uat_deployment` evidence and refuses with `EVIDENCE_INCOMPLETE`, and **both read one
predicate** — a successful `uat` deployment, *or a skip the workspace policy permits, with its
reason recorded*. `PL-1237` puts the decision in Slice 2 (`PL-1237:419-422`, `:795-798`) and
holds Slice 2's leaf plan at `draft` until it is decided (`:805`); roadmap §10 gate row
(`docs/roadmap.md:1496`).

**Premise re-checked at this tree** (`RL-1232`'s note was read at `c9f50232`; WK-674 S1,
#933, has landed since):
- `git grep -nE 'class (Deployment|Environment|WorkspacePolicy)\b' -- backend packages` →
  one hit, `backend/src/app/config.py:32` (the runtime-mode enum; `RL-1232` and `OQ-1234` cite
  `:31`, one line earlier — the line moved, the fact did not).
- `git grep -n PROMOTION_ORDER_VIOLATION -- backend packages frontend` → only
  `backend/src/app/errors.py:62`. Raised nowhere.
- `git grep -niE 'skip|promot' -- packages/model-schema/src/model_schema/approvals.py` → rc 1,
  no hit. The skip still has no schema home.

**What already exists that an answer can build on** (the evidence the options turn on):
- `ApprovalPolicy` / `ApprovalPolicyEntry`
  (`packages/model-schema/src/model_schema/approvals.py:111-160`): frozen, `extra="forbid"`,
  per artifact type **and per target environment** (`environment: str | None`, `:119-121`);
  `entry_for(artifact_type, environment)` resolves the environment-qualified entry first
  (`:146-160`). `EVIDENCE_FLOOR["deployment"] = ("rating_version_approval",
  "uat_deployment")` (`:107`).
- Its write path, `set_policy` (`backend/src/app/platform/approvals.py:137-180`), is already
  permission-gated (`admin:manage_roles`), refuses a policy below the evidence floor
  (`POLICY_BELOW_EVIDENCE_FLOOR`), and writes an audit event with the before-image.
- `06` §4.2 (`docs/specs/06-governance.md:305-331`) already specifies a **policy-level
  exception with a mandatory reason** of the same kind: `"expedited": {"enabled": true,
  "approvers_required": 1, "requires_reason": true, "reported_in_exception_log": true}`
  (FR-385, `06-governance.md:181`). **It is unbuilt**: `git grep -n -i expedited -- packages
  backend/src` → no hit, and `ApprovalPolicy`'s `extra="forbid"` would refuse §4.2's document
  as written (it also carries `separation_of_duties` and per-entry `escalation`, unmodelled).
  That is a pre-existing spec/code gap outside this question, recorded here as an observation
  for the ruling pass, not ruled.

## Options

| | Option | For | Against |
|---|---|---|---|
| (a) | **A new workspace-policy object in `model-schema`** (ADR-704 contract change, generated to `docs/contracts/`) | Typed, versioned, validated; route and verifier import one definition; a clean home for future non-approval workspace policy | A new artifact shape, contract, contract guard, write route, permission and audit event — all of which `set_policy` already has for the approval policy; a second policy document beside the one the evidence floor already reads, so the two halves of DP-7's one predicate read two documents |
| (b) | **Approval-policy configuration**: a field on the environment-qualified `deployment` entry of `ApprovalPolicy` (e.g. which predecessor environments may be skipped, and that a reason is required); the per-act reason held on the `uat_deployment` evidence item / the Deployment record the skip produces | The `uat_deployment` floor already reads this document, so route and floor read the same one — DP-7's *a permitted, recorded skip **is** the evidence item* gets a direct home; the write path is already gated, floor-checked and audited; per-environment keying already exists (`entry_for`); §4.2's `expedited` block is precedent for a policy-level exception with `requires_reason` in this same document | A `07` promotion-order rule configured in `06`'s approval policy; the deploy route must read the approval policy (a `07` → `06` read the dependency direction must permit — to be checked by the ruling pass against `07` §7 and `.importlinter`); `admin:manage_roles` gates it, not an environment-scoped permission |
| (c) | **An Environment setting** (`07` FR-431, resolved by FR-446's precedence) on the Environment object Slice 2 creates | Sits with FR-428's promotion order; audited on change | **Its resolution is exactly what `OQ-1235` asks** — FR-446's precedence has no Environment level — and `OQ-1235` is gated *Before WK-674 Slice 3* (`roadmap.md:1497`), so (c) makes Slice 2 wait on Slice 3's gate; a Setting is an untyped value no schema constrains, so the predicate reads configuration rather than a contract |
| (d) | **A field on the Environment record itself** (typed, on the `model-schema` shape Slice 2 creates), e.g. `skippable: bool` on the environment that may be bypassed | Typed and next to the promotion order; no dependency on `OQ-1235` | The evidence floor then reads two documents (policy for the floor, Environment for the skip), which is what DP-7's one predicate was ruled to avoid; the permission is workspace governance, and an Environment edit is not governed by the policy path |

## Provisional recommendation — (b), not ruled

**(b)**, the field on the environment-qualified `deployment` entry of `ApprovalPolicy`, with
the per-act reason carried by the `uat_deployment` evidence item the skip produces. This
agrees with `OQ-1234`'s own recommendation.

**The one piece of evidence that decides it:** the `uat_deployment` floor is already read from
`ApprovalPolicy` (`approvals.py:107`, `effective_evidence`), and DP-7 requires the route and
the floor to read **one** predicate — so the only home in which both halves read one document
without a new shape is the document the floor already reads. (c) is excluded independently:
it would make Slice 2 wait on `OQ-1235`, gated one slice later.

**Left for the ruling pass at effort `high`:** (1) whether the field sits on the `deployment`
entry (per target environment) or as a top-level block beside a future `expedited` (the §4.2
precedent); (2) the dependency-direction check for the deploy route reading
`platform/approvals.py`; (3) whether `set_policy`'s `admin:manage_roles` is the right gate for
a skip permission, given `CR-1212` item 4's environment-scoping of `deployment:promote` lands
in the same slice; (4) the spec amendments (`06` §4.2, `07` FR-429) that would be this
ruling's disposition.

## Interaction to read at the ruling pass

*Added 2026-09-30 at the lead's request.* **Option (b) and the unmodelled `06` §4.2 keys touch
the same shape.** Option (b) adds a skip-permission field to `ApprovalPolicy`'s
environment-specific `deployment` entry (`ApprovalPolicyEntry`,
`packages/model-schema/src/model_schema/approvals.py:111-122`). `06` §4.2
(`06-governance.md:305-331`) already declares keys the model does not carry: the top-level
`expedited` block (FR-385, which carries `requires_reason`), `separation_of_duties`, and the
per-entry `escalation`. Both models use `extra="forbid"`. So:
- any new field that (b) adds must be written into §4.2's document in the same change, or
  §4.2 and the model diverge further;
- the ruling pass decides whether the skip belongs on the entry or as a top-level block beside
  `expedited`, which is the nearest precedent for a policy-level exception with a reason;
- if FR-385 is built first, or later, it changes the same model. The ruling should name the
  order, or say that the two are independent.

Observed, not ruled. The unmodelled-keys gap is now filed as finding `FD-1281`; the
`status: draft` gap as `FD-1280`.

## Ruled

**Nothing.** This heading is present because check 37 requires it of the ruling family. It
records no decision. The provisional recommendation above is a draft for the ruling pass.

## What it obliges

**Nothing, and nobody.** No slice activates on this record, no plan freezes on it, and no
spec, open-question, roadmap or plan text is changed by it. `OQ-1234` stays open.

## Acceptance — the violation that must become detectable

*Provisional, for the ruling pass to confirm or revise.* If (b) is ruled: a `prod` deployment
of a Rating Version with no successful `uat` deployment and no skip permitted by the
workspace's `ApprovalPolicy` is refused at the route with `PROMOTION_ORDER_VIOLATION` **and**
at the approval submission with `EVIDENCE_INCOMPLETE`, by one predicate function that both
call; a permitted skip without a recorded reason is refused by both; and a test that flips the
policy field flips both refusals together.
