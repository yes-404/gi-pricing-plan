---
id: FD-9030
family: finding
title: CR-838 marks FR-217 delivered, but its versioned-artifact, pin and bundle-time inlining limbs are not built
status: active
created: 2026-09-29
owner: auditor
tree: 49604a31785c8e7709e9b87c3926e27ea1c0f7f2
corrected_by: []
relates: [WK-669, FR-217, FR-218]
---

# FD-9030 — CR-838 marks FR-217 delivered, but its versioned-artifact, pin and bundle-time inlining limbs are not built

## Finding

**Severity: medium.** `FR-217` (`docs/specs/03-rating-engine.md:86`) says an algorithm "can be composed from **sub-graphs** … that are versioned artifacts referenced by the parent and inlined at bundle time." The WK-669 closure record `CR-838` types `FR-217` **delivered** (`CR-838:39`, "marker-evidenced"). At `origin/main` `49604a31785c8e7709e9b87c3926e27ea1c0f7f2` the repository has one thing for `FR-217`: the **reference shape** (`SubGraphRef`, an `ArtifactRef` plus a `mount_point`). A sub-graph is not a stored artifact, a Rating Version does not pin one, and `compile_bundle` never reads `sub_graphs`, so nothing is inlined. Under `CLAUDE.md` §13's four verdicts the requirement's second half is **not started**, and `CR-838`'s "delivered" does not carry it.

The gap has one consequence that is live in code: `FR-218`'s fail-closed guard takes "any non-empty `sub_graphs`" as proof that the refund sub-graph is mounted, so a Rating Version that lists a sub-graph reference to something that does not exist passes the guard and prices a cancellation as new business (Evidence, *The consequence*). This record states the verdict gap. It does **not** propose reopening WK-669: the maintainer decided not to (entry "2026-09-29 16:25:49 BST · maintainer (acting on the maintainer's behalf) · BLOCKER DECISIONS by delegation: #882, the Dependabot merges, the Actions majors, FR-217, FD-1238, and the WK-672/PR16 acceptance", §4), and `CR-838` now carries a dated correction note pointing here.

Filed under a **working id** (`FD-9030`); the lead mints it at its merge turn.

## Evidence

All facts are read at `origin/main` `49604a31785c8e7709e9b87c3926e27ea1c0f7f2` on 2026-09-29, in a detached worktree of that commit, unless another source is named.

**The requirement, in full.** `03-rating-engine.md:86`: "**FR-217** An algorithm can be composed from **sub-graphs** (reusable fragments, e.g. "no-claims-discount ladder", "IPT and fees") that are versioned artifacts referenced by the parent and inlined at bundle time." It carries no dated amendment: `git grep -n 'FR-217'` over `docs/specs` finds only this row and the `FR-218` row that leans on it. `FR-218` (`:87`) adds: "pro-rata, refund and charge logic in a separately-versioned sub-graph (FR-217) … The mount is **declared on the Rating Version and version-pinned like any other sub-graph**", and "A version that mounts no such sub-graph refuses an MTA or cancellation quote rather than pricing it as new business — pricing it as new business is the failure this requirement exists to prevent, and it is silent."

**What is built.**
- The shape: `packages/model-schema/src/model_schema/rating.py:340-351` (`SubGraphRef`: `ref: ArtifactRef`, `mount_point: str`) and `:390` (`RatingAlgorithm.sub_graphs: list[SubGraphRef]`); `"sub_graph"` is a legal artifact type in `refs.py:25`. `mount_point` is a bare string: nothing checks that it names a step.
- The only test that carries `req("FR-217")` is `packages/model-schema/tests/test_rating_algorithm.py:81` `test_a_valid_algorithm_parses`, which asserts `algorithm.sub_graphs[0].ref.type == "sub_graph"` (`:93`) and `.mount_point == "s_ncd"` (`:94`): a parse of the shape. `python3 scripts/req-coverage.py` prints `FR-217           1 test file(s)`.
- The fail-closed guard: `packages/pricing-core/src/pricing_core/rating/score.py:393-410` `_check_purpose_mount`, applied at `:775` and `:936`, tested by three tests marked `FR-218` (`packages/pricing-core/tests/test_rating_score.py:414`, `:425`, `:433`). Its docstring says "sub-graph inlining (`SubGraphRef.mount_point` resolution, `compile_bundle`'s own TODO) is not built by any slice yet, so no rating version can meaningfully mount one today", and calls "any non-empty `algorithm.sub_graphs`" "a documented, provisional stand-in".

**What is not built** (each absence has a positive control run with the same form):
- **`compile_bundle` ignores sub-graphs.** `grep -c -i 'sub_graph' packages/pricing-core/src/pricing_core/rating/compile.py` prints `0`; the same command with `pins` prints `18`. The only hits for `sub_graph` under `pricing_core/rating/` are the two lines in `score.py` (`:397`, `:406`). The `TODO` the guard's docstring cites does not exist: `grep -rn 'TODO' packages/pricing-core/src/pricing_core/rating/` finds exactly one hit, that docstring at `score.py:399`. The `SubGraphRef` docstring (`rating.py:343-345`) says the sub-graph "is inlined at bundle time (W9-3)".
- **A sub-graph is not an artifact.** No model, route or table: `git grep -n -i 'sub_graph' -- backend` finds four hits, all `"sub_graphs": []` in test fixtures (`test_bundle_slot.py:72`, `test_rating_algorithms.py:61`, `test_rating_version_compile.py:70`, `test_regression_suites.py:322`); the positive control, `grep -c -i 'rate_table' backend/src/app/api/*.py`, finds hits in several modules (`rate_tables.py` 9, `traces.py` 1, `score.py` 2, among the first three it lists). `model-schema` has `SubGraphRef` and no `SubGraph`.
- **A Rating Version does not pin one.** `Pins` (`rating.py:63-76`) holds `rate_tables`, `models`, `reference_tables` and `custom_objectives`, and no `sub_graphs`. `bundle_hash` hashes `{"graph": …, "pins": …}` (`compile.py:403-417`), so a sub-graph's content is in neither the Bundle nor its hash, against `FR-218`'s "version-pinned like any other sub-graph".

**The record trail.**
- The plan `PL-818` (WK-669) asked the question: `DP2` (`PL-818:194`) "build the sub-graph reference and the inlining in W9-1, or declare the reference and defer the inlining". The decision-maker ruled on 2026-08-27 (`PL-818:204-206`): "**DP2 confirmed.** Build the sub-graph reference and the inlining in W9-1. FR-217 requires sub-graphs to be "inlined at bundle time"; deferring the inlining would contradict the requirement."
- The plan's own W9-1 task list carried only the shape: "Add the sub-graph shape: a versioned artifact reference and a mount point (FR-217)" (`PL-818:100`); no task in `PL-818` mentions building the inlining (`grep -n -i 'inlin' PL-818` finds only the DP2 question and ruling).
- The W9-1 slice record `CR-835:35` lists `SubGraphRef (FR-217)` as delivered under the shape row. `CR-838:31` (the W9-1 row) lists "6 (sub-graphs)" among the delivered requirements, and `CR-838:39` gives 13 requirements including `FR-217` the single verdict "delivered" with the evidence "marker-evidenced (req-coverage: FR-212 6 files, 2-13 at least 1 each)"; its W9-3 row (`CR-838:33`) names no sub-graph work. Plan review 7 (`CR-825:47`) repeats it: "FR-217 (sub-graphs) was W9-1's own delivery".
- No record says the inlining was built, and none defers it with an owner: `git grep -n -i -E 'sub-graph|sub_graph|inlin|FR-217'` over `docs/findings/register.md`, `docs/open-questions.md` and `docs/roadmap.md` finds nothing that owns it (roadmap `:1286-1300` only reproduces `OQ-617`'s prose on the mount).

**The consequence, demonstrated** (log `~/gi-pricing-plan.local/evidence/fr217/fr217-demo.log`, script `fr217-demo.py`, both in `SHA256SUMS`; the log opens `SHA: 49604a31785c8e7709e9b87c3926e27ea1c0f7f2` and ends `RC=0`). Using the test module's own fixture helpers (`test_rating_score._compiled`, `_ctx`, `_algorithm_payload`), scoring through `score_one`:
| Rating Version | purpose | result |
|---|---|---|
| no `sub_graphs` (the fixture) | `new_business` | quoted, payable 1507 |
| no `sub_graphs` | `cancellation` | refused `INPUT_CONTRACT_VIOLATION` |
| no `sub_graphs` | `mid_term_adjustment` | refused `INPUT_CONTRACT_VIOLATION` |
| `sub_graphs=[sub_graph:does-not-exist@1 at s_nowhere]` | `cancellation` | **quoted, payable 1507** |
| the same | `mid_term_adjustment` | **quoted, payable 1507** |
So a reference to a sub-graph that exists nowhere, mounted at a point that names no step, satisfies the guard, and the cancellation is priced exactly as new business, which is what `FR-218` names as the failure the refusal exists to prevent. **Not shown:** that the API path (`POST /api/v1/rating-algorithms`, then compile and score) accepts such a version end to end. I ran it at the `pricing-core` level only; `backend` has no sub-graph code to reject it (above), and I did not test the save-time validation.

**Journey steps that cite `FR-217`** (`close-workstream` §5c). `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:62`, step B7: "Pricing Actuary — Mounts the reusable `sub_graph:ncd-ladder@4` rather than re-drawing it. `03` FR-217". The step still says what the requirement says. It cannot be carried out today: there is no sub-graph `ncd-ladder@4` to mount, and a mount would be inert.

**The verdict gap, in `CLAUDE.md` §13's terms.** For `FR-217`: the **reference shape** is delivered and tested at the level of a parse; **sub-graphs as versioned artifacts** (a stored, versioned thing): not started; **pinning by the Rating Version**: not started; **inlining at bundle time**: not started. `CR-838` records one verdict, "delivered", for the requirement.

## Disposition

**Proposed by the auditor; the decision is the lead's.** The Work is **not reopened** (the maintainer's entry above, §4). Plan review 16 routes the remedy to the Work that takes `FR-218`'s authoring half, since both are the mid-term-adjustment sub-graph: the planner proposes it, the lead gives the verdict, the maintainer accepts. `CR-838` carries the dated correction "guard delivered; `sub_graphs` inlining NOT delivered → FD-9030" beside its verdict table (its verdict text is not rewritten).

**not started** for `FR-217`'s versioned-artifact, pin and inlining limbs, **unowned-pending-authorisation**: no Work owns them, and none was ever named. The event that next confirms or discharges the row: plan review 16 gives the requirement a disposition, either an owner and a Work that builds the artifact, the pin and the inlining (which would also let `FR-218`'s guard test a real mount instead of a non-empty list), or a maintainer amendment that narrows `FR-217` to the reference shape. The maintainer's decision already routes it: the Work that takes `FR-218`'s authoring half. Until then the guard's "any non-empty list" stand-in is the only thing between a cancellation and new-business pricing.

Ownership shape: event.
