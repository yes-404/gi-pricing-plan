---
id: PL-9589
family: plan
kind: leaf
title: WK-673 Slice 6 — the approval gate, part two, the floor wiring: leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05
owner: planner
tree: 137bc817ef1fb40ea57e9053e0ad40b73bdff3a8
phase: P2
work: WK-673
slice: SL-1390
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-1390, PL-1267, PL-1371, RL-881, RL-1184, RL-1263, SL-1389]
---

# PL 9589 (working id) — WK-673 Slice 6: the approval gate, part two — the floor wiring: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor is spawned from `.claude/roles/executor.md` and also
> binds `test-driven-development` (every task is red first), `python-test` (requirement
> markers, negative tests), `spec-change` (Task 1), `dev-commands` (the two-half gate) and
> `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before the first
> step.

Filed under working id **9589**, reserved by the lead and named in the lead's brief
`~/gi-pricing-plan.local/handover/brief-prep-wave-2026-10-05.md`, section AQ (written for
planner-673s46). Drafted from 17:05:48 BST (`TZ=Europe/London date`) on 2026-10-05 against
origin/main `137bc817ef1fb40ea57e9053e0ad40b73bdff3a8`. Every locator below was read at that
tree unless another tree or a branch head is named. Unminted records are cited by working id
and kept out of `relates:` (check 32): PL 9590 (WK-673 Slice 5, draft #1181, head
`7db4d646`), PL 9591 (Slice 4, #1176, head `ac8221ec`), PL 9649 (the FR-240 family fix,
WK-673, #1152), PL 9688 (the FD 9707 fix, WK-673, #1145), PL 9683 (the FD 9708 fix, #1140),
PL 9629 (the exit-demo plan, #1164, head `68dd997c`), RL 9607 (PL 9616's ruling), RL 9614
(#1167), RL 9620 (the RL-1263 amendment, #1162).

## Goal

`submit_for_review` (`backend/src/app/platform/rating_versions.py:278`) checks
`policy.effective_evidence("rating_version")` against a `verifiable` map —
`structural_diff` (Slice 5), `regression_run` (WK-672 Slice 3's `_regression_run_gate`,
`:648`), `dislocation_run` (Slice 5) — replacing the direct limb checks, limb (1)'s
`_regression_run_gate` call at `:317` included, in the pattern of `modelling.py:1230-1261`.
A workspace policy naming a kind nothing can verify is refused by name, never passed
(`06` FR-364). This closes `RL-881`'s finding that `EVIDENCE_FLOOR["rating_version"]`
names kinds no submission path consults (`PL-1267` premise e), and discharges FR-364's
2026-08-29 invariant ("Wiring the rating-version check is WK-673's, the last of the two
enablers", `06:145`).

**Architecture.** One loop over `effective_evidence("rating_version")` in floor-then-policy
order. Each verifiable kind maps to an async verifier that either returns the evidence value
written to `row.evidence` or raises the kind's own `EVIDENCE_INCOMPLETE` (Slice 5's and
WK-672's existing refusal texts, unchanged). A kind with no verifier is refused with
`EVIDENCE_INCOMPLETE` naming it, as `modelling.py:1249-1260` does. The golden-quote gate
(FR-260, `:314`) and FR-224's `approximation` gate (Slice 5) are not floor kinds and stay
direct checks.

**Tech stack.** Python 3.12, SQLAlchemy 2 async. No new dependency, no shape change.

**Spec.** [`06-governance.md`](../specs/06-governance.md) FR-363 (`:109`), FR-364 (`:145`,
with its 2026-08-29 and 2026-09-28 amendments), FR-352 (`:93`), §4.2 (`:344-…`, the
`rating_version` entry at `:360-362`); [`03-rating-engine.md`](../specs/03-rating-engine.md)
FR-257 (`:174`), FR-260 (`:177`).

## Status

`draft`. **One decision point is open** (DP-S6-1), the decision-maker's and blocking. The
plan moves to `active` only through a separate activation PR.

### Activation needs, in order

1. **This plan is merged, minted and made `active` by a dated line.**
2. **`SL-1389` (Slice 5) is closed**, and so transitively `SL-1388` and `SL-1256`. This slice
   consumes Slice 5's `structural_diff_verified`, `dislocation_run_verified` and its direct
   gates (PL 9590 Tasks 2–3). Where Slice 5's merged code differs from this plan, the merged
   code governs and the dispatch record names each difference.
3. **A ruling on DP-S6-1** is merged and minted, adopting or amending P1.
4. **The lane is free under `RL-1263`** as RL 9620 amends it, with the same-Work conditions in
   the dispatch record.
5. **The maintainer's dispatch GO**, and the lead's go in a separate activation PR.

## Acceptance Standard

Each item is a named test or command a fresh reviewer can re-run, in the executor's own
worktree, against `origin/main...HEAD`. Every test is shown red before its code exists, and
the ledger quotes the red by its cause (README convention 2). `F` is the new
`backend/tests/test_rating_version_evidence_floor.py`.

1. **At the floor, each kind missing in turn is refused.** `F::test_a_policy_at_the_floor_refuses_each_missing_kind`
   (parametrised over `structural_diff`, `regression_run`, `dislocation_run`): 422
   `EVIDENCE_INCOMPLETE` whose `detail` is the kind's own refusal text (Slice 5's or
   `_regression_run_gate`'s, quoted in the ledger). `@pytest.mark.req("FR-364")`.
2. **The floor holds against a policy that omits it.** `F::test_a_stored_policy_below_the_floor_is_still_held_to_it`:
   a policy whose `rating_version` entry lists only `regression_run` (stored directly, as a
   pre-FR-364 policy would be; `set_policy` refuses it, so the test writes the row) still
   refuses a submission with no Dislocation Run.
3. **A policy above the floor adds its kinds.** `F::test_a_policy_above_the_floor_adds_a_verifiable_kind`
   per DP-S6-1's ruled map (for example `change_summary` under DP-S6-1 (a) or (c)).
4. **An unverifiable kind is refused by name, never passed.** `F::test_a_policy_naming_an_unverifiable_kind_is_refused_by_name`:
   an entry adding `"telepathy_check"` refuses with `EVIDENCE_INCOMPLETE` whose `detail`
   names `telepathy_check` and says this build cannot verify it. Shown red on a deliberately
   broken loop that skips unknown kinds (scratch-reverted).
5. **The direct calls are gone.** `git grep -n "_regression_run_gate(\|_dislocation_gate(\|_structural_diff_gate(" -- backend/src/app/platform/rating_versions.py`
   prints each function's definition and its one entry in the `verifiable` map, and no other
   call inside `submit_for_review`.
6. **Behaviour at the default policy is unchanged.** `uv run pytest
   backend/tests/test_rating_versions.py backend/tests/test_rating_version_dislocation_gate.py
   backend/tests/test_regression_runs.py -q` passes with no test file edited
   (`git diff origin/main...HEAD -- <those three files>` empty).
7. **The evidence written is unchanged.** `F::test_evidence_keys_match_the_direct_checks`:
   after a successful submit, `row.evidence` holds the same keys and values the Slice 5 build
   wrote (`regression_suite_run_id`, `dislocation_run_id`, `structural_diff_blob`,
   `golden_quotes`, and `approximation_check` when applicable).
8. **The two-half gate** passes on the slice head, and the four docs checks with their rc and
   summary lines quoted; `req-coverage.py` lists `06` FR-364 with a test in `F`.
9. **The slice closes on the maintainer's MERGE-ACK and a clean audit** (`PL-1267`
   Acceptance 8). The auditor's close of WK-673 then reads `RL-881`'s premise e as
   discharged; `PL-1267` premise e′'s stale clause in `RL-881` stays the decision-maker's.

## Global Constraints

- **Fail closed** (`06` FR-364: "Submission continues to fail closed on any evidence kind it
  cannot verify (R4)"). No kind is ever skipped because it is unknown.
- **The floor is the union** (`ApprovalPolicy.effective_evidence`,
  `model_schema/approvals.py:205-220`): the loop reads that method, never `entry.evidence`
  alone.
- **No refusal text changes.** Each verifier keeps the `detail` its direct check had, so
  existing tests and Slice 5's refusals read the same.
- **No new permission, no shape change** (`PL-1267` Global Constraints).

## Scope

### Requirement coverage, each id individually

| Id | Where | What this slice builds | Task |
|---|---|---|---|
| FR-364 (`06`) | `06:145` | the floor-and-policy union enforced for `rating_version`; fail closed on an unverifiable kind | 2 |
| FR-363 (`06`) | `06:109` | required evidence enforced at submission, per artifact type, for `rating_version` | 2 |
| FR-257 (`03`) limbs (1) and (2) | `03:174` | routed through the floor rather than called directly (no new limb) | 2 |

**Not in scope:** any new evidence kind's verifier beyond DP-S6-1's ruling; FR-224 (Slice 5,
stays direct); FR-260's golden quotes (stay direct).

### Premises read at `137bc817`

| # | Premise | At `137bc817` | Status |
|---|---|---|---|
| a | The floor | `EVIDENCE_FLOOR["rating_version"] = ("structural_diff", "regression_run", "dislocation_run")` (`model_schema/approvals.py:120`) | reproduces |
| b | The shipped default entry | `DEFAULT_POLICY`'s `rating_version` entry (`approvals.py:344-349`): the same three kinds | reproduces |
| c | **The documented default entry is wider** | `06` §4.2's `rating_version` entry (`06:360-362`): `structural_diff`, `rate_table_diffs`, `regression_run`, `dislocation_run`, `gipp_check_if_enabled`, `change_summary`; the code's comment calls `DEFAULT_POLICY` "the defaults `06` §4.2 documents" (`approvals.py:291`) | **spec and code disagree**; DP-S6-1 |
| d | No `rating_version` caller | `effective_evidence(` has callers in `modelling.py:1246`, `objectives.py:1027`, `metrics.py:797`, none for `rating_version` | reproduces |
| e | The pattern | `modelling.py:1230-1261`: `verifiable` dict, `missing`, `unknown`, one `PlatformError("EVIDENCE_INCOMPLETE", …)` naming every missing kind and the unverifiable ones | reproduces; this slice keeps per-kind texts (§"Architecture") |
| f | The change summary is already enforced | `approvals.submit`'s blank-change-summary guard (FR-352), named in the submit route's comment (`backend/src/app/api/models.py:1189-1193`) and tested by `test_a_blank_change_summary_cannot_submit_a_rating_version` (`backend/tests/test_rating_versions.py:350`); it runs after the evidence checks | reproduces; DP-S6-1 |
| g | GIPP cannot be enabled yet | `04` FR-294 is WK-685, Phase 4 (PL 9629 step D9: "the demo runs with GIPP not enabled") | reproduces; DP-S6-1 |
| h | The precedent for a workspace copying a kind "off the page" | `approvals.py`'s comment on the `model` entry: "a workspace copying the kind off the page got a fail-closed refusal for evidence it had" | reproduces; why DP-S6-1 matters |

### Risks

- **A workspace that copied `06` §4.2's `rating_version` entry** is refused on every
  submission for three kinds, unless DP-S6-1 maps them. This is the premise-h failure,
  recurring. Task 0 Step 3 counts the stored policies that name each kind.
- **Refusal order changes.** The loop runs floor order (`structural_diff` first); Slice 5's
  direct order ran regression first. A test that submits with several kinds missing and
  asserts the first refusal would change; Acceptance 6 forbids editing such a test, so the
  executor stops and reports one if found.

## Write set, and its contention (`RL-1263`, RL 9620)

Classes as in PL 9591 §"Write set".

| Path | Symbol or region | Change | Other slice | Class |
|---|---|---|---|---|
| `backend/src/app/platform/rating_versions.py` | `submit_for_review` (`:278-338` at `137bc817`, as Slice 5 leaves it); the verifier wrappers | edited | **SL-1389** (Slice 5, WK-673): the same function | **SERIAL** (plan dependency: consumes Slice 5's output) |
| the same file | — | — | **PL 9649** (WK-673): `_Resolver` (moved by Slice 4); **PL 9683**: `create_rating_version` (`:230-275`); **PL 9610**: `_Resolver` | **ALLOWED one-sided** (different functions), the dispatch record naming the `git diff -U0` check; for PL 9649 (same Work) RL 9620 (b) holds both ways (neither consumes the other's output) |
| `docs/specs/06-governance.md` | FR-364 row (`:145`), a dated note at its end (P1) | the ruled text | **RL 9607** (`06` `:67`, `:483`, `:640`); **RL 9614** T3 (`06` §5.1 `:558`) | none (other sections) |
| `backend/tests/test_rating_version_evidence_floor.py` | new | Acceptance 1–4, 7 | none | none |
| `docs/ledgers/LG-<n>-…md`; `docs/INDEX.md` | added; regenerated | | | exempt |

**Not written:** `packages/` (no shape change; `EVIDENCE_FLOOR` and `DEFAULT_POLICY` stay as
they are unless DP-S6-1 (b) is ruled); `errors.py`; any route.

**Same-Work pairs, RL 9620 condition 2, both ways.** With **SL-1389**: consumes its output →
serial. With **PL 9649** and **PL 9688**: (a) no shared existing definition (PL 9688 writes
`03` §3.2 and `pricing-core` files only), and (b) no plan dependency either way; they may run
at once if the dispatch record names both.

### Size

About half an executor day: one loop, three wrappers, one test module.

## Needs this slice serves (PL 9629 #1164, its step table)

| Need | Step | What this slice provides |
|---|---|---|
| G2, PL 9629 activation need 6 | E3 the first submission is refused: the dislocation run is stale → 422 `EVIDENCE_INCOMPLETE` | the refusal now reached through the floor |
| G2, need 6 | E9 `approved`, evidence pinned, audit events; the evidence ids on the decision | Acceptance 7 (the same evidence keys) |
| G1 | WK-673 resolved: `RL-881`'s premise discharged; FR-364's last enabler wired | this slice |

PL 9629's demo seeds its own policy or uses `DEFAULT_POLICY`; under DP-S6-1 (b) a demo
policy copied from `06` §4.2 would refuse E2. Task 0 Step 3 checks what the demo seed stores.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S6-1 | **What does the loop do with `rate_table_diffs`, `gipp_check_if_enabled` and `change_summary`**, which `06` §4.2's documented `rating_version` default names and the shipped `DEFAULT_POLICY` does not (premise c)? | (a) **Map all three**: `change_summary` → verified when the summary is non-blank, the same test `approvals.submit` applies later (premise f; FR-352); `gipp_check_if_enabled` → verified while no workspace can enable GIPP (premise g), with a dated note that the slice building `04` FR-294 replaces the verifier; `rate_table_diffs` → verified when the persisted structural diff (Slice 5) exists and the pin difference between baseline and candidate is recorded with it. (b) **Fail closed on all three** (FR-364's literal rule) and file the §4.2-versus-`DEFAULT_POLICY` disagreement as a finding; a workspace copying §4.2 is refused until it is resolved. (c) **Map `change_summary` and `gipp_check_if_enabled` as in (a); fail closed on `rate_table_diffs`** with a named owner (the slice that persists rate-table diffs as evidence) | **(c).** `change_summary` is already enforced and GIPP cannot be on, so refusing either would refuse evidence the version has (premise h, the same mistake the `model` entry's comment records). `rate_table_diffs` has no artifact: the structural diff covers re-pointed steps, not pin version changes (`rate_table:…@5→@6`, `06:469`), and verifying it from a blob that does not hold it would be asserting, not checking. (c) keeps FR-364's fail-closed rule where it bites and names the owner. Under (a) Slice 5's blob would need the pin diff added, a Slice 5 scope change | decision point | yes — Task 2 | open |

**Decided here (slice design, the planner's):** the verifiers raise their own refusal texts
rather than collecting every missing kind into one message as `modelling.py:1247-1261` does.
The texts are Slice 5's and WK-672 Slice 3's, and existing tests pin them (Acceptance 6). The
unknown-kind refusal follows `modelling.py`'s wording.

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm each activation need at the dispatch tree
  (`git -C <worktree> log -1 --format='%H %aI' origin/main`; `SL-1389` `closed`; the ruling
  resolves by minted id; this plan `active`).
- [ ] **Step 2:** `uv sync --all-packages`.
- [ ] **Step 3:** Record: the contention re-check (as PL 9591 Task 0 Step 3); every stored
  `approval_policies` row in the dev seed and the demo seed (`examples/fremtpl2/seed.py`)
  naming a `rating_version` kind outside the floor (`git grep -n "rate_table_diffs\|gipp_check_if_enabled\|change_summary" -- examples backend/src`).
- [ ] **Step 4:** Copy Slice 5's merged `submit_for_review` (with line numbers) and its gate
  functions' signatures into the ledger.
- [ ] **Step 5:** Baseline Acceptance 6's three test files and the four docs checks; record rc
  and the summary lines.

### Task 1: Spec — the ruled text

**Files:** `docs/specs/06-governance.md` (FR-364 `:145`).

- [ ] **Step 1:** Apply P1 as the ruling adopts it, verbatim from the ledger copy;
  `grep -cF` its anchor (1).
- [ ] **Step 2:** `python3 scripts/audit-docs.py` (only check 31 may fail while ids are
  working ids).
- [ ] **Step 3: Commit** `docs(specs): 06 FR-364 — the rating_version floor is wired (SL-1390)`.

### Task 2: The floor loop

**Files:**
- Modify: `backend/src/app/platform/rating_versions.py` (`submit_for_review`)
- Test: `backend/tests/test_rating_version_evidence_floor.py` (new)

**Interfaces:**
- Consumes: Slice 5's `_structural_diff_gate`, `_dislocation_gate` (and its baseline helper),
  WK-672's `_regression_run_gate` (`:648`); `approvals.policy_for` (`platform/approvals.py:166`);
  `ApprovalPolicy.effective_evidence` (`model_schema/approvals.py:205`).
- Produces: inside `submit_for_review`, `verifiers: dict[str, Callable[[], Awaitable[tuple[str, Any]]]]`
  — each returns the `row.evidence` key and value it writes — and the loop:

```python
policy = await approvals.policy_for(session, workspace_id=workspace_id)
evidence: dict[str, Any] = {}
for kind in policy.effective_evidence("rating_version"):
    verify = verifiers.get(kind)
    if verify is None:
        raise _evidence_incomplete(
            ref,
            f"the approval policy requires {kind!r}, which this build cannot verify; "
            "treating an uncheckable requirement as met would make a policy tightening do nothing",
        )
    key, value = await verify()
    if key:
        evidence[key] = value
```

`policy_for` is `async def policy_for(session: AsyncSession, workspace_id: UUID) -> ApprovalPolicy`
(`platform/approvals.py:166`); `modelling.py:1230` calls it positionally. Mirror that call.

- [ ] **Step 1: Write the failing tests** — Acceptance 1–4 and 7.
- [ ] **Step 2:** Run them. Expected: Acceptance 2 and 4 FAIL because the submission
  **succeeds** (the direct checks ignore the policy); Acceptance 1 and 7 PASS already (the
  direct checks refuse the same kinds) — record that they pass on the old code, since they
  guard behaviour this task must keep, not behaviour it adds. Acceptance 3 fails per DP-S6-1's
  ruled kind.
- [ ] **Step 3:** Replace the direct calls (`_regression_run_gate` at `:317` and Slice 5's
  calls) with the loop; keep the golden-quote gate before it and FR-224's gate after it.
- [ ] **Step 4:** Run Acceptance 1–7 (PASS). For Acceptance 4, break the loop to `continue`
  on an unknown kind; the test must fail naming the accepted submission; revert; quote both.
- [ ] **Step 5:** Acceptance 5's `git grep`.
- [ ] **Step 6: Commit** `feat(rating): submission checks the rating_version evidence floor (06 FR-364)`.

### Task 3: The gate and the ledger

- [ ] **Step 1:** The full two-half gate (`dev-commands`); the four docs checks;
  `req-coverage.py`. Quote every rc and summary line with the tree.
- [ ] **Step 2:** The ledger: Task 0's records, every red quoted by its cause, Acceptance 1–9
  with evidence, and `RL-881` premise e recorded as discharged for the auditor.

## Hand-off

The executor works in its own worktree on a branch from origin/main after `SL-1389` merges.
The slice closes on a clean audit and the lead's merge. It is WK-673's last build slice in
`PL-1267`'s order; the Work then closes by `close-workstream`, accepted by the maintainer
(`PL-1267` Acceptance 10).

## Appendix — proposed text (for the ruling to adopt, amend or reject)

### P1 — `06` FR-364 (`:145`), appended at the row's end (DP-S6-1 (c))

```markdown
**Amended <date> (WK-673 Slice 6, RL-<n>): the `rating_version` floor is wired.** Submission of a Rating Version checks the union of the floor and the matching policy entry, in that order, and fails closed on any kind it cannot verify, naming it. `change_summary` is verified when the submitted summary is non-blank, the test FR-352's guard in `approvals.submit` applies; `gipp_check_if_enabled` is verified while no workspace can enable the GIPP check (`04` FR-294, Phase 4), and the slice that builds FR-294 replaces that verifier. `rate_table_diffs` has no persisted artifact and is refused when a policy names it; owner: the slice that persists rate-table diffs as approval evidence.
```

`<date>` is the code commit's date and `RL-<n>` the ruling's minted id.

## Self-review

1. **Spec coverage.** `06` FR-364 and FR-363 for `rating_version` → Task 2. The floor at, above
   and below the policy, and each kind missing in turn (`PL-1267` Slice 6's three tests) →
   Acceptance 1–4. FR-257 limbs (1) and (2) re-routed → Acceptance 5–6.
2. **Placeholder scan.** `<date>`, `RL-<n>`, `LG-<n>` are fixed at the code commit, the mint
   and the ledger. Acceptance 3's kind is DP-S6-1's outcome.
3. **Type consistency.** `verifiers`, `structural_diff_verified`, `dislocation_run_verified`
   and the gate names match PL 9590's Interfaces (grepped against #1181 at `7db4d646`).
4. **Rulings between sweep and filing.** Open PRs read at 17:05 BST: none rules on FR-364 or on
   `06` §4.2's `rating_version` entry; RL 9607's `06` texts and RL 9614's T3 are in other
   sections.
5. **Spec and code disagree (premise c), and this plan does not pick a side silently.**
   DP-S6-1 puts it to the decision-maker (`CLAUDE.md` §0).
