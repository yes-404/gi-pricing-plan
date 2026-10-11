---
id: PL-1629
family: plan
kind: leaf
title: WK-1250 Slice 3 — FR-218's purpose mount and the real check (retires RL-1242): leaf plan
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-10-11            # original date 2026-10-05, set at the draft; minted 2026-10-11
owner: planner
tree: 02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a   # refreshed 2026-10-11; first written at cdaaa573
phase: P2
work: WK-1250
slice: SL-1341
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1254, PL-1325, RL-1344, RL-1309, RL-1242, FD-1241, RL-1263, PL-1371, PL-1572, RL-1571, RL-1519, RL-1445, SL-1436, PL-1546]
---

# PL-1629 — WK-1250 Slice 3: FR-218's purpose mount and the real check, leaf plan

Filed under working id 9609. It is the leaf plan for `SL-1341` (`draft`, minted 2026-09-30, in
[`../roadmap.md`](../roadmap.md) under `### WK-1250`), which is `PL-1254` Task 3. The lead
re-issued the id (`~/gi-pricing-plan.local/handover/eta.md`, row "PL 9609", "RE-ISSUED: WK-1250
S3 leaf plan on SL-1341", 5 Oct 15:34:40). The row is not edited here; its "leaf plan" note is
added at the mint. It builds on Slice 2's leaf plan, **`PL-1572`** (PL 9610 minted in D5,
2026-10-10). *(refreshed 2026-10-11)* Everything below was first read at `origin/main`
`cdaaa57345cb765f96034ce1ec2733c338f1c3cd` on 2026-10-05, and **every need, line cite and
file:line was re-read at `origin/main` `02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a` (#1273,
`SL-1600`) on 2026-10-11** (§"Pre-mint refresh, 2026-10-11"), unless a line names a branch. *(refreshed 2026-10-11)*
**No test was run at planning time.**

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds:
> - `test-driven-development`;
> - `spec-change` (Task 1: FR-218's strike);
> - `contract-schema` and `contract-guard` (Task 2);
> - `python-package`;
> - `python-test`;
> - `dev-commands`;
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

## Goal

Price a `mid_term_adjustment` or `cancellation` quote with the **same** Rating Algorithm for the
risk price, plus a separately versioned sub-graph mounted only for that purpose (FR-218, `03:87`):
- `SubGraphRef` gains `RL-1344`'s optional `purposes` selector;
- FR-212 holds for each purpose's graph;
- the bundle carries what each purpose evaluates, and its hash covers it;
- `_check_purpose_mount` (`score.py:391-421`) *(refreshed 2026-10-11)* becomes the **real check**: refuse unless the
  bundle inlines a mount for this purpose.

The slice then strikes `RL-1242`'s interim clause in FR-218.

**G2.** No step of `PL-1544` needs this slice: *"Slice 3 serves no PL-1544 step"* (`PL-1572:64`). *(refreshed 2026-10-11)* `PL-1371:218` places this slice on lane B after Slice 2, in the week
of 24–30 Oct (`PL-1371:305`). It is not on G2's critical path (`to-lead.md` entry headed
"2026-10-05 15:37:35 BST", the WK-1250 line).

## Status

The status is the `status:` field in the header, and nothing else. **It stays `draft` while
DP-S3-1 and DP-S3-2 below are open.** `RL-1344` §3 requires them to be *"raised as a decision
point in its leaf plan before the slice starts"* (`RL-1344:180-181`). They are the
decision-maker's. **Both are now ruled by RL-1628** (minted in the same D12 batch; refreshed at
`origin/dm-9573-refresh-2026-10-11` `ad05af54`, the refresh accepted by the maintainer (by
delegation), `to-lead.md` entry "2026-10-11 11:39:18 BST", item 4). DP-S3-1 is final at RL-1628's
ACK. RL-1628 mints in the same docs batch as this plan, before it, and this plan goes `active` at
that mint (the D5 precedent: PL 9610 + RL 9586 → `PL-1572` + `RL-1571`). *(refreshed 2026-10-11)*

**Activation needs, in order** (each with its state at `02f23b4a`) *(refreshed 2026-10-11)*:
1. **Slice 2 (`SL-1340`) closed.** `PL-1254:331`: *"Depends on: Slice 2."* **MET**: `docs/roadmap.md`
   `#### SL-1340`, `status: closed`, *"Closed 2026-10-10 as a Slice … ledger LG-1588"*.
2. **DP-S3-1 and DP-S3-2 ruled by an `RL-`.** **Met at RL-1628's mint**, which precedes this plan's
   in the same batch; DP-S3-1 is final at RL-1628's ACK.
3. **The dispatch record carries `RL-1344` §2, §3 and §4's Slice 3 bullet**, and the ruling on
   §3's open question (`RL-1344:180-181`), which is RL-1628, including its §"What it obliges"
   bullet naming acceptance 9's writer. Open until the GO.
4. **The `score.py` and `runtime.py` writers in flight have merged, or the dispatch record names
   the definitions.** The writers this plan named at `cdaaa573` have all landed: PL 9688 (the
   FD-1420 fix), PL 9776 (as `PL-1520`), and Slice 2 (`PL-1572`); `SL-1436` (`to_wire`) is
   `closed`. planner-d11's sweep at `d699a561` found no branch ahead of main touching
   `pricing_core/rating/{score,runtime,compile,inline}.py`
   (`~/gi-pricing-plan.local/handover/readiness-wk1250-s3-2026-10-11.md` §2 need 4 and §4).
   **`SL-1600` (#1273), which edited `SubGraphRef`, merged as `02f23b4a`, the refresh base**, so
   that serialisation is MET. **WK-675 S5 (`SL-1547`)** is named by definition (File contention
   below). This refresh ran no branch sweep (gate-1 was held). **Re-check at the GO.**

   `RL-1263:89` names `score.py` as a shared file.
5. **A free build slot and the single gate** (`RL-1445` item 1, `:127-128`: *"At most ONE full
   gate runs at a time on this VM"*; RL 9620 was its working id). Slice 2 is closed, so the
   same-Work rule (`RL-1445` item 2 (b), `:139-141`) no longer bites.
6. **The lead's dispatch.**

### Dependencies

- **On Slice 2 (`PL-1572`, closed).** This slice consumes these, by their landed names at
  `02f23b4a`: *(refreshed 2026-10-11)*
  - `SubGraphRef`'s port map (`model_schema/rating.py:445`, `inputs`/`outputs` `:458-459`);
  - `inline_mounts` (`inline.py:229`), `mounted_fragments` (`:190`) and `_stable_topological`
    (`:161`); a mount is inlined as one namespaced unit, so it can be gated as one unit
    (`RL-1344:177-179`);
  - `Pins.sub_graphs` (`rating.py:84`) and G1;
  - the diff limb;
  - DP-S2-1's answer, `RL-1571` C1: the algorithm is re-inlined at load behind a node-id check
    (`runtime.py` `_check_graph_matches_inlined_algorithm` `:962`, called by `load_bundle` `:974`).
- **No other WK-1250 or WK-674 dependency.** WK-675 S9 (`SL-1554`, the designer's sub-graph
  mounting) comes after this slice (`PL-1371:387-388`; `PL-1546` row 8, `:153`: *"`SL-1341`
  (WK-1250 S3) closed"*). It is not a dependency of this slice.

### File contention (`RL-1263` option (c), as amended by `RL-1445`) *(refreshed 2026-10-11)*

Read at `02f23b4a`; the in-flight column is planner-d11's file-set sweep at `d699a561`
(readiness memo §4) plus `SL-1600`'s merge. Re-checked at the GO.

| This slice's path | What it does there | Also changed by (in flight) | Under option (c) |
|---|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/score.py` | `_check_purpose_mount` (`:391-421`) rewritten; its two calls (`:941` in `score_one` `:919`, `:1108` in `_score_context_sync` `:1090`) take the bundle; every read of `bundle.algorithm` / `bundle.decision` in `build_scoring_result` (`:873`, `:887-902`), `score_one` (`:938`, `:961`), `_score_context_sync` (`:1106`, `:1117-1118`) and `_score_batch_row` (`:1128`, `:1142`) goes through the purpose selector (RL-1628, condition 1) | none found (`SL-1455`'s `score.py` is `backend/src/app/api/score.py`, `PL-1454:102`) | Re-check at the GO |
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | `CompiledBundle` (`:941`, fields `:956-959`) and `load_bundle` (`:974`): per purpose graph, its decision, algorithm and `model_call` handler; C1 per purpose graph (DP-S3-2 and its conditions) | none found | Re-check at the GO |
| `packages/pricing-core/src/pricing_core/rating/compile.py` | `Bundle` (`:632`), `compile_bundle`, `bundle_hash` (`:661`, the `sub_graphs` omission `:670-673`) | every `compile_bundle` writer (`PL-1371:291-294`). **WK-675 S5 (`SL-1547`, not yet branched)** edits `to_jdm` (`:600`), a different definition, but inside the hashed graph | **Serialised outright** with `compile_bundle` writers. With S5, named by definition; **both carry a hash-stability invariant** (DP-S3-2's "only when non-empty"; RL-1613 (working id) item 2's "omit when false"), so **whichever merges second re-runs the other's existing-hash test on its own tree** (acceptance 7) |
| `packages/pricing-core/src/pricing_core/rating/inline.py` | `inline_mounts` (`:229`) gains a `purpose` argument | none (Slice 2 closed) | — |
| `packages/model-schema/src/model_schema/rating.py` | `SubGraphRef.purposes` (`:445`); `graph_invariant_issues` (`:617`, raised from `RatingAlgorithm._graph_invariants` `:565`) per purpose | `SL-1600` edited `SubGraphRef` (`_no_namespace_separator` `:464-466`): **merged as `02f23b4a`, so MET**; WK-675 S4 (`RateTable*`), `SL-1503` (`RateTableDiffCell`), WK-675 S5 (`InputContractField`): different definitions | Names by definition |
| `docs/specs/03-rating-engine.md` FR-218 (`:87`), §4.1 (`:241`), §4.11 (`:919`), §5.2 (`:1139`) | Task 1 (RL-1628's T1 to T3) and Task 5 | no in-flight branch edits these sections (readiness memo §4) | **Serialises** where one appears (`RL-1263:89`) |
| `docs/contracts/schemas/rating-algorithm.schema.json` | `purposes` on the mount | none found | **Not exempt** (`RL-1263:113`) |
| `packages/pricing-core/tests/test_rating_score.py` `:477-543` and `:1016-1047` | the interim tests and `PL-1572`'s two Task 8 tests (acceptance 8) | none found | **An existing-test edit**, deliberate and named; nothing else in the file is edited |
| `packages/pricing-core/tests/test_quote_input_raise_sites.py` `:63` | the count, only if it changes | — | — |

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means the
failing run is quoted in the ledger, with its failing assert line and the cause the step
predicts. A failure for any other cause is a plan defect, reported and not worked around. Every new
test carries `@pytest.mark.req("FR-218")`, and also `FR-217` where it inlines.

1. **Spec** (Task 1).
   - FR-218's `RL-1242` interim clause is struck, dated, in `03:87`, citing this slice (`RL-1242:83-85`:
     *"It retires the interim rule in the same commit, with a dated strike"*).
   - RL-1628's T1 to T3 applied verbatim: *(refreshed 2026-10-11)* `03` §4.1 states FR-212 per purpose graph
     and DP-S3-1's rule (T1, `RL-1344` §3); §4.11 gains the purpose-mount bullet showing
     `purposes` on a mount (T2; §4.1's example mounts nothing since `RL-1519`, `03:344-347`);
     §5.2 says what the bundle carries per purpose (T3, DP-S3-2).
   - FR-217 and FR-258 are not reworded, and FR-218's own text is not reworded beyond the strike.
   - `python3 scripts/audit-docs.py` exits 0.
2. **The selector** (`RL-1344` acceptance 1; §2). Red first, one test per form:
   `purposes: ["renewal"]`, `["what_if"]`, `["new_business"]`, `[]` and
   `["cancellation", "cancellation"]` are each refused at save with `VALIDATION_FAILED`.
   `["mid_term_adjustment"]`, `["cancellation"]` and both together are accepted, and an absent
   selector keeps every existing mount's meaning.
3. **FR-212 per purpose** (`RL-1344` §3; acceptance 4). Red first: an algorithm in which a step
   that runs for every purpose consumes a name only a purpose mount produces is refused at save,
   naming the step and the purpose, with `RATING_GRAPH_UNRESOLVED_REF` (RL-1628). Also red first (RL-1628, DP-S3-1 (d)): a purpose mount whose steps reach the `risk_premium_minor` output is refused with `VALIDATION_FAILED` (R1); a second re-producer of a name already re-produced is refused with `RATING_GRAPH_CYCLIC` (Limit 2). *(refreshed 2026-10-11, RL-1628 P1)*
4. **The real check** (`RL-1344` acceptance 2; `RL-1242:83-85`). Red first, through `pricing-core`
   (`score_one` and the batch path) and through `POST /api/v1/score` and
   `POST /api/v1/score/compare`:
   - a version whose only purpose mount selects `cancellation` refuses a `mid_term_adjustment`
     quote with `INPUT_CONTRACT_VIOLATION`, and the message says no mount for this purpose is
     inlined, not "interim";
   - the same version prices a `cancellation` quote with the mount;
   - it prices a `new_business` quote **exactly** as the same version with that mount removed:
     the same `payable_premium_minor`, the same ladder, and the same trace step ids.
5. **Not bypassable** (`PL-1254` Task 3's gate outline). A version that inlines a sub-graph for
   one purpose does not price the other: the cancellation-only mount's steps are absent from an
   MTA evaluation, and the quote is refused by step 4's check. With the check removed locally, a
   test fails. That edit is never committed.
6. **G1, unchanged** (`RL-1344` acceptance 3): a purpose mount whose version is not in
   `Pins.sub_graphs` is refused at compile with `RATING_VERSION_UNPINNED`. This is Slice 2's G1
   test, re-run with a selector on the mount.
7. **Diff and hash** (`RL-1344` acceptance 5): a change to a mount's `purposes` alone appears in
   `diff_algorithms` as a mount change (Slice 2's limb), and changes the bundle's
   `content_hash`. **A version with no purpose mount keeps the hash it had at Slice 2** (the
   existing hash tests pass unmodified, including the pinned `_SCORE_FIXTURE_HASH` in
   `test_rating_shadowed_inputs.py:74` and `test_rating_wire_order.py:145`). **If WK-675 S5
   (`SL-1547`) merges first, this slice re-runs S5's existing-hash test (RL-1613 item 2 (ii)) on
   its own tree; if this slice merges first, S5 re-runs this one's.** The ledger quotes the run. *(refreshed 2026-10-11)*
8. **The interim tests rewritten** (`PL-1254:328-330`). The tests at
   `test_rating_score.py:477-543` are rewritten to the new rule: *(refreshed 2026-10-11)*
   - "no purpose sub-graph → refused" (`test_a_purpose_needing_a_sub_graph_is_refused_when_none_is_mounted`
     `:481`) and "other purposes unaffected" (`test_the_other_purposes_are_unaffected_on_the_same_algorithm`
     `:517`, `test_new_business_is_not_refused_by_the_purpose_guard` `:526`) stay, re-pointed to
     the real check;
   - the bogus-reference test (`test_a_bogus_sub_graph_ref_does_not_satisfy_the_purpose_guard`
     `:504`, helper `_compiled_with_bogus_sub_graph` `:490`) is deleted, because Slice 2's G1
     compile refusal now covers that case. The ledger names the Slice 2 test that does;
   - `test_the_purpose_guard_would_be_caught_if_removed` (`:534-543`) stays, re-pointed.

   **`PL-1572` Task 8's two tests** (`:1016-1047`, *"pinned so that WK-1250 Slice 3 changes it on
   purpose"*) are named existing-test edits too: *(refreshed 2026-10-11)*
   - `test_a_version_that_mounts_a_sub_graph_still_refuses_mta_and_cancellation` (`:1023`) asserts
     `"interim"` (`:1030`). Its mount has no `purposes`, so under DP-S3-2 (a) it yields no purpose
     graph and the quote is still refused, now by the real check: the `"interim"` assert is
     replaced by the real check's message;
   - `test_an_unconditional_mount_prices_a_new_business_quote_with_the_fragment` (`:1036`): an
     absent selector keeps every existing mount's meaning (acceptance 2), so its assertions
     still hold. The ledger states whether it was kept or re-pointed, and why.

   The raise-site count `("rating/score.py", "_check_purpose_mount"): 1`
   (`test_quote_input_raise_sites.py:63`) is unchanged, or the ledger says why it moved.
9. **`RL-1242` retired.** The strike (acceptance 1) is in the slice's final commit, as
   `RL-1242:83-85` requires. `RL-1242`'s `status:` goes `active → retired`, in the same commit.
   That status change is the decision-maker's (`document-ids.md` §1.6, RL row: *"`retired` when
   overridden with no successor"*), and **RL-1628 makes it** (§"What it obliges", last bullet):
   **the writer is Slice 3's executor**, who changes `RL-1242`'s `status:` line only, in the final
   commit, and the commit message cites RL-1628. The dispatch record names that bullet. *(refreshed 2026-10-11)* **`RL-1242`'s
   body is frozen and takes no note** (`document-ids.md` §1.5). `PL-1254:316-319`'s *"`RL-1242`
   gets a dated retirement note"* is therefore met by the dated strike and the status change.
   If the decision-maker rules that a body note is required, that is a correcting `RL-`, not an
   edit.
10. **Coverage and verdict.** `uv run python scripts/req-coverage.py` lists the new tests against
    FR-218. The ledger records **FR-218's authoring half delivered** (`PL-1254`'s scope for this
    Work).
11. **The gate.** The full two-half gate exits 0 under the single gate (`RL-1445` item 1). *(refreshed 2026-10-11)* The ledger
    quotes every rc, the `N passed` line and `HEAD`.
12. **MERGE-ACK**, as `PL-1572`'s acceptance 14. *(refreshed 2026-10-11)* A Slice closes on a clean audit and the lead's
    merge (`CLAUDE.md` §13).

## Global Constraints

- **Spec first** (`CLAUDE.md` §0).
- **One risk price** (FR-218). The selector admits only `mid_term_adjustment` and `cancellation`
  (`RL-1344` §2.3). A `new_business` or `renewal` quote never evaluates a purpose mount.
- **One bundle per Rating Version** (FR-239; `RL-1344` §3, second bullet).
- **One inliner** (Slice 2's), extended, never copied.
- **A shape is defined once, in `model-schema`** (`CLAUDE.md` §2).
- **No new error code**: RL-1628 names none. `RATING_GRAPH_CYCLIC`, `RATING_GRAPH_UNRESOLVED_REF`
  and `BUNDLE_COMPILE_FAILED` are in `RATING_ERROR_CODES` (`backend/src/app/errors.py:311`;
  `:313`, `:314`, `:324`), and `INPUT_CONTRACT_VIOLATION` (`:367`) and `VALIDATION_FAILED` are
  registered. *(refreshed 2026-10-11)*
- **A model-schema raise is an `InputFreeError`** with a literal message (`model_schema/input_free.py`;
  `packages/model-schema/tests/test_input_free_raises.py` rules (i) and (ii)), landed by `SL-1600`
  (#1273, merged as `02f23b4a`); `SubGraphRef._no_namespace_separator` (`rating.py:464-466`) is the
  neighbouring precedent. It still maps to `VALIDATION_FAILED`. *(refreshed 2026-10-11)*
- **Money is integer minor units or `Decimal`.** FR-248's ladder reconciles on every purpose's
  evaluation.
- **Do not build ahead of the phase.** No designer view (WK-675 S9). No APR or schedule
  (FR-252).

## Scope

### Requirement coverage, each id individually

| Spec section | Id | This slice |
|---|---|---|
| `03` §3.1 | FR-218 | **The authoring half**: the purpose mount, FR-212 per purpose, the real check, and the interim rule's retirement |
| `03` §3.1 | FR-212 | Checked for each purpose's graph (`RL-1344` §3) |
| `03` §3.1 | FR-217 | Purpose mounts use Slice 2's pin and inliner, unchanged |
| `03` §3.4 | FR-239 | One bundle per Rating Version; the hash covers each purpose's evaluation |
| `03` §3.8 | FR-258 | A purpose quote's trace shows the purpose mount's inlined steps (the Slice 2 form) |

**Not in this slice:** the designer view (WK-675 S9); G3 (WK-674 Slice 2); and any `04` GIPP or
ENBP work (`04` FR-294 is WK-685, Phase 4).

### Premises, read at `02f23b4a` (refreshed 2026-10-11; first read at `cdaaa573`)

| # | Premise | Evidence |
|---|---|---|
| a | The interim guard refuses both purposes, whatever is mounted | `score.py:391-421`; message contains "interim" (`:416`) |
| b | It is called on both scoring paths, with the algorithm | `score.py:941` (`score_one`), `:1108` (`_score_context_sync`) |
| c | `QuotePurpose` has five values | `model_schema/scoring.py:45`; `QuoteContext.purpose` `:106` |
| d | `SubGraphRef` has no `purposes` | `model_schema/rating.py:445`, fields `:456-459` (Slice 2's port map is `inputs`/`outputs`) |
| e | The interim tests | `test_rating_score.py:477-543` and `PL-1572` Task 8's `:1016-1047`, listed in acceptance 8 |
| f | FR-218's interim clause | `03:87`, *"(Amended 2026-09-29, an interim rule, `RL-1242` …)"* |
| g | The bundle has one graph | `Bundle` `compile.py:632` (`graph` `:642`, `pins` `:644`); `bundle_hash(graph, pins)` `:661`, omitting an empty `pins.sub_graphs` `:670-673` |
| h | `CompiledBundle` holds one decision | `runtime.py:941`, fields `:956-959` (`content_hash`, `decision`, `algorithm`, `boosters`) |

Each premise still holds at `02f23b4a`; only locators moved. The executor re-reads each premise
**at its own base**. *(refreshed 2026-10-11)*

### Decision points

**Ruled, and binding here:** `RL-1344` §2 (the selector), §3 (the real check from the bundle; one
bundle; FR-212 per purpose) and §4's Slice 3 bullet.

**Raised for the decision-maker, and ruled by RL-1628** (minted in the same D12 batch). *(refreshed 2026-10-11)* These are
`RL-1344` §3's open question, split in two. Each answer must fit inside §3's invariants. The table
below is the question as raised; **the ruling binds, not the recommendation**: DP-S3-1 is
**(d) re-production** (a purpose mount re-produces a parent name through FR-212's chain), with
R1 (no route to `risk_premium_minor`), Limit 2 (one re-producer per name), Limit 3 (author-placed
`X`) and Limit 4 (the stable topological order), accepted in principle and final at RL-1628's
ACK; DP-S3-2 is **(a)** with its two conditions (a per-purpose decision, algorithm and
`model_call` handler in `CompiledBundle`; `RL-1571`'s C1 per purpose graph). Read RL-1628's
§"Ruled" for the text.

| DP | Question | Options | Recommendation | Blocking |
|---|---|---|---|---|
| **DP-S3-1** | **How does a purpose mount's output reach the ladder and the payable?** `RL-1344` §3 asks, for example, *"whether a cancellation's refund is a new declared output, a ladder rung, or something else"* | (a) **Override.** A purpose mount's mapped output names a value that a parent step already produces, upstream of the ladder (for example the annual premium before `payable_premium`). In that purpose's graph, the mount's output replaces the parent's producer of that name. The parent's producer, and any step that feeds only it, is absent from that graph. The chain downstream (the ladder rungs, FR-248's reconciliation, the payable) is unchanged; (b) **new optional outputs.** Purpose mount outputs feed new declared outputs (`required: false`, for example `refund_minor`), present only for that purpose; `payable_premium_minor` stays the annual chain; (c) **a separate result section.** `ScoringResult` gains a `purpose_outputs` map | **(a).** FR-218 prices the MTA or cancellation itself with "pro-rata, refund and charge logic", so the **payable** of such a quote must be the adjusted figure. Under (b) and (c), `payable_premium_minor` on an MTA quote is the annual premium, a silent mispricing of the kind FR-218 exists to prevent. Under (a), each purpose graph still has exactly one producer per name (FR-212, `RL-1344` §3), and a name only a purpose mount produces still cannot be consumed by an always-running step (`RL-1344` acceptance 4), because under (a) every overridden name also has a parent producer. **Codes:** an override of a name no parent step produces, or of an `input` step's name, is refused at save with `RATING_GRAPH_UNRESOLVED_REF`; a consumer outside the mount of a purpose-only name, with the same code (acceptance 3) | Tasks 2–4 |
| **DP-S3-2** | **How are the inlined nodes gated by `purpose` at evaluation?** | (a) **One graph per purpose that has a mount.** `Bundle` gains `purpose_graphs: dict[str, JdmGraph]`, holding only the purposes some mount selects, so it is empty for every version without a purpose mount. `bundle_hash` covers it **only when non-empty**, so every existing hash is unchanged. `CompiledBundle` holds one decision per graph, and scoring chooses by `ctx.purpose`, falling back to the base graph; (b) **one graph with a `purpose` switch node** in `to_jdm`; (c) **scorer-side pruning** of the decision at run time | **(a).** Each purpose graph is a plain DAG, which is exactly what `RL-1344` §3's "FR-212 for each purpose's graph" checks, and the trace of a quote shows only what ran. (b) puts two producers of an overridden name in one graph, against FR-212 within the graph, and adds a node type to the ADR-706 translation layer. (c) evaluates a graph that is not the one that was hashed. One bundle per Rating Version (FR-239) holds under (a): one `Bundle`, several graphs | Tasks 3–4 |

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree, and `git branch --show-current` is the slice branch, cut
  from `main` after Slice 2 merged.
- [ ] `uv sync --all-packages`.
- [ ] Re-derive premises a–h at that tree and record each one. *(refreshed 2026-10-11)*
- [ ] `gh pr list --state open`, and read anything that rules on FR-218, `purpose`, sub-graphs,
  `score.py`, `runtime.py` or `Bundle`. Name the SHA read.
- [ ] Confirm DP-S3-1 and DP-S3-2's resolutions **by RL-1628's minted id**, and that its ACK made
  DP-S3-1 final. Stop if either differs from **Decision points**. *(refreshed 2026-10-11)*
- [ ] Confirm that the dispatch record carries `RL-1344` §2, §3, §4's Slice 3 bullet and RL-1628,
  including its bullet naming `RL-1242`'s status writer (acceptance 9). *(refreshed 2026-10-11)*

### Task 1: Spec — FR-218's strike, `03` §4.1, §4.11, and the bundle text

**Files:** `docs/specs/03-rating-engine.md`.

- [ ] **FR-218** (`03:87`). Strike the `RL-1242` amendment, dated, citing `RL-1242:83-85` and this
  slice. The `RL-1344` amendment's last clause, *"the interim rule above stands until WK-1250
  Slice 3 delivers this"*, gets a dated note that Slice 3 delivered it. **This edit lands in the
  slice's final commit** (acceptance 9), not here. Task 1 writes the rest.
- [ ] **§4.1.** RL-1628's **T1** verbatim: the per-purpose paragraph after the Slice 2 paragraph
  (`03:349`), giving FR-212 per purpose graph (`RL-1344` §3, third bullet) and DP-S3-1's rule. *(refreshed 2026-10-11)*
- [ ] **§4.11** (`03:919`). RL-1628's **T2** verbatim: the "Purpose mounts" bullet after the
  "Inlining and namespacing" bullet (`03:943`), which shows `purposes` on a mount and states that
  the purpose mount landed in WK-1250 Slice 3. *(refreshed 2026-10-11)*
- [ ] **The bundle text.** RL-1628's **T3** verbatim, after `load_bundle` in §5.2 (`03:1154`); then
  state what the bundle carries per purpose (DP-S3-2) at any other site where `03` describes
  `Bundle` and `compile_bundle` (Task 0 finds them with
  `grep -n 'resolved_payloads\|content_hash' docs/specs/03-rating-engine.md`). *(refreshed 2026-10-11)*
- [ ] Re-count each T1 to T3 anchor at the slice base; stop on any count other than one (RL-1628,
  §"The spec texts"). *(refreshed 2026-10-11)*
- [ ] `python3 scripts/audit-docs.py` exits 0.
- [ ] Commit: `docs(specs): 03 §4.1 and §4.11 — FR-218's purpose mount and per-purpose graphs (RL-1344)`.

### Task 2: `model-schema` — `SubGraphRef.purposes` and FR-212 per purpose

**Files:** `packages/model-schema/src/model_schema/rating.py`;
`docs/contracts/schemas/rating-algorithm.schema.json`. Test:
`packages/model-schema/tests/test_rating_algorithm.py` (appended).

**Interfaces:**
- Produces: `SubGraphRef.purposes: list[Literal["mid_term_adjustment", "cancellation"]] | None = None`.
  The `Literal` members are `QuotePurpose`'s (`model_schema/scoring.py:44`), restricted by
  `RL-1344` §2.2. Do not write a second purpose vocabulary: derive the admitted pair from
  `QuotePurpose`, or state it once beside it.

- [ ] **Step 1: Write the failing tests** (acceptance 2 and 3), mirroring the neighbouring algorithm
  builders. One test per refused form; the accepted forms; a step that runs for every purpose
  consuming a purpose-only name; DP-S3-1's re-production cases (RL-1628): a mount re-producing a parent name is accepted per purpose graph; R1's route to `risk_premium_minor` is refused; a second re-producer and a fragment step consuming `X` beside the re-producer are each refused as a cycle. *(refreshed 2026-10-11, RL-1628 P2)*
- [ ] **Step 2: Run them.** Expected: the selector cases fail on `extra="forbid"` (the field does
  not exist), and the FR-212 cases are accepted when they should be refused. Any other cause is a
  plan defect.
- [ ] **Step 3: Implement.**
  - Add the field: non-empty, no duplicates, the admitted pair only. Each violation is an
    `InputFreeError` (a `ValueError`; Global Constraints), so the route maps it to
    `VALIDATION_FAILED`, as `RL-1344` §2.2 says. *(refreshed 2026-10-11)*
  - `graph_invariant_issues` (`rating.py:617`) runs once per purpose graph: *(refreshed 2026-10-11)* the base graph with unconditional mounts
    only, then one per selected purpose with its purpose mounts added. Reuse Slice 2's
    mount-as-node code for every pass; never copy it.
- [ ] **Step 4:** the contract (`contract-schema`), `generate-contracts.py --check`, and
  `backend/tests/test_contracts.py`.
- [ ] **Step 5: Run Step 2's command; it passes.**
- [ ] **Step 6: Commit:** `feat(model-schema): SubGraphRef.purposes and FR-212 per purpose (FR-218, RL-1344)`.

### Task 3: The bundle per purpose — `inline_mounts`, `compile_bundle`, `bundle_hash`, `load_bundle`

**Files:** `inline.py`, `compile.py`, `runtime.py` (Slice 2's names). Tests:
`test_rating_inline.py`, `test_rating_compile_bundle.py`, `test_rating_runtime.py` (appended).

- [ ] **Step 1: Write the failing tests** (acceptance 6 and 7; DP-S3-1 and DP-S3-2 as ruled):
  - `inline_mounts(..., purpose=None)` inlines unconditional mounts only;
  - `purpose="cancellation"` adds the cancellation mounts, whose re-producing step reads the parent's value and re-produces it (RL-1628, DP-S3-1 (d)); *(refreshed 2026-10-11, RL-1628 P3)*
  - `compile_bundle` emits `purpose_graphs` for exactly the selected purposes;
  - the hash changes when only `purposes` changes, and is unchanged for a version with no purpose
    mount;
  - `load_bundle` gives one decision, algorithm and `model_call` handler per purpose graph, and refuses with `BUNDLE_COMPILE_FAILED` when a purpose graph's node ids differ from its re-inlined algorithm's (RL-1628, DP-S3-2 conditions 1 and 2). *(refreshed 2026-10-11, RL-1628 P4)*
- [ ] **Step 2: Run them; they fail by cause.** `purpose` is an unexpected keyword, and
  `purpose_graphs` is missing.
- [ ] **Step 3: Implement**, under DP-S3-2 (a):
  - `inline_mounts` gains `purpose: str | None = None`. One function, with the default behaving as
    Slice 2's.
  - `compile_bundle` runs Slice 2's structure checks on **every** purpose's inlined algorithm,
    not only the base one, so a fragment refused for one purpose is refused at compile.
  - `bundle_hash` covers `purpose_graphs` only when it is non-empty.
  - `CompiledBundle` holds the per-purpose decision, algorithm and handler; boosters stay shared (RL-1628, condition 1). *(refreshed 2026-10-11, RL-1628 P4)*
- [ ] **Step 4: Run** the four `pricing-core` test files named above, then
  `test_quote_input_raise_sites.py`. All pass, and the existing ones are unmodified.
- [ ] **Step 5: Commit:** `feat(pricing-core): per-purpose graphs in the bundle (FR-218, RL-1344 §3)`.

### Task 4: The real check and the purpose's decision in scoring

**Files:** `score.py` (`_check_purpose_mount` `:391-421`, calls `:941` and `:1108`; `score_one`
`:919`; `_score_context_sync` `:1090`; `build_scoring_result` `:873`; `_score_batch_row` `:1128`).
Tests: `test_rating_score.py` (`:477-543` and `:1016-1047` rewritten per acceptance 8; new tests
appended); `backend/tests/test_score.py` for the routes. *(refreshed 2026-10-11)*

- [ ] **Step 1: Rewrite and write the tests** (acceptance 4, 5 and 8). Use `_compiled` (`:160`)
  and `_ctx` (`:168`). *(refreshed 2026-10-11)* Mirror `backend/tests/test_score.py` for `/score` and `/score/compare`.
- [ ] **Step 2: Run them.** Expected: the cancellation quote is refused with the **"interim"**
  message (premise a). That is the cause; any other is a plan defect.
- [ ] **Step 3: Implement.**
  - `_check_purpose_mount(bundle, ctx)` refuses `mid_term_adjustment` and `cancellation` with
    `INPUT_CONTRACT_VIOLATION` unless `ctx.purpose` has a purpose graph in the bundle. The message
    names the purpose and says no mount for it is inlined. The docstring says this is the real
    check and cites `RL-1344` §3. It keeps one raise site.
  - `score_one` and `_score_context_sync` evaluate the purpose's decision when one exists, and the
    base decision otherwise. One selector returns the purpose's decision and algorithm, and every read of `bundle.algorithm` or `bundle.decision` in `build_scoring_result`, `score_one`, `_score_context_sync` and the batch row path goes through it: lookup misses, constraints, ladder inputs, outputs and the trace all use the algorithm that was evaluated (RL-1628, condition 1). Red first: a clamping `constraint` inside a cancellation mount appears in the cancellation quote's ladder. *(refreshed 2026-10-11, RL-1628 P5)*
- [ ] **Step 4: The broken-input proof** (acceptance 5). This is a local edit, never committed.
- [ ] **Step 5: Run** `uv run pytest packages/pricing-core/tests/test_rating_score.py backend/tests/test_score.py -q`.
- [ ] **Step 6: Commit:** `feat(pricing-core): FR-218's real purpose check replaces the interim refusal (RL-1344, RL-1242)`.

### Task 5: The final commit — FR-218's strike and `RL-1242`'s retirement

- [ ] FR-218's strike (Task 1, first bullet) and `RL-1242`'s `status: retired`, written by this
  slice's executor as RL-1628 names (acceptance 9); the commit message cites RL-1628. Nothing else
  is edited in `RL-1242`. *(refreshed 2026-10-11)*
- [ ] `python3 scripts/doc-index.py`, then `python3 scripts/audit-docs.py`.
- [ ] Commit: `docs(specs,rulings): FR-218's interim rule struck; RL-1242 retired (RL-1242:83-85)`.

### Task 6: The gate and the ledger

- [ ] Run the full two-half gate under the single gate. Quote every rc, the `N passed` line and
  `HEAD`.
- [ ] The ledger records:
  - the tree and the premises;
  - the red-first quotes;
  - `RL-1344` and RL-1628's minted id; *(refreshed 2026-10-11)*
  - the deleted bogus-reference test, and the Slice 2 test that covers it;
  - FR-218's verdict (acceptance 10).
- [ ] The MERGE-ACK.

## Self-review

1. **Against `RL-1344`:**
   - §2 → Task 2 and acceptance 2;
   - §3 → DP-S3-1, DP-S3-2, Tasks 3–4 and acceptance 3–4;
   - §4's Slice 3 bullet → Tasks 1–5;
   - the five *Acceptance* cases → acceptance 2, 4, 6, 3 and 7, in that order;
   - the open question → DP-S3-1 and DP-S3-2, raised here as `RL-1344:180-181` requires.
2. **Against `PL-1254` Task 3** (`:314-339`):
   - the strike → Task 5;
   - the mount in `model-schema` → Task 2;
   - the scorer → Task 4;
   - `_check_purpose_mount` → Task 4;
   - the interim tests → acceptance 8;
   - the gate outline → acceptance 4 and 5;
   - the "dated retirement note" → acceptance 9, with the frozen-body reason stated.
3. **FR-218 read to its clauses** (`03:87`):
   - "same Rating Algorithm for the risk price" → acceptance 4, third bullet;
   - "mounted only when `purpose ∈ {mid_term_adjustment, cancellation}`" → acceptance 2 and 5;
   - "declared on the Rating Version and version-pinned" → acceptance 6;
   - "refuses … rather than pricing it as new business" → acceptance 4.
4. **Literals.** Each was first read at `cdaaa573` and re-read at `02f23b4a`. Slice 2's names
   (`inline_mounts`, `Pins.sub_graphs`, the port map) have landed (`PL-1572`). *(refreshed 2026-10-11)*
5. **Open:** nothing for the decision-maker. DP-S3-1 and DP-S3-2 are ruled by RL-1628 (DP-S3-1
   final at its ACK), and RL-1628 names acceptance 9's writer. *(refreshed 2026-10-11)*

## Pre-mint refresh, 2026-10-11

Written 2026-10-11 12:01 BST (by `date`) by the planner seat `planner-9609`, on the maintainer's
(by delegation) entry headed *"2026-10-11 11:21:02 BST — DP-F (WK-1250 S3 plan form): (a); DP-W-1
(a): confirmed; dm-wk690 seated: OK"* in `~/gi-pricing-plan.local/channel/to-lead.md`, item 1:
*"Refresh both forward to current main and mint them together, on the D5 precedent (PL 9610/RL
9586 → PL-1572/RL-1571)"*. Its three conditions, as applied:
- **The refresh base:** `origin/main` `02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a` (#1273, `SL-1600`).
  Every need, line cite and file:line in this plan was re-read there. The branch
  `pl-9609-refresh-2026-10-11` is cut forward from `pl-9609-wk1250-s3-leaf` and merges that main
  by content; nothing was rebased.
- **This section is the dated record of every change.** Each edited place carries
  "(refreshed 2026-10-11)"; nothing changed silently.
- **The ACK diff:** old draft tip `7c8736fd5c083fddf175d3a10a2e51b2cbcdc3d6`, refreshed tip = this
  branch's head (`git diff 7c8736fd..<head> -- docs/plans/PL-01629-*`).

**Not changed: what was decided, or the plan's scope.** The Goal, the requirement coverage, the
Global Constraints' rules, the task cut and the acceptance items stand. The DP table keeps the
question as raised; the ruling is RL-1628's, cited, not re-argued. Each premise a–h still holds at
`02f23b4a`: the guard still refuses both purposes with "interim"; `SubGraphRef` still has no
`purposes`; `Bundle` still has one graph; `CompiledBundle` still holds one decision.

**Changed:**
1. **Header.** `tree:` moves to `02f23b4a` (first written at `cdaaa573`). `relates:` gains
   `PL-1572`, `RL-1571`, `RL-1519`, `RL-1445`, `SL-1436` and `PL-1546`. RL-1628 stays out of
   `relates:` until it is minted (check 32). `status:` stays `draft`; it goes `active` at the mint,
   after RL-1628's.
2. **Minted ids for working ids:** PL 9610 → `PL-1572`; RL 9620 → `RL-1445` (item 1, `:127-128`;
   item 2 (b), `:139-141`); PL 9629 → `PL-1544` (via `PL-1572:64`); PL 9776 → `PL-1520`.
3. **Every locator re-read at `02f23b4a`:** the Goal, the premises table (a–h), the File contention
   table, acceptance 8, Global Constraints' error-code lines, Tasks 1, 2 and 4. Premise moves:
   `_check_purpose_mount` `:395-422` → `:391-421`; its calls `:898`/`:1063` → `:941`/`:1108`;
   `QuotePurpose` `:44` → `:45`; `SubGraphRef` `:342-352` → `:445`; `Bundle` `:505` → `:632`;
   `bundle_hash` `:522-535` → `:661`; `CompiledBundle` `:625-643` → `:941`; the interim tests
   `:438-507` → `:477-543`; `_compiled`/`_ctx` `:137`/`:143` → `:160`/`:168`; `03` §4.11 `:822` →
   `:919`; §5.2 `:1028` → `:1139`; `errors.py` `:309`/`:355` → `:311`/`:367`. Unchanged and
   re-verified: `03:87`; `RL-1242:83-85`; `RL-1344:177-181`; `PL-1254:314-339`, `:328-330`,
   `:331`; `PL-1371:218`, `:291-294`, `:305`, `:387-388`; `RL-1263:89`, `:113`;
   `test_quote_input_raise_sites.py:63`.
4. **RL-1628's texts for PL-1629, P1 to P5, applied verbatim** (RL-1628 at
   `origin/dm-9573-refresh-2026-10-11` `ad05af54`, §"The texts for PL-1629"). Each find string had
   exactly one hit at `7c8736fd`, and none moved. P1 → acceptance 3; P2 → Task 2 Step 1; P3 → Task
   3 Step 1; P4 → Task 3 Steps 1 and 3; P5 → Task 4 Step 3. Each carries "(refreshed 2026-10-11,
   RL-1628 Pn)".
5. **Aligned with RL-1628's refresh.** The DP lead-in, §Status and self-review item 5 cite RL-1628
   as the ruling (DP-S3-1 (d) with R1 and Limits 2–4, final at its ACK; DP-S3-2 (a) with its two
   conditions). Task 1 and acceptance 1 apply T1 to T3: §4.1 states the per-purpose rule (T1),
   **§4.11** shows `purposes` on a mount (T2, re-pointed there by RL-1628 because `RL-1519` left
   §4.1's example with no mount, `03:344-347`), and §5.2 carries the bundle per purpose (T3). Task
   1 also re-counts each anchor. Global Constraints records that RL-1628 names no new code.
   RL-1628's Limit 4 (the order, now delivered by `SL-1436`'s `_dependency_order` and the inliner's
   `_stable_topological`) adds no task: Slice 3 adds no ordering code.
6. **Acceptance 8 gains `PL-1572` Task 8's two interim-pinning tests** (planner-d11's drift list):
   `test_a_version_that_mounts_a_sub_graph_still_refuses_mta_and_cancellation` (`:1023`, asserting
   `"interim"` at `:1030`) and
   `test_an_unconditional_mount_prices_a_new_business_quote_with_the_fragment` (`:1036`). What
   each must become follows from DP-S3-2 (a) and acceptance 2, as written there; no new rule.
7. **Acceptance 9's writer** is named from RL-1628 (§"What it obliges", last bullet): Slice 3's
   executor flips `RL-1242`'s `status:` line only, in the final commit, citing RL-1628. Task 0,
   Task 5 and self-review item 5 follow.
8. **Serialisation.** After `SL-1600` (#1273), which edited `SubGraphRef`: **merged as
   `02f23b4a`**, the refresh base, so MET. With WK-675 S5 (`SL-1547`), named by definition
   (`to_jdm` against this slice's `compile_bundle`/`bundle_hash`), and **the hash-stability
   re-run**: whichever of the two merges second re-runs the other's existing-hash test (RL-1613,
   working id, item 2 (ii)) on its own tree; acceptance 7 now says so, and names the pinned
   `_SCORE_FIXTURE_HASH` tests.
9. **`SL-1600`'s rule on raises.** A new model-schema raise is an `InputFreeError` with a literal
   message (`test_input_free_raises.py` rules (i) and (ii)); Global Constraints and Task 2 Step 3
   say so. It still maps to `VALIDATION_FAILED`.
10. **Activation needs restated at `02f23b4a`:** 1 MET; 2 met at RL-1628's mint; 3, 5 and 6 open
    at the GO; 4 MET at planner-d11's `d699a561` sweep plus `SL-1600`'s merge, re-checked at the
    GO. **This refresh ran no branch sweep**: gate-1 was held throughout (the sweep-pause rule in
    `.claude/roles/planner.md`).

**Observed, not changed here:**
- `_check_purpose_mount`'s docstring (`score.py:392-410`) still says *"`compile_bundle` never reads
  `sub_graphs`"*, false since Slice 2. Task 4 Step 3 rewrites the docstring anyway.
- RL-1628's `model_schema/rating.py` locators were read at `d699a561`; at `02f23b4a` (after
  `SL-1600`) each is one line later (`SubGraphRef` `:444` → `:445`, `sub_graphs` `:540` → `:541`,
  `_graph_invariants` `:564` → `:565`, `graph_invariant_issues` `:616` → `:617`). A moved line
  only. It is the decision-maker's record, not this plan's.
