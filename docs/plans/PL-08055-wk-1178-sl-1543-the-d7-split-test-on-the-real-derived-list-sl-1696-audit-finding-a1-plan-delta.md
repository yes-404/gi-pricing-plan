---
id: PL-8055
family: plan
kind: map
title: WK-1178 — SL-1543 owns SL-1696's audit finding A1, the D7 split test on the real derived list (PL-1694 Acceptance 18), red first by cause against SL-1696's hand-written list — a dated Work-plan delta to PL-1542 and PL-1705
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-16
owner: planner
tree: 0877e6e7a756c4621890713a4d3b016e75e33654
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1542, PL-1705, PL-1694, SL-1543, SL-1696]
---

# PL 8055 — WK-1178, SL-1543 owns A1: the D7 split test on the real derived list (delta to PL-1542 and PL-1705)

> **For agentic workers:** this is a **dated delta** under Lean P2 L5 (`document-ids.md` §1.6,
> PL row: *"a change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's
> plan"*), in the form of
> [`PL-1705`](PL-01705-wk-1178-sl-1543-the-severity-response-claim-severity-the-refusal-red-and-sl-1702-before-sl-1543-plan-delta.md).
> It does not replace
> [`PL-1542`](PL-01542-wk-1178-a-4-the-exit-demo-walks-wf-699-s-peril-structure-path-leaf-plan.md)
> or `PL-1705`; their bodies are frozen and are not edited. It adds no slice row. It adds **one
> task and one acceptance item** to `SL-1543`. **Read `PL-1542`, then `PL-1705`, then
> [`PL-1694`](PL-01694-wk-673-fd-1660-the-guard-then-the-fix-attribution-carries-sub-graph-mounts-plan-delta.md)
> Acceptance 18 and its Stage B Task 4, then this file. Where they differ, this file is the
> latest statement for the task it adds.** The executor of `SL-1543` binds what `PL-1542`'s
> header names (`python-test`, `test-driven-development`, `python-package`, `dev-commands`,
> `git-hygiene`), and is spawned from `.claude/roles/executor.md`.

Filed under **working id 8055**, reserved by the lead in `~/gi-pricing-plan.local/handover/eta.md`
at "2026-10-16 09:37:02 BST". Written 2026-10-16 from 09:40 BST (`TZ=Europe/London date`) by the
planner (seat planner-a1), on the lead's brief of the same morning. **Trees read:** `origin/main`
`0877e6e7a756c4621890713a4d3b016e75e33654` (#1307) for the plans; `SL-1696`'s head on #1310,
`d85e3d724f49c4e353bd9d066a3871b841f64aa9` (tree `4fc1bbc8`), for `examples/fremtpl2/journey.py`,
`backend/tests/test_wf699_journey.py` and the ledger `LG-1732`. **No test or code was run at
planning time**; every claim below about behaviour is a reading of the code at `d85e3d72`.

*(Amended 2026-10-16 from 09:52 BST, before merge, by the planner (seat planner-8055b), on the lead's
brief: **DP-A1-1 is ruled (a) by RL 8060** (`origin/rl-8060-pl8055-dp-a1-1-2026-10-16`
@`5b07a5b6`), confirmed by the maintainer in the entry "2026-10-16 09:51:34 BST — Maintainer: RL 8060 (PL 8055 DP-A1-1 → (a)) CONFIRMED" in `~/gi-pricing-plan.local/channel/to-lead.md`.
The ruling's two precisions and the confirmation's four conditions are carried into the DP row,
Status, N2, N4, Steps 2 to 5, Acceptance item 1 (v), Hand-off 3 and Self-review 2. Each edited
place names RL 8060. RL 8060 is a working id, so it is not in `relates:` until it is minted.)*

*(Amended 2026-10-16 from 10:18 BST, before merge, by the planner (seat planner-8055b), on the
maintainer's ruling "2026-10-16 10:17:07 BST — Maintainer: DP-1543-APPROVERS → (a): the policy
governs; PL-1542:444's "two principals" is the plan's error, corrected by a dated line in PL 8055"
in `~/gi-pricing-plan.local/channel/to-lead.md`, items 1 and 2. **`PL-1542` Task 2 Step 2**
(`:444` at `origin/main` `0877e6e7`), *"`approval_service.decide` with two principals who are
neither submitter nor author"*, **is superseded: the Peril Structure is decided by ONE
approver**, per `docs/specs/06-governance.md:358` (`{"artifact_type": "peril_structure",
"approvers_required": 1, …}`) and `DEFAULT_POLICY` (`packages/model-schema/src/model_schema/approvals.py:376`,
its `peril_structure` entry `:422-427`, `approvers_required=1`), both read at `0877e6e7`.
Neither the spec nor the code supports two. **The one approver is distinct from both the
submitter and the author**; that separation is the control 06 requires. **The test asserts
both differences** (the approver's id differs from the submitter's and from the author's)
**and that the structure reaches `approved` after exactly one `decide`.** `PL-1542`'s body is
frozen and is not edited; this line is the correction, and the Tasks section below points at
it.)*

## Goal

Put `SL-1696`'s audit finding A1 into plan text as `SL-1543`'s owned work. A1 is the one clause
of `PL-1694` Acceptance 18 that `SL-1696` did not meet in its committed form: *"the D7 split test
built on the **real** derived list (ids, kinds, descriptions copied from a run of the fixed
code …)"* (`PL-1694` `:395-404`). This delta gives `SL-1543` the task that meets it, with a red
that fails **by cause** on `SL-1696`'s hand-written list.

## The entries this delta records

1. **The owner — the lead, from-lead "2026-10-14 20:25:11 BST"** (`channel/from-lead-2026-10-09.md`):
   *"LEAD VERDICT on A1 (LOW; PL-1694 Acceptance 18 — the D7 split test on the REAL derived list;
   reverted under ACK cond. 4): DEFERRED WITH OWNER = SL-1543 (WK-673; serialised on
   examples/fremtpl2/journey.py + backend/tests/test_wf699_journey.py after SL-1696; lands through
   its own gate); the behaviour is evidenced by the demo D7 decomposition."*
2. **The vehicle — the lead, from-lead "2026-10-16 09:36:30 BST"**, `SL-1543` item: *"A1: the
   seat recommends a dated plan delta (a PL relating PL-1542/1705/1694) over a roadmap line.
   Lead: ADOPTED as the vehicle; a planner writes it after #1310 merges."* This file is written
   before #1310 merges, on the lead's 09:37:02 reservation; #1310's merge is therefore its
   activation need N1, not a precondition of writing it.
3. **The finding — `LG-1732` §"Audit", row A1** (`git show d85e3d72:docs/ledgers/LG-01732-*.md`,
   `:160`): `test_d7_splits_the_derived_changes_into_the_journeys_own_effects` *"holds the gated,
   DP-1-shaped list (`c1` `m_ncd: mount added (sub_graph:ncd-ladder@1)` and a hand-written `pin`
   row on a rate table)"*. *"The real list was read from the gate's demo run (11 changes, no
   sub-graph pin row) and committed in `5debb32a`, then reverted by `9c399b6b` because a post-gate
   test edit is not gated code (the maintainer's ACK condition 4)."* The disposition line
   (`:172`) repeats entry 1.

## What the reading at `d85e3d72` shows (the premises of the design)

- **P1. The split test's input is a literal.** `test_d7_splits_the_derived_changes_into_the_journeys_own_effects`
  (`backend/tests/test_wf699_journey.py:470-507`) builds `derived` by hand (six rows `c1`–`c6`,
  row `c6` being `{"kind": "pin", "description": "rate_tables pin rate_table:x@2 added"}`) and
  asserts `journey.split_effects(derived)`. Nothing ties that literal to what the code derives.
- **P2. `split_effects` is already right for the real list.** The auditor evaluated it by hand
  against `5debb32a`'s list: *"c4 to c10 to the table effect; c1, c2, c3, c11 to the structure
  effect"* (`LG-1732` `:160`). So a test that only **pastes** the real list in place of the
  hand-written one is green on `SL-1696`'s code and has no red. A red by cause needs a check that
  the literal **is** the derived list.
- **P3. The real list is reachable inside CI.** `test_wf699_journey_runs_end_to_end`
  (`:338-392`) runs the whole journey against the test database through `_world`, and the
  journey's `dislocation` (`examples/fremtpl2/journey.py:1040-1093`) reads the decomposing run
  back as `run` (`:1064`), whose `derived_changes`, `change_groups`, `attribution` and
  `attribution_summary` it checks before it records D7 `ok`. `JourneyResult` (`:200-208`) does not
  carry that run, so the test cannot see it.
- **P4. One token of the list is random per world.** `_world` names the fitted model
  `family = f"fremtpl2-gbm-{uuid4().hex[:6]}"` (`test_wf699_journey.py:257`), and the real list
  carries a `models pin model:<family>@1 added` row (`5debb32a`'s `c11`). An exact comparison must
  substitute that token from the world, not match it by pattern.
- **P5. The demo-seed list and the CI-world list are different runs.** `5debb32a`'s list came
  from the gate's demo run (`ncd-ladder@3`, `wf699-area@2`, `fremtpl2-gbm-130a2e`). `PL-1694`
  Acceptance 18 predicted `ncd-ladder@1`. Neither is evidence of what `_world` derives after
  `SL-1543`'s own journey edits (B4's `model_call`, the C1′ pin; `PL-1542` Task 5) — those edits
  can add derived changes. The copy must be taken from `SL-1543`'s own head, after its last
  journey edit.

## Decision points

| DP | Question | Options | Recommendation | Owner | Blocks | Ruled |
|---|---|---|---|---|---|---|
| **DP-A1-1** | **Which run's `derived_changes` is "the real derived list" of `PL-1694` Acceptance 18?** | **(a)** The decomposing D7 run of `test_wf699_journey_runs_end_to_end`'s own world (`_world`), at `SL-1543`'s head. The split test's literal is copied from it, and the end-to-end test asserts the literal **equals** that run's list (the world's model family substituted, P4). Red by cause on `SL-1696`'s hand-written list (P2); runs in CI on every change; drifts loudly when a later journey edit changes the list. Cost: the red and green need a DB run (N4). **(b)** The demo-seed run, copied as `5debb32a` did, with no equality check. Cost: green on `SL-1696`'s code (P2), so no red by cause; not reproducible in CI (the seed's versions and family, P5); stale silently after `SL-1543`'s journey edits. **(c)** No literal: the split test is folded into the end-to-end test and reads only the live run. Cost: loses the DB-free unit test, and `PL-1694`'s write set says *"no test deleted"* | **(a).** Only (a) gives the red by cause the lead's brief requires, and only (a) keeps Acceptance 18's "copied from a run of the fixed code" true after the copy: the equality check re-proves it on every CI run. (a) is within Acceptance 18's words; it replaces (b)'s source run, which the clause does not name | the decision-maker (`delivery-process.md` §3) | Task A Steps 2–5 | **ruled (a)** by RL 8060, confirmed by the maintainer 2026-10-16 09:51:34 BST with four conditions (Steps 2 to 5, Hand-off 3) |

No other decision is opened. Substituting the family token (P4) from `record` rather than by a
regular expression is not a separate choice: a pattern match would accept any family, and the
world knows the one it made.

## Status

`draft`. **DP-A1-1 is ruled (a)** (RL 8060; amended 2026-10-16), so no decision point is open. The
delta stays `draft` only until its mint, and becomes `active` at the mint (RL 8060, "What it
obliges"). The mint waits for N1 (#1310 merged) and goes with or after RL 8060's mint
(Hand-off 3). `SL-1543`'s GO stays the lead's (N5).
`SL-1543`'s row in [`../roadmap.md`](../roadmap.md) is not written by this file (Hand-off 1).

## Activation needs, each with its state at `0877e6e7`

| # | Need | State |
|---|---|---|
| N1 | **#1310 merged** (`SL-1696`, `PL-1694` Stage B): the D7 block, `split_effects` and the split test exist on `main` | **open**: #1310 is `OPEN`, head `d85e3d72` (`gh pr view 1310`, read 2026-10-16 09:3x BST) |
| N2 | **DP-A1-1 ruled** | **met** (amended 2026-10-16): RL 8060 rules (a); the maintainer confirmed it at 09:51:34 BST |
| N3 | **Serialisation** (`PL-1694` Activation needs, Stage A need 3 `:260`, Stage B need 4 `:278`): `SL-1543` is the second of the two to merge on `examples/fremtpl2/journey.py` and `backend/tests/test_wf699_journey.py`, so it re-merges `main` after N1 and re-runs the journey test and the journey run before its ACK | follows N1 |
| N4 | **A DB window granted by the lead** for Task A's red run and its two green runs (RL 8060 precision 2) (`seat-brief-common-2026-10-16.md` item 6: no DB window unless granted in writing); each run goes through `run-small.sh`, one test file | not requested |
| N5 | This delta minted; `SL-1543`'s GO stays the lead's (`PL-1705` N5) | — |

## Tasks

`PL-1542`'s and `PL-1705`'s tasks stand, except `PL-1542` Task 2 Step 2's approver count
(*amended 2026-10-16: one approver, distinct from submitter and author, not two; the dated
amendment after the header, on the maintainer's 10:17:07 BST ruling*). This delta adds **Task A**, run after Task 5 of
`PL-1542` (the last task that edits the journey) and before Task 6 (the gate), so the copied list
is the list `SL-1543`'s head derives (P5).

### Task A: the D7 split test on the real derived list, red first by cause (A1; `PL-1694` Acceptance 18)

**Files:**
- Modify: `examples/fremtpl2/journey.py` — `JourneyResult` (`:200-208` at `d85e3d72`) and
  `_Journey.dislocation` (`:1064`).
- Modify: `backend/tests/test_wf699_journey.py` — `_world` (`:257`), a new module constant,
  `test_wf699_journey_runs_end_to_end` (`:338-392`) and
  `test_d7_splits_the_derived_changes_into_the_journeys_own_effects` (`:470-507`).

**Interfaces:**
- Consumes: `journey.split_effects(derived) -> dict[str, list[str]] | None`,
  `journey.EFFECT_RATE_TABLES`, `journey.EFFECT_STRUCTURE` (`journey.py:1237-1258`); the
  `GET /dislocation-runs/{id}` body the journey already reads (`:1035-1037`).
- Produces: `JourneyResult.d7_run: dict[str, Any]` — the decomposing D7 run's body as read back;
  `record["gbm_family"]` in `_world`; `D7_DERIVED_CHANGES: Final[list[dict[str, str]]]` in the
  test module.

- [ ] **Step 1: The plumbing, no behaviour change.** Merge `main` (N1, N3) first. Then:

  In `journey.py`, `JourneyResult` gains one field (after `prod_premium_minor`):

  ```python
      d7_run: dict[str, Any] = field(default_factory=dict)
  ```

  and `dislocation` keeps the decomposing run, directly after
  `run_id, run = self.run_dislocation({**spec, "change_groups": groups})`:

  ```python
          self.result.d7_run = run
  ```

  In `test_wf699_journey.py`, `_world` records the family it made, directly after
  `family = f"fremtpl2-gbm-{uuid4().hex[:6]}"`:

  ```python
      record["gbm_family"] = family
  ```

  Move the split test's `derived` literal **byte for byte** (the six rows at `d85e3d72`
  `:479-496`) to a module constant above the split test, and make the test read it:

  ```python
  #: The `derived_changes` of the journey's decomposing D7 run in `_world`, as `id`, `kind` and
  #: `description` (`PL-1694` Acceptance 18; PL 8055). `{gbm_family}` stands for `_world`'s
  #: random model family; `test_wf699_journey_runs_end_to_end` asserts this list IS the run's.
  D7_DERIVED_CHANGES: Final[list[dict[str, str]]] = [
      # the six rows of d85e3d72 :479-496, unchanged
  ]
  ```

  (`from typing import Final` joins the existing `typing` import.) In the split test,
  `derived = D7_DERIVED_CHANGES`. Run `uv run pytest -q backend/tests/test_wf699_journey.py -k "d7_splits"`
  (no DB): passes, as at `d85e3d72`. Commit.

- [ ] **Step 2: Write the red.** At the end of `test_wf699_journey_runs_end_to_end`, add:

  ```python
      # PL-1694 Acceptance 18 (PL 8055): the split test's list IS this run's derived list.
      run = result.d7_run
      real = [
          {key: str(change[key]) for key in ("id", "kind", "description")}
          for change in run["derived_changes"]
      ]
      expected = [
          {**row, "description": row["description"].replace("{gbm_family}", record["gbm_family"])}
          for row in D7_DERIVED_CHANGES
      ]
      print(f"D7 gbm_family: {record['gbm_family']}")  # RL 8060 precision 2: the LG records it
      assert real == expected, json.dumps(real, ensure_ascii=False, indent=1)
      # The four checks of Acceptance 18, on the real run as stored.
      effects = journey.split_effects(real)
      assert effects is not None
      assert {group["name"]: group["changes"] for group in run["change_groups"]} == effects
      placed = [cid for ids in effects.values() for cid in ids]
      assert sorted(placed) == sorted(row["id"] for row in real)
      assert len(set(placed)) == len(placed)
      summary = run["attribution_summary"]
      total = int(summary["total_change_minor"])
      assert summary["method"] == "shapley"
      assert sum(int(item["shapley_minor"]) for item in run["attribution"]) == total
      isolated = sum(int(item["isolated_minor"]) for item in run["attribution"])
      assert isolated + int(summary["residual_minor"]) == total
  ```

  (`import json` joins the imports.)

  **The substitution (RL 8060; the maintainer's condition 2, 2026-10-16 09:51:34 BST).** The one
  random token that reaches a description is the world's family (RL 8060 V4). It maps to one
  fixed placeholder, `{gbm_family}`, by its exact value from `record`, at every place it occurs
  (`str.replace` replaces all). It is never a pattern that matches any random hex, so two rows that
  name the family both name `{gbm_family}`. Any other random token in a description makes the
  assert red; that is not by cause, and is a STOP to the lead.

  **The token list (the maintainer's entry "2026-10-16 09:54:43 BST — Maintainer: PL 8055
  condition 2 reading CONFIRMED — exact-value substitution of the one gbm family token" in
  `to-lead.md`).** The token list is RL 8060 V4's and has **one entry**: the world's gbm family,
  `record["gbm_family"]`, replaced by its exact value with `{gbm_family}`. There is **no general
  mapper**: a general first-appearance mapper would also absorb a new random token without a red.
  Adding an entry needs a dated line from the lead that cites the red that found it.
  *(Amended 2026-10-16, before the mint, by the planner, on that 09:54:43 entry.)*

- [ ] **Step 3: Run the red (N4's DB window, through `run-small.sh`).**

  Run: `uv run pytest -q backend/tests/test_wf699_journey.py -k end_to_end`
  Expected: **FAIL**, rc 1, at `assert real == expected`, with the message printing the real list
  as JSON. **By cause:** the list `SL-1696` wrote by hand is not the list the code derives (row
  `c6` `rate_tables pin rate_table:x@2 added` and the `x@1 → x@2` descriptions are not derived;
  `5debb32a` read 11 changes on the demo seed). **Not by cause, and a STOP to the lead:** an
  `AttributeError`, `KeyError`, `ImportError`, a fixture or DB error, or a `JourneyStepFailed`
  before D7 records `ok`. Record the run's command, rc and the failing assert's first and last
  lines verbatim in `SL-1543`'s ledger, **and the rows that differ** (the literal's rows not in
  the real list, and the real list's rows not in the literal). The red is **run**, not only read
  (the maintainer's condition 1 on RL 8060, 2026-10-16 09:51:34 BST); a red by any other cause is
  RL 8060's STOP.

- [ ] **Step 4: The green — copy, never write.** Replace `D7_DERIVED_CHANGES`'s rows with the
  JSON the red printed, unchanged except that the world's family (`record["gbm_family"]` of that
  run, e.g. `fremtpl2-gbm-1a2b3c`) becomes `{gbm_family}`. In the split test, write the expected
  groups from the copied ids, which `split_effects` places by kind: the `table_repointed` rows and
  any `pin` row whose description names `rate_table` in `EFFECT_RATE_TABLES`, every other row
  (the `m_ncd` mount among them) in `EFFECT_STRUCTURE`. Replace the two sub-list asserts, which
  index `derived[1:3]` and `derived[3:5]` by hand, with the sub-lists built from those groups:

  ```python
      ids = {row["id"]: row for row in derived}
      tables = [ids[cid] for cid in effects[journey.EFFECT_RATE_TABLES]]
      structure = [ids[cid] for cid in effects[journey.EFFECT_STRUCTURE]]
      assert journey.split_effects(tables) is None  # tables only: nothing else to decompose
      assert journey.split_effects(structure) is None  # structure only
  ```

  **The mount check of `PL-1694` Task 4 Step 2** is kept as one more assert in the split test: the
  row whose description starts `m_ncd: mount` is in `EFFECT_STRUCTURE` and its kind is not
  `table_repointed`.

  **The copy governs (RL 8060 precision 1).** `PL-1694` Acceptance 18's parenthetical predicted
  `m_ncd: mount added (sub_graph:ncd-ladder@1)`. A fresh world derives `ncd-ladder@3` (the ladder
  is built three times; RL 8060 V4, V5). Where the copied list differs from the parenthetical,
  the copied value is right, and that is not a STOP. **This step STOPs to the lead only if** no row's
  description starts `m_ncd: mount` (the fix's derived mount is missing), **or** that row's kind is
  `table_repointed`.

- [ ] **Step 5: Run the green and the broken-input check.**

  All runs are in one DB window (N4), each through `run-small.sh`.

  Run: `uv run pytest -q -rP backend/tests/test_wf699_journey.py -k end_to_end`
  Expected: PASS, rc 0; the captured output prints `D7 gbm_family: <family>`.
  **Run the same command a second time** (RL 8060 precision 2; the maintainer's condition 3,
  2026-10-16 09:51:34 BST). Expected: PASS, rc 0, with a **different** family. Each run makes a fresh
  workspace and a new family, so two greens prove the substitution and the determinism of the list
  (RL 8060 V4); one run cannot tell a deterministic list from a lucky one. If the two families are
  the same, or the second run is red, STOP to the lead.

  Run: `uv run pytest -q backend/tests/test_wf699_journey.py`. Expected: PASS, rc 0 (the split
  test and the rest of the file).

  Then change one character of one `description` in `D7_DERIVED_CHANGES`,
  run `-k end_to_end` again: FAIL at `assert real == expected` (the check fails on wrong input);
  revert the scratch edit and confirm `git diff --stat` is empty. Record every run in the ledger:
  the command verbatim and its rc, and for the two `-k end_to_end` greens the two families, beside
  Step 3's red.
  Commit:

  ```bash
  git -C <wt> add examples/fremtpl2/journey.py backend/tests/test_wf699_journey.py
  git -C <wt> commit -m "test(journey): the D7 split test holds the real derived list, tied to the run (A1, PL 8055)"
  ```

## Acceptance Standard

`PL-1542`'s and `PL-1705`'s acceptance items stand. This delta adds one item, cited as **PL 8055
item 1**; it is checked from the repository root on `SL-1543`'s merge tree.

1. **A1 discharged: the D7 split test is built on the real derived list (`PL-1694` Acceptance
   18).** (i) `uv run pytest -q backend/tests/test_wf699_journey.py` passes;
   (ii) `git grep -n 'D7_DERIVED_CHANGES' -- backend/tests/test_wf699_journey.py` prints the
   constant, its use in the split test and its use in `test_wf699_journey_runs_end_to_end`;
   (iii) `git grep -n 'rate_tables pin rate_table:x@2 added\|rate_table_ref x@1' -- backend/tests/test_wf699_journey.py`
   prints nothing; (iv) `git grep -n 'd7_run' -- examples/fremtpl2/journey.py` prints the field
   and its assignment; (v) `SL-1543`'s ledger carries Step 3's red (rc 1, at
   `assert real == expected`, the cause stated, the differing rows) and Step 5's runs, each
   with its command verbatim and its rc: the two `-k end_to_end` greens in one DB window with
   their two different families (RL 8060 precision 2), the whole-file green and the broken-input
   red. The mount row is checked as Step 4 states it, not against Acceptance 18's `@1` (RL 8060
   precision 1); (vi) the end-to-end test asserts partition, `method == "shapley"`,
   the Shapley parts summing to `total_change_minor`, and isolated + residual == total on the
   stored run (Step 2's block, read in the diff).

## Global Constraints

- **Serialised** on `examples/fremtpl2/journey.py` and `backend/tests/test_wf699_journey.py`
  after `SL-1696` (entry 1; `PL-1694` `:260`, `:278`).
- **No test deleted** (`PL-1694` write set, `:232`); the split test keeps its name.
- **The list is copied from a run, never written** (`PL-1694` Acceptance 18: *"ids, kinds,
  descriptions copied from a run of the fixed code"*).
- **No full gate, no full pytest, no DB window without the lead's written grant**
  (`seat-brief-common-2026-10-16.md` item 6; `executor.md`).
- `backend/src/`, `packages/` and `docs/contracts/` are not written by Task A; if one must change,
  STOP to the lead.

## Hand-off (not this plan's writes)

1. **The roadmap.** `SL-1543`'s row gains a dated line naming this delta, A1 and needs N1, N2 and
   N4; this planner writes `docs/roadmap.md` only for rows it cuts, so the line is the lead's.
2. **The discharge.** `SL-1543`'s auditor records A1 discharged against PL 8055 item 1 in
   `SL-1543`'s ledger audit; `LG-1732` is frozen at its merge and is not edited.
3. **Mint.** PL 8055 mints from working id 8055 after #1310, so the `LG-1732` cites resolve on
   `main`, and with or after RL 8060 (amended 2026-10-16: RL 8060 "What it obliges"; the
   maintainer's condition 4). RL 8060 joins `relates:` at the mint.

## Self-review

1. **The brief's items.** One task (Task A) and one acceptance item (PL 8055 item 1); red-first
   by cause on `SL-1696`'s hand-written list (Step 3), not on a missing name (Step 1 lands the
   plumbing first); serialisation (N3, Global Constraints); activation need #1310 (N1); relates
   `PL-1542`, `PL-1705`, `PL-1694`.
2. **One decision opened, not picked:** DP-A1-1, three options and a recommendation; `draft`
   until it is ruled. *(Amended 2026-10-16: ruled (a) by RL 8060, the recommendation; `draft`
   until the mint.)*
3. **Placeholders.** The constant's rows in Step 1 are a move of named lines, and in Step 4 a
   copy of a printed run: both are content the executor reads, not content this plan can know.
   Writing either here would be the hand-written list A1 is about.
4. **What was not executed.** No test ran. P2 rests on the auditor's hand evaluation; Step 3's
   STOP covers a red that is not by cause, and Step 4's STOP a list without the mount.
5. **Type consistency.** `JourneyResult` is a `@dataclass` (`journey.py:200`) already using
   `field(default_factory=…)`; `run["derived_changes"]`, `run["change_groups"]`,
   `run["attribution"]` and `run["attribution_summary"]` with the keys used in Step 2 are the
   ones `dislocation` reads at `:1068-1082`.
