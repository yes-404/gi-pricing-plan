---
id: PL-WORKING
family: plan
kind: leaf
title: WK-672 Slice 3 — Property assertions and regression runs: leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-28
owner: planner
tree: e6a9ca71a0bef3da41720d20f3f20db73f6a1d80
phase: P2
work: WK-672
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-930, PL-1189, RL-1172, RS-1176]
---

# WK-672 Slice 3 — Property assertions and regression runs: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `python-package`, `contract-guard` and `repo-architecture` (Tasks 2–3; a new runtime dependency), `python-test`, `fastapi-service` (Task 5) and `dev-commands` (the gate).

## Goal

Build FR-261's regression run and FR-257 limb (1):
- `generate_contexts` and `run_regression` in `pricing-core`, on `hypothesis` under RS-1176's six conditions;
- the five stored property classes evaluated;
- `RegressionRun` as a `model-schema` artifact;
- `POST …/regression-runs` as a 202 Job;
- submission refused unless a passing run exists for the version's current bundle.

**Architecture:** This is the leaf plan for Slice 3 of the map plan `PL-930`, after Slice 2 (`PL-1189`). It applies:
- `RL-1172` items 3a–3c and 4;
- the deputy's F4 decision as filed in `RS-1176` (`docs/research/RS-01176-hypothesis-seed-and-shrink-determinism-across-processes.md:220-229`, condition 1 as corrected at `:235-247`);
- `PL-1189`'s carries to Slice 3.

Placement (RL-1172 item 3c):
- **`pricing-core`** holds only pure generation, evaluation and replay.
- **The backend** holds the route, the Job, the run row, the blob and the submit check.

No `SL-` row exists, so there is no `slice:` field.

**Prerequisite, checked at Task 0.** Slice 2's code PR (the one executing `PL-1189`) is merged. At `e6a9ca71`, `packages/pricing-core/src/pricing_core/rating/` holds no `testing.py`, and `RegressionSuite` and `evaluate_golden_quotes` do not exist yet. This plan uses the names `PL-1189` fixes: `model_schema.regression`, `evaluate_golden_quotes`, `GoldenQuoteCheck`, the `regression_suites` registry and `rating_versions.submit_for_review` with its golden-quote gate.

**Tech Stack:**
- `hypothesis` 6.165.7, the version `uv.lock:914-915` resolves at `e6a9ca71`, pinned exactly;
- Pydantic v2, FastAPI, Celery (the Job worker), PostgreSQL and the blob store;
- pytest.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md):
- §3.8: FR-257 and FR-261;
- §4.7 and §4.9;
- §5.1 (`POST /api/v1/rating-versions/{id}/regression-runs`, **202**);
- §5.2 (the `testing.py` block);
- §8 (tech dependencies).

Also [`../specs/06-governance.md`](../specs/06-governance.md) FR-364 (the `regression_run` evidence floor) and NFR-499 (`03` §9, RL-917).

## Acceptance Standard

Every command runs in the executor's worktree (`env -C <worktree> …`), over `origin/main...HEAD`. "Red first" means the failing run is quoted in the ledger with its failing assert line; a failure for another cause is a plan defect.

1. **Spec.** `03` changes as follows:
   - §8 names `hypothesis` as a `pricing-core` runtime dependency at its exact pin;
   - §4.9 declares the new `RegressionRun` fields (Task 1);
   - §5.2 declares `replay_cases`;
   - FR-261 carries a dated amendment: persisted cases are the reproduction mechanism, and the seed serves same-version regeneration.

   Also:
   - FR-257 carries the dated at-least-one-golden-quote clarification (DP-S3-1);
   - one appended §3.8 FR names the case store, its id minted at the code PR's turn (DP-S3-4 (i));
   - NFR-499 carries the dated clarification that adds it as the third store and corrects the "persists a seed" sentence (DP-S3-4 (ii)).

   `docs/skills-map.md` names the dependency. `python3 scripts/audit-docs.py` adds no failure row.
2. **Condition 1, the pin.** `grep -n 'hypothesis==6.165.7' packages/pricing-core/pyproject.toml pyproject.toml` prints two lines: pricing-core's `[project] dependencies` and the root dev group, aligned. `uv.lock` resolves one `hypothesis` version. `uv run lint-imports` exits 0, and the PR description lists `uv tree --package pricing-core` for `hypothesis`, showing no FastAPI, SQLAlchemy or Redis.
3. **Condition 2, the settings.** A test asserts the settings `run_regression` applies:
   - `database is None`;
   - `deadline is None`;
   - `report_multiple_bugs is False`;
   - `derandomize is False`;
   - `max_examples == suite.generation.cases`;
   - the seed is the suite's.

   `RegressionGeneration.cases` refuses above 10 000 (the bound).
4. **Condition 3, the version.** Every `RegressionRun` records `generation.hypothesis_version`. `generate_contexts(..., expect_version=v)` with `v != hypothesis.__version__` raises `GeneratorVersionMismatch`, naming both versions. The test is red first.
5. **Condition 4, the persisted cases.** A run persists every generated case and every counterexample as one content-addressed canonical JSON blob, recorded in `cases_blob`. `replay_cases(bundle, cases, suite)` re-scores those cases and never calls the generator; a test patches the generator to raise and replay still passes. Reading the blob requires `rating:read`, **the same control as reading a Golden Quote's suite**. A test (DP-S3-4 (iii), `req("NFR-499")`) asserts that a principal refused a suite read is refused the blob read, that one allowed is allowed, and that no log line carries a case's inputs.
6. **Condition 5, a stopped shrink.** Each failing property result records `shrink: "completed" | "stopped_on_limit"`, read through `hypothesis.statistics.collector` (Task 3). A test forces the limit by monkeypatching `hypothesis.internal.conjecture.engine.MAX_SHRINKS` to 1. It asserts `shrink == "stopped_on_limit"` and `counterexample_minimal is False`, and it is red first.
7. **Condition 6, determinism across processes.** `uv run pytest packages/pricing-core/tests/test_testing_determinism.py -v` passes. It covers:
   - two fresh `subprocess` interpreters, given the same persisted seed, produce identical sha256 of the canonical case log and identical counterexamples;
   - the no-seed negative control produces differing logs, so the comparator can fail.

   It is a CI test.
8. **The five classes are evaluated.** `uv run pytest packages/pricing-core/tests/test_testing.py -k property -v` passes: a passing and a failing case for each of `premium_positive`, `monotone`, `no_null_output`, `ladder_reconciles` (FR-248) and `premium_bounded`. A `monotone` naming an input absent from the input contract is refused before generation.
9. **The run is a 202 Job and a row.**
   - `POST /api/v1/rating-versions/{id}/regression-runs` returns 202 with a Job.
   - The Job persists a `RegressionRun` row whose `bundle_hash` is the scored `CompiledBundle.content_hash`, with `suite_ref`, `suite_content_hash` and `overall`.
   - A failing run ends the Job `failed`, with problem `PROPERTY_ASSERTION_FAILED` (or `GOLDEN_QUOTE_MISMATCH` when a golden quote failed), and the row still persists.
   - The route is refused 403 without `rating:compile`.
10. **FR-257 limb (1).**
    - `submit_for_review` refuses with `EVIDENCE_INCOMPLETE` when there is no run, a failing run, a run on a stale `bundle_hash`, or (DP-S3-2) a run whose `suite_content_hash` differs from the suite the submit gate pins. **The latest run for that (`bundle_hash`, `suite_content_hash`) pair must itself be a pass** (audit A1). A test runs a pass, then a later fail on the same pair, and submit is refused. Each test is red first and carries `req("FR-257")` with a docstring naming limb (1) only.
    - A passing run sets `evidence.regression_suite_run_id`.
    - A test asserts `evidence.golden_quotes` is byte-identical before and after that write.
11. **DP-S3-1 applied** as the deputy decides. The default (a): a submission whose algorithm has no suite, or whose suite has zero golden quotes, is refused with `EVIDENCE_INCOMPLETE`. The test is red first.
11b. **Every fixture and demo Rating Version that must reach `review` or `approved` has a golden quote** (DP-S3-1 applies forward; the deputy's note on WF-699 and gate G2). `grep -rlnE 'submit_for_review|rating-versions/[^"]*/submit' backend/tests backend/src scripts examples frontend` at the executor's tree lists the sites. Each goes through one shared fixture that authors a suite with at least one golden quote, and the list is quoted in the ledger with a pass for each.
12. **The contract.**
    - `regression-run` is generated from `model-schema` and in `COMPARED_SLUGS`, and its `ONE_SIDED_SLUGS` entry is removed.
    - `uv run python scripts/generate-contracts.py --check` exits 0.
    - `uv run pytest backend/tests/test_contracts.py -q` passes.
13. **The gate.**
    - The full two-half gate exits 0, with every rc and `HEAD` in the ledger.
    - `uv run pytest packages/pricing-core/tests/test_rating_score.py -q` runs **five times**, each rc recorded. If any run aborts natively (a negative rc, or a `PyGILState` message), the slice does not pass its gate: FD-1199's triage moves ahead of it, and nothing is re-run until green.
    - The four docs checks pass on a detached copy, with DISCLOSED no higher than main's.
    - `git diff --stat origin/main...HEAD` lists only the Files blocks' paths, the ledger and `docs/INDEX.md`.
14. **The deputy's merge acknowledgement is recorded** on the PR before the lead merges, and
    the slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and
    the lead's merge — no maintainer acceptance line is required for this slice, and none is
    to be waited on.

## Global Constraints

- **`pricing-core` stays standalone** (`CLAUDE.md` §2). `hypothesis` pulls no FastAPI, SQLAlchemy or Redis, and `lint-imports` enforces it.
- **A new runtime dependency lands with `docs/skills-map.md`** (`CLAUDE.md` §10) **and `03` §8**, in the same PR.
- **Money is integer minor units** (`CLAUDE.md` §7, FR-273). Property checks compare `MoneyMinor` integers.
- **Shapes are `model-schema`'s** (ADR-704). `RegressionRun`'s new fields are declared there, never in the backend.
- **Quote inputs are held only in access-controlled artifacts, never logged** (NFR-499, RL-917). The cases blob is one of them.
- **`evidence.golden_quotes` is never overwritten** (`PL-1189`, re-audit N5).
- **Permissions: `rating:compile` to start a run, `rating:read` to read a run or its blob.**
  - Both exist, and none is added.
  - A run is a Job over a Rating Version's compiled bundle, as `POST …/compile` is, and that route is already gated on `rating:compile`.
  - This is named per #855's permission-catalogue finding. The coarse catalogue follows #856's catalogue ruling, DP-A (c).
- **The scoring path's threading is unchanged.** The five-run repeat (acceptance item 13) runs because of FD-1199.
- **Approval rules from #864 are consumed, not changed.** An approval applies only to a version in review.

---

## Scope

**Requirements:**
- **FR-261** (`03` §3.8): Tasks 1, 3, 4 and 5.
- **FR-257 limb (1)** (`03` §3.8; RL-1172 item 4; the register row F44): Task 6.
- **FR-260**: composed, not rebuilt. `run_regression` calls S2's `evaluate_golden_quotes`.
- **FR-248** (the ladder reconciles): evaluated as a property class.
- **FR-273**: exact integer comparison.
- **NFR-499**: the blob's access control.
- **`06` FR-364**: the `regression_run` floor is fed by `evidence.regression_suite_run_id`.

**Carried in from `PL-1189`:**
- evaluating the five classes (Task 4);
- validating monotone inputs (Task 4);
- `run_regression` composing `evaluate_golden_quotes` (Task 4);
- `RegressionRun` as a `model-schema` artifact, with the authored `regression-run.schema.json` moved to compared (Task 2);
- FR-257 limb (1) (Task 6);
- `PROPERTY_ASSERTION_FAILED` together with its raiser (Task 5);
- the required-suite decision (DP-S3-1);
- no overwrite of `golden_quotes` (Task 6).

**Carried out:**
- `POST /api/v1/score/compare` is Slice 4's.
- WK-672's closure record follows.
- Rendering the run in the UI is WK-675's.

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S3-1 | Is a suite with at least one golden quote **required** at submission, at least for Rating Versions headed to `prod`? FR-257 limb (1) already requires a passing run, so a suite, for every approval; the open part is golden quotes (`PL-1189` carry, the deputy's 15:57:21 item (i)) | (a) every submission needs at least one golden quote; (b) only a `prod` deployment needs one, enforced at WK-674's deploy gate; (c) neither, since a properties-only suite suffices | (a): every approved version can reach `prod`, and a properties-only suite checks no priced outcome | **scope** (the maintainer's, by delegation to the deputy) | yes (Tasks 1, 6, 6b) | **(a), every submit**, with a spec line: the deputy's decision by delegation, 2026-09-28 18:17:32 BST, quoted above |
| DP-S3-2 | Must the passing run's `suite_content_hash` equal the suite the submit gate pins? | yes; no | yes: otherwise a suite edited after the run is approved on a stale run | decision point | yes (Task 6) | **yes**: the deputy's decision by delegation, 2026-09-28 18:17:32 BST, quoted above |
| DP-S3-3 | Is the run a blocking gate by itself, and what raises `PROPERTY_ASSERTION_FAILED`? | (a) the run records `overall=fail`, and submission refuses through limb (1); the code is the failed Job's problem; (b) the run's route itself refuses | (a) | decision point | yes (Task 5) | **yes, blocking through FR-257 limb (1)**: the deputy's decision by delegation, 2026-09-28 18:17:32 BST, quoted above |
| DP-S3-4 | Where does the cases blob live? | (a) the existing blob store, as a `BlobRef` (`model_schema/refs.py:138`), read-gated on `rating:read`; (b) inline JSONB on the run row | (a): a run can hold 10 000 cases, and NFR-499 wants one access-controlled home | decision point | yes (Tasks 1, 5) | **(a), AMENDED**: the store needs its own requirement (RL-917). An appended `03` §3.8 FR, a dated NFR-499 clarification and an access-control test land in the same commit; the blob route's own access control is Task 0b (audit B1, pending the deputy); the deputy's decision by delegation, 2026-09-28 18:17:32 BST, quoted above |

The deputy's ruling, quoted whole:

```text
## 2026-09-28 18:17:32 BST · deputy · WK-672 S3 DPs: DP-S3-1 (a) with a spec line; DP-S3-2 yes; DP-S3-3 yes; DP-S3-4 AMENDED — the case store needs its own requirement (RL-917)

Read at origin/main e6a9ca71: `03-rating-engine.md` :68–69 (glossary), :174 FR-257, :177 FR-260, :178 FR-261, :990 NFR-499 including its 2026-08-30 clarification.

- **DP-S3-1: (a), every submit, by delegation** (scope; on the maintainer's instruction of 2026-09-26 17:02:52 BST and the extension of 2026-09-28 ~13:50).
  - **Grounds:** with zero golden quotes, FR-260's "re-scores every golden quote" is satisfied vacuously, and nothing checks a priced outcome.
  - **Condition:** nothing in `03` states the minimum today. FR-257 and the glossary are silent on the count. S3 therefore lands it as a spec change in the same commit, per CLAUDE.md §0: a dated clarification on FR-257, or an appended FR in §3.8 (the planner picks, with the id minted at its turn), stating that a passing Regression Suite has at least one golden quote.
  - **Note it applies forward only,** at submit. Any fixture or demo RV that must reach `approved` (WF-699, gate G2) needs an authored golden quote. Say so in the plan.
- **DP-S3-2: yes.** The run's `suite_content_hash` must equal the suite pinned at submit, or submit refuses EVIDENCE_INCOMPLETE. This is the same class as my S2 condition.
- **DP-S3-3: yes, blocking via FR-257 limb (1).** FR-261 names no refusal of its own, but its property assertions are part of the Regression Suite, and FR-257 needs a *passing* one. PROPERTY_ASSERTION_FAILED is per property in the Job result, and submit refuses EVIDENCE_INCOMPLETE.
- **DP-S3-4: AMENDED, the blob store yes, but not "under NFR-499" alone.**
  - NFR-499's clarification (RL-917) names exactly two quote-input stores, sampled traces (FR-259) and Golden Quotes (FR-260). It says **"Any further store requires its own requirement"**, and it states that FR-261 "persists a seed rather than quote data" so needs no carve-out.
  - RS-1176's condition (a content-addressed case/counterexample blob, replayed by re-scoring and never regenerated) persists quote inputs. It is a third store, and it falsifies that sentence.
  - **S3 therefore lands in the same commit:**
    - (i) an appended `03` §3.8 requirement naming the regression case/counterexample store: BlobRef, content-addressed, and carrying the same access-control obligation as a trace;
    - (ii) a dated clarification on NFR-499 adding it as the third named store, with FR-261's "persists a seed" sentence corrected there, not silently;
    - (iii) a test that the store is under the same access control as golden quotes.
  - **Alternative, if the planner prefers:** persist only the seed plus the settings and version, and replay by regeneration. That breaks RS-1176's replay condition, so it would need a dated amendment to my F4 decision. I do not recommend it.

The plan carries these four as ruled; its DP table quotes this entry.
```

All four have resolvers. The plan applies them as ruled.

---

## Tasks

### Task 0: Preconditions

- [ ] Confirm that Slice 2's code PR is on `origin/main`: `git log --grep 'PL-1189' -1 origin/main`, and `packages/pricing-core/src/pricing_core/rating/testing.py` exists. Confirm that DP-S3-1 to DP-S3-4 carry resolvers. **If either fails, stop and report.**

### Task 0b: The blob route's access control (audit B1; pending the deputy)

The generic `GET /api/v1/blobs/{sha256}` (`backend/src/app/api/blobs.py:97-135`) is gated on `dataset:read` (`:39`), and `BlobRow` is keyed on `sha256` alone, with no workspace column (`db/models.py:286-288`). So the case store's "`rating:read` in its workspace" (DP-S3-4 (i), acceptance item 5) would be false as built. The same exposure is live for traces today.

- [ ] **The blob-route fix, as the deputy decides it, is on `origin/main` before Task 5, or Slice 3 lands it.** This plan does not design that fix. Its shape is the deputy's decision, pending, and the plan is amended to cite it when it is given. Until then **Task 5 does not start**, and acceptance item 5's access-control test is written against the decided route.

### Task 1: Spec — `03` §3.8, §4.9, §5.2, §8; `docs/skills-map.md`

**Files:** Modify `docs/specs/03-rating-engine.md` and `docs/skills-map.md`.

- [ ] **Step 1, FR-261.** Add a dated amendment, citing the deputy's F4 decision in `RS-1176`, with no new id: *"The generated cases and every counterexample are persisted with the run and are its reproduction record; replaying a run re-scores them. The seed, with the generator version persisted beside it, serves same-version regeneration only."*
- [ ] **Step 2, §4.9.** Add these fields to the example and the prose:
  - `suite_ref` and `suite_content_hash`;
  - `generation: {"seed", "cases", "hypothesis_version"}`;
  - `cases_blob` (a `BlobRef`);
  - on `property_results[]`, `shrink` (`completed` or `stopped_on_limit`) and `counterexample_minimal` (bool);
  - on a failing entry, `error_code`.

  A stopped shrink's counterexample is reported as **unminimised** (condition 5).
- [ ] **Step 3, §5.2.** Add `def replay_cases(bundle: CompiledBundle, cases: CasesLog, suite: RegressionSuite) -> RegressionRun` and `class GeneratorVersionMismatch(ValueError)`. `generate_contexts` gains `*, expect_version: str | None = None`.
- [ ] **Step 4, §8.** Record `hypothesis` as a `pricing-core` runtime dependency, `==6.165.7`, per RS-1176 condition 1. Add the same entry to `docs/skills-map.md`.
- [ ] **Step 5, FR-257 (DP-S3-1).** Add a dated clarification, with no new id: *"(Clarified 2026-09-28, WK-672 Slice 3, the deputy's DP-S3-1 by delegation.) A passing Regression Suite has at least one golden quote; a submission whose suite has none, or whose algorithm has no suite, is refused with `EVIDENCE_INCOMPLETE`. It applies forward, at submit."* The clarification is chosen over an appended FR because it changes the meaning of an existing FR's own term, "a passing Regression Suite".
- [ ] **Step 6, the case store's own requirement (DP-S3-4 (i)).** Append one FR to §3.8. **Its id is minted at the Slice 3 code PR's mint turn** (`doc-id.py next --ref origin/main`, the lead's call), and the text uses the `Next free:` marker line convention until then (`docs/plans/README.md` convention 2). It reads: *"A Regression Run's generated cases and counterexamples are persisted as one content-addressed canonical JSON blob (`BlobRef`), referenced from the run. They are replayed by re-scoring and never regenerated (RS-1176 condition 4). The blob carries the same access control as a sampled trace and a Golden Quote: read only with `rating:read` in its workspace, and never logged (NFR-499)."*
- [ ] **Step 7, NFR-499 (DP-S3-4 (ii)).** Add a dated clarification after its 2026-08-30 clause that names the case store (by the new FR's id) as the **third** quote-input store, after sampled traces (FR-259) and Golden Quotes (FR-260). It also **corrects** the sentence that FR-261 "persists a seed rather than quote data": since RS-1176 condition 4, a regression run persists quote inputs, and the correction is written, not silent.
- [ ] **Step 8.** Run `python3 scripts/audit-docs.py` (no new failure row), then commit.

### Task 2: `model-schema` — `RegressionRun`; the contract moves to compared

**Files:**
- Modify: `packages/model-schema/src/model_schema/regression.py` (from `PL-1189`), its tests, `scripts/generate-contracts.py` (`GENERATED_SHAPES` gains `"regression-run": "RegressionRun"`), `docs/contracts/schemas/regression-run.schema.json` (the authored side, brought to the model), and `backend/tests/test_contracts.py` (`regression-run` into `COMPARED_SLUGS`; its `ONE_SIDED_SLUGS` entry removed).
- Create: `docs/contracts/schemas/generated/regression-run.schema.json`.

**Interfaces:**
- `RegressionRun` (frozen, `extra="forbid"`) has:
  - `suite_ref: ArtifactRef`, `suite_content_hash: str`, `rating_version_ref: ArtifactRef` and `bundle_hash: str`;
  - `job_id: UUID | None`, `started_at` and `finished_at`;
  - `overall: Literal["pass", "fail"]`;
  - `generation: RunGeneration{seed: int, cases: int, hypothesis_version: str}` and `cases_blob: BlobRef`;
  - `golden_results: list[GoldenQuoteResult]` (S2's type);
  - `property_results: list[PropertyResult{name, status, cases_run, counterexample: dict | None, counterexample_minimal: bool, shrink: Literal["completed", "stopped_on_limit"] | None, error_code: str | None}]`.
- `RegressionGeneration.cases` gains `le=10_000`.
- `CasesLog` is `{"cases": [QuoteContext…], "counterexamples": {name: QuoteContext}}`, canonicalised as in `suite_content_hash`.

- [ ] **Step 1.** Write the failing model tests (round trip; `le` bound; `shrink` required on a `fail`). Expected: an `ImportError` on `RegressionRun`.
- [ ] **Step 2.** Implement, then generate. Following `contract-guard`, fix the authored side to the model. Run `uv run pytest backend/tests/test_contracts.py -q` until it passes, then commit.

### Task 3: `hypothesis` and `generate_contexts` — conditions 1, 2, 3, 5 and 6

**Files:**
- Modify: `packages/pricing-core/pyproject.toml` (`[project] dependencies`: `"hypothesis==6.165.7"`), `pyproject.toml:19` (the root dev entry aligned to `==6.165.7`, not removed), `uv.lock` (by `uv lock`) and `packages/pricing-core/src/pricing_core/rating/testing.py`.
- Create: `packages/pricing-core/tests/test_testing_determinism.py`.

**Interfaces:**
- `generate_contexts(contract: Sequence[InputContractField], n: int, seed: int, *, expect_version: str | None = None) -> list[QuoteContext]`. It is plain `def`, and it raises `GeneratorVersionMismatch(expected, actual)` when `expect_version` is given and differs from `hypothesis.__version__`.
- The generator runs its strategy under `@seed(seed)` and `@settings(database=None, deadline=None, report_multiple_bugs=False, derandomize=False, max_examples=n)`.

**Condition 5's mechanism, verified at the pin.** It was read to the function bodies of `hypothesis` 6.165.7 in the root `.venv`:
- The engine records its stop reason in `runner.statistics["stopped-because"]` through `exit_with` (`hypothesis/internal/conjecture/engine.py:1131-1134`), using `ExitReason.describe` (`:171-183`).
- `core.py:1427` hands `runner.statistics` to `hypothesis.statistics.note_statistics`, which calls `hypothesis.statistics.collector.value` if one is set (`statistics.py:22-28`).
- So `run_regression` wraps each property's execution in `with collector.with_value(stats.append):`.
- A shrink stopped on a limit is `stopped-because` equal to `ExitReason.very_slow_shrinking.value` ("shrinking was very slow", the `MAX_SHRINKING_SECONDS` deadline at `:1689` and `:766-770`) or to `ExitReason.max_shrinks` ("shrunk test case 500 times", `MAX_SHRINKS` at `:83`, `:764-765`).
- **`collector` is internal API.** The exact pin (condition 1) and the forced-limit test (acceptance item 6) keep it honest. An upgrade that moves it fails that test.

- [ ] **Step 1.** Pin, run `uv lock`, and record the `uv tree --package pricing-core` excerpt for the PR. Run `uv run lint-imports`.
- [ ] **Step 2.** Write the red tests for acceptance items 3, 4 and 6. Then write the determinism test for item 7: two `subprocess.run([sys.executable, "-c", …])` children generate from the same persisted seed and print the sha256 of the canonical case log and the counterexample; the parent asserts equality, and a no-seed pair asserts inequality.
- [ ] **Step 3.** Implement `generate_contexts` and the settings. Everything goes green. Commit.

### Task 4: `run_regression` and `replay_cases` — the five classes and condition 4

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/testing.py` and `packages/pricing-core/tests/test_testing.py`.

**Interfaces:** `run_regression(bundle, suite, *, seed) -> tuple[RegressionRun without persistence ids, CasesLog]`. It is plain `def` (RL-1172 item 3a). It does the following:
- validates every `monotone.input` against `bundle.algorithm.input_contract`, raising `ValueError` naming the input;
- calls `evaluate_golden_quotes` (S2);
- generates `suite.generation.cases` contexts;
- scores them through S2's `_score_context_sync`;
- evaluates each class:
  - `premium_positive`: the payable rung's `value_minor > 0` when `quoted`;
  - `monotone`: over contexts sorted by the input within `lower`/`upper`, with the payable premium non-decreasing or non-increasing, strictly when `strict`;
  - `no_null_output`: no `None` in `outputs`;
  - `ladder_reconciles`: per FR-248, reusing the existing reconciliation check;
  - `premium_bounded`: within `lower_minor`/`upper_minor`;
- shrinks a failing property through `hypothesis` to a counterexample, and records `shrink` and `counterexample_minimal`.

`replay_cases` **only re-scores** the persisted cases and counterexamples in a `CasesLog`. It **never shrinks, never calls `generate_contexts` and never imports or calls `hypothesis`** (audit R1). Its result reports each counterexample's `shrink` and `counterexample_minimal` exactly as persisted. A test patches `hypothesis` out of `sys.modules` for the call, and replay still passes.

- [ ] **Step 1.** Write red tests for acceptance items 5 and 8.
- [ ] **Step 2.** Implement, make them green, and commit.

### Task 5: The route, the Job, the row and the blob — DP-S3-3 and DP-S3-4

**Files:**
- Modify: `model_schema/jobs.py` (`JobKind` gains `REGRESSION_RUN`), the rating-version API module that holds `/compile` (`backend/src/app/api/models.py:1215`, a 202 Job), and the worker's job dispatch (`backend/src/app/worker/tasks.py:265`, `TASK_RUN_JOB`); `backend/src/app/errors.py` (`PROPERTY_ASSERTION_FAILED` into `RATING_ERROR_CODES`, with its raiser, below); `backend/src/app/db/models.py`; and a migration (`regression_runs`: `id`, `workspace_id`, `rating_version_id`, the `RegressionRun` fields as JSONB plus indexed `bundle_hash`, `suite_content_hash` and `overall`, `created_at`, `created_by`).
- Create: `backend/src/app/platform/regression_runs.py` and `backend/tests/test_regression_runs.py`.

**Behaviour:**
- The route requires `rating:compile` and enqueues a `REGRESSION_RUN` Job.
- The Job loads the bundle through S2's `_fetch_bundle` loader and the algorithm's current suite, then calls `run_regression` (sync, inside the worker).
- It writes the `CasesLog` to the blob store (DP-S3-4 (a)), whose key is the content hash.
- It persists the row.
- On `overall == "fail"` it finishes the Job `failed` with the problem from `PlatformError("PROPERTY_ASSERTION_FAILED" | "GOLDEN_QUOTE_MISMATCH", …, 409)`. **This is the raiser.**
- A read of the run and its blob requires `rating:read`.
- No log line carries a context (NFR-499).

- [ ] **Step 1.** Write red tests for acceptance items 5 (the blob's access) and 9, including the 403.
- [ ] **Step 2.** Implement and migrate (upgrade, downgrade, upgrade). Make them green and commit.

### Task 6: FR-257 limb (1) — DP-S3-1 and DP-S3-2

**Files:** Modify `backend/src/app/platform/rating_versions.py` (`submit_for_review`, after S2's golden-quote gate and before `approvals.submit`) and `backend/tests/test_rating_versions.py`.

**Behaviour:**
1. **DP-S3-1 (a).** If `evidence.golden_quotes` is `not_checked`, or its suite has zero golden quotes, raise `EVIDENCE_INCOMPLETE` ("a Regression Suite with at least one golden quote is required"), using the status `06` registers.
2. Find the **latest** `regression_runs` row for this Rating Version with `bundle_hash == row.bundle["content_hash"]` and `suite_content_hash ==` the pinned `evidence.golden_quotes.suite_content_hash` (DP-S3-2), ordered by `finished_at` then `id`. **That row must itself have `overall == "pass"`.** An earlier pass does not count once a later run on the same pair has failed (audit A1). If there is no such row, or the latest one failed, raise `EVIDENCE_INCOMPLETE`, naming which condition failed.
3. Set `evidence["regression_suite_run_id"]` to that run's id. **No other key of `evidence` is written.**

- [ ] **Step 1.** Write red tests for acceptance items 10 and 11. Each FR-257 test's docstring says "limb (1) only: a passing Regression Suite; limbs (2)–(4) are not tested here".
- [ ] **Step 2.** Implement and make them green. Confirm the existing no-suite path test changes only as DP-S3-1 dictates, and quote its old and new expectations in the ledger. Commit.

### Task 6b: Fixtures and the demo carry a golden quote (DP-S3-1)

- [ ] **Step 1.** Run acceptance item 11b's grep and record the list.
- [ ] **Step 2.** Add one shared test fixture, and one seed helper for the demo if the list includes a seed, that authors a suite for the algorithm with at least one golden quote and a passing run. Route every listed site through it. A site that must *not* have a suite, the refusal test itself, is named as the exception.
- [ ] **Step 3.** Run the listed tests and commit.

### Task 7: The gate and the ledger

- [ ] Run acceptance items 12 and 13: the two-half gate, the five-run repeat of `test_rating_score.py` with its stop rule, and the four docs checks on a detached copy. Record every rc and the `HEAD` in the slice's `LG-` ledger (its id comes from the lead). Record `git diff --stat origin/main...HEAD`, then open the PR.

---

## Self-review

1. **Coverage.** Each of RS-1176's six conditions maps to a task and an acceptance item:

   | Condition | Task | Acceptance item |
   |---|---|---|
   | 1 | Task 3 | 2 |
   | 2 | Task 3 | 3 |
   | 3 | Task 3 | 4 |
   | 4 | Task 4 | 5 |
   | 5 | Task 3 | 6 |
   | 6 | Task 3 | 7 |

   FR-261 is Tasks 1–5. FR-257 limb (1) is Task 6. Every `PL-1189` carry is listed under "Carried in".
2. **Literals checked at `e6a9ca71`:**
   - the `hypothesis` 6.165.7 pin (`uv.lock:914-915`) and the root dev entry (`pyproject.toml:19`);
   - `BlobRef` (`refs.py:138`) and `JobKind` (`jobs.py:39`);
   - `TASK_RUN_JOB` (`worker/tasks.py:265`) and the 202 compile route (`api/models.py:1215`);
   - the hypothesis internals (engine `:83`, `:171-183`, `:764-770`, `:1131-1134`, `:1689`; core `:1427`; statistics `:22-28`).

   The Slice 2 names come from `PL-1189` and are re-checked at Task 0 against the merged S2 code.
3. **Placeholders.** The migration's revision id and the ledger id are named as the executor's.
