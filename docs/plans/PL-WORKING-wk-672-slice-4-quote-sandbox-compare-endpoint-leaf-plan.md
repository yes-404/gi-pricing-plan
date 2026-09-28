---
id: PL-WORKING
family: plan
kind: leaf
title: WK-672 Slice 4 — Quote Sandbox compare endpoint (FR-262 backend limb): leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-28
owner: planner
tree: f91af639b70126765062395f213e648ea9a48b15
phase: P2
work: WK-672
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-930, PL-1189, PL-1205, RL-1172, RL-858, RL-917, FD-1197, FD-1199]
---

# WK-672 Slice 4 — Quote Sandbox compare endpoint (FR-262 backend limb): leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package` (Tasks 2–3), `python-test`, `fastapi-service` (Task 4) and `dev-commands` (the gate).

## Goal

Build the backend limb of FR-262, the Quote Sandbox: `POST /api/v1/score/compare` scores one Quote Context against two Rating Versions through two `score_one` calls and returns both results with a step-level diff of the two traces. No frontend (`RL-1172` item 5, DP1 = Option A).

**Architecture:** This is the leaf plan for Slice 4 of the map plan `PL-930`, the last slice of WK-672. It applies the deputy's DP1 decision as quoted in `RL-1172` §5:
- **No new evaluator.** The route calls `score_one` twice, each ending in the shared `build_scoring_result` tail (`RL-858`).
- **`pricing-core`** holds one pure function, `diff_traces`, which needs neither the database nor the network.
- **`model-schema`** holds the request, the diff and the response shapes (ADR-704: nobody hand-writes a shape).
- **The backend** holds the route only. It reuses `_compiled_for`, the bundle resolver `/score` uses (`RL-922`), and adds no second copy of it.

**Tech Stack:** Pydantic v2, FastAPI, pytest. No new dependency.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md):
- §3.8: FR-262 (`:179`), FR-258 (`:175`), FR-251 (`:163`);
- §4.4, §4.5 and a new §4.10;
- §5.1 (the `POST /api/v1/score/compare` row, `:706`);
- §5.2 (the `pricing_core/rating/` blocks);
- §9: NFR-499 (`:1062`), NFR-502 (`:1065`).

Line numbers are at `origin/main` `f91af639` (#870). Re-read them at the executor's tree.

## Status

**Draft 2026-09-28 21:04 BST (planner-s4); resolvers written 2026-09-28 (planner-s4, on the deputy's entry of 21:08:30 BST).** Filed at `f91af639`. DP-S4-1 to DP-S4-5 are all decided as recommended, with conditions, by the deputy's decision by delegation, quoted whole under "Decision points". The conditions are folded into Tasks 1, 3 and 5 and acceptance items 2, 5, 7. The plan stays `draft` and keeps the working id until the lead's freeze and mint turn.

**Where this plan differs from the map plan and the first scope note.**
- `PL-930:380` still carries the heading *"[BLOCKED on DP1]"* and cites `03` §5.1 at `:596`. Both are stale. DP1 is lifted (`RL-1172` §5, 2026-09-28 11:28:03 BST). The row is at `03:706` at `f91af639`, and `RL-1172`'s own correction of `:596`/`:597` to `:603` has itself drifted since.
- **The spec has a gap** (`CLAUDE.md` §0: a capability not yet specified is a spec change first). `03` §4 defines no compare request, no diff and no response. The §5.1 row names no permission, no status and no error code. Task 1 closes the gap and Task 2 puts the shapes in `model-schema`.
- **No new FR id is needed.** FR-262 already states the behaviour; the gap is in the data contract and the interface. A dated clarification on FR-262 records what WK-672 delivers. If the deputy rules that a new requirement is needed (for example a permission), its id is the code PR's to mint; Task 1 then uses the `Next free:` convention of `docs/plans/README.md`.

**Coordination with Slice 3 (`PL-1205`, branch `p2-d-s3`, not merged when this plan is filed).** Slice 4 uses nothing S3 adds. `PL-930` and `RL-1172` §6 order the slices one at a time, so the S4 executor starts after S3 merges. The shared files S3 also edits are `packages/model-schema/src/model_schema/__init__.py`, `scripts/generate-contracts.py`, `docs/contracts/openapi/generated.json`, `backend/tests/test_contracts.py` and `03` (§3.8, §4.9, §5.2, §8, NFR-499). Task 0 re-reads each at the executor's tree and merges `origin/main`. **If S3's shape changes,** this plan changes only in that those files conflict: S4's edits are additive (a new section §4.10, new names, a new `GENERATED_SHAPES` entry) and touch none of S3's names. Regenerate the contracts after any merge; never hand-merge `generated.json`.

## Acceptance Standard

Every command runs in the executor's worktree (`env -C <worktree> …`), over `origin/main...HEAD`. "Red first" means the failing run is quoted in the ledger with its failing assert line; a failure for another cause is a plan defect.

1. **Spec.** `03` changes as follows:
   - a new §4.10 declares the compare request, the response and the step diff, with a worked example;
   - the §5.1 row for `POST /api/v1/score/compare` names the permission, the status codes and the error codes (DP-S4-3, DP-S4-5);
   - §5.2 declares `diff_traces`;
   - FR-262 carries a dated clarification: WK-672 delivers the backend limb; the UI limb is reassigned to WK-675 (`RL-1172` §5's wording);
   - NFR-499's "FR-262's sandbox is inline" sentence is left unchanged and is now enforced by acceptance item 7.

   `python3 scripts/audit-docs.py` adds no failure row.
2. **The one-step proof, on the deputy's reading (DP-S4-2: "reported as the change").** `uv run pytest packages/pricing-core/tests/test_trace_diff.py -q` passes, and asserts on two hand-built fixtures:
   1. **Cascade fixture** (the edited step feeds a later step): exactly one entry has `own_change is True`, and it is the edited step.
   2. In that fixture every other entry has `own_change is False` **and** its `consumed` differs between the two sides.
   3. **No-downstream fixture** (the edited step feeds nothing that changes): `len(diff.steps) == 1`.
   4. **Mutation.** With `own_change` forced to `True` for every changed step, assertion 1 goes red; the failing assert line is quoted in the ledger. With `"produced"` dropped from the compared fields, the one-step tests go red too. Neither mutation is committed.

3. **The diff's shape is pinned.** The same file asserts, on hand-built traces:
   - identical traces give `steps == []` and `unchanged == len(steps)`;
   - `elapsed_us` never makes a step differ;
   - an added and a removed step are reported with the right `change`;
   - `1` and `1.0`, and `True` and `1`, are different values;
   - a duplicate `step_id` in one trace raises `ValueError`.
4. **One shape, one home.** `uv run python scripts/generate-contracts.py --check` exits 0. `docs/contracts/schemas/generated/score-comparison.schema.json` exists and is generated. `grep -rn 'class .*Comparison\|class TraceDiff\|class StepChange' backend/src packages/pricing-core/src` prints nothing (no shape is defined outside `model-schema`).
5. **The route.** `uv run pytest backend/tests/test_score_compare.py -q` passes, and each test is red first. It covers:
   - a 200 whose body carries both `ScoringResult`s, each traced, and the diff;
   - a 403 for a principal without the DP-S4-3 permission (and a 401 without a credential);
   - a 404 when either ref names no version, and the problem names which side;
   - a 409 `BUNDLE_COMPILE_FAILED` when either version is not compiled;
   - DP-S4-5 (a): when one side raises a per-quote code, a 422 carrying that code, whose problem names the failing side (`base` or `comparison`), asserted for each side;
   - a 422 when the context carries its own `options.rating_version_ref` (DP-S4-3);
   - two identical refs give an empty diff (the positive control).
6. **The one-step proof at the HTTP layer.** Two compiled versions built from the same algorithm, differing only in one step's rate table row, return a diff whose single `own_change` entry names that step. The test is red first.
7. **NFR-499: inline, nothing persisted, nothing logged.** With the trace sample rate set to `1.0`, a compare request leaves `scoring_traces` and `jobs` unchanged (row counts before and after are equal), and the route's logs carry no input value (a sentinel input value is absent from every `caplog` record). Both tests drive the **route** through the HTTP client, never the service function (a service-level `caplog` check passes vacuously, S2's G3 lesson, as the deputy's entry states it). The `caplog` test also asserts the capture is non-empty for the request, so an empty capture is not read as silence. Both tests are red first against a route that calls `_maybe_sample_trace`, which is the natural copy-paste from `/score`.
8. **No outbound validation** (NFR-502, `RL-883`). `grep -n 'response_model\|-> ScoreComparison' backend/src/app/api/score.py` prints nothing for the new route. The response is returned in a raw `Response`, as `/score` does.
9. **The route publishes its contract.** `docs/contracts/openapi/generated.json` lists `/api/v1/score/compare` with `problems(401, 403, 404, 409, 422)`, and `pnpm --dir frontend generate:api` succeeds and lists the operation. The frontend generated client is VCS-ignored and is not committed.
10. **The gate.**
    - The full two-half gate exits 0, with every rc and `HEAD` in the ledger.
    - `uv run pytest packages/pricing-core/tests/test_rating_score.py -q` runs **five times**, each rc recorded, because the route runs the real scoring path twice per request (`FD-1199`).
    - `uv run python scripts/req-coverage.py` shows an FR-262 row with the route tests attached, and the ledger types FR-262 as `RL-1172` §5 requires: *"backend limb delivered and tested (WK-672); UI limb reassigned to WK-675"*, not as delivered.
    - The four docs checks pass on a detached copy, with DISCLOSED no higher than main's.
    - `git diff --stat origin/main...HEAD` lists only the Files blocks' paths, the ledger and `docs/INDEX.md`.
11. **The deputy's merge acknowledgement is recorded** on the PR before the lead merges, and the slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and the lead's merge; no maintainer acceptance line is required for this slice. The Work close is a separate record and the maintainer's.

## Global Constraints

- **`pricing-core` stays standalone** (`CLAUDE.md` §2). `diff_traces` imports `model_schema` and the standard library only.
- **Nobody hand-writes a shape that exists in `model-schema`** (`CLAUDE.md` §2). The request, the diff and the response are declared there, and the frontend consumes the generated client.
- **Money is integer minor units** (`CLAUDE.md` §7, FR-273). Nothing here converts money.
- **No new evaluator** (`RL-1172` §5, the confirmed reading of "the one shared evaluator"). Two `score_one` calls, each ending in `build_scoring_result` (`RL-858`).
- **Inline, nothing persisted, nothing logged** (NFR-499 as clarified by `RL-917`: FR-262's sandbox needs no carve-out because it stores nothing). `/score` samples traces into `scoring_traces`; the new route must not.
- **Validate inbound, never outbound** (NFR-502 as amended by `RL-883`). No `response_model=`, no Pydantic return annotation.
- **The error boundary is the API module's.** `pricing-core` raises code-named `ValueError`; `_as_platform_error` maps it (`backend/src/app/api/score.py:241`).
- **The scoring path's threading is unchanged** (`FD-1199`). The two `score_one` calls run one after the other, never with `asyncio.gather`.
- **Permissions are not added.** Both candidate permissions exist (`rating:read`, `score:execute`; `model_schema/permissions.py:47,58`). The permission catalogue is `FD-1197`'s open finding, and this plan names its choice for that record.
- **A generated contract is never hand-edited** (`CLAUDE.md` §2). Regenerate with `scripts/generate-contracts.py`.

---

## Scope

**Requirements:**
- **FR-262** (`03` §3.8), backend limb: Tasks 1–5.
- **FR-258** (the trace shape): consumed, unchanged. The diff compares `TraceStep` fields.
- **FR-251** (explicit `rating_version_ref` for what-if and testing): consumed. Compare scores a `draft` version, as `/score` does (`RL-880` clause 3).
- **NFR-499** and **NFR-502**: enforced, Tasks 4–5.
- **FR-248, FR-273**: untouched, inherited from `build_scoring_result`.

**Carried out:**
- The Quote Sandbox view is WK-675's (`RL-1172` §5).
- The comparison "against live" of `WF-701` A5 is out of scope: `live` is a property of a Deployment (WK-674), and `_required_ref`'s refusal is permanent until then (`backend/src/app/api/score.py:114-134`). A5 is served today by naming the live version's ref explicitly as the comparison side.
- A Job-backed compare for a portfolio is FR-263's dislocation run, not this route.
- No frontend type is hand-written (`frontend/src/api/generated` is VCS-ignored).

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S4-1 | Where does the diff live? | (a) `diff_traces` is a pure function in `pricing-core`, and its result types are `model-schema` artifacts; (b) the diff is computed in the backend route module, and its types are `model-schema` artifacts; (c) both in the backend | (a): a pure, deterministic function of two traces belongs beside `score_one`. The regression executor and WK-675 can reuse it, and it is testable with hand-built traces and no database, which is what the broken-input proof needs. (b) buries a domain rule in an HTTP module; (c) hand-writes a shape the seam forbids | decision point | yes (Tasks 2, 3) | **(a)**: the deputy's decision by delegation, 2026-09-28 21:08:30 BST, quoted below. Condition: the result types are `model-schema` artifacts with the contracts regenerated, pricing-core's dependencies unchanged, and the names distinct from FR-219's structural diff |
| DP-S4-2 | How are steps matched, and what is "changed"? Sub-question: how does the diff treat a downstream step whose input moved because an upstream step changed? | Matching: (a) by `step_id`; (b) by position. Reporting, given (a): (i) every step whose `consumed`, `produced`, `matched`, `violation`, `type` or `label` differs, each marked `own_change`, true when it is added, removed, or changed with **identical** `consumed` (the step saw the same inputs and behaved differently), false when its `consumed` moved; (ii) only the `own_change` steps; (iii) every differing step, no marker | (a) with (i). `step_id` is the author-assigned id of the algorithm step (`score.py:668`, `step_meta` keyed on `step.step_id`), stable across versions of one algorithm; position breaks when a step is inserted. `elapsed_us` is recorded on each side but never compared. **(i) over (ii) and (iii):** a changed rate table changes every downstream step's `consumed`, so (iii) reports a cascade and cannot satisfy `RL-1172` §5's *"exactly that step is reported"* on its own, while (ii) hides how far the change reached. (i) reports the cascade and names the origin. **The deputy should confirm the reading of that acceptance sentence:** under (i), "exactly that step is reported" means exactly one entry has `own_change == True`. Acceptance items 2 and 6 assert that reading | decision point | yes (Tasks 2, 3) | **(a) with (i)**: the deputy's decision by delegation, 2026-09-28 21:08:30 BST, quoted below, with the reading of `RL-1172` "reported as the change" and four assertions (acceptance item 2) |
| DP-S4-3 | The request shape and the permission | Request: (a) `{"context": QuoteContext, "base": ArtifactRef, "comparison": ArtifactRef}`, with a validator refusing a `context` that carries its own `options.rating_version_ref`; (b) two `QuoteContext`s; (c) `context` plus a list of refs. Permission: (i) `rating:read`; (ii) `score:execute`; (iii) a new `score:compare` permission | Request: (a). FR-262 compares *one quote* across versions, so one context and two refs cannot drift into two different quotes, and a context ref that the route would silently overwrite is refused at validation (a 422) rather than ignored. Permission: **(i) `rating:read`, pending the permission-catalogue ruling `FD-1197` is waiting on.** No builtin role holds `score:execute` (`model_schema/permissions.py:58` is in no role set: `READ_PERMISSIONS` at `:83` and the Analyst set at `:113` omit it; `test_score.py:76-92` builds its "may set up but may not score" user on this fact), so (ii) would make the sandbox unusable by any human actuary; Analyst and Auditor hold `rating:read` (`permissions.py:83,113`). The cost of (i): an Auditor can then submit an ad hoc quote. Nothing is stored or logged (Task 5 proves it), so the read-only property FR-346 gives the Auditor holds. (iii) adds a permission with no catalogue ruling to place it | decision point | yes (Tasks 1, 2, 4) | **request (a), permission (i) `rating:read`**: the deputy's decision by delegation, 2026-09-28 21:08:30 BST, quoted below. Condition: the context is never persisted and never logged, proven by a route-level test |
| DP-S4-4 | Which versions may be compared, and how does the call answer? | (a) any compiled version, `draft` included; an uncompiled one answers 409 `BUNDLE_COMPILE_FAILED`; **200 synchronous**; `trace=True` on both calls; nothing persisted; (b) `approved` only; (c) a 202 Job | (a). FR-262 says "any accessible Rating Version", FR-251 allows what-if on a `draft`, and `RL-880` clause 3 says WK-671 has no environments to restrict on. The route reuses `_compiled_for`, which already raises the two 409s. Two `score_one` calls on one quote are inside `/score`'s own budget class (NFR-454's p99 is per call), so a Job (c) adds a store and an async poll for nothing, and a persisted result would need the NFR-499 requirement the spec says the sandbox does not have | decision point | yes (Task 4) | **(a)**: the deputy's decision by delegation, 2026-09-28 21:08:30 BST, quoted below |
| DP-S4-5 | When one side raises a per-quote error (`INPUT_CONTRACT_VIOLATION` and its siblings, FR-255) and the other does not, what does compare answer? | (a) the whole request answers 422 with the code, and the problem names the failing side; (b) 200, with an `error` entry in place of that side's result and no diff | (a). A step diff needs two traces, so (b) would need a partial response shape and a second wire form for the same field. The actuary who wants to see that version B rejects a quote version A accepts gets the code and the side from the problem. (b) is the better sandbox UX. It changes a 422 into a 200, so it is a breaking change if chosen later; the cost of (a) is that the choice is made now | decision point | no (Task 4 may proceed on (a); Task 1 records the answer) | **(a)**: the deputy's decision by delegation, 2026-09-28 21:08:30 BST, quoted below. Condition: the `03` §5.1 compare row states the 422-with-side behaviour in the same commit |

The deputy's entry, quoted whole from `channel/to-lead.md` (2026-09-28 21:08:30 BST, "WK-672 S4 DPs decided (#872 PL-WORKING, be988cdd)"):

```text
- DP-S4-1: (a). `diff_traces` is pure pricing-core, and its result types are model-schema artifacts (CLAUDE.md §2), with contracts regenerated. pricing-core keeps zero FastAPI or SQLAlchemy deps (lint-imports green). It is not FR-219's structural diff, so keep the names distinct.
- DP-S4-2: (a) with (i). The RL-1172 reading: "reported" means reported as the change. The broken-input proof asserts:
  1. exactly one entry with `own_change: true`, and it is the edited step;
  2. every other entry has `own_change: false`, and its `consumed` differs between the two sides (a downstream entry must be explained by a moved input, never listed without cause);
  3. a second fixture, where the edited step feeds nothing that changes, yields exactly one entry in total;
  4. a mutation that marks every differing step `own_change: true` turns (1) red.
- DP-S4-3: request (a), permission (i) `rating:read`, consistent with my RL-9204 ruling (#856: the code's coarse names are P2's record; the fine split goes to WK-676). Condition: the request `context` is never persisted and never logged, with a test in the NFR-499 form that drives the route, not the service. S2's G3 lesson was that a service-level caplog check passes vacuously.
- DP-S4-4: (a). Any compiled version, `draft` included; uncompiled answers the 409s; 200 sync; `trace=True`; nothing persisted.
- DP-S4-5: (a). 422 with the code, and the problem names the failing side (`base` or `comparison`). Condition: `03` §5.1's `POST /api/v1/score/compare` row states the 422-with-side behaviour in the same commit, so a later switch to (b) is visibly a breaking change.
- FR-262's typing at WK-672's close stays as RL-1172 fixed it: backend limb delivered and tested; UI limb reassigned to WK-675.
```

Task 0 stops the executor if any of these entries is missing from the record the lead names.

## Tasks

### Task 0: Preconditions

- [ ] **Step 1.** Confirm Slice 3's code PR is on `origin/main`. Use the **subject-line form and a symbol check, never a body grep** (`git log --grep` matches a plan's own commit body, as `PL-1205` Task 0 found): `git log origin/main --format=%s | grep -F '(#<S3 PR>)'` (the lead gives the number), and `test -f packages/pricing-core/src/pricing_core/rating/replay.py`. **If either fails, stop and report**: the slices run one at a time.
- [ ] **Step 2.** Confirm that DP-S4-1 to DP-S4-4 carry resolvers, and record DP-S4-5's. **If any is missing, stop and report.**
- [ ] **Step 3.** Merge `origin/main` (never rebase). Re-read, at your tree, the literals this plan cites: `score.py:110` (`ScoreExecuteDep`), `:114` (`_required_ref`), `:206` (`_compiled_for`), `:241` (`_as_platform_error`), `:258` (`/score`), `model_schema/scoring.py` (`Trace`, `TraceStep`, `ScoringResult`), and `03`'s §4.10 (which must not exist yet), §5.1 row and §5.2 blocks. Any drift is recorded in the ledger.

### Task 1: Spec — `03` §4.10, §5.1, §5.2, FR-262

**Files:** Modify `docs/specs/03-rating-engine.md`.

- [ ] **Step 1, §4.10 `ScoreComparison`.** Add a section after §4.9 (S3's section) with:
  - the request, per DP-S4-3: `{"context": <QuoteContext without options.rating_version_ref>, "base": "rating_version:motor-gb@27", "comparison": "rating_version:motor-gb@28"}`;
  - the response, `{"base": <ScoringResult>, "comparison": <ScoringResult>, "diff": {"steps": [...], "unchanged": 11}}`, both results traced;
  - a worked `diff.steps` entry with `step_id`, `change` (`added` | `removed` | `changed`), `changed_fields` (a subset of `type`, `label`, `consumed`, `produced`, `matched`, `violation`), `own_change` and both `TraceStep`s (`null` on the missing side);
  - the prose rules of DP-S4-2: steps match by `step_id`; `elapsed_us` is recorded and never compared; values compare as canonical JSON, so `1` and `1.0` differ; `steps` lists base steps in base order, then added steps in comparison order.
- [ ] **Step 2, §5.1.** Replace the row's text with the permission (DP-S4-3), the status codes (200; 401; 403; 404; 409 `BUNDLE_COMPILE_FAILED`; 422 with FR-255's per-quote codes or a context carrying its own ref) *"nothing is persisted or logged (NFR-499)"*, and the DP-S4-5 (a) behaviour verbatim in substance: *"a per-quote error on either side answers 422 with that code, and the problem names the failing side (`base` or `comparison`)"*, marked `**Amended 2026-09-28**`. The deputy's condition: this wording lands in the same commit as the route, so a later switch to a 200 with a partial result is visibly a breaking change. Task 1 is therefore committed with Tasks 4 and 5, not before them.
- [ ] **Step 3, §5.2.** Add to the `pricing_core/rating/` blocks: `def diff_traces(base: Trace, comparison: Trace) -> TraceDiff` in `trace_diff.py`, dated.
- [ ] **Step 4, FR-262.** Add a dated clarification, with no new id: *"(Clarified 2026-09-28, WK-672 Slice 4, `RL-1172` §5.) The endpoint `POST /api/v1/score/compare` delivers the backend limb: two `score_one` calls and a step-level trace diff, no new evaluator. The Quote Sandbox view is WK-675's."*
- [ ] **Step 5.** Run `python3 scripts/audit-docs.py` (no new failure row). The commit is the slice's one code PR commit: spec, code, tests and the regenerated contracts land together (`CLAUDE.md` §2).

### Task 2: `model-schema` — the shapes and the contract

**Files:**
- Modify: `packages/model-schema/src/model_schema/scoring.py` (after `ScoringResult`), `packages/model-schema/src/model_schema/__init__.py`, `scripts/generate-contracts.py` (`GENERATED_SHAPES`), `backend/tests/test_contracts.py` if the guard needs a scope line.
- Create: `packages/model-schema/tests/test_scoring_compare.py`; generated `docs/contracts/schemas/generated/score-comparison.schema.json` (by the script).

**Interfaces:**
- Produces: `ScoreCompareRequest(context: QuoteContext, base: ArtifactRef, comparison: ArtifactRef)`; `StepChange`; `TraceDiff(steps: list[StepChange], unchanged: int)`; `ScoreComparison(base: ScoringResult, comparison: ScoringResult, diff: TraceDiff)`. All `frozen=True, extra="forbid"`. The names stay distinct from FR-219's structural diff (`AlgorithmDiff`, `model_schema/rating.py:539`): `TraceDiff` and `StepChange` describe two executed traces, not two algorithm definitions. `uv run lint-imports` stays green and `packages/pricing-core/pyproject.toml` gains no dependency.

```python
StepChangeKind = Literal["added", "removed", "changed"]
TraceStepField = Literal["type", "label", "consumed", "produced", "matched", "violation"]


class StepChange(BaseModel):
    """One step that differs between two Traces (FR-262, `03` §4.10). `own_change` is true
    when the step was added, removed, or changed while consuming identical inputs: the
    step itself, not a value flowing into it, differs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str
    change: StepChangeKind
    changed_fields: list[TraceStepField] = Field(default_factory=list)
    own_change: bool
    base: TraceStep | None = None
    comparison: TraceStep | None = None


class TraceDiff(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    steps: list[StepChange]
    unchanged: int = Field(ge=0)


class ScoreCompareRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    context: QuoteContext
    base: ArtifactRef
    comparison: ArtifactRef

    @model_validator(mode="after")
    def _context_names_no_version(self) -> Self:
        options = self.context.options
        if options is not None and options.rating_version_ref is not None:
            raise ValueError(
                "context.options.rating_version_ref must be omitted: "
                "`base` and `comparison` name the two versions"
            )
        return self


class ScoreComparison(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    base: ScoringResult
    comparison: ScoringResult
    diff: TraceDiff
```

- [ ] **Step 1.** Write the failing tests in `test_scoring_compare.py`: a request carrying `options.rating_version_ref` is refused; `extra="forbid"` refuses an unknown key; a `StepChange` with `change="changed"` round-trips through `model_dump_json`/`model_validate_json`. Run: `uv run pytest packages/model-schema/tests/test_scoring_compare.py -q`. Expected: FAIL with an `ImportError` naming `ScoreCompareRequest`.
- [ ] **Step 2.** Add the classes, export them in `__init__.py` and add `"score-comparison": "ScoreComparison"` to `GENERATED_SHAPES` with the dated comment its neighbours carry (*no hand-authored Phase-0 counterpart; `03` §4.10 is the shape's first written form*), the precedent being `model-comparison` and `dataset-lineage`. Run the tests: PASS.
- [ ] **Step 3.** Run `uv run python scripts/generate-contracts.py`, then `--check` (rc 0) and `uv run pytest backend/tests/test_contracts.py -q`. Follow `contract-guard` if a walker asks for a scope line. The OpenAPI document gains the route only in Task 4; commit this step's generated schema now.
- [ ] **Step 4.** Commit.

### Task 3: `diff_traces` — TDD, with the one-step proof

**Files:**
- Create: `packages/pricing-core/src/pricing_core/rating/trace_diff.py`, `packages/pricing-core/tests/test_trace_diff.py`.

**Interfaces:**
- Consumes: `Trace`, `TraceStep`, `TraceDiff`, `StepChange` from `model_schema` (Task 2).
- Produces: `diff_traces(base: Trace, comparison: Trace) -> TraceDiff`, deterministic and pure.

- [ ] **Step 1.** Write the failing tests, with a `_step(step_id, **overrides)` and a `_trace(*steps)` helper that build `TraceStep`s and a `Trace` with a fixed hash. Include:

```python
def test_a_change_to_one_steps_own_definition_is_the_one_own_change() -> None:
    # s_area is unchanged; s_rate consumed the same input and produced a different value;
    # s_total consumed the moved value and so differs only by propagation.
    base = _trace(_step("s_area"), _step("s_rate", produced={"r": 1}), _step("s_total", consumed={"r": 1}))
    other = _trace(_step("s_area"), _step("s_rate", produced={"r": 2}), _step("s_total", consumed={"r": 2}))
    diff = diff_traces(base, other)
    own = [c.step_id for c in diff.steps if c.own_change]
    assert own == ["s_rate"]  # assertion 1: exactly one own change, the edited step
    assert [c.step_id for c in diff.steps] == ["s_rate", "s_total"]
    for change in diff.steps:  # assertion 2: every other entry is explained by a moved input
        if not change.own_change:
            assert "consumed" in change.changed_fields
            assert change.base is not None and change.comparison is not None
            assert change.base.consumed != change.comparison.consumed
    assert diff.unchanged == 1


def test_an_edit_that_feeds_nothing_that_changes_is_the_only_entry() -> None:
    # assertion 3: s_rate's produced value changes but s_total's consumed dict does not
    # carry it, so nothing downstream differs.
    base = _trace(_step("s_area"), _step("s_rate", produced={"r": 1}), _step("s_total", consumed={"q": 5}))
    other = _trace(_step("s_area"), _step("s_rate", produced={"r": 2}), _step("s_total", consumed={"q": 5}))
    diff = diff_traces(base, other)
    assert [c.step_id for c in diff.steps] == ["s_rate"]


def test_elapsed_time_never_makes_a_step_differ() -> None:
    assert diff_traces(_trace(_step("a", elapsed_us=1)), _trace(_step("a", elapsed_us=900))).steps == []


@pytest.mark.parametrize(("left", "right"), [(1, 1.0), (True, 1), (0, False)])
def test_one_and_one_point_zero_and_true_are_different_values(left: object, right: object) -> None:
    diff = diff_traces(_trace(_step("a", produced={"v": left})), _trace(_step("a", produced={"v": right})))
    assert [(c.change, c.changed_fields) for c in diff.steps] == [("changed", ["produced"])]


def test_an_added_and_a_removed_step_are_reported_with_their_kind() -> None:
    diff = diff_traces(_trace(_step("gone"), _step("kept")), _trace(_step("kept"), _step("new")))
    assert [(c.step_id, c.change, c.own_change) for c in diff.steps] == [
        ("gone", "removed", True),
        ("new", "added", True),
    ]
    assert diff.unchanged == 1


def test_identical_traces_have_an_empty_diff() -> None:
    trace = _trace(_step("a"), _step("b"))
    assert diff_traces(trace, trace) == TraceDiff(steps=[], unchanged=2)


def test_a_duplicate_step_id_in_one_trace_is_refused() -> None:
    with pytest.raises(ValueError, match="duplicate step_id"):
        diff_traces(_trace(_step("a"), _step("a")), _trace(_step("a")))
```

  Run: `uv run pytest packages/pricing-core/tests/test_trace_diff.py -q`. Expected: FAIL with `ModuleNotFoundError` for `pricing_core.rating.trace_diff` (the cause, not the status). The helpers `_step` (a `TraceStep` with `type="expression"` and the given overrides) and `_trace` (a `Trace` with a fixed `sha256:` hash of 64 `a`s, `ladder_reconciled=True`) sit at the top of the file.
- [ ] **Step 2.** Implement:

```python
_COMPARED: Final[tuple[TraceStepField, ...]] = (
    "type", "label", "consumed", "produced", "matched", "violation",
)


def _canonical(value: object) -> str:
    """Canonical JSON, so `1`, `1.0` and `True` are three different values."""
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))


def _by_id(trace: Trace) -> dict[str, TraceStep]:
    steps: dict[str, TraceStep] = {}
    for step in trace.steps:
        if step.step_id in steps:
            raise ValueError(f"duplicate step_id {step.step_id!r} in one trace")
        steps[step.step_id] = step
    return steps


def diff_traces(base: Trace, comparison: Trace) -> TraceDiff:
    base_steps, other_steps = _by_id(base), _by_id(comparison)
    changes: list[StepChange] = []
    unchanged = 0
    for step_id, before in base_steps.items():
        after = other_steps.get(step_id)
        if after is None:
            changes.append(StepChange(step_id=step_id, change="removed", own_change=True, base=before))
            continue
        fields = [f for f in _COMPARED if _canonical(getattr(before, f)) != _canonical(getattr(after, f))]
        if not fields:
            unchanged += 1
            continue
        changes.append(StepChange(
            step_id=step_id, change="changed", changed_fields=fields,
            own_change="consumed" not in fields, base=before, comparison=after,
        ))
    changes.extend(
        StepChange(step_id=step_id, change="added", own_change=True, comparison=after)
        for step_id, after in other_steps.items() if step_id not in base_steps
    )
    return TraceDiff(steps=changes, unchanged=unchanged)
```

  Add `__all__ = ["diff_traces"]`. Run: PASS.
- [ ] **Step 3, the broken-input proofs (acceptance item 2, assertion 4).** Two mutations, each run, quoted and reverted; neither is committed.
  1. Force `own_change=True` on every `changed` `StepChange`. The cascade test's assertion 1 must go red (`assert own == ["s_rate"]` fails with both steps listed).
  2. Drop `"produced"` from `_COMPARED`. The one-step tests and the one-and-one-point-zero test must go red.
  Restore and run green.
- [ ] **Step 4.** `uv run mypy` and `uv run lint-imports` (no forbidden import: the module imports `json`, `typing` and `model_schema`). Commit.

### Task 4: The route

**Files:** Modify `backend/src/app/api/score.py` (a new `RatingReadDep`-style dependency and the route, after `/score`); `docs/contracts/openapi/generated.json` (generated).

**Interfaces:**
- Consumes: `_compiled_for` (`score.py:206`), `_as_platform_error` (`:241`), `score_one`, `diff_traces` (Task 3), `ScoreCompareRequest`, `ScoreComparison` (Task 2).
- Produces: `POST /api/v1/score/compare`, 200 with a raw `Response`.

```python
RatingReadDep = Annotated[Caller, Depends(requires(Permission.RATING_READ))]  # DP-S4-3 (i)


@router.post(
    "/score/compare",
    summary="Score one Quote Context against two Rating Versions, with a step-level diff",
    status_code=200,
    responses=problems(401, 403, 404, 409, 422),
)
async def score_compare(
    body: ScoreCompareRequest,
    caller: RatingReadDep,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
    slot: BundleSlotDep,
) -> Response:
    """FR-262: one quote, two versions, two `score_one` calls, one step diff. Nothing is persisted
    or logged (NFR-499): this route never calls `_maybe_sample_trace`."""
    results: list[ScoringResult] = []
    for side, ref in (("base", body.base), ("comparison", body.comparison)):
        compiled = await _compiled_for(database, blob_store, slot, workspace_id=caller.workspace_id, ref=ref)
        ctx = body.context.model_copy(update={"options": QuoteContextOptions(trace=True, rating_version_ref=ref)})
        try:
            results.append(await score_one(compiled, ctx, trace=True))
        except ValueError as exc:
            problem = _as_platform_error(exc)
            if problem is None:
                raise
            raise _naming_side(problem, side) from exc
    base_result, comparison_result = results
    if base_result.trace is None or comparison_result.trace is None:
        raise RuntimeError("score_one(trace=True) returned no trace")
    comparison = ScoreComparison(
        base=base_result, comparison=comparison_result,
        diff=diff_traces(base_result.trace, comparison_result.trace),
    )
    return Response(content=comparison.model_dump_json(), media_type="application/json")
```

`_naming_side(problem, side)` returns a `PlatformError` with the same code and status and a `detail` prefixed `"{side}: "`. A 404 or 409 from `_compiled_for` names its side the same way: wrap the `_compiled_for` call and re-raise through the same helper. Sequential, never `asyncio.gather` (`FD-1199`). Verify every name above against the tree at Task 0 (`QuoteContextOptions` is `model_schema.scoring`'s; `problems` is imported already).

- [ ] **Step 1.** Write the red route tests (Task 5's file, first test only): a 200 with both results. Run `uv run pytest backend/tests/test_score_compare.py -q -k returns_both`. Expected: FAIL with a 404 for the unrouted path, which is the cause (no route), not a wrong body.
- [ ] **Step 2.** Implement the route and the helper. Run it: PASS.
- [ ] **Step 3.** Run `uv run python scripts/generate-contracts.py`, then `--check` (rc 0). Commit with Task 5's tests.

### Task 5: Route tests — 403/404/409/422, the one-step proof, NFR-499

**Files:** Create `backend/tests/test_score_compare.py`. Reuse the fixtures of `backend/tests/test_score.py` (`_compiled`, `_insert_version`, `_minimal_algorithm`, `_run_compile_job`, `_set_trace_sample_rate`, `_rows_for`, `_trace_produce_jobs`; verify the names at your tree).

- [ ] **Step 1.** Write a fixture that compiles two versions of one algorithm that differ in exactly one step (one rate-table cell), plus one uncompiled version. **If the existing helpers cannot produce two versions differing in one step, stop and report** (a plan defect), rather than hand-building a bundle.
- [ ] **Step 2.** Write each test of acceptance items 5, 6 and 7, each with its own docstring naming the requirement (`req("FR-262")`; `req("NFR-499")` for item 7), and each red first:
  - the 200 with two traced results and a diff whose single `own_change` entry names the differing step;
  - identical refs give `steps == []`;
  - no permission gives 403 and no credential 401; a ref naming no version gives 404 naming the side; an uncompiled version gives 409 `BUNDLE_COMPILE_FAILED`;
  - a context violating one version's input contract gives 422 with the per-quote code and the side (DP-S4-5 (a));
  - a context carrying `options.rating_version_ref` gives 422;
  - with `_set_trace_sample_rate(..., 1.0)`, `scoring_traces` and `jobs` row counts are equal before and after the call, driven through the HTTP client (the deputy's DP-S4-3 condition: the route, not the service);
  - a sentinel input value (for example `"ZZ99 9ZZ"`) appears in no `caplog` record at `DEBUG` across the HTTP call, and the same capture is shown non-empty for that call (so silence is not vacuous, S2's G3 lesson, as the deputy's entry states it);
  - the 422 tests assert the problem names `base` or `comparison` for each side.
- [ ] **Step 3.** Run: `uv run pytest backend/tests/test_score_compare.py -q`. Show the two NFR-499 tests red once against a route that calls `_maybe_sample_trace`, quote the failing assert lines, then revert. Commit.

### Task 6: The gate and the ledger

- [ ] Run acceptance items 9 and 10: `pnpm --dir frontend generate:api` and the rest of the two-half gate, the five-run repeat of `test_rating_score.py` with its stop rule (a native abort moves `FD-1199`'s triage ahead of the slice), `uv run python scripts/req-coverage.py` for FR-262, and the four docs checks on a detached copy. Record every rc and the `HEAD` in the slice's `LG-` ledger (its id comes from the lead), record `git diff --stat origin/main...HEAD`, then open the PR.

---

## Self-review

1. **Spec coverage.**

   | Source | Clause | Task |
   |---|---|---|
   | FR-262 | score against any accessible version, full trace inline | Tasks 4, 5 (item 5) |
   | FR-262 | comparison version with a step-by-step difference | Tasks 2, 3 (items 2, 3, 6) |
   | `RL-1172` §5 | backend limb, no frontend, shape tests, broken-input proof | Tasks 3, 5 (items 2, 3, 6) |
   | `RL-1172` §5 | UI limb reassigned; FR-262 typed "backend limb delivered and tested" | Task 6 (item 10) |
   | `RL-1172` §5 | two `score_one` calls, no new evaluator | Task 4 |
   | FR-258 | trace shape consumed | Task 3 |
   | NFR-499, `RL-917` | inline, nothing persisted or logged | Task 5 (item 7) |
   | NFR-502, `RL-883` | no outbound validation | Task 4 (item 8) |
   | `03` §4 / §5.1 gap | shapes, permission, status, errors | Tasks 1, 2 |

2. **Literals checked at `f91af639`:** `score.py:110` `ScoreExecuteDep`, `:114` `_required_ref`, `:206` `_compiled_for`, `:241` `_as_platform_error`, `:258` `/score`; `model_schema/scoring.py` `TraceStep`, `Trace`, `ScoringResult`; `permissions.py:47` `RATING_READ`, `:58` `SCORE_EXECUTE`, `:83,113` the roles holding `rating:read`; `test_contracts.py` `COMPARED_SLUGS`/`ONE_SIDED_SLUGS`; `generate-contracts.py` `GENERATED_SHAPES` (the `model-comparison` precedent); `03:175,179,706,1062,1065`; `FD-1199`, `FD-1197` exist. The test helper names in Task 5 come from `test_score.py` and are re-checked at Task 0.
3. **Placeholders.** The ledger id and the S3 PR number are the lead's. Task 3 shows every test body. Task 5 names each route test by its assertion and cause; its bodies follow `test_score.py`'s fixtures, which the executor reads at Task 0.
4. **Open risks the plan does not resolve.** (i) DP-S4-2's reading of "exactly that step is reported". (ii) `rating:read` as the permission rests on a catalogue `FD-1197` has not ruled. (iii) Whether the existing fixtures can build a one-step-different pair is Task 5 Step 1's stop condition.
