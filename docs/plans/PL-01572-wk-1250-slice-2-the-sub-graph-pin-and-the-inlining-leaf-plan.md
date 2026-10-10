---
id: PL-1572
family: plan
kind: leaf
title: WK-1250 Slice 2 — the sub-graph pin and the inlining (FR-217's pin and inlining limbs; FR-258's inlined steps): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-10            # original date 2026-10-05, set at the draft; minted 2026-10-10
owner: planner
tree: cdaaa57345cb765f96034ce1ec2733c338f1c3cd
phase: P2
work: WK-1250
slice: SL-1340
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1254, PL-1325, RL-1309, RL-1344, FD-1241, FD-1246, RL-1242, RL-1263, FD-1297, PL-1371, LG-1355, RL-1571]
---

# PL-1572 — WK-1250 Slice 2: the sub-graph pin and the inlining, leaf plan

*(Minted 2026-10-10 as PL-1572 from working id 9610, in the D5 batch mint PR with RL-1571 (from RL 9586); RL 9586's P1 to P5 were applied to this plan before the mint; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

Filed under working id 9610. It is the leaf plan for `SL-1340` (`draft`, minted 2026-09-30, in
[`../roadmap.md`](../roadmap.md) under `### WK-1250`), which is `PL-1254` Task 2. The lead
re-issued the id (`~/gi-pricing-plan.local/handover/eta.md`, row "PL 9610", "RE-ISSUED: WK-1250
S2 leaf plan on SL-1340", 5 Oct 15:34:40). The row is not edited here; its "leaf plan" note is
added at the mint. Everything below was read at `origin/main`
`cdaaa57345cb765f96034ce1ec2733c338f1c3cd` on 2026-10-05, unless a line names a branch. **No test
was run at planning time.** Every red below is predicted from the code that was read.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds:
> - `test-driven-development`: see every red fail by its stated cause before writing the code
>   that turns it green;
> - `spec-change` (Task 1);
> - `contract-schema` and `contract-guard` (Task 2: the hand-authored `rating-version` and
>   `rating-algorithm` contracts);
> - `python-package`: `pricing-core` stays standalone, and a shape is defined once, in
>   `model-schema`;
> - `python-test`: the `req` marker and negative tests;
> - `dev-commands`: the two-half gate, and `uv sync --all-packages` in a fresh worktree;
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

## Goal

Make a stored sub-graph **price**. A Rating Version pins the exact sub-graph version
(`Pins.sub_graphs`). The parent algorithm mounts it through an explicit **port map**.
`compile_bundle` then inlines the fragment at its mount point, with every internal name
namespaced, and runs the whole structure check over the inlined algorithm. The bundle hash
covers the pinned fragment, and a scored trace shows the inlined steps, attributed to their mount
point (FR-258).

This slice adds **no** `purposes` field. Every mount it inlines is unconditional, and `RL-1242`'s
interim refusal of MTA and cancellation quotes stays in force (`RL-1344` §4). FR-218's purpose
mount and the real check are Slice 3's (`SL-1341`, PL 9609, working id).

**What it unblocks for G2.** In PL-1544 (#1164, branch `pl-9629-p2-exit-demo` at
`c5f60f7b`), this slice is what step **B7** waits on: "mount `sub_graph:ncd-ladder@4` | inlined at
compile | DP-b3". B7 is a row of that plan's Task 2 ("Phases A and B over HTTP"). No other PL-1544
step needs WK-1250. Slice 3 serves no PL-1544 step.

**The consequence `RL-1344` §4 says this plan must state.** Between this slice's merge and Slice 3,
an author who mounts a refund fragment without a selector mounts it for **every** purpose. No
selector exists yet, so every mount is unconditional. The interim refusal still stops every MTA and
cancellation quote, so no such quote is priced. A `new_business` or `renewal` quote on a version that
mounts a refund fragment **is** priced with it. That is the author's mount, made visible in the
diff (acceptance 7), approved inside the pinning Rating Version (`RL-1309` DP-1 (b)), and shown in
the trace (acceptance 8).

## Status

The status is the `status:` field in the header, and nothing else. **It stays `draft` while
DP-S2-1 and DP-S2-2 below are open**; they are the decision-maker's (`document-ids.md` §1.6, PL
row). Activation is that field's flip only. Its facts (the date, the dispatch, the gate slot) are
recorded in the dispatch record and quoted in the ledger's Task 0, never added here.

**Activation needs, in order** (each with its state at `cdaaa573`):
1. **`SL-1339` closed.** **Met:** `closed` 2026-10-01 (`LG-1355`).
2. **DP-S2-1 and DP-S2-2 ruled by an `RL-`.** Open.
3. **The `TraceStep` ruling (FD-1246) minted.** `PL-1254:176` and `:301`, and `PL-1371:217`,
   make "the FD-1246 trace ruling" a dependency of this slice. **It existed, unminted, at `cdaaa573`:** RL 9771 (then a working id, minted since as RL-1519, 2026-10-08;
   #1060, branch `dm-f35-rulings` at `758336a1`, `status: draft`), DP-F35-2, *"Ruled
   (b): yes"*, input and output steps are traced. It says: *"`SL-1340`'s inlined ports are then
   traceable without a second ruling … `FD-1246`'s disposition, the decision-maker's ruling, is
   this paragraph. Its delivery is PL-1520 Task 3."* Nothing rules on FD-1246 on `main`
   (`git grep -n 'FD-1246' cdaaa573 -- docs/rulings` prints only `RL-1263`'s line, which states
   the dependency). **Open at `cdaaa573` until RL-1519 minted (it has, 2026-10-08).** The order against PL-1520, which delivers it,
   is **Sequencing for the lead** below.
4. **`RL-1309` DP-1 item 3's condition** (`RL-1309:309-310`): *"Before Slice 2 is dispatched, both
   WK-673's plan and PL-1254 Task 2 carry this limb."* The maintainer then ruled that **a local
   file does not satisfy it; an in-repo record must carry the limb verbatim, citing `RL-1309`**:
   WK-673's Slice 5 leaf plan, or a WK-673 slice ledger's Task 0, whichever lands first. That ruling
   is the entry in `~/gi-pricing-plan.local/channel/to-lead.md` headed "2026-09-30 14:47:19 BST —
   RL-1309:309-311's gate: NO, a local delta file doesn't satisfy it; an IN-REPO carrier is
   needed", as quoted at `PL-1325:861-866`. **Unmet at `cdaaa573`:** no WK-673 plan or ledger
   cites `RL-1309` (`git grep -l 'RL-1309' cdaaa573 -- docs/plans docs/ledgers` prints only
   `PL-1325` and `LG-1355`). None of the four open WK-673 leaf plans cites it either: PL-1452
   (#1138), PL-1419, PL-1403 and PL-1395, read at their branch heads `e810b785`, `33ea0052`,
   `d2d3244c` and `3359f585`. `PL-1254` is frozen, so for `PL-1254` Task 2 **this leaf plan
   carries the limb** (Task 4 and acceptance 7). Routing the WK-673 carrier is the lead's
   (`RL-1309:310`).
5. **The `compile_bundle` writers ahead of it have merged, one at a time.** `PL-1371:291-294`
   serialises WK-673 S3, WK-1250 S2, WK-1250 S3 and WK-675 S3 outright, on `compile.py` and
   `compile_bundle`. The lane-B fixes also edit `compile_bundle`'s body: PL-1471 (#1152, the FR-240
   family fix) and the FD-1420 fix (PL-1447, #1145). Each of them "never runs concurrently with a
   slice that edits `compile_bundle`'s body" (PL-1471's *Lane* item 4, at `2b5bf12d`). **PL-1471
   should merge first** (Task 0 and **Dependencies**).
6. **A free build slot and the single gate**, under the dispatch rule in force: `RL-1263`, as
   amended by RL-1445 (#1162, branch `dm-9620-rl1263-amend`, not merged), *"Build
   slices: at most 3 at once. At most ONE full gate runs at a time on this VM."*
7. **The lead's dispatch record**, carrying the write-set check (**File contention**) and
   `RL-1344`'s §4 bullet for Slice 2 verbatim: *"The inliner must not foreclose §3's per-purpose
   gating: a mount is inlined as a namespaced unit (DP-3), so Slice 3 can gate it as one unit"*
   (`RL-1344:177-179`).

### Dependencies

- **On Slice 1 (`SL-1339`, closed).** This slice consumes:
  - `SubGraph`, `SubGraphInputPort` and `SubGraphBody` (`model_schema/sub_graphs.py:31-164`);
  - `resolve_ref` (`backend/src/app/platform/sub_graphs.py:202-213`, whose docstring says "Not
    wired into compile (Slice 2)");
  - `fragment_output_type_issues` (`compile.py:173-199`);
  - the `sub_graph_versions` table (`SubGraphVersionRow`, `backend/src/app/db/models.py:2384`).
- **On PL-1471 (the FR-240 family fix, #1152, `draft` at `2b5bf12d`).** PL-1471 builds the
  transitive model → custom-objective compile check, `_check_reachable_objectives(version,
  payloads, resolver)` (PL-1471 Task 2, Step 4). `RL-1309` G1 (`:350-361`) says:
  - *"Whichever Work lands the transitive model → objective compile check first builds it"*;
  - *"One implementation, never a copy. The second Work calls the first Work's function"*.
  `RL-1309` expected WK-1250 Slice 2 to be first. At this tree, PL-1471 is ordered ahead of it in
  lane B: FD-1420 fix → PL-1471 → PL-1454 (`to-lead.md` entry headed "2026-10-05 15:33:14 BST").
  `PL-1371:305` places this slice in the week of 24–30 Oct. **So this slice calls PL-1471's
  function, and never builds a second one.** If PL-1471 has not merged at dispatch, Task 0 stops and
  reports, and the lead orders the two. This plan does not choose the builder.
- **On the FD-1421 fix (PL-1429, #1140, at `f18549bb`).** PL-1429 gives `POST
  /api/v1/rating-versions` an `algorithm_ref` and `pins` (its *Architecture*,
  `RatingVersionCreate` in `model_schema/rating.py`). That is the first pin write path in
  `backend/src`. G2 (Task 6) is proved over **every** pin write path at the dispatch tree,
  whichever exist then.
- **WK-673's diff persistence ("whichever lands second").** If WK-673's slice that persists
  `structural_diff` has merged, this slice's diff test asserts the limb **in the persisted
  evidence** (`RL-1309:303-308`). If not, WK-673 carries the re-point case (Task 4).
- **No WK-674 dependency.** `RL-1263` item 5 lifts "after WK-674" as bare sequencing (roadmap
  `### WK-1250`, the 2026-09-30 amendment).

### File contention (`RL-1263` option (c), as amended by RL-1445)

`RL-1263:89`: *"Two concurrent build slices may not both change the same **existing** function,
class, method, spec section, or policy table."* The registry-exempt paths are `RL-1263:90-100` and
the corrections at `:108-115`. Hand-authored contracts **are not** exempt (`:113`). RL-1445 adds,
for two slices of one Work: *"(b) No plan dependency, either way … Otherwise the two slices
serialise"* (RL-1445 `:130-142` on its branch). Slice 3 depends on this slice, so **the two never
run together**.

| This slice's path | What it does there | Also changed by (in flight at `cdaaa573`) | Under option (c) |
|---|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/compile.py` | `compile_bundle` (`:573-643`): G1, mount resolution, the inlined validation, `all_refs`; `_MATURITY_CHECK_EXEMPT` (`:431`) | PL-1471 (#1152; `compile_bundle` and `ResolvedArtifact` `:434`); the FD-1420 fix (PL-1447, #1145); WK-673 S3 (PL-1452, #1138: called, not edited, at its `:386-387`); WK-675 S3 (no leaf plan); **PL-1520** (#1051) appends `_check_declared_reads` to `ALGORITHM_CHECKS` and its import block (its `:534`) | **Serialised outright** (`PL-1371:291-294`); PL-1520's append is in a different definition, and the dispatch record names it |
| `packages/pricing-core/src/pricing_core/rating/inline.py` | **new**: the pure inliner (Task 3) | none | Not shared |
| `packages/pricing-core/src/pricing_core/rating/vocabulary.py` | the shared tokenizer helper the inliner renames with (RL-1571) | the dispatch record checks in-flight plans for `vocabulary.py` | An existing-module edit. The dispatch record names it |
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | `load_bundle` (`:646`): it inlines with the same function (DP-S2-1) | **PL-1520** (#1051) edits `load_bundle` and `CompiledBundle`; the FD-1420 fix (PL-1447) edits `_decision_table_node`; PL-1452 calls it and does not edit it | **Serialises with PL-1520**: the same function. With PL-1447 it is a different definition, so the dispatch record names it |
| `packages/model-schema/src/model_schema/rating.py` | `Pins` (`:65-78`) gains `sub_graphs`; `SubGraphRef` (`:342-352`) gains the port map; `RatingAlgorithm._graph_invariants` (`:394`) sees a mount as a node; `AlgorithmDiff` (`:541`) and `diff_algorithms` (`:571`) gain the sub-graph limb | **PL-1452** edits `AlgorithmDiff` and `diff_algorithms` (its DP-S3-2 (a)). **PL-1476** (WK-675 S2, #1131) moves `RatingAlgorithm`'s fields to a new `RatingAlgorithmDraft` (its write-set row for `rating.py:375`). PL-1429 adds `RatingVersionCreate` | **Serialises** with PL-1452 and PL-1476: the same existing classes. The second to merge re-derives these edits on the first's names (Task 0) |
| `docs/specs/03-rating-engine.md` §4.1, §4.3, §4.11 and §5.2 | Task 1 | any slice editing those sections | **Serialises** (`RL-1263:89`), unless the dispatch record names the path with the check that no definition is edited by both |
| `docs/contracts/schemas/rating-version.schema.json`, `rating-algorithm.schema.json` | hand-authored; `pins.sub_graphs` and the mount's port map (Task 2) | PL-1429 (`rating-version`), PL-1476 (`rating-algorithm`) if they edit them | **Not exempt** (`RL-1263:113`); serialises |
| `backend/src/app/platform/rating_versions.py` | `_Resolver` (`:445`) gains a `sub_graph` branch before the `NOT_FOUND` fall-through (`:550-555`) | PL-1429 (the create path), PL-1471 | An existing-class edit. The dispatch record names it |
| `backend/tests/test_rating_version_compile.py`, `packages/pricing-core/tests/test_rating_compile_bundle.py`, `test_rating_runtime.py`, `test_rating_score.py`, `packages/model-schema/tests/test_rating_algorithm.py` | appended tests only | any slice adding tests there | Appended only; no existing test is edited (acceptance 10) |
| `docs/INDEX.md`, `docs/contracts/schemas/generated/`, `docs/contracts/openapi/generated.json` | regenerated | any | **Exempt**, never hand-merged |

**Not in this slice's set:** `score.py` (Slice 3 edits `_check_purpose_mount`), `TraceStep` and
`model_schema/scoring.py` (RL-1519's, delivered by PL-1520), the sub-graph routes (`backend/src/app/api/sub_graphs.py`),
any `approvals.py`, `errors.py` (no new code: DP-S2-2), `conftest*.py`, `pyproject.toml` and
`uv.lock`.

**FD-1366's residue (`PL-1371:258`, row 9, "sized at WK-1250 S2's leaf").** This slice does not
edit the two sub-graph routes (`sub_graphs.py:45`, `:60`, both `body: dict[str, Any]`). They stay in
WK-1178 item 9's residue (`PL-1371:409-411`), which this sizes at **0** for this slice.

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means the
failing run is quoted in the ledger, with its failing assert line **and the cause the step
predicts**. A failure for any other cause, including the right status or code for a different
reason, is a plan defect. The executor reports it and does not work around it. Every new test carries
`@pytest.mark.req("FR-217")`. The trace tests also carry `FR-258`, and the G-guard tests also carry
`FR-20` or `FR-237` where the guard is about the pin.

1. **Spec first** (Task 1).
   - `03` §4.1 shows a mount with its port map, and its invariants treat a mount as a node
     (`RL-1309` DP-3 items 2–4).
   - `03` §4.3's `pins` example has `sub_graphs`, and its FR-20 invariant is restated **by class**
     with `RL-1309`'s text verbatim (DP-1 item 5).
   - `03` §4.11's Slice note says what landed. `03` §5.2's `compile_bundle` contract says it
     inlines each pinned mount.
   - FR-217, FR-218 and FR-258 are **not** reworded. If the executor believes one needs a change,
     it stops and reports.
   - `python3 scripts/audit-docs.py` exits 0.
2. **Contracts.**
   - `uv run python scripts/generate-contracts.py --check` exits 0.
   - The hand-authored `docs/contracts/schemas/rating-version.schema.json` has a
     `pins.sub_graphs` array of artifact references. `rating-algorithm.schema.json`'s
     `sub_graphs` items carry the port map (DP-S2-2).
   - The `contract-guard` comparisons in `backend/tests/test_contracts.py` pass.
3. **Save-time invariants see the mount** (`RL-1309` DP-3 item 4; its *Acceptance*, Slice 2,
   first bullet). Red first, in `packages/model-schema/tests/test_rating_algorithm.py`:
   - a parent that consumes a name only an **unmapped** port would produce is refused with
     `GraphUnresolvedRefError`, which the route maps to `RATING_GRAPH_UNRESOLVED_REF`;
   - a parent that consumes a **mapped** output is accepted;
   - a mount that consumes a parent value which no step produces is refused, by the same cause;
   - a `mount_point` equal to a parent `step_id` or to another mount's `mount_point` is refused
     (DP-3 item 2), with the code DP-S2-2 rules.
4. **Compile refusals, each red first and each by its cause** (`RL-1309` G1, DP-3 item 5, DP-4,
   DP-S1-4 item 6), in `packages/pricing-core/tests/test_rating_compile_bundle.py`, with the
   codes DP-S2-2 rules:
   - **G1:** a `SubGraphRef` whose version is not in `Pins.sub_graphs` is refused with
     `RATING_VERSION_UNPINNED`, and **the bundle contains none of its steps**;
   - **G1:** a fragment whose `table`, `lookup` or `model_call` reference is not among the Rating
     Version's pins is refused with `RATING_VERSION_UNPINNED`, naming the namespaced step;
   - **the port map against the pinned version's ports:** a mapped port the version does not
     declare; an input port left unmapped; an input port fed by a parent value of an
     incompatible result type;
   - **DP-4:** a pinned payload that carries `sub_graphs` (a nested mount reaching compile by
     another path) is refused by cause;
   - **DP-S1-4 item 6:** a fragment with a non-deterministic expression, saved at create, is
     refused when a mounting algorithm is compiled. The same holds for the other three checks
     (FR-274, FR-275, FR-276), one case each;
   - **a namespacing collision:** a parent name equal to a namespaced fragment name is refused,
     never silently merged (DP-S2-2).
5. **Inlining is correct and isolated** (`RL-1309` DP-3 item 3; its *Acceptance*, Slice 2, second
   bullet). Red first:
   - **the deliberate clash:** a fragment's internal name equal to a parent name. After inlining
     and scoring, the parent value is unchanged, and the fragment's value appears under the
     namespaced name;
   - a version that mounts `ncd-ladder` scores the fragment's output into the mapped parent name,
     through `pricing-core` (`compile_bundle` → `load_bundle` → `score_one`);
   - **a version that pins no sub-graph compiles and scores exactly as today:** the existing
     compile, bundle, runtime and score suites pass **unmodified**, and the bundle hash of each
     existing fixture is unchanged (`bundle_hash` over a graph and pins with no sub-graph).
6. **The hash** (`PL-1254` Task 2's gate outline):
   - change only a pinned sub-graph's version (the mount's `ref` and the pin move together), and
     `content_hash` changes;
   - recompile the same pins, and `content_hash` is identical;
   - with `Pins.sub_graphs` removed from what `bundle_hash` reads, the first assertion fails.
7. **The diff limb** (`RL-1309` DP-1 item 3; its *Acceptance*, Slice 2, fourth bullet). Red
   first, in `test_rating_algorithm.py`. `diff_algorithms` over two algorithms that differ only
   in a sub-graph mount names the re-point (mount point, before and after refs) **and the inner
   step changes**. With the limb removed, the test fails. **If WK-673's persistence slice has
   merged at this tree**, a second test asserts the limb in the **persisted** `structural_diff`
   evidence of a Rating Version whose only change is a sub-graph re-point (`RL-1309:651-653`).
   The ledger records which case held.
8. **The trace (FR-258)**, in the order the lead sets with PL-1520 (**Sequencing for the lead**). Red first, in `test_rating_score.py`. A traced
   `score_one` on a version that mounts a fragment returns one `TraceStep` per inlined step. Each
   one's `step_id` is the namespaced id (`<mount_point>` + separator + fragment `step_id`), so it
   is attributable to its mount. Real-time and batch carry the same structure (FR-258's last
   sentence), and a batch trace test mirrors the existing one.
9. **The guards** (`RL-1309` DP-1 items 5 and 6), red first on broken input:
   - **G1, the objective clause:** an unapproved custom objective planted inside a pinned
     sub-graph, reached through that fragment's `model_call`, is refused at compile. The refusal
     comes from **PL-1471's** `_check_reachable_objectives` (or its name at the dispatch tree),
     **called, not copied**: `git grep -c 'def _check_reachable_objectives'` over
     `packages/pricing-core/src` prints exactly 1. With the call removed locally, the planted
     objective compiles and the test fails. That edit is never committed;
   - **G2:** every pin write path in `backend/src` at the dispatch tree is enumerated by
     `git grep -nE '\.pins\s*=[^=]|pins=' -- backend/src` and listed in the ledger. Each path that
     can reach an existing row refuses a pin change unless the row is `draft`, red first. A
     tripwire test fails when a new writer appears outside the enumerated set;
   - **G4 (a) and (b):** `Pins.sub_graphs` is in `all_refs`. With `sub_graph` removed from
     `_MATURITY_CHECK_EXEMPT`, a sub-graph pin is refused with `PIN_NOT_APPROVED`, in the form of
     `test_the_algorithm_maturity_check_would_be_caught_if_removed`
     (`packages/pricing-core/tests/test_rating_compile_bundle.py:213`);
   - **G4 (c):** a tripwire, in the form of `test_rate_table_version_row_has_no_status_column`
     (`backend/tests/test_rating_version_compile.py:248`), fails the day a `status` column is
     added to `sub_graph_versions`, and names `RL-1309`.
10. **Nothing else changes.** `git diff origin/main...HEAD` shows no removed or changed line in an
    existing test. The raise-site count in `packages/pricing-core/tests/test_quote_input_raise_sites.py`
    (`_INPUT_FREE`, `("rating/compile.py", "compile_bundle"): 5` at `:79`) is updated only if
    `compile_bundle`'s own raise count changes, and the ledger says why.
11. **Through the backend:** `POST /api/v1/rating-versions/{id}/compile` on a version that mounts a
    stored sub-graph returns 202, and the `rating.compile` Job succeeds. The same request with the
    pin missing makes the Job fail with `RATING_VERSION_UNPINNED`. This needs the FD-1421 fix's
    pin write path, or a test row built directly, as the existing compile tests do. The executor
    mirrors `backend/tests/test_rating_version_compile.py`'s fixtures and does not invent new ones.
12. **Coverage and verdicts.** `uv run python scripts/req-coverage.py` lists the new tests against
    FR-217 and FR-258. The ledger records **FR-217: all three limbs delivered** (artifact
    `SL-1339`; pin and inlining here). **FD-1241's FR-217 limbs are the auditor's to close at this
    slice's close** (`PL-1254:312`). Whoever ends up building the transitive objective check
    records its symbol and file in the ledger (`RL-1309:360`).
13. **The gate.** The full two-half gate (`CLAUDE.md` §11) exits 0 on the committed tree, under the
    single gate (RL-1445). The ledger quotes every rc, the `N passed` line and `HEAD`, and compares
    `N passed` with `origin/main`'s.
14. **MERGE-ACK.** Before the lead merges, the maintainer's MERGE-ACK naming the PR's full head SHA
    is recorded in `~/gi-pricing-plan.local/channel/to-lead.md`. It is never posted on the PR. The
    slice's clean audit is filed. A Slice closes on a clean audit and the lead's merge (`CLAUDE.md`
    §13).

## Global Constraints

- **Spec first** (`CLAUDE.md` §0): Task 1 lands before any code.
- **No hand-written shape that `model-schema` owns** (`CLAUDE.md` §2). `Pins.sub_graphs`, the port
  map and the diff limb are declared once, in `model-schema`.
- **`pricing-core` stays standalone** (`.importlinter`). The inliner is pure: no I/O, no database,
  no FastAPI.
- **One inliner, called by both `compile_bundle` and `load_bundle`** (DP-S2-1), never a copy.
- **Depth 1** (`RL-1309` DP-4). The compiler refuses a nested mount again, by cause.
- **Money stays integer minor units or `Decimal`** (`00` §2; `CLAUDE.md` §7). The inliner moves
  steps and renames names; it computes nothing.
- **A version that pins no sub-graph compiles, hashes and scores exactly as today** (`PL-1254`
  Task 2, last scope bullet).
- **`RL-1242`'s interim refusal stays** (`RL-1344` §4). `score.py`'s `_check_purpose_mount`
  (`:395-422`) is not edited here.
- **Do not build ahead of the phase.** No designer view (WK-675 S9), no `purposes` selector
  (Slice 3), and no deploy guard (G3 is WK-674 Slice 2's, `RL-1309:378-392`).

## Scope

### Requirement coverage, each id individually

| Spec section | Id | This slice |
|---|---|---|
| `03` §3.1 | FR-217 | **The pin limb and the inlining limb.** The artifact limb was `SL-1339`'s |
| `03` §3.8 | FR-258 | **The inlined steps only**: each one in the trace, attributable to its mount point |
| `03` §3.1 | FR-212 | The parent's save-time invariants count a mount as a node (`RL-1309` DP-3 item 4) |
| `03` §3.1 | FR-216 | Determinism, run at compile on the inlined algorithm (DP-S1-4 item 6) |
| `03` §3.11 | FR-274 | Division guards, on the inlined algorithm at compile |
| `03` §3.11 | FR-275 | The scale cap, on the inlined algorithm at compile |
| `03` §3.11 | FR-276 | The vocabulary, on the inlined algorithm at compile |
| `03` §3.4 | FR-237 | G1: a mount and every fragment reference resolve only against the version's pins |
| `00` §3 | FR-20 | Restated by class; `sub_graph` joins the exemption (DP-1 item 5; G4) |

The section column follows `03`'s own headings at `cdaaa573`. Task 0 re-reads each id's row and
stops if one has moved.

**Not in this slice:**
- **Slice 3 (`SL-1341`):** `SubGraphRef.purposes`, FR-212 per purpose, the real check in
  `_check_purpose_mount`, and `RL-1242`'s retirement.
- **WK-673:** persisting `structural_diff` (`RL-1309` DP-1 item 3, second bullet).
- **WK-674 Slice 2:** G3.
- **WK-1178 (FD-1246):** any change to what a `TraceStep` records.
- **WK-675 S9:** the designer's sub-graph view.

### Premises, read at `cdaaa573`

| # | Premise | Evidence |
|---|---|---|
| a | `Pins` has four lists and no `sub_graphs` | `model_schema/rating.py:65-78`, `frozen=True, extra="forbid"` at `:73` |
| b | `SubGraphRef` is `ref` plus `mount_point` only | `rating.py:342-352` |
| c | `compile_bundle` never reads `sub_graphs` | `compile.py:573-643`; the only `sub_graph` mention in the file is the `SubGraphInputPort` import at `:44` |
| d | The maturity loop reads four pin lists, and `sub_graph` is not exempt | `all_refs` at `compile.py:618-623`; `_MATURITY_CHECK_EXEMPT = frozenset({"rate_table", "rating_algorithm"})` at `:431` |
| e | `bundle_hash` hashes the graph and the pins | `compile.py:522-535` |
| f | Step references are checked against the pins after validation, on the parent's steps | `check_step_refs_pinned` `compile.py:542-570`, called at `:615`, and again in `load_bundle` (`runtime.py:663`) |
| g | `load_bundle` rebuilds the algorithm from the **un-inlined** stored payload | `runtime.py:662`: `RatingAlgorithm.model_validate(bundle.resolved_payloads[bundle.algorithm_ref])` |
| h | The trace keeps only steps in `algorithm.steps` | `score.py:788` builds `step_meta` from `algorithm.steps`; `:792-794` skip any other engine node. So without g fixed, inlined steps would be **dropped** from the trace |
| i | The backend resolver has no `sub_graph` branch | `rating_versions.py:445-555`; any other type falls to `NOT_FOUND` at `:550-555` |
| j | Slice 1's resolver exists, unwired | `backend/src/app/platform/sub_graphs.py:202-213` |
| k | A `step_id` has no pattern | `RatingStepBase.step_id: str = Field(min_length=1)` (`rating.py:264`). So no separator is reserved today (DP-S2-2) |
| l | The diff covers steps, tables, the input contract and outputs, not mounts | `AlgorithmDiff` `rating.py:541-569`; `diff_algorithms` `:571`; tests at `packages/model-schema/tests/test_rating_algorithm.py:257`, `:285` |
| m | No backend path writes a Rating Version's pins at `cdaaa573` | `RatingVersionCreate` (`backend/src/app/api/models.py:271`) has no `pins`; `pins` is only read (`rating_versions.py:113`). The FD-1421 fix (PL-1429) adds the first writer |
| n | The `03` sites Task 1 edits | §4.1's mount example `03:283` and invariants `:286-288`; §4.3's `pins` example `:377-382` and invariants `:423-428`; §4.11's Slice note `:822`; §5.2's `compile_bundle` line `:1028` |

The executor re-reads each premise at its own tree. **It stops on any premise that no longer holds**
([`README.md`](README.md) convention 4), and it maps a, b and l to PL-1452's and PL-1476's names if
either has merged.

### Decision points

**Ruled, and binding here** (`RL-1309`'s *What it obliges*, `:607-612`, for "WK-1250 Slice 2"):
DP-1 items 3, 5 and 6 (G1, G2, G4), DP-3 items 3 to 5, DP-4 and DP-S1-4 item 6 — each is quoted
where it acts. `RL-1344` §4 rules what this slice does and does not carry for purposes.

**Open, for the decision-maker.** The plan stays `draft` until each has an `RL-`.

| DP | Question | Options | Recommendation | Blocking |
|---|---|---|---|---|
| **DP-S2-1** | Where does the **inlined** algorithm live, so that scoring, the engine's `model_call` boosters (`_load_boosters`, `_model_call_handler`, `runtime.py`) and the trace see the fragment's steps (premises g, h)? | (a) **Re-inline at load.** `resolved_payloads` already gets each pinned sub-graph's payload once `Pins.sub_graphs` joins `all_refs` (G4 (a); the loop writes `payloads[str(ref)]`, `compile.py:632`). `load_bundle` calls the **same** pure inliner as `compile_bundle`. `Bundle`'s shape is unchanged; (b) `Bundle` gains an `inlined_algorithm` field written at compile, and `load_bundle` reads it; (c) `compile_bundle` replaces the algorithm's entry in `resolved_payloads` with the inlined algorithm | **(a).** One function, two callers, so compile and load cannot disagree. No `Bundle` contract change. A bundle stored before this slice has no mounts, so re-inlining is the identity. (b) stores a second copy of what the payloads already determine, and the two can diverge. (c) makes `resolved_payloads[algorithm_ref]` stop being the artifact the ref names, which breaks the payload ↔ ref invariant `load_bundle`'s docstring relies on (RL-873) | Tasks 3 and 5 |
| **DP-S2-2** | The port map's shape, the namespace separator, and the codes for the new refusals | **Shape:** (a) `inputs: dict[str, str]` (port → parent value) and `outputs: dict[str, str]` (port → parent name) on `SubGraphRef`, both `extra="forbid"`; (b) a list of `{port, name}` pairs. **Completeness:** every input port mapped exactly once; output ports mapped as a subset, at least one. **Separator:** `/`, with a compile refusal on any collision between a namespaced name and a parent name (premise k: no separator is reserved). **Codes:** an unmapped or undeclared port → `RATING_GRAPH_UNRESOLVED_REF`; an incompatible input type → `RATING_TYPE_MISMATCH`; a sub-graph not pinned → `RATING_VERSION_UNPINNED`; a nested mount → `VALIDATION_FAILED`; a `mount_point` clash or a namespacing collision → `VALIDATION_FAILED` | **Shape (a)**, since a dict cannot map one port twice. **Separator `/`** and **the codes as listed**: each reuses a code that `backend/src/app/errors.py:309-355` already registers, so `errors.py` is not edited. A new code would add a second meaning for one defect. An unmapped output port is legal: the parent does not consume it, and acceptance 3 refuses a consumer | Tasks 1–4 |


**Sequencing for the lead, with PL-1520 (not a decision point).** PL-1520 (#1051, branch
`wk1178-f35-leaf-plan` at `ecbb82ab`, `draft`) delivers RL-1519. It edits `_build_trace`,
`CompiledBundle` and `load_bundle` (its write-set rows for `score.py` and `runtime.py`), and
`compile.py`'s `ALGORITHM_CHECKS` (its `:534`). Its contention row for `SL-1340` (its `:541`)
says: *"**serialise.** Recommended order: this slice first, so `SL-1340` builds on the ruled
content. The lead decides."*
- **(a) PL-1520 first** (its recommendation). Task 7 then asserts the inlined steps in RL-1519's
  ruled trace content.
- **(b) This slice first.** The inlined steps reach the trace under today's `TraceStep` with no
  change to it: `_build_trace` (`score.py:781-819`) emits one entry per algorithm step, and under
  DP-S2-1 (a) the inlined steps are algorithm steps whose namespaced `step_id` names the mount.
  PL-1520 then traces them under its ruling (RL-1519: *"traceable without a second ruling"*).
- **This plan recommends (a)**, unless G2's date needs PL-1544's B7 before PL-1520 can merge. In
  that case, (b). A port here is a **rename**, never a node: a fragment has no `input` or `output`
  steps (`03` §4.11). So the map's reason for the wait (*"DP-3 (a)'s ports make inlined input and
  output nodes likely"*, `PL-1254:171-177`) does not arise, and either order is safe. **The order is
  the lead's**, not this plan's.

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree, and `git branch --show-current` is the slice branch, cut
  from `main` **after** every `compile_bundle` writer ahead of it merged (activation need 5).
- [ ] `uv sync --all-packages` (`dev-commands`).
- [ ] Re-derive premises a–n at that tree, and record each result in the ledger.
- [ ] `gh pr list --state open`, then read anything that rules on FR-217, FR-258, sub-graphs,
  `Pins`, `diff_algorithms`, `03` §4 or §5.2, `compile.py`, `runtime.py` or `TraceStep`
  ([`README.md`](README.md) convention 4). Name the SHA read.
- [ ] Confirm the resolutions **by record id**: `RL-1309` for its items; the `RL-` for DP-S2-1 to
  DP-S2-2; RL-1519 for FD-1246. Stop if any differs from **Decision points**.
- [ ] **PL-1520.** Record whether it has merged. That decides which branch of Task 7 runs.
- [ ] **PL-1471.** Confirm it has merged, and record the symbol and file of the transitive
  objective check (`_check_reachable_objectives` in its plan). If it has not merged, stop and
  report. The lead orders the two, and this slice does not build a copy.
- [ ] **WK-673's persistence.** Record whether `structural_diff` persistence has merged. That
  decides acceptance 7's second test.
- [ ] **The in-repo carrier** (activation need 4). Quote the WK-673 record that carries `RL-1309`
  DP-1 item 3 verbatim, by path and line. If none exists, stop.
- [ ] Confirm the dispatch record's write-set check and its gate rule.
- [ ] **At the second merge**, if a contending slice merges first: merge `origin/main` in,
  regenerate `docs/contracts/` and `docs/INDEX.md` (never hand-merged), re-derive the edits on
  any renamed class, and re-run Task 9's gate.

### Task 1: Spec — `03` §4.1, §4.3, §4.11 and §5.2

**Files:** `docs/specs/03-rating-engine.md`. Also `docs/specs/00-overview.md` §2, but only if a new
term is used (grep first; `spec-change`).

- [ ] **§4.1, the mount** (`03:283`). The example becomes
  `{"ref": "sub_graph:ncd-ladder@4", "mount_point": "m_ncd", "inputs": {"ncd_years": "ncd_years"}, "outputs": {"ncd_factor": "ncd_factor"}}`
  in DP-S2-2's ruled shape. The port names are `ncd-ladder`'s at `03:830-831`. Rename the mount
  point from `s_ncd` to `m_ncd` only if DP-S2-2's collision rule needs it: the §4.11 example's
  step is also `s_ncd`. Record the choice in the ledger.
- [ ] **§4.1, the invariants** (`03:286-288`). Append, dated and citing `RL-1309` DP-3 items 2–4:
  - a mount is a node;
  - its mapped outputs are produced by it, and its mapped inputs are consumed by it;
  - acyclicity and "produced by exactly one upstream step" count it;
  - `mount_point` is unique among the parent's `step_id`s and its other mounts.
- [ ] **§4.3, the pins** (`03:377-382`). Add `"sub_graphs": ["sub_graph:ncd-ladder@4"]`.
- [ ] **§4.3, the invariants** (`03:423-428`). Restate FR-20's clause **by class**, verbatim from
  `RL-1309:321-324`: *"every pin to an artifact that has an approval lifecycle resolves to
  `approved` or better (FR-20); a pin to an artifact that has none (Rate Table Version, Rating
  Algorithm, Sub-graph Version) is governed by the pinning Rating Version's own approval."* Add a
  dated note citing `RL-1309` DP-1 item 5. The struck clause stays visible.
- [ ] **§4.11, the Slice note** (`03:822`). Append a dated line: the pin, the inlining and the
  port map landed in WK-1250 Slice 2 (this plan, PL-1572), and FR-218's purpose mount is
  still Slice 3's. Add one bullet on namespacing (DP-S2-2's separator), and one on what compile
  refuses (acceptance 4's list, with the codes).
- [ ] **§5.2** (`03:1028`). The `compile_bundle` line's comment says that it inlines each pinned
  mount (FR-217) and runs `validate_algorithm` over the inlined algorithm. Name the inliner's
  public function (Task 3) on its own line, in the form of the other §5.2 lines.
- [ ] `python3 scripts/audit-docs.py`. Expected: exit 0. A working-id gap (check 31) on this
  plan's own id does not apply to the spec commit, which cites no working id.
- [ ] Commit: `docs(specs): 03 §4 and §5.2 — the sub-graph pin, the port map and the inlining (FR-217, RL-1309)`.

### Task 2: `model-schema` — `Pins.sub_graphs`, the port map, the mount as a node, and the contracts

**Files:**
- Modify: `packages/model-schema/src/model_schema/rating.py` (`Pins` `:65-78`; `SubGraphRef`
  `:342-352`; `RatingAlgorithm._graph_invariants` `:394-477`)
- Modify: `docs/contracts/schemas/rating-version.schema.json` (`pins`, `:12-21`) and
  `docs/contracts/schemas/rating-algorithm.schema.json` (`sub_graphs` items, `:89-94`)
- Test: `packages/model-schema/tests/test_rating_algorithm.py` (appended)

**Interfaces:**
- Produces: `Pins.sub_graphs: list[ArtifactRef]`, defaulting to an empty list so every stored
  `Pins` still validates. Also `SubGraphRef.inputs: dict[str, str]` and
  `SubGraphRef.outputs: dict[str, str]`, in DP-S2-2's ruled shape.

- [ ] **Step 1: Write the failing tests** (acceptance 3). Mirror the neighbouring tests'
  algorithm builders in `test_rating_algorithm.py`; do not invent a fixture. Cases:
  - a consumer of an unmapped port's name is refused with `GraphUnresolvedRefError`
    (`model_schema/graph_errors.py`), naming the name;
  - a consumer of a mapped output is accepted;
  - a mount whose mapped input names an undefined parent value is refused, by the same cause;
  - a `mount_point` equal to a `step_id`, or two mounts sharing one, are refused;
  - `Pins()` validates with `sub_graphs == []`, and `Pins.model_validate` of a stored four-list
    dict still validates.
- [ ] **Step 2: Run them; they fail.** `uv run pytest packages/model-schema/tests/test_rating_algorithm.py -q -k mount`.
  Expected: each fails **by its own cause**. A mapped consumer is refused today as an undefined
  value, at `rating.py:418-421`; a port-map field is refused by `extra="forbid"`. A failure for
  any other reason is a plan defect.
- [ ] **Step 3: Implement.**
  - Add `sub_graphs` to `Pins`.
  - Add the port maps to `SubGraphRef`.
  - In `_graph_invariants`, treat each mount as a pseudo-step: id `mount_point`, `consumes` the
    mapped input parent values, `produces` the mapped output parent names. Feed it to the
    existing `_produced_by`, `_consumed_by`, the cycle check and the reachability check. **Do not
    copy those helpers.** Check `mount_point` uniqueness beside the FR-215 uniqueness check
    (`:396-399`).
- [ ] **Step 4:** Update the two hand-authored contracts, with an example each (`contract-schema`).
  Run `uv run pytest backend/tests/test_contracts.py -q` and
  `uv run python scripts/generate-contracts.py --check`.
- [ ] **Step 5: Run Step 2's command; it passes.** The whole of `test_rating_algorithm.py` passes
  unmodified.
- [ ] **Step 6: Commit:** `feat(model-schema): Pins.sub_graphs and the mount's port map (FR-217, RL-1309 DP-3)`.

### Task 3: `pricing-core` — the inliner

**Files:**
- Create: `packages/pricing-core/src/pricing_core/rating/inline.py`
- Test: `packages/pricing-core/tests/test_rating_inline.py` (new)

**Interfaces:**
- Produces: `inline_mounts(algorithm: RatingAlgorithm, fragments: Mapping[str, SubGraph]) -> RatingAlgorithm`.
  `fragments` is keyed by `str(ArtifactRef)`, the key form `resolved_payloads` uses. The result
  has `sub_graphs == []`, and its steps in a stable topological order computed from the dependency edges: Kahn's algorithm with list order as the tie-break (the parent's steps, then each mount's namespaced steps), the rule the maintainer, by delegation, ruled for `to_wire` (RL-1571, P5). It is a proposal name, recorded in the ledger if it differs.
  A red test scores `03` §4.1's shape through `load_bundle` and asserts that the parent step consuming `ncd_factor` reads the fragment's value.

- [ ] **Step 1: Write the failing tests:**
  - **identity:** an algorithm with no mounts is returned equal to itself;
  - **namespacing:** every fragment `step_id`, and every name that is not a mapped port, becomes
    `f"{mount_point}__{name}"` (RL-1571, the separator `__`), renamed by FR-244 token in every name-bearing field, never by substring;
  - **ports:** a mapped input port's name is replaced by its parent value, and a mapped output
    port's name by its parent name;
  - **the deliberate clash:** a fragment internal name equal to a parent name stays namespaced,
    and the parent's producer is unchanged;
  - **a nested mount:** a fragment payload carrying `sub_graphs` → refused (`SubGraph`'s own
    `extra="forbid"`, re-raised by cause, DP-4);
  - **collisions:** a namespaced name equal to a parent name → refused (DP-S2-2);
  - **token renaming** (RL-1571): an internal name inside an `expr` is renamed and the expression passes `_check_division_guards`; with `ncd` and `ncd_years` both present, only the exact token `ncd` is renamed;
  - **port checks (names only):** an undeclared port, and an unmapped input port. The
    input-port **type** check is not here; it is Task 5's, in `compile.py`.
- [ ] **Step 2: Run** `uv run pytest packages/pricing-core/tests/test_rating_inline.py -q`.
  Expected: an `ImportError` on `inline_mounts`, and nothing else.
- [ ] **Step 3: Implement** the pure function, with no I/O. The result is constructed as a
  `RatingAlgorithm`, so the parent's `_graph_invariants` run over the inlined graph. Raise
  `CodedError(f"{code}: {message}")` from `pricing_core.safe_error`, the form `compile.py`'s
  `_raise_named` produces (`compile.py:48`, `:538`). The backend's code split
  (`rating_versions.py:559-566`) then maps each one. **`inline.py` imports nothing from
  `compile.py`**: `compile.py` imports `inline_mounts`, so a reverse import would be a cycle.
  That is why the type check lives in Task 5.
- [ ] **Step 4: Run Step 2's command; it passes.** Then run `uv run lint-imports`.
- [ ] **Step 5: Commit:** `feat(pricing-core): inline_mounts, the pure sub-graph inliner (FR-217, RL-1309 DP-3)`.

### Task 4: The diff limb

**Files:** `packages/model-schema/src/model_schema/rating.py` (`AlgorithmDiff` `:541`,
`diff_algorithms` `:571`). Test: `test_rating_algorithm.py` (appended).

**Interfaces:**
- Produces: `AlgorithmDiff.sub_graph_mounts: list[AlgorithmSubGraphChange]` (a proposal name).
  Each change carries `mount_point`, `before: ArtifactRef | None`, `after: ArtifactRef | None`,
  `ports_changed: bool` and `steps: AlgorithmDiff | None`, the inner step diff.
  `diff_algorithms(old, new, *, fragments: Mapping[str, SubGraph] | None = None)` fills `steps`
  when both versions' fragments are given. With no `fragments`, it still names the re-point.
  `summary` gains a "sub-graph(s) re-pointed" part.

- [ ] **Step 1: Write the failing test.** Two algorithms differ only in one mount's `ref` version,
  and the two fragments differ in one step's field. The diff names the mount point, both refs and
  the inner step change.
- [ ] **Step 2: Run it; it fails** on the missing attribute, not on any other assert.
- [ ] **Step 3: Implement.** Reuse `diff_algorithms` itself for the inner diff, by calling it on
  two fragment-shaped algorithms or on a shared step-diff helper extracted from it. Never write a
  second step-diff walk. The existing diff tests (`:257`, `:285`) pass unmodified.
- [ ] **Step 4: Broken-input proof.** With the limb's loop removed locally, the test fails. That
  edit is never committed.
- [ ] **Step 5 (only if WK-673's persistence has merged):** a backend test whose Rating Version's
  only change is a sub-graph re-point. It asserts the limb in the persisted `structural_diff`
  evidence blob. Mirror WK-673's own persistence test; do not invent its fixtures.
- [ ] **Step 6: Commit:** `feat(model-schema): the sub-graph limb of diff_algorithms (FR-219, RL-1309 DP-1 item 3)`.

### Task 5: `compile_bundle` and `load_bundle` inline

**Files:** `packages/pricing-core/src/pricing_core/rating/compile.py` (`compile_bundle`
`:573-643`; `_MATURITY_CHECK_EXEMPT` `:431`), `runtime.py` (`load_bundle` `:646`). Tests:
`test_rating_compile_bundle.py`, `test_rating_runtime.py` (appended).

- [ ] **Step 1: Write the failing tests** (acceptance 4, 5, 6 and 9's G4). Mirror `_version`
  (`test_rating_compile_bundle.py:69`) and `_resolver` (`:107`), extending the fake resolver with
  a `sub_graph` payload. Cases: every acceptance 4 bullet, one test each; the clash and the
  `ncd-ladder` score through `compile_bundle` → `load_bundle` → `score_one`; both hash
  assertions; G4 (a) and (b).
- [ ] **Step 2: Run them; they fail by cause.** Today a `sub_graphs` pin is refused by
  `extra="forbid"` until Task 2 lands. After Task 2, a mount is silently **not inlined**:
  `compile_bundle` never reads `sub_graphs` (premise c). The G1 test therefore fails on "the
  bundle contains a step" being false for the pinned case, not on a code.
- [ ] **Step 3: Implement**, in this order inside `compile_bundle`:
  1. after the algorithm's maturity check (`:603-608`), and **before** `validate_algorithm`:
     G1. Each `SubGraphRef.ref` must be in `version.pins.sub_graphs`, else
     `RATING_VERSION_UNPINNED`. Each mounted ref is resolved **once**, and that resolution is
     kept for the pin loop below;
  2. **the input-port type check**: for each mount, each mapped input port's declared type
     against the parent value's producer type, using `producer_types` (`compile.py:95`) and
     `_compatible` (`:124`), never a second type table, refused with `RATING_TYPE_MISMATCH`
     (DP-S2-2). It is a small new function beside `output_type_issues` (`:132`). Then
     `inline_mounts(algorithm, fragments)`, then `validate_algorithm`, `check_model_reference_mode`
     and `check_step_refs_pinned` on the **inlined** algorithm. That gives G1's fragment-reference
     half and DP-S1-4 item 6's four checks;
  3. `*version.pins.sub_graphs` joins `all_refs` (G4 (a)). The loop reuses step 1's resolutions
     instead of fetching twice (the same reason as the comment at `:598-602`);
  4. `sub_graph` joins `_MATURITY_CHECK_EXEMPT`, with a comment citing `RL-1309` DP-1 item 5, in
     the form of the comment block above `:431`;
  5. PL-1471's transitive objective check runs over the pins as it does at the dispatch tree. The
     fragment's `model_call` is pinned in `pins.models` (G1), so the check sees it. G1's
     objective-clause test (acceptance 9) proves it;
  6. `to_jdm(inlined)`.
  `bundle_hash(graph, pins)` is unchanged: the graph now contains the fragment, and the pins
  contain `sub_graphs`.
- [ ] **Step 4: `load_bundle`** (DP-S2-1 (a)): rebuild `fragments` from
  `bundle.resolved_payloads` for each `bundle.pins.sub_graphs` ref, then
  `algorithm = inline_mounts(algorithm, fragments)` **before** `check_step_refs_pinned` and
  `_load_boosters`. Then C1 (RL-1571): refuse with `BUNDLE_COMPILE_FAILED` when the set of `bundle.graph` node ids differs from the set of the inlined algorithm's `step_id`s, naming the first difference, before the engine is built; red first, on a bundle whose graph has one node renamed. Update its docstring.
- [ ] **Step 5: Run** `uv run pytest packages/pricing-core/tests/test_rating_compile_bundle.py packages/pricing-core/tests/test_rating_runtime.py packages/pricing-core/tests/test_rating_compile.py packages/pricing-core/tests/test_quote_input_raise_sites.py -q`.
  Expected: all pass, the existing tests unmodified (acceptance 10).
- [ ] **Step 6: Broken-input proofs**, each a local edit that is never committed: remove `sub_graph`
  from the exemption, and G4 (b) goes red; drop `pins.sub_graphs` from `all_refs`, and the hash
  test goes red; skip G1, and the unpinned-mount test goes red.
- [ ] **Step 7: Commit:** `feat(pricing-core): compile_bundle and load_bundle inline pinned sub-graphs (FR-217, RL-1309 G1, G4)`.

### Task 6: The backend — the resolver branch, G1's objective clause, G2 and G4 (c)

**Files:** `backend/src/app/platform/rating_versions.py` (`_Resolver` `:445`). Test:
`backend/tests/test_rating_version_compile.py` (appended).

- [ ] **Step 1: Write the failing tests:**
  - acceptance 11, through the compile route and the Job;
  - **G1's objective clause** (acceptance 9): a sub-graph whose `model_call` names a model whose
    custom objective is not approved. Mirror PL-1471's own objective test at the dispatch tree;
  - **G2** over each enumerated pin write path;
  - **G4 (c)**, the status-column tripwire on `SubGraphVersionRow`, in the form of
    `test_rate_table_version_row_has_no_status_column` (`:248`).
- [ ] **Step 2: Run them; they fail by cause.** The compile Job fails with `NOT_FOUND`, because
  `sub_graph` reaches the fall-through at `:550-555`.
- [ ] **Step 3: Implement** the `sub_graph` branch. It calls Slice 1's
  `sub_graphs.resolve_ref(session, workspace_id=…, ref=ref)` and returns
  `ResolvedArtifact(status="no_maturity_concept", payload=sub_graph.model_dump(mode="json"))`.
  That is the rate-table branch's sentinel and its reason (`:497-514`, RL-856): the exemption,
  not a constant, admits it. Also implement G2's refusal on every non-create writer, if one exists.
- [ ] **Step 4: Run** `uv run pytest backend/tests/test_rating_version_compile.py -q`; it passes.
- [ ] **Step 5: Commit:** `feat(backend): the compile resolver resolves sub-graph pins; G2 and G4 (c) (RL-1309)`.

### Task 7: The trace (FR-258) — in the lead's order with PL-1520

- [ ] **If PL-1520 has not merged (order (b)):** add tests only, in `packages/pricing-core/tests/test_rating_score.py`
  (appended), using `_compiled` (`:137`) and `_ctx` (`:143`). A traced `score_one` on a mounted
  version carries each inlined step with its namespaced `step_id`; a batch trace mirrors it. Red
  first: they fail before Task 5's `load_bundle` step, because `_build_trace` skips the inlined
  nodes (premise h). Quote that red in the ledger, from a checkout of Task 4's commit.
- [ ] **If PL-1520 has merged (order (a)):** the same tests, asserting the inlined steps in RL
  9771's ruled content: what each step reads and declares, under its namespaced `step_id`. Mirror
  PL-1520's own trace tests at the dispatch tree. **In either order, `TraceStep` and `_build_trace`
  are not edited here.**
- [ ] Commit: `test(pricing-core): inlined steps in the trace (FR-258)`.

### Task 8: `RL-1242` stays, stated

- [ ] Run the existing FR-218 interim tests (`test_rating_score.py:438-507`). They pass
  **unmodified**: a version that mounts a fragment still refuses an MTA or cancellation quote
  (`RL-1344` §4).
- [ ] Add one test: a version with an unconditional mount prices a `new_business` quote **with**
  the fragment. That is the consequence **Goal** states, pinned so that Slice 3 changes it on
  purpose. Commit with Task 7 or separately.

### Task 9: The gate and the ledger

- [ ] The full two-half gate under the single gate. Quote every rc, the `N passed` line and
  `HEAD`.
- [ ] The ledger records:
  - the tree and premises a–n;
  - every red-first quote;
  - `RL-1309` and the DP-S2 `RL-`;
  - `inline_mounts`' final name;
  - the transitive objective check's symbol and file (`RL-1309:360`);
  - the pin write paths G2 enumerated;
  - which case of acceptance 7 held;
  - FR-217's verdict (acceptance 12).
- [ ] The MERGE-ACK (acceptance 14).

## Hand-off

Slice 3 (`SL-1341`, PL 9609, working id) starts after this slice closes. It consumes:
- `SubGraphRef`'s port map, adding `purposes` beside it;
- `inline_mounts`. A mount is inlined as one namespaced unit, so Slice 3 can gate it by
  `purpose` as one unit (`RL-1344:177-179`);
- the Task 8 test, which Slice 3 changes on purpose.

`RL-1344` §3 leaves Slice 3 a decision point of its own: how a purpose mount's outputs reach the
ladder and the payable, and how the inlined nodes are gated by `purpose` at evaluation.

**Owed to PL 9521 (working id; #1202, the FD-1424 fix, WK-1178): the mounted red, and
`_compatible`.** *(Dated note, 2026-10-05, written 18:00:25 BST, pre-mint, by planner-a12fold
on the lead's order. From the maintainer's (by delegation) entry headed "2026-10-05 17:58:03 BST — PL 9521 @148892d6 and A-2 @176a6a75 noted; the mounted-case dependency (item 12 (c)) ACCEPTED, named in both plans",
verbatim:)*

> The A-control arithmetic was checked: 1234.4 × 1.1 = 1357.84, which rounds once to 1358; rounding first gives 1234 × 1.1 = 1357.4 → 1357. The control distinguishes the two. Good.

> Item 12 (c), the mounted case (a decimal port → the parent's output step rounds once): ACCEPTED as "owed by whichever of SL-1340 (PL 9610) and PL 9521 merges SECOND". PL 9610 gets the hand-off line at its next fold, and PL 9521 names it. Neither closes its slice without either building the mounted red or citing the other's merged test.

- **The mounted red.** `test_a_mounted_decimal_port_rounds_once_at_the_parent_output`: a
  fragment computes a money value as `decimal` into a `decimal` output port. A parent
  algorithm mounts it, and the port feeds the parent's `output` step declared `money_minor`
  with `rounding {"mode": "half_even", "dp": 0}`. With `1234.4 × 1.1 = 1357.84`, the served
  value is **1358**: one rounding, at the output step. Rounding first would give
  `1234 × 1.1 = 1357.4 → 1357`, and the test asserts that the two differ before it asserts
  `1358`. It is PL 9521's item 12 (c). **Whichever of this slice and PL 9521 merges second
  builds it.** Neither closes its slice without either building it or citing the other's
  merged test.
- **`_compatible`.** PL 9521 changes `_compatible` (`compile.py:124`) to a closed numeric
  rule, with a required keyword-only `at_output_step`. This slice's mount-port check calls
  `_compatible` (Task 5 Step 3, this plan's `:581-583`). The two **serialise** (PL 9521's contention
  table). Whichever lands second updates the other's call. A mount port is not an output
  step, so it passes `at_output_step=False`. A `decimal` value into a `money_minor` port is
  then refused (PL 9521 D9; "a sub-graph port carries money as decimal", the maintainer's
  entry of 17:50:43 BST).

## Self-review

1. **Against `RL-1309`'s Slice 2 obligations** (`:607-612`, under *What it obliges* at `:582`) and its *Acceptance* (`:627-653`):
   - DP-1 item 5 → Task 1 (§4.3), Task 5 step 3.4, acceptance 9;
   - DP-1 item 3 → Task 4, acceptance 7, including whichever-lands-second;
   - G1 → Task 5 step 3.1–3.2, Task 6, acceptance 4 and 9;
   - G2 → Task 6, acceptance 9;
   - G4 (a)–(c) → Tasks 5 and 6, acceptance 9;
   - DP-3 items 3–5 → Tasks 2, 3 and 5, acceptance 3–5;
   - DP-4 → Task 3, acceptance 4;
   - DP-S1-4 item 6 → Task 5 step 3.2, acceptance 4.
   Each of the nine *Acceptance* bullets for Slice 2 maps to an acceptance item here.
2. **Against `PL-1254` Task 2** (`:288-312`): the spec change → Task 1; `Pins.sub_graphs` and the
   contracts → Task 2; resolve, refuse and inline with namespacing → Tasks 3 and 5; `bundle_hash`
   → acceptance 6; the trace → Task 7; "no sub-graph, exactly as today" → acceptance 5 and 10;
   the four red-first proofs → acceptance 4; FD-1241 → acceptance 12.
3. **Against `RL-1344` §4:** no `purposes`, the interim refusal stays, and the window's
   consequence is stated (**Goal**) and pinned (Task 8). The dispatch-record bullet is activation
   need 7.
4. **FR-217 read to its clauses** (`03:86`): "versioned artifacts referenced by the parent" → the
   pin and G1; "inlined at bundle time" → Tasks 3 and 5. **FR-258** (`03:175`): "every step's id,
   label, consumed values, produced value … Traces are the same structure in real-time and batch"
   → Task 7, both paths.
5. **Literals.** Every file:line in the premises, Status and Tasks was read at `cdaaa573`. The
   names the executor adds are proposals, each named once: `Pins.sub_graphs`,
   `SubGraphRef.inputs` and `.outputs`, `inline_mounts`, `inline.py`, `AlgorithmSubGraphChange`
   and `sub_graph_mounts`. PL-1471's `_check_reachable_objectives` is that plan's name at
   `2b5bf12d`, and is re-read at dispatch.
6. **Placeholders.** None. The open DP cells are the §1.7 form for open rows.
7. **Open:** DP-S2-1 and DP-S2-2 for the decision-maker. Activation need 3 (RL-1519's mint), need
   4 (the WK-673 carrier) and the order against PL-1520 for the lead.
