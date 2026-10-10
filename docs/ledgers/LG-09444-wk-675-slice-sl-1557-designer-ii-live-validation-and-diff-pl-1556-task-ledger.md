---
id: LG-9444
family: ledger
title: WK-675 slice SL-1557 — Designer II, live validation and diff (PL-1556), task ledger
status: active
created: 2026-10-09
owner: executor
tree: 8b9d12c7dac1c0272b1109c9c1d2e295847dd575
phase: P2
work: WK-675
slice: SL-1557
plans: [PL-1556]
corrected_by: []
relates: [PL-1556, RL-1555, RL-1474, RL-1438, FD-1437, RL-1445, SL-1477, WK-675]
---

# LG-9444 — WK-675 slice SL-1557: Designer II, live validation and diff

*(LG-9444 is a working id reserved by the lead; the lead mints it. Authored ahead of the GO at the user's order of 2026-10-09 15:22:26 BST.)*

**GO:** not yet given. This slice is authored ahead of its GO at the user's order ("2026-10-09 15:22:26 BST — USER: 'worrying only one executor runs'. FILL THE VM NOW …", items 1–4 of `to-lead.md`). Nothing merges without its GO, its full gate and the maintainer's MERGE-ACK.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Executed from `PL-1556` (WK-675 Slice 3, leaf plan) by `executor-wk675s3` (sonnet). Branch
`sl-1557-wk675-s3`, worktree `.claude/worktrees/sl-1557`, cut from `origin/batch-d3-2026-10-09`
at `8b9d12c7dac1c0272b1109c9c1d2e295847dd575` (the D3 mint batch; it must merge before this slice;
`origin/main` is ahead by one commit, `61e2a8d9`, which is merged at the merge turn, never rebased).
Row: `SL-1557` in `docs/roadmap.md` (minted from working id 9581), plan `PL-1556` (from 9578),
ruling `RL-1555` (from 9543). Requirements: FR-24, FR-212, FR-214, FR-215, FR-219, FR-223, FR-227,
FR-240, FR-244, FR-403, NFR-463, and the FR that RL-1474 T1 creates. FR-246 is not delivered here
(PL-1556 *Scope*).

### Task list

| Task | Plan step | Acceptance | Status |
|---|---|---|---|
| 0 | Task 0 preconditions | Task 0 rows re-run at the dispatch tree | done (below) |
| 0A | diff route typed, contract regenerated | Acceptance 21 | done, commit 2 |
| 1 | `graph_invariant_issues` and types in model-schema | Acceptance 2, 4 | done, commit 3 |
| 2 | mode mismatch named at compile | Acceptance 16, 17, 19 (18 already on main) | pure level done, commit 4; HTTP test authored, unrun (DB) |
| 3 | bare-`ValueError` sweep | Acceptance 20 | done, commit 5 (no code change) |
| 4 | validate route and spec texts | Acceptance 1, 3, 5–11 | authored, commit 6; DB tests unrun; FR id pending |
| 6 | live validation in the designer | Acceptance 12–15, 23 | authored, commit b1fe4d9e; tests UNRUN (no install) |
| 7 | diff overlay | Acceptance 22 | authored, commit a7a66a6f; tests UNRUN (no install) |
| 8 | accessibility check | NFR-463 | static review done (below); browser checks OWED |
| 9 | gate and ledger | Acceptance 24 | open (waits for the gate slot) |

### Gate

Not run. Full gates, builds, whole-tree mypy, audit-docs and `migrate --verify` wait for the gate
slot after S3's Task 7 (the lead's brief, small-test rule).

### Audit

Not yet. The auditor writes it.

### Build log

#### 2026-10-09 15:25 BST — worktree and first commit

- Worktree cut from `origin/batch-d3-2026-10-09` = `8b9d12c7` (the brief's head, confirmed by
  `git rev-parse`). The brief's Section C head matches.
- First commit: `PL-1556` status `draft` → `active`, `SL-1557` row `draft` → `active`, this ledger.
- Activation needs (PL-1556 *Activation needs, in order*), read at this tree:
  1. RL-1474 minted: file `RL-01474-…` present. Met.
  2. RL-1438 and FD-1437 minted: both files present. Met.
  3. S2 (SL-1477) merged: `frontend/src/components/dag/` carries `DagDesigner.vue`, `StepNode.vue`,
     `NodeNavigator.vue`; `RatingAlgorithmDraft` at `rating.py:423`. Met.
  4. DP-S3-1 and DP-S3-2 decided: RL-1555 (in this batch). Met.
  5. No slice editing `compile.py` in flight: **to be named in Task 0** (SL-1340, a sibling seat of
     this overnight wave, may edit `compile_bundle`; the brief's order is merge-ordered, so the
     conflict is a merge-turn matter, but the lead should read it).
  6. Task 0 re-run: Task 0 below.
  7. Maintainer's agreement and the lead's go: not given; this slice is authored ahead of it.

#### 2026-10-09 15:30 BST — Task 0 re-run at `8b9d12c7` (deltas only; every other row as expected)

- 0.1: `class ValidationIssue` now at `compile.py:62`. 0.2: importers at `operations.py:58` and `platform/rating_algorithms.py:21`.
- 0.3: `_graph_invariants` `rating.py:462`, `_reachable` `:546`, `_reaches_output` `:566`. 0.4: `sub_graphs.py:118`, `:122` unchanged.
- 0.6: `validate_algorithm(algorithm)` `compile.py:733`, `check_model_reference_mode` `:736` (bare, so a mismatch is still `BUNDLE_COMPILE_FAILED`).
- **0.7 DELTA:** `grep -c MODEL_REFERENCE_MODE_INCONSISTENT backend/src/app/errors.py` is now **1** (plan: 0). `SL-1430` (#1227, `LG-1468`) added the code to `RATING_ERROR_CODES` (`errors.py:341`) and applies it at the Rating Version create/pin write (`rating_versions.py:296`, `check_model_reference_mode` caught and re-raised 422).
- **RL-1438 T1 is already applied on main**: `03` FR-223's cell carries the "Amended 2026-10-05 (`RL-1438`)" text. Acceptance 18's test already exists in `backend/tests/test_rating_version_create_pins.py:328-330` (registry and owned-list both asserted, and both pass on this tree). Consequence: Task 2's `errors.py` edit, `test_errors.py` test and the `03` FR-223 edit are **already done**; they are NOT repeated, and Acceptance 18 has no red to show. Task 2 keeps the compile-site wrapping (the pure test and the HTTP test) only. **Plan delta, reported to the lead.**
- 0.9: the diff route is still `-> dict[str, Any]`; 0.11: `03` §5.1 header is three-cell (count 1); 0.13: `UNTYPED_2XX_PENDING_PART_B` absent in `test_contracts.py` (no hit), so DP-S3-1 (a) has no list entry to remove.
- 0.12 (S2 merged): met (see the first entry).
- **Activation need 5:** `SL-1340` (WK-1250 S2; sibling seat in this wave) is a `compile.py` editor candidate; this slice edits `compile_bundle` (`:736`). Both are authored ahead of GO, serialised at merge: the merge turn of the second reads `git merge-tree` rc 0 before taking the tree.

#### 2026-10-09 15:34 BST — Task 0A (commit 2)

- RED: `nice -n 19 flock -w 300 /tmp/slots/small-test -c "timeout 150 uv run --directory <wt> pytest -q -p no:xdist backend/tests/test_contracts.py -k algorithm_diff_response"` → rc 1, `1 failed, 154 deselected`, `AssertionError` at `test_contracts.py:227` (the 200 schema is `{'additionalProperties': True, 'title': 'Response Algorithm Diff …', 'type': 'object'}`, not the `$ref`). Cause as stated.
- Code: `algorithm_diff` returns `AlgorithmDiff`; `diff_between` returns the model it built (wire unchanged).
- `scripts/generate-contracts.py` then `--check`: rc 0 (`46 generated contracts match the models`). `pnpm generate:api` waits for the frontend install after Task 7 (generated, VCS-ignored).
- GREEN: same command → `1 passed, 154 deselected`.
- Position: this is the slice's **second** commit, after the activation commit `b15d1a57` (docs only); no frontend code consumes the route, so the FD-1335 item-5 reading (own route, before any frontend consumption) holds. The ledger's "first commit" requirement is read as the first code commit.

#### 2026-10-09 15:50 BST — Task 1 (commit 3)

- RED: `nice -n 19 flock -w 300 /tmp/slots/small-test -c "timeout 150 uv run --directory <wt> pytest -q -p no:xdist packages/model-schema/tests/test_graph_invariant_issues.py"` → rc 2, collection `ImportError: cannot import name 'graph_invariant_issues' from 'model_schema'`.
- Code: `ValidationIssue` moved into `model_schema/rating.py` (unchanged), `AlgorithmValidationReport`, `graph_invariant_issues`; `RatingAlgorithm._graph_invariants` raises on the first issue with today's exception classes and messages. Exports added to `__init__`.
- GREEN: same file `7 passed`; `test_rating_algorithm.py` + `test_graph_errors.py` `13 passed` unmodified.
- One test assertion was wrong in my first draft (which of two unchained producers is flagged depends on Kahn's pop order, today's behaviour); the test now asserts exactly one ambiguous issue naming one of the two. Behaviour unchanged from the pre-move code.
- Broken input (Acceptance 2 and 4), each run then restored: (M1) drop the duplicate-id `return` → `test_a_duplicate_step_id_is_the_only_issue_even_with_a_cycle` FAILED; (M2) ambiguous-producer check run unconditionally → `test_no_ambiguous_producer_issue_after_a_cycle` FAILED; (M3) return early at the orphan stage → `test_every_breach_is_reported_not_the_first` and the ambiguous-after-cycle test FAILED.
- Not yet done for Task 1: `pricing-core`'s `ValidationIssue` re-import (Task 2's file; `compile.py` still defines its own class, so the class exists twice until Task 2, by plan order). `test_sub_graph.py` and whole-tree mypy wait for the gate slot.

#### 2026-10-09 16:10 BST — Task 2 (commit 4), scope reduced per the lead's ruling "2026-10-09 15:29:43 BST — RULINGS …" DELTA 2

- Scope: the compile-site wrapping and its tests only. Already on main: `RATING_ERROR_CODES` entry (SL-1430/#1227, `errors.py:341`), RL-1438 T1 on `03` FR-223, and the Acceptance 18 test (`test_rating_version_create_pins.py:328`).
- RED: `pytest -q -p no:xdist packages/pricing-core/tests/test_rating_compile_bundle.py -k mode_mismatch` → `1 failed, 9 deselected`: `ValueError: model_call step 's_rp' declares mode 'exact', but the version declares 'approximation' (FR-223)` raised where `CodedError` `^MODEL_REFERENCE_MODE_INCONSISTENT: .*'s_rp'` was expected. (Load1 read 4.34 at that run, a little over the 4.0 cap.)
- Code: `compile_bundle` catches the `ValueError` of `check_model_reference_mode` and re-raises through `_raise_named`; `ValidationIssue` is removed from `compile.py` and imported from `model_schema` (still in `__all__`).
- GREEN: `test_rating_compile_bundle.py` `10 passed`; `test_rating_compile.py` `45 passed`. `ruff check packages/pricing-core` clean.
- `backend/tests/test_rating_mode_mismatch_api.py` is authored (Acceptance 16 over HTTP and the 201 save of the same algorithm, 19). It imports clean but is **not run**: it needs the Postgres fixtures, which the small-test rule bars. Owed in the heavy-run phase; its red on main (`BUNDLE_COMPILE_FAILED`) is to be shown then, by running it at `origin/main`'s `compile.py`. The `s_model` step shape is written from the valid-algorithm fixture and unverified against `validate_algorithm` until that run.
- Acceptance 17 (the matching version compiles) is covered by the existing compile-bundle tests that use `_version()` unchanged.

#### 2026-10-09 16:25 BST — Task 3, the FD-1437 limb (3) sweep (Acceptance 20; no code change)

Predicate, verbatim, run at tree `893d8161` (`git -C <wt> grep -n -E 'raise (ValueError|[A-Za-z]*Error)\(|_raise_named\(' -- packages/pricing-core/src/pricing_core/rating/compile.py packages/model-schema/src/model_schema/rating.py`): **27 lines** (rating.py 15 `raise …Error(` sites, 3 of them in `_graph_invariants`' mapping; compile.py 1 `raise CodedError(` inside `_raise_named`, plus 11 `_raise_named(` call/def lines). Only the ones that can reach `compile_rating_version`'s `except ValueError` (`backend/src/app/platform/rating_versions.py:622`) with a non-`CodedError` are rows below; that handler maps a `CODE: detail` message to its code and everything else to `BUNDLE_COMPILE_FAILED`.

| # | Site (file, symbol) | Raises | Outcome today | Verdict |
|---|---|---|---|---|
| 1 | `compile.py` `compile_bundle`: `RatingAlgorithm.model_validate(resolved_algorithm.payload)` (`:704`) | pydantic `ValidationError` (a `ValueError`), incl. `rating.py`'s validators and `_graph_invariants` messages | `BUNDLE_COMPILE_FAILED` | right: a stored payload that no longer validates is a corrupt artifact; `03` §5.1 owns no code for it. Finding candidate for the auditor, not fixed here |
| 2 | `compile.py` `_refuse_unapproved_objectives`: `ArtifactRef.model_validate(objective["ref"])` (`:619`) | `ValidationError` | `BUNDLE_COMPILE_FAILED` | right: a malformed `spec.objective.ref` inside a pinned model payload; no owned code |
| 3 | `compile.py` `_refuse_control_factor_keys`: `ArtifactRef.model_validate(factor_ref)` (`:643`) | `ValidationError` | `BUNDLE_COMPILE_FAILED` | right, as row 2 |
| 4 | `compile.py` `compile_bundle`: `Bundle(...)` construction | `ValidationError` | `BUNDLE_COMPILE_FAILED` | right: an internal-shape failure, not a user-correctable refusal |
| 5 | `rating.py` `check_model_reference_mode` (`:221`) | bare `ValueError` | **now `MODEL_REFERENCE_MODE_INCONSISTENT`** (Task 2) | named |
| 6 | `compile.py` `validate_algorithm` issues (`:721`) | `_raise_named(issues[0].code, …)` | named | named |
| 7 | the platform `_Resolver.resolve` | `PlatformError` (not a `ValueError`, `errors.py:423`) | passes through | outside the handler |
| 8 | `to_jdm`, `bundle_hash` | no `raise` in `compile.py` | none | none |

Count: **4** sites keep `BUNDLE_COMPILE_FAILED` with a reason (rows 1–4), **1** is now named (row 5). A site that should carry a named code and has none in `03` §5.1: rows 1–3 are recorded for the auditor as a finding candidate (no spec code for "a pinned artifact's stored payload is malformed"). Nothing mapped to an existing owned code, so no code change (plan Task 3 Step 3).

#### 2026-10-09 16:50 BST — Task 4 (commit 6): spec texts, route, tests

- **FR id:** RL-1474 T1 needs `FR-<new>`; no working id was reserved for this seat, so every occurrence is the greppable token `FR 9445` (spec `03` §3.1, §4.1, §5.1 rows, `00` FR-24, route docstrings, test markers) until the lead names one. `grep -rn FR 9445` finds them all. **Open: asked the lead.**
- Spec: T1 applied after the `| **FR-219** |` row (the anchor occurs once; S2's `FR-1530` row now follows it, as the plan predicted), T2 in its three-cell form (§5.1 header still `| Method | Path | Purpose |`), T3 before `### 4.2`, T4 appended to FR-24's second cell. Taken programmatically from RL-1474's code blocks (T1 to T4), then the placeholders `RL-<this>` → `RL-1474`, `<date>` → `2026-10-09`, `FR-<new>` → `FR 9445`. Every anchor found exactly once.
- Code: `platform/rating_algorithms.py` `validate_draft`; `api/rating_algorithms.py` `validate_rating_algorithm` (registered before the `{slug}@{version}` routes; no `DatabaseDep`, so nothing persists). `generate-contracts` then `--check` rc 0; Acceptance 11's command prints two `$ref`s, `RatingAlgorithmDraft` and `AlgorithmValidationReport`.
- Tests (`backend/tests/test_rating_algorithm_validate.py`, 14 cases incl. the 7-way parity parametrisation): authored; collection and `test_the_route_publishes_typed_bodies` run green; the rest need Postgres fixtures and are **UNRUN, so no red-on-404 was observed** (owed in the heavy phase: run each at `origin/main`'s router to show 404/422 red, then green here). A DB-free probe (`validate_draft` called directly on the save fixtures) printed: valid → `[]`; division → `EXPRESSION_UNGUARDED_DIVISION` on `s_office`; pre-edit → `LADDER_CLAMP_UNPLACEABLE` on `s_minprem`; cycle → `RATING_GRAPH_CYCLIC` on `s_office` and `s_minprem`.
- Plan deltas: the type-mismatch fixture's issue is on `s_name_out`, not `s_clamp` (Acceptance 5 names `s_clamp`; the fixture in `test_rating_compile.py::test_an_algorithm_type_mismatch_reports_the_output_step` is the one the plan's pointer reaches). Load1 read 4.67 on the last small run, over the 4.0 cap: it should have waited.

#### 2026-10-10 00:3x BST — Tasks 6–8 authored by `executor-wk675s3fe` (fresh seat; frontend deps NOT installed)

- Seat's head at start `cc80a3bf` (ls-remote matched). No `pnpm install` yet (the lead's hold on gate-1), so there is **no `frontend/node_modules` and no generated client**: every test below is **UNRUN, and no red was observed**. Owed: run each file once through the small-test slot, show it red against the pre-change component (`git stash` is barred; use the commit before) and green here.
- Task 6 (`b1fe4d9e`): `validateRatingAlgorithm`; `useGraphValidation` (debounce 400 ms, abort, sequence number so a late older answer is dropped, `byStep`, `graphLevel`); `GraphIssues.vue` (`role="status"`); `StepNode` renders `⚠ n` (glyph `aria-hidden`), the messages in a list, `invalid` class with a 2px border, and `, n issue(s)` in its `aria-label`; `NodeNavigator` takes an optional `issueCounts` map and names its options `<id> <label>, n issue(s)`; `DagDesigner` wires them and adds an `aria-live="polite"` count (`n issues`). Tests: `__tests__/useGraphValidation.test.ts` (4: one call for three changes; abort; stale response; grouping), `__tests__/DagDesignerValidation.test.ts` (3: the `FR 9445` unresolved-reference-on-node-before-save test with `saveRatingAlgorithm` not called, graph-level issue in the status panel plus the live count, navigator option name). FR id is still the token `FR 9445` (hyphen form is barred outside the FR row and req markers).
- Task 7 (`a7a66a6f`): `getAlgorithmDiff`; `DiffOverlay.vue` (number input defaulting to `version - 1`, absent at version 1; Compare; panel lists Removed and Re-pointed tables; 404 branches on `code === "NOT_FOUND"`, the code `get_algorithm` raises); `StepNode` renders the `added`/`changed` text chip; `DagDesigner` maps the emitted diff (a re-pointed table counts as changed). Test: `__tests__/DiffOverlay.test.ts` (5).
- Task 8 (static review of the authored markup, WCAG 2.2 AA; not the `accessibility-tester` agent, which cannot run a browser here either): every marker has a text channel (`⚠ n` plus the messages, the `added`/`changed` chip, the graph issue prefixed "Graph issue:"); the new controls are native `input`/`button` with a visible `<label for>`; the red border (`red-700` on white) is ≥ 3:1 as a non-text indicator and is never the only channel; count region and `role="status"` panel are polite. **OWED, browser-only:** real keyboard tab order through the overlay and designer, focus ring visibility on the new input/button, screen-reader announcement of the count and of the status panel, and contrast measured on the rendered page. Not run.
- **Deviations / open for the lead:** (a) `frontend/src/views/__tests__/RatingDesignView.test.ts` mocks `@/api/ratingAlgorithms` without `validateRatingAlgorithm`, so it will fail once run; the one-line fix is outside PL-1556's write set and was NOT made (asked the lead). (b) Acceptance 14's grep is not empty at this tree: `graph.test.ts:38` ("topological" in a test title), `graph.ts:39` (a Kahn comment), `RatingDesignView.test.ts:93,102` (a save-refusal fixture); none is a check of consumes/produces. (c) `DiffOverlay` is fed `draft.slug`/`draft.version`; whether `draft.version` is a plain `number` in the generated draft type is unchecked until `generate:api` and `type-check` run.

**Handover to the next seat.** Remaining: Task 9 (the gate, after the lead's slot). First after install: `pnpm --dir <wt>/frontend generate:api`, then `vitest run` each new file singly (Task 6: `useGraphValidation.test.ts`, `DagDesignerValidation.test.ts`; Task 7: `DiffOverlay.test.ts`), then `lint` and `type-check` and fix what they find (expect fixes: `exactOptionalPropertyTypes` on the `diffMark` prop, `draft.version` typing, the `RatingAlgorithmDraft` vs `AlgorithmDiff` import in `DiffOverlay`). Then the heavy owed list: the unrun backend DB tests of Tasks 2 and 4 with their red-on-main, the browser a11y checks above, `test_sub_graph.py`, whole-tree mypy, audit-docs, `migrate --verify`, and the FR-id replacement of `FR 9445` once the lead names it.

#### 2026-10-10 — Acceptance 14 grep hits, listed and classified (lead's instruction; ruling pending with the maintainer)

Predicate verbatim, run at tree `a7a66a6f`: `git -C <wt> grep -n -i -E 'RATING_GRAPH_CYCLIC|RATING_GRAPH_UNRESOLVED_REF|topolog|kahn' -- frontend/src ':!frontend/src/api/generated'` → 4 lines (the case-sensitive form of the plan's command differs only on the `kahn` hit).

| # | Hit | Classification | Reason |
|---|---|---|---|
| 1 | `components/dag/__tests__/graph.test.ts:38` — test title "orders the topological eleven-step fixture as declared" | not a check | the word "topological" in a title; asserts S2's display layout order |
| 2 | `components/dag/graph.ts:39` — comment "Kahn's order, ties by declared position…" | not a check | describes `graphOrder`, S2's navigator/layout ordering; it validates nothing and emits no issue |
| 3 | `views/__tests__/RatingDesignView.test.ts:93` — fixture `code: "RATING_GRAPH_CYCLIC"` | not a check | a mocked save refusal (S2); the code is displayed from the response, never produced client-side |
| 4 | `views/__tests__/RatingDesignView.test.ts:102` — assertion that the alert shows that code | not a check | asserts display of a server-supplied code |

Neither `useGraphValidation.ts` nor `GraphIssues.vue` contains any of the four tokens. No file is edited on this account.

#### 2026-10-10 21:23 BST — merge turn work by `executor-675s3g`: main merged at `d5959dee`, citations re-read, Acceptance 14 re-read

- **Merge** of `origin/main` `31b88780` into the branch (true base `8b9d12c7`): the six forecast conflicts, plus PL-1558 and RL-1555 add/add residue from git's wrong base, taken from the true-base merge-tree `f9d971c0`. `rating.py`: SL-1340's mount nodes (`_MountNode`, the `mount_point` uniqueness issue) now live once, in `graph_invariant_issues`; three tests in `test_graph_invariant_issues.py` (a pinned mount's outputs resolve; a broken mount is `RATING_GRAPH_UNRESOLVED_REF` on the mount; a `mount_point` equal to a `step_id` is an issue). Red-first: with the mounts left out of `nodes`, the first two fail; green with the port. `compile.py`: the FR-223 refusal renders `safe_error_detail(exc) or type(exc).__name__` (the 10:14:29 form), so the text is `MODEL_REFERENCE_MODE_INCONSISTENT: ValueError`; a sentinel test (a raw message in the underlying error) is red with `str(exc)` and green now.
- **Citations re-read at `d5959dee`** (the lines above were taken at `8b9d12c7`/`893d8161`): `RatingAlgorithmDraft` `rating.py:519`; `ValidationIssue` now defined at `rating.py:496` and imported by `compile.py` (and by `rate_tables/operations.py:58` via `compile`); `_graph_invariants` `rating.py:558`, `_reachable` `:570`, `_reaches_output` `:590`, `graph_invariant_issues` `:610`; `validate_algorithm` call `compile.py:987`, the mode check `:991`; `errors.py:343` (the code in `RATING_ERROR_CODES`); `rating_versions.py:313` (the create-time check) and the `except ValueError` at `:769`; the Acceptance 18 test at `test_rating_version_create_pins.py:331`; `test_contracts.py:220` (the diff response test). Content unchanged where a line is not listed here.
- **Acceptance 14, re-read at `d5959dee`** by the dated reading of `to-lead.md` "2026-10-10 00:21:33 BST" item 2 (every hit listed and classified, the auditor reads each at the slice head). Predicate verbatim: `git -C <wt> grep -n -i -E 'RATING_GRAPH_CYCLIC|RATING_GRAPH_UNRESOLVED_REF|topolog|kahn' -- frontend/src ':!frontend/src/api/generated'` → 5 lines. The four above are unchanged (`graph.test.ts:38`, `graph.ts:39`, `RatingDesignView.test.ts:94` and `:103`, lines moved by one with the mock line); the fifth is new: `components/dag/__tests__/DagDesignerValidation.test.ts:33`, a mocked validate response with `code: "RATING_GRAPH_UNRESOLVED_REF"`: **not a check**, a server-supplied code the test feeds the component to assert it is displayed on the node. What the grep cannot see: a graph check written with other names (for example a walk over `consumes` with no token above); `useGraphValidation.ts` and `GraphIssues.vue` were read in full and hold none.
- **Mock line:** `RatingDesignView.test.ts` +1 (`validateRatingAlgorithm: () => Promise.resolve({ issues: [] }),`), 0 assertions changed. **No red was observed for it:** the file without the line passes 7 of 7 three times in a row here; one cold first run failed `findByLabelText` at 1017 ms, a 1 s timing limit, with and without the line. The line is precautionary, as the ruling allowed.
- **Frontend:** the 12 tests pass singly (`useGraphValidation` 4, `DagDesignerValidation` 3, `DiffOverlay` 5). `type-check` was red with 9 `TS18048` errors (the generated `AlgorithmDiff` marks its four list fields optional); fixed with `?? []` at the nine reads in `DagDesigner.vue` and `DiffOverlay.vue`; `lint` and `type-check` clean.

#### 2026-10-10 21:27 BST — FR-223 compile refusal, corrected on the lead's rulings (the entry above, bullet 1, is superseded on this point)

- The `safe_error_detail(exc) or type(exc).__name__` form in the merge-turn entry lost the step id. The lead ruled (A) on the 21:3x entries of `to-lead.md`: `check_model_reference_mode` raises `ModelReferenceModeError(ValueError)` (new, `model_schema/rating.py`, exported), with today's text (the step id and the two declared modes; artifact structure, no quote input). `CodedError` could not be raised at the source: `pricing-core` depends on `model-schema`, not the reverse. `compile.py` catches that class by name and calls `_raise_named("MODEL_REFERENCE_MODE_INCONSISTENT", str(exc))`; any other `ValueError` falls through uncoded. Red-first on the small-test slot: the restored `'s_rp'` assertion and a foreign-`ValueError` sentinel test (`test_a_foreign_value_error_is_not_given_the_mode_code`) both failed, a class-text test in `test_rating_version.py` failed at collection; all green after.
- `backend/tests/test_error_sinks.py` gains one `_SINKS` row for the new `str(exc)` in `compile_bundle` (the census test failed without it: a sink added). One row, no other change.
- **For the merge turn:** if SL-1600 (`InputFreeError`) has merged by then, `ModelReferenceModeError` subclasses `InputFreeError` (`to-lead.md` "2026-10-10 21:05:35 BST" item 2): its text is authored and input-free.
- The `?? []` fixes (nine reads in `DagDesigner.vue` and `DiffOverlay.vue`) are the slice's own code, inside the write set. The mock line is precautionary under "2026-10-10 00:21:33 BST" (1), not a red-first.

## PRs

None yet.
