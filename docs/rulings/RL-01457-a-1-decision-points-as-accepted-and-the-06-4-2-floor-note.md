---
id: RL-1457
family: ruling
title: WK-1178 Option A, A-1 (PL-1461) decision points as accepted — per-peril model approvals enforced at approval, an earlier approved Peril Structure version superseded, a named interim refusal until A-3; and the 06 §4.2 floor note amended
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-06              # the mint date (check 31); ruled 2026-10-05
owner: decision-maker
tree: 4d3be1414ad4dacdaa0c14ef49fb21853adbaed6
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-20, FR-191, FR-255, FR-363, FR-364]
---

# RL-1457 — A-1's decision points, as accepted, and the 06 §4.2 floor note

## How this was ruled

- **Filed under working id 9563 (minted as RL-1457), reserved by the lead (team-lead) on 2026-10-05.** At the
  mint, on 2026-10-06 in the G2 chain batch, the working ids named here (PL 9599, SL 9600, PL 9595,
  FD 9995) were replaced by their minted ids (PL-1461, SL-1462, PL-1465, FD-1456). `<date>` and `<RL>` in T1 are filled by the
  slice that applies it.
- **The decisions are not this record's.** They are the maintainer's (by delegation), in
  three entries in `channel/to-lead.md`, each quoted verbatim below. This record writes them
  down, because a plan cannot cite a message (RFC-777) and A-1's Task 5 waits on a worded
  text.
  - From "2026-10-05 17:02:50 BST — A-1/A-2 plans and batch 5 noted; the model_call ROUNDING
    is fixed IN A-2 by declared result type, not worked around in A-3":

```text
A-1 (#1177 PL 9599): its DPs at the plan's recommendations, DP-1 (a) FR-363 per-peril approvals enforced at approval, DP-2 (a) supersede the earlier approved version, DP-3 (b) a named interim refusal until A-3: ACCEPTED (no DM needed; each is a choice inside settled scope).
```

  - From "2026-10-05 17:08:35 BST — A-3 / A-4 DP memo (handover/dp-memo-a3-a4-2026-10-05.md)
    RULED; the reconciliation TOLERANCE set":

```text
A-1 BUG (to planner-a12fold): `_require_approved_components` lists "approved, live or retired", but `live` and `retired` are not ModelStatus values (copied from compile's cross-type _APPROVED_OR_BETTER). Fix: use ModelStatus's own approved set, with a red test (a model in a non-existent status string never passes). Good catch.
```

  - From "2026-10-05 17:14:54 BST — FD 9572 placement accepted; WK-673 S4/S5/S6, A-1, A-2 and
    CR-838 DECISIONS (1–8)":

```text
6. A-1 DP-1's 06 §4.2 note: YES, worded text. A DM drafts the dated amendment to 06:407 ("the per-peril approvals half is unqueryable" becomes the enforced rule A-1 builds), adopted in A-1's ruling. Task 5 is not left empty, and a stale note must not contradict the code.
```

- **The plan the decisions read** is PL-1461 (#1177, branch `pl-9599-a1-peril-approval` @
  `e8bd0ff67e6b250d85504249e07088b83d830526`): its §"Decision points" DP-1 to DP-3, its
  Acceptance item 13, and its Task 5. Task 5 reads: "If the ruling carries a dated amendment
  to `06` §4.2's note (`:405-408`), apply it verbatim under `spec-change` …".

## Locators — read at `4d3be141` (origin/main at filing) unless a PR head is named

| What | Where | Says |
|---|---|---|
| The note to amend | `docs/specs/06-governance.md` §4.2, the floor note, line 407 | "`peril_structure` has an **empty** floor — not for want of a §3.3 row, which it has had since 2026-08-14, but because its reconciliation half is enforced structurally and its per-peril approvals half is unqueryable." |
| The evidence it describes | same file, FR-363's table, the **Peril Structure** row (line 118) | "Per-peril model approvals; reconciliation result within tolerance (`02` FR-190)" |
| The floor rule | same file, FR-364 | "The table above is a floor. §4.2's `ApprovalPolicy` may add to it and may never remove from it." |
| What A-1 builds | PL-1461 @`e8bd0ff6`, DP-1 (a), Acceptance 5 and 13 | approving refuses `422 EVIDENCE_INCOMPLETE` naming each component model that is not `ModelStatus.APPROVED` (`superseded` included); "the structure and the request stay `review`" and the decision rolls back |
| The model statuses | `packages/model-schema/src/model_schema/modelling.py`, `ModelStatus` | `draft`, `fitted`, `review`, `approved`, `superseded`, `archived` |
| A Model's supersession, which DP-2 mirrors | `backend/src/app/platform/modelling.py`, `_supersede_earlier_versions` | "`approved → superseded` for every earlier approved version of the family" |
| The interim failure DP-3 replaces | `packages/pricing-core/src/pricing_core/rating/runtime.py`, `_model_call_handler` | `fit_result = dict(payload["fit_result"])`, which a structure payload does not carry |

## Ruled

1. **DP-1 (a), as corrected at 17:08:35.** Approving a Peril Structure enforces `06` FR-363's
   "Per-peril model approvals" at the approval carry. `decide` with `approve` refuses with
   `422 EVIDENCE_INCOMPLETE`, naming each component model ref (`frequency_model`,
   `severity_model`, `burning_cost_model`, and a `separate_model` treatment's `excess_model`)
   whose model is not `ModelStatus.APPROVED`. The decision rolls back, and the structure and
   the request stay `review`. The accepted set is `ModelStatus`'s own (`approved` only). It is
   not compile's cross-type `_APPROVED_OR_BETTER`, whose `live` and `retired` are not model
   statuses (the 17:08:35 "A-1 BUG" paragraph; PL-1461 Acceptance 13).
2. **DP-2 (a).** Approving a Peril Structure version supersedes every earlier `approved`
   version of the same structure, as `_supersede_earlier_versions` does for a Model.
3. **DP-3 (b).** Until A-3 merges, a `model_call` on a Peril Structure fails as a typed,
   named `_model_call_failure` (FR-255). The failure names the ref and that scoring a Peril
   Structure is slice A-3. The bare `KeyError` on `payload["fit_result"]` does not reach the
   caller.
4. **The `06` §4.2 floor note is amended (T1).** The 17:14:54 item 6 says: "the per-peril
   approvals half is unqueryable" becomes the enforced rule A-1 builds. **The floor stays
   empty.** Neither half is a stored evidence kind a policy entry could name; one is enforced
   at reconciliation and submission, the other at approval. FR-364 therefore needs no change.

## The spec text

T1's find string occurs **exactly once** at `4d3be141` (`grep -c -F`). T1 is applied by
**A-1 (SL-1462 / PL-1461, WK-1178), in its Task 5**, in one commit with the code it
describes (`CLAUDE.md` §2). It is not applied in this commit.

**T1 — `06-governance.md` §4.2, the floor note (line 407).** Find:

```text
> per-peril approvals half is unqueryable. Submission checks the union of the floor and the entry,
```

Replace with:

```text
> per-peril approvals half is enforced at approval *(amended <date>, <RL>: it read "is unqueryable" until A-1 built the approval carry; deciding `approve` on a Peril Structure now refuses `422 EVIDENCE_INCOMPLETE`, naming each component model — `frequency_model`, `severity_model`, `burning_cost_model`, or a `separate_model` treatment's `excess_model` — whose status is not `approved`, and rolls the decision back. Neither half is an evidence kind a policy entry stores, so the floor stays empty)*. Submission checks the union of the floor and the entry,
```

## What it obliges

- **This commit:** this record and the regenerated `docs/INDEX.md`. No `06` text, no plan,
  and no code is edited here.
- **A-1 (SL-1462 / PL-1461)** cites this record. Its Task 5 applies T1 verbatim, so the task
  is no longer empty, and `06` stops calling enforced behaviour "unqueryable" once A-1's
  code merges. PL-1461's pre-mint note in Task 5 ("this task is empty …") is replaced, before
  its first merge, by a pointer to this record.

## Acceptance — the violation that must become detectable

The violation: **a Peril Structure approved over a component model that is not `approved`, or
a `06` text that contradicts what the approval does.**

- PL-1461 Acceptance 5 and 13: a structure whose component model has any `ModelStatus` other
  than `APPROVED` is refused `422 EVIDENCE_INCOMPLETE` at approval, naming the ref. The
  decision rolls back. The all-approved control is approved.
- After A-1 merges, `git grep -n 'per-peril approvals half is unqueryable' -- docs/specs`
  prints nothing.

Drafted as working id 9563; minted as RL-1457 on 2026-10-06.
