---
id: FD-1281
family: finding
title: 06 §4.2 shows three ApprovalPolicy keys the model refuses, and FR-385 is unbuilt
status: active
created: 2026-09-30
owner: auditor
tree: 880feb499eddb9e854c525770e95fb19373a2311
corrected_by: []
relates: [WK-677, WK-674]
---

# FD-1281 — 06 §4.2 shows three ApprovalPolicy keys the model refuses, and FR-385 is unbuilt

## Finding

**Severity: medium.** `06-governance.md` §4.2 gives the workspace's default `ApprovalPolicy`
as a JSON document. The document as printed is refused by the `ApprovalPolicy` model that
implements it, because the model is `extra="forbid"` and models none of three keys the
example carries: the per-entry `escalation`, the top-level `expedited` and the top-level
`separation_of_duties` object. FR-385, which `expedited` serves, has no code. This record does
not decide whether the spec or the model is wrong: that is `CLAUDE.md` §0's question.

## Evidence

At `origin/main` `880feb499eddb9e854c525770e95fb19373a2311`.

- `docs/specs/06-governance.md:305-335`, §4.2: entry 2 (`custom_objective`) carries
  `"escalation": {"when": …, "approvers_required": 2}` (line 314); the document ends with
  `"expedited": {"enabled": true, "approvers_required": 1, "requires_reason": true,
  "reported_in_exception_log": true}` (329) and `"separation_of_duties":
  {"submitter_may_approve": false, "configurable": false}` (331).
- `packages/model-schema/src/model_schema/approvals.py:111-160`: `ApprovalPolicyEntry` and
  `ApprovalPolicy` are both `ConfigDict(frozen=True, extra="forbid")`. `ApprovalPolicy` has
  `policies` and a flat `submitter_may_approve: bool = False`; entries have `artifact_type`,
  `approvers_required`, `approver_roles`, `environment`, `evidence`. No field is named
  `escalation`, `expedited` or `separation_of_duties`.
- Measured: the §4.2 block parsed out of the spec and given to `ApprovalPolicy.model_validate`
  (`uv run python`, this tree): the whole document is **REJECTED**, 3 `extra_forbidden`
  errors (`policies.1.escalation`, `expedited`, `separation_of_duties`); the
  same document without the top-level keys is REJECTED on `policies.1.escalation` alone; the
  `policies` list with the `escalation` key removed validates OK.
- `grep -rniE 'expedited' packages backend/src` (`.py`, `.ts`, `.vue`, excluding
  `generated`) prints nothing: FR-385 (`06-governance.md:181`) has no code, and
  `ApprovalRequest` (`approvals.py:275`) has no `expedited` field. The hand-authored
  `docs/contracts/schemas/approval-request.schema.json:20-24` does carry `expedited` and
  `expedited_reason` (line 102's invariant *"expedited == true requires expedited_reason"*);
  `backend/tests/test_contracts.py:83` lists `approval-request` in `ONE_SIDED_SLUGS` (`:69`) as
  *"later-phase — 06 governance"*, an authored-only slug with no generated side, so the drift
  guard does not compare that file against the model and nothing holds the two together.
- Not verified: whether `escalation.when` (an expression) is a wanted feature at all. It is in
  the spec example and nowhere else in the spec text I read.

## Interaction with OQ-1234

OQ-1234 option (b) (prepared on #935, `RL-[9901]`) puts the FR-429 promotion-skip permission on
the approval policy's `deployment` entry. It then adds a field to a model that already refuses
the document its own spec prints. Whoever builds (b) must decide, in the same change, whether
the model catches up with §4.2's three keys or the spec drops them. The prepared record says
so too (its lines on FR-385 and `extra="forbid"`), so this finding is the standalone home for
what that record only notes. It does not favour (a), (b) or (c) of OQ-1234.

## Disposition

**Carry forward, unowned**, proposed by the auditor on 2026-09-30; the register row's
`decision:` is the lead's. Spec versus code, for the decision-maker (`CLAUDE.md` §0). Event:
the OQ-1234 ruling, then the Work that builds FR-385 or amends §4.2. If unowned at the next
`CLAUDE.md` §14 review, the row decays to that review.

*Square brackets in `RL-[99nn]` are inserted so this record does not cite the prepared rulings' working ids as live ids under checks 31 and 32; the real ids carry none.*

*Disclosure: this record was drafted under working id 9911 and minted as FD-1281; the working id survives only in this line and in PR #947's history.*

## Amendment, 2026-09-30: owner confirmed WK-677 (FR-385)

Appended, not rewritten; nothing above changes. The maintainer's entry `to-lead.md`
"2026-09-30 11:56:33 BST — DECISIONS: slice order after the split; FR-384 confirmed; FR-383 and
FR-385 owners" makes **WK-677** (approval policies) the owner of FR-385, and the entry "2026-09-30
11:58:07 BST — FD-1281 disposition: yes, add a dated line" asks for this line. **The Disposition
above ("Carry forward, unowned") is superseded**: *unowned* is not a permitted state (`CLAUDE.md`
§14, the 2026-09-29 amendment, RFC-1248 and RL-1249). **Owner confirmed WK-677 (FR-385), maintainer
entry 2026-09-30 11:56:33 BST.** The register row carries the same line, with the earlier text
struck, not deleted. The event is unchanged: the OQ-1234 ruling, then the Work that builds FR-385
or amends §4.2.
