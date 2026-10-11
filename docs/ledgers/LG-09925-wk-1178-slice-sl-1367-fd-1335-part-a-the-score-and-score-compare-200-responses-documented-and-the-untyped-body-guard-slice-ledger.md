---
id: LG-9925
family: ledger
title: WK-1178 slice SL-1367 — FD-1335 Part A, the /score and /score/compare 200 responses documented and the untyped-body guard (PL-1364), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-11
owner: executor
tree: 99f22479a20e7fa64f8b6654e0d371c595b1e35a
phase: P2
work: WK-1178
slice: SL-1367
plans: [PL-1364]
corrected_by: []
relates: [FD-1335, FD-1366, FD-1372, RL-1365, SL-1345]
---

# LG-9925 — WK-1178 slice SL-1367: FD-1335 Part A

**GO:** the activation record, `from-lead-2026-10-09.md` "2026-10-11 10:58:50 BST — Lead: GO SL-1367 (WK-1178, FD-1335 Part A, PL-1364) — the activation record (DP-A3 (a), DP-A4 (a))"; its acceptance, `to-lead.md` "2026-10-11 10:59:23 BST — SL-1367 GO accepted; Task 5's NFR-502 re-measure: run LOCAL now as "measured, diagnostic", verdict CARRIED to the dedicated-VM run list. SL-1367's merge does NOT wait for the VM". **Ruling on Task 5 (the maintainer, relayed by the lead, 2026-10-11 11:00):** Acceptance 10 compares HEAD with base on the same box, so its stop conditions are decided locally and are a true verdict; only NFR-502's absolute reading against the budget is "carried; discharge: the dedicated-VM run", and it does not block the merge. A clear FAIL is a STOP to the lead.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Executed from `PL-1364` (leaf plan, now `active`) by `executor-sl1367` (sonnet). Branch
`sl-1367-wk1178-fd1335a`, worktree `.claude/worktrees/sl-1367`, cut from `origin/main` at
`99f22479a20e7fa64f8b6654e0d371c595b1e35a`. Row: `SL-1367` in `docs/roadmap.md`. Requirements:
FR-250, FR-262, FR-451, NFR-502. The slice's `SL-1345` base: squash
`1dd5e264195677b4a13268b80ac8673c2c027135`, an ancestor of the base.

Decision points (lead-kind), recorded dated in the GO entry: DP-A3 = (a), a separate slice from
`RL-1343` rule 4 (history: `to-lead.md` "2026-10-05 18:25:42 BST"); DP-A4 = (a), the stream and file
routes' media types follow later. DP-A1 and DP-A2 are ruled by `RL-1365`. `FD 9775` is minted as
`FD-1372` (verified by the lead in the GO).

### Task list

| Task | Plan step | Acceptance | Status |
|---|---|---|---|
| 0 | preconditions, dated delta below | needs 1–8 | done |
| 1 | predicates, red first | 1, 2 | done |
| 2 | guard on the real document | 3, 4, 5 | done (one item red until Task 3) |
| 3 | two 200 declarations, regenerated contract | 6–9 | done |
| 4 | the NFR-502 spec line | 10 | open (after Task 5) |
| 5 | NFR-502 re-measure, local, diagnostic | 10 | open |
| 6 | client evidence, skill note, gate, ledger | 11–13 | client evidence and skill note done; gate and closing acts open |

### Gate

Not run.

### Audit

Not yet. The auditor writes it.

### Build log

#### 2026-10-11 — Task 0: the needs, and a dated delta against PL-1364's counts

Read at `origin/main` `99f22479a20e7fa64f8b6654e0d371c595b1e35a`. Needs 1–6 met (SL-1345 squash
`1dd5e264`; `scoring.py` changed since `9b0fb97c`, 1 file, 44+/11-; `grep -c '200: {"model"'
score.py` prints 0; FD-1366 and FD-1372 minted; plan, row and RL-1365 minted). Need 7: the GO
entry above. Need 8: this commit flips the plan and the row to `active`.

**Delta against the plan (the plan body is frozen and is not edited).** Need 3's sweep (hash prefix
`4574b64f1293849b`, the FD's own) printed `paths=133 responses_2xx=157`, `form1_empty_schema=6`,
`form2_object_without_properties=9`, `total_untyped=15`. The plan expects 6, 12 and 18. Three
form-2 routes were typed since 1 Oct: `GET /api/v1/rating-algorithms/{slug}@{version}/diff`,
`POST /api/v1/rating-algorithms` (201) and `POST /api/v1/rate-tables/{slug}/seed-from-model` (201).
The request-side command printed 5 lines, not 7: three JSON `OPEN` (bulk-operation,
`POST /api/v1/sub-graphs`, `POST /api/v1/sub-graphs/{slug}/versions`) and the two multipart
`NON-JSON`; `POST /api/v1/rating-algorithms` and seed-from-model are typed. By need 3's own clause
a route missing because it has since been typed is met, and Task 2's lists shrink to:
`UNTYPED_2XX_PERMANENT` 4, `UNTYPED_2XX_PENDING_PART_B` 9, `UNTYPED_REQUEST_PENDING` 3,
`NON_JSON_REQUEST_BODIES` 2. Every "12", "five" and "18" in Task 2 and Acceptance 3–5 reads 9, three
and 15 here, and `[response]`'s planted remainder is the two `/score` keys plus the planted one.

**S5 (SL-1547).** It types `POST .../bulk-operation` (request and 201) and the `.../import` 200
response in its first commit (`to-lead.md` "2026-10-11 10:57:53 BST"). Both are still on the lists
at this base. Whichever of S5 and this slice merges second removes them by content and re-proves
the guard on the shortened lists. The merge turn records which merged second.

**Overlap.** `sl-1257-wk674-s3-env` (WK-674 S3) edits the same `responses=problems(…)` line on
`/score` (adds 429) and regenerates `generated.json`; it does not touch `test_contracts.py`.
Plan: take main after it lands and regenerate the contract.

#### 2026-10-11 — Task 1: the predicates, red first on planted input (Acceptance 1, 2)

Stubs first: `_untyped_bodies` returned `[]` and `_visited_bodies` returned `iter(())`, with the
tests appended to `backend/tests/test_contracts.py`. Command:
`uv run --directory <wt> pytest -q -p no:cacheprovider backend/tests/test_contracts.py -k "untyped_body_predicates"`
(under the small-test flock). Result: **5 failed, 159 deselected** (rc 1), as the plan predicted:
- `test_the_untyped_body_predicates_flag_each_planted_form[response-form1|response-form2|request-form1|request-form2]`:
  4 of 4 red, the planted body is not reported;
- `test_the_untyped_body_predicates_pass_typed_bodies`: red on its first visited assertion,
  `AssertionError: the walker never reached ('response', 'POST', '/api/v1/score/batch', '202')`.

Then `_walk_bodies`, `_visited_bodies` and `_untyped_bodies` went in: **5 passed**. Negative
control: with `_is_open_object`'s `and "properties" not in schema` clause deleted on a backup copy,
the pass-typed test is red (1 failed, 4 passed) with `assert ('response', 'POST',
'/api/v1/score/batch', '202') not in {…}`, the object-with-properties control reported; the file was
restored and is green again (5 passed). `_guard_remainder` is defined in Task 2, with the lists it
subtracts.

#### 2026-10-11 — Task 2: the guard on the real document (Acceptance 3, 4, 5), lists 4 / 9 / 3 / 2

Lines cited by the reasons were re-read at the base and corrected where they had moved
(`rate_tables.py:184` csv, `:206-207` xlsx, `:225-226` import upload, `:128` bulk body; `datasets.py:215`;
`sub_graphs.py:46`, `:61`; `rating.py:1179` `BulkOperationBase`; `audit.py:280`, `:308`; `jobs.py:310`).
Command (small-test flock): `pytest -q backend/tests/test_contracts.py -k "untyped_body or no_json_body or non_json_request or unlisted_open_body"`.
- End of Task 2: **1 failed, 10 passed** (rc 1). The one red is `test_no_json_body_is_untyped[response]`,
  remainder exactly `{('response','POST','/api/v1/score','200'), ('response','POST','/api/v1/score/compare','200')}`
  (the prediction); `[request]` green. 11 node ids collect.
- Request side red on broken input: with `("POST", "/api/v1/sub-graphs")` removed from `UNTYPED_REQUEST_PENDING`
  on a backup copy (the plan's example route, `/api/v1/rating-algorithms`, is typed at this base),
  `[request]` is red with exactly `[('request','POST','/api/v1/sub-graphs','application/json')]` and `[response]` unchanged. Restored.
- Stale entries: `("POST","/api/v1/score/batch","202")` added to the pending 2xx list ->
  `no longer untyped, remove from the 2xx lists: [('POST', '/api/v1/score/batch', '202')]`; the request-side twin ->
  `no longer untyped, remove: [('POST', '/api/v1/score/batch')]`. One `NON_JSON_REQUEST_BODIES` entry deleted ->
  `test_non_json_request_bodies_are_exactly_the_cited_routes` red (set inequality). Each restored.
- `test_the_guard_fails_on_an_unlisted_open_body` green on both sides (planted remainder = real remainder plus the planted key).

#### 2026-10-11 — Task 3: the two 200 declarations and the regenerated contract (Acceptance 6–9, 8, 8b)

Environment note: fastapi is **0.142.2** at this base (the plan measured 0.141.1);
`fastapi._compat.v2.ModelField.validate(self, value, values={}, *, loc=())` is unchanged, and the
control route counts 1 at this version. The per-worktree database was created with the dev-commands
`docker exec … createdb -T` block and migrated to head.
- Red first: `test_the_score_responses_document_their_models` before the edit: **1 failed**,
  `assert {} == {'$ref': '#/components/schemas/ScoringResult'}` on `/api/v1/score` (premise a).
- The two spy tests and `test_the_comparison_is_returned_without_outbound_validation` are green on the
  unchanged routes (2 passed per file, spy 0 on the route, ≥ 1 on the planted control).
- FD-1372 docstring: `test_the_result_is_returned_without_outbound_validation`'s docstring replaced with
  the plan's text, with the placeholder filled `FD-1372`. **Delta:** the plan's lines carry the placeholder
  across a wrap (`FD-<minted id of / FD 9775>`); with a 7-character id the paragraph re-flows by one
  line, and the words are otherwise identical. The test body is unchanged and green.
- `score.py`: `responses={**problems(401, 403, 404, 409, 422, 500), 200: {"model": ScoringResult}}` on
  `/score`, `… 200: {"model": ScoreComparison}` on `/score/compare`; `problems(…)` copied from main
  (it carries 500). One sentence added to the module docstring's NFR-502 paragraph citing FD-1335.
  `git diff origin/main -- backend/src` = 4 insertions, 2 deletions, only those. (Acceptance 9.)
- `uv run python scripts/generate-contracts.py` then `--check`: rc 0 ("47 generated contracts match the models").
- Acceptance 7, `sl1367_cmp.py` (sha256 prefix `9cbc9fe1844b8dc3`), against `origin/main`: paths changed = `POST /api/v1/score`
  and `POST /api/v1/score/compare`, `responses["200"]` only; components added = `LadderOperation`, `LadderRounding`,
  `LadderRung`, `ScoreComparison`, `ScoringResult`, `StepChange`, `TraceDiff` (`LadderRounding` is the model SL-1345 added
  that `LadderRung` reaches); removed none; changed none; the only `-Input`/`-Output` names are the pre-existing `InputContractField-*`.
  `LadderRung.properties` at HEAD = `components, operation, rounding, rung, unrounded_minor, value_minor`.
- Collected: 15 node ids (`pytest --collect-only -q` over the three files with the new tests' selectors): 12 in `test_contracts.py`,
  1 spy test in `test_score.py`, 2 in `test_score_compare.py`. All 15 green after the edit.
- Broken-input proofs on a backup of `score.py` (annotation `-> ScoringResult` / `-> ScoreComparison`), each restored:
  - dict form (`return result.model_dump()` / `comparison.model_dump()`): the 500 test is red, `assert 500 == 200`
    (`INTERNAL_ERROR`, mapped by `_handle_unexpected`) and the spy test is red, `assert 1 == 0`, on both routes;
  - instance form (`return result` / `return comparison`): the spy test is red, `assert 1 == 0`, and the 500 test stays green
    (status 200), which is Acceptance 8b's point, on both routes.

#### 2026-10-11 — Task 6 (part): the client evidence and the skill note (Acceptance 11)

`pnpm --dir frontend install --frozen-lockfile` then `pnpm --dir frontend generate:api` at HEAD; the base
count generated with the same `openapi-typescript` 7.13.0 from `git show origin/main:docs/contracts/openapi/generated.json`:

| | `grep -c 'ScoringResult' schema.d.ts` | `grep -c '"application/json": unknown;' schema.d.ts` |
|---|---|---|
| base (`origin/main` `99f22479`) | 0 | 6 |
| HEAD | 6 | 4 (base minus 2) |

`.claude/skills/contract-guard/SKILL.md` gains the section "The untyped-body guard is a different kind
of guard" and a `Verified` entry for 2026-10-11 at `origin/main` `99f22479` plus this slice;
`.claude/skills/README.md`'s row date is refreshed.

## PRs

None yet.
