---
id: LG-8056
family: ledger
title: WK-1250 slice SL-1341 — FR-218's purpose mount and the real check (retires RL-1242), PL-1629 slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-16
owner: executor
tree: 5576628141a98b5ce768096a7a0e96b212f1f761
phase: P2
work: WK-1250
slice: SL-1341
plans: [PL-1629]
corrected_by: []
relates: [PL-1629, RL-1344, RL-1628, RL-1242, RL-1571, LG-1588, SL-1341, FR-218, FR-212, FR-217, FR-239]
---

# LG 8056 — SL-1341: FR-218's purpose mount and the real check

Executed by `executor-1341b` (sonnet, medium) from **PL-1629** (`active`), binding **RL-1344** §2, §3, §4 (Slice 3 bullet) and
**RL-1628** (T1 to T3, "What it obliges"). Branch `sl-1341-wk1250-s3-purpose-mount`, worktree `.claude/worktrees/sl-1341`,
base `origin/main` `0877e6e7` merged at `c1f7c447`.
**GO:** the maintainer (by delegation), `to-lead.md` "2026-10-16 09:35:13 BST"; the lead's request in
`from-lead-2026-10-09.md`, entry "SL-1341 … GO-READY". That entry is the dispatch record (need 3).
**MERGE-ACK:** at the lead's merge turn (not yet).

**Dispatch-record locators** (the GO entry carries them by locator at `origin/main` `0877e6e7`): `RL-1344` §2 (`:113-133`),
§3 (`:134-153`), §4's Slice 3 bullet (`:154-172`); `RL-1628` "What it obliges" (`:150-168`), with acceptance 9's writer at `:224`.
Conditions of the GO: SL-1566's `score.py` edits make the plan's cites stale (recorded below); `sl-1547-wk675-s5` is not touched,
and whichever of the two merges second re-merges and re-runs `generate-contracts`.

## Tasks

| Task | Commit | State |
|---|---|---|
| 1 spec: RL-1628 T1, T2, T3 (+ the `CompiledBundle` field note in `03` §5.x) | `aa482243` | done; audit-docs rc 0 |
| 2 `SubGraphRef.purposes`, FR-212 per purpose, R1 | `c06677f6` | done |
| 3 `inline_mounts(purpose=)`, `Bundle.purpose_graphs`, `bundle_hash`, `load_bundle` per purpose | `53019ea3` | done |
| 4 the real check and one selector for every algorithm/decision read; interim tests rewritten | `e17a0f62` (pricing-core), `f534d6d8` (backend route tests) | done |
| 5 FR-218 strike; `RL-1242` `status: retired` (status line only; RL-1628 names the writer) | `658c4cd6` | done |
| 6 full gate; backend route tests run | — | **not done** (gate barred; route tests need the DB) |

**Beyond the plan's text** (the two changes ruled on in the next section; the rest below is in the plan). `AlgorithmSubGraphChange.purposes_changed` (and its change-summary wording): without it a change
to `purposes` alone was not in `diff_algorithms`, failing RL-1344 acceptance 5. `backend/src/app/api/score.py`'s compare route
reads the purpose's algorithm for its trace diff. `MountPurpose` is stated once beside `QuotePurpose`. The hand-authored
`rating-algorithm.schema.json` carries `purposes`; `docs/contracts/openapi/generated.json` regenerated.

## Out-of-plan changes (for the auditor to rule on)

1. `backend/src/app/api/score.py`, `score_compare`: `algorithms.append(compiled.evaluation_for(body.context.purpose).algorithm)`
   instead of `compiled.algorithm`. Reason: the trace being diffed was produced by the purpose's algorithm, so the diff must read the
   same one. Plan clause: RL-1628 DP-S3-2 condition 1 ("every read of `bundle.algorithm` … goes through" the selector), carried by
   PL-1629 Task 4 Step 3 (P5); the plan's list of reads named only `score.py`.
2. `AlgorithmSubGraphChange.purposes_changed` (`model_schema/rating.py`), set in `_diff_mounts`, one change-summary clause
   (`backend/src/app/platform/change_summary.py`), the test `test_a_change_to_a_mounts_purposes_alone_appears_in_the_diff_as_a_mount_change`,
   and the regenerated `docs/contracts/openapi/generated.json`. Reason: before it, a change to `purposes` alone produced no mount
   change in `diff_algorithms`. Plan clause: PL-1629 acceptance 7 / RL-1344 acceptance 5 ("a change to a mount's `purposes` alone
   appears in `diff_algorithms` as a mount change"); no task named the diff code.

## Stale cites (plan/ruling cite → at base `c1f7c447`)

`docs/specs/03-rating-engine.md`: RL-1628 T1 find `:340` → `:341`; T1 anchor `:349` → `:350`; T2 anchor `:943` → `:980`;
T3 anchor `:1154` → `:1195`; FR-218 `:87` unchanged. Each anchor counted exactly once at the base.
`packages/pricing-core/src/pricing_core/rating/score.py` (changed by SL-1566, `cad75a7e`):
`_check_purpose_mount` `:391` → `:392`; its calls `:941` → `:942` (`score_one` `:919` → `:920`) and `:1108` → `:1134`
(`_score_context_sync` `:1090` → `:1116`); `build_scoring_result` `:873` → `:874`; `_score_batch_row` `:1128` → `:1175`;
the reads of `bundle.algorithm`/`decision`: `score_one` `:939`, `:962`; `_score_context_sync` `:1132`, `:1143`;
`_score_batch_row` `:1191`. Not re-measured one by one: the `runtime.py`, `compile.py`, `inline.py` and `rating.py` cites.

**Completion of the `score.py` cites (2026-10-16 10:14 BST by `date`, `executor-1341d`, writing only).** The paragraph above omits five
of the plan's changed cites. Every `score.py` cite of PL-1629 (`:53`, `:120`, `:258-262`, `:386-392`, `:527`) is now paired with its line in
`git show c1f7c447:packages/pricing-core/src/pricing_core/rating/score.py` (read by `grep -n` and `sed -n` on that blob; the same lines
read identically in `0877e6e7`'s blob):
- `_check_purpose_mount` whole function `:391-421` (the plan's range includes the blank line before and the two after) → `:392-419`;
  its docstring `:392-410` → `:393-410`; the "interim" message line `:416` → `:417`.
- `build_scoring_result` reads `:887-902` → `:888-903` (`_check_lookup_misses` `:888`, `_apply_constraints` `:889`, `_ladder_inputs` `:891`,
  `_build_outputs` `:893`, `_build_trace` `:903`).
- `score_one` reads `:938`, `:961` → `:939`, `:962` (as above). `_score_context_sync` reads `:1106` → `:1132` (`algorithm = bundle.algorithm`);
  `:1117-1118` → `:1143-1144` (`bundle.decision.evaluate`, both arms). `_score_batch_row` `:1142` → `:1191` (as above); its def `:1128` → `:1175`.
- Test-file cites unchanged between `0877e6e7` and `c1f7c447` (`git show <sha>:packages/pricing-core/tests/test_rating_score.py`):
  `_compiled` `:160`, `_ctx` `:168`, the "interim" asserts `:512` and `:1030`.

## Proofs run (no full gate; run-small, ≤3 files each, before GATE START)

- model-schema `test_rating_algorithm.py` + `backend/tests/test_contracts.py` + `test_rating_purpose_mount.py`: 230 passed, 2 skipped.
- `test_rating_score.py` + `test_rating_compile_bundle.py` + `test_rating_inline.py`: 100 passed.
- `test_rating_runtime.py` + `test_quote_input_raise_sites.py` + `test_rating_shadowed_inputs.py`: 45 passed.
- `test_rating_wire_order.py` + `test_rating_mounted_model_call.py`: 17 passed. `test_input_free_raises.py` + `test_rating_algorithm_draft.py`: 8 passed.
- ruff and mypy on the touched files: rc 0. `generate-contracts.py --check`: rc 0. `audit-docs`, `doc-index`, `req-coverage`: rc 0.
- Acceptance 5 (not bypassable): `test_removing_the_real_check_would_be_caught` and `test_the_purpose_guard_would_be_caught_if_removed`
  patch `_check_purpose_mount` out and see the MTA quote priced; the patch is in the test, never committed.
- Acceptance 7, existing hashes: `test_rating_wire_order.py` and `test_rating_shadowed_inputs.py` pass unmodified; the re-run against
  WK-675 S5 (`SL-1547`) belongs to whichever slice merges second.

## Verdicts

FR-218's authoring half: delivered (the purpose mount, FR-212 per purpose, the real check, the interim rule's retirement); the route
tests (`backend/tests/test_score_purpose_mount.py`) are written and **delivered but untested** until a DB window runs them.

### Pre-gate audit (code and spec)

Written 2026-10-16 09:53 BST (by `date`) by `auditor-1341` (the auditor role), reading `git diff origin/main...b0ee492c`
(merge-base `0877e6e7`), the plan `PL-1629` at `origin/main`, `RL-1628` at `origin/main`, and the dispatch record (from-lead
"2026-10-16 09:34:47 BST"; to-lead "2026-10-16 09:35:13 BST"). **No test was run**; the gate half comes after the gate.
Scope was derived from PL-1629's tasks and acceptance items 1 to 12 first, then evidenced.

**Checked and conformant.**
- Write set: every changed path is in PL-1629's file table or Tasks 1 to 6, except the two ruled on below and the test files (A-3).
  `docs/INDEX.md`, `generated.json` and `rating-algorithm.schema.json` are Task 2 Step 4 and Task 5 outputs.
- T1, T2 and T3: each block of `RL-1628` (`<date>` replaced by 2026-10-16) is a verbatim substring of `03-rating-engine.md` at
  `b0ee492c` (checked by script, 3 of 3 found). The extra `CompiledBundle` note (`03` §4.x, one clause) is Task 1's "any other site".
- FR-218: the `RL-1242` amendment is wrapped in `~~ ~~` and followed by a dated strike citing `RL-1242:83-85` and `SL-1341`; the
  `RL-1344` clause gets a dated "Delivered" note (Task 1, bullet 1). FR-218's own text is otherwise unchanged.
- `RL-1242`: the diff is the `status:` line only (`active` to `retired`); commit `658c4cd6` cites RL-1628.
- Hash and bytes: `Bundle._without_an_empty_purpose_graphs` drops an empty `purpose_graphs` from the dump, and `bundle_hash` adds the key
  only when non-empty. The pinned-hash tests (`test_rating_shadowed_inputs.py`, `test_rating_wire_order.py`) are not in the diff
  (unmodified, acceptance 7); they and `test_rating_compile_bundle.py` `:510` are the proofs the gate must show green.
- Acceptance to test node, in `packages/pricing-core/tests/test_rating_purpose_mount.py` (P), `packages/model-schema/tests/test_rating_algorithm.py` (M),
  `backend/tests/test_score_purpose_mount.py` (B): 2 selector: M `test_a_purposes_selector_outside_the_two_admitted_purposes_is_refused`
  (5 forms), M `..._of_the_two_admitted_purposes_is_accepted` (3 forms), M `test_an_absent_selector_keeps_every_existing_mount_unconditional`;
  3: M `test_a_step_that_runs_for_every_purpose_cannot_consume_a_purpose_only_name`, `..._may_not_reach_the_risk_premium_output`,
  `test_a_second_re_producer_of_one_name_is_a_cycle`, `test_a_mount_re_producing_a_name_the_parent_already_re_produces_is_a_cycle`;
  4: P `test_a_cancellation_only_mount_refuses_a_mid_term_adjustment_quote`, `..._prices_a_cancellation_with_the_mount`,
  `..._leaves_new_business_exactly_as_without_it`, B `test_score_*`, `test_score_compare_*`; 5: P `test_removing_the_real_check_would_be_caught`
  and `test_the_purpose_guard_would_be_caught_if_removed`; 7: M `test_a_change_to_a_mounts_purposes_alone_appears_in_the_diff_as_a_mount_change`,
  P `test_a_change_to_purposes_alone_changes_the_content_hash`; 8: `test_rating_score.py` rewritten (bogus test deleted, G1 tests named in a comment);
  RL-1628 condition 1: P `test_a_constraint_inside_a_cancellation_mount_is_evaluated_for_it`; condition 2: P `test_load_bundle_refuses_a_purpose_graph_that_disagrees_with_its_algorithm`.
  `test_quote_input_raise_sites.py` is not in the diff (raise-site count unchanged, acceptance 8).

**Findings.**

| Id | Severity | Finding |
|---|---|---|
| A-1 | medium | **Acceptance 4 names the batch path; no test reaches it.** `_score_batch_row` was edited (`bundle.evaluation_for(ctx.purpose)` for `_outputs_json`) and `_score_context_sync` gained the real check, yet no new test calls `score_batch`/`_score_context_sync` with a purpose. The `grep -n "batch"` over both new test files returns nothing. Gap: delivered but untested. Owner: executor, one test (a cancellation-only mount, MTA row refused, cancellation row priced) before the gate. |
| A-2 | medium | **Acceptance 6 (G1 re-run with a selector on the mount) has no node.** The comment in `test_rating_score.py` `:505-510` names Slice 2's two G1 tests, which carry no `purposes`. No test in the diff compiles a purpose mount whose version is not in `Pins.sub_graphs` and expects `RATING_VERSION_UNPINNED`. The code path is shared, so the risk is low, but the item says "with a selector". |
| A-3 | low | **Test placement differs from the plan.** Task 3 names `test_rating_inline.py`, `test_rating_compile_bundle.py`, `test_rating_runtime.py`; Task 4 names `backend/tests/test_score.py`. The executor used two new files (`test_rating_purpose_mount.py`, `test_score_purpose_mount.py`), from the prep commit `77cbf522`. Coverage by id is unchanged. Record in the ledger as a deviation; no code change. |
| A-4 | low | **The hash-unchanged test is a tautology.** `test_a_version_with_no_purpose_mount_keeps_the_hash_it_had` asserts `bundle.content_hash == bundle_hash(bundle.graph, bundle.pins)`, which holds for any implementation of the new default. The real proofs are the unmodified pinned-hash tests. No test asserts the serialised bytes of an empty-`purpose_graphs` bundle omit the key (the `model_serializer` is untested directly). The gate must show the pinned-hash tests green; recommend one `"purpose_graphs" not in json.loads(bundle.model_dump_json())` assert. |
| A-5 | low | **RL-1628 condition 1 red-first names a clamp in the ladder; the test uses a decline.** `test_a_constraint_inside_a_cancellation_mount_is_evaluated_for_it` proves the purpose's algorithm is read (a `CANCEL_GUARD` decline), not that a clamp reaches the ladder. Same selector, so low. |
| A-6 | low | **The ledger is short of PL-1629 Task 6's list.** Tasks 2 to 4 carry a commit subject, not a SHA (`c06677f6`, `53019ea3`, `e17a0f62`, `f534d6d8` exist and are ancestors of `b0ee492c`); premises a to h are not recorded; the red-first quotes are not in the ledger (the dispatch entry says 25 reds by cause); the header `tree:` is a commit (`658c4cd6`), not a tree. |
| A-7 | low | **Reads of `bundle.algorithm` outside the Locators remain.** `testing.py:259,264`, `replay.py:68,76`, `analysis.py:180` read `input_contract` and `outputs` from the base algorithm. `inline_mounts` rebuilds `steps` only, so these are purpose-independent; condition 1 binds the Locators' scoring rows. Observation, no action; the compare route is ruled on below. |
| A-8 | low | **`FR-218`'s strike sits in the penultimate commit.** Acceptance 9 says "the slice's final commit"; `658c4cd6` is final among the code and spec commits, and `b0ee492c` adds the ledger only. Conformant in intent; the lead may read the ledger commit as outside "final". |

**Out-of-plan edits: proposed verdicts (the lead adopts or rejects).**
1. `backend/src/app/api/score.py` `score_compare`, `compiled.algorithm` to `compiled.evaluation_for(body.context.purpose).algorithm`:
   **in scope, as necessary to acceptance 4.** Acceptance 4 requires the real check "through `POST /api/v1/score/compare`", and
   RL-1628 condition 1 says the trace uses "the algorithm that was evaluated". The compare route diffs traces whose step ids are the
   purpose graph's; reading the base algorithm would mis-attribute them. The plan's file list named only the pricing-core `score.py`; the
   route is the same read. B `test_score_compare_prices_each_side_by_its_purposes_graph` covers it.
2. `AlgorithmSubGraphChange.purposes_changed` (+ `_diff_mounts`, one `change_summary.py` clause, the test, `generated.json`):
   **in scope, as necessary to acceptance 7.** Acceptance 7 (RL-1344 acceptance 5): "a change to a mount's `purposes` alone appears in
   `diff_algorithms` as a mount change". Before the edit `_diff_mounts` skipped a mount whose ref and ports were equal, so the item could not
   pass; the plan assumed Slice 2's limb covered it and named no task. The new field is a `model-schema` shape (`default False`,
   backward compatible) and `generated.json` was regenerated. The `change_summary.py` clause has no test (A-9, low, below).
   Note for the second-to-merge rule: both edits touch files `sl-1547-wk675-s5` also edits (`rating.py`, `generated.json`).
   A-9 (low): no test asserts the `(purposes changed)` wording in `change_summary.py`.

**Proposed verdict: conformant pending the gate, with A-1 and A-2 (medium) to close first** (one test each, no code change expected),
and A-3 to A-9 recorded. If the lead prefers, A-1 and A-2 may be carried to the gate window as `delivered but untested` with an owner.

### Executor response to the pre-gate audit (2026-10-16 09:56 BST, `executor-1341c`; writing only, nothing run)

The lead's verdicts: A-1, A-2, A-4, A-6, A-9 close now; A-3, A-5, A-7, A-8 noted, no action (A-3 is the recorded
deviation: two new test files instead of the plan's named ones, coverage by id unchanged). Each new test names its
audit item in its docstring and carries the plan's requirement markers. **None has been run.** Predicted result on the
current head for each is **GREEN** (the code exists); a red would be a code gap, to be reported, not fixed in `src`.

| Item | New test node | Predicted | Basis |
|---|---|---|---|
| A-1 | `test_rating_purpose_mount.py::test_a_batch_row_under_a_purpose_mount_is_priced_by_the_purposes_graph` | green | `_score_batch_row` reads `bundle.evaluation_for(ctx.purpose)`; the real check is in `_score_context_sync`; cancellation row equals `score_one`'s payable, new business 1507, mid-term row an error row naming the purpose |
| A-1 | `test_rating_purpose_mount.py::test_a_batch_row_reads_the_purposes_algorithm_for_its_decision` | green | the decline constraint exists only in the cancellation mount |
| A-2 | `test_rating_compile_bundle.py::test_g1_a_purpose_mount_whose_version_is_not_pinned_is_refused[not_pinned, pinned_at_another_version]` | green (one risk: reuses the purpose-mount fixture with `pinned=` varied, so a fixture error would show as a different code, not the pin refusal) | `mounted_fragments` refuses before the purpose graphs are built |
| A-4 | `test_rating_purpose_mount.py::test_the_serialised_bytes_of_a_bundle_with_no_purpose_mount_omit_the_key` | green | `Bundle._without_an_empty_purpose_graphs`; the hash is recomputed from the serialised parts, not by `bundle_hash` |
| A-9 | `backend/tests/test_change_summary_purposes.py` (2 nodes) | green | `_structural_lines` `(purposes changed)` clause; no DB |

A-4 finding kept: no pinned-bytes fixture of a stored pre-slice bundle exists in the repository, so "equals the pre-slice
bytes" is shown by the key's absence from both dumps plus the hash recomputed from the pre-slice canonical form.
`_bundle_with_a_mount` gained a `pinned=` parameter (default the one cancel ref) so A-2 reuses its fixture; every existing caller is unchanged.

**A-6, the ledger record.**
- Header `tree:` is now `5576628141a98b5ce768096a7a0e96b212f1f761`, the tree of `658c4cd6` (`git rev-parse 658c4cd6^{tree}`),
  the last code-and-spec commit. Trees of the others: `c06677f6` `5fe9885d`, `53019ea3` `8d39cbf7`, `e17a0f62` `b7537f59`,
  `f534d6d8` `0c1852c5`, `458d056b` (the audit's head) `26d8e2fc`.
- Task commits are in the table above (all ancestors of `458d056b`).
- **Premises a to h at the base `c1f7c447`** (`git show c1f7c447:<path>`, locators in the Stale cites section): a the interim guard
  `score.py:392` (message "interim" `:417`); b called at `:942` and `:1134`; c `QuotePurpose` five values `scoring.py:45`, `QuoteContext.purpose` `:106`;
  d `SubGraphRef` has `inputs`/`outputs` and no `purposes` (`rating.py:460-461`); e the interim tests `test_rating_score.py:512`, `:1030` ("interim" asserts);
  f FR-218's interim clause present in `03` row 87 ("an interim rule, `RL-1242`"); g `Bundle` `compile.py:632`, `bundle_hash(graph, pins)` `:661`;
  h `CompiledBundle` `runtime.py:941`. Each held at the base; this is a re-read of the cited line, not of the full clause.
- **Red-first quotes: NOT recorded here, and not fabricated.** The red-first tests were committed at `77cbf522` (SL-1341 prep). The red run's
  output (the dispatch entry's "25 reds by cause") was not captured in this ledger by the executor that ran it, and this seat ran nothing.
  Owner: `executor-1341b` or the lead, to paste the quoted failures from the run record; or the gate window re-derives them against
  `77cbf522` with the source reverted. Verdict for that Task 6 limb: **owed, with that owner**.


## Gate Step 0 (written 2026-10-16 10:14 BST by `date`, `executor-1341d`; nothing below has been run)

Authority: the maintainer's GO, `to-lead.md` "2026-10-16 09:35:13 BST" (red-first: "the gate re-proves them by cause at Step 0"), and the
lead's ruling in `from-lead-2026-10-09.md` (entry after the 09:56 response): **SL-1341's red-first quotes are owned by this gate's Step 0**; the
LG records them then. The run-small output of the prep (`25 failed, 33 passed`, `from-lead` "2026-10-16 09:34:47 BST") is the pre-build
evidence; the seat's table of node ids was never captured, so the list below is **derived by reading** `77cbf522`'s two test files, and the
Step 0 run confirms or corrects it.

**What runs.** Against `77cbf522` (the prep commit, before the source changed), not against the gate head: a detached worktree at `77cbf522`
(`git -C <main checkout> worktree add --detach .claude/worktrees/sl-1341-step0 77cbf522`; setup per `dev-commands`, done outside any ALONE
gate), then `run-small.sh <that worktree> packages/model-schema/tests/test_rating_algorithm.py packages/pricing-core/tests/test_rating_purpose_mount.py`
(2 files, no DB; RL-1626). Quote the `-rf` FAILED lines and the `N failed, N passed` line into this section. Expected: `25 failed, 33 passed`.
The worktree is removed after the quote is pasted.

**The 25 reds, by node and cause** (27 new cases in the two files: 14 + 13; 2 are controls and pass). Causes are the plan's: **(F)** `SubGraphRef`
has no `purposes` (`extra_forbidden`, or `AttributeError` on read), PL-1629 Task 2 premise d; **(I)** the interim guard (`score.py:392`, message
"interim" `:417`), premise a. File M = `packages/model-schema/tests/test_rating_algorithm.py`, P = `packages/pricing-core/tests/test_rating_purpose_mount.py`.

| # | Node (`<file>::<test>`) | Cause |
|---|---|---|
| 1-5 | M `::test_a_purposes_selector_outside_the_two_admitted_purposes_is_refused[bad0..bad4]` (5 forms) | F: asserts `extra_forbidden` is absent |
| 6-8 | M `::test_a_purposes_selector_of_the_two_admitted_purposes_is_accepted[good0..good2]` (3 forms) | F: `extra_forbidden` raised on an admitted selector |
| 9 | M `::test_an_absent_selector_keeps_every_existing_mount_unconditional` | F: `SubGraphRef.purposes` does not exist (`AttributeError`) |
| 10 | M `::test_a_step_that_runs_for_every_purpose_cannot_consume_a_purpose_only_name` | F: no `GraphUnresolvedRefError`; the field is refused first |
| 11 | M `::test_a_purpose_mount_may_re_produce_a_parent_name` | F: `extra_forbidden` on a valid input |
| 12 | M `::test_a_purpose_mount_may_not_reach_the_risk_premium_output` | F: asserts `extra_forbidden` is absent |
| 13 | M `::test_a_second_re_producer_of_one_name_is_a_cycle` | F: no `GraphCycleError`; the field is refused first |
| 14 | M `::test_a_mount_re_producing_a_name_the_parent_already_re_produces_is_a_cycle` | F: no `GraphCycleError`; the field is refused first |
| 15-16 | P `::test_a_version_with_only_an_unconditional_mount_is_refused_by_the_real_check[mid_term_adjustment,cancellation]` | I: the message still says "interim" |
| 17 | P `::test_a_cancellation_only_mount_refuses_a_mid_term_adjustment_quote` | F (the fixture mounts `purposes`), the first error; the refusal's wording is I |
| 18 | P `::test_a_cancellation_only_mount_prices_a_cancellation_with_the_mount` | F, then I (the interim guard refuses a cancellation) |
| 19 | P `::test_a_cancellation_only_mount_leaves_new_business_exactly_as_without_it` | F |
| 20 | P `::test_a_constraint_inside_a_cancellation_mount_is_evaluated_for_it` | F, then I |
| 21 | P `::test_removing_the_real_check_would_be_caught` | F (fixture) |
| 22 | P `::test_compile_bundle_emits_a_graph_for_exactly_the_selected_purposes` | F; `Bundle.purpose_graphs` absent |
| 23 | P `::test_a_change_to_purposes_alone_changes_the_content_hash` | F |
| 24 | P `::test_load_bundle_refuses_a_purpose_graph_that_disagrees_with_its_algorithm` | F; `Bundle.purpose_graphs` absent |
| 25 | P `::test_inline_mounts_inlines_a_purpose_mount_for_its_purpose_only` | F; `inline_mounts` has no `purpose=` |

The two **controls, expected green at `77cbf522`**: P `::test_the_fixture_prices_new_business_with_an_unconditional_re_producing_mount` (the
test's own docstring: "Control: not red") and P `::test_a_version_with_no_purpose_mount_keeps_the_hash_it_had` (the unconditional mount,
`bundle_hash(graph, pins)` as before). **Rule for the quote:** for each of the 25, read the first error line; a red whose first error is
neither F nor I is a plan defect and is reported, not fixed. A control that is red, or a count other than 25, stops the gate before Step 1.
The rows 17 to 21 name the fixture first; whether the interim guard (I) is reached after it is read from the run, not assumed.

**The 5 route tests, for the small slot first** (`backend/tests/test_score_purpose_mount.py`, DB-backed, so a granted DB window, not run-small
alone): `::test_score_prices_a_cancellation_with_the_purpose_mount`, `::test_score_prices_new_business_as_if_the_cancellation_mount_were_absent`,
`::test_score_refuses_a_mid_term_adjustment_the_cancellation_mount_does_not_serve`,
`::test_score_compare_prices_each_side_by_its_purposes_graph`, `::test_score_compare_refuses_a_mid_term_adjustment_naming_the_failing_side`.
They run before the full pytest so a route red is read alone. Predicted green (the code exists); a red is a code gap, reported, not fixed in `src`.
The full gate (`sl1341-gate.sh`, `EXPECT_HEAD` = the head at the lead's grant) then runs every one again.

**Shared paths with SL-1547 (`sl-1547-wk675-s5`, unmerged, draft)**: both edit `model_schema/rating.py`, `rating-algorithm.schema.json` and
`03-rating-engine.md` at the plan's anchors; this slice also changed `docs/contracts/openapi/generated.json`. **Whichever of the two merges
second re-merges `origin/main` (a merge, never a rebase), re-runs `python scripts/generate-contracts.py --check` (regenerating `generated.json`
if red), and re-runs the pinned-hash and quote-form tests** (`test_rating_shadowed_inputs.py`, `test_rating_wire_order.py`,
`test_rating_compile_bundle.py`, `test_quote_input_raise_sites.py`, `test_rating_purpose_mount.py`); the second merge's ACK checks the contract
diff (the maintainer's GO, "4 MET with its caveats"). Neither slice's ledger edits the other's paths to make a conflict disappear.

**Re-merge of `origin/main`, 2026-10-16 10:28 BST (BST)**: merged `origin/main` a2f77b2dcad5aaec41a5f10aa664383caf421e8b (#1309, SL-1702) into this branch with `git merge --no-ff` (`merge-tree --write-tree` rc 1 before; the one conflicting path was `docs/INDEX.md`, resolved by taking main's side, regeneration owed). No other conflicts. Files changed by both #1309 (`0877e6e7..a2f77b2d`) and this slice, auto-merged cleanly: `backend/src/app/platform/change_summary.py`, `docs/contracts/openapi/generated.json`, `docs/specs/03-rating-engine.md`, `packages/model-schema/src/model_schema/rating.py`. **Owed after the SL-1455 GATE END**: (1) `docs/INDEX.md` regeneration under the gate-2 flock; (2) `generate-contracts.py --check` (SL-1702 added `RateTableChange.step_id` to `generated.json` and `rating.py`); (3) the Step 0 reds re-proved on the new base, the 25 reds' causes must not change; then the full gate on the new head after the lead's grant.

## PRs

One PR for this slice (L1 (a')): opened and merged by the lead; not yet opened.
