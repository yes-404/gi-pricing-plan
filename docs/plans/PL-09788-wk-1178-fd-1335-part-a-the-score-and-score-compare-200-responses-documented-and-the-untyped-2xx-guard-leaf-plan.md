---
id: PL-9788
family: plan
kind: leaf
title: WK-1178 slice — FD-1335 Part A, the /score and /score/compare 200 responses documented, and the untyped-2xx guard (FR-250, FR-262, FR-451, NFR-502): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-01
owner: planner
tree: 9b0fb97c9ed1cea743639897351191bc1a862041
phase: P2
work: WK-1178
slice: SL-9787
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1335, RL-1343, RL-1263, RL-883, PL-1348, SL-1345, PL-1286, PL-1299]
---

# PL-9788 — WK-1178 slice — FD-1335 Part A: the `/score` and `/score/compare` 200 responses documented, and the untyped-2xx guard: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `contract-guard` (Tasks 1–2), `contract-schema` (Task 3's regeneration), `fastapi-service` (Task 3), `python-test` (every task: requirement markers, negative tests), `test-driven-development` (every red-first step), `spec-change` (Task 4, only if DP-A1 is ruled (b)), `performance-engineer`'s discipline for Task 5 (a measurement, never an estimate), and `dev-commands` (the gate and the gate slot). It reads [`README.md`](README.md)'s five unchecked conventions before its first step. The executor is spawned from `.claude/roles/executor.md`, whose Model / effort line it quotes verbatim.

## Goal

Give the one-way contract (`CLAUDE.md` §2) a shape for the two scoring responses that carry a
premium. `POST /api/v1/score` documents its 200 as `$ref ScoringResult` and
`POST /api/v1/score/compare` documents its 200 as `$ref ScoreComparison`, with **no outbound
validation** (`NFR-502`). A contract guard then fails on any JSON 2xx response that is `{}` or an
object with no `properties`, from the day it lands.

**Architecture.** This is `FD-1335`'s **Part A** (*Disposition*, items 1–3). Two route decorators
in `backend/src/app/api/score.py` gain `200: {"model": …}` in their `responses=` mapping, beside
the `problems(…)` entries. The handlers keep their raw `Response` and stay without
`response_model=` and without a return annotation. FastAPI builds a documented response from
`responses=` at OpenAPI time only, so the request path does not change. `FD-1335` Evidence §2
measured this in a scratch app: the schema becomes a `$ref`, and a non-conforming body still
answers 200. `scripts/generate-contracts.py` regenerates `docs/contracts/openapi/generated.json`
(`FR-451`). `backend/tests/test_contracts.py` gains the untyped-2xx guard. It uses `FD-1335`
Evidence §1's two predicates verbatim, with an exact exclusion list in two parts: four permanent
entries and twelve temporary entries marked `pending FD-1335 part B`. Each form is shown red
first. `NFR-502` is measured again in a solo window (Task 5).

**Tech stack.** FastAPI and Pydantic v2 (the pinned versions in `uv.lock`), pytest, and
`openapi-typescript` through `pnpm --dir frontend generate:api` for the client evidence.

**Spec.** [`../findings/FD-01335-the-score-200-response-has-no-schema-in-the-generated-openapi-so-the-one-way-contract-cannot-type-it.md`](../findings/FD-01335-the-score-200-response-has-no-schema-in-the-generated-openapi-so-the-one-way-contract-cannot-type-it.md)
(*Disposition*, Part A), `03` FR-250, FR-262 and NFR-502
([`../specs/03-rating-engine.md`](../specs/03-rating-engine.md)), `07` FR-451
([`../specs/07-platform.md`](../specs/07-platform.md)), and `RL-1343` §5
([`../rulings/RL-01343-oq-1334-decided-a-declared-decimal-output-is-served-on-every-scoring-path-as-an-exact-decimal-string-rounded-once.md`](../rulings/RL-01343-oq-1334-decided-a-declared-decimal-output-is-served-on-every-scoring-path-as-an-exact-decimal-string-rounded-once.md)).

## Status

Filed 2026-10-01 against the tree above (`origin/main` `9b0fb97c`), under **working id 9788**
(this plan) and **working id 9787** (its slice row `SL-9787` under `### WK-1178` in
`docs/roadmap.md`). The lead allocated both ids. The lead is the only allocator (`FD-1338`). Both
are minted at this PR's merge turn, and each citation of a working id is then re-pointed.

**`draft`.** The plan stays `draft` while DP-A1 to DP-A4 are open and while `SL-1345` has not
merged. It turns `active` only when every activation need below is met. The dispatch record
shows each need by its command, run at a named `origin/main` SHA.

### Sequencing: after `SL-1345` merges (decided by the lead, recorded here)

**Part A is serialised after WK-674's ladder slice `SL-1345` (`PL-1348`) merges.** The lead
decided this on the evidence below. The planner records it and does not decide it
(`delivery-process.md` §3).

- **The same existing definition, in a file that is not registry-exempt.** `PL-1348`'s write set
  (`PL-1348:525-590`, the `backend/src/app/api/score.py` row) edits "the explicit 500 mapping on
  `/score` and `/score/compare`, the `ERROR` log line, the OpenAPI `responses`". `RL-1346` adds
  `LADDER_RECONCILIATION_FAILED` as a **500** from `/score` and from `/score/compare`
  (`03:815`). So `PL-1348` changes the `responses=problems(401, 403, 404, 409, 422)` argument on
  the **same two decorators** (`score.py:276-286` and `:330-335` at `9b0fb97c`) that Part A
  changes. `score.py` is not on `RL-1263`'s closed registry list (`RL-1263:104-116`: only
  `backend/migrations/versions/`, `docs/contracts/openapi/generated.json`,
  `docs/contracts/schemas/generated/` and `docs/INDEX.md`). "Any other shared path serialises"
  (`RL-1263`, the same block).
- **The contract must document the post-ladder rung shape.** `PL-1348` changes
  `model_schema/scoring.py`'s `LadderOperationKind`, `LadderOperation`, `LadderRung` and
  `Trace.ladder_check_version` (its write-set row). Part A does **not** edit `scoring.py`. But
  its `$ref` publishes whatever `ScoringResult` holds at Part A's base. If Part A landed first,
  WK-675's Quote Sandbox would be typed first against the pre-ladder rung and then re-typed. If
  Part A lands after, the first generated client already carries the exact rungs (Acceptance 6).
- **`SL-1345` is already `active`, and Part A is not.** Serialising Part A behind it reworks
  nothing that is in flight.
- **`RL-1343` §5 does not contradict this.** "Part A does not wait for this ruling or for
  Slice 3" says there is no **logical** dependency on rule 4 or on Slice 3's content. The order
  here comes from `RL-1263`'s file rule, which applies on its own terms. `RL-1343`'s timing
  condition still holds. Part A lands before a WK-675 slice that consumes `/score` or
  `/score/compare` dispatches (`FD-1335` *Disposition* item 1). In `PL-1286`'s order
  (S1 → S2 → S3 → S4 → S13 → S14 → S5 → S6 → …, `PL-1286` §Sequencing), the first such slice
  is S6, the eighth.
- **The `NFR-502` timing run needs a solo window.** It cannot share a window with `SL-1345`'s
  `scripts/bench-rating.py` run (`PL-1348` Acceptance 9, "in a solo window (`RL-1263` item 3)")
  or with any other measurement or suite (`delivery-process.md` §8, amended 2026-09-29: "a
  measurement step runs alone"). Serialising after `SL-1345` gives that by construction for
  `SL-1345`. Task 5 checks every other holder.

### Activation needs, in order

Run them from any checkout after `git fetch -q origin`. The SHA recorded is
`M=$(git rev-parse origin/main)`. **A need with no pasted output in the dispatch record is
unmet.** The lead's GO check starts here, before anything else.

1. **`SL-1345` has merged to `main`:**
   ```bash
   S=$(git log -n1 --format=%H -E --grep='^(feat|fix)\([^)]*\): SL-1345 ' "$M"); echo "squash=${S:-NONE}"; test -n "$S" && git merge-base --is-ancestor "$S" "$M" && echo MET
   ```
   Expected: `squash=<a 40-hex SHA>` and then `MET`. `squash=NONE`, or no `MET`, is **unmet**.
   The dispatch record names that SHA. It is Part A's minimum base.
2. **The post-ladder rung shape is on `main`, and `SL-1345` did not already type the 200:**
   ```bash
   git diff 9b0fb97c9ed1cea743639897351191bc1a862041 "$M" --stat -- packages/model-schema/src/model_schema/scoring.py
   git show "$M":backend/src/app/api/score.py | grep -c '200: {"model"'
   ```
   Expected: the first prints one changed-file line for `scoring.py`, which is `SL-1345`'s rung
   change. The second prints `0`. A `1` or `2` means another change already added a 200 model.
   That is a stop, reported to the lead, because Tasks 2–3 would then be partly done.
3. **The finding's premise still holds on `main`:** the same 18 untyped 2xx responses that the
   exclusion lists name.
   ```bash
   T=$(mktemp -d); git show "$M":docs/findings/FD-01335-the-score-200-response-has-no-schema-in-the-generated-openapi-so-the-one-way-contract-cannot-type-it.md | awk '/^```python$/{f=1;next} f&&/^```$/{exit} f' > "$T/sweep.py"; sha256sum "$T/sweep.py" | cut -c1-16; git show "$M":docs/contracts/openapi/generated.json > "$T/g.json"; python3 "$T/sweep.py" "$T/g.json"
   ```
   Expected: the hash prefix `4574b64f1293849b` (the FD's own), then `form1_empty_schema=6`
   listing exactly the six form-1 routes of **Task 2**'s two lists, `form2_object_without_properties=12`
   listing exactly the twelve, and `total_untyped=18`. At `9b0fb97c` this printed `paths=120
   responses_2xx=141` and that exact listing. A different listing means the exclusion lists below
   are stale: **unmet** until the planner files a dated delta in the dispatch record.
4. **This plan and its slice row are minted on `main`:**
   ```bash
   git grep -l -E '^title: WK-1178 slice — FD-1335 Part A' "$M" -- docs/plans/
   git show "$M":docs/roadmap.md | grep -E '^#### SL-[0-9]+ — WK-1178 slice — FD-1335 Part A'
   ```
   Expected: exactly one path, where `basename <path> | cut -c4-8` prints a number below `09000`;
   and exactly one heading whose `SL-` number is below `9000`. `09788` or `SL-9787` is the
   working-id draft: **unmet**.
5. **DP-A1 and DP-A2 are ruled and minted** (the decision-maker's):
   ```bash
   git grep -l --all-match -e 'FD-1335' -e 'DP-A1' -e 'DP-A2' "$M" -- docs/rulings/
   ```
   Expected: exactly one path whose 5-digit id is below `09000`. Where the ruling and a task
   below differ, **the ruling wins**, and the dispatch record names each difference.
6. **DP-A3 and DP-A4 are resolved by the lead**, in the dispatch record (a local file under
   `~/gi-pricing-plan.local/handover/`):
   ```bash
   grep -n -E '^(DP-A3|DP-A4): ' <the dispatch record's path>
   ```
   Expected: two lines, each naming the option taken. If DP-A3 is ruled (b) (fold `RL-1343`'s
   rule 4 into this slice), **this plan is superseded** by a new `PL-` that carries both, and
   nothing below is dispatched.
7. **The status flip has merged, and the lead has given the go:**
   ```bash
   P=$(git grep -l -E '^title: WK-1178 slice — FD-1335 Part A' "$M" -- docs/plans/ | sed 's/^[^:]*://'); git show "$M":"$P" | grep -m1 '^status:'
   git show "$M":docs/roadmap.md | awk '/^#### SL-[0-9]+ — WK-1178 slice — FD-1335 Part A/{f=1} f && /^status:/{print; exit}'
   ```
   Expected: both lines begin `status: active`. Then the lead's go is dated in the dispatch
   record.

### Build-start conditions (Task 0, after activation; not activation needs)

- **A free lane under `RL-1263`:** at most two build slices at once, from different Works, each
  holding a gate slot, with no shared file outside the registry list. The **File contention**
  section below gives the check against every planned slice.
- **A solo window for Task 5**, granted by the lead and dated in the dispatch record. No other
  gate, suite, benchmark or `migrate --verify` runs during it (Task 5 shows this by command).

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means the
failing run is quoted in the ledger, with its failing assert line **and the cause that the step
predicts**. A failure for any other cause is a plan defect. The executor reports it and does not
work around it (`README.md` convention 2).

1. **Each predicate is red on planted input before it is implemented** (`FD-1335` *Disposition*
   item 3: "Each form is shown red on broken input before the guard is written"). In
   `backend/tests/test_contracts.py`, `test_the_untyped_2xx_predicates_flag_each_planted_form`
   plants into a copy of the real document: form 1 (`POST /api/v1/score/batch` 202 blanked to
   `{}`), and then form 2 (the same response replaced by
   `{"type": "object", "additionalProperties": true}`). It runs first against `_untyped_2xx`
   defined as `return []`. **Predicted red:** the assertion that the planted response is
   reported fails, once for each form, because the stub reports nothing. Then the predicates go
   in, verbatim from `FD-1335` Evidence §1 (`is_empty`, `is_open_object`, an absent `schema`
   counted as `{}`, a 2xx with no `content` reported apart), and the test is green.
2. **Negative controls**, in `test_the_untyped_2xx_predicates_pass_typed_responses`: the real
   `POST /api/v1/score/batch` 202 (`$ref Job`) is reported in neither form, and an object **with**
   `properties` is not reported as form 2. Green from the start. Its enforcement is proven by
   Acceptance 1 (same predicates) and by one deliberate break: `is_open_object` edited to drop
   its `"properties" not in schema` clause. The control then fails on the object with
   `properties`. The break is made on a backup copy (`contract-guard` step 5) and quoted.
3. **The guard is red on the real document, naming exactly the two `/score` responses.**
   `test_no_json_2xx_response_is_untyped` collects every reported `(METHOD, path, status)` from
   `docs/contracts/openapi/generated.json` and subtracts `UNTYPED_2XX_PERMANENT` and
   `UNTYPED_2XX_PENDING_PART_B` (Task 2). It asserts that the remainder is empty. **Predicted
   red, before Task 3:** the remainder is exactly
   `{("POST", "/api/v1/score", "200"), ("POST", "/api/v1/score/compare", "200")}`, both form 1.
   Any other member is a stale exclusion list: stop and report.
4. **A planted form-2 route that is not on the list fails the guard**
   (`test_the_guard_fails_on_an_unlisted_open_object`): the real document, with
   `POST /api/v1/score/batch` 202 made an open object, is reported. Green on correct code. Its
   enforcement is the same red as Acceptance 1.
5. **The exclusion lists are exact, and each temporary entry carries the marker.**
   `test_every_untyped_2xx_exclusion_is_still_untyped` asserts that every excluded key is still
   reported by the predicates. So a route fixed in Part B fails until its entry is removed, and
   the FD closes when `UNTYPED_2XX_PENDING_PART_B` is empty (`FD-1335` *Event*). Each of the 12
   reason strings contains `pending FD-1335 part B`. Each of the 4 permanent reasons names its
   file and line, as in `FD-1335` *Disposition* item 3. **Shown red on broken input:** add
   `("POST", "/api/v1/score/batch", "202")` to `UNTYPED_2XX_PENDING_PART_B` on a backup copy.
   The test fails, naming it as not untyped. Then restore.
6. **The two 200 responses are `$ref`s to the post-ladder shapes.**
   `test_the_score_responses_document_their_models` asserts the following on
   `docs/contracts/openapi/generated.json`:
   - `paths["/api/v1/score"].post.responses["200"].content["application/json"].schema` is
     `{"$ref": "#/components/schemas/ScoringResult"}`, and `/score/compare`'s is
     `{"$ref": "#/components/schemas/ScoreComparison"}`;
   - for each of `ScoringResult`, `LadderRung`, `LadderOperation`, `ScoreComparison`,
     `StepChange` and `TraceDiff`, the component's `properties` keys equal that model's
     `model_fields` keys, read from `model_schema` at the same tree (by alias, if a field has
     one). This makes "the contract documents the post-ladder rung shape" a property of the
     merged tree, not a list of names copied into the test.

   **Predicted red, before Task 3:** a `KeyError` or a failed equality on the `$ref`, because
   the 200 schema is `{}` (premise a). The ledger also quotes
   `python3 -c 'import json; d=json.load(open("docs/contracts/openapi/generated.json")); print(sorted(d["components"]["schemas"]["LadderRung"]["properties"]))'`
   at HEAD. It must include each field that `SL-1345`'s squash added to `LadderRung` (read from
   `git show <SL-1345 squash> -- packages/model-schema/src/model_schema/scoring.py`).
7. **The regenerated contract changes only what it should.** A comparison script, quoted in the
   ledger with its sha256 prefix, compares `generated.json` at `origin/main` against HEAD. It
   prints these four things:
   - which paths changed: exactly `/api/v1/score` and `/api/v1/score/compare`, and in each only
     `responses["200"]`;
   - which components were added: exactly `LadderOperation`, `LadderRung`, `ScoreComparison`,
     `ScoringResult`, `StepChange` and `TraceDiff`, plus any model that `SL-1345` added and that
     `ScoringResult` reaches (each named);
   - which components were removed: none;
   - which existing components changed: none.

   **No component name ends `-Input` or `-Output`.** Measured at `9b0fb97c` with the change
   applied to a scratch copy: exactly the six added, none removed, none changed. If FastAPI
   splits a model into `-Input` and `-Output` names after `SL-1345` (`PositionalDecimalStr`
   carries a `PlainSerializer`), that is a **stop**. It is reported to the lead as a new
   decision point, because it renames shapes a consumer types against.
8. **`NFR-502` holds on both routes, proven on broken input.** The existing
   `backend/tests/test_score.py::test_the_result_is_returned_without_outbound_validation` stays
   green. A new `backend/tests/test_score_compare.py::test_the_comparison_is_returned_without_outbound_validation`,
   marked `@pytest.mark.req("NFR-502")`, returns a `ScoreComparison.model_construct(…)` that
   carries values violating its declared types, and asserts a 200 with those values verbatim.
   Mirror the neighbouring `/score` test and the module's own fixtures. Do not reinvent them
   (`README.md` convention 3). **Shown red on broken input**, both tests: add
   `response_model=ScoringResult` (or `ScoreComparison`) to the decorator on a backup copy. Each
   test then fails with a **500** from FastAPI's outbound validation, and the executor quotes the
   cause line. Then restore. A red with any other cause is a plan defect.
9. **The handlers' bodies are unchanged.**
   `git diff origin/main...HEAD -- backend/src/app/api/score.py` shows changes only in:
   - the two `responses=` arguments;
   - the module docstring's `NFR-502` paragraph, which gains one sentence saying that the 200 is
     documented through `responses=`, which FastAPI reads only to build the OpenAPI document,
     and is never validated;
   - comments.

   No line inside `async def score(` or `async def score_compare(` changes.
10. **`NFR-502` measured again and quoted** (`FD-1335` *Disposition* item 2; method by DP-A2). The
    run is in the solo window, with the script inline in the ledger with its sha256 prefix, the
    tree, `uptime` and `free -h` before and after, and both slot holders read by `flock -n`.
    The figures are read against `NFR-502`'s cited p99 0.070 ms (0.14 % of the 50 ms budget,
    `docs/research/w8-spike-resolution.md` T4). No budget is changed. If DP-A1 is ruled (b),
    `03` NFR-502 gains the dated line (Task 4). `python3 scripts/audit-docs.py` then reports only
    check 31's working-id gap as red while this plan's ids are unminted.
11. **The generated client types both bodies.** After
    `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api`:
    - `grep -c 'ScoringResult' frontend/src/api/generated/schema.d.ts` prints a number above 0
      (it was `0`, `FD-1335` Evidence §2);
    - `grep -c '"application/json": unknown;' frontend/src/api/generated/schema.d.ts` prints the
      `origin/main` figure minus 2. Both figures are quoted.
12. **The gate, in a gate slot, with every evidence field** (**Gate evidence rules**, below). The
    full two-half gate (`CLAUDE.md` §11) exits 0, with every rc, the `N passed` line and `HEAD`
    quoted against `origin/main`'s. `uv run python scripts/generate-contracts.py --check` exits
    0. `uv run python scripts/req-coverage.py` shows the new tests under FR-451 and NFR-502.
13. **The ledger** (an `LG-` under `docs/ledgers/`, with an id from the lead) records the base
    (`SL-1345`'s squash SHA and `origin/main` at start), premises a–h re-read, every red quote,
    the DP resolutions by record id, the Acceptance 7 output, the Acceptance 10 figures and the
    Acceptance 11 counts.

## Global Constraints

- **Validate inbound, never outbound** (`03` NFR-502 as amended by `RL-883`). No
  `response_model=` and no Pydantic return annotation on either route. The raw
  `Response(content=….model_dump_json(), media_type="application/json")` stays.
- **One contract, one way** (`CLAUDE.md` §2): `model-schema` → `docs/contracts/` →
  `frontend/src/api/generated`. `docs/contracts/` is generated and never hand-edited.
  `frontend/src/api/generated` is VCS-ignored and never committed.
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2). The guard
  reads model fields from `model_schema` and never copies them.
- **The hand-authored design stub `docs/contracts/openapi/gi-pricing.yaml` is not touched**
  (`test_the_phase_zero_design_stub_is_not_overwritten`). Neither is the hand-authored
  `docs/contracts/schemas/scoring.schema.json`. Its `outputs` value type is `RL-1343` rule 4's,
  in a later slice.
- **`model_schema/scoring.py` is read, never edited, by this slice.**
- **A shell edit that would `cd`** is refused in this repository. Use absolute paths and `git -C`.

## Scope

### Requirement coverage, each id individually

- **FR-250** (`03` §3.7, `03:162`): the real-time scoring response's contract. Acceptance 6, 11.
- **FR-262** (`03` §3.8, `03:179`): `/score/compare`'s response contract, the Quote Sandbox's
  backend limb. Acceptance 6, 11.
- **FR-451** (`07`): the contract is generated from the models and committed, and CI fails on
  drift. Acceptance 1–7, 12.
- **NFR-502** (`03` §9, `03:1203`): no outbound validation, measured again. Acceptance 8, 9, 10.

**Out of scope, each named:**
- `FD-1335` **Part B**: the 12 open-object routes. They are excluded here, marked
  `pending FD-1335 part B`, and each one is fixed by a later WK-1178 slice, before any WK-675
  slice that consumes it (`FD-1335` *Disposition* items 4–5).
- `FD-1335`'s **LOW sub-item**: documenting the four stream and file routes' media types
  (DP-A4).
- `RL-1343` **rule 4**: typing the values inside `ScoringResult.outputs` (DP-A3).
- Nested open objects inside a typed response, for example `ScoringResult.outputs`. The guard
  reads the top-level response schema only, as `FD-1335`'s predicate does. The skill note
  (Task 6) states this limit.

### Premises, read at `9b0fb97c`

The executor reads each one again at its own base, which is after `SL-1345`, and stops on any
that no longer holds.

| # | Premise | Evidence | Status |
|---|---|---|---|
| a | Both 200s are form 1 | the sweep: `POST /api/v1/score 200` and `POST /api/v1/score/compare 200` under `form1_empty_schema=6` | reproduces `FD-1335` |
| b | 18 untyped, same listing as the FD | `total_untyped=18` over `paths=120 responses_2xx=141`. The FD's tree had 117 and 137. The new routes (`SL-1339`'s sub-graph routes) are all typed | the exclusion lists hold |
| c | Both decorators use `responses=problems(401, 403, 404, 409, 422)` with no 200 entry | `score.py:276-286`, `:330-335` | Task 3's edit site |
| d | Both models are already imported | `score.py:77-78` (`ScoreComparison`, `ScoringResult` from `model_schema`) | no import change |
| e | The merge form has a precedent | `rate_tables.py:304-312` (`responses={**problems(…), 200: {"model": RateTableDiff}, 202: {"model": Job}}`) | Task 3 copies it |
| f | `/score` has the `NFR-502` test, `/score/compare` has none | `test_score.py:341-380`; `grep -n 'NFR-502\|model_construct' backend/tests/test_score_compare.py` prints nothing | Acceptance 8 adds it |
| g | The four permanent exclusions' media types | `audit.py:280` (`application/x-ndjson`), `:308` (`text/csv`); `jobs.py:310` (`text/event-stream`); `rate_tables.py:213` (`text/csv`), `:235-236` (`spreadsheetml`) | the reasons cite these lines |
| h | The change is additive in the OpenAPI | applied to a scratch copy at `9b0fb97c` and regenerated: the two 200s become `$ref`s; added `LadderOperation`, `LadderRung`, `ScoreComparison`, `ScoringResult`, `StepChange`, `TraceDiff`; removed none; changed no existing component or other path; sweep `total_untyped=16` (form 1 = 4, form 2 = 12). The scratch edit was reverted | Acceptance 7's expectation |

### Decision points

| DP | Question | Options | Recommendation | Resolver | State |
|---|---|---|---|---|---|
| DP-A1 | Does `03` NFR-502 change text when the route documents its 200? | (a) No spec change: the re-measure lives in the ledger only. (b) One dated line on NFR-502: the 200 is documented through `responses=`, which builds the contract and validates nothing, plus the re-measured figure and its tree. (c) A dated line only if the figure moved materially | **(b).** The requirement already names its mechanism ("a raw `Response` carrying those bytes runs no outbound validation"). Without a line, a later reader can take documentation for the forbidden `response_model` and remove it, and the cited 0.070 ms would stand unconfirmed against a changed route. (c) needs a threshold that nothing defines | decision-maker | **open** (activation need 5) |
| DP-A2 | How is `NFR-502` measured again? | (a) The w8 shape again (`w8-spike-resolution.md` T4: `time.perf_counter`, 1000 iterations, p99 = the 990th sorted value) on a realistic **post-ladder** `ScoringResult` (premium, 20 rate steps, 60 factors, metadata, the ladder with exact rungs), as validate + serialise and as serialise only (`model_dump_json`, what the route does). (b) Route level: an in-process ASGI client posting to `/score` with `score_one` stubbed to return that result, 1000 requests, p99, on the base and on HEAD. (c) Both, the script inline in the ledger. (d) As (c), but committed as `scripts/bench-score-response.py` | **(c).** (a) re-checks the requirement's own figure (the maintainer: "Its own figure is the one to re-check"), and (b) is "the route as changed", where base and HEAD should agree within noise. Inline keeps the write set to the files below. `RL-872` makes a benchmark a closure input, not a CI gate, and `SL-1259` owns the full-path NFR-502 measurement later | decision-maker | **open** (activation need 5) |
| DP-A3 | Does one WK-1178 slice carry both Part A and `RL-1343` rule 4? (`RL-1343` §5: "If both are ready together, one WK-1178 slice may carry both. That is the lead's cut.") | (a) Separate: this slice is Part A only, and the rule-4 slice follows on the next free lane. (b) Fold: one new plan carries both, and this one is superseded | **(a).** Part A gates WK-675 S6 and S7 (`FD-1335` item 1). Rule 4 gates nothing on WK-675 (`RL-1343` §5) and adds `_build_outputs`, `_coerce_output_value`, the hand-authored `scoring.schema.json`, a release note and a stored-data check. Folding widens the acceptance on the gating path. Both are WK-1178 and touch `score.py`, so they are serial either way | lead | **open** (activation need 6) |
| DP-A4 | Does `FD-1335`'s LOW sub-item (the four stream and file routes' media types) ride in this slice? ("follows in Part A or later and gates nothing") | (a) Later, as its own WK-1178 slice. (b) In this slice | **(a).** It edits `audit.py`, `jobs.py` and `rate_tables.py`, and `rate_tables.py` is on WK-675 S4's and WK-673 Slice 7's paths (`PL-1286` §Sequencing, contention table). It gates nothing. The permanent exclusions are keyed by method, path and status, so they stay correct after it lands | lead | **open** (activation need 6) |

No other open design choice was found. The exclusion keying, the two-direction exactness of the
lists (`contract-guard`, "Every scoped list needs the thing that notices it went stale") and the
predicates are `FD-1335`'s or the skill's, not choices made here.

### Write set, and its contention (`RL-1263`)

| Path | This slice | Existing definitions edited |
|---|---|---|
| `backend/src/app/api/score.py` | `200: {"model": ScoringResult}` and `200: {"model": ScoreComparison}` merged into the two `responses=` mappings; one sentence in the module docstring's NFR-502 paragraph (`:21-27`) | **yes**: the `score` and `score_compare` decorators; the module docstring |
| `backend/tests/test_contracts.py` | appended: `UNTYPED_2XX_PERMANENT`, `UNTYPED_2XX_PENDING_PART_B`, `_untyped_2xx` and its two predicates, and the six tests of Acceptance 1–6 | none |
| `backend/tests/test_score_compare.py` | one appended test (Acceptance 8) | none |
| `docs/contracts/openapi/generated.json` | regenerated | registry-exempt (`RL-1263:104-116`) |
| `docs/specs/03-rating-engine.md` §9, the NFR-502 row | one dated line, **only if DP-A1 is ruled (b)** | **yes**: that row |
| `docs/ledgers/LG-<id>-….md` | new (Acceptance 13) | none |
| `docs/INDEX.md` | regenerated (`python3 scripts/doc-index.py`) | registry-exempt |
| `.claude/skills/contract-guard/SKILL.md` | a short section naming the untyped-2xx guard, its two lists and their stale check, and its top-level-only limit; `Verified` refreshed | that file's `Verified` line |

**Read, not edited:** `packages/model-schema/src/model_schema/scoring.py`,
`scripts/generate-contracts.py`, `backend/src/app/api/responses.py`. `backend/tests/test_score.py`
is run, not edited. Nothing under `frontend/` is committed.

## File contention

Read at `9b0fb97c` against the merged plans. **Serialise** means the two do not build
concurrently, and the second merges `origin/main` first and re-runs its full gate.

### Against `PL-1348` (`SL-1345`, WK-674's ladder slice, `active`)

| Shared path | `PL-1348` edits (`PL-1348:525-590`) | This slice edits | Kind |
|---|---|---|---|
| `backend/src/app/api/score.py` | the explicit 500 mapping on `/score` and `/score/compare`, the `ERROR` log line, **the OpenAPI `responses`**, `_PER_QUOTE_CODES`'s comment | the **same two `responses=` arguments**; the module docstring | **serialise: this slice after `SL-1345` merges** (activation need 1) |
| `packages/model-schema/src/model_schema/scoring.py` | `LadderOperationKind`, `LadderOperation`, `LadderRung`, `Trace.ladder_check_version` | read only. Its `$ref` must publish the post-ladder shape | **dependency: after** (activation need 2; Acceptance 6, 7) |
| `backend/tests/test_contracts.py` | "only if the guard needs a comparison" | appended functions and constants only | no shared definition. Already merged by the time this slice starts, so it is in this slice's gate |
| `docs/contracts/openapi/generated.json` | regenerated | regenerated | exempt. Regenerate on the merged base |
| `docs/specs/03-rating-engine.md` §9 | the NFR-496 row | the NFR-502 row (DP-A1 (b) only) | different rows. Serial anyway |
| timing runs | `scripts/bench-rating.py`, solo (`PL-1348` Acceptance 9) | Task 5's NFR-502 run, solo | **never the same window** |

### Against WK-675's planned slices (`PL-1286`, `draft`)

| WK-675 slice | Shared path or dependency | Kind |
|---|---|---|
| **S6 — Sandbox: form, waterfall, trace** | consumes `POST /api/v1/score` | **held: S6 does not dispatch until this slice merges** (`FD-1335` *Disposition* item 1). The lead records the hold in `PL-1286`'s next dispatch record (a dispatch record, because `PL-1286` is frozen) |
| **S7 — Sandbox compare** | consumes `POST /api/v1/score/compare` | **held**, as S6 |
| **S7b — Compare backend** | `score.py` `score_compare` (its body: each side's `CompiledBundle.algorithm` passed to `diff_traces`), `model_schema/scoring.py` `StepChange`, the generated contract (`PL-1286` §Tasks, S7b) | **serialise.** `score_compare` is one existing function, and this slice edits its decorator. Recommended order: this slice first, because `PL-1286` puts S7b after S6. S7b's `StepChange` change then reaches the documented contract through the `$ref` with no further edit |
| S2 — Designer I | `backend/tests/test_contracts.py` `ONE_SIDED_SLUGS`, `scripts/generate-contracts.py` `GENERATED_SHAPES`, if S2 registers `RatingAlgorithm` (`PL-1286` contention table); consumes `POST /api/v1/rating-algorithms`, one of the 12 | this slice edits neither definition. Append-only on the same file, so the second to merge re-gates. The `POST /rating-algorithms` 201 is **Part B**'s per-route hold, not this slice's |
| S3, S4, S5, S10, S11 (new or changed routes, `03` §5.1) | `generated.json` (exempt) | no shared definition. **After this slice merges, a new route whose 2xx is `{}` or an open object fails the guard.** That is the intended effect, and each leaf plan types its responses |
| S13, S14 (Jobs views) | consume `GET /api/v1/jobs/{job_id}/events`, a permanent exclusion | no conflict. No backend change (`PL-1286`: "no backend change") |
| S1, S8, S9, S12 | none | no conflict |

### Against other open work at `9b0fb97c`

- **The `RL-1343` rule-4 slice** (WK-1178, not yet planned): `score.py`, `model_schema/scoring.py`,
  `scoring.schema.json`, `docs/contracts/` and `test_contracts.py`. It is in the same Work, so the
  two are serial (DP-A3).
- **`SL-1257`** (WK-674's environment half, waiting on WK-674 Slice 2) edits `score.py`. Its
  dispatch record re-checks `score.py` against this slice.
- **`SL-1259`** (WK-674 Slice 5) measures `NFR-502` on the full path. Its measurement never shares
  a window with Task 5's.
- **`SL-1340`** (WK-1250 Slice 2) may change `TraceStep` in `scoring.py`. This slice does not edit
  `scoring.py`, so there is no shared definition. Whichever lands second regenerates
  `generated.json` (exempt).
- **Open PRs**, read by title at 2026-10-01 06:40 UTC: none rules on `FD-1335`, on `/score`'s
  responses or on `test_contracts.py`. The executor reads `gh pr list --state open` again at
  Task 0 (`README.md` convention 4).

## Risks

| Risk | Effect | Detection | Response |
|---|---|---|---|
| `SL-1345` slips | Part A waits, and WK-675 S6 and S7 wait on it in turn | activation need 1 unmet when the WK-675 order reaches S6 | the lead's call (replan vs proceed, `delivery-process.md` §3). The alternative order is Part A first and `SL-1345` rebasing its `responses=` edit. Either order is correct on the code. Only `RL-1263`'s file rule and the shape point decide it |
| FastAPI splits a model into `-Input` and `-Output` after `SL-1345` | component names change, and a consumer types against the wrong name | Acceptance 7 | stop, and the lead raises a new decision point |
| The real-document red names a route that is not on the lists | the exclusion lists are stale | activation need 3; Acceptance 3 | stop. The planner files a dated delta in the dispatch record |
| A `responses=` key typed as the string `"200"` beside the integer keys from `problems()` | FastAPI emits both, or one overwrites the other | Acceptance 6 (the `$ref` is exact), Acceptance 7 (no other change) | use the integer `200`, as `rate_tables.py:310` does |
| The NFR-502 run is contended | a slow figure booked as a pass or a fail | Task 5's `uptime`, `free -h` and two `flock -n` reads | discard and re-run in a new solo window. Never average a contended run in |
| The DB stack is absent | mass fixture errors that look like test failures (`test_score.py` needs `GIP_TEST_DATABASE_URL`) | an `ERROR` at setup, not a `FAILED` assert | bring the stack up and re-run. An error at setup is never quoted as a red |
| The guard over-reaches into a non-JSON body that the LOW sub-item later re-documents | a false red after that slice | Acceptance 5's exactness | the keys are method, path and status, not media type, so the permanent entries still match |
| The guard reads only the top-level schema | a nested open object (`outputs`) stays untyped | stated in Scope and in the skill note | `RL-1343` rule 4 types `outputs`. The rest is outside `FD-1335` |

## Gate evidence rules

For **every** suite-level run, the full gate and Task 5, the ledger records each of these:

- **A clean checkout of the named SHA:** `git status --porcelain` prints nothing, and `HEAD` is
  quoted.
- **The dev-commands slot wrapper, verbatim** (`.claude/skills/dev-commands/SKILL.md:122-171`,
  the gate body and the two-slot `flock -n -E 99` / `flock -w 7200 -E 98` loop), with
  **`LOKY_MAX_CPU_COUNT=4`** exported beside the thread caps. Run it in the foreground with a
  `timeout`.
- **`ruff check --no-cache`**, and **`mypy --no-incremental`** (or a fresh cache).
- **`uptime` and `free -h`** at the start and at the end.
- **The other slot's holder**, read with `flock -n /tmp/slots/gate-1 true; echo $?` and
  `flock -n /tmp/slots/gate-2 true; echo $?` before the run and named as gate or not-gate. An
  rc of 1 means the slot is held.
- **The wall time and the pytest time** against the 1469.6 s solo baseline that `PL-1348` uses
  (`PL-1348:433`; step-down line about 2204 s). A slower run is read as load first.
- **Every rc** of the two-half gate (`CLAUDE.md` §11), the `N passed` line, and `origin/main`'s
  `N passed` beside it. Only named single test files or node ids are exempt from these fields.
  The docs checks run on a clean detached checkout. After merging a `main` that adds a
  migration, run `alembic upgrade head` on the per-worktree test database first.

## Tasks

### Task 0: Preconditions

- [ ] Paste activation needs 1–7 with their outputs and `$M` (from the dispatch record). Read
  `gh pr list --state open` for anything that rules on `/score`'s responses, `FD-1335` or
  `test_contracts.py`, and name the commit read.
- [ ] Branch from `origin/main` at or after `SL-1345`'s squash. Run `uv sync --all-packages`
  (memory: a fresh worktree without it gives hundreds of phantom failures).
- [ ] Re-read premises a–h at the base. Re-run the scratch measurement of premise h (apply the
  Task 3 edit on a scratch copy, regenerate, run the Acceptance 7 script, then restore with
  `git restore`). If any premise does not hold, stop.

### Task 1: The predicates, red first on planted input (Acceptance 1, 2)

- [ ] Append `test_the_untyped_2xx_predicates_flag_each_planted_form` and
  `test_the_untyped_2xx_predicates_pass_typed_responses` to `backend/tests/test_contracts.py`,
  each `@pytest.mark.req("FR-451")`. Each planted document is a `copy.deepcopy` of
  `_load(OPENAPI)` (the module's own loader, `test_contracts.py:141`).
- [ ] Define `_untyped_2xx(document) -> list[tuple[str, str, str, str]]` as `return []`. Run the
  two tests and quote the red: the planted form 1 and form 2 are not reported.
- [ ] Implement `_untyped_2xx` with `FD-1335` Evidence §1's iteration, `is_empty` and
  `is_open_object` verbatim. It returns `(METHOD, path, status, form)` with `form` in
  `{"form1", "form2"}`. Green.
- [ ] Break `is_open_object` on a backup copy, quote the negative control's red, and restore.

### Task 2: The guard on the real document, red first (Acceptance 3, 4, 5)

- [ ] Append the two lists. Keys are `(METHOD, path, status)` and values are reason strings.

  `UNTYPED_2XX_PERMANENT` (a stream or file body, so there is no JSON shape):
  - `("GET", "/api/v1/audit/export", "200")`: `StreamingResponse`, `application/x-ndjson`
    (`backend/src/app/api/audit.py:280`) or `text/csv` (`:308`);
  - `("GET", "/api/v1/jobs/{job_id}/events", "200")`: `text/event-stream`
    (`backend/src/app/api/jobs.py:310`);
  - `("GET", "/api/v1/rate-tables/{slug}@{version}/export/csv", "200")`: `text/csv`
    (`backend/src/app/api/rate_tables.py:213`);
  - `("GET", "/api/v1/rate-tables/{slug}@{version}/export/xlsx", "200")`: the `spreadsheetml`
    type (`backend/src/app/api/rate_tables.py:235-236`).

  `UNTYPED_2XX_PENDING_PART_B`. Each reason is
  `"pending FD-1335 part B: an object with no properties"`:
  - `("GET", "/api/v1/approval-requests/{request_id}", "200")`
  - `("GET", "/api/v1/dataset-versions/{version_id}/rejected", "200")`
  - `("GET", "/api/v1/rating-algorithms/{slug}@{version}/diff", "200")`
  - `("POST", "/api/v1/approval-requests", "201")`
  - `("POST", "/api/v1/approval-requests/{request_id}/decide", "200")`
  - `("POST", "/api/v1/approval-requests/{request_id}/withdraw", "200")`
  - `("POST", "/api/v1/rate-tables/{slug}/seed-from-model", "201")`
  - `("POST", "/api/v1/rate-tables/{slug}@{version}/bulk-operation", "201")`
  - `("POST", "/api/v1/rate-tables/{slug}@{version}/import", "200")`
  - `("POST", "/api/v1/rating-algorithms", "201")`
  - `("POST", "/api/v1/sources/{source_id}/preview", "200")`
  - `("POST", "/api/v1/validation-reports/{report_id}/results/{rule_id}/acknowledge", "201")`

  These are `FD-1335` Evidence §1's listing, re-measured at `9b0fb97c` (premise b) and checked
  again by activation need 3.
- [ ] Append `test_no_json_2xx_response_is_untyped`,
  `test_the_guard_fails_on_an_unlisted_open_object` and
  `test_every_untyped_2xx_exclusion_is_still_untyped`, each `@pytest.mark.req("FR-451")`.
  The reach control: `test_the_untyped_2xx_predicates_pass_typed_responses` names
  `("POST", "/api/v1/score/batch", "202")` as **visited and not reported**. `_untyped_2xx` gains
  a `visited` companion, or returns both, the executor's choice. This makes a walker that stops
  descending fail on a named path, not on a count (`contract-guard`, "Never count what a walker
  reached — name a path").
- [ ] Run the three tests and quote Acceptance 3's red: the remainder is exactly the two
  `/score` keys. Quote Acceptance 5's red from the planted stale entry, then restore.

### Task 3: The two response declarations, and the regenerated contract (Acceptance 6–9)

- [ ] Append `test_the_score_responses_document_their_models`
  (`@pytest.mark.req("FR-250")`, `@pytest.mark.req("FR-262")`, `@pytest.mark.req("FR-451")`)
  and the `/score/compare` `NFR-502` test. Quote the shape test's red (premise a).
- [ ] In `backend/src/app/api/score.py`, on the `score` decorator:
  ```python
      responses={**problems(<the statuses on main after SL-1345>), 200: {"model": ScoringResult}},
  ```
  and on the `score_compare` decorator:
  ```python
      responses={**problems(<the statuses on main after SL-1345>), 200: {"model": ScoreComparison}},
  ```
  The `problems(…)` arguments are whatever `main` carries after `SL-1345`, which will include
  `500` per `RL-1346`. Copy them and do not retype them. Keep the existing comment block above
  `/score`'s `responses=`. Do not add `response_model=`. Do not change `-> Response` or either
  `return Response(…)`.
- [ ] Add one sentence to the module docstring's NFR-502 paragraph: the 200 is documented
  through `responses=`, which FastAPI reads only when it builds the OpenAPI document, so the
  contract carries the shape and nothing validates the body. Cite `FD-1335`.
- [ ] `uv run python scripts/generate-contracts.py`, then `--check` (exit 0). Run the
  Acceptance 7 comparison script and quote it.
- [ ] Run Task 2's tests, the shape test and both `NFR-502` tests: green. Then make the
  `response_model=` break on a backup copy, quote both 500s, and restore.
- [ ] The Acceptance 9 diff, quoted.

### Task 4: The spec line (only if DP-A1 is ruled (b); Acceptance 10)

- [ ] Append one dated amendment to `03` NFR-502's row, as the ruling words it. It goes after
  Task 5, so that it quotes the measured figure and its tree. Run
  `python3 scripts/audit-docs.py`. Expect only check 31 red, for this plan's unminted ids.

### Task 5: `NFR-502` measured again, solo (Acceptance 10; method by DP-A2)

- [ ] In the lead's solo window: record `uptime`, `free -h` and both `flock -n` slot reads, and
  check that no `pytest`, `bench-*` or `doc-id.py migrate --verify` process runs
  (`pgrep -af 'pytest|bench-|migrate --verify'`; exclude the `pgrep` line itself).
- [ ] Run the method DP-A2 rules, with the script inline in the ledger and its sha256 prefix.
  Quote p50, p99 and max beside `NFR-502`'s 0.070 ms and the 50 ms budget. For a route-level
  limb, quote the base and HEAD figures side by side.
- [ ] Record `uptime` and `free -h` after the run. A run with a held slot or a load above the
  box's core count at either end is discarded and re-run.

### Task 6: The client evidence, the skill note, the gate and the ledger (Acceptance 11–13)

- [ ] `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api` on the
  base and on HEAD, and quote both counts.
- [ ] Add the `contract-guard` skill section and refresh its `Verified` line with the tree.
- [ ] Regenerate `docs/INDEX.md` after the ledger is added. Run
  `python3 scripts/doc-id.py migrate --verify <tmpdir> --ref HEAD` and read row (a)
  (`delivery-process.md` §11a).
- [ ] Run the full gate under **Gate evidence rules**, and write the ledger.

## Hand-off

- **To the lead:** record in `PL-1286`'s next dispatch record that WK-675 S6 and S7 dispatch only
  after this slice merges (`FD-1335` *Disposition* item 1). At this slice's merge, record, dated,
  that the hold lifts for `/score` and `/score/compare`, and that it **stays per route** for the
  12 routes in `UNTYPED_2XX_PENDING_PART_B` (item 5).
- **To Part B's planner:** each fixed route removes its entry from `UNTYPED_2XX_PENDING_PART_B`
  in the same commit. Acceptance 5's test forces this. `FD-1335` closes when the list is empty.
- **To the `RL-1343` rule-4 slice:** the contract already carries `$ref ScoringResult`. Rule 4
  narrows `outputs`' value type inside it, and it re-measures `NFR-502` by this plan's Task 5
  method (`RL-1343` §5, "The `NFR-502` re-measure").

## Self-review

- **`FD-1335` Part A, clause by clause:**
  - Item 1, timing before WK-675's `/score` slices → Status (Sequencing), File contention (S6,
    S7), Hand-off.
  - Item 2, the two response models, the raw `Response` kept, no `response_model` → Task 3,
    Acceptance 6, 8, 9.
  - Item 2, the contracts regenerated → Task 3, Acceptance 7, 12.
  - Item 2, NFR-502 re-read and measured again → Task 5, Acceptance 10, DP-A1, DP-A2.
  - Item 3, the guard over both forms, each red first → Acceptance 1, 3, 4.
  - Item 3, the two `/score` responses as form 1's red on the real document → Acceptance 3.
  - Item 3, the four permanent exclusions cited by line → Task 2, premise g.
  - Item 3, the twelve temporary exclusions marked `pending FD-1335 part B` → Task 2,
    Acceptance 5.
  - Item 3, "fails on a planted form-2 route not on the list" → Acceptance 4.
  - Parts B and the LOW sub-item → Scope (out of scope), DP-A4.
- **The lead's sequencing** → Status, activation needs 1–2, the `PL-1348` contention table. The
  post-ladder shape → Acceptance 6 and 7. The solo window → Build-start conditions and Task 5.
- **Literals read at `9b0fb97c`:** the route paths and statuses (the sweep's output), the
  decorator lines, the imports, the `rate_tables.py` precedent, the line numbers of the media
  types, `_load` and `OPENAPI` in `test_contracts.py`, and the existing `NFR-502` test's name.
  The new test names, `_untyped_2xx`, `UNTYPED_2XX_PERMANENT` and `UNTYPED_2XX_PENDING_PART_B`
  are this plan's proposals. Each is named once and used consistently in the acceptance items
  and Tasks 1–6.
- **Open:** DP-A1 to DP-A4. **Unminted:** this plan (working id 9788), `SL-9787` and the ledger.
  Task 0 re-points them at the mint.
