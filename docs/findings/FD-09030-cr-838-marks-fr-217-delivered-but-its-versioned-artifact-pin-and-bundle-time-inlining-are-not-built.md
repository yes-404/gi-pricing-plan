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

**Severity: high** (raised from medium on 2026-09-29 at 15:38Z by the end-to-end run in *Update*; first written as medium on a reading). `FR-217` (`docs/specs/03-rating-engine.md:86`) says an algorithm "can be composed from **sub-graphs** … that are versioned artifacts referenced by the parent and inlined at bundle time." The WK-669 closure record `CR-838` types `FR-217` **delivered** (`CR-838:39`, "marker-evidenced"). At `origin/main` `49604a31785c8e7709e9b87c3926e27ea1c0f7f2` the repository has one thing for `FR-217`: the **reference shape** (`SubGraphRef`, an `ArtifactRef` plus a `mount_point`). A sub-graph is not a stored artifact, a Rating Version does not pin one, and `compile_bundle` never reads `sub_graphs`, so nothing is inlined. Under `CLAUDE.md` §13's four verdicts the requirement's second half is **not started**, and `CR-838`'s "delivered" does not carry it.

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
So a reference to a sub-graph that exists nowhere, mounted at a point that names no step, satisfies the guard, and the cancellation is priced exactly as new business, which is what `FR-218` names as the failure the refusal exists to prevent. *(This paragraph's "Not shown" is superseded: the API path was run end to end at 15:38Z, see *Update* below. What follows is the earlier text.)* **Not shown then:** that the API path (`POST /api/v1/rating-algorithms`, then compile and score) accepts such a version end to end. I ran it at the `pricing-core` level only; `backend` has no sub-graph code to reject it (above), and I did not test the save-time validation.

**Journey steps that cite `FR-217`** (`close-workstream` §5c). `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:62`, step B7: "Pricing Actuary — Mounts the reusable `sub_graph:ncd-ladder@4` rather than re-drawing it. `03` FR-217". The step still says what the requirement says. It cannot be carried out today: there is no sub-graph `ncd-ladder@4` to mount, and a mount would be inert.

**The verdict gap, in `CLAUDE.md` §13's terms.** For `FR-217`: the **reference shape** is delivered and tested at the level of a parse; **sub-graphs as versioned artifacts** (a stored, versioned thing): not started; **pinning by the Rating Version**: not started; **inlining at bundle time**: not started. `CR-838` records one verdict, "delivered", for the requirement.

## Update — the end-to-end run and what could have been stored (2026-09-29, 15:37Z to 15:40Z)

The maintainer's entry "2026-09-29 16:34:39 BST · maintainer (acting on the maintainer's behalf) · FR-217 GUARD FAILS OPEN: the interim fix is dispatched NOW as HIGH; P9 recurrence check" (`~/gi-pricing-plan.local/channel/to-lead.md`) dispatched an interim fix as HIGH without waiting for this run: the guard is to refuse every `mid_term_adjustment` and `cancellation` quote until FR-217 inlining exists, whatever `sub_graphs` holds. It asked for this run in parallel, to set the severity recorded here, and for this record to say whether a quote of either purpose could have reached a stored result.

**The run.** One targeted test, `backend/tests/test_zz_scratch_fr217.py::test_scratch_fr217_end_to_end` (a scratch file, never committed; a copy is in the evidence directory), run at load 2.13 with `nice -n 19` and thread caps, over a per-worktree database, through the HTTP client and the real routes. The log opens `SHA: 33d5cba0cce827accc6016d11ac6ee24187775a5` and ends `RC=0` (`~/gi-pricing-plan.local/evidence/fr217/fr217-e2e.log`; raw lines in `fr217-e2e-raw.txt`; all in `SHA256SUMS`). The code under test is `origin/main` `49604a31785c8e7709e9b87c3926e27ea1c0f7f2` (the branch adds docs only). Output, verbatim:

```text
POST /rating-algorithms v1 sub_graphs=0 -> 201
compile job v1 -> succeeded
POST /rating-algorithms v2 sub_graphs=1 -> 201
compile job v2 -> succeeded
compare purpose=new_business         version v1 (sub_graphs=none) -> 200 2000
compare purpose=new_business         version v2 (sub_graphs=unknown ref) -> 200 2000
compare purpose=cancellation         version v1 (sub_graphs=none) -> 422 INPUT_CONTRACT_VIOLATION
compare purpose=cancellation         version v2 (sub_graphs=unknown ref) -> 200 2000
compare purpose=mid_term_adjustment  version v1 (sub_graphs=none) -> 422 INPUT_CONTRACT_VIOLATION
compare purpose=mid_term_adjustment  version v2 (sub_graphs=unknown ref) -> 200 2000
```

So `POST /api/v1/rating-algorithms` with `sub_graphs=[{"ref": "sub_graph:does-not-exist@1", "mount_point": "s_nowhere"}]` is saved (201); the compile job succeeds; and `POST /api/v1/score/compare` prices a `cancellation` and a `mid_term_adjustment` at 2000, the same as `new_business`, where the same algorithm with no `sub_graphs` refuses both with `INPUT_CONTRACT_VIOLATION`. The fixture is the minimal algorithm of `backend/tests/test_rating_version_compile.py`, not the earlier `pricing-core` fixture, which is why the payable is 2000 here and 1507 there. The static reading in the earlier text is now confirmed by a run.

**Could a quote of either purpose have reached a stored result?** Every route that runs `score_one` or its synchronous twin passes through the same guard (`packages/pricing-core/src/pricing_core/rating/score.py:775` and `:936`), so a Rating Version whose algorithm lists any `sub_graphs` prices these purposes as new business on each route below. Where a result can be stored, at `49604a31785c8e7709e9b87c3926e27ea1c0f7f2`:
- **`POST /api/v1/score`** (`backend/src/app/api/score.py:312`): the price is returned. If the trace sampler selects the outcome, `_maybe_sample_trace` (`score.py:319`, defined `:379`) writes a pending `ScoringTraceRow` (`backend/src/app/db/models.py:2134`) carrying the whole `QuoteContext`, purpose included, and a summary of the served result (`backend/src/app/platform/traces.py:159` `write_pending_trace`), and submits the `score.trace_produce` Job (`backend/src/app/worker/trace_handlers.py:44`, completing the row at `:94`). Those rows are permanent by design. **Stored only when sampled.**
- **`POST /api/v1/score/batch`** (`score.py:481`): the Job `_score_batch_handler` (`backend/src/app/worker/scoring_handlers.py:304`) calls `score_batch` (`:231`); rows carry their own `purpose` column (`pricing-core score.py:268`, `:914`) and pass the guard on the synchronous path (`:936`). The scored rows are written to the blob store as an output parquet (`scoring_handlers.py:280` `blob_store.put`) with a summary blob. **Stored.**
- **Regression Runs** (`POST …/regression-runs`, worker `backend/src/app/worker/rating_handlers.py:180` `run_regression`): the suite's golden quotes each carry a `QuoteContext` with a `purpose` (`packages/model-schema/src/model_schema/regression.py:75-81`), are scored by `evaluate_golden_quotes` (`packages/pricing-core/src/pricing_core/rating/testing.py:266`), and the run is persisted as a `RegressionRunRow` (`db/models.py:2092`, `persist_run` at `rating_handlers.py:199`) with a cases blob. **Stored, if a golden quote uses one of the two purposes.**
- **The submit gate** (`backend/src/app/platform/rating_versions.py:593` `evaluate_golden_quotes`): its results are pinned into the Rating Version's `evidence.golden_quotes` (`:294`). **Stored, same condition.**
- **`POST /api/v1/score/compare`** (`score.py:334` onward): nothing is stored; `test_compare_persists_nothing_even_at_a_trace_sample_rate_of_one` asserts it and I reproduced its red under a copied sampler.

**What this record can and cannot say.** Every one of those paths needs a saved Rating Algorithm whose `sub_graphs` list is non-empty. In the repository, every fixture, example and script writes `"sub_graphs": []` (`examples/fremtpl2/model.py:347`, `scripts/bench-compiled-for.py:91`, `scripts/bench-rating.py:269`, `scripts/bench-score-batch.py:90`, the backend tests), and the frontend source has no `sub_graphs`. Whether any environment holds an algorithm with a non-empty list is a question about data, which the maintainer's entry keeps as a separate review; **this record did not query any database** and does not say whether any such quote was stored.

## Disposition

**Proposed by the auditor; the decision is the lead's.** The Work is **not reopened** (the maintainer's entry above, §4). Plan review 16 routes the remedy to the Work that takes `FR-218`'s authoring half, since both are the mid-term-adjustment sub-graph: the planner proposes it, the lead gives the verdict, the maintainer accepts. `CR-838` carries the dated correction "guard delivered; `sub_graphs` inlining NOT delivered → FD-9030" beside its verdict table (its verdict text is not rewritten).

**not started** for `FR-217`'s versioned-artifact, pin and inlining limbs, **unowned-pending-authorisation**: no Work owns them, and none was ever named. The event that next confirms or discharges the row: plan review 16 gives the requirement a disposition, either an owner and a Work that builds the artifact, the pin and the inlining (which would also let `FR-218`'s guard test a real mount instead of a non-empty list), or a maintainer amendment that narrows `FR-217` to the reference shape. The maintainer's decision already routes it: the Work that takes `FR-218`'s authoring half. **Interim, dispatched 2026-09-29 (the maintainer's 16:34:39 BST entry, cited in *Update*):** the guard refuses every `mid_term_adjustment` and `cancellation` quote until FR-217 inlining exists, whatever `sub_graphs` holds (branch `wk1178-fr218-fail-closed`, executor-s2-2); it merges on the maintainer's ACK. That fix closes the silent-mispricing path; it does not build FR-217. Until then the guard's "any non-empty list" stand-in is the only thing between a cancellation and new-business pricing.

Ownership shape: event.
