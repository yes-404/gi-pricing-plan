---
id: RL-1917
family: ruling
title: PL-1787 DP-A1-1 — the real derived list is the D7 run of the end-to-end test's own world at SL-1543's head, tied to the split test's literal by an equality assert (option a)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-25   # drafted 2026-10-16 under working id 8060; minted 2026-10-25 as RL-1917
owner: decision-maker
tree: 0877e6e7a756c4621890713a4d3b016e75e33654
phase: P2
work: WK-1178
slice: SL-1543
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1787, PL-1542, PL-1705, PL-1694, SL-1543, SL-1696, LG-1732, FR-264]   # PL-8055 is PL 8055's working id; minted with or after PL 8055, after #1310 (the maintainer 2026-10-16 09:51:34 BST, condition (4)), which writes its minted id; LG-1732 resolves once #1310 is on main
---

# RL-1917 — PL-1787 DP-A1-1: which run is "the real derived list"

*Disclosure: drafted under **working id RL 8060**, reserved by the lead (team-lead) in
`~/gi-pricing-plan.local/handover/eta.md`, the entry stamped "2026-10-16 09:45:58 BST":
"RESERVED RL 8060 = the ruling on PL 8055 DP-A1-1 (which run is "the real derived list" for
SL-1543's A1 D7 split test) (decision-maker-a1)". The plan it rules on, PL-1787, is also a
working id, filed on `origin/pl-8055-sl1543-a1-delta-2026-10-16` @`397fb2e862ce956061978001c3f78f52af1bb27a`
and not edited here. The lead mints both; the mint sweep replaces the working ids. Written
2026-10-16 from 09:48 BST (`TZ=Europe/London date`) by the decision-maker (seat
decision-maker-a1, effort medium, inherited; no raise). **No test or code was run**: every
claim about behaviour below is a reading of the code at the named tree.*

## How this was ruled

- **The decision point** is PL-1787's DP-A1-1 (its "Decision points" table, row DP-A1-1, owner
  "the decision-maker (`delivery-process.md` §3)"), on the lead's brief to this seat of
  2026-10-16.
- **The owner of A1** is `SL-1543`, per the lead's from-lead entry "2026-10-14 20:25:11 BST"
  (`~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`): *"LEAD VERDICT on A1 (LOW;
  PL-1694 Acceptance 18 — the D7 split test on the REAL derived list; reverted under ACK cond.
  4): DEFERRED WITH OWNER = SL-1543 (WK-673; serialised on examples/fremtpl2/journey.py +
  backend/tests/test_wf699_journey.py after SL-1696; lands through its own gate)"*. `LG-1732`'s
  disposition line (`:172` at `d85e3d72`) repeats it.
- **Why `5debb32a` was reverted** — the lead's entry "2026-10-14 20:16:08 BST" in the same file:
  the copy was a *"POST-GATE CODE EDIT"* that *"breaks the maintainer's 20:15:08 ACK condition 4
  (code blob-identical to the gated 279970f5)"*; the revert is `9c399b6b` ("test: revert the
  post-gate D7 fixture change to the gated blob (SL-1696 ACK cond. 4)"). **The reason was
  process, not content**: nothing in either entry says the demo-seed list was wrong.

## Verified first

Trees: `origin/main` `0877e6e7` for `PL-1694`; `SL-1696`'s head on #1310,
`d85e3d724f49c4e353bd9d066a3871b841f64aa9`, for the code (the code PL-1787 Task A edits after
#1310 merges). Line numbers are at `d85e3d72` unless named otherwise.

1. **The clause.** `PL-1694` Acceptance 18 (`origin/main`, `:395-404`): *"the D7 split test
   built on the **real** derived list (ids, kinds, descriptions copied from a run of the fixed
   code …)"*. It names no particular run. Its parenthetical also predicts the mount description
   *"`m_ncd: mount added (sub_graph:ncd-ladder@1)`"*; see V5.
2. **The finding.** `LG-1732` §Audit row A1 (`:160`): the committed split test *"holds the gated,
   DP-1-shaped list (`c1` `m_ncd: mount added (sub_graph:ncd-ladder@1)` and a hand-written `pin`
   row on a rate table)"*. Confirmed against `backend/tests/test_wf699_journey.py:470-507`: six
   hand-written rows, among them `c2` `s_t_region: rate_table_ref x@1 → x@2`, `c3`
   `s_t_area: rate_table_ref y@1 → y@2`, `c5` `s_premium: expr a → b` and `c6`
   `{"kind": "pin", "description": "rate_tables pin rate_table:x@2 added"}`.
3. **(a)'s red would be by cause (read, not run).** The equality assert of PL-1787 Task A Step 2
   compares that literal with the run's `derived_changes`, which
   `packages/pricing-core/src/pricing_core/rating/analysis.py` `_derive` (`:581`) builds. It
   cannot equal the literal:
   - a repoint row is rendered as `"<step_id>: rate_table_ref <before> → <after>"` from the
     algorithm's full refs (`_render`, `:577`), and the world's tables are the seeded
     `fremtpl2-*` and the journey's `wf699-*` slugs (`5debb32a`'s real list:
     `s_t_area: rate_table_ref rate_table:fremtpl2-area@1 → rate_table:wf699-area@2`). No table
     named `x` or `y` exists in the world, so rows `c2`, `c3` cannot occur;
   - a pin that a step change already names is **not** its own change (`ref not in step_refs`,
     `:666`, `:669`), so a `rate_tables pin` row on a repointed table cannot occur either; the
     demo run had none (`5debb32a`, 11 rows);
   - the counts differ (6 hand-written; 11 on the demo seed, with the same journey code).
   So on `SL-1696`'s code the assert fails on the list's content, not on a missing name. This
   is a reading; Step 3 of PL-1787 is where it is proved, and its STOP clause (a red that is not
   at `assert real == expected`) stands.
4. **`_world`'s derived list is deterministic apart from the model family.**
   - **Order.** Ids are numbered in one fixed order (`:723`): step and mount changes sorted by
     node id (`:651`), then pin changes sorted by `(ref, description)` (`:671`), then interface
     changes sorted by name. `_render` dumps dicts with `sort_keys=True` (`:577`).
   - **Versions.** Every version in a description is allocated `max + 1` **per workspace**:
     sub-graphs (`backend/src/app/platform/sub_graphs.py:53-58`), rate tables (the
     `RateTableRow` looked up by workspace and slug, `rate_tables.py:193-196`, then
     `current_version + 1`), rating versions (`rating_versions.py:291-297`). The `workspace_id`
     fixture is *"A fresh workspace per test"* (`backend/tests/conftest_db.py:324-326`). So the
     versions depend only on the journey's own calls: for example the ladder is built three
     times (`examples/fremtpl2/journey.py:719`, `:907`, `:927`), so its ref is `@3` in every
     fresh world, as it was on the demo seed (`5debb32a`'s `c1`).
   - **Random tokens.** `_world` draws `uuid4()` three times (`test_wf699_journey.py:257`,
     `:266`, `:313`): the model family, a `spec_hash`, a `dataset_id`. Only the family reaches a
     description: the journey reads the fitted model back as
     `self.gbm_ref = f"model:{gbm['model_family_slug']}@{gbm['version']}"` (`journey.py:314`)
     and pins it, which derives `models pin model:<family>@1 added` (`5debb32a`'s `c11`). That is
     PL-1787's P4, and Step 2 substitutes it from `record["gbm_family"]` exactly.
   - **The one place the family could move the order** is the pin sort key (`:671`). It can only
     reorder two pin refs that agree up to the random hex, that is two `model:fremtpl2-gbm-…`
     refs; `_world` makes one. Against every other ref the order is decided by the fixed prefix.
   - **Conclusion:** (a) does not flake on the list. If a later edit adds a second random
     family to the pins, the order could become random and the assert would show it on the first
     run that crosses; the green run twice (Ruled, item 3) is the check.
5. **The `@1` in Acceptance 18 is a prediction the code does not bear out.** Per V4, a fresh
   world derives `ncd-ladder@3`, not `@1`. The clause's operative words are *"copied from a
   run"*; the parenthetical says what the planner expected the run to show.
6. **(a) runs in CI.** `test_wf699_journey_runs_end_to_end` (`:330-338`) carries no skip marker,
   and `.github/workflows/python.yml` runs `pytest` with a `postgres` service (`:92`, `:113`).
7. **(c)'s premise.** `PL-1694`'s write-set row for `backend/tests/test_wf699_journey.py`
   (`origin/main`, `:232`) says *"no test deleted"*, and PL-1787 Global Constraints adopts it for
   Task A. Folding the split test into the end-to-end test deletes it.

## Ruled

**DP-A1-1: option (a).** "The real derived list" of `PL-1694` Acceptance 18 is the
`derived_changes` of the decomposing D7 run of `test_wf699_journey_runs_end_to_end`'s own world
(`_world`), at `SL-1543`'s head after its last journey edit. The split test's literal
`D7_DERIVED_CHANGES` is copied from it, with the world's model family written as
`{gbm_family}`, and the end-to-end test asserts the literal **equals** that run's list as PL-1787
Task A Steps 2 to 5 write it.

**Why (a):**

- It is the only option with a red by cause on `SL-1696`'s list (V3). (b) is green on that code
  (PL-1787 P2, the auditor's hand evaluation in `LG-1732` `:160`), so it proves nothing.
- It keeps "copied from a run of the fixed code" true **after** the copy: CI re-proves it on
  every run (V6), and a later journey edit that changes the list reds the assert by name instead
  of leaving a stale literal (PL-1787 P5). (b) goes stale silently.
- It answers the reason `5debb32a` was reverted (process, not content): the copy lands in Task A,
  before `PL-1542` Task 6's gate, so the gated code contains it.
- (c) deletes a test (V7) and loses the DB-free check of `split_effects`.
- Its premise holds on reading: no flake from the world (V4).

**Two precisions, binding on Task A:**

1. **The copy governs the parenthetical.** Where the copied list differs from Acceptance 18's
   predicted forms (V5: `ncd-ladder@3` where it says `@1`), the copy is right and is not a STOP.
   PL-1787 Step 4's STOP fires only if **no** row's description starts `m_ncd: mount`, or if that
   row's kind is `table_repointed`. The auditor discharges Acceptance 18's split-test clause
   against PL-1787 item 1, not against the parenthetical's version number.
2. **The green runs twice.** PL-1787 Step 5's green run of
   `uv run pytest -q backend/tests/test_wf699_journey.py -k end_to_end` is run a second time, in
   the same DB window, through `run-small.sh`. Each run makes a fresh workspace and a new family,
   so two greens prove the substitution and the determinism of V4 on the code, not only on this
   reading (one run cannot tell a deterministic list from a lucky one). Both commands, rcs and the
   two families are recorded in `SL-1543`'s ledger beside Step 3's red.

## What it obliges

- **`SL-1543`'s executor:** PL-1787 Task A as written, with the two precisions.
- **`SL-1543`'s auditor:** PL-1787 item 1, plus precision 2's two green runs in the ledger.
- **The lead:** mint RL-1917 with PL-1787 (PL-1787 N2 is met by this record); PL-1787's
  `status` becomes `active` at its mint, which is the plan's own rule, not this record's edit.

## Acceptance — the violation that must become detectable

A literal that is not the run's list must red. PL-1787 Step 5's broken-input check (one
character of one description changed, `-k end_to_end` fails at `assert real == expected`) is
that proof and stays required.

Adopted 2026-10-25 by the lead (lead 28) for filing, per to-lead "2026-10-25 11:24:40 GMT" and "2026-10-25 11:25:53 GMT". The record was confirmed by the maintainer's entry "2026-10-16 09:51:34 BST — Maintainer: RL 8060 (PL 8055 DP-A1-1 → (a)) CONFIRMED" (verified at 5b07a5b6) on four conditions: (1) the red is RUN, not only read, and PL-1787 Step 3 records it in the LG with the differing rows; (2) the uuid4 substitution maps each id to a stable placeholder by first appearance, never "any uuid"; (3) the green run twice in one DB window goes in the LG; (4) mint with or after PL-1787, after #1310. Folded from 88145ef6, whose only delta from 5b07a5b6 is a trailing YAML comment on `relates:` (ids identical), per to-lead "2026-10-25 11:25:53 GMT". `status: active` and `tree:` are as the file carries them. Mints in the FD-1919 PR at its turn (working id 8060 until then).
