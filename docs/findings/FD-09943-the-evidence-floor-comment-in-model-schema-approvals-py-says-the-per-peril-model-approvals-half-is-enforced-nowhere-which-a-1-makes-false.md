---
id: FD-9943
family: finding
title: The EVIDENCE_FLOOR comment in model-schema approvals.py says the per-peril model approvals half is enforced nowhere, which A-1 makes false when it merges
status: draft
created: 2026-10-10
owner: auditor
tree: 2ef1393fec8eb0d974eb366f558a42e585771f35
corrected_by: []
relates: [WK-1178, PL-1461, SL-1462, RL-1457, FR-363, FR-364]
---

# FD-9943 — "enforced nowhere" in approvals.py goes stale when A-1 merges

**DRAFT**, filed on `draft/d6-fd9941-fd9943-process` (no PR), at the lead's entry in `to-lead.md`, "2026-10-10 05:19:53 BST — DISPATCH GOs at main 84ff9f0b: A-1 (PL-1461/SL-1462) GO NOW on gate-1; WK-673 S5 (PL-1500/SL-1389) GO to gate AFTER A-1 merges", last paragraph: *"A-1's stale DEFAULT_POLICY comment: an FD row in D6 is ACCEPTED (owner WK-1178), not fixed in A-1 unless it is a one-line comment inside A-1's write set, in which case fix it and state it in the LG."*

**Two corrections to the ruling's description, found while reading.** (1) The text is not on `DEFAULT_POLICY`; it is on `EVIDENCE_FLOOR`, about 177 lines above it. (2) It is **not stale at `main` `2ef1393f`**: it is true there. It becomes false when A-1 (`PL-1461`, `SL-1462`) merges. This FD records the second state, which is the one the ruling's "stale" anticipates.

## Finding

**The comment**, `packages/model-schema/src/model_schema/approvals.py:105-114` at `2ef1393f` (the `#:` block above `EVIDENCE_FLOOR`, `:115`; the sentence is at `:112-114`):

> The row's other half — **per-peril model approvals** — is enforced nowhere, and is FR-364's uncheckable remainder rather than something this floor's silence permits.

(The block's text, from `:105`: "**Corrected 2026-08-22 (WK-661, the audit-remediation slice).**" through "…rather than something this floor's silence permits.") The same sentence is repeated in the docstring of `packages/model-schema/tests/test_approvals.py:101-103`: "its **per-peril model approvals** half is enforced nowhere and is FR-364's uncheckable remainder."

**What enforces it, and when.**

- **At `main` `2ef1393f`: nothing.** `grep -rn -E 'per-peril|per_peril|approved.*component|APPROVED_COMPONENT' backend/src` finds no enforcement, and `backend/src/app/platform/perils.py` at that tree has no approval-time check on a structure's component models. The comment is accurate there.
- **On `origin/sl-1462-a1-peril-approval` @ `a93fb9048c2ff5f7eeb92536f9a8c16d407c3513`** (A-1, GO at "2026-10-10 05:19:53 BST", not merged: `git merge-base --is-ancestor` exits 1 against `origin/main`): `backend/src/app/platform/perils.py:708` `_require_approved_components`, called at `:556` inside `apply_approval_decision` (`:498`). Deciding `approve` on a Peril Structure whose `frequency_model`, `severity_model`, `burning_cost_model` or `separate_model` `excess_model` is not `approved` is refused `422 EVIDENCE_INCOMPLETE` naming each such ref, and the decision is rolled back (`:714`, `:742`). The accepted statuses are `APPROVED_COMPONENT_STATUSES` (`:70`). Tests: `backend/tests/test_peril_structure_approval.py:244`, `:276`, `:297`. This is `RL-1457` item 1, `06` `FR-363`.
- A-1 amends `docs/specs/06-governance.md` (one line, the §4.2 note: "per-peril approvals half is enforced at approval *(amended 2026-10-09, RL-1457 …)*") but touches **neither** `approvals.py` **nor** `test_approvals.py` (`git diff origin/main...origin/sl-1462-a1-peril-approval --stat` lists twelve files, neither among them).

**Related staleness, not in this FD's remedy.** `docs/specs/06-governance.md` `FR-364` (the row at `:145`) says of the same half: "sits in `peril_structures.perils` as JSONB and cannot be queried". That sentence stays true of the *floor* (the half is not an evidence kind a policy entry stores, which is why the floor stays empty and is A-1's own reasoning in the §4.2 note), but a reader of `FR-364` alone is told the half is unenforced. It is a spec edit, so it is named here and left to the owner's choice (`CLAUDE.md` §0: a spec change first).

## Evidence

Read at `2ef1393f` (this worktree) and at `a93fb904` (the A-1 branch tip); nothing was run.

1. `sed -n 100,125p packages/model-schema/src/model_schema/approvals.py` prints the block and `EVIDENCE_FLOOR` at `:115`; `grep -n 'enforced nowhere' -r packages backend/src` prints exactly `approvals.py:113` and `tests/test_approvals.py:103`.
2. `git show origin/sl-1462-a1-peril-approval:packages/model-schema/src/model_schema/approvals.py | grep -n 'enforced nowhere'` prints `113`: the branch leaves the sentence as it is.
3. `git show origin/sl-1462-a1-peril-approval:backend/src/app/platform/perils.py | grep -n -E '_require_approved_components|EVIDENCE_INCOMPLETE'` prints `329`, `516`, `556`, `708`, `714`, `742`.
4. `DEFAULT_POLICY` itself (`approvals.py:292-362`) is used, not unenforced: `backend/src/app/platform/approvals.py:46` imports it and `policy_for` returns it at `:170` for a workspace with no policy row; `environments.py:295` reads it. Its comments at `:316-349` make no "enforced nowhere" claim. So the ruling's phrase, read as being about the policy, does not describe the tree; read as being about this floor comment, it does.

## Disposition

**Proposed severity: LOW (the auditor proposes; the lead decides).** Reason: a comment, not behaviour; nothing is mispriced and no record's meaning depends on it. It is not zero because the platform's own rule is that a stale note must not contradict the code (the lead's entry of "2026-10-05 17:14:54 BST", item 6, for the same half), and this one is a governance claim in a published model-schema module.

**Decision (proposed): fix before close with an owner: WK-1178.** Remedy: correct the sentence in `approvals.py:112-114` and the matching docstring in `tests/test_approvals.py:101-103` to say the half is enforced at approval by `backend/src/app/platform/perils.py` `_require_approved_components` (`RL-1457`), and remains outside the floor because it is not an evidence kind a policy entry stores. The edit is a comment and a docstring, no behaviour. It goes in the next WK-1178 slice that touches `packages/model-schema/src/model_schema/approvals.py`; per the lead's entry, A-1 may carry it only if it is inside A-1's write set, and A-1's ledger must then say so. At `a93fb904` it is not in A-1's write set.

**Order condition:** the correction must not land before A-1 merges, because before then the sentence is true; a correction written now would be the stale note.

**Event that next confirms or discharges it:** A-1's merge (the sentence becomes false), then the first WK-1178 slice that edits `approvals.py` (the correction).
